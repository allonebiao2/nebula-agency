# -*- coding: utf-8 -*-
"""
Parler à l'agent.

L'agent répond à partir de CE QU'IL SAIT, pas de ce qu'il imagine : chaque
chiffre qu'il cite vient d'un outil qui lit son journal, son état ou ses
rapports. Le modèle ne voit jamais le marché directement.

Deux moteurs :
  · AVEC CLÉ API : Claude, avec des outils de lecture et d'action.
  · SANS CLÉ : un répondeur local qui comprend les demandes courantes (état,
    risque, pourquoi pas de trade, pause, reprise). Un client qui n'a pas de
    clé doit quand même pouvoir parler à son agent.

La règle qui compte : **l'agent peut rendre le bot plus prudent tout seul,
jamais plus risqué**. Baisser le risque, mettre en pause, analyser : il le fait.
Relever un risque, passer en réel, arrêt d'urgence : il PROPOSE, et
l'utilisateur confirme d'un bouton. Une phrase mal comprise ne doit jamais
suffire à engager de l'argent.
"""
from __future__ import annotations

import json
import re
import secrets as alea
import time
from datetime import datetime, timezone

from ..noyau import reglages
from ..noyau.chemins import dossier_rapports, fichier

MODELE_DEFAUT = "claude-sonnet-5"
MODELES = ("claude-sonnet-5", "claude-opus-5")

SYSTEME = """Tu es NEBULA Trader, un agent de trading automatique sur EUR/USD. Tu parles à la personne qui t'a installé, en français, simplement, comme un associé prudent qui rend des comptes.

Ce que tu es : une stratégie de cassure de tendance en H4, encadrée par huit verrous (thèse, invalidation technique, risque en % et en devise, ratio gain/risque, annonces économiques, état du système, discipline, marché négociable), des disjoncteurs (jour, semaine, mois, arrêt total) et un dimensionnement qui ne dépasse jamais le risque autorisé. Tu tournes sur MetaTrader 5.

Règles absolues :
- Tout chiffre que tu cites vient d'un outil. Si tu ne l'as pas lu, tu ne l'inventes pas : tu appelles l'outil ou tu dis que tu ne sais pas.
- Tu ne promets jamais de rendement. Tu dis ce qui a été mesuré, sur combien de trades, et si c'est statistiquement solide ou non. À ce jour, le walk-forward sur quinze ans n'a pas prouvé d'avantage : dis-le si on te pose la question.
- Tu peux rendre le système plus prudent de toi-même (baisser un risque, mettre en pause). Tout ce qui augmente le risque, le passage en réel ou l'arrêt d'urgence passe par une PROPOSITION que l'utilisateur confirme dans l'interface : tu l'expliques en une phrase.
- Martingale, grille, moyenne à la baisse, stop élargi : interdits, pas des réglages. Si on te le demande, tu expliques pourquoi.
- Quand on te demande pourquoi tu n'as pas tradé, tu lis les décisions et tu cites le verrou qui a refusé, avec sa raison.
- Réponses courtes : quelques phrases, une liste seulement si elle aide. Pas de tirets cadratins. Montants avec leur devise."""

OUTILS = [
    {"name": "lire_etat",
     "description": "État actuel de l'agent : connexion MT5, compte (solde, équité, type), mode, pause, positions ouvertes avec leur R, prochaine bougie, et jauges de risque contre leurs limites.",
     "input_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "lire_decisions",
     "description": "Les dernières décisions : chaque signal proposé par une stratégie, le verdict (pris, refusé, observé, échec) et le détail des 8 verrous.",
     "input_schema": {"type": "object", "properties": {"limite": {"type": "integer", "minimum": 1, "maximum": 30}},
                      "additionalProperties": False}},
    {"name": "lire_journal",
     "description": "Les derniers événements : analyses de bougies, trades, disjoncteurs, commandes, erreurs de connexion.",
     "input_schema": {"type": "object", "properties": {"limite": {"type": "integer", "minimum": 1, "maximum": 60}},
                      "additionalProperties": False}},
    {"name": "lire_performance",
     "description": "Performance : statistiques des trades réels du journal, et résultats hors échantillon du walk-forward et de la mesure par capital.",
     "input_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "lire_reglages",
     "description": "Tous les réglages modifiables avec leur valeur, leurs bornes et leur effet sur le risque, plus la liste des protections non modifiables.",
     "input_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "modifier_reglages",
     "description": "Change un ou plusieurs réglages (clés exactes de lire_reglages). Les changements qui rendent le système plus prudent sont appliqués ; ceux qui augmentent le risque deviennent une proposition à confirmer par l'utilisateur.",
     "input_schema": {"type": "object",
                      "properties": {"changements": {"type": "object", "description": "{cle: valeur}"},
                                     "raison": {"type": "string"}},
                      "required": ["changements", "raison"], "additionalProperties": False}},
    {"name": "commander",
     "description": "Commande l'agent. pause / reprendre / analyser / reconnecter s'exécutent. urgence (tout fermer et mettre en pause) et mode (observation, demo, reel) deviennent une proposition à confirmer.",
     "input_schema": {"type": "object",
                      "properties": {"action": {"type": "string", "enum": ["pause", "reprendre", "analyser", "reconnecter", "urgence", "mode"]},
                                     "valeur": {"type": "string", "description": "motif de pause, ou mode visé"},
                                     "raison": {"type": "string"}},
                      "required": ["action", "raison"], "additionalProperties": False}},
]


class Assistant:
    def __init__(self, agent, journal):
        self.agent = agent
        self.journal = journal
        self.propositions: dict[str, dict] = {}

    # ------------------------------------------------------------------ #
    #  Configuration
    # ------------------------------------------------------------------ #
    @staticmethod
    def config() -> dict:
        p = fichier("assistant.json")
        d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        return {"modele": d.get("modele", MODELE_DEFAUT)}

    @staticmethod
    def cle_api() -> str | None:
        import os
        from ..noyau.coffre import lire_secret
        return os.environ.get("ANTHROPIC_API_KEY") or lire_secret("anthropic")

    @classmethod
    def configurer(cls, *, cle: str | None = None, modele: str | None = None) -> dict:
        from ..noyau.coffre import enregistrer_secret
        if cle is not None:
            enregistrer_secret("anthropic", cle.strip())
        if modele:
            if modele not in MODELES:
                raise ValueError(f"modèle inconnu : {modele}")
            fichier("assistant.json").write_text(json.dumps({"modele": modele}), encoding="utf-8")
        return {**cls.config(), "cle": bool(cls.cle_api())}

    # ------------------------------------------------------------------ #
    #  Outils
    # ------------------------------------------------------------------ #
    def executer_outil(self, nom: str, entree: dict) -> dict:
        if nom == "lire_etat":
            return self.agent.instantane()
        if nom == "lire_decisions":
            lignes = self.journal.decisions(int(entree.get("limite", 8)))
            return [{"quand": d["ts"], "strategie": d["strategie"], "sens": d["sens"],
                     "verdict": d["verdict"], "motif": d["motif"], "risque_pct": d["risque_pct"],
                     "these": d["these"],
                     "verrous_refuses": [f"Q{v['n']} {v['question']} : {v['detail']}"
                                         for v in d["verrous"] if not v["passe"]]}
                    for d in lignes]
        if nom == "lire_journal":
            return [{"quand": e["ts"], "niveau": e["niveau"], "type": e["type"],
                     "message": e["message"]} for e in self.journal.evenements(int(entree.get("limite", 20)))]
        if nom == "lire_performance":
            return self.performance()
        if nom == "lire_reglages":
            return reglages.decrire()
        if nom == "modifier_reglages":
            return self._modifier(entree.get("changements", {}), entree.get("raison", ""))
        if nom == "commander":
            return self._commander(entree["action"], entree.get("valeur"), entree.get("raison", ""))
        return {"erreur": f"outil inconnu {nom}"}

    def performance(self) -> dict:
        wf = {}
        for p in sorted(dossier_rapports().glob("walkforward_*.json")):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except Exception:                                  # noqa: BLE001
                continue
            m = d.get("metriques", {})
            wf[p.stem] = {"trades": m.get("trades"), "esperance_R": m.get("esperance_R"),
                          "profit_factor": m.get("profit_factor"),
                          "capital": [m.get("capital_initial"), m.get("capital_final")],
                          "drawdown_max_pct": m.get("drawdown_max_pct"),
                          "statistiquement_credible": d.get("credible"),
                          "variante": d.get("variante")}
        return {"journal_reel": self.journal.statistiques(), "walk_forward_hors_echantillon": wf}

    def _modifier(self, changements: dict, raison: str) -> dict:
        schema = {e["cle"]: e for e in reglages.SCHEMA}
        cfg = reglages.config_effective()
        prudents, risques = {}, {}
        for cle, valeur in changements.items():
            e = schema.get(cle)
            if not e:
                prudents[cle] = valeur          # le videur renverra l'erreur
                continue
            avant = reglages.valeur_actuelle(cfg, cle)
            plus = False
            try:
                if e["type"] in ("nombre", "entier"):
                    v = float(valeur)
                    plus = (e.get("sens") == "risque" and v > avant) or \
                           (e.get("sens") == "prudence" and v < avant) or e.get("sens") is None
                elif e["type"] == "bool":
                    v = str(valeur).lower() in ("1", "true", "oui", "on")
                    plus = (e.get("sens") == "prudence" and not v) or e.get("sens") is None
                else:
                    plus = True
            except (TypeError, ValueError):
                plus = True
            (risques if plus else prudents)[cle] = valeur
        resultat = {"appliques": None, "proposition": None}
        if prudents:
            dd = (self.agent.instantane().get("risque") or {}).get("drawdown_pct", 0.0)
            resultat["appliques"] = reglages.modifier(prudents, auteur="agent (conversation)",
                                                     drawdown_pct=dd, journal=self.journal)
        if risques:
            resultat["proposition"] = self._proposer("reglages", risques, raison)
        return resultat

    def _commander(self, action: str, valeur, raison: str) -> dict:
        if action in ("urgence", "mode"):
            if action == "mode" and valeur not in ("observation", "demo", "reel"):
                return {"erreur": "mode attendu : observation, demo ou reel"}
            if action == "mode" and valeur == "observation":
                self.agent.commander("mode", "observation", auteur="agent (conversation)")
                return {"fait": "mode observation : plus aucun ordre ne part"}
            return {"proposition": self._proposer(action, valeur, raison)}
        self.agent.commander(action, valeur or raison, auteur="agent (conversation)")
        return {"fait": action}

    def _proposer(self, type_: str, contenu, raison: str) -> dict:
        pid = alea.token_hex(4)
        self.propositions[pid] = {"id": pid, "type": type_, "contenu": contenu, "raison": raison,
                                  "cree_le": time.time()}
        self.journal.evenement("proposition", f"l'agent propose {type_} : {contenu} ({raison})",
                               donnees={"id": pid})
        return {"id": pid, "a_confirmer": True,
                "message": "proposition enregistrée : l'utilisateur doit la confirmer dans l'interface"}

    def repondre_proposition(self, pid: str, accepter: bool) -> dict:
        p = self.propositions.pop(pid, None)
        if not p:
            return {"ok": False, "erreur": "proposition inconnue ou déjà traitée"}
        if not accepter:
            self.journal.evenement("proposition", f"proposition {p['type']} refusée par l'utilisateur")
            return {"ok": True, "refusee": True}
        if p["type"] == "reglages":
            dd = (self.agent.instantane().get("risque") or {}).get("drawdown_pct", 0.0)
            r = reglages.modifier(p["contenu"], auteur="utilisateur (confirmation)",
                                  drawdown_pct=dd, journal=self.journal)
            return {"ok": r["ok"], "resultat": r}
        if p["type"] == "urgence":
            self.agent.commander("urgence", auteur="utilisateur (confirmation)")
            return {"ok": True}
        if p["type"] == "mode":
            self.agent.commander("mode", p["contenu"], auteur="utilisateur (confirmation)")
            return {"ok": True}
        return {"ok": False, "erreur": "type inconnu"}

    def propositions_en_attente(self) -> list[dict]:
        limite = time.time() - 3600
        for pid in [k for k, v in self.propositions.items() if v["cree_le"] < limite]:
            self.propositions.pop(pid)
        return list(self.propositions.values())

    # ------------------------------------------------------------------ #
    #  Réponse
    # ------------------------------------------------------------------ #
    def parler(self, message: str) -> dict:
        message = (message or "").strip()[:4000]
        if not message:
            return {"reponse": "", "moteur": "aucun"}
        historique = self.journal.conversation(20)
        self.journal.message("utilisateur", message)
        cle = self.cle_api()
        try:
            if cle:
                texte, moteur = self._claude(cle, historique, message), self.config()["modele"]
            else:
                texte, moteur = self._local(message), "local"
        except Exception as exc:                               # noqa: BLE001
            texte = (f"Je n'arrive pas à joindre le modèle ({exc.__class__.__name__}). "
                     f"Voici ce que je peux dire sans lui :\n\n{self._local(message)}")
            moteur = "local (secours)"
        self.journal.message("agent", texte)
        return {"reponse": texte, "moteur": moteur,
                "propositions": self.propositions_en_attente()}

    def _claude(self, cle: str, historique: list[dict], message: str) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=cle)
        messages = []
        for h in historique:
            role = "user" if h["role"] == "utilisateur" else "assistant"
            if messages and messages[-1]["role"] == role:
                messages[-1]["content"] += "\n\n" + h["contenu"]
            else:
                messages.append({"role": role, "content": h["contenu"]})
        if messages and messages[0]["role"] != "user":
            messages.pop(0)
        maintenant = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        messages.append({"role": "user", "content": f"[{maintenant}] {message}"})

        for _ in range(8):
            reponse = client.messages.create(
                model=self.config()["modele"], max_tokens=4000,
                system=[{"type": "text", "text": SYSTEME, "cache_control": {"type": "ephemeral"}}],
                tools=OUTILS, messages=messages,
                output_config={"effort": "medium"},
            )
            if reponse.stop_reason == "refusal":
                return "Je ne peux pas répondre à cette demande."
            appels = [b for b in reponse.content if b.type == "tool_use"]
            if reponse.stop_reason != "tool_use" or not appels:
                return "\n".join(b.text for b in reponse.content if b.type == "text").strip()
            messages.append({"role": "assistant", "content": reponse.content})
            resultats = []
            for appel in appels:
                try:
                    sortie = self.executer_outil(appel.name, dict(appel.input))
                    resultats.append({"type": "tool_result", "tool_use_id": appel.id,
                                      "content": json.dumps(sortie, ensure_ascii=False,
                                                            default=str)[:30000]})
                except Exception as exc:                       # noqa: BLE001
                    resultats.append({"type": "tool_result", "tool_use_id": appel.id,
                                      "content": f"erreur : {exc}", "is_error": True})
            messages.append({"role": "user", "content": resultats})
        return "J'ai dû m'arrêter : trop d'étapes pour cette question. Reformule-la plus simplement."

    # ------------------------------------------------------------------ #
    #  Répondeur local (sans clé)
    # ------------------------------------------------------------------ #
    def _local(self, message: str) -> str:
        def fr(x, d=2):
            return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
        m = message.lower()
        s = self.agent.instantane()
        r = s.get("risque") or {}
        c = s.get("compte") or {}

        # « stop » seul ne suffit pas : « c'est quoi mon stop ? » est une question,
        # pas un ordre. Seules des formules d'arrêt explicites mettent en pause.
        if re.search(r"\b(pause|arr[eê]te[- ]toi|arr[eê]te de trader|stoppe|stop trading)\b", m) \
                and "urgence" not in m:
            self.agent.commander("pause", "demandé dans la conversation", auteur="conversation")
            return "C'est fait : je suis en pause. Plus aucune nouvelle position ne s'ouvrira tant que tu ne me dis pas « reprends »."
        if any(k in m for k in ("reprend", "relance", "continue")):
            self.agent.commander("reprendre", auteur="conversation")
            return "Je reprends. Les huit verrous restent actifs : je n'entrerai que sur un signal qui les passe tous."
        if "urgence" in m or "ferme tout" in m:
            p = self._proposer("urgence", None, "demandé dans la conversation")
            return f"Arrêt d'urgence prêt : il fermera toutes mes positions et me mettra en pause. Confirme-le avec le bouton (proposition {p['id']})."
        if any(k in m for k in ("pourquoi", "refus", "pas de trade", "rien fait")):
            ds = self.journal.decisions(3)
            if not ds:
                ev = self.journal.evenements(3)
                derniere = next((e["message"] for e in ev if e["type"] == "analyse"), None)
                return ("Aucune stratégie ne m'a proposé de trade pour l'instant. "
                        + (f"Dernière analyse : {derniere}." if derniere else ""))
            d = ds[0]
            refus = [f"Q{v['n']} {v['detail']}" for v in d["verrous"] if not v["passe"]]
            if d["verdict"] == "refuse":
                return (f"Le dernier signal ({d['strategie']}, {d['sens']}) a été refusé :\n- "
                        + "\n- ".join(refus))
            return f"Dernier signal ({d['strategie']}, {d['sens']}) : {d['verdict']}. {d['motif'] or ''}"
        if any(k in m for k in ("risque", "drawdown", "perte")):
            lim = r.get("limites", {})
            if not lim:
                return "Je ne suis pas encore connecté au compte : je ne peux pas mesurer le risque en cours."
            return (f"Risque par trade : {fr(lim['risque_par_trade_pct'], 1)} % "
                    f"(plafond petit compte {fr(lim['risque_max_petit_compte_pct'], 1)} %). "
                    f"Aujourd'hui {fr(r.get('pnl_jour_pct', 0))} % sur une limite de "
                    f"-{fr(lim['perte_max_jour_pct'], 1)} %, drawdown {fr(r.get('drawdown_pct', 0))} % "
                    f"sur un arrêt total à {fr(lim['drawdown_max_total_pct'], 0)} %, "
                    f"{r.get('pertes_consecutives', 0)} perte(s) d'affilée.")
        if any(k in m for k in ("performance", "rentable", "gagne", "résultat", "resultat")):
            p = self.performance()
            j = p["journal_reel"]
            lignes = [f"Sur ce compte : {j['trades']} trade(s) fermé(s), résultat {fr(j['resultat_net'])}."]
            for nom, w in p["walk_forward_hors_echantillon"].items():
                lignes.append(f"{nom} : {w['trades']} trades hors échantillon, espérance "
                              f"{'+' if (w['esperance_R'] or 0) > 0 else ''}{fr(w['esperance_R'] or 0, 3)} R, "
                              f"{'solide' if w['statistiquement_credible'] else 'pas encore statistiquement solide'}.")
            return "\n".join(lignes)
        # état par défaut
        cx = s.get("connexion", {})
        pos = s.get("positions", [])
        return (f"{cx.get('message', 'état inconnu')}. Mode {s.get('mode')}"
                + (f", en pause ({s['pause']})" if s.get("pause") else "")
                + (f". Solde {fr(c.get('solde', 0))} {c.get('devise', '')}" if c else "")
                + f". {len(pos)} position(s) ouverte(s). Prochaine bougie analysée : "
                  f"{(s.get('prochaine_bougie') or '?')[11:16]}.\n\n"
                  "Sans clé API je comprends : état, risque, pourquoi pas de trade, performance, pause, reprends, urgence. "
                  "Ajoute une clé dans « Compte et licence » pour discuter librement.")

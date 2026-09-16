# -*- coding: utf-8 -*-
"""
Le serveur de l'interface : une application web LOCALE.

Sécurité, parce qu'un serveur local reste joignable par n'importe quel site
ouvert dans le navigateur de la même machine :
  · il n'écoute que 127.0.0.1 ;
  · toute requête qui MODIFIE quelque chose exige l'en-tête `X-Jeton`, un secret
    tiré au démarrage et écrit dans la page. Un site tiers ne peut pas le lire
    (même origine) et ne peut pas envoyer d'en-tête personnalisé sans une
    prévalidation CORS que ce serveur ne donne jamais ;
  · l'en-tête `Host` doit être local : ça ferme la porte au « DNS rebinding ».
"""
from __future__ import annotations

import glob
import json
import os
import secrets as alea
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ..noyau import coffre, licence, reglages
from ..noyau.chemins import dossier_rapports, dossier_ressources
from ..noyau.config import ConfigDangereuse
from ..strategies import catalogue
from .chat import MODELES

VERSION = "0.1.0"
STATIQUE = dossier_ressources() / "interface" / "statique"
TERMINAUX_CONNUS = [
    r"C:\Program Files\MetaTrader 5\terminal64.exe",
    r"C:\Program Files\MetaTrader 5 Terminal\terminal64.exe",
]


def _terminaux() -> list[str]:
    trouves = set(p for p in TERMINAUX_CONNUS if Path(p).exists())
    for motif in (r"C:\Program Files\*\terminal64.exe", r"C:\Program Files (x86)\*\terminal64.exe",
                  os.path.expandvars(r"%APPDATA%\*\terminal64.exe")):
        trouves.update(glob.glob(motif))
    return sorted(trouves)


def _json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:                                          # noqa: BLE001
        return None


def creer_app(agent, journal, assistant, *, port: int) -> FastAPI:
    jeton = alea.token_urlsafe(32)
    hotes = {f"127.0.0.1:{port}", f"localhost:{port}"}
    app = FastAPI(title="NEBULA Trader", docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def garde(request: Request, suivant):
        if request.headers.get("host") not in hotes:
            return JSONResponse({"erreur": "hôte refusé"}, status_code=403)
        if request.method not in ("GET", "HEAD") and request.headers.get("x-jeton") != jeton:
            return JSONResponse({"erreur": "jeton de session manquant"}, status_code=403)
        reponse = await suivant(request)
        # Un site TIERS ne peut pas encadrer l'interface (vol de clic) ; la même
        # origine le peut, ce qui sert à contrôler le rendu téléphone.
        reponse.headers["X-Frame-Options"] = "SAMEORIGIN"
        reponse.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
        reponse.headers["X-Content-Type-Options"] = "nosniff"
        reponse.headers["Cache-Control"] = "no-store"
        return reponse

    app.mount("/statique", StaticFiles(directory=STATIQUE), name="statique")

    @app.get("/", response_class=HTMLResponse)
    def accueil():
        page = (STATIQUE / "index.html").read_text(encoding="utf-8")
        return page.replace("{{JETON}}", jeton).replace("{{VERSION}}", VERSION)

    # ------------------------------------------------------------------ #
    #  Lecture
    # ------------------------------------------------------------------ #
    @app.get("/api/etat")
    def etat():
        lic = licence.actuelle()
        return {**agent.instantane(), "licence": lic.en_dict(), "version": VERSION,
                "propositions": assistant.propositions_en_attente(),
                "stats": journal.statistiques(),
                "assistant": {**assistant.config(), "cle": bool(assistant.cle_api())}}

    @app.get("/api/equite")
    def equite(jours: int = 90):
        return journal.courbe(depuis_jours=max(1, min(jours, 3650)))

    @app.get("/api/evenements")
    def evenements(limite: int = 60):
        return journal.evenements(max(1, min(limite, 500)))

    @app.get("/api/decisions")
    def decisions(limite: int = 50):
        return journal.decisions(max(1, min(limite, 500)))

    @app.get("/api/trades")
    def trades(limite: int = 200):
        return {"trades": journal.trades(max(1, min(limite, 1000))),
                "stats": journal.statistiques(), "ordres": journal.ordres(50)}

    @app.get("/api/reglages")
    def lire_reglages():
        d = reglages.decrire()
        d["reglages"] = [r for r in d["reglages"] if not r.get("cache")]
        return {**d, "historique": journal.historique_reglages(50)}

    @app.get("/api/strategies")
    def strategies():
        actives = reglages.agent()["strategies_actives"]
        variante_courante = ("reference" if reglages.config_effective().calendrier.fermer_avant_weekend
                             else "sans_weekend")
        rapports = {}
        for p in sorted(dossier_rapports().glob("walkforward_*.json")):
            d = _json(p)
            if not d:
                continue
            rapports.setdefault(d.get("strategie", p.stem), []).append({
                "fichier": p.name, "variante": d.get("variante"), "calcule_le": d.get("calcule_le"),
                "correspond_config": d.get("variante") == variante_courante,
                "metriques": d.get("metriques"), "credible": d.get("credible"),
                "efficacite": d.get("efficacite"), "fenetres": d.get("fenetres"),
                "stabilite": d.get("stabilite"), "sorties": d.get("sorties"),
                "courbe": d.get("courbe_equite", [])[::max(1, len(d.get("courbe_equite", [])) // 300)],
                "couts": d.get("couts"),
            })
        return {"catalogue": [{**s, "active": s["nom"] in actives} for s in catalogue.decrire()],
                "rapports": rapports}

    @app.get("/api/capital")
    def capital():
        return _json(dossier_rapports() / "capital.json") or {}

    @app.get("/api/conversation")
    def conversation():
        return {"messages": journal.conversation(80),
                "propositions": assistant.propositions_en_attente()}

    @app.get("/api/installation")
    def installation():
        from ..noyau.identifiants import charger
        ids = charger()
        return {
            "compte_application": coffre.resume_compte(),
            "identifiants_actifs": {"source": ids.profil, "login": ids.login,
                                    "serveur": ids.serveur, "complets": ids.complets},
            "terminaux": _terminaux(),
            "licence": licence.actuelle().en_dict(),
            "assistant": {**assistant.config(), "cle": bool(assistant.cle_api())},
            "modeles": list(MODELES),
            "version": VERSION,
        }

    # ------------------------------------------------------------------ #
    #  Actions
    # ------------------------------------------------------------------ #
    @app.post("/api/reglages")
    def modifier_reglages(corps: dict = Body(...)):
        dd = (agent.instantane().get("risque") or {}).get("drawdown_pct", 0.0)
        r = reglages.modifier(corps.get("changements", {}), auteur="interface",
                              drawdown_pct=dd, journal=journal)
        if r["ok"] and r["changes"]:
            journal.evenement("reglages", "réglages modifiés : " + ", ".join(
                f"{c['libelle']} {c['avant']} -> {c['apres']}" for c in r["changes"]),
                niveau="alerte" if r["alertes"] else "info")
        return r

    @app.post("/api/reglages/reinitialiser")
    def reinitialiser(corps: dict = Body(default={})):
        reglages.reinitialiser(corps.get("cle"), journal=journal)
        return {"ok": True}

    @app.post("/api/commande")
    def commande(corps: dict = Body(...)):
        action, valeur = corps.get("action"), corps.get("valeur")
        if action in ("pause", "reprendre", "analyser", "reconnecter"):
            agent.commander(action, valeur, auteur="interface")
            return {"ok": True}
        if action == "urgence":
            if not corps.get("confirme"):
                raise HTTPException(400, "l'arrêt d'urgence doit être confirmé")
            agent.commander("urgence", auteur="interface")
            return {"ok": True}
        if action == "relancer_apres_arret":
            if not corps.get("confirme"):
                raise HTTPException(400, "la reprise après un arrêt total doit être confirmée")
            agent.commander("relancer_apres_arret", auteur="interface")
            return {"ok": True}
        if action == "strategies":
            inconnues = [s for s in valeur or [] if s not in catalogue.STRATEGIES]
            if inconnues:
                raise HTTPException(400, f"stratégies inconnues : {inconnues}")
            agent.commander("strategies", list(valeur or []), auteur="interface")
            return {"ok": True}
        if action == "mode":
            if valeur not in ("observation", "demo", "reel"):
                raise HTTPException(400, "mode attendu : observation, demo ou reel")
            if valeur in ("demo", "reel") and not corps.get("confirme"):
                raise HTTPException(400, "le passage dans un mode qui envoie des ordres doit être confirmé")
            if valeur == "reel":
                lic = licence.actuelle()
                if not lic.valide:
                    return {"ok": False, "erreur": f"mode réel refusé : {lic.raison}"}
                r = reglages.modifier({"compte.mode": "reel"}, auteur="interface", journal=journal)
                if not r["ok"]:
                    return {"ok": False, "erreur": "mode réel refusé par le videur : "
                                                  + " ".join(r["erreurs"])}
            else:
                reglages.modifier({"compte.mode": "demo"}, auteur="interface", journal=journal)
            agent.commander("mode", valeur, auteur="interface")
            return {"ok": True}
        raise HTTPException(400, f"action inconnue : {action}")

    @app.post("/api/chat")
    def chat(corps: dict = Body(...)):
        return assistant.parler(str(corps.get("message", "")))

    @app.post("/api/propositions/{pid}")
    def proposition(pid: str, corps: dict = Body(...)):
        return assistant.repondre_proposition(pid, bool(corps.get("accepter")))

    @app.post("/api/installation/compte")
    def enregistrer_compte(corps: dict = Body(...)):
        try:
            login = int(str(corps.get("login", "")).strip())
        except ValueError:
            raise HTTPException(400, "le numéro de compte doit être un nombre")
        mdp, serveur = str(corps.get("motdepasse", "")), str(corps.get("serveur", "")).strip()
        if not mdp or not serveur:
            raise HTTPException(400, "mot de passe et serveur obligatoires")
        coffre.enregistrer_compte(login=login, motdepasse=mdp, serveur=serveur,
                                  terminal=str(corps.get("terminal", "")))
        journal.evenement("installation", f"identifiants du compte {login} @ {serveur} enregistrés "
                                          f"(mot de passe chiffré par Windows)")
        agent.commander("reconnecter", auteur="installation")
        return {"ok": True, "compte": coffre.resume_compte()}

    @app.post("/api/licence")
    def activer_licence(corps: dict = Body(...)):
        lic = licence.installer(str(corps.get("cle", "")))
        journal.evenement("licence", f"activation : {lic.raison}",
                          niveau="info" if lic.valide else "alerte")
        return lic.en_dict()

    @app.post("/api/assistant")
    def configurer_assistant(corps: dict = Body(...)):
        try:
            return assistant.configurer(cle=corps.get("cle"), modele=corps.get("modele"))
        except ValueError as exc:
            raise HTTPException(400, str(exc))

    @app.exception_handler(ConfigDangereuse)
    async def config_dangereuse(_request, exc):
        return JSONResponse({"ok": False, "erreurs": [str(exc)]}, status_code=400)

    return app

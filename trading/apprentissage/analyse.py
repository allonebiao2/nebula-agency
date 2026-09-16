# -*- coding: utf-8 -*-
"""
L'auto-analyse : ce que le journal dit de l'agent, sans lui faire dire plus.

    « Le backtest ment, le walk-forward vérifie, le marché décide. »

Le cahier des charges demande d'identifier « les heures rentables, les jours
rentables, les régimes favorables ». Piège : découper 30 trades en 24 heures et 5
jours, c'est trouver des « heures rentables » dans le hasard pur. Chaque tranche
porte donc son effectif, et **aucune conclusion n'est tirée sous 20 trades par
tranche**. Le rapport montre, il ne recommande que ce que l'échantillon autorise.

Ce qui est mesuré :
  · par stratégie, heure d'entrée, jour, régime : trades, réussite, espérance, PF
  · le glissement RÉEL des ordres contre le modèle de coûts du backtest
  · les refus par verrou : ce qui empêche l'agent de trader
  · la santé (CUSUM) de chaque stratégie
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone

MIN_PAR_TRANCHE = 20
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def _stats(trades: list[dict]) -> dict:
    n = len(trades)
    if not n:
        return {"trades": 0}
    r = [t["resultat_R"] for t in trades if t.get("resultat_R") is not None]
    gains = sum(t["resultat_devise"] for t in trades if (t["resultat_devise"] or 0) > 0)
    pertes = -sum(t["resultat_devise"] for t in trades if (t["resultat_devise"] or 0) <= 0)
    return {
        "trades": n,
        "reussite": sum(1 for t in trades if (t["resultat_devise"] or 0) > 0) / n,
        "esperance_R": sum(r) / len(r) if r else None,
        "profit_factor": gains / pertes if pertes else None,
        "resultat": sum(t["resultat_devise"] or 0 for t in trades),
        "concluant": n >= MIN_PAR_TRANCHE,
    }


def _par(trades, cle) -> dict:
    groupes: dict = defaultdict(list)
    for t in trades:
        groupes[cle(t)].append(t)
    return {str(k): _stats(v) for k, v in sorted(groupes.items(), key=lambda kv: str(kv[0]))}


def _regime(t: dict) -> str:
    try:
        ctx = json.loads(t.get("contexte") or "{}")
    except (TypeError, ValueError):
        ctx = {}
    e = ctx.get("efficacite")
    if e is None:
        return "inconnu"
    return "tendance" if e >= 0.30 else "range"


def analyser(journal, *, depuis_jours: int | None = None, glissement_modele_points: float = 1.0) -> dict:
    maintenant = datetime.now(timezone.utc)
    debut = maintenant - timedelta(days=depuis_jours) if depuis_jours else datetime(2000, 1, 1, tzinfo=timezone.utc)
    trades = [t for t in journal.fermes_depuis(debut) if t.get("ferme_le")]

    def entree(t):
        return datetime.fromisoformat(t["ouvert_le"])

    ordres = [o for o in journal.ordres(1000)
              if o["action"] == "ouvrir" and o.get("glissement_points") is not None
              and datetime.fromisoformat(o["ts"]) >= debut]
    gliss = sorted(o["glissement_points"] for o in ordres)
    refus: dict = defaultdict(int)
    for d in journal.decisions(1000):
        if datetime.fromisoformat(d["ts"]) < debut:
            continue
        for v in d["verrous"]:
            if not v["passe"]:
                refus[f"Q{v['n']} {v['question']}"] += 1

    rapport = {
        "calcule_le": maintenant.isoformat(timespec="seconds"),
        "periode_jours": depuis_jours,
        "global": _stats(trades),
        "par_strategie": _par(trades, lambda t: t.get("strategie") or "?"),
        "par_symbole": _par(trades, lambda t: t.get("symbole") or "EURUSD"),
        "par_heure_utc": _par(trades, lambda t: f"{entree(t).hour:02d} h"),
        "par_jour": _par(trades, lambda t: JOURS[entree(t).weekday()]),
        "par_regime": _par(trades, _regime),
        "glissement": {
            "ordres": len(gliss),
            "moyen_points": sum(gliss) / len(gliss) if gliss else None,
            "p90_points": gliss[int(0.9 * (len(gliss) - 1))] if gliss else None,
            "modele_points": glissement_modele_points,
            "conforme": (sum(gliss) / len(gliss) <= glissement_modele_points * 2) if gliss else None,
        },
        "refus_par_verrou": dict(sorted(refus.items(), key=lambda kv: -kv[1])),
    }
    rapport["constats"] = _constats(rapport)
    return rapport


def _constats(r: dict) -> list[str]:
    """Des phrases, seulement quand l'échantillon les autorise."""
    c = []
    g = r["global"]
    if g["trades"] == 0:
        c.append("Aucun trade fermé sur la période : rien à analyser, l'agent n'a pas encore d'histoire.")
    elif g["trades"] < MIN_PAR_TRANCHE:
        c.append(f"{g['trades']} trade(s) fermé(s) : trop peu pour conclure quoi que ce soit, "
                 f"il en faut au moins {MIN_PAR_TRANCHE} par tranche.")
    for nom, tranche in (("régime", r["par_regime"]), ("jour", r["par_jour"]), ("heure", r["par_heure_utc"])):
        concluantes = {k: v for k, v in tranche.items() if v.get("concluant") and v.get("esperance_R") is not None}
        if len(concluantes) >= 2:
            meilleur = max(concluantes.items(), key=lambda kv: kv[1]["esperance_R"])
            pire = min(concluantes.items(), key=lambda kv: kv[1]["esperance_R"])
            c.append(f"Par {nom} : le meilleur est « {meilleur[0]} » ({meilleur[1]['esperance_R']:+.2f} R sur "
                     f"{meilleur[1]['trades']} trades), le pire « {pire[0]} » ({pire[1]['esperance_R']:+.2f} R). "
                     f"À confirmer en walk-forward avant d'en faire une règle.")
    gl = r["glissement"]
    if gl["ordres"]:
        etat = "conforme au modèle" if gl["conforme"] else "AU-DELÀ du modèle : le backtest est trop optimiste"
        c.append(f"Glissement réel moyen {gl['moyen_points']:.1f} point(s) sur {gl['ordres']} ordre(s), "
                 f"modèle {gl['modele_points']:g} : {etat}.")
    if r["refus_par_verrou"]:
        premier = next(iter(r["refus_par_verrou"].items()))
        c.append(f"Le verrou qui bloque le plus : {premier[0]} ({premier[1]} refus).")
    return c

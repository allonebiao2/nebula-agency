# -*- coding: utf-8 -*-
"""
Les portes : ce qu'il faut avoir PROUVÉ avant d'engager plus d'argent.

    « Aucune modification live sans validation sur compte démo. »

PORTE DÉMO (avant tout mode réel). Le cahier demandait « 30 jours de paper trading
rentable ». Mesuré : en H4, 30 jours font environ 2 trades, ce qui ne prouve rien.
Et « rentable » sur 2 trades est un tirage de pièce. La porte vérifie donc ce que
le démo PEUT vérifier, c'est-à-dire l'EXÉCUTION :
  · au moins 30 jours ET au moins 30 trades sur compte démo ;
  · 100 % des ordres partis avec leur stop chez le courtier ;
  · glissement réel moyen au plus le double du modèle du backtest ;
  · santé CUSUM non en pause.
L'avantage, lui, se prouve en walk-forward, pas sur 30 trades.

PORTE BOOST RÉEL (phase 5 du cahier, gardée telle quelle) : 60 jours de PRO en
réel, résultat net positif, santé non en pause.
"""
from __future__ import annotations

from datetime import datetime, timezone


def _jours_depuis(iso: str | None) -> float:
    if not iso:
        return 0.0
    return (datetime.now(timezone.utc) - datetime.fromisoformat(iso)).total_seconds() / 86400


def _critere(nom: str, valeur, seuil: str, ok: bool) -> dict:
    return {"nom": nom, "valeur": valeur, "seuil": seuil, "ok": bool(ok)}


def porte_demo(journal, *, sante: dict | None = None, glissement_modele: float = 1.0,
               jours_min: int = 30, trades_min: int = 30) -> dict:
    trades = [t for t in journal.trades(5000) if t.get("mode") == "demo"]
    fermes = [t for t in trades if t.get("ferme_le")]
    premier = min((t["ouvert_le"] for t in trades), default=None)
    ordres = [o for o in journal.ordres(5000) if o["action"] == "ouvrir" and o.get("mode") == "demo"
              and o.get("retcode") == 10009]
    avec_stop = sum(1 for o in ordres if o.get("sl"))
    gliss = [o["glissement_points"] for o in ordres if o.get("glissement_points") is not None]
    moyen = sum(gliss) / len(gliss) if gliss else None
    criteres = [
        _critere("Jours sur compte démo", round(_jours_depuis(premier), 1), f"≥ {jours_min}",
                 _jours_depuis(premier) >= jours_min),
        _critere("Trades fermés en démo", len(fermes), f"≥ {trades_min}", len(fermes) >= trades_min),
        _critere("Ordres avec stop chez le courtier", f"{avec_stop}/{len(ordres)}", "100 %",
                 len(ordres) > 0 and avec_stop == len(ordres)),
        _critere("Glissement moyen (points)", None if moyen is None else round(moyen, 2),
                 f"≤ {2 * glissement_modele:g}", moyen is not None and moyen <= 2 * glissement_modele),
        _critere("Santé de la stratégie", (sante or {}).get("statut", "inconnu"), "pas en pause",
                 (sante or {}).get("statut") != "pause"),
    ]
    return {"porte": "demo", "franchie": all(c["ok"] for c in criteres), "criteres": criteres}


def porte_boost_reel(journal, *, sante: dict | None = None, jours_min: int = 60) -> dict:
    trades = [t for t in journal.trades(5000) if t.get("mode") == "reel" and (t.get("profil") or "pro") == "pro"]
    fermes = [t for t in trades if t.get("ferme_le")]
    premier = min((t["ouvert_le"] for t in trades), default=None)
    net = sum(t["resultat_devise"] or 0 for t in fermes)
    criteres = [
        _critere("Jours de PRO en réel", round(_jours_depuis(premier), 1), f"≥ {jours_min}",
                 _jours_depuis(premier) >= jours_min),
        _critere("Résultat net du PRO réel", round(net, 2), "> 0", fermes and net > 0),
        _critere("Santé de la stratégie", (sante or {}).get("statut", "inconnu"), "pas en pause",
                 (sante or {}).get("statut") != "pause"),
    ]
    return {"porte": "boost_reel", "franchie": all(c["ok"] for c in criteres), "criteres": criteres}

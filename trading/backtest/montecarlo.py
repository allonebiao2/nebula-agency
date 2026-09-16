# -*- coding: utf-8 -*-
"""
Monte Carlo : ce que la variance normale d'une stratégie peut faire à un compte.

    « Le backtest ment, le walk-forward vérifie, le marché décide. »

Un walk-forward donne UNE histoire. Le marché en rejouera une autre, faite des
mêmes trades dans un ordre différent. On rejoue donc les trades hors échantillon
des milliers de fois, par BLOCS de trades consécutifs (les séries de pertes
arrivent groupées quand le régime change : tirer les trades un par un les
disperserait et sous-estimerait les creux), à n'importe quel risque par trade.

Ce que ça sert à décider, et pourquoi c'est obligatoire :
  · UN SEUIL D'ARRÊT se place AU-DELÀ du bruit. Mesuré le 2026-09-16 : un arrêt à
    −10 % avec 1 % de risque est touché 99 % du temps sur quinze ans, par une
    stratégie qui gagne. Un seuil qui se déclenche sur la variance normale arrête un
    système sain et apprend à l'opérateur à désactiver ses protections.
  · UN RISQUE ÉLEVÉ se choisit en connaissant ses probabilités de ruine. C'est ce que
    l'interface affiche au moment de régler le profil BOOST.

⚠️ Le Monte Carlo ne crée pas d'avantage : il redistribue celui des trades. Si les
trades n'en ont pas, aucun risque ne les rend rentables.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np

HORIZON_CALIBRAGE_ANS = 2.0     # un arrêt doit tenir deux ans de variance normale
MARGE_CALIBRAGE = 1.2           # au-delà du p99, pas dessus
PLAFOND_ARRET = 35.0            # plafond du code (config.PLAFOND_DRAWDOWN_TOTAL)


def rendements_en_R(rapport: dict) -> np.ndarray:
    """Les R hors échantillon d'un rapport de walk-forward.

    Les rapports récents portent `trades_R`. Les anciens n'ont que la courbe
    d'équité : on retrouve R en divisant le rendement de chaque trade par le risque
    nominal (1 %). C'est une approximation (la taille est arrondie au lot), dite.
    """
    if rapport.get("trades_R"):
        return np.asarray(rapport["trades_R"], dtype=float)
    courbe = rapport.get("courbe_equite") or []
    if len(courbe) < 2:
        return np.array([])
    equite = np.array([rapport.get("capital_initial", courbe[0][1])] + [e for _, e in courbe], dtype=float)
    return np.diff(equite) / equite[:-1] / 0.01


def simuler(R: np.ndarray, *, risque_pct: float, n_trades: int, tirages: int = 10_000,
            bloc: int = 5, graine: int = 7) -> dict:
    """Rejoue `n_trades` trades tirés par blocs, `tirages` fois, à `risque_pct` % par trade."""
    R = np.asarray(R, dtype=float)
    R = R[np.isfinite(R)]
    if len(R) < 10 or n_trades < 1:
        return {"valide": False, "raison": f"{len(R)} trades : trop peu pour simuler"}
    rng = np.random.default_rng(graine)
    bloc = max(1, min(bloc, len(R)))
    nb_blocs = math.ceil(n_trades / bloc)
    departs = rng.integers(0, len(R) - bloc + 1, size=(tirages, nb_blocs))
    idx = (departs[:, :, None] + np.arange(bloc)[None, None, :]).reshape(tirages, -1)[:, :n_trades]
    rendements = np.maximum(R[idx] * risque_pct / 100.0, -0.999)
    courbe = np.cumprod(1.0 + rendements, axis=1)
    sommets = np.maximum.accumulate(np.concatenate([np.ones((tirages, 1)), courbe], axis=1), axis=1)[:, 1:]
    dd = (1.0 - courbe / sommets).max(axis=1) * 100
    final = (courbe[:, -1] - 1.0) * 100

    def p(x):
        return float(np.mean(x))

    return {
        "valide": True, "risque_pct": risque_pct, "n_trades": n_trades, "tirages": tirages,
        "bloc": bloc, "esperance_R": float(R.mean()), "trades_source": int(len(R)),
        "drawdown": {"p50": float(np.percentile(dd, 50)), "p95": float(np.percentile(dd, 95)),
                     "p99": float(np.percentile(dd, 99))},
        "p_drawdown": {str(s): p(dd >= s) for s in (10, 20, 30, 50, 80)},
        "resultat": {"p5": float(np.percentile(final, 5)), "p50": float(np.percentile(final, 50)),
                     "p95": float(np.percentile(final, 95))},
        "p_perte": p(final < 0),
    }


def seuil_arret_calibre(R: np.ndarray, *, risque_pct: float, trades_par_an: float) -> dict:
    """Le drawdown d'arrêt total qui ne se déclenche PAS sur deux ans de variance normale."""
    n = max(10, int(round(trades_par_an * HORIZON_CALIBRAGE_ANS)))
    sim = simuler(R, risque_pct=risque_pct, n_trades=n)
    if not sim["valide"]:
        return {"valide": False, "raison": sim["raison"]}
    brut = sim["drawdown"]["p99"] * MARGE_CALIBRAGE
    return {
        "valide": True, "seuil_pct": float(min(PLAFOND_ARRET, max(5.0, math.ceil(brut)))),
        "plafonne": brut > PLAFOND_ARRET, "p95": sim["drawdown"]["p95"],
        "p99": sim["drawdown"]["p99"], "horizon_trades": n, "risque_pct": risque_pct,
    }


# --------------------------------------------------------------------------- #
#  Lecture du rapport actif
# --------------------------------------------------------------------------- #

def rapport_actif(dossier: Path, strategie: str, timeframe: str, garder_weekend: bool,
                  symbole: str = "EURUSD") -> dict | None:
    variante = "sans_weekend" if garder_weekend else "reference"
    choix = None
    for p in sorted(dossier.glob(f"walkforward_{strategie}_{symbole.upper()}_{timeframe}*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:                                      # noqa: BLE001
            continue
        if d.get("variante", "reference") == variante:
            return d
        choix = choix or d
    return choix


@lru_cache(maxsize=64)
def _cache(chemin: str, mtime: float, risque_pct: float, horizon_ans: float) -> dict:
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    R = rendements_en_R(d)
    par_an = (d.get("metriques") or {}).get("trades_par_mois", 2.3) * 12
    sim = simuler(R, risque_pct=risque_pct, n_trades=max(10, int(round(par_an * horizon_ans))))
    sim["trades_par_an"] = par_an
    sim["credible"] = d.get("credible")
    return sim


def pour_interface(dossier: Path, strategie: str, timeframe: str, garder_weekend: bool,
                   risque_pct: float, horizon_ans: float = 1.0, symbole: str = "EURUSD") -> dict:
    variante = "sans_weekend" if garder_weekend else "reference"
    candidats = [p for p in sorted(dossier.glob(
        f"walkforward_{strategie}_{symbole.upper()}_{timeframe}*.json"))]
    choisi = None
    for p in candidats:
        try:
            if json.loads(p.read_text(encoding="utf-8")).get("variante", "reference") == variante:
                choisi = p
                break
        except Exception:                                      # noqa: BLE001
            continue
    choisi = choisi or (candidats[0] if candidats else None)
    if not choisi:
        return {"valide": False, "raison": "aucun walk-forward pour cette stratégie"}
    sim = dict(_cache(str(choisi), choisi.stat().st_mtime, float(risque_pct), float(horizon_ans)))
    sim["rapport"] = choisi.name
    sim["horizon_ans"] = horizon_ans
    return sim

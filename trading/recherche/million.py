# -*- coding: utf-8 -*-
"""
L'objectif du million, mesuré et non promis.

À partir des R RÉELLEMENT obtenus hors échantillon, on rejoue le compte des milliers de
fois (tirage par blocs, comme `backtest/montecarlo.py`) et on répond à trois questions :
  · quelle probabilité d'atteindre 1 000 000 $ depuis le capital de départ, en N années ?
  · en combien de temps, quand ça arrive ?
  · quelle probabilité de perdre la moitié du capital avant ?

⚠️ Une espérance négative ne s'améliore pas avec le risque : elle ruine plus vite.
⚠️ Les chiffres supposent que l'avenir ressemble au passé mesuré. C'est déjà une hypothèse
généreuse pour un échantillon de quelques centaines de trades.
"""
from __future__ import annotations

import math

import numpy as np


def projeter(R, *, trades_par_mois: float, capital: float, risque_pct: float, objectif: float = 1_000_000,
             annees: int = 10, tirages: int = 4000, bloc: int = 5, graine: int = 11) -> dict:
    R = np.asarray(R, float)
    R = R[np.isfinite(R)]
    if len(R) < 30 or trades_par_mois <= 0:
        return {"valide": False, "raison": f"{len(R)} trades : trop peu pour projeter"}
    n = int(math.ceil(trades_par_mois * 12 * annees))
    rng = np.random.default_rng(graine)
    bloc = max(1, min(bloc, len(R)))
    departs = rng.integers(0, len(R) - bloc + 1, size=(tirages, math.ceil(n / bloc)))
    idx = (departs[:, :, None] + np.arange(bloc)[None, None, :]).reshape(tirages, -1)[:, :n]
    croissance = np.cumprod(1.0 + np.maximum(R[idx] * risque_pct / 100.0, -0.999), axis=1)
    multiple = objectif / capital
    atteint = croissance >= multiple
    atteint_ok = atteint.any(axis=1)
    premier = np.where(atteint_ok, atteint.argmax(axis=1), -1)
    sommets = np.maximum.accumulate(np.concatenate([np.ones((tirages, 1)), croissance], axis=1), axis=1)[:, 1:]
    moitie = ((1.0 - croissance / sommets) >= 0.5).any(axis=1)
    mois_atteinte = premier[atteint_ok] / trades_par_mois
    return {
        "valide": True, "capital": capital, "objectif": objectif, "risque_pct": risque_pct, "annees": annees,
        "esperance_R": float(R.mean()), "trades_par_mois": trades_par_mois,
        "p_million": float(atteint_ok.mean()),
        "mois_median_si_atteint": float(np.median(mois_atteinte)) if len(mois_atteinte) else None,
        "p_perdre_moitie": float(moitie.mean()),
        "capital_median_fin": float(np.median(croissance[:, -1]) * capital),
    }


def croissance_necessaire(capital: float, objectif: float = 1_000_000) -> dict:
    """Le rendement mensuel composé qu'il faut tenir, sans une seule mauvaise année."""
    multiple = objectif / capital
    return {str(a): (multiple ** (1 / (12 * a)) - 1) * 100 for a in (3, 5, 10, 20)}

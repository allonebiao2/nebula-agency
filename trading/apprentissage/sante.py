# -*- coding: utf-8 -*-
"""
La santé d'une stratégie : son avantage est-il en train de mourir ?

    « Le bot ne cherche pas à avoir raison, il cherche à être rentable. »

Le cahier des charges proposait « pause après 5 pertes d'affilée ». Mesuré : pour
une stratégie à 40 % de réussite, 5 pertes d'affilée arrivent 97 % du temps sur
100 trades. La règle aurait mis en pause une stratégie saine par pure variance.

On surveille donc un ÉCART STATISTIQUE à ce que le walk-forward a mesuré, avec un
CUSUM unilatéral (Page, 1954) : chaque trade ajoute (R − espérance attendue + k),
la somme ne garde que les écarts défavorables, et l'alarme sonne quand elle
descend sous −h. Une mauvaise série isolée se résorbe ; une dérive durable, non.

Le seuil h n'est pas un chiffre rond : il est CALIBRÉ sur les trades du walk-forward
eux-mêmes, pour qu'une stratégie qui se comporte exactement comme mesuré ne
déclenche une fausse alarme que dans 5 % des cas sur 100 trades.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

FAUSSE_ALARME_CIBLE = 0.05
HORIZON_CALIBRAGE = 100


def cusum_bas(R, mu0: float, k: float) -> np.ndarray:
    """La trajectoire du CUSUM inférieur : 0 tant que tout va bien, négatif sinon."""
    s, trajet = 0.0, []
    for x in R:
        s = min(0.0, s + (x - mu0 + k))
        trajet.append(s)
    return np.array(trajet)


def calibrer_h(R_ref: np.ndarray, *, k: float, n: int = HORIZON_CALIBRAGE,
               cible: float = FAUSSE_ALARME_CIBLE, tirages: int = 4000, graine: int = 11) -> float:
    """Le seuil h tel que P(alarme sur n trades | stratégie inchangée) ≈ cible."""
    R_ref = np.asarray(R_ref, dtype=float)
    mu0 = float(R_ref.mean())
    rng = np.random.default_rng(graine)
    tirs = R_ref[rng.integers(0, len(R_ref), size=(tirages, n))]
    minima = np.empty(tirages)
    for j in range(tirages):
        s, m = 0.0, 0.0
        for x in tirs[j]:
            s = min(0.0, s + (x - mu0 + k))
            m = min(m, s)
        minima[j] = m
    # l'alarme sonne si le minimum passe sous -h : on veut P(minimum < -h) = cible
    return float(-np.percentile(minima, 100 * cible))


@lru_cache(maxsize=32)
def _reference(cle: str, R_tuple: tuple) -> tuple[float, float, float]:
    R = np.array(R_tuple)
    sigma = float(R.std()) or 1.0
    k = 0.5 * sigma                       # détecte une baisse d'environ un écart-type
    return float(R.mean()), k, calibrer_h(R, k=k)


def diagnostiquer(R_live, R_reference, *, cle: str = "") -> dict:
    """Statut d'une stratégie à partir de ses trades réels et de sa référence walk-forward."""
    R_ref = np.asarray(R_reference, dtype=float)
    R_ref = R_ref[np.isfinite(R_ref)]
    R_live = [float(x) for x in R_live if x is not None and np.isfinite(x)]
    if len(R_ref) < 30:
        return {"statut": "inconnu", "message": "pas de référence walk-forward suffisante", "n": len(R_live)}
    mu0, k, h = _reference(cle or str(len(R_ref)), tuple(np.round(R_ref, 6)))
    if not R_live:
        return {"statut": "saine", "n": 0, "S": 0.0, "h": h, "k": k, "esperance_reference": mu0,
                "esperance_live": None, "message": "aucun trade réel encore : rien à surveiller"}
    trajet = cusum_bas(R_live, mu0, k)
    S = float(trajet[-1])
    if trajet.min() < -h and S < -h / 2:
        statut, message = "pause", (
            f"écart défavorable durable : CUSUM {S:.1f} sous le seuil −{h:.1f} calibré sur le "
            f"walk-forward. L'espérance réelle ({np.mean(R_live):+.2f} R sur {len(R_live)} trades) "
            f"ne ressemble plus à la mesure ({mu0:+.2f} R).")
    elif S < -h / 2:
        statut, message = "surveillance", (
            f"écart défavorable en cours (CUSUM {S:.1f}, alarme à −{h:.1f}) : rien d'anormal à ce "
            f"stade, une série perdante ordinaire y ressemble.")
    else:
        statut, message = "saine", (f"conforme à la mesure : espérance réelle {np.mean(R_live):+.2f} R "
                                    f"sur {len(R_live)} trades, référence {mu0:+.2f} R.")
    return {"statut": statut, "n": len(R_live), "S": S, "h": h, "k": k,
            "esperance_reference": mu0, "esperance_live": float(np.mean(R_live)),
            "trajet": [float(x) for x in trajet[-200:]], "message": message}

# -*- coding: utf-8 -*-
"""
La règle de Mongazi, écrite une fois : **un trade s'ouvre et se ferme le même jour.**

    from .intraday import fenetres, masque_entree, fin_de_journee, jour_ny

Tout est en heure de NEW YORK, jamais en UTC : le rollover de l'EUR/USD est à 17:00 New York toute
l'année (21:00 UTC l'été, 22:00 l'hiver) et la clôture cash du NAS100 à 16:00 New York. Un masque
écrit en UTC se décale d'une heure deux fois par an, c'est-à-dire justement aux dates où les séances
changent de forme.

Les bornes, par instrument :
  · **fenêtre d'entrée** : on n'ouvre pas une position qu'on n'aura pas le temps de laisser vivre.
  · **clôture forcée** : au-delà, toute position est fermée à la clôture de la barre. Elle vient
    AVANT le moment cher (rollover EUR/USD à 17:00, où le spread médian passe de 3 à 35 points et
    touche 100 ; clôture cash du NAS100 à 16:00, où le CFD s'écarte).
Le vendredi, la clôture forcée tombe à la même heure : rien ne passe le week-end.
"""
from __future__ import annotations

import numpy as np

from .spread_horaire import minute_ny

# (première minute d'entrée, dernière minute d'entrée, minute de clôture forcée), heure de New York
FENETRES = {
    "EURUSD": (2 * 60, 16 * 60 + 45, 16 * 60 + 55),      # Francfort → juste avant le rollover
    "NAS100": (3 * 60, 15 * 60 + 45, 15 * 60 + 55),      # pré-marché → juste avant la clôture cash
}


def fenetres(base: str) -> tuple[int, int, int]:
    return FENETRES[base.upper()]


def minutes_et_jours(temps: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(minute du jour, jour de semaine) en heure de New York. Calcul unique, à garder."""
    return minute_ny(temps)


def masque_entree(base: str, temps: np.ndarray, *, minute=None, jour=None) -> np.ndarray:
    """Les barres où une entrée est permise : dans la fenêtre, du lundi au vendredi."""
    debut, fin, _ = fenetres(base)
    if minute is None:
        minute, jour = minutes_et_jours(temps)
    return (minute >= debut) & (minute <= fin) & (jour < 5)


def fin_de_journee(base: str, temps: np.ndarray, *, minute=None, jour=None) -> np.ndarray:
    """Les barres où toute position ouverte est fermée : la journée est finie.
    ⚠️ C'est un masque de SORTIE, pas d'entrée : il est vrai sur toutes les barres tardives, pas
    seulement la première, pour qu'une position ouverte plus tard ne survive jamais à la nuit."""
    _, _, cloture = fenetres(base)
    if minute is None:
        minute, jour = minutes_et_jours(temps)
    return (minute >= cloture) | (jour >= 5)


def jour_ny(temps: np.ndarray) -> np.ndarray:
    """La journée de New York à laquelle appartient chaque barre (pour grouper par jour)."""
    import pandas as pd
    idx = pd.DatetimeIndex(temps).tz_localize("UTC").tz_convert("America/New_York")
    return idx.normalize().tz_localize(None).to_numpy().astype("datetime64[D]")


def barres_restantes(base: str, temps: np.ndarray, minutes_par_barre: int = 1,
                     *, minute=None, jour=None) -> np.ndarray:
    """Combien de barres restent avant la clôture forcée : le plafond de durée d'un trade ouvert
    à cette barre. Zéro ou moins = trop tard pour entrer."""
    _, _, cloture = fenetres(base)
    if minute is None:
        minute, jour = minutes_et_jours(temps)
    reste = (cloture - minute) // minutes_par_barre
    return np.where(jour < 5, reste, 0).astype(np.int64)

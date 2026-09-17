# -*- coding: utf-8 -*-
"""
Ce qu'on sait à la clôture d'une barre, et rien de plus.

    from .caracteristiques import construire
    X = construire(serie)          # dict nom -> tableau aligné sur les barres

Toutes les valeurs de l'indice `i` ne dépendent que des barres `<= i`. C'est la règle qui décide si
une recherche vaut quelque chose : une seule caractéristique qui regarde une barre future rend tout
le reste faux, et le résultat est toujours magnifique.

Les extrêmes de la VEILLE et de la journée en cours sont calculés en heure de New York, comme les
séances (`intraday.py`). Le plus haut « du jour » à l'indice i est celui des barres du jour
**jusqu'à i**, jamais celui de la journée entière : c'est là que se cache la fuite la plus courante.
"""
from __future__ import annotations

import numpy as np

from .banc import Serie
from .etiquettes import atr
from .intraday import fenetres, jour_ny, minutes_et_jours


def _cumul_par_jour(valeurs: np.ndarray, jour: np.ndarray, quoi: str) -> np.ndarray:
    """Maximum (ou minimum) depuis le début de la journée, barre à barre, sans regarder plus loin."""
    out = np.empty(len(valeurs))
    debuts = np.flatnonzero(np.concatenate(([True], jour[1:] != jour[:-1])))
    fins = np.append(debuts[1:], len(valeurs))
    for a, b in zip(debuts, fins):
        out[a:b] = np.maximum.accumulate(valeurs[a:b]) if quoi == "max" else np.minimum.accumulate(valeurs[a:b])
    return out


def _valeur_veille(valeurs_du_jour: np.ndarray, jour: np.ndarray, quoi: str) -> np.ndarray:
    """Pour chaque barre, l'extrême de la journée PRÉCÉDENTE (complète)."""
    import pandas as pd
    s = pd.Series(valeurs_du_jour)
    par_jour = s.groupby(jour).max() if quoi == "max" else s.groupby(jour).min()
    veille = par_jour.shift(1)
    return veille.reindex(jour).to_numpy()


def _ecart_type_roulant(x: np.ndarray, n: int) -> np.ndarray:
    """Écart-type des n dernières valeurs, barre courante comprise."""
    import pandas as pd
    return pd.Series(x).rolling(n, min_periods=n // 2).std().to_numpy()


def construire(serie: Serie, *, annonces: np.ndarray | None = None,
               surprises: tuple[np.ndarray, np.ndarray, np.ndarray] | None = None) -> dict[str, np.ndarray]:
    """Le dictionnaire des caractéristiques. Chaque valeur est un tableau de la longueur de la série."""
    o, h, b, c = serie.ouverture, serie.haut, serie.bas, serie.cloture
    n = len(c)
    minute, jsem = minutes_et_jours(serie.temps)
    jour = jour_ny(serie.temps)
    a14, a60 = atr(serie, 14), atr(serie, 60)
    par_barre = max(1, serie.minutes)
    a_jour = atr(serie, max(20, int(1440 / par_barre)))        # la volatilité d'une journée entière
    X: dict[str, np.ndarray] = {}

    X["minute_ny"] = minute.astype(np.float64)
    X["heure_ny"] = (minute // 60).astype(np.float64)
    X["jour_semaine"] = jsem.astype(np.float64)
    ouverture_seance = fenetres(serie.base)[0]
    X["barres_depuis_ouverture"] = ((minute - ouverture_seance) / par_barre).astype(np.float64)

    # --- volatilité : la même mesure, rapportée à elle-même -------------------------------------
    with np.errstate(invalid="ignore", divide="ignore"):
        X["vol_relative"] = a14 / a_jour
        X["vol_heure"] = a14 / a60
    X["atr14_points"] = a14 / serie.point
    X["cout_R_atr14x2"] = np.where(a14 > 0, 2 * serie.couts_prix() / (2 * a14), np.nan)

    # --- mouvement récent, en unités de volatilité ----------------------------------------------
    for k in (1, 3, 5, 15, 60, 120, 240):
        p = max(1, int(k / par_barre))
        prec = np.concatenate((np.full(p, np.nan), c[:-p]))
        with np.errstate(invalid="ignore", divide="ignore"):
            X[f"ret_{k}min"] = (c - prec) / a14
    corps = c - o
    amplitude = np.maximum(h - b, 1e-12)
    X["corps_relatif"] = corps / amplitude
    X["ibs"] = (c - b) / amplitude
    X["meche_haute"] = (h - np.maximum(o, c)) / amplitude
    X["meche_basse"] = (np.minimum(o, c) - b) / amplitude

    # --- structure de la journée ------------------------------------------------------------------
    haut_jour = _cumul_par_jour(h, jour, "max")
    bas_jour = _cumul_par_jour(b, jour, "min")
    with np.errstate(invalid="ignore", divide="ignore"):
        etendue = np.maximum(haut_jour - bas_jour, 1e-12)
        X["position_dans_le_jour"] = (c - bas_jour) / etendue
        X["etendue_jour_atr"] = etendue / a_jour
        X["dist_haut_jour"] = (haut_jour - c) / a14
        X["dist_bas_jour"] = (c - bas_jour) / a14
        haut_veille = _valeur_veille(h, jour, "max")
        bas_veille = _valeur_veille(b, jour, "min")
        X["dist_haut_veille"] = (haut_veille - c) / a14
        X["dist_bas_veille"] = (c - bas_veille) / a14
        ouverture_jour = o[np.searchsorted(jour, jour, side="left")]   # le prix d'ouverture du jour
        X["depuis_ouverture_jour"] = (c - ouverture_jour) / a14

    # --- tendance de fond (aucune barre future) ---------------------------------------------------
    import pandas as pd
    for p in (50, 200):
        ema = pd.Series(c).ewm(span=p, adjust=False, min_periods=p).mean().to_numpy()
        with np.errstate(invalid="ignore", divide="ignore"):
            X[f"ecart_ema{p}"] = (c - ema) / a14
        X[f"pente_ema{p}"] = np.concatenate((np.full(p, np.nan), (ema[p:] - ema[:-p]) / np.maximum(a14[p:], 1e-12)))

    # --- suite de bougies et balayages de niveaux --------------------------------------------------
    hausse = np.sign(c - o)
    serie_meme_sens = np.zeros(n)
    for i in range(1, n):
        serie_meme_sens[i] = serie_meme_sens[i - 1] + hausse[i] if hausse[i] == hausse[i - 1] else hausse[i]
    X["bougies_meme_sens"] = serie_meme_sens
    haut_avant = np.concatenate(([np.nan], haut_jour[:-1]))      # le plus haut du jour AVANT cette barre
    bas_avant = np.concatenate(([np.nan], bas_jour[:-1]))
    X["balayage_haut_jour"] = ((h > haut_avant) & (c < haut_avant)).astype(float)
    X["balayage_bas_jour"] = ((b < bas_avant) & (c > bas_avant)).astype(float)
    X["balayage_haut_veille"] = ((h > haut_veille) & (c < haut_veille)).astype(float)
    X["balayage_bas_veille"] = ((b < bas_veille) & (c > bas_veille)).astype(float)

    # --- volume de ticks : le seul flux d'ordres dont on dispose ------------------------------------
    if serie.volume is not None and len(serie.volume) == n:
        v = np.asarray(serie.volume, float)
        moyenne = pd.Series(v).rolling(60, min_periods=20).mean().to_numpy()
        with np.errstate(invalid="ignore", divide="ignore"):
            X["volume_relatif"] = v / np.maximum(moyenne, 1e-9)
            X["volume_relatif_jour"] = v / np.maximum(
                pd.Series(v).rolling(max(20, int(1440 / par_barre)), min_periods=50).mean().to_numpy(), 1e-9)

    # --- coût de la minute (il fait partie de l'information) --------------------------------------
    X["spread_points"] = 2 * serie.couts_prix() / serie.point

    # --- annonces --------------------------------------------------------------------------------
    if annonces is not None and len(annonces):
        t = serie.temps.astype("datetime64[s]").astype("int64")
        ann = np.sort(np.asarray(annonces).astype("datetime64[s]").astype("int64"))
        i_apres = np.searchsorted(ann, t, side="right")
        depuis = np.where(i_apres > 0, (t - ann[np.maximum(i_apres - 1, 0)]) / 60.0, 1e9)
        avant = np.where(i_apres < len(ann), (ann[np.minimum(i_apres, len(ann) - 1)] - t) / 60.0, 1e9)
        X["minutes_depuis_annonce"] = np.minimum(depuis, 1e4)
        X["minutes_avant_annonce"] = np.minimum(avant, 1e4)

    # --- la SURPRISE : ce qui bouge un marché n'est pas l'annonce, c'est l'écart au consensus -----
    if surprises is not None and len(surprises[0]):
        t = serie.temps.astype("datetime64[s]").astype("int64")
        ts, signe, ampleur = (np.asarray(x) for x in surprises)
        ts = ts.astype("datetime64[s]").astype("int64")
        k = np.searchsorted(ts, t, side="right") - 1
        valide = k >= 0
        kk = np.maximum(k, 0)
        minutes = np.where(valide, (t - ts[kk]) / 60.0, 1e9)
        # L'effet d'une annonce s'éteint : une surprise d'il y a trois heures n'est plus un signal.
        poids = np.where(minutes <= 240, np.exp(-minutes / 60.0), 0.0)
        X["surprise_signe"] = np.where(valide, signe[kk], 0.0) * poids
        X["surprise_ampleur"] = np.where(valide, ampleur[kk], 0.0) * poids
        X["minutes_depuis_surprise"] = np.minimum(minutes, 1e4)

    return {k: np.asarray(v, dtype=np.float64) for k, v in X.items()}


# Les découpages utilisés par la carte et par la recherche de règles. Fixés ici, une fois, pour que
# deux vagues ne découpent pas la même caractéristique de deux façons.
DECOUPAGES = {
    "minute_ny": ("quantiles", 0),          # traité à part : une case par tranche de 15 minutes
    "heure_ny": ("valeurs", 0),
    "jour_semaine": ("valeurs", 0),
}
QUANTILES = (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0)


def bords(valeurs: np.ndarray, nom: str) -> np.ndarray:
    """Les bords de cases d'une caractéristique : ses quantiles, sauf si elle est déjà discrète."""
    mode = DECOUPAGES.get(nom, ("quantiles", 0))[0]
    fini = valeurs[np.isfinite(valeurs)]
    if not len(fini):
        return np.array([0.0, 1.0])
    if mode == "valeurs":
        return np.unique(fini)
    return np.unique(np.quantile(fini, QUANTILES))


def cases(valeurs: np.ndarray, nom: str) -> tuple[np.ndarray, np.ndarray]:
    """(numéro de case par barre, bords). Case -1 = valeur manquante."""
    br = bords(valeurs, nom)
    if DECOUPAGES.get(nom, ("quantiles", 0))[0] == "valeurs":
        idx = np.searchsorted(br, valeurs)
        idx = np.where(np.isfinite(valeurs), np.clip(idx, 0, len(br) - 1), -1)
        return idx.astype(np.int64), br
    idx = np.clip(np.searchsorted(br, valeurs, side="right") - 1, 0, len(br) - 2)
    return np.where(np.isfinite(valeurs), idx, -1).astype(np.int64), br

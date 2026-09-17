# -*- coding: utf-8 -*-
"""
Les deux méthodes des vidéos envoyées par Mongazi le 2026-09-17, rendues mécaniques.

Chaque règle est reliée au moment de la vidéo qui la donne (transcriptions locales dans
`trading/rapports/recherche/videos/`, hors dépôt).

A · MambaFx, « The Only 1-Minute Scalping Strategy You'll EVER NEED » (US30)
    [00:48] « on commence TOUJOURS sur le 5 minutes » : support touché plusieurs fois
            ([01:15] « one, two, three, four touches ») ou résistance rejetée ([06:16]).
    [02:02] en 1 minute, structure : plus haut plus haut, plus bas plus haut, puis
            [02:19] une bougie qui prend les plus hauts = cassure -> entrée.
    [02:50] stop serré ; [03:32] objectif 1:3 à 1:5 ; [09:13] « 30 minutes par jour ».
    Rendu mécanique : zone = extrême des N dernières barres de zone touché par au
    moins `touches` creux (ou sommets) à `tol_atr` ATR près ; prix revenu tester la zone
    dans les `recence` dernières barres ; cassure du dernier sommet de structure après un
    plus bas plus haut ; stop sous ce plus bas plus haut.

B · Hugo FX, « J'ai trouvé la MEILLEURE Stratégie de Scalping M1 pour 2026 ! »
    [00:36] CRT H1 : la bougie 2 prend le bas de la bougie 1 et CLÔTURE dans son range ;
            [02:09] objectif = l'autre côté du range ; [06:51] attendre la clôture H1.
    [06:57] en M15, attendre un NOUVEAU swing low (3 bougies en V) qui n'invalide pas le
            CRT ; [08:52] « pas de swing low, pas de trade ».
    [12:52] en M1 : retour en « discount » (sous 50 % de l'impulsion) dans un PD array,
            [13:31] stop derrière ; [22:16] « protégé par le 0,79 ».
    [24:09] séances Londres et New York.
    Non modélisé, et c'est écrit : le passage au point mort [14:45] et les ajouts [22:54]
    (une seule position par instrument, règle maison).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..strategies.indicateurs import atr
from .banc import Agregat, Ordres, Serie, Signaux, agreger

ZONE_DE = {"M1": "M5", "M5": "M15", "M15": "H1", "H1": "H4"}
CRT_DE = {"M1": ("H1", "M15"), "M5": ("H1", "M15"), "M15": ("H1", "M15"), "H1": ("D1", "H4")}


def _minutes_locales(temps: np.ndarray, fuseau: str) -> np.ndarray:
    idx = pd.DatetimeIndex(temps).tz_localize("UTC").tz_convert(fuseau)
    return (idx.hour * 60 + idx.minute).to_numpy()


def seance_masque(serie: Serie, seance: str) -> np.ndarray:
    """Barres où une entrée est permise. Heure serveur Deriv = GMT+0 (profil du courtier)."""
    n = len(serie)
    if seance == "toutes":
        return np.ones(n, dtype=bool)
    ny = _minutes_locales(serie.temps, "America/New_York")
    lon = _minutes_locales(serie.temps, "Europe/London")
    if seance == "ouverture":        # MambaFx : les premières minutes de la séance cash
        masque = (ny >= 9 * 60 + 30) & (ny < 11 * 60)
        if serie.base == "EURUSD":
            masque |= (lon >= 7 * 60) & (lon < 9 * 60)
        return masque
    if seance == "londres_ny":       # Hugo FX : Londres le matin, New York l'après-midi
        return ((lon >= 7 * 60) & (lon < 11 * 60)) | ((ny >= 8 * 60 + 30) & (ny < 12 * 60))
    raise ValueError(seance)


# --------------------------------------------------------------------------- #
# A · MambaFx : zone M5, cassure de structure M1
# --------------------------------------------------------------------------- #
def _zones(z: Agregat, fenetre: int, tol_atr: float):
    """Support/résistance des `fenetre` dernières barres de zone CLOSES, et leurs touches."""
    n = len(z.cloture)
    a = atr(z.haut, z.bas, z.cloture, 14)
    support, resist = np.full(n, np.nan), np.full(n, np.nan)
    t_sup, t_res = np.zeros(n, np.int64), np.zeros(n, np.int64)
    creux = np.zeros(n, bool)
    sommet = np.zeros(n, bool)
    creux[1:-1] = (z.bas[1:-1] < z.bas[:-2]) & (z.bas[1:-1] <= z.bas[2:])
    sommet[1:-1] = (z.haut[1:-1] > z.haut[:-2]) & (z.haut[1:-1] >= z.haut[2:])
    for m in range(fenetre + 1, n):
        if np.isnan(a[m]):
            continue
        k0, k1 = m - fenetre, m            # creux en k confirmé à k+1 <= m
        s, r = z.bas[k0:k1 + 1].min(), z.haut[k0:k1 + 1].max()
        tol = tol_atr * a[m]
        support[m], resist[m] = s, r
        t_sup[m] = int((creux[k0:k1] & (z.bas[k0:k1] <= s + tol)).sum())
        t_res[m] = int((sommet[k0:k1] & (z.haut[k0:k1] >= r - tol)).sum())
    return support, resist, t_sup, t_res, a


def mamba_cassure(serie: Serie, *, touches: int = 3, rr: float = 3.0, seance: str = "ouverture",
                  tol_atr: float = 0.25, fenetre_zone: int = 48, recence: int = 30) -> Signaux:
    z = agreger(serie, ZONE_DE[serie.tf])
    support, resist, t_sup, t_res, a_zone = _zones(z, fenetre_zone, tol_atr)
    h, b, c = serie.haut, serie.bas, serie.cloture
    a = atr(h, b, c, 14)
    n = len(c)
    permis = seance_masque(serie, seance)
    sens, dist = np.zeros(n, np.int8), np.zeros(n)
    k = 2                                    # pivot = extrême de 5 barres, confirmé 2 barres après
    ph_val = ph_t = pl_val = pl_t = -1.0
    pl_prec = ph_prec = np.nan
    ph_hist, pl_hist = [], []                # (temps, valeur) des pivots confirmés
    for i in range(2 * k + 1, n):
        j = i - k                            # pivot candidat, confirmé à la clôture de i
        if h[j] == h[j - k:i + 1].max() and h[j] > h[j - 1]:
            ph_hist.append((j, h[j]))
        if b[j] == b[j - k:i + 1].min() and b[j] < b[j - 1]:
            pl_hist.append((j, b[j]))
        if not permis[i] or np.isnan(a[i]) or len(ph_hist) < 2 or len(pl_hist) < 2:
            continue
        zi = z.fermee_a[i]
        if zi < 0 or np.isnan(support[zi]):
            continue
        lo_recent, hi_recent = b[max(0, i - recence):i + 1].min(), h[max(0, i - recence):i + 1].max()
        tol = tol_atr * a_zone[zi]
        # --- achat : support tenu, plus bas plus haut, cassure du dernier sommet ---
        t_ph, v_ph = ph_hist[-1]
        apres = [p for p in pl_hist if p[0] > t_ph]
        avant = [p for p in pl_hist if p[0] < t_ph]
        if (t_sup[zi] >= touches and c[i] > support[zi] and lo_recent <= support[zi] + tol
                and apres and avant and apres[-1][1] > avant[-1][1]
                and c[i] > v_ph and c[i - 1] <= v_ph):
            stop = apres[-1][1] - 0.1 * a[i]
            sens[i], dist[i] = 1, c[i] - stop
            continue
        # --- vente : résistance tenue, plus haut plus bas, cassure du dernier creux ---
        t_pl, v_pl = pl_hist[-1]
        apres_h = [p for p in ph_hist if p[0] > t_pl]
        avant_h = [p for p in ph_hist if p[0] < t_pl]
        if (t_res[zi] >= touches and c[i] < resist[zi] and hi_recent >= resist[zi] - tol
                and apres_h and avant_h and apres_h[-1][1] < avant_h[-1][1]
                and c[i] < v_pl and c[i - 1] >= v_pl):
            stop = apres_h[-1][1] + 0.1 * a[i]
            sens[i], dist[i] = -1, stop - c[i]
        if len(ph_hist) > 50:
            del ph_hist[:25]
        if len(pl_hist) > 50:
            del pl_hist[:25]
    return Signaux(sens, dist, rr=rr, max_barres=36)


# --------------------------------------------------------------------------- #
# B · Hugo FX : CRT H1, swing M15, entrée en discount
# --------------------------------------------------------------------------- #
def hugo_crt(serie: Serie, *, fib: float = 0.5, stop: str = "swing", expiration: int = 4,
             seance: str = "londres_ny") -> Ordres:
    tf_crt, tf_swing = CRT_DE[serie.tf]
    H = agreger(serie, tf_crt)
    Q = agreger(serie, tf_swing)
    q_min = {"M15": 15, "H1": 60, "H4": 240}[tf_swing]
    h_min = {"H1": 60, "D1": 1440}[tf_crt]
    a_q = atr(Q.haut, Q.bas, Q.cloture, 14)
    fin_q = Q.debut + np.timedelta64(q_min * 60, "s")
    fin_base = serie.temps + np.timedelta64(serie.minutes * 60, "s")
    permis = seance_masque(serie, seance)
    poses, sens_l, lim_l, stop_l, cible_l, exp_l = [], [], [], [], [], []
    for j in range(1, len(H.cloture)):
        haut1, bas1 = H.haut[j - 1], H.bas[j - 1]
        haussier = H.bas[j] < bas1 and bas1 < H.cloture[j] < haut1
        baissier = H.haut[j] > haut1 and bas1 < H.cloture[j] < haut1
        if haussier == baissier:
            continue
        fin_crt = H.debut[j] + np.timedelta64(h_min * 60, "s")
        fin_fenetre = fin_crt + np.timedelta64(expiration * h_min * 60, "s")
        k0 = int(np.searchsorted(Q.debut, fin_crt))           # première barre swing APRÈS le CRT
        extreme_crt = H.bas[j] if haussier else H.haut[j]
        cible = haut1 if haussier else bas1
        for k in range(k0 + 1, len(Q.cloture) - 1):
            if fin_q[k + 1] > fin_fenetre:
                break
            if haussier:
                if Q.bas[k] <= extreme_crt or Q.haut[k] >= cible:   # invalidé ou déjà servi
                    break
                if not (Q.bas[k] < Q.bas[k - 1] and Q.bas[k] < Q.bas[k + 1]):
                    continue
                if Q.haut[k + 1] >= cible:
                    break
                sommet = max(Q.haut[k], Q.haut[k + 1])
                bas_sw = Q.bas[k]
                limite = sommet - fib * (sommet - bas_sw)
                niveau = bas_sw - 0.1 * a_q[k] if stop == "swing" else sommet - 0.79 * (sommet - bas_sw)
                s_ = 1
            else:
                if Q.haut[k] >= extreme_crt or Q.bas[k] <= cible:
                    break
                if not (Q.haut[k] > Q.haut[k - 1] and Q.haut[k] > Q.haut[k + 1]):
                    continue
                if Q.bas[k + 1] <= cible:
                    break
                creux = min(Q.bas[k], Q.bas[k + 1])
                haut_sw = Q.haut[k]
                limite = creux + fib * (haut_sw - creux)
                niveau = haut_sw + 0.1 * a_q[k] if stop == "swing" else creux + 0.79 * (haut_sw - creux)
                s_ = -1
            if np.isnan(a_q[k]):
                break
            pose = int(np.searchsorted(fin_base, fin_q[k + 1], side="left"))
            if pose >= len(serie) or not permis[min(pose + 1, len(serie) - 1)]:
                break
            expire = int(np.searchsorted(fin_base, fin_fenetre, side="left"))
            poses.append(pose)
            sens_l.append(s_)
            lim_l.append(limite)
            stop_l.append(niveau)
            cible_l.append(cible)
            exp_l.append(expire)
            break                                                  # un seul swing par CRT
    heures_max = 4 * 60 // serie.minutes
    return Ordres(np.array(poses, np.int64), np.array(sens_l, np.int8), np.array(lim_l, float),
                  np.array(stop_l, float), np.array(cible_l, float), np.array(exp_l, np.int64),
                  max_barres=max(1, heures_max))

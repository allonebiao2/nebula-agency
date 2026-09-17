# -*- coding: utf-8 -*-
"""
Les stratégies publiées « à haut taux de réussite », apprises et réécrites sans tricher.

Chaque candidate garde l'ENTRÉE telle que sa source la décrit. Ce qui change, et
c'est écrit à chaque fois :
  · un stop TOUJOURS (Connors n'en met pas : NEBULA ne trade jamais sans) ;
  · un objectif d'au moins 2 R (Mongazi, 2026-09-17), là où les sources visent
    souvent plus court que leur stop : c'est ce qui fabrique leurs « 80 % » ;
  · une sortie seulement par stop, objectif, temps ou fin de séance.

Sources (lues le 2026-09-17) :
  RSI(2)      StockCharts ChartSchool « RSI(2) » ; MQL5 article 17636 (M30, US500)
  BB + RSI    learn-forextrading.org « 5 min scalping Bollinger Bands and RSI » ;
              forextester.com « Bollinger Bands Scalping with RSI & Stochastic »
  IBS         Alvarez Quant Trading « IBS for mean reversion » ; WealthLab ;
              A. Pagonidis, « The IBS Effect » (NAAIM 2014)
  EMA200+Stoch ForexCracked « 200 EMA and Stochastic scalping » ; OpoFinance
  Range       London breakout (dailyforex, backtests GitHub adrian-baehler,
              MHZardary) ; Opening Range Breakout (tradetaurex)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..strategies.indicateurs import atr, bandes_bollinger, ema, ibs, rsi, sma, stochastique
from .banc import Candidate, Serie, Signaux


def _heures_locales(serie: Serie, fuseau: str) -> tuple[np.ndarray, np.ndarray]:
    """Minutes depuis minuit et jour, dans le fuseau du marché (heure d'été comprise).
    L'heure serveur de Deriv est GMT+0 : mesurée dans le profil du courtier."""
    idx = pd.DatetimeIndex(serie.temps).tz_localize("UTC").tz_convert(fuseau)
    minutes = (idx.hour * 60 + idx.minute).to_numpy()
    jours = (idx.year * 400 + idx.dayofyear).to_numpy()
    return minutes, jours


def _vide(serie: Serie):
    return np.zeros(len(serie), np.int8), np.zeros(len(serie), float)


# --------------------------------------------------------------------------- #
# 1. RSI(2) de Connors
# --------------------------------------------------------------------------- #
def rsi2_connors(serie: Serie, *, seuil: float = 5, stop_atr: float = 1.5, rr: float = 2.0) -> Signaux:
    c = serie.cloture
    r2, tendance, a = rsi(c, 2), sma(c, 200), atr(serie.haut, serie.bas, c, 14)
    sens, dist = _vide(serie)
    ok = ~np.isnan(r2) & ~np.isnan(tendance) & ~np.isnan(a)
    sens[ok & (c > tendance) & (r2 < seuil)] = 1
    sens[ok & (c < tendance) & (r2 > 100 - seuil)] = -1
    dist[ok] = stop_atr * a[ok]
    return Signaux(sens, dist, rr=rr)


# --------------------------------------------------------------------------- #
# 2. Bollinger + RSI(7) (+ Stochastique), scalping
# --------------------------------------------------------------------------- #
def bb_rsi_scalp(serie: Serie, *, niveau: float = 25, marge_atr: float = 0.3, rr: float = 2.0,
                 stochastique_exige: bool = False) -> Signaux:
    h, b, c = serie.haut, serie.bas, serie.cloture
    basse, _, haute = bandes_bollinger(c, 20, 2.0)
    r7 = rsi(c, 7)
    r7_moy = sma(np.nan_to_num(r7, nan=50.0), 7)
    k, _ = stochastique(h, b, c, 14, 3, 3)
    a = atr(h, b, c, 14)
    n = len(c)
    sens, dist = _vide(serie)
    fen = 3
    for i in range(fen + 20, n):
        if np.isnan(a[i]) or np.isnan(basse[i - fen]) or np.isnan(r7[i - 1]):
            continue
        croise_haut = r7[i] > r7_moy[i] and r7[i - 1] <= r7_moy[i - 1]
        croise_bas = r7[i] < r7_moy[i] and r7[i - 1] >= r7_moy[i - 1]
        dehors_bas = np.any(c[i - fen:i] < basse[i - fen:i])
        dehors_haut = np.any(c[i - fen:i] > haute[i - fen:i])
        rsi_min, rsi_max = np.nanmin(r7[i - fen:i + 1]), np.nanmax(r7[i - fen:i + 1])
        stoch_bas = not stochastique_exige or np.nanmin(k[i - fen:i + 1]) < 20
        stoch_haut = not stochastique_exige or np.nanmax(k[i - fen:i + 1]) > 80
        if dehors_bas and rsi_min < niveau and croise_haut and stoch_bas:
            stop = b[i - fen:i + 1].min() - marge_atr * a[i]
            sens[i], dist[i] = 1, c[i] - stop
        elif dehors_haut and rsi_max > 100 - niveau and croise_bas and stoch_haut:
            stop = h[i - fen:i + 1].max() + marge_atr * a[i]
            sens[i], dist[i] = -1, stop - c[i]
    return Signaux(sens, dist, rr=rr)


# --------------------------------------------------------------------------- #
# 3. IBS / barres consécutives (retour à la moyenne sur indice)
# --------------------------------------------------------------------------- #
def ibs_baisses(serie: Serie, *, mode: str = "ibs", stop_atr: float = 2.0, rr: float = 2.0) -> Signaux:
    h, b, c = serie.haut, serie.bas, serie.cloture
    tendance, a, force = sma(c, 200), atr(h, b, c, 14), ibs(h, b, c)
    sens, dist = _vide(serie)
    ok = ~np.isnan(tendance) & ~np.isnan(a)
    if mode == "ibs":
        achat, vente = force < 0.1, force > 0.9
    else:
        bas_dec = (b < np.roll(b, 1)) & (h < np.roll(h, 1))
        haut_cr = (h > np.roll(h, 1)) & (b > np.roll(b, 1))
        achat = bas_dec & np.roll(bas_dec, 1) & np.roll(bas_dec, 2)
        vente = haut_cr & np.roll(haut_cr, 1) & np.roll(haut_cr, 2)
        achat[:3] = vente[:3] = False
    sens[ok & (c > tendance) & achat] = 1
    # Le Nasdaq a une dérive haussière documentée : la source ne trade que l'achat.
    if serie.base != "NAS100":
        sens[ok & (c < tendance) & vente] = -1
    dist[ok] = stop_atr * a[ok]
    return Signaux(sens, dist, rr=rr)


# --------------------------------------------------------------------------- #
# 4. EMA 200 + Stochastique, pullback de tendance
# --------------------------------------------------------------------------- #
def ema_stoch_pullback(serie: Serie, *, niveau: float = 20, stop_atr: float = 1.5, rr: float = 2.0) -> Signaux:
    h, b, c = serie.haut, serie.bas, serie.cloture
    e200, a = ema(c, 200), atr(h, b, c, 14)
    k, d = stochastique(h, b, c, 14, 3, 3)
    sens, dist = _vide(serie)
    kp, dp = np.roll(k, 1), np.roll(d, 1)
    ok = ~np.isnan(e200) & ~np.isnan(a) & ~np.isnan(k) & ~np.isnan(dp)
    ok[0] = False
    haussier = (k > d) & (kp <= dp) & (kp < niveau) & (c > e200)
    baissier = (k < d) & (kp >= dp) & (kp > 100 - niveau) & (c < e200)
    sens[ok & haussier] = 1
    sens[ok & baissier] = -1
    dist[ok] = stop_atr * a[ok]
    return Signaux(sens, dist, rr=rr)


# --------------------------------------------------------------------------- #
# 5. Range de séance : Asie -> Londres (EUR/USD), ouverture US (NAS100)
# --------------------------------------------------------------------------- #
SEANCES = {
    # fuseau, début du range, fin du range, fin des entrées, sortie forcée (minutes locales)
    "EURUSD": ("Europe/London", 0, 7 * 60, 11 * 60, 16 * 60),
    "NAS100": ("America/New_York", 9 * 60 + 30, 10 * 60, 12 * 60, 15 * 60 + 45),
}


def range_seance(serie: Serie, *, mode: str = "cassure", stop: str = "oppose", rr: float = 2.0) -> Signaux:
    fuseau, r0, r1, e1, sortie = SEANCES[serie.base]
    minutes, jours = _heures_locales(serie, fuseau)
    h, b, c = serie.haut, serie.bas, serie.cloture
    a = atr(h, b, c, 14)
    n = len(c)
    sens, dist = _vide(serie)
    fin_seance = np.zeros(n, dtype=bool)
    fin_barre = minutes + serie.minutes
    fin_seance[(minutes < sortie) & (fin_barre >= sortie)] = True
    jour_courant, haut_r, bas_r, deja, extreme_h, extreme_b = -1, -np.inf, np.inf, False, -np.inf, np.inf
    for i in range(n):
        if jours[i] != jour_courant:
            jour_courant, haut_r, bas_r, deja = jours[i], -np.inf, np.inf, False
            extreme_h, extreme_b = -np.inf, np.inf
        m = minutes[i]
        if r0 <= m < r1:
            haut_r, bas_r = max(haut_r, h[i]), min(bas_r, b[i])
            continue
        if not (r1 <= m < e1) or deja or not np.isfinite(haut_r) or np.isnan(a[i]):
            continue
        extreme_h, extreme_b = max(extreme_h, h[i]), min(extreme_b, b[i])
        milieu = (haut_r + bas_r) / 2
        if mode == "cassure":
            if c[i] > haut_r:
                niveau = bas_r if stop == "oppose" else milieu
                sens[i], dist[i], deja = 1, c[i] - niveau, True
            elif c[i] < bas_r:
                niveau = haut_r if stop == "oppose" else milieu
                sens[i], dist[i], deja = -1, niveau - c[i], True
        else:   # retour : la mèche sort du range, la clôture y revient
            if h[i] > haut_r and c[i] < haut_r:
                sens[i], dist[i], deja = -1, extreme_h + 0.1 * a[i] - c[i], True
            elif b[i] < bas_r and c[i] > bas_r:
                sens[i], dist[i], deja = 1, c[i] - (extreme_b - 0.1 * a[i]), True
    return Signaux(sens, dist, rr=rr, fin_seance=fin_seance)


# --------------------------------------------------------------------------- #
# 6. Témoin : l'entrée au hasard (la barre à battre)
# --------------------------------------------------------------------------- #
def temoin_hasard(serie: Serie, *, graine: int = 1, stop_atr: float = 1.5, rr: float = 2.0) -> Signaux:
    rng = np.random.default_rng(graine)
    a = atr(serie.haut, serie.bas, serie.cloture, 14)
    n = len(serie)
    sens = np.where(rng.random(n) < 1 / 20, np.where(rng.random(n) < 0.5, 1, -1), 0).astype(np.int8)
    sens[np.isnan(a)] = 0
    return Signaux(sens, np.nan_to_num(stop_atr * a), rr=rr)


CANDIDATES = [
    Candidate("rsi2_connors", "RSI(2) de Connors", "StockCharts ; MQL5 17636", rsi2_connors,
              {"seuil": [5, 10], "stop_atr": [1.0, 2.0], "rr": [2.0, 3.0]}, ("M15", "H1")),
    Candidate("bb_rsi_scalp", "Bollinger + RSI(7) (+ Stochastique)", "learn-forextrading ; forextester",
              bb_rsi_scalp, {"niveau": [25, 30], "marge_atr": [0.2, 0.5], "rr": [2.0, 3.0],
                             "stochastique_exige": [False, True]}, ("M5", "M15")),
    Candidate("ibs_baisses", "IBS / 3 barres consécutives", "Alvarez ; WealthLab ; Pagonidis (NAAIM)",
              ibs_baisses, {"mode": ["ibs", "consecutifs"], "stop_atr": [1.5, 2.5], "rr": [2.0, 3.0]},
              ("M15", "H1")),
    Candidate("ema_stoch_pullback", "EMA 200 + Stochastique", "ForexCracked ; OpoFinance",
              ema_stoch_pullback, {"niveau": [20, 30], "stop_atr": [1.5, 2.0], "rr": [2.0, 3.0]},
              ("M5", "M15")),
    Candidate("range_seance", "Range de séance (Asie→Londres, ouverture US)",
              "dailyforex ; GitHub adrian-baehler, MHZardary ; tradetaurex (ORB)", range_seance,
              {"mode": ["cassure", "retour"], "stop": ["oppose", "milieu"], "rr": [2.0, 3.0]}, ("M15", "M5")),
]

TEMOIN = Candidate("temoin_hasard", "Témoin : entrée au hasard", "—", temoin_hasard,
                   {"graine": [1], "stop_atr": [1.5], "rr": [2.0]}, ("M5", "M15", "H1"))

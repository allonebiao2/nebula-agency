# -*- coding: utf-8 -*-
"""
Indicateurs, en numpy, calculés une fois pour toutes.

RÈGLE ABSOLUE, et c'est le mensonge n°1 des backtests : **un indicateur ne voit
jamais le futur**. Un canal de cassure se calcule sur les barres PRÉCÉDENTES,
sinon le prix qui casse le canal est celui-là même qui l'a défini, et le
backtest devient une machine à prédire le passé.

Toutes les fonctions ici renvoient un tableau aligné sur les barres, où
l'indice `i` ne dépend **que** des barres `<= i` (et, pour les canaux,
strictement `< i`).
"""
from __future__ import annotations

import numpy as np


def vrai_range(haut: np.ndarray, bas: np.ndarray, cloture: np.ndarray) -> np.ndarray:
    """True Range : l'amplitude réelle, gaps compris."""
    cloture_prec = np.concatenate(([cloture[0]], cloture[:-1]))
    return np.maximum.reduce([
        haut - bas,
        np.abs(haut - cloture_prec),
        np.abs(bas - cloture_prec),
    ])


def atr(haut: np.ndarray, bas: np.ndarray, cloture: np.ndarray,
        periode: int = 14) -> np.ndarray:
    """ATR au lissage de Wilder (RMA), celui qu'utilise MT5.

    Les `periode` premières valeurs sont NaN : pas assez d'histoire pour
    prétendre mesurer quoi que ce soit.
    """
    tr = vrai_range(haut, bas, cloture)
    out = np.full(len(tr), np.nan)
    if len(tr) <= periode:
        return out
    out[periode] = tr[1:periode + 1].mean()
    alpha = 1.0 / periode
    for i in range(periode + 1, len(tr)):
        out[i] = out[i - 1] + alpha * (tr[i] - out[i - 1])
    return out


def ema(valeurs: np.ndarray, periode: int) -> np.ndarray:
    out = np.full(len(valeurs), np.nan)
    if len(valeurs) < periode:
        return out
    out[periode - 1] = valeurs[:periode].mean()
    k = 2.0 / (periode + 1)
    for i in range(periode, len(valeurs)):
        out[i] = valeurs[i] * k + out[i - 1] * (1 - k)
    return out


def canal_donchian(haut: np.ndarray, bas: np.ndarray,
                   periode: int = 20) -> tuple[np.ndarray, np.ndarray]:
    """Plus haut et plus bas des `periode` barres PRÉCÉDENTES.

    Le décalage d'une barre n'est pas un détail de confort : sans lui, la barre
    qui casse le canal est celle qui l'a défini, et la cassure est garantie
    d'arriver. C'est ainsi qu'on fabrique un backtest à 3 000 %.
    """
    n = len(haut)
    hautes = np.full(n, np.nan)
    basses = np.full(n, np.nan)
    for i in range(periode, n):
        fenetre = slice(i - periode, i)          # exclut i : voilà le décalage
        hautes[i] = haut[fenetre].max()
        basses[i] = bas[fenetre].min()
    return hautes, basses


def ratio_efficacite(cloture: np.ndarray, periode: int = 20) -> np.ndarray:
    """Ratio d'efficacité de Kaufman : le marché va-t-il quelque part ?

    Distance parcourue / chemin réellement fait.
        proche de 1  ->  tendance nette, le prix avance sans zigzaguer
        proche de 0  ->  range, le prix s'agite sans se déplacer

    C'est notre détecteur de régime : une stratégie de cassure ne perd pas par
    malchance dans un range, elle y perd **par construction**.
    """
    n = len(cloture)
    out = np.full(n, np.nan)
    variations = np.abs(np.diff(cloture, prepend=cloture[0]))
    for i in range(periode, n):
        direction = abs(cloture[i] - cloture[i - periode])
        chemin = variations[i - periode + 1:i + 1].sum()
        out[i] = direction / chemin if chemin > 0 else 0.0
    return out


def pente_ema(cloture: np.ndarray, periode: int = 50,
              recul: int = 5) -> np.ndarray:
    """Pente de l'EMA, normalisée par le prix : le filtre de tendance.

    Exprimée en fraction du prix pour rester comparable d'une époque à l'autre :
    50 points de pente ne veulent pas dire la même chose à 0,95 qu'à 1,60.
    """
    moyenne = ema(cloture, periode)
    out = np.full(len(cloture), np.nan)
    for i in range(periode + recul, len(cloture)):
        if not np.isnan(moyenne[i]) and not np.isnan(moyenne[i - recul]) and cloture[i]:
            out[i] = (moyenne[i] - moyenne[i - recul]) / cloture[i]
    return out


def percentile_glissant(valeurs: np.ndarray, periode: int = 100) -> np.ndarray:
    """Position de la valeur courante dans sa propre histoire récente (0 à 1).

    Sert à dire « la volatilité est-elle haute *pour ce marché-ci* », sans
    seuil absolu qui vieillirait mal.
    """
    n = len(valeurs)
    out = np.full(n, np.nan)
    for i in range(periode, n):
        fenetre = valeurs[i - periode:i]
        fenetre = fenetre[~np.isnan(fenetre)]
        if len(fenetre) and not np.isnan(valeurs[i]):
            out[i] = (fenetre < valeurs[i]).mean()
    return out


def sma(valeurs: np.ndarray, periode: int) -> np.ndarray:
    """Moyenne mobile simple ; l'indice i ne dépend que des barres <= i."""
    out = np.full(len(valeurs), np.nan)
    if len(valeurs) < periode:
        return out
    cumul = np.cumsum(np.insert(valeurs.astype(float), 0, 0.0))
    out[periode - 1:] = (cumul[periode:] - cumul[:-periode]) / periode
    return out


def rsi(cloture: np.ndarray, periode: int = 14) -> np.ndarray:
    """RSI au lissage de Wilder, celui de MT5 (le RSI(2) de Connors est periode=2)."""
    n = len(cloture)
    out = np.full(n, np.nan)
    if n <= periode:
        return out
    delta = np.diff(cloture.astype(float))
    hausses, baisses = np.maximum(delta, 0.0), np.maximum(-delta, 0.0)
    moy_h, moy_b = hausses[:periode].mean(), baisses[:periode].mean()
    out[periode] = 100.0 if moy_b == 0 else 100.0 - 100.0 / (1.0 + moy_h / moy_b)
    for i in range(periode + 1, n):
        moy_h = (moy_h * (periode - 1) + hausses[i - 1]) / periode
        moy_b = (moy_b * (periode - 1) + baisses[i - 1]) / periode
        out[i] = 100.0 if moy_b == 0 else 100.0 - 100.0 / (1.0 + moy_h / moy_b)
    return out


def bandes_bollinger(cloture: np.ndarray, periode: int = 20,
                     ecarts: float = 2.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(basse, milieu, haute), écart-type de population comme MT5."""
    milieu = sma(cloture, periode)
    carre = sma(cloture.astype(float) ** 2, periode)
    ecart = np.sqrt(np.maximum(carre - milieu ** 2, 0.0))
    return milieu - ecarts * ecart, milieu, milieu + ecarts * ecart


def stochastique(haut: np.ndarray, bas: np.ndarray, cloture: np.ndarray,
                 periode_k: int = 14, lissage_k: int = 3,
                 periode_d: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """Stochastique lent (%K lissé, %D), sur les barres <= i."""
    n = len(cloture)
    k_brut = np.full(n, np.nan)
    if n >= periode_k:
        from numpy.lib.stride_tricks import sliding_window_view
        hh = sliding_window_view(haut, periode_k).max(axis=1)
        ll = sliding_window_view(bas, periode_k).min(axis=1)
        amplitude = hh - ll
        with np.errstate(divide="ignore", invalid="ignore"):
            k_brut[periode_k - 1:] = np.where(amplitude > 0,
                                              100.0 * (cloture[periode_k - 1:] - ll) / amplitude, 50.0)
    k = _sma_nan(k_brut, lissage_k)
    return k, _sma_nan(k, periode_d)


def _sma_nan(valeurs: np.ndarray, periode: int) -> np.ndarray:
    out = np.full(len(valeurs), np.nan)
    valides = np.flatnonzero(~np.isnan(valeurs))
    if len(valides) == 0:
        return out
    d = valides[0]
    out[d:] = sma(valeurs[d:], periode)
    return out


def ibs(haut: np.ndarray, bas: np.ndarray, cloture: np.ndarray) -> np.ndarray:
    """Internal Bar Strength : où la barre ferme dans son amplitude (0 = au plus bas)."""
    amplitude = haut - bas
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(amplitude > 0, (cloture - bas) / amplitude, 0.5)

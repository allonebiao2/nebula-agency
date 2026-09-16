# -*- coding: utf-8 -*-
"""
Ce qui change d'un instrument à l'autre, et qui ne doit JAMAIS être un nombre commun.

Trois choses, toutes des fonctions pures (aucun terminal) :

  NOMS        « NAS100 » s'appelle « US Tech 100 » chez Deriv, « USTEC » ailleurs,
              « EURUSDm » chez Exness. On cherche l'instrument, pas une chaîne.
  PLAFONDS    un plafond de spread en POINTS n'a de sens que pour un instrument.
              ⛔ Mesuré le 2026-09-16 : le plafond de 20 points calibré sur l'EUR/USD
              (spread médian 2 à 3 points) refusait 92,8 % des bougies du NAS100, dont
              le spread fixe est de 70 points chez Deriv. Le walk-forward du NAS100
              « 2 trades en 12 mois » mesurait ce plafond, pas l'indice.
  FACTEURS    EUR/USD et NAS100 sont deux symboles mais partagent le dollar : le
              risque se compte par facteur, pas par ligne de position.
"""
from __future__ import annotations

ALIAS = {
    "NAS100": ("NAS100", "US Tech 100", "USTEC", "US100", "NDX100", "NQ100", "USTECH", "NASDAQ100",
               "US TECH 100", "Nasdaq 100", "USTech100"),
    "EURUSD": ("EURUSD",),
}

# Les facteurs de risque de chaque instrument. Un instrument inconnu est son propre
# facteur ; une paire de change à six lettres porte ses deux devises.
FACTEURS = {
    "EURUSD": ("EUR", "USD"),
    "NAS100": ("USD", "actions US"),
}


def _normaliser(nom: str) -> str:
    return "".join(ch for ch in nom.upper() if ch.isalnum())


def candidats_symbole(base: str, noms) -> list[str]:
    """Les noms du terminal qui désignent `base` : exact, puis alias, puis suffixe de compte
    (EURUSDm chez Exness, US Tech 100.cash…).

    ⚠️ Un suffixe de compte commence par une LETTRE ou un point : « US1000 » n'est pas
    « US100 » suivi d'un suffixe, c'est un autre indice.
    """
    noms = list(noms)
    base_u = base.upper()
    exacts = [n for n in noms if n.upper() == base_u]
    if exacts:
        return exacts
    alias = {_normaliser(a) for a in ALIAS.get(base_u, (base_u,))}
    trouves = [n for n in noms if _normaliser(n) in alias]
    if trouves:
        return trouves

    def suffixe_de_compte(nom: str) -> bool:
        n = _normaliser(nom)
        for a in alias:
            reste = n[len(a):]
            if n.startswith(a) and len(reste) <= 4 and not reste[:1].isdigit():
                return True
        return False
    return [n for n in noms if suffixe_de_compte(n)]


def base_de(nom: str) -> str:
    """L'instrument NEBULA derrière un nom de courtier (« US Tech 100 » → « NAS100 »)."""
    for base in ALIAS:
        if candidats_symbole(base, [nom]):
            return base
    return nom.upper()


def facteurs_de(base: str) -> tuple[str, ...]:
    b = base_de(base)
    if b in FACTEURS:
        return FACTEURS[b]
    if len(b) == 6 and b.isalpha():
        return (b[:3], b[3:])
    return (b,)


def exposition_par_facteur(positions) -> dict[str, float]:
    """`positions` : couples (instrument, risque en %). Somme du risque par facteur."""
    expo: dict[str, float] = {}
    for instrument, risque_pct in positions:
        for f in facteurs_de(instrument):
            expo[f] = expo.get(f, 0.0) + float(risque_pct or 0.0)
    return expo


def limites_execution(execution, base: str, point: float) -> tuple[float, float]:
    """(spread maximal, déviation maximale) en POINTS de cet instrument.

    `[execution] spread_max_points` et `slippage_max_points` restent la règle de
    l'EUR/USD et de tout instrument sans ligne propre. Un instrument listé dans
    `[execution.par_instrument]` porte ses plafonds en PRIX (2,0 = deux points
    d'indice), convertis ici avec le point de CE courtier : la taille du point d'un
    indice change d'un courtier à l'autre, un plafond en points ne voyagerait pas.
    """
    propre = (getattr(execution, "par_instrument", None) or {}).get(base_de(base), {})
    spread = (propre["spread_max_prix"] / point if propre.get("spread_max_prix") and point
              else float(execution.spread_max_points))
    deviation = (propre["slippage_max_prix"] / point if propre.get("slippage_max_prix") and point
                 else float(execution.slippage_max_points))
    return spread, deviation

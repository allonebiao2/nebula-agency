# -*- coding: utf-8 -*-
"""
Les mécanismes du profil BOOST qui dépendent de l'histoire du compte.

    « Survivre d'abord, performer ensuite. »

Deux idées du cahier des charges de Mongazi, gardées parce qu'elles sont justes :

  PALIERS ANTI-MARTINGALE. À chaque doublement du capital depuis l'activation du
  profil, le risque par trade descend d'un cran (10 → 5 → 3 → 2 → 1,5 → 1 %). Plus
  on a à perdre, moins on risque. Le contraire de la martingale, qui risque plus
  quand on a moins. Le risque ne remonte JAMAIS au-dessus de celui qui a été choisi,
  même si le capital retombe sous son point de départ.

  POCHE ÉPARGNE. À chaque +50 % depuis la dernière mise à l'abri, 25 % du gain
  sortent du capital de travail : le dimensionnement ne les voit plus, ils ne sont
  plus jamais risqués. MT5 n'a pas d'API de retrait ; c'est la seule façon honnête
  de « retirer » sans toucher à l'argent du client.

Mêmes fonctions pour le backtest et pour l'agent : une règle qui n'existe que d'un
côté fait diverger la mesure et le compte.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass


@dataclass
class EtatProfil:
    profil: str = "pro"
    capital_depart: float = 0.0        # capital au moment où le profil a été activé
    reference_poche: float = 0.0       # équité à la dernière mise à l'abri
    verrouille: float = 0.0            # total mis à l'abri, dans l'unité du compte
    mises_a_l_abri: int = 0

    def en_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def depuis_json(cls, texte: str) -> "EtatProfil":
        return cls(**json.loads(texte))


def initialiser(profil: str, equite: float) -> EtatProfil:
    return EtatProfil(profil=profil, capital_depart=equite, reference_poche=equite)


def echelle(risque_choisi: float, paliers: tuple[float, ...]) -> list[float]:
    """Le risque choisi, puis les paliers strictement inférieurs, dans l'ordre."""
    return [risque_choisi] + [p for p in paliers if p < risque_choisi - 1e-9]


def risque_courant(cfg, etat: EtatProfil | None, equite: float) -> tuple[float, str]:
    """Le risque par trade à appliquer maintenant, et pourquoi."""
    r = cfg.risque.risque_par_trade_pct
    p = cfg.profil
    if not p.boost or not p.paliers_actifs or not p.paliers or not etat or etat.capital_depart <= 0:
        return r, ""
    niveau = math.floor(math.log2(equite / etat.capital_depart)) if equite > etat.capital_depart else 0
    marches = echelle(r, p.paliers)
    applique = marches[min(niveau, len(marches) - 1)]
    if applique < r:
        return applique, (f"palier {niveau} : capital ×{equite / etat.capital_depart:.1f} depuis "
                          f"l'activation, risque ramené de {r:g} % à {applique:g} %")
    return applique, ""


def mettre_a_l_abri(cfg, etat: EtatProfil | None, equite: float) -> float:
    """Verrouille une part des gains si le seuil est franchi. Renvoie le montant verrouillé à
    l'instant (0 si rien). Mute `etat`."""
    p = cfg.profil
    if not etat or not p.boost or p.poche_declencheur_pct <= 0 or p.poche_part_pct <= 0:
        return 0.0
    if etat.reference_poche <= 0:
        etat.reference_poche = equite
        return 0.0
    disponible = equite - etat.verrouille
    if disponible < etat.reference_poche * (1 + p.poche_declencheur_pct / 100):
        return 0.0
    part = (disponible - etat.reference_poche) * p.poche_part_pct / 100
    etat.verrouille += part
    etat.reference_poche = equite - etat.verrouille
    etat.mises_a_l_abri += 1
    return part


def capital_disponible(solde: float, etat: EtatProfil | None) -> float:
    """Le solde moins la poche épargne : ce que le dimensionnement a le droit de voir."""
    return max(0.0, solde - (etat.verrouille if etat else 0.0))

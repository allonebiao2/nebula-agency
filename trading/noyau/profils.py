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

  ÉCHELLE PAR LE DRAWDOWN (plan de Mongazi, 2026-09-18). On risque le taux plein
  tant que le capital est à son SOMMET ; dès qu'on passe sous le sommet on descend
  d'un cran (6 → 4 %), plus bas d'un cran de plus (→ 3 %), et **on remonte au taux
  plein dès qu'un nouveau sommet est touché**. Même esprit que les paliers
  ci-dessus : on risque moins quand on va moins bien, jamais l'inverse.
  ⚠️ Ce qu'elle apporte, mesuré sur 1 467 vrais trades : le pire recul passe de
  28,8 % à 23,7 %, et surtout, **si l'avantage disparaît, la probabilité de ruine
  passe de 46,6 % à 5,8 %**. Elle ne fait pas gagner plus : elle fait survivre.

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
    sommet_equite: float = 0.0         # LE « TOP » : le plus haut capital atteint depuis l'activation

    def en_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def depuis_json(cls, texte: str) -> "EtatProfil":
        return cls(**json.loads(texte))


def initialiser(profil: str, equite: float) -> EtatProfil:
    return EtatProfil(profil=profil, capital_depart=equite, reference_poche=equite,
                      sommet_equite=equite)


def maj_sommet(etat: EtatProfil | None, equite: float) -> float:
    """Mettre à jour le sommet du capital. À appeler à chaque clôture de trade.

    ⚠️ Si personne ne l'appelle, l'échelle croit qu'on est toujours au sommet et ne descend
    jamais d'un cran : un contrôle du QC le vérifie, parce que c'est une panne silencieuse.
    """
    if etat is None:
        return equite
    etat.sommet_equite = max(etat.sommet_equite, float(equite))
    return etat.sommet_equite


def drawdown_courant(etat: EtatProfil | None, equite: float) -> float:
    if not etat or etat.sommet_equite <= 0:
        return 0.0
    return max(0.0, 1.0 - equite / etat.sommet_equite)


def risque_du_drawdown(paliers: tuple, risque_plein: float, drawdown: float) -> tuple[float, str]:
    """Le risque de l'échelle par drawdown. `paliers` = ((seuil, risque), …), seuils croissants.

    Le premier palier (seuil 0) est le taux plein, appliqué au sommet. Chaque seuil franchi fait
    descendre d'un cran, et **rien ne fait remonter tant que le sommet n'est pas repris** : c'est le
    retour au vert de la planche.

    ⚠️ L'échelle est **ancrée sur le risque choisi**, pas écrite en dur. Les paliers 6-4-3 sont lus
    comme des proportions du premier (1 · 2/3 · 1/2) : à 6 % choisi ils donnent 6-4-3, à 10 % ils
    donnent 10-6,7-5, à 1 % ils donnent 1-0,67-0,5. Sans cet ancrage, une échelle écrite pour 6 %
    plafonnerait à 6 % quelqu'un qui a choisi 10, et changerait sa décision sans le lui dire.
    """
    if not paliers:
        return risque_plein, ""
    plein_echelle = float(paliers[0][1]) or risque_plein
    choisi, seuil_atteint = risque_plein, 0.0
    for seuil, risque in paliers:
        if drawdown >= seuil - 1e-12:
            choisi = risque_plein * (float(risque) / plein_echelle)
            seuil_atteint = float(seuil)
    choisi = min(choisi, risque_plein)
    if choisi < risque_plein - 1e-9:
        return choisi, (f"échelle du drawdown : capital à -{100 * drawdown:.1f} % de son sommet "
                        f"(palier -{100 * seuil_atteint:.0f} %), risque ramené de "
                        f"{risque_plein:g} % à {choisi:g} %")
    return choisi, ""


def echelle(risque_choisi: float, paliers: tuple[float, ...]) -> list[float]:
    """Le risque choisi, puis les paliers strictement inférieurs, dans l'ordre."""
    return [risque_choisi] + [p for p in paliers if p < risque_choisi - 1e-9]


def risque_courant(cfg, etat: EtatProfil | None, equite: float) -> tuple[float, str]:
    """Le risque par trade à appliquer maintenant, et pourquoi.

    **Le point unique où le risque est décidé** : l'agent en direct et les backtests passent tous
    les deux ici. Une règle qui n'existerait que d'un côté ferait diverger la mesure et le compte.
    Deux échelles peuvent agir, et on garde toujours **la plus prudente des deux** :
      · celle des doublements de capital (anti-martingale historique) ;
      · celle du drawdown (plan de Mongazi) : plein tarif au sommet, moins en dessous.
    """
    r = cfg.risque.risque_par_trade_pct
    p = cfg.profil
    motifs = []
    applique = r
    if etat and etat.capital_depart > 0 and p.boost and p.paliers_actifs and p.paliers:
        niveau = math.floor(math.log2(equite / etat.capital_depart)) if equite > etat.capital_depart else 0
        marches = echelle(r, p.paliers)
        par_doublement = marches[min(niveau, len(marches) - 1)]
        if par_doublement < applique:
            applique = par_doublement
            motifs.append(f"palier {niveau} : capital ×{equite / etat.capital_depart:.1f} depuis "
                          f"l'activation, risque ramené de {r:g} % à {par_doublement:g} %")
    if etat and getattr(p, "paliers_drawdown", ()):
        par_drawdown, motif = risque_du_drawdown(p.paliers_drawdown, r,
                                                 drawdown_courant(etat, equite))
        if par_drawdown < applique:
            applique = par_drawdown
            if motif:
                motifs.append(motif)
    return applique, " · ".join(motifs)


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

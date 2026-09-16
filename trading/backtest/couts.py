# -*- coding: utf-8 -*-
"""
Ce que le courtier prend. Facturé sur CHAQUE trade du backtest.

Un backtest sans coûts n'est pas une mesure, c'est une publicité. Et l'erreur
n'est pas petite : sur une stratégie qui gagne 15 pips nets, 2 pips de spread
représentent 13 % du brut. Sur une stratégie de scalping, ils représentent tout.

Quatre coûts, et on les facture tous les quatre :

  SPREAD      payé à l'entrée ET à la sortie. On facture le spread MÉDIAN
              mesuré chez le courtier, pas celui de la vitrine publicitaire.
  COMMISSION  par lot et par sens, sur les comptes « raw ».
  SLIPPAGE    l'écart entre le prix demandé et le prix obtenu. Toujours
              défavorable en moyenne : c'est de l'antisélection, pas du bruit
              symétrique. Un backtest qui le modélise centré sur zéro ment.
  SWAP        le portage, par nuit. Négligeable en intraday, décisif en swing.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..noyau.risque import SpecsSymbole


@dataclass(frozen=True)
class ModeleCouts:
    """Les coûts d'un courtier donné, pour un symbole donné.

    À construire depuis `Courtier.couts()` — mesuré — et non à la main.
    """
    spread_points: float               # médian mesuré
    spread_points_max: float | None = None
    commission_par_lot_par_sens: float = 0.0
    slippage_points: float = 0.5       # défavorable, toujours
    swap_long_points: float = 0.0      # par nuit, en points
    swap_short_points: float = 0.0
    triple_swap_mercredi: bool = True  # le roll du week-end tombe le mercredi

    @classmethod
    def depuis_mesure(cls, couts, specs: SpecsSymbole,
                      commission_par_lot_par_sens: float = 0.0) -> "ModeleCouts":
        """Construit le modèle à partir de ce qu'on a LU chez le courtier."""
        return cls(
            spread_points=couts.spread_fiable,
            spread_points_max=couts.spread_max_observe_points,
            commission_par_lot_par_sens=commission_par_lot_par_sens,
            swap_long_points=couts.swap_long,
            swap_short_points=couts.swap_short,
        )

    # --- Facturation --------------------------------------------------------
    def cout_aller_retour_points(self) -> float:
        """Spread + slippage, à l'entrée et à la sortie, en points."""
        return self.spread_points + 2 * self.slippage_points

    def cout_aller_retour_devise(self, lots: float, specs: SpecsSymbole) -> float:
        points = self.cout_aller_retour_points()
        commission = 2 * self.commission_par_lot_par_sens * lots
        return points * lots * specs.valeur_point_par_lot + commission

    def portage_devise(self, *, sens: str, lots: float, nuits: int,
                       specs: SpecsSymbole, mercredis: int = 0) -> float:
        """Le swap accumulé. Positif = crédité, négatif = débité."""
        par_nuit = self.swap_long_points if sens == "achat" else self.swap_short_points
        nuits_facturees = nuits + (2 * mercredis if self.triple_swap_mercredi else 0)
        return par_nuit * nuits_facturees * lots * specs.valeur_point_par_lot

    def prix_entree(self, *, sens: str, prix_theorique: float,
                    specs: SpecsSymbole) -> float:
        """Le prix réellement obtenu à l'entrée : toujours du mauvais côté.

        En achat on paie le ASK (= mid + spread/2) et le slippage nous pousse
        encore plus haut. En vente, l'inverse. Un backtest qui entre au prix de
        clôture surestime chaque trade du spread entier.
        """
        penalite = (self.spread_points / 2 + self.slippage_points) * specs.point
        return prix_theorique + penalite if sens == "achat" else prix_theorique - penalite

    def prix_sortie(self, *, sens: str, prix_theorique: float,
                    specs: SpecsSymbole) -> float:
        """Le prix réellement obtenu à la sortie : du mauvais côté aussi."""
        penalite = (self.spread_points / 2 + self.slippage_points) * specs.point
        return prix_theorique - penalite if sens == "achat" else prix_theorique + penalite

    def en_R(self, points_de_risque: float) -> float:
        """Le coût aller-retour exprimé en fraction du risque.

        C'est LE chiffre qui décide de l'unité de temps. Sur EUR/USD à 1,5 pip :
            stop H4 de 70 pips  ->  0,02 R   (négligeable)
            stop M5 de 8 pips   ->  0,19 R   (il mange toute l'espérance)
        """
        return self.cout_aller_retour_points() / points_de_risque if points_de_risque else 0.0

    def __str__(self) -> str:
        c = (f" + {self.commission_par_lot_par_sens:g}/lot/sens"
             if self.commission_par_lot_par_sens else "")
        return (f"spread {self.spread_points:g} pts · slippage "
                f"{self.slippage_points:g} pts/sens{c} · "
                f"aller-retour {self.cout_aller_retour_points():g} pts")


# Repères, à remplacer par la mesure dès que le courtier répond.
# Ils servent à faire tourner le moteur avant la connexion, jamais à conclure.
REPERE_EURUSD_STANDARD = ModeleCouts(spread_points=15, slippage_points=5)
REPERE_EURUSD_RAW = ModeleCouts(spread_points=3, slippage_points=5,
                                commission_par_lot_par_sens=3.5)

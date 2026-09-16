# -*- coding: utf-8 -*-
"""
Cassure de canal, filtrée par la tendance et par le régime.

LA THÈSE, en une phrase : *les cycles de politique monétaire et les flux de
portage font que les devises vont quelque part pendant des semaines ; quand le
prix sort de son couloir récent dans le sens où il se dirige déjà, il continue
plus souvent qu'il ne rebrousse.*

C'est le système de suivi de tendance le mieux documenté sur plusieurs
décennies (les Tortues de Dennis, 1983). Ce n'est pas une garantie : son edge a
largement décliné depuis, il est connu de tout le monde, et il perd de l'argent
dans les marchés en range. D'où les deux filtres.

Son profil est ingrat et il faut le savoir AVANT de le vivre :
  · taux de réussite bas (35 à 45 %)
  · rentable par quelques gros gagnants, pas par la régularité
  · séries de 6 à 8 pertes parfaitement normales
Un opérateur qui ignore ça coupe le système pendant sa série noire, c'est-à-dire
exactement au mauvais moment.
"""
from __future__ import annotations

import numpy as np

from ..noyau.plan import ACHAT, VENTE, PlanDeTrade
from .base import Barres, ContexteStrategie, Strategie
from .indicateurs import atr, canal_donchian, pente_ema, ratio_efficacite


class CassureDonchian(Strategie):
    nom = "cassure_donchian"
    libelle = "Cassure de canal (Donchian)"
    these_generale = ("Le prix qui sort de son couloir récent dans le sens de sa "
                      "tendance continue plus souvent qu'il ne rebrousse.")

    def __init__(self, *, periode_canal: int = 20, periode_atr: int = 14,
                 atr_stop: float = 2.0, rr: float = 2.0,
                 periode_ema: int = 50, efficacite_min: float = 0.30):
        super().__init__(periode_canal=periode_canal, periode_atr=periode_atr,
                         atr_stop=atr_stop, rr=rr, periode_ema=periode_ema,
                         efficacite_min=efficacite_min)
        self.periode_canal = periode_canal
        self.periode_atr = periode_atr
        self.atr_stop = atr_stop
        self.rr = rr
        self.periode_ema = periode_ema
        self.efficacite_min = efficacite_min

    # ------------------------------------------------------------------ #
    def preparer(self, barres: Barres) -> None:
        self._atr = atr(barres.haut, barres.bas, barres.cloture, self.periode_atr)
        self._canal_haut, self._canal_bas = canal_donchian(
            barres.haut, barres.bas, self.periode_canal)
        self._pente = pente_ema(barres.cloture, self.periode_ema)
        self._efficacite = ratio_efficacite(barres.cloture, self.periode_canal)
        self._prete = True

    def regime_a(self, i: int) -> str:
        e = self._efficacite[i]
        if np.isnan(e):
            return "inconnu"
        return "tendance" if e >= self.efficacite_min else "range"

    def regime_favorable(self, ctx: ContexteStrategie) -> bool:
        """Une cassure dans un range ne perd pas par malchance : par construction."""
        return self.regime_a(ctx.i) == "tendance"

    # ------------------------------------------------------------------ #
    def signal(self, ctx: ContexteStrategie) -> PlanDeTrade | None:
        i, b = ctx.i, ctx.barres
        haut_c, bas_c = self._canal_haut[i], self._canal_bas[i]
        pente, atr_i = self._pente[i], self._atr[i]

        if np.isnan(haut_c) or np.isnan(bas_c) or np.isnan(pente) or np.isnan(atr_i):
            return None
        if atr_i <= 0:
            return None
        if self.regime_a(i) != "tendance":
            return None

        cloture = float(b.cloture[i])
        risque = self.atr_stop * float(atr_i)

        # --- Cassure haussière, tendance haussière -------------------------
        if cloture > haut_c and pente > 0:
            return PlanDeTrade(
                symbole=b.symbole or "?", sens=ACHAT,
                entree=cloture,
                stop=cloture - risque,
                objectif=cloture + self.rr * risque,
                these=(f"Sortie par le haut du couloir de {self.periode_canal} barres "
                       f"({haut_c:.5f}), dans le sens de la tendance, marché directionnel "
                       f"(efficacité {self._efficacite[i]:.2f})."),
                atr=float(atr_i), horodatage=ctx.maintenant, strategie=self.nom,
                contexte=self._contexte(i, haut_c, "haussiere"),
            )

        # --- Cassure baissière, tendance baissière -------------------------
        if cloture < bas_c and pente < 0:
            return PlanDeTrade(
                symbole=b.symbole or "?", sens=VENTE,
                entree=cloture,
                stop=cloture + risque,
                objectif=cloture - self.rr * risque,
                these=(f"Sortie par le bas du couloir de {self.periode_canal} barres "
                       f"({bas_c:.5f}), dans le sens de la tendance, marché directionnel "
                       f"(efficacité {self._efficacite[i]:.2f})."),
                atr=float(atr_i), horodatage=ctx.maintenant, strategie=self.nom,
                contexte=self._contexte(i, bas_c, "baissiere"),
            )
        return None

    def _contexte(self, i: int, borne: float, sens: str) -> dict:
        """Ce qui sera relu par le modèle de meta-labeling. Il faut le poser
        MAINTENANT : reconstitué après coup, il contiendrait le futur."""
        return {
            "borne_canal": float(borne),
            "sens_cassure": sens,
            "atr": float(self._atr[i]),
            "efficacite": float(self._efficacite[i]),
            "pente_ema": float(self._pente[i]),
            "periode_canal": self.periode_canal,
        }

    @property
    def espace_parametres(self) -> dict[str, list]:
        """Volontairement petit : 3 x 3 x 2 = 18 combinaisons.

        Plus l'espace est large, plus il est facile de trouver par hasard un
        réglage qui a bien marché sur le passé. Un balayage de 10 000
        combinaisons ne trouve pas un edge, il trouve du bruit.
        """
        return {
            "periode_canal": [20, 40, 55],
            "atr_stop": [1.5, 2.0, 3.0],
            "rr": [2.0, 3.0],
        }

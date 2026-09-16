# -*- coding: utf-8 -*-
"""
Retour à la moyenne, seulement quand le marché ne va nulle part.

LA THÈSE, en une phrase : *quand un marché tourne en rond, un écart brutal à sa
moyenne récente se referme plus souvent qu'il ne se prolonge.*

C'est l'exact complément de la cassure : elle gagne en tendance et perd en
range, celle-ci gagne en range et se fait écraser en tendance. D'où le filtre
de régime, qui est ici une question de survie : un retour à la moyenne dans un
marché qui part est la définition même de « rattraper un couteau qui tombe ».

Son profil, à connaître AVANT de le vivre :
  · taux de réussite élevé (50 à 60 %)
  · gains plus petits que les pertes en moyenne
  · perd rarement, mais quand un range se transforme en tendance, il perd
    plusieurs fois de suite
"""
from __future__ import annotations

import numpy as np

from ..noyau.plan import ACHAT, VENTE, PlanDeTrade
from .base import Barres, ContexteStrategie, Strategie
from .indicateurs import atr, ema, ratio_efficacite


def _ecart_type_glissant(valeurs: np.ndarray, periode: int) -> np.ndarray:
    n = len(valeurs)
    out = np.full(n, np.nan)
    if n < periode:
        return out
    fenetres = np.lib.stride_tricks.sliding_window_view(valeurs, periode)
    out[periode - 1:] = fenetres.std(axis=1)
    return out


class RetourMoyenne(Strategie):
    nom = "retour_moyenne"
    libelle = "Retour à la moyenne"
    these_generale = ("Dans un marché qui tourne en rond, un écart brutal à la moyenne "
                      "récente se referme plus souvent qu'il ne se prolonge.")

    def __init__(self, *, periode: int = 20, ecarts: float = 2.0, periode_atr: int = 14,
                 atr_stop: float = 1.5, rr: float = 1.5, efficacite_max: float = 0.25):
        super().__init__(periode=periode, ecarts=ecarts, periode_atr=periode_atr,
                         atr_stop=atr_stop, rr=rr, efficacite_max=efficacite_max)
        self.periode = periode
        self.ecarts = ecarts
        self.periode_atr = periode_atr
        self.atr_stop = atr_stop
        self.rr = rr
        self.efficacite_max = efficacite_max

    def preparer(self, barres: Barres) -> None:
        self._atr = atr(barres.haut, barres.bas, barres.cloture, self.periode_atr)
        self._moyenne = ema(barres.cloture, self.periode)
        self._ecart = _ecart_type_glissant(barres.cloture, self.periode)
        self._efficacite = ratio_efficacite(barres.cloture, self.periode)
        self._prete = True

    def regime_a(self, i: int) -> str:
        e = self._efficacite[i]
        if np.isnan(e):
            return "inconnu"
        return "range" if e <= self.efficacite_max else "tendance"

    def regime_favorable(self, ctx: ContexteStrategie) -> bool:
        return self.regime_a(ctx.i) == "range"

    def signal(self, ctx: ContexteStrategie) -> PlanDeTrade | None:
        i, b = ctx.i, ctx.barres
        moy, ec, atr_i = self._moyenne[i], self._ecart[i], self._atr[i]
        if np.isnan(moy) or np.isnan(ec) or np.isnan(atr_i) or atr_i <= 0 or ec <= 0:
            return None
        if self.regime_a(i) != "range":
            return None

        cloture = float(b.cloture[i])
        z = (cloture - moy) / ec
        risque = self.atr_stop * float(atr_i)

        if z <= -self.ecarts:
            return PlanDeTrade(
                symbole=b.symbole or "?", sens=ACHAT, entree=cloture,
                stop=cloture - risque, objectif=cloture + self.rr * risque,
                these=(f"Marché en range (efficacité {self._efficacite[i]:.2f}) et prix à "
                       f"{abs(z):.1f} écarts-types sous sa moyenne : l'écart devrait se refermer."),
                atr=float(atr_i), horodatage=ctx.maintenant, strategie=self.nom,
                contexte={"z": float(z), "atr": float(atr_i),
                          "efficacite": float(self._efficacite[i]), "moyenne": float(moy)})
        if z >= self.ecarts:
            return PlanDeTrade(
                symbole=b.symbole or "?", sens=VENTE, entree=cloture,
                stop=cloture + risque, objectif=cloture - self.rr * risque,
                these=(f"Marché en range (efficacité {self._efficacite[i]:.2f}) et prix à "
                       f"{z:.1f} écarts-types au-dessus de sa moyenne : l'écart devrait se refermer."),
                atr=float(atr_i), horodatage=ctx.maintenant, strategie=self.nom,
                contexte={"z": float(z), "atr": float(atr_i),
                          "efficacite": float(self._efficacite[i]), "moyenne": float(moy)})
        return None

    @property
    def espace_parametres(self) -> dict[str, list]:
        """3 x 2 x 2 = 12 combinaisons. Petit, exprès."""
        return {"ecarts": [1.8, 2.2, 2.6], "atr_stop": [1.5, 2.0], "rr": [1.5, 2.0]}

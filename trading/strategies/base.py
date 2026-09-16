# -*- coding: utf-8 -*-
"""
Le contrat qu'une stratégie doit remplir, et le porteur de données.

Une stratégie ne renvoie **jamais** « acheter ». Elle renvoie un `PlanDeTrade`
complet — entrée, invalidation technique, objectif, thèse en une phrase — ou
rien du tout. C'est ce qui rend la règle « une position sans plan écrit est un
pari » structurelle plutôt que morale.

Elle ne décide pas non plus de la taille de position : ça ne la regarde pas.
Le dimensionnement appartient au risque, les verrous au contrôle préalable.
Une stratégie qui choisirait ses lots pourrait contourner le plafond.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone

import numpy as np

from ..noyau.plan import PlanDeTrade


@dataclass
class Barres:
    """Des chandeliers. Tableaux numpy alignés, un indice = une barre close."""
    temps: np.ndarray            # datetime64[s]
    ouverture: np.ndarray
    haut: np.ndarray
    bas: np.ndarray
    cloture: np.ndarray
    volume: np.ndarray | None = None
    spread: np.ndarray | None = None      # en points, quand le courtier le donne
    symbole: str = ""
    timeframe: str = ""

    def __len__(self) -> int:
        return len(self.cloture)

    def quand(self, i: int) -> datetime:
        return self.temps[i].astype("datetime64[s]").astype(datetime)

    @classmethod
    def depuis_mt5(cls, rates, symbole: str = "", timeframe: str = "") -> "Barres":
        """Construit depuis le tableau structuré renvoyé par `copy_rates_*`."""
        champs = rates.dtype.names
        return cls(
            temps=rates["time"].astype("datetime64[s]"),
            ouverture=rates["open"].astype(float),
            haut=rates["high"].astype(float),
            bas=rates["low"].astype(float),
            cloture=rates["close"].astype(float),
            volume=(rates["tick_volume"].astype(float)
                    if "tick_volume" in champs else None),
            spread=(rates["spread"].astype(float) if "spread" in champs else None),
            symbole=symbole, timeframe=timeframe,
        )

    def tronquer(self, debut: int, fin: int) -> "Barres":
        """Une tranche, pour le walk-forward. Les vues numpy ne copient rien."""
        d = slice(debut, fin)
        return Barres(
            temps=self.temps[d], ouverture=self.ouverture[d], haut=self.haut[d],
            bas=self.bas[d], cloture=self.cloture[d],
            volume=self.volume[d] if self.volume is not None else None,
            spread=self.spread[d] if self.spread is not None else None,
            symbole=self.symbole, timeframe=self.timeframe,
        )

    def trous(self, ecart_max_heures: float) -> list[tuple[datetime, datetime, float]]:
        """Les trous dans l'historique, week-ends exclus.

        Un historique troué fabrique des résultats faux sans jamais lever
        d'erreur : on le mesure avant de s'en servir.
        """
        trouves = []
        for i in range(1, len(self)):
            a, b = self.quand(i - 1), self.quand(i)
            heures = (b - a).total_seconds() / 3600
            if heures <= ecart_max_heures:
                continue
            # Un week-end normal : vendredi soir -> dimanche/lundi.
            if a.weekday() == 4 and b.weekday() in (0, 6) and heures < 72:
                continue
            trouves.append((a, b, heures))
        return trouves


@dataclass
class ContexteStrategie:
    """Ce que la stratégie sait au moment de décider. Rien de plus."""
    i: int                       # indice de la barre qui vient de CLORE
    barres: Barres
    atr: float
    regime: str                  # "tendance" | "range" | "inconnu"
    maintenant: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class Strategie(ABC):
    """Une règle primaire. Elle propose, les verrous disposent."""

    nom: str = "sans nom"
    #: décrit en une phrase ce que la stratégie croit du marché
    these_generale: str = ""

    def __init__(self, **parametres):
        self.parametres = parametres
        self._prete = False

    @abstractmethod
    def preparer(self, barres: Barres) -> None:
        """Calcule tous les indicateurs d'un coup. Appelé une fois.

        Aucun indicateur ne doit regarder au-delà de son indice : c'est ici que
        se joue l'absence de biais de survie.
        """

    @abstractmethod
    def signal(self, ctx: ContexteStrategie) -> PlanDeTrade | None:
        """Renvoie un plan COMPLET, ou None.

        L'exécution aura lieu à l'OUVERTURE DE LA BARRE SUIVANTE : le plan est
        donc bâti sur la barre qui vient de clore, jamais sur celle en cours.
        """

    def regime_favorable(self, ctx: ContexteStrategie) -> bool:
        """Les régimes où cette stratégie gagne. Par défaut : tous."""
        return True

    @property
    def espace_parametres(self) -> dict[str, list]:
        """Les valeurs à balayer en walk-forward.

        Volontairement petit : plus il y a de combinaisons, plus il est facile
        de trouver par hasard un réglage qui a bien marché sur le passé.
        """
        return {}

    def __str__(self) -> str:
        p = ", ".join(f"{k}={v}" for k, v in self.parametres.items())
        return f"{self.nom}({p})"

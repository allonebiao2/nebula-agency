# -*- coding: utf-8 -*-
"""
Le moteur de décision de LE REFLUX, minute par minute, **strictement causal**.

Un seul code décide, dans le rejeu d'un an (`recherche/rejeu.py`) comme chez le courtier
(`live/scalpeur.py`) : quel ordre attend, lequel est armé pour la minute qui vient, et lequel est
abandonné. Seul ce qui arrive AU prix (remplissage, stop, objectif) change de mains : simulé dans le
rejeu, observé chez le courtier en direct.

⛔ **POURQUOI CE MOTEUR EXISTE** (2026-09-18). Le banc de recherche (`banc._simuler_ordres`) traite
les ordres dans l'ordre où ils ont été POSÉS : quand plusieurs ordres limites attendent en même
temps, il donne le trade au plus ancien qui finit par être servi, même si un plus récent a été servi
AVANT lui. Aucun courtier ne peut faire ça : chez lui, c'est l'ordre touché le premier qui entre.
Ici, la règle est celle du courtier :
  · à la clôture de chaque barre, la stratégie pose un ordre candidat (`candidates_v2.rabais`, les
    mêmes formules que la recherche), valable 60 minutes ;
  · les ordres en attente sont tous dans le sens de la dernière barre : quand la tendance se
    retourne, les ordres de l'autre sens sont abandonnés ;
  · le filtre juge la barre qui vient de se fermer ; s'il dit oui, **un seul** ordre est armé pour
    la minute suivante : celui que le prix touchera le premier (la limite la plus haute à l'achat,
    la plus basse à la vente) ;
  · un ordre dont l'objectif est touché avant d'être servi est abandonné (comme dans la recherche) ;
  · dès qu'une position existe, tous les ordres en attente sont abandonnés.
La recherche jugeait la barre qui précède le remplissage ; ici aussi : un ordre ne peut être servi
pendant la minute j que si le filtre a approuvé la barre j-1.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class OrdreVirtuel:
    pose: int            # barre dont la CLÔTURE a créé l'ordre ; servi au plus tôt à pose + 1
    sens: int            # +1 achat, -1 vente
    limite: float
    stop: float
    cible: float
    expire: int          # dernière barre où il peut être servi

    @property
    def risque(self) -> float:
        return abs(self.limite - self.stop)


@dataclass
class Attente:
    """Les ordres candidats encore valables. Rien n'est chez le courtier tant qu'il n'est pas armé."""
    ordres: list[OrdreVirtuel] = field(default_factory=list)

    def vider(self) -> None:
        self.ordres.clear()

    def poser(self, o: OrdreVirtuel) -> None:
        self.ordres.append(o)

    def nettoyer(self, j: int, haut_j: float, bas_j: float, sens_j: int) -> None:
        """À la clôture de la barre j : retirer ce qui ne peut plus être servi à j + 1."""
        garde = []
        for o in self.ordres:
            if o.expire < j + 1:
                continue
            # L'objectif touché pendant j alors que l'ordre attendait : il ne sera plus servi
            # (la recherche fait pareil, à partir de pose + 1).
            if j > o.pose and ((o.sens > 0 and haut_j >= o.cible) or (o.sens < 0 and bas_j <= o.cible)):
                continue
            if sens_j and o.sens != sens_j:
                continue
            garde.append(o)
        self.ordres = garde

    def meilleur(self, choix: str = "premier") -> OrdreVirtuel | None:
        """L'ordre à armer. `premier` : celui que le prix touchera le PREMIER (à l'achat la limite la
        plus haute), la règle du courtier. `profond` : le plus loin du prix (à l'achat la plus basse),
        la version CAUSALE de ce que le banc faisait en connaissant l'avenir : n'entrer que sur les
        replis les plus profonds, sans savoir s'ils viendront."""
        if not self.ordres:
            return None
        if choix == "profond":
            return min(self.ordres, key=lambda o: o.sens * o.limite)
        return max(self.ordres, key=lambda o: o.sens * o.limite)


def ordre_de_la_barre(ordres, index_par_pose: np.ndarray, j: int,
                      stop_min_prix: float = 0.0) -> OrdreVirtuel | None:
    """L'ordre candidat que la clôture de la barre j autorise (celui de `rabais`), ou rien.

    ⚠️ Un ordre dont le stop est plus court que le minimum du courtier n'existe pas : le courtier
    le refuserait, et la recherche l'écarte (`banc._simuler_ordres`, `d >= stop_min`). Sur l'EUR/USD
    ce minimum est de 20 points, et un stop de 2 x ATR(14) en M1 tombe souvent en dessous.
    """
    k = int(index_par_pose[j]) if 0 <= j < len(index_par_pose) else -1
    if k < 0:
        return None
    if abs(float(ordres.limite[k]) - float(ordres.stop[k])) < stop_min_prix:
        return None
    return OrdreVirtuel(pose=int(ordres.pose[k]), sens=int(ordres.sens[k]), limite=float(ordres.limite[k]),
                        stop=float(ordres.stop[k]), cible=float(ordres.cible[k]), expire=int(ordres.expire[k]))


def index_des_ordres(ordres, n: int) -> np.ndarray:
    """Pour chaque barre, l'indice de l'ordre qu'elle pose dans `ordres` (-1 si aucun)."""
    idx = np.full(n, -1, dtype=np.int64)
    idx[ordres.pose] = np.arange(len(ordres.pose))
    return idx


def sens_par_barre(ordres, n: int) -> np.ndarray:
    s = np.zeros(n, dtype=np.int8)
    s[ordres.pose] = ordres.sens
    return s


def arme(proba: float, seuil: float) -> bool:
    return bool(np.isfinite(proba) and proba >= seuil)

# -*- coding: utf-8 -*-
"""
Le catalogue des stratégies : le seul endroit qui les nomme.

L'agent, le walk-forward et l'interface lisent cette table. Ajouter une
stratégie = l'écrire dans `strategies/` et l'inscrire ici, rien d'autre.
"""
from __future__ import annotations

from .cassure_donchian import CassureDonchian
from .retour_moyenne import RetourMoyenne

STRATEGIES = {
    CassureDonchian.nom: CassureDonchian,
    RetourMoyenne.nom: RetourMoyenne,
}


def decrire() -> list[dict]:
    return [{"nom": n, "libelle": getattr(c, "libelle", n), "these": c.these_generale,
             "parametres": c().parametres, "espace": c().espace_parametres}
            for n, c in STRATEGIES.items()]

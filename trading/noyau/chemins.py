# -*- coding: utf-8 -*-
"""
Où vivent les données de l'utilisateur.

Trois situations, un seul point de vérité :

  · DÉVELOPPEMENT (le dépôt) : `trading/donnees/`, ignoré par git.
  · PRODUIT INSTALLÉ (exécutable) : `%APPDATA%/NEBULA Trader/`. Un logiciel
    installé n'écrit jamais à côté de son programme : `Program Files` est en
    lecture seule pour un utilisateur ordinaire.
  · FORCÉ : la variable `NEBULA_TRADER_DONNEES`, pour un VPS ou plusieurs
    comptes sur la même machine.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

RACINE_CODE = Path(__file__).resolve().parent.parent


def est_installe() -> bool:
    """Vrai quand on tourne depuis l'exécutable empaqueté."""
    return bool(getattr(sys, "frozen", False))


def dossier_donnees() -> Path:
    force = os.environ.get("NEBULA_TRADER_DONNEES")
    if force:
        d = Path(force)
    elif est_installe():
        d = Path(os.environ.get("APPDATA", Path.home())) / "NEBULA Trader"
    else:
        d = RACINE_CODE / "donnees"
    d.mkdir(parents=True, exist_ok=True)
    return d


def fichier(nom: str) -> Path:
    return dossier_donnees() / nom


def dossier_rapports() -> Path:
    d = dossier_donnees() / "rapports" if est_installe() else RACINE_CODE / "rapports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def initialiser() -> None:
    """Premier lancement d'un produit installé : les rapports livrés avec le
    programme (walk-forward, mesure du capital) sont copiés dans le dossier de
    l'utilisateur. Sans eux, l'agent ne connaît pas ses réglages de stratégie et
    l'interface n'a rien à montrer. On ne remplace jamais un rapport existant :
    l'utilisateur a pu en recalculer un plus récent."""
    if not est_installe():
        return
    import shutil
    livres = dossier_ressources() / "rapports"
    if not livres.exists():
        return
    cible = dossier_rapports()
    for p in livres.glob("*.json"):
        if not (cible / p.name).exists():
            shutil.copy2(p, cible / p.name)


def dossier_ressources() -> Path:
    """Les fichiers livrés avec le programme (interface, config par défaut)."""
    if est_installe():
        return Path(getattr(sys, "_MEIPASS", RACINE_CODE)) / "trading"
    return RACINE_CODE

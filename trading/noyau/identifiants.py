# -*- coding: utf-8 -*-
"""
Identifiants de courtier : lus dans `secrets/`, jamais dans le dépôt.

Le dépôt `allonebiao2/nebula-agency` est PUBLIC. `secrets/` est ignoré par git
depuis toujours — c'est la seule place acceptable pour un mot de passe.

Pourquoi des identifiants explicites plutôt que la session enregistrée du
terminal : un bot qui doit tourner **chez n'importe quel courtier** ne peut pas
dépendre de ce qu'un terminal a bien voulu mémoriser. On nomme le compte, on
nomme le serveur, on se connecte. C'est aussi ce qui permet d'avoir plusieurs
profils (démo, réel, autre courtier) et d'en changer sans rien réinstaller.

Format de `secrets/mt5.env` — une ligne par valeur, un profil par préfixe :

    # profil par défaut
    MT5_LOGIN=12345678
    MT5_PASSWORD=le-mot-de-passe-MAITRE
    MT5_SERVER=Deriv-Demo
    MT5_TERMINAL=C:\\Program Files\\MetaTrader 5 Terminal\\terminal64.exe

    # profil nommé : MT5_<PROFIL>_<CHAMP>
    MT5_EXNESS_LOGIN=87654321
    MT5_EXNESS_PASSWORD=...
    MT5_EXNESS_SERVER=Exness-MT5Trial9
    MT5_EXNESS_TERMINAL=C:\\Program Files\\MetaTrader 5 EXNESS\\terminal64.exe

⚠️ Le mot de passe MAÎTRE, pas celui d'investisseur : le mot de passe
investisseur donne un accès en LECTURE SEULE. Le terminal se connecte quand
même, les graphiques s'affichent, et **tout ordre est rejeté** — une panne qui
ressemble à un bug et qui n'en est pas un.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent.parent
FICHIER = RACINE_DEPOT / "secrets" / "mt5.env"


class IdentifiantsManquants(Exception):
    """Pas de quoi se connecter. On le dit, on ne devine pas."""


@dataclass(frozen=True)
class Identifiants:
    login: int | None
    motdepasse: str | None
    serveur: str | None
    terminal: str | None
    profil: str = "defaut"

    @property
    def complets(self) -> bool:
        return bool(self.login and self.motdepasse and self.serveur)

    def __str__(self) -> str:
        """Jamais le mot de passe. Même dans un log, même en démo."""
        return (f"profil {self.profil} · compte {self.login or '?'} @ "
                f"{self.serveur or '?'} · mot de passe "
                f"{'fourni' if self.motdepasse else 'ABSENT'}")


def _lire_env(chemin: Path) -> dict[str, str]:
    if not chemin.exists():
        return {}
    valeurs: dict[str, str] = {}
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#"):
            continue
        if "=" not in ligne:
            continue
        cle, _, val = ligne.partition("=")
        valeurs[cle.strip().upper()] = val.strip().strip('"').strip("'")
    return valeurs


def charger(profil: str = "defaut", *, chemin: Path | None = None) -> Identifiants:
    """Lit un profil. Les variables d'environnement l'emportent sur le fichier."""
    valeurs = _lire_env(chemin or FICHIER)
    valeurs.update({k: v for k, v in os.environ.items() if k.startswith("MT5_")})

    prefixe = "MT5_" if profil in ("defaut", "", None) else f"MT5_{profil.upper()}_"

    def champ(nom: str) -> str | None:
        return valeurs.get(prefixe + nom) or None

    login = champ("LOGIN")
    return Identifiants(
        login=int(login) if login and login.isdigit() else None,
        motdepasse=champ("PASSWORD"),
        serveur=champ("SERVER"),
        terminal=champ("TERMINAL"),
        profil=profil,
    )


def profils_disponibles(chemin: Path | None = None) -> list[str]:
    """Les profils que le fichier déclare, d'après les clés `*_LOGIN`."""
    valeurs = _lire_env(chemin or FICHIER)
    trouves = []
    for cle in valeurs:
        if cle == "MT5_LOGIN":
            trouves.append("defaut")
        elif (m := re.fullmatch(r"MT5_([A-Z0-9]+)_LOGIN", cle)):
            trouves.append(m.group(1).lower())
    return sorted(set(trouves))


def gabarit() -> str:
    return """# Identifiants MT5 — ce fichier vit dans secrets/, ignore par git.
# Le mot de passe MAITRE, pas celui d'investisseur (lecture seule = ordres rejetes).

MT5_LOGIN=
MT5_PASSWORD=
MT5_SERVER=Deriv-Demo
MT5_TERMINAL=C:\\Program Files\\MetaTrader 5 Terminal\\terminal64.exe

# Autre courtier, meme bot :
# MT5_EXNESS_LOGIN=
# MT5_EXNESS_PASSWORD=
# MT5_EXNESS_SERVER=Exness-MT5Trial9
# MT5_EXNESS_TERMINAL=C:\\Program Files\\MetaTrader 5 EXNESS\\terminal64.exe
"""


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(f"Fichier attendu : {FICHIER}")
    if not FICHIER.exists():
        FICHIER.parent.mkdir(parents=True, exist_ok=True)
        modele = FICHIER.with_suffix(".env.exemple")
        modele.write_text(gabarit(), encoding="utf-8")
        print(f"  absent. Gabarit écrit ici : {modele}")
        print("  Renomme-le en mt5.env et remplis-le.")
        sys.exit(1)

    dispo = profils_disponibles()
    print(f"  profils déclarés : {', '.join(dispo) if dispo else 'aucun'}")
    for p in dispo or ["defaut"]:
        ids = charger(p)
        print(f"  {ids}  ->  {'utilisable' if ids.complets else 'INCOMPLET'}")

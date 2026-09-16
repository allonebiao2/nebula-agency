# -*- coding: utf-8 -*-
"""
Le coffre : les identifiants du client, chiffrés par Windows.

Un produit installé chez quelqu'un d'autre ne peut pas lire un `secrets/mt5.env`
posé à la main. Le mot de passe du compte est saisi dans l'interface, puis
chiffré avec **DPAPI** (`CryptProtectData`), le coffre intégré à Windows : seul
le même utilisateur, sur la même machine, peut le relire. Copier le fichier sur
un autre PC ne donne rien.

Hors Windows (développement), le coffre refuse d'écrire plutôt que de stocker
en clair : un mot de passe en clair sur un disque est un mot de passe publié.
"""
from __future__ import annotations

import base64
import ctypes
import json
import sys
from ctypes import wintypes

from .chemins import fichier

ENTROPIE = b"NEBULA-Trader/coffre/v1"


class CoffreIndisponible(Exception):
    pass


class _BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]


def _blob(donnees: bytes) -> _BLOB:
    tampon = ctypes.create_string_buffer(donnees, len(donnees))
    return _BLOB(len(donnees), ctypes.cast(tampon, ctypes.POINTER(ctypes.c_char)))


def _dpapi(donnees: bytes, chiffrer: bool) -> bytes:
    if sys.platform != "win32":
        raise CoffreIndisponible("le coffre DPAPI n'existe que sous Windows")
    crypt32, kernel32 = ctypes.windll.crypt32, ctypes.windll.kernel32
    entree, entropie, sortie = _blob(donnees), _blob(ENTROPIE), _BLOB()
    fonction = crypt32.CryptProtectData if chiffrer else crypt32.CryptUnprotectData
    ok = fonction(ctypes.byref(entree), None, ctypes.byref(entropie), None, None, 0x01,
                  ctypes.byref(sortie))
    if not ok:
        raise CoffreIndisponible(f"DPAPI a refusé (erreur {ctypes.GetLastError()})")
    try:
        return ctypes.string_at(sortie.pbData, sortie.cbData)
    finally:
        kernel32.LocalFree(sortie.pbData)


def proteger(texte: str) -> str:
    return base64.b64encode(_dpapi(texte.encode("utf-8"), True)).decode("ascii")


def devoiler(jeton: str) -> str:
    return _dpapi(base64.b64decode(jeton), False).decode("utf-8")


# --------------------------------------------------------------------------- #

def enregistrer_compte(*, login: int, motdepasse: str, serveur: str, terminal: str = "") -> None:
    fichier("compte.json").write_text(json.dumps({
        "login": int(login), "serveur": serveur.strip(), "terminal": terminal.strip(),
        "motdepasse_dpapi": proteger(motdepasse),
    }, indent=2), encoding="utf-8")


def lire_compte() -> dict | None:
    p = fichier("compte.json")
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    try:
        d["motdepasse"] = devoiler(d.pop("motdepasse_dpapi"))
    except (CoffreIndisponible, KeyError, ValueError):
        d["motdepasse"] = None
    return d


def resume_compte() -> dict | None:
    """Ce que l'interface a le droit de montrer : jamais le mot de passe."""
    d = lire_compte()
    if not d:
        return None
    return {"login": d["login"], "serveur": d["serveur"], "terminal": d.get("terminal", ""),
            "motdepasse": "enregistré" if d.get("motdepasse") else "illisible sur cette machine"}


def enregistrer_secret(nom: str, valeur: str) -> None:
    p = fichier("secrets.json")
    d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    if valeur:
        d[nom] = proteger(valeur)
    else:
        d.pop(nom, None)
    p.write_text(json.dumps(d, indent=2), encoding="utf-8")


def lire_secret(nom: str) -> str | None:
    p = fichier("secrets.json")
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    if nom not in d:
        return None
    try:
        return devoiler(d[nom])
    except (CoffreIndisponible, ValueError):
        return None

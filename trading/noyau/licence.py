# -*- coding: utf-8 -*-
"""
La licence : ce qui sépare l'évaluation du mode réel.

Une clé est un petit texte signé par NEBULA avec une clé privée Ed25519 qui ne
quitte jamais `secrets/` (dépôt public). Le programme n'embarque que la clé
PUBLIQUE : il peut vérifier une licence sans connexion, il ne peut pas en
fabriquer. Modifier une date d'expiration dans la clé casse la signature.

    NTR1.<charge utile en base64url>.<signature en base64url>

Ce que la licence débloque, et rien d'autre :
  · sans licence (évaluation) : observation et compte DÉMO, toutes les
    fonctions visibles ; c'est ce qui permet d'essayer avant d'acheter
  · avec licence : le mode RÉEL

⚠️ Une vérification locale se contourne par qui modifie le programme. Elle
suffit à séparer un client honnête d'un essai, pas à arrêter un pirate
déterminé : le jour où ce risque coûte plus qu'un serveur d'activation, on
ajoute l'activation en ligne.
"""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import date

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .chemins import fichier

CLE_PUBLIQUE = "P1YCCp+ywmJpiWp4bx9gJqIoqOUH7xi1Kc6pqzriS0I="
PREFIXE = "NTR1"


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")


@dataclass(frozen=True)
class Licence:
    valide: bool
    raison: str = ""
    titulaire: str = ""
    email: str = ""
    edition: str = "evaluation"
    expire: str | None = None
    identifiant: str = ""

    def en_dict(self) -> dict:
        return self.__dict__.copy()


EVALUATION = Licence(False, "aucune licence : mode évaluation (observation et démo)")


def verifier(cle: str, *, aujourdhui: date | None = None) -> Licence:
    cle = (cle or "").strip()
    if not cle:
        return EVALUATION
    try:
        prefixe, charge, signature = cle.split(".")
    except ValueError:
        return Licence(False, "clé mal formée")
    if prefixe != PREFIXE:
        return Licence(False, "clé d'un autre produit ou d'une autre version")
    try:
        Ed25519PublicKey.from_public_bytes(base64.b64decode(CLE_PUBLIQUE)).verify(
            _b64d(signature), f"{prefixe}.{charge}".encode("ascii"))
    except (InvalidSignature, ValueError):
        return Licence(False, "signature invalide : cette clé n'a pas été émise par NEBULA")
    d = json.loads(_b64d(charge))
    expire = d.get("expire")
    if expire and date.fromisoformat(expire) < (aujourdhui or date.today()):
        return Licence(False, f"licence expirée le {expire}", d.get("nom", ""), d.get("email", ""),
                       d.get("edition", ""), expire, d.get("id", ""))
    return Licence(True, "licence valide", d.get("nom", ""), d.get("email", ""),
                   d.get("edition", "pro"), expire, d.get("id", ""))


def signer(charge: dict, cle_privee_pem: bytes) -> str:
    """Réservé à NEBULA : fabriquer une clé (voir `outils/licence.py`)."""
    from cryptography.hazmat.primitives import serialization
    privee = serialization.load_pem_private_key(cle_privee_pem, password=None)
    corps = _b64e(json.dumps(charge, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    message = f"{PREFIXE}.{corps}".encode("ascii")
    return f"{PREFIXE}.{corps}.{_b64e(privee.sign(message))}"


# --------------------------------------------------------------------------- #

def cle_installee() -> str:
    p = fichier("licence.txt")
    return p.read_text(encoding="utf-8").strip() if p.exists() else ""


def installer(cle: str) -> Licence:
    lic = verifier(cle)
    if lic.valide:
        fichier("licence.txt").write_text(cle.strip(), encoding="utf-8")
    return lic


def actuelle() -> Licence:
    return verifier(cle_installee())

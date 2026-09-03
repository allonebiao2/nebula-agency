"""Ce qu'un canal doit savoir faire, et rien de plus.

Un canal, c'est le tuyau : il reçoit un message d'un client et en renvoie un.
Meta Cloud API, Twilio et la console en sont trois. Le cerveau ne sait pas
lequel il a en face, ce qui permet de tester toute la chaîne dans un terminal,
sans compte WhatsApp, sans réseau, et sans dépenser un franc.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class MessageEntrant:
    """Un message d'un client, quel que soit le tuyau par lequel il est arrivé."""

    numero: str                 # chiffres uniquement, sans « + » ni « whatsapp: »
    texte: str
    identifiant: str = ""       # l'id du fournisseur, pour ne pas traiter deux fois
    nom_profil: str = ""
    quand: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    type: str = "text"          # text | audio | image | autre


def chiffres(numero: str) -> str:
    """« whatsapp:+229 01 52 00 64 90 » → « 2290152006490 »."""
    return "".join(c for c in (numero or "") if c.isdigit())


def poster_json(url: str, charge: dict, entetes: dict, delai: float = 15.0) -> tuple[int, str]:
    """Un POST JSON, en bibliothèque standard.

    Le kit ne dépend que d'`anthropic`. Deux appels HTTP ne justifient pas
    d'imposer un paquet de plus à un hébergement qu'on ne choisit pas toujours.
    """
    corps = json.dumps(charge, ensure_ascii=False).encode("utf-8")
    requete = urllib.request.Request(url, data=corps, method="POST",
                                     headers={"Content-Type": "application/json", **entetes})
    try:
        with urllib.request.urlopen(requete, timeout=delai) as reponse:
            return reponse.status, reponse.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode("utf-8", "replace")
    except urllib.error.URLError as err:
        return 0, f"réseau : {err.reason}"


def poster_formulaire(url: str, champs: dict, entetes: dict,
                      delai: float = 15.0) -> tuple[int, str]:
    corps = urllib.parse.urlencode(champs).encode("utf-8")
    requete = urllib.request.Request(
        url, data=corps, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded", **entetes})
    try:
        with urllib.request.urlopen(requete, timeout=delai) as reponse:
            return reponse.status, reponse.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode("utf-8", "replace")
    except urllib.error.URLError as err:
        return 0, f"réseau : {err.reason}"

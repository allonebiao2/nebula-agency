"""Twilio — le canal du pilote.

Le bac à sable Twilio permet d'essayer en une heure, sur un numéro partagé,
sans validation Meta. C'est bien pour montrer à un client que ça marche ; ce
n'est pas ce qu'on lui livre (numéro partagé = sa marque n'apparaît pas et la
qualité d'envoi est mutualisée).
"""
from __future__ import annotations

import base64
import logging

from canaux.base import MessageEntrant, chiffres, poster_formulaire

log = logging.getLogger("whatsapp-agent.twilio")

NOM = "twilio"


class CanalTwilio:
    def __init__(self, sid: str = "", jeton: str = "", numero: str = ""):
        self.sid = sid
        self.jeton = jeton
        self.numero = numero  # le numéro WhatsApp de l'émetteur, ex. +14155238886
        self.nom = NOM

    def configure(self) -> bool:
        return bool(self.sid and self.jeton and self.numero)

    @staticmethod
    def lire_entrant(champs: dict) -> list[MessageEntrant]:
        """Twilio poste un formulaire, pas du JSON : `From`, `Body`, `MessageSid`."""
        expediteur = chiffres(champs.get("From", ""))
        corps = champs.get("Body", "") or ""
        if not expediteur:
            return []
        return [MessageEntrant(
            numero=expediteur,
            texte=corps,
            identifiant=champs.get("MessageSid", "") or "",
            nom_profil=champs.get("ProfileName", "") or "",
            type="text" if corps else "autre",
        )]

    def envoyer(self, a: str, texte: str) -> bool:
        if not (self.configure() and a and texte):
            return False
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.sid}/Messages.json"
        identite = base64.b64encode(f"{self.sid}:{self.jeton}".encode()).decode()
        code, corps = poster_formulaire(
            url,
            {"From": f"whatsapp:{self.numero}", "To": f"whatsapp:+{chiffres(a)}",
             "Body": texte[:1600]},
            {"Authorization": f"Basic {identite}"},
        )
        if code not in (200, 201):
            log.error("Twilio a refusé l'envoi (%s) : %s", code, corps[:300])
            return False
        return True

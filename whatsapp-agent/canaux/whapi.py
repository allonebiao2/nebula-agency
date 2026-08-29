"""Whapi.cloud — brancher un WhatsApp ORDINAIRE, sans passer par Meta.

C'est le canal qui met un client en ligne le jour même. On scanne un QR code
depuis le téléphone de la maison, comme pour WhatsApp Web, et le numéro répond.
Ni vérification d'entreprise, ni Phone Number ID, ni App Secret, ni les
documents légaux que Meta réclame — et c'est justement ce mur-là qui empêchait
un commerçant de Cotonou d'avoir un agent.

⚠️ CE QU'IL FAUT SAVOIR AVANT DE BRANCHER LE NUMÉRO D'UN CLIENT. Whapi n'est
pas l'API officielle : il pilote une session WhatsApp comme le ferait un
appareil lié. C'est rapide, ça coûte un abonnement mensuel par numéro, et
**WhatsApp peut suspendre un numéro qui automatise par ce chemin**. Le risque
n'est pas théorique : un restaurant qui perd son numéro perd son carnet
d'adresses. À utiliser pour un pilote, une démonstration, ou en connaissance de
cause — et à basculer sur `canaux/meta.py` quand la maison veut du définitif.
Le reste du kit ne change pas d'une ligne : c'est le même agent derrière.

⚠️ Whapi ne SIGNE pas ses appels comme Meta. La porte se protège donc par un
en-tête secret qu'on choisit et qu'on recopie dans les « custom headers » du
webhook Whapi. Sans lui, n'importe qui connaissant l'adresse peut faire parler
l'agent d'un client.
"""
from __future__ import annotations

import hmac
import logging

from canaux.base import MessageEntrant, chiffres, poster_json

log = logging.getLogger("whatsapp-agent.whapi")

NOM = "whapi"
BASE = "https://gate.whapi.cloud"
ENTETE_SECRET = "X-Nebula-Secret"


class CanalWhapi:
    def __init__(self, jeton: str = "", base: str = BASE, secret: str = ""):
        self.jeton = jeton
        self.base = (base or BASE).rstrip("/")
        self.secret = secret
        self.nom = NOM

    def configure(self) -> bool:
        return bool(self.jeton)

    def verifier_secret(self, entete: str | None) -> bool:
        """L'appel vient-il bien de notre webhook Whapi ?

        Sans secret configuré on laisse passer — sinon la promesse des trente
        minutes tombe — mais le serveur le crie au démarrage, et l'assistant
        d'installation en pose un par défaut.
        """
        if not self.secret:
            return True
        return bool(entete) and hmac.compare_digest(entete, self.secret)

    @staticmethod
    def lire_entrant(charge: dict) -> list[MessageEntrant]:
        """Extrait les messages d'un appel Whapi.

        ⚠️ `from_me` EST LE PIÈGE. Whapi renvoie aussi les messages que le
        numéro ENVOIE — y compris ceux que l'agent vient d'écrire. Les traiter
        comme des messages entrants met l'agent en conversation avec lui-même,
        et la boucle tourne jusqu'au plafond anti-abus.

        ⚠️ Les accusés de statut arrivent par la même porte, sous « statuses » :
        aucun message à en tirer.
        """
        recoltes: list[MessageEntrant] = []
        for message in charge.get("messages", []) or []:
            if message.get("from_me"):
                continue
            expediteur = chiffres(message.get("from")
                                  or str(message.get("chat_id", "")).split("@")[0])
            if not expediteur:
                continue
            genre = message.get("type", "") or "autre"
            texte = ""
            if genre == "text":
                texte = ((message.get("text") or {}).get("body") or "").strip()
            recoltes.append(MessageEntrant(
                numero=expediteur,
                texte=texte,
                identifiant=str(message.get("id", "") or ""),
                nom_profil=str(message.get("from_name", "") or ""),
                type=genre,
            ))
        return recoltes

    def envoyer(self, a: str, texte: str) -> bool:
        if not (self.configure() and a and texte):
            return False
        code, corps = poster_json(
            f"{self.base}/messages/text",
            {"to": chiffres(a), "body": texte[:4096]},
            {"Authorization": f"Bearer {self.jeton}", "Accept": "application/json"},
        )
        if code not in (200, 201):
            log.error("Whapi a refusé l'envoi (%s) : %s", code, corps[:300])
            return False
        return True

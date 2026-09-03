"""Meta Cloud API — le canal de production, l'officiel.

C'est celui qu'on vise : le client garde SON numéro, sa marque et sa qualité,
et les conversations de service (le client écrit, on répond dans les 24 h) sont
gratuites jusqu'à un millier par mois. Twilio reste utile pour un pilote.

⚠️ LE WEBHOOK EST UNE PORTE PUBLIQUE. Sans vérification de signature, n'importe
qui peut poster une fausse conversation et faire parler l'agent — donc dépenser
les jetons du client et lui faire dire n'importe quoi. `verifier_signature()`
n'est pas une option : elle est appelée par le serveur avant toute lecture.
"""
from __future__ import annotations

import hashlib
import hmac
import logging

from canaux.base import MessageEntrant, chiffres, poster_json

log = logging.getLogger("whatsapp-agent.meta")

NOM = "meta"


class CanalMeta:
    def __init__(self, jeton: str = "", identifiant_numero: str = "",
                 jeton_verification: str = "", secret_app: str = "",
                 version: str = "v21.0"):
        self.jeton = jeton
        self.identifiant_numero = identifiant_numero
        self.jeton_verification = jeton_verification
        self.secret_app = secret_app
        self.version = version
        self.nom = NOM

    def configure(self) -> bool:
        return bool(self.jeton and self.identifiant_numero)

    # --- vérification d'abonnement (GET) --------------------------------
    def verifier_abonnement(self, mode: str | None, jeton: str | None,
                            defi: str | None) -> str | None:
        """Meta appelle le webhook en GET une fois, pour vérifier qu'il est à nous."""
        if mode == "subscribe" and jeton and self.jeton_verification \
                and hmac.compare_digest(jeton, self.jeton_verification):
            return defi
        return None

    # --- authenticité des appels (POST) ---------------------------------
    def verifier_signature(self, corps: bytes, entete: str | None) -> bool:
        """L'en-tête `X-Hub-Signature-256` prouve que Meta est bien l'expéditeur.

        Sans `secret_app` configuré, on REFUSE : mieux vaut un webhook muet
        qu'un webhook que le premier venu peut piloter.
        """
        if not self.secret_app:
            return False
        if not entete or not entete.startswith("sha256="):
            return False
        attendu = hmac.new(self.secret_app.encode("utf-8"), corps, hashlib.sha256).hexdigest()
        return hmac.compare_digest(attendu, entete[len("sha256="):])

    # --- lecture des messages entrants ----------------------------------
    @staticmethod
    def lire_entrant(charge: dict) -> list[MessageEntrant]:
        """Extrait les messages d'un appel Meta.

        ⚠️ Un même appel peut porter plusieurs messages, et beaucoup n'en portent
        AUCUN : les accusés de lecture et de livraison passent par le même
        webhook. Les traiter comme des messages ferait répondre l'agent à ses
        propres accusés de réception.
        """
        recoltes: list[MessageEntrant] = []
        for entree in charge.get("entry", []) or []:
            for changement in entree.get("changes", []) or []:
                valeur = changement.get("value", {}) or {}
                noms = {}
                for contact in valeur.get("contacts", []) or []:
                    noms[contact.get("wa_id", "")] = \
                        (contact.get("profile", {}) or {}).get("name", "")
                for message in valeur.get("messages", []) or []:
                    genre = message.get("type", "")
                    texte = ""
                    if genre == "text":
                        texte = (message.get("text", {}) or {}).get("body", "")
                    elif genre == "button":
                        texte = (message.get("button", {}) or {}).get("text", "")
                    elif genre == "interactive":
                        inter = message.get("interactive", {}) or {}
                        for cle in ("button_reply", "list_reply"):
                            if cle in inter:
                                texte = (inter[cle] or {}).get("title", "")
                    expediteur = chiffres(message.get("from", ""))
                    recoltes.append(MessageEntrant(
                        numero=expediteur,
                        texte=texte,
                        identifiant=message.get("id", ""),
                        nom_profil=noms.get(message.get("from", ""), ""),
                        type=genre or "autre",
                    ))
        return recoltes

    # --- envoi -----------------------------------------------------------
    def envoyer(self, a: str, texte: str) -> bool:
        if not (self.configure() and a and texte):
            return False
        url = f"https://graph.facebook.com/{self.version}/{self.identifiant_numero}/messages"
        charge = {"messaging_product": "whatsapp", "recipient_type": "individual",
                  "to": chiffres(a), "type": "text",
                  "text": {"preview_url": False, "body": texte[:4096]}}
        code, corps = poster_json(url, charge,
                                  {"Authorization": f"Bearer {self.jeton}"})
        if code not in (200, 201):
            log.error("Meta a refusé l'envoi (%s) : %s", code, corps[:300])
            return False
        return True

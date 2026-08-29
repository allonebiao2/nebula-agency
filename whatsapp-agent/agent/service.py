"""LE SERVICE — un message arrive, une réponse part, la maison est prévenue.

C'est la pièce que le serveur HTTP et le simulateur partagent : toute la chaîne
est ici, et aucun des deux n'en refait un morceau. Ce qui est testé dans un
terminal est donc exactement ce qui tourne en production.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from agent.catalogue import Catalogue
from agent.cerveau import Cerveau, Reponse
from agent.garde_prix import GardePrix
from agent.maison import Maison
from agent.memoire import Memoire

log = logging.getLogger("whatsapp-agent.service")


def charger_catalogue(maison: Maison, racine: Path) -> Catalogue:
    """Va chercher le lecteur nommé dans la fiche de la maison."""
    from importlib import import_module
    try:
        module = import_module(f"lecteurs.{maison.lecteur}")
    except ModuleNotFoundError as exc:
        raise ValueError(
            f"{maison.id} : aucun lecteur « {maison.lecteur} » dans lecteurs/") from exc
    return module.charger(racine)


@dataclass
class Traitement:
    """Ce qui s'est passé pour un message, de bout en bout."""

    reponse: Reponse
    envoye: bool = False
    patron_prevenu: bool = False
    doublon: bool = False
    note: str = ""


class Service:
    def __init__(self, maison: Maison, racine: Path, memoire: Memoire,
                 canal, client=None, catalogue: Catalogue | None = None):
        self.maison = maison
        self.racine = racine
        self.memoire = memoire
        self.canal = canal
        self.catalogue = catalogue or charger_catalogue(maison, racine)
        self.garde = GardePrix(self.catalogue)
        self.cerveau = Cerveau(maison, self.catalogue, self.garde, client=client)

    # --- le tour complet --------------------------------------------------
    def traiter(self, numero: str, texte: str, nom_client: str = "",
                identifiant: str = "") -> Traitement:
        if identifiant and self.memoire.deja_vu(identifiant):
            log.info("message %s déjà traité, ignoré", identifiant)
            return Traitement(Reponse("", sortie="silence", motif="doublon"), doublon=True)

        if not (texte or "").strip():
            # Une photo, un vocal, un partage de contact : on ne devine pas.
            return self._sans_texte(numero)

        reponse = self.cerveau.repondre(self.memoire, numero, texte, nom_client=nom_client)
        traitement = Traitement(reponse)

        if reponse.a_envoyer:
            traitement.envoye = self.canal.envoyer(numero, reponse.texte)
            if not traitement.envoye:
                log.error("la réponse n'a pas pu être envoyée à %s", numero)

        # ⚠️ UNE COMMANDE PRÉVIENT AUSSI, MÊME SANS ESCALADE. Le premier jet
        # n'alertait que sur `escalades` : une commande confirmée était donc
        # enregistrée, récapitulée au client… et la maison ne l'apprenait jamais.
        # Un client qui vient chercher un plat que personne n'a mis sur le feu,
        # c'est le seul défaut de ce kit qui coûte un client au restaurant.
        if reponse.escalades or reponse.commandes:
            traitement.patron_prevenu = self.alerter_patron(numero, reponse)
        return traitement

    def _sans_texte(self, numero: str) -> Traitement:
        """Un message qu'on ne sait pas lire passe à un humain, il ne s'ignore pas.

        Un client qui envoie la photo d'un plat attend une réponse. Se taire lui
        fait croire que la maison ne répond pas.
        """
        mot = ("J'ai bien reçu votre message. Je passe la main à la maison, "
               "elle vous répond ici même.")
        envoye = self.canal.envoyer(numero, mot)
        reponse = Reponse(mot, sortie="humain",
                          escalades=[{"raison": "message sans texte (photo, vocal ou autre)",
                                      "resume": "Le client a envoyé autre chose que du texte.",
                                      "urgent": False}],
                          motif="message non textuel")
        self.memoire.noter(self.maison.id, numero, "assistant", mot, entrant=False)
        return Traitement(reponse, envoye=envoye,
                          patron_prevenu=self.alerter_patron(numero, reponse))

    # --- prévenir un humain ------------------------------------------------
    def alerter_patron(self, numero_client: str, reponse: Reponse) -> bool:
        """Envoie l'alerte au numéro de la maison.

        ⚠️ CETTE ALERTE PEUT NE PAS PARTIR, ET CE N'EST PAS UNE PANNE. WhatsApp
        n'autorise un message libre que dans les 24 h qui suivent le dernier
        message de la personne. Si le patron n'a rien écrit à son propre agent
        depuis la veille, seul un modèle pré-approuvé par Meta peut le joindre.
        On le journalise fort, et l'escalade reste dans la base : une alerte qui
        n'a pas pu partir ne doit pas disparaître.
        """
        if not self.maison.numero_patron:
            log.error("ESCALADE PERDUE (%s) : aucun numero_patron dans %s.yaml",
                      reponse.escalades, self.maison.id)
            return False

        titre = ("🧾 une commande vient d'être passée" if reponse.commandes
                 and not reponse.escalades else "⚠️ un client a besoin de vous")
        lignes = [f"{self.maison.nom} — {titre}", f"Client : +{numero_client}"]
        for e in reponse.escalades:
            lignes.append(f"Motif : {e.get('raison', '')}")
            if e.get("resume"):
                lignes.append(f"Ce qu'il demande : {e['resume']}")
        for c in reponse.commandes:
            articles = ", ".join(
                f"{a.get('quantite', 1)} × {a.get('nom', '?')}" for a in c.get("articles", []))
            lignes.append(f"Commande : {articles} ({c.get('retrait_ou_livraison', '?')})")
        lignes.append("Répondez directement au client sur son numéro.")
        texte = "\n".join(lignes)

        fenetre = self.memoire.fenetre_ouverte(self.maison.id, self.maison.numero_patron)
        envoye = self.canal.envoyer(self.maison.numero_patron, texte)
        if not envoye:
            log.error("ALERTE NON DÉLIVRÉE au patron (%s). Fenêtre de 24 h ouverte : %s. "
                      "Hors fenêtre, il faut un modèle Meta pré-approuvé. Contenu : %s",
                      self.maison.numero_patron, fenetre, texte.replace("\n", " | "))
        return envoye

"""LE CERVEAU — la carte, la conversation, et Claude qui répond.

Le tour se joue en quatre temps, et le quatrième est le seul qui distingue ce
kit d'un robot de démonstration :

    1. on rassemble ce que la maison sait (sa carte, son ton, ses horaires) ;
    2. on ajoute la conversation de CE client ;
    3. Claude répond, et peut appeler deux outils : passer la main, noter une
       commande ;
    4. le GARDE-FOU relit la réponse avant qu'elle parte. Un prix qui n'existe
       pas dans la carte fait avorter l'envoi et réveille un humain.

⚠️ MODÈLE. Sonnet pour tout le texte qui s'adresse à un client : c'est la règle
de la maison, validée par Mongazi et écrite dans `boutique-ia/config.py`
(« jamais Opus sur les réponses client »). `claude-sonnet-5` est plus récent et
moins cher que le `claude-sonnet-4-6` qui y est nommé, à qualité au moins égale.

⚠️ CACHE. La carte est posée dans un bloc système STABLE, marqué pour la mise en
cache ; l'heure et le prénom du client vont dans un second bloc, APRÈS la
coupure. Mettre l'heure dans le bloc stable suffirait à invalider le cache à
chaque message, sans le moindre message d'erreur : le cache est un accord sur un
préfixe, et une minute qui change casse le préfixe.
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime

from agent.catalogue import Catalogue
from agent.garde_prix import GardePrix, Verdict
from agent.maison import Maison
from agent.memoire import Memoire, maintenant

log = logging.getLogger("whatsapp-agent.cerveau")

MODELE = os.environ.get("WA_MODELE", "claude-sonnet-5")
EFFORT = os.environ.get("WA_EFFORT", "low")
JETONS_MAX = int(os.environ.get("WA_JETONS_MAX", "4000"))
TOURS_OUTILS_MAX = 4

PASSER_LA_MAIN = {
    "name": "passer_la_main",
    "description": (
        "Prévient un humain de la maison et lui passe la conversation. À appeler "
        "dès que la réponse honnête est « je ne sais pas » : une question dont la "
        "réponse n'est ni dans la carte ni dans les informations de la maison, une "
        "réclamation, une négociation, une réservation, une demande de gros volume, "
        "ou un client mécontent. Mieux vaut passer la main une fois de trop qu'inventer "
        "une seule fois. N'invente jamais une information pour éviter d'appeler cet outil."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "raison": {"type": "string",
                       "description": "Pourquoi un humain est nécessaire, en une phrase."},
            "resume": {"type": "string",
                       "description": "Ce que le client demande, résumé pour que l'humain "
                                      "reprenne sans relire toute la conversation."},
            "urgent": {"type": "boolean",
                       "description": "Vrai si le client attend une réponse tout de suite."},
        },
        "required": ["raison", "resume"],
    },
}

NOTER_LA_COMMANDE = {
    "name": "noter_la_commande",
    "description": (
        "Enregistre une commande FERME et prévient la maison. À appeler uniquement "
        "quand le client a confirmé ce qu'il veut : les articles, les quantités, et "
        "comment il récupère. Une seule fois par commande, et jamais pour une commande "
        "que le client n'a pas confirmée. Les prix doivent être ceux de la carte."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "articles": {
                "type": "array",
                "description": "Les articles commandés, avec leur nom EXACT dans la carte.",
                "items": {
                    "type": "object",
                    "properties": {
                        "nom": {"type": "string"},
                        "quantite": {"type": "integer"},
                        "precisions": {"type": "string",
                                       "description": "Taille, accompagnement, garniture."},
                    },
                    "required": ["nom", "quantite"],
                },
            },
            "total_estime": {"type": "integer",
                             "description": "Total en francs CFA, ou 0 si un prix dépend "
                                            "d'un choix que la maison doit confirmer."},
            "retrait_ou_livraison": {"type": "string", "enum": ["retrait", "livraison"]},
            "adresse": {"type": "string"},
            "nom_client": {"type": "string"},
        },
        "required": ["articles", "retrait_ou_livraison"],
    },
}

OUTILS = [PASSER_LA_MAIN, NOTER_LA_COMMANDE]


@dataclass
class Reponse:
    """Ce qui sort d'un tour : le texte, et ce qu'il faut en faire."""

    texte: str
    sortie: str = "agent"      # agent | humain | silence
    verdict: Verdict | None = None
    escalades: list[dict] = field(default_factory=list)
    commandes: list[dict] = field(default_factory=list)
    jetons: dict = field(default_factory=dict)
    motif: str = ""            # pourquoi on s'est tu, ou pourquoi on a passé la main

    @property
    def a_envoyer(self) -> bool:
        return self.sortie != "silence" and bool(self.texte.strip())


def _liste(titre: str, elements) -> str:
    if not elements:
        return ""
    return titre + "\n" + "\n".join(f"- {e}" for e in elements) + "\n"


def socle(maison: Maison, catalogue: Catalogue) -> str:
    """Le bloc STABLE du prompt : la maison et sa carte. C'est lui qu'on met en cache.

    Rien de daté ici, rien qui change d'un message à l'autre : ni l'heure, ni le
    nom du client, ni le numéro du message. Une seule variable qui bouge et le
    cache ne prend plus, sans que rien ne le signale.
    """
    morceaux = [
        f"Tu réponds sur WhatsApp pour {maison.nom}"
        + (f", {maison.metier}" if maison.metier else "")
        + (f", à {maison.ville}." if maison.ville else "."),
        "",
        "COMMENT TU PARLES",
        maison.ton.strip() or "Chaleureux, clair, bref.",
        "",
        "LA RÈGLE QUI PASSE AVANT TOUTES LES AUTRES",
        "Tu ne donnes JAMAIS un prix, un délai, une adresse ou une disponibilité qui",
        "ne soit pas écrit ci-dessous. Si tu ne sais pas, tu le dis et tu appelles",
        "l'outil passer_la_main. Un client qui attend cinq minutes une vraie réponse",
        "revient ; un client à qui on a annoncé un prix faux ne revient pas.",
        "Quand tu annonces un prix, NOMME l'article dans la même phrase :",
        "« le tilapia braisé, c'est 3 000 F » et jamais « c'est 3 000 F ».",
        "",
        "CE QUE LA MAISON VEND, ET À QUEL PRIX",
        "C'est la seule source de prix. Elle est à jour : elle est lue dans le",
        f"fichier que le site sert ({catalogue.source}).",
        "",
        catalogue.texte(),
        "",
        "COMMENT LIRE UN PRIX",
        "- un prix seul : c'est le prix.",
        "- deux tailles : chacune a son prix, dis les deux.",
        "- « de X à Y selon la garniture » : le prix dépend de ce que le client met",
        "  dedans. Annonce la fourchette, jamais un prix ferme, et dis que la maison",
        "  confirme à la commande.",
        "- plusieurs crans nommés : donne le cran qui correspond à ce qu'il demande.",
        "- « prix sur demande » : la maison n'a pas encore donné ce prix. Tu ne",
        "  l'inventes pas, tu passes la main.",
    ]

    infos = []
    if maison.horaires:
        infos.append(f"Horaires : {maison.horaires.strip()}")
    if maison.livraison:
        infos.append(f"Livraison : {maison.livraison.strip()}")
    if maison.paiement:
        infos.append(f"Paiement : {maison.paiement.strip()}")
    if infos:
        morceaux += ["", "CE QUE TU PEUX DIRE D'AUTRE", *infos]

    passer = _liste("TU PASSES LA MAIN, TOUJOURS, POUR :", maison.a_passer)
    if passer:
        morceaux += ["", passer.rstrip()]

    inconnu = _liste(
        "CE QUE LA MAISON N'A PAS ENCORE TRANCHÉ — tu ne l'inventes sous aucun prétexte :",
        maison.a_confirmer)
    if inconnu:
        morceaux += ["", inconnu.rstrip()]

    morceaux += [
        "",
        "LA FORME",
        "Deux à quatre lignes. Pas de liste à puces sauf si on te demande la carte.",
        "Pas de gras, pas de titres : c'est WhatsApp. Une question à la fois.",
        "Tu ne dis jamais que tu es une intelligence artificielle sauf si on te le",
        "demande — auquel cas tu le dis simplement et tu proposes un humain.",
    ]
    return "\n".join(morceaux)


def contexte(maison: Maison, nom_client: str, quand: datetime | None = None) -> str:
    """Le bloc VOLATIL : après la coupure du cache, parce qu'il change à chaque tour."""
    quand = quand or maintenant()
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    lignes = [f"Nous sommes {jours[quand.weekday()]}, il est {quand:%H:%M} (UTC)."]
    if nom_client:
        lignes.append(f"Le client s'appelle {nom_client}.")
    return "\n".join(lignes)


class Cerveau:
    def __init__(self, maison: Maison, catalogue: Catalogue,
                 garde: GardePrix | None = None, client=None):
        self.maison = maison
        self.catalogue = catalogue
        self.garde = garde or GardePrix(catalogue)
        self._client = client
        self._socle = socle(maison, catalogue)

    @property
    def client(self):
        """Le client Anthropic, créé au dernier moment.

        Ainsi la suite de contrôles importe ce module, construit les prompts et
        vérifie le garde-fou sans clé d'API, sans réseau et sans dépense.
        """
        if self._client is None:
            import anthropic  # importé ici : le kit s'installe sans lui pour les tests
            self._client = anthropic.Anthropic()
        return self._client

    # --- le tour ---------------------------------------------------------
    def repondre(self, memoire: Memoire, numero: str, message: str,
                 nom_client: str = "", quand: datetime | None = None) -> Reponse:
        maison_id = self.maison.id

        if memoire.main_humaine(maison_id, numero):
            return Reponse("", sortie="silence",
                           motif="un humain de la maison a repris cette conversation")

        memoire.noter(maison_id, numero, "user", message, entrant=True, quand=quand)

        if memoire.messages_du_client(maison_id, numero) > self.maison.limite_messages:
            # On se tait AVANT d'appeler le modèle : un plafond qui coûte des
            # jetons ne protège de rien.
            return Reponse("", sortie="silence",
                           motif=f"plus de {self.maison.limite_messages} messages en 24 h")

        historique = memoire.historique(maison_id, numero, limite=20)
        systeme = [
            {"type": "text", "text": self._socle, "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": contexte(self.maison, nom_client, quand)},
        ]

        escalades: list[dict] = []
        commandes: list[dict] = []
        jetons = {"entree": 0, "sortie": 0, "cache_lu": 0, "cache_ecrit": 0}
        messages = list(historique)
        derniere = None

        for _ in range(TOURS_OUTILS_MAX):
            derniere = self._appeler(systeme, messages)
            self._compter(jetons, derniere)

            if derniere.stop_reason != "tool_use":
                break

            messages.append({"role": "assistant", "content": derniere.content})
            resultats = []
            for bloc in derniere.content:
                if bloc.type != "tool_use":
                    continue
                # ⚠️ Les entrées d'outil se lisent avec json, jamais par comparaison
                # de chaînes : l'échappement varie d'un modèle à l'autre.
                entree = bloc.input if isinstance(bloc.input, dict) else json.loads(bloc.input)
                if bloc.name == "passer_la_main":
                    escalades.append(entree)
                    rendu = {"fait": True,
                             "message": "La maison est prévenue. Dis-le au client simplement, "
                                        "sans promettre de délai."}
                elif bloc.name == "noter_la_commande":
                    commandes.append(entree)
                    rendu = {"fait": True,
                             "message": "Commande transmise à la maison. Récapitule-la au "
                                        "client et rappelle que la maison confirme."}
                else:
                    rendu = {"fait": False, "message": f"outil inconnu : {bloc.name}"}
                resultats.append({"type": "tool_result", "tool_use_id": bloc.id,
                                  "content": json.dumps(rendu, ensure_ascii=False)})
            messages.append({"role": "user", "content": resultats})

        texte = self._texte(derniere)
        verdict = self.garde.verifier(texte)

        if not verdict.sur:
            # Le garde-fou a parlé : la réponse ne part pas telle quelle.
            log.warning("garde-fou : %s | réponse bloquée : %r",
                        verdict.explication(), texte[:200])
            escalades.append({
                "raison": "un prix annoncé ne figure pas dans la carte",
                "resume": f"L'agent allait écrire : « {texte.strip()[:300]} » — "
                          f"{verdict.explication()}.",
                "urgent": True,
            })
            texte = self._repli()
            reponse = Reponse(texte, sortie="humain", verdict=verdict,
                              escalades=escalades, commandes=commandes, jetons=jetons,
                              motif=verdict.explication())
        else:
            reponse = Reponse(texte, sortie="humain" if escalades else "agent",
                              verdict=verdict, escalades=escalades, commandes=commandes,
                              jetons=jetons)

        if reponse.texte.strip():
            memoire.noter(maison_id, numero, "assistant", reponse.texte,
                          entrant=False, quand=quand)
        if nom_client:
            memoire.nommer(maison_id, numero, nom_client)
        return reponse

    # --- plomberie -------------------------------------------------------
    def _appeler(self, systeme, messages):
        return self.client.messages.create(
            model=MODELE,
            max_tokens=JETONS_MAX,
            system=systeme,
            tools=OUTILS,
            thinking={"type": "adaptive"},
            output_config={"effort": EFFORT},
            messages=messages,
        )

    @staticmethod
    def _texte(reponse) -> str:
        if reponse is None:
            return ""
        return "\n".join(b.text for b in reponse.content
                         if getattr(b, "type", "") == "text").strip()

    @staticmethod
    def _compter(jetons: dict, reponse) -> None:
        u = getattr(reponse, "usage", None)
        if not u:
            return
        jetons["entree"] += getattr(u, "input_tokens", 0) or 0
        jetons["sortie"] += getattr(u, "output_tokens", 0) or 0
        jetons["cache_lu"] += getattr(u, "cache_read_input_tokens", 0) or 0
        jetons["cache_ecrit"] += getattr(u, "cache_creation_input_tokens", 0) or 0

    def _repli(self) -> str:
        """Ce qu'on dit quand on préfère se taire que se tromper.

        On ne s'excuse pas d'un problème technique — le client s'en moque — et
        on ne promet pas de délai, parce qu'on ne le tient pas.
        """
        return ("Je préfère vous confirmer ce point exactement plutôt que de vous "
                "donner un chiffre approximatif. Je passe la main à la maison, "
                "elle vous répond ici même.")

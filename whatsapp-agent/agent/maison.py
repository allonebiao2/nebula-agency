"""LA MAISON — tout ce qui change d'un client à l'autre, dans un seul fichier.

Un fichier `maisons/<id>.yaml` par client. Il ne contient JAMAIS de catalogue :
le catalogue est lu dans le site (voir `lecteurs/`). Il contient ce que le site
ne dit pas — les horaires, la livraison, le paiement, le ton, et surtout ce que
l'agent NE SAIT PAS et doit passer à un humain.

⚠️ `numero_patron` VIDE = l'agent ne se déploie pas. Un agent qui ne peut
prévenir personne n'est pas un agent, c'est un répondeur : le jour où un client
demande quelque chose qu'il ne sait pas, la conversation meurt en silence et la
maison ne l'apprend jamais.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Maison:
    id: str
    nom: str
    lecteur: str                       # le module de `lecteurs/` qui lit son catalogue
    metier: str = ""
    ville: str = ""
    ton: str = ""
    horaires: str = ""
    livraison: str = ""
    paiement: str = ""
    accueil: str = ""
    signature: str = ""
    numero_whatsapp: str = ""          # le numéro du client, celui qui reçoit
    numero_patron: str = ""            # où part une escalade
    a_passer: list[str] = field(default_factory=list)   # ce qui va TOUJOURS à un humain
    a_confirmer: list[str] = field(default_factory=list)  # ce que la maison n'a pas encore tranché
    limite_messages: int = 60          # garde-fou anti-abus, par client et par 24 h

    @property
    def prete(self) -> tuple[bool, list[str]]:
        """Peut-on la mettre en ligne ? Sinon, exactement ce qui manque."""
        manques = []
        if not self.numero_patron:
            manques.append("numero_patron (personne à prévenir quand l'agent ne sait pas)")
        if not self.numero_whatsapp:
            manques.append("numero_whatsapp (le numéro de la maison)")
        if not self.ton:
            manques.append("ton (comment la maison parle à ses clients)")
        return (not manques, manques)


def charger(chemin: Path) -> Maison:
    donnees = yaml.safe_load(chemin.read_text(encoding="utf-8")) or {}
    connus = {c for c in Maison.__dataclass_fields__}
    inconnus = set(donnees) - connus
    if inconnus:
        # Une clé mal orthographiée est un réglage qui ne s'applique jamais, en
        # silence. Mieux vaut refuser de démarrer que servir une maison à moitié
        # configurée en croyant qu'elle l'est.
        raise ValueError(f"{chemin.name} : clé(s) inconnue(s) {sorted(inconnus)}")
    return Maison(**donnees)


def toutes(dossier: Path) -> list[Maison]:
    return [charger(f) for f in sorted(dossier.glob("*.yaml"))]

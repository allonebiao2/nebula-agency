"""La CONSOLE — le canal qui n'envoie rien nulle part.

Il sert au simulateur et à la suite de contrôles : toute la chaîne tourne
(mémoire, catalogue, cerveau, garde-fou) et le message « part » dans une liste
qu'on peut relire. C'est ce qui permet de vérifier un agent sans compte
WhatsApp, sans jeton Meta et sans réseau.
"""
from __future__ import annotations

from canaux.base import MessageEntrant

NOM = "console"


class CanalConsole:
    def __init__(self, afficher: bool = False):
        self.nom = NOM
        self.envoyes: list[tuple[str, str]] = []
        self.afficher = afficher

    def configure(self) -> bool:
        return True

    @staticmethod
    def lire_entrant(charge: dict) -> list[MessageEntrant]:
        return [MessageEntrant(numero=str(charge.get("numero", "")),
                               texte=str(charge.get("texte", "")))]

    def envoyer(self, a: str, texte: str) -> bool:
        self.envoyes.append((a, texte))
        if self.afficher:
            print(f"\n[{a}] {texte}\n")
        return True

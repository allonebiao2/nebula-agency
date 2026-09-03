"""UN FAUX MODÈLE — pour éprouver toute la chaîne sans clé, sans réseau, sans dépense.

Ce n'est pas un jouet : c'est ce qui permet à la suite de contrôles de vérifier
les choses qu'un vrai appel ne permet PAS de vérifier de façon fiable — qu'un
prix inventé est bien bloqué, qu'une escalade réveille bien le patron, qu'un
webhook rejoué ne répond pas deux fois. Un modèle réel répond différemment à
chaque appel ; un contrôle a besoin de la même réponse à chaque fois.

⚠️ Il vit dans `tests/`, jamais dans `agent/` : rien en production ne doit
pouvoir l'importer par accident.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BlocTexte:
    text: str
    type: str = "text"


@dataclass
class BlocOutil:
    name: str
    input: dict
    id: str = "toolu_faux"
    type: str = "tool_use"


@dataclass
class Usage:
    input_tokens: int = 100
    output_tokens: int = 30
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0


@dataclass
class FausseReponse:
    content: list
    stop_reason: str = "end_turn"
    usage: Usage = field(default_factory=Usage)


class FauxModele:
    """Rejoue un scénario écrit d'avance, et garde ce qu'on lui a envoyé.

    Chaque élément de `scenario` est soit une chaîne (le modèle répond ce
    texte et s'arrête), soit un couple ("outil", nom, entrée) — le modèle appelle
    l'outil, puis passe à l'élément suivant au tour d'après.
    """

    def __init__(self, scenario: list):
        self.scenario = list(scenario)
        self.appels: list[dict] = []      # tout ce qu'on a demandé au modèle
        self.messages = self                # pour imiter `client.messages.create`

    def create(self, **kwargs):
        self.appels.append(kwargs)
        if not self.scenario:
            return FausseReponse([BlocTexte("(le scénario est épuisé)")])
        etape = self.scenario.pop(0)
        if isinstance(etape, tuple) and etape and etape[0] == "outil":
            _, nom, entree = etape
            return FausseReponse([BlocOutil(name=nom, input=entree)], stop_reason="tool_use")
        return FausseReponse([BlocTexte(str(etape))])

    # --- ce que les contrôles regardent ---------------------------------
    @property
    def dernier_systeme(self) -> list:
        return self.appels[-1].get("system", []) if self.appels else []

    @property
    def derniers_messages(self) -> list:
        return self.appels[-1].get("messages", []) if self.appels else []

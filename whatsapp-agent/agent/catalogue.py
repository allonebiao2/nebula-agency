"""Le CATALOGUE — ce que la maison vend, et à quel prix.

⚠️ RÈGLE FONDATRICE DU KIT : le catalogue n'est JAMAIS recopié à la main.
Il est LU dans le fichier qui fait déjà autorité sur le site du client
(`carte.ts` pour Au Braisé d'Or, `PIECES` pour Hillary M. Styl…). Le jour où la
maison change un prix sur son site, l'agent WhatsApp change avec lui, le même
jour, sans que personne y pense. Recopier un prix ici, c'est fabriquer une
deuxième vérité, et une deuxième vérité est une faute de prix qui attend son
tour — la leçon est déjà écrite en tête de `dishes.ts` chez Au Braisé d'Or.

⚠️ UN ARTICLE A CINQ FAÇONS D'AVOIR UN PRIX, et le kit les porte toutes parce
que la carte d'Au Braisé d'Or les utilise toutes :

    simple        3 000 F                      (un prix, un seul)
    deux_tailles  3 000 F / 6 000 F            (Normal / Grand, ou des libellés à soi)
    fourchette    de 1 500 à 3 500 F           (les sauces : le prix dépend de la garniture,
                                                la maison le confirme à la commande)
    paliers       1 000 / 1 500 / 2 500 F      (la glace, à la boule : N crans nommés)
    sur_demande   aucun prix connu             (⛔ n'entre jamais dans un total)

Aplatir tout ça sur un seul nombre, c'est ce qui faisait encaisser 1 500 F au
lieu de 2 500 F sur la glace à trois boules (leçon du 2026-08-26).
"""
from __future__ import annotations

from dataclasses import dataclass, field


def formater_fcfa(montant: int) -> str:
    """3000 → « 3 000 F ». Espace insécable : « 3 000 » ne se coupe pas en fin de ligne."""
    return f"{montant:,}".replace(",", " ") + " F"


@dataclass(frozen=True)
class Prix:
    """Le prix d'un article, dans l'un des cinq modes ci-dessus."""

    mode: str  # simple | deux_tailles | fourchette | paliers | sur_demande
    montants: tuple[tuple[str, int], ...] = ()  # (libellé, montant en FCFA)

    @property
    def connu(self) -> bool:
        return self.mode != "sur_demande" and bool(self.montants)

    @property
    def bas(self) -> int | None:
        return min(m for _, m in self.montants) if self.montants else None

    @property
    def haut(self) -> int | None:
        return max(m for _, m in self.montants) if self.montants else None

    def acceptable(self, montant: int) -> bool:
        """Ce montant peut-il honnêtement sortir de la bouche de l'agent ?

        Pour une FOURCHETTE, oui partout entre les deux bornes : le prix d'une
        sauce dépend de ce qu'on met dedans, et la maison le confirme à la
        commande. Pour tous les autres modes, il faut tomber sur un montant exact.
        """
        if not self.connu:
            return False
        if self.mode == "fourchette":
            return self.bas <= montant <= self.haut
        return any(montant == m for _, m in self.montants)

    def texte(self) -> str:
        if self.mode == "sur_demande":
            return "prix sur demande"
        if self.mode == "simple":
            return formater_fcfa(self.montants[0][1])
        if self.mode == "fourchette":
            return f"de {formater_fcfa(self.bas)} à {formater_fcfa(self.haut)} selon la garniture"
        return " · ".join(
            f"{lib} {formater_fcfa(m)}" if lib else formater_fcfa(m)
            for lib, m in self.montants
        )


@dataclass(frozen=True)
class Article:
    """Une ligne vendable : un plat, une pièce, une bouteille."""

    nom: str
    prix: Prix
    categorie: str = ""
    description: str = ""
    # Ce qu'on peut mettre dedans, et qui fait monter le prix (les garnitures des sauces).
    garnitures: tuple[str, ...] = ()
    # Les accompagnements au choix, hérités de la catégorie.
    accompagnements: tuple[str, ...] = ()
    # Délai de fabrication, quand la maison en annonce un (couture, pâtisserie).
    delai: str = ""

    def texte(self) -> str:
        bouts = [f"- {self.nom} : {self.prix.texte()}"]
        if self.description:
            bouts.append(f"  {self.description}")
        if self.garnitures:
            bouts.append("  Au choix dedans : " + ", ".join(self.garnitures))
        if self.delai:
            bouts.append(f"  Délai : {self.delai}")
        return "\n".join(bouts)


@dataclass
class Categorie:
    id: str
    label: str
    note: str = ""
    accompagnements: tuple[str, ...] = ()
    articles: list[Article] = field(default_factory=list)


@dataclass
class Catalogue:
    """Tout ce que la maison vend, tel que son site l'affiche aujourd'hui."""

    maison: str
    categories: list[Categorie] = field(default_factory=list)
    source: str = ""  # le fichier d'où ça sort, pour qu'on puisse le rouvrir
    # Les montants que la maison annonce dans une AUTRE devise, par symbole.
    # Hillary donne ses prix en F CFA, en euros et en dollars, tels quels : le
    # garde-fou doit pouvoir vérifier un « 150 € » comme il vérifie un « 100 000 F ».
    # Vide chez un client qui ne facture qu'en francs — et c'est voulu : un euro
    # cité par Au Braisé d'Or serait un euro inventé.
    devises: dict[str, set[int]] = field(default_factory=dict)

    @property
    def articles(self) -> list[Article]:
        return [a for c in self.categories for a in c.articles]

    def __len__(self) -> int:
        return len(self.articles)

    def trouver(self, nom: str) -> Article | None:
        """Retrouve un article par son nom exact, à la casse et aux accents près."""
        cible = _pliable(nom)
        for a in self.articles:
            if _pliable(a.nom) == cible:
                return a
        return None

    def chercher(self, terme: str) -> list[Article]:
        """Tous les articles dont le nom ou la description contient le terme."""
        t = _pliable(terme)
        if not t:
            return []
        return [a for a in self.articles
                if t in _pliable(a.nom) or t in _pliable(a.description)]

    def prix_acceptable(self, montant: int) -> bool:
        """Ce montant existe-t-il quelque part dans la carte ?

        C'est la question que pose le garde-fou avant de laisser partir une
        réponse : un nombre en francs qui ne correspond à aucun prix de la
        maison est un prix inventé, et un prix inventé se paie au comptoir.
        """
        return any(a.prix.acceptable(montant) for a in self.articles)

    def montants(self) -> list[tuple[int, int]]:
        """Chaque article, réduit à ce qu'il peut coûter : (borne basse, borne haute).

        Un article à prix unique donne (3000, 3000) ; une sauce donne (1500, 3500) ;
        la glace donne (1000, 2500) mais avec des crans, qui sont rendus séparément
        pour qu'un total ne puisse pas passer par un montant qui n'existe pas.
        """
        paires: list[tuple[int, int]] = []
        for a in self.articles:
            if not a.prix.connu:
                continue
            if a.prix.mode == "fourchette":
                paires.append((a.prix.bas, a.prix.haut))
            else:
                paires.extend((m, m) for _, m in a.prix.montants)
        return paires

    def texte(self) -> str:
        """La carte, telle qu'on la pose dans le prompt système (et qu'on met en cache)."""
        blocs: list[str] = []
        for c in self.categories:
            entete = f"### {c.label}"
            corps = [entete]
            if c.note:
                corps.append(c.note)
            # ⚠️ Une seule fois. La note de la rubrique énumère déjà les
            # accompagnements chez Au Braisé d'Or : les réécrire dessous doublait
            # dix lignes dans un prompt qu'on paie et qu'on met en cache, et
            # donnait au modèle deux listes à comparer là où il en faut une.
            if c.accompagnements and "ccompagnement" not in (c.note or ""):
                corps.append("Accompagnements au choix : " + ", ".join(c.accompagnements) + ".")
            corps.extend(a.texte() for a in c.articles)
            blocs.append("\n".join(corps))
        return "\n\n".join(blocs)


_ACCENTS = str.maketrans("àâäçéèêëîïôöùûüÿœæ’ʼ´",
                         "aaaceeeeiioouuuyoa'''")


def _pliable(s: str) -> str:
    """Minuscules, sans accents, apostrophes uniformisées.

    Pour comparer « Sauce Crème » et « sauce creme », mais aussi « L'ensemble
    Mira » tapé avec l'apostrophe droite et « L’ensemble Mira » tapé avec
    la typographique : ce sont deux caractères différents, et le client tape
    celui que son clavier lui donne.

    ⚠️ La chaîne rendue a EXACTEMENT la même longueur que celle d'origine —
    une lettre pour une lettre, jamais un retrait. Le garde-fou repère la
    position d'un nom d'article dans le texte replié puis lit le texte
    d'origine à cette position : un décalage d'un seul caractère attacherait
    un prix au mauvais plat.
    """
    return (s or "").strip().lower().translate(_ACCENTS)

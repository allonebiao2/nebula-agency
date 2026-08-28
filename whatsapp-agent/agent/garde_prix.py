"""LE GARDE-FOU DES PRIX — la seule pièce du kit qui rende l'agent livrable.

Un modèle de langue qui parle argent finit par arrondir. Il dira « le tilapia,
c'est 4 500 F » avec le même aplomb que s'il disait 3 000, et le client se
présentera au comptoir avec ce chiffre en tête. C'est le client qui a raison :
c'est la maison qui a écrit 4 500.

Le prompt demande de ne jamais inventer un prix. Ça ne suffit pas — une consigne
n'est pas un contrôle. Donc AVANT que la réponse parte, le code relit la
réponse, en extrait tout ce qui ressemble à un montant, et vérifie chaque
montant contre la carte. Un montant qui n'existe pas nulle part fait AVORTER
l'envoi : l'agent passe la main à un humain au lieu de mentir.

Le garde-fou lit la réponse PHRASE PAR PHRASE, et distingue deux cas.

1. UN MONTANT À CÔTÉ D'UN NOM D'ARTICLE — « le tilapia braisé, c'est 4 500 F ».
   Là on est sévère : le montant doit être un prix DE CET ARTICLE, ou une somme
   des articles nommés dans la phrase. C'est le contrôle qui vaut quelque chose,
   et c'est celui qui attrape l'invention pure.

2. UN MONTANT TOUT SEUL — « ça vous fera 4 500 F ». Là on ne peut vérifier
   qu'une chose : que ce total soit atteignable en additionnant des articles de
   la carte. C'est un contrôle FAIBLE, et il faut savoir à quel point : mesuré
   sur la carte d'Au Braisé d'Or, 90 % des montants ronds entre 100 et 18 000 F
   sont atteignables en six articles ou moins. Chez Hillary, dont les prix sont
   gros et espacés, c'est 2 %. Un total nu n'est donc presque pas vérifiable
   chez un restaurateur — c'est pour ça que le cas 1 existe, et pour ça que le
   prompt demande à l'agent de nommer ce qu'il chiffre.

Sont acceptés, dans les deux cas :

  · un prix exact de la carte                    3 000 F
  · n'importe quoi dans une fourchette           2 000 F sur une sauce à 1 500-3 500
  · une somme des articles nommés                un poulet et une salade : 4 000 F
  · un montant dans une autre devise annoncée    150 € chez Hillary, qui les donne

Tout le reste est refusé, et le refus n'est jamais silencieux : il est
journalisé et il réveille un humain.

⚠️ COMMENT ON RECONNAÎT UN ARTICLE DANS UNE PHRASE. Par son nom entier, et
sinon par un mot qui n'appartient qu'à lui dans TOUTE la carte — « tilapia »,
« gombo », « krinkrin » désignent un seul plat, « sauce » et « poulet » en
désignent dix. Ces mots distinctifs sont calculés à partir des données, jamais
écrits à la main : le jour où la maison ajoute un seul autre plat au tilapia,
le mot cesse tout seul d'être distinctif.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from math import gcd

from agent.catalogue import Catalogue, _pliable, formater_fcfa

# Combien d'articles au maximum peuvent composer un total annoncé.
# Au-delà, l'agent devrait de toute façon faire confirmer la commande.
ARTICLES_PAR_TOTAL = 6

# Un montant plus grand que ça n'est pas une commande, c'est une erreur.
def _plafond(maxi: int) -> int:
    return max(maxi * ARTICLES_PAR_TOTAL, 50_000)


# « 3 000 F », « 3000F », « 3.000 FCFA », « 100 000 francs », « 150 € », « 180 $ »
_DEVISES = r"(?:F\s?CFA|FCFA|XOF|francs?|F\b|€|EUR\b|\$|USD\b)"
# ⚠️ Les séparateurs de milliers sont nommés un par un, en échappement Unicode.
# La carte est rendue avec une espace fine insécable (U+202F) et le « F » collé
# par une insécable (U+00A0) — c'est ce qui empêche « 3 000 » de se couper en
# fin de ligne sur un téléphone. Le modèle les recopie. Une classe qui ne
# contiendrait que l'espace ordinaire lirait « 3 000 F » comme « 000 F », et le
# garde-fou vérifierait un montant qui n'a jamais été écrit.
_ESPACES = " \u00a0\u202f\u2009\u2007"
_NOMBRE = rf"\d{{1,3}}(?:[{_ESPACES}.,]\d{{3}})+|\d+"
_MONTANT = re.compile(rf"(?P<n>{_NOMBRE})\s*(?P<d>{_DEVISES})", re.IGNORECASE)
# « de 1 500 à 3 500 F » : le premier nombre est un prix lui aussi, sans symbole.
_FOURCHETTE = re.compile(
    rf"(?P<a>{_NOMBRE})\s*(?:à|a|-|–|—|et)\s*(?P<b>{_NOMBRE})\s*(?P<d>{_DEVISES})",
    re.IGNORECASE)


def _entier(brut: str) -> int | None:
    chiffres = re.sub(r"[^\d]", "", brut)
    return int(chiffres) if chiffres else None


def _symbole(brut: str) -> str:
    b = brut.lower()
    if "€" in b or "eur" in b:
        return "€"
    if "$" in b or "usd" in b:
        return "$"
    return "F"


@dataclass
class MontantCite:
    montant: int
    devise: str
    extrait: str
    position: int = 0
    # L'article auquel ce montant est ATTACHÉ : celui dont le nom est le plus
    # proche dans la phrase. C'est lui qu'on interroge, pas la carte entière.
    article: str = ""
    # Tous les articles nommés dans la phrase, pour le cas d'un total.
    articles: tuple[str, ...] = ()

    @property
    def attache(self) -> bool:
        return bool(self.article)


@dataclass
class Verdict:
    """Ce que le garde-fou a vu. `sur` est faux dès qu'un seul montant cloche."""

    sur: bool
    cites: list[MontantCite]
    fautifs: list[MontantCite]

    def explication(self) -> str:
        if self.sur:
            return "aucun montant inventé"
        bouts = []
        for m in self.fautifs:
            if m.article:
                bouts.append(f"{m.montant} {m.devise} annoncé pour « {m.article} »")
            else:
                bouts.append(f"{m.montant} {m.devise}")
        return "montant(s) que la carte ne porte pas : " + ", ".join(bouts)


def relever(texte: str) -> list[MontantCite]:
    """Tout ce qui ressemble à de l'argent dans une réponse."""
    trouves: list[MontantCite] = []
    vus: set[tuple[int, str, int]] = set()

    def ajouter(valeur: int | None, devise: str, extrait: str, position: int) -> None:
        if valeur is None:
            return
        cle = (valeur, devise, position)
        if cle in vus:
            return
        vus.add(cle)
        trouves.append(MontantCite(valeur, devise, extrait.strip(), position))

    for m in _FOURCHETTE.finditer(texte):
        devise = _symbole(m.group("d"))
        ajouter(_entier(m.group("a")), devise, m.group(0), m.start("a"))
        ajouter(_entier(m.group("b")), devise, m.group(0), m.start("b"))
    for m in _MONTANT.finditer(texte):
        ajouter(_entier(m.group("n")), _symbole(m.group("d")), m.group(0), m.start("n"))
    return trouves


# Une phrase se termine par une ponctuation forte, un retour à la ligne ou un
# point-virgule. Une puce de liste sépare aussi deux affirmations distinctes.
_COUPURE = re.compile(r"[.!?;\n\r]+|\s+[-·•]\s+")


def _segments(texte: str) -> list[str]:
    return [b for b in _COUPURE.split(texte or "") if b and b.strip()]


class GardePrix:
    """Construit une fois par catalogue : tout le coûteux est pré-calculé."""

    def __init__(self, catalogue: Catalogue, articles_par_total: int = ARTICLES_PAR_TOTAL):
        self.catalogue = catalogue
        self.articles_par_total = max(1, articles_par_total)
        self._preparer()

    # --- préparation ---------------------------------------------------
    def _preparer(self) -> None:
        paires = self.catalogue.montants()
        atomes: set[int] = set()
        self._intervalles: list[tuple[int, int]] = []
        for bas, haut in paires:
            atomes.add(bas)
            atomes.add(haut)
            if haut > bas:
                self._intervalles.append((bas, haut))
        self._atomes = atomes
        self._indexer_noms()

        if not atomes:
            self._pas, self._sommes, self._plafond = 0, 1, 0
            return

        pas = 0
        for a in atomes:
            pas = gcd(pas, a)
        self._pas = pas or 1
        self._plafond = _plafond(max(atomes))
        largeur = self._plafond // self._pas

        # Sommes atteignables, en champ de bits : le bit n dit « n × pas est un
        # total possible ». Quelques décalages d'entiers, quelques microsecondes.
        atteignables = 1
        for _ in range(self.articles_par_total):
            suivant = atteignables
            for a in atomes:
                suivant |= atteignables << (a // self._pas)
            atteignables = suivant & ((1 << (largeur + 1)) - 1)
        self._sommes = atteignables

    def _indexer_noms(self) -> None:
        """Prépare de quoi reconnaître un article cité dans une phrase."""
        self._par_nom: dict[str, list] = {}
        occurrences: dict[str, set[str]] = {}
        for a in self.catalogue.articles:
            plie = _pliable(a.nom)
            self._par_nom.setdefault(plie, []).append(a)
            # Quatre lettres suffisent : « Mira », « JOSY » et « King » nomment
            # chacun une seule pièce. C'est l'unicité qui protège, pas la
            # longueur — un mot porté par deux articles est écarté juste après.
            for mot in re.findall(r"[a-z0-9]{4,}", plie):
                occurrences.setdefault(mot, set()).add(a.nom)
        # Un mot n'est distinctif que s'il ne désigne qu'un article de la carte.
        self._mots_distinctifs: dict[str, str] = {
            mot: next(iter(noms)) for mot, noms in occurrences.items() if len(noms) == 1
        }

    def _occurrences(self, phrase: str) -> list[tuple[int, int, object]]:
        """Où chaque article est nommé dans la phrase : (début, fin, article).

        Par son nom entier, et sinon par un mot qui n'appartient qu'à lui dans
        toute la carte. Les positions sont celles du texte replié, qui a la même
        longueur que l'original : `_pliable` ne fait que baisser la casse et
        remplacer des lettres accentuées une pour une.
        """
        plie = _pliable(phrase)
        trouvees: list[tuple[int, int, object]] = []
        for nom_plie, articles in self._par_nom.items():
            for m in re.finditer(rf"(?<![a-z0-9]){re.escape(nom_plie)}(?![a-z0-9])", plie):
                for a in articles:
                    trouvees.append((m.start(), m.end(), a))
        for mot, nom in self._mots_distinctifs.items():
            article = self.catalogue.trouver(nom)
            if article is None:
                continue
            for m in re.finditer(rf"(?<![a-z0-9]){mot}(?![a-z0-9])", plie):
                trouvees.append((m.start(), m.end(), article))
        return trouvees

    def articles_cites(self, phrase: str) -> list:
        """Les articles que cette phrase nomme, sans doublon."""
        vus: dict[str, object] = {}
        for _, _, a in self._occurrences(phrase):
            vus[a.nom] = a
        return list(vus.values())

    # --- les trois questions, dans l'ordre -------------------------------
    def _quantite_avant(self, phrase: str, debut_nom: int) -> int:
        """« trois yaourts » → 3. Le nombre doit précéder LE NOM, pas le suivre.

        ⚠️ Ce détail décide d'un vrai cas : dans « la glace 4 boules », le 4
        compte des boules, pas des glaces. Le lire comme une quantité laisserait
        passer « 3 000 F » (trois glaces à 1 000) pour un barème qui s'arrête à
        2 500 F. Un nombre qui suit le nom ne compte donc pas.
        """
        avant = _pliable(phrase[max(0, debut_nom - 14):debut_nom])
        mots = {"deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6,
                "sept": 7, "huit": 8, "neuf": 9, "dix": 10}
        for mot, valeur in mots.items():
            if re.search(rf"(?<![a-z0-9]){mot}\s+[a-z\']*$", avant):
                return valeur
        m = re.search(r"(\d{1,2})\s*[a-z\']*$", avant)
        return int(m.group(1)) if m else 1

    def _prix_de(self, article, montant: int, facteur: int = 1) -> bool:
        prix = article.prix
        if not prix.connu:
            return False
        if prix.mode == "fourchette":
            return prix.bas * facteur <= montant <= prix.haut * facteur
        return any(montant == m * facteur for _, m in prix.montants)

    def _total_de_plusieurs(self, montant: int, articles: list) -> bool:
        """Un TOTAL : une addition qui met en jeu AU MOINS DEUX articles nommés.

        C'est la clé qui laisse passer « un tilapia et une salade : 4 000 F »
        sans laisser passer « le cappuccino est à 600 F » (le 600 du yaourt).
        Un montant collé à un seul article se vérifie sur cet article, point.
        """
        utiles = [a for a in articles if a.prix.connu]
        if len(utiles) < 2:
            return False
        atteints: set[tuple[int, int, int]] = {(0, 0, 0)}  # (bas, haut, nb d'articles distincts)
        for a in utiles[:6]:
            bornes = ([(a.prix.bas, a.prix.haut)] if a.prix.mode == "fourchette"
                      else [(m, m) for _, m in a.prix.montants])
            suivant = set(atteints)
            for lo, hi, n in atteints:
                for k in range(1, 4):  # jusqu'à trois fois le même article
                    for b, h in bornes:
                        suivant.add((lo + b * k, hi + h * k, n + 1))
            atteints = suivant
        return any(n >= 2 and lo <= montant <= hi for lo, hi, n in atteints)

    def montant_connu(self, montant: int, devise: str = "F", articles: list | None = None) -> bool:
        """Version courte, pour un montant isolé : utile aux contrôles et aux appels simples."""
        if montant <= 0:
            return False
        if devise != "F":
            return montant in self.catalogue.devises.get(devise, set())
        if articles:
            return (any(self._prix_de(a, montant) for a in articles)
                    or self._total_de_plusieurs(montant, articles))
        return self.total_atteignable(montant)

    def total_atteignable(self, montant: int) -> bool:
        """Contrôle FAIBLE : ce total est-il une addition possible de la carte ?"""
        if montant <= 0 or self._pas == 0:
            return False
        if montant in self._atomes:
            return True
        for bas, haut in self._intervalles:
            if bas <= montant <= haut:
                return True
        if montant > self._plafond or montant % self._pas:
            return False
        return bool(self._sommes >> (montant // self._pas) & 1)

    def verifier(self, texte: str) -> Verdict:
        cites: list[MontantCite] = []
        fautifs: list[MontantCite] = []
        for phrase in _segments(texte):
            occurrences = self._occurrences(phrase)
            nommes = list({a.nom: a for _, _, a in occurrences}.values())
            noms = tuple(a.nom for a in nommes)
            for cite in relever(phrase):
                cite.articles = noms
                proche = self._plus_proche(occurrences, cite.position, len(cite.extrait))
                if proche is not None:
                    debut_nom, article = proche
                    cite.article = article.nom
                cites.append(cite)
                if self._valide(cite, proche, phrase, nommes):
                    continue
                fautifs.append(cite)
        return Verdict(sur=not fautifs, cites=cites, fautifs=fautifs)

    def _plus_proche(self, occurrences, position: int, longueur: int):
        """L'article nommé le plus près du montant, le précédent l'emportant.

        Un nom qui vient AVANT le chiffre est le sujet de la phrase (« le
        tilapia est à 3 000 F ») ; un nom qui vient après est souvent le sujet
        suivant. À distance égale, on préfère donc celui de gauche.
        """
        meilleur = None
        for debut, fin, article in occurrences:
            if fin <= position:
                distance = position - fin
            elif debut >= position + longueur:
                distance = (debut - position - longueur) + 1  # léger malus à droite
            else:
                distance = 0
            if distance > 80:
                continue
            if meilleur is None or distance < meilleur[0]:
                meilleur = (distance, debut, article)
        return (meilleur[1], meilleur[2]) if meilleur else None

    def _valide(self, cite: MontantCite, proche, phrase: str, nommes: list) -> bool:
        if cite.montant <= 0:
            return False
        if cite.devise != "F":
            return cite.montant in self.catalogue.devises.get(cite.devise, set())
        if proche is None:
            # Aucun article nommé près du montant : on ne peut vérifier qu'un total.
            return self.total_atteignable(cite.montant)
        debut_nom, article = proche
        if self._prix_de(article, cite.montant):
            return True
        quantite = self._quantite_avant(phrase, debut_nom)
        if quantite > 1 and self._prix_de(article, cite.montant, quantite):
            return True
        return self._total_de_plusieurs(cite.montant, nommes)

    # --- de quoi écrire un message d'excuse honnête ---------------------
    def rappel_prix(self, nom: str) -> str:
        article = self.catalogue.trouver(nom)
        return f"{article.nom} : {article.prix.texte()}" if article else ""

    def resume(self) -> str:
        atomes = sorted(self._atomes)
        if not atomes:
            return "aucun prix connu"
        return (f"{len(self.catalogue)} articles · prix de {formater_fcfa(atomes[0])} "
                f"à {formater_fcfa(atomes[-1])} · {len(self._mots_distinctifs)} mots distinctifs")

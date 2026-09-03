"""HILLARY M. STYL — les pièces, lues dans la source de la vitrine.

Source : `clients/10-hillary-m-styl/_vitrine_src.html`, tableau `PIECES`.

⚠️ On lit `_vitrine_src.html`, JAMAIS `vitrine.html` : le second est généré par
`_build.py`, et la maison a pour règle qu'on n'édite ni ne cite le fichier
généré.

⚠️ LE SUPPLÉMENT EXPRESS EST PROPRE À CHAQUE PIÈCE (+40 000 F sur une robe à
100 000, +15 000 F sur une robe à 30 000). Le moteur du site a appliqué 10 000 F
à tout le monde pendant un temps, et Hillary absorbait l'écart. Ici, les deux
prix sont lus tels quels, jamais recalculés — comme les montants en euros et en
dollars, qui sont ceux qu'elle donne.
"""
from __future__ import annotations

from pathlib import Path

from agent.catalogue import Article, Catalogue, Categorie, Prix
from lecteurs.js_litteral import ErreurLitteral, lire_declaration

CHEMIN = "clients/10-hillary-m-styl/_vitrine_src.html"

# `cat` dans les données → la rubrique telle qu'on la dit à une cliente.
RUBRIQUES = {"sm": "Sur-mesure", "pap": "Prêt-à-porter"}


def _delai(p: dict) -> str:
    """« 14 jours · express 2 à 4 jours ». Une seule borne quand elles se rejoignent.

    On annonce la borne HAUTE quand on promet une date : promettre la basse
    fabrique une cliente déçue (règle posée le 2026-07-31).
    """
    def bornes(mini, maxi) -> str:
        if mini is None or maxi is None:
            return ""
        return f"{mini} jours" if mini == maxi else f"{mini} à {maxi} jours"

    normal = bornes(p.get("jmin"), p.get("jmax"))
    express = bornes(p.get("expMin"), p.get("expMax"))
    if normal and express:
        return f"{normal} · express {express}"
    return normal or express


def _prix(p: dict) -> Prix:
    """Confection normale et express sont DEUX prix vrais, pas un prix et un supplément."""
    base = p.get("prix")
    if not base:
        # « Création libre » : la cliente choisit le vêtement, le prix se dit ensuite.
        return Prix("sur_demande")
    montants = [("confection normale", int(base))]
    express = p.get("expPrix")
    if express:
        montants.append(("express", int(express)))
    if len(montants) == 1:
        return Prix("simple", (("", int(base)),))
    return Prix("paliers", tuple(montants))


def charger(racine: Path) -> Catalogue:
    source = (racine / CHEMIN).read_text(encoding="utf-8")
    brut = lire_declaration(source, "PIECES")
    if not isinstance(brut, list) or not brut:
        raise ErreurLitteral(f"{CHEMIN} : PIECES lu vide")

    par_rubrique: dict[str, Categorie] = {}
    for p in brut:
        cle = str(p.get("cat", ""))
        label = RUBRIQUES.get(cle, "Les pièces")
        cat = par_rubrique.get(cle)
        if cat is None:
            cat = Categorie(id=cle or "pieces", label=label)
            par_rubrique[cle] = cat

        description = str(p.get("ds", "") or "")
        # Les montants en euros et en dollars sont ceux qu'elle donne : on les
        # récite, on ne les recalcule pas.
        devises = []
        if p.get("eur"):
            devises.append(f"{p['eur']} €")
        if p.get("usd"):
            devises.append(f"{p['usd']} $")
        if devises:
            description = (description + " ").strip() + \
                f" (soit {' / '.join(devises)} en confection normale)"

        cat.articles.append(Article(
            nom=str(p["nom"]),
            prix=_prix(p),
            categorie=label,
            description=description.strip(),
            delai=_delai(p),
        ))

    return Catalogue(maison="Hillary M. Styl",
                     categories=list(par_rubrique.values()),
                     source=CHEMIN)

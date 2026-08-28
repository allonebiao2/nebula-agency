"""Au Braisé d'Or — la carte, lue dans le fichier que le site sert déjà.

Source : `clients/09-au-braise-dor/experience/data/carte.ts`.

⚠️ Ce fichier est LA carte. Le site l'affiche, l'agent WhatsApp la récite : une
seule vérité. `MENU.md`, à côté, n'en est qu'un résumé, et la maison a déjà payé
pour savoir qu'on ne corrige pas une donnée contre un résumé (le pêcheur à
6 000 F, 2026-08-19).
"""
from __future__ import annotations

from pathlib import Path

from agent.catalogue import Article, Catalogue, Categorie, Prix
from lecteurs.js_litteral import ErreurLitteral, lire_declaration

CHEMIN = "clients/09-au-braise-dor/experience/data/carte.ts"


def _prix(item: dict) -> Prix:
    """Les cinq modes, dans l'ordre où ils l'emportent l'un sur l'autre.

    ⚠️ La glace porte À LA FOIS `p: 1000` et ses trois `paliers` : le barème est
    plus précis que le prix d'appel, donc il passe devant. Prendre `p` ferait
    encaisser 1 000 F une glace à trois boules qui en vaut 2 500.
    """
    paliers = item.get("paliers")
    if paliers:
        return Prix("paliers", tuple((str(lib), int(m)) for lib, m in paliers))

    base = item.get("p")
    if base is None:
        return Prix("sur_demande")
    base = int(base)

    # ⚠️ `p: 0` est la convention maison pour « prix pas encore donné ». Un
    # article à 0 n'entre JAMAIS dans un total : le total mentirait.
    if base == 0:
        return Prix("sur_demande")

    haut = item.get("pMax")
    if haut is not None:
        # FOURCHETTE, pas deux tailles : le prix dépend de ce qu'on met dedans.
        return Prix("fourchette", (("", base), ("", int(haut))))

    seconde = item.get("p2")
    if seconde is not None:
        libelles = item.get("tailles") or ["Normal", "Grand"]
        return Prix("deux_tailles",
                    ((str(libelles[0]), base), (str(libelles[1]), int(seconde))))

    return Prix("simple", (("", base),))


def charger(racine: Path) -> Catalogue:
    chemin = racine / CHEMIN
    source = chemin.read_text(encoding="utf-8")
    brut = lire_declaration(source, "CARTE")
    acc = lire_declaration(source, "ACC") or {}
    if not isinstance(brut, list) or not brut:
        raise ErreurLitteral(f"{CHEMIN} : CARTE lue vide")

    categories: list[Categorie] = []
    for c in brut:
        accompagnements = tuple(acc.get(c.get("acc"), ()) or ())
        cat = Categorie(
            id=str(c.get("id", "")),
            label=str(c.get("label", "")),
            note=str(c.get("note", "") or ""),
            accompagnements=accompagnements,
        )
        for item in c.get("items", []):
            cat.articles.append(Article(
                nom=str(item["n"]),
                prix=_prix(item),
                categorie=cat.label,
                description=str(item.get("d", "") or ""),
                garnitures=tuple(str(g) for g in (item.get("garn") or ())),
                accompagnements=accompagnements,
            ))
        categories.append(cat)

    return Catalogue(maison="Au Braisé d'Or", categories=categories, source=CHEMIN)

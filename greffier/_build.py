#!/usr/bin/env python3
"""
PLUME · construction de la maquette.

    python3 plume/_build.py

Lit `_maquette_src.html`, injecte les polices en base64, écrit `maquette.html`.

⚠️ On édite `_maquette_src.html`, JAMAIS `maquette.html` : il est régénéré et
toute modification à la main y est perdue. C'est la convention de la maison
(voir `clients/10-hillary-m-styl/`).

Les polices sont embarquées dans le fichier : la page se charge entière, sans
une seule requête vers l'extérieur. C'est une contrainte de NEBULA, et c'est
aussi ce qui la rend lisible sur un forfait data qui traîne.
"""

import base64
import pathlib
import re
import sys

ICI = pathlib.Path(__file__).parent
RACINE = ICI.parent

POLICES = {
    "@BODONI@": RACINE / "clients/10-hillary-m-styl/assets/fonts/bodoni-normal.woff2",
    "@BODONI_IT@": RACINE / "clients/10-hillary-m-styl/assets/fonts/bodoni-italic.woff2",
    "@ARCHIVO@": RACINE / "clients/10-hillary-m-styl/assets/fonts/archivo-normal.woff2",
}


def construire(source: pathlib.Path) -> int:
    """Une source `_nom_src.html` devient `nom.html`, polices embarquées."""
    html = source.read_text(encoding="utf-8")

    for marque, chemin in POLICES.items():
        if not chemin.exists():
            print(f"⛔ police introuvable : {chemin}")
            return 1
        if marque not in html:
            print(f"⛔ la marque {marque} n'est pas dans la source")
            return 1
        b64 = base64.b64encode(chemin.read_bytes()).decode("ascii")
        html = html.replace(marque, f"data:font/woff2;base64,{b64}")
        print(f"   {marque:<14} {chemin.name:<22} {len(b64) // 1024} Ko en base64")

    restants = re.findall(r"@[A-Z_]+@", html)
    if restants:
        print(f"⛔ marques non remplacées : {set(restants)}")
        return 1

    sortie = ICI / (source.stem.removeprefix("_").removesuffix("_src") + ".html")
    sortie.write_text(html, encoding="utf-8")
    print(f"\n✅ {sortie.name} · {len(html.encode('utf-8')) // 1024} Ko")
    return 0


def main() -> int:
    sources = sorted(ICI.glob("_*_src.html"))
    if not sources:
        print("⛔ aucune source `_*_src.html`")
        return 1
    for source in sources:
        print(f"\n── {source.name}")
        if construire(source):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

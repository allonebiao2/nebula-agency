#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GABARIT NEBULA — construction d'une vitrine mono-fichier.

    cp _memoire/procedure-vitrine/templates/_build.py clients/NN-slug/
    cd clients/NN-slug && python3 _build.py

On édite TOUJOURS `_vitrine_src.html` (lisible, éditable).
Ce script y injecte les images en base64 et écrit `vitrine.html`, le livrable.

⚠️ Ne jamais éditer `vitrine.html` à la main : la prochaine construction
   écraserait la modification.

Pourquoi ce détour : un logo pèse ~75 Ko une fois en base64. Éditer
directement le livrable revient à travailler dans un fichier où le code utile
est noyé — et à risquer de dupliquer l'image (681 Ko sur une première version).
"""

import base64
import pathlib
import sys

ICI = pathlib.Path(__file__).resolve().parent
SRC = ICI / "_vitrine_src.html"
OUT = ICI / "vitrine.html"

# Marqueur dans la source  ->  fichier image à injecter
IMAGES = {
    "__LOGO_B64__": ICI / "assets/images/logo.webp",
    "__FAVICON_B64__": ICI / "assets/images/favicon.png",
}


def main() -> int:
    if not SRC.exists():
        print("source introuvable :", SRC)
        return 1

    html = SRC.read_text(encoding="utf-8")

    for marqueur, chemin in IMAGES.items():
        if marqueur not in html:
            print("marqueur absent de la source :", marqueur)
            return 1
        if not chemin.exists():
            print("image introuvable :", chemin)
            return 1
        b64 = base64.b64encode(chemin.read_bytes()).decode("ascii")
        html = html.replace(marqueur, b64)
        print("  %-18s %-24s %7d octets -> %7d en base64"
              % (marqueur, chemin.name, chemin.stat().st_size, len(b64)))

    OUT.write_text(html, encoding="utf-8")

    externes = html.count('src="http') + html.count("url(http")
    print("\n%s écrit — %d octets" % (OUT.name, OUT.stat().st_size))
    print("images en dur : %d · ressources externes hors polices : %d"
          % (html.count("data:image"), externes))
    if externes:
        print("⚠️  une ressource externe subsiste : à inliner (règle NEBULA)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

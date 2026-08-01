#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HILLARY M. STYL — version APERÇU, entièrement autonome.

    python3 _apercu.py    (après `python3 _build.py`)

Produit `_apercu.html` : le livrable, mais avec les polices **embarquées
en base64** au lieu du lien Google Fonts.

Pourquoi ce fichier existe : pour montrer la vitrine dans un
environnement qui bloque les domaines externes (aperçu hébergé, poste
hors ligne, démonstration chez un client sans réseau). Sans ça, Bodoni
Moda ne charge pas et toute la direction artistique tombe sur Georgia.

⚠️ Ce n'est PAS le livrable. Le livrable reste `vitrine.html`, qui garde
   le lien Google Fonts : 209 Ko de polices en base64 sur la 3G de
   Cotonou, ce serait payer la typographie deux fois pour rien puisque
   Google Fonts est mis en cache d'un site à l'autre.
"""

import base64
import pathlib
import re
import sys

ICI = pathlib.Path(__file__).resolve().parent
SRC = ICI / "vitrine.html"
OUT = ICI / "_apercu.html"
FONTS = ICI / "assets/fonts"

# fichier woff2 -> (famille CSS, graisses couvertes, style)
POLICES = [
    ("bodoni-normal.woff2", "Bodoni Moda", "400 700", "normal"),
    ("bodoni-italic.woff2", "Bodoni Moda", "400 600", "italic"),
    ("archivo-normal.woff2", "Archivo", "500 700", "normal"),
    ("manrope-normal.woff2", "Manrope", "400 700", "normal"),
]


def main() -> int:
    if not SRC.exists():
        print("livrable introuvable — lancer d'abord : python3 _build.py")
        return 1

    html = SRC.read_text(encoding="utf-8")

    faces, poids = [], 0
    for fichier, famille, graisses, style in POLICES:
        f = FONTS / fichier
        if not f.exists():
            print("police introuvable :", f)
            return 1
        poids += f.stat().st_size
        b64 = base64.b64encode(f.read_bytes()).decode("ascii")
        faces.append(
            "@font-face{font-family:'%s';font-style:%s;font-weight:%s;font-display:block;"
            "src:url(data:font/woff2;base64,%s) format('woff2')}"
            % (famille, style, graisses, b64)
        )

    bloc = "<style>" + "".join(faces) + "</style>"

    # retirer les trois balises Google Fonts, poser les polices embarquées
    avant = html
    html = re.sub(r'<link rel="preconnect" href="https://fonts\.g[^"]*"[^>]*>\s*', "", html)
    html = re.sub(r'<link href="https://fonts\.googleapis\.com[^"]*" rel="stylesheet">', bloc, html)
    if html == avant:
        print("les balises Google Fonts n'ont pas été trouvées — rien n'a été remplacé")
        return 1
    if "fonts.googleapis" in html or "fonts.gstatic" in html:
        print("il reste une référence externe aux polices")
        return 1

    OUT.write_text(html, encoding="utf-8")
    print("  polices embarquées : %d fichiers, %d Ko -> %d Ko en base64"
          % (len(POLICES), poids // 1024, int(poids * 1.34) // 1024))
    print("  %s écrit — %d Ko (le livrable en fait %d)"
          % (OUT.name, OUT.stat().st_size // 1024, SRC.stat().st_size // 1024))
    print("  ressources externes restantes :",
          html.count('src="http') + html.count("url(http") + html.count('href="http'))
    return 0


if __name__ == "__main__":
    sys.exit(main())

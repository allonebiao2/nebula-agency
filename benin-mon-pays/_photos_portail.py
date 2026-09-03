# -*- coding: utf-8 -*-
"""Les photos du PORTAIL, plus légères que celles des stations.

POURQUOI UN FICHIER À PART. Le portail montre la photo sous une nappe de
couleur, un motif et un titre de 96 px : il n'a aucun besoin de 1 400 px. Et
surtout **il enchaîne les lieux tout seul** depuis le 2026-08-11, donc chaque
kilo-octet est payé huit fois au lieu d'une.

⚠️ ON VISE UN POIDS, PAS UNE QUALITÉ. Une qualité fixe donne 15 Ko sur la
Porte et 169 Ko sur la Pendjari : la savane est pleine de feuilles, et la
compression n'a rien à mordre. On baisse donc la qualité jusqu'à tenir sous
le plafond, image par image.
"""
import os

from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(ICI, "assets", "images", "lieux")

LIEUX = ["porte", "ouidah", "cotonou", "ganvie", "abomey",
         "koutammakou", "pendjari", "fleuve"]
LARGEUR = 1000
PLAFOND = 92 * 1024      # le premier écran doit rester sous 320 Ko


def faire(nom):
    src = Image.open(os.path.join(D, nom + ".webp")).convert("RGB")
    p = os.path.join(D, nom + "-po.webp")
    # ⚠️ La Pendjari reste à 113 Ko même à la qualité la plus basse : une
    # savane, c'est des dizaines de milliers de feuilles, et la compression
    # n'a rien à mordre. Quand la qualité ne suffit plus, on RÉDUIT LA
    # TAILLE : une photo un peu plus petite sous une nappe et un titre se
    # voit moins qu'une photo pleine de vermicelles de compression.
    for larg in (LARGEUR, 860, 740, 640):
        im = src.copy()
        im.thumbnail((larg, larg), Image.LANCZOS)
        for q in (58, 50, 44, 38, 32):
            im.save(p, "WEBP", quality=q, method=6)
            if os.path.getsize(p) <= PLAFOND:
                return p, os.path.getsize(p), q, im.size
    return p, os.path.getsize(p), q, im.size


if __name__ == "__main__":
    tot = 0
    for n in LIEUX:
        p, poids, q, (l, h) = faire(n)
        tot += poids
        print("  %-22s %5.0f Ko   q=%d   %dx%d"
              % (os.path.basename(p), poids / 1024.0, q, l, h))
    print("  ---")
    print("  total %.0f Ko pour huit lieux" % (tot / 1024.0))

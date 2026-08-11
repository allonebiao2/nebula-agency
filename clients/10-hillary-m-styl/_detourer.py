# -*- coding: utf-8 -*-
"""Détoure les photos des nouveaux modèles et les pose dans assets/images/.

⚠️ Le détourage n'est pas une coquetterie : sans lui, le chiffre géant du
héros est entièrement couvert et chaque pièce tient dans une boîte blanche.
Leçon du 2026-08-06.

⚠️ On livre en WebP `quality=94, alpha_quality=100, exact=True` : l'alpha est
alors identique BIT POUR BIT à celui du PNG, pour un cinquième du poids.
Sans `exact=True`, les pixels transparents sont réécrits et la frange bave.

    python _detourer.py            traite ce qui manque
    python _detourer.py --refaire  refait tout
"""
import io
import os
import sys

from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ICI, "_sources")
DET = os.path.join(SRC, "detoure")
IMG = os.path.join(ICI, "assets", "images")

# modèle -> (dossier source, nom du fichier final)
MODELES = [
    ("modele-violette", "piece-violette"),
    ("modele-orange", "piece-orange"),
    ("modele-verte", "piece-verte"),
    ("modele-tulle", "piece-tulle"),
]

# ⚠️ ON RAISONNE EN HAUTEUR, jamais en largeur : une robe longue et une robe
# courte n'ont pas la même silhouette, et caler la LARGEUR à 1100 donnait
# 2 475 px de haut sur la robe verte, soit 689 Ko pour une seule image. Les
# quatre pièces déjà en ligne font toutes 950 px de haut pour 94 Ko de
# moyenne : c'est le standard, on s'y tient.
HAUT = 950            # la photo principale, partagée par le héros et les cartes
HAUT2 = 760           # la seconde vue, dans la fiche de commande


def detourer(chemin, session):
    from rembg import remove
    with open(chemin, "rb") as f:
        brut = f.read()
    # ⚠️ PAS d'alpha_matting : il fabrique un halo sur un fond blanc uni.
    out = remove(brut, session=session)
    return Image.open(io.BytesIO(out)).convert("RGBA")


def recadrer(im, haut):
    """Coupe au plus près de la matière, puis met à la HAUTEUR voulue.
    On n'agrandit jamais : agrandir n'ajoute rien et alourdit."""
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    haut = min(haut, im.height)
    r = haut / float(im.height)
    return im.resize((max(1, int(round(im.width * r))), haut), Image.LANCZOS)


def poser(im, dest):
    im.save(dest, "WEBP", quality=94, alpha_quality=100,
            method=6, exact=True)
    return os.path.getsize(dest)


if __name__ == "__main__":
    from rembg import new_session
    os.makedirs(DET, exist_ok=True)
    os.makedirs(IMG, exist_ok=True)
    refaire = "--refaire" in sys.argv
    session = new_session("isnet-general-use")

    for dossier, base in MODELES:
        d = os.path.join(SRC, dossier)
        if not os.path.isdir(d):
            print("%-18s dossier absent, ignore" % dossier)
            continue
        for vue, hh, suffixe in [("face", HAUT, ""), ("dos", HAUT2, "-dos")]:
            src = None
            for ext in (".jpeg", ".jpg", ".png"):
                p = os.path.join(d, vue + ext)
                if os.path.exists(p):
                    src = p
                    break
            if not src:
                print("%-18s %-5s introuvable" % (dossier, vue))
                continue

            png = os.path.join(DET, base + suffixe + ".png")
            if refaire or not os.path.exists(png):
                im = detourer(src, session)
                im = recadrer(im, hh)
                im.save(png, "PNG", optimize=True)
            else:
                im = Image.open(png).convert("RGBA")

            web = os.path.join(IMG, base + suffixe + ".webp")
            t = poser(im, web)

            # combien de la photo reste opaque ? un detourage rate laisse
            # tout opaque (fond garde) ou presque rien (sujet mange)
            a = im.split()[3]
            h = a.histogram()
            opaque = sum(h[250:]) / float(im.width * im.height)
            print("%-18s %-5s %4dx%-4d  %6d o  matiere %.0f%%  %s"
                  % (dossier, vue, im.width, im.height, t, opaque * 100,
                     "OK" if 0.12 < opaque < 0.80 else "A REGARDER"))

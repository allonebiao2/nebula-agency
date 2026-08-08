# -*- coding: utf-8 -*-
"""
ANGY ART — fabrique les images du site à partir des VRAIES photos.

Source : _sources/photos/*.webp   (photos fournies par la cliente, 2026-08-08,
         archivées en WebP qualité 95 ; les PNG d'origine pesaient 34 Mo)
Sortie : assets/images/scenes/*.webp
         assets/images/situations/*.webp

Deux familles, et elles ne se traitent pas pareil :

  · ATELIER      photos 100 % réelles d'Angélique au travail, à Cotonou.
                 Ce sont elles qui portent l'authenticité du site. Aucun
                 trucage, aucun ajout : on recadre, on redimensionne, point.

  · SITUATIONS   ses VRAIS masques, photographiés dans des intérieurs de
                 présentation montés. Le site les annonce comme des MISES EN
                 SITUATION : jamais un prix, jamais un titre d'œuvre, jamais
                 le mot « disponible ». Preuve que les masques sont d'elle :
                 le terracotta à spirale de situ-duo est celui qu'elle peint
                 sur atelier-trait, et le jaune/orange de situ-perles est
                 celui d'atelier-detail.
                 Seule retouche : noyer dans le flou le dos d'un livre de
                 décor dont le titre est mal orthographié (« PICASO »). On ne
                 touche pas à l'œuvre, on efface une faute du décor.

Relancer :  python _photos.py           (idempotent)
            python _photos.py --voir    (détaille chaque sortie)
"""
import os
import sys

from PIL import Image, ImageFilter

ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ICI, "_sources", "photos")
SCENES = os.path.join(ICI, "assets", "images", "scenes")
SITUS = os.path.join(ICI, "assets", "images", "situations")


def ouvrir(nom):
    return Image.open(os.path.join(SRC, nom)).convert("RGB")


def recadrer(im, boite):
    """boite = (gauche, haut, droite, bas), en fraction de l'image."""
    L, H = im.size
    g, h, d, b = boite
    return im.crop((int(g * L), int(h * H), int(d * L), int(b * H)))


def poser(im, dest, large, qualite=84):
    L, H = im.size
    if L > large:
        im = im.resize((large, round(H * large / L)), Image.LANCZOS)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    im.save(dest, "WEBP", quality=qualite, method=6)
    return im.size


# ── ce que chaque photo devient, et où elle atterrit ──────────────────────
# (source, sortie, dossier, recadrage, largeur finale)
PLAN = [
    # LE HÉROS — elle peint dehors, de profil, sur le grand masque en relief.
    ("atelier-dehors.webp", "hero.webp", SCENES, (0.00, 0.05, 1.00, 0.88), 1100),

    # 01 LA DÉMARCHE — le geste de précision, le pinceau fin.
    ("atelier-precision.webp", "demarche.webp", SCENES, (0.02, 0.03, 1.00, 0.90), 900),

    # 02 LA MAIN EN QUATRE TEMPS — la chronologie vraie d'une pièce.
    ("atelier-enduit.webp", "temps-1.webp", SCENES, (0.28, 0.00, 0.84, 1.00), 780),
    ("atelier-pigment.webp", "temps-2.webp", SCENES, (0.24, 0.00, 0.80, 1.00), 780),
    ("atelier-trait.webp", "temps-3.webp", SCENES, (0.30, 0.00, 0.86, 1.00), 780),
    ("atelier-grande-toile.webp", "temps-4.webp", SCENES, (0.28, 0.00, 0.84, 1.00), 780),

    # 04 LA CITATION — la matière seule, sans personne : détail du relief.
    ("atelier-dehors.webp", "matiere.webp", SCENES, (0.42, 0.00, 1.00, 0.56), 900),

    # 05 POUR UN LIEU — le masque monumental dans un restaurant.
    ("lieu-restaurant.webp", "lieu.webp", SCENES, (0.00, 0.00, 1.00, 1.00), 900),

    # 06 LA VISITE — le duo dans son cadre large, en fond de section.
    ("situ-duo.webp", "visite.webp", SCENES, (0.00, 0.00, 1.00, 1.00), 1500),

    # 03 LE CARROUSEL — les six mises en situation, dans cet ordre.
    # Le duo est recadré en portrait : les six cartes gardent le même rythme.
    ("situ-duo.webp", "situ-1.webp", SITUS, (0.25, 0.02, 0.77, 1.00), 1000),
    ("situ-perles.webp", "situ-2.webp", SITUS, (0.00, 0.00, 1.00, 1.00), 1000),
    ("situ-bleu.webp", "situ-3.webp", SITUS, (0.00, 0.00, 1.00, 1.00), 1000),
    ("situ-jaune-clair.webp", "situ-4.webp", SITUS, (0.00, 0.00, 1.00, 1.00), 1000),
    ("situ-terracotta.webp", "situ-5.webp", SITUS, (0.00, 0.00, 1.00, 1.00), 1000),
    ("situ-jaune-sombre.webp", "situ-6.webp", SITUS, (0.00, 0.00, 1.00, 1.00), 1000),
]

# Le dos du livre de décor porte « PICASO ». C'est une faute du décor, pas de
# l'œuvre : on la noie dans une profondeur de champ, comme sur n'importe quelle
# photo d'intérieur. Fractions de l'image source.
# ⚠️ Un flou posé sur un rectangle net se VOIT : on distingue les quatre arêtes.
# Le masque est donc dégradé (`ADOUCI`), et la zone déborde largement du livre
# pour que la transition tombe sur du mur uni.
FLOU_DECOR = {"situ-bleu.webp": (0.745, 0.400, 1.000, 0.980)}
RAYON = 12      # force du flou
ADOUCI = 55     # largeur du dégradé du masque, en pixels


def flouter_doux(im, boite):
    """Floute une zone en fondu, sans laisser d'arête visible."""
    L, H = im.size
    g, h, d, b = boite
    zone = (int(g * L), int(h * H), int(d * L), int(b * H))
    masque = Image.new("L", im.size, 0)
    masque.paste(255, zone)
    masque = masque.filter(ImageFilter.GaussianBlur(ADOUCI))
    return Image.composite(im.filter(ImageFilter.GaussianBlur(RAYON)), im, masque)


def main():
    voir = "--voir" in sys.argv
    total = 0
    print("ANGY ART — les images du site, depuis les vraies photos\n")
    for src, sortie, dossier, boite, large in PLAN:
        im = ouvrir(src)
        if src in FLOU_DECOR:
            im = flouter_doux(im, FLOU_DECOR[src])
        im = recadrer(im, boite)
        dest = os.path.join(dossier, sortie)
        taille = poser(im, dest, large)
        ko = os.path.getsize(dest) // 1024
        total += ko
        if voir:
            rel = os.path.relpath(dest, ICI).replace("\\", "/")
            print(f"  {taille[0]:4d}x{taille[1]:<5d} {ko:4d} Ko   {rel:42s} <- {src}")
    print(f"\n{len(PLAN)} images, {total} Ko au total.")


if __name__ == "__main__":
    main()

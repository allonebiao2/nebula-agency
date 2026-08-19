# -*- coding: utf-8 -*-
"""
DÉTOURE UN PLAT POUR LE HÉROS — Au Braisé d'Or.

    python _outils/_detoure_plats.py

Le héros pose l'assiette sur un fond crème : sans détourage, le plat arrive
dans un carré noir. Les images de `experience/public/plats/` sont donc TOUTES
en RGBA, c'est la règle de cette scène ; celles de `public/carte/` sont
carrées et opaques, elles servent aux cartes du catalogue.

⚠️ MODÈLE : `isnet-general-use`, choisi sur planche comparative (2026-08-19),
pas au hasard :
  · `u2net`            perd le bol et ne garde que la viande ;
  · `birefnet-general` déchiquette le bol ;
  · `isnet-general-use` garde le bol entier ET la vapeur, qui fait tout le
    charme de ces images.

⚠️ CE QUI NE MARCHE PAS. Sur la Béchamel et la Sauce Crème, isnet garde un
morceau de l'ardoise posée sous le bol : une languette sombre, invisible en
vignette et flagrante au format du héros. Tenter de la retirer par ouverture
morphologique (`binary_opening` + dilatation) MORD DANS LE BOL et laisse une
encoche : essayé, c'est pire que le mal. Ces deux sauces attendent donc une
vraie photo. Ne pas refaire l'essai en pensant l'améliorer.

⚠️ WEBP en `quality=94, alpha_quality=100, exact=True` : réglage retenu chez
Hillary, l'alpha ressort bit pour bit celui du PNG pour un cinquième du poids.
"""
import os
import sys

from PIL import Image
from rembg import remove, new_session

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RACINE, "experience", "public", "carte")
DST = os.path.join(RACINE, "experience", "public", "plats")

# Ce qui passe au héros. Le nom du fichier est le même des deux côtés.
A_DETOURER = ["sc-moyo", "sc-poisson"]


def main():
    session = new_session("isnet-general-use")
    for nom in A_DETOURER:
        src = os.path.join(SRC, nom + ".webp")
        if not os.path.exists(src):
            sys.exit("⛔ introuvable : " + src)
        im = Image.open(src).convert("RGB").resize((1100, 1100), Image.LANCZOS)
        out = remove(im, session=session, post_process_mask=True)

        alpha = out.getchannel("A")
        bas, haut = alpha.getextrema()
        if haut < 250 or bas > 5:
            sys.exit("⛔ %s : l'alpha va de %d à %d, le détourage a échoué."
                     % (nom, bas, haut))
        out = out.crop(alpha.getbbox())

        dst = os.path.join(DST, nom + ".webp")
        out.save(dst, "WEBP", quality=94, alpha_quality=100, exact=True)
        print("%-12s %4dx%-4d  %3d Ko  →  plats/%s.webp"
              % (nom, out.width, out.height,
                 os.path.getsize(dst) // 1024, nom))

    print("\n⚠️ REGARDER LE RÉSULTAT SUR FOND CRÈME (#ede9e3), pas sur du blanc :")
    print("   un halo clair ne se voit que sur le fond où l'image sera posée.")


if __name__ == "__main__":
    main()

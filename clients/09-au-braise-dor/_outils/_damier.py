# -*- coding: utf-8 -*-
"""
LES PLATS DÉTOURÉS PAR LA MAISON — Au Braisé d'Or.

    python _outils/_damier.py

Mongazi envoie les plats déjà détourés, mais les fichiers arrivent en **RGB sans
canal alpha** : le damier gris de son éditeur est PEINT dans les pixels. Il faut
donc redétourer, en traitant le damier comme un fond ordinaire.

⚠️ ET C'EST TOUT CE QU'IL Y A À FAIRE. J'ai d'abord voulu retirer le damier
« proprement », en le reconnaissant à ses deux gris : on apprend les gris sur
les coins, on remplit depuis les bords, on ponte les pixels de transition, on
rembourre pour que l'érosion ne mange pas l'anneau du bord… Quatre tours, et un
échec de fond : **sur le gombo, les deux gris du damier sont 77 et 124, et le
bord noir de l'assiette a des reflets dans cette plage.** Aucun seuil de
luminance ne les sépare — le bord se faisait manger et laissait un escalier
dans l'assiette. Reconstruire la grille du damier pour ne retirer que ce qui
coïncide avec elle n'a pas marché non plus (phase et pas dérivent).

**rembg, lui, sort les trois d'un coup, sans une bavure.** Un modèle de saillance
ne se demande pas de quelle couleur est le fond : il voit une assiette.

⚠️ ICI `isnet-general-use` gagne — assiette entière, vapeur gardée. Ce n'est pas
la même conclusion que `_photos_sauces.py`, où birefnet gagnait sur les MÊMES
plats photographiés sur fond noir. Le fond change, le gagnant change :
**refaire la planche comparative à chaque lot.**
"""
import os
import sys

from PIL import Image
from rembg import remove, new_session

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTAGE = os.path.normpath(os.path.join(RACINE, "..", "..", "_partage"))
PLATS = os.path.join(RACINE, "experience", "public", "plats")

# ⚠️ L'ordre des fichiers reçus ne suit PAS l'ordre du message. L'appariement
# est vérifié à l'œil sur la FORME DE L'ASSIETTE — gombo octogonale, krinkrin
# octogonale sur ardoise, feuille hexagonale — les mêmes repères que les trois
# vignettes imprimées sur la feuille de menu de la maison.
LOTS = [
    ("sc-gombo", "2026-08-19-sauce-gombo-detoure.png"),
    ("sc-krinkrin", "2026-08-19-sauce-krinkrin-detoure.png"),
    ("sc-feuille", "2026-08-19-sauce-feuille-detoure.png"),
]


def main():
    session = new_session("isnet-general-use")
    for slug, fichier in LOTS:
        src = os.path.join(PARTAGE, fichier)
        if not os.path.exists(src):
            sys.exit("⛔ introuvable : " + src)
        im = Image.open(src).convert("RGB")
        out = remove(im, session=session, post_process_mask=True)

        alpha = out.getchannel("A")
        bas, haut = alpha.getextrema()
        if haut < 250 or bas > 5:
            sys.exit("⛔ %s : alpha de %d à %d, le détourage a échoué." % (slug, bas, haut))
        out = out.crop(alpha.getbbox())
        out.thumbnail((1200, 1200), Image.LANCZOS)

        dst = os.path.join(PLATS, slug + ".webp")
        out.save(dst, "WEBP", quality=94, alpha_quality=100, exact=True)
        print("%-13s %4dx%-4d  %3d Ko" % (slug, out.width, out.height,
                                          os.path.getsize(dst) // 1024))

    print("\n⚠️ REGARDER LE RÉSULTAT SUR FOND CRÈME (#ede9e3), jamais sur du blanc.")


if __name__ == "__main__":
    main()

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

import numpy as np
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
    ("sc-gombo", "2026-08-19-sauce-gombo-detoure.png", False),
    ("sc-feuille", "2026-08-19-sauce-feuille-detoure.png", False),
    ("sc-graine", "2026-08-19-sauce-graine-detoure.png", False),
    # ⚠️ LE KRINKRIN REJOINT LES AUTRES LE 2026-08-26, et l'exception tombe.
    # Il venait d'une source à part pour une seule raison : sa version
    # détourée de 2026-08-19 était RECADRÉE TROP SERRÉ — l'assiette touchait
    # les bords et l'ardoise sortait du cadre à gauche, à droite et en bas.
    # On repartait donc de la photo sur fond noir, où l'assiette tient
    # entière… mais assiette NOIRE sur table NOIRE : le masque gardait une
    # dalle de table sous le plat (16,7 % de transparent seulement), et sur le
    # fond crème du héros ça faisait un pâté sombre. C'est le défaut que
    # Mongazi a signalé : « elle a mal été découpée au niveau de la héros ».
    # Il a renvoyé le plat détouré par ses soins, cette fois CORRECTEMENT
    # CADRÉ. La raison de l'exception n'existe plus.
    # ⚠️ Et la rustine anti-vapeur ne sert plus : mesuré sur cette source, il
    # n'y a que 9 lignes étroites au-dessus de l'assiette et leur largeur
    # croît régulièrement (10, 51, 86, 116…) — c'est le coin de l'octogone qui
    # s'élargit, pas un panache transformé en tache.
    # ⚠️ Le fichier porte l'extension .jpg et ce n'est pas une erreur : le
    # damier arrive PEINT DANS LES PIXELS, sans canal alpha, et cette fois
    # aplati en JPEG. On ne le renomme pas en .png pour faire joli.
    ("sc-krinkrin", "2026-08-26-sauce-krinkrin-detoure.jpg", False),
]


def main():
    session = new_session("isnet-general-use")
    for slug, fichier, couper_vapeur in LOTS:
        src = os.path.join(PARTAGE, fichier)
        if not os.path.exists(src):
            sys.exit("⛔ introuvable : " + src)
        im = Image.open(src).convert("RGB")
        out = remove(im, session=session, post_process_mask=True)

        alpha = out.getchannel("A")
        bas, haut = alpha.getextrema()
        if haut < 250 or bas > 5:
            sys.exit("⛔ %s : alpha de %d à %d, le détourage a échoué." % (slug, bas, haut))

        if couper_vapeur:
            m = np.asarray(alpha).copy()
            largeurs = (m > 120).sum(axis=1)
            depart = int(np.argmax(largeurs > 0.28 * largeurs.max()))
            m[:depart, :] = 0
            alpha = Image.fromarray(m)
            out.putalpha(alpha)

        out = out.crop(alpha.getbbox())
        out.thumbnail((1200, 1200), Image.LANCZOS)

        dst = os.path.join(PLATS, slug + ".webp")
        out.save(dst, "WEBP", quality=94, alpha_quality=100, exact=True)
        print("%-13s %4dx%-4d  %3d Ko" % (slug, out.width, out.height,
                                          os.path.getsize(dst) // 1024))

    print("\n⚠️ REGARDER LE RÉSULTAT SUR FOND CRÈME (#ede9e3), jamais sur du blanc.")


if __name__ == "__main__":
    main()

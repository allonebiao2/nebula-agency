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
from PIL import Image, ImageDraw
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
    # ⛔ CETTE PHOTO N'A JAMAIS ETE LA SAUCE GRAINE. Mongazi, 2026-08-26 :
    #    « celle actuelle sur la vitrine est pour la sauce d'arachide de base ».
    #    Il a raison, et ca se voit a deux choses : la sauce est CREMEUSE ET
    #    BEIGE (la graine est rouge, c'est de l'huile de palme), et le plat est
    #    un bol rond a bord CUIVRE — toutes les autres photos de la maison sont
    #    dans la meme assiette octogonale noire. C'etait un autre jour, un autre
    #    plat. Le fichier source a ete renomme lui aussi : on ne garde pas dans
    #    `_partage` un nom qui ment.
    ("sc-arachide", "2026-08-19-sauce-arachide-detoure.png", False),
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
    # ⚠️ Tête de mouton (gbotâ), 2026-08-26. Planche refaite comme toujours :
    #    ici birefnet JETTE L'ASSIETTE et ne garde que la viande, qui flotte
    #    sans bol ni sauce (23,4 % d'opaque contre 49,6). isnet garde le plat
    #    entier, bord compris. L'écart entre les deux modèles est le plus net
    #    qu'on ait mesuré : 26 points.
    ("sc-tete-mouton", "2026-08-26-sauce-tete-mouton-detoure.jpg", False),
    # ⚠️ Yassa au poulet, 2026-08-26. Planche refaite : birefnet mange le bord
    #    noir de l'assiette a gauche et laisse une encoche a droite ; isnet
    #    garde l'octogone entier. Troisieme lot d'affilee ou isnet gagne sur
    #    une source en damier — la conclusion de ce fichier tient.
    ("sc-yassa-poulet", "2026-08-26-sauce-yassa-poulet-detoure.jpg", False),
    # ⚠️ Pieds de boeuf (blokoto), 2026-08-26. Planche refaite : birefnet mange
    #    presque tout le bord noir, il ne reste qu'un filet en bas a gauche et la
    #    masse de viande sort avec un contour dechire ; isnet garde l'octogone.
    #    QUATRIEME lot d'affilee ou isnet gagne sur une source en damier.
    ("sc-pieds-boeuf", "2026-08-26-sauce-pieds-boeuf-detoure.jpg", False),
    # la VRAIE sauce graine, recue le 2026-08-26 : rouge d'huile de palme.
    ("sc-graine", "2026-08-26-sauce-graine-detoure.jpg", False),
]


def reboucher(alpha, seuil=8):
    """⚠️ UNE ASSIETTE N'A NI TROU NI FENTE.

    Sur la sauce graine (2026-08-26), le masque a taille un COULOIR VERTICAL
    dans le rebord du plat : 158 lignes percees, 52 px au pire, soit 5,8 % de
    la largeur. Invisible sur fond blanc, bien visible sur le creme du heros —
    une morsure claire au milieu de l'assiette.

    Deux passes, et elles ne servent pas a la meme chose :

    1. LES CAVITES. Tout ce qui est transparent et qu'on ne peut PAS atteindre
       depuis le bord de l'image est, par definition, enferme. Le fond
       communique toujours avec le bord ; la vapeur aussi, qui monte jusqu'en
       haut du cadre.

    2. LES FENTES. Un couloir qui DEBOUCHE echappe a la premiere passe. On
       reboucle donc ligne par ligne : tout intervalle transparent pris entre
       deux morceaux de plat et plus etroit que 8 % de la largeur est comble.

    ⚠️ LIGNE PAR LIGNE, JAMAIS COLONNE PAR COLONNE. En colonnes, l'espace entre
    le panache de vapeur et l'assiette serait « pris entre deux morceaux » lui
    aussi, et on souderait la vapeur au plat.

    Mesure : six des sept assiettes n'ont aucune fente et ressortent
    identiques ; seul le gombo en a une de 3 px, sans effet visible.
    """
    n = np.asarray(alpha).copy()
    total = 0

    dehors = Image.new("L", (n.shape[1] + 2, n.shape[0] + 2), 0)
    dehors.paste(Image.fromarray((n > seuil).astype("uint8") * 255), (1, 1))
    ImageDraw.floodfill(dehors, (0, 0), 128)
    atteint = np.asarray(dehors)[1:-1, 1:-1] == 128
    cavites = (n <= seuil) & (~atteint)
    if cavites.any():
        n[cavites] = 255
        total += int(cavites.sum())

    maxi = int(0.08 * n.shape[1])
    op = n > seuil
    for y in range(n.shape[0]):
        xs = np.flatnonzero(op[y])
        if xs.size < 2:
            continue
        d = np.diff(xs)
        for i in np.flatnonzero(d > 1):
            if d[i] - 1 <= maxi:
                n[y, xs[i] + 1:xs[i + 1]] = 255
                total += int(d[i]) - 1

    if not total:
        return alpha, 0
    return Image.fromarray(n), total


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

        alpha, comble = reboucher(alpha)
        if comble:
            out.putalpha(alpha)
            print("   %-13s %d px de trou ou de fente reboucher" % (slug, comble))

        out = out.crop(alpha.getbbox())
        out.thumbnail((1200, 1200), Image.LANCZOS)

        dst = os.path.join(PLATS, slug + ".webp")
        out.save(dst, "WEBP", quality=94, alpha_quality=100, exact=True)
        print("%-13s %4dx%-4d  %3d Ko" % (slug, out.width, out.height,
                                          os.path.getsize(dst) // 1024))

    print("\n⚠️ REGARDER LE RÉSULTAT SUR FOND CRÈME (#ede9e3), jamais sur du blanc.")


if __name__ == "__main__":
    main()

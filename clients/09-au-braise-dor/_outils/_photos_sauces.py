# -*- coding: utf-8 -*-
"""
LES PHOTOS DES SAUCES — Au Braisé d'Or.

    python _outils/_photos_sauces.py

Prend les photos envoyées par la maison (dans `_partage/`) et en tire les
DEUX formes dont le site a besoin :

  · `experience/public/carte/<slug>.webp`  carré, opaque   → la carte
  · `experience/public/plats/<slug>.webp`  détouré, RGBA   → le héros

⚠️ POURQUOI DEUX FORMES. Le héros pose l'assiette sur un fond crème : une
image opaque y arriverait dans un carré noir. Les cartes du catalogue, elles,
montrent la photo entière dans un cadre — le détourage y ferait flotter le plat
dans le vide.

⚠️ LE CARRÉ N'EST PAS UN RECADRAGE AVEUGLE. On se sert du masque de détourage
pour savoir OÙ est l'assiette, puis on centre le carré dessus. Un recadrage
centré à l'aveugle coupait le bord du plat sur deux des trois photos.

⚠️ CES PHOTOS SONT DE VRAIES PHOTOS DE PLATS BÉNINOIS, retouchées à l'IA par
Mongazi, qui l'a confirmé le 2026-08-19. Ce ne sont donc PAS des images
générées : la règle du 2026-08-01 ne s'y applique pas. Les originaux restent
dans `_partage/` pour que ça reste vérifiable.

⚠️ L'APPARIEMENT PHOTO ↔ SAUCE EST VÉRIFIÉ, pas deviné. La feuille de menu de
la maison porte trois vignettes imprimées, et la FORME DE L'ASSIETTE concorde :
gombo octogonale, feuille hexagonale, krinkrin octogonale sur ardoise.
"""
import os
import sys

from PIL import Image
from rembg import remove, new_session

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTAGE = os.path.join(os.path.dirname(RACINE), "..", "_partage")
PARTAGE = os.path.normpath(os.path.join(RACINE, "..", "..", "_partage"))
CARTE = os.path.join(RACINE, "experience", "public", "carte")
PLATS = os.path.join(RACINE, "experience", "public", "plats")

# (slug, fichier, faire_le_heros) — ⚠️ le héros de certaines sauces vient
# d'un AUTRE fichier, celui que la maison a détouré elle-même : voir
# `_damier.py`. Le mettre à False ici évite de l'écraser au passage.
PHOTOS = [
    # ⚠️ TOUS À False DEPUIS LE 2026-08-19 : les quatre héros viennent
    # désormais des fichiers que la maison a détourés elle-même, traités par
    # `_damier.py`. Laisser True ici les écraserait silencieusement à la
    # prochaine régénération — et on retrouverait les découpes sans assiette.
    ("sc-gombo", "2026-08-19-sauce-gombo.png", False),
    ("sc-krinkrin", "2026-08-19-sauce-krinkrin.png", False),
    ("sc-feuille", "2026-08-19-sauce-feuille.png", False),
    ("sc-graine", "2026-08-19-sauce-graine.png", False),
]


def carre_autour(src, masque, marge=0.06):
    """Le plus grand carré centré sur l'assiette, sans sortir de l'image."""
    boite = masque.getbbox()
    if not boite:
        return src
    gx, hy, dx, by = boite
    cx, cy = (gx + dx) // 2, (hy + by) // 2
    cote = int(max(dx - gx, by - hy) * (1 + marge))
    cote = min(cote, src.width, src.height)
    g = max(0, min(cx - cote // 2, src.width - cote))
    h = max(0, min(cy - cote // 2, src.height - cote))
    return src.crop((g, h, g + cote, h + cote))


def main():
    # ⚠️ birefnet ICI, isnet POUR LES BOLS. Ce n'est pas une préférence, c'est
    # une planche comparative (2026-08-19) : sur ces photos-là — assiettes
    # NOIRES sur fond NOIR — isnet garde une tache de vapeur pleine au-dessus
    # du krinkrin, une encoche dans l'assiette de la feuille et un bout
    # d'ardoise ; birefnet découpe la masse du plat proprement. Sur les bols
    # de `_detoure_plats.py`, c'est exactement l'inverse.
    # → Refaire la planche à chaque nouveau lot de photos, ne pas présumer.
    session = new_session("birefnet-general")
    for slug, fichier, faire_le_heros in PHOTOS:
        src = os.path.join(PARTAGE, fichier)
        if not os.path.exists(src):
            sys.exit("⛔ introuvable : " + src)
        origine = Image.open(src).convert("RGB")

        decoupe = remove(origine, session=session, post_process_mask=True)
        alpha = decoupe.getchannel("A")
        bas, haut = alpha.getextrema()
        if haut < 250 or bas > 5:
            sys.exit("⛔ %s : alpha de %d à %d, le détourage a échoué." % (slug, bas, haut))

        # 1. la carte : carré, opaque, centré sur l'assiette
        car = carre_autour(origine, alpha).resize((900, 900), Image.LANCZOS)
        fc = os.path.join(CARTE, slug + ".webp")
        car.save(fc, "WEBP", quality=82, method=6)

        if not faire_le_heros:
            print("%-12s carte %3d Ko %dx%d   (héros : voir _damier.py)"
                  % (slug, os.path.getsize(fc) // 1024, car.width, car.height))
            continue

        # 2. le héros : détouré, RGBA
        det = decoupe.crop(alpha.getbbox())
        det.thumbnail((1200, 1200), Image.LANCZOS)
        fp = os.path.join(PLATS, slug + ".webp")
        det.save(fp, "WEBP", quality=94, alpha_quality=100, exact=True)

        print("%-12s carte %3d Ko %dx%d   héros %3d Ko %dx%d"
              % (slug, os.path.getsize(fc) // 1024, car.width, car.height,
                 os.path.getsize(fp) // 1024, det.width, det.height))

    print("\n⚠️ REGARDER LE DÉTOURAGE SUR FOND CRÈME (#ede9e3), jamais sur du blanc :")
    print("   un halo clair ne se voit que sur le fond où l'image sera posée.")


if __name__ == "__main__":
    main()

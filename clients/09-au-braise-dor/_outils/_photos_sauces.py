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
import subprocess
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
    # (slug, fichier, faire_le_heros, refaire_le_carre)
    # ⚠️ `refaire_le_carre=False` N'EST PAS UN OUBLI. Le carré automatique se
    #    centre sur le masque avec 6 % de marge : sur `sc-graine` il coupe TOUT
    #    LE BORD DU BOL et il ne reste qu'une texture jaune, sans vaisselle —
    #    la carte du menu en ligne, elle, montre le bol entier. Vu à l'œil le
    #    2026-08-26 en comparant les deux. `sc-feuille` change aussi de cadre
    #    sans que personne l'ait demandé.
    #    Ces deux cartes-là sont donc GELÉES : elles ne se régénèrent plus.
    #    Sans ce drapeau, la prochaine exécution les écrasait en silence — et
    #    c'est précisément ce qui vient d'arriver, parce que le script mourait
    #    jusqu'ici avant de les atteindre.
    ("sc-gombo", "2026-08-19-sauce-gombo.png", False, True),
    ("sc-feuille", "2026-08-19-sauce-feuille.png", False, False),
    ("sc-graine", "2026-08-19-sauce-graine.png", False, False),
    # ⚠️ Krinkrin refait le 2026-08-26 : la maison a renvoyé la même sauce en
    #    1254 px sur fond noir, plus nette et mieux éclairée que la photo de
    #    2026-08-19 dont venait l'ancien carré. Le héros, lui, vient toujours
    #    du fichier détouré par la maison — d'où le False.
    ("sc-krinkrin", "2026-08-26-sauce-krinkrin-v2.png", False, True),
    ("sc-tete-mouton", "2026-08-26-sauce-tete-mouton.png", False, True),
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


def une(slug, fichier, faire_le_heros, refaire_le_carre=True):
    """UNE photo, UN processus. Voir `main()` pour le pourquoi."""
    # ⚠️ birefnet ICI, isnet POUR LES BOLS. Ce n'est pas une préférence, c'est
    # une planche comparative (2026-08-19) : sur ces photos-là — assiettes
    # NOIRES sur fond NOIR — isnet garde une tache de vapeur pleine au-dessus
    # du krinkrin, une encoche dans l'assiette de la feuille et un bout
    # d'ardoise ; birefnet découpe la masse du plat proprement. Sur les bols
    # de `_detoure_plats.py`, c'est exactement l'inverse.
    # → Refaire la planche à chaque nouveau lot de photos, ne pas présumer.
    session = new_session("birefnet-general")
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
    fc = os.path.join(CARTE, slug + ".webp")
    if refaire_le_carre:
        car = carre_autour(origine, alpha).resize((900, 900), Image.LANCZOS)
        car.save(fc, "WEBP", quality=82, method=6)
        etat = "carte %3d Ko 900x900" % (os.path.getsize(fc) // 1024)
    else:
        etat = "carte GELEE, laissee telle quelle"

    if not faire_le_heros:
        print("%-12s %s   (héros : voir _damier.py)" % (slug, etat))
        return

    # 2. le héros : détouré, RGBA
    det = decoupe.crop(alpha.getbbox())
    det.thumbnail((1200, 1200), Image.LANCZOS)
    fp = os.path.join(PLATS, slug + ".webp")
    det.save(fp, "WEBP", quality=94, alpha_quality=100, exact=True)

    print("%-12s %s   héros %3d Ko %dx%d"
          % (slug, etat, os.path.getsize(fp) // 1024, det.width, det.height))


def main():
    # ⚠️ UNE PHOTO, UN PROCESSUS. Ce script gardait une seule session rembg
    # pour tout le lot : il mourait en **code 137 (tué faute de mémoire)** dès
    # la DEUXIÈME photo, après avoir écrit la première sans se plaindre. On
    # croyait donc que le lot était passé, alors qu'une seule image l'était.
    # Trouvé le 2026-08-26 en régénérant le krinkrin ; c'est la même fuite
    # d'onnxruntime que celle notée chez Hillary le 2026-08-20. Le seul
    # remède qui tienne est de rendre la mémoire au système : on ressort.
    for slug, fichier, faire_le_heros, refaire in PHOTOS:
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--une",
                            slug, fichier, "1" if faire_le_heros else "0",
                            "1" if refaire else "0"])
        if r.returncode != 0:
            sys.exit("⛔ %s : le détourage s'est arrêté (code %d)%s"
                     % (slug, r.returncode,
                        " — tué faute de mémoire" if r.returncode == 137 else ""))

    print("\n⚠️ REGARDER LE DÉTOURAGE SUR FOND CRÈME (#ede9e3), jamais sur du blanc :")
    print("   un halo clair ne se voit que sur le fond où l'image sera posée.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--une":
        une(sys.argv[2], sys.argv[3], sys.argv[4] == "1", sys.argv[5] == "1")
    else:
        main()

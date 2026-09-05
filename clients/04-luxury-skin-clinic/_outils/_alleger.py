# -*- coding: utf-8 -*-
"""
_alleger.py — ramène les photos produits au gabarit de la maison.

    python _outils/_alleger.py --simuler     # dit ce qu'il ferait, ne touche rien
    python _outils/_alleger.py               # allège

⚠️ POURQUOI. Mesuré sur le site en ligne le 2026-09-05 : la page INA Luxury
   pèse **1,5 Mo**, dont 1,45 Mo d'images. Vingt-quatre photos sortent en
   1179 px de large (l'export brut d'un téléphone) et pèsent jusqu'à 350 Ko,
   quand les vingt-cinq autres — passées par la normalisation de mai — font
   28 Ko en moyenne. Sur la 3G de Cotonou, c'est la différence entre une page
   qui s'ouvre et une page qu'on abandonne.

⚠️ LA CARTE FAIT 330 px DE LARGE. À deux fois la densité d'un écran de
   téléphone, 700 px suffisent : au-delà, on télécharge des pixels que
   personne ne verra jamais.

⛔ CE SONT LES VRAIES PHOTOS DE GLORIA. On ne recadre pas, on ne retouche pas :
   on redimensionne et on ré-encode, rien d'autre. Les originaux restent dans
   git — un `git checkout` les rend intacts.
"""
import argparse, io, os, sys, glob
from PIL import Image

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIERS = ["assets/images/ina-luxury", "assets/images/cozy"]
LARGEUR_MAX = 700      # la carte fait 330 px : 700 couvre les ecrans a double densite
QUALITE = 80
SEUIL_KO = 60          # en dessous, la photo est deja au gabarit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simuler", action="store_true")
    a = ap.parse_args()

    avant = apres = 0
    faits = 0
    for d in DOSSIERS:
        base = os.path.join(RACINE, d.replace("/", os.sep))
        if not os.path.isdir(base):
            continue
        for p in sorted(glob.glob(os.path.join(base, "**", "*.jpg"), recursive=True)):
            ko = os.path.getsize(p) / 1024.0
            if ko <= SEUIL_KO:
                continue
            im = Image.open(p)
            L, H = im.size
            if L > LARGEUR_MAX:
                H = int(round(H * LARGEUR_MAX / L))
                L = LARGEUR_MAX
            if a.simuler:
                # on encode en memoire pour annoncer un vrai chiffre
                t = io.BytesIO()
                im.convert("RGB").resize((L, H), Image.LANCZOS).save(t, "JPEG", quality=QUALITE, optimize=True)
                neuf = t.tell() / 1024.0
            else:
                im.convert("RGB").resize((L, H), Image.LANCZOS).save(
                    p, "JPEG", quality=QUALITE, optimize=True, progressive=True)
                neuf = os.path.getsize(p) / 1024.0
            print("  %6.0f -> %5.0f Ko  %-11s %s"
                  % (ko, neuf, "%dx%d" % (L, H), os.path.relpath(p, RACINE).replace("\\", "/")))
            avant += ko
            apres += neuf
            faits += 1

    if not faits:
        print("  rien a alleger : tout est deja au gabarit.")
        return
    print("  %s : %d photos, %.0f Ko -> %.0f Ko (%.0f %% de moins)"
          % ("SIMULATION" if a.simuler else "fait", faits, avant, apres,
             100 * (1 - apres / max(avant, 1))))
    if a.simuler:
        print("  relancer sans --simuler pour appliquer.")
    else:
        print("  ⚠️ REGARDER deux ou trois photos avant de deployer.")


if __name__ == "__main__":
    main()

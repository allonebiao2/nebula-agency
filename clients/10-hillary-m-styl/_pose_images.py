#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HILLARY M. STYL — met les images retenues au format du web.

    python _pose_images.py

Lit `_sources/ia/*.png`, écrit `assets/images/*.webp`. Ré-exécutable.

⚠️ POURQUOI LE SITE PASSE EN MULTI-FICHIERS
La vitrine était un fichier unique, logo et favicon en base64. C'était tenable
pour 2 images de 6 Ko. Avec 19 photos, le base64 ferait grimper le HTML à plus
de 6 Mo : illisible, non cachable, et impossible à charger en 4G.

Les photos vivent donc dans `assets/images/` et sont référencées en relatif.
Le logo et le favicon restent en base64 (ils sont petits et évitent deux
requêtes au premier rendu).

⛔ CE QUI N'EST PAS ICI : les photos du catalogue commandable (`PIECES`). Elles
   portent un prix et un bouton de commande. Une image générée n'y entre pas.
"""
import os, sys
from PIL import Image

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RACINE = os.path.dirname(os.path.abspath(__file__))
IA = os.path.join(RACINE, "_sources", "ia")
OUT = os.path.join(RACINE, "assets", "images")

# (source, sortie, largeur, qualité)
LOT = [
    # le héros — fond blanc uni, c'est lui qui porte l'effet du numéro géant
    ("hero-1", "hero-1.webp", 1000, 80),
    ("hero-2", "hero-2.webp", 1000, 80),
    ("hero-3", "hero-3.webp", 1000, 80),
    ("hero-4", "hero-4.webp", 1000, 80),
    # l'atelier — trois plans rapprochés
    ("atelier-1", "atelier-1.webp", 860, 78),
    ("atelier-2", "atelier-2.webp", 860, 78),
    ("atelier-3", "atelier-3.webp", 860, 78),
    # le lookbook — affiché en noir et blanc, couleurs au survol
    ("look-1", "look-1.webp", 1000, 78),
    ("look-2", "look-2.webp", 900, 78),
    ("look-3", "look-3.webp", 900, 78),
    ("look-4", "look-4.webp", 1000, 78),
    ("look-5", "look-5.webp", 1100, 76),
    ("look-6", "look-6.webp", 900, 78),
    # le carrousel des collections — sans prix, sans bouton de commande
    ("coll-1", "coll-1.webp", 820, 80),
    ("coll-2", "coll-2.webp", 820, 80),
    ("coll-3", "coll-3.webp", 820, 80),
    ("coll-4", "coll-4.webp", 820, 80),
    ("coll-5", "coll-5.webp", 820, 80),
    ("coll-6", "coll-6.webp", 820, 80),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    total, n = 0, 0
    print("HILLARY M. STYL — mise au web des images\n")
    for src, dst, larg, q in LOT:
        s = os.path.join(IA, src + ".png")
        if not os.path.exists(s):
            print(f"  [KO] {src}.png introuvable")
            continue
        im = Image.open(s).convert("RGB")
        if im.width > larg:
            im = im.resize((larg, round(im.height * larg / im.width)), Image.LANCZOS)
        p = os.path.join(OUT, dst)
        im.save(p, "WEBP", quality=q, method=6)
        k = os.path.getsize(p) // 1024
        total += k; n += 1
        print(f"  {dst:<16} {im.width:>5}px  {k:>4} Ko" + ("   ⚠️ lourd" if k > 260 else ""))
    print(f"\n  {n} images · {total} Ko au total ({total/1024:.1f} Mo)")
    if total > 3000:
        print("  ⚠️ au-dessus de 3 Mo : réduire la qualité avant de déployer")
    return 0


if __name__ == "__main__":
    sys.exit(main())

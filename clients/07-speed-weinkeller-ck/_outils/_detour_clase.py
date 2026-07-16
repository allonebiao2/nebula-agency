#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-détourage de la NOUVELLE Clase Azul Reposado (« corrigé », bouteille complète)
-> remplace assets/images/cave/clase-azul-reposado.webp. Même pipeline que _build_whisky.py.
Le fichier source a un DAMIER collé en fond : rembg (isnet) isole la bouteille quand même.
Produit aussi un QC (mi-clair / mi-sombre) pour vérifier qu'il ne reste pas de damier."""
import os
from PIL import Image, ImageFilter
from rembg import remove, new_session

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, "assets", "images", "gallery", "Catégorie TEQUILA",
                    "Clase Azul Reposado Prix _ 250.000 FCFA corrigé.PNG")
OUT  = os.path.join(ROOT, "assets", "images", "cave", "clase-azul-reposado.webp")
QC   = os.path.join(ROOT, "_clase_qc.png")
NH = 1100
session = new_session("isnet-general-use")

def cut_ai(path):
    im = Image.open(path).convert("RGB")
    out = remove(im, session=session, post_process_mask=True)
    a = out.split()[3].filter(ImageFilter.GaussianBlur(0.5))
    out.putalpha(a)
    bbox = out.split()[3].getbbox()
    if bbox:
        out = out.crop(bbox)
    W, H = out.size
    nw = max(1, round(W * NH / H))
    return out.resize((nw, NH), Image.LANCZOS)

im = cut_ai(SRC)
im.save(OUT, quality=90, method=6)
print("OK  clase-azul-reposado.webp  %dx%d  <- corrigé" % im.size)

# QC : bouteille sur moitié claire / moitié sombre
w, h = im.size
pad = 40
sheet = Image.new("RGB", (w + 2 * pad, h + 2 * pad), (239, 234, 227))
from PIL import ImageDraw
ImageDraw.Draw(sheet).rectangle([(w + 2 * pad) // 2, 0, w + 2 * pad, h + 2 * pad], fill=(18, 16, 14))
sheet.paste(im, (pad, pad), im)
sheet.save(QC, quality=92)
print("QC:", QC)

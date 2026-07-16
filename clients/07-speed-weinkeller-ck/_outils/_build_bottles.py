#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Détoure les photos champagnes (fond blanc -> transparent) pour le monde Weinkeller.
Flood-fill depuis les bords (ne touche pas l'intérieur) + nettoyage du liseré, crop, resize, webp."""
import os, glob
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, "assets", "images", "Wenkeller")
OUT  = os.path.join(ROOT, "assets", "images", "cave")
os.makedirs(OUT, exist_ok=True)

# substring trouvé dans le nom de fichier -> (slug, marque, détail, prix FCFA)
CATALOG = [
 ("Ruinart Blanc de Blancs", "ruinart-blanc-de-blancs", "Ruinart", "Blanc de Blancs · 75 CL · étui", "80 000"),
 ("Ruinart Brut Ros",        "ruinart-brut-rose",       "Ruinart", "Brut Rosé · 75 CL",               "80 000"),
 ("R de Ruinart",            "ruinart-r",               "Ruinart", "R de Ruinart · 75 CL · étui",     "60 000"),
 ("Veuve Clicquot",          "veuve-clicquot",          "Veuve Clicquot", "Brut · 75 CL",             "60 000"),
 ("Ice Imp",                 "moet-ice",                "Moët & Chandon", "Ice Impérial · 75 CL",     "55 000"),
 ("Nicolas Feuillatte",      "nicolas-feuillatte",      "Nicolas Feuillatte", "Cuvée Spéciale · Blanc de Blancs", "50 000"),
 ("Lanson Black Label",      "lanson-black-label",      "Lanson", "Black Label · 75 CL · étui",       "45 000"),
 ("Brut Imp",                "moet-brut-imperial",      "Moët & Chandon", "Brut Impérial · 75 CL",    "45 000"),
]

def find(sub):
    for f in glob.glob(os.path.join(SRC, "*.png")):
        if sub.lower() in os.path.basename(f).lower() and "(1)" not in f:
            return f
    return None

def cutout(path, tol=26):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    SENT = (255, 0, 255)
    seeds = [(1,1),(w-2,1),(1,h-2),(w-2,h-2),(w//2,1),(w//2,h-2),(1,h//2),(w-2,h//2)]
    for s in seeds:
        try: ImageDraw.floodfill(im, s, SENT, thresh=tol)
        except Exception: pass
    arr = np.array(im)
    sent = (arr[:,:,0] > 250) & (arr[:,:,1] < 8) & (arr[:,:,2] > 250)
    alpha = np.where(sent, 0, 255).astype("uint8")
    a = Image.fromarray(alpha, "L")
    a = a.filter(ImageFilter.MinFilter(3))          # érode 1px -> tue le liseré blanc
    a = a.filter(ImageFilter.GaussianBlur(0.6))     # adoucit le bord
    out = im.convert("RGBA"); out.putalpha(a)
    bbox = a.getbbox()
    if bbox: out = out.crop(bbox)
    W, H = out.size; nh = 820; nw = max(1, round(W*nh/H))
    return out.resize((nw, nh), Image.LANCZOS)

if __name__ == "__main__":
    done = []
    for sub, slug, brand, detail, price in CATALOG:
        f = find(sub)
        if not f:
            print("MANQUE:", sub); continue
        cutout(f).save(os.path.join(OUT, slug + ".webp"), quality=84, method=6)
        done.append(slug)
        print("OK", slug, "<-", os.path.basename(f))
    print("== %d bouteilles détourées ==" % len(done))

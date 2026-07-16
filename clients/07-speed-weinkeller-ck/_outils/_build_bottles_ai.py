#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Détourage haute qualité des 21 bouteilles (hauteur 1100 px, webp q92).
- rembg (isnet-general-use) pour 20 bouteilles : bords IA propres.
- Clase Azul (céramique blanc-sur-blanc) : flood-fill silhouette + nettoyage,
  car rembg découpe la 'taille' blanche sans motif."""
import os, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from rembg import remove, new_session
from scipy.ndimage import binary_fill_holes, binary_erosion, binary_opening, label

ROOT = os.path.dirname(os.path.abspath(__file__))
WEN = os.path.join(ROOT, "assets", "images", "Wenkeller")
GAL = os.path.join(ROOT, "assets", "images", "gallery")
TEQ = os.path.join(GAL, "Catégorie TEQUILA")
OUT = os.path.join(ROOT, "assets", "images", "cave")
os.makedirs(OUT, exist_ok=True)
session = new_session("isnet-general-use")
NH = 1100

# (dossier, sous-chaîne, slug, méthode, pré-crop)
JOBS = [
    (WEN, "Ruinart Blanc de Blancs", "ruinart-blanc-de-blancs", "ai",   None),
    (WEN, "Ruinart Brut Ros",        "ruinart-brut-rose",       "ai",   None),
    (WEN, "R de Ruinart",            "ruinart-r",               "ai",   None),
    (WEN, "Veuve Clicquot",          "veuve-clicquot",          "ai",   None),
    (WEN, "Ice Imp",                 "moet-ice",                "ai",   None),
    (WEN, "Nicolas Feuillatte",      "nicolas-feuillatte",      "ai",   None),
    (WEN, "Lanson Black Label",      "lanson-black-label",      "ai",   None),
    (WEN, "Brut Imp",                "moet-brut-imperial",      "ai",   None),
    (GAL, "DELAGNE",                 "delagne-grande-cuvee",    "ai",   None),
    (GAL, "Dom P",                   "dom-perignon-2015",       "ai",   None),
    (GAL, "Ruinart R Mill",          "ruinart-r-magnum",        "ai",   None),
    (GAL, "Grande Dame 2012",        "grande-dame-2012",        "ai",   None),
    (GAL, "Grande Dame 2015",        "grande-dame-2015",        "ai",   None),
    (TEQ, "Clase Azul",              "clase-azul-reposado",     "ff",   (0.52, 0.0, 1.0, 1.0)),
    (TEQ, "Reposado 1942",           "don-julio-1942",          "ai",   None),
    (TEQ, "70 Cristalino",           "don-julio-70",            "ai",   None),
    (TEQ, "AGAVE 70CL",              "don-julio-anejo",         "ai",   None),
    (TEQ, "Casamigos - Anejo",       "casamigos-anejo",         "ai",   None),
    (TEQ, "Casamigos - Blanco",      "casamigos-blanco",        "ai",   None),
    (TEQ, "Patron Anejo",            "patron-anejo",            "ai",   None),
    (TEQ, "patrón silver",           "patron-silver",           "ai",   None),
]

def find(folder, sub):
    for f in sorted(glob.glob(os.path.join(folder, "*"))):
        if os.path.isfile(f) and sub.lower() in os.path.basename(f).lower() and "(1)" not in f:
            return f
    return None

def fit(res):
    bbox = res.split()[3].getbbox()
    if bbox: res = res.crop(bbox)
    W, H = res.size; nw = max(1, round(W * NH / H))
    return res.resize((nw, NH), Image.LANCZOS)

def cut_ai(path, crop):
    im = Image.open(path).convert("RGB")
    if crop:
        w, h = im.size; im = im.crop((int(w*crop[0]), int(h*crop[1]), int(w*crop[2]), int(h*crop[3])))
    out = remove(im, session=session, post_process_mask=True)
    a = out.split()[3].filter(ImageFilter.GaussianBlur(0.5)); out.putalpha(a)
    return fit(out)

def cut_ff(path, crop):
    base = Image.open(path).convert("RGB")
    w, h = base.size
    box = (int(w*crop[0]), int(h*crop[1]), int(w*crop[2]), int(h*crop[3]))
    im = base.crop(box)
    w, h = im.size
    seeds = []
    for fx in (0.02,0.1,0.3,0.5,0.7,0.9,0.98): seeds += [(int(w*fx),1),(int(w*fx),h-2)]
    for fy in (0.02,0.2,0.4,0.6,0.8,0.98):     seeds += [(1,int(h*fy)),(w-2,int(h*fy))]
    for s in seeds:
        try: ImageDraw.floodfill(im, s, (255,0,255), thresh=12)
        except Exception: pass
    arr = np.array(im); R=arr[:,:,0].astype(int); G=arr[:,:,1].astype(int); Bc=arr[:,:,2].astype(int)
    sent = (R>140)&(Bc>140)&(G<R-50)&(G<Bc-50)
    m = binary_fill_holes(~sent)
    lab, n = label(m)
    if n > 1:
        sz = np.bincount(lab.ravel()); sz[0] = 0; m = lab == sz.argmax()
    m = binary_opening(m, structure=np.ones((3,3)))
    m = binary_erosion(m, structure=np.ones((3,3)), iterations=2)
    a = Image.fromarray((m*255).astype("uint8")).filter(ImageFilter.GaussianBlur(1.0))
    res = base.crop(box).convert("RGBA"); res.putalpha(a)
    return fit(res)

if __name__ == "__main__":
    ok, miss = 0, []
    for folder, sub, slug, meth, crop in JOBS:
        f = find(folder, sub)
        if not f:
            print("MANQUE:", sub); miss.append(sub); continue
        try:
            (cut_ff(f, crop) if meth == "ff" else cut_ai(f, crop)).save(os.path.join(OUT, slug + ".webp"), quality=88, method=6)
            ok += 1; print(f"OK [{meth}] {slug:24s} <- {os.path.basename(f)[:36]}")
        except Exception as e:
            print("ERR", slug, e); miss.append(slug)
    print(f"== {ok}/{len(JOBS)} ==", ("MANQUE: "+",".join(miss)) if miss else "")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Détoure les NOUVELLES bouteilles (champagnes + tequilas) fond clair -> transparent.
Flood-fill multi-graines depuis les bords (préserve l'intérieur), tolérance par image,
pré-crop optionnel (Clase Azul = retire le coffret), érosion liseré, crop bbox, resize, webp."""
import os, glob
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
GAL  = os.path.join(ROOT, "assets", "images", "gallery")
TEQ  = os.path.join(GAL, "Catégorie TEQUILA")
OUT  = os.path.join(ROOT, "assets", "images", "cave")
os.makedirs(OUT, exist_ok=True)

# (dossier, sous-chaîne nom, slug, tolérance, pré-crop (l,t,r,b en fractions) ou None)
JOBS = [
    # --- Champagnes (bouteilles sombres -> facile) ---
    (GAL, "DELAGNE",                 "delagne-grande-cuvee", 32, None),
    (GAL, "Dom P",                   "dom-perignon-2015",    32, None),
    (GAL, "Ruinart R Mill",          "ruinart-r-magnum",     32, None),
    (GAL, "Grande Dame 2012",        "grande-dame-2012",     32, None),
    (GAL, "Grande Dame 2015",        "grande-dame-2015",     32, None),
    # --- Tequilas ---
    (TEQ, "Clase Azul",              "clase-azul-reposado",  14, (0.535, 0.0, 0.995, 1.0)),  # retire le coffret (gauche)
    (TEQ, "Reposado 1942",           "don-julio-1942",       34, None),                    # bouteille très sombre
    (TEQ, "70 Cristalino",           "don-julio-70",         18, None),
    (TEQ, "AGAVE 70CL",              "don-julio-anejo",      30, None),                    # ambre foncé
    (TEQ, "Casamigos - Anejo",       "casamigos-anejo",      22, None),                    # ambre
    (TEQ, "Casamigos - Blanco",      "casamigos-blanco",     15, None),                    # verre transparent
    (TEQ, "Patron Anejo",            "patron-anejo",         22, None),                    # ambre
    (TEQ, "patrón silver",           "patron-silver",        15, None),                    # verre transparent
]

def find(folder, sub):
    for f in sorted(glob.glob(os.path.join(folder, "*"))):
        if os.path.isfile(f) and sub.lower() in os.path.basename(f).lower() and "(1)" not in f:
            return f
    return None

def cutout(path, tol, crop):
    im = Image.open(path).convert("RGB")
    if crop:
        w, h = im.size
        im = im.crop((int(w*crop[0]), int(h*crop[1]), int(w*crop[2]), int(h*crop[3])))
    w, h = im.size
    SENT = (255, 0, 255)
    # graines denses le long des 4 bords
    seeds = []
    for fx in (0.02, 0.12, 0.3, 0.5, 0.7, 0.88, 0.98):
        seeds += [(int(w*fx), 1), (int(w*fx), h-2)]
    for fy in (0.02, 0.15, 0.35, 0.5, 0.65, 0.85, 0.98):
        seeds += [(1, int(h*fy)), (w-2, int(h*fy))]
    for s in seeds:
        try: ImageDraw.floodfill(im, s, SENT, thresh=tol)
        except Exception: pass
    arr = np.array(im)
    R = arr[:, :, 0].astype(int); G = arr[:, :, 1].astype(int); B = arr[:, :, 2].astype(int)
    # magenta sentinelle + sa frange anti-crénelée (R&B hauts, G bas) — n'attrape PAS le bleu (R bas)
    sent = (R > 140) & (B > 140) & (G < R - 50) & (G < B - 50)
    alpha = np.where(sent, 0, 255).astype("uint8")
    a = Image.fromarray(alpha, "L")
    a = a.filter(ImageFilter.MaxFilter(3))          # bouche les micro-trous dans le sujet
    a = a.filter(ImageFilter.MinFilter(3))          # érode 1px -> tue le liseré clair
    a = a.filter(ImageFilter.GaussianBlur(0.6))     # adoucit le bord
    out = im.convert("RGBA"); out.putalpha(a)
    bbox = a.getbbox()
    if bbox: out = out.crop(bbox)
    W, H = out.size
    nh = 820; nw = max(1, round(W * nh / H))
    return out.resize((nw, nh), Image.LANCZOS)

if __name__ == "__main__":
    ok, miss = 0, []
    for folder, sub, slug, tol, crop in JOBS:
        f = find(folder, sub)
        if not f:
            print("MANQUE:", sub); miss.append(sub); continue
        try:
            cutout(f, tol, crop).save(os.path.join(OUT, slug + ".webp"), quality=86, method=6)
            # alpha coverage stat
            print(f"OK  {slug:24s} <- {os.path.basename(f)[:40]}")
            ok += 1
        except Exception as e:
            print("ERR", slug, e); miss.append(slug)
    print(f"== {ok}/{len(JOBS)} détourées ==", "MANQUE:" + ",".join(miss) if miss else "")

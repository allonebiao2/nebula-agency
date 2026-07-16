#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Détourage haute qualité des bouteilles « Les whisky » du client Ck
(4 single malts + 6 cognacs + 1 rhum) : fond clair -> transparent.
Même pipeline que _build_bottles_ai.py : rembg (isnet-general-use), hauteur 1100 px, webp q90.
Génère aussi une planche de contrôle (fond mi-clair / mi-sombre) pour vérifier le détourage."""
import os, glob
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from rembg import remove, new_session

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, "assets", "images", "gallery", "Les whisky_")
OUT  = os.path.join(ROOT, "assets", "images", "cave")
QC   = os.path.join(ROOT, "_whisky_qc.png")
os.makedirs(OUT, exist_ok=True)
session = new_session("isnet-general-use")
NH = 1100

# (sous-chaîne unique du nom de fichier, slug de sortie)
JOBS = [
    ("aberlour",              "aberlour-14"),
    ("benriach",              "benriach-10"),
    ("lagavulin 16",          "lagavulin-16"),
    ("distillers",            "lagavulin-distillers"),
    ("hennessy v.s.o.p",      "hennessy-vsop"),
    ("hennessy very special", "hennessy-vs"),
    ("martin",                "remy-martin-vsop"),
    ("martell vs 1",          "martell-vs"),
    ("martell vsop",          "martell-vsop"),
    ("camus",                 "camus-vs"),
    ("eminente",              "eminente-reserva"),
]

def find(sub):
    for f in sorted(glob.glob(os.path.join(SRC, "*"))):
        if os.path.isfile(f) and sub in os.path.basename(f).lower() and "(1)" not in f:
            return f
    return None

def cut_ai(path):
    im = Image.open(path).convert("RGB")
    out = remove(im, session=session, post_process_mask=True)   # RGBA, bords IA propres
    a = out.split()[3].filter(ImageFilter.GaussianBlur(0.5))     # adoucit le bord
    out.putalpha(a)
    bbox = out.split()[3].getbbox()
    if bbox:
        out = out.crop(bbox)
    W, H = out.size
    nw = max(1, round(W * NH / H))
    return out.resize((nw, NH), Image.LANCZOS)

def contact_sheet(items):
    """items = list of (slug, RGBA). Chaque vignette : moitié gauche claire, moitié droite sombre."""
    cols, cell, pad, lab = 4, 300, 14, 26
    rows = (len(items) + cols - 1) // cols
    ch = cell + lab
    sheet = Image.new("RGB", (cols * cell, rows * ch), (60, 60, 64))
    d = ImageDraw.Draw(sheet)
    try: font = ImageFont.truetype("arial.ttf", 15)
    except Exception: font = ImageFont.load_default()
    for i, (slug, im) in enumerate(items):
        cx, cy = (i % cols) * cell, (i // cols) * ch
        d.rectangle([cx, cy, cx + cell // 2, cy + cell], fill=(239, 234, 227))       # clair
        d.rectangle([cx + cell // 2, cy, cx + cell, cy + cell], fill=(18, 16, 14))   # sombre
        th = cell - 2 * pad
        tw = max(1, round(im.width * th / im.height))
        thumb = im.resize((tw, th), Image.LANCZOS)
        sheet.paste(thumb, (cx + (cell - tw) // 2, cy + pad), thumb)
        d.rectangle([cx, cy + cell, cx + cell, cy + cell + lab], fill=(30, 30, 33))
        d.text((cx + 8, cy + cell + 5), slug, fill=(230, 210, 170), font=font)
    sheet.save(QC, quality=92)

if __name__ == "__main__":
    ok, miss, thumbs = 0, [], []
    for sub, slug in JOBS:
        f = find(sub)
        if not f:
            print("MANQUE:", sub); miss.append(sub); continue
        try:
            im = cut_ai(f)
            im.save(os.path.join(OUT, slug + ".webp"), quality=90, method=6)
            thumbs.append((slug, im))
            ok += 1
            print("OK  %-22s <- %s" % (slug, os.path.basename(f)[:44]))
        except Exception as e:
            print("ERR", slug, repr(e)); miss.append(slug)
    if thumbs:
        contact_sheet(thumbs)
        print("Planche de contrôle:", QC)
    print("== %d/%d détourées ==" % (ok, len(JOBS)), ("MANQUE: " + ",".join(miss)) if miss else "")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Détourage des NOUVELLES bouteilles (gin, vodka, pastis, martini, rhums, whiskies, apéritifs)
déposées par Ck dans assets/images/gallery/catégorie *. Même pipeline que _build_whisky.py
(rembg isnet -> transparent -> hauteur 1100 -> webp q90). Planche de contrôle _newcave_qc.png."""
import os, glob
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from rembg import remove, new_session

ROOT = os.path.dirname(os.path.abspath(__file__))
GAL  = os.path.join(ROOT, "assets", "images", "gallery")
OUT  = os.path.join(ROOT, "assets", "images", "cave")
QC   = os.path.join(ROOT, "_newcave_qc.png")
os.makedirs(OUT, exist_ok=True)
session = new_session("isnet-general-use")
NH = 1100

# (dossier, sous-chaîne unique du nom, slug de sortie)
JOBS = [
 ("catégorie GIN", "dry gin", "gin-dry"),
 ("catégorie GIN", "hendrick", "hendricks"),
 ("catégorie GIN", "june", "june-gvine"),
 ("catégorie GIN", "whitley", "whitley-neill"),
 ("catégorie RHUM", "bologne", "bologne-reserve"),
 ("catégorie RHUM", "ti ced", "ti-ced"),
 ("catégorie RHUM", "baileys the original", "baileys-original"),
 ("catégorie RHUM", "salted", "baileys-salted"),
 ("catégorie RHUM", "hédone", "hedone"),
 ("catégorie RHUM", "rivière", "riviere-du-mat"),
 ("catégorie VODKA", "roc vodka", "ciroc"),
 ("catégorie PASTIS", "ricard", "ricard"),
 ("catégorie MARTINI", "martini rosso", "martini-rosso"),
 ("catégorie Le WHISKY", "aberlour distillery 10", "aberlour-10"),
 ("catégorie Le WHISKY", "akashi", "akashi-sherry"),
 ("catégorie Le WHISKY", "chivas", "chivas-18"),
 ("catégorie Le WHISKY", "glenfiddich", "glenfiddich-vat01"),
 ("catégorie Le WHISKY", "glen turner", "glen-turner-12"),
 ("catégorie Le WHISKY", "haig", "haig-club"),
 ("catégorie Le WHISKY", "hwayo", "hwayo"),
 ("catégorie Le WHISKY", "daniel", "jack-daniels"),
 ("catégorie Le WHISKY", "germeifter 35", "jagermeister-35"),
 ("catégorie Le WHISKY", "germeifter 70", "jagermeister-70"),
 ("catégorie Le WHISKY", "germeifter 1l", "jagermeister-1l"),
 ("catégorie Le WHISKY", "knockando", "knockando-18"),
 ("catégorie Le WHISKY", "kraken", "kraken"),
 ("catégorie Le WHISKY", "deveron", "the-deveron-10"),
 ("catégorie Le WHISKY", "san-in", "the-san-in"),
]

def find(folder, sub):
    for f in sorted(glob.glob(os.path.join(GAL, folder, "*"))):
        b = os.path.basename(f).lower()
        if os.path.isfile(f) and sub in b and "(1)" not in b and not b.startswith("img_"):
            return f
    return None

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

def contact_sheet(items):
    cols, cell, pad, lab = 5, 260, 12, 24
    rows = (len(items) + cols - 1) // cols
    ch = cell + lab
    sheet = Image.new("RGB", (cols * cell, rows * ch), (60, 60, 64))
    d = ImageDraw.Draw(sheet)
    try: font = ImageFont.truetype("arial.ttf", 13)
    except Exception: font = ImageFont.load_default()
    for i, (slug, im) in enumerate(items):
        cx, cy = (i % cols) * cell, (i // cols) * ch
        d.rectangle([cx, cy, cx + cell // 2, cy + cell], fill=(239, 234, 227))
        d.rectangle([cx + cell // 2, cy, cx + cell, cy + cell], fill=(18, 16, 14))
        th = cell - 2 * pad
        tw = max(1, round(im.width * th / im.height))
        thumb = im.resize((tw, th), Image.LANCZOS)
        sheet.paste(thumb, (cx + (cell - tw) // 2, cy + pad), thumb)
        d.rectangle([cx, cy + cell, cx + cell, cy + cell + lab], fill=(30, 30, 33))
        d.text((cx + 6, cy + cell + 4), slug, fill=(230, 210, 170), font=font)
    sheet.save(QC, quality=92)

if __name__ == "__main__":
    ok, miss, thumbs = 0, [], []
    for folder, sub, slug in JOBS:
        f = find(folder, sub)
        if not f:
            print("MANQUE:", folder, "/", sub); miss.append(slug); continue
        try:
            im = cut_ai(f)
            im.save(os.path.join(OUT, slug + ".webp"), quality=90, method=6)
            thumbs.append((slug, im)); ok += 1
            print("OK  %-20s <- %s" % (slug, os.path.basename(f)[:40]))
        except Exception as e:
            print("ERR", slug, repr(e)); miss.append(slug)
    if thumbs:
        contact_sheet(thumbs); print("QC:", QC)
    print("== %d/%d détourées ==" % (ok, len(JOBS)), ("MANQUE: " + ",".join(miss)) if miss else "")

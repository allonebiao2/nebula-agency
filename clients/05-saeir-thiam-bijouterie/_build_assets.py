#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline d'assets — Djambar Team / Saeir Thiam Bijouterie
Ré-exécutable : quand le client envoie de nouvelles photos, relancer ce script.

  python _build_assets.py

Produit dans assets/images/ :
  - logo-full-dark.png / logo-full-white.png   (logo complet, détouré, web)
  - logo-mark-dark.png / logo-mark-white.png   (arbre seul, pour la nav)
  - favicon-32.png / apple-touch-icon.png       (icônes onglet)
  - og-djambar.jpg / og-bijouterie.jpg          (images de partage social 1200x630)
  - gallery/<cat>/gN.jpg                         (photos optimisées par catégorie)
"""
import os
from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG  = os.path.join(ROOT, "assets", "images")

NAVY = (7, 20, 46)
GOLD = (201, 162, 75)
GOLD_SOFT = (231, 214, 163)
WHITE = (255, 255, 255)

def trim(im):
    """Recadre sur le contenu non transparent."""
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    bbox = im.split()[3].getbbox()
    return im.crop(bbox) if bbox else im

def load_font(names, size):
    for n in names:
        for base in (r"C:\Windows\Fonts", "/usr/share/fonts"):
            p = os.path.join(base, n)
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
    try:
        return ImageFont.truetype(names[0], size)
    except Exception:
        return ImageFont.load_default()

# ---------------------------------------------------------------- LOGOS
def process_logos():
    dark = trim(Image.open(os.path.join(IMG, "Logo", "1000000104.png")).convert("RGBA"))
    white = trim(Image.open(os.path.join(IMG, "Logo", "1000000103.png")).convert("RGBA"))

    # logo complet (web, max 600px)
    for im, name in ((dark, "logo-full-dark.png"), (white, "logo-full-white.png")):
        o = im.copy(); o.thumbnail((600, 600), Image.LANCZOS)
        o.save(os.path.join(IMG, name)); print("ok", name, o.size)

    # marque = arbre seul (on coupe le texte « DJAMBAR TEAM » du bas ~30%)
    def mark(im, name, px=240):
        w, h = im.size
        top = trim(im.crop((0, 0, w, int(h * 0.70))))
        top.thumbnail((px, px), Image.LANCZOS)
        top.save(os.path.join(IMG, name)); print("ok", name, top.size)
        return top
    mark_dark = mark(dark, "logo-mark-dark.png")
    mark_white = mark(white, "logo-mark-white.png")

    # favicon : arbre blanc sur carré navy arrondi
    def icon(size, fname):
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        r = int(size * 0.22)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, size, size], radius=r, fill=255)
        bg = Image.new("RGBA", (size, size), NAVY + (255,))
        canvas.paste(bg, (0, 0), mask)
        m = mark_white.copy(); pad = int(size * 0.16)
        m.thumbnail((size - 2 * pad, size - 2 * pad), Image.LANCZOS)
        canvas.alpha_composite(m, ((size - m.size[0]) // 2, (size - m.size[1]) // 2))
        canvas.save(os.path.join(IMG, fname)); print("ok", fname, (size, size))
    icon(64, "favicon-32.png")
    icon(180, "apple-touch-icon.png")
    return mark_white

# ---------------------------------------------------------------- OG IMAGES
def process_og(mark_white):
    serif = load_font(["georgiab.ttf", "Georgia.ttf", "timesbd.ttf"], 86)
    serif_sm = load_font(["georgia.ttf", "times.ttf"], 40)
    sans = load_font(["arial.ttf", "Arial.ttf"], 30)

    def og(fname, title, subtitle, kicker):
        W, H = 1200, 630
        im = Image.new("RGB", (W, H), NAVY)
        d = ImageDraw.Draw(im)
        # halo discret
        for i, col in enumerate([(13, 34, 79), (10, 26, 60)]):
            d.ellipse([W - 520 + i*60, -260 + i*40, W + 220, 360], fill=col)
        # logo en haut à gauche
        m = mark_white.copy(); m.thumbnail((120, 120), Image.LANCZOS)
        im.paste(m, (80, 70), m)
        # kicker or
        d.text((210, 96), kicker, font=sans, fill=GOLD_SOFT)
        # titre
        d.text((80, 250), title, font=serif, fill=WHITE)
        # sous-titre
        d.text((84, 360), subtitle, font=serif_sm, fill=(185, 198, 226))
        # filet or
        d.rectangle([84, 440, 148, 444], fill=GOLD)
        # pied
        d.text((84, 540), "Cotonou, Benin  -  wa.me/2290197967671", font=sans, fill=(150, 165, 195))
        im.save(os.path.join(IMG, fname), quality=88, optimize=True)
        print("ok", fname)

    og("og-djambar.jpg", "Djambar Team", "L'excellence, sous toutes ses formes.", "GROUPE DJAMBAR TEAM")
    og("og-bijouterie.jpg", "Saeir Thiam Bijouterie", "L'elegance dans chaque detail.", "DJAMBAR TEAM  -  LE BIJOUTIER")

# ---------------------------------------------------------------- GALLERY
def pick(files, k):
    """Sélection régulièrement espacée pour de la variété."""
    files = sorted(files)
    if len(files) <= k:
        return files
    step = len(files) / k
    return [files[int(i * step)] for i in range(k)]

def process_gallery():
    cats = [
        ("Colliers", "colliers", 8),
        ("Bracelet", "bracelets", 8),
        ("Bague D'alliance en Or et Argent", "bagues", 8),
    ]
    manifest = {}
    for src_name, out_name, k in cats:
        src = os.path.join(IMG, src_name)
        out = os.path.join(IMG, "gallery", out_name)
        os.makedirs(out, exist_ok=True)
        files = [f for f in os.listdir(src)
                 if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
        chosen = pick(files, k)
        names = []
        for i, f in enumerate(chosen, 1):
            im = Image.open(os.path.join(src, f))
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((1080, 1080), Image.LANCZOS)
            outf = f"g{i}.jpg"
            im.save(os.path.join(out, outf), quality=82, optimize=True, progressive=True)
            names.append(outf)
        manifest[out_name] = names
        print(f"ok gallery/{out_name}: {len(names)} images")
    return manifest

if __name__ == "__main__":
    mw = process_logos()
    process_og(mw)
    man = process_gallery()
    print("MANIFEST", man)

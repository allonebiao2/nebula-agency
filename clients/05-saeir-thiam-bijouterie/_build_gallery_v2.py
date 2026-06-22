#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Art-direction de la galerie — Djambar Team / Saeir Thiam (thème sombre luxe)
Curate + grade unifié (vers le nuit) + vignette → cohérence "shoot commandé".
Watermarks du client CONSERVÉS (branding anti-vol).
  python _build_gallery_v2.py
"""
import os
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFilter, ImageChops

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, "assets", "images")
NAVY = (10, 24, 58)

# curatage : index (= ordre alphabétique) des meilleures sources, g1..g8
CURATION = {
    "Colliers": {"out": "colliers", "pick": [0, 5, 4, 3, 11, 10, 7, 13]},
    "Bracelet": {"out": "bracelets", "pick": [12, 1, 20, 13, 0, 17, 18, 21]},
    "Bague D'alliance en Or et Argent": {"out": "bagues", "pick": [17, 4, 6, 13, 19, 22, 24, 29]},
}

def vignette(im, strength=0.42, radius=1.18):
    """Assombrit les bords (multiply avec un radial) → focus sur le centre."""
    w, h = im.size
    # masque radial : blanc au centre -> gris foncé aux bords
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([-w*(radius-1), -h*(radius-1), w*radius, h*radius], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(min(w, h)*0.16))
    dark = ImageEnhance.Brightness(im).enhance(1 - strength)
    return Image.composite(im, dark, mask)

def grade(im):
    im = ImageOps.exif_transpose(im).convert("RGB")
    # crop carré centré
    w, h = im.size; s = min(w, h)
    im = im.crop(((w-s)//2, (h-s)//2, (w-s)//2+s, (h-s)//2+s))
    im = im.resize((1080, 1080), Image.LANCZOS)
    # punch léger + grade
    im = ImageOps.autocontrast(im, cutoff=0.4)
    im = ImageEnhance.Contrast(im).enhance(1.07)
    im = ImageEnhance.Brightness(im).enhance(0.93)
    im = ImageEnhance.Color(im).enhance(1.04)
    # très léger liant nuit dans les ombres (cohérence du set)
    navy = Image.new("RGB", im.size, NAVY)
    im = ImageChops.blend(im, ImageChops.multiply(im, navy), 0.10)
    im = vignette(im)
    return im

def run():
    for folder, cfg in CURATION.items():
        src = os.path.join(IMG, folder)
        out = os.path.join(IMG, "gallery", cfg["out"])
        os.makedirs(out, exist_ok=True)
        files = sorted(f for f in os.listdir(src)
                       if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
        for n, idx in enumerate(cfg["pick"], 1):
            idx = min(idx, len(files)-1)
            im = grade(Image.open(os.path.join(src, files[idx])))
            im.save(os.path.join(out, f"g{n}.jpg"), quality=84, optimize=True, progressive=True)
        print(f"ok {cfg['out']}: {len(cfg['pick'])} images gradées")

    # Hero (Chadé velours) regradé, cadrage large
    col = os.path.join(IMG, "Colliers")
    cf = sorted(os.listdir(col))
    hero = ImageOps.exif_transpose(Image.open(os.path.join(col, cf[0]))).convert("RGB")
    tw, th = 1500, 1100; w, h = hero.size; sc = max(tw/w, th/h)
    hero = hero.resize((int(w*sc), int(h*sc)), Image.LANCZOS)
    w, h = hero.size; hero = hero.crop(((w-tw)//2, (h-th)//2, (w-tw)//2+tw, (h-th)//2+th))
    hero = ImageEnhance.Brightness(hero).enhance(0.82)
    hero = ImageEnhance.Contrast(hero).enhance(1.06)
    hero = vignette(hero, strength=0.5, radius=1.25)
    hero.save(os.path.join(IMG, "hero-bijou.jpg"), quality=84, optimize=True, progressive=True)
    print("ok hero-bijou.jpg")

if __name__ == "__main__":
    run()

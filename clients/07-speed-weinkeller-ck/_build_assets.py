#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline d'assets — SPEED SHOPPING x WEINKELLER BY CK (client #07).
- Détoure le logo Speed (cercle) -> speed-round.png + favicon + apple-touch
- Compose 3 OG sociales 1200x630 : maison / speed / weinkeller
Ré-exécutable. Pillow requis.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG  = os.path.join(ROOT, "assets", "images")
LOGOS, FAV, OG = (os.path.join(IMG, d) for d in ("logos", "favicon", "og"))
for d in (LOGOS, FAV, OG): os.makedirs(d, exist_ok=True)

WIN = r"C:\Windows\Fonts"
def font(name, size):
    for n in ([name] if isinstance(name, str) else name):
        p = os.path.join(WIN, n)
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()

BLACK_SANS = "ariblk.ttf"           # Arial Black -> display Speed/maison
BOLD_SANS  = "arialbd.ttf"
SERIF_B    = ["georgiab.ttf", "timesbd.ttf"]  # Weinkeller serif
SERIF      = ["georgia.ttf", "times.ttf"]

# ---------- 1) Logo Speed : détourage circulaire ----------
def build_logo():
    src = os.path.join(LOGOS, "speed-logo-src.jpg")
    im = Image.open(src).convert("RGBA")
    g = im.convert("L").point(lambda p: 255 if p > 28 else 0)
    bbox = g.getbbox()
    if bbox: im = im.crop(bbox)
    w, h = im.size; s = max(w, h)
    sq = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    sq.paste(im, ((s - w) // 2, (s - h) // 2)); im = sq
    # masque cercle (léger inset pour gommer le liseré noir résiduel)
    big = s * 4
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse([6, 6, big - 6, big - 6], fill=255)
    mask = mask.resize((s, s), Image.LANCZOS)
    im.putalpha(mask)

    im.resize((512, 512), Image.LANCZOS).save(os.path.join(LOGOS, "speed-round.png"))
    im.resize((32, 32), Image.LANCZOS).save(os.path.join(FAV, "favicon-32.png"))
    # apple-touch : disque sur fond blanc (iOS arrondit lui-même)
    at = Image.new("RGBA", (180, 180), (255, 255, 255, 255))
    disc = im.resize((168, 168), Image.LANCZOS)
    at.paste(disc, (6, 6), disc)
    at.convert("RGB").save(os.path.join(FAV, "apple-touch.png"))
    print("logo + favicons OK")
    return im

# ---------- helpers OG ----------
def lin_grad(size, c0, c1, horiz=True):
    w, h = size; base = Image.new("RGB", size, c0)
    top = Image.new("RGB", size, c1)
    mask = Image.new("L", size)
    md = mask.load()
    for x in range(w):
        for y in range(h):
            md[x, y] = int(255 * (x / w if horiz else y / h))
    base.paste(top, (0, 0), mask); return base

def radial(size, inner, outer, cx=0.5, cy=0.4, r=0.9):
    w, h = size; img = Image.new("RGB", size, outer)
    px = img.load(); R = (max(w, h) * r)
    for y in range(h):
        for x in range(w):
            d = (((x - w*cx)**2 + (y - h*cy)**2) ** .5) / R
            d = min(1, d)
            px[x, y] = tuple(int(inner[i] + (outer[i]-inner[i])*d) for i in range(3))
    return img

def center(draw, xy, text, fnt, fill, anchor="la"):
    draw.text(xy, text, font=fnt, fill=fill, anchor=anchor)

# ---------- 2) OG cards ----------
def og_speed(logo):
    W, H = 1200, 630
    img = lin_grad((W, H), (10, 79, 214), (54, 167, 255))
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(-2, 30):  # lignes de vitesse
        x = i * 70
        d.line([(x, 0), (x - 220, H)], fill=(255, 255, 255, 18), width=10)
    disc = logo.resize((150, 150), Image.LANCZOS)
    img.paste(disc, (84, 70), disc)
    d.text((250, 96), "SPEED SHOPPING", font=font(BOLD_SANS, 40), fill=(255, 255, 255, 230))
    d.text((80, 250), "LA FRANCE", font=font(BLACK_SANS, 120), fill="white")
    d.text((80, 372), "À PORTÉE DE MAIN", font=font(BLACK_SANS, 92), fill=(214, 235, 255))
    d.text((84, 512), "Vos achats en France, livrés chez vous au Bénin.", font=font(BOLD_SANS, 36), fill=(235, 244, 255))
    img.save(os.path.join(OG, "og-speed.png"))
    print("og-speed OK")

def og_wein():
    W, H = 1200, 630
    img = radial((W, H), (44, 18, 14), (8, 5, 4), cx=.62, cy=.34, r=.95)
    d = ImageDraw.Draw(img, "RGBA")
    d.text((600, 150), "WEINKELLER", font=font(SERIF_B, 104), fill=(203, 161, 76), anchor="ma")
    d.text((600, 276), "B Y   C K", font=font(BOLD_SANS, 40), fill=(233, 216, 182), anchor="ma")
    d.line([(470, 350), (730, 350)], fill=(203, 161, 76), width=2)
    d.text((600, 392), "La cave élevée au rang d'art", font=font(SERIF, 40), fill=(233, 216, 182), anchor="ma")
    d.text((600, 470), "Vins · Champagnes · Spiritueux   —   Porto-Novo", font=font(BOLD_SANS, 30), fill=(172, 150, 122), anchor="ma")
    img.save(os.path.join(OG, "og-wein.png"))
    print("og-wein OK")

def og_house(logo):
    W, H = 1200, 630
    left = lin_grad((W, H), (10, 79, 214), (30, 107, 255))
    right = radial((W, H), (40, 16, 13), (7, 4, 3), cx=.5, cy=.4, r=.8)
    img = left.copy()
    # diagonale : colle la moitié droite
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(W*0.58, 0), (W, 0), (W, H), (W*0.42, H)], fill=255)
    img.paste(right, (0, 0), mask)
    d = ImageDraw.Draw(img, "RGBA")
    # éclair doré
    d.line([(W*0.585, -10), (W*0.5, H*0.5), (W*0.42, H+10)], fill=(255, 255, 255, 230), width=8)
    d.line([(W*0.585, -10), (W*0.5, H*0.5), (W*0.42, H+10)], fill=(233, 198, 108, 180), width=3)
    d.text((96, 250), "SPEED", font=font(BLACK_SANS, 92), fill="white")
    d.text((96, 348), "SHOPPING", font=font(BLACK_SANS, 60), fill=(214, 235, 255))
    d.text((1124, 256), "WEINKELLER", font=font(SERIF_B, 54), fill=(203, 161, 76), anchor="ra")
    d.text((1124, 332), "BY CK", font=font(BOLD_SANS, 36), fill=(233, 216, 182), anchor="ra")
    # sceau CK central
    d.ellipse([W/2-58, H/2-58, W/2+58, H/2+58], fill=(10, 12, 22), outline=(255, 255, 255, 120), width=3)
    d.text((W/2, H/2-6), "CK", font=font(SERIF_B, 46), fill=(233, 216, 182), anchor="mm")
    d.text((W/2, H/2+28), "MAISON", font=font(BOLD_SANS, 15), fill=(180, 180, 200), anchor="mm")
    d.text((600, 560), "DEUX UNIVERS · UNE MAISON", font=font(BOLD_SANS, 30), fill=(255, 255, 255, 220), anchor="ma")
    img.save(os.path.join(OG, "og-house.png"))
    print("og-house OK")

if __name__ == "__main__":
    logo = build_logo()
    og_speed(logo); og_wein(); og_house(logo)
    print("== assets terminés ==")

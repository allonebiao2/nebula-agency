#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HH Design — assets de marque (placeholder élégant en attendant le vrai logo).
Favicon + apple-touch (monogramme HH) + OG social 1200x630. Blanc · or · noir.
Ré-exécutable."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FAV = os.path.join(ROOT, "assets", "images", "favicon")
OG  = os.path.join(ROOT, "assets", "images", "og")
for d in (FAV, OG): os.makedirs(d, exist_ok=True)

BG="#FCFCFB"; INK="#141416"; BLACK="#0F0F11"; GOLD="#B0894A"; GOLD_D="#8C6C34"

def font(paths, size):
    for p in paths:
        try: return ImageFont.truetype(p, size)
        except Exception: pass
    return ImageFont.load_default()
SERIF = ["C:/Windows/Fonts/georgia.ttf","georgia.ttf","C:/Windows/Fonts/times.ttf"]
SERIF_B = ["C:/Windows/Fonts/georgiab.ttf","C:/Windows/Fonts/timesbd.ttf"]
SANS = ["C:/Windows/Fonts/arial.ttf","arial.ttf"]

def ctext(d, cx, y, s, f, fill, ls=0):
    # texte centré avec letter-spacing
    ws=[d.textlength(ch,font=f) for ch in s]
    total=sum(ws)+ls*(len(s)-1)
    x=cx-total/2
    for ch,w in zip(s,ws):
        d.text((x,y), ch, font=f, fill=fill); x+=w+ls
    return total

# ---------- Favicon / apple-touch (monogramme HH sur fond noir + accent or) ----------
def monogram(size):
    im=Image.new("RGB",(size,size),BLACK); d=ImageDraw.Draw(im)
    # filet or intérieur
    m=int(size*0.10); d.rectangle([m,m,size-m-1,size-m-1], outline=GOLD, width=max(1,size//64))
    f=font(SERIF_B if size>=64 else SERIF, int(size*0.46))
    # "HH" centré
    ctext(d, size/2, size*0.26, "HH", f, BG, ls=int(size*0.01))
    # point or
    r=max(1,size//26); d.ellipse([size/2-r, size*0.74-r, size/2+r, size*0.74+r], fill=GOLD)
    return im
m180=monogram(180); m180.save(os.path.join(FAV,"apple-touch.png"))
monogram(180).resize((32,32),Image.LANCZOS).save(os.path.join(FAV,"favicon-32.png"))
print("favicon + apple-touch OK")

# ---------- OG 1200x630 ----------
W,H=1200,630
im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
# filet or
d.rectangle([40,40,W-41,H-41], outline=GOLD, width=2)
# label
fl=font(SANS,22)
ctext(d, W/2, 150, "I M M O B I L I E R   D ' E X C E P T I O N", fl, GOLD_D, ls=2)
# wordmark
fw=font(SERIF_B, 120)
ctext(d, W/2, 215, "HH DESIGN", fw, INK, ls=10)
# hairline or
d.line([(W/2-90,395),(W/2+90,395)], fill=GOLD, width=2)
# tagline
ft=font(SANS,30)
ctext(d, W/2, 425, "Cotonou, Bénin", ft, INK, ls=2)
# losange or
import math
cx,cy,s=W/2,505,9
d.polygon([(cx,cy-s),(cx+s,cy),(cx,cy+s),(cx-s,cy)], fill=GOLD)
im.save(os.path.join(OG,"og-hh.png"))
print("OG OK")
print("DONE")

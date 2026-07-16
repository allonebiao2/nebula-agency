#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Optimise l'image hero Weinkeller (PNG lourd -> webp desktop + mobile) pour le fond du héros."""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, "..", "..", "_partage", "weinkeller HERO.PNG")
OUT  = os.path.join(ROOT, "assets", "images", "hero")
os.makedirs(OUT, exist_ok=True)

im = Image.open(SRC).convert("RGB")
print("source:", im.size)

def save(w, name, q):
    h = round(im.height * w / im.width)
    p = os.path.join(OUT, name)
    im.resize((w, h), Image.LANCZOS).save(p, quality=q, method=6)
    print(f"  {name:32s} {w}x{h}  {os.path.getsize(p)//1024} KB")

save(1672, "weinkeller-hero.webp", 82)         # desktop / retina
save(1000, "weinkeller-hero-mobile.webp", 80)  # mobile portrait
print("OK hero webp")

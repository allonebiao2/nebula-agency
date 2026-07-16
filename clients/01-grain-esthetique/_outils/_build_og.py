#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Finitions : étoile dorée (5★) + génère l'image OG (aperçu WhatsApp/réseaux) 1200×630
à partir de la photo hero intégrée. UTF-8."""
import io, os, re, base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter
os.chdir(os.path.dirname(os.path.abspath(__file__)))
F = "grain-esthetique-LIVE.html"
s = io.open(F, encoding="utf-8").read()

# 1) étoile dorée
s2 = s.replace('<div class="stat-val">5★</div>',
               '<div class="stat-val">5<span style="color:#D4AF72">★</span></div>', 1)
print("étoile dorée:", "OK" if s2 != s else "déjà fait / introuvable")
s = s2
io.open(F, "w", encoding="utf-8").write(s)

# 2) image OG à partir de la plus grande image base64 du fichier (le hero)
imgs = re.findall(r'data:image/(?:jpeg|jpg|png);base64,([A-Za-z0-9+/=]+)', s)
imgs.sort(key=len, reverse=True)
hero = Image.open(io.BytesIO(base64.b64decode(imgs[0]))).convert("RGB")
print("hero source:", hero.size)

W, H = 1200, 630
# cover-crop
scale = max(W / hero.width, H / hero.height)
rw, rh = int(hero.width * scale), int(hero.height * scale)
bg = hero.resize((rw, rh), Image.LANCZOS).crop(((rw - W) // 2, (rh - H) // 2, (rw - W) // 2 + W, (rh - H) // 2 + H))

# assombrissement dégradé (lisibilité du texte) — plus sombre en bas
ov = Image.new("L", (1, H))
for y in range(H):
    t = y / H
    ov.putpixel((0, y), int(150 + 105 * (t ** 1.4)))   # 150→255
ov = ov.resize((W, H))
dark = Image.new("RGB", (W, H), (14, 5, 10))
bg = Image.composite(dark, bg, ov.point(lambda v: int(v * 0.82)))
# léger voile radial central plus clair
bg = Image.blend(bg, Image.new("RGB", (W, H), (26, 14, 20)), 0.06)

d = ImageDraw.Draw(bg)
FT = r"C:\Windows\Fonts"
def font(name, size):
    try: return ImageFont.truetype(os.path.join(FT, name), size)
    except Exception: return ImageFont.load_default()
f_title = font("georgiai.ttf", 92)      # Georgia italique (élégant, proche Cormorant)
f_title2 = font("georgia.ttf", 92)
f_label = font("segoeui.ttf", 27)
f_sub = font("georgia.ttf", 33)

CREAM, ROSE, GOLD, MUT = (253, 240, 246), (240, 168, 200), (212, 175, 114), (208, 190, 200)
def tracked_w(text, fnt, tr): return sum(d.textlength(c, font=fnt) + tr for c in text) - tr
def tracked(x, y, text, fnt, fill, tr):
    for c in text:
        d.text((x, y), c, font=fnt, fill=fill); x += d.textlength(c, font=fnt) + tr

# label haut
lab = "INSTITUT DE BEAUTÉ"
tracked((W - tracked_w(lab, f_label, 8)) / 2, 150, lab, f_label, MUT, 8)
# gem doré + lignes
cx, cy = W / 2, 205
d.line((cx - 120, cy, cx - 16, cy), fill=GOLD, width=2)
d.line((cx + 16, cy, cx + 120, cy), fill=GOLD, width=2)
d.polygon([(cx, cy - 8), (cx + 8, cy), (cx, cy + 8), (cx - 8, cy)], fill=ROSE)
# titre "Grain d'Esthétique" (Grain crème + d'Esthétique rose italique)
t1, t2 = "Grain ", "d'Esthétique"
w1 = d.textlength(t1, font=f_title2); w2 = d.textlength(t2, font=f_title)
tx = (W - (w1 + w2)) / 2; ty = 250
d.text((tx, ty), t1, font=f_title2, fill=CREAM)
d.text((tx + w1, ty), t2, font=f_title, fill=ROSE)
# sous-titre
sub = "Cotonou · Bénin"
d.text(((W - d.textlength(sub, font=f_sub)) / 2, 375), sub, font=f_sub, fill=CREAM)
# bas : maisons
low = "SOTHYS PARIS   ·   SULTANE DE SABA"
tracked((W - tracked_w(low, f_label, 6)) / 2, 545, low, f_label, GOLD, 6)

os.makedirs(os.path.join("assets", "images"), exist_ok=True)
out = os.path.join("assets", "images", "og-grain.jpg")
bg.save(out, quality=88, optimize=True)
print("OG image:", out, os.path.getsize(out) // 1024, "KB")

# -*- coding: utf-8 -*-
"""Genere photo de profil + couverture Facebook pour Vendora, raccord charte app."""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.dirname(os.path.abspath(__file__))

# Charte Vendora
BG     = (10, 10, 18)     # #0a0a12
PURPLE = (139, 91, 255)   # #8B5CFF
CYAN   = (34, 211, 238)   # #22D3EE
WHITE  = (240, 242, 250)

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def font(sz, bold=True):
    for p in ([r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"] if bold
              else [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def diag_grad(W, H):
    """Degrade diagonal violet (haut-gauche) -> cyan (bas-droite)."""
    yy, xx = np.mgrid[0:H, 0:W]
    t = (xx + yy) / max(1, (W + H - 2))
    ch = [PURPLE[i] + (CYAN[i] - PURPLE[i]) * t for i in range(3)]
    arr = np.dstack(ch).astype("uint8")
    return Image.fromarray(arr, "RGB")

def v_points(cx, cy, vsize):
    A, B, C = (19, 21), (32, 45), (45, 21)
    def mp(p):
        return (cx + (p[0] - 32) / 64 * vsize, cy + (p[1] - 33) / 64 * vsize)
    return mp(A), mp(B), mp(C)

def v_mask(size, cx, cy, vsize, width):
    m = Image.new("L", size, 0)
    md = ImageDraw.Draw(m)
    pa, pb, pc = v_points(cx, cy, vsize)
    md.line([pa, pb, pc], fill=255, width=width, joint="curve")
    r = width / 2
    for p in (pa, pb, pc):
        md.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=255)
    return m, (pa, pb, pc)

def paste_v(img, cx, cy, vsize, width):
    """Pose le V degrade + glow + pastilles sur img (RGB), renvoie img."""
    W, H = img.size
    grad = diag_grad(W, H)
    mask, (pa, pb, pc) = v_mask((W, H), cx, cy, vsize, width)
    # glow
    glowmask = mask.filter(ImageFilter.GaussianBlur(width * 0.7))
    glow_grad = Image.blend(Image.new("RGB", (W, H), BG), grad, 0.6)
    img = Image.composite(glow_grad, img, glowmask)
    # stroke plein
    img = Image.composite(grad, img, mask)
    # pastilles aux sommets
    d = ImageDraw.Draw(img)
    r = width * 0.66
    for p, c in [(pa, PURPLE), (pc, CYAN), (pb, CYAN)]:
        d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=c)
        rh = r * 0.42
        d.ellipse([p[0]-rh, p[1]-rh, p[0]+rh, p[1]+rh], fill=lerp(c, WHITE, 0.55))
    return img

# ---------- PHOTO DE PROFIL (1080x1080) ----------
S = 1080
prof = Image.new("RGB", (S, S), BG)
# halo radial doux
glow = Image.new("RGB", (S, S), BG)
ImageDraw.Draw(glow).ellipse([S*0.20, S*0.20, S*0.80, S*0.80], fill=(28, 23, 56))
prof = Image.blend(prof, glow.filter(ImageFilter.GaussianBlur(130)), 0.7)
# anneau degrade circulaire
ring = Image.new("RGBA", (S, S), (0, 0, 0, 0))
rd = ImageDraw.Draw(ring)
cx = cy = S/2; R = S*0.40
steps = 240
for i in range(steps):
    col = lerp(PURPLE, CYAN, abs(0.5 - i/steps) * 2)
    rd.arc([cx-R, cy-R, cx+R, cy+R], i/steps*360, (i+1)/steps*360 + 1, fill=col + (255,), width=11)
prof = prof.convert("RGBA"); prof.alpha_composite(ring); prof = prof.convert("RGB")
prof = paste_v(prof, S/2, S/2 + 8, S*0.42, int(S*0.072))
prof.save(os.path.join(OUT, "vendora-profil-1080.png"))

# ---------- COUVERTURE (1640x624) ----------
W, H = 1640, 624
cov = Image.new("RGB", (W, H), BG)
g = Image.new("RGB", (W, H), BG); gd = ImageDraw.Draw(g)
gd.ellipse([W*0.55, -H*0.4, W*1.15, H*1.2], fill=(44, 28, 84))
gd.ellipse([-W*0.10, H*0.3, W*0.40, H*1.4], fill=(12, 42, 58))
cov = Image.blend(cov, g.filter(ImageFilter.GaussianBlur(170)), 0.85)
cov = paste_v(cov, W*0.83, H*0.50, 340, 30)
d = ImageDraw.Draw(cov)
x0 = 96
d.text((x0, 150), "Vendora", font=font(122, True), fill=WHITE)
d.text((x0, 300), "Votre vendeur IA sur WhatsApp, 24h/24", font=font(46, True), fill=CYAN)
d.text((x0, 372), "Il répond, conseille et prend les commandes à votre place.",
       font=font(34, False), fill=(184, 190, 208))
d.ellipse([x0, 452, x0+22, 474], fill=(37, 211, 102))
d.text((x0+38, 447), "Essai gratuit, sans carte bancaire", font=font(34, False), fill=(150, 156, 176))
cov.save(os.path.join(OUT, "vendora-couverture-1640x624.png"))

print("OK:", [f for f in os.listdir(OUT) if f.endswith(".png")])

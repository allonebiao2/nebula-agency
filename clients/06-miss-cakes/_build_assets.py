# -*- coding: utf-8 -*-
"""
MISS CAKES — pipeline d'assets (NEBULA / nebula-site).
Génère, à partir de rien (logo client non encore reçu) :
  - une MARQUE provisoire « cupcake badge » (logos/mark.png)  -> nav + footer
  - favicon.ico + favicon-32.png + apple-touch-icon.png
  - image sociale OG 1200x630 (og/og.jpg)
  - QR WhatsApp « Commander » (qr/qr-whatsapp.png) pour l'affiche
Ré-exécutable. Quand la patronne envoie son vrai logo + photos :
  - remplacer logos/mark.png par le logo détouré (blanc/noir)
  - ranger les photos optimisées dans images/gallery/<cat>/gN.jpg et
    basculer les .gitem .ph du HTML en <img>.
"""
import os
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "assets", "images")

# ---- Palette Miss cakes (cohérente avec app.css) ----
ROSE      = (229, 156, 169)
ROSE_DEEP = (199, 107, 124)
ROSE_INK  = (162, 59, 83)
COCOA     = (62, 39, 35)
COCOA_2   = (78, 52, 46)
CREAM     = (255, 251, 248)
BG        = (255, 251, 248)
GOLD      = (201, 146, 91)
GOLD_INK  = (135, 85, 36)
MUTED     = (121, 86, 78)

WA_NUMBER = "2290167748955"  # numéro migré 10 chiffres — à CONFIRMER avec la cliente


def ensure(*p):
    d = os.path.join(IMG, *p)
    os.makedirs(d, exist_ok=True)
    return d


def font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


SERIF_B = ["C:/Windows/Fonts/georgiab.ttf", "C:/Windows/Fonts/georgia.ttf"]
SERIF_I = ["C:/Windows/Fonts/georgiaz.ttf", "C:/Windows/Fonts/georgiai.ttf"]
SANS    = ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
SANS_SB = ["C:/Windows/Fonts/segoeuisb.ttf", "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/segoeui.ttf"]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(size, top, bottom):
    w, h = size
    img = Image.new("RGB", size, top)
    d = ImageDraw.Draw(img)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=lerp(top, bottom, y / max(1, h - 1)))
    return img


def radial_glow(base, center, radius, color, strength=0.5):
    """Pose un halo radial doux (color) sur une image RGB."""
    w, h = base.size
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = center
    gd.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=color)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.5))
    return Image.blend(base, Image.composite(Image.new("RGB", (w, h), color), base,
                                             glow.convert("L").point(lambda v: int(v * strength))), 0)


def draw_cupcake(d, S, ink=CREAM, cherry=ROSE):
    """Dessine un cupcake plein, centré, sur un canvas SxS (proportions ~512)."""
    k = S / 512.0
    cx = S / 2

    def E(x, y, r, fill):
        d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    # --- caissette (trapèze) ---
    top_y, bot_y = 268 * k, 392 * k
    tw, bw = 118 * k, 78 * k
    d.polygon([(cx - tw, top_y), (cx + tw, top_y), (cx + bw, bot_y), (cx - bw, bot_y)], fill=ink)
    # base arrondie
    d.ellipse([cx - bw, bot_y - 16 * k, cx + bw, bot_y + 16 * k], fill=ink)
    # plis de la caissette (contraste rose)
    for i in range(-2, 3):
        x0 = cx + i * (tw / 2.4)
        x1 = cx + i * (bw / 2.4)
        d.line([(x0, top_y + 6 * k), (x1, bot_y - 6 * k)], fill=ROSE_DEEP, width=max(2, int(5 * k)))

    # --- glaçage (dôme + 3 boules) ---
    dome_y = 250 * k
    d.ellipse([cx - 126 * k, dome_y - 64 * k, cx + 126 * k, dome_y + 34 * k], fill=ink)
    E(cx - 66 * k, 198 * k, 62 * k, ink)
    E(cx + 66 * k, 198 * k, 62 * k, ink)
    E(cx, 158 * k, 70 * k, ink)

    # --- cerise ---
    E(cx, 112 * k, 22 * k, cherry)
    # tige
    d.line([(cx + 6 * k, 96 * k), (cx + 20 * k, 66 * k)], fill=GOLD, width=max(2, int(6 * k)))


def make_badge(px=512, opaque=False):
    grad = vgrad((px, px), lerp(ROSE, ROSE_DEEP, 0.35), COCOA)
    # léger halo clair en haut
    grad = radial_glow(grad, (px * 0.5, px * 0.12), px * 0.5, (255, 220, 226), 0.18)
    d = ImageDraw.Draw(grad)
    draw_cupcake(d, px, ink=CREAM, cherry=ROSE)
    if opaque:
        return grad
    # coins arrondis -> RGBA
    mask = Image.new("L", (px, px), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, px - 1, px - 1], radius=int(px * 0.27), fill=255)
    out = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    out.paste(grad, (0, 0), mask)
    return out


def build_logo_and_favicons():
    logos = ensure("logos")
    fav = ensure("favicon")

    badge = make_badge(512)
    badge.save(os.path.join(logos, "mark.png"))

    # favicons
    badge.resize((32, 32), Image.LANCZOS).save(os.path.join(fav, "favicon-32.png"))
    badge.resize((16, 16), Image.LANCZOS).save(os.path.join(fav, "favicon-16.png"))
    badge.save(os.path.join(fav, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

    # apple-touch : carré plein (iOS arrondit lui-même)
    apple = make_badge(180, opaque=True)
    apple.save(os.path.join(fav, "apple-touch-icon.png"))
    print("logo + favicons OK")


def build_og():
    og = ensure("og")
    W, H = 1200, 630
    img = vgrad((W, H), (255, 253, 251), (252, 238, 233))
    img = radial_glow(img, (W * 0.86, -40), 520, (245, 200, 210), 0.5)
    img = radial_glow(img, (-30, H + 40), 460, (240, 214, 180), 0.4)
    d = ImageDraw.Draw(img)

    # badge à gauche
    badge = make_badge(232)
    img.paste(badge, (96, H // 2 - 116), badge)

    x = 384
    f_brand = font(SERIF_B, 118)
    f_tag = font(SANS_SB, 36)
    f_sub = font(SANS, 30)

    d.text((x, 196), "Miss cakes", font=f_brand, fill=COCOA)
    # filet rose
    d.rectangle([x + 4, 330, x + 132, 336], fill=ROSE_DEEP)
    d.text((x + 152, 318), "PÂTISSERIE · COTONOU", font=f_tag, fill=ROSE_INK)
    d.text((x + 4, 372), "Gâteaux sur commande · faits maison · livrés à Cotonou",
           font=f_sub, fill=MUTED)
    d.text((x + 4, 420), "Anniversaires · mariages · cupcakes · gourmandises",
           font=f_sub, fill=MUTED)

    img.convert("RGB").save(os.path.join(og, "og.jpg"), quality=86, optimize=True, progressive=True)
    print("OG 1200x630 OK")


def build_qr():
    import segno
    qr = ensure("qr")
    msg = "Bonjour Miss cakes, je souhaite commander un gâteau."
    url = "https://wa.me/%s?text=%s" % (WA_NUMBER, quote(msg))
    segno.make(url, error="m").save(
        os.path.join(qr, "qr-whatsapp.png"), scale=12, border=2,
        dark="#3E2723", light="#FFFFFF")
    print("QR WhatsApp OK ->", url)


if __name__ == "__main__":
    build_logo_and_favicons()
    build_og()
    build_qr()
    print("Terminé.")

# -*- coding: utf-8 -*-
"""Fabrique le favicon et l'image de partage.

Rien ici ne prétend représenter un lieu : ce sont des dessins.
"""
import io
import math
import os

from PIL import Image, ImageDraw, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ICI, "assets", "images")
os.makedirs(IMG, exist_ok=True)

ENCRE = (11, 10, 9)
CLAIR = (242, 237, 229)
TERRE = (164, 70, 42)
OR = (229, 180, 122)


def police(noms, taille):
    for n in noms:
        for d in (r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu"):
            p = os.path.join(d, n)
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, taille)
                except Exception:
                    pass
    return ImageFont.load_default()


SERIF = lambda t: police(["georgia.ttf", "Georgia.ttf", "times.ttf", "DejaVuSerif.ttf"], t)
SERIF_I = lambda t: police(["georgiai.ttf", "timesi.ttf", "DejaVuSerif-Italic.ttf"], t)
SANS = lambda t: police(["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"], t)


# ── 1 · LE FAVICON : l'anneau gradué, l'emblème du site ────────────
def favicon():
    p = []
    for i in range(24):
        a = (i / 24) * math.tau - math.pi / 2
        lg = 4 if i % 6 == 0 else 2.2
        x1, y1 = 16 + math.cos(a) * 10.5, 16 + math.sin(a) * 10.5
        x2, y2 = 16 + math.cos(a) * (10.5 + lg), 16 + math.sin(a) * (10.5 + lg)
        o = "1" if i % 6 == 0 else ".45"
        p.append(
            '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#e5b47a" '
            'stroke-width="1.3" opacity="%s"/>' % (x1, y1, x2, y2, o)
        )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        '<rect width="32" height="32" fill="#0b0a09"/>'
        '<circle cx="16" cy="16" r="10.5" fill="none" stroke="#a4462a" stroke-width="1.6"/>'
        + "".join(p)
        + '<path d="M16 16 L16 7.5" stroke="#f2ede5" stroke-width="1.7" stroke-linecap="round"/>'
        "</svg>"
    )
    with io.open(os.path.join(IMG, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print("favicon.svg  ", len(svg), "octets")


# ── 2 · L'IMAGE DE PARTAGE ─────────────────────────────────────────
def og():
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), ENCRE)
    d = ImageDraw.Draw(im)

    # un dégradé de terre, très sourd, du bas vers le haut
    for y in range(H):
        t = (y / H) ** 2.1
        d.line(
            [(0, y), (W, y)],
            fill=(
                int(ENCRE[0] + (58 - ENCRE[0]) * t),
                int(ENCRE[1] + (26 - ENCRE[1]) * t),
                int(ENCRE[2] + (16 - ENCRE[2]) * t),
            ),
        )

    # l'anneau gradué, à droite
    cx, cy, R = 960, 315, 168
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(72, 62, 52), width=2)
    for i in range(48):
        a = (i / 48) * math.tau - math.pi / 2
        lg = 17 if i % 6 == 0 else 9
        x1, y1 = cx + math.cos(a) * (R + 8), cy + math.sin(a) * (R + 8)
        x2, y2 = cx + math.cos(a) * (R + 8 + lg), cy + math.sin(a) * (R + 8 + lg)
        d.line([x1, y1, x2, y2], fill=(96, 84, 70) if i % 6 else (150, 132, 108), width=2)
    # l'arc parcouru
    d.arc([cx - R, cy - R, cx + R, cy + R], -90, 158, fill=TERRE, width=6)

    f_km = SERIF(64)
    f_u = SANS(18)
    t = "700"
    b = d.textbbox((0, 0), t, font=f_km)
    d.text((cx - (b[2] - b[0]) / 2, cy - 52), t, font=f_km, fill=CLAIR)
    t2 = "K M"
    b2 = d.textbbox((0, 0), t2, font=f_u)
    d.text((cx - (b2[2] - b2[0]) / 2, cy + 26), t2, font=f_u, fill=(160, 150, 136))

    # le titre, à gauche
    x0 = 86
    d.text((x0, 148), "SEPT CENTS KILOMÈTRES · HUIT LIEUX", font=SANS(19), fill=(176, 166, 150))
    d.text((x0, 202), "Bénin", font=SERIF(104), fill=CLAIR)
    f_i = SERIF_I(104)
    d.text((x0, 316), "mon", font=f_i, fill=OR)
    # on mesure « mon » au lieu de deviner : l'italique déborde de sa boîte
    lm = d.textbbox((x0, 316), "mon", font=f_i)[2] - x0
    d.text((x0 + lm + 26, 316), "pays", font=SERIF(104), fill=CLAIR)
    d.line([x0, 452, x0 + 300, 452], fill=TERRE, width=3)
    d.text((x0, 478), "De la Porte du Non-Retour jusqu'au fleuve.", font=SANS(26), fill=(226, 219, 206))
    d.text((x0, 516), "Le voyage remonte la route, à l'envers.", font=SANS(26), fill=(226, 219, 206))
    d.text((x0, 566), "NEBULA AGENCY · COTONOU", font=SANS(17), fill=(132, 122, 108))

    p = os.path.join(IMG, "og.png")
    im.save(p, "PNG", optimize=True)
    print("og.png       ", os.path.getsize(p), "octets", im.size)


if __name__ == "__main__":
    favicon()
    og()

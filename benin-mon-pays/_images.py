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

# Le drapeau, mêmes couleurs officielles que le logo (voir `_logo.py`).
VERT = (0, 135, 81)
JAUNE = (252, 209, 22)
ROUGE = (232, 17, 45)
OR_LOGO = (201, 162, 74)


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


# ── 1 · LE FAVICON ─────────────────────────────────────────────────
# ⚠️ IL N'Y EN A PLUS QU'UN, et il est écrit par `_logo.py` :
# `assets/images/logo/favicon.svg`. Celui qui vivait ici (l'anneau gradué)
# était orphelin depuis que `index.html` pointe vers le dossier du logo :
# deux favicons dans un dépôt, c'est celui que personne ne regarde qui finit
# par partir en ligne.


# ── 1 bis · LE PAYS, dessiné au drapeau ────────────────────────────
def pays(im, cx, cy, hauteur, ligne=True, sur=4):
    """Colle le Bénin rempli du drapeau, avec la ligne des 700 km.

    ⚠️ Dessiné à `sur` fois la taille puis réduit : PIL ne lisse pas les
    polygones, et un contour de pays en escalier se voit immédiatement.
    """
    from _logo import PART_VERTE, pays_points
    from _contour import MALANVILLE, PORTE

    pts, (bx, by, bw, bh), projeter = pays_points(
        cx * sur, cy * sur, hauteur * sur, 0.006)

    masque = Image.new("L", (im.width * sur, im.height * sur), 0)
    ImageDraw.Draw(masque).polygon(pts, fill=255)

    drap = Image.new("RGB", masque.size, ENCRE)
    dd = ImageDraw.Draw(drap)
    vx = bx + bw * PART_VERTE
    dd.rectangle([bx - 4, by - 4, vx, by + bh + 4], fill=VERT)
    dd.rectangle([vx, by - 4, bx + bw + 4, by + bh / 2.0], fill=JAUNE)
    dd.rectangle([vx, by + bh / 2.0, bx + bw + 4, by + bh + 4], fill=ROUGE)

    if ligne:
        x0, y0 = projeter(*PORTE)
        x1, y1 = projeter(*MALANVILLE)
        xf, yf = x0 + (x1 - x0) * 1.16, y0 + (y1 - y0) * 1.16
        e = max(2, int(hauteur * sur * 0.0085))
        dd.line([x0, y0, xf, yf], fill=ENCRE, width=e)
        ang = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
        for i in range(1, 7):
            t = i / 7.0
            mx, my = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            lg = hauteur * sur * 0.019
            dd.line([mx - math.cos(ang) * lg / 2, my - math.sin(ang) * lg / 2,
                     mx + math.cos(ang) * lg / 2, my + math.sin(ang) * lg / 2],
                    fill=ENCRE, width=max(1, int(e * 0.62)))

    corps = Image.new("RGBA", masque.size, (0, 0, 0, 0))
    corps.paste(drap, (0, 0), masque)

    if ligne:
        # le kilomètre zéro, par-dessus la découpe : il déborde sur la mer,
        # comme le monument lui-même
        x0, y0 = projeter(*PORTE)
        dc = ImageDraw.Draw(corps)
        r = hauteur * sur * 0.028
        dc.ellipse([x0 - r, y0 - r, x0 + r, y0 + r], fill=ENCRE + (255,))
        r2 = hauteur * sur * 0.015
        dc.ellipse([x0 - r2, y0 - r2, x0 + r2, y0 + r2], fill=OR_LOGO + (255,))

    corps = corps.resize((im.width, im.height), Image.LANCZOS)
    im.paste(corps, (0, 0), corps)


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

    # LE PAYS, à droite : c'est la marque depuis le 2026-08-11. La vignette
    # WhatsApp est la première impression au Bénin, elle porte le logo.
    cx, cy = 962, 292
    pays(im, cx, cy, 462)
    d = ImageDraw.Draw(im)

    f_km, f_u = SERIF(52), SANS(17)
    t = "700"
    b = d.textbbox((0, 0), t, font=f_km)
    d.text((cx - (b[2] - b[0]) / 2, 552), t, font=f_km, fill=CLAIR)
    t2 = "K M"
    b2 = d.textbbox((0, 0), t2, font=f_u)
    d.text((cx - (b2[2] - b2[0]) / 2, 604), t2, font=f_u, fill=(160, 150, 136))

    # le titre, à gauche
    x0 = 86
    d.text((x0, 148), "HUIT LIEUX · UN SEUL MOUVEMENT", font=SANS(19), fill=(176, 166, 150))
    f_n = SERIF(104)
    f_i = SERIF_I(104)
    d.text((x0, 232), "Mon", font=f_n, fill=CLAIR)
    # on mesure au lieu de deviner : l'italique déborde de sa boîte
    lm = d.textbbox((x0, 232), "Mon", font=f_n)[2] - x0
    d.text((x0 + lm + 30, 232), "Bénin", font=f_i, fill=OR)
    d.text((x0, 384), "S E P T   C E N T S   K I L O M È T R E S",
           font=SANS(23), fill=(205, 196, 182))
    d.line([x0, 452, x0 + 300, 452], fill=TERRE, width=3)
    d.text((x0, 478), "De la Porte du Non-Retour jusqu'au fleuve.", font=SANS(26), fill=(226, 219, 206))
    d.text((x0, 516), "Le voyage remonte la route, à l'envers.", font=SANS(26), fill=(226, 219, 206))
    d.text((x0, 566), "NEBULA AGENCY · COTONOU", font=SANS(17), fill=(132, 122, 108))

    p = os.path.join(IMG, "og.png")
    im.save(p, "PNG", optimize=True)
    print("og.png       ", os.path.getsize(p), "octets", im.size)


if __name__ == "__main__":
    og()

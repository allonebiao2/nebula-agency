#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HILLARY M. STYL — l'image de partage (Open Graph).

    python _og.py

POURQUOI ELLE EXISTE
Le site n'avait AUCUNE `og:image`. Au Bénin, un lien se partage sur WhatsApp :
sans image, la maison apparaissait comme une ligne de texte grise au milieu
d'une conversation, à côté de liens qui, eux, montrent une photo. C'est le
défaut le plus coûteux commercialement qu'un site puisse avoir, et il ne se
voit jamais en regardant le site.

CE QU'ELLE MONTRE
Une vraie pièce d'Hillary, détourée, sur son encre, avec son magenta. Rien de
généré, rien d'inventé : la photo vient de `assets/images/`.

⚠️ En JPEG, pas en WebP : l'aperçu de WhatsApp ne montre pas toujours le WebP.
⚠️ 1200x630, le format que lisent Facebook, WhatsApp, LinkedIn et X.
"""
import io, os, sys
from PIL import Image, ImageDraw, ImageFont

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ICI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ICI, "assets", "images")
SORTIE = os.path.join(IMG, "og.jpg")

L, H = 1200, 630
ENCRE = (12, 12, 12)
ROSE = (230, 0, 126)
PAPIER = (247, 245, 240)
GRIS = (150, 146, 140)

# des polices réellement présentes sur la machine, dans l'ordre de préférence
SERIF = [r"C:\Windows\Fonts\BOD_R.TTF", r"C:\Windows\Fonts\georgia.ttf",
         r"C:\Windows\Fonts\times.ttf"]
SANS = [r"C:\Windows\Fonts\ARIALN.TTF", r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeui.ttf"]


def police(liste, taille):
    for p in liste:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, taille)
            except Exception:
                pass
    return ImageFont.load_default()


def main():
    im = Image.new("RGB", (L, H), ENCRE)
    d = ImageDraw.Draw(im)

    # une nappe de magenta très basse, en bas à gauche : elle donne la
    # profondeur sans jamais passer derrière le texte
    nappe = Image.new("RGB", (L, H), ENCRE)
    nd = ImageDraw.Draw(nappe)
    nd.ellipse([-260, H - 300, 520, H + 340], fill=ROSE)
    nappe = nappe.filter(__import__("PIL.ImageFilter", fromlist=["ImageFilter"]).GaussianBlur(150))
    im = Image.blend(im, nappe, 0.22)
    d = ImageDraw.Draw(im)

    # la pièce, détourée, à droite
    piece = None
    for nom in ("piece-ceremonie.webp", "piece-mira.webp", "piece-josy.webp"):
        c = os.path.join(IMG, nom)
        if os.path.exists(c):
            piece = Image.open(c).convert("RGBA")
            break
    if piece:
        h_cible = 600
        r = h_cible / piece.height
        piece = piece.resize((max(1, int(piece.width * r)), h_cible), Image.LANCZOS)
        im.paste(piece, (L - piece.width - 40, H - h_cible + 20), piece)

    # le trait de coupe : la signature de la V4
    d.line([(72, 214), (168, 214)], fill=ROSE, width=3)

    f_nom = police(SERIF, 92)
    f_sous = police(SANS, 27)
    f_pied = police(SANS, 23)

    d.text((70, 240), "HILLARY", font=f_nom, fill=PAPIER)
    d.text((70, 340), "M. STYL", font=f_nom, fill=PAPIER)
    d.text((74, 462), "MAISON DE COUTURE · COTONOU", font=f_sous, fill=(214, 210, 203))
    d.text((74, 508), "Sur-mesure, prêt-à-porter, pagne et wax.", font=f_pied, fill=GRIS)
    d.text((74, 542), "Vos mesures en ligne, la date de livraison annoncée.",
           font=f_pied, fill=GRIS)

    im.save(SORTIE, "JPEG", quality=86, optimize=True, progressive=True)
    print(f"  og.jpg écrit — {os.path.getsize(SORTIE) // 1024} Ko, {L}x{H}")

    # ---- la couverture de la fiche Google (1024x576, format 16:9) -------
    couv = im.resize((1024, 538), Image.LANCZOS).crop((0, 0, 1024, 538))
    fond = Image.new("RGB", (1024, 576), ENCRE)
    fond.paste(couv, (0, 19))
    c_out = os.path.join(IMG, "google-couverture.jpg")
    fond.save(c_out, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"  google-couverture.jpg écrit — {os.path.getsize(c_out) // 1024} Ko, 1024x576")

    # ---- le logo carré de la fiche Google (720x720) ---------------------
    # ⚠️ Google recadre parfois en cercle : on garde une marge franche, le
    #    logo ne doit jamais toucher le bord.
    logo_src = os.path.join(IMG, "logo.png")
    if os.path.exists(logo_src):
        carre = Image.new("RGB", (720, 720), PAPIER)
        lg = Image.open(logo_src).convert("RGBA")
        r = 560 / lg.width
        lg = lg.resize((560, max(1, int(lg.height * r))), Image.LANCZOS)
        carre.paste(lg, ((720 - lg.width) // 2, (720 - lg.height) // 2), lg)
        l_out = os.path.join(IMG, "google-logo.jpg")
        carre.save(l_out, "JPEG", quality=92, optimize=True)
        print(f"  google-logo.jpg écrit — {os.path.getsize(l_out) // 1024} Ko, 720x720")
    return 0


if __name__ == "__main__":
    sys.exit(main())

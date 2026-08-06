#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANGY ART — génération des assets. Ré-exécutable, idempotent.

    python _build_assets.py

Part du VRAI logo d'Angélique (`_sources/logo-transparent.png`) et en tire :
  · assets/images/logos/marque.png       le glyphe seul, détouré (nav, affiche)
  · assets/images/logos/logo-complet.png le logo entier, détouré
  · assets/images/favicon.png            32 px, glyphe sur noir
  · assets/images/favicon-180.png        apple-touch
  · assets/images/og/og.png              1200x630, partage social
  · assets/images/qr/qr-whatsapp.png     la conversation, pré-remplie
  · assets/images/qr/qr-site.png         le site

⚠️ Chaque QR est RELU par décodage avant d'être gardé. Un QR qu'on n'a pas
   décodé est un QR dont on ne sait rien, et il part à l'imprimeur.
"""
import os, sys, urllib.parse
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import segno

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RACINE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(RACINE, "assets", "images")
SRC = os.path.join(RACINE, "_sources", "logo-transparent.png")

NUM = "2290152006490"
SITE = "https://angy-art.pages.dev/"
MSG = ("Bonjour Angélique, j'ai vu votre site. Pouvez-vous m'envoyer le "
       "portfolio complet des pièces disponibles ?")
WA = "https://wa.me/" + NUM + "?text=" + urllib.parse.quote(MSG)

NOIR = (10, 10, 10)
CREME = (243, 239, 230)
OR = (189, 159, 100)          # son or réel, relevé sur le logo


def police(noms, taille):
    base = r"C:\Windows\Fonts"
    for n in noms:
        p = os.path.join(base, n)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, taille)
            except Exception:
                pass
    return ImageFont.load_default()


SERIF = lambda t: police(["georgiab.ttf", "georgia.ttf", "times.ttf"], t)
SANS = lambda t: police(["seguisb.ttf", "segoeui.ttf", "arial.ttf"], t)


def bandes(alpha, seuil=24, mini=4):
    """Les blocs horizontaux de contenu : le glyphe, le mot, l'accroche."""
    lignes = (alpha > seuil).sum(axis=1)
    out, dans, deb = [], False, 0
    for y, v in enumerate(lignes):
        if v > 0 and not dans:
            dans, deb = True, y
        elif v == 0 and dans:
            dans = False
            if y - deb > mini:
                out.append((deb, y))
    if dans:
        out.append((deb, len(lignes)))
    return out


def decouper(im, haut, bas, marge=0):
    """Coupe une bande et la resserre sur son contenu réel."""
    z = im.crop((0, haut, im.width, bas))
    b = z.getchannel("A").getbbox()
    z = z.crop(b)
    if marge:
        f = Image.new("RGBA", (z.width + marge * 2, z.height + marge * 2), (0, 0, 0, 0))
        f.paste(z, (marge, marge))
        z = f
    return z


def faire_logos():
    os.makedirs(os.path.join(IMG, "logos"), exist_ok=True)
    im = Image.open(SRC).convert("RGBA")
    a = np.array(im.getchannel("A"))
    bs = bandes(a)
    if len(bs) < 3:
        raise SystemExit(f"  le logo source a {len(bs)} bande(s), 3 attendues")

    marque = decouper(im, bs[0][0], bs[0][1])
    marque.save(os.path.join(IMG, "logos", "marque.png"))
    print(f"  logos/marque.png        {marque.width}x{marque.height}  (le glyphe seul)")

    complet = im.crop(im.getchannel("A").getbbox())
    complet.save(os.path.join(IMG, "logos", "logo-complet.png"))
    print(f"  logos/logo-complet.png  {complet.width}x{complet.height}")
    return marque, complet


def poser(fond, calque, cx, cy, h):
    """Pose un calque transparent, centré, à une hauteur donnée."""
    r = h / calque.height
    c = calque.resize((max(1, int(calque.width * r)), h), Image.LANCZOS)
    fond.paste(c, (int(cx - c.width / 2), int(cy - c.height / 2)), c)
    return c


def faire_favicons(marque):
    for taille, nom in ((180, "favicon-180.png"), (32, "favicon.png")):
        S = 4
        im = Image.new("RGB", (taille * S, taille * S), NOIR)
        poser(im, marque, taille * S / 2, taille * S * 0.46, int(taille * S * 0.62))
        d = ImageDraw.Draw(im)
        y = int(taille * S * 0.9)
        d.line([(taille * S * 0.16, y), (taille * S * 0.84, y)],
               fill=OR, width=max(2, int(taille * S * 0.035)))
        im.resize((taille, taille), Image.LANCZOS).save(os.path.join(IMG, nom))
        print(f"  {nom}")


def faire_og(marque):
    """La carte de partage : le glyphe, le nom, l'accroche d'Angélique."""
    os.makedirs(os.path.join(IMG, "og"), exist_ok=True)
    L, H, S = 1200, 630, 2
    im = Image.new("RGB", (L * S, H * S), NOIR)
    d = ImageDraw.Draw(im)

    for x in range(0, L * S):                       # la lumière rasante
        k = max(0.0, 1 - abs(x - L * S * 0.68) / (L * S * 0.46))
        if k <= 0:
            continue
        k = k ** 1.6
        d.line([(x, 0), (x - 150 * S, H * S)],
               fill=(int(10 + 32 * k), int(10 + 27 * k), int(10 + 19 * k)))

    mg = 78 * S
    poser(im, marque, mg + 62 * S, 150 * S, 168 * S)

    d.text((mg, 268 * S), "ANGY · ART", font=SERIF(76 * S), fill=CREME)
    d.text((mg, 372 * S), "Inspiré d'en haut, enraciné ici.",
           font=police(["georgiai.ttf", "georgia.ttf"], 34 * S), fill=OR)
    d.line([(mg, 448 * S), (mg + 92 * S, 448 * S)], fill=OR, width=2 * S)
    d.text((mg, 476 * S), "ANGÉLIQUE AVOCEVOU", font=SANS(21 * S), fill=(214, 210, 202))
    d.text((mg, 512 * S), "ARTISTE PLASTICIENNE · COTONOU, BÉNIN",
           font=SANS(18 * S), fill=(166, 162, 154))

    im.resize((L, H), Image.LANCZOS).save(os.path.join(IMG, "og", "og.png"))
    print("  og/og.png  1200x630")


def faire_qr(donnee, nom, libelle):
    dossier = os.path.join(IMG, "qr")
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, nom)
    segno.make(donnee, error="h").save(chemin, scale=14, border=3,
                                       dark="#0a0a0a", light="#ffffff")
    lu = None
    try:
        import cv2
        lu, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread(chemin))
    except Exception:
        pass
    if not lu:
        try:
            from pyzbar.pyzbar import decode
            r = decode(Image.open(chemin))
            lu = r[0].data.decode("utf-8") if r else None
        except Exception:
            pass
    if lu != donnee:
        raise SystemExit(f"  QR {nom} : DÉCODAGE FAUX\n    attendu : {donnee}\n    lu      : {lu}")
    print(f"  qr/{nom}  décodé et vérifié ({libelle})")


if __name__ == "__main__":
    print("ANGY ART — assets, à partir du vrai logo")
    marque, complet = faire_logos()
    faire_favicons(marque)
    faire_og(marque)
    faire_qr(WA, "qr-whatsapp.png", "WhatsApp pré-rempli")
    faire_qr(SITE, "qr-site.png", "le site")
    print("Terminé.")

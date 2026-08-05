#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANGY ART — génération des assets. Ré-exécutable, idempotent.

    python _build_assets.py

Produit :
  · assets/images/favicon-180.png       (apple-touch, monogramme)
  · assets/images/og/og.png             (1200x630, partage social)
  · assets/images/qr/qr-whatsapp.png    (la conversation, pré-remplie)
  · assets/images/qr/qr-site.png        (le site)

⚠️ Chaque QR est RELU par décodage avant d'être gardé. Un QR qu'on n'a pas
   décodé est un QR dont on ne sait rien, et il part à l'imprimeur.
"""
import io, os, sys, urllib.parse
from PIL import Image, ImageDraw, ImageFont
import segno

RACINE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(RACINE, "assets", "images")

NUM = "2290152006490"
SITE = "https://angy-art.pages.dev/"
MSG = ("Bonjour Angélique, j'ai vu votre site. Pouvez-vous m'envoyer le "
       "portfolio complet des pièces disponibles ?")
WA = "https://wa.me/" + NUM + "?text=" + urllib.parse.quote(MSG)

NOIR = (10, 10, 10)
CREME = (243, 239, 230)
OR = (201, 185, 154)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


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


def monogramme(im, d, cx, cy, h, coul, ep):
    """Le A·A gravé : deux A, barre comprise. Les deux A se chevauchent
    légèrement, comme un poinçon frappé deux fois au même endroit."""
    l = h * 0.66
    ecart = l * 0.58
    for dx in (-ecart, ecart):
        x = cx + dx
        haut, bas = cy - h / 2, cy + h / 2
        d.line([(x - l / 2, bas), (x, haut)], fill=coul, width=ep)
        d.line([(x, haut), (x + l / 2, bas)], fill=coul, width=ep)
        # la barre, posée aux deux tiers de la hauteur
        k = 0.62
        y = haut + (bas - haut) * k
        demi = (l / 2) * k
        d.line([(x - demi, y), (x + demi, y)], fill=coul, width=ep)


def arche(d, cx, cy, larg, haut, coul, ep):
    """La silhouette de l'arche : la forme des cadres du site."""
    r = larg / 2
    g, dr = cx - r, cx + r
    b = cy + haut / 2
    sommet = cy - haut / 2
    d.arc([g, sommet, dr, sommet + larg], 180, 360, fill=coul, width=ep)
    d.line([(g, sommet + r), (g, b)], fill=coul, width=ep)
    d.line([(dr, sommet + r), (dr, b)], fill=coul, width=ep)
    d.line([(g, b), (dr, b)], fill=coul, width=ep)


def centre(d, y, txt, fnt, coul, larg):
    b = d.textbbox((0, 0), txt, font=fnt)
    d.text(((larg - (b[2] - b[0])) / 2 - b[0], y), txt, font=fnt, fill=coul)
    return b[3] - b[1]


def faire_favicon():
    os.makedirs(IMG, exist_ok=True)
    T = 180
    im = Image.new("RGB", (T * 4, T * 4), NOIR)
    d = ImageDraw.Draw(im)
    monogramme(im, d, T * 2, T * 1.9, T * 1.9, CREME, 22)
    d.line([(T * 0.5, T * 3.35), (T * 3.5, T * 3.35)], fill=OR, width=14)
    im = im.resize((T, T), Image.LANCZOS)
    im.save(os.path.join(IMG, "favicon-180.png"))
    print("  favicon-180.png")


def faire_og():
    """La carte de partage : la composition du site, en une image.
    Titre à gauche, l'arche à droite, la lumière qui passe entre les deux."""
    os.makedirs(os.path.join(IMG, "og"), exist_ok=True)
    L, H = 1200, 630
    S = 2                                      # on dessine en double, on réduit
    im = Image.new("RGB", (L * S, H * S), NOIR)
    d = ImageDraw.Draw(im)

    # la lumière rasante
    for x in range(0, L * S):
        k = max(0.0, 1 - abs(x - L * S * 0.66) / (L * S * 0.44))
        if k <= 0:
            continue
        k = k ** 1.6
        d.line([(x, 0), (x - 150 * S, H * S)],
               fill=(int(10 + 34 * k), int(10 + 29 * k), int(10 + 21 * k)))

    mg = 74 * S
    # l'arche, à droite
    ax, ay = L * S * 0.775, H * S * 0.5
    aw, ah = 268 * S, 400 * S
    arche(d, ax, ay, aw, ah, (86, 78, 64), 3 * S)
    for i, dy in enumerate((-96, -64)):         # les entailles, dedans
        d.arc([ax - aw * 0.3, ay + dy * S - 34 * S, ax + aw * 0.3, ay + dy * S + 34 * S],
              200, 340, fill=(150, 138, 116), width=2 * S)
    for i in range(4):                          # les chevrons
        x0 = ax - aw * 0.3 + i * (aw * 0.2)
        d.line([(x0, ay + 26 * S), (x0 + aw * 0.1, ay), (x0 + aw * 0.2, ay + 26 * S)],
               fill=(150, 138, 116), width=2 * S)
    for i in range(7):                          # les traits creusés
        x0 = ax - aw * 0.32 + i * (aw * 0.107)
        d.line([(x0, ay + 104 * S), (x0, ay + 138 * S)], fill=(150, 138, 116), width=2 * S)

    # le titre, à gauche
    monogramme(im, d, mg + 30 * S, 118 * S, 52 * S, CREME, 4 * S)
    d.text((mg, 168 * S), "ANGY", font=SERIF(104 * S), fill=CREME)
    d.text((mg, 268 * S), "ART", font=SERIF(104 * S), fill=CREME)
    d.text((mg, 402 * S), "Angélique Avocevou", font=SERIF(34 * S), fill=OR)
    d.text((mg, 456 * S), "ARTISTE PLASTICIENNE · COTONOU, BÉNIN",
           font=SANS(19 * S), fill=(166, 162, 154))
    d.line([(mg, 512 * S), (mg + 96 * S, 512 * S)], fill=OR, width=2 * S)
    d.text((mg, 534 * S), "On ne peint pas la mémoire. On la creuse.",
           font=SERIF(26 * S), fill=(196, 192, 184))

    im.resize((L, H), Image.LANCZOS).save(os.path.join(IMG, "og", "og.png"))
    print("  og/og.png  1200x630")


def faire_qr(donnee, nom, libelle):
    dossier = os.path.join(IMG, "qr")
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, nom)
    q = segno.make(donnee, error="h")
    q.save(chemin, scale=14, border=3, dark="#0a0a0a", light="#ffffff")

    # ---- on relit ce qu'on vient d'écrire ----
    lu = None
    try:
        import cv2
        import numpy as np
        img = cv2.imread(chemin)
        lu, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
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
    return chemin


if __name__ == "__main__":
    print("ANGY ART — assets")
    faire_favicon()
    faire_og()
    faire_qr(WA, "qr-whatsapp.png", "WhatsApp pré-rempli")
    faire_qr(SITE, "qr-site.png", "le site")
    print("Terminé.")

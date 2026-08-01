# -*- coding: utf-8 -*-
"""
Affiche A4 imprimable + QR pour HILLARY M. STYL.
A4 à 300 DPI (2480 × 3508), fond crème, accents magenta, logo réel de la maison.
Deux QR : le site (catalogue et commande) et WhatsApp (parler à Hillary).

Sortie : assets/docs/Affiche_Hillary_M_Styl_A4.{png,pdf} + qr-site.png + qr-whatsapp.png
Le PDF est produit par reportlab (pas de navigateur, pas de puppeteer qui se fige).
"""
import os, urllib.parse
from PIL import Image, ImageDraw, ImageFont
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4

CL   = r"C:/Users/USER/nebula-agency/clients/10-hillary-m-styl"
DOCS = CL + "/assets/docs"; os.makedirs(DOCS, exist_ok=True)
F    = "C:/Windows/Fonts/"

SITE = "https://hillary-m-styl.pages.dev"
WA   = "22951374793"
WA_L = "+229 51 37 47 93"
WA_URL = "https://wa.me/" + WA + "?text=" + urllib.parse.quote(
    "Bonjour HILLARY M. STYL, je viens de votre affiche. J'aimerais commander une tenue.")

W, H = 2480, 3508
CX = W // 2
MAGENTA = (230, 0, 126)
MAG_CLAIR = (255, 232, 244)
NOIR = (10, 10, 10)
CREME = (251, 251, 252)
GRIS = (122, 122, 130)

def f(nom, sz): return ImageFont.truetype(F + nom, sz)
bahn  = lambda s: f("bahnschrift.ttf", s)   # géométrique, cousin d'Archivo (titres)
ar    = lambda s: f("arial.ttf", s)
arb   = lambda s: f("arialbd.ttf", s)

img = Image.new("RGB", (W, H), CREME)
d = ImageDraw.Draw(img, "RGBA")

# ── bandeau magenta en haut, pavé noir en pied (le ruban du logo, repris en aplat) ──
BANDE = 3230                       # le pied noir commence ici, SOUS les cartes QR
d.rectangle([0, 0, W, 26], fill=MAGENTA)
d.rectangle([0, BANDE, W, H], fill=NOIR)

# ── voile rose très pâle derrière les QR, sans mordre sur le paragraphe ──
d.rectangle([0, 2110, W, BANDE], fill=MAG_CLAIR)

def centre(txt, y, font, fill, espacement=0):
    """Écrit centré ; espacement = interlettrage en pixels."""
    if not espacement:
        w = d.textlength(txt, font=font)
        d.text((CX - w / 2, y), txt, font=font, fill=fill)
        return
    largeurs = [d.textlength(c, font=font) for c in txt]
    total = sum(largeurs) + espacement * (len(txt) - 1)
    x = CX - total / 2
    for c, lc in zip(txt, largeurs):
        d.text((x, y), c, font=font, fill=fill)
        x += lc + espacement

# ── logo réel de la maison ──
logo = Image.open(CL + "/assets/images/logo.png").convert("RGBA")
lw = 1180
logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
img.paste(logo, (CX - lw // 2, 210), logo)

y = 210 + logo.height + 120

# ── accroche ──
centre("PRÊT-À-PORTER  ·  SUR-MESURE", y, bahn(74), MAGENTA, espacement=6)
y += 190

centre("Vos tenues,", y, bahn(178), NOIR); y += 205
centre("à votre taille", y, bahn(178), NOIR); y += 205
centre("ou à vos mesures.", y, bahn(178), MAGENTA); y += 265

# filet magenta
d.rectangle([CX - 190, y, CX + 190, y + 7], fill=MAGENTA)
y += 110

for ligne in ["Choisissez votre pièce, donnez vos mesures en ligne,",
              "retirez à l'atelier ou faites-vous livrer."]:
    centre(ligne, y, ar(64), GRIS); y += 92

# ── les deux QR ──
def qr_png(data, chemin, taille=760):
    q = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=20, border=2)
    q.add_data(data); q.make(fit=True)
    im = q.make_image(fill_color=(10, 10, 10), back_color="white").convert("RGB")
    im = im.resize((taille, taille), Image.NEAREST)
    im.save(chemin)
    return im

qr_site = qr_png(SITE,   DOCS + "/qr-site.png")
qr_wa   = qr_png(WA_URL, DOCS + "/qr-whatsapp.png")

QY = 2190
for qr, cx, titre, sous in ((qr_site, CX - 560, "VOIR LE CATALOGUE", "et commander en ligne"),
                            (qr_wa,   CX + 560, "PARLER À HILLARY",  "directement sur WhatsApp")):
    # carte blanche sous le QR
    d.rounded_rectangle([cx - 440, QY - 60, cx + 440, QY + 1000], radius=34, fill=(255, 255, 255))
    d.rounded_rectangle([cx - 440, QY - 60, cx + 440, QY + 1000], radius=34, outline=MAGENTA, width=5)
    img.paste(qr, (cx - qr.width // 2, QY + 10))
    w = d.textlength(titre, font=bahn(60)); d.text((cx - w / 2, QY + 806), titre, font=bahn(60), fill=NOIR)
    w = d.textlength(sous, font=ar(46));    d.text((cx - w / 2, QY + 894), sous,  font=ar(46),  fill=GRIS)

# ── pied noir : le numéro en clair, pour qui n'a pas de lecteur de QR ──
centre("COMMANDEZ SUR WHATSAPP", BANDE + 38, ar(44), (176, 176, 186), espacement=5)
centre(WA_L, BANDE + 92, bahn(92), (255, 255, 255))
w = d.textlength("hillary-m-styl.pages.dev", font=ar(42))
d.text((CX - w / 2, BANDE + 205), "hillary-m-styl.pages.dev", font=ar(42), fill=MAGENTA)

png = DOCS + "/Affiche_Hillary_M_Styl_A4.png"
img.save(png, dpi=(300, 300))

pdf = DOCS + "/Affiche_Hillary_M_Styl_A4.pdf"
c = rl_canvas.Canvas(pdf, pagesize=A4)
c.drawImage(png, 0, 0, width=A4[0], height=A4[1])
c.save()

print("affiche :", png)
print("pdf     :", pdf, os.path.getsize(pdf) // 1024, "Ko")

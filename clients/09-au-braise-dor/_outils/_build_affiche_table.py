# -*- coding: utf-8 -*-
"""
L'affiche CARRÉE des tables : un seul QR, en grand, vers la carte en ligne.

    python _outils/_build_affiche_table.py

Produit dans assets/docs/ :
  - Affiche_Table_Au_Braise_dOr_20cm.png / .pdf : le carré maître, 20 x 20 cm à 300 DPI.
    Il se réduit sans perte à 15 ou 10 cm (c'est le même fichier, l'imprimeur choisit l'échelle).
  - Planche_A4_6_carres_Au_Braise_dOr.pdf : six carrés de 9 cm sur une feuille A4, avec
    traits de coupe, pour l'imprimeur du coin qui n'imprime que de l'A4.

Même charte que l'affiche A4 (`_build_affiche.py`) : fond braise, or, Cambria.

⚠️ Aucun numéro de téléphone imprimé : le site en porte un, l'enseigne un autre, et une
affiche collée sur trente tables ne se corrige pas. Le QR mène au site, le site mène à WhatsApp.
⚠️ Chaque QR est DÉCODÉ après fabrication, à pleine taille ET réduit comme sur une
impression de 9 cm : un QR qu'on n'a pas relu n'est pas livré.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import qrcode

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CL   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(CL, "assets", "docs"); os.makedirs(DOCS, exist_ok=True)
F    = "C:/Windows/Fonts/"

SITE = "https://aubraisedor.com"
N    = 2362                  # 200 mm à 300 DPI
CX   = N // 2
GOLD  = (244, 212, 149); GOLD2 = (233, 184, 102)
CREAM = (246, 236, 218); CREAMD = (220, 202, 169); MUTED = (150, 132, 110)
EMBER = (255, 106, 26);  INK = (20, 12, 7); CARTE = (247, 240, 228)


def font(name, sz): return ImageFont.truetype(F + name, sz)
cam = lambda s: font("cambriab.ttf", s)
ar  = lambda s: font("arial.ttf", s)
arb = lambda s: font("arialbd.ttf", s)


def fond():
    """Le dégradé braise de l'affiche A4, recadré au carré."""
    top = np.array([13, 7, 4.]); mid = np.array([30, 19, 10.]); bot = np.array([36, 22, 13.])
    t = np.linspace(0, 1, N)[:, None]
    grad = np.where(t < .5, top * (1 - t * 2) + mid * (t * 2), mid * (1 - (t - .5) * 2) + bot * ((t - .5) * 2))
    bg = np.repeat(grad[:, None, :], N, axis=1)
    yy, xx = np.mgrid[0:N, 0:N]

    def glow(cx, cy, rad, col, force, pw=1.0):
        r = np.sqrt((xx - cx) ** 2 + ((yy - cy) / pw) ** 2)
        return (np.clip(1 - r / rad, 0, 1) ** 1.7)[..., None] * np.array(col) * force

    bg = bg + glow(CX, N * 1.05, N * 0.95, EMBER, .62, 1.1)      # la braise, en bas
    bg = bg + glow(N * .1, -N * .03, N * .5, (226, 64, 27), .16)
    bg = bg + glow(N * .92, N * .02, N * .45, GOLD2, .10)
    return Image.fromarray(np.clip(bg, 0, 255).astype("uint8"), "RGB")


def qr_net(data, px):
    """QR sans marge propre (la carte crème fait la zone de silence), modules entiers."""
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=1, border=0)
    q.add_data(data); q.make(fit=True)
    m = q.modules_count
    taille = (px // m) * m                   # pas de module à demi-pixel : bords nets à l'impression
    im = q.make_image(fill_color=(20, 12, 7), back_color=CARTE).convert("RGB")
    return im.resize((taille, taille), Image.NEAREST), m


def carre():
    img = fond(); d = ImageDraw.Draw(img, "RGBA")

    def ctext(y, txt, fnt, fill): d.text((CX, y), txt, font=fnt, fill=fill, anchor="mm")

    def tracked(y, txt, fnt, fill, sp):
        w = [d.textlength(c, font=fnt) + sp for c in txt]; x = CX - (sum(w) - sp) / 2
        for c, wd in zip(txt, w):
            d.text((x, y), c, font=fnt, fill=fill, anchor="lm"); x += wd

    # ---- en-tête ----
    tracked(150, "DE PARIS À COTONOU", arb(38), GOLD, 20)
    ctext(290, "Au Braisé d'Or", cam(180), GOLD)
    ctext(435, "Toute la carte, en photos", cam(72), CREAM)

    # ---- la carte crème et son QR ----
    qr, modules = qr_net(SITE, 1020)
    q = qr.size[0]; mod = q // modules
    silence = 4 * mod                         # la zone de silence exigée par la norme
    cw = q + 2 * silence
    # Dessous : l'adresse écrite, pour qui ne scanne pas. Elle commence à 3 modules du QR,
    # jamais collée à lui (un texte dans la zone de silence gêne les lecteurs bon marché).
    legende = q + silence + 3 * mod + 37
    ch = legende + 37 + 60
    x0 = CX - cw // 2; y0 = 510
    d.rounded_rectangle([x0 + 10, y0 + 18, x0 + cw + 10, y0 + ch + 18], 64, fill=(0, 0, 0, 90))  # ombre
    d.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], 64, fill=CARTE + (255,))
    d.rounded_rectangle([x0 - 14, y0 - 14, x0 + cw + 14, y0 + ch + 14], 76, outline=GOLD2 + (200,), width=5)
    img.paste(qr, (CX - q // 2, y0 + silence))
    d.text((CX, y0 + legende), "aubraisedor.com", font=arb(74), fill=(120, 70, 20), anchor="mm")

    # ---- les trois gestes ----
    gy = y0 + ch + 14 + 112                   # sous le filet d'or
    gestes = ["Scannez", "Choisissez", "Envoyez sur WhatsApp"]
    fg = arb(54); r = 40; gap = 90
    larg = [2 * r + 22 + d.textlength(g, font=fg) for g in gestes]
    x = CX - (sum(larg) + gap * (len(gestes) - 1)) / 2
    for i, (g, w) in enumerate(zip(gestes, larg), 1):
        d.ellipse([x, gy - r, x + 2 * r, gy + r], fill=GOLD2)
        d.text((x + r, gy + 2), str(i), font=arb(50), fill=INK, anchor="mm")
        d.text((x + 2 * r + 22, gy), g, font=fg, fill=CREAM, anchor="lm")
        x += w + gap

    ctext(gy + 105, "Sur place  ·  À emporter  ·  En livraison", ar(48), CREAMD)
    bas = N - 80
    assert bas - 15 > gy + 105 + 24 + 40, "la mention NEBULA touche la ligne du dessus"
    ctext(bas, "Vitrine créée par NEBULA Agency", arb(30), MUTED)
    return img, modules


def lire(im):
    """Décode avec DEUX lecteurs indépendants ; renvoie ce que chacun lit."""
    import cv2
    from pyzbar import pyzbar
    a = np.array(im.convert("RGB"))[:, :, ::-1]
    lu_cv, _, _ = cv2.QRCodeDetector().detectAndDecode(a)
    lu_zb = [s.data.decode("utf-8") for s in pyzbar.decode(im.convert("L"))]
    return lu_cv, lu_zb


def planche(maitre):
    """Six carrés de 90 mm sur A4 (210 x 297), traits de coupe HORS de la grille.

    ⚠️ 90 mm et pas 95 : trois carrés de 95 mm + 2 gouttières font 293 mm, soit 2 mm de marge
    en haut et en bas, or une imprimante de bureau n'imprime pas à moins de 4-5 mm du bord.
    Les carrés du haut et du bas sortaient rognés. À 90 mm il reste 9,5 mm.
    ⚠️ Les traits vivent dans la marge de la feuille, jamais dans une gouttière : là, le trait
    d'un carré mordait sur son voisin.
    """
    dpi = 300; mm = dpi / 25.4
    W, H = round(210 * mm), round(297 * mm)
    cote = round(90 * mm); gout = round(4 * mm)
    feuille = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(feuille)
    petit = maitre.resize((cote, cote), Image.LANCZOS)
    larg, haut = 2 * cote + gout, 3 * cote + 2 * gout
    ox, oy = (W - larg) // 2, (H - haut) // 2
    assert min(ox, oy) >= 5 * mm, "une marge sous 5 mm : l'imprimante rognerait"
    xs = [ox + c * (cote + gout) + k * cote for c in range(2) for k in (0, 1)]
    ys = [oy + l * (cote + gout) + k * cote for l in range(3) for k in (0, 1)]
    for l in range(3):
        for c in range(2):
            feuille.paste(petit, (ox + c * (cote + gout), oy + l * (cote + gout)))
    ecart, trait, gris = round(1.5 * mm), round(3 * mm), (110, 110, 110)
    for x in xs:                                   # coupes verticales : au-dessus et au-dessous
        d.line([(x, oy - ecart), (x, oy - ecart - trait)], fill=gris, width=2)
        d.line([(x, oy + haut + ecart), (x, oy + haut + ecart + trait)], fill=gris, width=2)
    for y in ys:                                   # coupes horizontales : à gauche et à droite
        d.line([(ox - ecart, y), (ox - ecart - trait, y)], fill=gris, width=2)
        d.line([(ox + larg + ecart, y), (ox + larg + ecart + trait, y)], fill=gris, width=2)
    return feuille, petit


def main():
    img, modules = carre()
    png = os.path.join(DOCS, "Affiche_Table_Au_Braise_dOr_20cm.png")
    pdf = os.path.join(DOCS, "Affiche_Table_Au_Braise_dOr_20cm.pdf")
    img.save(png, "PNG", optimize=True)
    img.save(pdf, "PDF", resolution=300.0)

    feuille, petit = planche(img)
    pl = os.path.join(DOCS, "Planche_A4_6_carres_Au_Braise_dOr.pdf")
    feuille.save(pl, "PDF", resolution=300.0)

    # ---- relecture : à pleine taille, puis comme un téléphone voit un carré de 9 cm ----
    echecs = 0
    for nom, im in (("carré 20 cm", img), ("carré 9 cm (planche)", petit),
                    ("vu de loin, 600 px", img.resize((600, 600), Image.LANCZOS))):
        cv, zb = lire(im)
        ok = cv == SITE and zb == [SITE]
        echecs += not ok
        print(f"  {'OK ' if ok else 'ÉCHEC'}  {nom:<24} cv2={cv!r}  zbar={zb!r}")
    for p in (png, pdf, pl):
        print(f"  {os.path.basename(p):<44} {os.path.getsize(p) / 1024:.0f} Ko")
    print(f"  QR : {modules} modules, correction H, cible {SITE}")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())

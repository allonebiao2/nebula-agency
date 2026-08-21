#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Affiche de recrutement NEBULA — **variante « équipe »**.

Même affiche que `_build_affiche.py`, à trois choses près : le QR mène au
WhatsApp du responsable qui constitue son équipe, le numéro affiché est le
sien, et le geste demandé est d'écrire, pas de remplir un formulaire.

    cd _documents/nebula-agency/vente && python3 _build_affiche_equipe.py

Produit deux formats :
    assets/Affiche-Recrutement-EQUIPE-A4.pdf   (impression)
    assets/Affiche-Recrutement-EQUIPE-A4.png   (2480 x 3508, 300 dpi)
    assets/Affiche-Recrutement-EQUIPE-9x16.png (1080 x 1920, statut WhatsApp)

⚠️ On ne touche pas à `_affiche_recrutement_src.html` : c'est l'affiche de
   l'agence. On y substitue le contact après coup.
⚠️ Le QR est **relu dans le rendu final** avant d'autoriser l'écriture.
   Un QR mort, c'est l'impression entière perdue.
"""

import base64
import pathlib
import subprocess
import sys

import _build_affiche as base   # on réutilise étoiles(), places(), b64(), CHROME

ICI = pathlib.Path(__file__).resolve().parent
SRC = ICI / "_affiche_recrutement_src.html"
ASSETS = ICI / "assets"

# ══════════════════════════════════════════════════════════════════════
# LE CONTACT DE CETTE VARIANTE
# ══════════════════════════════════════════════════════════════════════
URL_QR = "https://wa.me/2290196555565"
TEL_AFFICHE = "01 96 55 55 65"
# ⚠️ Le Bénin est passé de 8 à 10 chiffres. Si le lien n'ouvre pas la bonne
#    conversation, essayer "https://wa.me/22996555565" et regénérer.
# ══════════════════════════════════════════════════════════════════════

# Ce qu'on remplace dans la source de l'agence, texte pour texte
CONTACT = [
    ("<u>WhatsApp +229 96 74 07 32</u>", f"<u>WhatsApp {TEL_AFFICHE}</u>"),
    ("<b>Scannez pour postuler</b>", "<b>Scannez pour écrire</b>"),
    ("<span>5 minutes suffisent · aucun quota</span>",
     "<span>Écrivez PARTENAIRE · aucun quota</span>"),
]

# Le 9:16 doit tenir dans la BANDE SÛRE de WhatsApp : les 220 px du haut sont
# couverts par la barre de profil, les 340 px du bas par le champ « Répondre ».
# La page est donc agrandie en mm (213.75 x 380, ratio 0.5625) pour que le
# contenu, dont les tailles sont en mm, se retrouve proportionnellement plus
# petit et rentre entre les deux bandes.
#   220 px sur 1920 → 43.5 mm en haut · 340 px → 67.3 mm en bas. On prend un
#   peu plus des deux côtés.
CSS_9X16 = """
<style>
  @page{size:213.75mm 380mm;margin:0}
  html,body,.page{width:213.75mm !important;height:380mm !important}
  .in{padding:46mm 24mm 70mm !important}
</style>
</head>"""

# Bande sûre WhatsApp, en pixels de l'image finale (1080 x 1920)
ZONES_MORTES = {"haut": 220, "bas": 340, "hauteur": 1920}


def assembler(css_extra: str = "") -> str:
    qr = ASSETS / "QR-recrutement-equipe.png"
    import segno
    segno.make(URL_QR, error="h").save(str(qr), scale=20, border=2,
                                       dark="#060713", light="#FFFFFF")

    html = SRC.read_text(encoding="utf-8")
    for vieux, neuf in CONTACT:
        if vieux not in html:
            raise SystemExit(f"⛔ contact introuvable dans la source : {vieux[:40]}")
        html = html.replace(vieux, neuf)

    for marqueur, valeur in {
        "__ARCHIVO__": base.b64(ASSETS / "fonts/archivo.woff2"),
        "__MANROPE__": base.b64(ASSETS / "fonts/manrope.woff2"),
        "__LOGO__": base.b64(base.LOGO),
        "__QR__": base.b64(qr),
        "__STARS__": base.etoiles(),
        "__PLACES__": base.places(),
    }.items():
        if marqueur not in html:
            raise SystemExit(f"⛔ marqueur absent : {marqueur}")
        html = html.replace(marqueur, valeur)

    if css_extra:
        html = html.replace("</head>", css_extra, 1)
    return html


def rendre(html: str, nom: str, largeur_px: int, hauteur_px: int, echelle: float,
           zones=None):
    """Rend une page, contrôle le débordement et les zones mortes, relit le QR."""
    import asyncio

    from playwright.async_api import async_playwright

    tmp = ICI / f"_affiche_equipe_{nom}.html"
    tmp.write_text(html, encoding="utf-8")
    png = ASSETS / f"Affiche-Recrutement-EQUIPE-{nom}.png"

    async def shot():
        async with async_playwright() as pw:
            br = await pw.chromium.launch(executable_path=base.CHROME)
            ctx = await br.new_context(viewport={"width": largeur_px, "height": hauteur_px},
                                       device_scale_factor=echelle)
            pg = await ctx.new_page()
            await pg.goto(tmp.as_uri(), wait_until="networkidle")
            await pg.wait_for_timeout(700)
            mesure = await pg.evaluate("""()=>{
              const p=document.querySelector('.in');
              const enfants=[...p.children].filter(e=>e.getBoundingClientRect().height>0);
              const premier=enfants[0].getBoundingClientRect();
              const dernier=enfants[enfants.length-1].getBoundingClientRect();
              return {h:p.scrollHeight, hp:p.clientHeight, l:p.scrollWidth, lp:p.clientWidth,
                      haut:premier.top, bas:dernier.bottom};}""")
            await pg.screenshot(path=str(png))
            await br.close()
            return mesure

    m = asyncio.run(shot())
    if m["h"] > m["hp"] + 1:
        print(f"  ⛔ {nom} : le contenu déborde de {m['h']-m['hp']} px en hauteur, le pied est coupé")
        return False
    if m["l"] > m["lp"] + 1:
        print(f"  ⛔ {nom} : le contenu déborde de {m['l']-m['lp']} px en largeur")
        return False
    print(f"  {nom} : {m['h']} px de contenu pour {m['hp']} px de page, ça tient")

    if zones:
        haut, bas = m["haut"] * echelle, m["bas"] * echelle
        limite_bas = zones["hauteur"] - zones["bas"]
        if haut < zones["haut"]:
            print(f"  ⛔ {nom} : le contenu commence à {haut:.0f} px, la barre de profil "
                  f"de WhatsApp couvre les {zones['haut']} premiers")
            return False
        if bas > limite_bas:
            print(f"  ⛔ {nom} : le contenu finit à {bas:.0f} px, le champ « Répondre » "
                  f"couvre tout après {limite_bas} px. Le QR serait masqué.")
            return False
        print(f"  {nom} : bande sûre respectée, contenu de {haut:.0f} à {bas:.0f} px "
              f"(autorisé {zones['haut']} à {limite_bas})")

    import cv2
    import numpy as np
    from PIL import Image
    im = Image.open(png)
    W, H = im.size
    det = cv2.QRCodeDetector()
    for etiquette, arr in (("affiche entière", np.array(im.convert("RGB"))),
                           ("recadré sur le pied",
                            np.array(im.crop((0, int(H * .78), W, H)).convert("RGB")))):
        txt, _, _ = det.detectAndDecode(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
        if txt == URL_QR:
            print(f"  ✅ {nom} : QR relu ({etiquette}) → {txt}")
            print(f"     PNG {im.size}, {png.stat().st_size//1024} Ko")
            return True
    print(f"  ⛔ {nom} : LE QR NE SE RELIT PAS DANS LE RENDU, ne pas diffuser")
    return False


def main() -> int:
    ASSETS.mkdir(exist_ok=True)
    print(f"Affiche recrutement · équipe · QR → {URL_QR}")

    # A4, impression
    html_a4 = assembler()
    if not rendre(html_a4, "A4", 794, 1123, 3.125):
        return 1
    pdf = ASSETS / "Affiche-Recrutement-EQUIPE-A4.pdf"
    subprocess.run([base.CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", f"--print-to-pdf={pdf}",
                    "--virtual-time-budget=8000",
                    (ICI / "_affiche_equipe_A4.html").as_uri()],
                   check=True, capture_output=True)
    print(f"  PDF   : {pdf.name}, {pdf.stat().st_size//1024} Ko")

    # 9:16, statut WhatsApp. 213.75 mm = 807.87 px ; 1080 / 807.87 = 1.3368
    html_916 = assembler(CSS_9X16)
    if not rendre(html_916, "9x16", 808, 1436, 1.3366, zones=ZONES_MORTES):
        return 1

    print("\n✓ tout est vert")
    return 0


if __name__ == "__main__":
    sys.exit(main())

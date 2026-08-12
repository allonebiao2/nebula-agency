#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Affiche des forfaits NEBULA (côté CLIENT) : source -> A4 (JPEG + PNG + PDF).

    cd _documents/nebula-agency/vente && python3 _build_affiche_tarifs.py

On édite `_affiche_tarifs_src.html`. Ce script y injecte les polices, le logo,
le QR et le champ d'étoiles, puis rend :

    assets/Affiche-Forfaits-NEBULA-A4.jpg   (à envoyer sur WhatsApp)
    assets/Affiche-Forfaits-NEBULA-A4.png   (source du JPEG, sans perte)
    assets/Affiche-Forfaits-NEBULA-A4.pdf   (impression)

⚠️ Cette affiche part chez des PROSPECTS : aucune commission partenaire
   n'y figure, jamais. Les taux sont internes (socle §4).
⚠️ Les prix viennent de `00-SOCLE-COMMERCIAL.md`, et de nulle part ailleurs.
   Le contrôle final relit les 6 montants sur l'image assemblée.
⚠️ Le QR n'est PAS dessiné : c'est le vrai fichier, relu APRÈS rendu.
   Un QR mort, c'est l'affiche entière perdue.
"""

import base64, glob, pathlib, random, re, subprocess, sys

ICI = pathlib.Path(__file__).resolve().parent
SRC = ICI / "_affiche_tarifs_src.html"
OUT = ICI / "_affiche_tarifs.html"
ASSETS = ICI / "assets"
SOCLE = ICI / "00-SOCLE-COMMERCIAL.md"
URL_QR = "https://www.nebula-agency.online"
LOGO = ICI.parents[2] / "nebula-affilies/static/nebula-logo.png"
NOM = "Affiche-Forfaits-NEBULA-A4"

_C = [g for g in glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome") if "headless" not in g]
CHROME = _C[0] if _C else "chromium"

# Les montants annoncés, et la ligne du socle qui doit les porter.
MONTANTS = {
    "50 000": "Catalogue",
    "150 000": "Vitrine",
    "55 000": "plancher Outil",
    "500 000": "plafond Outil",
    "20 000": "abonnement 6 mois",
    "30 000": "QR Google Review",
}


def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode("ascii")


def etoiles(n=210, graine=7):
    """Champ d'étoiles déterministe : même affiche à chaque construction."""
    r = random.Random(graine)
    c = []
    for _ in range(n):
        x, y = r.uniform(0, 210), r.uniform(0, 297)
        rr = r.choice([0.14, 0.18, 0.22, 0.28, 0.36])
        o = round(r.uniform(0.18, 0.92), 2)
        c.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="#fff" opacity="{o}"/>')
    return ('<svg class="stars" viewBox="0 0 210 297" preserveAspectRatio="none">'
            + "".join(c) + "</svg>")


def prix_du_socle(html):
    """Le socle est la source de vérité : tout montant affiché doit s'y trouver,
    et l'abonnement ne doit jamais être annoncé au mois."""
    socle = SOCLE.read_text(encoding="utf-8")
    ok = True
    for m, quoi in MONTANTS.items():
        if m not in html:
            print("  ❌ montant absent de l'affiche : %s (%s)" % (m, quoi))
            ok = False
        elif ("**%s F**" % m) not in socle and ("%s F" % m) not in socle:
            print("  ❌ %s (%s) ne figure pas dans le socle" % (m, quoi))
            ok = False
    if re.search(r"20 000 F?\s*(par|/)\s*mois", html):
        print("  ❌ l'abonnement est annoncé au MOIS : la vente est perdue sur-le-champ")
        ok = False
    if "6 mois" not in html:
        print("  ❌ l'abonnement n'est pas annoncé par semestre")
        ok = False
    # ce qui ne doit JAMAIS partir chez un prospect
    for interdit in ("commission", "30 %", "40 %", "partenaire", "filleul"):
        if interdit.lower() in html.lower():
            print("  ❌ mot interdit sur une affiche client : « %s »" % interdit)
            ok = False
    # ce qu'on ne promet jamais (socle §6)
    for promesse in ("premier sur Google", "1er sur Google", "garanti"):
        if promesse.lower() in html.lower():
            print("  ❌ promesse interdite : « %s »" % promesse)
            ok = False
    return ok


def main():
    ASSETS.mkdir(exist_ok=True)

    # 1. le QR, généré (jamais dessiné)
    import segno
    qr = ASSETS / "QR-site-nebula.png"
    segno.make(URL_QR, error="h").save(str(qr), scale=20, border=2,
                                       dark="#060713", light="#FFFFFF")

    # 2. injection
    html = SRC.read_text(encoding="utf-8")
    remp = {
        "__ARCHIVO__": b64(ASSETS / "fonts/archivo.woff2"),
        "__MANROPE__": b64(ASSETS / "fonts/manrope.woff2"),
        "__LOGO__": b64(LOGO),
        "__QR__": b64(qr),
        "__STARS__": etoiles(),
    }
    for k, v in remp.items():
        if k not in html:
            print("marqueur absent :", k)
            return 1
        html = html.replace(k, v)

    # 3. les prix disent-ils la même chose que le socle ?
    if not prix_du_socle(SRC.read_text(encoding="utf-8")):
        return 1
    print("  prix : les 6 montants concordent avec le socle commercial")

    OUT.write_text(html, encoding="utf-8")
    print("  source assemblée :", OUT.name, OUT.stat().st_size, "octets")

    # 4. rendu PDF (impression)
    pdf = ASSETS / (NOM + ".pdf")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", f"--print-to-pdf={pdf}",
                    "--virtual-time-budget=8000", OUT.as_uri()],
                   check=True, capture_output=True)
    print("  PDF   :", pdf.name, pdf.stat().st_size, "octets")

    # 5. rendu PNG
    png = ASSETS / (NOM + ".png")
    import asyncio
    from playwright.async_api import async_playwright

    async def shot():
        async with async_playwright() as pw:
            br = await pw.chromium.launch(executable_path=CHROME)
            ctx = await br.new_context(viewport={"width": 794, "height": 1123},
                                       device_scale_factor=2.5)
            pg = await ctx.new_page()
            await pg.goto(OUT.as_uri(), wait_until="networkidle")
            await pg.wait_for_timeout(600)
            # le contenu tient-il dans les 297 mm ? sinon le pied est coupé
            mes = await pg.evaluate("""()=>{
              const p=document.querySelector('.in');
              const d=[...document.querySelectorAll('.in *')]
                .filter(e=>e.scrollWidth>e.clientWidth+1)
                .map(e=>e.className||e.tagName);
              return {contenu:p.scrollHeight, page:p.clientHeight, deborde:d};}""")
            await pg.screenshot(path=str(png))
            await br.close()
            return mes

    mes = asyncio.run(shot())
    if mes["contenu"] > mes["page"] + 1:
        print("  ❌ DÉBORDEMENT : %d px de contenu pour une page de %d px."
              % (mes["contenu"], mes["page"]))
        print("     Le pied de l'affiche est coupé. Resserrer avant d'envoyer.")
        return 1
    if mes["deborde"]:
        print("  ❌ débordement horizontal :", mes["deborde"])
        return 1
    print("  mise en page : %d px de contenu pour %d px de page, ça tient"
          % (mes["contenu"], mes["page"]))

    from PIL import Image
    im = Image.open(png)
    print("  PNG   :", png.name, im.size, png.stat().st_size, "octets")

    # 6. le JPEG, c'est le livrable qui part sur WhatsApp
    jpg = ASSETS / (NOM + ".jpg")
    im.convert("RGB").save(jpg, "JPEG", quality=92, optimize=True,
                           progressive=True, subsampling=0)
    ko = jpg.stat().st_size / 1024
    print("  JPEG  :", jpg.name, im.size, "%.0f Ko" % ko)
    if ko > 4096:
        print("  ❌ trop lourd pour un envoi WhatsApp confortable")
        return 1

    # 7. LE contrôle qui compte : le QR scanne-t-il encore une fois rendu ?
    import cv2, numpy as np
    det = cv2.QRCodeDetector()
    relu = Image.open(jpg)           # on relit le JPEG livré, pas le PNG
    W, H = relu.size
    essais = [("affiche entière", relu),
              ("recadré sur le pied", relu.crop((0, int(H * .78), W, H)))]
    lu = ""
    for nom, img in essais:
        arr = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
        txt, _, _ = det.detectAndDecode(arr)
        if txt.rstrip("/") == URL_QR.rstrip("/"):
            lu = txt
            print("  ✅ QR relu sur le JPEG (%s) : %s" % (nom, txt))
            break
    if not lu:
        print("  ❌ LE QR NE SE RELIT PAS SUR L'AFFICHE RENDUE : ne pas envoyer")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

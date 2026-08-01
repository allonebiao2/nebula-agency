#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Affiche de recrutement NEBULA — source -> A4 imprimable (PDF + PNG 300 dpi).

    cd _documents/nebula-agency/vente && python3 _build_affiche.py

On édite `_affiche_recrutement_src.html`. Ce script y injecte les polices,
le logo, le QR code et le champ d'étoiles, puis rend :

    assets/Affiche-Recrutement-NEBULA-A4.pdf   (impression)
    assets/Affiche-Recrutement-NEBULA-A4.png   (2480 x 3508, 300 dpi)

⚠️ Le QR n'est PAS dessiné : c'est le vrai fichier, regénéré ici et
   **relu après rendu** pour vérifier qu'il scanne encore une fois imprimé.
   Un QR mort, c'est l'impression entière perdue.
"""

import base64, glob, pathlib, random, subprocess, sys

ICI = pathlib.Path(__file__).resolve().parent
SRC = ICI / "_affiche_recrutement_src.html"
OUT = ICI / "_affiche_recrutement.html"
ASSETS = ICI / "assets"
URL_QR = "https://partenaires.nebula-agency.online/devenir"
LOGO = ICI.parents[2] / "nebula-affilies/static/nebula-logo.png"

_C = [g for g in glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome") if "headless" not in g]
CHROME = _C[0] if _C else "chromium"


def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode("ascii")


def etoiles(n=210, graine=7):
    """Champ d'étoiles déterministe — même affiche à chaque construction."""
    r = random.Random(graine)
    c = []
    for _ in range(n):
        x, y = r.uniform(0, 210), r.uniform(0, 297)
        # plus dense dans la diagonale de la nébuleuse
        rr = r.choice([0.14, 0.18, 0.22, 0.28, 0.36])
        o = round(r.uniform(0.18, 0.92), 2)
        c.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="#fff" opacity="{o}"/>')
    return ('<svg class="stars" viewBox="0 0 210 297" preserveAspectRatio="none">'
            + "".join(c) + "</svg>")


def places(n=8):
    """Les huit portails : identiques, ouverts, aucun marqué comme pris."""
    larg, haut, pas = 150.0, 17.0, 150.0 / n
    hx = []
    for i in range(n):
        cx = pas * (i + 0.5)
        cy = haut / 2
        w, h = 7.0, 8.6
        pts = [(cx, cy - h / 2), (cx + w / 2, cy - h / 4), (cx + w / 2, cy + h / 4),
               (cx, cy + h / 2), (cx - w / 2, cy + h / 4), (cx - w / 2, cy - h / 4)]
        d = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        hx.append(f'<polygon points="{d}" fill="rgba(34,211,238,.07)" '
                  f'stroke="#22D3EE" stroke-width=".38" stroke-linejoin="round"/>')
        hx.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r=".9" fill="#22D3EE" opacity=".55"/>')
    return ('<div class="places"><svg viewBox="0 0 150 17">'
            f'<line x1="2" y1="8.5" x2="148" y2="8.5" stroke="rgba(34,211,238,.22)" stroke-width=".25"/>'
            + "".join(hx) + "</svg></div>")


def main():
    ASSETS.mkdir(exist_ok=True)

    # 1. le QR, généré (jamais dessiné)
    import segno
    qr = ASSETS / "QR-devenir-partenaire.png"
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
        "__PLACES__": places(),
    }
    for k, v in remp.items():
        if k not in html:
            print("marqueur absent :", k)
            return 1
        html = html.replace(k, v)
    OUT.write_text(html, encoding="utf-8")
    print("  source assemblée :", OUT.name, OUT.stat().st_size, "octets")

    # 3. rendu PDF
    pdf = ASSETS / "Affiche-Recrutement-NEBULA-A4.pdf"
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", f"--print-to-pdf={pdf}",
                    "--virtual-time-budget=8000", OUT.as_uri()],
                   check=True, capture_output=True)
    print("  PDF   :", pdf.name, pdf.stat().st_size, "octets")

    # 4. rendu PNG 300 dpi
    png = ASSETS / "Affiche-Recrutement-NEBULA-A4.png"
    import asyncio
    from playwright.async_api import async_playwright

    async def shot():
        async with async_playwright() as pw:
            br = await pw.chromium.launch(executable_path=CHROME)
            ctx = await br.new_context(viewport={"width": 794, "height": 1123},
                                       device_scale_factor=3.125)
            pg = await ctx.new_page()
            await pg.goto(OUT.as_uri(), wait_until="networkidle")
            await pg.wait_for_timeout(600)
            # le contenu tient-il dans les 297 mm ? sinon le pied est coupe
            deb = await pg.evaluate("""()=>{
              const p=document.querySelector('.in');
              return {contenu:p.scrollHeight, page:p.clientHeight};}""")
            await pg.screenshot(path=str(png))
            await br.close()
            return deb

    deb = asyncio.run(shot())
    if deb["contenu"] > deb["page"] + 1:
        print("  ❌ DEBORDEMENT : le contenu fait %d px pour une page de %d px."
              % (deb["contenu"], deb["page"]))
        print("     Le pied de l'affiche est coupe. Resserrer avant d'imprimer.")
        return 1
    print("  mise en page : %d px de contenu pour %d px de page — ca tient"
          % (deb["contenu"], deb["page"]))
    from PIL import Image
    im = Image.open(png)
    print("  PNG   :", png.name, im.size, png.stat().st_size, "octets")

    # 5. LE contrôle qui compte : le QR scanne-t-il encore après rendu ?
    import cv2, numpy as np
    det = cv2.QRCodeDetector()
    W, H = im.size
    essais = [
        ("affiche entiere", np.array(im.convert("RGB"))),
        ("recadre sur le pied", np.array(im.crop((0, int(H * .80), W, H)).convert("RGB"))),
    ]
    lu = ""
    for nom, arr in essais:
        txt, _, _ = det.detectAndDecode(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
        if txt == URL_QR:
            lu = txt
            print("  ✅ QR relu (%s) : %s" % (nom, txt))
            break
    if not lu:
        print("  ❌ LE QR NE SE RELIT PAS SUR L'AFFICHE RENDUE — ne pas imprimer")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

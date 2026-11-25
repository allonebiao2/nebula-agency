# -*- coding: utf-8 -*-
"""Étiquettes de jus d'Au Braisé d'Or, version RECTANGLE (9 × 5,5 cm, en largeur : le tour d'une bouteille).

Mongazi, 26/11/2026 : « donne-moi les formats rectangle ». Même style que la carrée et le médaillon festonné
(`_etiquettes_folk.py`, dont on reprend tous les dessins) : rectangle crème aux coins arrondis, double cadre de la
couleur du fruit, fleurs aux coins ; le médaillon du fruit à gauche, à droite le logo, le nom, le ruban, le goût
et les deux numéros. Aucune date (« pas besoin de date de péremption », 24/11).

    python clients/09-au-braise-dor/_outils/_etiquettes_rectangle.py
Sorties : imprimer/rectangle/ (png 300 DPI, planches A4 de 10, unitaires, aperçu).
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _etiquettes_folk as F  # noqa: E402
import _etiquettes_jus as B  # noqa: E402

OUT = F.OUT / "rectangle"
for d in ("png", "planches"):
    (OUT / d).mkdir(parents=True, exist_ok=True)

W, H = 900, 550              # 1 unité = 0,1 mm (90 × 55 mm)
MX, MY, MR = 208, 275, 132   # le médaillon du fruit, à gauche
DX = 600 - 325               # le bloc de texte (dessiné autour de x = 325) est centré à x = 600


def etiquette(j):
    f, petit, nom, _pt, mention, gout, _c, dessin = j
    fruit, ink, acc = F.PAL[f]
    s = [f'<svg class="lab" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"><defs>{B.DEFS}</defs>',
         f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="44" fill="{F.CREME}"/>',
         f'<rect x="18" y="18" width="{W-36}" height="{H-36}" rx="32" fill="none" stroke="{fruit}" stroke-width="7"/>',
         f'<rect x="32" y="32" width="{W-64}" height="{H-64}" rx="22" fill="none" stroke="{fruit}" stroke-width="3.2" stroke-dasharray="0.1 11" stroke-linecap="round"/>']
    for x, y in [(66, 66), (W - 66, 66), (66, H - 66), (W - 66, H - 66)]:
        s.append(F.fleur(x, y, 14, fruit, acc))
    # le médaillon, son anneau pointillé, le fruit dessiné ; un filet pointillé le sépare du texte
    s += [f'<circle cx="{MX}" cy="{MY}" r="{MR}" fill="#fffaf0" stroke="{fruit}" stroke-width="7"/>',
          f'<circle cx="{MX}" cy="{MY}" r="{MR-13}" fill="none" stroke="{acc}" stroke-width="2.2" stroke-dasharray="0.1 9" stroke-linecap="round"/>',
          f'<svg x="{MX-MR*0.8:.1f}" y="{MY-MR*0.8:.1f}" width="{MR*1.6:.1f}" height="{MR*1.6:.1f}" viewBox="0 0 200 200">{dessin()}</svg>',
          f'<line x1="372" y1="92" x2="372" y2="{H-92}" stroke="{fruit}" stroke-width="3.2" stroke-dasharray="0.1 11" stroke-linecap="round"/>']
    # le bloc de droite (mêmes dessins que la carrée, décalés)
    s += [f'<g transform="translate({DX} 0)">',
          F.mot_symbole(112, 32, 168, "devise", fruit),
          f'<text x="325" y="224" text-anchor="middle" class="petit" fill="{fruit}">{petit.strip()}</text>',
          f'<text x="325" y="304" text-anchor="middle" class="nom" data-max="440" fill="{ink}">{nom}</text>',
          F.ruban(320, mention.upper(), fruit, ink),
          f'<text x="325" y="412" text-anchor="middle" class="gout" data-max="420" fill="{ink}">{gout}</text>',
          f'<text x="325" y="452" text-anchor="middle" class="arcwa" data-max="440" fill="{fruit}">COMMANDES · {F.NUMEROS}</text>',
          "</g></svg>"]
    return "".join(s)


EXTRA = "svg.lab{width:90mm;height:55mm} .nom{font-size:84px} .petit{font-size:21px} .gout{font-size:25px}"


def doc(corps, extra=""):
    return F.doc(corps, EXTRA + extra)


def unitaires():
    return doc("".join(f'<div class="pg">{etiquette(j)}</div>' for j in F.JUS),
               "@page{size:90mm 55mm;margin:0} .pg{width:90mm;height:55mm;page-break-after:always}")


def planche(j):
    return doc(f'<div class="a4"><div class="g">{etiquette(j) * 10}</div><div class="n">Au Braisé d\'Or · étiquette rectangle '
               f'{j[2].title()} · 9 × 5,5 cm · découper en suivant le bord arrondi</div></div>',
               "@page{size:A4;margin:0} .a4{width:210mm;height:297mm;display:flex;flex-direction:column;align-items:center;padding-top:5mm}"
               ".g{display:grid;grid-template-columns:repeat(2,90mm);grid-auto-rows:55mm;gap:2mm}"
               ".n{font:600 7pt Montserrat,sans-serif;color:#999;margin-top:2mm}")


def apercu():
    return doc('<div class="g">' + "".join(etiquette(j) for j in F.JUS) + "</div>",
               "body{background:#2a1a10;padding:8mm} .g{display:grid;grid-template-columns:repeat(2,90mm);gap:7mm}"
               "svg.lab{filter:drop-shadow(0 1.2mm 2mm rgba(0,0,0,.5))}")


if __name__ == "__main__":
    DPI = 300 / 96
    with sync_playwright() as pw:
        nav = pw.chromium.launch()

        def charger(html, w, h, e=1):
            pg = nav.new_page(viewport={"width": w, "height": h}, device_scale_factor=e)
            pg.set_content(html, wait_until="networkidle"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            pg.evaluate(F.AJUSTE); pg.evaluate(F.CENTRE); return pg
        pg = charger(unitaires(), 340, 208)
        pg.pdf(path=str(OUT / "etiquettes-rectangle-unitaires.pdf"), prefer_css_page_size=True, print_background=True); pg.close()
        pg = charger(unitaires(), 340, 208, DPI)
        for i, j in enumerate(F.JUS):
            pg.locator("svg.lab").nth(i).screenshot(path=str(OUT / "png" / f"{j[0]}-rectangle.png"), omit_background=True)
        pg.close()
        for j in F.JUS:
            pg = charger(planche(j), 794, 1123)
            pg.pdf(path=str(OUT / "planches" / f"planche-A4-rectangle-{j[0]}.pdf"), prefer_css_page_size=True, print_background=True); pg.close()
        pg = charger(apercu(), 800, 900, 1.6)
        pg.screenshot(path=str(OUT / "apercu-rectangle.png"), full_page=True); pg.close()
        nav.close()
    for p in sorted(OUT.rglob("*.*")):
        print(f"{p.relative_to(OUT)}  {p.stat().st_size // 1024} Ko")

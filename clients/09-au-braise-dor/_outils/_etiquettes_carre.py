# -*- coding: utf-8 -*-
"""Étiquettes de jus d'Au Braisé d'Or, version CARRÉE (6,5 × 6,5 cm).

Mongazi, 24/11/2026 : « mets ça en format carré aussi ». Même style que le médaillon festonné
(`_etiquettes_folk.py`, dont on reprend tous les dessins) : carré crème aux coins arrondis, double cadre
de la couleur du fruit, fleurs aux coins, rinceaux, médaillon, ruban, deux numéros en bas.

    python clients/09-au-braise-dor/_outils/_etiquettes_carre.py
Sorties : imprimer/carre/ (png 300 DPI, planches A4 de 12, unitaires, aperçu).
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _etiquettes_folk as F  # noqa: E402
import _etiquettes_jus as B  # noqa: E402

OUT = F.OUT / "carre"
for d in ("png", "planches"):
    (OUT / d).mkdir(parents=True, exist_ok=True)

S = 650                      # 1 unité = 0,1 mm (65 × 65 mm)
EY, ER = 262, 78             # médaillon
K = 0.7                      # échelle des rinceaux
TX, TY = 325 - K * 325, EY - K * 372


def etiquette(j):
    f, petit, nom, _pt, mention, gout, _c, dessin = j
    fruit, ink, acc = F.PAL[f]
    r = F.rinceau(fruit, ink, acc)
    s = [f'<svg class="lab" viewBox="0 0 {S} {S}" xmlns="http://www.w3.org/2000/svg"><defs>{B.DEFS}</defs>',
         f'<rect x="2" y="2" width="{S-4}" height="{S-4}" rx="46" fill="{F.CREME}"/>',
         f'<rect x="18" y="18" width="{S-36}" height="{S-36}" rx="34" fill="none" stroke="{fruit}" stroke-width="7"/>',
         f'<rect x="32" y="32" width="{S-64}" height="{S-64}" rx="24" fill="none" stroke="{fruit}" stroke-width="3.2" stroke-dasharray="0.1 11" stroke-linecap="round"/>']
    for x, y in [(66, 66), (S - 66, 66), (66, S - 66), (S - 66, S - 66)]:
        s.append(F.fleur(x, y, 15, fruit, acc))
    s += [F.mot_symbole(96, 34, 158, "devise", fruit),
          f'<g transform="translate({TX:.1f} {TY:.1f}) scale({K})">{r}</g>',
          f'<g transform="translate({S} 0) scale(-1 1)"><g transform="translate({TX:.1f} {TY:.1f}) scale({K})">{r}</g></g>',
          f'<circle cx="325" cy="{EY}" r="{ER}" fill="#fffaf0" stroke="{fruit}" stroke-width="7"/>',
          f'<circle cx="325" cy="{EY}" r="{ER-12}" fill="none" stroke="{acc}" stroke-width="2.2" stroke-dasharray="0.1 9" stroke-linecap="round"/>',
          f'<svg x="{325-ER*0.8:.1f}" y="{EY-ER*0.8:.1f}" width="{ER*1.6:.1f}" height="{ER*1.6:.1f}" viewBox="0 0 200 200">{dessin()}</svg>',
          f'<text x="325" y="372" text-anchor="middle" class="petit" fill="{fruit}">{petit.strip()}</text>',
          f'<text x="325" y="452" text-anchor="middle" class="nom" data-max="470" fill="{ink}">{nom}</text>',
          F.ruban(468, mention.upper(), fruit, ink),
          f'<text x="325" y="560" text-anchor="middle" class="gout" data-max="420" fill="{ink}">{gout}</text>',
          f'<text x="325" y="598" text-anchor="middle" class="arcwa" data-max="470" fill="{fruit}">COMMANDES · {F.NUMEROS}</text>',
          "</svg>"]
    return "".join(s)


EXTRA = "svg.lab{width:65mm;height:65mm} .nom{font-size:84px} .petit{font-size:21px} .gout{font-size:25px}"


def doc(corps, extra=""):
    return F.doc(corps, EXTRA + extra)


def unitaires():
    return doc("".join(f'<div class="pg">{etiquette(j)}</div>' for j in F.JUS),
               "@page{size:65mm 65mm;margin:0} .pg{width:65mm;height:65mm;page-break-after:always}")


def planche(j):
    return doc(f'<div class="a4"><div class="g">{etiquette(j) * 12}</div><div class="n">Au Braisé d\'Or · étiquette carrée '
               f'{j[2].title()} · 6,5 × 6,5 cm · découper en suivant le bord arrondi</div></div>',
               "@page{size:A4;margin:0} .a4{width:210mm;height:297mm;display:flex;flex-direction:column;align-items:center;padding-top:10mm}"
               ".g{display:grid;grid-template-columns:repeat(3,65mm);grid-auto-rows:65mm;gap:2mm}"
               ".n{font:600 7pt Montserrat,sans-serif;color:#999;margin-top:3mm}")


def apercu():
    return doc('<div class="g">' + "".join(etiquette(j) for j in F.JUS) + "</div>",
               "body{background:#2a1a10;padding:8mm} .g{display:grid;grid-template-columns:repeat(3,65mm);gap:7mm}"
               "svg.lab{filter:drop-shadow(0 1.2mm 2mm rgba(0,0,0,.5))}")


if __name__ == "__main__":
    DPI = 300 / 96
    with sync_playwright() as pw:
        nav = pw.chromium.launch()

        def charger(html, w, h, e=1):
            pg = nav.new_page(viewport={"width": w, "height": h}, device_scale_factor=e)
            pg.set_content(html, wait_until="networkidle"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            pg.evaluate(F.AJUSTE); pg.evaluate(F.CENTRE); return pg
        pg = charger(unitaires(), 246, 246)
        pg.pdf(path=str(OUT / "etiquettes-carrees-unitaires.pdf"), prefer_css_page_size=True, print_background=True); pg.close()
        pg = charger(unitaires(), 246, 246, DPI)
        for i, j in enumerate(F.JUS):
            pg.locator("svg.lab").nth(i).screenshot(path=str(OUT / "png" / f"{j[0]}-carre.png"), omit_background=True)
        pg.close()
        for j in F.JUS:
            pg = charger(planche(j), 794, 1123)
            pg.pdf(path=str(OUT / "planches" / f"planche-A4-carre-{j[0]}.pdf"), prefer_css_page_size=True, print_background=True); pg.close()
        pg = charger(apercu(), 900, 900, 1.6)
        pg.screenshot(path=str(OUT / "apercu-carre.png"), full_page=True); pg.close()
        nav.close()
    for p in sorted(OUT.rglob("*.*")):
        print(f"{p.relative_to(OUT)}  {p.stat().st_size // 1024} Ko")

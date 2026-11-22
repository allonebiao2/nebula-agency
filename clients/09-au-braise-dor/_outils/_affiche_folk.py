# -*- coding: utf-8 -*-
"""Affiche « verre ou chicha cassé » d'Au Braisé d'Or, dans le style des étiquettes de jus v2
(Mongazi, 22/11/2026 : « fais l'affiche dans le même style aussi »).

Même grammaire que `_etiquettes_folk.py` : panneau crème au bord festonné, double cadre plein et pointillé,
marque en arc, médaillon, rameaux fleuris, ruban plié, Fraunces + Montserrat. Le pictogramme d'interdiction
vient de `_etiquettes_jus.py`. A4, vectoriel.

    python clients/09-au-braise-dor/_outils/_affiche_folk.py
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _etiquettes_jus as B   # noqa: E402
import _etiquettes_folk as F  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
W, H = 650, 919                       # A4 (1 unité = 0,323 mm)
ROUGE, ENCRE, OR = "#c8102e", "#4a0617", "#e9a23b"
CREME = F.CREME


def feston_rect(x0, y0, x1, y1, pas=22):
    """Rectangle aux bords en coquille (demi-cercles vers l'extérieur)."""
    def cote(a, b, n):
        return [a + (b - a) * i / n for i in range(1, n + 1)]
    nx, ny = round((x1 - x0) / pas), round((y1 - y0) / pas)
    rx, ry = (x1 - x0) / nx / 2, (y1 - y0) / ny / 2
    d = [f"M{x0} {y0}"]
    d += [f"A{rx:.2f} {rx:.2f} 0 0 1 {x:.2f} {y0}" for x in cote(x0, x1, nx)]
    d += [f"A{ry:.2f} {ry:.2f} 0 0 1 {x1} {y:.2f}" for y in cote(y0, y1, ny)]
    d += [f"A{rx:.2f} {rx:.2f} 0 0 1 {x:.2f} {y1}" for x in cote(x1, x0, nx)]
    d += [f"A{ry:.2f} {ry:.2f} 0 0 1 {x0} {y:.2f}" for y in cote(y1, y0, ny)]
    return " ".join(d) + " Z"


def coin(x, y, sx, sy):
    """Bouquet d'angle : deux feuilles, une fleur, deux points."""
    return (f'<g transform="translate({x} {y}) scale({sx} {sy})">'
            + F.feuille(0, 0, 10, 40, F.VERT) + F.feuille(0, 0, 80, 40, F.VERT2)
            + F.fleur(6, 6, 17, ROUGE, OR)
            + f'<circle cx="52" cy="14" r="4.5" fill="{OR}"/><circle cx="14" cy="52" r="4.5" fill="{OR}"/></g>')


def rameau(x, y, miroir=False):
    s = (F.feuille(0, 0, 200, 46, F.VERT) + F.feuille(0, 0, 150, 40, F.VERT2) + F.feuille(0, 0, 245, 36, F.VERT2)
         + F.fleur(-38, -58, 22, ROUGE, OR) + F.fleur(-44, 46, 15, OR, ENCRE)
         + F.goutte(-70, -6, 180, 22, ROUGE) + f'<circle cx="-12" cy="-70" r="5" fill="{OR}"/><circle cx="-74" cy="30" r="5" fill="{OR}"/>')
    return f'<g transform="translate({x} {y}) scale({-1 if miroir else 1} 1)">{s}</g>'


def affiche():
    my, mr = 468, 138                                   # médaillon
    picto = B.page_affiche().split('<svg viewBox="0 0 400 400" class="picto"', 1)[1].split("</svg>", 1)[0]
    picto = '<svg viewBox="0 0 400 400"' + picto + "</svg>"
    picto = picto.replace("<svg viewBox", f'<svg x="{325-mr*0.86:.1f}" y="{my-mr*0.86:.1f}" width="{mr*1.72:.1f}" height="{mr*1.72:.1f}" viewBox', 1)
    ruban = F.ruban(250, "ATTENTION", ROUGE, ENCRE).replace('class="rub"', 'class="rubA"')
    s = [f'<svg class="a4" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"><defs>{B.DEFS}'
         f'<radialGradient id="fondA" cx=".5" cy=".42" r=".75"><stop offset="0" stop-color="#7a1222"/><stop offset="1" stop-color="#3a0710"/></radialGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#fondA)"/>',
         f'<path d="{feston_rect(24, 24, 626, 895)}" fill="{CREME}"/>',
         f'<rect x="40" y="40" width="570" height="839" rx="14" fill="none" stroke="{ROUGE}" stroke-width="5"/>',
         f'<rect x="51" y="51" width="548" height="817" rx="9" fill="none" stroke="{ROUGE}" stroke-width="2.6" stroke-dasharray="0.1 9" stroke-linecap="round"/>',
         coin(70, 70, 1, 1), coin(580, 70, -1, 1), coin(70, 849, 1, -1), coin(580, 849, -1, -1),
         F.mot_symbole(132, 60, 232, "deviseA", ROUGE),
         ruban,
         rameau(150, my), rameau(500, my, True),
         f'<circle cx="325" cy="{my}" r="{mr}" fill="#fffaf0" stroke="{ROUGE}" stroke-width="10"/>',
         f'<circle cx="325" cy="{my}" r="{mr-17}" fill="none" stroke="{OR}" stroke-width="3" stroke-dasharray="0.1 10" stroke-linecap="round"/>',
         picto,
         f'<text x="325" y="664" text-anchor="middle" class="titre" data-max="540" fill="{ENCRE}">Vous cassez,</text>',
         f'<text x="325" y="734" text-anchor="middle" class="titre" data-max="540" fill="{ROUGE}">vous remboursez.</text>',
         F.socle(760, ROUGE, OR).replace("stroke-width=\"3.5\"", "stroke-width=\"4\""),
         f'<text x="325" y="800" text-anchor="middle" class="corps" data-max="420" fill="{ENCRE}">Verres et chichas sont payés au prix de l\'article.</text>',
         f'<text x="325" y="832" text-anchor="middle" class="merci" data-max="440" fill="{ENCRE}">Merci d\'en prendre soin</text>',
         f'<text x="325" y="857" text-anchor="middle" class="dir" fill="{ROUGE}">LA DIRECTION</text>',
         "</svg>"]
    css = F.CSS + """
@page{size:A4;margin:0} svg.a4{width:210mm;height:297mm;display:block}
.arcA{font:800 46px Fraunces,serif;letter-spacing:3px;font-variation-settings:"opsz" 144}
.deviseA{font:700 17px Montserrat,sans-serif;letter-spacing:9px}
.rubA{font:800 27px Montserrat,sans-serif;letter-spacing:8px}
.titre{font:900 70px Fraunces,serif;font-variation-settings:"opsz" 144}
.corps{font:600 21px Montserrat,sans-serif}
.merci{font:italic 500 27px Fraunces,serif}
.dir{font:800 16px Montserrat,sans-serif;letter-spacing:8px}
"""
    return f'<!doctype html><html lang="fr"><meta charset="utf-8"><style>{css}</style><body>{"".join(s)}</body></html>'


if __name__ == "__main__":
    OUT = B.OUT
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        for e, sortie in [(1, "pdf"), (300 / 96, "png")]:
            pg = nav.new_page(viewport={"width": 794, "height": 1123}, device_scale_factor=e)
            pg.set_content(affiche(), wait_until="networkidle"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            pg.evaluate(F.AJUSTE); pg.evaluate(F.CENTRE)
            if sortie == "pdf":
                pg.pdf(path=str(OUT / "affiche-casse-A4.pdf"), prefer_css_page_size=True, print_background=True)
            else:
                pg.locator("svg.a4").screenshot(path=str(OUT / "affiche-casse-A4.png"))
            pg.close()
        nav.close()
    for n in ("affiche-casse-A4.pdf", "affiche-casse-A4.png"):
        print(n, (OUT / n).stat().st_size // 1024, "Ko")

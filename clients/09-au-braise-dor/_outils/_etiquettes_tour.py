# -*- coding: utf-8 -*-
"""Étiquettes de jus d'Au Braisé d'Or qui font LE TOUR d'une bouteille de 50 cl (rectangle 21 × 7 cm).

Mongazi, 25/11/2026 : « envoie-les moi dans le format rectangle, elle veut le mettre autour de bouteille de 50 cl ».
Maman Djibom veut des étiquettes RECTANGULAIRES (pas carrées). Même style que le carré et le médaillon festonné
(`_etiquettes_folk.py`, dont on reprend les dessins), déroulé à plat :

    [ collage | AU BRAISÉ D'OR · 50 cl | fruit + JUS DE MANGUE (le devant) | COMMANDES · numéros | bord ]

Taille : le tour d'une bouteille ronde de 50 cl (≈ 6,4 cm de diamètre, donc ≈ 20,2 cm) + 8 mm de recouvrement pour
coller, soit 21 cm, sur 7 cm de haut. Les 9 premiers millimètres passent SOUS l'autre bout : rien d'écrit dessus.
Si sa bouteille est différente, mesurer le tour avec une ficelle et relancer avec `--tour 19.5` (en cm) et/ou
`--haut 6` : tout se recalcule.

    python clients/09-au-braise-dor/_outils/_etiquettes_tour.py [--tour 20.2] [--haut 7]
Sorties : imprimer/tour-50cl/ (png 300 DPI, unitaires, planches A4 paysage de 2 par jus, A3 de 5 pour l'imprimeur,
aperçu).
"""
import io
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _etiquettes_folk as F  # noqa: E402
import _etiquettes_jus as B  # noqa: E402

a = sys.argv[1:]
opt = lambda n, d: float(a[a.index(n) + 1]) if n in a else d
TOUR, HAUT = opt("--tour", 20.2), opt("--haut", 7.0)       # cm
RECOUVRE = 0.8                                             # cm, la bande collée sous l'autre bout
L_MM, H_MM = round((TOUR + RECOUVRE) * 10, 1), HAUT * 10
K = H_MM / 70                                              # tout est dessiné pour 7 cm de haut
W, H = round(L_MM * 10 / K), 700                           # 1 unité = 0,1 mm à 7 cm de haut

OUT = F.OUT / "tour-50cl"
for d in ("png", "planches"):
    (OUT / d).mkdir(parents=True, exist_ok=True)

BANDE = 46
A0, A1 = round(RECOUVRE * 100 / K) + 10, W - 30            # la zone visible (le début passe sous la fin)
CX = (A0 + A1) / 2                                         # le milieu du devant
F0, F1 = CX - 470, CX + 470                                # le devant
LC, RC = (A0 + F0) / 2, (F1 + A1) / 2                      # les deux côtés
PW = min(F0 - A0, A1 - F1) - 70                            # largeur utile d'un côté


def fronton(x, y, fruit, acc):
    """Le petit motif fleur + feuilles du médaillon festonné, posé en (x, y)."""
    return f'<g transform="translate({x - 325:.1f} {y - 222:.1f})">{F.fronton(fruit, "", acc)}</g>'


def etiquette(j):
    f, petit, nom, _pt, mention, gout, _c, dessin = j
    fruit, ink, acc = F.PAL[f]
    mx, my, mr = F0 + 225, 350, 178                        # le médaillon du fruit
    tx = F1 - 255                                          # le centre du texte du devant
    s = [f'<svg class="lab" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"><defs>{B.DEFS}</defs>',
         f'<rect width="{W}" height="{H}" fill="{F.CREME}"/>',
         # les deux bandes qui font le tour, en haut et en bas
         f'<rect width="{W}" height="{BANDE}" fill="{fruit}"/><rect y="{H-BANDE}" width="{W}" height="{BANDE}" fill="{fruit}"/>',
         f'<line x1="0" y1="{BANDE/2}" x2="{W}" y2="{BANDE/2}" stroke="{F.CREME}" stroke-width="2.4" stroke-dasharray="0.1 10" stroke-linecap="round"/>',
         f'<line x1="0" y1="{H-BANDE/2}" x2="{W}" y2="{H-BANDE/2}" stroke="{F.CREME}" stroke-width="2.4" stroke-dasharray="0.1 10" stroke-linecap="round"/>',
         f'<line x1="0" y1="{BANDE+12}" x2="{W}" y2="{BANDE+12}" stroke="{fruit}" stroke-width="3"/>',
         f'<line x1="0" y1="{H-BANDE-12}" x2="{W}" y2="{H-BANDE-12}" stroke="{fruit}" stroke-width="3"/>']
    # les séparations du devant, en pointillés, avec une fleur à chaque bout
    for x in (F0, F1):
        s.append(f'<line x1="{x}" y1="120" x2="{x}" y2="{H-120}" stroke="{fruit}" stroke-width="3.2" stroke-dasharray="0.1 11" stroke-linecap="round"/>')
        s += [F.fleur(x, 96, 13, fruit, acc), F.fleur(x, H - 96, 13, fruit, acc)]

    # LE DEVANT : le fruit dans son médaillon, le nom du jus, le ruban, le goût
    s += [f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="#fffaf0" stroke="{fruit}" stroke-width="8"/>',
          f'<circle cx="{mx}" cy="{my}" r="{mr-14}" fill="none" stroke="{acc}" stroke-width="2.4" stroke-dasharray="0.1 9" stroke-linecap="round"/>',
          f'<svg x="{mx-mr*0.8:.1f}" y="{my-mr*0.8:.1f}" width="{mr*1.6:.1f}" height="{mr*1.6:.1f}" viewBox="0 0 200 200">{dessin()}</svg>',
          fronton(tx, 150, fruit, acc),
          f'<text x="{tx}" y="238" text-anchor="middle" class="petit" fill="{fruit}">{petit.strip()}</text>',
          f'<text x="{tx}" y="352" text-anchor="middle" class="nom" data-max="440" fill="{ink}">{nom}</text>',
          f'<g transform="translate({tx - 325} 0)">{F.ruban(376, mention.upper(), fruit, ink)}</g>',
          f'<text x="{tx}" y="512" text-anchor="middle" class="gout" data-max="420" fill="{ink}">{gout}</text>']

    # CÔTÉ GAUCHE : la maison
    s += [fronton(LC, 150, fruit, acc),
          f'<g class="marqueC" data-cx="{LC}">'
          f'<rect x="{-21:.1f}" y="{262-42:.1f}" width="6" height="43" fill="{F.BRAISE_MARQUE}"/>'
          f'<text x="0" y="262" class="motS" style="font-size:58px" fill="{F.ENCRE_MARQUE}">AU BRAISÉ</text>'
          f'<text x="0" y="323" class="motS" style="font-size:58px" fill="{F.BRAISE_MARQUE}">D\'OR</text></g>',
          f'<text x="{LC}" y="372" text-anchor="middle" class="devise" data-max="{PW}" fill="{fruit}">DE PARIS À COTONOU</text>',
          f'<rect x="{LC-92}" y="412" width="184" height="74" rx="37" fill="none" stroke="{fruit}" stroke-width="5"/>',
          f'<text x="{LC}" y="466" text-anchor="middle" class="cl" fill="{ink}">50 cl</text>',
          f'<text x="{LC}" y="556" text-anchor="middle" class="agite" data-max="{PW}" fill="{ink}">Bien agiter avant de servir</text>']

    # CÔTÉ DROIT : pour commander
    s += [f'<text x="{RC}" y="168" text-anchor="middle" class="tit" fill="{fruit}">COMMANDES</text>',
          f'<text x="{RC}" y="250" text-anchor="middle" class="num" data-max="{PW}" fill="{ink}">01 56 05 71 57</text>',
          f'<text x="{RC}" y="322" text-anchor="middle" class="num" data-max="{PW}" fill="{ink}">01 43 99 29 29</text>',
          f'<line x1="{RC-120}" y1="368" x2="{RC+120}" y2="368" stroke="{fruit}" stroke-width="3" stroke-dasharray="0.1 10" stroke-linecap="round"/>',
          f'<text x="{RC}" y="428" text-anchor="middle" class="srv" data-max="{PW}" fill="{ink}">Grillades au feu de bois</text>',
          f'<text x="{RC}" y="470" text-anchor="middle" class="srv" data-max="{PW}" fill="{ink}">Traiteur · Place des fêtes</text>',
          f'<text x="{RC}" y="552" text-anchor="middle" class="site" data-max="{PW}" fill="{fruit}">aubraisedor.com</text>',
          "</svg>"]
    return "".join(s)


EXTRA = (f"svg.lab{{width:{L_MM}mm;height:{H_MM}mm}} .nom{{font-size:118px}} .petit{{font-size:24px}} .gout{{font-size:31px}}"
         ".devise{font-size:17px;letter-spacing:6px} .tit{font-size:24px;letter-spacing:7px}"
         ".cl{font:900 44px Fraunces,serif;font-variation-settings:'opsz' 144}"
         ".agite{font:italic 500 25px Fraunces,serif}"
         ".num{font:800 44px Montserrat,sans-serif;letter-spacing:1px}"
         ".srv{font:600 23px Montserrat,sans-serif}"
         ".site{font:800 25px Montserrat,sans-serif;letter-spacing:1.5px}")

CENTRE = """() => { for (const g of document.querySelectorAll('g.marqueC')) {
  const b = g.getBBox(); g.setAttribute('transform', `translate(${+g.dataset.cx - (b.x + b.width / 2)} 0)`); } }"""


def doc(corps, extra=""):
    return F.doc(corps, EXTRA + extra)


def unitaires():
    return doc("".join(f'<div class="pg">{etiquette(j)}</div>' for j in F.JUS),
               f"@page{{size:{L_MM}mm {H_MM}mm;margin:0}} .pg{{width:{L_MM}mm;height:{H_MM}mm;page-break-after:always}}")


def note(j, n):
    return (f'<div class="n">Au Braisé d\'Or · {j[1].strip()} {j[2].title()} · {L_MM/10:g} × {H_MM/10:g} cm, fait le tour d\'une '
            f'bouteille de 50 cl · découper sur le trait gris · le bout gauche (sans texte) passe sous le bout droit</div>')


PLANCHE = ("@page{{size:{p};margin:0}} .pg{{width:{w};height:{h};display:flex;flex-direction:column;align-items:center;"
           "justify-content:center;gap:{g};page-break-after:always}} .pg svg.lab{{outline:.15mm solid #b9b9b9}}"
           ".n{{font:600 7pt Montserrat,sans-serif;color:#999}}")


def planche_a4(j):
    return doc(f'<div class="pg">{etiquette(j) * 2}{note(j, 2)}</div>',
               PLANCHE.format(p="A4 landscape", w="297mm", h="210mm", g="5mm"))


def planches_a3():
    n = int((400 - 10) // (H_MM + 4))
    return doc("".join(f'<div class="pg">{etiquette(j) * n}{note(j, n)}</div>' for j in F.JUS),
               PLANCHE.format(p="A3", w="297mm", h="420mm", g="4mm"))


def apercu():
    return doc('<div class="g">' + "".join(etiquette(j) for j in F.JUS) + "</div>",
               "body{background:#2a1a10;padding:8mm} .g{display:grid;grid-template-columns:repeat(2,auto);gap:6mm}"
               "svg.lab{filter:drop-shadow(0 1.2mm 2mm rgba(0,0,0,.5))}")


def polices_embarquees(textes):
    """Les polices DANS le fichier : Fraunces et Montserrat (sous-ensembles latins de Google Fonts, en base64) et
    Segoe UI Black (fsType 8 : intégration permise), réduite aux seules lettres du mot-symbole."""
    import base64, urllib.request
    from fontTools import subset
    from fontTools.ttLib import TTFont
    ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"}
    url = re.search(r"@import url\('([^']+)'\)", F.CSS).group(1)
    css = urllib.request.urlopen(urllib.request.Request(url, headers=ua), timeout=30).read().decode()
    blocs = []
    for sub, bloc in re.findall(r"/\* ([\w-]+) \*/\s*(@font-face\s*\{[^}]+\})", css):
        if sub not in ("latin", "latin-ext"):
            continue
        u = re.search(r"url\((https://[^)]+)\)", bloc).group(1)
        b = base64.b64encode(urllib.request.urlopen(urllib.request.Request(u, headers=ua), timeout=30).read()).decode()
        blocs.append(bloc.replace(f"url({u})", f"url(data:font/woff2;base64,{b})"))
    f = TTFont(r"C:\Windows\Fonts\seguibl.ttf")
    o = subset.Options(); o.flavor = "woff2"; o.name_IDs = []
    sb = subset.Subsetter(o); sb.populate(text=textes); sb.subset(f)
    tampon = io.BytesIO(); f.flavor = "woff2"; f.save(tampon)
    blocs.append("@font-face{font-family:'Segoe UI Black';font-weight:900;src:url(data:font/woff2;base64,"
                 + base64.b64encode(tampon.getvalue()).decode() + ")}")
    return "\n".join(blocs)


def en_svg(nav, charger):
    """Mongazi, 26/11 : « elle imprime chez elle, il faut même que ce soit du SVG pour que la qualité reste ».
    Les SVG sont pris DANS la page, après les ajustements : tout reste vectoriel (dégradés compris) et les polices
    voyagent dans le fichier. ⚠️ Ne pas les tirer du PDF avec PyMuPDF : il change les dégradés des fruits en petites
    images de 73 px, floues à l'impression (essayé le 26/11). S'ouvrent et s'impriment dans Chrome, Edge ou Safari,
    à 100 %. Plus un PDF A4 unique de toutes les planches (impression maison)."""
    import pymupdf
    S = OUT / "svg"
    for d in ("etiquette-seule", "planche-A4"):
        (S / d).mkdir(parents=True, exist_ok=True)
    pg = charger(unitaires(), 900, 400)
    labs = pg.evaluate("() => [...document.querySelectorAll('svg.lab')].map(s => s.outerHTML)"); pg.close()
    css = re.sub(r"@import url\([^)]+\);", "", F.CSS + EXTRA)
    css = re.sub(r"svg\.lab\{[^}]*\}", "", css)
    style = "<style>" + polices_embarquees("AU BRAISÉD'O") + css + "</style>"
    ns = 'xmlns="http://www.w3.org/2000/svg"'

    def nu(lab, x=0, y=0):
        lab = lab.replace(' class="lab"', "").replace(f" {ns}", "")
        return lab.replace("<svg ", f'<svg x="{x}" y="{y}" width="{W}" height="{H}" ', 1)
    for j, lab in zip(F.JUS, labs):
        (S / "etiquette-seule" / f"{j[0]}-tour-50cl-{L_MM/10:g}x{H_MM/10:g}cm.svg").write_text(
            f'<svg {ns} width="{L_MM:g}mm" height="{H_MM:g}mm" viewBox="0 0 {W} {H}">{style}{nu(lab)}</svg>', encoding="utf-8")
        k = 10 / K                                         # unités de l'étiquette par mm
        PW_, PH_ = 297 * k, 210 * k
        x0, ys = (PW_ - W) / 2, [(PH_ - 2 * H - 50 * k / 10) / 2, (PH_ - 2 * H - 50 * k / 10) / 2 + H + 50 * k / 10]
        cadres = "".join(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{W}" height="{H}" fill="none" stroke="#b9b9b9" stroke-width="{1.5*k/10:.2f}"/>' for y in ys)
        txt = (f'<text x="{PW_/2:.1f}" y="{ys[1] + H + 60*k/10:.1f}" text-anchor="middle" '
               f'style="font:600 {25*k/10:.1f}px Montserrat,sans-serif" fill="#999">Au Braisé d\'Or · {j[1].strip()} {j[2].title()} · '
               f'{L_MM/10:g} × {H_MM/10:g} cm · imprimer à 100 % (taille réelle) · découper sur le trait gris</text>')
        (S / "planche-A4" / f"planche-A4-{j[0]}.svg").write_text(
            f'<svg {ns} width="297mm" height="210mm" viewBox="0 0 {PW_:.1f} {PH_:.1f}">{style}'
            f'<rect width="{PW_:.1f}" height="{PH_:.1f}" fill="#fff"/>'
            + "".join(nu(lab, f"{x0:.1f}", f"{y:.1f}") for y in ys) + cadres + txt + "</svg>", encoding="utf-8")
    tout = pymupdf.open()
    for j in F.JUS:
        tout.insert_pdf(pymupdf.open(OUT / "planches" / f"planche-A4-tour-50cl-{j[0]}.pdf"))
    tout.save(OUT / "planches-A4-tour-50cl-maison.pdf", garbage=3, deflate=True)


def ouvrir(pw):
    nav = pw.chromium.launch()

    def charger(html, w, h, e=1):
        pg = nav.new_page(viewport={"width": w, "height": h}, device_scale_factor=e)
        pg.set_content(html, wait_until="networkidle"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.evaluate(F.AJUSTE); pg.evaluate(CENTRE); return pg
    return nav, charger


if __name__ == "__main__" and "--svg" in a:
    with sync_playwright() as pw:
        nav, charger = ouvrir(pw); en_svg(nav, charger); nav.close()
    sys.exit()

if __name__ == "__main__":
    DPI = 300 / 96
    px = lambda mm: round(mm / 25.4 * 96)
    with sync_playwright() as pw:
        nav, charger = ouvrir(pw)
        pg = charger(unitaires(), px(L_MM) + 2, px(H_MM) + 2)
        pg.pdf(path=str(OUT / "etiquettes-tour-50cl-unitaires.pdf"), prefer_css_page_size=True, print_background=True); pg.close()
        pg = charger(unitaires(), px(L_MM) + 2, px(H_MM) + 2, DPI)
        for i, j in enumerate(F.JUS):
            pg.locator("svg.lab").nth(i).screenshot(path=str(OUT / "png" / f"{j[0]}-tour-50cl.png"), omit_background=True)
        pg.close()
        for j in F.JUS:
            pg = charger(planche_a4(j), 1123, 794)
            pg.pdf(path=str(OUT / "planches" / f"planche-A4-tour-50cl-{j[0]}.pdf"), prefer_css_page_size=True, print_background=True); pg.close()
        pg = charger(planches_a3(), 1123, 1587)
        pg.pdf(path=str(OUT / "planches-A3-tour-50cl-imprimeur.pdf"), prefer_css_page_size=True, print_background=True); pg.close()
        pg = charger(apercu(), px(L_MM) * 2 + 160, 900, 1.2)
        pg.screenshot(path=str(OUT / "apercu-tour-50cl.png"), full_page=True); pg.close()
        en_svg(nav, charger)
        nav.close()
    print(f"étiquette {L_MM/10:g} × {H_MM/10:g} cm (tour {TOUR:g} cm + {RECOUVRE:g} cm de recouvrement)")
    for p in sorted(OUT.rglob("*.*")):
        print(f"{p.relative_to(OUT)}  {p.stat().st_size // 1024} Ko")

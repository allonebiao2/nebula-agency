# -*- coding: utf-8 -*-
"""Étiquettes de jus d'Au Braisé d'Or, version 2 : « le médaillon festonné ».

Mongazi, 22/11/2026 : « va sur Pinterest, inspire-toi au maximum, il faut que ce soit ultra joli ».
Référence retenue (Pinterest, « 214+ Premium Die Cut Bottle Label Design », l'étiquette ROOT & PRESS) :
une forme DÉCOUPÉE crème au bord festonné, des ornements populaires symétriques (feuilles, fleurs, volutes,
gouttes) dans les couleurs du fruit, le fruit dans un médaillon, la marque écrite EN ARC en haut, la mention
en arc en bas, le nom en grandes capitales à empattements. Ici : une palette par fruit, nos propres dessins.

Tout est en SVG (vectoriel) : PDF nets à toutes les tailles et légers. Les dessins des fruits, la liste des
jus et l'affiche viennent de `_etiquettes_jus.py`.

    python clients/09-au-braise-dor/_outils/_etiquettes_folk.py
"""
import base64, math, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _etiquettes_jus as B  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
OUT = B.OUT
for d in ("png", "planches"):
    (OUT / d).mkdir(parents=True, exist_ok=True)

W, H, CX, CY = 650, 900, 325, 450          # 1 unité = 0,1 mm (65 × 90 mm)
RX, RY = 312, 437                          # le bord festonné
CREME = "#f8efdf"
VERT, VERT2 = "#2f7a3a", "#5aa652"

PAL = {  # couleur du fruit, encre (texte), accent
    "orange": ("#ef7a0c", "#7a3305", "#ffc23d"),
    "mangue": ("#f29a0c", "#73300b", "#e2431a"),
    "ananas": ("#e3a01a", "#634307", "#2b7a3f"),
    "passion": ("#7b2d6e", "#3b1033", "#f59a0c"),
    "pasteque": ("#d1142c", "#690a17", "#2f8a3e"),
    "corossol": ("#3f7f26", "#1d3d11", "#9ccf63"),
    "bissap": ("#a3123a", "#4a0617", "#e44a6e"),
    "gingembre": ("#b8783d", "#55361a", "#e3b062"),
    "carotte-betterave": ("#e2560c", "#5c0a2e", "#8e1a4b"),
    "cocktail": ("#e2364a", "#6b0f1a", "#ffae2e"),
}
GOUT = {"carotte-betterave": ""}
BIENFAITS = ["Riche en vitamine A", "Bon pour la vue et la peau", "Plein d'antioxydants", "Un coup d'énergie naturel"]


def pt(cx, cy, rx, ry, a):
    a = math.radians(a); return cx + rx * math.cos(a), cy + ry * math.sin(a)


def feston(n=40, k=0.034):
    """Le contour découpé : une ellipse aux bords en coquille."""
    d = []
    for i in range(n):
        a0, a1 = i * 360 / n, (i + 1) * 360 / n
        x0, y0 = pt(CX, CY, RX, RY, a0); x1, y1 = pt(CX, CY, RX, RY, a1)
        cx_, cy_ = pt(CX, CY, RX * (1 + 2 * k), RY * (1 + 2 * k * RX / RY), (a0 + a1) / 2)
        d.append((f"M{x0:.1f} {y0:.1f} " if i == 0 else "") + f"Q{cx_:.1f} {cy_:.1f} {x1:.1f} {y1:.1f}")
    return " ".join(d) + " Z"


def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
    y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
    dx = 3 * u * u * (p1[0] - p0[0]) + 6 * u * t * (p2[0] - p1[0]) + 3 * t * t * (p3[0] - p2[0])
    dy = 3 * u * u * (p1[1] - p0[1]) + 6 * u * t * (p2[1] - p1[1]) + 3 * t * t * (p3[1] - p2[1])
    return x, y, math.degrees(math.atan2(dy, dx))


def feuille(x, y, ang, L, c, veine="#ffffff"):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f})"><path d="M0 0 C {L*.3:.1f} {-L*.32:.1f} {L*.75:.1f} {-L*.3:.1f} {L} 0 '
            f'C {L*.75:.1f} {L*.3:.1f} {L*.3:.1f} {L*.32:.1f} 0 0 Z" fill="{c}"/>'
            f'<path d="M{L*.08:.1f} 0 L{L*.85:.1f} 0" stroke="{veine}" stroke-width="1.6" opacity=".45"/></g>')


def fleur(x, y, r, c, coeur):
    s = "".join(f'<ellipse cx="{x + r*.62*math.cos(math.radians(a)):.1f}" cy="{y + r*.62*math.sin(math.radians(a)):.1f}" rx="{r*.52:.1f}" ry="{r*.34:.1f}" '
                f'transform="rotate({a} {x + r*.62*math.cos(math.radians(a)):.1f} {y + r*.62*math.sin(math.radians(a)):.1f})" fill="{c}"/>'
                for a in range(-90, 270, 72))
    return s + f'<circle cx="{x}" cy="{y}" r="{r*.3:.1f}" fill="{coeur}"/>'


def goutte(x, y, ang, L, c):
    return (f'<path transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f})" d="M0 0 C {L*.4:.1f} {-L*.25:.1f} {L*.85:.1f} {-L*.18:.1f} {L} 0 '
            f'C {L*.85:.1f} {L*.18:.1f} {L*.4:.1f} {L*.25:.1f} 0 0 Z" fill="{c}"/>')


def rinceau(fruit, ink, acc):
    """La branche de gauche (la droite est son miroir) : tige, feuilles alternées, fleurs, gouttes, volute."""
    p = [(208, 488), (118, 470), (80, 372), (128, 262)]
    s = [f'<path d="M{p[0][0]} {p[0][1]} C{p[1][0]} {p[1][1]} {p[2][0]} {p[2][1]} {p[3][0]} {p[3][1]}" stroke="{VERT}" stroke-width="5" fill="none" stroke-linecap="round"/>']
    for i, t in enumerate([.16, .32, .48, .64, .8]):
        x, y, a = bezier(*p, t)
        cote = 1 if i % 2 == 0 else -1
        s.append(feuille(x, y, a + cote * 58, 44 - i * 2, VERT2 if i % 2 else VERT))
    # volute qui part vers l'intérieur
    s.append(f'<path d="M150 432 C 176 420 186 396 172 384 C 162 376 150 386 158 394" stroke="{fruit}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    s.append(fleur(128, 256, 26, fruit, acc))
    s.append(fleur(96, 404, 17, acc, ink))
    for x, y, a in [(110, 330, 200), (150, 470, 40), (178, 330, -30)]:
        s.append(goutte(x, y, a, 22, fruit))
    for x, y in [(86, 300), (126, 488), (176, 360)]:
        s.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{acc}"/>')
    return "".join(s)


def fronton(fruit, ink, acc):
    """Le petit motif au-dessus du médaillon."""
    return (feuille(325, 228, -152, 36, VERT) + feuille(325, 228, -28, 36, VERT2)
            + fleur(325, 222, 15, fruit, acc) + f'<circle cx="281" cy="212" r="4.5" fill="{acc}"/><circle cx="369" cy="212" r="4.5" fill="{acc}"/>')


def socle(y, fruit, acc):
    """La volute double sous le ruban."""
    return (f'<path d="M325 {y} C 300 {y-14} 262 {y-12} 246 {y+2} C 236 {y+12} 250 {y+22} 260 {y+12}" stroke="{fruit}" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
            f'<path d="M325 {y} C 350 {y-14} 388 {y-12} 404 {y+2} C 414 {y+12} 400 {y+22} 390 {y+12}" stroke="{fruit}" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
            f'<path d="M325 {y-9} L333 {y} L325 {y+9} L317 {y} Z" fill="{acc}"/>')


def ruban(y, texte, fruit, ink):
    h = 50; x0, x1 = 206, 444
    return (f'<path d="M{x0-28} {y+10} L{x0} {y+10} L{x0} {y+h+10} L{x0-28} {y+h+10} L{x0-15} {y+h/2+10} Z" fill="{ink}"/>'
            f'<path d="M{x1+28} {y+10} L{x1} {y+10} L{x1} {y+h+10} L{x1+28} {y+h+10} L{x1+15} {y+h/2+10} Z" fill="{ink}"/>'
            f'<path d="M{x0} {y+h} L{x0+14} {y+h+10} L{x0+14} {y+h} Z M{x1} {y+h} L{x1-14} {y+h+10} L{x1-14} {y+h} Z" fill="#000" opacity=".35"/>'
            f'<rect x="{x0}" y="{y}" width="{x1-x0}" height="{h}" fill="{fruit}"/>'
            f'<rect x="{x0+6}" y="{y+6}" width="{x1-x0-12}" height="{h-12}" fill="none" stroke="{CREME}" stroke-width="1.4" stroke-dasharray="1 6" stroke-linecap="round"/>'
            f'<text x="325" y="{y+h/2+8}" text-anchor="middle" class="rub" data-max="{x1-x0-22}" fill="{CREME}">{texte}</text>')


def marque(ink, fruit, uid):
    """La marque en arc (un grand cercle, plus plat que le bord) puis la devise, droite, dessous."""
    if B.LOGO_FICHIER:
        b = base64.b64encode(Path(B.LOGO_FICHIER).read_bytes()).decode()
        return f'<image href="data:image/png;base64,{b}" x="190" y="72" width="270" height="128" preserveAspectRatio="xMidYMid meet"/>'
    return (f'<path id="arcH{uid}" d="M25 420 A300 300 0 0 1 625 420" fill="none"/>'
            f'<text class="arc" fill="{ink}"><textPath href="#arcH{uid}" startOffset="50%" text-anchor="middle">AU BRAISÉ D\'OR</textPath></text>'
            f'<text x="325" y="194" text-anchor="middle" class="devise" fill="{fruit}">DE PARIS À COTONOU</text>')


def arc_bas(uid, ry, texte, cls, fill):
    rx = ry * (RX - 36) / (RY - 38) - 6   # suit le pointillé, sans en sortir sur les côtés
    return (f'<path id="{uid}" d="M{CX-rx:.1f} {CY} A{rx:.1f} {ry} 0 0 0 {CX+rx:.1f} {CY}" fill="none"/>'
            f'<text class="{cls}" fill="{fill}"><textPath href="#{uid}" startOffset="50%" text-anchor="middle">{texte}</textPath></text>')


def etiquette(j):
    f, petit, nom, _pt, mention, gout, _c, dessin = j
    fruit, ink, acc = PAL[f]
    be = f == "carotte-betterave"
    uid = f.replace("-", "")
    ey, er = (300, 80) if be else (352, 112)        # médaillon
    s = [f'<svg class="lab" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"><defs>{B.DEFS}</defs>',
         f'<path d="{feston()}" fill="{CREME}"/>',
         f'<ellipse cx="{CX}" cy="{CY}" rx="{RX-22}" ry="{RY-24}" fill="none" stroke="{fruit}" stroke-width="7"/>',
         f'<ellipse cx="{CX}" cy="{CY}" rx="{RX-36}" ry="{RY-38}" fill="none" stroke="{fruit}" stroke-width="3.2" stroke-dasharray="0.1 11" stroke-linecap="round"/>',
         marque(ink, fruit, uid)]
    if not be:
        r = rinceau(fruit, ink, acc)
        s += [f'<g transform="translate(0 -20)">{r}</g>', f'<g transform="translate(650 -20) scale(-1 1)">{r}</g>']
    else:
        s += [feuille(222, ey + 10, 200, 40, VERT), feuille(428, ey + 10, -20, 40, VERT2),
              fleur(206, ey - 34, 16, fruit, acc), fleur(444, ey - 34, 16, fruit, acc),
              f'<circle cx="226" cy="{ey+48}" r="5" fill="{acc}"/><circle cx="424" cy="{ey+48}" r="5" fill="{acc}"/>']
    s += [f'<circle cx="{CX}" cy="{ey}" r="{er}" fill="#fffaf0" stroke="{fruit}" stroke-width="8"/>',
          f'<circle cx="{CX}" cy="{ey}" r="{er-14}" fill="none" stroke="{acc}" stroke-width="2.4" stroke-dasharray="0.1 9" stroke-linecap="round"/>',
          f'<svg x="{CX-er*0.8:.1f}" y="{ey-er*0.8:.1f}" width="{er*1.6:.1f}" height="{er*1.6:.1f}" viewBox="0 0 200 200">{dessin()}</svg>']
    if not be:
        s += [f'<text x="325" y="510" text-anchor="middle" class="petit" fill="{fruit}">{petit.strip()}</text>',
              f'<text x="325" y="590" text-anchor="middle" class="nom" data-max="460" fill="{ink}">{nom}</text>',
              ruban(606, mention.upper(), fruit, ink), socle(682, fruit, acc),
              f'<text x="325" y="730" text-anchor="middle" class="gout" data-max="320" fill="{ink}">{gout}</text>',
              arc_bas(f"b{uid}", 360, "Préparé le ...../..... · Au frais", "arcbas", ink)]
    else:
        l1, l2 = nom.split(" ")
        s += [f'<text x="325" y="414" text-anchor="middle" class="petit" fill="{fruit}">{petit}</text>',
              f'<text x="325" y="466" text-anchor="middle" class="nom2" data-max="420" fill="{ink}">{l1}</text>',
              f'<text x="325" y="516" text-anchor="middle" class="nom2" data-max="420" fill="{acc}">{l2}</text>',
              ruban(530, mention.upper(), fruit, ink),
              f'<text x="325" y="612" text-anchor="middle" class="tit" fill="{fruit}">LES BIENFAITS</text>']
        for i, b in enumerate(["Vitamine A : bon pour la vue et la peau", "Plein d'antioxydants naturels", "Un coup d'énergie, sans sucre ajouté"]):
            s.append(f'<text x="325" y="{640+i*25}" text-anchor="middle" class="bien" data-max="{460 - i*30}" fill="{ink}">{b}</text>')
        s += [f'<text x="325" y="{718}" text-anchor="middle" class="bien" data-max="380" fill="{ink}"><tspan class="tit2" fill="{fruit}">INGRÉDIENTS · </tspan>carotte, betterave</text>',
              arc_bas(f"b{uid}", 342, "Préparé le ...../..... · Au frais", "arcbas", ink)]
    s.append(arc_bas(f"c{uid}", 388, f"COMMANDES WHATSAPP {B.WHATSAPP}", "arcwa", fruit))
    s.append("</svg>")
    return "".join(s)


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,800;0,9..144,900;1,9..144,500&family=Montserrat:wght@600;700;800&display=block');
*{box-sizing:border-box;margin:0;padding:0}
body{-webkit-print-color-adjust:exact;print-color-adjust:exact}
svg.lab{width:65mm;height:90mm;display:block}
.arc{font:800 38px Fraunces,serif;letter-spacing:2px;font-variation-settings:"opsz" 144}
.devise{font:700 15px Montserrat,sans-serif;letter-spacing:7px}
.petit{font:800 23px Montserrat,sans-serif;letter-spacing:9px}
.nom{font:900 98px Fraunces,serif;letter-spacing:1px;font-variation-settings:"opsz" 144}
.nom2{font:900 54px Fraunces,serif;font-variation-settings:"opsz" 144}
.rub{font:800 21px Montserrat,sans-serif;letter-spacing:3px}
.gout{font:italic 500 28px Fraunces,serif}
.arcbas{font:600 16px Montserrat,sans-serif;letter-spacing:.8px}
.arcwa{font:800 16px Montserrat,sans-serif;letter-spacing:2.5px}
.tit{font:800 19px Montserrat,sans-serif;letter-spacing:5px}
.tit2{font:800 17px Montserrat,sans-serif;letter-spacing:2px}
.bien{font:600 19px Montserrat,sans-serif}
"""
AJUSTE = """() => { for (const t of document.querySelectorAll('text[data-max]')) {
  const max = +t.dataset.max; let fs = parseFloat(getComputedStyle(t).fontSize);
  while (t.getComputedTextLength() > max && fs > 10) { fs -= 1; t.style.fontSize = fs + 'px'; } } }"""


def doc(corps, extra=""):
    return f'<!doctype html><html lang="fr"><meta charset="utf-8"><style>{CSS}{extra}</style><body>{corps}</body></html>'


def unitaires():
    return doc("".join(f'<div class="pg">{etiquette(j)}</div>' for j in B.JUS),
               "@page{size:65mm 90mm;margin:0} .pg{width:65mm;height:90mm;page-break-after:always}")


def planche(j):
    return doc(f'<div class="a4"><div class="g">{etiquette(j) * 9}</div><div class="n">Au Braisé d\'Or · étiquette {j[2].title()} · '
               f'6,5 × 9 cm · découper en suivant le bord festonné</div></div>',
               "@page{size:A4;margin:0} .a4{width:210mm;height:297mm;display:flex;flex-direction:column;align-items:center;padding-top:10mm}"
               ".g{display:grid;grid-template-columns:repeat(3,65mm);grid-auto-rows:90mm;gap:2mm}"
               ".n{font:600 7pt Montserrat,sans-serif;color:#999;margin-top:3mm}")


def apercu():
    return doc('<div class="g">' + "".join(etiquette(j) for j in B.JUS) + "</div>",
               "body{background:#2a1a10;padding:8mm} .g{display:grid;grid-template-columns:repeat(5,65mm);gap:7mm}"
               "svg.lab{filter:drop-shadow(0 1.2mm 2mm rgba(0,0,0,.5))}")


if __name__ == "__main__":
    DPI = 300 / 96
    with sync_playwright() as pw:
        nav = pw.chromium.launch()

        def charger(html, w, h, e=1):
            pg = nav.new_page(viewport={"width": w, "height": h}, device_scale_factor=e)
            pg.set_content(html, wait_until="networkidle"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            pg.evaluate(AJUSTE); return pg
        pg = charger(unitaires(), 246, 341)
        pg.pdf(path=str(OUT / "etiquettes-unitaires.pdf"), prefer_css_page_size=True, print_background=True); pg.close()
        pg = charger(unitaires(), 246, 341, DPI)
        for i, j in enumerate(B.JUS):
            pg.locator("svg.lab").nth(i).screenshot(path=str(OUT / "png" / f"{j[0]}.png"), omit_background=True)
        pg.close()
        for j in B.JUS:
            pg = charger(planche(j), 794, 1123)
            pg.pdf(path=str(OUT / "planches" / f"planche-A4-{j[0]}.pdf"), prefer_css_page_size=True, print_background=True); pg.close()
        pg = charger(apercu(), 1400, 900, 1.6)
        pg.screenshot(path=str(OUT / "apercu.png"), full_page=True); pg.close()
        nav.close()
    for p in sorted(list((OUT / "planches").glob("*.pdf")) + [OUT / "etiquettes-unitaires.pdf", OUT / "apercu.png"]):
        print(f"{p.name}  {p.stat().st_size // 1024} Ko")

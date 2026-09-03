# -*- coding: utf-8 -*-
"""Le logo de MON BÉNIN, institutionnel, en SVG et en PNG.

LA MARQUE (2026-08-11, demandée par Mongazi) : **le pays lui-même, rempli du
drapeau**. Le contour du Bénin, la bande verte au guindant, le jaune en haut,
le rouge en bas, et **la ligne des sept cents kilomètres** qui monte de la
Porte du Non-Retour au fleuve Niger, avec le point du kilomètre zéro sur la
côte.

Ce que la ligne apporte, et sans quoi ce logo serait celui de n'importe quel
site béninois : c'est l'instrument du voyage, le même que l'anneau gradué du
site. Elle relie deux lieux réels, elle ne décore pas. Fait vérifié sur les
coordonnées : **tirée droite de la Porte à Malanville, elle tient entièrement
à l'intérieur du pays.**

⚠️ LE DRAPEAU NE SE REDESSINE PAS À VUE. Les trois couleurs sont celles du
fichier officiel de Wikimedia Commons (vert `#008751`, jaune `#fcd116`, rouge
`#e8112d`) et la bande verte occupe **40 %** de la largeur, comme sur le
drapeau (360 sur 900). Un drapeau approximatif sur un logo de pays se voit en
deux secondes.

⚠️ LE TEXTE EST TRACÉ EN COURBES, jamais en `<text>`. Un logo qui dépend
d'une police installée chez le lecteur n'est pas un logo : il change d'allure
d'une machine à l'autre. Ici, Bodoni Moda est converti en chemins avec
fontTools, et le fichier ne dépend plus de rien.

⚠️ LE MOT RESTE MONOCHROME. La couleur vit dans la marque ; « MON BÉNIN » en
trois couleurs ferait une enseigne, pas une signature. C'est aussi ce qui
permet de poser le logo sur l'encre comme sur le papier sans le refaire.

⚠️ LA PETITE MARQUE N'A NI LIGNE NI CONTOUR : à 26 px, un trait de plus est
une rayure. Elle est remplie, donc lisible sur l'encre comme sur le clair, et
c'est pour ça que la barre du site ne doit plus l'inverser en CSS
(`filter: invert(1)` retournait le vert en magenta).

Sort dans `assets/images/logo/` :
  logo.svg              le verrouillage complet, sur noir
  logo-clair.svg        le même, sur fond clair (traits sombres)
  logo-marque.svg       la marque seule, carrée, sur l'encre
  logo-marque-clair.svg la marque seule, fond transparent (barre, page claire)
  favicon.svg           la marque, simplifiée pour 16 px
  logo-*.png            les mêmes en pixels, pour ce qui n'accepte pas le SVG
"""
import io
import math
import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

from _contour import CONTOUR, MALANVILLE, PORTE

ICI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ICI, "assets", "images", "logo")
POLICE = os.path.join(ICI, "assets", "fonts", "bodoni-normal.woff2")

OR = "#c9a24a"          # l'or du site, celui de la jauge
CLAIR = "#f4efe7"
ENCRE = "#0b0a09"

# Le drapeau du Bénin, couleurs officielles.
VERT = "#008751"
JAUNE = "#fcd116"
ROUGE = "#e8112d"
PART_VERTE = 0.40       # 360 / 900 sur le fichier officiel


# ─── le texte, converti en chemins ────────────────────────────────
def chemins(texte, taille, interlettre):
    """Rend `texte` en chemins SVG. Renvoie (chemins, largeur totale)."""
    f = TTFont(POLICE)
    upem = f["head"].unitsPerEm
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]

    ech = taille / float(upem)
    x, sortie = 0.0, []
    for ch in texte:
        if ch == " ":
            x += taille * 0.30 + interlettre
            continue
        nom = cmap.get(ord(ch))
        if not nom:
            continue
        pen = SVGPathPen(gs)
        gs[nom].draw(pen)
        d = pen.getCommands()
        if d:
            sortie.append(
                '<path d="%s" transform="translate(%.2f 0) scale(%.5f -%.5f)"/>'
                % (d, x, ech, ech))
        x += hmtx[nom][0] * ech + interlettre
    return "".join(sortie), max(0.0, x - interlettre)


# ─── le contour du pays, simplifié puis projeté ───────────────────
def _simplifier(pts, eps):
    """Douglas-Peucker. Sans lui, 146 points pour un dessin de 26 px."""
    if len(pts) < 3:
        return pts

    def ecart(p, a, b):
        (x, y), (x1, y1), (x2, y2) = p, a, b
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(x - x1, y - y1)
        t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
        return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))

    dmax, idx = 0.0, 0
    for i in range(1, len(pts) - 1):
        d = ecart(pts[i], pts[0], pts[-1])
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return _simplifier(pts[:idx + 1], eps)[:-1] + _simplifier(pts[idx:], eps)
    return [pts[0], pts[-1]]


def pays_points(cx, cy, hauteur, eps=0.008):
    """Renvoie (points projetés, cadre, projeter(lon, lat)).

    ⚠️ Les longitudes sont multipliées par cos(latitude moyenne). Sans ça le
    pays est trop large de 1,4 % : invisible sur une carte, visible sur un
    logo qu'on compare au vrai contour.
    """
    pts = _simplifier(list(CONTOUR) + [CONTOUR[0]], eps)
    lat_moy = sum(p[1] for p in pts) / len(pts)
    k = math.cos(math.radians(lat_moy))

    xs = [p[0] * k for p in pts]
    ys = [-p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    ech = hauteur / (y1 - y0)
    larg = (x1 - x0) * ech

    def projeter(lon, lat):
        return (cx - larg / 2.0 + (lon * k - x0) * ech,
                cy - hauteur / 2.0 + (-lat - y0) * ech)

    cadre = (cx - larg / 2.0, cy - hauteur / 2.0, larg, hauteur)
    return [projeter(p[0], p[1]) for p in pts], cadre, projeter


def pays(cx, cy, hauteur, eps=0.008):
    """Le même, en chemin SVG."""
    pts, cadre, projeter = pays_points(cx, cy, hauteur, eps)
    d = ["%s%.2f %.2f" % ("M" if i == 0 else "L", x, y)
         for i, (x, y) in enumerate(pts)]
    d.append("Z")
    return " ".join(d), cadre, projeter


# ─── la marque : le pays, le drapeau, la ligne des 700 km ─────────
def marque(cx, cy, hauteur, cle, trait_c=None, ligne=True, eps=0.008,
           epaisseur=1.0):
    d, (bx, by, bw, bh), projeter = pays(cx, cy, hauteur, eps)
    p = ['<defs><clipPath id="%s"><path d="%s"/></clipPath></defs>' % (cle, d)]

    # le drapeau, à l'intérieur du pays : vert au guindant, jaune en haut,
    # rouge en bas. Les rectangles débordent du cadre puis sont découpés.
    vx = bx + bw * PART_VERTE
    p.append('<g clip-path="url(#%s)">' % cle)
    p.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s"/>'
             % (bx - 2, by - 2, bw * PART_VERTE + 2, bh + 4, VERT))
    p.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s"/>'
             % (vx, by - 2, bw - bw * PART_VERTE + 2, bh / 2.0 + 2, JAUNE))
    p.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s"/>'
             % (vx, by + bh / 2.0, bw - bw * PART_VERTE + 2, bh / 2.0 + 2, ROUGE))

    if ligne:
        # LA LIGNE DES SEPT CENTS KILOMÈTRES, de la Porte au fleuve. Elle est
        # tracée dans l'encre : sur le jaune, un trait clair ne se voit pas.
        # ⚠️ Elle est PROLONGÉE au-delà de Malanville et c'est la découpe du
        # pays qui l'arrête : sinon elle s'interrompt au milieu du jaune et
        # a l'air inachevée. Le fleuve EST la frontière, la ligne doit y finir.
        x0, y0 = projeter(*PORTE)
        x1, y1 = projeter(*MALANVILLE)
        xf, yf = x0 + (x1 - x0) * 1.16, y0 + (y1 - y0) * 1.16
        e = hauteur * 0.0085 * epaisseur
        p.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" '
                 'stroke-width="%.2f" stroke-linecap="round" opacity=".9"/>'
                 % (x0, y0, xf, yf, ENCRE, e))
        # les graduations : une par centaine de kilomètres. ⚠️ Courtes et
        # fines : plus longues, l'ensemble devient une arête de poisson.
        ang = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
        for i in range(1, 7):
            t = i / 7.0
            mx, my = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            lg = hauteur * 0.019
            p.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" '
                     'stroke-width="%.2f" stroke-linecap="round" opacity=".85"/>'
                     % (mx - math.cos(ang) * lg / 2, my - math.sin(ang) * lg / 2,
                        mx + math.cos(ang) * lg / 2, my + math.sin(ang) * lg / 2,
                        ENCRE, e * 0.62))
        p.append('</g>')
        # le kilomètre zéro : la Porte, sur le sable. Hors découpe, pour
        # qu'il déborde légèrement sur la mer comme le fait le monument.
        p.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/>'
                 % (x0, y0, hauteur * 0.028, ENCRE))
        p.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/>'
                 % (x0, y0, hauteur * 0.015, OR))
    else:
        p.append('</g>')

    if trait_c:
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.2f" '
                 'stroke-linejoin="round" opacity=".72"/>'
                 % (d, trait_c, hauteur * 0.0062))
    return "".join(p), bw


def svg_verrouillage(fond, trait_c, or_c, nom_fichier, cle):
    """La marque à gauche, MON BÉNIN à droite, sur une seule ligne."""
    H = 200
    m, larg_pays = marque(84.0, 100.0, 152.0, cle, trait_c=trait_c)

    t1, l1 = chemins("MON", 46, 11.0)
    t2, l2 = chemins("BÉNIN", 46, 11.0)
    ecart = 30.0
    xt = 84.0 + larg_pays / 2.0 + 54.0
    largeur = xt + l1 + ecart + l2 + 30

    sous, lsous = chemins("SEPT CENTS KILOMÈTRES", 13.5, 5.6)

    s = []
    s.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.0f %d" '
             'width="%.0f" height="%d" role="img" aria-label="Mon Bénin">'
             % (largeur, H, largeur, H))
    s.append('<title>Mon Bénin</title>')
    if fond:
        s.append('<rect width="%.0f" height="%d" fill="%s"/>' % (largeur, H, fond))
    s.append('<g>' + m + '</g>')
    s.append('<g transform="translate(%.1f 108)" fill="%s" opacity=".82">%s</g>'
             % (xt, trait_c, t1))
    s.append('<g transform="translate(%.1f 108)" fill="%s">%s</g>'
             % (xt + l1 + ecart, trait_c, t2))
    s.append('<g transform="translate(%.1f 140)" fill="%s" opacity=".70">%s</g>'
             % (xt, trait_c, sous))
    s.append('</svg>')
    p = os.path.join(OUT, nom_fichier)
    io.open(p, "w", encoding="utf-8").write("".join(s))
    print("  %-24s %6d o  %.0fx%d" % (nom_fichier, os.path.getsize(p), largeur, H))
    return p


def svg_marque(fond, trait_c, nom_fichier, cle, taille=200, simple=False,
               part=None):
    # ⚠️ Le pays est deux fois plus haut que large : à 26 px dans la barre, un
    # dessin qui ne remplit que 80 % de sa case a l'air d'un timbre perdu.
    # La version sur fond d'encre garde sa marge (icône Apple, elle est cadrée).
    h = taille * (part or (0.80 if simple else 0.86))
    m, _ = marque(taille / 2.0, taille / 2.0, h, cle, trait_c=trait_c,
                  ligne=not simple, eps=0.05 if simple else 0.008)
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
         'width="%d" height="%d" role="img" aria-label="Mon Bénin">'
         % (taille, taille, taille, taille),
         '<title>Mon Bénin</title>']
    if fond:
        s.append('<rect width="%d" height="%d" fill="%s"/>' % (taille, taille, fond))
    s.append(m)
    s.append('</svg>')
    p = os.path.join(OUT, nom_fichier)
    io.open(p, "w", encoding="utf-8").write("".join(s))
    print("  %-24s %6d o" % (nom_fichier, os.path.getsize(p)))
    return p


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("SVG :")
    svg_verrouillage(ENCRE, CLAIR, OR, "logo.svg", "c1")
    svg_verrouillage(None, "#14110d", "#8a6d24", "logo-clair.svg", "c2")
    svg_marque(ENCRE, CLAIR, "logo-marque.svg", "c3")
    # ⚠️ fond TRANSPARENT et AUCUN contour : c'est la version de la barre du
    # site et des pages claires. Le remplissage suffit à la lire partout.
    svg_marque(None, None, "logo-marque-clair.svg", "c4", part=0.96)
    svg_marque(ENCRE, None, "favicon.svg", "c5", taille=64, simple=True,
               part=0.92)

    # les PNG, pour ce qui n'accepte pas le SVG (réseaux, courriel, impression)
    print("\nPNG :")
    try:
        import cairosvg
        for src, larg in [("logo.svg", 1200), ("logo-clair.svg", 1200),
                          ("logo-marque.svg", 512)]:
            d = os.path.join(OUT, src.replace(".svg", ".png"))
            cairosvg.svg2png(url=os.path.join(OUT, src), write_to=d,
                             output_width=larg)
            print("  %-24s %6d o" % (os.path.basename(d), os.path.getsize(d)))
    except Exception as e:
        print("  cairosvg indisponible (%s) : on rend au navigateur "
              "(python _logo_png.py)" % type(e).__name__)

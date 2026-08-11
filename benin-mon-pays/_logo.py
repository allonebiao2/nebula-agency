# -*- coding: utf-8 -*-
"""Le logo de MON BÉNIN, institutionnel, en SVG et en PNG.

LA MARQUE : **l'anneau gradué**, l'instrument du site lui-même. Ce n'est pas
un ornement choisi au hasard — c'est ce que le visiteur a sous les yeux
pendant tout le voyage, gradué en kilomètres depuis l'océan. L'aiguille
pointe vers le haut : le kilomètre zéro, la Porte, la mer.

⚠️ LE TEXTE EST TRACÉ EN COURBES, jamais en `<text>`. Un logo qui dépend
d'une police installée chez le lecteur n'est pas un logo : il change d'allure
d'une machine à l'autre. Ici, Bodoni Moda est converti en chemins avec
fontTools, et le fichier ne dépend plus de rien.

Sort dans `assets/images/logo/` :
  logo.svg            le verrouillage complet, sur noir
  logo-blanc.svg      le même, sur fond clair (traits sombres)
  logo-marque.svg     la marque seule, carrée
  favicon.svg         la marque, simplifiée pour 16 px
  logo-*.png          les mêmes en pixels, pour ce qui n'accepte pas le SVG
"""
import io
import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ICI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ICI, "assets", "images", "logo")
POLICE = os.path.join(ICI, "assets", "fonts", "bodoni-normal.woff2")

OR = "#c9a24a"          # l'or du site, celui de la jauge
CLAIR = "#f4efe7"
ENCRE = "#0b0a09"


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


# ─── la marque : le méridien gradué ───────────────────────────────
# ⚠️ PREMIÈRE VERSION ÉCARTÉE : une aiguille partant du centre, avec un
# point au milieu, se lit comme une HORLOGE. Pour une marque qui parle
# d'un pays traversé, c'est un contresens. Ici la ligne traverse le
# cercle de part en part et le dépasse : c'est un méridien, une route,
# une échelle. Aucune lecture d'heure n'est possible.
def marque(cx, cy, r, trait, couleur_or, couleur_trait, graduations=36,
           aiguille=True):
    import math
    p = []
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="%.2f"/>' % (cx, cy, r, couleur_trait, trait))

    # les graduations, seulement sur les flancs : le haut et le bas sont
    # réservés à la ligne, sinon l'ensemble se referme en cadran
    for i in range(graduations):
        a = (i / float(graduations)) * math.tau - math.pi / 2
        # on saute les 20 degrés autour de la verticale, en haut et en bas
        d = abs(((math.degrees(a) + 90) % 180) - 90)
        if d > 72:
            continue
        lg = r * (0.20 if i % 3 == 0 else 0.11)
        x1, y1 = cx + math.cos(a) * (r + trait * 1.7), cy + math.sin(a) * (r + trait * 1.7)
        x2, y2 = cx + math.cos(a) * (r + trait * 1.7 + lg), cy + math.sin(a) * (r + trait * 1.7 + lg)
        p.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" '
                 'stroke-width="%.2f" stroke-linecap="round" opacity="%s"/>'
                 % (x1, y1, x2, y2, couleur_trait,
                    trait * (1.0 if i % 3 == 0 else .74),
                    "1" if i % 3 == 0 else ".55"))

    # LE MÉRIDIEN : il traverse tout et dépasse. C'est la route, les
    # sept cents kilomètres, du haut vers le bas.
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
             'stroke-width="%.2f" stroke-linecap="round"/>'
             % (cx, cy - r * 1.30, cx, cy + r * 1.30, couleur_trait, trait * 1.5))

    # la part parcourue, en or, sur le méridien lui-même
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
             'stroke-width="%.2f" stroke-linecap="round"/>'
             % (cx, cy - r * 1.30, cx, cy + r * 0.16, couleur_or, trait * 1.5))

    # le point de départ : le kilomètre zéro, la Porte, la mer
    p.append('<circle cx="%.1f" cy="%.1f" r="%.2f" fill="%s"/>'
             % (cx, cy - r * 1.30, trait * 1.55, couleur_or))
    return "".join(p)


def svg_verrouillage(fond, trait_c, or_c, nom_fichier):
    """La marque à gauche, MON BÉNIN à droite, sur une seule ligne."""
    H = 200
    cx, cy, r = 100.0, 100.0, 62.0
    m = marque(cx, cy, r, 3.0, or_c, trait_c)

    t1, l1 = chemins("MON", 46, 11.0)
    t2, l2 = chemins("BÉNIN", 46, 11.0)
    ecart = 30.0
    xt = 208.0
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
    s.append('<g transform="translate(%.1f 108)" fill="%s">%s</g>' % (xt, trait_c, t1))
    s.append('<g transform="translate(%.1f 108)" fill="%s">%s</g>'
             % (xt + l1 + ecart, or_c, t2))
    s.append('<g transform="translate(%.1f 140)" fill="%s" opacity=".78">%s</g>'
             % (xt, trait_c, sous))
    s.append('</svg>')
    p = os.path.join(OUT, nom_fichier)
    io.open(p, "w", encoding="utf-8").write("".join(s))
    print("  %-20s %6d o  %.0fx%d" % (nom_fichier, os.path.getsize(p), largeur, H))
    return p


def svg_marque(fond, trait_c, or_c, nom_fichier, taille=200, simple=False):
    r = taille * 0.34
    c = taille / 2.0
    m = marque(c, c, r, taille * 0.017, or_c, trait_c,
               graduations=12 if simple else 36, aiguille=True)
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
         'width="%d" height="%d" role="img" aria-label="Mon Bénin">' % (taille, taille, taille, taille),
         '<title>Mon Bénin</title>']
    if fond:
        s.append('<rect width="%d" height="%d" fill="%s"/>' % (taille, taille, fond))
    s.append(m)
    s.append('</svg>')
    p = os.path.join(OUT, nom_fichier)
    io.open(p, "w", encoding="utf-8").write("".join(s))
    print("  %-20s %6d o" % (nom_fichier, os.path.getsize(p)))
    return p


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("SVG :")
    svg_verrouillage(ENCRE, CLAIR, OR, "logo.svg")
    svg_verrouillage(None, "#14110d", "#8a6d24", "logo-clair.svg")
    svg_marque(ENCRE, CLAIR, OR, "logo-marque.svg")
    svg_marque(None, "#14110d", "#8a6d24", "logo-marque-clair.svg")
    svg_marque(ENCRE, CLAIR, OR, "favicon.svg", taille=64, simple=True)

    # les PNG, pour ce qui n'accepte pas le SVG (réseaux, courriel, impression)
    print("\nPNG :")
    try:
        import cairosvg
        for src, larg in [("logo.svg", 1200), ("logo-clair.svg", 1200),
                          ("logo-marque.svg", 512)]:
            d = os.path.join(OUT, src.replace(".svg", ".png"))
            cairosvg.svg2png(url=os.path.join(OUT, src), write_to=d,
                             output_width=larg)
            print("  %-20s %6d o" % (os.path.basename(d), os.path.getsize(d)))
    except Exception as e:
        print("  cairosvg indisponible (%s) : on rend avec le navigateur"
              % type(e).__name__)

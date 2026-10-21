# -*- coding: utf-8 -*-
"""MA LETTRE À… · le logo, dessiné en vectoriel (2026-10-21).

    python malettre/_logo.py

LA MARQUE : un cachet de cire dont l'empreinte est « … », les trois points de
« Ma lettre à… ». Le nom est suspendu, la lettre aussi, jusqu'à l'heure dite ;
et trois points, c'est « quelqu'un est en train de t'écrire ». Redessiné d'après
l'essai de Mongazi (`_partage/Sceau de cire rouge brisé.png` : neuf lobes, l'anneau
d'or), mais ⚠️ dans son essai la fissure coupait le point du MILIEU : on lisait
QUATRE points. Ici la fissure passe ENTRE le 2e et le 3e : les trois points restent.

Écrit dans `malettre/logo/` :
  cachet.svg          le cachet entier (la marque)
  cachet-brise.svg    le cachet brisé (le moment où la lettre s'ouvre)
  favicon.svg         la petite marque : points crème, sans or (lisible à 16 px)
Le build de l'accueil reprend `favicon.svg` (onglet + cachet de la barre).
Une GRAINE fixe : le dessin est le même à chaque fois.
"""
import math
import pathlib
import random
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ICI = pathlib.Path(__file__).resolve().parent
SORTIE = ICI / "logo"

VIN, VIN_FONCE, VIN_CLAIR, OR, CREME = "#8c2f39", "#6d1f27", "#b2434e", "#c9a227", "#f4ede0"


def bord_cire(cx, cy, r, lobes=9, amp=.075, graine=7):
    """Le bord d'une flaque de cire : neuf lobes doux, jamais tout à fait réguliers,
    lissés en courbes de Bézier (Catmull-Rom). Rend un chemin SVG fermé."""
    rnd = random.Random(graine)
    n = lobes * 6
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        rr = r * (1 + amp * math.cos(lobes * t + .4) + .018 * math.sin(2 * t + 1.3) + rnd.uniform(-.008, .008))
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
    d = "M%.2f %.2f" % pts[0]
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += "C%.2f %.2f %.2f %.2f %.2f %.2f" % (c1 + c2 + p2)
    return d + "Z"


def cachet(points=VIN_FONCE, anneau=True, relief=True):
    """Le cachet entier, dans un carré 200 × 200, sans fond."""
    bord = bord_cire(100, 100, 76)
    ombre = bord_cire(102.5, 103.5, 76)
    morceaux = []
    if relief:
        morceaux.append('<path d="%s" fill="%s"/>' % (ombre, VIN_FONCE))       # l'épaisseur de la cire
    morceaux.append('<path d="%s" fill="%s"/>' % (bord, VIN))
    if relief:
        # un seul reflet, en haut à gauche du bourrelet
        morceaux.append('<path d="M52 74C57 60 68 49 82 43C74 52 66 61 61 74C58 80 50 81 52 74Z" fill="%s" opacity=".85"/>' % VIN_CLAIR)
    # l'empreinte du sceau, à peine décentrée comme pressée à la main
    morceaux.append('<circle cx="101" cy="99" r="50" fill="%s"/>' % VIN_FONCE)
    morceaux.append('<circle cx="101" cy="100" r="47" fill="%s"/>' % VIN)
    if anneau:
        morceaux.append('<circle cx="101" cy="100" r="43" fill="none" stroke="%s" stroke-width="2.2"/>' % OR)
    for x in (79, 101, 123):
        morceaux.append('<circle cx="%d" cy="100" r="7.5" fill="%s"/>' % (x, points))
        if relief and points == VIN_FONCE:
            # le bas de chaque point accroche la lumière : il est ENFONCÉ dans la cire
            morceaux.append('<path d="M%.1f 104.2A7.5 7.5 0 0 0 %.1f 104.2" fill="none" stroke="%s" stroke-width="1.4" '
                            'stroke-linecap="round" opacity=".8"/>' % (x - 5.3, x + 5.3, VIN_CLAIR))
    return "".join(morceaux)


def svg(corps, fond=None):
    f = '<rect width="200" height="200" fill="%s"/>' % fond if fond else ""
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">%s%s</svg>' % (f, corps)


def brise():
    """Deux moitiés écartées le long d'une fissure en zigzag qui passe ENTRE le
    2e et le 3e point (x ≈ 112), et trois éclats près de la fissure."""
    zz = [(108, 18), (115, 40), (107, 58), (116, 78), (109, 100), (117, 122), (108, 142), (115, 162), (109, 184)]
    gauche = "M0 0L%s L0 200Z" % " L".join("%d %d" % p for p in [(108, 0)] + zz + [(109, 200)])
    droite = "M200 0L%s L200 200Z" % " L".join("%d %d" % p for p in [(108, 0)] + zz + [(109, 200)])
    corps = cachet()
    return ('<defs><clipPath id="g"><path d="%s"/></clipPath><clipPath id="d"><path d="%s"/></clipPath></defs>'
            '<g clip-path="url(#g)" transform="translate(-5 1) rotate(-3 100 100)">%s</g>'
            '<g clip-path="url(#d)" transform="translate(5 -1) rotate(3 100 100)">%s</g>'
            '<path d="M106 10l5 -4 3 5 -5 3z" fill="%s"/><path d="M114 186l4 2 -2 5 -5 -2z" fill="%s"/>'
            '<circle cx="119" cy="17" r="2.2" fill="%s"/>' % (gauche, droite, corps, corps, VIN, VIN_FONCE, VIN))


def main():
    SORTIE.mkdir(exist_ok=True)
    fichiers = {
        "cachet.svg": svg(cachet()),
        "cachet-brise.svg": svg(brise()),
        # la petite marque : points CRÈME (le contraste se lit à 16 px), ni or ni reflet
        "favicon.svg": svg(cachet(points=CREME, anneau=False, relief=False)),
    }
    for nom, contenu in fichiers.items():
        (SORTIE / nom).write_text(contenu, encoding="utf-8")
        print("logo/%-18s %5d octets" % (nom, len(contenu.encode("utf-8"))))


if __name__ == "__main__":
    main()

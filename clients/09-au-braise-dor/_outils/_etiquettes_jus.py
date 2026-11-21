# -*- coding: utf-8 -*-
"""Étiquettes de jus (autocollants de bouteille) + affiche « casse » d'Au Braisé d'Or.

Demande de la patronne, transmise par Mongazi le 22/11/2026 :
- une étiquette par jus : orange, mangue, ananas, passion, pastèque, corossol, bissap, gingembre ;
- le jus bien-être carotte et betterave, avec ses bienfaits et ses ingrédients ;
- le cocktail de fruits ;
- bissap et ananas : naturels, au miel ; tous les autres : 100 % naturels ;
- une affiche « interdit » pour la salle : verre ou chicha cassé = remboursé.

Sorties dans `imprimer/` (jamais dans `assets/docs/`, qui part en ligne avec le site) :
- etiquettes-unitaires.pdf : une étiquette par page, 65 × 90 mm ;
- planches-A4.pdf : une page A4 par jus, 9 étiquettes identiques (papier autocollant) ;
- png/<jus>.png : chaque étiquette à 300 DPI (pour un imprimeur numérique ou WhatsApp) ;
- affiche-casse-A4.pdf + .png ;
- apercu.png : les 10 étiquettes côte à côte.

Le « logo » est le mot-symbole de l'affiche déjà imprimée (Cambria gras, or) : le restaurant n'a pas
de logo officiel en fichier (CONTEXT.md). S'il en arrive un, le poser dans LOGO_FICHIER.

    python clients/09-au-braise-dor/_outils/_etiquettes_jus.py
"""
import base64, math, random, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
CL = Path(__file__).resolve().parent.parent
OUT = CL / "imprimer"; (OUT / "png").mkdir(parents=True, exist_ok=True)
LOGO_FICHIER = None          # ex. CL / "assets/images/logo.png" quand la patronne l'envoie
WHATSAPP = "01 56 05 71 57"  # celui de l'affiche A4 déjà imprimée

# ---------------------------------------------------------------- dessins (viewBox 0 0 200 200)
def P(cx, cy, r, a):
    a = math.radians(a); return cx + r * math.cos(a), cy + r * math.sin(a)

def miel(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M0 -22 C 9 -8 16 2 16 10 A16 16 0 0 1 -16 10 '
            f'C -16 2 -9 -8 0 -22 Z" fill="url(#gMiel)" stroke="#8a5a0b" stroke-width="1.2"/>'
            f'<ellipse cx="-5" cy="6" rx="3.5" ry="6" fill="#fff6c8" opacity=".75"/></g>')

DEFS = """
<radialGradient id="gOr" cx=".45" cy=".4" r=".7"><stop offset="0" stop-color="#ffc94a"/><stop offset="1" stop-color="#f07a0c"/></radialGradient>
<linearGradient id="gMangue" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#e63b0f"/><stop offset=".45" stop-color="#ff9a1f"/><stop offset="1" stop-color="#ffd84a"/></linearGradient>
<radialGradient id="gBlush" cx=".3" cy=".75" r=".5"><stop offset="0" stop-color="#d7261e" stop-opacity=".75"/><stop offset="1" stop-color="#d7261e" stop-opacity="0"/></radialGradient>
<linearGradient id="gAnanas" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffd35a"/><stop offset="1" stop-color="#d9771a"/></linearGradient>
<linearGradient id="gFeuille" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#1f6b3a"/><stop offset="1" stop-color="#5cc06b"/></linearGradient>
<radialGradient id="gPulpe" cx=".5" cy=".5" r=".55"><stop offset="0" stop-color="#ffd23f"/><stop offset="1" stop-color="#ff9500"/></radialGradient>
<radialGradient id="gPassion" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#9b3f86"/><stop offset="1" stop-color="#3e1236"/></radialGradient>
<radialGradient id="gChair" cx=".5" cy=".2" r=".9"><stop offset="0" stop-color="#ff5a6a"/><stop offset="1" stop-color="#d1142c"/></radialGradient>
<linearGradient id="gCoro" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8fd05a"/><stop offset="1" stop-color="#2f6d1f"/></linearGradient>
<radialGradient id="gBissap" cx=".5" cy=".55" r=".6"><stop offset="0" stop-color="#e0274f"/><stop offset="1" stop-color="#5c0a1e"/></radialGradient>
<linearGradient id="gGing" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f0c88c"/><stop offset="1" stop-color="#b9824a"/></linearGradient>
<linearGradient id="gCarotte" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffab3d"/><stop offset="1" stop-color="#e2560c"/></linearGradient>
<radialGradient id="gBett" cx=".35" cy=".35" r=".75"><stop offset="0" stop-color="#c2185b"/><stop offset="1" stop-color="#4a0627"/></radialGradient>
<linearGradient id="gMiel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd76a"/><stop offset="1" stop-color="#e39b12"/></linearGradient>
<linearGradient id="gCocktail" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#c3123a"/><stop offset=".38" stop-color="#ff5d2a"/><stop offset=".7" stop-color="#ffb02e"/><stop offset="1" stop-color="#ffe27a"/></linearGradient>
<linearGradient id="gVerre" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".25" stop-color="#fff" stop-opacity=".08"/><stop offset="1" stop-color="#fff" stop-opacity=".3"/></linearGradient>
"""

def feuille(x, y, rot, s=1.0, fill="url(#gFeuille)"):
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})"><path d="M0 0 C 14 -16 42 -18 58 -4 C 40 12 14 12 0 0 Z" '
            f'fill="{fill}"/><path d="M2 0 C 20 -4 38 -5 54 -4" stroke="#14482a" stroke-width="1.4" fill="none" opacity=".6"/></g>')

def rondelle_orange(cx, cy, r):
    s = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#f28a12"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{r*0.9}" fill="#fff0cc"/>']
    n = 10
    for i in range(n):
        a0, a1 = i * 360 / n + 3.2, (i + 1) * 360 / n - 3.2
        am = (a0 + a1) / 2
        x0, y0 = P(cx, cy, r * 0.09, am); x1, y1 = P(cx, cy, r * 0.83, a0); x2, y2 = P(cx, cy, r * 0.83, a1)
        s.append(f'<path d="M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f} A{r*0.83:.1f} {r*0.83:.1f} 0 0 1 {x2:.1f} {y2:.1f} Z" fill="url(#gOr)"/>')
        jx, jy = P(cx, cy, r * 0.55, am)
        s.append(f'<ellipse cx="{jx:.1f}" cy="{jy:.1f}" rx="{r*0.05:.1f}" ry="{r*0.16:.1f}" transform="rotate({am+90:.1f} {jx:.1f} {jy:.1f})" fill="#fff3c4" opacity=".55"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r*0.07}" fill="#fff0cc"/>')
    return "".join(s)

def d_orange():
    return (feuille(118, 40, -35, 1.1) + f'<circle cx="112" cy="112" r="72" fill="#e8730a"/>'
            '<circle cx="112" cy="112" r="72" fill="url(#gOr)" opacity=".85"/>'
            '<ellipse cx="88" cy="86" rx="18" ry="10" fill="#fff" opacity=".25" transform="rotate(-35 88 86)"/>'
            + rondelle_orange(62, 136, 50))

def d_mangue():
    corps = "M52 160 C 14 120 30 44 104 34 C 168 26 192 92 160 140 C 136 176 86 186 52 160 Z"
    return (f'<path d="{corps}" fill="url(#gMangue)"/><path d="{corps}" fill="url(#gBlush)"/>'
            '<ellipse cx="128" cy="70" rx="22" ry="11" fill="#fff" opacity=".28" transform="rotate(-25 128 70)"/>'
            '<path d="M104 36 C 106 24 110 18 116 14" stroke="#5b3a1a" stroke-width="5" stroke-linecap="round" fill="none"/>'
            + feuille(114, 16, -20, 1.15))

def d_ananas():
    s = ['<clipPath id="cpA"><ellipse cx="100" cy="132" rx="50" ry="60"/></clipPath>',
         '<ellipse cx="100" cy="132" rx="50" ry="60" fill="url(#gAnanas)"/>', '<g clip-path="url(#cpA)">']
    for k in range(-12, 13):
        s.append(f'<line x1="{30+k*15}" y1="60" x2="{30+k*15+150}" y2="210" stroke="#a5520f" stroke-width="2.6" opacity=".7"/>')
        s.append(f'<line x1="{170+k*15}" y1="60" x2="{170+k*15-150}" y2="210" stroke="#a5520f" stroke-width="2.6" opacity=".7"/>')
    s.append('<ellipse cx="80" cy="110" rx="12" ry="28" fill="#fff" opacity=".18"/></g>')
    for ang, L, c in [(-62, 34, "#2b7a3f"), (-40, 48, "#3d9a4f"), (-18, 60, "#2b7a3f"), (0, 70, "#4cb35e"),
                      (18, 60, "#2b7a3f"), (40, 48, "#3d9a4f"), (62, 34, "#2b7a3f")]:
        tx, ty = 100 + L * math.sin(math.radians(ang)), 76 - L * math.cos(math.radians(ang))
        s.append(f'<path d="M{100-7} 78 Q {(100+tx)/2-6:.1f} {(76+ty)/2:.1f} {tx:.1f} {ty:.1f} Q {(100+tx)/2+6:.1f} {(76+ty)/2:.1f} {100+7} 78 Z" fill="{c}"/>')
    s.append(miel(162, 168, .9))
    return "".join(s)

def d_passion():
    rnd = random.Random(7); s = ['<circle cx="100" cy="104" r="78" fill="url(#gPassion)"/>',
                                 '<circle cx="100" cy="104" r="68" fill="#f3e9c6"/>', '<circle cx="100" cy="104" r="61" fill="url(#gPulpe)"/>']
    for _ in range(46):
        r = 52 * math.sqrt(rnd.random()); a = rnd.random() * 360
        x, y = P(100, 104, r, a)
        s.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="6.5" ry="5" fill="#ffe27a" opacity=".85" transform="rotate({a:.0f} {x:.1f} {y:.1f})"/>'
                 f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="3.2" ry="2.4" fill="#2a160c" transform="rotate({a:.0f} {x:.1f} {y:.1f})"/>')
    s.append('<ellipse cx="72" cy="52" rx="20" ry="8" fill="#fff" opacity=".22" transform="rotate(-30 72 52)"/>')
    return "".join(s)

def d_pasteque():
    rnd = random.Random(3); cx, cy = 100, 62
    arc = lambda r: f'M{cx-r} {cy} A{r} {r} 0 0 0 {cx+r} {cy} Z'
    s = [f'<path d="{arc(92)}" fill="#1f7a37"/>', f'<path d="{arc(86)}" fill="#7cc46a"/>',
         f'<path d="{arc(80)}" fill="#eef7d6"/>', f'<path d="{arc(74)}" fill="url(#gChair)"/>']
    for i in range(7):
        a = 24 + i * 22; x, y = P(cx, cy, 44 + (i % 2) * 14, a)
        s.append(f'<path d="M{x:.1f} {y-5:.1f} C {x+4:.1f} {y:.1f} {x+3:.1f} {y+6:.1f} {x:.1f} {y+7:.1f} C {x-3:.1f} {y+6:.1f} {x-4:.1f} {y:.1f} {x:.1f} {y-5:.1f} Z" fill="#1b0f0a" transform="rotate({a-90:.0f} {x:.1f} {y:.1f})"/>')
    s.append(f'<path d="M{cx-74} {cy} L{cx+74} {cy}" stroke="#ff8a96" stroke-width="3" opacity=".6"/>')
    # petit triangle de pastèque devant
    s.append('<g transform="translate(130 128) rotate(14)"><path d="M0 0 L50 0 L25 52 Z" fill="url(#gChair)"/>'
             '<path d="M-3 -6 L53 -6 L50 0 L0 0 Z" fill="#1f7a37"/><path d="M0 0 L50 0 L49 3 L1 3 Z" fill="#eef7d6"/>'
             '<ellipse cx="18" cy="16" rx="2.5" ry="4" fill="#1b0f0a"/><ellipse cx="32" cy="20" rx="2.5" ry="4" fill="#1b0f0a"/></g>')
    return "".join(s)

def d_corossol():
    rnd = random.Random(11)
    corps = "M70 40 C 120 20 172 60 168 118 C 164 168 110 190 74 168 C 36 146 26 64 70 40 Z"
    s = ['<clipPath id="cpC"><path d="' + corps + '"/></clipPath>', f'<path d="{corps}" fill="url(#gCoro)"/>', '<g clip-path="url(#cpC)">']
    for _ in range(70):
        x, y = 30 + rnd.random() * 145, 25 + rnd.random() * 165
        s.append(f'<path d="M{x:.1f} {y:.1f} q 3 -5 7 -6" stroke="#204d14" stroke-width="2.2" stroke-linecap="round" fill="none"/>'
                 f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" fill="#c9ec9a"/>')
    s.append('<ellipse cx="80" cy="70" rx="14" ry="26" fill="#fff" opacity=".16"/></g>')
    s.append('<path d="M86 36 C 84 26 86 18 92 12" stroke="#4b3017" stroke-width="5" stroke-linecap="round" fill="none"/>' + feuille(92, 14, -30, 1.0))
    # morceau coupé : chair blanche, graines noires
    s.append('<g transform="translate(36 150) rotate(-12)"><ellipse cx="0" cy="0" rx="34" ry="24" fill="#3f8a28"/>'
             '<ellipse cx="0" cy="-2" rx="30" ry="20" fill="#fbf8ee"/>'
             + "".join(f'<ellipse cx="{dx}" cy="{dy}" rx="2.6" ry="4.2" fill="#22160f" transform="rotate({r} {dx} {dy})"/>'
                       for dx, dy, r in [(-14, -6, 20), (-2, 4, -15), (11, -8, 35), (16, 6, -10), (-18, 8, 0), (2, -12, 60)])
             + '</g>')
    return "".join(s)

def calice(cx, cy, r, rot):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.42
        pts.append(P(cx, cy, rr, rot + i * 36 - 90))
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    s = f'<path d="{d}" fill="url(#gBissap)" stroke="#3a0612" stroke-width="1.5" stroke-linejoin="round"/>'
    for i in range(5):
        x, y = P(cx, cy, r * 0.88, rot + i * 72 - 90)
        s += f'<path d="M{cx} {cy} L{x:.1f} {y:.1f}" stroke="#ff7a95" stroke-width="1.6" opacity=".55"/>'
    s += f'<circle cx="{cx}" cy="{cy}" r="{r*0.2:.1f}" fill="#7a0a22"/>'
    return s

def hibiscus(cx, cy, r):
    s = ""
    for i in range(5):
        a = i * 72 - 90
        s += (f'<g transform="rotate({a} {cx} {cy})"><path d="M{cx} {cy} C {cx+r*0.25:.1f} {cy-r*0.35:.1f} {cx+r*0.55:.1f} {cy-r*0.62:.1f} {cx+r*0.95:.1f} {cy-r*0.3:.1f} '
              f'C {cx+r*1.1:.1f} {cy+r*0.05:.1f} {cx+r*0.75:.1f} {cy+r*0.42:.1f} {cx} {cy} Z" fill="url(#gBissap)" stroke="#5c0a1e" stroke-width="1.2"/>'
              f'<path d="M{cx} {cy} Q {cx+r*0.5:.1f} {cy-r*0.12:.1f} {cx+r*0.85:.1f} {cy-r*0.12:.1f}" stroke="#ff8aa3" stroke-width="1.4" fill="none" opacity=".55"/></g>')
    s += f'<circle cx="{cx}" cy="{cy}" r="{r*0.2:.1f}" fill="#5c0a1e"/>'
    s += f'<path d="M{cx} {cy} Q {cx+r*0.15:.1f} {cy-r*0.5:.1f} {cx+r*0.42:.1f} {cy-r*0.78:.1f}" stroke="#ffd0dc" stroke-width="3" fill="none" stroke-linecap="round"/>'
    s += "".join(f'<circle cx="{cx+r*(0.42+dx):.1f}" cy="{cy-r*(0.78+dy):.1f}" r="2.6" fill="#ffd23f"/>' for dx, dy in [(0,0),(0.06,0.05),(-0.05,0.06),(0.08,-0.04)])
    return s

def d_bissap():
    return (hibiscus(96, 100, 74) + calice(158, 160, 26, 20) + calice(42, 166, 22, -10) + miel(164, 54, .85))

def d_gingembre():
    corps = ("M24 124 C 22 104 40 94 58 100 C 56 78 74 64 90 74 C 96 52 122 48 130 68 C 146 58 170 68 164 92 "
             "C 182 98 184 124 164 130 C 158 150 132 154 120 142 C 104 156 80 154 72 140 C 52 150 26 144 24 124 Z")
    s = f'<path d="{corps}" fill="url(#gGing)" stroke="#8a5a2b" stroke-width="2.4" stroke-linejoin="round"/>'
    for x, y in [(46, 120), (70, 112), (96, 120), (122, 110), (146, 114), (84, 88), (112, 78), (148, 88)]:
        s += f'<path d="M{x} {y-7} q 5 7 0 14" stroke="#9b6833" stroke-width="2" fill="none" opacity=".75"/>'
    s += '<ellipse cx="70" cy="104" rx="14" ry="5" fill="#fff" opacity=".22" transform="rotate(-20 70 104)"/>'
    s += '<path d="M90 74 q -4 -12 2 -20" stroke="#7cbf5a" stroke-width="3" fill="none" stroke-linecap="round"/>'
    s += ('<g transform="translate(150 170)"><circle r="22" fill="#d9a25c"/><circle r="18.5" fill="#f6dc8c"/>'
          '<circle r="11" fill="none" stroke="#e6bf62" stroke-width="2"/><circle r="5" fill="#e6bf62"/></g>')
    return s

def d_carotte_betterave():
    return ('<g transform="rotate(-28 80 100)">'
            '<path d="M72 46 Q 64 40 58 22" stroke="#2f8a3e" stroke-width="5" stroke-linecap="round" fill="none"/>'
            '<path d="M80 46 Q 80 30 84 14" stroke="#3fa34f" stroke-width="5" stroke-linecap="round" fill="none"/>'
            '<path d="M88 46 Q 96 36 106 24" stroke="#2f8a3e" stroke-width="5" stroke-linecap="round" fill="none"/>'
            '<path d="M58 50 Q 80 40 104 50 Q 96 120 82 186 Q 76 190 72 184 Q 64 120 58 50 Z" fill="url(#gCarotte)"/>'
            '<path d="M66 72 l12 2 M70 100 l14 1 M72 128 l10 1 M74 152 l8 0" stroke="#b9470a" stroke-width="2.4" stroke-linecap="round"/>'
            '</g>'
            '<path d="M136 92 Q 128 60 116 38" stroke="#8e1a4b" stroke-width="4" fill="none"/>'
            '<path d="M142 90 Q 150 58 168 42" stroke="#8e1a4b" stroke-width="4" fill="none"/>'
            + feuille(116, 40, -120, 1.0) + feuille(168, 44, -60, 1.0)
            + '<circle cx="140" cy="128" r="42" fill="url(#gBett)"/>'
            '<path d="M140 170 Q 144 184 152 192" stroke="#4a0627" stroke-width="3" fill="none" stroke-linecap="round"/>'
            '<ellipse cx="124" cy="112" rx="10" ry="16" fill="#fff" opacity=".18"/>')

def d_cocktail():
    verre = "M56 52 L144 52 L134 186 Q 100 194 66 186 Z"
    return ('<clipPath id="cpV"><path d="' + verre + '"/></clipPath>'
            f'<path d="{verre}" fill="url(#gCocktail)"/>'
            '<g clip-path="url(#cpV)">'
            '<rect x="70" y="70" width="24" height="22" rx="4" fill="#fff" opacity=".35" transform="rotate(12 82 81)"/>'
            '<rect x="104" y="92" width="22" height="20" rx="4" fill="#fff" opacity=".3" transform="rotate(-10 115 102)"/>'
            '<circle cx="80" cy="150" r="3" fill="#fff" opacity=".5"/><circle cx="118" cy="164" r="2.5" fill="#fff" opacity=".5"/>'
            '<circle cx="96" cy="128" r="2" fill="#fff" opacity=".5"/></g>'
            f'<path d="{verre}" fill="url(#gVerre)" stroke="#fff" stroke-opacity=".7" stroke-width="2.5"/>'
            '<path d="M118 20 L106 150" stroke="#f5f0e6" stroke-width="7" stroke-linecap="round"/>'
            '<path d="M118 20 L106 150" stroke="#e63946" stroke-width="7" stroke-dasharray="8 8" stroke-linecap="round"/>'
            + rondelle_orange(56, 54, 28)
            + '<g transform="translate(150 60) rotate(30)"><path d="M0 0 L18 -6 L22 14 Z" fill="#ffd23f"/></g>'
            + feuille(146, 44, -150, .7))

# ---------------------------------------------------------------- les jus
JUS = [  # (fichier, petit titre, nom, taille nom pt, mention, goût, couleur, dessin)
    ("orange", "JUS D'", "ORANGE", 24, "100 % naturel", "Vitaminé, plein de soleil", "#ff8a00", d_orange),
    ("mangue", "JUS DE", "MANGUE", 24, "100 % naturel", "Doux et fruité", "#ffb703", d_mangue),
    ("ananas", "JUS D'", "ANANAS", 24, "Naturel · au miel", "Sucré au miel, rien d'autre", "#f4c430", d_ananas),
    ("passion", "JUS DE", "PASSION", 23, "100 % naturel", "Acidulé et parfumé", "#b5459b", d_passion),
    ("pasteque", "JUS DE", "PASTÈQUE", 21, "100 % naturel", "Frais et désaltérant", "#ff3b4e", d_pasteque),
    ("corossol", "JUS DE", "COROSSOL", 21, "100 % naturel", "Doux et onctueux", "#6cc04a", d_corossol),
    ("bissap", "JUS DE", "BISSAP", 24, "Naturel · au miel", "Fleurs d'hibiscus et miel", "#e0274f", d_bissap),
    ("gingembre", "JUS DE", "GINGEMBRE", 19, "100 % naturel", "Relevé, ça réveille !", "#e3b062", d_gingembre),
    ("carotte-betterave", "JUS BIEN-ÊTRE", "CAROTTE BETTERAVE", 15, "100 % naturel", "", "#ff6a1a", d_carotte_betterave),
    ("cocktail", "COCKTAIL DE", "FRUITS", 24, "100 % naturel", "Fruits frais de saison, mélangés", "#ff4d6d", d_cocktail),
]
BIENFAITS = ["Riche en vitamine A : bon pour la vue et la peau",
             "Plein d'antioxydants naturels",
             "Un coup d'énergie, sans sucre ajouté"]
INGREDIENTS = "Carotte, betterave."

def marque_html(petite=False):
    if LOGO_FICHIER:
        b = base64.b64encode(Path(LOGO_FICHIER).read_bytes()).decode()
        return f'<img class="logo" src="data:image/png;base64,{b}" alt="Au Braisé d\'Or">'
    return ('<div class="mot">Au Braisé d\'Or</div><div class="devise">DE PARIS À COTONOU</div>')

def svg(dessin, cls="illu"):
    return f'<svg class="{cls}" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><defs>{DEFS}</defs>{dessin()}</svg>'

def etiquette(j):
    f, petit, nom, pt, mention, gout, coul, dessin = j
    bienetre = f == "carotte-betterave"
    corps = ""
    if bienetre:
        corps = ('<div class="bien"><b>Les bienfaits</b>' + "".join(f"<span>· {b}</span>" for b in BIENFAITS) +
                 f'<b class="ing">Ingrédients</b><span>{INGREDIENTS} Rien d\'autre.</span></div>')
    nom_html = nom.replace(" ", "<br>") if bienetre else nom
    return f'''
<div class="lab{' be' if bienetre else ''}" style="--c:{coul}">
  <div class="cadre"></div>
  <div class="haut">{marque_html()}</div>
  <div class="scene"><div class="halo"></div>{svg(dessin)}</div>
  <div class="titre"><div class="petit">{petit}</div><div class="nom" style="font-size:{pt}pt">{nom_html}</div></div>
  <div class="pastille">{mention}</div>
  {f'<div class="gout">{gout}</div>' if gout else ''}
  {corps}
  <div class="pied"><span>Préparé le ..... / .....</span><span>À garder au frais</span></div>
  <div class="wa">Commandes WhatsApp {WHATSAPP}</div>
</div>'''

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,600;0,700;0,800;0,900;1,600&display=block');
*{box-sizing:border-box;margin:0;padding:0}
body{background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.lab{width:65mm;height:90mm;position:relative;overflow:hidden;color:#f6ecda;font-family:Montserrat,sans-serif;
  background:radial-gradient(60mm 55mm at 50% 36%, color-mix(in srgb,var(--c) 42%, transparent), transparent 70%),
             radial-gradient(70mm 30mm at 50% 104%, rgba(255,106,26,.38), transparent 70%),
             linear-gradient(#170d07,#0f0804 60%,#1c110a);
  display:flex;flex-direction:column;align-items:center;padding:4.2mm 4mm 3.6mm}
.cadre{position:absolute;inset:2mm;border:.3mm solid rgba(244,212,149,.6);border-radius:3mm;pointer-events:none}
.cadre::after{content:"";position:absolute;inset:.8mm;border:.15mm solid rgba(244,212,149,.25);border-radius:2.4mm}
.haut{text-align:center;position:relative;z-index:2}
.mot{font-family:Cambria,Georgia,serif;font-weight:700;font-size:12.5pt;line-height:1;color:#f4d495;
  background:linear-gradient(180deg,#fbe6b6,#e9b866 60%,#c8953d);-webkit-background-clip:text;background-clip:text;color:transparent}
.devise{font-size:3.7pt;letter-spacing:.42em;color:#e9b866;margin-top:.8mm;font-weight:700;padding-left:.42em}
.logo{height:12mm;background:#fbf4e6;padding:.8mm 2.4mm;border-radius:2mm;box-shadow:0 .5mm 1.5mm rgba(0,0,0,.5)}
.scene{position:relative;flex:1;width:100%;display:flex;align-items:center;justify-content:center;min-height:0}
.halo{position:absolute;width:40mm;height:40mm;border-radius:50%;
  background:radial-gradient(circle, color-mix(in srgb,var(--c) 55%, transparent), transparent 68%);filter:blur(1mm)}
.illu{position:relative;width:40mm;height:40mm;filter:drop-shadow(0 1.4mm 1.6mm rgba(0,0,0,.55))}
.titre{text-align:center;line-height:1}
.petit{font-size:6pt;font-weight:800;letter-spacing:.32em;color:#e9b866;padding-left:.32em}
.nom{font-weight:900;letter-spacing:.01em;color:#fff8ea;margin-top:.6mm;text-shadow:0 .6mm 0 color-mix(in srgb,var(--c) 70%, #000)}
.pastille{margin-top:1.8mm;font-size:6.2pt;font-weight:800;text-transform:uppercase;letter-spacing:.12em;color:#1d1007;
  background:linear-gradient(180deg,#fbe6b6,#e9b866);padding:.9mm 3mm;border-radius:5mm}
.gout{font-family:Cambria,Georgia,serif;font-style:italic;font-size:7.6pt;color:#f6ecda;margin-top:1.5mm;opacity:.92}
.pied{display:flex;justify-content:space-between;width:100%;margin-top:2.2mm;font-size:4.5pt;font-weight:600;color:#cdb894;padding:0 2mm}
.wa{font-size:4.6pt;font-weight:700;color:#e9b866;margin-top:.8mm;letter-spacing:.04em}
.be .illu{width:24mm;height:24mm}.be .halo{width:26mm;height:26mm}
.be .scene{flex:0 0 25mm}
.be .nom{line-height:.95}
.be .pastille{margin-top:1.4mm}
.bien{margin-top:2mm;width:100%;padding:1.6mm 2.2mm;border-radius:2mm;background:rgba(255,248,234,.07);border:.2mm solid rgba(244,212,149,.35);
  display:flex;flex-direction:column;gap:.5mm;font-size:5.3pt;line-height:1.25;font-weight:600}
.bien b{font-size:5.4pt;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#e9b866}
.bien b.ing{margin-top:.8mm}
.be .pied{margin-top:auto}
"""

def page_unitaires():
    pages = "".join(f'<div class="pg">{etiquette(j)}</div>' for j in JUS)
    return f'''<!doctype html><html lang="fr"><meta charset="utf-8"><style>{CSS}
@page{{size:65mm 90mm;margin:0}} .pg{{width:65mm;height:90mm;page-break-after:always}}</style><body>{pages}</body></html>'''

def page_planches():
    pages = ""
    for j in JUS:
        cell = etiquette(j)
        pages += f'<div class="a4"><div class="grille">{cell * 9}</div><div class="note">Au Braisé d\'Or · étiquette {j[2].title()} · 6,5 × 9 cm · découper sur le trait blanc</div></div>'
    return f'''<!doctype html><html lang="fr"><meta charset="utf-8"><style>{CSS}
@page{{size:A4;margin:0}}
.a4{{width:210mm;height:297mm;position:relative;page-break-after:always;display:flex;flex-direction:column;align-items:center;padding-top:10mm}}
.grille{{display:grid;grid-template-columns:repeat(3,65mm);grid-auto-rows:90mm;gap:2mm}}
.note{{font:600 7pt Montserrat,sans-serif;color:#999;margin-top:3mm}}</style><body>{pages}</body></html>'''

def page_apercu():
    cells = "".join(etiquette(j) for j in JUS)
    return f'''<!doctype html><html lang="fr"><meta charset="utf-8"><style>{CSS}
body{{background:#e9e4dc;padding:6mm}} .g{{display:grid;grid-template-columns:repeat(5,65mm);gap:5mm}}
.lab{{border-radius:2mm;box-shadow:0 1mm 3mm rgba(0,0,0,.3)}}</style><body><div class="g">{cells}</div></body></html>'''

# ---------------------------------------------------------------- l'affiche « casse »
def verre_casse():
    return ('<g transform="translate(-6 0)">'
            '<path d="M60 40 L120 40 L112 150 Q 90 156 68 150 Z" fill="rgba(200,235,255,.18)" stroke="#e8f6ff" stroke-width="4" stroke-linejoin="round"/>'
            '<path d="M64 70 L116 70 L111 140 Q 90 145 69 140 Z" fill="#ff9a2a" opacity=".85"/>'
            '<path d="M92 40 L84 66 L98 84 L86 108 L96 128" stroke="#fff" stroke-width="3.2" fill="none" stroke-linejoin="round"/>'
            '<path d="M84 66 L70 74 M98 84 L114 80 M86 108 L72 116" stroke="#fff" stroke-width="2.4" fill="none"/>'
            '<path d="M128 46 L140 38 L136 52 Z M132 70 L148 66 L140 80 Z M44 54 L54 48 L52 62 Z M40 92 L30 86 L34 100 Z M138 108 L152 112 L142 120 Z" '
            'fill="#e8f6ff" opacity=".9"/></g>')

def chicha():
    return ('<g>'
            '<path d="M100 40 L120 40 L116 54 L104 54 Z" fill="#e9b866"/>'
            '<ellipse cx="110" cy="38" rx="16" ry="5" fill="#c8953d"/>'
            '<rect x="106" y="54" width="8" height="56" fill="#d9a85a"/>'
            '<ellipse cx="110" cy="78" rx="14" ry="5" fill="#e9b866"/>'
            '<path d="M100 112 C 66 128 66 178 110 182 C 154 178 154 128 120 112 Z" fill="#1d8bd1" stroke="#e8f6ff" stroke-width="3"/>'
            '<rect x="92" y="106" width="36" height="8" rx="3" fill="#e9b866"/>'
            '<path d="M114 92 C 146 92 156 112 150 136 C 146 150 152 158 160 156" stroke="#e9b866" stroke-width="5" fill="none" stroke-linecap="round"/>'
            '<path d="M100 120 L108 140 L100 158" stroke="#fff" stroke-width="3" fill="none"/>'
            '<path d="M70 150 L60 158 L72 162 Z M146 176 L158 182 L148 188 Z" fill="#e8f6ff" opacity=".9"/></g>')

def page_affiche():
    picto = (f'<svg viewBox="0 0 400 400" class="picto" xmlns="http://www.w3.org/2000/svg">'
             '<defs><radialGradient id="fondP" cx=".5" cy=".45" r=".6"><stop offset="0" stop-color="#3a1a0c"/><stop offset="1" stop-color="#150a05"/></radialGradient></defs>'
             '<circle cx="200" cy="200" r="178" fill="url(#fondP)"/>'
             f'<g transform="translate(46 112) scale(1.2)">{verre_casse()}</g>'
             f'<g transform="translate(150 92) scale(1.12)">{chicha()}</g>'
             '<circle cx="200" cy="200" r="178" fill="none" stroke="#e11d2e" stroke-width="34"/>'
             '<line x1="74" y1="74" x2="326" y2="326" stroke="#e11d2e" stroke-width="34"/></svg>')
    return f'''<!doctype html><html lang="fr"><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800;900&display=block');
@page{{size:A4;margin:0}}*{{box-sizing:border-box;margin:0;padding:0}}
body{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.a4{{width:210mm;height:297mm;position:relative;overflow:hidden;color:#f6ecda;font-family:Montserrat,sans-serif;text-align:center;
  background:radial-gradient(160mm 120mm at 50% 40%, rgba(225,29,46,.28), transparent 70%),
             radial-gradient(220mm 90mm at 50% 108%, rgba(255,106,26,.5), transparent 70%),
             linear-gradient(#140b06,#0d0704 55%,#1e1209);
  display:flex;flex-direction:column;align-items:center;padding:16mm 16mm 14mm}}
.cadre{{position:absolute;inset:7mm;border:.6mm solid rgba(244,212,149,.6);border-radius:6mm}}
.mot{{font-family:Cambria,Georgia,serif;font-weight:700;font-size:30pt;line-height:1;
  background:linear-gradient(180deg,#fbe6b6,#e9b866 60%,#c8953d);-webkit-background-clip:text;background-clip:text;color:transparent}}
.devise{{font-size:8pt;letter-spacing:.5em;color:#e9b866;margin-top:2mm;font-weight:700;padding-left:.5em}}
.att{{margin-top:9mm;display:inline-block;background:#e11d2e;color:#fff;font-weight:900;font-size:17pt;letter-spacing:.35em;padding:2.2mm 7mm 2.2mm 8.5mm;border-radius:2mm}}
.picto{{width:118mm;height:118mm;margin-top:8mm;filter:drop-shadow(0 3mm 6mm rgba(0,0,0,.6))}}
h1{{margin-top:8mm;font-weight:900;font-size:33pt;line-height:1.02;letter-spacing:-.01em;color:#fff8ea}}
.egal{{margin-top:4mm;font-weight:900;font-size:40pt;line-height:1;color:#ff3b47;text-shadow:0 1.2mm 0 #5c0a12}}
.txt{{margin-top:7mm;font-size:14pt;font-weight:600;line-height:1.4;color:#f1e3c8;max-width:160mm}}
.txt b{{color:#f4d495}}
.merci{{margin-top:auto;font-family:Cambria,Georgia,serif;font-style:italic;font-size:15pt;color:#e9b866}}
.dir{{margin-top:1.5mm;font-size:9pt;font-weight:700;letter-spacing:.3em;color:#cdb894;padding-left:.3em}}
</style><body><div class="a4"><div class="cadre"></div>
<div class="mot">Au Braisé d'Or</div><div class="devise">DE PARIS À COTONOU</div>
<div class="att">ATTENTION</div>
{picto}
<h1>Verre ou chicha cassé</h1>
<div class="egal">= à rembourser</div>
<p class="txt">Vous cassez un verre ou une chicha ?<br><b>Vous le remboursez</b>, au prix de l'article.<br>Merci d'en prendre soin.</p>
<div class="merci">Merci de votre compréhension</div>
<div class="dir">LA DIRECTION</div>
</div></body></html>'''

# ---------------------------------------------------------------- rendu
DPI = 300 / 96
with sync_playwright() as pw:
    nav = pw.chromium.launch()
    def charger(html, w, h, echelle=1):
        pg = nav.new_page(viewport={"width": w, "height": h}, device_scale_factor=echelle)
        pg.set_content(html, wait_until="networkidle"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        return pg
    pg = charger(page_unitaires(), 246, 341)
    pg.pdf(path=str(OUT / "etiquettes-unitaires.pdf"), prefer_css_page_size=True, print_background=True); pg.close()
    pg = charger(page_unitaires(), 246, 341, DPI)
    for i, j in enumerate(JUS):
        pg.locator(".lab").nth(i).screenshot(path=str(OUT / "png" / f"{j[0]}.png"))
    pg.close()
    pg = charger(page_apercu(), 1300, 900, 1.6)
    pg.screenshot(path=str(OUT / "apercu.png"), full_page=True); pg.close()
    pg = charger(page_affiche(), 794, 1123)
    pg.pdf(path=str(OUT / "affiche-casse-A4.pdf"), prefer_css_page_size=True, print_background=True); pg.close()
    pg = charger(page_affiche(), 794, 1123, DPI)
    pg.locator(".a4").screenshot(path=str(OUT / "affiche-casse-A4.png")); pg.close()
    nav.close()

# planches A4 : composées à partir des PNG à 300 DPI (le PDF vectoriel de Chromium pesait 31 Mo,
# il rastérise chaque ombre portée) · un fichier par jus, pour imprimer jus par jus
from PIL import Image, ImageDraw, ImageFont
(OUT / "planches").mkdir(exist_ok=True)
(OUT / "planches-A4.pdf").unlink(missing_ok=True)
MM = 300 / 25.4
for j in JUS:
    lab = Image.open(OUT / "png" / f"{j[0]}.png").convert("RGB").resize((round(65 * MM), round(90 * MM)), Image.LANCZOS)
    a4 = Image.new("RGB", (round(210 * MM), round(297 * MM)), "white")
    x0, y0, g = round(5.5 * MM), round(10 * MM), round(2 * MM)
    for r in range(3):
        for c in range(3):
            a4.paste(lab, (x0 + c * (lab.width + g), y0 + r * (lab.height + g)))
    ImageDraw.Draw(a4).text((a4.width // 2, round(289 * MM)), f"Au Braisé d'Or · étiquette {j[2].title()} · 6,5 × 9 cm · découper sur le blanc",
                            fill=(150, 150, 150), anchor="mm", font=ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 26))
    a4.save(OUT / "planches" / f"planche-A4-{j[0]}.pdf", "PDF", resolution=300.0, quality=92)
for p in sorted(OUT.rglob("*.*")):
    print(f"{p.relative_to(CL)}  {p.stat().st_size // 1024} Ko")

"""Le logo de Grain d'Esthétique en couches, pour l'animer sans le redessiner.

Source : clients/01-grain-esthetique/assets/images/logo-grain-esthetique.svg, le
tracé de SON fichier (55 contours, 2240 x 1620), fait par _vectoriser_logo.py. Un
seul <path> en « evenodd » : un contour posé dans un autre y fait un trou (le
creux du « a », la pupille de l'œil). On regroupe donc chaque contour avec ses
trous, sinon une lettre animée seule se remplirait en noir.

Ce qui sort, dans src/grain35/couches.ts :

    sourcil   le trait du sourcil, et sa LIGNE MÉDIANE (squelette) pour le tracer
              comme un coup de pinceau, du bout gauche au crochet de droite
    oeil      le contour de l'œil avec ses trous (blancs, iris), la ligne des
              cils (là où la paupière s'ouvre) et la boîte de l'iris (la pupille
              y brille, et la caméra y plonge)
    g         le grand G calligraphié, et sa ligne médiane la plus longue
    grain     le point rond du « i » de « rain » : LE GRAIN du nom, centre et rayon
    ligne1    les autres signes de « rain d'esthétique », de gauche à droite
    ligne2    les signes de « Institut de beauté », de gauche à droite

    python _outils/grain35_logo.py
"""
import json
import re
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from skimage.morphology import skeletonize
from scipy.ndimage import distance_transform_edt

ICI = Path(__file__).resolve().parent.parent
SOURCE = ICI.parent / "clients/01-grain-esthetique/assets/images/logo-grain-esthetique.svg"
SORTIE = ICI / "src/grain35/couches.ts"  # ⚠️ pas logo.ts : sous Windows il se confondrait avec Logo.tsx


def lire_sous_chemins(d):
    """Découpe le tracé en sous-chemins, et aplatit chacun en polygone."""
    morceaux = [m for m in re.split(r"(?=M)", d) if m.strip()]
    res = []
    for m in morceaux:
        jetons = re.findall(r"[MQZ]|-?\d+\.?\d*", m)
        pts, i, cmd, cur = [], 0, None, None
        while i < len(jetons):
            j = jetons[i]
            if j in "MQZ":
                cmd = j
                i += 1
                continue
            if cmd == "M":
                cur = (float(jetons[i]), float(jetons[i + 1]))
                pts.append(cur)
                i += 2
            elif cmd == "Q":
                c = (float(jetons[i]), float(jetons[i + 1]))
                f = (float(jetons[i + 2]), float(jetons[i + 3]))
                for t in np.linspace(0, 1, 7)[1:]:
                    pts.append(((1 - t) ** 2 * cur[0] + 2 * (1 - t) * t * c[0] + t * t * f[0],
                                (1 - t) ** 2 * cur[1] + 2 * (1 - t) * t * c[1] + t * t * f[1]))
                cur = f
                i += 4
            else:
                i += 1
        poly = np.array(pts)
        res.append({"d": m.strip(), "poly": poly,
                    "boite": [float(poly[:, 0].min()), float(poly[:, 1].min()),
                              float(poly[:, 0].max()), float(poly[:, 1].max())]})
    return res


def dedans(pt, poly):
    """Point dans polygone (règle du rayon)."""
    x, y = pt
    xs, ys = poly[:, 0], poly[:, 1]
    x2, y2 = np.roll(xs, -1), np.roll(ys, -1)
    croise = ((ys > y) != (y2 > y)) & (x < (x2 - xs) * (y - ys) / (y2 - ys + 1e-12) + xs)
    return bool(croise.sum() % 2)


def contient(a, b):
    ba, bb = a["boite"], b["boite"]
    if not (ba[0] <= bb[0] and ba[1] <= bb[1] and ba[2] >= bb[2] and ba[3] >= bb[3]):
        return False
    return dedans(tuple(b["poly"][0]), a["poly"])


def regrouper(sous):
    """Chaque contour de premier niveau avec les contours qu'il contient (ses trous)."""
    parent = {}
    for i, b in enumerate(sous):
        cands = [j for j, a in enumerate(sous) if j != i and contient(a, b)]
        if cands:  # le plus petit contenant direct
            parent[i] = min(cands, key=lambda j: (sous[j]["boite"][2] - sous[j]["boite"][0])
                            * (sous[j]["boite"][3] - sous[j]["boite"][1]))
    racines = [i for i in range(len(sous)) if i not in parent]

    def racine(i):
        while i in parent:
            i = parent[i]
        return i

    groupes = {r: [r] for r in racines}
    for i in parent:
        groupes[racine(i)].append(i)
    out = []
    for r, membres in groupes.items():
        out.append({"d": " ".join(sous[m]["d"] for m in membres),
                    "boite": sous[r]["boite"], "polys": [sous[m]["poly"] for m in membres],
                    "trous": [sous[m]["boite"] for m in membres if m != r]})
    return out


def masque(groupe, marge=20):
    x0, y0, x1, y1 = groupe["boite"]
    w, h = int(x1 - x0) + 2 * marge, int(y1 - y0) + 2 * marge
    acc = np.zeros((h, w), dtype=bool)
    for p in groupe["polys"]:
        im = Image.new("1", (w, h), 0)
        ImageDraw.Draw(im).polygon([(x - x0 + marge, y - y0 + marge) for x, y in p], fill=1)
        acc ^= np.array(im, dtype=bool)  # evenodd
    return acc, (x0 - marge, y0 - marge)


def ligne_mediane(groupe, pas=6, depart="gauche"):
    """Le plus long chemin du squelette, ordonné depuis le bout le plus à gauche
    (ou le plus haut), simplifié tous les `pas` pixels. Et l'épaisseur maximale."""
    m, (ox, oy) = masque(groupe)
    sq = skeletonize(m)
    epaisseur = float(distance_transform_edt(m).max() * 2)
    pts = {(int(y), int(x)) for y, x in zip(*np.nonzero(sq))}
    voisins = lambda p: [(p[0] + dy, p[1] + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                         if (dy or dx) and (p[0] + dy, p[1] + dx) in pts]

    def plus_loin(src):
        dist, prec, file = {src: 0}, {src: None}, deque([src])
        while file:
            p = file.popleft()
            for q in voisins(p):
                if q not in dist:
                    dist[q], prec[q] = dist[p] + 1, p
                    file.append(q)
        fin = max(dist, key=dist.get)
        return fin, prec

    bouts = [p for p in pts if len(voisins(p)) == 1] or list(pts)
    cle = (lambda p: (p[1], p[0])) if depart == "gauche" else (lambda p: (p[0], p[1]))
    a = min(bouts, key=cle)
    b, prec = plus_loin(a)
    chemin = []
    while b is not None:
        chemin.append(b)
        b = prec[b]
    chemin.reverse()
    if cle(chemin[0]) > cle(chemin[-1]):
        chemin.reverse()
    chemin = chemin[::pas] + [chemin[-1]]
    d = "M" + " L".join(f"{x + ox:.1f},{y + oy:.1f}" for y, x in chemin)
    return d, epaisseur


def main():
    svg = SOURCE.read_text(encoding="utf-8")
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    d = re.search(r'<path[^>]*\sd="([^"]+)"', svg).group(1)
    groupes = regrouper(lire_sous_chemins(d))
    print(len(groupes), "groupes")

    def taille(g):
        b = g["boite"]
        return b[2] - b[0], b[3] - b[1]

    sourcil = [g for g in groupes if g["boite"][3] < 350]
    oeil = [g for g in groupes if g["boite"][1] >= 350 and g["boite"][3] < 720]
    gg = [g for g in groupes if taille(g)[1] > 400]
    grain = [g for g in groupes if 80 < taille(g)[0] < 125 and 80 < taille(g)[1] < 125
             and g["boite"][3] < 910]
    pris = {id(g) for g in sourcil + oeil + gg + grain}
    reste = [g for g in groupes if id(g) not in pris]
    ligne1 = sorted([g for g in reste if g["boite"][1] < 1300], key=lambda g: g["boite"][0])
    ligne2 = sorted([g for g in reste if g["boite"][1] >= 1300], key=lambda g: g["boite"][0])
    assert len(sourcil) == 1 and len(oeil) == 1 and len(gg) == 1 and len(grain) == 1, \
        (len(sourcil), len(oeil), len(gg), len(grain))
    print("ligne 1 :", len(ligne1), "signes · ligne 2 :", len(ligne2), "signes")

    trace_s, ep_s = ligne_mediane(sourcil[0], depart="gauche")
    trace_g, ep_g = ligne_mediane(gg[0], depart="haut")
    gb = grain[0]["boite"]
    ob = oeil[0]["boite"]
    # La ligne des cils : la rangée de l'œil la plus remplie en haut (le trait d'eyeliner).
    m, (ox, oy) = masque(oeil[0])
    rangs = m.sum(1)
    cils = float(oy + int(np.argmax(rangs[: len(rangs) // 2])))
    # L'iris : le trou de l'œil le plus proche d'un carré (les deux blancs sont plats).
    iris = min(oeil[0]["trous"], key=lambda b: abs((b[2] - b[0]) / (b[3] - b[1]) - 1))

    donnees = {
        "largeur": vb[2], "hauteur": vb[3],
        "sourcil": {"d": sourcil[0]["d"], "boite": sourcil[0]["boite"], "trace": trace_s, "epaisseur": ep_s},
        "oeil": {"d": oeil[0]["d"], "boite": ob, "cils": cils, "iris": iris},
        "g": {"d": gg[0]["d"], "boite": gg[0]["boite"], "trace": trace_g, "epaisseur": ep_g},
        "grain": {"d": grain[0]["d"], "boite": gb,
                  "centre": [(gb[0] + gb[2]) / 2, (gb[1] + gb[3]) / 2], "rayon": (gb[2] - gb[0]) / 2},
        "ligne1": [{"d": g["d"], "boite": g["boite"]} for g in ligne1],
        "ligne2": [{"d": g["d"], "boite": g["boite"]} for g in ligne2],
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        "/**\n * Le logo de Grain d'Esthétique en couches : écrit par _outils/grain35_logo.py\n"
        " * depuis SON fichier vectoriel. Ne pas éditer à la main : relancer l'outil.\n */\n"
        f"export const LOGO = {json.dumps(donnees, ensure_ascii=False)} as const;\n",
        encoding="utf-8")
    print("écrit :", SORTIE, f"({SORTIE.stat().st_size // 1024} Ko)")
    print("iris :", [round(v) for v in iris])
    print("sourcil : épaisseur", round(ep_s), "· G : épaisseur", round(ep_g), "· cils à y =", cils,
          "· grain : centre", donnees["grain"]["centre"], "rayon", donnees["grain"]["rayon"])


if __name__ == "__main__":
    main()

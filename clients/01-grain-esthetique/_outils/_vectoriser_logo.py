#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VECTORISE LE LOGO DE GRAIN D'ESTHÉTIQUE.

⚠️ Le seul logo qui existe fait **224 x 162 px** (`logo-grain-esthetique-detoure.png`).
Posé sur une affiche imprimée il est agrandi 3 a 4 fois : il ressort flou, et un
logo flou sur un mur d'institut dit exactement le contraire de ce que la maison
vend. Ce script en fait un SVG, donc net a n'importe quelle taille.

⚠️ CE N'EST PAS UN REDESSIN. On trace les contours du fichier qu'elle nous a
donné : c'est SON logo, au pixel prés, seulement rendu extensible. Redessiner
« dans l'esprit de » aurait produit une marque qui n'est pas la sienne.

La méthode, et pourquoi chaque étape est la :
  1. on ne lit QUE le canal alpha (le logo est détouré : l'alpha est la forme) ;
  2. on agrandit 8x au Lanczos AVANT de seuiller. Tracer un contour a 224 px
     donne des marches d'escalier que rien ne rattrape ensuite ; agrandir
     d'abord, c'est laisser l'interpolation lisser la marche ;
  3. `findContours` en mode arborescent (RETR_CCOMP) pour garder les TROUS :
     sans ça la pupille de l'oeil et le compteur des lettres se remplissent ;
  4. `approxPolyDP` avec un epsilon minuscule, puis des courbes de Bézier
     lissées, pour que le trait ne soit pas un polygone visible.

Sortie : `assets/images/logo-grain-esthetique.svg` (+ une version marque seule,
l'oeil sans le lettrage, utile quand le nom est déjà écrit a côté).
"""
import os, sys
import numpy as np
import cv2
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
CLIENT = os.path.dirname(ICI)
SRC = os.path.join(CLIENT, "assets", "images", "logo-grain-esthetique-detoure.png")
OUT = os.path.join(CLIENT, "assets", "images")

AGRANDIR = 8          # avant seuillage, pour tuer l'escalier
SEUIL = 128           # sur l'alpha agrandi
EPSILON = 0.6         # en pixels de l'image agrandie : ~0.075 px a l'échelle d'origine


def lisser(points):
    """Un contour en courbes de Bézier quadratiques passant par les milieux.

    ⚠️ Relier les points au segment droit laisse un polygone VISIBLE des que le
    logo est agrandi : c'est exactement le défaut qu'on essaie de corriger. En
    prenant les milieux comme points d'ancrage et les sommets comme points de
    contrôle, la courbe est continue partout, sans avoir a ajuster de tangentes.
    """
    n = len(points)
    if n < 3:
        return ""
    mil = lambda a, b: ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
    d0 = mil(points[-1], points[0])
    d = [f"M{d0[0]:.2f},{d0[1]:.2f}"]
    for i in range(n):
        ctrl = points[i]
        fin = mil(points[i], points[(i + 1) % n])
        d.append(f"Q{ctrl[0]:.2f},{ctrl[1]:.2f} {fin[0]:.2f},{fin[1]:.2f}")
    d.append("Z")
    return "".join(d)


def tracer(alpha, echelle):
    gros = cv2.resize(alpha, None, fx=AGRANDIR, fy=AGRANDIR, interpolation=cv2.INTER_LANCZOS4)
    _, binaire = cv2.threshold(gros, SEUIL, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binaire, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    chemins = []
    for c in contours:
        if cv2.contourArea(c) < (AGRANDIR * AGRANDIR) * 1.5:   # poussière de seuillage
            continue
        approx = cv2.approxPolyDP(c, EPSILON, True).reshape(-1, 2).astype(float)
        approx *= echelle / AGRANDIR
        chemins.append(lisser(approx))
    return chemins


def ecrire(chemins, w, h, chemin_fichier, titre):
    # fill-rule evenodd = les contours intérieurs redeviennent des trous
    corps = "".join(chemins)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
        f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="{titre}">'
        f'<title>{titre}</title>'
        f'<path fill="currentColor" fill-rule="evenodd" d="{corps}"/>'
        f'</svg>'
    )
    open(chemin_fichier, "w", encoding="utf-8").write(svg)
    return len(svg)


def main():
    if not os.path.exists(SRC):
        sys.exit(f"source introuvable : {SRC}")
    im = Image.open(SRC).convert("RGBA")
    alpha = np.array(im.split()[-1])
    h0, w0 = alpha.shape
    # On travaille dans un repére 10x la source : assez fin pour les décimales,
    # assez rond pour rester lisible dans le fichier.
    ech = 10.0
    W, H = w0 * ech, h0 * ech

    chemins = tracer(alpha, ech)
    p1 = os.path.join(OUT, "logo-grain-esthetique.svg")
    o1 = ecrire(chemins, W, H, p1, "Grain d'Esthétique, institut de beauté")

    # La marque seule : l'oeil et le sourcil, sans le lettrage. Le partage se lit
    # sur la source — le lettrage commence sous ~52 % de la hauteur.
    coupe = int(h0 * 0.50)
    marque = alpha.copy()
    marque[coupe:, :] = 0
    ys, xs = np.nonzero(marque)
    if len(ys):
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rogne = marque[y0:y1, x0:x1]
        ch2 = tracer(rogne, ech)
        p2 = os.path.join(OUT, "logo-grain-marque.svg")
        o2 = ecrire(ch2, rogne.shape[1] * ech, rogne.shape[0] * ech, p2,
                    "Grain d'Esthétique, la marque")
        print(f"marque seule : {p2}  {o2//1024} Ko  {rogne.shape[1]}x{rogne.shape[0]} source")

    print(f"logo complet : {p1}  {o1//1024} Ko  {len(chemins)} contours  viewBox {W:.0f}x{H:.0f}")


if __name__ == "__main__":
    main()

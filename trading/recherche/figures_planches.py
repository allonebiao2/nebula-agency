# -*- coding: utf-8 -*-
"""
Dessiner des figures détectées, pour vérifier À L'ŒIL qu'un ETE ressemble à un ETE et un biseau à un biseau.

    python -m trading.recherche.figures_planches --base EURUSD --tf H4 --par-figure 3 --graine 1

Images dans `trading/rapports/recherche/figures/planches/` (OpenCV, sans matplotlib).
"""
from __future__ import annotations

import argparse
import sys

import cv2
import numpy as np
import pandas as pd

from . import banc, figures
from .lancer import DOSSIER

VERT, ROUGE, NOIR, BLEU, OR, GRIS = (80, 170, 60), (60, 60, 210), (30, 30, 30), (200, 120, 40), (40, 160, 220), (150, 150, 150)


def planche(serie: banc.Serie, e: figures.Evenement, chemin) -> None:
    debut = max(0, min(p[0] for p in e.pivots) - 15)
    fin = min(len(serie), e.b + 45)
    o, h, l, c = (x[debut:fin] for x in (serie.ouverture, serie.haut, serie.bas, serie.cloture))
    img = np.full((640, 1400, 3), 250, np.uint8)
    stop = e.stop_proche
    d = e.sens * (serie.cloture[e.b] - stop)
    cible = serie.cloture[e.b] + e.sens * 2 * d
    pm = min(l.min(), stop, cible, e.stop_loin)
    pM = max(h.max(), stop, cible, e.stop_loin)
    marge = (pM - pm) * 0.04
    pm, pM = pm - marge, pM + marge
    n = fin - debut
    pas = 1360 / n
    y = lambda p: int(40 + 560 - (p - pm) / (pM - pm) * 560)  # noqa: E731
    x = lambda i: int(20 + (i - debut + 0.5) * pas)  # noqa: E731
    larg = max(1, int(pas / 3))
    for k in range(n):
        coul = VERT if c[k] >= o[k] else ROUGE
        xc = x(debut + k)
        cv2.line(img, (xc, y(h[k])), (xc, y(l[k])), NOIR, 1)
        cv2.rectangle(img, (xc - larg, y(max(o[k], c[k]))), (xc + larg, y(min(o[k], c[k])) + 1), coul, -1)
    for (i0, p0), (i1, p1) in e.lignes:
        cv2.line(img, (x(i0), y(p0)), (x(i1), y(p1)), BLEU, 2)
    for k, (i, p) in enumerate(e.pivots):
        cv2.circle(img, (x(i), y(p)), 6, OR, 2)
        cv2.putText(img, str(k), (x(i) + 6, y(p) - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, OR, 1)
    cv2.line(img, (x(e.b), 40), (x(e.b), 600), GRIS, 1)
    for prix, coul, nom in ((stop, ROUGE, "stop proche"), (e.stop_loin, ROUGE, "stop loin"), (cible, VERT, "objectif 2R (stop proche)")):
        cv2.line(img, (x(e.b), y(prix)), (1380, y(prix)), coul, 1)
        cv2.putText(img, nom, (1180, y(prix) - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.42, coul, 1)
    t = pd.Timestamp(serie.temps[e.b])
    cv2.putText(img, f"{serie.base} {serie.tf} {e.figure}  cassure {t}  {'VENTE' if e.sens < 0 else 'ACHAT'}  "
                     f"divergence RSI {'oui' if e.rsi_ok else 'non'}  EMA50 {'oui' if e.ema_ok else 'non'}",
                (20, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, NOIR, 1)
    cv2.imwrite(str(chemin), img)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="EURUSD")
    p.add_argument("--tf", default="H4")
    p.add_argument("--par-figure", type=int, default=3)
    p.add_argument("--graine", type=int, default=1)
    a = p.parse_args()
    s = banc.charger(a.base, a.tf)
    dossier = DOSSIER / "figures" / "planches"
    dossier.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(a.graine)
    for f in figures.FIGURES:
        ev = figures.detecter(s, f)
        for q in sorted(rng.choice(len(ev), size=min(a.par_figure, len(ev)), replace=False)):
            chemin = dossier / f"{a.base}_{a.tf}_{f}_{pd.Timestamp(s.temps[ev[q].b]):%Y%m%d_%H%M}.png"
            planche(s, ev[q], chemin)
            print(chemin)
    return 0


if __name__ == "__main__":
    sys.exit(main())

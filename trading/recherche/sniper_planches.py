# -*- coding: utf-8 -*-
"""
Dessiner des trades « Sniper Entry » tirés au hasard, pour vérifier À L'ŒIL que le code voit ce que
l'auteur montre : le sommet M15, la bougie de balayage, le rectangle, la clôture M1, le stop, l'objectif.

    python -m trading.recherche.sniper_planches --base EURUSD --nombre 12 --graine 3
    python -m trading.recherche.sniper_planches --base EURUSD --dates 2025-10-31T01:31 2025-10-31T16:05

Sans matplotlib (OpenCV, déjà installé). Images dans `trading/rapports/recherche/sniper/planches/`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from . import banc, sniper
from .lancer import DOSSIER

VERT, ROUGE, GRIS, NOIR = (80, 170, 60), (60, 60, 210), (150, 150, 150), (30, 30, 30)
BLEU, OR = (200, 120, 40), (40, 160, 220)


def _bougies(img, x0, y0, l, h, o, hi, lo, c, prix_min, prix_max, largeur):
    n = len(c)
    pas = l / max(n, 1)
    y = lambda p: int(y0 + h - (p - prix_min) / (prix_max - prix_min) * h)  # noqa: E731
    for k in range(n):
        xc = int(x0 + (k + 0.5) * pas)
        couleur = VERT if c[k] >= o[k] else ROUGE
        cv2.line(img, (xc, y(hi[k])), (xc, y(lo[k])), NOIR, 1)
        cv2.rectangle(img, (int(xc - largeur), y(max(o[k], c[k]))), (int(xc + largeur), y(min(o[k], c[k])) + 1), couleur, -1)
    return y, pas


def planche(prep: sniper.Preparation, tr: sniper.TradesSniper, q: int, niveau: float, chemin: Path) -> None:
    s, m = prep.serie, prep.m15
    j = int(tr.balayage_m15[q])
    e, x = int(tr.entree[q]), int(tr.sortie[q])
    img = np.full((620, 1500, 3), 250, np.uint8)
    # --- gauche : M15, 40 bougies avant le balayage, 6 après ---
    a, b = max(0, j - 40), min(len(m.cloture), j + 7)
    pm = min(m.bas[a:b].min(), tr.cible[q], tr.stop[q])
    pM = max(m.haut[a:b].max(), tr.cible[q], tr.stop[q])
    marge = (pM - pm) * 0.05
    y, pas = _bougies(img, 20, 40, 700, 540, m.ouverture[a:b], m.haut[a:b], m.bas[a:b], m.cloture[a:b], pm - marge, pM + marge, 5)
    xj = int(20 + (j - a + 0.5) * pas)
    cv2.line(img, (20, y(niveau)), (720, y(niveau)), OR, 1)
    cv2.rectangle(img, (xj - 7, y(m.haut[j] if tr.sens[q] < 0 else m.bas[j])), (720, y(m.cloture[j])), BLEU, 2)
    moy = prep.ema15(sniper.Reglages().ema)[a:b]
    for k in range(1, b - a):
        if not (np.isnan(moy[k - 1]) or np.isnan(moy[k])):
            cv2.line(img, (int(20 + (k - 0.5) * pas), y(moy[k - 1])), (int(20 + (k + 0.5) * pas), y(moy[k])), GRIS, 2)
    # --- droite : M1, du balayage à la sortie (+10) ---
    debut_m1 = int(np.searchsorted(prep.m15_de, j))
    a1, b1 = max(0, debut_m1 - 5), min(len(s), x + 11)
    if b1 - a1 > 240:
        a1 = max(a1, e - 60)
        b1 = min(b1, a1 + 240)
    pm1 = min(s.bas[a1:b1].min(), tr.cible[q], tr.stop[q])
    pM1 = max(s.haut[a1:b1].max(), tr.cible[q], tr.stop[q])
    marge = (pM1 - pm1) * 0.05
    y1, pas1 = _bougies(img, 760, 40, 720, 540, s.ouverture[a1:b1], s.haut[a1:b1], s.bas[a1:b1], s.cloture[a1:b1],
                        pm1 - marge, pM1 + marge, max(1, int(720 / max(b1 - a1, 1) / 3)))
    for prix, coul, nom in ((tr.prix_entree[q], NOIR, "entree"), (tr.stop[q], ROUGE, "stop"), (tr.cible[q], VERT, "objectif"),
                            (m.cloture[j], BLEU, "rectangle")):
        cv2.line(img, (760, y1(prix)), (1480, y1(prix)), coul, 1)
        cv2.putText(img, nom, (1400, y1(prix) - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, coul, 1)
    for idx, coul in ((e, NOIR), (x, OR)):
        if a1 <= idx < b1:
            xx = int(760 + (idx - a1 + 0.5) * pas1)
            cv2.line(img, (xx, 40), (xx, 580), coul, 1)
    t = pd.DatetimeIndex(s.temps)
    ny = t[e].tz_localize("UTC").tz_convert("America/New_York")
    titre = (f"{s.base} {'VENTE' if tr.sens[q] < 0 else 'ACHAT'}  balayage M15 {pd.Timestamp(m.debut[j])} UTC  "
             f"entree {t[e]} UTC ({ny:%H:%M} New York)  R {tr.R[q]:+.2f} ({banc.MOTIFS[tr.motif[q]]})  "
             f"stop {tr.risque_prix[q] / (s.point * (10 if s.base == 'EURUSD' else 100)):.1f}")
    cv2.putText(img, titre, (20, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.5, NOIR, 1)
    cv2.putText(img, "M15 (EMA 200 en gris, niveau balaye en or, rectangle en bleu)", (20, 605), cv2.FONT_HERSHEY_SIMPLEX, 0.45, GRIS, 1)
    cv2.putText(img, "M1 (entree en noir, sortie en or)", (760, 605), cv2.FONT_HERSHEY_SIMPLEX, 0.45, GRIS, 1)
    cv2.imwrite(str(chemin), img)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="EURUSD")
    p.add_argument("--nombre", type=int, default=12)
    p.add_argument("--graine", type=int, default=3)
    p.add_argument("--dates", nargs="*", default=[])
    a = p.parse_args()
    s = banc.charger(a.base, "M1")
    prep = sniper.preparer(s)
    r = sniper.Reglages(annonces=1)
    sens, rc, rx, niv, fvg = sniper.balayages(prep, r)
    tr = sniper.simuler(prep, r, balayage=(sens, rc, rx, niv, fvg))
    t = pd.DatetimeIndex(s.temps)
    if a.dates:
        choix = [int(np.argmin(np.abs((t[tr.entree] - pd.Timestamp(d)).total_seconds()))) for d in a.dates]
    else:
        choix = sorted(np.random.default_rng(a.graine).choice(len(tr), size=min(a.nombre, len(tr)), replace=False))
    dossier = DOSSIER / "sniper" / "planches"
    dossier.mkdir(parents=True, exist_ok=True)
    for q in choix:
        chemin = dossier / f"{a.base}_{t[tr.entree[q]]:%Y%m%d_%H%M}.png"
        planche(prep, tr, q, float(niv[tr.balayage_m15[q]]), chemin)
        print(chemin)
    return 0


if __name__ == "__main__":
    sys.exit(main())

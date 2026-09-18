# -*- coding: utf-8 -*-
"""
Contrôle de PARITÉ : les caractéristiques calculées sur une fenêtre = celles calculées sur tout.

    python -m trading.recherche._qc_parite

Le modèle a appris sur des caractéristiques calculées avec tout l'historique derrière chaque barre.
L'agent en direct, lui, ne lit qu'une fenêtre récente, et l'apprentissage calcule par morceaux
(`construire_aux_barres`) pour tenir dans la mémoire du PC. Si les deux ne donnent pas les MÊMES
chiffres, le modèle lit en direct des valeurs qu'il n'a jamais vues : il répond quand même, sans
erreur ni alerte, et la démo mesure une autre stratégie que celle qu'on a testée.

Ce contrôle tire des barres au hasard sur la série Deriv du NAS100, compare barre par barre, et
dit pour chaque fenêtre la pire différence relative, caractéristique par caractéristique.
⚠️ Il a un TÉMOIN : une fenêtre volontairement trop courte (500 barres) DOIT échouer. Un contrôle
qui passerait aussi avec elle ne contrôlerait rien.
"""
from __future__ import annotations

import sys

import numpy as np


def comparer(serie, indices, echauffement: int) -> tuple[float, str, int]:
    from .caracteristiques import construire, construire_aux_barres
    X = construire(serie)
    noms = sorted(X)
    plein = np.column_stack([X[k][indices] for k in noms]).astype(np.float64)
    fenetre, noms2 = construire_aux_barres(serie, indices, echauffement=echauffement, bloc=1)
    assert noms == noms2, "l'ordre des caractéristiques diffère"
    fenetre = fenetre.astype(np.float64)
    pire, qui, trous = 0.0, "", 0
    for k, nom in enumerate(noms):
        a, b = plein[:, k], fenetre[:, k]
        fa, fb = np.isfinite(a), np.isfinite(b)
        trous += int((fa != fb).sum())
        m = fa & fb
        if not m.any():
            continue
        # Écart relatif à l'échelle de la caractéristique (float32 oblige : 1e-6 près)
        echelle = max(np.nanstd(a[m]), 1e-9)
        ecart = float(np.max(np.abs(a[m] - b[m])) / echelle)
        if ecart > pire:
            pire, qui = ecart, nom
    return pire, qui, trous


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from . import banc
    serie = banc.charger("NAS100", "M1")
    rng = np.random.default_rng(11)
    indices = np.sort(rng.choice(np.arange(40_000, len(serie)), 60, replace=False))
    print(f"  NAS100 Deriv, {len(serie)} barres, {len(indices)} barres tirées au hasard\n")
    echecs = 0
    for ech, doit_passer in ((20_000, True), (6_000, None), (500, False)):
        pire, qui, trous = comparer(serie, indices, ech)
        ok = pire < 1e-3 and trous == 0
        verdict = ("OK " if ok else "ÉCART") if doit_passer is not False else (
            "OK (témoin rouge)" if not ok else "⛔ TÉMOIN VERT")
        if doit_passer and not ok:
            echecs += 1
        if doit_passer is False and ok:
            echecs += 1
        print(f"  {verdict:<18} fenêtre {ech:>6} barres : pire écart {pire:.2e} écart-type"
              f" ({qui or '-'}), {trous} valeurs manquantes d'un seul côté")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())

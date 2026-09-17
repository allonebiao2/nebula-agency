# -*- coding: utf-8 -*-
"""
Le banc ment-il ? Quatre preuves avant de croire un seul de ses chiffres.

    python -m trading.recherche._qc_banc

Appelé aussi par `python -m trading.outils.qc` (section BANC DE RECHERCHE).
"""
from __future__ import annotations

import dataclasses
import sys

import numpy as np


def controles(verifier) -> None:
    from trading.recherche import banc, candidates

    # --- 3. stop et objectif dans la même barre : le stop d'abord ------------
    n = 60
    ouv = np.full(n, 1.0)
    haut, bas, clo = ouv + 0.001, ouv - 0.001, ouv.copy()
    haut[11], bas[11] = 1.05, 0.95                        # la barre qui touche les deux
    s = banc.Serie("QC", "M5", np.arange(n).astype("datetime64[m]").astype("datetime64[s]"), ouv, haut, bas,
                   clo, point=1e-5, cout_sens_pts=0.0, swap_long_pts=0.0, swap_court_pts=0.0,
                   nuits_cumul=np.zeros(n))
    sens = np.zeros(n, np.int8)
    sens[9] = 1
    dist = np.full(n, 0.01)
    t = banc.simuler(s, banc.Signaux(sens, dist, rr=2.0))
    verifier(len(t) == 1 and t.motif[0] == banc.STOP and abs(t.R[0] + 1) < 1e-9,
             "banc : stop et objectif touchés dans la même barre, le STOP sort d'abord",
             str((len(t), t.motif, t.R)))
    haut2 = haut.copy()
    bas2 = bas.copy()
    bas2[11] = 0.999
    t2 = banc.simuler(dataclasses.replace(s, haut=haut2, bas=bas2), banc.Signaux(sens, dist, rr=2.0))
    verifier(len(t2) == 1 and t2.motif[0] == banc.OBJECTIF and abs(t2.R[0] - 2) < 1e-9,
             "TÉMOIN : objectif seul touché, +2 R")
    try:
        banc.simuler(s, banc.Signaux(sens, dist, rr=1.5))
        verifier(False, "banc : un objectif sous 2 R est refusé (cahier)")
    except ValueError:
        verifier(True, "banc : un objectif sous 2 R est refusé (cahier)")

    # --- stop plus court que le minimum du courtier : aucun trade -----------
    serre = dataclasses.replace(s, stop_min_prix=0.02)
    verifier(len(banc.simuler(serre, banc.Signaux(sens, dist, rr=2.0))) == 0
             and len(banc.simuler(dataclasses.replace(s, stop_min_prix=0.005), banc.Signaux(sens, dist, rr=2.0))) == 1,
             "banc : un stop sous le minimum du courtier n'est jamais pris (témoin : au-dessus, il l'est)")

    # --- ordres limites : servi au prix, annulé si la cible passe avant ----
    o_haut, o_bas = ouv + 0.001, ouv - 0.001
    o_bas[20] = 0.990                                    # le prix revient chercher la limite
    o_haut[25] = 1.030                                   # puis file à la cible
    serie_o = dataclasses.replace(s, haut=o_haut, bas=o_bas, stop_min_prix=0.0)
    ordre = banc.Ordres(np.array([15]), np.array([1], np.int8), np.array([0.995]), np.array([0.985]),
                        np.array([1.025]), np.array([40]), max_barres=30)
    t_o = banc.simuler(serie_o, ordre)
    verifier(len(t_o) == 1 and t_o.entree[0] == 20 and t_o.motif[0] == banc.OBJECTIF and abs(t_o.R[0] - 3) < 1e-9,
             "banc : ordre limite servi au retour du prix, objectif à +3 R", str((len(t_o), t_o.R)))
    annule_haut = o_haut.copy()
    annule_haut[18] = 1.030                              # la cible passe AVANT le retour
    t_a = banc.simuler(dataclasses.replace(serie_o, haut=annule_haut), ordre)
    verifier(len(t_a) == 0, "banc : cible atteinte avant le remplissage, l'ordre est annulé")

    # --- 1. aucune candidate ne lit le futur ---------------------------------
    rng = np.random.default_rng(4)
    m = 3000
    prix = 1.1 + np.cumsum(rng.normal(0, 0.0004, m))
    temps = (np.datetime64("2025-03-03T00:00") + np.arange(m) * np.timedelta64(15, "m")).astype("datetime64[s]")
    ecart = np.abs(rng.normal(0, 0.0003, m))
    base = banc.Serie("EURUSD", "M15", temps, prix, prix + ecart, prix - ecart, prix + rng.normal(0, 0.0001, m),
                      point=1e-5, cout_sens_pts=2.5, swap_long_pts=0.0, swap_court_pts=0.0,
                      nuits_cumul=np.zeros(m))
    coupe = 2000
    futur = dataclasses.replace(base, ouverture=base.ouverture.copy(), haut=base.haut.copy(),
                                bas=base.bas.copy(), cloture=base.cloture.copy())
    for tableau in (futur.ouverture, futur.haut, futur.bas, futur.cloture):
        tableau[coupe + 1:] = tableau[coupe + 1:][::-1] * 1.01
    fautives = []
    for cand in candidates.CANDIDATES:
        reglages = cand.combinaisons()[0]
        a, b = cand.fabrique(base, **reglages), cand.fabrique(futur, **reglages)
        if not (np.array_equal(a.sens[:coupe + 1], b.sens[:coupe + 1])
                and np.allclose(a.stop_dist[:coupe + 1], b.stop_dist[:coupe + 1], equal_nan=True)):
            fautives.append(cand.nom)
    from trading.recherche import videos
    for nom, fabrique in (("video_mamba", videos.mamba_cassure), ("video_hugo", videos.hugo_crt)):
        a, b = fabrique(base, seance="toutes"), fabrique(futur, seance="toutes")
        if isinstance(a, banc.Signaux):
            egal = (np.array_equal(a.sens[:coupe + 1], b.sens[:coupe + 1])
                    and np.allclose(a.stop_dist[:coupe + 1], b.stop_dist[:coupe + 1], equal_nan=True))
        else:
            ka, kb = a.pose <= coupe, b.pose <= coupe
            egal = all(np.allclose(getattr(a, c)[ka], getattr(b, c)[kb]) for c in ("pose", "sens", "limite", "stop", "cible")) \
                and ka.sum() == kb.sum()
        if not egal:
            fautives.append(nom)
    verifier(not fautives, "banc : aucune candidate (vidéos comprises) ne change ses signaux passés quand on change le futur",
             ", ".join(fautives))
    signaux = sum(int((cand.fabrique(base, **cand.combinaisons()[0]).sens != 0).sum())
                  for cand in candidates.CANDIDATES)
    verifier(signaux > 0, "TÉMOIN : les candidates produisent des signaux sur la série d'essai", str(signaux))

    # --- 2. le témoin au hasard paie les coûts, il ne gagne rien -------------
    marche = dataclasses.replace(base, cout_sens_pts=5.0)
    resultats = [banc.simuler(marche, candidates.temoin_hasard(marche, graine=g)) for g in range(1, 21)]
    R = np.concatenate([r.R for r in resultats])
    verifier(len(R) > 500 and R.mean() < 0.05,
             "banc : l'entrée au hasard ne fabrique pas d'avantage (coûts payés)",
             f"{len(R)} trades, {R.mean():+.3f} R")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    resultats = []

    def verifier(condition, libelle, detail=""):
        resultats.append(bool(condition))
        print(f"  {'✓' if condition else '✗'} {libelle}" + (f"  ({detail})" if detail and not condition else ""))
    controles(verifier)
    print(f"\n  {sum(resultats)} verts · {len(resultats) - sum(resultats)} rouges")
    return 0 if all(resultats) else 1


if __name__ == "__main__":
    sys.exit(main())

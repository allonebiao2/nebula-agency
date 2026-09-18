# -*- coding: utf-8 -*-
"""
Le moteur causal (`live/moteur_scalp.py` + `recherche/rejeu.rejouer`) contre le banc de recherche.

    python -m trading.recherche._qc_moteur

1. **ÉGALITÉ** quand elle est due : avec des ordres valables UNE minute, un seul ordre attend à la
   fois, donc « le plus ancien servi » (banc) et « le premier servi » (moteur) sont le même ordre.
   Filtre ouvert, capital sans contrainte : les deux doivent donner les MÊMES trades (entrée, sortie,
   R). Seule différence admise : le banc laisse un ordre posé pendant la dernière barre d'un trade
   être servi dans cette même barre, le moteur non (il est encore en position).
2. **L'ÉCART** quand les ordres se chevauchent (60 minutes) : même année, mêmes prix, aucun filtre.
"""
from __future__ import annotations

import sys

import numpy as np


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import pandas as pd
    from . import banc, candidates_v2
    from .candidat import REGLAGES
    from .banc import OBJECTIF
    from .rejeu import rejouer
    serie = banc.charger("NAS100", "M1")
    fin = pd.Timestamp(serie.temps[-1])
    j0 = int(np.searchsorted(serie.temps, np.datetime64((fin - pd.DateOffset(years=1)).normalize().to_datetime64(), "s")))
    n = len(serie)
    ouvert = np.ones(n)
    zero = np.zeros(n)
    echecs = 0

    # ---- 1. égalité avec des ordres d'une minute ----
    r1 = dict(REGLAGES, expiration_min=1)
    j_fin = j0 + 60_000
    ordres = candidates_v2.rabais(serie, **r1)
    tb = banc.simuler_ordres(serie, ordres, j0, j_fin - 1)
    tb_ok = tb.sortie < j_fin - 1
    res = rejouer("NAS100", 1e9, [], levier_max=None, serie=serie, proba=ouvert, seuils=zero, j0=j0,
                  reglages=r1, j_fin=j_fin)
    tm = res["notes"]
    B = [(int(e), int(s_), float(r)) for e, s_, r in zip(tb.entree[tb_ok], tb.sortie[tb_ok], tb.R[tb_ok])]
    M = [(t["j_rempli"], t["j_sortie"], t["R"]) for t in tm if t["j_sortie"] < j_fin - 1]
    # Les épisodes de divergence : chacun DOIT commencer par une réentrée du banc dans la barre
    # même où son trade précédent se ferme. Toute autre première différence est un défaut du moteur.
    sortie_b = {e: s_ for e, s_, _ in B}
    fins_b = {s_ for _, s_, _ in B}
    ib = im = 0
    episodes = expliques = 0
    ecart_R = 0.0
    communs = 0
    while ib < len(B) and im < len(M):
        if B[ib][:2] == M[im][:2]:
            ecart_R = max(ecart_R, abs(B[ib][2] - M[im][2]))
            communs += 1
            ib += 1
            im += 1
            continue
        episodes += 1
        if ib > 0 and B[ib][0] == B[ib - 1][1]:
            expliques += 1
        # resynchroniser : avancer celui qui est en retard jusqu'au prochain trade commun
        cles_m = {m[:2] for m in M[im:]}
        cles_b = {b[:2] for b in B[ib:]}
        while ib < len(B) and B[ib][:2] not in cles_m:
            ib += 1
        while im < len(M) and M[im][:2] not in cles_b:
            im += 1
    ok1 = episodes == expliques and ecart_R < 1e-3 and communs > 0.75 * len(B)
    echecs += not ok1
    print(f"  {'OK ' if ok1 else 'ÉCART'}  ordres d'une minute, {j_fin - j0} barres : banc {len(B)} trades, "
          f"moteur {len(M)}, communs {communs} · {episodes} épisodes de divergence, dont {expliques} "
          f"ouverts par une réentrée du banc dans la barre de sortie · pire écart de R {ecart_R:.1e}")

    # ---- 1 bis. le VERROU du banc : des ordres qui se chevauchent sont refusés ----
    ordres60 = candidates_v2.rabais(serie, **REGLAGES)
    try:
        banc.simuler_ordres(serie, ordres60, j0, j0 + 5000)
        ok_v = False
    except banc.SimulationNonCausale:
        ok_v = True
    try:                                   # TÉMOIN : des ordres d'une minute passent
        banc.simuler_ordres(serie, candidates_v2.rabais(serie, **r1), j0, j0 + 5000)
        ok_t = True
    except banc.SimulationNonCausale:
        ok_t = False
    echecs += not (ok_v and ok_t)
    print(f"  {'OK ' if ok_v and ok_t else 'ÉCHEC'}  verrou du banc : ordres qui se chevauchent "
          f"{'refusés' if ok_v else 'ACCEPTÉS'}, ordres isolés {'acceptés' if ok_t else 'REFUSÉS'} (témoin)")

    # ---- 2. l'écart avec des ordres de 60 minutes, sans filtre, toute l'année ----
    ordres = candidates_v2.rabais(serie, **REGLAGES)
    tb = banc.simuler_ordres(serie, ordres, j0, n - 1, non_causal_accepte=True)   # comparaison
    res = rejouer("NAS100", 1e9, [], levier_max=None, serie=serie, proba=ouvert, seuils=zero, j0=j0)
    Rm = np.array([t["R"] for t in res["notes"]])
    om = np.array([t["motif"] == "objectif" for t in res["notes"]])
    print(f"  INFO  sans filtre, un an, ordres de 60 min :")
    print(f"        banc (le plus ancien servi) : {len(tb)} trades, "
          f"{100 * (tb.motif == OBJECTIF).mean():.1f} % de 2 R, {tb.R.mean():+.3f} R")
    print(f"        moteur (le premier servi)   : {len(Rm)} trades, {100 * om.mean():.1f} % de 2 R, "
          f"{Rm.mean():+.3f} R")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())

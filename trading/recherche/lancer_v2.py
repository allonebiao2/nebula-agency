# -*- coding: utf-8 -*-
"""
Lancer les familles de scalping de la vague 2, sur les données de DÉCOUVERTE seulement.

    python -m trading.recherche.lancer_v2 --tour 6
    python -m trading.recherche.lancer_v2 --tour 6 --seulement balayage_niveau --unites M1 M5

Différences avec `lancer.py` (vagues 1 à 4 de la recherche précédente) :
  · les séries viennent de `scelle.series_decouverte` : le scellé reste fermé ;
  · un instrument peut avoir DEUX historiques (NAS100 : Dukascopy jusqu'en 2019, Deriv depuis 2024) ;
    chacun est un test à part, parce qu'un avantage vrai doit se voir sur les deux ;
  · chaque ligne du registre porte les trois chiffres de Mongazi : 2 R atteints, point mort réel,
    probabilité de 5 et 6 pertes d'affilée.
"""
from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from dataclasses import asdict

from . import banc, candidates_v2, scelle
from .lancer import DOSSIER, enregistrer_test, resume

INSTRUMENTS = ("EURUSD", "NAS100")


def lancer(tour: int, seulement: set[str] | None = None, unites=("M1", "M5", "M15"),
           liste=None) -> None:
    DOSSIER.mkdir(parents=True, exist_ok=True)
    liste = liste or candidates_v2.CANDIDATES
    for tf in unites:
        for base in INSTRUMENTS:
            try:
                series = scelle.series_decouverte(base, tf)
            except FileNotFoundError as exc:
                print(f"  {exc}")
                continue
            for serie in series:
                marque = f"{serie.source}{str(serie.temps[0])[:4]}"
                for cand in liste:
                    if tf not in cand.unites or base not in cand.instruments:
                        continue
                    if seulement and cand.nom not in seulement:
                        continue
                    t0 = time.time()
                    res = banc.walk_forward(serie, cand)
                    h = res.hors_echantillon
                    cle = f"t{tour}_{cand.nom}_{base}_{tf}_{marque}"
                    (DOSSIER / f"{cle}.json").write_text(json.dumps(
                        {"tour": tour, "candidate": cand.nom, "libelle": cand.libelle,
                         "source": cand.source, "grille": cand.grille, "flux": serie.source,
                         **asdict(res)}, ensure_ascii=False, default=str), encoding="utf-8")
                    enregistrer_test(cle, {
                        "tour": tour, "candidate": cand.nom, "base": base, "tf": tf,
                        "temoin": False, "combinaisons": res.combinaisons, "flux": serie.source,
                        "vague": "2 · familles de scalping",
                        **{k: h.get(k) for k in ("trades", "taux_reussite", "taux_objectif",
                                                 "point_mort_objectif", "p_objectif", "esperance_R",
                                                 "profit_factor", "p_valeur", "drawdown_max_pct",
                                                 "R_par_mois", "trades_par_mois", "debut", "fin")}})
                    if h.get("trades"):
                        series_p = h.get("series_perdantes") or {}
                        print(f"  {cand.nom:18s} {base} {tf:3s} {marque:9s} {h['trades']:6d} trades  "
                              f"objectif {100 * h['taux_objectif']:5.1f} % "
                              f"(point mort {100 * h['point_mort_objectif']:5.1f} %)  "
                              f"{h['esperance_R']:+.3f} R  p={h['p_objectif']:.3f}  "
                              f"P(5 pertes/100)={series_p.get('p_5_pertes_sur_100_montecarlo')}  "
                              f"({time.time() - t0:.0f} s)", flush=True)
                    else:
                        print(f"  {cand.nom:18s} {base} {tf:3s} {marque:9s} aucun trade "
                              f"({time.time() - t0:.0f} s)", flush=True)
                del serie
                gc.collect()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument("--tour", type=int, default=6)
    p.add_argument("--seulement", nargs="*")
    p.add_argument("--unites", nargs="*", default=["M1", "M5", "M15"])
    p.add_argument("--resume", action="store_true")
    a = p.parse_args()
    if not a.resume:
        lancer(a.tour, set(a.seulement) if a.seulement else None, tuple(a.unites))
    resume()
    return 0


if __name__ == "__main__":
    sys.exit(main())

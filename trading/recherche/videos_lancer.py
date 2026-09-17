# -*- coding: utf-8 -*-
"""
Backtest des deux méthodes des vidéos, sur EUR/USD et NAS100, sur tout l'historique chargé.

    python -m trading.recherche.videos_lancer

Deux lectures, toujours côte à côte :
  · « auteur »  : les réglages tels que la vidéo les enseigne, SANS optimisation ;
  · « adaptée » : une petite grille jugée en walk-forward (hors échantillon seulement),
                  inscrite au registre, où chaque essai compte dans la correction de Holm.
"""
from __future__ import annotations

import gc
import json
import sys
import time

import numpy as np

from . import banc, videos
from .banc import Candidate
from .lancer import DOSSIER, REGISTRE, _registre, resume

INSTRUMENTS = ("EURUSD", "NAS100")
UNITES = ("M1", "M5", "M15", "H1")


def par_annee(serie: banc.Serie, t: banc.Trades) -> dict:
    if not len(t):
        return {}
    annees = serie.temps[t.entree].astype("datetime64[Y]").astype(int) + 1970
    sortie = {}
    for a in np.unique(annees):
        R = t.R[annees == a]
        sortie[str(a)] = {"trades": int(len(R)), "taux_reussite": float((R > 0).mean()),
                          "esperance_R": float(R.mean()), "somme_R": float(R.sum())}
    return sortie


CANDIDATES = [
    Candidate("video_mamba", "MambaFx : zone M5 + cassure de structure M1", "YouTube MambaFx",
              videos.mamba_cassure, {"touches": [2, 3], "rr": [3.0, 5.0], "seance": ["ouverture", "toutes"]},
              UNITES),
    Candidate("video_hugo", "Hugo FX : CRT H1 + swing M15 + discount M1", "YouTube Hugo FX",
              videos.hugo_crt, {"fib": [0.5, 0.62], "stop": ["swing", "079"], "seance": ["londres_ny", "toutes"]},
              UNITES),
]
AUTEUR = {"video_mamba": {}, "video_hugo": {}}      # les valeurs par défaut SONT celles des vidéos


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    DOSSIER.mkdir(parents=True, exist_ok=True)
    registre = _registre()
    for base in INSTRUMENTS:
        for tf in UNITES:
            try:
                serie = banc.charger(base, tf)
            except FileNotFoundError as exc:
                print(f"  {exc}")
                continue
            periode = f"{str(serie.temps[0])[:10]} -> {str(serie.temps[-1])[:10]}"
            for cand in CANDIDATES:
                t0 = time.time()
                strat = cand.fabrique(serie, **AUTEUR[cand.nom])
                t_auteur = banc.simuler(serie, strat)
                chere = banc.charger(base, tf, multiplicateur_couts=1.5)
                t_chere = banc.simuler(chere, cand.fabrique(chere, **AUTEUR[cand.nom]))
                auteur = {**banc.mesurer(serie, t_auteur), "par_annee": par_annee(serie, t_auteur),
                          "couts_x1_5": banc.mesurer(chere, t_chere)}
                adaptee = banc.walk_forward(serie, cand) if len(serie) > 20_000 else None
                cle = f"videos_{cand.nom}_{base}_{tf}"
                (DOSSIER / f"{cle}.json").write_text(json.dumps(
                    {"candidate": cand.nom, "libelle": cand.libelle, "base": base, "tf": tf, "periode": periode,
                     "auteur": auteur, "trades_R_auteur": [round(float(x), 4) for x in t_auteur.R],
                     "adaptee": None if adaptee is None else {
                         "hors_echantillon": adaptee.hors_echantillon, "fenetres": adaptee.fenetres,
                         "trades_R": adaptee.trades_R}},
                    ensure_ascii=False, default=str), encoding="utf-8")
                for variante, h, combis in (("auteur", auteur, 1),
                                            ("adaptee", adaptee.hors_echantillon if adaptee else {}, len(cand.combinaisons()))):
                    if not h.get("trades"):
                        continue
                    k = f"{cle}_{variante}"
                    registre = [r for r in registre if r["cle"] != k]
                    registre.append({"cle": k, "tour": "videos", "candidate": cand.nom, "base": base, "tf": tf,
                                     "temoin": False, "combinaisons": combis,
                                     **{x: h.get(x) for x in ("trades", "taux_reussite", "esperance_R",
                                                              "profit_factor", "p_valeur", "drawdown_max_pct",
                                                              "R_par_mois", "trades_par_mois", "debut", "fin")}})
                REGISTRE.write_text(json.dumps(registre, ensure_ascii=False, indent=1), encoding="utf-8")
                a = auteur
                print(f"  {cand.nom:12s} {base} {tf:3s} {periode}  AUTEUR "
                      + (f"{a['trades']:5d} tr {100 * a['taux_reussite']:5.1f} % {a['esperance_R']:+.3f} R "
                         f"PF {a['profit_factor']:.2f} (coûts x1,5 : {a['couts_x1_5'].get('esperance_R', 0):+.3f} R)"
                         if a.get("trades") else "aucun trade")
                      + ("" if not adaptee or not adaptee.hors_echantillon.get("trades") else
                         f" | ADAPTÉE {adaptee.hors_echantillon['trades']} tr "
                         f"{100 * adaptee.hors_echantillon['taux_reussite']:.1f} % "
                         f"{adaptee.hors_echantillon['esperance_R']:+.3f} R")
                      + f"  ({time.time() - t0:.0f} s)", flush=True)
            del serie
            gc.collect()
    resume()
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""
Backtest des figures chartistes (ETE, ETE inversé, biseaux) avec et sans RSI et EMA 50.

    python -m trading.recherche.figures_lancer            # tout : tests, stabilité, 10 000 $
    python -m trading.recherche.figures_rapport           # puis le rapport

4 figures × 4 filtres (aucun, divergence RSI, EMA 50, les deux) × 2 stops (proche, loin) × H1, H4, D1 ×
EUR/USD et NAS100 = 192 versions, TOUTES fixées avant le premier résultat et TOUTES inscrites au registre
(la correction de Holm les compte). Objectif 2 R, coûts Deriv, entrée à l'ouverture suivante.
"""
from __future__ import annotations

import gc
import json
import sys
import time

import numpy as np
import pandas as pd

from . import banc, compte, figures
from .lancer import DOSSIER, REGISTRE, _registre

SORTIE = DOSSIER / "figures"
INSTRUMENTS = ("EURUSD", "NAS100")
UNITES = ("H1", "H4", "D1")


def ecrire(nom, donnees):
    SORTIE.mkdir(parents=True, exist_ok=True)
    (SORTIE / f"{nom}.json").write_text(json.dumps(donnees, ensure_ascii=False, default=str), encoding="utf-8")


def mesures(serie: banc.Serie, tr: banc.Trades) -> dict:
    m = banc.mesurer(serie, tr)
    if not len(tr):
        return m
    R = tr.R
    g = R > 0
    m["objectif_atteint"] = float((tr.motif == banc.OBJECTIF).mean())
    m["rr_realise"] = float(R[g].mean() / -R[~g].mean()) if g.any() and (~g).any() else None
    m["series_perdantes"] = compte.series_perdantes(R)
    annees = pd.DatetimeIndex(serie.temps[tr.entree]).year
    m["par_annee"] = {str(a): {"trades": int((annees == a).sum()), "somme_R": float(R[annees == a].sum())}
                      for a in np.unique(annees)}
    # stabilité : les 80 % anciens contre les 20 % récents (en nombre de bougies)
    coupe = int(len(serie) * 0.8)
    for nom, masque in (("avant_80", tr.entree < coupe), ("apres_20", tr.entree >= coupe)):
        m[nom] = {"trades": int(masque.sum()), "esperance_R": float(R[masque].mean()) if masque.any() else None}
    return m


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from ..noyau.donnees_mt5 import specs_et_couts
    registre = [r for r in _registre() if not r["cle"].startswith("figures_")]
    resultats = {}
    for base in INSTRUMENTS:
        specs = specs_et_couts(base)[0]
        for tf in UNITES:
            s = banc.charger(base, tf)
            chere = banc.charger(base, tf, multiplicateur_couts=1.5)
            for fig in figures.FIGURES:
                t0 = time.time()
                ev = figures.detecter(s, fig)
                for filtre in figures.FILTRES:
                    for stop in figures.STOPS:
                        sig = figures.signaux(s, ev, filtre=filtre, stop=stop)
                        tr = banc.simuler(s, sig)
                        m = mesures(s, tr)
                        cle = f"figures_{fig}_{filtre}_{stop}_{base}_{tf}"
                        trades_compte = [
                            {"entree": str(s.temps[tr.entree[q]]), "sortie": str(s.temps[tr.sortie[q]] + np.timedelta64(s.minutes * 60, "s")),
                             "sens": int(tr.sens[q]), "R": float(tr.R[q]),
                             "points_risque": float(sig.stop_dist[tr.entree[q] - 1] / s.point),
                             "prix": float(s.ouverture[tr.entree[q]])} for q in range(len(tr))]
                        m_cher = banc.mesurer(chere, banc.simuler(chere, sig)) if len(tr) else {}
                        resultats[cle] = {"figure": fig, "filtre": filtre, "stop": stop, "base": base, "tf": tf,
                                          "figures_detectees": len(ev), "mesures": m, "trades": trades_compte,
                                          "couts_x1_5": {k: m_cher.get(k) for k in ("trades", "esperance_R", "p_valeur")}}
                        if m.get("trades"):
                            registre.append({"cle": cle, "tour": "figures", "candidate": f"figures_{fig}", "base": base,
                                             "tf": tf, "temoin": False, "combinaisons": 1,
                                             **{x: m.get(x) for x in ("trades", "taux_reussite", "esperance_R", "profit_factor",
                                                                      "p_valeur", "drawdown_max_pct", "R_par_mois",
                                                                      "trades_par_mois", "debut", "fin")}})
                print(f"  {base} {tf} {fig:18s} {len(ev):4d} figures · sans filtre, stop proche : "
                      f"{resultats[f'figures_{fig}_aucun_proche_{base}_{tf}']['mesures'].get('trades', 0)} tr "
                      f"{resultats[f'figures_{fig}_aucun_proche_{base}_{tf}']['mesures'].get('esperance_R', 0):+.3f} R "
                      f"({time.time() - t0:.0f} s)", flush=True)
            del s, chere
            gc.collect()
    REGISTRE.write_text(json.dumps(registre, ensure_ascii=False, indent=1), encoding="utf-8")
    ecrire("resultats", {k: {x: v[x] for x in v if x != "trades"} for k, v in resultats.items()})

    # --- 10 000 $ : chaque figure sans filtre (stop proche), puis la meilleure version (CHOISIE APRÈS COUP) ---
    specs = {b: specs_et_couts(b)[0] for b in INSTRUMENTS}
    comptes = {}
    candidats = {k: v for k, v in resultats.items() if v["mesures"].get("trades", 0) >= 30}
    meilleure = min(candidats, key=lambda k: candidats[k]["mesures"]["p_valeur"]) if candidats else None
    choix = [f"figures_{fig}_aucun_proche_EURUSD_H4" for fig in figures.FIGURES]
    if meilleure and meilleure not in choix:
        choix.append(meilleure)
    for cle in choix:
        v = resultats[cle]
        for regles in ("video", "pro"):
            tc = [compte.TradeCompte(base=v["base"], entree=pd.Timestamp(t["entree"]).to_pydatetime(),
                                     sortie=pd.Timestamp(t["sortie"]).to_pydatetime(), sens=t["sens"], R=t["R"],
                                     points_risque=t["points_risque"], prix=t["prix"]) for t in v["trades"]]
            res = compte.simuler_compte(tc, specs, risque_pct=1.0, regles=regles).resume()
            res.pop("courbe", None)
            comptes[f"{cle}|{regles}"] = res
            print(f"  10 000 $ {cle:55s} {regles:5s} -> {res.get('capital_final', 10000):>10,.0f} $ "
                  f"({res.get('rendement_pct', 0):+.1f} %) DD {res.get('drawdown_max_pct', 0):.1f} %", flush=True)
    ecrire("comptes", {"meilleure_apres_coup": meilleure, "comptes": comptes})
    return 0


if __name__ == "__main__":
    sys.exit(main())

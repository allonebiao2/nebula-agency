# -*- coding: utf-8 -*-
"""
Les pistes publiées, transposées à l'EUR/USD : versions DÉCLARÉES AVANT tout résultat.

    python -m trading.recherche.eurusd_seances

Demande de Mongazi (2026-09-18) : « et pour l'EUR/USD ? cherche aussi supérieur à 50 % ET 1:2 ».

⚠️ Aucune étude publiée ne donne ces règles pour l'EUR/USD (l'étude du momentum intraday des devises
porte sur le rouble à Moscou ; les tests publiés de la « cassure de Londres » sur l'EUR/USD perdent).
Pour ne pas choisir les réglages en regardant les résultats, la liste est FIXÉE ICI, une fois :
  · deux séances, les ouvertures naturelles de l'EUR/USD : **Londres** (3 h 00 New York, jusqu'à
    11 h 59) et **New York** (8 h 00, jusqu'à 16 h 59, avant le roulement de 17 h 00) ;
  · deux stratégies, celles qui ont tenu sur le NAS100 : **zone de bruit** et **cassure des
    5 premières minutes (ORB)** ;
  · pour chacune, la version de l'article ET la version « crochet » du critère de Mongazi : stop
    fixe, objectif à 2 R, sortie en fin de séance sinon.
Stop jamais plus court que le minimum du courtier (20 points). Coûts Deriv minute par minute.
Trois périodes : Dukascopy 2003-2015, Dukascopy 2016-2026, prix Deriv 2019-2026. Rien n'est retenu
« parce que c'est le meilleur » : tout est rapporté.
"""
from __future__ import annotations

import json
import sys

import numpy as np

from . import banc, orb, zone_bruit
from .lancer import DOSSIER

SORTIE = DOSSIER / "eurusd_seances"
SEANCES = {"Londres": (3 * 60, 540), "New York": (8 * 60, 540)}
PERIODES = (("Dukascopy 2003-2015", "duka", "2003-06-01", "2016-01-01"),
            ("Dukascopy 2016-2026", "duka", "2016-01-01", None),
            ("Deriv 2019-2026", "mt5", "2019-02-01", None))


def lignes_R(tr):
    if not tr:
        return {"trades": 0}
    R = np.array([x["R"] for x in tr])
    g = R > 0
    obj = np.mean([x["motif"] == "objectif" for x in tr])
    lo, hi = banc._wilson(int(g.sum()), len(R))
    t = R.mean() / (R.std(ddof=1) / np.sqrt(len(R))) if len(R) > 2 else 0.0
    serie = pire = 0
    for x in g:
        serie = 0 if x else serie + 1
        pire = max(pire, serie)
    return {"trades": len(R), "gagnants": round(float(g.mean()), 4), "ic95": [round(lo, 3), round(hi, 3)],
            "objectif": round(float(obj), 4), "esperance_R": round(float(R.mean()), 4), "t": round(float(t), 2),
            "pire_serie": int(pire)}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    SORTIE.mkdir(parents=True, exist_ok=True)
    tout = []
    for source in ("duka", "mt5"):
        serie = banc.charger("EURUSD", "M1", source=source)
        smin = serie.stop_min_prix
        for nom_s, (ouv, n) in SEANCES.items():
            mats = zone_bruit.matrices(serie, ouv, n)
            for nom_p, src, d, f in PERIODES:
                if src != source:
                    continue
                essais = {
                    "zone de bruit, article": ("perf", zone_bruit.simuler(*mats, stop_courtier=False, debut=d, fin=f, stop_min_prix=smin)),
                    "zone de bruit, stop courtier": ("perf", zone_bruit.simuler(*mats, stop_courtier=True, debut=d, fin=f, stop_min_prix=smin)),
                    "zone de bruit, crochet 1:2": ("R", zone_bruit.simuler(*mats, stop_courtier=True, debut=d, fin=f, cible_R=2.0, stop_min_prix=smin)),
                    "ORB 5 min, objectif 10 R": ("R", orb.trades_orb(serie, 10.0, d, f, ouverture=ouv, cloture=ouv + n - 1, stop_min_prix=smin)),
                    "ORB 5 min, crochet 1:2": ("R", orb.trades_orb(serie, 2.0, d, f, ouverture=ouv, cloture=ouv + n - 1, stop_min_prix=smin)),
                }
                for nom_e, (mesure, tr) in essais.items():
                    r = zone_bruit.perf(tr) if mesure == "perf" else lignes_R(tr)
                    r.update({"seance": nom_s, "periode": nom_p, "essai": nom_e})
                    tout.append(r)
                    if not r.get("trades"):
                        print(f"  {nom_s:<8} {nom_p:<20} {nom_e:<30} aucun trade", flush=True)
                    elif mesure == "perf":
                        print(f"  {nom_s:<8} {nom_p:<20} {nom_e:<30} {r['trades']:>5} trades · gagnants "
                              f"{100 * r['gagnants']:.1f} % · gain/perte {r['ratio_gain_perte']} · "
                              f"{r['rendement_annuel_pct']:+.1f} %/an · Sharpe {r['sharpe']} · recul {r['pire_recul_pct']} %",
                              flush=True)
                    else:
                        print(f"  {nom_s:<8} {nom_p:<20} {nom_e:<30} {r['trades']:>5} trades · gagnants "
                              f"{100 * r['gagnants']:.1f} % ({100 * r['ic95'][0]:.0f}-{100 * r['ic95'][1]:.0f}) · "
                              f"objectif atteint {100 * r['objectif']:.1f} % · {r['esperance_R']:+.3f} R (t = {r['t']})"
                              f" · pire série {r['pire_serie']}", flush=True)
        del serie
    (SORTIE / "resume.json").write_text(json.dumps(tout, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

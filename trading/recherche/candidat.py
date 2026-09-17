# -*- coding: utf-8 -*-
"""
LE candidat : l'entrée limite au rabais sur NAS100 M1, figée le 2026-09-17.

    python -m trading.recherche.candidat            # rejoue toutes ses mesures
    python -m trading.recherche.candidat --resume   # relit le dernier rapport

**La règle, en une phrase** : dans le sens de l'EMA 60 minutes, poser un ordre limite à 0,5 R sous le
prix (au-dessus, en vente), stop à 2 × ATR(14) de l'entrée, objectif à 2 R, ordre annulé après 60
minutes, position fermée au plus tard à la clôture de la journée.

Pourquoi il existe : sur **480 tests** de cette recherche, c'est le seul qui reste positif après
  · le remplissage réaliste (le prix doit traverser la limite d'un spread complet, parce qu'un achat
    s'exécute au prix acheteur — sans cette exigence, l'EUR/USD paraissait aussi rentable, et il ne
    l'est pas) ;
  · **deux fournisseurs de données indépendants** sur la même période (Deriv et Dukascopy donnent
    +0,169 et +0,175 R : ce n'est pas un artefact d'un flux) ;
  · **le scellé** : 2020-2023, jamais regardé pendant la recherche, +0,165 R sur 29 362 trades ;
  · un coût **trois fois** supérieur à celui de Deriv aujourd'hui.

⛔ Ce qu'il n'est PAS : il n'atteint **pas** les critères de Mongazi. 40 % des trades atteignent 2 R
(il en faut plus de 50), et la probabilité de 5 pertes d'affilée sur 100 trades reste au-dessus de
95 %. Le plafond mesuré (63,8 % avec un devin parfait) dit que ces critères ne sont pas atteignables
en intraday, par personne.

⚠️ Sa fragilité tient en un nombre : **le spread**. À 70 points chez Deriv (mesuré : 70 points dans
99,8 % des minutes, y compris à l'ouverture et sur les annonces) il gagne ; au spread d'époque de
Dukascopy (167 points) il perd. Rien ne garantit que Deriv tienne ce spread, ni qu'un ordre limite y
soit servi comme dans la simulation. **C'est la démo en observation qui tranche, pas ce fichier.**
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from . import banc, candidates_v2, scelle
from .lancer import DOSSIER, enregistrer_test

REGLAGES = dict(tendance=60, retrait=0.5, stop_atr=2.0, expiration_min=60, remplissage=2.0)
FICHIER = DOSSIER / "candidat_rabais.json"
PERIODES = [
    ("découverte · Dukascopy 2013-2019", "duka", "2013-01-01", "2020-01-01"),
    ("SCELLÉ · Dukascopy 2020-2023", "duka", "2020-01-01", "2024-01-01"),
    ("découverte · Dukascopy 2024-2026", "duka", "2024-01-01", None),
    ("découverte · Deriv 2024-2026", "mt5", None, None),
]


def mesurer_periode(libelle: str, source: str, debut, fin, cout: str = "deriv",
                    multiplicateur: float = 1.0) -> dict:
    s = banc.charger("NAS100", "M1", source=source, cout=cout, multiplicateur_couts=multiplicateur)
    s = s.tranche(debut, fin)
    if len(s) < 1000:
        return {"libelle": libelle, "trades": 0}
    t = banc.simuler(s, candidates_v2.rabais(s, **REGLAGES))
    if not len(t):
        return {"libelle": libelle, "trades": 0}
    m = banc.mesurer(s, t)
    annees = s.temps[t.entree].astype("datetime64[Y]").astype(int) + 1970
    par_an = {int(a): round(float(t.R[annees == a].mean()), 4) for a in np.unique(annees)}
    par_sens = {("achat" if sn > 0 else "vente"): round(float(t.R[t.sens == sn].mean()), 4)
                for sn in (1, -1) if (t.sens == sn).any()}
    return {"libelle": libelle, "source": source, "cout": cout, "multiplicateur": multiplicateur,
            "debut": str(s.temps[0])[:10], "fin": str(s.temps[-1])[:10],
            "cout_points_par_sens": round(float(np.median(s.couts_prix()) / s.point), 1),
            "trades": m["trades"], "taux_objectif": m["taux_objectif"],
            "point_mort_objectif": m["point_mort_objectif"], "taux_reussite": m["taux_reussite"],
            "esperance_R": m["esperance_R"], "profit_factor": m["profit_factor"],
            "gain_moyen_R": m["gain_moyen_R"], "perte_moyenne_R": m["perte_moyenne_R"],
            "rr_realise": round(abs(m["gain_moyen_R"] / m["perte_moyenne_R"]), 2) if m["perte_moyenne_R"] else None,
            "p_objectif": m["p_objectif"], "series_perdantes": m["series_perdantes"],
            "trades_par_mois": m["trades_par_mois"], "par_an": par_an, "par_sens": par_sens}


def rejouer() -> dict:
    lignes = [mesurer_periode(*p) for p in PERIODES]
    couts = [mesurer_periode(f"Deriv 2024-2026 · coût ×{k}", "mt5", None, None, multiplicateur=k)
             for k in (1.5, 2.0, 3.0, 4.0)]
    autres = [mesurer_periode("SCELLÉ · coût relatif au prix", "duka", "2020-01-01", "2024-01-01",
                              cout="relatif"),
              mesurer_periode("SCELLÉ · spread d'époque Dukascopy", "duka", "2020-01-01", "2024-01-01",
                              cout="epoque")]
    sortie = {"reglages": REGLAGES, "periodes": lignes, "couts": couts, "variantes": autres}
    DOSSIER.mkdir(parents=True, exist_ok=True)
    FICHIER.write_text(json.dumps(sortie, ensure_ascii=False, default=str), encoding="utf-8")
    for d in lignes + autres:
        if d.get("trades"):
            enregistrer_test(f"candidat_rabais_{d['libelle'][:28]}", {
                "tour": 8, "candidate": "rabais_ema60_0.5R_2atr", "base": "NAS100", "tf": "M1",
                "temoin": False, "combinaisons": 1, "vague": "5 · candidat figé",
                **{k: d.get(k) for k in ("trades", "taux_reussite", "taux_objectif",
                                         "point_mort_objectif", "p_objectif", "esperance_R",
                                         "profit_factor")}})
    return sortie


def afficher(d: dict) -> None:
    print(f"\n  CANDIDAT « rabais » · NAS100 M1 · {d['reglages']}\n")
    print(f"  {'période':38s} {'trades':>7s} {'2 R':>7s} {'pt mort':>8s} {'esp.':>8s} {'PF':>6s} "
          f"{'P(5/100)':>9s}")
    for x in d["periodes"] + d["variantes"] + d["couts"]:
        if not x.get("trades"):
            continue
        sp = x.get("series_perdantes") or {}
        print(f"  {x['libelle'][:38]:38s} {x['trades']:7d} {100 * x['taux_objectif']:6.1f}% "
              f"{100 * x['point_mort_objectif']:7.1f}% {x['esperance_R']:+8.3f} "
              f"{x['profit_factor']:6.2f} "
              f"{100 * (sp.get('p_5_pertes_sur_100_montecarlo') or 0):8.1f}%")
    scelle_ligne = next((x for x in d["periodes"] if x["libelle"].startswith("SCELLÉ")), None)
    if scelle_ligne and scelle_ligne.get("trades"):
        s = scelle_ligne
        print(f"\n  LES TROIS CHIFFRES DE MONGAZI, sur le scellé ({s['trades']} trades jamais vus) :")
        print(f"    1. 2 R réellement atteints : {100 * s['taux_objectif']:.1f} %  "
              f"(objectif : plus de 50 %)  ⛔ non atteint")
        print(f"    2. R:R réalisé : {s['rr_realise']}  (gain moyen {s['gain_moyen_R']:+.2f} R, "
              f"perte moyenne {s['perte_moyenne_R']:+.2f} R)  ✅")
        sp = s["series_perdantes"]
        print(f"    3. P(5 pertes d'affilée sur 100) : "
              f"{100 * sp['p_5_pertes_sur_100_montecarlo']:.1f} %  ·  P(6) : "
              f"{100 * sp['p_6_pertes_sur_100_montecarlo']:.1f} %  ·  la plus longue observée : "
              f"{sp['plus_longue_observee']}  ⛔ pas « extrêmement bas »")
        print(f"\n    Ce qu'il fait, lui : {s['esperance_R']:+.3f} R par trade, "
              f"{s['trades_par_mois']:.0f} trades par mois, positif chaque année "
              f"({', '.join(f'{a} {v:+.2f}' for a, v in s['par_an'].items())}) "
              f"et dans les deux sens ({', '.join(f'{k} {v:+.2f}' for k, v in s['par_sens'].items())}).")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument("--resume", action="store_true")
    a = p.parse_args()
    d = json.loads(FICHIER.read_text(encoding="utf-8")) if (a.resume and FICHIER.exists()) else rejouer()
    afficher(d)
    return 0


if __name__ == "__main__":
    sys.exit(main())

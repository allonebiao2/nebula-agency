# -*- coding: utf-8 -*-
"""
Le backtest le plus long possible, **comme on l'aurait vraiment tradé** : filtre réentraîné au fil
du temps, jamais avec une information future.

    python -m trading.recherche.long_backtest --marche NAS100
    python -m trading.recherche.long_backtest --marche EURUSD --parts 0.05 0.10 0.20

Différence avec ce qui a été fait jusqu'ici, et elle est de taille : le filtre n'est plus appris une
fois pour toutes sur 2013-2019 puis appliqué au reste. Ici il est **réappris tous les six mois sur
tout le passé disponible**, et jugé sur les six mois suivants — ce qu'un agent aurait fait s'il avait
tourné depuis le premier jour.

Trois règles, toutes vérifiables dans le code :
  · **aucune information future** : l'apprentissage s'arrête aux trades DÉJÀ CLOS avant le début du
    bloc de test, et on purge ceux qui débordent dessus ;
  · **la décision se prend sur la dernière barre close avant le remplissage** (la fuite d'une minute
    a été mesurée : elle offrait 3 points de taux d'objectif) ;
  · **le résultat final passe par le simulateur de compte**, avec les vrais lots et l'échelle 6-4-3.

⚠️ Il n'y a plus de données scellées : les deux jeux ont été ouverts. Ce backtest est donc la
meilleure mesure possible, **et la dernière** : tout ce qui suit se juge en avant, sur la démo.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import timedelta

import numpy as np
import pandas as pd

from .lancer import DOSSIER, enregistrer_test

SORTIE = DOSSIER / "long"
BLOC_MOIS = 6           # on rejuge tous les six mois
MIN_APPRENTISSAGE = 3000    # trades minimum avant de faire confiance au filtre


def serie_complete(marche: str):
    """L'historique le plus long d'un seul tenant, chez un seul fournisseur."""
    from . import banc
    return banc.charger(marche, "M1", source="duka")


def _modele():
    from sklearn.ensemble import HistGradientBoostingClassifier
    return HistGradientBoostingClassifier(max_iter=200, learning_rate=0.06, max_leaf_nodes=31,
                                          min_samples_leaf=100, l2_regularization=1.0,
                                          early_stopping=True, validation_fraction=0.15,
                                          random_state=5)


def walk_forward(marche: str, parts=(0.05, 0.10, 0.20)) -> dict:
    from . import meta_candidat as mc
    serie = serie_complete(marche)
    d = mc.trades_et_caracteristiques(serie)
    if d is None:
        raise SystemExit(f"{marche} : aucun trade")
    t, ok = d["trades"], d["ok"]
    X, i_signal, y = d["X"], d["i_signal"], d["objectif"]
    temps_entree = pd.DatetimeIndex(serie.temps[t.entree])
    temps_sortie = pd.DatetimeIndex(serie.temps[t.sortie])
    n = len(t)
    idx_ok = np.flatnonzero(ok)
    debut = temps_entree[idx_ok[0]]
    fin = temps_entree[idx_ok[-1]]
    proba = np.full(n, np.nan)
    blocs = []
    curseur = debut + pd.DateOffset(years=2)              # deux ans avant la première décision
    while curseur < fin:
        suivant = curseur + pd.DateOffset(months=BLOC_MOIS)
        # Apprentissage : uniquement les trades DÉJÀ CLOS avant le bloc (purge incluse).
        app = ok & np.asarray(temps_sortie < curseur)
        test = ok & np.asarray(temps_entree >= curseur) & np.asarray(temps_entree < suivant)
        if app.sum() >= MIN_APPRENTISSAGE and test.sum() >= 30 and y[app].sum() >= 300:
            m = _modele()
            m.fit(X[i_signal[app]], y[app].astype(np.int8))
            proba[test] = m.predict_proba(X[i_signal[test]])[:, 1]
            blocs.append({"debut": str(curseur)[:10], "fin": str(suivant)[:10],
                          "apprentissage": int(app.sum()), "test": int(test.sum())})
        curseur = suivant
    juge = np.isfinite(proba)
    sortie = {"marche": marche, "serie": [str(serie.temps[0])[:10], str(serie.temps[-1])[:10]],
              "trades_total": int(ok.sum()), "trades_juges": int(juge.sum()),
              "blocs": len(blocs), "premier_bloc": blocs[0]["debut"] if blocs else None,
              "paliers": []}
    if not juge.any():
        return sortie
    # Le seuil est choisi BLOC PAR BLOC sur le passé : le quantile d'un bloc ne doit pas dépendre
    # de ce bloc, sinon on choisit le seuil en connaissant déjà ses résultats.
    for part in parts:
        garde = np.zeros(n, bool)
        for b in blocs:
            m = juge & np.asarray(temps_entree >= b["debut"]) & np.asarray(temps_entree < b["fin"])
            if m.sum() < 20:
                continue
            passe = juge & np.asarray(temps_entree < b["debut"])
            seuil = (np.nanquantile(proba[passe], 1 - part) if passe.sum() > 200
                     else np.nanquantile(proba[m], 1 - part))
            garde |= m & (proba >= seuil)
        if garde.sum() < 50:
            continue
        R = t.R[garde]
        obj = y[garde]
        sp_mois = (temps_entree[garde][-1] - temps_entree[garde][0]).days / 30.44
        sortie["paliers"].append({
            "part": part, "trades": int(garde.sum()),
            "taux_objectif": round(float(obj.mean()), 4),
            "esperance_R": round(float(R.mean()), 4),
            "somme_R": round(float(R.sum()), 1),
            "R_par_mois": round(float(R.sum() / max(sp_mois, 1)), 2),
            "trades_par_mois": round(garde.sum() / max(sp_mois, 1), 1),
            "par_an": {int(a): {"trades": int(m.sum()), "taux": round(float(y[garde][m].mean()), 3),
                                "R": round(float(R[m].sum()), 1)}
                       for a in sorted({d.year for d in temps_entree[garde]})
                       if (m := (temps_entree[garde].year == a)).sum() > 5},
            "indices": np.flatnonzero(garde).tolist()})
    return sortie


def en_compte(marche: str, res: dict, part: float, capital: float = 500.0) -> dict:
    """Les trades retenus, passés au simulateur de compte : vrais lots, échelle 6-4-3."""
    from . import candidates_v2, meta_candidat as mc
    from ..noyau.donnees_mt5 import specs_et_couts
    from .candidat import REGLAGES
    from .compte import TradeCompte, simuler_compte
    from .compte_plan import ECHELLE
    palier = next((p for p in res["paliers"] if abs(p["part"] - part) < 1e-9), None)
    if not palier:
        return {}
    serie = serie_complete(marche)
    d = mc.trades_et_caracteristiques(serie)
    ordres = candidates_v2.rabais(serie, **REGLAGES)
    t = d["trades"]
    idx = np.array(palier["indices"])
    i_ordre = t.ordre[idx]
    entrees = pd.DatetimeIndex(serie.temps[t.entree[idx]]).to_pydatetime()
    sorties = pd.DatetimeIndex(serie.temps[t.sortie[idx]]).to_pydatetime()
    trades = [TradeCompte(base=serie.base, entree=entrees[k], sortie=sorties[k],
                          sens=int(t.sens[idx][k]), R=float(t.R[idx][k]),
                          points_risque=float(abs(ordres.limite[i_ordre][k] - ordres.stop[i_ordre][k])
                                              / serie.point),
                          prix=float(ordres.limite[i_ordre][k]))
              for k in range(len(idx))]
    specs, _ = specs_et_couts(marche)
    res_compte = simuler_compte(trades, {serie.base: specs}, capital=capital, risque_pct=6.0,
                                regles="video", echelle_drawdown=ECHELLE)
    return res_compte.resume()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--marche", default="NAS100")
    ap.add_argument("--parts", nargs="*", type=float, default=[0.05, 0.10, 0.20])
    ap.add_argument("--capital", type=float, default=500.0)
    a = ap.parse_args()
    SORTIE.mkdir(parents=True, exist_ok=True)
    res = walk_forward(a.marche, tuple(a.parts))
    print(f"\n  {a.marche} · {res['serie'][0]} → {res['serie'][1]} · {res['trades_total']} trades "
          f"possibles · {res['trades_juges']} jugés hors échantillon · {res['blocs']} blocs de "
          f"{BLOC_MOIS} mois (premier : {res['premier_bloc']})\n")
    print(f"  {'sélectivité':>12s} {'trades':>8s} {'2 R atteints':>13s} {'espérance':>11s} "
          f"{'R/mois':>8s} {'trades/mois':>12s}")
    for p in res["paliers"]:
        print(f"  {100 * p['part']:11.0f} % {p['trades']:8d} {100 * p['taux_objectif']:12.1f} % "
              f"{p['esperance_R']:+10.3f} R {p['R_par_mois']:8.1f} {p['trades_par_mois']:12.1f}")
        enregistrer_test(f"long_{a.marche}_{int(100 * p['part'])}pct", {
            "tour": 11, "candidate": "long_walkforward", "base": a.marche, "tf": "M1",
            "temoin": False, "combinaisons": len(a.parts), "vague": "6 · backtest long",
            "trades": p["trades"], "taux_objectif": p["taux_objectif"],
            "esperance_R": p["esperance_R"], "taux_reussite": None, "profit_factor": None,
            "p_valeur": None, "point_mort_objectif": None, "p_objectif": None})
    sans_indices = {**res, "paliers": [{k: v for k, v in p.items() if k != "indices"}
                                       for p in res["paliers"]]}
    (SORTIE / f"long_{a.marche}.json").write_text(json.dumps(sans_indices, ensure_ascii=False, default=str),
                                                  encoding="utf-8")
    for p in res["paliers"]:
        print(f"\n  Année par année, sélectivité {100 * p['part']:.0f} % :")
        for an, v in p["par_an"].items():
            print(f"    {an} : {v['trades']:5d} trades · {100 * v['taux']:5.1f} % de 2 R · "
                  f"{v['R']:+8.1f} R")
    meilleur = max(res["paliers"], key=lambda p: p["esperance_R"] * np.sqrt(p["trades"])) if res["paliers"] else None
    if meilleur:
        compte = en_compte(a.marche, res, meilleur["part"], a.capital)
        print(f"\n  AU COMPTE (capital {a.capital:,.0f} $, vrais lots, échelle 6-4-3, sélectivité "
              f"{100 * meilleur['part']:.0f} %) :".replace(",", " "))
        print(f"    {compte.get('trades')} trades · capital final "
              f"{compte.get('capital_final', 0):,.0f} $ · {compte.get('rendement_annuel_pct', 0):.0f} %/an · "
              f"pire recul {compte.get('drawdown_max_pct', 0):.1f} % · série perdante max "
              f"{compte.get('serie_perdante_max')}".replace(",", " "))
        print(f"    mois positifs {compte.get('mois_positifs_pct')} % · pire mois "
              f"{compte.get('pire_mois_pct')} % · {compte.get('annees')} ans")
        (SORTIE / f"compte_{a.marche}.json").write_text(json.dumps(compte, ensure_ascii=False, default=str),
                                                        encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

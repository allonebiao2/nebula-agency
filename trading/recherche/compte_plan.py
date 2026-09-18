# -*- coding: utf-8 -*-
"""
Le plan de Mongazi, appliqué à la stratégie, **avec n'importe quel capital et de vrais lots**.

    python -m trading.recherche.compte_plan
    python -m trading.recherche.compte_plan --marche EURUSD --capitaux 100 1000 10000

Ce que ce fichier fait, et que les tableaux d'intérêts composés ne font pas :
  · il dimensionne **en lots réels** (lot minimum 0,1 sur le NAS100, pas de 0,1, lot maximum 100),
    via `noyau/risque.dimensionner` — le même code que l'agent en direct ;
  · il applique **l'échelle 6-4-3 par le drawdown** via `noyau/profils.risque_courant` — encore le
    même code que l'agent ;
  · il rejoue les **vrais trades** de la stratégie (entrée limite au rabais + filtre à 5 %), dans
    l'ordre du temps, avec leur vraie distance de stop.

⚠️ **Ce qu'il révèle et qu'aucune planche ne dit** : le lot maximum du courtier plafonne le risque
par trade, donc la croissance **cesse d'être exponentielle** au-delà d'un certain capital. Sur le
NAS100 : stop d'environ 17 points d'indice, 1 lot = 1 $ par point → 100 lots = ~1 730 $ de risque
maximum, soit un compte saturé autour de **29 000 $ à 6 %**. C'est une information, pas un défaut :
c'est exactement pour ça que la planche « LES POSSIBILITÉS » parle de plusieurs comptes.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime

import numpy as np
import pandas as pd

from ..noyau.donnees_mt5 import specs_et_couts
from .candidat import REGLAGES
from .compte import TradeCompte, simuler_compte
from .lancer import DOSSIER

SORTIE = DOSSIER / "plan"
ECHELLE = ((0.0, 6.0), (0.0001, 4.0), (0.20, 3.0))     # le plan : 6 % au sommet, 4 % dessous, 3 % à -20 %
CAPITAUX = (50, 100, 500, 1_000, 5_000, 20_000, 100_000, 1_000_000)


def trades_du_plan(marche: str = "NAS100", part: float = 0.05) -> list[TradeCompte]:
    """Les trades de la stratégie retenue, prêts à être dimensionnés (stop et prix d'entrée réels)."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from . import banc, candidates_v2, meta_candidat as mc
    if marche.upper() == "NAS100":
        s_app = banc.charger("NAS100", "M1", source="duka").tranche("2013-01-01", "2020-01-01")
        s_test = banc.charger("NAS100", "M1", source="duka").tranche("2020-01-01", "2024-01-01")
    else:
        s_app = banc.charger("EURUSD", "M1")
        s_test = banc.charger("EURUSD", "M1", source="duka").tranche("2003-05-05", "2012-01-01")
    a = mc.trades_et_caracteristiques(s_app)
    b = mc.trades_et_caracteristiques(s_test)
    modele = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.06, max_leaf_nodes=31,
                                            min_samples_leaf=100, l2_regularization=1.0,
                                            early_stopping=True, validation_fraction=0.15,
                                            random_state=5)
    modele.fit(a["X"][a["i_signal"][a["ok"]]], a["objectif"][a["ok"]].astype(np.int8))
    proba = modele.predict_proba(b["X"][b["i_signal"][b["ok"]]])[:, 1]
    garde = proba >= np.quantile(proba, 1 - part)

    ordres = candidates_v2.rabais(s_test, **REGLAGES)
    t = b["trades"]
    i_ordre = t.ordre[b["ok"]][garde]
    entree = t.entree[b["ok"]][garde]
    sortie = t.sortie[b["ok"]][garde]
    sens = t.sens[b["ok"]][garde]
    R = t.R[b["ok"]][garde]
    # La distance de stop RÉELLE du trade : celle de l'ordre qui a été servi, pas une moyenne.
    points = np.abs(ordres.limite[i_ordre] - ordres.stop[i_ordre]) / s_test.point
    prix = ordres.limite[i_ordre]
    temps = pd.DatetimeIndex(s_test.temps[entree]).to_pydatetime()
    temps_sortie = pd.DatetimeIndex(s_test.temps[sortie]).to_pydatetime()
    base = s_test.base
    return [TradeCompte(base=base, entree=temps[k], sortie=temps_sortie[k], sens=int(sens[k]),
                        R=float(R[k]), points_risque=float(points[k]), prix=float(prix[k]))
            for k in range(len(R))]


def _neufs(trades: list[TradeCompte]) -> list[TradeCompte]:
    """Une copie fraîche : `simuler_compte` écrit dans les trades (lots, pnl, capital)."""
    return [TradeCompte(base=t.base, entree=t.entree, sortie=t.sortie, sens=t.sens, R=t.R,
                        points_risque=t.points_risque, prix=t.prix) for t in trades]


def balayer(marche: str = "NAS100", capitaux=CAPITAUX, part: float = 0.05,
            echelle=ECHELLE, risque_fixe: float | None = None) -> list[dict]:
    trades = trades_du_plan(marche, part)
    specs, _ = specs_et_couts(marche)
    lignes = []
    for capital in capitaux:
        res = simuler_compte(_neufs(trades), {trades[0].base: specs}, capital=float(capital),
                             risque_pct=risque_fixe or echelle[0][1], regles="video",
                             echelle_drawdown=None if risque_fixe else echelle)
        r = res.resume()
        pris = res.pris
        refus_taille = sum(1 for t in res.trades if t.refuse.startswith("taille"))
        # Saturation : la part des trades où le lot a buté sur le maximum du courtier.
        satures = sum(1 for t in pris if t.lots >= specs.volume_max - 1e-9)
        lignes.append({
            "marche": marche, "capital": capital, "risque": risque_fixe or "échelle 6-4-3",
            "trades_pris": r.get("trades", 0), "refuses_taille": refus_taille,
            "capital_final": r.get("capital_final"), "rendement_annuel_pct": r.get("rendement_annuel_pct"),
            "drawdown_max_pct": r.get("drawdown_max_pct"), "serie_perdante_max": r.get("serie_perdante_max"),
            "risque_moyen_pct": r.get("risque_moyen_pct"), "lots_moyens": r.get("lots_moyens"),
            "trades_satures": satures,
            "part_saturee_pct": round(100 * satures / max(len(pris), 1), 1),
            "mois_positifs_pct": r.get("mois_positifs_pct"), "annees": r.get("annees")})
    return lignes


def tableau_mensuel(marche: str = "NAS100", capital: float = 500.0, part: float = 0.05,
                    echelle=ECHELLE) -> list[dict]:
    """Le tableau de la planche, mais rempli avec les VRAIS trades : mois par mois, ce que le plan
    aurait donné. Le R du mois et le risque appliqué ne sont pas supposés, ils sont mesurés."""
    trades = trades_du_plan(marche, part)
    specs, _ = specs_et_couts(marche)
    res = simuler_compte(_neufs(trades), {trades[0].base: specs}, capital=capital,
                         risque_pct=echelle[0][1], regles="video", echelle_drawdown=echelle)
    pris = sorted(res.pris, key=lambda t: t.sortie)
    df = pd.DataFrame({"mois": [t.sortie.strftime("%Y-%m") for t in pris],
                       "R": [t.R for t in pris], "pnl": [t.pnl_usd for t in pris],
                       "risque": [t.risque_pct_applique for t in pris],
                       "capital": [t.capital_apres for t in pris],
                       "lots": [t.lots for t in pris]})
    g = df.groupby("mois")
    sortie = []
    depart = capital
    for mois, bloc in g:
        fin = float(bloc["capital"].iloc[-1])
        sortie.append({"mois": mois, "trades": int(len(bloc)), "R_du_mois": round(float(bloc["R"].sum()), 2),
                       "risque_moyen_pct": round(float(bloc["risque"].mean()), 2),
                       "croissance_pct": round(100 * (fin / depart - 1), 1),
                       "capital_fin": round(fin, 2), "lots_moyens": round(float(bloc["lots"].mean()), 2)})
        depart = fin
    return sortie


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--marche", default="NAS100")
    ap.add_argument("--capitaux", nargs="*", type=float)
    ap.add_argument("--part", type=float, default=0.05)
    ap.add_argument("--comparer", action="store_true", help="ajouter les risques fixes 6 % et 1 %")
    ap.add_argument("--mensuel", type=float, help="tableau mois par mois pour ce capital de départ")
    a = ap.parse_args()
    SORTIE.mkdir(parents=True, exist_ok=True)
    if a.mensuel:
        lignes = tableau_mensuel(a.marche, a.mensuel, a.part)
        (SORTIE / f"mensuel_{a.marche}_{int(a.mensuel)}.json").write_text(
            json.dumps(lignes, ensure_ascii=False), encoding="utf-8")
        print(f"\n  {a.marche} · capital de départ {a.mensuel:,.0f} $ · plan 6-4-3, vrais lots\n"
              .replace(",", " "))
        print(f"  {'mois':8s} {'trades':>7s} {'R du mois':>10s} {'risque moyen':>13s} "
              f"{'croissance':>11s} {'capital':>16s} {'lots':>8s}")
        for d in lignes:
            print(f"  {d['mois']:8s} {d['trades']:7d} {d['R_du_mois']:10.1f} "
                  f"{d['risque_moyen_pct']:12.2f} % {d['croissance_pct']:10.1f} % "
                  f"{d['capital_fin']:16,.0f} $ {d['lots_moyens']:8.1f}".replace(",", " "))
        croissances = [d["croissance_pct"] for d in lignes]
        print(f"\n  {len(lignes)} mois · croissance médiane {np.median(croissances):.1f} % par mois · "
              f"pire mois {min(croissances):.1f} % · meilleur {max(croissances):.1f} % · "
              f"mois positifs {100 * np.mean([c > 0 for c in croissances]):.0f} %")
        return 0
    capitaux = a.capitaux or CAPITAUX
    lignes = balayer(a.marche, capitaux, a.part)
    if a.comparer:
        for fixe in (6.0, 1.0):
            lignes += balayer(a.marche, capitaux, a.part, risque_fixe=fixe)
    (SORTIE / f"capitaux_{a.marche}.json").write_text(json.dumps(lignes, ensure_ascii=False, default=str),
                                                      encoding="utf-8")
    entete = (f"{'capital':>12s} {'plan':>14s} {'trades':>7s} {'refusés':>8s} {'capital final':>16s} "
              f"{'%/an':>9s} {'pire recul':>11s} {'risque moyen':>13s} {'lots au max':>12s}")
    print(f"\n  {a.marche} · stratégie filtrée à {100 * a.part:.0f} % · "
          f"{lignes[0]['annees']:.1f} ans de trades\n")
    print("  " + entete)
    for d in lignes:
        if not d["trades_pris"]:
            print(f"  {d['capital']:12,.0f} $ {str(d['risque'])[:14]:>14s} "
                  f"AUCUN TRADE (lot minimum du courtier)".replace(",", " "))
            continue
        print(f"  {d['capital']:12,.0f} $ {str(d['risque'])[:14]:>14s} {d['trades_pris']:7d} "
              f"{d['refuses_taille']:8d} {d['capital_final']:16,.0f} $ "
              f"{d['rendement_annuel_pct']:8.1f} % {d['drawdown_max_pct']:10.1f} % "
              f"{d['risque_moyen_pct']:12.2f} % {d['part_saturee_pct']:11.1f} %".replace(",", " "))
    print(f"\n  → {SORTIE / f'capitaux_{a.marche}.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

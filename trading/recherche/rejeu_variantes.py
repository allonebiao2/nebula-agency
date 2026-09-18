# -*- coding: utf-8 -*-
"""
Les variantes CAUSALES de LE REFLUX, sur l'année du rejeu (même moteur que l'agent).

    python -m trading.recherche.rejeu_variantes --marche NAS100

Question posée après le rejeu du 2026-09-18 : l'avantage de la recherche venait-il des entrées
PROFONDES (que le banc choisissait en sachant que le prix irait jusque-là) ? Si oui, une règle qui
n'arme que l'ordre le plus éloigné, ou qui pose l'ordre plus bas dès le départ, devrait le retrouver
sans regarder l'avenir. Chaque variante est jugée sans filtre ET avec les filtres trimestriels du
rejeu (appris sur les trades du banc : c'est justement ce qui est en cause).
⚠️ Ces variantes sont choisies APRÈS avoir vu que la version d'origine perd : c'est de la recherche,
chaque ligne compte au registre, et rien ne vaut preuve tant qu'une période neuve ne l'a pas confirmé.
"""
from __future__ import annotations

import argparse
import json
import sys

import joblib
import numpy as np
import pandas as pd

from . import banc
from .candidat import REGLAGES
from .caracteristiques import construire_aux_barres
from .rejeu import SORTIE, rejouer

VARIANTES = [
    ("d'origine : premier touché, retrait 0,5 R", "premier", {}),
    ("le plus profond, retrait 0,5 R", "profond", {}),
    ("premier touché, retrait 1,0 R", "premier", {"retrait": 1.0}),
    ("premier touché, retrait 1,5 R", "premier", {"retrait": 1.5}),
]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--marche", default="NAS100")
    a = ap.parse_args()
    marche = a.marche.upper()
    serie = banc.charger(marche, "M1")
    fin = pd.Timestamp(serie.temps[-1])
    debut = (fin - pd.DateOffset(years=1)).normalize()
    filtres = joblib.load(SORTIE / f"filtres_{marche}_{debut:%Y%m%d}.joblib")
    j0 = int(np.searchsorted(serie.temps, np.datetime64(debut.to_datetime64(), "s")))
    n = len(serie)
    X, noms = construire_aux_barres(serie, np.arange(j0, n))
    proba = np.full(n, np.nan)
    seuils = np.full(n, np.inf)
    t = pd.DatetimeIndex(serie.temps)
    ok = np.isfinite(X).all(axis=1)
    for f in filtres:
        m = (t[j0:] >= f["debut"]) & (t[j0:] < f["fin"])
        if (m & ok).any():
            proba[j0:][m & ok] = f["modele"].predict_proba(X[m & ok])[:, 1]
        seuils[j0:][m] = f["seuil"]
    lignes = []
    print(f"  {marche}, {debut:%Y-%m-%d} → {fin:%Y-%m-%d}, capital sans contrainte, prix et coûts Deriv\n")
    for nom, choix, regl in VARIANTES:
        for filtre in (False, True):
            res = rejouer(marche, 1e9, filtres, levier_max=None, serie=serie, X=X, noms=noms,
                          proba=proba if filtre else np.ones(n), seuils=seuils if filtre else np.zeros(n),
                          j0=j0, reglages=dict(REGLAGES, **regl), choix=choix)
            R = np.array([x["R"] for x in res["notes"]])
            obj = np.array([x["motif"] == "objectif" for x in res["notes"]])
            ligne = {"variante": nom, "filtre": filtre, "trades": len(R),
                     "taux_objectif": round(float(obj.mean()), 4) if len(R) else None,
                     "esperance_R": round(float(R.mean()), 4) if len(R) else None,
                     "somme_R": round(float(R.sum()), 1) if len(R) else None}
            lignes.append(ligne)
            print(f"  {nom:<44} {'filtre 5 %' if filtre else 'sans filtre':<11} "
                  f"{ligne['trades']:>6} trades  {100 * (ligne['taux_objectif'] or 0):5.1f} % de 2 R  "
                  f"{(ligne['esperance_R'] or 0):+.3f} R", flush=True)
    (SORTIE / f"variantes_{marche}.json").write_text(json.dumps(lignes, ensure_ascii=False, indent=1),
                                                    encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

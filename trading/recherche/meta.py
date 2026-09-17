# -*- coding: utf-8 -*-
"""
La sonde de prévisibilité, puis le modèle : **peut-on savoir À L'AVANCE dans quel sens 2 R tombera ?**

    python -m trading.recherche.meta --base NAS100 --tf M1 --schema pts1200
    python -m trading.recherche.meta --base EURUSD --tf M1 --schema pts50 --sous-echantillon 3

La vague 1 a mesuré le plafond : environ 64 % sur NAS100 M1, 57 % sur EUR/USD M1. Autrement dit, pour
tenir l'objectif de Mongazi (plus de 50 % de 2 R atteints), il faut choisir le bon sens **dans trois
cas sur quatre**. Ce fichier mesure ce qu'on sait vraiment faire, sans se raconter d'histoire :

  · un modèle par sens (achat, vente) apprend P(2 R avant 1 R) sur les caractéristiques causales ;
  · **walk-forward purgé** : on apprend sur le passé, on juge sur l'avenir, et on jette les exemples
    d'apprentissage dont le trade déborde sur la période de test (sinon le modèle a déjà vu la
    réponse : c'est la fuite la plus discrète de tout l'apprentissage sur séries financières) ;
  · on lit la **précision des meilleures probabilités** : parmi les 1 % de minutes où le modèle est
    le plus sûr, combien atteignent vraiment 2 R ? C'est le seul chiffre qui compte ;
  · les trades retenus repassent par `banc.simuler` : une position à la fois, coût de la minute,
    clôture en fin de journée. Jamais jugés sur les étiquettes seules.

⚠️ Témoins obligatoires (`--temoin`) : étiquettes mélangées → la précision doit retomber au taux de
base. Sans ce contrôle, un pipeline qui fuit ressemble exactement à un pipeline qui marche.
"""
from __future__ import annotations

import argparse
import json
import sys
import time

import numpy as np

from . import banc, caracteristiques, etiquettes, scelle
from .intraday import fin_de_journee
from .lancer import DOSSIER, enregistrer_test

SORTIE = DOSSIER / "meta"
DECILES = (0.5, 0.2, 0.1, 0.05, 0.02, 0.01)


def jeu(serie: banc.Serie, schema: str):
    """Les caractéristiques, les deux étiquettes, et le masque des barres utilisables."""
    X = caracteristiques.construire(serie)
    noms = sorted(X)
    M = np.column_stack([X[n] for n in noms]).astype(np.float32)
    deux = etiquettes.deux_sens(serie, schema)
    ok = deux[1].valides() & deux[-1].valides() & np.isfinite(M).all(axis=1)
    return M, noms, deux, ok


def _modele():
    from sklearn.ensemble import HistGradientBoostingClassifier
    return HistGradientBoostingClassifier(
        max_iter=250, learning_rate=0.06, max_leaf_nodes=31, min_samples_leaf=200,
        l2_regularization=1.0, early_stopping=True, validation_fraction=0.1, random_state=7)


def precision_par_seuil(proba: np.ndarray, verite: np.ndarray) -> list[dict]:
    """Parmi les X % de minutes les plus sûres, quelle part atteint vraiment 2 R ?"""
    out = []
    ordre = np.argsort(-proba)
    for part in DECILES:
        k = max(30, int(len(proba) * part))
        if k > len(proba):
            continue
        sel = ordre[:k]
        out.append({"part": part, "n": int(k), "precision": round(float(verite[sel].mean()), 4),
                    "proba_min": round(float(proba[sel].min()), 4)})
    return out


def sonder(serie: banc.Serie, schema: str, *, plis: int = 5, sous_echantillon: int = 1,
           embargo_barres: int | None = None, melanger: bool = False) -> dict:
    """Walk-forward purgé sur une série. Rend la précision par sens et la simulation des trades."""
    M, noms, deux, ok = jeu(serie, schema)
    n = len(serie)
    if embargo_barres is None:
        embargo_barres = int(24 * 60 / serie.minutes)          # une journée
    bornes = np.linspace(int(n * 0.35), n, plis + 1).astype(int)
    rng = np.random.default_rng(11)
    proba = {1: np.full(n, np.nan), -1: np.full(n, np.nan)}
    detail = []
    for p in range(plis):
        t0, t1 = bornes[p], bornes[p + 1]
        fin_app = t0 - embargo_barres
        app = np.zeros(n, bool)
        app[:fin_app] = True
        # Purge : un exemple d'apprentissage dont le trade déborde après `fin_app` a vu le futur.
        app &= ok
        for sens in (1, -1):
            e = deux[sens]
            deborde = np.zeros(n, bool)
            idx = np.flatnonzero(app)
            deborde[idx] = (idx + 1 + e.duree[idx]) >= fin_app
            i_app = np.flatnonzero(app & ~deborde)
            if sous_echantillon > 1:
                i_app = i_app[::sous_echantillon]
            y = e.objectif()[i_app].astype(np.int8)
            if melanger:                                        # TÉMOIN : la réponse est détruite
                y = rng.permutation(y)
            if len(i_app) < 5000 or y.sum() < 100:
                continue
            modele = _modele()
            modele.fit(M[i_app], y)
            i_test = np.flatnonzero(ok & (np.arange(n) >= t0) & (np.arange(n) < t1))
            if not len(i_test):
                continue
            proba[sens][i_test] = modele.predict_proba(M[i_test])[:, 1]
            detail.append({"pli": p, "sens": sens, "apprentissage": int(len(i_app)),
                           "test": int(len(i_test)),
                           "taux_base_test": round(float(e.objectif()[i_test].mean()), 4),
                           "precision": precision_par_seuil(proba[sens][i_test], e.objectif()[i_test])})
        print(f"    pli {p + 1}/{plis} : {str(serie.temps[t0])[:10]} → {str(serie.temps[t1 - 1])[:10]}",
              flush=True)
    return {"noms": noms, "detail": detail, "proba": proba, "deux": deux, "ok": ok}


def trades_du_modele(serie: banc.Serie, schema: str, proba: dict, ok: np.ndarray, seuil: float):
    """Le modèle choisit un sens quand il dépasse le seuil ; le banc, lui, tranche."""
    pa, pv = np.nan_to_num(proba[1], nan=-1), np.nan_to_num(proba[-1], nan=-1)
    sens = np.where((pa >= seuil) & (pa >= pv), 1, np.where((pv >= seuil) & (pv > pa), -1, 0)).astype(np.int8)
    sens[~ok] = 0
    sig = banc.Signaux(sens=sens, stop_dist=etiquettes.distances(serie, schema), rr=2.0,
                       max_barres=int(24 * 60 / serie.minutes),
                       fin_seance=fin_de_journee(serie.base, serie.temps))
    return banc.simuler(serie, sig)


def lancer(base: str, tf: str, schema: str, *, plis: int = 5, sous_echantillon: int = 1,
           temoin: bool = False) -> dict:
    SORTIE.mkdir(parents=True, exist_ok=True)
    resultats = []
    for serie in scelle.series_decouverte(base, tf):
        etiquette = f"{serie.source} {str(serie.temps[0])[:7]}→{str(serie.temps[-1])[:7]}"
        print(f"  {base} {tf} {schema} · {etiquette} · {len(serie)} barres", flush=True)
        t0 = time.time()
        s = sonder(serie, schema, plis=plis, sous_echantillon=sous_echantillon, melanger=temoin)
        for d in s["detail"]:
            ligne = ", ".join(f"{100 * p['precision']:.1f} % sur {p['part']:.0%}" for p in d["precision"])
            print(f"      sens {d['sens']:+d} pli {d['pli']} base {100 * d['taux_base_test']:.1f} % → {ligne}",
                  flush=True)
        # Ce que ça donne vraiment, une position à la fois
        mesures = {}
        for seuil in (0.40, 0.45, 0.50, 0.55, 0.60):
            t = trades_du_modele(serie, schema, s["proba"], s["ok"], seuil)
            if len(t) >= 30:
                m = banc.mesurer(serie, t, series=len(t) <= 20000)
                mesures[f"{seuil:.2f}"] = {k: m[k] for k in ("trades", "taux_reussite", "taux_objectif",
                                                             "point_mort_objectif", "p_objectif",
                                                             "esperance_R", "profit_factor")}
                d = mesures[f"{seuil:.2f}"]
                # Chaque seuil essayé est un test : il entre au registre, qu'il plaise ou non.
                enregistrer_test(f"meta_{base}_{tf}_{schema}_s{seuil:.2f}{'_temoin' if temoin else ''}",
                                 {"tour": 5, "candidate": f"meta_{schema}", "base": base, "tf": tf,
                                  "temoin": temoin, "combinaisons": 1, "vague": "3 · méta-étiquetage",
                                  **{k: m.get(k) for k in ("trades", "taux_reussite", "taux_objectif",
                                                           "point_mort_objectif", "p_objectif",
                                                           "esperance_R", "profit_factor", "p_valeur",
                                                           "drawdown_max_pct", "R_par_mois",
                                                           "trades_par_mois", "debut", "fin")}})
                print(f"      seuil {seuil:.2f} : {d['trades']:6d} trades, objectif "
                      f"{100 * d['taux_objectif']:5.1f} % (point mort {100 * d['point_mort_objectif']:.1f} %), "
                      f"{d['esperance_R']:+.3f} R, p={d['p_objectif']:.3g}", flush=True)
        resultats.append({"base": base, "tf": tf, "schema": schema, "source": etiquette,
                          "temoin": temoin, "secondes": round(time.time() - t0, 1),
                          "detail": [{k: v for k, v in d.items()} for d in s["detail"]],
                          "seuils": mesures})
        del s
    nom = f"meta_{base}_{tf}_{schema}{'_temoin' if temoin else ''}.json"
    (SORTIE / nom).write_text(json.dumps(resultats, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"  → {SORTIE / nom}")
    return {"fichier": str(SORTIE / nom), "resultats": resultats}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="NAS100")
    p.add_argument("--tf", default="M1")
    p.add_argument("--schema", default="pts1200")
    p.add_argument("--plis", type=int, default=5)
    p.add_argument("--sous-echantillon", type=int, default=1)
    p.add_argument("--temoin", action="store_true", help="étiquettes mélangées : doit retomber au taux de base")
    a = p.parse_args()
    lancer(a.base, a.tf, a.schema, plis=a.plis, sous_echantillon=a.sous_echantillon, temoin=a.temoin)
    return 0


if __name__ == "__main__":
    sys.exit(main())

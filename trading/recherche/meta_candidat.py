# -*- coding: utf-8 -*-
"""
Filtrer le candidat : peut-on faire passer ses 40 % de 2 R au-dessus de 50 % en refusant des trades ?

    python -m trading.recherche.meta_candidat --base NAS100 --tf M1

Le candidat (`candidat.py`) atteint 2 R dans **40,3 %** des cas sur le scellé. Mongazi en veut plus de
50. Ici, on ne cherche pas une nouvelle stratégie : on apprend **quand ne pas prendre** celle-ci.
C'est le méta-étiquetage au sens propre — un modèle primaire qui décide du sens, un modèle secondaire
qui décide s'il faut y aller.

Trois précautions, sinon le résultat est faux et flatteur :
  · les caractéristiques sont lues **à la barre du signal**, jamais à l'entrée (l'ordre limite peut
    être servi une heure plus tard : lire le prix du moment de l'entrée serait regarder le futur) ;
  · **walk-forward purgé** : on apprend sur le passé, et on jette les trades d'apprentissage qui se
    terminent après le début du test ;
  · le filtre ne change ni le sens, ni le stop, ni l'objectif. Il ne fait que **retirer des trades**,
    donc son effet se lit directement sur le taux de 2 R et sur le nombre de trades restants.
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from . import banc, candidates_v2, caracteristiques, scelle
from .banc import OBJECTIF
from .candidat import REGLAGES
from .lancer import DOSSIER, enregistrer_test

SORTIE = DOSSIER / "meta"
PARTS = (1.0, 0.5, 0.3, 0.2, 0.1, 0.05)


def trades_et_caracteristiques(serie: banc.Serie):
    """Les trades du candidat, et ce qu'on savait à la barre du signal de chacun."""
    ordres = candidates_v2.rabais(serie, **REGLAGES)
    t = banc.simuler(serie, ordres)
    if not len(t):
        return None
    X = caracteristiques.construire(serie)
    noms = sorted(X)
    M = np.column_stack([X[n] for n in noms]).astype(np.float32)
    # ⛔ FUITE D'UNE MINUTE, mesurée le 2026-09-17 : lire les caractéristiques de la barre où l'ordre
    # est SERVI utilise sa clôture, c'est-à-dire le prix de la fin de la minute pendant laquelle on
    # est entré — donc une partie du rebond qu'on prétend prédire. Résultat : 65 % de 2 R, même sur
    # une période où la stratégie perd. On lit la **dernière barre close avant le remplissage**,
    # la seule information dont on dispose réellement au moment d'entrer.
    i_signal = np.maximum(t.entree - 1, 0)
    ok = np.isfinite(M[i_signal]).all(axis=1)
    return {"trades": t, "i_signal": i_signal, "X": M, "noms": noms, "ok": ok,
            "objectif": (t.motif == OBJECTIF)}


def filtrer(serie: banc.Serie, *, plis: int = 4, part_apprentissage: float = 0.35,
            melanger: bool = False, recul: int = 0) -> dict:
    """`melanger` : TÉMOIN, les étiquettes sont détruites — tout gain restant est une fuite.
    `recul` : lire les caractéristiques N barres plus tôt encore. Un avantage réel doit s'atténuer
    doucement ; un artefact d'une minute disparaît d'un coup."""
    d = trades_et_caracteristiques(serie)
    if d is None:
        return {"trades": 0}
    from sklearn.ensemble import HistGradientBoostingClassifier
    t, i_signal, M, ok, y = d["trades"], d["i_signal"], d["X"], d["ok"], d["objectif"]
    if recul:
        i_signal = np.maximum(i_signal - recul, 0)
    if melanger:
        y = np.random.default_rng(3).permutation(y)
    n = len(t)
    bornes = np.linspace(int(n * part_apprentissage), n, plis + 1).astype(int)
    proba = np.full(n, np.nan)
    for p in range(plis):
        a, b = bornes[p], bornes[p + 1]
        # Purge : un trade d'apprentissage qui se termine APRÈS le début du test a vu le futur.
        fin_app = np.searchsorted(t.sortie, t.entree[a], side="left")
        app = np.zeros(n, bool)
        app[:min(a, fin_app)] = True
        app &= ok
        if app.sum() < 2000 or y[app].sum() < 200:
            continue
        modele = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.06, max_leaf_nodes=31,
                                                min_samples_leaf=100, l2_regularization=1.0,
                                                early_stopping=True, validation_fraction=0.15,
                                                random_state=5)
        modele.fit(M[i_signal[app]], y[app].astype(np.int8))
        test = np.zeros(n, bool)
        test[a:b] = True
        test &= ok
        if test.any():
            proba[test] = modele.predict_proba(M[i_signal[test]])[:, 1]
    juge = np.isfinite(proba)
    if juge.sum() < 200:
        return {"trades": int(juge.sum())}
    sortie = {"trades_juges": int(juge.sum()),
              "taux_objectif_sans_filtre": round(float(y[juge].mean()), 4),
              "esperance_sans_filtre": round(float(t.R[juge].mean()), 4), "paliers": []}
    ordre = np.argsort(-proba[juge])
    R_j, y_j = t.R[juge], y[juge]
    for part in PARTS:
        k = int(len(ordre) * part)
        if k < 100:
            continue
        sel = ordre[:k]
        Rs = R_j[sel]
        sortie["paliers"].append({
            "part_gardee": part, "trades": int(k), "taux_objectif": round(float(y_j[sel].mean()), 4),
            "esperance_R": round(float(Rs.mean()), 4),
            "point_mort": round(banc.point_mort_objectif(Rs, y_j[sel]), 4),
            "p_objectif": banc.p_binomial(int(y_j[sel].sum()), k,
                                          banc.point_mort_objectif(Rs, y_j[sel]))})
    return sortie


def essai_scelle(*, entrainement=("2013-01-01", "2020-01-01"),
                 scelle_periode=("2020-01-01", "2024-01-01"), melanger: bool = False) -> dict:
    """LE test du filtre : apprendre sur des années strictement ANTÉRIEURES, juger sur le scellé.

    Pas de walk-forward ici, pas de réglage : un modèle appris une fois sur 2013-2019, appliqué tel
    quel à 2020-2023. Si le filtre est une illusion, c'est ici qu'elle tombe.
    """
    from sklearn.ensemble import HistGradientBoostingClassifier
    s_app = banc.charger("NAS100", "M1", source="duka").tranche(*entrainement)
    s_test = banc.charger("NAS100", "M1", source="duka").tranche(*scelle_periode)
    a, b = trades_et_caracteristiques(s_app), trades_et_caracteristiques(s_test)
    ya = a["objectif"][a["ok"]].astype(np.int8)
    if melanger:
        ya = np.random.default_rng(3).permutation(ya)
    modele = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.06, max_leaf_nodes=31,
                                            min_samples_leaf=100, l2_regularization=1.0,
                                            early_stopping=True, validation_fraction=0.15,
                                            random_state=5)
    modele.fit(a["X"][a["i_signal"][a["ok"]]], ya)
    proba = modele.predict_proba(b["X"][b["i_signal"][b["ok"]]])[:, 1]
    t, y = b["trades"], b["objectif"][b["ok"]]
    R = t.R[b["ok"]]
    ordre = np.argsort(-proba)
    sortie = {"entrainement": list(entrainement), "scelle": list(scelle_periode),
              "trades_appris": int(a["ok"].sum()), "trades_juges": int(b["ok"].sum()),
              "taux_sans_filtre": round(float(y.mean()), 4),
              "esperance_sans_filtre": round(float(R.mean()), 4), "temoin": melanger, "paliers": []}
    from .compte import series_perdantes
    for part in PARTS:
        k = int(len(ordre) * part)
        if k < 100:
            continue
        sel = np.sort(ordre[:k])                       # remettre dans l'ordre du temps
        Rs, ys = R[sel], y[sel]
        p0 = banc.point_mort_objectif(Rs, ys)
        sp = series_perdantes(Rs, fenetre=100)
        sortie["paliers"].append({
            "part_gardee": part, "trades": int(k), "taux_objectif": round(float(ys.mean()), 4),
            "point_mort": round(p0, 4), "esperance_R": round(float(Rs.mean()), 4),
            "p_objectif": banc.p_binomial(int(ys.sum()), k, p0),
            "rr_realise": round(abs(Rs[Rs > 0].mean() / Rs[Rs <= 0].mean()), 2) if (Rs <= 0).any() else None,
            "p_5_pertes_sur_100": sp["p_5_pertes_sur_100_montecarlo"],
            "p_6_pertes_sur_100": sp["p_6_pertes_sur_100_montecarlo"],
            "plus_longue_serie": sp["plus_longue_observee"]})
    return sortie


def lancer(base: str, tf: str) -> dict:
    SORTIE.mkdir(parents=True, exist_ok=True)
    resultats = []
    for serie in scelle.series_decouverte(base, tf):
        etiquette = f"{serie.source} {str(serie.temps[0])[:7]}→{str(serie.temps[-1])[:7]}"
        print(f"\n  {base} {tf} · {etiquette} · {len(serie)} barres", flush=True)
        d = filtrer(serie)
        if not d.get("paliers"):
            print("    trop peu de trades jugés", flush=True)
            continue
        print(f"    sans filtre : {d['trades_juges']} trades, "
              f"{100 * d['taux_objectif_sans_filtre']:.1f} % de 2 R, "
              f"{d['esperance_sans_filtre']:+.3f} R", flush=True)
        for p in d["paliers"]:
            print(f"    garder {100 * p['part_gardee']:5.0f} % : {p['trades']:6d} trades, "
                  f"{100 * p['taux_objectif']:5.1f} % de 2 R (point mort "
                  f"{100 * p['point_mort']:.1f} %), {p['esperance_R']:+.3f} R, "
                  f"p={p['p_objectif']:.2e}", flush=True)
            enregistrer_test(f"meta_candidat_{base}_{tf}_{serie.source}_{p['part_gardee']}", {
                "tour": 9, "candidate": "meta_candidat_rabais", "base": base, "tf": tf,
                "temoin": False, "combinaisons": len(PARTS), "vague": "5 · filtre du candidat",
                "trades": p["trades"], "taux_objectif": p["taux_objectif"],
                "point_mort_objectif": p["point_mort"], "p_objectif": p["p_objectif"],
                "esperance_R": p["esperance_R"], "taux_reussite": None, "profit_factor": None,
                "p_valeur": None})
        resultats.append({"source": etiquette, **d})
    (SORTIE / f"meta_candidat_{base}_{tf}.json").write_text(
        json.dumps(resultats, ensure_ascii=False, default=str), encoding="utf-8")
    return {"resultats": resultats}


def modele_2013_2019():
    """Le modèle du filtre : appris UNE fois sur 2013-2019, jamais réglé ailleurs."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    s = banc.charger("NAS100", "M1", source="duka").tranche("2013-01-01", "2020-01-01")
    d = trades_et_caracteristiques(s)
    m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.06, max_leaf_nodes=31,
                                       min_samples_leaf=100, l2_regularization=1.0,
                                       early_stopping=True, validation_fraction=0.15,
                                       random_state=5)
    m.fit(d["X"][d["i_signal"][d["ok"]]], d["objectif"][d["ok"]].astype(np.int8))
    return m, int(d["ok"].sum())


def juger(modele, serie: banc.Serie, libelle: str) -> dict:
    """Appliquer le filtre à une période, et rendre les trois chiffres de Mongazi par palier."""
    from .compte import series_perdantes
    d = trades_et_caracteristiques(serie)
    if d is None:
        return {"libelle": libelle, "trades": 0}
    p = modele.predict_proba(d["X"][d["i_signal"][d["ok"]]])[:, 1]
    y, R = d["objectif"][d["ok"]], d["trades"].R[d["ok"]]
    sens = d["trades"].sens[d["ok"]]
    annees = serie.temps[d["trades"].entree[d["ok"]]].astype("datetime64[Y]").astype(int) + 1970
    paliers = []
    for part in PARTS:
        sel = p >= np.quantile(p, 1 - part) if part < 1 else np.ones(len(p), bool)
        if sel.sum() < 100:
            continue
        Rs, ys = R[sel], y[sel]
        sp = series_perdantes(Rs, fenetre=100)
        paliers.append({
            "part_gardee": part, "trades": int(sel.sum()), "taux_objectif": round(float(ys.mean()), 4),
            "point_mort": round(banc.point_mort_objectif(Rs, ys), 4),
            "esperance_R": round(float(Rs.mean()), 4),
            "rr_realise": round(abs(Rs[Rs > 0].mean() / Rs[Rs <= 0].mean()), 2) if (Rs <= 0).any() else None,
            "p_5_pertes_sur_100": sp["p_5_pertes_sur_100_montecarlo"],
            "p_6_pertes_sur_100": sp["p_6_pertes_sur_100_montecarlo"],
            "plus_longue_serie": sp["plus_longue_observee"],
            "part_achat": round(float((sens[sel] > 0).mean()), 3),
            "par_an": {int(an): round(float(ys[annees[sel] == an].mean()), 4)
                       for an in np.unique(annees[sel]) if (annees[sel] == an).sum() > 30}})
    return {"libelle": libelle, "trades": int(d["ok"].sum()), "paliers": paliers}


def tout(base: str = "NAS100", tf: str = "M1") -> dict:
    modele, n_app = modele_2013_2019()
    jeux = [(("SCELLÉ · Dukascopy 2020-2023"),
             banc.charger(base, tf, source="duka").tranche("2020-01-01", "2024-01-01")),
            ("Deriv 2024-2026", banc.charger(base, tf)),
            ("Dukascopy 2024-2026", banc.charger(base, tf, source="duka").tranche("2024-01-01", None))]
    jeux += [(f"Deriv 2024-2026 · coût ×{k:.0f}", banc.charger(base, tf, multiplicateur_couts=k))
             for k in (2.0, 3.0, 5.0)]
    resultats = [juger(modele, s, lib) for lib, s in jeux]
    # TÉMOIN : le même pipeline avec des étiquettes détruites. Tout gain restant serait une fuite.
    temoin = essai_scelle(melanger=True)
    sortie = {"trades_appris": n_app, "resultats": resultats, "temoin_melange": temoin}
    SORTIE.mkdir(parents=True, exist_ok=True)
    (SORTIE / "candidat_filtre.json").write_text(json.dumps(sortie, ensure_ascii=False, default=str),
                                                 encoding="utf-8")
    for r in resultats:
        if not r.get("paliers"):
            continue
        print(f"\n  {r['libelle']} · {r['trades']} trades")
        for p in r["paliers"]:
            print(f"    garder {100 * p['part_gardee']:5.0f} % : {p['trades']:6d} trades  "
                  f"{100 * p['taux_objectif']:5.1f} % de 2 R  R:R {p['rr_realise']}  "
                  f"{p['esperance_R']:+.3f} R  P(5/100) {100 * p['p_5_pertes_sur_100']:.0f} %  "
                  f"P(6/100) {100 * p['p_6_pertes_sur_100']:.0f} %  "
                  f"série max {p['plus_longue_serie']}  achats {100 * p['part_achat']:.0f} %")
        for p in r["paliers"]:
            if p["part_gardee"] == 0.05:
                enregistrer_test(f"filtre_{r['libelle'][:30]}_5pct", {
                    "tour": 10, "candidate": "candidat_filtre_5pct", "base": base, "tf": tf,
                    "temoin": False, "combinaisons": len(PARTS), "vague": "5 · candidat filtré",
                    "trades": p["trades"], "taux_objectif": p["taux_objectif"],
                    "point_mort_objectif": p["point_mort"], "esperance_R": p["esperance_R"],
                    "p_objectif": banc.p_binomial(int(round(p["taux_objectif"] * p["trades"])),
                                                  p["trades"], p["point_mort"]),
                    "taux_reussite": None, "profit_factor": None, "p_valeur": None})
    t5 = next((x for x in temoin["paliers"] if x["part_gardee"] == 0.05), None)
    if t5:
        print(f"\n  TÉMOIN (étiquettes mélangées), garder 5 % : {100 * t5['taux_objectif']:.1f} % de 2 R "
              f"contre {100 * temoin['taux_sans_filtre']:.1f} % sans filtre — l'écart qui reste est"
              f" l'effet de SÉLECTION, pas de prédiction.")
    return sortie


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="NAS100")
    p.add_argument("--tf", default="M1")
    p.add_argument("--walkforward", action="store_true", help="l'ancien mode, walk-forward par série")
    a = p.parse_args()
    if a.walkforward:
        lancer(a.base, a.tf)
    else:
        tout(a.base, a.tf)
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""
LE TEST D'UN AN : l'agent LE REFLUX rejoué minute par minute sur les 12 derniers mois.

    python -m trading.recherche.rejeu --marche EURUSD --capital 10
    python -m trading.recherche.rejeu --tout            # les deux marchés, 10 $, avec et sans plafond

Demande de Mongazi (2026-09-18) : « fais le test sur 1 an avec un capital de 10 dollars sur chacun,
et prends les notes pour le deep learning ».

Ce qui distingue ce test des backtests précédents, et pourquoi ses chiffres peuvent être plus bas :
  1. **Le moteur est celui de l'agent** (`live/moteur_scalp.py`) : c'est l'ordre touché le PREMIER
     qui entre, comme chez un courtier. La recherche donnait le trade au plus ancien ordre servi.
  2. **Le filtre n'a jamais vu l'année** : réappris chaque trimestre sur les seuls trades CLOS avant
     le trimestre (Dukascopy, tout l'historique), et son seuil est le quantile des probabilités des
     quatre trimestres PRÉCÉDENTS. Le modèle posé sur le disque, lui, a appris jusqu'au 16/09/2026 :
     rejouer l'année avec lui serait se juger sur sa propre copie.
  3. **Les prix et les coûts sont ceux de Deriv**, le courtier où l'on tradera, minute par minute.
  4. **Le compte est réel** : 10 $ de départ, lots minimum, pas et maximum du courtier, échelle 6-4-3
     par `noyau/profils.risque_courant`, taille par `noyau/risque.dimensionner` (le code de l'agent).
  5. **Le levier est mesuré trade par trade**, et le test tourne deux fois : avec le plafond de la
     configuration (x30, profil BOOST) et sans plafond (ce que supposaient les calculs précédents).

Les NOTES : chaque trade est écrit en entier dans `trading/rapports/rejeu/*.jsonl` (les 38
caractéristiques de la barre qui a armé l'ordre, la probabilité, le seuil, le prix voulu et le prix
obtenu, le coût payé, le plus loin allé pour et contre, la durée, le palier de risque, les lots, le
levier, le résultat). C'est la matière du réapprentissage et de l'analyse trade par trade.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from ..live import moteur_scalp as ms
from ..noyau import profils
from ..noyau.donnees_mt5 import specs_et_couts
from ..noyau.risque import dimensionner
from . import banc, candidates_v2
from .banc import OBJECTIF, STOP, GAP, SEANCE, TEMPS
from .candidat import REGLAGES
from .caracteristiques import construire_aux_barres
from .compte import _config_echelle
from .intraday import minutes_et_jours
from .lancer import DOSSIER

SORTIE = DOSSIER / "rejeu"
ECHELLE = ((0.0, 6.0), (0.0001, 4.0), (0.20, 3.0))
PART = 0.05
MOTIFS = {OBJECTIF: "objectif", STOP: "stop", GAP: "saut au-delà du stop", SEANCE: "fin de journée",
          TEMPS: "durée max"}


def _modele():
    from sklearn.ensemble import HistGradientBoostingClassifier
    return HistGradientBoostingClassifier(max_iter=200, learning_rate=0.06, max_leaf_nodes=31,
                                          min_samples_leaf=100, l2_regularization=1.0,
                                          early_stopping=True, validation_fraction=0.15,
                                          random_state=5)


# --------------------------------------------------------------------------- #
#  1. Les filtres, un par trimestre, sans jamais voir l'avenir
# --------------------------------------------------------------------------- #

def filtres_trimestriels(marche: str, debut: pd.Timestamp, trimestres: int = 4,
                         historique_seuil: int = 4) -> list[dict]:
    """Pour chaque trimestre du rejeu : un modèle appris sur les trades clos AVANT lui, et un seuil
    tiré des probabilités hors échantillon des `historique_seuil` trimestres précédents."""
    duka = banc.charger(marche, "M1", source="duka")
    ordres = candidates_v2.rabais(duka, **REGLAGES)
    t = banc.simuler(duka, ordres)
    del ordres
    i_signal = np.maximum(t.entree - 1, 0)
    X, noms = construire_aux_barres(duka, i_signal)
    ok = np.isfinite(X).all(axis=1)
    y = t.motif == OBJECTIF
    entree = duka.temps[t.entree]
    sortie = duka.temps[t.sortie]
    del duka
    departs = [debut + pd.DateOffset(months=3 * k) for k in range(-historique_seuil, trimestres)]
    blocs = []
    for T in departs:
        T2 = T + pd.DateOffset(months=3)
        t64, t264 = np.datetime64(T.to_datetime64(), "s"), np.datetime64(T2.to_datetime64(), "s")
        app = ok & (sortie < t64)
        test = ok & (entree >= t64) & (entree < t264)
        m = _modele()
        m.fit(X[app], y[app].astype(np.int8))
        p = m.predict_proba(X[test])[:, 1] if test.any() else np.array([])
        blocs.append({"debut": T, "fin": T2, "modele": m, "proba_oos": p, "y_oos": y[test],
                      "R_oos": t.R[test], "appris": int(app.sum()),
                      "taux_appris": round(float(y[app].mean()), 4)})
    sortie_blocs = []
    for k in range(historique_seuil, len(blocs)):
        passe = np.concatenate([blocs[i]["proba_oos"] for i in range(k - historique_seuil, k)])
        seuil = float(np.quantile(passe, 1 - PART))
        b = blocs[k]
        garde = b["proba_oos"] >= seuil
        sortie_blocs.append({
            "debut": b["debut"], "fin": b["fin"], "modele": b["modele"], "seuil": seuil,
            "noms": noms, "appris": b["appris"],
            # Ce que la RECHERCHE aurait dit de ce trimestre (prix Dukascopy, sélection non causale)
            "recherche": {"trades": int(garde.sum()),
                          "taux_objectif": round(float(b["y_oos"][garde].mean()), 4) if garde.any() else None,
                          "esperance_R": round(float(b["R_oos"][garde].mean()), 4) if garde.any() else None,
                          "part_gardee": round(float(garde.mean()), 4) if len(garde) else None}})
    return sortie_blocs


# --------------------------------------------------------------------------- #
#  2. Le rejeu, minute par minute
# --------------------------------------------------------------------------- #

def rejouer(marche: str, capital: float, filtres: list[dict], *, levier_max: float | None,
            serie=None, X=None, noms=None, proba=None, seuils=None, j0: int | None = None,
            reglages: dict | None = None, j_fin: int | None = None, choix: str = "premier") -> dict:
    serie = serie if serie is not None else banc.charger(marche, "M1")
    n = len(serie) if j_fin is None else j_fin
    specs, _ = specs_et_couts(marche)
    ordres = candidates_v2.rabais(serie, **(reglages or REGLAGES))
    idx = ms.index_des_ordres(ordres, len(serie))
    sens_barre = ms.sens_par_barre(ordres, len(serie))
    fin = ordres.fin_seance
    couts = serie.couts_prix()
    k_rempl = float(REGLAGES["remplissage"])
    max_barres = max(1, int(240 / serie.minutes))
    o_, h_, b_, c_ = serie.ouverture, serie.haut, serie.bas, serie.cloture
    minute, jsem = minutes_et_jours(serie.temps)

    cfg = _config_echelle(None, ECHELLE[0][1], ECHELLE)
    etat = profils.initialiser("plan", capital)
    equite = capital
    attente = ms.Attente()
    position = None
    armee = None                # (ordre, dimensionnement, barre qui a armé, risque %, drawdown)
    notes: list[dict] = []
    compteurs = {"barres_armees": 0, "ordres_armes": set(), "remplis": 0, "refus_taille": 0,
                 "capital_requis": [], "abandon_objectif": 0, "levier_trades": []}

    def fermer(j: int, sortie: float, motif: int) -> None:
        nonlocal position, equite
        p = position
        s = p["sens"]
        net = s * ((sortie - s * couts[j]) - p["entree_nette"])
        R = net / p["d"]
        pnl = R * p["risque_usd"]
        equite_avant = equite
        equite += pnl
        profils.maj_sommet(etat, equite)
        p.update({"sortie_a": str(serie.temps[j])[:16], "duree_min": int(j - p["j_rempli"]),
                  "motif": MOTIFS.get(motif, str(motif)), "R": round(float(R), 4),
                  "cout_sortie_pts": round(float(couts[j] / serie.point), 1),
                  "pnl_usd": round(float(pnl), 4), "capital_apres": round(float(equite), 4),
                  "capital_avant": round(float(equite_avant), 4)})
        p["j_rempli"], p["j_sortie"] = int(p["j_rempli"]), int(j)
        p.pop("entree_nette"), p.pop("d")
        notes.append(p)
        position = None

    for j in range(j0, n):
        # ---------- pendant la barre j : ce qui arrive AU PRIX ----------
        if position is not None:
            p, s = position, position["sens"]
            st, ci = p["stop"], p["cible"]
            p["mfe_R"] = max(p["mfe_R"], s * ((h_[j] if s > 0 else b_[j]) - p["entree_nette"]) / p["d"])
            p["mae_R"] = min(p["mae_R"], s * ((b_[j] if s > 0 else h_[j]) - p["entree_nette"]) / p["d"])
            if j > p["j_rempli"] and ((s > 0 and o_[j] <= st) or (s < 0 and o_[j] >= st)):
                fermer(j, o_[j], GAP)
            elif (s > 0 and b_[j] <= st) or (s < 0 and h_[j] >= st):
                fermer(j, st, STOP)
            elif j > p["j_rempli"] and ((s > 0 and h_[j] >= ci) or (s < 0 and b_[j] <= ci)):
                fermer(j, ci, OBJECTIF)
            elif fin[j]:
                fermer(j, c_[j], SEANCE)
            elif j - p["j_rempli"] >= max_barres:
                fermer(j, c_[j], TEMPS)
        elif armee is not None:
            o, taille, j_arme, risque_pct, dd = armee
            s = o.sens
            compteurs["barres_armees"] += 1
            if fin[j]:
                pass
            elif (s > 0 and h_[j] >= o.cible) or (s < 0 and b_[j] <= o.cible):
                compteurs["abandon_objectif"] += 1           # objectif touché avant d'être servi
            elif (s > 0 and b_[j] <= o.limite - k_rempl * couts[j]) or \
                 (s < 0 and h_[j] >= o.limite + k_rempl * couts[j]):
                prix = min(o.limite, o_[j]) if s > 0 else max(o.limite, o_[j])
                d = o.risque
                entree_nette = prix + s * couts[j]
                compteurs["remplis"] += 1
                compteurs["levier_trades"].append(taille.levier)
                position = {
                    "n": len(notes) + 1, "marche": marche, "sens": s,
                    "pose_a": str(serie.temps[o.pose])[:16], "arme_a": str(serie.temps[j_arme])[:16],
                    "rempli_a": str(serie.temps[j])[:16], "age_ordre_min": int(j - o.pose),
                    "limite": float(o.limite), "prix_rempli": float(prix), "stop": float(o.stop),
                    "cible": float(o.cible), "risque_points": round(float(d / serie.point), 1),
                    "cout_entree_pts": round(float(couts[j] / serie.point), 1),
                    "proba": round(float(proba[j_arme]), 4), "seuil": round(float(seuils[j_arme]), 4),
                    "minute_ny": int(minute[j]), "jour_semaine": int(jsem[j]),
                    "risque_pct_palier": risque_pct, "drawdown_avant_pct": round(100 * dd, 2),
                    "lots": taille.lots, "risque_usd": round(float(taille.risque_devise), 4),
                    "risque_pct_reel": round(float(taille.risque_pct), 3),
                    "levier": round(float(taille.levier), 1), "note_taille": taille.note,
                    "mfe_R": 0.0, "mae_R": 0.0,
                    "caracteristiques": ({} if X is None else
                                         {nm: (None if not np.isfinite(v) else round(float(v), 5))
                                          for nm, v in zip(noms, X[j_arme - j0])}),
                    "j_pose": o.pose,
                    "j_rempli": j, "entree_nette": entree_nette, "d": d}
                attente.vider()
                # La barre du remplissage peut déjà toucher le stop (la recherche fait pareil).
                if (s > 0 and b_[j] <= o.stop) or (s < 0 and h_[j] >= o.stop):
                    position["mae_R"] = -1.0
                    fermer(j, o.stop, STOP)
            armee = None

        # ---------- à la clôture de la barre j : ce que la stratégie DÉCIDE ----------
        if fin[j]:
            attente.vider()
            armee = None
            continue
        if position is not None or equite <= 0:
            continue
        attente.nettoyer(j, h_[j], b_[j], int(sens_barre[j]))
        nouvel = ms.ordre_de_la_barre(ordres, idx, j, serie.stop_min_prix)
        if nouvel is not None:
            attente.poser(nouvel)
        o = attente.meilleur(choix)
        if o is None or not ms.arme(proba[j], seuils[j]):
            continue
        risque_pct, _motif = profils.risque_courant(cfg, etat, equite)
        dd = profils.drawdown_courant(etat, equite)
        taille = dimensionner(capital=equite, risque_pct=risque_pct,
                              points_de_risque=o.risque / serie.point, specs=specs,
                              lots_total_max=specs.volume_max * 10, prix=o.limite, levier_max=levier_max)
        if not taille.autorise:
            compteurs["refus_taille"] += 1
            if taille.capital_requis:
                compteurs["capital_requis"].append(taille.capital_requis)
            continue
        compteurs["ordres_armes"].add(o.pose)
        armee = (o, taille, j, risque_pct, dd)

    if position is not None:
        fermer(n - 1, c_[n - 1], TEMPS)
    return {"notes": notes, "compteurs": compteurs, "capital_final": equite}


# --------------------------------------------------------------------------- #
#  3. Résumé
# --------------------------------------------------------------------------- #

def resumer(marche: str, capital: float, levier_max, res: dict, debut, fin_donnees) -> dict:
    notes, c = res["notes"], res["compteurs"]
    base = {"marche": marche, "capital_depart": capital,
            "plafond_levier": levier_max if levier_max else "aucun",
            "periode": [str(debut)[:10], str(fin_donnees)[:16]],
            "ordres_armes": len(c["ordres_armes"]), "barres_armees": c["barres_armees"],
            "refus_taille": c["refus_taille"],
            "capital_requis_median": (round(float(np.median(c["capital_requis"])), 1)
                                      if c["capital_requis"] else None),
            "trades": len(notes), "capital_final": round(float(res["capital_final"]), 2)}
    if not notes:
        return base
    R = np.array([t["R"] for t in notes])
    objectif = np.array([t["motif"] == "objectif" for t in notes])
    gains = R > 0
    serie_p, pire = 0, 0
    for g in gains:
        serie_p = 0 if g else serie_p + 1
        pire = max(pire, serie_p)
    eq = np.array([capital] + [t["capital_apres"] for t in notes])
    sommets = np.maximum.accumulate(eq)
    dd = float(np.max((sommets - eq) / sommets))
    mois = pd.Series([t["pnl_usd"] for t in notes],
                     index=pd.to_datetime([t["sortie_a"] for t in notes])).groupby(pd.Grouper(freq="MS")).sum()
    cap_mois = capital + mois.cumsum().shift(1).fillna(0.0)
    pct_mois = (mois / cap_mois * 100)
    lev = np.array([t["levier"] for t in notes])
    base.update({
        "taux_objectif": round(float(objectif.mean()), 4),
        "taux_gagnants": round(float(gains.mean()), 4),
        "ic95_objectif": [round(x, 4) for x in banc._wilson(int(objectif.sum()), len(R))],
        "esperance_R": round(float(R.mean()), 4), "somme_R": round(float(R.sum()), 1),
        "R_moyen_gain": round(float(R[gains].mean()), 3) if gains.any() else None,
        "R_moyen_perte": round(float(R[~gains].mean()), 3) if (~gains).any() else None,
        "serie_perdante_max": int(pire), "drawdown_max_pct": round(100 * dd, 1),
        "trades_par_mois": round(len(R) / 12, 1),
        "taux_remplissage": round(len(notes) / max(len(c["ordres_armes"]), 1), 3),
        "motifs": {m: int(sum(1 for t in notes if t["motif"] == m)) for m in sorted({t["motif"] for t in notes})},
        "levier_median": round(float(np.median(lev)), 1), "levier_max": round(float(lev.max()), 1),
        "risque_pct_reel_median": round(float(np.median([t["risque_pct_reel"] for t in notes])), 2),
        "mois_positifs_pct": round(100 * float((mois > 0).mean()), 0),
        "pire_mois_pct": round(float(pct_mois.min()), 1), "meilleur_mois_pct": round(float(pct_mois.max()), 1),
        "par_mois": {str(k)[:7]: round(float(v), 1) for k, v in pct_mois.items()},
        "cout_moyen_R": round(float(np.mean([(t["cout_entree_pts"] + t["cout_sortie_pts"])
                                             / t["risque_points"] for t in notes])), 3),
    })
    return base


def lancer(marche: str, capitaux=(10.0,), plafonds=(30.0, None)) -> list[dict]:
    t0 = time.time()
    serie = banc.charger(marche, "M1")
    fin_donnees = pd.Timestamp(serie.temps[-1])
    debut = (fin_donnees - pd.DateOffset(years=1)).normalize()
    print(f"  {marche} : rejeu du {debut:%Y-%m-%d} au {fin_donnees:%Y-%m-%d %H:%M} (Deriv)", flush=True)
    cache = SORTIE / f"filtres_{marche}_{debut:%Y%m%d}.joblib"
    import joblib
    if cache.exists():
        filtres = joblib.load(cache)
    else:
        filtres = filtres_trimestriels(marche, debut)
        SORTIE.mkdir(parents=True, exist_ok=True)
        joblib.dump(filtres, cache)
    print(f"    4 filtres trimestriels appris ({time.time() - t0:.0f} s) : seuils "
          + ", ".join(f"{f['seuil']:.3f}" for f in filtres), flush=True)
    j0 = int(np.searchsorted(serie.temps, np.datetime64(debut.to_datetime64(), "s")))
    X, noms = construire_aux_barres(serie, np.arange(j0, len(serie)))
    assert noms == filtres[0]["noms"], "les caractéristiques du rejeu ne sont pas celles de l'apprentissage"
    proba = np.full(len(serie), np.nan)
    seuils = np.full(len(serie), np.inf)
    t = pd.DatetimeIndex(serie.temps)
    ok = np.isfinite(X).all(axis=1)
    for f in filtres:
        m = (t[j0:] >= f["debut"]) & (t[j0:] < f["fin"]) & ok
        if m.any():
            proba[j0:][m] = f["modele"].predict_proba(X[m])[:, 1]
        seuils[j0:][(t[j0:] >= f["debut"]) & (t[j0:] < f["fin"])] = f["seuil"]

    # La recherche, sur les MÊMES prix Deriv et la même année : le trade au plus ancien ordre servi.
    ordres = candidates_v2.rabais(serie, **REGLAGES)
    tr = banc.simuler(serie, ordres)
    dans = tr.entree - 1 >= j0
    ps = proba[np.maximum(tr.entree - 1, 0)]
    garde = dans & (ps >= seuils[np.maximum(tr.entree - 1, 0)])
    recherche = {"trades": int(garde.sum()),
                 "taux_objectif": round(float((tr.motif[garde] == OBJECTIF).mean()), 4) if garde.any() else None,
                 "esperance_R": round(float(tr.R[garde].mean()), 4) if garde.any() else None,
                 "sans_filtre_trades": int(dans.sum()),
                 "sans_filtre_taux": round(float((tr.motif[dans] == OBJECTIF).mean()), 4),
                 "sans_filtre_R": round(float(tr.R[dans].mean()), 4)}
    del ordres, tr

    SORTIE.mkdir(parents=True, exist_ok=True)
    resultats = []
    for capital in capitaux:
        for plafond in plafonds:
            res = rejouer(marche, capital, filtres, levier_max=plafond, serie=serie, X=X, noms=noms,
                          proba=proba, seuils=seuils, j0=j0)
            r = resumer(marche, capital, plafond, res, debut, fin_donnees)
            r["recherche_meme_annee"] = recherche
            r["filtres"] = [{"debut": str(f["debut"])[:10], "seuil": round(f["seuil"], 4),
                             "appris": f["appris"], "recherche_duka": f["recherche"]} for f in filtres]
            cle = f"{marche}_{int(capital)}usd_{'x' + str(int(plafond)) if plafond else 'sans-plafond'}"
            (SORTIE / f"{cle}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
            with open(SORTIE / f"{cle}.jsonl", "w", encoding="utf-8") as fh:
                for note in res["notes"]:
                    fh.write(json.dumps(note, ensure_ascii=False) + "\n")
            resultats.append(r)
            print(f"    {capital:g} $ · levier {r['plafond_levier']} : {r['trades']} trades"
                  + (f", {100 * r['taux_objectif']:.1f} % de 2 R, {r['esperance_R']:+.3f} R, "
                     f"{capital:g} $ → {r['capital_final']:.2f} $, recul max {r['drawdown_max_pct']} %"
                     if r["trades"] else f" (refus de taille : {r['refus_taille']}, capital requis "
                                         f"médian {r['capital_requis_median']} $)"), flush=True)
    print(f"    recherche, même année, mêmes prix : {recherche['trades']} trades, "
          f"{100 * (recherche['taux_objectif'] or 0):.1f} % de 2 R, {recherche['esperance_R']} R "
          f"({time.time() - t0:.0f} s)", flush=True)
    return resultats


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--marche", default="EURUSD")
    ap.add_argument("--capital", type=float, nargs="*", default=[10.0])
    ap.add_argument("--tout", action="store_true")
    a = ap.parse_args()
    marches = ["NAS100", "EURUSD"] if a.tout else [a.marche.upper()]
    tout = []
    for m in marches:
        tout += lancer(m, tuple(a.capital))
    (SORTIE / "synthese.json").write_text(json.dumps(tout, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

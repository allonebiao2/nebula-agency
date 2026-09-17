# -*- coding: utf-8 -*-
"""
Backtest de la vidéo « Sniper Entry » sur EUR/USD et NAS100 en M1, puis un compte de 10 000 $.

    python -m trading.recherche.sniper_lancer fidelite
    python -m trading.recherche.sniper_lancer auteur
    python -m trading.recherche.sniper_lancer heures
    python -m trading.recherche.sniper_lancer variantes
    python -m trading.recherche.sniper_lancer compte
    python -m trading.recherche.sniper_lancer tout

Ordre voulu, et pourquoi :
  1. fidelite  : le détecteur retrouve-t-il les exemples de la vidéo ? (avant tout chiffre)
  2. auteur    : les règles de la vidéo, SANS optimisation, sur tout l'historique, année par année,
                 coûts ×1 / ×1,5 / ×2, avec et sans le filtre des annonces.
  3. heures    : les meilleures heures choisies sur les 80 % ANCIENS seulement, puis la période de
                 contrôle (20 % récents) ouverte UNE fois. Les 24 heures essayées comptent au registre.
  4. variantes : petite grille en walk-forward, hors échantillon, chaque combinaison au registre.
  5. compte    : 10 000 $, tailles réelles, règles de la vidéo contre règles NEBULA PRO.
Chaque résultat est écrit en JSON dans `trading/rapports/recherche/sniper/` ; le rapport les relit.
"""
from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
import pandas as pd

from . import banc, compte, sniper
from .banc import Candidate
from .lancer import DOSSIER, REGISTRE, _registre

SORTIE = DOSSIER / "sniper"
INSTRUMENTS = ("EURUSD", "NAS100")
AUTEUR = sniper.Reglages()
NEBULA = replace(AUTEUR, annonces=1)          # la vidéo + le verrou des annonces de l'agent

VERSIONS_AUTEUR = {
    "auteur": AUTEUR,
    "auteur_annonces": NEBULA,
    "auteur_annonces_sortie": replace(AUTEUR, annonces=2),
    "auteur_imbalance": replace(NEBULA, fvg=True),
    "auteur_5R": replace(NEBULA, rr=5.0),
    "auteur_2R": replace(NEBULA, rr=2.0),
    "auteur_niveau_oppose": replace(NEBULA, rr=-3.0),
    "auteur_dernier_creux_m1": replace(NEBULA, dernier_creux_m1=True),
    "auteur_stop_saute": replace(NEBULA, stop_trop_court="sauter"),
}


def ecrire(nom: str, donnees) -> Path:
    SORTIE.mkdir(parents=True, exist_ok=True)
    p = SORTIE / f"{nom}.json"
    p.write_text(json.dumps(donnees, ensure_ascii=False, default=str), encoding="utf-8")
    return p


def lire(nom: str):
    p = SORTIE / f"{nom}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def inscrire(cle: str, candidate: str, base: str, h: dict, combinaisons: int) -> None:
    registre = [r for r in _registre() if r["cle"] != cle]
    if h.get("trades"):
        registre.append({"cle": cle, "tour": "sniper", "candidate": candidate, "base": base, "tf": "M1",
                         "temoin": False, "combinaisons": combinaisons,
                         **{x: h.get(x) for x in ("trades", "taux_reussite", "esperance_R", "profit_factor",
                                                  "p_valeur", "drawdown_max_pct", "R_par_mois", "trades_par_mois",
                                                  "debut", "fin")}})
    REGISTRE.write_text(json.dumps(registre, ensure_ascii=False, indent=1), encoding="utf-8")


def mesures(serie: banc.Serie, tr: sniper.TradesSniper) -> dict:
    """`banc.mesurer` + ce que Mongazi regarde en premier (mémoire : critères de rentabilité)."""
    m = banc.mesurer(serie, tr)
    if not len(tr):
        return m
    R = tr.R
    gagnants = R > 0
    m["objectif_atteint"] = float((tr.motif == sniper.OBJECTIF).mean())
    m["rr_realise"] = float(R[gagnants].mean() / -R[~gagnants].mean()) if gagnants.any() and (~gagnants).any() else None
    m["stops_elargis"] = float(tr.stop_elargi.mean())
    m["risque_median_points"] = float(np.median(tr.risque_prix) / serie.point)
    # EUR/USD : en pips (10 points) ; NAS100 : en points d'indice (100 points MT5 = 1,00)
    m["risque_median_unite"] = float(np.median(tr.risque_prix) / (serie.point * (10 if serie.base == "EURUSD" else 100)))
    m["unite_risque"] = "pips" if serie.base == "EURUSD" else "points d'indice"
    m["cout_moyen_R"] = None
    m["series_perdantes"] = compte.series_perdantes(R)
    temps = pd.DatetimeIndex(serie.temps[tr.entree])
    ny = temps.tz_localize("UTC").tz_convert("America/New_York")
    m["par_heure_ny"] = {int(h): {"trades": int((ny.hour == h).sum()), "esperance_R": float(R[ny.hour == h].mean()),
                                  "taux_reussite": float(gagnants[ny.hour == h].mean())}
                         for h in np.unique(ny.hour)}
    annees = temps.year
    m["par_annee"] = {str(a): {"trades": int((annees == a).sum()), "taux_reussite": float(gagnants[annees == a].mean()),
                               "esperance_R": float(R[annees == a].mean()), "somme_R": float(R[annees == a].sum())}
                      for a in np.unique(annees)}
    return m


def charger(base: str, couts: float = 1.0) -> tuple[banc.Serie, sniper.Preparation]:
    s = banc.charger(base, "M1")
    return s, sniper.preparer(s)


# --------------------------------------------------------------------------- #
def fidelite() -> dict:
    """Les exemples de la vidéo, lus sur ses images (heure de New York convertie en UTC)."""
    exemples = [
        {"nom": "exemple 1 (Asie)", "balayage_utc": "2025-10-31 01:15", "video": "vente, plus haut 1,15775, clôture 1,15766, stop 1,6 pip, R:R affiché 34,9"},
        {"nom": "exemple 2 (Londres)", "balayage_utc": "2025-10-31 06:15", "video": "vente, plus haut 1,15734, « même celui-ci fait 3 pour 1 »"},
        {"nom": "exemple 3 (New York + 1 h 45)", "balayage_utc": "2025-10-31 15:45", "video": "vente, plus haut 1,15434, entrée à la clôture M1 de 12:04 New York, « 3 pour 1 puis 5 pour 1 »"},
        {"nom": "exemple 4 (Londres, imbalance)", "balayage_utc": "2025-11-04 07:30", "video": "vente, plus haut 1,15336, clôture 1,15311, « 3 pour 1 puis 6 pour 1 »"},
    ]
    s, prep = charger("EURUSD")
    sens, rc, rx, niv, fvg = sniper.balayages(prep, AUTEUR)
    tr = sniper.simuler(prep, AUTEUR)
    d15 = pd.DatetimeIndex(prep.m15.debut)
    t1 = pd.DatetimeIndex(s.temps)
    m = prep.m15
    for e in exemples:
        j = d15.get_loc(pd.Timestamp(e["balayage_utc"]))
        e["bougie_deriv"] = {"ouverture": m.ouverture[j], "haut": m.haut[j], "bas": m.bas[j], "cloture": m.cloture[j]}
        e["detecte"] = bool(sens[j] != 0)
        e["niveau_balaye"] = float(niv[j]) if sens[j] else None
        k = np.where(tr.balayage_m15 == j)[0]
        if len(k):
            q = k[0]
            e["trade"] = {"entree_utc": str(t1[tr.entree[q]]), "sortie_utc": str(t1[tr.sortie[q]]),
                          "prix_entree": float(tr.prix_entree[q]), "stop": float(tr.stop[q]), "cible": float(tr.cible[q]),
                          "R": float(tr.R[q]), "motif": banc.MOTIFS[tr.motif[q]], "stop_elargi": bool(tr.stop_elargi[q]),
                          "risque_pips": float(tr.risque_prix[q] / 1e-4)}
        print(f"  {e['nom']:32s} détecté={e['detecte']}  " + (f"entrée {e['trade']['entree_utc']} R {e['trade']['R']:+.2f} ({e['trade']['motif']})" if "trade" in e else ""))
    # la semaine des exemples, tout ce que le détecteur a vu
    semaine = (d15 >= "2025-10-27") & (d15 < "2025-11-08") & (sens != 0)
    autres = [{"balayage_utc": str(d15[j]), "sens": int(sens[j]), "niveau": float(niv[j]), "fvg": bool(fvg[j])}
              for j in np.where(semaine)[0]]
    dans_semaine = (t1[tr.entree] >= "2025-10-27") & (t1[tr.entree] < "2025-11-08")
    trades_semaine = [{"entree_utc": str(t1[tr.entree[q]]), "sens": int(tr.sens[q]), "R": float(tr.R[q]),
                       "motif": banc.MOTIFS[tr.motif[q]]} for q in np.where(dans_semaine)[0]]
    donnees = {"exemples": exemples, "setups_semaine": autres, "trades_semaine": trades_semaine, "reglages": asdict(AUTEUR)}
    ecrire("fidelite", donnees)
    return donnees


# --------------------------------------------------------------------------- #
def auteur() -> None:
    for base in INSTRUMENTS:
        s, prep = charger(base)
        resultats = {"base": base, "periode": [str(s.temps[0])[:10], str(s.temps[-1])[:10]],
                     "couverture_annonces": prep.couverture_annonces, "versions": {}}
        for nom, r in VERSIONS_AUTEUR.items():
            t0 = time.time()
            tr = sniper.simuler(prep, r)
            m = mesures(s, tr)
            v = {"reglages": asdict(r), "mesures": m, "trades_R": [round(float(x), 4) for x in tr.R]}
            if nom in ("auteur", "auteur_annonces"):
                # DIAGNOSTICS, hors registre : l'avantage BRUT (sans spread ni glissement) et des coûts de
                # courtier « raw » (moitié de Deriv). Ils disent si la méthode a quelque chose à vendre
                # avant que le courtier se serve, pas ce qu'elle rapporte.
                for mult, cle_d in ((0.0, "sans_couts"), (0.5, "couts_x0.5")):
                    trd = sniper.simuler(prep, replace(r, couts=mult))
                    md = banc.mesurer(s, trd)
                    v[cle_d] = {k: md.get(k) for k in ("trades", "taux_reussite", "esperance_R", "profit_factor", "p_valeur")}
                    v[cle_d]["objectif_atteint"] = float((trd.motif == sniper.OBJECTIF).mean()) if len(trd) else None
                m["cout_moyen_R"] = float(v["sans_couts"]["esperance_R"] - m["esperance_R"]) if v["sans_couts"].get("trades") else None
                if nom == "auteur":
                    # Les trades SANS filtre, séparés selon qu'ils sont entrés dans la fenêtre d'une annonce forte
                    bloque, _ = prep.masques_annonces(r.avant_min, r.apres_min, r.sortie_avant_min)
                    pres = bloque[tr.entree]
                    v["pres_annonce"] = {cle_p: {"trades": int(masque.sum()),
                                                 "taux_reussite": float((tr.R[masque] > 0).mean()) if masque.any() else None,
                                                 "esperance_R": float(tr.R[masque].mean()) if masque.any() else None}
                                         for cle_p, masque in (("dans_la_fenetre", pres), ("hors_fenetre", ~pres))}
                for mult in (1.5, 2.0):
                    trc = sniper.simuler(prep, replace(r, couts=mult))
                    v[f"couts_x{mult}"] = {k: banc.mesurer(s, trc).get(k) for k in ("trades", "taux_reussite", "esperance_R", "profit_factor", "p_valeur")}
            resultats["versions"][nom] = v
            inscrire(f"sniper_{nom}_{base}", f"sniper_{nom}", base, m, 1)
            print(f"  {base} {nom:26s} {m.get('trades', 0):5d} tr  {100 * m.get('taux_reussite', 0):5.1f} %  "
                  f"objectif {100 * m.get('objectif_atteint', 0):5.1f} %  {m.get('esperance_R', 0):+.3f} R  "
                  f"PF {m.get('profit_factor', 0):.2f}  p {m.get('p_valeur', 1):.3f}  ({time.time() - t0:.0f} s)", flush=True)
        ecrire(f"auteur_{base}", resultats)
        del s, prep
        sniper.Sniper._cache.clear()
        gc.collect()


# --------------------------------------------------------------------------- #
def heures() -> None:
    """Les heures choisies sur le développement, jugées sur le contrôle."""
    for base in INSTRUMENTS:
        s, prep = charger(base)
        fin_dev, _ = banc.bornes(s)
        toutes = replace(NEBULA, seances="toutes")
        dev = sniper.simuler(prep, toutes, 0, fin_dev - 1)
        dev = dev.selection(dev.sortie < fin_dev)
        ny = pd.DatetimeIndex(s.temps[dev.entree]).tz_localize("UTC").tz_convert("America/New_York").hour
        table = {}
        for h in range(24):
            R = dev.R[ny == h]
            table[h] = {"trades": int(len(R)), "esperance_R": float(R.mean()) if len(R) else None,
                        "taux_reussite": float((R > 0).mean()) if len(R) else None,
                        "p_valeur": banc.p_valeur_unilaterale(R) if len(R) > 1 else None}
        choisies = tuple(h for h, v in table.items() if v["trades"] >= 30 and v["esperance_R"] > 0)
        sortie = {"base": base, "fin_developpement": str(s.temps[fin_dev])[:16], "par_heure_dev": table,
                  "heures_choisies_ny": list(choisies)}
        if choisies:
            # ⚠️ l'heure du tableau est celle de l'ENTRÉE ; le filtre porte sur la clôture du balayage.
            # On filtre donc sur l'entrée, à la simulation, pour juger exactement ce qui a été choisi.
            regle = replace(NEBULA, seances="toutes")
            tr_ctrl = sniper.simuler(prep, regle, fin_dev, len(s) - 1)
            ny_c = pd.DatetimeIndex(s.temps[tr_ctrl.entree]).tz_localize("UTC").tz_convert("America/New_York").hour
            garde = np.isin(ny_c, choisies)
            ctrl = tr_ctrl.selection(garde)
            sortie["controle_heures_choisies"] = banc.mesurer(s, ctrl)
            sortie["controle_heures_choisies"]["objectif_atteint"] = float((ctrl.motif == sniper.OBJECTIF).mean()) if len(ctrl) else None
            inscrire(f"sniper_heures_controle_{base}", "sniper_meilleures_heures", base, sortie["controle_heures_choisies"], 24)
        auteur_ctrl = sniper.simuler(prep, NEBULA, fin_dev, len(s) - 1)
        sortie["controle_seances_auteur"] = banc.mesurer(s, auteur_ctrl)
        ecrire(f"heures_{base}", sortie)
        c = sortie.get("controle_heures_choisies", {})
        print(f"  {base} heures NY choisies sur le développement : {choisies} -> contrôle "
              f"{c.get('trades', 0)} tr {c.get('esperance_R', 0):+.3f} R  | séances de l'auteur au contrôle "
              f"{sortie['controle_seances_auteur'].get('trades', 0)} tr {sortie['controle_seances_auteur'].get('esperance_R', 0):+.3f} R", flush=True)
        del s, prep
        gc.collect()


# --------------------------------------------------------------------------- #
GRILLE = {"ema": [50, 200], "fvg": [False, True], "rr": [2.0, 3.0, 5.0, -3.0], "validite": [1, 4],
          "seances": ["auteur", "toutes"], "annonces": [1]}


def variantes() -> None:
    cand = Candidate("sniper_variantes", "Sniper Entry : grille en walk-forward", "YouTube Mulham Trading",
                     sniper.fabrique, GRILLE, ("M1",))
    for base in INSTRUMENTS:
        t0 = time.time()
        s = banc.charger(base, "M1")
        res = banc.walk_forward(s, cand)
        ctrl = banc.controle(s, cand)
        h = res.hors_echantillon
        sortie = {"base": base, "combinaisons": len(cand.combinaisons()), "hors_echantillon": h,
                  "fenetres": res.fenetres, "trades_R": res.trades_R, "controle": ctrl}
        ecrire(f"variantes_{base}", sortie)
        inscrire(f"sniper_variantes_{base}_adaptee", "sniper_variantes", base, h, len(cand.combinaisons()))
        print(f"  {base} walk-forward {h.get('trades', 0)} tr {100 * h.get('taux_reussite', 0):.1f} % "
              f"{h.get('esperance_R', 0):+.3f} R p {h.get('p_valeur', 1):.3f} | contrôle {ctrl.get('trades', 0)} tr "
              f"{ctrl.get('esperance_R', 0):+.3f} R réglages {ctrl.get('reglages')}  ({time.time() - t0:.0f} s)", flush=True)
        del s
        sniper.Sniper._cache.clear()
        gc.collect()


# --------------------------------------------------------------------------- #
def lancer_compte(risques=(0.5, 1.0, 2.0, 3.0)) -> None:
    from ..noyau.donnees_mt5 import specs_et_couts
    configs = {"auteur": AUTEUR, "auteur_annonces": NEBULA}
    trades = {nom: {} for nom in configs}
    specs = {}
    for base in INSTRUMENTS:
        s, prep = charger(base)
        specs[base] = specs_et_couts(base)[0]
        for nom, r in configs.items():
            trades[nom][base] = compte.depuis_sniper(base, s, sniper.simuler(prep, r))
        del s, prep
        gc.collect()
    sortie = {}
    for nom in configs:
        debut_nas = min(t.entree for t in trades[nom]["NAS100"]) if trades[nom]["NAS100"] else None
        paniers = {
            "EURUSD": trades[nom]["EURUSD"],
            "NAS100": trades[nom]["NAS100"],
            "EURUSD_et_NAS100": [t for b in INSTRUMENTS for t in trades[nom][b] if debut_nas and t.entree >= debut_nas],
        }
        for panier, liste in paniers.items():
            for regles in ("video", "pro"):
                for risque in risques:
                    if regles == "pro" and risque > 2.0:
                        continue                                  # plafond du code en PRO
                    copie = [compte.TradeCompte(**{k: getattr(t, k) for k in ("base", "entree", "sortie", "sens", "R", "points_risque", "prix")})
                             for t in liste]
                    res = compte.simuler_compte(copie, specs, risque_pct=risque, regles=regles)
                    cle = f"{nom}|{panier}|{regles}|{risque}"
                    sortie[cle] = res.resume()
                    r_ = sortie[cle]
                    print(f"  {cle:45s} {r_.get('trades', 0):5d} tr  10 000 $ -> {r_.get('capital_final', 0):>12,.0f} $  "
                          f"({r_.get('rendement_pct', 0):+.1f} %)  DD {r_.get('drawdown_max_pct', 0):.1f} %  refusés {r_.get('refuses', 0)}", flush=True)
    ecrire("compte", sortie)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument("etape", choices=["fidelite", "auteur", "heures", "variantes", "compte", "tout"])
    a = p.parse_args()
    etapes = ["fidelite", "auteur", "heures", "variantes", "compte"] if a.etape == "tout" else [a.etape]
    for e in etapes:
        print(f"== {e}", flush=True)
        t0 = time.time()
        {"fidelite": fidelite, "auteur": auteur, "heures": heures, "variantes": variantes, "compte": lancer_compte}[e]()
        print(f"   ({time.time() - t0:.0f} s)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

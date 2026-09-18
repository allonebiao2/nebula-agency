# -*- coding: utf-8 -*-
"""
Momentum intraday par « zone de bruit » (Zarattini, Aziz & Barbon, SSRN 4824172), sur le NAS100.

    python -m trading.recherche.zone_bruit

Règles de l'article (résumées par CXO Advisory), **sans rien optimiser** :
  · chaque jour, pour chaque minute depuis l'ouverture de 9 h 30, sigma = la moyenne, sur les 14
    jours précédents, de |prix à cette minute / ouverture - 1| ;
  · borne haute = max(ouverture, clôture de la veille) x (1 + sigma), borne basse =
    min(ouverture, clôture de la veille) x (1 - sigma) : le gap de la nuit élargit la zone ;
  · on regarde aux heures et demi-heures (10 h 00 → 15 h 30) : au-dessus de la borne haute → achat,
    sous la borne basse → vente, à l'ouverture de la minute suivante ;
  · stop suiveur : le plus haut de (borne haute, VWAP du jour) pour un achat, le plus bas de
    (borne basse, VWAP) pour une vente ; tout est fermé à la clôture.
Publié sur SPY, 2007 → début 2024 : 19,6 %/an, Sharpe 1,33, ~43 % de trades gagnants.

Deux versions, parce que notre doctrine l'exige :
  · « article » : le stop n'est vérifié qu'aux demi-heures, comme dans le papier ;
  · « stop courtier » : le stop est POSÉ chez le courtier en permanence, relevé aux demi-heures,
    jamais élargi (règle maison). Une barre qui le touche sort au stop.
Un R = la distance entre l'entrée et le stop initial. Entrée au marché, un seul trade à la fois :
aucun chevauchement d'ordres limites, le piège du 2026-09-18 ne peut pas se produire.
**Juge** : ce que les auteurs n'ont jamais vu, **mars 2024 → aujourd'hui**, et le NAS100 lui-même
(l'article est sur le S&P 500).
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from . import banc
from .intraday import jour_ny, minutes_et_jours
from .lancer import DOSSIER

SORTIE = DOSSIER / "zone_bruit"
OUV = 9 * 60 + 30
N_MIN = 390                       # 9 h 30 → 15 h 59
CONTROLES = list(range(30, 390, 30))   # 10 h 00, 10 h 30, … 15 h 30 (minutes depuis l'ouverture)
RECUL = 14


def matrices(serie):
    """Une ligne par jour de New York complet : ouverture, haut, bas, clôture, volume par minute."""
    minute, jsem = minutes_et_jours(serie.temps)
    jour = jour_ny(serie.temps)
    k = minute - OUV
    garde = (k >= 0) & (k < N_MIN) & (jsem < 5)
    jours, inv = np.unique(jour[garde], return_inverse=True)
    nj = len(jours)
    O = np.full((nj, N_MIN), np.nan); H = O.copy(); L = O.copy(); C = O.copy(); V = np.zeros((nj, N_MIN))
    Kc = np.full((nj, N_MIN), np.nan)
    idx = np.flatnonzero(garde)
    O[inv, k[garde]] = serie.ouverture[idx]
    H[inv, k[garde]] = serie.haut[idx]
    L[inv, k[garde]] = serie.bas[idx]
    C[inv, k[garde]] = serie.cloture[idx]
    vol = serie.volume if serie.volume is not None else np.ones(len(serie))
    V[inv, k[garde]] = vol[idx]
    Kc[inv, k[garde]] = serie.couts_prix()[idx]
    complet = (np.isnan(C).sum(axis=1) <= 10) & np.isfinite(O[:, 0]) & np.isfinite(C[:, -1])
    # Les rares minutes manquantes : le dernier prix connu (aucune barre future)
    for M in (C, O, H, L, Kc):
        for j in range(1, N_MIN):
            m = np.isnan(M[:, j])
            M[m, j] = C[m, j - 1] if M is not Kc else Kc[m, j - 1]
    return jours[complet], O[complet], H[complet], L[complet], C[complet], V[complet], Kc[complet]


def simuler(jours, O, H, L, C, V, K, *, stop_courtier: bool, debut=None, fin=None) -> list[dict]:
    nj = len(jours)
    ouverture = O[:, 0]
    veille = np.concatenate(([np.nan], C[:-1, -1]))
    mouvement = np.abs(C / ouverture[:, None] - 1)            # |prix à la minute / ouverture - 1|
    # Taille de l'article : viser 2 % de volatilité par jour, levier plafonné à 4.
    r_jour = np.concatenate(([np.nan], C[1:, -1] / C[:-1, -1] - 1))
    typ = (H + L + C) / 3
    vwap = np.cumsum(typ * V, axis=1) / np.maximum(np.cumsum(V, axis=1), 1e-12)
    trades = []
    for d in range(RECUL, nj):
        js = str(jours[d])
        if (debut and js < debut) or (fin and js >= fin) or not np.isfinite(veille[d]):
            continue
        sigma = mouvement[d - RECUL:d].mean(axis=0)
        vol14 = np.nanstd(r_jour[d - RECUL:d])
        levier = float(min(4.0, 0.02 / vol14)) if vol14 > 0 else 1.0
        haut_z = max(ouverture[d], veille[d]) * (1 + sigma)
        bas_z = min(ouverture[d], veille[d]) * (1 - sigma)
        pos = None
        for ci, kc in enumerate(CONTROLES):
            j = kc - 1                                       # la dernière minute close
            px = C[d, j]
            # 1. la position ouverte : le stop suiveur, vérifié à la demi-heure
            if pos is not None:
                s = pos["s"]
                niveau = max(haut_z[j], vwap[d, j]) if s > 0 else min(bas_z[j], vwap[d, j])
                if stop_courtier:
                    pos["stop"] = max(pos["stop"], niveau) if s > 0 else min(pos["stop"], niveau)
                elif (s > 0 and px < niveau) or (s < 0 and px > niveau):
                    fermer(pos, O[d, kc], K[d, kc], kc, "stop suiveur (demi-heure)", trades, js)
                    pos = None
            # 2. à plat : une sortie de zone ?
            if pos is None:
                s = 1 if px > haut_z[j] else (-1 if px < bas_z[j] else 0)
                if s:
                    entree = O[d, kc]
                    stop = max(haut_z[j], vwap[d, j]) if s > 0 else min(bas_z[j], vwap[d, j])
                    if s * (entree - stop) <= 0:
                        stop = haut_z[j] if s > 0 else bas_z[j]
                    if s * (entree - stop) > 0:
                        pos = {"s": s, "entree": entree, "stop": stop, "d": s * (entree - stop),
                               "k": kc, "cout": K[d, kc], "mfe": 0.0, "mae": 0.0, "levier": levier}
            # 3. entre deux demi-heures : le stop chez le courtier
            if pos is not None:
                fin_k = CONTROLES[ci + 1] if ci + 1 < len(CONTROLES) else N_MIN
                for m in range(max(pos["k"], kc), fin_k):
                    s = pos["s"]
                    pos["mfe"] = max(pos["mfe"], s * ((H[d, m] if s > 0 else L[d, m]) - pos["entree"]) / pos["d"])
                    pos["mae"] = min(pos["mae"], s * ((L[d, m] if s > 0 else H[d, m]) - pos["entree"]) / pos["d"])
                    if stop_courtier and ((s > 0 and L[d, m] <= pos["stop"]) or (s < 0 and H[d, m] >= pos["stop"])):
                        prix = O[d, m] if m > pos["k"] and ((s > 0 and O[d, m] < pos["stop"]) or
                                                            (s < 0 and O[d, m] > pos["stop"])) else pos["stop"]
                        fermer(pos, prix, K[d, m], m, "stop courtier", trades, js)
                        pos = None
                        break
        if pos is not None:
            fermer(pos, C[d, -1], K[d, -1], N_MIN - 1, "clôture", trades, js)
    return trades


def fermer(pos, prix, cout, k, motif, trades, jour):
    s = pos["s"]
    net = s * ((prix - s * cout) - (pos["entree"] + s * pos["cout"]))
    ret = net / pos["entree"]                  # rendement du trade, en fraction du prix, coûts compris
    trades.append({"jour": jour, "sens": s, "entree": float(pos["entree"]), "sortie": float(prix),
                   "ret_pct": round(100 * float(ret), 5), "levier": round(pos["levier"], 3),
                   "ret_compte_pct": round(100 * float(ret) * pos["levier"], 5),
                   "risque_points": round(float(pos["d"] / 0.01), 1),
                   "R": round(float(net / pos["d"]), 4),
                   "R_sans_cout": round(float(s * (prix - pos["entree"]) / pos["d"]), 4),
                   "cout_R": round(float((cout + pos["cout"]) / pos["d"]), 4), "motif": motif,
                   "duree_min": int(k - pos["k"]), "mfe_R": round(pos["mfe"], 3),
                   "mae_R": round(pos["mae"], 3), "annee": int(jour[:4])})


def perf(trades: list[dict]) -> dict:
    """La mesure de l'ARTICLE : rendement du compte jour par jour (taille par volatilité)."""
    import pandas as pd
    if not trades:
        return {"trades": 0}
    df = pd.DataFrame(trades)
    jour = df.groupby("jour")["ret_compte_pct"].sum() / 100
    idx = pd.to_datetime(jour.index)
    tous = pd.Series(0.0, index=pd.bdate_range(idx.min(), idx.max()))
    tous.loc[idx] = jour.values
    eq = (1 + tous).cumprod()
    annees = max(len(tous) / 252, 1e-9)
    dd = float((1 - eq / eq.cummax()).max())
    gagnant = df["ret_pct"] > 0
    par_an = {int(a): round(100 * float((1 + g).prod() - 1), 1) for a, g in tous.groupby(tous.index.year)}
    return {"trades": len(df), "gagnants": round(float(gagnant.mean()), 4),
            "gain_moyen_pct": round(float(df.loc[gagnant, "ret_pct"].mean()), 4),
            "perte_moyenne_pct": round(float(df.loc[~gagnant, "ret_pct"].mean()), 4),
            "ratio_gain_perte": round(float(df.loc[gagnant, "ret_pct"].mean() / -df.loc[~gagnant, "ret_pct"].mean()), 2),
            "rendement_annuel_pct": round(100 * float(eq.iloc[-1] ** (1 / annees) - 1), 1),
            "sharpe": round(float(tous.mean() / tous.std() * np.sqrt(252)), 2) if tous.std() > 0 else None,
            "pire_recul_pct": round(100 * dd, 1), "levier_moyen": round(float(df["levier"].mean()), 2),
            "par_an_pct": par_an}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.parse_args()
    SORTIE.mkdir(parents=True, exist_ok=True)
    duka = matrices(banc.charger("NAS100", "M1", source="duka"))
    deriv = matrices(banc.charger("NAS100", "M1"))
    tout = []
    for version, sc in (("article (stop aux demi-heures)", False), ("stop courtier permanent", True)):
        for nom, m, d, f in (("avant et pendant l'article (Dukascopy, 2013 → 2024-02)", duka, "2013-01-01", "2024-03-01"),
                             ("JUGE : jamais vu par les auteurs (Dukascopy, 2024-03 → 2026-09)", duka, "2024-03-01", None),
                             ("JUGE, prix Deriv (2024-03 → 2026-09)", deriv, "2024-03-01", None)):
            tr = simuler(*m, stop_courtier=sc, debut=d, fin=f)
            r = perf(tr)
            r["periode"] = f"{version} · {nom}"
            tout.append(r)
            if not r["trades"]:
                print(f"  {version} · {nom} : aucun trade")
                continue
            print(f"\n  {version} · {nom}\n    {r['trades']} trades · gagnants {100 * r['gagnants']:.1f} % · "
                  f"gain moyen {r['gain_moyen_pct']:+.3f} % du prix, perte moyenne {r['perte_moyenne_pct']:+.3f} % "
                  f"(ratio {r['ratio_gain_perte']}) · compte : {r['rendement_annuel_pct']:+.1f} %/an, Sharpe "
                  f"{r['sharpe']}, pire recul {r['pire_recul_pct']} %, levier moyen x{r['levier_moyen']}", flush=True)
            print("    par an : " + " · ".join(f"{k} {v:+.1f} %" for k, v in r["par_an_pct"].items()), flush=True)
            with open(SORTIE / f"{'article' if not sc else 'courtier'}_{d[:4]}_{'deriv' if m is deriv else 'duka'}.jsonl",
                      "w", encoding="utf-8") as fh:
                for x in tr:
                    fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    (SORTIE / "resume.json").write_text(json.dumps(tout, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""
Opening Range Breakout 5 minutes sur le NAS100, **règles de l'article, sans rien optimiser**.

    python -m trading.recherche.orb

Zarattini & Aziz, « Can Day Trading Really Be Profitable? » (SSRN 4416622), version QQQ :
  · à 9 h 35 New York, entrer dans le sens de la première bougie de 5 minutes (9 h 30 → 9 h 35) :
    achat si elle clôture au-dessus de son ouverture, vente en dessous, rien si elle est plate ;
  · stop à l'extrême OPPOSÉ de cette bougie (son plus bas pour un achat) ;
  · objectif 10 R, sinon sortie à la clôture de 16 h 00 ;
  · 1 % de risque par trade.
Publié sur 2016 → février 2023 : 24 % de trades gagnants, ~+0,13 R par trade, Sharpe 1,13.

**Pourquoi ce test est honnête** : (1) entrée AU MARCHÉ à une heure fixe, un trade par jour, donc
aucun chevauchement d'ordres limites : le piège du 2026-09-18 ne peut pas se produire ; (2) les
règles sont celles de l'article, aucun paramètre n'est choisi ici ; (3) **mars 2023 → aujourd'hui est
une période que les auteurs n'ont jamais vue** : c'est elle qui juge. 2016-2023 ne sert qu'à vérifier
qu'on retrouve leurs chiffres (sinon, notre code ou leur article a un défaut).

Simulation minute par minute, pessimiste : sur une barre qui touche le stop ET l'objectif, c'est le
stop. Coût Deriv minute par minute à l'entrée et à la sortie (spread de 70 points + glissement).
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
import pandas as pd

from . import banc
from .intraday import jour_ny, minutes_et_jours
from .lancer import DOSSIER

SORTIE = DOSSIER / "orb"
OUVERTURE, ENTREE, CLOTURE = 9 * 60 + 30, 9 * 60 + 35, 15 * 60 + 59
OBJECTIF_R = 10.0


def trades_orb(serie, objectif_R: float = OBJECTIF_R, debut: str | None = None,
               fin: str | None = None) -> list[dict]:
    minute, jsem = minutes_et_jours(serie.temps)
    jour = jour_ny(serie.temps)
    o, h, b, c = serie.ouverture, serie.haut, serie.bas, serie.cloture
    couts = serie.couts_prix()
    t = serie.temps
    trades = []
    debuts = np.flatnonzero(np.concatenate(([True], jour[1:] != jour[:-1])))
    fins = np.append(debuts[1:], len(jour))
    for a, z in zip(debuts, fins):
        if jsem[a] >= 5:
            continue
        m = minute[a:z]
        i_open = np.flatnonzero(m == OUVERTURE)
        i_entree = np.flatnonzero(m == ENTREE)
        if not len(i_open) or not len(i_entree):
            continue
        k0, ke = a + i_open[0], a + i_entree[0]
        if ke - k0 != 5:                       # une minute manque dans l'ouverture : on ne devine pas
            continue
        jour_str = str(t[k0])[:10]
        if (debut and jour_str < debut) or (fin and jour_str >= fin):
            continue
        ouv5, clo5 = o[k0], c[ke - 1]
        haut5, bas5 = h[k0:ke].max(), b[k0:ke].min()
        if clo5 == ouv5:
            continue
        s = 1 if clo5 > ouv5 else -1
        prix = o[ke]
        stop = bas5 if s > 0 else haut5
        d = s * (prix - stop)
        if d <= 0:                             # l'ouverture de 9 h 35 est déjà au-delà du stop
            continue
        cible = prix + s * objectif_R * d
        entree_nette = prix + s * couts[ke]
        sortie, motif, j = None, "", ke
        mfe = mae = 0.0
        derniere = a + int(np.searchsorted(m, CLOTURE, side="right")) - 1
        for j in range(ke, max(derniere, ke) + 1):
            mfe = max(mfe, s * ((h[j] if s > 0 else b[j]) - prix) / d)
            mae = min(mae, s * ((b[j] if s > 0 else h[j]) - prix) / d)
            if (s > 0 and b[j] <= stop) or (s < 0 and h[j] >= stop):
                sortie, motif = (o[j] if j > ke and ((s > 0 and o[j] < stop) or (s < 0 and o[j] > stop))
                                 else stop), "stop"
                break
            if (s > 0 and h[j] >= cible) or (s < 0 and b[j] <= cible):
                sortie, motif = cible, "objectif"
                break
            if minute[j] >= CLOTURE:
                sortie, motif = c[j], "clôture"
                break
        if sortie is None:
            sortie, motif = c[j], "clôture"
        R = s * ((sortie - s * couts[j]) - entree_nette) / d
        trades.append({"jour": jour_str, "sens": s, "entree": float(prix), "stop": float(stop),
                       "cible": float(cible), "risque_points": round(float(d / serie.point), 1),
                       "sortie": float(sortie), "motif": motif, "R": round(float(R), 4),
                       "R_sans_cout": round(float(s * (sortie - prix) / d), 4),
                       "cout_R": round(float((couts[ke] + couts[j]) / d), 4),
                       "mfe_R": round(float(mfe), 3), "mae_R": round(float(mae), 3),
                       "duree_min": int(j - ke), "annee": int(jour_str[:4])})
    return trades


def resume(trades: list[dict], nom: str) -> dict:
    if not trades:
        return {"periode": nom, "trades": 0}
    from .compte import series_perdantes
    R = np.array([x["R"] for x in trades])
    gagnant = R > 0
    serie_p = pire = 0
    for g in gagnant:
        serie_p = 0 if g else serie_p + 1
        pire = max(pire, serie_p)
    eq = np.cumsum(R)
    dd_R = float(np.max(np.maximum.accumulate(np.concatenate(([0.0], eq)))[1:] - eq))
    par_an = {}
    for a in sorted({x["annee"] for x in trades}):
        r = np.array([x["R"] for x in trades if x["annee"] == a])
        par_an[a] = {"trades": len(r), "gagnants": round(float((r > 0).mean()), 3), "somme_R": round(float(r.sum()), 1)}
    try:
        p56 = series_perdantes(R, longueurs=(5, 6), fenetre=100, tirages=5000)
    except Exception:                                                    # noqa: BLE001
        p56 = None
    lo, hi = banc._wilson(int(gagnant.sum()), len(R))
    return {"periode": nom, "trades": len(R), "gagnants": round(float(gagnant.mean()), 4),
            "ic95_gagnants": [round(lo, 3), round(hi, 3)],
            "objectif_10R": round(float(np.mean([x["motif"] == "objectif" for x in trades])), 4),
            "esperance_R": round(float(R.mean()), 4),
            "esperance_R_sans_cout": round(float(np.mean([x["R_sans_cout"] for x in trades])), 4),
            "cout_moyen_R": round(float(np.mean([x["cout_R"] for x in trades])), 4),
            "gain_moyen_R": round(float(R[gagnant].mean()), 3) if gagnant.any() else None,
            "perte_moyenne_R": round(float(R[~gagnant].mean()), 3) if (~gagnant).any() else None,
            "somme_R": round(float(R.sum()), 1), "pire_recul_R": round(dd_R, 1),
            "serie_perdante_max": int(pire), "series_perdantes_100": p56,
            "stop_median_points": (float(np.median([x["risque_points"] for x in trades]))
                                   if "risque_points" in trades[0] else float("nan")),
            "par_an": par_an}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--objectif", type=float, default=OBJECTIF_R)
    a = ap.parse_args()
    SORTIE.mkdir(parents=True, exist_ok=True)
    duka = banc.charger("NAS100", "M1", source="duka")
    deriv = banc.charger("NAS100", "M1")
    blocs = [("reproduction de l'article (Dukascopy, 2016 → 2023-02)", duka, "2016-01-01", "2023-03-01"),
             ("JUGE : jamais vu par les auteurs (Dukascopy, 2023-03 → 2026-09)", duka, "2023-03-01", None),
             ("JUGE, prix Deriv (2024-01 → 2026-09)", deriv, "2024-01-23", None),
             ("avant l'article (Dukascopy, 2013 → 2015)", duka, "2013-01-01", "2016-01-01")]
    tout = []
    for nom, serie, d, f in blocs:
        tr = trades_orb(serie, a.objectif, d, f)
        r = resume(tr, nom)
        tout.append(r)
        cle = nom.split(" (")[0].split(" :")[0].replace(" ", "_").replace("'", "")
        with open(SORTIE / f"{cle}.jsonl", "w", encoding="utf-8") as fh:
            for x in tr:
                fh.write(json.dumps(x, ensure_ascii=False) + "\n")
        if not r["trades"]:
            print(f"  {nom} : aucun trade")
            continue
        p = r["series_perdantes_100"] or {}
        print(f"\n  {nom}\n    {r['trades']} trades · gagnants {100 * r['gagnants']:.1f} % "
              f"({100 * r['ic95_gagnants'][0]:.0f}-{100 * r['ic95_gagnants'][1]:.0f} %) · objectif 10 R "
              f"{100 * r['objectif_10R']:.1f} % · espérance {r['esperance_R']:+.3f} R "
              f"(sans coût {r['esperance_R_sans_cout']:+.3f}, coût {r['cout_moyen_R']:.3f} R)\n"
              f"    gain moyen {r['gain_moyen_R']} R · perte moyenne {r['perte_moyenne_R']} R · total "
              f"{r['somme_R']:+.1f} R · pire recul {r['pire_recul_R']} R · pire série perdante "
              f"{r['serie_perdante_max']} · stop médian {r['stop_median_points']:.0f} points · "
              f"P(5 pertes/100) {p}", flush=True)
        print("    par an : " + " · ".join(f"{k} {v['somme_R']:+.1f} R ({v['trades']})"
                                          for k, v in r["par_an"].items()), flush=True)
    (SORTIE / "resume.json").write_text(json.dumps(tout, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

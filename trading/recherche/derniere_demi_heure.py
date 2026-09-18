# -*- coding: utf-8 -*-
"""
Momentum de la dernière demi-heure (Gao, Han, Li & Zhou, Journal of Financial Economics, 2018),
sur le NAS100.

    python -m trading.recherche.derniere_demi_heure

Règle de l'article : le rendement de la PREMIÈRE demi-heure, mesuré depuis la clôture de la veille
(16 h 00 → 10 h 00 New York), prédit celui de la DERNIÈRE (15 h 30 → 16 h 00), dans le même sens.
  · à 15 h 30 : achat si ce rendement est positif, vente s'il est négatif ;
  · sortie à la clôture (fin de la minute de 15 h 59).
Variante de l'article : ne trader que les jours où la 12e demi-heure (15 h 00 → 15 h 30) va dans le
même sens (« r1 et r12 d'accord »). Publié sur SPY 1993-2013 ; tout ce qui suit 2013 est neuf.

Pas d'objectif, pas de stop dans l'article. Notre doctrine exige un stop chez le courtier : il est
posé à 1 x l'amplitude moyenne d'une demi-heure (mesurée sur les 14 jours précédents), et on mesure
aussi la version sans stop pour savoir ce qu'il coûte. Entrée au marché, un trade par jour.
"""
from __future__ import annotations

import json
import sys

import numpy as np

from . import banc
from .lancer import DOSSIER
from .zone_bruit import N_MIN, matrices

SORTIE = DOSSIER / "derniere_demi_heure"
K_1030 = 29           # dernière minute close à 10 h 00 (la minute de 9 h 59)
K_1500, K_1530 = 330, 360


def simuler(jours, O, H, L, C, V, K, *, accord: bool, stop: bool, debut=None, fin=None) -> list[dict]:
    veille = np.concatenate(([np.nan], C[:-1, -1]))
    amplitude = (H[:, K_1530:].max(axis=1) - L[:, K_1530:].min(axis=1))   # amplitude de la dernière demi-heure
    trades = []
    for d in range(15, len(jours)):
        js = str(jours[d])
        if (debut and js < debut) or (fin and js >= fin) or not np.isfinite(veille[d]):
            continue
        r1 = C[d, K_1030] / veille[d] - 1
        r12 = C[d, K_1530 - 1] / C[d, K_1500 - 1] - 1
        if r1 == 0 or (accord and np.sign(r12) != np.sign(r1)):
            continue
        s = 1 if r1 > 0 else -1
        entree = O[d, K_1530]
        dist = float(np.mean(amplitude[d - 14:d]))            # passé seulement
        niveau = entree - s * dist
        sortie, motif, k = C[d, -1], "clôture", N_MIN - 1
        if stop:
            for m in range(K_1530, N_MIN):
                if (s > 0 and L[d, m] <= niveau) or (s < 0 and H[d, m] >= niveau):
                    sortie = O[d, m] if m > K_1530 and ((s > 0 and O[d, m] < niveau) or
                                                        (s < 0 and O[d, m] > niveau)) else niveau
                    motif, k = "stop", m
                    break
        net = s * ((sortie - s * K[d, k]) - (entree + s * K[d, K_1530]))
        trades.append({"jour": js, "sens": s, "annee": int(js[:4]), "ret_pct": round(100 * net / entree, 5),
                       "R": round(float(net / dist), 4), "motif": motif,
                       "cout_pct": round(100 * float(K[d, k] + K[d, K_1530]) / entree, 5)})
    return trades


def resumer(tr: list[dict]) -> dict:
    if not tr:
        return {"trades": 0}
    r = np.array([x["ret_pct"] for x in tr])
    g = r > 0
    t_stat = r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))
    lo, hi = banc._wilson(int(g.sum()), len(r))
    return {"trades": len(r), "gagnants": round(float(g.mean()), 4), "ic95": [round(lo, 3), round(hi, 3)],
            "gain_moyen_pct": round(float(r[g].mean()), 4), "perte_moyenne_pct": round(float(r[~g].mean()), 4),
            "ratio": round(float(r[g].mean() / -r[~g].mean()), 2), "moyenne_pct": round(float(r.mean()), 5),
            "t": round(float(t_stat), 2), "cout_moyen_pct": round(float(np.mean([x["cout_pct"] for x in tr])), 5),
            "par_an": {a: round(float(sum(x["ret_pct"] for x in tr if x["annee"] == a)), 2)
                       for a in sorted({x["annee"] for x in tr})}}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    SORTIE.mkdir(parents=True, exist_ok=True)
    duka = matrices(banc.charger("NAS100", "M1", source="duka"))
    deriv = matrices(banc.charger("NAS100", "M1"))
    tout = []
    for accord in (False, True):
        for stop in (False, True):
            for nom, m, d in (("Dukascopy 2013 → 2026", duka, "2013-01-01"), ("Deriv 2024 → 2026", deriv, "2024-01-23")):
                tr = simuler(*m, accord=accord, stop=stop, debut=d)
                r = resumer(tr)
                r["version"] = f"{'r1 et r12 d accord' if accord else 'r1 seul'} · {'stop courtier' if stop else 'sans stop'} · {nom}"
                tout.append(r)
                print(f"  {r['version']:<55} {r['trades']:>5} trades · gagnants {100 * r['gagnants']:.1f} % "
                      f"({100 * r['ic95'][0]:.0f}-{100 * r['ic95'][1]:.0f}) · gain/perte {r['ratio']} · "
                      f"moyenne {r['moyenne_pct']:+.4f} % (t = {r['t']}, coût {r['cout_moyen_pct']:.4f} %)", flush=True)
    (SORTIE / "resume.json").write_text(json.dumps(tout, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

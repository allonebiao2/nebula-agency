# -*- coding: utf-8 -*-
"""
Deux flux, la même période, la même stratégie : lequel raconte la vérité ?

    python -m trading.recherche.comparer_flux --base NAS100

Pourquoi ce fichier existe. Le 2026-09-17, une entrée limite sur repli (`candidates_v2.rabais`)
sortait **+0,17 R par trade sur 19 000 trades** sur le NAS100 de Deriv, 2024-2026, et **-0,12 R** sur
le même NAS100 chez Dukascopy, 2013-2019. Deux explications possibles, et elles n'ont pas du tout les
mêmes conséquences :

  · le marché a changé (spread relatif, microstructure) — alors la piste est peut-être vraie ;
  · **le flux de Deriv porte des mèches que le marché n'a pas** — alors la piste est une illusion
    fabriquée par les données, et tout backtest d'ordre limite sur ces bougies est faux.

On tranche en comparant les deux flux sur les MÊMES dates : les rendements minute doivent coller, et
surtout la forme des bougies (mèches) doit se ressembler. Une mèche qui n'existe que chez un
fournisseur remplit des ordres limites qui n'auraient jamais été servis.
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from . import banc, candidates_v2
from .lancer import DOSSIER


def _aligner(a: banc.Serie, b: banc.Serie):
    communs, ia, ib = np.intersect1d(a.temps, b.temps, return_indices=True)
    return communs, ia, ib


def meches(serie: banc.Serie, i: np.ndarray) -> dict:
    """La forme des bougies : combien la mèche dépasse le corps, et à quelle fréquence elle est
    extrême. C'est exactement ce qui remplit — ou non — un ordre limite."""
    o, h, b, c = (x[i] for x in (serie.ouverture, serie.haut, serie.bas, serie.cloture))
    corps = np.abs(c - o)
    basse = np.minimum(o, c) - b
    haute = h - np.maximum(o, c)
    ref = np.median(h - b)
    with np.errstate(invalid="ignore", divide="ignore"):
        part_basse = basse / np.maximum(h - b, 1e-12)
    return {"amplitude_mediane": round(float(ref), 4),
            "meche_basse_mediane": round(float(np.median(basse)), 4),
            "meche_haute_mediane": round(float(np.median(haute)), 4),
            "corps_median": round(float(np.median(corps)), 4),
            "part_meche_basse_mediane": round(float(np.median(part_basse)), 4),
            "minutes_meche_basse_sup_3x_amplitude": int(np.count_nonzero(basse > 3 * ref)),
            "minutes_meche_basse_sup_5x_amplitude": int(np.count_nonzero(basse > 5 * ref)),
            "amplitude_p99": round(float(np.quantile(h - b, 0.99)), 4)}


def signature(rendements: np.ndarray) -> dict:
    """La signature statistique d'un flux de prix, en trois nombres.

    · **autocorrélation à 1 minute** : positive = le prix traîne (quote lissée ou en retard, donc
      prévisible) ; négative = rebond acheteur-vendeur (bruit de cotation).
    · **ratio de variance** (variance à 5 min / 5 × variance à 1 min) : 1 = marche au hasard,
      au-dessus = tendance, en dessous = retour à la moyenne.
    Un flux qui s'écarte de 1 est exploitable… ou mal construit. C'est la même mesure qui le dit,
    et c'est pour ça qu'on la compare à un second fournisseur.
    """
    r = rendements[np.isfinite(rendements)]
    out = {f"autocorr_{k}": round(float(np.corrcoef(r[:-k], r[k:])[0, 1]), 4) for k in (1, 2, 5)}
    n5 = (len(r) // 5) * 5
    r5 = r[:n5].reshape(-1, 5).sum(axis=1)
    out["ratio_variance_5min"] = round(float(np.var(r5) / (5 * np.var(r))), 4)
    return out


def strategie(serie: banc.Serie, **reglages) -> dict:
    o = candidates_v2.rabais(serie, **reglages)
    t = banc.simuler(serie, o)
    if not len(t):
        return {"trades": 0}
    m = banc.mesurer(serie, t, series=False)
    return {k: m[k] for k in ("trades", "taux_objectif", "point_mort_objectif", "esperance_R",
                              "profit_factor", "p_objectif")}


def comparer(base: str, tf: str = "M1", **reglages) -> dict:
    deriv = banc.charger(base, tf, source="mt5")
    duka = banc.charger(base, tf, source="duka")
    debut = max(deriv.temps[0], duka.temps[0])
    fin = min(deriv.temps[-1], duka.temps[-1])
    if fin <= debut:
        raise SystemExit(f"aucune période commune : Deriv {deriv.temps[0]}→{deriv.temps[-1]}, "
                         f"Dukascopy {duka.temps[0]}→{duka.temps[-1]}")
    d1 = deriv.tranche(str(debut)[:10], str(fin)[:10])
    d2 = duka.tranche(str(debut)[:10], str(fin)[:10])
    communs, ia, ib = _aligner(d1, d2)
    ra = np.diff(d1.cloture[ia]) / d1.cloture[ia][:-1]
    rb = np.diff(d2.cloture[ib]) / d2.cloture[ib][:-1]
    sortie = {"base": base, "tf": tf, "periode": [str(debut)[:10], str(fin)[:10]],
              "minutes_deriv": len(d1), "minutes_dukascopy": len(d2), "minutes_communes": len(communs),
              "correlation_rendements": round(float(np.corrcoef(ra, rb)[0, 1]), 4),
              "volatilite_minute_deriv": round(float(np.std(ra)), 8),
              "volatilite_minute_dukascopy": round(float(np.std(rb)), 8),
              "signature_deriv": signature(ra), "signature_dukascopy": signature(rb),
              "meches_deriv": meches(d1, ia), "meches_dukascopy": meches(d2, ib),
              "strategie_deriv": strategie(d1, **reglages),
              "strategie_dukascopy": strategie(d2, **reglages)}
    (DOSSIER / f"flux_{base}_{tf}.json").write_text(json.dumps(sortie, ensure_ascii=False, default=str),
                                                    encoding="utf-8")
    return sortie


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="NAS100")
    p.add_argument("--tf", default="M1")
    p.add_argument("--remplissage", type=float, default=2.0)
    a = p.parse_args()
    d = comparer(a.base, a.tf, tendance=60, retrait=0.5, stop_atr=2.0, expiration_min=60,
                 remplissage=a.remplissage)
    print(f"\n  {d['base']} {d['tf']} · {d['periode'][0]} → {d['periode'][1]}")
    print(f"  minutes : Deriv {d['minutes_deriv']}, Dukascopy {d['minutes_dukascopy']}, "
          f"communes {d['minutes_communes']}")
    print(f"  corrélation des rendements minute : {d['correlation_rendements']}")
    print(f"  volatilité minute : Deriv {d['volatilite_minute_deriv']:.2e}, "
          f"Dukascopy {d['volatilite_minute_dukascopy']:.2e}")
    for nom in ("deriv", "dukascopy"):
        g = d[f"signature_{nom}"]
        print(f"  signature {nom:10s} : autocorrélation 1 min {g['autocorr_1']:+.4f}, 2 min "
              f"{g['autocorr_2']:+.4f}, 5 min {g['autocorr_5']:+.4f}, ratio de variance "
              f"{g['ratio_variance_5min']:.3f}")
    for nom in ("deriv", "dukascopy"):
        m = d[f"meches_{nom}"]
        print(f"  mèches {nom:10s} : amplitude médiane {m['amplitude_mediane']}, mèche basse "
              f"{m['meche_basse_mediane']} ({100 * m['part_meche_basse_mediane']:.0f} % de la bougie), "
              f"minutes à mèche > 3× amplitude : {m['minutes_meche_basse_sup_3x_amplitude']}")
    for nom in ("deriv", "dukascopy"):
        s = d[f"strategie_{nom}"]
        if s.get("trades"):
            print(f"  STRATÉGIE sur {nom:10s} : {s['trades']:6d} trades, objectif "
                  f"{100 * s['taux_objectif']:.1f} % (point mort {100 * s['point_mort_objectif']:.1f} %), "
                  f"espérance {s['esperance_R']:+.4f} R, PF {s['profit_factor']:.3f}")
        else:
            print(f"  STRATÉGIE sur {nom} : aucun trade")
    return 0


if __name__ == "__main__":
    sys.exit(main())

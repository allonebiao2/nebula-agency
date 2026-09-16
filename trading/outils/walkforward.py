# -*- coding: utf-8 -*-
"""
Le verdict sur l'historique réel : walk-forward sur ~20 ans d'EUR/USD.

    python -m trading.outils.walkforward                   # H4, capital 10 000
    python -m trading.outils.walkforward --capital 500
    python -m trading.outils.walkforward --sans-weekend    # garder les positions le week-end

Écrit `rapports/walkforward_<tf>[_variante].json`, que l'interface affiche.

Ce qui est mesuré ici est ce qu'aurait vécu quelqu'un qui aurait appliqué la
méthode en temps réel : réglages choisis sur les 4 années précédentes,
appliqués à l'année suivante sans la connaître. Les coûts sont ceux mesurés
chez le courtier (spread médian sur ticks, swaps réels, 1 point de glissement
défavorable par sens).
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from trading.backtest.metriques import rapport                     # noqa: E402
from trading.backtest.walkforward import walk_forward               # noqa: E402
from trading.noyau.config import charger                            # noqa: E402
from trading.noyau.donnees_mt5 import charger_historique, specs_et_couts  # noqa: E402
from trading.strategies import catalogue                            # noqa: E402

RAPPORTS = Path(__file__).resolve().parent.parent / "rapports"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tf", default="H4")
    ap.add_argument("--capital", type=float, default=10_000.0)
    ap.add_argument("--strategie", default="cassure_donchian")
    ap.add_argument("--apprentissage", type=int, default=4)
    ap.add_argument("--sans-weekend", action="store_true",
                    help="ne pas fermer les positions le vendredi soir")
    ap.add_argument("--nom", default="")
    args = ap.parse_args()

    cfg = charger()
    if args.sans_weekend:
        cfg = dataclasses.replace(
            cfg, calendrier=dataclasses.replace(cfg.calendrier, fermer_avant_weekend=False))
    barres = charger_historique("EURUSD", args.tf)
    specs, couts = specs_et_couts("EURUSD")
    if specs is None:
        print("⛔ Profil du courtier absent : lancer python -m trading.noyau.donnees_mt5")
        return 1
    fabrique = catalogue.STRATEGIES[args.strategie]

    print("=" * 72)
    print(f"  WALK-FORWARD · {args.strategie} · EURUSD {args.tf} · capital {args.capital:,.0f}"
          .replace(",", " "))
    print("=" * 72)
    print(f"  {len(barres)} barres, du {barres.quand(0):%Y-%m-%d} au "
          f"{barres.quand(len(barres) - 1):%Y-%m-%d}")
    print(f"  Coûts : {couts}")
    print(f"  Apprentissage {args.apprentissage} ans -> test 1 an · "
          f"fermeture du vendredi : {'NON' if args.sans_weekend else 'oui'}")
    print()

    t0 = time.time()
    rep = walk_forward(
        barres, fabrique, fabrique().espace_parametres, cfg=cfg, specs=specs, couts=couts,
        capital=args.capital, annees_apprentissage=args.apprentissage, rappel=print)
    print(f"\n  ({time.time() - t0:.0f} s)\n")
    print(rapport(rep.metriques, "WALK-FORWARD · RÉSULTATS HORS ÉCHANTILLON UNIQUEMENT"))
    print(f"\n  Efficacité (espérance test / apprentissage) : {rep.efficacite:.2f}")
    print("  Stabilité des réglages choisis :")
    for k, d in rep.stabilite_parametres().items():
        print(f"    {k:<16} " + " · ".join(f"{v} ×{n}" for v, n in d.items()))
    motifs: dict[str, int] = {}
    for t in rep.trades:
        motifs[t.motif_sortie] = motifs.get(t.motif_sortie, 0) + 1
    print("  Sorties : " + " · ".join(f"{m} {n}" for m, n in
                                       sorted(motifs.items(), key=lambda kv: -kv[1])))

    RAPPORTS.mkdir(exist_ok=True)
    suffixe = args.nom or ("sans_weekend" if args.sans_weekend else "")
    sortie = RAPPORTS / f"walkforward_{args.strategie}_{args.tf}{'_' + suffixe if suffixe else ''}.json"
    donnees = rep.en_dict()
    donnees.update({"strategie": args.strategie, "timeframe": args.tf,
                    "variante": suffixe or "reference", "couts": str(couts),
                    "sorties": motifs, "calcule_le": time.strftime("%Y-%m-%d %H:%M")})
    sortie.write_text(json.dumps(donnees, ensure_ascii=False, indent=1, default=str),
                      encoding="utf-8")
    print(f"\n  -> {sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

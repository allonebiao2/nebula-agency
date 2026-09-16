# -*- coding: utf-8 -*-
"""
Avec combien peut-on trader ? Mesuré, pas supposé.

    python -m trading.outils.capital

Deux mesures, écrites dans `rapports/capital.json` pour l'interface :

  1. VIABILITÉ : pour chaque capital et chaque type de compte, la part des
     stops RÉELS (2 × ATR mesurés sur l'historique récent) qu'on peut trader à
     1 %, puis au plafond du petit compte.
  2. BACKTEST PAR CAPITAL : la même stratégie, les mêmes coûts, sur les mêmes
     années, avec 50 $ ou 10 000 $, en compte standard et en compte cent.
     Ce qui change : combien de trades passent, et le rendement en %.

Le compte cent se simule honnêtement : solde et valeur du point en CENTS. Le
calcul de taille est exactement celui du courtier.
"""
from __future__ import annotations

import dataclasses
import json
import sys
from datetime import datetime

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from trading.backtest.moteur import Moteur                              # noqa: E402
from trading.live.agent import parametres_du_walkforward                # noqa: E402
from trading.noyau.capital import viabilite                             # noqa: E402
from trading.noyau.chemins import dossier_rapports                      # noqa: E402
from trading.noyau.config import charger                                # noqa: E402
from trading.noyau.donnees_mt5 import charger_historique, specs_et_couts  # noqa: E402
from trading.strategies import catalogue                                # noqa: E402
from trading.strategies.indicateurs import atr                          # noqa: E402

CAPITAUX = [10, 25, 50, 100, 250, 500, 700, 1000, 2500, 10000]


def main() -> int:
    cfg = charger()
    barres = charger_historique("EURUSD", cfg.marche.timeframe)
    specs, couts = specs_et_couts("EURUSD")

    # --- 1. viabilité sur les stops des deux dernières années ---------------
    a = atr(barres.haut, barres.bas, barres.cloture, cfg.risque.atr_periode)
    recents = a[-6 * 260 * 2:]
    stops = recents * cfg.risque.stop_loss_atr_multiple / specs.point
    vpl_min = specs.volume_min * specs.valeur_point_par_lot
    via = {
        "standard": viabilite(points_de_stop=stops, valeur_point_lot_min=vpl_min,
                              capitaux=CAPITAUX, risque_pct=cfg.risque.risque_par_trade_pct,
                              plafond_pct=cfg.risque.risque_max_petit_compte_pct),
        "cent": viabilite(points_de_stop=stops, valeur_point_lot_min=vpl_min,
                          capitaux=CAPITAUX, risque_pct=cfg.risque.risque_par_trade_pct,
                          plafond_pct=cfg.risque.risque_max_petit_compte_pct, facteur=100),
    }
    print("VIABILITÉ (stops réels des 2 dernières années, médiane "
          f"{np.nanmedian(stops):.0f} points)")
    print(f"  {'capital':>8} | {'standard 1 %':>12} {'std plafond':>11} | {'cent 1 %':>9}")
    for s, c in zip(via["standard"], via["cent"]):
        print(f"  {s['capital']:>7} $ | {s['a_1pct']:>11.0%} {s['au_plafond']:>11.0%} | "
              f"{c['a_1pct']:>8.0%}")

    # --- 2. backtest par capital, depuis 2019 ------------------------------
    nom = "cassure_donchian"
    params, origine = parametres_du_walkforward(nom, cfg.marche.timeframe,
                                                not cfg.calendrier.fermer_avant_weekend, "EURUSD")
    debut = int(np.searchsorted(barres.temps, np.datetime64("2019-01-01")))
    tranche = barres.tronquer(debut - 300, len(barres))
    # Compte cent : le solde est en CENTS, la valeur du point par lot garde le
    # même chiffre (1 lot cent = 1 000 unités, 1 point = 1 USC). Seul le capital
    # est multiplié par 100. ⚠️ Multiplier aussi la valeur du point (1er jet du
    # 2026-09-16) annule l'effet et recopie le compte standard.
    specs_cent = specs
    strict = dataclasses.replace(cfg, risque=dataclasses.replace(
        cfg.risque, risque_max_petit_compte_pct=cfg.risque.risque_par_trade_pct))

    lignes = []
    print(f"\nBACKTEST 2019-2026 par capital · {nom} {params} ({origine})")
    print(f"  {'capital':>8} | {'type':<18} | {'trades':>6} | {'rendement':>9} | {'DD max':>6} | "
          f"{'relevés':>7}")
    for cap in CAPITAUX:
        for type_, config, sp, cap_compte in (
                ("standard strict 1 %", strict, specs, cap),
                ("standard + plafond", cfg, specs, cap),
                ("cent", cfg, specs_cent, cap * 100)):
            res = Moteur(config, sp, couts, catalogue.STRATEGIES[nom](**params),
                         journaliser_refus=False).lancer(tranche, cap_compte, echauffement=300)
            m = res.metriques
            releves = sum(1 for t in res.trades
                          if abs(t.resultat_R) > 0 and t.lots <= sp.volume_min + 1e-9)
            rendement = 100 * (m.capital_final / m.capital_initial - 1) if m.trades else 0.0
            ligne = {"capital": cap, "type": type_, "trades": m.trades,
                     "rendement_pct": rendement, "drawdown_max_pct": m.drawdown_max_pct,
                     "esperance_R": m.esperance_R, "trades_lot_minimum": releves}
            lignes.append(ligne)
            print(f"  {cap:>7} $ | {type_:<18} | {m.trades:>6} | {rendement:>+8.1f} % | "
                  f"{m.drawdown_max_pct:>5.1f} % | {releves:>7}")

    sortie = dossier_rapports() / "capital.json"
    sortie.write_text(json.dumps({
        "calcule_le": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "stop_median_points": float(np.nanmedian(stops)),
        "viabilite": via, "backtest": lignes, "strategie": nom, "parametres": params,
        "periode": "2019-2026",
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  -> {sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

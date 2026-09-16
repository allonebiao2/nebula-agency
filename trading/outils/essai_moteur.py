# -*- coding: utf-8 -*-
"""
Essai du moteur sur données SYNTHÉTIQUES.

    python trading/outils/essai_moteur.py

⛔ CE QUE CET ESSAI NE PROUVE PAS : que la stratégie gagne. Les données sont
inventées. Un bon résultat ici ne veut strictement rien dire sur le marché réel,
et un mauvais non plus.

⛔ CE QU'IL PROUVE : que la mécanique tourne sans planter, que les coûts sont
bien facturés, que les verrous refusent au bon moment, que les positions se
ferment, et que les métriques se calculent. C'est un test de plomberie.

Le vrai verdict viendra de l'historique réel du courtier, en walk-forward.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from trading.backtest.couts import ModeleCouts                      # noqa: E402
from trading.backtest.metriques import rapport                      # noqa: E402
from trading.backtest.moteur import Moteur                          # noqa: E402
from trading.noyau.config import charger                            # noqa: E402
from trading.noyau.risque import SpecsSymbole                       # noqa: E402
from trading.strategies.base import Barres                          # noqa: E402
from trading.strategies.cassure_donchian import CassureDonchian     # noqa: E402


def horodatages_h4(n: int, debut: datetime) -> np.ndarray:
    """Des barres H4 qui sautent les week-ends, comme le vrai marché.

    Sans ça, la règle de fermeture du vendredi ne serait jamais exercée et le
    test passerait à côté d'un morceau entier du moteur.
    """
    temps, t = [], debut
    while len(temps) < n:
        if t.weekday() < 5 and not (t.weekday() == 4 and t.hour >= 21):
            temps.append(t)
        t += timedelta(hours=4)
    return np.array(temps, dtype="datetime64[s]")


def barres_synthetiques(n: int = 6000, graine: int = 7) -> Barres:
    """Marche aléatoire à régimes alternés : des phases de tendance, des ranges.

    On alterne délibérément, parce qu'une stratégie de cassure doit rencontrer
    les deux — la tester uniquement sur de la tendance serait se mentir.
    """
    rng = np.random.default_rng(graine)
    prix, sigma = 1.0850, 0.0016          # ~16 pips d'écart-type par barre H4

    derive = np.zeros(n)
    i = 0
    while i < n:
        duree = rng.integers(60, 320)
        if rng.random() < 0.45:           # phase directionnelle
            d = rng.normal(0, 0.00028)
        else:                             # phase de range
            d = 0.0
        derive[i:i + duree] = d
        i += duree

    cloture = np.empty(n)
    c = prix
    for k in range(n):
        c += derive[k] + rng.normal(0, sigma)
        cloture[k] = c

    ouverture = np.concatenate(([prix], cloture[:-1]))
    corps = np.abs(cloture - ouverture)
    meche = np.abs(rng.normal(0, sigma * 0.75, n))
    haut = np.maximum(ouverture, cloture) + meche
    bas = np.minimum(ouverture, cloture) - np.abs(rng.normal(0, sigma * 0.75, n))

    return Barres(
        temps=horodatages_h4(n, datetime(2021, 1, 4, 0, 0)),
        ouverture=ouverture, haut=haut, bas=bas, cloture=cloture,
        spread=np.full(n, 15.0), symbole="EURUSD", timeframe="H4",
    )


def main() -> int:
    cfg = charger()
    specs = SpecsSymbole(
        nom="EURUSD", point=0.00001, digits=5,
        volume_min=0.01, volume_max=100.0, volume_step=0.01,
        valeur_tick=1.0, taille_tick=0.00001, taille_contrat=100_000,
    )
    couts = ModeleCouts(spread_points=15, slippage_points=5)
    barres = barres_synthetiques()
    strategie = CassureDonchian()

    print("=" * 68)
    print("  ESSAI DU MOTEUR  ·  DONNÉES SYNTHÉTIQUES")
    print("=" * 68)
    print(f"  ⛔ Données INVENTÉES : aucun résultat ci-dessous ne dit quoi que ce")
    print(f"     soit sur la rentabilité réelle. C'est un test de plomberie.")
    print()
    print(f"  Barres        {len(barres)} en {barres.timeframe}, "
          f"du {barres.quand(0):%Y-%m-%d} au {barres.quand(len(barres) - 1):%Y-%m-%d}")
    print(f"  Stratégie     {strategie}")
    print(f"  Coûts         {couts}")

    trous = barres.trous(ecart_max_heures=5)
    print(f"  Trous         {len(trous)} (hors week-ends)")

    capital = 5_000.0
    moteur = Moteur(cfg, specs, couts, strategie)
    res = moteur.lancer(barres, capital_initial=capital)

    # Le coût en R : le chiffre qui décide de l'unité de temps.
    if res.trades:
        risque_moyen_pts = np.mean([
            abs(t.prix_entree - t.stop_initial) / specs.point for t in res.trades])
        print(f"  Coût en R     {couts.en_R(risque_moyen_pts):.3f} R par trade "
              f"(stop moyen {risque_moyen_pts:.0f} points)")

    print()
    print(rapport(res.metriques, "MÉCANIQUE DU MOTEUR (données synthétiques)"))

    print()
    print("  SIGNAUX ET REFUS")
    print(f"    Barres parcourues   {res.barres_vues}")
    print(f"    Signaux proposés    {res.signaux_proposes}")
    print(f"    Trades pris         {len(res.trades)}")
    print(f"    Taux de refus       {res.taux_de_refus:.0%}")
    for motif, nb in list(res.motifs_de_refus().items())[:6]:
        print(f"      {nb:>4}x  {motif[:58]}")

    if res.trades:
        print()
        print("  MOTIFS DE SORTIE")
        motifs: dict[str, int] = {}
        for t in res.trades:
            motifs[t.motif_sortie] = motifs.get(t.motif_sortie, 0) + 1
        for m, nb in sorted(motifs.items(), key=lambda kv: -kv[1]):
            print(f"      {nb:>4}x  {m}")

    print()
    print("  " + "─" * 64)
    print("  Rappel : ces chiffres mesurent le MOTEUR, pas la stratégie.")
    print("  Le verdict viendra de l'historique réel, en walk-forward.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

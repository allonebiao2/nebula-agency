# -*- coding: utf-8 -*-
"""
Démonstration des verrous : on voit le bot refuser des trades.

    python trading/outils/demo_verrous.py

Aucune connexion, aucun argent : ce sont des plans fabriqués à la main pour
montrer chaque refus. C'est le test qui prouve que la doctrine est appliquée et
pas seulement écrite.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from noyau.config import charger                                   # noqa: E402
from noyau.plan import (ACHAT, EtatSysteme, PlanDeTrade,            # noqa: E402
                        PlanInvalide, controle_prealable)
from noyau.risque import SpecsSymbole                               # noqa: E402

cfg = charger()

EURUSD = SpecsSymbole(
    nom="EURUSD", point=0.00001, digits=5,
    volume_min=0.01, volume_max=100.0, volume_step=0.01,
    valeur_tick=1.0, taille_tick=0.00001, taille_contrat=100_000,
)

ATR = 0.00350                      # 35 pips, ordre de grandeur H4 sur EUR/USD
MARDI_10H = datetime(2026, 9, 15, 10, 0)
CAPITAL = 2_000.0

PAS_D_ANNONCE = lambda t: (False, "")                              # noqa: E731
NFP_DANS_20_MIN = lambda t: (True, "NFP dans 20 min (impact élevé)")  # noqa: E731


def plan_de_base(**remplace) -> PlanDeTrade:
    champs = dict(
        symbole="EURUSD", sens=ACHAT,
        entree=1.08500, stop=1.07800, objectif=1.09900,   # 70 pips risqués, 140 visés
        these="Cassure de la borne haute du range hebdomadaire, dans le sens de la "
              "tendance D1 haussière.",
        atr=ATR, horodatage=MARDI_10H, strategie="demo",
    )
    champs.update(remplace)
    return PlanDeTrade(**champs)


def etat_sain(**remplace) -> EtatSysteme:
    base = dict(spread_points=12, spread_habituel_points=10, atr_courant=ATR,
                atr_plage_connue=(0.0015, 0.0080), pertes_consecutives=1,
                minutes_depuis_derniere_perte=600, trades_aujourdhui=0,
                trades_cette_semaine=2, confiance_modele=0.63,
                regime="tendance", regimes_favorables=("tendance", "expansion"))
    base.update(remplace)
    return EtatSysteme(**base)


def scenario(titre: str, plan, etat, annonce=PAS_D_ANNONCE, capital=CAPITAL,
             quand=MARDI_10H) -> None:
    print("\n" + "─" * 72)
    print(f"  {titre}")
    print("─" * 72)
    verdict = controle_prealable(plan, cfg, etat, capital=capital, specs=EURUSD,
                                 annonce_imminente=annonce, maintenant=quand)
    print(verdict.rapport())


print("=" * 72)
print("  LES VERROUS EN ACTION  ·  EUR/USD  ·  capital 2 000 USD")
print("=" * 72)

scenario("1. Un trade propre : tout doit passer", plan_de_base(), etat_sain())

scenario("2. Ratio R:R insuffisant (objectif à 1R au lieu de 2R)",
         plan_de_base(objectif=1.09200), etat_sain())

scenario("3. Stop trop serré : 15 pips là où la volatilité en demande 70",
         plan_de_base(stop=1.08350), etat_sain())

scenario("4. NFP dans 20 minutes", plan_de_base(), etat_sain(), annonce=NFP_DANS_20_MIN)

scenario("5. Le spread a triplé (ouverture erratique)",
         plan_de_base(), etat_sain(spread_points=34, spread_habituel_points=10))

scenario("6. Série noire en cours + régime défavorable",
         plan_de_base(), etat_sain(pertes_consecutives=6, regime="range",
                                   confiance_modele=0.41))

scenario("7. Revenge trading : une perte il y a 12 minutes",
         plan_de_base(), etat_sain(minutes_depuis_derniere_perte=12,
                                   trades_aujourdhui=2))

scenario("8. Capital trop petit pour ce stop (120 USD)",
         plan_de_base(), etat_sain(), capital=120.0)

scenario("9. Vendredi 19h : le gap du week-end guette",
         plan_de_base(horodatage=datetime(2026, 9, 18, 19, 0)), etat_sain(),
         quand=datetime(2026, 9, 18, 19, 0))

# --- Les plans qui ne peuvent même pas exister ------------------------------
print("\n" + "=" * 72)
print("  LES PLANS QUI NE PEUVENT MÊME PAS SE CONSTRUIRE")
print("=" * 72)
for titre, champs in (
    ("Thèse vide", dict(these="signal")),
    ("Achat avec le stop AU-DESSUS de l'entrée", dict(stop=1.09000)),
    ("Objectif du mauvais côté", dict(objectif=1.08000)),
    ("Pas de mesure de volatilité", dict(atr=0.0)),
):
    try:
        plan_de_base(**champs)
        print(f"  [X] {titre} : accepté (mauvais signe)")
    except PlanInvalide as e:
        print(f"  [OK] {titre}")
        print(f"        -> {str(e).splitlines()[0]}")

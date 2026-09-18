# NEBULA Trader · carnet de suivi

*Régénéré le 2026-09-18 03:23. Une ligne par trade, et l'écart à ce que le backtest promettait.*

## Ce que le backtest promet

- **66.8 %** des trades atteignent 2 R (intervalle de confiance 64.3 – 69.2 %, sur 1467 trades)
- **+0.960 R** par trade, écart-type 1.41 R
- gain moyen **+1.94 R**, perte moyenne **-1.05 R**
- **2.0 trades par jour**, durée médiane 17 minutes

## Le direct

**Aucun trade fermé pour l'instant.** Le carnet se remplira tout seul dès que l'agent tournera : chaque ouverture et chaque fermeture passent déjà par le journal (`trading/donnees/journal.db`).

⏳ Ce qu'il faut pour commencer : lancer l'agent en observation sur le démo `6305888` avec le profil du plan (échelle 6-4-3).

## Ce qu'on surveille, dans cet ordre

1. **Le taux de remplissage des ordres limites.** C'est la seule hypothèse du backtest qu'un courtier peut démentir, et toute la stratégie repose dessus.
2. **Le spread réellement payé**, contre les 70 points mesurés chez Deriv.
3. **Le taux de 2 R atteints**, comparé à l'intervalle de confiance ci-dessus.
4. **La série perdante en cours**, qui décide du palier de risque.

⚠️ Un écart ne se corrige pas le jour même. On note, on accumule, et on ne change une règle qu'avec assez de trades pour que le changement ne soit pas du bruit. Toute modification repasse par le registre et se juge en avant.


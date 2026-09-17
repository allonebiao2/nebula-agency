# NEBULA Trader · recherche de stratégies scalping et intraday (EUR/USD, NAS100)

## Verdict : NON, pas avec nos données. Aucun des 50 tests ne montre une rentabilité qu'on puisse distinguer de la chance après correction statistique.

*Généré par `python -m trading.recherche.rapport` à partir des résultats bruts. Coûts réels Deriv (spread médian mesuré sur ticks, 1 point de glissement par sens, swap), entrée à l'ouverture suivante, stop avant objectif dans une même bougie, objectif ≥ 2 R, stop jamais plus court que le minimum du courtier.*

## Les données utilisées

| Instrument | M1 | M5 | M15 | H1 |
|---|---|---|---|---|
| EURUSD | 2026-06 → 2026-09 (99 000 bougies) | 2025-05 → 2026-09 (99 000 bougies) | 2022-09 → 2026-09 (100 000 bougies) | 2010-08 → 2026-09 (100 000 bougies) |
| NAS100 | 2026-06 → 2026-09 (99 000 bougies) | 2025-04 → 2026-09 (99 000 bougies) | 2024-01 → 2026-09 (62 638 bougies) | 2024-01 → 2026-09 (15 686 bougies) |

⚠️ MT5 ne rend que les 100 000 dernières bougies de chaque unité de temps (réglage « Max. barres dans le graphique ») : **3 mois en M1 et 16 mois en M5**. Le NAS100 ne remonte qu'à janvier 2024 chez Deriv.

## 1. Les 5 stratégies publiées « à haut taux de réussite » (walk-forward, hors échantillon)

| Stratégie | Marché | Trades | Réussite | Espérance (R) | PF | R/mois | Drawdown à 1 % | p | Correction |
|---|---|---|---|---|---|---|---|---|---|
| Range de séance (Asie→Londres, ouverture US) | EURUSD M15 | 358 | 34,1 % | +0,087 | 1,13 | +1,35 | 20,6 % | 0,151 | non |
| Témoin : entrée au hasard | NAS100 H1 | 259 | 36,3 % | +0,051 | 1,08 | +0,86 | 16,6 % | 0,283 | témoin |
| Range de séance (Asie→Londres, ouverture US) | EURUSD M5 | 112 | 33,9 % | +0,049 | 1,08 | +0,72 | 24,8 % | 0,370 | non |
| EMA 200 + Stochastique | NAS100 M15 | 649 | 31,7 % | +0,042 | 1,06 | +1,78 | 23,9 % | 0,252 | non |
| Témoin : entrée au hasard | NAS100 M15 | 945 | 38,1 % | +0,035 | 1,06 | +2,16 | 29,5 % | 0,217 | témoin |
| Range de séance (Asie→Londres, ouverture US) | NAS100 M5 | 158 | 50,0 % | +0,001 | 1,00 | +0,02 | 9,2 % | 0,495 | non |
| Range de séance (Asie→Londres, ouverture US) | NAS100 M15 | 289 | 49,8 % | +0,000 | 1,00 | +0,00 | 12,6 % | 0,500 | non |
| Témoin : entrée au hasard | NAS100 M5 | 1508 | 36,1 % | -0,008 | 0,99 | -1,45 | 48,1 % | 0,587 | témoin |
| Bollinger + RSI(7) scalping | NAS100 M5 | 1518 | 30,4 % | -0,008 | 0,99 | -1,55 | 54,2 % | 0,578 | non |
| IBS / 3 barres en baisse | EURUSD H1 | 1824 | 35,9 % | -0,019 | 0,97 | -0,37 | 52,0 % | 0,724 | non |
| Bollinger + RSI(7) scalping | EURUSD M15 | 1454 | 34,3 % | -0,021 | 0,97 | -1,29 | 73,9 % | 0,701 | non |
| RSI(2) de Connors | EURUSD H1 | 1439 | 32,3 % | -0,026 | 0,96 | -0,40 | 54,7 % | 0,750 | non |
| Bollinger + RSI(7) scalping | EURUSD M5 | 1235 | 32,7 % | -0,036 | 0,95 | -5,77 | 51,1 % | 0,796 | non |
| EMA 200 + Stochastique | NAS100 M5 | 1076 | 35,4 % | -0,038 | 0,94 | -4,96 | 49,3 % | 0,820 | non |
| RSI(2) de Connors | EURUSD M15 | 971 | 37,2 % | -0,045 | 0,93 | -1,88 | 54,8 % | 0,853 | non |
| Témoin : entrée au hasard | EURUSD H1 | 1527 | 33,7 % | -0,047 | 0,93 | -0,78 | 64,3 % | 0,910 | témoin |
| Bollinger + RSI(7) scalping | NAS100 M15 | 909 | 32,7 % | -0,054 | 0,92 | -3,21 | 53,5 % | 0,861 | non |
| IBS / 3 barres en baisse | EURUSD M15 | 1062 | 35,5 % | -0,061 | 0,89 | -2,81 | 63,2 % | 0,933 | non |
| IBS / 3 barres en baisse | NAS100 M15 | 542 | 37,5 % | -0,066 | 0,89 | -2,35 | 41,4 % | 0,886 | non |
| EMA 200 + Stochastique | EURUSD M15 | 1010 | 32,1 % | -0,082 | 0,87 | -3,58 | 68,3 % | 0,965 | non |
| RSI(2) de Connors | NAS100 M15 | 966 | 28,6 % | -0,083 | 0,88 | -5,20 | 60,6 % | 0,955 | non |
| IBS / 3 barres en baisse | NAS100 H1 | 149 | 34,9 % | -0,097 | 0,85 | -0,95 | 19,6 % | 0,805 | non |
| RSI(2) de Connors | NAS100 H1 | 282 | 30,9 % | -0,112 | 0,84 | -2,05 | 30,1 % | 0,913 | non |
| Témoin : entrée au hasard | EURUSD M15 | 1504 | 33,2 % | -0,113 | 0,83 | -7,32 | 84,2 % | 1,000 | témoin |
| EMA 200 + Stochastique | EURUSD M5 | 1160 | 28,4 % | -0,191 | 0,75 | -28,86 | 91,6 % | 1,000 | non |
| Témoin : entrée au hasard | EURUSD M5 | 1533 | 30,3 % | -0,204 | 0,72 | -40,90 | 96,4 % | 1,000 | témoin |

## 2. Les deux vidéos

« auteur » = les règles telles que la vidéo les enseigne, sans rien optimiser. « adaptée » = une petite grille de réglages jugée hors échantillon.

| Stratégie | Marché | Trades | Réussite | Espérance (R) | PF | R/mois | Drawdown à 1 % | p | Correction |
|---|---|---|---|---|---|---|---|---|---|
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | NAS100 M1 | 6 | 83,3 % | +0,876 | 6,24 | +1,88 | 1,0 % | 0,052 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | NAS100 M15 | 1 | 100,0 % | +0,764 | infini | +23,27 | 0,0 % | 1,000 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | EURUSD M15 | 14 | 50,0 % | +0,655 | 2,79 | +0,23 | 1,9 % | 0,073 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | NAS100 M5 | 6 | 66,7 % | +0,566 | 2,69 | +0,22 | 1,0 % | 0,175 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | NAS100 M1 | 13 | 46,2 % | +0,525 | 1,95 | +2,67 | 4,0 % | 0,157 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | EURUSD M1 | 14 | 50,0 % | +0,345 | 1,64 | +1,69 | 3,2 % | 0,211 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | EURUSD M5 | 28 | 46,4 % | +0,297 | 1,59 | +0,54 | 3,1 % | 0,156 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | EURUSD H1 | 58 | 41,4 % | +0,127 | 1,32 | +0,04 | 7,0 % | 0,221 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | EURUSD H1 | 107 | 35,5 % | +0,022 | 1,05 | +0,03 | 14,4 % | 0,431 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | NAS100 M5 | 150 | 36,0 % | +0,018 | 1,03 | +0,33 | 16,8 % | 0,439 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | EURUSD H1 | 13 | 30,8 % | +0,011 | 1,02 | +0,00 | 3,8 % | 0,490 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | EURUSD H1 | 57 | 33,3 % | -0,004 | 0,99 | -0,00 | 7,0 % | 0,507 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | NAS100 M1 | 96 | 34,4 % | -0,021 | 0,97 | -1,31 | 17,0 % | 0,549 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | EURUSD M15 | 72 | 31,9 % | -0,026 | 0,96 | -0,09 | 13,9 % | 0,555 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | EURUSD M5 | 69 | 26,1 % | -0,057 | 0,92 | -0,25 | 21,7 % | 0,614 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | NAS100 M5 | 179 | 19,6 % | -0,058 | 0,93 | -1,33 | 25,5 % | 0,634 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | NAS100 M5 | 67 | 25,4 % | -0,064 | 0,91 | -0,26 | 18,4 % | 0,625 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | NAS100 M15 | 73 | 31,5 % | -0,073 | 0,89 | -0,35 | 15,9 % | 0,661 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | NAS100 M15 | 121 | 24,0 % | -0,082 | 0,88 | -0,32 | 26,4 % | 0,716 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | EURUSD M15 | 179 | 23,5 % | -0,156 | 0,79 | -0,59 | 26,9 % | 0,903 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | NAS100 M15 | 300 | 13,3 % | -0,170 | 0,81 | -3,31 | 67,4 % | 0,857 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | EURUSD M5 | 33 | 27,3 % | -0,207 | 0,72 | -1,02 | 14,2 % | 0,797 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | EURUSD M1 | 82 | 29,3 % | -0,215 | 0,70 | -12,18 | 20,5 % | 0,912 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | EURUSD M5 | 41 | 31,7 % | -0,258 | 0,60 | -1,40 | 14,5 % | 0,910 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | NAS100 M1 | 52 | 15,4 % | -0,291 | 0,64 | -10,51 | 18,5 % | 0,883 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | EURUSD M15 | 101 | 16,8 % | -0,307 | 0,65 | -1,36 | 34,1 % | 0,929 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | NAS100 H1 | 8 | 25,0 % | -0,356 | 0,49 | -0,10 | 4,2 % | 0,828 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | EURUSD M1 | 14 | 14,3 % | -0,375 | 0,54 | -1,80 | 8,8 % | 0,822 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | EURUSD M1 | 18 | 16,7 % | -0,510 | 0,44 | -9,99 | 9,2 % | 0,936 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | NAS100 H1 | 2 | 0,0 % | -0,985 | 0,00 | -0,10 | 2,0 % | 1,000 | non |

## 3. Le taux de réussite

- Le plus haut sur au moins 100 trades : **50,0 %**, Range de séance (Asie→Londres, ouverture US) sur NAS100 M5 (158 trades, espérance +0,001 R).
- **Aucun 80 %** sur un échantillon qui compte. Les 83 % de la vidéo MambaFx sur NAS100 M1 portent sur **6 trades** : l'intervalle de confiance va de 44 % à 97 %.
- À 1:2, le point mort est à **33,3 %** de réussite. Un taux de réussite élevé sans objectif d'au moins 2 R ne dit rien de la rentabilité.

## 4. PRO et BOOST : les stratégies retenues

**Aucune.** Retenir deux stratégies par profil sur ces chiffres, ce serait choisir au hasard parmi des résultats qu'on ne peut pas distinguer de zéro. Les pistes qui méritent plus de données :

- **Vidéo MambaFx (zone M5 + cassure M1)** · EURUSD M15 (auteur) : 14 trades, 50,0 %, +0,655 R, p = 0,07.
- **Range de séance (Asie→Londres, ouverture US)** · EURUSD M15 : 358 trades, 34,1 %, +0,087 R, p = 0,15.
- **Vidéo MambaFx (zone M5 + cassure M1)** · EURUSD M5 (auteur) : 28 trades, 46,4 %, +0,297 R, p = 0,16.
- **Vidéo MambaFx (zone M5 + cassure M1)** · EURUSD M1 (auteur) : 14 trades, 50,0 %, +0,345 R, p = 0,21.

## 5. Le million de dollars

Rendement **mensuel** composé à tenir chaque mois, sans une seule mauvaise année :

| Capital de départ | en 3 ans | en 5 ans | en 10 ans | en 20 ans |
|---|---|---|---|---|
| 1 000 $ | 21,2 % | 12,2 % | 5,9 % | 2,9 % |
| 10 000 $ | 13,6 % | 8,0 % | 3,9 % | 1,9 % |
| 100 000 $ | 6,6 % | 3,9 % | 1,9 % | 1,0 % |

**Si Range de séance (Asie→Londres, ouverture US) (EURUSD M15, +0,087 R, 15,5 trades par mois) gardait son espérance mesurée**, ce qui n'est pas prouvé :

| Capital | Risque par trade | P(1 M $ en 10 ans) | Délai médian si atteint | P(perdre 50 % en chemin) |
|---|---|---|---|---|
| 1 000 $ | 1 % | 0,0 % | jamais | 17,9 % |
| 1 000 $ | 3 % | 2,8 % | 8,8 ans | 99,9 % |
| 1 000 $ | 10 % | 9,6 % | 5,0 ans | 100,0 % |
| 10 000 $ | 1 % | 0,0 % | jamais | 17,9 % |
| 10 000 $ | 3 % | 22,4 % | 7,8 ans | 99,9 % |
| 10 000 $ | 10 % | 21,7 % | 3,1 ans | 100,0 % |

**Si EMA 200 + Stochastique (NAS100 M15, +0,042 R, 42,2 trades par mois) gardait son espérance mesurée**, ce qui n'est pas prouvé :

| Capital | Risque par trade | P(1 M $ en 10 ans) | Délai médian si atteint | P(perdre 50 % en chemin) |
|---|---|---|---|---|
| 1 000 $ | 1 % | 0,0 % | jamais | 74,6 % |
| 1 000 $ | 3 % | 5,3 % | 7,5 ans | 100,0 % |
| 1 000 $ | 10 % | 1,1 % | 1,7 ans | 100,0 % |
| 10 000 $ | 1 % | 0,3 % | 8,7 ans | 74,6 % |
| 10 000 $ | 3 % | 21,0 % | 6,5 ans | 100,0 % |
| 10 000 $ | 10 % | 4,1 % | 1,0 ans | 100,0 % |

## 6. Conseils

1. **Ne rien passer en réel.** Aucun résultat ne distingue un avantage de la chance.
2. **Donner plusieurs années de M1 au test des vidéos** : dans MT5, *Outils → Options → Graphiques → Max. barres dans le graphique* = « Unlimited », redémarrer MT5, puis relancer `python -m trading.noyau.donnees_mt5 M1 M5 --base EURUSD` (et `--base NAS100`) et `python -m trading.recherche.videos_lancer`. La vidéo MambaFx est la seule piste positive sur tous ses échantillons EUR/USD, mais sur 14 à 28 trades.
3. **Garder la règle 1:2 en PRO et en BOOST** (appliquée le 2026-09-17, le videur refuse désormais 1:1,5).
4. **Se méfier des preuves des vidéos** : captures de gains, replays choisis, abonnements et prop firms vendus dans la même vidéo. Aucune des deux ne publie une série de trades.
5. **Le million** exige un avantage réel ET du temps. Monter le risque ne remplace pas l'avantage : à espérance nulle, un risque plus grand ruine seulement plus vite.

## 7. Ce qui n'est pas modélisé, et pourquoi c'est écrit

- Passage au point mort et ajouts de positions (Hugo FX) : une seule position par instrument, règle maison.
- Lignes de tendance de MambaFx : remplacées par la structure (plus haut plus haut, plus bas plus haut, cassure).
- PD arrays et FVG de Hugo FX : remplacés par un retour sous 50 % (ou 62 %) de l'impulsion M15.
- Transposition H1 des vidéos : sortie temporelle calibrée pour le M1, trop courte pour une structure journalière.

## Sources

- StockCharts ChartSchool, RSI(2) : https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/rsi-2
- MQL5, Larry Connors RSI2 intraday : https://www.mql5.com/en/articles/17636
- learn-forextrading, 5 min scalping Bollinger + RSI : https://www.learn-forextrading.org/2017/06/5-min-scalping-bollinger-bands-and-rsi.html
- Alvarez Quant Trading, IBS : https://alvarezquanttrading.com/blog/internal-bar-strength-for-mean-reversion/
- ForexCracked, 200 EMA + Stochastic : https://www.forexcracked.com/education/forex-200-ema-and-stochastic-indicator-scalping-strategy/
- London breakout, backtests GitHub : https://github.com/adrian-baehler/london-breakout
- Vidéo MambaFx « The Only 1-Minute Scalping Strategy You'll EVER NEED » (fichier fourni)
- Vidéo Hugo FX « J'ai trouvé la MEILLEURE Stratégie de Scalping M1 pour 2026 ! » (fichier fourni)

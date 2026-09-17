# NEBULA Trader · recherche de stratégies scalping et intraday (EUR/USD, NAS100)

## Verdict : NON, pas avec nos données. Aucun des 146 tests ne montre une rentabilité qu'on puisse distinguer de la chance après correction statistique.

*Généré par `python -m trading.recherche.rapport` à partir des résultats bruts. Coûts réels Deriv (spread médian mesuré sur ticks, 1 point de glissement par sens, swap), entrée à l'ouverture suivante, stop avant objectif dans une même bougie, objectif ≥ 2 R, stop jamais plus court que le minimum du courtier.*

## 0. Ton objectif : R:R d'au moins 1:2 ET plus de 50 % de réussite

- Tests avec **plus de 50 % de trades gagnants, au moins 100 trades et une espérance positive** : **1** sur 146.
- Tests où **plus de la moitié des trades atteignent vraiment leur objectif d'au moins 2 R** : **0** sur 146.
- ⚠️ « Gagnant » compte tout trade fini au-dessus de zéro, y compris une petite sortie par le temps ou en fin de séance. C'est pour ça que les deux lignes diffèrent : seule la seconde dit « j'ai pris mes 2 R ».
- **Le calcul qui borne l'ambition** : à 1:2, gagner 2 R une fois sur deux rapporte **+0,5 R par trade** avant coûts. La meilleure espérance mesurée ici sur au moins 100 trades est de **+0,094 R**.

Les plus hauts taux de réussite sur au moins 100 trades :

| Stratégie | Marché | Trades | Gagnants | Objectif ≥ 2 R atteint | Espérance (R) |
|---|---|---|---|---|---|
| Range de séance (Asie→Londres, ouverture US) | NAS100 M1 | 320 | 53,8 % | 0,3 % | +0,032 |
| Range de séance (Asie→Londres, ouverture US) | NAS100 M15 | 289 | 49,8 % | 4,2 % | +0,000 |
| Range de séance (Asie→Londres, ouverture US) | NAS100 M30 | 267 | 49,4 % | 4,9 % | -0,003 |
| Range de séance (Asie→Londres, ouverture US) | NAS100 M5 | 304 | 49,3 % | 2,6 % | +0,035 |
| Range de séance (Asie→Londres, ouverture US) | EURUSD H4 | 1366 | 47,1 % | 2,3 % | -0,018 |
| Vidéo MambaFx (zone M5 + cassure M1) | EURUSD M5 | 262 | 41,2 % | 1,1 % | +0,061 |
| IBS / 3 barres en baisse | NAS100 M1 | 4943 | 40,2 % | 7,0 % | -0,027 |
| IBS / 3 barres en baisse | EURUSD M15 | 6014 | 40,0 % | 20,4 % | -0,009 |

## Les données utilisées

| Instrument | M1 | M5 | M15 | H1 |
|---|---|---|---|---|
| EURUSD | 2019-01 → 2026-09 (2 864 062 bougies) | 2012-01 → 2026-09 (1 093 502 bougies) | 2012-01 → 2026-09 (364 931 bougies) | 2005-01 → 2026-09 (134 605 bougies) |
| NAS100 | 2024-01 → 2026-09 (938 868 bougies) | 2024-01 → 2026-09 (187 885 bougies) | 2024-01 → 2026-09 (62 638 bougies) | 2024-01 → 2026-09 (15 686 bougies) |

MT5 réglé sur « Max. barres = Unlimited » par Mongazi le 2026-09-17 : **7,7 ans de M1 et 14,7 ans de M5 sur EUR/USD**. Le M1 est borné à 2019 (8 Go de mémoire vive). Le NAS100 ne remonte qu'à janvier 2024 chez Deriv, quelle que soit l'unité de temps.

## 1. Les 5 stratégies publiées « à haut taux de réussite » (walk-forward, hors échantillon)

| Stratégie | Marché | Trades | Réussite | Espérance (R) | PF | R/mois | Drawdown à 1 % | p | Correction |
|---|---|---|---|---|---|---|---|---|---|
| Témoin : entrée au hasard | NAS100 H4 | 71 | 42,3 % | +0,189 | 1,32 | +0,88 | 6,4 % | 0,137 | témoin |
| EMA 200 + Stochastique | NAS100 H1 | 126 | 33,3 % | +0,094 | 1,14 | +0,77 | 11,0 % | 0,264 | non |
| Témoin : entrée au hasard | NAS100 H1 | 259 | 36,3 % | +0,051 | 1,08 | +0,86 | 16,6 % | 0,283 | témoin |
| Bollinger + RSI(7) scalping | NAS100 H4 | 56 | 33,9 % | +0,051 | 1,08 | +0,18 | 13,8 % | 0,402 | non |
| Bollinger + RSI(7) scalping | NAS100 H1 | 242 | 36,8 % | +0,048 | 1,08 | +0,76 | 16,1 % | 0,306 | non |
| RSI(2) de Connors | NAS100 M30 | 333 | 36,3 % | +0,045 | 1,07 | +0,98 | 17,4 % | 0,289 | non |
| EMA 200 + Stochastique | NAS100 M15 | 649 | 31,7 % | +0,042 | 1,06 | +1,78 | 23,9 % | 0,252 | non |
| Témoin : entrée au hasard | NAS100 M15 | 945 | 38,1 % | +0,035 | 1,06 | +2,16 | 29,5 % | 0,217 | témoin |
| Range de séance (Asie→Londres, ouverture US) | NAS100 M5 | 304 | 49,3 % | +0,035 | 1,10 | +0,69 | 9,7 % | 0,238 | non |
| Range de séance (Asie→Londres, ouverture US) | NAS100 M1 | 320 | 53,8 % | +0,032 | 1,17 | +0,66 | 6,7 % | 0,146 | non |
| Témoin : entrée au hasard | NAS100 M30 | 480 | 36,0 % | +0,029 | 1,05 | +0,90 | 21,3 % | 0,326 | témoin |
| RSI(2) de Connors | EURUSD H4 | 470 | 33,8 % | +0,020 | 1,03 | +0,08 | 23,9 % | 0,384 | non |
| EMA 200 + Stochastique | NAS100 M30 | 333 | 33,9 % | +0,013 | 1,02 | +0,27 | 21,6 % | 0,439 | non |
| RSI(2) de Connors | EURUSD M15 | 3303 | 35,1 % | +0,012 | 1,02 | +0,45 | 67,2 % | 0,329 | non |
| IBS / 3 barres en baisse | EURUSD M30 | 3122 | 37,3 % | +0,011 | 1,02 | +0,40 | 48,2 % | 0,331 | non |
| RSI(2) de Connors | EURUSD H1 | 1710 | 34,2 % | +0,000 | 1,00 | +0,01 | 42,9 % | 0,496 | non |
| Range de séance (Asie→Londres, ouverture US) | NAS100 M15 | 289 | 49,8 % | +0,000 | 1,00 | +0,00 | 12,6 % | 0,500 | non |
| Range de séance (Asie→Londres, ouverture US) | NAS100 M30 | 267 | 49,4 % | -0,003 | 0,99 | -0,05 | 14,4 % | 0,518 | non |
| IBS / 3 barres en baisse | EURUSD M15 | 6014 | 40,0 % | -0,009 | 0,98 | -0,61 | 81,3 % | 0,709 | non |
| Bollinger + RSI(7) scalping | EURUSD H4 | 470 | 30,2 % | -0,009 | 0,99 | -0,03 | 33,7 % | 0,547 | non |
| RSI(2) de Connors | NAS100 M5 | 2234 | 35,4 % | -0,015 | 0,98 | -2,11 | 69,3 % | 0,681 | non |
| Range de séance (Asie→Londres, ouverture US) | EURUSD H1 | 2054 | 36,8 % | -0,015 | 0,98 | -0,24 | 61,5 % | 0,688 | non |
| RSI(2) de Connors | EURUSD M30 | 2243 | 35,0 % | -0,017 | 0,97 | -0,45 | 50,0 % | 0,716 | non |
| Range de séance (Asie→Londres, ouverture US) | EURUSD H4 | 1366 | 47,1 % | -0,018 | 0,94 | -0,20 | 40,3 % | 0,800 | non |
| IBS / 3 barres en baisse | EURUSD H1 | 2112 | 37,5 % | -0,020 | 0,97 | -0,34 | 52,1 % | 0,758 | non |
| IBS / 3 barres en baisse | NAS100 M5 | 1265 | 39,0 % | -0,023 | 0,96 | -1,86 | 55,2 % | 0,729 | non |
| Bollinger + RSI(7) scalping | EURUSD H1 | 2101 | 34,8 % | -0,025 | 0,96 | -0,41 | 69,9 % | 0,782 | non |
| IBS / 3 barres en baisse | NAS100 M1 | 4943 | 40,2 % | -0,027 | 0,95 | -8,73 | 91,1 % | 0,925 | non |
| Témoin : entrée au hasard | NAS100 M5 | 2822 | 35,8 % | -0,031 | 0,95 | -5,69 | 76,2 % | 0,882 | témoin |
| Range de séance (Asie→Londres, ouverture US) | EURUSD M30 | 1428 | 34,2 % | -0,031 | 0,95 | -0,53 | 58,6 % | 0,794 | non |
| RSI(2) de Connors | NAS100 H4 | 72 | 27,8 % | -0,033 | 0,96 | -0,15 | 13,5 % | 0,567 | non |
| Témoin : entrée au hasard | EURUSD H1 | 2096 | 34,3 % | -0,034 | 0,95 | -0,58 | 70,8 % | 0,873 | témoin |
| EMA 200 + Stochastique | NAS100 M5 | 2034 | 34,4 % | -0,039 | 0,94 | -5,18 | 70,6 % | 0,891 | non |
| Range de séance (Asie→Londres, ouverture US) | EURUSD M15 | 1424 | 30,3 % | -0,040 | 0,94 | -0,67 | 69,3 % | 0,829 | non |
| Bollinger + RSI(7) scalping | NAS100 M30 | 423 | 34,8 % | -0,042 | 0,93 | -1,17 | 32,0 % | 0,729 | non |
| IBS / 3 barres en baisse | EURUSD H4 | 662 | 28,7 % | -0,044 | 0,94 | -0,23 | 53,3 % | 0,763 | non |
| Range de séance (Asie→Londres, ouverture US) | EURUSD M1 | 526 | 36,1 % | -0,044 | 0,93 | -0,53 | 28,5 % | 0,767 | non |
| RSI(2) de Connors | NAS100 M1 | 9546 | 34,6 % | -0,045 | 0,93 | -27,60 | 99,8 % | 0,997 | non |
| EMA 200 + Stochastique | NAS100 H4 | 56 | 33,9 % | -0,045 | 0,93 | -0,16 | 11,2 % | 0,594 | non |
| EMA 200 + Stochastique | EURUSD H1 | 1337 | 33,5 % | -0,047 | 0,93 | -0,51 | 56,8 % | 0,890 | non |
| EMA 200 + Stochastique | EURUSD M30 | 2375 | 33,6 % | -0,049 | 0,92 | -1,37 | 78,3 % | 0,952 | non |
| Range de séance (Asie→Londres, ouverture US) | EURUSD M5 | 1319 | 29,9 % | -0,051 | 0,93 | -0,80 | 65,9 % | 0,878 | non |
| EMA 200 + Stochastique | NAS100 M1 | 10415 | 33,9 % | -0,052 | 0,92 | -34,92 | 99,9 % | 1,000 | non |
| Bollinger + RSI(7) scalping | NAS100 M15 | 909 | 32,7 % | -0,054 | 0,92 | -3,21 | 53,5 % | 0,861 | non |
| Bollinger + RSI(7) scalping | EURUSD M30 | 2802 | 31,0 % | -0,059 | 0,91 | -1,97 | 89,8 % | 0,981 | non |
| Bollinger + RSI(7) scalping | NAS100 M5 | 2499 | 30,5 % | -0,059 | 0,92 | -9,62 | 87,0 % | 0,969 | non |
| EMA 200 + Stochastique | EURUSD M15 | 4498 | 32,8 % | -0,065 | 0,90 | -3,49 | 97,7 % | 0,999 | non |
| IBS / 3 barres en baisse | NAS100 M15 | 542 | 37,5 % | -0,066 | 0,89 | -2,35 | 41,4 % | 0,886 | non |
| Bollinger + RSI(7) scalping | EURUSD M15 | 5597 | 31,5 % | -0,070 | 0,90 | -4,66 | 99,1 % | 1,000 | non |
| Bollinger + RSI(7) scalping | NAS100 M1 | 11091 | 32,4 % | -0,075 | 0,89 | -53,69 | 100,0 % | 1,000 | non |
| Bollinger + RSI(7) scalping | EURUSD M5 | 13244 | 32,2 % | -0,075 | 0,89 | -11,76 | 100,0 % | 1,000 | non |
| RSI(2) de Connors | EURUSD M5 | 10563 | 32,7 % | -0,077 | 0,89 | -9,61 | 100,0 % | 1,000 | non |
| IBS / 3 barres en baisse | EURUSD M5 | 10659 | 37,1 % | -0,077 | 0,87 | -9,72 | 100,0 % | 1,000 | non |
| EMA 200 + Stochastique | EURUSD H4 | 413 | 33,7 % | -0,080 | 0,88 | -0,27 | 37,0 % | 0,891 | non |
| Témoin : entrée au hasard | EURUSD M15 | 5486 | 34,7 % | -0,082 | 0,87 | -5,33 | 99,3 % | 1,000 | témoin |
| RSI(2) de Connors | NAS100 M15 | 966 | 28,6 % | -0,083 | 0,88 | -5,20 | 60,6 % | 0,955 | non |
| Témoin : entrée au hasard | NAS100 M1 | 14938 | 33,5 % | -0,092 | 0,87 | -88,81 | 100,0 % | 1,000 | témoin |
| IBS / 3 barres en baisse | NAS100 H1 | 149 | 34,9 % | -0,097 | 0,85 | -0,95 | 19,6 % | 0,805 | non |
| RSI(2) de Connors | EURUSD M1 | 10107 | 25,5 % | -0,101 | 0,88 | -23,13 | 100,0 % | 1,000 | non |
| Témoin : entrée au hasard | EURUSD M30 | 2702 | 32,4 % | -0,107 | 0,84 | -3,43 | 95,8 % | 1,000 | témoin |
| Témoin : entrée au hasard | EURUSD M5 | 16466 | 33,8 % | -0,111 | 0,84 | -21,64 | 100,0 % | 1,000 | témoin |
| RSI(2) de Connors | NAS100 H1 | 282 | 30,9 % | -0,112 | 0,84 | -2,05 | 30,1 % | 0,913 | non |
| EMA 200 + Stochastique | EURUSD M5 | 11054 | 33,0 % | -0,113 | 0,83 | -14,82 | 100,0 % | 1,000 | non |
| Bollinger + RSI(7) scalping | EURUSD M1 | 18298 | 31,8 % | -0,114 | 0,84 | -46,91 | 100,0 % | 1,000 | non |
| Témoin : entrée au hasard | EURUSD H4 | 565 | 31,2 % | -0,119 | 0,83 | -0,54 | 52,1 % | 0,982 | témoin |
| IBS / 3 barres en baisse | EURUSD M1 | 18716 | 27,7 % | -0,131 | 0,83 | -55,53 | 100,0 % | 1,000 | non |
| IBS / 3 barres en baisse | NAS100 M30 | 295 | 27,8 % | -0,136 | 0,82 | -2,63 | 36,2 % | 0,935 | non |
| EMA 200 + Stochastique | EURUSD M1 | 17310 | 27,3 % | -0,140 | 0,82 | -54,96 | 100,0 % | 1,000 | non |
| Témoin : entrée au hasard | EURUSD M1 | 23368 | 31,7 % | -0,160 | 0,78 | -84,37 | 100,0 % | 1,000 | témoin |
| IBS / 3 barres en baisse | NAS100 H4 | 49 | 28,6 % | -0,197 | 0,74 | -0,68 | 12,9 % | 0,838 | non |

## 2. Les vidéos

« auteur » = les règles telles que la vidéo les enseigne, sans rien optimiser. « adaptée » = une petite grille de réglages jugée hors échantillon.

| Stratégie | Marché | Trades | Réussite | Espérance (R) | PF | R/mois | Drawdown à 1 % | p | Correction |
|---|---|---|---|---|---|---|---|---|---|
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | NAS100 M15 | 1 | 100,0 % | +0,764 | infini | +23,27 | 0,0 % | 1,000 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur + point mort) | NAS100 M15 | 1 | 100,0 % | +0,764 | infini | +23,27 | 0,0 % | 1,000 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | EURUSD H4 | 16 | 56,2 % | +0,378 | 2,08 | +0,08 | 3,2 % | 0,134 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | EURUSD H4 | 70 | 25,7 % | +0,366 | 1,54 | +0,10 | 8,8 % | 0,100 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | EURUSD H1 | 72 | 29,2 % | +0,307 | 1,49 | +0,09 | 7,5 % | 0,122 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur + point mort) | EURUSD H4 | 70 | 28,6 % | +0,288 | 1,52 | +0,08 | 8,8 % | 0,140 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | EURUSD M15 | 51 | 41,2 % | +0,282 | 1,61 | +0,09 | 8,0 % | 0,090 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur + point mort) | EURUSD H1 | 72 | 26,4 % | +0,188 | 1,37 | +0,05 | 7,2 % | 0,216 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | NAS100 M30 | 39 | 35,9 % | +0,140 | 1,22 | +0,36 | 4,9 % | 0,311 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | NAS100 M5 | 9 | 44,4 % | +0,136 | 1,29 | +0,05 | 2,7 % | 0,382 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur + point mort) | EURUSD H1 | 17 | 35,3 % | +0,122 | 1,22 | +0,01 | 3,6 % | 0,376 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | NAS100 M30 | 49 | 22,4 % | +0,065 | 1,09 | +0,11 | 12,1 % | 0,413 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | EURUSD M5 | 262 | 41,2 % | +0,061 | 1,11 | +0,19 | 18,8 % | 0,249 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | NAS100 M5 | 74 | 32,4 % | +0,051 | 1,09 | +0,25 | 11,5 % | 0,393 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur + point mort) | NAS100 M1 | 124 | 20,2 % | +0,047 | 1,09 | +0,19 | 20,6 % | 0,360 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur + point mort) | NAS100 M5 | 10 | 30,0 % | +0,047 | 1,12 | +0,02 | 2,6 % | 0,453 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur + point mort) | NAS100 M5 | 124 | 20,2 % | +0,043 | 1,09 | +0,17 | 20,6 % | 0,369 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur + point mort) | NAS100 M1 | 45 | 28,9 % | +0,029 | 1,06 | +0,04 | 9,9 % | 0,444 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur + point mort) | NAS100 H1 | 2 | 50,0 % | +0,015 | infini | +0,00 | 0,0 % | 0,159 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | EURUSD H1 | 17 | 29,4 % | +0,003 | 1,00 | +0,00 | 5,4 % | 0,497 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur + point mort) | EURUSD M15 | 52 | 23,1 % | +0,000 | 1,00 | +0,00 | 12,7 % | 0,499 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | NAS100 M1 | 45 | 35,6 % | -0,004 | 0,99 | -0,01 | 11,3 % | 0,507 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | EURUSD H1 | 153 | 20,3 % | -0,008 | 0,98 | -0,01 | 27,0 % | 0,520 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | EURUSD M1 | 239 | 34,7 % | -0,025 | 0,96 | -0,14 | 37,3 % | 0,597 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur + point mort) | NAS100 M15 | 122 | 19,7 % | -0,026 | 0,95 | -0,10 | 23,2 % | 0,578 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | EURUSD M5 | 227 | 34,8 % | -0,030 | 0,95 | -0,04 | 20,0 % | 0,627 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | NAS100 M1 | 80 | 41,2 % | -0,041 | 0,93 | -0,22 | 13,8 % | 0,614 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | NAS100 M5 | 123 | 25,2 % | -0,046 | 0,93 | -0,18 | 24,7 % | 0,623 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | NAS100 M1 | 123 | 25,2 % | -0,047 | 0,93 | -0,19 | 25,0 % | 0,626 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | EURUSD M1 | 367 | 36,8 % | -0,059 | 0,91 | -0,24 | 32,7 % | 0,791 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | EURUSD M15 | 94 | 34,0 % | -0,074 | 0,86 | -0,08 | 19,3 % | 0,709 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur + point mort) | NAS100 M30 | 49 | 12,2 % | -0,080 | 0,86 | -0,13 | 10,9 % | 0,627 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | NAS100 M30 | 84 | 11,9 % | -0,084 | 0,87 | -0,47 | 24,6 % | 0,652 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | NAS100 M5 | 302 | 12,6 % | -0,087 | 0,88 | -1,71 | 63,8 % | 0,721 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | NAS100 M15 | 121 | 23,1 % | -0,089 | 0,88 | -0,35 | 27,7 % | 0,730 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur + point mort) | EURUSD M5 | 228 | 24,1 % | -0,101 | 0,81 | -0,13 | 30,8 % | 0,888 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur + point mort) | EURUSD M1 | 373 | 26,0 % | -0,101 | 0,81 | -0,41 | 36,9 % | 0,943 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur + point mort) | EURUSD M5 | 805 | 17,0 % | -0,107 | 0,82 | -0,49 | 64,1 % | 0,981 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | NAS100 M1 | 331 | 9,4 % | -0,122 | 0,79 | -2,62 | 62,6 % | 0,840 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | EURUSD H1 | 61 | 29,5 % | -0,137 | 0,76 | -0,08 | 12,6 % | 0,803 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | EURUSD M5 | 802 | 23,3 % | -0,137 | 0,82 | -0,62 | 71,7 % | 0,991 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | EURUSD M1 | 342 | 23,1 % | -0,139 | 0,81 | -0,52 | 44,6 % | 0,943 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur + point mort) | EURUSD M1 | 343 | 15,7 % | -0,148 | 0,74 | -0,55 | 43,9 % | 0,977 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur + point mort) | EURUSD M15 | 797 | 15,8 % | -0,148 | 0,76 | -0,67 | 72,6 % | 0,997 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | NAS100 M15 | 290 | 11,4 % | -0,160 | 0,80 | -3,03 | 66,6 % | 0,844 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | NAS100 M15 | 72 | 27,8 % | -0,165 | 0,74 | -0,79 | 18,5 % | 0,842 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | EURUSD M30 | 91 | 19,8 % | -0,175 | 0,77 | -0,09 | 18,5 % | 0,850 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | EURUSD M15 | 794 | 20,9 % | -0,184 | 0,76 | -0,83 | 79,2 % | 0,999 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur + point mort) | NAS100 M30 | 3 | 33,3 % | -0,187 | 0,44 | -0,04 | 1,0 % | 0,670 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur + point mort) | EURUSD M30 | 91 | 14,3 % | -0,242 | 0,57 | -0,13 | 23,8 % | 0,975 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | EURUSD H4 | 103 | 20,4 % | -0,267 | 0,60 | -0,22 | 37,8 % | 0,945 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur + point mort) | EURUSD M30 | 25 | 20,0 % | -0,304 | 0,48 | -0,05 | 9,0 % | 0,911 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | EURUSD M30 | 108 | 11,1 % | -0,316 | 0,59 | -0,42 | 32,8 % | 0,958 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (adaptée, hors échantillon) | EURUSD M30 | 65 | 26,2 % | -0,325 | 0,49 | -0,26 | 20,0 % | 0,991 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | EURUSD H4 | 2 | 50,0 % | -0,340 | 0,32 | -0,01 | 1,0 % | 0,698 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur + point mort) | EURUSD H4 | 2 | 50,0 % | -0,340 | 0,32 | -0,01 | 1,0 % | 0,698 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | EURUSD M15 | 319 | 12,2 % | -0,373 | 0,53 | -1,41 | 74,0 % | 1,000 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | EURUSD M5 | 284 | 11,3 % | -0,384 | 0,53 | -1,30 | 71,0 % | 1,000 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (adaptée, hors échantillon) | EURUSD M1 | 169 | 13,0 % | -0,399 | 0,53 | -1,54 | 50,5 % | 0,998 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur + point mort) | NAS100 H1 | 8 | 12,5 % | -0,457 | 0,40 | -0,13 | 5,9 % | 0,856 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | EURUSD M30 | 25 | 20,0 % | -0,467 | 0,38 | -0,07 | 12,6 % | 0,979 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | NAS100 M30 | 3 | 33,3 % | -0,523 | 0,22 | -0,12 | 2,0 % | 0,861 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | NAS100 H1 | 8 | 12,5 % | -0,583 | 0,34 | -0,16 | 6,9 % | 0,913 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur) | NAS100 H4 | 8 | 12,5 % | -0,583 | 0,34 | -0,16 | 6,9 % | 0,913 | non |
| Vidéo Hugo FX (CRT H1 + swing M15) (auteur + point mort) | NAS100 H4 | 8 | 12,5 % | -0,583 | 0,34 | -0,16 | 6,9 % | 0,913 | non |
| Vidéo MambaFx (zone M5 + cassure M1) (auteur) | NAS100 H1 | 2 | 0,0 % | -0,985 | 0,00 | -0,10 | 2,0 % | 1,000 | non |

### La troisième vidéo : « Sniper Entry » (balayage M15, clôture M1)

Testée à part, en M1 avec simulation bid/ask minute par minute, historique des annonces Forex Factory et compte de 10 000 $ : **détail complet dans `trading/RECHERCHE-SNIPER.md`**.

| Stratégie | Marché | Trades | Réussite | Espérance (R) | PF | R/mois | Drawdown à 1 % | p | Correction |
|---|---|---|---|---|---|---|---|---|---|
| Vidéo Sniper Entry + cassure du dernier creux M1 | NAS100 M1 | 935 | 26,6 % | -0,020 | 0,97 | -0,60 | 50,4 % | 0,642 | non |
| Vidéo Sniper Entry, meilleures heures (contrôle) | EURUSD M1 | 309 | 25,9 % | -0,036 | 0,95 | -0,60 | 32,5 % | 0,645 | non |
| Vidéo Sniper Entry, objectif 5 R | NAS100 M1 | 1041 | 18,5 % | -0,049 | 0,94 | -1,62 | 64,6 % | 0,772 | non |
| Vidéo Sniper Entry, objectif 2 R | NAS100 M1 | 1077 | 32,0 % | -0,064 | 0,91 | -2,17 | 63,8 % | 0,934 | non |
| Vidéo Sniper Entry (balayage M15 + clôture M1), telle quelle | NAS100 M1 | 1087 | 24,7 % | -0,064 | 0,92 | -2,20 | 66,3 % | 0,894 | non |
| Vidéo Sniper Entry, stop trop court sauté | NAS100 M1 | 1069 | 24,7 % | -0,074 | 0,90 | -2,49 | 69,8 % | 0,924 | non |
| Vidéo Sniper Entry + filtre des annonces | NAS100 M1 | 1070 | 24,7 % | -0,075 | 0,90 | -2,52 | 70,1 % | 0,927 | non |
| Vidéo Sniper Entry + sortie avant annonce | NAS100 M1 | 1073 | 25,3 % | -0,075 | 0,90 | -2,54 | 69,7 % | 0,931 | non |
| Vidéo Sniper Entry, objectif au niveau opposé | NAS100 M1 | 1047 | 19,6 % | -0,085 | 0,90 | -2,82 | 70,5 % | 0,901 | non |
| Vidéo Sniper Entry, stop trop court sauté | EURUSD M1 | 2620 | 24,0 % | -0,106 | 0,86 | -3,02 | 95,9 % | 1,000 | non |
| Vidéo Sniper Entry + filtre des annonces | EURUSD M1 | 2941 | 23,8 % | -0,113 | 0,86 | -3,58 | 97,7 % | 1,000 | non |
| Vidéo Sniper Entry + sortie avant annonce | EURUSD M1 | 2952 | 24,9 % | -0,114 | 0,85 | -3,65 | 97,8 % | 1,000 | non |
| Vidéo Sniper Entry (balayage M15 + clôture M1), telle quelle | EURUSD M1 | 3018 | 23,6 % | -0,116 | 0,85 | -3,80 | 98,1 % | 1,000 | non |
| Vidéo Sniper Entry, objectif 2 R | EURUSD M1 | 2981 | 30,4 % | -0,118 | 0,83 | -3,80 | 97,9 % | 1,000 | non |
| Vidéo Sniper Entry + imbalance exigé | EURUSD M1 | 967 | 23,8 % | -0,121 | 0,84 | -1,27 | 75,8 % | 0,989 | non |
| Vidéo Sniper Entry, objectif au niveau opposé | EURUSD M1 | 2887 | 19,5 % | -0,121 | 0,85 | -3,78 | 98,3 % | 0,999 | non |
| Vidéo Sniper Entry + imbalance exigé | NAS100 M1 | 331 | 23,0 % | -0,143 | 0,82 | -1,50 | 48,2 % | 0,946 | non |
| Vidéo Sniper Entry + cassure du dernier creux M1 | EURUSD M1 | 2555 | 23,4 % | -0,145 | 0,81 | -4,01 | 98,3 % | 1,000 | non |
| Vidéo Sniper Entry, objectif 5 R | EURUSD M1 | 2874 | 17,1 % | -0,148 | 0,83 | -4,60 | 99,2 % | 1,000 | non |
| Vidéo Sniper Entry, variantes (walk-forward) (adaptée, hors échantillon) | EURUSD M1 | 576 | 22,4 % | -0,152 | 0,81 | -1,98 | 65,1 % | 0,982 | non |
| Vidéo Sniper Entry, variantes (walk-forward) (adaptée, hors échantillon) | NAS100 M1 | 298 | 21,1 % | -0,207 | 0,74 | -4,01 | 52,7 % | 0,987 | non |
| Vidéo Sniper Entry, meilleures heures (contrôle) | NAS100 M1 | 93 | 21,5 % | -0,220 | 0,73 | -3,33 | 20,3 % | 0,898 | non |

### Les vidéos, version auteur, année par année

**Vidéo Hugo FX (CRT H1 + swing M15) · EURUSD H1** (2005-01-02 -> 2026-09-17, 72 trades, 29,2 %, +0,307 R par trade)

| Année | Trades | Réussite | Somme des R |
|---|---|---|---|
| 2005 | 2 | 50,0 % | +3,9 |
| 2006 | 1 | 0,0 % | -0,6 |
| 2007 | 4 | 25,0 % | +0,7 |
| 2008 | 2 | 50,0 % | -0,3 |
| 2009 | 3 | 33,3 % | +3,1 |
| 2010 | 2 | 0,0 % | -2,1 |
| 2011 | 2 | 50,0 % | +2,8 |
| 2012 | 5 | 40,0 % | +1,8 |
| 2013 | 2 | 0,0 % | -1,4 |
| 2014 | 4 | 50,0 % | +3,1 |
| 2015 | 2 | 0,0 % | -1,8 |
| 2016 | 5 | 20,0 % | -3,4 |
| 2017 | 4 | 25,0 % | -0,7 |
| 2018 | 6 | 16,7 % | +4,1 |
| 2019 | 3 | 33,3 % | +5,9 |
| 2020 | 7 | 28,6 % | +1,7 |
| 2021 | 3 | 66,7 % | +5,7 |
| 2022 | 5 | 60,0 % | +5,9 |
| 2023 | 2 | 50,0 % | +0,3 |
| 2024 | 4 | 0,0 % | -2,8 |
| 2025 | 3 | 0,0 % | -3,1 |
| 2026 | 1 | 0,0 % | -0,8 |

**Vidéo Hugo FX (CRT H1 + swing M15) · EURUSD H4** (2005-01-02 -> 2026-09-17, 70 trades, 25,7 %, +0,366 R par trade)

| Année | Trades | Réussite | Somme des R |
|---|---|---|---|
| 2005 | 2 | 50,0 % | +3,9 |
| 2006 | 1 | 0,0 % | -0,6 |
| 2007 | 4 | 25,0 % | +2,7 |
| 2008 | 2 | 50,0 % | +1,5 |
| 2009 | 3 | 33,3 % | +3,1 |
| 2010 | 2 | 0,0 % | -2,1 |
| 2011 | 2 | 50,0 % | +2,8 |
| 2012 | 5 | 20,0 % | -1,1 |
| 2013 | 2 | 50,0 % | +1,3 |
| 2014 | 3 | 66,7 % | +7,7 |
| 2015 | 2 | 0,0 % | -1,8 |
| 2016 | 5 | 0,0 % | -4,8 |
| 2017 | 4 | 25,0 % | -0,7 |
| 2018 | 6 | 16,7 % | +4,1 |
| 2019 | 3 | 33,3 % | +5,9 |
| 2020 | 7 | 28,6 % | +1,3 |
| 2021 | 2 | 50,0 % | +1,3 |
| 2022 | 5 | 60,0 % | +9,6 |
| 2023 | 2 | 0,0 % | -2,0 |
| 2024 | 4 | 0,0 % | -2,8 |
| 2025 | 3 | 0,0 % | -3,1 |
| 2026 | 1 | 0,0 % | -0,8 |

**Vidéo Hugo FX (CRT H1 + swing M15) · EURUSD M1** (2019-01-02 -> 2026-09-17, 342 trades, 23,1 %, -0,139 R par trade)

| Année | Trades | Réussite | Somme des R |
|---|---|---|---|
| 2019 | 34 | 20,6 % | -5,7 |
| 2020 | 43 | 18,6 % | -17,0 |
| 2021 | 42 | 23,8 % | -0,4 |
| 2022 | 58 | 22,4 % | -9,0 |
| 2023 | 43 | 27,9 % | +3,8 |
| 2024 | 33 | 18,2 % | -10,1 |
| 2025 | 51 | 31,4 % | +3,9 |
| 2026 | 38 | 18,4 % | -13,3 |

**Vidéo Hugo FX (CRT H1 + swing M15) · EURUSD M15** (2012-01-01 -> 2026-09-17, 794 trades, 20,9 %, -0,184 R par trade)

| Année | Trades | Réussite | Somme des R |
|---|---|---|---|
| 2012 | 80 | 17,5 % | -26,6 |
| 2013 | 94 | 22,3 % | -13,9 |
| 2014 | 65 | 26,2 % | -6,4 |
| 2015 | 54 | 18,5 % | -10,2 |
| 2016 | 48 | 22,9 % | +0,6 |
| 2017 | 60 | 21,7 % | -9,8 |
| 2018 | 55 | 18,2 % | -19,1 |
| 2019 | 34 | 17,6 % | -8,5 |
| 2020 | 41 | 14,6 % | -23,1 |
| 2021 | 42 | 23,8 % | +4,7 |
| 2022 | 58 | 22,4 % | -6,4 |
| 2023 | 43 | 27,9 % | +4,6 |
| 2024 | 33 | 18,2 % | -9,5 |
| 2025 | 51 | 27,5 % | +5,3 |
| 2026 | 36 | 8,3 % | -28,0 |

**Vidéo Hugo FX (CRT H1 + swing M15) · EURUSD M30** (2012-01-01 -> 2026-09-17, 91 trades, 19,8 %, -0,175 R par trade)

| Année | Trades | Réussite | Somme des R |
|---|---|---|---|
| 2012 | 4 | 0,0 % | -3,8 |
| 2013 | 5 | 20,0 % | -0,7 |
| 2014 | 4 | 25,0 % | -0,8 |
| 2015 | 8 | 25,0 % | -1,0 |
| 2016 | 9 | 11,1 % | -5,8 |
| 2017 | 9 | 33,3 % | +6,8 |
| 2018 | 7 | 14,3 % | -3,3 |
| 2019 | 8 | 37,5 % | +2,9 |
| 2020 | 6 | 0,0 % | -5,3 |
| 2021 | 7 | 14,3 % | -2,3 |
| 2022 | 3 | 0,0 % | -2,1 |
| 2023 | 4 | 50,0 % | +3,8 |
| 2024 | 6 | 16,7 % | -1,4 |
| 2025 | 4 | 0,0 % | -3,1 |
| 2026 | 7 | 28,6 % | +0,2 |

**Vidéo Hugo FX (CRT H1 + swing M15) · EURUSD M5** (2012-01-01 -> 2026-09-17, 802 trades, 23,3 %, -0,137 R par trade)

| Année | Trades | Réussite | Somme des R |
|---|---|---|---|
| 2012 | 79 | 20,3 % | -20,0 |
| 2013 | 95 | 25,3 % | -1,8 |
| 2014 | 66 | 30,3 % | -2,3 |
| 2015 | 55 | 20,0 % | -5,6 |
| 2016 | 48 | 22,9 % | -3,8 |
| 2017 | 61 | 24,6 % | -6,6 |
| 2018 | 56 | 19,6 % | -18,8 |
| 2019 | 34 | 17,6 % | -8,5 |
| 2020 | 43 | 18,6 % | -17,6 |
| 2021 | 42 | 23,8 % | -0,7 |
| 2022 | 58 | 22,4 % | -9,1 |
| 2023 | 43 | 30,2 % | +4,0 |
| 2024 | 33 | 18,2 % | -10,2 |
| 2025 | 51 | 31,4 % | +4,1 |
| 2026 | 38 | 18,4 % | -13,1 |

**Vidéo Hugo FX (CRT H1 + swing M15) · NAS100 M1** (2024-01-22 -> 2026-09-17, 123 trades, 25,2 %, -0,047 R par trade)

| Année | Trades | Réussite | Somme des R |
|---|---|---|---|
| 2024 | 42 | 31,0 % | +6,3 |
| 2025 | 48 | 14,6 % | -18,1 |
| 2026 | 33 | 33,3 % | +6,1 |

**Vidéo Hugo FX (CRT H1 + swing M15) · NAS100 M15** (2024-01-22 -> 2026-09-17, 121 trades, 23,1 %, -0,089 R par trade)

| Année | Trades | Réussite | Somme des R |
|---|---|---|---|
| 2024 | 41 | 29,3 % | +3,8 |
| 2025 | 47 | 10,6 % | -21,8 |
| 2026 | 33 | 33,3 % | +7,2 |

**Vidéo Hugo FX (CRT H1 + swing M15) · NAS100 M30** (2024-01-22 -> 2026-09-17, 49 trades, 22,4 %, +0,065 R par trade)

| Année | Trades | Réussite | Somme des R |
|---|---|---|---|
| 2024 | 19 | 31,6 % | +9,9 |
| 2025 | 20 | 20,0 % | -2,4 |
| 2026 | 10 | 10,0 % | -4,3 |

**Vidéo Hugo FX (CRT H1 + swing M15) · NAS100 M5** (2024-01-22 -> 2026-09-17, 123 trades, 25,2 %, -0,046 R par trade)

| Année | Trades | Réussite | Somme des R |
|---|---|---|---|
| 2024 | 42 | 31,0 % | +6,3 |
| 2025 | 48 | 14,6 % | -17,7 |
| 2026 | 33 | 33,3 % | +5,8 |

**Vidéo MambaFx (zone M5 + cassure M1) · EURUSD M1** (2019-01-02 -> 2026-09-17, 367 trades, 36,8 %, -0,059 R par trade)

| Année | Trades | Réussite | Somme des R |
|---|---|---|---|
| 2019 | 46 | 30,4 % | -10,8 |
| 2020 | 42 | 42,9 % | +5,0 |
| 2021 | 61 | 41,0 % | +6,5 |
| 2022 | 44 | 40,9 % | +1,3 |
| 2023 | 32 | 40,6 % | +6,3 |
| 2024 | 56 | 30,4 % | -19,3 |
| 2025 | 54 | 35,2 % | -6,8 |
| 2026 | 32 | 34,4 % | -3,9 |

**Vidéo MambaFx (zone M5 + cassure M1) · EURUSD M15** (2012-01-01 -> 2026-09-17, 51 trades, 41,2 %, +0,282 R par trade)

| Année | Trades | Réussite | Somme des R |
|---|---|---|---|
| 2012 | 3 | 33,3 % | +0,1 |
| 2013 | 5 | 40,0 % | +1,4 |
| 2014 | 1 | 100,0 % | +0,2 |
| 2015 | 1 | 100,0 % | +3,0 |
| 2016 | 2 | 100,0 % | +3,8 |
| 2017 | 6 | 33,3 % | +0,1 |
| 2018 | 2 | 0,0 % | -2,0 |
| 2019 | 8 | 25,0 % | -3,4 |
| 2020 | 3 | 33,3 % | -1,5 |
| 2021 | 6 | 33,3 % | +3,4 |
| 2022 | 2 | 100,0 % | +6,0 |
| 2023 | 3 | 33,3 % | -0,0 |
| 2024 | 4 | 50,0 % | +2,2 |
| 2025 | 4 | 50,0 % | +2,1 |
| 2026 | 1 | 0,0 % | -1,0 |

**Vidéo MambaFx (zone M5 + cassure M1) · EURUSD M5** (2012-01-01 -> 2026-09-17, 227 trades, 34,8 %, -0,030 R par trade)

| Année | Trades | Réussite | Somme des R |
|---|---|---|---|
| 2012 | 20 | 50,0 % | +4,1 |
| 2013 | 13 | 15,4 % | -8,0 |
| 2014 | 12 | 25,0 % | -3,6 |
| 2015 | 16 | 31,2 % | -1,8 |
| 2016 | 11 | 18,2 % | -2,9 |
| 2017 | 16 | 37,5 % | +2,9 |
| 2018 | 14 | 28,6 % | -4,7 |
| 2019 | 15 | 53,3 % | +12,0 |
| 2020 | 16 | 12,5 % | -10,7 |
| 2021 | 17 | 35,3 % | -2,3 |
| 2022 | 10 | 60,0 % | +5,9 |
| 2023 | 17 | 41,2 % | -0,6 |
| 2024 | 18 | 22,2 % | -3,8 |
| 2025 | 17 | 41,2 % | +4,0 |
| 2026 | 15 | 46,7 % | +2,6 |

**Vidéo MambaFx (zone M5 + cassure M1) · NAS100 M1** (2024-01-22 -> 2026-09-17, 45 trades, 35,6 %, -0,004 R par trade)

| Année | Trades | Réussite | Somme des R |
|---|---|---|---|
| 2024 | 14 | 35,7 % | +0,6 |
| 2025 | 17 | 17,6 % | -6,8 |
| 2026 | 14 | 57,1 % | +6,0 |


## 3. Le taux de réussite

- Le plus haut sur au moins 100 trades : **53,8 %**, Range de séance (Asie→Londres, ouverture US) sur NAS100 M1 (320 trades, espérance +0,032 R).
- **Aucun 80 % sur 100 trades ou plus.** Le plus haut taux affiché, 100,0 % (Vidéo MambaFx (zone M5 + cassure M1), NAS100 M15), porte sur **1 trades** : l'intervalle de confiance va de 20,7 % à 100,0 %.
- À 1:2, le point mort est à **33,3 %** de réussite. Un taux de réussite élevé sans objectif d'au moins 2 R ne dit rien de la rentabilité.

## 4. PRO et BOOST : les stratégies retenues

**Aucune.** Retenir deux stratégies par profil sur ces chiffres, ce serait choisir au hasard parmi des résultats qu'on ne peut pas distinguer de zéro. Les pistes qui méritent plus de données :

- **Vidéo MambaFx (zone M5 + cassure M1)** · EURUSD M15 (auteur) : 51 trades, 41,2 %, +0,282 R, p = 0,09.
- **Vidéo Hugo FX (CRT H1 + swing M15)** · EURUSD H4 (auteur) : 70 trades, 25,7 %, +0,366 R, p = 0,10.
- **Vidéo Hugo FX (CRT H1 + swing M15)** · EURUSD H1 (auteur) : 72 trades, 29,2 %, +0,307 R, p = 0,12.
- **Vidéo MambaFx (zone M5 + cassure M1)** · EURUSD H4 : 16 trades, 56,2 %, +0,378 R, p = 0,13.

## 5. Le million de dollars

Rendement **mensuel** composé à tenir chaque mois, sans une seule mauvaise année :

| Capital de départ | en 3 ans | en 5 ans | en 10 ans | en 20 ans |
|---|---|---|---|---|
| 1 000 $ | 21,2 % | 12,2 % | 5,9 % | 2,9 % |
| 10 000 $ | 13,6 % | 8,0 % | 3,9 % | 1,9 % |
| 100 000 $ | 6,6 % | 3,9 % | 1,9 % | 1,0 % |

**Si Range de séance (Asie→Londres, ouverture US) (NAS100 M1, +0,032 R, 20,8 trades par mois) gardait son espérance mesurée**, ce qui n'est pas prouvé :

| Capital | Risque par trade | P(1 M $ en 10 ans) | Délai médian si atteint | P(perdre 50 % en chemin) |
|---|---|---|---|---|
| 1 000 $ | 1 % | 0,0 % | jamais | 0,0 % |
| 1 000 $ | 3 % | 0,0 % | jamais | 7,4 % |
| 1 000 $ | 10 % | 16,5 % | 8,4 ans | 100,0 % |
| 10 000 $ | 1 % | 0,0 % | jamais | 0,0 % |
| 10 000 $ | 3 % | 0,0 % | 9,7 ans | 7,4 % |
| 10 000 $ | 10 % | 49,5 % | 6,9 ans | 100,0 % |

**Si Range de séance (Asie→Londres, ouverture US) (NAS100 M5, +0,035 R, 19,7 trades par mois) gardait son espérance mesurée**, ce qui n'est pas prouvé :

| Capital | Risque par trade | P(1 M $ en 10 ans) | Délai médian si atteint | P(perdre 50 % en chemin) |
|---|---|---|---|---|
| 1 000 $ | 1 % | 0,0 % | jamais | 0,4 % |
| 1 000 $ | 3 % | 0,0 % | jamais | 73,4 % |
| 1 000 $ | 10 % | 4,5 % | 7,9 ans | 100,0 % |
| 10 000 $ | 1 % | 0,0 % | jamais | 0,4 % |
| 10 000 $ | 3 % | 0,5 % | 9,3 ans | 73,4 % |
| 10 000 $ | 10 % | 18,2 % | 6,0 ans | 100,0 % |

## 6. Conseils

1. **Ne rien passer en réel.** Aucun résultat ne distingue un avantage de la chance.
2. **Ne pas croire un résultat court** : un échantillon de quelques mois ou de quelques dizaines de trades dit presque toujours n'importe quoi. Pour le vérifier : `python -m trading.recherche.videos_lancer` puis `python -m trading.recherche.rapport`.
3. **Garder la règle 1:2 en PRO et en BOOST** (appliquée le 2026-09-17, le videur refuse désormais 1:1,5).
4. **Se méfier des preuves des vidéos** : captures de gains, replays choisis, abonnements et prop firms vendus dans la même vidéo. Aucune des trois ne publie une série de trades.
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
- Vidéo Mulham Trading « My Secret 1 Minute Scalping Strategy (Sniper Entry) » (fichier fourni)
- Calendrier économique Forex Factory, pages hebdomadaires 2019-2026 : https://www.forexfactory.com/calendar

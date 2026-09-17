# NEBULA Trader · recherche d'une stratégie de SCALPING (EUR/USD, NAS100)

## Verdict : NON, pas encore. **Aucun test ne dépasse 50 % de 2 R atteints sur au moins 100 trades**, et rien ne survit à la correction.

- Meilleur taux de 2 R atteints : **41.0 %** (t6_rabais_EURUSD_M1_mt52019, 29173 trades, point mort 37.6 %).

- Objectif de Mongazi : **plus de 50 %** (idéal 60-70 %) de 2 R atteints, R:R 1:2, et un risque très bas de 5-6 pertes d'affilée.
- Rappel calculé : à 50 % de 2 R, la probabilité de 5 pertes d'affilée sur 100 trades vaut encore **81 %** ; elle ne tombe sous 5 % (6 pertes) qu'à partir de **70 %**.
- Protocole, données scellées et paliers : `trading/RECHERCHE-SANS-FIN.md`.

## 1. Le plafond : jusqu'où 2 R peut tomber avant 1 R, dans la journée

Sur chaque minute, on regarde ce qui serait arrivé dans les DEUX sens. Un devin qui choisirait toujours le bon sens atteindrait le « plafond ». **Aucune règle, aucun modèle, aucune intuition ne peut le dépasser.** En face, le « point mort » est le taux d'objectif qui rend l'espérance nulle, coûts et fins de journée compris.

**EURUSD M1**

| stop | plafond (devin parfait) | point mort | coût aller-retour | durée médiane |
|---|---|---|---|---|
| 20 points | **57.7 %** | 37.1 % | 0.250 R | 4 barres |
| 30 points | **57.3 %** | 35.0 % | 0.167 R | 9 barres |
| 50 points | **53.7 %** | 31.9 % | 0.100 R | 24 barres |
| 80 points | **47.6 %** | 28.1 % | 0.062 R | 55 barres |
| 120 points | **39.7 %** | 23.7 % | 0.042 R | 105 barres |
| 200 points | **24.5 %** | 15.9 % | 0.025 R | 201 barres |
| 300 points | **12.3 %** | 9.4 % | 0.017 R | 290 barres |
| 500 points | **2.8 %** | 3.9 % | 0.010 R | 383 barres |

**NAS100 M1**

| stop | plafond (devin parfait) | point mort | coût aller-retour | durée médiane |
|---|---|---|---|---|
| 150 points | **37.6 %** | 41.3 % | 0.480 R | 0 barres |
| 250 points | **49.7 %** | 38.1 % | 0.288 R | 0 barres |
| 400 points | **57.6 %** | 36.3 % | 0.180 R | 0 barres |
| 700 points | **62.6 %** | 35.0 % | 0.103 R | 2 barres |
| 1200 points | **63.8 %** | 34.1 % | 0.060 R | 6 barres |
| 2000 points | **62.8 %** | 32.7 % | 0.036 R | 16 barres |
| 3500 points | **58.3 %** | 29.5 % | 0.021 R | 44 barres |

## 2. Entrer sur un retour de prix (ordre limite)

La géométrie change : depuis un meilleur prix, l'objectif est plus près en valeur absolue. ⛔ Piège mesuré : à 0,5 R de retrait les deux sens sont des miroirs exacts, donc « au moins un des deux gagne » vaut 99 % **par construction**. Seuls comptent les taux par sens, rapportés aux ordres servis.

## 3. Le modèle : ce qu'on sait prévoir, mesuré hors échantillon

Un modèle par sens apprend P(2 R avant 1 R) sur les caractéristiques causales, walk-forward purgé. On lit la précision parmi les minutes où il est le plus sûr : si les 1 % les plus sûres ne dépassent pas le point mort, il n'y a rien à prendre.

- **EURUSD M1 pts50** (mt5 2019-01→2026-09) : taux de base 27.2 %, précision moyenne du 1 % le plus sûr **32.2 %**
  - seuil 0.40 : 7057 trades, objectif atteint 32.3 % (point mort 34.6 %), espérance -0.068 R
  - seuil 0.45 : 2155 trades, objectif atteint 31.6 % (point mort 34.3 %), espérance -0.079 R
  - seuil 0.50 : 835 trades, objectif atteint 32.6 % (point mort 34.0 %), espérance -0.042 R
  - seuil 0.55 : 400 trades, objectif atteint 31.2 % (point mort 34.2 %), espérance -0.087 R
  - seuil 0.60 : 211 trades, objectif atteint 32.7 % (point mort 34.0 %), espérance -0.037 R
- **NAS100 M1 pts1200** (mt5 2024-01→2026-09) : taux de base 32.1 %, précision moyenne du 1 % le plus sûr **32.1 %**
  - seuil 0.40 : 12201 trades, objectif atteint 33.1 % (point mort 34.3 %), espérance -0.036 R
  - seuil 0.45 : 4794 trades, objectif atteint 33.4 % (point mort 34.2 %), espérance -0.026 R
  - seuil 0.50 : 2263 trades, objectif atteint 33.8 % (point mort 34.2 %), espérance -0.011 R
  - seuil 0.55 : 1065 trades, objectif atteint 34.2 % (point mort 34.2 %), espérance -0.002 R
  - seuil 0.60 : 548 trades, objectif atteint 34.1 % (point mort 34.2 %), espérance -0.002 R

## 4. La recherche exhaustive de règles

Toutes les paires de conditions (puis les meilleurs triplets) sont essayées sur la période d'apprentissage, puis rejouées après la coupe et passées au simulateur. **Le nombre d'essais est publié** : c'est lui qui décide de ce qu'on a le droit de croire.

**NAS100 M1 pts1200** · 54946 règles essayées

| règle | sens | apprentissage | validation | trades | 2 R atteints |
|---|---|---|---|---|---|
| dist_bas_veille>41.9724 ET dist_haut_jour>18.4084 | achat | 43.0 % (n=1278) | 47.4 % (n=840) | 151 | 39.1 % |
| dist_haut_jour>12.2286 ET pente_ema200>5.11619 | vente | 38.6 % (n=1844) | 40.3 % (n=935) | 245 | 33.1 % |
| pente_ema200>10.1012 ET pente_ema50<=-1.91758 | achat | 42.0 % (n=2568) | 40.0 % (n=1461) | 260 | 37.7 % |
| jour_semaine>3 ET position_dans_le_jour>0.94023 | vente | 36.7 % (n=6315) | 39.5 % (n=3218) | 744 | 37.6 % |
| dist_haut_jour>12.2286 ET position_dans_le_jour>0.580674 | vente | 40.1 % (n=2357) | 38.9 % (n=1409) | 324 | 34.3 % |
| dist_haut_veille<=1.04257 ET pente_ema50<=-3.93776 | vente | 38.7 % (n=1999) | 37.3 % (n=941) | 271 | 32.1 % |
| depuis_ouverture_jour<=-13.8963 ET ecart_ema200>3.72689 | vente | 42.4 % (n=784) | 37.2 % (n=656) | 166 | 31.9 % |
| dist_bas_jour>26.2961 ET dist_haut_jour>12.2286 | vente | 43.0 % (n=839) | 36.9 % (n=797) | 164 | 34.8 % |

## 5. Le registre

- **360 tests comptés** (témoins exclus), correction de Holm à 5 % sur le registre entier.
- **3 survivant(s).**

Les plus hauts taux de 2 R atteints, sur au moins 100 trades :

| test | trades | 2 R atteints | point mort | espérance | p |
|---|---|---|---|---|---|
| t6_rabais_EURUSD_M1_mt52019 | 29173 | **41.0 %** | 37.6 % | +0.101 R | 0.000 |
| t6_rabais_NAS100_M1_duka2013 | 25786 | **40.1 %** | 39.9 % | +0.006 R | 0.240 |
| t6_exces_EURUSD_M15_mt52012 | 141 | **34.8 %** | 29.6 % | +0.144 R | 0.108 |
| t6_balayage_niveau_EURUSD_M1_mt52019 | 3446 | **33.5 %** | 36.1 % | -0.079 R | 0.999 |
| t6_rabais_NAS100_M5_mt52024 | 2705 | **33.0 %** | 25.9 % | +0.191 R | 0.000 |
| t6_exces_NAS100_M1_mt52024 | 5614 | **32.4 %** | 33.6 % | -0.035 R | 0.970 |
| t6_exces_NAS100_M15_mt52024 | 383 | **32.1 %** | 29.9 % | +0.064 R | 0.181 |
| t6_exces_EURUSD_M5_mt52012 | 571 | **32.0 %** | 31.7 % | +0.011 R | 0.437 |
| t6_exces_EURUSD_M1_mt52019 | 5128 | **31.9 %** | 35.8 % | -0.117 R | 1.000 |
| t6_suite_EURUSD_M1_mt52019 | 12439 | **31.5 %** | 35.9 % | -0.132 R | 1.000 |


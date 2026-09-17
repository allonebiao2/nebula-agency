# NEBULA Trader · recherche d'une stratégie de SCALPING (EUR/USD, NAS100)

## Verdict : **l'objectif tel qu'il est écrit n'est pas atteignable en intraday**, et ce n'est pas une opinion : c'est mesuré.

Un devin qui choisirait toujours le bon sens atteindrait **63,8 %** de 2 R sur NAS100 M1 et **57,7 %** sur EUR/USD M1 (section 2). Viser « plus de 50 % » revient donc à exiger de choisir le bon sens **trois fois sur quatre**, et viser 60-70 % est au-dessus du plafond lui-même. Sur tous les tests de cette recherche, le meilleur taux de 2 R atteints est de **41 %**.

**Mais la recherche a trouvé quelque chose d'autre** : une stratégie qui gagne de l'argent sans remplir ces critères — 40.3 % de 2 R, +0.165 R par trade, **confirmée sur des années scellées** (29362 trades jamais regardés). C'est le profil que Mongazi appelait « nul » : un taux de réussite bas, compensé par un gain moyen presque deux fois la perte moyenne. Section 1.

- Meilleur taux de 2 R atteints : **41.2 %** (candidat_rabais_SCELLÉ · coût relatif au pri, 29893 trades, point mort 33.5 %).

- Objectif de Mongazi : **plus de 50 %** (idéal 60-70 %) de 2 R atteints, R:R 1:2, et un risque très bas de 5-6 pertes d'affilée.
- Rappel calculé : à 50 % de 2 R, la probabilité de 5 pertes d'affilée sur 100 trades vaut encore **81 %** ; elle ne tombe sous 5 % (6 pertes) qu'à partir de **70 %**.
- Protocole, données scellées et paliers : `trading/RECHERCHE-SANS-FIN.md`.

## 1. Le seul candidat de la recherche : l'entrée limite « au rabais »

**La règle** : dans le sens de l'EMA 60 minutes, poser un ordre limite à 0,5 R sous le prix (au-dessus, en vente), stop à 2 × ATR(14), objectif à 2 R, ordre annulé après 60 minutes, position fermée au plus tard à la clôture de la journée. NAS100, M1.

| période | trades | 2 R atteints | point mort | espérance | PF | P(5 pertes/100) |
|---|---|---|---|---|---|---|
| découverte · Dukascopy 2013-2019 | 39951 | **34.3 %** | 38.3 % | -0.118 R | 0.85 | 99 % |
| SCELLÉ · Dukascopy 2020-2023 | 29362 | **40.3 %** | 34.7 % | +0.165 R | 1.26 | 97 % |
| découverte · Dukascopy 2024-2026 | 19389 | **40.1 %** | 34.1 % | +0.176 R | 1.29 | 97 % |
| découverte · Deriv 2024-2026 | 19346 | **39.8 %** | 34.1 % | +0.169 R | 1.27 | 97 % |
| SCELLÉ · coût relatif au prix | 29893 | **41.2 %** | 33.5 % | +0.227 R | 1.38 | 96 % |
| SCELLÉ · spread d'époque Dukascopy | 27510 | **35.3 %** | 38.6 % | -0.100 R | 0.87 | 99 % |
| Deriv 2024-2026 · coût ×1.5 | 19177 | **39.2 %** | 34.9 % | +0.129 R | 1.20 | 97 % |
| Deriv 2024-2026 · coût ×2.0 | 18943 | **38.6 %** | 35.6 % | +0.088 R | 1.13 | 98 % |
| Deriv 2024-2026 · coût ×3.0 | 18493 | **37.4 %** | 36.9 % | +0.013 R | 1.02 | 98 % |
| Deriv 2024-2026 · coût ×4.0 | 17808 | **36.2 %** | 38.0 % | -0.052 R | 0.93 | 99 % |

**Les trois chiffres de Mongazi, sur le scellé** (29362 trades jamais regardés pendant la recherche) :

1. **2 R réellement atteints : 40.3 %** — l'objectif est « plus de 50 % ». ⛔ **Non atteint.**
2. **R:R réalisé : 1.79** (gain moyen +1.91 R, perte moyenne -1.06 R). ✅
3. **P(5 pertes d'affilée sur 100 trades) : 97 %**, P(6) : 85 %, plus longue série observée : 15. ⛔ **Pas « extrêmement bas ».**

Ce qu'il fait, lui : **+0.165 R par trade**, 613 trades par mois, positif chaque année (2020 +0.16 R, 2021 +0.11 R, 2022 +0.21 R, 2023 +0.17 R) et dans les deux sens (achat +0.17 R, vente +0.16 R).

⚠️ **Sa fragilité tient en un nombre : le spread.** À 70 points chez Deriv (mesuré : 70 points dans 99,8 % des minutes, ouverture et annonces comprises) il gagne ; au spread d'époque de Dukascopy (167 points) il perd. Il survit à un coût **trois fois** supérieur à celui de Deriv, pas quatre.
⚠️ **Il échoue sur 2013-2019 au coût absolu d'aujourd'hui** (70 points sur un indice à 5 000, c'est quatre fois plus cher en proportion) et **réussit au coût relatif** (+0,164 R). Le mécanisme est ancien ; sa rentabilité est récente, et tient au spread.
⛔ **Rien n'est en réel.** Le juge est la démo en observation : un ordre limite servi dans une simulation n'est pas un ordre limite servi par un courtier.

## 2. Le plafond : jusqu'où 2 R peut tomber avant 1 R, dans la journée

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

## 3. Entrer sur un retour de prix (ordre limite)

La géométrie change : depuis un meilleur prix, l'objectif est plus près en valeur absolue. ⛔ Piège mesuré : à 0,5 R de retrait les deux sens sont des miroirs exacts, donc « au moins un des deux gagne » vaut 99 % **par construction**. Seuls comptent les taux par sens, rapportés aux ordres servis.

## 4. Le modèle : ce qu'on sait prévoir, mesuré hors échantillon

Un modèle par sens apprend P(2 R avant 1 R) sur les caractéristiques causales, walk-forward purgé. On lit la précision parmi les minutes où il est le plus sûr : si les 1 % les plus sûres ne dépassent pas le point mort, il n'y a rien à prendre.

- **EURUSD M1 pts50** (mt5 2019-01→2026-09) : taux de base 27.2 %, précision moyenne du 1 % le plus sûr **32.2 %**
  - seuil 0.40 : 7057 trades, objectif atteint 32.3 % (point mort 34.6 %), espérance -0.068 R
  - seuil 0.45 : 2155 trades, objectif atteint 31.6 % (point mort 34.3 %), espérance -0.079 R
  - seuil 0.50 : 835 trades, objectif atteint 32.6 % (point mort 34.0 %), espérance -0.042 R
  - seuil 0.55 : 400 trades, objectif atteint 31.2 % (point mort 34.2 %), espérance -0.087 R
  - seuil 0.60 : 211 trades, objectif atteint 32.7 % (point mort 34.0 %), espérance -0.037 R
- **NAS100 M1 pts1200** (duka 2013-01→2019-12) : taux de base 25.0 %, précision moyenne du 1 % le plus sûr **29.9 %**
  - seuil 0.40 : 6100 trades, objectif atteint 32.2 % (point mort 33.2 %), espérance -0.030 R
  - seuil 0.45 : 4300 trades, objectif atteint 30.7 % (point mort 33.0 %), espérance -0.068 R
  - seuil 0.50 : 3024 trades, objectif atteint 31.1 % (point mort 32.8 %), espérance -0.052 R
  - seuil 0.55 : 2125 trades, objectif atteint 30.4 % (point mort 32.6 %), espérance -0.063 R
  - seuil 0.60 : 1481 trades, objectif atteint 29.3 % (point mort 32.8 %), espérance -0.104 R
- **NAS100 M1 pts1200** (mt5 2024-01→2026-09) : taux de base 32.1 %, précision moyenne du 1 % le plus sûr **30.0 %**
  - seuil 0.40 : 14319 trades, objectif atteint 32.7 % (point mort 34.3 %), espérance -0.048 R
  - seuil 0.45 : 5496 trades, objectif atteint 32.9 % (point mort 34.2 %), espérance -0.041 R
  - seuil 0.50 : 2531 trades, objectif atteint 32.4 % (point mort 34.3 %), espérance -0.056 R
  - seuil 0.55 : 1206 trades, objectif atteint 33.1 % (point mort 34.4 %), espérance -0.039 R
  - seuil 0.60 : 580 trades, objectif atteint 31.6 % (point mort 34.1 %), espérance -0.075 R

## 5. La recherche exhaustive de règles

Toutes les paires de conditions (puis les meilleurs triplets) sont essayées sur la période d'apprentissage, puis rejouées après la coupe et passées au simulateur. **Le nombre d'essais est publié** : c'est lui qui décide de ce qu'on a le droit de croire.

**EURUSD M1 pts50** · 58806 règles essayées

| règle | sens | apprentissage | validation | trades | 2 R atteints |
|---|---|---|---|---|---|
| dist_bas_veille<=2.71413 ET dist_haut_jour<=4.81832 ET jour_semaine<=2 | achat | 40.6 % (n=4940) | 39.6 % (n=1335) | 152 | 30.9 % |
| barres_depuis_ouverture<=88 ET dist_bas_veille<=2.71413 | achat | 35.5 % (n=16971) | 36.3 % (n=6701) | 443 | 32.7 % |
| dist_bas_veille<=2.71413 ET minute_ny<=208 | achat | 35.5 % (n=16971) | 36.3 % (n=6701) | 443 | 32.7 % |
| dist_bas_veille<=2.71413 ET dist_haut_jour<=4.81832 | achat | 37.5 % (n=7228) | 36.1 % (n=2625) | 266 | 34.6 % |
| barres_depuis_ouverture<=88 ET dist_bas_veille<=2.71413 ET atr14_points>11.6955 | achat | 36.8 % (n=14695) | 35.2 % (n=5584) | 426 | 32.9 % |
| barres_depuis_ouverture<=88 ET dist_bas_veille<=2.71413 ET cout_R_atr14x2<=0.213758 | achat | 36.8 % (n=14695) | 35.2 % (n=5584) | 426 | 32.9 % |
| dist_bas_veille<=2.71413 ET minute_ny<=208 ET atr14_points>11.6955 | achat | 36.8 % (n=14695) | 35.2 % (n=5584) | 426 | 32.9 % |
| dist_bas_veille<=2.71413 ET minute_ny<=208 ET cout_R_atr14x2<=0.213758 | achat | 36.8 % (n=14695) | 35.2 % (n=5584) | 426 | 32.9 % |

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

## 6. Le registre

- **389 tests comptés** (témoins exclus), correction de Holm à 5 % sur le registre entier.
- **16 survivant(s).**

Les plus hauts taux de 2 R atteints, sur au moins 100 trades :

| test | trades | 2 R atteints | point mort | espérance | p |
|---|---|---|---|---|---|
| candidat_rabais_SCELLÉ · coût relatif au pri | 29893 | **41.2 %** | 33.5 % | +0.227 R | 0.000 |
| t6_rabais_EURUSD_M1_mt52019 | 29173 | **41.0 %** | 37.6 % | +0.101 R | 0.000 |
| t7_rabais_EURUSD_M1_mt52019 | 29173 | **41.0 %** | 37.6 % | +0.101 R | 0.000 |
| t6_rabais_NAS100_M1_mt52024 | 9560 | **40.9 %** | 34.2 % | +0.199 R | 0.000 |
| t7_rabais_NAS100_M1_mt52024 | 9560 | **40.9 %** | 34.2 % | +0.199 R | 0.000 |
| candidat_rabais_SCELLÉ · Dukascopy 2020-2023 | 29362 | **40.3 %** | 34.7 % | +0.165 R | 0.000 |
| t6_rabais_NAS100_M1_duka2013 | 25786 | **40.1 %** | 39.9 % | +0.006 R | 0.240 |
| t7_rabais_NAS100_M1_duka2013 | 25786 | **40.1 %** | 39.9 % | +0.006 R | 0.240 |
| candidat_rabais_découverte · Dukascopy 2024- | 19389 | **40.1 %** | 34.1 % | +0.176 R | 0.000 |
| candidat_rabais_découverte · Deriv 2024-2026 | 19346 | **39.8 %** | 34.1 % | +0.169 R | 0.000 |


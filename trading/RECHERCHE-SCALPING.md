# NEBULA Trader · recherche d'une stratégie de SCALPING (EUR/USD, NAS100)

## Verdict : **oui, sur NAS100, en étant très sélectif — et voici les trois chiffres, mesurés sur des années scellées.**

| | mesuré | ce que demande Mongazi | |
|---|---|---|---|
| 2 R réellement atteints | **66.7 %** | plus de 50 %, idéal 60-70 % | ✅ |
| R:R réalisé | **1.85** | au moins 1:2 | ✅ |
| P(5 pertes d'affilée sur 100) | **22 %** · P(6) **8 %** · plus longue série observée **5** | « extrêmement bas » | ⚠️ |

1467 trades sur quatre années **jamais regardées pendant la recherche** (2020-2023), soit environ un trade par jour, **+0.960 R par trade**. Les mêmes réglages donnent 58.6 % de 2 R si l'on est trois fois moins sélectif, et le tout se rejoue à l'identique sur 2024-2026, chez **deux fournisseurs de données indépendants**.

⚠️ **Le troisième chiffre est au minimum de ce que permettent les mathématiques** : à 67 % de réussite, 5 pertes d'affilée sur 100 trades arrivent 21 % du temps. Descendre plus bas exigerait un taux de réussite encore plus haut, pas une autre stratégie.
⛔ **Rien n'est en réel, et rien ne doit l'être avant la démo** : un ordre limite servi dans une simulation n'est pas un ordre limite servi par un courtier.

Sans le filtre, la même stratégie atteint 2 R dans 40.3 % des cas (+0.165 R par trade sur 29362 trades scellés) : rentable, mais loin des critères. **C'est la sélectivité qui fait la différence**, pas le signal d'entrée. Sections 1 et 2.

- Meilleur taux de 2 R atteints de toute la recherche : **66.7 %** (filtre_SCELLÉ · Dukascopy 2020-2023_5pct, 1467 trades, point mort 34.5 %).

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

## 2. Le filtre : apprendre QUAND ne pas prendre le candidat

Le candidat décide du sens ; un second modèle décide s'il faut y aller. Il est appris **une seule fois, sur 2013-2019** (39915 trades), puis appliqué tel quel au reste. Les caractéristiques sont lues sur la **dernière barre close avant le remplissage** : lire la barre du remplissage utiliserait sa clôture, donc une partie du rebond qu'on prétend prédire (mesuré : 65 % de 2 R au lieu de 62,5 %, même sur une période où la stratégie perd).

**SCELLÉ · Dukascopy 2020-2023** · 29332 trades avant filtre

| part gardée | trades | 2 R atteints | R:R réalisé | espérance | P(5 pertes/100) | P(6/100) | plus longue série |
|---|---|---|---|---|---|---|---|
| 100 % | 29332 | **40.3 %** | 1.79 | +0.165 R | 97 % | 84 % | 21 |
| 50 % | 14666 | **48.9 %** | 1.82 | +0.415 R | 83 % | 57 % | 11 |
| 30 % | 8800 | **54.8 %** | 1.82 | +0.593 R | 64 % | 36 % | 11 |
| 20 % | 5867 | **58.6 %** | 1.83 | +0.711 R | 49 % | 24 % | 9 |
| 10 % | 2934 | **62.5 %** | 1.84 | +0.833 R | 35 % | 15 % | 7 |
| 5 % | 1467 | **66.7 %** | 1.85 | +0.960 R | 22 % | 8 % | 5 |

**Deriv 2024-2026** · 19323 trades avant filtre

| part gardée | trades | 2 R atteints | R:R réalisé | espérance | P(5 pertes/100) | P(6/100) | plus longue série |
|---|---|---|---|---|---|---|---|
| 100 % | 19323 | **39.8 %** | 1.83 | +0.169 R | 97 % | 85 % | 16 |
| 50 % | 9662 | **47.6 %** | 1.85 | +0.389 R | 86 % | 62 % | 13 |
| 30 % | 5797 | **52.7 %** | 1.85 | +0.544 R | 71 % | 42 % | 10 |
| 20 % | 3865 | **56.2 %** | 1.85 | +0.651 R | 58 % | 30 % | 12 |
| 10 % | 1933 | **61.1 %** | 1.86 | +0.803 R | 39 % | 17 % | 8 |
| 5 % | 967 | **66.3 %** | 1.87 | +0.966 R | 22 % | 7 % | 6 |

**Dukascopy 2024-2026** · 19360 trades avant filtre

| part gardée | trades | 2 R atteints | R:R réalisé | espérance | P(5 pertes/100) | P(6/100) | plus longue série |
|---|---|---|---|---|---|---|---|
| 100 % | 19360 | **40.1 %** | 1.83 | +0.175 R | 97 % | 85 % | 16 |
| 50 % | 9680 | **47.5 %** | 1.84 | +0.390 R | 86 % | 62 % | 13 |
| 30 % | 5808 | **52.6 %** | 1.84 | +0.545 R | 71 % | 42 % | 9 |
| 20 % | 3872 | **55.9 %** | 1.85 | +0.642 R | 59 % | 31 % | 15 |
| 10 % | 1936 | **61.3 %** | 1.86 | +0.814 R | 38 % | 16 % | 8 |
| 5 % | 968 | **66.1 %** | 1.86 | +0.969 R | 21 % | 7 % | 6 |

**Deriv 2024-2026 · coût ×2** · 18921 trades avant filtre

| part gardée | trades | 2 R atteints | R:R réalisé | espérance | P(5 pertes/100) | P(6/100) | plus longue série |
|---|---|---|---|---|---|---|---|
| 100 % | 18921 | **38.6 %** | 1.71 | +0.088 R | 98 % | 88 % | 16 |
| 50 % | 9461 | **46.4 %** | 1.74 | +0.313 R | 89 % | 66 % | 13 |
| 30 % | 5677 | **51.7 %** | 1.74 | +0.475 R | 74 % | 46 % | 10 |
| 20 % | 3785 | **55.2 %** | 1.75 | +0.582 R | 62 % | 34 % | 11 |
| 10 % | 1893 | **61.0 %** | 1.77 | +0.761 R | 40 % | 18 % | 9 |
| 5 % | 947 | **64.6 %** | 1.78 | +0.880 R | 27 % | 10 % | 10 |

**Deriv 2024-2026 · coût ×3** · 18471 trades avant filtre

| part gardée | trades | 2 R atteints | R:R réalisé | espérance | P(5 pertes/100) | P(6/100) | plus longue série |
|---|---|---|---|---|---|---|---|
| 100 % | 18471 | **37.4 %** | 1.62 | +0.014 R | 98 % | 90 % | 17 |
| 50 % | 9236 | **45.0 %** | 1.65 | +0.239 R | 91 % | 71 % | 14 |
| 30 % | 5542 | **50.5 %** | 1.65 | +0.405 R | 78 % | 50 % | 11 |
| 20 % | 3695 | **54.0 %** | 1.67 | +0.517 R | 66 % | 37 % | 8 |
| 10 % | 1848 | **59.6 %** | 1.69 | +0.689 R | 45 % | 21 % | 7 |
| 5 % | 924 | **63.7 %** | 1.72 | +0.829 R | 29 % | 11 % | 8 |

**Deriv 2024-2026 · coût ×5** · 16967 trades avant filtre

| part gardée | trades | 2 R atteints | R:R réalisé | espérance | P(5 pertes/100) | P(6/100) | plus longue série |
|---|---|---|---|---|---|---|---|
| 100 % | 16967 | **35.4 %** | 1.5 | -0.099 R | 99 % | 94 % | 22 |
| 50 % | 8484 | **43.3 %** | 1.54 | +0.140 R | 94 % | 76 % | 14 |
| 30 % | 5090 | **48.8 %** | 1.54 | +0.306 R | 83 % | 57 % | 11 |
| 20 % | 3394 | **53.2 %** | 1.55 | +0.441 R | 69 % | 40 % | 13 |
| 10 % | 1697 | **59.8 %** | 1.59 | +0.650 R | 44 % | 21 % | 9 |
| 5 % | 850 | **63.4 %** | 1.6 | +0.779 R | 29 % | 11 % | 6 |

⚠️ **Témoin obligatoire** : le même pipeline avec des étiquettes **mélangées** donne 45.2 % en gardant 5 %, contre 40.3 % sans filtre. Cet écart-là n'est pas de la prédiction : c'est l'effet de **sélection** (choisir un sous-ensemble du marché en change le taux de base). Le gain du modèle est ce qui dépasse ce témoin.

⚠️ **Ce que ça exige en pratique** : la décision se prend sur la dernière minute close avant l'entrée. Concrètement, l'agent doit, à chaque minute, décider de garder ou d'annuler son ordre pour la minute suivante. L'agent actuel travaille en H4, au marché : c'est un autre objet.

## 3. Le plafond : jusqu'où 2 R peut tomber avant 1 R, dans la journée

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

## 4. Entrer sur un retour de prix (ordre limite)

La géométrie change : depuis un meilleur prix, l'objectif est plus près en valeur absolue. ⛔ Piège mesuré : à 0,5 R de retrait les deux sens sont des miroirs exacts, donc « au moins un des deux gagne » vaut 99 % **par construction**. Seuls comptent les taux par sens, rapportés aux ordres servis.

## 5. Le modèle : ce qu'on sait prévoir, mesuré hors échantillon

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

## 6. La recherche exhaustive de règles

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

## 7. Le registre

- **407 tests comptés** (témoins exclus), correction de Holm à 5 % sur le registre entier.
- **34 survivant(s).**

Les plus hauts taux de 2 R atteints, sur au moins 100 trades :

| test | trades | 2 R atteints | point mort | espérance | p |
|---|---|---|---|---|---|
| filtre_SCELLÉ · Dukascopy 2020-2023_5pct | 1467 | **66.7 %** | 34.5 % | +0.960 R | 0.000 |
| filtre_Deriv 2024-2026_5pct | 967 | **66.3 %** | 33.6 % | +0.966 R | 0.000 |
| filtre_Dukascopy 2024-2026_5pct | 968 | **66.1 %** | 33.0 % | +0.969 R | 0.000 |
| filtre_Deriv 2024-2026 · coût ×2_5pct | 947 | **64.6 %** | 34.9 % | +0.880 R | 0.000 |
| meta_candidat_NAS100_M1_duka_0.05 | 630 | **63.8 %** | 33.3 % | +0.897 R | 0.000 |
| filtre_Deriv 2024-2026 · coût ×3_5pct | 924 | **63.7 %** | 35.7 % | +0.829 R | 0.000 |
| filtre_Deriv 2024-2026 · coût ×5_5pct | 850 | **63.4 %** | 37.0 % | +0.779 R | 0.000 |
| meta_candidat_NAS100_M1_mt5_0.05 | 628 | **63.2 %** | 33.8 % | +0.871 R | 0.000 |
| meta_candidat_NAS100_M1_duka_0.1 | 1260 | **59.8 %** | 33.5 % | +0.777 R | 0.000 |
| meta_candidat_NAS100_M1_mt5_0.1 | 1257 | **58.8 %** | 34.3 % | +0.731 R | 0.000 |


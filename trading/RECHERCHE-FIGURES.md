# NEBULA Trader · figures chartistes : ETE, ETE inversé, biseaux, avec RSI et EMA 50

*Demande de Mongazi du 2026-09-17. Généré par `python -m trading.recherche.figures_lancer` puis `python -m trading.recherche.figures_rapport` : aucun chiffre recopié à la main. Définitions mécaniques fixées avant le premier résultat : `trading/recherche/figures.py`.*

## Verdict : NON. Aucune figure, avec ou sans RSI et EMA 50, n'approche tes critères, et aucune ne se distingue du hasard.

- **192 versions testées** (4 figures × 4 filtres × 2 stops × H1, H4, D1 × EUR/USD et NAS100), objectif 2 R, coûts Deriv. **166** ont au moins un trade et entrent au registre, qui compte désormais **312 tests** ; **0** résistent à la correction de Holm.
- Versions avec **plus de 50 % de réussite, au moins 100 trades et une espérance positive : 0**.
- Versions à espérance positive sur au moins 30 trades : 18 sur 40, soit à peu près la moitié : ce qu'on attend du hasard.

## 1. Tes chiffres, figure par figure (EUR/USD, sans filtre, stop proche)

| Figure | Unité | Trades | Gagnants | Objectif 2 R atteint | R:R réalisé | P(5 pertes d'affilée sur 100) | Plus longue série perdante | Espérance | p |
|---|---|---|---|---|---|---|---|---|---|
| Épaule-tête-épaule | H1 | 233 | **32,2 %** | 27,9 % | 1:1,86 | 100 % | 10 | **-0,078 R** | 0,81 |
| Épaule-tête-épaule | H4 | 89 | **42,7 %** | 33,7 % | 1:1,76 | 95 % | 8 | **+0,175 R** | 0,12 |
| Épaule-tête-épaule | D1 | 22 | **59,1 %** | 18,2 % | 1:1,52 | 49 % | 3 | **+0,379 R** | 0,06 |
| ETE inversé | H1 | 208 | **36,5 %** | 30,8 % | 1:1,69 | 99 % | 9 | **-0,018 R** | 0,58 |
| ETE inversé | H4 | 94 | **29,8 %** | 17,0 % | 1:1,40 | 100 % | 10 | **-0,288 R** | 0,99 |
| ETE inversé | D1 | 25 | **48,0 %** | 24,0 % | 1:1,24 | 87 % | 3 | **+0,075 R** | 0,39 |
| Biseau ascendant | H1 | 140 | **36,4 %** | 36,4 % | 1:1,98 | 99 % | 12 | **+0,086 R** | 0,24 |
| Biseau ascendant | H4 | 53 | **24,5 %** | 22,6 % | 1:1,94 | 100 % | 16 | **-0,277 R** | 0,94 |
| Biseau ascendant | D1 | 12 | **41,7 %** | 33,3 % | 1:1,75 | 96 % | 5 | **+0,143 R** | 0,37 |
| Biseau descendant | H1 | 136 | **27,9 %** | 26,5 % | 1:1,84 | 100 % | 15 | **-0,213 R** | 0,97 |
| Biseau descendant | H4 | 63 | **31,7 %** | 27,0 % | 1:1,73 | 100 % | 6 | **-0,139 R** | 0,79 |
| Biseau descendant | D1 | 13 | **7,7 %** | 7,7 % | 1:1,73 | 100 % | 7 | **-0,844 R** | 1,00 |

- ⚠️ **Épaule-tête-épaule en D1 dépasse 50 % (59,1 %), mais sur 22 trades** : l'intervalle de confiance va de 39 % à 77 %, et seulement 4 trades atteignent l'objectif de 2 R ; les autres gagnants sortent par le temps avec un petit gain (R:R réalisé 1:1,52). Ce n'est pas le 50 % à 1:2 que tu cherches.

**Comparaison avec Bulkowski** (actions, sortie au meilleur prix, sans stop ni coûts) :

| Figure | Bulkowski : objectif atteint | Bulkowski : échec | Ici : gagnants, toutes versions EUR/USD | Ici : espérance moyenne |
|---|---|---|---|---|
| Épaule-tête-épaule | 51 % | 19 % | 39,1 % | +0,006 R |
| ETE inversé | 71 % | 11 % | 38,4 % | -0,058 R |
| Biseau ascendant | 32 % | 51 % | 35,0 % | +0,017 R |
| Biseau descendant | 62 % | 26 % | 30,7 % | -0,160 R |

Avec un vrai stop et un objectif à 2 R, **la meilleure figure fait 39,1 % de gagnants en moyenne** (toutes versions EUR/USD confondues), et la meilleure espérance moyenne est de +0,017 R. Les « objectifs atteints » de Bulkowski supposent une sortie au meilleur prix, sans stop : on ne les retrouve pas.

## 2. Ce que le RSI et l'EMA 50 ajoutent vraiment

Chaque version filtrée comparée à la même figure, même stop, même marché, même unité, sans filtre (paires où les deux ont au moins 20 trades) :

| Filtre | Paires comparées | Gain moyen de réussite | Gain moyen d'espérance | Paires améliorées | Trades gardés |
|---|---|---|---|---|---|
| divergence RSI | 14 | +0,0 points | -0,007 R | 7 sur 14 | 31 % |
| EMA 50 | 14 | +2,3 points | +0,025 R | 7 sur 14 | 59 % |
| RSI + EMA 50 | 4 | +5,1 points | +0,087 R | 4 sur 4 | 20 % |

- **Stop loin (tête / haut du biseau) au lieu de proche** : +2,5 points de réussite, -0,019 R d'espérance en moyenne (27 paires). Plus de trades gagnants, mais des gains plus petits en dollars pour le même risque.
- **Lecture** : un filtre retire des trades. S'il retirait surtout les perdants, l'espérance monterait nettement et régulièrement ; ici elle bouge de quelques centièmes de R, dans un sens ou dans l'autre selon la paire. Le filtre le plus sévère (RSI + EMA 50) ne se compare que sur les rares paires qui gardent 20 trades : ce sont les échantillons les plus petits, donc les plus trompeurs.

## 3. Les 12 meilleures versions (au moins 30 trades, classées par p)

| Version | Trades | Gagnants | Espérance | p | Coûts ×1,5 | 80 % anciens | 20 % récents | Correction |
|---|---|---|---|---|---|---|---|---|
| Biseau ascendant, divergence RSI, stop proche · EURUSD H1 | 41 | 46,3 % | +0,382 R | 0,053 | +0,375 R | 34 tr, +0,229 R | 7 tr, +1,127 R | non |
| Épaule-tête-épaule, sans filtre, stop proche · EURUSD H4 | 89 | 42,7 % | +0,175 R | 0,119 | +0,173 R | 78 tr, +0,163 R | 11 tr, +0,259 R | non |
| Biseau ascendant, EMA 50, stop loin · EURUSD H1 | 30 | 43,3 % | +0,302 R | 0,138 | +0,297 R | 24 tr, +0,376 R | 6 tr, +0,005 R | non |
| ETE inversé, RSI + EMA 50, stop proche · EURUSD H1 | 41 | 43,9 % | +0,201 R | 0,189 | +0,126 R | 33 tr, +0,294 R | 8 tr, -0,179 R | non |
| Épaule-tête-épaule, sans filtre, stop loin · EURUSD H4 | 88 | 44,3 % | +0,109 R | 0,201 | +0,108 R | 77 tr, +0,110 R | 11 tr, +0,106 R | non |
| Biseau ascendant, EMA 50, stop proche · EURUSD H1 | 30 | 40,0 % | +0,199 R | 0,234 | +0,192 R | 24 tr, +0,245 R | 6 tr, +0,012 R | non |
| Biseau ascendant, sans filtre, stop proche · EURUSD H1 | 140 | 36,4 % | +0,086 R | 0,240 | +0,079 R | 119 tr, -0,023 R | 21 tr, +0,707 R | non |
| Biseau descendant, divergence RSI, stop proche · EURUSD H1 | 44 | 40,9 % | +0,138 R | 0,263 | +0,130 R | 34 tr, +0,216 R | 10 tr, -0,130 R | non |
| ETE inversé, divergence RSI, stop loin · EURUSD H1 | 58 | 43,1 % | +0,094 R | 0,298 | +0,091 R | 48 tr, +0,155 R | 10 tr, -0,200 R | non |
| Épaule-tête-épaule, EMA 50, stop loin · EURUSD H4 | 63 | 44,4 % | +0,075 R | 0,305 | +0,073 R | 56 tr, +0,070 R | 7 tr, +0,111 R | non |
| Biseau ascendant, divergence RSI, stop loin · EURUSD H1 | 39 | 35,9 % | +0,076 R | 0,372 | +0,071 R | 32 tr, -0,062 R | 7 tr, +0,705 R | non |
| Épaule-tête-épaule, divergence RSI, stop loin · EURUSD H1 | 68 | 42,6 % | +0,050 R | 0,375 | +0,048 R | 60 tr, +0,064 R | 8 tr, -0,052 R | non |

- Même la meilleure (p = 0,053 sur 41 trades) ne résiste pas à la correction : avec 312 tests au registre, la première marche de Holm exige p < 0,00016. Sur 192 versions, en trouver une vers 0,05 est ce que produit le hasard.
- Stabilité dans le temps : parmi ces 12, 2 perdaient sur les 80 % anciens et ne gagnent que sur les 20 % récents, et 4 gagnaient avant et perdent sur les 20 % récents.

## 4. NAS100 : trop peu de figures pour conclure

| Figure | H1 | H4 | D1 |
|---|---|---|---|
| Épaule-tête-épaule | 17 trades, +0,063 R | 11 trades, -0,713 R | 1 trade, -0,977 R |
| ETE inversé | 9 trades, -0,345 R | 8 trades, -0,291 R | 1 trade, +1,685 R |
| Biseau ascendant | 27 trades, -0,113 R | 12 trades, +0,011 R | 1 trade, -0,953 R |
| Biseau descendant | 14 trades, +0,037 R | 2 trades, +0,406 R | 0 trade |

L'historique Deriv du NAS100 commence en janvier 2024 : 2 ans et demi ne contiennent que quelques dizaines de figures. Rien ne peut être conclu, dans un sens ou dans l'autre.

## 5. Les 10 000 $ (1 % de risque par trade)

| Version | Règles | Trades | Capital final | Résultat | Par an | Drawdown max | Gagnants | Pire série |
|---|---|---|---|---|---|---|---|---|
| Épaule-tête-épaule, sans filtre, stop proche · EURUSD H4 | vidéo | 89 | 11 550 $ | **1 550 $ (+15,5 %)** | +0,7 % | 9,2 % | 42,7 % | 8 |
| Épaule-tête-épaule, sans filtre, stop proche · EURUSD H4 | NEBULA PRO | 76 | 11 646 $ | **1 646 $ (+16,5 %)** | +0,7 % | 6,2 % | 43,4 % | 7 |
| ETE inversé, sans filtre, stop proche · EURUSD H4 | vidéo | 94 | 7 728 $ | **-2 272 $ (-22,7 %)** | -1,2 % | 22,7 % | 29,8 % | 10 |
| ETE inversé, sans filtre, stop proche · EURUSD H4 | NEBULA PRO | 72 | 8 230 $ | **-1 770 $ (-17,7 %)** | -0,9 % | 17,7 % | 29,2 % | 7 |
| Biseau ascendant, sans filtre, stop proche · EURUSD H4 | vidéo | 53 | 8 627 $ | **-1 373 $ (-13,7 %)** | -0,7 % | 17,0 % | 24,5 % | 16 |
| Biseau ascendant, sans filtre, stop proche · EURUSD H4 | NEBULA PRO | 37 | 9 503 $ | **-497 $ (-5,0 %)** | -0,2 % | 7,5 % | 27,0 % | 10 |
| Biseau descendant, sans filtre, stop proche · EURUSD H4 | vidéo | 63 | 9 150 $ | **-850 $ (-8,5 %)** | -0,4 % | 11,0 % | 31,8 % | 6 |
| Biseau descendant, sans filtre, stop proche · EURUSD H4 | NEBULA PRO | 57 | 9 324 $ | **-676 $ (-6,8 %)** | -0,3 % | 9,4 % | 31,6 % | 6 |
| Biseau ascendant, divergence RSI, stop proche · EURUSD H1 ⚠️ choisie après coup | vidéo | 41 | 11 616 $ | **1 616 $ (+16,2 %)** | +0,7 % | 3,9 % | 46,3 % | 4 |
| Biseau ascendant, divergence RSI, stop proche · EURUSD H1 ⚠️ choisie après coup | NEBULA PRO | 25 | 10 516 $ | **516 $ (+5,2 %)** | +0,3 % | 3,1 % | 44,0 % | 4 |

- **Figures gagnantes sans filtre en H4 : Épaule-tête-épaule.** L'ETE transforme 10 000 $ en 11 550 $ en 21 ans : **+0,7 % par an**, sur 89 trades (environ 4 par an). Même si c'était un vrai avantage, ce serait moins qu'un livret.
- **La « meilleure version » est choisie après avoir vu les résultats** : son chiffre est le plus optimiste possible, et c'est pour ça qu'il est marqué.

## 6. Comment les figures ont été reconnues, et ce que ça ne voit pas

- **Pivots** : extrême de 7 bougies, séquence alternée sommet/creux. **ETE** : tête au-dessus des épaules, hauteur d'au moins 2 ATR, épaules comparables, ligne de cou peu penchée, cassure à la clôture. **Biseaux** : 5 pivots, deux lignes dans le même sens qui convergent, cassure à la clôture avant la pointe.
- **Regardé sur des planches** avant de lire les résultats : les figures détectées ressemblent à des figures. Deux constats : certains ETE « de sommet » se forment après une forte baisse (continuation plutôt que retournement), et certains biseaux ascendants ont une ligne haute presque plate (proches d'un triangle).
- **Corrigé avant tout tableau** : dans un biseau, le stop « proche » tombait au même prix que le « loin » ; il est devenu l'extrême des 4 dernières bougies.
- **Contrôles** : figures dessinées à la main reconnues, témoins rejetés, aucune lecture du futur (deux fuites injectées exprès sont attrapées).
- **Limite** : un trader humain ne trace pas ses lignes comme ce code. Une autre définition donnerait d'autres chiffres ; mais pour qu'une figure soit un avantage réel, il faudrait qu'elle gagne sous une définition raisonnable, et aucune des 192 versions ne le montre.

## 7. Conseils

1. **Ne pas trader ces figures comme un système** : elles ne font pas mieux que le hasard une fois le stop et les coûts posés.
2. **Le RSI et l'EMA 50 ne changent pas la nature du résultat** : ils retirent des trades, pas des pertes.
3. **Ton critère (plus de 50 % à 1:2 sur au moins 100 trades) n'est atteint par aucun des 312 tests du registre.** Le chercher dans des figures ou des indicateurs publics, c'est chercher ce que des milliers de gens ont déjà arbitré.

## Sources

- Bulkowski, épaule-tête-épaule : https://thepatternsite.com/hst.html · inversé : https://thepatternsite.com/hsb.html
- Bulkowski, biseaux ascendants : https://thepatternsite.com/risewedge.html · descendants : https://thepatternsite.com/fallwedge.html
- Chang et Osler, « Methodical Madness », Economic Journal 1999 : https://onlinelibrary.wiley.com/doi/abs/10.1111/1468-0297.00466

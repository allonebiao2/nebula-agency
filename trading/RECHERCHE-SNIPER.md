# NEBULA Trader · « My Secret 1 Minute Scalping Strategy (Sniper Entry) »

*Vidéo de Mulham Trading (Edge Skool) envoyée par Mongazi le 2026-09-17. Généré par `python -m trading.recherche.sniper_rapport` depuis `trading/rapports/recherche/sniper/` : aucun chiffre recopié à la main. Fiche de la méthode : `trading/recherche/METHODE-SNIPER.md`.*

## Verdict : NON. La méthode ne gagne pas, ni sur EUR/USD ni sur NAS100, et elle est très loin de tes critères.

Tes trois chiffres d'abord (règles de la vidéo + filtre des annonces de l'agent, coûts Deriv réels) :

| | Ton critère | EUR/USD (2019-2026) | NAS100 (2024-2026) |
|---|---|---|---|
| Trades gagnants | plus de 50 % (idéal 60-70 %) | **23,8 %** | **24,7 %** |
| Objectif de 3 R réellement atteint | | 21,1 % | 22,1 % |
| R:R réalisé (gain moyen / perte moyenne) | au moins 1:2 | 1:2,74 | 1:2,75 |
| Probabilité de 5 pertes d'affilée sur 100 trades | extrêmement basse | **100 %** | **100 %** |
| Probabilité de 6 pertes d'affilée sur 100 trades | extrêmement basse | **100 %** | **100 %** |
| Plus longue série perdante observée | | 28 trades | 17 trades |
| Espérance par trade | positive | **-0,113 R** | **-0,075 R** |
| Trades | au moins 100 | 2941 | 1070 |

- **Même sans AUCUN coût** (ni spread, ni glissement), la méthode fait **-0,020 R** par trade sur EUR/USD (25,4 % de gagnants, p = 0,74) et **+0,015 R** sur NAS100 (p = 0,39). Aucun des deux ne se distingue du hasard : il n'y a pas d'avantage à protéger. Le courtier prend ensuite environ **0,09 R** par trade sur EUR/USD et **0,09 R** sur NAS100.
- À un objectif de 3 R, l'équilibre est à **25 %** de réussite avant coûts. La méthode en fait 25,4 % sur EUR/USD et 26,7 % sur NAS100 avant coûts : à peu près ce qu'on obtient en entrant au hasard avec un stop et un objectif de ces tailles.
- **Les exemples de la vidéo sont vrais** (retrouvés au dixième de pip, et gagnants) : ils sont choisis. Du 27 octobre au 7 novembre 2025, les mêmes règles ont pris **17 trades** ; hors des 3 montrés, il y en a 14, dont **11 perdants** (somme -2,3 R).

## 1. Les 10 000 $

Tailles de position réelles (lots arrondis vers le bas, lot minimum et maximum du courtier), résultat net de spread, glissement et swap. **« Vidéo »** = risque fixe par trade, aucun frein, comme l'auteur. **« NEBULA PRO »** = les verrous de ton agent (levier ×3, 0,50 lot au plus, 3 trades/jour, 8/semaine, 4 h d'attente après une perte, -3 %/jour, -6 %/semaine, -10 %/mois, arrêt total à -20 %).

| Compte (1 % par trade) | Capital final | Bénéfice | En % | Par an | Drawdown max | Trades | Gagnants | Gain moyen / perte moyenne | Pire série | Mois positifs |
|---|---|---|---|---|---|---|---|---|---|---|
| EUR/USD 2019-2026, vidéo | 273 $ | **-9 727 $** | **-97,3 %** | -37,4 % | 97,4 % (10 320 $) | 2940 | 23,8 % | 79 $ / -29 $ | 28 | 29 % |
| EUR/USD 2019-2026, NEBULA PRO | 7 970 $ | **-2 030 $** | **-20,3 %** | -6,6 % | 20,3 % (2 030 $) | 680 | 22,7 % | 37 $ / -15 $ | 24 | 29 % |
| NAS100 2024-2026, vidéo | 4 015 $ | **-5 985 $** | **-59,9 %** | -29,3 % | 69,0 % (8 758 $) | 1070 | 24,7 % | 216 $ / -78 $ | 17 | 27 % |
| NAS100 2024-2026, NEBULA PRO | 9 557 $ | **-443 $** | **-4,4 %** | -1,7 % | 9,7 % (987 $) | 523 | 24,3 % | 41 $ / -14 $ | 26 | 33 % |
| Les deux, 2024-2026, vidéo | 1 080 $ | **-8 920 $** | **-89,2 %** | -56,9 % | 90,9 % (10 754 $) | 2107 | 24,1 % | 115 $ / -42 $ | 20 | 30 % |
| Les deux, 2024-2026, NEBULA PRO | 9 345 $ | **-655 $** | **-6,6 %** | -2,5 % | 12,9 % (1 331 $) | 831 | 25,0 % | 40 $ / -14 $ | 18 | 48 % |

Selon le risque par trade, règles de la vidéo :

| Risque par trade | EUR/USD 2019-2026 | NAS100 2024-2026 | Les deux 2024-2026 |
|---|---|---|---|
| 0,5 % | 1 756 $ (-82 %, drawdown 83 %) | 6 496 $ (-35 %, drawdown 43 %) | 3 455 $ (-65 %, drawdown 68 %) |
| 1 % | 273 $ (-97 %, drawdown 97 %) | 4 015 $ (-60 %, drawdown 69 %) | 1 080 $ (-89 %, drawdown 91 %) |
| 2 % | 11 $ (-100 %, drawdown 100 %) | 1 223 $ (-88 %, drawdown 93 %) | 103 $ (-99 %, drawdown 99 %) |
| 3 % | 7 $ (-100 %, drawdown 100 %) | 299 $ (-97 %, drawdown 99 %) | 16 $ (-100 %, drawdown 100 %) |

- ⚠️ **En NEBULA PRO, le risque choisi ne change presque rien** : le levier ×3 et le plafond de 0,50 lot ramènent le risque réel à **0,17 %** par trade en moyenne sur EUR/USD (le stop médian de 4,6 pips demande 2,2 lots à 1 % de 10 000 $, soit un levier de ×24). Les freins limitent la casse, ils ne créent pas de gain. Arrêt total le 2022-05-13 : -20,3 % depuis le sommet de 10 000 $.
- Trades refusés par les verrous PRO sur EUR/USD : arrêt total 1624, Asie creuse 371, attente après une perte 193, pause après série perdante 71, 3 trades par jour 2.

EUR/USD, règles de la vidéo à 1 %, année par année :

| Année | Résultat | En % | Capital en fin d'année |
|---|---|---|---|
| 2019 | -4 693 $ | -46,9 % | 5 307 $ |
| 2020 | -650 $ | -12,2 % | 4 657 $ |
| 2021 | -1 246 $ | -26,8 % | 3 411 $ |
| 2022 | -1 547 $ | -45,4 % | 1 864 $ |
| 2023 | -885 $ | -47,5 % | 979 $ |
| 2024 | -535 $ | -54,6 % | 444 $ |
| 2025 | -104 $ | -23,4 % | 340 $ |
| 2026 | -67 $ | -19,7 % | 273 $ |

Meilleur mois +22,5 %, pire mois -19,7 %, plus gros gain 308 $, plus grosse perte -107 $, 31,8 trades par mois.

**Et l'année prochaine ?** Si les trades à venir ressemblaient aux trades passés (10 000 tirages, 1 % par trade) :

| Marché | Trades en 1 an | Capital médian | 1 fois sur 10 sous | 1 fois sur 10 au-dessus de | Chance de finir gagnant | Chance de toucher -20 % | Chance de toucher -50 % |
|---|---|---|---|---|---|---|---|
| EURUSD | 382 | 6 177 $ | 4 131 $ | 9 367 $ | 7 % | 90 % | 33 % |
| NAS100 | 406 | 6 940 $ | 4 594 $ | 10 787 $ | 14 % | 83 % | 22 % |

## 2. La méthode (maîtrisée, règle par règle)

| # | Règle | Moment de la vidéo |
|---|---|---|
| 1 | Unité principale **M15**, entrée en **M1** : « attraper les balayages de liquidité M15 avec le graphique M1 » | [09:25] |
| 2 | Direction : **EMA 200** (entourée à l'écran). Au-dessus = achats, en dessous = ventes, avec une structure propre, pas un prix qui zigzague autour | [03:10 · 04:39 · 04:57] |
| 3 | **Continuation seulement** : en baisse on vise les sommets, en hausse les creux | [06:16] |
| 4 | Étape 1 : marquer un sommet M15 dans la tendance, de préférence dans un imbalance (FVG) non rempli, partie d'une structure propre ; plus hauts/bas de séance aussi | [09:45 · 08:51] |
| 5 | Étape 2 : une bougie M15 prend le sommet **sans clôturer au-dessus** (rejet par la mèche) | [10:20] |
| 6 | Cette bougie doit être **haussière** pour une vente (baissière pour un achat) : sinon « le mouvement est déjà parti » | [22:15 · 25:27] |
| 7 | Étape 3 : **rectangle** de la clôture de cette bougie à son extrême ; regarder l'ouverture de la M15 suivante | [10:45 · 11:16] |
| 8 | **Entrée** quand une bougie M1 clôture hors du rectangle ; valide tant qu'aucune clôture ne dépasse le sommet | [15:06 · 20:33] |
| 9 | **Stop** légèrement au-delà de l'extrême (le spread) ; **objectif** 3:1 minimum, ou le prochain niveau clé | [15:56 · 01:18 · 16:06] |
| 10 | **Heures** : début d'Asie, Londres, New York et un peu après, jamais après New York | [12:36 · 13:12 · 20:10] |

**Ce que l'image a tranché** : graphique EUR/USD M15 Tickmill en **heure de New York** ; boîtes de séance Asie 20:00-00:00, Londres 02:00-05:00, New York 07:00-10:00 ; stops de **1,6 à 4 pips** ; la vidéo vend un abonnement (Edge Skool) et ne publie aucune statistique. **Elle ne parle jamais des annonces économiques** : le filtre des annonces est ton ajout.

## 3. Le code voit-il ce que l'auteur montre ?

| Exemple de la vidéo | Ce qu'il montre | Bougie Deriv (M15) | Détecté | Trade simulé |
|---|---|---|---|---|
| exemple 1 (Asie), 2025-10-31 01:15 UTC | vente, plus haut 1,15775, clôture 1,15766, stop 1,6 pip, R:R affiché 34,9 | haut 1.15775, clôture 1.15766 | oui | entrée 01:31 UTC, stop 2,3 pips, **+3,00 R** (objectif) |
| exemple 2 (Londres), 2025-10-31 06:15 UTC | vente, plus haut 1,15734, « même celui-ci fait 3 pour 1 » | haut 1.15734, clôture 1.15712 | oui | entrée 06:39 UTC, stop 2,8 pips, **+3,00 R** (objectif) |
| exemple 3 (New York + 1 h 45), 2025-10-31 15:45 UTC | vente, plus haut 1,15434, entrée à la clôture M1 de 12:04 New York, « 3 pour 1 puis 5 pour 1 » | haut 1.15430, clôture 1.15409 | oui | entrée 16:05 UTC, stop 3,2 pips, **+3,00 R** (objectif) |
| exemple 4 (Londres, imbalance), 2025-11-04 07:30 UTC | vente, plus haut 1,15336, clôture 1,15311, « 3 pour 1 puis 6 pour 1 » | haut 1.15336, clôture 1.15309 | **non** | — |

- Les prix Deriv reproduisent ceux de Tickmill **au dixième de pip** : le serveur Deriv est en UTC et le graphique de l'auteur en heure de New York.
- **Exemple 4 non détecté**, et c'est dit : chez Deriv la bougie clôture à 1,15309, soit 0,3 pip AU-DESSUS des deux sommets égaux qu'elle balaie (1,15306). La règle « clôture sous le sommet » la refuse.
- ⚠️ **Un seul réglage a été choisi pour retrouver ses exemples, avant tout résultat** : la structure « majeure » (pivots M15 de 12 bougies de chaque côté). Avec des pivots de 5 bougies, un simple repli inverse la tendance et AUCUN exemple ne passe.
- La même semaine (27 octobre - 7 novembre 2025), le détecteur a vu **19 setups**, dont 16 que la vidéo ne montre pas.

## 4. Toutes les versions testées (historique complet, coûts Deriv)

**EURUSD** (2019-01-02 → 2026-09-17, annonces couvertes 2018-12-30 → 2026-09-13)

| Version | Trades | Gagnants | Objectif atteint | Espérance | PF | Stop médian | Stops élargis | p |
|---|---|---|---|---|---|---|---|---|
| Règles de la vidéo, telles quelles | 3018 | 23,6 % | 21,2 % | -0,116 R | 0,85 | 4,6 pips | 11 % | 1,000 |
| Règles de la vidéo + pas d'entrée 30 min avant / 15 min après une annonce forte | 2941 | 23,8 % | 21,1 % | -0,113 R | 0,86 | 4,6 pips | 11 % | 1,000 |
| … + sortie 5 min avant chaque annonce forte | 2952 | 24,9 % | 19,7 % | -0,114 R | 0,85 | 4,6 pips | 11 % | 1,000 |
| … + sommet dans un imbalance non rempli EXIGÉ | 967 | 23,8 % | 20,4 % | -0,121 R | 0,84 | 4,9 pips | 9 % | 0,989 |
| … objectif 5 R (au lieu de 3) | 2874 | 17,1 % | 12,1 % | -0,148 R | 0,83 | 4,6 pips | 11 % | 1,000 |
| … objectif 2 R | 2981 | 30,4 % | 29,2 % | -0,118 R | 0,83 | 4,6 pips | 11 % | 1,000 |
| … objectif = prochain niveau M15 opposé (au moins 3 R) | 2887 | 19,5 % | 15,9 % | -0,121 R | 0,85 | 4,6 pips | 11 % | 0,999 |
| … la clôture M1 doit aussi casser le dernier creux M1 | 2555 | 23,4 % | 19,5 % | -0,145 R | 0,81 | 5,6 pips | 4 % | 1,000 |
| … stop trop court pour Deriv : trade sauté au lieu d'élargi | 2620 | 24,0 % | 21,0 % | -0,106 R | 0,86 | 5,0 pips | 0 % | 1,000 |

Coûts, même version : sans coûts **-0,020 R** · courtier « raw » (moitié) -0,069 R · Deriv -0,113 R · ×1,5 -0,179 R · ×2 -0,224 R.

**NAS100** (2024-01-22 → 2026-09-17, annonces couvertes 2018-12-30 → 2026-09-13)

| Version | Trades | Gagnants | Objectif atteint | Espérance | PF | Stop médian | Stops élargis | p |
|---|---|---|---|---|---|---|---|---|
| Règles de la vidéo, telles quelles | 1087 | 24,7 % | 22,8 % | -0,064 R | 0,92 | 17,4 points d'indice | 0 % | 0,894 |
| Règles de la vidéo + pas d'entrée 30 min avant / 15 min après une annonce forte | 1070 | 24,7 % | 22,1 % | -0,075 R | 0,90 | 17,6 points d'indice | 0 % | 0,927 |
| … + sortie 5 min avant chaque annonce forte | 1073 | 25,3 % | 21,1 % | -0,075 R | 0,90 | 17,6 points d'indice | 0 % | 0,931 |
| … + sommet dans un imbalance non rempli EXIGÉ | 331 | 23,0 % | 20,2 % | -0,143 R | 0,82 | 20,1 points d'indice | 0 % | 0,946 |
| … objectif 5 R (au lieu de 3) | 1041 | 18,5 % | 14,0 % | -0,049 R | 0,94 | 17,6 points d'indice | 0 % | 0,772 |
| … objectif 2 R | 1077 | 32,0 % | 30,6 % | -0,064 R | 0,91 | 17,6 points d'indice | 0 % | 0,934 |
| … objectif = prochain niveau M15 opposé (au moins 3 R) | 1047 | 19,6 % | 16,7 % | -0,085 R | 0,90 | 17,6 points d'indice | 0 % | 0,901 |
| … la clôture M1 doit aussi casser le dernier creux M1 | 935 | 26,6 % | 22,9 % | -0,020 R | 0,97 | 22,2 points d'indice | 0 % | 0,642 |
| … stop trop court pour Deriv : trade sauté au lieu d'élargi | 1069 | 24,7 % | 22,2 % | -0,074 R | 0,90 | 17,6 points d'indice | 0 % | 0,924 |

Coûts, même version : sans coûts **+0,015 R** · courtier « raw » (moitié) -0,017 R · Deriv -0,075 R · ×1,5 -0,101 R · ×2 -0,147 R.

## 5. Les annonces économiques

Source : les pages hebdomadaires de Forex Factory (horodatage Unix, aucun fuseau à deviner), 402 semaines. **Vérifié** : le NFP et l'IPC tombent à 08:30 New York dans 100 % des cas, le FOMC à 14:00 (les deux exceptions sont les réunions d'urgence de mars 2020). ⛔ Le jeu de données Hugging Face « Forex Factory 2007-2025 » a été écarté : 40 à 50 % des annonces fortes y sont à 00:00, l'heure est perdue.

| Marché | Trades dans la fenêtre d'une annonce (-30/+15 min) | Leur espérance | Trades hors fenêtre | Leur espérance |
|---|---|---|---|---|
| EURUSD | 131 (22,9 % gagnants) | -0,206 R | 2887 | -0,112 R |
| NAS100 | 43 (39,5 % gagnants) | +0,531 R | 1044 | -0,089 R |

- EURUSD : hors des annonces la méthode fait -0,112 R, donc le filtre ne peut pas la rendre gagnante.
- NAS100 : hors des annonces la méthode fait -0,089 R, donc le filtre ne peut pas la rendre gagnante. Les 43 trades pris près d'une annonce gagnent (+0,531 R), mais 43 trades ne prouvent rien, et c'est justement là que le spread s'écarte en vrai.

## 6. Les meilleures heures

Choisies sur les **80 % anciens** seulement (heures de New York avec au moins 30 trades et une espérance positive), puis jugées **une seule fois** sur les 20 % récents, jamais vus.

| Marché | Heures choisies (New York) | Au contrôle : trades | Gagnants | Espérance | Séances de l'auteur au contrôle |
|---|---|---|---|---|---|
| EURUSD | 4 h, 7 h, 8 h, 10 h, 13 h, 21 h | 309 | 25,9 % | **-0,036 R** | 618 trades, -0,062 R |
| NAS100 | 0 h, 2 h, 7 h, 9 h, 14 h, 22 h | 93 | 21,5 % | **-0,220 R** | 205 trades, -0,102 R |

Espérance par heure d'entrée (New York), règles de la vidéo, tout l'historique :

| Heure | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EURUSD | -0,19 (48) |  | -0,29 (227) | -0,24 (306) | -0,04 (244) | -0,52 (46) |  | +0,14 (178) | -0,01 (249) | +0,04 (189) | -0,00 (258) | -0,18 (203) | -0,24 (45) |  |  |  |  |  |  |  | -0,04 (240) | -0,07 (293) | -0,23 (232) | -0,26 (183) |
| NAS100 | +0,64 (17) |  | +0,09 (77) | -0,26 (109) | -0,07 (98) | -0,07 (17) |  | -0,10 (66) | -0,07 (103) | +0,07 (78) | -0,05 (105) | +0,02 (65) | -0,50 (16) |  |  |  |  |  |  |  | -0,28 (93) | -0,03 (70) | +0,08 (81) | -0,26 (75) |

Les heures qui brillaient sur le passé perdent sur la période jamais vue : c'était du bruit.

## 7. Les variantes (walk-forward, hors échantillon)

Grille : EMA 50 ou 200 · imbalance exigé ou non · objectif 2, 3, 5 R ou niveau opposé · validité 1 ou 4 bougies M15 · séances de l'auteur ou toutes, filtre des annonces toujours actif. Les réglages sont choisis sur 4 fenêtres passées et jugés sur la suivante, six fois de suite.

| Marché | Combinaisons | Trades hors échantillon | Gagnants | Espérance | p | Contrôle final (20 % récents) |
|---|---|---|---|---|---|---|
| EURUSD | 64 | 576 | 22,4 % | **-0,152 R** | 0,982 | 387 trades, -0,113 R |
| NAS100 | 64 | 298 | 21,1 % | **-0,207 R** | 0,987 | 39 trades, -0,385 R |

## 8. La correction statistique

Le registre compte désormais **146 tests** (les 124 d'avant + 22 pour cette vidéo). Tests Sniper qui survivent à la correction de Holm : **0**. Tests Sniper à espérance positive : **0**.

## 9. Ce que le backtest ne peut pas voir, et dans quel sens ça joue

- **Bougies M1, pas de ticks** : Deriv ne sert aucun tick passé (sondé : 0 tick pour la veille comme pour 2019). L'ordre des prix dans une minute est inconnu, donc **stop avant objectif** quand les deux tombent dans la même minute : hypothèse défavorable, mais le résultat SANS aucun coût est déjà nul.
- **Le spread de chaque minute** vient du champ `spread` des bougies 2025-2026 recalé sur les ticks du jour (3 points EUR/USD, jusqu'à 100 points à 17:01 New York ; 70 points fixes NAS100).
- **Chez un courtier « raw » comme celui de l'auteur**, les coûts seraient plus bas : c'est la ligne « moitié » de la section 4 (-0,069 R sur EUR/USD, -0,017 R sur NAS100).
- **Le discrétionnaire** : « structure propre », « niveau clé », sorties partielles et objectifs choisis à l'œil ne se codent pas tels quels. Chaque traduction est écrite dans `trading/recherche/sniper.py` pour être contestée, et les variantes testent les plus plausibles.
- **Deriv impose 2 pips** entre le prix et le stop : le stop de 1,6 pip de l'exemple 1 est impossible à poser. Élargi (version principale, -0,113 R) ou trade sauté (variante, -0,106 R) sur EUR/USD.

## 10. Conseils

1. **Ne pas trader cette méthode**, ni en démo pour « voir » : 7 ans de M1 et 2941 trades disent déjà ce que six mois de démo diraient, avec beaucoup moins de bruit.
2. **Ne pas l'intégrer à l'agent** : rien ne survit à la correction, rien n'est positif hors échantillon.
3. **Se méfier des exemples parfaits** : ils sont réels, mais sélectionnés. Une méthode se juge sur tous ses setups, y compris ceux qu'on ne montre pas.
4. **Le scalping M1 chez Deriv part avec un handicap d'environ 0,09 R par trade** sur EUR/USD : il faudrait un avantage brut bien supérieur pour le couvrir, et aucune des trois vidéos reçues n'en a montré.


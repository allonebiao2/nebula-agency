# 2026-10-08/09 · recherche trading : la méthode de Tori Trades (0026 et 0026b)

*Le détail vit dans le dépôt privé `nebula-trader` ; ici, seulement le renvoi.*

## Ce que Mongazi a demandé

Le 2026-10-08 au soir : « je t'ai envoyé dans le dossier partage les vidéos de Tori Trades, c'est la même stratégie, c'est
sa méthode, analyse en profondeur… et on passe à la simulation ». Puis trois autres vidéos dans la nuit, et : « garder en
mémoire… je t'enverrai d'autres vidéos, que tu emmagasines un max d'infos sur sa méthode » ; « appliquer à 100 % ce
qu'elle dit… que tu ne te trompes absolument pas lors des tests ».

## Comment les vidéos ont été lues

Six vidéos (A à F, environ 2 h 15 en tout). Aucune n'a de sous-titres dans le MP4 : les **sous-titres publiés sur YouTube**
ont été récupérés (`youtube-transcript-api`, durées identiques aux fichiers), donc **pas de Whisper** (arrêt brutal du PC
le 2026-10-08). 2 300 images clés regardées, plus la checklist FX Replay de sa méthode. Tout ce qu'elle dit, avec la
source et la minute : **`nebula-trader/_cerveau/methodes/tori-trades-sources/CARNET-METHODE.md`**, un carnet vivant à
enrichir à chaque nouvelle vidéo.

## Sa méthode en bref

Tracer les lignes que le prix n'a jamais traversées, du mensuel à l'unité d'entrée (chaque ligne repart du point B de la
précédente) : c'est exactement **l'enveloppe convexe** des plus bas et des plus hauts. Une clôture casse une ligne
(« ligne d'action ») : on entre dans le sens de la cassure ; le stop va derrière **la ligne opposée** (« ligne de
sécurité »), qui part du point extrême de l'écran, puis monte sur des lignes plus raides quand le prix avance. En 2026
elle trade **le pétrole seul, en 1 h** (avant : 4 h ; or, platine, Dow).

## Les décisions de Mongazi

- Entrées M3, M5, M15 (« intrascalping »), puis toutes les unités (4 h à M3) ; marchés : or, Dow, Nasdaq, S&P 500, puis
  le pétrole et le platine (chez Deriv, Dukascopy refusant les téléchargements) ; toutes les sorties et entrées testées.
- **« Il faut que le prix soit connecté à la trendline 3 fois »** : une touche est un vrai contact (0,05 ATR) ; il l'a
  maintenue même quand le trade d'or de Tori n'en avait que 2 nets dans nos données.
- Sa remarque sur la ligne de sécurité (« le stop serait derrière la ligne verte du bas ») a fait trouver un défaut :
  le stop montait sur un creux formé avant l'entrée. Corrigé. Il a conclu : « tu avais raison » (elle trace bien des
  lignes plus raides quand le prix prend de l'avance).
- « On ne trade que les breakouts » : les trois entrées (clôture, retest, double confirmation) sont des cassures, gardées.

## Les résultats

- **0026 (D-077)**, M3/M5/M15, ligne de sécurité fixe : **ne tient pas** (meilleur +0,08 R, t 0,6). Page :
  https://claude.ai/artifact/9hxiFMGck3xYhZXj2gBw3g
- **0026b (D-078)**, version complète, 360 réglages × 6 marchés : **ne tient pas**. Recherche : 10 réglages positifs sur
  110, **55 pour le miroir** (le trade à l'envers de la cassure) ; confirmation : meilleur +0,12 R (t 1,4) ; sa façon à
  elle (1 h) −0,15 R ; 42-48 % de gagnants, 1:2 touché 6-13 %. Page : https://claude.ai/artifact/15ie9NVnvG3mtJKWxFbeE6
- Son trade d'or du 20/05/2025 est retrouvé à l'heure près (entrée 3 235,75 contre 3 237,3) ; son trade du pétrole de mai
  2026 seulement à peu près (le CFD Deriv n'est pas son contrat).
- Le portage de Deriv sur le pétrole (0,19 à 0,20 $ par baril et par nuit) tue le swing.

## L'envers de ses cassures (D-079)

Mongazi : « tester l'envers de ses cassures ». Les 5 meilleurs miroirs de la recherche, figés avant de regarder, jugés sur la
confirmation : **aucun ne confirme** (−0,26 à +0,24 R, 20 à 30 % de gagnants, t ≤ 0,77). Le scellé EUR/USD 2003-2011 n'a pas
été ouvert (la règle exigeait les deux juges, le verdict était acquis). Ajouté à la page 0026b.

## Ce que le code a appris (dans `nebula-trader`)

Contrôles qui ont arrêté la chaîne et fait corriger avant tout chiffre : un contact compté sur un sommet non confirmé, un
rejeu qui oubliait le portage. Un jour férié américain se traverse comme un week-end. Commit `f45c909`.

## Ce qui reste

Le sort de la méthode (enterrer ou garder) : à la décision de Mongazi ; l'envers est jugé (ne confirme pas). L'audit du banc commun (bid/ask) et les correctifs 0025 non commités restent en attente.

## Méthode 0027 · les macros ICT de BananaFX (D-080)

Mongazi : « je t'ai envoyé une nouvelle vidéo, regarde-la, comprends-la, lis-la minutieusement ; l'objectif est de comprendre
la méthode à 100 % et de la reproduire en test et faire des simulations ». Vidéo « ICT : Le Marché Fait TOUJOURS pareil à ces
4 Horaires » (BananaFX, la chaîne du breaker block 0018), 10 min 42 s.

- **Lue en entier** : sous-titres YouTube (pas de Whisper, arrêt brutal du PC le 2026-10-08) et 269 images regardées.
- **La méthode** : 8 « macros » (fenêtres de 20-30 min, heure de New York) ; il en trade 3 (9 h 50, 10 h 50, 11 h 50) + Londres
  2 h 33 en option. Méthode 1 « dans la macro » (retour dans un FVG, objectif la liquidité) ; méthode 2 « après la macro », la
  sienne (la macro prend la liquidité, on trade le retournement après 10 h 10).
- **Son jour retrouvé** : il dit « Euro USD », mais l'échelle est celle du **Nasdaq (NQ)** ; vendredi **2023-12-01**, 1,1 point
  d'écart moyen sur 191 minutes (lecture des pixels de l'image contre toutes les journées 2019-2025). Sa liquidité = le plus
  haut / plus bas depuis 8 h ; ses FVG = le plus récent dont les 50 % n'ont pas été touchés : le code les retrouve seul.
  Ses entrées sont au point exact de la mèche (à 50 %, 1 achat servi sur 3 en vrai prix ; sa méthode 2 manque de 0,1 point).
- **Ses choix (questions à cliquer)** : le sens, tester les trois lectures (aucun, veille, premium/discount) ; l'entrée, 50 %
  et bord ; les 8 macros une par une ; marchés **EUR/USD, Nasdaq, USD/JPY**.
- **Résultat : ne tient pas.** 144 réglages × 3 marchés, recherche 2013-2021, confirmation 2022 → fin. Méthode 1 négative
  dans ses 48 réglages ; les 5 finalistes de la méthode 2 (toutes à Londres 4 h 03) perdent toutes depuis 2022. Ses critères :
  5,6 à 20,5 % d'objectifs, et même 1:2 hors d'atteinte (+2 R touché dans 23 à 31 % des trades). Sur son marché et sa macro,
  +0,02 R ; le miroir perd −0,45 R (le prix rebondit sur le FVG mais va rarement jusqu'à la liquidité). Les frais ne sont pas
  la cause. Page : https://claude.ai/artifact/MuDuwnagvhveYCvjXq9r1Q
- **Contrôle** : causalité par un futur empoisonné ; le premier essai était aveugle (son témoin tricheur passait), attrapé
  et refait avant tout chiffre. Commit `c25e3fc` (dépôt privé).
- **En attente** : enterrer ou garder la 0027 (décision de Mongazi) ; le scellé EUR/USD 2003-2011 n'a pas été ouvert.

## Classements et psychologie de « liquidity in the water » (fin du 2026-10-09)

- **Classement par taux de réussite** (demandé par Mongazi), relu dans les verdicts, rien de recalculé :
  https://claude.ai/artifact/KV2vqCBzn1usojGy5aTE3a. Aucune méthode à plus de 50 % à 1:2 ; la seule au-dessus de 50 %
  est le RSI(2) de Connors (64-67 %, sortie à la moyenne) ; la meilleure à 1:2 est le VWAP de l'or (41,4 %). La réussite
  dépend surtout de la distance de l'objectif.
- **Classement des 10 rentables** (gain par trade, période jugée) : 0024b +0,80 à +1,07 R (très fragile, 5 trades font
  86 %), LE PIÈGE +0,46 R, CDS 5 min +0,40 R, VWAP or +0,19 R, RSI(2) +0,15 R, ORB +0,13 R, Tori M5 +0,12 R, 0019 +0,11 R,
  macros ICT M2 +0,04 R, boîte de l'ouverture or +0,03 R. Par solidité : VWAP or, LE PIÈGE, ORB.
- **Psychologie de « liquidity in the water »** (sa méthode, 0024) : un piège tendu aux acheteurs dans un marché vendeur ;
  le code reproduit la FORME du piège, pas sa MATIÈRE. Version **0024c** proposée (règles de contexte : vraie liquidité de
  séance + heure de volume, imbalance M15/H1, preuve du piège, sortie en deux temps, moins de géométrie), à juger sur des
  marchés neufs (S&P 500, Dow, GBP/USD, USD/JPY). ⏳ **Mongazi : « tu me reposeras les questions, on y reviendra »** :
  `nebula-trader/_cerveau/methodes/liquidity-water-sources/PSYCHOLOGIE-0024c.md`.

## ULTIME METHOD (0028, sa méthode) : en pause

- Zone H1 = mèche du sommet ou du creux cassé, puis en M3 une imbalance et une liquidité confirmée par une CDS, entrée à la
  clôture de la prise. Ses deux exemples sont de l'**EUR/USD** (pas de l'AUD/USD) et le code les retrouve au point près
  (minutes Deriv de septembre-octobre 2026). Planche 1 faite, pas encore validée.
- Mongazi : « zappons ultime method actuellement » ; priorité à BBLOCK. Reprise : faire valider la planche 1, puis les flous
  (`nebula-trader/_cerveau/methodes/ultime-method-sources/ANALYSE.md`). Commit `b5e5ef7` (dépôt privé).

## BBLOCK (0029, sa méthode) : prête à simuler, rien n'est calculé

- **La figure, en exactement 4 bougies** : CDS 1 forte qui casse la structure (la première clôture au-delà) ; une bougie ;
  CDS 2 forte qui casse la structure ET l'EMA 50 dans la même bougie (ouvre d'un côté, clôture de l'autre) ; la bougie
  d'après, qui laisse une **imbalance** (obligatoire). Entrée au retour dans l'imbalance (bord ou 50 %), stops A/B/C,
  objectifs 1:2, 1:3, 1:5, ancien plus haut, sinon sortie à 18 h New York. Or et Nasdaq ; M3, M5, M15, H1.
- **Ses planches** : NAS100 M5 22/01/2024 (« oui, avec réserves »), XAUUSD M15 13/11/2024 (7/10 : l'EMA touchée avant
  devient un axe de qualité, pas une règle) ; **son trade EUR/USD H1 du 21/09/2026 retrouvé** (« oui c'est mon trade »).
- **Sa ligne de sortie** (« ajuste pour que ça corresponde, c'est juste les placements de trend comme j'ai fait ») : la 1re
  ligne part du plus haut ou du plus bas de la figure ; un repli confirmé par une mini-CDS et d'au moins **2 ATR** donne une
  nouvelle ligne plus raide ; on sort à la clôture d'une bougie au-delà de la ligne en vigueur. Elle redonne **ses trois
  lignes au point près** et sa sortie : **+5,44 R** contre ses +5,59 R (0,6 pip d'écart entre Deriv et ses prix FXCM).
  ⚠️ Le seuil de 2 ATR est calé sur un seul trade.
- **Défaut attrapé avant tout chiffre** : la première version réajustait la ligne sur la bougie testée, elle ne cassait donc
  jamais (+8,76 R sur son trade, faux). Un **contrôle de causalité des suivis** est ajouté (34 sorties inchangées quand
  l'avenir est empoisonné, témoin tricheur pris 17 fois sur 24).
- **La grille (D-081)** : 10 368 cellules par marché, recherche jusqu'à 2022, confirmation 2022 → fin. Essai à blanc de la
  chaîne passé (≈ 45-60 min pour le vrai calcul). ⚠️ Faute déclarée dans D-081 : l'essai à blanc a tourné sur janvier-mars
  2023, donc en période de confirmation ; il a affiché les 8 réglages « fidèles » sur ces trois mois (aucun ne remplit les
  conditions). Un essai à blanc se fait désormais sur la période de recherche.
- Commits `af028f5` et `db7ddba` (dépôt privé).

## BBLOCK jugée, puis le test à l'aveugle (fin d'après-midi et soir du 2026-10-09)

- **Simulations lancées** à la demande de Mongazi (« je veux qu'on commence les simulations test Bblock »).
- **Défaut de vitesse attrapé** : la recherche des sommets et creux (`_figures.pivots`, commune à plusieurs méthodes)
  réécrivait le reste du tableau à chaque sommet, d'où un temps au carré de la durée (≈ 4 h pour l'or en M3, 6 à 8 h la
  chaîne). Réécrite en un passage, **mêmes tableaux à l'octet près** (300 séries synthétiques + or et Nasdaq, 4 unités),
  300 à 400 fois plus rapide ; le calcul repart et tient en 10 min. ⚠️ L'essai à blanc sur 3 mois ne pouvait pas le voir.
- **D-081, unité par unité : ne tient pas.** 434 réglages positifs en recherche contre 1 138 pour le miroir ; les 10
  finalistes s'effondrent en confirmation ; H1 et figures « idéales » trop rares pour être jugés.
- **D-082, unités combinées** (idée de Mongazi : « combiner les unités pour avoir plus de setups »), 11 groupes, deux règles
  de chevauchement jugées à part (toutes les positions / une à la fois) : **ne tient pas non plus**. Hors verdict, une seule
  ligne ressort : sa version fidèle sur les 4 unités avec SA ligne dès 2 R, positive sur 2022 → fin (321-327 trades, deux
  moitiés positives, or et Nasdaq) mais négative sur 2008-2021 et t 1,4 : une époque ou le hasard. Seul le temps réel peut
  trancher. Page : https://claude.ai/artifact/WA4kHebPjpC7pXt4116XVq
- **D-083, 60 figures à l'aveugle** (Mongazi : « 60 trades à l'aveugle comme l'autre et je gère moi-même ») : tirage figé
  avant toute issue (graine 20261009, 4 strates), il pose ses niveaux d'avance sur un compte prop firm simulé (2 phases).
  Page : https://claude.ai/artifact/3eXAHcLfEpS2rQmBw2UHx1. Verdict écrit avant ; à faire quand il dit « verdict du test à
  l'aveugle BBLOCK ».
- ⏳ **D-084, le temps réel** (son choix : alertes + prop firm simulée) : à concevoir et écrire avant de brancher.
- Commits privés `69866ca`, `2e03c42`.


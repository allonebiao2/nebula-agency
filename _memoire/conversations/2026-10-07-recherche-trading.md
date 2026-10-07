# Recherche trading, 7 octobre 2026 (renvoi)

Le travail de trading vit dans le dépôt **privé** `allonebiao2/nebula-trader`
(`C:\Users\USER\nebula-trader`). Cette page n'en garde que le fil, sans chiffre ni règle de
méthode : ce dépôt-ci est public.

## Ce qui s'est passé

- Mongazi renvoie d'abord la vidéo du scalping EMA 50/200 : c'était la méthode 0016, déjà jugée et
  enterrée. Rien n'a été refait ; le résultat lui a été redonné.
- Il envoie une vidéo de BananaFX, « ICT & SMC Le BREAKER BLOCK expliqué en 7 MINUTES », rangée dans
  `_partage/`. Elle a été **transcrite et lue image par image** (172 images). Elle ne donne aucun chiffre et
  aucun objectif de gain.
- **Méthode 0018** (décision D-067 dans le dépôt privé, figée avant calcul) : le breaker block codé en M15,
  12 variantes (deux stops, trois objectifs, avec ou sans biais), sur l'or et le Nasdaq. Mongazi a ajouté le
  Nasdaq en cours de route.
- Il a demandé ce qui empêche un résultat d'être flatteur : réponse donnée en dix protections (règles figées
  avant, années jamais utilisées, garde de causalité, frais réels, ordres limites honnêtes, témoin miroir,
  seuil relevé, deux moitiés, son critère, la démo).
- **Verdict 0018 : ne tient pas**, sur aucun marché. À sa demande (« test à la dure »), le scellé EUR/USD
  2003-2011 a été ouvert : il ne confirme rien non plus.
- Une erreur de dessin a été trouvée et dite : les objectifs de la planche 1 étaient tracés du mauvais côté.
  Le calcul, lui, était juste. La planche est corrigée.
- Mongazi a demandé que les « ratios » soient positifs : expliqué que le ratio (1:2, 1:3) l'est, et que le
  chiffre négatif est le résultat moyen réel. Le rendre positif serait régler après coup.
- **Méthode 0019** (D-068), son idée : les setups du breaker gardés seulement si la bougie de cassure traverse
  aussi l'EMA 50 avec force, et si le schéma se joue au POC du profil de volume d'hier. 15 filtres × 12
  variantes. **Verdict : ne tient pas.** Le scellé n'a pas été ouvert.
- **Méthode 0020** (D-069), sa demande : « tester les combinaisons possibles ». Prévenu avant du piège (une
  recherche sur des milliers de combinaisons trouve toujours quelque chose par hasard). Recherche en deux
  temps : la grille sur les années déjà utilisées, puis 5 finalistes confirmés sur des années jamais utilisées
  pour le breaker. **Verdict : rien.** Prendre le trade à l'envers trouvait plus de combinaisons gagnantes que le
  breaker lui-même, et aucun finaliste n'a tenu sur les années neuves. Le scellé n'a pas été ouvert.
- Il a demandé que tout lui soit expliqué en français : une partie des messages était partie en anglais.

## La décision

- Mongazi : « oui enterre les trois ». Les méthodes 0018, 0019 et 0020 vont au cimetière du cerveau, qui compte
  désormais 21 méthodes (nouvelle famille « structure »). Seule piste vivante : le VWAP de l'or en 1 heure, en démo.

## Pages des résultats (privées)

- 0018 : https://claude.ai/artifact/2Xq6qL9WuGMXP6U7UrrYgG
- 0019 : https://claude.ai/artifact/GhfHr7WMgi9W2SJ3aCHM6s
- 0020 : https://claude.ai/artifact/7yff2XPjpFBW7qMs7sJGTh

## Où lire la suite

Dans le dépôt privé : `_cerveau/DECISIONS.md` (D-067, D-068, D-069 et leurs résultats),
`_cerveau/methodes/0018-breaker-block.md`, `_cerveau/methodes/0019-breaker-ema-poc.md`,
`_cerveau/methodes/0020-recherche-breaker.md`,
`_cerveau/methodes/breaker-block-sources/ANALYSE.md`.

## Laissé sur le disque

- La vidéo du breaker reste dans `_partage/` **sans être committée**.
- Les planches en PNG sont copiées dans `_partage/capture de la methode/` pour Mongazi.

## Après-midi : la vidéo « Testing a 91% Win Rate Trading Strategy » (analyse seule)

Reçue de Mongazi : un vidéaste reteste la stratégie de Trading Nerds sur **GBP/JPY** :
**HalfTrend** (everget, amplitude 5) + **Laguerre RSI** (Kivanc, alpha 0,2) en **1 h**, entrée en
**5 min** au premier rejet dans la **golden zone** d'un Fibonacci, stop sous le dernier plus bas,
objectif sur l'extension −0,25. Il annonce 44 % de réussite, ratio moyen 2,88, +102 % sur 100 trades
(2022-2023). **Rien n'est testé** ; aucun chiffre de trading n'est le nôtre.

Ce que la relecture image par image a montré :
- les **61 lignes visibles** de son registre font **56 %** ; les **39 lignes jamais montrées**
  (novembre 2022 à avril 2023) doivent donc faire environ **26 %** ;
- **12 de ses 62 dates (19 %) tombent un week-end, marché fermé** : ses trades ne se retrouvent pas
  un par un.

Analyse : dépôt privé, `_cerveau/methodes/halftrend-laguerre-sources/ANALYSE.md` (commit `30dd51f`).
La vidéo reste dans `_partage/` sans être committée.

## Soir : la méthode 0021 jugée (D-070)

Mongazi a répondu « tester les trois » à chaque flou, puis : « pas forcément les planches, assure-toi que ça
corresponde à ce qu'il montre, commence les simulations ».
- **Fidélité** : nos indicateurs retrouvent ses signaux 1 h à l'heure près ; il achète avec une ligne HalfTrend
  rouge (« clôture au-dessus » est sa vraie règle). Ses entrées sont en partie à l'œil : la meilleure lecture
  mécanique retrouve 3 de ses 6 trades datés.
- **Reproduction** (sa période) : 173 trades, 12,7 %, ratio prévu 1:9,2, −0,39 R. Lui : 100 trades, 44 %, 2,88.
- **Recherche** (GBP/JPY 2019-2023, 26 244 combinaisons) : 703 positives, 573 à l'envers ; aucun réglage à
  espérance moyenne positive. Aucune combinaison ne remplit le critère de Mongazi.
- **Confirmation** (GBP/JPY 2023-2026, EUR/JPY) : les cinq finalistes perdent sur les années neuves de GBP/JPY.
- **Verdict : ne tient pas.** Mongazi : gardée en attente, pas enterrée.

Page : https://claude.ai/artifact/Fz6MHtFemkNgqEERh6tqJF · dépôt privé : D-070, `_cerveau/methodes/0021-halftrend-laguerre.md`.

## Fin de journée : la méthode 0022 « scalping 15 secondes » (D-071)

Vidéo d'IBLV Trading (Nasdaq, ouverture de New York) : prise de liquidité au-delà d'un niveau du jour, reclôture de
l'autre côté, entrée dans le sens du retour, stop juste au-delà, sortie sur la chasse ; zone 1 h en confluence ; ajout
sur le 15 secondes. Mongazi : « tester les trois » partout, recherche 2013-2021, confirmation 2022-2026.
- **Fidélité** : son trade du 20 juin 2025 retrouvé à sa minute (9 h 46, +3,5 R). Ses niveaux de carnet d'ordres
  tombent sur le haut et le bas de la pré-ouverture. Le 15 s et le niveau 2 n'existent pas dans nos données.
- **Résultat** : recherche 79 % de combinaisons positives ; confirmation : aucun finaliste ne gagne significativement
  sur le Nasdaq ET le S&P 500 → **ne confirme pas**. La fidèle : Nasdaq +0,46 R (t 2,5), S&P 500 −0,13 R.
  Critère de Mongazi non rempli (38 % de réussite, 11 pertes d'affilée).
- **Hors verdict** : 64 % des combinaisons positives sur le Nasdaq 2022-2026, 23 % sur le S&P 500 : un effet propre au
  Nasdaq, porté par la zone 1 h. Plus d'années Nasdaq vierges : la suite serait un essai en démo.
- **Défaut corrigé** : stop calculé sur le prix prévu, entrée à l'ouverture suivante ; une ouverture déjà au-delà du stop
  sortait au prix du stop (gain fictif). Présent dans la 0021 aussi ; tout rejoué, verdicts inchangés.

Page : https://claude.ai/artifact/SphYSJP5rCpDA8tfv17L3s · dépôt privé : D-071, `_cerveau/methodes/0022-scalping-15s.md`.

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

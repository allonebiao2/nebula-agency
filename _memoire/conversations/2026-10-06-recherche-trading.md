# Recherche trading, 6 octobre 2026 (renvoi)

Le travail de trading vit dans le dépôt **privé** `allonebiao2/nebula-trader`
(`C:\Users\USER\nebula-trader`). Cette page n'en garde que le fil, sans chiffre ni règle de
méthode : ce dépôt-ci est public.

## Ce qui s'est passé

- Mongazi envoie une vidéo YouTube de Casper SMC, « The Best Volume Profile Strategy (That Actually
  Works) », rangée dans `_partage/` : une stratégie de **profil de volume** sur le S&P 500 et le NASDAQ.
- La vidéo a été **transcrite et lue image par image**, puis analysée : ce qu'elle prouve (peu, son
  propre compte ne dit pas ce que disent ses exemples), ce qui est mécanique et ce qui est laissé à l'œil.
- **Une planche** de son exemple du 10 mars 2026, tracée avec nos données, a montré que le point de
  départ de la jambe décide du sens du trade. Mongazi ne maîtrisant pas la méthode, la règle retenue est
  celle qui reproduit l'écran de l'auteur.
- **Méthode 0015** (décision D-064 dans le dépôt privé, figée avant calcul) : les trois scénarios de
  l'auteur, deux placements de stop et deux sorties, comme Mongazi l'a demandé.
- **Verdict : aucune combinaison ne tient** sur treize ans. Le résultat positif vu chez Deriv sur la
  période récente vient de la période, pas du volume du courtier.
- Page des résultats (privée) : https://claude.ai/artifact/FnvsiF66wvGG1p9SC7oSGS

## Seconde vidéo du jour : méthode 0016

- Mongazi envoie une seconde vidéo, de la chaîne Trade Pro : « 1 Minute Scalping Strategy Just Using
  50 EMA And 200 EMA ». Ses règles sont entièrement mécaniques.
- Notre moteur **retrouve ses 14 trades** de février 2021, dans le même ordre.
- **Méthode 0016** (décision D-065, figée avant calcul). Choix de Mongazi : six autres paires majeures,
  puis une ouverture unique des années scellées de l'EUR/USD ; unités 1, 5 et 15 minutes ; sa règle seule.
- **Verdict : elle ne tient dans aucune unité**, ni sur les six paires ni sur les années scellées. Sans
  frais elle est à zéro : ses bons résultats venaient de sa période.
- Page des résultats (privée) : https://claude.ai/artifact/SdztAoPndbmapUxvxmS6Tu

## L'idée de Mongazi : ajouter le profil de volume (méthode 0017)

- Mongazi demande d'ajouter le profil de volume à la méthode EMA 50/200. Prévenu avant : deux méthodes
  à zéro ne font pas une méthode positive en s'additionnant.
- **Méthode 0017** (D-066, figée avant calcul) : les setups de la 0016, filtrés par le profil de la
  journée précédente, trois filtres jugés chacun à part, en 5 et 15 minutes.
- **Verdict : aucun filtre ne passe.** Un seul trie un peu dans le bon sens et reste négatif. Les années
  scellées de l'EUR/USD n'ont pas été ouvertes, comme prévu dans ce cas.
- La page de la 0016 porte maintenant aussi la 0017 (même adresse).

## Le 7 octobre : les trois méthodes enterrées

- Mongazi : « d'accord ». Les méthodes 0015, 0016 et 0017 vont au cimetière du cerveau, qui compte
  désormais 18 méthodes. Le cerveau refusera de les retester sans dire ce qui a changé.
- Le contrôle qui vérifie qu'« une idée neuve ne déclenche rien » a dû changer de phrase témoin : l'ancienne
  parlait de volume, elle est devenue une cousine légitime des profils de volume enterrés. Un contrôle
  ajouté exige désormais qu'elle déclenche l'alerte de famille.
- Seule piste vivante : le VWAP de l'or en 1 heure, en démo. L'arrêt du 31 décembre 2026 tient.

## Où lire la suite

Dans le dépôt privé : `CLAUDE.md` (l'état), `_cerveau/DECISIONS.md` (D-064 et son résultat),
`_cerveau/methodes/0015-vacuum-volume-profile.md`, `_cerveau/methodes/volume-profile-sources/ANALYSE.md`,
D-065, `_cerveau/methodes/0016-scalping-ema-50-200.md`, `_cerveau/methodes/ema-50-200-scalping-sources/ANALYSE.md`,
D-066, `_cerveau/methodes/0017-ema-50-200-profil-volume.md`.

## Laissé sur le disque

- Les deux vidéos (35 et 54 Mo) restent dans `_partage/` **sans être committées**.
- Deux planches en PNG ont été copiées dans `_partage/capture de la methode/` pour Mongazi.

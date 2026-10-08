# 2026-10-08 · recherche trading : la méthode 0023, après l'arrêt brutal du PC

*Le détail vit dans le dépôt privé `nebula-trader` ; ici, seulement le renvoi.*

## L'arrêt du PC

Le 2026-10-08 à **00 h 38**, le PC s'est arrêté sans arrêt normal (journal Windows : Kernel-Power 41 et 6008).
La session transcrivait la vidéo `yoyoyo.mp4` envoyée par Mongazi la veille au soir (« fais comme d'hab ») ; la
transcription n'en était qu'à 5 min 56 s sur 19 min 50 s, ralentie par le manque de mémoire. Rien n'a été perdu (les
369 images étaient extraites). Mongazi au retour : « le pc s'est coupé, tu traitais les méthodes trading je crois ».

- Relancée, Whisper large-v3-turbo traitait **46 s d'audio en 22 min** (1 Go libre, processeur à 4 % : le disque
  d'échange) ; le modèle léger mettait plus de 3 h à se télécharger (37 Ko/s la nuit).
- **Parade** : la vidéo porte ses **sous-titres incrustés** ; la bande du bas a été découpée toutes les 0,5 s et
  lue sur 14 planches (`nebula-trader/_cerveau/methodes/yoyoyo-sources/_sous_titres.py`). Plus rapide et plus sûr.

## La méthode 0023, « la boîte de la bougie d'ouverture américaine » (D-073)

Boîte = haut et bas de la bougie 1 h de 9 h - 10 h New York, avec son milieu. En 5 min après 10 h : rejet au bord,
rejet au milieu, ou cassure puis retour (stop au bord opposé, objectif 2 hauteurs). Mongazi : « tester toutes les
lectures », Nasdaq et or, recherche 2013-2021, confirmation 2022-2026 (S&P 500 en juge).

- **Son seul trade réel** (or, 19/12/2025, +3 627 $) est **reproduit à la minute** (entrée 10 h 30, objectif touché le
  21/12 à 20 h 38, comme son relevé).
- 1 296 combinaisons : 298 positives en recherche, finalistes = billets de loterie (10-16 % de réussite).
- **Aucune ne confirme.** Sa lecture de la cassure est la seule positive sur les trois marchés en 2022-2026 (t 2,24,
  il fallait 2,6) mais perdait avant. **Hors verdict, le hasard fait mieux que la méthode sur les trois marchés.**
- Critère de Mongazi : rempli nulle part (à 1:2, au mieux 36,6 % d'objectifs atteints).
- **Enterrée** (Mongazi : « oui, enterre-la ») : cimetière à 22, fiche `22-boite-ouverture.md`.

Page : https://claude.ai/artifact/3oxChWZ3NwDkbR5W7mvP1p · dépôt privé : D-073, `_cerveau/methodes/0023-boite-ouverture.md`.

## En attente

- Ses deux dossiers de méthode personnelle, **`_partage/ULTIME METHOD/`** (AUDUSD, schéma, 2026-10-06) et
  **`_partage/liquidity in the water/`** (EUR/USD, EMA 50/200, jambes, CDS, imbalance, 2026-10-07), n'ont pas encore
  été traités. Mongazi choisit de commencer par **« liquidity in the water »**.

## Suite : sa méthode « liquidity in the water » (0024, D-074), validée planche par planche

Mongazi a choisi de traiter sa propre méthode (`_partage/liquidity in the water/`, 2 captures EUR/USD 3 min, 23 et 28/09/2026).
- Ses deux captures sont **retrouvées au prix près** par le code (jambe 1, CDS, imbalance, stop exactement le sien le 28/09).
- **11 planches** (`_partage/liquidity in the water/planches/`), chacune a donné une règle : bougie de prise baissière (3) ; CDS
  nette (4) ; « un bon setup doit être une évidence » → imbalance et figure minimales (5) ; jambe 1 = le plus haut avant la CDS,
  imbalance vierge (6) ; ⛔ **la prise = la PREMIÈRE bougie qui balaie la jambe 1 et entre dans l'imbalance, jamais la suivante**
  (7, faute de Claude corrigée : « ne refais plus cette erreur ») ; imbalance extrême, mèches dégagées sur les planches (8) ;
  ⛔ **EMA emmêlées = consolidation, jamais de trade** : la lecture « la 50 sous la 200 » seule est retirée (9, « tu dois
  comprendre cette psychologie ») ; rien dans l'imbalance après la jambe 1 (10) ; **planche 11 : « c'est ma figure »**.
- **Extrême** (sa définition) : l'imbalance tout en haut de l'impulsion qui a créé la CDS, encore vierge.
- ⚠️ **Très rare** : EUR/USD 3 min 2013-2021, 24 472 figures, **4** passent toutes ses règles (231 sans « imbalance ≥ 1 ATR ») ;
  les filtres qui coupent le plus : la couleur de la bougie de prise (9,6 %) et l'imbalance ≥ 1 ATR (12,6 %).
- **D-074 figée** : 11 337 408 combinaisons par marché et par unité, EUR/USD, Nasdaq, or, 3/5/15 min ; « le point de chaque
  combinaison » gardé (outil local `python -m cerveau.methodes_code._0024_point` → http://localhost:8724/).
- Annonces : calendrier Forex Factory 2013-2018 téléchargé pour l'occasion (le serveur a coupé une fois, reprise patiente).

## Le verdict de la 0024 (D-074)

102 millions de combinaisons (EUR/USD, Nasdaq, or ; 3, 5, 15 min), recherche 2013-2021 puis confirmation 2022-2026.
- **Sa lecture complète est trop rare pour être jugée** : 9 trades en 9 ans (3 min, trois marchés réunis), 8 sur 2022-2026.
- Recherche : le 5 min se détache (73 % de combinaisons positives contre 24 % pour le témoin) ; le 3 et le 15 min non.
- **Aucun finaliste ne confirme** sur 2022-2026 (moins de 100 trades, t < 2,6). Hors verdict : l'avantage du 5 min disparaît ;
  le 3 min fait l'inverse de la recherche (53 % positives contre 10 % pour le témoin après 2022, l'inverse avant).
- Page : https://claude.ai/artifact/T7HnKERq85K4kLS7qVPZZv · le point de chaque combinaison (dépôt privé) :
  `python -m cerveau.methodes_code._0024_point` → http://localhost:8724/.
- Enterrement : à la décision de Mongazi (c'est sa méthode). « ULTIME METHOD » reste à traiter.

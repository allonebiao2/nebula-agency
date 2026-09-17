# Recherche sans fin · une stratégie de SCALPING qui atteint les critères de Mongazi

> **Ce document est écrit AVANT le premier résultat de cette recherche** (2026-09-17). Tout ce qui
> suit — mesure, paliers, données scellées, règles de comptage — est fixé d'avance. C'est la seule
> protection contre le défaut central d'une recherche « jusqu'à trouver » : à force d'essayer, on
> finit toujours par trouver un backtest flatteur né du hasard.

## Ce qu'on cherche

Mongazi, 2026-09-17 : « recherche une stratégie qui puisse atteindre ces objectifs, tant qu'on ne
trouve pas tu ne peux pas t'arrêter », puis « je veux plus de scalping, des trades ouvrables et
fermables dans la même journée, et à la limite de l'intrascalping ».

- **R:R d'au moins 1:2**, et **plus de 50 %** des trades qui atteignent vraiment leur objectif de 2 R
  (idéal 60-70 %).
- **Risque extrêmement bas de 5 ou 6 pertes d'affilée.**
- **EUR/USD et NAS100 seuls** sont tradés. D'autres marchés peuvent servir d'information.
- **Scalping et intraday** : exécution M1 à M15, **tout trade fermé le jour même**. H1, H4 et D1
  servent de contexte, jamais d'horizon de détention.

## La borne, calculée avant de chercher

Probabilité exacte (programmation dynamique) d'au moins une série de pertes sur 100 trades :

| 2 R atteints | Espérance à 1:2, avant coûts | P(5 pertes d'affilée) | P(6 pertes d'affilée) |
|---|---|---|---|
| 34 % (point mort) | +0,02 R | 99,7 % | 96,7 % |
| 50 % | +0,50 R | 81,0 % | 54,6 % |
| 60 % | +0,80 R | 45,9 % | 21,2 % |
| 70 % | +1,10 R | 15,3 % | 4,8 % |

**Conséquence, dite une fois** : « série de pertes extrêmement rare » et « 50 % de réussite » ne
peuvent pas coexister. Il faut environ **70 %** de 2 R atteints pour que 6 pertes d'affilée sur 100
trades tombent sous 5 %. D'où les deux paliers, choisis par Mongazi.

## Les deux paliers

| | Palier 50 | Palier 70 |
|---|---|---|
| 2 R atteints, hors échantillon | > 50 % | ≥ 70 % |
| Trades hors échantillon | ≥ 100 | ≥ 100 |
| Espérance après coûts réels | > 0 | > 0 |
| Correction de Holm sur le registre entier | survit | survit |
| P(6 pertes d'affilée / 100) | mesurée et affichée | < 5 % |

## Le coût, qui décide de tout en scalping

Le point mort à 1:2 n'est pas 33,3 % mais **(1 + c) / 3**, où *c* est le coût d'un aller-retour
exprimé en R. Mesuré sur ce dépôt : 0,02 R en H4, **0,19 R en M5** → point mort ≈ **40 %**, et
davantage en M1. Le coût est donc compté **minute par minute** (`spread_horaire.spread_par_barre`,
heure de New York, rollover de 17:00 compris) et non avec une médiane unique.

Sur les données Dukascopy, le coût retenu est le **plus cher des deux** : le profil Deriv d'aujourd'hui
et le spread réellement observé à l'époque. Appliquer le spread de 2026 à l'EUR/USD de 2004 (où il
valait plusieurs pips) rendrait rentable ce qui ne l'était pas.

## Les données : découverte et scellé

Vérifié le 2026-09-17 en sondant le service : le M1 Dukascopy commence le **2003-05-04** pour
`eurusd` et en **janvier 2013** pour `usatechidxusd` (rien en 2012).

| Instrument | Découverte (on cherche dessus) | **Scellé** (on n'y touche qu'une fois, par candidate) |
|---|---|---|
| EUR/USD | Deriv M1 2019→2026, M5-M15 2012→2026 | **Dukascopy 2003-05 → 2011-12** |
| NAS100 | Dukascopy 2013 → 2019-12 · Deriv 2024-01 → 2026 | **Dukascopy 2020-01 → 2023-12** (krach 2020, baisse 2022) |

Règles du scellé, tenues par `trading/recherche/scelle.py` :
- il refuse de rendre les barres sans `--ouvrir <candidate>` ;
- **une ouverture par candidate**, inscrite au registre avec sa date ;
- aucune grille de réglages n'est choisie dessus : les réglages arrivent figés de la découverte.

## Les trois étages

1. **Découverte** : walk-forward du banc (`banc.walk_forward`) sur les données de découverte.
2. **Confirmation** : une ouverture du scellé, puis le moteur officiel `backtest/moteur.py` avec tous
   les verrous du cahier des charges.
3. **Démo en observation** sur le compte Deriv `6305888` : 30 jours **et** 30 trades. **« Trouvé » ne
   se dit qu'ici.** Un candidat qui passe l'étage 2 est annoncé aussitôt comme *candidat confirmé*.

Rien ne passe en réel sans l'accord de Mongazi.

## Le comptage

- **Mesure primaire** : part des trades sortis par **OBJECTIF** (2 R touché), jamais « gagnants » :
  un test à 53,8 % de gagnants n'atteignait l'objectif que 1 fois sur 320.
- Test binomial unilatéral contre le point mort **coûts compris**, et **correction de Holm sur le
  registre entier** : les 312 tests déjà faits plus tous les nouveaux, chaque réglage compté.
- Un avantage de la taille demandée survit à cette correction : 50 % contre 33 % sur 300 trades donne
  z = 6,1, au-delà du seuil de Holm même après un million de tests (z ≈ 5,9). **La correction
  n'empêche pas de trouver ; elle empêche de croire au hasard.**
- Chaque verdict s'ouvre par les trois chiffres de Mongazi : 2 R atteints (et gagnants à part), R:R
  réalisé, P(5) et P(6) pertes d'affilée sur 100 trades avec la plus longue série observée.

## Les vagues

| # | Vague | Ce qu'elle produit |
|---|---|---|
| 0 | Données et outils | Dukascopy, scellé, coût par minute, surprise des annonces |
| 1 | **Carte de P(2 R avant 1 R)** | Où, dans la journée, la probabilité dépasse le point mort |
| 2 | Familles de scalping à mécanisme | 7 familles jamais testées |
| 3 | Méta-étiquetage (apprentissage) | Un modèle qui vise directement P(2 R avant 1 R) |
| 4 | Recherche exhaustive de règles | Conjonctions de 2-3 conditions, toutes au registre |
| 5 | Confirmation | Scellé, moteur officiel, démo |

La vague 5 se déclenche dès qu'un candidat existe, sans attendre la fin des autres.

## POINT D'ARRÊT

*(mis à jour à la fin de chaque vague ; une nouvelle session reprend ici)*

- **2026-09-17** · Vague 0 en cours. Protocole écrit. Dukascopy sondé : EUR/USD M1 depuis 2003-05-04,
  NAS100 M1 depuis 2013-01. Registre : 312 tests, 0 survivant, meilleur taux de 2 R atteint **26,2 %**
  (ETE inversé EUR/USD H1) et **7,0 %** sur au moins 1 000 trades.
- **Prochaine étape** : télécharger le M1 Dukascopy (bid et ask), contrôler l'alignement avec Deriv,
  puis la carte de la vague 1.

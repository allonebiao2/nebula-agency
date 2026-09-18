# Stratégies publiées, cherchées sur le web · 2026-09-18

*Demande de Mongazi, après le test d'un an : « trouve-moi sur la toile une méthode qui pourra nous
permettre d'atteindre l'objectif du plan (compounding, échelle par le drawdown) ».*

## Ce que dit la recherche sérieuse, en une phrase

**Aucune étude crédible ne montre plus de 50 % de trades gagnants avec un objectif à 2 fois le
risque.** Ce serait +0,5 R par trade, soit un avantage énorme. Les stratégies publiées avec des
données se rangent en deux familles, qui font chacune l'inverse de l'autre :

| famille | trades gagnants | taille des gains | exemple sourcé |
|---|---|---|---|
| **suivre le mouvement** (cassure, momentum) | **25 à 48 %** | gains 2 à 10 fois plus grands que les pertes | ORB 5 minutes sur QQQ : 24 %, objectif 10 R |
| **parier sur le retour** (survente) | **70 à 75 %** | gains plus petits que les pertes, souvent sans stop | RSI(2) de Connors sur le S&P 500 : 75 % |

Une page qui affiche « 80 % à 1:2 » vend quelque chose, ou triche comme notre simulateur trichait.

## Les candidats testables sur nos marchés

### 1. Opening Range Breakout 5 minutes · Nasdaq 100 (Zarattini & Aziz)
- **Règles (version QQQ)** : à 9 h 35 New York, entrer dans le sens de la première bougie de
  5 minutes (achat si elle monte, vente si elle baisse). Stop à l'extrême opposé de cette bougie.
  Objectif 10 R, sinon sortie à la clôture. 1 % de risque par trade, levier plafonné à x4.
- **Résultats publiés (2016 → février 2023)** : **24 % de trades gagnants**, ~+0,13 R par trade,
  33 %/an, Sharpe 1,13, pire recul 22 %. Sur TQQQ : 48 %/an, recul 28 %.
- **Réserves** : pas de glissement modélisé, pas de période hors échantillon séparée, une variante à
  9 350 % sort d'une recherche de paramètres. Jamais testé sur un CFD US100.
- **Pourquoi c'est intéressant pour nous** : c'est le même indice que notre NAS100, l'entrée est au
  marché (le piège des ordres limites ne s'applique pas), et **tout ce qui suit février 2023 est une
  période que les auteurs n'ont jamais vue** : 3,5 ans de juge neutre dans nos données.
- Sources : [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416622) ·
  [synthèse des deux articles ORB](https://danfin.net/opening-range-breakout-research) ·
  [CXO Advisory](https://www.cxoadvisory.com/technical-trading/day-trading-with-an-opening-range-breakout-strategy/)

### 2. Momentum intraday par « zone de bruit » · S&P 500 (Zarattini, Aziz & Barbon)
- **Règles** : chaque minute, une zone de bruit = prix d'ouverture ± la variation moyenne atteinte à
  cette minute sur les 14 derniers jours (corrigée du gap de la nuit). Entrer quand le prix sort de
  la zone, stop suiveur (bord de la zone ou VWAP), tout fermé à la clôture, taille par volatilité.
- **Résultats publiés (2007 → début 2024, net de coûts)** : 19,6 %/an, Sharpe 1,33 ; **environ 43 %
  de trades gagnants**, les gagnants nettement plus grands que les perdants.
- **Réserves** : remplissage instantané supposé, un seul marché (SPY), un relecteur trouve les
  résultats « un peu trop beaux ». Hors échantillon naturel : **2024 → 2026**.
- Sources : [SSRN](https://ssrn.com/abstract=4824172) ·
  [Swiss Finance Institute](https://www.sfi.ch/en/publications/n-24-97-beat-the-market-an-effective-intraday-momentum-strategy-for-s-p500-etf-spy) ·
  [revue critique](https://quantmacro.substack.com/p/paper-review-an-effective-intraday)

### 3. Momentum de la dernière demi-heure (Gao, Han, Li & Zhou, 2018)
- **Règle** : le rendement de la première demi-heure (depuis la clôture de la veille) prédit celui de
  la dernière demi-heure, dans le même sens. Plus fort les jours volatils et les jours d'annonces.
- **Publié au Journal of Financial Economics**, 1993-2013, pente 6,94, R² 1,6 % : réel mais faible.
- Source : [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866)

### 4. Momentum de série temporelle (Moskowitz, Ooi & Pedersen, 2012)
- **Règle** : acheter ce qui a monté sur 12 mois, vendre ce qui a baissé, chaque mois. Les 58 contrats
  testés (devises comprises) ont un momentum positif ; portefeuille diversifié : Sharpe ~1,1.
- **Pour nous** : lent (quelques trades par an et par marché) et fait pour un portefeuille diversifié,
  pas pour deux marchés avec 10 $.
- Sources : [article (NYU Stern)](https://w4.stern.nyu.edu/facdir/lpederse/papers/TimeSeriesMomentum.pdf) ·
  [Quantpedia](https://quantpedia.com/strategies/time-series-momentum-effect)

### 5. RSI(2) de Connors · retour à la moyenne (S&P 500, journalier)
- **Publié** : ~75 % de trades gagnants depuis 1993, ~+0,5 % par trade, **293 trades en 30 ans**.
- ⛔ **Incompatible avec notre doctrine** : Connors note que le **stop fixe dégrade** la stratégie ;
  elle vit sans stop chez le courtier, ce que notre code interdit.
- Source : [QuantifiedStrategies](https://www.quantifiedstrategies.com/rsi-2-strategy/)

## Ce que ça change pour le plan de Mongazi

- **L'échelle 6-4-3 et le compounding marchent avec n'importe quelle stratégie à espérance positive**,
  mais **6 % de risque est incompatible** avec une stratégie gagnante à 24-43 % : ses séries de 10
  pertes sont normales (à 24 %, 10 pertes d'affilée ont 6 % de chances sur chaque suite de 10
  trades, donc presque sûrement dans l'année), soit −46 % à 6 %. Les auteurs risquent **1 %**.
- **Le critère « plus de 50 % à 1:2 » exclut toutes les stratégies crédibles trouvées.** Le critère
  qu'utilisent les études : espérance positive sur une période jamais vue, Sharpe au-dessus de 1,
  pire recul supportable. C'est à Mongazi de trancher.

## Comment on les testerait (règle anti-triche)

1. Reproduire d'abord la période de l'article (2016-2023 pour l'ORB) : si on ne retrouve pas ses
   chiffres, notre code ou l'article a un défaut.
2. Juger ensuite **uniquement** sur la période que les auteurs n'ont jamais vue (ORB : mars 2023 →
   septembre 2026), au spread Deriv, avec les vrais lots, **par le moteur de l'agent**.
3. Ouvrir le verdict par les critères de Mongazi, puis par l'espérance et le pire recul.

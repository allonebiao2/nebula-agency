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

## RÉSULTATS DES TESTS (2026-09-18 soir, NAS100, règles des articles, rien d'optimisé)

⚠️ Simulateurs simples, **causaux par construction** (entrée au marché, une position à la fois), mais
**pas encore rejoués par un moteur d'agent** : ce sont des pistes au sens de la règle anti-triche.

| stratégie | période JAMAIS VUE par les auteurs | gagnants | gain / perte | résultat |
|---|---|---|---|---|
| **ORB 5 min** (`orb.py`) | mars 2023 → sept. 2026, Dukascopy | 24,8 % | 3,4 R / −1,0 R | **+0,078 R/trade**, 896 trades, non significatif (t ≈ 1) |
| ORB 5 min | 2024 → 2026, prix Deriv | 25,0 % | 3,3 / −1,0 | +0,059 R/trade, 683 trades |
| **Zone de bruit, version article** (`zone_bruit.py`) | mars 2024 → sept. 2026, Dukascopy | **39,5 %** | 1,76 | **+8,2 %/an**, Sharpe 0,59, recul 18,5 % |
| Zone de bruit, version article | idem, prix Deriv | **40,1 %** | 1,80 | **+10,6 %/an**, Sharpe 0,74, recul 17,7 % |
| Zone de bruit, stop courtier permanent | idem, prix Deriv | 25,6 % | 3,42 | +10,0 %/an, Sharpe 0,78, recul 14,5 % |
| Dernière demi-heure (`derniere_demi_heure.py`) | 2013 → 2026 | 48,3 % | 0,93 | **négatif** (−0,014 %/trade) |

- **Reproduction de l'ORB** sur la période de l'article (2016 → 2023-02) : 23,5 % de gagnants et
  +0,10 R, contre 24 % et +0,13 R publiés : **notre code retrouve l'article**. Avant l'article
  (2013-2015) : −0,13 R, parce qu'avec l'indice plus bas les stops étaient petits et le spread Deriv
  de 70 points coûtait 0,20 R.
- **Zone de bruit, 2013 → 2024 (période de l'article, sur un autre indice)** : 38 % de gagnants,
  +8,7 %/an, Sharpe 0,67, recul 32 %.
- ⚠️ Le « R » ne convient pas à la zone de bruit : son stop initial colle parfois au prix d'entrée
  et fait exploser les multiples (+24 637 R une année). Elle se mesure comme l'article : rendement
  du compte avec taille ajustée à la volatilité (2 % par jour, levier plafonné à 4).
- **Aucune ne remplit « plus de 50 % à 1:2 »**. La plus proche : zone de bruit, 40 % et 1:1,8.
- ⛔ **Avec 10 $, aucune n'est tradable à son niveau de risque** : 0,1 lot de NAS100 représente
  ~2 400 $ d'exposition, soit x240 sur 10 $, quand l'article travaille à x2 en moyenne. Il faudrait
  **~1 200 $** pour la zone de bruit et **~400 $** pour l'ORB à 1 % de risque.

## EUR/USD, ET LE CRITÈRE « PLUS DE 50 % À 1:2 » PARTOUT (2026-09-18, nuit)

Versions **déclarées avant tout résultat** (`eurusd_seances.py`) : 2 séances (Londres 3 h 00 → 11 h 59
New York, New York 8 h 00 → 16 h 59) × zone de bruit (article, stop courtier, crochet 1:2) et ORB
5 min (objectif 10 R, crochet 1:2) × 3 périodes. Stop jamais sous le minimum du courtier.

| EUR/USD | 2003-2015 | 2016-2026 | prix Deriv 2019-2026 |
|---|---|---|---|
| zone de bruit (article), Londres | **+8,4 %/an**, 35 % | −9,7 %/an, 31 % | −7,9 %/an, 31 % |
| zone de bruit (article), New York | +1,3 %/an, 35 % | −8,2 %/an, 34 % | −5,9 %/an, 34 % |
| ORB 10 R, Londres | +0,043 R (n.s.), 14 % | −0,041 R, 14 % | −0,061 R, 14 % |
| ORB 10 R, New York | −0,140 R, 12 % | −0,147 R, 12 % | −0,100 R, 13 % |
| **crochet 1:2, meilleur des 4** | 36 %, −0,014 R | 35 %, −0,067 R | 36 %, −0,044 R |

**Sur l'EUR/USD, rien ne tient depuis 2016**, ni sur Dukascopy ni sur Deriv. La seule ligne positive
(Londres 2003-2015) s'est retournée ensuite.

**Le crochet 1:2 (stop fixe, objectif 2 R), le critère de Mongazi, partout** :

| | gagnants | résultat |
|---|---|---|
| NAS100 zone de bruit, 2013-2026 | 39,7 % | +0,006 R (nul) |
| NAS100 zone de bruit, 2023-03 → 2026 (jamais vu) | 39,6 % | +0,039 R (t = 1,0) |
| NAS100 zone de bruit, Deriv 2024-2026 | 39,6 % | +0,018 R |
| NAS100 ORB, toutes périodes | 35 à 36 % | ≈ 0 |
| EUR/USD, 20 mesures | 33 à 36 % | toutes négatives |

**Aucune des 26 mesures « à 1:2 » ne dépasse 40 % de gagnants.** Le point mort à 1:2, coûts
compris, est vers 34-35 % : les meilleures versions sont à l'équilibre, pas au-dessus de 50 %.

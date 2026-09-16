# NEBULA Trader · Cahier des charges v2

> Version corrigée et chiffrée du cahier remis par Mongazi le 2026-09-16
> (`CAHIER-DES-CHARGES-v1.md`, conservé mot pour mot). **C'est ce document qui fait foi.**
>
> Légende : ✅ fait et testé · 🔧 corrigé (le chiffre qui le justifie est donné) ·
> ➕ à construire · ⛔ écarté (avec la raison) · 🎯 décision de Mongazi

L'esprit du v1 est gardé intact : **survivre d'abord**, walk-forward obligatoire, aucune
martingale, démo avant réel, auto-amélioration sous garde-fous. Ce qui change, ce sont les
**chiffres** : chacun a été rejoué sur les **436 trades hors échantillon réels** de la meilleure
stratégie (walk-forward 2011-2026, coûts Deriv mesurés, bootstrap de 20 000 tirages). Plusieurs
seuils ronds du v1 se déclenchaient sur la variance normale, ou se contredisaient entre eux.

---

## 0. Ce que les mesures ont changé

| Règle du v1 | Mesure sur les vrais trades | Règle v2 |
|---|---|---|
| PRO : arrêt total à −10 % avec 1 %/trade | touché **99 %** du temps sur 15 ans | 🔧 seuil **calibré au Monte Carlo** de la stratégie |
| PRO : levier ≤ x2 | EUR/USD H4 à 1 % : levier effectif **x2,2** médian, 42 % des signaux sous x2 | 🔧 plafond par profil ET par instrument, part des signaux bloqués affichée |
| BOOST : 3 %/trade, levier ≤ x5 | 3 % → **x6,6** ; 10 % → **x21,7** (0 % des signaux sous x5) | 🎯 **10 % maximum**, plafond de levier dérivé (x30 au plus) |
| Pause après 5 pertes d'affilée | arrive **97 %** du temps sur 100 trades à 40 % de réussite | 🔧 **CUSUM** : écart statistique à la distribution walk-forward |
| Viser 3 à 8 % par mois | exige **1,30 R** par trade (le KPI du v1, 0,2 R, donne 0,46 %/mois) | ⛔ aucun rendement visé, ni dans le code, ni dans la vente |
| 30 jours de paper trading | ≈ **2 trades** en H4 | 🔧 porte démo : 30 jours **ET** 30 trades **ET** conformité d'exécution |
| PF > 1,5 sur 90 jours glissants | ≈ 7 trades | 🔧 PF > 1,3 sur **≥ 50 trades** glissants, avec intervalle de confiance |
| Score de confiance ≥ 75/100 | jamais défini | 🔧 probabilité **calibrée** du méta-modèle, seuil choisi en walk-forward |
| Crypto (ccxt) et actions (yfinance) | 2e chemin d'exécution ; yfinance n'est pas une API de trading | 🎯 **EUR/USD et NAS100 seulement**, via MT5 |
| backtrader / vectorbt / Streamlit | notre moteur appelle **les mêmes verrous** que le live | ⛔ on garde moteur maison, FastAPI, SQLite |
| Kill switch « fermer si l'API tombe » | impossible de fermer quand l'API est tombée | 🔧 le **stop chez le courtier** est le coupe-circuit, plus un chien de garde |

### Ce que coûte le BOOST à 10 % (à afficher au moment de le choisir)

Avec la stratégie actuelle (+0,040 R par trade, **pas d'avantage prouvé**), sur ~29 trades par an :

| Risque par trade | P(perdre 20 %) sur 1 an | P(perdre 50 %) sur 1 an | pire 5 % des années | P(perdre 50 %) sur 3 ans |
|---|---|---|---|---|
| 1 % | 0 % | 0 % | −9 % | 0 % |
| 2 % | 8 % | 0 % | −18 % | 0 % |
| 3 % | 33 % | 0 % | −26 % | · |
| 5 % | 76 % | 3 % | −41 % | 35 % |
| **10 %** | **99 %** | **46 %** | **−67 %** | **92 %** |

Dix pertes d'affilée (normales pour une stratégie à 40 % de réussite) laissent 90 % du capital à
1 %, 74 % à 3 %, **35 % à 10 %**. Ces chiffres sont recalculés sur la stratégie active au moment du
choix : avec un avantage prouvé, ils s'améliorent.

---

## 1. Objectif global

| v1 | v2 |
|---|---|
| Analyser crypto, actions et forex | 🎯 **EUR/USD et NAS100**, par le terminal MT5 du courtier |
| Décisions 100 % autonomes | ✅ agent `live/agent.py`, huit verrous avant chaque ordre |
| S'auto-améliorer en continu | 🔧 **hors ligne** : walk-forward, champion/challenger, jamais d'apprentissage en direct |
| Modes PRO et BOOST | ➕ profils de risque, voir §2 |
| Rentabilité durable | ✅ doctrine ; ⛔ aucun avantage prouvé à ce jour, c'est le chantier prioritaire après ce cahier |
| (ajout) Être vendable | ✅ exécutable, licences, évaluation en démo ; ⛔ jamais de performance vendue sans historique réel vérifié |

---

## 2. Les deux profils

Un profil est un **jeu de plafonds**. Les plafonds écrits dans le code ne se desserrent pas
depuis un fichier : `PLAFOND_RISQUE_PAR_TRADE = 2 %` pour PRO, `PLAFOND_RISQUE_BOOST = 10 %` pour
BOOST.

### 🔵 PRO · capital protégé (profil par défaut)

| Paramètre | v1 | v2 | Pourquoi |
|---|---|---|---|
| Risque par trade | 1 % | ✅ 1 % (plafond code 2 %) | |
| Exposition simultanée | 4 % | 🔧 4 % **par facteur de risque** | EUR/USD et NAS100 partagent le facteur USD |
| R:R minimum | 1:2 | ✅ 2 (plancher des verrous 1,5) | |
| Perte max du jour | −3 % | ✅ −3 % | |
| Drawdown total | −10 % | 🔧 **Monte Carlo** : p99 × 1,2, borné à 35 % | −10 % touché 99 % du temps |
| Trades A+ (≥ 75/100) | | 🔧 probabilité calibrée ≥ seuil walk-forward | vague « méta-labeling » |
| Levier | x2 | 🔧 x3 sur EUR/USD, mesuré par instrument | x2 bloque 58 % des signaux EUR/USD |
| Trades par jour | 5 | 🔧 3 | 2,3 trades par MOIS en H4 : 3/jour n'est jamais une contrainte, 5 non plus |
| Objectif 3-8 %/mois | | ⛔ retiré | exige 1,30 R/trade |

### 🔴 BOOST · petit capital, croissance agressive

| Paramètre | v1 | v2 | Pourquoi |
|---|---|---|---|
| Comptes < 500 € | | 🎯 **n'importe quel capital** | décision de Mongazi |
| Risque par trade | 3 % | 🎯 **choisi jusqu'à 10 %**, probabilités affichées au choix | décision de Mongazi |
| Exposition | 9 % | 🔧 3 × le risque choisi, par facteur | cohérent avec 3 positions |
| R:R minimum | 1,5 | ✅ 1,5 | |
| Levier | x5 | 🔧 dérivé du risque, **x30 au plus** | x5 bloque 100 % des signaux à 10 % |
| Perte max du jour | −5 % | 🔧 max(−5 %, −1,5 × risque) | à 10 %/trade, −5 % tomberait au premier trade perdant |
| Drawdown total | −20 % → PRO | 🔧 **Monte Carlo** au risque choisi, puis retour en PRO | |
| Trades par jour | 10 | ✅ 10 | |
| Paliers anti-martingale | 3 → 2 → 1,5 → 1 % à chaque ×2 | ✅ gardé et étendu : risque choisi → … → 1 % à chaque ×2 | la bonne idée du v1 : moins de risque quand on a plus à perdre |
| Poche épargne | +50 % → retirer 25 % des gains | 🔧 **verrouillés hors dimensionnement** | MT5 n'a pas d'API de retrait ; le capital verrouillé n'est plus jamais risqué |
| Activation en réel | après 60 jours de PRO rentable | ✅ **gardé tel quel** | règle de phase 5 du v1 ; en démo, BOOST est libre |
| Stratégies prioritaires | momentum, cassure | ➕ quand elles auront prouvé un avantage | |

---

## 3. Gestion du risque · règles non négociables

| # | v1 | v2 |
|---|---|---|
| 1 | Stop obligatoire, niveau technique | ✅ stop déposé chez le courtier, position **relue** (sans stop, fermée) ; ➕ stop de **structure** (dernier creux/sommet) borné par l'ATR (verrou 2 : 0,5 à 2 ATR) |
| 2 | Taille = capital × risque / (stop × valeur du point) | ✅ `noyau/risque.dimensionner`, arrondi vers le bas, compte cent géré |
| 3 | Pas de moyenne à la baisse | ✅ interdit par conception, non réglable |
| 4 | TP partiel 50 % à 1 R | 🔧 **option**, activée seulement si le walk-forward l'améliore ; impossible sous 0,02 lot |
| 5 | Suiveur dès +1 R | ✅ jamais élargi |
| 6 | Pas de 2e position même actif même sens | ✅ 1 position par instrument |
| 7 | Pas de trade ±15 min des annonces | ✅ −30/+15 min réglables, calendrier indisponible = abstention |
| 8 | Kill switch : fermer tout si bug ou API down | 🔧 stop chez le courtier + **chien de garde** : ordres rejetés en série, position sans stop, API muette, équité −X % en 1 h → plus d'entrée, alerte ; fermeture sur arrêt d'urgence explicite |
| 9 | Max trades/jour 5 PRO, 10 BOOST | 🔧 3 PRO, 10 BOOST |
| 10 | Pas de trade si spread trop large | ✅ verrou 8 (seuil absolu et 3 × le spread habituel) |
| + | Martingale, grille, stop élargi | ✅ interdits par conception |
| + | Relever un risque en drawdown | ✅ alerte journalisée ; l'agent ne peut qu'en faire la PROPOSITION |

---

## 4. Auto-amélioration

| v1 | v2 |
|---|---|
| Journal complet de chaque trade | ✅ SQLite : décisions **et refus**, contexte au moment T, verrous, R ; ➕ symbole, profil, glissement réel |
| Analyse hebdomadaire | ➕ rapport par stratégie, régime, heure, jour, glissement réel contre modèle ; page « Évolution », lisible par l'agent |
| Walk-forward obligatoire | ✅ 4 ans → 1 an, SQN, capital reporté ; ➕ Monte Carlo joint à chaque rapport |
| Modification déployée seulement si le walk-forward s'améliore | ✅ règle ; ➕ **garde contre les tests multiples** : chaque variante essayée est comptée, le seuil de significativité se durcit avec leur nombre |
| Score vivant par stratégie | 🔧 espérance a posteriori **rétrécie vers zéro** (on ne croit pas 10 trades chanceux) |
| Plus de capital aux stratégies en forme | 🔧 allocation proportionnelle à l'espérance rétrécie, plafonnée par le profil |
| Pause après 5 pertes ou −10 % sur la poche | 🔧 **CUSUM** contre la distribution walk-forward, ou drawdown au-delà du p95 Monte Carlo |
| 30 jours de paper trading rentable | 🔧 **porte démo** : ≥ 30 jours, ≥ 30 trades, 100 % d'ordres avec stop, glissement ≤ modèle, CUSUM non déclenché. Le compte démo MT5 teste le **vrai** chemin d'exécution ; l'avantage, lui, se prouve en walk-forward |

---

## 5. Stack

| v1 | v2 |
|---|---|
| Python | ✅ |
| ccxt, yfinance, pandas | ⛔ MT5 (historique lu par année, 20 ans) ; numpy |
| backtrader / vectorbt | ⛔ moteur maison : mêmes verrous que le live, coûts réels, entrée à l'ouverture suivante |
| scikit-learn | ➕ pour le méta-modèle (disque à surveiller) |
| cron / APScheduler | ✅ boucle de l'agent + rapport hebdomadaire planifié dans l'agent |
| Logs JSON + Streamlit | ✅ journal SQLite + interface FastAPI 8 pages (Streamlit ne s'empaquette pas proprement) |
| Telegram | ➕ |
| Clés en variables d'environnement | ✅ + coffre **DPAPI** pour le produit installé ; MT5 n'a pas de droits « trade only », le mot de passe principal reste sur la machine |

---

## 6. Phases, réalignées sur l'existant

| Phase v1 | État v2 |
|---|---|
| 1 · Backtest, 3 stratégies, walk-forward 3 ans | ✅ moteur, 2 stratégies, walk-forward **15 ans** (3 ans ≈ 70 trades : trop peu) · ⛔ aucun avantage prouvé |
| 2 · Paper trading 30 jours | 🔧 agent en observation sur le démo Deriv, puis **mode démo** jusqu'à la porte |
| 3 · Self-learning | ➕ vague 3 |
| 4 · Réel PRO sur 100-200 € | 🔧 exige **compte cent** (sur compte standard, rien ne passe sous 250 $), licence, porte démo franchie |
| 5 · BOOST si phase 4 rentable 60 jours | ✅ gardé tel quel pour le réel |

## 7. Règles d'or

Écrites en tête des modules et dans `DOCTRINE.md` :
« Survivre d'abord, performer ensuite » · « Un trade sans stop n'existe pas » · « Le backtest ment,
le walk-forward vérifie, le marché décide » · « Le bot ne cherche pas à avoir raison, il cherche à
être rentable » · « Aucune modification live sans validation sur compte démo » · **ajoutées** :
« Un seuil se calibre sur la distribution de la stratégie, jamais en chiffre rond » · « Aucun
rendement promis ».

## 8. Indicateurs de réussite

| v1 | v2 | Pourquoi |
|---|---|---|
| PF > 1,5 sur 90 jours | PF > 1,3 sur **≥ 50 trades** glissants | 90 jours ≈ 7 trades |
| DD max < 15 % | DD réel **sous le p95 du Monte Carlo** de la stratégie | un seuil fixe ignore le risque choisi |
| Espérance > 0,2 R | espérance hors échantillon **> 0,15 R, borne basse de l'IC > 0**, sur ≥ 100 trades | un point sans intervalle ne prouve rien |
| Réussite > 40 % | ⛔ remplacé par l'espérance | la réussite seule ne dit rien sans le ratio |
| Aucun jour < −3 % (PRO) | ✅ disjoncteur du jour | |
| 60 % des mois positifs | 🔧 mesuré seulement quand ≥ 8 trades par mois | à 2,3 trades/mois, un mois est du bruit |
| (ajout) Sharpe | Sharpe hors échantillon > 0,7 | |

---

## 9. Intégration, par vagues

Chaque vague : QC vert avec témoins, captures 1440 et 390, paquet reconstruit, push.

1. **Profils PRO / BOOST** : plafonds du code, paliers anti-martingale, poche épargne, verrou
   de levier effectif, trades/jour et R:R par profil, sélecteur dans l'interface (BOOST confirmé
   avec ses probabilités), colonnes symbole et profil dans le journal.
2. **Monte Carlo** : `backtest/montecarlo.py`, seuils de drawdown calibrés proposés, alerte du
   videur sous le p95, affichage Stratégies et BOOST, outil de lecture pour l'agent.
3. **Auto-surveillance** : CUSUM par stratégie, rapport hebdomadaire et page « Évolution », porte
   démo, chien de garde, glissement mesuré par ordre.
4. **EUR/USD + NAS100** : alias du symbole vérifiés chez Deriv, boucle multi-instruments,
   exposition par facteur, historique, walk-forward et Monte Carlo par instrument.

**Ensuite** : filtre D1, stratégies momentum, range et cassure de structure, indicateurs RSI,
MACD, Bollinger et structure HH/HL, garde contre les tests multiples, méta-labeling, Telegram.

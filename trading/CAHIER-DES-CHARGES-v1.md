# 🤖 AGENT DE TRADING AUTONOME AUTO-AMÉLIORANT — CAHIER DES CHARGES COMPLET

> Texte remis par Mongazi le 2026-09-16, conservé **mot pour mot**. La version corrigée et
> intégrée à NEBULA Trader est `CAHIER-DES-CHARGES.md`.

## OBJECTIF GLOBAL
Construire un agent de trading algorithmique capable de :
1. Analyser les marchés en temps réel (crypto + actions + forex selon dispo API)
2. Prendre des décisions de trading 100% autonomes selon des règles strictes
3. S'AUTO-AMÉLIORER en continu via machine learning + backtesting itératif
4. Fonctionner en 2 modes : MODE PRO (capital protégé, risque minimal) et MODE BOOST (petit capital, croissance agressive contrôlée)
5. Viser la rentabilité durable sur le long terme, PAS les gains rapides non durables

---
## 1. ARCHITECTURE GÉNÉRALE (modulaire)

### Modules obligatoires :
- **MODULE 1 — INGESTION DE DONNÉES** : connexion APIs (Binance/ccxt pour crypto, yfinance/yahoo_finance pour actions, autres selon dispo). Récupération OHLCV multi-timeframes (1H, 4H, D, W), carnet d'ordres, sentiment news si dispo.
- **MODULE 2 — MOTEUR D'ANALYSE** : indicateurs techniques (EMA, RSI, MACD, ATR, Bollinger, Volume Profile, structure de marché : HH/HL/LH/LL), détection de tendance multi-timeframe, niveaux clés (supports/résistances), divergence RSI, analyse de la volatilité (ATR).
- **MODULE 3 — MOTEUR DE DÉCISION (STRATÉGIES)** : chaque stratégie = classe indépendante avec entrées/sorties/stops codés en dur. Minimum 5 stratégies au départ (trend-following, mean-reversion, breakout, range, momentum).
- **MODULE 4 — GESTION DU RISQUE** : cœur du système, NON contournable (voir section 3).
- **MODULE 5 — EXÉCUTION** : envoi d'ordres, gestion des erreurs, retry logic, vérification de l'exécution, gestion du slippage.
- **MODULE 6 — SELF-LEARNING ENGINE** : voir section 4.
- **MODULE 7 — MONITORING & LOGGING** : dashboard, alertes Telegram/Discord, journal de chaque décision avec raisonnement.
- **MODULE 8 — BACKTESTING ENGINE** : backtests réalistes (frais, slippage, latence simulée) + walk-forward analysis + paper trading obligatoire avant tout déploiement réel.

---
## 2. LES 2 MODES DE FONCTIONNEMENT

### 🔵 MODE PRO — "Capital Protégé"
- Risque par trade : MAX 1% du capital
- Exposition totale simultanée : MAX 4% du capital
- Ratio R:R minimum : 1:2 (refuser tout trade en dessous)
- Drawdown journalier max : -3% → arrêt automatique jusqu'au lendemain
- Drawdown total max : -10% → arrêt complet + revue manuelle obligatoire
- Préférence : trades A+ uniquement (score de confiance ≥ 75/100)
- Levier : MAX x2, idéalement x1
- Frais et liquidité : uniquement actifs liquides, spreads faibles
- Objectif : capital preservation d'abord, croissance composée ensuite (visée 3-8%/mois)

### 🔴 MODE BOOST — "Petit Capital Aggressif"
- Pour comptes < 500€ uniquement (paramètre configurable)
- Risque par trade : MAX 3% du capital
- Exposition totale : MAX 9%
- Ratio R:R minimum : 1:1.5
- Levier : MAX x5 (jamais plus)
- Drawdown journalier max : -5% → stop
- Drawdown total max : -20% → stop + réinitialisation en mode PRO
- Rotation plus rapide, stratégies momentum/breakout prioritaires
- Objectif : croissance rapide mais SANS ruin — règle de "bankroll building" : à chaque palier ×2 du capital, réduire automatiquement le risque par paliers (3% → 2% → 1.5% → 1%)
- Règle de sécurisation : à +50% de gain, retirer 25% des profits vers une "poche épargne" hors risque

---
## 3. GESTION DU RISQUE — RÈGLES NON NÉGOCIABLES (codées en dur, non désactivables)

1. Stop-loss OBLIGATOIRE sur chaque position, positionné sur un niveau technique (jamais arbitraire)
2. Position sizing automatique : taille = (capital × risque%) / (distance au stop × valeur du pip/lot)
3. Jamais de moyennage à la baisse (ajouter à une position perdante interdit)
4. Take-profit partiel possible : fermer 50% à 1:1, laisser courir le reste avec trailing stop
5. Trailing stop activé dès que le trade atteint +1R
6. Pas de nouvelle position sur le même actif dans la même direction
7. Pas de trading 15 min avant/après les annonces économiques majeures (NFP, CPI, FOMC, taux) — calendrier économique intégré
8. KILL SWITCH global : si bug, API down, ou comportement anormal → fermeture douce de toutes les positions et arrêt du bot
9. Limite de trades par jour (max 5 en PRO, max 10 en BOOST) contre le sur-trading
10. Pas de trade si spread > seuil défini ou liquidité insuffisante

---
## 4. SELF-LEARNING ENGINE (cœur de l'auto-amélioration)

### Boucle d'apprentissage continue :
1. **JOURNAL COMPLET** de chaque trade : timestamp, actif, timeframe, stratégie, raison d'entrée, contexte marché (volatilité, tendance, indicateurs au moment T), émotion simulée = score de confiance, résultat en R
2. **ANALYSE HEBDOMADAIRE AUTOMATIQUE** :
   - Win rate, profit factor, expectancy, max drawdown par stratégie
   - Identification des conditions gagnantes/perdantes (ex: "stratégie X gagne en tendance forte mais perd en range")
   - Détection des patterns : heures rentables, jours rentables, actifs rentables, régimes de marché favorables
3. **OPTIMISATION CONTRÔLÉE** :
   - Walk-forward analysis OBLIGATOIRE (jamais d'overfitting : données out-of-sample jamais touchées pendant l'optimisation)
   - Paramètres optimisés sur période N, VALIDÉS sur période N+1. Si validation échoue → rejet
   - Théorème : si une modification améliore le backtest mais pas le walk-forward → elle n'est PAS déployée
4. **SYSTEME DE SCORING DES STRATÉGIES** :
   - Chaque stratégie a un score vivant mis à jour après chaque trade
   - Allocation de capital dynamique : plus de capital aux stratégies en forme, réduction automatique des stratégies en drawdown
   - Une stratégie passe en "pause automatique" après 5 pertes consécutives ou -10% sur sa poche
5. **PAPER TRADING GATE** : toute nouvelle stratégie ou modification DOIT passer 30 jours de paper trading rentable avant d'obtenir du capital réel

---
## 5. STACK TECHNIQUE RECOMMANDÉ
- Langage : Python
- Data : ccxt (crypto), yfinance ou API broker (actions), pandas/polars
- Backtest : backtrader OU vectorbt OU backtesting.py
- ML : scikit-learn au départ (gradient boosting pour scorer les trades), éventuellement reinforcement learning en v2
- Scheduling : cron ou APScheduler
- Monitoring : logging structuré (JSON) + dashboard Streamlit simple
- Alertes : Telegram Bot (entrées, sorties, erreurs, résumé quotidien)
- Sécurité : clés API en variables d'environnement, jamais en dur, permissions API en "trade only" (pas de retrait)

---
## 6. LIVRABLES À PRODUIRE (ordre de développement)

1. **PHASE 1** : Backtesting engine + 3 stratégies de base + analyse walk-forward sur 3 ans de données (BTC, ETH, + 2 actions). LIVRABLE : rapport de performance par stratégie avec métriques complètes (win rate, PF, max DD, Sharpe, expectancy)
2. **PHASE 2** : Paper trading bot complet avec gestion du risque intégrée et journal. LIVRABLE : 30 jours de paper trading documentés
3. **PHASE 3** : Self-learning engine (scoring, analyse hebdo, pause auto des stratégies). LIVRABLE : rapport d'auto-analyse après 2 semaines
4. **PHASE 4** : Déploiement réel avec MODE PRO uniquement sur petit capital réel (100-200€) + monitoring Telegram
5. **PHASE 5** : Activation MODE BOOST si PHASE 4 rentable après 60 jours minimum

---
## 7. RÈGLES D'OR ÉCRITES EN DUR DANS LE CODE (commentaires obligatoires)

- "Survivre d'abord, performer ensuite"
- "Un trade sans stop n'existe pas"
- "Le backtest ment, le walk-forward vérifie, le marché décide"
- "Le bot ne cherche pas à avoir raison, il cherche à être rentable"
- "Aucune modification live sans validation paper trading"

---
## 8. MÉTRIQUES DE SUCCÈS (KPIs)
- Profit Factor > 1.5 sur rolling 90 jours
- Max drawdown < 15%
- Expectancy > 0.2R par trade
- Win rate > 40% (avec ratio 1:2)
- Aucun jour > -3% (mode PRO)
- Cohérence : 60% des mois positifs minimum en mode PRO


3 conseils avant de l'envoyer à Claude Code :
1. Démarre par la Phase 1 uniquement — dis à Claude de faire le backtest d'abord. Ne lui demande JAMAIS de connecter de l'argent réel dans un premier temps.
2. Exige le paper trading de 30 jours minimum avant tout réel. C'est la différence entre un bot et un joueur de casino automatisé.
3. L'auto-amélioration avec ML est risquée si mal faite (overfitting) — c'est pourquoi la spec impose le walk-forward et le paper trading gate. Ne les retire pas, ce sont tes garde-fous.

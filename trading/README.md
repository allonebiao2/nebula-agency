# NEBULA TRADER

Robot de trading EUR/USD, conçu pour trois objectifs, dans cet ordre :

1. **Être rentable** sur une seule paire, chez Mongazi
2. **S'améliorer tout seul** à partir de ses propres erreurs, sans se suicider
3. **Être vendable** — donc tourner chez n'importe quel courtier MT5

L'ordre compte : l'objectif 3 **découle** du 1. Un EA ne se vend pas sur un
backtest, il se vend sur un historique réel vérifié. Il faut donc gagner
d'abord, petit, pendant des mois.

---

## État au 2026-09-16

### Ce qui est construit et testé

| Module | Rôle | Test |
|---|---|---|
| `config.toml` | tous les paramètres de risque, en amont, commentés | — |
| `noyau/config.py` | **le videur** : refuse de démarrer sur un réglage dangereux | 6 refus vérifiés |
| `noyau/risque.py` | dimensionnement dérivé du stop + invariant du stop | viabilité mesurée sur 6 tailles de compte |
| `noyau/plan.py` | `PlanDeTrade` obligatoire + **les 8 verrous** | 9 scénarios + 4 plans impossibles |
| `noyau/courtier.py` | adaptateur multi-courtiers : tout se lit, rien ne se suppose | bloqué (voir ci-dessous) |
| `DOCTRINE.md` | les principes de trading traduits en mécanismes exécutables | — |

```bash
python trading/noyau/config.py          # la posture de risque en clair
python trading/noyau/risque.py          # le dimensionnement, sur 6 tailles de compte
python trading/outils/demo_verrous.py   # voir le bot refuser 9 trades
python trading/outils/profil_courtier.py # la carte d'identité du courtier
```

### ⛔ Ce qui bloque : le pont Python ↔ MT5

`mt5.initialize()` renvoie **`(-6, 'Terminal: Authorization failed')`**, sur les
deux courtiers installés. Rien ne peut lire les vraies spécifications du
contrat tant que ce n'est pas levé, et **sans elles tout dimensionnement serait
une supposition** — donc rien n'est câblé en dur en attendant.

**Éliminé avec certitude** (mesuré, pas supposé) :

- ❌ pas un problème d'identifiants — les comptes se connectent, titres visibles
- ❌ pas le chemin du terminal — échec identique avec et sans `path`
- ❌ pas le bac à sable — échec identique hors bac à sable
- ❌ pas Git Bash — échec identique depuis PowerShell
- ❌ pas la version du paquet — testé en 5.0.5735 **et** 5.0.6180
- ❌ pas propre à Deriv — **Exness échoue exactement pareil**
- ❌ pas l'état du terminal — terminal fermé, relancé seul, laissé connecter

**Corrigé au passage** (c'était nécessaire, ça n'a pas suffi) : les deux
terminaux avaient `[Experts] Enabled=0` et **`Api=0`**, soit l'accès API externe
désactivé. Passés à `1`. `AllowDllImport` **laissé à 0** : le pont Python n'en a
pas besoin et l'activer desserrerait la sécurité pour rien.
Sauvegardes : `common.ini.avant-nebula` dans chaque dossier de terminal.

**Ce qui reste à essayer, par ordre de probabilité :**

1. **Le bouton AutoTrading dans MT5** — ouvrir le terminal, vérifier
   *Outils → Options → Expert Advisors*, et surtout que le bouton
   **AutoTrading de la barre d'outils est VERT**. Le fichier de configuration
   dit `Enabled=1`, mais l'interface peut exiger une confirmation.
2. **Windows Defender** — protection temps réel active, et ce PC a déjà un
   précédent documenté (Defender bloquant Chrome headless pour Remotion).
   Ajouter une exclusion sur les dossiers MT5 et sur Python. Demande les droits
   administrateur.
3. **Mettre à jour le terminal** — *Aide → Vérifier les mises à jour*.
   Build actuel 5830, le paquet Python est en 6180.

---

## Les décisions déjà prises

| Décision | Valeur | Pourquoi |
|---|---|---|
| Paire | **EUR/USD** | spread le plus serré, liquidité maximale, 25 ans d'historique |
| Unité de temps | **H4**, filtre **D1** | le coût de transaction y pèse 0,02 R contre 0,19 R en M5 |
| Risque par trade | **1 %**, plafond code 2 % | à 5 %, une série de 10 pertes coûte 40 % du compte |
| Stop | **2 × ATR(14)** | un stop en pips fixes ne veut pas dire la même chose en août et un jour de FOMC |
| Objectif | **2 R**, plancher 1,5 R | équilibre atteint dès 33 % de réussite |
| Hébergement | PC de Cotonou, VPS plus tard | **d'où** : stops toujours déposés côté serveur |
| Apprentissage | **meta-labeling**, hors ligne, champion/challenger | le signal FX est à ~5 % : un réseau lâché sur des prix bruts mémorise le bruit |
| Courtier | Deriv (compte démo) | choisi par Mongazi ; le code reste agnostique |

### ⚠️ La viabilité du capital, mesurée

Avec un stop H4 de 70 pips et 1 % de risque, sur un compte standard
(lot minimum 0,01, valeur du point 1 $) :

| Capital | Verdict |
|---|---|
| 50 – 500 $ | **tous les trades refusés** — le lot minimum risque déjà 7 $ |
| 700 $ | premier capital viable à 1 % |
| 1 000 $ | 0,01 lot, risque 0,70 % |
| 5 000 $ | 0,07 lot, risque 0,98 % |

Le code **refuse** au lieu de dépasser « juste cette fois ». Trois sorties
possibles : un compte **cent** (lot 100× plus petit), accepter 2 % (plancher
~350 $), ou attendre d'avoir le capital. **À trancher par Mongazi.**

---

## Ce qui reste à construire

- [ ] **Données** : téléchargement de l'historique H4/D1, cache local, contrôle des trous
- [ ] **Backtest** : moteur barre par barre, **coûts réels facturés** (spread médian mesuré, commission, slippage, swap)
- [ ] **Métriques** : espérance, profit factor, Sharpe, drawdown max, MAR, et surtout **taille d'échantillon**
- [ ] **Stratégies candidates** : cassure Donchian + filtre D1 · retour à la moyenne avec filtre de régime · momentum D1
- [ ] **Walk-forward** : la seule validation acceptée
- [ ] **Journal SQLite** : le contexte complet de chaque trade = le jeu de données d'entraînement
- [ ] **Meta-labeling** : le modèle qui filtre les signaux de la règle primaire
- [ ] **Champion / challenger** : promotion seulement sur gain hors échantillon
- [ ] **Exécution live** : ordres avec SL/TP côté serveur, reprise d'état après coupure
- [ ] **Telegram** : alertes + **commandes depuis le portable** (état, pause, tout fermer)
- [ ] **Export ONNX + EA MQL5** : le chemin de la revente

---

## Architecture visée, pour la revente

Un bot Python ne se vend pas à des traders retail : ils ne veulent pas
installer Python. Le canal réel est le **MQL5 Market** (un `.ex5` qu'on glisse
sur un graphique, licence et anti-copie gérés par MetaQuotes).

MT5 embarque un **runtime ONNX** depuis 2023. D'où :

```
   Python (chez nous)                ONNX              MQL5 (chez le client)
   ──────────────────                ────              ─────────────────────
   données · backtest          →   modele.onnx   →     EA .ex5
   walk-forward · entraînement                          même modèle,
   champion / challenger                                mêmes verrous
```

**La doctrine, les verrous et le dimensionnement doivent exister des deux côtés
à l'identique.** C'est pour cela qu'ils sont écrits comme des règles pures, sans
dépendance : ils se portent en MQL5 presque ligne pour ligne.

⚠️ Trois contraintes commerciales : le MQL5 Market **déclasse** les EA à
martingale et à grille (les nôtres sont interdits par conception, c'est un
argument de vente) · **ne jamais promettre un rendement** dans une fiche produit
· un EA se vend sur un **historique réel vérifié**, pas sur un backtest.

---

## Les règles qui ne se négocient pas

1. **Aucune valeur de courtier écrite en dur.** Symbole, décimales, taille de
   contrat, lot minimum, valeur du point, mode de remplissage, stops level,
   fuseau du serveur : tout se lit. Douze choses changent d'un courtier à
   l'autre, chacune casse un bot qui les suppose.
2. **Tout ordre part avec son stop déposé chez le courtier.** Le bot tourne sur
   un PC à Cotonou : une coupure ne doit jamais laisser une position nue.
3. **Un stop ne se déplace que vers le profit.** Jamais élargi, par personne,
   pas même par un module du bot.
4. **Jamais d'apprentissage en direct.** Réentraînement hors ligne, walk-forward,
   promotion seulement sur gain hors échantillon.
5. **Ni martingale, ni moyenne à la baisse, ni grille.** Non implémentés.
6. **Le backtest facture les coûts réels.** Un backtest sans coûts est une
   publicité, pas une mesure.
7. **Aucun chiffre de performance annoncé avant d'avoir été mesuré.**

Détail des principes et de leur traduction en code : **`DOCTRINE.md`**.

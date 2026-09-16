# 2026-09-16 — NEBULA TRADER : le socle d'un robot de trading EUR/USD

Nouveau chantier, à la demande de Mongazi. Trois objectifs, énoncés dans cet
ordre au fil de la session :

1. **Être rentable** sur une seule paire (EUR/USD), chez Mongazi
2. **S'améliorer tout seul**, apprendre de ses erreurs, « super agent » et non
   simple bot
3. **Être vendable** — donc tourner chez **n'importe quel courtier MT5**

⚠️ **L'ordre compte et il a été dit** : l'objectif 3 **découle** du 1. Un EA ne
se vend pas sur un backtest, il se vend sur un historique réel vérifié
(signal MQL5 / Myfxbook). Il faut donc gagner d'abord, petit, pendant des mois.

---

## Les décisions prises

| Décision | Valeur | Pourquoi |
|---|---|---|
| Paire | **EUR/USD** | spread le plus serré, liquidité maximale |
| Courtier | **Deriv** (choisi par Mongazi, après avoir envisagé Exness) | le code reste agnostique |
| Unité de temps | **H4**, filtre **D1** | *décidé par moi, sur mesure* : le coût pèse 0,02 R en H4 contre 0,19 R en M5 |
| Hébergement | PC de Cotonou + suivi téléphone, VPS quand ça paiera | **d'où** : stops toujours déposés côté serveur |
| Risque | **1 %** par trade, plafond **2 %** écrit dans le code | à 5 %, une série de 10 pertes coûte 40 % du compte |
| Apprentissage | **meta-labeling**, hors ligne, champion/challenger | le signal FX est à ~5 % : un réseau sur prix bruts mémorise le bruit |

---

## Ce qui a été construit (détail et pourcentages : `trading/JOURNAL.md`)

- **`config.toml`** : tous les paramètres de risque en amont, commentés.
- **`noyau/config.py`** — *le videur* : refuse de démarrer sur un réglage
  dangereux. 6 refus vérifiés (risque à 5 %, martingale, apprentissage en
  direct, stops non déposés, réel sans plafond, disjoncteurs inversés).
- **`noyau/risque.py`** : dimensionnement dérivé du stop, **arrondi vers le
  bas**, refus si le lot minimum dépasse le risque autorisé, et l'invariant du
  stop (il ne se déplace que vers le profit).
- **`noyau/plan.py`** : `PlanDeTrade` obligatoire + **8 verrous** (les 6
  questions de Mongazi + 2 de la maison).
- **`noyau/courtier.py`** : adaptateur multi-courtiers, **12 valeurs lues**.
- **`backtest/`** : coûts réels, métriques (dont taille d'échantillon et
  intervalle de Wilson), moteur barre par barre.
- **`strategies/`** : indicateurs numpy, contrat `Strategie`, cassure Donchian.
- **`noyau/donnees_deriv.py`** : historique par l'API publique Deriv.
- **`DOCTRINE.md`** : les principes traduits en mécanismes exécutables.

---

## Les quatre corrections apportées au document de trading de Mongazi

Il avait collé une liste de principes (gestion du risque, analyse, plan écrit,
journal, psychologie, 6 questions). Le fond était juste ; quatre points ont dû
être corrigés, dont deux coûtent de l'argent pris au pied de la lettre :

1. **« 1:2 à 40 % de réussite est profitable » est vrai HORS COÛTS**, et les
   coûts étaient absents de tout le texte. Même système : **+0,18 R en H4,
   +0,01 R en M5**. Le spread n'a pas bougé, c'est R qui a rétréci. C'est ce
   calcul qui a décidé de l'unité de temps.
2. **« Ne jamais déplacer un stop-loss » est faux tel quel** : c'est *ne jamais
   l'ÉLARGIR*. Le resserrer est le mécanisme même du suiveur. Appliquée
   littéralement, la règle interdirait le trailing.
3. **« Quelle est mon émotion ? » n'a pas de sens pour un bot**, mais se
   traduit exactement : la **dérive d'état** (série en cours, spread anormal,
   volatilité hors plage, confiance du modèle, régime).
4. **Le risque psychologique ne disparaît pas, il se déplace sur l'opérateur** —
   angle mort du document, et propre aux systèmes automatisés. Les 5 gestes qui
   tuent un bot rentable : couper pendant une série de pertes, monter le risque
   après un drawdown, désactiver un disjoncteur, ré-optimiser après chaque
   perte, reprendre une position en manuel.

**Manquaient aussi** : la taille d'échantillon, le stop temporel, le fait qu'un
stop soit une instruction et pas une garantie, et le sur-apprentissage.

---

## Les défauts trouvés en mesurant

### ⛔ Le disjoncteur de série noire se verrouillait POUR TOUJOURS
Le compteur de pertes consécutives ne retombe que sur un gain, et aucun gain
n'est possible tant que les entrées sont bloquées. **Mesuré : le bot cessait de
trader en octobre 2021 sur un jeu allant à fin 2024.** Le `config.toml`
prévoyait une pause de 24 h, le moteur ne l'avait jamais implémentée. En
production, ça se serait vu comme « le bot ne trade plus », sans explication.

⚠️ **Trouvé parce que le nombre de trades n'était PAS MONOTONE** dans un
balayage (123 à 12 barres, 25 à 18, 64 à 48). Un résultat non monotone là où la
physique impose la monotonie est un défaut d'instrument : *vérifier sa sonde
avant d'accuser le produit.*

### ⚠️ Le stop temporel étranglait les trades
À 12 barres il était le mode de sortie **principal** (83 sur 123) au lieu d'être
un filet. Porté à **36**, sur un argument de conception — pas sur une
performance mesurée sur données synthétiques, ce qui aurait été du
sur-apprentissage sur du bruit inventé.

### ⚠️ `\t` dans un chemin Windows écrit par heredoc
`C:\...\terminal64.exe` est ressorti avec une **tabulation** à la place de
`\t`. Le chemin était cassé et se lisait mal à l'œil. Écrire les chemins
Windows par script Python, jamais par heredoc shell.

---

## ⛔ Le pont Python ↔ MT5 refuse : `-6 Authorization failed`

Sur **Deriv ET Exness**. Éliminé en mesurant, pas en supposant :

- ❌ identifiants — les comptes se connectent, titres de fenêtre visibles
- ❌ chemin du terminal — échec identique avec et sans `path`
- ❌ bac à sable — échec identique hors bac à sable
- ❌ Git Bash — échec identique depuis PowerShell
- ❌ version du paquet — testé en 5.0.5735 **et** 5.0.6180
- ❌ courtier — les deux échouent pareil
- ❌ état du terminal — fermé, relancé seul, laissé se connecter
- ❌ bouton « Trading Algo » — **vérifié vert par Mongazi**

**Corrigé en route sans que ça suffise** : les deux terminaux avaient
`[Experts] Enabled=0` et **`Api=0`** (accès API externe désactivé). Passés à `1`.
`AllowDllImport` **laissé à 0** : le pont n'en a pas besoin et l'activer
desserrerait la sécurité pour rien. Sauvegardes `common.ini.avant-nebula`.

**Reste à essayer** : la connexion par **identifiants explicites**
(`mt5.initialize(login=, password=, server=)`), qui est de toute façon la bonne
architecture pour un bot multi-courtiers. En attente du mot de passe.

---

## ✅ Le déblocage : l'API publique de Deriv donne de vraies bougies

Découvert le 2026-09-16 : **`ticks_history` répond sans aucun jeton**.
`wss://ws.derivws.com/websockets/v3?app_id=1089`, symbole `frxEURUSD`,
`style: candles`, `granularity: 14400`.

Résultat : **1 555 barres H4 réelles, 0 bougie incohérente**, les 2 seuls trous
étant Noël et le Nouvel An.

⛔ **MAIS : Deriv plafonne à UN AN**, quelle que soit l'unité de temps
(D1 260 barres, H4 1 555, H1 3 471, M15 0,1 an). À ~3 trades/mois, ça fait ~35
trades — **très en dessous des 100** nécessaires pour qu'un taux de réussite
veuille dire quelque chose. L'historique long viendra du terminal MT5, ou d'une
source tierce (⏳ Dukascopy essayé le 2026-09-16 : 404/503 sur le format d'URL
des bougies mensuelles, à creuser).

---

## ⚠️ La viabilité du capital, mesurée

Avec un stop H4 de 70 pips et 1 % de risque, lot minimum 0,01 :

| Capital | Verdict |
|---|---|
| 50 – 500 $ | **tous les trades refusés** — le lot minimum risque déjà 7 $ |
| ~700 $ | premier capital viable à 1 % |
| ~350 $ | viable seulement à 2 % (plafond du code) |

Le code **refuse** au lieu de dépasser « juste cette fois ». ⏳ **Mongazi doit
trancher** : compte cent, 2 %, ou attendre le capital.

---

## 🔐 Sécurité — deux incidents le même jour

1. **Un jeton collé en clair dans la conversation**
   (`pat_…`, 64 hex). Testé : **`InvalidToken`**, et le format ne correspond pas
   à Deriv (qui utilise `a1-…`). Il appartient donc à un autre service.
   ⛔ **À révoquer quand même** : il a été exposé.
2. **Mongazi a demandé s'il devait coller son mot de passe MT5 dans le chat.**
   Réponse : **non**. Il va dans `secrets/mt5.env` (ignoré par git), rempli à la
   main. Un mot de passe n'entre jamais dans une conversation.

⚠️ **Le dépôt est PUBLIC** : `secrets/` est la seule place acceptable, et le
numéro de compte a été retiré du `README.md` avant publication.

---

## Pour la revente : l'architecture ONNX

Un bot Python ne se vend pas à des traders retail (ils n'installeront pas
Python). Le canal est le **MQL5 Market** : un `.ex5` qu'on glisse sur un
graphique, licence et anti-copie gérées par MetaQuotes.

MT5 embarque un **runtime ONNX** depuis 2023 → on entraîne en Python, on exporte
en ONNX, et **l'EA MQL5 fait l'inférence nativement**. La doctrine, les verrous
et le dimensionnement doivent exister **des deux côtés à l'identique** : c'est
pour ça qu'ils sont écrits comme des règles pures, sans dépendance.

⚠️ Trois contraintes commerciales : le MQL5 Market **déclasse** les EA à
martingale et à grille (les nôtres sont interdits par conception) · **ne jamais
promettre un rendement** dans une fiche produit · un EA se vend sur un
**historique réel vérifié**.

---

## Ce qui reste, par priorité

**P0** — le mot de passe MT5 · l'historique long · la décision de capital
**P1** — journal SQLite (= le jeu d'entraînement) · walk-forward · calendrier économique
**P2** — 3 stratégies de plus · meta-labeling · auto-surveillance réel vs backtest
**P3** — exécution live · Telegram (alertes + commandes depuis le portable)
**P4** — export ONNX + EA MQL5

Détail et pourcentages : **`trading/JOURNAL.md`**.

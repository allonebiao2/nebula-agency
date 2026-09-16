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

## ✅ L'après-midi : le pont s'ouvre (13 h 00 - 13 h 30)

**Le `-6` venait du mot de passe maître manquant.** Une fois posé, la connexion
par identifiants explicites passe du premier coup : compte `6305888` @
`Deriv-Demo`, 10 000 $ démo, 1:1000, couverture, serveur UTC+0.

Ce que la première vraie connexion a révélé, dans l'ordre :

1. **Le mot de passe était dans le mauvais fichier** (`deriv.env`), puis une
   copie **à la racine du dépôt** : `notepad secrets\mt5.env` tapé dans Git Bash
   crée `secretsmt5.env` (antislash mangé), **non ignoré par git**. Jamais
   commité, supprimé, `.gitignore` refuse désormais `*.env` et `secrets*`.
   Le mot de passe a été déplacé et comparé **sans jamais être affiché**.
2. **Deux défauts de `courtier.py`** écrits sans connexion : `trade_expert` lu
   sur le terminal (il appartient au compte) et `SYMBOL_FILLING_FOK/IOC`, que le
   paquet Python n'exporte pas (drapeaux 1 et 2 en MQL5).
3. **`profil_courtier.py` n'envoyait que le chemin du terminal**, la voie même
   qui renvoyait `-6` : il lit désormais les profils de `secrets/mt5.env`.
4. **Le bouton Trading Algo était éteint** : MT5 le coupe **à chaque changement
   de compte** (journal du terminal). Mongazi l'a rallumé.
5. ⛔ **`Api=1` coupait l'API au lieu de l'ouvrir.** La correction du matin était
   inversée : c'est la case « désactiver le trading algorithmique via l'API
   Python externe ». La lecture passait, **tout ordre aurait été refusé**
   (`tradeapi_disabled = True`). Case décochée par Mongazi (Deriv), valeur
   d'origine rétablie dans le terminal Exness, fermé.
6. **Validé sans rien envoyer** : `order_check` sur 0,01 lot avec stop et
   objectif → « Done », remplissage FOK, marge 1,15 $, 0 position, 0 ordre.

**L'historique n'est plus un blocage** : 25 000 barres H4 depuis le
2011-02-24 (~15 ans, ~500 trades). Le terminal télécharge **à la minute**, une
année par minute en remontant, ~22 Mo par année. ⚠️ Disque C: à **6 Go libres**.

**Le spread du backtest est juste** : 149 485 ticks réels sur 24 h, médiane
3 points, p90 4, p99 15. Seule heure à éviter : **21 h UTC** (médiane 15).

**Reste à Mongazi : la décision de capital.** Reste à écrire : l'export de
l'historique MT5 vers `trading/donnees/`, puis le walk-forward sur 15 ans.

---

## Le soir : l'agent, l'interface, le produit (commit `74e96a9`)

Demande de Mongazi : « applique les 3, fais en sorte qu'il passe, on doit pouvoir trader avec
n'importe quel capital en restant performant », « une interface pour parler à l'agent, voir son
évolution, régler, désactiver, voir le risque », « le vendre, l'installer partout ».

**Les données.** Historique MT5 lu **année par année** (une plage de 20 ans d'un coup renvoie
`Call failed`) : 34 876 barres H4 depuis 2005, 6 767 D1, 100 000 H1 depuis 2010. Profil du
courtier mesuré et gardé en JSON (spread médian **3 points** sur 147 161 ticks, swaps en points).

**Le verdict, sans fard.** Walk-forward (4 ans d'apprentissage → 1 an de test, 2011-2026, coûts
réels) :

| Stratégie | Trades | Espérance | PF | 10 000 → |
|---|---|---|---|---|
| Cassure, positions gardées le week-end | 436 | +0,040 R | 1,07 | 11 488 |
| Cassure, fermeture du vendredi | 497 | −0,007 R | 0,97 | 9 415 |
| Retour à la moyenne (nouvelle) | 311 | −0,081 R | 0,82 | 7 663 |

**Aucune n'est distinguable de zéro.** Le réglage par défaut passe à « garder le week-end »
(197 sorties forcées sinon, coûts = 344 % du brut ; 2 gaps en 15 ans).

**Deux défauts du moteur** trouvés en le relisant : les verrous étaient datés à l'ouverture de
la barre du SIGNAL (une entrée à 00 h passait le filtre « Asie » en se datant de 20 h) et la
fermeture du vendredi ne se déclenchait JAMAIS en H4 (dernière barre ouverte à 20 h 00, seuil
20 h 30 : on compare maintenant la fin de la barre).

**Le capital.** Trois réponses automatiques : compte cent détecté (10 $ prennent les mêmes 71
trades que 10 000 $), lot minimum toléré jusqu'à 2 %, attente d'un stop plus court. ⚠️ Le 1er
jet simulait le compte cent en multipliant AUSSI la valeur du point : les lignes « cent »
recopiaient le compte standard.

**L'agent et le produit.** `live/agent.py` (seul fil qui parle à MT5, commandes en file),
`live/execution.py` (stop relu chez le courtier), `live/journal.py` (SQLite), calendrier
Forex Factory, interface FastAPI locale en 8 pages, conversation Claude avec outils (l'agent
rend le système plus prudent seul, jamais plus risqué), coffre DPAPI, licences Ed25519,
QC de 79 contrôles, exécutable PyInstaller de 44 Mo testé sur un premier lancement réel.

**Vu sur les captures, QC vert** : barre « Enregistrer » visible sans changement (`[hidden]`
écrasé par `display:flex`), libellés de courbe écrasés par un SVG étiré, variante non active
affichée en premier, défilement conservé d'une page à l'autre, 8 entrées qui débordaient la
barre du téléphone. ⚠️ L'iframe de contrôle à 390 px était bloquée par `X-Frame-Options: DENY`
(passé à `SAMEORIGIN` + `frame-ancestors 'self'`).

**Deux contrôles truqués de ma main dans le QC** (`or True`, `if False`), repérés en relisant et
remplacés par de vraies mesures. Et le témoin du moteur a trouvé un réglage de TEST faux : spread
facturé 3 contre des barres à 15, le verrou 8 refusait tout, exactement son rôle.

---

## La nuit : le cahier des charges de Mongazi passé au Monte Carlo

Mongazi colle un cahier des charges complet (« Agent de trading autonome auto-améliorant » :
8 modules, modes PRO et BOOST, self-learning, KPIs). Copie verbatim :
`trading/CAHIER-DES-CHARGES-v1.md` ; version corrigée : `trading/CAHIER-DES-CHARGES.md`.

Chiffré sur les 436 vrais trades (bootstrap 20 000 tirages) :
- arrêt total −10 % à 1 %/trade : touché **99 %** du temps sur 15 ans ;
- pause après 5 pertes d'affilée : **97 %** sur 100 trades à 40 % de réussite ;
- 3 à 8 %/mois : il faudrait **1,30 R** par trade (son propre KPI 0,2 R donne 0,46 %/mois) ;
- 30 jours de paper trading : **2 trades** en H4 ;
- levier x5 : incompatible avec 3 % (x6,6) et a fortiori 10 % (**x21,7**, 0 % des signaux) ;
- BOOST à 10 % avec la stratégie actuelle : **46 %** de chances de perdre la moitié en un an,
  **92 %** en trois ans ; dix pertes d'affilée laissent 35 % du capital.

**Décisions de Mongazi** : BOOST jusqu'à **10 %** par trade avec n'importe quel capital · seuils
de drawdown **calibrés au Monte Carlo** · marchés **EUR/USD et NAS100** seulement · intégration
par vagues (profils, Monte Carlo, auto-surveillance et porte démo, puis NAS100). Le BOOST réel
reste derrière la règle de son propre cahier : 60 jours de PRO rentable d'abord.

---

## Ce qui reste, par priorité

**Maintenant** : vague 1 profils PRO/BOOST · vague 2 Monte Carlo · vague 3 auto-surveillance,
auto-analyse, porte démo, chien de garde · vague 4 NAS100
**Ensuite** : filtre D1 · 3 stratégies (momentum, range, cassure de structure) · garde contre les
tests multiples · méta-labeling · Telegram
**Hors code** : page de vente, prix et paiement (décisions de Mongazi) · révoquer le jeton collé

Détail et pourcentages : **`trading/JOURNAL.md`**.

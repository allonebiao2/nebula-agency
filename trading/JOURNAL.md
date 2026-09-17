# NEBULA TRADER — journal d'avancement

Mis à jour le **2026-09-17, fin de journée** (vague 4 finie, recherche de stratégies faite, QC 190 verts).
Une ligne par brique, avec son pourcentage réel.

> ⚠️ **Un pourcentage ici mesure ce qui est ÉCRIT ET TESTÉ, pas ce qui est
> prévu.** Une brique conçue mais non codée vaut 0 %. Une brique codée mais
> jamais exécutée ne dépasse pas 70 %.

---

## 🔴 POINT D'ARRÊT EXACT (à lire en premier en reprenant)

### 🔬 RECHERCHE DE STRATÉGIES du 2026-09-17 : verdict NON (rapport : `trading/RECHERCHE-STRATEGIES.md`)

Demande de Mongazi : les 5 meilleures stratégies scalping et intraday « à plus de 80 % », plus les
deux vidéos qu'il a envoyées (MambaFx, scalping M1 sur US30 ; Hugo FX, CRT H1 + swing M15 + entrée
M1), testées sur EUR/USD et NAS100, R:R d'au moins 1:2, 2 stratégies pour PRO et 2 pour BOOST.
- **50 tests, 0 survit à la correction de Holm.** Aucune stratégie retenue pour PRO ni pour BOOST,
  **rien d'intégré dans l'agent** (plan : on n'intègre rien de perdant).
- **Aucun 80 % sur un échantillon qui compte** (le 83 % MambaFx NAS100 M1 = 6 trades).
- Pistes à creuser, pas à trader : **MambaFx version auteur**, positive sur tous ses échantillons
  EUR/USD mais sur 14 à 28 trades ; **range de séance EUR/USD M15** (+0,087 R, 358 trades, p = 0,15).
- **Bloquant** : MT5 plafonne à 100 000 bougies (`MaxBars` de `common.ini`) = **3 mois de M1**.
  Fermer MT5 pour le relever a été **refusé par le garde de sécurité** de Claude Code : geste de
  Mongazi (Outils → Options → Graphiques → Max. barres = Unlimited, redémarrer), puis
  `python -m trading.noyau.donnees_mt5 M1 M5 --base EURUSD` (et NAS100) et
  `python -m trading.recherche.videos_lancer`, puis `python -m trading.recherche.rapport`.
- **Fait en chemin** : banc `trading/recherche/` (numba, ordres limites, agrégation multi-unités,
  plancher de stop du courtier, registre + Holm, projection vers le million) · **R:R 1:2 imposé en
  PRO ET en BOOST** par le videur · `lire_plage` récupère les 100 000 dernières barres (le M5 perdait
  47 000 barres) · moteur : **une nuit de swap par nuit** en M5/M15 (12 et 4 avant) · QC 176 → 190.

**La VAGUE 4 (EUR/USD + NAS100) est finie** le 2026-09-17 : écrite, contrôlée, **lancée en
direct en observation** sur le démo Deriv `6305888`, captures regardées. QC **176 verts / 0
rouge** (`python -m trading.outils.qc`), dont **42 contrôles multi-instruments** prouvés rouges
sur l'ancien code. Détail de la session : `_memoire/conversations/2026-09-17-nebula-trader-vague4.md`.

### ⛔ Ce que la vague 4 a fait tomber : les chiffres d'hier étaient faux

| | Affiché jusqu'au 2026-09-16 | **Mesuré sous les règles appliquées** |
|---|---|---|
| EUR/USD cassure, week-end gardé | 436 trades · **+0,040 R** · 10 000 → 11 488 | **372 trades · −0,045 R** · PF 0,89 · 10 000 → 8 074 · DD 27,5 % |
| EUR/USD cassure, fermeture du vendredi | 497 trades · −0,007 R | **454 trades · −0,021 R** · PF 0,91 · 10 000 → 8 632 · DD 26,3 % |
| EUR/USD retour à la moyenne (vendredi / week-end) | 311 trades · −0,081 R | **308 · −0,059 R** / **348 · −0,077 R** |
| NAS100 cassure (12 → 6 mois) | 2 trades · « rien de prouvé » | **49 trades · −0,095 R** · PF 0,80 |
| NAS100 retour à la moyenne | 0 trade | **39 trades · −0,218 R** · PF 0,64 |

Trois causes, toutes mesurées :

1. **Les rapports EUR/USD dataient d'avant « R:R minimum 1:2 »** (vague 1, cahier). Preuve : en
   rejouant un réglage à la fois, **seul le R:R à 1,0 ramène les 436 trades et +0,0399 R** ; le
   plafond de levier et la limite de trades par jour ne changent rien. L'agent prenait ses
   réglages et le Monte Carlo ses seuils dans des rapports qui ne décrivaient plus l'agent.
   → **`empreinte_regles(cfg)`** écrite dans chaque rapport, comparée par l'interface (bandeau
   « mesuré sous d'autres règles ») et par l'agent (alerte une fois par instrument).
   ⚠️ **Premier jet faux positif, vu EN DIRECT** : l'arrêt total est calibré au Monte Carlo À
   PARTIR du rapport (20 % dans le fichier, 26 % appliqués), tous les rapports sortaient
   périmés à la minute. Exclu de l'empreinte, et un contrôle le garde.
2. **Le plafond de spread de 20 points était commun aux deux instruments.** Il refusait
   **92,8 % des bougies du NAS100** (spread FIXE de 70 points chez Deriv). Le « 2 trades »
   mesurait le plafond. → `[execution.par_instrument.NAS100]` en **prix** (2,0 = 200 points),
   converti avec le point du courtier ; la **déviation** suit la même règle.
3. **L'outil de walk-forward n'imposait que `--sans-weekend`.** Sans le drapeau il héritait du
   `config.toml`, qui garde le week-end : la variante « fermeture du vendredi » ne fermait rien
   et l'écrivait quand même. → `configurer()` impose la variante, contrôle ajouté.

⚠️ **Preuve que la vague 4 est neutre pour l'EUR/USD** : même walk-forward sur le code d'avant
(`git archive HEAD`) et d'après, **trades_R et courbe d'équité identiques**.

⚠️ **Conséquences à dire à Mongazi, pas à trancher seul** :
- **La décision « positions gardées le week-end » reposait sur +0,040 contre −0,007.** Sous les
  règles actuelles c'est l'inverse : fermer le vendredi perd moins (−0,021 contre −0,045). Les
  deux sont négatifs et aucun n'est distinguable de zéro. `config.toml` n'a pas été touché.
- **Arrêt total PRO calibré : 26 %** (23 % annoncé). **BOOST à 10 % : 55 %** de chances de
  perdre la moitié en un an (46 % annoncé), lu par `montecarlo.pour_interface`.

### Ce qui est FAIT dans la vague 4

| Fichier | Ce qui a été fait |
|---|---|
| `noyau/instruments.py` (neuf) | alias et `candidats_symbole` (déplacés de `courtier.py`, réexportés) · ⛔ **« US1000 » était pris pour « US100 » + suffixe** : un suffixe de compte ne commence pas par un chiffre · `base_de` · `FACTEURS` et `exposition_par_facteur` · `limites_execution` |
| `noyau/config.py` · `config.toml` | `Execution.par_instrument` validé par le videur · `empreinte_regles` |
| `noyau/plan.py` | Q8 lit le plafond de l'instrument · Q3 refuse aussi par **facteur** (« le facteur USD porterait l'exposition à 4,5 % ») · ⚠️ avec deux instruments qui partagent le dollar, c'est l'équivalent du plafond total : la règle vaut quand on en ajoute un troisième |
| `backtest/moteur.py` | plafond de spread de l'instrument |
| `live/execution.py` | **`marche_ferme()`** : à l'échelle H4 aucune bougie du NAS100 ne manque (coupure quotidienne d'une heure DANS la bougie de 20 h), ce qui ferme l'indice ce sont les **jours fériés US** (4 vendredis sur 49 sans bougie de 20 h). Un ordre là revient rejeté, et **3 rejets en une heure mettent TOUT l'agent en pause**. Fraîcheur comparée à la cotation la plus fraîche des marchés, pas à l'horloge |
| `live/agent.py` | ⛔ **EUR/USD et NAS100 ferment leur bougie H4 à la même heure** : le second décidait sur l'état d'avant la première position (plafond d'exposition franchissable à deux) → `_analyser_marches` relit positions et risque après chaque ouverture · `_motif_blocage` extrait (testable sans terminal) · déviation par instrument · alerte « autres règles » |
| `outils/walkforward.py` | `configurer()` impose la variante · empreinte dans le rapport |
| `interface/` | `regles_a_jour` par rapport, bandeau si périmé |
| `outils/qc.py` | bloc **MULTI-INSTRUMENTS** : noms, configuration, plafonds, facteurs, séances, swap mode 5, rapports par instrument, routage d'une position vers SON exécuteur, blocage par instrument, cycle commun, variantes, empreinte |
| `trading/rapports/_archive/` | les rapports faux, gardés pour comparaison (hors de la recherche des rapports actifs) |

**Vérifié en direct** : connexion, **« US Tech 100 » trouvé par l'agent**, une analyse par
instrument et par bougie, réglages du NAS100 lus dans son walk-forward, aucune erreur de cycle,
`/api/etat` publie les deux marchés, captures Tableau, Stratégies, Décisions, Évolution en 1440
et 390 : **0 débordement, 0 erreur JavaScript**.

### Ce qui RESTE, dans cet ordre

1. **Reconstruire le paquet** : `python -m trading.empaquetage.construire` après avoir fermé Chrome et VS Code (tué 3 fois par manque de RAM le 2026-09-17, `sortie/` est vide). Vérifier qu'il embarque les six rapports et aucun secret.
2. **Mongazi tranche** : week-end gardé ou fermeture du vendredi (voir plus haut), et s'il veut
   garder le NAS100 malgré −0,095 R sur 49 trades (échantillon court, rien de prouvé dans un
   sens ou dans l'autre).
3. **Après la vague 4 (déjà décidé, pas commencé)** : filtre **D1** · 3 stratégies (**momentum,
   range, cassure de structure**) · RSI, MACD, Bollinger, structure HH/HL · **garde contre les
   tests multiples** · **méta-labeling** (scikit-learn, surveiller le disque) · **Telegram**.
   ⚠️ **Priorité absolue : un avantage.** Tout le reste du produit est prêt autour d'un moteur
   qui, mesuré honnêtement, perd.

### Ce qui n'appartient qu'à Mongazi

- Prix, page de vente, paiement, remise de licence.
- ⛔ **Révoquer le jeton `pat_…` collé en clair** le 2026-09-16.
- La **porte démo** exige 30 jours ET 30 trades : au rythme EUR/USD H4 (~2 trades/mois),
  c'est **plus d'un an** de démo avant le réel.
- Le capital du NAS100 (**3 372 $ minimum à 1 %** chez Deriv, lot minimum 0,1) et le risque BOOST.
- Retirer de l'Observation du marché MT5 les symboles inutiles (disque C: à **14 Go libres**).

---

## Avancement global : **70 %**

```
Socle de discipline   ████████████████████  100 %   videur, 8 verrous, profils, plafonds par instrument (QC 176)
Mesure (backtest)     ████████████████████  100 %   walk-forward, Monte Carlo, empreinte des règles par rapport
Données               ██████████████████░░   90 %   EUR/USD 20 ans · NAS100 depuis 2024-01 seulement
Courtier / exécution  ████████████████░░░░   80 %   agent multi-instruments EN DIRECT en observation · aucun ordre
Surveillance          ████████████████░░░░   80 %   CUSUM, chien de garde, portes, rapport hebdo
Interface + produit   ██████████████████░░   90 %   profils, BOOST, Évolution, rapports périmés signalés
Intelligence          ░░░░░░░░░░░░░░░░░░░░    0 %   AUCUN AVANTAGE PROUVÉ : la priorité après la vague 4
Vente en ligne        ██░░░░░░░░░░░░░░░░░░   10 %   licences signées prêtes, ni page ni paiement
```

⚠️ **Le chiffre qui compte n'est pas le pourcentage : c'est que le walk-forward,
mesuré sous les règles réellement appliquées, PERD sur les six variantes** : EUR/USD cassure
−0,045 R (372 trades) ou −0,021 R en fermant le vendredi, NAS100 −0,095 R (49 trades). Le
« +0,040 R » affiché jusqu'au 2026-09-16 datait d'avant la règle R:R 1:2. Un produit fini autour
d'une stratégie sans edge reste un produit qui ne gagne rien.

---

## Le détail

| Brique | % | État |
|---|---|---|
| `noyau/config.py` le videur, `config.toml` | **100 %** | ✅ refus + témoins, surcharges, **profils PRO (plafond 2 %) et BOOST (plafond 10 %)**, disjoncteurs BOOST recalculés en escalier |
| `noyau/profils.py` paliers + poche épargne | **100 %** | ✅ échelle anti-martingale 10 → 5 → 3 → 2 → 1,5 → 1 % à chaque ×2 ; à +50 %, 25 % du gain sort du dimensionnement |
| `noyau/risque.py` dimensionnement | **100 %** | ✅ petit compte, **levier effectif plafonné en RÉDUISANT la taille** (refus seulement si le lot minimum dépasse) |
| `noyau/capital.py` compte cent + viabilité | **100 %** | ✅ 10 $ en cent = mêmes trades que 10 000 $ |
| `noyau/plan.py` 8 verrous | **100 %** | ✅ levier dans le détail du verrou 3 |
| `noyau/calendrier.py` annonces à fort impact | **90 %** | ✅ USD + EUR · ⏳ pas d'historique pour le backtest |
| `noyau/donnees_mt5.py` historique + profil courtier | **100 %** | ✅ EUR/USD 34 876 H4 · NAS100 4 250 H4 · swap en % annuel |
| `noyau/courtier.py` · `identifiants.py` · `coffre.py` · `instruments.py` | **100 %** | ✅ « US Tech 100 » trouvé **par l'agent en direct** · « US1000 » n'est plus pris pour le NAS100 · plafonds et facteurs par instrument |
| `noyau/reglages.py` | **100 %** | ✅ profils, seuil d'arrêt **calibré au Monte Carlo** injecté (en cache) |
| `noyau/licence.py` Ed25519 hors ligne | **100 %** | ✅ |
| `backtest/moteur.py` | **100 %** | ✅ suit paliers et poche comme le direct |
| `backtest/walkforward.py` | **100 %** | ✅ années ou mois, `trades_R`, **empreinte des règles**, variante IMPOSÉE (`outils/walkforward.configurer`) |
| `backtest/montecarlo.py` | **100 %** | ✅ bootstrap par blocs de 5, seuil = p99 sur 2 ans × 1,2 plafonné à 35 %, par instrument |
| `apprentissage/sante.py` CUSUM | **90 %** | ✅ 0 % de fausses pauses, 76 % de détection d'une chute de 0,6 R en 60 trades · ⏳ jamais déclenché en direct |
| `apprentissage/analyse.py` rapport hebdo | **85 %** | ✅ par stratégie, symbole, heure, jour, régime ; non concluant sous 20 trades |
| `apprentissage/porte.py` portes démo et BOOST réel | **90 %** | ✅ exigées par `execution.autorisation` |
| `strategies/` | **30 %** | 2 écrites, **0 rentable** · ⏳ filtre D1, momentum, range, cassure de structure |
| `live/journal.py` SQLite | **100 %** | ✅ `symbole`, `profil`, `risque_choisi`, glissement par ordre (migrations) |
| `live/execution.py` | **80 %** | ✅ glissement mesuré, `poser_stop` · ⛔ **aucun ordre réel envoyé** |
| `live/agent.py` la boucle | **80 %** | ✅ **multi-instruments lancé en direct** (observation) · risque relu après chaque ouverture · séance fermée détectée · ⛔ aucun ordre envoyé |
| `interface/` serveur + chat + pages | **90 %** | ✅ onglets par instrument regardés en capture 1440 et 390 · bandeau « mesuré sous d'autres règles » |
| `empaquetage/construire.py` | **60 %** | ⛔ **plus de paquet sur le disque** : la construction du 2026-09-17 vide `sortie/` en démarrant, puis a été tuée **trois fois par manque de mémoire vive** (1,5 Go libres sur 7,9 ; PyInstaller meurt pendant l'analyse des modules). ⏳ fermer Chrome et VS Code, puis `python -m trading.empaquetage.construire` |
| Méta-labeling · champion/challenger | **0 %** | conçu, pas codé |
| Telegram | **0 %** | rien |
| Page de vente + paiement + remise de licence | **0 %** | ⛔ attend les décisions de Mongazi |

---

## Ce qui a été trouvé en chemin (et qui vaut d'être gardé)

**⛔ Le disjoncteur de série noire se verrouillait pour toujours.** Le compteur
de pertes consécutives ne retombe que sur un gain, et aucun gain n'est possible
tant que les entrées sont bloquées. Mesuré : le bot cessait de trader en
**octobre 2021** sur un jeu allant à fin 2024. Le `config.toml` prévoyait une
pause de 24 h, le moteur ne l'avait jamais implémentée. En production, ça se
serait vu comme « le bot ne trade plus » sans explication.
**Trouvé parce que le nombre de trades n'était pas monotone** dans un balayage
(123 à 12 barres, 25 à 18, 64 à 48) : *vérifier sa sonde avant d'accuser le
produit.*

**⚠️ Le stop temporel étranglait les trades.** À 12 barres il était le mode de
sortie **principal** (83 sorties sur 123) au lieu d'être un filet. Porté à 36,
sur un argument de conception et non sur une performance mesurée sur données
synthétiques.

**✅ L'API publique de Deriv donne de vraies bougies sans aucun jeton.** C'est ce
qui a débloqué le projet alors que le pont MT5 refusait de s'ouvrir.

**✅ Le `-6 Authorization failed` venait du mot de passe manquant.** La
connexion par identifiants explicites (`mt5.initialize(login=, password=,
server=)`) passe du premier coup. `profil_courtier.py`, qui n'envoyait que le
chemin du terminal, lit désormais les profils de `secrets/mt5.env`.

**⛔ `Api=1` NE DONNE PAS l'accès à l'API, IL LE COUPE.** La clé `[Experts] Api`
de `common.ini` est la case « **désactiver** le trading algorithmique via l'API
Python externe », comme `Account` et `Profile` sont des « désactiver quand… ».
Elle avait été passée de 0 à 1 en croyant l'ouvrir : la lecture restait
possible, **tout ordre aurait été refusé**. Prouvé : `Api=1` donnait
`tradeapi_disabled = True`, la case décochée donne `Api=0` et `False`.
*Une clé d'ini se lit dans l'interface qui l'écrit, pas d'après son nom.*
Et on ne corrige pas `common.ini` à la main pendant que le terminal tourne : il
l'écrase en se fermant.

**⚠️ MT5 coupe le Trading Algo à chaque CHANGEMENT DE COMPTE** (`Account=1`,
journal : « automated trading is disabled because the account has been
changed »). Le terminal portait un autre compte, la première connexion du bot
l'a éteint. Réglage laissé tel quel, c'est une sécurité : c'est au bot de
**vérifier les quatre autorisations** avant d'armer, pas au terminal de se taire.

**⛔ Deux défauts de `courtier.py`, écrits sans connexion et invisibles jusqu'à
la première** : `trade_expert` lu sur le terminal alors qu'il appartient au
**compte** (plantage dès la connexion), et `SYMBOL_FILLING_FOK/IOC` que le paquet
Python **n'exporte pas** (drapeaux 1 et 2 en MQL5, à ne pas confondre avec
`ORDER_FILLING_*` qui valent 0, 1, 2 et ne sont pas des bits). Contrôlé depuis :
toutes les autres constantes `mt5.*` du code existent.

**✅ Le spread du backtest est juste.** 149 485 ticks réels sur 24 h : médiane
**3 points**, p90 4, p99 15. Le « 11 points » affiché à la connexion était un
pic. **Seule heure à éviter : 21 h UTC** (bascule de journée, médiane 15).

**⛔ `notepad secrets\mt5.env` tapé dans Git Bash crée `secretsmt5.env` À LA
RACINE** (l'antislash est mangé). Le mot de passe s'y est retrouvé, **hors de
`secrets/` et visible par git**, dans un dépôt public. Jamais commité, supprimé,
et `.gitignore` refuse désormais `*.env` et `secrets*`. Sous Git Bash : des
barres obliques (`notepad secrets/mt5.env`).

**⛔ Le jeton collé le 2026-09-16 n'est pas un jeton Deriv** (`InvalidToken` ;
format `pat_` + 64 hex, alors que Deriv utilise `a1-…`). Il a été collé en clair
dans une conversation : **à révoquer quel que soit le service auquel il
appartient**.

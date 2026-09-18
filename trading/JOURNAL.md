# NEBULA TRADER — journal d'avancement

Mis à jour le **2026-09-18, après-midi** (test d'un an : la méthode perd chez un courtier). Avant : le **2026-09-17, nuit** (recherche de scalping : un candidat confirmé sur données scellées, plafond intraday mesuré, QC 219 + 35 verts).
Une ligne par brique, avec son pourcentage réel.

> ⚠️ **Un pourcentage ici mesure ce qui est ÉCRIT ET TESTÉ, pas ce qui est
> prévu.** Une brique conçue mais non codée vaut 0 %. Une brique codée mais
> jamais exécutée ne dépasse pas 70 %.

---

## 🔴 POINT D'ARRÊT EXACT (à lire en premier en reprenant)

### 🌐 STRATÉGIES PUBLIÉES, TESTÉES LE 2026-09-18 AU SOIR (rapport : `trading/RECHERCHE-WEB.md`)

Mongazi : « trouve-moi sur la toile une méthode… ne t'arrête jamais tant que tu ne trouves pas ».
- **Aucune source crédible ne montre plus de 50 % de gagnants à 1:2.** Momentum : 25-48 % avec de gros
  gains ; retour à la moyenne : 70-75 % avec de petits gains et souvent sans stop.
- Testées sur le NAS100, règles des articles, **juge = la période que les auteurs n'ont jamais vue** :
  ORB 5 min (article reproduit, puis 25 % de gagnants, +0,06 à +0,08 R, non significatif) · **zone de
  bruit** (40 % de gagnants, gain/perte 1,8, **+8 à +10,6 %/an**, Sharpe 0,6-0,7, recul 18 %) ·
  dernière demi-heure (négative).
- ⛔ Avec 10 $, aucune n'est tradable à son risque : il faut ~1 200 $ (zone de bruit) ou ~400 $ (ORB).
- ⏳ **Suite** : moteur d'agent pour la zone de bruit (règle anti-triche), la même sur l'EUR/USD,
  et le critère à trancher par Mongazi (50 % à 1:2, ou espérance et recul).


### ⛔ LE TEST D'UN AN DU 2026-09-18 (après-midi) : LE REFLUX PERD CHEZ UN COURTIER (rapport : `trading/REJEU-1AN.md`)

Mongazi : « fais le test sur 1 an avec un capital de 10 dollars sur chacun, et prends les notes ».
- **Fait avec le moteur de l'agent** (`live/moteur_scalp.py`, neuf, partagé par `recherche/rejeu.py`
  et `live/scalpeur.py`) : l'ordre touché le PREMIER entre, comme chez un courtier. Filtres
  trimestriels qui n'ont jamais vu l'année, prix et coûts Deriv, vrais lots, échelle 6-4-3.
- **Résultat** : NAS100 **30,8 % de 2 R, −0,103 R** (1 457 trades) · EUR/USD **25,4 %, −0,370 R**
  (1 045) · 10 $ : **0 trade** sous le plafond x30 (il faut ~80 $ NAS100, ~39 $ EUR/USD), et sans
  plafond 10 $ → 8,98 $ (NAS100) et 6,62 $ (EUR/USD). Même année, mêmes prix, la recherche disait
  67,3 % et +0,987 R (NAS100).
- ⛔ **LA CAUSE : `banc._simuler_ordres` n'est pas causal.** Il traite les ordres limites dans l'ordre
  de POSE et donne le trade au plus ancien qui finit par être servi, donc au plus bas quand le prix
  plonge à travers plusieurs ordres : il « sait » que le prix ira jusque-là. Sans filtre : banc
  +0,186 R, moteur causal −0,090 R. Le filtre a appris sur ces trades-là. Second défaut, même sens :
  réentrée dans la barre même où le trade précédent sort.
- ✅ **Le moteur est contrôlé contre le banc** (`_qc_moteur.py`) : ordres d'une minute → mêmes trades
  au 1e-4 R près, 208 épisodes de divergence sur 208 ouverts par la réentrée du banc.
- **Variantes causales** (`rejeu_variantes.py`) : ordre le plus profond, repli 1,0 R, repli 1,5 R,
  avec et sans filtre : **toutes entre −0,08 et −0,34 R**. Registre : ce sont des essais, pas des preuves.
- **Fait en chemin** : `construire_aux_barres` (caractéristiques par morceaux, tient dans 1,7 Go) et
  `_qc_parite.py` (**20 000 minutes = parité à 2e-6 ; les 6 000 de l'agent s'écartaient de 3,7 %** ;
  témoin à 500 rouge) · `scalpeur.py` réécrit : ⛔ **il n'appelait pas `execution.autorisation`**
  (avec son drapeau il aurait tradé un compte RÉEL), il n'écrivait aucun trade dans le journal
  (le carnet serait resté vide), il jugeait le filtre à la pose et non à la minute du remplissage,
  et son coût était constant alors que deux caractéristiques dépendent du coût minute par minute ·
  `Executeur.ouvrir_niveaux` · fiches par trade `rapports/recherche/rejeu/*.jsonl` et `direct/`.
- ⚠️ **Le plafond de levier x30 de BOOST interdit le scalping M1 à 6 %** : levier médian x29 (NAS100)
  et x73 (EUR/USD). Les calculs « 50 $ → 8 M$ » n'avaient aucun plafond.
- ⏳ **Suite** : (1) réapprendre le filtre sur les trades du moteur causal et le rejuger ; (2) rendre
  le banc causal et **rejouer tout le registre** ; (3) aucune démo ni argent réel avant une version
  causale positive sur une période neuve. Donnée : EUR/USD Dukascopy du **2024-10-10** corrompu
  (617 bougies), `_qc_sans_fin` rouge, à retélécharger.
  ⚠️ Rappel déplacé de `CLAUDE.md` : l'export MT5 « Unlimited » renvoie des **bougies factices depuis
  1971** en M15/H1 (une par jour à 22 h, historique reconstitué d'avant l'euro) : filtrées à la
  lecture (`noyau/donnees_mt5.py`).
- QC : `trading.outils.qc` **219 verts** · `_qc_moteur` vert · `_qc_parite` vert (témoin rouge) ·
  `_qc_sans_fin` 44 verts, 1 rouge (la journée corrompue).


### 💰 PLAN DE RISQUE DE MONGAZI appliqué le 2026-09-18 (document : `trading/PLAN-DE-RISQUE.md`)

Mongazi envoie ses planches : **échelle 6-4-3 pilotée par le drawdown + intérêts composés**, et
demande que la stratégie et le backtest la suivent **à n'importe quel capital**, avec un carnet de
trades analysé au fil de l'eau.

- **L'échelle est écrite au SEUL endroit où le risque est décidé** (`noyau/profils.risque_courant`),
  donc l'agent en direct et les backtests décident avec le même code. Réglage : `config.toml`,
  `[profil_boost] paliers_drawdown = [[0, 6], [0.0001, 4], [0.20, 3]]`. Le profil actif reste `pro` :
  **rien n'a changé pour l'agent tant que Mongazi ne bascule pas**.
- ⚠️ **L'échelle est ANCRÉE sur le risque choisi** (à 10 % elle donne 10-6,7-5) : écrite en dur, elle
  aurait plafonné à 6 % quelqu'un qui a choisi 10, sans le lui dire. ⛔ **Le videur refuse toute
  échelle dont le risque remonte quand le drawdown s'aggrave** (martingale).
- **Ce qu'elle apporte, mesuré sur 1 467 vrais trades** : pire recul **28,8 % → 23,7 %**, et si
  l'avantage disparaît, **P(ruine) 46,6 % → 5,8 %**. Elle ne fait pas gagner plus, elle fait survivre.
- ⛔ **LE PLAFOND DE LOTS CHANGE TOUT** (`recherche/compte_plan.py`, vrais lots) : les 100 lots
  maximum de Deriv plafonnent le risque à ~1 700 $ par trade sur le NAS100, donc **la croissance
  cesse d'être exponentielle** et **tous les capitaux de départ convergent** (50 $ comme 1 M$
  finissent vers 2,5 M$ en 4 ans). La planche « 5 000 $ → 41 millions » ne peut pas se produire sur
  un seul compte : c'est ce que répond sa propre planche « LES POSSIBILITÉS » (plusieurs comptes).
- **Mois par mois à 500 $** : croissance médiane **6,2 %/mois**, 100 % de mois positifs — ⚠️ une
  conséquence arithmétique de +0,96 R sur 30 trades/mois, **pas une promesse** : tout repose sur la
  tenue de l'avantage en direct.
- **Carnet** : `python -m trading.recherche.suivi` → `trading/SUIVI.md` (une ligne par trade, palier
  appliqué, série en cours, écart au backtest avec intervalle de confiance). Il lit le journal
  SQLite de l'agent. **Premier chiffre à surveiller : le taux de remplissage des ordres limites.**
- ⛔ **Deux régressions attrapées** : un champ ajouté à `banc.Trades` **décalait les champs de
  `TradesSniper`** (prix d'entrée faux, 2 contrôles rouges) — ne jamais ajouter de champ à une classe
  dont une fille passe ses valeurs par position ; et un **tableau de coûts survivait à une découpe de
  série** (`dataclasses.replace`), corrigé par un `__post_init__` qui le jette s'il ne fait plus la
  bonne longueur.
- QC **219 + 45 + 43 + 20 verts**. ⏳ **Prochaine étape : la démo en observation** sur `6305888`.

### ⚡ RECHERCHE DE SCALPING du 2026-09-17 : **un candidat, et une réponse mesurée à la question de Mongazi** (rapports : `trading/RECHERCHE-SCALPING.md`, protocole `trading/RECHERCHE-SANS-FIN.md`)

Mongazi : « recherche une stratégie qui puisse atteindre ces objectifs, tant qu'on ne trouve pas tu ne
peux pas t'arrêter », puis « je veux plus de scalping, ouvrable et fermable dans la même journée ».

- ⚠️ **Le plafond, mesuré** : un devin parfait qui trade **toutes** les occasions atteindrait **63,8 %**
  de 2 R sur NAS100 M1 et **57,7 %** sur EUR/USD M1, tout fermé le jour même. Le point mort n'est pas
  33 % mais **34 à 41 %** selon le stop. ⚠️ **Ce plafond borne une stratégie qui prend tout, pas une
  stratégie SÉLECTIVE** : c'est exactement par là que le filtre passe (il garde 5 % des occasions).
- ✅ **UN CANDIDAT survit à tout** (`trading/recherche/candidat.py`) : **entrée limite « au rabais »**
  sur **NAS100 M1** — dans le sens de l'EMA 60 min, ordre limite à 0,5 R sous le prix, stop 2 × ATR(14),
  objectif 2 R, ordre annulé après 60 min, tout fermé le soir.
  **SCELLÉ OUVERT le 2026-09-17** (2020-2023 Dukascopy, jamais regardé) : **29 362 trades, 40,3 % de
  2 R (point mort 34,7 %), +0,165 R par trade, PF 1,26**, positif **chaque année** (2020 +0,16 · 2021
  +0,11 · 2022 +0,21 · 2023 +0,17) et **dans les deux sens** (achat +0,17, vente +0,16).
  ⛔ **Il ne remplit PAS les critères** : 40,3 % au lieu de 50 %, et P(5 pertes/100) = 96,7 %.
- ⚠️ **Il vit et meurt par le spread** : il survit à **×3** le coût Deriv (70 points), pas ×4 ; au
  spread d'époque de Dukascopy (167 points) il perd. Deriv tient **70 points dans 99,8 % des minutes**,
  ouverture et annonces comprises (mesuré sur 2025-2026).
- ⛔ **Le piège qui a failli faire publier un faux** : un ordre limite rempli « dès que la bougie touche »
  donnait **+0,101 R sur EUR/USD** ; en exigeant que le prix TRAVERSE d'un spread (un achat s'exécute au
  prix acheteur), il tombe à **+0,017 R**, puis **-0,019 R** en prudent. L'EUR/USD était entièrement un
  artefact ; seul le NAS100 survit. `Ordres.k_remplissage`.
- ✅ **Ce n'est pas un artefact de Deriv** : sur 2024-2026, **Deriv +0,169 R et Dukascopy +0,175 R**,
  deux fournisseurs indépendants, corrélation des minutes 0,985, mêmes mèches, même autocorrélation.
- **Le reste de la recherche, tout négatif** : 7 familles de scalping (ouverture de séance, balayage de
  niveau, compression, excès, suite de bougies, créneau volatil) · un modèle (41 caractéristiques
  causales dont volume, annonces et **surprise économique**, walk-forward purgé) qui gagne 1 à 5 points
  sur le taux de base mais **jamais le point mort** · **55 000 paires et 6 500 triplets** de conditions
  minés en bitsets, meilleure règle validée 37,6 % sur 744 trades. **Registre 312 → 389 tests.**
- **Fait en chemin** : `dukascopy.py` (EUR/USD M1 depuis 2003-05, NAS100 depuis 2013-01, bid ET ask,
  écriture atomique) · `scelle.py` (une ouverture par candidate, journalisée) · `intraday.py` (tout se
  ferme le jour même, heure de New York) · `etiquettes.py` (triple barrière par barre, marché et limite)
  · `carte.py` (plafonds) · `caracteristiques.py` · `meta.py` · `regles.py` · `comparer_flux.py` ·
  `candidat.py` · `_qc_sans_fin.py` **35 contrôles** · coût **minute par minute** dans le banc.
- ✅ **ET LE FILTRE ATTEINT LES CRITÈRES** (`trading/recherche/meta_candidat.py`) : un second modèle,
  appris **une seule fois sur 2013-2019**, décide s'il faut prendre le trade que le candidat propose.
  Sur le **scellé 2020-2023**, en gardant les **5 %** les plus sûrs : **1 467 trades (≈ 1 par jour),
  66,7 % de 2 R, R:R réalisé 1,85, +0,960 R par trade, P(5 pertes/100) 22 %, P(6) 8 %, plus longue
  série 5**. En gardant 20 % : 58,6 %. Rejoué à l'identique sur 2024-2026 : **66,3 % (Deriv) et
  66,1 % (Dukascopy)**. Équilibré achat/vente (61/39), positif **chaque année, 2022 compris**, et il
  survit à un spread **×5**.
  ⚠️ **Témoin** : étiquettes mélangées → 45,2 % au lieu de 66,7 %. L'écart 40,3 → 45,2 est un effet
  de **sélection** (choisir un sous-ensemble du marché change le taux de base), pas de prédiction.
  ⛔ **Fuite d'une minute attrapée** : lire la barre où l'ordre est SERVI utilise sa clôture, donc une
  partie du rebond à prédire (65 % au lieu de 62,5 %). On lit la dernière barre close avant.
  ⚠️ **Ce que ça exige** : décider à chaque minute de garder ou d'annuler l'ordre. L'agent actuel est
  en H4 au marché : c'est un autre objet à construire.
- ✅ **ÇA MARCHE SUR LES DEUX MARCHÉS** : mêmes réglages, jamais ajustés sur l'EUR/USD, filtre appris
  sur Deriv 2019-2026. **Scellé EUR/USD ouvert** (2003-2011) : en gardant 5 %, **2 618 trades, 61,4 %
  de 2 R, R:R 1,81, +0,795 R, P(5/100) 38 %** ; **au spread d'époque** (2,6× Deriv) **60,9 %, +0,727 R**.
  Sans filtre : 37,2 %, +0,120 R. (`rapports/recherche/meta/scelle_eurusd.json`)
- 🎯 **LA LEÇON** : le taux de réussite n'est pas une propriété du marché, c'est une propriété de la
  **sélectivité**. Tout prendre = 37-40 % de 2 R ; garder 5 % = 61-67 %. Le plafond de 63,8 % borne
  celui qui prend TOUT, pas celui qui choisit.
- ⏳ **Ce qui attend Mongazi** : **la démo en observation** (seul juge restant), puis l'ingénierie de
  l'agent M1 à ordres limites. **Les deux scellés sont désormais ouverts** (NAS100 deux fois, EUR/USD
  une fois) : la prochaine confirmation ne peut plus être qu'**en avant**, sur la démo.
- Relancer : `python -m trading.recherche.candidat` · `python -m trading.recherche.meta_candidat` ·
  `python -m trading.recherche.rapport_sans_fin` · `python -m trading.recherche._qc_sans_fin`.

### 📐 FIGURES CHARTISTES + RSI + EMA 50 du 2026-09-17 nuit : verdict NON (rapport : `trading/RECHERCHE-FIGURES.md`)

Mongazi : « et les biseaux ? et l'épaule-tête-épaule et l'inversé ? et si on ajoute le RSI et l'EMA 50 ?
backtestons ».
- **192 versions fixées avant le premier résultat** (`trading/recherche/figures.py`) : 4 figures × 4 filtres
  (aucun, divergence RSI 14, confirmation EMA 50, les deux) × 2 stops (proche, loin) × H1, H4, D1 × EUR/USD
  et NAS100, objectif 2 R, coûts Deriv. Registre 146 → **312 tests, 0 survit**. **0 version** à plus de
  50 % sur au moins 100 trades. 18 positives sur 40 avec au moins 30 trades : le hasard.
- EUR/USD sans filtre : ETE H4 **89 trades, 42,7 %, +0,175 R (p 0,12)** → 10 000 $ = 11 550 $ en 21 ans
  (+0,7 %/an) ; ETE inversé H4 −0,288 R ; biseaux négatifs sauf ascendant H1 +0,086 R. ETE D1 59 % mais
  22 trades et 4 objectifs atteints.
- **RSI** : 0 point de réussite en plus, garde 31 % des trades. **EMA 50** : +2,3 points, +0,025 R, garde
  59 %. Filtres = moins de trades, pas moins de pertes.
- NAS100 : quelques dizaines de figures depuis 2024, rien à conclure.
- **Planches regardées** avant les tableaux ; stop « proche » des biseaux corrigé (tombait au prix du
  « loin »). `_qc_figures.py` **11 contrôles**, dont 2 fuites du futur injectées et attrapées (la seconde
  seulement après avoir corrigé l'échantillonnage du contrôle). QC **219 verts**.
- Relancer : `python -m trading.recherche.figures_lancer` puis `figures_rapport` et `rapport`.

### 🎯 3e VIDÉO « SNIPER ENTRY » du 2026-09-17 soir : verdict NON (rapport : `trading/RECHERCHE-SNIPER.md`)

Mongazi : « analyse en profondeur, apprends parfaitement la stratégie, backtest le plus proprement
possible, news et meilleures heures comprises, capital de 10 000 $ ».
- **Méthode apprise** (`trading/recherche/METHODE-SNIPER.md`) : EMA 200 M15, sommet M15 balayé par une
  bougie de couleur opposée qui clôture en deçà, rectangle clôture→mèche, entrée sur clôture M1 hors du
  rectangle, stop derrière la mèche, 3 R minimum. Vidéo transcrite ET regardée : **EUR/USD Tickmill en
  heure de New York**, 4 exemples retrouvés **au dixième de pip** dans les bougies Deriv (serveur UTC).
- **Fidélité** : exemples 1, 2, 3 détectés à la minute et gagnants comme à l'écran ; exemple 4 non
  (clôture Deriv 0,3 pip au-dessus du sommet). Structure « majeure » (pivots M15 de 12) choisie sur ses
  exemples AVANT tout résultat.
- **Résultats (coûts Deriv, bid/ask minute par minute)** : EUR/USD 2019-2026 **2 941 trades, 23,8 %,
  -0,113 R** ; NAS100 2024-2026 **1 070 trades, 24,7 %, -0,075 R**. **Sans aucun coût : -0,020 R et
  +0,015 R** (hasard). Chaque année perd sur EUR/USD. P(5 pertes d'affilée sur 100) = 100 %.
- **10 000 $ à 1 %** : EUR/USD → **273 $** (-97 %) ; NAS100 → 4 015 $ (-60 %) ; en NEBULA PRO → 7 970 $
  (arrêt total à -20 % le 2022-05-13) et 9 557 $, parce que le levier ×3 ramène le risque réel à ~0,17 %.
- Annonces, meilleures heures (choisies sur 80 %, contrôle sur 20 %), 64 variantes en walk-forward :
  **tout négatif**. Registre 124 → **146 tests, 0 survit**. **Rien d'intégré.**
- **Fait en chemin** : `recherche/annonces.py` (402 semaines Forex Factory, horodatage Unix, NFP/IPC à
  08:30 NY vérifiés 100 %) ⛔ jeu Hugging Face écarté (40-50 % des annonces à 00:00) · `spread_horaire.py`
  (⛔ Deriv ne sert AUCUN tick passé ; profil par minute en heure de NEW YORK tiré des bougies 2025-2026,
  rollover 17:00 NY jusqu'à 100 points) · `sniper.py` (numba, bid/ask, stop élargi au minimum Deriv) ·
  `compte.py` (10 000 $, `dimensionner`, verrous PRO) · `sniper_lancer.py`, `sniper_rapport.py`,
  `sniper_planches.py` (planches OpenCV regardées) · `_qc_sniper.py` **20 contrôles, prouvés rouges** sur
  3 fautes injectées · `banc.simuler` accepte un objet `simuler_banc`.
- Relancer : `python -m trading.recherche.sniper_lancer tout` puis `python -m trading.recherche.sniper_rapport`
  et `python -m trading.recherche.rapport`.

### 🔬 RECHERCHE DE STRATÉGIES du 2026-09-17 : verdict NON (rapport : `trading/RECHERCHE-STRATEGIES.md`)

**Mise à jour du soir** : MT5 en « Unlimited » (fait par Mongazi) → EUR/USD M1 depuis 2019, M5-M30 depuis
2012, H1-H4 depuis 2005 ; **124 tests sur M1, M5, M15, M30, H1, H4, 0 après correction**. Objectif de
Mongazi **1:2 ET plus de 50 %** : 1 test à 53,8 % de gagnants mais 300 sorties par le temps sur 320 et
1 objectif atteint ; **aucun** test où plus de la moitié des trades atteignent 2 R. Piste unique :
Hugo FX transposé EUR/USD H4, +0,366 R sur 70 trades en 21 ans (25,7 %, années 2023-2026 perdantes).
Le bloc ci-dessous date de l'après-midi (3 mois de M1) : ses chiffres sont remplacés par le rapport.

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

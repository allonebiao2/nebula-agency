# NEBULA TRADER — journal d'avancement

Mis à jour le **2026-09-16, fin de nuit** (code au commit `724fe99`). Une ligne par brique,
avec son pourcentage réel.

> ⚠️ **Un pourcentage ici mesure ce qui est ÉCRIT ET TESTÉ, pas ce qui est
> prévu.** Une brique conçue mais non codée vaut 0 %. Une brique codée mais
> jamais exécutée ne dépasse pas 70 %.

---

## 🔴 POINT D'ARRÊT EXACT (à lire en premier en reprenant)

**On est au milieu de la VAGUE 4 (EUR/USD + NAS100)** du plan d'intégration du cahier des
charges v2 (`trading/CAHIER-DES-CHARGES.md` §9). Les vagues 1, 2 et 3 sont finies, commitées
et poussées (`418f4be`, `4db053b`).

**État du code à l'arrêt** : tout compile, **QC 134 verts / 0 rouge**, commité en
`724fe99`. ⚠️ **Rien de la vague 4 n'a tourné en direct** : l'application est **arrêtée**
(port 8765 libre) et aucun contrôle QC n'exerce encore la boucle multi-instruments.
Un QC vert ici veut dire « rien d'ancien n'est cassé », pas « le NAS100 marche ».

### Ce qui est FAIT dans la vague 4

| Fichier | Ce qui a été fait |
|---|---|
| `noyau/courtier.py` | `ALIAS` (NAS100 → NAS100, US Tech 100, USTEC, US100, NDX100…) + `candidats_symbole(base, noms)` fonction pure, utilisée par `trouver_symbole` |
| `noyau/donnees_mt5.py` | `--base NAS100` : historique + profil exportés. **Swap mode 5/6** (taux annuel en %) converti en points par lot par nuit |
| `trading/donnees/` (ignoré par git) | `NAS100_H4_mt5.npz` (4 250 barres **depuis le 2024-01-22 seulement**), `NAS100_D1_mt5.npz`, `NAS100_courtier_mt5.json` (Deriv : symbole **« US Tech 100 »**, point 0,01, lot min **0,1**, pas 0,1, contrat 1, stops level 150, spread médian **70 points**, swap_mode 5) |
| `backtest/walkforward.py` | fenêtres **en mois** (`_decaler_mois`, `mois_apprentissage`, `mois_test`), `trades_R` dans le rapport |
| `outils/walkforward.py` | `--symbole`, `--mois-apprentissage`, `--mois-test`, `--min-trades` ; rapport nommé **`walkforward_{strat}_{SYM}_{tf}[_variante].json`** avec `symbole`, `fenetres_mois`, `min_trades_apprentissage` (les rapports EURUSD ont été renommés ; `trading/rapports/` est ignoré par git) |
| `config.toml` · `noyau/config.py` | `[marche] symboles = ["EURUSD", "NAS100"]`, `positions_simultanees_max = 2` ; `Marche.symboles` + propriété **`liste`** (`symboles` ou, à défaut, `(symbole,)`). `symbole` reste l'instrument **principal** (Monte Carlo, calibrage) |
| `live/agent.py` | `@dataclass MarcheLive(base, nom, specs, executeur)`, `self.marches` construit dans `_assurer_connexion` depuis `cfg.marche.liste` (symbole introuvable = alerte et on continue ; le 1er = principal, recopié dans `self.symbole/specs/executeur` pour la compatibilité) · `_toutes_positions()` · `_marche_de(position)` · le cycle boucle **marchés × stratégies** vers `_analyser(nom, marche, …)` · santé CUSUM par clé **`"stratégie · SYMBOLE"`** · **une position par instrument** (« une position déjà ouverte sur NAS100 ») · urgence, gestion des positions, fermeture et chien de garde passent par l'exécuteur **du marché de la position** · `symbole` dans les positions et `marches` dans l'instantané |
| `backtest/montecarlo.py` | `rapport_actif(…, symbole)` et `pour_interface(…, symbole)` cherchent le rapport **de l'instrument** |
| `noyau/reglages.py` · `interface/serveur.py` · `interface/chat.py` · `outils/capital.py` | passent le symbole principal (capital : EURUSD) ; `/api/strategies` renvoie `symbole` et `fenetres_mois` |
| `interface/statique/app.js` | onglets de rapport « EURUSD · week-end gardé · actif », avertissement **« Historique court »** sous 48 mois d'apprentissage, colonne **Instrument** dans les positions, symbole dans les décisions |

### Ce que le NAS100 a donné (mesuré, à ne pas sur-interpréter)

- **Walk-forward 12 mois → 6 mois, 15 trades minimum, week-end gardé** :
  `cassure_donchian` = **1 fenêtre tradée sur 3, 2 trades** (+1,06 R) → **rien de prouvé** ;
  `retour_moyenne` = **0 fenêtre tradée** (aucun réglage n'atteint 15 trades en 12 mois).
- Conséquence dans l'agent : cassure prend les réglages de la seule fenêtre
  (`periode_canal 20, atr_stop 2.0, rr 3.0`), retour à la moyenne tourne avec ses
  **réglages par défaut** (« walk-forward vide »). En démo et en observation c'est acceptable ;
  **ce n'est pas une validation**.
- **Capital minimum mesuré** (stop médian 2 × ATR H4 sur un an) : EUR/USD stop 440 points,
  lot minimum = **4,40 $** de risque → **440 $ à 1 %**, 220 $ à 2 %. **NAS100 stop 33 721
  points, lot minimum 0,1 = 33,72 $ de risque → 3 372 $ à 1 %, 1 686 $ à 2 %**. Deriv n'a pas
  de compte cent : **sous ~1 700 $, le NAS100 ne passera presque jamais** en PRO. En BOOST à
  10 %, ~340 $.

### Ce qui RESTE dans la vague 4, dans cet ordre

1. **QC du multi-instruments, avec témoins** (bloc à ajouter dans `outils/qc.py`) :
   `candidats_symbole` (NAS100 trouve « US Tech 100 », EURUSD trouve `EURUSDm`, rien de faux) ·
   `Marche.liste` (repli sur `symbole`) · walk-forward en mois (`_decaler_mois` en fin de mois) ·
   coût de swap mode 5 · `montecarlo.rapport_actif(symbole="NAS100")` **ne prend jamais** un
   rapport EURUSD · agent : `_marche_de` route une position vers le bon exécuteur, **une position
   EURUSD ouverte ne bloque PAS le NAS100** (témoin) mais bloque un 2e EURUSD, instantané publié
   avec deux marchés.
2. **Exposition par facteur** (les deux instruments sont exposés au USD) : non fait. Aujourd'hui
   seuls `positions_simultanees_max = 2` et `exposition_totale_max_pct` s'appliquent.
3. **Heures de séance de l'indice** (le NAS100 a une coupure quotidienne et ferme plus tôt le
   vendredi) : non lues chez le courtier, non gérées. Le calendrier économique filtre
   `USD, EUR`, ce qui couvre déjà le NAS100.
4. **Relancer l'agent** (`python -m trading.app`) et vérifier dans le journal : connexion,
   `trouver_symbole` trouve « US Tech 100 » **en direct**, une analyse par bougie H4 **par
   marché**, aucun plantage sur un cycle complet ; captures **1440 et 390** des pages
   Stratégies, Positions, Décisions.
5. **Reconstruire le paquet** (`python -m trading.empaquetage.construire`) et vérifier qu'il
   embarque les rapports NAS100 et aucun secret.
6. **Mettre à jour** ce journal, `CAHIER-DES-CHARGES.md` §9, `CLAUDE.md`, la conversation du
   jour ; commit + push après `git grep` du mot de passe et de la clé privée.

### Après la vague 4 (déjà décidé, pas commencé)

Filtre **D1** · 3 stratégies (**momentum, range, cassure de structure**) · indicateurs RSI,
MACD, Bollinger, structure HH/HL · **garde contre les tests multiples** (plus on essaie de
stratégies, plus l'une gagne par hasard) · **méta-labeling** (scikit-learn, surveiller le
disque) · **Telegram**.

### Ce qui n'appartient qu'à Mongazi

- Prix, page de vente, paiement, remise de licence.
- ⛔ **Révoquer le jeton `pat_…` collé en clair** le 2026-09-16.
- La **porte démo** exige 30 jours ET 30 trades : au rythme EUR/USD H4 (~2,3 trades/mois),
  c'est **environ un an** de démo avant le réel.
- Le capital du NAS100 (voir ci-dessus) et le risque BOOST à 10 % (46 % de chances de perdre
  la moitié en un an avec la stratégie actuelle).
- Retirer de l'Observation du marché MT5 les symboles inutiles (le terminal télécharge
  l'historique de tout ce qui y est affiché ; disque C: à **14 Go libres** le 2026-09-16).

---

## Avancement global : **66 %**

```
Socle de discipline   ████████████████████  100 %   videur, 8 verrous, profils PRO/BOOST (QC 134 verts)
Mesure (backtest)     ████████████████████  100 %   walk-forward en années ou en mois, Monte Carlo
Données               ██████████████████░░   90 %   EUR/USD 20 ans · NAS100 depuis 2024-01 seulement
Courtier / exécution  ███████████████░░░░░   75 %   agent en observation · multi-instruments jamais lancé
Surveillance          ████████████████░░░░   80 %   CUSUM, chien de garde, portes, rapport hebdo
Interface + produit   █████████████████░░░   85 %   profils, BOOST, Évolution · paquet pas reconstruit depuis
Intelligence          ░░░░░░░░░░░░░░░░░░░░    0 %   AUCUN AVANTAGE PROUVÉ : la priorité après la vague 4
Vente en ligne        ██░░░░░░░░░░░░░░░░░░   10 %   licences signées prêtes, ni page ni paiement
```

⚠️ **Le chiffre qui compte n'est pas le pourcentage : c'est que le walk-forward
n'a trouvé aucun avantage statistique**, ni sur EUR/USD (+0,040 R sur 436 trades) ni sur
NAS100 (2 trades). Un produit fini autour d'une stratégie sans edge reste un produit qui ne
gagne rien.

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
| `noyau/courtier.py` · `identifiants.py` · `coffre.py` | **90 %** | ✅ alias de symboles · ⏳ « US Tech 100 » trouvé à l'export, pas encore par l'agent en direct |
| `noyau/reglages.py` | **100 %** | ✅ profils, seuil d'arrêt **calibré au Monte Carlo** injecté (en cache) |
| `noyau/licence.py` Ed25519 hors ligne | **100 %** | ✅ |
| `backtest/moteur.py` | **100 %** | ✅ suit paliers et poche comme le direct |
| `backtest/walkforward.py` | **100 %** | ✅ années ou mois, `trades_R` |
| `backtest/montecarlo.py` | **100 %** | ✅ bootstrap par blocs de 5, seuil = p99 sur 2 ans × 1,2 plafonné à 35 %, par instrument |
| `apprentissage/sante.py` CUSUM | **90 %** | ✅ 0 % de fausses pauses, 76 % de détection d'une chute de 0,6 R en 60 trades · ⏳ jamais déclenché en direct |
| `apprentissage/analyse.py` rapport hebdo | **85 %** | ✅ par stratégie, symbole, heure, jour, régime ; non concluant sous 20 trades |
| `apprentissage/porte.py` portes démo et BOOST réel | **90 %** | ✅ exigées par `execution.autorisation` |
| `strategies/` | **30 %** | 2 écrites, **0 rentable** · ⏳ filtre D1, momentum, range, cassure de structure |
| `live/journal.py` SQLite | **100 %** | ✅ `symbole`, `profil`, `risque_choisi`, glissement par ordre (migrations) |
| `live/execution.py` | **80 %** | ✅ glissement mesuré, `poser_stop` · ⛔ **aucun ordre réel envoyé** |
| `live/agent.py` la boucle | **65 %** | ✅ vagues 1-3 tournées en observation · ⏳ **boucle multi-instruments écrite, jamais lancée** |
| `interface/` serveur + chat + pages | **85 %** | ✅ profils, BOOST avec probabilités, Évolution · ⏳ onglets par symbole jamais regardés en capture |
| `empaquetage/construire.py` | **75 %** | ✅ exe 44 Mo (avant les vagues) · ⏳ à reconstruire |
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

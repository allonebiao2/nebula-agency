# NEBULA TRADER — journal d'avancement

Mis à jour le **2026-09-16**. Une ligne par brique, avec son pourcentage réel.

> ⚠️ **Un pourcentage ici mesure ce qui est ÉCRIT ET TESTÉ, pas ce qui est
> prévu.** Une brique conçue mais non codée vaut 0 %. Une brique codée mais
> jamais exécutée ne dépasse pas 70 %.

---

## Avancement global : **36 %**

```
Socle de discipline   ████████████████████  100 %   fait et testé
Mesure (backtest)     █████████████████░░░   87 %   tourne sur données réelles
Données               █████████████░░░░░░░   65 %   15 ans chez MT5, pas encore exportés
Courtier / exécution  ███████████░░░░░░░░░   55 %   connecté, ordre validé, aucun envoyé
Intelligence          ░░░░░░░░░░░░░░░░░░░░    0 %   rien de commencé
Revente (MQL5/ONNX)   ░░░░░░░░░░░░░░░░░░░░    0 %   rien de commencé
```

L'ordre est voulu : **la discipline d'abord, l'intelligence ensuite.** Un modèle
brillant sur un socle de risque troué vide un compte plus vite qu'une règle
bête bien encadrée.

---

## Le détail

| Brique | % | État |
|---|---|---|
| `config.toml` — paramètres de risque en amont | **100 %** | ✅ |
| `noyau/config.py` — le videur | **100 %** | ✅ 6 refus vérifiés |
| `noyau/risque.py` — dimensionnement + invariant du stop | **100 %** | ✅ testé sur 6 tailles de compte |
| `noyau/plan.py` — PlanDeTrade + 8 verrous | **90 %** | ✅ 9 scénarios · ⏳ manque le vrai calendrier économique |
| `backtest/metriques.py` — dont la taille d'échantillon | **100 %** | ✅ |
| `backtest/couts.py` — spread, slippage, commission, swap | **95 %** | ✅ · ⏳ commission réelle à lire chez le courtier |
| `backtest/moteur.py` — simulateur barre par barre | **85 %** | ✅ tourne · ⏳ calendrier, journal SQLite |
| `noyau/donnees_deriv.py` — historique API publique | **60 %** | ✅ marche sans jeton · ⛔ **1 an maximum** |
| `noyau/courtier.py` — adaptateur 12 valeurs lues | **90 %** | ✅ **exécuté le 2026-09-16** · 2 défauts corrigés · `order_check` accepté |
| Historique MT5 (Deriv-Demo) | **20 %** | ✅ **25 000 barres H4 depuis 2011-02-24** mesurées · ⏳ export vers `donnees/` pas écrit |
| `noyau/identifiants.py` — profils multi-courtiers | **100 %** | ✅ connexion réelle par identifiants explicites |
| `strategies/` — cassure Donchian | **20 %** | 1 candidate sur 4 prévues |
| Walk-forward | **0 %** | rien |
| Journal SQLite (= jeu d'entraînement) | **0 %** | rien |
| Meta-labeling | **0 %** | conçu, pas codé |
| Champion / challenger | **0 %** | conçu, pas codé |
| Auto-surveillance réel vs backtest | **0 %** | conçu, pas codé |
| Exécution live | **0 %** | rien |
| Telegram (alertes + commandes) | **0 %** | rien |
| Export ONNX + EA MQL5 | **0 %** | rien |

---

## ⛔ Ce qui bloque, par ordre de coût

### ✅ P0-1 · Le mot de passe du compte démo MT5 : RÉSOLU le 2026-09-16
Posé dans `secrets/mt5.env` (compte `6305888` @ `Deriv-Demo`, mot de passe
**maître**). Connexion réelle, 10 000 $ démo, levier 1:1000, couverture, serveur
**UTC+0**. Les quatre autorisations sont vertes (compte, robots, bouton Trading
Algo, API Python) et le courtier **accepte** un ordre fictif de 0,01 lot en
`order_check` (remplissage **FOK**, stops level 20 points, marge 1,15 $).
**Aucun ordre n'a été envoyé.**

### P0-2 · L'historique est trop court pour conclure
Mesuré le 2026-09-16 : l'API publique Deriv plafonne à **un an**, quelle que
soit l'unité de temps (D1 260 barres, H4 1 555, H1 3 471). À ~3 trades par mois,
ça fait ~35 trades : **très en dessous des 100** nécessaires pour qu'un taux de
réussite veuille dire quelque chose.

Trois sorties :
1. ✅ **Le terminal MT5 : 25 000 barres H4 depuis le 2011-02-24** (mesuré le
   2026-09-16), soit ~15 ans et **~500 trades** au rythme actuel. Le terminal
   télécharge l'historique **à la minute**, une année par minute en remontant,
   ~22 Mo par année. ⏳ **Reste à écrire l'export** vers `trading/donnees/`.
   ⚠️ Le disque C: n'avait que **6 Go libres** ce jour-là.
2. **Dukascopy** (gratuit, sans clé, remonte à 2003). ⏳ Le format d'URL essayé
   le 2026-09-16 rend 404/503, à creuser.
3. **Stooq / Yahoo** : quotidien seulement, donc inutile pour un système H4.

### P0-3 · La décision de capital
Mesuré : avec un stop H4 de 70 pips à 1 %, le lot minimum risque **7 $**, donc
**tout compte sous ~700 $ voit TOUS ses trades refusés**. Trois sorties : compte
cent, accepter 2 % (plancher ~350 $), ou attendre le capital.
**Personne d'autre que Mongazi ne peut trancher.**

---

## La suite, par priorité

| Prio | Quoi | Pourquoi maintenant |
|---|---|---|
| **P1** | **Journal SQLite** | c'est le **jeu de données d'entraînement** : sans lui, l'auto-amélioration est un mot creux. Rien de l'intelligence n'est possible avant |
| **P1** | **Walk-forward** | la seule validation acceptée. Sans elle, tout chiffre de backtest est une coïncidence non réfutée |
| **P1** | **Calendrier économique** | le verrou Q5 s'abstient faute de données : il bloque tout, donc il coûte des trades |
| **P2** | **3 stratégies candidates de plus** | retour à la moyenne, momentum D1, cassure de session. On ne garde que ce qui survit |
| **P2** | **Meta-labeling** | le modèle qui filtre les signaux de la règle primaire |
| **P2** | **Auto-surveillance réel vs backtest** | la capacité que presque aucun robot retail n'a : dire « mon edge est mort » avant 40 % de drawdown |
| **P3** | **Exécution live + Telegram** | inutile tant qu'aucun edge n'est prouvé |
| **P3** | **Champion / challenger** | demande ≥ 200 trades journalisés |
| **P4** | **Export ONNX + EA MQL5** | la revente. Découle de la rentabilité, pas l'inverse |

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

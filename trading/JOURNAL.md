# NEBULA TRADER — journal d'avancement

Mis à jour le **2026-09-16**. Une ligne par brique, avec son pourcentage réel.

> ⚠️ **Un pourcentage ici mesure ce qui est ÉCRIT ET TESTÉ, pas ce qui est
> prévu.** Une brique conçue mais non codée vaut 0 %. Une brique codée mais
> jamais exécutée ne dépasse pas 70 %.

---

## Avancement global : **31 %**

```
Socle de discipline   ████████████████████  100 %   fait et testé
Mesure (backtest)     █████████████████░░░   87 %   tourne sur données réelles
Données               ████████████░░░░░░░░   60 %   1 an seulement
Courtier / exécution  ██████░░░░░░░░░░░░░░   30 %   écrit, jamais connecté
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
| `noyau/courtier.py` — adaptateur 12 valeurs lues | **70 %** | 🔧 écrit, **jamais exécuté** (pont MT5 bloqué) |
| `noyau/identifiants.py` — profils multi-courtiers | **90 %** | ✅ · ⏳ mot de passe manquant |
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

### P0-1 · Le mot de passe du compte démo MT5
**Bloque : l'historique long, les vrais spreads, et toute exécution.**
À coller dans `secrets/mt5.env` (login `31759703` et serveur `Deriv-Demo` déjà
remplis). ⚠️ Le mot de passe **maître**, pas celui d'investisseur : l'investisseur
donne un accès en lecture seule, le terminal se connecte quand même et **tous
les ordres sont rejetés** — une panne qui ressemble à un bug.

### P0-2 · L'historique est trop court pour conclure
Mesuré le 2026-09-16 : l'API publique Deriv plafonne à **un an**, quelle que
soit l'unité de temps (D1 260 barres, H4 1 555, H1 3 471). À ~3 trades par mois,
ça fait ~35 trades : **très en dessous des 100** nécessaires pour qu'un taux de
réussite veuille dire quelque chose.

Trois sorties :
1. **Le terminal MT5** en porte plusieurs années — dépend de P0-1.
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

**⛔ Le pont MT5 refuse toujours : `-6 Authorization failed`.** Éliminé en
mesurant : identifiants, chemin, bac à sable, Git Bash, version du paquet
(5735 et 6180), courtier (Deriv **et** Exness échouent pareil), état du
terminal, et le bouton Trading Algo (vérifié vert par Mongazi).
Corrigé en route sans que ça suffise : `[Experts] Api=0 -> 1` et `Enabled=0 -> 1`
dans les deux terminaux (`AllowDllImport` laissé à 0, sauvegardes
`.avant-nebula`). **Reste à essayer : la connexion par identifiants explicites**
(`mt5.initialize(login=, password=, server=)`), c'est P0-1.

**⛔ Le jeton collé le 2026-09-16 n'est pas un jeton Deriv** (`InvalidToken` ;
format `pat_` + 64 hex, alors que Deriv utilise `a1-…`). Il a été collé en clair
dans une conversation : **à révoquer quel que soit le service auquel il
appartient**.

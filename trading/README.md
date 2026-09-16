# NEBULA Trader

Agent de trading EUR/USD sur MetaTrader 5, avec son interface, conçu pour trois
objectifs dans cet ordre : **être rentable**, **s'améliorer seul**, **être vendable**.
L'objectif 3 découle du 1 : un robot se vend sur un historique réel vérifié,
jamais sur un backtest.

---

## Lancer

```bash
python -m trading.app                      # agent + interface, ouvre le navigateur
python -m trading.outils.qc                # contrôle qualité (79 contrôles), à passer vert
python -m trading.empaquetage.construire   # le produit installable (.zip, sans Python)
```

L'interface est une application web **locale** (127.0.0.1, jeton de session) :

| Page | Ce qu'on y fait |
|---|---|
| Tableau de bord | équité, jour, drawdown, positions, **les 8 verrous du dernier signal**, flux en direct, prochaine analyse, annonces |
| Parler à l'agent | conversation (Claude avec outils, ou répondeur local sans clé). L'agent **rend le système plus prudent seul, jamais plus risqué** : il propose, on confirme |
| Risque | disjoncteurs et discipline en jauges, **trader avec n'importe quel capital** |
| Décisions | chaque signal, son verdict et le détail des verrous |
| Trades | l'historique réel et ses statistiques |
| Stratégies | activer/désactiver, résultats **hors échantillon** du walk-forward |
| Réglages | 34 réglages validés par le videur, 6 protections non modifiables, historique |
| Compte et licence | identifiants MT5 (chiffrés par Windows), licence, clé de l'assistant |

Trois modes : **observation** (aucun ordre, par défaut) · **démo** (compte démo
seulement) · **réel** (licence + compte réel + plafond de capital).

---

## Ce que le walk-forward dit (2026-09-16)

Quinze ans d'EUR/USD H4 chez Deriv (2011-2026), réglages choisis sur 4 ans et
appliqués à l'année suivante, coûts réels (spread médian 3 points mesuré sur
147 161 ticks, swaps, 1 point de glissement par sens) :

| Stratégie | Trades | Espérance | PF | 10 000 → | DD max |
|---|---|---|---|---|---|
| Cassure, positions gardées le week-end | 436 | +0,040 R | 1,07 | 11 488 | 15,3 % |
| Cassure, fermeture du vendredi | 497 | −0,007 R | 0,97 | 9 415 | 21,1 % |
| Retour à la moyenne | 311 | −0,081 R | 0,82 | 7 663 | 30,9 % |

**Aucune n'est statistiquement distinguable de zéro.** L'avantage reste à trouver :
c'est le chantier « intelligence » (filtre D1, nouvelles stratégies, meta-labeling).
Ne pas passer en réel sur ces chiffres.

---

## Petit capital

Stop H4 médian mesuré : 527 points (53 pips). Sur un compte standard, le lot
minimum risque ~5,3 $ : sous 250 $, aucun signal ne tient dans le risque.

1. **Compte cent** détecté automatiquement (USC, EUC) : dès **10 $**, 98 à 100 %
   des signaux passent à 1 % exact. Mesuré en backtest : 10 $ en cent prend les
   mêmes 71 trades que 10 000 $ en standard.
2. **Lot minimum toléré** jusqu'à `risque_max_petit_compte_pct` (2 % au plus, plafond
   écrit dans le code) ; chaque trade concerné le dit.
3. **Attente** : au-delà, CE trade est refusé et l'agent attend un stop plus court.

`python -m trading.outils.capital` refait la mesure.

---

## Architecture

```
noyau/        config (le videur) · reglages · risque · plan (8 verrous) · capital
              courtier (12 valeurs lues, jamais supposées) · identifiants · coffre (DPAPI)
              calendrier (annonces) · licence (Ed25519) · donnees_mt5 · chemins
strategies/   cassure_donchian · retour_moyenne · catalogue
backtest/     moteur (coûts réels, mêmes verrous que le live) · walkforward · metriques
live/         agent (la boucle, seul fil qui parle à MT5) · execution · journal (SQLite)
interface/    serveur (FastAPI local) · chat · statique/ (HTML/CSS/JS sans bibliothèque)
outils/       qc · walkforward · capital · licence · profil_courtier
empaquetage/  construire (QC vert → PyInstaller → inspection des secrets → .zip)
```

**Données utilisateur** : `trading/donnees/` en développement, `%APPDATA%\NEBULA Trader`
une fois installé (journal, réglages, licence, identifiants chiffrés).

---

## Les règles qui ne se négocient pas

1. **Aucune valeur de courtier en dur** : symbole, fuseau, contrat, lot, remplissage se lisent.
2. **Tout ordre part avec son stop déposé chez le courtier**, et on relit la position : sans stop, elle est fermée.
3. **Un stop ne s'élargit jamais**, pas même demandé par l'agent.
4. **Ni martingale, ni grille, ni moyenne à la baisse** : non implémentés, non réglables.
5. **Jamais d'apprentissage en direct.**
6. **Le backtest facture les coûts réels** et appelle les mêmes verrous que le live.
7. **Aucun rendement promis**, nulle part, ni dans l'interface ni dans l'agent.
8. **Tout changement de réglage repasse par le videur**, et l'agent ne peut augmenter le risque que sur confirmation.

## Pièges MT5 mesurés

- `[Experts] Api=1` dans `common.ini` **coupe** le trading par l'API Python (c'est une case « désactiver »).
- MT5 **éteint le Trading Algo à chaque changement de compte**.
- `SYMBOL_FILLING_FOK/IOC` n'existent pas dans le paquet Python (drapeaux 1 et 2).
- Lire l'historique **par année** : une plage de vingt ans d'un coup renvoie `Call failed`.
- La page `LISEZ-MOI.txt` du paquet et la page « Compte et licence » expliquent ces réglages au client.

Détail des principes : `DOCTRINE.md` · avancement : `JOURNAL.md`.

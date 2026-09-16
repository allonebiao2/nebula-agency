# 2026-09-17 · NEBULA Trader, vague 4 finie : EUR/USD + NAS100, et les chiffres d'hier tombent

Mongazi : « continue le travail qu'on faisait ». Reprise au point d'arrêt de `trading/JOURNAL.md`
(vague 4 écrite le 16 au soir, jamais lancée, QC 134 verts). Fin de session : **vague 4 lancée en
direct en observation, QC 176 verts**, et **tous les résultats de walk-forward recalculés**,
parce que trois défauts faisaient mentir les chiffres affichés.

---

## Ce qui a été construit

- **`noyau/instruments.py`** : ce qui change d'un instrument à l'autre (noms chez le courtier,
  plafonds, facteurs de risque). ⛔ La recherche de symbole prenait **« US1000 » pour le NAS100**
  (un suffixe de compte ne commence pas par un chiffre).
- **Plafonds propres à chaque instrument** (`[execution.par_instrument.NAS100]`, en prix).
- **Exposition par facteur** (EUR/USD et NAS100 partagent le dollar) dans le verrou 3.
- **`marche_ferme()`** : pas d'ordre sur un instrument dont la cotation est figée (jour férié
  US, clôture anticipée). Mesuré : à l'échelle H4 aucune bougie du NAS100 ne manque, la coupure
  quotidienne tombe dans la bougie de 20 h ; ce sont les fériés qui ferment (4 vendredis sur 49).
  Sans ce garde, trois rejets en une heure mettaient tout l'agent en pause, EUR/USD compris.
- ⛔ **Même cycle, état périmé** : EUR/USD et NAS100 ferment leur bougie H4 à la même heure, le
  second instrument décidait sur l'état d'avant la position du premier. Positions et risque
  sont relus après chaque ouverture.
- **Empreinte des règles** dans chaque rapport, comparée par l'interface et l'agent.
- **42 contrôles** neufs, avec témoins, prouvés rouges sur l'ancien code (le bloc échoue, les
  134 anciens restent verts).

## ⛔ Les trois défauts qui faisaient mentir les chiffres

**1. Le plafond de spread de 20 points était commun.** Calibré sur l'EUR/USD (2 à 3 points de
spread), il refusait **92,8 % des bougies du NAS100** (70 points fixes). « NAS100 : 2 trades,
rien de prouvé » mesurait le plafond. Après correction : **49 trades, −0,095 R**.

**2. Les rapports EUR/USD dataient d'avant « R:R minimum 1:2 ».** Trouvé en voulant prouver que
la vague 4 était neutre pour l'EUR/USD : le code d'avant et d'après donnaient **exactement** les
mêmes trades (neutralité prouvée), mais tous deux **−0,045 R sur 372 trades**, loin des
**+0,040 R sur 436** affichés partout. Quatre essais en parallèle, un réglage à la fois : levier
et trades par jour ne changent rien, **seul le R:R à 1,0 ramène 436 trades et +0,0399 R**.

**3. L'outil n'imposait que `--sans-weekend`.** Le `config.toml` gardant le week-end, la variante
« fermeture du vendredi » ne fermait rien, en l'annonçant. Deux rapports identiques au trade près.

⚠️ **Un faux positif de ma main, vu en direct** : la première empreinte incluait l'arrêt total,
qui est calibré au Monte Carlo à partir du rapport lui-même (20 % dans le fichier, 26 % appliqués).
L'agent a déclaré périmés six rapports recalculés à la minute. Exclu, contrôle ajouté, rapports
recalculés (pas réestampillés : une empreinte écrite sans refaire la mesure est ce qu'elle doit
empêcher).

## Les chiffres, sous les règles réellement appliquées

| Stratégie | Trades | R | 10 000 $ → | DD max |
|---|---|---|---|---|
| EUR/USD cassure, week-end gardé | 372 | −0,045 | 8 074 | 27,5 % |
| EUR/USD cassure, fermeture du vendredi | 454 | −0,021 | 8 632 | 26,3 % |
| EUR/USD retour moyenne, vendredi / week-end | 308 / 348 | −0,059 / −0,077 | 8 399 / 7 696 | 26,0 / 34,8 % |
| NAS100 cassure (12 → 6 mois) | 49 | −0,095 | 9 556 | 6,8 % |
| NAS100 retour moyenne | 39 | −0,218 | 9 295 | 7,1 % |

Arrêt total PRO calibré : **26 %** (23 % annoncé). BOOST 10 % : **55 %** de chances de perdre la
moitié en un an (46 % annoncé).

## ⏳ À Mongazi

- **Week-end gardé ou fermeture du vendredi** : la décision du 16 reposait sur +0,040 contre
  −0,007, c'est aujourd'hui l'inverse (−0,045 contre −0,021). Les deux perdent, aucun n'est
  distinguable de zéro. Rien n'a été changé dans la configuration.
- Garder le NAS100 ou non (−0,095 R sur 49 trades, échantillon court).
- Toujours : révoquer le jeton `pat_…`, prix et vente.

## Fichiers touchés

`trading/noyau/{instruments,config,plan,courtier}.py` · `trading/config.toml` ·
`trading/backtest/moteur.py` · `trading/live/{agent,execution}.py` ·
`trading/outils/{qc,walkforward}.py` · `trading/interface/serveur.py` ·
`trading/interface/statique/app.js` · `trading/JOURNAL.md` · `trading/CAHIER-DES-CHARGES.md` ·
`CLAUDE.md` · `_memoire/lecons.md` · ce fichier · `trading/rapports/` (ignoré par git,
anciens rapports dans `_archive/`)

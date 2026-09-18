# Le plan de risque de NEBULA Trader — échelle 6-4-3 et intérêts composés

> ## ⛔ AVERTISSEMENT DU 2026-09-18 (après-midi) : chiffres invalidés
>
> Ces résultats viennent du simulateur de recherche `banc._simuler_ordres`, qui **n'est pas
> causal** pour les ordres limites : quand plusieurs ordres attendent, il donne le trade au plus
> ancien qui finit par être servi (donc au plus bas), comme s'il savait jusqu'où le prix irait.
> Rejouée avec le moteur de l'agent (l'ordre touché le premier entre), la même stratégie **perd** :
> NAS100 30,8 % de 2 R et −0,103 R par trade, EUR/USD 25,4 % et −0,370 R, sur l'année
> 2025-09 → 2026-09. Détail : `trading/REJEU-1AN.md`. **Ne rien trader sur la foi de ce document.**

> Plan de Mongazi, appliqué le **2026-09-18**. Tous les chiffres de ce document sont **mesurés sur
> les vrais trades** de la stratégie (NAS100 M1, entrée limite au rabais + filtre à 5 %), dont
> 1 467 trades sur les années **scellées** 2020-2023. Aucun n'est recopié d'un tableau.

## La règle, en trois lignes

1. **6 % de risque par trade tant que le capital est à son sommet.**
2. **4 % dès qu'on passe sous le sommet**, **3 % sous -20 %** du sommet.
3. **Retour à 6 % dès qu'un nouveau sommet est touché.** Le risque est toujours un pourcentage du
   capital **du moment** : c'est là qu'agissent les intérêts composés.

Écrit une seule fois, dans `noyau/profils.py::risque_courant` — **le même code décide pour le
backtest et pour l'agent en direct**. Réglé dans `config.toml`, `[profil_boost] paliers_drawdown`.

⚠️ **L'échelle est ancrée sur le risque choisi**, pas écrite en dur : à 6 % elle donne 6-4-3, à 10 %
elle donne 10-6,7-5, à 1 % elle donne 1-0,67-0,5. Sans cet ancrage, elle changerait la décision de
celui qui a choisi 10 % sans le lui dire.

⛔ **Le videur refuse toute échelle dont le risque REMONTE quand le drawdown s'aggrave.** C'est une
martingale : elle double la mise après une perte, et elle finit toujours de la même façon.

## Pourquoi l'échelle : ce qu'elle protège, mesuré

| | pire recul | P(ruine) si l'avantage disparaît |
|---|---|---|
| risque fixe 6 % | 28,8 % | **46,6 %** |
| **échelle 6-4-3** | **23,7 %** | **5,8 %** |
| risque fixe 2 % | 10,0 % | 0,1 % |

*(Monte Carlo, 5 000 tirages de 250 trades, capital 500 $. « L'avantage disparaît » = espérance
ramenée à zéro, la distribution des R gardée telle quelle.)*

**L'échelle ne fait pas gagner plus. Elle fait survivre quand l'avantage s'use.** C'est exactement
l'arithmétique de la planche : six pertes à 6 % coûtent 36 %, six de plus à 4 % amènent à 60 %, six
de plus à 3 % à 78 % — dix-huit pertes consécutives ne ruinent pas.

## Le backtest à n'importe quel capital, avec de vrais lots

`python -m trading.recherche.compte_plan` — lot minimum 0,1, pas de 0,1, **lot maximum 100**, via le
même `noyau/risque.dimensionner` que l'agent. NAS100, 4 ans (2020-2023), 1 467 trades.

| capital de départ | capital final | rendement annuel | pire recul | trades au lot maximum |
|---|---|---|---|---|
| 50 $ | 2 431 336 $ | 1 399 % | 14,1 % | 89 % |
| 500 $ | 2 504 026 $ | 747 % | 14,8 % | 92 % |
| 5 000 $ | 2 614 942 $ | 381 % | 13,7 % | 96 % |
| 100 000 $ | 2 759 491 $ | 130 % | 7,2 % | 100 % |
| 1 000 000 $ | 3 659 491 $ | 38 % | 1,0 % | 100 % |

⛔ **Lisez la dernière colonne, c'est elle qui compte.** Le lot maximum de Deriv (100 lots) plafonne
le risque à environ **1 700 $ par trade** sur le NAS100. Passé ce point, **la croissance cesse d'être
exponentielle** : chaque trade rapporte un montant fixe, et tous les capitaux de départ convergent
vers le même total. C'est pour ça que 50 $ et 1 000 000 $ finissent au même endroit.

**Conséquence directe** : la planche « 5 000 $ → 41 millions en deux ans » ne peut pas se produire
sur un seul compte NAS100 chez Deriv. Le plafond se contourne comme le dit la planche « LES
POSSIBILITÉS » : plusieurs comptes, prop firms, fonds de clients.

## Mois par mois, capital de départ 500 $

48 mois : croissance **médiane 6,2 % par mois**, meilleur mois +490 %, pire mois **+0,4 %**,
**100 % de mois positifs**.

⚠️ **Ce « 100 % de mois positifs » n'est pas une promesse, c'est une conséquence arithmétique** :
avec +0,96 R par trade et 30 trades par mois, un mois négatif demanderait un écart de presque
quatre écarts-types. **Toute cette régularité repose sur une seule hypothèse : que l'avantage mesuré
tienne en direct.** C'est précisément ce que la démo doit vérifier, et rien d'autre ne le peut.

## Ce que le plan ne protège pas

- **Il ne protège pas d'une stratégie qui ne marche plus.** L'échelle ralentit la chute, elle ne
  l'empêche pas : à avantage nul, le capital médian tombe quand même de 500 $ à 343 $ en 250 trades.
- **Il ne protège pas du spread.** La stratégie vit avec les 70 points de Deriv ; au-delà de trois
  fois ce coût, elle ne gagne plus rien (le filtre tient jusqu'à cinq fois).
- **Il ne protège pas d'un ordre limite qui ne serait pas servi.** C'est la seule hypothèse du
  backtest qu'un courtier peut démentir, et c'est le premier chiffre du carnet de suivi.

## Le carnet

`python -m trading.recherche.suivi` écrit **`trading/SUIVI.md`** : une ligne par trade, le palier de
risque appliqué, la série perdante en cours, et **l'écart entre le direct et ce que le backtest
promettait** (intervalle de confiance compris). Il lit le journal de l'agent, il n'invente rien.

⚠️ **Un écart ne se corrige pas le jour même.** On note, on accumule, et on ne change une règle
qu'avec assez de trades pour que le changement ne soit pas du bruit. Toute modification repasse par
le registre et se juge **en avant** : les deux jeux de données scellés sont désormais ouverts.

## Les commandes

```bash
python -m trading.recherche.compte_plan                       # tous les capitaux, vrais lots
python -m trading.recherche.compte_plan --mensuel 500         # le tableau mois par mois
python -m trading.recherche.plan --capital 500 --montecarlo   # la fourchette, pas la promesse
python -m trading.recherche.suivi --reference                 # le carnet et sa référence
python -m trading.recherche._qc_sans_fin                      # 45 contrôles, dont l'échelle
```

# Le backtest le plus long possible — 36 années cumulées, filtre réentraîné en continu

> ## ⛔ AVERTISSEMENT DU 2026-09-18 (après-midi) : chiffres invalidés
>
> Ces résultats viennent du simulateur de recherche `banc._simuler_ordres`, qui **n'est pas
> causal** pour les ordres limites : quand plusieurs ordres attendent, il donne le trade au plus
> ancien qui finit par être servi (donc au plus bas), comme s'il savait jusqu'où le prix irait.
> Rejouée avec le moteur de l'agent (l'ordre touché le premier entre), la même stratégie **perd** :
> NAS100 30,8 % de 2 R et −0,103 R par trade, EUR/USD 25,4 % et −0,370 R, sur l'année
> 2025-09 → 2026-09. Détail : `trading/REJEU-1AN.md`. **Ne rien trader sur la foi de ce document.**

> Écrit le **2026-09-18**. Tous les chiffres viennent de `python -m trading.recherche.long_backtest`.
> Aucun n'est recopié, aucun n'est arrondi à l'avantage.

## Ce qui change par rapport à tout ce qui précède

Jusqu'ici, le filtre était appris **une fois** sur 2013-2019 et appliqué au reste. C'était honnête,
mais ce n'est pas ce qu'un agent aurait fait. Ici il est **réappris tous les trois mois sur tout le
passé disponible**, puis jugé sur les trois mois suivants — 86 réapprentissages sur l'EUR/USD, 47 sur
le NAS100. C'est la simulation de ce qui se serait vraiment passé si l'agent avait tourné depuis le
premier jour.

Trois règles tenues par le code :
- l'apprentissage ne voit que les trades **déjà clos** avant le bloc de test (purge comprise) ;
- le **seuil de sélectivité** de chaque bloc est calculé sur le passé, jamais sur le bloc lui-même ;
- la décision se prend sur la **dernière barre close avant le remplissage**.

## Les résultats

| | **EUR/USD** | **NAS100** |
|---|---|---|
| Période | **2003-05 → 2026-09** (23,4 ans) | **2013-01 → 2026-09** (13,7 ans) |
| Minutes analysées | 8 667 035 | 4 078 642 |
| Trades possibles | 166 511 | 88 666 |
| **Jugés hors échantillon** | **154 119** | **81 411** |
| Réapprentissages | 86 | 47 |

**En gardant les 5 % d'occasions les plus sûres :**

| | EUR/USD | NAS100 |
|---|---|---|
| Trades | 7 146 | 5 881 |
| **2 R atteints** | **63,3 %** | **64,2 %** |
| Espérance | **+0,825 R** | **+0,859 R** |
| Trades par mois | 27,9 | 41,9 |
| R par mois | 23,0 | 36,0 |
| **Années négatives** | **aucune sur 22** | **aucune sur 12** |

**En gardant 10 %** : 59,4 % (EUR/USD) et 59,9 % (NAS100), soit deux fois plus de trades pour
quatre points de réussite en moins.

## Au compte, avec les vrais lots (NAS100, 11,7 ans)

| sélectivité | trades | 50 $ deviennent | %/an | pire recul | série perdante max | mois positifs |
|---|---|---|---|---|---|---|
| **5 %** | 6 073 | **8 192 311 $** | 179 % | **27,9 %** | 8 | **100 %** |
| 10 % | 11 170 | 12 838 915 $ | 190 % | 31,6 % | 9 | 99 % |
| 20 % | 20 445 | 17 804 840 $ | 199 % | **48,9 %** | 14 | 98 % |

**Plus on est sélectif, moins on gagne et moins on souffre.** À 5 %, un trade par jour environ, un
recul maximum de 28 % sur douze ans, et pas un seul mois négatif. À 20 %, on gagne deux fois plus,
mais on traverse un recul de 49 % et des séries de 14 pertes.

## Ce qui a été amélioré, et de combien

| amélioration | avant | après |
|---|---|---|
| Réapprentissage tous les **3 mois** au lieu de 6 | 63,4 % · +0,836 R | **64,2 % · +0,859 R** |
| Historique EUR/USD complété (2012-2018 manquaient) | 8,5 ans | **23,4 ans** |
| Filtre appris une fois → **réappris en continu** | 66,7 % sur 4 ans | 63-64 % sur **36 ans** |

⚠️ Le taux baisse de 66,7 % à 63-64 % : c'est **normal et c'est mieux**. L'ancien chiffre portait sur
quatre années récentes avec un modèle appris juste avant ; le nouveau porte sur trente-six années,
crises comprises, avec un modèle qui n'a jamais rien vu du futur.

## Ce que ça ne dit toujours pas

- **Aucun trade réel n'a été passé.** Ni un dollar, ni un ordre.
- **Le remplissage des ordres limites reste l'hypothèse non vérifiée.** Un simulateur sert toujours ;
  un courtier, pas forcément. C'est le premier chiffre du carnet de suivi.
- **Le plafond de lots de Deriv** (100 sur le NAS100, 20 sur l'EUR/USD) rend la croissance linéaire
  au-delà d'environ 29 000 $ (NAS100) et 10 000 $ (EUR/USD). Voir `PLAN-DE-RISQUE.md`.
- ⛔ **Avec 10 $, le NAS100 est impossible** : son lot minimum (0,1) risque 1,73 $, soit 17 % du
  capital. Il faut **29 $ au minimum**. L'EUR/USD passe dès 10 $ (lot minimum 0,01), mais avec un
  levier de 220, très au-dessus de nos propres plafonds.

## Les commandes

```bash
python -m trading.recherche.long_backtest --marche EURUSD --bloc 3 --parts 0.05 0.10
python -m trading.recherche.long_backtest --marche NAS100 --bloc 3 --capital 50
python -m trading.recherche.modele --marche NAS100 --entrainer     # le modèle que l'agent utilise
python -m trading.live.scalpeur --marche NAS100                    # l'agent, en observation
```

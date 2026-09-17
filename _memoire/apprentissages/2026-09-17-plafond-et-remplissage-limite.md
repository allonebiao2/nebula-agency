# Mesurer le plafond avant de chercher, et ne jamais croire un ordre limite sur parole

*2026-09-17 · NEBULA Trader, recherche d'une stratégie de scalping intraday*

## 1. Le plafond : la mesure qui doit précéder toute recherche de stratégie

Avant de chercher une règle qui atteint « 50 % de trades à 2 R », on mesure **ce qu'atteindrait un
devin parfait**. Sur chaque barre, on étiquette ce qui serait arrivé dans les DEUX sens ; « au moins
un des deux atteint 2 R » est un plafond que ni une règle, ni un modèle, ni une intuition ne
dépasseront.

Mesuré, en intraday (tout fermé le jour même), coûts Deriv :

| | EUR/USD M1 | NAS100 M1 |
|---|---|---|
| meilleur plafond | **57,7 %** (stop 20 points) | **63,8 %** (stop 1 200 points) |
| point mort au même stop | 37,1 % | 34,1 % |
| plafond avec un stop large | 2,8 % (stop 500 points) | 58,3 % (stop 3 500) |

**Ce que ça décide** : viser 70 % de 2 R en intraday est hors de portée (le plafond est à 64 %).
Viser 50 % demande de choisir le bon sens **trois fois sur quatre** parmi les barres où un mouvement
existe. Et un stop large rend l'objectif inatteignable **avant** la fin de la journée : le plafond
s'effondre bien avant que le coût devienne négligeable.

⚠️ La bonne zone est un compromis à deux forces opposées : un stop serré rend 2 R atteignable dans la
journée (le plafond monte) mais fait payer le spread en proportion (le point mort monte aussi). Sur
NAS100 le sommet est vers 1 200 points de stop ; sur EUR/USD vers 30-50 points.

⚠️ **Le point mort n'est pas 33,3 %.** Avec les coûts, les gaps et les sorties de fin de journée, il
se lit dans les trades : `banc.point_mort_objectif`. Mesuré entre 34 % (NAS100 M1, stop large) et
41 % (NAS100, stop de 150 points).

## 2. ⛔ Le piège des ordres limites : « la bougie a touché ma limite » n'est pas un remplissage

Nos bougies sont des prix VENDEUR (bid). Un achat s'exécute au prix ACHETEUR (bid + spread) : l'ordre
n'est donc servi que si le prix descend **un spread plus bas** que la limite. Remplir dès que le bas
de la bougie touche la limite fait entrer sur les creux les plus courts, exactement ceux qui
rebondissent, et fabrique un avantage qui n'existe pas.

Mesuré le 2026-09-17, même stratégie, trois hypothèses de remplissage (`Ordres.k_remplissage`) :

| | touche (k=0) | traverse un spread (k=2) | prudent (k=3) |
|---|---|---|---|
| EUR/USD M1 | **+0,101 R** | +0,017 R | **-0,019 R** |
| EUR/USD M5 | +0,093 R | +0,027 R | -0,006 R |
| NAS100 M1 (Deriv) | +0,199 R | +0,167 R | +0,149 R |

L'EUR/USD était **entièrement** un artefact de remplissage. Le NAS100 de Deriv survit : c'est ce qui
en fait un candidat, pas un résultat.

⚠️ L'amélioration de prix (servi à l'ouverture quand la barre ouvre au-delà de la limite) ne change
presque rien (+0,1687 contre +0,1676 R) : ce n'était pas la source.

## 3. ⛔ Deux ordres limites miroirs : « au moins un des deux gagne » est une tautologie

En mesurant le plafond des entrées limites, on obtient **99,3 %**. C'est faux. À 0,5 R de retrait,
l'achat et la vente ont des objectifs à ±1,5 d et des stops à ∓1,5 d : ce sont deux ordres
exactement opposés. Conditionnellement aux deux remplissages, l'un gagne **forcément**.

Un plafond « au moins un des deux sens » n'a de sens que si l'entrée est **inconditionnelle** (au
marché, à chaque barre). Dès que l'entrée dépend du prix (ordre limite), le conditionnement
fabrique le résultat. Le seul chiffre honnête est alors le taux par sens, rapporté aux ordres
**posés**.

## 4. Forex Factory code « pire que prévu » par 2, pas par -1

`actualBetterWorse` vaut **1 = mieux que prévu, 2 = pire, 0 = conforme**. Lu tel quel, toutes les
mauvaises surprises devenaient des bonnes, avec un poids double. Repéré parce que le compte affichait
**1 654 surprises positives et zéro négative** : une distribution impossible. Après correction :
855 mieux, 799 pire, 500 conformes.

**La leçon générale** : après avoir branché un champ d'une source externe, compter ses valeurs. Une
distribution absurde se voit en une ligne ; un signe inversé ne se voit jamais dans un backtest, il
se contente de rendre le résultat plat.

## 5. Deux détails qui coûtent une soirée

- **Écrire un `.npz` de façon atomique.** Un lecteur qui ouvre un fichier à moitié écrit reçoit
  « File is not a zip file ». On écrit à côté (`.tmp.npz`) puis on remplace.
- **Les heures de week-end sont légitimement vides.** Avec `dukascopy-node`, l'option « réessayer les
  réponses vides » (`-re`) fait échouer le mois entier ; il faut `-fr` (ne pas échouer après les
  tentatives).

## Où c'est écrit

`trading/RECHERCHE-SANS-FIN.md` (protocole), `trading/RECHERCHE-SCALPING.md` (résultats),
`trading/recherche/etiquettes.py`, `carte.py`, `banc.py`, `_qc_sans_fin.py` (35 contrôles).

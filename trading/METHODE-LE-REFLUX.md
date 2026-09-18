# LE REFLUX

## La méthode de trading de NEBULA, expliquée en entier

*Version du 2026-09-18 · NEBULA Agency · Mongazi*

---

> ## ⛔ AVERTISSEMENT DU 2026-09-18 (après-midi) : les chiffres de ce document ne tiennent pas
>
> Le test d'un an demandé par Mongazi a été fait avec **le moteur de l'agent**, minute par
> minute, et il **contredit les sections 3 et 7**.
>
> **Le défaut** : le simulateur de recherche (`banc._simuler_ordres`) traite les ordres limites
> dans l'ordre où ils ont été **posés**. Quand le prix plonge à travers plusieurs ordres d'achat,
> il donne le trade au plus **ancien** qui finit par être servi, c'est-à-dire au plus bas. Il
> « sait » donc que le prix ira jusque-là, et il évite l'ordre du haut, servi le premier, qui
> perd. Aucun courtier ne fait ça : chez lui, c'est l'ordre touché le premier qui entre.
>
> **Mesuré sur la même année et les mêmes prix Deriv (NAS100, 2025-09 → 2026-09)** :
>
> | | trades | 2 R atteints | par trade |
> |---|---|---|---|
> | recherche, sans filtre | 7 174 | 40,0 % | **+0,186 R** |
> | **moteur de l'agent, sans filtre** | 8 011 | 31,0 % | **−0,090 R** |
> | recherche, filtre à 5 % | 340 | 67,3 % | +0,987 R |
> | **moteur de l'agent, filtre à 5 %** | 1 457 | 30,8 % | **−0,103 R** |
>
> Le moteur est **validé contre le banc** (`recherche/_qc_moteur.py`) : quand un seul ordre attend
> à la fois, il donne les mêmes trades au dix-millième de R, et les 208 écarts observés viennent
> tous d'un second défaut, du même côté : le banc laisse un nouvel ordre être servi dans la minute
> même où le trade précédent s'arrête.
>
> **Conséquence** : la méthode telle qu'elle est décrite ici **perd de l'argent**. Ne pas la
> trader, ni en réel ni pour la vendre. Détail et suite : `trading/REJEU-1AN.md`.

---

## 1. Le nom, et pourquoi lui

**Le reflux, c'est la mer qui se retire avant de revenir.**

Cette méthode ne court jamais après le prix. Elle attend qu'il **reflue** vers elle, pose son ordre
plus bas que le marché, et ne prend que les retours qui en valent la peine. Tout est dans ce geste :
**on n'achète pas ce qui monte, on achète ce qui redescend dans une montée.**

Trois mots la résument : **attendre, choisir, sortir avant la nuit.**

---

## 2. L'idée, en une phrase

> Dans le sens de la tendance de l'heure, on pose un ordre d'achat **sous** le prix (ou de vente
> **au-dessus**), on ne le laisse vivre qu'une heure, et on ne garde qu'une occasion sur vingt —
> celle qu'un modèle, entraîné sur vingt-trois ans de marché, juge la plus sûre.

---

## 3. Pourquoi ça marche

Trois mécanismes se cumulent, et aucun n'est une croyance : chacun est mesuré.

**a) Le meilleur prix change la géométrie.** Entrer plus bas rapproche l'objectif et éloigne le stop,
en valeur absolue. Le même mouvement de marché devient un gain là où une entrée au marché aurait
donné une perte.

**b) Un repli court dans une tendance a tendance à rebondir.** C'est l'effet de retour à la moyenne à
l'échelle de la minute. Mesuré : après un repli d'un ATR dans le sens de la tendance, la probabilité
d'atteindre 2 R avant de perdre 1 R passe de 33 % (le hasard) à **40 %**.

**c) La sélection fait le reste.** Toutes les occasions ne se valent pas. Un modèle apprend à
reconnaître celles qui aboutissent : en n'en gardant que **5 %**, le taux passe de 40 % à **63-64 %**.

> **La leçon la plus importante de toute la recherche** : le taux de réussite n'est pas une propriété
> du marché. C'est une propriété de la **sélectivité**. Tout prendre donne 40 %. Choisir donne 64 %.

---

## 4. Les règles exactes

| | règle |
|---|---|
| **Marchés** | NAS100 et EUR/USD, rien d'autre |
| **Unité de temps** | M1 (une décision par minute close) |
| **Sens** | achat si le prix est au-dessus de l'EMA 60 minutes, vente s'il est en dessous |
| **Entrée** | ordre **limite** à 0,5 R sous le prix (au-dessus en vente) — jamais au marché |
| **Risque (1 R)** | 2 × ATR(14) en M1 |
| **Stop** | 1 R sous l'entrée (au-dessus en vente), **envoyé avec l'ordre**, jamais après |
| **Objectif** | 2 R au-dessus de l'entrée : **ratio 1:2, toujours** |
| **Expiration** | l'ordre non servi est annulé au bout de **60 minutes** |
| **Fin de journée** | tout est fermé avant la clôture (16:00 New York pour le NAS100, 16:55 pour l'EUR/USD) |
| **Positions** | **une seule à la fois** |
| **Filtre** | on ne pose l'ordre que si le modèle donne une probabilité au-dessus du seuil (5 % des occasions) |

**Rien ne passe la nuit.** Pas de position ouverte le soir, pas d'ordre en attente, pas de week-end.

---

## 5. Le filtre, expliqué simplement

À chaque minute, la méthode décrit le marché par **38 chiffres** : l'heure de New York, la
volatilité du moment, la distance au plus haut de la veille, la forme de la dernière bougie, le
volume, les annonces économiques et leur surprise, la position dans la journée…

Un modèle a appris, sur des centaines de milliers de trades passés, **lesquelles de ces situations
finissent par atteindre 2 R**. Il ne prédit pas le marché : il reconnaît les configurations qui, par
le passé, aboutissaient plus souvent.

**Il est réappris tous les trois mois**, sur tout le passé disponible, et jugé sur les trois mois
suivants qu'il n'a jamais vus. 86 réapprentissages sur l'EUR/USD, 47 sur le NAS100.

⚠️ **Une partie du gain vient de la sélection, pas de la prédiction.** Le témoin le prouve : un
modèle entraîné sur des étiquettes tirées au hasard améliore quand même le taux de 40 % à 45 %,
simplement parce que choisir un sous-ensemble du marché change le taux de base. Le vrai apport du
modèle, c'est ce qui dépasse ces 45 % — et c'est 20 points.

---

## 6. L'échelle de risque 6-4-3

Le risque par trade n'est pas fixe. Il suit le capital :

| situation du capital | risque par trade |
|---|---|
| à son **sommet** | **6 %** |
| sous le sommet | **4 %** |
| sous **-20 %** du sommet | **3 %** |
| nouveau sommet touché | retour à **6 %** |

**Pourquoi** : on risque moins quand on va moins bien. C'est l'inverse exact de la martingale, et
c'est ce qui permet de survivre à une série noire. Six pertes à 6 % coûtent 36 % ; six de plus à 4 %
amènent à 60 % ; six de plus à 3 % à 78 %. **Dix-huit pertes d'affilée ne ruinent pas.**

**Mesuré** : si l'avantage de la méthode venait à disparaître complètement, le risque de ruine passe
de **46,6 %** (risque fixe à 6 %) à **5,8 %** (avec l'échelle). L'échelle ne fait pas gagner plus.
Elle fait **survivre**.

---

## 7. Ce que les tests donnent

**Trente-six années cumulées, filtre réentraîné en continu, jamais une information future.**

| | **EUR/USD** | **NAS100** |
|---|---|---|
| Période | 2003 → 2026 (23,4 ans) | 2013 → 2026 (13,7 ans) |
| Minutes analysées | 8 667 035 | 4 078 642 |
| Trades jugés hors échantillon | 154 119 | 81 411 |
| **2 R atteints** | **63,3 %** | **64,2 %** |
| Espérance par trade | +0,825 R | +0,859 R |
| Trades par mois | 27,9 | 41,9 |
| **Années négatives** | **aucune sur 22** | **aucune sur 12** |

**Au compte, avec les vraies tailles de lots et l'échelle 6-4-3** (NAS100, 11,7 ans) :

| sélectivité | 50 $ deviennent | par an | pire recul | série perdante max | mois positifs |
|---|---|---|---|---|---|
| **5 %** | **8 192 311 $** | 179 % | **27,9 %** | 8 | **100 %** |
| 10 % | 12 838 915 $ | 190 % | 31,6 % | 9 | 99 % |
| 20 % | 17 804 840 $ | 199 % | 48,9 % | 14 | 98 % |

---

## 8. Ce que la méthode ne promet pas

Cette page existe pour que personne, y compris nous, ne se raconte d'histoires.

- **Aucun trade réel n'a jamais été passé.** Ni un dollar, ni un ordre. Tout ce qui précède est une
  simulation sur des prix passés.
- **L'hypothèse non vérifiée est le remplissage des ordres limites.** Un simulateur sert toujours ;
  un courtier, pas forcément. C'est le premier chiffre à surveiller en démo.
- **Le spread commande tout.** La méthode gagne à 70 points de spread sur le NAS100 ; elle perd
  au-delà de trois fois ce coût sans le filtre (cinq fois avec).
- **Le lot maximum du courtier plafonne la croissance.** 100 lots sur le NAS100 = 1 730 $ de risque
  par trade au maximum : au-delà d'environ 29 000 $, la croissance devient linéaire, plus
  exponentielle. Sur l'EUR/USD, le plafond arrive vers 10 000 $.
- **Si l'avantage disparaît, on perd de l'argent.** L'échelle ralentit la chute ; elle ne
  l'empêche pas.

---

## 9. Le capital minimum, et pourquoi il ne se discute pas

Le courtier impose une taille de position minimale. En dessous d'un certain capital, **cette taille
minimale devient un risque énorme**, et l'échelle de protection ne peut plus descendre.

| capital | NAS100 | EUR/USD |
|---|---|---|
| 5 $ | **impossible** | seul le palier 6 % existe, la protection ne joue plus |
| 10 $ | **impossible** | possible, échelle grossière (6 % → 3 %) |
| 50 $ | possible, échelle partielle | complète |
| **100 $** | **complète** | complète |

⛔ **Le piège à comprendre** : à très petit capital, si le compte baisse, le lot minimum fait
**monter** le pourcentage risqué au lieu de le baisser. Le plan de protection se retourne contre
lui-même. C'est la seule raison pour laquelle un capital de départ trop faible est dangereux — pas
la méthode, le lot minimum.

---

## 10. Comment ça tourne

1. **Le modèle** est entraîné hors ligne et posé sur le disque, avec l'ordre exact de ses 38
   caractéristiques (`python -m trading.recherche.modele --entrainer`).
2. **L'agent** lit la dernière minute close, calcule les mêmes caractéristiques que le backtest,
   demande sa probabilité au modèle, et pose l'ordre limite si le seuil est franchi
   (`python -m trading.live.scalpeur`). **Il est en observation par défaut** : il faut le demander
   explicitement pour qu'il envoie un ordre.
3. **Le carnet** note chaque trade, le palier de risque appliqué, et l'écart entre le direct et ce
   que le backtest promettait (`python -m trading.recherche.suivi` → `trading/SUIVI.md`).

**Le même code décide du risque dans le backtest et en direct.** C'est la seule façon que la mesure
et le compte disent la même chose.

---

*NEBULA Agency · Cotonou · document interne*

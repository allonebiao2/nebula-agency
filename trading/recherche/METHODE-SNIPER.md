# La méthode « Sniper Entry », apprise règle par règle

*Vidéo « My Secret 1 Minute Scalping Strategy (Sniper Entry) », Mulham Trading (Edge Skool), 26 min 24 s,
envoyée par Mongazi le 2026-09-17. Transcrite en local (faster-whisper) et regardée image par image
(une image toutes les 5 s, pleine résolution sur chaque exemple). Les moments entre crochets renvoient à la
vidéo. Résultats du backtest : `trading/RECHERCHE-SNIPER.md`. Code : `trading/recherche/sniper.py`.*

## L'idée en une phrase

Dans une tendance, le prix va chercher la liquidité au-dessus d'un sommet M15 (ou sous un creux), **échoue à
clôturer au-delà**, et la mèche qu'il laisse devient un **rectangle** : quand une bougie M1 clôture de
l'autre côté du rectangle, on entre avec un stop juste derrière la mèche et un objectif loin.

## Les quatre notions avant les trois étapes

| Notion | Ce que dit l'auteur | Moment |
|---|---|---|
| **Direction** | EMA 200 (il hésite avec la 50, puis entoure la 200). Au-dessus = on cherche des achats, en dessous = des ventes. Le prix ne doit pas zigzaguer autour de la moyenne : il faut une structure valide du bon côté. | [03:07] [04:39] [04:57] |
| **Continuation, pas retournement** | En baisse on travaille les **sommets**, en hausse les **creux**. Un retournement « surétendu » existe mais est hors des règles du jour. | [05:46] [06:16] [17:37] |
| **Force ou faiblesse** | Force = clôture au-delà du niveau (le mouvement continue). Faiblesse = la mèche dépasse et la bougie clôture en deçà (rejet). On trade la faiblesse. | [08:15] [08:28] |
| **Sommets à haute probabilité** | Dans un **imbalance** (FVG) non rempli, ou plus haut/plus bas de **séance** (Asie, Londres, New York). | [08:51] [09:04] |

## Les trois étapes

1. **Marquer un sommet (ou creux) M15** : dans le sens de la tendance, idéalement dans un imbalance, partie
   d'une structure propre (un sommet qui a fait une cassure de structure). [09:44]
2. **Attendre la clôture** : une bougie M15 prend le sommet mais **clôture en dessous** : c'est le rejet par
   la mèche. ⚠️ **Cette bougie doit être de la couleur opposée au trade** : haussière pour une vente,
   baissière pour un achat. Clôturée baissière, « une partie du mouvement est déjà faite » : pas de trade.
   [10:18] [21:53] [22:15] [25:27]
3. **Tracer le rectangle et regarder la M15 suivante** : de la **clôture** de la bougie à son **extrême**
   (le haut de la mèche pour une vente), prolongé à droite. Puis on passe en **M1** : « la minute décide
   tout, tu as l'entrée ou tu ne l'as pas ». [10:41] [11:16] [14:39]

## L'entrée, le stop, l'objectif

- **Entrée** : une bougie M1 **clôture sous le rectangle** (au-dessus pour un achat). Il préfère qu'elle
  casse aussi le dernier creux M1. Variante « risquée » : entrer dans le rectangle sur un niveau clé.
  [15:06] [15:19] [18:47]
- **Toujours valide** tant qu'aucune clôture ne « déplace » au-delà du sommet, même si une mèche le reprend
  pendant l'attente. [20:33]
- **Stop** : « légèrement au-dessus du sommet, à cause du spread ». [15:56] [23:20]
- **Objectif** : 3:1 au minimum, 5:1, 10:1, ou le prochain niveau clé M15, voire l'EMA 200. Après l'entrée,
  il ne regarde plus que le M15 pour ignorer le bruit. [01:18] [16:06] [16:39] [23:31]
- **Heures** : début d'Asie, Londres, New York, et jusqu'à une heure ou deux après l'ouverture de New York ;
  pas après, ni à l'ouverture d'une bougie journalière quand le spread est large. [12:36] [13:12] [20:10]

## Ce que l'image a appris (le son ne le disait pas)

- **EUR/USD M15 chez Tickmill, en heure de New York.** Ses boîtes de séance : Asie 20:00-00:00, Londres
  02:00-05:00, New York 07:00-10:00 (heure de New York).
- **Les quatre exemples, retrouvés au dixième de pip dans les bougies Deriv** :

| Exemple | Bougie M15 (UTC) | Heure New York | Rectangle (Deriv) | Entrée M1 simulée (New York) | Stop simulé chez Deriv | Ce qu'il dit du résultat |
|---|---|---|---|---|---|---|
| 1, Asie | 31/10/2025 01:15 | 21:15 | 1,15766 → 1,15775 | 21:31 (identique à l'écran) | 2,3 pips (1,6 à l'écran, R:R 34,9) | « 5 pour 1 en 30 minutes », puis 10 pour 1 |
| 2, Londres | 31/10/2025 06:15 | 02:15 | 1,15712 → 1,15734 | 02:39 | 2,8 pips | « même celui-ci fait 3 pour 1 » |
| 3, New York + 1 h 45 | 31/10/2025 15:45 | 11:45 | 1,15409 → 1,15430 | 12:05 (clôture de 12:04 à l'écran) | 3,2 pips | « 3 pour 1 puis 5 pour 1 » |
| 4, Londres, imbalance | 04/11/2025 07:30 | 02:30 | 1,15309 → 1,15336 | non détecté (voir la fin) | | « 3 pour 1 puis 6 pour 1 » |

- Le sommet balayé peut être un **sommet de trois bougies formé juste avant** (exemple 1), ou des **sommets
  égaux** (exemple 4).
- La tendance qu'il lit est la **structure majeure** (la grosse cassure de la veille), pas la petite
  structure du repli : c'est pendant le repli que le balayage se produit.
- La vidéo vend un abonnement (Edge Skool) et un modèle « swing » différent ; elle ne publie **aucune
  statistique** et **ne parle jamais des annonces économiques**. Un post de sa communauté affiché à l'écran
  parle de « 0,5 % de risque par trade ».

## La checklist d'un trade (vente ; l'achat est le miroir)

1. Prix M15 **sous l'EMA 200**, et depuis au moins 2 h.
2. Dernière cassure de **structure majeure** baissière.
3. Un **sommet M15** non encore pris, de moins de 24 h (idéalement dans un imbalance).
4. Une bougie M15 **haussière** dépasse ce sommet et **clôture en dessous**.
5. Heure de clôture dans une séance : Asie (20:15-00:00 NY), Londres (02:15-05:00 NY), New York (07:15-12:00 NY).
6. Rectangle = clôture → plus haut de cette bougie.
7. Dans l'heure qui suit (4 bougies M15), une bougie **M1 clôture sous le rectangle** → vendre à l'ouverture suivante.
8. Aucune clôture M15 au-dessus du sommet avant l'entrée, sinon on abandonne.
9. Stop au-dessus du plus haut atteint depuis la bougie de balayage + le spread ; **au moins 2 pips chez Deriv**.
10. Objectif 3 R. Sortie avant 16:55 New York. Pas d'entrée 30 min avant / 15 min après une annonce forte (règle NEBULA).

## Les traductions mécaniques (ce qui a dû être décidé à la place de l'œil de l'auteur)

| Geste de l'auteur | Traduction dans le code | Pourquoi |
|---|---|---|
| « Structure valide » | Dernière cassure sur pivots M15 de 12 bougies de chaque côté (≈ 3 h) + 8 clôtures M15 du bon côté de l'EMA | Avec 5 bougies, aucun de ses exemples ne passait ; à 12, les exemples 1, 2 et 3 passent. **Choisi sur ses exemples, avant tout résultat.** |
| « Un sommet » | Pivot M15 de 3 bougies (« >= » à droite), jamais dépassé, moins de 24 h | Exemples 1 et 4 |
| Plusieurs sommets dépassés d'un coup | Le plus haut d'entre eux sert de niveau | Clôturer sous le plus haut = rejet de la zone |
| « Légèrement au-dessus » | Extrême depuis le balayage + 1,5 spread de la minute | Son stop de l'exemple 1 : 0,5 pip au-dessus |
| Combien de temps attendre la M1 | 4 bougies M15 (variante : 1) | Il attend plusieurs bougies dans l'exemple 3 |
| « N'importe quel niveau clé » | Objectif fixe 3 R ; variantes 2 R, 5 R, niveau M15 opposé au-delà de 3 R | Un « niveau clé » choisi à l'œil ne se teste pas |
| Sorties partielles, ajouts | Non modélisés : une position par instrument, sortie unique | Règle maison |

## Pourquoi l'exemple 4 échappe au code

Chez Deriv, la bougie de 07:30 UTC clôture à **1,15309**, soit 0,3 pip **au-dessus** des sommets égaux
qu'elle balaie (1,15306). Chez Tickmill elle clôturait à 1,15311, et on ne lit pas ses sommets à l'image.
La règle « clôture sous le sommet » est gardée telle quelle : l'assouplir pour un exemple, c'est
optimiser sur la vidéo.

# Recherche d'une stratégie de scalping : le plafond, le piège, et un candidat

*2026-09-17, nuit · NEBULA Trader*

## La demande

Mongazi : « il faut que tu recherches une stratégie qui puisse atteindre ces objectifs, tu dois
pouvoir trouver, tant qu'on ne trouve pas tu ne peux pas t'arrêter », puis, en cours de route :
« je veux plus de scalping, des trades ouvrables et fermables dans la même journée, à la limite de
l'intrascalping ».

Les objectifs, rappelés : **plus de 50 % (idéal 60-70 %) des trades atteignent 2 R**, R:R d'au moins
1:2, et un **risque extrêmement bas de 5-6 pertes d'affilée**.

Deux décisions prises par lui au début : **les deux paliers** (viser 70, signaler tout ce qui passe
50) et **EUR/USD et NAS100 seuls** comme marchés tradés.

## Ce qui a été construit avant de chercher

Un protocole écrit **avant le premier résultat** (`trading/RECHERCHE-SANS-FIN.md`) : deux paliers
chiffrés, un registre unique corrigé par Holm, et surtout **des données scellées** — des années que
la recherche ne peut pas regarder pendant qu'elle cherche.

- `dukascopy.py` : l'historique M1 que Deriv n'a pas. **EUR/USD depuis 2003-05-04**, **NAS100 depuis
  2013-01**, bid ET ask (le spread d'époque est mesuré, pas supposé). Alignement avec Deriv vérifié
  sur un mois commun : **corrélation 0,985 au décalage nul**, 0,02 à ±1 minute, écart de prix médian
  1 point. Les deux flux sont sur la même horloge.
- `scelle.py` : **EUR/USD 2003-2011** et **NAS100 2020-2023** scellés, une ouverture par candidate,
  inscrite au journal avec sa date et sa raison.
- `intraday.py` : la règle de Mongazi écrite une fois — tout se ferme le jour même, en heure de New
  York, avant le rollover de 17:00 (EUR/USD) et la clôture cash de 16:00 (NAS100).
- Le banc paie désormais le spread **minute par minute** (le rollover coûte 30 fois midi), mesure le
  **taux de 2 R atteints**, le **point mort réel** et les **séries perdantes**.

## Le résultat qui cadre tout : le plafond

Avant de chercher une règle, on mesure ce qu'atteindrait **un devin parfait** : sur chaque minute,
on étiquette les deux sens, et « au moins un des deux atteint 2 R » borne tout le reste.

| | EUR/USD M1 | NAS100 M1 |
|---|---|---|
| meilleur plafond | **57,7 %** (stop 20 points) | **63,8 %** (stop 1 200 points) |
| point mort au même stop | 37,1 % | 34,1 % |

**Donc le palier 70 est hors de portée en intraday, par construction**, et le palier 50 exige de
choisir le bon sens **trois fois sur quatre**. Ce n'est pas un avis : c'est une mesure, et elle
vaut pour toute règle, tout modèle, toute intuition.

## Ce qui a été essayé, et qui n'a rien donné

- **Sept familles de scalping** (ouverture de séance, balayage de niveau, compression, excès,
  suite de bougies, créneau volatil, entrée au rabais) en M1, M5, M15, sur les deux marchés.
- **Un modèle** (`meta.py`) : 41 caractéristiques causales — dont le volume, les annonces et la
  **surprise économique** (réel contre prévu) — un modèle par sens, walk-forward **purgé**. Il gagne
  1 à 5 points sur le taux de base, **jamais le point mort**. Tous les seuils sont négatifs.
- **55 000 paires et 6 500 triplets** de conditions minés en bitsets (`regles.py`). Meilleure règle
  validée hors apprentissage : 37,6 % de 2 R sur 744 trades, contre 34 % de point mort.

## Le piège qui a failli produire un faux résultat

Une entrée limite « au rabais » sortait **+0,101 R par trade sur EUR/USD M1, 29 000 trades**. C'était
un artefact : nos bougies sont des prix vendeur, un achat s'exécute au prix acheteur, donc l'ordre
n'est servi que si le prix **traverse** la limite d'un spread. En l'exigeant, l'EUR/USD tombe à
+0,017 R, puis **-0,019 R** en hypothèse prudente.

Deuxième piège, mesuré le même soir : un plafond « au moins un des deux sens gagne » appliqué à deux
ordres limites **miroirs** affiche 99 %. C'est une tautologie de sélection, pas un avantage.

## Le candidat

Seul survivant de 389 tests : **NAS100 M1, entrée limite au rabais** — dans le sens de l'EMA 60
minutes, ordre limite à 0,5 R sous le prix, stop 2 × ATR(14), objectif 2 R, ordre annulé après 60
minutes, position fermée le soir.

**Le scellé a été ouvert pour lui, une fois** (NAS100 2020-2023, Dukascopy, jamais regardé) :

| | valeur | critère de Mongazi |
|---|---|---|
| 2 R réellement atteints | **40,3 %** (point mort 34,7 %) | plus de 50 % ⛔ |
| R:R réalisé | **1,79** | au moins 1:2 ✅ |
| P(5 pertes d'affilée / 100) | **96,7 %** (P(6) 84,6 %, plus longue 15) | « extrêmement bas » ⛔ |

29 362 trades, **+0,165 R par trade**, PF 1,26, positif **chaque année** et **dans les deux sens**.

Il survit à : le remplissage réaliste puis prudent · **deux fournisseurs de données indépendants**
sur la même période (Deriv +0,169 R, Dukascopy +0,175 R) · un coût **trois fois** supérieur à celui
de Deriv.

⚠️ **Sa fragilité tient en un nombre : le spread.** Deriv cote 70 points dans 99,8 % des minutes,
ouverture et annonces comprises ; au spread d'époque de Dukascopy (167 points) la stratégie perd.
Et sur 2013-2019, elle perd au coût absolu d'aujourd'hui (70 points sur un indice à 5 000) mais
gagne au coût relatif : le mécanisme est ancien, sa rentabilité tient au spread.

⛔ **Les chiffres d'argent d'un backtest à 28 trades par jour ne veulent rien dire** : composés, ils
donnent des multiples absurdes. Ce qui se mesure, c'est l'espérance par trade ; ce qui décide, c'est
la démo en observation.

## Ce qui attend Mongazi

1. Ce profil — **40 % de réussite, gain moyen presque deux fois la perte moyenne** — l'intéresse-t-il ?
   C'est exactement le profil qu'il appelait « nul », et c'est le seul qui existe en intraday.
2. Si oui : **démo en observation** sur `6305888`, puis l'ingénierie d'un agent à ordres limites en
   M1 (l'agent actuel travaille en H4, au marché).
3. Si non : l'intraday est clos par la mesure du plafond ; il faudra changer d'horizon ou de marché,
   et c'est sa décision.

**Le scellé EUR/USD n'a pas été ouvert** : aucune candidate ne le méritait. Il reste intact.

# DOCTRINE — ce que le bot doit respecter, et pourquoi

Ce document est la traduction, en mécanismes exécutables, des principes de
trading que Mongazi a posés le 2026-09-16. Chaque principe y est : (a) évalué,
(b) corrigé quand il est imprécis, (c) rattaché à l'endroit du code qui
l'impose.

**La règle de la maison : un principe qui n'est pas imposé par du code n'est pas
un principe, c'est une intention.** Un humain fatigué contourne une intention.

---

## 1. La gestion du risque

### Ce qui est juste, et retenu tel quel

| Principe | Où c'est imposé |
|---|---|
| Risque max 1 à 2 % par trade | `config.toml` + plafond **écrit dans le code** (`PLAFOND_RISQUE_PAR_TRADE`) que le fichier ne peut pas desserrer |
| Ratio rendement/risque min. 1:2 | `take_profit_r_multiple`, validé avant chaque ordre |
| Taille calculée **avant** l'entrée, dérivée du stop | `risque.dimensionner()` — jamais un lot en dur |
| Exposition totale simultanée max 5-6 % | `exposition_totale_max_pct` |
| Survivre d'abord, performer ensuite | tout le module `coupe_circuits` |

### Correction n°1 — les coûts sont absents, et c'est l'omission la plus chère

Le document affirme : « avec un ratio de 1:2, tu peux avoir raison seulement
40 % du temps et être profitable ». C'est arithmétiquement exact **hors coûts** :

- seuil d'équilibre à 1:2 → `1 / (1 + 2)` = **33,3 %**
- à 40 % de réussite → espérance `0,40 × 2R − 0,60 × 1R` = **+0,20 R** par trade

Mais on paie le courtier à chaque aller-retour, et ce coût est **fixe en pips**
alors que R dépend de l'unité de temps. Le même système devient une autre
affaire selon l'échelle :

| Unité | ATR(14) approx. | Stop 2×ATR = 1R | Spread | Coût en R | Espérance nette |
|---|---|---|---|---|---|
| H4 | ~35 pips | ~70 pips | ~1,5 pip | 0,02 R | **+0,18 R** |
| H1 | ~12 pips | ~24 pips | ~1,5 pip | 0,06 R | **+0,14 R** |
| M5 | ~4 pips | ~8 pips | ~1,5 pip | 0,19 R | **+0,01 R** |

Même stratégie, même taux de réussite, même ratio. **Rentable en H4, morte en
M5.** Le spread n'a pas bougé : c'est R qui a rétréci.

→ **Conséquence** : le bot travaille en **H4**, et le backtest facture le spread
réel, la commission et le slippage sur chaque trade. Un backtest sans coûts est
une publicité, pas une mesure.

*(Les ATR ci-dessus sont des ordres de grandeur usuels sur EUR/USD. Le bot
mesurera les vrais sur l'historique Deriv et ce tableau sera recalculé avec les
chiffres réels — voir `outils/couts_reels.py`.)*

### Correction n°2 — l'exposition « 5-6 % » cache un piège en forex

La règle est juste pour un portefeuille diversifié. Mais en change, **la
diversification est souvent fausse** : EUR/USD, GBP/USD et AUD/USD sont
corrélés de 0,7 à 0,9. Trois positions à 2 % sur ces trois paires ne font pas
6 % réparti, elles font presque **6 % sur un seul pari** (le dollar).

→ Sans objet tant qu'on tient une seule paire, mais la règle est encodée dès
maintenant : l'exposition se compte **par facteur de risque**, pas par symbole.

---

## 2. L'analyse avant d'entrer

Retenu intégralement, et traduit en filtres mesurables :

| Principe | Traduction machine |
|---|---|
| Trader dans le sens de la tendance | filtre **D1** obligatoire ; un signal H4 contre la tendance D1 est refusé sauf score de retournement explicite |
| Niveaux clés (supports/résistances) | détection des zones de réaction ; distance à la zone = variable du modèle |
| Multi-timeframe (W/D pour la tendance, 4H/1H pour le timing) | `timeframe` + `timeframe_filtre` |
| Catalyseurs économiques (NFP, CPI, Fed, BCE) | `blackout_news_actif` : aucune entrée ±30/15 min autour d'une annonce à fort impact |

### Précision — « les slippages peuvent sauter ton stop »

C'est exact, et mérite d'être dit dans sa forme complète, parce que c'est la
chose que les débutants comprennent le plus tard :

> **Un stop-loss est une instruction, pas une garantie.** Sur un gap (ouverture
> du dimanche, annonce surprise, intervention de banque centrale), il n'existe
> aucun prix à ton niveau : l'ordre s'exécute au premier prix disponible, qui
> peut être très loin. C'est la raison — la seule — pour laquelle le
> dimensionnement ne suffit pas et pour laquelle on ferme avant le week-end.

→ `fermer_avant_weekend`, `eviter_ouverture_dimanche`, `blackout_news_actif`.

---

## 3. Le plan de trade écrit AVANT l'entrée

> « Une position sans plan écrit, c'est un pari, pas un trade. »

C'est le principe le plus facile à trahir pour un humain, et le plus facile à
imposer pour une machine. Il devient un **objet obligatoire** : `PlanDeTrade`
(`noyau/plan.py`). Une stratégie ne renvoie pas un signal « acheter » — elle
renvoie un plan complet, ou rien.

Un plan sans entrée, sans stop technique, sans objectif, sans thèse en une
phrase, **n'est pas transmissible à l'exécution** : l'objet refuse de se
construire.

---

## 4. Le journal

> « En 6 mois, ton journal te dira plus que n'importe quel livre. »

Vrai, et pour un bot c'est plus fort encore : **le journal est le jeu de données
d'entraînement.** Sans lui, l'auto-amélioration est un mot creux.

Chaque trade enregistre son contexte au moment de la décision — pas après :
régime, volatilité, spread **réellement payé**, session, distance aux niveaux,
score du modèle, slippage constaté, et le résultat. Les **signaux refusés** sont
enregistrés aussi : savoir ce que le bot a laissé passer et ce que ça aurait
donné est la moitié de l'information.

L'« émotion ressentie » du journal humain devient **l'état du système** (voir §5).

---

## 5. La psychologie

### Ce dont le bot est immunisé par construction

C'est son avantage le plus sous-estimé sur un humain. Ces quatre erreurs
deviennent littéralement **impossibles à commettre** :

| Erreur humaine | Pourquoi elle ne peut pas arriver |
|---|---|
| Revenge trading | délai de refroidissement imposé après une perte ; nombre de trades plafonné par jour |
| Sur-trader | le signal se déclenche ou ne se déclenche pas ; il n'y a pas d'ennui à combler |
| Trader fatigué ou stressé | sans objet |
| Refuser d'avoir tort | le stop est déposé chez le courtier avant que la position existe |

### Correction n°3 — « ne jamais déplacer un stop-loss » est faux tel quel

La formule exacte est : **jamais l'élargir.** Le resserrer dans le sens du
profit n'est pas seulement permis, c'est le mécanisme même du trailing.
Appliquée littéralement, la règle du document interdirait le suiveur et
laisserait filer tous les gains.

→ **Invariant imposé en code** : un stop ne se déplace que dans la direction du
profit. Toute tentative d'élargissement est refusée et journalisée comme une
anomalie, même si elle vient d'un module du bot lui-même.

### Correction n°4 — « quelle est mon émotion ? » n'a pas de sens pour un bot, mais se traduit

L'équivalent machine de la peur et de la cupidité, c'est **la dérive d'état**.
Le bot se pose donc la question, avec des chiffres :

- série de pertes en cours
- spread hors de sa plage habituelle
- volatilité hors de sa plage d'entraînement
- score de confiance du modèle en baisse
- régime de marché différent de celui où la stratégie gagne

→ `noyau/sante.py`. Si l'état dérive, le bot réduit la taille ou s'abstient.
C'est exactement ce qu'un bon trader fait en se sentant mal : il passe son tour.

### Ce que le document ne voit pas : le risque se DÉPLACE sur l'opérateur

C'est l'angle mort, et il n'existe que pour les systèmes automatisés. Les cinq
gestes qui tuent un bot **rentable** :

1. **Couper le bot pendant une série de pertes** — exactement au moment où il ne
   faut pas. Les séries noires sont la façon dont un système gagnant respire.
2. **Monter le risque après un drawdown** pour « rattraper ».
3. **Désactiver un disjoncteur** qui vient de se déclencher.
4. **Ré-optimiser les paramètres après chaque perte** — c'est du sur-apprentissage
   en temps réel, opéré à la main.
5. **Reprendre une position du bot en manuel.**

→ Contre-mesures : le `magic_number` isole les ordres du bot ; toute
modification de `config.toml` est **horodatée et journalisée** ; et le bot
**alerte** si le risque est relevé alors que le compte est en drawdown.

---

## 6. Les six questions avant chaque position → six verrous

Les six questions du document deviennent six contrôles exécutés avant tout
ordre. **Aucune réponse manquante n'est tolérée : pas de réponse, pas d'ordre.**

| # | Question humaine | Verrou machine |
|---|---|---|
| 1 | Quelle est ma thèse ? | `PlanDeTrade.these` non vide, ≤ 200 caractères, journalisée |
| 2 | Où est mon invalidation technique ? | stop dérivé d'un niveau + ATR, jamais d'un montant rond |
| 3 | Combien je risque, en devise et en % ? | calculé et **plafonné** avant l'ordre |
| 4 | Quel est mon ratio R:R ? | ≥ `ratio_rr_minimum`, sinon refus |
| 5 | Une annonce est-elle imminente ? | fenêtre de blackout consultée |
| 6 | Quelle est mon émotion ? | santé du système (§5) dans sa plage |

---

## 7. Ce que le document ne dit pas, et qui compte autant

### La taille d'échantillon

Juger un système sur 10 trades est **l'erreur fatale la plus courante**. Un
système à 40 % de réussite produit 6 pertes d'affilée environ une fois tous les
60 trades : c'est du bruit, pas un signal de panne. Il faut de l'ordre de **100
trades** pour qu'un taux de réussite mesuré veuille dire quelque chose, et c'est
précisément pourquoi `echantillon_min_trades` a un plancher dans le code.

### Le stop temporel

Un trade qui n'a rien fait après N barres immobilise du capital et du risque
sans rien produire. Il se ferme. Absent du document, présent dans le moteur
(`stop_temporel_barres`).

### Le sur-apprentissage

Pour un bot, c'est **le** sujet. Toute la discipline d'exécution du monde ne
sauve pas un système validé sur les données qui ont servi à le construire.
D'où : walk-forward obligatoire, champion/challenger, et marge d'amélioration
exigée avant toute promotion.

### Le risque de ruine

Ce n'est pas la même chose que le drawdown. Avec 1 % par trade, 40 % de
réussite et 1:2, le risque de ruine est négligeable. À 5 %, il devient réel. Le
plafond dans le code est là pour ça, et pas pour être prudent par principe.

---

*Établi le 2026-09-16. Toute modification de cette doctrine doit se traduire par
un changement de code ou de configuration le même jour, sinon elle n'existe pas.*

# Le cerveau de NEBULA Trader, et son départ du dépôt public

*2026-09-23 · session terminal, PC de Cotonou*

## Ce que Mongazi a demandé

« Concernant l'agent de trading intelligent, je veux que tu crées un cerveau à
part entière pour lui, hors NEBULA si c'est la meilleure décision. Le but, c'est
qu'il ne se mélange pas, qu'il puisse s'auto-améliorer et comprendre ce qu'il
fait, et toujours être en constante amélioration, avec une vue sur l'ensemble de
ce qu'il fait. Pose-moi 10 questions autour de ça. »

Puis, en cours de travail : « Assure-toi qu'il n'y ait aucune erreur, et fais en
sorte que ça puisse s'adapter parfaitement et entièrement à la méthode que
j'enverrai une fois le travail terminé » et « sans tricher et faire d'erreur, il
faut toujours s'en assurer avant de donner les résultats à chaque fois ».

## Les dix réponses

Elles sont recopiées mot pour mot dans **`nebula-trader/_cerveau/DECISIONS.md`**,
avec ce qui en a été fait. En résumé : dépôt séparé et privé · markdown plus
index · le cerveau va jusqu'à la démo tout seul, jamais au réel · scellé du
dernier an et plafond de regards · le critère de Mongazi maintenu · les méthodes
viennent de lui désormais · tour de nuit sur le PC · le cerveau reste chez
NEBULA · **EUR/USD seul**, le NAS100 sort.

⏳ **La question 6 n'a pas reçu de réponse** (la date et le chiffre d'arrêt du
projet) : c'est la décision D-003.

## Le déménagement

`trading/` a quitté `allonebiao2/nebula-agency`, qui est **public**, pour
**`allonebiao2/nebula-trader`**, **privé**, sur `C:\Users\USER\nebula-trader`.

Les 31 commits qui touchaient `trading/` ont été **rejoués un par un**, avec
leurs auteurs et leurs dates d'origine, chacun renvoyant à son commit source.
⚠️ `git subtree split` a été essayé d'abord : il laboure les 1 080 commits du
dépôt et n'avait pas fini au bout de cinq minutes. Le rejeu des 31 commits
concernés prend quelques secondes et garde le préfixe `trading/` intact, ce que
`subtree split` aurait de toute façon supprimé.

Ont suivi : `secrets/mt5.env`, `secrets/deriv.env`,
`secrets/nebula-trader-licence.pem` (la clé privée qui signe les licences), et
les 461 Mo de prix, de rapports et de modèles, tous hors git.

## Ce qu'est le cerveau

Six pièces, et chacune se définit par ce qu'elle **refuse** :

| Pièce | Refuse |
|---|---|
| `verdict.py` | de juger des trades non causaux, sous 100 trades, sur une période brûlée, ou avec une mesure réclamée après coup |
| `regards.py` | de laisser regarder la dernière année, de laisser chercher au-delà de 20 essais |
| `registre.py` | un chiffre non déclaré à l'ouverture, une hypothèse invérifiable, la réécriture d'un essai fermé |
| `banc.py` | une méthode qui regarde l'avenir, même d'une barre |
| `cimetiere.py` | de retester une idée enterrée sans dire ce qui a changé |
| `methode.py` | de formaliser une fiche incomplète, d'ouvrir une démo sans verdict |

Plus 11 leçons, chacune rattachée au code qui l'impose, un tour de nuit et une
vue d'ensemble régénérée à chaque tour.

Le registre démarre avec les **428 essais** de `rapports/recherche/registre.json`,
tous marqués non causaux. Le cimetière démarre avec **15 méthodes mortes**,
tirées des 16 documents de recherche.

## Ce que la construction a trouvé, et qui ne se voyait pas

**Les trois critères de Mongazi ne sont pas compatibles entre eux.** Il demande
plus de 50 % d'objectifs atteints, un rapport d'au moins 1:2, et un risque très
bas de 5 ou 6 pertes d'affilée. Les deux premiers sont des réglages ; le
troisième est une **conséquence arithmétique** du premier :

| objectifs atteints | P(5 pertes d'affilée sur 100) | P(6) |
|---|---|---|
| 50 % | 81 % | 55 % |
| 60 % | 46 % | 21 % |
| 67 % | 24 % | 8 % |

Une méthode à tout juste 50 % verra cinq pertes d'affilée quatre fois sur cinq.
Exiger des séries rares revient donc à exiger **66,2 %**, c'est-à-dire le haut de
la fourchette « idéale » que Mongazi a lui-même donnée, pas son plancher. Le
chiffre est **calculé** par `verdict.taux_minimal_pour_les_series()`, jamais
écrit en dur. Décision D-002 en attente.

## Trois défauts de ma propre garde, trouvés en la mesurant

La garde de causalité recalcule les signaux sur des séries tronquées et compare.
Elle a échoué **deux fois** avant de marcher, et c'est la partie la plus utile de
la journée.

1. **Une marge de 36 barres « pour le stop temporel »** : une triche d'une seule
   barre ne se voit qu'à la dernière barre de la troncature, précisément celle
   que la marge écartait. Un signal causal à la barre i ne dépend que des barres
   jusqu'à i : il n'y a rien à excuser.
2. **Des coupures ancrées sur les barres qui PORTENT un signal** : ça semblait
   malin et ça regardait partout sauf là où il y avait quelque chose à voir. Une
   triche qui **retire** des signaux (on ne garde que ceux dont la barre suivante
   donne raison, le cas le plus courant) laisse justement une barre **vide** là
   où elle a frappé.
3. **La version qui marche** balaie toutes les barres d'une fenêtre dense, une
   coupure par barre. Trois tricheurs sur trois sont attrapés : retrait d'une
   barre, ajout d'une barre, meta-labeling sur vingt barres.

⚠️ **Leçon de méthode** : les deux premières versions affichaient « garde
vérifiée » avec un joli nombre de barres comparées. Sans un témoin rouge écrit
exprès, elles seraient passées pour bonnes.

## Un défaut trouvé par le tour de nuit lui-même

Au premier essai réel, le tour a trébuché : les 428 essais importés portent la
clé `id` avec la valeur `None`, et `e.get("id", "")` rend `None`, pas `""`. Une
clé présente et vide n'est pas une clé absente. Le tour l'a **inscrit dans son
compte rendu** au lieu de mourir en silence, ce qui est exactement ce pour quoi
il est écrit ainsi.

## Vérifié, pas supposé

- **62 contrôles verts** pour le cerveau, chaque garde avec son témoin rouge.
- **219 contrôles verts** pour l'agent depuis le nouvel emplacement.
- **Un tour de nuit réel** de bout en bout : méthode reçue, code écrit, fiche
  formalisée, 24 876 trades simulés sur EUR/USD M5 de 2012 à 2025 avec les coûts
  Deriv réels, témoin au hasard, verdict **REJET** (18,1 % d'objectifs atteints,
  R:R 1:1,40, et elle ne bat même pas le témoin).

## Deux pièges de la machine, revus aujourd'hui

- ⚠️ **Les heredocs Bash mangent les accents sur ce PC.** `cat > f.py <<'EOF'`
  avec des caractères accentués casse le script ou produit des `?`. Écrire les
  fichiers par un script Python en UTF-8.
- ⚠️ **La console Windows est en cp1252** : tout script qui affiche des accents
  commence par `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`.

## Ce qui reste

- Les **trois décisions** D-002, D-003, D-004 (`_cerveau/DECISIONS.md`).
- **La méthode que Mongazi va envoyer.** Le chemin est prêt :
  `python -m cerveau methode --recevoir "nom" --source "..."` crée la fiche
  **et** le module de code avec sa signature déjà écrite.
- Créer le dépôt privé sur GitHub et pousser (pas de `gh` sur ce PC).

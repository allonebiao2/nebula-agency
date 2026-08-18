# HILLARY M. STYL — les pièces envoyées en double basculent toutes seules

**Date :** 2026-08-18
**Demandé par Mongazi :**
> « Je vais t'envoyer les modèles restants. Je t'enverrai certains en double
> pour un seul, et d'autres seuls. Ceux en double, assure-toi qu'il switch
> automatiquement quand on regarde. »
> puis : « Maintenant dans la hero tu n'y mets en plus que les nouvelles,
> dans le style de ceux déjà présents, histoire que ça reste cohérent. »

**Branche :** `claude/hillary-style-auto-switch-9ij9wz`
**Site :** https://hillary-m-styl.pages.dev — ⚠️ **rien n'est encore déployé.**

---

## Ce qui a été fait

### 1. La bascule face / dos, là où on regarde une pièce

Une pièce qui a deux photos les montre **l'une après l'autre, toute seule**,
au catalogue et au carrousel. Trois règles la gouvernent :

- **hors de l'écran, rien ne tourne.** Un `IntersectionObserver` ouvre et
  ferme le robinet ; le battement s'arrête dès que plus aucune carte n'est vue.
- **onglet en arrière-plan ou fiche de commande ouverte : tout se fige**, ET
  l'échéance est repoussée. Sans ce report, toutes les cartes rattrapent leur
  retard d'un coup au retour et basculent ensemble.
- **le va-et-vient est décalé d'une carte à l'autre.** Synchrones, les cartes
  clignoteraient ensemble comme une panne.

La **première** bascule vient vite (1,6 s) : c'est elle qui apprend à la
cliente que la pièce a un dos. Les suivantes prennent leur temps (3,6 s).

⛔ **On ne bascule jamais vers une image pas encore arrivée.** La seconde vue
est en `loading="lazy"` : sur une 4G de Cotonou elle peut n'être là qu'après
l'heure de la première bascule. On révélerait alors **du vide pendant 3,6 s**,
et la carte semblerait cassée. Tant qu'elle n'est pas peinte, on attend.

`prefers-reduced-motion` : rien ne tourne, les pastilles disparaissent, et le
dos reste joignable dans la fiche de commande (figure « Le dos », inchangée).

**Le héros n'a PAS été touché** : son glissement (la pièce et le chiffre géant,
même durée, même courbe) a été réglé au millième le 2026-08-06. Une seconde vue
qui s'y fondrait entrerait en concurrence avec lui.

### 2. Les pastilles

Deux points en bas à droite de la photo. L'actif est **plus large**, pas
seulement rose : un état qui ne tient qu'à la couleur ne se lit pas pour tout
le monde. Contrastes mesurés : rose `#E6007E` 4,5:1 et gris `rgba(26,26,26,.45)`
3,4:1 sur le papier de la carte, les deux au-dessus des 3:1 exigés.

### 3. ⛔ Trois bugs qui auraient fait perdre les photos

Ils dormaient dans `_nouveaux_modeles.py` et se seraient déclenchés **le jour
où les photos arrivent** :

1. **`injecter()` sautait les onze fiches.** Elles sont entrées au catalogue le
   2026-08-18 sans photo (`photoWa:true`). Le script voyait `id:"h10"` déjà
   présent, écrivait « déjà au catalogue » et passait. Les photos auraient été
   détourées, posées dans `assets/images/`… et **jamais raccrochées à une
   fiche**. Le site n'aurait pas bougé d'un pixel, et rien ne l'aurait signalé.
   → `fiche_existante()` accroche `img` / `img2` et retire `photoWa:true`.
2. **`motion.js` n'était jamais réécrit.** Le carrousel et le héros étaient
   calculés ligne par ligne, puis **jetés** à la sortie de la fonction. Une
   pièce serait entrée au catalogue et nulle part ailleurs.
3. **Les chaînes JS étaient bâties en `'%s'`.** La première apostrophe dans un
   nom ou une description cassait tout le fichier, donc tout le site. Aucune
   pièce d'aujourd'hui n'en porte — ce n'est pas une raison.

Au passage : la légende du carrousel se coupait **au milieu d'un mot**
(« jupe longu »), affiché en grand sous la pièce. Elle coupe maintenant sur un
mot.

### 4. La règle du « tout ou rien » a été inversée, et c'est voulu

Avant, le script refusait de poser tant qu'une seule photo manquait : « un
catalogue à moitié rempli est pire qu'un catalogue qui attend ». C'était juste
quand les onze pièces n'étaient nulle part. **Elles sont maintenant en ligne**,
avec « Photo sur WhatsApp ». Le calcul s'est inversé : chaque photo posée est un
gain net, et celles qui manquent gardent une mention honnête et actionnable.
Attendre la dernière, c'est laisser dix pièces sans image pour une onzième.

### 5. Le héros prend les nouvelles, dans le style des anciennes

Il n'y a plus de liste de trois élues (`HEROS = ["lacee","coeurs","soleil"]`).
**Toute pièce qui a sa photo entre au héros**, écrite exactement comme ses
voisines : `f` `c` `col` `mat` entre apostrophes, `t` et `d` entre guillemets,
`mat:'Fait main · 2 semaines'` quand la pièce est faite main, comme l'ensemble
JOSY qui est là depuis le premier jour.

⚠️ **La règle des nappes, née le 2026-08-17**, est maintenant appliquée par le
code au lieu d'être un choix à la main. Le héros peint le fond avec la teinte
de la pièce : deux teintes voisines à la suite, c'est **une transition qui
n'existe pas**. C'est pour ça que la robe à tulle avait été écartée. On garde
la règle — mais **on ne perd plus la pièce : au lieu de l'exclure, on la
déplace.** `poser_heros()` choisit l'ordre des ajouts, et **la boucle compte**
(la dernière diapositive précède la première).

⛔ **On ne touche à AUCUNE entrée déjà présente**, comme demandé.

### 6. À SIGNALER À MONGAZI

Le contrôle des nappes trouve **2 voisinages de même teinte parmi les 7
diapositives déjà en place**, antérieurs à la règle :

| voisinage | écart |
|---|---|
| `hero-3` bleu `#275eb7` → `hero-4` cyan `#0e85b7` | **19°** |
| `piece-violette` `#6b3065` → `piece-orange` `#925437` | **23°** |

Deux transitions du héros sont donc presque invisibles aujourd'hui. **Rien n'a
été changé** : il a dit de n'ajouter que les nouvelles. Un simple échange de
place réglerait les deux. **À trancher par lui.**

---

## Les contrôles : 121 → 138

Onze contrôles neufs, plus une note.

**Sur les fichiers, sans navigateur :**
- chaque `img2` a son fichier, au catalogue et au carrousel ;
- **la face et le dos ne sont pas le même fichier** (comparaison MD5). Deux
  fois la même photo posée par erreur donne une carte qui bascule d'une image
  **vers elle-même** : strictement invisible, donc indétectable à l'œil ;
- carrousel et catalogue connaissent les mêmes paires.

**Dans le navigateur, en mesurant l'opacité réellement calculée :**
- la seconde vue prend la place de la première, toute seule ;
- une pièce à deux vues porte 2 images et 2 pastilles, une pièce à une seule
  photo n'en porte qu'une ;
- l'état de la pastille ne tient pas qu'à la couleur (largeurs comparées) ;
- **témoin** : sous les yeux, le catalogue tourne ;
- hors de l'écran, aucune carte ne bascule ;
- fiche ouverte, le catalogue derrière se fige ;
- au carrousel, **seule** la carte active respire ;
- mouvement réduit : aucune bascule, aucune pastille figée ;
- seconde vue coupée au réseau : la carte reste sur sa face.

---

## ⚠️ Trois leçons de contrôle

1. **Un contrôle de mise en pause a besoin d'un témoin.** « Rien ne bascule
   hors de l'écran » passerait tout seul si le mécanisme était **mort** : deux
   états identiques prouvent l'immobilité, pas la pause. On établit d'abord que
   sous les yeux, ça change.

2. **On échantillonne, on ne compare pas deux instantanés.** Première version :
   état, on attend 5,2 s, état, « ils doivent différer ». La bascule a une
   période de 7,2 s : **une fois sur cinq**, les deux relevés tombent sur la
   même phase et le contrôle échoue sans que rien ne soit cassé. Même famille
   que le contrôle qui échouait au hasard le 2026-08-17. On relève toutes les
   200 ms et on compte les états **distincts**.

3. **Un contrôle qui dit « il manque quelque chose » sans dire QUOI fait perdre
   une demi-heure.** Il nomme maintenant les fichiers.

## ⚠️ Un faux positif corrigé, antérieur au chantier

Le contrôle « aucune ressource locale manquante » échouait sur les **six
`.mp3`**. Ils sont bien sur le disque : la boucle ouvre la page en `file://`,
où Chromium **interdit `fetch()` par principe** (CORS). Pire, ils n'échouaient
qu'**après** le clic sur une pièce : le contrôle passait ou non selon la
vitesse de la machine. Les sons ont déjà leur propre contrôle, `sons()`, qui
sert la page sur un vrai serveur HTTP — c'est le bon endroit. Vérifié identique
sur `main` avant de toucher à quoi que ce soit.

---

## Quand les photos arrivent

```
1. les déposer dans _partage/
2. les ranger, une par dossier : _sources/modele-<clé>/
     · UNE photo  → la pièce a une seule vue
     · DEUX photos → face et dos. Nommer le dos `dos.jpg` suffit à fixer
       l'ordre ; sans ça, c'est l'ordre alphabétique qui tranche.
3. python _nouveaux_modeles.py --poser      (pose ce qui est prêt, pas plus)
4. python _v4/_assembler.py && python _build.py && python _qc.py
5. REGARDER les captures avant de déployer
```

⚠️ `python _nouveaux_modeles.py` sans `--poser` ne touche à rien et dit ce qui
manque, avec le signalement à reconnaître pour chaque pièce.

## Reste à faire

- **les photos elles-mêmes** : les 11 modèles attendent toujours. Les 4 pièces
  du 10/08 servent déjà de démonstration : la bascule est visible en local.
- **trancher les 2 voisinages de nappe du héros** (§6).
- déploiement : rien n'est en ligne, tout est sur la branche.

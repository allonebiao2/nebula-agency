# Hillary M. Styl — le détourage, et le catalogue qui ne mentait plus

**2026-08-06** · suite de la V4 « LA COUPE » · en ligne https://hillary-m-styl.pages.dev

---

## Ce que Mongazi a vu, et que le contrôle qualité ne voyait pas

Deux phrases, deux vrais défauts :

> « je vois des bandes autour du modèle dans le héros, enlève-les, ça doit être
> en png [...] enlève le fond blanc, ça doit être fluide »
>
> « les images doivent être transparentes, enlève ce cadre »

Le héros portait des photos de studio **rectangulaires** : un bloc blanc posé sur
du papier crème, qui **couvrait entièrement le chiffre géant**. L'effet du héros
n'existait donc pas. Le carrousel, lui, enfermait chaque pièce dans une boîte
blanche. 74 contrôles étaient verts pendant ce temps.

**La leçon, encore la même** : un contrôle vérifie ce qu'on lui a appris à
regarder. Il faut ouvrir les captures.

---

## 1 · La transparence : WebP, pas PNG

Mongazi a demandé du PNG. Le PNG est le réflexe correct pour de la
transparence, mais il n'est pas obligatoire :

| Format | Poids des 4 mannequins | Alpha |
|---|---|---|
| PNG | 3 560 Ko | référence |
| WebP sans perte | 2 426 Ko | identique |
| **WebP `quality=94, alpha_quality=100, exact=True`** | **761 Ko** | **écart maximum 0** |

Le canal alpha est **bit pour bit celui du PNG**, pour 4,7 fois moins lourd. À
Cotonou, en 4G, ces 2,8 Mo décident si la page s'affiche ou non. Les PNG sources
sont conservés dans `_sources/detoure/` : on peut revenir en arrière.

Détourage : `rembg` / `isnet-general-use`, **sans `alpha_matting`** (1,9 Go de
RAM et ça tombe), puis seuil alpha, érosion `MinFilter`, léger flou, et
décontamination des bords en RVB pour retirer le halo blanc du studio.

## 2 · Le cadre : la pièce se pose, elle ne tient pas dans une boîte

`.car-c` et `.piece .ph` sont passés en `object-fit:contain` +
`object-position:center bottom`, fond retiré, `drop-shadow` sur la silhouette et
**une ombre au sol** en `radial-gradient`. La pièce a du poids sans qu'on
redessine son contour.

Même traitement dans les trois endroits : héros, carrousel, carte du catalogue.

## 3 · Une seule photo par pièce

Le carrousel avait ses fichiers `coll-*.webp` et le catalogue ses
`piece-*.webp` : **les mêmes quatre photos, en double**. Elles sont fusionnées
sous les noms sémantiques `piece-ceremonie / mira / josy / ville`. Le navigateur
ne télécharge plus qu'une image pour les deux surfaces.

⚠️ Au passage : `_pose_images.py` portait encore un lot `coll-*` qui **écrasait
ses vraies pièces** par des vêtements générés à chaque exécution. Le lot est
retiré, avec le commentaire qui explique pourquoi il ne doit pas revenir.

## 4 · Deux défauts trouvés en regardant les captures

- **« 14 À 14 JOURS »** sur chaque carte. Ses quatre pièces sont à deux semaines
  fermes, donc `jmin === jmax`. Une fonction `libDelai(a,b)` n'annonce qu'un
  chiffre quand les bornes se rejoignent. Ça se lisait comme une erreur de la
  maison.
- **Le prix cassé en deux lignes** sur téléphone : « 100 000 » puis « F ».
  `white-space:nowrap` sur le prix et le délai, et la ligne passe en colonne
  sous 560 px.

## 5 · Ce qui protège désormais

Cinq contrôles ajoutés (**79 au total**, tous verts) :

1. les images du héros et du catalogue **portent un canal alpha réellement
   transparent** (lu au pixel par PIL, pas déduit du nom de fichier) ;
2. **aucun fond opaque ni bordure** sur `.car-c` et `.hsl` ;
3. **prix et délais tiennent sur une seule ligne**, aux trois largeurs (un
   `Range` qui renvoie plusieurs rectangles trahit un retour à la ligne).

Et **une page `404.html`** est désormais écrite par `_predeploy.py`. Sans elle,
Cloudflare Pages répond `200` avec le HTML d'accueil pour un fichier absent, et
ce `200` hérite du cache d'un an. C'est la panne qui avait cassé PISTE le
2026-08-04.

---

## Vérifié en ligne

- 4 diapositives au héros, 4 pièces au carrousel, 5 cartes au catalogue
- aucune erreur JavaScript, aucune réponse ≥ 400
- délais affichés : « 14 jours » cinq fois
- `/fichier-inexistant.css` → **404**, plus un 200 déguisé
- l'image servie comparée **par empreinte MD5** au fichier du disque :
  identique, transparence comprise. ⚠️ `curl -w "%{size_download}"` avait
  annoncé un poids faux et fait croire à un cache empoisonné — **seul le corps
  compte**.

---

## Ce qui reste à obtenir d'Hillary

Inchangé, dans `clients/10-hillary-m-styl/_sources/hillary/PIECES-RECUES.md` :

1. **les 11 mesures de la robe ovale** — ses quatre pièces en dépendent, et
   elles ne sont toujours pas validées par l'atelier ;
2. la **matière** de chaque pièce ;
3. **« haut + jupe »** pour l'ensemble Mira : ce jeu de mesures n'existe pas ;
4. le libellé **« Robe de ville »** sur une photo de robe longue habillée ;
5. d'autres pièces (quatre est un début, huit fait une collection) ;
6. de **vraies photos d'atelier**, pour remplacer les trois plans générés.

---

*NEBULA Agency · Cotonou · 2026-08-06*

---

# Deuxième passe · « ça bugue un peu, surtout sur les chiffres, ça doit suivre »

Mongazi a regardé le héros et a vu quelque chose que 79 contrôles ne voyaient
pas. Trois défauts, tous réels, tous dans le même geste.

## 1 · Le chiffre arrivait 900 ms avant le vêtement

Le chiffre roulait 240 ms, puis son contenu était **remplacé d'un coup**, alors
que la pièce glissait pendant 1,15 s. Il était posé avant qu'elle n'arrive.

Il est maintenant fait de **deux chiffres qui se croisent** : l'ancien sort par
le haut, le nouveau entre par le bas, **dans le sens du mouvement** (`--s` vaut
1 vers l'avant, -1 vers l'arrière), sur exactement la même durée et la même
courbe que le glissement.

## 2 · La courbe partait à plat

`cubic-bezier(.45,.02,.2,1)` : avec un point de contrôle à `y = .02`, il ne se
passe presque rien pendant le premier tiers. **Mesuré : la pièce restait
immobile ~580 ms après le clic, puis se précipitait.** C'est ça qui se lisait
comme un bug.

Remplacée par `cubic-bezier(.25,1,.5,1)` sur 1 s : le mouvement part à la
première image et se pose longuement. Le chiffre porte la même.

## 3 · Le travail lourd bloquait le départ

`ecrire()` fabriquait le chiffre géant (un glyphe de 30 rem, donc un calcul de
mise en page) **et** posait `--piece` sur `:root` (donc un recalcul de tout le
document) **avant** de lancer le glissement.

Découpé en deux : `preparerNum()` fabrique le chiffre et le pose à son point de
départ **hors du chemin critique**, et rend une fonction de départ que `aller()`
déclenche **dans la même image** que le changement de classe des diapositives.
La couleur et les textes passent à l'image suivante : ils suivent le mouvement,
ils ne le portent pas.

## 4 · Deux chiffres restaient empilés au clic rapide

Trouvé par le contrôle, pas à l'œil : « 0302 ». Le verrou de `aller()` et le
retrait de l'ancien chiffre tombent **tous les deux à 1050 ms** — selon lequel
gagne la course, un chiffre restait. Réparé des deux côtés : on jette à l'entrée
tout chiffre déjà sortant, et **seule la transition la plus récente fait le
ménage** (`if (num.lastElementChild !== neuf) return;`).

## Deux corrections d'apparence, vues sur les captures

- **Le pied du « 2 » ressemblait à un bug.** Le mannequin couvre le milieu du
  chiffre, et le pied plat du 2 de Bodoni se retrouvait seul, cerné de blanc et
  de gris : une dalle posée dans le vide. Ombre dure retirée, et un `mask-image`
  fait **fondre le chiffre dans le papier** par le bas.
- **La nappe de couleur virait au gris sale sur le denim.** `color-mix(in srgb,
  var(--piece) 22%, transparent)` : un bleu à 22 % sur du papier crème donne un
  voile gris. Passé **`in oklab` à 26 %** : la teinte survit à la transparence,
  et la nappe redevient une couleur.

## Ce qui a été mesuré, et ce que ça a montré

| Mesure | Résultat |
|---|---|
| Départ du mouvement, pièce et chiffre | **la même milliseconde**, à chaque tour |
| Page au repos, téléphone 4× ralenti | médiane 17 ms |
| Pendant le glissement, même téléphone | médiane **21 ms** |
| Le grain désactivé | aucun gain |

Le glissement coûte **4 ms par image**. Ce n'était donc pas un problème de
performance : c'était la courbe. ⚠️ Les ombres portées sont quand même coupées
pendant le mouvement (`.hsc.bouge`) : une `drop-shadow` sur une photo détourée
de 700 px se recalcule à chaque image, et c'est gratuit de s'en passer une
seconde.

⚠️ **Aucune image du héros en `loading="lazy"`.** Elles sont quatre, elles
pèsent 760 Ko en tout, et le visiteur les verra toutes. Elles sont aussi
**décodées en arrière-plan** 1,2 s après l'ouverture.

## Cinq contrôles de plus (84 au total)

Le chiffre croise vraiment · les deux chiffres sont de part et d'autre · un seul
reste à l'arrivée · il dit la même chose que le compteur · cliquer vite
n'empile rien.

⚠️ **Un contrôle ne doit pas regarder à un instant fixe** : la première version
échantillonnait à 420 ms et tombait pendant un défilement automatique qui avait
avalé le clic. Elle échantillonne maintenant **tout le glissement**, et reclique
si rien n'a bougé.

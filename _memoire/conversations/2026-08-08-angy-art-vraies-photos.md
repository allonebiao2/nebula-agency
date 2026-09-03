# 2026-08-08 — ANGY ART : la vitrine passe aux vraies photos

**Client 11, Angélique Avocevou.** Mongazi envoie 15 photos avec une consigne
précise : « ce ne sont pas ses produits, ce sont des images pour rendre son
activité plus authentique ; les photos des produits arriveront plus tard ».

## Ce qu'il y avait à voir dans les photos

Deux familles, et c'est toute la décision.

**7 photos d'atelier, 100 % réelles.** Angélique au travail à Cotonou : elle pose
l'enduit blanc sur une forme encore nue, elle mélange l'orange sur une palette
tenue dans un vieux cadre doré, elle trace les lignes blanches au pinceau fin,
elle peint dehors au soleil, et surtout elle est **assise de dos devant une toile
de plus de deux mètres**. Ces sept-là racontent un métier.

**8 mises en situation.** Ses masques dans des niches design. ⚠️ **Les masques
sont bien les siens, les intérieurs sont des rendus.** La preuve est dans les
photos elles-mêmes : le terracotta à spirale de la niche en noyer est
**exactement** celui qu'elle peint sur une des photos d'atelier, et le
jaune/orange à collier de perles est celui qu'elle trace sur une autre. Le décor,
lui, se trahit : un livre y est imprimé « PICASO ».

## Ce que ça a permis de supprimer

C'est le vrai gain. Depuis sa mise en ligne, le carrousel de cette vitrine
montrait **8 œuvres générées par IA**, assumées comme une préfiguration. Elles
étaient le point faible du site. Avec ces photos, elles n'avaient plus de raison
d'exister : **les 13 images générées ont été supprimées**, ainsi que
`_gen_images.py` et `_pose_images.py`. Le site ne contient plus une seule image
d'IA.

## L'architecture retenue

7 sections au lieu de 6. Deux nouvelles :

- **« La main, en quatre temps »** : la chronologie vraie d'une pièce, en photos
  d'atelier. L'enduit, le pigment, le trait, l'échelle. C'est elle qui porte
  l'authenticité. Elle remplace l'ancien plein écran « L'ATELIER », qui disait la
  même chose avec une salle de galerie inventée.
- **« Pour un lieu »** : le masque monumental dans un restaurant, au service de
  l'axe le plus commercial de son activité (hôtels, restaurants, halls).

Le carrousel devient **« Dans un lieu »** et assume ce qu'il montre : le cartel de
chaque carte porte le mot **« MISE EN SITUATION »**, répété dans la vue en grand
et dans le texte alternatif lu par les lecteurs d'écran. ⛔ Aucun prix, aucune
dimension, **aucun titre d'œuvre inventé** : la légende décrit ce qu'on voit
(« Le bleu outremer »), elle ne nomme pas une pièce. Seule Angélique peut nommer.

**La signature du héros sort de son propre geste** : la photo se révèle d'abord
sans couleur, comme la forme enduite de blanc, puis le pigment monte. Deux calques
du même fichier (un seul téléchargement) et **seule l'opacité s'anime** : animer
un `filter` sur une image de cette taille aurait fait tressauter l'entrée du héros
sur un téléphone.

## Les défauts trouvés en regardant, puis mesurés

Le QC était vert à 76 contrôles. Les quatre défauts suivants passaient dessous.

1. ⛔ **Cliquer une entrée du menu posait l'étiquette de section à 6 px sous la
   barre fixe** (mesuré à 390 px). Le défilement de ce site est écrit à la main,
   donc `scroll-margin-top` n'était **pas** appliqué : il faut le lire et le
   retrancher. Défaut **antérieur**, il touchait aussi `#demarche` et
   `#portfolio`. Corrigé : 6 px → 90 px.
2. ⛔ **Le texte de « Pour un lieu » se posait sur un masque orange vif.** C'est la
   photo la plus claire du site, et le voile standard tombe à 20 % en son milieu.
3. ⛔ À 768 px, « DÉCOUVRIR L'ATELIER » **barrait** « PIÈCES · UNIQUES » : la
   pilule est en absolu, et dès que le héros passe sur une colonne elle s'assied
   sur la ligne des métriques.
4. Le flou posé sur le livre « PICASO » laissait voir ses **quatre arêtes**.

## Trois familles de contrôles ajoutées

`_qc.py` passe de 67 à **106 contrôles**, dont trois nouvelles familles :

- **l'arrivée par le menu** (l'étiquette respire-t-elle sous la barre ?) ;
- **le chevauchement des boîtes** ;
- **le contraste mesuré sur les pixels réellement rendus** : on masque le texte,
  on photographie la zone, on prend le décile le plus clair du fond.

⚠️ **C'est ce dernier qui compte.** Le contrôle de contraste habituel lit la
couleur de fond **calculée** ; au-dessus d'une photo elle est transparente, donc
il ne voit rien et laisse passer du texte blanc sur de l'orange vif. Tant qu'on
mesure `background-color`, on ne mesure pas ce que l'œil voit.

## Deux pièges rencontrés en écrivant ces contrôles

- `page.screenshot(clip=…)` et `bounding_box()` **ne parlent pas dans le même
  repère** (page contre viewport). Les mélanger fait mesurer une zone qui n'a rien
  à voir : j'ai cru une seconde à un défaut de contraste inexistant.
- Une boîte lue **avant** que le défilement doux se soit posé est périmée de
  plusieurs centaines de pixels. Lire la boîte après stabilisation, toujours.
- Un test de chevauchement doit viser les boîtes **qui portent du texte**.
  Comparer à un `<ul>` large de toute la page déclare des collisions imaginaires.

## Le cache de bordure garde les vieilles images, et on ne peut pas le purger

Après déploiement, les 4 anciennes images IA répondaient encore **200**.
Vérification : `cf-cache-status: HIT`, `immutable` un an. C'est le **cache**, pas
le déploiement : la même URL sur l'alias du déploiement renvoie bien **404**.

⚠️ Sur un `*.pages.dev`, **il n'y a pas de purge** (ce n'est pas une zone du
compte, `scripts/purger.py` ne peut rien). Sans conséquence ici, mais la leçon
vaut pour le parc : **retirer un fichier d'un site NEBULA ne le retire pas
d'Internet.** La protection reste celle posée sur PISTE, la marque de déploiement
dans le nom des fichiers.

## Aussi refait

- **La carte de partage** (`og.png`) porte maintenant une vraie photo d'atelier à
  droite, fondue vers le noir. C'est la vignette que voient les gens quand le lien
  circule sur WhatsApp, et au Bénin c'est là que se joue la première impression.
- **L'affiche A4** est régénérée : elle portait encore l'ancienne image générée.
  Sa photo passe de 76 à 106 mm, ce qui comble une bande vide de près de 5 cm.
  Nouveau script `_affiche.py` (Chromium imprime le PDF) et `_dist.py` (compose
  le paquet de déploiement, et **refuse** de laisser revenir `assets/images/gallery`).

## État de la machine, à surveiller

Le disque de Mongazi était **plein à 100 %** (73 Mo libres sur 290 Go) : le
worktree a échoué deux fois. Libérés sans rien coûter en téléchargement : cache
pip (270 Mo), archives des photos converties en WebP (34 → 6 Mo), et les dossiers
`_qc_captures` de Hillary, PISTE et Angy Art (86 Mo, régénérables par
`python _qc.py --voir`). ⚠️ **Non touchés à dessein** : le cache puppeteer
(684 Mo, il sert au QC de PISTE) et `cercle/node_modules` (336 Mo). Il a aussi
fallu `git config core.longpaths true` : un fichier de la vitrine Weinkeller a un
nom si long que le chemin du worktree dépassait la limite Windows.

## Ce qui reste

- ⏳ **Les photos des œuvres elles-mêmes** (pièce seule, fond neutre, avec titre,
  technique et dimensions). Mongazi les a annoncées. Elles iront dans un tableau
  `OEUVRES` **séparé** de `SITUATIONS` : un catalogue et une mise en situation ne
  se mélangent pas.
- ⏳ Tester le numéro WhatsApp `+229 01 52 00 64 90` une fois pour de vrai.
- ⏳ Adresse de l'atelier, et de vrais avis.

**En ligne et vérifié : https://angy-art.pages.dev** (106 contrôles verts,
corps des réponses relus, pas seulement les codes).

# 2026-08-26 — Au Braisé d'Or : les sauces, et cinq bugs trouvés en chemin

## Ce qui a été fait

Neuf assiettes posées ou refaites en une session : krinkrin (correction),
tête de mouton, Yassa au poulet, pieds de bœuf, graine, arachide
(réattribution), Yassa, tomate. **Les quatorze sauces ont leur photo.**

Chaque plat suit la même chaîne : le fichier au **damier** donne le héros
détouré, la photo sur **fond noir** donne le carré du menu.

## ⚠️ Les fichiers reçus sont TOUJOURS opaques

Sans exception sur ce lot : le fichier qui *montre* un damier est un **JPEG**,
le damier est peint dans les pixels. Le fichier en `.png` est la photo sur
fond noir. **Aucun des deux n'a de canal alpha.** Poser l'un ou l'autre tel
quel mettrait un damier gris ou un carré noir dans le héros.

## La planche comparative, refaite à chaque lot

C'est écrit dans les deux outils, et ça a payé six fois :

| Lot | birefnet | isnet | écart |
|---|---|---|---|
| krinkrin | équivalent | équivalent | — |
| **tête de mouton** | **jette l'assiette**, garde la viande qui flotte | plat entier | **26 points** |
| Yassa au poulet | mange le bord à gauche, encoche à droite | plat entier | 6 |
| pieds de bœuf | ne garde qu'un filet de bord | plat entier | 6 |
| graine | jette l'assiette | plat entier | 14 |
| Yassa | identique | identique | 0 |
| tomate | mange le bord droit, laisse un crochet flottant | plat entier | 3 |

**isnet gagne six fois sur six sur une source en damier.** La conclusion écrite
dans `_damier.py` tient — mais la vérifier reste ce qui a évité de poser **une
viande sans assiette** sur la tête de mouton.

## Les cinq défauts trouvés en chemin

### 1. ⛔ Le krinkrin gardait une dalle de table (le défaut signalé)

83,3 % de matière conservée : sous l'assiette, une large dalle d'ardoise noire
partait avec elle, et sur le fond crème du héros ça faisait un pâté sombre.
Assiette noire sur table noire, aucun masque ne les séparait.

**L'exception du krinkrin tombe.** Il venait d'une source à part pour une seule
raison : sa version détourée du 19/08 était recadrée trop serré. La nouvelle
est bien cadrée, donc il rejoint les autres. La rustine anti-vapeur ne sert plus
non plus : mesuré, 9 lignes étroites au-dessus de l'assiette dont la largeur
croît régulièrement (10, 51, 86, 116) — c'est le coin de l'octogone.

**262 Ko au lieu de 347**, la dalle en moins.

### 2. ⛔ `_photos_sauces.py` mourait en code 137 à la DEUXIÈME photo

Une seule session rembg pour tout le lot : **tué faute de mémoire**, après
avoir écrit la première image sans se plaindre. On croyait le lot passé alors
qu'une seule photo l'était. Même fuite d'onnxruntime que chez Hillary le 20/08.
Remède identique : **une photo, un processus**.

⚠️ Ça allait tomber pile sur les six sauces de cette session.

### 3. ⚠️ En le réparant, il a écrasé deux cartes qu'il n'atteignait plus

Le script mourant n'arrivait jamais jusqu'à `sc-feuille` et `sc-graine`. Réparé,
il les a réécrites : sur `sc-graine`, le carré automatique **coupe tout le bord
du bol**, il ne reste qu'une texture jaune sans vaisselle. Les deux cartes sont
restaurées et **gelées** par un drapeau, avec la raison à côté.

**Réparer un script qui échouait tôt, c'est réveiller tout ce qu'il ne faisait
plus.** Regarder ce qu'il touche pour la première fois depuis longtemps.

### 4. ⛔ Le contrôle du bouton du héros mentait, et depuis longtemps

Deux rouges sur `main`, vérifiés en reconstruisant HEAD. Il **photographiait**
l'opacité à un instant, au milieu d'une animation qui tourne en permanence.
Mesuré sur 63 relevés en 16 s : min 0,00, **max 1,00, médiane 1,00, pleine
opacité 71 % du temps** — le bouton traverse un fondu de 750 ms à chaque
changement de sauce. Il échantillonne maintenant sur un cycle complet et
regarde le **maximum**. Le défaut d'origine (`clearProps:"all"` qui laissait le
bouton transparent pour toujours) reste attrapé : le maximum ne monterait pas.

### 5. ⛔ Une photo portait le nom d'un autre plat depuis le 19 août

Mongazi : « celle actuelle sur la vitrine est pour la sauce d'arachide de base ».
Il avait raison, et **deux choses le prouvaient sans avoir à demander** : la
sauce est crémeuse et beige alors que la graine est rouge d'huile de palme, et
le plat est un **bol rond à bord cuivré** quand toutes les autres photos de la
maison sont dans la même assiette octogonale noire. Un autre jour, un autre
plat.

Les deux formes ont été déplacées vers `sc-arachide`, **les fichiers sources de
`_partage` renommés avec** (on ne garde pas un nom qui ment), et le **gel de la
carte a suivi le fichier**, pas le slug.

## Une opération neuve : `reboucher()`

Sur la graine, le masque avait **percé le rebord du plat** : une fente de 52 px
entre la sauce et le bord extérieur, invisible sur blanc, très visible sur le
crème du héros.

⚠️ **Le bouche-trous par cavité fermée n'a rien trouvé** : la fente était
ouverte, connectée au fond. Il a fallu la traiter **ligne par ligne** — une
assiette n'a pas de fente : tout ce qui est transparent **entre** deux pixels
opaques sur une même ligne, en dessous d'une largeur, se remplit.

⚠️ **Le seuil a été choisi sur mesure, pas au jugé.** Les dix assiettes ont été
mesurées d'abord : zéro ligne fendue sur six d'entre elles, 3 px sur le gombo,
**52 px sur la graine** — mais **161 px sur le moyo et 121 px sur le poisson**.

⚠️ **Et là j'ai failli écrire une bêtise.** J'avais noté que ces deux-là étaient
« des plats à deux bols », donc que la fente y était légitime. C'est faux, et il
a suffi de les regarder : ce sont des bols ronds simples, et l'écart large est
celui **entre le panache de vapeur et le bord du bol**. Les combler souderait la
vapeur au plat. Un seuil à 8 % de la largeur ferme la graine (5,8 %) et le
gombo (0,4 %), et laisse ces deux-là loin au-dessus. Vérifié au MD5 : les six
autres ressortent identiques.

⚠️ Accessoirement, `sc-moyo` et `sc-poisson` **ne passent pas par `_damier.py`**
du tout — ils viennent d'un autre outil. Le seuil ne les protège donc que par
précaution, pour le jour où ils y passeraient.

## Chiffres

- **QC 102 → 94 verts, 0 rouge.** La baisse est mécanique : la suite contrôle
  **une ardoise à la fois**, sur mobile et sur bureau. Chaque photo posée retire
  deux contrôles. Neuf ardoises de moins, dix-huit contrôles de moins, et deux
  gagnés sur l'opacité.
- Il ne reste **aucune ardoise** dans la section des sauces.

## ⏳ Ce qui reste

- ⚠️ **« gbata » ou « gbotâ »** : le menu écrit l'un, Mongazi l'autre. Un seul
  mot, mais c'est le texte du client — pas touché sans réponse.
- La vraie photo de la salle, le numéro WhatsApp à confirmer, les vrais avis,
  l'adresse, le logo, les réseaux.

⚠️ **9e réinitialisation du conteneur** pendant la session, dont une en plein
travail. Pousser après **chaque** sauce est ce qui a tout sauvé : au dernier
retour en arrière, le dépôt local avait perdu les neuf assiettes, `origin` les
avait toutes.

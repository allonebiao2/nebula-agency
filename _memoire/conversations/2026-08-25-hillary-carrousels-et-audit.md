# 2026-08-25 — Hillary M. Styl : les carrousels, et l'audit qui a trouvé le vrai défaut

> Mongazi : « Fais en sorte que les carrousels soient plus fluides et plus
> vites, et analyse le site en profondeur et corrige les bugs. »

## Les carrousels : ce qui gênait n'était pas la vitesse

### ⛔ Le héros jetait les clics

`occupe` tenait 1 050 ms et `aller()` sortait **sans un mot**. Qui appuyait
deux fois de suite ne voyait avancer qu'une pièce : le carrousel passait pour
bloqué alors qu'il obéissait à moitié.

On ne peut pas lever le verrou — deux `aller()` qui se croisent empilent les
classes, c'est ce qui donnait « 0302 » le 2026-08-06. Alors on **retient** le
dernier geste et on le joue à l'arrivée. Un seul en attente : au-delà, le
visiteur ne suit plus ce qu'il a demandé.

**Mesuré après correctif : deux clics rapides = deux pas (02 → 04).**

### ⛔ Le second carrousel n'avait jamais reçu la correction du 6 août

Sa courbe était restée `cubic-bezier(.4,0,.2,1)`, qui met un bon sixième de sa
durée à démarrer — **exactement** le défaut réparé au héros ce jour-là
(« la pièce restait figée ~580 ms après le clic, puis se précipitait »). Une
carte qui ne bouge pas tout de suite se lit comme un clic perdu.

⚠️ **Une correction faite à un endroit n'est pas faite partout.** Personne
n'avait reporté celle-ci sur le deuxième carrousel, deux mois durant.

### Les cadences

| | avant | après |
|---|---|---|
| héros, glissement | 1 s | **.72 s** |
| héros, défilement | 5 s | **4,2 s** |
| cartes, glissement | .8 s | **.6 s** |
| cartes, défilement | 5,5 s | **4,4 s** |
| cartes à deux vues | 7,4 s | **6,8 s** |

⚠️ **Le chiffre géant et la pièce changent de durée ENSEMBLE** (`.hnum span` et
`.hsl` portent la même ligne). Les désynchroniser recréerait le défaut du
06/08, où le chiffre arrivait 900 ms avant le vêtement.

⚠️ Une pièce à deux vues garde un tour plus long : **3 600 ms sont dus à la
face** avant que la carte se retourne, et sans ce reste son dos n'aurait pas
le temps d'être vu. Mesuré après : 4,5 s et 4,3 s entre deux pas.

## L'audit : le catalogue est sain, l'accès ne l'était pas

### Ce qui a été vérifié et qui tient

20 pièces, chaque carte porte son prix · l'express coûte **toujours** plus
cher que le normal, avec **5 suppléments différents propres à chaque pièce** ·
aucun délai inversé · les euros suivent les francs partout · 22 liens, aucun
`href` vide, les 18 ancres pointent vers une section qui existe · 2 liens
WhatsApp sur le bon numéro · aucun identifiant en double · 27 titres, hiérarchie
continue · le panier survit au rechargement · **le délai est celui de la pièce
la plus lente** · le message WhatsApp porte le bon prix express, nomme la pièce,
307 caractères.

Le tunnel **refuse d'avancer** sans la moitié des mesures, et sans un choix
**explicite** entre normal et express : aucun prix par défaut. C'est du bon
travail, pas un blocage — un contrôle qui crierait au bug ici se tromperait.

### ⛔ AU CLAVIER, ON NE POUVAIT PAS COMMANDER

`role="dialog" aria-modal="true"` sur un `<div>` **n'apporte que l'étiquette**.
Contrairement à un vrai `<dialog>`, le navigateur ne pose ni couche supérieure,
ni piège à focus, ni mise à l'écart du fond. Mesuré, fiche ouverte :

- le focus restait sur `<body>` : on ouvrait une pièce et on ne tabulait pas
  dedans ;
- **une seule** tabulation en sortait, et on se promenait dans le catalogue
  caché derrière ;
- rien n'était `inert` : un lecteur d'écran lisait les vingt cartes du fond
  par-dessus la commande ;
- en refermant, le focus retombait sur `<body>` : au clavier on repartait du
  haut du site à chaque fiche fermée.

**Cette fiche EST le bon de commande.** Corrigé pour la fiche et le tiroir du
panier.

⚠️ **Le bouton du son reste dans la boucle, volontairement** : la maison exige
qu'on puisse couper le son en donnant ses mesures. Un contrôle qui
l'appellerait « fuite » se tromperait de coupable — c'est écrit à côté.

⚠️ **`focus({preventScroll:true})` partout** : donner le focus fait défiler la
page, et le moteur de défilement maison se serait battu avec.

### ⛔ Le défilement lissé écrasait tout le monde — la TROISIÈME fois

Le même défaut, **mot pour mot**, que celui trouvé sur Angy Art le même jour,
et déjà rencontré sur Au Braisé d'Or où Lenis arrêtait un `scrollIntoView` à
7 382 px de sa cible. `cible` n'était relue que `if (!anime)`.

**Mesuré : un saut à 200 px ramené à 5 996.**

Correctif identique : on regarde **où**. Entre `courant` et `cible` c'est nous,
ailleurs c'est quelqu'un d'autre.

## Contrôles : 141 → 150

Les neuf nouveaux ont tous été vus **rouges avant le correctif et verts après**,
et celui du défilement porte son **témoin** : il prouve d'abord que la page
glisse, sinon un moteur mort le passerait les doigts dans le nez.

⚠️ **Un dixième contrôle a été corrigé avant d'être gardé** : il comptait le
tiroir du panier, qui porte `aria-hidden="true"` **par construction** quand il
est fermé, et accusait le site d'un défaut qui n'existait pas. Il exclut
maintenant exactement ce que `fondInerte()` ne touche jamais, et il **nomme**
le coupable s'il y en a un.

## ⚠️ Quatre fausses pistes, toutes dues à mes sondes

Elles valent d'être notées : chacune ressemblait à un bug du site.

1. `NaN` dans le message WhatsApp → j'avais injecté un panier au mauvais
   format. Les lignes s'appellent **`{id, qte, express}`**.
2. « la fiche ne s'ouvre pas » → **le rideau d'ouverture dure 4 800 ms** et
   j'attendais 4 200.
3. « la fiche ne s'ouvre pas » (bis) → **ce n'est pas un `<dialog>`** mais un
   `div#ov.on`.
4. « le focus sort de la fiche » → c'était **le bouton du son**, qui y est par
   décision de la maison.

**Toujours vérifier une sonde avant d'accuser le produit.**

## État

Poussé sur `main` : `95b23c2` (carrousels) et `078d279` (clavier, lecteurs
d'écran, défilement). **Rien n'est déployé** — la publication se fait depuis le
PC de Cotonou.

⚠️ **7e réinitialisation du conteneur**, en plein travail : HEAD était retombé
sur un commit d'il y a deux jours et j'ai édité un arbre périmé pendant
plusieurs minutes — l'assemblage effaçait la Robe d'été. Repéré parce que le
fichier avait **perdu 70 lignes** et que trois contrôles avaient disparu.
Récupéré depuis `origin`, modifications rejouées. **Pousser après chaque étape
reste la seule protection.**

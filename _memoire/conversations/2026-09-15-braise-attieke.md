# Au Braisé d'Or — l'attiéké entre à la carte (2026-09-15)

Mongazi : « Je veux que tu me ajoutes sur la vitrine de au braisé d'or le plat
d'Atiele avec bien sûr son image. L'objectif c'est que la présentation soit
dans le même style que les autres. Il s'agit de l'attieke. »

## Ce qui n'était pas dit, et qu'il a fallu demander

L'attiéké **n'existait nulle part comme plat**. Il figurait deux fois sur la
carte, mais en **accompagnement** : « Attiéké » dans la liste des grillades,
« Atchiéké » dans celle des sauces. Aucune photo de la maison, aucun prix.

Trois questions posées, trois réponses :

| Question | Réponse de Mongazi |
|---|---|
| Quel plat, quelle rubrique ? | « y'a poisson à part et viande à part, donc quand on clique sur attiéké on doit pouvoir choisir entre poisson ou viande » |
| Le prix ? | **2 000 F** |
| La photo ? | « Tu m'envoies une vraie photo » |

⚠️ **NE PAS INVENTER UN PRIX est une règle de cette maison**, née le 19/08
quand la propriétaire a corrigé la carte. Demander coûte un aller-retour ;
une faute de prix se paie à chaque commande, tous les jours.

## ⛔ Les deux générateurs d'images étaient à sec

**WaveSpeed 0,03 $** (il en faut 0,14 pour un nano-banana-pro) et
**Higgsfield 0 crédit**, mesurés. Mongazi a de toute façon tranché pour une
vraie photo, ce qui est le bon sens : l'exception d'images générées nommée sur
ce client le 2026-08-26 couvrait des **produits de commodité** (un café serré,
une boule de glace), pas un plat de la maison.

En attendant, le plat part avec **l'ardoise** — son nom écrit sur la pierre,
le mécanisme construit le 19/08 exactement pour ça. **Une place qui attend,
pas un cadre vide.**

## ⚠️ UN CHOIX N'EST NI UNE TAILLE, NI UNE GARNITURE, NI UN BARÈME

Le modèle connaissait quatre façons d'avoir un prix (`p` · `p2` deux tailles ·
`pMax` fourchette · `paliers` barème à N crans) et une façon de choisir
(`garn`, les garnitures qui font MONTER le prix). Poisson ou viande n'entre
dans aucune : **le prix est le même des deux côtés, et on en prend un, un
seul, obligatoirement.**

Le tordre dans `p2` aurait affiché « 2 000 F / 2 000 F » sur la pastille et
appelé ça une taille. Le tordre dans `garn` en aurait fait une option
facultative qui fait monter le prix. D'où un champ neuf, **`choix`**, et son
verrou : sans réponse, le bouton reste gris et dit « Poisson ou viande ? ».

## ⚠️ ET UN PLAT QUI EST DÉJÀ UN ACCOMPAGNEMENT N'EN REDEMANDE PAS UN

La rubrique Grillades exige un accompagnement parmi dix, et **l'attiéké est
l'un des dix**. Sa fiche proposait donc « Attiéké » comme accompagnement de
l'attiéké. D'où le second champ, **`sansAcc`**.

## ⛔ LE PIÈGE DU 2026-08-26 S'EST REFERMÉ À L'ENVERS

Le QC accrochait **trois choses au même clic** : il cherchait « un plat sans
image » pour ouvrir une fiche, et vérifiait au passage l'ardoise **et**
l'accompagnement obligatoire. Le 26/08 il avait planté parce qu'il n'y avait
plus aucune ardoise ; le commentaire posé ce jour-là disait déjà qu'il fallait
les séparer.

En ajoutant l'attiéké, **il est redevenu le seul plat sans photo** : le clic
« ardoise » tombait donc sur lui, et comme il ne demande pas d'accompagnement,
**le contrôle de l'accompagnement se serait éteint sans un mot, tout vert.**

→ **Une règle, une fiche.** Trois clics indépendants : l'ardoise (le plat sans
photo, s'il y en a un), l'accompagnement (**toujours une sauce**, dont la
catégorie en exige un quoi qu'il arrive), le choix (**les plats lus dans la
carte**, jamais recopiés).

## ⚠️ LE CONTRÔLE QUI COMPTE EST CELUI QUI REGARDE CE QUE LA CUISINE REÇOIT

Tout le reste peut être vert — le bloc s'affiche, le bouton bloque, il se
débloque — et la commande partir en disant « 1 × Attiéké » sans dire poisson
ou viande. Un contrôle lit donc le **lien WhatsApp du panier** et exige
« Attiéké (Poisson) ».

## ⛔ DEUX ROUGES QUI N'ÉTAIENT PAS DU SITE : `button.flex-1`

Le QC visait le bouton d'ajout par `button.flex-1`. **Les boutons de taille
portent `flex-1` eux aussi.** Sur « Sauce Yassa au poulet », seule sauce à
deux tailles, il cliquait donc **« Quart de poulet · 2 500 F »** au lieu de
« Ajouter » : rien n'entrait au panier, deux contrôles viraient au rouge.

Et comme le héros montre une sauce différente à chaque passage, **ça ne ratait
qu'une fois sur quatorze** : défaut antérieur, invisible presque toujours.
Mesuré côte à côte, puis réparé par une prise explicite, `data-ajouter` :

```
  ancienne sonde   vise : Quart de poulet · 2 500 F
  nouvelle sonde   vise : Choisissez un accompagnement
  ligne commandee : • 1 × Sauce Yassa au poulet (Quart de poulet) + Telibo — 2 500 F
```

## ⚠️ MA PROPRE SONDE A CASSÉ L'INSTRUMENT

Le contrôle neuf du message WhatsApp nommait sa variable `attendu` — **le nom
qu'utilise déjà la boucle pour le compte de plats**. Le premier passage
(mobile) passait, le second (bureau) mourait sur un `%d` qui recevait
« Attiéké (Poisson) ». Renommée `dit`.

## ⛔ ET UN CONTRÔLE QUI PASSE TOUJOURS, ÉCRIT DE MA MAIN

`dire(… or True, "")` s'était glissé dans le premier jet. Retiré : un contrôle
qui ne peut pas échouer ne protège rien, et occupe la place de celui qui
aurait pu.

## Un défaut vu sur la capture, QC vert

Le bouton bloqué affichait **« Poisson ou viande » puis « ? » seul sur la
ligne suivante**. La typographie française demande de toute façon une **espace
fine insécable** avant le point d'interrogation : ` ` règle les deux.

## L'état

- **53 plats** (52 avant), 9 rubriques inchangées.
- `python _outils/_qc.py` → **117 contrôles verts** (102 avant).
- `python _outils/_qc_partage.py` → **36 verts**, 53 plats balisés.
- Nouveau `_outils/_vues_attieke.py` : 6 captures, 390 et 1440.

## Ce qui reste

1. **La vraie photo** (Mongazi l'envoie). La poser = une entrée dans `PHOTO`
   de `index.html`, le fichier dans `assets/images/` **et**
   `experience/public/carte/`, puis `node _outils/_extraire_carte.js`.
2. **La description**, écrite par moi, à faire relire par la maison.
3. **Quel poisson, quelle viande** : la fiche dit « Poisson » et « Viande ».
4. **La rubrique** : Grillades, faute d'une meilleure.

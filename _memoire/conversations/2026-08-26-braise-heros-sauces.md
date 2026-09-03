# Au Braisé d'Or — les six dernières photos, la glace à la boule, et le héros qui devient le comptoir

*2026-08-26. Client 09. Trois demandes de Mongazi dans la même session.*

---

## 1. « Les déjeuners, les desserts, génère-les d'abord et pose-les »

Six lignes de la carte n'avaient pas d'image et s'affichaient en **ardoise**
(le nom écrit sur une tuile de pierre) : œuf sur plat, café au lait écrémé,
café chaud serré, Lipton citron, yaourt, glace.

**Fait** : les six sont générées et posées (`_outils/_gen_plats.py`, WaveSpeed
`nano-banana-pro`, **0,84 $**), en 900 × 900, aux deux endroits qu'il faut
(`assets/images/` **et** `experience/public/carte/`).

### ⚠️ La règle, et pourquoi elle n'a pas été appliquée ici

Le cerveau dit depuis le 2026-08-01 : *« INTERDIT ABSOLU : une photo produit
générée par IA présentée comme le catalogue du client. »* Mongazi a demandé
l'inverse, explicitement, sur ce client précis — le seul où l'héritage généré
est déjà assumé (tranché le 2026-08-20, sujet clos).

**Ce que ça reste** : une exception nommée, sur un client, pour des produits de
**commodité** — un café serré, un thé au citron, une boule de glace ne sont pas
des créations de la maison. **Ce que ça ne devient pas** : une autorisation
générale. La règle tient pour tous les autres clients et pour tout plat
signature. C'est écrit en tête de `_gen_plats.py`.

### Le socle de prompt, relevé sur les images existantes

Une série, pas une collection : même lumière rasante chaude, même table de
bois sombre, même flou d'arrière-plan, **un 100 mm à f/4**, sujet seul et
centré, et la ligne de négations qui finit tout
(`no text, no lettering, no watermark, no logo`). Une seule phrase change d'une
image à l'autre.

---

## 2. Le prix du yaourt et de la glace — et le modèle qui n'y arrivait pas

Mongazi : **yaourt 600 F** · **glace : 1 boule 1 000, 2 boules 1 500, 3 boules
2 500**.

### ⛔ TROIS PRIX N'ENTRAIENT PAS DANS LE MODÈLE

Un plat pouvait avoir `p` (un prix), `p2` (une deuxième taille) ou `pMax`
(une fourchette). La taille était un **booléen** `grand` dans la fiche. Poser
la glace là-dedans revenait à **jeter un des trois paliers** : la boule à
2 500 F disparaissait, et la maison encaissait 1 500 F à sa place, tous les
jours, sans que personne le voie.

**Ajouté** : `paliers?: [string, number][]`, un barème à N crans, avec son
libellé et son prix exact par cran. La fiche ne connaît plus qu'un **index** :
`p2` et `paliers` sont ramenés à la même liste à l'entrée.
Quatre endroits suivent la donnée, sans recopie :
`index.html` (la vérité) → `_extraire_carte.js` → `carte.ts` → la fiche, la
pastille de prix, **et les données structurées** (N offres, une par cran).

⚠️ **Le balisage a maintenant QUATRE façons d'avoir un prix**, et les confondre
ment au client : `pMax` = fourchette → une `AggregateOffer` · `p2` = deuxième
taille → deux offres · `paliers` = barème → N offres · `p: 0` = pas de prix →
aucune offre.

---

## 3. « Toutes les sauces dans le héros, et beaucoup plus vite »

> « je veux que toutes les sauces soient dans le carrousel dans la hero, et que
> ce carrousel avance tout seul et beaucoup plus vite, et optimisé, de telle
> façon qu'on puisse directement commander ces sauces depuis la hero. »

### ⛔ LE DÉFILEMENT ÉTAIT LE MOTEUR, ET C'EST CE QUI BLOQUAIT TOUT

La scène était une **piste de N × 100vh** parcourue par le défilement
(ScrollTrigger « scrub » + aimant). À quatre plats : 400vh, un beau voyage.
**À quatorze sauces : 1 400vh** — quatorze écrans à traverser avant d'atteindre
la carte. Et « beaucoup plus vite » aurait fait **défiler la page toute seule
à toute vitesse** : ce n'est pas un carrousel, c'est une fuite.

**La scène tient désormais sur UN écran**, et l'index est piloté par un tween
sur un simple nombre. Le mouvement des assiettes (la diagonale + la rotation +
l'échelle qui recule, réglé image par image sur la vidéo de référence) n'a pas
bougé d'un pixel : **c'est son moteur qui a changé, pas son dessin.**

Trois choses tombent d'elles-mêmes :
- la crainte du 2026-08-21 (« reboucler ferait REMONTER la page ») **n'existe
  plus** : avancer ne touche plus au défilement. La boucle est franche, sans le
  tour de respiration qu'il avait fallu ajouter ;
- le carrousel tourne **par le chemin le plus court sur l'anneau** : de la 14e
  à la 1re, on avance d'un cran, on ne recule pas de treize ;
- on peut enfin **commander** sans que la scène se dérobe sous le doigt.

⚠️ **Lenis reste** : `components/aller.ts` passe par `window.__lenis` pour
sauter aux catégories. Un `scrollIntoView` lancé à côté de Lenis s'arrête en
chemin (mesuré : le saut vers « Cocktails » restait à 7 382 px de sa cible).

### ⚠️ LA PAUSE AU SURVOL QUI AURAIT TUÉ LE CARROUSEL

Premier jet : `onPointerEnter` sur la scène pour mettre en pause. **La scène
fait tout l'écran**, et la souris d'un visiteur est toujours quelque part
dessus : sur un ordinateur, le carrousel ne serait **jamais reparti**, et on
aurait cherché le bug dans le tween. On ne s'arrête plus que là où l'on vise
quelque chose : la carte de verre (le bouton) et la bande des miniatures.

### « Toutes » veut dire toutes, y compris celles sans photo

`DISHES` n'est plus une liste écrite à la main : c'est **la catégorie Sauces de
`carte.ts`**, lue, avec ses prix et ses textes. Deux vérités pour le même plat,
c'était une faute de prix qui attendait son tour. Ajouter une sauce à la carte
la fait entrer au héros toute seule, et le QC le **réclame** (il compte les
sauces dans les données).

Les sauces sans photo prennent une **ardoise ronde** — le disque de pierre au
nom de la sauce, avec son **filet à la couleur de la sauce** : huit ardoises
identiques à la file ressemblent à une panne, la même pierre avec huit couleurs
ressemble à une collection.

⚠️ **Béchamel et Crème n'auront pas de découpe** : `_detoure_plats.py` le
documente depuis le 19/08 (isnet garde un morceau d'ardoise sous le bol, et
l'ouverture morphologique mord dans le bol). Elles attendent une vraie photo.

### Ce qui a été optimisé, vraiment

- **Les quatorze découpes pèsent plus de 2 Mo.** On ne monte que les assiettes
  déjà approchées (fenêtre glissante, liste qui ne fait que grandir) : **4 au
  premier écran**, et le QC refuse au-delà de 5.
- **On ne repositionne plus quatorze assiettes par image.** Au-delà de la
  fenêtre, l'assiette est **rangée une fois** (opacité 0) et on ne la retouche
  plus tant qu'elle ne revient pas.

### Commander depuis le héros : un pont, pas un second moteur

⛔ **Ce qu'on n'a pas fait** : recoder « ajouter au panier » dans le héros.
Ç'aurait été un **deuxième moteur de commande**, avec sa propre idée du prix,
de l'accompagnement et de la fourchette — et le jour où l'un des deux change,
la page vend deux prix différents pour la même sauce.

✅ `data/commande.ts` : le héros **demande**, la carte **ouvre sa propre
fiche**. Une seule fonction traverse, et c'est un nom de plat. La fiche qui
s'ouvre est exactement celle du menu — mêmes garnitures, **même accompagnement
obligatoire**, même fourchette, même panier, même message WhatsApp.

⚠️ **La barre du panier recouvrait la scène.** Elle est fixe, en bas, et depuis
qu'on ajoute depuis le héros elle apparaît **pendant** qu'on y est : elle se
posait par-dessus la barre du bas ET par-dessus le carrousel. Trois rangées de
boutons empilées, deux inutilisables. Le corps du document porte maintenant
`a-panier`, la scène remonte, et un contrôle **mesure le chevauchement**.
(Même famille que la règle née sur Mon Bénin : *un instrument flottant ne
recouvre jamais un autre instrument*.)

---

## ⛔ CE QUE LE QC VERT NE VOYAIT PAS — quatre défauts trouvés SUR LES CAPTURES

Le QC était vert à 90 contrôles. J'ai quand même photographié les quatorze
sauces, en 390 et en 1440, et regardé les vingt-huit planches. Quatre défauts,
dont deux graves, n'apparaissaient dans aucun contrôle et ne faisaient aucune
erreur en console.

### ⛔ 1. `clearProps: "all"` VIDE L'ATTRIBUT `style`
Il ne retire pas « ce que GSAP a posé ». Il vide tout, y compris ce que le
composant y avait écrit.

- **Le bouton qui prend la commande était INVISIBLE.** Sa couleur était en
  style en ligne : après l'animation, `background-color: rgba(0,0,0,0)` avec un
  texte crème, sur une carte de verre claire. **1,1:1 mesuré.**
  ⚠️ **Le défaut est ANTÉRIEUR à cette session** : l'ancien bouton vert
  « Commander sur WhatsApp » avait exactement le même sort, sur le site en
  ligne. C'est la **deuxième fois** que GSAP fait disparaître le seul bouton
  qui rapporte de l'argent sur cette carte — la première est écrite en tête
  d'`InfoCard.tsx` depuis le 12/08.
- **La deuxième ligne du titre ressortait plus PETITE que la première**, alors
  que c'est la signature du héros (fine et espacée, puis très grasse). Son
  corps est calculé par sauce, donc en style en ligne, donc effacé.

→ **`clearProps: "opacity,visibility,transform"`** : on ne nettoie que ce que
l'animation a touché. Et une couleur fixe va dans une **classe**, qu'aucun
`clearProps` ne peut atteindre.

### ⛔ 2. L'ardoise ronde sortait de sa boîte de 100 px
`absolute inset-0` + `aspect-ratio` + `margin: auto`. Sur grand écran la boîte
de l'assiette est carrée, tout allait bien. Sur téléphone elle fait
`100 % × 30vh` — **350 × 253** — et les deux `inset` fixent déjà les deux
dimensions : **`aspect-ratio` est alors ignoré**. Le disque se posait
par-dessus l'accroche et le titre.
→ la boîte devient un **conteneur mesuré** et le disque prend
`min(100cqw, 100cqh)` : aucun autre calcul CSS ne sait dire « le plus petit des
deux côtés ». (`width: 100%` reste en repli.)

### ⛔ 3. La pile de points se posait sur le texte, sur téléphone
Sur grand écran elle vit dans la marge gauche, vide. Sur téléphone la scène est
une **colonne pleine largeur** : les quatorze points tombaient sur l'accroche
et sur le titre. Et ce sont quatorze cibles de 5 px sur un écran tactile, alors
que la bande des miniatures, juste dessous, donne déjà accès à toutes.
→ **masquée sous 768 px**. (À quatre plats la colonne était courte et le défaut
se voyait à peine : c'est le passage à quatorze qui l'a rendu flagrant.)

### ⛔ 4. Les deux flèches du carrousel étaient posées SUR des miniatures
La bande était en `overflow: visible` et les flèches juste à l'extérieur
(`-left-9`). À quatre plats rien ne dépassait jusque-là ; à quatorze la piste
déborde des deux côtés et les chevrons se retrouvaient au milieu de la rangée.
→ `overflow-x: clip` (l'horizontale seulement : la verticale laisse la
miniature active monter de 15 px avec son ombre ; `hidden` aurait rogné
l'ombre).

⚠️ **La leçon est celle du 2026-08-01, encore** : *une vitrine n'est pas finie
quand elle marche.* Le QC dit que rien n'est cassé. Il ne dit pas que ça se
voit. `_outils/_vues_heros.py` photographie maintenant les quatorze sauces aux
deux largeurs — et chacun des quatre défauts a reçu son contrôle.

## Deux défauts trouvés en chemin, sans rapport avec la demande

⛔ **La carte de verre listait les mauvais accompagnements.** Elle affichait
« riz, attiéké, aloco… » — ceux des **grillades** — alors que le héros ne
montre que des **sauces**, qui se servent au telibo, à l'agbéli, au wassa
wassa. Elle les **lit** maintenant dans la carte.

⛔ **LE SITE A DEUX NUMÉROS WHATSAPP.** `index.html` écrit `2290156057157`
(dix chiffres, avec le `01`) ; `experience/data/dishes.ts`, **le fichier que le
site servi utilise**, écrit `22956057157` — **le `01` a sauté**. C'est celui
sans le `01` qui reçoit aujourd'hui toutes les commandes.
⚠️ **Rien n'a été touché** : le cerveau interdit de modifier un lien WhatsApp
sans confirmation. À trancher avec la maison.

---

## L'état

- **62 → N contrôles** dans `_outils/_qc.py`, avec trois familles neuves :
  le héros (toutes les sauces, il avance seul, il s'arrête derrière la fiche,
  on y commande, aucun titre ne déborde, la barre ne recouvre rien) et la
  glace à trois paliers.
- ⚠️ **Le contrôle « ça avance tout seul » a un TÉMOIN** : on prouve d'abord le
  mouvement, sinon un contrôle de pause passe aussi quand le mécanisme est
  mort. Et la mesure des titres se fait **sous `prefers-reduced-motion`**,
  sinon la scène avance entre le clic et la mesure et on croit mesurer la 7e
  sauce en mesurant la 8e.

### ⚠️ TROIS INSTRUMENTS FAUX, ZÉRO PANNE DU SITE

Chacun accusait un site sain. Un contrôle faux coûte plus cher qu'un contrôle
absent, parce qu'on le croit.

1. **Il mesurait le X d'une animation.** Le contrôle de débordement du titre
   comparait `getBoundingClientRect()` 260 ms après le clic, pendant que le
   titre entre par un `fromTo({x: 50})` de 0,7 s. ⚠️ **GSAP ignore
   `prefers-reduced-motion`** — seul notre code le lit. Verdict : « KRINKRIN
   dépasse de 36 px » sur un titre parfaitement posé.
   → **`scrollWidth - clientWidth`**, qui ne connaît pas les transformations,
   et qui voit en plus le mot qui ne peut pas aller à la ligne : exactement le
   défaut cherché.
2. **Il mesurait la voisine, garée hors champ.** Le contrôle du débordement de
   l'ardoise comparait le disque à `.scene-plat`, la boîte commune. Or les
   quatorze assiettes sont **déplacées** par GSAP : il attrapait une assiette
   rangée à 74 % de large et annonçait **170 px** de débordement.
   → on compare l'enfant à **son propre conteneur** : les deux subissent la
   même transformation, leur différence est du pur débordement.
3. **`display: none` laisse les boutons dans le DOM.** Le contrôle des points
   passait en annonçant une pile visible, alors qu'elle est masquée sur
   téléphone. → on teste aussi que la boîte a une taille.

### ⏳ Ce qui reste

- **Les six photos de sauces** que Mongazi envoie (arachide, tomate, tête de
  mouton, pieds de bœuf, Yassa, Yassa au poulet) : elles se posent dans
  `PHOTO` d'`index.html` + une découpe dans `/plats/`, et l'ardoise s'éteint
  toute seule.
- Béchamel et Crème : une vraie photo, la découpe est impossible.
- L'aileron (correction au surligneur), le numéro WhatsApp, la vraie photo de
  la salle, les vrais avis, l'adresse.

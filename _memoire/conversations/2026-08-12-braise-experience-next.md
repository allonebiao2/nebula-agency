# 2026-08-11/12 · AU BRAISÉ D'OR — l'expérience Next.js et le catalogue de vente

**EN LIGNE : https://au-braise-dor.pages.dev** · dossier
`clients/09-au-braise-dor/experience/`

---

## Le point de départ

Mongazi demande de reprendre **toute la présentation du catalogue**, sans
enlever la vidéo ni les photos des plats. Puis il envoie **une vidéo de
référence** (un prototype de présentation de plats) et un cahier des charges
très détaillé : Next.js 14, TypeScript, Tailwind, GSAP + ScrollTrigger +
CustomEase, Swiper, Lenis, avec la reproduction fidèle des animations.

## Les deux décisions prises avec lui avant d'écrire une ligne

1. **L'expérience passe AU-DESSUS de la carte**, elle ne la remplace pas. Le
   restaurant garde ses 48 plats commandables ET gagne sa vitrine.
2. **La pile technique est la sienne.** J'avais recommandé le site actuel sans
   bibliothèque (précédents Hillary V4, Angy Art, Mon Bénin, où des briefs
   demandaient GSAP et Lenis et où tout a été écrit en natif). Il a maintenu
   son choix. C'est le sien, on l'exécute.

⚠️ **Coût mesuré et annoncé une fois, sans y revenir : 179 kB de JavaScript au
premier chargement.**

---

## Ce qui a été construit

**L'expérience** (`components/`) : la scène fixe, la piste de défilement
invisible de N × 100vh qui pilote la position des assiettes (scrub) avec un
aimant, le titre en deux lignes qui **se dédouble** (la fine part à gauche, la
grasse à droite), la carte de verre qui glisse avec ses éléments en cascade, le
prix qui monte de 0, le carrousel Swiper dont l'item actif est **surélevé**,
l'indicateur de gauche où le lieu courant devient **un trait**, la barre du bas
et son bouton micro, le tilt 3D à la souris, le flottement de l'assiette.

**Les 4 assiettes détourées** au rembg depuis les photos du site, alphas
faibles coupés (sur fond sombre la fumée était une ambiance, sur le mur clair
elle devenait une traînée grise), puis **WebP `alpha_quality=100, exact=True`** :
3,4 Mo → **449 Ko**, alpha vérifié identique au pixel près.

**La carte complète en dessous** : `_outils/_extraire_carte.js` lit le tableau
`CATS` dans `index.html`, l'évalue et le réécrit en TypeScript. 8 catégories,
48 plats, 48 photos, accompagnements, deuxièmes tailles. ⚠️ **Recopier une
carte de 48 prix à la main, c'est s'offrir une faute qui se paie à chaque
commande, tous les jours, sans que personne la voie.**

**Le moteur de commande** refait en React : fiche (taille, accompagnement,
quantité), panier cumulatif, mode sur place / à emporter / livraison, message
WhatsApp rédigé.

**Le pied de page** : ⚠️ **écrit en catastrophe avant la bascule**, parce que
remplacer le site c'est remplacer TOUT le site. Seraient partis d'un coup : les
deux numéros, l'adresse électronique, le WiFi, les horaires, le traiteur, la
place des fêtes, et **les mentions légales RC et IFU**. Un restaurant qui perd
son RCCM de son site, ce n'est pas un détail de mise en page. Le titre et la
description de l'ancienne page sont gardés aussi : ils portent son
référencement depuis juillet.

---

## LES SEPT DÉFAUTS TROUVÉS, ET COMMENT

### 1. Les 48 photos se téléchargeaient toutes d'un coup (mesure, avant tout)
Sur un téléphone, **avant même d'arriver au menu**, le navigateur téléchargeait
**4,3 Mo**. La page ne déclenchait pas son événement `load` en 30 secondes **en
local**. Cause : les photos étaient en `background-image`, et un navigateur ne
sait pas différer un fond CSS. Passées en `<img loading="lazy">` : **50 images
au chargement → 21**, puis **0 photo de carte avant d'y arriver** dans la
version Next.

### 2. ⚠️ `gsap.from()` laisse l'interface invisible si on l'interrompt
**Le bouton « Commander sur WhatsApp » était à `opacity: 0, visibility:
hidden`.** La carte s'affichait complète, sauf le seul bouton qui rapporte de
l'argent. `from()` pose l'état de DÉPART et compte sur la fin du tween pour
révéler l'élément : un re-rendu React, un contexte qui se replie, et l'élément
reste caché **pour toujours**. → `fromTo()` + `clearProps` partout.

### 3. Les quatre assiettes visibles en même temps au premier écran
Le calcul de position ne tournait qu'au défilement. Il tourne au montage aussi.

### 4. Une scène en `fixed` ne se décolle jamais
Elle serait restée en travers des 48 plats. → `sticky` dans un parent de
N × 100vh : elle tient l'écran le temps du voyage et rend la main à la fin.

### 5. La mise en page téléphone : ne jamais empiler à la main
Premier essai : les trois blocs à 39 %, 56 % et 7 % de la hauteur. Ça tenait à
844 px et se chevauchait à 640. ⚠️ **Un pourcentage de hauteur ne sait rien de
la hauteur en pixels du texte qu'il contient.** → un conteneur en
`display: contents` sur grand écran (il n'existe pas, la composition absolue
reste intacte) et en **colonne flex** sur téléphone.
⚠️ Piège dans le piège : en `width: auto`, la boîte de l'assiette est mesurée à
**ZÉRO de large**, ses enfants étant tous en position absolue. L'assiette
disparaissait alors que l'image était chargée. → `width: 100%`.

### 6. ⚠️ Un conteneur plein écran avale les clics des boutons posés avant lui
Le bouton « … » du héros s'affichait, s'illuminait au survol, **et ne faisait
rien** : le conteneur des assiettes le recouvrait. → `pointer-events-none`.

### 7. ⚠️ LENIS TIENT LE DÉFILEMENT : tout `scrollIntoView` lancé à côté meurt
Mesuré **en ligne** : le saut vers « Cocktails » s'arrêtait à **7 382 px** de sa
cible, sans la moindre erreur en console. → `components/aller.ts`, tous les
sauts passent par l'instance Lenis exposée, avec repli si elle n'est pas
montée. Après : **+8 px de la cible**, sur PC et téléphone.

---

## LE MOUVEMENT DES ASSIETTES : ma faute, et la méthode

J'avais écrit une sortie **verticale**, du bas vers le haut. Mongazi : « de
base dans la vidéo ça roule en cercle vers la droite, là ça part en vertical du
haut vers le bas, c'était pas censé être ça ».

J'ai extrait la transition **image par image, à 12 centièmes d'intervalle**
(ffmpeg via `imageio_ffmpeg`, disponible sur ce poste). La vidéo montre :
**l'assiette qui arrive vient du HAUT À DROITE, descend en tournant sur
elle-même, celle qui part continue vers le BAS À GAUCHE.** Elle roule.

→ Trois mouvements combinés au lieu d'un : diagonale (74 % / 66 % par plat),
**rotation de presque un quart de tour**, échelle qui recule. C'est la rotation
qui fait tout : sans elle une diagonale n'est qu'un glissement.

⚠️ **LEÇON : une vidéo de référence se MESURE image par image avant d'écrire
l'animation. Elle ne se résume pas de mémoire.**

---

## L'ALLER-RETOUR SUR LA DIRECTION, ET CE QU'IL A APPRIS

Mongazi demande de remettre **la vidéo du gril en fond**. La scène bascule dans
le sombre (sur un mur crème, un feu ne se voit pas), le voile est réglé **non
uniforme** : dense à droite où vivent le titre et la carte, ouvert à gauche où
le feu doit se voir. Contraste mesuré sur les pixels rendus : 7,45:1 sur PC.

Puis : « finalement remets ça comme c'était mdr, c'était trop beau avant ». →
`git revert`. **La version braise est dans l'historique (32062e3), la reprendre
est une commande.**

⚠️ **CE QUE CET ALLER-RETOUR A PROUVÉ : basculer TOUTE la scène du clair au
sombre n'a demandé de réécrire que CINQ JETONS de couleur, aucun composant.**
C'est exactement à ça que servent des jetons. Un site où les couleurs sont
écrites en dur dans les composants aurait coûté une journée.

⚠️ **Et la vidéo montrait LE GRIL, pas la salle. Aucune photo de la salle n'a
jamais été reçue.**

---

## LA DERNIÈRE VAGUE : le catalogue optimisé pour la vente

« Je veux que toute personne qui vient directement à partir de la héros puisse
commander tous les plats, toutes les catégories, tout accessible depuis cette
belle héros section. »

- **Le filtre était un mur** : choisir « Pizza » faisait **disparaître 38
  plats**. Sur un catalogue, ce qu'on cache ne se vend pas. Les chips sont
  devenues des **ancres**, tout reste affiché, la chip active suit le
  défilement (IntersectionObserver), et chacune annonce son nombre de plats.
- **Le héros ne disait pas que la carte existait** : le bouton « … », jusque-là
  décoratif, ouvre un **tiroir des 8 univers** avec photo, nombre de plats et
  signature.
- L'appel à l'action annonce le chiffre : « Voir la carte · 48 plats ».
- Et **tout le site est passé dans la langue du héros** : la carte et le pied
  étaient restés en braise sombre, le site racontait deux histoires.

---

## Les outils laissés dans le dossier

| Fichier | Ce qu'il fait |
|---|---|
| `_outils/_extraire_carte.js` | relit `index.html` et régénère `experience/data/carte.ts` |
| `_outils/_carte_claire.py` | passe la carte et le pied dans la langue du héros, par remplacements ciblés |
| `_outils/_catalogue_vente.py` | ancres + scroll-spy + tiroir des catégories |

⚠️ Ces trois scripts **s'arrêtent net si un motif a disparu**, pour ne jamais
repeindre à moitié.

## Publier

```bash
cd clients/09-au-braise-dor/experience
npm run build                       # sort dans out/
cp -r ../assets/docs out/           # l'affiche A4 et ses QR gardent leur adresse
npx wrangler pages deploy out --project-name au-braise-dor --branch main
```

⚠️ **L'alias Cloudflare a du retard** : un fichier peut répondre 404 huit
secondes après le déploiement et 200 quinze secondes plus tard. Ne pas
diagnostiquer une panne là-dessus.

## Ce qui reste

- **La vraie photo de la salle.** Le fond est un mur neutre, pas leur
  restaurant.
- Le numéro WhatsApp à confirmer (01 56 05 71 57 câblé, l'enseigne affiche
  43 99 29 29).
- Les vrais avis et le nom du chef : les champs `chef` et `avis` existent dans
  les données et s'affichent tout seuls le jour où ils arrivent. ⛔ Rien
  d'inventé en attendant.
- L'ancien `index.html` reste dans le dépôt : un retour arrière est un
  déploiement, pas une reconstruction.

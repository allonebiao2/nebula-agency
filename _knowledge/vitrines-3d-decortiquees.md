# Les vitrines « 3D au défilement » décortiquées (19/11/2026)

Demandé par Mongazi après avoir vu nos premiers aperçus : « la 3D ne se ressent pas, on dirait des vidéos qui tournent en
boucle, un travail de 300 euros ; l'objectif c'est 10 000 euros ». Neuf vidéos Pinterest à étudier « à 99 % ». Huit ont été
téléchargées et analysées image par image (la huitième le 19/11 à 10 h 53, par le Chrome de Mongazi connecté à
Pinterest). ⚠️ La neuvième (`pin.it/zl6lmLOe`) renvoie à l'accueil de Pinterest : le lien compte 8 caractères au lieu
de 9, il a été tronqué au copier-coller. À redemander à Mongazi.
Vidéos, planches et pages brutes hors dépôt : `C:\Users\USER\nebula-apercus\pinterest\etude-3d\`.

## 1. Ce que montre chaque vidéo, et comment c'est fait

**Observé** = mesuré sur le site en ligne (REA, CDP). **Déduit** = lu sur les images de la vidéo.

| # | Vidéo | Ce qu'on voit | Comment c'est fait |
|---|---|---|---|
| 1 | **Alethia** (alethia.earth, agence ++hellohello) | Un rocher couvert de mousse flotte ; au défilement la caméra fonce sur lui, **entre dedans**, ressort dans un autre monde (sol, plantes, brume), arrive sur une station météo, puis la page devient éditoriale. | **Observé** : site **Framer**, aucun Three.js. **181 images WebP de 1920 px** (`floating-island_00000…00180.webp`) dessinées dans **un canevas fixe**, image choisie selon le défilement. Plus des vidéos WebM en boucle (nuages, « scan »), des animations Lottie et Framer Motion pour les textes. La « 3D » est **calculée à l'avance** (Blender ou C4D) puis jouée au doigt. |
| 2 | **Forge Automotive** (prix « Site du jour ») | Voitures de luxe sur fond noir, grands titres à empattements, photos qui s'ouvrent dans des masques, écrans coupés en deux, volets horizontaux, la gamme alignée à la fin. | **Déduit** : masques (clip-path) animés au défilement, images qui grossissent dans leur cadre, textes révélés ligne par ligne, sections épinglées. Pile courante : GSAP ScrollTrigger + défilement amorti (Lenis). Site non retrouvé : non vérifié. |
| 3 | **Promoteur immobilier** (Londres) | « We build what lasts » : **le terrain vide devient charpente, puis murs, puis maison finie** à mesure qu'on descend ; ensuite des sections blanches, des chiffres, une galerie de projets. | **Déduit** : suite d'images **à caméra fixe** dont le contenu change d'état (plans générés puis enchaînés), jouée au défilement. Le défilement **raconte une transformation**. |
| 4 | **Nuii** (glaces, concept QClay sur Dribbble) | Le bâtonnet au centre, ses ingrédients en lévitation, des **formes organiques** qui ouvrent sur des photos d'ambiance (savane, lion), un carrousel de parfums avec une couleur par produit. | **Déduit** : produit détouré + masques SVG qui se déforment + couches en parallaxe + thème de couleur par produit. |
| 5 | **Effet portail** (modèle Slider Revolution) | Une arche de pierre dans un paysage ; on **traverse l'arche** et l'on se retrouve dans un autre monde (désert, nuit, orage, aurore boréale), l'arche restant le cadre. | **Déduit** : 2,5D en couches : arche en PNG transparent au premier plan, décor derrière ; la transition agrandit l'arche jusqu'à la traverser (flou de premier plan) pendant que le monde suivant apparaît dans l'ouverture. |
| 6 | **Soin VERA** (concept Figma) | Le mot géant « NOURISH » derrière des feuilles d'aloès ; **le pot tombe en tournant** jusqu'au centre, ses ingrédients s'allument autour ; puis **le même pot** glisse dans un cercle, tenu par une main. | **Déduit** : produit détouré animé au défilement (translation, rotation, échelle), section épinglée, **le même objet traverse les sections** (transition d'élément partagé). |
| 7 | **Argon 18** (vélos) | Titre géant et vélo sur fond sombre ; **le vélo glisse et tourne** jusqu'à la fiche produit (fond clair), puis rejoint une rangée de modèles. | **Déduit** : même principe d'objet partagé (FLIP) : un seul vélo voyage de section en section. |
| 8 | **Système solaire** (concept Dribbble, 10,7 s) | La Terre se lève en bas de l'écran, ses voisines (Vénus, Mars) **dépassent des bords** ; au défilement la planète **glisse vers la droite** pendant que le titre passe à gauche ; puis **la caméra plonge dans la planète** (continents, lumières des villes) ; un clic sur une voisine la fait **venir au centre**, le titre change par un fondu flou. | **Déduit** : un seul objet qui voyage (bas → côté → gros plan dans sa matière), un **carrousel horizontal dont les voisins restent visibles aux bords** (on voit qu'il y a une suite), les textes qui s'échangent par **flou + fondu** (filter: blur). Chez nous : le produit est la planète, ses voisins de rubrique dépassent des bords, et le gros plan plonge dans sa matière (la crème, le glaçage, l'or). |

## 2. La grammaire commune : ce qui sépare 300 € de 10 000 €

1. **Le défilement change l'état du monde.** On construit la maison, on entre dans le rocher, on traverse l'arche. Jamais
   une boucle derrière des cartes.
2. **Un voyage continu de la caméra**, sans coupe : un plan finit là où commence le suivant.
3. **Le produit est le héros et il voyage** : il arrive, tourne, se pose dans la fiche, rejoint la grille. C'est le même
   objet d'une section à l'autre.
4. **La profondeur se fabrique en couches** : premier plan flou qui passe vite, produit au milieu, décor qui bouge lentement.
5. **Les passages d'un monde à l'autre** se font en traversant quelque chose : un objet, une arche, une brume.
6. **La typographie fait partie du décor** : mot géant derrière le produit, lignes qui se révèlent, masques.
7. **L'atmosphère** : brume, poussière, lumière qui balaie, vidéos d'ambiance en boucle **par-dessus** la suite d'images.
8. **La fluidité** : défilement amorti, rien ne saute.
9. **Peu de texte, au bon moment** : une phrase par étape du voyage.
10. **La fin redevient une page qui vend** : grille, prix, bouton.

## 3. Notre recette « le voyage » (pour tous les catalogues NEBULA)

1. **Le scénario du voyage** en 3 à 5 étapes tirées du métier. Exemple pour une marque de cosmétique naturelle : la
   goutte tombe → on plonge dans l'eau → on remonte à travers les racines → la plante s'ouvre → le soin apparaît.
2. **Les images clés** dans Flow (Nano Banana Pro, gratuit), une par étape, même lumière, même optique.
3. **Les plans Veo 3.1** entre deux images clés (image de début et image de fin) : **chaque plan finit sur l'image de
   début du suivant**. Mouvement de caméra imposé (avancer, traverser, s'élever), jamais caméra fixe.
4. **Montage** (ffmpeg) bout à bout, puis découpe en **150 à 240 images** : 1920 px pour l'ordinateur, plans 9:16 refaits
   pour le téléphone. Chargement progressif (une image sur quatre d'abord, puis le reste) pour la 3G de Cotonou.
5. **Le canevas fixe** qui joue la suite au défilement (`_socle/sequence.js`, à étendre aux plans enchaînés).
6. **Les couches par-dessus** : les **vrais produits détourés** du client qui voyagent (CSS 3D ou Three.js), un premier
   plan flou, une vidéo d'ambiance (brume, poussière) en mode écran, les textes qui se révèlent.
7. **La fin qui vend** : la grille, les prix, la commande sur WhatsApp.
8. **Le son** : musique douce au premier toucher, bruitages calés sur les étapes (`_socle/son.js`).

⛔ Les images générées sont le **décor et le voyage**, jamais le produit : le produit reste la vraie photo du client.
⚠️ Les crédits Veo sont comptés (environ 20 par plan rapide) : un voyage de 4 plans coûte environ 80 crédits.

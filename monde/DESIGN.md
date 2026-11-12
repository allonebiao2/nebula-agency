---
name: "LE MONDE · le salon HILLARY M. STYL"
description: "Une boutique de couture visitée en 3D au téléphone, sous une interface de verre fumé qui s'efface devant la scène."
colors:
  marque-vif: "#e6007e"
  marque-profond: "#c4006b"
  magenta-texte: "#ff8cc6"
  verre: "rgba(12, 10, 14, .46)"
  verre-fort: "rgba(12, 10, 14, .68)"
  verre-panneau: "rgba(14, 12, 16, .78)"
  verre-formulaire: "rgba(14, 12, 16, .86)"
  verre-clair: "rgba(255, 255, 255, .1)"
  filet: "rgba(255, 255, 255, .16)"
  texte: "#f6f3ee"
  texte-doux: "rgba(246, 243, 238, .74)"
  encre: "#0e0c10"
  boite-sous-titre: "rgba(0, 0, 0, .55)"
  texte-sous-titre: "#ececec"
  voix-hillary: "#ff8cc6"
  voix-afi: "#8fc3ff"
  voix-senami: "#ffc061"
  menthe: "#9be3b7"
  mur-taupe: "#4b3d37"
  plafond-expresso: "#2b2421"
  faisceau-ambre: "#ffcf96"
typography:
  display:
    fontFamily: "Bodoni Moda, Georgia, serif"
    fontSize: "clamp(1.55rem, 3.4vw, 2.1rem)"
    fontWeight: 500
    lineHeight: 1.05
    letterSpacing: "-0.005em"
  headline:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "1.05rem"
    fontWeight: 800
  title:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "1.15rem"
    fontWeight: 800
    letterSpacing: "0.01em"
  body:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "0.94rem"
    fontWeight: 400
    lineHeight: 1.45
  body-sm:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "0.88rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "0.84rem"
    fontWeight: 600
    letterSpacing: "0.01em"
  label-sm:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "0.74rem"
    fontWeight: 600
    letterSpacing: "0.01em"
  caption:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "0.7rem"
    fontWeight: 700
    letterSpacing: "0.02em"
    fontFeature: "\"tnum\""
rounded:
  sous-titre: "4px"
  vignette: "6px"
  etiquette: "8px"
  bouton: "10px"
  carte-options: "12px"
  carte: "14px"
  panneau: "16px"
spacing:
  xxs: "4px"
  xs: "8px"
  bord: "10px"
  sm: "12px"
  md: "16px"
  lg: "22px"
components:
  button-verre:
    backgroundColor: "{colors.verre}"
    textColor: "{colors.texte}"
    typography: "{typography.label}"
    rounded: "{rounded.bouton}"
    padding: "0 16px"
    height: "40px"
  button-plein:
    backgroundColor: "{colors.marque-profond}"
    textColor: "#ffffff"
    typography: "{typography.label}"
    rounded: "{rounded.bouton}"
    padding: "0 16px"
    height: "40px"
  button-plein-hover:
    backgroundColor: "{colors.marque-vif}"
  button-express:
    backgroundColor: "rgba(196, 0, 107, .2)"
    textColor: "#ffffff"
    rounded: "{rounded.bouton}"
    height: "40px"
  button-icone:
    backgroundColor: "{colors.verre}"
    textColor: "{colors.texte}"
    rounded: "{rounded.bouton}"
    size: "40px"
  etiquette-repere:
    backgroundColor: "{colors.verre-fort}"
    textColor: "{colors.texte}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.etiquette}"
    padding: "4px 9px"
  sous-titre-nom:
    backgroundColor: "rgba(0, 0, 0, .6)"
    textColor: "{colors.voix-hillary}"
    rounded: "{rounded.sous-titre}"
    padding: "4px 8px"
  sous-titre-replique:
    backgroundColor: "{colors.boite-sous-titre}"
    textColor: "{colors.texte-sous-titre}"
    typography: "{typography.body}"
    rounded: "{rounded.sous-titre}"
    padding: "4px 10px 5px"
  reponse-croix:
    backgroundColor: "rgba(0, 0, 0, .5)"
    textColor: "#ffffff"
    typography: "{typography.label}"
    rounded: "{rounded.etiquette}"
    padding: "6px 12px"
  reponse-croix-hover:
    backgroundColor: "rgba(196, 0, 107, .92)"
  carte-options:
    backgroundColor: "{colors.verre-fort}"
    textColor: "{colors.texte}"
    rounded: "{rounded.carte-options}"
    padding: "8px"
  fiche-piece:
    backgroundColor: "{colors.verre-panneau}"
    textColor: "{colors.texte}"
    rounded: "{rounded.panneau}"
    padding: "22px 22px 20px"
  champ-commande:
    backgroundColor: "rgba(255, 255, 255, .08)"
    textColor: "{colors.texte}"
    rounded: "{rounded.bouton}"
---

# Design System: LE MONDE · le salon HILLARY M. STYL

## Overview

**Creative North Star: "Le verre fumé devant la vitrine"**

La scène est le produit ; l'interface n'est qu'une vitre posée devant. Le visiteur se tient dans un salon de couture tamisé (murs taupe expresso, plafond plus sombre, un halo ambré sous la coupole, un faisceau chaud par création) et tout ce qui lui parle flotte par-dessus en petits morceaux de verre fumé translucide, flous à 12 px, cernés d'un filet blanc à 16 %. Rien ne remplit l'écran, rien ne cache durablement une robe. Les conversations suivent la grammaire de Call of Duty : la réplique en sous-titre dans des boîtes noires translucides, le nom de la personne dans sa couleur, les réponses en croix au centre sur un voile léger.

Le système est petit, plat et dense en sens plutôt qu'en surface. Un seul accent, le magenta H.M.S d'Hillary ; une seule famille pour toute l'interface, Archivo ; la Bodoni de la maison réservée au nom des créations, là où l'on parle couture. Les boutons sont plats, à 40 px de cible, sans relief ni dégradé. La profondeur vient du flou et de la translucidité, pas des ombres, sauf pour les trois panneaux qui s'ouvrent au-dessus de la scène.

Rejet confirmé par le propriétaire : la direction « enseignes peintes » (panneaux décorés dans le décor, gros boutons de jeu) a été construite puis refusée comme ringarde et peu professionnelle. Le verre fumé discret est sa préférence durable ; c'est une contrainte du système, pas une étape de son histoire.

**Key Characteristics:**
- La scène d'abord : verre translucide, jamais d'aplat opaque qui cache.
- Petit et plat : boutons de 40 px, rayons de 4 à 16 px, aucune ombre au repos.
- Un seul accent, le magenta H.M.S, profond sous le texte, clair en texte sur verre.
- Archivo partout, Bodoni Moda pour le seul nom des créations.
- Conversations en sous-titres et réponses en croix, comme dans Call of Duty.
- L'interface se retire d'elle-même : objectif replié, un seul « Partir », HUD absent avant « Entrer ».

## Colors

Une nuit de verre fumé chaud sur un salon taupe, traversée d'un seul magenta.

### Primary
- **Magenta H.M.S profond** (`marque-profond`): le magenta qui porte du texte blanc. Fond des boutons pleins (à 90 % d'opacité), de la réponse ou de l'étiquette survolée (à 92 %), du sac rempli (à 85 %), de l'annulation d'un toast ; teinte du bouton express (à 20 %, bordé de magenta clair à 55 %) et de la case express de la fiche (à 32 %).
- **Magenta H.M.S vif** (`marque-vif`): la couleur de marque d'Hillary, dans son état de survol et dans les éléments sans texte : la barre de chargement d'« Entrer », la jauge du carnet, la pastille du sac, le point d'une création, la sélection et le caret.
- **Magenta clair sur verre** (`magenta-texte`): le magenta lorsqu'il EST le texte, sur fond sombre : titre court de l'objectif, genre d'une pièce, intertitres et total de la commande, astérisque des champs requis, point « nouvelle réponse », bordure des puces.

### Neutral
- **Verre fumé** (`verre`): boutons, carte d'arrivée, HUD, objectif. Toujours accompagné du flou et du filet.
- **Verre fort** (`verre-fort`): ce qui doit se lire sur n'importe quel morceau de scène : étiquettes de repère, noms au-dessus des personnes, carte d'options, toast, mention « maquette ».
- **Verre de panneau** (`verre-panneau`) et **verre de formulaire** (`verre-formulaire`): la fiche d'une pièce, le sac et le carnet (à 80 %), puis le cadran de commande, le plus opaque parce qu'on y écrit.
- **Verre clair** (`verre-clair`): surfaces internes d'un panneau (options, cases de la fiche, choix de la commande).
- **Filet** (`filet`): la bordure de 1 px de tout morceau de verre.
- **Crème** (`texte`) et **crème douce** (`texte-doux`): le texte et le texte secondaire ; le blanc pur est réservé aux titres et aux chiffres.
- **Encre** (`encre`): texte sur la pastille claire du carnet.
- **Boîte de sous-titre** (`boite-sous-titre`) et **texte de sous-titre** (`texte-sous-titre`): les répliques, à la manière d'un film sous-titré ; la boîte du nom monte à 60 %.

### Voix et repères
- **Couleur par personne** : chaque personne parle sous son nom dans sa couleur, posée par la donnée (`--c`) : Hillary en magenta clair (`voix-hillary`), Afi en bleu ciel (`voix-afi`), Sènami en ambre (`voix-senami`), Maman Sènami en menthe (`menthe`).
- **Repères** : un point magenta vif pour une création, ambre pour une personne, menthe pour une porte. La menthe dit aussi « fait » (objectif terminé, carnet complet, réponse déjà donnée).

### La scène sous le verre
- **Mur taupe expresso** (`mur-taupe`), **plafond expresso** (`plafond-expresso`), **faisceau ambré** (`faisceau-ambre`) : ce ne sont pas des couleurs d'interface, mais le fond sur lequel le verre est calibré. Le verre fumé à 46 % y reste lisible parce que le salon est tamisé ; un lieu clair devrait remonter vers le verre fort.

### Named Rules
**The Deep Magenta Under Text Rule.** Tout magenta qui porte du texte est le magenta profond ; le magenta vif ne passe sous du petit texte qu'au survol d'un bouton déjà lu. Le vif sous du texte blanc de 11 à 14 px échoue au contraste.

**The One Accent Rule.** Le magenta H.M.S est le seul accent. Les couleurs de voix et de repères désignent quelqu'un ou quelque chose ; elles ne décorent jamais une surface.

## Typography

**Display Font:** Bodoni Moda (avec Georgia, serif), auto-hébergée dans `polices/`
**Body Font:** Archivo (avec system-ui, sans-serif), auto-hébergée, toute l'interface
**Label Font:** Archivo

**Character:** Une grotesque nette et légèrement large pour tout ce qui sert, et la didone de la maison pour ce qui se porte. La Bodoni n'apparaît que lorsque l'on nomme une création ; elle dit « couture » précisément parce qu'elle est rare.

### Hierarchy
- **Display** (Bodoni Moda 500, clamp(1.55rem, 3.4vw, 2.1rem), 1.05) : le nom d'une création en tête de sa fiche ; en 1rem dans une ligne du sac.
- **Headline** (Archivo 800, 1.05rem) : titres du sac, du carnet et de la commande.
- **Title** (Archivo 800, 1.15rem) : la carte de titre du lieu, posée sans boîte avec une ombre de texte ; total de la commande.
- **Body** (Archivo 400, 0.94rem, 1.45, 46ch au plus) : la réplique d'un dialogue ; 0.86rem pour les sous-titres d'ambiance, 0.9rem au téléphone.
- **Body small** (Archivo 400, 0.88rem, 1.5) : la description d'une pièce, le texte des panneaux.
- **Label** (Archivo 600, 0.84rem, 0.01em) : boutons, réponses, options, invites. Casse de phrase, jamais de capitales espacées.
- **Label small** (Archivo 600, 0.74rem) : étiquettes de repère, heure, sous-libellés.
- **Caption** (Archivo 700, 0.7rem, chiffres tabulaires) : pastilles de compte, titre court de l'objectif, intitulés des cases de la fiche.

Manrope est chargée par la page mais aucune règle d'interface ne s'en sert : Archivo l'a remplacée dans le verre.

### Named Rules
**The Bodoni Is For The Piece Rule.** La Bodoni Moda nomme une création, et rien d'autre : ni bouton, ni titre de panneau, ni marque.

**The Legibility Floor Rule.** Un texte fonctionnel (étiquette, compte, libellé) ne descend pas sous 11 px ; une phrase qu'on lit ne descend pas sous 12,5 px. Les chiffres qui se comparent (prix, délais, totaux) sont tabulaires.

## Layout

L'écran est la scène ; l'interface s'accroche à ses bords et au bas du centre. Le HUD tient en haut, à 10 px des bords et sous la zone sûre (`env(safe-area-inset-top)`) : à gauche le logo dans sa vignette de verre, puis l'heure en texte nu, à droite le son ; sous lui, à gauche l'objectif, à droite la colonne du sac puis du carnet (pas de 48 px puis 60 px). Les sous-titres partent de 36 % de la largeur jusqu'à 6 % du bord droit, à 11 % du bas ; au téléphone (560 px et moins) ils occupent toute la largeur à 10 à 12 px des bords et montent au-dessus de la mention « maquette ». Les réponses forment une croix de trois rangées autour d'un losange, centrée à 46 % de la hauteur (44 % au téléphone), dans 560 px au plus.

Les panneaux (fiche, commande) sont centrés en ordinateur ; à 720 px et moins pour la fiche, 560 px et moins pour la commande, ils deviennent des feuilles collées en bas, arrondies en haut seulement, la fiche plafonnée à 78 % de la hauteur pour que la scène reste visible au-dessus.

Rythme d'espacement : 4 px entre une boîte de nom et sa réplique, 8 px de gouttière courante, 10 px de marge d'écran, 12 et 16 px à l'intérieur des cartes, 22 px de marge de fiche (14 px au téléphone).

Une étiquette de repère reste à droite de son point et ne passe à gauche que si elle sortirait de l'écran à droite tout en tenant à gauche ; les étiquettes au sol sont centrées sur leur point puis bornées à 8 px des bords.

### Named Rules
**The Nothing Fills The Screen Rule.** L'objectif se replie en une ligne au bout de 6 s et se rouvre au toucher ; un seul « Partir » est visible à la fois (celui du dialogue s'efface sous une fiche ou la commande) ; la mention « maquette » s'efface sous une carte d'options, une fiche ou la commande ; tant que la carte « Entrer » est là, le HUD, le sac, le carnet, l'objectif et tous les repères sont invisibles et intouchables.

## Elevation & Depth

La profondeur est une affaire de verre : translucidité, flou d'arrière-plan à 12 px saturé à 1,2, filet blanc. Au repos, aucun bouton, étiquette ni carte d'options ne porte d'ombre portée. Seuls les panneaux qui recouvrent la scène (fiche, sac et carnet, commande) prennent une ombre large et douce qui les décolle, et un voile sombre léger tombe derrière eux (28 % sous la fiche, 40 % sous la commande, 16 % sous les réponses en croix). Le texte posé à même la scène, sans boîte (heure, carte de titre, aide d'arrivée), tient par une ombre de texte serrée.

### Shadow Vocabulary
- **Panneau fiche** (`box-shadow: 0 24px 60px rgba(0,0,0,.45)`) : la fiche d'une pièce.
- **Panneau latéral** (`box-shadow: 0 20px 50px rgba(0,0,0,.45)`) : le sac et le carnet.
- **Panneau commande** (`box-shadow: 0 30px 70px rgba(0,0,0,.5)`) : le cadran, le plus haut.
- **Point de repère** (`box-shadow: 0 1px 4px rgba(0,0,0,.6)`) : le point d'une création, d'une personne, d'une porte.
- **Texte nu** (`text-shadow: 0 1px 3px rgba(0,0,0,.8)`) : tout texte sans boîte sur la scène.

### Named Rules
**The Glass Not Paint Rule.** Une surface d'interface est du verre (fond translucide, flou, filet), jamais un aplat opaque ni un décor peint. Aucune animation infinie ne tourne sous un flou d'arrière-plan.

## Shapes

Des rectangles doucement arrondis, sans pilule ni cercle : 4 px pour les boîtes de sous-titres (le registre du film), 6 px pour les vignettes et pastilles, 8 px pour les étiquettes, réponses et options, 10 px pour les boutons et le HUD, 12 px pour la carte d'options, 14 px pour la carte d'arrivée et le sac, 16 px pour la fiche et la commande. Les pastilles de compte sont les seules formes rondes (18 px), avec les points de repère. Le losange de la croix est un carré de 14 px tourné, au trait blanc de 1,5 px, sans remplissage.

Les icônes sont dessinées en SVG, trait `currentColor` à 1,8, extrémités arrondies, 18 à 19 px dans un bouton de 40 px, 14 px dans une ligne du sac. Les signes d'état sont dessinés en CSS (coche menthe en équerre, point magenta), jamais tirés d'un caractère.

## Components

### Buttons
Plats, petits, en verre ; ils se lisent sans se faire remarquer.
- **Shape:** rectangle doux (10 px), 40 px de haut au moins, 16 px de marge latérale (22 px pour « Entrer »).
- **Verre (défaut):** fond de verre fumé, flou, filet, texte crème en label Archivo 600.
- **Plein:** magenta profond à 90 % ; survol en magenta vif. Une seule action pleine par vue : « Entrer », « Je la prends ».
- **Express:** verre teinté de magenta profond à 20 %, bordé de magenta clair à 55 % ; survol à 32 %.
- **Ligne:** transparent, filet en bordure ; « Une autre », « Retour ».
- **Icône:** carré de verre de 40 px (son, sac, carnet), icône SVG au trait 1,8 ; le sac rempli passe en magenta profond et sa pastille en blanc. La pastille du sac n'apparaît que s'il contient quelque chose.
- **États:** focus visible par un contour blanc de 2 px décalé de 2 px ; pression à 97 % d'échelle ; inactif à 55 % d'opacité.

### Repères et étiquettes
- **Point:** 14 px, bord blanc de 2 px, rempli de la couleur du type (création, personne, porte). Immobile.
- **Étiquette:** verre fort, label small, 8 px de rayon, apparue seulement pour les repères proches ; magenta profond à 92 % au survol.
- **Étiquette au sol:** même verre, 8 px de rayon, un trait vertical de 8 px qui la relie à son point.
- **Nom au-dessus d'une personne:** verre fort, 6 px, texte dans la couleur de sa voix.

### Sous-titres et conversation
La signature du système, empruntée à Call of Duty.
- **Ligne:** le nom dans sa propre boîte noire à 60 %, en Archivo 700 et dans la couleur de la personne, puis la réplique dans une boîte noire à 55 %, 4 px d'écart, rayons de 4 px. Pas de panneau, pas de cadre, pas de « suite » clignotante ; toucher n'importe où fait avancer.
- **Réponses en croix:** quatre boutons noirs à 50 % au filet blanc à 18 %, 8 px de rayon, texte équilibré, autour d'un losange ; un voile de 16 % tombe sur la scène. Survol ou focus en magenta profond. Une réponse neuve porte un point magenta clair de 6 px dans son coin ; une réponse déjà donnée passe à 70 % avec une coche menthe.
- **Partir:** un petit bouton de verre en haut à droite, un seul à la fois.

### Carte d'options
Une petite carte de verre fort près d'une personne : 168 px de large au moins, 8 px de marge, 12 px de rayon. Les options sont des lignes de 40 px en verre clair ; l'option principale est en magenta profond. Elle se pose en 0,25 s depuis 6 px plus bas et 98 % d'échelle, sans rebond.

### Fiche d'une pièce
- **Corner Style:** 16 px (feuille arrondie en haut seulement au téléphone).
- **Background:** verre de panneau, flou, filet ; la photo de la pièce sur un verre blanc à 6 %.
- **Shadow Strategy:** ombre « panneau fiche ».
- **Contenu:** le nom en Bodoni, le genre en magenta clair, la description en body small, quatre cases de verre clair (prix, délai, express teinté de magenta, mesures) aux chiffres tabulaires, puis une seule action pleine.
- **Internal Padding:** 22 px (14 px au téléphone, plus la zone sûre du bas).

### Inputs / Fields
- **Style:** verre blanc à 8 %, bordure blanche à 22 %, 10 px de rayon, texte crème, indication à 55 %.
- **Libellés:** en casse de phrase, 0.78rem ; un champ requis porte une astérisque magenta clair sur la même ligne, jamais le mot « obligatoire » répété.
- **Puces:** transparentes, bordées de magenta clair à 50 %, texte magenta clair.

### Navigation
- **HUD:** la marque H.M.S dans une vignette de verre de 4 px de marge, l'heure en texte nu avec ombre (le lieu et la météo masqués à 560 px et moins), le son en carré de verre. Absent tant qu'on n'est pas entré.
- **Objectif:** carte de verre en haut à gauche, titre court en magenta clair (menthe une fois fini), repliée en une ligne au bout de 6 s.

### Carte d'arrivée
Dehors, devant l'enseigne éclairée : une seule petite carte de verre de 14 px de rayon en bas de l'écran, avec le nom de la maison et sa ligne en Archivo, le bouton plein « Entrer » et une barre de chargement magenta de 2 px collée à son bord bas ; une aide en texte nu dessous. La rue et la façade restent visibles. Elle s'efface en 0,6 s.

## Do's and Don'ts

### Do:
- **Do** poser toute surface d'interface en verre fumé (de `rgba(12,10,14,.46)` à `rgba(14,12,16,.86)` selon ce qu'elle doit couvrir), floutée à 12 px, cernée d'un filet blanc à 16 %.
- **Do** mettre le magenta profond `#c4006b` sous tout texte magenta et le magenta clair `#ff8cc6` quand le magenta est le texte lui-même.
- **Do** garder chaque cible tactile à 40 px au moins.
- **Do** tenir le texte fonctionnel à 11 px au moins et le texte de phrase à 12,5 px au moins.
- **Do** dessiner chaque icône en SVG au trait de 1,8, extrémités arrondies, en `currentColor`.
- **Do** replier l'objectif en une ligne au bout de 6 s, montrer un seul « Partir » à la fois et cacher HUD, sac, carnet, objectif et repères jusqu'à « Entrer ».
- **Do** faire passer une étiquette à gauche de son point seulement si elle déborderait à droite, et borner les étiquettes au sol à 8 px des bords.
- **Do** écrire chaque réplique en sous-titre, nom et phrase dans deux boîtes noires translucides, le nom dans la couleur de la personne.
- **Do** réserver la Bodoni Moda au nom des créations.
- **Do** honorer `prefers-reduced-motion` : apparitions sans transition.

### Don't:
- **Don't** poser de panneau plein, d'enseigne peinte ni de décor d'interface dans la scène : la direction « enseignes peintes » a été refusée par le propriétaire.
- **Don't** fabriquer de gros boutons de jeu, de pilules ou de dégradés : boutons plats, 10 px de rayon.
- **Don't** mettre le magenta vif `#e6007e` sous du petit texte blanc.
- **Don't** faire pulser ou clignoter un point, un repère ou un indicateur décoratif, ni faire tourner une animation infinie sous un flou.
- **Don't** dresser de colonnes de lumière au sol pour marquer un lieu.
- **Don't** utiliser un caractère comme icône (croix, flèche, coche, étoile tapées) : dessiner l'icône.
- **Don't** écrire en capitales espacées : toute l'interface est en casse de phrase.
- **Don't** ajouter un second accent de couleur ; les couleurs de voix et de repères ne remplissent jamais une surface.

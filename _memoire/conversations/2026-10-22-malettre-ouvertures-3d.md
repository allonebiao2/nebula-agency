# 2026-10-22 · MA LETTRE À… : les ouvertures en 3D, une par occasion (le chantier, vague 1 et moteur « cinéma »)

Suite de `2026-10-22-malettre-video-minuit.md` (le film), le même après-midi.

## Ce que Mongazi a demandé

- Le matin (08 h 47) : « chaque événement doit avoir son animation spéciale […] les animations que je vois actuellement
  ne sont pas si impressionnantes […] utilise les animations des vidéos que je t'ai envoyées dans le dossier ma lettre,
  UTILISE-LES TOUTES ET EN PLUS INSPIRE-TOI D'elles […] tu peux utiliser Remotion aussi […] mais avant ça tu dois faire
  la vidéo ».
- Après le film (« j'aime pas à 100 % mais bon c'est pas mal ») : « les animations maintenant pour chaque événement et
  la possibilité au client de choisir certaines animations, certaines peuvent être plus chères ; les animations doivent
  être immersives et en 3D, bien faites ; inspire-toi des vidéos ; utilise Blender et Remotion ; invoque les skills ».
- Skill chargé : `impeccable` (volet animation, registre « brand », PRODUCT.md de `malettre/`).

## Les onze vidéos de référence (`_partage/ma lettre/*.mp4`), lues image par image

Portes brodées tenues par un sceau d'or (3964bcf0), collier de perles autour d'une longue enveloppe dont les quatre
rabats s'ouvrent (971ee54d), monogramme qui se grave en or (4c46da1e), cadres de dentelle et compte « counting down to
forever » (3a06fe10), télé rétro et collage (timbres, billet à code-barres, alliances) (8ab65a27), rabats festonnés
gaufrés (0d136ce0), gratter pour révéler la date (0e910abc), calligraphie de lumière (d69edd61), noir et blanc en
dentelle (a5b8b505), enveloppe bordeaux et sceau à la colombe (c83bac02). La correspondance occasion par occasion est
dans `malettre/RITES.md` (28 ouvertures).

## Ce qui est construit (vague 1, commit `6feea09`, rien de déployé)

- **Le théâtre** `malettre/rites/moteur.js` : un moteur 3D WebGL 1 écrit pour la lettre, AUCUNE bibliothèque. Tout
  bouge par le temps (le même rite se photographie à n'importe quel instant, et pourra se filmer dans Remotion).
- **L'atelier** `rites/atelier.js` : la table, l'enveloppe aux couleurs de l'habillage (papier, cire, doublure damassée,
  carte « Ma lettre à <prénom> »), le cachet de cire (sceau en relief par bosselage, éclats PLEINS extrudés), les pluies
  3D, les sons (les fonctions de la lettre : `audio`, `bruit`, `sonOuverture`).
- **Le branchement** `rites/branchement.js` : glisse le canvas sous les mots du seuil, cadre l'enveloppe 3D exactement
  où était celle en CSS (qui reste invisible pour la mise en page et le doigt), éteint la cire avant l'heure, prend le
  mot du bouton du rite (« Souffler la bougie »), et RETOMBE sur l'ouverture d'avant sans WebGL, en mouvement réduit,
  dans l'aperçu du constructeur ou à la moindre erreur.
- **Quatre ouvertures** : `cachet` (toutes les occasions en attendant la leur), `perles` (mariage), `portes`
  (Saint-Valentin), `bougie` (anniversaire). Photographiées par `_voir.py`, essayées dans de vraies lettres
  (`_lettre_essai.py`, `_demo.py` sur http://localhost:8765/).
- **Les matières viennent de Blender** : `rites/_matieres_blender.py` (Cycles sur le processeur, EEVEE plante ici)
  rend douze « matcaps » de 256 px (cinq cires, or poli et brossé, argent, perle irisée par film mince, deux velours,
  papier) sous la lumière « interior » (Poly Haven, CC0, livrée avec Blender) : un vrai rendu, lu par la lettre pour
  le prix d'une texture. Environ 60 s la matière, Blender compris.
- **La lettre** (`lettre.html`) : un marqueur `/*MALETTRE_RITE*/null/*FIN_MALETTRE_RITE*/` et un aiguillage dans
  `ouvrir()` (la 3D si elle est là, sinon l'ouverture d'avant). 61 323 octets (seuil 61 440). Contrôle `_qc.py` : 284
  verts. `gabarit.ts` régénéré.
- **La construction** `malettre/_rites.py` : minifie par esbuild (celui du studio vidéo), réduit les matières en WebP,
  écrit `malettre/rites.js` (constructeur) et `supabase/functions/_shared/rites.ts` (serveur) avec la même fonction
  `poserRite(html, id, cire)`. ⛔ Le rite vient de nos fichiers, jamais du navigateur ; identifiant inconnu → `cachet`.

## Le retour de Mongazi sur la démonstration, et la réponse

- « Plus spectaculaire » ET « la qualité et le rendu doivent être meilleurs : actuellement c'est pixelisé, ça doit être
  FLUIDE AUSSI ; on dirait la qualité des jeux de la console Sega au lieu de la qualité des jeux de la PS5, avec plus de
  détail ».
- Causes trouvées : un rendu direct sans lissage, des textures trop petites agrandies (la carte en 512 px plein écran,
  les matières), aucun halo ni profondeur de champ, et l'animation de repos bridée à 30 images par seconde.
- **Le moteur « cinéma »** (en cours) : image calculée hors écran (sur-échantillonnée 1,5 fois sur un écran
  d'ordinateur), lissage FXAA, halo (« bloom »), profondeur de champ, vignetage, grain, courbe de couleur, reflet doux
  sur le papier, le rabat qui se COURBE dans le nuanceur (il se soulève et s'enroule comme du papier), textures de
  papier et de carte en 1024 px, filtrage anisotrope, 60 images par seconde et baisse automatique de qualité par
  paliers si l'appareil peine. Première planche : plus cinématographique ; deux défauts à corriger (halo trop fort,
  précision de profondeur à 16 bits hors écran qui laisse transparaître la doublure).

## Décisions de Mongazi

- **Les prix des ouvertures** : « Incluse + grandes à +1 000 F ». L'ouverture de son occasion est incluse dans TOUTES
  les offres (même La Carte, c'est elle qui fait parler) ; on peut en choisir une autre : les simples incluses, les
  « grandes » (perles, portes, bougie…) à +1 000 F. ⛔ Le prix se calcule au serveur, comme celui des paliers.
- **À traiter plus tard** : « lors de la création, des gens peuvent faire une capture d'écran de la création et aller
  l'envoyer, donc trouver une solution plus tard pour contrer cela ». Pistes, rien de tranché : filigrane « Aperçu »,
  texte flouté au-delà des premières lignes, ouverture 3D et lettre complète seulement au lien payé.

## Pièges rencontrés

- ⛔ **Un minifieur efface une expression seule** (code mort) : le rite sortait vide (0 octet). On l'affecte
  (`var __RITE__=…`), puis on retire l'affectation.
- ⛔ **`node -e` avec 50 Ko de script dépasse la longueur d'une commande sous Windows** (`WinError 206`) : passer par
  un fichier.
- ⚠️ **Un polygone creux triangulé depuis son centre recouvre son échancrure** : la poche de l'enveloppe (en V) se
  dessinait sur le V. Deux moitiés convexes.
- ⚠️ **Le bouton du son est en position absolue** : la règle `#seuil>*{position:relative}` l'aurait arraché de son coin.
- ⚠️ Des quads dressés, vus d'en haut, ressemblent à des aiguilles : pétales et confettis sont couchés.
- ⚠️ Un relief (bosselage) sur des traits fins d'un canvas les noircit : la broderie des portes est sans relief.
- ⚠️ Une profondeur à 16 bits (le seul format simple d'un rendu hors écran en WebGL 1) ne sépare plus deux feuilles
  à 2 mm : prendre `DEPTH_STENCIL` (24 bits) et reculer le plan proche.
- ⚠️ Le rendu logiciel du navigateur de contrôle (SwiftShader) est lent : les captures « en temps réel » sautent ;
  pour regarder, `_voir.py` peint chaque instant (`figer(t)`).

## La suite

1. Finir le moteur « cinéma » (halo, profondeur), le regarder, puis le montrer à Mongazi (http://localhost:8765/).
2. Plus spectaculaire : caméras plus mobiles, plus de lumière et de particules, durées un peu plus longues.
3. Les 24 autres ouvertures (`RITES.md`), le choix dans le constructeur, le prix au serveur et à la caisse, le
   branchement de `poserRite` dans `malettre-lettre`, les contrôles, puis la publication (avec le feu vert de Mongazi).
4. Remotion : filmer chaque ouverture (le même code) pour la vitrine et les statuts.

## La suite, le même soir : « au moins 3 à 5 par événement », l'écran entier comme une porte, le texte qui s'écrit

Après la démonstration du moteur « cinéma », Mongazi : « j'aime mieux ». Puis : au moins 3 à 5 animations
différentes pour chaque événement, adaptées à l'événement ; « comme dans une ou deux vidéos, l'écran entier du
téléphone doit s'ouvrir comme une porte en 3D, de façon immersive » ; « le texte aussi doit être animé et venir
s'écrire lentement » ; « faire durer » (c'est l'expérience qui impressionne celle qui reçoit) ; « ultra interactif,
encore plus d'effet wow ». À la question « plusieurs ouvertures au choix, ou une seule qui dure ? » : **« Les deux »**.

### Ce qui est construit (commits `05fb31a` à `dc0f8e6`, rien de déployé)

- **La lettre qui s'écrit** (`rites/ecriture.js`, `05fb31a`) : après l'ouverture (3D, ou celle d'avant sans WebGL), la
  lettre s'écrit dans l'ordre de la page ; le titre lettre à lettre, l'encre couleur de cire qui sèche couleur d'encre,
  le texte au rythme d'une main, une plume d'or qui suit et gratte, la page qui défile ; puis la phrase à gratter, les
  photos une à une, les jours qui roulent, la formule, le nom, le trait, la pluie de l'habillage en final. Un toucher
  accélère, un second écrit tout ; relue, quatre fois plus vite ; 40 s de texte au plus (70 s pour une lettre fleuve).
- **Six mécaniques plein écran ou à geste**, chacune habillée de thèmes (`rites/carte.json`) :
  - **les portes** (`battants.js`) : deux battants gaufrés couvrent l'écran, un cachet les tient ; on touche, on les
    écarte du doigt, elles s'ouvrent vers soi SUR LA VRAIE LETTRE ; dentelle, velours capitonné, moucharabieh éclairé
    par une lanterne, Art déco ;
  - **le rideau** (`rideau.js`) : « les trois coups » du brigadier, le rideau s'ouvre à l'italienne, la salle
    applaudit ; théâtre, soie, minuit ;
  - **le feu d'artifice** (`feu.js`) : on touche le ciel, une fusée part vers le doigt ; le bouquet final ÉCRIT LE
    PRÉNOM en étincelles (dans un cœur pour l'amour) ; fête, or, cœur ;
  - **les lanternes** (`lanterne.js`) : garder le doigt sur la lanterne, elle s'allume et s'envole, des dizaines
    d'autres montent de la rive ; papier, sous la lune (Ramadan, Tabaski) ;
  - **la lettre pliée** (`pli.js`) : le cachet se décolle, un toucher par rabat, la feuille devient la lettre ; lin,
    noyer ;
  - et les quatre d'avant (cachet, perles, petit cabinet brodé, bougie).
- **18 ouvertures, chacune des 28 occasions en a au moins trois** (la première est la sienne). Sobriété gardée : excuse,
  rupture et brouille n'ont ni feu ni rideau.
- **Le moteur** : fenêtre transparente (les portes s'ouvrent sur la page), feuille d'or (masque de métal), reflet de la
  lumière ponctuelle qui se déplace, étoffe qui bouge (`S.maj`), rites qui décident eux-mêmes (`revele(t)`, `fini(t)`),
  le doigt passé au rite (`toucher`), une phrase d'aide que le rite change en route (`dire`, `taire`).
- **Les sons propres d'un rite vivent dans son fichier** : une lettre au cachet n'emporte pas les fusées (le commun
  redescend à 48,9 Ko).
- **Le banc du geste** (`rites/_geste_essai.py`) vérifie le GESTE de chaque mécanique (portes, rideau, feu, lanterne,
  pli), sur le banc et dans une vraie lettre ; la démonstration (`_demo.py`) sert quatorze vraies lettres, toutes vertes.

### Pièges de la soirée (et leur parade)

- ⛔ **Le contrôle disait « ouverte, portes devant la lettre » alors que les portes s'étaient ouvertes SEULES** (le
  repli automatique de 6,5 s) : SwiftShader met une demi-seconde par image, le geste arrivait après. Parade : un banc
  qui repousse l'automatique (`auto=99`, `window.__malettreAuto`) ; si ça s'ouvre, c'est le doigt.
- ⛔ **Glisser avant d'avoir touché le cachet ne faisait rien** (un glissé n'est pas un clic) : plus de 24 px avant le
  cachet comptent pour le toucher, et le même doigt prend les battants.
- ⛔ **La courbe de couleur repliait le rouge au-delà de 1** (la lanterne allumée virait au VERT) : bornée avant.
- Papier chaud × lumière chaude × ambiance chaude = brun : la lumière se multiplie, un papier clair veut une lumière
  presque blanche.
- Un tirage au hasard CONDITIONNEL dans une boucle de particules décale toutes les suivantes d'une image à l'autre.
- Une chaleur intégrée image par image (pas borné à 0,05 s) ralentit sur un téléphone lent : la calculer sur le temps
  réel du doigt.
- Un reflet est SOUS l'eau : l'eau opaque le cachait par la profondeur.

### Ce qui reste

1. Le choix de l'ouverture dans le constructeur (avec son prix), `poserRite` dans `malettre-lettre`, la validation au
   serveur (l'ouverture doit appartenir à l'occasion), le prix des « grandes » à la caisse, les contrôles.
2. La publication, avec le feu vert de Mongazi.
3. Les films Remotion des ouvertures (le même code) pour la vitrine.
4. ⏳ La capture d'écran de l'aperçu (plus tard).


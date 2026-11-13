# 2026-11-13 · LE MONDE, l'audit d'un expert en jeu vidéo, vague par vague

> Suite de `2026-11-12-monde-salon-hillary.md`. Le point de reprise exact est
> **`monde/REPRENDRE-ICI.md`** (réécrit ce matin « à la lettre près », à la demande de Mongazi).

## Ce qu'il a demandé (ses mots)

1. « hormis la relecture d'Impeccable, quand tu analyses en profondeur, mets-toi dans la peau d'un
   expert en animation 3D et en création de jeu vidéo : qu'est-ce qui peut encore être optimisé et
   apporté à ce niveau ? » → `monde/AUDIT-JEU-VIDEO.md` (`25ef0cd`).
2. « enchaîne donc chacun jusqu'au dernier… chacun doit être à 100 % ; tu as champ libre » puis
   « fais-les par vagues… ne passe pas à une autre tant que celle sur laquelle tu es n'est pas à 100 % ».
3. « OUI JE LES ENVOIE D'ici là » (les photos d'Hillary).
4. « en attendant tu peux enchaîner avec le prochain ; je pense qu'il faut que je génère en 3D les
   autres persos… laisse-moi les prompts » → `personnages/CONSIGNES.md` (`6a07d12`).
5. « pour chacun des prompts, donne-moi des prompts pour animer les images générées » →
   `personnages/CONSIGNES.md` (`5e9a19d`).
6. « mets tout en mémoire à la lettre près ainsi que tout ce qui reste à faire, comme ça quand je fais
   clear et je démarre une nouvelle discussion tu puisses te repérer à la lettre près ».

## Ce qui a été fait

- ✅ **Vague 1, l'ouverture cinéma** (`bcfc59e`) : filmée de nuit et de jour.
- 🟡 **Vague 2, des personnages qui vivent** (`b271315`) : Afi a 13 animations et vit (variantes,
  démarrage et arrêt, pieds au pivot, regard). Sènami, Maman et Hillary attendent leurs modèles.
- ✅ **Vague 3, la mise en scène des conversations** (`f7d60aa`) : cadrage par la distance et la
  largeur d'écran, profondeur de champ (qualité haute), caméra qui suit la tête à chaque image,
  souffle de caméra, oratrice à 1,30 m, les autres écartées de la ligne de regard, lumière de face
  douce. Deux défauts trouvés en regardant les captures et corrigés : le flou d'un podium qui bavait
  sur Afi (flou plafonné), la tête d'Afi coupée à l'ordinateur (tangage −0,47 au lieu de −0,20, une
  orientation tardive ; d'où le suivi à chaque image). QC 52/52.
- Les scripts de capture, qui vivaient dans le dossier temporaire de la session, sont rangés dans
  `monde/_outils/captures/` (avec un `LISEZMOI.md`), plus `generer_visiteuses.py` et
  `design_sidecar.py` dans `monde/_outils/`.
- Vérifié : Epic et Unreal ont bien disparu du disque (7,2 Go rendus le 2026-11-12 ; `C:` à 43 Go
  libres ce matin).
- Constaté : les images de Sènami et de Maman aux **bons âges n'ont jamais été générées** (le quota
  Cloudflare était épuisé ; le dossier de sortie est vide). Celles du dépôt sont les anciennes, aux âges
  faux : à ne pas utiliser.

## La suite

**La vague 4, la chaîne d'assets pour la 3G**, avec son plan pas à pas dans `REPRENDRE-ICI.md`,
section 4 (mesurer d'abord). Puis la 5 (lumière cuite dans Blender). Toute la liste de ce qui reste,
à moi, à Mongazi et à Hillary : `REPRENDRE-ICI.md`, section 5.

## Suite (même jour) : le réalisme, Hillary, et deux idées gardées

- Mongazi : « le salon doit être virtuel mais le plus réaliste possible » → `monde/REALISME.md` (R1-R15), puis
  « concentre-toi sur ce que tu peux faire toi… un à la fois… à 200 %… regarde avec Chrome ».
- ✅ R1 la lumière cuite dans Blender, ✅ R2 les ombres de contact ; R6 (le sol qui reflète au téléphone)
  planifié en détail dans `monde/REPRENDRE-ICI.md` § 4.
- ✅ Site d'Hillary : mesures de la jupe (ses mots), « haut + jupe » réparé, publié.
- Gardés en mémoire : la consigne d'Afi (il la régénère), le commercial NEBULA (`monde/COMMERCIAL.md`), un teaser
  vidéo par boutique (`monde/TEASERS.md`).

## Suite (après-midi) : ses assets, puis « intègre »

- Mongazi dépose 24 fichiers en vrac dans `hillary\` : **rangés et analysés** (`monde/ARRIVEES.md`) : nouvelle
  Afi (29 ans), Sènami (21), Maman (47), Hillary en pose A ; 9 vidéos (parler, marcher, écouter, tourner) ;
  planches h1 et h2 (fidèles, défauts notés) + une pièce **absente de son catalogue** ; 8 vues du salon.
  Dossier `_partage/immersive  store 3D/` **exclu de git en entier**.
- Il dit ne pas arriver à rendre ses images cohérentes : **la 3D est la constance**, une image pour le plan
  (`salon-plan-iso`), une pour la lumière (`salon-vue-comptoir-arche`).
- **« parfait intègres et /goal … 20 000 euros minimum … minimum à 100 % »**, puis « prends le contrôle du
  PC et de Chrome pour mieux regarder », puis « libère l'espace ».
- **I1, la pièce de ses images** (`monde/VAGUES.md`, « L'INTÉGRATION ») : murs crème, coupole OVALE à gorge
  dorée + couronne de spots, comptoir de bois blond cannelé (relief en carte de normales) au plateau de pierre
  blanche, arche rétroéclairée au logo, portant doré à coupons de wax (des tissus, jamais des vêtements), sol
  crème poli ; **le jour clair, le soir tamisé** (`TAMISE` 0,45, halo limité aux lampes : la pièce claire
  devenait laiteuse) ; lumière recuite (essai 1024 en 6 min 30, finale 2048 lancée). Regardé dans son Chrome :
  l'arrivée dehors est belle, **les silhouettes des visiteuses cassent l'illusion**.
- **R6, le sol qui reflète au téléphone** : le plan du matin (photo au centre + parallaxe en boîte) **ne
  montrait aucun reflet** ; remplacé par **le miroir par l'œil reflété** (photo à 360° prise en (x, −y, z),
  refaite à chaque arrêt, une face par image).
- **I2, les personnages** : nouvelle Afi et Sènami en 3D (TRELLIS.2, qui exige désormais ≥ 100 000 faces) ;
  Maman : quota ZeroGPU du compte épuisé, demain (`--sans-jeton` ajouté) ; `habiller({ gestes })` : Sènami et
  Maman rejoueront les 12 animations d'Afi (rotations seules, bassin remis à l'échelle) ; `alleger_perso.py`
  écrit (Blender, avant Mixamo). Mongazi accepte les 2 téléchargements Mixamo.
- Planche h1 : bijoux effacés (OpenCV) ; vues de face h1 et h2 découpées.
- ⛔ Hillary : son accord écrit est demandé avant d'envoyer son visage à Hugging Face.
- **Fin d'après-midi** : cuisson 2048 refaite (19 min) ; QC 53/53 ; Mixamo (Mongazi s'est reconnecté) : nouvelle
  Afi riggée ; **Sènami refusée 5 fois par Mixamo** → `transferer_squelette.py` (squelette d'Afi + poids recopiés) ;
  les deux **visibles et animées** dans le salon (bug du bassin négatif corrigé). Maman : quota ZeroGPU épuisé
  (compte et anonyme). `mesurer.py` : 57 i/s immobile / 28 en marchant au téléphone, 25 Mo chargés.
- Mongazi demande aussi de regarder un **port USB** (gauche, ne reconnaît plus le téléphone) : diagnostic seul
  (le contrôleur USB 3.0 Intel n'est plus détecté), réglages laissés à Mongazi.

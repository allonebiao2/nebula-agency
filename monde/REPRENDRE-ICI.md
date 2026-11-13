# LE MONDE · reprendre ici, à la lettre près

> **Réécrit le 2026-11-13 (matin)**, à la demande de Mongazi : « mets tout en mémoire à la lettre
> près ainsi que tout ce qui reste à faire, comme ça quand je fais clear et je démarre une nouvelle
> discussion tu puisses te repérer à la lettre près ».
>
> **Ordre de lecture en arrivant** : cette page → **`REALISME.md`** (le mini-objectif « le plus
> réaliste possible » du 2026-11-13 : la grille R1 à R15, ce qu'il faut de chacun) → `AUDIT-JEU-VIDEO.md` (la feuille de route en
> vagues, et sa section « Avancement ») → `VAGUES.md` (toutes ses demandes, avec ses mots) →
> `DEROULEMENT.md` (le carnet du futur skill et tous les pièges) → `DESIGN.md` (les règles de
> l'interface en verre) → `lieux/hillary-m-styl/personnages/CONSIGNES.md` (âges, consignes d'image,
> de 3D et d'animation).
>
> Les états précédents (12 novembre) sont recopiés tels quels en **annexe**, en bas : ils sont
> **périmés** (Unreal, Mixamo à faire, etc.), on ne les exécute pas.

---

## 0 · En arrivant, dans cet ordre

1. `python scripts/rapatrier.py` (règle du dépôt), puis `git pull` si `main` est en retard.
2. **Relancer le serveur du salon en tâche de fond** (Mongazi le voyait tourner « en bas ») :
   `python monde/_servir.py --sans-construire` → `http://localhost:8765/lieux/hillary-m-styl/`.
   Au téléphone, sur le même Wi-Fi : `http://192.168.100.203:8765/lieux/hillary-m-styl/` (adresse
   relevée le 2026-11-13, elle peut changer : `ipconfig`). Sans `--sans-construire` si `plan.json`
   ou le catalogue d'Hillary a changé (il reconstruit d'abord).
3. **Regarder ce que Mongazi a déposé** dans `_partage\immersive  store 3D\personnages\` (deux
   espaces entre « immersive » et « store ») : un dossier `senami\` ou `maman\` (modèle 3D, vidéos
   d'animation dans `videos\`), un dossier `_partage\immersive  store 3D\hillary\` (ses photos + son
   accord écrit). Au 2026-11-13 au matin, **seul `afi\` existe**.
4. Puis **la prochaine action exacte** (section 4).

⚠️ **Plus aucune tâche Epic ou Unreal à relancer** : Epic et Unreal sont **désinstallés** le
2026-11-12 (19 h 59), dossiers supprimés, vérifié le 2026-11-13 (`C:\Program Files\Epic Games`
n'existe plus). `C:` a 43 Go libres, `D:` 59 Go.

## 1 · Où on en est, en une phrase

Le salon 3D d'HILLARY M. STYL **tourne en local et se joue de bout en bout** (on arrive DEHORS face
à son enseigne, « Entrer », visiteuses, Hillary au comptoir, conseil, fiche, sac, commande en trois
étapes, WhatsApp), avec une **interface en verre** relue par Impeccable (« ship », `DESIGN.md`), un
**salon tamisé** avec musique, une **ouverture cinéma**, **Afi en vraie 3D animée** et des
**conversations mises en scène** (cadrage, profondeur de champ, caméra qui suit). **Les trois autres
personnages sont encore des silhouettes de maquette.** **Rien n'est en ligne.** QC **52/52**.

## 2 · La méthode imposée par Mongazi (2026-11-12, nuit)

- On suit **`monde/AUDIT-JEU-VIDEO.md` vague par vague** : « fais-les par vagues, mets toute ton
  énergie et tes compétences dans une à la fois, et ne passe pas à une autre tant que celle sur
  laquelle tu es n'est pas à 100 % » ; « tu as champ libre, utilise tous les moyens possibles ».
- **Seule exception, donnée par lui** : quand une vague attend un apport de sa part, « en attendant
  tu peux enchaîner avec le prochain » (c'est ainsi que la vague 3 a été faite pendant que la vague 2
  attend la 3D de Sènami et de sa mère).
- **Une vague n'est finie que si** : QC `python monde/_qc.py` à **52/52** (ou plus, si on ajoute des
  contrôles) · captures **regardées** au téléphone (390) et à l'ordinateur (1440, `?qualite=haute`) ·
  section « Avancement » de `AUDIT-JEU-VIDEO.md`, `VAGUES.md` et cette page à jour · commit + push sur
  `main`.
- **L'objectif** : « ressembler à GTA 6 et Call of Duty à 200 % », une immersion « qui vaut 20 000 €
  minimum », et **faire ACHETER** (chaque choix se juge à « est-ce que ça donne envie d'acheter ? »).
  Le succès principal : un commerçant qui signe. Un enfant de 5 ans doit savoir s'en servir ; rien ne
  remplit l'écran.

## 3 · L'avancement des vagues de l'audit (état exact au 2026-11-13, matin)

| Vague | État | Commit | Fait | Reste |
|---|---|---|---|---|
| **1 · L'ouverture cinéma** | ✅ 100 % | `bcfc59e` | travelling de la rue au trottoir (7,5 s, attend que le salon soit chargé), immeuble au-dessus avec fenêtres aux rideaux éclairés le soir, ciel jour/nuit, façade anthracite, enseigne lumineuse (logo détouré), filet sous le linteau, portes vitrées qui coulissent, musique qui monte, projecteurs un à un, Afi qui attend 5 s puis s'arrête à 1,60 m | rien |
| **2 · Des personnages qui vivent** | 🟡 partielle | `b271315` | **Afi** : 13 FBX, variantes (`parler`/`parler-2`, `attendre`/`attendre-2`), `demarrer`/`arreter` joués une fois, pieds qui piétinent quand elle pivote, regard cou 35 % + tête 50 %, geste qui change toutes les 5 à 8 s en parlant, 9 à 14 s en attente | 🙋 **Sènami et Maman en 3D** (Mongazi les génère) · 🙋 **Hillary** (photos + accord) · ⛔ clignements impossibles sur un modèle TRELLIS (pas de visage riggé ; il faudrait un visage à blend shapes, MPFB2/MakeHuman) · non faits : IK des pieds, os ressorts (jupes, boubou, gele), peau délitée, gestes de métier · allègement d'Afi (88 000 sommets) → vague 4 |
| **3 · La mise en scène des conversations** | ✅ 100 % | `f7d60aa` | voir le détail juste en dessous | rien |
| **4 · La chaîne d'assets pour la 3G** | ⏭️ **LA PROCHAINE** | | | tout (section 4) |
| **5 · La lumière cuite dans Blender** | ⏳ | `8137808` (export) | le décor s'exporte : `python monde/_outils/exporter_decor.py` → `monde/_cuisson/salon-decor.glb` (116 objets nommés `decor-N`, 3 lampes ; dossier ignoré par git) | `cuire.py` à écrire, cartes de lumière à recharger |
| **6 · Les robes en 3D et le mode « examiner »** | ⏳ 🙋 | | | attend les 18 planches (`PROMPTS-ROBES-3D.md`) |
| **7 · La vraie rue et la voix d'Hillary** | ⏳ 🙋 | | | attend la vidéo d'une rue de Cotonou et l'accord d'Hillary |

### Le détail de la vague 3 (pour ne rien refaire)

- **Profondeur de champ** : `BokehPass` de three.js r180, copié dans `socle/vendor/three/addons/postprocessing/BokehPass.js`
  et `shaders/BokehShader.js` (source : `_studio-video/node_modules/three/examples/jsm/`). Monté dans
  `socle/moteur.js` en qualité « haute » seulement (`qualite.cinema`), **éteint hors dialogue**, API
  `moteur.flou(actif, distance)`. Réglage **`aperture: 0.0018, maxblur: 0.0055`**. ⚠️ À `0.009` le
  disque très clair d'un podium « bavait » sur les jambes d'Afi : ce flou ne gère pas l'occlusion.
- **Cadrage selon la distance et la largeur d'écran** (`socle/dialogue.js`, `montrer()`) :
  `enHauteur = 2·atan(0,6/d)` (de la taille à la tête), `enLargeur = 2·atan(tan(atan(0,55/d))/aspect)`
  (1,10 m de large, indispensable en portrait), `fov = min(base − 4, max(base × 0,55, max(enHauteur, enLargeur)))`,
  puis `deplacement.cadrer(fov, d)` (resserre le champ ET met au point à `d`).
- **La caméra SUIT la tête de celle qui parle à chaque image** : `deplacement.suivre(f)` (`socle/deplacement.js`),
  `f` = l'os de la tête moins 20 cm. ⚠️ La viser une seule fois ne suffisait pas : selon le trajet, une
  orientation arrivée après coup laissait la caméra sur les hanches d'Afi (tangage −0,47 au lieu de
  −0,20, tête coupée). `cinema(false)` remet à zéro le cadre, le suivi et le flou.
- **Le souffle de la caméra au repos** : 0,0016 / 0,0013 / 0,0008 rad sur tangage, lacet, roulis.
- **L'oratrice tenue à 1,30 m** du visiteur ; les autres visiteuses **écartées de la ligne de regard**
  (`socle/pnj.js` : si une autre est entre la caméra et l'oratrice, k ∈ ]0 ; 0,98[ et à moins de 0,9 m
  de la ligne, elle est poussée de côté de `min(0,9 − dd, dt × 0,9)`). Celle qui marche reste à 0,65 m
  des autres ; distance minimale au visiteur : 1,3 m (`joueur`), 0 (`retenue`), 0,85 sinon.
- **Une lumière de face** portée par la caméra (`lieu.js`) : `SpotLight(0xfff0dd, …, 6, 0.55, 1, 2)`,
  décalée de (0,35 ; 0,25 ; 0) dans le repère de la caméra, visant la tête de l'oratrice, **intensité
  2,4** (à 7 elle brûlait le manteau crème d'Afi), fondu en `exp(−dt × 3)`.
- **Preuves** : `monde/_vues/ordi-scene-afi.png`, `tel-scene-afi.png`, `ordi-scene-hillary.png`,
  `tel-scene-hillary.png` (filmées par `monde/_outils/captures/filmer_dialogue.py`, **par le vrai
  parcours** : toucher Afi, s'approcher, options, « Parler »).

## 4 · LA PROCHAINE ACTION EXACTE : la vague 4, la chaîne d'assets pour la 3G

> ⚡ **2026-11-13, plus tard dans la matinée** : Mongazi fixe un mini-objectif, « le salon doit être
> virtuel mais le plus réaliste possible ». Tout est dans **`monde/REALISME.md`**. J'y propose de
> **commencer par la lumière cuite** (vague 5) en y fondant la compression 3G, au lieu de la vague 4
> seule. **Attendre sa réponse sur l'ordre** ; s'il dit oui, la prochaine action devient « écrire
> `monde/_outils/cuire.py` » (REALISME.md, « Ce que JE fais », point 1). Sinon, le plan ci-dessous.

> Les consignes « image → vidéo » pour animer les personnages ont été **données à Mongazi le
> 2026-11-13** (elles sont aussi dans `personnages/CONSIGNES.md`). Rien ne l'attend de ce côté.
> Quand il dépose Sènami ou Maman, on **interrompt** la vague en cours pour finir la vague 2 (section 5).

Le plan (à tenir dans cet ordre ; **mesurer avant d'optimiser**) :

1. **Mesurer l'état de départ** : écrire `monde/_outils/mesurer.py` (Playwright, un seul navigateur) qui
   relève, aux trois qualités (`?qualite=basse|moyenne|haute`) et au téléphone (390 × 844) : le poids de
   chaque fichier chargé (`page.on('response')`), le poids total, le temps jusqu'au bouton « Entrer »
   actif et jusqu'à `body.embelli`, `renderer.info.render.calls` et `.triangles`,
   `renderer.info.memory.textures` et `.geometries`, la cadence (images par seconde sur 10 s).
   Écrire le tableau « avant » dans `AUDIT-JEU-VIDEO.md`.
2. **Afi allégée** : 88 000 sommets, `afi-attendre.fbx` 6 Mo (le seul avec la peau). Dans Blender
   (`D:\Blender\blender.exe -b -P …`) : importer le FBX, *Decimate* vers ~30 000 triangles (et un
   niveau de détail à ~8 000 pour le loin), texture à 1024 px au téléphone, réexporter. ⚠️ Vérifier
   que le squelette et les poids survivent (les 12 autres FBX sont « sans peau » et se rejouent sur
   ce squelette). Contrôle visuel obligatoire (`monde/_vues/`).
3. **Compression** : géométrie en **meshopt** (`gltfpack`, ⚠️ à vérifier : présent ou non sur le PC,
   npm ou binaire GitHub ; GitHub et PyPI sont parfois injoignables depuis Cotonou), textures en
   **KTX2/Basis** (mémoire graphique divisée par 4 à 6). Côté three.js : copier `MeshoptDecoder`
   (`examples/jsm/libs/meshopt_decoder.module.js`) et `KTX2Loader` + le transcodeur
   (`examples/jsm/libs/basis/`) depuis `_studio-video/node_modules/three/examples/jsm/` vers
   `monde/socle/vendor/three/`.
4. **Moins d'appels de dessin** : fusionner la géométrie fixe par matière
   (`BufferGeometryUtils.mergeGeometries`), instancier les objets répétés (rouleaux de wax, cintres)
   en `InstancedMesh`.
5. **Zéro allocation par image** : chercher les `new THREE.Vector3` / `new THREE.Quaternion` dans
   les fonctions passées à `moteur.chaqueImage` (repères, points de passage, PNJ) et les sortir.
6. **Chargement par étapes** : la rue et la façade d'abord (ce qu'on voit dehors), l'intérieur et
   les objets Poly Haven ensuite (déjà en partie : `socle/ressources.js` après l'ouverture).
7. **Mesurer « après »** avec le même script, comparer, QC 52/52, captures 390 et 1440 regardées.
   Cible : 30 images/s au téléphone, 60 à l'ordinateur. 🙋 La vraie preuve : un Android d'entrée de
   gamme (Mongazi n'en a pas fourni) et **son iPhone** (point 1 de l'interface, ci-dessous).

## 5 · TOUT ce qui reste à faire (liste complète)

### 🤖 Moi, sans attendre personne
1. **Vague 4** (section 4), puis **vague 5** : écrire `monde/_outils/cuire.py` (Blender sans
   fenêtre : `D:\Blender\blender.exe -b -P monde/_outils/cuire.py`) : importer
   `monde/_cuisson/salon-decor.glb`, UV de cuisson (*Smart UV Project*, UV2), Cycles « Diffuse,
   Indirect + Color » ou AO, une carte de lumière par grand objet, export PNG ; côté three.js,
   `material.lightMap` sur l'UV2, retrouvé par le nom `decor-N`. ⚠️ Le jour et la nuit sont réels
   (MET Norway) : on ne cuit que l'**indirect** (rebonds, ombres douces), le direct reste dynamique.
   Ajouter alors une ombre douce sous les personnages (ombre de contact) et une légère brume dans
   les cônes des projecteurs (audit, section 3).
2. **Interface, ce qui restait de la liste « à 100 % »** : point 2, **une main animée la première
   fois** (montrer qu'on touche un point pour avancer et qu'on glisse pour regarder) ; point 4, **les
   animations soignées** des panneaux (entrée et sortie des fiches, du sac, du cadran). Toujours
   conformes à `DESIGN.md` (le détecteur Impeccable le fait respecter :
   `.claude/skills/impeccable/scripts/impeccable detect --json`, lancé depuis `monde/`).
3. **Afi** : `afi-tourner-gauche.fbx` et `afi-tourner-droite.fbx` sont téléchargés mais **pas
   branchés** (`ANIMATIONS` de `socle/habiller.js` ne les liste pas) ; les brancher sur un pivot de
   plus de 60° quand elle est à l'arrêt, au lieu de piétiner avec `marcher`.

### 🙋 Mongazi
4. **Sènami (21 ans, 1,64 m) et Maman Sènami (47 ans, 1,62 m) en 3D** : il les génère lui-même avec
   les consignes de `personnages/CONSIGNES.md` (image de face en pose A sur fond gris uni, 20 000 à
   40 000 triangles, texture de 2048 px au plus, GLB ou FBX), et les dépose dans
   `_partage\immersive  store 3D\personnages\senami\` et `...\maman\`. ⚠️ Les images
   `personnages/senami-face.png` et `maman-face.png` du dépôt sont les **anciennes, aux âges faux**
   (16-17 ans et 60-65 ans, faites le 2026-11-12 à 14 h 29) : **ne pas s'en servir**. Les images aux
   bons âges **n'ont jamais été générées** (quota Cloudflare épuisé le 2026-11-12 ; le dossier de
   sortie est resté vide) ; si besoin : `python monde/_outils/generer_visiteuses.py <dossier>`.
   **Quand un modèle arrive**, la suite est à moi : s'il n'a pas de squelette,
   `python monde/_outils/glb_vers_obj.py <modele>.glb` → `.zip` → Mixamo par Chrome (Mongazi relie
   Chrome par `/chrome` et se connecte LUI-MÊME à Mixamo ; ⛔ jamais taper son mot de passe ; demander
   l'accord avant chaque téléchargement) → les mêmes animations qu'Afi (voir section 7) → les ranger
   dans `monde/lieux/hillary-m-styl/personnages/senami/senami-<anim>.fbx` (et `maman/maman-<anim>.fbx`)
   → dans `lieu.js`, à côté de la ligne 951 :
   `habiller(personnes.senami.perso, { dossier: 'personnages/senami/', prefixe: 'senami', taille: 1.64 })`
   et `habiller(personnes.maman.perso, { dossier: 'personnages/maman/', prefixe: 'maman', taille: 1.62 })`
   → QC, captures, commit.
5. **Les vidéos d'animation** (consignes « image → vidéo » de `CONSIGNES.md`, déposées dans
   `…\personnages\<prénom>\videos\`). ⚠️ **Ce qu'on en fera n'est pas encore décidé ni vérifié** :
   les transformer en mouvement 3D demande un outil de capture de mouvement depuis une vidéo (à
   chercher, gratuit et à licence commerciale, le jour où elles arrivent). Les animations Mixamo
   restent la voie sûre.
6. **Essayer le salon sur son vrai téléphone** (point 1 de l'interface) :
   `http://192.168.100.203:8765/lieux/hillary-m-styl/` sur le même Wi-Fi, et **écouter la musique**
   (un navigateur de test ne prouve pas le son).
7. Recharger WaveSpeed (≈ 40 $) si on veut des images ou du son payants · un Android d'entrée de gamme
   pour mesurer · les 18 planches des robes (`PROMPTS-ROBES-3D.md`, vague 6) · la vidéo d'une rue de
   Cotonou filmée à l'iPhone (vague 7, Gaussian splat) · les 11 vues du salon et les panoramas
   (`PROMPTS-NANO-BANANA.md` D et P ; les panoramas figés sont écartés par lui : « je veux que ça vive »).

### 🙋 Hillary (par Mongazi)
8. **Ses photos + son accord écrit** (visage, voix) → `_partage\immersive  store 3D\hillary\` (dossier
   exclu de GitHub). Mongazi a écrit le 2026-11-13 : « OUI JE LES ENVOIE D'ici là ». Puis la même
   chaîne que les visiteuses, à 26 ans et 1,68 m.
9. Le questionnaire (`QUESTIONNAIRE-HILLARY.md`), son TikTok, les vidéos de ses vrais gestes, sa voix.
10. ⛔ Le défaut de son site en ligne (section 11).

### Plus loin (vagues du registre `VAGUES.md`)
11. La mise en ligne du salon (rien n'est en ligne) · la ville (vague 6 du registre) · le back-office
    d'Hillary (vague 7 du registre) · le loyer (vague 8) · le futur skill tiré de `DEROULEMENT.md`.

## 6 · Ce qui a été fait les 12 et 13 novembre (dans l'ordre, avec les commits)

Le 2026-11-12 (détail dans l'annexe et dans `VAGUES.md`) : analyse avant construction (`40a9400`) ·
maquette jouable (`163bf53`) · TRELLIS.2 et Afi en 3D (`9335bd6`, `acea3c1`, `decfd71`) · décor
Poly Haven (`ee899d2`) · âges (Hillary 26, Afi 29, Sènami 21, Maman 47) et Afi riggée (`36737bf`) ·
Afi animée dans le salon (`5d44eae`) · interface « enseignes peintes » (`cc87378`) puis **rejetée**
par Mongazi (« ringard ») et remplacée par **le verre** + arrivée dehors + dialogues Call of Duty
(`3411a92`) · rendu cinéma (`158c755`) · décor exportable pour Blender (`8137808`) · salon tamisé
(`9843184`) · musique Pixabay (`f648bac`) · revue Impeccable « ship » et `DESIGN.md` (`69fb6f1`,
`84ca3df`, `894a11b`, `afcda49`) · commande en trois étapes (`694ab4c`) · audit d'expert jeu vidéo
(`25ef0cd`) · Epic et Unreal désinstallés (7,2 Go rendus à `C:`).

Le 2026-11-13 : vague 1 de l'audit, l'ouverture cinéma (`bcfc59e`) · vague 2 commencée, Afi qui vit
(`b271315`) · point de reprise (`cc015eb`) · consignes pour que Mongazi génère les personnages en 3D
(`6a07d12`) · consignes image → vidéo (`5e9a19d`) · **vague 3, la mise en scène des conversations
(`f7d60aa`)** · scripts de capture rangés dans `monde/_outils/captures/` et ce point de reprise.

## 7 · La carte du code (ce que fait chaque fichier)

- `monde/socle/` (commun à tous les lieux) :
  `moteur.js` (rendu, qualités `basse|moyenne|haute`, rendu cinéma GTAO + flou + halo + étalonnage +
  SMAA en « haute », descente automatique de qualité si < 30 i/s, `flou()`, `reglerHalo()`) ·
  `deplacement.js` (points de passage, regard au glisser façon Street View, `allerA`, `allerPres`,
  `tournerVers`, `cinema`, `cadrer`, `suivre`, souffle de caméra, étiquettes de sol) ·
  `dialogue.js` (sous-titres, réponses en croix, `montrer()` = la mise en scène) ·
  `pnj.js` (visiteuses : goûts, places, conversations entre elles, abordage du visiteur à 1,6 m,
  écartement, ligne de regard) · `personnages.js` (les silhouettes, `positionTete`, `corps`) ·
  `habiller.js` (habille une silhouette d'un personnage Mixamo : `habiller(perso, { dossier, prefixe,
  taille, vitesseMarche = 1.2, fondu = 0.35 })`, animations `['marcher','parler','saluer','hocher',
  'reflechir','regarder','parler-2','attendre-2','demarrer','arreter']` + `attendre` (le seul fichier
  avec la peau), `perso.animation()` pour les contrôles) · `boutique.js` (fiche, sac, commande en 3
  étapes, WhatsApp) · `reperes.js` (étiquettes au pouce) · `carnet.js` · `son.js` (bruitages placés,
  `musique(url, volume)`, `reglerMusique()` étouffée dehors : passe-bas 650 Hz, 35 %) ·
  `ressources.js` (Poly Haven) · `interface.css` · `vendor/` (three r180, `FBXLoader`, `BokehPass`…).
- `monde/lieux/hillary-m-styl/` : `index.html` · `lieu.js` (le lieu, construit depuis `plan.json` ;
  Afi habillée ligne 951, musique ligne 884, `window.__monde` ligne 984 pour les tests) · `plan.json`
  · `verre.css` (l'interface en verre) · `personnages/` (`CONSIGNES.md`, `afi/` = 13 FBX hors git,
  `afi.glb`, planches) · `musique/salon-lounge.mp3` (hors git, licence Pixabay).
- Les animations d'Afi (Mixamo, FBX binaire 30 i/s) : `attendre` (*Breathing Idle*, avec la peau) ·
  `marcher` (*Female Walk*, sur place) · `parler` (*Talking*) · `saluer` (*Waving*) · `hocher`
  (*Head Nod Yes*) · `reflechir` (*Thinking*) · `regarder` (*Looking Around*) · `attendre-2`
  (*Weight Shift Idle*) · `demarrer` (*Start Walking*) · `arreter` (*Stop Walking*) · `tourner-gauche`
  (*Standing Left Turn*) et `tourner-droite` · `parler-2` (une seconde animation de parole ; nom
  Mixamo exact non noté).
- `monde/_outils/` : `en_3d.py` (TRELLIS.2) · `glb_vers_obj.py` (pour Mixamo) · `polyhaven.py` ·
  `exporter_decor.py` · `voir_modele.html` · `generer_visiteuses.py` · `design_sidecar.py` ·
  `captures/` (voir son `LISEZMOI.md`).
- `monde/_qc.py` (52 contrôles, visite jouée jusqu'au WhatsApp, captures dans `monde/_vues/`).

## 8 · Les pièges appris pendant les vagues 1 à 3 (en plus de l'annexe)

> Le tableau des chemins pris et des impasses (Unreal, TRELLIS, Hugging Face, Mixamo, Kenney,
> `git push` en erreur 408…) **reste valable** : annexe, « 4 · Les chemins pris, et les impasses ».

- **Un abonné `moteur.chaqueImage` passe dans l'ordre d'inscription** : on peut reprendre la caméra
  après le module de déplacement.
- **Un modèle Mixamo issu d'un OBJ n'a pas de normales** : `mergeVertices` puis
  `computeVertexNormals`, sinon il est noir.
- **Mesurer la taille sur les OS, après `mixer.update(0)`** (sinon il flotte à un mètre).
- **Viser une fois ne tient pas** : en conversation, suivre la tête à chaque image (`suivre`).
- **Le flou de three.js ne gère pas l'occlusion** : un fond très clair bave sur la personne nette ;
  garder `maxblur` bas.
- **Une lumière de face trop forte brûle un vêtement clair** (7 → 2,4).
- **Tester par le VRAI parcours** : faire parler une visiteuse à distance (`pnj.parler` direct) la
  filmait derrière un panneau, ce qu'aucun visiteur ne peut faire.
- **Ce PC** : 8 Go, un seul navigateur Playwright à la fois ; Claude Code a déjà tué le serveur par
  manque de mémoire (le relancer seulement avec l'accord de Mongazi, qu'il a donné une fois :
  « Oui, relance-le »). `rm -f` sur des captures est bloqué par la sécurité : écraser par copie.
- **Sous Windows**, la console Python est en cp1252 : `sys.stdout.reconfigure(encoding="utf-8")`.

## 9 · Comment voir et tester

- **Voir** : section 0. Paramètres d'essai : `?direct=1` (on saute l'ouverture, on est dedans),
  `?qualite=basse|moyenne|haute` (ce PC est en « moyenne » ; le rendu cinéma se voit avec `haute`),
  `?heure=21` ou `?heure=14`, `?meteo=pluie|orage|clair|brume`.
- **Contrôler** : `python monde/_qc.py` (plusieurs minutes, 52 contrôles).
- **Filmer** : `monde/_outils/captures/` (ouverture de nuit et de jour, conversations, sonde du cadre).

## 10 · Les comptes et les clés (aucune valeur ici)

| Quoi | Où | État |
|---|---|---|
| Hugging Face | `secrets/huggingface.env` (`HF_TOKEN`, lecture seule, compte « mongazi ») | ✅ (limite de calculs par jour) |
| Mixamo (Adobe) | Chrome de Mongazi, relié par `/chrome` | ✅ il s'y est connecté lui-même le 2026-11-12 |
| Cloudflare Workers AI (images gratuites) | `secrets/cloudflare.env` | ✅ (quota quotidien) |
| WaveSpeed | `secrets/wavespeed.env` | solde 0,04 $ (relevé le 2026-11-12) |
| Higgsfield | MCP | 0 crédit (relevé en septembre, non revérifié) |
| Epic Games | | ⛔ désinstallé |

## 11 · Trouvé en route (hors salon)

⛔ **Sur le site EN LIGNE d'Hillary**, l'Ensemble Jean et la Robe Émeraude affichent « Type de
vêtement introuvable » à l'étape des mesures (jeu `haut_jupe` inexistant). 🙋 Il faut qu'Hillary
dise quelles mesures elle prend pour une jupe. Rien n'est corrigé sans elle.

---

## Annexe · les états précédents, recopiés tels quels (⚠️ PÉRIMÉS : ne rien exécuter d'ici)

### LE MONDE · reprendre ici, au poil près (version du 2026-11-12/13, nuit)

> Écrit le 2026-11-12 au soir, à la demande de Mongazi : « mets tout en mémoire, ce qu'on
> doit faire, tout ce qui a été fait, absolument tout, chemin pris pour être là, comme ça
> quand je démarre une autre discussion on puisse se retrouver au poil près ».
>
> **Ordre de lecture en arrivant** : cette page → `VAGUES.md` (toutes ses demandes, avec
> ses mots) → `DEROULEMENT.md` (le carnet du futur skill, avec tous les pièges).

---

#### 1 · Où on en est, en une phrase

Le salon 3D d'HILLARY M. STYL **tourne en local et se joue de bout en bout**
(entrée, visiteuses, Hillary, conseil, fiche, sac, cadran, WhatsApp), avec un **décor
réel** (marbre, plâtre, chêne, velours, plantes, fauteuils, suspensions scannés), mais
**ses personnages sont encore des silhouettes de maquette**. Le premier **vrai personnage
3D (Afi)** existe ; il doit recevoir **squelette et animations sur Mixamo** (Mongazi y est
connecté, l'extension Claude pour Chrome vient d'être installée). **Rien n'est en ligne.**

#### 2 · La prochaine action exacte

> **ÉTAT DU 2026-11-13, 0 h 30 : ON SUIT `monde/AUDIT-JEU-VIDEO.md` VAGUE PAR VAGUE** (Mongazi : « une à la
> fois, et ne passe pas à une autre tant que celle-ci n'est pas à 100 % »).
> - ✅ Vague 1, l'ouverture cinéma : faite et filmée de nuit et de jour.
> - 🔨 **Vague 2, des personnages qui vivent.** Afi est faite (13 animations, variantes, départ et arrêt, regard cou + tête ; `socle/habiller.js`, `perso.animation()` pour les contrôles). **Reste à faire** :
>   1. Sènami (21 ans) et Maman Sènami (47 ans) : images par `personnages/CONSIGNES.md` (Cloudflare, quota remis à 0 h UTC) → regarder l'âge → TRELLIS.2 (`_outils/en_3d.py … --detourer-ici`) → `glb_vers_obj.py` → Mixamo (repères, puis 8 animations : attendre AVEC la peau, puis marcher en Female Walk sur place, parler, parler-2, hocher, attendre-2, demarrer, arreter) → `habiller()` avec `prefixe: 'senami'` / `'maman'`, tailles 1,64 et 1,62.
>   2. 🙋 Hillary : il faut ses photos et son accord écrit. Bloqué sans Mongazi.
>   ⚠️ Pas de clignement possible sur un modèle TRELLIS : il n'a ni yeux séparés ni visage riggé. Il faudrait un visage à blend shapes (MPFB2/MakeHuman), noté pour plus tard.
> - Ensuite : la vague 3 (mise en scène des conversations), la 4 (compression pour la 3G), la 5 (lumière cuite dans Blender) ; la 6 et la 7 attendent les planches des robes, la vidéo de rue et l'accord d'Hillary.
>
> **ÉTAT DU 2026-11-12, 23 h** : interface en verre **relue par Impeccable (verdict « ship »)** et documentée
> (`monde/DESIGN.md` ; le détecteur Impeccable le fait respecter). Salon tamisé (murs expresso, coupole
> ambrée, un faisceau par création), musique Pixabay (hors dépôt, `lieux/hillary-m-styl/musique/`),
> Blender 5.3 installé (`D:\Blender\blender.exe`). Commande en 3 étapes faite (point 3, QC 52/52). **Restent de la liste « interface à 100 % » : l'essai sur le vrai téléphone de Mongazi (point 1), la main animée de la première fois (point 2), les animations soignées (point 4).**
>
> **ÉTAT DU 2026-11-12, 20 h** (le plus récent, à lire d'abord) :
> - ✅ Afi est en 3D et animée dans le salon (`socle/habiller.js`). Les FBX vivent dans `lieux/hillary-m-styl/personnages/afi/`, ignorés par git (licence Mixamo).
> - ✅ **L'interface est en verre** (`lieux/hillary-m-styl/verre.css`). Mongazi a rejeté les « enseignes peintes », trouvées **ringardes**, et veut des boutons plats, petits, translucides, et rien qui cache la scène.
> - ✅ **On arrive dehors**, face au caisson lumineux qui porte le logo d'Hillary, avec un petit bouton de verre « Entrer ».
> - ✅ Les conversations suivent la vidéo Call of Duty : sous-titres en boîtes translucides, réponses en croix au centre.
> - ✅ **Tout est REGARDÉ** (20 h 25). QC 48/48 au téléphone. Dialogue Call of Duty vérifié (`_vues/tel-03-dialogue.png`). Arrivée dehors vérifiée (`_vues/tel-00-arrivee.png`). Rendu cinéma vérifié (`_vues/ordi-00-cinema.png`). Script de capture : scratchpad `voir_dehors.py` ; à recopier dans `monde/_outils/` si on le garde.
> - ✅ **Le rendu cinéma est branché** en qualité « haute » (`socle/moteur.js` : GTAO, étalonnage, SMAA, halo adouci). ⚠️ Ce PC est en « moyenne » : on le voit avec `?qualite=haute`.
> - ⚠️ **Dehors reste pauvre** : on voit l'enseigne et l'intérieur par la vitrine, mais ni mur de façade ni trottoir crédibles. 🙋 Le vrai remède est **la capture d'une vraie rue** (vidéo iPhone, puis Gaussian splat).
> - **LA CUISSON DE LA LUMIÈRE (Blender, prochaine grande étape)** :
>   1. Ajouter `GLTFExporter` (`_studio-video/node_modules/three/examples/jsm/exporters/`) et un `__monde.exporterDecor()` qui exporte le décor fixe, sans personnages ni repères, avec un **nom stable par objet**.
>   2. Lancer `blender -b -P monde/_outils/cuire.py` : import, UV de cuisson (Smart UV Project, UV2), cuisson Cycles « Diffuse, Indirect + Color » ou AO, une carte de lumière par grand objet, puis export des PNG.
>   3. Côté three.js : `material.lightMap` sur l'UV2, objet par objet, retrouvé par son nom.
>   ⚠️ Le jour et la nuit sont réels (MET Norway) : on ne cuit que la lumière **indirecte** (rebonds, ombres douces), et la lumière directe reste dynamique.
> - ✅ **Epic et Unreal sont désinstallés**, à la demande de Mongazi. ⚠️ Le journal de la suppression des dossiers n'a pas été relu : vérifier que `C:\Program Files\Epic Games` a disparu.
> - 🔨 **Blender s'installe sur `D:\Blender`** (`winget`), pour le précalcul de la lumière.
>
> **L'OBJECTIF FIXÉ PAR MONGAZI** : « ressembler à GTA 6 et Call of Duty à 200 % », « ne t'arrête pas tant que tu ne l'auras pas atteint », « invoque tous tes meilleurs skills de design, utilise Blender ». Le plan, dans l'ordre de ce qui rapporte le plus :
> 1. **La lumière précalculée** : exporter le salon en glTF (`GLTFExporter`, depuis la page), le cuire dans Blender (Cycles, sans fenêtre : `blender -b -P cuire.py`, une nuit sur ce PC), puis recharger les cartes de lumière dans three.js. En secours : three-gpu-pathtracer (MIT).
> 2. **Le décor photoréel par Gaussian splats** (Spark, MIT, three r180 compatible, conçu pour mobile). 🙋 **Il faut une vidéo d'un VRAI lieu**, filmée à l'iPhone par Mongazi : un bel intérieur de boutique et la rue devant, à Cotonou. ⚠️ La lumière d'un splat est figée : pas de jour ni de nuit dedans.
> 3. **Un post-traitement cinéma sur ordinateur** : GTAO, SMAA, bloom et étalonnage par LUT. Les addons sont dans `_studio-video/node_modules/three/examples/jsm/`, à copier comme `FBXLoader`. Niveau de qualité « haute » seulement.
> 4. **Les personnages** : Sènami et sa mère (images avec l'âge, puis TRELLIS.2, puis Mixamo, comme Afi) ; Hillary avec ses photos et son accord ; alléger Afi (88 000 sommets).
> 5. **Les robes en 3D sur les mannequins** (`PROMPTS-ROBES-3D.md`).
> 6. **La finition de l'interface** par Impeccable (revue, puis `DESIGN.md`) et les autres skills de design.

> **MISE À JOUR du 2026-11-12, 18 h 30** (à lire avant le reste de cette section) :
> - ✅ Les **7 animations d'Afi** sont téléchargées : `_partage\immersive  store 3D\personnages\afi\afi-{attendre,marcher,parler,saluer,hocher,reflechir,regarder}.fbx`. Seule `attendre` porte le corps (6 Mo). `marcher` est *Female Walk* sur place. ⚠️ Sur Mixamo, **ne jamais changer de page pendant « Preparing download »** : la préparation reste bloquée (le serveur répond 202 en boucle).
> - ✅ **L'interface est refaite par Impeccable** : direction « Les enseignes peintes de Cotonou », choisie par Mongazi (`lieux/hillary-m-styl/enseignes.css`, `PRODUCT.md`). Le contrat de direction vit dans `.impeccable/` (ignoré par git) ; `impeccable surface-brief read lieux/hillary-m-styl/index.html`, à lancer depuis `monde/`.
> - ⛔ **Impeccable n'est PAS fini**, selon son contrat : il manque les captures 390 et 1440 de tous les états (dialogue, options, fiche, sac, cadran), `impeccable detect`, la revue finale (agent `impeccable-finish-reviewer`), puis `DESIGN.md` (agent `impeccable-documenter`). ⚠️ Le détecteur signale encore une lueur magenta sans décalage, qui vient de `socle/interface.css`.
> - **Prochaine action** : copier les 7 FBX dans `lieux/hillary-m-styl/personnages/afi/` et brancher Afi animée (étape 2 ci-dessous ; `FBXLoader` est déjà dans le vendor). C'est ce qui fera disparaître les « Lego ».
> - 🙋 **Unreal** : le lanceur Epic est ouvert sur la page d'Unreal. Mongazi installe dans **`D:\Epic Games`** (59,9 Go libres, contre 11,4 Go sur `C:`).
> - ⚠️ **Les visiteuses se collent au visiteur dès l'entrée** (Maman Sènami et Afi à moins d'un mètre, vu en capture). Elles ne s'évitent pas non plus entre elles.

0. **EN TOUT PREMIER, relancer les tâches de fond** que Mongazi voyait tourner « en bas »
   avant son `/clear` (il a demandé qu'on s'en souvienne) :
   - **le serveur du salon** (indispensable) : `python monde/_servir.py --sans-construire`
     en tâche de fond → `http://localhost:8765/` et, au téléphone, `http://192.168.100.203:8765/` ;
   - **le poids de ce qui remplit `C:`** (diagnostic) : `du -sh "/c/Program Files/Epic Games" /c/ProgramData/Epic /c/Users/USER/AppData/Local/Temp` (lent, en tâche de fond) ;
   - **le journal d'installation d'Epic** (diagnostic) : `grep -aiE "BuildPatch|LogInstall|UE_5\.8|Insufficient|Disk|Error" /c/Users/USER/AppData/Local/EpicGamesLauncher/Saved/Logs/EpicGamesLauncher.log | grep -viE "EOSAuth|Verify access" | tail -30`
     (on y avait vu l'alerte **DP-06** ; Unreal 5.8 est sur `C:\Program Files\Epic Games\UE_5.8`, `C:` à 12,8 Go libres).
1. ✅ **FAIT le 2026-11-12 après-midi** : Afi est envoyée sur Mixamo, ses 9 repères sont posés, le
   squelette standard fonctionne (marche vérifiée dans l'aperçu), *Breathing Idle* appliquée.
   `FBXLoader` (+ `fflate`, `NURBSCurve`, `NURBSUtils`) est copié dans `socle/vendor/three/addons/`.
   🙋 **Reste : l'accord de Mongazi pour les 7 téléchargements**, puis les ranger.
   (Rappel de la procédure, si tout est à refaire :)
   **Chrome** : il a été relié le 2026-11-12 par la commande **`/chrome`** (« Browser 1 »).
   Si `tabs_context_mcp` répond « not connected », demander à Mongazi de retaper `/chrome`.
   ⚠️ **Dans ce Chrome, Mongazi N'ÉTAIT PAS connecté à Mixamo** (la page affichait « Log in ») :
   lui demander de cliquer sur **Log in** et de se connecter lui-même (⛔ ne jamais taper son mot
   de passe). Ensuite, sur **mixamo.com**, *Upload Character* → `monde\lieux\hillary-m-styl\personnages\afi-mixamo.zip`
   (régénérable : `python monde/_outils/glb_vers_obj.py monde/lieux/hillary-m-styl/personnages/afi.glb`)
   → 5 repères (menton, poignets, coudes, genoux, aine) → *Skeleton LOD : Standard* →
   animations **Breathing Idle, Walking, Talking, Waving, Head Nod Yes, Thinking, Looking Around**
   → téléchargement **FBX Binary, 30 fps, With Skin pour la 1re, Without Skin pour les autres**
   → `_partage\immersive  store 3D\personnages\afi\`. ⚠️ **Demander l'accord de Mongazi avant
   chaque téléchargement** (nom, source, taille). ⛔ Ne jamais taper un mot de passe.
   Si Chrome n'est pas relié : lui faire redémarrer Chrome, sinon la voie B (il le fait lui-même).
   Alternative SANS compte : **Mesh2Motion** (mesh2motion.org, squelettes et animations CC0).
2. **Brancher Afi animée dans le salon** : copier `FBXLoader.js` (+ ses dépendances) depuis
   `_studio-video/node_modules/three/examples/jsm/loaders/` vers `monde/socle/vendor/three/addons/loaders/`,
   remplacer la silhouette d'Afi par le modèle, l'**échelle à 1,71 m** (le .glb fait 1 m),
   un `AnimationMixer` (attendre / marcher / parler / écouter) branché sur l'état du PNJ.
   ⚠️ **Alléger** : Afi fait 115 000 triangles (viser ~30 000 ; `trimesh` est installé).
3. **Sènami et Maman Sènami en 3D**, dès que le quota Hugging Face est revenu (il se
   remet chaque jour). ⚠️ **D'ABORD refaire leurs images avec leur âge** (Sènami 21 ans,
   Maman 47 ; les premières faisaient 16-17 et 60-65) : consignes mot pour mot dans
   `lieux/hillary-m-styl/personnages/CONSIGNES.md`, Cloudflare `flux-2-dev` (quota épuisé le
   2026-11-12, remis à 1 h), REGARDER l'âge sur l'image, puis seulement : `python monde/_outils/en_3d.py monde/lieux/hillary-m-styl/personnages/senami-face.png --sortie monde/lieux/hillary-m-styl/personnages/senami.glb --resolution 512 --faces 40000 --detourer-ici`
   (puis `maman`). ⚠️ Le compte gratuit limite **le nombre de calculs par jour** : on a épuisé
   la journée du 2026-11-12 avec Afi et les essais.
4. **Relancer le contrôle complet** (`python monde/_qc.py`) : ⚠️ **il n'a PAS été rejoué
   après l'embellissement** (Poly Haven, AgX, plafond) ; le dernier résultat (48/48) est
   d'avant. Puis commit + push.

#### 3 · Ce qui a été fait (le 2026-11-12, dans l'ordre)

1. **Analyse avant tout** (sa consigne) : références de `_partage\immersive  store 3D\` lues
   image par image et la vidéo *Call of Duty* transcrite ; PC mesuré (i5-5300U, 8 Go,
   Intel HD 5500) ; faits vérifiés en ligne → `VISION.md`, `A-APPORTER.md`.
2. **Un agent** a analysé la vidéo en profondeur → `ANALYSE-VIDEO-REFERENCE.md` (52 procédés,
   10 priorités) ; ses corrections sont appliquées (champ 75°, yeux 1,55 m, pas 0,68 m,
   dialogue qui avance seul, accueil sans bras croisés).
3. **La maquette jouable** : socle commun (`socle/`) + lieu d'Hillary (`lieux/hillary-m-styl/`,
   construit depuis `plan.json`). Catalogue **lu** dans sa vitrine (`_construire.py`).
4. **Ce que Mongazi a ajouté en route** (tout est dans `VAGUES.md`) : mobile d'abord et
   repères au pouce · tailles (Hillary 1,68 m ; Afi 1,71 ; Sènami 1,64 ; Maman 1,62) · les
   corps parlent (pas d'images) · question, écoute, réponse · tout choisir apprend tout (le
   **carnet**) · sons réalistes libres (19 bruitages Kenney CC0, placés dans l'espace) · on
   ne voit pas ses bras · s'approcher, puis **options**, puis discussion · back-office d'Hillary
   (vague 7) · Unreal pour la construction · PNJ noires, claires ou foncées · Hillary reconnaissable ·
   « pas de Lego, de vrais personnages 3D » · « voie gratuite » · « graphisme comme Call of Duty
   Korea, GTA 6, objectif principal ».
5. **Graphisme, piste 1** : lumière HDR photographiée, matières et objets **Poly Haven (CC0)**
   chargés après l'ouverture (`_outils/polyhaven.py`, `socle/ressources.js`), tons AgX.
6. **Personnages** : planches des 3 visiteuses générées gratuitement (Cloudflare Workers AI) ;
   **Afi convertie en vraie 3D** par **TRELLIS.2** (Microsoft, MIT) sur Hugging Face
   (`_outils/en_3d.py`) ; convertisseur `.glb` → OBJ pour Mixamo (`_outils/glb_vers_obj.py`) ;
   visionneuse `_outils/voir_modele.html`.
7. **Consignes** : `PROMPTS-NANO-BANANA.md` (Hillary B1-B4, visiteuses, salon D1-D11,
   **panoramas 360° P1-P4**, objets, voix), `PROMPTS-ROBES-3D.md` (18 robes), `QUESTIONNAIRE-HILLARY.md`.
8. **Unreal** : lanceur installé (`winget`), compte Epic de Mongazi ; script `unreal/construire_lieu.py`
   écrit (jamais lancé).

#### 4 · Les chemins pris, et les impasses (pour ne pas les refaire)

| Essayé | Résultat | Ce qu'on fait à la place |
|---|---|---|
| Faire tourner Unreal sur ce PC | 8 Go, Intel HD 5500 : l'éditeur risque de ne pas s'ouvrir | navigateur (Three.js) ; Unreal pour construire, éclairer, filmer |
| **Unreal 5.8 installé sur `C:`** | ⛔ **bloqué vers la fin, alerte DP-06** : `C:` n'a que **12,8 Go libres** | 🙋 Mongazi : **annuler** dans le lanceur, réinstaller dans **`D:\Epic Games`** (créé, NTFS, 64 Go libres ; le lanceur refuse la racine `D:\`) |
| Prendre le contrôle de l'écran | pas disponible dans le terminal (il faut l'app Claude pour ordinateur + « Computer use ») | lanceur ouvert par lien interne `com.epicgames.launcher://ue/library` ; navigateur par l'extension Chrome |
| WaveSpeed (3D payante) | solde 0,04 $ | **voie gratuite** choisie par Mongazi |
| Démo `microsoft/TRELLIS` | en panne (CONFIG_ERROR) | **`microsoft/TRELLIS.2`** (poids MIT), qui marche |
| `pip install gradio_client` | PyPI ne répondait pas | l'outil parle le protocole Gradio 6 à la main |
| Hugging Face sans compte | quota de carte graphique épuisé | **jeton « read »** de Mongazi dans `secrets/huggingface.env` (compte « mongazi ») |
| Hugging Face avec compte gratuit | **limite de NOMBRE de calculs par jour** | `--detourer-ici` (détourage sur le PC, `rembg`) : 2 calculs par personnage |
| Mixamo avec un `.glb` | Mixamo n'accepte que FBX, OBJ ou .zip | `_outils/glb_vers_obj.py` (sans bibliothèque) → `afi-mixamo.zip`, texture en PNG |
| Kenney : téléchargement direct | lien signé derrière la session de la page | récupérer d'abord les cookies de la page, puis `/download-link/<id hex>` |
| `potted_plant_01` (Poly Haven) | 5,8 Mo (géométrie) | écartée, `potted_plant_04` (0,6 Mo) |
| Un `heredoc` Python avec du JavaScript | le shell casse sur les apostrophes | écrire le script dans un fichier, puis le lancer |
| `git push` d'un gros commit | erreur 408 (connexion lente) | `git -c http.postBuffer=524288000 push` |

#### 5 · Comment voir et tester

- **Voir** : `python monde/_servir.py` (construit puis sert) → `http://localhost:8765/` ;
  au téléphone sur le même Wi-Fi : `http://192.168.100.203:8765/` (l'adresse peut changer).
  Essais : `?direct=1` (sans écran d'ouverture), `?qualite=basse|moyenne|haute`, `?heure=21`, `?meteo=pluie|orage|clair|brume`.
- **Contrôler** : `python monde/_qc.py` (visite jouée jusqu'au WhatsApp, captures dans
  `monde/_vues/`, **un seul navigateur à la fois sur ce PC**).
- ⚠️ **Mémoire du PC** : 8 Go, souvent 1,2 Go libres ; Claude Code a déjà tué le serveur
  local par manque de mémoire. Fermer Edge aide.

#### 6 · Les comptes et les clés (aucune valeur ici)

| Quoi | Où | État |
|---|---|---|
| Hugging Face | `secrets/huggingface.env` (`HF_TOKEN`, lecture seule, compte « mongazi ») | ✅ |
| Mixamo (Adobe) | navigateur de Mongazi | ✅ connecté (dit le 2026-11-12) |
| Epic Games | lanceur | ✅ compte créé |
| Extension Claude pour Chrome | Chrome | ✅ installée, **liaison à vérifier** |
| WaveSpeed | `secrets/wavespeed.env` | solde 0,04 $ (non utilisé) |
| Cloudflare Workers AI (images gratuites) | `secrets/cloudflare.env` | ✅ |

#### 7 · Ce qui attend Mongazi ou Hillary

Le tableau complet est en bas de `VAGUES.md`. L'essentiel : **annuler Unreal sur C: et le
réinstaller sur D:** · **les photos d'Hillary + son accord écrit** (dans
`_partage\immersive  store 3D\hillary\`, dossier exclu de GitHub) · le questionnaire · son
TikTok · **ses gestes filmés** · les **panoramas 360°** et les vues du salon · les planches
de ses robes.

#### 8 · Trouvé en route (hors salon)

⛔ **Sur le site EN LIGNE d'Hillary**, l'Ensemble Jean et la Robe Émeraude affichent « Type de
vêtement introuvable » à l'étape des mesures (jeu `haut_jupe` inexistant). Rien corrigé sans elle.

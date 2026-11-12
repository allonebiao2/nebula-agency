# LE MONDE · reprendre ici, au poil près

> Écrit le 2026-11-12 au soir, à la demande de Mongazi : « mets tout en mémoire, ce qu'on
> doit faire, tout ce qui a été fait, absolument tout, chemin pris pour être là, comme ça
> quand je démarre une autre discussion on puisse se retrouver au poil près ».
>
> **Ordre de lecture en arrivant** : cette page → `VAGUES.md` (toutes ses demandes, avec
> ses mots) → `DEROULEMENT.md` (le carnet du futur skill, avec tous les pièges).

---

## 1 · Où on en est, en une phrase

Le salon 3D d'HILLARY M. STYL **tourne en local et se joue de bout en bout**
(entrée, visiteuses, Hillary, conseil, fiche, sac, cadran, WhatsApp), avec un **décor
réel** (marbre, plâtre, chêne, velours, plantes, fauteuils, suspensions scannés), mais
**ses personnages sont encore des silhouettes de maquette**. Le premier **vrai personnage
3D (Afi)** existe ; il doit recevoir **squelette et animations sur Mixamo** (Mongazi y est
connecté, l'extension Claude pour Chrome vient d'être installée). **Rien n'est en ligne.**

## 2 · La prochaine action exacte

> **ÉTAT DU 2026-11-12, 23 h** : interface en verre **relue par Impeccable (verdict « ship »)** et documentée
> (`monde/DESIGN.md` ; le détecteur Impeccable le fait respecter). Salon tamisé (murs expresso, coupole
> ambrée, un faisceau par création), musique Pixabay (hors dépôt, `lieux/hillary-m-styl/musique/`),
> Blender 5.3 installé (`D:\Blenderlender.exe`). **Prochaine action : la commande en 3 étapes (point 3).**
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

## 3 · Ce qui a été fait (le 2026-11-12, dans l'ordre)

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

## 4 · Les chemins pris, et les impasses (pour ne pas les refaire)

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

## 5 · Comment voir et tester

- **Voir** : `python monde/_servir.py` (construit puis sert) → `http://localhost:8765/` ;
  au téléphone sur le même Wi-Fi : `http://192.168.100.203:8765/` (l'adresse peut changer).
  Essais : `?direct=1` (sans écran d'ouverture), `?qualite=basse|moyenne|haute`, `?heure=21`, `?meteo=pluie|orage|clair|brume`.
- **Contrôler** : `python monde/_qc.py` (visite jouée jusqu'au WhatsApp, captures dans
  `monde/_vues/`, **un seul navigateur à la fois sur ce PC**).
- ⚠️ **Mémoire du PC** : 8 Go, souvent 1,2 Go libres ; Claude Code a déjà tué le serveur
  local par manque de mémoire. Fermer Edge aide.

## 6 · Les comptes et les clés (aucune valeur ici)

| Quoi | Où | État |
|---|---|---|
| Hugging Face | `secrets/huggingface.env` (`HF_TOKEN`, lecture seule, compte « mongazi ») | ✅ |
| Mixamo (Adobe) | navigateur de Mongazi | ✅ connecté (dit le 2026-11-12) |
| Epic Games | lanceur | ✅ compte créé |
| Extension Claude pour Chrome | Chrome | ✅ installée, **liaison à vérifier** |
| WaveSpeed | `secrets/wavespeed.env` | solde 0,04 $ (non utilisé) |
| Cloudflare Workers AI (images gratuites) | `secrets/cloudflare.env` | ✅ |

## 7 · Ce qui attend Mongazi ou Hillary

Le tableau complet est en bas de `VAGUES.md`. L'essentiel : **annuler Unreal sur C: et le
réinstaller sur D:** · **les photos d'Hillary + son accord écrit** (dans
`_partage\immersive  store 3D\hillary\`, dossier exclu de GitHub) · le questionnaire · son
TikTok · **ses gestes filmés** · les **panoramas 360°** et les vues du salon · les planches
de ses robes.

## 8 · Trouvé en route (hors salon)

⛔ **Sur le site EN LIGNE d'Hillary**, l'Ensemble Jean et la Robe Émeraude affichent « Type de
vêtement introuvable » à l'étape des mesures (jeu `haut_jupe` inexistant). Rien corrigé sans elle.

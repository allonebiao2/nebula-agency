# LE MONDE · carnet de fabrication

> **Pourquoi ce fichier** : Mongazi, 2026-11-12 : « gardes tout le déroulement
> d'un côté car je compte plus tard créer un skill autour de ça que je pourrai
> potentiellement vendre et moi-même utiliser plus tard ».
>
> **Règle** : chaque étape y entre **au moment où elle est faite**, avec ce qui a
> marché, ce qui a échoué, les commandes exactes et le coût. Ce carnet est la
> matière première du futur skill (nom provisoire : `nebula-lieu-3d`). Il ne
> raconte pas, il **transmet** : quelqu'un d'autre doit pouvoir refaire un lieu
> en le suivant.

---

## Étape 0 · Analyser avant de construire (2026-11-12)

### Ce qui a été fait

1. **Lire la demande trois fois** et la reformuler en trois étages (salon, ville,
   loyer) + un objectif caché (le visiteur apprend tout de la maison par les
   échanges). Résultat : `VISION.md` § 1.
2. **Regarder les références**, pas seulement les lister :
   - photos : lues directement ;
   - vidéo de référence (1 min 41, 214 Mo) : **découpée en planches** d'une
     image toutes les 5 secondes, puis 4 images en pleine résolution sur les
     moments clés (interface de dialogue, sortie dans la rue) :
     ```bash
     ffmpeg -i ref.mp4 -vf "fps=1/5,scale=444:-1,tile=4x3" -frames:v 2 planche_%02d.jpg
     ffmpeg -ss 26 -i ref.mp4 -frames:v 1 f_26.jpg
     ```
   - en tirer **une grammaire** (densité, lumière, gestes des PNJ, sous-titres
     nommés, choix en croix, caisse, sortie), jamais une copie du jeu.
3. **Relire le client** : `CONTEXT.md`, le catalogue `PIECES` dans
   `_v4/garde-moteur.js` (19 pièces, prix en FCFA/€/$, délais, express propre
   à chaque pièce), ses règles de commande (4 champs obligatoires, délai de la
   pièce la plus lente), ses photos (portées par des femmes réelles, fond
   détouré, face et parfois dos).
4. **Mesurer la machine** avant de promettre un outil :
   ```powershell
   Get-CimInstance Win32_ComputerSystem      # RAM
   Get-CimInstance Win32_Processor           # processeur
   Get-CimInstance Win32_VideoController     # carte graphique
   Get-PSDrive -PSProvider FileSystem        # disque
   ```
   Résultat : i5-5300U 2 cœurs, 8 Go (1,8 libre), Intel HD 5500, 38 Go libres.
   **Unreal exclu par la machine, Blender exclu en local pour le précalcul.**
5. **Inventorier les générateurs et leurs soldes** :
   - WaveSpeed : `GET /api/v3/balance` puis `GET /api/v3/models`, filtrer sur
     `3d`, `trellis`, `hunyuan3d`, `tripo`, `rodin`, `meshy`, `splat`.
     1 139 modèles, dont une chaîne 3D complète (photo → 3D, multi-vues → 3D,
     squelette, animation, retopologie, UV, photo → splat). Solde 0,04 $.
   - Higgsfield : 0 crédit.
6. **Vérifier en ligne ce qu'on ne sait que de mémoire** (et ne rien affirmer
   avant) :
   - Ready Player Me : **fermé le 31 janvier 2026** (racheté par Netflix) ;
   - MetaHuman hors Unreal : autorisé depuis juin 2025 selon Epic, mais sources
     contradictoires, et trop lourd pour un téléphone de toute façon ;
   - Open-Meteo : **gratuit seulement en non commercial** → MET Norway ;
   - Unreal : 32 Go de RAM et 8 Go de mémoire graphique recommandés ; aucune
     sortie navigateur hors *Pixel Streaming* (un serveur à carte graphique par
     visiteur) ;
   - couverture « Photorealistic 3D Tiles » de Google sur Cotonou : **non
     confirmée**, à vérifier sur leur carte avant l'étage 2.
7. **Écrire la vision, la liste à apporter, les questions** (`VISION.md`,
   `A-APPORTER.md`), puis **poser les questions avant de construire**.

### Étape 0 bis · analyser « à 100 % » une vidéo de référence (demandé par Mongazi)

La première passe (une image toutes les 5 s) **avait raté la moitié des
mécaniques** : la course confiée au début, le PNJ guide, l'article montré,
l'écran mural commenté, le sac visible, l'écran de paiement avec QR. Méthode
complète, à appliquer d'emblée la prochaine fois :

1. **Une image toutes les 2 s**, en planches de 6 (12 s chacune, dans l'ordre),
   rognées sur la zone du jeu :
   ```bash
   ffmpeg -i ref.mp4 -vf "fps=1/2,crop=888:330:0:0,tile=2x3" p_%02d.jpg
   ```
   ⚠️ `drawtext` (horodatage incrusté) **fait planter ffmpeg sur ce PC**
   (Fontconfig absent) : on compte les planches à la place.
2. **La bande son transcrite**, parce que la moitié du sens est dans ce qu'on
   dit :
   ```bash
   ffmpeg -i ref.mp4 -vn -ac 1 -ar 16000 audio.wav
   python -I -c "from faster_whisper import WhisperModel; …('small', device='cpu', compute_type='int8')"
   ```
   ⚠️ Sous `python -I`, `PYTHONIOENCODING` est ignoré : écrire
   `sys.stdout.reconfigure(encoding='utf-8')` (sinon un émoji fait planter
   l'affichage, console cp1252).
3. **Un tableau temps → ce qui se passe → le procédé**, puis **la traduction
   de chaque procédé dans le métier du client**.
4. **Les vidéos YouTube citées** : titre, chapitres et description par
   `ytInitialPlayerResponse` ; ⚠️ les sous-titres automatiques répondent
   **vide puis 429** : télécharger **seulement les passages utiles** et les
   transcrire soi-même :
   ```bash
   yt-dlp -f bestaudio --download-sections "*0:00-2:10" -x --audio-format wav \
     --postprocessor-args "ffmpeg:-ac 1 -ar 16000" -o "debut.%(ext)s" <url>
   yt-dlp --flat-playlist --print "%(id)s | %(title)s" "https://www.youtube.com/channel/<id>/videos"
   yt-dlp --skip-download --print "%(chapters)j" <url>
   ```
   (`/@pseudo/videos` répond 404 : passer par l'identifiant de chaîne, lu dans
   la description.)

### Étape 0 ter · Unreal, installé quand même (2026-11-12)

```powershell
winget install --id EpicGames.EpicGamesLauncher -e --silent --accept-package-agreements --accept-source-agreements
```
L'installateur **demande l'accord administrateur** (fenêtre Windows à valider
par Mongazi), puis s'installe dans `C:\Program Files\Epic Games\Launcher`. Le
moteur exige le compte Epic de Mongazi : marche à suivre dans `A-APPORTER.md`.

### Ce que cette étape a appris (à garder dans le skill)

- ⚠️ **Une vidéo de référence se lit image par image ET s'écoute.** À une
  image toutes les 5 s, sans le son, la moitié des mécaniques passait au
  travers.
- ⚠️ **Le chiffre qui recadre une promesse est souvent dans la vidéo
  elle-même** : le jeu « 100 heures » a coûté environ 14 000 $ d'API, 54
  agents et 19 jours, et son auteur avoue les zones bâclées.

- ⚠️ **La référence de qualité d'un client est un jeu de console ; son public
  est un téléphone en 3G.** On le dit avant de commencer, avec des chiffres, et
  on promet **la sensation** (lumière précalculée, densité, sons, caméra,
  interface), pas le moteur.
- ⚠️ **L'outil que montre une vidéo YouTube n'est pas forcément l'outil du
  projet.** Mesurer la machine et vérifier où le résultat doit tourner (un lien
  sur téléphone) tranche.
- ⚠️ **Un personnage inventé qui vante la maison est un faux avis.** Les PNJ
  sont des visiteurs curieux, pas des clientes témoins.
- ⚠️ **Les photos du catalogue sont portées par des personnes réelles** : on
  reconstruit la pièce sur un mannequin, jamais la personne.
- ⚠️ **Une reconstruction 3D invente ce qu'elle ne voit pas** : validation de
  chaque pièce par la cliente, et la fiche montre la vraie photo.
- ⚠️ **Un service d'avatars peut fermer** (Ready Player Me) : on possède ses
  fichiers 3D, on ne dépend d'aucune plateforme d'avatars.
- ✅ **La photo de référence du client dit souvent la solution** : ses
  mannequins blancs sans tête règlent à la fois le style et la question des
  personnes réelles.

### La liste de contrôle « étape 0 » réutilisable (pour tout futur lieu)

- [ ] références regardées image par image, grammaire écrite
- [ ] dossier client relu : catalogue (où il vit, qui fait foi), règles de
      commande, numéro, photos (qui est dessus ?)
- [ ] machine mesurée, outils exclus nommés avec le chiffre qui les exclut
- [ ] soldes des générateurs relevés, coût estimé
- [ ] faits vérifiés en ligne (services, licences, API)
- [ ] ce qui doit être vrai listé (prix, avis, événements, actualités)
- [ ] consentements nécessaires listés (visage, voix)
- [ ] questions posées au client **avant** la première ligne

---

## Décisions de Mongazi

| Date | Question | Réponse |
|---|---|---|
| 2026-11-12 | Le moteur | « je dirai le 1 [navigateur] mais installe quand même Unreal pour l'utiliser pour la création, pour la fluidité et la qualité de l'expérience » |
| 2026-11-12 | Les PNJ | écrits d'abord, IA plus tard |
| 2026-11-12 | Les visiteurs | « il peut y avoir 3 personnes, donc le 1 et le 2 » → lu comme : la Parisienne + la jeune de Cotonou + sa mère (à confirmer) |
| 2026-11-12 | Les mesures à la commande | au choix du client |

---

## Étape 1 · la maquette jouable

*À venir.*

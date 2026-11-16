# Les visiteuses · les consignes exactes de leurs images

> Les premières images (2026-11-12, matin) ont été faites sans garder leurs
> consignes. Celles-ci sont gardées mot pour mot : une image se refait à
> l'identique, ou se corrige d'une seule ligne.

## LES ÂGES (Mongazi, 2026-11-12 : « on doit appliquer les âges aussi dorénavant »)

Hillary a **26 ans** (un fait). Les visiteuses sont inventées, leurs âges tiennent
leurs répliques :

| Qui | Âge | Pourquoi ce chiffre |
|---|---|---|
| **Hillary** | **26 ans** | dit par Mongazi |
| **Afi** | **29 ans** | « J'ai grandi à Akpakpa, ça fait dix ans que je suis partie » : partie à 19 ans, pour ses études à Paris |
| **Sènami** | **21 ans** | fan du TikTok d'Hillary, étudiante ; **une adulte, pas une adolescente** |
| **Maman Sènami** | **47 ans** | mère d'une fille de 21 ans ; **pas une grand-mère** |

⚠️ **Le piège** : les générateurs vieillissent les mères et rajeunissent les filles.
La première Maman Sènami faisait 60-65 ans, la première Sènami 16-17. Chaque
consigne dit donc l'âge **et** ce qu'il ne faut pas montrer (rides profondes,
cheveux gris, visage d'adolescente).

## Les règles communes (les mêmes que B1 pour Hillary)

Vue de face en pied, pose A pour Mixamo, fond gris clair uni, pas d'ombre portée,
rien dans les mains (le téléphone et le sac sont ajoutés dans le salon).

## Afi, 29 ans (Mongazi la régénère lui-même, 2026-11-13)

> Écrite d'après son image actuelle (`afi-face.png`, celle du modèle 3D en place) pour qu'elle reste
> reconnaissable : manteau crème, cheveux courts naturels, créoles dorées. Elle vit à Paris depuis dix ans
> (partie à 19 ans), c'est la diaspora qui vient commander pour une cérémonie.

```
Full body front view of a 29-year-old Beninese woman who lives in Paris, a confident young professional who looks her age: smooth skin, no wrinkles, no grey hair, an adult face, not a teenager. Photorealistic 3D video game character reference. Very dark brown skin, natural, no skin lightening. Height 1.71 m, tall and slim. Short natural afro hair, small round gold hoop earrings. Open knee-length cream wool coat with notched lapels, fitted black crew-neck top, slim black trousers, black pointed ballet flats. Pose for 3D rigging: A-pose, arms straight and held 45 degrees away from the body, palms facing down, fingers slightly spread and visible, legs straight and slightly apart, feet flat on the ground and visible. Neutral face, mouth closed, eyes open looking straight ahead. Nothing in the hands, no bag, no phone. Plain light grey background, soft even studio lighting, no cast shadows, orthographic-like camera, the whole body visible from head to feet, centered, sharp focus.
```

## Sènami, 21 ans

```
Full body front view of a 21-year-old Beninese woman, clearly a young adult university student, not a teenager: adult face and adult body proportions. Photorealistic 3D video game character reference. Light brown skin, natural, no skin lightening. Height 1.64 m, slim build. Long box braids gathered up in a high bun, small gold hoop earrings. Cropped short-sleeve top in colorful wax print fabric, high-waisted blue jeans, white sneakers. Pose for 3D rigging: A-pose, arms straight and held 45 degrees away from the body, palms facing down, fingers slightly spread and visible, legs straight and slightly apart, feet flat on the ground and visible. Neutral face, mouth closed, eyes open looking straight ahead. Nothing in the hands, no bag, no phone. Plain light grey background, soft even studio lighting, no cast shadows, orthographic-like camera, the whole body visible from head to feet, centered, sharp focus.
```

## Maman Sènami, 47 ans

```
Full body front view of a 47-year-old Beninese woman who looks her age and no older: a youthful mature face, smooth skin with only faint smile lines, no deep wrinkles, no grey hair, elegant and dignified. Photorealistic 3D video game character reference. Very dark brown skin, natural, no skin lightening. Height 1.62 m, average build. Long boubou dress in green and yellow wax print fabric with a matching gele head wrap, gold bracelets, brown leather sandals. Pose for 3D rigging: A-pose, arms straight and held 45 degrees away from the body, palms facing down, fingers slightly spread and visible, legs straight and slightly apart, feet flat on the ground and visible. Neutral face, mouth closed, eyes open looking straight ahead. Nothing in the hands, no bag. Plain light grey background, soft even studio lighting, no cast shadows, orthographic-like camera, the whole body visible from head to feet, centered, sharp focus.
```

Commande : `python scripts/image_cf.py "<consigne>" --modele flux-2-dev --largeur 1024 --hauteur 1024 --sortie <fichier>.jpg`

## Générer les personnages en 3D soi-même (Mongazi, 2026-11-13)

Mongazi génère les personnages en 3D de son côté. Pour qu'ils entrent dans le salon sans retouche :

- **Une image d'entrée** : la consigne ci-dessus (vue de face en pied, pose A, fond gris uni, rien dans
  les mains). Regarder l'âge AVANT de lancer la 3D.
- **Le modèle 3D attendu** : un seul maillage, **pose A ou T**, debout, pieds au sol ; **20 000 à
  40 000 triangles** ; une texture de **2048 px** au plus ; format **GLB** (ou FBX).
- **Le squelette** : sur Mixamo, comme Afi (menton, poignets, coudes, genoux, aine ; squelette
  standard). Ou bien me laisser le modèle : je fais Mixamo.
- **Le déposer** dans `_partage\immersive  store 3D\personnages\<prénom>\` (hors de GitHub).
- ⚠️ Pas de visage d'une personne réelle sans son accord écrit : Sènami et sa mère sont inventées ;
  Hillary seulement avec ses photos et son accord.

## Animer les images générées (image → vidéo), pour des références de mouvement

> Demandé par Mongazi le 2026-11-13. À coller dans l'outil image → vidéo, AVEC l'image du personnage.
> Chaque vidéo doit pouvoir servir de **capture de mouvement** : corps entier visible du début à la fin,
> caméra fixe, un seul personnage, fond gris uni, 5 à 8 s, sans coupure ni zoom.

**Début commun à coller avant chaque action :**

```
Animate this exact character, keep her face, skin tone, body, hair and clothes identical. Full body always visible from head to feet, static locked-off camera at chest height, no zoom, no camera movement, no cuts, plain light grey studio background, soft even lighting, realistic natural human motion, real-time speed, 6 seconds. Action:
```

**Les actions (les mêmes pour Afi, Sènami et Maman Sènami, chacune dans son caractère) :**

| Fichier | Action à ajouter après « Action: » |
|---|---|
| `attendre` | `she stands relaxed, breathing calmly, shifts her weight slightly from one foot to the other, small natural hand movements, looks around the room with curiosity.` |
| `marcher` | `she walks slowly and elegantly forward toward the camera for four steps, natural arm swing, then stops.` |
| `parler` | `she talks warmly to someone in front of her, expressive natural hand gestures at chest height, head nods and small smiles, mouth moving as if speaking.` |
| `ecouter` | `she listens attentively to someone in front of her, nods twice, small smile, hands relaxed in front of her.` |
| `saluer` | `she smiles and waves hello with her right hand, friendly and warm, then lowers her hand.` |
| `regarder-robe` | `she looks closely at a dress on a mannequin to her left, tilts her head, touches her chin, admiring it.` |

**Une action propre à chacune :**

- **Sènami (TikTok)** : `she raises her phone in her right hand and films herself, smiling and talking to the phone camera, turns slightly to show the room behind her.`
- **Afi (la diaspora)** : `she reads a small price tag at chest height, then checks her phone, smiles and nods, satisfied.`
- **Maman Sènami (le wax)** : `she gently takes the edge of a wax fabric between her fingers, feels its texture, nods with approval like an expert.`

⚠️ Exiger « full body always visible » et « static camera » : une vidéo qui recadre ou coupe les pieds ne
sert pas à la capture. Déposer les vidéos dans `_partage\immersive  store 3D\personnages\<prénom>\videos\`.


## LES PERSONNAGES EN VIDÉO (2026-11-14) : la vidéo EST le personnage en conversation

> Mongazi : « comment faire pour que ce soit ultra réaliste ? », « pour les visages, comment se rapprocher
> le maximum possible ? ». Constat : ses images et vidéos sont photoréalistes, c'est le passage en 3D
> (TRELLIS : ~100 px de texture pour le visage ; Mixamo : mouvement générique) qui les détruit. Donc en
> conversation on montre **sa vidéo elle-même**, détourée, posée dans le salon (fond déjà flou). La 3D ne
> sert plus qu'à marcher, de loin. Les consignes « mouvement » plus haut restent pour la capture de mouvement.

**Les règles** : toujours partir de la MÊME image (jamais d'un texte seul) · Flow, mode « Frames to Video »,
**la même image en PREMIÈRE et en DERNIÈRE image** (la boucle se rejoue sans saut) · Veo 3.1 **Qualité**
plutôt que Fast pour les visages si les crédits le permettent · **1080p** si Flow le propose · fond gris uni,
caméra fixe, corps entier (je détoure) · le son ne sert pas (je l'enlève).

### 1 · L'image de départ (Nano Banana Pro, en joignant l'image en pose A du personnage)

Fichier : `personnages\<prénom>\<prénom>-depart.jpg`

```
Keep this exact woman perfectly identical: same face, same skin tone, same hair, same clothes, same jewelry, same body proportions, same plain light grey background, same soft even studio lighting, same full-body framing from head to feet. Change only her pose: she stands naturally and relaxed, facing the camera, arms resting loosely along her body, hands relaxed and visible, weight evenly on both feet, a very slight natural smile, eyes looking straight into the camera. Photorealistic photograph, sharp focus on the face, 9:16 vertical.
```

### 2 · Le début commun des vidéos (Flow, à coller avant chaque action)

```
Animate this exact woman. Keep her face, skin tone, hair, body and clothes perfectly identical to the image. Static locked-off camera at her eye level, about 2.5 meters in front of her, no zoom, no camera movement, no cuts. Her full body stays visible from head to feet the whole time. Plain light grey studio background, soft even frontal lighting, no cast shadows. Realistic, subtle, natural human motion at real-time speed, natural blinking, 8 seconds. She faces the camera because she is talking with the person holding it. The video starts and ends in exactly the same pose as the image, so it loops seamlessly. Action:
```

### 3 · Les actions (après « Action: »)

| Fichier | Qui | Action |
|---|---|---|
| `<prénom>-ecouter-boucle.mp4` | Afi, Sènami, Maman, Hillary | `she listens attentively to the person in front of her, looking them in the eyes, nods slowly twice, a small warm smile, hands relaxed, a slight shift of weight, then settles back into the starting pose.` |
| `<prénom>-parler-boucle.mp4` | Afi, Sènami, Maman, Hillary | `she talks warmly to the person in front of her, natural lip movement as if speaking French, small hand gestures kept close to her body at waist and chest height, elbows near her sides, gentle head movements, then returns to the starting pose.` |
| `hillary-accueillir-boucle.mp4` | Hillary | `she welcomes a client who just walked into her boutique, a bright and sincere smile, a small open-hand gesture inviting them closer, then returns to the starting pose.` |
| `hillary-conseiller-boucle.mp4` | Hillary | `she advises a client about a dress, confident and professional, her hands describe a fitted waist and a long flowing skirt with graceful gestures close to her body, then returns to the starting pose.` |

⚠️ « elbows near her sides » : des mains qui partent loin sortent du cadre et se détourent mal.

### 4 · Hillary : partir de SES vraies photos

Joindre 2 ou 3 vraies photos de son visage (face, trois quarts) **et** `hillary\hillary-corps-face.jpg` :

```
The woman in the reference photos is the person to depict: keep her real face exactly, same face shape, same features, same skin tone, same hairline, do not beautify or change her. Full body front view, she wears exactly the outfit of the full-body image: black long-sleeved dress with an asymmetric hem, nude ballet flats, long locs with rings, gold hoop earrings. She stands naturally and relaxed, facing the camera, arms resting loosely along her body, a warm natural smile, eyes looking straight into the camera. Plain light grey background, soft even studio lighting, no cast shadows, full body visible from head to feet, photorealistic photograph, sharp focus on the face, 9:16 vertical.
```

Fichier : `hillary\hillary-depart.jpg`. ⛔ Son accord écrit (une trace) dans `hillary\` avant toute mise en ligne.

### 5 · Le décor pour Marble (Nano Banana Pro, en joignant `salon\salon-vue-comptoir-arche.jpg`)

Les robes de ces vues ne sont PAS les siennes (fourreaux magenta inventés) : le monde se génère avec des
mannequins nus, sans logo (le vrai logo est posé par-dessus en 3D), sans personne.

```
Keep this boutique interior identical: same architecture, same oval ceiling with the golden light cove and recessed spotlights, same glossy cream floor with its reflections, same wooden counter, same arch, same magenta velvet curtains, same shelves of folded wax fabrics, same plants, same windows onto the street, same daylight. Change only: every mannequin is a bare white mannequin with no clothes at all; the backlit arch behind the counter is plain and empty, no logo and no text; the vertical screen on the wall is switched off, plain black; no people anywhere. Widen the view into a 16:9 landscape wide-angle photograph taken at eye level, about 1.6 m high, showing more of the room on both sides, with straight vertical lines. Photorealistic architectural photograph, sharp everywhere.
```

Fichier : `salon\salon-a-vide-16x9.jpg`, puis dans Marble (compte gratuit) : « créer un monde » depuis cette image.
⚠️ Vérifié le 2026-11-14 (docs.worldlabs.ai) : **le gratuit permet de REGARDER le monde, pas de l'exporter** ;
l'export demande Standard (20 $), les droits commerciaux demandent Pro (35 $/mois).


## HILLARY : SES VIDÉOS FAITES PAR WAN 2.2 (2026-11-15), consignes exactes

> Accord : Mongazi, 2026-11-13 et 2026-11-14 (« Elle est d'accord donc t'inquiètes fais ce que tu as à faire »), noté dans
> `_partage/immersive  store 3D/hillary/ACCORD.md`. Outil : `monde/_outils/en_video.py` (Wan 2.2, Apache 2.0, ZeroGPU,
> gratuit). Tout vit dans `_partage/immersive  store 3D/hillary/` (hors dépôt).

**1 · Le buste** : `hillary-buste-apose.jpg` = `hillary-corps-face.jpg` (1536 × 2752, pose A, robe noire) recadré à
`(150, 43, 1426, 1745)` → 1276 × 1702 (3:4) : de 12 cm au-dessus de la tête jusqu'à 0,62 m du sol, soit **1,18 m de haut**
(le comptoir fait 1,05 m). Calcul : `PX_M = (2640 − 216) / 1,68` (haut de la tête à y = 216, pieds à y = 2640, elle mesure
1,68 m), centre x = 788.

**2 · La pose de repos** (toutes les autres vidéos en PARTENT, donc s'enchaînent sans saut) : `hillary-2-repos.mp4`
(`--duree 3 --graine 11`, depuis le buste en pose A), sa dernière image (`f_049`) = **`hillary-buste-repos.png`**.
```
The young woman slowly lowers both arms and lets them hang naturally along her body, shoulders relaxed, standing still and calm, looking at the camera with a soft closed-mouth smile. Her hands stay down at her sides. Static locked-off camera, no zoom, no camera movement, plain light grey studio background, soft even lighting, subtle realistic human motion, photorealistic.
```
(Un premier essai, `hillary-1-bras.mp4`, `--graine 7`, finissait mains jointes « namaste » : écarté.)

**3 · Les vidéos, toutes depuis `hillary-buste-repos.png`** :

| Fichier | Réglages | Consigne |
|---|---|---|
| `hillary-ecouter-boucle.mp4` | `--fin` = la même image (boucle parfaite), `--duree 5.1 --graine 21` | `The young woman listens attentively to a person standing in front of her, looking into the camera. She nods slowly twice with a small warm smile, blinks naturally and breathes calmly. Her arms stay relaxed along her body. Static locked-off camera, no zoom, no camera movement, plain light grey studio background, soft even lighting, subtle realistic human motion, photorealistic.` |
| `hillary-parler.mp4` | `--duree 5 --etapes 4 --graine 33` | `The young woman talks warmly to a person standing in front of her, looking into the camera. Her lips move naturally as she speaks, she raises her hands and makes small expressive gestures at chest height close to her body, gentle head movements and a friendly smile. She stays in place. Static locked-off camera, no zoom, no camera movement, plain light grey studio background, soft even lighting, realistic natural human motion, photorealistic.` |
| `hillary-ecouter-2.mp4` | `--duree 4 --etapes 4 --graine 52 --sans-jeton` | `The young woman listens attentively to a person standing in front of her, looking into the camera. She nods gently twice, blinks naturally, tilts her head slightly and keeps a small warm smile. Her arms stay relaxed along her body, she stays in place. Static locked-off camera, no zoom, no camera movement, plain light grey studio background, soft even lighting, subtle realistic human motion, photorealistic.` |
| `hillary-accueillir.mp4` | `--duree 4 --etapes 4 --graine 64 --sans-jeton` | `The young woman welcomes a client who just walked into her boutique: a bright sincere smile, she raises her right hand in a small friendly wave at shoulder height, then opens her hand toward the camera in an inviting gesture and lowers her arm back along her body. She stays in place. Static locked-off camera, no zoom, no camera movement, plain light grey studio background, soft even lighting, realistic natural human motion, photorealistic.` |
| `hillary-conseiller.mp4` | `--duree 4 --etapes 4 --graine 77 --sans-jeton` | `The young woman advises a client about a dress, confident and professional, speaking with a warm smile. Her hands describe a fitted waist and then a long flowing skirt with graceful gestures close to her body, then she lowers her arms back along her body. She stays in place. Static locked-off camera, no zoom, no camera movement, plain light grey studio background, soft even lighting, realistic natural human motion, photorealistic.` |

Ce qu'on en a vu : le visage reste fidèle (comparé agrandi à l'image d'origine) ; la boucle « première = dernière image »
bouge à peine (d'où le montage de 23 s : calme, calme, `ecouter-2` aller-retour, calme) ; « parler » à 4 pas de calcul a un
flou de mouvement sur les mains (le détourage par la couleur le garde transparent, c'est juste). Puis : section F de
`monde/REPRENDRE-ICI.md` (détourer, monter, alléger).

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

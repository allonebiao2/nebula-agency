# Le mini-Mongazi · les prompts de l'avatar

> **Source de vérité.** La fiche avec les boutons « Copier » (https://claude.ai/artifact/FJRogAtCUgXEi4NCNHLN6H, privée)
> est fabriquée à partir de ce fichier par `python _studio-video/_outils/avatar_fiche_prompts.py <sortie.html>`, puis
> republiée à la même adresse. On corrige ICI, jamais dans la page.

L'avatar de Mongazi, en **3D**, dans le style de l'image que Mongazi joint lui-même. Il présente les vidéos ACTU et
ASTUCE de son TikTok, et il est le héros des ÉPISODES. Mongazi génère les images dans Google Flow (Nano Banana Pro) ;
Claude les détoure et les anime au rythme de sa voix dans `_studio-video/` : bouche fermée ou ouverte selon le volume de
la voix, avec un fondu de deux images, et clignement des yeux. **31 images** : la fiche, 12 poses, puis la bouche ouverte
et les yeux fermés des 9 poses où il parle. Les prompts sont en anglais, parce que le modèle les suit mieux.

## La marche à suivre

1. **A00, la fiche** : joins 2 ou 3 photos de toi et ton image de style. Génère 2 à 4 essais, garde celui qui te ressemble le plus et envoie-le-moi **avant de continuer** : tout le reste copie cette fiche.
2. **A01, la pose de base** : joins la fiche et ton image de style. Elle fixe le cadrage de toutes les autres. Envoie-la-moi avant de continuer.
3. **A02 à A12** : joins la fiche, ton image de style et A01.
4. **M1 et M2** sur chacune des poses A01 à A09 : joins seulement la pose à modifier.
5. Enregistre chaque image sous son nom dans `_partage/avatar/`. Ce dossier ne part jamais sur GitHub.

## Bon à savoir

- **Tes photos restent chez toi** : tu les joins dans Flow, je n'en ai pas besoin.
- **La tenue n'est écrite que dans A00** (sweat à capuche violet NEBULA, casque noir autour du cou). Pour la changer, modifie la ligne OUTFIT de A00 : les poses copient la fiche.
- **Fond gris clair, pas vert** : en 3D, un fond vert laisse des reflets verts sur le personnage. Je détoure le gris aussi bien.
- **L'écran du téléphone (A05) est vert exprès** : c'est là que j'incruste tes vraies démos.

## Les images

### A00 · La fiche du personnage
- À joindre : 2 ou 3 photos de toi (de face, de trois-quarts, en pied si possible) · ton image de style
- Format : 16:9
- Fichier : `A00-fiche.png`
- Note : c'est la référence de tout le reste, et de tes épisodes animés. On la valide avant tout.

```text
Character model sheet for a 3D animated series. Horizontal 16:9 image. ONE single character, shown several times.

TOP ROW, full body, neutral standing pose, arms relaxed: front view, three-quarter view, side profile, back view.
BOTTOM ROW, head and shoulders: six expressions of the same character: neutral, warm smile, big laugh, surprised, serious, thoughtful.

LIKENESS: the character is the person in the attached PHOTOS. Keep his face shape, skin tone, hairline and hairstyle, facial hair (if any) and glasses (if any), stylized as a 3D animated character but instantly recognizable. A friendly, smart tech creator.
STYLE: use the attached STYLE image only for the art style: copy its 3D rendering, materials, shading and level of detail. Do not copy its character, its pose or its background.
OUTFIT, identical in every view: a deep violet hoodie (#9333EA) with no print and no logo, black over-ear headphones resting around his neck, dark blue jeans, white sneakers.

Same proportions, same outfit and same colors in every view. Evenly spaced, nothing overlapping, nothing cropped.
LIGHT: soft, even studio lighting.
BACKGROUND: plain, flat light grey (#D9D9D9). No gradient, no floor, no shadow.
No text, no labels, no letters, no logo, no watermark.
```

### A01 · Il explique, mains ouvertes (la pose de base)
- À joindre : la fiche A00 validée · ton image de style
- Format : 3:4
- Fichier : `A01-explique.png`
- Note : la pose la plus utilisée. Elle fixe le cadrage des 11 autres : envoie-la-moi avant de continuer.

```text
Use the attached CHARACTER SHEET as the exact reference for the character: same face, same hairstyle, same skin tone, same body proportions, same outfit, same colors.
Use the attached STYLE image only for the art style: copy its 3D rendering, materials, shading and level of detail. Do not copy its character, its pose or its background.

FRAMING: vertical 3:4 image. Waist-up medium shot, from the top of the head down to the hips. Eye-level camera, the character centered and facing the camera. The top of his head sits about 22% below the top edge of the image, so a raised hand would stay inside the frame. His hips touch the bottom edge. Both hands stay fully inside the frame.

POSE: he explains something to the viewer, both hands open in front of his chest, palms slightly up, fingers relaxed, as if presenting an idea.
EXPRESSION: friendly and confident. Mouth closed and relaxed. Eyes open, looking straight into the camera.

LIGHT: soft, even studio lighting from the front left.
BACKGROUND: plain, flat light grey (#D9D9D9). No gradient, no floor, no shadow, no props.
No text, no letters, no logo, no watermark.
```

### A02 · Il salue
- À joindre : la fiche A00 · ton image de style · A01
- Format : 3:4
- Fichier : `A02-salue.png`
- Note : pour ouvrir et fermer la vidéo.

```text
Use the attached CHARACTER SHEET as the exact reference for the character: same face, same hairstyle, same skin tone, same body proportions, same outfit, same colors.
Use the attached STYLE image only for the art style: copy its 3D rendering, materials, shading and level of detail. Do not copy its character, its pose or its background.
Use the attached FRAMING image (pose A01) only for the framing: same camera distance, same character size, same position in the image, same light.

FRAMING: vertical 3:4 image. Waist-up medium shot, from the top of the head down to the hips. Eye-level camera, the character centered and facing the camera. The top of his head sits about 22% below the top edge of the image. His hips touch the bottom edge. Both hands stay fully inside the frame.

POSE: he raises his right hand to shoulder height and waves at the viewer, palm open toward the camera. His left arm rests relaxed along his body.
EXPRESSION: warm, welcoming smile. Mouth closed and relaxed. Eyes open, looking straight into the camera.

LIGHT: soft, even studio lighting from the front left.
BACKGROUND: plain, flat light grey (#D9D9D9). No gradient, no floor, no shadow, no props.
No text, no letters, no logo, no watermark.
```

### A03 · Il montre le haut
- À joindre : la fiche A00 · ton image de style · A01
- Format : 3:4
- Fichier : `A03-haut.png`
- Note : pour désigner le gros texte au-dessus de lui.

```text
Use the attached CHARACTER SHEET as the exact reference for the character: same face, same hairstyle, same skin tone, same body proportions, same outfit, same colors.
Use the attached STYLE image only for the art style: copy its 3D rendering, materials, shading and level of detail. Do not copy its character, its pose or its background.
Use the attached FRAMING image (pose A01) only for the framing: same camera distance, same character size, same position in the image, same light.

FRAMING: vertical 3:4 image. Waist-up medium shot, from the top of the head down to the hips. Eye-level camera, the character centered and facing the camera. The top of his head sits about 22% below the top edge of the image. His hips touch the bottom edge. Both hands stay fully inside the frame, including the raised hand.

POSE: he points straight up with the index finger of his right hand, arm raised, the hand above the level of his head but fully inside the frame, as if pointing at a title written above him. His left arm rests relaxed.
EXPRESSION: enthusiastic, eyebrows slightly raised. Mouth closed and relaxed. Eyes open, looking straight into the camera.

LIGHT: soft, even studio lighting from the front left.
BACKGROUND: plain, flat light grey (#D9D9D9). No gradient, no floor, no shadow, no props.
No text, no letters, no logo, no watermark.
```

### A04 · Il montre le bas
- À joindre : la fiche A00 · ton image de style · A01
- Format : 3:4
- Fichier : `A04-bas.png`
- Note : pour « Écris en commentaire ».

```text
Use the attached CHARACTER SHEET as the exact reference for the character: same face, same hairstyle, same skin tone, same body proportions, same outfit, same colors.
Use the attached STYLE image only for the art style: copy its 3D rendering, materials, shading and level of detail. Do not copy its character, its pose or its background.
Use the attached FRAMING image (pose A01) only for the framing: same camera distance, same character size, same position in the image, same light.

FRAMING: vertical 3:4 image. Waist-up medium shot, from the top of the head down to the hips. Eye-level camera, the character centered and facing the camera. The top of his head sits about 22% below the top edge of the image. His hips touch the bottom edge. Both hands stay fully inside the frame.

POSE: he points down with the index finger of his right hand, his arm stretched diagonally down in front of his body, toward the bottom of the image, as if pointing at the comments below. His left hand rests on his hip.
EXPRESSION: playful, a small knowing smile. Mouth closed and relaxed. Eyes open, looking straight into the camera.

LIGHT: soft, even studio lighting from the front left.
BACKGROUND: plain, flat light grey (#D9D9D9). No gradient, no floor, no shadow, no props.
No text, no letters, no logo, no watermark.
```

### A05 · Il montre son téléphone
- À joindre : la fiche A00 · ton image de style · A01
- Format : 3:4
- Fichier : `A05-telephone.png`
- Note : l'écran vert, c'est là que j'incruste tes vraies démos.

```text
Use the attached CHARACTER SHEET as the exact reference for the character: same face, same hairstyle, same skin tone, same body proportions, same outfit, same colors.
Use the attached STYLE image only for the art style: copy its 3D rendering, materials, shading and level of detail. Do not copy its character, its pose or its background.
Use the attached FRAMING image (pose A01) only for the framing: same camera distance, same character size, same position in the image, same light.

FRAMING: vertical 3:4 image. Waist-up medium shot, from the top of the head down to the hips. Eye-level camera, the character centered and facing the camera. The top of his head sits about 22% below the top edge of the image. His hips touch the bottom edge. Both hands stay fully inside the frame.

POSE: he holds a smartphone upright in his right hand at chest height and turns its screen toward the camera to show it to the viewer. His left index finger points at the phone. The phone screen is a perfectly flat, uniform bright green rectangle (#00FF00): no interface, no icons, no reflection, no glare, fully visible, not covered by his fingers.
EXPRESSION: excited, as if showing something great. Mouth closed and relaxed. Eyes open, looking straight into the camera.

LIGHT: soft, even studio lighting from the front left.
BACKGROUND: plain, flat light grey (#D9D9D9). No gradient, no floor, no shadow, no props.
No text, no letters, no logo, no watermark.
```

### A06 · Il réfléchit
- À joindre : la fiche A00 · ton image de style · A01
- Format : 3:4
- Fichier : `A06-reflechit.png`
- Note : pour poser la question.

```text
Use the attached CHARACTER SHEET as the exact reference for the character: same face, same hairstyle, same skin tone, same body proportions, same outfit, same colors.
Use the attached STYLE image only for the art style: copy its 3D rendering, materials, shading and level of detail. Do not copy its character, its pose or its background.
Use the attached FRAMING image (pose A01) only for the framing: same camera distance, same character size, same position in the image, same light.

FRAMING: vertical 3:4 image. Waist-up medium shot, from the top of the head down to the hips. Eye-level camera, the character centered and facing the camera. The top of his head sits about 22% below the top edge of the image. His hips touch the bottom edge. Both hands stay fully inside the frame.

POSE: he thinks: his right hand under his chin, thumb and index finger resting on the chin, his left arm folded across his body under the right elbow.
EXPRESSION: thoughtful, one eyebrow raised, eyes looking up to the side, away from the camera. Mouth closed and relaxed.

LIGHT: soft, even studio lighting from the front left.
BACKGROUND: plain, flat light grey (#D9D9D9). No gradient, no floor, no shadow, no props.
No text, no letters, no logo, no watermark.
```

### A07 · Bras croisés, sérieux
- À joindre : la fiche A00 · ton image de style · A01
- Format : 3:4
- Fichier : `A07-serieux.png`
- Note : pour les réalités et les mises en garde.

```text
Use the attached CHARACTER SHEET as the exact reference for the character: same face, same hairstyle, same skin tone, same body proportions, same outfit, same colors.
Use the attached STYLE image only for the art style: copy its 3D rendering, materials, shading and level of detail. Do not copy its character, its pose or its background.
Use the attached FRAMING image (pose A01) only for the framing: same camera distance, same character size, same position in the image, same light.

FRAMING: vertical 3:4 image. Waist-up medium shot, from the top of the head down to the hips. Eye-level camera, the character centered and facing the camera. The top of his head sits about 22% below the top edge of the image. His hips touch the bottom edge. Both arms stay fully inside the frame.

POSE: arms crossed firmly over his chest, shoulders straight, standing tall.
EXPRESSION: serious and calm, a slight frown. Mouth closed and relaxed. Eyes open, looking straight into the camera.

LIGHT: soft, even studio lighting from the front left.
BACKGROUND: plain, flat light grey (#D9D9D9). No gradient, no floor, no shadow, no props.
No text, no letters, no logo, no watermark.
```

### A08 · « Non » du doigt
- À joindre : la fiche A00 · ton image de style · A01
- Format : 3:4
- Fichier : `A08-non.png`
- Note : pour « Ne fais pas ça ».

```text
Use the attached CHARACTER SHEET as the exact reference for the character: same face, same hairstyle, same skin tone, same body proportions, same outfit, same colors.
Use the attached STYLE image only for the art style: copy its 3D rendering, materials, shading and level of detail. Do not copy its character, its pose or its background.
Use the attached FRAMING image (pose A01) only for the framing: same camera distance, same character size, same position in the image, same light.

FRAMING: vertical 3:4 image. Waist-up medium shot, from the top of the head down to the hips. Eye-level camera, the character centered and facing the camera. The top of his head sits about 22% below the top edge of the image. His hips touch the bottom edge. Both hands stay fully inside the frame.

POSE: he raises his right index finger at the height of his face and wags it as if saying "no, no, no", the palm facing the camera. His left arm rests relaxed.
EXPRESSION: amused but firm, eyebrows raised. Mouth closed and relaxed. Eyes open, looking straight into the camera.

LIGHT: soft, even studio lighting from the front left.
BACKGROUND: plain, flat light grey (#D9D9D9). No gradient, no floor, no shadow, no props.
No text, no letters, no logo, no watermark.
```

### A09 · Pouce levé
- À joindre : la fiche A00 · ton image de style · A01
- Format : 3:4
- Fichier : `A09-pouce.png`
- Note : pour « Bonne idée ».

```text
Use the attached CHARACTER SHEET as the exact reference for the character: same face, same hairstyle, same skin tone, same body proportions, same outfit, same colors.
Use the attached STYLE image only for the art style: copy its 3D rendering, materials, shading and level of detail. Do not copy its character, its pose or its background.
Use the attached FRAMING image (pose A01) only for the framing: same camera distance, same character size, same position in the image, same light.

FRAMING: vertical 3:4 image. Waist-up medium shot, from the top of the head down to the hips. Eye-level camera, the character centered and facing the camera. The top of his head sits about 22% below the top edge of the image. His hips touch the bottom edge. Both hands stay fully inside the frame.

POSE: he gives a big thumbs-up with his right hand at chest height, toward the camera. His left arm rests relaxed.
EXPRESSION: big satisfied smile. Mouth closed and relaxed. Both eyes open, looking straight into the camera.

LIGHT: soft, even studio lighting from the front left.
BACKGROUND: plain, flat light grey (#D9D9D9). No gradient, no floor, no shadow, no props.
No text, no letters, no logo, no watermark.
```

### A10 · Il rigole
- À joindre : la fiche A00 · ton image de style · A01
- Format : 3:4
- Fichier : `A10-rigole.png`
- Note : pour la blague. Pas de M1 ni de M2 : la bouche est déjà ouverte.

```text
Use the attached CHARACTER SHEET as the exact reference for the character: same face, same hairstyle, same skin tone, same body proportions, same outfit, same colors.
Use the attached STYLE image only for the art style: copy its 3D rendering, materials, shading and level of detail. Do not copy its character, its pose or its background.
Use the attached FRAMING image (pose A01) only for the framing: same camera distance, same character size, same position in the image, same light.

FRAMING: vertical 3:4 image. Waist-up medium shot, from the top of the head down to the hips. Eye-level camera, the character centered and facing the camera. The top of his head sits about 22% below the top edge of the image. His hips touch the bottom edge. Both hands stay fully inside the frame.

POSE: he laughs out loud, his head tilted slightly back, one hand on his belly.
EXPRESSION: big genuine laugh, mouth wide open, eyes squinting with joy.

LIGHT: soft, even studio lighting from the front left.
BACKGROUND: plain, flat light grey (#D9D9D9). No gradient, no floor, no shadow, no props.
No text, no letters, no logo, no watermark.
```

### A11 · Il est choqué
- À joindre : la fiche A00 · ton image de style · A01
- Format : 3:4
- Fichier : `A11-choque.png`
- Note : pour l'ACTU qui surprend. Pas de M1 ni de M2.

```text
Use the attached CHARACTER SHEET as the exact reference for the character: same face, same hairstyle, same skin tone, same body proportions, same outfit, same colors.
Use the attached STYLE image only for the art style: copy its 3D rendering, materials, shading and level of detail. Do not copy its character, its pose or its background.
Use the attached FRAMING image (pose A01) only for the framing: same camera distance, same character size, same position in the image, same light.

FRAMING: vertical 3:4 image. Waist-up medium shot, from the top of the head down to the hips. Eye-level camera, the character centered and facing the camera. The top of his head sits about 22% below the top edge of the image. His hips touch the bottom edge. Both hands stay fully inside the frame.

POSE: both hands on his cheeks, shoulders raised, leaning slightly back.
EXPRESSION: shocked and amazed, eyes wide open, eyebrows high, mouth open in a round "O". Looking straight into the camera.

LIGHT: soft, even studio lighting from the front left.
BACKGROUND: plain, flat light grey (#D9D9D9). No gradient, no floor, no shadow, no props.
No text, no letters, no logo, no watermark.
```

### A12 · Il se tape le front
- À joindre : la fiche A00 · ton image de style · A01
- Format : 3:4
- Fichier : `A12-front.png`
- Note : pour « Oups » et les épisodes. Pas de M1 ni de M2.

```text
Use the attached CHARACTER SHEET as the exact reference for the character: same face, same hairstyle, same skin tone, same body proportions, same outfit, same colors.
Use the attached STYLE image only for the art style: copy its 3D rendering, materials, shading and level of detail. Do not copy its character, its pose or its background.
Use the attached FRAMING image (pose A01) only for the framing: same camera distance, same character size, same position in the image, same light.

FRAMING: vertical 3:4 image. Waist-up medium shot, from the top of the head down to the hips. Eye-level camera, the character centered and facing the camera. The top of his head sits about 22% below the top edge of the image. His hips touch the bottom edge. Both hands stay fully inside the frame.

POSE: he slaps his forehead with the palm of his right hand, head slightly down, as if he just realized a silly mistake. His left arm rests relaxed.
EXPRESSION: funny embarrassed "oops" face, eyes shut tight, teeth clenched in a grimace.

LIGHT: soft, even studio lighting from the front left.
BACKGROUND: plain, flat light grey (#D9D9D9). No gradient, no floor, no shadow, no props.
No text, no letters, no logo, no watermark.
```

### M1 · La bouche ouverte
- À joindre : la pose à modifier, une à la fois (A01 à A09)
- Format : celui de la pose
- Fichier : `A01-bouche.png`, `A02-bouche.png`… jusqu'à `A09-bouche.png`
- Note : on modifie la pose, on ne la refait pas. Il ne doit rien bouger d'autre que la bouche.

```text
Edit the attached image. Keep everything exactly identical: same character, same pose, same hands, same framing, same lighting, same background, same expression.
Change only the mouth: open it naturally, as if he is in the middle of saying "ah" while talking. The lower jaw drops slightly, the mouth is open about the width of a finger, a little of the upper teeth is visible.
Do not move his head, his eyes or his eyebrows. No text, no logo, no watermark.
```

### M2 · Les yeux fermés
- À joindre : la pose à modifier, une à la fois (A01 à A09)
- Format : celui de la pose
- Fichier : `A01-yeux.png`, `A02-yeux.png`… jusqu'à `A09-yeux.png`
- Note : pour qu'il cligne des yeux. Toujours la pose d'origine, jamais celle à la bouche ouverte.

```text
Edit the attached image. Keep everything exactly identical: same character, same pose, same hands, same framing, same lighting, same background, same mouth.
Change only the eyes: both eyelids gently closed, as in the middle of a natural blink.
Keep the eyebrows exactly where they are. No text, no logo, no watermark.
```

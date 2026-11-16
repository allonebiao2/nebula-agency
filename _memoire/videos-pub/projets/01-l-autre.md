# « L'AUTRE » · pub vidéo IA n° 01

> **Pour** : NEBULA Agency. La pub vend le Catalogue digital (la porte d'entrée, 50 000 F) et, sur la carte de fin,
> la pub vidéo elle-même (« Une pub comme ça pour ton commerce ? On la fait aussi. »).
> **Format** : 9:16, environ 1 min · version courte de 30 s au § 7.
> **Qui fait quoi** : Mongazi génère les images et les vidéos dans Google Flow · Claude fait le montage.
> **État au 2026-11-16** : scénario validé par Mongazi (« j'adore le scénario »), dossier prêt, rien n'est généré.
> **Ses deux consignes** : la pub ne dit **pas** qu'elle est faite avec l'IA ; le français reste **très simple**.
> La méthode et les pièges : [`../methode.md`](../methode.md) · les prix : [`../tarifs.md`](../tarifs.md).

---

## 1. L'histoire

À 3 h 14 du matin, Koffi surprend sa femme Afi qui sourit à son téléphone. Elle avoue : « Il y a quelqu'un. Depuis
trois mois. » Tout le quartier écoute à la fenêtre. Koffi allume le néon et regarde le téléphone : ce n'est pas un
amant, c'est le catalogue d'Afi, sa boutique dans le téléphone, qui vend même quand elle dort. « Il livre aussi ? »
« Non. Ça, c'est toi. » Elle lui tend un casque de moto. « Et moi, on me paie combien ? » Elle se recouche : « Dors. »
Puis elle nous regarde, nous : « Et toi ? Ta boutique, elle dort quand tu dors ? »

- **On ne voit pas la fin venir** : chaque réplique d'Afi marche pour un amant ET pour un catalogue (« il dort
  jamais », « il répond à tout le monde », « même à Lomé, on le connaît », « lui, au moins, il travaille »).
- **La bascule** : tout le drame est éclairé comme un film ; le néon s'allume, la musique se coupe, tout devient banal.
  C'est là qu'on rit.
- **La fin en boucle** : le « Dors. » de la fin répond au « Personne. Dors. » du début.
- **L'indice caché** : des piles de pagnes pliés et un sac de livraison sont dans la chambre dès le premier plan. Dans
  le noir on ne les voit pas ; au néon, si.
- **Le 4e mur** (demandé par Mongazi) : deux fois, Afi se tourne vers nous. Au milieu, pour relancer l'attention
  (« Toi aussi, tu crois que c'est un homme ? »). À la fin, pour l'appel (« Et toi ? Ta boutique, elle dort quand tu
  dors ? »). Entre les deux, Koffi nous fixe en silence, le casque à la main (P16).

### Les répliques (à relire par Mongazi)

| Plan | Qui | Réplique |
|---|---|---|
| P02 | Koffi | Afi… C'est qui ? |
| P03 | Afi | Personne. Dors. |
| P04 | Koffi | À trois heures du matin, personne t'écrit ? |
| P05 | Afi | Bon… Oui. Il y a quelqu'un. Depuis trois mois. |
| P06 | Koffi | Trois mois ?! |
| P07 | la tantie | Eeeh Dieu ! |
| P08 | Koffi | Il a quoi de plus que moi ? |
| P09 | Afi | Lui, il dort jamais. Il répond à tout le monde. Même à Lomé, on le connaît. |
| P10 | Afi | Et lui, au moins… il travaille. |
| P11 | les voisins | Waaaah ! |
| P11b | Afi, **à nous** | Toi aussi, tu crois que c'est un homme ? |
| P13 | Koffi | … Des pagnes ? C'est quoi ça ? |
| P14 | Afi | Mon catalogue. Ma boutique dans le téléphone. Il vend même quand je dors. |
| P15 | Koffi | … Il livre aussi ? |
| P16 | Afi | Non. Ça, c'est toi. |
| P17 | la tantie | Afi ! Envoie-moi le lien ! |
| P18 | Koffi | Et moi, on me paie combien ? |
| P19 | Afi | Dors. |
| P20 | Afi, **à nous** | Et toi ? Ta boutique, elle dort quand tu dors ? |

Pour changer une réplique : ne toucher qu'au texte entre guillemets, dans le prompt d'ANIMATION du plan.

---

## 2. Avant de générer

1. **Le filigrane** : réglé, les générations Flow de Mongazi n'en portent aucun (vérifié par lui le 2026-11-16).
2. **Un seul plan d'essai.** Fais R1, R2, R3, puis **P02 seulement**. Écoute : l'accent est-il d'ici ou de Paris ? Les
   lèvres suivent-elles ? Ce plan décide de la suite.
3. **Tout en 9:16**, images et vidéos.

---

## 3. Les références (Nano Banana Pro, une seule fois)

Ensuite, on joint R1, R2 et R3 à **chaque** image de plan (R4 ou R5 pour la fenêtre) : c'est ce qui garde les mêmes
visages et la même chambre d'un plan à l'autre. Visages inventés uniquement, jamais la photo d'une vraie personne.

Les prompts sont en anglais : le modèle les suit mieux. Les répliques restent en français.

### R1 · Afi (format 16:9)

```
Photorealistic character reference sheet, 16:9 landscape. Three views of the SAME woman side by side on a plain light grey studio background: on the left a front close-up portrait, in the middle a three-quarter view, on the right a full-body standing view.
The character, Afi: a Beninese woman, 33 years old, dark brown skin, round face, high cheekbones, expressive almond-shaped eyes, full lips, small gold stud earrings. She wears a burgundy satin sleep bonnet that covers all her hair, and a loose sleeveless nightdress in indigo and orange wax-print fabric. Natural look, no makeup. Kind but sharp expression: the face of a clever businesswoman from the market.
Soft, even studio light, realistic skin texture and pores, natural West African features. No text, no labels, no watermark.
```

### R2 · Koffi (format 16:9)

```
Photorealistic character reference sheet, 16:9 landscape. Three views of the SAME man side by side on a plain light grey studio background: on the left a front close-up portrait, in the middle a three-quarter view, on the right a full-body standing view.
The character, Koffi: a Beninese man, 42 years old, dark skin, slightly round belly, short greying beard, receding hairline, thick eyebrows, a very expressive, slightly dramatic face. He wears a slightly yellowed white sleeveless undershirt and a green and yellow wax-print cloth wrapped around his waist like a sarong. Barefoot.
Soft, even studio light, realistic skin texture and pores, natural West African features. No text, no labels, no watermark.
```

### R3 · La chambre vide (format 9:16)

```
Photorealistic cinematic vertical photo, 9:16. An empty, modest bedroom in a family house in Cotonou, Benin, at night.
A double bed with a wax-print bedsheet, a white mosquito net knotted above the bed, a ceiling fan, louvered glass windows with white wrought-iron burglar bars, pale green painted walls with faint water stains, a small bedside lamp. Clues of a small business, half hidden in the shadows: a white plastic chair piled with neatly folded wax-print fabrics, more stacks of folded wax fabrics on top of a wooden wardrobe, a canvas delivery bag hanging on the door. A single fluorescent tube light fixed on the wall above the door, switched off, and a light switch next to the door.
Low-key night lighting: warm amber light from the bedside lamp, faint blue moonlight through the louvers, deep shadows. Shot on a 35mm lens, subtle film grain, Kodak Vision3 500T color. No people, no text, no watermark.
```

### R4 · La fenêtre, la nuit (format 9:16)

```
Cinematic vertical film still, 9:16. View from inside a dark bedroom toward louvered glass windows with white wrought-iron burglar bars, the glass slats half open.
From outside, four neighbors press their faces into the gaps between the glass slats, eyes wide, spying on the room: in front, an elderly woman in a bright orange headwrap, the most curious; a young man in a football jersey; a teenage girl with braids; a bald middle-aged man in a sleeveless undershirt.
Their faces are lit by faint blue moonlight and by a cold glow coming from inside the room. Night, deep shadows, subtle film grain, Kodak Vision3 500T color, realistic skin texture, natural West African features. A funny situation played completely seriously. No text, no captions, no watermark.
```

### R5 · La fenêtre, au néon (format 9:16, en MODIFIANT R4)

```
Edit the attached image. Keep exactly the same window, the same framing and the same four neighbors with the same faces and clothes.
Change only two things. The window is now lit by flat, harsh, cold white fluorescent light coming from inside the room, almost no shadows, slightly greenish, banal like a low-budget sitcom. And the four neighbors now hold up their smartphones, eager, the elderly woman in the orange headwrap waving hers in front.
No text, no captions, no watermark.
```

---

## 4. Les plans

**Pour chaque plan :**
1. **IMAGE** : Nano Banana Pro, format 9:16, avec les références indiquées jointes. Garder la meilleure.
2. **ANIMATION** : Veo 3.1, mode **Frames to Video**, l'image en première image, 8 s, 2 à 3 prises en Fast. Refaire la
   meilleure en Quality si elle le mérite.
3. **Remettre** la prise retenue sous le nom du plan (`P01.mp4`…) dans `_partage/pub-l-autre/`.

« Garder » = la durée gardée au montage ; le reste des 8 s est coupé.

### Acte 1 · le soupçon (lumière de film)

#### P01 · Le sourire · garder 2 s
Afi sourit à son téléphone dans le noir ; derrière elle, les yeux de Koffi s'ouvrent. Pas de réplique. Références : R1, R2, R3.

**IMAGE**
```
Use the attached reference images for Afi, Koffi and the bedroom: same faces, same satin bonnet, same clothes, same room.
Extreme close-up: Afi lies on her side in bed in the dark, her face lit only by the smartphone she holds close to her face; we see only the back of the phone. She smiles tenderly at the screen. Behind her, out of focus, Koffi lies asleep with his eyes closed, under the white mosquito net.
Cinematic vertical film still, 9:16. Shot on a 35mm lens at f/1.8, shallow depth of field, subtle film grain, Kodak Vision3 500T color. Low-key night lighting: the cold blue-white glow of a smartphone, warm amber light from the bedside lamp, faint blue moonlight through the louvers, deep shadows. Realistic skin texture, natural West African features. The phone screen always faces away from the camera. No text, no captions, no watermark.
```

**ANIMATION**
```
[00:00-00:03] Extreme close-up. Afi, lit only by her phone, smiles tenderly at the screen and bites her lower lip. SFX: a soft phone notification chime.
[00:03-00:06] Behind her, out of focus, Koffi's eyes snap open in the dark. He does not move.
[00:06-00:08] Afi keeps smiling at her phone; she has noticed nothing.
No dialogue. Ambient noise: a ceiling fan humming, crickets outside, a distant motorbike. Audio: only the room sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P02 · « C'est qui ? » · garder 2 s · LE PLAN D'ESSAI
Références : R2, R3.

**IMAGE**
```
Use the attached reference images for Koffi and the bedroom: same face, same undershirt and waist cloth, same room.
Close-up: Koffi lies in bed in the dark, his head on the pillow, eyes wide open and suspicious, staring at his wife's back (she is off-screen, in front of him). His face is half lit by the cold blue glow of her phone.
Cinematic vertical film still, 9:16. Shot on a 35mm lens at f/1.8, shallow depth of field, subtle film grain, Kodak Vision3 500T color. Low-key night lighting: the cold blue-white glow of a smartphone, warm amber light from the bedside lamp, faint blue moonlight through the louvers, deep shadows. Realistic skin texture, natural West African features. No text, no captions, no watermark.
```

**ANIMATION**
```
Close-up. In the dark, Koffi raises his head slightly from the pillow, narrows his eyes and says slowly, in a deep, raspy male voice, speaking French with a West African accent from Benin: "Afi... C'est qui ?"
Then he stays silent and keeps staring.
Ambient noise: a ceiling fan humming, crickets outside, a distant motorbike. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P03 · « Personne. Dors. » · garder 2 s
Références : R1, R2, R3.

**IMAGE**
```
Use the attached reference images for Afi, Koffi and the bedroom: same faces, same satin bonnet, same clothes, same room.
Medium close-up: Afi in bed, caught, presses her glowing smartphone flat against her chest with both hands; the light leaks between her fingers. Her eyes avoid her husband. Koffi is blurred in the background.
Cinematic vertical film still, 9:16. Shot on a 35mm lens at f/1.8, shallow depth of field, subtle film grain, Kodak Vision3 500T color. Low-key night lighting: the cold blue-white glow of a smartphone, warm amber light from the bedside lamp, faint blue moonlight through the louvers, deep shadows. Realistic skin texture, natural West African features. The phone screen always faces away from the camera. No text, no captions, no watermark.
```

**ANIMATION**
```
Medium close-up. Afi presses the glowing phone against her chest, avoids her husband's eyes and says quickly, in a warm, slightly husky female voice, speaking French with a West African accent from Benin: "Personne. Dors."
She pulls the wax-print sheet up to her chin and stays silent. Only Afi speaks in this shot.
Ambient noise: a ceiling fan humming, crickets outside, a distant motorbike. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P04 · Le téléphone vibre · garder 3 s
Références : R1, R2, R3.

**IMAGE**
```
Use the attached reference images for Afi, Koffi and the bedroom: same faces, same satin bonnet, same clothes, same room.
Medium two-shot: in the foreground, Afi lies on her side clutching the phone to her chest, eyes wide open. Behind her, Koffi is propped up on one elbow, looking down at her, his face lit by the glow.
Cinematic vertical film still, 9:16. Shot on a 35mm lens at f/1.8, shallow depth of field, subtle film grain, Kodak Vision3 500T color. Low-key night lighting: the cold blue-white glow of a smartphone, warm amber light from the bedside lamp, faint blue moonlight through the louvers, deep shadows. Realistic skin texture, natural West African features. The phone screen always faces away from the camera. No text, no captions, no watermark.
```

**ANIMATION**
```
[00:00-00:02] The phone vibrates against Afi's chest. SFX: a muffled vibration and three notification chimes in a row.
[00:02-00:06] Behind her, Koffi sits up slowly and says with controlled anger, in a deep, raspy male voice, speaking French with a West African accent from Benin: "À trois heures du matin, personne t'écrit ?"
[00:06-00:08] Silence. Afi closes her eyes. Only Koffi speaks in this shot.
Ambient noise: a ceiling fan humming, crickets outside. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

### Acte 2 · l'aveu (lumière de film)

#### P05 · L'aveu · garder 3,5 s
Références : R1, R3.

**IMAGE**
```
Use the attached reference images for Afi and the bedroom: same face, same satin bonnet and nightdress, same room.
Close-up: Afi sits up in bed, turned toward her husband (off-screen, on the left), eyes wet with tears, jaw set, lit from below by the glow of the phone in her lap.
Cinematic vertical film still, 9:16. Shot on a 35mm lens at f/1.8, shallow depth of field, subtle film grain, Kodak Vision3 500T color. Low-key night lighting: the cold blue-white glow of a smartphone, warm amber light from the bedside lamp, faint blue moonlight through the louvers, deep shadows. Realistic skin texture, natural West African features. The phone screen always faces away from the camera. No text, no captions, no watermark.
```

**ANIMATION**
```
Close-up. Afi takes a deep breath, tears in her eyes, looks straight at her husband (off-screen) and confesses slowly, in a warm, slightly husky female voice, speaking French with a West African accent from Benin: "Bon... Oui. Il y a quelqu'un. Depuis trois mois."
Then she holds his gaze in silence.
Ambient noise: a ceiling fan humming, crickets outside. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P06 · « Trois mois ?! » · garder 2 s
Références : R2, R3.

**IMAGE**
```
Use the attached reference images for Koffi and the bedroom: same face, same undershirt and waist cloth, same room.
Close-up: Koffi sits up in bed in the dark, frozen in shock, one hand pressed on his heart over his white undershirt, mouth slightly open.
Cinematic vertical film still, 9:16. Shot on a 35mm lens at f/1.8, shallow depth of field, subtle film grain, Kodak Vision3 500T color. Low-key night lighting: the cold blue-white glow of a smartphone, warm amber light from the bedside lamp, faint blue moonlight through the louvers, deep shadows. Realistic skin texture, natural West African features. No text, no captions, no watermark.
```

**ANIMATION**
```
Slow dolly-in on Koffi's face. He is devastated, his lips tremble, and he says in a broken whisper, in a deep, raspy male voice, speaking French with a West African accent from Benin: "Trois mois ?!"
He presses his hand harder on his heart and stays silent.
Ambient noise: a ceiling fan humming, crickets outside. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P07 · Les voisins · garder 1,5 s
**IMAGE** : R4 telle quelle, rien à générer.

**ANIMATION**
```
Static shot. The four neighbors spying through the window gasp at the same time. The elderly woman in the orange headwrap covers her mouth and cries out, in a high-pitched old woman's voice, speaking French with a West African accent from Benin: "Eeeh Dieu !"
The others press closer to the glass slats, eyes wide. Only the elderly woman speaks.
Ambient noise: crickets, the night outside. Audio: only the dialogue and the night sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P08 · « Il a quoi de plus que moi ? » · garder 2 s
Références : R2, R3.

**IMAGE**
```
Use the attached reference images for Koffi and the bedroom: same face, same undershirt and waist cloth, same room.
Medium shot: Koffi sits on the edge of the bed in the dark, shoulders slumped, turning his head toward Afi (off-screen), eyes glistening, the white mosquito net hanging behind him.
Cinematic vertical film still, 9:16. Shot on a 35mm lens at f/1.8, shallow depth of field, subtle film grain, Kodak Vision3 500T color. Low-key night lighting: the cold blue-white glow of a smartphone, warm amber light from the bedside lamp, faint blue moonlight through the louvers, deep shadows. Realistic skin texture, natural West African features. No text, no captions, no watermark.
```

**ANIMATION**
```
Medium shot. Koffi turns toward his wife and asks with a broken voice, in a deep, raspy male voice, speaking French with a West African accent from Benin: "Il a quoi de plus que moi ?"
Then he waits, breathing heavily.
Ambient noise: a ceiling fan humming, crickets outside. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P09 · La liste (la réplique à deux sens) · garder 5 s
Références : R1, R3.

**IMAGE**
```
Use the attached reference images for Afi and the bedroom: same face, same satin bonnet and nightdress, same room.
Medium close-up: Afi sits up in bed, glowing with pride and passion, raising three fingers of one hand as if counting, the phone glowing in her other hand on the sheet.
Cinematic vertical film still, 9:16. Shot on a 35mm lens at f/1.8, shallow depth of field, subtle film grain, Kodak Vision3 500T color. Low-key night lighting: the cold blue-white glow of a smartphone, warm amber light from the bedside lamp, faint blue moonlight through the louvers, deep shadows. Realistic skin texture, natural West African features. The phone screen always faces away from the camera. No text, no captions, no watermark.
```

**ANIMATION**
```
Medium close-up. Afi, passionate and proud, counts on her fingers and says, in a warm, slightly husky female voice, speaking French with a West African accent from Benin: "Lui, il dort jamais. Il répond à tout le monde. Même à Lomé, on le connaît."
Then she smiles dreamily and stays silent.
Ambient noise: a ceiling fan humming, crickets outside. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P10 · La pique · garder 2,5 s
Références : R1, R3.

**IMAGE**
```
Use the attached reference images for Afi and the bedroom: same face, same satin bonnet and nightdress, same room.
Close-up: Afi turns her face toward Koffi (off-screen) with a cold half-smile, one eyebrow raised.
Cinematic vertical film still, 9:16. Shot on a 35mm lens at f/1.8, shallow depth of field, subtle film grain, Kodak Vision3 500T color. Low-key night lighting: the cold blue-white glow of a smartphone, warm amber light from the bedside lamp, faint blue moonlight through the louvers, deep shadows. Realistic skin texture, natural West African features. No text, no captions, no watermark.
```

**ANIMATION**
```
Close-up. Afi leans toward her husband (off-screen) and says slowly and coldly, in a warm, slightly husky female voice, speaking French with a West African accent from Benin: "Et lui, au moins... il travaille."
She raises an eyebrow and stays silent.
Ambient noise: a ceiling fan humming, crickets outside. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P10 bis · La moustiquaire (bonus, facultatif) · garder 2 s
Koffi s'effondre sur le lit, la moustiquaire lui tombe dessus comme un voile de mariée. **IMAGE** : celle de P08.

**ANIMATION**
```
Medium shot. Koffi slowly falls backward onto the bed as if his heart has just broken, and the white mosquito net comes loose and slowly falls over him like a bridal veil. Slow, tragic, completely serious.
No dialogue. Ambient noise: a ceiling fan humming, crickets outside. Audio: only the room sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P11 · « Waaaah ! » · garder 1,5 s
**IMAGE** : R4 telle quelle.

**ANIMATION**
```
Static shot. The four neighbors at the window react to an outrageous insult and all cry out together: "Waaaah !" The young man in the football jersey covers his mouth with his fist, the elderly woman shakes her head, the teenage girl slaps the bald man's shoulder.
Ambient noise: crickets, the night outside. Audio: only the voices and the night sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P11b · L'aparté : elle nous parle · garder 3 s · LE 4e MUR
Tout le monde se fige, sauf Afi, qui se tourne vers nous. Références : R1, R2, R3.

**IMAGE**
```
Use the attached reference images for Afi, Koffi and the bedroom: same faces, same satin bonnet, same clothes, same room.
Medium close-up: Afi sits in bed and looks straight into the camera lens with a mischievous half-smile, as if she knows someone is watching. Behind her, slightly out of focus, Koffi is frozen like a statue, mouth open, one hand on his heart.
Cinematic vertical film still, 9:16. Shot on a 35mm lens at f/1.8, shallow depth of field, subtle film grain, Kodak Vision3 500T color. Low-key night lighting: the cold blue-white glow of a smartphone, warm amber light from the bedside lamp, faint blue moonlight through the louvers, deep shadows. Realistic skin texture, natural West African features. No text, no captions, no watermark.
```

**ANIMATION**
```
Medium close-up. Afi breaks the fourth wall: she slowly turns her face to the camera, looks straight into the lens and says to the viewer with a mischievous smile, in a warm, slightly husky female voice, speaking French with a West African accent from Benin: "Toi aussi, tu crois que c'est un homme ?"
Behind her, Koffi stays completely frozen like a statue, mouth open, not moving at all. Then Afi turns back toward her husband. Only Afi speaks in this shot.
Ambient noise: a ceiling fan humming, crickets outside. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

### Acte 3 · le néon (lumière plate)

#### P12 · Le néon · garder 2,5 s · PREMIÈRE ET DERNIÈRE IMAGE
Références : R1, R2, R3. Deux images : A (dans le noir) puis B (au néon), B faite **en modifiant A**.

**IMAGE A (première image)**
```
Use the attached reference images for Afi, Koffi and the bedroom: same faces, same satin bonnet, same clothes, same room.
Wide shot, static and centered: the dark bedroom at night. Koffi stands by the door in his white undershirt and waist cloth, holding Afi's glowing phone in one hand, his other hand on the light switch. Afi sits in bed in the background. Above the door, the fluorescent tube light is switched off.
Cinematic vertical film still, 9:16. Shot on a 35mm lens at f/1.8, subtle film grain, Kodak Vision3 500T color. Low-key night lighting: the cold blue-white glow of a smartphone, warm amber light from the bedside lamp, faint blue moonlight through the louvers, deep shadows. Realistic skin texture, natural West African features. The phone screen always faces away from the camera. No text, no captions, no watermark.
```

**IMAGE B (dernière image : joindre A et la modifier)**
```
Edit the attached image. Keep exactly the same framing, the same room, the same poses, the same faces and clothes.
Change only the light: the fluorescent tube above the door is now switched on. Flat, harsh, cold white fluorescent light floods the whole room, almost no shadows, slightly greenish, banal and unflattering like a low-budget sitcom. Koffi and Afi squint in the sudden light. The stacks of folded wax-print fabrics and the delivery bag on the door are now clearly visible.
No text, no captions, no watermark.
```

**ANIMATION** (Frames to Video : A en première image, B en dernière)
```
Static wide shot. Koffi slaps the light switch. SFX: a loud plastic switch click, then the fluorescent tube flickers twice with a tinkling sound and buzzes on. The room goes from dark cinematic night light to flat, harsh fluorescent light. Afi squints and shields her eyes with her hand.
No dialogue. Ambient noise: the steady buzz of the neon tube. Audio: no music. No subtitles, no captions, no on-screen text.
```

#### P13 · « Des pagnes ? » · garder 3 s
Références : R2, R3.

**IMAGE**
```
Use the attached reference images for Koffi and the bedroom: same face, same undershirt and waist cloth, same room.
Medium shot: Koffi stands in the middle of the room in his white undershirt and waist cloth, holding the phone with both hands close to his face (the screen faces him, we only see the back of the phone), frowning, confused. Behind him, stacks of folded wax-print fabrics.
Vertical film still, 9:16. Static, centered, symmetrical framing. Flat, harsh, cold white fluorescent light from the neon tube on the wall, almost no shadows, slightly greenish, banal and unflattering like a low-budget sitcom. The stacks of folded wax-print fabrics and the delivery bag on the door are clearly visible. Realistic skin texture, natural West African features. The phone screen always faces away from the camera. No text, no captions, no watermark.
```

**ANIMATION**
```
Static medium shot under flat fluorescent light. Koffi scrolls on the phone with his thumb; his angry face slowly turns into total confusion. He looks up and says, completely lost, in a deep, raspy male voice, speaking French with a West African accent from Benin: "... Des pagnes ? C'est quoi ça ?"
Ambient noise: the steady buzz of the neon tube, crickets outside. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P14 · « Ma boutique dans le téléphone » · garder 4,5 s
Références : R1, R3.

**IMAGE**
```
Use the attached reference images for Afi and the bedroom: same face, same satin bonnet and nightdress, same room.
Medium shot: Afi sits very straight in the bed, arms crossed, chin up, dignified like a queen, satin bonnet on.
Vertical film still, 9:16. Static, centered, symmetrical framing. Flat, harsh, cold white fluorescent light from the neon tube on the wall, almost no shadows, slightly greenish, banal and unflattering like a low-budget sitcom. The stacks of folded wax-print fabrics and the delivery bag on the door are clearly visible. Realistic skin texture, natural West African features. No text, no captions, no watermark.
```

**ANIMATION**
```
Static medium shot under flat fluorescent light. Afi, arms crossed and chin up, says calmly and proudly, in a warm, slightly husky female voice, speaking French with a West African accent from Benin: "Mon catalogue. Ma boutique dans le téléphone. Il vend même quand je dors."
Then she stares at her husband without blinking.
Ambient noise: the steady buzz of the neon tube, crickets outside. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

### Acte 4 · le décalage (lumière plate)

#### P15 · « Il livre aussi ? » · garder 2 s
Références : R2, R3.

**IMAGE**
```
Use the attached reference images for Koffi and the bedroom: same face, same undershirt and waist cloth, same room.
Medium close-up: Koffi holds the phone against his belly with both hands, humbled, shoulders low, eyes down like a scolded child.
Vertical film still, 9:16. Static, centered, symmetrical framing. Flat, harsh, cold white fluorescent light from the neon tube on the wall, almost no shadows, slightly greenish, banal and unflattering like a low-budget sitcom. Realistic skin texture, natural West African features. The phone screen always faces away from the camera. No text, no captions, no watermark.
```

**ANIMATION**
```
Static medium close-up under flat fluorescent light. A long silence. Koffi swallows, then asks in a tiny, humble voice, the same deep, raspy male voice but very soft, speaking French with a West African accent from Benin: "... Il livre aussi ?"
Ambient noise: the steady buzz of the neon tube, a cricket outside. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P16 · Le casque · garder 3 s · 3 À 4 PRISES (objet passé de main en main)
Références : R1, R2, R3.

**IMAGE**
```
Use the attached reference images for Afi, Koffi and the bedroom: same faces, same satin bonnet, same clothes, same room.
Medium two-shot: Afi sits in bed and holds out a black motorcycle helmet toward Koffi at arm's length; Koffi stands beside the bed and stares at the helmet.
Vertical film still, 9:16. Static, centered, symmetrical framing. Flat, harsh, cold white fluorescent light from the neon tube on the wall, almost no shadows, slightly greenish, banal and unflattering like a low-budget sitcom. The stacks of folded wax-print fabrics and the delivery bag on the door are clearly visible. Realistic skin texture, natural West African features. No text, no captions, no watermark.
```

**ANIMATION**
```
Static two-shot under flat fluorescent light. Afi holds out the motorcycle helmet and says flatly, in a warm, slightly husky female voice, speaking French with a West African accent from Benin: "Non. Ça, c'est toi."
Koffi slowly takes the helmet with both hands, then turns his head and stares straight into the camera, deadpan. Only Afi speaks in this shot.
Ambient noise: the steady buzz of the neon tube, crickets outside. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P17 · Le lien · garder 2,5 s
**IMAGE** : R5 telle quelle.

**ANIMATION**
```
Static shot under flat fluorescent light. The elderly woman in the orange headwrap waves her phone at the window and shouts, excited, in a high-pitched old woman's voice, speaking French with a West African accent from Benin: "Afi ! Envoie-moi le lien !"
The three other neighbors raise their phones and nod eagerly. Only the elderly woman speaks.
Ambient noise: the buzz of a neon tube, crickets outside. Audio: only the dialogue and the night sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P18 · « On me paie combien ? » · garder 2,5 s
Références : R1, R2, R3.

**IMAGE**
```
Use the attached reference images for Afi, Koffi and the bedroom: same faces, same satin bonnet, same clothes, same room.
Medium two-shot: Koffi stands beside the bed wearing the black motorcycle helmet with the visor up, looking at Afi with hope; Afi sits in bed and looks back at him, unimpressed.
Vertical film still, 9:16. Static, centered, symmetrical framing. Flat, harsh, cold white fluorescent light from the neon tube on the wall, almost no shadows, slightly greenish, banal and unflattering like a low-budget sitcom. The stacks of folded wax-print fabrics and the delivery bag on the door are clearly visible. Realistic skin texture, natural West African features. No text, no captions, no watermark.
```

**ANIMATION**
```
Static two-shot under flat fluorescent light. Koffi, wearing the helmet with the visor up, asks hopefully, in a deep, raspy male voice, speaking French with a West African accent from Benin: "Et moi, on me paie combien ?"
Then he waits. Afi does not answer. Only Koffi speaks in this shot.
Ambient noise: the steady buzz of the neon tube, crickets outside. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P19 · « Dors. » · garder 2 s
**IMAGE** : celle de P18 (même cadre, la suite immédiate).

**ANIMATION**
```
Static two-shot under flat fluorescent light. Afi lies back down, turns her back to her husband and says flatly, without even looking at him, in a warm, slightly husky female voice, speaking French with a West African accent from Benin: "Dors."
She pulls the sheet up over her shoulder. Koffi stands frozen beside the bed, helmet on. Only Afi speaks in this shot.
Ambient noise: the steady buzz of the neon tube, crickets outside. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

#### P20 · « Et toi ? » : elle nous parle encore · garder 3 s · LE 4e MUR, L'APPEL
Elle s'est recouchée face à nous. Références : R1, R2, R3.

**IMAGE**
```
Use the attached reference images for Afi, Koffi and the bedroom: same faces, same satin bonnet, same clothes, same room.
Close-up: Afi lies in bed on her side, her head on the pillow, facing the camera, and looks straight into the lens, calm and amused. Behind her, out of focus, Koffi still stands beside the bed with the motorcycle helmet on.
Vertical film still, 9:16. Static, centered, symmetrical framing. Flat, harsh, cold white fluorescent light from the neon tube on the wall, almost no shadows, slightly greenish, banal and unflattering like a low-budget sitcom. Realistic skin texture, natural West African features. No text, no captions, no watermark.
```

**ANIMATION**
```
Close-up under flat fluorescent light. Afi, lying on her pillow, looks straight into the camera lens and speaks directly to the viewer, calm and amused, in a warm, slightly husky female voice, speaking French with a West African accent from Benin: "Et toi ? Ta boutique, elle dort quand tu dors ?"
Then she raises an eyebrow and keeps looking at the viewer. Behind her, out of focus, Koffi does not move. Only Afi speaks in this shot.
Ambient noise: the steady buzz of the neon tube, crickets outside. Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.
```

---

## 5. Le montage (la part de Claude)

Mongazi dépose une prise par plan dans `_partage/pub-l-autre/`, nommée par son numéro (`P01.mp4`…), téléchargée en
1080p, son de Veo compris. Je la range dans le studio, hors dépôt (`_studio-video/public/`).

### Le minutage (environ 1 min)

| Plan | Garder | Fin à |
|---|---|---|
| P01 | 2 s | 0:02 |
| P02 | 2 s | 0:04 |
| P03 | 2 s | 0:06 |
| P04 | 3 s | 0:09 |
| P05 | 3,5 s | 0:12,5 |
| P06 | 2 s | 0:14,5 |
| P07 | 1,5 s | 0:16 |
| P08 | 2 s | 0:18 |
| P09 | 5 s | 0:23 |
| P10 | 2,5 s | 0:25,5 |
| (P10 bis) | (2 s) | (facultatif) |
| P11 | 1,5 s | 0:27 |
| P11b · à nous | 3 s | 0:30 |
| P12 | 2,5 s | 0:32,5 |
| P13 | 3 s | 0:35,5 |
| P14 | 4,5 s | 0:40 |
| P15 | 2 s | 0:42 |
| P16 | 3 s | 0:45 |
| P17 | 2,5 s | 0:47,5 |
| P18 | 2,5 s | 0:50 |
| P19 | 2 s | 0:52 |
| P20 · à nous | 3 s | 0:55 |
| noir + « clac » | 0,5 s | 0:55,5 |
| carte | 4 s | 0:59,5 |

### Le son

- **Musique 1, de P01 à P11** : cordes ou piano de mélodrame, très sérieux.
- **Coupure sèche au « clac » du néon (P12)** : plus de musique, seulement le bourdonnement du néon jusqu'à P20. Ce
  silence est la blague.
- **P11b, l'aparté** : l'image et la musique se figent, seule Afi bouge ; la musique repart quand elle se retourne
  vers Koffi, juste avant le néon.
- Après « Et toi ? » (P20) : noir, et on entend seulement Koffi éteindre la lumière (« clac »). Puis la carte.
- **Musique 2 sur la carte** : un afrobeat léger et joyeux. Les deux musiques depuis Pixabay, lien de la page gardé.
- Voix nettoyées et égalisées, −14 LUFS, crête à −1 dBTP.

### Texte et dessins, plan par plan

| Plan | Ce que j'ajoute |
|---|---|
| P01 | « 3 h 14 » en chiffres de radio-réveil, en haut à gauche |
| P02 | zoom sec sur les yeux de Koffi · « ?! » dessiné au-dessus de sa tête |
| P04 | trois bulles de notification qui sortent de la poitrine d'Afi |
| P05 | « DEPUIS TROIS MOIS » en très gros, un mot par coup de tambour |
| P06 | léger ralenti · un cœur dessiné qui se fissure · arrêt sur image : « KOFFI · le mari · n'a rien vu venir » |
| P07 | arrêt sur image : « LES VOISINS · ne dorment jamais non plus » |
| P09 | les doigts d'Afi comptés à l'écran : 1, 2, 3 |
| P10 | la phrase tombe lettre par lettre · coup de cymbale |
| P11 | « WAAAH » en onomatopée de bande dessinée |
| P11b | tout se fige et grisonne, sauf Afi · un petit « ⏸ » en coin · son sous-titre plus gros : elle nous parle |
| P12 | « CLAC » · flash blanc · la musique se coupe net |
| P13 | un cercle rouge dessiné sur les piles de pagnes et le sac de livraison |
| P14 | « MA BOUTIQUE DANS LE TÉLÉPHONE » plein écran |
| P15 | sa réplique en lettres minuscules, comme sa voix |
| P16 | arrêt sur image sur son regard caméra : « KOFFI · livreur depuis 3 h 16 » |
| P17 | une pluie de bulles de notification |
| P18 | un « ? » qui clignote au-dessus du casque |
| P19 | des « Zzz » dessinés au-dessus d'elle |
| P20 | elle nous regarde : sous-titre plus gros · puis noir, « clac », la carte |

**Sous-titres** : toutes les répliques, gros, blancs cernés de noir, dans le tiers haut de l'image.

---

## 6. La carte de fin (4 s)

TikTok, Reels, statut WhatsApp (on tutoie) :

> **Ton catalogue vend même quand tu dors.**
> Catalogue digital : 50 000 F
> Une pub comme ça pour ton commerce ? On la fait aussi.
> NEBULA Agency · WhatsApp +229 96 74 07 32

Facebook (on vouvoie) : « Votre catalogue vend même quand vous dormez. » · « Une pub comme ça pour votre commerce ? On
la fait aussi. »

⚠️ Le numéro est celui du site (`wa.me/22996740732`). À 10 chiffres, il s'écrit 01 96 74 07 32 : à Mongazi de choisir
la forme affichée. Le lien du site, lui, ne change pas.

---

## 7. La version courte (30 s)

P02 · P03 · P05 · P09 (ses deux premières phrases) · P12 · P13 · P14 · P16 · P20 · la carte. Pour les statuts
WhatsApp.

---

## 8. La publication

**Légende** :
```
3 h 14 du matin. Elle sourit à son téléphone. Lui, il dort plus.
Regarde jusqu'à la fin.

#cotonou #benin #229 #couple #commerce
```

**Commentaire épinglé** (il prolonge l'histoire) : « Pour la tantie qui veut le lien : www.nebula-agency.online »

**L'étiquette IA** : TikTok et Facebook demandent de cocher « contenu généré par IA » pour une vidéo réaliste faite par
IA, sinon ils peuvent la retirer. C'est une petite mention sous la vidéo, pas dans l'image : elle ne casse pas
l'histoire. (À trancher par Mongazi, cf. `../cerveau.md` règle 5.)

---

## 9. Ce qui attend

- [ ] 🙋 Le plan d'essai P02 : la voix, l'accent, les lèvres
- [ ] 🙋 Relire les répliques (§ 1)
- [ ] 🙋 La forme du numéro sur la carte (§ 6)
- [ ] 🤖 Choisir les deux musiques (Pixabay) et les faire écouter
- [ ] 🤖 Le montage, dès que les prises sont dans `_partage/pub-l-autre/`
- [ ] 💡 Bonus : le lien que réclame la tantie pourrait mener à un vrai catalogue de démonstration, « Afi Pagnes »,
  avec de vraies photos de vrais pagnes (jamais des pagnes générés).

# LE POST DU JOUR · un message, trois mondes

> **Le principe.** Le même jour, la même idée, sur trois canaux qui n'ont rien à voir.
> Ce n'est pas le même visuel redimensionné trois fois : c'est **trois objets différents**,
> parce qu'on ne lit pas de la même façon un fil Instagram, un statut WhatsApp et un
> carrousel TikTok. Recadrer un post carré en 9:16, ça se voit, et ça dit au lecteur qu'on
> ne l'a pas regardé.
>
> **Ce qui ne change jamais entre les trois :** le label « LE SAVIEZ-VOUS ? » et l'idée du
> jour. Tout le reste change, y compris la façon de s'adresser au lecteur.
>
> **WhatsApp : 1 image. TikTok : 3 images.** Instagram et Facebook : 3 images, dans
> `PROMPTS-CARROUSELS.md`.
>
> Message du 2026-08-04 : *sur internet, introuvable ne veut pas dire discret.*
> Version 2.0 · 2026-08-04

---

## 1. Les trois mondes

| | Instagram / Facebook | WhatsApp | TikTok |
|---|---|---|---|
| **Format** | 4:5, 1080 x 1350 | 9:16, 1080 x 1920 | 9:16, 1080 x 1920 |
| **Nombre d'images** | 3 (carrousel) | **1 (statut)** | **3 (carrousel photo)** |
| **Direction** | MARBRE & ROUGE | **NUIT CINÉMA** | **AFFICHE FLUO** |
| **Matière** | papier imprimé, sculpture | noir profond, une seule source de lumière | aplats saturés, découpe nette, trame |
| **Ambiance** | musée, froid, silencieux | cinéma, nocturne, dramatique | affiche de rue, loud, premium |
| **Registre** | **vous** | **vous** | **tu** |
| **Temps de lecture** | 8 secondes | 2 secondes | 1 seconde par image |
| **L'action demandée** | aimer, s'abonner | **répondre au statut** | s'abonner, liker |
| **Le prompt** | `PROMPTS-CARROUSELS.md` | §4 de ce document | §5 de ce document |

**Le registre change, pas seulement le décor.** On vouvoie sur Instagram et sur WhatsApp,
on tutoie sur TikTok. C'est ce qui fait que le post TikTok n'a pas l'air d'un post
Instagram recyclé, avant même de regarder les couleurs.

### Ce qui a changé en version 2.0

| | Version 1 | Version 2 |
|---|---|---|
| WhatsApp | typographie seule sur du noir, une barre de recherche en fil de fer | **un vrai plan de cinéma** : un téléphone dressé dans le noir, son écran seule source de lumière, un faisceau volumétrique, et le mot posé dans le faisceau |
| TikTok | photocopie, papier déchiré, scotch | **affiche graphique** : aplats saturés, main découpée nette, trame de points, ombre portée dure, typo condensée énorme, un accent chromé |

La version 1 était juste, mais elle n'était pas belle. Un statut nu ressemble à une carte
de citation, et une photocopie déchirée ressemble à un fanzine : ni l'un ni l'autre ne
donne envie d'acheter un site à quelqu'un.

---

## 2. L'ordre des pièces jointes

**Image 1 = la référence de style. Image 2 = le logo NEBULA.**
Tous les prompts de ce document sont écrits dans cet ordre.

⚠️ **La mise en garde du prompt-maître (2026-07-30) disait l'inverse** : logo en premier,
référence en second, sinon le modèle prend le logo pour un modèle de style et la marque
disparaît. Comme on inverse l'ordre, **chaque prompt de ce document commence par un bloc
anti-confusion** qui nomme les deux rôles deux fois. Si malgré ça le logo se fait
réinterpréter, remettre le logo en premier et échanger les mots « IMAGE 1 » et « IMAGE 2 »
dans le prompt.

**Choisir une référence différente par canal.** C'est là que se joue l'écart entre les
trois. Une seule et même référence envoyée trois fois donnera trois images cousines, quoi
qu'en dise le prompt.

| Canal | Le genre de référence à envoyer |
|---|---|
| Instagram / Facebook | page de magazine imprimé, papier clair, sculpture, une couleur d'accent |
| WhatsApp | photo de nuit, une seule source de lumière, faisceau visible, grain de film |
| TikTok | affiche graphique, aplats saturés, découpe nette, trame, typo énorme |

Si aucune référence n'est sous la main, chaque prompt contient un bloc **DIRECTION DE
SECOURS** à coller : le modèle s'en sert quand la référence ne répond pas à la question.

---

## 3. Les zones mortes, canal par canal

C'est le détail qui fait rater un post qui était bon. L'interface du réseau vient se poser
**par-dessus** l'image, et elle mange toujours les mêmes endroits.

**WhatsApp, statut 1080 x 1920 :**
- les **220 premiers pixels** en haut : photo de profil, nom, heure
- les **340 derniers pixels** en bas : le champ « Répondre »
- rien d'important en dehors de la bande centrale

**TikTok, carrousel photo 1080 x 1920 :**
- les **480 derniers pixels** en bas : la légende, le pseudo, le son, la barre de lecture
- les **240 pixels de droite** : les boutons cœur, commentaire, partage, profil
- la zone sûre est donc un rectangle **décalé vers le haut et vers la gauche**

Un titre centré verticalement sur TikTok se retrouve à moitié derrière les boutons. C'est
la faute la plus courante, et elle ne se voit qu'une fois le post publié.

---

## 4. WhatsApp · **1 image** · direction « NUIT CINÉMA »

### Ce que fait ce statut

Sur WhatsApp, on ne parle pas à des inconnus : on parle à des gens qui ont déjà le numéro.
Donc on ne demande pas un abonnement, **on demande une réponse**. Un statut qui obtient une
réponse ouvre une conversation, et une conversation vaut mille vues.

**Le parti pris visuel :** un seul objet, une seule source de lumière, et beaucoup de noir.
Le téléphone éclaire, le reste disparaît. C'est un plan de film, pas une diapositive.

**Peu de mots.** Cinq lignes au total, dont une seule est grosse. Un statut se regarde en
deux secondes : chaque phrase en plus retire du style à celles qui restent.

⚠️ **La promesse doit être tenue.** Le statut propose de faire le test gratuitement pour
celui qui répond. Ça prend dix secondes par personne : taper le nom de son commerce et lui
envoyer la capture. Si on ne compte pas le faire, retirer cette ligne.

### PROMPT · statut WhatsApp

```
===========================================================
NEBULA AGENCY — WHATSAPP STATUS — ONE IMAGE, 9:16
===========================================================

ATTACHED INPUTS — two attachments, two different roles.
Read this block twice. Swapping the two roles ruins the image.

  IMAGE 1 = THE STYLE REFERENCE.
     Study it and inherit its DESIGN LANGUAGE and its COLOUR PALETTE:
     composition grid, type hierarchy, weight contrast, letter-spacing,
     spacing rhythm, texture, lighting, level of finish and density.
     Take NOTHING else from it: not its subject, not its imagery, not
     its words, not its numbers, not its logo, not its brand.
     If any of its content appears in the output, the image has failed.

  IMAGE 2 = THE LOGO.
     The official NEBULA Agency logo. It is an ASSET TO PLACE, exactly
     as provided. Never a style reference. Never a subject to
     reinterpret. Never redrawn, restyled, recoloured, cropped,
     rotated, or completed with a wordmark of your own.

  To be explicit: the STYLE comes from IMAGE 1. The LOGO is IMAGE 2.

-----------------------------------------------------------
TASK
-----------------------------------------------------------
Create ONE original WhatsApp status image for NEBULA Agency, a digital
studio in Cotonou, Benin, serving West African merchants.
It is read in TWO SECONDS, at night, on a phone held in one hand.
It must look expensive: a cinematic still, not a quote card.

-----------------------------------------------------------
INTENT — "NUIT CINÉMA", use this to settle anything IMAGE 1
           does not answer
-----------------------------------------------------------
One object. One light source. A great deal of darkness.
  - a deep, rich, matte black space with no visible background
  - the ONLY light in the entire image comes from the phone screen
    at the centre. Everything else is lit by that light or not lit
    at all. No second lamp, no rim light from nowhere, no ambient fill.
  - a wide VOLUMETRIC CONE of light rises from the screen into the
    dark, with fine dust suspended in the beam
  - a soft reflection of the phone and its glow on the dark surface
    it stands on
  - fine cinematic film grain over the whole frame
  - ONE accent colour only: the colour of the screen light. It lights
    the beam, the reflection, and the huge word. Nothing else is
    coloured.
It should feel photographed with a fast lens in a dark room, not
rendered and not illustrated.

MUST NOT look like: a flat quote card, plain text on a black square,
a printed magazine page, a paper texture, a collage, a marble
sculpture, a neon cyberpunk street, a cluttered infographic, a
3D product render on a studio backdrop.

-----------------------------------------------------------
FORMAT AND SAFE ZONES — a hard requirement
-----------------------------------------------------------
Canvas: 1080 x 1920 px, vertical 9:16.
WhatsApp draws its own interface OVER this image:
  - the TOP 220 px are covered by the profile bar
  - the BOTTOM 340 px are covered by the reply field
Nothing that matters may sit in those two strips. All text, the logo
and the phone live inside the central band, between 220 px and
1580 px from the top.

-----------------------------------------------------------
THE HERO IMAGE (the largest zone, centre of the canvas)
-----------------------------------------------------------
A single modern smartphone standing upright on a dark reflective
surface, seen slightly from the side in three-quarter view, tilted a
few degrees, photographed close.
On its screen: a search field with a single blinking cursor and NO
readable text, and under it a completely EMPTY result area. Two or
three faint unfinished placeholder lines fade out and stop. The
screen is mostly empty, and that emptiness is the subject.
From the screen, a wide cone of light opens upward into the darkness,
volumetric, with dust motes drifting inside it.
No hand, no face, no person, no app frame, no visible brand or logo
on the device, no icons, no notification badges.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (top of the safe band, small, uppercase, widely letter-spaced,
       dim grey, discreet): "LE SAVIEZ-VOUS ?"

HOOK LINE (just above the phone, small, clean sans-serif, soft white):
  "Ils ont cherché votre commerce."

HUGE WORD (sitting INSIDE the cone of light, as if written by the
           light itself, by far the loudest element of the image,
           condensed, all caps, in the accent colour, glowing softly):
  "RIEN."

CLOSING LINE (under the huge word, clean sans-serif, soft white):
  "C'est ce qu'ils ont trouvé."

CALL TO ACTION (bottom of the safe band, slightly set apart, in the
                accent colour, smaller than the huge word):
  "Répondez « TEST » : je regarde pour vous."
  Keep the French guillemets « » exactly as written, with their inner
  spaces.

FOOTER: the logo from IMAGE 2, centred, small, about 14% of canvas
width, placed just ABOVE the 340 px bottom safe strip, never inside
it. Keep it quiet: it must not compete with the light.

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Inside the central safe band, top to bottom:
  1. LABEL
  2. HOOK LINE
  3. THE PHONE AND ITS CONE OF LIGHT     <- the largest zone by far
  4. "RIEN."   (inside the cone)
  5. CLOSING LINE
  6. CALL TO ACTION
  7. LOGO
Wide margins left and right. Five text elements in total and only one
of them is large: the image must breathe, the reader has two seconds.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM: no translation, no rephrasing, no added
  punctuation, no exclamation marks.
- Correct French diacritics and apostrophes: "cherché", "C'est".
- "RIEN." must be readable at 20% of the image size.
- No readable text on the phone screen. No hashtag, no social icon,
  no interface element, no emoji.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO invented statistics, percentages or figures of any kind.
- NO human faces, no hands, no people, no recognisable third-party
  brand, app name or interface.
- NO watermark, no signature, no frame, no border.
- ONE single idea in this image.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1920 image, publication-ready,
high-fidelity text rendering, cinematic quality.
===========================================================
```

**DIRECTION DE SECOURS**, à coller sous le bloc INTENT si la référence ne suffit pas :

```
FALLBACK ART DIRECTION, use only where IMAGE 1 is silent:
  darkness     rich matte black #060608, no visible background
  screen light one cold luminous white-cyan #BFF4FF, and the beam it
               casts, slightly warmer at its edges
  accent       the same screen light, used for "RIEN." and the call
               to action, nothing else
  text         soft white #F2F4F6 for the two short lines,
               dim grey #6B7280 for the label
  Exactly these values. No second colour, no gradient background,
  no neon signage.
```

### Le texte à écrire sous le statut

WhatsApp permet d'ajouter une légende. Une phrase, pas plus :

```
Tapez le nom de votre commerce dans votre téléphone. Ça prend dix secondes.
Répondez TEST et je le fais pour vous.
```

### Le message pour la liste de diffusion

Le statut se regarde, la liste de diffusion se lit. Deux textes différents, envoyés le
même soir.

```
Bonjour, une question rapide.

Tapez le nom de votre commerce dans votre téléphone, maintenant.
Ce que vous voyez à l'écran, c'est exactement ce que voient vos clients
quand ils vous cherchent le soir.

Si vous ne trouvez rien, ce n'est pas grave : ça se règle.
Répondez TEST et je regarde pour vous, gratuitement.

Mongazi · NEBULA Agency
nebula-agency.online
```

⚠️ **Liste de diffusion, pas groupe.** Un groupe met tout le monde en copie et fait fuir.
Une liste de diffusion arrive comme un message personnel, et seuls ceux qui ont votre
numéro enregistré le reçoivent.

---

## 5. TikTok · **3 images** · direction « AFFICHE FLUO »

### Ce que fait ce carrousel

TikTok ne pardonne pas la première image : c'est elle qui passe dans le fil, et c'est elle
seule qui décide si on glisse. Quatre mots maximum, énormes, et on tutoie.

**Le parti pris visuel :** une affiche, pas un collage. Aplat de couleur saturée, une main
découpée au couteau qui tient un téléphone, une ombre portée dure et graphique, une trame
de points, et une typographie condensée gigantesque. Loud, mais dessiné.

**Le fil rouge des trois images :** c'est le même téléphone, tenu de la même façon, et
seul son écran change. L'écran vide, puis l'écran occupé par quelqu'un d'autre, puis
l'écran occupé par toi. On comprend l'histoire sans lire.

Le carrousel photo tourne en boucle avec un son. L'aplat revient à sa couleur de départ
sur la troisième image, pour que la boucle se referme proprement.

### PROMPT · TikTok image 1 sur 3

```
===========================================================
NEBULA AGENCY — TIKTOK PHOTO CAROUSEL — SLIDE 1 OF 3
===========================================================

ATTACHED INPUTS — two attachments, two different roles.
Read this block twice. Swapping the two roles ruins the image.

  IMAGE 1 = THE STYLE REFERENCE.
     Inherit its DESIGN LANGUAGE and its COLOUR PALETTE: composition,
     type hierarchy, weight contrast, texture, level of finish.
     Take NOTHING else: not its subject, not its imagery, not its
     words, not its logo, not its brand.

  IMAGE 2 = THE LOGO.
     The official NEBULA Agency logo. An ASSET TO PLACE exactly as
     provided. Never a style reference, never redrawn or recoloured.

  To be explicit: the STYLE comes from IMAGE 1. The LOGO is IMAGE 2.

-----------------------------------------------------------
TASK
-----------------------------------------------------------
Create SLIDE 1 of a 3-slide TikTok photo carousel for NEBULA Agency, a
digital studio in Cotonou, Benin, serving West African merchants.
This slide is the cover. It has ONE second to stop a thumb.
It must look designed and expensive, never cheap and never homemade.

-----------------------------------------------------------
INTENT — "AFFICHE FLUO", use this to settle anything IMAGE 1
           does not answer
-----------------------------------------------------------
A graphic poster, loud and crafted:
  - ONE flat saturated colour field filling the whole canvas, edge to
    edge, no gradient and no photographic background
  - ONE cut-out photographic element, knife-sharp, sitting on that
    field with a HARD flat graphic drop shadow offset in one direction
  - a halftone dot texture used deliberately in one or two areas, as
    a designed element and not as noise
  - ENORMOUS condensed sans-serif type, tight tracking, set on a
    slight diagonal or hard left-aligned, overlapping the cut-out
    element so that type and image share the same plane
  - one small chrome or metallic accent, a single element, no more
  - clean edges everywhere: this is printed, trimmed and pinned up
Bold, young, confident. Expensive-looking, not raw.

MUST NOT look like: a torn photocopy, a fanzine, sticky tape and
scissors, a clean corporate layout, a printed luxury magazine page, a
marble sculpture, a dark cinematic still, a 3D studio render.

-----------------------------------------------------------
FORMAT AND SAFE ZONES — a hard requirement
-----------------------------------------------------------
Canvas: 1080 x 1920 px, vertical 9:16.
TikTok draws its own interface OVER this image:
  - the BOTTOM 480 px are covered by the caption, the username and
    the progress bar
  - the RIGHT 240 px are covered by the action buttons
Nothing that matters may sit in those two strips. The live area is a
rectangle pushed UP and to the LEFT. The huge headline sits in the
upper half, left-aligned.

-----------------------------------------------------------
THE HERO IMAGE
-----------------------------------------------------------
A cut-out photograph of a single hand holding a modern smartphone
upright, cropped at the wrist, knife-sharp edges, oversized, tilted a
few degrees, placed in the lower-middle of the live area.
A hard flat graphic shadow sits behind it, offset, in a darker shade
of the colour field.
On the screen: a search field and an EMPTY result area, two or three
faint unfinished placeholder lines, and nothing else. No readable
text, no app frame, no icons, no brand on the device.
The hand is a hand only: no face, no arm beyond the wrist, no person.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (small, top-left, uppercase, widely letter-spaced, inside a
       thin rectangular outline): "LE SAVIEZ-VOUS ?"

HEADLINE (upper half, left-aligned, ENORMOUS condensed sans-serif in
          all caps, two stacked lines, filling the live width, tight
          tracking, overlapping the top of the cut-out element, the
          loudest thing on the canvas by a wide margin):
  "TU N'EXISTES PAS"

SUB-LINE (immediately under the headline, much smaller, same family,
          regular weight, on a short solid bar of the accent colour):
  "sur internet, en tout cas."

SWIPE CUE (left side, below the sub-line, small, uppercase,
           letter-spaced): "GLISSE" followed by a solid triangular
           arrow pointing right.

FOOTER: the logo from IMAGE 2, small, about 12% of canvas width,
bottom-LEFT, placed just ABOVE the 480 px bottom safe strip and well
clear of the 240 px right strip.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM. No translation, no rewording.
- Correct French apostrophe in "N'EXISTES".
- The headline must be readable at 20% of the image size.
- No readable text on the phone screen. No hashtag, no social icon,
  no interface element, no emoji, no TikTok logo, no play button.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO invented statistics, percentages or figures.
- NO human faces, no people beyond a single hand, no recognisable
  third-party brand.
- NO watermark, no frame, no border.
- ONE single idea in this image.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1920 image, publication-ready,
high-fidelity text rendering, poster-grade finish.
===========================================================
```

### PROMPT · TikTok image 2 sur 3

```
===========================================================
NEBULA AGENCY — TIKTOK PHOTO CAROUSEL — SLIDE 2 OF 3
===========================================================

ATTACHED INPUTS — three attachments, three different roles:

  IMAGE 1 = THE STYLE REFERENCE. Design language and palette only.
            Its subject and its words never appear.
  IMAGE 2 = THE LOGO. An asset to place exactly as provided,
            never a style reference, never redrawn.
  IMAGE 3 = SLIDE 1 OF THIS CAROUSEL, generated just before.
            The CONSISTENCY REFERENCE.

-----------------------------------------------------------
CONSISTENCY — the most important instruction of this prompt
-----------------------------------------------------------
Match IMAGE 3 exactly on: the cut-out hand and phone (same hand, same
grip, same angle, same size, same crop at the wrist), the hard flat
drop shadow and its offset direction, the halftone treatment, the type
family and weight, the label box, the margins and the safe zones.
Two things change, and only two:
  1. the flat colour field INVERTS to a deep saturated dark tone, with
     the type now in the light colour. That inversion is the reward
     for swiping.
  2. the phone screen: the empty result area is now occupied by ONE
     filled, glowing result block at the top, clearly showing that
     someone else is there. The rows beneath it stay empty.
Everything else is identical, so the two images read as one object.

-----------------------------------------------------------
FORMAT AND SAFE ZONES — identical to slide 1
-----------------------------------------------------------
1080 x 1920 px, 9:16. Bottom 480 px and right 240 px are covered by
the TikTok interface: nothing that matters goes there. Headline in the
upper half, left-aligned.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (same box, same place): "LE SAVIEZ-VOUS ?"

HEADLINE (upper half, left-aligned, ENORMOUS condensed caps, three
          stacked lines, tight tracking, filling the live width):
  "ON TROUVE"
  "QUELQU'UN"
  "D'AUTRE"

BODY (under the headline, much smaller, three short lines, the last
      one sitting on a solid bar of the accent colour):
  "Le téléphone ne répond jamais « rien »."
  "Il répond quelqu'un."
  "Et ce soir encore."
  Keep the French guillemets « » exactly as written.

FOOTER: the logo from IMAGE 2, bottom-left, same size and position as
slide 1, clear of both safe strips.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM. No translation, no rewording.
- Correct French apostrophes: "QUELQU'UN", "D'AUTRE".
- The headline must be readable at 20% of the image size.
- No readable text inside the glowing result block on the screen.
- No hashtag, no social icon, no emoji, no interface element.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO invented statistics, percentages or figures.
- NO human faces, no people beyond the same single hand, no
  recognisable third-party brand.
- NO watermark, no frame, no border. ONE single idea.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1920 image, publication-ready,
high-fidelity text rendering, poster-grade finish.
===========================================================
```

### PROMPT · TikTok image 3 sur 3

```
===========================================================
NEBULA AGENCY — TIKTOK PHOTO CAROUSEL — SLIDE 3 OF 3
===========================================================

ATTACHED INPUTS — three attachments, three different roles:

  IMAGE 1 = THE STYLE REFERENCE. Design language and palette only.
  IMAGE 2 = THE LOGO. An asset to place exactly as provided,
            never a style reference, never redrawn.
  IMAGE 3 = SLIDE 2 OF THIS CAROUSEL, generated just before.
            The CONSISTENCY REFERENCE.

-----------------------------------------------------------
CONSISTENCY — the most important instruction of this prompt
-----------------------------------------------------------
Match IMAGE 3 exactly on: the cut-out hand and phone, the hard flat
drop shadow and its offset, the halftone treatment, the type family
and weight, the label box, the margins and the safe zones.
Two things change:
  1. the flat colour field RETURNS to the bright one used on slide 1,
     so the carousel closes its loop when it repeats.
  2. the phone is raised slightly higher and held straighter, and on
     its screen the glowing result block at the top now contains a
     small bright storefront symbol: the shop is the one being found
     this time. The rows beneath stay empty.

-----------------------------------------------------------
FORMAT AND SAFE ZONES — identical to slides 1 and 2
-----------------------------------------------------------
1080 x 1920 px, 9:16. Bottom 480 px and right 240 px are covered by
the TikTok interface: nothing that matters goes there.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (same box, same place): "LE SAVIEZ-VOUS ?"

HEADLINE (upper half, left-aligned, ENORMOUS condensed caps, two
          stacked lines, tight tracking): "FAIS LE TEST"

BODY (under the headline, much smaller, two lines):
  "Tape le nom de ton commerce dans ton téléphone."
  "Ce que tu vois, tes clients le voient aussi."

CALL TO ACTION (two solid pill-shaped buttons side by side, drawn as
                flat graphic shapes in the accent colour with a hard
                offset shadow like everything else in this series,
                uppercase, tight letter-spacing):
  pill 1: "ABONNE-TOI"
  pill 2: "LIKE"
They are printed graphic shapes, never app buttons, never heart or
bell icons, never a screenshot of an interface.

FOOTER: the logo from IMAGE 2, bottom-left, same size and position as
slides 1 and 2, clear of both safe strips.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM. No translation, no rewording.
- Correct French diacritics: "téléphone".
- The headline must be readable at 20% of the image size.
- No hashtag, no social icon, no emoji, no heart, no bell, no
  interface element, no TikTok logo.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO invented statistics, percentages or figures.
- NO human faces, no people beyond the same single hand, no
  recognisable third-party brand.
- NO watermark, no frame, no border. ONE single idea.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1920 image, publication-ready,
high-fidelity text rendering, poster-grade finish.
===========================================================
```

**DIRECTION DE SECOURS TikTok**, à coller sous le bloc INTENT de l'image 1 :

```
FALLBACK ART DIRECTION, use only where IMAGE 1 is silent:
  slides 1 and 3   flat acid lime field #D8FF2E, near-black type
                   #0E0E0E, hard shadow in deep olive #4A5A00
  slide 2          flat deep ultramarine field #1A1AE6, bone-white
                   type #F4F4F0, hard shadow in navy #0A0A7A
  accent bars      hot magenta #FF2E88 on all three slides
  texture          black halftone dots, used in one or two areas only
  chrome           one small chrome element per slide, no more
  No gradient background, no glow, no soft shadow, no paper texture.
```

### La légende TikTok

```
Tape le nom de ton commerce dans ton téléphone. Là, maintenant.
Ce que tu vois, c'est exactement ce que voient tes clients.

Abonne-toi, on en remet une chaque semaine.

#cotonou #benin #229 #business #entrepreneur #commerce
```

### Le son

Prendre un son **qui monte dans les tendances**, pas un son déjà partout, et le laisser
bas. Sur un carrousel photo, le son ne raconte rien : il sert seulement à ne pas être
muet, parce qu'un carrousel muet est poussé moins loin.

---

## 6. Contrôles avant publication

| Contrôle | Canal | Pourquoi |
|---|---|---|
| Réduire à 20 % | les trois | Si le mot énorme ne se lit plus, le post est mort dans le fil |
| Poser l'image dans l'app et regarder | WhatsApp, TikTok | C'est le seul moyen de voir ce que l'interface recouvre |
| Rien dans les 480 px du bas ni les 240 px de droite | TikTok | Sinon le titre finit derrière les boutons |
| Rien dans les 220 px du haut ni les 340 px du bas | WhatsApp | Sinon le titre finit derrière le champ « Répondre » |
| Une seule source de lumière | WhatsApp | Deux sources et le plan de cinéma redevient une image de banque |
| La même main, le même téléphone sur les 3 | TikTok | C'est le fil rouge : s'il casse, ce sont trois posts, pas un carrousel |
| Les trois canaux côte à côte | les trois | S'ils se ressemblent, c'est que la référence était la même |
| Le logo n'a pas été redessiné | les trois | Défaut n° 1 quand la référence est en première position |
| Aucun chiffre, aucun pourcentage | les trois | Règle absolue de la rubrique |
| La promesse du test est tenable | WhatsApp | Dix secondes par personne, sinon retirer la ligne |

---

## 7. L'ordre de publication dans la journée

| Heure | Canal | Pourquoi cette heure |
|---|---|---|
| matin | Instagram / Facebook | le carrousel a besoin de temps pour tourner |
| 12 h à 14 h | TikTok | la pause, le moment où l'on glisse sans but |
| **20 h à 22 h** | **WhatsApp** | l'heure où l'on regarde les statuts, et l'heure du message |

Le statut WhatsApp arrive en dernier **volontairement** : c'est le seul canal où l'on
demande une réponse, et une réponse se donne le soir, quand la journée est finie.

---

*NEBULA Agency · Cotonou, Bénin · Document vivant. Ajouter chaque journée multicanale ici.*

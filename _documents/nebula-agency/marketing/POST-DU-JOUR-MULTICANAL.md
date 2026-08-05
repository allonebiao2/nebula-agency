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
> Message du 2026-08-04 : *sur internet, introuvable ne veut pas dire discret.*
> Version 1.0 · 2026-08-04

---

## 1. Les trois mondes

| | Instagram / Facebook | WhatsApp | TikTok |
|---|---|---|---|
| **Format** | 4:5, 1080 x 1350 | 9:16, 1080 x 1920 | 9:16, 1080 x 1920 |
| **Nombre d'images** | 3 (carrousel) | 1 (statut) | 3 (carrousel photo) |
| **Monde** | musée, papier imprimé | écran dans le noir | photocopie, papier déchiré |
| **Ambiance** | froid, silencieux, posé | alerte, nocturne, sec | bruyant, saturé, collé |
| **Registre** | **vous** | **vous** | **tu** |
| **Temps de lecture** | 8 secondes | 2 secondes | 1 seconde par image |
| **L'action demandée** | aimer, s'abonner | **répondre au statut** | s'abonner, liker |
| **Le prompt** | `PROMPTS-CARROUSELS.md` | §4 de ce document | §5 de ce document |

**Le registre change, pas seulement le décor.** On vouvoie sur Instagram et sur WhatsApp,
on tutoie sur TikTok. C'est ce qui fait que le post TikTok n'a pas l'air d'un post
Instagram recyclé, avant même de regarder les couleurs.

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
| WhatsApp | écran dans le noir, néon, typographie seule, beaucoup de vide |
| TikTok | collage, photocopie, papier déchiré, scotch, feutre, aplats fluo |

Si aucune référence n'est sous la main, chaque prompt contient un bloc **DIRECTION DE
SECOURS** à décommenter : le modèle s'en sert quand la référence ne répond pas à la
question.

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

## 4. WhatsApp · le statut du jour

### Ce que fait ce statut

Sur WhatsApp, on ne parle pas à des inconnus : on parle à des gens qui ont déjà le numéro.
Donc on ne demande pas un abonnement, **on demande une réponse**. Un statut qui obtient une
réponse ouvre une conversation, et une conversation vaut mille vues.

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
Editorial and direct, never an advertisement.

-----------------------------------------------------------
INTENT — use this to settle anything IMAGE 1 does not answer
-----------------------------------------------------------
This is a SCREEN SEEN IN THE DARK, not a printed page. It should feel
like a notification that arrived at 11pm and stopped the reader.
  - a deep, quiet, dark field: more than half the canvas stays empty
  - ONE single luminous accent colour, glowing like a lit screen,
    used for exactly two things: the huge word and the thin line work
  - pure typography and thin line drawing
  - emptiness is the subject: the void under the search bar is the
    whole message, so do not fill it

MUST NOT look like: a printed magazine page, a paper texture, a
collage, a torn-paper sticker, a marble sculpture, a photograph, a 3D
render, a stock image, a cluttered infographic.

-----------------------------------------------------------
FORMAT AND SAFE ZONES — a hard requirement
-----------------------------------------------------------
Canvas: 1080 x 1920 px, vertical 9:16.
WhatsApp draws its own interface OVER this image:
  - the TOP 220 px are covered by the profile bar
  - the BOTTOM 340 px are covered by the reply field
Nothing that matters may sit in those two strips. All text, the logo
and the visual live inside the central band, between 220 px and
1580 px from the top.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (top of the safe band, small, uppercase, widely letter-spaced,
       muted): "LE SAVIEZ-VOUS ?"

HOOK LINE (above the visual, medium size, clean sans-serif):
  "Tapez le nom de votre commerce dans votre téléphone."

VISUAL (middle of the canvas, thin luminous line drawing only):
  A wide search field drawn in thin glowing lines, empty, containing a
  single blinking text cursor and NO readable text at all.
  Directly under it, where results should be: NOTHING. A wide, deep,
  deliberately empty void. At the very bottom of that void, two or
  three hollow horizontal placeholder lines, dim and unfinished,
  fading out into the dark before they reach the edge.
  No icon, no magnifier, no app frame, no button, no brand.

HUGE WORD (under the void, by far the loudest element on the canvas,
           in the luminous accent colour, condensed, all caps):
  "RIEN."

CLOSING LINE (under the huge word, clean sans-serif):
  "C'est ce que vos clients voient."

CALL TO ACTION (bottom of the safe band, on its own, slightly set
                apart, in the accent colour):
  "Répondez « TEST » : je regarde pour vous."
  Keep the French guillemets « » exactly as written, with their inner
  spaces.

FOOTER: the logo from IMAGE 2, centred, small, about 14% of canvas
width, placed just ABOVE the 340 px bottom safe strip, never inside it.

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Inside the central safe band, top to bottom:
  1. LABEL
  2. HOOK LINE
  3. THE EMPTY SEARCH FIELD AND ITS VOID   <- the largest zone
  4. "RIEN."
  5. CLOSING LINE
  6. CALL TO ACTION
  7. LOGO
Wide margins left and right. The composition must breathe: the reader
has two seconds and one word to catch.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM: no translation, no rephrasing, no added
  punctuation, no exclamation marks.
- Correct French diacritics and apostrophes: "téléphone", "C'est".
- "RIEN." must be readable at 20% of the image size.
- No hashtag, no social icon, no interface element, no emoji.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO invented statistics, percentages or figures of any kind.
- NO human faces, no people, no recognisable third-party brand, app
  name or interface.
- NO watermark, no signature, no frame, no border.
- ONE single idea in this image.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1920 image, publication-ready,
high-fidelity text rendering.
===========================================================
```

**DIRECTION DE SECOURS**, à coller sous le bloc INTENT si la référence ne suffit pas :

```
FALLBACK ART DIRECTION, use only where IMAGE 1 is silent:
  background   matte near-black #0A0A0B, no texture, no grain
  accent       one luminous signal green #00FF85, screen-lit
  text         pure white #FFFFFF for the hook and closing lines,
               muted grey #6B7280 for the label
  Exactly three values. No other colour anywhere.
```

### Le texte à écrire par-dessus le statut

WhatsApp permet d'ajouter une légende sous l'image. Une phrase, pas plus :

```
Faites le test, ça prend dix secondes. Répondez TEST et je le fais pour vous.
```

### Le message pour la liste de diffusion

Le statut se regarde, la liste de diffusion se lit. Deux textes différents, envoyés le
même jour.

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

## 5. TikTok · le carrousel photo du jour

### Ce que fait ce carrousel

TikTok ne pardonne pas la première image : c'est elle qui passe dans le fil, et c'est elle
seule qui décide si on glisse. Quatre mots maximum, énormes, et on tutoie.

Le carrousel photo tourne en boucle avec un son. La dernière image revient sur la première :
elle doit donc **fermer** la boucle, pas laisser une question ouverte.

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

-----------------------------------------------------------
INTENT — use this to settle anything IMAGE 1 does not answer
-----------------------------------------------------------
Loud, raw, hand-made. A photocopied poster taped to a wall, not a
designed page: flat saturated colour field, torn paper edges, visible
photocopy grain and misregistration, strips of tape, marker strokes.
Type is enormous, condensed, and slightly off-axis.
Nothing precious, nothing quiet, nothing centred and polite.

MUST NOT look like: a clean corporate layout, a printed luxury
magazine page, a marble sculpture, a dark screen-lit interface, a
3D render, a stock photograph.

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
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (small torn-paper sticker, top-left, slightly rotated,
       uppercase, letter-spaced): "LE SAVIEZ-VOUS ?"

HEADLINE (upper half, left-aligned, ENORMOUS condensed sans-serif in
          all caps, two stacked lines, filling the live width, the
          loudest thing on the canvas by a wide margin):
  "TU N'EXISTES PAS"

SUB-LINE (immediately under the headline, much smaller, handwritten
          marker style, slightly tilted):
  "sur internet, en tout cas."

SWIPE CUE (left side, under the sub-line, on a small torn strip of
           paper, uppercase): "GLISSE" followed by a thick arrow
           pointing right, drawn like a marker stroke.

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
- No hashtag, no social icon, no interface element, no emoji, no
  TikTok logo, no play button.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO invented statistics, percentages or figures.
- NO human faces, no people, no recognisable third-party brand.
- NO watermark, no frame, no border.
- ONE single idea in this image.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1920 image, publication-ready,
high-fidelity text rendering.
===========================================================
```

### PROMPT · TikTok image 2 sur 3

```
===========================================================
NEBULA AGENCY — TIKTOK PHOTO CAROUSEL — SLIDE 2 OF 3
===========================================================

ATTACHED INPUTS — three attachments this time:
  IMAGE 1 = THE STYLE REFERENCE. Design language and palette only.
  IMAGE 2 = THE LOGO. An asset to place exactly as provided.
  IMAGE 3 = SLIDE 1 OF THIS CAROUSEL, generated just before.
            The CONSISTENCY REFERENCE.

CONSISTENCY: match IMAGE 3 on the paper and photocopy treatment, the
grain, the tape and torn-paper language, the type family and weight,
the label sticker size and position, the margins and the safe zones.
Only the colour field, the headline and the body text change.
The colour field INVERTS on this slide: if slide 1 was dark type on a
bright field, this one is bright type on a dark saturated field. That
inversion is the reward for swiping.

-----------------------------------------------------------
FORMAT AND SAFE ZONES — identical to slide 1
-----------------------------------------------------------
1080 x 1920 px, 9:16. Bottom 480 px and right 240 px are covered by
the TikTok interface: nothing that matters goes there. Headline in the
upper half, left-aligned.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (same torn sticker, same place): "LE SAVIEZ-VOUS ?"

HEADLINE (upper half, left-aligned, ENORMOUS condensed caps, three
          stacked lines, filling the live width):
  "ON TROUVE"
  "QUELQU'UN"
  "D'AUTRE"

BODY (under the headline, smaller, clean condensed sans-serif, three
      short lines, on a torn strip of lighter paper):
  "Le téléphone ne répond jamais « rien »."
  "Il répond quelqu'un."
  "Et ce soir encore."
  The last line is underlined with a thick marker stroke.
  Keep the French guillemets « » exactly as written.

FOOTER: the logo from IMAGE 2, bottom-left, same size and position as
slide 1, clear of both safe strips.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM. No translation, no rewording.
- Correct French apostrophes: "QUELQU'UN", "D'AUTRE", "n'est".
- The headline must be readable at 20% of the image size.
- No hashtag, no social icon, no emoji, no interface element.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO invented statistics, percentages or figures.
- NO human faces, no people, no recognisable third-party brand.
- NO watermark, no frame, no border. ONE single idea.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1920 image, publication-ready,
high-fidelity text rendering.
===========================================================
```

### PROMPT · TikTok image 3 sur 3

```
===========================================================
NEBULA AGENCY — TIKTOK PHOTO CAROUSEL — SLIDE 3 OF 3
===========================================================

ATTACHED INPUTS — three attachments:
  IMAGE 1 = THE STYLE REFERENCE. Design language and palette only.
  IMAGE 2 = THE LOGO. An asset to place exactly as provided.
  IMAGE 3 = SLIDE 2 OF THIS CAROUSEL, generated just before.
            The CONSISTENCY REFERENCE.

CONSISTENCY: match IMAGE 3 on the photocopy treatment, the grain, the
tape and torn-paper language, the type family and weight, the label
sticker, the margins and the safe zones.
The colour field RETURNS to the one used on slide 1, so the carousel
closes its loop when it repeats.

-----------------------------------------------------------
FORMAT AND SAFE ZONES — identical to slides 1 and 2
-----------------------------------------------------------
1080 x 1920 px, 9:16. Bottom 480 px and right 240 px are covered by
the TikTok interface: nothing that matters goes there.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (same torn sticker, same place): "LE SAVIEZ-VOUS ?"

HEADLINE (upper half, left-aligned, ENORMOUS condensed caps, two
          stacked lines): "FAIS LE TEST"

BODY (under the headline, smaller, on a torn strip of lighter paper,
      two lines):
  "Tape le nom de ton commerce dans ton téléphone."
  "Ce que tu vois, tes clients le voient aussi."

CALL TO ACTION (two separate torn-paper stickers, each slightly
                rotated, overlapping the body strip, in the loudest
                accent of the palette, uppercase):
  sticker 1: "ABONNE-TOI"
  sticker 2: "LIKE"
They are hand-cut paper stickers with tape, never app buttons, never
heart or bell icons.

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
- NO human faces, no people, no recognisable third-party brand.
- NO watermark, no frame, no border. ONE single idea.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1920 image, publication-ready,
high-fidelity text rendering.
===========================================================
```

**DIRECTION DE SECOURS TikTok**, à coller sous le bloc INTENT de l'image 1 :

```
FALLBACK ART DIRECTION, use only where IMAGE 1 is silent:
  slide 1 and 3   flat acid yellow field #E4FF1A, near-black type
  slide 2         flat electric blue field #1B1BFF, bone-white type
  accents         torn white paper strips, beige masking tape,
                  thick black marker strokes, visible photocopy grain
  Exactly these values. No gradient, no glow, no soft shadow.
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

# LE POST DU JOUR · un message, trois canaux

> **Le principe.** Le même jour, la même idée, sur trois canaux. Ce n'est pas le même
> visuel redimensionné trois fois : c'est **trois objets différents**, parce qu'on ne lit
> pas de la même façon un fil Instagram, un statut WhatsApp et un carrousel TikTok.
>
> **La règle qui commande tout, depuis la version 3 :** ce sont **les images envoyées qui
> font l'image**. La référence apporte le sujet, la matière et la palette ; le logo est posé
> proprement, avec sa transparence. Rien n'est inventé à côté.
>
> **WhatsApp : 1 image. TikTok : 3 images.** Instagram et Facebook : 3 images, dans
> `PROMPTS-CARROUSELS.md`.
>
> Message du 2026-08-04 : *sur internet, introuvable ne veut pas dire discret.*
> Version 3.0 · 2026-08-04

---

## 1. Ce qui a changé en version 3, et pourquoi

Les versions 1 et 2 inventaient un décor à côté de la référence : une barre de recherche en
fil de fer, un téléphone dressé dans un faisceau de lumière, une main découpée qui tient un
écran. **Tout ça est retiré.**

| | Avant | Maintenant |
|---|---|---|
| Le sujet de l'image | inventé dans le prompt | **celui de la référence envoyée**, remis en scène |
| Le rôle de la référence | « forme seulement, son sujet ne doit pas apparaître » | **c'est la matière du post** : sujet, palette, texture, lumière |
| Le logo | « posé en bas, 12 % de large » | **un bloc entier** : transparence gardée, aucun cadre, aucune plaque, aucune ombre, taille lisible |
| Ce qu'on ajoute | un décor de plus | rien |

**Pourquoi c'est mieux.** Un modèle d'image qui invente un décor invente aussi un style, et
le post cesse de ressembler à la marque. En lui donnant le sujet, on ne lui laisse qu'un
seul travail : mettre en scène et écrire proprement. C'est là qu'il est bon.

---

## 2. Les deux pièces jointes

**Image 1 = la référence de style. Image 2 = le logo NEBULA.**
Tous les prompts de ce document sont écrits dans cet ordre.

### Quel fichier de logo envoyer

| Fichier | Quand |
|---|---|
| `_documents/nebula-agency/marketing/logo/nebula-logo-detoure.png` | **par défaut, toujours** |
| `nebula-affilies/static/nebula-logo.png` | jamais pour un visuel, il sert ailleurs |

⚠️ **Le fichier d'origine est faux pour cet usage.** Il fait 900 x 600 px mais le logo n'y
occupe que **382 x 256 px**, soit **42 % de la largeur** : le reste est du vide transparent.
Demandé « à 12 % de la largeur du visuel », le logo réellement visible tombait à 5 %, et il
avait l'air perdu. La version détourée règle ça toute seule.

⚠️ **Le logo est violet et bleu.** Il est magnifique sur un fond sombre. Sur un papier
clair ou un aplat saturé, il jure. La référence marbre affiche d'ailleurs « NEBULA /
Agency » **en noir**, pas la galaxie. Si le fond du post est clair, demander la version
monochrome, ou accepter que le logo soit rendu en un seul ton.

⚠️ **L'ordre est l'inverse du prompt-maître de 2026-07-30**, qui mettait le logo en premier.
On suit ici l'ordre réellement utilisé, et chaque prompt commence donc par un bloc
anti-confusion qui nomme les deux rôles deux fois. Si le logo se fait quand même
réinterpréter, remettre le logo en premier et échanger « IMAGE 1 » et « IMAGE 2 » dans le
prompt.

### Quelle référence envoyer

Une par canal, jamais la même trois fois : c'est elle qui porte le post maintenant.

| Canal | Ce que la référence doit contenir |
|---|---|
| Instagram / Facebook | le sujet et la matière voulus pour le fil, format posé |
| WhatsApp | un sujet fort et un fond sombre : c'est lu de nuit, en deux secondes |
| TikTok | un sujet qui supporte d'être énorme et recadré très serré |

---

## 3. Les zones mortes, canal par canal

L'interface du réseau se pose **par-dessus** l'image, et elle mange toujours les mêmes
endroits. C'est le détail qui fait rater un post qui était bon, et il ne se voit qu'une fois
publié.

**WhatsApp, statut 1080 x 1920 :**
- les **220 premiers pixels** en haut : photo de profil, nom, heure
- les **340 derniers pixels** en bas : le champ « Répondre »

**TikTok, carrousel photo 1080 x 1920 :**
- les **480 derniers pixels** en bas : la légende, le pseudo, le son, la barre de lecture
- les **240 pixels de droite** : les boutons cœur, commentaire, partage, profil
- la zone sûre est donc un rectangle **décalé vers le haut et vers la gauche**

---

## 4. WhatsApp · **1 image**

> **Les règles générales du statut** (zones mortes, contraste au soleil, vouvoiement, l'appel
> à l'action qui se répond d'un caractère) sont dans `PROMPTS-WHATSAPP-STATUT.md`, qui
> rassemble aussi les autres statuts. Ce paragraphe ne garde que celui du jour.

### Ce que fait ce statut

Sur WhatsApp, on ne parle pas à des inconnus : ils ont déjà le numéro. Donc on ne demande
pas un abonnement, **on demande une réponse**. Un statut qui obtient une réponse ouvre une
conversation, et une conversation vaut mille vues.

**Cinq lignes, dont une seule est grosse.** Un statut se regarde en deux secondes. Chaque
phrase en plus retire du poids à celles qui restent.

⚠️ **La promesse doit être tenue.** Le statut propose de faire le test gratuitement pour
celui qui répond. Dix secondes par personne : taper le nom de son commerce et lui envoyer la
capture. Si on ne compte pas le faire, retirer cette ligne.

### PROMPT · statut WhatsApp

```
===========================================================
NEBULA AGENCY — WHATSAPP STATUS — ONE IMAGE, 9:16
===========================================================

ATTACHED INPUTS — two attachments, two different roles.
Read this block twice. Swapping the two roles ruins the image.

  IMAGE 1 = THE SOURCE IMAGE.
     This is the material of the post: its subject, its palette, its
     texture, its lighting and its typographic craft all carry over.
     It is not a vague inspiration and it is not a form reference.

  IMAGE 2 = THE LOGO.
     The official NEBULA Agency logo, a PNG with a transparent
     background. An ASSET TO PLACE, exactly as provided. Never a
     style reference, never a subject to reinterpret.

  To be explicit: the IMAGE comes from IMAGE 1. The LOGO is IMAGE 2.

-----------------------------------------------------------
TASK
-----------------------------------------------------------
Create ONE original WhatsApp status image for NEBULA Agency, a digital
studio in Cotonou, Benin, serving West African merchants.
It is read in TWO SECONDS, at night, on a phone held in one hand.
It must look expensive and deliberate, never like a quote card.

-----------------------------------------------------------
THE MATERIAL — IMAGE 1 IS THE SOURCE, NOT AN INSPIRATION
-----------------------------------------------------------
Build this image OUT OF IMAGE 1. Do not invent a new subject and do
not add a decor of your own.
  KEEP    its main subject, and re-stage it for the message below:
          same object, same rendering, same level of realism
  KEEP    its palette, its texture, its grain and its lighting
  KEEP    its typographic craft: the same kind of contrast between a
          huge word and small quiet lines
  CHANGE  its pose or its state, its framing for a 9:16 canvas, and
          every single word on it
  DROP    its original words, numbers, captions, logo and watermark:
          none of them may appear
If you find yourself inventing a new object, stop. The subject is
already in IMAGE 1. Nothing else enters the frame: no phone, no
screen, no hand, no icon, no prop, no second element.

-----------------------------------------------------------
THE STAGING — what the subject must be doing
-----------------------------------------------------------
The subject is being LOOKED FOR, and not found.
Stage it so that reads instantly: most of it swallowed by darkness or
by empty space, only an edge still catching the light, the frame far
emptier than it is full. The emptiness around it is the message.
More than half of the canvas stays quiet and unoccupied.

-----------------------------------------------------------
LOGO INTEGRATION — read twice, most attempts fail here
-----------------------------------------------------------
IMAGE 2 is a PNG with a TRANSPARENT background. Place it exactly as
provided and KEEP that transparency.
  - the logo sits DIRECTLY on the artwork. NO white box, NO black
    box, NO coloured plate, NO rounded card, NO badge, NO circle,
    NO outline, NO glow, NO drop shadow behind it.
  - do NOT redraw it, restyle it, recolour it, stretch it, crop it,
    rotate it, or add a wordmark or tagline of your own.
  - reserve a CALM area for it: no busy texture and no strong
    contrast directly behind it, so it reads cleanly with no plate.
  - size it so its wordmark stays comfortably readable when the whole
    image is viewed at 20% of its size, and align its left or centre
    to the same margin as the text.
A logo pasted on a white rectangle is a failed image.

-----------------------------------------------------------
FORMAT AND SAFE ZONES — a hard requirement
-----------------------------------------------------------
Canvas: 1080 x 1920 px, vertical 9:16.
WhatsApp draws its own interface OVER this image:
  - the TOP 220 px are covered by the profile bar
  - the BOTTOM 340 px are covered by the reply field
Nothing that matters may sit in those two strips. All text, the logo
and the subject live inside the central band, between 220 px and
1580 px from the top.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (top of the safe band, small, uppercase, widely letter-spaced,
       muted, discreet): "LE SAVIEZ-VOUS ?"

HOOK LINE (above the subject, small, clean, quiet):
  "Ils ont cherché votre commerce."

HUGE WORD (the loudest element of the whole image by a wide margin,
           condensed, all caps, in the accent colour of IMAGE 1):
  "RIEN."

CLOSING LINE (under the huge word, small, clean, quiet):
  "C'est ce qu'ils ont trouvé."

CALL TO ACTION (bottom of the safe band, slightly set apart, in the
                accent colour, much smaller than the huge word):
  "Répondez « TEST » : je regarde pour vous."
  Keep the French guillemets « » exactly as written, with their inner
  spaces.

FOOTER: the logo from IMAGE 2, per the LOGO INTEGRATION block, placed
just ABOVE the 340 px bottom safe strip, never inside it.

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Inside the central safe band, top to bottom:
  1. LABEL
  2. HOOK LINE
  3. THE SUBJECT FROM IMAGE 1     <- the largest zone by far
  4. "RIEN."
  5. CLOSING LINE
  6. CALL TO ACTION
  7. LOGO
Wide margins left and right. Five text elements in total, and only one
of them is large.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM: no translation, no rephrasing, no added
  punctuation, no exclamation marks.
- Correct French diacritics and apostrophes: "cherché", "C'est".
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

### Le texte à écrire sous le statut

```
Tapez le nom de votre commerce dans votre téléphone. Ça prend dix secondes.
Répondez TEST et je le fais pour vous.
```

### Le message pour la liste de diffusion

Le statut se regarde, la liste de diffusion se lit. Deux textes différents, le même soir.

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

---

## 5. TikTok · **3 images**

### Ce que fait ce carrousel

TikTok ne pardonne pas la première image : c'est elle qui passe dans le fil, et elle seule
décide si on glisse. Quatre mots maximum, énormes, et on tutoie.

**Le fil rouge des trois images :** c'est **le même sujet, celui de la référence**, dans
trois états. Effacé, remplacé, revenu. On comprend l'histoire sans lire une ligne, et la
boucle se referme quand TikTok rejoue la première.

### PROMPT · TikTok image 1 sur 3

```
===========================================================
NEBULA AGENCY — TIKTOK PHOTO CAROUSEL — SLIDE 1 OF 3
===========================================================

ATTACHED INPUTS — two attachments, two different roles.
Read this block twice. Swapping the two roles ruins the image.

  IMAGE 1 = THE SOURCE IMAGE.
     The material of the post: its subject, its palette, its texture,
     its lighting and its typographic craft all carry over.
     Not a vague inspiration, not a form reference.

  IMAGE 2 = THE LOGO.
     The official NEBULA Agency logo, a PNG with a transparent
     background. An ASSET TO PLACE exactly as provided.

  To be explicit: the IMAGE comes from IMAGE 1. The LOGO is IMAGE 2.

-----------------------------------------------------------
TASK
-----------------------------------------------------------
Create SLIDE 1 of a 3-slide TikTok photo carousel for NEBULA Agency, a
digital studio in Cotonou, Benin, serving West African merchants.
This slide is the cover. It has ONE second to stop a thumb.
It must look designed and expensive, never cheap, never homemade.

-----------------------------------------------------------
THE MATERIAL — IMAGE 1 IS THE SOURCE, NOT AN INSPIRATION
-----------------------------------------------------------
Build this image OUT OF IMAGE 1. Do not invent a new subject and do
not add a decor of your own.
  KEEP    its main subject, re-staged for a 9:16 canvas and cropped
          much tighter: on TikTok the subject fills the frame
  KEEP    its palette, its texture, its grain and its lighting
  KEEP    its typographic craft, pushed louder: the huge line here is
          bigger, tighter and more aggressive than in the source
  CHANGE  its state, its framing, and every single word on it
  DROP    its original words, numbers, captions, logo and watermark
If you find yourself inventing a new object, stop. The subject is
already in IMAGE 1. Nothing else enters the frame.

-----------------------------------------------------------
THE STAGING — what the subject must be doing
-----------------------------------------------------------
The subject is DISAPPEARING. Show it partly erased, dissolving or
falling out of the frame, clearly on its way to not being there.
It still fills the live area: this is a close, confident crop, not a
small object lost in space.

-----------------------------------------------------------
LOGO INTEGRATION — read twice, most attempts fail here
-----------------------------------------------------------
IMAGE 2 is a PNG with a TRANSPARENT background. Place it exactly as
provided and KEEP that transparency.
  - the logo sits DIRECTLY on the artwork. NO white box, NO black
    box, NO coloured plate, NO rounded card, NO badge, NO circle,
    NO outline, NO glow, NO drop shadow behind it.
  - do NOT redraw it, restyle it, recolour it, stretch it, crop it,
    rotate it, or add a wordmark or tagline of your own.
  - reserve a CALM area for it: no busy texture and no strong
    contrast directly behind it, so it reads cleanly with no plate.
  - size it so its wordmark stays comfortably readable when the whole
    image is viewed at 20% of its size.
A logo pasted on a white rectangle is a failed image.

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
LABEL (small, top-left, uppercase, widely letter-spaced):
  "LE SAVIEZ-VOUS ?"

HEADLINE (upper half, left-aligned, ENORMOUS, all caps, two stacked
          lines, tight tracking, filling the live width, overlapping
          the subject, the loudest thing on the canvas by far):
  "TU N'EXISTES PAS"

SUB-LINE (immediately under the headline, much smaller, quiet):
  "sur internet, en tout cas."

SWIPE CUE (left side, below the sub-line, small, uppercase,
           letter-spaced): "GLISSE" followed by a solid triangular
           arrow pointing right.

FOOTER: the logo from IMAGE 2, per the LOGO INTEGRATION block,
bottom-LEFT, just ABOVE the 480 px bottom safe strip and well clear
of the 240 px right strip.

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
- NO watermark, no frame, no border. ONE single idea.

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

ATTACHED INPUTS — three attachments, three different roles:

  IMAGE 1 = THE SOURCE IMAGE. Subject, palette, texture, lighting.
  IMAGE 2 = THE LOGO, transparent PNG, placed exactly as provided.
  IMAGE 3 = SLIDE 1 OF THIS CAROUSEL, generated just before.
            The CONSISTENCY REFERENCE.

-----------------------------------------------------------
CONSISTENCY — the most important instruction of this prompt
-----------------------------------------------------------
Match IMAGE 3 exactly on: the subject and how it is rendered, the
crop distance, the palette, the texture and grain, the type family
and weight, the label, the margins, the safe zones and the logo
placement. The two must read as one object.
ONE thing changes in the staging, and only one, described below.

-----------------------------------------------------------
THE STAGING — what the subject must be doing
-----------------------------------------------------------
The subject is REPLACED. It has been pushed aside, out of the centre,
losing its light; and the place it occupied is now taken by another
shape of the same kind, sharper, brighter, clearly the one being
looked at. Same world, same material, two presences: yours fading at
the edge, the other one holding the centre.
Nothing else is invented: no phone, no screen, no icon, no prop.

-----------------------------------------------------------
LOGO INTEGRATION
-----------------------------------------------------------
Same rules as slide 1: transparency preserved, no box, no plate, no
outline, no glow, no shadow behind it, never redrawn or recoloured,
placed on a calm area, same size and same position as slide 1.

-----------------------------------------------------------
FORMAT AND SAFE ZONES — identical to slide 1
-----------------------------------------------------------
1080 x 1920 px, 9:16. Bottom 480 px and right 240 px are covered by
the TikTok interface: nothing that matters goes there. Headline in the
upper half, left-aligned.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (same place, same size): "LE SAVIEZ-VOUS ?"

HEADLINE (upper half, left-aligned, ENORMOUS all caps, three stacked
          lines, tight tracking):
  "ON TROUVE"
  "QUELQU'UN"
  "D'AUTRE"

BODY (under the headline, much smaller, three short lines, the last
      one emphasised):
  "Le téléphone ne répond jamais « rien »."
  "Il répond quelqu'un."
  "Et ce soir encore."
  Keep the French guillemets « » exactly as written.

FOOTER: the logo from IMAGE 2, bottom-left, same size and position as
slide 1.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM. No translation, no rewording.
- Correct French apostrophes: "QUELQU'UN", "D'AUTRE".
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

ATTACHED INPUTS — three attachments, three different roles:

  IMAGE 1 = THE SOURCE IMAGE. Subject, palette, texture, lighting.
  IMAGE 2 = THE LOGO, transparent PNG, placed exactly as provided.
  IMAGE 3 = SLIDE 2 OF THIS CAROUSEL, generated just before.
            The CONSISTENCY REFERENCE.

-----------------------------------------------------------
CONSISTENCY — the most important instruction of this prompt
-----------------------------------------------------------
Match IMAGE 3 exactly on: the subject and how it is rendered, the
crop distance, the palette, the texture and grain, the type family
and weight, the label, the margins, the safe zones and the logo
placement. This slide closes the loop back to slide 1, so its overall
tone returns to the one of the first slide.

-----------------------------------------------------------
THE STAGING — what the subject must be doing
-----------------------------------------------------------
The subject is BACK, whole and clear. Nothing missing, nothing eroded,
nothing pushed aside: it holds the centre of the frame in full light,
and it is the only presence left. The other shape from slide 2 is gone.
Nothing else is invented: no phone, no screen, no icon, no prop.

-----------------------------------------------------------
LOGO INTEGRATION
-----------------------------------------------------------
Same rules as slides 1 and 2: transparency preserved, no box, no
plate, no outline, no glow, no shadow behind it, never redrawn or
recoloured, placed on a calm area, same size and same position.

-----------------------------------------------------------
FORMAT AND SAFE ZONES — identical to slides 1 and 2
-----------------------------------------------------------
1080 x 1920 px, 9:16. Bottom 480 px and right 240 px are covered by
the TikTok interface: nothing that matters goes there.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (same place, same size): "LE SAVIEZ-VOUS ?"

HEADLINE (upper half, left-aligned, ENORMOUS all caps, two stacked
          lines, tight tracking): "FAIS LE TEST"

BODY (under the headline, much smaller, two lines):
  "Tape le nom de ton commerce dans ton téléphone."
  "Ce que tu vois, tes clients le voient aussi."

CALL TO ACTION (two solid pill shapes side by side, drawn in the
                accent colour of IMAGE 1, uppercase, tight tracking):
  pill 1: "ABONNE-TOI"
  pill 2: "LIKE"
They are printed graphic shapes, never app buttons, never heart or
bell icons, never a screenshot of an interface.

FOOTER: the logo from IMAGE 2, bottom-left, same size and position as
slides 1 and 2.

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

### La légende TikTok

```
Tape le nom de ton commerce dans ton téléphone. Là, maintenant.
Ce que tu vois, c'est exactement ce que voient tes clients.

Abonne-toi, on en remet une chaque semaine.

#cotonou #benin #229 #business #entrepreneur #commerce
```

### Le son

Un son **qui monte dans les tendances**, pas un son déjà partout, laissé bas. Sur un
carrousel photo il ne raconte rien : il sert à ne pas être muet, parce qu'un carrousel muet
est poussé moins loin.

---

## 6. Contrôles avant publication

| Contrôle | Canal | Pourquoi |
|---|---|---|
| **Le logo n'a aucun cadre derrière lui** | les trois | Une plaque blanche sous le logo, et tout le post a l'air amateur |
| **Le logo est encore lisible à 20 %** | les trois | Avec le fichier non détouré, il tombait à 5 % de la largeur |
| Le sujet vient bien de la référence | les trois | Si le modèle a inventé un décor, le post ne ressemble plus à la marque |
| Réduire à 20 % | les trois | Si le mot énorme ne se lit plus, le post est mort dans le fil |
| Poser l'image dans l'app et regarder | WhatsApp, TikTok | Le seul moyen de voir ce que l'interface recouvre |
| Rien dans les 480 px du bas ni les 240 px de droite | TikTok | Sinon le titre finit derrière les boutons |
| Rien dans les 220 px du haut ni les 340 px du bas | WhatsApp | Sinon le titre finit derrière le champ « Répondre » |
| Le même sujet sur les 3 images | TikTok | C'est le fil rouge : s'il casse, ce sont trois posts, pas un carrousel |
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

# TIKTOK · prompts image par image

> **Ce que TikTok pardonne, et ce qu'il ne pardonne pas.** Il pardonne un fond simple, une
> faute de goût, un son quelconque. Il ne pardonne **jamais** une première image molle : elle
> passe dans le fil et elle a **une seconde**. Tout le travail est là.
>
> **On tutoie.** C'est ce qui sépare le plus sûrement un post TikTok d'un post Instagram
> recyclé, avant même de regarder les couleurs.
>
> **Ce qui ne change jamais :** le label « LE SAVIEZ-VOUS ? », ancre de la rubrique, même
> texte, même place, même casse.
>
> Version 1.0 · 2026-08-04

---

## 1. Les règles TikTok, une fois pour toutes

**Format :** 1080 x 1920 px, 9:16.

**Les zones mortes.** L'interface se pose **par-dessus** l'image, et ça ne se voit qu'une
fois publié :
- les **480 derniers pixels en bas** : légende, pseudo, son, barre de lecture
- les **240 pixels de droite** : cœur, commentaire, partage, profil

La zone vivante est donc un rectangle **poussé vers le haut et vers la gauche**. Un titre
centré verticalement finit à moitié derrière les boutons.

**La hiérarchie est brutale ou elle n'existe pas.** Un seul bloc est énorme, tout le reste
est petit. Deux blocs énormes, c'est zéro bloc lu.

**Le test :** réduire à 20 %. Si l'accroche ne se lit plus, regénérer.

---

## 2. Les deux pièces jointes, identifiées par leur contenu

Les prompts de ce document **ne comptent pas sur l'ordre des pièces jointes**. Ils
identifient chaque image par ce qu'elle contient. C'est ce qui évite le défaut n° 1 : le
modèle qui prend le logo pour un modèle de style et fait disparaître la marque.

| Ce qu'on envoie | Fichier | Rôle dans le prompt |
|---|---|---|
| Le logo | `logo/nebula-logo-detoure.png` | posé tel quel, transparence gardée |
| La référence | l'image dont on veut le design | c'est **la matière** du post |

⚠️ **Toujours le logo DÉTOURÉ.** Celui de `nebula-affilies/static/` fait 900 x 600 px alors
que le logo n'y occupe que 382 x 256 px : **58 % du fichier est du vide transparent**.
Demandé « à 12 % de la largeur », le logo réellement visible tombait à 5 %.

⚠️ **La référence n'est pas une vague inspiration : c'est la matière.** Son sujet, sa
palette, sa texture et sa lumière passent tous dans le post. On ne change que l'état du
sujet, le cadrage et les mots. Un modèle à qui on laisse inventer un décor invente aussi un
style, et le post cesse de ressembler à la marque.

---

## 3. Post n° 1 · « UN PAS DEDANS »

⚠️ **Ce message est finalement parti en statut WhatsApp**, pas sur TikTok : voir
`PROMPTS-WHATSAPP-STATUT.md`. La version ci-dessous reste utilisable telle quelle si on veut
le publier aussi sur TikTok. Trois choses seulement changent entre les deux : **on tutoie
ici et on vouvoie là-bas**, les zones mortes ne sont pas les mêmes, et **l'appel à l'action
est un abonnement ici, une réponse là-bas**.

**Le sujet :** le numérique, et le fait qu'il n'y a pas besoin de tout comprendre pour
commencer. Un pied dedans suffit à changer de camp.

**L'accroche, et pourquoi elle marche :**

> **LE NUMÉRIQUE NE TE REMPLACERA PAS. QUELQU'UN, SI.**

Elle rassure sur une ligne et frappe sur la suivante. Le lecteur croit reconnaître le
discours mou qu'on lui sert partout (« la technologie, l'avenir »), et la troisième ligne
déplace la menace : ce n'est pas une machine qui arrive, c'est **son voisin**. C'est ce
déplacement qui fait le choc, et il tient en une seconde.

**La valeur, et pourquoi elle est grosse :** le post démonte l'excuse la plus répandue,
« je ne m'y connais pas ». Il n'y a pas de compétence à acquérir, il y a **trois choses
concrètes** à avoir : une adresse où l'on te trouve, un prix qu'on peut lire, une page qui
répond quand tu dors. Le lecteur repart avec une liste, pas avec une inquiétude.

**Trois choses. Pas un diplôme.** C'est la phrase qu'on doit retenir en fermant TikTok.

**L'image, et pourquoi elle est bonne :** le sujet de la référence est posé sur un seuil,
**un seul pas déjà franchi** au-delà d'une fine ligne de lumière. Derrière lui, tout est
éteint. Devant, tout est éclairé. Ce n'est pas un saut, c'est un pas : l'image dit
exactement ce que dit le texte, et elle le dit sans mot.

⚠️ **Aucun chiffre nulle part.** Rien dans ce post ne repose sur une statistique. Règle
absolue de la rubrique : le jour où quelqu'un demande la source, on perd plus que le post
n'a rapporté.

### LE PROMPT

```
===========================================================
NEBULA AGENCY — TIKTOK — ONE IMAGE, 9:16
===========================================================

ATTACHED INPUTS — TWO attachments.
Identify them BY THEIR CONTENT, not by their order. Never swap their
roles: swapping them ruins the image.

  THE LOGO = the attachment showing the NEBULA Agency logo: a purple
     and blue cosmic swirl above the wordmark "NEBULA", with "AGENCY"
     underneath, on a transparent background.
     It is an ASSET TO PLACE, exactly as provided. It is never a style
     reference and never a subject to reinterpret.

  THE STYLE REFERENCE = the other attachment. This one is the design
     the post takes after, and it is the MATERIAL of the post: its
     subject, its palette, its texture, its lighting and its
     typographic craft all carry over.

  If you hesitate: the attachment with a transparent background and a
  readable "NEBULA AGENCY" wordmark is THE LOGO. The other one is THE
  STYLE REFERENCE.

-----------------------------------------------------------
TASK
-----------------------------------------------------------
Create ONE original TikTok image for NEBULA Agency, a digital studio
in Cotonou, Benin, serving West African merchants and business owners.
It has ONE SECOND to stop a thumb, and it must teach something in the
next three. It is editorial content, never an advertisement.
It must look designed and expensive, never cheap, never homemade.

-----------------------------------------------------------
THE MATERIAL — THE STYLE REFERENCE IS THE SOURCE,
                NOT A VAGUE INSPIRATION
-----------------------------------------------------------
Build this image OUT OF the style reference. Do not invent a new
subject and do not add a decor of your own.
  KEEP    its main subject, re-staged as described below, and cropped
          tighter: on TikTok the subject fills the frame
  KEEP    its palette, its texture, its grain and its lighting
  KEEP    its typographic craft, pushed louder: the huge lines here
          are bigger, tighter and more aggressive than in the source
  CHANGE  its state, its framing for a 9:16 canvas, and every single
          word on it
  DROP    its original words, numbers, captions, logo and watermark:
          none of them may appear
If you find yourself inventing a new object, stop. The subject is
already in the style reference. Nothing else enters the frame.

-----------------------------------------------------------
THE STAGING — this is the whole idea of the image
-----------------------------------------------------------
ONE STEP IN. Not a leap: a single step.
A single thin luminous line crosses the frame and divides it in two.
  - BEHIND the line: everything is flat, cold, unlit, still
  - BEYOND the line: everything is lit, alive, with depth
The subject of the style reference stands ON that line, with ONE part
of itself already across it, into the light. The rest of it is still
behind, in the dull half. The crossing is small and deliberate: the
subject has not moved much, and yet everything about the lit part
looks different from the dull part.
The contrast between the two halves of the same subject is the entire
message. Make it unmistakable at a glance.
No arrow, no icon, no diagram, no before-and-after label, no second
object: only the line, the subject, and the light.

-----------------------------------------------------------
LOGO INTEGRATION — read twice, most attempts fail here
-----------------------------------------------------------
The logo attachment is a PNG with a TRANSPARENT background. Place it
exactly as provided and KEEP that transparency.
  - it sits DIRECTLY on the artwork. NO white box, NO black box, NO
    coloured plate, NO rounded card, NO badge, NO circle, NO outline,
    NO glow, NO drop shadow behind it.
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
rectangle pushed UP and to the LEFT, and everything below is
composed as if it did not exist.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (small, top-left, uppercase, widely letter-spaced, muted):
  "LE SAVIEZ-VOUS ?"

HEADLINE (upper half, left-aligned, ENORMOUS all caps, condensed,
          tight tracking and tight leading, three stacked lines
          filling the live width. By far the loudest element of the
          image. The first two lines in the ink colour of the style
          reference, THE THIRD LINE in its accent colour):
  "LE NUMÉRIQUE NE"
  "TE REMPLACERA PAS."
  "QUELQU’UN, SI."

BODY (under the headline, MUCH smaller, quiet, three short lines):
  "Il ne travaille pas plus que toi."
  "Il a une adresse où on le trouve, un prix qu’on peut lire,"
  "et une page qui répond quand il dort."

CLOSER (under the body, medium size, in the accent colour, set apart
        with real breathing space above it so it lands on its own):
  "Trois choses. Pas un diplôme."

CALL TO ACTION (small, discreet, bottom-left of the live area, a
                solid pill shape in the accent colour, uppercase,
                tight tracking): "ABONNE-TOI"
It is a printed graphic shape, never an app button, never a heart or
bell icon, never a screenshot of an interface.

FOOTER: the logo, per the LOGO INTEGRATION block, bottom-LEFT, just
ABOVE the 480 px bottom safe strip and well clear of the 240 px right
strip.

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Inside the live area, top to bottom:
  1. LABEL
  2. HEADLINE, three stacked lines     <- the loudest zone
  3. THE SUBJECT ON ITS LINE OF LIGHT  <- the largest zone
  4. BODY, three quiet lines
  5. CLOSER
  6. CALL TO ACTION, then the LOGO
The hierarchy must be brutal: ONE block is enormous and everything
else is small. Two large blocks means neither gets read.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM: no translation, no rephrasing, no
  shortening, no added punctuation, no exclamation marks.
- Correct French diacritics and apostrophes: "NUMÉRIQUE", "où",
  "qu’on", "diplôme".
- The headline must be readable at 20% of the image size.
- No hashtag, no social icon, no interface element, no emoji, no
  TikTok logo, no play button.

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

### La légende

```
Le numérique ne remplace personne. Il déplace ceux qui s'y sont mis, c'est tout.

Et il n'y a pas besoin de tout comprendre pour commencer.
Une adresse où on te trouve. Un prix qu'on peut lire. Une page qui répond
quand tu dors. Trois choses, pas un diplôme.

Commence par une. Laquelle te manque ?

#cotonou #benin #229 #entrepreneur #business #commerce #digital
```

**Le premier commentaire, à poster soi-même :**

> Laquelle des trois te manque aujourd'hui ? Réponds 1, 2 ou 3, je te dis par où commencer.

Une question fermée à laquelle on répond d'un chiffre, depuis un téléphone, en marchant.
C'est ce qui fait vivre un post.

### Le son

Un son **qui monte dans les tendances**, pas un son déjà partout, laissé bas. Sur une image
fixe il ne raconte rien : il sert à ne pas être muet, parce qu'un post muet est poussé moins
loin.

## 4. Post n° 2 · carrousel « LE NUAGE N’EXISTE PAS »

**3 images, 9:16, on tutoie. Pure rubrique éditoriale : ça enseigne et ça ne vend rien.**
Le label « LE SAVIEZ-VOUS ? » est donc présent, et un compteur 1/3, 2/3, 3/3.

**Le sujet :** ce qu'est vraiment un site internet. Trois faits vrais qui, mis bout à bout,
expliquent la chose entière. À la fin, le spectateur sait quelque chose que presque personne
autour de lui ne sait, et il pourra le raconter le soir même.

| Image | Le fait | Ce qu'il démonte |
|---|---|---|
| 1/3 | **LE NUAGE N’EXISTE PAS.** | le mot que tout le monde répète sans y penser |
| 2/3 | **TON ADRESSE N’EST PAS TON SITE.** | on croit que le nom de domaine *est* le site |
| 3/3 | **LE SITE NE VIENT JAMAIS À TOI.** | on croit que la page « arrive » |

**Pourquoi commencer par le nuage.** Parce que c'est le seul mot du numérique que tout le
monde emploie et que personne n'a jamais interrogé. Dire qu'il n'existe pas arrête le pouce
en une seconde, et la vérité derrière est banale et vertigineuse : **c'est la machine de
quelqu'un, dans un bâtiment, avec une facture d'électricité.**

**La leçon d'ensemble, donnée sur la 3 :** *la machine peut changer, le nom reste à toi.*
C'est la chose pratique à retenir, et elle arrive après trois faits, pas avant. Le
spectateur la déduit presque seul, ce qui la rend beaucoup plus solide qu'un conseil.

⚠️ **Aucune vente, aucun prix, aucune offre.** Le seul appel à l'action est un abonnement,
et il est petit. C'est un post qui donne ; c'est lui qui achètera le droit d'être cru quand
un post commercial passera.

⚠️ **Les trois faits sont exacts.** Un site est bien hébergé sur une machine physique
refroidie et alimentée ; le nom de domaine est bien une entrée d'annuaire qui pointe vers une
adresse et ne contient rien ; et une page consultée est bien une copie envoyée, l'original
restant en place. Rien n'est arrondi, rien n'est chiffré.

**Le fil visuel : l'original et ses copies.**

1. le sujet, **solide et lourd**, posé sur une surface physique, ombre pleine, rien ne
   flotte : il existe quelque part pour de vrai ;
2. le sujet d'un côté du cadre, et **une petite plaque vide** de l'autre, reliée à lui par un
   fil de lumière : le nom ne contient rien, il pointe ;
3. le sujet **immobile et intact**, pendant que des **dizaines de copies translucides** de
   lui s'échappent vers l'extérieur : l'original ne diminue pas.

### PROMPT · image 1 sur 3

```
===========================================================
NEBULA AGENCY — TIKTOK CAROUSEL, LESSON — SLIDE 1 OF 3
===========================================================

ATTACHED INPUTS — TWO attachments.
Identify them BY THEIR CONTENT, not by their order. Never swap their
roles: swapping them ruins the image.

  THE LOGO = the attachment showing the NEBULA Agency logo: a purple
     and blue cosmic swirl above the wordmark "NEBULA", with "AGENCY"
     underneath, on a transparent background.
     It is an ASSET TO PLACE, exactly as provided. It is never a style
     reference and never a subject to reinterpret.

  THE STYLE REFERENCE = the other attachment. This one is the design
     the post takes after, and it is the MATERIAL of the post: its
     subject, its palette, its texture, its lighting and its
     typographic craft all carry over.

  If you hesitate: the attachment with a transparent background and a
  readable "NEBULA AGENCY" wordmark is THE LOGO. The other one is THE
  STYLE REFERENCE.

-----------------------------------------------------------
TASK
-----------------------------------------------------------
Create SLIDE 1 of a 3-slide TikTok photo carousel for NEBULA Agency, a
digital studio in Cotonou, Benin, serving West African merchants and
business owners.
The three slides teach ONE lesson in three facts: what a website
actually is. This first one is the cover: it has ONE SECOND to stop a
thumb, and it must make the viewer realise they have been repeating a
word without ever questioning it.
This post SELLS NOTHING. It is editorial: the viewer simply ends the
day knowing something almost nobody around them knows.
It must look designed and expensive, never cheap, never homemade.

-----------------------------------------------------------
THE MATERIAL — THE STYLE REFERENCE IS THE SOURCE,
                NOT A VAGUE INSPIRATION
-----------------------------------------------------------
Build this image OUT OF the style reference. Do not invent a new
subject and do not add a decor of your own.
  KEEP    its main subject, re-staged as described below, and cropped
          tighter: on TikTok the subject fills the frame
  KEEP    its palette, its texture, its grain and its lighting
  KEEP    its typographic craft, pushed louder: the huge lines here
          are bigger and tighter than in the source
  CHANGE  its state, its framing for a 9:16 canvas, and every single
          word on it
  DROP    its original words, numbers, captions, logo and watermark:
          none of them may appear
If you find yourself inventing a new object, stop. The subject is
already in the style reference. Nothing else enters the frame.

-----------------------------------------------------------
THE STAGING — this is the whole idea of the image
-----------------------------------------------------------
IT IS SOLID, AND IT IS SOMEWHERE.
Everything about the subject must contradict the idea of floating.
Show it resting on a hard physical surface, heavy, weighted, with a
full dense contact shadow directly under it where it touches. Give it
real material presence: visible mass, a sense that it would be
difficult to lift.
The air around it is clear and ordinary. NOTHING floats, NOTHING is
suspended, NOTHING glows in mid-air, and there is no mist, no vapour,
no cloud, no fog anywhere in the frame.
No arrow, no icon, no diagram, no cable, no server rack, no building,
no phone, no screen, no hand, no label.

-----------------------------------------------------------
LOGO INTEGRATION — read twice, most attempts fail here
-----------------------------------------------------------
The logo attachment is a PNG with a TRANSPARENT background. Place it
exactly as provided and KEEP that transparency.
  - it sits DIRECTLY on the artwork. NO white box, NO black box, NO
    coloured plate, NO rounded card, NO badge, NO circle, NO outline,
    NO glow, NO drop shadow behind it.
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
rectangle pushed UP and to the LEFT, and everything below it is
composed as if it did not exist.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (top-left, small, uppercase, widely letter-spaced, muted):
  "LE SAVIEZ-VOUS ?"
COUNTER (top-right, same size, same colour, same baseline): "1/3"

THE FACT (upper half, left-aligned, ENORMOUS all caps, condensed,
          tight tracking and tight leading, two stacked lines filling
          the live width. By far the loudest element of the image, and
          the only large one. The accent colour of the style
          reference on the second line):
  "LE NUAGE"
  "N’EXISTE PAS."

THE EXPLANATION (under it, MUCH smaller, quiet, three lines):
  "Ton site n’est pas dans le ciel."
  "Il est sur une machine, dans un bâtiment, avec de l’électricité et une climatisation."
  "Quelqu’un paie sa facture, tous les mois."

SWIPE CUE (left side, below the explanation, small, uppercase,
           letter-spaced, in the accent colour): "GLISSE" followed by
           a solid triangular arrow pointing right.

FOOTER: the logo, per the LOGO INTEGRATION block, bottom-LEFT, just
ABOVE the 480 px bottom safe strip and well clear of the 240 px right
strip.

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Top to bottom, inside the live area:
  1. LABEL and COUNTER
  2. THE FACT, two stacked lines     <- the loudest zone
  3. THE EXPLANATION, three quiet lines
  4. SWIPE CUE
  5. THE SOLID SUBJECT ON ITS SURFACE  <- the largest zone
  6. LOGO
The hierarchy must be brutal: ONE block is enormous, everything else
is small.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM: no translation, no rephrasing, no
  shortening, no added punctuation, no exclamation marks.
- Correct French typographic apostrophes ’ exactly as written:
  "N’EXISTE", "n’est", "l’électricité", "Quelqu’un".
- Correct diacritics: "bâtiment", "électricité", "climatisation".
- The fact must be readable at 20% of the image size.
- No hashtag, no social icon, no interface element, no emoji, no
  TikTok logo, no play button.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO price, NO amount, NO currency, NO offer, NO commercial call to
  action. This carousel sells nothing at all.
- NO invented statistics, percentages or figures of any kind.
- NO cloud, NO mist, NO vapour, NO fog, NO floating object anywhere:
  the image contradicts the word, it must not illustrate it.
- NO first name, no age, no portrait, no face, no human figure.
- NO recognisable third-party brand, app name or interface.
- NO watermark, no frame, no border. ONE single idea.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1920 image, publication-ready,
high-fidelity text rendering.
===========================================================
```

### PROMPT · image 2 sur 3

```
===========================================================
NEBULA AGENCY — TIKTOK CAROUSEL, LESSON — SLIDE 2 OF 3
===========================================================

ATTACHED INPUTS — THREE attachments.
Identify the first two BY THEIR CONTENT, not by their order.

  THE LOGO = the attachment showing the NEBULA Agency logo: a purple
     and blue cosmic swirl above the wordmark "NEBULA", with "AGENCY"
     underneath, on a transparent background. An ASSET TO PLACE,
     exactly as provided, never a style reference.

  THE STYLE REFERENCE = the attachment that is a designed image with
     its own subject and palette. It is the MATERIAL of the post.

  SLIDE 1 = the image you generated just before, the first slide of
     this carousel. It is the CONSISTENCY REFERENCE.

-----------------------------------------------------------
CONSISTENCY — the most important instruction of this prompt
-----------------------------------------------------------
Match SLIDE 1 exactly on: the subject and how it is rendered, the
palette, the texture and grain, the lighting, the type family and
weight, the label, the counter, the margins, the safe zones and the
logo placement. The three slides must read as one object when swiped.
ONE thing changes in the staging, described below, plus the words.

-----------------------------------------------------------
THE STAGING — this is the whole idea of the image
-----------------------------------------------------------
THE NAME POINTS, IT DOES NOT HOLD.
The subject sits at ONE side of the live area, solid and grounded as
in slide 1.
At the OPPOSITE side, alone in empty space, floats a small flat plate,
thin as paper and visibly EMPTY: nothing engraved on it, no thickness,
no contents, nothing inside. It is a marker, and it holds nothing.
A single thin line of light runs from that empty plate, across the
open space, and lands on the subject. The line only points; it carries
nothing along it.
The distance between the small empty plate and the solid subject is
the whole message: the name is here, the thing is over there.
No arrow head, no icon, no diagram, no text on the plate, no phone,
no screen, no hand.

-----------------------------------------------------------
LOGO INTEGRATION
-----------------------------------------------------------
Same rules as slide 1: transparency preserved, no box, no plate behind
it, no outline, no glow, no shadow, never redrawn or recoloured,
placed on a calm area, same size and same position as slide 1.

-----------------------------------------------------------
FORMAT AND SAFE ZONES — identical to slide 1
-----------------------------------------------------------
1080 x 1920 px, 9:16. The BOTTOM 480 px and the RIGHT 240 px are
covered by the TikTok interface: nothing that matters goes there.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (same place, same size): "LE SAVIEZ-VOUS ?"
COUNTER (top-right): "2/3"

THE FACT (upper half, left-aligned, ENORMOUS all caps, condensed,
          tight tracking, three stacked lines filling the live width,
          the accent colour of the style reference on the last line):
  "TON ADRESSE"
  "N’EST PAS"
  "TON SITE."

THE EXPLANATION (under it, MUCH smaller, quiet, three lines):
  "C’est un nom dans un annuaire géant."
  "Il ne contient rien : il dit seulement où aller chercher."
  "C’est pour ça qu’on peut changer de machine sans changer de nom."

SWIPE CUE (left side, below, small, uppercase, letter-spaced, in the
           accent colour): "GLISSE" followed by a solid triangular
           arrow pointing right.

FOOTER: the logo, per the LOGO INTEGRATION block, bottom-left, same
size and position as slide 1.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM. No translation, no rewording.
- Correct French typographic apostrophes ’ exactly as written:
  "N’EST", "C’est", "qu’on".
- Correct diacritics: "géant", "où".
- The fact must be readable at 20% of the image size.
- No text of any kind on the small floating plate: it is empty.
- No hashtag, no social icon, no emoji, no interface element.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO price, NO amount, NO offer, NO commercial call to action.
- NO invented statistics, percentages or figures of any kind.
- NO first name, no age, no portrait, no face, no human figure.
- NO recognisable third-party brand, app name or interface.
- NO watermark, no frame, no border. ONE single idea.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1920 image, publication-ready,
high-fidelity text rendering.
===========================================================
```

### PROMPT · image 3 sur 3

```
===========================================================
NEBULA AGENCY — TIKTOK CAROUSEL, LESSON — SLIDE 3 OF 3
===========================================================

ATTACHED INPUTS — THREE attachments.
Identify the first two BY THEIR CONTENT, not by their order.

  THE LOGO = the attachment showing the NEBULA Agency logo: a purple
     and blue cosmic swirl above the wordmark "NEBULA", with "AGENCY"
     underneath, on a transparent background. An ASSET TO PLACE,
     exactly as provided, never a style reference.

  THE STYLE REFERENCE = the attachment that is a designed image with
     its own subject and palette. It is the MATERIAL of the post.

  SLIDE 2 = the image you generated just before, the second slide of
     this carousel. It is the CONSISTENCY REFERENCE.

-----------------------------------------------------------
CONSISTENCY — the most important instruction of this prompt
-----------------------------------------------------------
Match SLIDE 2 exactly on: the subject and how it is rendered, the
palette, the texture and grain, the type family and weight, the label,
the counter, the margins, the safe zones and the logo placement.
This slide closes the lesson, so its light is a little fuller and
warmer than the two before: same world, resolved.

-----------------------------------------------------------
THE STAGING — this is the whole idea of the image
-----------------------------------------------------------
THE ORIGINAL STAYS, THE COPIES LEAVE.
The subject sits at the centre, solid, sharp, perfectly still and
COMPLETELY INTACT: it loses nothing, it does not fade, it does not
crumble, it is not consumed.
From it, DOZENS of translucent copies of that same subject stream
outward in every direction, thinning and fading as they travel toward
the edges of the frame. They are ghosts of it, identical in shape,
lighter and lighter as they go.
The essential point: the source is exactly as solid as before, while
the copies keep leaving. Nothing is being taken from it. Make that
readable at a glance.
No arrow, no icon, no diagram, no phone, no screen, no hand, no
duplication grid, no photocopier.

-----------------------------------------------------------
LOGO INTEGRATION
-----------------------------------------------------------
Same rules as slides 1 and 2: transparency preserved, no box, no
plate, no outline, no glow, no shadow behind it, never redrawn or
recoloured, placed on a calm area, same size and same position.

-----------------------------------------------------------
FORMAT AND SAFE ZONES — identical to slides 1 and 2
-----------------------------------------------------------
1080 x 1920 px, 9:16. The BOTTOM 480 px and the RIGHT 240 px are
covered by the TikTok interface: nothing that matters goes there.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (same place, same size): "LE SAVIEZ-VOUS ?"
COUNTER (top-right): "3/3"

THE FACT (upper half, left-aligned, ENORMOUS all caps, condensed,
          tight tracking, three stacked lines filling the live width,
          the accent colour of the style reference on the last line):
  "LE SITE NE"
  "VIENT JAMAIS"
  "À TOI."

THE EXPLANATION (under it, MUCH smaller, quiet, three lines):
  "Quand tu ouvres une page, rien ne quitte la machine d’en face."
  "On t’en envoie une copie. L’original ne bouge pas."
  "C’est pour ça qu’un million de personnes peuvent la lire en même temps."

THE LESSON (under the explanation, medium size, in the accent colour,
            set apart with real breathing space above it):
  "La machine peut changer. Le nom, lui, reste à toi."

CALL TO ACTION (a single small solid pill shape in the accent colour,
                uppercase, tight tracking, at the left of the live
                area below the lesson): "ABONNE-TOI"
It is a printed graphic shape, never an app button, never a heart or
bell icon, never a screenshot of an interface.
There is NO swipe cue on this slide: the lesson ends here.

FOOTER: the logo, per the LOGO INTEGRATION block, bottom-left, same
size and position as slides 1 and 2.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM. No translation, no rewording.
- Correct French typographic apostrophes ’ exactly as written:
  "d’en", "t’en", "L’original", "C’est", "qu’un".
- Correct diacritics: "À TOI", "même".
- "un million" is written in letters, never in figures.
- The fact must be readable at 20% of the image size.
- No hashtag, no social icon, no emoji, no interface element.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO price, NO amount, NO offer. The only call to action is the
  subscribe pill.
- NO invented statistics, percentages or figures of any kind.
- NO first name, no age, no portrait, no face, no human figure.
- NO recognisable third-party brand, app name or interface.
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
Le nuage n’existe pas.

Ton site n’est pas dans le ciel. Il est sur une machine, dans un bâtiment, avec
de l’électricité et une climatisation, et quelqu’un paie sa facture tous les mois.

Ton adresse, elle, ne contient rien. C’est un nom dans un annuaire géant qui dit
seulement où aller chercher. C’est pour ça qu’on peut changer de machine sans
changer de nom.

Et quand tu ouvres une page, rien ne quitte la machine d’en face : on t’en envoie
une copie. L’original ne bouge pas. C’est pour ça qu’un million de personnes
peuvent la lire en même temps sans se gêner.

Voilà. Tu te couches moins bête.

#cotonou #benin #229 #culturegenerale #internet #business
```

**Le premier commentaire, à poster soi-même :**

> Lequel des trois tu ne savais pas ? Réponds 1, 2 ou 3.

### Contrôles propres à ce carrousel

| Contrôle | Pourquoi |
|---|---|
| **Aucun nuage, aucune brume, rien qui flotte sur la 1** | l'image contredit le mot, elle ne doit surtout pas l'illustrer |
| **La petite plaque de la 2 est vraiment vide** | si le modèle écrit quelque chose dessus, le fait devient faux |
| **Sur la 3, la source ne diminue pas** | le modèle voudra la faire s'effriter ; c'est exactement le contraire du fait |
| Le même sujet, la même surface sur les 3 | sinon ce sont trois posts, pas un carrousel |
| « GLISSE » sur la 1 et la 2, jamais sur la 3 | la leçon se termine, on ne renvoie pas ailleurs |
| Aucun prix, aucune offre | c'est un post qui donne, il achète le droit d'être cru plus tard |

---

## 5. Contrôles avant publication

| Contrôle | Pourquoi |
|---|---|
| Réduire à 20 % | Si l'accroche ne se lit plus, le post est mort dans le fil |
| Poser l'image dans TikTok et regarder | Le seul moyen de voir ce que l'interface recouvre |
| Rien dans les 480 px du bas ni les 240 px de droite | Sinon le titre finit derrière les boutons |
| **Le logo n'a aucun cadre derrière lui** | Une plaque blanche sous le logo, et tout le post a l'air amateur |
| **Le logo est encore lisible à 20 %** | Avec le fichier non détouré, il tombait à 5 % de la largeur |
| Le sujet vient bien de la référence | Si le modèle a inventé un décor, le post ne ressemble plus à la marque |
| Les deux moitiés du sujet sont franchement différentes | C'est toute l'image : si le contraste est mou, il n'y a plus d'idée |
| Un seul bloc énorme | Deux blocs énormes, et aucun n'est lu |
| Aucun chiffre, aucun pourcentage | Règle absolue de la rubrique |

---

## 6. Les prochains posts TikTok

Le gabarit se réutilise tel quel : on garde le label, la hiérarchie brutale, les zones
mortes, le pied de page, et on ne change que **l'accroche, la valeur et la mise en scène**.

| Post | L'accroche | La valeur qu'il donne |
|---|---|---|
| **Le prix caché** | « CE N'EST PAS TON PRIX QUI FAIT FUIR. C'EST QU'IL SOIT CACHÉ. » | tout le monde n'ose pas demander |
| **Le locataire** | « TA PAGE NE T'APPARTIENT PAS. » | un compte se bloque, une adresse non |
| **Les douze messages** | « DOUZE MESSAGES POUR UNE VENTE. » | chaque question posée est une vente ralentie |
| **L'heure du soir** | « ON T'ÉCRIT QUAND TU DORS. » | la décision se prend entre 21 h et 23 h |

⚠️ **Ne jamais enchaîner deux posts qui font peur.** Entre deux, en publier un qui ne vend
rien du tout et donne un savoir utile. C'est lui qui achète le droit d'être cru la fois
d'après.

---

*NEBULA Agency · Cotonou, Bénin · Document vivant. Ajouter chaque post TikTok ici.*

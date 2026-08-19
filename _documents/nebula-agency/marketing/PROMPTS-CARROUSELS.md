# CARROUSELS « LE SAVIEZ-VOUS ? »
## Direction artistique « MARBRE & ROUGE » · prompts image par image

> **Le principe du carrousel.** Un post fixe raconte une idée. Un carrousel raconte une
> **histoire en trois temps** : on fait peur, on explique, on tend la main. Chaque image
> doit donner envie de glisser vers la suivante, et la dernière doit demander quelque
> chose. C'est le seul format où on a le droit de réclamer l'abonnement, parce qu'on a
> donné pendant deux images avant de demander.
>
> **Ce qui ne change jamais.** Le label « LE SAVIEZ-VOUS ? » : même texte, même place,
> même casse, même taille, sur les trois images. C'est l'ancre de reconnaissance de la
> rubrique. Tout le reste peut bouger, ça jamais.
>
> Version 1.0 · 2026-08-04

---

## 1. La direction artistique « MARBRE & ROUGE »

C'est une **deuxième** direction, en plus de celle du prompt-maître
(`PROMPTS-POSTS-LE-SAVIEZ-VOUS.md`, fond nuit + violet). Les deux sont valables, mais
**on ne les mélange pas dans une même campagne** : on choisit une direction et on la tient
au moins un mois. Le lecteur reconnaît une série à sa couleur avant de reconnaître son logo.

**Référence de style :** `references/REF-marbre-rouge.jpg`

Ses six marqueurs, à respecter sur les trois images :

1. **Trois valeurs, pas une de plus** : papier os `#EDEAE5`, encre `#111111`, rouge
   éditorial `#D6001C`. Aucun dégradé, aucune lueur, aucun néon.
2. **Une sculpture de marbre** au centre, photographique, détourée sur le papier, presque
   sans ombre portée.
3. **Deux barres rouges pleines** qui passent derrière les épaules, bord à bord, comme une
   surimpression d'imprimerie.
4. **L'annotation au carré rouge** : un petit carré vide, un trait fin, une légende de deux
   lignes en tout petit rouge. C'est le détail qui fait « magazine » et pas « publicité ».
5. **La typo en trois coupes** : italique serif noire, puis **UN SEUL MOT EN CAPITALES
   ROUGES ÉNORMES**, puis une ligne sans-serif noire qui retourne le sens.
6. **Le pied fixe** : logo NEBULA en bas à gauche, `nebula-agency.online` en bas à droite,
   dans un gris discret.

⚠️ **Ce carrousel est en MODE A** : la référence est déjà une image NEBULA, donc on hérite
**aussi de sa palette**. Ne pas y coller le violet du prompt-maître.

---

## 2. Comment l'envoyer à ChatGPT

**Une image à la fois, dans la même conversation.** Jamais les trois d'un coup : le modèle
sacrifie toujours la troisième.

**Pièces jointes de l'image 1, dans cet ordre exact :**

| Ordre | Fichier | Rôle |
|---|---|---|
| 1 | `_documents/nebula-agency/marketing/references/REF-marbre-rouge.jpg` | le style à imiter |
| 2 | `logo/nebula-logo-detoure.png` | le logo, à poser tel quel |

⚠️ **Envoyer le logo DÉTOURÉ, jamais celui de `nebula-affilies/static/`.** Ce dernier fait
900 x 600 px alors que le logo n'y occupe que 382 x 256 px : le reste est du vide
transparent. Demandé « à 12 % de la largeur », le logo réellement visible tombait à 5 %.

⚠️ **C'est l'ordre inverse de celui du prompt-maître de 2026-07-30**, qui mettait le logo en
premier. On suit ici l'ordre que Mongazi utilise vraiment, et chaque prompt commence donc
par un bloc anti-confusion qui nomme les deux rôles deux fois. Si le logo se fait quand même
réinterpréter, remettre le logo en premier et échanger « IMAGE 1 » et « IMAGE 2 » dans le
prompt.

**Pour les images 2 et 3 :** rester dans la même conversation et **joindre en plus l'image
que le modèle vient de générer**. Sans ça, le marbre change de grain, la marge bouge de
trois pixels, et le carrousel ne se lit plus comme un seul objet quand on le glisse.

**Le seul test qui compte :** réduire le résultat à 20 % de sa taille. Si le mot rouge ne se
lit plus, on regénère. C'est comme ça qu'on le verra dans un fil.

---

## 3. Le carrousel n° 1 · « INTROUVABLE »

**Le sujet :** sur internet, ne pas être trouvé ne veut pas dire passer inaperçu. Ça veut
dire être remplacé, tous les soirs, par quelqu'un d'autre, sans jamais le savoir.

**L'histoire en trois temps :**

| Image | Rôle | Ce qu'elle fait au lecteur |
|---|---|---|
| 1/3 | **Le choc** | « Introuvable ne veut pas dire discret. » Il se reconnaît, il glisse. |
| 2/3 | **Le mécanisme et l'urgence** | Le téléphone ne répond jamais « rien » : il répond quelqu'un. Et c'est ce soir. |
| 3/3 | **Le cadeau et la demande** | Un test gratuit à faire tout de suite, puis « aimez, abonnez-vous ». |

**Aucun chiffre nulle part.** Pas de pourcentage, pas de statistique : tout ce qui est
affirmé ici est vérifiable par le lecteur avec son propre téléphone, en dix secondes. C'est
ce qui rend la peur crédible au lieu de la rendre suspecte.

---

### PROMPT · IMAGE 1 sur 3

```
===========================================================
NEBULA AGENCY — CAROUSEL "LE SAVIEZ-VOUS ?" — SLIDE 1 OF 3
===========================================================

ATTACHED INPUTS — two attachments, two different roles.
Read this block twice. Swapping the two roles ruins the image.

  IMAGE 1 = THE STYLE REFERENCE.
     An existing NEBULA post. Inherit its DESIGN LANGUAGE *and* its
     COLOUR PALETTE. Its subject, its words, its message and its
     caption must never appear in the output.

  IMAGE 2 = THE LOGO.
     The official NEBULA Agency logo. An ASSET TO PLACE, exactly as
     provided. Never a style reference, never a subject to
     reinterpret, never redrawn, restyled, recoloured or cropped.

  To be explicit: the STYLE comes from IMAGE 1. The LOGO is IMAGE 2.

-----------------------------------------------------------
TASK
-----------------------------------------------------------
Create ONE original editorial social graphic for NEBULA Agency, a
digital studio in Cotonou, Benin, serving West African merchants.
This is SLIDE 1 of a 3-slide carousel. Its only job is to stop the
scroll, disturb the reader, and make them swipe.
This is editorial content, never an advertisement.

-----------------------------------------------------------
ART DIRECTION — "MARBRE & ROUGE", locked
-----------------------------------------------------------
Palette, exactly three values, nothing else:
  paper       warm bone off-white #EDEAE5, with a faint circular
              brush-swept texture and fine printed paper grain
  ink         near-black #111111, for all body and sans-serif type
  signature   editorial red #D6001C, for the huge headline word,
              the bars, the annotation line and its caption
No gradient, no glow, no neon, no drop shadow, no 3D render look,
no stock-photo look, no additional colour of any kind.

CENTRAL OBJECT: a CLASSICAL WHITE MARBLE SCULPTURE, museum lighting,
photographic realism, cleanly cut out on the paper background with
almost no cast shadow. It is a carved sculpture, never a photograph
of a real person.

GRAPHIC OVERLAY: two solid red horizontal bars pass BEHIND the
sculpture's shoulders, running edge to edge, like a printing
overprint. They sit behind the marble, never in front of it.

ANNOTATION DEVICE: one small empty red-outlined square placed in the
negative space, joined by a single thin straight red line to the
exact detail it names, with a two-line caption in tiny red type.

TYPOGRAPHY — three contrasting cuts, exactly as in the reference:
  line A : elegant SERIF ITALIC, black, medium size
  line B : MASSIVE CONDENSED SERIF, ALL CAPS, red, filling the full
           width of the canvas. By far the loudest element.
  line C : clean SANS-SERIF, black, medium size

-----------------------------------------------------------
SERIES ANCHOR — identical on all three slides
-----------------------------------------------------------
Top-left, small uppercase widely letter-spaced muted grey type:
"LE SAVIEZ-VOUS ?"
Top-right, same size, same grey, same baseline: "1/3"
This label never changes across the series: same words, same place,
same size, same colour, same tracking.

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
    image is viewed at 20% of its size, bottom-left, aligned to the
    same margin as the body text.
A logo pasted on a white rectangle is a failed image.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL ....... "LE SAVIEZ-VOUS ?"        (top-left)
COUNTER ..... "1/3"                     (top-right)

HEADLINE ....
  line A (serif italic, black) ....... "Sur internet,"
  line B (HUGE CAPS, red) ............ "INTROUVABLE"
  line C (sans-serif, black) ......... "ne veut pas dire discret."

VISUAL (centre of canvas, about 42% of its height):
  A classical white marble bust of a young man with carved curly
  hair, facing the viewer, cropped at the chest.
  The RIGHT THIRD of the head is DISINTEGRATING into a drift of
  small square blocks that scatter to the right, thin out, and
  vanish into the bone paper. The dissolution reads as a digital
  image losing its pixels, not as broken or chipped stone: clean
  square fragments, decreasing in size, fading out. What remains of
  the face is intact, calm, and looking straight at the viewer.
  Two solid red bars behind the shoulders.
  Annotation: small red square in the empty space on the right,
  thin red line pointing to the emptiest part of the drift, where
  the face is already gone.
  Annotation caption (tiny red type, two lines):
  "ce que le client trouve"

BODY (bottom zone, black sans-serif, two lines, one bold segment):
  "Celui qui vous cherche et ne trouve rien ne se dit pas que vous
  êtes discret. Il se dit que vous n'existez plus."
  Set in bold: "vous n'existez plus"

SWIPE CUE (bottom right, just above the site URL):
  a small solid red pill containing, in bone-white uppercase
  letter-spaced type: "GLISSEZ"
  followed by a thin white arrow pointing right.

FOOTER (identical on all three slides):
  the logo from IMAGE 2, bottom-left, per the LOGO INTEGRATION block.
  "nebula-agency.online" bottom-right, tiny muted grey type.

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Format: 4:5 vertical, 1080 x 1350 px.
Four horizontal zones, top to bottom:
  1. LABEL + COUNTER ....................  ~8%
  2. HEADLINE, three stacked lines ......  ~22%
  3. MARBLE VISUAL, the whole point .....  ~42%
  4. BODY, swipe cue, logo and URL ......  ~28%
Generous margins. Nothing touches the edges. Real negative space
around the sculpture: the emptiness is part of the message.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted in the CONTENT block, plus
  "nebula-agency.online". Any extra word is a failure.
- Reproduce them VERBATIM: do not translate, rephrase, shorten,
  complete or correct them.
- Correct French diacritics and apostrophes: é è ê à â î ô û ç ù,
  and the apostrophes in "n'existez", "d'à", "l'heure".
- The huge red word must stay legible when the image is viewed at
  20% of its size.
- No other words, labels, captions, tags, numbers, UI elements,
  hashtags or social icons anywhere in the image.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO invented statistics, percentages or figures of any kind.
- NO human faces, no photographs of real people, no recognisable
  third-party brand, logo or app interface.
- NO watermark, no signature, no frame, no border.
- ONE single idea in this image.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1350 graphic, publication-ready,
high-fidelity text rendering.
===========================================================
```

---

### PROMPT · IMAGE 2 sur 3

```
===========================================================
NEBULA AGENCY — CAROUSEL "LE SAVIEZ-VOUS ?" — SLIDE 2 OF 3
===========================================================

ATTACHED INPUTS — three attachments, three different roles:

  IMAGE 1 = THE STYLE REFERENCE. Inherit its design language and
            its palette. Its subject and its words never appear.
  IMAGE 2 = THE LOGO. An asset to place exactly as provided,
            never a style reference, never redrawn or recoloured.
  IMAGE 3 = SLIDE 1 OF THIS CAROUSEL, which you generated just
            before. This is the CONSISTENCY REFERENCE.

-----------------------------------------------------------
CONSISTENCY — the most important instruction of this prompt
-----------------------------------------------------------
This image is the SECOND of three, swiped one after the other.
Match IMAGE 3 exactly on:
  - the paper colour, its texture and its grain
  - the marble treatment, its lighting and its whiteness
  - the exact size, weight, tracking and position of the label,
    the counter, the headline lines, the body and the footer
  - the margins, on all four sides
Only these change: the sculpture's pose, the headline words, the
annotation caption, the body text and the counter.
The two images must feel printed on the same sheet, the same day.

-----------------------------------------------------------
ART DIRECTION — identical to slide 1
-----------------------------------------------------------
Paper bone #EDEAE5 with printed grain, ink #111111, single
editorial red #D6001C. No other colour. Classical white marble
sculpture, photographic, cut out, almost no cast shadow. Two solid
red bars passing behind the shoulders. One red-outlined annotation
square joined by a thin red line to the detail it names.
Typography in three cuts: serif italic black, MASSIVE CONDENSED
SERIF CAPS in red, clean sans-serif black.

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
    image is viewed at 20% of its size, bottom-left, aligned to the
    same margin as the body text.
A logo pasted on a white rectangle is a failed image.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL ....... "LE SAVIEZ-VOUS ?"        (top-left, unchanged)
COUNTER ..... "2/3"                     (top-right)

HEADLINE ....
  line A (serif italic, black) ....... "Quand on vous cherche,"
  line B (HUGE CAPS, red) ............ "UN AUTRE"
  line C (sans-serif, black) ......... "apparaît à votre place."

VISUAL (centre of canvas, about 42% of its height):
  THE SAME marble bust as slide 1, now whole again but seen in
  three-quarter PROFILE, turned to the left, looking at an object
  floating in front of it.
  That object: a thin upright slab of the same white marble, carved
  into the silhouette of a phone screen, floating vertically.
  Carved in relief into the slab, from top to bottom:
    - a search field at the top, empty, with NO readable text in it
    - three result rows below it
    - the FIRST result row is a SOLID RED FILLED BLOCK
    - the two rows beneath it are hollow, empty carved grooves
  The red block is the only saturated element inside the marble.
  Two solid red bars behind the shoulders.
  Annotation: small red square in the negative space, thin red line
  pointing precisely at the solid red result row.
  Annotation caption (tiny red type, two lines):
  "celui qu'on trouve"

BODY (bottom zone, black sans-serif, two lines, one bold segment):
  "Un téléphone ne répond jamais « rien » : il répond quelqu'un.
  Et ce n'est pas pour dans un an, c'est ce soir."
  Set in bold: "c'est ce soir"
  Keep the French guillemets « » exactly as written, with their
  inner spaces.

SWIPE CUE (bottom right, just above the site URL):
  a single thin red arrow pointing right, discreet, no pill,
  no word.

FOOTER: the logo from IMAGE 2, bottom-left, per the LOGO INTEGRATION
block, same size and same position as slide 1.
"nebula-agency.online" bottom-right in tiny muted grey type.

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Format: 4:5 vertical, 1080 x 1350 px.
Same four zones and same proportions as slide 1:
label 8%, headline 22%, marble visual 42%, bottom block 28%.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the quoted strings, plus "nebula-agency.online".
- Reproduce them VERBATIM. No translation, no rewording.
- Correct French diacritics and apostrophes: "apparaît", "n'est",
  "qu'on", "à votre place".
- The huge red word must survive being viewed at 20% size.
- No readable text inside the carved search field. No app name,
  no brand, no interface label, no icon of any known product.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO invented statistics, percentages or figures.
- NO human faces, no real people, no recognisable third-party
  brand or app interface.
- NO watermark, no frame, no border.
- ONE single idea in this image.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1350 graphic, publication-ready,
high-fidelity text rendering.
===========================================================
```

---

### PROMPT · IMAGE 3 sur 3

```
===========================================================
NEBULA AGENCY — CAROUSEL "LE SAVIEZ-VOUS ?" — SLIDE 3 OF 3
===========================================================

ATTACHED INPUTS — three attachments, three different roles:

  IMAGE 1 = THE STYLE REFERENCE. Design language and palette only.
  IMAGE 2 = THE LOGO. An asset to place exactly as provided,
            never a style reference, never redrawn or recoloured.
  IMAGE 3 = SLIDE 2 OF THIS CAROUSEL, which you generated just
            before. This is the CONSISTENCY REFERENCE.

-----------------------------------------------------------
CONSISTENCY — the most important instruction of this prompt
-----------------------------------------------------------
This is the THIRD and last slide of the carousel. Match IMAGE 3
exactly on paper colour and grain, marble treatment and lighting,
type sizes and tracking, and margins on all four sides.
Only these change: the sculpture's state, the headline words, the
annotation caption, the body text, the counter, and one new
element described below (the call-to-action band).

-----------------------------------------------------------
ART DIRECTION — identical to slides 1 and 2
-----------------------------------------------------------
Paper bone #EDEAE5 with printed grain, ink #111111, single
editorial red #D6001C. No other colour. Classical white marble
sculpture, photographic, cut out, almost no cast shadow. Two solid
red bars passing behind the shoulders. One red-outlined annotation
square joined by a thin red line. Typography in three cuts.

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
    image is viewed at 20% of its size, bottom-left, aligned to the
    same margin as the body text.
A logo pasted on a white rectangle is a failed image.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL ....... "LE SAVIEZ-VOUS ?"        (top-left, unchanged)
COUNTER ..... "3/3"                     (top-right)

HEADLINE ....
  line A (serif italic, black) ....... "Ce soir,"
  line B (HUGE CAPS, red) ............ "EXISTEZ"
  line C (sans-serif, black) ......... "là où on vous cherche."

VISUAL (centre of canvas, about 38% of its height):
  THE SAME marble bust, now facing the viewer, WHOLE and intact:
  no missing fragments, no dissolution, the stone perfectly closed.
  It reads as the repaired version of slide 1.
  The same carved marble slab floats in front of it, at chest
  height, slightly smaller than in slide 2.
  On the slab: the FIRST result row is again a SOLID RED FILLED
  BLOCK, and inside that red block sits a tiny bone-white
  silhouette of THIS VERY BUST. The two rows beneath stay hollow
  and empty.
  Two solid red bars behind the shoulders.
  Annotation: small red square in the negative space, thin red line
  pointing at the tiny white silhouette inside the red block.
  Annotation caption (tiny red type, two lines):
  "vous, cette fois"

BODY (black sans-serif, two lines, one bold segment):
  "Faites le test maintenant : tapez le nom de votre commerce dans
  votre téléphone. Ce que vous voyez, vos clients le voient aussi."
  Set in bold: "vos clients le voient aussi"

CALL-TO-ACTION BAND (new on this slide only):
  A solid red horizontal band, full canvas width minus the margins,
  placed between the body text and the footer, about 9% of the
  canvas height. Inside it, centred, in bone-white uppercase
  letter-spaced sans-serif:
  "AIMEZ CE POST · ABONNEZ-VOUS"
  Immediately below the band, centred, in tiny black sans-serif:
  "Une vérité du digital chaque semaine."
  The band must read as the same red as the two bars behind the
  bust: same ink, promoted to a button.

FOOTER: the logo from IMAGE 2, bottom-left, per the LOGO INTEGRATION
block, same size and same position as slides 1 and 2.
"nebula-agency.online" bottom-right in tiny muted grey type.

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Format: 4:5 vertical, 1080 x 1350 px.
Five horizontal zones, top to bottom:
  1. LABEL + COUNTER ....................  ~8%
  2. HEADLINE, three stacked lines ......  ~21%
  3. MARBLE VISUAL ......................  ~38%
  4. BODY ...............................  ~12%
  5. CTA BAND, its sub-line, logo, URL ..  ~21%
Nothing touches the edges. The band is the only filled rectangle
in the bottom half: it must feel deliberate, not decorative.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the quoted strings, plus "nebula-agency.online".
- Reproduce them VERBATIM. No translation, no rewording, no
  added exclamation marks.
- Correct French diacritics and apostrophes: "là où", "vérité",
  "téléphone", "Faites le test".
- Use the middle dot "·" in "AIMEZ CE POST · ABONNEZ-VOUS",
  never a hyphen, never a bullet, never an emoji.
- The huge red word must survive being viewed at 20% size.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO invented statistics, percentages or figures.
- NO human faces, no real people, no recognisable third-party
  brand, app interface, heart icon, bell icon or social button:
  the call to action is typographic only.
- NO watermark, no frame, no border.
- ONE single idea in this image.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1350 graphic, publication-ready,
high-fidelity text rendering.
===========================================================
```

---

## 4. La légende de la publication

À coller sous le carrousel. Elle refait le chemin des trois images, pour ceux qui lisent
sans glisser, et elle redemande l'abonnement une seule fois, à la fin.

```
Ce soir, quelqu'un va taper le nom de votre commerce dans son téléphone.

S'il ne trouve rien, il ne se dira pas que vous êtes discret. Il se dira que
c'est fermé, ou que ce n'est pas sérieux. Et il ne vous le dira jamais.

Le pire n'est pas là. Un téléphone ne répond jamais « rien » : il répond
quelqu'un. Quand on ne vous trouve pas, on trouve un autre. Ce client, vous
ne saurez même pas qu'il a existé.

Le test coûte dix secondes, faites-le maintenant : tapez le nom de votre
commerce dans votre propre téléphone. Ce que vous voyez à l'écran, c'est
exactement ce que vos clients voient.

Si ce post vous a appris quelque chose : aimez-le, et abonnez-vous.
Une vérité du digital chaque semaine, sans jargon.

NEBULA Agency · Cotonou
nebula-agency.online

#Cotonou #Benin #Commerce #Digital #Entrepreneur #NebulaAgency
```

**Le premier commentaire, à poster soi-même dans la foulée :**

> Faites le test et dites-moi en commentaire ce que vous avez trouvé en tapant le nom de
> votre commerce. Je réponds à tout le monde.

C'est ce commentaire qui fait vivre le post : une question fermée, à laquelle on peut
répondre en trois mots depuis un téléphone.

---

## 5. Contrôles avant publication

| Contrôle | Pourquoi |
|---|---|
| Réduire les 3 images à 20 % | Si le mot rouge ne se lit plus, le post est mort dans le fil |
| Le label « LE SAVIEZ-VOUS ? » identique sur les 3 | C'est l'ancre de la rubrique, elle ne bouge jamais |
| Les 3 côte à côte, dans l'ordre | Même papier, même marbre, mêmes marges, sinon ça se voit |
| Les accents et les apostrophes | Un « apparait » sans accent circonflexe et la crédibilité tombe |
| Le logo n'a pas été redessiné | Le modèle adore le réinterpréter, c'est le défaut n° 1 |
| Aucun chiffre, aucun pourcentage | Règle absolue de la rubrique, sans exception |
| Aucune marque tierce lisible | Ni nom d'application, ni interface reconnaissable |

---

## 6. Dépannage

| Ce qui rate | Ce qu'on ajoute au prompt |
|---|---|
| Le violet du prompt-maître revient | `MODE A: inherit the reference palette. Bone paper, black ink, one editorial red. No violet, no blue, no cyan anywhere.` |
| Le sujet de la référence réapparaît | `IMAGE 1 is a FORM reference only. Its subject must not appear. If in doubt, ignore its content entirely.` |
| Le logo est redessiné | `The logo must be a pixel-faithful placement of IMAGE 2, the second attachment. Treat it as a pasted asset, not as something to generate.` Si ça persiste, remettre le logo en première position et échanger les numéros dans le prompt |
| **Le logo arrive dans un cadre blanc** | `IMAGE 2 has a transparent background. Place it directly on the artwork with NO box, NO plate, NO card, NO outline, NO glow and NO shadow behind it.` |
| **Le logo est minuscule** | Envoyer `logo/nebula-logo-detoure.png` et non le fichier de `nebula-affilies/static/`, dont 58 % de la surface est du vide |
| Les 3 images ne se ressemblent pas | Regénérer la 2 et la 3 **en joignant la précédente**, avec `Match IMAGE 3 exactly: same paper, same grain, same margins, same type sizes.` |
| « INTROUVABLE » déborde ou casse | Remplacer par `"INVISIBLE"`, deux lettres de moins, même sens |
| Du texte parasite s'ajoute | `Render ONLY the quoted strings. Any additional word is a failure.` |
| Le marbre a l'air d'une vraie personne | `It is a carved marble sculpture, not a photograph of a person. Visible stone surface and tool marks.` |

---

## 7. Pour le prochain carrousel

Le gabarit se réutilise tel quel : on garde la direction, le label, les trois zones, le
pied de page, et on ne change que **l'histoire en trois temps**. Trois sujets déjà prêts,
tirés de la série des posts fixes :

| Carrousel | Image 1, le choc | Image 2, le mécanisme | Image 3, la sortie |
|---|---|---|---|
| **Le prix qu'on n'ose pas demander** | « Il est parti sans demander le prix. » | La gêne fait fuir en silence, on ne le voit jamais | Afficher ses prix, une gêne en moins |
| **Locataire ou propriétaire** | « Votre page ne vous appartient pas. » | Un compte se bloque du jour au lendemain | Une adresse à vous, qui ne se bloque pas |
| **Douze messages pour une vente** | « Douze messages pour une vente. » | Chaque question posée est une vente ralentie | Répondre avant que la question arrive |

⚠️ **Ne jamais enchaîner deux carrousels qui font peur.** Entre deux, publier un post
« cadeau pur » de la série fixe, qui ne vend rien du tout. C'est lui qui achète le droit
d'être cru la fois d'après.

---

*NEBULA Agency · Cotonou, Bénin · Document vivant. Ajouter chaque nouveau carrousel ici.*

# WHATSAPP · statuts, prompts image par image

> **Ce qui rend un statut différent de tout le reste.** Sur Instagram et sur TikTok, on
> parle à des inconnus et on demande une audience. Sur WhatsApp, **ces gens ont déjà votre
> numéro**. Il n'y a rien à leur faire suivre : il y a une conversation à ouvrir.
> Donc un statut ne demande jamais un abonnement. **Il demande une réponse.**
>
> **Et il expire dans 24 heures.** Ce qui se demande se demande maintenant.
>
> **Ce qui ne change jamais :** le label « LE SAVIEZ-VOUS ? », ancre de la rubrique.
>
> Version 1.3 · 2026-08-31

---

## 1. Les règles du statut, une fois pour toutes

**Format :** 1080 x 1920 px, 9:16.

**Les zones mortes.** WhatsApp pose son interface **par-dessus** l'image :
- les **220 premiers pixels en haut** : photo de profil, nom, heure
- les **340 derniers pixels en bas** : le champ « Répondre »

Tout ce qui compte vit dans la bande centrale, entre 220 px et 1580 px. Le logo aussi.

**On vouvoie.** Ce sont des clients, des prospects, des connaissances de Cotonou. Le
tutoiement est réservé à TikTok, où l'on parle à des inconnus plus jeunes.

**Le contraste doit être extrême.** Un statut se regarde dehors, en plein jour, l'écran à
moitié éteint. Un gris sur gris qui passait très bien sur un écran d'ordinateur disparaît.

**L'appel à l'action est une réponse, jamais un abonnement.** Et la meilleure réponse est
**un seul caractère** : un chiffre, un mot. Personne ne rédige un message depuis un statut,
tout le monde peut taper « 2 ».

**Le test :** réduire à 20 %. Si l'accroche ne se lit plus, regénérer.

---

## 2. Les deux pièces jointes, identifiées par leur contenu

Les prompts de ce document **ne comptent pas sur l'ordre des pièces jointes** : ils
identifient chaque image par ce qu'elle contient. Toute la classe d'erreur du logo pris pour
un modèle de style disparaît, quel que soit l'ordre d'envoi.

| Ce qu'on envoie | Fichier | Rôle |
|---|---|---|
| Le logo | `logo/nebula-logo-detoure.png` | posé tel quel, transparence gardée |
| La référence | l'image dont on veut le design | c'est **la matière** du post |

⚠️ **Toujours le logo DÉTOURÉ.** Celui de `nebula-affilies/static/` fait 900 x 600 px alors
que le logo n'y occupe que 382 x 256 px : **58 % du fichier est du vide transparent.**

⚠️ **Le logo est violet et bleu.** Superbe sur fond sombre, il jure sur un papier clair.

---

## 3. Statut n° 1 · « UN PAS DEDANS »

**Le sujet :** le numérique, et le fait qu'il n'y a pas besoin de tout comprendre pour
commencer. Un pas dedans suffit à changer de camp.

**L'accroche :**

> **LE NUMÉRIQUE NE VOUS REMPLACERA PAS. QUELQU'UN, SI.**

Elle rassure sur une ligne et frappe sur la suivante. Le lecteur croit reconnaître le
discours mou qu'on lui sert partout (« la technologie, l'avenir »), et la troisième ligne
**déplace la menace** : ce n'est pas une machine qui arrive, c'est son voisin. Le choc est
dans le déplacement, pas dans le volume, et il passe en une seconde.

**La valeur :** le statut démonte l'excuse la plus répandue, « je ne m'y connais pas ». Il
n'y a pas de compétence à acquérir, il y a **trois choses concrètes**, numérotées sur
l'image. Le lecteur repart avec une liste, pas avec une inquiétude.

**« Trois choses. Pas un diplôme. »** C'est la phrase qu'il doit garder en tête.

**Le mécanisme de conversion, propre à WhatsApp :** les trois choses sont **numérotées**, et
la dernière ligne demande de répondre 1, 2 ou 3. Le lecteur n'a pas à écrire une phrase, à
expliquer sa situation ni à demander un devis : il tape un chiffre. Et ce chiffre dit déjà
ce qui lui manque, donc la conversation démarre au bon endroit.

⚠️ **La promesse doit être tenue.** Qui répond un chiffre doit recevoir une vraie réponse,
utile, gratuite, le soir même. Sinon retirer la dernière ligne : un statut qui promet et ne
répond pas coûte plus cher qu'un statut qui ne demande rien.

**L'image :** « avoir un pas dedans », pris au pied de la lettre. Une fine ligne de lumière
traverse le cadre. Derrière : éteint, plat, froid. Devant : éclairé, vivant. Le sujet de la
référence se tient **sur** la ligne, avec une seule partie de lui déjà passée de l'autre
côté. Ce n'est pas un saut, c'est un pas : l'image dit exactement ce que dit le texte, sans
un mot.

⚠️ **Aucun chiffre nulle part**, sauf la numérotation 1, 2, 3 de la liste. Aucune
statistique, aucun pourcentage : règle absolue de la rubrique.

### LE PROMPT

```
===========================================================
NEBULA AGENCY — WHATSAPP STATUS — ONE IMAGE, 9:16
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
Create ONE original WhatsApp STATUS image for NEBULA Agency, a digital
studio in Cotonou, Benin, serving West African merchants and business
owners.
It is seen on a phone, often outdoors in daylight, at half screen
brightness. It has ONE SECOND to earn a pause, and it must teach
something in the next five.
Editorial and direct, never an advertisement.
It must look designed and expensive, never cheap, never homemade.

-----------------------------------------------------------
THE MATERIAL — THE STYLE REFERENCE IS THE SOURCE,
                NOT A VAGUE INSPIRATION
-----------------------------------------------------------
Build this image OUT OF the style reference. Do not invent a new
subject and do not add a decor of your own.
  KEEP    its main subject, re-staged as described below
  KEEP    its palette, its texture, its grain and its lighting
  KEEP    its typographic craft, pushed louder: the huge lines here
          are bigger and tighter than in the source
  CHANGE  its state, its framing for a 9:16 canvas, and every single
          word on it
  DROP    its original words, numbers, captions, logo and watermark:
          none of them may appear
If you find yourself inventing a new object, stop. The subject is
already in the style reference. Nothing else enters the frame.

CONTRAST: push the contrast harder than the style reference does.
This image is read outdoors, in daylight, on a dimmed screen. Any
tone that sits close to its neighbour will vanish. Text is either
clearly light on dark, or clearly dark on light. Never mid-grey on
mid-grey.

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
WhatsApp draws its own interface OVER this image:
  - the TOP 220 px are covered by the profile bar
  - the BOTTOM 340 px are covered by the reply field
Nothing that matters may sit in those two strips. All text, the logo
and the subject live inside the central band, between 220 px and
1580 px from the top. Compose as if those two strips did not exist.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (top of the safe band, small, uppercase, widely letter-spaced,
       muted): "LE SAVIEZ-VOUS ?"

HEADLINE (upper part of the safe band, left-aligned, ENORMOUS all
          caps, condensed, tight tracking and tight leading, three
          stacked lines filling the width. By far the loudest element
          of the image. The first two lines in the ink colour of the
          style reference, THE THIRD LINE in its accent colour):
  "LE NUMÉRIQUE NE"
  "VOUS REMPLACERA PAS."
  "QUELQU’UN, SI."

BRIDGE (under the headline, MUCH smaller, quiet, one line):
  "Il ne travaille pas plus que vous. Il a juste un pas dedans."

THE THREE THINGS (under the bridge, small, three numbered lines, each
                  starting with its numeral set in the accent colour,
                  the text itself in the plain text colour, generous
                  spacing between the three so the list is scannable):
  "1.  Une adresse où on vous trouve."
  "2.  Un prix qu’on peut lire."
  "3.  Une page qui répond quand vous dormez."

CLOSER (under the list, medium size, in the accent colour, set apart
        with real breathing space above it so it lands on its own):
  "Trois choses. Pas un diplôme."

CALL TO ACTION (bottom of the safe band, on its own line, in the
                accent colour, smaller than the closer):
  "Répondez 1, 2 ou 3 : je vous dis par où commencer."

FOOTER: the logo, per the LOGO INTEGRATION block, centred, placed
just ABOVE the 340 px bottom safe strip, never inside it.

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Inside the central safe band, top to bottom:
  1. LABEL
  2. HEADLINE, three stacked lines     <- the loudest zone
  3. THE SUBJECT ON ITS LINE OF LIGHT  <- the largest zone
  4. BRIDGE
  5. THE THREE NUMBERED LINES
  6. CLOSER
  7. CALL TO ACTION, then the LOGO
The hierarchy must be brutal: ONE block is enormous and everything
else is small. Two large blocks means neither gets read.
Wide margins left and right. The numbered list must read as a list at
a glance, aligned on its numerals.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM: no translation, no rephrasing, no
  shortening, no added punctuation, no exclamation marks.
- Correct French diacritics and apostrophes: "NUMÉRIQUE", "où",
  "qu’on", "diplôme", "Répondez".
- The headline must be readable at 20% of the image size.
- The only numerals anywhere in the image are the list markers
  "1.", "2." and "3." and the digits in the call to action.
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

### La légende du statut

WhatsApp permet une légende sous l'image. Une phrase, pas plus :

```
Répondez juste le chiffre qui vous manque. Je réponds à tout le monde ce soir.
```

### Le message pour la liste de diffusion

Le statut se regarde, la liste de diffusion se lit. Deux textes différents, le même soir.

```
Bonjour,

On croit qu'il faut s'y connaître pour se mettre au numérique. C'est faux.
Il n'y a pas de compétence à apprendre, il y a trois choses à avoir :

1. Une adresse où on vous trouve
2. Un prix qu'on peut lire
3. Une page qui répond quand vous dormez

Trois choses, pas un diplôme. Et on ne les fait pas toutes le même jour :
on commence par celle qui manque le plus.

Répondez 1, 2 ou 3 et je vous dis par où commencer, sans engagement.

Mongazi · NEBULA Agency
nebula-agency.online
```

⚠️ **Liste de diffusion, pas groupe.** Un groupe met tout le monde en copie et fait fuir.
Une liste de diffusion arrive comme un message personnel, et seuls ceux qui ont votre numéro
enregistré le reçoivent.

### Ce qu'on répond à chaque chiffre

Préparer les trois réponses AVANT de publier. Une réponse qui met deux jours à venir annule
tout le bénéfice du statut.

| Réponse reçue | Ce qu'on renvoie |
|---|---|
| **1** | On tape le nom de son commerce ensemble et on regarde ce que ça donne. C'est la porte du Catalogue à 50 000 F. |
| **2** | Les prix affichés ne font pas fuir, ce sont les prix cachés qui font fuir. Catalogue également. |
| **3** | La page qui répond la nuit : c'est la Vitrine, et l'escalier commence quand même par le Catalogue. |

⚠️ **On entre toujours par le Catalogue à 50 000 F**, jamais par la Vitrine
(`_documents/nebula-agency/vente/00-SOCLE-COMMERCIAL.md`). Un commerçant méfiant dit oui à
50 k, pas à 150 k.

## 4. Statut n° 2 · « N’ACHETEZ PAS DE SITE. »

**Le départ est impensable, et c'est tout le mécanisme :** c'est **une agence qui vend des
sites** qui vous dit de ne pas en acheter. Personne ne s'attend à ça. Le lecteur s'arrête
parce que la phrase n'a aucun sens venant de celui qui la signe, et il reste pour comprendre.

La ligne minuscule sous l'accroche est la clé de voûte : *« Écrit par une agence qui en
construit. »* Sans elle, le statut est un conseil banal. Avec elle, c'est un aveu, et un aveu
se lit jusqu'au bout.

**Ce que ça enseigne, et pourquoi c'est vrai :** un site ne fabrique pas de clients, il
retient ceux qui vous cherchaient déjà. Donc il y a deux cas, et le lecteur peut se situer
tout seul :

| Le cas | Ce qu'il lui faut vraiment |
|---|---|
| **Personne ne vous cherche encore** | pas une Vitrine : de quoi se faire chercher, donc le **Catalogue** |
| **On vous cherche et on ne vous trouve pas** | là, **chaque jour coûte**, et la Vitrine se justifie |

**C'est le statut qui alimente l'escalier au lieu de le court-circuiter.** En disant
honnêtement « ça ne vous servira à rien » au premier cas, on gagne le droit d'être cru par le
second. Et le premier cas atterrit exactement là où le socle commercial veut qu'il atterrisse.

⚠️ **La promesse engage vraiment.** Qui répond « MOI » doit recevoir un diagnostic franc, y
compris **« vous n'en avez pas besoin tout de suite »** quand c'est le cas. Un statut qui
fait ce numéro puis vend une Vitrine à tout le monde se retourne contre l'agence en une
semaine, à Cotonou où tout se sait.

**L'image :** on retire au lieu de tendre. Le sujet de la référence est **emporté vers le
fond**, en arrière, avec une traînée douce derrière lui. Toutes les publicités poussent
quelque chose vers vous ; celle-ci le reprend. C'est l'accroche, dite sans un mot.

### LE PROMPT

```
===========================================================
NEBULA AGENCY — WHATSAPP STATUS — ONE IMAGE, 9:16
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
Create ONE original WhatsApp STATUS image for NEBULA Agency, a digital
studio in Cotonou, Benin, serving West African merchants and business
owners.
It is seen on a phone, often outdoors in daylight, at half screen
brightness. It has ONE SECOND to earn a pause, and it must teach
something in the next five.
The whole post rests on ONE reversal: a company that builds websites is
telling the reader NOT to buy one. Everything must serve that reversal
and stay calm: the more sober the design, the more credible the
confession. Never a loud advertisement, never a promotional banner,
never a price tag.
It must look designed and expensive, never cheap, never homemade.

-----------------------------------------------------------
THE MATERIAL — THE STYLE REFERENCE IS THE SOURCE,
                NOT A VAGUE INSPIRATION
-----------------------------------------------------------
Build this image OUT OF the style reference. Do not invent a new
subject and do not add a decor of your own.
  KEEP    its main subject, re-staged as described below
  KEEP    its palette, its texture, its grain and its lighting
  KEEP    its typographic craft: the same kind of contrast between a
          huge line and small quiet lines
  CHANGE  its state, its framing for a 9:16 canvas, and every single
          word on it
  DROP    its original words, numbers, captions, logo and watermark:
          none of them may appear
If you find yourself inventing a new object, stop. The subject is
already in the style reference. Nothing else enters the frame.

CONTRAST: push the contrast harder than the style reference does.
This image is read outdoors, in daylight, on a dimmed screen. Any tone
that sits close to its neighbour will vanish. Text is either clearly
light on dark, or clearly dark on light. Never mid-grey on mid-grey.

-----------------------------------------------------------
THE STAGING — this is the whole idea of the image
-----------------------------------------------------------
IT IS BEING TAKEN AWAY, NOT OFFERED.
Every advertisement pushes something toward the viewer. This one pulls
it back.
Stage the subject of the style reference as if it were being WITHDRAWN:
moving away from the viewer, deeper into the frame, smaller and
receding, with a soft motion trail left behind it in the direction it
came from. It is retreating, calmly and deliberately, not falling and
not fleeing.
Leave the space it has just vacated visibly EMPTY in the foreground:
that emptiness is where the reader expected to be handed something.
Do not fill it.
No arrow, no icon, no diagram, no crossed-out symbol, no prohibition
sign, no red circle-and-bar, no phone, no screen, no hand.

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
The logo matters more than usual here: the reversal only works if the
reader sees WHO is saying it.

-----------------------------------------------------------
FORMAT AND SAFE ZONES — a hard requirement
-----------------------------------------------------------
Canvas: 1080 x 1920 px, vertical 9:16.
WhatsApp draws its own interface OVER this image:
  - the TOP 220 px are covered by the profile bar
  - the BOTTOM 340 px are covered by the reply field
Nothing that matters may sit in those two strips. All text, the logo
and the subject live inside the central band, between 220 px and
1580 px from the top. Compose as if those two strips did not exist.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
THE REVERSAL (at the very TOP of the safe band, so it is the first
              thing seen. Left-aligned, ENORMOUS all caps, condensed,
              tight tracking and tight leading, three stacked lines
              filling the width. By far the loudest element of the
              image, and the only large one):
  "N’ACHETEZ"
  "PAS DE"
  "SITE."

THE CONFESSION (immediately under it, TINY, quiet, in the accent
                colour of the style reference, on one line. It is the
                keystone of the whole post: it must be small, and it
                must be unmissable):
  "Écrit par une agence qui en construit."

THE LESSON (under the visual, small, quiet, three lines):
  "Un site ne fabrique pas de clients : il retient ceux qui vous cherchaient déjà."
  "Si personne ne vous cherche encore, il ne vous servira à rien."
  "Si on vous cherche et qu’on ne vous trouve pas, chaque jour vous coûte."

CALL TO ACTION (bottom of the safe band, on its own line, in the
                accent colour, smaller than the reversal):
  "Répondez « MOI » : je vous dis franchement dans quel cas vous êtes."
  Keep the French guillemets « » exactly as written, with their inner
  spaces.

FOOTER: the logo, per the LOGO INTEGRATION block, centred, placed just
ABOVE the 340 px bottom safe strip, never inside it, with
"nebula-agency.online" under it in tiny muted type.

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Inside the central safe band, top to bottom:
  1. THE REVERSAL, three stacked lines   <- first seen, loudest
  2. THE CONFESSION, one tiny line
  3. THE SUBJECT BEING WITHDRAWN         <- the largest zone
  4. THE LESSON, three quiet lines
  5. CALL TO ACTION
  6. LOGO, then the site address
The hierarchy must be brutal: ONE block is enormous, everything else
is small. The reversal must sit at the top: on a status, the top is
what the eye lands on first, and the shock has to be first.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above, plus "nebula-agency.online".
  Any extra word is a failure.
- Reproduce them VERBATIM: no translation, no rephrasing, no
  shortening, no added punctuation, no exclamation marks.
- Correct French typographic apostrophes ’ exactly as written:
  "N’ACHETEZ", "qu’on". Correct diacritics: "Écrit", "êtes",
  "cherchaient", "servira".
- The reversal must be readable at 20% of the image size.
- No hashtag, no social icon, no interface element, no emoji.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO price, NO amount, NO currency, NO "à partir de", NO discount
  badge, NO offer sticker. This post never quotes a price.
- NO invented statistics, percentages or figures of any kind.
- NO first name, no age, no portrait, no face, no human figure.
- NO recognisable third-party brand, app name or interface.
- NO prohibition sign, no red cross, no crossed-out object: the
  refusal is carried by the words and by the retreat, never by a
  warning symbol.
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
Oui, vous avez bien lu. Répondez MOI et je vous dis franchement dans quel cas
vous êtes, même si la réponse est « pas encore ».
```

### Ce qu'on répond à « MOI »

À préparer **avant** de publier. Deux questions suffisent à trancher :

1. *« Est-ce qu'on vous demande parfois votre lien, ou votre page ? »*
2. *« Quand quelqu'un vous découvre, qu'est-ce que vous lui envoyez aujourd'hui ? »*

| Ce qu'il répond | Le cas | Ce qu'on propose |
|---|---|---|
| « on ne me demande rien » | personne ne le cherche encore | de quoi se faire chercher : le **Catalogue** |
| « on me demande, et je n'ai rien » | on le cherche et on ne le trouve pas | la **Vitrine**, et on lui dit pourquoi |
| « j'envoie des photos WhatsApp » | il a la demande, pas la porte | **Catalogue** d'abord, Vitrine ensuite |

⚠️ Dans le doute, **on entre par le Catalogue à 50 000 F**
(`_documents/nebula-agency/vente/00-SOCLE-COMMERCIAL.md`). Et si la réponse honnête est
« pas encore », on la donne : c'est le prix du droit d'être cru la prochaine fois.

## 5. Statut n° 3 · « C’EST L’HEURE. » — cadeau pur

⚠️ **Celui-ci ne vend rien, et c'est volontaire.** Le statut n° 2 était un renversement
commercial. La règle de la série : **jamais deux statuts d'affilée qui font peur ou qui
vendent.** Celui-ci est un cadeau, sans contrepartie, et c'est lui qui achète le droit
d'être cru la prochaine fois.

**L'accroche insulte, puis complimente :** *« Ce n'est pas votre produit. C'est l'heure. »*
Le lecteur croit une seconde qu'on critique sa marchandise, et on lui retire le reproche
aussitôt. Ce mouvement-là retient plus sûrement qu'une menace, et il ne laisse aucune
amertume.

**Ce que ça enseigne, et c'est vrai partout :** à midi le soleil tombe à la verticale, les
couleurs s'écrasent et l'ombre devient un trou noir. La même chose photographiée avant 9 h
ou après 16 h devient belle. Aucun logiciel ne rattrape une mauvaise lumière, et **ça ne
coûte rien à essayer dès demain matin**.

**L'appel à l'action, le plus natif possible sur WhatsApp : envoyer une photo.** C'est un
geste, pas une rédaction. Personne n'écrit un message depuis un statut, tout le monde peut
appuyer sur « envoyer une photo ». Et une photo reçue ouvre une vraie conversation, sur son
produit à lui.

⚠️ **La promesse engage :** qui envoie une photo doit recevoir **une phrase utile et
honnête**, le jour même, sans que ça devienne un devis. Si la photo est bonne, on le dit et
on s'arrête là. C'est exactement ce qui fera qu'il reviendra le jour où il aura besoin d'un
site.

**L'image :** le même objet, coupé en deux par la lumière. À gauche, écrasé par un éclairage
vertical et dur, couleurs délavées, ombre noire sous lui. À droite, la même matière prise
dans une lumière basse et chaude, riche, avec du relief et une ombre longue et douce. Une
seule image, une seule idée, aucune flèche, aucun schéma : la démonstration est dans l'objet.

### LE PROMPT

```
===========================================================
NEBULA AGENCY — WHATSAPP STATUS — ONE IMAGE, 9:16
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
Create ONE original WhatsApp STATUS image for NEBULA Agency, a digital
studio in Cotonou, Benin, serving West African merchants and business
owners.
It is seen on a phone, often outdoors in daylight, at half screen
brightness. It has ONE SECOND to earn a pause, and it must teach
something useful in the next five.
This post SELLS NOTHING. It is a gift: a craft tip the reader can use
tomorrow morning for free. Keep it generous and calm. Never an
advertisement, never a promotional banner, never a price tag.
It must look designed and expensive, never cheap, never homemade.

-----------------------------------------------------------
THE MATERIAL — THE STYLE REFERENCE IS THE SOURCE,
                NOT A VAGUE INSPIRATION
-----------------------------------------------------------
Build this image OUT OF the style reference. Do not invent a new
subject and do not add a decor of your own.
  KEEP    its main subject, re-staged as described below
  KEEP    its palette, its texture, its grain
  KEEP    its typographic craft: the same kind of contrast between a
          huge line and small quiet lines
  CHANGE  its LIGHTING, which is the whole point of this image, its
          framing for a 9:16 canvas, and every single word on it
  DROP    its original words, numbers, captions, logo and watermark:
          none of them may appear
If you find yourself inventing a new object, stop. The subject is
already in the style reference. Nothing else enters the frame.

CONTRAST: push the contrast harder than the style reference does.
This image is read outdoors, in daylight, on a dimmed screen. Any tone
that sits close to its neighbour will vanish. Text is either clearly
light on dark, or clearly dark on light. Never mid-grey on mid-grey.

-----------------------------------------------------------
THE STAGING — this is the whole idea of the image
-----------------------------------------------------------
ONE OBJECT, CUT IN TWO BY THE LIGHT.
Show the subject of the style reference ONCE, whole and centred, and
light its two halves completely differently along a clean vertical
split down its middle.
  - LEFT HALF: lit from directly overhead by a hard midday light.
    Colours washed out and flat, no depth, blown highlights, and a
    small dense BLACK shadow pooled straight underneath it. It looks
    cheap, and it should.
  - RIGHT HALF: lit by a low, warm, side light. Saturated colour,
    visible texture and relief, a long soft shadow stretching to the
    side, a gentle gradient on the surface. It looks expensive, and
    it is the SAME object.
The split must be unmistakable at a glance, and the two halves must
belong to one single object: this is not two objects side by side, and
it is not a before-and-after panel.
No dividing line drawn on top, no arrow, no icon, no diagram, no
clock, no sun symbol, no label, no caption pointing at either half.

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
WhatsApp draws its own interface OVER this image:
  - the TOP 220 px are covered by the profile bar
  - the BOTTOM 340 px are covered by the reply field
Nothing that matters may sit in those two strips. All text, the logo
and the subject live inside the central band, between 220 px and
1580 px from the top. Compose as if those two strips did not exist.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
THE HOOK (at the TOP of the safe band, so it is the first thing seen.
          Left-aligned, ENORMOUS all caps, condensed, tight tracking
          and tight leading, three stacked lines filling the width. By
          far the loudest element, and the only large one. The FIRST
          TWO lines in the ink colour of the style reference, THE
          THIRD in its accent colour):
  "CE N’EST PAS"
  "VOTRE PRODUIT."
  "C’EST L’HEURE."

THE LESSON (under the visual, small, quiet, three lines):
  "À midi, le soleil tombe droit : les couleurs s’écrasent et l’ombre devient un trou noir."
  "Avant 9 h ou après 16 h, la même chose devient belle."
  "À l’ombre, sur un fond uni, sans flash."

CALL TO ACTION (bottom of the safe band, on its own line, in the
                accent colour, smaller than the hook):
  "Envoyez-moi une photo de votre produit. Je vous dis en une phrase ce qui la retient."

FOOTER: the logo, per the LOGO INTEGRATION block, centred, placed just
ABOVE the 340 px bottom safe strip, never inside it, with
"nebula-agency.online" under it in tiny muted type.

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Inside the central safe band, top to bottom:
  1. THE HOOK, three stacked lines   <- first seen, loudest
  2. THE OBJECT CUT IN TWO BY LIGHT  <- the largest zone
  3. THE LESSON, three quiet lines
  4. CALL TO ACTION
  5. LOGO, then the site address
The hierarchy must be brutal: ONE block is enormous, everything else
is small. Give the object room: the demonstration needs to be seen
before the lesson is read.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above, plus "nebula-agency.online".
  Any extra word is a failure.
- Reproduce them VERBATIM: no translation, no rephrasing, no
  shortening, no added punctuation, no exclamation marks.
- Correct French typographic apostrophes ’ exactly as written:
  "N’EST", "C’EST", "L’HEURE", "s’écrasent", "l’ombre", "l’ombre".
- Correct diacritics: "À midi", "après", "écrasent".
- "9 h" and "16 h" keep their space before the h.
- The hook must be readable at 20% of the image size.
- No hashtag, no social icon, no interface element, no emoji.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO price, NO amount, NO currency, NO offer sticker. This post sells
  nothing at all.
- NO invented statistics or percentages. The only numerals allowed
  are the two hours, "9 h" and "16 h".
- NO first name, no age, no portrait, no face, no human figure.
- NO recognisable third-party brand, app name or interface.
- NO clock, NO sun icon, NO before-and-after label, NO split-screen
  divider drawn on top: the light does the explaining alone.
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
Essayez demain matin avec le même produit et le même téléphone. Vous verrez la
différence tout de suite. Envoyez-moi la photo, je vous dis ce qui la retient.
```

### Ce qu'on répond à une photo reçue

**Une phrase, honnête, le jour même.** Trois choses à regarder, dans cet ordre :

| Ce qu'on voit | La phrase qu'on renvoie |
|---|---|
| ombre dure et noire sous l'objet | « C'est la lumière du haut. Refaites-la à l'ombre demain matin, vous ne reconnaîtrez pas le produit. » |
| fond chargé, du désordre derrière | « Le produit est bon, c'est le fond qui le mange. Un mur uni suffit. » |
| photo sombre, prise à l'intérieur | « Sortez-la près de la porte, sans flash. La lumière du jour fait tout le travail. » |
| la photo est bonne | « Celle-là est bonne, ne la retouchez pas. » **et on s'arrête là** |

⚠️ **On ne glisse aucune offre dans cette réponse.** Ni site, ni catalogue, ni « au fait ».
C'est un cadeau ou ce n'est rien. La vente viendra d'elle-même, plus tard, parce qu'on aura
été utile sans rien demander.

## 6. Statut n° 4 · « LE PREMIER SITE DU MONDE EST TOUJOURS EN LIGNE. »

**Celui-ci porte le label « LE SAVIEZ-VOUS ? »**, contrairement aux statuts n° 2 et n° 3.
C'est la rubrique éditoriale dans sa forme la plus pure : **une leçon, rien d'autre**. Aucune
douleur, aucun retournement commercial, aucune demande. On se couche moins bête, c'est tout.

**Le fait, et il est rare :** le tout premier site web du monde a été publié en 1991, et il
répond encore aujourd'hui, à la même adresse, `info.cern.ch`. Presque personne ne le sait, et
tout le monde peut le vérifier en dix secondes.

**Pourquoi ce fait-là et pas un autre :** parce qu'il enseigne quelque chose de rare sur la
présence en ligne, et qui va contre l'intuition. On croit qu'internet est ce qui change le
plus vite. En réalité, **ce sont les plateformes qui passent, pas les adresses.** Des milliers
d'applications à la mode sont nées et ont disparu pendant que cette page-là n'a pas bougé.

⚠️ **Il est vérifiable, et c'est ce qui autorise à le publier.** La règle « aucune
statistique inventée » interdit les pourcentages sortis de nulle part ; elle n'interdit pas
un fait historique documenté que le lecteur peut aller contrôler lui-même. **Le statut donne
d'ailleurs l'adresse pour ça** : c'est le contraire d'un chiffre qu'on demande de croire.

**Aucun appel à l'action commercial.** Le seul geste proposé est d'aller voir la page. Ce que
le lecteur en tire pour son propre commerce, il le tire tout seul, et il le tirera mieux que
si on le lui avait dit.

**L'image :** la pose longue. Le sujet de la référence est **parfaitement net et immobile**,
et tout l'espace autour de lui est une traînée de lumière floue, celle de tout ce qui est
passé pendant que la photo se faisait. En pose longue, **seul ce qui ne bouge pas reste net** :
la leçon est déjà dans le phénomène, il n'y a rien à expliquer.

### LE PROMPT

```
===========================================================
NEBULA AGENCY — WHATSAPP STATUS — ONE IMAGE, 9:16
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
Create ONE original WhatsApp STATUS image for NEBULA Agency, a digital
studio in Cotonou, Benin, serving West African merchants and business
owners.
It is seen on a phone, often outdoors in daylight, at half screen
brightness. It has ONE SECOND to earn a pause.
This post TEACHES ONE RARE FACT and sells absolutely nothing. There is
no offer, no pain, no persuasion: the reader simply goes to bed knowing
something they did not know this morning. Keep it calm, generous and
quietly astonishing.
It must look designed and expensive, never cheap, never homemade.

-----------------------------------------------------------
THE MATERIAL — THE STYLE REFERENCE IS THE SOURCE,
                NOT A VAGUE INSPIRATION
-----------------------------------------------------------
Build this image OUT OF the style reference. Do not invent a new
subject and do not add a decor of your own.
  KEEP    its main subject, re-staged as described below
  KEEP    its palette, its texture, its grain
  KEEP    its typographic craft: the same kind of contrast between a
          huge line and small quiet lines
  CHANGE  its framing for a 9:16 canvas, the way it is photographed,
          and every single word on it
  DROP    its original words, numbers, captions, logo and watermark:
          none of them may appear
If you find yourself inventing a new object, stop. The subject is
already in the style reference. Nothing else enters the frame.

CONTRAST: push the contrast harder than the style reference does.
This image is read outdoors, in daylight, on a dimmed screen. Any tone
that sits close to its neighbour will vanish. Text is either clearly
light on dark, or clearly dark on light. Never mid-grey on mid-grey.

-----------------------------------------------------------
THE STAGING — this is the whole idea of the image
-----------------------------------------------------------
A LONG EXPOSURE. ONLY WHAT DOES NOT MOVE STAYS SHARP.
Photograph the subject of the style reference as if with a very long
shutter speed:
  - THE SUBJECT ITSELF is perfectly SHARP, still, solid, every detail
    crisp. It did not move for the entire exposure.
  - EVERYTHING AROUND IT is pure motion blur: long smooth streaks of
    light sweeping past and through the frame, layered, translucent,
    going in one general direction. Nothing in the blur is
    identifiable: no shapes, no objects, no figures, no letters. Only
    movement that has already gone by.
The contrast between the one sharp thing and the blurred world around
it is the entire message, and it must be unmistakable at a glance.
This is a photographic phenomenon, not a graphic effect: no radial
zoom filter, no speed lines drawn on top, no arrow, no icon, no
diagram, no clock, no calendar, no hourglass, no label.

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
  - reserve a CALM area for it: place it over a quiet part of the
    blur, never over the sharp subject, so it reads with no plate.
  - size it so its wordmark stays comfortably readable when the whole
    image is viewed at 20% of its size.
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
1580 px from the top. Compose as if those two strips did not exist.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (top of the safe band, small, uppercase, widely letter-spaced,
       muted): "LE SAVIEZ-VOUS ?"

THE FACT (under the label, left-aligned, ENORMOUS all caps, condensed,
          tight tracking and tight leading, three stacked lines
          filling the width. By far the loudest element of the image,
          and the only large one. The first two lines in the ink
          colour of the style reference, THE THIRD in its accent
          colour):
  "LE PREMIER SITE"
  "DU MONDE EST"
  "TOUJOURS EN LIGNE."

THE LESSON (under the visual, small, quiet, three lines):
  "Publié en 1991. Jamais déplacé, jamais renommé."
  "Depuis, des milliers d’applications à la mode sont nées, puis ont disparu."
  "Ce qui dure en ligne, ce n’est pas la plateforme. C’est l’adresse."

THE PROOF (under the lesson, small, in the accent colour, on one line.
           It is a web address the reader can visit, written as plain
           type. It is NOT a brand logo and it is NOT an interface):
  "Allez le voir ce soir : info.cern.ch"

THE APHORISM (bottom of the safe band, medium size, in the accent
              colour, set apart with real breathing space above it):
  "Une adresse se garde. Une mode, non."

FOOTER: the logo, per the LOGO INTEGRATION block, centred, placed just
ABOVE the 340 px bottom safe strip, never inside it, with
"nebula-agency.online" under it in tiny muted type.

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Inside the central safe band, top to bottom:
  1. LABEL
  2. THE FACT, three stacked lines   <- the loudest zone
  3. THE SHARP SUBJECT IN ITS BLUR   <- the largest zone
  4. THE LESSON, three quiet lines
  5. THE PROOF
  6. THE APHORISM
  7. LOGO, then the site address
The hierarchy must be brutal: ONE block is enormous, everything else
is small. The sharp subject needs room to be seen as sharp: give the
blur space to run past it.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above, plus "nebula-agency.online".
  Any extra word is a failure.
- Reproduce them VERBATIM: no translation, no rephrasing, no
  shortening, no added punctuation, no exclamation marks.
- Correct French typographic apostrophes ’ exactly as written:
  "n’est", "C’est", "l’adresse", "d’applications".
- Correct diacritics: "Publié", "déplacé", "renommé", "nées".
- "info.cern.ch" and "nebula-agency.online" must be rendered exactly,
  in lowercase, with their dots, and must stay legible.
- "1991" is the only other numeral allowed in the image.
- The fact must be readable at 20% of the image size.
- No hashtag, no social icon, no interface element, no emoji.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO price, NO amount, NO currency, NO offer, NO call to action of
  any commercial kind. This post sells nothing at all.
- NO invented statistics or percentages. The only figures are the
  year 1991 and the two web addresses.
- NO first name, no age, no portrait, no face, no human figure.
- NO third-party logo, app icon, browser window or interface anywhere
  in the imagery: "info.cern.ch" appears as plain type only.
- NO clock, NO calendar, NO hourglass, NO speed lines drawn on top:
  the long exposure does the explaining alone.
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
Ouvrez info.cern.ch ce soir. C’est la toute première page du web, publiée en 1991,
et elle répond encore. Trente-cinq ans, sans changer d’adresse.
```

### Si quelqu’un répond

Il répondra, parce qu’un fait rare donne envie de réagir. **On ne vend rien à ce
moment-là.** On raconte : que la page a été écrite au CERN, qu’elle n’a jamais bougé,
qu’elle est plus vieille que la plupart des applications qu’on a sur son téléphone.

C’est tout. Le lecteur fera lui-même le rapprochement avec son propre commerce, et il le
fera mieux que si on le lui avait dit.

### Pourquoi ce statut compte, même s’il ne vend rien

Il fait deux choses qu’aucun post commercial ne peut faire :

1. **Il donne une raison de garder le contact.** On suit quelqu’un qui apprend des choses,
   pas quelqu’un qui propose des choses.
2. **Il rend crédible la vente d’après.** Une série qui donne vraiment gagne le droit d’être
   crue quand elle parle d’elle-même.

## 7. Statut n° 5 · « LE DERNIER MESSAGE N’EST PAS DE VOUS. »

**La mécanique est nouvelle : ce statut ne fait pas lire, il fait FAIRE.** Et il fait faire
**dans l’application où il est publié**. Le lecteur n’a rien à croire sur parole : il ouvre
une conversation, il regarde, et la preuve est dans son propre téléphone.

C’est la quatrième mécanique de la série, après le déplacement de la menace (n° 1), le
renversement de l’émetteur (n° 2), la disculpation du lecteur (n° 3) et le fait rare
vérifiable (n° 4). **Ici, on parie sur son téléphone, et on gagne presque à tous les coups.**

**Le pari, et pourquoi il tient :** dans un commerce qui tourne sur WhatsApp, il y a toujours
des conversations où le dernier message est celui du client. Une question sans réponse, un
« bonjour » du soir, un « c’est disponible ? » noyé. Ce ne sont pas des clients perdus : ce
sont des **ventes en attente**, à portée de pouce, depuis des jours.

**Le multiplicateur, c’est ce qui fait mal :** on ne demande pas d’en regarder une, on
demande d’en **remonter dix et de compter**. Une conversation oubliée, c’est une distraction.
Sept, c’est un problème d’organisation, et le lecteur le découvre tout seul.

**L’appel à l’action est un nombre**, donc un seul caractère à taper. Et ce nombre **qualifie
la conversation d’avance** : celui qui répond « 7 » a sept ventes en attente et il le sait
depuis dix secondes.

⚠️ **La promesse engage, et elle est précise :** qui répond un nombre reçoit **le message de
relance à copier**, gratuitement, le jour même. Pas un devis, pas une offre. Le texte type
est plus bas dans ce document : le préparer avant de publier.

**L’image :** ce qui attend est **juste derrière vous**, et vous ne vous êtes pas retourné.
Un petit point de lumière suspendu à hauteur d’épaule du sujet, immobile depuis longtemps, et
le sujet tourné dans l’autre sens. La distance est minuscule : c’est à portée de main.

### LE PROMPT

```
===========================================================
NEBULA AGENCY — WHATSAPP STATUS — ONE IMAGE, 9:16
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
Create ONE original WhatsApp STATUS image for NEBULA Agency, a digital
studio in Cotonou, Benin, serving West African merchants and business
owners.
It is seen on a phone, often outdoors in daylight, at half screen
brightness. It has ONE SECOND to earn a pause.
This post asks the reader to DO something immediately, inside the very
app they are reading it in, and the proof appears in their own phone.
Calm, precise, certain of itself. Never a loud advertisement, never a
promotional banner, never a price tag.
It must look designed and expensive, never cheap, never homemade.

-----------------------------------------------------------
THE MATERIAL — THE STYLE REFERENCE IS THE SOURCE,
                NOT A VAGUE INSPIRATION
-----------------------------------------------------------
Build this image OUT OF the style reference. Do not invent a new
subject and do not add a decor of your own.
  KEEP    its main subject, re-staged as described below
  KEEP    its palette, its texture, its grain and its lighting
  KEEP    its typographic craft: the same kind of contrast between a
          huge line and small quiet lines
  CHANGE  its orientation, its framing for a 9:16 canvas, and every
          single word on it
  DROP    its original words, numbers, captions, logo and watermark:
          none of them may appear
If you find yourself inventing a new object, stop. The subject is
already in the style reference. Nothing else enters the frame.

CONTRAST: push the contrast harder than the style reference does.
This image is read outdoors, in daylight, on a dimmed screen. Any tone
that sits close to its neighbour will vanish. Text is either clearly
light on dark, or clearly dark on light. Never mid-grey on mid-grey.

-----------------------------------------------------------
THE STAGING — this is the whole idea of the image
-----------------------------------------------------------
IT IS WAITING RIGHT BEHIND YOU.
The subject of the style reference is turned AWAY, facing one side of
the frame, calm and unaware.
Just behind it, at shoulder height and very close, hangs a single
small steady point of light. Around that point, a faint halo shows it
has been there a long while without moving: it has waited.
The whole tension is the distance, and the distance is tiny: the point
is within arm's reach, and the subject simply has not turned round.
Everything else in the frame is quiet and unoccupied. Do not add a
second point, do not add a crowd, do not fill the space.
No arrow, no icon, no diagram, no phone, no screen, no message bubble,
no notification badge, no hand, no label.

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
WhatsApp draws its own interface OVER this image:
  - the TOP 220 px are covered by the profile bar
  - the BOTTOM 340 px are covered by the reply field
Nothing that matters may sit in those two strips. All text, the logo
and the subject live inside the central band, between 220 px and
1580 px from the top. Compose as if those two strips did not exist.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (top of the safe band, small, uppercase, widely letter-spaced,
       muted): "LE SAVIEZ-VOUS ?"

THE CLAIM (under the label, left-aligned, ENORMOUS all caps,
           condensed, tight tracking and tight leading, three stacked
           lines filling the width. By far the loudest element of the
           image, and the only large one. The first two lines in the
           ink colour of the style reference, THE THIRD in its accent
           colour):
  "LE DERNIER"
  "MESSAGE N’EST"
  "PAS DE VOUS."

THE INSTRUCTION (immediately under it, small, quiet, one line):
  "Ouvrez votre conversation client la plus récente. Regardez qui a écrit en dernier."

THE LESSON (under the visual, small, quiet, two lines):
  "Le dernier message dit qui attend."
  "Si ce n’est pas vous, c’est vous qu’on attend."

THE MULTIPLIER (under it, small, quiet, one line):
  "Remontez-en dix et comptez. Ce sont des ventes en attente dans votre poche."

CALL TO ACTION (bottom of the safe band, on its own line, in the
                accent colour, smaller than the claim):
  "Répondez-moi ce nombre. Je vous envoie quoi écrire pour les rouvrir."

FOOTER: the logo, per the LOGO INTEGRATION block, centred, placed just
ABOVE the 340 px bottom safe strip, never inside it, with
"nebula-agency.online" under it in tiny muted type.

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Inside the central safe band, top to bottom:
  1. LABEL
  2. THE CLAIM, three stacked lines   <- the loudest zone
  3. THE INSTRUCTION
  4. THE SUBJECT AND THE WAITING LIGHT  <- the largest zone
  5. THE LESSON, two quiet lines
  6. THE MULTIPLIER
  7. CALL TO ACTION
  8. LOGO, then the site address
The hierarchy must be brutal: ONE block is enormous, everything else
is small. Leave real quiet space around the waiting point of light:
its isolation is what makes it read as waiting.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above, plus "nebula-agency.online".
  Any extra word is a failure.
- Reproduce them VERBATIM: no translation, no rephrasing, no
  shortening, no added punctuation, no exclamation marks.
- Correct French typographic apostrophes ’ exactly as written:
  "N’EST", "n’est", "c’est", "qu’on".
- Correct diacritics: "récente", "dernier", "Répondez".
- "dix" is written in letters, never in figures.
- The claim must be readable at 20% of the image size.
- No hashtag, no social icon, no interface element, no emoji.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO price, NO amount, NO currency, NO offer, NO commercial call to
  action. This post asks for a number, nothing else.
- NO invented statistics or percentages. There is no figure anywhere
  in this image.
- NO first name, no age, no portrait, no face, no human figure.
- NO recognisable third-party brand, app name or interface. In
  particular: no chat bubble, no unread badge, no green tick.
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
Faites-le maintenant, ça prend dix secondes. Répondez-moi juste le nombre que vous
avez trouvé, je vous envoie le message de relance à copier.
```

### Le message de relance à envoyer en retour

**À préparer avant de publier.** Qui répond un nombre reçoit ceci, tel quel, gratuitement.

```
Voilà ce que vous pouvez leur écrire, en copiant, une conversation à la fois :

« Bonjour, je reprends votre message. Toutes mes excuses pour le délai.
Est-ce que vous cherchez toujours [ce dont il parlait] ? Je vous réponds
tout de suite. »

Trois choses la rendent efficace :
· on ne se justifie pas, on s'excuse en une ligne et on avance ;
· on rappelle ce qu'il voulait, il n'a pas à remonter la conversation ;
· on finit par une question fermée, à laquelle on répond par oui ou non.

Commencez par les trois plus récentes. Les plus vieilles répondent moins.
```

⚠️ **On ne glisse aucune offre dans cette réponse.** Ni site, ni catalogue. Celui qui
compte sept conversations en attente vient de comprendre tout seul qu'il lui manque quelque
chose : on ne le lui dit pas, il y reviendra.

### Où ça mène, sans être dit

Le lecteur qui découvre sept ventes en attente dans son téléphone tire lui-même la
conclusion : **il lui faut quelque chose qui réponde quand lui ne peut pas.** C’est
exactement ce que fait un catalogue avec ses prix affichés et sa page qui travaille la nuit.
**Ne pas le formuler dans le statut.** Une conclusion qu’on tire soi-même tient mille fois
mieux qu’une conclusion qu’on nous vend.

---

## 8. Statut n° 6 · « LA VOIE VIDE » · direction « NUIT ÉLECTRIQUE »

**Le thème demandé :** sortir de la masse et passer devant tout le monde.

**Le piège du thème.** Tout le monde traite « sortir de la masse » de la même façon :
faites-vous remarquer, criez plus fort, publiez plus. Or **crier plus fort, c’est
exactement ce que fait la masse.** C’est même sa définition. Un statut qui dit ça ne sort
de rien du tout : il rejoint le tas.

**Le retournement.** On ne passe pas devant en poussant dans la file. **On passe devant en
prenant la voie où personne n’est.** Et cette voie existe pour de bon : au Bénin, dans la
plupart des métiers, la concurrence n’est **pas encore** en ligne. Ce n’est pas un argument
de vente, c’est un fait que le lecteur peut vérifier en cherchant trois de ses concurrents
ce soir.

### L’image

Un boulevard de Cotonou, la nuit, vu d’un pont. **D’un côté la file : pare-chocs contre
pare-chocs jusqu’à l’horizon, des dizaines de feux arrière, immobile.** De l’autre côté de
la ligne blanche, **une voie totalement vide**, l’asphalte encore humide, éclairée d’un
bleu froid, qui file droit vers le point de fuite.

**Et le détail qui fait tout le post :** la voie vide **n’est pas vide.** Tout au fond,
minuscule, un seul phare. **Quelqu’un est déjà passé.**

C’est ce point lumineux qui transforme une jolie métaphore en urgence. Sans lui, le post
dit « il y a de la place ». Avec lui, il dit **« il y a de la place, et elle se prend en
ce moment. »** L’envie fait travailler un statut bien mieux que la peur, et elle ne coûte
rien à la confiance.

### Les mots

> **Tout le monde attend** · **Doublez**
>
> *La file, c’est le marché. La voie vide, c’est internet.*
> *Elle est encore vide. Quelqu’un est déjà devant.*

Deux temps, comme la référence : une petite ligne posée sur une barre bleue pleine, puis
**un seul mot énorme dans un cadre en pointillés.** « Doublez » se lit à 20 %, se comprend
sans l’image, et c’est un ordre : sur un statut, un verbe à l’impératif vaut dix phrases.

### Pourquoi il vient aujourd’hui, et pas hier

Hier, « L’HEURE DORÉE » vendait. **La règle du document interdit d’enchaîner.** Celui-ci ne
vend rien : il donne une lecture stratégique, et il demande **un mot**, pas un achat. C’est
lui qui rachète le droit d’être cru la prochaine fois.

### LE PROMPT

```
===========================================================
NEBULA AGENCY — WHATSAPP STATUS — ONE IMAGE, 9:16
"LA VOIE VIDE" — electric night direction
===========================================================

ATTACHED INPUTS — TWO attachments.
Identify them BY THEIR CONTENT, not by their order. Never swap
their roles: swapping them ruins the image.

  THE STYLE REFERENCE = the attachment showing a very dark navy
     poster with a blue-tinted close-up of a hand moving a chess
     piece on a board, a small white headline sitting on a solid
     blue bar that bleeds off the left edge, a much larger white
     headline inside a DASHED blue rectangle, a logo at the top
     centre and a website address at the bottom centre.
     Take from it, and only from it:
       - the DEEP NAVY / NEAR-BLACK ground and the single cold BLUE
         light source coming from the upper left
       - the BLUE DUOTONE photographic treatment: desaturated,
         high contrast, cinematic, almost monochrome
       - the ROUNDED GEOMETRIC HEAVY SANS-SERIF lettering
       - THE TWO-PART HEADLINE DEVICE: a small line on a SOLID
         electric-blue bar bleeding off the LEFT EDGE, and under it
         a much larger line inside a DASHED electric-blue rectangle
       - the logo centred at the top, the address centred at the
         very bottom
       - its level of finish
     Take NOTHING of its subject, its words or its brand. There is
     NO chess, NO chessboard, NO chess piece, NO hand and NO
     tabletop anywhere in the new image, and the words "The Zubix"
     appear nowhere.

  THE LOGO = the attachment showing the NEBULA Agency logo: a purple
     and blue cosmic swirl above the wordmark "NEBULA", with
     "AGENCY" underneath, on a transparent background.
     It is an ASSET TO PLACE, exactly as provided. It is never a
     style reference and never a subject to reinterpret.

  If you hesitate: the attachment with a transparent background and
  a readable "NEBULA AGENCY" wordmark is THE LOGO. The other one is
  THE STYLE REFERENCE.

-----------------------------------------------------------
TASK
-----------------------------------------------------------
Create ONE original WhatsApp status image for NEBULA Agency, a
digital studio in Cotonou, Benin, that builds pages and online
catalogues for West African merchants.
The idea: everyone is queuing in the same lane; the lane beside it
is open, and someone is already far down it.
Cinematic, cold, premium, night. Never cheap, never clip-art.

-----------------------------------------------------------
THE SCENE — full bleed, it fills the whole canvas
-----------------------------------------------------------
A wide city boulevard in Cotonou, Benin, at NIGHT, seen from a
FOOTBRIDGE ABOVE IT, looking straight down the road toward a distant
vanishing point.

RIGHT SIDE — THE QUEUE: a dense, unbroken traffic jam. Cars and
moto-taxis packed bumper to bumper, crowded, identical, stretching
all the way to the horizon, completely motionless. Rendered DIM: the
mass is dark, cluttered and slightly out of focus.

LEFT SIDE — THE OPEN LANE: separated only by a painted white line,
ONE COMPLETELY EMPTY LANE. Wet asphalt reflecting a cold blue light,
crisp painted markings, running clean and straight to the vanishing
point. It is the ONLY brightly lit thing in the picture. Nothing on
it, no vehicle, no obstacle, no person.

FAR AWAY, at the very end of the empty lane, almost at the vanishing
point, TINY: a single motorcycle silhouette with its headlight on,
already far ahead. It must be small enough that the eye finds it
second, after the empty lane, and it must be unmistakable.

SKY: the upper third is a near-black navy sky with one soft cold
blue glow spilling from the upper left, exactly like the light in
the reference. Keep it clean and uncluttered: the logo and the
headline sit on it.

FOREGROUND: the bottom of the frame is dark, empty asphalt. Keep it
plain: the small lines of text sit there.

-----------------------------------------------------------
THE COLOUR
-----------------------------------------------------------
Blue duotone throughout, exactly as in the reference: deep navy,
steel blue, cold white highlights, near-black shadows.
ONE controlled exception: the tail lights of the jam stay red, but
DIM and desaturated, small points only. They are the only red in the
image and they must never compete with the blue lane.
No orange street lamps, no warm tones anywhere else.

-----------------------------------------------------------
LOGO INTEGRATION — read twice, most attempts fail here
-----------------------------------------------------------
The logo attachment is a PNG with a TRANSPARENT background. Place
it at the TOP of the image, centred, on the dark sky, small, exactly
as provided, and KEEP that transparency.
  - it sits DIRECTLY on the sky. NO white box, NO black box, NO
    coloured plate, NO rounded card, NO badge, NO outline, NO glow,
    NO drop shadow behind it.
  - do NOT redraw it, restyle it, recolour it, stretch it, crop it,
    rotate it, or add a wordmark or tagline of your own.
  - size it so its wordmark stays comfortably readable when the
    whole image is viewed at 20% of its size.
A logo pasted on a plate is a failed image.

-----------------------------------------------------------
FORMAT AND SAFE ZONES — a status is covered by the interface
-----------------------------------------------------------
Canvas: 1080 x 1920 px, vertical 9:16.
WhatsApp draws its own interface ON TOP of the image:
  - the TOP 220 px are covered (profile picture, name, time)
  - the BOTTOM 340 px are covered (the "Reply" field)
The logo, every line of type and the small motorcycle must ALL sit
between y = 220 px and y = 1580 px. Nothing that matters may fall
inside those two strips.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
HEADLINE, part 1 — small white bold capitals-and-lowercase text on a
SOLID ELECTRIC-BLUE BAR that starts off the LEFT EDGE of the canvas
and stops after the words, exactly the device used in the reference:
    "Tout le monde attend"

HEADLINE, part 2 — directly under it, MUCH larger, white, the
loudest element of the whole image, inside a DASHED ELECTRIC-BLUE
RECTANGLE OUTLINE, exactly the device used in the reference:
    "Doublez"

THE READING, lower area, over the dark asphalt, two lines, centred,
medium size, white:
    "La file, c’est le marché."
    "La voie vide, c’est internet."

THE STING, one line under it, smaller, in electric blue:
    "Elle est encore vide. Quelqu’un est déjà devant."

THE ANSWER TO GIVE, one line under it, small, white, semi-bold:
    "Répondez VOIE à ce statut."

FOOTER, at the very bottom of the safe area, tiny, centred, white at
reduced opacity:
    "nebula-agency.online"

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Top to bottom, all inside the safe band:
  1. NEBULA logo, centred on the dark sky
  2. blue bar + "Tout le monde attend"        (bleeds off the left)
  3. dashed rectangle + "Doublez"             <- loudest zone
  4. THE ROAD: the jam on the right, the lit empty lane on the left,
     the tiny motorcycle far away              <- largest zone
  5. "La file, c’est le marché." / "La voie vide, c’est internet."
  6. THE STING
  7. "Répondez VOIE à ce statut."
  8. nebula-agency.online
Lines 5 to 8 form ONE tight block over the dark foreground asphalt,
with generous space between that block and the headline above.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM: no translation, no rephrasing, no
  shortening, no added punctuation, no exclamation marks.
- Correct French typographic apostrophes ’ exactly as written:
  "c’est" (twice), "Quelqu’un".
- Correct diacritics: "marché", "déjà".
- The word "VOIE" stays in capitals, exactly as written. Do not turn
  it into a button, a pill or a badge: it is plain text.
- "Doublez" must still be readable when the image is viewed at 20%
  of its size, and it must be the first thing the eye reads.
- No hashtag, no emoji, no icon, no arrow, no star, no rating, no
  road sign, no speed limit disc, no number plate, no readable text
  on any vehicle.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO chess, NO chessboard, NO chess piece, NO hand, NO tabletop.
  The reference gives the style and NOTHING of its subject.
- NO price, NO amount, NO currency symbol, NO offer, NO discount,
  NO percentage.
- NO invented statistics, follower counts, client counts, ratings or
  stars. No figures anywhere in the image.
- NO visible human face and no readable person: the only human
  presence is the distant motorcycle silhouette.
- NO recognisable third-party brand, logo, car badge or app, and the
  words "The Zubix" must not appear.
- NO watermark, no frame, no border around the image itself.
- The empty lane stays EMPTY apart from the one distant motorcycle.
  Filling it destroys the entire idea.
- One idea, told once.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1920 image, publication-ready, cinematic
quality, high-fidelity text rendering.
===========================================================
```

### Pour le fil Instagram et Facebook (4:5)

Même prompt, en remplaçant le bloc FORMAT. **La ligne « Répondez VOIE à ce statut. »
disparaît** : sur un fil, on ne répond pas à un statut, on écrit en commentaire ou en
message. Elle est reprise dans la légende.

```
-----------------------------------------------------------
FORMAT
-----------------------------------------------------------
Canvas: 1080 x 1350 px, vertical 4:5, for an Instagram and Facebook
feed. No safe zones: the whole canvas is visible.
Bring the horizon slightly higher so the road still runs deep into
the frame, and keep the same top-to-bottom order.

REMOVE ONE LINE: do not render "Répondez VOIE à ce statut." on this
version. Everything else is unchanged.
```

### Le texte à écrire sous le statut

```
La file, ce n’est pas la circulation. C’est le marché.

Tout le monde y est. Tout le monde attend le même client, au même
endroit, au même moment. Et personne ne regarde la voie d’à côté.

Cherchez trois de vos concurrents ce soir. Tapez leur nom. Regardez
combien vous en trouvez vraiment.

C’est ça, la voie vide. Elle ne restera pas vide.

Répondez VOIE, je vous dis par où on entre.
```

**Pourquoi cette légende marche :** elle ne demande pas de croire, **elle demande de
vérifier**, et la vérification se fait en trente secondes, dans le téléphone qui tient déjà
le statut. Celui qui cherche ses trois concurrents et n’en trouve aucun vient de se
convaincre tout seul.

### Ce qu’on répond à « VOIE »

⚠️ **La réponse ne vend pas de vitrine.** Le socle est formel : on entre par le Catalogue.
La voie vide, dans la conversation, c’est **une adresse où tout ce qu’on vend est rangé**,
pas un site à 150 000 F.

```
Bonjour, merci d’avoir répondu.

Une question avant tout : aujourd’hui, quand quelqu’un veut savoir ce que
vous vendez et à quel prix, vous faites comment ? Vous renvoyez les photos
une par une sur WhatsApp ?

Si c’est ça, la voie vide commence exactement là. On range tout ce que vous
vendez à une seule adresse, que vous envoyez en un lien. Vous arrêtez de
renvoyer les mêmes photos dix fois par semaine, et vous existez là où on
vous cherche.

Dites-moi votre activité, je vous envoie un exemple dans votre métier.
```

**On termine par une demande minuscule** (« votre activité »), pas par un prix. Celui qui
répond son métier a déjà commencé la vente sans le savoir.

### Contrôles propres à ce statut

| Contrôle | Pourquoi |
|---|---|
| **La voie vide est vraiment vide** | un seul véhicule dedans, et l’idée est morte |
| **Le phare lointain est présent et minuscule** | c’est lui qui transforme la métaphore en urgence |
| L’œil trouve la voie vide avant la file | c’est la lumière qui doit séparer, pas une flèche |
| Aucun échiquier, aucune main, aucune table | on prend le style de la référence, jamais son sujet |
| « The Zubix » n’apparaît nulle part | c’est la marque de quelqu’un d’autre |
| Le rouge des feux reste faible | s’il domine, la file devient le sujet |
| Rien dans les 220 px du haut ni les 340 px du bas | le phare lointain compte aussi |
| **Réduire à 20 %** | si « Doublez » ne se lit plus, le statut est mort |
| **La réponse à « VOIE » est prête avant de publier** | promettre une réponse et la faire attendre coûte plus que se taire |
| Aucune statistique | règle absolue de la maison |

---

## 9. Statut n° 7 · « EN CE MOMENT » · la peur, poussée au maximum

**Ce qui est demandé :** l’urgence et la peur en avant, et l’envie d’acheter dès la dernière
ligne lue. C’est le statut le plus agressif du document, et il n’est publiable **que parce
que celui d’hier n’a rien vendu du tout.**

### La peur qui marche, et les trois qui ne marchent pas

**Ne marchent pas :** la peur inventée (« il ne reste que 3 places »), la peur générale
(« le monde se digitalise »), la peur qui accuse (« vous êtes en retard »). La première se
démonte, la deuxième glisse, la troisième vexe. Un commerçant vexé ne répond pas, il ferme
le statut.

**Marche :** **la perte qu’on ne voit pas.** Un client qui vous cherche et ne vous trouve
pas ne se plaint jamais. Il n’écrit pas, il ne râle pas, il ne dit rien. **Il achète
ailleurs, et vous ne saurez jamais qu’il a existé.**

C’est la seule peur de la liste qui soit **vraie, invisible et sans reproche**. Le lecteur
ne peut pas la contredire, et surtout : **il ne peut pas se rassurer tout seul.** Il n’a
aucun moyen de vérifier que ça ne lui arrive pas. Une inquiétude qu’on ne peut pas éteindre
soi-même cherche une sortie, et la sortie, c’est nous.

### L’urgence, sans faux compte à rebours

Rien n’expire, rien n’est limité, aucune place n’est comptée. **L’urgence est que la perte
est continue et définitive.** Les clients d’hier ne reviennent pas, ceux de demain seront
plus nombreux. C’est vrai, ça ne se démonte pas, et ça ne s’use pas.

> **« Demain, ils seront plus nombreux. »**

### Les mots

> **Vous perdez des clients** · **en ce moment**
>
> *Ils ont cherché. Ils n’ont pas trouvé.*
> *Ils ont acheté ailleurs, et vous ne le saurez jamais.*
> *Demain, ils seront plus nombreux.*

**« en ce moment » est le mot énorme du cadre en pointillés.** Trois mots, présent, aucun
verbe : à 20 % il se lit encore, et il fait relever les yeux vers la petite ligne au-dessus.
La peur est au présent ou elle n’est pas.

⚠️ **C’est la ligne la plus dure jamais écrite ici.** Elle est défendable : pour un
commerçant absent d’internet, quelqu’un cherche en ce moment ce qu’il vend. Ce n’est pas une
statistique, c’est l’ordinaire, et le statut donne le moyen de le vérifier. Si elle paraît
trop frontale un jour, la remplacer par **« sans le savoir »** dans le cadre. Le reste ne
bouge pas.

### L’image

**Une main serrée, en très gros plan, et du sable lumineux qui coule entre les doigts** et
se perd dans le noir. Chaque grain est un client parti sans rien dire.

Pourquoi le sable : il **tombe tout seul**, on ne peut pas le rattraper, et il compte le
temps. Trois idées du post dans un seul objet. Et pourquoi lumineux : dans la direction de
la référence, **c’est la lumière qui désigne le sujet**, et une main qui se vide de sa
lumière raconte la perte sans une flèche ni un graphique.

C’est la même direction que « LA VOIE VIDE » (fond navy, duotone bleu, barre pleine et
cadre en pointillés), avec **une scène diamétralement différente** : hier un boulevard vu de
loin, aujourd’hui un macro serré. Deux statuts reconnaissables comme venant de la même
maison, sans se ressembler. C’est ce qui fait une direction, et plus une référence.

### Ce que le statut demande, et ce que ça engage

**« Répondez TEST à ce statut. »** On cherche leur commerce devant eux et on leur envoie ce
qu’on trouve. C’est gratuit, ça prend deux minutes, et **c’est la démonstration la plus
convaincante qui existe** : le doute qu’on vient d’installer, ils le lèvent eux-mêmes, et il
se referme du mauvais côté.

⚠️ **Ça engage vraiment.** Promettre une recherche et la faire attendre coûte plus cher que
tout le statut. **Les deux réponses possibles doivent être prêtes avant de publier**, y
compris celle du cas où le commerçant apparaît bien.

### Version 1 · direction « NUIT ÉLECTRIQUE » · le prompt

*Gardée : c’est la variante sombre du même message. La version publiée est la
**version 2** plus bas, « PLEIN SOLEIL ».*

```
===========================================================
NEBULA AGENCY — WHATSAPP STATUS — ONE IMAGE, 9:16
"EN CE MOMENT" — electric night direction
===========================================================

ATTACHED INPUTS — TWO attachments, IN THIS ORDER:
  1st = THE STYLE REFERENCE
  2nd = THE NEBULA LOGO
Never swap their roles: swapping them ruins the image. If the order
is ever unclear, fall back on their content, described below.

  THE STYLE REFERENCE (first attachment) = a very dark navy poster
     showing a blue-tinted dramatic close-up of a hand moving a
     chess piece on a board, with a small white headline sitting on
     a SOLID BLUE BAR that bleeds off the left edge, a much larger
     white headline inside a DASHED BLUE RECTANGLE, a logo at the
     top centre and a website address at the bottom centre.
     REPRODUCE ITS DESIGN SYSTEM COMPLETELY AND FAITHFULLY:
       - the DEEP NAVY / NEAR-BLACK ground
       - ONE single cold BLUE light source from the UPPER LEFT,
         hard, raking, leaving most of the frame in shadow
       - the BLUE DUOTONE photographic treatment: desaturated,
         high contrast, cinematic, almost monochrome
       - a TIGHT DRAMATIC CLOSE-UP OF A HAND as the central subject,
         filling the middle of the frame, at the same scale and with
         the same theatrical lighting as in the reference
       - the ROUNDED GEOMETRIC HEAVY SANS-SERIF lettering
       - THE TWO-PART HEADLINE DEVICE: a small line on a SOLID
         electric-blue bar bleeding off the LEFT EDGE, and under it
         a much larger line inside a DASHED electric-blue rectangle
       - the logo centred at the top, the address centred at the
         very bottom
       - its exact level of polish and finish
     Take NOTHING of its subject and none of its words. There is NO
     chess, NO chessboard, NO chess piece and NO game anywhere in
     the new image, and the words "The Zubix" appear nowhere.

  THE LOGO (second attachment) = the NEBULA Agency logo: a purple
     and blue cosmic swirl above the wordmark "NEBULA", with
     "AGENCY" underneath, on a transparent background.
     It is an ASSET TO PLACE, exactly as provided. It is never a
     style reference and never a subject to reinterpret.

-----------------------------------------------------------
TASK
-----------------------------------------------------------
Create ONE original WhatsApp status image for NEBULA Agency, a
digital studio in Cotonou, Benin, that builds pages and online
catalogues for West African merchants.
The idea: something valuable is running out of a closed hand, right
now, silently, and it cannot be caught again.
Cinematic, cold, tense, premium. Never cheap, never clip-art.

-----------------------------------------------------------
THE SUBJECT — extreme close-up, same scale as the reference
-----------------------------------------------------------
A HUMAN HAND in the centre of the frame, dark brown skin, seen very
close, held horizontally and CLENCHED into a loose fist, knuckles
up, tilted slightly toward the camera.
FROM BETWEEN THE FINGERS, FINE SAND IS POURING OUT in a thin
continuous stream, falling into the darkness below and dispersing.
THE SAND IS LUMINOUS: each grain glows cold electric blue, so the
falling stream is the BRIGHTEST THING in the picture, and the hand
that holds it is already darker than the sand escaping it.
Some grains catch the light on the way down and scatter like sparks.
The stream lands on a dark, matte, textured surface at the bottom
and disappears into shadow: no pile, no heap, nothing recovered.
The hand is straining slightly, tendons visible: it is trying to
hold, and it is losing.

Skin, sleeve and background all fall into the blue duotone. NO warm
tones anywhere. NO jewellery, NO watch, NO ring, NO tattoo, NO
sleeve logo.

-----------------------------------------------------------
THE LIGHT AND THE FRAME
-----------------------------------------------------------
One hard cold blue key light from the upper left, exactly as in the
reference, raking across the knuckles and the falling sand.
Everything else falls to near-black. The upper part of the frame is
clean empty darkness: the logo and the headline sit on it.
The lower part of the frame is dark, plain and uncluttered: the
small lines of text sit there.
Shallow depth of field, cinematic macro, visible skin texture and
individual grains in the lit area.

-----------------------------------------------------------
LOGO INTEGRATION — read twice, most attempts fail here
-----------------------------------------------------------
The logo attachment is a PNG with a TRANSPARENT background. Place
it at the TOP of the image, centred, on the dark background, small,
exactly as provided, and KEEP that transparency.
  - it sits DIRECTLY on the dark background. NO white box, NO black
    box, NO coloured plate, NO rounded card, NO badge, NO outline,
    NO glow, NO drop shadow behind it.
  - do NOT redraw it, restyle it, recolour it, stretch it, crop it,
    rotate it, or add a wordmark or tagline of your own.
  - size it so its wordmark stays comfortably readable when the
    whole image is viewed at 20% of its size.
A logo pasted on a plate is a failed image.

-----------------------------------------------------------
FORMAT AND SAFE ZONES — a status is covered by the interface
-----------------------------------------------------------
Canvas: 1080 x 1920 px, vertical 9:16.
WhatsApp draws its own interface ON TOP of the image:
  - the TOP 220 px are covered (profile picture, name, time)
  - the BOTTOM 340 px are covered (the "Reply" field)
The logo, every line of type, the hand and the falling sand must ALL
sit between y = 220 px and y = 1580 px. Nothing that matters may
fall inside those two strips.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
HEADLINE, part 1 — small white bold text on a SOLID ELECTRIC-BLUE
BAR that starts off the LEFT EDGE of the canvas and stops after the
words, exactly the device used in the reference:
    "Vous perdez des clients"

HEADLINE, part 2 — directly under it, MUCH larger, white, the
loudest element of the whole image, inside a DASHED ELECTRIC-BLUE
RECTANGLE OUTLINE, exactly the device used in the reference:
    "en ce moment"

THE MECHANISM, lower area, over the dark background, two lines,
centred, medium size, white:
    "Ils ont cherché. Ils n’ont pas trouvé."
    "Ils ont acheté ailleurs, et vous ne le saurez jamais."

THE URGENCY, one line under it, smaller, in electric blue:
    "Demain, ils seront plus nombreux."

THE ANSWER TO GIVE, one line under it, small, white, semi-bold:
    "Répondez TEST à ce statut."

FOOTER, at the very bottom of the safe area, tiny, centred, white at
reduced opacity:
    "nebula-agency.online"

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Top to bottom, all inside the safe band:
  1. NEBULA logo, centred on the dark background
  2. blue bar + "Vous perdez des clients"   (bleeds off the left)
  3. dashed rectangle + "en ce moment"      <- loudest zone
  4. THE CLENCHED HAND AND THE FALLING LUMINOUS SAND  <- largest
  5. the two lines of THE MECHANISM
  6. THE URGENCY
  7. "Répondez TEST à ce statut."
  8. nebula-agency.online
Lines 5 to 8 form ONE tight block over the dark lower area, with
generous space between that block and the hand above.
No text may cross the falling sand: the stream must stay clean and
unbroken from the fingers to the bottom of the subject area.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM: no translation, no rephrasing, no
  shortening, no added punctuation, no exclamation marks.
- Correct French typographic apostrophes ’ exactly as written:
  "n’ont".
- Correct diacritics: "cherché", "acheté", "à".
- The word "TEST" stays in capitals, exactly as written. Do not turn
  it into a button, a pill or a badge: it is plain text.
- "en ce moment" must still be readable when the image is viewed at
  20% of its size, and it must be the first thing the eye reads.
- No hashtag, no emoji, no icon, no arrow, no clock, no hourglass,
  no countdown, no timer, no star, no rating, no percentage sign.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO chess, NO chessboard, NO chess piece, NO game.
  The reference gives the design system and NOTHING of its subject.
- NO hourglass and NO clock anywhere: the sand alone tells the time.
- NO price, NO amount, NO currency symbol, NO offer, NO discount,
  NO percentage.
- NO invented statistics, follower counts, client counts, ratings or
  stars. No figures anywhere in the image.
- NO visible human face, NO head, NO body: one hand and part of a
  forearm only.
- NO coins, NO banknotes, NO money of any kind falling from the
  hand: it is sand, and only sand.
- NO recognisable third-party brand, logo or app, and the words
  "The Zubix" must not appear.
- NO watermark, no frame, no border around the image itself.
- One idea, told once. No second object, no second message.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1920 image, publication-ready, cinematic
quality, high-fidelity text rendering.
===========================================================
```

### Pour le fil Instagram et Facebook (4:5)

Même prompt, en remplaçant le bloc FORMAT. **La ligne « Répondez TEST à ce statut. »
disparaît** : sur un fil on ne répond pas à un statut. Elle passe dans la légende.

```
-----------------------------------------------------------
FORMAT
-----------------------------------------------------------
Canvas: 1080 x 1350 px, vertical 4:5, for an Instagram and Facebook
feed. No safe zones: the whole canvas is visible.
Crop tighter on the hand so it fills more of the frame, and keep the
same top-to-bottom order.

REMOVE ONE LINE: do not render "Répondez TEST à ce statut." on this
version. Everything else is unchanged.
```

### Le texte à écrire sous le statut

```
Un client mécontent, vous le savez. Il vous le dit, il râle, il revient
se plaindre.

Un client qui ne vous a pas trouvé ne dit rien.

Il a cherché votre commerce, il n’a rien vu, il a acheté ailleurs et il
n’y a plus jamais repensé. Vous n’avez reçu aucun message. Vous n’avez
rien vu passer. Pour vous, cette vente n’a jamais existé.

C’est le seul argent qu’on perd sans jamais l’apprendre.

Répondez TEST : je cherche votre commerce devant vous, et je vous envoie
exactement ce que votre client voit. C’est gratuit et ça prend deux
minutes.
```

**Pourquoi ça convertit :** le statut installe un doute que le lecteur **ne peut pas lever
tout seul**, puis lui tend le seul moyen de le lever. Répondre devient plus confortable que
ne pas répondre. C’est tout le mécanisme, et il est honnête : le test est réel et gratuit.

### Les deux réponses à préparer avant de publier

⚠️ **Il y a deux cas, et le second arrive souvent.** N’en préparer qu’un, c’est se
retrouver muet devant la moitié des réponses.

**Cas 1 · on ne le trouve pas.**

```
J’ai cherché [nom du commerce] comme le ferait un client. Voilà exactement
ce qui apparaît. [capture]

Ce n’est pas un problème de qualité, ni de prix, ni de réputation. C’est un
problème d’adresse : il n’y a rien à trouver.

La première marche est simple : on range tout ce que vous vendez à une seule
adresse, que vous envoyez en un lien. Dites-moi votre activité, je vous
envoie un exemple dans votre métier.
```

**Cas 2 · on le trouve, mais mal.**

```
Bonne nouvelle : on vous trouve. [capture]

Regardez maintenant ce que le client voit vraiment : pas de prix, pas de
liste de ce que vous vendez, la dernière publication date d’il y a
longtemps. Il a l’information qu’il vous cherchait, pas celle qui le fait
acheter.

Vous existez. Il manque l’endroit où on voit ce que vous vendez et combien.
Dites-moi votre activité, je vous envoie un exemple dans votre métier.
```

**Dans les deux cas on finit sur une demande minuscule** (« votre activité »), jamais sur un
prix : le socle veut qu’on entre par le Catalogue, et c’est la conversation qui décide de la
marche.

### Contrôles propres à ce statut

| Contrôle | Pourquoi |
|---|---|
| **Le sable est plus lumineux que la main** | c’est la perte qui doit briller, pas celui qui perd |
| **Rien ne se dépose en bas** | un petit tas, et on croit que ça se rattrape |
| Aucun sablier, aucune horloge, aucun compte à rebours | le sable dit déjà le temps ; un sablier fait publicité |
| **Aucune pièce, aucun billet** | de l’argent qui tombe d’une main, c’est un autre post et une autre promesse |
| Aucun échiquier, aucune main sur une table | on prend le système de la référence, jamais son sujet |
| Aucun texte ne traverse le filet de sable | c’est la seule chose que l’œil doit suivre |
| Rien dans les 220 px du haut ni les 340 px du bas | |
| **Réduire à 20 %** | si « en ce moment » ne se lit plus, le statut est mort |
| **Les DEUX réponses à « TEST » sont prêtes** | la moitié des gens sont dans le cas 2 |
| **Faire le test le jour même** | promettre une recherche et la faire attendre coûte plus que tout le statut |
| Aucune statistique | règle absolue de la maison |

⚠️ **Le prochain statut ne fait pas peur.** Deux peurs d’affilée et on devient la personne
qui angoisse tout le monde ; celui d’après doit donner quelque chose sans rien demander.

---

### Version 2 · direction « PLEIN SOLEIL » · **c’est celle à publier**

Référence : `references/REF-plein-soleil.jpg` (affiche « scale. Your Vision », mur teal et
sol ocre séparés par une arête nette, plein soleil, deux hommes en costume orange assis,
minuscules dans un mur immense et vide).

**Même message, même mécanisme, même « TEST ». Tout le reste change.**

#### Pourquoi une image ensoleillée fait plus peur qu’une image sombre

Le premier réflexe serait de refuser : cette référence est calme, lumineuse, presque
amusante, et le texte parle d’argent perdu. **C’est justement ce qui la rend meilleure.**

Une image sombre annonce la couleur : le lecteur voit qu’on va lui faire peur, il met sa
garde, il passe. **Une belle journée ensoleillée, un mur propre, un homme tranquille assis
au soleil : c’est un mardi ordinaire.** Et c’est exactement ce que dit le post, il ne se
passe rien de visible, et c’est là que ça se passe. La phrase brutale posée sur une image
paisible ne se voit pas venir, et **elle ne peut pas être classée comme « une pub qui fait
peur »**, donc elle n’est pas filtrée.

#### Ce que la référence donne, et qu’aucune autre n’avait

**Elle contient déjà le dispositif de comparaison : deux hommes identiques, côte à côte,
même costume, même posture, même soleil.** Il n’y a rien à inventer, il suffit de mettre
**une seule différence** entre eux, et elle devient énorme parce que tout le reste est
rigoureusement pareil.

**Et cette différence, la référence la fournit aussi : les ombres.** Le sol ocre en plein
soleil, avec ses longues ombres géométriques, est la signature de l’image. On s’en sert
pour dire la chose invisible du post.

> **À droite :** un homme, et sur le sol, en plus de la sienne, **cinq ou six longues ombres
> de gens debout qui montent vers lui.**
> **À gauche :** le même homme, le même costume, la même posture, et **rien**. Le sol autour
> de lui est nu.

Même métier, même jour, même soleil. **Pas les mêmes clients.** Et celui de gauche ne verra
jamais ce qui lui manque, puisqu’une ombre qui n’est pas venue ne fait pas de bruit.

⛔ **Aucun personnage ne doit avoir de corps dans les ombres.** Ce sont des ombres seules,
qui entrent par le bas du cadre. Des gens dessinés à côté et le post redevient une
illustration.

#### Le texte, dans la typographie de la référence

La référence empile quatre niveaux, et ils se remplissent un par un :

| Niveau de la référence | Chez nous |
|---|---|
| le mot énorme en bas de casse avec un point (*scale.*) | **« introuvable. »** |
| la ligne grasse dessous (*Your Vision*) | **« en ce moment »** |
| les trois mots très espacés (*FOCUS. DEPTH, IMPACT.*) | **« CHERCHÉ. RIEN. AILLEURS. »** |
| le petit paragraphe justifié en capitales | la phrase qui coupe |

**« introuvable. »** est le seul mot lisible à 20 %, et il dit déjà tout : c’est la
définition du problème en un mot. Les **trois mots espacés** racontent la vente perdue en
trois temps, à la place des trois vertus de la référence. Ce détournement est le cœur de
l’adaptation : **le gabarit de la référence sert à énumérer une perte au lieu d’énumérer des
qualités.**

⚠️ **Pas de pastille « vérifié ».** La référence en porte une à côté de son nom. Un badge de
vérification imité est un mensonge de plateforme, et il ne coûte rien à retirer : le logo se
pose directement sur le mur, il est plus beau comme ça.

⚠️ **Le teal est gardé.** Sur un bleu indigo, le logo NEBULA (violet et bleu) se noierait ;
sur le teal profond de la référence il ressort, et la vibe est intacte.

#### LE PROMPT

```
===========================================================
NEBULA AGENCY — WHATSAPP STATUS — ONE IMAGE, 9:16
"INTROUVABLE" — full sun, colour-block direction
===========================================================

ATTACHED INPUTS — TWO attachments, IN THIS ORDER:
  1st = THE STYLE REFERENCE
  2nd = THE NEBULA LOGO
Never swap their roles: swapping them ruins the image. If the order
is ever unclear, fall back on their content, described below.

  THE STYLE REFERENCE (first attachment) = a bright editorial poster
     with a deep TEAL wall filling the upper two thirds, a saturated
     OCHRE YELLOW ground filling the lower third, a thin orange lip
     between them, hard sunlight casting sharp geometric shadows,
     and two small men in identical bright orange suits sitting on
     the ledge with laptops. Its type is centred on the empty wall:
     one huge lowercase word with a full stop, a bold line under it,
     a row of three widely spaced bold capitalised words, and a
     small justified all-caps paragraph.
     REPRODUCE ITS DESIGN SYSTEM COMPLETELY AND FAITHFULLY:
       - the FLAT COLOUR BLOCKING: one large deep TEAL field above,
         one saturated OCHRE YELLOW field below, divided by a clean
         straight architectural ledge with a thin ORANGE lip
       - HARD DIRECT SUNLIGHT from the upper left, with crisp
         geometric shadows and one large diagonal shadow shape on
         the teal wall
       - the enormous EMPTY WALL: the human figures are small and
         the emptiness around them is most of the picture
       - editorial architectural photography, matte surfaces,
         slight wall texture, no gloss, no gradient
       - the TYPOGRAPHY SYSTEM described below, in a clean heavy
         GEOMETRIC SANS-SERIF, all type in white
       - its exact level of polish and finish
     Take NOTHING of its words and NOTHING of its branding. The
     words "scale", "Your Vision", "FOCUS", "DEPTH", "IMPACT" and
     "bizzjum" appear NOWHERE, and there is NO verified tick, NO
     white brand chip and NO social badge anywhere in the image.

  THE LOGO (second attachment) = the NEBULA Agency logo: a purple
     and blue cosmic swirl above the wordmark "NEBULA", with
     "AGENCY" underneath, on a transparent background.
     It is an ASSET TO PLACE, exactly as provided. It is never a
     style reference and never a subject to reinterpret.

-----------------------------------------------------------
TASK
-----------------------------------------------------------
Create ONE original WhatsApp status image for NEBULA Agency, a
digital studio in Cotonou, Benin, that builds pages and online
catalogues for West African merchants.
Two identical men, the same day, the same sun. One of them has
customers coming. The other one does not, and cannot see it.
Bright, calm, editorial, expensive. The image must look like an
ordinary sunny afternoon, never like an advertisement about fear.

-----------------------------------------------------------
THE SCENE — full bleed
-----------------------------------------------------------
A clean modern wall in hard sunlight, photographed straight on.
  - the UPPER TWO THIRDS: one flat DEEP TEAL wall, matte, softly
    textured, almost entirely empty. A large soft-edged diagonal
    shadow falls across its left side, exactly as in the reference.
  - a straight horizontal LEDGE crossing the frame, with a thin
    bright ORANGE lip along its front edge
  - the LOWER THIRD: a flat saturated OCHRE YELLOW ground in full
    sun, plain and open

SEATED ON THE LEDGE, small in the frame exactly like the reference:
TWO MEN, deliberately IDENTICAL. Same bright orange suit, same
build, same shoes, same posture: seated, knees apart, forearms on
the thighs, head lowered over a mobile phone held in both hands.
Dark brown skin. Heads down, faces not readable, no recognisable
identity, no hat, no jewellery, no visible logo on the clothing.
They are placed apart from each other with a clear gap of empty
ledge between them: one in the LEFT half, one in the RIGHT half.
Nothing distinguishes them. That is the point.

-----------------------------------------------------------
THE SHADOWS — this is the whole message, get it right
-----------------------------------------------------------
On the sunlit ochre ground, the sunlight casts long crisp shadows.

UNDER THE MAN ON THE RIGHT: his own long shadow, AND, converging
toward him, FIVE OR SIX LONG ELONGATED SHADOWS OF STANDING PEOPLE.
They enter from the BOTTOM EDGE of the frame and stretch up toward
him, as if a small group were standing in front of him just outside
the picture. They are SHADOWS ONLY: no bodies, no heads, no figures
anywhere in the frame, only their dark shapes on the yellow ground.

UNDER THE MAN ON THE LEFT: his own shadow, and NOTHING ELSE. The
ochre ground around him is completely bare and evenly lit.

The difference between the two sides must be obvious at a glance,
and it must be the ONLY difference in the entire picture.

-----------------------------------------------------------
LOGO INTEGRATION — read twice, most attempts fail here
-----------------------------------------------------------
The logo attachment is a PNG with a TRANSPARENT background. Place
it in the UPPER RIGHT of the teal wall, small, exactly as provided,
and KEEP that transparency.
  - it sits DIRECTLY on the teal wall. NO white chip, NO rounded
    pill, NO plate, NO badge, NO outline, NO glow, NO drop shadow,
    and above all NO VERIFIED TICK of any kind.
  - keep the wall behind it clean and evenly lit, with no shadow
    edge crossing it.
  - do NOT redraw it, restyle it, recolour it, stretch it, crop it,
    rotate it, or add a wordmark or tagline of your own.
  - size it so its wordmark stays comfortably readable when the
    whole image is viewed at 20% of its size.
Directly UNDER the logo, in small white type:
    "nebula-agency.online"

-----------------------------------------------------------
FORMAT AND SAFE ZONES — a status is covered by the interface
-----------------------------------------------------------
Canvas: 1080 x 1920 px, vertical 9:16.
WhatsApp draws its own interface ON TOP of the image:
  - the TOP 220 px are covered (profile picture, name, time)
  - the BOTTOM 340 px are covered (the "Reply" field)
The logo, every line of type, both men and ALL the shadows must sit
between y = 220 px and y = 1580 px. The extra height compared with
the reference goes into MORE EMPTY TEAL WALL above the type: the
emptiness is the luxury of this layout, do not fill it.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
All type is WHITE, centred on the teal wall, in a clean geometric
sans-serif, arranged exactly like the reference:

THE HUGE WORD — lowercase, very heavy, enormous, with a full stop,
the single loudest element of the image, exactly like the big word
in the reference:
    "introuvable."

THE BOLD LINE — directly under it, clearly smaller but still bold:
    "en ce moment"

THE THREE BEATS — one line further down, three short words in bold
capitals, spread WIDELY APART across the full width with large
even gaps between them, exactly the device used in the reference:
    "CHERCHÉ."        "RIEN."        "AILLEURS."

THE PARAGRAPH — under it, small, light weight, ALL CAPITALS, set
JUSTIFIED to both margins with exaggerated word spacing so the
lines align on both edges, exactly like the small paragraph in the
reference, two lines:
    "VOUS PERDEZ DES CLIENTS SANS LE SAVOIR. UN CLIENT QUI NE VOUS
    A PAS TROUVÉ NE DIT RIEN."

THE ANSWER TO GIVE — one line lower on the teal wall, just above
the seated men, small, white, semi-bold, centred:
    "Répondez TEST à ce statut."

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Top to bottom, all inside the safe band:
  1. empty teal wall
  2. NEBULA logo, upper right, and "nebula-agency.online" under it
  3. "introuvable."                          <- loudest zone
  4. "en ce moment"
  5. "CHERCHÉ."  "RIEN."  "AILLEURS."
  6. the justified two-line paragraph
  7. "Répondez TEST à ce statut."
  8. THE LEDGE, THE TWO IDENTICAL SEATED MEN
  9. THE OCHRE GROUND AND THE SHADOWS      <- second largest zone
No text at all sits on the ochre ground or over the men: everything
written lives on the empty teal wall, exactly as in the reference.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM: no translation, no rephrasing, no
  shortening, no added punctuation, no exclamation marks.
- THERE IS NO APOSTROPHE ANYWHERE IN THIS IMAGE. If an apostrophe
  appears, a word has been invented and the image is wrong.
- Keep the accents ON THE CAPITAL LETTERS, as French requires:
  "CHERCHÉ.", "TROUVÉ". Never "CHERCHE", never "TROUVE".
- "introuvable." stays lowercase and keeps its full stop.
- Each of the three beats keeps its own full stop: "CHERCHÉ."
  "RIEN." "AILLEURS."
- The word "TEST" stays in capitals, exactly as written. Do not turn
  it into a button, a pill or a badge: it is plain text.
- "introuvable." must still be readable when the image is viewed at
  20% of its size, and it must be the first thing the eye reads.
- No hashtag, no emoji, no icon, no arrow, no star, no rating, no
  percentage sign, no verified tick.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- The TWO MEN ARE IDENTICAL. Same suit, same colour, same posture,
  same build. If they differ in any way other than their shadows,
  the image has failed.
- The shadows of the crowd are SHADOWS ONLY: no bodies, no heads,
  no drawn people anywhere in the frame.
- NO verified tick, NO white brand chip, NO social badge, NO
  follower count, NO app interface.
- NO laptop brand, NO phone brand, NO visible screen content, NO
  readable text on any device.
- NO price, NO amount, NO currency symbol, NO offer, NO discount.
- NO invented statistics, client counts, ratings or stars. No
  figures anywhere in the image.
- NO readable face and no recognisable person: heads stay lowered.
- NO watermark, no frame, no border around the image itself.
- The teal wall stays FLAT and mostly EMPTY: no pattern, no poster,
  no window, no plant, no second object. The emptiness is the
  subject.
- One difference, told once.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1920 image, publication-ready, editorial
photographic quality, high-fidelity text rendering.
===========================================================
```

#### Pour le fil Instagram et Facebook (4:5)

C’est le format natif de la référence, donc c’est là qu’elle est la plus juste.

```
-----------------------------------------------------------
FORMAT
-----------------------------------------------------------
Canvas: 1080 x 1350 px, vertical 4:5, for an Instagram and Facebook
feed. No safe zones: the whole canvas is visible.
This is the reference's own proportion: follow its composition
exactly, with the teal wall filling the upper two thirds and the
ochre ground the lower third.

REMOVE ONE LINE: do not render "Répondez TEST à ce statut." on this
version. Everything else is unchanged.
```

**La légende et les deux réponses préparées ne changent pas** : ce sont celles du § 9,
elles servent aux deux versions.

#### Contrôles propres à cette version

| Contrôle | Pourquoi |
|---|---|
| **Les deux hommes sont vraiment identiques** | une seule différence ailleurs, et la comparaison ne veut plus rien dire |
| **Les ombres de foule sont des ombres seules** | des gens dessinés, et c’est une illustration, plus une photo |
| **Le sol est nu à gauche** | s’il y traîne une ombre, le post ne dit plus rien |
| Aucune pastille « vérifié », aucun jeton blanc | imiter un badge de plateforme est un mensonge, et ça se voit |
| Le mur teal reste vide | c’est le vide qui fait le luxe et qui porte le texte |
| Accents gardés sur les capitales | « CHERCHE » au lieu de « CHERCHÉ » et tout le bloc a l’air bâclé |
| Aucune apostrophe sur l’image | il n’y en a pas une seule ; s’il en apparaît une, un mot a été inventé |
| Aucun texte sur le sol ocre | tout vit sur le mur, comme dans la référence |
| **Réduire à 20 %** | si « introuvable. » ne se lit plus, le statut est mort |
| **Les DEUX réponses à « TEST » sont prêtes** | inchangé, voir plus haut |

---

## 10. Contrôles avant publication

| Contrôle | Pourquoi |
|---|---|
| Réduire à 20 % | Si l'accroche ne se lit plus, le statut est mort |
| **Poser l'image dans WhatsApp et regarder** | Le seul moyen de voir ce que l'interface recouvre |
| Rien dans les 220 px du haut ni les 340 px du bas | Sinon le texte finit derrière le champ « Répondre » |
| **Regarder l'écran dehors, en plein jour** | Un contraste qui passait à l'intérieur disparaît au soleil |
| Le logo n'a aucun cadre derrière lui | Une plaque blanche sous le logo, et tout a l'air amateur |
| La liste 1-2-3 se lit d'un coup d'œil | C'est elle qui déclenche la réponse |
| Un seul bloc énorme | Deux blocs énormes, et aucun n'est lu |
| **Les trois réponses sont prêtes** | Promettre une réponse et la faire attendre coûte plus que se taire |
| Aucune statistique | Règle absolue de la rubrique |

---

## 11. Les prochains statuts

Même gabarit : le label, la hiérarchie brutale, les zones mortes, et surtout **la question
fermée qui se répond d'un caractère**.

| Statut | L'accroche | Ce qu'on demande de répondre |
|---|---|---|
| **Le prix caché** | « CE N'EST PAS VOTRE PRIX QUI FAIT FUIR. » | « OUI » ou « NON » : affichez-vous vos prix ? |
| **L'heure du soir** | « ON VOUS ÉCRIT QUAND VOUS DORMEZ. » | l'heure à laquelle ils reçoivent le plus de messages |

*Le statut « Introuvable » qui était prévu ici est **fait** : c’est le § 9,
« EN CE MOMENT ». Une première version plus ancienne existe aussi dans
`POST-DU-JOUR-MULTICANAL.md`.*

⚠️ **Ne jamais enchaîner deux statuts qui font peur.** Entre deux, en publier un qui ne
vend rien et donne un savoir utile. C'est lui qui achète le droit d'être cru la fois
d'après.

---

*NEBULA Agency · Cotonou, Bénin · Document vivant. Ajouter chaque statut ici.*

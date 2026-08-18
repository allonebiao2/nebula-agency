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
> Version 1.0 · 2026-08-04

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

---

## 5. Contrôles avant publication

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

## 6. Les prochains statuts

Même gabarit : le label, la hiérarchie brutale, les zones mortes, et surtout **la question
fermée qui se répond d'un caractère**.

| Statut | L'accroche | Ce qu'on demande de répondre |
|---|---|---|
| **Introuvable** | « ILS ONT CHERCHÉ VOTRE COMMERCE. RIEN. » | « TEST », et on fait la recherche pour eux |
| **Le prix caché** | « CE N'EST PAS VOTRE PRIX QUI FAIT FUIR. » | « OUI » ou « NON » : affichez-vous vos prix ? |
| **L'heure du soir** | « ON VOUS ÉCRIT QUAND VOUS DORMEZ. » | l'heure à laquelle ils reçoivent le plus de messages |

*Le statut « Introuvable » a son prompt complet dans `POST-DU-JOUR-MULTICANAL.md`.*

⚠️ **Ne jamais enchaîner deux statuts qui font peur.** Entre deux, en publier un qui ne
vend rien et donne un savoir utile. C'est lui qui achète le droit d'être cru la fois
d'après.

---

*NEBULA Agency · Cotonou, Bénin · Document vivant. Ajouter chaque statut ici.*

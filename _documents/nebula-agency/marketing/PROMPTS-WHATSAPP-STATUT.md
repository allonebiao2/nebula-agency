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
  "QUELQU'UN, SI."

BRIDGE (under the headline, MUCH smaller, quiet, one line):
  "Il ne travaille pas plus que vous. Il a juste un pas dedans."

THE THREE THINGS (under the bridge, small, three numbered lines, each
                  starting with its numeral set in the accent colour,
                  the text itself in the plain text colour, generous
                  spacing between the three so the list is scannable):
  "1.  Une adresse où on vous trouve."
  "2.  Un prix qu'on peut lire."
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
  "qu'on", "diplôme", "Répondez".
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

---

## 4. Contrôles avant publication

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

## 5. Les prochains statuts

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

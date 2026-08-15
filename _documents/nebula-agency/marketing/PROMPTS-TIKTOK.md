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
  "QUELQU'UN, SI."

BODY (under the headline, MUCH smaller, quiet, three short lines):
  "Il ne travaille pas plus que toi."
  "Il a une adresse où on le trouve, un prix qu'on peut lire,"
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
  "qu'on", "diplôme".
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

---

## 4. Contrôles avant publication

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

## 5. Les prochains posts TikTok

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

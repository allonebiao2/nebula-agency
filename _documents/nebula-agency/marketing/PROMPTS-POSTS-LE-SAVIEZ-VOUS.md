# RUBRIQUE « LE SAVIEZ-VOUS ? »
## Prompt-maître et série de posts informatifs NEBULA

> **Le principe.** On ne vend pas, on enseigne. Chaque post apprend au lecteur quelque
> chose qu'il ignorait sur son propre métier. La vente vient après, toute seule, parce
> qu'on a été utile avant d'être commerçant.
>
> **La règle qui fait la série.** Le label « LE SAVIEZ-VOUS ? » ne change jamais : ni le
> texte, ni la position, ni la casse, ni la taille. C'est l'ancre de reconnaissance.
> Tout le reste change, ça jamais.
>
> Outil de génération : **Nano Banana Pro** (Gemini 3 Pro Image).
> Version 1.0 · 2026-07-30

---

## 1. Ce qui fait un post informatif qui marche

1. **Une seule idée par image.** Deux idées, c'est zéro idée retenue.
2. **Le titre ouvre une boucle.** Pas un intitulé de service, un fait que le lecteur
   n'avait jamais formulé.
3. **Le visuel enseigne, il ne décore pas.** Si on peut retirer l'image sans rien perdre,
   l'image ne sert à rien.
4. **Le logo est discret et toujours au même endroit.** C'est la répétition d'une position
   qui crée une série, pas la taille du logo.
5. **Le titre doit survivre en vignette.** À 20 % de sa taille : s'il est illisible, il est
   mort, parce que c'est comme ça qu'on le verra dans un fil.

**Interdit absolu : aucune statistique inventée.** « 73 % des clients vérifient en ligne »
circule partout et ne vient de nulle part. Le jour où quelqu'un demande la source, on perd
plus que le post n'a rapporté. Tous les visuels de cette série reposent sur des vérités
observables.

---

## 2. Le prompt-maître

**Les prompts sont en anglais** : les modèles d'image suivent les instructions de mise en
page plus fidèlement en anglais. **Tout le texte à afficher est en français entre
guillemets et ne doit jamais être traduit.**

**Ordre des pièces jointes : le logo en premier, la référence de style en second.**
Inversés, le modèle traite le logo comme un modèle de style et la marque disparaît.

```
===========================================================
NEBULA AGENCY : INFORMATIVE SOCIAL POST · MASTER PROMPT
===========================================================

ATTACHED INPUTS: read these roles carefully, do not confuse them:

  IMAGE 1 = THE LOGO.
     This is the official NEBULA Agency logo (cosmic galaxy swirl +
     "NEBULA AGENCY" wordmark). It is an ASSET TO PLACE, never a style
     reference and never a subject to reinterpret.

  IMAGE 2 = THE STYLE REFERENCE.
     This is an existing post whose CRAFT I want you to learn from.
     It is a reference for FORM ONLY. Its subject, its text, its brand
     and its message are irrelevant and must never appear in the output.

-----------------------------------------------------------
TASK
-----------------------------------------------------------
Create ONE original informative social media graphic for NEBULA Agency,
a digital studio in Cotonou, Benin, serving West African merchants.
The purpose is to TEACH the audience something they did not know.
This is editorial content, not an advertisement.

-----------------------------------------------------------
STYLE INHERITANCE : what to take from IMAGE 2
-----------------------------------------------------------
Study IMAGE 2 and reproduce its DESIGN LANGUAGE:
  - composition grid and how the canvas is divided
  - type hierarchy: relative sizes, weight contrast, letter-spacing
  - spacing rhythm and margin generosity
  - how graphic elements are drawn (flat, 3D, line art, glass, gradient)
  - lighting, depth, shadow and texture treatment
  - overall level of finish and density

Do NOT take from IMAGE 2:
  - its subject matter or imagery
  - any of its words, numbers or captions
  - its logo, brand or watermark
  - [MODE B] its colour palette

-----------------------------------------------------------
BRAND LOCK : non-negotiable, overrides the reference
-----------------------------------------------------------
MODE: B
  MODE A = inherit the reference palette as well (use only when the
           reference is already a NEBULA-branded visual)
  MODE B = keep the NEBULA palette below, inherit structure only

NEBULA palette:
  background   very dark navy-black #070A14
  primary glow violet #9B5CFF
  secondary    blue #4A7DFF
  accent       cyan #3FD8E6
  text         warm white #EAEEF9, muted grey-blue #9AA6C4 for secondary
  highlight    amber #F6A63C : used sparingly, one element maximum

Texture: fine star dust, subtle film grain, soft nebula bleed.
Never flat corporate stock. Never neon cyberpunk. Never clip-art.

LOGO PLACEMENT:
  Place IMAGE 1 exactly as provided, bottom-left, occupying about 12%
  of the canvas width, with clear margin. Pixel-faithful: do not redraw,
  restyle, recolour, crop, rotate or add a wordmark of your own.

-----------------------------------------------------------
SERIES CONSISTENCY: this is a recurring rubric
-----------------------------------------------------------
This image belongs to an ongoing series titled "LE SAVIEZ-VOUS ?".
The label always reads exactly "LE SAVIEZ-VOUS ?", always uppercase,
always in the same top-left position, always the same size, colour and
letter-spacing. It is the recognition anchor of the series and must be
identical across every post. Everything else changes; this never does.

-----------------------------------------------------------
CONTENT: the only block I edit between posts
-----------------------------------------------------------
TOPIC ....... [en une phrase, ce que le lecteur doit APPRENDRE]

LABEL ....... "LE SAVIEZ-VOUS ?"      <- FIXE, ne jamais modifier

HEADLINE .... "[ligne 1]"
              "[ligne 2]"
              Emphasis word: "[le mot à faire ressortir]"

TEACHING VISUAL (centre of the canvas, 40% of its height):
              [décrire le schéma, la comparaison ou la scène qui
               ENSEIGNE l'idée. Pas de décor : une démonstration.]
              Inline captions, if any:
              "[légende gauche]"  /  "[légende droite]"

BODY ........ "[une ou deux phrases courtes qui closent l'idée]"

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Format: 4:5 vertical, 1080 x 1350 px.
Four horizontal zones, top to bottom:
  1. LABEL          : small, uppercase, letter-spaced, muted    (~10%)
  2. HEADLINE       : large, bold, two lines, high contrast     (~20%)
  3. TEACHING VISUAL the demonstration, the heart of the image (~40%)
  4. BODY + LOGO    : body text, then logo bottom-left,
                      site URL bottom-right                     (~20%)
Generous negative space. Nothing touches the edges.

-----------------------------------------------------------
TEXT RENDERING : read twice
-----------------------------------------------------------
- Render ONLY the strings given in quotation marks in the CONTENT block,
  plus the site URL "nebula-agency.online" in tiny muted type bottom-right.
- Reproduce them VERBATIM. Do not translate, rephrase, shorten or complete.
- French text with correct diacritics: é è ê à â î ô û ç ù, and correct
  apostrophes (l'; d'; n'; s').
- The headline must remain legible when the image is viewed at 20% size.
- Absolutely NO other words, labels, captions, tags, numbers or UI text
  anywhere in the image.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO invented statistics, percentages or figures of any kind.
- NO faces, no recognisable people, no readable third-party brands.
- NO stock-photo look, no lens flare clutter, no random floating icons.
- NO watermark, no signature, no frame, no border.
- One single idea per image. If it needs two, it needs two posts.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080x1350 graphic, publication-ready, high fidelity text.
===========================================================
```

**Logo à joindre :** `nebula-affilies/static/nebula-logo.png`

---

## 3. La série · 8 posts

Ne changer que le bloc `CONTENT`. La légende accompagne la publication.

### Post 1 · La durée de vie d'un contenu

```
TOPIC ....... Un contenu publié s'enfonce dans le fil et devient
              introuvable ; un lien reste atteignable indéfiniment.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "Un post descend."
              "Un lien reste."
              Emphasis word: "reste"
TEACHING VISUAL:
              Side-by-side diagram. LEFT: five small photo-cards along a
              descending curve, each lower, smaller and more faded, dissolving
              into darkness; a thin dotted line traces the fall. RIGHT: one
              upright luminous card bearing a small QR code, perfectly stable,
              casting a steady vertical cyan beam upward. Thin vertical divider.
              Inline captions: "Vos photos dans le fil" / "Votre catalogue en ligne"
BODY ........ "Sur les réseaux, vos photos s'enfoncent dans le fil.
              Un lien, lui, ne descend jamais."
```
**Légende :** Vos photos d'il y a deux semaines, vos clients ne les voient plus. Elles ne
sont pas supprimées : elles sont enterrées. Un lien, lui, reste au même endroit pour toujours.

### Post 2 · La vérification silencieuse

```
TOPIC ....... Avant d'appeler, les gens cherchent votre nom. S'ils ne
              trouvent rien, ils renoncent sans jamais vous le dire.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "Le client qui ne"
              "vous appelle jamais"
              Emphasis word: "jamais"
TEACHING VISUAL:
              Quiet cinematic scene. Foreground: stylised smartphone at an
              angle, screen glowing cold blue, showing a search bar containing
              "nom du commerce" and below it an empty result area : a thin grey
              line and a faded magnifier icon. The emptiness must read as
              "nothing found". Background, soft focus: silhouette of a person
              walking away to the right toward a small warmly lit storefront.
              No face, no readable brand.
BODY ........ "Avant d'appeler, il cherche votre nom. S'il ne trouve rien,
              il n'appelle pas."
              "Et il ne vous dira jamais pourquoi."
```
**Légende :** Celui-là, vous ne saurez jamais qu'il a existé. Il a cherché, il n'a rien
trouvé, il est allé ailleurs. C'est le client le plus cher du monde : celui qu'on perd
sans le voir.

### Post 3 · Ce qu'il y a vraiment dans un QR code

```
TOPIC ....... Un QR code ne contient pas une image ni un catalogue :
              il contient une adresse. Si l'adresse meurt, tous les QR
              imprimés deviennent inutiles.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "Un QR code ne contient"
              "pas vos produits."
              Emphasis word: "pas"
TEACHING VISUAL:
              A clean QR code on the left. From its centre, a single luminous
              violet thread unspools to the right, straightening into a stylised
              address bar, then arriving at a small glowing product-card panel.
              Three stages, one continuous thread, left to right.
              Inline captions: "Le QR" / "Une adresse" / "Vos produits"
BODY ........ "Il contient une adresse. Si l'adresse change, tous vos QR
              déjà imprimés deviennent morts."
```
**Légende :** C'est pour ça qu'on ne donne jamais une adresse provisoire à un client.
Le QR que vous collez sur votre comptoir doit pointer vers quelque chose qui ne bougera
plus. Sinon, vous réimprimez tout.

### Post 4 · Locataire ou propriétaire

```
TOPIC ....... Sur un réseau social, vous êtes locataire : le compte, les
              photos et l'audience appartiennent à la plateforme.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "Votre page ne vous"
              "appartient pas."
              Emphasis word: "pas"
TEACHING VISUAL:
              Side-by-side architectural metaphor, minimal line-art with glow.
              LEFT: a small shop suspended inside a large translucent floating
              container, no ground beneath it, a thin chain holding it up.
              RIGHT: a small solid house standing on visible foundations, warm
              light inside, roots of light going into the ground.
              Inline captions: "Sur un réseau" / "Chez vous"
BODY ........ "Un compte peut être bloqué du jour au lendemain.
              Un site, lui, reste à vous."
```
**Légende :** Demandez autour de vous : tout le monde connaît quelqu'un dont la page a été
bloquée ou piratée. Ce jour-là, on ne perd pas des photos. On perd des années de clients.

### Post 5 · Le prix qu'on n'ose pas demander

```
TOPIC ....... Beaucoup de clients partent sans demander le prix. L'absence
              de prix affiché crée une gêne, et la gêne fait fuir.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "Il est parti sans"
              "demander le prix."
              Emphasis word: "sans"
TEACHING VISUAL:
              Two panels, same shelf of stylised products in both.
              LEFT: no price tags at all; a customer silhouette stands facing
              the shelf, then a faded duplicate of the same silhouette turning
              away to the left, motion trail behind it. A small "?" floats above.
              RIGHT: the same shelf with small glowing price tags on every item;
              the silhouette leans in, hand reaching toward a product.
              Inline captions: "Sans prix" / "Avec les prix"
BODY ........ "Tout le monde n'ose pas demander. Un prix affiché,
              c'est une gêne en moins entre vous et la vente."
```
**Légende :** On croit qu'afficher ses prix fait fuir. C'est l'inverse : ce sont les prix
cachés qui font fuir, silencieusement, et vous ne le voyez jamais.

### Post 6 · Le coût de revient

```
TOPIC ....... Le prix d'achat n'est pas le coût de revient. Beaucoup de
              commerçants vendent à perte sans jamais s'en apercevoir.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "On peut vendre à perte"
              "sans le savoir."
              Emphasis word: "perte"
TEACHING VISUAL:
              A vertical stacked-bar diagram, clean and precise, glowing edges.
              A tall column built of four stacked blocks of decreasing brightness,
              labelled inside from bottom to top: "Achat", "Transport",
              "Emballage", "Pertes". A horizontal amber line crosses the column
              near the top, labelled at its right end: "Prix de vente". The top
              block clearly rises ABOVE that line, glowing red-amber at the tip.
              No numbers anywhere.
BODY ........ "Le prix d'achat n'est qu'une partie du coût. Transport,
              emballage, pertes, votre temps : tout compte."
```
**Légende :** C'est le calcul que presque personne ne fait, et c'est celui qui décide si
votre mois a été bon ou pas. Beaucoup de commerçants travaillent beaucoup et gagnent peu,
simplement parce qu'un seul produit leur coûte plus cher qu'ils ne le croient.

### Post 7 · La lumière de midi

```
TOPIC ....... La lumière dure de midi écrase les couleurs et creuse des
              ombres noires. Le matin et la fin d'après-midi donnent de
              bien meilleures photos de produits.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "Vos photos ratent"
              "à cause de l'heure."
              Emphasis word: "l'heure"
TEACHING VISUAL:
              The same single stylised product object, shown twice side by side
              on a plain neutral surface.
              LEFT: lit from directly overhead by harsh light : washed-out
              colours, a hard black shadow directly beneath, blown highlights.
              RIGHT: lit by soft low-angle warm light : rich saturated colour,
              a long soft shadow, gentle gradient on the surface.
              Inline captions: "Midi" / "Le matin"
BODY ........ "Photographiez le matin ou en fin d'après-midi, à l'ombre,
              sur un fond uni. Rien d'autre à changer."
```
**Légende :** Aucun logiciel ne rattrape une mauvaise lumière. Essayez demain matin avec
le même produit et le même téléphone : vous verrez la différence tout de suite.

### Post 8 · Ceux qui achètent de loin

```
TOPIC ....... La diaspora achète pour sa famille restée au pays, mais
              elle ne peut rien vérifier à distance, donc elle n'ose pas.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "Il veut commander"
              "de l'étranger."
              Emphasis word: "l'étranger"
TEACHING VISUAL:
              A simplified globe curve at the bottom of the frame, with a thin
              luminous arc travelling from upper-left down to a glowing point
              on the curve. At the arc's origin, a small phone screen showing
              an empty search result : a thin grey line, nothing found. The arc
              begins solid, then breaks into a dotted line halfway and fades
              out before reaching the destination point.
              No flags, no country names, no readable text on the globe.
BODY ........ "Il veut payer pour sa famille restée ici. Mais il ne peut
              rien vérifier, alors il renonce."
```
**Légende :** Ce client-là est le plus facile à convaincre et le plus difficile à
atteindre. Il a l'argent, il a l'envie, il n'a que la preuve qui manque.

---

---

## 3bis. La semaine complète · 7 posts, du lundi au dimanche

**Même prompt-maître, même rubrique.** On ne change que le bloc `CONTENT`.
Cette série se publie **un post par jour pendant sept jours** : un rythme de campagne,
à utiliser au lancement de la vague 1 ou avant une tournée de prospection.

⚠️ L'alternance est calculée : **jamais deux « ça vous concerne » d'affilée.**
Quatre posts ne vendent rien du tout. Ce sont eux qui achètent le droit aux trois autres.

| Jour | Post | Famille | Ce que ça sert |
|---|---|---|---|
| Lundi | 9 · La zone du pouce | **Cadeau pur** |, |
| Mardi | 10 · Le nom mal écrit | Ça vous concerne | Vitrine |
| Mercredi | 11 · 4 Mo contre 200 Ko | **Cadeau pur** |, |
| Jeudi | 12 · Le catalogue qui vit enfermé | **Cadeau pur** | Catalogue (en creux) |
| Vendredi | 13 · Les douze allers-retours | Ça vous concerne | Catalogue |
| Samedi | 14 · L'heure où l'on vous écrit | **Cadeau pur** |, |
| Dimanche | 15 · Le client que vous avez déjà | Ça vous concerne | Outil métier |

---

### Post 9 · Lundi · La zone du pouce

```
TOPIC ....... On tient son téléphone d'une main. Le pouce n'atteint
              confortablement que le bas de l'écran. Un bouton placé en
              haut demande un effort, et l'effort fait renoncer.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "Votre bouton est"
              "trop haut."
              Emphasis word: "haut"
TEACHING VISUAL:
              Clean instructional diagram. A stylised smartphone seen from the
              front, held in one hand, the hand rendered as a simple silhouette
              gripping the lower left edge. Overlaid on the screen: a translucent
              arc sweeping from the thumb's base across the LOWER THIRD of the
              screen, glowing warm and clearly reachable. Above that arc, the
              upper two thirds are rendered cold, dim and slightly desaturated.
              A single call-to-action button sits INSIDE the warm arc, luminous.
              A second, ghosted button sits in the cold zone, faded, with a
              small thin arrow showing the thumb straining upward and not
              quite reaching it.
              Inline captions: "Zone du pouce" (on the warm arc) /
              "Zone morte" (on the cold area)
BODY ........ "Le pouce ne monte pas."
              "Ce qui compte se met en bas."
```
**Légende :** Regardez comment vous tenez votre téléphone en ce moment. Une main, un pouce,
et un arc de cercle qui s'arrête au tiers de l'écran. Tout ce qui est au-dessus demande de
se replacer. Sur un site, ce petit effort suffit à faire renoncer. Le numéro, le bouton
« commander », le WhatsApp : en bas, toujours.

---

### Post 10 · Mardi · Le nom mal écrit

```
TOPIC ....... Vos clients n'écrivent pas votre nom comme vous l'écrivez.
              Accents oubliés, espaces en trop, orthographe approximative.
              Sans page à vous, ces recherches ne mènent nulle part 
              ou pire, chez un autre.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "Personne n'écrit"
              "votre nom comme vous."
              Emphasis word: "personne"
TEACHING VISUAL:
              Composition on two levels. TOP: four small paper slips at slight
              random angles, each showing the SAME business name written
              differently : with and without accents, with a space, with a
              spelling slip. Render them as handwriting-like type, imperfect,
              human. Each slip has a thin arrow leaving it. BOTTOM: all four
              arrows converge into ONE upright luminous card bearing a small QR
              code, perfectly stable and sharp. The contrast is between four
              uncertain attempts and one certain destination.
              Inline captions: "Quatre façons de l'écrire" (top) /
              "Une seule adresse" (bottom)
BODY ........ "Il tape votre nom de mémoire."
              "S'il se trompe, il ne vous trouve pas."
```
**Légende :** Votre nom, vous l'écrivez parfaitement. Vos clients, non. Ils oublient un
accent, ajoutent un espace, se trompent d'une lettre : et ils ne recommencent pas. Une
adresse à vous, un QR code, un lien : ça marche même quand la mémoire ne marche pas.

---

### Post 11 · Mercredi · 4 Mo contre 200 Ko

```
TOPIC ....... Une photo sortie d'un téléphone pèse plusieurs mégaoctets.
              Réduite correctement, elle pèse vingt fois moins et reste
              identique à l'œil. Sur une connexion mobile, c'est la
              différence entre huit secondes d'attente et une.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "Votre photo pèse"
              "vingt fois trop."
              Emphasis word: "vingt"
TEACHING VISUAL:
              A balance scale, seen straight on, elegant and minimal.
              LEFT PAN, sunk low under the weight: a photo card, and beside it
              a bold weight label "4 Mo" and a small circular loading indicator
              with "8 s". RIGHT PAN, risen high: THE EXACT SAME photo card,
              visually identical in sharpness and colour, with the label
              "200 Ko" and a small check mark with "1 s". The two photo cards
              must be indistinguishable : that is the entire point of the image.
              Inline caption running under both pans:
              "Même photo. Même netteté."
BODY ........ "L'œil ne voit pas la différence."
              "La connexion, si."
```
**Légende :** Une photo prise au téléphone sort à 4 Mo. Sur une 4G qui tousse, c'est huit
secondes d'écran blanc : et huit secondes, personne ne les attend. Réduite à 200 Ko, c'est
exactement la même photo à l'œil, et elle s'affiche tout de suite. On ne perd pas en
qualité, on perd du poids.

---

### Post 12 · Jeudi · Le catalogue qui vit enfermé

```
TOPIC ....... Le catalogue de WhatsApp Business est un bon outil, mais il
              n'existe que dans WhatsApp : on ne peut pas le trouver sur
              internet, ni l'ouvrir sans l'application, ni le mettre sur
              une affiche autrement qu'en passant par un numéro.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "Votre catalogue vit"
              "enfermé."
              Emphasis word: "enfermé"
TEACHING VISUAL:
              A glass dome, drawn in thin luminous lines, sealed on a dark
              surface. INSIDE the dome: a small warm-lit grid of product cards,
              cosy and complete, clearly alive. OUTSIDE the dome, in cold grey:
              a browser window, a search field, and a printed poster : all
              rendered dim and unreachable. One thin arrow leaves the outside
              world toward the dome and BOUNCES OFF its surface, drawn with a
              small deflection mark. No brand names, no app logos of any kind.
              Inline captions: "Il vit ici" (inside) /
              "Il n'existe pas ici" (outside)
BODY ........ "Il est très bien là où il est."
              "Le problème, c'est qu'il n'en sort pas."
```
**Légende :** Le catalogue de WhatsApp Business est utile, et gratuit : on ne va pas dire
le contraire. Mais il ne vit que dans l'application. On ne le trouve pas sur internet, on
ne l'ouvre pas sans avoir le numéro, on ne le met pas sur une affiche. Ce n'est pas un
mauvais outil : c'est un outil qui n'a pas de porte vers l'extérieur.

---

### Post 13 · Vendredi · Les douze allers-retours

```
TOPIC ....... Une vente sans prix affiché coûte une dizaine de messages :
              c'est combien, tu l'as en rouge, tu livres, c'est disponible.
              Une page qui répond d'avance remplace toute la conversation.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "Douze messages"
              "pour une vente."
              Emphasis word: "Douze"
TEACHING VISUAL:
              Split composition, vertical divider. LEFT: a tall stacked column
              of twelve chat bubbles, cramped and repetitive, the same short
              questions recurring : render three of them legibly:
              "C'est combien ?", "Tu l'as en rouge ?", "Tu livres ?" : and let
              the rest fade into a compressed grey stack. A large numeral "12"
              floats faintly behind them. RIGHT: ONE single luminous product
              card, showing a price line, three small colour dots, and a small
              delivery icon : everything answered at once. A large numeral "1"
              behind it, clean and confident.
              Inline captions: "Douze messages" / "Un lien"
BODY ........ "Chaque question posée est une vente ralentie."
              "Répondez avant qu'elle arrive."
```
**Légende :** Comptez vos conversations d'hier. Combien de fois avez-vous écrit le même
prix, la même couleur, le même « oui je livre » ? Ce ne sont pas des clients difficiles :
ce sont des informations qui manquaient. Une page qui répond d'avance vous rend vos
journées.

---

### Post 14 · Samedi · L'heure où l'on vous écrit

```
TOPIC ....... Les gens regardent les commerces le soir, entre 21 h et 23 h,
              une fois la journée finie. C'est l'heure où le commerçant
              dort : donc l'heure où personne ne répond.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "On vous écrit"
              "quand vous dormez."
              Emphasis word: "dormez"
TEACHING VISUAL:
              A circular 24-hour dial, drawn in thin elegant lines on a dark
              field, hours marked discreetly. A luminous arc glows along the
              segment between 21 and 23, clearly the brightest zone of the
              whole ring. Small message icons cluster densely along that arc
              and thin out everywhere else. At the centre of the dial, a small
              simple house shape with one warmly lit window. The rest of the
              ring stays cold and quiet.
              Inline caption on the glowing arc: "21 h : 23 h"
BODY ........ "Le client décide le soir."
              "Il achète chez celui qui a déjà répondu."
```
**Légende :** Le soir, la journée est finie, le téléphone sort. C'est là qu'on regarde les
boutiques, qu'on compare, qu'on décide. Et c'est là que personne ne répond. Le lendemain
matin, la décision est déjà prise : ailleurs. Une page qui affiche tout travaille pendant
que vous dormez.

---

### Post 15 · Dimanche · Le client que vous avez déjà

```
TOPIC ....... Faire revenir un client coûte bien moins cher que d'en
              trouver un nouveau. Mais sans son nom ni son numéro quelque
              part, on recommence à zéro à chaque fois : on rachète les
              mêmes clients toute l'année.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "Vous rachetez les mêmes"
              "clients chaque mois."
              Emphasis word: "rachetez"
TEACHING VISUAL:
              Two parallel paths, seen side by side, separated by a thin divider.
              LEFT PATH: faint human silhouettes enter through a door, pass a
              counter, and exit through a back opening into darkness : the path
              is one-way and the figures dissolve as they leave. Nothing remains
              behind them. RIGHT PATH: the same silhouettes follow the same
              route, but each one leaves behind a small luminous contact card
              at the counter; the cards accumulate into a neat, orderly, glowing
              stack, and a thin curved arrow loops from the stack back to the
              entrance door.
              Inline captions: "Il achète, il repart" (left) /
              "Il achète, il revient" (right)
BODY ........ "Le client le moins cher est celui"
              "qui vous connaît déjà."
```
**Légende :** Trouver un nouveau client coûte cher : de l'affichage, du temps, de la
persuasion. Le faire revenir ne coûte presque rien : à condition de savoir qui il est.
Sans un endroit où son nom reste, chaque mois recommence à zéro. Ce n'est pas un problème
de clients : c'est un problème de mémoire.

---

### Comment enchaîner les deux séries

Les 8 posts du §3 tiennent **un mois à deux publications par semaine**.
Les 7 posts ci-dessus tiennent **une semaine à un post par jour**.

**L'ordre recommandé :** la semaine intensive d'abord, pour exister d'un coup, puis le
rythme de croisière mardi/vendredi avec la série de huit. Après quinze posts, on ne
recommence pas au début : on reprend les deux ou trois qui ont le mieux marché, on refait
l'image, on change la légende. Un bon post se republie ; un fil neuf ne se fabrique pas
chaque semaine.

## 4. Le rythme de publication

**Deux publications par semaine, mardi et vendredi.** Huit posts tiennent un mois complet.
*Pour une campagne intensive d'un post par jour pendant sept jours, voir le §3bis.*

| Famille | Posts | Ce qu'elle fait |
|---|---|---|
| **Ça vous concerne** | 1, 2, 4, 5, 8 | Le lecteur se reconnaît, et il pense à NEBULA |
| **Cadeau pur** | 3, 6, 7 | Aucune vente derrière, juste un savoir utile |

**Ne jamais publier deux « ça vous concerne » d'affilée.** C'est le post 7, celui sur la
lumière, qui achète le droit de publier le post 2. Une série qui ne fait que remuer le
couteau finit par être vue comme de la publicité déguisée ; une série qui donne vraiment
gagne le droit d'être crue quand elle parle de nous.

---

## 5. Dépannage

| Ce qui rate | Ce qu'on ajoute au prompt |
|---|---|
| Le sujet de la référence réapparaît | `IMAGE 2 is a FORM reference only. Its subject must not appear. If in doubt, ignore its content entirely.` |
| Le logo est redessiné | `The logo must be a pixel-faithful placement of IMAGE 1. Treat it as a pasted asset, not as something to generate.` |
| Du texte parasite s'ajoute | `Render ONLY the quoted strings. Any additional word is a failure.` |
| Les accents sautent | `Render French text with correct diacritics and apostrophes.` |
| Titre illisible en vignette | `Increase headline size by 30% and reduce the teaching visual accordingly.` |

**Le seul test qui compte :** réduire le résultat à 20 %. Si le titre ne se lit plus,
regénérer. C'est le défaut qui tue un post dans un fil, et le seul qu'on ne rattrape pas
au montage.

---

## 6. Pourquoi cette série renforce la vente

Les posts 1, 2, 5 et 6 sont **exactement les insights centraux des guides de vente** :

| Post | Guide correspondant |
|---|---|
| 1 · Un post descend, un lien reste | `03-GUIDE-CATALOGUE.md`, chapitre 2 |
| 2 · La vérification silencieuse | `04-GUIDE-VITRINE.md`, le test Google |
| 5 · Le prix qu'on n'ose pas demander | `03-GUIDE-CATALOGUE.md`, les 3 fuites d'argent |
| 6 · Le coût de revient | `05-GUIDE-OUTIL-METIER.md`, les 4 fuites |

Les partenaires diront donc en boutique exactement ce que les posts racontent en ligne.
Le prospect a déjà entendu l'idée avant que le vendeur n'arrive : c'est ce qui transforme
une visite en conversation.

---



---

# DIRECTION ARTISTIQUE 2 · COLLAGE ÉDITORIAL ROUGE ET NOIR

> **Ajoutée le 2026-08-02**, d'après une planche de référence validée par Mongazi.
> Elle **ne remplace pas** la direction précédente : c'est un second registre, plus
> spectaculaire, réservé aux posts qui doivent arrêter le pouce.
>
> ⚠️ **Cette direction n'utilise PAS la palette du site NEBULA** (bleu, cyan, or).
> Elle est volontairement en **rouge, noir et gris clair**. Assumé : sur un fil, le
> rouge pur arrête l'œil là où le bleu se fond dans l'interface.

## Les sept marqueurs du style, à répéter dans chaque prompt

1. **Trois couleurs, pas une de plus** : gris papier très clair `#EDECEA`, noir profond,
   et **un seul rouge saturé** `#E01A1A`. Tout le reste est désaturé.
2. **Le sujet est un découpage**, posé sur le fond comme un collage, avec un bord net.
3. **Une tranche décalée** : une bande horizontale du sujet est glissée de quelques pixels
   sur le côté. C'est la signature du style.
4. **Des barres et blocs rouges géométriques**, souvent en bas ou derrière le sujet.
5. **Typographie display à empattements, généreuse et un peu rétro**, en très gros corps,
   mélangée à des petits mots en italique manuscrite. Certains mots en rouge, d'autres en noir.
6. **Des annotations fines** : un trait qui relie un mot à un détail encadré du sujet.
7. **Texture papier** en fond, grain visible, et parfois un immense mot fantôme en contour
   qui déborde du cadre.

## Les règles de la série qui NE changent pas

Le label **« LE SAVIEZ-VOUS ? »**, sa position, sa casse. Le logo discret, toujours au même
endroit. **Aucune statistique inventée.** Le texte français rendu VERBATIM, jamais traduit.

---

## PROMPT A · le post de demain (image seule, 4:5)

**Sujet : le vrai concurrent d'un commerçant, c'est le temps de réponse.**
Vérité observable, aucun chiffre inventé.

```
Create ONE original informative social media graphic for NEBULA Agency.

ATTACHED INPUTS:
  IMAGE 1 = THE LOGO. An asset to place, never a style reference.
  IMAGE 2 = THE STYLE REFERENCE. Learn its CRAFT only. Its subject,
            its text and its brand must never appear in the output.

ART DIRECTION: reproduce this craft exactly:
Bold editorial collage poster. STRICTLY THREE COLOURS: a very light warm
grey paper background (#EDECEA) with visible paper grain and a faint
circular brushed texture, deep black, and ONE saturated red (#E01A1A).
Everything else is desaturated to black and white. The red is used only
for accents: geometric bars, a few words, one object.

SUBJECT (cut-out collage, centred, occupying the middle 45% of the canvas):
A classical marble bust in sharp black and white, photographed straight on.
A HORIZONTAL SLICE across the eyes is offset a few pixels to the right,
like a mis-registered print. Where the mouth should be, an antique
hourglass is embedded, and the sand falling inside it is BRIGHT RED.
A thin red annotation line runs from the hourglass to a small red-outlined
square in the empty space, labelled with the small caption below.
Two solid red horizontal bars sit behind the base of the bust.

TEXT TO RENDER: verbatim, French, correct diacritics and apostrophes.
Render NOTHING else:
  Small label, top left, uppercase, letter-spaced, dark grey:
      "LE SAVIEZ-VOUS ?"
  Headline, three stacked lines, mixed sizes, top area:
      "Votre pire"            <- small, italic script, black
      "CONCURRENT"            <- HUGE display serif, RED, the hero word
      "n'est pas la boutique d'a cote"   <- small, black, uppercase tracking
      (render this last line exactly as: "n'est pas la boutique d'à côté")
  Tiny caption at the annotation square, red:
      "le temps de reponse"   -> render as: "le temps de réponse"
  Body paragraph, small, justified, lower left, dark grey, 2 lines:
      "Pendant qu'il attend votre prix, il compare. Le client qui doit
      demander combien ça coûte a déjà commencé à chercher ailleurs."
  Site URL, tiny, muted, bottom right:
      "nebula-agency.online"

LAYOUT: 4:5 vertical, 1080 x 1350 px. Generous negative space. Nothing
touches the edges. The logo sits bottom left, small and discreet.

TYPOGRAPHY: a characterful display serif with slight retro swashes for the
hero word, a clean grotesque for the small text. The headline must stay
legible at 20% size.

NO other words, no numbers, no watermark, no UI elements, no extra logos.
```

---

## PROMPTS B · CARROUSEL TIKTOK, 3 IMAGES

**Format : 9:16, 1080 x 1920 px.** ⚠️ **Zones de sécurité TikTok :** rien d'important dans
les **250 px du bas** (légende et boutons) ni dans les **150 px de droite** (colonne
d'icônes). Toute la composition doit vivre dans le tiers central haut.

**Sujet du carrousel : un client qui doit demander le prix achète moins.**

> **Le fil narratif :** image 1 nomme la douleur, image 2 l'explique, image 3 donne
> la sortie. Une seule idée traverse les trois. Si on peut lire l'image 3 sans avoir vu
> la 1, le carrousel a raté.

### IMAGE 1 · LE HOOK

```
Create ONE original social media graphic for NEBULA Agency, first slide of
a 3-slide TikTok carousel.

ATTACHED INPUTS:
  IMAGE 1 = THE LOGO. An asset to place, never a style reference.
  IMAGE 2 = THE STYLE REFERENCE. Learn its CRAFT only, never its content.

ART DIRECTION: bold editorial collage. STRICTLY THREE COLOURS: very light
warm grey paper background (#EDECEA) with paper grain, deep black, and ONE
saturated red (#E01A1A). All imagery desaturated to black and white, red
reserved for accents only.

SUBJECT (cut-out collage, upper-centre, 40% of canvas height):
A black and white hand holding an old smartphone, seen from the side. The
screen is BLANK RED, empty, no interface, no icons. A HORIZONTAL SLICE
across the phone is offset to the left, breaking the object in two. Behind
the hand, an enormous ghost word in red outline only, cropped by the frame
edges, unreadable as a whole. One thick red bar runs under the hand.

TEXT TO RENDER: verbatim French, correct diacritics. Nothing else:
  Headline, stacked, centred, mixed sizes:
      "Il n'a pas dit"        <- small, italic script, black
      "NON"                   <- ENORMOUS display serif, RED
      "il a juste arrete de repondre"
      (render exactly as: "il a juste arrêté de répondre")
                              <- small, black, uppercase, letter-spaced
  Tiny prompt, bottom centre, dark grey, small:
      "Glissez"
  Logo bottom left, small and discreet.

LAYOUT: 9:16 vertical, 1080 x 1920 px. Keep ALL text and the subject inside
the central column: leave 150 px clear on the right edge and 250 px clear
at the bottom. Generous negative space at the top.

NO other words, no numbers, no watermark, no UI elements.
```

### IMAGE 2 · LA VALEUR

```
Create ONE original social media graphic for NEBULA Agency, second slide of
a 3-slide TikTok carousel. Same series, same craft as the previous slide.

ATTACHED INPUTS:
  IMAGE 1 = THE LOGO. An asset to place.
  IMAGE 2 = THE STYLE REFERENCE. Craft only.

ART DIRECTION: identical to slide 1. Light grey paper background (#EDECEA)
with grain, deep black, one saturated red (#E01A1A). Desaturated imagery,
red accents only. This slide must feel like the same poster series.

SUBJECT (cut-out collage, centre, 40% of canvas height):
A split comparison, two black and white shop scenes side by side, separated
by a thin vertical red line. LEFT: a market stall where a price tag hangs
BLANK and empty. RIGHT: the same stall where the price tag is a solid RED
rectangle, filled. A thin red annotation line runs from each tag to its
caption. A horizontal slice across both scenes is offset, in the style of a
mis-registered print.

TEXT TO RENDER: verbatim French, correct diacritics. Nothing else:
  Small label, top left, uppercase, letter-spaced, dark grey:
      "LE SAVIEZ-VOUS ?"
  Headline, stacked, mixed sizes, upper area:
      "Un prix cache"         <- render as: "Un prix caché"
                              <- small, italic script, black
      "FAIT FUIR"             <- HUGE display serif, RED
      "avant meme la question"
                              <- render as: "avant même la question"
                              <- small, black, uppercase, letter-spaced
  Two tiny captions at the annotation lines, dark grey:
      left:  "il demande, il attend, il compare"
      right: "il decide"      <- render as: "il décide"
  Body paragraph, small, justified, lower area, 2 lines:
      "Le prix visible n'est pas une faiblesse. C'est ce qui permet au
      client de dire oui pendant qu'il en a encore envie."
  Logo bottom left, small and discreet.

LAYOUT: 9:16 vertical, 1080 x 1920 px. Leave 150 px clear on the right edge
and 250 px clear at the bottom.

NO other words, no numbers, no percentages, no statistics, no watermark.
```

### IMAGE 3 · L'APPEL À L'ACTION

```
Create ONE original social media graphic for NEBULA Agency, final slide of
a 3-slide TikTok carousel. Same series, same craft as the two previous
slides.

ATTACHED INPUTS:
  IMAGE 1 = THE LOGO. An asset to place.
  IMAGE 2 = THE STYLE REFERENCE. Craft only.

ART DIRECTION: identical to slides 1 and 2. Light grey paper background
(#EDECEA) with grain, deep black, one saturated red (#E01A1A).

SUBJECT (cut-out collage, upper-centre, 35% of canvas height):
A black and white hand holding a smartphone, mirroring slide 1 but now the
screen shows a clean RED QR code, sharp and complete. A second black and
white hand enters from the right edge and scans it. A horizontal slice
across the phone is offset, keeping the series signature. Two thick red
bars anchor the composition beneath the hands. Small red arrows point from
the QR code outward.

TEXT TO RENDER: verbatim French, correct diacritics. Nothing else:
  Headline, stacked, mixed sizes, upper area:
      "Vos prix, vos photos"  <- small, italic script, black
      "EN UN SCAN"            <- HUGE display serif, RED
  Body, small, centred, 2 lines, dark grey:
      "NEBULA Agency fabrique le catalogue de votre commerce.
      Vos clients l'ouvrent sans rien installer."
  Call to action block, lower-centre, red rectangle with light text inside:
      "ECRIVEZ-NOUS SUR WHATSAPP"
      (render exactly as: "ÉCRIVEZ-NOUS SUR WHATSAPP")
  Two short lines under the block, small, black, one per line:
      "Abonnez-vous pour la suite"
      "Dites en commentaire : votre metier"
      (render exactly as: "Dites en commentaire : votre métier")
  Site URL, tiny, muted:
      "nebula-agency.online"
  Logo bottom left, small and discreet.

LAYOUT: 9:16 vertical, 1080 x 1920 px. Leave 150 px clear on the right edge
and 250 px clear at the bottom. The call to action block must sit ABOVE
that bottom safe zone, never inside it.

NO other words, no numbers, no watermark, no fake UI, no invented handles.
```

---

## Ce qu'il faut vérifier sur les trois images avant de publier

| | |
|---|---|
| **Les trois couleurs** | Gris papier, noir, un seul rouge. Si une quatrième couleur apparaît, régénérer |
| **La zone basse** | 250 px libres en bas, 150 px à droite. Sinon TikTok mange le texte |
| **Les accents** | é è à ê ç corrects. Les modèles les perdent souvent : c'est le défaut n°1 |
| **La cohérence** | Les 3 images doivent se ressembler. Si la 2 ou la 3 dérive, la régénérer en joignant la 1 comme référence supplémentaire |
| **Aucun chiffre** | Pas de pourcentage, pas de statistique. Règle absolue de la rubrique |
| **Le logo** | Même position sur les 3, discret |

---

*NEBULA Agency · Cotonou, Bénin · Document vivant. Ajouter chaque nouveau post ici.*

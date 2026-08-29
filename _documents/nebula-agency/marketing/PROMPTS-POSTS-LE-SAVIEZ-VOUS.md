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
>
> **Troisième direction artistique, « BLEU ÉLECTRIQUE » : voir le §7.** Blanc pur, un seul
> bleu, grotesque géométrique, annotation par pastilles. Diamétralement opposée aux deux
> autres, et faite pour parler à un chef d'entreprise.
>
> **Format carrousel :** voir `PROMPTS-CARROUSELS.md`. Il porte une **deuxième direction
> artistique** (« MARBRE & ROUGE » : papier os, un seul rouge éditorial, sculpture de
> marbre), à ne pas mélanger avec celle-ci dans une même campagne. Le label
> « LE SAVIEZ-VOUS ? » est le même dans les deux : c'est lui qui fait la série.

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
NEBULA AGENCY — INFORMATIVE SOCIAL POST · MASTER PROMPT
===========================================================

ATTACHED INPUTS — read these roles carefully, do not confuse them:

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
STYLE INHERITANCE — what to take from IMAGE 2
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
BRAND LOCK — non-negotiable, overrides the reference
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
  highlight    amber #F6A63C — used sparingly, one element maximum

Texture: fine star dust, subtle film grain, soft nebula bleed.
Never flat corporate stock. Never neon cyberpunk. Never clip-art.

LOGO PLACEMENT:
  Place IMAGE 1 exactly as provided, bottom-left, occupying about 12%
  of the canvas width, with clear margin. Pixel-faithful: do not redraw,
  restyle, recolour, crop, rotate or add a wordmark of your own.

-----------------------------------------------------------
SERIES CONSISTENCY — this is a recurring rubric
-----------------------------------------------------------
This image belongs to an ongoing series titled "LE SAVIEZ-VOUS ?".
The label always reads exactly "LE SAVIEZ-VOUS ?", always uppercase,
always in the same top-left position, always the same size, colour and
letter-spacing. It is the recognition anchor of the series and must be
identical across every post. Everything else changes; this never does.

-----------------------------------------------------------
CONTENT — the only block I edit between posts
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
  1. LABEL          — small, uppercase, letter-spaced, muted    (~10%)
  2. HEADLINE       — large, bold, two lines, high contrast     (~20%)
  3. TEACHING VISUAL— the demonstration, the heart of the image (~40%)
  4. BODY + LOGO    — body text, then logo bottom-left,
                      site URL bottom-right                     (~20%)
Generous negative space. Nothing touches the edges.

-----------------------------------------------------------
TEXT RENDERING — read twice
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
              "nom du commerce" and below it an empty result area — a thin grey
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
              "à cause de l’heure."
              Emphasis word: "l'heure"
TEACHING VISUAL:
              The same single stylised product object, shown twice side by side
              on a plain neutral surface.
              LEFT: lit from directly overhead by harsh light — washed-out
              colours, a hard black shadow directly beneath, blown highlights.
              RIGHT: lit by soft low-angle warm light — rich saturated colour,
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
              "de l’étranger."
              Emphasis word: "l'étranger"
TEACHING VISUAL:
              A simplified globe curve at the bottom of the frame, with a thin
              luminous arc travelling from upper-left down to a glowing point
              on the curve. At the arc's origin, a small phone screen showing
              an empty search result — a thin grey line, nothing found. The arc
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
Cette série se publie **un post par jour pendant sept jours** — un rythme de campagne,
à utiliser au lancement de la vague 1 ou avant une tournée de prospection.

⚠️ L'alternance est calculée : **jamais deux « ça vous concerne » d'affilée.**
Quatre posts ne vendent rien du tout. Ce sont eux qui achètent le droit aux trois autres.

| Jour | Post | Famille | Ce que ça sert |
|---|---|---|---|
| Lundi | 9 · La zone du pouce | **Cadeau pur** | — |
| Mardi | 10 · Le nom mal écrit | Ça vous concerne | Vitrine |
| Mercredi | 11 · 4 Mo contre 200 Ko | **Cadeau pur** | — |
| Jeudi | 12 · Le catalogue qui vit enfermé | **Cadeau pur** | Catalogue (en creux) |
| Vendredi | 13 · Les douze allers-retours | Ça vous concerne | Catalogue |
| Samedi | 14 · L'heure où l'on vous écrit | **Cadeau pur** | — |
| Dimanche | 15 · Le client que vous avez déjà | Ça vous concerne | Outil métier |

---

### Post 9 · Lundi — La zone du pouce

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

### Post 10 · Mardi — Le nom mal écrit

```
TOPIC ....... Vos clients n'écrivent pas votre nom comme vous l'écrivez.
              Accents oubliés, espaces en trop, orthographe approximative.
              Sans page à vous, ces recherches ne mènent nulle part —
              ou pire, chez un autre.
LABEL ....... "LE SAVIEZ-VOUS ?"
HEADLINE .... "Personne n'écrit"
              "votre nom comme vous."
              Emphasis word: "personne"
TEACHING VISUAL:
              Composition on two levels. TOP: four small paper slips at slight
              random angles, each showing the SAME business name written
              differently — with and without accents, with a space, with a
              spelling slip. Render them as handwriting-like type, imperfect,
              human. Each slip has a thin arrow leaving it. BOTTOM: all four
              arrows converge into ONE upright luminous card bearing a small QR
              code, perfectly stable and sharp. The contrast is between four
              uncertain attempts and one certain destination.
              Inline captions: "Quatre façons de l'écrire" (top) /
              "Une seule adresse" (bottom)
BODY ........ "Il tape votre nom de mémoire."
              "S’il se trompe, il ne vous trouve pas."
```
**Légende :** Votre nom, vous l'écrivez parfaitement. Vos clients, non. Ils oublient un
accent, ajoutent un espace, se trompent d'une lettre — et ils ne recommencent pas. Une
adresse à vous, un QR code, un lien : ça marche même quand la mémoire ne marche pas.

---

### Post 11 · Mercredi — 4 Mo contre 200 Ko

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
              must be indistinguishable — that is the entire point of the image.
              Inline caption running under both pans:
              "Même photo. Même netteté."
BODY ........ "L'œil ne voit pas la différence."
              "La connexion, si."
```
**Légende :** Une photo prise au téléphone sort à 4 Mo. Sur une 4G qui tousse, c'est huit
secondes d'écran blanc — et huit secondes, personne ne les attend. Réduite à 200 Ko, c'est
exactement la même photo à l'œil, et elle s'affiche tout de suite. On ne perd pas en
qualité, on perd du poids.

---

### Post 12 · Jeudi — Le catalogue qui vit enfermé

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
              a browser window, a search field, and a printed poster — all
              rendered dim and unreachable. One thin arrow leaves the outside
              world toward the dome and BOUNCES OFF its surface, drawn with a
              small deflection mark. No brand names, no app logos of any kind.
              Inline captions: "Il vit ici" (inside) /
              "Il n’existe pas ici" (outside)
BODY ........ "Il est très bien là où il est."
              "Le problème, c’est qu’il n’en sort pas."
```
**Légende :** Le catalogue de WhatsApp Business est utile, et gratuit — on ne va pas dire
le contraire. Mais il ne vit que dans l'application. On ne le trouve pas sur internet, on
ne l'ouvre pas sans avoir le numéro, on ne le met pas sur une affiche. Ce n'est pas un
mauvais outil : c'est un outil qui n'a pas de porte vers l'extérieur.

---

### Post 13 · Vendredi — Les douze allers-retours

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
              questions recurring — render three of them legibly:
              "C’est combien ?", "Tu l’as en rouge ?", "Tu livres ?" — and let
              the rest fade into a compressed grey stack. A large numeral "12"
              floats faintly behind them. RIGHT: ONE single luminous product
              card, showing a price line, three small colour dots, and a small
              delivery icon — everything answered at once. A large numeral "1"
              behind it, clean and confident.
              Inline captions: "Douze messages" / "Un lien"
BODY ........ "Chaque question posée est une vente ralentie."
              "Répondez avant qu’elle arrive."
```
**Légende :** Comptez vos conversations d'hier. Combien de fois avez-vous écrit le même
prix, la même couleur, le même « oui je livre » ? Ce ne sont pas des clients difficiles :
ce sont des informations qui manquaient. Une page qui répond d'avance vous rend vos
journées.

---

### Post 14 · Samedi — L'heure où l'on vous écrit

```
TOPIC ....... Les gens regardent les commerces le soir, entre 21 h et 23 h,
              une fois la journée finie. C'est l'heure où le commerçant
              dort — donc l'heure où personne ne répond.
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
              Inline caption on the glowing arc: "21 h — 23 h"
BODY ........ "Le client décide le soir."
              "Il achète chez celui qui a déjà répondu."
```
**Légende :** Le soir, la journée est finie, le téléphone sort. C'est là qu'on regarde les
boutiques, qu'on compare, qu'on décide. Et c'est là que personne ne répond. Le lendemain
matin, la décision est déjà prise — ailleurs. Une page qui affiche tout travaille pendant
que vous dormez.

---

### Post 15 · Dimanche — Le client que vous avez déjà

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
              counter, and exit through a back opening into darkness — the path
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
persuasion. Le faire revenir ne coûte presque rien — à condition de savoir qui il est.
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

## 7. Troisième direction artistique · « BLEU ÉLECTRIQUE »

**Référence :** `references/REF-bleu-electrique.jpg` · format **4:5, 1080 x 1350**.

C'est la troisième direction de la maison, et elle est **diamétralement opposée aux deux
autres** : là où « MARBRE & ROUGE » est un papier imprimé et où la nuit cosmique est une
nébuleuse, celle-ci est **blanche, nette, commerciale**. Aucun grain, aucune texture, aucune
poésie. C'est le registre des studios SaaS, et c'est exactement ce qui manquait à NEBULA pour
parler à un chef d'entreprise plutôt qu'à un lecteur.

### Les neuf marqueurs à respecter

1. **Fond blanc pur** `#FFFFFF`. Aucune texture, aucun grain, aucun dégradé de fond.
2. **Un seul bleu électrique**, celui de la référence, autour de `#0F5BFF`. Avec le noir et le
   blanc, ça fait trois valeurs et pas une de plus.
3. **Une forme organique bleue** en haut à gauche, à pétales arrondis, **qui déborde du
   cadre**. C'est la seule fantaisie de la direction.
4. **Le logo en haut à droite**, petit, en noir.
5. **Le titre en trois lignes d'intensité croissante**, et c'est LA signature :
   - ligne 1 : noir nu ;
   - ligne 2 : noir **dans un cadre à filet fin bleu** ;
   - ligne 3 : **blanc sur un bloc bleu plein, légèrement incliné**, et énorme.
6. **Typographie** : un grotesque géométrique très gras, **en casse mixte**, jamais en
   capitales. Interlettrage serré.
7. **Un mockup produit au centre**, photographique, posé sur une **dalle de pierre en noir et
   blanc** qui traverse le bas du cadre.
8. **Des pastilles bleues arrondies flottantes** : un cercle blanc avec une icône à gauche, un
   libellé blanc à droite, **reliées au mockup par un trait pointillé bleu fin à angle droit**.
9. **L'adresse du site en bas, centrée**, en blanc sur la pierre.

### ⚠️ Les deux pièges de cette référence

**1. Les pastilles de la référence contiennent un chiffre de notoriété inventé.** Elle
affiche « Trusted By 1000+ Clients ». NEBULA en a une dizaine, tous vérifiables et tous
nommés dans l'avis de recrutement. **Ne jamais recopier ce genre de pastille.** Une agence de
Cotonou qui annonce mille clients se fait démonter en un commentaire, et elle perd bien plus
que le post ne rapporte. Dans notre version, **les pastilles ne portent aucun argument de
vente et aucun chiffre** : elles portent les questions du client.

**2. Le label de la rubrique doit se déplacer un peu.** La forme organique occupe l'angle
supérieur gauche, donc « LE SAVIEZ-VOUS ? » se pose **juste en dessous**, toujours aligné à
gauche et toujours en haut. C'est le seul assouplissement accepté, et il vaut pour toute
cette direction.

---

## 8. Post n° 16 · « ILS POSENT TOUS LES MÊMES QUESTIONS. »

**Direction : BLEU ÉLECTRIQUE · 4:5 · famille « ça vous concerne ».**

### Ce que le post enseigne, et pourquoi c'est un vrai retournement

Tout le monde subit les mêmes messages sans jamais y voir autre chose que de l'agacement :
*« c'est combien ? »*, *« c'est disponible ? »*, *« tu livres ? »*, dix fois par jour.

Le renversement tient en une phrase : **ce ne sont pas des questions, ce sont des
informations qui manquent.** Une question qu'on vous repose n'est pas un client pénible,
c'est **un trou dans votre présentation, et il est toujours au même endroit**.

À partir de là, le lecteur ne voit plus jamais ces messages de la même façon. C'est ça, un
« le saviez-vous » qui vaut d'être publié : il change ce qu'on voit, pas ce qu'on sait.

### Pourquoi ça convertit, sans qu'on vende quoi que ce soit

Parce que le remède est **évident et visible dans l'image elle-même**. Le dispositif
d'annotation de la référence sert ici à montrer que **les trois questions ont déjà leur
réponse écrite** sur une fiche produit : le prix, la disponibilité, la livraison. Le lecteur
n'a pas besoin qu'on lui dise ce qu'il lui faut, il le voit.

**On inverse l'usage du dispositif :** la référence annote un produit pour vanter ses
qualités ; nous, on annote un produit avec **les questions du client**, et chaque trait
pointillé va se poser sur la ligne qui y répond déjà. C'est la démonstration, pas l'argument.

### L'appel à l'action, et pourquoi il est facile

*« Répondez-moi la question qu'on vous pose le plus. »* Il la connaît par cœur, il la tape en
trois mots, sans réfléchir. Et **cette question dit tout de son commerce** : celui qui répond
« c'est combien ? » n'affiche pas ses prix, celui qui répond « c'est où ? » n'a pas d'adresse
trouvable. La conversation démarre au bon endroit sans qu'on ait rien demandé d'autre.

⚠️ **La promesse engage :** on répond où cette information devrait être écrite, concrètement,
et gratuitement. **Aucun devis dans cette réponse.**

### LE PROMPT

```
===========================================================
NEBULA AGENCY — SOCIAL POST « LE SAVIEZ-VOUS ? » — 4:5
DIRECTION: ELECTRIC BLUE
===========================================================

ATTACHED INPUTS — TWO attachments.
Identify them BY THEIR CONTENT, not by their order. Never swap their
roles: swapping them ruins the image.

  THE LOGO = the attachment showing the NEBULA Agency logo: a purple
     and blue cosmic swirl above the wordmark "NEBULA", with "AGENCY"
     underneath, on a transparent background.
     It is an ASSET TO PLACE, exactly as provided. It is never a style
     reference and never a subject to reinterpret.

  THE STYLE REFERENCE = the other attachment. It is a white, blue and
     black agency poster showing a laptop on a stone slab with floating
     blue pills. Its DESIGN LANGUAGE is the design language of this
     post, and it must be followed closely.

  If you hesitate: the attachment with a transparent background and a
  readable "NEBULA AGENCY" wordmark is THE LOGO. The other one is THE
  STYLE REFERENCE.

-----------------------------------------------------------
TASK
-----------------------------------------------------------
Create ONE original social media image for NEBULA Agency, a digital
studio in Cotonou, Benin, serving West African merchants and business
owners.
It teaches ONE idea that changes how the reader sees something they
live through every single day. Clean, commercial, confident, modern.
It must look designed and expensive, never cheap, never homemade.

-----------------------------------------------------------
THE DESIGN LANGUAGE — copy the reference closely, this one time
-----------------------------------------------------------
Unlike other briefs, here you follow the STYLE REFERENCE tightly. Take
all nine of these from it:

  1. PURE WHITE background #FFFFFF. No texture, no grain, no gradient
     backdrop, no paper, no noise. Absolutely flat white.
  2. ONE electric blue only, the blue of the reference, around #0F5BFF.
     With black and white that makes three values and no more. No
     second accent colour anywhere.
  3. An ORGANIC BLUE SHAPE with rounded petals in the TOP-LEFT corner,
     bleeding off the edge of the canvas.
  4. Type: a heavy GEOMETRIC GROTESQUE, tight letter-spacing, set in
     MIXED CASE. Never all caps.
  5. The headline in THREE lines of rising intensity, exactly as in the
     reference. This is the signature of the design, reproduce it:
       line 1 — plain black text, medium size
       line 2 — black text INSIDE a thin blue outlined rectangle
       line 3 — WHITE text on a SOLID BLUE BLOCK, slightly rotated,
                by far the largest element of the image
  6. A photographic PRODUCT MOCKUP at the centre, resting on a
     BLACK-AND-WHITE STONE SLAB that crosses the lower part of the
     frame. The slab is desaturated; everything else keeps its colour.
  7. FLOATING BLUE PILLS: rounded blue capsules, each with a white
     circle holding a simple line icon on the left and a white label
     on the right, casting a soft shadow.
  8. Each pill is joined to the mockup by a THIN DASHED BLUE LINE that
     turns at a RIGHT ANGLE, exactly like the reference.
  9. The website address at the BOTTOM, centred, in white type over
     the dark stone.

-----------------------------------------------------------
THE MOCKUP AND THE ANNOTATION — this is the whole idea
-----------------------------------------------------------
Replace the reference's laptop with a MODERN SMARTPHONE, seen straight
on, standing upright on the stone slab, screen clearly readable.
On its screen: a clean, well-designed PRODUCT PAGE. A large product
photograph at the top, and under it a short stack of lines, of which
THREE must be plainly visible and legible:
     a PRICE line, an AVAILABILITY line, and a DELIVERY line.
Then a single blue action button at the bottom of the screen.
Design that page in the same white-and-electric-blue language: it is a
NEBULA product, not a copy of an existing app.

THE THREE PILLS CARRY THE CUSTOMER'S QUESTIONS, and each dashed line
lands precisely on the line of the screen that already answers it:
  - the pill "C’est combien ?"    points at the PRICE line
  - the pill "C’est disponible ?" points at the AVAILABILITY line
  - the pill "Tu livres ?"        points at the DELIVERY line
That correspondence is the entire demonstration: the questions people
keep asking are already answered, in writing, in one place. Make each
dashed line clearly reach its own target and no other.

-----------------------------------------------------------
LOGO INTEGRATION — read twice, most attempts fail here
-----------------------------------------------------------
The logo attachment is a PNG with a TRANSPARENT background. Place it
in the TOP-RIGHT corner, small, exactly as provided, and KEEP that
transparency.
  - it sits DIRECTLY on the white. NO white box, NO coloured plate, NO
    rounded card, NO badge, NO circle, NO outline, NO glow, NO shadow.
  - do NOT redraw it, restyle it, recolour it, stretch it, crop it,
    rotate it, or add a wordmark or tagline of your own.
  - keep the area behind it perfectly empty white.
  - size it so its wordmark stays comfortably readable when the whole
    image is viewed at 20% of its size.
A logo pasted on a plate is a failed image.

-----------------------------------------------------------
FORMAT
-----------------------------------------------------------
Canvas: 1080 x 1350 px, vertical 4:5, for an Instagram and Facebook
feed. Generous margins. Nothing important touches the edges, except
the organic blue shape, which is meant to bleed off the top-left.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
LABEL (top-left, just under the organic blue shape, small, uppercase,
       widely letter-spaced, in the electric blue):
  "LE SAVIEZ-VOUS ?"

HEADLINE (centred, three stacked lines of rising intensity):
  line 1, plain black, medium:                 "Ils posent tous"
  line 2, black inside a thin blue outline:    "les mêmes"
  line 3, white on a solid slightly rotated
          blue block, ENORMOUS:                "questions."

THE THREE PILLS (on the mockup, exactly as described above):
  "C’est combien ?"
  "C’est disponible ?"
  "Tu livres ?"

THE LESSON (under the mockup, black, small, two lines, centred):
  "Ce ne sont pas des questions."
  "Ce sont des informations qui manquent."

CALL TO ACTION (under the lesson, in the electric blue, one line):
  "Répondez-moi celle qu’on vous pose le plus."

FOOTER: the site address at the very bottom, centred, in white over
the stone: "nebula-agency.online"

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Top to bottom:
  1. organic blue shape (top-left) · LOGO (top-right)
  2. LABEL
  3. HEADLINE, three stacked lines      <- the loudest zone
  4. THE PHONE ON THE STONE, WITH ITS THREE PILLS  <- the largest zone
  5. THE LESSON, two lines
  6. CALL TO ACTION
  7. site address over the stone
The three pills sit around the phone, not on top of it: two on the
left edge and one on the right, so the screen stays fully readable.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM: no translation, no rephrasing, no
  shortening, no added punctuation, no exclamation marks.
- Correct French typographic apostrophes ’ exactly as written:
  "C’est", "qu’on".
- Correct diacritics: "mêmes", "Répondez".
- Keep the space before the question marks, as French requires:
  "C’est combien ?", "C’est disponible ?", "LE SAVIEZ-VOUS ?"
- The headline must be readable at 20% of the image size.
- The price, availability and delivery lines on the phone screen may
  show short realistic French labels, but NO amount, NO number, NO
  currency: write them as words only.
- No hashtag, no social icon, no emoji.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- NO client-count claim, NO "1000+ clients", NO rating, NO star, NO
  award badge, NO testimonial. The reference has one; it must NOT be
  copied. NEBULA has a dozen clients and every claim it makes is
  verifiable.
- NO invented statistics, percentages or figures of any kind, anywhere,
  including on the phone screen.
- NO price, NO amount, NO currency.
- NO human face, no portrait, no person.
- NO recognisable third-party brand, app, messaging interface, chat
  bubble, green tick or app icon. The screen is a NEBULA product page.
- NO second accent colour: white, black, and one electric blue.
- NO watermark, no frame, no border.
- ONE single idea in this image.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1350 image, publication-ready,
high-fidelity text rendering.
===========================================================
```

### Pour le passer en statut WhatsApp (9:16)

Trois lignes à remplacer, rien d’autre :

```
FORMAT: 1080 x 1920 px, vertical 9:16.
SAFE ZONES: the TOP 220 px are covered by the WhatsApp profile bar and
the BOTTOM 340 px by the reply field. Nothing that matters may sit in
those two strips: the logo, the label, the headline, the phone, the
pills, the lesson and the call to action all live between 220 px and
1580 px from the top.
CALL TO ACTION: replace it with "Répondez à ce statut avec celle qu’on
vous pose le plus."
```

### La légende

```
Ce ne sont pas des questions.

« C’est combien ? » · « C’est disponible ? » · « Tu livres ? »
Dix fois par jour, les mêmes, à des gens différents.

On croit que ce sont des clients pénibles. C’est l’inverse : ce sont des clients
intéressés, qui butent sur la même information manquante. Une question qu’on vous
repose n’est jamais un hasard. C’est un trou, et il est toujours au même endroit.

Écrivez la réponse une seule fois, à un endroit qu’on peut ouvrir, et vous
arrêtez de la donner vingt fois par semaine. Ce n’est pas du temps gagné :
c’est de la vente qui arrête de refroidir.

Répondez-moi celle qu’on vous pose le plus. Je vous dis où elle devrait être
écrite, gratuitement.

NEBULA Agency · Cotonou
nebula-agency.online
```

**Le premier commentaire, à poster soi-même :**

> Laquelle on vous pose le plus ? Écrivez-la, je réponds à tout le monde.

### Ce qu’on répond selon la question reçue

| Il répond | Ce qui manque, et ce qu’on lui dit |
|---|---|
| « c’est combien ? » | ses prix ne sont écrits nulle part. Un prix affiché est une gêne en moins entre lui et la vente |
| « c’est disponible ? » | son stock n’est visible nulle part, il paie chaque rupture deux fois |
| « tu livres ? » | ses conditions ne sont écrites nulle part, et le client hésite au dernier mètre |
| « c’est où ? » | il est introuvable : ce n’est plus un trou, c’est une porte fermée |

⚠️ **Aucun devis dans cette réponse.** On dit **où** l’information devrait être écrite, pas
combien ça coûte de l’écrire. Et **on entre par le Catalogue**
(`_documents/nebula-agency/vente/00-SOCLE-COMMERCIAL.md`).

### Contrôles propres à ce post

| Contrôle | Pourquoi |
|---|---|
| **Aucune pastille avec un chiffre de clients** | la référence en a une, la recopier serait un mensonge démontable |
| **Chaque pointillé atteint SA ligne** | si les trois traits se croisent ou se rejoignent, la démonstration disparaît |
| **Aucun montant sur l’écran du téléphone** | la ligne « prix » existe, le chiffre non |
| Trois valeurs seulement : blanc, noir, bleu | une quatrième couleur et la direction s’effondre |
| Le fond est un blanc plat, sans grain | c’est ce qui l’oppose aux deux autres directions |
| Le logo n’a aucune plaque derrière lui | sur du blanc pur, une plaque se voit immédiatement |
| Réduire à 20 % | si « questions. » ne se lit plus, le post est mort dans le fil |

---

*NEBULA Agency · Cotonou, Bénin · Document vivant. Ajouter chaque nouveau post ici.*

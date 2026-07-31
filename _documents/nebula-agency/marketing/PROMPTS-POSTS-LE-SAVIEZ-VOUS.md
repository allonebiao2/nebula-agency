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
              "à cause de l'heure."
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
              "de l'étranger."
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

## 4. Le rythme de publication

**Deux publications par semaine, mardi et vendredi.** Huit posts tiennent un mois complet.

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

*NEBULA Agency · Cotonou, Bénin · Document vivant. Ajouter chaque nouveau post ici.*

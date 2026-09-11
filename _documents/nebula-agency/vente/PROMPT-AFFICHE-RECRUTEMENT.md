# AFFICHE DE RECRUTEMENT · le prompt
## Vague 1 · Cotonou · **recrutement ouvert, sans quota**

> Complète le §3 de `01-AVIS-DE-RECRUTEMENT.md`, qui contenait le **texte** de l'affiche.
> Ici : le prompt pour la **fabriquer en image**, et le QR code réel.
>
> Créé le 2026-08-01.

---

## Avant de générer · deux choses à savoir

### 1. Recrutement ouvert · ce qui filtre désormais

**Décision de Mongazi, 2026-08-01 : plus de quota de 8 places. On veut un maximum de
partenaires.** L'affiche, l'annonce et le socle sont alignés dessus.

Deux conséquences à garder en tête :

1. **L'entretien devient le seul filtre**, et il reste obligatoire. L'annonce le dit
   franchement : tout le monde peut postuler, tout le monde n'est pas retenu.
2. **Le vrai plafond n'est plus le nombre de vendeurs, c'est la capacité à livrer.**
   NEBULA promet 5 à 7 jours. Le jour où ce délai glisse, c'est le signal qu'il faut
   ralentir le recrutement, pas attendre les réclamations.

Ce qui donne envie n'a jamais été la rareté : ce sont **les chiffres réels** (15 000 à
120 000 F par vente, 200 000 F sur un bon mois) et **les trois barrières qu'on enlève**
(aucun diplôme, rien à payer, aucune compétence technique). Au Bénin, la plupart des
annonces disent « gains attractifs », ça ne veut rien dire et ça sent l'arnaque. Nous,
on écrit les montants.

**Le motif de l'affiche suit :** la rangée de portails déborde du cadre et s'estompe aux
deux extrémités. Elle ne se compte pas, elle continue.

### 2. ⚠️ Le QR code ne se génère PAS par IA

Un QR code dessiné par un modèle d'image **ne scanne pas**. C'est de la décoration qui
ressemble à un QR. Imprimé à 200 exemplaires, ça vous coûte l'impression entière.

Le vrai QR est déjà généré, testé et vérifié en le relisant :

```
_documents/nebula-agency/vente/assets/QR-devenir-partenaire.png
→ https://partenaires.nebula-agency.online/devenir
correction d'erreur haute · 980 × 980 px · vérifié par décodage
```

Le prompt réserve donc **un carré blanc vide** à l'emplacement du QR.
Vous y collez ce fichier après génération. C'est la seule étape manuelle.

---

## La palette NEBULA (valeurs réelles du site)

| | |
|---|---|
| Fond | `#060713` |
| Bleu | `#4F6FFF` |
| Cyan | `#22D3EE` |
| Or | `#E8C88A` |
| Violet | `#9333EA` |
| Texte | `#EEF0FB` |

---

## Le prompt · affiche A4 portrait (impression + partage)

```
You are given ONE reference image.

IMAGE 1 = THE NEBULA AGENCY LOGO.
          Place it EXACTLY as given, pixel-faithful, correct proportions,
          untouched colours. Treat it as a pasted asset, never as something
          to redraw, restyle or reinterpret. Top centre, at roughly 16% of
          the poster width, with generous space beneath it.

------------------------------------------------------------------
FORMAT
------------------------------------------------------------------
Vertical poster, A4 proportions (1:1.414), portrait. Highest resolution
available. Designed to be readable BOTH printed on paper at arm's length
AND as a thumbnail on a phone.

------------------------------------------------------------------
ART DIRECTION
------------------------------------------------------------------
Deep space. Background #060713, never pure black. A wide nebula cloud
sweeps diagonally from the lower left to the upper right in cyan #22D3EE,
blue #4F6FFF and violet #9333EA, with a warm gold #E8C88A glow near the
centre. Fine scattered stars, denser inside the cloud. Subtle film grain
over the whole poster. Premium, cinematic, calm, a serious company, not
a flyer. No clip art, no stock-photo people, no money emoji, no banknote
imagery, no cartoon, no confetti.

CENTRAL MOTIF, "the open row":
A horizontal row of MANY hexagonal portals, thin luminous outlines in
cyan, evenly spaced across the middle of the poster, each empty and open.
The row runs the full width and FADES OUT at both ends, it must read as
uncountable and continuing beyond the frame, never as a fixed number of
seats. All portals are identical and none is marked as taken. A thin
luminous line runs through them, itself fading at both ends. One soft
beam of light rises from the row toward the headline above.

------------------------------------------------------------------
TYPOGRAPHY, render ONLY these strings, nothing else
------------------------------------------------------------------
Font family throughout: a confident geometric sans-serif, tight tracking
on the large sizes, wide letter-spacing on the small uppercase labels.

1. EYEBROW, small, uppercase, wide letter-spacing, cyan:
      "COTONOU · RECRUTEMENT OUVERT"

2. HEADLINE, uppercase, three lines. The first two in pure white
   #EEF0FB, the third smaller and in gold #E8C88A with wide tracking:
      "NOUS RECRUTONS"
      "DES CONSEILLERS"          <- the largest line of the poster
      "EN DIGITALISATION"        <- smaller, gold, letterspaced
   No number appears in the headline. There is no quota.

3. SUBHEAD, one line, light grey-white, sentence case:
      "Vous savez parler aux commerçants ?"
      "Nous, on sait les digitaliser."

4. THE NUMBERS BLOCK, the most important zone after the headline.
   Set inside a thin-bordered rectangle with a faint dark glass fill.
   Three lines, the middle figure by far the largest, in gold #E8C88A:

      "30 % à 40 % par vente"
      "15 000 F à 120 000 F"
      "150 000 F sur un bon mois"

   Small caption beneath, grey, smaller:
      "Et 20 % de chaque abonnement, à vie."

5. THE THREE BARRIERS, one line, three items separated by thin vertical
   rules, uppercase, letterspaced, white:
      "AUCUN DIPLÔME"   "RIEN À PAYER"   "AUCUNE COMPÉTENCE TECHNIQUE"

6. FOOT ZONE, bottom of the poster:
   A CLEAN EMPTY WHITE SQUARE, roughly 22% of the poster width, placed
   bottom centre, with a generous white margin around it. Leave it
   COMPLETELY BLANK, no pattern, no code, no icon, no placeholder mark.
   It is a reserved area.

   To its right, two short lines, white, small:
      "Scannez pour postuler"
      "5 minutes suffisent · aucun quota"

   Bottom line of the poster, very small, letterspaced, grey:
      "WhatsApp +229 96 74 07 32 · www.nebula-agency.online"

------------------------------------------------------------------
RULES
------------------------------------------------------------------
- Render ONLY the quoted strings above. Any additional word is a failure.
- DO NOT draw a QR code. The white square must stay empty, a real QR
  code will be composited into it afterwards. A generated QR code does
  not scan and would ruin the entire print run.
- Render French text with correct diacritics and apostrophes: the accent
  on "commerçants", "DIPLÔME", "À PAYER", "COMPÉTENCE".
- Currency written exactly as given, with the space: "15 000 F".
- The percentage sign is separated by a space: "30 %".
- No stock photography, no human faces, no handshake, no briefcase, no
  arrow-going-up chart, no dollar sign. The nebula and the row of portals
  are the only imagery.
- NEVER render a number of places, a countdown, a "plus que X places" or
  any scarcity claim. Recruitment is open and the poster must say so.
- Text must never sit on the brightest part of the nebula. Keep the areas
  under the headline and under the numbers block dark enough for contrast.
- The headline and the figure "150 000 F" must remain legible when the
  poster is reduced to 20% of its size.
```

---

## Les variantes · même prompt, blocs à remplacer

### Statut WhatsApp et stories · 9:16

Remplacer le bloc `FORMAT` par :

```
------------------------------------------------------------------
FORMAT
------------------------------------------------------------------
Vertical, 9:16. The headline sits in the UPPER-MIDDLE third, never in
the top 12% nor the bottom 18%, which interface elements cover on a
phone. The row of portals is tighter but still fades at both ends. The
numbers block sits
directly beneath the headline. Drop the reserved white square entirely
and replace the foot zone by a single line, white, centred:
      "Écrivez « PARTENAIRE » au +229 96 74 07 32"
```

*Sur un statut, on ne scanne pas : on écrit. Le QR n'a de sens qu'imprimé.*

### Publication carrée · 1:1 (Facebook, LinkedIn)

Remplacer le bloc `FORMAT` par :

```
------------------------------------------------------------------
FORMAT
------------------------------------------------------------------
Square, 1:1. Two zones: the headline and the fading row of portals in the upper
half, the numbers block in the lower half. Drop the three barriers line
and the reserved white square. Foot line only:
      "Candidatures : www.nebula-agency.online"
```

---

## Le montage final de l'affiche A4 (2 minutes)

1. Générer l'image A4 avec le prompt ci-dessus
2. Ouvrir dans n'importe quel éditeur (Canva, Photoshop, même Word)
3. **Coller `assets/QR-devenir-partenaire.png` dans le carré blanc réservé**
4. **Scanner le QR avec votre propre téléphone** avant d'imprimer quoi que ce soit
5. Exporter en PDF, 300 dpi, A4

---

## Contrôles avant impression

| # | Ce qu'on vérifie | Pourquoi |
|---|---|---|
| 1 | **Le QR scanne, testé sur un vrai téléphone** | Un QR mort, c'est l'impression entière perdue |
| 2 | Réduire l'affiche à 20 %, « DES CONSEILLERS » et « 150 000 F » se lisent-ils ? | Elle sera vue de loin, ou en vignette |
| 3 | Les accents : `commerçants`, `DIPLÔME`, `À PAYER`, `COMPÉTENCE` | Une faute sur une affiche imprimée est définitive |
| 4 | Les montants sont-ils **exacts** : 30-40 %, 15 000 à 120 000, 200 000 | Un chiffre faux sur une affiche = une promesse qu'on devra tenir |
| 5 | Le numéro WhatsApp est-il le bon, et **répond-il** ? | Envoyer un vrai message dessus avant d'imprimer |
| 6 | Le logo est-il **intact**, pas redessiné, pas recoloré ? | Le modèle a tendance à « améliorer » les logos |
| 7 | Aucun mot ajouté par le modèle ? | Un slogan inventé peut engager l'agence |

---

## Où l'afficher

Cybercafés · écoles de commerce et centres de formation · agences de transfert d'argent ·
salles de sport · églises et paroisses · boutiques de téléphonie · campus.

*(Repris du §3 de `01-AVIS-DE-RECRUTEMENT.md`.)*

---

## Variante « RUBAN » · affiche sociale 4:5 et 9:16 (2026-09-01)

Référence : `../marketing/references/REF-bande-rouge.jpg` (affiche « WE'RE HIRING », panneau
rouge à coins arrondis sur fond clair pointillé, rubans diagonaux qui répètent « HIRING »,
titre condensé énorme qui se fond dans le panneau, carte blanche des postes, jumelles
détourées en noir et blanc, contact entre crochets en bas).

**Ce n'est pas l'affiche A4 d'impression du § précédent.** Celle-ci est faite pour le fil et
le statut : un seul regard, un seul chiffre, un seul geste.

### Le renversement qui rend cette affiche meilleure que la référence

La référence exige **« EXP-2-5 YEARS »**, en gras, juste sous la carte des postes. C'est la
barrière, et c'est ce qui fait refermer l'image à quatre-vingt-dix pour cent des gens qui la
voient.

**On garde exactement cette place, cette taille et ce gras, et on écrit le contraire :**

> **« AUCUNE EXPÉRIENCE EXIGÉE »**

Même emplacement, même poids, sens inverse. C'est la seule ligne de l'affiche qui fait dire
« alors ça me concerne » à quelqu'un qui allait passer. Tout le reste du marketing découle
de là.

### Le chiffre en énorme, et pourquoi c'est la doctrine de la maison

`01-AVIS-DE-RECRUTEMENT.md` est formel : *« La plupart des annonces de commission au Bénin
disent gains attractifs. Ça ne veut rien dire et ça sent l'arnaque. Nous, on écrit les
montants. »* Donc le mot énorme de la référence (*HIRING*) devient **un montant vrai** :

> **ON RECRUTE** · **45 000 F** · *sur une seule vente*

**45 000 F, c'est 30 % d'une Vitrine à 150 000 F**, au palier par défaut, sans condition.
C'est le chiffre le plus frappant qui soit à la fois vrai et vérifiable en une phrase. Un
vendeur le lit, il calcule tout seul, et c'est exactement ce qu'on veut.

⚠️ **Le montant seul ressemblerait à une arnaque.** C'est la carte blanche juste dessous qui
l'immunise, en disant dans la même seconde ce que c'est : *partenaire commissionné, rien à
payer pour entrer.* Les deux blocs ne se séparent jamais.

### Ce qui n'est PAS sur l'affiche, et pourquoi

⛔ **Aucune place comptée, aucun compte à rebours.** Le quota de 8 places a été retiré le
2026-08-01 et l'affiche dit **« Aucun quota de places »**, ce qui est à la fois vrai et
contre-intuitif : toutes les annonces du marché fabriquent de la rareté. Ne pas en faire est
le signal de sérieux le moins cher qui existe.

⛔ **Aucun chiffre inventé.** Les seuls nombres autorisés sur l'image sont ceux qui sont
écrits dans `01-AVIS-DE-RECRUTEMENT.md` : 45 000 F, 30 %, 40 %, 3 ventes, et le numéro.

**L'urgence est réelle et elle tient en une ligne de la carte :** *« Vous vendez dès le
premier jour. »* C'est la phrase de l'annonce (« Vous pouvez vendre le jour même ») et c'est
ce qui transforme l'envie en geste.

### LE PROMPT

```
===========================================================
NEBULA AGENCY — RECRUITMENT POSTER — ONE IMAGE, 4:5
"ON RECRUTE" — ribbon direction
===========================================================

ATTACHED INPUTS — TWO attachments, IN THIS ORDER:
  1st = THE STYLE REFERENCE
  2nd = THE NEBULA LOGO
Never swap their roles: swapping them ruins the image. If the order
is ever unclear, fall back on their content, described below.

  THE STYLE REFERENCE (first attachment) = a bold recruitment poster
     on a light dotted background, with a large rounded-corner
     ORANGE-RED panel, diagonal ribbons in the top-left and
     bottom-right corners repeating the word "HIRING", an enormous
     condensed white headline whose lower word FADES OUT into the
     panel, a small script line on a highlight bar overlapping the
     headline, a WHITE ROUNDED CARD holding the job details in dark
     type, one bold line under that card, a BLACK AND WHITE CUT-OUT
     of two hands holding binoculars, and a contact line inside a
     thin bracket frame at the bottom.
     REPRODUCE ITS LAYOUT SYSTEM COMPLETELY AND FAITHFULLY:
       - the light, very subtly dotted off-white background
       - the large ROUNDED-CORNER COLOUR PANEL covering most of the
         canvas
       - the DIAGONAL RIBBONS crossing the top-left and bottom-right
         corners, over everything, with a short phrase repeated
         along them
       - the ENORMOUS CONDENSED HEAVY SANS-SERIF headline in white,
         with the biggest element FADING SMOOTHLY to transparent at
         its lower edge
       - the small SCRIPT / HANDWRITTEN line sitting on a solid
         highlight bar, overlapping the headline
       - the WHITE ROUNDED CARD with dark centred type
       - one BOLD line directly under the card
       - the BLACK AND WHITE CUT-OUT of two hands holding an object,
         large, at the bottom centre
       - the CONTACT LINE inside a thin open bracket frame
       - its exact level of polish and finish
     Take NOTHING of its words and NOTHING of its colours. The words
     "HIRING", "WE'RE", "Join our team", "Technical Faculty",
     "Data Analyst", "Digital Marketing", "Data Science", "Job Type",
     "EXP-2-5 YEARS", "Submit your resume" and the number
     "+91 93518 43610" appear NOWHERE.

  THE LOGO (second attachment) = the NEBULA Agency logo: a purple
     and blue cosmic swirl above the wordmark "NEBULA", with
     "AGENCY" underneath, on a transparent background.
     It is an ASSET TO PLACE, exactly as provided. It is never a
     style reference and never a subject to reinterpret.

-----------------------------------------------------------
TASK
-----------------------------------------------------------
Create ONE original recruitment poster for NEBULA Agency, a digital
studio in Cotonou, Benin. It recruits commission-based sales
partners, not salaried staff.
It must make a capable person want to start the same week: one
number they can check, one barrier removed, one message to send.
Bold, confident, premium. Never cheap, never clip-art.

-----------------------------------------------------------
THE COLOURS — these replace the red of the reference
-----------------------------------------------------------
  - BACKGROUND: light warm off-white, with the same very subtle
    dotted texture as the reference
  - THE BIG PANEL: deep saturated NEBULA VIOLET #9333EA, rounded
    corners, matte and flat, exactly the shape and proportion of the
    red panel in the reference
  - THE DIAGONAL RIBBONS: bright NEBULA CYAN #22D3EE, with their
    repeated text in near-black #060713
  - THE HIGHLIGHT BAR under the script line: the same cyan #22D3EE,
    with its text in near-black #060713
  - ALL HEADLINE TYPE: pure white
  - THE CARD: white, with near-black #060713 type
Keep the panel absolutely flat: no gradient, no glow, no pattern,
apart from the intentional fade of the headline into it.

-----------------------------------------------------------
THE CUT-OUT — same device, different meaning
-----------------------------------------------------------
At the bottom centre, large, a BLACK AND WHITE CUT-OUT PHOTOGRAPH of
TWO HANDS HOLDING A PAIR OF BINOCULARS raised toward the viewer,
exactly the position, scale and cut-out treatment of the reference.
The hands have dark brown skin, plain, no watch, no ring, no
bracelet, no sleeve logo. No face, no head, no body: hands and
forearms only, entering from the bottom edge.
ONE difference from a plain black and white photograph: THE TWO
LENSES GLOW, one NEBULA VIOLET #9333EA and one NEBULA CYAN #22D3EE,
soft and clean. They are the ONLY colour in the cut-out, and they
must read as "what we are looking for is you".

-----------------------------------------------------------
LOGO INTEGRATION — read twice, most attempts fail here
-----------------------------------------------------------
The logo attachment is a PNG with a TRANSPARENT background.
Leave a clean band of the LIGHT OFF-WHITE BACKGROUND at the very top
of the canvas, above the violet panel, and place the logo there,
centred, small, exactly as provided, keeping that transparency.
  - it sits DIRECTLY on the light background, where its purple and
    blue read clearly. NEVER place it on the violet panel: it would
    disappear into it.
  - NO white box, NO black box, NO coloured plate, NO rounded card,
    NO badge, NO outline, NO glow, NO drop shadow behind it.
  - no ribbon may cross the logo.
  - do NOT redraw it, restyle it, recolour it, stretch it, crop it,
    rotate it, or add a wordmark or tagline of your own.
  - size it so its wordmark stays comfortably readable when the
    whole image is viewed at 20% of its size.
A logo pasted on a plate is a failed image.

-----------------------------------------------------------
FORMAT
-----------------------------------------------------------
Canvas: 1080 x 1350 px, vertical 4:5, for an Instagram and Facebook
feed. This is the reference's own proportion: follow its composition
closely.

-----------------------------------------------------------
CONTENT — render these strings verbatim, nothing else
-----------------------------------------------------------
ON THE TWO DIAGONAL RIBBONS, repeated along their length in dark
capitals, separated by thin vertical bars exactly as in the
reference:
    "ON RECRUTE"

HEADLINE, part 1 — white condensed capitals, upper area of the
panel, clearly smaller than part 2:
    "ON RECRUTE"

HEADLINE, part 2 — ENORMOUS white condensed type, the single
loudest element of the image, fading smoothly to transparent at its
lower edge exactly like the big word in the reference:
    "45 000 F"

THE SCRIPT LINE — small, in a rounded handwritten style, on a solid
cyan highlight bar overlapping the lower edge of the big number,
exactly the device used in the reference:
    "sur une seule vente"

THE WHITE CARD — centred dark type, three lines, the first one
bolder and slightly larger, exactly like the card in the reference:
    "Conseiller en digitalisation · Cotonou"
    "30 % par vente · 40 % dès 3 ventes dans le mois"
    "Rien à payer pour entrer · Vous vendez dès le premier jour"

THE BOLD LINE UNDER THE CARD — white, bold capitals, in the exact
place the reference puts its experience requirement:
    "AUCUNE EXPÉRIENCE EXIGÉE"

THE CONTACT, at the bottom, inside a thin open bracket frame like
the reference, two lines, centred:
    "Écrivez PARTENAIRE sur WhatsApp"
    "+229 96 74 07 32"

ONE SMALL LINE under the bracket frame, discreet:
    "Aucun quota de places"

-----------------------------------------------------------
LAYOUT
-----------------------------------------------------------
Top to bottom:
  1. light background band with the NEBULA logo, centred
  2. the violet panel begins
  3. "ON RECRUTE"
  4. "45 000 F", fading into the panel      <- loudest zone
  5. the cyan bar with "sur une seule vente"
  6. the white card, three lines
  7. "AUCUNE EXPÉRIENCE EXIGÉE"
  8. the hands and the binoculars           <- second largest zone
  9. the bracketed contact, then the small line
The two cyan ribbons cross the TOP-LEFT and BOTTOM-RIGHT corners
diagonally, over the panel and over the background, never over the
logo, never over the white card, and never over the contact lines.

-----------------------------------------------------------
TEXT RENDERING — read twice
-----------------------------------------------------------
- Render ONLY the strings quoted above. Any extra word is a failure.
- Reproduce them VERBATIM: no translation, no rephrasing, no
  shortening, no added punctuation, no exclamation marks.
- THERE IS NO APOSTROPHE ANYWHERE IN THIS IMAGE. If an apostrophe
  appears, a word has been invented and the image is wrong.
- Keep the accents ON THE CAPITAL LETTERS, as French requires:
  "AUCUNE EXPÉRIENCE EXIGÉE". Never "EXPERIENCE", never "EXIGEE".
- Correct diacritics elsewhere: "dès".
- Amounts are written the French way, with a space as the thousands
  separator and a space before the currency letter:
  "45 000 F", never "45000F", never "45,000 F", never "45.000".
- Keep the space before the percent sign: "30 %", "40 %".
- The separator between the card items is a MIDDLE DOT · It is not a
  hyphen, not a dash, not a slash.
- The phone number is written exactly "+229 96 74 07 32", with those
  spaces and no other separator.
- "PARTENAIRE" stays in capitals, exactly as written. Do not turn it
  into a button, a pill or a badge: it is plain text.
- "45 000 F" must still be readable when the image is viewed at 20%
  of its size, and it must be the first thing the eye reads.
- No hashtag, no emoji, no icon, no arrow, no star, no rating, no
  verified tick, no QR code.

-----------------------------------------------------------
HARD CONSTRAINTS
-----------------------------------------------------------
- The ONLY figures anywhere in the image are those in the strings
  above: "45 000 F", "30 %", "40 %", "3", and the phone number.
  NO invented statistics, NO client counts, NO follower counts, NO
  number of places, NO deadline, NO countdown, NO percentage of
  success, NO salary.
- NO scarcity of any kind: no "limited places", no "last chance",
  no timer. The poster states the opposite, and it is true.
- NO visible human face and no recognisable person: hands and
  forearms only.
- NO recognisable third-party brand, logo, app or interface.
- NO watermark, no frame, no border around the image itself.
- The violet panel stays FLAT and uncluttered: no photograph on it
  other than the cut-out, no second object, no pattern.
- The white card and the big number are never separated: the number
  promises, the card explains what it is.
- One offer, told once.

-----------------------------------------------------------
OUTPUT
-----------------------------------------------------------
One finished 1080 x 1350 image, publication-ready, high-fidelity
text rendering, print-clean edges.
===========================================================
```

### Pour le statut WhatsApp (9:16)

```
-----------------------------------------------------------
FORMAT AND SAFE ZONES
-----------------------------------------------------------
Canvas: 1080 x 1920 px, vertical 9:16.
WhatsApp draws its own interface ON TOP of the image:
  - the TOP 220 px are covered (profile picture, name, time)
  - the BOTTOM 340 px are covered (the "Reply" field)
The logo, every line of type, the white card, the hands and the
bracketed contact must ALL sit between y = 220 px and y = 1580 px.
The extra height goes into the violet panel around the big number,
not into extra content.

REPLACE ONE LINE: instead of "Écrivez PARTENAIRE sur WhatsApp",
render:
    "Répondez PARTENAIRE à ce statut"
The phone number stays underneath, unchanged.
```

### La légende, à publier avec l'affiche

```
45 000 F. C'est ce que touche un partenaire NEBULA sur UNE vitrine vendue.
Pas un bonus, pas une prime : sa commission, 30 % du prix.

Ce que nous cherchons tient en une phrase : quelqu'un qui sait parler à un
commerçant. Pas un diplôme, pas un CV, pas une expérience en vente. Nous
formons, et vous vendez dès le premier jour.

Ce que vous vendez existe déjà et tourne : neuf commerces de Cotonou et de
Porto-Novo sont en ligne aujourd'hui grâce à nous. Ouvrez djambarteam.com ou
graindesthetique.com sur votre téléphone, maintenant, avant même de postuler.
Nous vous demandons de le faire.

Ce que ce n'est pas : un salaire. Il faut sortir, marcher, parler, essuyer des
refus. Les bons partenaires voient 5 à 10 commerçants par jour.

Il n'y a rien à payer pour entrer, et aucun quota de places. Il y a un
entretien, et il est obligatoire.

Écrivez PARTENAIRE et votre prénom au +229 96 74 07 32.
Ou déposez votre candidature : partenaires.nebula-agency.online/devenir
```

⚠️ **Les neuf clients livrés sont nommés exprès.** Une annonce de recrutement qui ne montre
rien à ouvrir se lit comme une arnaque ; celle-ci demande au candidat d'aller vérifier avant
de postuler. C'est le seul argument qu'aucun concurrent local ne peut copier ce soir.

### Contrôles propres à cette affiche

| Contrôle | Pourquoi |
|---|---|
| **Le logo est sur le fond clair, jamais sur le violet** | violet sur violet, il disparaît |
| **La carte blanche touche le gros chiffre** | le montant seul ressemble à une arnaque, la carte l'immunise |
| **Aucune place comptée, aucune date limite** | il n'y a plus de quota depuis le 2026-08-01, et l'affiche le dit |
| Les seuls nombres sont 45 000 F, 30 %, 40 %, 3 et le numéro | tout autre chiffre serait inventé |
| Accents gardés sur les capitales | « EXPERIENCE » sans accent et toute l'affiche a l'air bâclée |
| Espaces des montants à la française | « 45000F » se lit indien, pas béninois |
| Aucune apostrophe sur l'image | il n'y en a pas une seule ; s'il en apparaît une, un mot a été inventé |
| Aucun ruban ne traverse le logo ni la carte | ce sont les deux zones qui doivent rester lisibles |
| **Réduire à 20 %** | si « 45 000 F » ne se lit plus, l'affiche est morte dans le fil |
| **Le numéro reçoit vraiment** | inchangé depuis le § précédent : à confirmer une fois |

---

## Ce qui reste à décider avant de diffuser

- [ ] **La date limite de candidature**, elle n'est pas encore fixée. L'affiche marche sans,
      mais une date fait bouger les gens. À insérer dans l'eyebrow :
      `"COTONOU · CANDIDATURES JUSQU'AU [date]"`
- [ ] **Vérifier que `/devenir` est accessible** et que le formulaire notifie bien l'admin
      sinon les candidatures tombent dans le vide
- [ ] Confirmer que le **+229 96 74 07 32** est bien le numéro de réception des candidatures
- [ ] ⛔ **`01-AVIS-DE-RECRUTEMENT.md` se contredit sur son chiffre phare.** La note de
      méthode annonce **200 000 F sur un mois à 6 ventes**, le tableau juste en dessous écrit
      **150 000 F** pour les mêmes 6 ventes. Le tableau calcule à 30 %, or 6 ventes font
      passer tout le mois au palier ARGENT (40 %), donc **c'est 200 000 F et le tableau est
      faux**. À trancher et à corriger dans les deux endroits : un candidat qui recalcule
      trouvera l'écart, et c'est exactement le genre de détail qui coûte la confiance.
      *(L'affiche « RUBAN » n'utilise ni l'un ni l'autre : elle s'en tient à 45 000 F sur une
      vente, qui n'est ambigu nulle part.)*

---

*NEBULA Agency · Cotonou, Bénin · Adossé à `00-SOCLE-COMMERCIAL.md` et `01-AVIS-DE-RECRUTEMENT.md`.*

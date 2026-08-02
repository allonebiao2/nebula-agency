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

## Ce qui reste à décider avant de diffuser

- [ ] **La date limite de candidature**, elle n'est pas encore fixée. L'affiche marche sans,
      mais une date fait bouger les gens. À insérer dans l'eyebrow :
      `"COTONOU · CANDIDATURES JUSQU'AU [date]"`
- [ ] **Vérifier que `/devenir` est accessible** et que le formulaire notifie bien l'admin
      sinon les candidatures tombent dans le vide
- [ ] Confirmer que le **+229 96 74 07 32** est bien le numéro de réception des candidatures

---

*NEBULA Agency · Cotonou, Bénin · Adossé à `00-SOCLE-COMMERCIAL.md` et `01-AVIS-DE-RECRUTEMENT.md`.*

---

# VARIANTE « NOUS RECRUTONS » · format réseaux sociaux

> **Ajoutée le 2026-08-02**, d'après trois affiches de référence fournies par Mongazi
> (immeuble/chevrons orange, mégaphone vert et ocre, chaise de bureau sur fond rouge).
>
> Ce n'est **pas** l'affiche A4 imprimée ci-dessus. C'est la version **réseaux sociaux et
> statut WhatsApp** : plus courte, plus frappante, faite pour être vue en trois secondes.

## Ce que les trois références ont en commun, et qu'on reprend

1. **Un mot énorme** qui occupe le tiers haut, lisible en vignette.
2. **UNE seule couleur d'accent** sur un fond sombre ou saturé. Jamais trois.
3. **Un objet héros** détouré, éclairé comme une photo produit (mégaphone, chaise).
4. **Des pastilles flottantes** qui portent les postes ou les avantages.
5. **Un bloc contact compact en bas**, séparé visuellement du reste.
6. **Le logo à un coin**, discret.

**Ce qu'on ne reprend pas :** leur maquette exacte, leurs couleurs, leur objet. On reprend
l'énergie et la structure, pas le dessin.

## ⚠️ Deux règles à ne jamais enfreindre sur cette affiche

- **Aucune rareté inventée.** Pas de « 8 places », pas de « plus que 3 jours ». Le
  recrutement est **sans quota** (décision du 2026-08-01) : écrire le contraire est un
  mensonge que le premier candidat vérifiera. **L'urgence vient de la vitesse, pas de la
  rareté** : entretien sous 72 heures, et on peut vendre le jour même.
- **Aucun chiffre faux.** 30 % à 40 % par vente, 20 % sur l'abonnement à vie, paiement sous
  24 à 72 h. Ce sont les vrais chiffres, ils suffisent.

---

## PROMPT · Nano Banana Pro (Gemini 3 Pro Image)

**Pièces jointes, dans cet ordre :** le **logo NEBULA en premier**, puis les **trois
affiches de référence**. Inversés, le modèle traite le logo comme un modèle de style et la
marque disparaît.

```
Create ONE original recruitment poster for NEBULA Agency.

ATTACHED INPUTS, read these roles carefully:
  IMAGE 1 = THE LOGO of NEBULA Agency (cosmic swirl + wordmark).
            It is AN ASSET TO PLACE, never a style reference, never a
            subject to reinterpret. Place it, do not redraw it.
  IMAGES 2, 3, 4 = STYLE REFERENCES, for ENERGY AND STRUCTURE ONLY.
            Learn from them: one enormous headline word, a single accent
            colour, a hero object lit like a product shot, floating pill
            labels, a compact contact block at the bottom.
            Their colours, their objects, their text and their brands are
            IRRELEVANT and must never appear in the output.

ART DIRECTION:
Deep space brand world, premium and confident. Background #060713, never
pure black. A nebula cloud sweeps diagonally from lower left to upper
right in cyan #22D3EE, blue #4F6FFF and violet #9333EA, with a warm gold
#E8C88A glow near the centre. Fine star field, subtle grain. GOLD #E8C88A
is the single accent colour used for the key figures and the call to
action. Text in near-white #EEF0FB.

HERO OBJECT (right half, lit like a studio product shot, cut out):
A modern smartphone held upright in a dark-skinned hand, seen at a slight
angle. From the screen rises a spiral of light and particles in cyan and
violet, echoing a galaxy, as if the phone were opening a small universe.
The screen itself glows softly and shows no interface, no icons, no text.
Sharp rim light on the hand and the phone edges.

TEXT TO RENDER, verbatim French with correct diacritics and apostrophes.
Render NOTHING else:

  Small kicker, top left, uppercase, letter-spaced, gold:
      "NEBULA AGENCY · COTONOU"

  Headline, upper third, two stacked lines, the second by far the largest:
      "NOUS"                    <- large, near-white
      "RECRUTONS"               <- ENORMOUS, heavy condensed sans, gold
  Subtitle directly under it, medium, near-white:
      "Conseillers en Digitalisation"

  Four floating pill-shaped labels over the left half, rounded, dark
  translucent with a thin gold outline, each one line:
      "30 % à 40 % par vente"
      "20 % de chaque abonnement, à vie"
      "Payé sous 24 à 72 h"
      "Aucun frais d'entrée"

  One short line under the pills, small, cyan, uppercase, letter-spaced:
      "SUR LE TERRAIN, PAS DERRIÈRE UN BUREAU"

  Urgency strip, a thin gold horizontal bar with dark text inside:
      "ENTRETIEN SOUS 72 H · VOUS POUVEZ VENDRE LE JOUR MÊME"

  Contact block at the bottom, visually separated, compact:
      "Écrivez « PARTENAIRE » au +229 96 74 07 32"
      "partenaires.nebula-agency.online/devenir"

  The NEBULA logo sits in the bottom left corner, small and discreet.

LAYOUT: 4:5 vertical, 1080 x 1350 px. Left half carries the text, right
half the hero object. Nothing touches the edges. The word "RECRUTONS"
must stay legible at 20% size.

NO other words, no numbers, no invented statistics, no scarcity claims,
no fake UI, no watermark, no extra logos, no stock-photo people.
```

---

## PROMPT · ChatGPT (GPT Image)

**Même affiche, mais le prompt est raccourci.** GPT Image rend moins bien les blocs de texte
longs et n'accepte que trois formats : carré, portrait `1024 x 1536`, paysage `1536 x 1024`.
**Demandez le portrait.** Attendez-vous à devoir régénérer deux ou trois fois pour obtenir
tout le texte correct, et à corriger les accents.

```
Create a recruitment poster, portrait 1024 x 1536.

I am attaching the NEBULA Agency logo first: PLACE it in the bottom left
corner, small. Do not redraw it, do not use it as a style reference.
The other attached images are style references for ENERGY ONLY: one huge
headline, one accent colour, a hero object, floating pill labels, a
contact block at the bottom. Ignore their colours, objects and text.

Style: deep space. Background #060713. A nebula sweeps diagonally in cyan
#22D3EE, blue #4F6FFF and violet #9333EA. Gold #E8C88A is the ONLY accent
colour. Text near-white #EEF0FB. Premium, confident, high contrast.

Hero object, right half, lit like a product shot: a smartphone held
upright in a dark-skinned hand, a spiral of cyan and violet light rising
from its screen like a small galaxy. No interface on the screen.

Render this French text EXACTLY, with the accents, and nothing else:
  top left, small, gold:      "NEBULA AGENCY · COTONOU"
  headline, two lines:        "NOUS" then "RECRUTONS" (huge, gold)
  subtitle:                   "Conseillers en Digitalisation"
  four pill labels, left side:
                              "30 % à 40 % par vente"
                              "20 % de chaque abonnement, à vie"
                              "Payé sous 24 à 72 h"
                              "Aucun frais d'entrée"
  one cyan line:              "SUR LE TERRAIN, PAS DERRIÈRE UN BUREAU"
  gold bar:                   "ENTRETIEN SOUS 72 H"
  bottom contact block:       "Écrivez « PARTENAIRE » au +229 96 74 07 32"
                              "partenaires.nebula-agency.online/devenir"

No other text. No invented numbers. No fake scarcity. No watermark.
```

---

## Les cinq contrôles avant de publier

| | |
|---|---|
| **Les chiffres** | 30 à 40 %, 20 % à vie, 24 à 72 h. Un chiffre faux sur une affiche est une promesse qu'on devra tenir |
| **Le numéro** | `+229 96 74 07 32`, chiffre par chiffre. C'est l'erreur la plus coûteuse et la plus fréquente |
| **Les accents** | « Payé », « MÊME », « DERRIÈRE », « Écrivez ». Les modèles les perdent |
| **Le logo** | Placé, pas redessiné. S'il est déformé ou réinventé, régénérer |
| **La lisibilité en vignette** | Réduisez l'image à 20 %. Si « RECRUTONS » n'est plus lisible, l'affiche est morte dans un fil |

⚠️ **Et la ligne à ne jamais retirer : « SUR LE TERRAIN, PAS DERRIÈRE UN BUREAU ».**
C'est elle qui évite le candidat qui croit qu'il aura « juste à closer ». Une affiche qui ne
filtre pas fait perdre des entretiens.


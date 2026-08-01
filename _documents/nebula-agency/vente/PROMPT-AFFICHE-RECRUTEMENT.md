# AFFICHE DE RECRUTEMENT — le prompt
## Vague 1 · Cotonou · 8 conseillers en digitalisation

> Complète le §3 de `01-AVIS-DE-RECRUTEMENT.md`, qui contenait le **texte** de l'affiche.
> Ici : le prompt pour la **fabriquer en image**, et le QR code réel.
>
> Créé le 2026-08-01.

---

## Avant de générer — deux choses à savoir

### 1. « Un max de partenaires » et « 8 places » ne se contredisent pas

L'objectif est de **maximiser les candidatures**, pas les places. C'est même l'inverse :
c'est **parce qu'il n'y a que 8 places** que les bons postulent.

> « On prend tout le monde » attire des gens qui ne vendront jamais et qui encombrent le
> back-office. « 8 places, entretien obligatoire » attire les vendeurs qui se croient bons
> et veulent le prouver.
> — `01-AVIS-DE-RECRUTEMENT.md`, note de méthode

L'affiche garde donc **8 places**. Ce qui donne envie, ce n'est pas la porte grande ouverte :
ce sont **les chiffres réels** (12 500 à 75 000 F par vente, 150 000 F sur un bon mois) et
**les trois barrières qu'on enlève** (aucun diplôme, rien à payer, aucune compétence
technique). Au Bénin, la plupart des annonces disent « gains attractifs » — ça ne veut rien
dire et ça sent l'arnaque. Nous, on écrit les montants.

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
          Place it EXACTLY as given — pixel-faithful, correct proportions,
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
over the whole poster. Premium, cinematic, calm — a serious company, not
a flyer. No clip art, no stock-photo people, no money emoji, no banknote
imagery, no cartoon, no confetti.

CENTRAL MOTIF — "the eight places":
A horizontal row of EIGHT identical hexagonal portals, thin luminous
outlines in cyan, evenly spaced across the middle of the poster, each
empty and open. They read as eight seats waiting to be taken. All eight
are identical and equally lit — none is marked as taken. One soft beam
of light rises from the row toward the headline above.

------------------------------------------------------------------
TYPOGRAPHY — render ONLY these strings, nothing else
------------------------------------------------------------------
Font family throughout: a confident geometric sans-serif, tight tracking
on the large sizes, wide letter-spacing on the small uppercase labels.

1. EYEBROW, small, uppercase, wide letter-spacing, cyan:
      "COTONOU · CANDIDATURES OUVERTES"

2. HEADLINE, very large, uppercase, pure white #EEF0FB, two lines:
      "NOUS RECRUTONS"
      "8 CONSEILLERS"
   The figure "8" is the single largest glyph on the poster.

3. SUBHEAD, one line, light grey-white, sentence case:
      "Vous savez parler aux commerçants ?"
      "Nous, on sait les digitaliser."

4. THE NUMBERS BLOCK — the most important zone after the headline.
   Set inside a thin-bordered rectangle with a faint dark glass fill.
   Three lines, the middle figure by far the largest, in gold #E8C88A:

      "25 % à 35 % par vente"
      "12 500 F à 75 000 F"
      "150 000 F sur un bon mois"

   Small caption beneath, grey, smaller:
      "Et 25 % de chaque abonnement, à vie."

5. THE THREE BARRIERS — one line, three items separated by thin vertical
   rules, uppercase, letterspaced, white:
      "AUCUN DIPLÔME"   "RIEN À PAYER"   "AUCUNE COMPÉTENCE TECHNIQUE"

6. FOOT ZONE, bottom of the poster:
   A CLEAN EMPTY WHITE SQUARE, roughly 22% of the poster width, placed
   bottom centre, with a generous white margin around it. Leave it
   COMPLETELY BLANK — no pattern, no code, no icon, no placeholder mark.
   It is a reserved area.

   To its right, two short lines, white, small:
      "Scannez pour postuler"
      "5 minutes suffisent"

   Bottom line of the poster, very small, letterspaced, grey:
      "WhatsApp +229 96 74 07 32 · www.nebula-agency.online"

------------------------------------------------------------------
RULES
------------------------------------------------------------------
- Render ONLY the quoted strings above. Any additional word is a failure.
- DO NOT draw a QR code. The white square must stay empty — a real QR
  code will be composited into it afterwards. A generated QR code does
  not scan and would ruin the entire print run.
- Render French text with correct diacritics and apostrophes: the accent
  on "commerçants", "DIPLÔME", "À PAYER", "COMPÉTENCE".
- Currency written exactly as given, with the space: "12 500 F".
- The percentage sign is separated by a space: "25 %".
- No stock photography, no human faces, no handshake, no briefcase, no
  arrow-going-up chart, no dollar sign. The nebula and the eight portals
  are the only imagery.
- Text must never sit on the brightest part of the nebula. Keep the areas
  under the headline and under the numbers block dark enough for contrast.
- The headline and the figure "150 000 F" must remain legible when the
  poster is reduced to 20% of its size.
```

---

## Les variantes · même prompt, blocs à remplacer

### Statut WhatsApp et stories — 9:16

Remplacer le bloc `FORMAT` par :

```
------------------------------------------------------------------
FORMAT
------------------------------------------------------------------
Vertical, 9:16. The headline sits in the UPPER-MIDDLE third — never in
the top 12% nor the bottom 18%, which interface elements cover on a
phone. The eight portals form a tighter row. The numbers block sits
directly beneath the headline. Drop the reserved white square entirely
and replace the foot zone by a single line, white, centred:
      "Écrivez « PARTENAIRE » au +229 96 74 07 32"
```

*Sur un statut, on ne scanne pas : on écrit. Le QR n'a de sens qu'imprimé.*

### Publication carrée — 1:1 (Facebook, LinkedIn)

Remplacer le bloc `FORMAT` par :

```
------------------------------------------------------------------
FORMAT
------------------------------------------------------------------
Square, 1:1. Two zones: the headline and the eight portals in the upper
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
| 2 | Réduire l'affiche à 20 % — « 8 CONSEILLERS » et « 150 000 F » se lisent-ils ? | Elle sera vue de loin, ou en vignette |
| 3 | Les accents : `commerçants`, `DIPLÔME`, `À PAYER`, `COMPÉTENCE` | Une faute sur une affiche imprimée est définitive |
| 4 | Les montants sont-ils **exacts** : 25-35 %, 12 500 à 75 000, 150 000 | Un chiffre faux sur une affiche = une promesse qu'on devra tenir |
| 5 | Le numéro WhatsApp est-il le bon, et **répond-il** ? | Envoyer un vrai message dessus avant d'imprimer |
| 6 | Le logo est-il **intact** — pas redessiné, pas recoloré ? | Le modèle a tendance à « améliorer » les logos |
| 7 | Aucun mot ajouté par le modèle ? | Un slogan inventé peut engager l'agence |

---

## Où l'afficher

Cybercafés · écoles de commerce et centres de formation · agences de transfert d'argent ·
salles de sport · églises et paroisses · boutiques de téléphonie · campus.

*(Repris du §3 de `01-AVIS-DE-RECRUTEMENT.md`.)*

---

## Ce qui reste à décider avant de diffuser

- [ ] **La date limite de candidature** — elle n'est pas encore fixée. L'affiche marche sans,
      mais une date fait bouger les gens. À insérer dans l'eyebrow :
      `"COTONOU · CANDIDATURES JUSQU'AU [date]"`
- [ ] **Vérifier que `/devenir` est accessible** et que le formulaire notifie bien l'admin —
      sinon les candidatures tombent dans le vide
- [ ] Confirmer que le **+229 96 74 07 32** est bien le numéro de réception des candidatures

---

*NEBULA Agency · Cotonou, Bénin · Adossé à `00-SOCLE-COMMERCIAL.md` et `01-AVIS-DE-RECRUTEMENT.md`.*

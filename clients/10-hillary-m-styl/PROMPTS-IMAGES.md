# HILLARY M. STYL — les 3 images d'ambiance

> **Outil de génération : Nano Banana Pro.** Les prompts sont en anglais — les modèles
> d'image suivent mieux les consignes de cadrage en anglais.
> Version 1.0 · 2026-08-01

---

## ⛔ CE QUE CES IMAGES NE SONT PAS

**Aucune de ces trois images ne montre un vêtement fini présenté comme une pièce du
catalogue.** C'est la règle absolue du dépôt (`DIRECTION-ARTISTIQUE.md`) et elle n'est pas
bureaucratique : une cliente qui commande une « Robe Amazone » sur la foi d'une photo IA
reçoit autre chose, et c'est **Hillary** qui paie le mensonge, pas nous.

Ce sont des images de **matière et de geste** : du tissu, du fil, de la craie, des mains au
travail. Elles disent « cette maison coud pour de vrai ». Elles ne promettent aucun produit.

Les 12 cartes du catalogue gardent leur mention **« Photo à venir »** jusqu'à ce qu'Hillary
envoie ses vraies pièces photographiées.

---

## LES RÈGLES COMMUNES AUX TROIS

| | |
|---|---|
| **Aucun visage** | Des mains, oui. Un visage crée une égérie qui n'existe pas |
| **Aucun local identifiable** | Pas de vitrine, pas d'enseigne, pas d'atelier reconnaissable : le site ne doit pas laisser croire qu'on montre SON atelier |
| **Aucun texte, logo ou filigrane** | Le texte du site passe par-dessus |
| **Des mains d'Afrique de l'Ouest** | Peau noire. Une main blanche sur une maison de Cotonou se voit immédiatement et trahit l'image |
| **Une seule source de lumière** | Rasante, directionnelle. C'est ça qui fait cher, pas la saturation |
| **Palette** | encre `#0B0A0C` · papier `#F4F1EC` · magenta `#E6007E` en accent minuscule (un fil, un trait de craie) |

---

## IMAGE 1 · LE HÉROS — plein écran, sombre

**Où :** derrière le titre d'accueil, plein cadre.
**Format : 3:2 paysage, 2400 × 1600 px.** (Pas carré : ça ne couvre pas un écran d'accueil.)

**⚠️ La contrainte de composition, vérifiée dans le code :**
`.hero{align-items:flex-end}` et `.in{padding-bottom:84px}` — **le titre est calé EN BAS**,
sur toute la largeur. Et `.croquis{right:8%}` place le croquis de robe animé **à droite**,
au-dessus de 1020 px. Donc :

| Zone | Ce qu'il faut |
|---|---|
| **Tiers bas** | **vide et très sombre** — le titre s'y pose |
| **Droite** | **libre** — le croquis animé y vit, deux robes s'y battraient |
| **Moitié gauche / haut** | c'est là que va le sujet |

> **Leçon du 1er essai.** Le premier brief demandait de garder le *haut* vide : l'image a
> donc concentré tout son intérêt dans le tiers bas, exactement là où le titre le recouvre.
> Il ne serait resté que du noir. **Toujours lire l'alignement réel du héros avant d'écrire
> une contrainte de cadrage.**

**Et le sujet doit dire « couture » en un quart de seconde.** Du tissu sombre et un
mètre-ruban disent « du textile », pas « on fabrique un vêtement ici ». D'où la **toile** :
le prototype en calicot écru, couvert d'épingles et de traits de craie, monté sur buste.
Impossible à confondre avec autre chose que de la couture, **inachevé par définition** donc
sans risque de photo-catalogue, et **clair sur fond sombre** — ce qui règle la luminosité
au lieu de la contourner.

```
A tailor's dress form standing in a dark studio, draped with an unfinished cream calico
toile — a work-in-progress garment mock-up, raw unhemmed edges, visible basting stitches,
dressmaker's pins pushed into the fabric, and blue chalk marking lines drawn across it.
The dress form is placed in the LEFT half of the frame, lit by a single warm directional
light from the left that makes the pale calico glow clearly against the darkness. The right
side of the frame is open, dark and empty. The BOTTOM THIRD of the image falls into deep
ink-black shadow with no detail. A soft measuring tape hangs over the shoulder of the form,
and a single fine magenta thread catches the light. Palette of ink black (#0B0A0C), warm
cream (#F4F1EC) and one small magenta accent (#E6007E). Editorial fashion-atelier
photography, medium format, shallow depth of field, fine film grain. No people, no faces,
no hands, no finished garment, no text, no logo, no watermark. Dark and cinematic, but the
calico must be clearly visible and well lit.
```

**À vérifier sur le résultat :** le bas est-il vide et sombre ? le buste est-il à gauche ?
la toile est-elle **visiblement inachevée** (épingles, bords bruts) ? Si le modèle rend une
belle robe finie, régénérer — on retombe dans la photo-catalogue interdite.

---

## IMAGE 2 · À PROPOS — claire, verticale

**Où :** à côté du texte « Le vêtement vous précède » (au-dessus sur téléphone).
**Format : 4:5 portrait, 1600 × 2000 px.**
**Contrainte :** la section est sur fond **papier clair**. L'image doit être **haute en
lumière**, sinon elle fait un trou noir au milieu d'une page claire et casse le rythme
alterné sombre/clair du site.

```
Overhead flat-lay of a tailor's work table in bright, soft, diffused daylight. Cream pattern
paper (#F4F1EC) with faint chalk lines drawn on it, a flat wooden tailor's ruler, a few
steel pins scattered, a worn nub of tailor's chalk, and a small spool of magenta thread
placed off-centre. Everything sits on a pale linen surface. High-key, airy, lots of empty
space in the upper half of the frame. Soft shadows, no harsh contrast. Warm neutral palette
of cream, bone and pale wood, with one single accent of magenta (#E6007E) on the thread
spool. Editorial still-life photography, medium format, natural light, subtle film grain,
no people, no faces, no finished garment, no text, no logo, no watermark.
```

---

## IMAGE 3 · L'ATELIER — bande large, sombre

**Où :** une bande horizontale juste avant les cartes de contact.
**Format : 21:9 panoramique, 2400 × 1030 px.**
**Contrainte :** très large et très basse. Le sujet doit être **centré horizontalement** :
sur téléphone, l'image est recadrée sur son centre, les bords disparaissent.

```
Extreme close-up of a Black West African artisan's hands guiding a length of dark fabric
under the presser foot of an old mechanical sewing machine. Only the hands and the machine
foot are visible, centred in the frame, cropped tight — no face, no body, no room around
them. Single warm tungsten light falling from the upper left, deep ink-black shadows
(#0B0A0C) filling the rest of the wide frame. The needle is caught mid-stitch, a fine
magenta thread (#E6007E) running through the fabric. Dark, warm, cinematic. Editorial
craft photography, shallow depth of field, fine film grain, no faces, no text, no logo,
no watermark. Panoramic composition, subject dead centre.
```

---

## APRÈS LA GÉNÉRATION — ce que je fais des fichiers

1. **Conversion en WebP** et redimensionnement au format exact ci-dessus
2. **Budget de poids** : la vitrine est **un seul fichier autonome** (images en base64,
   règle du dépôt). Elle pèse 177 Ko aujourd'hui. Objectif : **rester sous 700 Ko** au
   total. Trois images à ~100 Ko en WebP font ~410 Ko une fois en base64. Je mesure et
   j'annonce le poids réel — sur une connexion mobile béninoise, chaque centaine de Ko
   se paie en secondes d'attente
3. **Trois nouveaux marqueurs** dans `_vitrine_src.html` + trois entrées dans `_build.py`,
   exactement comme le logo — jamais de fichier image à côté du HTML
4. **Voile de lisibilité** sur le héros et la bande : le texte doit garder son contraste
   AA, image ou pas. C'est contrôlé par `_qc.py`
5. **`_qc.py` doit rester vert** (71 contrôles) et je vérifie qu'aucune image ne crée de
   débordement en 390 px

**Envoyez les images dans l'ordre 1, 2, 3** ou en me disant laquelle est laquelle — le
format ne suffit pas toujours à les distinguer.

---

*NEBULA Agency · Cotonou*

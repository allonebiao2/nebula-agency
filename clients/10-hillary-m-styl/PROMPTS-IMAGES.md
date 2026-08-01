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
**Format : 3:2 paysage, 2400 × 1600 px.**
**Contrainte de composition :** le titre occupe la moitié gauche et le croquis de robe la
droite. **Les deux tiers supérieurs doivent rester très sombres et presque vides** — sinon
le titre devient illisible. Tout l'intérêt se joue dans le tiers bas.

```
Extreme close-up of dark charcoal-black fabric draped across a surface, shot from a low
raking angle. A single warm directional light grazes the weave from the right, revealing
the texture of the threads and the soft folds; the upper two thirds of the frame fall off
into near-black shadow with almost no detail. In the lower third, a tailor's soft measuring
tape lies coiled across the fabric, and a single fine magenta thread traces a loose curve
over it. Deep ink-black palette (#0B0A0C), warm off-white highlights, one small accent of
magenta (#E6007E) on the thread only. Editorial fashion-house photography, medium format,
shallow depth of field, fine film grain, no people, no faces, no garment, no text, no logo,
no watermark. Moody, quiet, expensive.
```

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

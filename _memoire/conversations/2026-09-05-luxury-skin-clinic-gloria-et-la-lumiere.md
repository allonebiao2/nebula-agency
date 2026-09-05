# 2026-09-05 — Luxury Skin Clinic : les quatre demandes de Gloria, puis « LA LUMIÈRE »

> Client 04 · LUXURY CLUB 229 (Ahouangnimon Gloria) · https://luxuryclub229.com
> Deux chantiers dans la même journée : le **contenu** que Gloria a envoyé sur
> WhatsApp, puis l'**élévation** de la vitrine demandée par Mongazi
> (« que ça devienne une vitrine à 100 000 $ »).

---

## 1. Les quatre demandes de Gloria (contenu)

Reçues en capture WhatsApp + texte collé par Mongazi.

| Demande | Ce qui a été fait |
|---|---|
| Supprimer l'option consultation non payante | la **Consultation Peau gratuite** quitte le catalogue, la section « Votre consultation peau, offerte » est supprimée, le bouton du héros devient **« Prendre rendez-vous »** |
| « On reçoit désormais du lundi au samedi, 10h à 17h » | **9 endroits** mis d'accord : bandeau, règlement, ligne sous chaque fiche, aide du calendrier, messages WhatsApp, récapitulatifs, `ALLOWED_WEEKDAYS`, créneaux |
| Nouvelle prestation **SOIN VISAGE CLASSIC — 15 000 F** | fiche complète : description, 8 étapes du protocole, bénéfices, pour qui, résultats, fréquence, esprit du soin — **ses mots** |
| **Diagnostic Capillaire (5 000 F)** → **CONSULTATION CAPILLAIRE PREMIUM (30 000 F)** | remplacé : 30 minutes, présentiel privilégié, distance possible, bilan, routine, **suivi 3 mois** en trois étapes |

### ⚠️ Une liste de demandes n'est pas une liste de textes

**Supprimer la consultation gratuite, c'est supprimer un MOTEUR.** Le
questionnaire de peau (10 sections) était le contenu de cette consultation,
et le questionnaire capillaire était le contenu du diagnostic. Les deux
n'avaient plus aucune porte d'entrée :

- `SKIN_FORM` et `HAIR_FORM` (les deux questionnaires), la modale de
  formulaire, la modale « Conditions du diagnostic », le moteur multi-étapes
  et `payViaWa` sont **retirés** — sinon un `document.getElementById('openSkinForm')`
  sur un élément disparu **cassait tout le JavaScript de la page**.
- Ils sont **récupérables dans git** (état du 2026-09-04) le jour où Gloria
  voudrait revenir à un questionnaire.
- Gain au passage : **−30 Ko** sur une page de 205 Ko.

### ⚠️ Un changement de jours change la forme du calendrier

Mercredi + samedi sur 8 semaines = 16 boutons. **Du lundi au samedi = 48.**
Le calendrier n'en montre donc que **12**, puis « + N autres dates ».
Et le créneau de **9h a été déplacé à 10h** : il tombait avant l'ouverture.

### ⚠️ Le nouveau soin capillaire est un RENDEZ-VOUS, pas un formulaire

Gloria écrit « consultation personnalisée de 30 minutes, privilégiée en
présentiel ». L'analyse se fait **pendant** la consultation : elle passe donc
en `kind:'book'` (règlement, acompte, créneau), comme la Consultation Peau —
Suivi. C'est ce qui a rendu le questionnaire capillaire caduc.

---

## 2. « LA LUMIÈRE » — la direction artistique

**La phrase :** *une clinique esthétique, c'est **la lumière qu'on approche
d'une peau** : d'abord pour la lire, ensuite pour la révéler.*

Tout en sort : les images (matière + lumière), le rythme des fonds, et **une
animation par zone**.

| Zone | Animation signature |
|---|---|
| héros | **la lampe qui passe** — un rai traverse le héros à chaque entrée |
| bandeau RDV | **le filet de lumière** qui court sur la bande |
| manifeste (neuf) | **les trois foyers** — les piliers s'allument un à un |
| ruban | **le défilé** des mots du métier |
| en-tête de famille | **l'examen** — le voile se retire, l'image s'éclaire |
| carte de soin | **le trait qui se trace** — le croquis se dessine |
| protocole | **les étapes qui s'allument** en cascade |
| rendez-vous | **le créneau qui s'illumine** |
| final | **le halo qui se referme** |

Rythme des fonds : héros **sombre** → bandeau **menthe** (accent) → manifeste
**papier** → ruban **encre** → soins **clair** → rendez-vous **papier** →
final **encre** → pied **encre**.

### Un croquis par soin, pas un par famille

Les onze cartes partageaient **quatre** dessins : les trois soins du visage
montraient la même goutte. Onze croquis au trait ont été écrits dans le même
idiome (208×100, or, une étincelle) — et c'est ce trait qui **se trace** à
l'apparition, longueur mesurée au `getTotalLength()` pour que la vitesse soit
la même d'un dessin à l'autre. `SVC_ART` (par famille) reste en secours.

---

## 3. Les images

**19 images générées** (WaveSpeed, `nano-banana-pro`, **~2,66 $**) :
7 pour la clinique, 12 pour les trois univers.
Deux dernières fabriquées **par recadrage** (voir plus bas).

⛔ **Aucune ne montre un visage, une peau, un cheveu, une main, un produit ni
un intérieur.** Ce sont des matières : brume sur marbre, gouttes de sérum,
cristaux de gommage, soie, huile d'or, halo. C'est ce que le standard du
2026-08-01 autorise (« ambiance, matière, texture, arrière-plan, éditorial »).

### ⛔ Le solde est épuisé, et Mongazi veut autre chose

En fin de journée : *« les images doivent mettre en avant les soins, les
massages, l'esthétique, pas de "genre" image »*. C'est-à-dire des **gestes de
soin** et non des matières.

- **WaveSpeed : 0,03 $. Higgsfield : 0 crédit.** Impossible de générer.
- Le script est **écrit et prêt** : `_outils/_gen_soins.py`. Rechargez le
  solde, lancez `python _outils/_gen_soins.py`, regardez les cinq images, puis
  `--poser`. Rien d'autre.
- **La ligne qui n'est pas franchie**, écrite dans le script : aucun
  avant/après, aucun visage en portrait « après soin », aucune vue large d'une
  cabine présentée comme l'institut de Gloria. Et **la peau est
  ouest-africaine, c'est écrit dans le prompt** — le modèle occidentalise par
  défaut.
- ⚠️ La photo d'un vrai soin réalisé par Mme Sabrina vaudra toujours mieux que
  la meilleure image générée. C'est le dernier palier, celui qu'on ne peut pas
  franchir à sa place.

---

## 4. Ce que les CAPTURES ont montré et qu'aucun code ne disait

Le QC était vert pendant que ces défauts existaient. Ils ont tous été trouvés
en regardant les images, une par une.

| Défaut | Pourquoi le code ne le montrait pas |
|---|---|
| Les pastilles sociales se posaient sur **« ENTRER »** (hub) et sur les titres de section (clinique) | un `fixed` est ancré au viewport : réserver une marge en bas de page n'y change rien |
| La pastille **« Catalogue » chevauchait l'icône WhatsApp** à 390 px | 16 → 166 px contre une première icône à 119 px : il fallait mesurer |
| La bande d'image **recouvrait le sous-titre** des trois univers | ma règle était posée **avant** `.brand` : à spécificité égale, la dernière gagne |
| Le raccourci `padding` de deux requêtes média **remettait le haut à zéro** | il ne touchait « que » les côtés, en apparence |
| La matière des familles INA était **invisible** | `z-index:-1` la posait DERRIÈRE la carte : on voyait le fond de page au travers |
| Le fond d'INA **concurrençait le texte** | une image de fond à 42 % n'est plus un fond |
| Le bouton final portait une **icône WhatsApp**, le libellé « Voir les soins » et un lien vers `#soins` | trois promesses dans un seul bouton |
| Le pavé « 2. Choisissez un créneau » était **un grand vide** | il n'affichait rien tant qu'aucun jour n'était choisi |

---

## 5. La visibilité, mesurée et non supposée

Demande de Mongazi : *« que tout soit bien visible, pas de bouton invisible »*.
Un contrôle a été écrit pour ça : **il mesure le contraste sur les PIXELS
RENDUS** (on masque le texte, on photographie ce qu'il y a dessous, on compare).
Un contrôle qui lit `background-color` est aveugle dès qu'un texte est posé sur
une photo — c'est la leçon Angy Art du 2026-08-08.

**Ce qu'il a trouvé, et qui existait pour la plupart AVANT ce chantier :**

- ⛔ **Au survol, les boutons passaient en or et le texte restait crème :
  3,29:1.** Règle de la maison confirmée une fois de plus — *un aplat d'or
  porte du texte foncé, jamais du clair.*
- le lien « Accueil » à **2,72:1**, la mention « réalisé par » à **2,49:1**,
  les badges de préoccupation à **3,84:1**, les méta à **3,00:1**
- sur Cozy : l'étiquette du héros à **2,89:1**, la pastille de filtre active
  (blanc sur rose) à **1,59:1**
- trois valeurs nouvelles, mesurées : `--or-texte:#7d5f18`, `--gris-f:#63605a`,
  `--menthe-f:#42695b` (et `--rose-texte:#9c5468` sur Cozy)

**Résultat : 4 pages, contrastes tous verts.**

### ⚠️ Quatre fois, c'est ma SONDE qui mentait

Vérifier l'instrument avant d'accuser la page, à chaque fois :

1. **La sonde se mesurait elle-même** : elle posait le drapeau « texte
   transparent » *avant* de lire la couleur du texte. À partir de la deuxième
   mesure elle lisait `rgba(0,0,0,0)` et annonçait 1,10:1 sur des textes
   parfaitement lisibles.
2. **Elle mesurait au bord de la fenêtre** : l'élément passait sous la bande de
   bord, et c'est l'ombre de l'instrument qu'elle photographiait (2,10:1).
   → on amène l'élément **au milieu** avant de mesurer.
3. **Elle mesurait pendant la révélation** : une carte à mi-opacité donne
   3,29:1 sur un bouton qui en vaut 16,6 une fois posé. → attendre 800 ms.
4. **Elle accusait l'image du héros de déborder** : elle est agrandie par un
   `transform` et rognée par un `overflow:hidden`. → on regarde qui la coupe.

Et un cinquième, plus subtil : le **piège à robots** du formulaire est posé à
−9999 px. Il est « visible » au sens du CSS et personne ne le touchera jamais.

---

## 6. Ce qui a été retiré parce que ça coûtait cher pour rien

`.marble::before` sur le hub **et** sur INA Luxury : un calque plein écran,
`position:fixed`, en **`mix-blend-mode:screen`**, **animé en boucle**. C'est
exactement ce qui a été mesuré sur Angy Art le 2026-08-26 (un tiers à trois
quarts du budget d'une image, pour un effet indiscernable). Remplacé par une
vraie image, sans mélange et sans animation.

Idem : `.lc-social a` animait une ombre **en boucle sous un `backdrop-filter`**
sur les quatre pages — l'interdit né sur Boussole le 2026-07-21.

---

## 7. Les outils, tous neufs

| Outil | Ce qu'il fait |
|---|---|
| `_outils/_qc.py` | **la suite de contrôle** — contraste mesuré sur les pixels rendus, recouvrements **calculés** (pas échantillonnés), cibles 44 px, boutons fantômes, animations infinies sous `backdrop-filter`, bande de bord vraiment opaque. `--page` pour les 4 pages |
| `_outils/_vues.py` | photographie zone par zone en 390 et 1440 — **la fenêtre, pas l'élément** |
| `_outils/_gen_ambiances.py` | les 7 matières de la clinique |
| `_outils/_gen_univers.py` | les 12 matières du hub, d'INA et de Cozy |
| `_outils/_gen_soins.py` | **les 5 images de gestes de soin — prêtes, en attente du solde** |

---

## 8. Ce qui reste

- ⏳ **Recharger WaveSpeed** puis `python _outils/_gen_soins.py` (≈ 0,70 $).
- ⏳ **Deux ambiances sont des recadrages** (`ina-levres`, `cozy-fermete`) :
  à régénérer proprement quand le solde revient.
- ⏳ **Déployer** : `wrangler pages deploy . --project-name luxury-club-229`
  ⚠️ ce projet se déploie avec `.` — tout fichier manquant sur le disque
  disparaît aussi du site. Vérifier `git status` avant.
- ⏳ Les vraies photos de l'institut et des soins de Mme Sabrina.
- ⏳ `assets/images/clinic/consultation-peau.jpg` est un **avant/après** de
  provenance inconnue, toujours pas intégré, et il ne doit pas l'être.

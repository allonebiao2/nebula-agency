# NEBULA · le studio vidéo

Le montage des vidéos de l'agence, écrit en code plutôt qu'à la souris. Une
vidéo est un programme : on change une question, on relance, la vidéo est
refaite à l'identique. Aucun projet CapCut à retrouver, aucun export à refaire à
la main.

Outil : **Remotion 4.0.512** (React + rendu H.264).

---

## Ce qu'il y a dedans aujourd'hui

Les trois séries « oui / non » de
`_documents/nebula-agency/marketing/TIKTOK-OUI-NON.md`, en 1080x1920, 30 images
par seconde :

| Composition | Contenu | Durée |
|---|---|---|
| `oui-non-1-prix` | Script 1 · le prix, 9 questions | 25,5 s |
| `oui-non-2-besoin` | Script 2 · « je n'ai pas besoin de site », 8 questions | 23 s |
| `oui-non-3-logiciel` | Script 3 · le logiciel métier, 8 questions | 23 s |

Et la démonstration d'un produit de la maison :

| Composition | Contenu | Durée |
|---|---|---|
| `lepli-demo` | **LE PLI · la lettre digitale**, six plans | 30 s |
| `lepli-plans/` | Les six plans, chacun réglable seul | |

Le rythme est celui du document : la question tient **1,5 s**, la réponse
**1 s**, la carte finale **3 s**, et la coupe est **sèche** (aucune transition,
c'est le format qui le veut).

Les cartes ne sont pas redessinées ici : ce sont les PNG écrits par
`_documents/nebula-agency/marketing/_cartes.py`, importés tels quels. Une
question change → on regénère la carte avec `python _cartes.py`, jamais à la
main.

Et une vidéo filmée, reprise en motion design (2026-09-27) :

| Composition | Contenu | Durée |
|---|---|---|
| `dimanche-plan` | **Le plan du dimanche** : le face caméra d'un proche (trading, 3 min 29) habillé scène par scène | 3 min 33 |

La méthode, réutilisable sur n'importe quel face caméra :

1. **La source reste hors dépôt** (`public/dimanche/`, ignoré) : c'est la vidéo
   d'un particulier.
2. `python _outils/dimanche_image.py` **efface les sous-titres incrustés**
   (blanc pur, en traits fins, remplissage Telea), étalonne et agrandit en
   1080x1920. `--essai 56` rend un avant/après d'une seule image.
3. `python _outils/dimanche_son.py` nettoie la voix (passe-haut, débruitage
   spectral, compression) et la pose à **−14 LUFS**, mesurés (BS.1770).
4. La parole est transcrite **en local** (faster-whisper large-v3-turbo, au mot),
   puis `python _outils/dimanche_mots.py <transcription.json>` applique les
   corrections et écrit `src/dimanche/mots.ts`. **Chaque animation se cale sur un
   mot par son indice** (`d(62)` = le début de « jamais »), jamais sur une
   seconde recopiée.
5. `python _outils/dimanche_bruitages.py` synthétise les bruitages (aucun
   fichier tiers).
6. `node _outils/planches.mjs dimanche-plan 1.2 7.2 …` rend des images fixes en
   une seule ouverture de Chrome, `python _outils/assembler_planches.py` les
   met en planche : **on regarde avant de rendre les 3 min**.
7. `node _outils/rendu_morceaux.mjs dimanche-plan` rend **par morceaux** de
   640 images, puis le son, puis recolle sans réencoder (~1 h 30 sur ce PC).
   ⛔ **Jamais d'un seul tenant** : le 2026-09-27, Chrome est tombé à l'image
   2 562 sur 6 391 faute de mémoire (8 Go, Chrome ouvert à côté) et tout était
   perdu. Un morceau fini est gardé, relancer reprend où ça s'est arrêté. À
   lancer détaché, avec un garde-éveil (le PC s'endort après 30 min).

⚠️ Le ffmpeg livré avec Remotion est réduit : ni `rawvideo`, ni `s16le`, ni
`drawtext`, ni `ebur128`. On lui passe des JPEG (`image2pipe`) et des WAV.

Et la vidéo de marque de l'agence (2026-10-02) :

| Composition | Contenu | Durée |
|---|---|---|
| `nebula-30s` | **NEBULA · le tour de magie** : vitrine, catalogue, outil, et la vidéo elle-même | 30 s |

Voir la section « NEBULA · la vidéo de marque » plus bas.

## Ce qui manque encore

- **Les plans filmés.** Le visage qui fait oui ou non n'est pas tourné. En
  attendant, la réponse s'affiche en grosses lettres sur fond noir et la vidéo
  se rend quand même. Voir `public/LISEZ-MOI.md` pour la brancher.
- **La musique.** Même dossier, mêmes explications, et l'avertissement qui va
  avec sur les droits.

---

## Les commandes

```bash
cd _studio-video

npm run studio          # l'aperçu dans le navigateur, on scrube à la souris
npm run rendu           # les trois vidéos dans out/
npm run rendu:prix      # une seule
npm run rendu:dimanche  # le plan du dimanche, par morceaux (~1 h 30, garde-éveil)
npm run rendu:nebula30  # la vidéo de marque NEBULA, par morceaux, puis le mastering du son
npm run verifier        # contrôle TypeScript, sans rien rendre
```

Le premier rendu télécharge un Chrome sans interface (une centaine de Mo). Les
suivants ne le retéléchargent pas.

`out/` n'est pas versionné : une vidéo se refabrique, elle n'a rien à faire dans
un dépôt public.

## Les fichiers

```
src/scripts.ts    les questions, les réponses, le rythme  ← c'est ici qu'on édite
src/OuiNon.tsx    le montage : question, coupe, réponse
src/Root.tsx      toutes les compositions, 1080x1920
public/           les plans filmés et la musique (hors dépôt)

src/lepli/donnees.ts   LE PLI : couleurs, texte de la lettre, rythme  ← on édite ICI
src/lepli/LePli.tsx   le montage des six plans
src/lepli/*.tsx        un fichier par plan
```

---

## LE PLI · la démonstration du produit

> Une lettre digitale, c'est **une enveloppe cachetée qu'on ouvre à l'heure
> dite.** Toutes les animations sortent de cet objet, et d'aucun autre.

Six plans, six signatures, reprises une par une de `lepli/README.md` :

| # | Plan | Signature | Durée |
|---|---|---|---|
| 1 | Le seuil | le cachet **respire, puis se brise** en trois éclats de cire | 5,5 s |
| 2 | La lettre | **le dépliage**, puis **l'encre qui sèche** ligne après ligne | 8,5 s |
| 3 | Le compte | **les chiffres qui roulent**, avec une sortie qui ralentit | 3 s |
| 4 | La signature | **le trait qui s'écrit** (`stroke-dashoffset`) | 3 s |
| 5 | L'heure dite | **l'aiguille qui monte à minuit** | 6 s |
| 6 | La carte | **le cachet qui se referme** : la boucle du plan 1, à l'envers | 4 s |

Le plan 5 est le seul dont la signature n'existe pas dans le produit, et c'est
lui qui vend : l'heure choisie est ce qui donne son nom à LE PLI. Elle sort
quand même du même objet, le cadran reprenant le cercle et le pointillé **du
cachet**.

### Ce qui n'est pas inventé

Rien. Les couleurs sont les jetons de `lepli/lettre.html`, le texte de la
lettre est celui de la démonstration du produit (accentué, il ne l'était pas
dans les captures), le prix est celui de `lepli/creer.html`. Tout est recopié
**une seule fois**, dans `src/lepli/donnees.ts`.

⚠️ **Aucune police téléchargée**, comme dans le produit : la pile est système,
Palatino Linotype sous Windows. La vidéo doit ressembler à la lettre que la
destinataire ouvrira, pas à une version embellie pour la publicité.
⛔ Ne pas rajouter Google Fonts ici.

### ⛔ Avant de publier cette vidéo

Elle promet **« Elle l'ouvre à minuit pile. Pas avant. »** et affiche
`lepli.nebula-agency.online`. Au 2026-09-03, ni l'un ni l'autre n'existe :
la livraison à l'heure choisie (n8n) et le serveur en ligne sont les deux
chantiers ouverts de `lepli/README.md`. La vidéo est prête, **la promesse ne
l'est pas** : elle attend que l'adresse réponde.

### ⛔ Pas de fondu enchaîné, et ce n'est pas un raccourci

Les six plans posent leur contenu sur **le même fond de nuit**, et chacun fait
entrer et sortir ce contenu lui-même. Une coupe entre deux plans est donc
invisible : ce qui change, c'est ce qui est posé dessus, pas le fond.

Un fondu enchaîné, lui, superpose les deux plans. Essayé, puis **regardé** sur
l'image 372 : la feuille de la lettre à 50 % et la carte du compte à 50 %
donnaient deux rectangles clairs décalés l'un sur l'autre, le « 332 » roulant
par-dessus le texte de la lettre. Ça ne ressemble pas à une transition, ça
ressemble à une panne. `@remotion/transitions` a été désinstallé.

### ⚠️ Ce que CSS ne sait pas faire ici

`lettre.html` anime son cachet en `@keyframes`. **Une animation CSS ne se rend
pas** : elle joue à l'horloge du navigateur, et le rendu la photographierait
figée ou au hasard. Tout est donc réécrit en `useCurrentFrame()` et
`interpolate()`. Même chose pour un `transition:` : il n'existe pas ici.

⚠️ **`rotate: 12` en nombre nu sort en `rotate:12px`, donc invalide et ignoré
sans un mot** (React n'a `scale` dans sa table des valeurs sans unité, pas
`rotate`). Toute rotation s'écrit `` `${...}deg` ``.

---

## ⚠️ La licence Remotion, vérifiée le 2026-08-14

Lue dans `node_modules/remotion/LICENSE.md`, la licence de la version installée,
et dans la FAQ officielle. Ce n'est pas du logiciel libre au sens habituel.

**NEBULA est éligible à la licence gratuite**, à trois conditions qui sont
remplies aujourd'hui :

1. **Trois personnes au plus.** Le texte : *« a for-profit organization with up
   to 3 employees »*. Les partenaires commerciaux ne sont pas des salariés, mais
   le jour où l'agence emploie quatre personnes, la licence entreprise devient
   obligatoire.
2. **L'usage commercial est autorisé**, y compris les vidéos vendues à un
   client : *« Any commercial use case is allowed as long as you are not selling
   Remotion as a product itself »*. La FAQ le dit pour les agences : *« If your
   agency has 3 or fewer personnel, the Free License covers this work. »*
3. **On livre des fichiers vidéo, pas le projet Remotion.** Si le client devient
   propriétaire du projet, la FAQ additionne les effectifs des deux sociétés et
   c'est **au client** de payer la licence. Un client de plus de trois salariés
   ferait donc basculer l'affaire : on lui remet le MP4, pas le code.

Ce qui reste interdit dans tous les cas : revendre, relouer ou sous-licencier
une version dérivée de Remotion. Vendre une vidéo faite avec Remotion, oui ;
vendre Remotion habillé en produit NEBULA, non.

**La version est figée à 4.0.512, et ce n'est pas un détail.** La licence
**change en 5.0** (télémétrie obligatoire avec clé de licence pour le modèle
« Automators »). Ne pas faire `npm update` sans relire la licence de la version
visée : c'est exactement pour ça que l'installation a été faite avec
`--save-exact`.

---

## NEBULA · la vidéo de marque (`nebula-30s`, 2026-10-02)

> Une nébuleuse, c'est **de la poussière qui devient des étoiles**. L'objet du
> film : la poussière d'étoiles. Elle explose, tourne en galaxie, dessine un
> téléphone, tourne en orbite autour d'un catalogue, puis revient s'effondrer
> dans l'étoile du logo.

Le film est un **tour de magie en trois temps** :

1. **la promesse** : « Regardez bien. Tout ce que vous allez voir… NEBULA le
   crée pour votre business. » ;
2. **les trois tours** : la vitrine (le vrai site d'Angy Art, puis un éventail
   de vitrines livrées), le catalogue (Au Braisé d'Or, les vrais champagnes de
   Weinkeller et les vraies robes d'Hillary en orbite, les commandes qui arrivent
   sur WhatsApp), l'outil (un tableau de bord qui change de peau selon le métier) ;
3. **la révélation** : l'image se fige, « Et même… cette vidéo. » La caméra
   recule : on était dans un logiciel de montage (les vrais sites en rushes, les
   vraies ondes de la voix et de la musique sur la timeline). La tête de lecture
   rembobine, puis file vers un clip vide : « La vôtre est la prochaine. »
   L'appel WhatsApp, puis la signature : le logo naît de l'étoile.

### La chaîne, dans l'ordre

```bash
python _outils/nebula30_logo.py        # le logo en couches + src/nebula30/couches.ts
python _outils/nebula30_captures.py    # les 9 sites, photographiés en ligne
python _outils/nebula30_bruitages.py   # 25 bruitages synthétisés (aucun fichier tiers)
python _outils/nebula30_son.py         # voix placée, musique montée, src/nebula30/minutage.ts
npm run rendu:nebula30                 # l'image par morceaux, le son, puis le mastering
python _outils/nebula30_verifier.py    # durée, sonie, synchro de la voix, planche tirée du MP4
```

La vidéo à publier : **`out/NEBULA-Agency-30s.mp4`**. ⚠️ Pas `NEBULA-30s.mp4` : sous Windows,
les noms ignorent la casse, et ce serait le même fichier que `nebula-30s.mp4`, le
provisoire que le mastering lit (il a été écrasé ainsi le 2026-10-02).

Entrées hors dépôt, dans `public/nebula30/` : `voix-vous-brute.mp3` (ElevenLabs,
voix « Alimata », Eleven v4), `musique-brute.mp3` (« afro house » d'artissizm,
**Pixabay**, licence Pixabay : garder le lien de la page, c'est la preuve) et
`transcription-vous.json` (Whisper large-v3-turbo en local, au mot).

### Ce qui n'est pas inventé

Les sites sont les vrais, photographiés en ligne. Les produits et leurs prix
sont ceux des catalogues livrés. Le tableau de bord de l'outil porte la pastille
**DÉMO** : ses chiffres sont un exemple, jamais un résultat promis. **La voix ne
dit aucun chiffre** : prix, délai et numéros vivent à l'écran (`FAITS` dans
`donnees.ts`), on refait l'image sans refaire la voix.

### Le son

- La voix sortait d'ElevenLabs à **−26,6 LUFS** : remontée à −16, compressée,
  découpée **dans ses silences mesurés** et posée réplique par réplique.
  « Et même » et « cette vidéo » sont séparés dans leur vrai silence (−60 dB,
  14,64 à 14,76 s de la prise) pour tenir le suspense du gel.
- La musique est à **120 BPM pile**. L'explosion tombe sur un premier temps,
  **l'image se fige là où la chute devait tomber** (la musique s'arrête comme une
  bande qu'on freine), la chute éclate après « …la prochaine. », le logo
  s'allume deux mesures plus tard, et la fin reprend **la vraie fin du morceau**.
- Sous chaque phrase, la musique est baissée automatiquement (≈ 13 LU sous la
  voix, mesuré). `_outils/nebula30_master.py` pose ensuite −14 LUFS et un
  limiteur à −1 dBTP sur le son rendu, et **vérifie réplique par réplique** que
  la voix passe devant.
- Toute nouvelle prise de voix : relancer la transcription, puis
  `nebula30_son.py`, qui **refuse** une prise dont le nombre de phrases ne
  correspond pas au plan (au lieu de mal placer la voix sans un mot).

### Les pièges rencontrés

- ⚠️ **Syne 800 est très large** : environ 1,1 em par capitale. « CATALOGUE » à
  116 px sortait du cadre, « REGARDEZ » se coupait en « REGARDE / Z ». Les titres
  restent à 96 px, en `nowrap`, et les lignes sont coupées **à la main**.
- ⚠️ Dans une ligne centrée, les mots encore invisibles **gardent leur place** :
  le premier mot apparaît à gauche du centre. Voulu ici (effet machine à écrire),
  mais à savoir.
- ⚠️ Des grains qui traversent tout l'écran font une **toile d'araignée** de
  traînées : l'orbite du catalogue s'ouvre depuis le téléphone, et la traînée est
  plafonnée à 70 px.
- ⚠️ Le téléphone n'apparaît qu'**après** que la poussière a dessiné son contour,
  sinon le tour est éventé.
- ⚠️ Le moniteur du logiciel de montage montre le film **pour de vrai** :
  `Montage` reçoit `Film` et le rend à un autre instant (figé, rembobiné). Toutes
  les scènes ne lisent que `t` : c'est ce qui rend ce tour possible.

### ⏳ Ce qui attend

- **La version TikTok** (tutoiement, règle de la marque) : les textes sont prêts
  (`TEXTES.tu`), il manque sa voix. Elle n'est pas déclarée tant qu'elle manque.
- Une version 16:9 (YouTube, site) si on la veut.

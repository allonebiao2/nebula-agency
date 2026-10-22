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
| `malettre-pub/` | **MA LETTRE À… · la pub** : `fr-30`, `en-30`, et les deux coupes de 15 s des statuts (`fr-15-lettre`, `fr-15-plume`, `en-15-letter`, `en-15-quill`) | 30 s / 15 s |
| `malettre-minuit` | **MA LETTRE À… · « Minuit pile, pour maman »** : le film YouTube, 16:9, 60 i/s, en 3D (Three.js) | 56 s |

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

Et la publicité d'une cliente (2026-10-03) :

| Composition | Contenu | Durée |
|---|---|---|
| `grain-35s` | **GRAIN D'ESTHÉTIQUE · le grain qui révèle** : l'institut de Jocelyne, pour faire écrire « rendez-vous » sur WhatsApp | 35 s |

Voir la section « GRAIN D'ESTHÉTIQUE · la publicité » plus bas.

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
npm run rendu:grain35   # la pub Grain d'Esthétique, par morceaux, mastering, vérification
npm run rendu:malettre  # MA LETTRE À… : les six versions, UN onglet (⛔ pas avant la voix et le site)
npm run rendu:minuit    # MA LETTRE À… · « Minuit pile » : par morceaux (UN onglet), puis la vérification
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

---

## GRAIN D'ESTHÉTIQUE · la publicité (`grain-35s`, 2026-10-03)

> Un institut comme celui-ci, c'est **un grain de peau qu'on révèle** (la phrase
> de son affiche). L'objet du film : **le grain d'or**. Il dérive sur les bords et
> laisse le centre libre, il balaie une scène pour révéler la suivante (comme un
> gommage révèle la peau), et c'est lui qui tombe en dernier sur le logo : le
> point rond du « i » de « Grain ». Et sa marque est un **œil** : il s'ouvre au
> début, et la caméra plonge dans sa pupille pour entrer dans l'institut.

Pour l'institut de Jocelyne, la mère de Mongazi. **Un seul but : qu'on écrive sur
WhatsApp.** 35 s, 1080x1920, 30 i/s.

| Temps | Voix (Alimata, Eleven v4, avec balises) | Image |
|---|---|---|
| 0 → 4,8 s | « Vous vous occupez de tout le monde… Mais qui s'occupe de vous ? » | l'œil de son logo se dessine en or ; les mots d'une journée saturent l'écran puis se dissolvent sur « vous » |
| 4,1 → 8,6 s | « Chez Grain d'Esthétique, vous passez enfin en premier. » | la plongée dans la pupille, l'or remplit l'écran, l'iris s'ouvre sur SA photo |
| 8,6 → 12 s | « Des soins signés Sothys Paris et Sultane de Saba. » | les deux noms en très grand, un reflet d'or |
| 12 → 16 s | (musique : la relance) | la vague de grains finit PILE sur la relance ; ses vrais avis Google |
| 16 → 20,8 s | « Un visage qui s'illumine. Un corps qui respire. » | la lumière qui s'épanouit, les ondes qui respirent, ses prix |
| 20,8 → 25 s | « Et des lèvres repulpées… sans une seule piqûre. » | les lèvres se tracent ; sur l'ARRÊT de la musique une seringue, sur LA RELANCE elle éclate en grains ; sa fiche Hyaluropen |
| 25 → 28,5 s | « C'est votre tour : écrivez rendez-vous sur WhatsApp. » | sa vitrine, le doigt, WhatsApp, « Rendez-vous » tapé au rythme de la voix, ✓✓ |
| 28,5 → 35 s | « Grain d'Esthétique. La beauté est un art de vivre. » | SON logo s'écrit (sourcil, eyeliner, l'œil s'ouvre, le G, les lettres, LE GRAIN tombe sur un premier temps), la devise, le numéro |

### La chaîne, dans l'ordre

```bash
python _outils/grain35_logo.py       # SON logo vectoriel en 40 couches + src/grain35/couches.ts
python _outils/grain35_faits.py      # les faits LUS dans sa vitrine → src/grain35/faits.ts
python _outils/grain35_captures.py   # sa vitrine photographiée en ligne (sections)
python _outils/grain35_son.py        # voix coupée et placée, musique montée → src/grain35/minutage.ts
                                     #   (python _outils/grain35_son.py afro-chill : l'autre musique)
node _outils/planches.mjs grain-35s 3.6 12.3 23.4 31.4   # REGARDER avant de rendre
npm run rendu:grain35                # rendu par morceaux (1 onglet), mastering −14 LUFS, vérification
```

La pub à envoyer : **`out/Grain-d-Esthetique-pub-35s.mp4`** (⚠️ pas `grain-35s.mp4`,
le provisoire que le mastering lit : sous Windows la casse ne compte pas).

Entrées hors dépôt, dans `public/grain35/` : `sources/voix-brute.mp3` (Alimata,
vitesse 1,08, stabilité 50, balises `[warmly]`, `[whispers]`…), les deux musiques
**Pixabay** (« Soulfire, the midnight ritual » de djoldcatz, n° 460495 ; « Afrobeat
ethnic beat electro chill » de jacquesflix, n° 293723 : garder le lien des pages,
c'est la preuve de licence), `institut.jpg` (sa seule photo), `vitrine/` (captures).

### Ce qui n'est pas inventé

- **Les prix, le numéro, les horaires, le quartier, les maisons, la devise** sont lus
  dans sa vitrine (`faits.ts`). ⚠️ Pas « le moins cher de la section » : celui du
  visage est un remplissage de faux cils (7 000 F). On lit des soins **par leur nom**
  (« Soin visage mini Sothys », 17 000 F) ; un nom absent fait échouer l'outil.
- **Les avis** sont recopiés mot pour mot des 7 captures de sa fiche Google
  (extraits en « … », accents rétablis, prénom + initiale). **Aucune note moyenne** :
  un avis est à 4 étoiles, la moyenne n'est peut-être pas 5,0.
- **La seule photo** est la sienne. Aucune personne d'une banque d'images.
- La conversation WhatsApp **s'arrête au message envoyé** : aucune réponse inventée.

### Le son

- La voix (23,95 s) est coupée en **13 répliques dans ses silences mesurés** (il y a
  −91 dB entre « repulpées » et « sans ») et posée sur la musique. ⚠️ ElevenLabs a
  dit « **rendez-vous** » pour « RDV » (Whisper sans indice, 0,99) : l'écran dit
  donc « rendez-vous » aussi. « Sothys » est juste (« Sotis »).
- **Soulfire, 90 BPM, une seule fenêtre sans raccord (piste 211,36 → 246,36 s)** : la
  basse entre sur « Mais qui s'occupe de vous ? », deux ARRÊTS d'un temps suivis
  d'une relance (12,67 s : les avis ; 23,33 s : « sans une seule piqûre »), le grain
  tombe sur un premier temps (31,33 s), la vraie fin du morceau s'éteint sous le logo.
- La musique est baissée sous la voix (−28 LUFS momentanés) : écart médian **12 LU**.
  Le chuchotement est posé à 8 LU au-dessus : un secret, pas un murmure perdu.
- Les bruitages sont ceux de NEBULA, synthétisés (aucun fichier tiers).

### Les pièges rencontrés

- ⛔ **`Logo.tsx` et `logo.ts` dans le même dossier** : sous Windows c'est le même
  fichier pour TypeScript. Les couches s'appellent `couches.ts`.
- ⛔ **`np.convolve` sur une fenêtre de 400 ms** (sonie momentanée) : 2,7·10¹⁰
  opérations, l'outil ne finissait pas en 5 minutes. Moyenne glissante par somme
  cumulée : **9 secondes**.
- ⛔ **Whisper avec un `initial_prompt` recrache l'indice** quand il n'entend pas bien
  (vu sur le clip de JP le même jour) : la voix est transcrite **sans indice**, et
  c'est aussi ce qui prouve que « Sothys » est bien prononcé.
- La vitrine pose un bouton WhatsApp flottant (`.wa-fab`) sur tout : il s'était
  imprimé sur la fiche Hyaluropen. Masqué dans `grain35_captures.py`.
- Les mots de l'accroche **tirés au hasard** se chevauchaient et sortaient de l'écran :
  ils ont des places composées.

## MA LETTRE À… · la publicité (`malettre-pub/`, 2026-10-21)

Six versions, une par MP3 de `src/malettre/VOIX.md` : 30 s en français et en
anglais, et deux coupes de 15 s par langue pour les statuts WhatsApp (A vend le
cachet, B lève le frein de la page blanche). **Les images sont faites ; la voix ne
l'est pas** : le minutage de `src/malettre/minutage.ts` est provisoire, écrit
d'après le tableau de `VOIX.md`.

La phrase, celle du produit : une lettre digitale, c'est une **enveloppe cachetée
qu'on ouvre à l'heure dite**. Sept plans, sept gestes de cet objet :

| Plan | Signature |
|---|---|
| L'accroche | le prénom qui se remplit (« Ma lettre à… papa. À Afi. À maman. »), chaque enveloppe avec l'habillage réel de son exemple |
| Scellée | la cire qu'on presse, qui s'écrase un peu puis respire |
| La plume | le **vrai constructeur photographié** : la fiche d'Afi, ses puces cochées une à une, puis la lettre que la plume a écrite |
| L'attente | le lien nu dans une bulle, puis l'enveloppe et le compte à rebours du produit |
| L'ouverture | la cire s'allume, le cachet casse en trois éclats, la feuille se déplie, l'encre sèche |
| Les occasions | quatre cachets pressés, quatre noms exacts du constructeur |
| La marque | le cachet se reforme (le favicon), « Dès 1 000 F » ou « La plume : 500 F de plus », l'adresse |
| La page blanche (coupe B) | une feuille vide où le curseur clignote |

### La chaîne, dans l'ordre

1. `python _outils/malettre_captures.py` : photographie `malettre/creer.html` et
   `en/creer.html` (390 px, ×3) dans `public/malettre/<langue>/`, et écrit
   `src/malettre/captures.ts` (taille de la fiche, centre de chaque puce cochée :
   c'est là que le doigt tombe). À relancer si le constructeur change.
2. ⏳ **Quand les MP3 sont posés** dans `_partage/ma lettre/voix/` :
   `python _outils/malettre_son.py`. Il transcrit chaque prise au mot (Whisper
   large-v3-turbo, sans indice), la rapproche du texte de `VOIX.md` (lu dans le
   fichier), nettoie la voix vers `public/malettre/voix-<version>.wav` et réécrit la
   ligne de la version dans `minutage.ts` : chaque phrase ouvre son plan, les mots-clés
   (prénoms, « plume », « cire », les occasions) deviennent ses `temps`. Si la voix va
   plus vite que l'image (une lettre qui s'ouvre doit se lire : `MINIMUM`), la prise est
   coupée dans le souffle avant la phrase suivante, qui attend. Une coupe de 15 s qui
   déborde est **refusée** (il faut une prise plus rapide). Les versions sans MP3 gardent
   leur minutage provisoire. `--essai` vérifie tout sans audio.
   **Aucune scène n'est à toucher** : un plan étire ses gestes sur la durée reçue.
3. `npm run rendu:malettre`, à UN onglet, pas pendant un calcul lourd.

### Ce qui n'est pas inventé

Les couleurs, cires, papiers et dessins de sceau sont ceux de `malettre/lettre.html`.
Les lettres montrées sont les **exemples écrits par la vraie plume** le 2026-10-16
(`exemples.json`, `exemples.en.json` ; la lettre anglaise n'est pas une traduction).
La phrase sous l'enveloppe est celle que la lettre affiche (`L.ouvre` + `libQuand()` :
« Elle s'ouvre dimanche 14 février à minuit. »). Le lien n'a pas d'aperçu d'image,
parce qu'une lettre n'en a pas (`lettre.html` n'en porte aucune, exprès) ; son jeton
a le bon alphabet et n'ouvre rien.

### ⛔ Avant de publier

L'adresse `malettre.nebula-agency.online` doit répondre, et la caisse être branchée :
la fin de la vidéo promet les deux. La licence Remotion : on livre le MP4.
⛔ **Les coupes de la plume (`fr-15-plume`, `en-15-quill`) attendent que la plume
rouvre en ligne** (coupée le 2026-10-22). Et plus rien n'est gratuit : la fin dit
« Dès 1 000 F » (La Carte), jamais « Gratuite pour commencer ».

---

## MA LETTRE À… · « Minuit pile, pour maman » (`malettre-minuit`, 2026-10-22)

> Une lettre digitale, c'est **une enveloppe cachetée qu'on ouvre à l'heure dite**.
> L'objet du film : **le cachet de cire**. Il se presse à Paris, file dans la nuit
> le long du méridien, dort sur un téléphone à Cotonou, s'embrase à minuit, éclate
> en trois morceaux, puis retombe sur le papier : c'est la marque.

Le film YouTube : **16:9, 1920×1080 à 60 i/s, 56,3 s**. Mongazi voulait 40 à 45 s ;
**la parole seule en fait 41**, et minuit garde ses trois secondes sans voix. On ne
le raccourcit qu'en réécrivant le script (`src/malettre-minuit/VOIX.md`).

Deux voix, deux musiques : **Koffi** raconte sur le piano (l'histoire), **Alimata**
vend sur l'afrobeat. Koffi est un personnage, pas un client : la vente est dite par
une autre voix, il n'y a pas de faux témoignage.

| Temps | Voix | Image (une signature par plan) |
|---|---|---|
| 0 → 3,3 s | Koffi : « Dans trois secondes… ma mère va pleurer. » | la chambre de Cotonou dans le noir, le téléphone s'allume, 23:59:57, le temps se fige |
| 3,2 → 7,3 s | « Elle a soixante ans ce soir. Moi… je suis à Paris. » | la table de Koffi, la pluie, la bougie ; le méridien d'or qui descend |
| 7,2 → 9,4 s | « Alors je lui ai écrit une lettre… » | la plume, la bougie ; le titre de la vraie lettre s'écrit à la main |
| 9,2 → 11 s | « …qui ne s'ouvre qu'à minuit pile. » | le sceau pressé dans la cire (la fumée), puis le cachet en relief, en 3D |
| 11 → 12 s | (le piano) | l'envol : Paris → Cotonou, 4 720 km, la lettre file dans la nuit |
| 11,8 → 14 s | (tic, tac, le cœur) | retour au téléphone ; 3, 2, 1 ; le piano s'étouffe |
| 14 → 17,2 s | (aucune voix) | **MINUIT** : la cire s'embrase, la lumière jaillit, les bandes du cinéma s'ouvrent, le cachet éclate en trois, la carte sort |
| 17,1 → 21,7 s | « Maman… tu me réveillais à cinq heures… pour réviser le bac… » | la lettre : l'encre sèche, la phrase lue est au point |
| 21,7 → 23,5 s | Alimata : « Ça, c'est Ma lettre à… » | le cachet de la marque tombe sur le papier, sur le premier temps de l'afrobeat |
| 23,5 → 26,3 s | « Une lettre scellée… qui s'ouvre à l'heure que TU choisis. » | le cadran : minuit, 7 h 30, 20 h, posés sur les temps |
| 26,3 → 30 s | « Et avant l'heure ? Impossible de l'ouvrir. Même en insistant. » | trois tapotements, le téléphone secoue, le cadenas : « Pas avant l'heure. » |
| 30 → 33,6 s | « Tu l'écris… ou la plume l'écrit avec toi… » | la fiche, les puces qui se cochent, puis l'écriture |
| 33,6 → 39 s | « La cire, le sceau, le papier, ta photo… et une pluie d'étoiles… » | l'enveloppe 3D change d'habit à chaque clic, la photo glisse dedans, les trois pluies du produit |
| 39 → 41,8 s | « Pour la Saint-Valentin… à minuit pile, avant tout le monde. » | 23:59 → 00:00, la lettre arrive la première, les autres messages derrière |
| 41,8 → 44,6 s | « Pour t'excuser… sans qu'on te raccroche au nez. » | l'appel coupé ; la lettre, elle, ne raccroche pas : « Pardon. » |
| 44,6 → 46,6 s | « Pour une demande… quand la voix tremble. » | les alliances en 3D ; « Veux-tu m'épouser ? » tremble, puis se pose |
| 46,6 → 51 s | « Ou la soirée entre potes : l'heure, le lieu… et qui ramène les boissons. » | la carte kraft, l'heure et le lieu cochés, le tampon « Toi. » ; les 28 occasions défilent au loin |
| 51 → 56,3 s | « Ma lettre à… Dès mille francs. Tape un prénom : ta lettre commence. » | le cachet de la marque, « Dès 1 000 F », « maman » tapé dans le champ de la vitrine, l'adresse |

### La chaîne, dans l'ordre

```bash
python _outils/malettre_minuit_preparer.py   # fonds, marque, grain, 20 bruitages synthétisés → public/malettre-minuit/
python _outils/malettre_minuit_son.py        # voix découpées et posées, musiques, mix, master → mix.wav + minutage.json
node _outils/planches.mjs malettre-minuit 2.4 14.35 22.5 45.9   # REGARDER avant de rendre
npm run rendu:minuit                         # l'image par morceaux (UN onglet, ~20 min), le master posé tel quel, la vérification
python _outils/malettre_minuit_ecouter.py    # Whisper (~6 min) : chaque phrase est la bonne, et s'entend dans le film
```

La vidéo à publier : **`out/MaLettreA-Minuit-pile-YouTube.mp4`** (H.264 + AAC 320 kb/s).
⚠️ Pas `malettre-minuit.mp4` : c'est l'image seule, que la vérification lit.

Entrées hors dépôt (`public/` est ignoré) : les deux voix de Mongazi
(`_partage/voix de koffi tony.mp3`, `_partage/voix de alimata.mp3`, ElevenLabs v4,
balises d'intonation), les deux musiques **Pixabay** (« Emotional piano » de
nastelbom, n° 598096 ; « Afrobeat music loop, positive vibes » de sonican,
n° 481253 : garder le lien des pages, c'est la preuve de licence), les fonds de la
vitrine (`_partage/ma lettre/fonds/<zone>-paysage.png`) et le cachet du site
(`malettre/logo/cachet.svg`).

### La 3D

**Three.js dans Remotion** (`@remotion/three`, `@react-three/fiber`, `three`
0.180.0, versions figées) : le cachet en relief (une géométrie, pas une image), ses
trois éclats, l'enveloppe (poche, carte, rabat à doublure damassée), les alliances,
le halo, les étincelles. Environ **0,4 s par image** sur ce PC.

⛔ **Blender ne sert pas ici** (essayé le 2026-10-22, Blender 4.5.15 portable dans
`D:\outils\`) : EEVEE plante sur la carte Intel HD 5500 (« Out of resource error »,
`EXCEPTION_ACCESS_VIOLATION`), et Cycles sur le processeur met **417 s par image**,
soit 16 jours pour ce film. ⚠️ `HtmlInCanvas` de Remotion exige Chrome 149 :
indisponible avec le Chrome de la 4.0.512.

### Ce qui n'est pas inventé

- **La lettre lue est une vraie lettre de la plume** (« Un bol de bouillie à
  5 heures »), écrite à partir d'une fiche inventée puis relue : aucun fait ajouté.
- Chaque promesse existe dans le produit : l'heure choisie, le cachet qui refuse de
  s'ouvrir avant, la plume, la cire, le sceau, le papier, la photo, les trois pluies,
  **les 28 occasions** (leurs noms exacts), le compte à rebours, « C'est l'heure. »,
  « Briser le cachet », le prix d'entrée (La Carte, 1 000 F) et l'adresse.
- Les couleurs, cires, papiers et sceaux sont ceux de `malettre/lettre.html`.
- Les fonds sont des **ambiances** générées par Mongazi pour la vitrine : jamais une
  vraie lettre, un vrai client, ni le produit lui-même.

### Le son

- `malettre_minuit_son.py` est **la seule vérité** du temps : il découpe les deux
  prises à leurs silences (31 phrases : 9 de Koffi, 22 d'Alimata), les pose, et
  écrit `minutage.json`. **Chaque plan lit ses phrases dans ce fichier** : l'image suit
  la voix, jamais l'inverse. Une prise qui n'a pas le bon nombre de phrases est
  **refusée**, et `malettre_minuit_ecouter.py` vérifie par l'oreille (Whisper, sans
  indice) que le n-ième morceau dit bien la n-ième phrase.
- ⚠️ Alimata est accélérée de 7 % (`atempo`), Koffi jamais (l'intime). On découpe
  **l'original**, puis on convertit les temps : accélérée, la pause entre « Ma lettre
  à… » et « Dès mille francs » passait sous le seuil et les deux phrases se collaient.
- Chaque phrase est nivelée (±6 dB) : les murmures de Koffi passaient sous le piano.
- Le piano **s'étouffe** pendant l'attente (passe-bas) et **se rouvre d'un coup** à
  minuit : le « wow » s'entend. Le premier temps fort de l'afrobeat (96,1 BPM) tombe
  sur « Ça, c'est Ma lettre à… ».
- Sous chaque phrase, la musique se retire de 12 dB (l'afrobeat est dense) et les
  bruitages de 7 dB, sauf les coups voulus de minuit.
- Master : **−14 LUFS, crête vraie −1,4 dBTP**, la voix devant (pire écart +1,6 LU).
  La vérification **remesure après l'AAC** et baisse le gain si la crête dépasse.

### Les pièges rencontrés

- ⛔ **`useCurrentFrame()` compte depuis le début de la `<Sequence>`**, pas du film.
  Les textes recevaient des secondes de la voix (le temps du film) : « Elle a 60 ans
  ce soir » arrivait 3 s trop tard. `useT()` rend le temps du film partout (le
  contexte `Decalage`, posé par chaque plan).
- ⚠️ Des lanternes posées en grille régulière font un motif : elles sont dispersées
  par `random()` (déterministe), sur les côtés ; la colonne du milieu reste à la marque.
- ⚠️ Le ffmpeg de Remotion n'écrit ni `f32le` sur la sortie standard, ni le filtre
  `fps` : tout passe par des WAV.
- ⛔ **`lightLeak({hueShift})` tourne à l'envers de l'intuition** (la matrice du shader est
  écrite en colonnes) : `335`, voulu « un peu vers le rouge », rendait minuit **vert-jaune**
  (74°). Mesuré : `20` donne l'ambre (34°) et le corail (10°) de la cire. Vu sur la planche
  tirée du MP4, invisible dans le code.
- ⛔ **Des éclats faits en triant les triangles d'une coque** sont creux et ont des bords en
  dents de peigne : vus de près au moment du « wow », ils ont été refaits en morceaux pleins
  (`ExtrudeGeometry` biseautée, le sceau en bosselage). Et l'ombre des morceaux qui volent
  haut faisait des taches grises : elle s'efface pendant le vol (`shadow-intensity`).
- ⛔ **`-shortest` de ffmpeg coupe à peu près** : la vidéo livrée avait perdu ses 4 dernières
  images avec une durée affichée juste. La vérification compte les images une à une.
- ⚠️ Rendre le son par Remotion évalue chaque image, 3D comprise (plus de cinq minutes ici) :
  `rendu_morceaux.mjs` accepte un WAV déjà masterisé en 4e argument et le pose tel quel.

### ⛔ Avant de publier

- **La plume est coupée en ligne** (2026-10-22) : la phrase « ou la plume l'écrit avec
  toi » vend une chose qu'on ne peut pas acheter. Attendre que la plume rouvre, ou
  enregistrer la variante sans la plume (`VOIX.md`).
- La licence Remotion : **on livre le MP4, jamais le projet**.
- ⏳ La version anglaise attend ses deux voix (`VOIX.md`, partie anglaise).

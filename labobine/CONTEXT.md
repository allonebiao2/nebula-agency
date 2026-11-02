# LA BOBINE · l'éditeur vidéo de NEBULA

## Ce que c'est

Le montage vidéo dans le navigateur, sur ordinateur comme sur téléphone. Décidé le 2026-11-02 : Mongazi veut
« créer exactement CapCut avec toutes ses options payantes, renommé ». **Le cadre posé et accepté** : on vise
toutes les **familles de fonctions** de CapCut et son **modèle payant** (relevé dans
`_knowledge/capcut-decortique.md`), mais **le code, le design, les textes, les icônes et les ressources sont à
nous**. On ne reprend rien de CapCut (ni code, ni effets, ni modèles, ni musiques, ni allure de ses écrans).

- Nom choisi par Mongazi : **LA BOBINE** (proposé parmi LE RACCORD, LE CHUTIER, LA BOBINE ; vérifiés aux registres
  le 2026-11-02 : `labobine.app` libre, `labobine.com` pris ; ⚠️ une app « La Bobine » de séances de cinéma existe).
- 🟢 **EN LIGNE depuis le 2026-11-02 : https://labobine.pages.dev** (projet Cloudflare Pages `labobine`, branche
  `main`). Vérifié en ligne : le corps de chaque fichier, les en-têtes (`no-cache` sur le code, `immutable` sur
  `vendor/`, sécurité), la 404, et **un export réel fait sur le site** (1280×720, filigrane, 0 erreur).
- ⏳ **Domaine `labobine.nebula-agency.online`** (déjà dans le `canonical`) : à brancher **par Mongazi** dans le
  tableau de bord (Pages → `labobine` → Custom domains). Le garde-fou de Claude Code refuse les changements de
  domaine, et nos jetons n'ont pas les droits DNS de toute façon.

## Les fichiers

| Fichier | Rôle |
|---|---|
| `index.html` | accueil (projets) + éditeur + dialogues |
| `app.css` | « salle de montage » : encre `#14110e`, lumière du projecteur `#ffd23f` ; Bricolage Grotesque, Instrument Sans, JetBrains Mono |
| `js/model.js` | le projet, les pistes, les clips, les opérations (diviser, rogner, déplacer, vitesse, superposition) et l'historique. **Sans DOM, testé dans Node** |
| `js/rendu.js` | **le moteur de dessin, un seul pour l'aperçu ET l'export** : ce qu'on voit est ce qui sort |
| `js/lecteur.js` | l'aperçu : un `<video>`/`<audio>` détaché par clip, composé sur la toile |
| `js/export.js` | l'export : décodage exact image par image (Mediabunny), son mixé hors temps réel (OfflineAudioContext), encodage WebCodecs, filigrane |
| `js/frise.js` | la frise : tête de lecture fixe au centre, la bande défile ; glisser, rogner, aimanter, pincer pour zoomer |
| `js/medias.js` · `js/stock.js` | import (durée, vignette, forme d'onde) · IndexedDB : **les fichiers restent sur l'appareil** |
| `js/offre.js` | Gratuit / Pro. `estPro()` rend **toujours faux** jusqu'à la vague 4 |
| `js/effets.js` | les 15 effets plein écran ; le « hasard » est un calcul (même image dans l'aperçu et l'export) ; `pulsation()` cale Battement et Flash sur le rythme |
| `js/stickers.js` | les 17 stickers, dessinés en `Path2D` dans une boîte de 100 × 100 (nets en 4K, rien à télécharger) |
| `js/rythme.js` | les temps d'une musique : flux spectral, tempo par autocorrélation, suivi par programmation dynamique (Ellis 2007) |
| `js/gif.js` | l'encodeur GIF : coupe médiane par image, tramage ordonné fixe, LZW, pixels inchangés transparents |
| `js/lut.js` | les LUT 3D `.cube` : lecture, application WebGL (atlas de tranches, trilinéaire), repli processeur identique |
| `js/catalogue.js` | la vidéo tirée d'un catalogue : fabrique un **projet ordinaire** (3 styles), calé sur la musique ; sans DOM, testé dans Node |
| `js/fabrique.js` | la fenêtre « Vidéo depuis mes produits » (catalogue d'une maison ou photos du commerçant) |
| `_catalogues.py` | lit les catalogues des maisons **à la source** (lecteurs de LE STANDARD) → `catalogues/<maison>/` (ignoré par git, refait à chaque publication) |
| `js/inverser.js` | lire une vidéo à l'envers : tranches décodées vers l'avant, réécrites à rebours ; le son retourné aussi |
| `vendor/mediabunny-1.65.0.min.mjs` | lecture/écriture MP4 et WebM, **MPL-2.0** (licence dans `vendor/`, créditée au pied de l'accueil) |

## Commandes

```bash
node labobine/_qc_modele.mjs  # sans navigateur : modèle, rythme, GIF, LUT, vidéo de catalogue (lancé aussi en tête de _qc.py)
python labobine/_catalogues.py # relit les catalogues des maisons (lancé aussi par _dist.py et par _qc.py)
python labobine/_qc.py        # contrôles Chrome (vagues 1 à 3 et 2 bis ; --sans-ia saute Whisper et MediaPipe quand le PC manque de mémoire) ; tests Node du modèle, du son, des visages et des légendes dans le scratchpad dans un vrai Chrome + examen du MP4 exporté (ffprobe), captures dans %TEMP%/labobine-qc
python labobine/_dist.py      # prépare labobine/_dist (on ne publie JAMAIS le dossier entier)
# publier (avec CLOUDFLARE_API_TOKEN de secrets/cloudflare.env) :
wrangler pages project create labobine --production-branch main   # une seule fois
wrangler pages deploy labobine/_dist --project-name labobine --branch main
```

## Les règles

- **Le verrou est à l'export, pas à l'outil** (appris de CapCut) : tout s'essaie ; le gratuit exporte avec le
  filigrane « LA BOBINE », en 720p ou 1080p, à 24, 25 ou 30 i/s. Pro : sans filigrane, 4K, 60 i/s, crédits IA.
- ⛔ **Aucune porte dérobée vers Pro dans le navigateur** : le droit Pro sera vérifié par le serveur après un
  paiement Mobile Money confirmé (vague 4).
- **Un seul moteur de dessin** (`rendu.js`) : ne jamais dessiner autrement dans l'aperçu et dans l'export.
- L'export demande les images **dans l'ordre exact** où `besoinsA()` les annonce : toute nouvelle couche visuelle
  doit passer par `besoinsA()` ET par `dessinerImage()`, sinon l'export se désynchronise.
- `vendor/` porte sa version dans le nom → cache `immutable` sûr ; `js/`, `app.css`, `index.html` en `no-cache`.
- **Ordre des couches**, le même partout : piste principale, superpositions, **effets**, **stickers**, textes, puis le
  filigrane (export seulement). Un effet ne voit que ce qui est sous lui.
- **Un effet ou un sticker ne tire jamais `Math.random()`** : le hasard est `hasard(n)` (un calcul), sinon l'aperçu et
  l'export ne montreraient pas la même image.
- Un clip sans fichier (`texte`, `sticker`, `effet`) a une **durée propre** : `M.SANS_MEDIA` / `M.aDureePropre()`.
  Tout nouveau genre de ce type s'y ajoute, sinon diviser et rogner le traitent comme une vidéo.

## Les vagues

1. ✅ **Le cœur du montage** (2026-11-02) : projets (créer, dupliquer, supprimer avec « Annuler »), 4 formats,
   import vidéo / photo / son (glisser-déposer), piste principale aimantée, superpositions, textes, sons, diviser,
   dupliquer, supprimer, rogner, déplacer, vitesse 0,25× à 4×, volume, fondus, 4 transitions (fondu enchaîné,
   passage au noir, glissement, zoom), 6 styles de texte et 5 animations, fond uni ou flouté, zoom lent sur photo,
   déplacer et agrandir sur l'aperçu (doigt, pince, molette), voix off au micro, annuler / rétablir, raccourcis
   clavier, sauvegarde automatique, export MP4 avec barre de progression et partage, installable (manifeste).
2. ✅ **Montage avancé** (2026-11-02, en ligne) : **images clés** (taille, position, rotation, opacité ; losanges dans
   le panneau et sur la frise ; partagées proprement quand on divise), **couleur** (8 filtres maison : Cotonou,
   Harmattan, Lagune, Nuit, Noir et blanc, Rétro, Éclat, Doux ; luminosité, contraste, saturation, température),
   **fond vert** (distance en chrominance, seuil et douceur), **masques** (cercle, rectangle, bande, inversables),
   recadrage, miroirs, 9 modes de fusion, **animations d'entrée et de sortie** (9 chacune), **6 transitions de plus**
   (glissement vers le haut, balayage, rideau, iris, flash blanc, tourbillon), **figer l'image**, **détacher le son**,
   remplacer le média, copier-coller les réglages, **garder le ton quand on accélère** (WSOLA, écrit ici : 440 Hz
   ralenti ou accéléré ×2 reste à 440 Hz), image de couverture PNG.
   **Vague 2 bis** (2026-11-02, le reste de la vague 2, tout sur l'appareil) :
   - **15 effets plein écran** sur leur propre piste (Pellicule, Cassette, Décalage RVB, Lueur, Vignettage, Bandes
     cinéma, Flou, Secousse, Battement, Flash, Lumière chaude, Paillettes, Pluie, Confettis, Lumières floues), appliqués
     à l'image composée, **sous** les stickers et les textes (qui restent lisibles). Posé sur un clip, l'effet en prend la fin.
   - **17 stickers dessinés ici**, pensés pour qui vend : flèches, « entourer » et « souligner » tracés à la main,
     étiquette de prix, PROMO, NOUVEAU, bandeau, bulle, épingle de lieu, validé, étoile, cœur, éclair, étincelle, feu,
     et l'émoji libre. Texte, couleurs, 6 mouvements en boucle (dont « bat au rythme »), entrée et sortie, images clés.
   - **Marqueurs de rythme** : « Trouver le rythme » sur un son (tempo exact sur 120, 96 et 140 BPM, temps à 8 ms
     près), touche **M** pour un marqueur à la main, les clips s'aimantent aux temps, et **« Caler les clips »** fait
     tomber chaque photo pile sur un temps (1, 2 ou 4 temps par photo ; une vidéo s'arrête sur le dernier temps atteint).
   - **Lire à l'envers** (vidéo et son), « Remettre à l'endroit » rend l'original, « Annuler » aussi.
   - **LUT 3D `.cube`** importées (Resolve, Premiere, LUT achetées) : WebGL, intensité réglable, repli processeur.
   - **Export en GIF animé** (240, 360 ou 480 px, 10 ou 15 i/s, filigrane en gratuit) et **du son seul** (M4A AAC,
     sinon WAV), par la même boucle d'images exactes que le MP4 (`parcourirImages()` dans `export.js`).
   - Contrôles : `_qc_modele.mjs` **39 verts** (dans le dépôt, plus dans un dossier temporaire) ; `_qc.py --sans-ia`
     **79 verts** dans un vrai Chrome (LUT mesurée au pixel, fondu au blanc relu à l'envers, 119,9 BPM sur une piste
     de clics, GIF relu par PIL, M4A par ffprobe). Le PC n'avait que 1 Go libre : le passage avec Whisper et
     MediaPipe a été coupé par Claude Code, d'où l'option `--sans-ia` (leur code n'a pas changé).
3. ✅ **IA de tous les jours** (2026-11-02), **tout sur l'appareil, rien n'est envoyé** :
   - **Sous-titres automatiques** : Whisper (MIT) via Transformers.js 4.3.2 (Apache 2.0, chargé depuis jsDelivr), modèle
     `onnx-community/whisper-base` (« précis », ~80 Mo) ou `whisper-tiny` (« rapide », ~40 Mo) téléchargé depuis Hugging
     Face **une fois** ; WebGPU si présent, sinon WASM. Légendes de 7 mots au plus, réparties au prorata des lettres,
     sur leur propre piste (`js/soustitres.js`).
   - **Détourage des personnes** et **cadrage qui suit les visages** : MediaPipe Tasks Vision 1.2.0 (Google, Apache 2.0),
     **rangé dans `vendor/`** avec ses deux modèles (`selfie_segmenter`, `blaze_face_short_range`) ; le moteur (14 Mo)
     ne se charge qu'au premier usage (`js/ia.js`). Le cadrage pose des images clés sur la position X et s'arrête au
     bord de l'image.
   - **Réduction du bruit** : porte spectrale écrite ici (FFT maison, gains lissés) : -13 dB de souffle, la parole
     garde son niveau. Le son nettoyé devient un nouveau média WAV, l'original reste intact (`js/audio.js`).
   - **Volume harmonisé** à l'export : mesure UIT BS.1770 écrite ici (pondération K, portes -70 et -10), cibles -14,
     -16 et -23 LUFS, crête plafonnée à -0,5 dBFS. Vérifié contre la norme (-3,01 LUFS) et contre FFmpeg (`ebur128`).
   - ⏳ **Voix de synthèse : reportée à la vague 4.** Elle demande un serveur payant ; sans comptes ni crédits, l'adresse
     serait ouverte à tous les abus.
4. 🟡 **L'argent** (2026-11-02, code prêt, serveur pas encore installé) : décisions de Mongazi : **Pro 1 500 F/mois ·
   12 000 F/an** (100 et 1 200 crédits IA), schéma `labobine` dans le projet Supabase partagé, nuage = le montage
   (pas les vidéos), paiement **SasPay** (même chemin que PISTE et MA LETTRE À…, `saspay.ts` identique). Connexion
   par e-mail (lien ou code), droits lus côté serveur, parrainage (7 jours chacun au premier paiement), pas d'essai
   gratuit, médias rebranchés par leur nom sur un autre appareil. Contrôle `_qc_caisse.mjs` : 31 verts.
   **Interface cachée (`OUVERT = false`) jusqu'à l'installation : `labobine/INSTALLER-COMPTES.md`, six étapes.**
   **Installé le 2026-11-02** (« installe le serveur ») : la base (6 tables RLS, 13 fonctions, rien pour `anon`) et
   les deux fonctions (refus vérifiés sans compte et sans signature), `LABOBINE_SITE` posé. **Reste** : le secret du
   webhook (Mongazi, SasPay), **la connexion par e-mail** et l'ouverture.
   ⛔ **Découvert à l'installation : sans SMTP, personne ne peut se connecter.** Le SMTP intégré de Supabase n'écrit
   qu'aux membres de l'équipe, 2 e-mails par heure (vrai aussi pour l'inscription à Boussole). Remède prêt :
   `python -I labobine/_installer_connexion.py` (clé Resend d'envoi seule sur `nebula-agency.online`, DKIM + SPF
   vérifiés ; adresses de retour ; modèles en français avec le code). **Refusé au garde-fou de Claude Code**
   (configuration partagée avec Boussole) : il faut l'accord explicite de Mongazi.
   ✅ **Appliqué le 2026-11-02** sur son accord : e-mails par Resend (`connexion@nebula-agency.online`, « NEBULA
   Agency »), 60 par heure, retours LA BOBINE ajoutés à celui de Boussole ; essai : **delivered**.
   ⚠️ Les confirmations d'e-mail sont activées : un nouveau client reçoit « Confirm signup », pas « Magic Link ».
   Le code fait **8 chiffres** (l'écran ne cite plus de nombre).
   Équipes : pas encore.
5. IA générative et modèles : image vers vidéo, avatars, musique IA, modèles, kit de marque.

## La vidéo depuis le catalogue du commerçant (2026-11-02, choisie par Mongazi)

L'angle que CapCut laisse : **partir des produits réels du commerçant** et sortir sa vidéo TikTok en un geste.
- **Deux portes** : le bouton « Vidéo depuis mes produits » de l'accueil (le commerçant ajoute ses photos, un nom et un
  prix par produit), ou le **lien d'une maison** : `https://labobine.pages.dev/#catalogue/hillary-m-styl`,
  `#catalogue/au-braise-dor`. Liens **non listés** (rien ne les annonce dans l'interface), `noindex` dans `_headers`.
- **Lu à la source, jamais recopié** : `_catalogues.py` passe par les **lecteurs de LE STANDARD**
  (`whatsapp-agent/lecteurs/`), qui lisent le fichier que le site sert déjà ; les photos sont celles que ce fichier
  nomme (`img`, champ `photo` ajouté à `Article` le 2026-11-02) ; les couleurs, celles de la feuille de style de la maison ;
  le numéro, celui de la **fiche** de la maison. Refait à chaque publication par `_dist.py` : un prix changé sur un site suit.
- ⛔ **Le numéro n'est jamais deviné** : la fiche d'Au Braisé d'Or est vide exprès (deux numéros dans le dépôt), donc
  le champ Contact reste vide et la vidéo finit sans numéro. Un contrôle le vérifie.
- **Un prix sur une étiquette ne ment jamais** : `prixCourt` = le prix exact, ou le plus bas précédé de « dès »
  (deux tailles, fourchette, normal/express), ou « Prix sur demande ». Un prix long passe en pastille, sans être coupé.
- **Un produit sans photo** devient une carte typographique sur le fond de la maison, jamais une image d'emprunt.
- **Trois styles** (`MODELES` dans `catalogue.js`) : La vitrine (étiquette de prix, glissements), La promo (prix en
  grand, éclat PROMO, battement et flash sur le rythme), L'élégante (lettres fines, fondus, lumières floues).
  Une pièce détourée (Hillary) se pose entière au-dessus de son nom ; une photo pleine remplit l'écran, en zoom lent.
- **La musique** : son rythme est trouvé sur l'appareil, chaque plan dure 1, 2, 4 ou 8 temps (le plus proche de la
  durée du style), les textes et les étiquettes suivent les plans **après** le calage, la musique s'arrête avec la
  vidéo, en fondu. 15 produits au plus.
- Le résultat est un **projet ordinaire** : tout se retouche dans l'éditeur, l'export garde le filigrane en gratuit.
- Contrôles : `_qc_modele.mjs` (fabrication) et `_qc.py` (le lien d'Hillary, celui d'Au Braisé d'Or, ses propres
  photos avec musique, export GIF avec les vraies photos, 390 px). ⚠️ Ils **lisent** les catalogues : on n'y recopie
  aucun nombre d'articles ni aucun prix.
- ⚠️ Les photos de plats d'Au Braisé d'Or sont générées par IA : gardées pour ce client seul (Mongazi, 2026-08-20).
  Pour toute autre maison, la règle reste entière : jamais une image générée présentée comme le catalogue.
- Ajouter une maison : un lecteur dans LE STANDARD (s'il n'existe pas), puis une entrée dans `MAISONS` de
  `_catalogues.py` (fiche, dossier des photos, feuille de style et noms de ses deux variables de couleur).

## Pièges rencontrés

- **MediaPipe écrit « INFO: Created TensorFlow Lite XNNPACK delegate for CPU. » sur le canal des erreurs** de la
  console : le QC l'écarte nommément, sans masquer les vraies erreurs.
- **Débruiteur : le 15e centile de l'énergie d'un bruit vaut 0,16 fois sa moyenne** (loi exponentielle). Sans la
  correction 1/-ln(0,85), le bruit est sous-estimé six fois et ne baisse que de 5 dB.
- Un test de détourage sur une mire **sans personne** rend une image noire : c'est le comportement voulu, mesurer
  l'image exportée sur un clip non détouré.
- Une commande Bash contenant des apostrophes françaises dans un script Python en ligne casse l'analyse du shell :
  écrire le script dans un fichier.

- **Un sticker entre en « rebond » par défaut : à son premier instant, sa taille vaut zéro.** Un contrôle qui le
  mesure doit avancer la tête de lecture d'au moins 0,5 s dans le clip.
- ⛔ **Le décodeur vidéo du navigateur n'a qu'une petite réserve d'images.** Garder une trentaine d'images décodées
  ouvertes (pour les réécrire à rebours) l'a **bloqué sans erreur** : l'inversion attendait pour toujours (QC du
  2026-11-02, 180 s). Règle : **recopier chaque image décodée dans une toile à nous, puis la fermer aussitôt** ;
  ne garder ouvertes que celles que le moteur dessine. `samplesAtTimestamps()` veut des instants croissants et peut
  rendre la même image pour deux instants voisins : on ne la ferme qu'une fois, quand une autre arrive.
- **Une LUT de 65 fait un atlas de 4 225 pixels** : au-delà de `MAX_TEXTURE_SIZE` (souvent 4 096 sur téléphone), on
  passe par le processeur, sans message.
- Le contrôle de design signale `.regle .marqueur::after` comme « bordure d'accent » : c'est le triangle du drapeau,
  dessiné par des bordures transparentes. Faux positif.

- **Dans un test Python, ne jamais nommer une variable `rouges`** (ou `verts`) : elle masque la liste des échecs.
- Les réglages animés passent TOUS par `reglerAnimable()` (panneau, glisser sur l'aperçu, pincer, molette) : un
  chemin qui écrit `c.cx` directement casserait les images clés.
- REA (2026-11-02, `analyze_web_bundle` sur le site en ligne) : 9 scripts, **aucun appel vers un serveur**. À refaire
  quand la vague 4 ajoutera les comptes et le paiement : ce sera alors la liste des seules portes de sortie.

- **Le Chromium de Playwright ne lit pas le H.264** : le QC lance `channel="chrome"` (le vrai Chrome installé).
- `python -I` **ignore `PYTHONIOENCODING`** : écrire les fichiers en UTF-8 soi-même (`open(..., encoding="utf-8")`).
- Au doigt, **un premier toucher sélectionne un clip, le suivant le déplace** : un clip sélectionné passe en
  `touch-action: none`, les autres laissent défiler la frise.
- Glisser un clip de la piste principale : il passe devant un voisin quand **son bord gauche** dépasse le milieu
  de ce voisin (comparer les milieux empêchait un clip long d'aller en tête ; attrapé par le test du modèle).

## Limites connues de la vague 1

- La vitesse change **aussi la hauteur du son** (pas d'étirement temporel).
- L'aperçu se cale « à peu près » (éléments `<video>`), l'export est exact.
- Le son de l'export est mixé en un seul tampon : une vidéo d'une heure demande beaucoup de mémoire.
- iPhone : le son des clips suivants peut rester muet dans l'aperçu (règle d'autoplay de Safari) ; l'export n'est pas touché.
- Vidéos HEVC d'iPhone : illisibles par Chrome sous Windows sans l'extension HEVC.
- Pas de service worker : l'application s'installe mais ne s'ouvre pas hors connexion.

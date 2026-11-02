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
| `vendor/mediabunny-1.65.0.min.mjs` | lecture/écriture MP4 et WebM, **MPL-2.0** (licence dans `vendor/`, créditée au pied de l'accueil) |

## Commandes

```bash
python labobine/_qc.py        # contrôles Chrome (vagues 1 à 3) ; tests Node du modèle, du son, des visages et des légendes dans le scratchpad dans un vrai Chrome + examen du MP4 exporté (ffprobe), captures dans %TEMP%/labobine-qc
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
   ralenti ou accéléré ×2 reste à 440 Hz), image de couverture PNG. Reste de la vague 2 : LUT (il faut WebGL),
   stickers, effets plein écran, marqueurs de rythme, inverser, export du son seul et en GIF.
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
4. L'argent : comptes, nuage, Gratuit / Pro / crédits, paiement Mobile Money, Équipes.
5. IA générative et modèles : image vers vidéo, avatars, musique IA, modèles, kit de marque.

## Pièges rencontrés

- **MediaPipe écrit « INFO: Created TensorFlow Lite XNNPACK delegate for CPU. » sur le canal des erreurs** de la
  console : le QC l'écarte nommément, sans masquer les vraies erreurs.
- **Débruiteur : le 15e centile de l'énergie d'un bruit vaut 0,16 fois sa moyenne** (loi exponentielle). Sans la
  correction 1/-ln(0,85), le bruit est sous-estimé six fois et ne baisse que de 5 dB.
- Un test de détourage sur une mire **sans personne** rend une image noire : c'est le comportement voulu, mesurer
  l'image exportée sur un clip non détouré.
- Une commande Bash contenant des apostrophes françaises dans un script Python en ligne casse l'analyse du shell :
  écrire le script dans un fichier.

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

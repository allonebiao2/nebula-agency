# 2026-10-02 — Vidéo de marque NEBULA, 30 s, en motion design (« le tour de magie »)

Mongazi veut une vidéo de 30 s en motion design pour NEBULA Agency : **émerveiller**, mettre
NEBULA AGENCY et le logo en valeur, vendre les **trois services** (vitrines, catalogues, outils
digitaux), et **donner envie qu'il réalise la même vidéo pour eux**. Voix off générée par lui
sur ElevenLabs. Il a d'abord demandé le script et le sexe de la voix, puis « un tout nouveau
script adapté au motion design ».

## Décisions

- **Voix : une femme.** Trois raisons : un tour de magie se dit à mi-voix (« Regardez bien »),
  une voix grave d'homme se bat avec les basses du sound design, et le contraste images
  spectaculaires + voix posée fait le haut de gamme. Léger accent d'Afrique de l'Ouest.
  Prise retenue : **Alimata** (ElevenLabs, **Eleven v4**, sorti le 2026-09-28), vitesse 1,08.
- **Le script, un tour de magie en trois temps** (vouvoiement : règle de la marque hors TikTok) :
  « Regardez bien. Tout ce que vous allez voir… Nébula le crée pour votre business. Une vitrine
  digitale… et vous devenez une marque. Un catalogue digital… et les commandes arrivent sur
  WhatsApp. Un outil digital… pensé pour VOTRE métier. Et même… cette vidéo. La vôtre est la
  prochaine. Écrivez-nous sur WhatsApp. Nébula Agency. Là où naissent les étoiles. »
- **La voix ne dit aucun chiffre** : prix, délai et numéros vivent à l'écran.
- Réponses de Mongazi aux questions de montage :
  - ses vraies réalisations sont montrées, **Angy Art, Au Braisé d'Or, Hillary M. Styl et
    Weinkeller en premier** ;
  - pour le prix, il m'a laissé choisir : **« Dès 50 000 F » seul** (le prix d'entrée de
    l'escalier ; plus la vidéo est belle, plus un petit commerçant croit que c'est trop cher
    pour lui) ;
  - **deux numéros** : appel **+229 01 96 74 07 32**, WhatsApp **+229 96 74 07 32** ;
  - **je fabrique tous les bruitages**, lui télécharge une musique libre de droits :
    « afro house » d'artissizm, **Pixabay** (licence Pixabay, éviter les morceaux au bouclier
    Content ID, garder le lien de la page).

## Ce qui a été construit

Composition Remotion **`nebula-30s`** dans `_studio-video/src/nebula30/`. Le détail technique est
dans le `README.md` du studio (section « NEBULA · la vidéo de marque »).

- **Le logo en couches** (`_outils/nebula30_logo.py`) : détouré par sa lumière, la galaxie, NEBULA
  et ses **six vraies lettres**, AGENCY et ses traits, le centre de l'étoile. Les animations
  utilisent les vraies lettres, jamais une police qui l'imite.
- **Les 9 sites photographiés en ligne** (`_outils/nebula30_captures.py`). ⚠️ Weinkeller ouvre
  « Offrir un cadeau » à chaque visite : masqué pour la photo.
- **Les vrais produits** : 6 champagnes de Weinkeller et 6 pièces d'Hillary, détourés, **avec
  leurs vrais prix** lus dans les sites ; « Poulet bicyclette · 3 000 F » d'Au Braisé d'Or (la
  sauce gombo a un prix variable, donc pas elle).
- **25 bruitages synthétisés** (`_outils/nebula30_bruitages.py`), contrôlés sur spectrogrammes
  (on ne les entend pas). Le son de notification n'imite pas celui de WhatsApp.
- **Le son** (`_outils/nebula30_son.py`) :
  - la voix sortait à −26,6 LUFS : elle est remontée à −16 LUFS et découpée dans ses silences
    mesurés ;
  - la musique est à 120 BPM : le gel tombe sur la chute, qui éclate après « …la prochaine » ;
  - la musique est baissée sous chaque phrase, **12,9 LU sous la voix** (médiane mesurée) ;
  - mastering final à −14 LUFS, −1 dBTP (`_outils/nebula30_master.py`).
- **Les instants viennent de la voix** : Whisper large-v3-turbo en local, mots recalés sur les
  bords mesurés de chaque phrase, écrits dans `src/nebula30/minutage.ts`.

## Ce que les planches ont attrapé (regardées avant le rendu)

- **« REGARDEZ » coupé en « REGARDE / Z »**, et **« CATALOGUE » sorti du cadre** : Syne 800 fait
  environ 1,1 em par capitale. Les titres sont passés à 96 px, sur des lignes coupées à la main.
- **Les étiquettes des sites en éventail** se chevauchaient : retirées, les captures montrent
  déjà les marques.
- **Les fiches en orbite passaient sur le bouton « Ajouter au panier »** que le doigt touche :
  l'orbite a été descendue.
- **La 3e commande arrivait pendant que les deux autres repartaient** : les commandes ont été
  avancées.
- **Une toile d'araignée de traînées** : l'orbite s'ouvre maintenant depuis le téléphone, et la
  traînée est plafonnée.
- **Le téléphone apparaissait avant que la poussière ait dessiné son contour** : il apparaît
  maintenant après.
- **« cette vidéo. » sur la règle de la timeline**, et **le message tapé par-dessus le mot
  « Message »** : corrigés.

## Le rendu et la vérification

- **Le premier rendu, à deux onglets, a été coupé par Claude Code** : il arrête ses tâches de
  fond quand la mémoire sature (8 Go, Chrome, Edge, Discord et VS Code ouverts). Avec l'accord
  de Mongazi, il a été relancé **à un seul onglet** : 3 tranches de 10 s, environ 110 s
  chacune, mémoire libre stable. `rendu_morceaux.mjs` accepte désormais ce réglage
  (3e argument : `1`).
- ⛔ **Piège Windows** : `NEBULA-30s.mp4` et `nebula-30s.mp4` sont le MÊME fichier, car les noms
  ignorent la casse. Le mastering a écrasé la vidéo qu'il lisait (il restait 4 images).
  Rien n'était perdu : il repart maintenant des morceaux, et la vidéo livrée s'appelle
  **`out/NEBULA-Agency-30s.mp4`**.
- **Vérifié sur le MP4 lui-même** (`_outils/nebula30_verifier.py`) :
  - 1080x1920, 30 i/s, 900 images, 30,00 s ;
  - −14,0 LUFS, −1,5 dBTP ;
  - **voix synchrone à 0 ms** (corrélation) ;
  - **la voix domine sur chacune des 14 répliques** (écart médian +0,7 LU entre le mélange et la
    voix seule) ;
  - planche tirée du MP4 conforme.
- Envoi à Mongazi : le fichier de 31 Mo n'est pas passé (délai de 30 s dépassé). La copie
  allégée de 13 Mo (`out/NEBULA-Agency-30s_leger.mp4`) est passée.

## Ce qui attend

- **L'écoute de Mongazi** : « Agency » est la seule syllabe douteuse (Whisper l'entend
  « Agencie », confiance 58 %).
- **La version TikTok** en « tu » : les textes sont prêts, il manque sa voix.
- **Le commit** : `Root.tsx`, `package.json` et le `README.md` du studio mélangent ce travail et
  celui, jamais commité, du « plan du dimanche » (2026-09-27). Lui demander quoi en faire.

# 2026-10-22 · MA LETTRE À… : le film « Minuit pile, pour maman » (16:9, YouTube, en 3D)

Suite de `2026-10-22-malettre-zero-gratuite-verre.md`. La vague 5 du produit (la pub), refaite à la demande de Mongazi.

## Ce que Mongazi a demandé

- Le matin : « la vidéo émotionnelle avec un effet wow qui mettra ma lettre en avant et donnera envie d'acheter ».
- Puis : horizontale (format YouTube), « ultra wow », 40 à 45 s ; l'émotion d'abord, puis la raison d'utiliser Ma
  lettre à…, ce qu'on propose, les autres occasions et les moments où l'on s'en sert, avec de l'humour, et l'envie
  d'essayer. Voix générées par lui (ElevenLabs), musiques choisies par lui (Pixabay), voix fortes et son égalisé.
- « chaque événement doit avoir son animation spéciale […] UTILISES LES TOUTE [les animations des vidéos du dossier
  ma lettre] ET EN PLUS INSPIRE TOI D'elles […] mais avant ça tu dois faire la vidéo » : le chantier des animations
  DU PRODUIT, une par occasion, vient après le film.
- « j'ai connecté le vrai remotion […] et blender aussi » : utiliser Blender pour la 3D, au maximum.

## L'histoire

Koffi, à Paris, écrit à sa mère pour ses 60 ans à Cotonou ; la lettre ne s'ouvre qu'à minuit pile. Trois actes :
l'histoire (la voix de Koffi, le piano), MINUIT (sans voix, le wow), puis la vente (la narratrice, l'afrobeat) : la
marque, l'heure choisie, l'impossible à ouvrir, la plume, l'habillage, la Saint-Valentin, les excuses, la demande, la
soirée entre potes, et la fin « Ma lettre à… Dès mille francs. Tape un prénom : ta lettre commence. »

- **La lettre lue est une vraie lettre de la plume** (« Un bol de bouillie à 5 heures »), écrite à partir d'une fiche
  inventée et relue : aucun fait ajouté (`scratchpad/video/lettres.json`, version anglaise « Hot porridge at 5 am »).
- **Koffi est un personnage, pas un client** : la vente est dite par une autre voix. Pas de faux témoignage.
- Le script (avec les balises ElevenLabs v3/v4) et sa variante sans la plume : `_studio-video/src/malettre-minuit/VOIX.md`.

## Les outils : Blender essayé, Three.js retenu

- Blender 4.5.15 portable installé dans `D:\outils\` (empreinte vérifiée). **EEVEE plante** sur l'Intel HD 5500
  (« Out of resource error », `EXCEPTION_ACCESS_VIOLATION`) ; **Cycles sur le processeur : 417 s par image**, soit
  16 jours pour ce film. L'extension Blender de Claude Desktop est une télécommande, et Claude Desktop n'est pas
  Claude Code. Higgsfield à 0 crédit, WaveSpeed à 0,039 $.
- **Retenu : la vraie 3D en Three.js dans Remotion** (`@remotion/three`, `@react-three/fiber` 9.8.2, `three`
  0.180.0, `@remotion/effects`, `@remotion/transitions`, `@remotion/media`, versions figées), environ 0,4 s par image :
  le cachet en relief (une géométrie), ses trois éclats, l'enveloppe à doublure damassée, les alliances, le halo.
  `HtmlInCanvas` exige Chrome 149 : indisponible.

## Le son

- Les deux voix de Mongazi (`_partage/voix de koffi tony.mp3` : 9 phrases ; `_partage/voix de alimata.mp3` : 22),
  découpées à leurs silences, nivelées (±6 dB), traitées (coupe-bas, présence, compression, sifflantes), posées.
  Alimata accélérée de 7 %, Koffi jamais ; on découpe l'ORIGINAL puis on convertit les temps (accélérée, deux phrases
  se collaient).
- Le piano (nastelbom, Pixabay 598096) s'étouffe pendant l'attente et se rouvre d'un coup à minuit ; l'afrobeat
  (sonican, Pixabay 481253, 96,1 BPM) pose son premier temps fort sur « Ça, c'est Ma lettre à… ».
- La musique se retire de 12 dB sous chaque phrase, les bruitages de 7 dB (sauf les coups de minuit). 20 bruitages
  synthétisés (aucun fichier tiers). Master −14 LUFS, crête vraie −1,4 dBTP, la voix devant (pire écart +1,6 LU).
- **La parole seule fait 41 s** : le film fait 56,3 s, au-dessus des 40 à 45 s demandées. Pour raccourcir, il faut
  réécrire le script, pas presser les voix.

## Ce que les planches ont montré (et ce qui a été corrigé)

- ⛔ Les textes arrivaient en retard : `useCurrentFrame()` compte depuis le début de chaque plan, alors que les
  instants viennent de la voix (temps du film). « Elle a 60 ans ce soir » 3 s trop tard. Corrigé par `useT()` et le
  contexte `Decalage`, posé par chaque plan.
- Le voile trop lourd, la gerbe d'étincelles derrière le téléphone, les éclats du cachet pas assez bordeaux, la
  plume qui écrivait tout d'un coup (ligne à ligne désormais), les alliances, les lanternes en grille (dispersées
  par `random()`), la marque.

## Ce que le MP4 a montré (planche tirée du fichier, puis images en pleine résolution)

- ⛔ **Minuit virait au vert-jaune** (14,4 à 14,9 s) : `lightLeak({hueShift: 335})`, voulu « un peu vers le rouge ».
  La matrice du shader est écrite en colonnes, la rotation tourne à l'envers : 335 donne 74° (vert-jaune), 20 donne
  l'ambre et le corail de la cire. Calculé, puis corrigé.
- ⛔ **Les éclats du cachet étaient creux, aux bords en dents de peigne** (chaque triangle de la coque allait au
  morceau de son angle), et leur ombre faisait des taches grises sur l'enveloppe. Refaits en morceaux PLEINS
  (secteurs extrudés, arêtes arrondies, tranche mate, le sceau en bosselage) ; l'ombre s'efface pendant le vol.
- **L'enveloppe traversait l'écran en 0,3 s** et finissait sur le mot « Cotonou » : elle plonge, ralentit et se pose
  au-dessus de Cotonou ; les mots de l'envol s'effacent avant le fondu (« Paris » se lisait à travers le téléphone).
- ⛔ **La vidéo livrée avait perdu ses 4 dernières images** (`-shortest` de ffmpeg, imprécis), avec une durée affichée
  juste. La vérification compte désormais les images une à une (3 381).
- Le son rendu par Remotion évaluait chaque image, 3D comprise (plus de cinq minutes pour un son remplacé ensuite) :
  `rendu_morceaux.mjs` prend le master en 4e argument.

## Whisper a écouté les 31 phrases

`_outils/malettre_minuit_ecouter.py` : la prise seule (le morceau découpé est-il la bonne phrase ?) et le film (la phrase
s'entend-elle par-dessus la musique ?), sans indice. **30 sur 31 confirmées** dans les deux écoutes ; l'ordre des
morceaux est juste. « Maman… » (Koffi, juste après minuit) est entendu parfaitement dans la prise, mais l'écoute du
film entier ne le trouve pas, alors que la mesure de niveau donnait la voix devant : Whisper saute volontiers un mot
isolé qui suit une plage de musique. Le script réécoute désormais DE PRÈS toute phrase manquée : réécouté ainsi,
« Maman… » est entendu (1,00). **Verdict final : les 31 phrases sont les bonnes et s'entendent dans le film.**
⚠️ La première version écoutait les 62 morceaux un par un : Whisper traite toujours 30 s d'audio, même pour une
seconde, et l'écoute dépassait 25 minutes. Trois passages au mot suffisent (environ 6 minutes, chargement compris).

## Propagé ailleurs

- **L'ancienne pub (`malettre-pub/`, 2026-10-21) finissait sur « Gratuite pour commencer »**, faux depuis le matin :
  écran, script de voix et textes d'annonce passés à « Dès mille francs » / « Dès 1 000 F » (`src/malettre/`). Ses
  coupes de la plume attendent que la plume rouvre.
- Les fonds du film étaient copiés à la main : `malettre_minuit_preparer.py` les produit désormais depuis les
  originaux de Mongazi (`_partage/ma lettre/fonds/<zone>-paysage.png`), et le cachet depuis `malettre/logo/`.
  **Vérifié : il refait tous les fichiers du film à l'octet près** (empreintes comparées ; le réglage JPEG d'origine,
  qualité 93, retrouvé en essayant les combinaisons).
- La composition d'essai `essai-3d` est retirée.

## Ce qui reste

- ⛔ **La plume est coupée en ligne** : le film dit « ou la plume l'écrit avec toi ». Ne pas le publier avant que la
  plume rouvre, ou enregistrer la variante sans la plume.
- ⏳ La version anglaise (deux voix à enregistrer).
- **Le chantier suivant** : les animations du PRODUIT, une par occasion, tirées des onze vidéos de référence.

# 2026-11-17 · Les 10 outils de motion graphics de Mongazi : retrouvés, contrôlés, installés

**La source** : une liste collée par Mongazi. C'est le résumé d'une vidéo YouTube, et plusieurs noms y étaient mal
transcrits (« Lemo Opus Car » pour `lemo-opuscar`). Le 2026-11-17, chaque nom a été retrouvé sur l'API GitHub. La
licence a été lue avant toute installation. Le contenu a été contrôlé : crochets (hooks), serveurs MCP, appels réseau,
accès aux secrets et consignes données à l'agent. Rappel : un plugin ou une compétence a les mêmes droits que nous sur
le PC et peut donc lire `secrets/`.

| Dans sa liste | Le vrai dépôt | Licence | Verdict | Où |
|---|---|---|---|---|
| Lemo Opus Car | `lemomo-ai/lemo-opuscar` (99 styles) | code MIT · fiches CC BY-NC 4.0, plus une permission pour nos films · films CC BY 4.0 | ✅ installé | plugin `lemo-opuscar@lemolab`, bibliothèque dans `C:\Users\USER\lemo-opuscar` |
| Three.js | `three` 0.180.0 | MIT | ✅ déjà là | `_studio-video/` (film « Minuit pile ») |
| Pixel FX | `patch-gg/pixelfx` (244 effets) | MIT | ✅ installé | plugin `pixelfx@pixelfx` |
| Blender (MCP) | `ahujasid/mcp-for-blender` | MIT | ⛔ pas installé | voir plus bas |
| Awesome Opus 5.5 Videos · Opus Video Prompts | `yihui-dev/awesome-opus5-5-videos` · `joeseesun/opus-video-prompts` | MIT · aucune licence | 📖 références, rien à installer | liens ci-dessous |
| Claude Animation Base | `JohnHeibel/ClaudeAnimationBase` | MIT | ✅ installé comme référence | `D:\outils\ClaudeAnimationBase` |
| React Rapier | `@react-three/rapier` 2.2.0 | MIT | ✅ installé | `_studio-video/` |
| React Three Postprocessing | `@react-three/postprocessing` 3.2.2 + `postprocessing` 6.39.6 | MIT · Zlib | ✅ installé | `_studio-video/` |
| Librosa | `librosa` 1.0.1 (numba 0.65.1) | ISC | ✅ installé | Python 3.13 du PC |
| Video Shotcraft | `Vincentwei1021/video-shotcraft` (124 fiches de plans) | Apache-2.0, sons Freesound sous leur propre licence | ✅ installé | compétence `~/.claude/skills/video-shotcraft` (99 Mo) |

Dans `_studio-video/`, l'installation s'est faite en versions figées (`--save-exact`). Remotion 4.0.512, React
19.2.8, `@react-three/fiber` 9.8.2 et `three` 0.180.0 n'ont pas bougé, et `tsc` passe.

Coût en contexte, mesuré par `claude plugin details <nom>` : pixelfx ~310 jetons et lemo-opuscar ~393 jetons à chaque
session. Aucun des deux n'a de crochet, de serveur MCP ou d'agent.

## Lemo Opuscar : ce que la licence permet

- **Nos films et ceux des clients sont permis.** La licence ajoute à la CC BY-NC une permission gratuite et
  irrévocable : lire, suivre, copier et adapter les fiches pour faire nos propres films, films commerciaux et films de
  clients compris, et les livrer dans les fichiers du projet.
- ⛔ **Jamais ses fiches (STYLE.md, guides, prompts d'images), même adaptées, dans le dépôt PUBLIC `nebula-agency`.**
  Ce serait les partager au-delà du film. Elles restent dans `C:\Users\USER\lemo-opuscar` et `~/lemo-my-styles/`.
- ⛔ **Jamais dans un produit** (LE MONTEUR, LA BOBINE, une appli vendue) sans leur licence commerciale. Pour la
  demander : lemomo.studio@gmail.com.
- **Le crédit** : « Lemo-Opuscar by Lemomo (LemoLab) », le lien du dépôt, la licence (CC BY-NC 4.0 pour les fiches,
  CC BY 4.0 pour les films), et dire si on a modifié. Deux styles ont aussi un auteur à nommer : Memphis Diorama
  (EianLu) et Crayon World 3D (2nd1st).
- Six voix de films de démonstration sont exclues de toute licence : ne jamais les extraire.
- **L'installation se fait en deux temps.**
  - `setup.sh` clone la bibliothèque (clone partiel, 32 Mo au départ).
  - `setup.sh deps` installe ses paquets : Node, le navigateur de rendu de Playwright, Python.
  - ⚠️ Le contrôle automatique a refusé que Claude lance seul ce script tiers. **Mongazi l'a autorisé** le 2026-11-17
    (« oui j'autorise »).
  - **Résultat, le même jour** : le niveau `core` est installé (paquets Node, Chrome Headless Shell 153 dans
    `AppData\Local\ms-playwright`, Python). La bibliothèque pèse 315 Mo. Les niveaux `voice` et `music` s'installent
    quand un film en a besoin : `sh setup.sh deps voice music`.
- Il exige ffmpeg 7 ou plus : le PC a ffmpeg 9.0.2.

## Video Shotcraft

- Ce n'est pas une place de marché de plugins (il n'a pas de `marketplace.json`, `claude plugin marketplace add`
  échoue). Il a donc été installé comme compétence : le dépôt contrôlé a été copié dans `~/.claude/skills/video-shotcraft`.
- Son gabarit est en **Remotion 4.0.484**. On applique ses fiches de plans dans `_studio-video/` (4.0.512, figé)
  plutôt que de créer un projet à part, ce qui demanderait un `npm install` de plus. ⛔ Jamais Remotion 5 sans relire la
  licence.
- Il sait publier sur les réseaux sociaux (`publish/upload_post.py`, API Upload-Post, clés absentes). ⛔ On ne s'en
  sert pas : Mongazi publie lui-même.
- Ses sons viennent de Freesound, chaque fichier sous sa propre licence. Il faut garder le manifeste et créditer les
  CC BY. ⛔ Aucun son NC.

## Pixel FX

- Ses effets ont une graine fixe : son `tools/check.mjs` chasse le hasard non semé. Ils sont donc compatibles avec
  Remotion si on les pilote par le numéro d'image.
- ⛔ Sa compétence propose, à la fin, de publier le jeu sur Patch en installant `pch` (`curl | sh` ou `irm | iex`). On
  ne le fait pas.

## Claude Animation Base

- Le code est MIT, mais **Clawd est la mascotte d'Anthropic**. ⛔ Elle n'apparaît jamais dans nos vidéos ni chez un
  client : la licence MIT du dépôt ne donne aucun droit sur le personnage d'Anthropic.
- On garde la technique pour NOS personnages, le mini-Mongazi et l'IA trop sûre d'elle des épisodes. Cette technique,
  c'est la peinture à la main en code (p5.js + p5.brush), les expressions et le guide d'animation (`ANIMATION_GUIDE.md`).
- Le rendu passe par le Chrome du PC (`puppeteer-core`, sans téléchargement de navigateur). `node_modules` : 72 Mo.

## Blender MCP : pourquoi pas

Blender ne rend pas sur ce PC : EEVEE plante sur l'Intel HD 5500, et Cycles en processeur met 417 s par image. En plus,
le serveur MCP se chargerait à chaque session. La 3D passe par Three.js. On l'installera le jour où il y aura une
machine avec une carte graphique (5 minutes).

## Rapier et postprocessing dans Remotion

- ⚠️ **Remotion rend les images dans le désordre, sur plusieurs onglets.** Une physique qui avance « en temps réel »
  donne une vidéo différente à chaque rendu. On précalcule donc la simulation (pas fixe, image par image) et chaque
  image lit sa position.
- ⚠️ **Les effets de lumière (halo, flou de profondeur, grain, glitch) coûtent cher sur l'Intel HD 5500.** Il faut
  mesurer le temps par image au premier usage. « Minuit pile » tournait à 0,4 s par image, sans effets.

## Librosa

`librosa.beat.beat_track` et `librosa.onset.onset_detect` donnent les temps forts d'une musique. On les écrit dans un
JSON que la composition lit, comme `minutage.json`. Test : il trouve 117 bpm sur un signal à 120.

## Les références (rien à installer)

- `yihui-dev/awesome-opus5-5-videos` (MIT) : des vidéos virales faites avec Opus 5.5, avec leurs prompts.
- `joeseesun/opus-video-prompts` : sans licence, donc lecture seule. On s'inspire, on ne recopie pas.
- Vu en passant, pas installé : `nexu-io/openmotion` (Apache-2.0), qui transforme une vidéo de référence en motion
  graphics modifiable.

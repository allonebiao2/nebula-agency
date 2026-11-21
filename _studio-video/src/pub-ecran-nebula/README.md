# Pub écran NEBULA · « écran filmé, motion design » (21/11/2026)

La pub de NEBULA d'après les deux références décortiquées dans `references/PUB-ECRAN-MOTION.md`. La barre de qualité,
c'est **B** : un seul élément par phrase sur la nuit, des entrées douces (0,4 s, fondu, échelle 0,96 → 1, flou → net),
un halo violet qui respire, une seule couleur forte. La voix est celle de Mongazi.

| Composition | Format | Ce que c'est |
|---|---|---|
| `PubEcranNebula169` | 1920 × 1080, 30 i/s | le film tel quel |
| `PubEcranNebulaTikTok` | 1080 × 1920, 30 i/s | le même film sur un moniteur fin, dans une pièce sombre : la lumière de l'écran sur le mur et la table brillante (son reflet), l'enseigne néon au mur, l'accroche en haut, les sous-titres mot à mot |

## La chaîne, dans l'ordre

```bash
python _outils/pub_ecran_captures.py      # la vraie capture d'aubraisedor.com au téléphone (une fois, travail lourd)
python _outils/pub_ecran_preparer.py      # l'enseigne néon, les bruitages, la musique, le grain → public/pub-ecran-nebula/
python _outils/caler_voix.py public/pub-ecran-nebula/voix-montee.wav   # la voix nettoyée et calée → minutage.json
python _outils/pub_ecran_planche.py       # une image par plan, les deux formats : À REGARDER avant de rendre
npm run rendu:pubecran                    # le son une fois, puis les deux MP4 par morceaux, à UN onglet
```

`_outils/pub_ecran_rendu.py` rend d'abord le son (sans image), le mesure et pose un limiteur doux si une crête dépasse
-1 dBTP ; puis l'image par morceaux de 300 (`rendu_morceaux.mjs`, un onglet, reprise après une chute de Chrome).
⚠️ Après un changement de la vidéo, effacer `out/morceaux/<composition>/` (le son, lui, est refait à chaque rendu).
Les fichiers à envoyer pèsent 45 Mo (8 Mb/s) ; le rendu brut (~37 à 78 Mb/s, le grain coûte cher) reste en `-master.mp4`.

Sorties : `out/NEBULA-Pub-Ecran-16x9.mp4` et `out/NEBULA-Pub-Ecran-TikTok.mp4`. On livre le MP4, jamais le projet
(licence Remotion).

**La version Facebook, sans la musique** (21/11) : `python _outils/pub_ecran_rendu.py facebook` refait seulement le
son, sans la piste de musique (`musique: false`, passé en props par un fichier JSON), le ramène à -16 LUFS et le pose sur
l'image de la version TikTok copiée telle quelle (`-c:v copy`) → `out/NEBULA-Pub-Ecran-Facebook.mp4`. La synchro est
vérifiée par corrélation avec la version TikTok (0 ms). Pourquoi : le Content ID de la musique n'est pas vérifié, et
Facebook peut couper tout le son d'une vidéo dont la musique est déposée.

## Le minutage : un seul fichier, jamais écrit à la main

- `script.json` : le TEXTE DIT par Mongazi (il fait foi pour l'alignement et les sous-titres). On change une ligne, on
  relance `caler_voix.py`, la vidéo suit.
- `minutage.json` : écrit par `caler_voix.py` (une entrée par ligne : début, fin, chaque mot et son temps). Les
  composants demandent « quand commence le mot X de la ligne N » (`quand(11, 'arrive')`), jamais une seconde.
- `caler_voix.py` : convertit la voix en WAV 48 kHz, la nettoie (passe-haut 80 Hz, débruitage léger `afftdn`,
  -16 LUFS), la transcrit (Deepgram nova-3, la réponse est gardée dans `<voix>.deepgram.json`), puis aligne chaque mot
  du texte dit sur les mots entendus, en souplesse. Il liste les écarts (« la » dit, « le » entendu) : le texte dit est
  gardé à l'écran. `--provisoire` pose un minutage estimé quand la voix n'existe pas encore.
- La fin dure 1,5 s après le dernier mot (`QUEUE` dans `donnees.ts`).
- Le compte à rebours de Noël (« J-34 ») se calcule depuis `DATE_PUBLICATION` (`donnees.ts`) : la changer si la pub
  sort un autre jour.

## Ce qui est à l'écran, et d'où ça vient

- **Aucune image générée par IA.** Les produits (robe, sac, parfum, escarpins) sont des dessins au trait en SVG
  (`Dessins.tsx`), avec des prix d'exemple.
- **La preuve** (ligne 8) est une vraie capture de https://aubraisedor.com, notre client livré, au téléphone (390 px).
  ⛔ **Polaris, 21/11 : on n'y descend jamais jusqu'à la grille des plats**, faite des photos GÉNÉRÉES de juillet (une
  pub ne les montre pas, même un instant). Le plan entre dans la VRAIE photo du haut (la sauce krinkrin, 1 500 F,
  « Ajouter au panier ») ; l'image est coupée au-dessus de la grille, et la 4e vignette du carrousel des sauces, qui
  n'est pas l'une des trois vraies photos, est cachée. Mongazi a l'accord d'Au Braisé d'Or pour paraître dans la pub. ⛔ Jamais l'aperçu non payé d'un prospect.
- **Pas le logo de WhatsApp** : bulle et icône de discussion génériques. Le mot « WhatsApp » n'est que dans la voix,
  les sous-titres et l'accroche.
- **Le numéro** est lu dans `src/tiktok-20-11/donnees.ts` (celui du site public), jamais écrit ici.
- **L'enseigne néon** suit le dessin d'`_outils/avatar_studio.py` : NEBULA violet (172, 82, 255), AGENCY cyan
  (40, 222, 255), Arial Black, des tubes au cœur clair et une lueur. Chaque mot s'allume sur le mot dit. Dans la pièce,
  l'écran s'éteint quand l'enseigne du mur s'allume : il ne reste qu'elle.
- **Le numéro** reste aussi en ligne discrète sous l'enseigne, de son allumage jusqu'à la fin (Polaris : il ne restait
  que 1,7 s), comme la ligne finale de la référence B.

## Le son

- La voix de Mongazi, nettoyée, à -16 LUFS.
- La musique : **« Piano Jazz Rainy Night », d'Alex Morgan, Pixabay n° 564276**, licence *Pixabay Content License*
  (usage commercial permis, sans attribution obligatoire ; le fichier seul ne se redistribue pas, il reste hors dépôt).
  Source : `_partage/alex-morgan-piano-jazz-rainy-night-music-564276.mp3`, coupée et ramenée à -28 LUFS, baissée encore
  sous la voix. ⚠️ « Content ID » pas vérifié pour ce morceau : le faire avant une publication sur YouTube ou Facebook.
- Les bruitages, tous synthétisés par `_outils/pub_ecran_preparer.py` (aucun fichier tiers) : pop (la bulle), clic (le
  doigt), carillon doux (la commande), souffle (le grand texte), claquement et bourdonnement du néon, glisse, tic, éclat.
- Polaris, 21/11 : le souffle de « tout de suite » et le carillon de la commande passent à 0,25 (ils étaient au
  niveau de la voix), le pop de la bulle à 0,4 (il couvrait « il »).
- ⛔ Rien de la musique ni des sons des références.

## Les pièges

- **Un seul travail lourd à la fois** (8 Go) : capture, planche, rendu, jamais deux ensemble, et aucun navigateur de
  test ouvert pendant un rendu.
- Le néon et le grain sont des PNG **transparents** (alpha = lumière) : un mode de fusion « screen » ne traverse pas un
  groupe isolé par une opacité ou un flou, et le noir de l'image s'y voyait.
- `public/` est hors dépôt : la voix, la musique, la capture, l'enseigne, les bruitages se refont par les commandes
  ci-dessus (la voix montée par le directeur reste dans `public/pub-ecran-nebula/voix-montee.wav`).

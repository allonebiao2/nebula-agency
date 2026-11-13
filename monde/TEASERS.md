# LES TEASERS · une vidéo publicitaire pour chaque boutique virtuelle (demandé par Mongazi le 2026-11-13)

> **Ses mots, tels quels** : « à garder en mémoire aussi : pour chaque boutique ou structure virtuelle qu'on
> fera, on fera une vidéo teaser publicitaire pour cette structure, de leurs boutiques, avec des plans,
> mouvements de caméra à l'intérieur, plans, etc., ultra réaliste ».
>
> **Statut : 💤 à faire pour chaque lieu**, le premier étant le salon d'HILLARY M. STYL. Il ne passe pas
> devant le mini-objectif réalisme en cours (`REALISME.md`) sans que Mongazi le demande ; d'ailleurs le
> teaser sera d'autant plus beau que le réalisme sera avancé (les robes en 3D surtout, R7).

## Ce que j'en comprends

- **Un livrable de plus par lieu** : une vidéo courte qui donne envie d'y entrer (et d'acheter), faite de
  **plans de cinéma tournés dans le lieu lui-même** : travellings, panoramiques, gros plans sur les pièces,
  passages d'une salle à l'autre, la porte qui s'ouvre, les projecteurs qui s'allument.
- **Ultra réaliste** : c'est le même lieu 3D que la visite, filmé avec les moyens qu'on n'a pas en direct.

## Les deux façons de la tourner (à trancher au premier teaser)

1. **Filmer la page elle-même, image par image** : une horloge fixe (60 images/s exactes), une
   trajectoire de caméra écrite à l'avance, Playwright qui enregistre chaque image en qualité maximale
   (rendu cinéma, lumière cuite, plus de résolution qu'un téléphone n'en tient), puis le montage. Ce qu'on voit
   est ce que le client verra : honnête et réutilisable pour chaque lieu.
2. **Rendre le lieu dans Blender avec Cycles** (le décor s'exporte déjà : `monde/_outils/exporter_decor.py`) :
   un vrai calcul de lumière à chaque image, donc le plus photographique. Plus long à rendre (ce PC : 8 Go,
   processeur seul) et il faut exporter aussi les personnages et les pièces.

**Le montage** : `_studio-video/` (Remotion 4.0.512) pour les titres, le rythme et la musique.
⚠️ Licence Remotion : **on livre le MP4, jamais le projet** (`CLAUDE.md`). ⚠️ La musique : une licence
qui autorise la publicité (Pixabay le permet, sans redistribuer le morceau seul).

## Les règles qui s'appliquent

- ⛔ Les pièces montrées sont **les vraies pièces du client**, avec leurs vraies photos (règle NEBULA : une
  image générée ne devient jamais le catalogue) ; les prix, s'ils apparaissent, sont **lus** dans le
  catalogue.
- ⛔ Aucun visage réel sans accord écrit (Hillary seulement avec le sien) ; les visiteuses sont des
  personnages inventés, jamais présentées comme de vraies clientes.
- Le bandeau « MAQUETTE » n'apparaît pas dans un teaser : un teaser ne se tourne que sur un lieu fini.

# 2026-11-11 · LE MONTEUR, l'agent de montage vidéo

## La demande

Mongazi, à partir d'une capture de la vidéo YouTube « I investigated 8 GitHub repos that print money » qui
présente OpenMontage : « une app, un agent capable de monter n'importe quel type de vidéo lui-même ». Puis son
objectif (/goal), répété deux fois :

> « L'agent IA dans l'app ou le SaaS doit pouvoir monter tout type de vidéo, quels que soient le type ou la demande
> du client ou moi, des montages et des vidéos qui valent toutes minimum 10 000 euros. Et même sans rush, l'agent
> doit pouvoir monter la vidéo en cherchant, en partant de rien, juste à partir d'une demande. »

## La recherche

Quatre dépôts lus dans leur code, une quarantaine relevés : `_knowledge/montage-ia-decortique.md`.
**OpenMontage est en AGPL-3.0** : bon studio interne, interdit au cœur d'un produit en libre-service fermé.
À Mongazi qui demandait s'il suffisait : non (licence, validation humaine à chaque étape, montage de rushes en
« beta »). Il a choisi **l'appli** (option B).

## Ce qui est construit

Un projet **privé**, hors de ce dépôt public : `C:\Users\USER\nebula-montage` (git local). Le dépôt GitHub privé
n'a pas pu être créé automatiquement (refusé par le garde-fou de Claude Code) : **Mongazi le crée**.

- **Avec rushes** : lecture (transcription mot à mot Deepgram, plans, visages, netteté, silences, planches), un
  réalisateur Claude Opus 5.5 qui rend un plan JSON validé et recalé entre les mots, une fabrication ffmpeg exacte à
  l'image et à l'échantillon, un banc de 16 mesures. Essai : une interview NASA de 3 min (domaine public) devenue un
  short vertical de 40,5 s pour 0,18 $, banc 16/16.
- **Sans rush** : un scénariste Claude, une voix off Deepgram Aura-2 (Agathe), une collecte d'images (Pexels et
  Pixabay si une clé existe, sinon FLUX.2 par Cloudflare Workers AI, gratuit), un mouvement de caméra sur chaque
  image, un sound design sobre, chaque licence notée. Essai : une pub TikTok de 30 s pour MA LETTRE À… à partir de
  la seule demande.
- **Le relecteur** : un second appel, neuf, qui note la vidéo sur 8 critères (accroche, histoire, rythme, image,
  artefacts d'IA, texte, son, exactitude), rend un plan corrigé et les images à refaire ; deux corrections au plus.

## Ce que le banc a attrapé

- Une cadence de 29,83 i/s au lieu de 30 : le son d'un segment commençait en retard, le collage décalait la suite.
  Corrigé : chaque segment a un nombre exact d'images et d'échantillons (`aresample=async=1:first_pts=0`).
- Le relecteur attrapera ce que le banc ne mesure pas : une image générée de tasse à deux anses en est l'exemple.

## Ce qui attend Mongazi

1. Créer le dépôt GitHub **privé** `nebula-montage`.
2. Choisir le nom du produit.
3. Une clé **Pexels** gratuite (vraies vidéos libres de droits au lieu d'images générées).
4. Un vrai rush et une demande pour un essai.

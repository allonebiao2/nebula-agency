# PUBS VIDÉO IA · la branche du cerveau

> Ouverte le 2026-11-16 à la demande de Mongazi. Tout ce qui touche à l'offre de **pubs vidéo générées par IA** :
> ce qu'on vend, comment on le fabrique, à quel prix, et chaque pub produite.
> Lire ce fichier avant toute nouvelle pub.

## L'offre en une phrase

Une pub vidéo pour TikTok, Reels, les statuts WhatsApp et Facebook, **sans tournage** : les personnages, les décors et
les voix sont générés ; le produit du client, lui, est le vrai.

## Qui fait quoi (décidé par Mongazi le 2026-11-16)

| Étape | Qui | Avec quoi |
|---|---|---|
| Le scénario | Mongazi et Claude, en conversation, court, d'abord | le chat |
| Le dossier de production (prompts plan par plan) | Claude, **quand Mongazi le demande** | `projets/` |
| Les images des plans | Mongazi | Nano Banana Pro, dans Google Flow |
| L'animation, les voix, les bruits | Mongazi | Veo 3.1, dans Google Flow |
| Le montage ultra dynamique (texte animé, dessins, bruitages, carte, son) | Claude | Remotion, `_studio-video/` |
| La livraison | Mongazi | le MP4 seulement |

## Les règles

1. **Le produit montré est le vrai** : photos ou vidéos du client, incrustées au montage. Jamais un produit généré
   présenté comme le sien (même règle que pour les catalogues). Personnages, décors, ambiances : générés, c'est permis.
2. **Aucun faux témoignage** : un personnage généré ne se présente jamais comme un vrai client qui donne son avis.
3. **Aucun visage réel sans accord écrit.** Si le client veut jouer dans sa pub : sa photo en référence et son accord
   écrit, rangé hors du dépôt (le dépôt est public).
4. **Dans la pub, on ne dit pas qu'elle est faite avec l'IA** (Mongazi, 2026-11-16 : « j'ai pas envie qu'on leur dise
   que ça a été créé avec l'IA »). **Le client qui achète, lui, le sait toujours** : pas de tournage, des personnages
   inventés. Il ne doit pas croire qu'il paie des acteurs.
5. **Les réseaux** : TikTok et Facebook demandent de cocher « contenu généré par IA » pour une vidéo réaliste faite par
   IA, sinon ils peuvent la retirer. C'est une petite mention sous la vidéo, pas dans l'image. (Conseil de Claude, à
   trancher par Mongazi.) En dessin animé, la vidéo n'est plus réaliste : la question ne se pose presque plus.
6. **Le filigrane** : les générations Flow de Mongazi n'en portent aucun de visible (vérifié par lui le 2026-11-16, sur
   les images et vidéos de la boutique 3D). Si un jour un compte en pose un, on ne le masque pas et on ne le recadre pas
   (conditions de Google).
7. **Le français reste très simple** (Mongazi, 2026-11-16) : [`methode.md`](methode.md) § 1.
8. **Aucun chiffre promis à l'écran** (ventes, clients gagnés) : une pub montre, elle ne garantit rien.
9. **On livre le MP4, jamais le projet** (licence Remotion, `CLAUDE.md`).
10. Aucun tiret cadratin dans les textes à l'écran.
11. **Un style qui rappelle une œuvre connue** : Mongazi a tranché le 2026-11-16, le nom du film (« Aya de Yopougon »)
    est cité dans les prompts, avec ses ingrédients (trait d'encre expressif, visages un peu caricaturaux, couleurs
    chaudes en aplats, texture de papier) et toujours la consigne « personnages originaux, pas ceux du film ». On ne
    reprend jamais ses personnages ni ses décors : l'œuvre est protégée. Si Flow refuse un prompt à cause du titre, on
    retire le titre, la description suffit.
12. **Une seule voix par clip Veo** (Mongazi, 2026-11-16) : jamais deux personnes qui parlent dans le même clip, sinon
    Veo mélange les voix. Le prompt le dit en toutes lettres.

## Les fichiers

- [`methode.md`](methode.md) : écrire une pub décalée, générer dans Flow, ce que Mongazi me remet, le montage, publier.
- [`tarifs.md`](tarifs.md) : la grille proposée, ce que coûte une pub, les conditions de vente.
- `projets/` : un dossier par pub.

## Les pubs

| N° | Pub | Pour | État |
|---|---|---|---|
| 01 | [« L'AUTRE »](projets/01-l-autre.md) | NEBULA : le catalogue, et la pub vidéo sur la carte | scénario validé, dossier prêt, rien de généré (2026-11-16) |

## Idées pour la suite (même format, mêmes règles)

- **« Les adieux »** (la vitrine) : à l'aéroport, une mère pleure son fils qui part en France. « Qui va garder la
  boutique ? » « Je te laisse quelqu'un. » « Une femme ? » « Mieux. » C'est la vitrine. Elle sèche ses larmes et le
  pousse vers l'avion : « Va. Tu vas rater ton avion. »
- **« L'interrogatoire »** (le catalogue) : un policier accuse une vendeuse. « À 3 h du matin, tu as vendu trois sacs à
  Abidjan ! » « Je dormais ! » « Alors c'est qui ? »

## Liens

- Le studio et la vidéo de marque NEBULA : `_studio-video/README.md`.
- LE MONTEUR (agent de montage, en pause) : pourra un jour automatiser une partie de ce montage.
- Les prix de NEBULA : `_documents/nebula-agency/vente/00-SOCLE-COMMERCIAL.md`. L'offre n'y est **pas encore** : elle y
  entre quand Mongazi aura validé la grille.

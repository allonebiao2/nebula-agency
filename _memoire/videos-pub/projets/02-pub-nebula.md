# 02 · La pub NEBULA (« les vidéos et NEBULA Agency »)

Ouverte le 2026-11-17. **État : en attente du scénario et des plans.**

## La demande, mot pour mot

- *« avant de créer tout ça je veux réaliser une vidéo publicitaire concernant les vidéos et nebula agency, je vais
  t'envoyer l'idée en gros que je viens de développer avec chat gpt »* (« tout ça » = l'avatar de son TikTok, qui passe
  donc après).
- *« donc en gros c'est l'idée : je génère les plans etc., ensuite je t'envoie tout et tu me fais un travail magistral,
  la vidéo doit coûter 10 000 dollars »*.
- *« je dois aussi t'envoyer les images et les vidéos pour le montage de la publicité de nebula, tu amélioreras et
  corrigeras les erreurs si possible »*.

## Ce qui manque

- ⏳ **Le scénario fait avec ChatGPT** : annoncé, **jamais reçu**. Son message décrivait la méthode, pas l'idée. Le
  demander en premier.
- ⏳ **Ses images et ses vidéos**, générées dans Google Flow.
- À voir avec le scénario : son personnage (l'avatar 3D du TikTok, dans le studio NEBULA en lumière orange tamisée)
  apparaît-il dans la pub ? Il en a parlé juste après, sans le dire.

## Qui fait quoi

- **Mongazi** : le scénario (avec ChatGPT), puis la génération des plans dans Flow (Nano Banana Pro, puis Veo 3.1).
- **Claude** : le montage, en code dans `_studio-video/` (Remotion 4.0.512). Il améliore et corrige les erreurs des plans
  quand c'est possible, et dit clairement ce qui doit être regénéré.

## La barre : « 10 000 dollars »

Ce que Claude lui a dit le 2026-11-17 : trois choses comptent avant le montage.
1. **Valider le scénario et la liste des plans AVANT qu'il génère** : chaque plan raté coûte des crédits, et le montage
   ne sauve pas une histoire faible.
2. **Des plans qui se ressemblent** : même style, mêmes personnages, même lumière. C'est ce qui donne l'impression d'un
   film et non d'un diaporama.
3. **Le son fait la moitié du résultat** : voix, musique, bruitages.

Rappel honnête : LE MONTEUR a montré qu'un montage automatique vaut 50 à 150 €, et que 10 000 € demandent une direction
humaine forte. Ici, la direction vient du scénario validé ensemble et du montage fait à la main, plan par plan.

## La remise (méthode des pubs, `methode.md` § 3)

- Le dossier **`_partage/pub-nebula/`**, exclu de GitHub le 2026-11-17 (le dépôt est public).
- Une prise par plan, nommée par son numéro : `P01.mp4`, `P02.mp4`… ; une autre prise : `P05-b.mp4`. Les images fixes :
  `I01.png`…
- Téléchargées en **1080p depuis Flow**, le son de Veo compris. **Jamais un export WhatsApp** : il compresse.

## Ce que le montage peut corriger, et ce qu'il ne peut pas

**Il peut corriger :**
- un texte mal écrit par l'IA, en le recouvrant ou en le remplaçant par une vraie typographie ;
- les couleurs et la lumière d'un plan à l'autre, avec un étalonnage commun ;
- un défaut au bord de l'image, en recadrant ou en zoomant ;
- un plan trop long ou un geste raté sur la fin, en coupant, en accélérant ou en enchaînant ;
- le son : nettoyer, remplacer une voix, poser musique et bruitages, caler les coupes sur le rythme (Librosa) ;
- un écran de téléphone illisible, en incrustant le vrai écran s'il est filmé de face.

**Il ne peut pas corriger, il faut regénérer :**
- un visage qui change d'un plan à l'autre ;
- une main déformée au centre de l'image ;
- un personnage qui ne fait pas le bon geste.

**Les outils neufs du studio** (2026-11-17) : Video Shotcraft (124 recettes de plans), les effets de lumière
(postprocessing), le calage sur le rythme (Librosa), Lemo Opuscar (99 styles). Détail et licences :
`_memoire/apprentissages/2026-11-17-dix-outils-motion-graphics.md`.

## Les règles qui s'appliquent (`cerveau.md`)

- Français très simple ; aucun chiffre inventé ; aucun visage réel sans accord écrit.
- Jamais un produit généré présenté comme celui d'un client.
- Musiques et bruitages sans Content ID, avec leurs preuves de licence ; Remotion : on livre le MP4, jamais le projet.
- La consigne « la pub ne dit pas qu'elle est faite avec l'IA » vaut pour les pubs des clients. Ici, c'est la pub de
  NEBULA elle-même, qui vend ces vidéos : **à trancher avec lui** selon le scénario.

## Prochaine étape

Mongazi colle le scénario de ChatGPT. Claude dit ce qu'il comprend et ce qu'il améliore, en peu de mots ; on valide la
liste des plans ; **ensuite seulement** il génère.

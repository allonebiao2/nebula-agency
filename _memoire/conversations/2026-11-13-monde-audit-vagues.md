# 2026-11-13 · LE MONDE, l'audit d'un expert en jeu vidéo, vague par vague

> Suite de `2026-11-12-monde-salon-hillary.md`. Le point de reprise exact est
> **`monde/REPRENDRE-ICI.md`** (réécrit ce matin « à la lettre près », à la demande de Mongazi).

## Ce qu'il a demandé (ses mots)

1. « hormis la relecture d'Impeccable, quand tu analyses en profondeur, mets-toi dans la peau d'un
   expert en animation 3D et en création de jeu vidéo : qu'est-ce qui peut encore être optimisé et
   apporté à ce niveau ? » → `monde/AUDIT-JEU-VIDEO.md` (`25ef0cd`).
2. « enchaîne donc chacun jusqu'au dernier… chacun doit être à 100 % ; tu as champ libre » puis
   « fais-les par vagues… ne passe pas à une autre tant que celle sur laquelle tu es n'est pas à 100 % ».
3. « OUI JE LES ENVOIE D'ici là » (les photos d'Hillary).
4. « en attendant tu peux enchaîner avec le prochain ; je pense qu'il faut que je génère en 3D les
   autres persos… laisse-moi les prompts » → `personnages/CONSIGNES.md` (`6a07d12`).
5. « pour chacun des prompts, donne-moi des prompts pour animer les images générées » →
   `personnages/CONSIGNES.md` (`5e9a19d`).
6. « mets tout en mémoire à la lettre près ainsi que tout ce qui reste à faire, comme ça quand je fais
   clear et je démarre une nouvelle discussion tu puisses te repérer à la lettre près ».

## Ce qui a été fait

- ✅ **Vague 1, l'ouverture cinéma** (`bcfc59e`) : filmée de nuit et de jour.
- 🟡 **Vague 2, des personnages qui vivent** (`b271315`) : Afi a 13 animations et vit (variantes,
  démarrage et arrêt, pieds au pivot, regard). Sènami, Maman et Hillary attendent leurs modèles.
- ✅ **Vague 3, la mise en scène des conversations** (`f7d60aa`) : cadrage par la distance et la
  largeur d'écran, profondeur de champ (qualité haute), caméra qui suit la tête à chaque image,
  souffle de caméra, oratrice à 1,30 m, les autres écartées de la ligne de regard, lumière de face
  douce. Deux défauts trouvés en regardant les captures et corrigés : le flou d'un podium qui bavait
  sur Afi (flou plafonné), la tête d'Afi coupée à l'ordinateur (tangage −0,47 au lieu de −0,20, une
  orientation tardive ; d'où le suivi à chaque image). QC 52/52.
- Les scripts de capture, qui vivaient dans le dossier temporaire de la session, sont rangés dans
  `monde/_outils/captures/` (avec un `LISEZMOI.md`), plus `generer_visiteuses.py` et
  `design_sidecar.py` dans `monde/_outils/`.
- Vérifié : Epic et Unreal ont bien disparu du disque (7,2 Go rendus le 2026-11-12 ; `C:` à 43 Go
  libres ce matin).
- Constaté : les images de Sènami et de Maman aux **bons âges n'ont jamais été générées** (le quota
  Cloudflare était épuisé ; le dossier de sortie est vide). Celles du dépôt sont les anciennes, aux âges
  faux : à ne pas utiliser.

## La suite

**La vague 4, la chaîne d'assets pour la 3G**, avec son plan pas à pas dans `REPRENDRE-ICI.md`,
section 4 (mesurer d'abord). Puis la 5 (lumière cuite dans Blender). Toute la liste de ce qui reste,
à moi, à Mongazi et à Hillary : `REPRENDRE-ICI.md`, section 5.

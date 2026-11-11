# Agent de montage vidéo : les pièges payés (2026-11-11)

Appris en construisant LE MONTEUR (dépôt privé `nebula-montage`). Chaque leçon est gravée dans son `_qc.py`.

## Le son et le texte

- **Deepgram entend mal une voix de synthèse.** Sur 75 mots dits par Aura-2, 15 étaient faux dans la transcription
  (« un cachet d'or » pour « dort », « Salut. » pour « Puis il s'allume… », « Nebulla »). Quand le texte est connu
  (une voix off qu'on a écrite), **le script fait foi** : la transcription ne sert que d'horloge, et l'alignement se
  fait par `difflib.SequenceMatcher` sur des mots normalisés.
- **Une voix off a besoin de silence après son dernier mot.** Sans lui, l'arrondi à l'image coupe le dernier mot
  (27 ms ici) et le banc le voit.
- **libass met une police à la taille 96 dans un corps de 63 px** (Montserrat : rapport 1,52 à 1,56, mesuré en rendant
  le texte et en comptant les pixels). Toute estimation de largeur sans cette mesure se trompe de 35 %.
- **libass ne coupe qu'aux espaces** : une adresse web plus large que l'écran déborde sans prévenir. Mesurer chaque
  texte avant de le poser, couper une adresse **après un point** (jamais après un tiret, qu'on lirait comme une
  césure), et mettre des espaces insécables dans « 1 000 F » et « quand ? ».

## L'image

- **`-ss 0` placé devant une image JPEG fait sortir un fichier vide** dans ffmpeg (« Output file is empty »). Le seek
  ne sert qu'aux vidéos.
- **Un générateur d'images ne refait jamais deux fois la même personne.** Une fin en boucle avec « la même femme »
  montrait une autre femme. Réutiliser la même image, ou générer à partir d'une image de référence.
- **Un sous-titre se place par plan, pas par sous-titre**, et un sous-titre appartient au plan où il passe le plus de
  temps (son milieu). Sinon il saute du bas vers le haut sur la même image.

## Les licences

- **Le code peut être libre et les poids interdits.** InfiniteYou et MMAudio ont un code Apache ou MIT et des poids
  CC-BY-NC. Vérifier les deux : l'API GitHub donne la licence du code, l'API Hugging Face (`/api/models/<id>`,
  `cardData.license`) celle des poids.
- Une dépendance peut tout interdire : PuLID et InstantID s'appuient sur insightface, non commercial.
- **Les GPU gratuits ne sont pas faits pour produire pour des clients** : Kaggle limite à un usage interne, personnel,
  non commercial ; Colab est prévu pour l'usage interactif. GitHub Actions (processeurs) et Cloudflare Workers AI
  permettent l'usage commercial.

## Les services

- **Nouveau format de clé Google (2026)** : `AQ.` suivi de 50 caractères, avec des points. L'ancien commençait par
  `AIza`. Un contrôle de forme `[A-Za-z0-9_-]` la refuse : y ajouter le point.
- **Gemini** : `generateContent` reste « entièrement prise en charge » à côté de la nouvelle API `/v1beta/interactions`.
  Les noms de modèles changent vite : choisir le modèle à l'exécution dans `GET /v1beta/models` (paginé), jamais en
  dur. Une clé gratuite n'ouvre pas les modèles les plus forts (`gemini-4-carbon`, `argon`) : passer au suivant sur
  403, 404 ou 429.
- **L'API GitHub sans jeton : 60 requêtes par heure.** Pour prouver qu'un dépôt est privé quand la limite est
  atteinte, la page web répond 404 à un inconnu, contre 200 pour un dépôt public.
- **Un appel payé ne s'écrit jamais dans un dossier qu'une étape suivante vide** : une relecture à 0,30 $ a été perdue
  ainsi.

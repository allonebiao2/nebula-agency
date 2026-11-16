# 2026-11-16 · PUBS VIDÉO IA : l'offre, la première pub, les prix

## La demande

Mongazi veut proposer des vidéos IA : les plans générés avec Nano Banana Pro dans Google Flow, animés avec Veo 3.1,
toujours dans Flow. Première vidéo : une pub pour NEBULA (la vidéo IA, les vitrines, les catalogues),
« conversationnelle, dramatique, virale », une discussion dont on ne voit pas la fin venir, « décalée comme les
publicités asiatiques ».

## Ce qui s'est passé

1. Claude est parti sur un dossier de production complet (lectures, recherches, prompts). Mongazi a coupé
   (« 54000 tokens ? ») : il voulait d'abord qu'on comprenne son projet et qu'on fixe un scénario. **Lui génère les plans
   et les vidéos, Claude fait le montage**, ultra dynamique, avec du texte et des dessins.
2. Scénario proposé : « L'AUTRE ». Mongazi : « j'adore le scénario ».
3. Il demande le dossier complet, une branche du cerveau pour les vidéos publicitaires, et à combien facturer.
4. Deux consignes en cours de route :
   - **la pub ne dit pas qu'elle est faite avec l'IA** : la fin « On existe, nous ? / Non. » est retirée, remplacée par
     « Et moi, on me paie combien ? / Dors. », qui répond au « Personne. Dors. » du début ;
   - **le français reste très simple** : « Qu'est-ce qu'il a, que je n'ai pas ? » devient « Il a quoi de plus que
     moi ? », et Afi dit « ma boutique dans le téléphone » au lieu de « catalogue ».

## Ce qu'on a appris (vérifié sur le web le 2026-11-16)

- **Veo 3.1** : la réplique entre guillemets après « says », `SFX:`, `Ambient noise:`, minutage `[00:00-00:02]`, clips
  de 4, 6 ou 8 s, 9:16 natif depuis janvier 2026 (guide officiel Google Cloud, blog Google).
- **Flow** : Veo 3.1 Fast = 20 crédits (10 sur Ultra), Quality = 100 ; recharge de 2 500 crédits pour 25 $ ; Pro
  donnerait 1 000 crédits par mois (contesté depuis mai 2026), Ultra 25 000.
- **Filigrane « Veo » visible avec Google AI Pro, pas avec Ultra** (FAQ de Flow). Avec une pub qui ne dit pas « IA »,
  c'est décisif.
- **API Veo 3.1** Fast avec le son : environ 0,12 $ la seconde en 1080p, sans filigrane visible.

## Ce qui a été produit

- La branche `_memoire/videos-pub/` : `cerveau.md` (entrée, rôles, règles), `methode.md` (écrire, générer, remettre,
  monter, publier), `tarifs.md` (grille proposée, coûts, conditions), `projets/01-l-autre.md` (le dossier : 5 références,
  19 plans et un bonus, montage, carte, publication).

## Décisions

Voir `_memoire/decisions.md` (2026-11-16).

## Ce qui attend

Voir `_memoire/EN-INSTANCE.md` (lignes PUBS VIDÉO IA) et `_memoire/videos-pub/projets/01-l-autre.md` § 9.

## Plus tard le même jour

- **Les prix** : Mongazi rejette la grille (« trop cher pour le Bénin ») et vise environ 10 000 F pour 30 s à 1 min.
  Piste proposée : la pub modèle, fabriquée une fois puis déclinée à chaque client (`videos-pub/tarifs.md`).
- **Les partenaires** : laissés de côté (« on zappe les partenaires »).
- **Le client qui achète sait** que c'est de l'IA (« oui ils doivent savoir, c'est clair »), rien ne le dit dans la vidéo.
- **Le 4e mur** : Mongazi veut qu'à un moment le scénario s'adresse aux spectateurs. Ajoutés : P11b (« Toi aussi, tu
  crois que c'est un homme ? ») au milieu, P20 (« Et toi ? Ta boutique, elle dort quand tu dors ? ») à la fin. La pub
  passe à environ 1 min, la version de 30 s garde P20.
- **Le filigrane** : Mongazi n'en a aucun sur ses générations Flow (preuve : les images et vidéos de la boutique 3D).
  Ni Ultra ni l'API ne sont nécessaires ; une FAQ générale ne dit pas ce que fait un compte précis.
- **Le style** : Mongazi veut « exactement » le style d'« Aya de Yopougon » (le film d'animation ivoirien) et des
  personnages créés d'abord, pour la constance. Les prompts décrivent le style sans nommer l'œuvre (elle est protégée,
  et le modèle suit mieux une description) ; une image de style R0 est jointe partout ; les fiches d'Afi et de Koffi
  montrent trois angles et six expressions. Les 45 prompts réalistes sont passés en 2D, un de plus (R0).
- **Le nom du film** : Mongazi veut que les prompts citent « Aya de Yopougon ». Fait partout (images et animations),
  avec « personnages originaux, pas ceux du film ».
- **Une seule voix par clip** : P07 (seule la tantie parle, les autres se taisent) et P11 (seul le jeune voisin crie
  « Waaaah ! ») réécrits ; chaque prompt d'animation dit qui parle, et que personne d'autre ne fait de bruit de voix.
- **La musique** : téléchargée par Chrome sur Pixabay, toutes **sans Content ID** (la plupart des morceaux le sont) :
  trois pour le drame, une afro house pour la carte, plus celle de la vidéo de marque. Rangées hors dépôt dans
  `_studio-video/public/pub-l-autre/musique/` avec `SOURCES.md`. Le 5e morceau (percussions africaines) a bloqué : Chrome
  a cessé de répondre. Les bruitages seront synthétisés au montage.

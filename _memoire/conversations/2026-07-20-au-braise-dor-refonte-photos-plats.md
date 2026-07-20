# 2026-07-20 — Au Braisé d'Or : refonte (ui-ux-pro-max) + 48 photos de plats + 1er déploiement

Suite de la session Higgsfield du 2026-07-19. Mongazi remonte 3 problèmes + demande le glassmorphisme et invoque le skill `ui-ux-pro-max`. Puis, en cours de route, demande de générer une image pour **tous** les plats. Session passée en effort **max**.

## Les 3 retours initiaux (+ glass) → traités
1. **Vidéo héro** : le scroll-scrub « la vidéo se décompose seconde par seconde au défilement » a d'abord été construit à fond (scène épinglée `heroStage` 210vh + héro `sticky` + pilotage `currentTime` au scroll + `requestVideoFrameCallback` anti-flash mobile + amorçage iOS play→pause). **Mais chez Mongazi ça ne passait pas au défilement** → il a demandé de **revenir à l'intro douce qui démarre toute seule**. Remis en : `hero.mp4` **autoplay muet en boucle**, `play()` au 1er geste si bloqué, **pause hors-écran** (IntersectionObserver), `prefers-reduced-motion` = poster Ken-Burns. `hero-scrub.mp4` n'est plus référencé (exclu du deploy).
2. **Images dans le cadre du plat** (pas une galerie séparée) : refonte des cartes plats = **cadre image en haut** (photo ou, à défaut, placeholder braise) + **prix en pastille verre** ; **carte entière cliquable → feuille de commande qui montre la photo en grand** (taille/accompagnement/qté). Section galerie « La braise en spectacle » **supprimée** (markup + CSS).
3. **FAB WhatsApp** flottant brillant (bas-droite, anneau pulsant) **retiré** ; reste « Commander » (header + héros + fiche).
4. **Glassmorphism « verre fumé braise »** : variables verre (highlight or, hairline), backdrop-filter sur barre d'onglets / feuilles / pastilles de prix, feuille de commande frostée (fond translucide au lieu d'opaque).

## Puis : une photo pour CHAQUE plat (48 au total)
Décision modèle **prise après A/B réel et inspection visuelle** (télécharger + `Read` les images) :
- **nano_banana_pro** 2 cr (modèle des 6 photos existantes) → 84 cr pour 42, **hors budget**.
- **Recraft V4.1** 1,25 cr → très bon.
- **z_image** 0,15 cr → **photoréaliste, sortie 2048², au moins aussi bon** pour des plats sur ardoise sombre. **→ RETENU.**
- 42 générations z_image (1:1) + **4 réutilisées des tests** (poulet chair, napolitaine, mojito, cheeseburger). Prompt commun = sujet + « Dark moody charcoal background, warm ember glow, golden rim light, wisps of smoke, appetizing, professional restaurant menu photography, no text/watermark/hands/cutlery ».
- ⚠️ **z_image rate-limit 429** si trop d'appels parallèles → lots de ~6-11.
- Récupération en masse via **`show_generations`** (donne `rawUrl` + `minUrl` pour chaque job) plutôt que 42 `job_status`. Script `scratchpad/fetch_dishes.py` : télécharge le `_min.webp` → réencode **WebP 900px q80** (PIL) dans `assets/images/<slug>.webp` (~72 Ko/pièce, **3 Mo les 42**).
- Map JS `PHOTO` = **nom du plat en minuscules → slug** ; QC node : **48/48 plats mappés, 48/48 fichiers présents, 0 lien mort**. La fiche de commande affiche aussi la photo.
- **Coût session ~10,2 cr** (dont ~4 en tests A/B). **Solde 66,15 / 100.**

## Déploiement (1er pour ce client)
- Accord Mongazi obtenu (« continu »). `wrangler pages deploy` d'un **dist propre** : `index.html` + `assets/images` + **`assets/videos/hero.mp4` seul** (exclus : `assets/raw/` 30 Mo, `hero-scrub.mp4` inutilisé). 53 fichiers, 5,4 Mo.
- Projet Cloudflare **`au-braise-dor`** créé → **LIVE https://au-braise-dor.pages.dev** (page + images + vidéo vérifiés **200**, en local sur :8130 ET en prod).

## Leçons / à retenir
- **z_image (Higgsfield, 0,15 cr) = excellent rapport qualité/prix pour de la photo de plat menu** (dark/moody), bien meilleur que ce que laisse penser son tag « stylized/budget ». Le préférer à nano pour les gros volumes. Toujours **regarder** les images (download + Read) avant de câbler en masse.
- Un **scroll-scrub vidéo** peut très bien ne pas « prendre » côté client même quand le code est correct → prévoir le repli **intro autoplay** et ne pas s'entêter.
- Le tag-balance regex en Bash inline casse (`\s` mangé par le shell) → écrire les validateurs dans un **.js/.py de scratchpad**.

## Reste (dispatché dans CONTEXT.md)
Affiche **A4 + QR (PHASE 7, pas encore faite — à générer maintenant que l'URL est live)** · photo du lieu · confirmer n° WhatsApp (0156057157 câblé) · adresse + Google Maps · horaires (badge ouvert/fermé) · logo officiel · réseaux IG/FB · vrais avis · reconfirmer couleur (braise sombre vs enseigne bleu/blanc/or).

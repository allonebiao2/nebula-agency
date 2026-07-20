# 2026-07-19 — Au Braisé d'Or : génération Higgsfield (MCP débloqué)

## DébLOCAGE HIGGSFIELD
Mongazi a connecté le **vrai serveur MCP Higgsfield** (`/mcp` → « Connected to higgsfield »). Ça lève le blocage `only_mcp_usage_on_trial_is_available` qui touchait le CLI ET les skills (qui wrappent le CLI). La génération passe désormais par les outils MCP `mcp__higgsfield__*`. Test validé (nano_banana_pro → job completed, 2 cr débités). Plan Plus, 100 crédits au départ. Détail dans la mémoire Claude `reference_higgsfield`.

Rappels d'usage MCP :
- `generate_image` / `generate_video` : **tout dans `params`** (model, prompt, count, aspect_ratio, medias). `get_cost:true` = préflight gratuit.
- Résultat via `job_status(jobId, sync:true)` → `rawUrl` (png/mp4) + `minUrl` (webp).
- Médias d'entrée image→vidéo : passer le **job_id** de l'image dans `medias:[{role:'start_image', value:<job_id>}]`.
- Coûts : nano_banana_pro 2 cr (1k), z_image **0,15 cr** (budget), Kling 3.0 Turbo vidéo 7,5 cr.

## CE QUI A ÉTÉ FAIT (client 09, `clients/09-au-braise-dor/index.html`)
Exécution du plan validé (budget ~50 cr, rendu photoréaliste), en 3 vagues testées :

**Vague A — 7 images (nano_banana_pro, ~14 cr)** : 6 plats (Tilapia braisé, Poulet bicyclette, Pizza feu de bois, Chawarma, Salade JOQ, Cocktail) + image héro (mains gantées noires retournant poisson/brochettes sur flammes). Style « braise premium » cohérent (charbon sombre + ember + or + bois). Optimisées WebP ≤1100px (PIL). Câblées dans la galerie « La braise en spectacle » (bento tessellant).

**Vague B — vidéo héro (Kling 3.0 Turbo, 7,5 cr)** : image héro animée (flammes, mains qui retournent le poisson, étincelles). **5 s** (durée courte demandée par Mongazi « optimisée pour la vente »). Compressée avec **imageio-ffmpeg** (pas de ffmpeg système) : `hero.mp4` boucle 1,07 Mo + `hero-scrub.mp4` keyframes tous les 3 frames 2,3 Mo. Câblage : **scroll-scrub sur PC** (currentTime piloté par le scroll dans le héro) + **poster Ken-Burns sur mobile** (aucun téléchargement vidéo = data light) + `prefers-reduced-motion` = poster statique.

**Vague C — univers braise (demande explicite Mongazi : boutons/cadres/curseur/onglets)** : 1 texture `coals.webp` (z_image, 0,15 cr) = lit de braises sous la barre d'onglets ; halo de braise qui suit le curseur (PC) ; boutons chauffés (balayage d'ember + respiration sur CTA or) ; cadres chauffés (liseré ember au survol des cartes) ; onglet actif qui palpite. Tout en CSS/JS gratuit (sauf la texture), respect reduced-motion.

## LEÇON TECHNIQUE (dispatchée)
**Cascade CSS + media queries** : une règle `@media` **n'augmente pas la spécificité**. Si les overrides responsives (`.gcell.big{grid-column:auto}`) sont placés AVANT les règles de base (`.gcell.big{grid-column:span 3}`) dans le source, les règles de base plus bas GAGNENT même quand la media query matche → la galerie gardait `span 3` sur mobile et créait des colonnes implicites (grille cassée). **Fix : placer les blocs `@media` APRÈS les règles de base.** À ajouter dans `_memoire/apprentissages/`.

## ÉTAT / RESTE
- QA Playwright PC + mobile + tablette : 0 erreur console, tous assets 200, galerie propre partout, héro vidéo OK des 2 côtés.
- **PAS déployé** (CONTEXT : pas de deploy sans accord). Sources IA lourdes → `assets/raw/` gitignoré ; livrables WebP/MP4 versionnés.
- Crédits : ~21,5 utilisés, ~76,5 restants / 100.
- Reste côté client : confirmer n° WhatsApp (01 56 05 71 57 câblé, vs 43 99 29 29 enseigne) · vraies photos/logo/adresse Maps/horaires/réseaux · 2ᵉ prix pizzas/grillades · reconfirmer direction couleur (braise sombre choisie vs enseigne bleu/blanc/or).

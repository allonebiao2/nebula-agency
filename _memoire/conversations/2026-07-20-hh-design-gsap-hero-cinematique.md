# 2026-07-20 — HH Design : héro GSAP pin & scrub + collection cinématique

Demande Mongazi : effet **GSAP ScrollTrigger « pin & scrub »** façon Spider-Verse (Miles Morales) sur HH Design, vidéo drone atelier dans le héro, régénérer les images en version ciné, effet GSAP sur les produits. Il a répondu à mes 4 questions.

## Décisions (réponses aux questions)
1. **Direction** = « Sombre + 1 accent néon braise » → j'ai transposé l'énergie Spider-Verse dans l'univers bois HH : fond **espresso sombre**, **1 seul accent braise** (`--braise:#C8461B` / `--braise2:#F0692A`) utilisé comme néon (titre « la différence. », spark, chips, hover produits), typo Cormorant conservée. Le reste du site (sections claires) inchangé (art-direction par section).
2. **Intégration** = **GSAP vanilla sur le site live** (pas React/Next). GSAP 3.12 + ScrollTrigger via CDN cdnjs.
3. **Vidéo héro** = **atelier / making-of** (drone).
4. **Images** = **régénérer aussi les pièces** en version ciné sombre (Mongazi assume le risque de fidélité ; je suis resté proche des vrais types : étagère, bibliothèque, table basse, chevets, console).

## Ce qui a été fait (LIVE https://hh-design.pages.dev, projet Cloudflare `hh-design`)
- **7 images z_image** (0,15 cr) : 1 atelier ciné 16:9 (`assets/images/hero/atelier.webp`) + 6 pièces sombres (`assets/images/collection/*.webp` — REMPLACENT les anciennes cutout claires). Rendu superbe (étagère flottante éclairée, bibliothèque Leon avec lueur braise interne, table Natura live-edge…). Total ~0,41 Mo.
- **Héro refondu en pin & scrub** : `.hero` = `height:100svh`, fond vidéo (`.hero-vid` + poster `.hero-poster`=atelier), scrim + halo braise. GSAP : **intro à l'arrivée** (accroche + titre `.ln>span` montent, `yPercent:120`) PUIS **timeline pin+scrub** (`pin:true, scrub:1, end:"+=140%"`) qui fait monter spark braise → sous-titre → 3 piliers verre (Fait main/Bois massif/Sur-mesure) → CTA, + parallax scale de la vidéo, puis **libère** le scroll. `gsap.matchMedia()` pour cleanup ; repli CSS/IO si GSAP absent ou `prefers-reduced-motion`.
- **Produits** : cartes `.piece` passées en **cover sombre** (fini le cutout clair), chip catégorie liseré braise, `.piece-view` braise ; reveal **GSAP `ScrollTrigger.batch`** (montent du bas, stagger) qui remplace l'IntersectionObserver pour ces cartes.
- QC Playwright : GSAP chargé, 0 erreur (hors 404 attendu du mp4), captures héro (mi-pin, éléments montés) + collection = validées. Déployé + commit `15cb3f9`.

## RESTE (Vague 2, bloqué sur MCP)
- **Vidéo drone atelier** : job Higgsfield **`f682a7ef-3721-4356-a656-89f634021dc9`** (kling3_0_turbo, image→vidéo depuis l'atelier, ~7,5 cr) lancé, en rendu. **Le serveur MCP Higgsfield n'arrête pas de se déconnecter** cette session → pas pu récupérer le mp4. À faire dès que `/mcp` tient : `job_status` → télécharger rawUrl → compresser (imageio-ffmpeg) → `assets/videos/hero-drone.mp4` → redéployer. En attendant, le **poster atelier** fait le fond (déjà très ciné). Le `<video><source src="assets/videos/hero-drone.mp4">` 404 proprement (poster reste).
- Options : bouton son ? non demandé. Pièces fidélité = choix client assumé.

## Leçon
GSAP pin&scrub 100% possible en **vanilla sur un site statique** (pas besoin de React malgré le brief). Toujours prévoir : intro non-scrubbée pour que le héro **ne soit pas vide à l'arrivée** (sinon au scroll=0 tout est en état « from » caché), + repli sans GSAP, + `matchMedia` pour le cleanup.

# Au Braisé d'Or — CONTEXT

## Identité
- Client : **Au Braisé d'Or**
- Secteur : Restaurant (braisé / grillades)
- Livrable : **Catalogue digital** (menu commandable) — 1er catalogue-resto NEBULA
- Marché : Cotonou, Bénin (à confirmer)
- Statut : **LIVE https://au-braise-dor.pages.dev** (Cloudflare Pages, projet `au-braise-dor`, déployé 2026-07-20)

## Décisions
- Architecture : **CATALOGUE DIGITAL** (grille de plats + prix + commande WhatsApp pré-remplie) — validé par Mongazi 2026-07-17
- Direction visuelle : à valider (reco : **braise premium** noir profond + or/braise + bois)
- Périmètre services : à préciser (sur place / à emporter / livraison)

## À DEMANDER au client (WhatsApp, en parallèle du build)
- [ ] **n° WhatsApp Business** (commandes) — à CONFIRMER avant câblage
- [ ] **Menu réel** : plats + prix, par catégorie
- [ ] **Photos** plats + lieu (5-10)
- [ ] **Logo** (si existe)
- [ ] **Adresse exacte** + quartier/ville (Google Maps)
- [ ] **Horaires** d'ouverture
- [ ] **Réseaux** (Instagram / Facebook)
- [ ] Positionnement/ambiance (premium vs populaire)

## ✅ GÉNÉRATION HIGGSFIELD EXÉCUTÉE (2026-07-19, vagues A/B/C)
- **MCP débloqué** : le vrai serveur MCP Higgsfield est connecté (`/mcp` → « Connected »), génération OK via `mcp__higgsfield__*` (le CLI/skills restent bloqués). Détail : [[reference_higgsfield]].
- **Vague A — 7 images (nano_banana_pro, ~14 cr)** : 6 plats photoréalistes (Tilapia braisé, Poulet bicyclette, Pizza feu de bois, Chawarma, Salade JOQ, Cocktail Piña Colada) + 1 image héro (mains gantées noires retournant poisson/brochettes sur flammes, 16:9 2k). Optimisées WebP ≤1100px (43-130 Ko) dans `assets/images/`. Câblées dans la **galerie « La braise en spectacle »** (bento 6 colonnes PC qui tessellise, cartes 2 col tablette / 1 col mobile — bug cascade CSS corrigé : media queries APRÈS les règles de base). Sous-titre honnête « Visuels d'illustration, bientôt remplacés par les photos de la maison ».
- **Vague B — vidéo héro (Kling 3.0 Turbo, 7,5 cr)** : les flammes bougent, mains gantées retournent le poisson, étincelles. 5 s (durée courte optimisée vente, demande Mongazi). Compressée ffmpeg (imageio-ffmpeg) : `hero.mp4` boucle 1,07 Mo + `hero-scrub.mp4` keyframes denses 2,3 Mo. **Câblage** : scroll-scrub sur PC (les images AVANCENT au défilement) + **poster Ken-Burns sur mobile (aucun téléchargement vidéo = data light)** + `prefers-reduced-motion` = poster statique.
- **Vague C — univers braise (1 texture z_image 0,15 cr + CSS/JS gratuit)** : lit de braises `coals.webp` en filigrane sous la **barre d'onglets** ; **halo de braise qui suit le curseur** (PC) ; **boutons chauffés** (balayage d'ember au survol + respiration d'ember sur le CTA or) ; **cadres chauffés** (liseré d'ember sur les cartes plats au survol) ; **onglet actif** = braise vivante qui palpite. Tout respecte `prefers-reduced-motion`.
- **Crédits** : ~21,5 utilisés (test 2 + 7 images ~12 + héro 2k + vidéo 7,5 + texture 0,15), **~76,5 restants** sur les 100 (budget ~50 respecté).
- **QA Playwright** : PC (héro vidéo scrub, galerie bento, onglets braise, halo curseur) + mobile/tablette (poster Ken-Burns, galerie 1/2 col) → 0 erreur console, tout 200. **PAS déployé** (attente accord Mongazi).
- ⚠️ Bump `?v=` de app.css/app.js **inexistants ici** : CSS/JS sont **inline dans index.html** (pas de fichiers externes) → recharge simple.

## ✅ REFONTE + 48 PHOTOS DE PLATS + DÉPLOIEMENT (2026-07-20)
Retours Mongazi après la session Higgsfield → refonte (skill `ui-ux-pro-max` invoqué) :
- **Vidéo héro** : le scroll-scrub « décomposition image par image » a été tenté (scène épinglée 210vh + `requestVideoFrameCallback`) mais **ne passait pas au défilement** chez Mongazi → **abandonné**. Remis en **vidéo d'intro douce qui démarre TOUTE SEULE** à l'entrée (`hero.mp4` boucle muette, autoplay, pause hors-écran via IntersectionObserver, `prefers-reduced-motion` = poster). `hero-scrub.mp4` n'est plus référencé.
- **Photos DANS les cartes** (plus de galerie séparée) : chaque plat a un **cadre image** en haut de sa carte + **prix en pastille verre** ; **carte entière cliquable → fiche de commande qui montre la photo en grand**. La section galerie « La braise en spectacle » a été **supprimée** (markup + CSS).
- **FAB WhatsApp** flottant brillant (bas-droite, anneau pulsant) **retiré** (il restait « Commander » header + héros + fiche).
- **Glassmorphism « verre fumé braise »** : tokens verre (highlight or, hairline), backdrop-filter sur barre d'onglets / feuilles / pastilles de prix, feuille de commande frostée.
- **48 plats = 48 vraies photos générées** (fini les placeholders) : map JS `PHOTO` (nom du plat en minuscules → slug WebP). Chaque fiche de commande affiche aussi la photo.

### Modèle image choisi = **z_image** (pas nano_banana_pro)
- A/B testé **nano_banana_pro (2 cr) vs Recraft V4.1 (1,25 cr) vs z_image (0,15 cr)** sur poulet/pizza/cocktail/burger, **images téléchargées et regardées**. Verdict : **z_image = photoréaliste, 2048², rendu au moins aussi bon** que les autres pour des plats sur ardoise sombre → retenu (nano à 2 cr aurait coûté 84 cr pour 42, hors budget).
- **42 nouvelles images z_image** (1:1) style « braise premium » (charbon + ember + halo doré + fumée), + 4 réutilisées des tests A/B (poulet chair, napolitaine, mojito, cheeseburger). Prompt commun = sujet + « Dark moody charcoal background, warm ember glow, golden rim light, wisps of smoke, appetizing, professional restaurant menu photography, no text/watermark/hands/cutlery ».
- Pipeline : `scratchpad/fetch_dishes.py` télécharge le `_min.webp` de chaque job (via `show_generations`) → réencode **WebP 900px q80** (~72 Ko/pièce, **3 Mo les 42**) dans `assets/images/<slug>.webp`. Slugs = `g-*` grillades, `p-*` pizzas, `c-*` chawarmas, `b-*` burgers, `s-*` salades, `sc-*` sauces, `pd-*` petit-déj, `k-*` cocktails.
- ⚠️ **z_image sujet au rate-limit (429)** si trop d'appels en parallèle → générer par lots de ~6-11.
- **Coût total session** : ~10,2 crédits (dont ~4 en tests A/B). **Solde 66,15 / 100.**
- **QC** : 48/48 plats mappés, 48/48 fichiers présents, 0 lien mort, JS parse OK, tous assets 200 en local ET en prod.
- **Déploiement** : `wrangler pages deploy` d'un dist propre (index.html + assets/images + `assets/videos/hero.mp4` seul ; `assets/raw/` 30 Mo et `hero-scrub.mp4` exclus). 53 fichiers, 5,4 Mo. Projet Cloudflare **`au-braise-dor`** créé + **LIVE https://au-braise-dor.pages.dev** (vérifié 200).

## PLAN GÉNÉRATION HIGGSFIELD (validé — HISTORIQUE, désormais exécuté ci-dessus)
- **Accès** : MCP Higgsfield ajouté à Claude Code (`https://mcp.higgsfield.ai/mcp`, scope user, authentifié via /mcp le 2026-07-19). ⚠️ Le CLI/skills sont BLOQUÉS sur le plan trial (`only_mcp_usage_on_trial_is_available`) → **générer uniquement via les outils MCP** (voir [[reference_higgsfield]]). Budget validé Mongazi = **~50 crédits / 100**, rendu **photoréaliste**.
- **1. Vidéo héro « qui avance au défilement »** : plan cinématique **grillade qui flambe + mains du cuisinier en GANTS NOIRS** qui retourne poisson/brochettes, braises, fumée → image (Nano Banana Pro 16:9 2k, ~2cr) puis animée en vidéo (Kling 3.0 Turbo, ~7,5cr). Câblage = scroll-scrub PC + repli boucle/Ken-Burns mobile.
- **2. Section « ultra puissante »** qui pousse à commander (feu + accroche haute énergie + CTA magnétique).
- **3. 6 visuels de plats photoréalistes** (Tilapia braisé, Poulet bicyclette, Pizza, Chawarma, Salade JOQ, Cocktail) — Nano Banana Pro ~2cr each (~12cr) — marqués « à remplacer » par vraies photos.
- **4. Textures UI boutons** (braise/charbon, or, flamme) via Soul Cinematic 0,12cr — quasi gratuit.
- Après génération : download → optimiser (WebP/JPEG) → câbler dans index.html → QA → rapport (pas de deploy sans accord).

## À FAIRE AUSSI (déjà demandé par Mongazi, en attente de génération/photos)
- Panier + options (taille/accompagnement/qté) + mode Sur place/Emporter/Livraison + message WhatsApp structuré = **DÉJÀ construit** dans index.html (moteur de commande V1).
- Barre de catégories sticky **corrigée** (overflow clip + scroll-spy).
- Ambiance sonore (feu de fond + survol/clic + son commander + boot façon Nintendo DS) = **déjà en place**.

## À REMPLACER / RESTE (placeholders posés pendant le build)
- Photos plats = **48 visuels IA générés** (à remplacer un jour par les vraies photos de la maison si souhaité, mais déjà propres et vendeurs).
- Photo **du lieu** (bloc « La maison » a encore un placeholder) · adresse exacte + carte Google Maps · horaires (badge ouvert/fermé) · logo officiel · réseaux IG/FB · 2ᵉ prix pizzas/grillades · vrais avis · **confirmer n° WhatsApp** (01 56 05 71 57 câblé, vs 43 99 29 29 enseigne).
- ✅ **Affiche A4 + 2 QR** produite (2026-07-20) : `assets/docs/Affiche_Au_Braise_dOr_A4.pdf` (print) + `.jpg` (partage WhatsApp). Design braise (héro flammes + trio tilapia/pizza/mojito), **QR site + QR WhatsApp décodés/vérifiés** (pyzbar). Générateur = `_outils/_build_affiche.py` (Python PIL + qrcode, sans navigateur).
- Reconfirmer direction couleur (braise sombre vs enseigne bleu/blanc/or).

## Infos enseigne (reçues 2026-07-17)
- Nom complet : **Restaurant Au Braisé d'Or**
- Slogan : **« De Paris à Cotonou »**
- Cuisine : **Africaine · Européenne · Américaine** (explique le menu très large)
- Services additionnels : **Service traiteur** + **Place des fêtes** (événementiel)
- Contact : **(+229) 43 99 29 29** (à CONFIRMER = numéro WhatsApp ?) · **aubraisedor@gmail.com** · WiFi 24h/24
- Légal (pied de page / mentions) : RC **RB/COT/24 A 102350** · IFU **0202501441177**
- ⚠️ Couleurs de l'ENSEIGNE = **bleu + blanc + jaune/or** (le menu papier, lui, était orange). Direction actuelle du site = **braise sombre** (choix Mongazi) → à reconfirmer vu l'enseigne.

## Journal
- 2026-07-17 — Création du dossier. Mongazi introduit la cliente (nom seul), puis précise : elle veut un **catalogue digital**. Architecture verrouillée = catalogue.
- 2026-07-17 (13h) — Menu reçu (5 photos → `MENU.md`) + enseigne. Choix validés : catalogue · **braise premium sombre** · son braise. **V1 construite** (`index.html` : dark braise, 3D glass, son braise, tout le menu rendu, commande WhatsApp par plat). Puis enseigne reçue (bleu/blanc/or + slogan + traiteur/place des fêtes + contacts) → questions de recadrage. QA V1 : rendu premium OK, à corriger = kicker hero qui clippe en mobile étroit.
- 2026-07-19 — **Génération Higgsfield exécutée (MCP débloqué)** : héro vidéo braise (scroll-scrub PC / Ken-Burns mobile), galerie de 6 plats + ambiance (bento responsive, bug cascade CSS corrigé), univers braise sur boutons/cadres/curseur/onglets (+ texture lit de braises). QA Playwright PC+mobile OK, 0 erreur. Sources IA lourdes dans `assets/raw/` (gitignoré) ; livrables WebP/MP4 dans `assets/images` + `assets/videos`. **Non déployé** (attente accord).
- 2026-07-20 — **Refonte (skill ui-ux-pro-max) + 48 photos de plats + 1ER DÉPLOIEMENT** (détail section « REFONTE… » ci-dessus). Scroll-scrub héro abandonné (ne passait pas) → intro douce autoplay ; galerie fusionnée dans les cartes (photo + prix + clic→fiche) ; FAB WhatsApp retiré ; verre fumé ; **z_image** retenu après A/B (0,15 cr) pour générer **42 photos** (+4 réutilisées) = 48 plats photographiés. Solde crédits 66,15/100. **LIVE https://au-braise-dor.pages.dev.** Reste : affiche A4+QR, photo du lieu, n° WhatsApp, adresse/Maps, horaires, logo, réseaux, avis.

# Miss cakes — CONTEXT

## Client
- **Marque** : Miss cakes
- **Patronne** : Samelia FAGBOHOUN
- **Activité** : Pâtisserie artisanale **en ligne** (gâteaux sur commande)
- **Ville** : Cotonou, Bénin
- **Secteur** : Restaurant / Alimentation (pâtisserie / dessert)
- **WhatsApp (à CONFIRMER)** : saisi `22967748955` (ancien format 8 chiffres) → forme migrée 10 chiffres câblée = **`2290167748955`** (préfixe `01` post-migration Bénin 2024). **À valider avant impression de l'affiche** (règle absolue : ne pas changer un lien WhatsApp sans confirmation).
- **Service commandé** : Vitrine Digitale + QR Code — 150 000 F setup + 15 000 F / 6 mois (hébergement). Aucune option supplémentaire cochée.
- **Couleurs imposées** : Rose poudré + marron (chocolat).
- **Logo** : annoncé « envoyé sur WhatsApp » → **pas encore reçu** → marque provisoire générée (badge cupcake crème sur dégradé rose→chocolat).
- **Délai** : « le plus vite possible ».

## Analyse (PHASE 0)
- Besoin réel = **vitrine gourmande + carte de créations commandables sur WhatsApp** (hybride **Vitrine + Catalogue**), une seule marque (≠ hub multi-pôles type Djambar).
- Pâtisserie « en ligne » → pas de boutique physique connue : axe **commande WhatsApp + livraison Cotonou**.
- Cible : occasions (anniversaires, mariages, baptêmes, baby showers, fêtes), cadeaux gourmands.

## Design (PHASE 1)
- `ui-ux-pro-max` (bleu/Inter) **écrasé** par la palette imposée : **crème dominante + rose poudré + chocolat + filets caramel-or**.
- Typo : **Cormorant** (display) + **Jost** (texte). Direction : **pâtisserie chic & gourmande, éditoriale** ; motion fluide tempéré 4G (pas de canvas lourd : hero clair + sparkles SVG + grille douce).

## Architecture (PHASE 2 — tranchée par défaut, brief non ambigu)
**Page unique élégante** `index.html` à ancres :
Hero → Barre de confiance → La maison (signature + credo) → Nos créations (6 cartes commandables) → Galerie filtrable + lightbox → Bandeau éditorial → Avis (exemples) → **Commander (formulaire → WhatsApp)** → Contact & livraison (carte Cotonou + horaires) → CTA → Footer. FAB WhatsApp + FAB audio.

## Réalisé (build nebula-site, 2026-06-23)
- **Socle** `assets/app.css` + `assets/app.js` (cache-bust `?v=20260623b`) : nav sticky + burger, lien actif au scroll, reveal, galerie masonry + filtres + lightbox, **formulaire commande → message WhatsApp pré-rempli** (sans backend), audio baseline mobile (OFF par défaut), motion (View Transitions, scroll-driven, tilt desktop), ergonomie mobile (inputs 16px, cibles 44px, safe-area, `overflow-x:hidden`).
- **6 cartes « créations »** commandables (anniversaire, wedding/pièce montée, cupcakes, layer/naked, number/letter, gourmandises) → chacune ouvre WhatsApp pré-rempli avec le nom.
- **Galerie** : 12 tuiles d'aperçu (placeholders SVG gradient par catégorie, marquées « à remplacer ») filtrables + lightbox. **Visibles sans JS** (PE corrigé sur `.gitem`).
- **SEO** : JSON-LD `Bakery`, meta description, OG (image générée), favicon/apple-touch.
- **Assets générés** (`_build_assets.py`, Pillow/segno) : marque provisoire `logos/mark.png` (badge cupcake), favicons, `og/og.jpg` 1200×630, `qr/qr-whatsapp.png`.
- **Affiche A4** `affiche.html` → `assets/docs/Affiche_Miss_cakes_A4.pdf` (logo, slogan, 3 visuels, QR WhatsApp « Commander », tél, chips, réseaux, crédit NEBULA).
- **Infra** : `robots.txt`, `sitemap.xml`, `_headers` (sécurité + cache immutable `/assets/*`), `404.html` de marque.

## QA (PHASE 6) — OK
- **0 débordement horizontal** mesuré (360/390/414/768/1024/1280, scrollWidth=clientWidth).
- Tous les assets **200** en local. Visuel desktop + mobile validé (captures Edge headless).
- **Formulaire testé** (harnais) : génère `https://wa.me/2290167748955?text=…` avec message structuré (nom, numéro, quartier, occasion, type, parts, parfums, message). `URLOK=true`.
- Hook **impeccable** : `em-dash-overuse` corrigé (· / : ) ; `single-font` = **faux positif** (Cormorant + Jost dans le CSS partagé, le hook ne scanne qu'un fichier).

## Mise en ligne (PHASE 8)
- Cloudflare Pages, projet **`miss-cakes`** → **https://miss-cakes.pages.dev** (à vérifier 200 en prod).

## V2 — Passe « spectaculaire » + corrections (2026-06-23, cache `?v=20260623c`)
Demande Mongazi : « applique toutes les corrections de l'audit + rends-la spectaculaire, animations
partout ; j'envoie le reste après ». Fait (tout natif/GPU, 0 lib, `prefers-reduced-motion` complet) :
- **Correction a11y** : bouton CTA rose recalculé en **raspberry `#B44E69→#9A3450` texte blanc** (WCAG AA
  4.96→7.04 ; l'ancien rose poudré + blanc échouait à 2.2–3.6). Tokens `--cta-1/--cta-2`.
- **Langage signature « atelier de pâtisserie »** : **coulures de glaçage** (icing drips, CSS mask
  radial) encadrant la bande chocolat éditoriale (crème qui coule dedans, chocolat qui coule dessous).
- **Hero** : mesh crème/rose/caramel qui dérive (desktop), **cake line-art qui se dessine**
  (stroke-dashoffset) + flamme qui vacille + halo + vapeur, **sucre/confettis qui flottent** (JS),
  titre « occasion » avec soulignement or qui se trace + reflet qui passe.
- **Cartes créations** : entrée échelonnée, sheen sweep, tilt 3D desktop, tag qui réagit.
- **Galerie** : glyphes qui bougent + shimmer au survol.
- **Micro-interactions partout** : ripple au clic (boutons/filtres/actions), label qui se lève au
  focus, pills qui « pop », icônes de confiance qui respirent, FAB qui invite, CTA aimantés (desktop).
- **PE préservé** (leçon réappliquée) : tracé du cake, flamme, drips, tuiles galerie = **visibles sans
  JS** (états cachés gatés `.js`). QA : overflow 0 (360→1280), cake visible no-JS, prod 200 v=c.
- ⚠️ Analytics (Cloudflare Web Analytics) = reste un clic dashboard (token déploiement sans scope RUM).

## V3 — Vraies images client intégrées (2026-06-24, cache `?v=20260624a`)
Samelia (via Mongazi) a envoyé 4 visuels générés (Nano Banana Pro) dans `_partage/` → traités + câblés :
- **HERO = vidéo de fond** (`Hero (à animer).mp4`, déjà animé en cinemagraph) : transcodée H.264
  **8 Mo → 256 Ko** (1600px, crf 28, faststart, muette), poster JPEG. Le **SVG cake-art + mesh +
  sprinkles retirés** ; vidéo plein écran, cake à droite, voile crème dense à gauche (titre sombre AA),
  autoplay vérifié (paused=false, readyState 4). `prefers-reduced-motion` → poster figé.
- **3 fonds photo** optimisés (PNG 5-6 Mo → JPEG ~100-200 Ko, 1920px) dans `assets/images/bg/` :
  - `editorial.jpg` (cake sombre) → bande éditoriale (`.editorial .bg`, voile chocolat, texte blanc AA).
  - `cta.jpg` (gâteau bougies festif) → bande CTA (`.cta-photo .cta-media`, voile sombre renforcé AA).
  - `maison.jpg` (flat-lay marbre/ingrédients) → section « La maison » (`.has-photo .sec-bg`, voile crème, texte sombre AA).
- Sources brutes conservées dans `_partage/` ; pipeline reproductible. QA : overflow 0, vidéo lit en
  H.264, contrastes AA vérifiés (calcul + captures), prod 200.
- Restent **provisoires** : la **galerie** (tuiles SVG d'aperçu), le **logo** (badge cupcake), les **avis**.

## V4 — Une animation signature DIFFÉRENTE par section + nettoyage code (2026-06-24, `?v=20260624c`)
Demande : « chaque section = une expérience différente, ultra-fluide, qui transporte dans l'univers
Miss cakes » (page unique conservée). Identités de motion (toutes natif/GPU, reduced-motion complet,
contenu visible sans JS) :
- **Hero** : parallax scroll-driven (la vidéo s'enfonce/zoome, le contenu dérive) + entrée chorégraphiée.
- **Engagements** : `trust-line` — ligne dorée qui se trace (scaleX) reliant les 4 piliers, piliers qui surgissent le long.
- **La maison** : `reveal-clip` (essuyage clip-path du texte) + `reveal-unfold` (le credo s'ouvre en rotateX, livre de recettes).
- **Créations** : `reveal-place` — cartes posées en perspective (rotateX bas + scale), cascade nth-child.
- **Galerie** : `gitem` scatter (translateY + rotation + scale, **sans translateX** = anti-débordement) → se rangent.
- **Éditorial** : Ken-Burns scroll-driven sur la photo sombre + **filet d'or** qui se trace.
- **Avis** : slide alterné gauche/droite (`reveal-from-l/r`, `#avis{overflow-x:clip}`) + **étoiles qui se remplissent** une à une (JS).
- **Commander** : `atelier` — blocs du formulaire en cascade + **poussière de sucre** qui dérive (`.flour`, clippée).
- **Contact** : `reveal-stamp` — lignes d'info qui s'impriment (scale .9→1, pas de débordement).
- **CTA** : `cta-celebrate` — **éclat de confettis** à l'entrée (JS, borné/GPU) + titre qui s'agrandit.
- **Nettoyage** : retrait du code mort (hero SVG cake-art/mesh/sprinkles/hero-bg/hero-grid en CSS+JS) laissé par V2 après passage à la vidéo. `node --check` OK.
- QA : overflow 0 (360→1280, 3 fuites horizontales corrigées : scatter/avis/stamp), prod 200 v=c, motion+confetti servis, dead code absent vérifié.

## V5 — Boutons « Liquid Glass » (réf _partage/liquid glass.jpg, 2026-06-24, `?v=20260624d`)
Demande explicite : boutons en verre liquide comme la réf, adaptés Miss cakes. (Le ban impeccable du
glassmorphism = « par défaut/décoratif » ; ici choix explicite ciblé, appliqué avec lisibilité AA.)
Recette (corps teinté pour l'AA + verre par-dessus) : reflet spéculaire haut (gloss ≤42% pour ne pas
toucher le texte centré) + profondeur basse (inset shadow) + liseré clair + **dispersion chromatique
discrète** (inset froid/chaud) + halo coloré + `backdrop-filter:blur saturate` + `text-shadow`.
- **Primaire** = raspberry glass (`--cta-1/2`, blanc, corps 4.96–7.04 où est le texte).
- **WhatsApp** = vert glass (vert approfondi `#34d977→#0e9a49`, blanc large-gras 3.66 ≥ AA grand).
- **Caramel** = ambre glass (texte chocolat). **Ghost/Outline** = verre givré (texte chocolat sur clair ;
  surcharge **fonds sombres** CTA/éditorial = verre clair + texte blanc 9.19). **`.order`** cartes = verre vert ;
  **`.lb-order`** = verre vert ; **filtres galerie** = verre givré, actif = raspberry glass ; **FAB WhatsApp** = verre vert.
- Repli `@supports not(backdrop-filter)` : corps plus opaques (AA préservé). QA : overflow 0, contrastes
  calculés, captures clair (hero/maison) OK, prod 200 v=d. Aucun JS modifié.

## V6 — Police de texte : Jost → Hanken Grotesk (2026-06-24, `?v=20260624e`)
Mongazi trouvait Jost « trop basique » (repéré via la deck du formulaire). Police de **corps**
remplacée partout par **Hanken Grotesk** (grotesque suisse raffiné, pro + distinctif, ≠ reflex-defaults
Inter/DM/Jost) ; **Cormorant** (display serif) conservé = pairing serif+grotesque. Remplacé dans
`index.html` (liens Google Fonts ×2), `assets/app.css` (body font-family), `affiche.html`, `404.html`
(weights 400/500/600/700). QA : 0 Jost restant, Hanken charge (200), overflow 0 (360→1280), rendu
vérifié. DESIGN.md à mettre à jour si besoin. (Choix validé par Mongazi parmi Hanken/Schibsted/Albert.)

## À REMPLACER (placeholders pro « à valider »)
- **Logo** → badge cupcake provisoire (remplacer par le vrai logo dès réception WhatsApp ; régénérer favicons/OG/affiche via `_build_assets.py`).
- **Photos** → tuiles d'aperçu SVG (basculer les `.gitem .ph` en `<img>` quand les vraies photos arrivent ; pipeline prêt).
- **Avis** → 3 exemples marqués « à valider » (remplacer par de vrais retours).
- **Numéro WhatsApp** → confirmer `2290167748955` (surtout avant d'imprimer l'affiche).
- **Réseaux sociaux** → Instagram / Facebook (emplacements présents, liens « # » à remplir).
- **Adresse / zone** → carte centrée sur Cotonou (générique) ; préciser quartier de retrait + frais de livraison si besoin.
- **Horaires** → valeurs par défaut (Lun-Ven 8h-20h, Sam 9h-20h, Dim sur RDV) à confirmer.

## À demander sur WhatsApp (en parallèle)
- [ ] Logo (idéalement fond transparent, 2 versions)
- [ ] Photos de réalisations par type (anniversaire, wedding, cupcakes, gourmandises)
- [ ] Confirmer le **numéro WhatsApp**
- [ ] Avis clients réels + horaires
- [ ] Réseaux (Instagram / TikTok / Facebook)
- [ ] Parfums / spécialités à mettre en avant ; fourchette de parts/prix

## Statut
- Créé le 2026-06-23. Build run-to-completion (skill nebula-site) terminé + déployé.
- Domaine custom éventuel = étape ultérieure (DNS) à la demande de Mongazi.

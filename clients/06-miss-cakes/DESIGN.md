# Design

## Theme
Pâtisserie chic & gourmande, éditoriale et chaleureuse. Fond **crème** dominant (clair, appétissant),
accents **rose poudré** (marque) et **chocolat** (encre profonde), filets **caramel-or** discrets.
Lumière douce, matières sucrées. Light theme assumé (pas de dark : on mange à la lumière du jour).
Color strategy : **Restrained-plus** — neutres crème tintés + rose comme couleur de marque (~15-20%
des surfaces), chocolat pour les bandes d'ancrage, caramel en filet rare.

## Color (tokens — voir assets/app.css `:root`)
- Fonds : `--bg #FFFBF8` (crème), `--bg-2 #FBEEE9` (rosé pâle), `--bg-3 #FFFFFF` (cartes), `--bg-warm #F8E9DD`.
- Chocolat (bandes/encre) : `--cocoa #3E2723`, `--cocoa-2 #4E342E`.
- Rose (marque, décoratif) : `--rose #E59CA9`, `--rose-deep #C76B7C`, `--rose-ink #A23B53` (texte AA),
  `--rose-soft #F6D9DE`, `--blush #FCEEF0`.
- **CTA rose (boutons, texte blanc AA)** : `--cta-1 #B44E69 → --cta-2 #9A3450` (raspberry ; white 4.96→7.04).
- Caramel : `--gold #C9925B`, `--gold-ink #875524` (texte AA).
- Texte : `--ink/--text #3A2723` (13.6:1 sur crème), `--muted #79564E` (6.3:1), `--on-ink #FBEDE7`.
- WhatsApp : `#25D366` (FAB + liens d'action ; convention de marque, icône reconnaissable).
- Contrastes vérifiés par calcul (script luminance) : corps 13.6, muted 6.3, rose-ink 6.2, gold-ink 6.1,
  CTA blanc/raspberry 4.96–7.04. Tout ≥ AA.

## Typography
- Display : **Cormorant** (serif couture) — titres, prix, légendes signatures. *Déjà shippé = identité
  préservée* (la liste reflex-reject ne s'applique pas à une marque déjà engagée).
- Texte : **Hanken Grotesk** (grotesque suisse raffiné, pro + distinctif ; ex-Jost jugé « trop basique » 2026-06-24). Paire sur axe serif + grotesque. Poids 400/500/600/700.
- Échelle fluide `clamp()`, h1 ≤ ~4.7rem, `text-wrap:balance` sur titres, `pretty` sur prose, corps ≤ 66ch.

## Components (socle partagé `assets/app.css` + `assets/app.js`)
Nav verre sticky + burger cascade · boutons (rose CTA / caramel / WhatsApp / ghost / outline) avec
sheen + press · cartes « créations » commandables (bento : 1 vedette) · galerie masonry filtrable +
lightbox · panneau « credo » chocolat · barre de confiance · témoignages · localisation/zone ·
**formulaire commande → WhatsApp** (sans backend) · FAB WhatsApp + FAB audio · footer chocolat.
0 emoji → SVG (viewBox 24, stroke uniforme). Cartes utilisées seulement là où c'est la bonne
affordance (catalogue produit) ; pas de grille de cartes génériques ailleurs.

## Motion — langage signature « atelier de pâtisserie »
Tout natif/GPU (0 lib CDN = robuste 4G). `prefers-reduced-motion` fige tout.
- **Hero** : mesh crème/rose qui dérive, **cake line-art qui se dessine** (stroke-dashoffset) + flamme
  qui vacille + vapeur, **sucre/sprinkles qui flottent**, titre en reveal masqué + shimmer sur l'italique.
- **Signature** : **coulures de glaçage** (SVG drips) entre sections — la respiration de marque, pas un
  fade générique.
- **Sections** : reveals variés (translateY, scale, glissé, stagger `--i`) ; jamais le même fade partout.
- **Cartes** : tilt 3D desktop, sheen sweep, glyphe qui « rebondit », prix/CTA qui se révèlent ; stagger.
- **Micro** : ripple au clic (boutons/CTA), focus glow + label, pills check, nav underline, FAB ping/eq,
  scroll-progress, magnetic CTA (desktop fin).
- Easing : `--ease-out-quart/quint/expo` (jamais bounce/elastic). Durées 100/300/500.
- Perf : effets lourds (mesh, particules) gated `!isMobile && !saveData` ; IO unobserve ; pause hors-écran.

## Layout
Mobile-first, `clamp()` fluide, rythme varié (bandes serrées/aérées). 0 débordement horizontal mesuré
(360→1280, `html{overflow-x:hidden}` + vérif scrollWidth). Reveals = enhancement d'un défaut déjà
visible (jamais cacher le contenu derrière une classe sans JS — `.js .reveal`, `.js .gitem`).

## Cache / déploiement
Cache-bust `?v=AAAAMMJJx` sur app.css/app.js (bumper à chaque modif). Cloudflare Pages (`miss-cakes`),
`_headers` immutable `/assets/*`, robots/sitemap/404. Assets générés ré-exécutables (`_build_assets.py`).

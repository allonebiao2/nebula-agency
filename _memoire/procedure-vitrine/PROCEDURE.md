# PROCÉDURE MAÎTRE — Vitrine / Catalogue digital + QR (NEBULA)

> Runbook end-to-end. Chaque phase = des **entrées**, des **actions**, des **livrables**, une **vérification**.
> Le futur skill exécute ces phases **dans l'ordre**, en autonomie, jusqu'au produit fini.
> Référence d'exécution : **Djambar Team / Saeir Thiam Bijouterie** (2026-06-22).

---

## PHASE 0 — Réception & analyse du brief
**Entrée** : le **formulaire client rempli** (voir `QUESTIONS-FORMULAIRE.md`) + tout brief additionnel (vocal/texte).

Actions :
1. Lire la fiche ET tout brief stratégique. **Analyser en profondeur** : le besoin réel dépasse souvent « une vitrine ».
   - *Ex. Djambar Team* : la fiche disait « bijouterie », mais le brief révélait un **GROUPE** (holding) dont la bijouterie est la locomotive → architecture multi-pôles évolutive, pas une page unique.
2. Détecter le **type de produit** : Vitrine (image/marque) vs Catalogue digital (vente/produits) — souvent hybride.
3. **Ancrer dans la mémoire** : lire le `CONTEXT.md` du client s'il existe, `CLAUDE.md`, `MEMORY.md`, `CONVENTIONS.md`. Reprendre les faits déjà connus (ne pas reposer des questions déjà répondues).
4. Lister ce que **seul le client possède** (à demander sur WhatsApp) : logo, photos, adresse/Maps, avis, horaires, réseaux, n° WhatsApp à confirmer, musique.

**Livrable** : compréhension écrite du besoin + liste des assets manquants.

---

## PHASE 1 — Design system grounded
**Entrée** : secteur + mots-clés + contraintes client (couleurs imposées, etc.).

Actions :
1. Invoquer **`/ui-ux-pro-max`** → `python .claude/skills/ui-ux-pro-max/scripts/search.py "<secteur mots-clés>" --design-system -p "<Marque>" -f markdown`.
2. **Écraser** les recos de l'outil par : (a) la **palette imposée** par le client, (b) la **réalité terrain** (perf mobile/4G en Afrique de l'Ouest → tempérer les effets lourds type liquid glass).
3. **Garder** ce qui est bon (souvent la typo). *Ex.* : on a gardé **Cormorant** (titres) ; on a remplacé le body par **Jost** (Montserrat jugé « sur-utilisé » par le hook impeccable).
4. Invoquer **`/frontend-design`** pour transformer ce design system en **parti-pris esthétique BOLD** : choisir un ton extrême et cohérent (luxe/éditorial, minimal, brutaliste…), une **typo distinctive** (jamais Inter/Roboto/Arial/system), un **moment de motion** fort (page-load staggered), une **composition** non générique (asymétrie/overlap/grid-breaking), une **atmosphère** (gradient mesh, grain, ombres). But : éviter le rendu « AI slop ». ⚠️ web responsive (≠ affiche A4 = skill visual-design).

**Livrable** : pattern + style + palette (hex) + typo + effets + anti-patterns + **direction esthétique** assumée.

---

## PHASE 2 — Cadrage avec le décideur (AskUserQuestion)
**3 à 4 questions max**, la **recommandation en 1ʳᵉ position** (suffixe « (Recommandé) »). Voir `QUESTIONS-FORMULAIRE.md`.
Décisions typiques : **architecture** (mono-page / hub multi-pages / catalogue), **périmètre** (pôles, pages « Bientôt »), **direction visuelle** (dans la palette client), **démarrage** (placeholders pro vs attendre les assets).

> Règle : démarrer **tout de suite** avec des **placeholders pro « à valider »** (jamais de vide), pour livrer vite ; on remplace dès réception des assets.

**Livrable** : décisions verrouillées.

---

## PHASE 3 — Socle technique partagé
Créer **`assets/app.css`** + **`assets/app.js`** (un seul socle pilote TOUT le site) :
- `app.css` : tokens (couleurs/typo/ombres/rayons), composants (nav sticky, boutons, cartes, galerie, lightbox, témoignages, localisation, CTA, footer, FAB), responsive (mobile-first), `reveal` au scroll, `prefers-reduced-motion`.
- `app.js` : nav scrollée + burger mobile, reveal (IntersectionObserver), **galerie filtrable + lightbox** (navigue dans les visibles), **audio d'ambiance baseline mobile** (déblocage iOS silent buffer + DynamicsCompressor + gain mobile, OFF par défaut, fondu).
- **Cache-bust** : suffixe `?v=AAAAMMJJx` sur les liens `app.css`/`app.js` ; **bumper à chaque modif** du socle (sinon JS/CSS périmé en cache).

**Pourquoi un socle partagé** (≠ pages auto-contenues) : changer le design une fois → tout le site suit ; **ajouter un pôle = dupliquer 1 page légère**. C'est le « évolutif » que le client réclame.

**Livrable** : `app.css` + `app.js` versionnés.

---

## PHASE 4 — Pages
**Vitrine** :
- `index.html` : hero (kicker + titre + accroche + CTA WhatsApp), sections (à-propos/valeurs, services/produits, galerie, avis, localisation), CTA, footer.
- **Hub multi-pages** (si groupe/multi-pôles) : `index.html` (accueil ombrelle) + 1 page par pôle actif + pages **« Bientôt »** élégantes (teaser + opt-in « me prévenir ») pour les pôles futurs.

**Catalogue digital** :
- Page(s) catalogue : **grille produits** (image + nom + prix/ « sur devis ») + **filtres par catégorie** + fiche/lightbox + **bouton commande WhatsApp pré-rempli** (nom du produit dans le message).

Communs : liens **WhatsApp pré-remplis par contexte de page**, **Google Maps + itinéraire texte**, **section avis**, **FAB WhatsApp** + **FAB audio**, méta OG + favicon.

**Livrable** : toutes les pages HTML.

---

## PHASE 5 — Pipeline d'assets (`_build_assets.py`, Pillow)
Script **ré-exécutable** (quand le client envoie d'autres photos). Voir `SKILLS-ET-OUTILS.md`.
1. **Logo** : détourer (bbox alpha) → versions **blanche** (fonds sombres) + **noire** (fonds clairs) ; **marque** seule (crop du symbole, sans le wordmark) pour la nav ; **favicon** + **apple-touch-icon** (symbole blanc sur carré navy arrondi) ; **images OG sociales** 1200×630 (navy + logo + titre serif).
2. **Photos** : `ImageOps.exif_transpose` (orientation) → resize max ~1080 px → **JPEG q82 progressive** → rangées par catégorie (`gallery/<cat>/gN.jpg`) ; **sélection régulièrement espacée** pour la variété. **Garder les watermarks** du client (son branding).
3. **QR codes** (segno) : **WhatsApp** + **Google Maps** (liens **stables**), couleur navy.

**Vérif** : planche-contact (montage) des photos optimisées ; poids total raisonnable (lazy-load).

**Livrable** : logos, favicons, OG, galerie optimisée, QR.

---

## PHASE 6 — QA réelle (navigateur)
1. **Serveur local** : `python -m http.server <PORT> --directory <dossier client>`.
2. **Captures Edge headless** (desktop + mobile) → relire les PNG (QA visuelle).
   `msedge --headless --disable-gpu --no-sandbox --hide-scrollbars --user-data-dir=... --force-device-scale-factor=1 --virtual-time-budget=6000 --window-size=W,H --screenshot=out.png URL`
3. **Mesure du débordement horizontal** : page diag (iframe même origine) + `--dump-dom` → `scrollWidth` vs `clientWidth` → **doit être `over=0`** (mobile inclus).
4. **Hook `impeccable`** (auto à chaque écriture) : corriger les vrais défauts (em-dashes en trop → `·`/ponctuation), **classer les faux positifs** (`single-font` = dû au CSS partagé : la paire Cormorant+sans est sur la page mais le hook scanne 1 fichier), gérer `overused-font` (changer la police si pertinent).
5. **Tous les assets répondent 200** (curl pages + images + css/js).

**Livrable** : QA OK (0 overflow, assets 200, hook traité).

---

## PHASE 7 — Affiche PDF A4 + QR (option formulaire)
1. `affiche.html` : `@page{size:A4;margin:0}`, **fond clair** (économe en encre), `print-color-adjust:exact`. Contenu : bandeau logo, marque + tagline, slogan serif, chips services, 3 photos, **matières**, **2 QR** (WhatsApp « Commander » + Maps « Nous trouver »), téléphone, adresse + repère, **ligne « Suivez-nous »** (réseaux), crédit NEBULA.
2. Rendu : `msedge --headless --no-pdf-header-footer --virtual-time-budget=7000 --print-to-pdf="…/Affiche_<Marque>_A4.pdf" http://localhost:PORT/affiche.html`.
3. QA : capture A4 (`--window-size=794,1123 --force-device-scale-factor=2`) → vérifier qu'aucun bloc ne déborde.

> **Choix du QR** : sur un support **imprimé**, viser des liens **stables** (WhatsApp + Maps). Ne PAS mettre une URL provisoire (sous-domaine temporaire) qui deviendra morte. Ajouter le QR « site » quand le **domaine final** est acquis.

**Livrable** : `assets/docs/Affiche_<Marque>_A4.pdf`.

---

## PHASE 8 — Mise en ligne (Cloudflare Pages)
1. **Build propre** `_dist/` : HTML + `assets/app.*` + `assets/images/{logos, favicon, og, gallery}`. **Exclure** les photos sources lourdes, `_build_assets.py`, `affiche.html`, `CONTEXT.md`.
2. Déployer : charger le token sans l'exposer (`set -a; source secrets/cloudflare.env; set +a`), puis
   `npx --yes wrangler@latest pages project create <projet> --production-branch=main` (idempotent) puis
   `npx --yes wrangler@latest pages deploy _dist --project-name=<projet> --branch=main --commit-dirty=true`.
3. **Lien `*.pages.dev` live immédiat** (HTTPS auto, **zéro DNS**). Vérifier 200 + titre en prod.
4. **Domaine custom** = étape **séparée, pas à pas** (souvent DNS Hostinger → peut nécessiter le client) ; à faire quand le domaine final est prêt.

**Livrable** : URL live HTTPS.

---

## PHASE 9 — Mémoire & livraison
1. **Mémoire** : `CONTEXT.md` du client (réécrit/à jour), table clients de `CLAUDE.md`, log `_memoire/conversations/<date>-<client>.md`, `_memoire/journal/<date>-journal.md`. Mettre à jour `EVOLUTION.md` de cette branche.
2. **Git** : montrer les changements ; **stage sélectif** (jamais `git add -A` qui balaie des fichiers étrangers) ; commit message clair + `Co-Authored-By` ; push selon validation.
3. **Livrer** : **lien live** + **PDF**, lister « reste à valider » (avis/horaires) + étapes futures (domaine).

**Livrable** : produit livré + mémoire à jour.

---

## RÈGLE D'OR (pour le skill)
**On ne s'arrête pas tant que tout n'est pas fini.** Le skill enchaîne PHASE 0→9 sans rendre la main,
**sauf** pour une donnée que seul le client détient (et encore : il pose alors des **placeholders pro
« à valider »** et **continue**). Voir `SPEC-SKILL.md`.

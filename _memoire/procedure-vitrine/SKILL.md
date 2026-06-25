---
name: nebula-site
description: >-
  Construit une VITRINE / CATALOGUE digital NEBULA de bout en bout, du formulaire client au site
  déployé en HTTPS. Utiliser quand Mongazi colle une fiche « NOUVELLE COMMANDE — NEBULA AGENCY »
  (ou un formulaire nebula-agency.online), ou dit « nouvelle vitrine », « crée le site de <client> »,
  « nouveau client <nom> », « catalogue digital », « hub multi-pages », « vitrine + QR ». Produit :
  site multi-pages (HTML/CSS/JS, socle partagé), galerie filtrable + lightbox, liens WhatsApp
  pré-remplis, Google Maps, affiche PDF A4 avec QR, assets générés (logos/favicons/OG/galerie),
  déploiement Cloudflare Pages, mémoire à jour. Run-to-completion : ne s'arrête pas tant que tout
  n'est pas fini, déployé et accessible (200). Marché : Afrique de l'Ouest francophone.
---

# NEBULA Vitrine-Express — du formulaire au produit fini

Tu es le **chef de projet + développeur + directeur artistique** d'une agence qui livre des
vitrines digitales premium en Afrique de l'Ouest francophone. On te donne **un formulaire client
rempli** ; tu rends **un site déployé, accessible, sur-mesure** — sans t'arrêter en route.

**Référence absolue (gold standard)** : `clients/05-saeir-thiam-bijouterie/` (Djambar Team).
Tout nouveau site doit l'égaler ou le dépasser.

## ⚖️ RÈGLE D'OR — Run-to-completion
**On ne s'arrête pas tant que tout n'est pas fini, déployé et vérifié (200).**
- Enchaîne **PHASE 0 → 9** d'affilée, sans rendre la main entre les phases.
- **Donnée manquante (côté client)** → ne bloque PAS : pose un **placeholder pro « à valider »**
  (texte rédigé, visuel SVG/libre de droits, avis-exemples marqués, wordmark) et **continue** ;
  tiens une liste **« À REMPLACER »**.
- **Boucle d'auto-vérification finale** : déroule la checklist (§ Checklist). Tant qu'un item
  échoue → corrige et re-vérifie. « Fini » = **tous** les items passent **et** site live 200.
- **Tranche toi-même** via les défauts (§ Cadrage) — n'attends pas le client pour des choix que
  la mémoire + le brief permettent de décider.
- **Points d'arrêt autorisés (rares)** : (a) actions **sortantes/irréversibles** non
  pré-autorisées (**push git**, **domaine/DNS**) → fais tout le reste, **livre**, puis demande ;
  (b) ambiguïté **bloquante** réelle → **1 question groupée** (AskUserQuestion), puis reprends.
- Le déploiement `*.pages.dev` (réversible) fait partie du run **normal**.

## 📥 Entrée
Le **formulaire rempli** collé tel quel (+ éventuel brief vocal/texte qui peut **redéfinir
l'ampleur**). Optionnel : chemin d'un dossier d'assets reçus, pré-autorisations (« commit+push OK »,
« sous-domaine = X »). Détail des champs : `_memoire/procedure-vitrine/QUESTIONS-FORMULAIRE.md`.

## 🧠 Cerveau de référence (lire pour le détail, ne pas tout recopier)
- `_memoire/procedure-vitrine/PROCEDURE.md` — le runbook complet PHASE 0→9.
- `_memoire/procedure-vitrine/CONVENTIONS.md` — standards non négociables.
- `_memoire/procedure-vitrine/QUESTIONS-FORMULAIRE.md` — parsing formulaire + défauts.
- `_memoire/procedure-vitrine/SKILLS-ET-OUTILS.md` — inventaire outils + commandes.
- `_memoire/procedure-vitrine/EVOLUTION.md` — **leçons accumulées (à lire AVANT de coder)**.
- Templates de code bundlés : `.claude/skills/nebula-site/templates/` (socle à adapter).

---

## Les phases (exécuter dans l'ordre)

### PHASE 0 — Réception & analyse
Lis la fiche **et** le brief stratégique. **Analyse en profondeur** : le besoin réel dépasse
souvent « une vitrine » (Djambar : « bijouterie » → en fait un **GROUPE** multi-pôles). Détecte
**Vitrine** (image/marque) vs **Catalogue** (vente) — souvent hybride. **Ancre dans la mémoire** :
`CONTEXT.md` du client s'il existe, `CLAUDE.md`, `MEMORY.md`, `CONVENTIONS.md` — ne repose pas une
question déjà répondue. Liste ce que **seul le client possède** (logo, photos, adresse/Maps, avis,
horaires, réseaux, n° WhatsApp à confirmer, musique) → à demander sur WhatsApp **en parallèle**.
Crée `clients/NN-slug/` (+ `assets/{images,videos,docs}`) et un `CONTEXT.md` initial.

### PHASE 1 — Design system grounded → parti-pris BOLD
1. `/ui-ux-pro-max` :
   `python .claude/skills/ui-ux-pro-max/scripts/search.py "<secteur mots-clés>" --design-system -p "<Marque>" -f markdown`
2. **Écrase** les recos par (a) la **palette imposée** par le client, (b) la **réalité 4G**
   (tempérer les effets lourds). **Garde** le bon (souvent la typo).
3. `/frontend-design` → transforme le design system en **parti-pris esthétique assumé** (luxe
   éditorial / minimal / brutaliste…), typo **distinctive** (jamais Inter/Roboto/Arial/system),
   un **moment de motion** fort, une **composition** non générique. But : zéro « AI slop ».
   ⚠️ web responsive (≠ affiche A4).

### PHASE 2 — Cadrage décideur (AskUserQuestion)
**≤ 3-4 questions, recommandation en 1ʳᵉ position** (« (Recommandé) »). Thèmes : **architecture**
(hub multi-pages / page unique / catalogue), **périmètre** (pôles, pages « Bientôt »), **direction
visuelle**, **démarrage** (placeholders pro vs attendre). Démarre **tout de suite** avec des
placeholders pro « à valider » (jamais de vide). Modèles validés : `QUESTIONS-FORMULAIRE.md` § 3.

### PHASE 3 — Socle technique partagé
Pars des templates `.claude/skills/nebula-site/templates/app.css` + `app.js` (gold standard
Djambar) → **adapte les tokens** (couleurs/typo) à la palette client, **retire** les blocs
spécifiques inutiles (hero-night, cta-video, formulaire devis…). Le socle pilote TOUT le site :
nav sticky + burger, boutons, cartes, galerie filtrable + lightbox, témoignages, localisation, CTA,
footer, FAB WhatsApp + FAB audio, `reveal` au scroll, `prefers-reduced-motion`, **audio baseline
mobile** (déblocage iOS + DynamicsCompressor + gain mobile, OFF par défaut).
**Cache-bust** `?v=AAAAMMJJx` sur app.css/app.js → **bumper à CHAQUE modif** du socle (sinon cache
périmé = « cassé sur PC, OK mobile »).

### PHASE 4 — Pages
**Vitrine** : `index.html` (hero kicker+titre+accroche+CTA WhatsApp, sections à-propos/valeurs,
services, galerie, avis, localisation, CTA, footer). **Hub multi-pages** (groupe) : accueil
ombrelle + 1 page/pôle actif + pages **« Bientôt »** (teaser + opt-in). **Catalogue** : grille
produits (image+nom+prix/« sur devis ») + filtres + lightbox + **commande WhatsApp pré-remplie**
(nom du produit dans le message). Communs : WhatsApp **pré-rempli par contexte de page**, Google
Maps + itinéraire texte, section avis, FABs, OG + favicon. **Anti-tells IA** (cf. EVOLUTION) :
pas d'eyebrow majuscule au-dessus de chaque section (2-3 max, moments signatures), pas de grille de
cartes identiques génériques, en-têtes éditoriaux variés (titre + deck sélective).

### PHASE 5 — Pipeline d'assets (`_build_assets.py`, Pillow)
Pars de `templates/_build_assets.py` (ré-exécutable). Génère : **logo** détouré (bbox alpha) →
blanc + noir + marque seule (nav) + **favicon** + **apple-touch** + **OG sociales** 1200×630 ;
**photos** `exif_transpose` → resize ~1080 → JPEG q82 progressive → `gallery/<cat>/gN.jpg` (sélection
espacée pour la variété, **watermarks client conservés**) ; **QR** (segno) WhatsApp + Maps (liens
**stables**, couleur navy). `pip install segno pillow` si besoin.

### PHASE 6 — QA réelle (navigateur) — voir § Pièges QA
1. `python -m http.server <PORT> --directory <dossier client>`.
2. **Captures Edge headless** desktop + mobile → relis les PNG (QA visuelle).
3. **Mesure overflow** : `over = scrollWidth > clientWidth` → **doit être 0** (mobile inclus).
4. **Hook `impeccable`** (auto) : corrige les vrais défauts ; **classe les faux positifs**
   (`single-font` = CSS partagé, la paire Cormorant+sans est bien là → faux positif).
5. **Tous les assets 200** (curl pages + images + css/js).

### PHASE 7 — Affiche PDF A4 + QR (si option formulaire)
`affiche.html` : `@page{size:A4;margin:0}`, **fond clair** (encre), `print-color-adjust:exact`.
Bandeau logo, marque + tagline, slogan serif, chips services, 3 photos, matières, **2 QR**
(WhatsApp « Commander » + Maps « Nous trouver »), tél, adresse + repère, « Suivez-nous », crédit
NEBULA. Rendu :
`msedge --headless --no-pdf-header-footer --virtual-time-budget=7000 --print-to-pdf=".../assets/docs/Affiche_<Marque>_A4.pdf" http://localhost:PORT/affiche.html`.
QA A4 (`--window-size=794,1123 --force-device-scale-factor=2`). **QR = liens stables** (jamais une
URL provisoire qui mourra) ; ajouter le QR « site » quand le **domaine final** existe.

### PHASE 8 — Mise en ligne (Cloudflare Pages)
1. **Build propre** `_dist/` : HTML + `assets/app.*` + `assets/images/{logos,favicon,og,gallery}`
   (+ `assets/videos/*` si utilisés). **Exclure** photos sources lourdes, `_build_assets.py`,
   `affiche.html`, `CONTEXT.md`.
2. `set -a; source secrets/cloudflare.env; set +a` (jamais afficher le token), puis
   `npx --yes wrangler@latest pages deploy _dist --project-name=<projet> --branch=main --commit-dirty=true`
   (idempotent : `pages project create <projet> --production-branch=main` si 1er déploiement).
3. **Lien `*.pages.dev` live** (HTTPS auto). Vérifie **200 + titre** en prod.
4. **Domaine custom** = étape **séparée, pas à pas** (DNS Hostinger → souvent action client) :
   procédure complète dans EVOLUTION (entrée V13). Le **token `cloudflare.env` est Pages-only**
   (ne crée pas de zone ni n'édite le DNS).

### PHASE 9 — Mémoire & livraison
1. **Mémoire** : `CONTEXT.md` client (à jour), table clients de `CLAUDE.md`,
   `_memoire/conversations/<date>-<client>.md`, `_memoire/journal/<date>-journal.md`, entrée
   `EVOLUTION.md` (toute leçon nouvelle).
2. **Git** : montrer les changements ; **stage sélectif** (jamais `git add -A`) ; commit clair +
   `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` ; **push selon autorisation**.
3. **Rapport final** : **lien live** + chemin **PDF** + **liste « À REMPLACER »** + étapes futures
   (domaine, vrais avis…).

---

## ✅ Checklist de pré-livraison (la boucle doit TOUTES les valider)
- [ ] Toutes les pages + assets répondent **200** (local **et** live).
- [ ] **0 débordement horizontal** (mesuré, mobile inclus).
- [ ] Liens **WhatsApp** pré-remplis OK ; numéro **confirmé** (sinon « à confirmer »).
- [ ] **Google Maps + itinéraire** présents (si adresse connue).
- [ ] **Galerie** filtrable + lightbox OK ; images optimisées + lazy-load.
- [ ] **Logo** intégré (nav/footer/favicon/OG) ; placeholders restants signalés.
- [ ] **Réseaux sociaux** : liens réels ou emplacements présents.
- [ ] Affiche **PDF A4** générée, sans débordement, QR stables (si option).
- [ ] Hook **`impeccable`** traité (défauts corrigés, faux positifs classés).
- [ ] A11y de base (contraste ≥ 4.5:1, focus visibles, alt, labels) ; `prefers-reduced-motion`.
- [ ] **Ergonomie mobile** : inputs `font-size:16px` (anti-zoom iOS) ; cibles tactiles ≥ 44px ; `html{overflow-x:hidden}` ; `touch-action:manipulation` + `-webkit-tap-highlight-color:transparent` ; effets lourds (canvas blur) gated `!isMobile && !saveData` ; FABs en `env(safe-area-inset-bottom)`.
- [ ] **Audio baseline mobile** intégré (OFF par défaut).
- [ ] **Cache-bust `?v=`** à jour sur app.css/app.js.
- [ ] Mémoire écrite + commit (push selon autorisation).

## 🛡️ Garde-fous (CONVENTIONS — non négociables)
- Secrets **jamais** affichés/commités (`secrets/*.env`) ; clé paiement secrète **jamais** côté client.
- **Stage git sélectif** ; **montrer avant commit** ; **ne pas pousser sans validation** (sauf routine autorisée).
- **Confirmer le n° WhatsApp** avant câblage ; ne jamais changer un lien WhatsApp sans confirmation.
- Contenu manquant = version **pro « à valider »**, jamais un vide ; **avis** = exemples marqués, **jamais** de faux avis présentés comme réels ; **0 fausse urgence / faux stock / faux chiffre**.
- **Watermarks** des photos client = conservés. Images **relatives** (multi-pages) ; **base64** = règle des mono-fichiers ; jamais de CDN Google Drive.
- **0 emoji en icône** → SVG. **Avertir des risques** sortants avant d'agir. **Vérifier avant d'affirmer**. **Réponses courtes**.

## 🧰 Briques & commandes
`/ui-ux-pro-max` (design system : *quoi*) → `/frontend-design` (esthétique BOLD : *comment*) →
Write socle + pages → `impeccable` (hook auto) → `_build_assets.py` (Pillow) → `segno` (QR) →
`http.server` + **Edge headless** (QA + mesure + PDF) → `wrangler` (deploy) → `git` + mémoire.
Edge : `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`. Détails : `SKILLS-ET-OUTILS.md`.

## ⚠️ Pièges QA headless (leçons EVOLUTION — éviter de les re-découvrir)
- **Boucle `requestAnimationFrame` infinie** (hero canvas beams) → `--screenshot` / `--dump-dom`
  **timeout**. Solutions : (a) captures statiques en **`--disable-javascript`** (le contenu est en
  *progressive enhancement* → visible sans JS) ; (b) pour tester que le JS s'exécute, plafonner rAF
  **avant** de charger le JS (`window.requestAnimationFrame` wrappé, stop après N frames) ; (c) le
  blur canvas en software-render est lent → réduire frames + taille. Toujours `timeout` + tuer les `msedge`.
- **`--window-size` ignoré en `--dump-dom`** (layout figé ~461/476px) → mesurer l'overflow dans le
  **DOM** (`scrollWidth` vs `clientWidth` + lister les éléments `getBoundingClientRect().right>clientWidth`),
  pas sur la largeur de l'image. Un screenshot « coupé à droite » est souvent un **artefact**
  (canvas plus étroit que le layout), pas un vrai débordement — vérifier avant de « corriger ».
- **Domaine tout neuf** : `curl https://domaine` peut renvoyer **000** alors que le site est live
  (cache DNS local en retard) → forcer l'IP : `curl --resolve domaine:443:188.114.96.5 https://domaine`.
- **`.btn` du socle = `white-space:nowrap`** → sur bouton pleine largeur à libellé long, passer
  `white-space:normal` ou raccourcir (sinon débordement réel sur petit écran).
- **`/tmp` peu fiable** dans ce shell → écrire les fichiers temporaires dans le **scratchpad** de session.
- **Édition `.py`/`.html`** : jamais via PowerShell `Set-Content` (mojibake) ; Edit/Write ou Python utf-8.
- **Vidéos de fond** : (1) **codec** — toute vidéo client (souvent iPhone = **HEVC/`hvc1`**, illisible Chrome/FF) → **transcoder en H.264** (vérifier `grep -a -o 'avc1\|hvc1' f.mp4` ; ffmpeg via `pip install imageio-ffmpeg` ; `-c:v libx264 -pix_fmt yuv420p -an -vf "scale='min(960,iw)':-2,fps=30" -crf 30 -movflags +faststart`). (2) **autoplay** — `muted`+`playsinline` forcés EN JS (pas juste l'attribut) + `play()` relancé (canplay/IO) + repli au 1er geste ; `preload="auto"` si above-the-fold. (3) **cache** — `/assets/* immutable` ⇒ **cache-buster l'URL vidéo `...mp4?v=`** quand le contenu change + **vérifier le contenu SERVI** (télécharger + grep codec), pas juste le 200. (4) **lisibilité** — vidéo derrière du texte = l'assombrir (brightness ~.5 + voile) ; hero clair → vidéo quasi invisible, basculer en cinématique sombre (`hero-night`+`hero-cine`).

## 📓 Journal des décisions (À TENIR À JOUR — 1 ligne par évolution)
Règle de Mongazi : « mets à chaque fois ce qu'on fait dans le skill ». Les leçons fines vont dans
`_memoire/procedure-vitrine/EVOLUTION.md` ; ici on note les évolutions **du skill lui-même**.
- **2026-06-23 — Création.** Distillé depuis la branche cerveau `_memoire/procedure-vitrine/`
  (PROCEDURE/CONVENTIONS/QUESTIONS/SKILLS/SPEC/EVOLUTION) après le gold standard Djambar Team
  (V1→V13 : hub multi-pages, socle partagé, galerie+lightbox, audio baseline, affiche PDF+QR,
  thème clair, SEO/JSON-LD, clean URLs, motion/View-Transitions, hero nuit beams, vidéo de fond,
  formulaire devis→WhatsApp, descriptions+commander partout, domaine `djambarteam.com` live).
  Templates de socle bundlés (`templates/app.css`, `app.js`, `_build_assets.py`).
- **2026-06-23 — 1er run réel : Miss cakes (#06).** Cas **mono-marque vitrine+catalogue commandable**
  (page unique, pâtisserie en ligne) → LIVE https://miss-cakes.pages.dev. Le pipeline tient hors hub
  multi-pages. **Template corrigé** : `.gitem` désormais gaté `.js` (galerie visible sans JS). Leçons
  ajoutées à EVOLUTION : numéro Bénin 8→10 chiffres « à confirmer », reveal horizontal pleine largeur
  = fuite overflow (préférer `.reveal-scale`), mesure overflow par iframe-diag, QA mi-page en
  `--disable-javascript`, placeholders « pro » (badge cupcake + tuiles SVG).
- **2026-06-24 — Miss cakes passe « spectaculaire ».** Après audit honnête (coquille soignée mais
  contenu réel manquant), demande « rends-la spectaculaire, animations partout ». Ajouté un **langage
  motion signature** (tout natif/GPU, reduced-motion complet) : coulures de glaçage (CSS mask), cake
  qui se dessine (`pathLength="1"`), mesh dérivant, sucre flottant, sheen/tilt/ripple/CTA aimantés.
  **Fix AA CTA** (rose poudré+blanc échoue → raspberry `#B44E69→#9A3450`, calcul luminance). **Garde-fou
  PE renforcé** : tout état caché en attente d'anim (dashoffset/opacity/scaleY) gaté `.js` sinon contenu
  invisible sans JS. **Honnêteté > imagerie stock** : pour un vrai commerçant, scènes SVG/canvas +
  placeholders marqués, jamais du stock déguisé en son produit (cf. EVOLUTION 2026-06-24).
- **2026-06-24 — Miss cakes : vraies images client intégrées.** La cliente fournit hero animé (mp4) +
  3 fonds (Nano Banana Pro). Patrons : hero = vidéo de fond (transcode H.264, cinemagraph 8 Mo→256 Ko,
  poster, voile crème côté texte) ; fonds de section = `.editorial .bg`, `.cta-photo`/`.cta-media`,
  `.has-photo`/`.sec-bg` (voiles calculés AA, attention `.cta>*{z-index:1}` qui attrape l'img). QA
  pleine page à fonds floutés = lente en headless → capturer étroit (mobile) + harnais iframe pour la
  lecture vidéo. Détails EVOLUTION 2026-06-24.
- **2026-06-24 — Miss cakes : motion signature PAR SECTION.** Donner à chaque section sa propre entrée
  sans casser PE/overflow : UN seul IO ajoute `.in`, des **variantes** par-dessus (clip/unfold/slide/
  stamp/perspective/scatter) + ambiances scroll-driven additives (parallax, Ken-Burns, lignes qui se
  tracent) + particules JS bornées (confettis/poussière, IO once, reduced-motion off). ⚠️ piège
  re-rencontré : tout `translateX`/`scale>1` sortant en pré-révélation déborde → scatter en translateY
  seul, slides clippés au niveau **section** (`overflow-x:clip`), tampon en scale<1. Nettoyer le code
  mort à chaque refonte (grep classe dans HTML = 0 ⇒ supprimer). Détails EVOLUTION 2026-06-24.
- **2026-06-24 — Boutons « Liquid Glass ».** Sur demande explicite (réf image), boutons en verre : corps
  teinté (AA) + reflet spéculaire (gloss ≤42% pour ne pas toucher le texte) + profondeur + liseré +
  dispersion chromatique (inset froid/chaud) + halo + `backdrop-filter`. WhatsApp vert approfondi pour
  AA. Fonds sombres → verre clair + texte blanc. Repli `@supports not(backdrop-filter)`. Détails EVOLUTION.

- **2026-06-24 — Passe CONVERSION (checklist).** Blocs réutilisables : FAQ `<details>` natif (0 JS, PE) + JSON-LD FAQPage · process 3 étapes (numéros légitimes) · bande garantie près du CTA · barre CTA collante mobile injectée JS (Devis WhatsApp + `tel:`), FAB WA masqué mobile + audio remonté + `body.has-mcta{padding-bottom}`. Contenu FAQ/garantie honnête. ~65% du gap « conversion » = contenu client (vrais avis, photos sans watermark, fiche Google Business). Détails EVOLUTION 2026-06-24.

- **2026-06-25 — RÈGLE D'OR (Mongazi) : CHAQUE SITE TOTALEMENT UNIQUE.** Deux sites NEBULA ne doivent
  **jamais se ressembler**, dans leur **entièreté** — pas seulement la couleur. Varier délibérément à chaque
  nouveau client : **disposition de la galerie / des images** (jamais la même grille ; ici Djambar = mosaïque
  bento à tailles variées, ailleurs masonry, colonnes, carrousel, plein-écran…), **tailles d'images non
  uniformes**, structure et ORDRE des sections, type de héros, grilles (asymétrie), système de motion,
  rythme typographique. Le socle partagé sert de moteur technique, **pas** de gabarit visuel : on le
  ré-agence et on change la présentation. Avant de livrer, se demander : « si je mets ce site à côté du
  précédent, se ressemblent-ils ? » Si oui → retravailler la composition jusqu'à ce que non.

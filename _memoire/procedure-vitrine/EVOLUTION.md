# JOURNAL D'ÉVOLUTION — procédure vitrine/catalogue

> Log **vivant**. Ajouter une entrée datée à chaque décision, apprentissage ou ajustement de méthode,
> jusqu'à ce que le skill soit créé (puis continuer à le faire évoluer).

---

## 2026-06-22 — Exécution de référence : Djambar Team / Saeir Thiam Bijouterie (#05)

### Contexte
Première exécution complète, end-to-end, qui sert de **gold standard** pour le futur skill.

### Décisions & apprentissages
- **Analyse du brief > formulaire** : la fiche disait « bijouterie » mais le brief révélait un **GROUPE Djambar Team** (la bijouterie est la locomotive). → architecture **hub multi-pages évolutif**, nom du **groupe** en tête, pôle = **Saeir Thiam Bijouterie**. **Leçon** : toujours analyser l'ampleur avant de coder.
- **`/ui-ux-pro-max` à écraser** : il proposait rose/or + liquid glass ; on a imposé **bleu nuit/blanc** (client) + verre **léger** (perf 4G). On a **gardé** sa reco typo de base puis ajusté.
- **Police** : Montserrat signalé « sur-utilisé » par `impeccable` → remplacé par **Jost** (plus de caractère, pairing luxe avec Cormorant). **Leçon** : écouter `overused-font`, classer `single-font` en faux positif (CSS partagé).
- **Images relatives, pas base64** : choix assumé pour un hub multi-pages (perf + évolutivité). La règle base64 vaut pour le mono-fichier.
- **Pipeline Pillow** (`_build_assets.py`) : détourage logo → marque arbre seule pour la nav + favicon + OG sociales ; 24 photos optimisées (3 catégories) ; watermarks client **conservés**.
- **QA mesurée** : capture Edge + page diag `--dump-dom` → **`over=0`** (0 débordement mobile). Le « cut » perçu sur les captures était un artefact de downscale d'aperçu, **pas** un bug réel. **Leçon** : mesurer, ne pas deviner.
- **Affiche PDF** : QR vers **WhatsApp + Maps** (stables), **pas** l'URL provisoire (le client prendra `djambarteam.com`). **Leçon** : sur l'imprimé, jamais d'URL périssable.
- **Déploiement** : `wrangler pages deploy` → **`*.pages.dev` live immédiat** sans DNS. Domaine custom = étape ultérieure (DNS). **Leçon** : livrer une URL live tout de suite, mapper le domaine après.
- **Réseaux sociaux** reçus après coup → câblés dans les 4 footers + ligne « Suivez-nous » de l'affiche → **redeploy**. **Leçon** : prévoir des emplacements réseaux dès le départ (placeholders), faciles à remplir.

### Outils nouveaux ajoutés à la boîte
- `segno` (QR), `uipro-cli`/`ui-ux-pro-max` (design system), Edge `--dump-dom` (mesure overflow).

### État
Site **LIVE** : https://djambar-team.pages.dev · Affiche PDF générée · poussé sur `main`.
Reste (client) : avis réels + horaires ; domaine `djambarteam.com` (mapping ultérieur).

### À intégrer dans le skill (issu de cette run)
- Étape « **détection d'ampleur** » (groupe vs simple vitrine) en PHASE 0.
- Bloc **réseaux sociaux** présent par défaut (placeholders) sur toutes les pages + affiche.
- Choix QR **stable** par défaut (WhatsApp+Maps), QR site ajouté quand domaine final connu.
- Garder le **pipeline d'assets** générique (logos/OG/galerie/QR) paramétrable par dossier.

---

## 2026-06-22 (suite) — Ajout de `frontend-design` à la boîte à outils
- Skill **`frontend-design:frontend-design`** (plugin officiel) invoqué et **intégré à la procédure** (PHASE 1, étape 4 ; orchestration SKILLS-ET-OUTILS § A/F ; SPEC § 6).
- **Rôle / complémentarité** : `ui-ux-pro-max` = *quoi* (design system data-driven) ; `frontend-design` = *comment le rendre mémorable* (direction esthétique BOLD anti-« AI slop » : typo distinctive, motion page-load, composition non générique, atmosphère). À enchaîner **après** le design system, **avant/pendant** l'écriture.
- ⚠️ Périmètre : `frontend-design` = **web responsive** ; pour un **canvas fixe** (affiche A4 / poster) → skill **visual-design**, pas frontend-design.
- À refléter dans le futur skill : étape « direction esthétique » distincte de l'étape « design system ».

## 2026-06-22 (suite) — Refonte visuelle V2 à partir d'une image d'inspiration
Mongazi a fourni une **capture d'inspiration** (`_partage/inspiration.jpg`) + consigne : s'en inspirer **profondément SANS sortir des envies du client**. Patterns dégagés (réutilisables par le skill) :
- **Traduire, pas copier** : on garde la **charte client** (ici bleu/blanc/or), on n'importe QUE la *structure/compo/animation* de la réf (sépia de la réf rejeté). Régle pour le skill : « inspiration = squelette & énergie, jamais la palette si le client en impose une ».
- **Composants éditoriaux réutilisables ajoutés au kit** :
  1. **Cartes Collections** (image + dégradé + libellé surimpression + liseré or), cliquables → filtre galerie + scroll.
  2. **Galerie masonry** : `grid-auto-rows:8px` + gap, **span calculé en JS** depuis la hauteur image (recalcul on load/resize/filter), hover (zoom + liseré or + légende), reveal échelonné. ⚠️ images en `loading=lazy` → recalcul on `load` ; défaut `span 24` pour limiter le saut.
  3. **Marquee** défilant (`white-space:nowrap` + `overflow:hidden` OBLIGATOIRE sinon débordement ; translateX -50% avec 2 segments identiques ; pause hover ; off si reduced-motion).
  4. **Bandeau éditorial à image de fond** (photo produit traitée Pillow + voile dégradé navy + `background-attachment:fixed` desktop) → ancrage émotionnel.
- **Traitement Pillow d'une photo en fond** : recadrage large 16:10, `GaussianBlur` léger, `Brightness 0.6`, **blend multiply navy 0.55** pour forcer la charte, q80. + voile CSS dégradé par-dessus (contraste texte AA).
- **Vérif anti-régression** : à chaque refonte, **remesurer `over=0`** (le marquee/nowrap peut déborder) + **DOM-dump** des hauteurs si masonry (ne pas se fier aux captures headless : `decoding=async` non peint).
- À intégrer au skill : ces 4 composants comme **blocs optionnels** activables selon le secteur (la galerie masonry + collections = idéal bijouterie/mode/déco).

## 2026-06-22 (suite) — « S'inspirer » = capturer le MOOD, pas juste la structure
Leçon forte (le client a dû recadrer) : quand on donne une image d'inspiration, il veut **l'ambiance globale** (ici : sombre, immersif, cinématographique), pas seulement des composants ajoutés sur un thème clair. **Règle pour le skill** :
- **Identifier le THÈME de l'inspiration** (clair vs **sombre**, dense vs aéré, mood) AVANT de coder, et l'appliquer à **tout le site** — puis le **traduire dans la palette client** (ici « bleu/blanc » imposé → interprété en **sombre bleu nuit + blanc + or**, parfaitement valide).
- **Hero = photo produit dramatique en fond** + voile dégradé navy (pattern fort de l'inspiration). Choisir une photo client déjà sur fond sombre/coloré (ici collier sur **velours bleu** = idéal, déjà dans la charte).
- **Bande « GET SOCIAL »** (grille de vignettes → Instagram) = pattern social de l'inspiration, conforme (renvoie au compte).
- **Honnêteté** : ne PAS copier les fausses urgences de l'inspiration (badges « -50% », compte à rebours) pour un vrai commerçant sans promo réelle. Reprendre le **traitement visuel**, pas le mensonge commercial.
- **QA visuelle obligatoire après réécriture CSS** : un token couleur invalide (`--gold-deep:#B8924`, 5 chiffres) cassait les boutons or — invisible sans regarder le rendu. Toujours screenshoter + corriger.
- Thème sombre : prévoir tokens `--bg/--bg-2/--bg-3`, surfaces en **verre** (`rgba(255,255,255,.035)` + bordure `.10`), texte clair, nav verre sombre, map `filter:grayscale(.2)`.

## 2026-06-22 (suite) — Grille « 10 000 $ » : patterns pour franchir le niveau premium
Mongazi a fait auditer le site contre 2 check-lists (« 10k$ vs 200$ » et « IA vs pro »). Honnêteté exigée. Verdict : belle COQUILLE, moitié contenu/invisible manquante. Corrections check-list 1 appliquées → **patterns réutilisables pour le skill** :
- **Imagerie (le tell n°1)** : des **photos catalogue WhatsApp** (fonds hétérogènes + watermark) = signature « 200$ ». Pipeline d'art-direction (`_build_gallery_v2.py`) : **curate** (meilleures sources) + **grade unifié** (autocontrast léger, contraste +, luminosité -, blend multiply navy 0.10) + **vignette radiale** (assombrit bords → focus produit + noie fonds/watermarks) + crops cohérents. NE PAS retirer un watermark client sans son accord (anti-vol). Dire la vérité : le vrai cran = reshoot fond noir.
- **Motion sans le tell AOS** : `<html>.js` (script inline AVANT le CSS) ; `.js .reveal{opacity:0}` → **sans JS = visible** (jamais cacher le contenu derrière une classe). **Hero = séquence chorégraphiée au chargement** (stagger nth-child + keyframes `forwards`), pas un fade-up uniforme. Toujours fallback `prefers-reduced-motion`.
- **Perf / « invisible »** : polices Google **non-bloquantes** (`rel=preload as=style onload=this.rel='stylesheet'` + `<noscript>`), **preload de l'image hero**, `canonical` + `og:url`, `theme-color` = couleur du fond réel.
- **Contraste AA = par le calcul, pas à l'œil** : petit script luminance relative ; viser ≥4.5 (texte) / ≥3 (grand). Les thèmes sombres passent facilement, mais le VÉRIFIER.
- **Mobile = décisions, pas rétrécissement** : `background-position` qui garde le sujet cadré, tailles de marquee dédiées, légendes visibles au tap (pas de hover tactile).
- **Le design ne sauve pas le fond** : un thème (clair/sombre) ne corrige NI les photos watermarkées, NI les faux avis, NI l'absence de SEO/analytics/domaine. Pour un vrai « 10k », prévoir dès le devis : photos pro, vrais témoignages + signaux de confiance, domaine, analytics, schema, tests réels.

## 2026-06-23 — Check-list 2 (IA vs pro) : SEO + conversion + analytics → patterns skill
- **SEO technique = systématiser** dans le skill (souvent oublié) : JSON-LD **LocalBusiness/JewelryStore** (nom, adresse, `openingHoursSpecification`, `telephone`, `makesOffer`, `sameAs` réseaux, `hasMap`) sur la page commerce + **Organization** sur l'accueil (lier via `subOrganization`/`parentOrganization`) ; **robots.txt** + **sitemap.xml** par défaut. Valider le JSON-LD (parse strict) avant deploy.
- **Conversion honnête** : barre de confiance avec piliers **VRAIS et vérifiables** (fait main, matières, sur-mesure, devis gratuit) + microcopie de réassurance près des CTA (gratuit · sans engagement · réponse rapide). **JAMAIS** de faux chiffres (« 500 clients »), fausse urgence ou faux avis — règle dure (cf. l'inspiration qui en abusait). Vrais avis = livrable client, pas à inventer.
- **Analytics gratuit sans CB** : sur Cloudflare Pages → **Cloudflare Web Analytics** (cookieless). ⚠️ le token de déploiement Pages n'a pas le scope RUM/Analytics (`/accounts/{id}/rum/...` → 10001) → activation = **1 clic dashboard** (à déléguer au client/Mongazi), ne pas injecter de script non fonctionnel.
- **Perf à chiffrer** : mesurer le poids 1er écran (curl -A) + TTFB ; viser <200 Ko 1er écran, polices non-bloquantes, images lazy. Donner un vrai chiffre, pas « c'est rapide ».
- **Le design ne remplace pas** : un site « beau » reste 200$ s'il manque SEO/analytics/contenu réel. Le skill doit traiter ces couches « invisibles » par défaut, pas seulement le visuel.

## 2026-06-23 (suite) — Bascule de thème (sombre↔clair) + clean URLs Cloudflare : patterns skill
- **Changer de thème = vérifier la NAV en priorité** (tell récurrent) : sur un hub multi-pages, la nav est partagée mais les heros diffèrent (clair vs sombre par page). Pattern robuste à mettre dans le skill : **nav sombre par défaut** (sûr sur fond clair) + une classe `body.dark-hero` posée UNIQUEMENT sur les pages à hero sombre → nav claire au sommet, repasse sombre dès `.scrolled`. Sans ça : texte/logo blancs **invisibles** sur hero clair (bug silencieux, pas vu sans QA visuelle). Toujours **2 jeux de logo** (mark + full, clair ET sombre) prêts.
- **Reprendre un travail non commité d'une session précédente** : d'abord `git diff` pour comprendre l'intention réelle (ici un virage sombre→clair à moitié fait que le journal ne mentionnait pas) ; si ça change toute la suite, **demander à Mongazi** (AskUserQuestion) avant de foncer, plutôt que deviner.
- **Clean URLs = règle par défaut sur Cloudflare Pages** : la plateforme redirige `/page.html` → **308** → `/page`. Donc pointer canonical/og:url/JSON-LD/sitemap/liens internes vers `*.html` = faire payer un hop de redirection à chaque clic + signal SEO faible. **Systématiser** dans le skill : liens internes **root-relative sans extension** (`/`, `/bijouterie`), pareil pour canonical/og:url/sitemap/breadcrumb. ⚠️ le `python -m http.server` local NE sert PAS les clean URLs → faire la QA des clean URLs **en prod** (curl `-w %{http_code}` doit donner 200 direct, pas 308). Garder les fichiers nommés `.html` sur disque (Pages mappe tout seul).
- **SEO structuré complet** : au-delà de LocalBusiness/Organization, ajouter **WebSite** (accueil) + **BreadcrumbList** (pages internes) = quasi gratuit, signal « pro ».
- **CLS = 0 par le calcul** : mesurer les dimensions réelles des images (ici toutes 1080² carrées) → si ratio constant, régler par `aspect-ratio` CSS + `width/height` sur les `<img>` plutôt qu'au cas par cas. `fetchpriority="high"` sur l'image/logo LCP.
- **Contraste AA à REVÉRIFIER après tout changement de thème** : un thème clair ne passe pas « automatiquement » — recalculer (script luminance) les couples texte/fond (or sur crème = le plus juste, viser ≥4,5). Idem skip-link a11y à garder sur toutes les pages.
- **Perf = chiffrer en prod** (compressé CDN) : `curl --compressed -w "%{time_starttransfer} %{size_download}"` par ressource → additionner le 1er écran. Donner le Ko réel, pas « c'est rapide ».

## 2026-06-23 (V7) — IA vs pro : tuer les *tells structurels* (pas que SEO/perf)
Les passes V5/V6 avaient traité les couches invisibles (SEO/perf/a11y/clean URLs). Restaient les **tells visuels** que les référentiels frontend-design + impeccable flaguent comme « signature IA ». À systématiser dans le skill :
- **Eyebrow = poison par défaut.** Un mini-libellé majuscule tracké (`.kicker`) au-dessus de **chaque** section = LE tell n°1 (présent sur 55-95 % des générations IA). Règle : un kicker **nommé et délibéré** = voix de marque ; un eyebrow sur chaque section = grammaire IA. Plafonner à **2-3 par page**, sur des moments signatures (hero, bandeau signature, CTA de clôture). Partout ailleurs : **le titre serif porte la section**, + une `.deck` (phrase de présentation) ajoutée **sélectivement** (sinon la deck devient le nouveau réflexe uniforme). Ici : 4/9/3/3 → 2/3/2/2.
- **Grille de N cartes identiques (icône+titre+1 ligne) = ban.** Surtout quand le contenu est du remplissage générique (« le détail à chaque étape »). Remplacer par une **surface éditoriale unique** (ici panneau `.creed` navy, lignes séparées par filets, raccordé à l'accent de marque) + **copy spécifique et vérifiable**. Garder les vraies grilles (services distincts, matières) — le tell c'est l'*identique générique*, pas la grille en soi.
- **Cadence variée** > uniformité : alterner en-têtes centrés titre-seul / gauches titre+deck / un seul moment à kicker. La règle impeccable : « le tell c'est le réflexe uniforme », pas tel ou tel élément.
- **QA headless robuste** : la boucle `requestAnimationFrame` du hero (canvas beams) empêche Edge `--headless --screenshot` de **sortir** (timeout). Solution : capturer avec **`--disable-javascript`** → comme le contenu est en *progressive enhancement* (`.js .reveal{opacity:0}` ⇒ sans la classe `.js`, tout est visible), le rendu statique est **propre et complet**, et le navigateur quitte. Idéal pour vérifier layout/typo/structure (pas la fidélité des photos `decoding=async`). Toujours `timeout` + tuer les `msedge` restants.
- **Hygiène** : après retrait d'un kicker, retirer aussi la classe `.eyebrow-gap` du `<h2>` (sinon marge haute orpheline). Unifier le `?v=` sur **toutes** les pages d'un coup (elles se désynchronisent vite : index en `c`, le reste en `b`).

## 2026-06-23 (V8) — Motion premium « fluide » SANS lib + pièges, pour le skill
Objectif client : « plus d'animation et de fluidité, mobile surtout ». Patterns à systématiser (tout natif, 0 dépendance CDN = robuste sur 4G Cotonou) :
- **Transitions de page = View Transitions cross-document** (`@view-transition{navigation:auto}` dans le CSS partagé). Sur un **hub multi-pages**, c'est LE gros gain de fluidité (fondu entre pages), gratuit, progressif (ignoré si non supporté), marche mobile+desktop. Les 2 pages doivent avoir l'at-rule (CSS partagé = ok d'office).
- **Parallax / progression = scroll-driven CSS** (`animation-timeline:scroll()` / `view()`), PAS de listener scroll qui anime : hors main-thread, fluide au tactile, 0 jank. Toujours `@supports (animation-timeline:scroll())` + état par défaut **visible/neutre** si non supporté. Repli JS rAF **passif** seulement si besoin (barre de progression).
- **Reveals : différencier** (panneau qui glisse, liste en stagger, image en scale) — le fade-up identique sur chaque section EST le tell IA (cf. brand.md). Easing **expo/quint** (`cubic-bezier(.16,1,.3,1)`), jamais bounce/elastic.
- **Mobile = `:active`, pas `:hover`** : sur tactile il n'y a pas de survol → mettre des états `:active{transform:scale(.95)}` sur boutons/cartes/liens pour le **feedback au toucher**, sinon le mobile paraît « mort ». Menu mobile en entrée échelonnée (nth-child + transition-delay quand `.open`). Effets desktop (tilt, aimant, halo) gardés derrière `(hover:hover) and (pointer:fine)`.
- **`will-change`/`isolation` avec parcimonie** : `isolation:isolate` sur un bouton pour qu'un `::after` en `z-index:-1` (le sheen doré) reste AU-DESSUS du fond mais SOUS le texte (sinon il passe derrière tout le bouton).
- **Filet de sécurité reveal** (règle impeccable) : le contenu gaté par `.js .reveal{opacity:0}`+IO peut **ne jamais apparaître** sur un rendu headless / onglet caché / crawler (l'IO ne se déclenche pas → section blanche). Ajouter au `window.load` un timer qui révèle ce qui est **déjà au-dessus/dans le viewport**, sans tuer le scroll-reveal des sections plus bas. (Idéalement : défaut visible + animation additive.)
- **QA motion en headless** : `--screenshot` et `--dump-dom` **hangent** si le hero a une boucle `requestAnimationFrame` infinie (canvas beams) → timeout. Astuces : (1) screenshots statiques en `--disable-javascript` (PE = contenu visible) ; (2) pour vérifier que le JS **s'exécute sans throw**, `--dump-dom` sur une page **sans** la boucle rAF (ici les pages « Bientôt » n'ont pas le canvas) → on voit les éléments injectés par JS (barre de progression, halo) et l'absence d'erreur. Toujours `timeout` + tuer les `msedge`.
- **🐛 Leçon propagation (récurrente, à mettre en garde-fou skill)** : un overlay de hero pensé pour UN thème casse l'autre. Ici le **voile blanc `.hero::before`** (hero clair à photo) **délavait les heros sombres `soon-hero`** → texte blanc illisible sur 2 pages LIVE, non vu à la bascule clair V6. **Règle** : tout `::before/::after` de voile sur une classe partagée (`.hero`) doit être **neutralisé/inversé** sur les variantes de thème opposé (`.hero.soon-hero::before`). QA visuelle de **toutes** les variantes de hero après tout changement d'overlay.
- **Infra « pro » par défaut (B7)** sur Cloudflare Pages : **`404.html` de marque** (Pages le sert auto, vrai statut 404) + **`_headers`** (HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy + `Cache-Control: immutable` sur `/assets/*` puisqu'on cache-bust en `?v=`). **Pas de CSP stricte** si le site a des handlers inline légitimes (onload des fonts, `classList.add('js')`) — elle les casserait ; la poser proprement = nonces/refonte, hors scope vitrine.

## 2026-06-23 (V9) — Intégrer un composant React/shadcn dans une vitrine HTML statique + canvas nuit
- **« Intègre ce composant React/shadcn » sur une vitrine HTML pure = NE PAS scaffolder React.** Le client envoie souvent un snippet `tsx` (motion/react, `@/components/ui`, Tailwind) trouvé sur 21st.dev/shadcn. Installer React+shadcn+Tailwind+TS+motion casserait tout le modèle (statique Cloudflare Pages, perf 4G). **Règle skill** : porter **l'effet** en natif (canvas/CSS/vanilla JS) — dire honnêtement pourquoi, et livrer le même rendu. Ici l'effet « Beams Background » existait déjà en port vanilla → réutilisé. (Le `motion/react` = juste des reveals transform/opacity + un overlay qui respire → trivial à refaire en CSS keyframes.)
- **Hero sombre à faisceaux lumineux** : sur fond sombre, le canvas de faisceaux doit être en **`mix-blend-mode:screen`** (ajoute de la lumière) ; sur fond clair c'est **`multiply`** (teinte). Même moteur JS, un flag `night = hero.classList.contains('hero-night')` qui monte le nombre/luminosité/opacité des beams. Couleurs **de marque** (or 40-48° + azur 212-226°), jamais le cyan/violet 190-260° du snippet d'origine. Plafonner les beams sur mobile (16) ; pause hors-écran/onglet caché (IntersectionObserver) ; `prefers-reduced-motion` = 1 frame figée.
- **Art-direction par section assumée** : un seul hero peut basculer en thème opposé (ici hero Bijouterie NUIT au milieu d'un site clair) — le register *brand* l'autorise (« different sections can have different visual worlds »). Gérer la **nav** (`body.dark-hero` → blanche au sommet, sombre au scroll) + `theme-color` du hero + la **transition** vers le contenu clair en dessous.
- **🎥 Capturer un canvas animé en headless** (boucle `requestAnimationFrame` infinie = `--screenshot`/`--dump-dom` **timeout**) : harnais same-origin qui **plafonne rAF AVANT de charger le JR** (`window.requestAnimationFrame = wrap qui s'arrête après N frames`) → la page peint N frames puis passe **idle** → capture possible. ⚠️ le **blur canvas en software-render (`--disable-gpu`) est très lent** → réduire N (~12) et la taille (mobile) sinon timeout ; le rendu soft **sous-représente** l'effet (le vrai navigateur/GPU est plus vif). Ne jamais déployer le fichier-harnais (le construire hors du dossier de staging).

## 2026-06-23 (V10) — Vidéo de fond dans un panneau (CTA) : recette réutilisable
- **Vidéo de fond = `<video autoplay muted loop playsinline preload="metadata" poster=...>`** + `<source ... type="video/mp4">`. `muted`+`playsinline` = **obligatoires** pour l'autoplay mobile. `poster` = repli image (autoplay bloqué / 4G lente) = pas de trou noir.
- **Flou gaussien « léger mais on voit la scène »** : `filter:blur(5px) brightness(.6) saturate(1.06)` + `transform:scale(1.12)` (le scale couvre le bord flou qui sinon laisse voir le fond). + un **voile** semi-opaque (`.cta-veil`, ~0,5) pour garder le texte lisible. Régler blur 5→8px selon « léger » vs « marqué ».
- **Scoping** : ne PAS toucher la classe partagée (`.cta` est sur plusieurs pages) → classe modifieur `.cta-video` + `<video>` ajouté **seulement** dans le panneau visé. `isolation:isolate` sur le conteneur → stacking propre (vidéo+voile z-index 0, contenu z-index 1) ; spécificité `.cta-video .cta-media` (2 classes) > `.cta>*` (1 classe) pour gagner sur le z-index/position du contenu.
- **Perf (4G/mobile)** : `preload="metadata"` (ne télécharge la vidéo que quand utile) + **IntersectionObserver** qui `play()`/`pause()` selon la visibilité (économie décodage/batterie) + **pause si `prefers-reduced-motion`** (poster figé). Garder la vidéo **légère** (ici 1,77 Mo ; < 25 Mo = limite/fichier Cloudflare Pages). `.play().catch()` pour avaler le rejet d'autoplay.
- **Déploiement** : penser à **copier `assets/videos/*` dans le staging** (le build copiait surtout images+gallery). Pages sert le `.mp4` en `video/mp4` + Range par défaut ; le `_headers /assets/* immutable` couvre aussi la vidéo (cache long, OK car nom/chemin stable).

## 2026-06-23 (V11) — Formulaire qualifiant → WhatsApp pré-rempli (sans backend) : recette skill
- **Modèle « no-backend »** : un formulaire qui **assemble les réponses en texte** et ouvre `https://wa.me/<num>?text=encodeURIComponent(msg)`. Zéro serveur, zéro base — parfait pour vitrine. `window.open(url,"_blank","noopener")` avec repli `location.href=url` si popup bloquée. **`encodeURIComponent`** gère les accents (UTF-8) → garder le français correct dans le message.
- **Choix multiples = pills tactiles** : `<label class="choice"><input type="radio"><span>…</span></label>`, l'input en `opacity:0` couvrant le label, `input:checked + span` stylé (dégradé or). Mobile-friendly (grande zone tap), accessible (`:focus-visible` sur le span).
- **Champ conditionnel** : afficher la **taille de bague uniquement si Bague/Alliance** (listener `change` sur le groupe radio + `field.hidden`). À généraliser : ne montrer un champ que quand il a du sens.
- **Validation douce** : `novalidate` + check JS des requis → classe `.field.invalid` (label rouge + input encadré) + `scrollIntoView` vers le 1er manquant + focus. Pas de `required` natif (messages navigateurs moches/incohérents).
- **Parcours qualifié** : rediriger les CTA « commander » génériques vers le **formulaire (`#devis`)** plutôt que vers un WhatsApp vide → le commerçant reçoit une demande **structurée** (service, bijou, matière, motif, gravure, échéance…), pas juste « bonjour ».
- **Honnêteté** : pas de tranche de budget inventée → le prix se discute sur WhatsApp. Astuce « envoyez une photo dans la conversation » plutôt qu'un upload (pas de stockage).
- **🔬 Vérifier la GÉNÉRATION, pas juste le visuel** : harnais qui extrait la section `<form>` réelle + le vrai `app.js`, **stub `window.open`** pour capturer l'URL, autofill + `requestSubmit()`, puis **décoder l'URL `wa.me`** et vérifier chaque champ (dont le conditionnel). C'est le seul test qui prouve que le formulaire *fait* la bonne chose.
- **⚠️ Piège QA headless mobile (important)** : Edge `--headless --screenshot --window-size=390` peut **mettre en page à une largeur ≠ de la largeur d'image** (observé : layout 476–496px alors que l'image fait 390px) → le rendu **paraît « coupé à droite »** alors qu'il n'y a **aucun overflow réel**. Ne PAS « corriger » un faux overflow sur la foi d'une capture. **Mesurer dans le DOM** : `document.documentElement.scrollWidth` vs `clientWidth` + lister les éléments dont `getBoundingClientRect().right > clientWidth` = la vérité. (`--window-size` aussi ignoré en `--dump-dom`.) Pour voir tout le layout sans crop : prendre une fenêtre **plus large** que le layout effectif.
- **Boutons larges sur mobile** : le `.btn` du site est `white-space:nowrap` (ok pour des libellés courts) → sur un bouton pleine largeur à libellé long, forcer `white-space:normal` (ou raccourcir le texte) sinon risque de débordement réel sur très petit écran.

## 2026-06-23 (V13) — Brancher un domaine (acheté Hostinger) sur Cloudflare Pages : procédure
Recette validée à mettre dans le skill (cas « domaine final »). Pré-requis : domaine acheté chez un registrar (ici Hostinger), site déjà sur Cloudflare Pages.
- **Toujours d'abord diagnostiquer le DNS** (`nslookup -type=NS`, `-type=MX`, A) : connaître les nameservers actuels + s'il y a un email (MX) à préserver. Ici parking `*.dns-parking.com`, **pas de MX** → bascule sans risque.
- **Méthode recommandée = confier le DNS à Cloudflare** (vs garder le DNS au registrar) : 1 seul changement (nameservers) côté registrar, puis apex + www + **SSL auto gratuit**. L'apex sur Pages en DNS externe est galère (pas de CNAME apex hors flattening) → Cloudflare règle ça.
- **Rassurer le client** : déplacer les nameservers **ne déplace pas le domaine** — il reste sa propriété chez le registrar ; seul le *DNS* est géré par Cloudflare. (Hostinger affiche « DNS géré ailleurs / remettez nos nameservers » = **normal, à ignorer**, ne pas revenir en arrière.)
- **Étapes (étape par étape, dashboards du client)** : (1) Cloudflare « Add a site » → domaine → plan Free → récupérer les 2 nameservers ; (2) registrar → nameservers personnalisés = ceux de Cloudflare ; (3) attendre activation (vérifier soi-même par `nslookup -type=NS @8.8.8.8`) ; (4) **Cloudflare Pages → projet → Custom domains** = apex + www ; (4b) **créer les 2 CNAME proxied** dans la zone (`@` et `www` → `<projet>.pages.dev`) si Pages ne les a pas auto-créés (cas fréquent si on a supprimé les enregistrements de parking) ; (5) migration des URLs du site.
- **⚠️ Token Cloudflare « Pages » ≠ token DNS/Zone** : un token de déploiement Pages **ne peut PAS** créer de zone (`zone.create` refusé) ni éditer le DNS d'une nouvelle zone. Donc add-site + nameservers + CNAME = **à la main par le client** au dashboard. (Pour automatiser un jour : token avec `Zone:Edit` + `DNS:Edit`.) Le POST `pages/projects/<p>/domains` lui marche (ajout custom domain) — utile pour vérifier le statut (`GET .../domains` → pending/active).
- **🩺 Piège de vérification : cache DNS local en retard.** Juste après la mise en place, `curl https://domaine` peut renvoyer **000** depuis la machine de dev alors que **le site est bien en ligne** — le resolver local (box/routeur) n'a pas encore le domaine tout neuf. **Vérifier en forçant l'IP Cloudflare** : `curl --resolve domaine:443:188.114.96.5 https://domaine` (IP vue via `nslookup domaine 8.8.8.8`). 200 = c'est live ; le 000 était local. Ne pas conclure « cassé » sur la foi du resolver local.
- **Migration des URLs après go-live** : remplacer **toutes** les occurrences `<projet>.pages.dev` → `https://<domaine>` dans canonical, og:url, JSON-LD, `sitemap.xml`, `robots.txt` (Sitemap:) → revalider le JSON-LD → redeploy. Sinon Google indexe l'ancienne adresse.
- **Restant optionnel** : redirect **www→apex** (Cloudflare Redirect Rule / Bulk Redirect) ; régénérer l'**affiche/QR** vers le vrai domaine.

## 2026-06-23 — SKILL `nebula-site` CONSTRUIT (depuis cette branche)
- Skill **`nebula-site`** installé dans `.claude/skills/nebula-site/` : `SKILL.md` (runbook exécutable PHASE 0→9 + règle run-to-completion + checklist pré-livraison + garde-fous + pièges QA) + `templates/` (socle gold standard copié de Djambar : `app.css`, `app.js`, `_build_assets.py`, `_build_gallery_v2.py`, en-têtés « TEMPLATE — à adapter par client »).
- **`.claude/` est gitignoré** (`.gitignore` l.15, « config locale machine, skills installés ») → comme `studio-quotidien`, le skill vit en local ; la **source versionnée = cette branche**. Copie canonique du SKILL.md mirrorée ici (`_memoire/procedure-vitrine/SKILL.md`). Procédure de réinstallation notée dans `README.md`.
- **Nom** : d'abord `vitrine-express` (provisoire), renommé **`nebula-site`** par Mongazi. Le skill se déclenche par dossier (`.claude/skills/nebula-site/`) + frontmatter `name: nebula-site`.
- ⚠️ Ne pas bundler de `__pycache__` dans les templates (bytecode, créé par `py_compile` — supprimé).
- **Reste à faire** : tester `nebula-site` sur un **nouveau formulaire client** (run-to-completion réel) → comparer à Djambar Team, puis itérer (ici + dans le SKILL.md).

## 2026-06-23 (V14 Djambar) — Fonds média réutilisables (image/vidéo) + dosage flou
- **Pattern `.soon-media`** (réutilisable, ajouté au socle) : un `<img>` OU `<video>` en fond plein écran (`object-fit:cover`, z-index 0) + `.soon-media-veil` (voile navy dégradé) pour garder le texte blanc lisible. Marche pour image (collier) et vidéo. JS bg-vidéo **généralisé** : `querySelectorAll("video.cta-media, video.soon-media")` → pause hors-écran (IntersectionObserver) + pause/retrait si `prefers-reduced-motion`.
- **Dosage flou « on voit l'image »** : flou de fond **8–9px** (image hero/éditorial), **4px** pour une vidéo (« très léger »). Le **voile** (pas le flou) porte la lisibilité → on peut alléger le flou tant que le voile reste assez dense.
- **Contraste sur média assombri = à CALCULER** : `composite = img*(1-veil) + navy*veil`, prendre le **pire cas** (zone claire du média ~blanc → brightness(.5)). Viser ≥ 4,5 pour le texte blanc. Ici voile navy ~.66→.82 + brightness .5 → pire cas 4,8–4,9 ✓.
- **Art-direction par page** : le même socle sert un fond **collier** (image) sur une page et un fond **vidéo** sur une autre (pages « Bientôt »), + un fond ghosté subtil sur un hero **clair** (sous le voile blanc — `::before` z-index 1 > bg z-index 0, le texte sombre reste lisible).
- **⚠️ QA headless** : une **animation CSS infinie** (ex. `.marquee`) empêche `--screenshot` de « settle » même en `--disable-javascript` (timeout) → screenshoter plutôt une page **sans** l'animation infinie, ou accepter le timeout et valider par le calcul + la structure. (Les pages « Bientôt » sans marquee se rendent, l'accueil avec marquee timeoute.)

## 2026-06-23 (V14b) — Vidéo de fond qui « ne bouge pas » : autoplay fiable
Symptôme : la vidéo de fond reste figée sur le poster. Causes + correctif (intégré au socle) :
- **`preload="metadata"` sur une vidéo de fond en haut de page = pas assez bufferisé pour démarrer en autoplay** → mettre **`preload="auto"`** sur une vidéo hero (qui doit jouer tout de suite). Garder `metadata` pour une vidéo sous la ligne de flottaison (joue au scroll).
- **Forcer `muted` EN JS** (pas seulement l'attribut) : `vid.muted=true; vid.defaultMuted=true; vid.playsInline=true;` — certains navigateurs n'autorisent l'autoplay que si la propriété (pas juste l'attribut) est vraie au moment du `play()`.
- **Relancer `play()`** à `loadeddata`/`canplay` + si `readyState>=2`, `vid.load()`, et **repli au 1er geste** (`pointerdown`/`touchstart` once) si `play()` est rejeté. IntersectionObserver `threshold:0.01` pour (re)jouer dès visible / pause hors-écran.
- **Vérifier réellement la lecture en headless** : `--autoplay-policy=no-user-gesture-required` + lire `video.paused`/`currentTime`/`readyState` (écrire dans `document.title`, `--dump-dom`). OK = `paused=false`, `currentTime>0`, `readyState=4`.

## 2026-06-23 (V16) — Vidéos client : codec H.264 obligatoire + cache-bust + hero cine
- **⭐ RÈGLE DURE : transcoder toute vidéo client en H.264** avant de l'utiliser sur le web. Les vidéos d'iPhone sont en **H.265/HEVC** (`hvc1`) par défaut → **ne se lisent PAS dans Chrome/Firefox** (Safari/iOS oui) = « la vidéo ne marche pas / écran noir ». **Toujours vérifier le codec** (`grep -a -o -E 'avc1|hvc1' file.mp4`) et transcoder si HEVC. ffmpeg système souvent absent → **`pip install imageio-ffmpeg`** fournit un binaire (`imageio_ffmpeg.get_ffmpeg_exe()`). Commande bg muet : `-c:v libx264 -pix_fmt yuv420p -an -vf "scale='min(960,iw)':-2,fps=30" -crf 30 -movflags +faststart` (≈ 1-2 Mo, parfait 4G ; `+faststart` = lecture avant fin du téléchargement ; `-an` = sans audio car fond muet).
- **🐛 Cache immutable + remplacement de contenu** : avec `_headers` `/assets/* immutable`, **remplacer le contenu d'un fichier au même nom (vidéo/image) ne se propage PAS** (le CDN/navigateur sert l'ancien pendant 1 an). → **cache-buster aussi les médias** qui changent : `...mp4?v=AAAAMMJJx` (pas seulement app.css/js). Vérifier le **contenu réellement servi** (télécharger + `grep avc1/hvc1`), pas juste le HTTP 200.
- **Hero vidéo lisible** = sombre. Une vidéo de fond derrière du texte doit être **assombrie** (brightness ~.5 + voile uniforme ~.66-.74) pour garder le texte blanc lisible (≥4.5). Sur un hero CLAIR, la vidéo sous voile blanc est quasi invisible (« on ne voit pas que ça tourne ») → si le client veut la vidéo VISIBLE, basculer le hero en **cinématique sombre** (réutiliser `hero-night` + un voile uniforme `hero-cine`), texte blanc, logo blanc, `body.dark-hero` pour la nav.

## 2026-06-23 (V17) — Checklist « ergonomie & fluidité mobile » (à systématiser dans le skill)
Six réglages à appliquer d'office sur toute vitrine (mobile-first, Afrique 4G/téléphones modestes) :
1. **Inputs `font-size:16px` minimum** → sinon iOS zoome au focus (saut de viewport). Non négociable sur tout `<input>/<textarea>/<select>`.
2. **Cibles tactiles `min-height:44px`** (boutons-pills, filtres, petits liens d'action) — confort du pouce.
3. **`html{overflow-x:hidden}`** (PAS seulement `body`) — un fond scalé (vidéo/photo `scale(1.06+)`) ou un marquee peut fuir quelques px et créer le « wiggle » latéral ; le `body` seul ne le contient pas toujours. **Mesurer** `scrollWidth>clientWidth` dans le DOM, pas à l'œil.
4. **`touch-action:manipulation` sur `a`/`button`** (supprime le délai 300ms + double-tap-zoom) + **`-webkit-tap-highlight-color:transparent`** sur `html` (pas de flash gris natif au tap).
5. **Effets lourds gated mobile** : un canvas avec `filter:blur(30px+)` par frame, ou tout effet coûteux, doit être **désactivé sur mobile + data-saver** (`window.matchMedia("(max-width:760px)")` + `navigator.connection?.saveData`). Le hero reste beau (vidéo/photo + SVG sparkles + grille CSS) sans la boucle gourmande. (Cf. V8 : déjà pause hors-écran/onglet caché via IntersectionObserver.)
6. **Safe-area iOS** : éléments fixés en bas (FAB) en `bottom:calc(Xpx + env(safe-area-inset-bottom))` pour ne pas passer sous la barre d'accueil iPhone.

## 2026-06-23 — 1er run réel du skill `nebula-site` : Miss cakes (#06, pâtisserie en ligne)
Premier client construit **entièrement via le skill** (≠ Djambar qui a servi à le forger). Confirme
que le pipeline tient sur un cas **mono-marque vitrine+catalogue** (≠ hub multi-pages). Leçons :
- **Page unique commandable** = bon défaut pour un commerçant mono-marque sans boutique physique
  (pâtisserie « en ligne ») : hero clair gourmand + barre de confiance + signature/credo + **grille
  de créations commandables** (chaque carte → `wa.me` pré-rempli avec le nom du produit) + galerie
  filtrable + **formulaire commande→WhatsApp** + contact/carte zone. Pas besoin de demander
  l'architecture (brief non ambigu) → tranché par défaut, gain de temps (run-to-completion).
- **Numéro Bénin 8 chiffres → 10 chiffres** : un formulaire qui donne `229XXXXXXXX` (8 chiffres après
  229) est en **ancien format**. Depuis la migration 2024, préfixer `01` → `22901XXXXXXXX`. Le câbler
  ainsi MAIS le marquer **« à confirmer »** partout (site + surtout **affiche imprimée**). Ne jamais
  imprimer un numéro non confirmé sans prévenir.
- **🐛 PE galerie (corrigé à la source, template inclus)** : `.gitem{opacity:0}` n'était **pas gaté
  par `.js`** → sans JS (crawler, no-JS, capture headless) la galerie est **invisible** (vs `.reveal`
  qui est bien `.js .reveal{opacity:0}`). Règle : **tout état caché par défaut doit être gaté `.js`**
  (défaut = visible). Corrigé en `.js .gitem{opacity:0}` dans le site ET le template bundlé.
- **🐛 Reveal horizontal = fuite d'overflow** : `.reveal-right{transform:translateX(46px)}` sur un
  élément **pleine largeur** (ici le panneau credo) pousse son bord droit hors viewport en état
  **pré-révélé** (avant que l'IO pose `.in`) → +26px de débordement mesuré (clippé par
  `html{overflow-x:hidden}` mais réel). Les **transforms comptent dans `scrollWidth`**. Règle :
  réserver `.reveal-right`/translateX positif à des éléments **non pleine largeur** ; pour un bloc
  large, utiliser `.reveal` (translateY) ou `.reveal-scale` (translateY + scale, pas de fuite latérale).
- **Mesure overflow fiable = iframe-diag** : `--window-size` étant ignoré en `--dump-dom`, créer une
  page diag same-origin qui charge `index.html` dans des **iframes de largeurs fixes** (360→1280) et
  lit `scrollWidth` vs `clientWidth` par iframe → mesure exacte par largeur (puis exclure les
  descendants `.marquee` clippés de la liste d'offenders, sinon ils masquent le vrai coupable).
- **Capture headless mi-page = piège reveal** : un screenshot d'une section ancrée mid-page rend
  **blanc** (IO non déclenché → `.reveal` à `opacity:0`). Pour QA visuelle du contenu/layout des
  sections basses, capturer en **`--disable-javascript`** (PE = tout visible) — d'où l'importance que
  TOUT le contenu soit visible sans JS (cf. bug `.gitem`).
- **Placeholders « pro » sans photo** : tuiles galerie = `.gitem .ph` (dégradé de marque + glyphe SVG
  catégorie + libellé), variantes `t-rose/t-cream/t-caramel/t-cocoa` ; marque provisoire = **badge
  généré** (cupcake Pillow) servant logo+favicon+apple-touch+OG. Tout marqué « à remplacer », le
  pipeline `_build_assets.py` reste ré-exécutable dès réception du vrai logo/photos.

## 2026-06-24 — Miss cakes : passe « spectaculaire » (impeccable + animate) après audit honnête
Mongazi a fait auditer le site contre les 2 check-lists (« 10k$ vs 200$ » + « IA vs pro »), exigé du
cru. Verdict honnête donné : **coquille très soignée mais vide de contenu réel** (0 vraie photo = échec
n°1 pour une pâtisserie ; faux avis marqués ; n° non confirmé ; pas d'analytics ; sous-domaine). Puis :
« applique toutes les corrections faisables + rends-la spectaculaire, animations partout, j'envoie le
reste ». Leçons réutilisables :
- **Honnêteté > remplissage d'imagerie** : `brand.md` (impeccable) réclame de l'imagerie réelle (stock
  Unsplash) plutôt que des blocs de couleur. MAIS les **règles d'honnêteté du projet priment** : on ne
  fait PAS passer des photos stock pour les gâteaux de la cliente (mensonge). Résolution : le
  « spectaculaire » vient du **motion + scènes SVG/canvas crédibles (imagerie légitime) + placeholders
  honnêtes magnifiés**, pas de photos empruntées. (brand.md autorise explicitement « credible
  canvas/SVG/WebGL scene » comme imagerie.) → règle skill : imagerie manquante d'un VRAI commerçant =
  scènes générées + placeholders marqués, jamais du stock déguisé en son produit.
- **Contraste CTA = à CALCULER avant de choisir la couleur** : un bouton « rose poudré » (clair) +
  texte blanc échoue l'AA (2.2–3.6). Ni blanc ni chocolat ne passent sur tout un dégradé rose moyen.
  Script luminance → choisir le rose le plus clair qui tient l'AA blanc : **raspberry `#B44E69→#9A3450`
  (white 4.96→7.04)**. Garder le rose poudré clair pour le décor, dédier un token `--cta-*` aux boutons.
- **Coulure de glaçage = séparateur signature pas cher** (POV pâtisserie, anti-template) : un `::after`
  pleine largeur, `background:inherit` + **`mask` en radial-gradient répété** (2 couches tailles/offsets
  différents) → drips irréguliers, scalables, sans SVG path à la main. Lisible seulement quand la
  couleur du bandeau ≠ section dessous (chocolat→clair = top). Animer par `scaleY` (origin top) au reveal.
- **Tracé SVG « qui se dessine » = `pathLength="1"`** : normalise tous les chemins (dasharray:1,
  dashoffset 1→0) quelle que soit la longueur réelle → 1 seule keyframe, stagger via `--i`.
- **PE des animations (récurrent, garde-fou dur)** : tout état caché en attente d'animation
  (`stroke-dashoffset:1` du tracé, `opacity:0` de la flamme, `scaleY(0)` des drips, `.gitem`) DOIT être
  **gaté `.js`** (défaut = visible). Sinon : sans JS / headless / crawler, le contenu (ici le **gâteau**
  du hero) est invisible. Vérifier en capture **`--disable-javascript`** à la largeur où l'élément
  s'affiche (le cake est `display:none` < 880px → tester ≥ 880px).
- **Mesh/sprinkles/effets lourds gated** : mesh blur(48px) = desktop only (`@media max-width:760px →
  display:none`) ; sprinkles JS gated `!isMobile && !reduce` ; **bloc `prefers-reduced-motion` maître**
  qui fige tout (mesh/sprinkles/draw/flicker/drips/ripple). 0 lib CDN (robuste 4G).
- **Stagger sans éditer le HTML** : `:nth-child(n){transition-delay}` sur les cartes plutôt que
  `style="--i"` carte par carte (spécificité du nth-child > classes d1/d2 existantes).
- **Docs impeccable en monorepo** : `context.mjs` cherche `PRODUCT.md` à la racine du repo → pour un
  client d'un monorepo, écrire `PRODUCT.md`+`DESIGN.md` **scopés dans `clients/NN-/`** (pas à la racine
  agence). Cormorant est sur la reflex-reject list MAIS déjà shippé = **identité préservée** (la liste
  ne vaut que pour le greenfield).

## 2026-06-24 — Miss cakes : intégrer les VRAIES images/vidéo client (fonds + hero animé)
La cliente a fourni (via Nano Banana Pro) 1 hero animé + 3 fonds de section. Recette réutilisable :
- **Cinemagraph = poids minuscule** : une vidéo « presque figée » (particules qui dérivent) se
  compresse extrêmement bien. Hero iPhone/IA de 8 Mo → **256 Ko** en H.264 `crf 28`, `scale=1600`,
  `-an`, `+faststart`. Toujours transcoder (même si déjà avc1, le bitrate source est énorme : 10 Mb/s).
  Poster JPEG extrait d'une frame. Vérifier le **codec réellement servi** en prod (download + grep avc1).
- **Hero photo/vidéo clair** : si l'image a une zone claire pour le texte (ici crème à gauche, cake à
  droite), garder le hero CLAIR (voile crème **dense côté texte**, dégradé vers transparent côté sujet)
  → texte sombre AA, pas besoin de basculer en cinématique sombre. `object-position` ~70% pour garder
  le sujet (droite) au recadrage ; voile **uniforme plus dense en mobile** (le sujet passe sous le texte).
- **Fonds de section = 3 patrons réutilisables** : (1) `.editorial .bg` (image floutée + voile
  dégradé, texte blanc) ; (2) `.cta-photo` + `<img class="cta-media">` (voile sombre, attention au
  `.cta>*{z-index:1}` qui attrape l'`<img>` → forcer `.cta-photo .cta-media{z-index:0}`) ; (3)
  `.has-photo` + `.sec-bg` pour une **section claire** (voile crème dégradé, texte sombre, le panneau
  opaque type credo masque la zone chargée de la photo).
- **Contraste sur média = calcul du pire cas** : texte blanc sur une bande sombre = sûr même avec voile
  léger (le sujet est déjà sombre) ; le piège = un fond **festif clair** (bougies/bokeh de `cta.jpg`) →
  baisser `brightness` (~.42) + voile .56→.76 pour que le blanc passe ≥4.5 même sur une flamme.
- **🎥 QA headless d'une page à fonds média = lente** : les `filter:blur()` sur `.bg`/`.sec-bg`/vidéo en
  software-render font **timeout** les captures pleine page hautes (1280×7200). Solutions : capturer
  **plus étroit** (mobile 430px = bien moins de pixels → passe) pour juger la légibilité empilée ; le
  **scroll d'iframe ne « prend » pas** de façon fiable en headless (revient en haut) → ne pas s'y fier.
  Vérifier la **lecture vidéo** par harnais iframe same-origin lisant `video.paused/currentTime/readyState`.

## 2026-06-24 — Miss cakes : une identité de motion DIFFÉRENTE par section (anti-uniformité)
Demande « chaque section = une expérience différente, ultra-fluide ». Recette réutilisable pour donner
à chaque section sa propre entrée sans casser perf/PE/overflow :
- **Système central, variantes par-dessus** : garder UN seul IntersectionObserver qui ajoute `.in` à
  tout `.reveal`. Créer des **variantes** (`.reveal-clip` clip-path, `.reveal-unfold` rotateX,
  `.reveal-from-l/r` slide, `.reveal-stamp` scale, `reveal-place` perspective) + des entrées par
  enfants (`.trust.in .t`, `.creations .creation.in`, form-sec cascade). Le déclencheur reste l'IO →
  PE robuste (contenu visible sans JS, rien gaté invisible).
- **Ambiances scroll-driven = additif pur** : parallax hero, Ken-Burns éditorial, filet d'or, ligne
  des engagements = `@supports (animation-timeline)` / scaleX au `.in`. Jamais gater le contenu dessus.
- **⚠️ Débordement horizontal = LE piège des entrées « slide »** (re-rencontré) : tout `translateX`
  sortant en état pré-révélé déborde la page sur les éléments de bord (galerie scatter `translate(+Xpx)`,
  avis `from-r +54px`, contact `scale(1.25)` qui élargit). Règles : (1) scatter = **translateY + rotation
  + scale<1**, jamais translateX ; (2) slide horizontal = clipper la **section** (`#avis{overflow-x:clip}`,
  pas le `.grid` qui couperait les ombres) ; (3) « tampon » = **scale .9→1** (jamais >1). Toujours
  re-mesurer `scrollWidth` après ; les `.bg`/`.hero-media`/`.sec-bg` listés comme offenders sont des
  **faux positifs** (clippés par `overflow:hidden` du parent → n'augmentent pas `scrollWidth`).
- **Confettis/particules bornés** : injectés en JS à l'entrée (IO once), N réduit sur mobile, conteneur
  `overflow:hidden`, nettoyés après l'anim (`innerHTML=""`), `reduced-motion` = pas d'injection.
- **Étoiles qui se remplissent = PE inversé** : par défaut pleines ; le JS ajoute une classe d'état
  creux (`.stars-anim`) PUIS allume `.lit` en séquence. Sans JS / erreur → restent pleines.
- **QA headless du motion = limité** : iframe `scrollTo` ne « prend » pas (sections mid-page non
  capturables ainsi) ; les anims infinies (marquee/flour) + la **vidéo en lecture** empêchent
  `--screenshot` de « settle » (timeout). Valider par : mesure overflow (iframe-diag multi-largeurs),
  capture `--disable-javascript` pleine page étroite (PE = tout visible) pour le layout, `node --check`,
  et inspection du reduced-motion. Ne pas s'acharner à filmer chaque frame.
- **Nettoyer le code mort à chaque refonte** : après bascule hero SVG→vidéo, retirer
  hero-art/mesh/sprinkles/hero-bg/hero-grid (CSS+JS) — sinon la dette s'accumule. `grep -c` du nom de
  classe dans le HTML = 0 ⇒ mort, supprimable.

<!-- Prochaines entrées : ajouter ici au fil des vitrines suivantes. Toute leçon → ici ; toute évolution DU SKILL → aussi dans .claude/skills/nebula-site/SKILL.md (§ Journal). -->
<!-- Après édition du SKILL.md : re-copier vers _memoire/procedure-vitrine/SKILL.md (mirroir versionné). -->

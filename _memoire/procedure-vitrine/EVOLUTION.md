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

<!-- Prochaines entrées : ajouter ici au fil des vitrines suivantes, avant la création du skill. -->

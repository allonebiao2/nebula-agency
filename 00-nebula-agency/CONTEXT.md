# CONTEXT — Nebula Agency (site de l'agence)

## Identité

- **Nom** : Nebula Agency
- **Type** : Agence web personnelle
- **Cible** : Artisans, créateurs, petites marques cherchant une vitrine soignée.

## Positionnement

Vitrines élégantes, modernes, rapides à livrer.
Esthétique premium accessible, pas de templates génériques.

**Positionnement 2026-07-03 (adopté par Mongazi)** : NEBULA se positionne en **studio de
solutions verticales / éditeur de logiciels métier** (*vertical SaaS*). Au-delà des
vitrines, l'agence propose désormais la **digitalisation sectorielle** : concevoir un
outil digital pensé pour le secteur du client (ex. Digital HSE pour l'industrie,
Vendora pour le commerce). Slogan : « Un outil pensé pour votre secteur, pas un site
générique. » Ce service phare est mis en avant sur le site (bloc `.vsaas` en bas de la
section Services). Voir mémoire `project_positionnement-vertical`.

## Grille tarifaire actuelle (2026-05-30)

| Service | Setup | Récurrent |
|---|---|---|
| Vitrine Digitale + QR Code | **150 000 FCFA** | 15 000 F / 6 mois *(hébergement & sécurité)* |
| Catalogue Digital + QR Code | **50 000 FCFA** | 15 000 F / 6 mois *(hébergement & sécurité)* |
| Création Fiche Google Maps | **20 000 FCFA** | — |
| Création QR Code Google Review | **30 000 FCFA** | — |
| Forfait Avatar IA ESSENTIEL | — | 30 000 F/mois (3 vidéos) |
| Forfait Avatar IA PRO | — | 100 000 F/mois (10 vidéos + scripts + publication + rapport) |

**Délai affiché** : **5 à 7 jours** partout (hero, métriques, why, étapes, CTAs).
Ancien « 48h / 48-72h » remplacé le 2026-05-30.

**Hébergement & sécurité** : **15 000 FCFA tous les 6 mois** (par semestre) pour la
Vitrine et le Catalogue Digital. Frais d'hébergement récurrent, indépendant des
modifications. *(Corrigé le 2026-06-20 : était affiché par erreur « /mois ».)*

## État

- **Version actuelle** : **v9.9** (`nebula_agency_v9.html` = `index.html` en prod ; + vrai logo PNG + écran de chargement cosmique)
- **Statut** : **LIVE** https://www.nebula-agency.online (Cloudflare Pages, projet `nebula-agency`, déployé 2026-07-02)
- **v8 conservé** (`nebula_agency_v8.html`) pour retour arrière.

### Historique des versions

#### v9.9 — 2026-07-03 (vrai logo PNG + écran de chargement cosmique)
- **Logo réel** : le logo NEBULA (`_partage/logo nebula agency.JPG`, galaxie violet/bleu +
  wordmark, sur fond noir) **détouré en PNG transparent** (alpha = luminance via Pillow, garde
  le halo). Enregistré dans `_partage/logo-nebula-transparent.png` (complet) et
  `_partage/logo-nebula-icon.png` (icône seule = tourbillon). Embarqué en **WebP base64**
  optimisé (full 83 Ko, icône 15 Ko) via classes CSS `.nb-logo` (complet) et `.nb-mark` (icône).
- **Nav + footer** : les anciens logos SVG orbitaux (`<svg class="brand-mark">`) remplacés par
  l'**icône PNG** (`.nb-mark`, 66×28), texte « NEBULA AGENCY » conservé à côté.
- **Écran de chargement cosmique** (`#preloader`) à l'entrée : logo complet centré + halo violet
  pulsant + **anneau orbital** (conic-gradient masqué qui tourne) + barre de chargement lumineuse,
  sur fond radial sombre. Se masque à `window.load` (min 1,1 s, filet JS 4 s + fallback CSS 5,5 s),
  `prefers-reduced-motion` respecté. Vérifié visuellement (capture headless) : rendu conforme.
- Process image = Pillow (`logo_assets.py`) : luminance→alpha + trim bbox + WebP q86. ⚠️ un logo
  glow sur fond noir se détoure mieux par **luminance-alpha** que par rembg (garde le halo).
- QC : `node --check` (3 scripts inline OK), déployé + vérifié 200 + capture nav/loader.

#### v9.8 — 2026-07-03 (configurateur « cadrage projet » à fourchette 55k–300k)
- Le configurateur de devis (modale `#devisModal`) est refondu sur le modèle du fichier
  `_partage/nebula-cadrage-projet-devis.html` fourni par Mongazi : **questionnaire en 3 temps
  Entrée → Traitement → Sortie** (+ identité + détails), en **pastilles d'options** (`.dm .opt`,
  cochables), chaque option portant un `data-price`. Habillé dans le thème cosmique du site.
- **Sortie = FOURCHETTE en direct** (`#dm-range`, ex. « 55 000 – 120 000 F »), **bornée par Mongazi :
  min 55 000 F, max 300 000 F** (`DEVIS={base:60000,factMin:.9,factMax:1.25,plancher:55000,plafond:300000,pas:5000}`).
  Base 60 000 + somme des `data-price`, min=clamp(round(total×.9)), max=clamp(round(total×1.25)).
- Envoi = WhatsApp + email auto + lead (`POST /api/site-lead`, `devis_email:true`). L'ancienne logique
  SaaS vertical (chiffre unique + abonnement /6 mois) est **remplacée**.
- **NOVA aligné** (`server.py` `agency_brain()`) : l'estimation en ligne va désormais de **55 000 à
  300 000 F** (fin du « à partir de 200 000 F »). ⚠️ règle : garder NOVA en phase avec le devis du site.
- QC : `node --check` (2 scripts OK), `py_compile` OK, fourchette simulée (vide 55k–75k, gros projet
  plafonné 300k). Déployé + vérifié 200. Backend auto-déployé (commit `8a068bd` RUNNING).

#### v9.7 — 2026-07-03 (NOVA remis sur le site + cerveau mis à jour)
- **Widget NOVA remis** (assistant IA) : bouton flottant « Discuter avec NOVA » + panneau
  de chat cosmique (bas-droite ; le bouton audio décalé à `bottom:86px` pour ne pas se
  chevaucher). Appelle `POST https://nebula-affilies-production.up.railway.app/api/agency-chat`
  (`{messages}` → `{reply}`, rate-limité) — endpoint public déjà existant. Script isolé
  (bloc `<script>` séparé), `node --check` OK. Greeting mentionne les logiciels métier.
- **Cerveau NOVA mis à jour** (`nebula-affilies/server.py` → `agency_brain()`) : NOVA connaît
  désormais l'offre **Digitalisation sectorielle / logiciel métier / SaaS vertical** (à partir
  de 200 000 F + abonnement /6 mois, configurateur de devis en ligne), au lieu de dire « on ne
  fait pas ça ». Avatar IA (retiré du site) enlevé du discours. ⚠️ **garder `agency_brain()` en
  phase avec les offres du site** à chaque évolution. Backend auto-déployé (commit `d590cc6`
  RUNNING), NOVA re-testé : répond correctement sur le SaaS vertical.

#### v9.6 — 2026-07-03 (configurateur de devis SaaS vertical + email auto)
- **Modale de devis** (`#devisModal`) ouverte par le bouton du service phare : le client
  choisit secteur, point de départ, 9 fonctionnalités, ampleur (utilisateurs/sites/
  contenus/délai), coordonnées → **estimation calculée EN DIRECT** (mise en service /
  abonnement / acompte) puis **envoi du devis chiffré sur WhatsApp**.
- **Grille de prix** isolée dans l'objet JS `DEVIS` (éditable par Mongazi). Décisions Mongazi :
  **plancher 300 000 F** (`DEVIS.min`, jamais en dessous) · affichage **« à partir de »** ·
  **abonnement /6 mois** (semestre, comme les vitrines) · le prix sort automatiquement selon
  ce que veut le client (pas de négociation).
- **Email automatique du devis au client** : `nebula-affilies/server.py` → nouvelle fonction
  `send_devis_email()` (Resend) ; `/api/site-lead` envoie l'email si `devis_email:true` + email.
  ✅ **ACTIF EN PROD** : Railway auto-déploie à chaque push (service `nebula-affilies`, projet
  `impartial-achievement`) — commit `6603dde` déployé RUNNING. ⚠️ Railway = **auto-deploy on
  push main** (pas besoin de `railway up`, juste pousser).
- QC : JS vérifié `node --check`, `server.py` `py_compile` OK, déployé + vérifié 200.

#### v9.5 — 2026-07-03 (service phare « Digitalisation sectorielle / SaaS vertical »)
- **Nouveau bloc `.vsaas`** ajouté en bas de la section Services (sous les 3 cartes) :
  offre phare **« Digitalisation sectorielle : votre logiciel métier »** (badge « Nouveau ·
  SaaS vertical », 3 atouts = Pensé pour votre secteur / Automatise votre métier / Évolue
  avec vous, chips secteurs HSE·Commerce·Immobilier·Santé·« Votre secteur ? », CTA « Parlons
  de votre secteur » → #order avec `setTier('Plusieurs services / besoin de conseils')`,
  mention « Sur devis »). Panneau cosmique (dégradé + bordure gradient masquée), responsive.
- **Chapeau Services** reformulé : « Du **site vitrine** au **logiciel métier** conçu pour
  votre secteur… » (introduit l'offre + retire un em-dash).
- **Vision/directive mises à jour** : `CLAUDE.md` (Mission + Positionnement) et ce CONTEXT
  (section Positionnement) → NEBULA = studio de solutions verticales / vertical SaaS.
- Déployé + vérifié 200 sur www.nebula-agency.online. Source + copie `_dist`.

#### v9.4 — 2026-07-03 (formulaire enrichi + email obligatoire)
Formulaire de commande étoffé pour capter un brief plus précis :
- **Email ajouté** (`f_email`, type email) : **obligatoire + validé** (regex), transmis
  dans le message WhatsApp ET dans le lead back-office (`email:email` dans le POST `/api/site-lead`).
- **8 nouvelles questions** dont **6 menus déroulants** (10 `<select>` au total, contre 4) :
  `f_objectif` (objectif principal du site, **obligatoire**), `f_pages` (ampleur),
  `f_style` (style visuel), `f_langue`, `f_existant` (présence en ligne actuelle),
  `f_contenu` (contenus prêts ?), + 2 champs texte `f_inspiration` (sites aimés) et
  `f_reseaux` (réseaux sociaux à afficher). Nouvelle section « Style & contenu ».
- `soumettreCommande()` : lit tous les champs, valide (nom/tel/email/marque/secteur/
  ville/service/objectif/desc requis + format email), message WhatsApp restructuré
  (blocs Contact / Projet / Style & contenu / Options / Description) avec `na()` =
  « Non précisé » pour les optionnels vides.
- ⚠️ n° WhatsApp **22996740732 inchangé** · options de service (setTier) **inchangées**.
- Déployé + vérifié 200 sur www.nebula-agency.online. Source + copie `_dist`.

#### v9.3 — 2026-07-03 (une animation signature DIFFÉRENTE par section)
Chaque section (hors héros, qui garde son shader WebGL) reçoit **sa propre animation, toutes distinctes**, calées sur l'univers cosmique (bleu/violet/cyan) et GPU-friendly (transform/opacity), **coupées sous `prefers-reduced-motion`** :
- **Trust** « Ils nous font confiance » → **comète filante** qui traverse le bandeau (`.sig-trust .comet`).
- **Services** → **anneau cosmique** (conic-gradient masqué) qui tourne autour de chaque icône + **soulignement aurora** qui se trace sous le titre (`.sig-services`).
- **Portfolio** → **éclat hypervitesse** (repeating-conic streaks) au 1er passage au scroll (`.sig-portfolio.go .warp`, one-shot via IntersectionObserver).
- **Tarifs** → **compteurs de prix qui montent** de 0 (JS `whenIn` + easing cubic) + **satellite doré en orbite** de l'offre recommandée (`.pcard-feat .psat`).
- **Pourquoi NEBULA** → **ligne d'énergie verticale** qui se trace + **point lumineux voyageur** le long des why-items (`.sig-why.go .why-line`).
- **Commander** → **impulsion séquentielle** qui parcourt les 3 étapes 1→2→3 en boucle (`.sig-steps .step-n`).
- **Contact** → **balayage radar** (conic sweep masqué en anneau) derrière les cartes (`.sig-contact .radar`).
- **Footer** → **nébuleuse violette à la dérive** (radial-gradient flou animé, `.sig-footer::before`).
Impl : bloc CSS `/* animations signatures par section */` + JS `whenIn()` (compteurs prix + `.go` one-shot portfolio/why). Aucune image, aucune dépendance. Déployé + vérifié 200 sur www.nebula-agency.online. Source `nebula_agency_v9.html` + copie `_dist`.

#### v9.2 — 2026-07-02 soir (nettoyage portfolio + section Tarifs)
- **Portfolio & bandeau « Ils nous font confiance »** : retrait des **3 sites non terminés**
  (Speed × Weinkeller, Miss Cakes, HH Design). Restent visibles = Djambar Team,
  Grain d'Esthétique, INA Luxury. Fichiers clients intacts (juste dé-mis-en-avant).
- **Nouvelle section `#pricing` « Tarifs »** insérée entre *Pourquoi NEBULA* et le
  formulaire *Commander* (position de conversion). Réutilise 100% de l'ADN v9
  (classes `.card/.pcard/.feats/.host-note/.pill-pop/.price`, reveals `.rv-scale`,
  spotlight). 3 offres = **Catalogue 50 000 F · Vitrine 150 000 F (plan Recommandé,
  anneau dégradé + halo doré) · QR Google Review 30 000 F**. Chaque carte : prix
  paiement unique, liste d'inclusions, encadré hébergement *15 000 F / 6 mois*
  (sauf QR = sans abo). Bandeau réassurance + appel au devis. Boutons `setTier`
  pré-remplissent le formulaire (chaînes = options exactes, vérifié). Lien **Tarifs**
  ajouté nav desktop + menu mobile. Prix **fidèles à la grille** (rien de réintroduit :
  ni Avatar IA, ni Google Maps). QC : balises équilibrées, 3 cartes/18 items,
  em-dash prose = 0, déployé + vérifié 200 sur www.nebula-agency.online.

#### v9 — 2026-07-02 (REFONTE cosmique haut de gamme + shader hero)
Refonte quasi totale, validée par Mongazi (direction « refonte cosmique haut de gamme »). Contenu réel préservé
(prix, forfaits, `soumettreCommande` → WhatsApp + lead back-office affiliés, `setTier`, liens partenaires).
- **Typo display Syne** (au lieu de Space Grotesk, jugé trop générique) ; Inter en corps ; JetBrains Mono en labels.
- **Fond nébuleuse animé WebGL** dans le hero (shader @atzedent porté en vanilla JS, **recoloré NEBULA** bleu/violet/cyan) :
  repli auto (dégradé + starfield) si pas de WebGL2, **pause hors-vue**, `prefers-reduced-motion`, demi-résolution mobile.
- **Portfolio RÉEL** (remplace les 3 vieux liens) : **6 vrais sites livrés** en cadres navigateur + captures webp base64 —
  Djambar Team (djambarteam.com), Speed×Weinkeller, Miss Cakes, HH Design, Grain d'Esthétique, INA Luxury.
- **Icônes SVG** partout (fini les emojis), nav en verre flottant, logo orbital SVG, image OG `assets/og-nebula.jpg` (1200×630).
- **Retraits demandés 2026-07-02** : forfait **Fiche Google Maps**, forfaits **Avatar IA Essentiel & Pro** (section entière),
  onglet nav **Tarifs**, **aperçus flottants** du hero. Services restants : Vitrine (150k) · Catalogue (50k) · QR Review (30k).
  (Case « Google Maps intégré » gardée = option d'intégration carte, ≠ forfait fiche.)
- **Bouton nav « WhatsApp » → « Commander »** (redirige vers le formulaire #order). WhatsApp reste en Contact/pied/formulaire.
- Scripts reproductibles : `_inject_v9.py`, `_add_shader.py`, `_trim_v9.py`, `_build_og.py`. Déploiement = `wrangler pages deploy _dist`.
- QC Playwright : 0 erreur, 0 404, formulaire OK (`setTier`), 6 sites portfolio, responsive. ⚠️ le shader ne se capture pas en
  WebGL logiciel (headless) mais valide/tourne sur GPU réel.

#### v8 — 2026-05-30 (grille tarifaire + délai + portfolio INA)
- **Vitrine Digitale** : 70 000 → **150 000 FCFA** setup
- **Mensuel** : 10 000 → **15 000 FCFA/mois** *(modèle initial v8)*.
  **Corrigé le 2026-06-20** → hébergement & sécurité = **15 000 F / 6 mois**
  (par semestre, voir la grille en tête).
- **Fiche Google Maps** : 15 550 → **20 000 FCFA**
- **QR Code Review** renommé **QR Code Google Review**, 20 550 → **30 000 FCFA**
- **Délai** : « 48h / 48 à 72h » → **« 5 à 7 jours »** partout
  (hero h1, métriques, stat-box, why-item, étape 3, CTAs, meta tags)
- **Stat « Vitrines déployées »** : 2 → **3**
- **Portfolio** : ajout d'une 3e carte **INA Luxury** pointant vers
  `https://luxuryskinclinic.netlify.app/ina-luxury.html` avec mock
  visuel dédié `.mock-ina` (palette or/noir, dégradé gold)

#### v7.2 — 2026-05-12 (polish pro + audio + mobile)
- **Audio jazz d'ambiance** : bouton flottant bas-droit, démarre au premier clic/scroll/touch, fade in/out, persistance localStorage. Fichier attendu : `audio/jazz-loop.mp3` (royalty-free, à déposer)
- **Film grain overlay** : texture SVG turbulence fixed, mix-blend-mode overlay, opacity .05 (.04 sur mobile)
- **Liquid glass inner borders** : `inset 0 1px 0 rgba(255,255,255,0.04)` sur nav/cards/btns pour effet de réfraction
- **Phone mockup décoratif** : 3 SVG mockups inline dans la section Avatar IA (animation hue-rotate)
- **Mobile pro polish** :
  - `font-size:16px` sur les inputs (élimine le zoom iOS)
  - Tap targets nav-links et CTA passés à 36-44px min
  - Padding ajusté < 420px
- **Audio README** dans `00-nebula-agency/audio/` avec sources royalty-free recommandées

#### v7.1 — 2026-05-12 (boost animations + déplacement)
- Reading progress bar (top, dégradé bleu/violet/cyan)
- Tilt 3D au hover sur cards (svc, port-card, why-item, ct) — desktop only
- Gradient border conique animé au hover des services
- Magnetic CTA sur btn-primary, btn-submit, nav-cta — desktop only
- Stagger reveal étendu (rv-d5 à rv-d8)
- Icônes bouncy avec spring easing `cubic-bezier(0.34,1.56,0.64,1)`
- Fichier déplacé de la racine vers `00-nebula-agency/`

#### v7 — 2026-05-12
- **Prix Service 01** : 35 550 → 50 550 FCFA (card + onclick + option du select)
- **Nouvelle section Forfaits Avatar IA** entre Services et Pourquoi NEBULA
  - Forfait ESSENTIEL : 30 000 FCFA/mois — 3 vidéos
  - Forfait PRO : 100 000 FCFA/mois — 10 vidéos + scripts + publication + rapport
  - 2 nouvelles options correspondantes ajoutées au formulaire
- **Performance / GPU** :
  - `will-change:transform` + `backface-visibility:hidden` sur les éléments animés
  - `translate3d` à la place de `translateY` sur tous les hovers de cards et boutons
  - Variable CSS unifiée `--ease-out-expo: cubic-bezier(0.16,1,0.3,1)` (remplace 9 cubic-bezier génériques)
  - `animation-fill-mode:both` sur les keyframes
  - `text-rendering:optimizeLegibility` + `-moz-osx-font-smoothing:grayscale` sur body
  - Canvas étoiles refactoré en delta-time pour 60fps stable
- **Bonus** :
  - Meta og: / twitter: ajoutées pour partage social
  - Preload de la feuille Google Fonts
  - `loading="lazy"` sur l'image du footer
  - Scrollbar enrichie (8px, dégradé 3 couleurs blue→violet→cyan, hover)
  - Box-shadow progressif sur hover des boutons primary/ghost/submit
  - Focus states accessibles (`outline:2px solid var(--blue2)`) sur CTAs et nav

### Contraintes respectées
- WhatsApp `+229 96 74 07 32` : intact
- Couleurs et variables CSS : intactes
- Fonts (Inter, Space Grotesk, JetBrains Mono) : intactes
- Structure des sections existantes : intacte (Avatar IA est une nouvelle section, pas une restructuration)

## Identité visuelle

- Style : moderne, sombre, accents lumineux (à confirmer dans `_memoire/decisions.md`)
- Ton : direct, premium, sans jargon

## Notes

- Le site sert aussi de démonstration des capacités de l'agence.
- Toute évolution doit refléter la qualité attendue côté clients.

## À faire

- [ ] Confirmer les couleurs/typographies de la charte
- [ ] Ajouter une section études de cas une fois 2-3 clients livrés
- [ ] Mettre en ligne (hébergement à choisir)

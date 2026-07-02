# CONTEXT — Nebula Agency (site de l'agence)

## Identité

- **Nom** : Nebula Agency
- **Type** : Agence web personnelle
- **Cible** : Artisans, créateurs, petites marques cherchant une vitrine soignée.

## Positionnement

Vitrines élégantes, modernes, rapides à livrer.
Esthétique premium accessible — pas de templates génériques.

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

- **Version actuelle** : **v9** (`nebula_agency_v9.html` = `index.html` en prod)
- **Statut** : **LIVE** https://www.nebula-agency.online (Cloudflare Pages, projet `nebula-agency`, déployé 2026-07-02)
- **v8 conservé** (`nebula_agency_v8.html`) pour retour arrière.

### Historique des versions

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

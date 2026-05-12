# CONTEXT — Nebula Agency (site de l'agence)

## Identité

- **Nom** : Nebula Agency
- **Type** : Agence web personnelle
- **Cible** : Artisans, créateurs, petites marques cherchant une vitrine soignée.

## Positionnement

Vitrines élégantes, modernes, rapides à livrer.
Esthétique premium accessible — pas de templates génériques.

## État

- **Version actuelle** : v7
- **Fichier** : `nebula_agency_v7.html`
- **Statut** : Livrée
- **Source** : copiée depuis `nebula_agency_v5_FINAL (1).html`

### Historique des versions

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

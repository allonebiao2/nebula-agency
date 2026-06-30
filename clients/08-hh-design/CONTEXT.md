# HH Design — CONTEXT

## Identité
- **Marque** : HH DESIGN
- **Secteur** : Immobilier (agence / biens d'exception, sensibilité design)
- **Ville** : Cotonou, Bénin
- **WhatsApp** : 0167975626 → `wa.me/2290167975626` ⚠️ **à confirmer** (même n° que client 04 Gloria)
- **Couleurs imposées** : Blanc · Doré · Noir
- **Logo** : fourni par le client sur WhatsApp → **placeholder wordmark Marcellus en attendant**

## Commande
- Vitrine Digitale + QR Code (150 000 F setup + 15 000 F / 6 mois hébergement)
- Options : **Galerie photos** + **Google Maps**
- Délai : le plus vite possible

## Parti-pris (TOTALEMENT distinct des vitrines précédentes)
- **Direction** : éditorial architectural luxe — blanc cassé + noir d'encre + or champagne, vide
  généreux, hairlines dorées, « exaggerated minimalism » (typo surdimensionnée).
- **Typo** : Marcellus (display, roman architectural) + Manrope (corps). Jamais Anton/Cinzel/
  Bricolage/Spectral (déjà utilisés ailleurs).
- **Galerie** : lignes éditoriales alternées (image pleine largeur ↔ texte, alternées) + filtres +
  lightbox. ≠ bento Djambar, ≠ coverflow Speed/Weinkeller, ≠ scatter Miss Cakes.
- **Motion** : tracés de lignes dorées (pathLength), révélations en rideau (clip-path), parallaxe
  lent. Calme/architectural, pas kinétique. reduced-motion complet.
- **Structure** : hero asymétrique → bandeau manifeste NOIR → expertise → biens (galerie) →
  approche → avis → localisation → CTA → footer.

## À REMPLACER (côté client)
- [ ] **Logo** réel (reçu sur WhatsApp) → remplacer le wordmark placeholder
- [ ] **Vraies photos de biens** (résidentiel/commercial/terrain) — actuellement scènes SVG
      architecturales « à valider »
- [ ] **Adresse exacte** + point Google Maps (actuellement « Cotonou » + recherche Maps)
- [ ] **Vrais avis clients** (actuellement exemples marqués « à valider »)
- [ ] **Confirmer le n° WhatsApp** 0167975626
- [ ] Réseaux sociaux (liens réels)
- [ ] Textes services/biens validés par le client

## Déploiement
- ✅ **LIVE : https://hh-design.pages.dev** (Cloudflare Pages, projet `hh-design`, branche main)
- Page unique (index.html, CSS/JS inline), galerie = scènes SVG inline, OG/favicon générés
- Affiche A4 + 2 QR (WhatsApp + Maps) : `assets/docs/Affiche_HH_Design_A4.pdf`
- Domaine custom : étape séparée (à voir avec Mongazi)

## Livré le 2026-06-30
Vitrine éditoriale architecturale luxe (blanc/or/noir, Marcellus+Manrope) : hero asymétrique,
manifeste noir, expertise (losanges or), galerie de biens en lignes alternées + filtres + lightbox,
approche 3 étapes, avis (exemples), localisation Maps, CTA, footer, FAB WhatsApp. QA : 0 débordement
(mobile inclus), 0 erreur, assets 200, reduced-motion complet. Affiche PDF A4 + QR.

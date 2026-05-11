# Checklist de livraison — Vitrine NEBULA

> À dérouler avant chaque mise en ligne client. Ne jamais sauter d'étape.

---

## Contenu

- [ ] Tous les textes relus (zéro faute)
- [ ] Toutes les images en base64 (aucune URL externe)
- [ ] Toutes les images ont un `alt` pertinent
- [ ] Aucune image manquante / cassée
- [ ] Liens WhatsApp testés (clic → ouverture conversation correcte, numéro bon, message pré-rempli OK)
- [ ] Liens externes (réseaux, formulaires, etc.) tous valides
- [ ] Téléphone, email, adresse à jour
- [ ] Horaires d'ouverture à jour si applicable

## Technique

- [ ] HTML validé (pas de balise ouverte, structure sémantique)
- [ ] CSS inline propre (pas de styles morts)
- [ ] Aucun lien Google Drive / Dropbox / CDN externe
- [ ] Aucun `console.log` ou code de debug
- [ ] Favicon présent
- [ ] `<title>` et `<meta name="description">` renseignés (SEO local)
- [ ] Open Graph (titre, image, description) renseigné si partage WhatsApp prévu

## Responsive

- [ ] Test mobile (Android entrée/milieu de gamme, écran 360px)
- [ ] Test tablette
- [ ] Test desktop
- [ ] Texte lisible sans zoom sur mobile
- [ ] Boutons tap-friendly (≥ 44px)
- [ ] Pas de débordement horizontal

## Performance

- [ ] Poids total de la page raisonnable (< 2 Mo idéal en base64)
- [ ] Images compressées avant base64 (WebP / JPEG optimisé)
- [ ] Lighthouse mobile > 85 visé
- [ ] Chargement testé sur 4G ralentie (DevTools throttling)

## Validation Mongazi (règles absolues)

- [ ] Diff complet montré avant commit
- [ ] Liens WhatsApp non modifiés sans confirmation
- [ ] Validation explicite reçue avant `git push`

## Validation client

- [ ] Capture d'écran (ou URL preview Netlify) envoyée au client
- [ ] OK écrit du client reçu et archivé

## Mise en ligne

- [ ] Déployé (Netlify / Hostinger)
- [ ] URL prod testée depuis un autre appareil
- [ ] URL prod testée depuis un réseau mobile réel
- [ ] Tableau clients mis à jour dans `CLAUDE.md`
- [ ] Statut mis à jour dans `_memoire/clients-historique.md`
- [ ] Décision/leçon notable consignée dans `_memoire/` si applicable

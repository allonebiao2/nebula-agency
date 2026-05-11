# Design system — NEBULA Agency

> Charte et conventions visuelles à respecter sur les vitrines NEBULA.

---

## Identité agence NEBULA

> À documenter officiellement (voir `_memoire/decisions.md` quand la charte sera figée).

- **Couleurs officielles** : à valider
- **Typographies** : à valider
- **Logo** : version officielle à archiver dans `00-nebula-agency/assets/` (à créer)
- **Ton de marque** : moderne, premium, accessible, direct

## Principes de conception vitrines clients

- **Premium accessible** : élégant sans surcharge
- **Mobile-first africain** : lisible sur 360px, charge sous 4G instable
- **Sobriété d'éléments** : 1 message clair par section
- **WhatsApp toujours accessible** (sticky CTA pertinent dans la majorité des cas)
- **Hiérarchie visuelle évidente** : on doit comprendre l'offre en 5 secondes

## Composants récurrents

| Section | Rôle | Notes |
|---|---|---|
| Hero | Accroche + CTA principal (souvent WhatsApp) | Image / vidéo de fond légère |
| Services / Produits | Présenter l'offre | 3 à 6 items, pas plus |
| Galerie | Réassurance visuelle | Carousel ou grid base64 |
| À propos | Humaniser | Photo + 3-5 lignes max |
| Témoignages | Preuve sociale | Si dispos vérifiables |
| FAQ | Lever les objections | 4 à 6 questions courtes |
| Contact / Footer | Coordonnées + réseaux | WhatsApp + Instagram souvent |

## Conventions code

- **CSS inline** dans le `<head>` (pas de feuille externe)
- **Variables CSS** pour la palette :
  ```css
  :root {
    --color-primary: #...;
    --color-accent:  #...;
    --color-bg:      #...;
    --color-text:    #...;
  }
  ```
- **Pas de framework CSS** (ni Bootstrap, ni Tailwind via CDN)
- **JS vanilla** minimal — uniquement si nécessaire
- **Images en base64**, jamais en lien externe

## Accessibilité minimale (non négociable)

- Contrastes WCAG AA respectés
- `alt` sur **toutes** les images
- Tap targets ≥ 44px
- Navigation clavier fonctionnelle
- `lang="fr"` sur le `<html>`
- Pas de texte uniquement dans une image

## Anti-patterns à éviter

- Carousels auto-play trop rapides
- Pop-ups intrusifs au chargement
- Texte clair sur fond clair (problème fréquent)
- Police trop fine sous 16px en corps de texte
- Animations gourmandes en CPU mobile

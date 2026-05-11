# Stack — Nebula Agency

> Outils, technologies et techniques utilisés sur les projets.

---

## Front-end

- **HTML5** — un fichier autonome par vitrine quand c'est possible.
- **CSS** — vanilla, parfois custom properties pour la palette.
- **JavaScript** — vanilla, sans framework par défaut.

## Design

- **Maquettes** : à définir (Figma ? direct HTML ?)
- **Typographies** : Google Fonts ou self-hosted selon performance.
- **Icônes** : à standardiser (Lucide ? Heroicons ? SVG inline ?)

## Performance

- Images optimisées avant intégration (WebP quand possible).
- Pas de dépendances JS lourdes sans raison.
- Score Lighthouse visé : > 90 mobile.

## Hébergement / déploiement

- À définir client par client (Netlify, Vercel, OVH, etc.)
- Nom de domaine : géré par le client la plupart du temps.

## Outils de travail

- **Éditeur** : VS Code
- **IA** : Claude Code (avec ce repo comme contexte)
- **Versionning** : Git (un commit lisible par étape significative)

---

## À évaluer

- [ ] Système de build minimal (concat CSS/JS) si projets plus gros
- [ ] Bibliothèque d'animations légère (GSAP ? Motion One ?)
- [ ] Solution CMS pour clients voulant éditer eux-mêmes

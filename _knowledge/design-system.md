# Design system — NEBULA Agency

> Charte et conventions visuelles à respecter sur les vitrines NEBULA.

---

## ⚠️ Le manuel fait foi

**Le document de référence est `_memoire/procedure-vitrine/DIRECTION-ARTISTIQUE.md`** —
le standard « 100 000 € », applicable à toute vitrine depuis le 2026-08-01.
Cette page en donne le résumé ; en cas de différence, le manuel a raison.

## Identité agence NEBULA

> À documenter officiellement (voir `_memoire/decisions.md` quand la charte sera figée).

- **Couleurs officielles** : à valider
- **Typographies** : à valider
- **Logo** : version officielle à archiver dans `00-nebula-agency/assets/` (à créer)
- **Ton de marque** : moderne, premium, accessible, direct

## Principes de conception vitrines clients

- **L'idée avant le style.** Écrire en une ligne ce qu'est le métier vu de l'intérieur, avec
  un **objet concret** dedans (le fil, la braise, la descente). Toutes les animations
  sortent de cet objet. Sans cette phrase, on décore — et ça se voit.
- **Fini ≠ ça marche.** Une vitrine est finie quand elle **impressionne**. Le QC vert et la
  beauté sont deux critères de sortie, pas un.
- **Premium accessible** : élégant sans surcharge
- **Mobile-first africain** : lisible sur 360px, charge sous 4G instable
- **Sobriété d'éléments** : 1 message clair par section
- **WhatsApp toujours accessible** (sticky CTA pertinent dans la majorité des cas)
- **Hiérarchie visuelle évidente** : on doit comprendre l'offre en 5 secondes

## Les trois choses qui font 80 % de l'écart — et aucune n'est une animation

### 1. La typographie — choisie PAR REGISTRE DE MÉTIER
Il n'y a pas de police NEBULA unique : la display se choisit selon ce que vend le client.

| Registre | Display | Exemple |
|---|---|---|
| Mode, couture, beauté, joaillerie | **Didone** (Bodoni Moda, Playfair) | Hillary M. Styl |
| Artisanat, bois, matière, restaurant | **Garamond / humaniste** (Cormorant) | HH Design |
| Commerce, tech, énergie | **Grotesque à caractère** (Bricolage, Anton) | Miss cakes, Speed |

- `clamp()` jusqu'à **6 rem** en héros ; jamais sous 40 px sur mobile
- **Jamais deux polices du même genre** : serif + sans, ou une famille en plusieurs graisses
- Un **italique de la display** en accent coloré vaut dix effets, et il est gratuit
- Interdits durables en display : Montserrat, Inter, Roboto, Poppins

### 2. Le rythme des fonds
Alterner sombre et clair, section par section. Sans alternance, tout se vaut et rien ne
ressort. **Jamais `#000` ni `#fff` en fond** : une encre (`#0B0A0C`), un papier (`#F4F1EC`).

### 3. Le vide
Un héros qui remplit l'écran fait pauvre ; un héros qui respire fait cher. Si la moitié
droite est vide en grand écran, ce n'est pas un défaut — c'est une place. Sans photo :
un **dessin au trait animé** de l'objet du métier, en SVG qui se trace (2 Ko).

## Images — la règle qui ne souffre aucune exception

⛔ **Une photo produit générée par IA ne doit JAMAIS être présentée comme le catalogue du
client.** Une cliente qui commande sur la photo d'une pièce que l'atelier ne fabrique pas,
c'est la maison qui paie à la livraison. Ambiance, matière, texture, arrière-plan :
autorisées. Un article vendable : jamais.

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

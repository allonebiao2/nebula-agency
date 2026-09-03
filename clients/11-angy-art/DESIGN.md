# Direction artistique — Angy Art

**Référence imposée par Mongazi le 2026-08-05 : l'esthétique « Selva Toscana ».**
Éditorial noir / crème, serif didone en très gros corps, italiques dorés, animations
fluides, curseur suiveur, carrousel en coverflow, défilement lourd.

## La phrase

> **Une œuvre d'Angy, c'est une entaille dans la matière : on marque la surface, et la
> mémoire y tient.**

Elle survit à la refonte : c'est elle qui remplit la maquette Selva quand les vraies
photos manquent. Là où le modèle met une photo d'œuvre, on met **la matière** (toile
tendue, pigment, relief, textile, lumière) et **les entailles qui se tracent**.

## Palette

Celle du brief, avec **une correction non négociable** :

| Jeton | Valeur | Rôle | Contraste mesuré |
|---|---|---|---|
| `--noir` | `#0a0a0a` | le fond de presque tout | — |
| `--noir-2` | `#141414` | la modale | — |
| `--creme` | `#f3efe6` | les sections claires, les boutons pleins | — |
| `--encre` | `#1a1a1a` | le texte sur crème | 15,2:1 |
| `--or` | `#c9b99a` | les italiques **sur noir** | 10,3:1 |
| **`--or-f`** | **`#7e6d3a`** | les italiques **sur crème** | **4,4:1** |
| `--tx-n` | `rgba(255,255,255,.72)` | le texte courant sur noir | 10,2:1 |
| `--tx-c` | `#54504a` | le texte courant sur crème | 7,0:1 |

⚠️ **L'or du brief (`#c9b99a`) sur le crème donne 1,68:1.** C'est illisible, pas
« élégant ». D'où `--or-f` pour toutes les italiques et tous les liens posés sur clair.
Les micro-libellés blancs, prévus à 70 % d'opacité, sont à **62 %** minimum (7,8:1) :
en dessous, à 10 px, ils disparaissent sur un vidéoprojecteur ou un écran de téléphone
en plein soleil, ce qui est la condition normale à Cotonou.

## Typographie

- **Playfair Display** (display), 400/500 + italique. Le didone demandé.
- **Public Sans** 300/400/500 (texte, libellés). Grotesque neutre, excellente en petit
  corps, remplace Inter (interdit maison) sans changer le registre.
- Titres jusqu'à `clamp(2.1rem, 5.9vw, 5rem)`, héros jusqu'à `clamp(3.1rem, 12.6vw, 9.4rem)`.
- Libellés : 10 à 10,5 px, `letter-spacing: .15em`, majuscules.

## Les sections, dans l'ordre

1. **Héros** — nom en très gros, sous-titre italique or, arche flottante à droite
   (l'emplacement de la vraie photo), métriques en bas, pilule centrée.
2. **La démarche** (crème) — grand titre révélé mot à mot, image en parallaxe à gauche,
   texte + lien souligné à droite.
3. **Le portfolio** (noir) — le carrousel coverflow.
4. **L'atelier** (plein écran) — le mur de la galerie, étiquettes, CTA.
5. **La citation** (split) — le lin de très près à gauche, la phrase d'Angélique à droite.
6. **La visite** (plein écran) — la salle le soir, CTA vers la modale.
7. **Pied** — coordonnées, réseaux, mentions.

## Le mouvement, sans une seule bibliothèque

| Ce que demandait le brief | Ce qui est livré | Poids |
|---|---|---|
| Lenis (smooth scroll) | interpolation de `scrollTop` en `rAF`, lerp 0,095 | 0 Ko |
| GSAP + ScrollTrigger | balayage au défilement + classes CSS | 0 Ko |
| SplitText | découpage en mots en DOM, `--d` par mot | 0 Ko |
| Swiper coverflow | positions calculées (`--tx --sc --op --bl --gs`) | 0 Ko |
| Curseur React + lerp | `pointermove` + `rAF` qui **s'arrête tout seul** | 0 Ko |

Motif : règle NEBULA (aucune bibliothèque) + 4G et Android d'entrée de gamme à Cotonou.
Un site d'artiste qui met six secondes à charger ne se visite pas.

**Les révélations passent par un balayage, pas par un `IntersectionObserver`.** Avec un
observateur seul, un visiteur qui clique « L'ATELIER » saute par-dessus « La démarche »,
l'observateur ne se déclenche jamais pour elle, et **ses textes restent invisibles pour
toujours**. Défaut réel, trouvé par le contrôle automatique, corrigé.

## Garde-fous

- `prefers-reduced-motion` : plus de curseur, plus de flottement, plus de balayage de
  lumière ; tout est posé et visible.
- **Aucun `backdrop-filter`** sur un élément de la page (vérifié à chaque contrôle).
  Seul le fond de la modale en porte un, et rien n'est animé dessous.
- Sans JavaScript : la page reste entièrement lisible et **tous les liens WhatsApp
  fonctionnent** (les `href` sont écrits en dur dans le HTML, le JS n'ajoute que le
  message pré-rempli).
- Cibles ≥ 44 px, `font-size: 16px` sur les listes déroulantes (anti-zoom iOS).
- `?v=` à bumper sur `app.css` et `app.js` à **chaque** modification.

## Ce qui a été écarté du brief, et pourquoi

| Demandé | Livré | Motif |
|---|---|---|
| Next.js / React / Tailwind | HTML, CSS, JS natifs | règle NEBULA, 4G Cotonou |
| « WORKS · 47 / YEARS · 12 » | technique, pièces uniques, atelier | on ne connaît ni le nombre d'œuvres ni l'ancienneté |
| Citation signée « ARTS MAGAZINE » | phrase d'Angélique, signée d'elle | inventer un critique est un faux |
| « au bord du Marais » | Cotonou | c'est là qu'est l'atelier |
| Datepicker + créneaux + « on garde 10 minutes » | 3 listes déroulantes → WhatsApp rédigé | il n'y a pas d'agenda derrière ; promettre un créneau qu'on ne tient pas coûte un client |
| « Book a visit », « Our story » | français | la cliente a demandé le français |

## Ce qui manque encore, et qui n'est pas à nous

Les **vraies photos d'œuvres**. Le carrousel est construit pour elles : une ligne dans
`OEUVRES` (en haut de `app.js`) et une photo remplace une matière, avec son cartel, son
compteur et sa vue en grand. **Aucune image d'œuvre générée par IA, aucun titre inventé** :
un collectionneur qui écrit pour une pièce qui n'existe pas, c'est l'artiste qui paie.

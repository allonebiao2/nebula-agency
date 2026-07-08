# Technique — Dashboard multi-granularité à partir d'un store « mensuel »

**Contexte** : Boussole avait un store 100 % orienté « mois » (`bilanMois`, `serieMensuelle`). Pour offrir Jour/Semaine/Mois/Année + comparaison sans tout réécrire.

## Recette (réutilisable pour tout tableau de bord NEBULA)
1. **`periodInfo(gran, offset)`** : une seule fonction décrit N'IMPORTE quelle période → `{ start, end, label, unit, buckets:[{start,end,label}], prev:{start,end,label} }`.
   - jour = 24 buckets horaires · semaine = 7 jours (lundi→dimanche) · mois = jours du mois · année = 12 mois.
   - `offset` (négatif) = naviguer dans le passé ; bloquer le futur (`offset >= 0` désactive la flèche suivante).
   - Labels **espacés** dès la source (`label:''` pour les buckets masqués) → les graphes n'ont pas à gérer l'anti-chevauchement.
2. **Agrégation générique** : `ventesEntre(start,end)` filtre par timestamp ; `serieDashboard()` mappe chaque bucket + calcule totaux, `prev` (période précédente = comparaison), et `deltas` (diff/pct/sens).
3. **Charges mensuelles → prorata** : `chargesProrataEntre(start,end)` répartit la charge mensuelle **au prorata des jours** (et jamais sur le futur : `min(end, now)`), en itérant mois par mois. Donne un « bénéfice net » **cohérent à toutes les échelles** (heure comme année), là où sinon les charges mensuelles casseraient les vues courtes.
4. **Comparaison** : delta = `{ diff, pct, sens }` ; badge coloré (vert hausse / rouge baisse), option `pts` pour les taux (ex. marge en points), option `invert` quand « baisser » est bon.

## Pièges rencontrés
- **Harnais de test** : cache-buster `?x=Date.now()` sur des `import()` dynamiques crée **deux instances** du module (state séparé) → le seed n'était pas vu par `ui.js`. En ESM, importer SANS query pour partager l'instance ; chaque run Chrome headless part de toute façon d'un cache vide.
- **SVG + variables CSS** : passer la couleur via `style="stroke:var(--x)"`, **jamais** en attribut `stroke=` (non résolu). Rappel déjà noté.
- **Anneau `progressRing`** : la classe `.ring` force `width:78px` → pour un grand anneau (objectif 140 px) surcharger via `.objx__ring .ring { width:140px }` (specificité).
- **Grille bento** : réutiliser `.panel` comme carte + classes de span `.c4/.c6/.c8/.c12` ; `grid-auto-flow: row dense` ; mobile 1 col, tablette 2, PC 12 col. `.dash > .panel { margin-bottom:0 }` (le gap gère l'espacement).

Voir `_memoire/conversations/2026-07-08-boussole-dashboard.md`.

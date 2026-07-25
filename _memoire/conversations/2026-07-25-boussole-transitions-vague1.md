# 2026-07-25 — Boussole proto : VAGUE 1 des transitions de lieux (addictif & enfant de 5 ans)

## Concept validé par Mongazi
Chaque écran = un LIEU de la boutique, on y entre par un geste physique reconnaissable (< 1 s, non bloquant, transform/opacity only, son signature, reduced-motion off). Plan complet des 13 écrans proposé et validé — vague 1 implémentée ici, vague 2 à suivre (Bilan-ECG, Stats-constellation, Carnet-répertoire, Factures-tampon, Équipe-badges, Réglages-engrenages, étagère catalogue, pluie de pièces, « premières fois »).

## Implémenté (vague 1)
- **Ventes = ticket qui s'imprime** : rouleau perforé en haut, la liste « sort » du rouleau (translateY -101 %→0 sous overflow hidden, tick-tick `playCountTicks`), le total du jour se **tamponne** (`.stamp`, scale 1.9 rot -7°→0, delay .55 s).
- **Dépenses = portefeuille cuir** : 2 volets brun cousu (rotateX ±94°, origin haut/bas), bouton-pression doré qui saute, **2 billets** (vert/or) qui s'envolent, replié à 1,5 s.
- **Objectifs = flèche dans la cible** : flèche or SVG file en diagonale (cubic-bezier accélérant), se plante au centre de l'anneau → **l'anneau tremble** (`ringHit`) + vibration 25 ms, la flèche s'efface à 2,2 s ; l'anneau se remplit ensuite (déjà existant).
- **Boussole = calibration** : rose des vents en tête d'écran, l'aiguille **tourne vite, hésite, se fixe** (keyframes 0→760→700→732→714→720°), halo au verrouillage (`playSuccess`), puis se range (shrink).
- **Confettis d'objectif (1×/jour)** : au franchissement de l'objectif du jour à l'encaissement (`preObj < obj ≤ postObj` + `meta.confettiDay ≠ aujourd'hui`) → **pluie de 44 confettis** or/émeraude/rose plein écran + toast « 🎉 Objectif atteint… le reste c'est du bonus » + vibration [40,60,40].
- **Flamme de série (accueil)** : pastille « 🔥 N jours de suite à objectif atteint — ne casse pas la série ! » dès 2 jours (flamme qui vacille). `calcStreak()` (aujourd'hui compte s'il est atteint, remonte 60 j) — refactor aussi utilisé par l'alerte positive.

## Mécanique anti-agacement
`_entryFx` : posé par `showSection` (navigation réelle), consommé par le premier bind → les **re-rendus internes ne rejouent JAMAIS la transition** (suppression, changement de période, etc.). Vérifié par QC.

## QC
`qc_v6.js` : **14/14 verts, 0 erreur console** (4 transitions jouées + rangées, non-rejeu interne, confettis au franchissement + marqueur 1×/jour, flamme avec 3 jours fabriqués). Non-régression `qc_v5` et `qc_v4` : tout vert.

Cf [[2026-07-25-boussole-caisse-coffre-couts-detailles]] (le coffre = le modèle du concept).

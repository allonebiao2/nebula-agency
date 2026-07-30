# 2026-07-30 — Boussole : mode performance adaptatif (fluidité)

## Demande de Mongazi
« Analyse Boussole et améliore la fluidité, je ressens des "burg" (lag). Invoque tous les outils de création/amélioration d'app. Relève puis améliore tous les problèmes de lag/défaillance. »

## Diagnostic (skill impeccable → optimize + analyse statique)
App = `boussole/_proto/app.html` (vanilla, ~4100 lignes inline). Comptage : 84 `@keyframes`, 133 `box-shadow`, 121 `animation:`, 11 `requestAnimationFrame`, 6 `backdrop-filter`.
- Les 11 rAF sont **one-shot/événementiels** (count-up, tilt throttlé + `cancelAnimationFrame`) → pas de boucle folle. OK.
- Les 8 animations d'icônes + `icoGlow` (qui anime `filter`) sont **sous `@media (hover:hover)`** → ne tournent jamais sur mobile tactile. OK.
- `armPulse` (box-shadow animé) = seulement sur bouton « armé » (confirm suppression), transitoire. OK.
- `backdrop-filter: blur(22px)` = sur le **tiroir** (visible seulement ouvert). Header = zéro flou (« verre nuit simulé », leçon perf déjà respectée).
- **VRAI problème** : par défaut sur mobile tournent en permanence 3 halos (`haloDrift`) + 16 poussières ×2 (`dustFloat`) + `logoPulse`/`hudDot`/`iaPulse`/`holoScan/Glow/Scale`/`syncBlink`/`flameFlick`/`sellWeigh`/`spendDip`. Ça ne se calmait QUE via `prefers-reduced-motion` (OFF chez presque tous les utilisateurs). **Aucune détection d'appareil faible n'existait.**

## Correctif livré (additif, aucune interaction touchée)
**Mode calme piloté par `.perf-lite` sur `<html>`** :
1. **Script précoce** (juste après `<body>`, avant peinture) : pose `.perf-lite` si `navigator.hardwareConcurrency <= 4` OU `deviceMemory <= 4` OU `connection.saveData`, ou si `localStorage['boussole:perf']==='lite'`. Ajoute aussi un `visibilitychange` → `.perf-pause` quand l'onglet est masqué.
2. **Sonde FPS** (dans le module, après `buildDust`, déclenchée à +900 ms pour laisser le démarrage se calmer) : mesure ~1 s de frames réels ; si < 55 fps → ajoute `.perf-lite`. Respecte `prefers-reduced-motion` et le choix `'full'` mémorisé.
3. **CSS** : `.perf-lite` coupe les animations d'ambiance (halos, poussières figées à opacity .2, pulses header/home, holo) + **retire le `backdrop-filter` du tiroir et du scrim** (l'op GPU la plus lourde). `.perf-pause` met `animation-play-state: paused` sur la couche depth + pulses.
- Les appareils puissants gardent 100 % du rendu.

## Vérif & déploiement
- `node --check` du module (238 Ko) + du script précoce = OK.
- Rebuild dist (proto aplati racine + 7 assets + `sw.js` kill-switch + `_headers`) → `wrangler pages deploy --project-name=boussole --branch=main`.
- Prod vérifiée : `/` et `/app` = 200, `perf-lite` servi (16 occ.), `perfProbe` présent.
- Commit source `f4bfbca` poussé sur `main`.

## Reste / next (proposé à Mongazi)
- **Toggle manuel « Mode léger »** dans Réglages (écrit `localStorage['boussole:perf']`) pour qu'il force le mode calme et sente la différence à la demande, indépendamment de l'auto-détection.
- **Chasse aux bugs empirique** en navigateur réel (webapp-testing / claude-in-chrome) : outillage Playwright/Puppeteer PAS installé localement → à faire dans une passe dédiée, ou cibler les écrans/actions précis que Mongazi signale.
- Les trouvailles du hook impeccable (`overused-font` Arial en repli, `side-tab` bordures) = préexistantes, hors sujet perf, laissées telles quelles (non masquées sans accord).

## Technique réutilisable
Pour une app vanilla très animée visant des téléphones d'entrée de gamme : ne pas compter sur `prefers-reduced-motion` seul (OFF chez la plupart). Ajouter un **mode calme auto** = heuristiques device posées AVANT peinture + **sonde FPS réelle** qui bascule une classe `.perf-lite` coupant les animations d'AMBIANCE en boucle (garder interactions + transitions). Cf. [[project-boussole-refonte]].

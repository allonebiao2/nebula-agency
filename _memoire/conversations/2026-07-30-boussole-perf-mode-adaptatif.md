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

## Vague 2 (2026-07-30) — boot non-bloquant + validation navigateur (Playwright)
Sonde Playwright (`scratchpad/pw/probe2.cjs`, Chrome/Edge via `playwright-core`, mobile 390px + CPU throttle 4× + état démo seedé `sm:state` `demo:true`). **Diagnostic empirique** : le « burg » = **tâches longues qui gèlent le thread principal**, PAS un bug fonctionnel (**0 pageerror, 0 requête échouée** sur tous les écrans). Pire gel = tâche ~1198 ms au démarrage (compil/exec du module inline 238 Ko + 1er rendu) ; Bilan bloque ~391 ms (graphes SVG). Les 88-172 warnings `AudioContext not allowed` = **artefact headless** (audio créé au 1er son, bénin en vrai). Tiroir `wall 3,7 s` mais `blocked=0` = pas un gel (attente d'actionnabilité Playwright).
**Correctifs** : `cloudPull()` (Supabase) et `buildDust()` sortis du chemin critique via `requestIdleCallback` ; poussières **sautées** en `.perf-lite` (moins de DOM/couches GPU).
**Mesuré (CPU 4×, mode calme) avant→après** : chargement **8,8→3,8 s** · FCP **→2,0 s** · pire tâche longue **1198→606 ms** · gel rendu Bilan **391→112 ms** · 0 crash.
**Chemin plein rendu validé** (forcé `full`, sans throttle) : `perf-lite` reste OFF, **30 animations** tournent (premium intact), 0 crash. ⚠️ la machine de test a **4 cœurs** → `hardwareConcurrency<=4` met perf-lite par défaut en test (forcer `full` pour valider le plein rendu).
**Reste (optionnel, plus gros / plus risqué, à décider avec Mongazi)** : la tâche ~500-600 ms au boot = **compilation du module inline 238 Ko** → pour la réduire, **externaliser le JS** (fichier `.js` séparé = cache navigateur + compil en parallèle). Le rendu Bilan (graphes SVG) bloque encore ~250 ms sur appareil puissant (différer le dessin des graphes après la peinture de l'écran). Non faits (refontes plus risquées).
Outillage : `playwright-core` installé dans `scratchpad/pw/` (pilote Edge/Chrome système, **pas de download de navigateur**) — réutilisable pour futurs audits perf.

## Vague 3 (2026-07-30) — externalisation du module + rendu différé Stats/Bilan (les 2 optims lourdes demandées par Mongazi « fais les deux aussi »)
**Externalisation du gros script** : le module inline (238 Ko) sorti dans `boussole/assets/js/proto-app.js` (extraction programmatique idempotente `scratchpad/pw/externalize.cjs`). ⚠️ **piège** : un module ES **externe** résout ses imports relatifs par rapport AU FICHIER JS, pas à la page → l'`import { SUPABASE_URL, ... } from '../assets/js/config.js'` a été corrigé en **`'./config.js'`** (proto-app.js et config.js sont dans le même dossier `/assets/js/`). Résultat : `app.html` **375 → 139 Ko** (parse HTML plus rapide), le JS bénéficie du **cache de compilation V8** aux visites suivantes. Pire tâche longue au boot **606 → 436 ms**. Build : `cp proto-app.js` ajouté au dist ; `_headers` = **`no-cache`** sur proto-app.js (revalidation etag, jamais périmé, cf [[feedback_cache-bust-assets]] — pas besoin de `?v=`).
**Rendu différé Stats/Bilan** : dans `showSection`, ces 2 écrans (graphes SVG lourds) rendent d'abord un **squelette instantané** (même en-tête tag/titre) puis le contenu à la frame suivante (double `requestAnimationFrame`) → le tap est acquitté tout de suite. Gel Bilan **391 → ~136 ms** (perçu quasi nul ; sans toucher aux fonctions de rendu).
**Validé Playwright en local ET sur la prod** (`https://boussole-19d.pages.dev/app`, mobile + CPU 4×) : **0 crash, 0 requête échouée** ; `proto-app.js` servi **200 `application/javascript` no-cache**. Commit `8e0d29b`. ⚠️ le JS de l'app vit désormais dans **`boussole/assets/js/proto-app.js`** (plus dans app.html) — c'est là qu'on édite la logique.

## Technique réutilisable
Pour une app vanilla très animée visant des téléphones d'entrée de gamme : ne pas compter sur `prefers-reduced-motion` seul (OFF chez la plupart). Ajouter un **mode calme auto** = heuristiques device posées AVANT peinture + **sonde FPS réelle** qui bascule une classe `.perf-lite` coupant les animations d'AMBIANCE en boucle (garder interactions + transitions). Cf. [[project-boussole-refonte]].

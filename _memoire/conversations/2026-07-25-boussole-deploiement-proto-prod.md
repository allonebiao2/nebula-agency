# 2026-07-25 — Boussole : mise en production du proto « verre de nuit »

## Demande de Mongazi
« J'ai fait des corrections et améliorations pour le proto Boussole. Supprime l'ancien Boussole et déploie le proto actuel. La dernière modif était il y a quelques minutes avec Claude Code sur mon portable. Déploie-le, le nom c'est boussole. »

## Ce qui a été fait
1. **Récupération du travail du portable** : les corrections étaient sur la branche distante `claude/protocole-boussole-memoire-9xy3j4` (7 features du 2026-07-25 + le dispatch mémoire, commit de tête `d9bf476`), pas encore sur `main`. Fusion **fast-forward** dans `main` puis `git push origin main`.
   - Contenu : édition des ventes / objectifs modifiables / stats par période libre · vague « logiciel » v4 (données propres, onboarding, IA proactive) · caisse-coffre 3D + coûts détaillés par produit · transitions de lieux + confettis d'objectif · signatures Vendre/Dépenser sur l'accueil · salutations intelligentes v2 + sons · correctifs d'audit (perf/vitesse) + sweep UI mobile & PC. `app.html` passe de ~227 Ko à ~371 Ko, + nouveau `etat.sql`.

2. **« Le nom c'est boussole » = résolu sans ambiguïté** : le projet Cloudflare Pages s'appelle déjà littéralement **`boussole`** (account `6289c10a…`, branche de production `main`). Son URL par défaut est `boussole-19d.pages.dev` (Cloudflare a suffixé `-19d` car `boussole` était pris). Donc **déployer sur ce projet = remplacer l'ancienne app, même URL, rien à supprimer/recréer côté Cloudflare**. « Supprimer l'ancien » est réalisé par l'écrasement de la prod.

3. **Construction d'un dist propre** (dans le scratchpad, sources `_proto/` **non modifiées**) : le proto n'est pas autonome, il tire 7 assets de `boussole/assets/` (`js/vendor/supabase.js`, `js/config.js`, `img/skyline-{pc,mobile}.webp`, `icons/logo-boussole-neon.png`, `icons/favicon-48.png`, `fonts/BricolageGrotesque.woff2`). Le reste d'`assets/` (l'ancien app : `app.js`/`ui.js`/`store.js`/`app.css`…) est **exclu** → dist ~1,1 Mo, « ancien » vraiment retiré.
   - Aplatissement à la racine : `connexion.html` → `index.html` (+ copie `connexion.html` pour que le lien retour de l'app marche) et `app.html`, avec réécriture `../assets/` → `/assets/` (seul `../` présent). Liens croisés = `location.href='app.html'` / `location.href='connexion.html'`.

4. **Déploiement** : `wrangler pages deploy <dist> --project-name=boussole --branch=main --commit-dirty=true` → succès (`74a2c411.boussole-19d.pages.dev`).

## Vérification en ligne
- `https://boussole-19d.pages.dev/` → **200**, `<title>Boussole · Connexion (verre de nuit)</title>` (nouveau proto ; l'ancienne app « …gestion financière du commerçant » n'est plus servie).
- `/app.html` → 308 → `/app` → **200** (`Boussole · App (verre de nuit)`) ; `/connexion.html` → 308 → `/connexion` → **200**. Le 308 est la canonicalisation `.html` normale de Cloudflare Pages, suivie automatiquement par le navigateur → navigation intacte.
- Les 7 assets → **200** (bons types MIME : js/webp/png/woff2).

## Points ouverts / à retenir
- **La prod `boussole-19d.pages.dev` n'est PLUS l'ancienne app** : elle sert le proto « verre de nuit ». `proto.boussole-19d.pages.dev` reste la preview branche.
- Il restait au proto (avant ce déploiement) : Agenda, comparateur de périodes, carnet enrichi/relances, intégration réelle à l'app live. Le déploiement les fige tels quels côté public.
- Sources de l'ancien app toujours dans le repo (`boussole/index.html`, `_demo.html`, `sw.js`, `manifest.webmanifest`, `schema.sql`, et les JS/CSS de l'ancien app dans `assets/`) — **non supprimées** (le proto réutilise `assets/`, et supprimer du code source est destructif). À nettoyer plus tard si voulu.
- ⚠️ Rappel sécurité déjà connu : régénérer les clés API Supabase + reset mdp DB + poser la Site URL de prod (le `config.js` déployé porte l'URL + clé anon, comme l'ancienne app).

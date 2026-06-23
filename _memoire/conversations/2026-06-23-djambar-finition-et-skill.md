# Log de session — Djambar Team : finition complète + domaine live + skill `nebula-site`

## Date : 2026-06-23
## Sujet : grosse session sur le site Djambar Team (#05) — de la finition design jusqu'au domaine final, ET construction du skill réutilisable.

> Suite directe de la création (2026-06-22). Site = `clients/05-saeir-thiam-bijouterie/` (hub multi-pages, socle partagé `assets/app.{css,js}`, déployé Cloudflare Pages). Détail technique passe par passe : voir `CONTEXT.md` du client (V7→V17) et `_memoire/procedure-vitrine/EVOLUTION.md`.

## Ce qui a été fait (chronologie des passes)
- **V7 — anti-tells IA** : fin de l'eyebrow majuscule systématique (kickers 4/9/3/3 → 2/3/2/2) ; suppression de la grille de 4 cartes identiques (ban) → panneau éditorial `.creed` ; en-têtes éditoriaux (titre + `.deck`).
- **V8 — motion & fluidité MAX + infra** : View Transitions inter-pages, parallax + barre de progression scroll-driven CSS, reveals différenciés, micro-interactions (sheen boutons, nav underline, CTA aimantés, tilt) ; **page 404 de marque** + **`_headers`** (HSTS, X-Frame, etc. + cache immuable `/assets/*`). 🐛 corrigé un bug LIVE : le voile blanc `.hero::before` délavait les heros sombres `soon-hero` (texte illisible sur communication/événementiel).
- **V9 — hero NUIT à faisceaux** : composant React/shadcn « Beams Background » fourni → **porté en vanilla** (pas de scaffold React, le site est HTML pur). Hero bijouterie en nuit dramatique, faisceaux or/azur `mix-blend:screen`, aura qui respire.
- **V10 — vidéo de fond** dans le volet commander (CTA bijouterie), flou léger + voile.
- **V11 — formulaire de devis → WhatsApp** : 100% client-side, assemble les réponses en message `wa.me` pré-rempli. Champs : identité + « 1ʳᵉ fois en bijouterie ? » + service/bijou/matière/modèle/**taille de bague conditionnelle**/motif/gravure/occasion. Pills tactiles. Les CTA « commander » pointent vers `#devis`.
- **V12 — conversion** : 24 légendes de galerie distinctes ; **lightbox = point de commande** (bouton « Commander ce modèle » pré-remplit WhatsApp avec la pièce) ; sous-titres collections ; nudge. 0 dark pattern.
- **V13 — DOMAINE FINAL `djambarteam.com` LIVE** : acheté Hostinger → DNS déplacé sur Cloudflare → CNAME proxied → Pages custom domains → HTTPS auto. URLs migrées `pages.dev`→`djambarteam.com` (canonical/og/JSON-LD/sitemap/robots).
- **V14 — fonds média** : flou allégé (on voit les pièces) ; fonds colliers (accueil + événementiel) ; vidéo en fond sur page Bientôt. Système `.soon-media` (img|video) + voile.
- **V15/V16 — vidéos de marque** : `thiam.MP4` remplacé par les 2 vidéos fournies ; **CAUSE des vidéos qui ne marchaient pas = codec HEVC** (iPhone) illisible Chrome/FF → **transcodées en H.264** (imageio-ffmpeg). Hero accueil passé en **cinématique sombre** pour que la vidéo soit visible.
- **V17 — ergonomie & fluidité mobile/PC** : inputs 16px (anti-zoom iOS), cibles ≥44px, `html{overflow-x:hidden}` (0 wiggle), `touch-action:manipulation`, beams gated `!isMobile && !saveData`, safe-area iOS sur les FABs.

## ⭐ SKILL `nebula-site` CONSTRUIT
- Distillé depuis la branche cerveau `_memoire/procedure-vitrine/`. Installé `.claude/skills/nebula-site/` (`SKILL.md` runbook PHASE 0→9 run-to-completion + checklist + garde-fous + pièges QA, + `templates/` = socle gold standard).
- ⚠️ `.claude/` gitignoré (comme `studio-quotidien`) → **source versionnée = la branche** + `SKILL.md` mirroré dedans. Renommé de `vitrine-express` → **`nebula-site`** (choix Mongazi).
- **Reste** : tester sur un nouveau formulaire client.

## Décisions clés prises
1. **Honnêteté stack** : refus de scaffolder React/shadcn pour un composant fourni → porter l'effet en natif (le site reste HTML/JS statique, perf 4G).
2. **`djambarteam.com`** : DNS confié à Cloudflare (1 changement de nameservers chez Hostinger), pas géré chez Hostinger. Domaine reste propriété Hostinger.
3. **0 dark pattern** sur la conversion (pas de fausse urgence/faux stock/faux avis) — cohérent luxe + honnêteté.
4. **Vidéo web = H.264 obligatoire** (jamais HEVC en prod).

## Fichiers touchés (principaux)
- `clients/05-saeir-thiam-bijouterie/` : 4 pages + `404.html` + `_headers` + `assets/app.{css,js}` + `assets/videos/fond-video{,-2}.mp4` (H.264) + `CONTEXT.md`.
- `.claude/skills/nebula-site/` (local) ; source `_memoire/procedure-vitrine/` (SKILL.md, EVOLUTION.md, README, SPEC).
- `CLAUDE.md` (table clients), `_memoire/journal/2026-06-23-journal.md`, `_memoire/decisions.md`, mémoire auto (project_procedure-vitrine, reference_domaines).

## Reste à faire (côté Mongazi/client)
- Vrais avis clients · photos sans watermark (ou reshoot) · activer Cloudflare Web Analytics (1 clic) · tester le parcours WhatsApp en vrai · régénérer l'affiche PDF avec QR « site » `djambarteam.com` · redirection www→apex (optionnel) · **tester `nebula-site` sur un nouveau client**.

## Liens
- LIVE : https://djambarteam.com · Back-office lead : https://partenaires.nebula-agency.online
- Skill : `.claude/skills/nebula-site/` · Cerveau : `_memoire/procedure-vitrine/`

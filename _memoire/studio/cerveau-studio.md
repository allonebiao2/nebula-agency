# NEBULA Studio Quotidien — Cerveau du produit

> Agent créatif : **2 contenus publiables par jour** (script + vidéo de marque), tous différents, livrés sur Telegram **avant 13h**. Créé 2026-06-20. Lié à [[2026-06-21-journal]].

## Quoi
Du contenu **éducatif de valeur** (« le saviez-vous ? ») sur le digital (vitrines, sites, présence en ligne) pour rendre les commerçants plus malins. **Marque = NEBULA Agency** (NOVA est l'agent, pas le sujet du contenu). Marché : Afrique de l'Ouest francophone.

## Où
- Code : `studio/` — `brain.py` (cerveau Claude Opus + taxonomie 24 formats + registre `ledger.jsonl` anti-répétition), `render.py` (vidéo), `heygen.py` (avatar optionnel OFF), `deliver.py` (Telegram), `run_daily.py` (orchestrateur, `STUDIO_COUNT=2`).
- Skill : `.claude/skills/studio-quotidien/` (avec « journal des décisions » à tenir à jour).
- Automatisation : `.github/workflows/studio-quotidien.yml` — cron `0 7 * * *` (08:00 Cotonou), `timeout-minutes: 45`.

## Vidéo
- **MP4 vertical 4K (2160×3840), 9:16, 60 i/s.** Rendu **déterministe image par image** (gabarit `templates/kinetic.html` expose `__seek(t)`/`__DURATION`, capture frame par frame, ffmpeg `-crf 18`). **Ne PAS revenir à `record_video`** (ralenti).
- Vrai **logo** `studio/assets/nebula-logo.png` (transparent), police **futuriste** Exo 2 + Orbitron. Style `stat` = blanc solide (background-clip:text invisible avec spans). `fitFont` = titre toujours à l'écran. Polices non bloquantes + `wait_until=commit`.

## Activation (reste à faire)
Poser les **secrets GitHub** : `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (+ `HEYGEN_API_KEY` si avatar). Réglages : `STUDIO_COUNT`, `STUDIO_VIDEO` (kinetic|heygen), `STUDIO_MODEL`.

## Détail technique
Voir la mémoire auto `project_studio-quotidien` (la plus à jour) et [[2026-06-21-journal]] §1.

# ⛔ luxuryclub229.com EST EN MAINTENANCE (depuis le 26/11/2026)

Demande de Mongazi, le 26/11 : « je ne veux pas qu'elle voie les modifications là-bas, coupe la visibilité, il faut que
ça affiche en maintenance ».

- **Ce qui est servi** : `_maintenance/_worker.js`. Toutes les adresses répondent une page « Notre site fait peau neuve »
  avec un 503 (indisponibilité temporaire : Google garde le site), en `noindex`. Le bouton WhatsApp de la maison reste.
  Déploiement de la maintenance : `15f909bb`.
- **Le verrou** : tant que ce fichier existe, `python _outils/_dist.py` REFUSE de préparer la production.
  - `python _outils/_dist.py --apercu` : livrable pour une adresse d'aperçu, puis
    `wrangler pages deploy _dist --project-name luxury-club-229 --branch apercu`. Le site reste fermé, et l'aperçu
    est servi sur https://apercu.luxury-club-229.pages.dev (Cloudflare le marque `noindex`).
  - **Rouvrir le site** (seulement sur la décision de Mongazi) : `python _outils/_dist.py --rouvrir`, puis
    `wrangler pages deploy _dist --project-name luxury-club-229 --branch main`. Supprimer ensuite ce fichier.
- Remettre la maintenance : `wrangler pages deploy _maintenance --project-name luxury-club-229 --branch main`.

# Apprentissages — pièges techniques (session 2026-06-20/21)

Pièges rencontrés et résolus. À relire avant de toucher au même genre de code. Lié à [[2026-06-21-journal]].

## 1. ⚠️ PowerShell corrompt les fichiers UTF-8 (le plus dangereux)
`Get-Content -Raw $f` (lecture cp1252 par défaut en PS 5.1) **puis** `Set-Content -Encoding utf8` = **double-encodage** → accents en mojibake (`é`→`Ã©`) + BOM ajouté. A corrompu `server.py` (réparé via `git checkout` + ré-application des edits).
- **Règle** : pour éditer un fichier de code/contenu, **toujours l'outil Edit** (jamais Get-Content/Set-Content). PowerShell uniquement pour git/commandes, pas pour réécrire des fichiers.
- `Copy-Item` est sûr (copie binaire) ; `Set-Content -Encoding utf8` ne l'est pas (BOM).

## 2. Vidéo générée : rendu DÉTERMINISTE image par image (pas record_video)
L'enregistrement temps réel de Playwright (`record_video`) donne du **ralenti + frames perdues** quand le navigateur headless ne suit pas (animations lourdes). 
- **Solution** : gabarit qui expose `__seek(t)` + `__DURATION`, **aucune animation CSS**, on calcule chaque frame à un temps exact → screenshot → ffmpeg. Vitesse parfaite, net.
- Polices Google **non bloquantes** (`<link media="print" onload="this.media='all'">`) + `wait_until="commit"` sinon `Page.goto` timeout en headless.
- `background-clip:text` + `color:transparent` devient **invisible** si le texte est dans des spans `inline-block` → utiliser une couleur solide.
- ffmpeg dispo via `imageio-ffmpeg` (binaire embarqué pip) si pas de ffmpeg système.

## 3. Resend (emails)
- Une clé Resend peut être valide mais le **domaine non vérifié** → 403. Vérifier `GET /domains` : seul **`nebula-agency.online`** est vérifié (DKIM+SPF), pas `.com`. **Envoyer depuis `contact@nebula-agency.online`.**
- Pour ENVOYER, seuls DKIM + SPF comptent ; le MX « Receiving » (réception) peut rester `failed` sans bloquer l'envoi.

## 4. Telegram (un webhook par bot)
- `getWebhookInfo` AVANT `setWebhook` : un bot ne peut avoir qu'**un seul** webhook. Le mettre écrase celui d'un autre service. @Nova_de_nebula_bot servait Vendora.
- Sécuriser le webhook avec `secret_token` (header `X-Telegram-Bot-Api-Secret-Token`).
- Envoi sortant en **thread daemon** (non bloquant) pour ne pas ralentir les requêtes.

## 5. NEBULA Affiliés — vérifications
- **`/admin` redirige vers `/` si pas connecté** (sécurité). Pour vérifier l'admin en prod : se connecter (POST `/api/admin/login`) PUIS GET `/admin` avec la session. Sinon on teste la mauvaise page.
- Le `?v=` ne buste QUE les assets liés (app.css/app.js). Les changements **inline** d'un HTML se chargent au rechargement de la page (la page elle-même n'est pas en cache long). Mais si app.js change, **bumper le `?v=`** partout où il est chargé.
- Railway affiliés **auto-déploie au push** ; vérifier en authentifié + cache-bust (`?z=timestamp`). Domaine via relais Cloudflare (`partenaires.nebula-agency.online`).

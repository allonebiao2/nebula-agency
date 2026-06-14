# 04 · Tech & Architecture

## Architecture 3 couches (LIVE)
1. **Backend** FastAPI + SQLite sur **Railway** — service `vitrina`, **volume `/data`** (persistance), URL `vitrina-production-686b.up.railway.app`.
   - Redeploy : `railway up --ci -p 3d1f7f58-7020-4e27-a7a5-3fb007d734f5 -s vitrina -e production` **depuis `vitrina/`**.
2. **Proxy** Cloudflare **Pages** — projet `vitrina-proxy` (`vitrina/cfproxy/_worker.js` = reverse-proxy vers l'URL Railway).
   - Redeploy : `wrangler pages deploy vitrina/cfproxy --project-name=vitrina-proxy` (token Pages dans `secrets/cloudflare.env`).
3. **DNS** chez **Hostinger** (NS `artemis/hermes.dns-parking.com`) : CNAME `vitrina` → `vitrina-proxy.pages.dev` (comme `www`→pages.dev, `vendora`→railway).

## Pourquoi ce montage (à ne pas oublier)
Railway **bloque l'ajout d'un domaine custom** (plan payant / CB) ; le DNS de `nebula-agency.online` est **chez Hostinger**, pas Cloudflare ; le token Cloudflare local est **Pages-only** (ni Zone DNS ni Workers). Le **proxy Pages contourne tout**, 100 % gratuit.

## Fichiers (`vitrina/`)
- `index.html` (vente) · `creer.html` (générateur client-side) · `exemple-beaute.html`
- `server.py` (FastAPI : /api/order, /admin + login, /v/{slug}, Telegram)
- `.env` (secrets, **gitignored**) · `requirements.txt` · `Procfile`
- `cfproxy/_worker.js` (proxy Pages)
- `presentation-vitrina.html` + `.pdf` (deck commercial, servi sur le site)

## Stack
HTML/CSS/JS pur (générateur 100 % client-side, base64 images), FastAPI, SQLite (+ migrations colonnes), Telegram Bot API, MoMo manuel. Volontairement léger.

# 07 · Décisions & Apprentissages

> Ce fichier s'enrichit **en continu**. Toute nouvelle décision ou leçon va ici, datée.

## Décisions (datées)
- **2026-06-12** — Paiement **manuel + Telegram + back-office** > FedaPay/API MTN au démarrage (rapide, gratuit, contrôle, universel).
- **2026-06-12** — **1 produit phare** (mini-site beauté) avant catalogue ; upsells via **gating** par pack.
- **2026-06-12** — **Email obligatoire** à la commande (clé des rappels, comme les abonnements NEBULA).
- **2026-06-13** — **Garder un vrai domaine** (`vitrina.nebula-agency.online`) plutôt qu'une URL Railway anonyme (choix Mongazi ; anonymat partiel accepté).
- **2026-06-13** — Déploiement via **Railway + proxy Cloudflare Pages + DNS Hostinger** (contourne le blocage domaine custom de Railway, gratuit).
- **2026-06-13** — Back-office **sécurisé** : login mot de passe + cookie HMAC (fin du `?key=`).

## Apprentissages (à enrichir)
- 🔑 Le **bottleneck = l'acquisition**, pas le produit (leçon Vendora). Traiter le tunnel/pub avec autant de sérieux que le produit.
- 🔧 Railway **n'autorise pas** de domaine custom sans plan payant → **Cloudflare Pages proxy** (gratuit) est la parade quand le DNS est externe (Hostinger).
- 🔧 Git Bash **mange les chemins** type `/data` (les convertit) → utiliser PowerShell ou `MSYS_NO_PATHCONV=1` pour les variables Railway.
- ⏳ *(à compléter avec le réel : taux de conversion, prix validés en A/B, canaux d'acquisition qui marchent, coût IA par génération…)*

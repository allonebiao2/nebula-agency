# Stack — Nebula Agency

> Outils, technologies et techniques utilisés sur les projets.
> Les **secrets et clés API** sont stockés dans `.env` local (ignoré par git) — jamais commités sur GitHub.

---

## Front-end

- **HTML5** — un fichier autonome par vitrine quand c'est possible.
- **CSS** — vanilla, parfois custom properties pour la palette.
- **JavaScript** — vanilla, sans framework par défaut.
- **Images** : base64 obligatoire (pas de CDN externe).

## Design

- **Maquettes** : à définir (Figma ? direct HTML ?)
- **Typographies** : Google Fonts ou self-hosted selon performance.
- **Icônes** : à standardiser (Lucide ? Heroicons ? SVG inline ?)

## Performance

- Images optimisées avant intégration (WebP quand possible).
- Pas de dépendances JS lourdes sans raison.
- Score Lighthouse visé : > 90 mobile.

## Hébergement / déploiement

- **Vitrines clients** : Netlify
- **VPS** : Hostinger (`72.61.103.56`) pour n8n self-hosted
- Nom de domaine : géré par le client la plupart du temps.

## Automatisation

- **n8n** self-hosted sur VPS Hostinger
- Workflows : commandes WhatsApp, notifications paiement, génération devis

## Intelligence Artificielle

- **Claude Anthropic** — génération de contenu, build vitrines via Claude Code
- **Gemini** — image generation, analyse
- **Groq** (`llama-3.3-70b`) — inférence rapide pour bots WhatsApp

## Communication

- **WhatsApp Business** : canal principal client
- **Twilio** : automatisations bot WhatsApp via n8n
- ⚠️ Twilio NON utilisé pour les vitrines simples (lien WhatsApp natif suffit)

## Base de données

- **Supabase** : commandes, leads, sous-comptes clients

---

## FedaPay — Paiement Mobile Money

### Configuration
- Provider de paiement Mobile Money + cartes pour l'Afrique de l'Ouest
- Compte principal NEBULA Agency (en attente de validation)
- Sous-comptes par client via "+ Ajouter un compte" dans le dashboard

### Clés API
Les clés sont dans `.env` local (voir `.env.example` pour la structure) :
- `FEDAPAY_PUBLIC_KEY` → `pk_live_*` → côté client (HTML, JS)
- `FEDAPAY_SECRET_KEY` → `sk_live_*` → côté serveur UNIQUEMENT (n8n, webhooks)

### Règles de sécurité
- ❌ **Jamais** mettre `sk_live_*` dans le code HTML d'une vitrine
- ❌ **Jamais** exposer la clé secrète dans une variable JS frontend
- ❌ **Jamais** coller les clés dans Claude.ai (uniquement Claude Code local)
- ✅ Toujours utiliser la clé publique côté navigateur
- ✅ Toute opération sensible (refund, lecture transactions) passe par le serveur n8n

### Notifications paiement — triple confirmation
1. **WhatsApp** : bouton "Confirmer" (1 tap pour le client)
2. **MyFeda** : notification dans l'app mobile FedaPay (note 2.8/5)
3. **Email** : natif FedaPay, automatique

### Validation compte FedaPay — checklist
- Adresse complète : ville + quartier + carré
- Description précise de l'activité
- Justificatifs uploadés

---

## Outils de travail

- **Éditeur** : VS Code + Obsidian (même dossier, sync auto)
- **IA** : Claude Code (avec ce repo comme contexte)
- **Versioning** : Git (commits lisibles par étape significative)
- **GitHub** : compte `allonebiao2`, repo `nebula-agency`

## Sécurité — gestion des secrets

- `.env` ignoré par git (voir `.gitignore`)
- `.env.example` commité comme template (sans valeurs réelles)
- Clés API : uniquement dans Claude Code local, **jamais** dans Claude.ai web

---

## À évaluer

- [ ] Système de build minimal (concat CSS/JS) si projets plus gros
- [ ] Bibliothèque d'animations légère (GSAP ? Motion One ?)
- [ ] Solution CMS pour clients voulant éditer eux-mêmes

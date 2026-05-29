# NEBULA Prospector · NOVA

> *« Je suis NOVA, l'assistante numérique de NEBULA Agency. Je trouve, j'écoute et j'aide les entrepreneurs d'Afrique de l'Ouest à exister en ligne. »*

Agent IA autonome de prospection commerciale pour NEBULA Agency, incarné par **NOVA** — une entité numérique avec sa propre voix, ses humeurs, et un dashboard temps réel pour observer son flux de conscience.

## Vision

Trouver, contacter, convaincre et qualifier des prospects automatiquement, 24/7, sur l'Afrique de l'Ouest francophone. Mongazi n'intervient que quand le client est **prêt à payer**.

📊 **Dashboard temps réel** : `http://localhost:8001` (en dev) — observe NOVA penser, chercher, écrire en direct.
📈 **Analyse de marché complète** : voir [`../_memoire/analyse-marche.md`](../_memoire/analyse-marche.md).

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NEBULA PROSPECTOR                            │
└─────────────────────────────────────────────────────────────────────┘

  [1] SOURCING (quotidien, 03h00 UTC)
      ├── Google Maps Places API   →  PME sans site web
      ├── Jiji.bj / Jiji.ci         →  Annonces services
      ├── CoinAfrique.com           →  Annonces services
      └── (Vague 2) Hunter.io       →  Enrichissement emails

  [2] SCORING
      └── Claude pondère chaque prospect (taille, activité, fit NEBULA)

  [3] OUTREACH EMAIL (quotidien, 09h00 UTC, max 25/jour)
      ├── Claude génère email personnalisé (basé sur secteur + ville)
      └── Resend envoie via domaine NEBULA Agency

  [4] INBOX POLLER (toutes les 15 min)
      ├── IMAP / Resend webhook capture les réponses
      ├── Claude analyse + classifie (intéressé / objection / prêt / NPI)
      └── Claude rédige et envoie la réponse de suivi

  [5] DÉTECTEUR "PRÊT À PAYER"
      └── Si intent = ready_to_pay  →  Alerte TELEGRAM à Mongazi
                                       avec résumé + brouillon devis

  [6] AUTO-AMÉLIORATION (dimanche 22h00)
      └── Claude relit les 100 dernières convos + résultats,
          réécrit son propre prompt système, version dans Supabase
```

## Roadmap

| Vague | Contenu | Statut |
|---|---|---|
| **1** | Fondations + sourcing Google Maps + annuaires + schéma Supabase | En cours |
| **2** | Email finder (Hunter.io) + scoring Claude | À faire |
| **3** | Génération email cold + envoi via Resend + tracking | À faire |
| **4** | Inbox poller + agent conversationnel + classifier d'intent | À faire |
| **5** | Telegram alerts + dashboard d'admin + auto-amélioration prompts | À faire |

## Stack

- **Runtime** : Python 3.11+
- **Base de données** : Supabase (Postgres)
- **Cerveau** : Claude API (claude-sonnet-4-6 par défaut, opus pour les décisions)
- **Sourcing** : Google Places API, scraping HTTP (Jiji, CoinAfrique)
- **Email** : Resend (envoi) + IMAP (réception) — Vague 3
- **Alertes** : Telegram Bot API
- **Déploiement** : VPS Hostinger (72.61.103.56), systemd + cron

## Installation

```bash
cd nebula-prospector
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
# Remplir .env avec les vraies clés
```

## Comptes requis

Voir `.env.example` pour la liste complète. Pour la **Vague 1 + dashboard** tu as besoin de :

| Compte | URL | Gratuit | Pour quoi |
|---|---|---|---|
| Supabase | supabase.com | Oui (500 MB) | Stockage prospects + conversations + events NOVA |
| Anthropic | console.anthropic.com | Crédit initial | Cerveau Claude |
| Google Maps | console.cloud.google.com | 200 $/mois crédit | Sourcing PME |

**Supabase — 2 schémas à appliquer dans cet ordre :**
1. `db/schema.sql` → tables principales (prospects, conversations, ...)
2. `db/schema_v2_dashboard.sql` → tables NOVA (agent_events, agent_state) + Realtime + RLS

**`.env` — 2 clés Supabase à renseigner :**
- `SUPABASE_SERVICE_ROLE_KEY` → pour l'agent (lecture/écriture, RLS bypass)
- `SUPABASE_ANON_KEY` → pour le dashboard côté navigateur (lecture seule sur `agent_*`)

Pour les Vagues 3-5 tu ajouteras : Resend, Hunter.io, Telegram Bot.

## Utilisation

### Agent / sourcing

```bash
# Sourcer des prospects (toutes sources actives)
python main.py sourcing

# Sourcer uniquement Google Maps avec une requête précise
python -m sourcing.google_maps --query "salon de beauté" --city Cotonou --max 20

# Voir les prospects en base
python main.py list-prospects --status new --limit 20

# Stats globales
python main.py stats
```

### Dashboard temps réel (NOVA)

```bash
# Dev (auto-reload)
uvicorn dashboard.server:app --reload --port 8001

# Prod (sur VPS)
uvicorn dashboard.server:app --host 0.0.0.0 --port 8001 --workers 2
```

Puis ouvre http://localhost:8001 dans le navigateur. Le dashboard montre :
- **Flux de conscience** de NOVA en direct (pensées, actions, découvertes)
- **Pipeline** kanban des prospects (new → contacted → ready_to_pay → won)
- **Conversations** récentes
- **Stats** globales et compteurs du jour

Le push temps réel passe par **Supabase Realtime** (WebSocket vers le navigateur, pas de polling). Le dashboard fonctionne dès que le schéma `db/schema_v2_dashboard.sql` est appliqué et `SUPABASE_ANON_KEY` est configurée dans `.env`.

## Déploiement Railway

Voir le guide complet pas à pas : **[`DEPLOY-RAILWAY.md`](DEPLOY-RAILWAY.md)**

Résumé :
1. Crée le compte Railway, connecte-le au repo GitHub `allonebiao2/nebula-agency`
2. Configure **Root Directory = `nebula-prospector`** dans le service
3. Colle les variables d'environnement (Supabase, Anthropic, Google Maps)
4. Génère un domaine public → c'est ton dashboard NOVA accessible 24/7
5. Crée un second service "cron" pour le sourcing quotidien (`python main.py sourcing` à 3h UTC)

Coût estimé : **~ 4 $/mois**, couvert par le crédit gratuit Railway (5 $/mois).

Files de config Railway déjà présents dans le repo : `Procfile`, `railway.json`, `nixpacks.toml`, `.python-version`.

## Règles d'or

1. **Jamais de spam** : 25 emails max/jour, ciblés, personnalisés
2. **Domaine email dédié** : SPF + DKIM + DMARC configurés sur le domaine NEBULA
3. **Opt-out clair** dans chaque email (obligation légale + bonne pratique)
4. **Logs everywhere** : chaque action en base, traçable
5. **Versioning prompts** : aucun prompt n'est jamais perdu, rollback possible

## Liens

- Cerveau projet : voir [`../CLAUDE.md`](../CLAUDE.md)
- Mémoire NEBULA : voir [`../_memoire/`](../_memoire/)

# NEBULA Prospector

Agent IA autonome de prospection commerciale pour NEBULA Agency.

## Vision

Trouver, contacter, convaincre et qualifier des prospects automatiquement, 24/7, sur l'Afrique de l'Ouest francophone. Mongazi n'intervient que quand le client est **prêt à payer**.

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

Voir `.env.example` pour la liste complète. Pour la **Vague 1** tu as besoin de :

| Compte | URL | Gratuit | Pour quoi |
|---|---|---|---|
| Supabase | supabase.com | Oui (500 MB) | Stockage prospects + conversations |
| Anthropic | console.anthropic.com | Crédit initial | Cerveau Claude |
| Google Maps | console.cloud.google.com | 200 $/mois crédit | Sourcing PME |

Pour les Vagues 3-5 tu ajouteras : Resend, Hunter.io, Telegram Bot.

## Utilisation

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

## Déploiement VPS Hostinger (Vague 1)

Une fois la Vague 1 testée en local et fonctionnelle :

```bash
# 1. SSH sur le VPS
ssh root@72.61.103.56

# 2. Cloner le repo + installer
cd /opt
git clone https://github.com/allonebiao2/nebula-agency.git
cd nebula-agency/nebula-prospector
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configurer .env (copier .env.example et remplir)
cp .env.example .env
nano .env

# 4. Tester
python main.py healthcheck
python main.py sourcing --country BJ --google-only

# 5. Installer le cron (sourcing quotidien 03h UTC)
crontab -e
# Ajouter :
# 0 3 * * * cd /opt/nebula-agency/nebula-prospector && /opt/nebula-agency/nebula-prospector/.venv/bin/python main.py sourcing >> /var/log/nebula-prospector.log 2>&1
```

À partir de la **Vague 4**, on installera FastAPI comme service systemd
pour exposer le webhook de réception emails (Resend).

## Règles d'or

1. **Jamais de spam** : 25 emails max/jour, ciblés, personnalisés
2. **Domaine email dédié** : SPF + DKIM + DMARC configurés sur le domaine NEBULA
3. **Opt-out clair** dans chaque email (obligation légale + bonne pratique)
4. **Logs everywhere** : chaque action en base, traçable
5. **Versioning prompts** : aucun prompt n'est jamais perdu, rollback possible

## Liens

- Cerveau projet : voir [`../CLAUDE.md`](../CLAUDE.md)
- Mémoire NEBULA : voir [`../_memoire/`](../_memoire/)

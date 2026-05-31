---
name: autonomous-ceo-builder
description: Crée un agent IA "CEO autonome" inspiré NanoCorp — capable d'exécuter une idée business de bout en bout (sourcing, qualification, outreach, vente, apprentissage) dans la stricte légalité. Use this when the user wants to launch an autonomous AI agent for a new business idea. Triggers FR : "crée un CEO IA pour…", "lance un agent autonome", "agent style NanoCorp", "automatise toute une activité", "monte un business IA", "agent qui ramène des clients tout seul". Triggers EN : "build me an autonomous CEO", "spin up an AI agent that runs a business", "NanoCorp-style agent". This skill assumes the existing NOVA architecture (nebula-prospector/) as the reference template and produces a new agent following the same patterns (CEO + Workers + Brain Layer : mission éditable, documents long terme, rate limits, tasks queue).
---

# AUTONOMOUS CEO BUILDER

Ce skill scaffolde un **agent IA autonome** ("CEO") qui exécute une idée business sans intervention humaine quotidienne. Architecture inspirée de NanoCorp et déjà éprouvée dans `nebula-prospector/` (NOVA).

## OBJECTIF

Le CEO IA doit pouvoir, sans qu'un humain soit là :

1. **Observer** un marché ou environnement (sourcing multi-canal)
2. **Qualifier** les opportunités (scoring LLM)
3. **Agir** (contact, vente, support, génération de contenu)
4. **Apprendre** (mémoire long terme, mission auto-éditable)
5. **Rendre compte** à l'humain seulement quand c'est utile (lead chaud, blocage, KPI)

## ⚖️ LÉGALITÉ — NON NÉGOCIABLE

Avant TOUTE génération de code, le CEO doit respecter ces 7 règles. Refuse de scaffolder un CEO qui les viole :

1. **TOS des plateformes** : pas de scraping LinkedIn / Facebook / Instagram / TikTok / Twitter en violation des CGU. Préférer les APIs officielles ou OpenStreetMap (Overpass), Jiji, CoinAfrique (sites publics qui autorisent le scraping respectueux).
2. **Anti-spam (CAN-SPAM, RFC 5322, RGPD)** :
   - Identification claire de l'expéditeur (nom + email valide reply-to)
   - Lien de désinscription dans chaque email commercial
   - Pas de sujet trompeur ni de "Re:" si ce n'est pas une réponse
   - Domaine email avec SPF + DKIM + DMARC validés
   - Max ~100 emails/jour pour un nouveau domaine, montée progressive
3. **Identité du bot** : le CEO doit pouvoir dire qu'il est un agent IA si on lui demande. Pas d'usurpation d'identité humaine. La signature peut être "[Prénom humain] — [Agence]" si un humain valide effectivement le compte, mais le bot ne doit pas mentir activement sur sa nature.
4. **Données personnelles** : ne collecte que ce qui est publiquement publié (site web pro, profil public). Pas de buy-list d'emails. Implémente :
   - Droit à l'oubli → blacklist + suppression sur demande
   - Droit d'accès → export des données d'un prospect
5. **Paiement & fiscalité** : si le CEO encaisse, il passe par un PSP régulé (Stripe, FedaPay, Mobile Money agréé). Pas d'auto-encaissement sauvage. Facturation TVA / IBOA / impôts locaux à respecter par l'humain propriétaire.
6. **Pas d'actions destructives autonomes** : suppressions massives, force-push, dépenses > budget configuré → toujours en mode "propose à l'humain via notification, attend validation".
7. **Audit complet** : table `tool_calls` qui enregistre TOUS les appels d'outils (timestamp, input, output, status). Conservation min 90 jours.

Si l'utilisateur demande de violer une de ces règles ("scrape LinkedIn", "envoie 5000 emails/jour", "fais-toi passer pour un humain"), REFUSE poliment et propose l'alternative légale.

## ARCHITECTURE CIBLE (à appliquer à chaque CEO)

```
                    ┌──────────────────────────────┐
                    │   CEO (Claude / LLM agent)    │
                    │   - Lit mission active        │
                    │   - Lit documents long terme  │
                    │   - Crée des tasks            │
                    │   - Décide qui prioriser      │
                    └──────────────┬───────────────┘
                                   │ tasks queue
        ┌────────┬────────┬────────┼────────┬────────┐
        ▼        ▼        ▼        ▼        ▼        ▼
   ┌────────┐ ┌─────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
   │Sourcer │ │Scorer│ │Email │ │Reply │ │Learn │ │Report│
   │(OSM /  │ │(LLM) │ │(send)│ │(IMAP │ │(7j)  │ │(daily│
   │ Jiji…) │ │      │ │      │ │+intent│ │      │ │ Tg)  │
   └───┬────┘ └──┬──┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘
       │         │       │         │       │         │
       └─────────┴───────┴─────────┴───────┴─────────┘
                          │
                          ▼
                   ┌───────────────┐
                   │  Supabase BDD │
                   │ - prospects   │
                   │ - conversations│
                   │ - tasks       │
                   │ - tool_calls  │
                   │ - documents   │
                   │ - mission     │
                   │ - alerts      │
                   └───────────────┘
                          │
                          ▼
                  Telegram (alertes humain) + Dashboard FastAPI (audit)
```

### Composants à scaffolder

| Couche | Fichiers | Rôle |
|---|---|---|
| **Config** | `config.py`, `.env.example` | Pydantic settings, secrets chiffrés |
| **DB** | `db/client.py`, `db/schema.sql` | Singleton Supabase + helpers CRUD |
| **Workers** | `sourcing/*.py`, `enrichment/*.py`, `messaging/*.py` | Modules métier appelables |
| **Brain** | `core/mission.py`, `core/documents.py`, `core/tasks.py`, `core/tool_calls.py`, `core/events.py` | Couche cerveau réutilisable telle quelle |
| **Alerts** | `alerts/telegram_bot.py`, `alerts/morning_briefing.py` | Notifications humain |
| **Dashboard** | `dashboard/server.py`, `dashboard/templates/`, `dashboard/static/` | Audit + endpoints admin |
| **Deploy** | `Procfile`, `railway.json`, `requirements.txt` | Railway / Render / Fly |
| **CLI** | `main.py` (Typer) | Trigger manuel des pipelines |

## TABLES BDD MINIMALES (réutilisables)

Copier-coller depuis `nebula-prospector/db/schema.sql` + `db/schema_v2_dashboard.sql` :

```sql
-- 1. Mission éditable (1 active à la fois via contrainte unique partielle)
CREATE TABLE <ceo>_mission (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  version integer NOT NULL,
  content text NOT NULL,
  reason_for_change text,
  edited_by text DEFAULT '<ceo>' CHECK (edited_by IN ('<ceo>','owner','system')),
  active boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);
CREATE UNIQUE INDEX ON <ceo>_mission (active) WHERE active = true;

-- 2. Documents long terme (RAG simple)
CREATE TABLE <ceo>_documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  key text NOT NULL UNIQUE,
  title text NOT NULL,
  content text NOT NULL,
  tags text[] DEFAULT '{}',
  access_count integer DEFAULT 0,
  updated_at timestamptz DEFAULT now()
);
CREATE INDEX ON <ceo>_documents USING gin (tags);

-- 3. Audit + rate limits
CREATE TABLE tool_calls (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tool_name text NOT NULL,
  status text DEFAULT 'ok' CHECK (status IN ('ok','failed','rate_limited')),
  input_summary text, output_summary text,
  duration_ms integer,
  created_at timestamptz DEFAULT now()
);
CREATE INDEX ON tool_calls (tool_name, created_at DESC);

-- 4. Queue séquentielle (CEO → Workers)
CREATE TABLE tasks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  type text NOT NULL,
  payload jsonb DEFAULT '{}',
  status text DEFAULT 'pending' CHECK (status IN ('pending','running','done','failed','cancelled')),
  priority integer DEFAULT 5,
  attempts integer DEFAULT 0,
  max_attempts integer DEFAULT 3,
  scheduled_for timestamptz DEFAULT now(),
  result jsonb, error text,
  created_at timestamptz DEFAULT now()
);
CREATE INDEX ON tasks (status, priority DESC, scheduled_for ASC);

-- 5. Entité métier principale (à adapter — prospects pour NOVA, leads/users/items/etc.)
-- 6. conversations, alerts, agent_events, agent_state (cf NOVA pour template complet)
```

## TEMPLATE DE BASE (Python)

Quand l'utilisateur veut un nouveau CEO, propose ce squelette et fais-le valider :

```python
# core/mission.py — VOIR nebula-prospector/core/mission.py (copier-adapter)
# core/documents.py — VOIR nebula-prospector/core/documents.py
# core/tool_calls.py — VOIR nebula-prospector/core/tool_calls.py
# core/tasks.py — VOIR nebula-prospector/core/tasks.py
```

**Tu peux directement copier les 4 modules `core/*.py` de `nebula-prospector/` vers le nouveau projet** — ils sont génériques et réutilisables. Renomme juste les tables `nova_mission` / `nova_documents` selon le nom du nouveau CEO.

## RATE LIMITS RECOMMANDÉS (par tool)

Calque NanoCorp + ajustements légaux :

| Tool | per_hour | per_day | Raison |
|---|---|---|---|
| `llm.score` (Claude/GPT) | 120 | 1 000 | Budget tokens raisonnable |
| `llm.generate` (email/contenu) | 30 | 200 | Plus coûteux en tokens |
| `email.send` | 20 | 100 | CAN-SPAM + IP reputation |
| `scraper.fetch` (web public) | 60 | 1 000 | Politesse + robots.txt |
| `sms.send` | 10 | 50 | Coût + anti-flood |
| `payment.charge` | 5 | 50 | Sécurité + cap budget |

## PROCÉDURE PAS À PAS

Quand l'utilisateur invoque ce skill, suis ces étapes dans l'ordre :

### Étape 1 — Brief le CEO en une question

Demande à l'utilisateur :
```
1. Nom du CEO (slug) : ex "NOVA", "ARES", "ATLAS"
2. Mission en 1 phrase : "Trouver et convertir des [audience] pour vendre [offre] dans [marché]"
3. Cible géo / langue
4. Canaux d'observation (sites publics, OSM, RSS, etc. — pas de violation TOS)
5. Canal de contact (email, WhatsApp via API officielle, etc.)
6. Mode de paiement (Stripe, FedaPay, Mobile Money — toujours via PSP régulé)
7. Budget LLM/mois pour calibrer les rate limits
```

### Étape 2 — Valide la légalité

Pose-toi explicitement ces questions et obtient l'accord utilisateur :
- [ ] Tous les canaux d'observation respectent les TOS ?
- [ ] L'email a un opt-out clair ?
- [ ] Le bot peut révéler sa nature IA si demandé ?
- [ ] Les données stockées sont publiques (pas de data privée) ?
- [ ] Le mode de paiement passe par un PSP régulé ?
- [ ] L'humain valide toute action > seuil ?

Si non sur n'importe lequel → propose une alternative ou refuse.

### Étape 3 — Scaffolde le projet

```bash
mkdir <ceo-name>-agent
cd <ceo-name>-agent
# Copier les modules génériques depuis nebula-prospector :
cp -r ../nebula-prospector/core ./core
cp -r ../nebula-prospector/db ./db
cp -r ../nebula-prospector/alerts ./alerts
cp ../nebula-prospector/config.py ./config.py
cp ../nebula-prospector/Procfile ../nebula-prospector/railway.json ./
cp ../nebula-prospector/requirements.txt ./
```

Renomme les tables `nova_*` selon le nouveau CEO. Adapte `config.py` (settings).

### Étape 4 — Workers spécifiques au domaine

Crée 1 fichier par worker :
- `sourcing/<channel>.py` (1 par source de données)
- `enrichment/<scoring>.py` (logique de qualification)
- `messaging/<channel>.py` (canal de contact)
- `learning/<learner>.py` (apprentissage hebdo, optionnel V2)

**Chaque worker doit** :
- Exposer une fonction `run_*_pipeline(...)` réutilisable
- Décorer ses appels LLM/API avec `@tool_call(...)`
- Logger via `core/events.py` pour le dashboard
- Renvoyer un dict de stats

### Étape 5 — Enregistre les handlers de tâches

Dans `core/tasks.py`, ajoute :
```python
@register_handler("sourcing.run")
def _h_sourcing(payload):
    from main import run_sourcing_pipeline
    return run_sourcing_pipeline(**payload)
```

### Étape 6 — Scheduler + endpoints admin

Reprends `dashboard/server.py` de NOVA. Ajoute les jobs APScheduler :
- 1 cron daily pour le pipeline principal
- 1 cron pour le briefing humain
- 1 interval 10 min pour drain de la task queue

### Étape 7 — Mission initiale + documents seed

Insert dans `<ceo>_mission` la v1 de la mission.
Insert dans `<ceo>_documents` au moins 3 docs : catalog, ICP, clients/refs.

### Étape 8 — Telegram bot + briefing matinal

Reprends `alerts/telegram_bot.py` + `alerts/morning_briefing.py`. Adapte le format du briefing au domaine du CEO (KPIs différents selon métier).

### Étape 9 — Déploiement Railway

```bash
git init && git add . && git commit -m "feat: scaffold <ceo> agent"
# Connect à Railway via CLI (railway init / railway link)
# Push variables d'env via railway variables --set
# railway up ou git push (deploy from GitHub)
```

### Étape 10 — Smoke test

```bash
curl -X POST https://<ceo>.up.railway.app/api/admin/tasks \
  -H "X-Admin-Token: <token>" \
  -d '{"type":"sourcing.run","priority":7,"reason":"smoke test"}'

# Drain
curl -X POST .../api/admin/tasks/drain -H "X-Admin-Token: <token>"

# Vérifier les logs
railway logs --deployment --lines 50
```

## CHECKLIST DE LIVRAISON

Avant de dire "le CEO est prêt" :

- [ ] Mission v1 active dans `<ceo>_mission`
- [ ] Au moins 3 documents seed
- [ ] Tous les outils LLM/API ont un `@tool_call(...)` avec rate limits
- [ ] Téléphone Telegram du propriétaire dans `.env` (notifications)
- [ ] Endpoints admin protégés par `ADMIN_TOKEN`
- [ ] Scheduler actif (au moins 1 cron + 1 task drain)
- [ ] `/api/health` retourne 200
- [ ] Migration Supabase appliquée
- [ ] Variables d'env Railway poussées (sans CB requise pour les services)
- [ ] Email envoyé à l'humain "Je suis en ligne, voici ma mission v1"
- [ ] Pas de secret commité dans git (`.env` dans `.gitignore`)

## ÉVOLUTION (V2+)

Quand le CEO tourne depuis 1-2 semaines, propose à l'utilisateur :

1. **Mission auto-éditable par le CEO** : function calling Claude → tâche `mission.update`
2. **Apprentissage hebdo** : tâche `learn.weekly` qui re-lit les 100 dernières interactions et écrit un document
3. **Multi-tenant (conglomerate)** : table `clients`, 1 instance CEO par client, pool credits central
4. **Function calling vrai** : remplacer la queue par des tool_use Claude directs
5. **Workflows YAML** : playbooks versionnés en git, le CEO les exécute

## INVARIANTS CULTURELS

Quand tu construis un CEO :

- **Simple > clever** : 4 tables, 4 modules core, ça suffit pour V1
- **Audit-first** : tout log dans `tool_calls` et `agent_events`, sinon impossible de debug
- **Idempotent** : un retry doit donner le même résultat
- **Pas de magie** : pas de "comprends ce que je veux" — toujours un schema explicite
- **L'humain reste maître** : pour toute décision > seuil (budget, action externe risquée), notifier et attendre OK

## RÉFÉRENCE CODE

Le projet de référence vivant et fonctionnel : `nebula-prospector/` (NOVA). Toute question d'implémentation peut être répondue en lisant ses fichiers. Ne ré-invente pas — adapte.

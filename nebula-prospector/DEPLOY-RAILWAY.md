# Déploiement Railway — NOVA + Dashboard

Railway héberge l'agent Python + le dashboard FastAPI. Tout est déjà
configuré, il reste juste à connecter le repo et coller tes clés.

## Étape 1 — Préparer Supabase (3 min)

1. Ouvre [supabase.com](https://supabase.com) → ton projet existant
2. **SQL Editor → New query** → colle `db/schema.sql` → **Run**
3. **SQL Editor → New query** → colle `db/schema_v2_dashboard.sql` → **Run**
4. **Database → Replication** → coche les cases pour `agent_events` et `agent_state`
5. **Settings → API** → récupère :
   - `URL` (déjà dans ton `.env` local)
   - `service_role` secret key
   - `anon` public key

## Étape 2 — Obtenir Google Maps API key (5 min)

1. [console.cloud.google.com](https://console.cloud.google.com) → New Project (ex: "nebula-prospector")
2. **APIs & Services → Library** → active **"Places API (New)"** + **"Geocoding API"**
3. **APIs & Services → Credentials → Create Credentials → API key**
4. **Restrict key** → API restrictions : sélectionne les 2 APIs ci-dessus
5. Active la facturation (carte demandée mais 200 $/mois de crédit gratuit = ~12 000 requêtes)

## Étape 3 — Déployer sur Railway (10 min)

### 3.1 Créer le projet

1. Va sur [railway.app](https://railway.app) → **Login with GitHub**
2. **New Project** → **Deploy from GitHub repo** → choisis `allonebiao2/nebula-agency`
3. Railway commence le build automatiquement (il détecte Python via `requirements.txt`)

### 3.2 Configurer le Root Directory

⚠️ **Important** : notre projet est dans `nebula-prospector/`, pas à la racine du repo.

- Dans Railway → **Settings → Service → Root Directory** → mets `nebula-prospector`
- Sauvegarde, Railway va re-builder

### 3.3 Variables d'environnement

Dans **Variables** de ton service Railway, colle ces variables (one par ligne) :

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
SUPABASE_ANON_KEY=eyJhbGc...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_MAPS_API_KEY=AIza...
ENV=production
LOG_LEVEL=INFO
TARGET_COUNTRIES=BJ,TG,CI,SN,BF
TARGET_CITIES=Cotonou,Lomé,Abidjan,Dakar,Ouagadougou,Porto-Novo,Parakou
MAX_EMAILS_PER_DAY=25
CLAUDE_MODEL_FAST=claude-sonnet-4-6
CLAUDE_MODEL_DEEP=claude-opus-4-7
```

Tu pourras ajouter Resend / Hunter / Telegram plus tard (vagues 2-5).

### 3.4 Exposer le dashboard

Dans **Settings → Networking → Generate Domain** → Railway te donne une URL
publique du genre `nebula-prospector-production.up.railway.app`.

C'est ton dashboard NOVA, accessible depuis n'importe où.

### 3.5 Tester

- Visite `https://<ton-url>/api/health` → tu dois voir `{"ok": true}`
- Visite `https://<ton-url>/` → tu vois NOVA (orbe + interface cosmique)

## Étape 4 — Cron quotidien pour le sourcing

Le dashboard tourne en permanence (service web). Mais le **sourcing**
doit s'exécuter périodiquement, pas en continu.

Dans Railway → ton projet → **+ New → Empty Service** :

1. **Name** : `nova-sourcing-daily`
2. **Settings → Source** : connecte au même repo `nebula-agency`
3. **Root Directory** : `nebula-prospector`
4. **Settings → Deploy → Custom Start Command** : `python main.py sourcing`
5. **Settings → Cron Schedule** : `0 3 * * *` (= tous les jours à 3h UTC = 4h Cotonou)
6. **Variables** : Railway te propose de "Reference" celles du service principal → fais-le pour ne pas tout recopier

Railway exécutera ton sourcing chaque nuit, écrira en base, et NOVA s'animera dans le dashboard.

## Étape 5 — Coûts

Railway facture à l'usage avec un crédit gratuit de **5 $/mois**.

Estimation pour NEBULA Prospector :
- Dashboard FastAPI : ~3-4 $/mois (toujours up, petit trafic)
- Cron sourcing : ~0,50 $/mois (1h d'exécution/jour)
- **Total : ~4 $/mois** → couvert par le crédit gratuit

Si tu dépasses → plan **Hobby à 5 $/mois flat** suffit largement.

## Étape 6 — Custom domain (optionnel)

Pour avoir `nova.nebula-agency.com` au lieu de l'URL Railway :

1. Railway → **Settings → Networking → Custom Domain** → ajoute `nova.nebula-agency.com`
2. Railway te donne un CNAME à pointer
3. Dans ton DNS (chez ton registrar) → ajoute le CNAME

## Troubleshooting

**Build échoue avec "Could not find requirements.txt"**
→ Tu as oublié de mettre Root Directory = `nebula-prospector`

**Dashboard affiche "Erreur Supabase"**
→ Vérifie que `SUPABASE_URL` + `SUPABASE_ANON_KEY` sont bien dans Variables

**L'orbe ne bouge jamais**
→ Realtime pas activé : retourne dans Supabase → Database → Replication → coche `agent_events` et `agent_state`

**"Application failed to respond"**
→ Le port doit être `$PORT`, pas un port codé en dur. Vérifie le Procfile.

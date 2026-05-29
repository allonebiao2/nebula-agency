# Base de données — Supabase

## Initialisation

1. Crée un nouveau projet sur [supabase.com](https://supabase.com)
2. Récupère `Project URL` et `service_role key` dans **Settings → API**, mets-les dans `.env`
3. Ouvre **SQL Editor → New query**, colle le contenu de `schema.sql`, **Run**

## Tables

| Table | Rôle |
|---|---|
| `prospects` | Une ligne = une entreprise/contact trouvé. Pipeline `new → enriched → scored → contacted → replied → engaged → ready_to_pay → won/lost` |
| `conversations` | Chaque email envoyé/reçu. Lié à un prospect. Analyse Claude (intent, sentiment) |
| `prompts_versions` | Tous les prompts système versionnés. L'auto-amélioration insère une nouvelle version chaque semaine |
| `alerts` | Alertes envoyées à Mongazi (Telegram principalement) |
| `sourcing_runs` | Trace de chaque run de sourcing pour debugging + quota tracking |

## Vérification post-install

```sql
select table_name
from information_schema.tables
where table_schema = 'public'
order by table_name;
```

Tu dois voir : `alerts`, `conversations`, `prompts_versions`, `prospects`, `sourcing_runs`.

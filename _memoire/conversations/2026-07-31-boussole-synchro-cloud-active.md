# 2026-07-31 — Boussole : synchro cloud activée + sécurité Supabase

## Contexte
Revue « qu'est-ce qui reste à faire ». Deux « à faire » Supabase identifiés pour Boussole (proto « verre de nuit » désormais en prod) : (1) exécuter `etat.sql` pour activer la synchro cloud, (2) sécurité = le mot de passe DB `QEPXHuSbmPmHr4rj` avait circulé en chat.

## Fait (par Mongazi, dashboard Supabase — projet `xukduhqqfzogisoimhyo`)
1. **`boussole/_proto/etat.sql` exécuté** dans le SQL Editor → table `public.boussole_proto_etat` (`user_id` PK → `auth.users`, `etat` jsonb, `updated_at`) + RLS + 3 policies (select/insert/update scoping `auth.uid() = user_id`).
2. **Mot de passe DB reset** (Settings → Database → Reset password). `QEPXHuSbmPmHr4rj` révoqué.

## Vérification (sans accès Supabase : MCP déconnecté, aucun identifiant DB en local)
Faite via l'**API REST PostgREST + la clé anon publique** (extraite de `config.js`, publique par design) :
- `GET /rest/v1/boussole_proto_etat?select=user_id&limit=1` → **`200` + `[]`** = table existe ET RLS active (l'anonyme ne voit aucune ligne). Contrôle : table inexistante → `404 / PGRST205 "Could not find the table"`.
- La clé anon répond toujours `200` → **elle n'a PAS été régénérée** = l'app live n'est pas cassée. ✅
- Le reset du mot de passe DB **n'est pas vérifiable de l'extérieur** (réglage de compte) → pris sur parole de Mongazi.

## Point important (corrigé au passage)
La clé **« anon » Supabase est PUBLIQUE par design** (embarquée dans tout client, sécurité assurée par la RLS). Le secret qui avait réellement fuité = le **mot de passe DB** (accès Postgres direct). → On reset le mdp DB (fait), on **ne touche PAS** à la clé anon (la régénérer casserait Boussole pour zéro bénéfice). Le reset du mdp DB ne casse pas Boussole (l'app utilise la clé anon via REST, pas le mdp Postgres).

## Reste
- Poser la **Site URL Supabase de prod** (redirect OAuth Google pour la connexion en prod, cf [[project-boussole-refonte]]).
- (Sans rapport Supabase) migration Railway → VPS du Partenaires, toujours en attente de l'accès VPS.

-- NEBULA SUIVI · l'espace où Mongazi suit tout ce que je fais, depuis son téléphone, avec des notifications.
-- Projet Supabase partagé. Lecture réservée à Mongazi (RLS sur ses deux e-mails, comme TES Alertes) ; le PC écrit par
-- DATABASE_URL. ⛔ Ce fichier ne contient aucune donnée : les fiches de prospects vivent dans ces tables, pas dans le dépôt.

-- le journal : chaque action, chaque travail fini (avec son lien), chaque alerte, chaque point
create table if not exists public.nebula_suivi_journal (
  id bigserial primary key,
  quand timestamptz not null default now(),
  genre text not null default 'action' check (genre in ('action', 'lien', 'alerte', 'besoin', 'point', 'vente')),
  titre text not null,
  texte text,
  lien text,
  fait boolean not null default false          -- pour « besoin » : Mongazi l'a traité
);
-- le portefeuille : une photographie des prospects, refaite par le PC (scripts/suivi.py pipeline)
create table if not exists public.nebula_suivi_prospects (
  id text primary key,
  nom text, metier text, telephone text, statut text, score int,
  dernier text,                                 -- le dernier échange, en une ligne
  prochaine text,                               -- la prochaine action et sa date
  montant int,                                  -- ce qu'on lui a proposé, en F
  maj timestamptz not null default now()
);
-- les messages prêts à partir, que Mongazi peut envoyer d'un toucher si Chrome est coupé
create table if not exists public.nebula_suivi_envois (
  id bigserial primary key,
  quand timestamptz not null default now(),
  pour text not null, telephone text not null, message text not null,
  heure text,                                   -- « 9 h 30 », « après 10 h 30 »
  envoye boolean not null default false
);
-- les chiffres du jour (encaissé, contactés, réponses…), écrits par le PC
create table if not exists public.nebula_suivi_chiffres (
  jour date primary key,
  encaisse int not null default 0, objectif int not null default 1000000,
  contactes int, reponses int, interesses int, payes int,
  maj timestamptz not null default now()
);
-- les appareils abonnés aux notifications
create table if not exists public.nebula_suivi_abonnements (
  endpoint text primary key, email text not null, p256dh text not null, auth text not null, appareil text,
  cree timestamptz not null default now()
);

do $$ declare t text; begin
  foreach t in array array['nebula_suivi_journal','nebula_suivi_prospects','nebula_suivi_envois','nebula_suivi_chiffres','nebula_suivi_abonnements'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('drop policy if exists "Mongazi seul" on public.%I', t);
    execute format($p$create policy "Mongazi seul" on public.%I for all to authenticated
      using ((auth.jwt() ->> 'email') in ('allonebiao@gmail.com', 'allonebiao2@gmail.com'))
      with check ((auth.jwt() ->> 'email') in ('allonebiao@gmail.com', 'allonebiao2@gmail.com'))$p$, t);
  end loop;
end $$;
grant select on public.nebula_suivi_journal, public.nebula_suivi_prospects, public.nebula_suivi_chiffres to authenticated;
grant select, update on public.nebula_suivi_envois to authenticated;
grant update (fait) on public.nebula_suivi_journal to authenticated;
grant select, insert, update, delete on public.nebula_suivi_abonnements to authenticated;
grant usage, select on sequence public.nebula_suivi_journal_id_seq, public.nebula_suivi_envois_id_seq to authenticated;

-- LE CARNET (2026-11-25) : une ligne par événement avec un prospect ou un client.
-- Le schéma complet (table, RLS, droits) est écrit et appliqué par suivi/carnet.py (constante SCHEMA, commande « remplir »).

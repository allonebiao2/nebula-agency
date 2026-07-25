-- Boussole proto — synchronisation cloud de l'état complet (mobile <-> PC)
-- À exécuter UNE FOIS dans Supabase : SQL Editor -> coller -> Run.
-- Chaque utilisateur ne voit et ne modifie QUE sa propre ligne (RLS).

create table if not exists public.boussole_proto_etat (
  user_id uuid primary key references auth.users (id) on delete cascade,
  etat jsonb not null,
  updated_at timestamptz not null default now()
);

alter table public.boussole_proto_etat enable row level security;

drop policy if exists "proto_etat_select" on public.boussole_proto_etat;
create policy "proto_etat_select" on public.boussole_proto_etat
  for select using (auth.uid() = user_id);

drop policy if exists "proto_etat_insert" on public.boussole_proto_etat;
create policy "proto_etat_insert" on public.boussole_proto_etat
  for insert with check (auth.uid() = user_id);

drop policy if exists "proto_etat_update" on public.boussole_proto_etat;
create policy "proto_etat_update" on public.boussole_proto_etat
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

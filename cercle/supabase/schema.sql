-- ============================================================
-- CERCLE — Schéma Supabase (MVP — vague 1)
-- Sécurité familiale CONSENTIE (modèle Life360).
-- Règle de confidentialité absolue :
--   On ne voit la position d'une personne QUE si on partage
--   au moins un cercle avec elle. Le consentement = le fait
--   d'avoir rejoint le même cercle. JAMAIS de pistage caché.
-- ============================================================

create extension if not exists "pgcrypto";

-- ---------- TABLES ----------

create table if not exists public.profiles (
  id           uuid primary key references auth.users(id) on delete cascade,
  phone        text unique,            -- optionnel (auth = email)
  display_name text not null,
  created_at   timestamptz not null default now()
);

-- Profil créé automatiquement à l'inscription (depuis les métadonnées auth).
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, display_name, phone)
  values (
    new.id,
    coalesce(nullif(new.raw_user_meta_data->>'display_name',''), split_part(new.email,'@',1)),
    nullif(new.raw_user_meta_data->>'phone','')
  )
  on conflict (id) do nothing;
  return new;
end; $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

create table if not exists public.circles (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  owner       uuid not null references public.profiles(id) on delete cascade,
  invite_code text unique not null,
  created_at  timestamptz not null default now()
);

create table if not exists public.circle_members (
  circle_id uuid not null references public.circles(id) on delete cascade,
  user_id   uuid not null references public.profiles(id) on delete cascade,
  role      text not null default 'member',
  joined_at timestamptz not null default now(),
  primary key (circle_id, user_id)
);

-- Une seule ligne de position "actuelle" par utilisateur (upsert).
create table if not exists public.locations (
  user_id    uuid primary key references public.profiles(id) on delete cascade,
  lat        double precision not null,
  lng        double precision not null,
  accuracy   double precision,
  battery    int,
  updated_at timestamptz not null default now()
);

-- ---------- HELPERS (SECURITY DEFINER => pas de récursion RLS) ----------

create or replace function public.shares_circle(other uuid)
returns boolean language sql security definer set search_path = public stable as $$
  select exists (
    select 1
    from circle_members me
    join circle_members them on them.circle_id = me.circle_id
    where me.user_id = auth.uid() and them.user_id = other
  );
$$;

create or replace function public.is_member(cid uuid)
returns boolean language sql security definer set search_path = public stable as $$
  select exists (
    select 1 from circle_members where circle_id = cid and user_id = auth.uid()
  );
$$;

-- ---------- RLS ----------

alter table public.profiles       enable row level security;
alter table public.circles        enable row level security;
alter table public.circle_members enable row level security;
alter table public.locations      enable row level security;

-- profiles : je me lis, et je lis les membres de mes cercles
drop policy if exists "profiles_select" on public.profiles;
create policy "profiles_select" on public.profiles for select
  using (id = auth.uid() or shares_circle(id));
drop policy if exists "profiles_insert" on public.profiles;
create policy "profiles_insert" on public.profiles for insert
  with check (id = auth.uid());
drop policy if exists "profiles_update" on public.profiles;
create policy "profiles_update" on public.profiles for update
  using (id = auth.uid());

-- circles : lisibles par leurs membres ; modifiables par le propriétaire
drop policy if exists "circles_select" on public.circles;
create policy "circles_select" on public.circles for select using (is_member(id));
drop policy if exists "circles_update" on public.circles;
create policy "circles_update" on public.circles for update using (owner = auth.uid());

-- circle_members : je vois la composition de mes cercles
-- (insertion/jointure gérées par les RPC SECURITY DEFINER ci-dessous)
drop policy if exists "members_select" on public.circle_members;
create policy "members_select" on public.circle_members for select
  using (is_member(circle_id));

-- locations : j'écris la mienne ; je lis celle des membres de mes cercles
drop policy if exists "loc_insert" on public.locations;
create policy "loc_insert" on public.locations for insert with check (user_id = auth.uid());
drop policy if exists "loc_update" on public.locations;
create policy "loc_update" on public.locations for update using (user_id = auth.uid());
drop policy if exists "loc_select" on public.locations;
create policy "loc_select" on public.locations for select
  using (user_id = auth.uid() or shares_circle(user_id));

-- ---------- RPC ----------

create or replace function public.create_circle(p_name text)
returns public.circles language plpgsql security definer set search_path = public as $$
declare c public.circles;
begin
  insert into circles(name, owner, invite_code)
  values (p_name, auth.uid(), upper(substr(encode(gen_random_bytes(4),'hex'),1,6)))
  returning * into c;
  insert into circle_members(circle_id, user_id, role) values (c.id, auth.uid(), 'owner');
  return c;
end; $$;

create or replace function public.join_circle(p_code text)
returns public.circles language plpgsql security definer set search_path = public as $$
declare c public.circles;
begin
  select * into c from circles where invite_code = upper(p_code);
  if c.id is null then raise exception 'Code invalide'; end if;
  insert into circle_members(circle_id, user_id) values (c.id, auth.uid())
    on conflict do nothing;
  return c;
end; $$;

-- Suppression de compte (exigée par les stores). Cascade -> profil, cercles, positions.
create or replace function public.delete_my_account()
returns void language plpgsql security definer set search_path = public, auth as $$
begin
  delete from auth.users where id = auth.uid();
end; $$;

-- ---------- REALTIME ----------
-- Diffusion en direct des positions (RLS appliquée : chacun ne reçoit
-- que les lignes qu'il a le droit de lire).
alter publication supabase_realtime add table public.locations;

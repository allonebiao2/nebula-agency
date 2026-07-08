-- ============================================================
--  Boussole — schéma Supabase (à coller dans SQL Editor)
--  Sécurité : Row-Level Security -> chaque commerçant ne voit
--  QUE ses propres données. La clé anon publique est donc sûre.
-- ============================================================

-- ---------- Tables ----------
create table if not exists public.profils (
  user_id           uuid primary key references auth.users on delete cascade,
  nom_activite      text default '',
  devise            text default 'F',
  objectif_benefice numeric default 0,
  solde_initial     numeric default 0,
  updated_at        timestamptz default now()
);
-- au cas où la table existe déjà d'une version antérieure :
alter table public.profils add column if not exists objectif_benefice numeric default 0;
alter table public.profils add column if not exists solde_initial numeric default 0;

create table if not exists public.produits (
  id          uuid primary key,
  user_id     uuid not null references auth.users on delete cascade,
  nom         text not null,
  modele      text not null default 'transformation',   -- 'transformation' | 'revente'
  prix_vente  numeric not null default 0,
  couts       jsonb   not null default '[]'::jsonb,      -- [{id,libelle,montant}]
  archive     boolean not null default false,
  created_at  timestamptz default now()
);

create table if not exists public.charges_fixes (
  id          uuid primary key,
  user_id     uuid not null references auth.users on delete cascade,
  libelle     text not null,
  montant     numeric not null default 0,                -- montant mensuel
  created_at  timestamptz default now()
);

create table if not exists public.ventes (
  id            uuid primary key,
  user_id       uuid not null references auth.users on delete cascade,
  produit_id    uuid not null,
  qte           numeric not null default 1,
  prix_unitaire numeric not null default 0,
  cout_unitaire numeric not null default 0,               -- coût de revient figé à la vente
  date          timestamptz not null default now(),
  created_at    timestamptz default now()
);

create index if not exists ventes_user_date_idx on public.ventes (user_id, date);

create table if not exists public.depenses (
  id          uuid primary key,
  user_id     uuid not null references auth.users on delete cascade,
  libelle     text default '',
  categorie   text not null default 'Divers',
  montant     numeric not null default 0,
  date        timestamptz not null default now(),
  created_at  timestamptz default now()
);
create index if not exists depenses_user_date_idx on public.depenses (user_id, date);

-- ---------- Row-Level Security ----------
alter table public.profils       enable row level security;
alter table public.produits      enable row level security;
alter table public.charges_fixes enable row level security;
alter table public.ventes        enable row level security;
alter table public.depenses      enable row level security;

-- Politiques : l'utilisateur ne touche que ses lignes.
do $$
declare t text;
begin
  foreach t in array array['profils','produits','charges_fixes','ventes','depenses'] loop
    execute format('drop policy if exists p_sel on public.%I;', t);
    execute format('drop policy if exists p_ins on public.%I;', t);
    execute format('drop policy if exists p_upd on public.%I;', t);
    execute format('drop policy if exists p_del on public.%I;', t);
    execute format('create policy p_sel on public.%I for select using (auth.uid() = user_id);', t);
    execute format('create policy p_ins on public.%I for insert with check (auth.uid() = user_id);', t);
    execute format('create policy p_upd on public.%I for update using (auth.uid() = user_id) with check (auth.uid() = user_id);', t);
    execute format('create policy p_del on public.%I for delete using (auth.uid() = user_id);', t);
  end loop;
end $$;

-- ---------- Synchro temps réel (mobile <-> PC) ----------
-- idempotent : ignore l'erreur si la table est déjà publiée (ré-exécution sûre)
do $$
declare t text;
begin
  foreach t in array array['profils','produits','charges_fixes','ventes','depenses'] loop
    begin
      execute format('alter publication supabase_realtime add table public.%I;', t);
    exception when duplicate_object then null;
    end;
  end loop;
end $$;

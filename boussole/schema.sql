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
-- identité fiscale (imprimée sur les factures / devis) :
alter table public.profils add column if not exists ifu       text default '';
alter table public.profils add column if not exists rccm      text default '';
alter table public.profils add column if not exists adresse   text default '';
alter table public.profils add column if not exists tel_pro   text default '';
alter table public.profils add column if not exists email_pro text default '';
alter table public.profils add column if not exists vendeurs  jsonb default '[]'::jsonb;   -- liste de noms de vendeurs
alter table public.profils add column if not exists wa_templates jsonb default '{}'::jsonb; -- textes WhatsApp personnalisés
alter table public.profils add column if not exists proprietaire text default '';          -- nom du propriétaire
alter table public.profils add column if not exists equipe    jsonb default '[]'::jsonb;   -- équipe {nom,role,actif,pin} (droits vendeurs)
alter table public.profils add column if not exists licence   jsonb default '{}'::jsonb;   -- abonnement {plan,statut,echeance,cle,essai_debut}

-- ============================================================
--  LICENCES — clés à USAGE UNIQUE (validation en ligne) + demandes de paiement
-- ============================================================
create table if not exists public.licence_keys (
  cle        text primary key,
  plan       text not null default 'essentiel',
  statut     text not null default 'dispo',   -- 'dispo' | 'used'
  used_by    uuid,
  used_nom   text,
  used_at    timestamptz,
  created_at timestamptz default now()
);
alter table public.licence_keys enable row level security;

create table if not exists public.licence_requests (
  id         uuid primary key default gen_random_uuid(),
  plan       text,
  montant    integer,
  devise     text default 'F',
  txn        text,          -- id de transaction Mobile Money
  nom        text,          -- nom + prénom du client
  contact    text,
  user_id    uuid,
  statut     text default 'en_attente',   -- en_attente | valide | rejete
  created_at timestamptz default now()
);
alter table public.licence_requests enable row level security;

-- N'importe qui (anon/authenticated) peut DÉPOSER une demande de paiement.
drop policy if exists lr_insert on public.licence_requests;
create policy lr_insert on public.licence_requests for insert to anon, authenticated with check (true);

-- Lecture/gestion réservée aux e-mails admin NEBULA.
drop policy if exists lr_admin on public.licence_requests;
create policy lr_admin on public.licence_requests for all to authenticated
  using ((select email from auth.users where id = auth.uid()) in ('allonebiao@gmail.com', 'allonebiao2@gmail.com'))
  with check ((select email from auth.users where id = auth.uid()) in ('allonebiao@gmail.com', 'allonebiao2@gmail.com'));
drop policy if exists lk_admin on public.licence_keys;
create policy lk_admin on public.licence_keys for all to authenticated
  using ((select email from auth.users where id = auth.uid()) in ('allonebiao@gmail.com', 'allonebiao2@gmail.com'))
  with check ((select email from auth.users where id = auth.uid()) in ('allonebiao@gmail.com', 'allonebiao2@gmail.com'));

-- CONSOMMATION ATOMIQUE d'une clé : une clé ne peut être activée qu'UNE SEULE FOIS.
create or replace function public.consume_licence_key(p_cle text, p_nom text default null)
returns table(plan text)
language plpgsql security definer set search_path = public as $$
declare v_plan text;
begin
  update public.licence_keys
     set statut = 'used', used_by = auth.uid(), used_nom = coalesce(p_nom, used_nom), used_at = now()
   where cle = upper(trim(p_cle)) and statut = 'dispo'
   returning licence_keys.plan into v_plan;
  if v_plan is null then return; end if;   -- clé inexistante OU déjà utilisée
  return query select v_plan;
end $$;
grant execute on function public.consume_licence_key(text, text) to anon, authenticated;

-- GÉNÉRATION d'une clé (réservée aux e-mails admin) -> back-office NEBULA.
create or replace function public.admin_create_licence_key(p_plan text)
returns table(cle text)
language plpgsql security definer set search_path = public as $$
declare v_email text; v_cle text;
begin
  select email into v_email from auth.users where id = auth.uid();
  if v_email is null or v_email not in ('allonebiao@gmail.com', 'allonebiao2@gmail.com') then
    raise exception 'non autorise';
  end if;
  v_cle := 'BSL-' || upper(substr(md5(random()::text), 1, 4)) || '-' || upper(substr(md5(random()::text), 1, 4));
  insert into public.licence_keys(cle, plan) values (v_cle, coalesce(p_plan, 'essentiel'));
  return query select v_cle;
end $$;
grant execute on function public.admin_create_licence_key(text) to authenticated;

create table if not exists public.produits (
  id          uuid primary key,
  user_id     uuid not null references auth.users on delete cascade,
  nom         text not null,
  modele      text not null default 'transformation',   -- 'transformation' | 'revente'
  prix_vente  numeric not null default 0,
  couts       jsonb   not null default '[]'::jsonb,      -- [{id,libelle,montant}]
  stock       numeric,                                    -- null = non suivi
  seuil       numeric not null default 0,                 -- seuil d'alerte stock bas
  archive     boolean not null default false,
  created_at  timestamptz default now()
);
-- stock : ajout si la table existe déjà d'une version antérieure
alter table public.produits add column if not exists stock numeric;
alter table public.produits add column if not exists seuil numeric not null default 0;

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
-- mode de paiement / vendeur / ticket (caisse) :
alter table public.ventes add column if not exists mode    text default 'especes';   -- especes|momo|carte|credit|autre
alter table public.ventes add column if not exists vendeur text default '';
alter table public.ventes add column if not exists ticket  text default '';           -- id partagé pour un encaissement panier

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

create table if not exists public.credits (
  id          uuid primary key,
  user_id     uuid not null references auth.users on delete cascade,
  client      text default '',
  tel         text default '',
  montant     numeric not null default 0,
  paye        boolean not null default false,
  date        timestamptz not null default now(),
  echeance    text default '',
  note        text default '',
  created_at  timestamptz default now()
);
create index if not exists credits_user_idx on public.credits (user_id);
-- paiement partiel : liste de versements [{montant, date}]
alter table public.credits add column if not exists paiements jsonb default '[]'::jsonb;

create table if not exists public.documents (
  id          uuid primary key,
  user_id     uuid not null references auth.users on delete cascade,
  type        text not null default 'facture',            -- 'facture' | 'devis'
  numero      text not null default '',
  date        text not null default '',                   -- 'YYYY-MM-DD'
  echeance    text default '',
  client      jsonb not null default '{}'::jsonb,          -- {nom,tel,adresse}
  lignes      jsonb not null default '[]'::jsonb,          -- [{designation,qte,pu}]
  remise      numeric not null default 0,
  tva_taux    numeric not null default 0,
  acompte     numeric not null default 0,
  notes       text default '',
  statut      text not null default 'impayee',            -- facture: impayee|payee · devis: en_attente|accepte|refuse
  created_at  timestamptz default now()
);
create index if not exists documents_user_idx on public.documents (user_id);

create table if not exists public.objectifs (
  id             uuid primary key,
  user_id        uuid not null references auth.users on delete cascade,
  titre          text not null default '',
  icone          text default 'target',                    -- clé d'icône (target/house/tool/car/school/ring/plane…)
  montant_cible  numeric not null default 0,
  montant_actuel numeric not null default 0,
  echeance       text default '',                          -- 'YYYY-MM-DD'
  note           text default '',
  created_at     timestamptz default now()
);
create index if not exists objectifs_user_idx on public.objectifs (user_id);

create table if not exists public.achats (
  id          uuid primary key,
  user_id     uuid not null references auth.users on delete cascade,
  fournisseur text default '',
  date        text default '',                     -- 'YYYY-MM-DD'
  lignes      jsonb not null default '[]'::jsonb,   -- [{produit_id, qte, cout_unitaire}]
  statut      text not null default 'paye',         -- paye | credit (dette fournisseur)
  note        text default '',
  created_at  timestamptz default now()
);
create index if not exists achats_user_idx on public.achats (user_id);

create table if not exists public.clients (
  id          uuid primary key,
  user_id     uuid not null references auth.users on delete cascade,
  nom         text default '',
  tel         text default '',
  adresse     text default '',
  note        text default '',
  created_at  timestamptz default now()
);
create index if not exists clients_user_idx on public.clients (user_id);

-- ---------- Row-Level Security ----------
alter table public.profils       enable row level security;
alter table public.produits      enable row level security;
alter table public.charges_fixes enable row level security;
alter table public.ventes        enable row level security;
alter table public.depenses      enable row level security;
alter table public.credits       enable row level security;
alter table public.documents     enable row level security;
alter table public.objectifs     enable row level security;
  alter table public.achats        enable row level security;
  alter table public.clients       enable row level security;

-- Politiques : l'utilisateur ne touche que ses lignes.
do $$
declare t text;
begin
  foreach t in array array['profils','produits','charges_fixes','ventes','depenses','credits','documents','objectifs','achats','clients'] loop
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
  foreach t in array array['profils','produits','charges_fixes','ventes','depenses','credits','documents','objectifs','achats','clients'] loop
    begin
      execute format('alter publication supabase_realtime add table public.%I;', t);
    exception when duplicate_object then null;
    end;
  end loop;
end $$;

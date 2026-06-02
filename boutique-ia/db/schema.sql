-- ============================================================
-- Boutique IA — schéma multi-boutiques (étage 1)
-- À exécuter UNE FOIS dans l'éditeur SQL Supabase.
-- Tables préfixées bia_ pour cohabiter avec NOVA dans le même projet.
-- ============================================================

-- 1. Les commerçants (= les "tenants", chaque ligne = une boutique cliente)
create table if not exists bia_merchants (
  id uuid primary key default gen_random_uuid(),

  -- Identité de la boutique
  business_name   text not null,
  sector          text,                 -- bijoux, vêtements, cosmétiques, resto, etc.
  description     text,                  -- ce qu'elle vend, son histoire en 2 lignes
  city            text,
  country         text default 'BJ',

  -- Canaux
  whatsapp_business text not null,       -- numéro où les CLIENTS écrivent
  owner_whatsapp    text,                -- numéro PERSO du patron (pour les alertes)
  owner_email       text,

  -- Encaissement client (Mobile Money manuel)
  momo_number   text,
  momo_name     text,
  momo_network  text,                    -- MTN / Moov / Celtis / Wave

  -- Livraison
  delivery_zones    text,                -- ex: "Cotonou, Calavi, Abomey-Calavi"
  delivery_fee_info text,                -- ex: "Cotonou 1000F, hors ville 2000F"

  -- Personnalité du vendeur IA (étage 2 utilisera ces champs)
  ai_tone        text default 'chaleureux et professionnel',
  languages      text default 'français',
  business_hours text,
  policies       text,                   -- acompte, retours, garanties
  extra_info     text,                   -- FAQ, infos diverses à connaître

  -- Abonnement SaaS
  plan          text default 'starter',
  status        text default 'pending_payment',
                -- pending_payment | paid_pending_validation | active | suspended
  activation_ref text,                   -- référence du paiement MoMo soumise par le commerçant

  created_at    timestamptz default now(),
  activated_at  timestamptz
);

-- 2. Les produits de chaque boutique
create table if not exists bia_products (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  name        text not null,
  price       numeric,
  currency    text default 'XOF',
  description text,
  photo_url   text,
  available   boolean default true,
  kind        text,                  -- 'produit' | 'service'
  duration    text,                  -- durée (pour les services)
  options     text,                  -- variantes : tailles, couleurs, formules…
  created_at  timestamptz default now()
);
create index if not exists bia_products_merchant_idx on bia_products(merchant_id);

-- 3. Les commandes (rempli par l'étage 3 — le cerveau WhatsApp)
create table if not exists bia_orders (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  customer_whatsapp text,
  customer_name     text,
  items             jsonb,               -- [{product, qty, price}]
  total             numeric,
  delivery_mode     text,                -- livraison | retrait
  delivery_address  text,
  status            text default 'pending',
                    -- pending | paid_pending_validation | confirmed | delivered | cancelled
  payment_proof     text,
  created_at        timestamptz default now()
);
create index if not exists bia_orders_merchant_idx on bia_orders(merchant_id);

-- 4. Mémoire des conversations WhatsApp (étage 3)
create table if not exists bia_messages (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  customer_whatsapp text,
  role        text,                      -- customer | assistant
  content     text,
  created_at  timestamptz default now()
);
create index if not exists bia_messages_conv_idx on bia_messages(merchant_id, customer_whatsapp);

-- 5. Routing WhatsApp (étage 2b) — un seul numéro Vendora sert toutes les boutiques
alter table bia_merchants add column if not exists code text;  -- code court par boutique
create unique index if not exists bia_merchants_code_idx on bia_merchants(code);

-- Back-office : couleur de marque du client (accent de SON back-office)
alter table bia_merchants add column if not exists brand_color text;

-- Quelle boutique un client WhatsApp est en train de contacter (mémoire de session)
create table if not exists bia_wa_sessions (
  customer_whatsapp text primary key,
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  updated_at timestamptz default now()
);

-- 6. Ordres donnés par le commerçant à son agent depuis le back-office
--    (langage naturel : "ajoute X", "mets Y en rupture"…). Sert aussi à
--    appliquer le quota d'ordres/jour selon le forfait.
create table if not exists bia_manager_commands (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  command    text,
  reply      text,
  created_at timestamptz default now()
);
create index if not exists bia_manager_cmd_idx on bia_manager_commands(merchant_id, created_at);

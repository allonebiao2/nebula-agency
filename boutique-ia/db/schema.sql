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

-- Sécurité back-office : code d'accès (hash PBKDF2) — étage "piliers"
alter table bia_merchants add column if not exists access_pin text;

-- Conversion : paiement à la livraison + marchandage encadré
alter table bia_merchants add column if not exists cod_enabled boolean default false;
alter table bia_merchants add column if not exists negotiation_enabled boolean default false;
alter table bia_merchants add column if not exists negotiation_rule text;
alter table bia_orders   add column if not exists payment_method text;  -- 'mobile_money' | 'livraison'

-- Réponses entrantes : désinscriptions / opt-out (STOP, unsub, bounce, plainte)
create table if not exists bia_optouts (
  contact    text primary key,   -- email (minuscule) OU numéro WhatsApp
  channel    text,               -- 'email' | 'whatsapp'
  reason     text,               -- stop | unsubscribe | bounce | complaint | manual
  created_at timestamptz default now()
);

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

-- 7. Prospection autonome (étage 5) : campagnes + prospects sourcés/contactés
create table if not exists bia_campaigns (
  id uuid primary key default gen_random_uuid(),
  owner_type  text not null default 'merchant',  -- 'merchant' | 'admin'
  merchant_id uuid references bia_merchants(id) on delete cascade,
  mode        text not null default 'client',     -- 'client' | 'recrutement'
  title text, category text, city text,
  status text default 'sourcing',                 -- sourcing|ready|sending|done|failed
  found int default 0, emailable int default 0, sent int default 0, failed int default 0,
  subject text, body text,
  created_at timestamptz default now()
);
create index if not exists bia_campaigns_owner_idx on bia_campaigns(owner_type, merchant_id, created_at);

create table if not exists bia_prospects (
  id uuid primary key default gen_random_uuid(),
  campaign_id uuid not null references bia_campaigns(id) on delete cascade,
  merchant_id uuid references bia_merchants(id) on delete cascade,
  owner_type text not null default 'merchant',
  name text, sector text, city text, country text, website text, email text, phone text,
  source_external_id text,
  status text default 'new',                       -- new|sent|failed|skipped|blacklisted
  error text, sent_at timestamptz,
  created_at timestamptz default now()
);
create index if not exists bia_prospects_campaign_idx on bia_prospects(campaign_id);
create index if not exists bia_prospects_email_idx on bia_prospects(owner_type, merchant_id, email);

-- 8. Cerveau d'apprentissage (auto-amélioration) : leçons de vente extraites
--    automatiquement des conversations (conclues vs perdues) et RÉINJECTÉES dans
--    le prompt des agents. scope='global' = intelligence collective (toutes les
--    boutiques) ; scope='merchant' + merchant_id = leçons propres à une boutique.
create table if not exists bia_lessons (
  id uuid primary key default gen_random_uuid(),
  scope       text not null default 'global',   -- 'global' | 'merchant'
  merchant_id uuid references bia_merchants(id) on delete cascade,
  lessons     text not null,                     -- synthèse injectée dans le system prompt
  stats       jsonb,                             -- {conversations, won, lost, revenue, ...}
  model       text,                              -- modèle ayant produit la synthèse
  created_at  timestamptz default now()
);
create index if not exists bia_lessons_scope_idx on bia_lessons(scope, merchant_id, created_at desc);

-- 9. Relances automatiques (autonomie) : l'agent recontacte de lui-même les clients
--    silencieux (devis sans réponse) et les paniers abandonnés (commande non payée),
--    dans ses garde-fous. Sert aussi d'anti-doublon (cooldown) + reporting.
create table if not exists bia_followups (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  customer_whatsapp text,
  kind        text,          -- 'silent' (client muet) | 'cart' (panier/commande non payée)
  order_id    uuid,          -- renseigné pour une relance de panier
  message     text,
  sent_at     timestamptz default now()
);
create index if not exists bia_followups_idx on bia_followups(merchant_id, customer_whatsapp, sent_at desc);

-- 10. Cerveau CEO (autonomie stratégique) : le directeur autonome de Vendora
--     analyse le business de lui-même et PROPOSE des décisions (prix, modèle/
--     intelligence, prospection, rétention). Mongazi valide ✓/✗ (le financier
--     reste à son niveau). Journal des décisions = mémoire stratégique.
create table if not exists bia_decisions (
  id uuid primary key default gen_random_uuid(),
  category       text,                       -- prix | modele | prospection | retention | produit | autre
  title          text not null,
  finding        text,                       -- le constat (ce que l'agent a observé)
  recommendation text,                       -- ce qu'il propose de faire
  impact         text,                       -- impact estimé
  level          text default 'validation',  -- 'auto' (réversible) | 'validation' (Mongazi)
  financial      boolean default false,      -- touche à l'argent → toujours Mongazi
  status         text default 'proposed',    -- proposed | approved | rejected | done
  created_at     timestamptz default now(),
  decided_at     timestamptz
);
create index if not exists bia_decisions_status_idx on bia_decisions(status, created_at desc);
-- Action exécutable (autonomie #2) : si une reco est réversible/interne, l'agent peut
-- l'APPLIQUER tout seul dès que Mongazi la valide (toggles sûrs uniquement).
alter table bia_decisions add column if not exists action text;        -- ex: enable_followups
alter table bia_decisions add column if not exists action_params jsonb; -- ex: {"daily": 20}

-- 11. Auto-expérimentation (le « ML » de Vendora) : l'agent teste des VARIANTES de
--     stratégie de vente (champion vs challenger), mesure laquelle conclut le plus,
--     et GARDE la gagnante. variant_text = bloc de tactiques injecté dans le prompt
--     du vendeur. Assignation STABLE par client (pour attribuer le résultat).
create table if not exists bia_experiments (
  id uuid primary key default gen_random_uuid(),
  name        text,
  hypothesis  text,                 -- l'hypothèse testée (pour Mongazi)
  variant_text text default '',      -- tactiques injectées (vide = approche standard)
  status      text default 'active', -- active | retired | winner
  total       int default 0,         -- conversations attribuées (calculé à l'évaluation)
  won         int default 0,         -- ventes conclues
  created_at  timestamptz default now()
);
create index if not exists bia_experiments_status_idx on bia_experiments(status, created_at desc);

create table if not exists bia_experiment_assignments (
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  customer    text not null,
  variant_id  uuid not null references bia_experiments(id) on delete cascade,
  created_at  timestamptz default now(),
  primary key (merchant_id, customer)
);

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

-- Forfait flexible : changement de forfait programmé (downgrade au renouvellement)
alter table bia_merchants add column if not exists pending_plan text;

-- Conversion : paiement à la livraison + marchandage encadré
alter table bia_merchants add column if not exists cod_enabled boolean default false;
alter table bia_merchants add column if not exists negotiation_enabled boolean default false;
alter table bia_merchants add column if not exists negotiation_rule text;
alter table bia_orders   add column if not exists payment_method text;  -- 'mobile_money' | 'livraison'

-- « Composez votre vendeur » : capacités choisies (ids séparés par virgule, cf.
-- core/capabilities). NULL = jamais réglé → repli sur les anciens interrupteurs.
alter table bia_merchants add column if not exists enabled_capabilities text;

-- Essai gratuit 3 jours : la boutique est active mais NON payante (is_trial=true).
-- À l'échéance (period_end), le cycle de facturation la suspend (jamais supprimée).
alter table bia_merchants add column if not exists is_trial boolean default false;
-- Win-back : date du dernier message de reconquête envoyé à une boutique suspendue.
alter table bia_merchants add column if not exists winback_at timestamptz;

-- Coach commercial : dernier conseil hebdo généré pour la boutique (+ snapshot).
create table if not exists bia_coaching (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  advice text,
  snapshot text,                  -- JSON des chiffres au moment du conseil
  created_at timestamptz default now()
);
create index if not exists bia_coaching_idx on bia_coaching(merchant_id, created_at);

-- Vendora Social (Phase 2) : brouillons de posts réseaux sociaux générés par l'agent.
create table if not exists bia_social_posts (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  posts text,                     -- JSON : liste de posts (jour/type/legende/hashtags/idee_visuelle)
  created_at timestamptz default now()
);
create index if not exists bia_social_posts_idx on bia_social_posts(merchant_id, created_at);

-- Prise de rendez-vous (capacité « rdv ») : disponibilités de la boutique.
alter table bia_merchants add column if not exists rdv_days text;   -- (ancien, texte libre)
alter table bia_merchants add column if not exists rdv_hours text;  -- ex : "09:00-17:00"
alter table bia_merchants add column if not exists rdv_note text;   -- ex : "Sur place, clinique"
-- Agenda visuel : disponibilités structurées + créneau fixé par RDV.
alter table bia_merchants add column if not exists rdv_weekdays text;  -- jours ouvrés CSV 1..7 (Lun..Dim)
alter table bia_merchants add column if not exists rdv_off_dates text; -- jours fermés CSV YYYY-MM-DD
alter table bia_appointments add column if not exists scheduled_at timestamptz; -- créneau confirmé

create table if not exists bia_appointments (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  customer_whatsapp text,
  customer_name text,
  service text,
  requested_time text,            -- créneau souhaité, tel que dit par le client
  note text,
  status text default 'pending',  -- pending | confirmed | cancelled
  created_at timestamptz default now()
);
create index if not exists bia_appointments_idx on bia_appointments(merchant_id, created_at);

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

-- 12. Boîte email entrante : fil des réponses de PROSPECTION RECRUTEMENT (les
--     réponses au recrutement reviennent dans notre boîte = reply-to ; l'agent y
--     répond pour convertir en boutique). direction 'in' = reçu, 'out' = envoyé.
create table if not exists bia_inbox (
  id uuid primary key default gen_random_uuid(),
  prospect_email text not null,
  merchant_id uuid references bia_merchants(id) on delete cascade,  -- null = recrutement (admin)
  direction text not null,            -- 'in' | 'out'
  status text default 'sent',         -- 'sent' | 'draft' (à valider) | 'rejected'
  subject text, body text,
  message_id text,                    -- Message-ID (dédup des entrants)
  created_at timestamptz default now()
);
create index if not exists bia_inbox_email_idx on bia_inbox(prospect_email, created_at desc);
create index if not exists bia_inbox_msgid_idx on bia_inbox(message_id);
create index if not exists bia_inbox_merchant_idx on bia_inbox(merchant_id, status, created_at desc);
-- Mode de réponse email par boutique : 'review' = l'agent rédige, le commerçant valide ;
-- 'auto' = l'agent envoie directement. (colonne bia_merchants.inbox_mode, défaut 'review')

-- 13. Assistant personnel du/de la propriétaire (Phase B) — mémoire de fil + agenda.
--     SÉPARÉ de bia_messages : ces tours NE polluent JAMAIS les conversations clients
--     ni le cerveau d'apprentissage. Le patron est identifié par owner_whatsapp (verrou).
create table if not exists bia_assistant_chat (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  role       text not null,                 -- 'user' (patron) | 'assistant'
  channel    text default 'whatsapp',       -- 'whatsapp' | 'backoffice'
  content    text,
  created_at timestamptz default now()
);
create index if not exists bia_assistant_chat_idx on bia_assistant_chat(merchant_id, created_at desc);

-- Agenda / rappels du patron (écriture par l'assistant : « note-moi… »). remind_at
-- daté → rappel proactif poussé UNIQUEMENT dans la fenêtre WhatsApp 24h (gratuit/conforme).
create table if not exists bia_agenda (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  title       text not null,
  when_text   text,                          -- tel que dit ("demain 15h", "lundi")
  remind_at   timestamptz,                   -- moment du rappel si déterminable (UTC)
  status      text default 'pending',        -- pending | done | cancelled
  reminded_at timestamptz,                   -- anti-doublon de notification
  created_at  timestamptz default now()
);
create index if not exists bia_agenda_idx on bia_agenda(merchant_id, status, remind_at);

-- 14. Metering : crédits de conversations supplémentaires (recharge prépayée MoMo,
--     persistants). SOFT CAP — ne bride jamais la vente ; sert l'affichage + le
--     nudge recharge/upgrade. Conversations incluses/mois = config.PLAN_CONV_INCLUDED.
alter table bia_merchants add column if not exists conv_credits integer not null default 0;

-- 15. Validation des paiements clients (onglet Validation du back-office). L'agent
--     capture la preuve quand le client dit avoir payé → 'paid_pending_validation' ;
--     le commerçant confirme (→ 'confirmed') ou rejette (→ 'pending').
alter table bia_orders add column if not exists payment_ref text;        -- ID/référence de transaction MoMo
alter table bia_orders add column if not exists payment_network text;    -- MTN / Moov / Celtis / Wave
alter table bia_orders add column if not exists validated_at timestamptz; -- horodatage de la confirmation

-- 16. Notifications « événement » du back-office (leads chauds à rappeler…). Les
--     alertes « état » (paiements à valider, RDV, abo) restent DÉRIVÉES de leurs
--     tables ; ici on stocke les événements transitoires sans table source. L'onglet
--     Notifications les affiche (en plus de Telegram/WhatsApp) ; status done = traité.
create table if not exists bia_notifications (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  type       text not null,             -- 'hot_lead' (extensible)
  title      text,
  body       text,
  customer   text,                      -- contact client (pour rappeler), si pertinent
  status     text default 'unread',     -- unread | done
  created_at timestamptz default now()
);
create index if not exists bia_notifications_idx on bia_notifications(merchant_id, status, created_at desc);

-- 17. Support client IN-APP : fil d'aide commerçant ↔ IA Vendora ↔ NEBULA (Mongazi
--     peut reprendre la main). role merchant|ai|owner ; kind message|problem. Les
--     'problem' alimentent le cerveau support (auto-amélioration, éviter la répétition).
--     Bascule « je gère » + drapeau « à traiter » via bia_settings (support_human_*/support_open_*).
create table if not exists bia_support (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  role       text not null,             -- 'merchant' | 'ai' | 'owner'
  content    text,
  kind       text default 'message',    -- 'message' | 'problem'
  created_at timestamptz default now()
);
create index if not exists bia_support_idx on bia_support(merchant_id, created_at);
create index if not exists bia_support_problem_idx on bia_support(kind, created_at desc);

-- 18. Mini-outils « employé numérique » : caisse, ardoise, stock, documents.
create table if not exists bia_cashbook (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  direction text not null,            -- 'in' (recette) | 'out' (dépense)
  amount numeric not null, label text,
  created_at timestamptz default now()
);
create index if not exists bia_cashbook_idx on bia_cashbook(merchant_id, created_at desc);

create table if not exists bia_debts (   -- ardoise : crédits clients
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  customer_name text, customer_contact text,
  amount numeric not null, reason text,
  status text default 'open',           -- open | paid
  created_at timestamptz default now(), paid_at timestamptz
);
create index if not exists bia_debts_idx on bia_debts(merchant_id, status, created_at desc);

alter table bia_products add column if not exists stock_qty integer;  -- NULL = non suivi

create table if not exists bia_documents (   -- factures / pro formas / devis / reçus
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  doc_type text not null,               -- facture | proforma | devis | recu
  number text, customer_name text, customer_contact text,
  items jsonb, total numeric, note text,
  created_at timestamptz default now()
);
create index if not exists bia_documents_idx on bia_documents(merchant_id, created_at desc);

-- 19. Mini-CRM : fiches clients (note/préférences + anniversaire). La fidélité se
--     dérive des commandes (bia_orders) ; ici ce qui ne s'y trouve pas.
create table if not exists bia_customer_notes (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  contact text, name text, note text,
  birthday text, birthday_md text,      -- 'MM-DD' pour le rappel d'anniversaire
  created_at timestamptz default now(), updated_at timestamptz default now()
);
create index if not exists bia_customer_notes_idx on bia_customer_notes(merchant_id);
create index if not exists bia_customer_notes_bd_idx on bia_customer_notes(birthday_md);

-- 20. Fiche boutique ENRICHIE : l'agent connaît vraiment le business (positionnement,
--     clientèle, arguments, objections, garanties…). Choix multiples + écriture libre.
alter table bia_merchants add column if not exists founded text;
alter table bia_merchants add column if not exists price_range text;
alter table bia_merchants add column if not exists target_audience text;
alter table bia_merchants add column if not exists occasions text;
alter table bia_merchants add column if not exists bestsellers text;
alter table bia_merchants add column if not exists unique_selling text;
alter table bia_merchants add column if not exists selling_points text;
alter table bia_merchants add column if not exists payment_methods text;
alter table bia_merchants add column if not exists guarantees text;
alter table bia_merchants add column if not exists promotions text;
alter table bia_merchants add column if not exists objections text;
alter table bia_merchants add column if not exists avoid_topics text;
alter table bia_merchants add column if not exists presence text;
alter table bia_merchants add column if not exists socials text;

-- Effort/intelligence du modèle choisi par le commerçant (eco | standard | max ; NULL=standard).
alter table bia_merchants add column if not exists ai_effort text;

-- Galerie : plusieurs images par produit (bia_products.photo_url = couverture).
create table if not exists bia_product_images (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid not null references bia_merchants(id) on delete cascade,
  product_id  uuid not null references bia_products(id) on delete cascade,
  url text not null, position int default 0,
  created_at timestamptz default now()
);
create index if not exists bia_product_images_idx on bia_product_images(product_id, position);
create index if not exists bia_product_images_m_idx on bia_product_images(merchant_id);

-- Mesure du COÛT IA (F3) : un enregistrement par appel modèle (tokens + coût estimé).
create table if not exists bia_usage (
  id uuid primary key default gen_random_uuid(),
  merchant_id uuid,
  task text,
  model text,
  input_tokens       int default 0,
  output_tokens      int default 0,
  cache_read_tokens  int default 0,
  cache_write_tokens int default 0,
  cost_usd numeric default 0,
  created_at timestamptz default now()
);
create index if not exists bia_usage_created_idx on bia_usage(created_at);
create index if not exists bia_usage_merchant_idx on bia_usage(merchant_id);

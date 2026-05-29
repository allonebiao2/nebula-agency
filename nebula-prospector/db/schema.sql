-- =============================================================================
-- NEBULA PROSPECTOR — Schéma Supabase
-- =============================================================================
-- Exécuter dans : Supabase Dashboard → SQL Editor → New query
-- =============================================================================

-- Extension pour générer des UUID
create extension if not exists "uuid-ossp";

-- =============================================================================
-- TABLE prospects
-- Un prospect = une entreprise / un décideur trouvé par une source de sourcing.
-- =============================================================================
create table if not exists public.prospects (
    id                  uuid primary key default uuid_generate_v4(),

    -- Identification source
    source              text not null check (source in (
                            'google_maps', 'jiji', 'coinafrique',
                            'pagesjaunes', 'linkedin', 'instagram',
                            'facebook', 'manual'
                        )),
    source_external_id  text,  -- place_id, ad_id, etc. (unique par source)

    -- Données business
    name                text not null,
    sector              text,
    sector_normalized   text,  -- beauty, restaurant, fashion, services, etc.
    country             text,  -- code ISO 2 (BJ, TG, CI...)
    city                text,
    address             text,
    lat                 double precision,
    lng                 double precision,

    -- Contact
    website             text,
    has_website         boolean,
    phone               text,
    email               text,
    facebook_url        text,
    instagram_url       text,
    linkedin_url        text,

    -- Données brutes pour ré-analyse ultérieure
    raw_json            jsonb,

    -- Pipeline
    score               integer default 0,
    status              text not null default 'new' check (status in (
                            'new',              -- vient d'être sourcé
                            'enriched',         -- email trouvé
                            'scored',           -- Claude a scoré
                            'contacted',        -- 1er email envoyé
                            'replied',          -- a répondu
                            'engaged',          -- conversation en cours
                            'ready_to_pay',     -- alerte envoyée à Mongazi
                            'won',              -- client signé
                            'lost',             -- pas intéressé / mauvais fit
                            'blacklisted'       -- ne plus jamais contacter
                        )),
    status_reason       text,

    -- Métadonnées
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now(),
    last_contacted_at   timestamptz,
    next_action_at      timestamptz,

    -- Unicité : pas deux fois le même externe par même source
    constraint prospects_source_uid_unique unique (source, source_external_id)
);

create index if not exists prospects_status_idx on public.prospects (status);
create index if not exists prospects_score_idx on public.prospects (score desc);
create index if not exists prospects_country_idx on public.prospects (country);
create index if not exists prospects_email_idx on public.prospects (email) where email is not null;
create index if not exists prospects_next_action_idx on public.prospects (next_action_at)
    where next_action_at is not null;

-- =============================================================================
-- TABLE conversations
-- Chaque message envoyé/reçu avec un prospect.
-- =============================================================================
create table if not exists public.conversations (
    id              uuid primary key default uuid_generate_v4(),
    prospect_id     uuid not null references public.prospects(id) on delete cascade,

    direction       text not null check (direction in ('outbound', 'inbound')),
    channel         text not null default 'email' check (channel in ('email', 'whatsapp', 'telegram', 'manual')),

    subject         text,
    body            text not null,

    -- Tracking
    message_id      text,                       -- Message-ID email pour threading
    in_reply_to     text,                       -- Reply-To message ID
    provider_id     text,                       -- ID Resend / Twilio
    opened_at       timestamptz,
    clicked_at      timestamptz,

    -- Analyse Claude (pour les inbound surtout)
    detected_intent text,                       -- interested, objection, price_question, ready_to_pay, not_interested, oof
    sentiment       text,                       -- positive, neutral, negative
    summary         text,                       -- résumé Claude pour l'historique

    -- Quel prompt a généré ce message (pour mesurer perf)
    prompt_version_id uuid,

    sent_at         timestamptz not null default now(),
    created_at      timestamptz not null default now()
);

create index if not exists conversations_prospect_idx on public.conversations (prospect_id, sent_at desc);
create index if not exists conversations_intent_idx on public.conversations (detected_intent)
    where detected_intent is not null;
create index if not exists conversations_provider_idx on public.conversations (provider_id)
    where provider_id is not null;

-- =============================================================================
-- TABLE prompts_versions
-- Tous les prompts système versionnés. L'auto-amélioration écrit ici.
-- =============================================================================
create table if not exists public.prompts_versions (
    id                  uuid primary key default uuid_generate_v4(),
    name                text not null,         -- 'first_contact_email', 'reply_handler', 'scorer'
    version             integer not null,
    content             text not null,

    -- Quel modèle a écrit ce prompt (pour audit)
    written_by          text default 'human',  -- 'human' | 'claude-opus-4-7' | etc.
    parent_version_id   uuid references public.prompts_versions(id),

    -- Mesures de performance (alimentées par weekly_review)
    sample_size         integer default 0,
    open_rate           numeric(5,4),
    reply_rate          numeric(5,4),
    positive_reply_rate numeric(5,4),
    conversion_rate     numeric(5,4),

    is_active           boolean not null default false,
    notes               text,

    created_at          timestamptz not null default now(),

    constraint prompts_versions_name_version_unique unique (name, version)
);

create index if not exists prompts_versions_active_idx on public.prompts_versions (name, is_active);

-- =============================================================================
-- TABLE alerts
-- Alertes envoyées à Mongazi (principalement Telegram).
-- =============================================================================
create table if not exists public.alerts (
    id                  uuid primary key default uuid_generate_v4(),
    prospect_id         uuid references public.prospects(id) on delete set null,
    conversation_id     uuid references public.conversations(id) on delete set null,

    type                text not null check (type in (
                            'ready_to_pay',
                            'hot_lead',
                            'objection_human_needed',
                            'sourcing_report',
                            'weekly_report',
                            'error'
                        )),
    severity            text not null default 'info' check (severity in ('info', 'warn', 'critical')),
    payload             jsonb,

    channel             text not null default 'telegram',
    delivered           boolean not null default false,
    provider_message_id text,

    sent_at             timestamptz,
    created_at          timestamptz not null default now()
);

create index if not exists alerts_type_idx on public.alerts (type, created_at desc);
create index if not exists alerts_undelivered_idx on public.alerts (created_at)
    where delivered = false;

-- =============================================================================
-- TABLE sourcing_runs
-- Trace de chaque exécution de sourcing (debugging, quota tracking).
-- =============================================================================
create table if not exists public.sourcing_runs (
    id              uuid primary key default uuid_generate_v4(),
    source          text not null,
    query           text,
    location        text,

    results_count   integer default 0,
    inserted_count  integer default 0,
    updated_count   integer default 0,
    skipped_count   integer default 0,

    status          text not null default 'running' check (status in ('running', 'success', 'failed')),
    error_message   text,

    started_at      timestamptz not null default now(),
    finished_at     timestamptz
);

create index if not exists sourcing_runs_source_idx on public.sourcing_runs (source, started_at desc);

-- =============================================================================
-- TRIGGER : updated_at sur prospects
-- =============================================================================
create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists prospects_touch_updated_at on public.prospects;
create trigger prospects_touch_updated_at
    before update on public.prospects
    for each row execute function public.touch_updated_at();

-- =============================================================================
-- RLS : désactivée — l'agent utilise uniquement la service_role_key
-- =============================================================================
alter table public.prospects        disable row level security;
alter table public.conversations    disable row level security;
alter table public.prompts_versions disable row level security;
alter table public.alerts           disable row level security;
alter table public.sourcing_runs    disable row level security;

-- =============================================================================
-- NEBULA PROSPECTOR — Schéma v2 (Dashboard temps réel + NOVA)
-- =============================================================================
-- À exécuter APRÈS schema.sql, dans Supabase SQL Editor.
-- Ajoute : agent_events, agent_state. Active Supabase Realtime + RLS lecture.
-- =============================================================================

-- =============================================================================
-- TABLE agent_events
-- Flux de "conscience" de NOVA : chaque pensée, action, découverte est loggée.
-- Le dashboard s'abonne à cette table via Supabase Realtime.
-- =============================================================================
create table if not exists public.agent_events (
    id              uuid primary key default uuid_generate_v4(),

    event_type      text not null check (event_type in (
                        'thought',          -- réflexion / décision interne
                        'action',           -- action en cours
                        'discovery',        -- nouveau prospect trouvé
                        'enrichment',       -- email trouvé / data ajoutée
                        'email_sent',       -- email envoyé
                        'reply_received',   -- réponse reçue d'un prospect
                        'intent_detected',  -- classifier a détecté un intent
                        'alert_sent',       -- alerte envoyée à Mongazi
                        'error',            -- erreur
                        'learning',         -- auto-amélioration : nouveau prompt
                        'state_change'      -- changement d'état NOVA
                    )),
    title           text not null,                          -- court (affichage)
    description     text,                                   -- long (détails)
    emoji           text default '✨',                       -- pour le dashboard

    severity        text not null default 'info'
                    check (severity in ('info', 'success', 'warn', 'error', 'celebration')),

    prospect_id     uuid references public.prospects(id) on delete set null,
    conversation_id uuid references public.conversations(id) on delete set null,

    metadata        jsonb,
    created_at      timestamptz not null default now()
);

create index if not exists agent_events_created_idx on public.agent_events (created_at desc);
create index if not exists agent_events_type_idx on public.agent_events (event_type, created_at desc);

-- =============================================================================
-- TABLE agent_state
-- État courant de NOVA. Singleton (1 seule ligne, mise à jour en place).
-- =============================================================================
create table if not exists public.agent_state (
    id                  uuid primary key default uuid_generate_v4(),

    name                text not null default 'NOVA',
    status              text not null default 'idle' check (status in (
                            'idle',         -- au repos
                            'thinking',     -- analyse / décide
                            'sourcing',     -- cherche des prospects
                            'enriching',    -- enrichit (Hunter, scoring)
                            'writing',      -- rédige un email
                            'sending',      -- envoie un email
                            'listening',    -- poll des réponses
                            'learning',     -- auto-amélioration
                            'sleeping',     -- pause nocturne
                            'error'         -- bloquée
                        )),
    mood                text default 'serene' check (mood in (
                            'serene', 'focused', 'excited', 'concerned', 'triumphant'
                        )),
    current_activity    text,             -- "Je scanne 20 boutiques mode à Cotonou..."
    current_target      text,             -- "Atelier Élégance · Cotonou"

    -- Compteurs cumul session courante
    prospects_found_today   integer default 0,
    emails_sent_today       integer default 0,
    replies_today           integer default 0,
    alerts_sent_today       integer default 0,

    version             text default '0.1.0',
    last_heartbeat      timestamptz not null default now(),
    updated_at          timestamptz not null default now()
);

-- Une seule ligne (insérée par bootstrap)
insert into public.agent_state (id)
values ('00000000-0000-0000-0000-000000000001')
on conflict (id) do nothing;

-- =============================================================================
-- TRIGGER : updated_at sur agent_state
-- =============================================================================
drop trigger if exists agent_state_touch on public.agent_state;
create trigger agent_state_touch
    before update on public.agent_state
    for each row execute function public.touch_updated_at();

-- =============================================================================
-- RLS : lecture publique sur agent_events + agent_state UNIQUEMENT
-- Le dashboard utilise l'anon key (côté navigateur) : sécurisée si seules
-- ces 2 tables sont lisibles publiquement.
-- =============================================================================
alter table public.agent_events enable row level security;
alter table public.agent_state  enable row level security;

drop policy if exists "Public read agent_events" on public.agent_events;
create policy "Public read agent_events"
    on public.agent_events for select
    to anon, authenticated
    using (true);

drop policy if exists "Public read agent_state" on public.agent_state;
create policy "Public read agent_state"
    on public.agent_state for select
    to anon, authenticated
    using (true);

-- L'agent écrit avec la service_role_key (bypasse RLS) → pas besoin d'INSERT policy

-- =============================================================================
-- REALTIME : activer le push WebSocket pour ces 2 tables
-- =============================================================================
-- Note : il faut aussi cocher "Realtime" sur ces tables dans le dashboard
-- Supabase → Database → Replication → enable replication on agent_events + agent_state
alter publication supabase_realtime add table public.agent_events;
alter publication supabase_realtime add table public.agent_state;

-- =============================================================================
-- VUE pratique : derniers events avec nom du prospect joint
-- =============================================================================
create or replace view public.v_recent_events as
select
    e.id,
    e.created_at,
    e.event_type,
    e.title,
    e.description,
    e.emoji,
    e.severity,
    e.metadata,
    p.name        as prospect_name,
    p.city        as prospect_city,
    p.sector_normalized as prospect_sector
from public.agent_events e
left join public.prospects p on p.id = e.prospect_id
order by e.created_at desc
limit 200;

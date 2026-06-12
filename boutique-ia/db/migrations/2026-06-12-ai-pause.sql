-- Migration — Pause IA / reprise humaine (§3 robustesse)
-- Appliquée le 2026-06-12 sur Supabase (projet anqdxzcbfuvzqxvgqzbj).
-- Quand une conversation (merchant, client) est en pause, l'agent ne répond plus
-- automatiquement → la patronne reprend la main (répond depuis le back-office).
create table if not exists bia_ai_pause (
  merchant_id       uuid not null references bia_merchants(id) on delete cascade,
  customer_whatsapp text not null,
  paused            boolean not null default true,
  updated_at        timestamptz default now(),
  primary key (merchant_id, customer_whatsapp)
);
alter table public.bia_ai_pause enable row level security;

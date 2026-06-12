-- Migration — Abonnements NEBULA Agency (vitrines / catalogues digitaux)
-- Appliquée le 2026-06-12 sur Supabase (projet anqdxzcbfuvzqxvgqzbj).
-- Facturation trimestrielle (period_months=3) + rappels d'échéance (J-7 + jour J).
-- DISTINCT des forfaits Vendora (bia_merchants). Tarifs : vitrine 15 000 F / catalogue 5 000 F.
create table if not exists nebula_abonnements (
  id              uuid primary key default gen_random_uuid(),
  client_name     text not null,
  offer           text not null default 'vitrine',   -- vitrine | catalogue
  amount          numeric not null default 0,
  client_whatsapp text,
  client_email    text,
  next_due        date not null,
  period_months   int not null default 3,
  status          text not null default 'active',     -- active | cancelled
  notif_pre_sent  boolean not null default false,
  notif_due_sent  boolean not null default false,
  created_at      timestamptz default now()
);
alter table public.nebula_abonnements enable row level security;

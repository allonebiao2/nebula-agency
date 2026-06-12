-- Migration — Conformité APDP / Code du numérique (Bénin)
-- À exécuter UNE FOIS dans l'éditeur SQL Supabase (projet Vendora).
-- Sûr et idempotent (create if not exists). Aucune donnée existante touchée.

-- Consentement marketing (opt-in) du client final, par boutique.
create table if not exists bia_optin (
  merchant_id       uuid not null references bia_merchants(id) on delete cascade,
  customer_whatsapp text not null,
  opted_in          boolean not null default false,
  updated_at        timestamptz default now(),
  primary key (merchant_id, customer_whatsapp)
);

-- Rappel : la suppression (droit à l'effacement) et la rétention 12 mois agissent
-- sur les tables existantes (bia_messages, bia_orders, ...) — pas de table dédiée.

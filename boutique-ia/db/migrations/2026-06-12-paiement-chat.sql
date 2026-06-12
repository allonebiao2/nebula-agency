-- Migration — Paiement en chat (semi-auto MoMo)
-- Appliquée le 2026-06-12 sur Supabase (projet anqdxzcbfuvzqxvgqzbj).
-- Montant ANNONCÉ par le client lors d'un paiement Mobile Money → permet de le
-- rapprocher du total de la commande et de signaler un écart au commerçant.
alter table public.bia_orders add column if not exists payment_amount numeric;

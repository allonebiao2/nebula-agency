-- Migration — Sécurité : activer RLS sur toutes les tables Vendora (bia_*)
-- Appliquée le 2026-06-12 sur Supabase (projet anqdxzcbfuvzqxvgqzbj).
-- Vendora se connecte UNIQUEMENT en service_role (cf. db/client.py), qui CONTOURNE
-- le RLS → aucune régression. Sans policy, anon/authenticated sont refusés par
-- défaut → la base n'est plus exposée via la clé anon.
-- NB : les tables NOVA (nova_*, tool_calls, tasks, chat_history) ne sont PAS
-- incluses (produit séparé, en pause) — à traiter au redémarrage de NOVA.
alter table public.bia_merchants            enable row level security;
alter table public.bia_products            enable row level security;
alter table public.bia_orders              enable row level security;
alter table public.bia_messages            enable row level security;
alter table public.bia_wa_sessions         enable row level security;
alter table public.bia_manager_commands    enable row level security;
alter table public.bia_campaigns           enable row level security;
alter table public.bia_prospects           enable row level security;
alter table public.bia_optouts             enable row level security;
alter table public.bia_settings            enable row level security;
alter table public.bia_lessons             enable row level security;
alter table public.bia_followups           enable row level security;
alter table public.bia_decisions           enable row level security;
alter table public.bia_experiments         enable row level security;
alter table public.bia_experiment_assignments enable row level security;
alter table public.bia_inbox               enable row level security;
alter table public.bia_appointments        enable row level security;
alter table public.bia_social_posts        enable row level security;
alter table public.bia_coaching            enable row level security;
alter table public.bia_assistant_chat      enable row level security;
alter table public.bia_agenda              enable row level security;
alter table public.bia_notifications       enable row level security;
alter table public.bia_support             enable row level security;
alter table public.bia_cashbook            enable row level security;
alter table public.bia_debts               enable row level security;
alter table public.bia_documents           enable row level security;
alter table public.bia_customer_notes      enable row level security;
alter table public.bia_product_images      enable row level security;
alter table public.bia_usage               enable row level security;
alter table public.bia_knowledge           enable row level security;
alter table public.bia_support_tickets     enable row level security;
alter table public.bia_optin               enable row level security;

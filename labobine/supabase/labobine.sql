-- LA BOBINE · comptes, abonnement Pro, crédits, nuage des projets, caisse SasPay.
-- À exécuter UNE fois dans l'éditeur SQL du projet Supabase partagé (xukduhqqfzogisoimhyo). Rejouable sans dégât.
--
-- ⛔ Les tables vivent dans le schéma `labobine`, NON exposé à l'API, avec la sécurité par ligne activée et AUCUNE
--    règle : personne ne les lit directement. Tout passe par les fonctions `public.labobine_*` ci-dessous.
-- ⛔ Les fonctions de la caisse (commande, journal, payer) ne sont exécutables QUE par le rôle serveur.
--    Un navigateur qui les appellerait se fait refuser, même connecté.

create schema if not exists labobine;
revoke all on schema labobine from public, anon, authenticated;

create table if not exists labobine.profils (
  utilisateur uuid primary key references auth.users(id) on delete cascade,
  code        text not null unique,
  parrain     uuid references auth.users(id) on delete set null,
  cree_le     timestamptz not null default now()
);

create table if not exists labobine.abonnements (
  utilisateur uuid primary key references auth.users(id) on delete cascade,
  pro_jusqua  timestamptz not null,
  modifie_le  timestamptz not null default now()
);

create table if not exists labobine.credits (
  id          bigint generated always as identity primary key,
  utilisateur uuid not null references auth.users(id) on delete cascade,
  delta       integer not null,
  motif       text not null,
  reference   text,
  cree_le     timestamptz not null default now()
);

create table if not exists labobine.commandes (
  reference   text primary key check (reference ~ '^LB-[A-Z0-9]{10}$'),
  utilisateur uuid not null references auth.users(id) on delete cascade,
  offre       text not null,
  total       integer not null check (total > 0),
  etat        text not null default 'attente',
  session     text,
  cree_le     timestamptz not null default now(),
  payee_le    timestamptz
);
create index if not exists commandes_session on labobine.commandes (session);

create table if not exists labobine.projets (
  utilisateur uuid not null references auth.users(id) on delete cascade,
  id          text not null check (char_length(id) between 1 and 64),
  nom         text not null default 'Sans titre',
  donnees     jsonb not null,
  modifie_le  timestamptz not null default now(),
  primary key (utilisateur, id)
);

create table if not exists labobine.paiements_journal (
  evenement_id text primary key,
  reference    text,
  session      text,
  montant      numeric,
  devise       text,
  etat_lu      text,
  agi          text,
  brut         jsonb,
  recu_le      timestamptz not null default now()
);

alter table labobine.profils           enable row level security;
alter table labobine.abonnements       enable row level security;
alter table labobine.credits           enable row level security;
alter table labobine.commandes         enable row level security;
alter table labobine.projets           enable row level security;
alter table labobine.paiements_journal enable row level security;

-- ===================================================================== pour la personne connectée
create or replace function public.labobine_moi() returns uuid
language plpgsql security definer set search_path = '' as $$
declare u uuid := auth.uid();
begin
  if u is null then raise exception 'connexion requise' using errcode = '28000'; end if;
  insert into labobine.profils (utilisateur, code)
    values (u, upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 6)))
    on conflict (utilisateur) do nothing;
  return u;
end $$;

create or replace function public.labobine_mes_droits() returns json
language plpgsql security definer set search_path = '' as $$
declare u uuid := public.labobine_moi();
begin
  return json_build_object(
    'pro_jusqua', (select a.pro_jusqua from labobine.abonnements a where a.utilisateur = u),
    'credits',    coalesce((select sum(c.delta) from labobine.credits c where c.utilisateur = u), 0),
    'code',       (select p.code from labobine.profils p where p.utilisateur = u),
    'parrain',    (select p.parrain is not null from labobine.profils p where p.utilisateur = u),
    'maintenant', now()
  );
end $$;

-- Un code de parrainage se pose une fois, avant le premier paiement, et jamais le sien.
create or replace function public.labobine_parrain_poser(p_code text) returns text
language plpgsql security definer set search_path = '' as $$
declare u uuid := public.labobine_moi(); cible uuid;
begin
  select p.utilisateur into cible from labobine.profils p where p.code = upper(trim(p_code));
  if cible is null then return 'code inconnu'; end if;
  if cible = u then return 'c''est ton propre code'; end if;
  if exists (select 1 from labobine.commandes c where c.utilisateur = u and c.etat = 'payee') then return 'trop tard : tu as déjà payé'; end if;
  update labobine.profils set parrain = cible where utilisateur = u and parrain is null;
  if not found then return 'un parrain est déjà posé'; end if;
  return 'ok';
end $$;

create or replace function public.labobine_projets_lister()
returns table (id text, nom text, modifie_le timestamptz)
language plpgsql security definer set search_path = '' as $$
declare u uuid := public.labobine_moi();
begin
  return query select p.id, p.nom, p.modifie_le from labobine.projets p where p.utilisateur = u order by p.modifie_le desc;
end $$;

create or replace function public.labobine_projet_lire(p_id text) returns jsonb
language plpgsql security definer set search_path = '' as $$
declare u uuid := public.labobine_moi();
begin
  return (select p.donnees from labobine.projets p where p.utilisateur = u and p.id = p_id);
end $$;

-- ⛔ Le nuage garde le MONTAGE, jamais les vidéos : 2 Mo au plus par projet.
create or replace function public.labobine_projet_ecrire(p_id text, p_nom text, p_donnees jsonb) returns boolean
language plpgsql security definer set search_path = '' as $$
declare u uuid := public.labobine_moi();
begin
  if octet_length(p_donnees::text) > 2000000 then raise exception 'projet trop lourd pour le nuage'; end if;
  if (select count(*) from labobine.projets p where p.utilisateur = u) >= 200
     and not exists (select 1 from labobine.projets p where p.utilisateur = u and p.id = p_id) then
    raise exception 'nuage plein : 200 projets au plus';
  end if;
  insert into labobine.projets (utilisateur, id, nom, donnees, modifie_le)
    values (u, p_id, left(coalesce(p_nom, 'Sans titre'), 80), p_donnees, now())
    on conflict (utilisateur, id) do update set nom = excluded.nom, donnees = excluded.donnees, modifie_le = now();
  return true;
end $$;

create or replace function public.labobine_projet_supprimer(p_id text) returns boolean
language plpgsql security definer set search_path = '' as $$
declare u uuid := public.labobine_moi();
begin
  delete from labobine.projets p where p.utilisateur = u and p.id = p_id;
  return found;
end $$;

-- ===================================================================== pour le serveur seulement (la caisse)
create or replace function public.labobine_commande_creer(p_utilisateur uuid, p_reference text, p_offre text, p_total integer)
returns boolean language sql security definer set search_path = '' as $$
  insert into labobine.commandes (reference, utilisateur, offre, total) values (p_reference, p_utilisateur, p_offre, p_total) returning true;
$$;

create or replace function public.labobine_commande_session(p_reference text, p_session text)
returns boolean language sql security definer set search_path = '' as $$
  update labobine.commandes set session = p_session where reference = p_reference returning true;
$$;

create or replace function public.labobine_commande_lire(p_reference text)
returns table (existe boolean, etat text, total integer, offre text)
language sql security definer set search_path = '' as $$
  select true, c.etat, c.total, c.offre from labobine.commandes c where c.reference = p_reference;
$$;

create or replace function public.labobine_paiement_par_session(p_session text)
returns table (reference text) language sql security definer set search_path = '' as $$
  select c.reference from labobine.commandes c where c.session = p_session limit 1;
$$;

-- Rend true si l'événement est nouveau, false s'il était déjà écrit (une notification rejouée).
create or replace function public.labobine_paiement_journal(
  p_evenement_id text, p_reference text, p_session text, p_montant numeric, p_devise text, p_etat_lu text, p_agi text, p_brut jsonb)
returns boolean language plpgsql security definer set search_path = '' as $$
begin
  insert into labobine.paiements_journal (evenement_id, reference, session, montant, devise, etat_lu, agi, brut)
    values (coalesce(p_evenement_id, gen_random_uuid()::text), p_reference, p_session, p_montant, p_devise, p_etat_lu, p_agi, p_brut);
  return true;
exception when unique_violation then
  return false;
end $$;

-- ⛔ Tout se fait d'un bloc ou pas du tout : la commande passe « payee » UNE seule fois, et c'est ce passage
--    qui ouvre l'abonnement, verse les crédits et récompense le parrain (7 jours chacun, au premier paiement).
create or replace function public.labobine_payer(p_reference text, p_jours integer, p_credits integer)
returns boolean language plpgsql security definer set search_path = '' as $$
declare u uuid; premier boolean; par uuid;
begin
  update labobine.commandes set etat = 'payee', payee_le = now()
    where reference = p_reference and etat = 'attente' returning utilisateur into u;
  if u is null then return false; end if;
  insert into labobine.abonnements (utilisateur, pro_jusqua) values (u, now() + make_interval(days => p_jours))
    on conflict (utilisateur) do update
      set pro_jusqua = greatest(labobine.abonnements.pro_jusqua, now()) + make_interval(days => p_jours), modifie_le = now();
  if p_credits > 0 then
    insert into labobine.credits (utilisateur, delta, motif, reference) values (u, p_credits, 'abonnement Pro', p_reference);
  end if;
  select count(*) = 1 into premier from labobine.commandes c where c.utilisateur = u and c.etat = 'payee';
  select p.parrain into par from labobine.profils p where p.utilisateur = u;
  if premier and par is not null then
    insert into labobine.abonnements (utilisateur, pro_jusqua) values (par, now() + interval '7 days')
      on conflict (utilisateur) do update set pro_jusqua = greatest(labobine.abonnements.pro_jusqua, now()) + interval '7 days', modifie_le = now();
    update labobine.abonnements set pro_jusqua = pro_jusqua + interval '7 days', modifie_le = now() where utilisateur = u;
  end if;
  return true;
end $$;

-- ===================================================================== droits d'exécution
revoke all on function public.labobine_moi(), public.labobine_mes_droits(), public.labobine_parrain_poser(text),
  public.labobine_projets_lister(), public.labobine_projet_lire(text), public.labobine_projet_ecrire(text, text, jsonb),
  public.labobine_projet_supprimer(text), public.labobine_commande_creer(uuid, text, text, integer),
  public.labobine_commande_session(text, text), public.labobine_commande_lire(text), public.labobine_paiement_par_session(text),
  public.labobine_paiement_journal(text, text, text, numeric, text, text, text, jsonb), public.labobine_payer(text, integer, integer)
  from public, anon, authenticated;

grant execute on function public.labobine_mes_droits(), public.labobine_parrain_poser(text), public.labobine_projets_lister(),
  public.labobine_projet_lire(text), public.labobine_projet_ecrire(text, text, jsonb), public.labobine_projet_supprimer(text)
  to authenticated;

grant execute on function public.labobine_commande_creer(uuid, text, text, integer), public.labobine_commande_session(text, text),
  public.labobine_commande_lire(text), public.labobine_paiement_par_session(text),
  public.labobine_paiement_journal(text, text, text, numeric, text, text, text, jsonb), public.labobine_payer(text, integer, integer)
  to service_role;

-- ════════════════════════════════════════════════════════════════════════════
-- PISTE · LE PAIEMENT EN LIGNE (SasPay)
--
-- À exécuter une fois dans l'éditeur SQL de Supabase, projet PISTE.
-- Il est REJOUABLE : deux exécutions ne font pas plus qu'une.
--
-- ⚠️ CE FICHIER EST LA SOURCE. Comme `functions/piste-cockpit/index.ts`, il
-- tourne chez Supabase mais il vit ICI. Une base n'est pas un dépôt : ce qui
-- n'est écrit que dans l'éditeur Supabase n'est relu par personne et disparaît
-- avec le projet.
--
-- ✅ VÉRIFIÉ SUR LA BASE le 2026-09-03 : la table est `piste.commandes`, AU
-- PLURIEL (le premier jet disait `piste.commande` et le garde-fou du bloc 0
-- l'a arrêté net, ce pour quoi il est écrit), et le total est bien dans
-- `commande->>'total'` (35 commandes relues).
-- ════════════════════════════════════════════════════════════════════════════

-- ── 0. le garde-fou ─────────────────────────────────────────────────────────
DO $$
BEGIN
  IF to_regclass('piste.commandes') IS NULL THEN
    RAISE EXCEPTION
      'Table piste.commandes introuvable. Regarde le vrai nom (\d piste.*) et '
      'remplace-le partout dans ce fichier avant de le rejouer. Rien n''a été '
      'installé.';
  END IF;
END $$;

-- ── 1. les sessions de paiement ─────────────────────────────────────────────
--
-- Pourquoi une table à nous plutôt qu'une colonne sur la commande : la
-- notification du fournisseur ne portera peut-être JAMAIS notre référence,
-- seulement SON identifiant de session. Sans ce répertoire, une notification
-- parfaitement valable serait impossible à rattacher à une commande.
--
-- Le montant y est recopié À LA CRÉATION, depuis la base, jamais depuis le
-- navigateur. C'est lui qu'on comparera au montant réellement encaissé.
CREATE TABLE IF NOT EXISTS piste.paiement_session (
  session     text PRIMARY KEY,
  fournisseur text        NOT NULL DEFAULT 'saspay',
  reference   text        NOT NULL,
  montant     numeric     NOT NULL,
  devise      text        NOT NULL,
  url         text,
  cree_le     timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS paiement_session_reference
  ON piste.paiement_session (reference);

-- ── 2. le journal des notifications ─────────────────────────────────────────
--
-- ⚠️ IL REÇOIT TOUT, MÊME CE QU'ON N'A PAS COMPRIS. Une notification qu'on
-- jette est un paiement qui n'a jamais existé. Tant que la forme exacte des
-- messages SasPay n'est pas confirmée, c'est cette table qui la révélera :
-- `brut` garde le corps entier.
CREATE TABLE IF NOT EXISTS piste.paiement_evenement (
  id           bigserial   PRIMARY KEY,
  fournisseur  text        NOT NULL DEFAULT 'saspay',
  evenement_id text,
  reference    text,
  session      text,
  montant      numeric,
  devise       text,
  etat_lu      text,
  agi          text,
  brut         jsonb       NOT NULL,
  recu_le      timestamptz NOT NULL DEFAULT now()
);

-- L'IDEMPOTENCE. Un fournisseur qui ne reçoit pas notre 200 renvoie la même
-- notification, parfois des heures durant. Sans cette contrainte, une commande
-- serait « payée » dix fois, et le jour où on branchera la livraison
-- automatique, dix carnets partiraient pour un seul paiement.
CREATE UNIQUE INDEX IF NOT EXISTS paiement_evenement_unique
  ON piste.paiement_evenement (fournisseur, evenement_id)
  WHERE evenement_id IS NOT NULL;

-- ── 3. ce que le serveur a le droit de demander ─────────────────────────────

-- Le montant attendu, lu dans la commande. Le navigateur ne le dit jamais :
-- s'il pouvait, on paierait 100 F pour 10 000 F de fiches.
CREATE OR REPLACE FUNCTION public.piste_paiement_attendu(p_reference text)
RETURNS TABLE (existe boolean, etat text, total numeric)
LANGUAGE sql SECURITY DEFINER SET search_path = piste, public AS $$
  SELECT true,
         c.etat::text,
         COALESCE((c.commande->>'total')::numeric, 0)
    FROM piste.commandes c
   WHERE c.reference = p_reference
   LIMIT 1;
$$;

CREATE OR REPLACE FUNCTION public.piste_paiement_session(
  p_session text, p_reference text, p_montant numeric,
  p_devise text, p_url text)
RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER SET search_path = piste, public AS $$
BEGIN
  INSERT INTO piste.paiement_session (session, reference, montant, devise, url)
       VALUES (p_session, p_reference, p_montant, p_devise, p_url)
  ON CONFLICT (session) DO UPDATE SET url = EXCLUDED.url;
  RETURN true;
END $$;

-- Retrouver la commande depuis l'identifiant de session du fournisseur.
CREATE OR REPLACE FUNCTION public.piste_paiement_par_session(p_session text)
RETURNS TABLE (reference text, montant numeric, devise text)
LANGUAGE sql SECURITY DEFINER SET search_path = piste, public AS $$
  SELECT s.reference, s.montant, s.devise
    FROM piste.paiement_session s
   WHERE s.session = p_session
   LIMIT 1;
$$;

-- Journaliser. Rend `false` si l'événement était déjà connu : c'est le signal
-- d'un renvoi, et l'appelant s'arrête là.
CREATE OR REPLACE FUNCTION public.piste_paiement_journal(
  p_evenement_id text, p_reference text, p_session text,
  p_montant numeric, p_devise text, p_etat_lu text, p_agi text, p_brut jsonb)
RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER SET search_path = piste, public AS $$
DECLARE v_pose boolean;
BEGIN
  INSERT INTO piste.paiement_evenement
         (evenement_id, reference, session, montant, devise, etat_lu, agi, brut)
  VALUES (NULLIF(p_evenement_id,''), p_reference, p_session,
          p_montant, p_devise, p_etat_lu, p_agi, p_brut)
  ON CONFLICT DO NOTHING;
  GET DIAGNOSTICS v_pose = ROW_COUNT;
  RETURN v_pose;
END $$;

-- ── 4. les droits ───────────────────────────────────────────────────────────
--
-- ⚠️ AUCUNE de ces portes n'est ouverte au navigateur. Elles ne parlent qu'au
-- `service_role`, c'est-à-dire aux fonctions de bord. Un site statique ne doit
-- pas pouvoir déclarer qu'une commande est payée.
REVOKE ALL ON FUNCTION public.piste_paiement_attendu(text)     FROM public, anon, authenticated;
REVOKE ALL ON FUNCTION public.piste_paiement_par_session(text) FROM public, anon, authenticated;
REVOKE ALL ON FUNCTION public.piste_paiement_journal(text,text,text,numeric,text,text,text,jsonb) FROM public, anon, authenticated;
REVOKE ALL ON FUNCTION public.piste_paiement_session(text,text,numeric,text,text) FROM public, anon, authenticated;

GRANT EXECUTE ON FUNCTION public.piste_paiement_attendu(text)     TO service_role;
GRANT EXECUTE ON FUNCTION public.piste_paiement_par_session(text) TO service_role;
GRANT EXECUTE ON FUNCTION public.piste_paiement_journal(text,text,text,numeric,text,text,text,jsonb) TO service_role;
GRANT EXECUTE ON FUNCTION public.piste_paiement_session(text,text,numeric,text,text) TO service_role;

ALTER TABLE piste.paiement_session    ENABLE ROW LEVEL SECURITY;
ALTER TABLE piste.paiement_evenement  ENABLE ROW LEVEL SECURITY;
-- Aucune politique : sans politique, personne ne lit rien, sauf le
-- `service_role` qui les contourne par construction. C'est voulu.

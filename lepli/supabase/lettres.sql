-- ════════════════════════════════════════════════════════════════════════════
-- LE PLI · LES LETTRES ET LEUR CAISSE
--
-- À exécuter une fois dans l'éditeur SQL de Supabase.
-- Il est REJOUABLE : deux exécutions ne font pas plus qu'une.
--
-- ⚠️ CE FICHIER EST LA SOURCE. Il tourne chez Supabase mais il vit ICI. Une
-- base n'est pas un dépôt : ce qui n'est écrit que dans l'éditeur Supabase
-- n'est relu par personne et disparaît avec le projet.
--
-- ⚠️ CE PROJET SUPABASE PORTE DÉJÀ TROIS PRODUITS (schéma `piste`, schéma
-- `naff`, et `public.boussole_proto_etat`). LE PLI est le quatrième. Il prend
-- son propre schéma, ne touche à rien d'autre, et ⛔ s'il est mis en pause,
-- les quatre tombent ensemble : c'est écrit dans l'arrêté du 2026-09-06.
-- ════════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS lepli;

-- ── 1. les lettres ──────────────────────────────────────────────────────────
--
-- ⛔ ON GARDE LES DONNÉES, PAS LE HTML DU NAVIGATEUR. Une porte publique qui
-- accepte du HTML et le sert sur notre domaine est un hébergeur de pages
-- arbitraires : gratuit, anonyme, et parfait pour une page qui imite une
-- banque. La lettre est rebâtie à partir du gabarit, à chaque lecture.
--
-- `donnees` porte donc exactement ce que le gabarit attend : occasion, pour,
-- de, titre, code, lettre[], photos[], depuis, ouvre, pied, lien.
CREATE TABLE IF NOT EXISTS lepli.lettres (
  jeton      text        PRIMARY KEY,
  palier     text        NOT NULL,
  prix       numeric     NOT NULL,
  donnees    jsonb       NOT NULL,
  -- attente : payée pas encore ; vivante : joignable ; le reste ne se sert pas.
  etat       text        NOT NULL DEFAULT 'attente'
             CHECK (etat IN ('attente', 'vivante', 'annulee')),
  -- Le WhatsApp de l'ACHETEUR, pour lui rendre son lien. ⛔ Jamais celui de la
  -- destinataire : on ne lui écrit pas, c'est une décision de conception.
  whatsapp   text,
  expire_le  timestamptz,
  -- Le retrait de `CONDITIONS.md` : il passe avant tout le reste.
  retire_le  timestamptz,
  cree_le    timestamptz NOT NULL DEFAULT now(),
  paye_le    timestamptz
);

CREATE INDEX IF NOT EXISTS lettres_etat ON lepli.lettres (etat, cree_le DESC);

-- ── 2. la caisse ────────────────────────────────────────────────────────────
--
-- Même forme que PISTE, et pour la même raison : la notification du
-- fournisseur ne portera peut-être JAMAIS notre référence, seulement SON
-- identifiant de session. Sans ce répertoire, une notification parfaitement
-- valable serait impossible à rattacher à une lettre.
--
-- Le montant y est recopié À LA CRÉATION, depuis la base, jamais depuis le
-- navigateur.
CREATE TABLE IF NOT EXISTS lepli.paiement_session (
  session     text PRIMARY KEY,
  fournisseur text        NOT NULL DEFAULT 'saspay',
  jeton       text        NOT NULL,
  montant     numeric     NOT NULL,
  devise      text        NOT NULL,
  url         text,
  cree_le     timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS paiement_session_jeton
  ON lepli.paiement_session (jeton);

-- ⚠️ IL REÇOIT TOUT, MÊME CE QU'ON N'A PAS COMPRIS. Une notification qu'on
-- jette est un paiement qui n'a jamais existé.
CREATE TABLE IF NOT EXISTS lepli.paiement_evenement (
  id           bigserial   PRIMARY KEY,
  fournisseur  text        NOT NULL DEFAULT 'saspay',
  evenement_id text,
  jeton        text,
  session      text,
  montant      numeric,
  devise       text,
  etat_lu      text,
  agi          text,
  brut         jsonb       NOT NULL,
  recu_le      timestamptz NOT NULL DEFAULT now()
);

-- L'IDEMPOTENCE. Un fournisseur qui ne reçoit pas notre 200 renvoie la même
-- notification, parfois des heures durant. Sans cette contrainte, une lettre
-- serait « payée » dix fois.
CREATE UNIQUE INDEX IF NOT EXISTS lepli_evenement_unique
  ON lepli.paiement_evenement (fournisseur, evenement_id)
  WHERE evenement_id IS NOT NULL;

-- ── 3. ce que le serveur a le droit de demander ─────────────────────────────

-- Déposer une lettre. Le prix vient du serveur, jamais du navigateur.
CREATE OR REPLACE FUNCTION public.lepli_deposer(
  p_jeton text, p_palier text, p_prix numeric, p_donnees jsonb,
  p_whatsapp text, p_etat text, p_expire timestamptz)
RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER SET search_path = lepli, public AS $$
BEGIN
  INSERT INTO lepli.lettres (jeton, palier, prix, donnees, whatsapp, etat, expire_le, paye_le)
       VALUES (p_jeton, p_palier, p_prix, p_donnees, p_whatsapp, p_etat, p_expire,
               CASE WHEN p_etat = 'vivante' AND p_prix = 0 THEN now() ELSE NULL END);
  RETURN true;
END $$;

-- Lire une lettre pour la servir. ⛔ Elle ne rend NI le WhatsApp de l'acheteur,
-- NI le prix, NI la date de paiement : servir une lettre ne demande que la
-- lettre.
CREATE OR REPLACE FUNCTION public.lepli_lire(p_jeton text)
RETURNS TABLE (donnees jsonb, etat text, expire_le timestamptz, retire_le timestamptz)
LANGUAGE sql SECURITY DEFINER SET search_path = lepli, public AS $$
  SELECT l.donnees, l.etat::text, l.expire_le, l.retire_le
    FROM lepli.lettres l
   WHERE l.jeton = p_jeton
   LIMIT 1;
$$;

-- Ce qu'on attend d'un paiement. Le montant est relu ICI, sur la lettre.
-- ⚠️ Elle rend AUSSI le palier : la duree de vie d'une lettre en depend, et
-- une valeur devinee cote fonction serait fausse le jour ou un palier change.
CREATE OR REPLACE FUNCTION public.lepli_paiement_attendu(p_jeton text)
RETURNS TABLE (existe boolean, etat text, total numeric, palier text)
LANGUAGE sql SECURITY DEFINER SET search_path = lepli, public AS $$
  SELECT true, l.etat::text, l.prix, l.palier::text
    FROM lepli.lettres l
   WHERE l.jeton = p_jeton
   LIMIT 1;
$$;

CREATE OR REPLACE FUNCTION public.lepli_paiement_session(
  p_session text, p_jeton text, p_montant numeric, p_devise text, p_url text)
RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER SET search_path = lepli, public AS $$
BEGIN
  INSERT INTO lepli.paiement_session (session, jeton, montant, devise, url)
       VALUES (p_session, p_jeton, p_montant, p_devise, p_url)
  ON CONFLICT (session) DO UPDATE SET url = EXCLUDED.url;
  RETURN true;
END $$;

CREATE OR REPLACE FUNCTION public.lepli_paiement_par_session(p_session text)
RETURNS TABLE (jeton text, montant numeric, devise text)
LANGUAGE sql SECURITY DEFINER SET search_path = lepli, public AS $$
  SELECT s.jeton, s.montant, s.devise
    FROM lepli.paiement_session s
   WHERE s.session = p_session
   LIMIT 1;
$$;

-- Journaliser. Rend `false` si l'événement était déjà connu : c'est le signal
-- d'un renvoi, et l'appelant s'arrête là.
CREATE OR REPLACE FUNCTION public.lepli_paiement_journal(
  p_evenement_id text, p_jeton text, p_session text, p_montant numeric,
  p_devise text, p_etat_lu text, p_agi text, p_brut jsonb)
RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER SET search_path = lepli, public AS $$
DECLARE v_pose boolean;
BEGIN
  INSERT INTO lepli.paiement_evenement
         (evenement_id, jeton, session, montant, devise, etat_lu, agi, brut)
  VALUES (NULLIF(p_evenement_id,''), p_jeton, p_session, p_montant, p_devise,
          p_etat_lu, p_agi, p_brut)
  ON CONFLICT DO NOTHING;
  GET DIAGNOSTICS v_pose = ROW_COUNT;
  RETURN v_pose;
END $$;

-- La lettre devient joignable. ⚠️ `expire_le` part de l'ENCAISSEMENT, pas du
-- dépôt : une lettre écrite le lundi et payée le vendredi vit un an à partir
-- du vendredi.
CREATE OR REPLACE FUNCTION public.lepli_ouvrir(p_jeton text, p_jours integer)
RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER SET search_path = lepli, public AS $$
DECLARE v_fait integer;
BEGIN
  UPDATE lepli.lettres
     SET etat = 'vivante',
         paye_le = COALESCE(paye_le, now()),
         expire_le = now() + (p_jours || ' days')::interval
   WHERE jeton = p_jeton AND retire_le IS NULL;
  GET DIAGNOSTICS v_fait = ROW_COUNT;
  RETURN v_fait > 0;
END $$;

-- ⛔ LE RETRAIT. Sans discuter, sans prévenir l'acheteur, sans rembourser.
-- Il n'efface pas la ligne tout de suite : il retire le contenu (donc les
-- photos) et garde la trace comptable du paiement. La lettre ne se sert plus.
CREATE OR REPLACE FUNCTION public.lepli_retirer(p_jeton text)
RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER SET search_path = lepli, public AS $$
DECLARE v_fait integer;
BEGIN
  UPDATE lepli.lettres
     SET retire_le = COALESCE(retire_le, now()),
         donnees = '{}'::jsonb
   WHERE jeton = p_jeton;
  GET DIAGNOSTICS v_fait = ROW_COUNT;
  RETURN v_fait > 0;
END $$;

-- Le ménage : une lettre expirée ne garde pas ses photos. À appeler par une
-- tâche planifiée, ou à la main. ⚠️ La ligne reste, vidée : c'est elle qui
-- permet de répondre « expirée » plutôt que « inconnue ».
CREATE OR REPLACE FUNCTION public.lepli_menage()
RETURNS integer
LANGUAGE plpgsql SECURITY DEFINER SET search_path = lepli, public AS $$
DECLARE v_fait integer;
BEGIN
  UPDATE lepli.lettres
     SET donnees = '{}'::jsonb
   WHERE expire_le IS NOT NULL AND expire_le < now() AND donnees <> '{}'::jsonb;
  GET DIAGNOSTICS v_fait = ROW_COUNT;
  RETURN v_fait;
END $$;

-- ── 4. les droits ───────────────────────────────────────────────────────────
--
-- ⚠️ AUCUNE de ces portes n'est ouverte au navigateur. Elles ne parlent qu'au
-- `service_role`, c'est-à-dire aux fonctions de bord. Un site statique ne doit
-- pas pouvoir déclarer qu'une lettre est payée, ni en lire une autre.
DO $$
DECLARE f text;
BEGIN
  FOR f IN
    SELECT format('%I.%I(%s)', n.nspname, p.proname, pg_get_function_identity_arguments(p.oid))
      FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
     WHERE n.nspname = 'public' AND p.proname LIKE 'lepli\_%'
  LOOP
    EXECUTE format('REVOKE ALL ON FUNCTION %s FROM public, anon, authenticated', f);
    EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO service_role', f);
  END LOOP;
END $$;

ALTER TABLE lepli.lettres            ENABLE ROW LEVEL SECURITY;
ALTER TABLE lepli.paiement_session   ENABLE ROW LEVEL SECURITY;
ALTER TABLE lepli.paiement_evenement ENABLE ROW LEVEL SECURITY;
-- Aucune politique : sans politique, personne ne lit rien, sauf le
-- `service_role` qui les contourne par construction. C'est voulu.

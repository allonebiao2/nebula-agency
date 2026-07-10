// Boussole — adaptateur Supabase (auth e-mail + synchro cloud).
// Le client UMD est chargé via <script> dans index.html -> window.supabase.
import { SUPABASE_URL, SUPABASE_ANON_KEY, CLOUD_ENABLED, ADMIN_EMAILS } from './config.js';
import { setRemote, hydrateFromRemote } from './store.js';

let client = null;
let currentUser = null;
const authListeners = new Set();

export function isCloudConfigured() { return CLOUD_ENABLED && Boolean(window.supabase); }
export function getUser() { return currentUser; }
export function onAuth(fn) { authListeners.add(fn); return () => authListeners.delete(fn); }
function emitAuth() { authListeners.forEach((fn) => fn(currentUser)); }

export async function initSupabase() {
  if (!isCloudConfigured()) return false;
  client = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    auth: { persistSession: true, autoRefreshToken: true },
  });
  const { data } = await client.auth.getSession();
  if (data && data.session) await onSignedIn(data.session.user);

  client.auth.onAuthStateChange(async (_event, session) => {
    if (session && session.user) {
      if (!currentUser || currentUser.id !== session.user.id) await onSignedIn(session.user);
    } else {
      onSignedOut();
    }
  });
  return true;
}

async function onSignedIn(user) {
  currentUser = user;
  setRemote(makeAdapter());
  await hydrateFromRemote();
  subscribeRealtime();
  emitAuth();
}
function onSignedOut() {
  currentUser = null;
  setRemote(null);
  unsubscribeRealtime();
  emitAuth();
}

// ---------- Auth ----------
export async function signUp(email, password) {
  if (!client) throw new Error('Cloud non configuré');
  const { data, error } = await client.auth.signUp({ email: email.trim(), password });
  if (error) throw error;
  return data;
}
export async function signIn(email, password) {
  if (!client) throw new Error('Cloud non configuré');
  const { data, error } = await client.auth.signInWithPassword({ email: email.trim(), password });
  if (error) throw error;
  return data;
}
export async function signOut() { if (client) await client.auth.signOut(); }
export async function updatePassword(newPassword) {
  if (!client) throw new Error('Cloud non configuré');
  const { error } = await client.auth.updateUser({ password: newPassword });
  if (error) throw error;
}
// Vérifie le mot de passe du compte (ré-authentification) — pour les actions sensibles.
export async function verifyPassword(password) {
  if (!client || !currentUser || !currentUser.email) return false;
  const { error } = await client.auth.signInWithPassword({ email: currentUser.email, password });
  return !error;
}

// ---------- Licences : validation À USAGE UNIQUE (en ligne) ----------
// Consomme une clé de façon ATOMIQUE côté serveur : une clé ne peut servir qu'UNE fois.
export async function consumeLicenceKey(code, nom) {
  if (!client) return { ok: false, offline: true };
  const { data, error } = await client.rpc('consume_licence_key', { p_cle: code, p_nom: nom || null });
  if (error) return { ok: false, msg: error.message };
  const plan = Array.isArray(data) ? (data[0] && data[0].plan) : (data && data.plan);
  if (!plan) return { ok: false, used: true };   // clé inexistante OU déjà utilisée
  return { ok: true, plan };
}
// Enregistre une demande de licence (paiement à valider par NEBULA).
export async function submitLicenceRequest(req) {
  if (!client) return { ok: false, offline: true };
  const { error } = await client.from('licence_requests').insert({
    plan: req.plan, montant: req.montant, devise: req.devise || 'F',
    txn: req.txn, nom: req.nom, contact: req.contact || '',
    user_id: currentUser ? currentUser.id : null,
  });
  return { ok: !error, msg: error && error.message };
}
// ---------- Back-office licences (réservé NEBULA) ----------
export function isAdmin() { return !!(currentUser && ADMIN_EMAILS.includes((currentUser.email || '').toLowerCase())); }
export async function adminCreateKey(plan) {
  if (!client) throw new Error('Cloud non configuré');
  const { data, error } = await client.rpc('admin_create_licence_key', { p_plan: plan });
  if (error) throw error;
  return Array.isArray(data) ? (data[0] && data[0].cle) : (data && data.cle);
}
export async function adminListRequests() {
  if (!client) return [];
  const { data } = await client.from('licence_requests').select('*').order('created_at', { ascending: false }).limit(50);
  return data || [];
}
export async function adminListKeys() {
  if (!client) return [];
  const { data } = await client.from('licence_keys').select('*').order('created_at', { ascending: false }).limit(80);
  return data || [];
}
export async function adminSetRequestStatut(id, statut) {
  if (client) await client.from('licence_requests').update({ statut }).eq('id', id);
}
export async function adminGetConfig(key) {
  if (!client) return '';
  const { data } = await client.from('app_config').select('value').eq('key', key).maybeSingle();
  return (data && data.value) || '';
}
export async function adminSetConfig(key, value) {
  if (!client) throw new Error('Cloud non configuré');
  const { error } = await client.rpc('admin_set_config', { p_key: key, p_value: value });
  if (error) throw error;
}
export async function adminTestTelegram() {
  if (!client) throw new Error('Cloud non configuré');
  const { data, error } = await client.rpc('admin_test_telegram');
  if (error) throw error;
  return data;
}

// ---------- Adaptateur CRUD (branché sur le store) ----------
function stripLocal(row) {
  // enlève les champs internes non stockés en base
  const { couts, ...rest } = row;
  return { ...rest, ...(couts !== undefined ? { couts } : {}) };
}
function makeAdapter() {
  const uid = () => currentUser && currentUser.id;
  return {
    async pullAll() {
      const [prof, prods, charges, ventes, depenses, credits, documents, objectifs, achats, clients, audit] = await Promise.all([
        client.from('profils').select('*').maybeSingle(),
        client.from('produits').select('*'),
        client.from('charges_fixes').select('*'),
        client.from('ventes').select('*'),
        client.from('depenses').select('*'),
        client.from('credits').select('*'),
        client.from('documents').select('*'),   // peut ne pas exister avant migration -> géré sans casse
        client.from('objectifs').select('*'),
        client.from('achats').select('*'),
        client.from('clients').select('*'),
        client.from('audit').select('*'),
      ]);
      const p = prof.data || {};
      return {
        profil: prof.data
          ? { nom_activite: p.nom_activite || '', devise: p.devise || 'F', objectif_benefice: Number(p.objectif_benefice) || 0, solde_initial: Number(p.solde_initial) || 0, ifu: p.ifu || '', rccm: p.rccm || '', adresse: p.adresse || '', tel_pro: p.tel_pro || '', email_pro: p.email_pro || '', vendeurs: Array.isArray(p.vendeurs) ? p.vendeurs : [], wa_templates: p.wa_templates || {}, proprietaire: p.proprietaire || '', equipe: Array.isArray(p.equipe) ? p.equipe : [], licence: p.licence || {} }
          : { nom_activite: '', devise: 'F', objectif_benefice: 0, solde_initial: 0, ifu: '', rccm: '', adresse: '', tel_pro: '', email_pro: '', vendeurs: [] },
        produits: (prods.data || []).map((pr) => ({ ...pr, couts: pr.couts || [] })),
        charges_fixes: charges.data || [],
        ventes: ventes.data || [],
        depenses: depenses.data || [],
        credits: credits.data || [],
        documents: documents.data || [],
        objectifs: objectifs.data || [],
        achats: achats.data || [],
        clients: clients.data || [],
        audit: audit.data || [],
        _documentsUnavailable: Boolean(documents.error),   // table absente = migration non lancée
      };
    },
    async upsert(table, row) {
      if (!uid()) return;
      if (table === 'profils') {
        const base = { user_id: uid(), nom_activite: row.nom_activite || '', devise: row.devise || 'F', objectif_benefice: Number(row.objectif_benefice) || 0, solde_initial: Number(row.solde_initial) || 0 };
        const full = { ...base, ifu: row.ifu || '', rccm: row.rccm || '', adresse: row.adresse || '', tel_pro: row.tel_pro || '', email_pro: row.email_pro || '', vendeurs: Array.isArray(row.vendeurs) ? row.vendeurs : [], wa_templates: row.wa_templates || {}, proprietaire: row.proprietaire || '', equipe: Array.isArray(row.equipe) ? row.equipe : [], licence: row.licence || {} };
        let { error } = await client.from('profils').upsert(full, { onConflict: 'user_id' });
        if (error && /column|schema cache|does not exist/i.test(error.message || '')) {
          // colonnes fiscales pas encore migrées -> on sauve au moins les champs de base
          ({ error } = await client.from('profils').upsert(base, { onConflict: 'user_id' }));
        }
        if (error) throw error;
        return;
      }
      const payload = { ...stripLocal(row), user_id: uid() };
      let { error } = await client.from(table).upsert(payload, { onConflict: 'id' });
      if (error && table === 'produits' && /column|schema cache|does not exist/i.test(error.message || '')) {
        // colonnes stock/seuil pas encore migrées -> on sauve au moins le reste du produit
        const { stock, seuil, ...rest } = payload;
        ({ error } = await client.from('produits').upsert(rest, { onConflict: 'id' }));
      }
      if (error) throw error;
    },
    async remove(table, id) {
      if (!uid()) return;
      const { error } = await client.from(table).delete().eq('id', id);
      if (error) throw error;
    },
  };
}

// ---------- Realtime ----------
let channel = null;
let repullTimer = null;
function subscribeRealtime() {
  if (!client || channel) return;
  channel = client.channel('boussole-sync');
  ['produits', 'charges_fixes', 'ventes', 'profils', 'depenses', 'credits', 'documents', 'objectifs', 'achats', 'clients', 'audit'].forEach((table) => {
    channel.on('postgres_changes', { event: '*', schema: 'public', table }, () => {
      clearTimeout(repullTimer);
      repullTimer = setTimeout(() => hydrateFromRemote().catch(() => {}), 400);
    });
  });
  channel.subscribe();
}
function unsubscribeRealtime() {
  if (client && channel) { client.removeChannel(channel); channel = null; }
}

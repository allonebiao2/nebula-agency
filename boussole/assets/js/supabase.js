// Boussole — adaptateur Supabase (auth e-mail + synchro cloud).
// Le client UMD est chargé via <script> dans index.html -> window.supabase.
import { SUPABASE_URL, SUPABASE_ANON_KEY, CLOUD_ENABLED } from './config.js';
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
      const [prof, prods, charges, ventes, depenses, credits, documents, objectifs, achats] = await Promise.all([
        client.from('profils').select('*').maybeSingle(),
        client.from('produits').select('*'),
        client.from('charges_fixes').select('*'),
        client.from('ventes').select('*'),
        client.from('depenses').select('*'),
        client.from('credits').select('*'),
        client.from('documents').select('*'),   // peut ne pas exister avant migration -> géré sans casse
        client.from('objectifs').select('*'),
        client.from('achats').select('*'),
      ]);
      const p = prof.data || {};
      return {
        profil: prof.data
          ? { nom_activite: p.nom_activite || '', devise: p.devise || 'F', objectif_benefice: Number(p.objectif_benefice) || 0, solde_initial: Number(p.solde_initial) || 0, ifu: p.ifu || '', rccm: p.rccm || '', adresse: p.adresse || '', tel_pro: p.tel_pro || '', email_pro: p.email_pro || '', vendeurs: Array.isArray(p.vendeurs) ? p.vendeurs : [] }
          : { nom_activite: '', devise: 'F', objectif_benefice: 0, solde_initial: 0, ifu: '', rccm: '', adresse: '', tel_pro: '', email_pro: '', vendeurs: [] },
        produits: (prods.data || []).map((pr) => ({ ...pr, couts: pr.couts || [] })),
        charges_fixes: charges.data || [],
        ventes: ventes.data || [],
        depenses: depenses.data || [],
        credits: credits.data || [],
        documents: documents.data || [],
        objectifs: objectifs.data || [],
        achats: achats.data || [],
        _documentsUnavailable: Boolean(documents.error),   // table absente = migration non lancée
      };
    },
    async upsert(table, row) {
      if (!uid()) return;
      if (table === 'profils') {
        const base = { user_id: uid(), nom_activite: row.nom_activite || '', devise: row.devise || 'F', objectif_benefice: Number(row.objectif_benefice) || 0, solde_initial: Number(row.solde_initial) || 0 };
        const full = { ...base, ifu: row.ifu || '', rccm: row.rccm || '', adresse: row.adresse || '', tel_pro: row.tel_pro || '', email_pro: row.email_pro || '', vendeurs: Array.isArray(row.vendeurs) ? row.vendeurs : [] };
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
  ['produits', 'charges_fixes', 'ventes', 'profils', 'depenses', 'credits', 'documents', 'objectifs', 'achats'].forEach((table) => {
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

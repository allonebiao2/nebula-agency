// Boussole — data layer + logique des 3 enveloppes.
// Offline-first : localStorage est toujours à jour. Si une session Supabase existe,
// on reflète chaque écriture dans le cloud (optimiste) pour la synchro multi-appareils.
import { DEVISE, CURRENCIES } from './config.js';

const LS_BASE = 'boussole:v1';
// Multi-boutiques : chaque boutique a son propre espace localStorage.
// « principale » = boussole:v1 (données existantes, SEULE synchronisée au cloud) ;
// les autres = boussole:v1:<id> (locales à l'appareil).
let activeBoutique = (() => { try { return localStorage.getItem('boussole:active-boutique') || 'principale'; } catch { return 'principale'; } })();
function lsKey() { return activeBoutique && activeBoutique !== 'principale' ? LS_BASE + ':' + activeBoutique : LS_BASE; }
export function isMainBoutique() { return activeBoutique === 'principale'; }
const uid = () => (crypto.randomUUID ? crypto.randomUUID() : 'id-' + Date.now() + '-' + Math.random().toString(16).slice(2));
const nowISO = () => new Date().toISOString();

// ---------- État ----------
function emptyState() {
  return {
    profil: { nom_activite: '', devise: DEVISE, solde_initial: 0, ifu: '', rccm: '', adresse: '', tel_pro: '', email_pro: '', vendeurs: [] },
    produits: [],        // {id, nom, modele, prix_vente, couts:[{id,libelle,montant}], archive, created_at}
    charges_fixes: [],   // {id, libelle, montant, created_at}  (mensuel, niveau activité)
    ventes: [],          // {id, produit_id, date, qte, prix_unitaire, cout_unitaire, created_at}
    depenses: [],        // {id, libelle, categorie, montant, date, created_at}  (sorties d'argent)
    credits: [],         // {id, client, tel, montant, paye, date, echeance, note}  (ventes à crédit)
    documents: [],       // {id, type:'facture'|'devis', numero, date, echeance, client:{nom,tel,adresse}, lignes:[{designation,qte,pu}], remise, tva_taux, acompte, notes, statut, created_at}
    objectifs: [],       // {id, titre, icone, montant_cible, montant_actuel, echeance, note, created_at}  (cagnottes/projets)
    achats: [],          // {id, fournisseur, date, lignes:[{produit_id,qte,cout_unitaire}], statut, note, created_at}  (achats fournisseurs)
    clients: [],         // {id, nom, tel, adresse, note, created_at}  (annuaire client explicite)
    audit: [],           // {id, action, cible, detail, auteur, date}  (journal anti-fraude — Pro)
  };
}

// ---------- Journal d'audit (Pro : qui a modifié/supprimé quoi, quand) ----------
let auditAuthor = 'Patron';
export function setAuditAuthor(nom) { auditAuthor = (nom || 'Patron').trim() || 'Patron'; }
export function logAudit(action, cible, detail) {
  if (!state.audit) state.audit = [];
  const row = { id: uid(), action, cible, detail: detail || '', auteur: auditAuthor, date: nowISO() };
  state.audit.push(row);
  if (state.audit.length > 800) state.audit = state.audit.slice(-800);
  persistLocal(); pushRemote('audit', row);
}
export function getAudit(n = 150) { return [...(state.audit || [])].reverse().slice(0, n); }

// Catégories de dépenses. « Réassort / Stock » = achat de marchandise : sort de la caisse
// mais N'EST PAS une charge (le coût passe déjà par la marge des produits) -> exclu du bénéfice.
export const DEPENSE_CATS = ['Réassort / Stock', 'Transport', 'Loyer', 'Salaires', 'Factures', 'Divers'];
export const RESTOCK_CAT = 'Réassort / Stock';

// Modes de paiement d'une vente (caisse)
export const PAYMENT_MODES = ['especes', 'momo', 'carte', 'credit', 'autre'];
export const PAYMENT_LABELS = { especes: 'Espèces', momo: 'Mobile Money', carte: 'Carte', credit: 'Crédit', autre: 'Autre' };

let state = emptyState();
let remote = null;          // adaptateur cloud (null = mode local)
const listeners = new Set();

// ---------- Événements ----------
export function subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); }
function emit() { listeners.forEach((fn) => fn(state)); }

// ---------- Persistance locale ----------
function hasLS() { try { return typeof localStorage !== 'undefined'; } catch { return false; } }
function persistLocal() {
  if (!hasLS()) return;
  try { localStorage.setItem(lsKey(), JSON.stringify(state)); } catch (e) { console.warn('persist local', e); }
}
function loadLocal() {
  if (!hasLS()) return;
  state = emptyState();
  try {
    const raw = localStorage.getItem(lsKey());
    if (raw) state = Object.assign(emptyState(), JSON.parse(raw));
  } catch (e) { console.warn('load local', e); }
}

// ---------- Cloud ----------
export function setRemote(adapter) { remote = adapter; }
export async function hydrateFromRemote() {
  if (!remote || !isMainBoutique()) return;   // le cloud ne concerne que la boutique principale
  const data = await remote.pullAll();
  if (!data) return;
  const cloudVide = !((data.produits && data.produits.length) || (data.ventes && data.ventes.length) ||
    (data.charges_fixes && data.charges_fixes.length) || (data.depenses && data.depenses.length) || (data.profil && data.profil.nom_activite));
  const localRempli = state.produits.length || state.ventes.length || state.charges_fixes.length || state.depenses.length || state.profil.nom_activite;
  if (cloudVide && localRempli) {
    // Premier appareil : le cloud est vide → on POUSSE le local vers le cloud (jamais d'écrasement).
    state.produits.forEach((p) => pushRemote('produits', p));
    state.charges_fixes.forEach((c) => pushRemote('charges_fixes', c));
    state.ventes.forEach((v) => pushRemote('ventes', v));
    state.depenses.forEach((d) => pushRemote('depenses', d));
    state.credits.forEach((c) => pushRemote('credits', c));
    state.documents.forEach((d) => pushRemote('documents', d));
    state.objectifs.forEach((o) => pushRemote('objectifs', o));
    state.achats.forEach((a) => pushRemote('achats', a));
    state.clients.forEach((cl) => pushRemote('clients', cl));
    (state.audit || []).forEach((a) => pushRemote('audit', a));
    pushRemote('profils', { id: 'me', ...state.profil });
    return;
  }
  // Sinon : le cloud fait foi (déjà des données en ligne, ou local vide).
  const localDocs = state.documents || [];
  const docsUnavail = data._documentsUnavailable;
  delete data._documentsUnavailable;
  state = Object.assign(emptyState(), data);
  // filet : si la table documents n'existe pas encore côté cloud (migration non
  // lancée), on NE perd PAS les factures/devis créés localement.
  if (docsUnavail && localDocs.length) state.documents = localDocs;
  persistLocal();
  emit();
}
// Le cloud ne synchronise QUE la boutique principale (les autres restent locales).
function pushRemote(table, row) { if (remote && isMainBoutique()) remote.upsert(table, row).catch((e) => console.warn('push', table, e)); }
function delRemote(table, id) { if (remote && isMainBoutique()) remote.remove(table, id).catch((e) => console.warn('del', table, e)); }

// ---------- Multi-boutiques (Pro) ----------
function loadBoutiques() { try { return JSON.parse(localStorage.getItem('boussole:boutiques')) || null; } catch { return null; } }
function saveBoutiques(list) { try { localStorage.setItem('boussole:boutiques', JSON.stringify(list)); } catch {} }
export function getBoutiques() {
  let list = loadBoutiques();
  if (!list || !list.length) { list = [{ id: 'principale', nom: state.profil.nom_activite || 'Ma boutique' }]; saveBoutiques(list); }
  return list;
}
export function activeBoutiqueId() { return activeBoutique; }
export function addBoutique(nom) {
  nom = (nom || '').trim(); if (!nom) return null;
  const list = getBoutiques();
  const id = 'b' + Date.now().toString(36);
  list.push({ id, nom }); saveBoutiques(list);
  return id;
}
export function renameBoutique(id, nom) { const list = getBoutiques().map((b) => (b.id === id ? { ...b, nom: (nom || '').trim() || b.nom } : b)); saveBoutiques(list); }
export function deleteBoutique(id) {
  if (id === 'principale') return;
  saveBoutiques(getBoutiques().filter((b) => b.id !== id));
  try { localStorage.removeItem(LS_BASE + ':' + id); } catch {}
  if (activeBoutique === id) switchBoutique('principale');
}
export function switchBoutique(id) {
  if (!getBoutiques().some((b) => b.id === id)) return;
  activeBoutique = id;
  try { localStorage.setItem('boussole:active-boutique', id); } catch {}
  loadLocal(); emit();
}
// Vue consolidée : lit l'espace de chaque boutique et agrège les indicateurs clés.
export function consolideBoutiques() {
  const now = new Date();
  const mkStart = new Date(now.getFullYear(), now.getMonth(), 1).getTime();
  const rows = getBoutiques().map((b) => {
    let data = state;
    if (b.id !== activeBoutique) {
      try { const raw = localStorage.getItem(b.id === 'principale' ? LS_BASE : LS_BASE + ':' + b.id); data = raw ? JSON.parse(raw) : emptyState(); } catch { data = emptyState(); }
    }
    const ventes = (data.ventes || []).filter((v) => new Date(v.date).getTime() >= mkStart);
    const ca = ventes.reduce((s, v) => s + (v.qte || 0) * (v.prix_unitaire || 0), 0);
    const marge = ventes.reduce((s, v) => s + (v.qte || 0) * ((v.prix_unitaire || 0) - (v.cout_unitaire || 0)), 0);
    const dep = (data.depenses || []).filter((d) => new Date(d.date).getTime() >= mkStart).reduce((s, d) => s + (Number(d.montant) || 0), 0);
    const dettes = (data.credits || []).reduce((s, c) => { const r = Math.max(0, (Number(c.montant) || 0) - (c.paiements || []).reduce((x, p) => x + (Number(p.montant) || 0), 0)); return s + (c.paye && !(c.paiements || []).length ? 0 : r); }, 0);
    return { id: b.id, nom: b.nom, ca, marge, depenses: dep, dettes, active: b.id === activeBoutique };
  });
  const tot = rows.reduce((t, r) => ({ ca: t.ca + r.ca, marge: t.marge + r.marge, depenses: t.depenses + r.depenses, dettes: t.dettes + r.dettes }), { ca: 0, marge: 0, depenses: 0, dettes: 0 });
  return { rows, tot };
}

// ---------- Sélecteurs de base ----------
export function getState() { return state; }
export function getProduits({ withArchived = false } = {}) {
  return state.produits.filter((p) => withArchived || !p.archive);
}
export function getProduit(id) { return state.produits.find((p) => p.id === id) || null; }
export function getChargesFixes() { return state.charges_fixes; }
export function getVentes() { return state.ventes; }

// ---------- Mutations : profil ----------
export function setProfil(patch) {
  state.profil = Object.assign({}, state.profil, patch);
  persistLocal(); pushRemote('profils', { id: 'me', ...state.profil }); emit();
}

// ---------- Mutations : produits ----------
export function addProduit({ nom, modele, prix_vente = 0, couts = [], stock = null, seuil = 0 }) {
  const p = {
    id: uid(), nom: nom.trim(), modele, prix_vente: Number(prix_vente) || 0,
    couts: couts.map((c) => ({ id: uid(), libelle: c.libelle, montant: Number(c.montant) || 0 })),
    stock: (stock === null || stock === '') ? null : Math.max(0, Number(stock) || 0),  // null = non suivi
    seuil: Number(seuil) || 0,                                                          // seuil d'alerte stock bas
    archive: false, created_at: nowISO(),
  };
  state.produits.push(p);
  persistLocal(); pushRemote('produits', p); emit();
  return p;
}
export function updateProduit(id, patch) {
  const p = getProduit(id); if (!p) return;
  Object.assign(p, patch);
  if (patch.couts) p.couts = patch.couts.map((c) => ({ id: c.id || uid(), libelle: c.libelle, montant: Number(c.montant) || 0 }));
  if (patch.prix_vente != null) p.prix_vente = Number(patch.prix_vente) || 0;
  if ('stock' in patch) p.stock = (patch.stock === null || patch.stock === '') ? null : Math.max(0, Number(patch.stock) || 0);
  if (patch.seuil != null) p.seuil = Math.max(0, Number(patch.seuil) || 0);
  persistLocal(); pushRemote('produits', p); emit();
}
export function archiveProduit(id) { updateProduit(id, { archive: true }); }
export function deleteProduit(id) {
  state.produits = state.produits.filter((p) => p.id !== id);
  state.ventes = state.ventes.filter((v) => v.produit_id !== id);
  persistLocal(); delRemote('produits', id); emit();
}

// ---------- Mutations : charges fixes ----------
export function addChargeFixe({ libelle, montant }) {
  const c = { id: uid(), libelle: libelle.trim(), montant: Number(montant) || 0, created_at: nowISO() };
  state.charges_fixes.push(c);
  persistLocal(); pushRemote('charges_fixes', c); emit();
  return c;
}
export function updateChargeFixe(id, patch) {
  const c = state.charges_fixes.find((x) => x.id === id); if (!c) return;
  Object.assign(c, patch); if (patch.montant != null) c.montant = Number(patch.montant) || 0;
  persistLocal(); pushRemote('charges_fixes', c); emit();
}
export function deleteChargeFixe(id) {
  state.charges_fixes = state.charges_fixes.filter((c) => c.id !== id);
  persistLocal(); delRemote('charges_fixes', id); emit();
}

// ---------- Mutations : dépenses (sorties d'argent) ----------
export function getDepenses() { return state.depenses; }
export function addDepense({ libelle, categorie, montant, date }) {
  const d = {
    id: uid(), libelle: (libelle || '').trim(), categorie: DEPENSE_CATS.includes(categorie) ? categorie : 'Divers',
    montant: Number(montant) || 0, date: date || nowISO(), created_at: nowISO(),
  };
  state.depenses.push(d);
  persistLocal(); pushRemote('depenses', d); emit();
  return d;
}
export function updateDepense(id, patch) {
  const d = state.depenses.find((x) => x.id === id); if (!d) return;
  Object.assign(d, patch); if (patch.montant != null) d.montant = Number(patch.montant) || 0;
  persistLocal(); pushRemote('depenses', d); emit();
}
export function deleteDepense(id) {
  const d = state.depenses.find((x) => x.id === id);
  if (d) logAudit('suppression', 'dépense', `${d.categorie || ''} ${formatF(d.montant)}`.trim());
  state.depenses = state.depenses.filter((x) => x.id !== id);
  persistLocal(); delRemote('depenses', id); emit();
}

// ---------- Solde de caisse (fond de départ) ----------
export function getSoldeInitial() { return Number(state.profil.solde_initial) || 0; }
export function setSoldeInitial(v) { setProfil({ solde_initial: Math.round(Number(v) || 0) }); }

// ---------- Mutations : ventes ----------
export function addVente({ produit_id, qte = 1, prix_unitaire, date, mode, vendeur, ticket }) {
  const p = getProduit(produit_id); if (!p) return null;
  const v = {
    id: uid(), produit_id, qte: Number(qte) || 1,
    prix_unitaire: prix_unitaire != null ? Number(prix_unitaire) : p.prix_vente,
    cout_unitaire: coutRevient(p),          // coût figé à l'instant de la vente
    mode: PAYMENT_MODES.includes(mode) ? mode : 'especes',
    vendeur: (vendeur || '').trim(),
    ticket: ticket || '',
    date: date || nowISO(), created_at: nowISO(),
  };
  state.ventes.push(v);
  // décrément automatique du stock si le produit est suivi
  if (p.stock !== null && p.stock !== undefined) { p.stock = Math.max(0, (Number(p.stock) || 0) - (Number(v.qte) || 1)); pushRemote('produits', p); }
  persistLocal(); pushRemote('ventes', v); emit();
  return v;
}
export function deleteVente(id) {
  const v = state.ventes.find((x) => x.id === id);
  if (v) {
    const p = getProduit(v.produit_id);
    logAudit('suppression', 'vente', `${p ? p.nom : 'Produit'} · ${v.qte}×${formatF(v.prix_unitaire)} = ${formatF((v.qte || 0) * (v.prix_unitaire || 0))}`);
    if (p && p.stock !== null && p.stock !== undefined) { p.stock = (Number(p.stock) || 0) + (Number(v.qte) || 0); pushRemote('produits', p); }
  }
  state.ventes = state.ventes.filter((x) => x.id !== id);
  persistLocal(); delRemote('ventes', id); emit();
}

// ---------- Caisse : encaissement panier (plusieurs articles en 1 ticket) ----------
export function encaisserPanier(items, { mode = 'especes', vendeur = '', date } = {}) {
  const list = (items || []).filter((it) => it.produit_id && (Number(it.qte) || 0) > 0);
  if (!list.length) return null;
  const ticket = uid();
  const d = date || nowISO();
  list.forEach((it) => addVente({ produit_id: it.produit_id, qte: it.qte, prix_unitaire: it.prix_unitaire, mode, vendeur, ticket, date: d }));
  return ticket;
}
export function ticketVentes(ticket) {
  return state.ventes.filter((v) => v.ticket && v.ticket === ticket)
    .map((v) => { const p = getProduit(v.produit_id); return { ...v, nom: p ? p.nom : 'Produit' }; });
}
// Données d'un reçu de caisse à partir d'une vente (regroupe le ticket si présent)
export function receiptData(venteId) {
  const v = state.ventes.find((x) => x.id === venteId); if (!v) return null;
  const lignes = v.ticket ? ticketVentes(v.ticket)
    : [{ ...v, nom: (getProduit(v.produit_id) || {}).nom || 'Produit' }];
  const total = lignes.reduce((s, l) => s + (Number(l.qte) || 0) * (Number(l.prix_unitaire) || 0), 0);
  return { lignes, total, mode: v.mode || 'especes', vendeur: v.vendeur || '', date: v.date, ref: v.ticket || v.id };
}
export function receiptByTicket(ticket) {
  const lignes = ticketVentes(ticket); if (!lignes.length) return null;
  const total = lignes.reduce((s, l) => s + (Number(l.qte) || 0) * (Number(l.prix_unitaire) || 0), 0);
  const f = lignes[0];
  return { lignes, total, mode: f.mode || 'especes', vendeur: f.vendeur || '', date: f.date, ref: ticket };
}

// ---------- Équipe & droits (rôles des vendeurs) ----------
// Rôles et ce que chacun a le droit de faire (permissions par écran/capacité).
export const ROLES = ['patron', 'gerant', 'vendeur'];
export const ROLE_LABELS = { patron: 'Patron', gerant: 'Gérant', vendeur: 'Vendeur' };
export const ROLE_DESCS = {
  patron: 'Accès total : ventes, finances, stock, réglages, équipe et sécurité.',
  gerant: 'Ventes, dépenses, stock, carnet et bilan. Pas les réglages ni la sécurité.',
  vendeur: 'Enregistre les ventes et consulte le carnet. Ni finances, ni réglages.',
};
export const ROLE_PERMS = {
  patron: ['ventes', 'depenses', 'stock', 'carnet', 'bilan', 'reglages'],
  gerant: ['ventes', 'depenses', 'stock', 'carnet', 'bilan'],
  vendeur: ['ventes', 'carnet'],
};
export function roleLabel(r) { return ROLE_LABELS[r] || r; }
export function rolePerms(r) { return ROLE_PERMS[r] || ROLE_PERMS.vendeur; }

function membreSlug(s) { return String(s || '').trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || ('m' + Date.now().toString(36)); }
// Renvoie l'équipe en objets {id,nom,role,actif}. Migre l'ancienne liste de noms.
export function getEquipe() {
  const raw = state.profil.equipe;
  if (Array.isArray(raw) && raw.length && typeof raw[0] === 'object') {
    return raw.map((m) => ({ id: m.id || membreSlug(m.nom), nom: m.nom || '', role: ROLES.includes(m.role) ? m.role : 'vendeur', actif: m.actif !== false }));
  }
  const noms = Array.isArray(state.profil.vendeurs) ? state.profil.vendeurs : [];
  return noms.map((n) => ({ id: membreSlug(n), nom: n, role: 'vendeur', actif: true }));
}
export function getMembre(id) { return getEquipe().find((m) => m.id === id) || null; }
function saveEquipe(list) { setProfil({ equipe: list }); }
export function addMembre(nom, role = 'vendeur') {
  nom = (nom || '').trim(); if (!nom) return;
  const list = getEquipe();
  if (list.some((m) => m.nom.toLowerCase() === nom.toLowerCase())) return;
  list.push({ id: membreSlug(nom), nom, role: ROLES.includes(role) ? role : 'vendeur', actif: true });
  saveEquipe(list);
}
export function updateMembre(id, patch) { saveEquipe(getEquipe().map((m) => (m.id === id ? { ...m, ...patch } : m))); }
export function removeMembre(id) { saveEquipe(getEquipe().filter((m) => m.id !== id)); }

// Compat : le reste de l'appli (caisse, historique) utilise les NOMS des vendeurs actifs.
export function getVendeurs() { return getEquipe().filter((m) => m.actif).map((m) => m.nom); }
export function addVendeur(nom) { addMembre(nom, 'vendeur'); }
export function removeVendeur(nom) { const m = getEquipe().find((x) => x.nom === nom); if (m) removeMembre(m.id); }

// ---------- Abonnement & licence (produit NEBULA) ----------
// Modèle : 30 jours d'essai gratuit -> ensuite BLOCAGE tant qu'une licence
// mensuelle n'est pas activée. 3 paliers. Paiement Mobile Money, validation par
// NEBULA (Telegram/WhatsApp) qui envoie la clé ; le client l'active ici.
export const TRIAL_DAYS = 30;
// 2 paliers payants (l'essai de 30 j ouvre TOUT ; ensuite blocage total = paywall).
// ⚠️ prix mensuels À VALIDER par Mongazi. Copywriting de vente fourni par Mongazi.
export const PLANS = {
  essentiel: {
    nom: 'Essentiel', tag: 'Commerçant solo', prix: 5000, badge: 'Le plus populaire',
    cible: '1 personne · 1 appareil',
    inclus: ['Ventes & dépenses (pro/perso)', 'Gestion de stock & alertes', 'Carnet de dettes & relances', 'Factures, reçus & rapports'],
    peur: 'Tu perds des milliers de FCFA chaque mois en oubliant des dettes ou en gérant mal ton stock sur papier. Ce plan rembourse son prix dès ton premier jour d’utilisation.',
    ridicule: 'Ne pas investir le prix d’un simple café par jour pour sécuriser ton gagne-pain et doubler tes bénéfices, c’est saboter ton propre business.',
  },
  pro: {
    nom: 'Pro / Équipe', tag: 'Gérant avec employés', prix: 10000, badge: 'Meilleure valeur',
    cible: 'Multi-appareils · équipe & droits',
    inclus: ['Tout l’Essentiel', 'Anti-vol : rôles (l’employé ne voit que la caisse)', 'Historique d’audit (qui a modifié/supprimé)', 'Multi-appareils & multi-boutiques', 'Relances de dettes automatiques'],
    peur: 'Quand tu as le dos tourné, tes employés gèrent TA caisse. Sans le mode Pro, tu acceptes de fermer les yeux sur le vol, les suppressions de ventes en douce et les erreurs suspectes.',
    ridicule: 'Continuer à te déplacer chaque soir pour vérifier tes boutiques ou risquer de te faire voler ta caisse pour un prix aussi dérisoire, c’est un suicide financier. Prends le contrôle à distance maintenant.',
  },
};
export function getLicence() {
  const l = state.profil.licence || {};
  return { plan: PLANS[l.plan] ? l.plan : 'essentiel', statut: l.statut || '', echeance: l.echeance || '', cle: l.cle || '', essai_debut: l.essai_debut || '' };
}
export function setLicence(patch) { setProfil({ licence: { ...getLicence(), ...patch } }); }
// Démarre l'essai à la 1re ouverture (idempotent).
export function ensureTrial() { const l = getLicence(); if (!l.essai_debut) setLicence({ essai_debut: nowISO() }); }
// État courant de la licence : essai en cours / active / expirée (+ blocage).
export function licenceEtat() {
  const l = getLicence(); const now = Date.now();
  if (l.cle && l.echeance) {
    const fin = new Date(l.echeance).getTime();
    if (now <= fin) return { mode: 'actif', bloque: false, plan: l.plan, echeance: l.echeance, joursRestants: Math.ceil((fin - now) / DAY_MS) };
    return { mode: 'expire', bloque: true, plan: l.plan, echeance: l.echeance };
  }
  if (l.essai_debut) {
    const fin = new Date(l.essai_debut).getTime() + TRIAL_DAYS * DAY_MS;
    if (now <= fin) return { mode: 'essai', bloque: false, plan: l.plan, joursRestants: Math.max(0, Math.ceil((fin - now) / DAY_MS)) };
    return { mode: 'expire_essai', bloque: true, plan: l.plan };
  }
  return { mode: 'essai', bloque: false, plan: l.plan, joursRestants: TRIAL_DAYS };
}
// Accès aux fonctions Pro : ouvert pendant l'essai (tout), sinon licence Pro active.
export function proAccess() { const e = licenceEtat(); return e.mode === 'essai' || (e.mode === 'actif' && e.plan === 'pro'); }

// ---------- Relances de dettes « intelligentes » (Pro) ----------
// Une relance devient DUE quand l'échéance est atteinte (ou dette ancienne sans échéance).
// Un clic ouvre le WhatsApp du client avec un message ADAPTÉ (retard, montant restant).
export function relancesDues() {
  const now = Date.now();
  return state.credits.map((c) => {
    const reste = creditReste(c);
    if (reste <= 0 || !c.tel) return null;
    const ech = c.echeance ? new Date(c.echeance).getTime() : null;
    const age = c.date ? Math.floor((now - new Date(c.date).getTime()) / DAY_MS) : 0;
    const joursRetard = ech ? Math.floor((now - ech) / DAY_MS) : null;
    const due = ech ? now >= ech - DAY_MS : age >= 14;   // échéance atteinte (ou J-1) / dette ancienne
    return due ? { id: c.id, client: c.client, tel: c.tel, reste, echeance: c.echeance, joursRetard, age } : null;
  }).filter(Boolean).sort((a, b) => (b.joursRetard ?? -999) - (a.joursRetard ?? -999));
}
// Message WhatsApp adapté à la situation de la dette (réutilise le modèle « relance »).
export function messageRelance(c) {
  const nom = state.profil.nom_activite || '';
  let contexte = '';
  const ech = c.echeance ? new Date(c.echeance).getTime() : null;
  if (ech) {
    const jr = Math.floor((Date.now() - ech) / DAY_MS);
    if (jr > 0) contexte = ` (échéance dépassée de ${jr} jour${jr > 1 ? 's' : ''})`;
    else if (jr === 0) contexte = ' (échéance aujourd’hui)';
    else contexte = ` (échéance dans ${-jr} jour${-jr > 1 ? 's' : ''})`;
  }
  const reste = c.reste != null ? c.reste : creditReste(c);
  return renderTemplate(getWaTemplate('relance'), { client: c.client || '', commerce: nom, reste: formatF(reste), echeance: contexte });
}

// Enregistre la clé envoyée par NEBULA (BSL-XXXX-XXXX) -> licence mensuelle active.
export function activateLicence(code, plan) {
  code = (code || '').trim().toUpperCase();
  if (!code) return { ok: false, msg: 'Entre le code envoyé par NEBULA.' };
  if (!/^BSL-[A-Z0-9]{4}-[A-Z0-9]{4}$/.test(code)) return { ok: false, msg: 'Code invalide. Format attendu : BSL-XXXX-XXXX.' };
  const echeance = new Date(Date.now() + 30 * DAY_MS).toISOString();
  setLicence({ cle: code, plan: PLANS[plan] ? plan : getLicence().plan, statut: 'actif', echeance });
  return { ok: true };
}

// ---------- Messages WhatsApp configurables (textes prédéfinis) ----------
// Le commerçant personnalise les textes envoyés par WhatsApp. Les {variables}
// sont remplacées automatiquement au moment de l'envoi.
export const WA_TEMPLATES_DEF = {
  relance: 'Bonjour {client}, petit rappel amical : il reste {reste} à régler sur votre ardoise chez {commerce}. Merci d’avance !',
  recu: 'Merci pour votre achat chez {commerce} ! Total réglé : {total}. À très bientôt.',
  remerciement: 'Bonjour {client}, merci pour votre confiance et à très bientôt chez {commerce} !',
};
export const WA_TEMPLATES_META = {
  relance: { label: 'Relance de dette', vars: ['client', 'commerce', 'reste', 'echeance'] },
  recu: { label: 'Message du reçu', vars: ['commerce', 'total', 'client'] },
  remerciement: { label: 'Message de remerciement', vars: ['client', 'commerce'] },
};
export function getWaTemplate(key) {
  const t = state.profil.wa_templates || {};
  return (t[key] != null && String(t[key]).trim()) ? t[key] : (WA_TEMPLATES_DEF[key] || '');
}
export function setWaTemplate(key, text) {
  const t = { ...(state.profil.wa_templates || {}) };
  t[key] = text; setProfil({ wa_templates: t });
}
export function resetWaTemplate(key) {
  const t = { ...(state.profil.wa_templates || {}) };
  delete t[key]; setProfil({ wa_templates: t });
}
// Remplace {cle} par vars.cle (chaîne vide si absent).
export function renderTemplate(text, vars = {}) {
  return String(text || '').replace(/\{(\w+)\}/g, (_, k) => (vars[k] != null ? String(vars[k]) : ''))
    .replace(/[ \t]{2,}/g, ' ').replace(/ +([.,!?])/g, '$1').trim();
}

// ---------- Reset (déconnexion / effacer) ----------
export function resetLocal() { state = emptyState(); persistLocal(); emit(); }

// =====================================================================
//  LOGIQUE MÉTIER — coûts, marges, 3 enveloppes, bilans
// =====================================================================
export function coutRevient(produit) {
  if (!produit || !produit.couts) return 0;
  return produit.couts.reduce((s, c) => s + (Number(c.montant) || 0), 0);
}
export function margeUnitaire(produit) { return (produit.prix_vente || 0) - coutRevient(produit); }
export function chargesMensuellesTotal() {
  return state.charges_fixes.reduce((s, c) => s + (Number(c.montant) || 0), 0);
}

export function monthKey(dateISO) { return String(dateISO).slice(0, 7); } // 'YYYY-MM'
export function currentMonthKey() { return monthKey(nowISO()); }

// Agrège une liste de ventes en 3 enveloppes, pour une cible de charges donnée.
function computeEnveloppes(ventes, chargesCible) {
  let revenu = 0, cout = 0, unites = 0;
  for (const v of ventes) {
    revenu += (v.qte || 0) * (v.prix_unitaire || 0);
    cout += (v.qte || 0) * (v.cout_unitaire || 0);
    unites += (v.qte || 0);
  }
  const marge = revenu - cout;
  const env2 = Math.max(0, Math.min(marge, chargesCible)); // charges couvertes
  const env3 = marge - env2;                               // bénéfice net (peut être <0)
  return {
    revenu, unites,
    relance: cout,           // enveloppe 1
    charges_cible: chargesCible,
    charges_couvertes: env2, // enveloppe 2
    benefice: env3,          // enveloppe 3
    marge,
    charges_reste: Math.max(0, chargesCible - env2),
    a_perte: marge < 0,
  };
}

export function ventesDuMois(mk = currentMonthKey()) {
  return state.ventes.filter((v) => monthKey(v.date) === mk);
}

// Bilan d'un mois (cible de charges = charges mensuelles totales).
export function bilanMois(mk = currentMonthKey()) {
  return computeEnveloppes(ventesDuMois(mk), chargesMensuellesTotal());
}

// Série des N derniers mois (bénéfice net par mois) pour le graphe.
export function serieMensuelle(nbMois = 6) {
  const out = [];
  const d = new Date();
  d.setDate(1);
  for (let i = nbMois - 1; i >= 0; i--) {
    const dd = new Date(d.getFullYear(), d.getMonth() - i, 1);
    const mk = `${dd.getFullYear()}-${String(dd.getMonth() + 1).padStart(2, '0')}`;
    const b = bilanMois(mk);
    out.push({ mois: mk, label: MOIS_COURTS[dd.getMonth()], annee: dd.getFullYear(), ...b });
  }
  return out;
}

export const MOIS_COURTS = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc'];
export const MOIS_LONGS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];

// Trimestre : renvoie les 3 mois du trimestre contenant la date de référence.
export function trimestreDe(dateISO = nowISO()) {
  const d = new Date(dateISO);
  const q = Math.floor(d.getMonth() / 3);       // 0..3
  const mois = [0, 1, 2].map((k) => {
    const m = q * 3 + k;
    const mk = `${d.getFullYear()}-${String(m + 1).padStart(2, '0')}`;
    return { mois: mk, index: m, label: MOIS_LONGS[m], ...bilanMois(mk) };
  });
  const totaux = mois.reduce((t, m) => ({
    revenu: t.revenu + m.revenu, relance: t.relance + m.relance,
    charges_couvertes: t.charges_couvertes + m.charges_couvertes,
    benefice: t.benefice + m.benefice, unites: t.unites + m.unites,
  }), { revenu: 0, relance: 0, charges_couvertes: 0, benefice: 0, unites: 0 });
  // Tendance : compare bénéfice du 1er vs dernier mois actifs
  const actifs = mois.filter((m) => m.unites > 0);
  let tendance = 0;
  if (actifs.length >= 2) tendance = actifs[actifs.length - 1].benefice - actifs[0].benefice;
  return { numero: q + 1, annee: d.getFullYear(), mois, totaux, tendance, viable: totaux.benefice > 0 };
}

// Seuil de rentabilité d'un produit : nb d'unités/mois pour couvrir les charges.
export function seuilRentabilite(produit) {
  const m = margeUnitaire(produit);
  if (m <= 0) return Infinity;
  return Math.ceil(chargesMensuellesTotal() / m);
}

// =====================================================================
//  STATISTIQUES & ANALYSE (rapport + conseils, 100% déterministe)
// =====================================================================
function sommeVentes(ventes) {
  let revenu = 0, cout = 0, unites = 0;
  for (const v of ventes) { revenu += (v.qte || 0) * (v.prix_unitaire || 0); cout += (v.qte || 0) * (v.cout_unitaire || 0); unites += (v.qte || 0); }
  return { revenu, cout, marge: revenu - cout, unites, nbTx: ventes.length };
}

// KPIs du mois + cumul global.
export function statistiques(mk = currentMonthKey()) {
  const vm = ventesDuMois(mk);
  const mois = sommeVentes(vm);
  const b = bilanMois(mk);
  const all = sommeVentes(state.ventes);
  return {
    mois: {
      ...mois, benefice: b.benefice, charges_couvertes: b.charges_couvertes, charges_cible: b.charges_cible,
      tauxMarge: mois.revenu ? mois.marge / mois.revenu : 0,
      panierMoyen: mois.nbTx ? mois.revenu / mois.nbTx : 0,
    },
    global: { ...all, tauxMarge: all.revenu ? all.marge / all.revenu : 0 },
  };
}

// Contribution de chaque produit (cumul) : marge apportée + part du CA.
export function contributionProduits() {
  const total = sommeVentes(state.ventes).revenu || 1;
  return getProduits({ withArchived: true }).map((p) => {
    const s = sommeVentes(state.ventes.filter((v) => v.produit_id === p.id));
    return { id: p.id, nom: p.nom, revenu: s.revenu, margeContrib: s.marge, unites: s.unites, part: s.revenu / total };
  }).filter((x) => x.unites > 0).sort((a, b) => b.margeContrib - a.margeContrib);
}

const PRIO_RANG = { haute: 0, moyenne: 1, basse: 2, info: 3 };

// Rapport automatique : santé, évolution, conseils, points forts.
export function analyseBusiness() {
  const produits = getProduits();
  if (state.ventes.length === 0) {
    return {
      sante: 'demarrage', score: 0, etat: ['Aucune vente enregistrée pour l’instant.'],
      evolution: null, forts: [],
      conseils: [{ priorite: 'info', titre: 'Enregistre tes premières ventes', detail: 'Dès que tu saisis des ventes, Boussole analyse ta rentabilité et te conseille automatiquement.' }],
    };
  }
  const serie = serieMensuelle(6);
  const actifs = serie.filter((m) => m.unites > 0);
  const cur = serie[serie.length - 1];
  const all = sommeVentes(state.ventes);
  const taux = all.revenu ? all.marge / all.revenu : 0;
  const charges = chargesMensuellesTotal();
  const b = bilanMois();
  const contrib = contributionProduits();
  const conseils = [], forts = [];

  // Évolution (dernier mois actif vs précédent mois actif)
  let evolution = null;
  if (actifs.length >= 2) {
    const a = actifs[actifs.length - 2], z = actifs[actifs.length - 1];
    const diff = z.benefice - a.benefice;
    const pct = a.benefice !== 0 ? diff / Math.abs(a.benefice) : (z.benefice > 0 ? 1 : 0);
    evolution = { sens: diff > 0 ? 'hausse' : (diff < 0 ? 'baisse' : 'stable'), diff, pct, moisFrom: a.label, moisTo: z.label, from: a.benefice, to: z.benefice };
  }

  // --- Conseils (dérivés des vrais chiffres) ---
  produits.filter((p) => margeUnitaire(p) < 0).forEach((p) => conseils.push({
    priorite: 'haute', titre: `« ${p.nom} » se vend à perte`,
    detail: `Son coût (${formatF(coutRevient(p))}) dépasse son prix (${formatF(p.prix_vente)}). Augmente le prix d’au moins ${formatF(Math.abs(margeUnitaire(p)))} ou réduis les coûts.`,
  }));
  if (all.revenu > 0 && taux < 0.15) conseils.push({
    priorite: 'moyenne', titre: 'Marges serrées',
    detail: `Ta marge moyenne est de ${Math.round(taux * 100)}%. Vise 20 à 30 % en ajustant tes prix ou en négociant tes coûts d’achat.`,
  });
  if (b.charges_cible > 0 && b.charges_reste > 0 && cur.unites > 0) conseils.push({
    priorite: 'moyenne', titre: 'Charges du mois pas encore couvertes',
    detail: `Il te manque ${formatF(b.charges_reste)} de marge pour couvrir tes charges (${formatF(b.charges_cible)}) ce mois-ci.`,
  });
  if (evolution && evolution.sens === 'baisse') conseils.push({
    priorite: 'moyenne', titre: 'Bénéfice en recul',
    detail: `Ton bénéfice a baissé de ${formatF(Math.abs(evolution.diff))} entre ${evolution.moisFrom} et ${evolution.moisTo}. Relance tes ventes ou vérifie si un coût a augmenté.`,
  });
  if (contrib.length > 1 && contrib[0]) {
    const top = [...contrib].sort((a, z) => z.part - a.part)[0];
    if (top.part > 0.8) conseils.push({
      priorite: 'basse', titre: 'Dépendance à un seul produit',
      detail: `« ${top.nom} » représente ${Math.round(top.part * 100)}% de ton chiffre d’affaires. Diversifier sécurise ton activité.`,
    });
  }
  if (charges > 0 && cur.unites > 0 && charges > cur.marge) conseils.push({
    priorite: 'moyenne', titre: 'Charges fixes lourdes',
    detail: `Tes charges fixes (${formatF(charges)}/mois) dépassent ta marge du mois (${formatF(cur.marge)}). Réduis-les ou augmente le volume de ventes.`,
  });

  // --- Points forts ---
  if (evolution && evolution.sens === 'hausse') forts.push(`Bénéfice en hausse de ${Math.round(evolution.pct * 100)}% (${evolution.moisFrom} → ${evolution.moisTo}).`);
  if (cur.benefice > 0) forts.push(`Tu dégages du bénéfice ce mois : ${formatF(cur.benefice)}.`);
  if (taux >= 0.3) forts.push(`Bonne marge moyenne (${Math.round(taux * 100)}%).`);
  if (contrib[0] && contrib[0].margeContrib > 0) forts.push(`« ${contrib[0].nom} » est ton moteur (${formatF(contrib[0].margeContrib)} de marge apportée).`);

  // --- Score de santé /100 ---
  let score = 0;
  score += Math.max(0, Math.min(40, (taux / 0.3) * 40));                                   // marge (40)
  score += b.charges_cible > 0 ? (b.charges_couvertes / b.charges_cible) * 20 : 20;         // charges (20)
  score += evolution ? Math.max(0, Math.min(20, 10 + evolution.pct * 20)) : 10;             // évolution (20)
  score += produits.some((p) => margeUnitaire(p) < 0) ? 0 : 10;                             // pas de perte (10)
  score += cur.unites > 0 ? 10 : 0;                                                         // activité (10)
  score = Math.round(Math.max(0, Math.min(100, score)));
  const sante = score >= 70 ? 'bonne' : score >= 45 ? 'moyenne' : 'fragile';

  // --- État actuel ---
  const etat = [];
  etat.push(cur.unites > 0
    ? `Ce mois : ${cur.unites} unité${cur.unites > 1 ? 's' : ''} vendue${cur.unites > 1 ? 's' : ''}, ${formatF(cur.revenu)} de chiffre d’affaires.`
    : 'Aucune vente enregistrée ce mois-ci pour l’instant.');
  etat.push(cur.benefice >= 0 ? `Bénéfice net du mois : ${formatF(cur.benefice)}.` : `Tu es en perte de ${formatF(-cur.benefice)} ce mois.`);
  if (evolution && evolution.sens !== 'stable') etat.push(`Comparé à ${evolution.moisFrom}, ton bénéfice ${evolution.sens === 'hausse' ? 'progresse' : 'recule'} de ${formatF(Math.abs(evolution.diff))}.`);

  // Alerte : dépense anormalement élevée
  const alerts = alertesDepenses();
  if (alerts.length) {
    const a = alerts[0];
    conseils.push({
      priorite: 'moyenne', titre: 'Dépense inhabituelle repérée',
      detail: `« ${a.libelle} » (${formatF(a.montant)}) dépasse largement ta moyenne « ${a.categorie} » (~${formatF(a.moyenne)}). Vérifie que c’est normal.`,
    });
  }

  conseils.sort((a, z) => PRIO_RANG[a.priorite] - PRIO_RANG[z.priorite]);
  return { sante, score, etat, evolution, conseils, forts };
}

// =====================================================================
//  MOTEUR MULTI-PÉRIODES (dashboard : heure / jour / semaine / mois / année)
// =====================================================================
export const JOURS_COURTS = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'];
export const JOURS_LONGS = ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'];
const DAY_MS = 86400000;
const startOfDay = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate());
const addDays = (d, n) => new Date(d.getFullYear(), d.getMonth(), d.getDate() + n);
const daysInMonthOf = (d) => new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate();

// Décrit une période + ses sous-buckets + la période précédente (comparaison).
export function periodInfo(gran = 'mois', offset = 0) {
  const now = new Date();
  const buckets = [];
  const push = (s, e, label, show = true) => buckets.push({ start: s, end: e, label: show ? label : '' });
  let start, end, label, unit, prev;

  if (gran === 'jour') {
    const day = addDays(startOfDay(now), offset);
    start = day; end = addDays(day, 1); unit = 'heure';
    for (let hh = 0; hh < 24; hh++) {
      const s = new Date(day.getFullYear(), day.getMonth(), day.getDate(), hh);
      push(s, new Date(day.getFullYear(), day.getMonth(), day.getDate(), hh + 1), hh + 'h', hh % 3 === 0);
    }
    label = offset === 0 ? "Aujourd'hui" : (offset === -1 ? 'Hier' : day.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' }));
    prev = { start: addDays(day, -1), end: day, label: 'la veille' };
  } else if (gran === 'semaine') {
    const base = addDays(startOfDay(now), offset * 7);
    const mon = addDays(base, -((base.getDay() + 6) % 7));
    start = mon; end = addDays(mon, 7); unit = 'jour';
    for (let i = 0; i < 7; i++) { const s = addDays(mon, i); push(s, addDays(s, 1), JOURS_COURTS[s.getDay()]); }
    label = offset === 0 ? 'Cette semaine' : `Semaine du ${mon.getDate()} ${MOIS_COURTS[mon.getMonth()]}`;
    prev = { start: addDays(mon, -7), end: mon, label: 'semaine précédente' };
  } else if (gran === 'annee') {
    const y = now.getFullYear() + offset;
    start = new Date(y, 0, 1); end = new Date(y + 1, 0, 1); unit = 'mois';
    for (let m = 0; m < 12; m++) push(new Date(y, m, 1), new Date(y, m + 1, 1), MOIS_COURTS[m]);
    label = String(y);
    prev = { start: new Date(y - 1, 0, 1), end: new Date(y, 0, 1), label: String(y - 1) };
  } else {
    gran = 'mois';
    const ref = new Date(now.getFullYear(), now.getMonth() + offset, 1);
    const y = ref.getFullYear(), m = ref.getMonth(), dim = daysInMonthOf(ref);
    start = new Date(y, m, 1); end = new Date(y, m + 1, 1); unit = 'jour';
    for (let d = 1; d <= dim; d++) push(new Date(y, m, d), new Date(y, m, d + 1), String(d), d === 1 || d % 5 === 0 || d === dim);
    label = `${MOIS_LONGS[m]} ${y}`;
    prev = { start: new Date(y, m - 1, 1), end: new Date(y, m, 1), label: MOIS_LONGS[(m + 11) % 12] };
  }
  return { gran, offset, unit, start, end, label, buckets, prev };
}

function ventesEntre(start, end) {
  const a = start.getTime(), b = end.getTime();
  return state.ventes.filter((v) => { const t = new Date(v.date).getTime(); return t >= a && t < b; });
}
function depensesEntre(start, end) {
  const a = start.getTime(), b = end.getTime();
  return state.depenses.filter((d) => { const t = new Date(d.date).getTime(); return t >= a && t < b; });
}
function sommeDepenses(list) { return list.reduce((s, d) => s + (Number(d.montant) || 0), 0); }
// dépenses d'exploitation (hors réassort/stock) : celles qui rognent le bénéfice
function depensesExploit(list) { return sommeDepenses(list.filter((d) => d.categorie !== RESTOCK_CAT)); }

// Quote-part de charges fixes pour un intervalle (au prorata des jours, sans compter le futur).
function chargesProrataEntre(start, end, nowT = Date.now()) {
  const cm = chargesMensuellesTotal();
  if (cm <= 0) return 0;
  const endT = Math.min(end.getTime(), nowT);
  let curT = start.getTime(), total = 0;
  while (curT < endT) {
    const cur = new Date(curT);
    const mEnd = new Date(cur.getFullYear(), cur.getMonth() + 1, 1).getTime();
    const segEnd = Math.min(endT, mEnd);
    total += cm * ((segEnd - curT) / DAY_MS) / daysInMonthOf(cur);
    curT = mEnd;
  }
  return total;
}

function periodTotals(start, end, nowT) {
  const s = sommeVentes(ventesEntre(start, end));
  const charges = chargesProrataEntre(start, end, nowT);
  const dep = depensesEntre(start, end);
  const depExploit = depensesExploit(dep);
  return {
    revenu: s.revenu, cout: s.cout, marge: s.marge, unites: s.unites, nbTx: s.nbTx,
    charges, depenses: sommeDepenses(dep), depensesExploit: depExploit,
    benefice: s.marge - charges - depExploit,
    tauxMarge: s.revenu ? s.marge / s.revenu : 0,
    panierMoyen: s.nbTx ? s.revenu / s.nbTx : 0,
  };
}

function makeDelta(cur, prv) {
  const diff = cur - prv;
  const pct = prv !== 0 ? diff / Math.abs(prv) : (cur > 0 ? 1 : (cur < 0 ? -1 : 0));
  return { diff, pct, sens: diff > 0 ? 'hausse' : (diff < 0 ? 'baisse' : 'stable') };
}

// Série complète prête pour le dashboard : buckets + totaux + comparaison + enveloppes.
export function serieDashboard(gran = 'mois', offset = 0) {
  const P = periodInfo(gran, offset);
  const nowT = Date.now();
  const buckets = P.buckets.map((bk) => {
    const s = sommeVentes(ventesEntre(bk.start, bk.end));
    const future = bk.start.getTime() > nowT;
    const charges = future ? 0 : chargesProrataEntre(bk.start, bk.end, nowT);
    const depExploit = future ? 0 : depensesExploit(depensesEntre(bk.start, bk.end));
    return { label: bk.label, revenu: s.revenu, cout: s.cout, marge: s.marge, unites: s.unites, nbTx: s.nbTx, charges, depenses: depExploit, benefice: s.marge - charges - depExploit, future };
  });
  const totals = periodTotals(P.start, P.end, nowT);
  // Comparaison équitable : si la période est EN COURS, on compare à la MÊME durée écoulée
  // de la période précédente (mois-à-date vs mêmes jours du mois d'avant), pas au total complet.
  const elapsed = Math.min(nowT, P.end.getTime()) - P.start.getTime();
  const prevEnd = P.offset === 0 ? new Date(P.prev.start.getTime() + elapsed) : P.prev.end;
  const prev = periodTotals(P.prev.start, prevEnd, nowT);
  const target = totals.charges;
  const env2 = Math.max(0, Math.min(totals.marge, target));
  const depExploit = totals.depensesExploit;
  const enveloppes = {
    revenu: totals.revenu, relance: totals.cout, marge: totals.marge,
    charges_cible: target, charges_couvertes: env2, charges_reste: Math.max(0, target - env2),
    depenses: depExploit, benefice: totals.marge - env2 - depExploit, a_perte: totals.marge < 0,
  };
  return {
    gran: P.gran, offset: P.offset, unit: P.unit, label: P.label, prevLabel: P.prev.label,
    buckets, totals, prev, enveloppes,
    deltas: {
      revenu: makeDelta(totals.revenu, prev.revenu),
      benefice: makeDelta(totals.benefice, prev.benefice),
      marge: makeDelta(totals.marge, prev.marge),
      unites: makeDelta(totals.unites, prev.unites),
      panierMoyen: makeDelta(totals.panierMoyen, prev.panierMoyen),
      tauxMarge: makeDelta(totals.tauxMarge, prev.tauxMarge),
    },
  };
}

// Classement des produits sur la période, avec mini-série (sparkline) par bucket.
export function topProduitsPeriode(gran = 'mois', offset = 0, n = 6) {
  const P = periodInfo(gran, offset);
  const ventes = ventesEntre(P.start, P.end);
  const totRev = ventes.reduce((a, v) => a + v.qte * v.prix_unitaire, 0) || 1;
  const bkRanges = P.buckets.map((b) => [b.start.getTime(), b.end.getTime()]);
  return getProduits({ withArchived: true }).map((p) => {
    const vs = ventes.filter((v) => v.produit_id === p.id);
    const s = sommeVentes(vs);
    const spark = bkRanges.map(([a, b]) => vs.filter((v) => { const t = new Date(v.date).getTime(); return t >= a && t < b; }).reduce((x, v) => x + v.qte * v.prix_unitaire, 0));
    return { id: p.id, nom: p.nom, modele: p.modele, revenu: s.revenu, marge: s.marge, unites: s.unites, part: s.revenu / totRev, spark };
  }).filter((x) => x.unites > 0).sort((a, b) => b.revenu - a.revenu).slice(0, n);
}

// Gravité des flops : du plus urgent (on perd de l'argent) au moins urgent (se vend peu).
const FLOP_RANG = { perte: 0, dormant: 1, stockdort: 2, faible: 3 };

// Palmarès de la période : les produits qui CARTONNENT (tops) ET ceux qui S'ÉCOULENT MAL (flops).
// Un flop = vendu à perte · jamais vendu (dormant) · stock qui dort · nettement sous la moyenne.
// Chaque flop porte une raison courte + un conseil d'action, pour que la patronne sache quoi faire.
export function palmaresProduits(gran = 'mois', offset = 0, n = 5) {
  const P = periodInfo(gran, offset);
  const startT = P.start.getTime();
  const ventes = ventesEntre(P.start, P.end);
  const prods = getProduits();
  const totRev = ventes.reduce((a, v) => a + (v.qte || 0) * (v.prix_unitaire || 0), 0) || 1;

  const rows = prods.map((p) => {
    const s = sommeVentes(ventes.filter((v) => v.produit_id === p.id));
    const info = getStockInfo(p);
    return {
      id: p.id, nom: p.nom, modele: p.modele,
      unites: s.unites, revenu: s.revenu, marge: s.marge,
      margeU: margeUnitaire(p), suivi: info.suivi, stock: info.suivi ? info.qte : null,
      part: s.revenu / totRev, nouveau: new Date(p.created_at || 0).getTime() >= startT,
    };
  });

  const vendus = rows.filter((r) => r.unites > 0);
  const revMoyen = vendus.length ? vendus.reduce((a, r) => a + r.revenu, 0) / vendus.length : 0;
  const tops = vendus.slice().sort((a, b) => b.revenu - a.revenu || b.unites - a.unites).slice(0, n);

  const flops = rows.map((r) => {
    let statut = null, raison = '', conseil = '';
    if (r.unites > 0 && r.margeU < 0) {
      statut = 'perte'; raison = 'Vendu à perte';
      conseil = `Chaque vente te fait perdre ${formatF(Math.abs(r.margeU))}. Monte le prix ou baisse le coût.`;
    } else if (r.unites === 0 && !r.nouveau) {
      statut = 'dormant'; raison = 'Aucune vente';
      conseil = (r.suivi && r.stock > 0)
        ? `${formatNombre(r.stock)} en stock qui ne bougent pas. Mets-le en avant ou fais une promo.`
        : 'Rien vendu sur la période. Propose-le à tes clients ou revois son prix.';
    } else if (r.suivi && r.stock > 0 && r.unites <= Math.max(1, Math.round(r.stock * 0.15))) {
      statut = 'stockdort'; raison = 'Stock qui dort';
      conseil = `${formatNombre(r.stock)} en stock pour seulement ${formatNombre(r.unites)} vendu${r.unites > 1 ? 's' : ''} : ton argent est immobilisé.`;
    } else if (r.unites > 0 && revMoyen > 0 && r.revenu < revMoyen * 0.5) {
      statut = 'faible'; raison = 'Se vend peu';
      conseil = 'Bien en dessous de tes autres produits. Une promo ou une meilleure mise en avant peut aider.';
    }
    return { ...r, statut, raison, conseil };
  }).filter((r) => r.statut)
    .sort((a, b) => (FLOP_RANG[a.statut] - FLOP_RANG[b.statut]) || (a.revenu - b.revenu) || (a.unites - b.unites))
    .slice(0, n);

  return { label: P.label, tops, flops, nbProduits: prods.length, nbVendus: vendus.length };
}

// ---------- Objectif de bénéfice mensuel ----------
export function getObjectif() { return Number(state.profil.objectif_benefice) || 0; }
export function setObjectif(v) { setProfil({ objectif_benefice: Math.max(0, Math.round(Number(v) || 0)) }); }

// ---------- Caisse + résumé du jour (vue trésorerie) ----------
// Caisse = fond de départ + tout l'encaissement (ventes) − toutes les sorties (dépenses).
export function soldeCaisse() {
  const encaisse = state.ventes.reduce((s, v) => s + (v.qte || 0) * (v.prix_unitaire || 0), 0);
  const achats = state.achats.filter((a) => a.statut === 'paye').reduce((s, a) => s + achatTotal(a), 0);
  return getSoldeInitial() + encaisse - sommeDepenses(state.depenses) - achats;
}
// Résumé d'AUJOURD'HUI (toujours le jour courant, indépendant de la période choisie).
export function resumeJour() {
  const now = new Date();
  const s0 = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const s1 = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
  const v = sommeVentes(ventesEntre(s0, s1));
  const dep = depensesEntre(s0, s1);
  const depExploit = depensesExploit(dep);
  const charges = chargesProrataEntre(s0, s1, Date.now());
  return {
    ca: v.revenu, cout: v.cout, marge: v.marge, unites: v.unites, nbTx: v.nbTx,
    depenses: sommeDepenses(dep), depensesExploit: depExploit, charges,
    benefice: v.marge - depExploit - charges,   // vrai bénéfice du jour (marge − dépenses expl. − quote-part charges)
    caisse: soldeCaisse(),
  };
}

// ---------- Historique des ventes : recherche (date / produit / texte) + regroupé par jour ----------
export function historiqueVentes({ from = '', to = '', produitId = '', q = '', mode = '', vendeur = '' } = {}) {
  const fromT = from ? new Date(from + 'T00:00:00').getTime() : -Infinity;
  const toT = to ? new Date(to + 'T23:59:59.999').getTime() : Infinity;
  const ql = (q || '').trim().toLowerCase();
  const rows = state.ventes.filter((v) => {
    const t = new Date(v.date).getTime();
    if (t < fromT || t > toT) return false;
    if (produitId && v.produit_id !== produitId) return false;
    if (mode && (v.mode || 'especes') !== mode) return false;
    if (vendeur && (v.vendeur || '') !== vendeur) return false;
    if (ql) { const p = getProduit(v.produit_id); if (!p || !p.nom.toLowerCase().includes(ql)) return false; }
    return true;
  }).map((v) => {
    const p = getProduit(v.produit_id);
    return {
      id: v.id, produit_id: v.produit_id, nom: p ? p.nom : 'Produit supprimé', modele: p ? p.modele : '',
      date: v.date, qte: v.qte, prix_unitaire: v.prix_unitaire, mode: v.mode || 'especes', vendeur: v.vendeur || '', ticket: v.ticket || '',
      total: (v.qte || 0) * (v.prix_unitaire || 0), marge: (v.qte || 0) * ((v.prix_unitaire || 0) - (v.cout_unitaire || 0)),
    };
  }).sort((a, b) => new Date(b.date) - new Date(a.date));
  const jours = [], map = {};
  for (const r of rows) {
    const dd = new Date(r.date);   // regroupement par jour LOCAL (pas UTC)
    const key = `${dd.getFullYear()}-${String(dd.getMonth() + 1).padStart(2, '0')}-${String(dd.getDate()).padStart(2, '0')}`;
    if (!map[key]) { map[key] = { jour: key, total: 0, marge: 0, unites: 0, nb: 0, lignes: [] }; jours.push(map[key]); }
    const g = map[key]; g.lignes.push(r); g.total += r.total; g.marge += r.marge; g.unites += r.qte; g.nb += 1;
  }
  return {
    jours,
    total: rows.reduce((s, r) => s + r.total, 0),
    marge: rows.reduce((s, r) => s + r.marge, 0),
    unites: rows.reduce((s, r) => s + r.qte, 0),
    nb: rows.length,
  };
}

// ---------- Historique des dépenses : filtres + groupé/jour + répartition par catégorie ----------
export function historiqueDepenses({ from = '', to = '', categorie = '', q = '' } = {}) {
  const fromT = from ? new Date(from + 'T00:00:00').getTime() : -Infinity;
  const toT = to ? new Date(to + 'T23:59:59.999').getTime() : Infinity;
  const ql = (q || '').trim().toLowerCase();
  const rows = state.depenses.filter((d) => {
    const t = new Date(d.date).getTime();
    if (t < fromT || t > toT) return false;
    if (categorie && d.categorie !== categorie) return false;
    if (ql && !((d.libelle || '').toLowerCase().includes(ql) || (d.categorie || '').toLowerCase().includes(ql))) return false;
    return true;
  }).sort((a, b) => new Date(b.date) - new Date(a.date));
  const jours = [], map = {}, cats = {};
  for (const r of rows) {
    const dd = new Date(r.date);
    const key = `${dd.getFullYear()}-${String(dd.getMonth() + 1).padStart(2, '0')}-${String(dd.getDate()).padStart(2, '0')}`;
    if (!map[key]) { map[key] = { jour: key, total: 0, nb: 0, lignes: [] }; jours.push(map[key]); }
    const g = map[key]; g.lignes.push(r); g.total += (Number(r.montant) || 0); g.nb += 1;
    cats[r.categorie] = (cats[r.categorie] || 0) + (Number(r.montant) || 0);
  }
  const total = rows.reduce((s, r) => s + (Number(r.montant) || 0), 0);
  const parCategorie = Object.keys(cats)
    .map((c) => ({ categorie: c, total: cats[c], part: total ? cats[c] / total : 0 }))
    .sort((a, b) => b.total - a.total);
  return { jours, total, nb: rows.length, parCategorie };
}

// ---------- Prévisions de trésorerie (projection fin de mois, à partir du rythme récent) ----------
export function previsions() {
  const now = new Date();
  const jour0 = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const fenetre = 14;
  const debut = new Date(jour0); debut.setDate(jour0.getDate() - (fenetre - 1));
  const fin = new Date(jour0); fin.setDate(jour0.getDate() + 1);
  const v = sommeVentes(ventesEntre(debut, fin));
  const depExploit = depensesExploit(depensesEntre(debut, fin));
  const depTotal = sommeDepenses(depensesEntre(debut, fin));
  const chargesF = chargesProrataEntre(debut, fin, Date.now());
  const avgJourBenef = (v.marge - depExploit - chargesF) / fenetre;
  const avgJourCash = (v.revenu - depTotal) / fenetre;
  const joursRestants = Math.max(0, daysInMonthOf(now) - now.getDate());
  const benefMois = serieDashboard('mois', 0).totals.benefice;
  const caisse = soldeCaisse();
  return {
    avgJour: avgJourBenef, avgJourCash, joursRestants,
    benefMoisActuel: benefMois, benefFinMois: benefMois + avgJourBenef * joursRestants,
    caisse, caisseFinMois: caisse + avgJourCash * joursRestants,
    actif: v.unites > 0 || depTotal > 0,
    tendance: avgJourBenef > 0 ? 'hausse' : (avgJourBenef < 0 ? 'baisse' : 'stable'),
  };
}

// ---------- Alertes : dépenses anormalement élevées vs la moyenne de leur catégorie ----------
export function alertesDepenses({ jours = 30, facteur = 2.5 } = {}) {
  const debutT = Date.now() - jours * DAY_MS;
  const recent = state.depenses.filter((d) => new Date(d.date).getTime() >= debutT);
  const parCat = {};
  recent.forEach((d) => { const c = d.categorie || 'Divers'; (parCat[c] = parCat[c] || []).push(Number(d.montant) || 0); });
  const moy = {};
  Object.keys(parCat).forEach((c) => { const a = parCat[c]; moy[c] = a.reduce((s, x) => s + x, 0) / a.length; });
  const alerts = [];
  recent.forEach((d) => {
    const c = d.categorie || 'Divers'; const m = Number(d.montant) || 0;
    if (moy[c] && parCat[c].length >= 3 && m > moy[c] * facteur && m >= 2000) {
      alerts.push({ id: d.id, libelle: d.libelle || c, categorie: c, montant: m, moyenne: Math.round(moy[c]), date: d.date });
    }
  });
  return alerts.sort((a, b) => new Date(b.date) - new Date(a.date));
}

// ---------- Crédits (ventes à crédit : clients qui doivent) ----------
export function getCredits() { return state.credits; }
export function getCredit(id) { return state.credits.find((c) => c.id === id) || null; }
export function addCredit({ client, tel, montant, echeance, note }) {
  const c = { id: uid(), client: (client || '').trim(), tel: (tel || '').trim(), montant: Number(montant) || 0, paye: false, paiements: [], date: nowISO(), echeance: echeance || '', note: (note || '').trim(), created_at: nowISO() };
  state.credits.push(c); persistLocal(); pushRemote('credits', c); emit(); return c;
}
export function updateCredit(id, patch) {
  const c = state.credits.find((x) => x.id === id); if (!c) return;
  Object.assign(c, patch); if (patch.montant != null) c.montant = Number(patch.montant) || 0;
  persistLocal(); pushRemote('credits', c); emit();
}
export function deleteCredit(id) { const c = getCredit(id); if (c) logAudit('suppression', 'dette', `${c.client || 'Client'} · ${formatF(c.montant)}`); state.credits = state.credits.filter((x) => x.id !== id); persistLocal(); delRemote('credits', id); emit(); }
// Paiement partiel : un crédit garde une liste de versements ; « payé » = reste ≤ 0.
function sommePaiements(c) { return (c.paiements || []).reduce((s, p) => s + (Number(p.montant) || 0), 0); }
export function creditReste(c) { if (c.paye && !(c.paiements || []).length) return 0; return Math.max(0, (Number(c.montant) || 0) - sommePaiements(c)); }
export function creditPaye(c) { return creditReste(c) <= 0; }
export function addPaiement(id, montant) {
  const c = state.credits.find((x) => x.id === id); if (!c) return;
  montant = Math.max(0, Number(montant) || 0); if (!montant) return;
  if (!Array.isArray(c.paiements)) c.paiements = [];
  c.paiements.push({ montant, date: nowISO() });
  c.paye = creditReste(c) <= 0;   // « soldé » synchronisé
  persistLocal(); pushRemote('credits', c); emit();
}
export function soldeCredit(id) {   // encaisse tout le reste d'un coup
  const c = state.credits.find((x) => x.id === id); if (!c) return;
  const r = creditReste(c);
  if (r > 0) addPaiement(id, r);
  else { c.paye = true; persistLocal(); pushRemote('credits', c); emit(); }
}
export function creditsSummary() {
  const impayes = state.credits.filter((c) => creditReste(c) > 0)
    .sort((a, b) => (a.echeance || 'z').localeCompare(b.echeance || 'z') || new Date(a.date) - new Date(b.date));
  return { impayes, total: impayes.reduce((s, c) => s + creditReste(c), 0), nb: impayes.length, nbTotal: state.credits.length };
}

// ---------- Documents (factures & devis pour les clients) ----------
// Une facture/devis « propre » : identité vendeur (dont IFU/RCCM), client, numéro,
// lignes détaillées, remise, TVA optionnelle, acompte, total + montant en lettres.
export function getDocuments() {
  return state.documents.slice().sort((a, b) =>
    (b.date || '').localeCompare(a.date || '') || (new Date(b.created_at || 0) - new Date(a.created_at || 0)));
}
export function getDocument(id) { return state.documents.find((d) => d.id === id) || null; }

export function nextDocNumero(type) {
  const year = new Date().getFullYear();
  const prefix = type === 'devis' ? 'DEV' : 'FAC';
  const re = new RegExp('^' + prefix + '-' + year + '-(\\d+)$');
  let max = 0;
  state.documents.forEach((d) => { const m = (d.numero || '').match(re); if (m) max = Math.max(max, parseInt(m[1], 10)); });
  return `${prefix}-${year}-${String(max + 1).padStart(4, '0')}`;
}

function normLignes(lignes) {
  return (lignes || []).map((l) => ({
    designation: (l.designation || '').trim(),
    qte: Number(l.qte) || 0,
    pu: Number(l.pu) || 0,
  }));
}
function normClient(c) {
  return { nom: (c && c.nom || '').trim(), tel: (c && c.tel || '').trim(), adresse: (c && c.adresse || '').trim() };
}

export function addDocument(doc = {}) {
  const type = doc.type === 'devis' ? 'devis' : 'facture';
  const d = {
    id: uid(), type,
    numero: doc.numero || nextDocNumero(type),
    date: doc.date || _ymd2(new Date()),
    echeance: doc.echeance || '',
    client: normClient(doc.client),
    lignes: normLignes(doc.lignes),
    remise: Number(doc.remise) || 0,
    tva_taux: Number(doc.tva_taux) || 0,
    acompte: Number(doc.acompte) || 0,
    notes: (doc.notes || '').trim(),
    statut: doc.statut || (type === 'devis' ? 'en_attente' : 'impayee'),
    created_at: nowISO(),
  };
  state.documents.push(d);
  persistLocal(); pushRemote('documents', d); emit();
  return d;
}
export function updateDocument(id, patch = {}) {
  const d = state.documents.find((x) => x.id === id); if (!d) return null;
  Object.assign(d, patch);
  if (patch.lignes) d.lignes = normLignes(patch.lignes);
  if (patch.client) d.client = normClient(Object.assign({}, d.client, patch.client));
  ['remise', 'tva_taux', 'acompte'].forEach((k) => { if (patch[k] != null) d[k] = Number(patch[k]) || 0; });
  persistLocal(); pushRemote('documents', d); emit();
  return d;
}
export function deleteDocument(id) {
  state.documents = state.documents.filter((d) => d.id !== id);
  persistLocal(); delRemote('documents', id); emit();
}

export function documentTotals(doc) {
  const sousTotal = (doc.lignes || []).reduce((s, l) => s + (Number(l.qte) || 0) * (Number(l.pu) || 0), 0);
  const remise = Math.min(Number(doc.remise) || 0, sousTotal);
  const baseHT = sousTotal - remise;
  const tva = Math.round(baseHT * ((Number(doc.tva_taux) || 0) / 100));
  const total = baseHT + tva;
  const acompte = Math.min(Number(doc.acompte) || 0, total);
  const net = total - acompte;
  return { sousTotal, remise, baseHT, tva, total, acompte, net };
}
export function documentsSummary() {
  const docs = state.documents;
  const factures = docs.filter((d) => d.type === 'facture');
  const impayees = factures.filter((d) => d.statut !== 'payee');
  const totalImpaye = impayees.reduce((s, d) => s + documentTotals(d).net, 0);
  const encaisse = factures.filter((d) => d.statut === 'payee').reduce((s, d) => s + documentTotals(d).total, 0);
  return { total: docs.length, nbFactures: factures.length, nbDevis: docs.length - factures.length, nbImpayees: impayees.length, totalImpaye, encaisse };
}

// Montant en toutes lettres (français) — mention classique d'une facture normalisée.
export function montantEnLettres(n) {
  n = Math.round(Math.abs(Number(n) || 0));
  if (n === 0) return 'zéro';
  const U = ['', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept', 'huit', 'neuf', 'dix', 'onze', 'douze',
    'treize', 'quatorze', 'quinze', 'seize', 'dix-sept', 'dix-huit', 'dix-neuf'];
  const DZ = ['', '', 'vingt', 'trente', 'quarante', 'cinquante', 'soixante', 'soixante', 'quatre-vingt', 'quatre-vingt'];
  // inv = groupe suivi de « mille » (invariable) : « quatre-vingt mille », « cinq cent mille ».
  function deux(x, inv) {
    if (x < 20) return U[x];
    const d = Math.floor(x / 10), u = x % 10;
    if (d === 7 || d === 9) return DZ[d] + (d === 7 && u === 1 ? ' et ' : '-') + U[10 + u];
    if (u === 1 && d !== 8) return DZ[d] + ' et un';
    if (u > 0) return DZ[d] + '-' + U[u];
    return DZ[d] + (d === 8 && !inv ? 's' : '');
  }
  function trois(x, inv) {
    const c = Math.floor(x / 100), r = x % 100; let s = '';
    if (c > 0) s = (c > 1 ? U[c] + ' ' : '') + 'cent' + (c > 1 && r === 0 && !inv ? 's' : '');
    if (r > 0) s += (s ? ' ' : '') + deux(r, inv);
    return s;
  }
  const g = Math.floor(n / 1e9), m = Math.floor((n % 1e9) / 1e6), k = Math.floor((n % 1e6) / 1000), r = n % 1000;
  const parts = [];
  if (g > 0) parts.push(trois(g, false) + ' milliard' + (g > 1 ? 's' : ''));
  if (m > 0) parts.push(trois(m, false) + ' million' + (m > 1 ? 's' : ''));
  if (k > 0) parts.push((k === 1 ? '' : trois(k, true) + ' ') + 'mille');
  if (r > 0) parts.push(trois(r, false));
  return parts.join(' ').replace(/\s+/g, ' ').trim();
}

// ---------- Stock (inventaire) ----------
// Un produit avec stock === null n'est PAS suivi (services, transformation à la demande…).
export function getStockInfo(p) {
  if (!p) return { suivi: false, qte: 0, seuil: 0, statut: 'non-suivi' };
  const suivi = p.stock !== null && p.stock !== undefined;
  const qte = Number(p.stock) || 0, seuil = Number(p.seuil) || 0;
  let statut = 'non-suivi';
  if (suivi) statut = qte <= 0 ? 'rupture' : (seuil > 0 && qte <= seuil ? 'bas' : 'ok');
  return { suivi, qte, seuil, statut };
}
export function setStock(id, qte) { updateProduit(id, { stock: (qte === '' || qte === null) ? null : Math.max(0, Math.round(Number(qte) || 0)) }); }
export function ajusterStock(id, delta) {
  const p = getProduit(id); if (!p) return;
  const base = (p.stock === null || p.stock === undefined) ? 0 : Number(p.stock) || 0;
  updateProduit(id, { stock: Math.max(0, base + delta) });
}
export function setSeuil(id, seuil) { updateProduit(id, { seuil: Math.max(0, Math.round(Number(seuil) || 0)) }); }
export function stockResume() {
  const prods = getProduits();
  let ruptures = 0, bas = 0, suivis = 0, valeur = 0;
  prods.forEach((p) => { const s = getStockInfo(p); if (s.suivi) { suivis++; valeur += s.qte * (p.prix_vente || 0); if (s.statut === 'rupture') ruptures++; else if (s.statut === 'bas') bas++; } });
  return { ruptures, bas, suivis, total: prods.length, valeur };
}

// ---------- Clients (annuaire dérivé des crédits + factures/devis) ----------
export function normClientKey(nom, tel) { return (tel && String(tel).replace(/[^0-9]/g, '')) || (nom || '').trim().toLowerCase(); }
export function getClients() {
  const map = new Map();
  const touch = (nom, tel) => {
    const k = normClientKey(nom, tel); if (!k) return null;
    if (!map.has(k)) map.set(k, { key: k, id: '', nom: (nom || 'Client').trim(), tel: (tel || '').trim(), adresse: '', note: '', dette: 0, nbCredits: 0, nbDocs: 0, dernier: '', explicit: false });
    const c = map.get(k);
    if (nom && (c.nom === 'Client' || !c.nom)) c.nom = nom.trim();
    if (!c.tel && tel) c.tel = tel.trim();
    return c;
  };
  state.clients.forEach((cl) => { const c = touch(cl.nom, cl.tel); if (!c) return; c.id = cl.id; c.explicit = true; if (cl.nom) c.nom = cl.nom.trim(); if (cl.adresse) c.adresse = cl.adresse; if (cl.note) c.note = cl.note; });
  state.credits.forEach((cr) => { const c = touch(cr.client, cr.tel); if (!c) return; c.nbCredits++; c.dette += creditReste(cr); if ((cr.date || '') > c.dernier) c.dernier = cr.date || ''; });
  state.documents.forEach((d) => { const c = touch(d.client && d.client.nom, d.client && d.client.tel); if (!c) return; c.nbDocs++; if ((d.date || '') > c.dernier) c.dernier = d.date || ''; });
  return [...map.values()].sort((a, b) => b.dette - a.dette || (b.nbDocs + b.nbCredits) - (a.nbDocs + a.nbCredits) || a.nom.localeCompare(b.nom));
}
export function clientByKey(key) { return getClients().find((c) => c.key === key) || null; }
export function clientCredits(key) { return state.credits.filter((c) => normClientKey(c.client, c.tel) === key).sort((a, b) => new Date(b.date) - new Date(a.date)); }
export function clientDocuments(key) { return state.documents.filter((d) => normClientKey(d.client && d.client.nom, d.client && d.client.tel) === key).map((d) => ({ id: d.id, type: d.type, numero: d.numero, date: d.date, total: documentTotals(d).total })).sort((a, b) => (b.date || '').localeCompare(a.date || '')); }
// Annuaire explicite (fiches clients ajoutées à la main)
export function getClientEntry(id) { return state.clients.find((x) => x.id === id) || null; }
export function addClient({ nom, tel, adresse, note } = {}) {
  nom = (nom || '').trim(); const t = (tel || '').trim();
  if (!nom && !t) return null;
  const cl = { id: uid(), nom, tel: t, adresse: (adresse || '').trim(), note: (note || '').trim(), created_at: nowISO() };
  state.clients.push(cl); persistLocal(); pushRemote('clients', cl); emit(); return cl;
}
export function updateClientEntry(id, patch = {}) {
  const cl = state.clients.find((x) => x.id === id); if (!cl) return;
  ['nom', 'tel', 'adresse', 'note'].forEach((k) => { if (patch[k] != null) cl[k] = String(patch[k]).trim(); });
  persistLocal(); pushRemote('clients', cl); emit();
}
export function deleteClientEntry(id) { state.clients = state.clients.filter((x) => x.id !== id); persistLocal(); delRemote('clients', id); emit(); }

// ---------- Recouvrement (jauge : dettes réglées vs total, en tenant compte des versements) ----------
export function recouvrement() {
  const cr = state.credits;
  const total = cr.reduce((s, c) => s + (Number(c.montant) || 0), 0);
  const reste = cr.reduce((s, c) => s + creditReste(c), 0);
  return { total, recouvre: total - reste, reste, taux: total > 0 ? (total - reste) / total : 1, nbDebiteurs: cr.filter((c) => creditReste(c) > 0).length };
}

// ---------- Journal de caisse (N dernières ventes, enrichies) ----------
export function journalCaisse(n = 10) {
  return state.ventes.slice().sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, n).map((v) => {
    const p = getProduit(v.produit_id);
    return { id: v.id, date: v.date, nom: p ? p.nom : 'Produit', qte: v.qte, montant: (Number(v.qte) || 0) * (Number(v.prix_unitaire) || 0) };
  });
}

// ---------- Notifications (alertes agrégées pour la cloche) ----------
export function notifications() {
  const list = [];
  getProduits().forEach((p) => { if (getStockInfo(p).statut === 'rupture') list.push({ type: 'rupture', icon: 'box', text: `${p.nom} — en rupture`, screen: 'stock' }); });
  getProduits().forEach((p) => { const s = getStockInfo(p); if (s.statut === 'bas') list.push({ type: 'bas', icon: 'box', text: `${p.nom} — bientôt épuisé (${s.qte})`, screen: 'stock' }); });
  const today = _ymd2(new Date());
  state.credits.filter((c) => creditReste(c) > 0 && c.echeance && c.echeance < today).forEach((c) => list.push({ type: 'dette', icon: 'alert', text: `${c.client || 'Client'} — échéance dépassée (${formatF(creditReste(c))})`, screen: 'carnet' }));
  state.documents.filter((d) => d.type === 'facture' && d.statut !== 'payee' && d.echeance && d.echeance < today).forEach((d) => list.push({ type: 'facture', icon: 'receipt', text: `Facture ${d.numero} en retard`, screen: 'bilan' }));
  return { list, count: list.length };
}

// ---------- Objectifs multiples (cagnottes / projets : outil, maison…) ----------
export function getObjectifs() {
  return state.objectifs.slice().sort((a, b) => {
    const aa = objectifInfo(a).atteint ? 1 : 0, bb = objectifInfo(b).atteint ? 1 : 0;
    if (aa !== bb) return aa - bb;  // non atteints d'abord
    return (a.echeance || 'z').localeCompare(b.echeance || 'z') || (new Date(a.created_at || 0) - new Date(b.created_at || 0));
  });
}
export function getObjectif2(id) { return state.objectifs.find((o) => o.id === id) || null; }
export function objectifInfo(o) {
  const cible = Math.max(0, Number(o.montant_cible) || 0);
  const actuel = Math.max(0, Number(o.montant_actuel) || 0);
  const taux = cible > 0 ? Math.min(1, actuel / cible) : (actuel > 0 ? 1 : 0);
  return { cible, actuel, reste: Math.max(0, cible - actuel), taux, atteint: cible > 0 && actuel >= cible };
}
export function addObjectif({ titre, icone, montant_cible, montant_actuel = 0, echeance, note } = {}) {
  const o = { id: uid(), titre: (titre || '').trim(), icone: icone || 'target', montant_cible: Math.max(0, Number(montant_cible) || 0), montant_actuel: Math.max(0, Number(montant_actuel) || 0), echeance: echeance || '', note: (note || '').trim(), created_at: nowISO() };
  state.objectifs.push(o); persistLocal(); pushRemote('objectifs', o); emit(); return o;
}
export function updateObjectif(id, patch = {}) {
  const o = state.objectifs.find((x) => x.id === id); if (!o) return;
  Object.assign(o, patch);
  ['montant_cible', 'montant_actuel'].forEach((k) => { if (patch[k] != null) o[k] = Math.max(0, Number(patch[k]) || 0); });
  if (patch.titre != null) o.titre = String(patch.titre).trim();
  if (patch.note != null) o.note = String(patch.note).trim();
  persistLocal(); pushRemote('objectifs', o); emit();
}
export function contribuerObjectif(id, montant) {
  const o = state.objectifs.find((x) => x.id === id); if (!o) return;
  o.montant_actuel = Math.max(0, (Number(o.montant_actuel) || 0) + (Number(montant) || 0));
  persistLocal(); pushRemote('objectifs', o); emit();
}
export function deleteObjectif(id) { state.objectifs = state.objectifs.filter((o) => o.id !== id); persistLocal(); delRemote('objectifs', id); emit(); }
export function objectifsSummary() {
  const os = state.objectifs;
  const cible = os.reduce((s, o) => s + (Number(o.montant_cible) || 0), 0);
  const actuel = os.reduce((s, o) => s + (Number(o.montant_actuel) || 0), 0);
  return { total: os.length, atteints: os.filter((o) => objectifInfo(o).atteint).length, cible, actuel, taux: cible > 0 ? Math.min(1, actuel / cible) : 0 };
}

// ---------- Achats fournisseurs (marchandise → augmente le stock, sort de la caisse) ----------
export const ACHAT_STATUTS = ['paye', 'credit'];
export function achatTotal(a) { return (a.lignes || []).reduce((s, l) => s + (Number(l.qte) || 0) * (Number(l.cout_unitaire) || 0), 0); }
export function getAchats() {
  return state.achats.slice().sort((a, b) => (b.date || '').localeCompare(a.date || '') || (new Date(b.created_at || 0) - new Date(a.created_at || 0)));
}
export function getAchat(id) { return state.achats.find((a) => a.id === id) || null; }
function normAchatLignes(lignes) {
  return (lignes || []).map((l) => ({ produit_id: l.produit_id, qte: Math.max(0, Number(l.qte) || 0), cout_unitaire: Math.max(0, Number(l.cout_unitaire) || 0) }))
    .filter((l) => l.produit_id && l.qte > 0);
}
export function addAchat({ fournisseur, date, lignes, statut, note } = {}) {
  const a = {
    id: uid(), fournisseur: (fournisseur || '').trim(), date: date || _ymd2(new Date()),
    lignes: normAchatLignes(lignes), statut: ACHAT_STATUTS.includes(statut) ? statut : 'paye',
    note: (note || '').trim(), created_at: nowISO(),
  };
  state.achats.push(a);
  // augmente le stock des produits achetés (démarre le suivi si le produit ne l'était pas)
  a.lignes.forEach((l) => { const p = getProduit(l.produit_id); if (p) { const base = (p.stock === null || p.stock === undefined) ? 0 : Number(p.stock) || 0; p.stock = base + l.qte; pushRemote('produits', p); } });
  persistLocal(); pushRemote('achats', a); emit();
  return a;
}
export function setAchatStatut(id, statut) {
  const a = getAchat(id); if (!a) return;
  a.statut = ACHAT_STATUTS.includes(statut) ? statut : a.statut;
  persistLocal(); pushRemote('achats', a); emit();
}
export function deleteAchat(id) {
  const a = getAchat(id); if (!a) return;
  logAudit('suppression', 'achat', `${a.fournisseur || 'Fournisseur'} · ${formatF(achatTotal(a))}`);
  // retire du stock ce qui avait été ajouté par cet achat
  (a.lignes || []).forEach((l) => { const p = getProduit(l.produit_id); if (p && p.stock !== null && p.stock !== undefined) { p.stock = Math.max(0, (Number(p.stock) || 0) - (Number(l.qte) || 0)); pushRemote('produits', p); } });
  state.achats = state.achats.filter((x) => x.id !== id);
  persistLocal(); delRemote('achats', id); emit();
}
export function achatsSummary() {
  const now = new Date();
  const moisKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  const total = state.achats.reduce((s, a) => s + achatTotal(a), 0);
  const mois = state.achats.filter((a) => (a.date || '').startsWith(moisKey)).reduce((s, a) => s + achatTotal(a), 0);
  const credit = state.achats.filter((a) => a.statut === 'credit').reduce((s, a) => s + achatTotal(a), 0);
  return { total, mois, nb: state.achats.length, credit };
}
export function getFournisseurs() {
  return [...new Set(state.achats.map((a) => (a.fournisseur || '').trim()).filter(Boolean))].sort();
}

// ---------- Meilleur jour de la semaine (8 dernières semaines) ----------
export function meilleurJour({ semaines = 8 } = {}) {
  const debut = Date.now() - semaines * 7 * DAY_MS;
  const tot = [0, 0, 0, 0, 0, 0, 0];
  state.ventes.forEach((v) => { const d = new Date(v.date); if (d.getTime() >= debut) tot[d.getDay()] += (v.qte || 0) * (v.prix_unitaire || 0); });
  let best = 0, bestv = -1;
  for (let j = 0; j < 7; j++) if (tot[j] > bestv) { bestv = tot[j]; best = j; }
  return { jour: best, total: bestv, nom: JOURS_LONGS[best] };
}

// ---------- Assistant (moteur déterministe local : répond aux questions sur les chiffres) ----------
function _ymd2(d) { return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; }
function _periodeRange(per) { const P = periodInfo(per, 0); return { from: _ymd2(P.start), to: _ymd2(new Date(P.end.getTime() - 1)) }; }
export const ASSISTANT_SUGGESTIONS = [
  "Combien j'ai gagné cette semaine ?",
  'Quel produit rapporte le plus ?',
  'Quel jour je vends le mieux ?',
  'Qui me doit de l\'argent ?',
  'Quelles sont mes prévisions ?',
  'Où part mon argent ?',
];
export function assistantRepondre(question) {
  const q = ' ' + (question || '').toLowerCase() + ' ';
  const has = (...ks) => ks.some((k) => q.includes(k));
  const per = has('semaine') ? 'semaine' : (has('année', 'annee', "cette an") ? 'annee' : (has("aujourd", ' jour ', 'du jour') ? 'jour' : 'mois'));
  const perLbl = { jour: "aujourd'hui", semaine: 'cette semaine', mois: 'ce mois-ci', annee: 'cette année' }[per];
  const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
  const D = serieDashboard(per, 0), t = D.totals;

  if (has('crédit', 'credit', 'me doit', 'doivent', 'dette', 'impay')) {
    const cs = creditsSummary();
    if (!cs.nb) return "Personne ne te doit d'argent pour l'instant. Enregistre une vente à crédit dans la carte « Crédits » du tableau de bord.";
    return `${cs.nb} client${cs.nb > 1 ? 's te doivent' : ' te doit'} ${formatF(cs.total)} au total. Le plus urgent : ${cs.impayes[0].client || '—'} (${formatF(cs.impayes[0].montant)}). Tu peux lui envoyer un rappel WhatsApp depuis « Crédits ».`;
  }
  if (has('prévi', 'previ', 'futur', 'fin de mois', 'vais gagner', 'projection', 'combien je vais')) {
    const P = previsions(); if (!P.actif) return "Pas encore assez de données pour prévoir. Enregistre quelques ventes et reviens me voir.";
    return `À ce rythme (~${formatF(P.avgJour)}/jour), tu finirais le mois vers ${formatF(P.benefFinMois)} de bénéfice et ${formatF(P.caisseFinMois)} en caisse (${P.joursRestants} jour${P.joursRestants > 1 ? 's' : ''} restants).`;
  }
  if (has('anormal', 'alerte', 'bizarre', 'trop dépens', 'trop depens', 'inhabituel')) {
    const al = alertesDepenses(); if (!al.length) return "Rien d'anormal dans tes dépenses récentes.";
    const a = al[0]; return `À surveiller : « ${a.libelle} » (${formatF(a.montant)}) dépasse largement ta moyenne « ${a.categorie} » (~${formatF(a.moyenne)}).`;
  }
  if (has('caisse', 'solde', 'en main', 'liquide', 'combien j\'ai en')) return `Ta caisse est à ${formatF(soldeCaisse())} (fond de départ + ventes encaissées − dépenses).`;
  if (has('quel jour', 'meilleur jour', 'jour je vend', 'jour vend')) {
    const mj = meilleurJour(); if (mj.total <= 0) return "Pas encore assez de ventes pour dire quel jour marche le mieux.";
    return `Ton meilleur jour, c'est le ${mj.nom} (~${formatF(mj.total)} sur 8 semaines). Prépare plus de stock ce jour-là.`;
  }
  if (has('produit', 'rapporte', 'rentable', 'vend le mieux', 'meilleure vente', 'best-seller', 'best seller')) {
    const tops = topProduitsPeriode(per, 0, 3); if (!tops.length) return `Aucune vente ${perLbl}.`;
    const p = tops[0]; return `${cap(perLbl)}, ton produit qui rapporte le plus est « ${p.nom} » : ${formatF(p.revenu)} (${Math.round(p.part * 100)}% de tes ventes).`;
  }
  if (has('dépens', 'depens', 'part mon argent', 'plus gros poste', 'coûte le plus', 'coute le plus')) {
    const hd = historiqueDepenses(_periodeRange(per)); if (!hd.total) return `Aucune dépense ${perLbl}.`;
    const c = hd.parCategorie[0]; return `${cap(perLbl)}, tu as dépensé ${formatF(hd.total)}. Ton plus gros poste : ${c.categorie} (${formatF(c.total)}, ${Math.round(c.part * 100)}%).`;
  }
  if (has('marge', 'taux')) return `${cap(perLbl)}, ta marge moyenne est de ${Math.round(t.tauxMarge * 100)}% (sur ${formatF(t.revenu)} de ventes).`;
  if (has('objectif', 'but ')) { const o = getObjectif(); if (!o) return "Tu n'as pas encore fixé d'objectif. Touche « Objectif du mois » sur le tableau de bord."; const b = serieDashboard('mois', 0).totals.benefice; return `Objectif du mois : ${formatF(o)}. Tu es à ${formatF(Math.max(0, b))} (${Math.round(Math.min(100, Math.max(0, b) / o * 100))}%).`; }
  if (has('réinvest', 'reinvest', 'stock', 'racheter', 'relance')) return `${cap(perLbl)}, mets de côté ${formatF(D.enveloppes.relance)} pour refaire/racheter ta marchandise (c'est le coût de ce que tu as vendu).`;
  if (has('évolu', 'evolu', 'augmente', 'progress', 'recule', 'monte', 'ça va')) {
    const a = analyseBusiness(); if (!a.evolution) return "Pas encore assez d'historique pour comparer d'un mois à l'autre."; const e = a.evolution;
    return `Ton bénéfice ${e.sens === 'hausse' ? 'progresse' : (e.sens === 'baisse' ? 'recule' : 'est stable')} de ${formatF(Math.abs(e.diff))} entre ${e.moisFrom} et ${e.moisTo} (${e.pct >= 0 ? '+' : ''}${Math.round(e.pct * 100)}%).`;
  }
  if (has('bénéf', 'benef', 'gagn', 'gain', 'reste', 'profit')) return `${cap(perLbl)}, ton bénéfice net est de ${formatF(t.benefice)} (marge ${formatF(t.marge)} − charges − dépenses).`;
  if (has('vendu', 'chiffre', ' ca ', 'ventes', 'encaiss', 'recette')) return `${cap(perLbl)}, tu as vendu pour ${formatF(t.revenu)} (${formatNombre(t.unites)} unité${t.unites > 1 ? 's' : ''}).`;
  if (has('bonjour', 'salut', 'bonsoir', 'coucou', 'aide', 'help')) return "Bonjour ! Je suis ton assistant. Pose-moi une question sur ton commerce — tape-la ou touche une suggestion.";
  return "Je réponds sur tes chiffres. Essaie : « Combien j'ai gagné cette semaine ? », « Quel produit rapporte le plus ? », « Quel jour je vends le mieux ? », « Qui me doit de l'argent ? », « Mes prévisions ? ».";
}

// ---------- Rapport d'une période (résumé exportable PDF / Excel / WhatsApp) ----------
export function rapportPeriode(gran = 'jour', offset = 0) {
  const P = periodInfo(gran, offset);
  const D = serieDashboard(gran, offset);
  const hd = historiqueDepenses({ from: _ymd2(P.start), to: _ymd2(new Date(P.end.getTime() - 1)) });
  const tops = topProduitsPeriode(gran, offset, 5);
  const t = D.totals;
  return {
    gran, label: D.label, unit: D.unit,
    ca: t.revenu, cout: t.cout, marge: t.marge, charges: t.charges,
    depenses: hd.total, depensesCat: hd.parCategorie,
    benefice: t.benefice, tauxMarge: t.tauxMarge,
    unites: t.unites, nbVentes: t.nbTx,
    caisse: soldeCaisse(), objectif: getObjectif(), tops,
  };
}

// ---------- Devise (multi-devises) ----------
export function getDevise() { return state.profil.devise || 'F'; }
export function setDevise(code) { setProfil({ devise: CURRENCIES[code] ? code : 'F' }); }

// ---------- Formatage ----------
export function formatF(n) {
  const cur = CURRENCIES[getDevise()] || CURRENCIES.F;
  const v = Math.round(Number(n) || 0);
  const neg = v < 0;
  const s = Math.abs(v).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  const body = cur.pos === 'before' ? `${cur.symbol} ${s}` : `${s} ${cur.symbol}`;
  return (neg ? '-' : '') + body;
}
export function formatNombre(n) {
  return (Math.round(Number(n) || 0)).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

// ---------- Export / import (sauvegarde) ----------
export function exportData() { return JSON.stringify(state, null, 2); }
export function importData(json) {
  const data = typeof json === 'string' ? JSON.parse(json) : json;
  state = Object.assign(emptyState(), data);
  persistLocal();
  if (remote) { // repousser tout vers le cloud
    state.produits.forEach((p) => pushRemote('produits', p));
    state.charges_fixes.forEach((c) => pushRemote('charges_fixes', c));
    state.ventes.forEach((v) => pushRemote('ventes', v));
    state.depenses.forEach((d) => pushRemote('depenses', d));
    state.credits.forEach((c) => pushRemote('credits', c));
    pushRemote('profils', { id: 'me', ...state.profil });
  }
  emit();
}

// ---------- Init ----------
export function initStore() { loadLocal(); emit(); }

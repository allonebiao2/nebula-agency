// Boussole — data layer + logique des 3 enveloppes.
// Offline-first : localStorage est toujours à jour. Si une session Supabase existe,
// on reflète chaque écriture dans le cloud (optimiste) pour la synchro multi-appareils.
import { DEVISE } from './config.js';

const LS_KEY = 'boussole:v1';
const uid = () => (crypto.randomUUID ? crypto.randomUUID() : 'id-' + Date.now() + '-' + Math.random().toString(16).slice(2));
const nowISO = () => new Date().toISOString();

// ---------- État ----------
function emptyState() {
  return {
    profil: { nom_activite: '', devise: DEVISE, solde_initial: 0 },
    produits: [],        // {id, nom, modele, prix_vente, couts:[{id,libelle,montant}], archive, created_at}
    charges_fixes: [],   // {id, libelle, montant, created_at}  (mensuel, niveau activité)
    ventes: [],          // {id, produit_id, date, qte, prix_unitaire, cout_unitaire, created_at}
    depenses: [],        // {id, libelle, categorie, montant, date, created_at}  (sorties d'argent)
  };
}

// Catégories de dépenses. « Réassort / Stock » = achat de marchandise : sort de la caisse
// mais N'EST PAS une charge (le coût passe déjà par la marge des produits) -> exclu du bénéfice.
export const DEPENSE_CATS = ['Réassort / Stock', 'Transport', 'Loyer', 'Salaires', 'Factures', 'Divers'];
export const RESTOCK_CAT = 'Réassort / Stock';

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
  try { localStorage.setItem(LS_KEY, JSON.stringify(state)); } catch (e) { console.warn('persist local', e); }
}
function loadLocal() {
  if (!hasLS()) return;
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (raw) state = Object.assign(emptyState(), JSON.parse(raw));
  } catch (e) { console.warn('load local', e); }
}

// ---------- Cloud ----------
export function setRemote(adapter) { remote = adapter; }
export async function hydrateFromRemote() {
  if (!remote) return;
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
    pushRemote('profils', { id: 'me', ...state.profil });
    return;
  }
  // Sinon : le cloud fait foi (déjà des données en ligne, ou local vide).
  state = Object.assign(emptyState(), data);
  persistLocal();
  emit();
}
function pushRemote(table, row) { if (remote) remote.upsert(table, row).catch((e) => console.warn('push', table, e)); }
function delRemote(table, id) { if (remote) remote.remove(table, id).catch((e) => console.warn('del', table, e)); }

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
export function addProduit({ nom, modele, prix_vente = 0, couts = [] }) {
  const p = {
    id: uid(), nom: nom.trim(), modele, prix_vente: Number(prix_vente) || 0,
    couts: couts.map((c) => ({ id: uid(), libelle: c.libelle, montant: Number(c.montant) || 0 })),
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
  state.depenses = state.depenses.filter((d) => d.id !== id);
  persistLocal(); delRemote('depenses', id); emit();
}

// ---------- Solde de caisse (fond de départ) ----------
export function getSoldeInitial() { return Number(state.profil.solde_initial) || 0; }
export function setSoldeInitial(v) { setProfil({ solde_initial: Math.round(Number(v) || 0) }); }

// ---------- Mutations : ventes ----------
export function addVente({ produit_id, qte = 1, prix_unitaire, date }) {
  const p = getProduit(produit_id); if (!p) return null;
  const v = {
    id: uid(), produit_id, qte: Number(qte) || 1,
    prix_unitaire: prix_unitaire != null ? Number(prix_unitaire) : p.prix_vente,
    cout_unitaire: coutRevient(p),          // coût figé à l'instant de la vente
    date: date || nowISO(), created_at: nowISO(),
  };
  state.ventes.push(v);
  persistLocal(); pushRemote('ventes', v); emit();
  return v;
}
export function deleteVente(id) {
  state.ventes = state.ventes.filter((v) => v.id !== id);
  persistLocal(); delRemote('ventes', id); emit();
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

  conseils.sort((a, z) => PRIO_RANG[a.priorite] - PRIO_RANG[z.priorite]);
  return { sante, score, etat, evolution, conseils, forts };
}

// =====================================================================
//  MOTEUR MULTI-PÉRIODES (dashboard : heure / jour / semaine / mois / année)
// =====================================================================
export const JOURS_COURTS = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'];
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

// ---------- Objectif de bénéfice mensuel ----------
export function getObjectif() { return Number(state.profil.objectif_benefice) || 0; }
export function setObjectif(v) { setProfil({ objectif_benefice: Math.max(0, Math.round(Number(v) || 0)) }); }

// ---------- Caisse + résumé du jour (vue trésorerie) ----------
// Caisse = fond de départ + tout l'encaissement (ventes) − toutes les sorties (dépenses).
export function soldeCaisse() {
  const encaisse = state.ventes.reduce((s, v) => s + (v.qte || 0) * (v.prix_unitaire || 0), 0);
  return getSoldeInitial() + encaisse - sommeDepenses(state.depenses);
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

// ---------- Formatage ----------
export function formatF(n) {
  const v = Math.round(Number(n) || 0);
  const neg = v < 0;
  const s = Math.abs(v).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  return (neg ? '-' : '') + s + ' ' + DEVISE;
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
    pushRemote('profils', { id: 'me', ...state.profil });
  }
  emit();
}

// ---------- Init ----------
export function initStore() { loadLocal(); emit(); }

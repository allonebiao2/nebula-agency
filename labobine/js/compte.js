// LA BOBINE · le compte : connexion par e-mail (lien ou code), droits Pro et crédits, nuage des projets, paiement.
// Aucune bibliothèque : on parle directement à l'API de Supabase. La clé ci-dessous est la clé PUBLIQUE du projet,
// faite pour être dans une page ; ce qui protège les données, ce sont les fonctions `labobine_*` côté serveur,
// qui ne rendent jamais que ce qui appartient à la personne connectée.

const URL_SB = 'https://xukduhqqfzogisoimhyo.supabase.co';
const CLE = 'sb_publishable_pOEeVKbTixrVx3BPIaohMg_FigTtoBH';
const STOCK = 'labobine:session';

/** ⛔ Fermé tant que la base, les fonctions et le webhook ne sont pas installés : l'interface des comptes reste cachée.
    Cet interrupteur n'ouvre AUCUN droit : être Pro exige toujours un paiement confirmé par le serveur. */
export const OUVERT = false || (typeof window !== 'undefined' && window.__labobineComptes === true);

let session = lire();
let droits = null;
const ecouteurs = new Set();

function lire() { try { return JSON.parse(localStorage.getItem(STOCK) || 'null'); } catch { return null; } }
function garder(s) {
  session = s;
  try { if (s) localStorage.setItem(STOCK, JSON.stringify(s)); else localStorage.removeItem(STOCK); } catch { /* navigation privée */ }
  for (const f of ecouteurs) f();
}
const garderDepuis = (s, ancien = null) => garder({
  access_token: s.access_token, refresh_token: s.refresh_token,
  expires_at: s.expires_at || Math.floor(Date.now() / 1000) + Number(s.expires_in || 3600), user: s.user || ancien,
});

export const surChangement = (f) => ecouteurs.add(f);
export const connecte = () => !!session;
export const adresse = () => (session && session.user && session.user.email) || '';
export const lesDroits = () => droits;
export const proActif = () => !!(droits && droits.pro_jusqua && new Date(droits.pro_jusqua) > new Date());

async function rafraichir() {
  if (!session || !session.refresh_token || session.expires_at - 60 > Date.now() / 1000) return;
  try { garderDepuis(await appel('/auth/v1/token?grant_type=refresh_token', { corps: { refresh_token: session.refresh_token }, auth: false }), session.user); }
  catch { garder(null); }
}

async function appel(chemin, { methode = 'POST', corps, auth = true } = {}) {
  const h = { apikey: CLE, 'Content-Type': 'application/json' };
  if (auth) {
    await rafraichir();
    if (!session) throw new Error('Connecte-toi pour continuer.');
    h.Authorization = `Bearer ${session.access_token}`;
  }
  const r = await fetch(URL_SB + chemin, { method: methode, headers: h, body: corps ? JSON.stringify(corps) : undefined });
  const texte = await r.text();
  let json = null;
  try { json = texte ? JSON.parse(texte) : null; } catch { json = null; }
  if (!r.ok) throw new Error((json && (json.msg || json.message || json.error_description || json.erreur)) || `Le serveur a répondu ${r.status}.`);
  return json;
}

/** Envoie l'e-mail de connexion : il contient un lien, et un code si le modèle d'e-mail l'affiche. */
export async function envoyerLien(email) {
  const retour = encodeURIComponent(`${location.origin}${location.pathname}`);
  await appel(`/auth/v1/otp?redirect_to=${retour}`, { corps: { email: email.trim(), create_user: true }, auth: false });
}
export async function verifierCode(email, code) {
  garderDepuis(await appel('/auth/v1/verify', { corps: { type: 'email', email: email.trim(), token: String(code).trim() }, auth: false }));
  await moi();
}
/** Au retour du lien de l'e-mail, la session arrive dans l'adresse (#access_token=…). */
export function lireRetourLien() {
  const h = new URLSearchParams(location.hash.slice(1));
  if (!h.get('access_token')) return false;
  garderDepuis({ access_token: h.get('access_token'), refresh_token: h.get('refresh_token'), expires_at: Number(h.get('expires_at')) || 0, expires_in: h.get('expires_in') });
  history.replaceState(null, '', location.pathname);
  return true;
}
export async function moi() {
  if (!session) return null;
  if (!session.user) { session.user = await appel('/auth/v1/user', { methode: 'GET' }); garder(session); }
  return session.user;
}
export async function deconnecter() {
  try { await appel('/auth/v1/logout', {}); } catch { /* déjà déconnecté côté serveur */ }
  droits = null;
  garder(null);
}

export async function chargerDroits() {
  if (!session) { droits = null; return null; }
  droits = await appel('/rest/v1/rpc/labobine_mes_droits', { corps: {} });
  for (const f of ecouteurs) f();
  return droits;
}
export const poserParrain = (code) => appel('/rest/v1/rpc/labobine_parrain_poser', { corps: { p_code: code } });

/** Ouvre la page de paiement SasPay. Le prix est décidé par le serveur, pas ici. */
export async function payer(offre) {
  const r = await appel('/functions/v1/labobine-commande', { corps: { offre } });
  if (!r || !r.url) throw new Error("Le paiement n'a pas pu s'ouvrir.");
  location.href = r.url;
}

// ---------- nuage : le montage seulement, jamais les vidéos ----------
export const nuageLister = () => appel('/rest/v1/rpc/labobine_projets_lister', { corps: {} });
export const nuageLire = (id) => appel('/rest/v1/rpc/labobine_projet_lire', { corps: { p_id: id } });
export const nuageEcrire = (p) => appel('/rest/v1/rpc/labobine_projet_ecrire', { corps: { p_id: p.id, p_nom: p.nom, p_donnees: p } });
export const nuageSupprimer = (id) => appel('/rest/v1/rpc/labobine_projet_supprimer', { corps: { p_id: id } });

export const PRIX = { 'pro-mois': '1 500 F par mois', 'pro-an': '12 000 F par an' };

// Boussole — multilingue (i18n) léger, sans dépendance.
// Principe : le français est la langue SOURCE (le code est écrit en français).
// Pour les autres langues, on traduit l'INTERFACE (libellés de navigation, titres,
// boutons, champs, menus) à la volée après chaque rendu, via un dictionnaire
// « texte français → texte traduit » appliqué sur des sélecteurs sûrs.
// Les langues locales (fon, yoruba…) sont ajoutées/corrigées par le commerçant
// lui-même (il connaît les bons mots) : honnête et juste par construction.

const LS_LANG = 'boussole:lang';
const LS_CUSTOM = 'boussole:lang-custom';

// Langues intégrées (traduction vérifiée) : français + anglais.
export const BUILTIN_LANGS = [
  { code: 'fr', nom: 'Français', natif: 'Français' },
  { code: 'en', nom: 'Anglais', natif: 'English' },
];

// Suggestions de langues locales à compléter par le commerçant (Bénin / Afrique de l'Ouest).
export const LOCAL_SUGGESTIONS = [
  { code: 'fon', natif: 'Fɔ̀ngbè (fon)' },
  { code: 'yo', natif: 'Yorùbá' },
  { code: 'ewe', natif: 'Èʋegbe (mina/goun)' },
  { code: 'ha', natif: 'Hausa' },
];

// Dictionnaire anglais (interface). Clé = texte FR exact rendu à l'écran.
const EN = {
  // Navigation & écrans
  'Accueil': 'Home', 'Ventes': 'Sales', 'Dépenses': 'Expenses', 'Carnet': 'Ledger',
  'Stock': 'Stock', 'Bilan': 'Report', 'Réglages': 'Settings', 'Paramètres': 'Settings',
  'Menu': 'Menu', 'Rechercher': 'Search', 'Rechercher…': 'Search…', 'Notifications': 'Notifications',
  // Actions fréquentes
  'Ajouter': 'Add', 'Enregistrer': 'Save', 'Modifier': 'Edit', 'Supprimer': 'Delete',
  'Fermer': 'Close', 'Annuler': 'Cancel', 'Retour': 'Back', 'Continuer': 'Continue',
  'Terminer': 'Finish', 'Valider': 'Confirm', 'Voir': 'View', 'Partager': 'Share',
  'Imprimer': 'Print', 'Exporter': 'Export', 'Importer': 'Import', 'Encaisser': 'Charge',
  'Se connecter': 'Sign in', 'Déconnexion': 'Sign out', 'Créer un compte': 'Create account',
  'Réinitialiser': 'Reset', 'Connecter': 'Connect', 'Oublier': 'Forget', 'Payé': 'Paid',
  'Marquer payé': 'Mark paid', 'Solder': 'Settle', 'Versement': 'Payment', 'Nouvel achat': 'New purchase',
  // Écran d'accueil / KPI
  "Aujourd'hui": 'Today', 'Encaissé': 'Collected', 'Dépensé': 'Spent',
  'Bénéfice du jour': 'Profit today', 'Solde de caisse': 'Cash balance', 'Trésorerie': 'Cash on hand',
  'Chiffre d’affaires': 'Revenue', "Chiffre d'affaires": 'Revenue', 'Bénéfice net': 'Net profit',
  'Bénéfice': 'Profit', 'Marge': 'Margin', 'Taux de marge': 'Margin rate', 'Panier moyen': 'Average basket',
  'Dettes dehors': 'Money owed to you', 'Mes objectifs': 'My goals', 'Objectif du mois': 'Monthly goal',
  // Ventes / caisse
  'Caisse': 'Checkout', 'Vente rapide': 'Quick sale', 'Reçu de caisse': 'Sales receipt',
  'Mode de paiement': 'Payment method', 'Vendeur': 'Seller', 'Total': 'Total', 'Historique': 'History',
  'Espèces': 'Cash', 'Mobile Money': 'Mobile Money', 'Carte': 'Card', 'Crédit': 'Credit', 'Virement': 'Transfer',
  // Dépenses / achats
  'Ajouter une dépense': 'Add an expense', 'Par catégorie': 'By category', 'Achats fournisseurs': 'Supplier purchases',
  'Fournisseur': 'Supplier', 'À crédit': 'On credit', 'À payer': 'To pay', 'Catégorie': 'Category', 'Montant': 'Amount',
  // Carnet / clients
  'Clients': 'Customers', 'Client': 'Customer', 'Dettes en cours': 'Outstanding debts', 'Recouvrement': 'Collection',
  'Reste': 'Remaining', 'Échéance': 'Due date', 'Rappel': 'Reminder', 'Fiche client': 'Customer profile',
  // Bilan / rapports
  'Rapport': 'Report', 'Jour': 'Day', 'Semaine': 'Week', 'Mois': 'Month', 'Année': 'Year',
  'Palmarès produits': 'Product ranking', 'Ça cartonne': 'Best sellers', 'À relancer': 'Needs attention',
  'Factures & devis': 'Invoices & quotes', 'Facture': 'Invoice', 'Devis': 'Quote', 'Par produit': 'By product',
  'Évolution revenu & bénéfice': 'Revenue & profit trend', 'Bénéfice net par mois': 'Net profit by month',
  // Stock
  'Rupture': 'Out of stock', 'Stock bas': 'Low stock', 'À réassort': 'To restock', 'Non suivi': 'Not tracked', 'Suivre': 'Track',
  // Réglages (panneaux)
  'Activité': 'Business', "Nom de l'activité": 'Business name', 'Devise': 'Currency',
  'Identité pour tes factures': 'Details for your invoices', 'Adresse': 'Address', 'Téléphone': 'Phone', 'E-mail': 'Email',
  'Vendeurs': 'Sellers', 'Produits': 'Products', 'Charges fixes mensuelles': 'Fixed monthly costs',
  'Compte & synchronisation': 'Account & sync', 'Sauvegarde': 'Backup', 'Aide': 'Help',
  'Effacer toutes les données': 'Erase all data', 'Revoir le tutoriel': 'Replay the tutorial',
  'Personnalisation': 'Personalization', 'Couleur d’accent': 'Accent color', 'Taille du texte': 'Text size',
  'Densité': 'Density', 'Coins': 'Corners', 'Messages WhatsApp': 'WhatsApp messages',
  'Imprimante Bluetooth': 'Bluetooth printer', 'Langue': 'Language', 'Thème': 'Theme',
  'Normale': 'Normal', 'Grande': 'Large', 'Très grande': 'Very large', 'Confortable': 'Comfortable',
  'Compact': 'Compact', 'Doux': 'Soft', 'Nets': 'Sharp', 'Clair': 'Light', 'Sombre': 'Dark',
  'Relance de dette': 'Debt reminder', 'Message du reçu': 'Receipt message', 'Message de remerciement': 'Thank-you message',
  'Imprimer un test': 'Print a test', 'Ajouter une langue locale': 'Add a local language',
  // États vides / divers
  'Aucun produit.': 'No products yet.', 'Aucune charge fixe.': 'No fixed costs.',
  'Mode local': 'Local mode', 'Synchronisé': 'Synced', 'Cloud disponible': 'Cloud available',
  'Nom du vendeur': "Seller's name", 'de ton commerce': 'of your shop',
};

const BUILTIN_DICTS = { en: EN };

// --- Langues personnalisées (locales) définies par le commerçant ---
function loadCustom() {
  try { return JSON.parse(localStorage.getItem(LS_CUSTOM)) || {}; } catch { return {}; }
}
function saveCustom(obj) {
  try { localStorage.setItem(LS_CUSTOM, JSON.stringify(obj)); } catch {}
}
export function getCustomLangs() {
  const c = loadCustom();
  return Object.keys(c).map((code) => ({ code, natif: c[code].natif || code, terms: c[code].terms || {}, custom: true }));
}
export function addCustomLang(code, natif) {
  const c = loadCustom(); code = String(code || '').trim().toLowerCase().replace(/[^a-z0-9-]/g, '') || ('loc' + Date.now());
  if (!c[code]) c[code] = { natif: natif || code, terms: {} };
  else if (natif) c[code].natif = natif;
  saveCustom(c); return code;
}
export function setCustomTerm(code, fr, val) {
  const c = loadCustom(); if (!c[code]) c[code] = { natif: code, terms: {} };
  if (val && val.trim()) c[code].terms[fr] = val.trim(); else delete c[code].terms[fr];
  saveCustom(c);
}
export function removeCustomLang(code) {
  const c = loadCustom(); delete c[code]; saveCustom(c);
  if (getLang() === code) setLang('fr');
}

// Termes-clés proposés à la traduction quand on crée une langue locale (l'essentiel de l'interface).
export const CORE_TERMS = [
  'Accueil', 'Ventes', 'Dépenses', 'Carnet', 'Stock', 'Bilan', 'Réglages',
  'Ajouter', 'Enregistrer', 'Modifier', 'Supprimer', 'Fermer', 'Encaisser', 'Payé',
  "Aujourd'hui", 'Encaissé', 'Dépensé', 'Bénéfice', 'Total', 'Client', 'Vendeur',
  'Caisse', 'Reçu de caisse', 'Mode de paiement', 'Espèces', 'Mobile Money',
  'Rechercher', 'Historique', 'Montant', 'Reste', 'Rappel',
];

// --- Langue courante ---
export function getLang() {
  try { return localStorage.getItem(LS_LANG) || 'fr'; } catch { return 'fr'; }
}
export function setLang(code) {
  try { localStorage.setItem(LS_LANG, code || 'fr'); } catch {}
  try { document.documentElement.lang = (code || 'fr').split('-')[0]; } catch {}
}
export function allLangs() { return [...BUILTIN_LANGS, ...getCustomLangs().map((l) => ({ code: l.code, nom: l.natif, natif: l.natif, custom: true }))]; }
export function langLabel(code) { const l = allLangs().find((x) => x.code === code); return l ? l.natif : code; }

function dictFor(code) {
  if (code === 'fr') return null;
  if (BUILTIN_DICTS[code]) return BUILTIN_DICTS[code];
  const c = loadCustom()[code];
  return c ? c.terms : null;
}

// --- Application de la traduction sur le DOM rendu ---
// Sélecteurs SÛRS : uniquement des libellés d'interface (jamais les données saisies,
// ni les montants, ni les noms de produits/clients).
const SELS = [
  '.nav__lbl', '.side__lbl', '.side__sub', '.sectitle h1', '.sectitle p',
  '.panel__head h2', '.panel__head h3', '.panel__sub', '.btn', 'label', '.opt',
  '.modal__title', '.modal__lead', '.lrow--empty', '.plm__empty', '.plm__good',
  '.vchip', '.pchip', '.chip', '.catchip', '.aschip', '.seg__b', '.authswitch__b',
  'th', '.emptystate h3', '.plm__tag', '.palm__h', '.rstat__lbl', '.pnav__t',
].join(',');

function translateTextNodes(el, dict) {
  for (const node of el.childNodes) {
    if (node.nodeType === 3) {
      const raw = node.nodeValue; const key = raw.trim();
      if (key && dict[key] != null) node.nodeValue = raw.replace(key, dict[key]);
    }
  }
}
function translateAttrs(root, dict) {
  root.querySelectorAll('[placeholder],[aria-label],[title]').forEach((el) => {
    ['placeholder', 'aria-label', 'title'].forEach((a) => {
      const v = el.getAttribute(a); if (v && dict[v.trim()] != null) el.setAttribute(a, dict[v.trim()]);
    });
  });
}
function translateRoot(root, dict) {
  try {
    root.querySelectorAll(SELS).forEach((el) => translateTextNodes(el, dict));
    translateAttrs(root, dict);
  } catch {}
}

let mo = null, applying = false, scheduled = false;
function runTranslate() {
  const dict = dictFor(getLang());
  if (!dict) return;
  applying = true;
  try {
    ['#app', '#modal-root', '#overlay-root', '#toast-root'].forEach((sel) => {
      const r = document.querySelector(sel); if (r) translateRoot(r, dict);
    });
  } finally { applying = false; }
}
function schedule() { if (scheduled) return; scheduled = true; requestAnimationFrame(() => { scheduled = false; runTranslate(); }); }

// Démarre l'observation : traduit à chaque (re)rendu. Idempotent.
export function startI18n() {
  if (mo) { mo.disconnect(); mo = null; }
  if (getLang() === 'fr') return;   // rien à faire : la langue source est le français
  runTranslate();
  mo = new MutationObserver(() => { if (!applying) schedule(); });
  const app = document.getElementById('app');
  if (app) mo.observe(app, { childList: true, subtree: true, characterData: true });
  ['modal-root', 'overlay-root'].forEach((id) => { const n = document.getElementById(id); if (n) mo.observe(n, { childList: true, subtree: true, characterData: true }); });
}

// Applique une nouvelle langue immédiatement (appelé après re-render).
export function applyLang() { startI18n(); }

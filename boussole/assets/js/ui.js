// Boussole — rendu des écrans, modales, toasts.
import { icon } from './icons.js';
import {
  getState, getProduits, getProduit, getChargesFixes, getVentes,
  coutRevient, margeUnitaire, chargesMensuellesTotal, seuilRentabilite,
  bilanMois, ventesDuMois, serieMensuelle, trimestreDe, currentMonthKey,
  statistiques, analyseBusiness,
  serieDashboard, topProduitsPeriode, palmaresProduits, getObjectif, resumeJour, historiqueVentes,
  historiqueDepenses, DEPENSE_CATS, previsions, getDevise, creditsSummary,
  ASSISTANT_SUGGESTIONS, rapportPeriode,
  getDocuments, documentTotals, documentsSummary, montantEnLettres, getCredits, creditReste, creditPaye,
  getClients, getStockInfo, stockResume, recouvrement, journalCaisse, notifications,
  getObjectifs, objectifInfo,
  PAYMENT_MODES, PAYMENT_LABELS, getVendeurs,
  achatsSummary, getAchats, achatTotal, ACHAT_STATUTS, getFournisseurs,
  WA_TEMPLATES_META, getWaTemplate,
  PLANS, getLicence, licenceEtat, TRIAL_DAYS, proAccess,
  getEquipe, ROLES, ROLE_LABELS, ROLE_DESCS, roleLabel,
  getAudit, getBoutiques, activeBoutiqueId, consolideBoutiques, relancesDues,
  isDigital, getBusinessType, TARIF_TYPES, TARIF_LABELS, TARIF_UNITS, depenseCats,
  getDepensesRecurrentes, coutsRecurrentsMensuels,
  formatF, formatNombre, MOIS_LONGS,
} from './store.js';
import { chartBeneficeMensuel, chartEvolution, miniSpark, progressRing, chartHero, chartDonut, sparklineRaw } from './charts.js';
import { APP_NAME, CURRENCIES, NEBULA_MOMO, NEBULA_WHATSAPP } from './config.js';
import * as I18n from './i18n.js';
import * as BT from './btprint.js';
import * as Sec from './security.js';

// Préférences d'apparence (appareil) — accent, taille, densité, coins.
const uiPref = (k, d) => { try { return localStorage.getItem('boussole:' + k) || d; } catch { return d; } };
export const ACCENTS = [
  { k: 'ambre', nom: 'Ambre', c: '#f6a63c' }, { k: 'emeraude', nom: 'Émeraude', c: '#34d399' },
  { k: 'ocean', nom: 'Océan', c: '#38bdf8' }, { k: 'violet', nom: 'Violet', c: '#a78bfa' },
  { k: 'rose', nom: 'Rose', c: '#fb7185' }, { k: 'or', nom: 'Or', c: '#eab308' },
];
function segControl(action, cur, opts) {
  return `<div class="seg seg--${opts.length}">${opts.map(([v, l]) => `<button class="seg__b seg__b--c ${cur === v ? 'is-on' : ''}" data-action="${action}" data-v="${v}">${l}</button>`).join('')}</div>`;
}

export const esc = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const moisLabel = (mk) => {
  const [y, m] = mk.split('-');
  return `${MOIS_LONGS[Number(m) - 1]} ${y}`;
};

// ============ TOPBAR ============
// Légende d'explication (toujours visible sous un titre de zone) — pour que
// chaque commerçant comprenne à quoi sert chaque zone, en langage simple.
export function zhelp(text) { return `<p class="zhelp"><span class="zhelp__ic" data-icon="help"></span><span>${esc(text)}</span></p>`; }

export function topbarHTML(cloud, theme = 'light', notifCount = 0) {
  const nom = getState().profil.nom_activite || 'Mon activité';
  const badge = notifCount > 0 ? `<span class="bell__badge">${notifCount > 9 ? '9+' : notifCount}</span>` : '';
  const cloudChip = cloud.configured
    ? (cloud.user
      ? `<button class="chip chip--on topbar__deskonly" data-action="open-auth" title="Synchronisé"><span class="chip__ic" data-icon="cloud"></span><span class="chip__t">${esc(cloud.user.email.split('@')[0])}</span></button>`
      : `<button class="chip chip--cta topbar__deskonly" data-action="open-auth" title="Se connecter"><span class="chip__ic" data-icon="cloud"></span><span class="chip__t">Se connecter</span></button>`)
    : `<button class="chip topbar__deskonly" data-action="cloud-info" title="Mode local"><span class="chip__ic" data-icon="cloudOff"></span><span class="chip__t">Local</span></button>`;
  return `
    <button class="topbar__menu" data-action="open-drawer" aria-label="Ouvrir le menu"><span data-icon="menu"></span></button>
    <div class="topbar__brand"><span class="brand__mark"><img src="assets/icons/logo-mark.png" alt="" width="26" height="25"></span>
      <div class="brand__txt"><span class="brand__name">${esc(APP_NAME)}</span><span class="brand__sub">${esc(nom)}</span></div>
    </div>
    <div class="topbar__search">
      <span class="topbar__search-ic" data-icon="search"></span>
      <input id="global-search" class="topbar__search-in" type="search" placeholder="Rechercher un produit, un client, une facture…" autocomplete="off" aria-label="Recherche globale" data-action="global-search">
      <div id="gsearch-res" class="topbar__search-res"></div>
    </div>
    <div class="topbar__actions">
      <button class="btn btn--sm topbar__new" data-action="fab-vente"><span data-icon="plus"></span> Vente</button>
      <button class="btn btn--ghost btn--sm topbar__new" data-action="fab-depense"><span data-icon="minus"></span> Dépense</button>
      <button class="chip chip--icon chip--bell" data-action="open-notifs" title="Notifications" aria-label="Notifications">${badge}<span class="chip__ic" data-icon="bell"></span></button>
      <button class="chip chip--icon chip--assist" data-action="open-assistant" title="Assistant" aria-label="Assistant"><span class="chip__ic" data-icon="spark"></span></button>
      <button class="chip chip--icon topbar__deskonly" data-action="toggle-theme" title="Thème clair / sombre" aria-label="Changer de thème"><span class="chip__ic" data-icon="${theme === 'dark' ? 'sun' : 'moon'}"></span></button>
      ${cloudChip}
    </div>`;
}

// ============ NAV ============
// Barre du bas (mobile) : 4 onglets + un creux central pour le FAB.
export function navHTML(active) {
  const item = (id, label, ic, badge) =>
    `<button class="nav__item ${active === id ? 'is-active' : ''}" data-action="go" data-screen="${id}">
      <span class="nav__ic" data-icon="${ic}"></span><span class="nav__lbl">${label}</span>${badge ? `<span class="nav__badge">${badge}</span>` : ''}</button>`;
  const nb = notifications().count;
  return item('accueil', 'Accueil', 'home') + item('ventes', 'Ventes', 'ventes')
    + `<span class="nav__notch" aria-hidden="true"></span>`
    + item('carnet', 'Carnet', 'users', nb) + item('stock', isDigital() ? 'Catalogue' : 'Stock', isDigital() ? 'spark' : 'box');
}

// Bouton flottant + speed-dial (Vente / Dépense)
export function fabHTML(open) {
  return `${open ? `<div class="fab__scrim" data-action="fab-close"></div>
    <div class="fab__menu">
      <button class="fab__act" data-action="fab-vente"><span class="fab__act-ic fab__act-ic--v" data-icon="ventes"></span> Vente</button>
      <button class="fab__act" data-action="fab-depense"><span class="fab__act-ic fab__act-ic--d" data-icon="receipt"></span> Dépense</button>
    </div>` : ''}
    <button class="fab__btn ${open ? 'is-open' : ''}" data-action="fab-toggle" aria-label="Ajouter une vente ou une dépense" aria-expanded="${open ? 'true' : 'false'}"><span class="fab__plus" data-icon="plus"></span></button>`;
}

// Sidebar (desktop) : arborescence complète en accordéon
const NAV_TREE = [
  { id: 'accueil', label: 'Accueil', icon: 'home' },
  { id: 'ventes', label: 'Ventes & recettes', icon: 'ventes', children: [
    { label: 'Nouvelle vente', action: 'fab-vente' },
    { label: 'Historique', screen: 'ventes' },
    { label: 'Factures & devis', screen: 'bilan' },
  ] },
  { id: 'depenses', label: 'Dépenses & achats', icon: 'receipt', children: [
    { label: 'Saisir une dépense', action: 'fab-depense' },
    { label: 'Historique', screen: 'depenses' },
    { label: 'Frais fixes', screen: 'reglages' },
  ] },
  { id: 'stock', label: 'Stock', icon: 'box' },
  { id: 'carnet', label: 'Carnet — clients', icon: 'users' },
  { id: 'bilan', label: 'Rapports & évolution', icon: 'bilan' },
  { id: 'reglages', label: 'Réglages', icon: 'reglages' },
];
export function sidebarHTML(active, cloud, openGroup) {
  const nb = notifications().count;
  const rows = NAV_TREE.map((n) => {
    if (n.children) {
      const childActive = n.children.some((c) => c.screen === active);
      const open = openGroup === n.id || (openGroup == null && childActive);
      const kids = n.children.map((c) => c.screen
        ? `<button class="side__sub ${active === c.screen ? 'is-active' : ''}" data-action="go" data-screen="${c.screen}">${c.label}</button>`
        : `<button class="side__sub" data-action="${c.action}">${c.label}</button>`).join('');
      return `<div class="side__grp ${open ? 'is-open' : ''}">
        <button class="side__item side__item--grp ${childActive ? 'is-current' : ''}" data-action="side-acc" data-grp="${n.id}" aria-expanded="${open ? 'true' : 'false'}">
          <span class="side__ic" data-icon="${n.icon}"></span><span class="side__lbl">${n.label}</span><span class="side__chev" data-icon="chevronDown"></span></button>
        <div class="side__subs">${kids}</div></div>`;
    }
    const badge = n.id === 'carnet' && nb ? `<span class="side__badge">${nb}</span>` : '';
    const lbl = (n.id === 'stock' && isDigital()) ? 'Catalogue' : n.label;
    const ic = (n.id === 'stock' && isDigital()) ? 'spark' : n.icon;
    return `<button class="side__item ${active === n.id ? 'is-active' : ''}" data-action="go" data-screen="${n.id}">
      <span class="side__ic" data-icon="${ic}"></span><span class="side__lbl">${esc(lbl)}</span>${badge}</button>`;
  }).join('');
  const acct = cloud.configured ? (cloud.user ? `<span class="side__acct-t"><strong>${esc(cloud.user.email.split('@')[0])}</strong><small>Synchronisé</small></span>` : `<span class="side__acct-t"><strong>Non connecté</strong><small>Mode local</small></span>`) : `<span class="side__acct-t"><strong>Mode local</strong><small>Cet appareil</small></span>`;
  const acctAction = cloud.configured && cloud.user ? 'logout' : (cloud.configured ? 'open-auth' : 'cloud-info');
  return `
    <div class="side__brand"><span class="side__logo"><img src="assets/icons/logo-app.png" alt="" width="34" height="34"></span>
      <span class="side__brandtxt"><strong>${esc(APP_NAME)}</strong><small>${esc(getState().profil.nom_activite || 'Mon activité')}</small></span></div>
    <nav class="side__nav">${rows}</nav>
    <div class="side__foot">
      <button class="side__acct" data-action="${acctAction}"><span class="side__avatar" data-icon="user"></span>${acct}<span class="side__acct-ic" data-icon="${cloud.user ? 'logout' : 'cloud'}"></span></button>
      <button class="side__foot-btn" data-action="toggle-theme" aria-label="Thème"><span data-icon="sun"></span></button>
      <button class="side__foot-btn" data-action="open-tuto" aria-label="Aide"><span data-icon="help"></span></button>
    </div>`;
}

// Drawer (mobile) : destinations secondaires + réglages rapides
export function drawerHTML(cloud, theme) {
  const nom = getState().profil.nom_activite || 'Mon activité';
  const acct = cloud.configured ? (cloud.user ? `${esc(cloud.user.email)} · synchronisé` : 'Non connecté · mode local') : 'Mode local · cet appareil';
  const item = (action, ic, label, screen) => `<button class="drawer__item" data-action="${action}"${screen ? ` data-screen="${screen}"` : ''}><span class="drawer__ic" data-icon="${ic}"></span>${label}</button>`;
  return `<div class="drawer__scrim" data-action="close-overlay"></div>
    <aside class="drawer" role="dialog" aria-label="Menu">
      <div class="drawer__head">
        <span class="drawer__avatar" data-icon="user"></span>
        <div class="drawer__id"><strong>${esc(nom)}</strong><small>${esc(acct)}</small></div>
        <button class="drawer__x" data-action="close-overlay" aria-label="Fermer"><span data-icon="close"></span></button>
      </div>
      <nav class="drawer__nav">
        ${item('go', 'receipt', 'Dépenses & achats', 'depenses')}
        ${item('go', 'bilan', 'Rapports & bilan', 'bilan')}
        ${item('go', 'reglages', 'Réglages', 'reglages')}
      </nav>
      <div class="drawer__sep"></div>
      <div class="drawer__nav">
        ${item('toggle-theme', theme === 'dark' ? 'sun' : 'moon', `Thème ${theme === 'dark' ? 'clair' : 'sombre'}`)}
        ${item('open-tuto', 'help', 'Aide & tutoriel')}
        ${cloud.configured && cloud.user
          ? item('logout', 'logout', 'Déconnexion')
          : item(cloud.configured ? 'open-auth' : 'cloud-info', 'cloud', cloud.configured ? 'Se connecter' : 'Mode local')}
      </div>
    </aside>`;
}

// Panneau notifications (cloche)
export function notifsHTML() {
  const n = notifications();
  const rows = n.list.length
    ? n.list.map((a) => `<button class="notif__row" data-action="notif-go" data-screen="${a.screen}">
        <span class="notif__ic notif__ic--${a.type}" data-icon="${a.icon}"></span>
        <span class="notif__t">${esc(a.text)}</span><span class="notif__chev" data-icon="chevron"></span></button>`).join('')
    : `<div class="notif__empty"><span class="notif__empty-ic" data-icon="check"></span>Tout est à jour, aucune alerte.</div>`;
  return `<div class="notif__scrim" data-action="close-overlay"></div>
    <div class="notif" role="dialog" aria-label="Notifications">
      <div class="notif__head"><strong>Alertes</strong>${n.count ? `<span class="notif__count">${n.count}</span>` : ''}</div>
      <div class="notif__list">${rows}</div>
    </div>`;
}

// ============ ÉCRAN D'ACCUEIL — connexion / inscription ============
export function viewWelcomeHTML() {
  return `<section class="view view--welcome">
    <img class="welcome__bg" src="assets/img/welcome.webp" alt="" aria-hidden="true">
    <div class="welcome__scrim"></div>
    <div class="welcome__top">
      <img class="welcome__logo" src="assets/icons/logo-app.png" alt="Boussole" width="76" height="76">
      <h1>${esc(APP_NAME)}</h1>
      <p class="welcome__sub">Gère ton commerce et vois ta rentabilité clairement — sur ton téléphone <strong>et</strong> ton PC, synchronisés.</p>
    </div>
    <div class="welcome__bottom">
      <div class="welcome__actions">
        <button class="btn btn--lg" data-action="welcome-signup">Créer un compte</button>
        <button class="btn btn--ghost btn--lg" data-action="welcome-signin">J'ai déjà un compte</button>
      </div>
      <button class="welcome__skip" data-action="welcome-skip">Continuer sans compte</button>
      <span class="welcome__local"><span data-icon="cloudOff"></span>Sans compte, tes données restent sur cet appareil</span>
    </div>
  </section>`;
}

// ============ BANDEAU 3 ENVELOPPES ============
export function enveloppesHTML(b, { compact = false } = {}) {
  const pct = b.charges_cible > 0 ? Math.min(100, Math.round((b.charges_couvertes / b.charges_cible) * 100)) : 100;
  const benClass = b.benefice > 0 ? 'env--ben-pos' : (b.benefice < 0 ? 'env--ben-neg' : '');
  return `
  <div class="env-grid ${compact ? 'env-grid--compact' : ''}">
    <div class="env env--relance">
      <div class="env__head"><span class="env__ic" data-icon="box"></span><span class="env__t">Relance production</span></div>
      <div class="env__val">${formatF(b.relance)}</div>
      <div class="env__sub">à remettre pour racheter / refaire</div>
    </div>
    <div class="env env--charges">
      <div class="env__head"><span class="env__ic" data-icon="bolt"></span><span class="env__t">Charges fixes</span></div>
      <div class="env__val">${formatF(b.charges_couvertes)}<span class="env__cap"> / ${formatF(b.charges_cible)}</span></div>
      <div class="env__bar"><span style="transform:scaleX(${(pct / 100).toFixed(3)})"></span></div>
      <div class="env__sub">${b.charges_reste > 0 ? `reste ${formatF(b.charges_reste)} à couvrir ce mois` : 'charges du mois couvertes'}</div>
    </div>
    <div class="env env--benefice ${benClass}">
      <div class="env__head"><span class="env__ic" data-icon="wallet"></span><span class="env__t">Bénéfice net</span></div>
      <div class="env__val">${formatF(b.benefice)}</div>
      <div class="env__sub">${b.a_perte ? 'attention : vente à perte' : 'mis de côté ce mois'}</div>
    </div>
  </div>`;
}

// ============ ÉCRAN ACCUEIL — tableau de bord bento ============
const PROD_COLORS = ['var(--acc)', 'var(--rel)', 'var(--pos)', 'var(--chg)', 'var(--dng)', '#9b8cff'];

// Badge de variation coloré (▲ +18 %  /  ▼ -5 %). opts.pts = points, opts.invert = baisse est bonne.
function deltaBadge(d, opts = {}) {
  if (!d || d.sens === 'stable') return `<span class="delta delta--flat">—</span>`;
  const up = d.sens === 'hausse';
  const good = opts.invert ? !up : up;
  let txt;
  if (opts.pts) {
    txt = `${d.diff > 0 ? '+' : ''}${Math.round(d.diff * 100)} pts`;
  } else {
    const p = Math.round(d.pct * 100);
    txt = Math.abs(p) > 999 ? `${p > 0 ? '>+' : '<-'}999 %` : `${p > 0 ? '+' : ''}${p} %`;
  }
  return `<span class="delta ${good ? 'pos' : 'neg'}"><span data-icon="${up ? 'arrowUp' : 'arrowDown'}"></span>${txt}</span>`;
}

function kpiHTML(lbl, val, delta, spark, opts = {}) {
  const sp = spark ? `<span class="kpi__spark">${sparklineRaw(spark, { color: opts.sparkColor || 'var(--acc)', w: 128, h: 30 })}</span>` : '';
  const cnt = opts.count ? ` data-count="${opts.count.n}" data-fmt="${opts.count.fmt}"` : '';
  return `<div class="kpi">
    <span class="kpi__lbl">${lbl}</span>
    <span class="kpi__val ${opts.valCls || ''}"${cnt}>${val}</span>
    <span class="kpi__foot">${deltaBadge(delta, opts.delta || {})}${sp}</span>
  </div>`;
}

function periodBarHTML(gran, offset, label) {
  const chip = (g, t) => `<button class="pchip ${g === gran ? 'is-on' : ''}" data-action="set-gran" data-gran="${g}">${t}</button>`;
  return `<div class="periodbar">
    <div class="pchips">${chip('jour', 'Jour')}${chip('semaine', 'Semaine')}${chip('mois', 'Mois')}${chip('annee', 'Année')}</div>
    <div class="pnav">
      <button class="pnav__btn pnav__btn--prev" data-action="period-prev" aria-label="Période précédente"><span data-icon="chevron"></span></button>
      <span class="pnav__lbl">${esc(label)}</span>
      <button class="pnav__btn" data-action="period-next" ${offset >= 0 ? 'disabled' : ''} aria-label="Période suivante"><span data-icon="chevron"></span></button>
    </div>
  </div>`;
}

export function viewAccueilHTML(period = { gran: 'mois', offset: 0 }) {
  const gran = period.gran || 'mois', offset = period.offset || 0;
  const produits = getProduits();
  const nom = getState().profil.nom_activite || 'Mon activité';
  const now = new Date();
  const hNow = now.getHours();
  const greet = (hNow >= 18 || hNow < 5) ? 'Bonsoir' : (hNow < 12 ? 'Bonjour' : 'Bon après-midi');
  const timeStr = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  const dateStr = now.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' });

  if (produits.length === 0) {
    return `<section class="view">${sectionTitle('Accueil', greet)}
      ${emptyState('home', `${greet}, ${esc(nom)}`, 'Configure ton activité et tes produits pour faire apparaître ton tableau de bord.', 'Configurer mon activité', 'go-config')}</section>`;
  }

  const D = serieDashboard(gran, offset);
  const t = D.totals, env = D.enveloppes;
  const analyse = analyseBusiness();
  const santeCol = (SANTE[analyse.sante] || SANTE.demarrage).col;
  const pctCharges = env.charges_cible > 0 ? Math.min(100, Math.round((env.charges_couvertes / env.charges_cible) * 100)) : 100;
  const pctMarge = Math.round(t.tauxMarge * 100);

  const objectif = getObjectif();
  const benMois = serieDashboard('mois', 0).totals.benefice;
  const pctObj = objectif > 0 ? Math.max(0, Math.min(100, Math.round((benMois / objectif) * 100))) : 0;

  const tops = topProduitsPeriode(gran, offset, 6);
  const rTot = env.revenu || 1;

  // ---- BLOC « AUJOURD'HUI » = carrousel KPI (swipe mobile / rangée PC) ----
  const R = resumeJour();
  const csKpi = creditsSummary();
  const kpit = (ic, lbl, num, cls, o = {}) => {
    const tag = o.action ? 'button' : 'div';
    const attrs = o.action ? ` data-action="${o.action}"${o.screen ? ` data-screen="${o.screen}"` : ''}` : '';
    return `<${tag} class="kpit ${o.tap ? 'kpit--tap' : ''}"${attrs}${o.title ? ` title="${o.title}"` : ''}>
      <span class="kpit__ic" data-icon="${ic}"></span>
      <span class="kpit__lbl">${lbl}</span>
      <span class="kpit__val ${cls || ''}" data-count="${num}" data-fmt="f">${formatF(num)}</span>
      ${o.edit ? '<span class="kpit__edit" data-icon="edit"></span>' : ''}
    </${tag}>`;
  };
  const kpiTiles = [
    kpit('coins', 'CA du jour', R.ca, 'pos'),
    kpit('receipt', 'Dépensé', R.depenses, R.depenses > 0 ? 'neg' : ''),
    kpit('spark', 'Bénéfice du jour', R.benefice, R.benefice >= 0 ? 'pos' : 'neg'),
    kpit('users', 'Dettes dehors', csKpi.total, csKpi.total > 0 ? 'neg' : '', { action: 'go', screen: 'carnet', tap: true, title: 'Voir le carnet' }),
    kpit('wallet', 'Trésorerie', R.caisse, '', { action: 'edit-caisse', tap: true, edit: true, title: 'Régler le fond de caisse' }),
  ];
  const dots = kpiTiles.map((_, i) => `<span class="kpicar__dot ${i === 0 ? 'is-on' : ''}" aria-hidden="true"></span>`).join('');
  const cashCard = `<article class="panel cashcard">
    <div class="cashcard__head">
      <div class="cashcard__id"><span class="cashcard__lbl">Aujourd'hui</span><span class="cashcard__date">${esc(dateStr)}</span></div>
      <div class="cashcard__acts">
        <button class="btn btn--ghost btn--sm" data-action="fab-depense"><span data-icon="minus"></span> Dépense</button>
        <button class="btn btn--sell btn--sm" data-action="fab-vente"><span data-icon="plus"></span> Vente</button>
      </div>
    </div>
    ${zhelp('Tes chiffres du jour. Glisse pour voir : encaissé, dépensé, bénéfice du jour, ce qu’on te doit, et ta trésorerie (touche-la pour régler ton fond de caisse).')}
    <div class="kpicar"><div class="kpicar__track" id="kpicar-track">${kpiTiles.join('')}</div></div>
    <div class="kpicar__dots">${dots}</div>
  </article>`;
  const legRow = (lbl, val, color, pct) => `<div class="leg__row"><span class="leg__dot" style="background:${color}"></span>
    <span class="leg__lbl">${lbl}</span><span class="leg__val">${formatF(val)}</span><span class="leg__pct">${pct}</span></div>`;

  // ---- HÉROS : CA + Bénéfice ----
  const hero = `<article class="panel c8 dhero">
    <div class="dhero__head">
      <div class="dhero__id">
        <span class="dhero__lbl">Chiffre d'affaires + Bénéfice</span>
        <h2 class="dhero__val" data-count="${t.revenu}" data-fmt="f">${formatF(t.revenu)}</h2>
        <span class="dhero__sub">${deltaBadge(D.deltas.revenu)} <em>vs ${esc(D.prevLabel)}</em></span>
      </div>
      <div class="dhero__leg">
        <span class="lg"><i style="background:var(--acc)"></i>CA</span>
        <span class="lg"><i style="background:var(--pos)"></i>Bénéfice</span>
      </div>
    </div>
    <div class="chartwrap">${chartHero(D)}</div>
  </article>`;

  // ---- OBJECTIF (mois courant, gamifié) ----
  const objCard = `<article class="panel c4 objx">
    <div class="panel__head"><h2>Objectif du mois</h2>
      <button class="btn btn--ghost btn--sm btn--icon" data-action="edit-objectif" title="Modifier l'objectif"><span data-icon="edit"></span></button></div>
    ${zhelp('Le bénéfice que tu veux atteindre ce mois-ci. L’anneau se remplit au fil de tes ventes. Touche le crayon pour changer le montant.')}
    ${objectif > 0 ? `
      <div class="objx__ring">${progressRing(pctObj, { color: 'var(--acc)', size: 140, stroke: 13 })}
        <div class="objx__center"><span class="objx__lvl" data-icon="flame"></span><strong><span data-count="${pctObj}" data-fmt="num">${pctObj}</span><small>%</small></strong></div></div>
      <div class="objx__meta"><b>${formatF(Math.max(0, benMois))}</b> / ${formatF(objectif)}</div>
      <p class="objx__hint">${benMois >= objectif ? 'Objectif atteint. Continue sur ta lancée.' : `Encore ${formatF(objectif - benMois)} pour l'atteindre ce mois-ci.`}</p>`
    : `<div class="objx__empty"><span class="objx__emptyic" data-icon="target"></span>
        <p>Fixe un objectif de bénéfice et suis ta progression chaque mois.</p>
        <button class="btn btn--sm" data-action="edit-objectif">Fixer un objectif</button></div>`}
  </article>`;

  // ---- KPIs colorés + comparaison ----
  const kpis = `<article class="panel c12 kpicard">
    <div class="kpis">
      ${kpiHTML("Chiffre d'affaires", formatF(t.revenu), D.deltas.revenu, D.buckets.map((x) => x.revenu), { sparkColor: 'var(--acc)', count: { n: t.revenu, fmt: 'f' } })}
      ${kpiHTML('Bénéfice net', formatF(t.benefice), D.deltas.benefice, D.buckets.map((x) => x.benefice), { valCls: t.benefice >= 0 ? 'pos' : 'neg', sparkColor: 'var(--pos)', count: { n: t.benefice, fmt: 'f' } })}
      ${kpiHTML('Taux de marge', pctMarge + ' %', D.deltas.tauxMarge, null, { delta: { pts: true }, count: { n: pctMarge, fmt: 'pct' } })}
      ${kpiHTML('Panier moyen', formatF(t.panierMoyen), D.deltas.panierMoyen, null, { count: { n: t.panierMoyen, fmt: 'f' } })}
      ${kpiHTML('Ventes', formatNombre(t.unites), D.deltas.unites, D.buckets.map((x) => x.unites), { sparkColor: 'var(--rel)', count: { n: t.unites, fmt: 'num' } })}
    </div>
  </article>`;

  // ---- VENTE RAPIDE ----
  const quick = produits.slice(0, 6).map((p) => `<button class="qsell" data-action="sell" data-id="${p.id}">
      <span class="qsell__nom">${esc(p.nom)}</span>
      <span class="qsell__row"><span class="qsell__price">${formatF(p.prix_vente)}</span><span class="qsell__plus" data-icon="plus"></span></span>
    </button>`).join('');
  const sellCard = `<article class="panel c12 sellcard">
    <div class="panel__head"><h2>Vendre en un clic</h2><button class="btn btn--ghost btn--sm" data-action="go" data-screen="ventes">Tout voir</button></div>
    <div class="quickrow">${quick}</div>
  </article>`;

  // ---- INDICATEURS (3 anneaux) ----
  const ringMini = (val, txt, sub, color) => `<div class="ring3">
    <div class="ring3__r">${progressRing(Math.max(0, val), { color, size: 78, stroke: 8 })}<span class="ring3__t">${txt}</span></div>
    <span class="ring3__s">${sub}</span></div>`;
  const ringsCard = `<article class="panel c4 ringscard">
    <div class="panel__head"><h2>Indicateurs clés</h2></div>
    <div class="rings3">
      ${ringMini(analyse.score, `${analyse.score}`, 'Santé /100', santeCol)}
      ${ringMini(pctMarge, `${pctMarge}%`, 'Taux de marge', 'var(--pos)')}
      ${ringMini(pctCharges, `${pctCharges}%`, 'Charges couvertes', 'var(--chg)')}
    </div>
  </article>`;

  // ---- DONUT « où va ton argent » (3 enveloppes) ----
  const envSegs = [
    { value: env.relance, color: 'var(--rel)' },
    { value: env.charges_couvertes, color: 'var(--chg)' },
    { value: env.depenses, color: '#9b8cff' },
    { value: Math.max(0, env.benefice), color: 'var(--pos)' },
  ];
  const envDonut = `<article class="panel c4 donutcard">
    <div class="panel__head"><h2>Où va ton argent</h2><span class="panel__sub">${esc(D.label)}</span></div>
    <div class="donutwrap">
      <div class="donut">${chartDonut(envSegs, { size: 168, stroke: 20 })}
        <div class="donut__center"><strong data-count="${env.revenu}" data-fmt="f">${formatF(env.revenu)}</strong><span>de ventes</span></div></div>
      <div class="leg">
        ${legRow('Relance', env.relance, 'var(--rel)', Math.round(env.relance / rTot * 100) + '%')}
        ${legRow('Charges', env.charges_couvertes, 'var(--chg)', Math.round(env.charges_couvertes / rTot * 100) + '%')}
        ${env.depenses > 0 ? legRow('Dépenses', env.depenses, '#9b8cff', Math.round(env.depenses / rTot * 100) + '%') : ''}
        ${legRow(env.a_perte ? 'Perte' : 'Bénéfice', env.a_perte ? env.marge : env.benefice, env.a_perte ? 'var(--dng)' : 'var(--pos)', Math.round(Math.max(0, env.benefice) / rTot * 100) + '%')}
      </div>
    </div>
  </article>`;

  // ---- DONUT ventes par produit ----
  const prodSegs = tops.map((p, i) => ({ value: p.revenu, color: PROD_COLORS[i % PROD_COLORS.length] }));
  const prodDonut = `<article class="panel c4 donutcard">
    <div class="panel__head"><h2>Ventes par produit</h2><span class="panel__sub">${esc(D.label)}</span></div>
    <div class="donutwrap">
      <div class="donut">${chartDonut(prodSegs.length ? prodSegs : [{ value: 0, color: 'var(--line)' }], { size: 168, stroke: 20 })}
        <div class="donut__center"><strong data-count="${tops.reduce((s, p) => s + p.unites, 0)}" data-fmt="num">${formatNombre(tops.reduce((s, p) => s + p.unites, 0))}</strong><span>unités</span></div></div>
      <div class="leg">
        ${tops.length ? tops.slice(0, 5).map((p, i) => legRow(esc(p.nom), p.revenu, PROD_COLORS[i % PROD_COLORS.length], Math.round(p.part * 100) + '%')).join('') : '<p class="leg__empty">Aucune vente sur la période.</p>'}
      </div>
    </div>
  </article>`;

  // ---- CLASSEMENT produits (sparkline) ----
  const rankRows = tops.length ? tops.map((p, i) => `<div class="rank">
      <span class="rank__n">${i + 1}</span>
      <div class="rank__id"><strong>${esc(p.nom)}</strong><small>${formatNombre(p.unites)} vendu${p.unites > 1 ? 's' : ''} · ${Math.round(p.part * 100)}%</small></div>
      <span class="rank__spark">${sparklineRaw(p.spark, { color: p.marge >= 0 ? 'var(--pos)' : 'var(--dng)', w: 96, h: 30 })}</span>
      <span class="rank__rev">${formatF(p.revenu)}</span>
    </div>`).join('') : '<p class="rank__empty">Aucune vente sur cette période. Change de période ou enregistre une vente.</p>';
  const rankCard = `<article class="panel c6 rankcard">
    <div class="panel__head"><h2>Meilleures ventes</h2><span class="panel__badge"><span data-icon="trophy"></span> ${esc(D.label)}</span></div>
    <div class="ranklist">${rankRows}</div>
  </article>`;

  // ---- BARRES bénéfice par unité de temps ----
  const barsCard = `<article class="panel c6">
    <div class="panel__head"><h2>Bénéfice par ${D.unit}</h2><span class="panel__sub">${esc(D.label)}</span></div>
    <div class="chartwrap">${chartBeneficeMensuel(D.buckets, { showValues: D.buckets.length <= 12 })}</div>
  </article>`;

  // ---- PRÉVISIONS (fin de mois, au rythme récent) ----
  const P2 = previsions();
  const prevCard = P2.actif ? `<article class="panel c6 prevcard">
    <div class="panel__head"><h2>Prévisions</h2><span class="panel__sub">fin du mois, à ce rythme</span></div>
    <div class="prevrow">
      <div class="prevtile"><span class="prevtile__lbl">Bénéfice fin de mois</span><span class="prevtile__val ${P2.benefFinMois >= 0 ? 'pos' : 'neg'}">${formatF(P2.benefFinMois)}</span></div>
      <div class="prevtile"><span class="prevtile__lbl">Caisse fin de mois</span><span class="prevtile__val">${formatF(P2.caisseFinMois)}</span></div>
    </div>
    <p class="prevhint">${P2.avgJour >= 0
      ? `Tu gagnes ~<b>${formatF(P2.avgJour)}</b>/jour en moyenne. Reste ${P2.joursRestants} jour${P2.joursRestants > 1 ? 's' : ''} ce mois.`
      : `Tu perds ~<b>${formatF(-P2.avgJour)}</b>/jour. Baisse une dépense ou pousse les ventes.`}</p>
  </article>` : '';

  // ---- CRÉDITS (clients qui doivent) ----
  const cs = creditsSummary();
  const creditsCard = `<article class="panel c6 creditcard">
    <div class="panel__head"><h2>Crédits</h2><button class="btn btn--ghost btn--sm" data-action="open-credits"><span data-icon="coins"></span> Gérer</button></div>
    ${cs.nb ? `
      <div class="creditsum"><span class="creditsum__lbl">On te doit</span><span class="creditsum__val">${formatF(cs.total)}</span><span class="creditsum__nb">${cs.nb} client${cs.nb > 1 ? 's' : ''} en attente</span></div>
      <ul class="creditmini">${cs.impayes.slice(0, 3).map((c) => `<li class="creditmini__row"><span class="creditmini__nom">${esc(c.client || 'Client')}</span><span class="creditmini__amt">${formatF(c.montant)}</span></li>`).join('')}</ul>`
      : `<div class="credit-empty"><span class="credit-empty__ic" data-icon="coins"></span><p>Aucune vente à crédit en cours.</p><button class="btn btn--sm" data-action="add-credit"><span data-icon="plus"></span> Ajouter un crédit</button></div>`}
  </article>`;

  // ---- CONSEIL ----
  const topConseil = analyse.conseils.find((c) => c.priorite !== 'info');
  const prio = topConseil ? (PRIO[topConseil.priorite] || PRIO.basse) : null;
  const conseilCard = topConseil ? `<article class="panel c12">
    <div class="panel__head"><h2>À améliorer</h2><span class="csl__tag" style="color:${prio.col}">${prio.lbl}</span></div>
    <strong class="hc__t">${esc(topConseil.titre)}</strong><p class="hc__d">${esc(topConseil.detail)}</p>
    <button class="btn btn--ghost btn--sm hc__more" data-action="go" data-screen="bilan">Voir le bilan complet <span data-icon="chevron"></span></button>
  </article>` : '';

  const journal = journalCaisse(10);
  const journalCard = journal.length ? `<article class="panel c6 jrncard">
    <div class="panel__head"><h2>Journal de caisse</h2><span class="panel__sub">dernières ventes</span></div>
    <ul class="jrn">${journal.map((j) => {
      const t = new Date(j.date); const hh = `${String(t.getHours()).padStart(2, '0')}:${String(t.getMinutes()).padStart(2, '0')}`;
      return `<li class="jrn__row"><span class="jrn__time">${hh}</span><span class="jrn__nom">${esc(j.nom)}</span><span class="jrn__q">×${formatNombre(j.qte)}</span><span class="jrn__amt">${formatF(j.montant)}</span></li>`;
    }).join('')}</ul>
  </article>` : '';

  return `<section class="view view--dash">
    <header class="dashhead">
      <div><p class="dashhead__greet">${greet},</p><h1 class="dashhead__nom">${esc(nom)}</h1></div>
      <span class="dashhead__time"><span data-icon="clock"></span>${timeStr}</span>
    </header>
    ${cashCard}
    ${alertsBlockHTML()}
    ${periodBarHTML(gran, offset, D.label)}
    <div class="dash">
      ${hero}
      ${objCard}
      ${objectifsCardHTML()}
      ${kpis}
      ${sellCard}
      ${ringsCard}
      ${envDonut}
      ${prodDonut}
      ${rankCard}
      ${barsCard}
      ${journalCard}
      ${prevCard}
      ${creditsCard}
      ${conseilCard}
    </div>
  </section>`;
}

// ============ ÉCRAN VENTES ============
function jourLabel(key) {
  const ymd = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  const t = new Date(); const today = ymd(t);
  const y = new Date(t); y.setDate(t.getDate() - 1);
  if (key === today) return "Aujourd'hui";
  if (key === ymd(y)) return 'Hier';
  return new Date(key + 'T12:00:00').toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' });
}
function hvRow(l) {
  const hm = new Date(l.date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  const modeLbl = PAYMENT_LABELS[l.mode] || '';
  return `<li class="hvrow">
    <span class="hvrow__ic" data-icon="${l.modele === 'revente' ? 'truck' : 'factory'}"></span>
    <div class="hvrow__id"><strong>${esc(l.nom)}</strong><small>${hm} · ${formatNombre(l.qte)} × ${formatF(l.prix_unitaire)}${modeLbl ? ` · ${modeLbl}` : ''}${l.vendeur ? ` · ${esc(l.vendeur)}` : ''}</small></div>
    <span class="hvrow__tot">${formatF(l.total)}</span>
    <button class="hvrow__recu" data-action="vf-recu" data-id="${l.id}" title="Reçu de caisse" aria-label="Reçu de caisse"><span data-icon="print"></span></button>
    <button class="hvrow__del" data-action="del-vente" data-id="${l.id}" aria-label="Supprimer la vente"><span data-icon="trash"></span></button>
  </li>`;
}

export function viewVentesHTML(filter = { preset: 'jour', from: '', to: '', produitId: '', q: '', mode: '', vendeur: '' }) {
  const produits = getProduits();
  const mk = currentMonthKey();

  if (produits.length === 0) {
    return `<section class="view">
      ${sectionTitle('Ventes', moisLabel(mk))}
      ${emptyState('box', 'Aucun produit configuré',
        'Commence par renseigner ton activité et les coûts de tes produits. Ensuite, vendre se fait en un clic.',
        'Configurer mon activité', 'go-config')}
    </section>`;
  }

  const b = bilanMois();
  const auj = new Date().toISOString().slice(0, 10);
  const ventesJour = getVentes().filter((v) => v.date.slice(0, 10) === auj);

  const tiles = produits.map((p) => {
    const marge = margeUnitaire(p);
    const nbJour = ventesJour.filter((v) => v.produit_id === p.id).reduce((s, v) => s + v.qte, 0);
    const margeClass = marge > 0 ? 'pos' : (marge < 0 ? 'neg' : 'zero');
    return `<article class="ptile">
      <div class="ptile__top">
        <div class="ptile__id">
          <span class="ptile__mk" data-icon="${p.modele === 'transformation' ? 'factory' : 'truck'}"></span>
          <div><h3 class="ptile__nom">${esc(p.nom)}</h3>
            <span class="ptile__marge ${margeClass}">marge ${formatF(marge)}/u</span></div>
        </div>
        ${nbJour > 0 ? `<span class="ptile__count">${nbJour} auj.</span>` : ''}
      </div>
      <div class="ptile__price"><span>${formatF(p.prix_vente)}</span><small>coût ${formatF(coutRevient(p))}</small></div>
      <div class="ptile__actions">
        <button class="btn btn--sell" data-action="sell" data-id="${p.id}">
          <span data-icon="plus"></span> 1 vente</button>
        <button class="btn btn--ghost btn--icon" data-action="sell-custom" data-id="${p.id}" title="Saisie détaillée">
          <span data-icon="edit"></span></button>
      </div>
    </article>`;
  }).join('');

  // ---- Historique + recherche ----
  const H = historiqueVentes({ from: filter.from, to: filter.to, produitId: filter.produitId, q: filter.q, mode: filter.mode, vendeur: filter.vendeur });
  const chip = (id, label) => `<button class="vchip ${filter.preset === id ? 'is-on' : ''}" data-action="vf-preset" data-preset="${id}">${label}</button>`;
  const prodOpts = ['<option value="">Tous les produits</option>']
    .concat(getProduits({ withArchived: true }).map((p) => `<option value="${p.id}" ${filter.produitId === p.id ? 'selected' : ''}>${esc(p.nom)}</option>`)).join('');
  const modeOpts = ['<option value="">Tous les paiements</option>']
    .concat(PAYMENT_MODES.map((m) => `<option value="${m}" ${filter.mode === m ? 'selected' : ''}>${PAYMENT_LABELS[m]}</option>`)).join('');
  const vends = getVendeurs();
  const vendOpts = vends.length ? ['<option value="">Tous les vendeurs</option>']
    .concat(vends.map((v) => `<option value="${esc(v)}" ${filter.vendeur === v ? 'selected' : ''}>${esc(v)}</option>`)).join('') : '';
  const groups = H.jours.length
    ? H.jours.map((g) => `<section class="daygrp">
        <div class="daygrp__head"><span class="daygrp__date">${esc(jourLabel(g.jour))}</span>
          <span class="daygrp__tot">${formatF(g.total)}<small>${formatNombre(g.unites)} u</small></span></div>
        <ul class="hvlist">${g.lignes.map(hvRow).join('')}</ul>
      </section>`).join('')
    : `<div class="hvempty"><span class="hvempty__ic" data-icon="ventes"></span>
        <p>Aucune vente sur cette sélection.</p>
        <span class="hvempty__hint">Change de période, ou enregistre une vente ci-dessus.</span></div>`;

  return `<section class="view" data-live>
    ${sectionTitle('Ventes', moisLabel(mk))}
    ${enveloppesHTML(b, { compact: true })}
    <button class="btn btn--sell btn--lg vcaisse-btn" data-action="fab-vente"><span data-icon="ventes"></span> Ouvrir la caisse</button>
    ${zhelp('Vente rapide : touche « 1 vente » sur un produit pour l’enregistrer d’un coup, ou « Ouvrir la caisse » pour un panier de plusieurs articles avec le mode de paiement.')}
    <div class="tiles">${tiles}</div>
    <article class="panel vhist">
      <div class="panel__head"><h2>Historique</h2><span class="panel__badge">${formatNombre(H.nb)} vente${H.nb > 1 ? 's' : ''} · ${formatF(H.total)}</span></div>
      ${zhelp('Toutes tes ventes passées, regroupées par jour. Filtre par période, produit, mode de paiement ou vendeur. Touche le reçu pour l’imprimer.')}
      <div class="vfilters">
        <div class="vchips">${chip('jour', "Aujourd'hui")}${chip('semaine', '7 jours')}${chip('mois', 'Ce mois')}${chip('tout', 'Tout')}</div>
        <div class="vfilters__dates">
          <label class="vf-field"><span>Du</span><input type="date" class="input" data-action="vf-from" value="${esc(filter.from)}"></label>
          <label class="vf-field"><span>Au</span><input type="date" class="input" data-action="vf-to" value="${esc(filter.to)}"></label>
        </div>
        <div class="vfilters__row">
          <select class="input vf-select" data-action="vf-produit" aria-label="Filtrer par produit">${prodOpts}</select>
          <select class="input vf-select" data-action="vf-mode" aria-label="Filtrer par paiement">${modeOpts}</select>
        </div>
        <div class="vfilters__row">
          ${vendOpts ? `<select class="input vf-select" data-action="vf-vendeur" aria-label="Filtrer par vendeur">${vendOpts}</select>` : ''}
          <div class="vf-search"><span class="vf-search__ic" data-icon="search"></span>
            <input class="input" type="search" data-action="vf-search" placeholder="Rechercher un produit…" value="${esc(filter.q)}" aria-label="Rechercher un produit"></div>
        </div>
      </div>
      <div class="hvgroups">${groups}</div>
    </article>
  </section>`;
}

// ============ ÉCRAN DÉPENSES ============
const CAT_COLORS = { 'Réassort / Stock': 'var(--rel)', 'Transport': '#9b8cff', 'Loyer': 'var(--chg)', 'Salaires': 'var(--dng)', 'Factures': 'var(--acc)', 'Divers': 'var(--ink-faint)' };
const catColor = (c) => CAT_COLORS[c] || 'var(--acc)';
function rangeLabel(f) {
  const m = { jour: "Aujourd'hui", semaine: '7 derniers jours', mois: 'Ce mois', tout: 'Tout' };
  return m[f.preset] || (f.from && f.to ? `du ${f.from} au ${f.to}` : 'période');
}
function dhRow(l) {
  const hm = new Date(l.date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  return `<li class="hvrow">
    <span class="hvrow__dot" style="background:${catColor(l.categorie)}"></span>
    <div class="hvrow__id"><strong>${esc(l.libelle || l.categorie)}</strong><small>${esc(l.categorie)} · ${hm}</small></div>
    <span class="hvrow__tot neg">-${formatF(l.montant)}</span>
    <button class="hvrow__del" data-action="del-depense" data-id="${l.id}" aria-label="Supprimer la dépense"><span data-icon="trash"></span></button>
  </li>`;
}

// Panneau « Abonnements & outils » (dépenses récurrentes → coûts fixes mensuels).
function abonnementsPanelHTML() {
  const rec = getDepensesRecurrentes();
  if (!rec.length) return '';
  const rows = rec.map((d) => `<li class="abrow">
    <div class="abrow__id"><strong>${esc(d.libelle || d.categorie)}</strong><small>${esc(d.categorie)} · ${d.frequence === 'annuel' ? 'chaque année' : 'chaque mois'}</small></div>
    <span class="abrow__amt">${formatF(d.montant)}<small>${d.frequence === 'annuel' ? '/an' : '/mois'}</small></span>
    <button class="hvrow__del" data-action="del-depense" data-id="${d.id}" aria-label="Supprimer"><span data-icon="trash"></span></button>
  </li>`).join('');
  return `<article class="panel">
    <div class="panel__head"><h2>Abonnements &amp; outils</h2><span class="panel__sub">coûts récurrents</span></div>
    ${zhelp('Tes abonnements et outils qui reviennent (Supabase, hébergement, Canva…). Boussole les compte automatiquement dans tes coûts fixes chaque mois.')}
    <div class="abtot"><span>Coût mensuel de tes outils</span><strong>${formatF(coutsRecurrentsMensuels())}<small> /mois</small></strong></div>
    <ul class="ablist">${rows}</ul>
  </article>`;
}

export function viewDepensesHTML(filter = { preset: 'mois', from: '', to: '', categorie: '', q: '' }) {
  const H = historiqueDepenses({ from: filter.from, to: filter.to, categorie: filter.categorie, q: filter.q });
  const chip = (id, label) => `<button class="vchip ${filter.preset === id ? 'is-on' : ''}" data-action="df-preset" data-preset="${id}">${label}</button>`;
  const catOpts = ['<option value="">Toutes catégories</option>']
    .concat(depenseCats().map((c) => `<option value="${esc(c)}" ${filter.categorie === c ? 'selected' : ''}>${esc(c)}</option>`)).join('');
  const breakdown = H.parCategorie.length ? `<div class="catbreak">${H.parCategorie.map((c) => `
      <div class="catbar">
        <div class="catbar__top"><span class="catbar__name"><span class="catbar__dot" style="background:${catColor(c.categorie)}"></span>${esc(c.categorie)}</span>
          <span class="catbar__amt">${formatF(c.total)}<small>${Math.round(c.part * 100)}%</small></span></div>
        <div class="catbar__track"><span style="width:${(c.part * 100).toFixed(1)}%;background:${catColor(c.categorie)}"></span></div>
      </div>`).join('')}</div>` : '';
  const groups = H.jours.length
    ? H.jours.map((g) => `<section class="daygrp">
        <div class="daygrp__head"><span class="daygrp__date">${esc(jourLabel(g.jour))}</span><span class="daygrp__tot neg">-${formatF(g.total)}</span></div>
        <ul class="hvlist">${g.lignes.map(dhRow).join('')}</ul></section>`).join('')
    : `<div class="hvempty"><span class="hvempty__ic" data-icon="receipt"></span>
        <p>Aucune dépense sur cette sélection.</p>
        <span class="hvempty__hint">Ajoute une dépense, ou change de période.</span></div>`;

  return `<section class="view">
    ${sectionTitle('Dépenses', "Où part ton argent")}
    ${zhelp('Tout ce qui sort de ta caisse : achats de marchandise, transport, loyer… Ajoute une dépense, vois la répartition par catégorie et retrouve l’historique. (Le « Réassort / Stock » ne compte pas dans le bénéfice : c’est déjà dans le coût de tes produits.)')}
    <div class="depsum">
      <div class="depsum__id"><span class="depsum__lbl">Total dépensé — ${esc(rangeLabel(filter))}</span>
        <span class="depsum__val neg">${formatF(H.total)}</span>
        <span class="depsum__nb">${formatNombre(H.nb)} dépense${H.nb > 1 ? 's' : ''}</span></div>
      <button class="btn btn--danger" data-action="add-depense"><span data-icon="minus"></span> Ajouter une dépense</button>
    </div>
    ${abonnementsPanelHTML()}
    ${breakdown ? `<article class="panel"><div class="panel__head"><h2>Par catégorie</h2><span class="panel__sub">${esc(rangeLabel(filter))}</span></div>${breakdown}</article>` : ''}
    <article class="panel vhist">
      <div class="panel__head"><h2>Historique</h2></div>
      <div class="vfilters">
        <div class="vchips">${chip('jour', "Aujourd'hui")}${chip('semaine', '7 jours')}${chip('mois', 'Ce mois')}${chip('tout', 'Tout')}</div>
        <div class="vfilters__dates">
          <label class="vf-field"><span>Du</span><input type="date" class="input" data-action="df-from" value="${esc(filter.from)}"></label>
          <label class="vf-field"><span>Au</span><input type="date" class="input" data-action="df-to" value="${esc(filter.to)}"></label>
        </div>
        <div class="vfilters__row">
          <select class="input vf-select" data-action="df-cat" aria-label="Filtrer par catégorie">${catOpts}</select>
          <div class="vf-search"><span class="vf-search__ic" data-icon="search"></span>
            <input class="input" type="search" data-action="df-search" placeholder="Rechercher…" value="${esc(filter.q)}" aria-label="Rechercher une dépense"></div>
        </div>
      </div>
      <div class="hvgroups">${groups}</div>
    </article>
    ${achatsPanelHTML()}
  </section>`;
}

// ============ ACHATS FOURNISSEURS ============
export function achatsPanelHTML() {
  const s = achatsSummary();
  const list = getAchats().slice(0, 6);
  const rows = list.length ? list.map(achatRowHTML).join('') : `<li class="docrow docrow--empty">Aucun achat. Enregistre un réassort : le stock des produits augmentera tout seul.</li>`;
  const sub = s.credit ? `<span class="panel__sub doccard__due"><span data-icon="alert"></span> ${formatF(s.credit)} à payer</span>` : `<span class="panel__sub">Réassorts & marchandise</span>`;
  return `<article class="panel doccard">
    <div class="panel__head"><h2>Achats fournisseurs</h2>${sub}</div>
    ${zhelp('Enregistre ce que tu achètes à tes fournisseurs. Le stock des produits augmente tout seul, ta caisse baisse (si payé), et ton bénéfice n’est pas touché — le coût est déjà dans ta marge.')}
    <div class="acsum">
      <div class="acsum__c"><span class="acsum__lbl">Ce mois</span><span class="acsum__val">${formatF(s.mois)}</span></div>
      <div class="acsum__c"><span class="acsum__lbl">Total</span><span class="acsum__val">${formatF(s.total)}</span></div>
      <div class="acsum__c ${s.credit ? 'is-dng' : ''}"><span class="acsum__lbl">À payer</span><span class="acsum__val">${formatF(s.credit)}</span></div>
    </div>
    <button class="btn btn--doc acnew" data-action="ac-new"><span data-icon="plus"></span> Nouvel achat</button>
    <ul class="doclist">${rows}</ul>
  </article>`;
}
function achatRowHTML(a) {
  const nbArt = (a.lignes || []).reduce((s, l) => s + (Number(l.qte) || 0), 0);
  const paye = a.statut === 'paye';
  return `<li class="docrow">
    <button class="docrow__main" data-action="ac-open" data-id="${a.id}">
      <span class="docrow__badge is-ach">Achat</span>
      <span class="docrow__body"><strong>${esc(a.fournisseur || 'Fournisseur')}</strong><small>${fmtDateFr(a.date)} · ${formatNombre(nbArt)} article${nbArt > 1 ? 's' : ''}</small></span>
      <span class="docrow__amt">${formatF(achatTotal(a))}<em class="docstat docstat--${paye ? 'paid' : 'due'}">${paye ? 'Payé' : 'À crédit'}</em></span>
    </button>
  </li>`;
}
export function achatFormFields(a) {
  const fourns = getFournisseurs();
  const datalist = fourns.length ? `<datalist id="ac-fourns">${fourns.map((f) => `<option value="${esc(f)}"></option>`).join('')}</datalist>` : '';
  const prods = getProduits();
  const lignes = (a.lignes && a.lignes.length) ? a.lignes : [{ produit_id: prods[0] ? prods[0].id : '', qte: 1, cout_unitaire: '' }];
  const statutChips = ACHAT_STATUTS.map((st) => `<button type="button" class="modechip ${((a.statut || 'paye') === st) ? 'is-on' : ''}" data-action="ac-statut" data-st="${st}">${st === 'paye' ? 'Payé' : 'À crédit'}</button>`).join('');
  return `<div class="achatform" data-id="${a.id || ''}" data-statut="${a.statut || 'paye'}">
    <div class="grid2">
      <div class="field"><label for="ac-four">Fournisseur</label><input id="ac-four" class="input" list="ac-fourns" value="${esc(a.fournisseur || '')}" placeholder="Ex. Grossiste Dantokpa" autocomplete="off">${datalist}</div>
      <div class="field"><label for="ac-date">Date</label><input id="ac-date" class="input" type="date" value="${esc(a.date || '')}"></div>
    </div>
    <div class="docform__sec">Marchandise achetée</div>
    <div id="ac-lignes" class="doclines">${achatLignesHTML(lignes)}</div>
    <button class="btn btn--ghost btn--sm docadd" data-action="ac-add-ligne"><span data-icon="plus"></span> Ajouter une ligne</button>
    <div class="field"><label>Paiement</label><div class="modechips">${statutChips}</div></div>
    <div class="field"><label for="ac-note">Note <span class="opt">(option)</span></label><textarea id="ac-note" class="input" rows="2" placeholder="Ex. Bon n°… , à régler vendredi">${esc(a.note || '')}</textarea></div>
    <div id="ac-tot" class="dtot">${achatTotalsHTML(lignes)}</div>
    ${zhelp('En enregistrant, le stock de ces produits augmente automatiquement. « Payé » = l’argent sort de ta caisse maintenant ; « À crédit » = tu dois encore ce montant au fournisseur.')}
  </div>`;
}
export function achatLignesHTML(lignes) {
  const prods = getProduits();
  const opts = (sel) => prods.map((p) => `<option value="${p.id}" ${sel === p.id ? 'selected' : ''}>${esc(p.nom)}</option>`).join('');
  return lignes.map((l, i) => {
    const montant = (Number(l.qte) || 0) * (Number(l.cout_unitaire) || 0);
    return `<div class="aline" data-i="${i}">
      <select class="input aline__prod" data-al="produit_id" aria-label="Produit">${opts(l.produit_id)}</select>
      <div class="aline__nums">
        <input class="input aline__q" type="number" inputmode="numeric" data-al="qte" value="${l.qte != null ? l.qte : ''}" placeholder="Qté" aria-label="Quantité">
        <span class="dline__x">×</span>
        <input class="input aline__pu" type="number" inputmode="numeric" data-al="cout_unitaire" value="${l.cout_unitaire != null ? l.cout_unitaire : ''}" placeholder="Coût" aria-label="Coût unitaire d'achat">
        <span class="aline__tot" data-al-tot>${formatF(montant)}</span>
        <button class="dline__del" data-action="ac-del-ligne" data-i="${i}" aria-label="Retirer la ligne"><span data-icon="close"></span></button>
      </div>
    </div>`;
  }).join('');
}
export function achatTotalsHTML(lignes) {
  return `<div class="dtot__row dtot__row--total"><span>Total achat</span><span class="dtot__v">${formatF(achatTotal({ lignes }))}</span></div>`;
}

// ---- Statistiques (KPIs) ----
const SANTE = {
  bonne: { lbl: 'Bonne santé', col: 'var(--pos-d)', soft: 'var(--pos-soft)' },
  moyenne: { lbl: 'Santé moyenne', col: 'var(--chg)', soft: 'var(--chg-soft)' },
  fragile: { lbl: 'Santé fragile', col: 'var(--dng)', soft: 'var(--dng-soft)' },
  demarrage: { lbl: 'Démarrage', col: 'var(--ink-faint)', soft: 'var(--glass-fill)' },
};
const PRIO = {
  haute: { col: 'var(--dng)', lbl: 'Priorité' },
  moyenne: { col: 'var(--chg)', lbl: 'À surveiller' },
  basse: { col: 'var(--rel)', lbl: 'Conseil' },
  info: { col: 'var(--acc)', lbl: 'Info' },
};

export function statsHTML(st) {
  const stat = (lbl, val, sub, cls = '') => `<div class="stat">
    <span class="stat__lbl">${lbl}</span>
    <span class="stat__val ${cls}">${val}</span>
    ${sub ? `<span class="stat__sub">${sub}</span>` : ''}</div>`;
  const m = st.mois;
  return `<div class="stats">
    ${stat("Chiffre d'affaires", formatF(m.revenu), 'ce mois')}
    ${stat('Bénéfice net', formatF(m.benefice), 'ce mois', m.benefice > 0 ? 'pos' : (m.benefice < 0 ? 'neg' : ''))}
    ${stat('Taux de marge', Math.round(m.tauxMarge * 100) + ' %', 'sur les ventes')}
    ${stat('Panier moyen', formatF(m.panierMoyen), 'par vente')}
    ${stat('Ventes', formatNombre(m.unites), 'unités ce mois')}
    ${stat("CA cumulé", formatF(st.global.revenu), 'depuis le début')}
  </div>`;
}

function scoreRing(score, col) {
  const r = 32, c = 2 * Math.PI * r, off = c * (1 - score / 100);
  return `<svg viewBox="0 0 78 78" class="ring" aria-hidden="true">
    <defs><filter id="sr${score}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
    <circle cx="39" cy="39" r="${r}" fill="none" style="stroke:var(--line)" stroke-width="7.5"/>
    <circle class="ring__p" cx="39" cy="39" r="${r}" fill="none" style="stroke:${col}" stroke-width="7.5" stroke-linecap="round"
      stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${off.toFixed(1)}" transform="rotate(-90 39 39)" filter="url(#sr${score})"/>
    <text x="39" y="46" text-anchor="middle" class="ring__t">${score}</text>
  </svg>`;
}

// ---- Rapport automatique (analyse + conseils) ----
export function rapportHTML(a) {
  const s = SANTE[a.sante] || SANTE.demarrage;
  const etat = a.etat.map((p) => `<li>${esc(p)}</li>`).join('');
  const conseils = a.conseils.length
    ? a.conseils.map((c) => { const pr = PRIO[c.priorite] || PRIO.basse; return `<div class="csl">
        <span class="csl__dot" style="background:${pr.col}"></span>
        <div class="csl__body"><span class="csl__tag" style="color:${pr.col}">${pr.lbl}</span>
          <strong>${esc(c.titre)}</strong><p>${esc(c.detail)}</p></div></div>`; }).join('')
    : `<div class="csl csl--none"><span class="csl__dot" style="background:var(--acc)"></span>
        <div class="csl__body"><strong>Rien d'urgent</strong><p>Continue sur cette lancée et surveille tes marges.</p></div></div>`;
  const forts = a.forts.length ? `<div class="forts"><h3>Points forts</h3>
      ${a.forts.map((f) => `<div class="fort"><span data-icon="check"></span>${esc(f)}</div>`).join('')}</div>` : '';
  return `<div class="panel rapport">
    <div class="panel__head"><h2>Rapport & conseils</h2><span class="panel__sub">analyse automatique</span></div>
    <div class="diag">
      <div class="diag__score" style="background:${s.soft}">
        ${scoreRing(a.score, s.col)}
        <span class="diag__sante" style="color:${s.col}">${s.lbl}</span>
        <span class="diag__scoresub">santé /100</span>
      </div>
      <ul class="diag__etat">${etat}</ul>
    </div>
    <div class="conseils"><h3>À améliorer</h3>${conseils}</div>
    ${forts}
  </div>`;
}

// ============ ÉCRAN BILAN ============
// Palmarès de la période : « Ça cartonne » (tops) + « À relancer » (flops). Suit la période du Rapport.
function palmaresPanelHTML(gran) {
  const P = palmaresProduits(gran, 0, 5);
  const flopIc = { perte: 'alert', dormant: 'moon', stockdort: 'box', faible: 'arrowDown' };
  const maxRev = Math.max(1, ...P.tops.map((t) => t.revenu));

  const topRows = P.tops.length ? P.tops.map((t, i) => `<li class="plm plm--top">
      <span class="plm__rk">${i + 1}</span>
      <div class="plm__id">
        <div class="plm__line"><strong>${esc(t.nom)}</strong><span class="plm__val pos">${formatF(t.revenu)}</span></div>
        <div class="plm__bar" aria-hidden="true"><i style="width:${Math.max(4, Math.round(t.revenu / maxRev * 100))}%"></i></div>
        <small>${formatNombre(t.unites)} vendu${t.unites > 1 ? 's' : ''} · ${Math.round(t.part * 100)}% du CA</small>
      </div>
    </li>`).join('')
    : `<li class="plm__empty">Aucune vente enregistrée sur cette période.</li>`;

  const flopRows = P.flops.length ? P.flops.map((f) => `<li class="plm plm--flop plm--${f.statut}">
      <span class="plm__ic" data-icon="${flopIc[f.statut] || 'alert'}"></span>
      <div class="plm__id">
        <div class="plm__line"><strong>${esc(f.nom)}</strong><span class="plm__tag">${f.raison}</span></div>
        <small>${esc(f.conseil)}</small>
      </div>
    </li>`).join('')
    : `<li class="plm__good"><span data-icon="check"></span> Rien à signaler : tous tes produits tournent bien sur la période.</li>`;

  return `<article class="panel palmcard">
    <div class="panel__head"><h2>Palmarès produits</h2><span class="panel__sub">${esc(P.label)}</span></div>
    ${zhelp('Ce qui marche et ce qui coince sur la période. À gauche, tes locomotives (classées par chiffre d’affaires). À droite, les produits à relancer : vendus à perte, jamais vendus, stock qui dort, ou qui se vendent peu — avec le geste à faire.')}
    <div class="palm">
      <div class="palm__col">
        <h3 class="palm__h palm__h--top"><span data-icon="trophy"></span> Ça cartonne</h3>
        <ul class="plmlist">${topRows}</ul>
      </div>
      <div class="palm__col">
        <h3 class="palm__h palm__h--flop"><span data-icon="alert"></span> À relancer</h3>
        <ul class="plmlist">${flopRows}</ul>
      </div>
    </div>
  </article>`;
}

export function viewBilanHTML(rapGran = 'jour') {
  const produits = getProduits();
  const b = bilanMois();
  const serie = serieMensuelle(6);
  const tri = trimestreDe();
  const mk = currentMonthKey();
  const stats = statistiques(mk);
  const analyse = analyseBusiness();

  if (getVentes().length === 0 && produits.length === 0) {
    return `<section class="view">${sectionTitle('Bilan', 'Vue d\'ensemble')}
      ${emptyState('bilan', 'Rien à analyser pour l\'instant', 'Configure ton activité et enregistre tes premières ventes : les statistiques, courbes et conseils apparaîtront ici.', 'Configurer mon activité', 'go-config')}</section>`;
  }

  const perf = produits.map((p) => {
    const s = seuilRentabilite(p);
    return `<li class="perf">
      <span class="perf__nom">${esc(p.nom)}</span>
      <span class="perf__marge ${margeUnitaire(p) >= 0 ? 'pos' : 'neg'}">${formatF(margeUnitaire(p))}/u</span>
      <span class="perf__seuil">${s === Infinity ? '—' : `${s} u/mois`}</span>
    </li>`;
  }).join('');

  const triRows = tri.mois.map((m) => `<tr>
      <td>${esc(m.label)}</td>
      <td class="num">${formatF(m.revenu)}</td>
      <td class="num">${formatF(m.relance)}</td>
      <td class="num">${formatF(m.charges_couvertes)}</td>
      <td class="num ${m.benefice > 0 ? 'pos' : (m.benefice < 0 ? 'neg' : '')}">${formatF(m.benefice)}</td>
    </tr>`).join('');

  const verdict = tri.totaux.benefice > 0
    ? `<span class="verdict verdict--ok"><span data-icon="check"></span> Activité rentable ce trimestre : ${formatF(tri.totaux.benefice)} de bénéfice net.</span>`
    : `<span class="verdict verdict--warn"><span data-icon="alert"></span> Pas encore rentable ce trimestre. Vise le seuil de rentabilité par produit.</span>`;
  const tendance = tri.tendance !== 0
    ? `<span class="trend ${tri.tendance > 0 ? 'pos' : 'neg'}"><span data-icon="${tri.tendance > 0 ? 'arrowUp' : 'arrowDown'}"></span> ${tri.tendance > 0 ? '+' : ''}${formatF(tri.tendance)} entre le début et la fin du trimestre</span>`
    : '';

  // ---- Panneau RAPPORT (période + résumé + exports PDF/Excel/WhatsApp) ----
  const RG = rapportPeriode(rapGran, 0);
  const rchip = (g, l) => `<button class="vchip ${rapGran === g ? 'is-on' : ''}" data-action="rap-gran" data-gran="${g}">${l}</button>`;
  const rstat = (lbl, val, cls = '') => `<div class="rstat"><span class="rstat__lbl">${lbl}</span><span class="rstat__val ${cls}">${val}</span></div>`;
  const rapportPanel = `<article class="panel rapportcard">
    <div class="panel__head"><h2>Rapport</h2><span class="panel__sub">${esc(RG.label)}</span></div>
    ${zhelp('Le résumé chiffré de ton activité sur la période choisie (jour, semaine, mois, année). Exporte-le en PDF ou Excel, ou envoie-le par WhatsApp.')}
    <div class="vchips">${rchip('jour', 'Jour')}${rchip('semaine', 'Semaine')}${rchip('mois', 'Mois')}${rchip('annee', 'Année')}</div>
    <div class="rsum">
      ${rstat("Chiffre d'affaires", formatF(RG.ca))}
      ${rstat('Dépenses', formatF(RG.depenses), RG.depenses > 0 ? 'neg' : '')}
      ${rstat('Bénéfice net', formatF(RG.benefice), RG.benefice >= 0 ? 'pos' : 'neg')}
      ${rstat('Solde de caisse', formatF(RG.caisse))}
      ${rstat('Ventes', formatNombre(RG.nbVentes))}
      ${rstat('Taux de marge', Math.round(RG.tauxMarge * 100) + ' %')}
    </div>
    <div class="rexport">
      <button class="btn" data-action="rap-pdf"><span data-icon="print"></span> PDF</button>
      <button class="btn btn--ghost" data-action="rap-csv"><span data-icon="download"></span> Excel</button>
      <button class="btn btn--ghost" data-action="rap-wa"><span data-icon="whatsapp"></span> WhatsApp</button>
    </div>
  </article>`;

  return `<section class="view">
    ${sectionTitle('Bilan', moisLabel(mk))}
    ${zhelp('Ton analyse complète : rapport exportable, factures & devis, santé de ton commerce, courbes d’évolution et conseils. Tout part de tes ventes et dépenses.')}
    ${rapportPanel}
    ${palmaresPanelHTML(rapGran)}
    ${documentsPanelHTML()}
    ${enveloppesHTML(b)}
    ${statsHTML(stats)}
    ${rapportHTML(analyse)}
    <div class="panel">
      <div class="panel__head"><h2>Évolution revenu &amp; bénéfice</h2><span class="panel__sub">6 derniers mois</span></div>
      <div class="chartwrap">${chartEvolution(serie)}</div>
    </div>
    <div class="panel">
      <div class="panel__head"><h2>Bénéfice net par mois</h2><span class="panel__sub">tendance</span></div>
      <div class="chartwrap">${chartBeneficeMensuel(serie)}</div>
    </div>
    <div class="panel">
      <div class="panel__head">
        <h2>Bilan trimestriel — T${tri.numero} ${tri.annee}</h2>
        <div class="panel__tools">
          <button class="btn btn--ghost btn--sm" data-action="share-bilan"><span data-icon="whatsapp"></span> Partager</button>
          <button class="btn btn--ghost btn--sm" data-action="print-bilan"><span data-icon="print"></span> Imprimer</button>
        </div>
      </div>
      <div class="tablewrap"><table class="tbl">
        <thead><tr><th>Mois</th><th class="num">Revenu</th><th class="num">Relance</th><th class="num">Charges</th><th class="num">Bénéfice</th></tr></thead>
        <tbody>${triRows}</tbody>
        <tfoot><tr><td>Total</td><td class="num">${formatF(tri.totaux.revenu)}</td><td class="num">${formatF(tri.totaux.relance)}</td><td class="num">${formatF(tri.totaux.charges_couvertes)}</td><td class="num ${tri.totaux.benefice >= 0 ? 'pos' : 'neg'}">${formatF(tri.totaux.benefice)}</td></tr></tfoot>
      </table></div>
      <div class="verdicts">${verdict}${tendance}</div>
    </div>
    <div class="panel">
      <div class="panel__head"><h2>Par produit</h2><span class="panel__sub">marge & seuil de rentabilité</span></div>
      <ul class="perflist"><li class="perf perf--head"><span>Produit</span><span>Marge unité</span><span>Seuil/mois</span></li>${perf}</ul>
    </div>
  </section>`;
}

// ============ FACTURES & DEVIS ============
function docCur() { return (CURRENCIES[getDevise()] || CURRENCIES.F).symbol; }
function fmtDateFr(ymd) {
  if (!ymd) return '';
  const m = String(ymd).match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (m) return `${m[3]}/${m[2]}/${m[1]}`;
  const d = new Date(ymd); if (isNaN(d)) return String(ymd);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
}
function capFirst(s) { s = String(s || ''); return s.charAt(0).toUpperCase() + s.slice(1); }
function docStatut(d) {
  if (d.type === 'facture') return d.statut === 'payee' ? { label: 'Payée', cls: 'paid' } : { label: 'Impayée', cls: 'due' };
  if (d.statut === 'accepte') return { label: 'Accepté', cls: 'paid' };
  if (d.statut === 'refuse') return { label: 'Refusé', cls: 'no' };
  return { label: 'En attente', cls: 'wait' };
}

// Panneau « Factures & devis » (écran Bilan)
export function documentsPanelHTML() {
  const s = documentsSummary();
  const docs = getDocuments().slice(0, 6);
  const rows = docs.length
    ? docs.map(docRowHTML).join('')
    : `<li class="docrow docrow--empty">Aucun document pour l'instant. Crée une facture ou un devis pour un client.</li>`;
  const sub = s.nbImpayees
    ? `<span class="panel__sub doccard__due"><span data-icon="alert"></span> ${s.nbImpayees} impayée${s.nbImpayees > 1 ? 's' : ''} · ${formatF(s.totalImpaye)}</span>`
    : `<span class="panel__sub">Documents propres pour tes clients</span>`;
  return `<article class="panel doccard">
    <div class="panel__head"><h2>Factures &amp; devis</h2>${sub}</div>
    ${zhelp('Crée des factures et des devis propres pour tes clients (numéro auto, montant en toutes lettres, ton IFU). Imprime-les en PDF ou envoie-les par WhatsApp.')}
    <div class="doccta">
      <button class="btn btn--doc" data-action="doc-new" data-type="facture"><span data-icon="receipt"></span> Nouvelle facture</button>
      <button class="btn btn--ghost" data-action="doc-new" data-type="devis"><span data-icon="doc"></span> Nouveau devis</button>
    </div>
    <ul class="doclist">${rows}</ul>
  </article>`;
}
function docRowHTML(d) {
  const t = documentTotals(d);
  const isFac = d.type === 'facture';
  const st = docStatut(d);
  return `<li class="docrow">
    <button class="docrow__main" data-action="doc-open" data-id="${d.id}">
      <span class="docrow__badge ${isFac ? 'is-fac' : 'is-dev'}">${isFac ? 'Facture' : 'Devis'}</span>
      <span class="docrow__body"><strong>${esc(d.numero)}</strong><small>${esc(d.client && d.client.nom || 'Client')} · ${fmtDateFr(d.date)}</small></span>
      <span class="docrow__amt">${formatF(t.total)}<em class="docstat docstat--${st.cls}">${st.label}</em></span>
    </button>
    <div class="docrow__acts">
      <button class="doc-btn" data-action="doc-pdf" data-id="${d.id}" title="Aperçu / PDF" aria-label="Aperçu ou PDF"><span data-icon="print"></span></button>
      <button class="doc-btn doc-btn--wa" data-action="doc-wa" data-id="${d.id}" title="Envoyer par WhatsApp" aria-label="Envoyer par WhatsApp"><span data-icon="whatsapp"></span></button>
    </div>
  </li>`;
}

// Éditeur (corps de la modale)
export function docFormFields(doc) {
  const isFac = doc.type === 'facture';
  const cur = docCur();
  const hasId = Boolean(doc.id);
  const lignes = (doc.lignes && doc.lignes.length) ? doc.lignes : [{ designation: '', qte: 1, pu: 0 }];
  const statutCtrl = hasId ? `<div class="docstat-ctrl">
      <span class="docstat-ctrl__lbl">Statut</span>
      <div class="seg seg--stat">${(isFac
        ? [['impayee', 'Impayée'], ['payee', 'Payée']]
        : [['en_attente', 'En attente'], ['accepte', 'Accepté'], ['refuse', 'Refusé']]
      ).map(([v, l]) => `<button class="seg__b ${doc.statut === v ? 'is-on' : ''}" data-action="doc-set-statut" data-id="${doc.id}" data-statut="${v}">${l}</button>`).join('')}</div>
    </div>` : '';
  return `<div class="docform" data-type="${doc.type}" data-id="${doc.id || ''}" data-numero="${esc(doc.numero || '')}">
    <div class="docform__lead"><span class="docrow__badge ${isFac ? 'is-fac' : 'is-dev'}">${isFac ? 'Facture' : 'Devis'}</span><strong>${esc(doc.numero || '')}</strong></div>
    ${statutCtrl}
    <div class="field"><label for="dc-client">Client</label>
      <input id="dc-client" class="input" data-df="nom" value="${esc(doc.client && doc.client.nom || '')}" placeholder="Nom du client" autocomplete="off"></div>
    <div class="grid2">
      <div class="field"><label for="dc-tel">Téléphone / WhatsApp</label>
        <input id="dc-tel" class="input" type="tel" inputmode="tel" data-df="tel" value="${esc(doc.client && doc.client.tel || '')}" placeholder="Ex. 22997000000"></div>
      <div class="field"><label for="dc-adr">Adresse <span class="opt">(option)</span></label>
        <input id="dc-adr" class="input" data-df="adresse" value="${esc(doc.client && doc.client.adresse || '')}" placeholder="Ville / quartier"></div>
    </div>
    <div class="grid2">
      <div class="field"><label for="dc-date">Date</label>
        <input id="dc-date" class="input" type="date" data-df="date" value="${esc(doc.date || '')}"></div>
      <div class="field"><label for="dc-ech">${isFac ? 'Échéance' : 'Valable jusqu\'au'} <span class="opt">(option)</span></label>
        <input id="dc-ech" class="input" type="date" data-df="echeance" value="${esc(doc.echeance || '')}"></div>
    </div>
    <div class="docform__sec">Articles</div>
    <div id="dc-lignes" class="doclines">${docLignesHTML(lignes)}</div>
    <button class="btn btn--ghost btn--sm docadd" data-action="doc-add-ligne"><span data-icon="plus"></span> Ajouter une ligne</button>
    <div class="grid2">
      <div class="field"><label for="dc-remise">Remise <span class="opt">(${cur})</span></label>
        <input id="dc-remise" class="input" type="number" inputmode="numeric" data-df="remise" value="${doc.remise || ''}" placeholder="0"></div>
      <div class="field"><label for="dc-tva">TVA <span class="opt">(%)</span></label>
        <input id="dc-tva" class="input" type="number" inputmode="decimal" data-df="tva_taux" value="${doc.tva_taux || ''}" placeholder="0"></div>
    </div>
    ${isFac ? `<div class="field"><label for="dc-acompte">Acompte déjà versé <span class="opt">(${cur})</span></label>
      <input id="dc-acompte" class="input" type="number" inputmode="numeric" data-df="acompte" value="${doc.acompte || ''}" placeholder="0"></div>` : ''}
    <div class="field"><label for="dc-notes">Note <span class="opt">(conditions, mode de paiement…)</span></label>
      <textarea id="dc-notes" class="input" rows="2" data-df="notes" placeholder="Ex. Paiement Mobile Money au 97 00 00 00. Merci de votre confiance.">${esc(doc.notes || '')}</textarea></div>
    <div id="dc-tot">${docTotalsHTML(doc)}</div>
    <div class="docactions">
      <button class="btn btn--ghost" data-action="doc-save-pdf" data-id="${doc.id || ''}"><span data-icon="print"></span> Aperçu / PDF</button>
      <button class="btn btn--doc" data-action="doc-save-wa" data-id="${doc.id || ''}"><span data-icon="whatsapp"></span> Enregistrer &amp; envoyer</button>
    </div>
    ${hasId ? `<button class="btn btn--danger-ghost btn--sm docdel" data-action="doc-del" data-id="${doc.id}"><span data-icon="trash"></span> Supprimer ce document</button>` : ''}
  </div>`;
}
export function docLignesHTML(lignes) {
  return lignes.map((l, i) => {
    const montant = (Number(l.qte) || 0) * (Number(l.pu) || 0);
    return `<div class="dline" data-i="${i}">
      <input class="input dline__des" data-dl="designation" value="${esc(l.designation || '')}" placeholder="Désignation (ex. Robe pagne cousue main)" autocomplete="off">
      <div class="dline__nums">
        <input class="input dline__q" type="number" inputmode="numeric" data-dl="qte" value="${l.qte != null ? l.qte : ''}" placeholder="Qté" aria-label="Quantité">
        <span class="dline__x">×</span>
        <input class="input dline__pu" type="number" inputmode="numeric" data-dl="pu" value="${l.pu != null ? l.pu : ''}" placeholder="P.U." aria-label="Prix unitaire">
        <span class="dline__tot" data-dl-tot>${formatF(montant)}</span>
        <button class="dline__del" data-action="doc-del-ligne" data-i="${i}" title="Retirer la ligne" aria-label="Retirer la ligne"><span data-icon="close"></span></button>
      </div>
    </div>`;
  }).join('');
}
export function docTotalsHTML(doc) {
  const t = documentTotals(doc);
  const isFac = doc.type === 'facture';
  const row = (l, v, cls = '') => `<div class="dtot__row ${cls}"><span>${l}</span><span class="dtot__v">${formatF(v)}</span></div>`;
  return `<div class="dtot">
    ${row('Sous-total', t.sousTotal)}
    ${t.remise ? row('Remise', -t.remise, 'is-neg') : ''}
    ${t.tva ? row(`TVA (${doc.tva_taux}%)`, t.tva) : ''}
    ${row('Total', t.total, 'dtot__row--total')}
    ${isFac && t.acompte ? row('Acompte versé', -t.acompte, 'is-neg') : ''}
    ${isFac && t.acompte ? row('Net à payer', t.net, 'dtot__row--net') : ''}
  </div>`;
}

// Mise en page imprimable (A4) — facture / devis « propre »
export function documentPrintHTML(doc) {
  const p = getState().profil;
  const t = documentTotals(doc);
  const isFac = doc.type === 'facture';
  const titre = isFac ? 'FACTURE' : 'DEVIS';
  const curLong = getDevise() === 'F' ? 'francs CFA' : docCur();
  const lignes = (doc.lignes || []).filter((l) => l.designation || l.qte || l.pu).map((l) => {
    const m = (Number(l.qte) || 0) * (Number(l.pu) || 0);
    return `<tr><td class="fd-l">${esc(l.designation || '')}</td><td class="num">${formatNombre(l.qte || 0)}</td><td class="num">${formatF(l.pu || 0)}</td><td class="num">${formatF(m)}</td></tr>`;
  }).join('');
  const lettres = capFirst(montantEnLettres(t.total)) + ' ' + curLong;
  const fisc = [p.ifu ? `IFU : ${esc(p.ifu)}` : '', p.rccm ? `RCCM : ${esc(p.rccm)}` : ''].filter(Boolean).join('&nbsp;·&nbsp;');
  return `<div class="facdoc">
    <header class="fd-head">
      <div class="fd-vendor">
        <h2>${esc(p.nom_activite || 'Mon activité')}</h2>
        ${p.adresse ? `<p>${esc(p.adresse)}</p>` : ''}
        ${p.tel_pro ? `<p>Tél : ${esc(p.tel_pro)}</p>` : ''}
        ${p.email_pro ? `<p>${esc(p.email_pro)}</p>` : ''}
        ${fisc ? `<p class="fd-fisc">${fisc}</p>` : ''}
      </div>
      <div class="fd-meta">
        <h1>${titre}</h1>
        <p class="fd-num">N° ${esc(doc.numero)}</p>
        <p>Date : ${fmtDateFr(doc.date)}</p>
        ${doc.echeance ? `<p>${isFac ? 'Échéance' : 'Valable jusqu\'au'} : ${fmtDateFr(doc.echeance)}</p>` : ''}
      </div>
    </header>
    <section class="fd-client">
      <span class="fd-client__lbl">${isFac ? 'Facturé à' : 'Client'}</span>
      <strong>${esc(doc.client && doc.client.nom || '—')}</strong>
      ${doc.client && doc.client.tel ? `<span>${esc(doc.client.tel)}</span>` : ''}
      ${doc.client && doc.client.adresse ? `<span>${esc(doc.client.adresse)}</span>` : ''}
    </section>
    <table class="fd-tbl">
      <thead><tr><th class="fd-l">Désignation</th><th class="num">Qté</th><th class="num">P.U.</th><th class="num">Montant</th></tr></thead>
      <tbody>${lignes || '<tr><td colspan="4" class="fd-l">—</td></tr>'}</tbody>
    </table>
    <div class="fd-bottom">
      <div class="fd-left">
        <p class="fd-lettres"><strong>Arrêté${isFac ? ' la présente facture' : ' le présent devis'} à la somme de :</strong><br>${lettres}.</p>
        ${doc.notes ? `<p class="fd-note">${esc(doc.notes)}</p>` : ''}
        <div class="fd-sign"><span>Signature &amp; cachet</span></div>
      </div>
      <div class="fd-tot">
        <div class="fd-tot__row"><span>Sous-total</span><span>${formatF(t.sousTotal)}</span></div>
        ${t.remise ? `<div class="fd-tot__row"><span>Remise</span><span>− ${formatF(t.remise)}</span></div>` : ''}
        ${t.tva ? `<div class="fd-tot__row"><span>TVA (${doc.tva_taux}%)</span><span>${formatF(t.tva)}</span></div>` : ''}
        <div class="fd-tot__row fd-tot__row--total"><span>Total</span><span>${formatF(t.total)}</span></div>
        ${isFac && t.acompte ? `<div class="fd-tot__row"><span>Acompte versé</span><span>− ${formatF(t.acompte)}</span></div>` : ''}
        ${isFac && t.acompte ? `<div class="fd-tot__row fd-tot__row--net"><span>Net à payer</span><span>${formatF(t.net)}</span></div>` : ''}
      </div>
    </div>
    <p class="fd-legal">${isFac ? 'Facture' : 'Devis'} n° ${esc(doc.numero)} — établi avec Boussole.</p>
  </div>`;
}

// ============ OBJECTIFS MULTIPLES (carte tableau de bord) ============
export function objectifsCardHTML() {
  const os = getObjectifs();
  if (!os.length) {
    return `<article class="panel c6 objscard">
      <div class="panel__head"><h2>Mes objectifs</h2><button class="btn btn--sm" data-action="obj-new"><span data-icon="plus"></span> Objectif</button></div>
      <div class="objs-empty"><span class="objs-empty__ic" data-icon="target"></span><p>Fixe-toi des projets — acheter un outil, une machine, une maison… — et regarde ta cagnotte grandir.</p></div>
    </article>`;
  }
  const rows = os.slice(0, 5).map((o) => {
    const i = objectifInfo(o); const pct = Math.round(i.taux * 100);
    return `<div class="objrow ${i.atteint ? 'is-done' : ''}">
      <button class="objrow__main" data-action="obj-open" data-id="${o.id}">
        <span class="objrow__ic" data-icon="${o.icone || 'target'}"></span>
        <span class="objrow__body">
          <span class="objrow__top"><strong>${esc(o.titre || 'Objectif')}</strong><em>${i.atteint ? 'Atteint' : pct + ' %'}</em></span>
          <span class="objrow__bar"><i style="width:${pct}%"></i></span>
          <span class="objrow__sub">${formatF(i.actuel)} / ${formatF(i.cible)}${o.echeance ? ` · ${esc(o.echeance)}` : ''}</span>
        </span>
      </button>
      <button class="objrow__add" data-action="obj-contrib" data-id="${o.id}" title="Ajouter de l'argent" aria-label="Ajouter de l'argent"><span data-icon="plus"></span></button>
    </div>`;
  }).join('');
  return `<article class="panel c6 objscard">
    <div class="panel__head"><h2>Mes objectifs</h2><button class="btn btn--sm" data-action="obj-new"><span data-icon="plus"></span> Objectif</button></div>
    ${zhelp('Tes cagnottes pour tes projets (outil, machine, maison…). Le bouton + ajoute de l’argent à un objectif ; touche un objectif pour le modifier.')}
    <div class="objlist">${rows}</div>
  </article>`;
}

// ============ CAISSE (panier POS) + REÇU ============
export function caisseHTML(cart, mode, vendeur) {
  const prods = getProduits();
  const dig = isDigital();
  const tiles = prods.length
    ? prods.map((p) => `<button class="qsell caisse__prod" data-action="cart-add" data-id="${p.id}"><span class="qsell__nom">${esc(p.nom)}</span><span class="qsell__price">${formatF(p.prix_vente)}${dig ? esc(TARIF_UNITS[p.tarif_type] || '') : ''}</span></button>`).join('')
    : `<p class="modal__note">${dig ? 'Aucune prestation. Ajoute-en dans le catalogue.' : 'Aucun produit. Ajoute-en dans Réglages.'}</p>`;
  const prixOf = (it) => (it.prix_unitaire != null ? Number(it.prix_unitaire) : ((getProduit(it.produit_id) || {}).prix_vente || 0));
  const lines = cart.map((it) => {
    const p = getProduit(it.produit_id); if (!p) return '';
    return `<div class="cline">
      <div class="cline__id"><strong>${esc(p.nom)}</strong><small>${formatF(prixOf(it))}</small></div>
      <div class="cline__qty">
        <button class="cline__pm" data-action="cart-dec" data-id="${it.produit_id}" aria-label="Retirer une unité"><span data-icon="minus"></span></button>
        <span class="cline__n">${formatNombre(it.qte)}</span>
        <button class="cline__pm" data-action="cart-inc" data-id="${it.produit_id}" aria-label="Ajouter une unité"><span data-icon="plus"></span></button>
      </div>
      <span class="cline__tot">${formatF((it.qte || 0) * prixOf(it))}</span>
      <button class="cline__x" data-action="cart-remove" data-id="${it.produit_id}" aria-label="Retirer du panier"><span data-icon="close"></span></button>
    </div>`;
  }).join('');
  const total = cart.reduce((s, it) => s + (it.qte || 0) * prixOf(it), 0);
  const modeChips = PAYMENT_MODES.map((m) => `<button class="modechip ${mode === m ? 'is-on' : ''}" data-action="cart-mode" data-mode="${m}">${PAYMENT_LABELS[m]}</button>`).join('');
  const vends = getVendeurs();
  const vendSel = vends.length ? `<div class="field caisse__vend"><label for="cs-vend">Vendeur</label>
      <select id="cs-vend" class="input" data-action="cart-vendeur"><option value="">— Personne —</option>${vends.map((v) => `<option value="${esc(v)}" ${vendeur === v ? 'selected' : ''}>${esc(v)}</option>`).join('')}</select></div>` : '';
  return `<div class="caisse">
    <div class="caisse__prods">${tiles}</div>
    ${dig ? '<button class="btn btn--ghost caisse__libre" data-action="vente-libre"><span data-icon="plus"></span> Montant libre / acompte de projet</button>' : ''}
    ${zhelp(dig ? 'Touche une prestation pour l’ajouter, ou « Montant libre » pour facturer un acompte de projet. Choisis le paiement, puis « Encaisser ».' : 'Touche un produit pour l’ajouter au panier. Ajuste les quantités, choisis le mode de paiement, puis « Encaisser ».')}
    <div class="caisse__cart">${cart.length ? lines : '<p class="cart-empty">Panier vide — touche un produit ci-dessus.</p>'}</div>
    <div class="caisse__pay">
      <span class="caisse__paylbl">Mode de paiement</span>
      <div class="modechips">${modeChips}</div>
      ${vendSel}
    </div>
    <button class="btn btn--sell btn--lg caisse__enc" data-action="cart-encaisser" ${cart.length ? '' : 'disabled'}>Encaisser ${formatF(total)}</button>
  </div>`;
}
export function receiptHTML(data, fmt) {
  const p = getState().profil;
  const d = new Date(data.date);
  const lignes = data.lignes.map((l) => `<tr><td class="rc-l">${esc(l.nom)}</td><td class="rc-q">${formatNombre(l.qte)}×${formatF(l.prix_unitaire)}</td><td class="rc-m">${formatF((l.qte || 0) * (l.prix_unitaire || 0))}</td></tr>`).join('');
  return `<div class="rcpt rcpt--${fmt === 'a4' ? 'a4' : 'thermal'}">
    <div class="rc-head"><strong>${esc(p.nom_activite || 'Mon activité')}</strong>${p.tel_pro ? `<span>Tél : ${esc(p.tel_pro)}</span>` : ''}${p.adresse ? `<span>${esc(p.adresse)}</span>` : ''}</div>
    <div class="rc-meta"><span>REÇU</span><span>${d.toLocaleDateString('fr-FR')} ${d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</span></div>
    <table class="rc-tbl"><tbody>${lignes}</tbody></table>
    <div class="rc-total"><span>TOTAL</span><span>${formatF(data.total)}</span></div>
    <div class="rc-pay">Payé en ${esc(PAYMENT_LABELS[data.mode] || data.mode)}${data.vendeur ? ` · Vendeur : ${esc(data.vendeur)}` : ''}</div>
    <div class="rc-foot">Merci de votre visite !</div>
  </div>`;
}

// ============ BLOC D'ALERTES (tableau de bord) ============
export function alertsBlockHTML() {
  const n = notifications();
  if (!n.count) return '';
  const st = stockResume();
  const dettes = n.list.filter((a) => a.type === 'dette').length;
  const facs = n.list.filter((a) => a.type === 'facture').length;
  const items = [];
  if (st.ruptures) items.push({ ic: 'box', cls: 'dng', text: `${st.ruptures} produit${st.ruptures > 1 ? 's' : ''} en rupture`, screen: 'stock' });
  if (st.bas) items.push({ ic: 'box', cls: 'warn', text: `${st.bas} produit${st.bas > 1 ? 's' : ''} bientôt épuisé${st.bas > 1 ? 's' : ''}`, screen: 'stock' });
  if (dettes) items.push({ ic: 'alert', cls: 'dng', text: `${dettes} dette${dettes > 1 ? 's' : ''} client en retard`, screen: 'carnet' });
  if (facs) items.push({ ic: 'receipt', cls: 'warn', text: `${facs} facture${facs > 1 ? 's' : ''} échue${facs > 1 ? 's' : ''}`, screen: 'bilan' });
  const rows = items.map((a) => `<button class="alertrow" data-action="go" data-screen="${a.screen}">
      <span class="alertrow__ic alertrow__ic--${a.cls}" data-icon="${a.ic}"></span>
      <span class="alertrow__t">${esc(a.text)}</span>
      <span class="alertrow__go">Voir <span data-icon="chevron"></span></span></button>`).join('');
  return `<article class="panel alertcard">
    <div class="alertcard__head"><span class="alertcard__ic" data-icon="bell"></span><h2>À traiter</h2><span class="alertcard__n">${n.count}</span></div>
    <div class="alertlist">${rows}</div>
  </article>`;
}

// ============ ÉCRAN STOCK ============
function _todayYmd() { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; }
const STOCK_LABEL = { rupture: 'Rupture', bas: 'Stock bas', ok: 'En stock', 'non-suivi': 'Non suivi' };
export function viewStockHTML(filter = {}) {
  const prods = getProduits();
  if (isDigital()) return catalogueHTML(prods, filter);
  const r = stockResume();
  if (!prods.length) {
    return `<section class="view">${sectionTitle('Stock', 'Inventaire & alertes')}
      ${emptyState('box', 'Aucun produit', "Ajoute tes produits pour suivre les quantités et être prévenu avant chaque rupture.", 'Ajouter un produit', 'add-produit')}</section>`;
  }
  const q = (filter.q || '').trim().toLowerCase();
  const flt = filter.statut || 'tous';
  let list = prods.filter((p) => !q || p.nom.toLowerCase().includes(q));
  if (flt === 'reassort') list = list.filter((p) => ['rupture', 'bas'].includes(getStockInfo(p).statut));
  else if (flt === 'nonsuivi') list = list.filter((p) => !getStockInfo(p).suivi);
  const rows = list.map(stockRowHTML).join('') || `<li class="strow strow--empty">Aucun produit dans ce filtre.</li>`;
  const chip = (id, lbl, n) => `<button class="vchip ${flt === id ? 'is-on' : ''}" data-action="stock-filter" data-f="${id}">${lbl}${n != null ? ` <b>${n}</b>` : ''}</button>`;
  return `<section class="view">
    ${sectionTitle('Stock', 'Inventaire & alertes')}
    ${zhelp('Suis les quantités de tes produits. Quand un stock passe sous son seuil, tu es prévenu ici et par la cloche. Les boutons − et + ajustent la quantité ; « Suivre » commence à compter un produit.')}
    <div class="stockstat">
      <div class="stockstat__c"><span class="stockstat__lbl">Valeur du stock</span><span class="stockstat__val">${formatF(r.valeur)}</span></div>
      <div class="stockstat__c ${r.ruptures ? 'is-dng' : ''}"><span class="stockstat__lbl">Ruptures</span><span class="stockstat__val">${formatNombre(r.ruptures)}</span></div>
      <div class="stockstat__c ${r.bas ? 'is-warn' : ''}"><span class="stockstat__lbl">Stock bas</span><span class="stockstat__val">${formatNombre(r.bas)}</span></div>
      <div class="stockstat__c"><span class="stockstat__lbl">Suivis</span><span class="stockstat__val">${formatNombre(r.suivis)}/${formatNombre(r.total)}</span></div>
    </div>
    <div class="vfilters">
      <div class="vchips">${chip('tous', 'Tous')}${chip('reassort', 'À réassort', r.ruptures + r.bas)}${chip('nonsuivi', 'Non suivi')}</div>
      <div class="vsearch"><span class="vsearch__ic" data-icon="search"></span><input class="input vsearch__in" placeholder="Rechercher un produit" value="${esc(filter.q || '')}" data-action="stock-search" aria-label="Rechercher un produit"></div>
    </div>
    <ul class="stocklist">${rows}</ul>
  </section>`;
}
// Catalogue (mode Services & digital) : prestations/produits, prix + type de tarif, pas de stock.
function catalogueHTML(prods, filter) {
  const q = (filter.q || '').trim().toLowerCase();
  const list = prods.filter((p) => !q || p.nom.toLowerCase().includes(q));
  const rows = list.length ? list.map((p) => {
    const tt = TARIF_TYPES.includes(p.tarif_type) ? p.tarif_type : 'fixe';
    return `<li class="catrow" data-action="edit-produit" data-id="${p.id}">
      <span class="catrow__ic" data-icon="spark"></span>
      <div class="catrow__id"><strong>${esc(p.nom)}</strong><small>${TARIF_LABELS[tt]}</small></div>
      <span class="catrow__price">${formatF(p.prix_vente)}${esc(TARIF_UNITS[tt] || '')}</span>
      <span class="catrow__chev" data-icon="chevron"></span>
    </li>`;
  }).join('') : `<li class="strow strow--empty">Aucune prestation. Ajoute la première ci-dessous.</li>`;
  return `<section class="view">
    ${sectionTitle('Catalogue', 'Prestations & produits digitaux')}
    ${zhelp('Ton catalogue de prestations et produits digitaux, avec leur prix (fixe, taux horaire ou par projet). Touche une ligne pour la modifier. Pas de stock à gérer.')}
    <div class="vfilters"><div class="vsearch"><span class="vsearch__ic" data-icon="search"></span><input class="input vsearch__in" placeholder="Rechercher une prestation" value="${esc(filter.q || '')}" data-action="stock-search" aria-label="Rechercher"></div></div>
    <button class="btn" data-action="add-produit"><span data-icon="plus"></span> Ajouter une prestation / produit</button>
    <ul class="catlist">${rows}</ul>
  </section>`;
}
function stockRowHTML(p) {
  const s = getStockInfo(p);
  const ctrl = s.suivi
    ? `<div class="strow__step">
        <button class="strow__pm" data-action="stock-minus" data-id="${p.id}" aria-label="Retirer une unité"><span data-icon="minus"></span></button>
        <button class="strow__qte" data-action="stock-edit" data-id="${p.id}" title="Modifier la quantité et le seuil">${formatNombre(s.qte)}</button>
        <button class="strow__pm" data-action="stock-plus" data-id="${p.id}" aria-label="Ajouter une unité"><span data-icon="plus"></span></button>
      </div>`
    : `<button class="btn btn--ghost btn--sm" data-action="stock-track" data-id="${p.id}">Suivre</button>`;
  return `<li class="strow strow--${s.statut}">
    <span class="strow__dot" aria-hidden="true"></span>
    <div class="strow__id"><strong>${esc(p.nom)}</strong><small>${formatF(p.prix_vente)} · <span class="strow__st">${STOCK_LABEL[s.statut]}</span>${s.suivi && s.seuil ? ` · seuil ${formatNombre(s.seuil)}` : ''}</small></div>
    ${ctrl}
  </li>`;
}

// ============ ÉCRAN CARNET (clients & créances) ============
export function viewCarnetHTML() {
  const rec = recouvrement();
  const clients = getClients();
  const credits = getCredits().slice().sort((a, b) => Number(creditPaye(a)) - Number(creditPaye(b)) || new Date(b.date) - new Date(a.date));
  const impayes = credits.filter((c) => creditReste(c) > 0);
  if (!clients.length && !credits.length) {
    return `<section class="view">${sectionTitle('Carnet', 'Clients & créances')}
      ${emptyState('users', 'Ton carnet est vide', "Note les clients qui te doivent de l'argent : tu vois qui doit quoi, et tu relances en un tap.", 'Ajouter un crédit', 'add-credit')}</section>`;
  }
  const pct = Math.round(rec.taux * 100);
  const gauge = `<article class="panel reccard">
    <div class="reccard__head"><span class="reccard__lbl">Recouvrement des dettes</span><span class="reccard__pct">${pct}<i>%</i></span></div>
    <div class="recbar"><span class="recbar__fill" style="width:${pct}%"></span></div>
    <div class="recmeta"><span class="recmeta__ok"><b>${formatF(rec.recouvre)}</b> recouvré</span><span class="recmeta__reste"><b>${formatF(rec.reste)}</b> à recouvrer${rec.nbDebiteurs ? ` · ${rec.nbDebiteurs} débiteur${rec.nbDebiteurs > 1 ? 's' : ''}` : ''}</span></div>
  </article>`;
  const dettesRows = impayes.length ? impayes.map(carnetCreditRow).join('') : `<li class="crdrow crdrow--empty">Aucune dette en cours. Bravo !</li>`;
  const clientRows = clients.length ? clients.map(clientRowHTML).join('') : `<li class="clirow clirow--empty">Aucun client enregistré.</li>`;
  return `<section class="view">
    ${sectionTitle('Carnet', 'Clients & créances')}
    ${zhelp('Qui te doit de l’argent (dettes) et ton annuaire clients. Tu peux encaisser des versements partiels, voir le reste dû, relancer par WhatsApp, et ouvrir la fiche d’un client pour son historique d’achat.')}
    ${gauge}
    ${relancesCardHTML()}
    <article class="panel">
      <div class="panel__head"><h2>Dettes en cours</h2><button class="btn btn--sm" data-action="add-credit"><span data-icon="plus"></span> Crédit</button></div>
      <ul class="crdlist">${dettesRows}</ul>
    </article>
    <article class="panel">
      <div class="panel__head"><h2>Clients</h2><button class="btn btn--sm" data-action="add-client"><span data-icon="plus"></span> Client</button></div>
      <ul class="clilist">${clientRows}</ul>
    </article>
  </section>`;
}
function carnetCreditRow(c) {
  const reste = creditReste(c);
  const late = reste > 0 && c.echeance && c.echeance < _todayYmd();
  const partiel = (c.paiements || []).length > 0 && reste > 0;
  return `<li class="crdrow ${reste <= 0 ? 'is-paid' : ''} ${late ? 'is-late' : ''}">
    <button class="crdrow__tap" data-action="credit-detail" data-id="${c.id}">
      <strong>${esc(c.client || 'Client')}</strong>
      <small>${formatF(reste)}${partiel ? ` <span class="crd-part">sur ${formatF(c.montant)}</span>` : ''}${c.echeance ? ` · éch. ${esc(c.echeance)}${late ? ' — dépassée' : ''}` : ''}</small>
    </button>
    <div class="crdrow__acts">
      ${reste > 0 ? `<button class="crd-btn crd-btn--pay" data-action="credit-versement" data-id="${c.id}" title="Encaisser un versement" aria-label="Encaisser un versement"><span data-icon="coins"></span></button>` : ''}
      ${reste > 0 && c.tel ? `<button class="crd-btn crd-btn--wa" data-action="credit-remind" data-id="${c.id}" title="Rappel WhatsApp" aria-label="Rappel WhatsApp"><span data-icon="whatsapp"></span></button>` : ''}
      <button class="crd-btn crd-btn--del" data-action="del-credit" data-id="${c.id}" title="Supprimer" aria-label="Supprimer"><span data-icon="trash"></span></button>
    </div></li>`;
}
function clientRowHTML(c) {
  const tel = (c.tel || '').replace(/[^0-9]/g, '');
  const meta = [c.nbDocs ? `${c.nbDocs} achat${c.nbDocs > 1 ? 's' : ''}` : '', c.nbCredits ? `${c.nbCredits} crédit${c.nbCredits > 1 ? 's' : ''}` : ''].filter(Boolean).join(' · ') || (c.tel || 'client');
  return `<li class="clirow">
    <button class="clirow__main" data-action="client-open" data-key="${esc(c.key)}">
      <span class="clirow__av" data-icon="user"></span>
      <span class="clirow__id"><strong>${esc(c.nom)}</strong><small>${esc(meta)}</small></span>
      ${c.dette > 0 ? `<span class="clirow__dette" title="Reste dû">${formatF(c.dette)}</span>` : ''}
    </button>
    ${tel ? `<a class="crd-btn crd-btn--wa" href="https://wa.me/${tel}" target="_blank" rel="noopener" title="WhatsApp" aria-label="Écrire sur WhatsApp"><span data-icon="whatsapp"></span></a>` : ''}
  </li>`;
}

// ============ ÉCRAN RÉGLAGES ============
// ============ COMPTE & SÉCURITÉ · ABONNEMENT & LICENCES ============
const initiales = (nom) => (nom || '?').trim().split(/\s+/).map((w) => w[0] || '').slice(0, 2).join('').toUpperCase() || '?';

// --- Cartes de plans (paywall + panneau abonnement). Copywriting de vente fort. ---
export function planCardsHTML(currentPlan) {
  const actif = licenceEtat().mode === 'actif';   // « Renouveler » seulement si une licence est active
  return `<div class="plans">${Object.keys(PLANS).map((k) => {
    const p = PLANS[k], isPro = k === 'pro', cur = actif && currentPlan === k;
    return `<article class="plan ${isPro ? 'plan--pro' : ''} ${cur ? 'is-current' : ''}">
      ${p.badge ? `<span class="plan__badge ${isPro ? 'plan__badge--pro' : ''}">${p.badge}</span>` : ''}
      <div class="plan__top">
        <h3 class="plan__nom">${esc(p.nom)}</h3>
        <p class="plan__cible">${esc(p.tag)} · ${esc(p.cible)}</p>
        <p class="plan__price"><strong>${formatNombre(p.prix)}</strong> <span>F / mois</span></p>
      </div>
      <ul class="plan__feats">${p.inclus.map((f) => `<li><span data-icon="check"></span> ${esc(f)}</li>`).join('')}</ul>
      <div class="plan__pitch">
        <p class="plan__peur"><span data-icon="alert"></span> ${esc(p.peur)}</p>
        <p class="plan__ridicule">${esc(p.ridicule)}</p>
      </div>
      <button class="btn btn--lg plan__cta ${isPro ? 'plan__cta--pro' : ''}" data-action="buy-plan" data-plan="${k}">
        ${cur ? 'Renouveler' : 'Choisir'} — ${formatNombre(p.prix)} F/mois</button>
    </article>`;
  }).join('')}</div>`;
}

// --- PAYWALL plein écran (essai terminé / licence expirée) : blocage total ---
export function paywallHTML(reason) {
  const titre = reason === 'expire' ? 'Ta licence a expiré' : 'Ton essai gratuit est terminé';
  return `<div class="paywall">
    <div class="paywall__inner">
      <div class="paywall__hero">
        <img class="paywall__logo" src="assets/icons/logo-app.png" alt="" width="56" height="56">
        <h1>${titre}</h1>
        <p class="paywall__lead">Pendant 30 jours, Boussole a tenu ta caisse, ton stock et tes dettes à ta place. Ne repars pas à l’aveugle : chaque jour sans Boussole, ce sont des ventes à perte, des dettes oubliées et du stock qui dort — de l’argent qui sort sans que tu le voies.</p>
        <p class="paywall__roi"><span data-icon="spark"></span> Récupère une seule dette oubliée, corrige un seul produit vendu à perte, et ton abonnement est déjà remboursé. Le reste, c’est du bénéfice en plus.</p>
      </div>
      ${planCardsHTML(getLicence().plan)}
      <div class="paywall__foot">
        <button class="btn btn--ghost" data-action="have-key"><span data-icon="key"></span> J’ai déjà reçu ma clé</button>
        <button class="btn btn--ghost" data-action="contact-nebula"><span data-icon="whatsapp"></span> Parler à NEBULA</button>
      </div>
      <p class="paywall__note">Sans engagement : tu paies au mois, tu arrêtes quand tu veux. Paiement Mobile Money, simple et local.</p>
    </div>
  </div>`;
}

// --- Bandeau de fin d'essai (booster de conversion, J-7 → J-1) ---
export function trialBannerHTML() {
  const e = licenceEtat();
  if (e.mode !== 'essai' || e.joursRestants > 7) return '';
  const j = e.joursRestants;
  const txt = j <= 0 ? 'Dernier jour d’essai !' : (j === 1 ? 'Il te reste 1 jour d’essai' : `Il te reste ${j} jours d’essai`);
  return `<button class="trialbar" data-action="go-offres">
    <span class="trialbar__l"><span data-icon="spark"></span> ${txt}</span>
    <span class="trialbar__cta">Voir les offres</span>
  </button>`;
}

// --- Panneau MON PROFIL ---
function monProfilPanelHTML(cloud) {
  const st = getState(); const nom = st.profil.proprietaire || '';
  return `<div class="panel">
    <div class="panel__head"><h2>Mon profil</h2></div>
    ${zhelp('Ton nom (le patron) et ton compte. Ton nom peut apparaître sur les reçus et le tableau de bord. Le compte sert à synchroniser et sécuriser tes données.')}
    <div class="profilcard">
      <span class="profilcard__av">${esc(initiales(nom || st.profil.nom_activite))}</span>
      <div class="profilcard__b">
        <strong>${esc(nom || 'Ton nom')}</strong>
        <small>${cloud.user ? esc(cloud.user.email) : 'Mode local (pas de compte)'}</small>
      </div>
    </div>
    <div class="field"><label for="rg-prop">Ton nom (propriétaire)</label>
      <input id="rg-prop" class="input" value="${esc(nom)}" data-action="save-prop" placeholder="Ex. Ada K."></div>
    ${cloud.user
      ? `<div class="btnrow">
           <button class="btn btn--ghost" data-action="change-pwd"><span data-icon="lock"></span> Changer le mot de passe</button>
           <button class="btn btn--danger-ghost" data-action="logout"><span data-icon="logout"></span> Déconnexion</button>
         </div>`
      : (cloud.configured
        ? `<button class="btn" data-action="open-auth"><span data-icon="user"></span> Créer un compte / se connecter</button>`
        : `<p class="panel__note">Mode local : tes données restent sur cet appareil. Pense à faire une sauvegarde.</p>`)}
  </div>`;
}

// --- Panneau CODE PIN ---
function pinPanelHTML() {
  const has = Sec.hasPin();
  return `<div class="panel">
    <div class="panel__head"><h2>Code PIN</h2><span class="panel__sub">verrouille l’appli</span></div>
    ${zhelp('Un code à 4 chiffres pour protéger l’ouverture de l’appli sur ce téléphone. Utile si on te l’emprunte. Sers-t’en aussi pour reprendre la main après un vendeur.')}
    <div class="secrow">
      <div class="secrow__b"><span class="secrow__ic" data-icon="shield"></span><div><strong>${has ? 'Code PIN activé' : 'Aucun code PIN'}</strong><small>${has ? 'L’appli demande le code à l’ouverture' : 'L’appli s’ouvre sans code'}</small></div></div>
    </div>
    <div class="btnrow">
      ${has
        ? `<button class="btn btn--ghost" data-action="pin-change"><span data-icon="edit"></span> Changer le code</button>
           <button class="btn btn--danger-ghost" data-action="pin-off">Désactiver</button>`
        : `<button class="btn" data-action="pin-set"><span data-icon="lock"></span> Créer un code PIN</button>`}
    </div>
    ${has ? `<button class="btn btn--ghost btn--sm" data-action="lock-now"><span data-icon="lock"></span> Verrouiller maintenant</button>` : ''}
  </div>`;
}

// --- Panneau GESTION DE L'ÉQUIPE (rôles + droits + PIN par vendeur) ---
function equipePanelHTML() {
  const eq = getEquipe();
  const rows = eq.length ? eq.map((m) => `<li class="mrow ${m.actif ? '' : 'is-off'}">
      <span class="mrow__av">${esc(initiales(m.nom))}</span>
      <div class="mrow__b"><strong>${esc(m.nom)}</strong><small>${roleLabel(m.role)}${m.pin ? ' · code défini' : ''}</small></div>
      <span class="mrow__role role--${m.role}">${roleLabel(m.role)}</span>
      <button class="lrow__btn" data-action="membre-edit" data-id="${m.id}" title="Modifier"><span data-icon="edit"></span></button>
    </li>`).join('') : '<li class="lrow lrow--empty">Aucun membre. Toi seul(e) pour l’instant.</li>';
  return `<div class="panel">
    <div class="panel__head"><h2>Gestion de l’équipe</h2><span class="panel__badge"><span data-icon="crown"></span> Pro</span></div>
    ${zhelp('Ajoute tes vendeurs et donne à chacun un rôle. Un Vendeur ne voit QUE la caisse (il ne voit ni tes bénéfices ni tes réglages) : c’est ta protection anti-vol. Chaque membre peut avoir son propre code.')}
    <ul class="list mlist">${rows}</ul>
    <div class="btnrow">
      <button class="btn btn--sm" data-action="membre-add"><span data-icon="plus"></span> Ajouter un membre</button>
      ${eq.length ? `<button class="btn btn--ghost btn--sm" data-action="hand-over"><span data-icon="users"></span> Passer la main à un vendeur</button>` : ''}
    </div>
    <div class="roleleg">${ROLES.map((r) => `<div class="roleleg__i"><span class="role--${r}">${ROLE_LABELS[r]}</span><small>${ROLE_DESCS[r]}</small></div>`).join('')}</div>
  </div>`;
}

// --- Panneau ABONNEMENT & LICENCES ---
function abonnementPanelHTML() {
  const e = licenceEtat(), lic = getLicence(), p = PLANS[lic.plan] || PLANS.essentiel;
  let statut;
  if (e.mode === 'actif') statut = `<span class="lic-tag lic-tag--ok">Actif · ${p.nom}</span><small>Jusqu’au ${fmtDateFr(lic.echeance)} (${e.joursRestants} j)</small>`;
  else if (e.mode === 'essai') statut = `<span class="lic-tag lic-tag--essai">Essai gratuit</span><small>${e.joursRestants} jour${e.joursRestants > 1 ? 's' : ''} restant${e.joursRestants > 1 ? 's' : ''} — accès complet</small>`;
  else statut = `<span class="lic-tag lic-tag--off">${e.mode === 'expire' ? 'Licence expirée' : 'Essai terminé'}</span><small>Active une licence pour continuer</small>`;
  return `<div class="panel">
    <div class="panel__head"><h2>Abonnement &amp; licences</h2></div>
    ${zhelp('Ton abonnement Boussole. Pendant l’essai, tout est ouvert. Ensuite, une licence mensuelle (envoyée par NEBULA après paiement Mobile Money) débloque l’appli. Une clé ne sert qu’une seule fois.')}
    <div class="liccard"><div class="liccard__b">${statut}</div></div>
    <div class="btnrow">
      <button class="btn" data-action="go-offres"><span data-icon="crown"></span> Voir les offres</button>
      <button class="btn btn--ghost" data-action="have-key"><span data-icon="key"></span> Activer une clé</button>
    </div>
    <button class="btn btn--ghost btn--sm" data-action="parrainage"><span data-icon="spark"></span> Parrainer un commerçant (1 mois offert)</button>
  </div>`;
}

// --- Carte d'incitation Pro (quand une fonction Pro est verrouillée) ---
function proUpsellHTML(titre, phrase) {
  return `<div class="proup">
    <span class="proup__ic" data-icon="crown"></span>
    <div class="proup__b"><strong>${esc(titre)} — réservé au Pro</strong><small>${esc(phrase)}</small></div>
    <button class="btn btn--sm plan__cta--pro" data-action="go-offres">Passer en Pro</button>
  </div>`;
}

// --- Panneau HISTORIQUE D'AUDIT (Pro anti-fraude) ---
function auditPanelHTML() {
  const pro = proAccess();
  const rows = getAudit(60);
  const body = !pro
    ? proUpsellHTML('Historique d’audit', 'Sache QUI a supprimé ou modifié une vente, et QUAND. Ta traçabilité anti-fraude.')
    : (rows.length
      ? `<ul class="auditlist">${rows.map((a) => `<li class="auditrow">
          <span class="auditrow__ic" data-icon="${a.action === 'suppression' ? 'trash' : 'edit'}"></span>
          <div class="auditrow__b"><strong>${esc(a.auteur)}</strong> a ${esc(a.action === 'suppression' ? 'supprimé' : 'modifié')} une ${esc(a.cible)}<small>${esc(a.detail)}</small></div>
          <span class="auditrow__t">${fmtDateTimeCourt(a.date)}</span>
        </li>`).join('')}</ul>`
      : '<p class="lrow--empty">Aucune suppression ni modification enregistrée. Tout est propre.</p>');
  return `<div class="panel">
    <div class="panel__head"><h2>Historique d’audit</h2><span class="panel__badge"><span data-icon="crown"></span> Pro</span></div>
    ${zhelp('Chaque suppression ou modification d’une vente, dépense, dette ou achat est tracée : qui l’a faite et quand. C’est ta protection contre les fraudes internes.')}
    ${body}
  </div>`;
}
function fmtDateTimeCourt(iso) {
  try { const d = new Date(iso); return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' }) + ' ' + d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }); } catch { return ''; }
}

// --- Panneau MULTI-BOUTIQUES (Pro) ---
function boutiquesPanelHTML() {
  const pro = proAccess();
  if (!pro) return `<div class="panel"><div class="panel__head"><h2>Mes boutiques</h2><span class="panel__badge"><span data-icon="crown"></span> Pro</span></div>${proUpsellHTML('Multi-boutiques', 'Gère plusieurs points de vente et vois le total consolidé, depuis un seul téléphone.')}</div>`;
  const active = activeBoutiqueId();
  const list = getBoutiques();
  const cons = consolideBoutiques();
  const rows = list.map((b) => `<li class="boutrow ${b.id === active ? 'is-active' : ''}">
      <button class="boutrow__pick" data-action="switch-boutique" data-id="${b.id}">
        <span class="boutrow__ic" data-icon="${b.id === active ? 'check' : 'box'}"></span>
        <div class="boutrow__b"><strong>${esc(b.nom)}</strong><small>${b.id === 'principale' ? 'Synchronisée au cloud' : 'Sur cet appareil'}</small></div>
      </button>
      ${b.id !== 'principale' ? `<button class="lrow__btn lrow__btn--del" data-action="del-boutique" data-id="${b.id}" title="Supprimer"><span data-icon="trash"></span></button>` : ''}
    </li>`).join('');
  const consRows = cons.rows.map((r) => `<tr><td>${esc(r.nom)}${r.active ? ' •' : ''}</td><td class="num">${formatF(r.ca)}</td><td class="num ${r.marge >= 0 ? 'pos' : 'neg'}">${formatF(r.marge)}</td><td class="num">${formatF(r.dettes)}</td></tr>`).join('');
  return `<div class="panel">
    <div class="panel__head"><h2>Mes boutiques</h2><span class="panel__badge"><span data-icon="crown"></span> Pro</span></div>
    ${zhelp('Gère plusieurs boutiques depuis cette appli. Chaque boutique a ses propres ventes, stock et dettes. La « principale » est synchronisée au cloud ; les autres restent sur cet appareil.')}
    <ul class="list boutlist">${rows}</ul>
    <div class="vaddrow"><input id="rg-bout" class="input" placeholder="Nom d’une nouvelle boutique" autocomplete="off"><button class="btn btn--sm" data-action="add-boutique"><span data-icon="plus"></span> Ajouter</button></div>
    <div class="panel__head" style="margin-top:16px"><h3 style="font-size:14px">Total consolidé (ce mois)</h3></div>
    <div class="tablewrap"><table class="tbl"><thead><tr><th>Boutique</th><th class="num">CA</th><th class="num">Marge</th><th class="num">Dettes</th></tr></thead>
      <tbody>${consRows}</tbody>
      <tfoot><tr><td>Total</td><td class="num">${formatF(cons.tot.ca)}</td><td class="num ${cons.tot.marge >= 0 ? 'pos' : 'neg'}">${formatF(cons.tot.marge)}</td><td class="num">${formatF(cons.tot.dettes)}</td></tr></tfoot>
    </table></div>
  </div>`;
}

// --- Carte RELANCES DU JOUR (Pro : dettes dues -> WhatsApp adapté) ---
export function relancesCardHTML() {
  if (!proAccess()) return '';
  const dues = relancesDues();
  if (!dues.length) return '';
  const rows = dues.slice(0, 8).map((c) => {
    const retard = c.joursRetard != null && c.joursRetard > 0 ? `<span class="rel-late">Retard ${c.joursRetard} j</span>` : (c.joursRetard === 0 ? '<span class="rel-due">Aujourd’hui</span>' : '<span class="rel-soft">À relancer</span>');
    return `<li class="relrow">
      <div class="relrow__b"><strong>${esc(c.client || 'Client')}</strong><small>${formatF(c.reste)} dû ${retard}</small></div>
      <button class="btn btn--sm btn--wa" data-action="relance-wa" data-id="${c.id}"><span data-icon="whatsapp"></span> Relancer</button>
    </li>`;
  }).join('');
  return `<article class="panel relcard">
    <div class="panel__head"><h2>Relances du jour</h2><span class="panel__badge"><span data-icon="crown"></span> Pro</span></div>
    ${zhelp('Les dettes dont l’échéance est arrivée. Un clic ouvre le WhatsApp du client avec un message de relance déjà écrit et adapté (montant restant, retard).')}
    <ul class="rellist">${rows}</ul>
  </article>`;
}

// --- ÉCRAN VERROUILLAGE (clavier PIN) : identifie patron OU vendeur ---
export function pinLockHTML(mode) {
  const titles = { open: 'Entre ton code', set: 'Choisis un code', confirm: 'Confirme le code', change: 'Nouveau code', owner: 'Code du patron' };
  const keys = [1, 2, 3, 4, 5, 6, 7, 8, 9, 'x', 0, 'ok'];
  return `<div class="lock">
    <div class="lock__inner">
      <img class="lock__logo" src="assets/icons/logo-app.png" alt="" width="52" height="52">
      <p class="lock__title">${titles[mode] || titles.open}</p>
      <div class="lock__dots" id="lock-dots">${[0, 1, 2, 3].map(() => '<span></span>').join('')}</div>
      <p class="lock__msg" id="lock-msg"></p>
      <div class="lock__pad">${keys.map((k) => k === 'x'
        ? `<button class="lock__key lock__key--fn" data-lock="del" aria-label="Effacer"><span data-icon="close"></span></button>`
        : k === 'ok'
          ? `<button class="lock__key lock__key--ok" data-lock="ok" aria-label="Valider"><span data-icon="check"></span></button>`
          : `<button class="lock__key" data-lock="${k}">${k}</button>`).join('')}</div>
      ${mode === 'open' ? `<button class="lock__forgot" data-lock="forgot">Code oublié ?</button>` : ''}
    </div>
  </div>`;
}

// --- Bandeau MODE EMPLOYÉ (quand un vendeur a la main) ---
export function empBannerHTML(membre) {
  if (!membre) return '';
  return `<div class="empbar">
    <span class="empbar__l"><span data-icon="user"></span> Mode employé : <strong>${esc(membre.nom)}</strong> (${roleLabel(membre.role)})</span>
    <button class="empbar__btn" data-action="reprendre"><span data-icon="lock"></span> Reprendre la main</button>
  </div>`;
}

// --- BACK-OFFICE licences (réservé NEBULA) ---
export function adminLicencesHTML(requests, keys, tgChat) {
  const reqRows = requests.length ? requests.map((r) => `<div class="areq ${r.statut !== 'en_attente' ? 'is-done' : ''}">
      <div class="areq__b"><strong>${esc(r.nom || 'Client')}</strong><small>${esc((PLANS[r.plan] || {}).nom || r.plan)} · ${formatNombre(r.montant || 0)} F · TXN ${esc(r.txn || '—')}</small></div>
      <div class="areq__acts">
        ${r.statut === 'en_attente'
          ? `<button class="btn btn--sm" data-action="admin-genkey" data-plan="${esc(r.plan)}" data-id="${r.id}"><span data-icon="key"></span> Générer la clé</button>
             <button class="btn btn--ghost btn--sm" data-action="admin-reject" data-id="${r.id}">Rejeter</button>`
          : `<span class="lic-tag lic-tag--${r.statut === 'valide' ? 'ok' : 'off'}">${r.statut}</span>`}
      </div>
    </div>`).join('') : '<p class="lrow--empty">Aucune demande de paiement.</p>';
  const keyRows = keys.slice(0, 20).map((k) => `<div class="akey ${k.statut === 'used' ? 'is-used' : ''}">
      <code>${esc(k.cle)}</code><span>${esc((PLANS[k.plan] || {}).nom || k.plan)}</span>
      <span class="lic-tag lic-tag--${k.statut === 'used' ? 'off' : 'ok'}">${k.statut === 'used' ? 'utilisée' : 'dispo'}</span>
      ${k.statut === 'dispo' ? `<button class="lrow__btn" data-action="admin-copykey" data-cle="${esc(k.cle)}" title="Copier"><span data-icon="download"></span></button>` : ''}
    </div>`).join('');
  return `<section class="view">
    ${sectionTitle('Back-office licences', 'NEBULA — clés & paiements')}
    ${zhelp('Écran réservé à toi. Quand un client paie, tu vois sa demande ici : génère une clé (à usage unique), copie-la et envoie-la lui sur WhatsApp. Il l’active dans son appli.')}
    <div class="panel">
      <div class="panel__head"><h2>Demandes de paiement</h2><span class="panel__sub">à valider</span></div>
      <div class="areqlist">${reqRows}</div>
    </div>
    <div class="panel">
      <div class="panel__head"><h2>Générer une clé</h2></div>
      <div class="btnrow">${Object.keys(PLANS).map((k) => `<button class="btn" data-action="admin-genkey" data-plan="${k}"><span data-icon="key"></span> ${PLANS[k].nom}</button>`).join('')}</div>
      <div class="akeylist">${keyRows}</div>
    </div>
    <div class="panel">
      <div class="panel__head"><h2>Notifications Telegram</h2></div>
      ${zhelp('Reçois une alerte Telegram à chaque paiement (sans n8n). Sur Telegram, écris à @userinfobot : il te donne ton « Id ». Colle-le ici puis teste.')}
      <div class="field"><label for="tg-chat">Ton Telegram (chat id)</label>
        <input id="tg-chat" class="input" inputmode="numeric" value="${esc(tgChat || '')}" placeholder="Ex. 123456789" autocomplete="off"></div>
      <div class="btnrow">
        <button class="btn" data-action="tg-save"><span data-icon="check"></span> Enregistrer</button>
        <button class="btn btn--ghost" data-action="tg-test"><span data-icon="spark"></span> Envoyer un test</button>
      </div>
    </div>
    <button class="btn btn--ghost" data-action="go" data-screen="reglages"><span data-icon="home"></span> Retour à l’appli</button>
  </section>`;
}

// ---- Panneau PERSONNALISATION (apparence à son goût) ----
function personnalisationPanelHTML() {
  const accent = uiPref('accent', 'ambre'), textsize = uiPref('textsize', 'normal');
  const density = uiPref('density', 'confort'), corners = uiPref('corners', 'doux');
  const theme = (typeof document !== 'undefined' && document.documentElement.dataset.theme) || 'dark';
  return `<div class="panel">
    <div class="panel__head"><h2>Personnalisation</h2><span class="panel__sub">à ton goût</span></div>
    ${zhelp('Choisis l’allure de l’appli : couleur, taille du texte, espacement et forme des coins. Ces réglages restent sur cet appareil.')}
    <div class="field"><label>Couleur d’accent</label>
      <div class="swatches">${ACCENTS.map((a) => `<button class="swatch ${accent === a.k ? 'is-on' : ''}" data-action="set-accent" data-v="${a.k}" style="--sw:${a.c}" title="${a.nom}" aria-label="Couleur ${a.nom}"><span></span></button>`).join('')}</div>
    </div>
    <div class="field"><label>Taille du texte</label>${segControl('set-textsize', textsize, [['normal', 'Normale'], ['grand', 'Grande'], ['xgrand', 'Très grande']])}</div>
    <div class="field"><label>Densité</label>${segControl('set-density', density, [['confort', 'Confortable'], ['compact', 'Compact']])}</div>
    <div class="field"><label>Coins</label>${segControl('set-corners', corners, [['doux', 'Doux'], ['net', 'Nets']])}</div>
    <div class="field"><label>Thème</label>${segControl('set-theme', theme, [['light', 'Clair'], ['dark', 'Sombre']])}</div>
  </div>`;
}

// ---- Panneau MESSAGES WHATSAPP (textes configurables) ----
function messagesWaPanelHTML() {
  return `<div class="panel">
    <div class="panel__head"><h2>Messages WhatsApp</h2><span class="panel__sub">textes prêts à envoyer</span></div>
    ${zhelp('Personnalise les messages envoyés à tes clients par WhatsApp. Les mots entre accolades comme {client} ou {total} sont remplacés automatiquement par les vraies valeurs.')}
    ${Object.keys(WA_TEMPLATES_META).map((key) => {
      const m = WA_TEMPLATES_META[key];
      return `<div class="watpl">
        <div class="watpl__head"><strong>${esc(m.label)}</strong><button class="btn btn--ghost btn--xs" data-action="watpl-reset" data-key="${key}">Réinitialiser</button></div>
        <textarea class="input watpl__ta" id="watpl-${key}" data-action="watpl-save" data-key="${key}" rows="3" spellcheck="false">${esc(getWaTemplate(key))}</textarea>
        <div class="watpl__vars">${m.vars.map((v) => `<button class="varchip" data-action="watpl-var" data-key="${key}" data-var="${v}">{${v}}</button>`).join('')}</div>
      </div>`;
    }).join('')}
  </div>`;
}

// ---- Panneau IMPRIMANTE BLUETOOTH (thermique 58 mm) ----
function imprimantePanelHTML() {
  const ok = BT.supported(), name = BT.savedName();
  return `<div class="panel">
    <div class="panel__head"><h2>Imprimante Bluetooth</h2><span class="panel__sub">reçus 58 mm</span></div>
    ${zhelp('Connecte une petite imprimante thermique Bluetooth pour imprimer tes reçus directement. Fonctionne sur Android (Chrome). Sur iPhone, Apple ne l’autorise pas : dans ce cas, utilise l’impression via le navigateur.')}
    ${ok ? `
    <div class="btstat"><span class="btstat__dot ${name ? 'is-on' : ''}"></span>
      <div class="btstat__b"><strong>${name ? esc(name) : 'Aucune imprimante'}</strong><small>${name ? 'Appareil mémorisé sur ce téléphone' : 'Pas encore connectée'}</small></div>
    </div>
    <div class="btnrow">
      <button class="btn" data-action="bt-connect"><span data-icon="bluetooth"></span> ${name ? 'Reconnecter' : 'Connecter une imprimante'}</button>
      <button class="btn btn--ghost" data-action="bt-test"><span data-icon="print"></span> Imprimer un test</button>
      ${name ? `<button class="btn btn--danger-ghost btn--sm" data-action="bt-forget">Oublier</button>` : ''}
    </div>` : `
    <div class="btstat btstat--off"><span class="btstat__ic" data-icon="info"></span>
      <div class="btstat__b"><strong>Bluetooth direct indisponible ici</strong><small>C’est souvent le cas sur iPhone. Tu peux quand même imprimer tes reçus (ticket ou A4) avec le bouton d’impression du navigateur.</small></div>
    </div>`}
  </div>`;
}

// ---- Panneau LANGUE (interface multilingue) ----
function languePanelHTML() {
  const cur = I18n.getLang();
  const rows = I18n.allLangs().map((l) => `<button class="langrow ${cur === l.code ? 'is-on' : ''}" data-action="set-lang" data-code="${l.code}">
      <span class="langrow__n">${esc(l.natif)}${l.custom ? ' <span class="langrow__beta">à valider</span>' : ''}</span>
      <span class="langrow__r">${l.custom ? `<span class="langrow__edit" data-action="lang-edit" data-code="${l.code}" title="Corriger les mots" aria-label="Corriger les mots"><span data-icon="edit"></span></span>` : ''}${cur === l.code ? '<span data-icon="check"></span>' : ''}</span>
    </button>`).join('');
  return `<div class="panel">
    <div class="panel__head"><h2>Langue</h2><span class="panel__sub">interface de l’appli</span></div>
    ${zhelp('Choisis la langue de l’interface. Français et Anglais sont complets. Pour une langue locale (fon, yoruba…), ajoute-la et saisis toi-même les bons mots — c’est toi qui connais ta langue.')}
    <div class="langlist">${rows}</div>
    <button class="btn btn--ghost btn--sm" data-action="lang-add"><span data-icon="plus"></span> Ajouter une langue locale</button>
  </div>`;
}

export function viewReglagesHTML(cloud) {
  const st = getState();
  const produits = getProduits({ withArchived: false });
  const charges = getChargesFixes();

  const prodItems = produits.length ? produits.map((p) => `<li class="lrow">
      <span class="lrow__ic" data-icon="${p.modele === 'transformation' ? 'factory' : 'truck'}"></span>
      <div class="lrow__body"><strong>${esc(p.nom)}</strong><small>${formatF(p.prix_vente)} · coût ${formatF(coutRevient(p))}</small></div>
      <button class="lrow__btn" data-action="edit-produit" data-id="${p.id}" title="Modifier"><span data-icon="edit"></span></button>
      <button class="lrow__btn lrow__btn--del" data-action="del-produit" data-id="${p.id}" title="Supprimer"><span data-icon="trash"></span></button>
    </li>`).join('') : `<li class="lrow lrow--empty">Aucun produit.</li>`;

  const chargeItems = charges.length ? charges.map((c) => `<li class="lrow">
      <span class="lrow__ic" data-icon="bolt"></span>
      <div class="lrow__body"><strong>${esc(c.libelle)}</strong><small>${formatF(c.montant)} / mois</small></div>
      <button class="lrow__btn lrow__btn--del" data-action="del-charge" data-id="${c.id}" title="Supprimer"><span data-icon="trash"></span></button>
    </li>`).join('') : `<li class="lrow lrow--empty">Aucune charge fixe.</li>`;

  return `<section class="view">
    ${sectionTitle('Réglages', 'Activité, coûts, sauvegarde')}
    <div class="panel">
      <div class="panel__head"><h2>Activité</h2></div>
      ${zhelp('Ton type d’activité adapte toute l’appli (stock ou catalogue de prestations). Ton nom et ta monnaie apparaissent en haut, sur tes factures et reçus.')}
      <div class="field"><label>Type d'activité</label>
        <div class="seg seg--2">
          <button class="seg__b seg__b--c ${getBusinessType() === 'physique' ? 'is-on' : ''}" data-action="set-biz" data-v="physique"><span data-icon="box"></span> Produits physiques<small>boutique, commerce</small></button>
          <button class="seg__b seg__b--c ${getBusinessType() === 'digital' ? 'is-on' : ''}" data-action="set-biz" data-v="digital"><span data-icon="spark"></span> Services &amp; digital<small>dev, design, agence</small></button>
        </div></div>
      <div class="field"><label for="rg-nom">Nom de l'activité</label>
        <input id="rg-nom" class="input" value="${esc(st.profil.nom_activite)}" data-action="save-nom" placeholder="Ex. Yaourt Maman Adjo"></div>
      <div class="field"><label for="rg-devise">Devise</label>
        <select id="rg-devise" class="input" data-action="save-devise">
          ${Object.keys(CURRENCIES).map((code) => `<option value="${code}" ${getDevise() === code ? 'selected' : ''}>${esc(CURRENCIES[code].label)}</option>`).join('')}
        </select></div>
    </div>
    ${personnalisationPanelHTML()}
    ${languePanelHTML()}
    <div class="panel">
      <div class="panel__head"><h2>Identité pour tes factures</h2><span class="panel__sub">imprimée sur chaque facture &amp; devis</span></div>
      <div class="field"><label for="rg-adresse">Adresse</label>
        <input id="rg-adresse" class="input" value="${esc(st.profil.adresse || '')}" data-action="save-fisc" data-field="adresse" placeholder="Ex. Cotonou, Haie-Vive"></div>
      <div class="grid2">
        <div class="field"><label for="rg-telpro">Téléphone</label>
          <input id="rg-telpro" class="input" type="tel" inputmode="tel" value="${esc(st.profil.tel_pro || '')}" data-action="save-fisc" data-field="tel_pro" placeholder="Ex. 97 00 00 00"></div>
        <div class="field"><label for="rg-mailpro">E-mail <span class="opt">(option)</span></label>
          <input id="rg-mailpro" class="input" type="email" value="${esc(st.profil.email_pro || '')}" data-action="save-fisc" data-field="email_pro" placeholder="toi@exemple.com"></div>
      </div>
      <div class="grid2">
        <div class="field"><label for="rg-ifu">IFU <span class="opt">(option)</span></label>
          <input id="rg-ifu" class="input" inputmode="numeric" value="${esc(st.profil.ifu || '')}" data-action="save-fisc" data-field="ifu" placeholder="N° IFU"></div>
        <div class="field"><label for="rg-rccm">RCCM <span class="opt">(option)</span></label>
          <input id="rg-rccm" class="input" value="${esc(st.profil.rccm || '')}" data-action="save-fisc" data-field="rccm" placeholder="N° RCCM"></div>
      </div>
      <div class="panel__note">Renseigne au moins ton adresse et ton téléphone. L'<strong>IFU</strong> apparaît sur la facture pour la rendre officielle.</div>
    </div>
    ${messagesWaPanelHTML()}
    ${imprimantePanelHTML()}
    <div class="panel">
      <div class="panel__head"><h2>Produits</h2><button class="btn btn--sm" data-action="add-produit"><span data-icon="plus"></span> Ajouter</button></div>
      <ul class="list">${prodItems}</ul>
    </div>
    <div class="panel">
      <div class="panel__head"><h2>Charges fixes mensuelles</h2><button class="btn btn--sm" data-action="add-charge"><span data-icon="plus"></span> Ajouter</button></div>
      ${zhelp('Les dépenses qui reviennent chaque mois, peu importe tes ventes (loyer, électricité, salaires…). L’appli les couvre d’abord, avant de compter ton bénéfice.')}
      <ul class="list">${chargeItems}</ul>
      <div class="panel__note">Total : <strong>${formatF(chargesMensuellesTotal())}</strong> / mois — c'est le « pot » à couvrir chaque mois avant de dégager du bénéfice.</div>
    </div>
    <h3 class="rgsec"><span data-icon="shield"></span> Compte & sécurité</h3>
    ${monProfilPanelHTML(cloud)}
    ${pinPanelHTML()}
    ${equipePanelHTML()}
    ${boutiquesPanelHTML()}
    ${auditPanelHTML()}
    ${abonnementPanelHTML()}
    <div class="panel">
      <div class="panel__head"><h2>Sauvegarde</h2></div>
      ${zhelp('Exporte une copie de toutes tes données dans un fichier (à garder au cas où), ou réimporte-la. « Effacer » remet tout à zéro — à utiliser avec prudence.')}
      <div class="btnrow">
        <button class="btn btn--ghost" data-action="export"><span data-icon="download"></span> Exporter</button>
        <button class="btn btn--ghost" data-action="import"><span data-icon="upload"></span> Importer</button>
      </div>
      <button class="btn btn--danger-ghost" data-action="wipe"><span data-icon="trash"></span> Effacer toutes les données</button>
    </div>
    <div class="panel">
      <div class="panel__head"><h2>Aide</h2></div>
      <button class="btn btn--ghost" data-action="open-tuto"><span data-icon="book"></span> Revoir le tutoriel</button>
    </div>
    <p class="ver">${esc(APP_NAME)} — outil NEBULA Agency</p>
  </section>`;
}

// ============ CONFIG / ONBOARDING (wizard) ============
export function viewConfigHTML(w) {
  const step = w.step || 1;
  const dots = [1, 2, 3].map((n) => `<span class="dot ${n === step ? 'is-active' : ''} ${n < step ? 'is-done' : ''}"></span>`).join('');
  let body = '';
  if (step === 1) {
    const bt = getBusinessType();
    body = `<div class="wz__head"><span class="wz__mark" data-icon="compass"></span>
      <h2>Bienvenue</h2><p>Configure ton activité une fois. Boussole s'adapte à TON métier.</p></div>
      <div class="field"><label>Quel est ton type d'activité&nbsp;?</label>
        <div class="bizpick">
          <button class="bizcard ${bt === 'physique' ? 'is-on' : ''}" data-action="wz-biz" data-v="physique">
            <span class="bizcard__ic" data-icon="box"></span><strong>Produits physiques</strong><small>Boutique, commerce, alimentation…</small></button>
          <button class="bizcard ${bt === 'digital' ? 'is-on' : ''}" data-action="wz-biz" data-v="digital">
            <span class="bizcard__ic" data-icon="spark"></span><strong>Services &amp; digital</strong><small>Développeur, designer, agence, infopreneur…</small></button>
        </div></div>
      <div class="field"><label for="wz-nom">Nom de ton activité</label>
        <input id="wz-nom" class="input input--lg" value="${esc(w.nom || '')}" placeholder="${bt === 'digital' ? 'Ex. Studio Koffi' : 'Ex. Yaourt Maman Adjo'}" autocomplete="off"></div>`;
  } else if (step === 2) {
    const dig = isDigital();
    body = `<div class="wz__head"><span class="wz__mark" data-icon="${dig ? 'spark' : 'box'}"></span>
      <h2>${dig ? 'Ta première prestation' : 'Ton premier produit'}</h2><p>${dig ? 'Une prestation ou un produit digital, avec son prix. Ajoute ses coûts si tu en as.' : 'Renseigne TOUS ses coûts. C\'est ce qui rend le calcul du bénéfice juste.'}</p></div>
      ${productFormFields(w.produit || { modele: dig ? 'revente' : 'transformation', couts: [], tarif_type: 'fixe' })}
      <div class="wz__hint">Tu pourras en ajouter d'autres plus tard, dans Réglages.</div>`;
  } else {
    const dig = isDigital();
    body = `<div class="wz__head"><span class="wz__mark" data-icon="bolt"></span>
      <h2>${dig ? 'Tes coûts fixes & outils' : 'Charges fixes mensuelles'}</h2><p>${dig ? 'Tes abonnements et charges qui reviennent chaque mois (Supabase, hébergement, loyer…).' : 'Les dépenses qui tombent chaque mois quel que soit le nombre de ventes (électricité, internet, loyer…).'}</p></div>
      <div id="wz-charges">${chargeRowsHTML(w.charges || defaultCharges())}</div>
      <button class="btn btn--ghost btn--sm" data-action="wz-add-charge"><span data-icon="plus"></span> Ajouter une charge</button>`;
  }
  const backBtn = step > 1 ? `<button class="btn btn--ghost" data-action="wz-back">Retour</button>` : `<span></span>`;
  const nextLbl = step < 3 ? 'Continuer' : 'Terminer';
  return `<section class="view view--wizard">
    <div class="wz">
      <div class="wz__dots">${dots}</div>
      <div class="wz__body">${body}</div>
      <div class="wz__nav">${backBtn}<button class="btn btn--lg" data-action="wz-next"><span>${nextLbl}</span> <span data-icon="chevron"></span></button></div>
    </div>
  </section>`;
}

export function defaultCharges() { return [{ libelle: 'Électricité', montant: '' }, { libelle: 'Internet', montant: '' }]; }

export function chargeRowsHTML(rows) {
  return rows.map((c, i) => `<div class="crow" data-i="${i}">
    <input class="input crow__lbl" data-cf="libelle" value="${esc(c.libelle)}" placeholder="Libellé (ex. Loyer)">
    <input class="input crow__amt" data-cf="montant" type="number" inputmode="numeric" value="${esc(c.montant)}" placeholder="0">
    <span class="crow__cur">F</span>
    <button class="crow__del" data-action="wz-del-charge" data-i="${i}"><span data-icon="close"></span></button>
  </div>`).join('');
}

// Champs d'un produit (utilisé dans wizard + modale) — modèle + coûts dynamiques.
export function productFormFields(p) {
  if (isDigital()) {
    const tt = TARIF_TYPES.includes(p.tarif_type) ? p.tarif_type : 'fixe';
    const couts = (p.couts && p.couts.length) ? p.couts : [{ libelle: '', montant: '' }];
    const prixLbl = tt === 'horaire' ? 'Taux horaire' : (tt === 'projet' ? 'Prix par projet' : 'Prix de la prestation');
    return `
      <div class="field"><label for="pf-nom">Nom de la prestation / produit</label>
        <input id="pf-nom" class="input" value="${esc(p.nom || '')}" placeholder="Ex. Développement mobile, Template Notion…" autocomplete="off"></div>
      <div class="field"><label>Type de tarif</label>
        <div class="seg seg--3">${TARIF_TYPES.map((t) => `<button type="button" class="seg__b seg__b--c ${tt === t ? 'is-on' : ''}" data-action="pf-tarif" data-tarif="${t}">${TARIF_LABELS[t]}</button>`).join('')}</div></div>
      <div class="field"><label for="pf-prix">${prixLbl}</label>
        <div class="inwrap"><input id="pf-prix" class="input" type="number" inputmode="numeric" value="${esc(p.prix_vente ?? '')}" placeholder="0"><span class="inwrap__cur">F${TARIF_UNITS[tt] || ''}</span></div></div>
      <div class="field"><label>Coûts éventuels <small class="lbl-help">sous-traitance, outils dédiés…</small></label>
        <div id="pf-couts">${coutRowsHTML(couts)}</div>
        <button type="button" class="btn btn--ghost btn--sm" data-action="pf-add-cout"><span data-icon="plus"></span> Ajouter un coût</button>
      </div>`;
  }
  const suggestions = p.modele === 'revente'
    ? ['Prix d\'achat', 'Transport', 'Stockage']
    : ['Matières premières', 'Emballage'];
  const couts = (p.couts && p.couts.length) ? p.couts : suggestions.map((s) => ({ libelle: s, montant: '' }));
  return `
    <div class="field"><label for="pf-nom">Nom du produit</label>
      <input id="pf-nom" class="input" value="${esc(p.nom || '')}" placeholder="Ex. Pot de yaourt 50cl" autocomplete="off"></div>
    <div class="field"><label>Modèle d'activité</label>
      <div class="seg">
        <button type="button" class="seg__b ${p.modele !== 'revente' ? 'is-on' : ''}" data-action="pf-modele" data-modele="transformation">
          <span data-icon="factory"></span> Transformation<small>je fabrique</small></button>
        <button type="button" class="seg__b ${p.modele === 'revente' ? 'is-on' : ''}" data-action="pf-modele" data-modele="revente">
          <span data-icon="truck"></span> Achat-revente<small>j'achète et je revends</small></button>
      </div></div>
    <div class="field"><label for="pf-prix">Prix de vente (par unité)</label>
      <div class="inwrap"><input id="pf-prix" class="input" type="number" inputmode="numeric" value="${esc(p.prix_vente ?? '')}" placeholder="0"><span class="inwrap__cur">F</span></div></div>
    <div class="field"><label>Coûts pour 1 unité <small class="lbl-help">${p.modele === 'revente' ? 'prix d\'achat + frais' : 'matières + emballage'}</small></label>
      <div id="pf-couts">${coutRowsHTML(couts)}</div>
      <button type="button" class="btn btn--ghost btn--sm" data-action="pf-add-cout"><span data-icon="plus"></span> Ajouter un coût</button>
    </div>`;
}
export function coutRowsHTML(rows) {
  return rows.map((c, i) => `<div class="crow" data-i="${i}">
    <input class="input crow__lbl" data-pf="libelle" value="${esc(c.libelle)}" placeholder="Libellé du coût">
    <input class="input crow__amt" data-pf="montant" type="number" inputmode="numeric" value="${esc(c.montant)}" placeholder="0">
    <span class="crow__cur">F</span>
    <button type="button" class="crow__del" data-action="pf-del-cout" data-i="${i}"><span data-icon="close"></span></button>
  </div>`).join('');
}

// ============ Fragments ============
function sectionTitle(t, sub) {
  return `<header class="vhead"><h1>${t}</h1>${sub ? `<span class="vhead__sub">${esc(sub)}</span>` : ''}</header>`;
}
function emptyState(ic, title, msg, cta, action) {
  return `<div class="empty"><span class="empty__ic" data-icon="${ic}"></span>
    <h2>${esc(title)}</h2><p>${esc(msg)}</p>
    ${cta ? `<button class="btn btn--lg" data-action="${action}">${esc(cta)}</button>` : ''}</div>`;
}

// ============ MODALES / SHEETS / TOASTS ============
export function openModal(html, { onClose } = {}) {
  const root = document.getElementById('modal-root');
  root.innerHTML = `<div class="scrim" data-action="close-modal"></div>
    <div class="modal" role="dialog" aria-modal="true">${html}</div>`;
  root.classList.add('is-open');
  root._onClose = onClose || null;
  const first = root.querySelector('input,button,select,textarea');
  if (first && !first.matches('[data-action="close-modal"]')) setTimeout(() => first.focus(), 40);
}
export function closeModal() {
  const root = document.getElementById('modal-root');
  root.classList.remove('is-open');
  root.innerHTML = '';
  if (root._onClose) { root._onClose(); root._onClose = null; }
}
export function modalShell(title, bodyHTML, footerHTML) {
  return `<div class="modal__bar"><h2>${esc(title)}</h2><button class="modal__x" data-action="close-modal"><span data-icon="close"></span></button></div>
    <div class="modal__body">${bodyHTML}</div>
    ${footerHTML ? `<div class="modal__foot">${footerHTML}</div>` : ''}`;
}

// ============ ASSISTANT (chat) ============
export function assistantMsgsHTML(chat) {
  return chat.map((m) => `<div class="asmsg asmsg--${m.role === 'user' ? 'user' : 'bot'}">${esc(m.text)}</div>`).join('');
}
export function assistantHTML(chat) {
  const sugg = ASSISTANT_SUGGESTIONS.map((s) => `<button class="aschip" data-action="assistant-ask" data-q="${esc(s)}">${esc(s)}</button>`).join('');
  return `<div class="modal__bar"><h2 class="as-title"><span class="as-ic" data-icon="spark"></span> Assistant</h2>
      <button class="modal__x" data-action="close-modal"><span data-icon="close"></span></button></div>
    <div class="as-msgs" id="as-msgs">${assistantMsgsHTML(chat)}</div>
    <div class="as-sugg">${sugg}</div>
    <div class="as-inputrow">
      <input id="as-input" class="input" type="text" placeholder="Pose ta question…" aria-label="Question à l'assistant" autocomplete="off">
      <button class="btn btn--icon as-send" data-action="assistant-send" aria-label="Envoyer"><span data-icon="send"></span></button>
    </div>`;
}

let toastTimer = null;
export function toast(msg, type = 'ok') {
  const root = document.getElementById('toast-root');
  const t = document.createElement('div');
  t.className = `toast toast--${type}`;
  t.innerHTML = `<span data-icon="${type === 'err' ? 'alert' : 'check'}"></span><span>${esc(msg)}</span>`;
  root.appendChild(t);
  requestAnimationFrame(() => t.classList.add('is-in'));
  setTimeout(() => { t.classList.remove('is-in'); setTimeout(() => t.remove(), 260); }, 2600);
}

// ============ DIDACTICIEL ============
export const TUTO_STEPS = [
  {
    ic: 'compass', titre: `Bienvenue dans ${APP_NAME}`,
    corps: `<p>${esc(APP_NAME)} t'aide à savoir si ton activité est <strong>rentable</strong>. Le principe est simple : comparer ce que tu <strong>dépenses</strong> à ce que tu <strong>gagnes</strong>, et te dire quoi améliorer.</p>`,
  },
  {
    ic: 'reglages', titre: '1 · Configure une seule fois',
    corps: `<p>Renseigne ton activité, tes <strong>produits</strong> et <strong>TOUS leurs coûts</strong> (matières, emballage, transport, prix d'achat…), puis tes <strong>charges fixes</strong> du mois (électricité, internet, loyer). C'est ce qui rend le calcul juste.</p>`,
  },
  {
    ic: 'coins', titre: '2 · Les 3 enveloppes',
    corps: `<p>À chaque vente, ${esc(APP_NAME)} range ton argent dans 3 poches :</p>
      <div class="tuto-env">
        <div class="tuto-env__row"><span class="tuto-env__d" style="background:var(--rel)"></span><b>Relance production</b> — de quoi refaire / racheter</div>
        <div class="tuto-env__row"><span class="tuto-env__d" style="background:var(--chg)"></span><b>Charges fixes</b> — pour payer électricité, internet…</div>
        <div class="tuto-env__row"><span class="tuto-env__d" style="background:var(--acc)"></span><b>Bénéfice net</b> — ce qui te reste vraiment</div>
      </div>
      <p class="tuto-ex">Ex. un yaourt vendu 250 F qui coûte 150 F : 150 F pour en refaire un, le reste couvre tes charges puis devient ton bénéfice.</p>`,
  },
  {
    ic: 'ventes', titre: '3 · Vends en un clic',
    corps: `<p>Chaque jour, appuie sur <strong>« +1 vente »</strong> sur le bon produit (ou saisis la quantité et le prix). Les 3 enveloppes se remplissent <strong>toutes seules</strong>.</p>`,
  },
  {
    ic: 'bilan', titre: '4 · Lis ton bilan et tes conseils',
    corps: `<p>L'écran <strong>Bilan</strong> te donne tes statistiques, la <strong>courbe d'évolution</strong> de tes bénéfices, un <strong>score de santé /100</strong> et des <strong>conseils concrets</strong> sur quoi améliorer. Tu peux l'exporter par WhatsApp ou l'imprimer.</p>`,
  },
  {
    ic: 'cloud', titre: '5 · Sauvegarde et appareils',
    corps: `<p>Sans compte, tes données restent sur cet appareil — pense à faire une <strong>sauvegarde</strong> (Réglages → Exporter). Avec un compte, elles se <strong>synchronisent</strong> entre ton téléphone et ton PC.</p>`,
  },
];

export function tutorielHTML(i) {
  const s = TUTO_STEPS[i];
  const total = TUTO_STEPS.length;
  const dots = TUTO_STEPS.map((_, n) => `<span class="dot ${n === i ? 'is-active' : ''} ${n < i ? 'is-done' : ''}"></span>`).join('');
  const prev = i > 0
    ? `<button class="btn btn--ghost" data-action="tuto-prev" data-i="${i}">Précédent</button>`
    : `<button class="btn btn--ghost" data-action="close-modal">Passer</button>`;
  const nextLbl = i < total - 1 ? 'Suivant' : 'C\'est parti';
  return `<div class="tuto">
    <button class="modal__x tuto__x" data-action="close-modal" aria-label="Fermer"><span data-icon="close"></span></button>
    <span class="tuto__ic" data-icon="${s.ic}"></span>
    <h2 class="tuto__t">${s.titre}</h2>
    <div class="tuto__c">${s.corps}</div>
    <div class="wz__dots tuto__dots">${dots}</div>
    <div class="tuto__nav">${prev}<button class="btn" data-action="tuto-next" data-i="${i}">${nextLbl} <span data-icon="chevron"></span></button></div>
  </div>`;
}

export function confirmDialog({ title, message, danger, okLabel = 'Confirmer' }, onOk) {
  openModal(modalShell(title, `<p class="confirm-msg">${esc(message)}</p>`,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn ${danger ? 'btn--danger' : ''}" data-action="confirm-ok">${esc(okLabel)}</button>`));
  document.getElementById('modal-root')._confirmOk = onOk;
}

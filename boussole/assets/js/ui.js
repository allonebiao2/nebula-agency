// Boussole — rendu des écrans, modales, toasts.
import { icon } from './icons.js';
import {
  getState, getProduits, getProduit, getChargesFixes, getVentes,
  coutRevient, margeUnitaire, chargesMensuellesTotal, seuilRentabilite,
  bilanMois, ventesDuMois, serieMensuelle, trimestreDe, currentMonthKey,
  statistiques, analyseBusiness,
  serieDashboard, topProduitsPeriode, getObjectif,
  formatF, formatNombre, MOIS_LONGS,
} from './store.js';
import { chartBeneficeMensuel, chartEvolution, miniSpark, progressRing, chartHero, chartDonut, sparklineRaw } from './charts.js';
import { APP_NAME } from './config.js';

export const esc = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const moisLabel = (mk) => {
  const [y, m] = mk.split('-');
  return `${MOIS_LONGS[Number(m) - 1]} ${y}`;
};

// ============ TOPBAR ============
export function topbarHTML(cloud, theme = 'light') {
  const nom = getState().profil.nom_activite || 'Mon activité';
  const cloudBtn = cloud.configured
    ? `<button class="chip ${cloud.user ? 'chip--on' : ''}" data-action="open-auth" title="${cloud.user ? 'Synchronisé' : 'Se connecter'}">
        <span class="chip__ic" data-icon="${cloud.user ? 'cloud' : 'cloudOff'}"></span>
        <span class="chip__t">${cloud.user ? esc(cloud.user.email.split('@')[0]) : 'Cloud'}</span></button>`
    : `<button class="chip" data-action="cloud-info" title="Mode local"><span class="chip__ic" data-icon="cloudOff"></span><span class="chip__t">Local</span></button>`;
  return `
    <div class="topbar__brand"><span class="brand__mark" data-icon="compass"></span>
      <div class="brand__txt"><span class="brand__name">${esc(APP_NAME)}</span><span class="brand__sub">${esc(nom)}</span></div>
    </div>
    <div class="topbar__actions">
      <button class="chip chip--icon" data-action="toggle-theme" title="Thème clair / sombre" aria-label="Changer de thème"><span class="chip__ic" data-icon="${theme === 'dark' ? 'sun' : 'moon'}"></span></button>
      <button class="chip chip--icon" data-action="open-tuto" title="Comment ça marche" aria-label="Aide"><span class="chip__ic" data-icon="help"></span></button>
      ${cloudBtn}
    </div>`;
}

// ============ NAV ============
export function navHTML(active) {
  const item = (id, label, ic) =>
    `<button class="nav__item ${active === id ? 'is-active' : ''}" data-action="go" data-screen="${id}">
      <span class="nav__ic" data-icon="${ic}"></span><span class="nav__lbl">${label}</span></button>`;
  return item('accueil', 'Accueil', 'home') + item('ventes', 'Ventes', 'ventes') + item('bilan', 'Bilan', 'bilan') + item('reglages', 'Réglages', 'reglages');
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
  return `<div class="kpi">
    <span class="kpi__lbl">${lbl}</span>
    <span class="kpi__val ${opts.valCls || ''}">${val}</span>
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
  const legRow = (lbl, val, color, pct) => `<div class="leg__row"><span class="leg__dot" style="background:${color}"></span>
    <span class="leg__lbl">${lbl}</span><span class="leg__val">${formatF(val)}</span><span class="leg__pct">${pct}</span></div>`;

  // ---- HÉROS : CA + Bénéfice ----
  const hero = `<article class="panel c8 dhero">
    <div class="dhero__head">
      <div class="dhero__id">
        <span class="dhero__lbl">Chiffre d'affaires + Bénéfice</span>
        <h2 class="dhero__val">${formatF(t.revenu)}</h2>
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
    ${objectif > 0 ? `
      <div class="objx__ring">${progressRing(pctObj, { color: 'var(--acc)', size: 140, stroke: 13 })}
        <div class="objx__center"><span class="objx__lvl" data-icon="flame"></span><strong>${pctObj}<small>%</small></strong></div></div>
      <div class="objx__meta"><b>${formatF(Math.max(0, benMois))}</b> / ${formatF(objectif)}</div>
      <p class="objx__hint">${benMois >= objectif ? 'Objectif atteint. Continue sur ta lancée.' : `Encore ${formatF(objectif - benMois)} pour l'atteindre ce mois-ci.`}</p>`
    : `<div class="objx__empty"><span class="objx__emptyic" data-icon="target"></span>
        <p>Fixe un objectif de bénéfice et suis ta progression chaque mois.</p>
        <button class="btn btn--sm" data-action="edit-objectif">Fixer un objectif</button></div>`}
  </article>`;

  // ---- KPIs colorés + comparaison ----
  const kpis = `<article class="panel c12 kpicard">
    <div class="kpis">
      ${kpiHTML("Chiffre d'affaires", formatF(t.revenu), D.deltas.revenu, D.buckets.map((x) => x.revenu), { sparkColor: 'var(--acc)' })}
      ${kpiHTML('Bénéfice net', formatF(t.benefice), D.deltas.benefice, D.buckets.map((x) => x.benefice), { valCls: t.benefice >= 0 ? 'pos' : 'neg', sparkColor: 'var(--pos)' })}
      ${kpiHTML('Taux de marge', pctMarge + ' %', D.deltas.tauxMarge, null, { delta: { pts: true } })}
      ${kpiHTML('Panier moyen', formatF(t.panierMoyen), D.deltas.panierMoyen, null, {})}
      ${kpiHTML('Ventes', formatNombre(t.unites), D.deltas.unites, D.buckets.map((x) => x.unites), { sparkColor: 'var(--rel)' })}
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
    { value: Math.max(0, env.benefice), color: 'var(--pos)' },
  ];
  const envDonut = `<article class="panel c4 donutcard">
    <div class="panel__head"><h2>Où va ton argent</h2><span class="panel__sub">${esc(D.label)}</span></div>
    <div class="donutwrap">
      <div class="donut">${chartDonut(envSegs, { size: 168, stroke: 20 })}
        <div class="donut__center"><strong>${formatF(env.revenu)}</strong><span>de ventes</span></div></div>
      <div class="leg">
        ${legRow('Relance', env.relance, 'var(--rel)', Math.round(env.relance / rTot * 100) + '%')}
        ${legRow('Charges', env.charges_couvertes, 'var(--chg)', Math.round(env.charges_couvertes / rTot * 100) + '%')}
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
        <div class="donut__center"><strong>${formatNombre(tops.reduce((s, p) => s + p.unites, 0))}</strong><span>unités</span></div></div>
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

  // ---- CONSEIL ----
  const topConseil = analyse.conseils.find((c) => c.priorite !== 'info');
  const prio = topConseil ? (PRIO[topConseil.priorite] || PRIO.basse) : null;
  const conseilCard = topConseil ? `<article class="panel c12">
    <div class="panel__head"><h2>À améliorer</h2><span class="csl__tag" style="color:${prio.col}">${prio.lbl}</span></div>
    <strong class="hc__t">${esc(topConseil.titre)}</strong><p class="hc__d">${esc(topConseil.detail)}</p>
    <button class="btn btn--ghost btn--sm hc__more" data-action="go" data-screen="bilan">Voir le bilan complet <span data-icon="chevron"></span></button>
  </article>` : '';

  return `<section class="view view--dash">
    <header class="dashhead">
      <div><p class="dashhead__greet">${greet},</p><h1 class="dashhead__nom">${esc(nom)}</h1></div>
      <span class="dashhead__time"><span data-icon="clock"></span>${timeStr}</span>
    </header>
    ${periodBarHTML(gran, offset, D.label)}
    <div class="dash">
      ${hero}
      ${objCard}
      ${kpis}
      ${sellCard}
      ${ringsCard}
      ${envDonut}
      ${prodDonut}
      ${rankCard}
      ${barsCard}
      ${conseilCard}
    </div>
  </section>`;
}

// ============ ÉCRAN VENTES ============
export function viewVentesHTML() {
  const produits = getProduits();
  const b = bilanMois();
  const mk = currentMonthKey();
  const ventesMois = ventesDuMois(mk).slice().reverse();
  const auj = new Date().toISOString().slice(0, 10);
  const ventesJour = ventesMois.filter((v) => v.date.slice(0, 10) === auj);

  if (produits.length === 0) {
    return `<section class="view">
      ${sectionTitle('Ventes', moisLabel(mk))}
      ${emptyState('box', 'Aucun produit configuré',
        'Commence par renseigner ton activité et les coûts de tes produits. Ensuite, vendre se fait en un clic.',
        'Configurer mon activité', 'go-config')}
    </section>`;
  }

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

  const journal = ventesJour.length ? ventesJour.map((v) => {
    const p = getProduit(v.produit_id);
    return `<li class="jrow">
      <span class="jrow__nom">${esc(p ? p.nom : '—')}</span>
      <span class="jrow__q">${v.qte} × ${formatF(v.prix_unitaire)}</span>
      <span class="jrow__tot">${formatF(v.qte * v.prix_unitaire)}</span>
      <button class="jrow__del" data-action="del-vente" data-id="${v.id}" title="Annuler"><span data-icon="close"></span></button>
    </li>`;
  }).join('') : `<li class="jrow jrow--empty">Aucune vente aujourd'hui pour l'instant.</li>`;

  const totalJour = ventesJour.reduce((s, v) => s + v.qte * v.prix_unitaire, 0);

  return `<section class="view" data-live>
    ${sectionTitle('Ventes', moisLabel(mk))}
    ${enveloppesHTML(b, { compact: true })}
    <div class="tiles">${tiles}</div>
    <div class="panel">
      <div class="panel__head"><h2>Aujourd'hui</h2><span class="panel__badge">${formatF(totalJour)}</span></div>
      <ul class="journal">${journal}</ul>
    </div>
  </section>`;
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
export function viewBilanHTML() {
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

  return `<section class="view">
    ${sectionTitle('Bilan', moisLabel(mk))}
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

// ============ ÉCRAN RÉGLAGES ============
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

  const cloudBlock = cloud.configured
    ? (cloud.user
      ? `<div class="cloudcard cloudcard--on"><div><strong>Synchronisé</strong><small>${esc(cloud.user.email)} · mobile et PC à jour</small></div>
          <button class="btn btn--ghost btn--sm" data-action="logout"><span data-icon="logout"></span> Déconnexion</button></div>`
      : `<div class="cloudcard"><div><strong>Cloud disponible</strong><small>Connecte-toi pour synchroniser mobile et PC</small></div>
          <button class="btn btn--sm" data-action="open-auth">Se connecter</button></div>`)
    : `<div class="cloudcard"><div><strong>Mode local</strong><small>Données sur cet appareil uniquement. Pense à faire une sauvegarde.</small></div></div>`;

  return `<section class="view">
    ${sectionTitle('Réglages', 'Activité, coûts, sauvegarde')}
    <div class="panel">
      <div class="panel__head"><h2>Activité</h2></div>
      <div class="field"><label for="rg-nom">Nom de l'activité</label>
        <input id="rg-nom" class="input" value="${esc(st.profil.nom_activite)}" data-action="save-nom" placeholder="Ex. Yaourt Maman Adjo"></div>
    </div>
    <div class="panel">
      <div class="panel__head"><h2>Produits</h2><button class="btn btn--sm" data-action="add-produit"><span data-icon="plus"></span> Ajouter</button></div>
      <ul class="list">${prodItems}</ul>
    </div>
    <div class="panel">
      <div class="panel__head"><h2>Charges fixes mensuelles</h2><button class="btn btn--sm" data-action="add-charge"><span data-icon="plus"></span> Ajouter</button></div>
      <ul class="list">${chargeItems}</ul>
      <div class="panel__note">Total : <strong>${formatF(chargesMensuellesTotal())}</strong> / mois — c'est le « pot » à couvrir chaque mois avant de dégager du bénéfice.</div>
    </div>
    <div class="panel">
      <div class="panel__head"><h2>Compte & synchronisation</h2></div>
      ${cloudBlock}
    </div>
    <div class="panel">
      <div class="panel__head"><h2>Sauvegarde</h2></div>
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
    body = `<div class="wz__head"><span class="wz__mark" data-icon="compass"></span>
      <h2>Bienvenue</h2><p>Configure ton activité une fois. Ensuite, vendre et voir tes bénéfices se fait en un clic.</p></div>
      <div class="field"><label for="wz-nom">Nom de ton activité</label>
        <input id="wz-nom" class="input input--lg" value="${esc(w.nom || '')}" placeholder="Ex. Yaourt Maman Adjo" autocomplete="off"></div>
      <div class="wz__hint">Tu vends quoi&nbsp;? Peu importe : nourriture, produits importés, biens immobiliers… Boussole s'adapte.</div>`;
  } else if (step === 2) {
    body = `<div class="wz__head"><span class="wz__mark" data-icon="box"></span>
      <h2>Ton premier produit</h2><p>Renseigne TOUS ses coûts. C'est ce qui rend le calcul du bénéfice juste.</p></div>
      ${productFormFields(w.produit || { modele: 'transformation', couts: [] })}
      <div class="wz__hint">Tu pourras ajouter d'autres produits plus tard, dans Réglages.</div>`;
  } else {
    body = `<div class="wz__head"><span class="wz__mark" data-icon="bolt"></span>
      <h2>Charges fixes mensuelles</h2><p>Les dépenses qui tombent chaque mois quel que soit le nombre de ventes (électricité, internet, loyer…).</p></div>
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

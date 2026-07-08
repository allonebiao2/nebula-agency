// Boussole — bootstrap, routeur, événements.
import { APP_VERSION, CLOUD_ENABLED } from './config.js';
import { hydrateIcons } from './icons.js';
import * as S from './store.js';
import * as Cloud from './supabase.js';
import * as UI from './ui.js';

let screen = 'ventes';
let wizard = null;
let authMode = 'signin';
let tutoStep = 0;
let period = loadPeriod();
let animateNext = false;   // déclenche cascades + compteurs à l'entrée (pas sur maj live)
let prevUser = null;
let pendingLogin = false;  // vrai après un login volontaire -> 2e splash
let venteFilter = Object.assign({ preset: 'jour', produitId: '', q: '' }, venteRange('jour'));

const $ = (s, r = document) => r.querySelector(s);
const cloudCtx = () => ({ configured: Cloud.isCloudConfigured(), user: Cloud.getUser() });

// ---------- Thème ----------
const THEME_COLORS = { light: '#f1efe8', dark: '#0c0e13' };
function systemPrefersDark() { try { return matchMedia('(prefers-color-scheme: dark)').matches; } catch { return false; } }
function effectiveTheme() {
  const forced = document.documentElement.dataset.theme;
  return forced || (systemPrefersDark() ? 'dark' : 'light');
}
function applyThemeMeta() {
  const m = document.querySelector('meta[name="theme-color"]');
  if (m) m.setAttribute('content', THEME_COLORS[effectiveTheme()]);
}
function toggleTheme() {
  const next = effectiveTheme() === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem('boussole:theme', next); } catch {}
  applyThemeMeta();
  render();
}
function initTheme() {
  let stored = null; try { stored = localStorage.getItem('boussole:theme'); } catch {}
  document.documentElement.dataset.theme = (stored === 'light' || stored === 'dark') ? stored : 'dark';
  applyThemeMeta();
}
const isConfigured = () => Boolean(S.getState().profil.nom_activite) || S.getProduits({ withArchived: true }).length > 0;

// ---------- Rendu ----------
function render() {
  const tb = $('#topbar');
  tb.style.display = (screen === 'welcome') ? 'none' : '';
  tb.innerHTML = UI.topbarHTML(cloudCtx(), effectiveTheme());
  const view = $('#view');
  if (screen === 'config') view.innerHTML = UI.viewConfigHTML(wizard || (wizard = { step: 1, charges: UI.defaultCharges() }));
  else if (screen === 'welcome') view.innerHTML = UI.viewWelcomeHTML();
  else if (screen === 'accueil') view.innerHTML = UI.viewAccueilHTML(period);
  else if (screen === 'bilan') view.innerHTML = UI.viewBilanHTML();
  else if (screen === 'reglages') view.innerHTML = UI.viewReglagesHTML(cloudCtx());
  else view.innerHTML = UI.viewVentesHTML(venteFilter);
  $('#nav').innerHTML = navVisible() ? UI.navHTML(screen) : '';
  $('#nav').style.display = navVisible() ? '' : 'none';
  hydrateIcons(document);
  if (screen === 'accueil' && animateNext) {
    const dash = view.querySelector('.view--dash'); if (dash) dash.classList.add('is-enter');
    animateCounts(view);
  }
  animateNext = false;
  view.scrollTop = 0;
}
function navVisible() { return screen !== 'config' && screen !== 'welcome'; }

function loadPeriod() {
  try { const p = JSON.parse(localStorage.getItem('boussole:period') || 'null'); if (p && p.gran) return { gran: p.gran, offset: 0 }; } catch {}
  return { gran: 'mois', offset: 0 };
}
function savePeriod() { try { localStorage.setItem('boussole:period', JSON.stringify({ gran: period.gran })); } catch {} }

// ---------- Filtre de l'historique des ventes ----------
function ymd(d) { return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; }
function venteRange(preset) {
  const now = new Date();
  if (preset === 'semaine') { const s = new Date(now); s.setDate(now.getDate() - 6); return { from: ymd(s), to: ymd(now) }; }
  if (preset === 'mois') { return { from: ymd(new Date(now.getFullYear(), now.getMonth(), 1)), to: ymd(now) }; }
  if (preset === 'tout') { return { from: '', to: '' }; }
  return { from: ymd(now), to: ymd(now) }; // jour
}
function refreshVentes() {
  if (screen !== 'ventes') return;
  const view = $('#view'); const top = view.scrollTop;
  view.innerHTML = UI.viewVentesHTML(venteFilter);
  hydrateIcons(view); view.scrollTop = top;
}
// Rafraîchit uniquement le tableau de bord en conservant la position de défilement.
function refreshDash() {
  const view = $('#view');
  const top = view.scrollTop;
  view.innerHTML = UI.viewAccueilHTML(period);
  const dash = view.querySelector('.view--dash'); if (dash) dash.classList.add('is-enter');
  hydrateIcons(view);
  animateCounts(view);
  view.scrollTop = top;
}

// ---------- Splash (écran de chargement au logo) ----------
function splashEl() { return document.getElementById('splash'); }
function hideSplash() { const s = splashEl(); if (s) s.classList.add('splash--gone'); }
function showSplash(tag) {
  const s = splashEl(); if (!s) return;
  const t = s.querySelector('.splash__tag'); if (t && tag) t.textContent = tag;
  s.classList.remove('splash--gone');
}

// ---------- Compteurs animés (chiffres qui montent) ----------
function animateCounts(root) {
  try { if (matchMedia('(prefers-reduced-motion: reduce)').matches) return; } catch {}
  root.querySelectorAll('[data-count]').forEach((el) => {
    const to = Number(el.dataset.count); if (!isFinite(to)) return;
    const fmt = el.dataset.fmt || 'num';
    const fmtFn = fmt === 'f' ? S.formatF : (fmt === 'pct' ? (v) => Math.round(v) + ' %' : S.formatNombre);
    const dur = 780, t0 = performance.now();
    const tick = (now) => {
      const p = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - p, 3);
      el.textContent = fmtFn(to * e);
      if (p < 1) requestAnimationFrame(tick); else el.textContent = fmtFn(to);
    };
    requestAnimationFrame(tick);
  });
}

function setScreen(s) {
  if (s === 'accueil') animateNext = true;
  screen = s; if (s !== 'config') wizard = null;
  try { if (s !== 'config' && s !== 'welcome') location.hash = s; } catch {}
  render();
}

// Re-render « live » quand les données changent (hors saisie wizard).
S.subscribe(() => { if (screen !== 'config') render(); });
Cloud.onAuth((user) => {
  const loggedInNow = !!user && !prevUser;
  prevUser = user || null;
  if (user && screen === 'welcome') { screen = isConfigured() ? 'accueil' : 'config'; if (screen === 'accueil') animateNext = true; }
  if (loggedInNow && pendingLogin) {
    pendingLogin = false;
    showSplash('Chargement de ton tableau de bord…');
    render();
    setTimeout(hideSplash, 1150);
  } else {
    render();
  }
});

// ---------- Helpers de saisie ----------
function readProduct(scope) {
  const q = (sel) => scope.querySelector(sel);
  return {
    nom: (q('#pf-nom')?.value || '').trim(),
    modele: scope.querySelector('.seg__b.is-on')?.dataset.modele || 'transformation',
    prix_vente: q('#pf-prix')?.value || 0,
    couts: [...scope.querySelectorAll('#pf-couts .crow')].map((r) => ({
      libelle: (r.querySelector('[data-pf="libelle"]').value || '').trim(),
      montant: r.querySelector('[data-pf="montant"]').value,
    })).filter((c) => c.libelle || c.montant),
  };
}
function readCharges(scope) {
  return [...scope.querySelectorAll('.crow[data-i]')].map((r) => ({
    libelle: (r.querySelector('[data-cf="libelle"]').value || '').trim(),
    montant: r.querySelector('[data-cf="montant"]').value,
  })).filter((c) => c.libelle || c.montant);
}
function productScope(target) {
  const modal = target.closest('.modal');
  return modal ? modal.querySelector('.modal__body') : $('#view');
}
function reRenderProduct(scope, product) {
  if (scope.classList.contains('modal__body')) {
    scope.innerHTML = UI.productFormFields(product);
  } else {
    wizard.produit = product;
    render();
    return;
  }
  hydrateIcons(scope);
}

// ---------- Produits (modale) ----------
function openProductModal(id) {
  const p = id ? S.getProduit(id) : { modele: 'transformation', couts: [] };
  UI.openModal(UI.modalShell(id ? 'Modifier le produit' : 'Nouveau produit',
    UI.productFormFields(p),
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn" data-action="save-produit" data-id="${id || ''}">Enregistrer</button>`));
  hydrateIcons($('#modal-root'));
}
function saveProduct(id) {
  const body = $('#modal-root .modal__body');
  const p = readProduct(body);
  if (!p.nom) return UI.toast('Donne un nom au produit', 'err');
  if (id) S.updateProduit(id, p); else S.addProduit(p);
  UI.closeModal();
  UI.toast('Produit enregistré');
}

// ---------- Charges (modale) ----------
function openChargeModal() {
  UI.openModal(UI.modalShell('Nouvelle charge fixe',
    `<div class="field"><label for="cf-lib">Libellé</label>
       <input id="cf-lib" class="input" placeholder="Ex. Loyer, Électricité"></div>
     <div class="field"><label for="cf-amt">Montant par mois</label>
       <div class="inwrap"><input id="cf-amt" class="input" type="number" inputmode="numeric" placeholder="0"><span class="inwrap__cur">F</span></div></div>`,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn" data-action="save-charge">Ajouter</button>`));
  hydrateIcons($('#modal-root'));
}

// ---------- Objectif de bénéfice (modale) ----------
function openObjectifModal() {
  const cur = S.getObjectif();
  UI.openModal(UI.modalShell('Objectif de bénéfice',
    `<p class="modal__lead">Quel bénéfice net veux-tu atteindre ce mois-ci&nbsp;?</p>
     <div class="field"><label for="obj-amt">Objectif mensuel</label>
       <div class="inwrap"><input id="obj-amt" class="input input--lg" type="number" inputmode="numeric" value="${cur || ''}" placeholder="Ex. 100000"><span class="inwrap__cur">F</span></div></div>
     <p class="modal__note">Tu suis ta progression en direct sur le tableau de bord. Mets 0 pour le retirer.</p>`,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn" data-action="save-objectif">Enregistrer</button>`));
  hydrateIcons($('#modal-root'));
}

// ---------- Dépense (modale) ----------
function depensesRecentesHTML() {
  const list = S.getDepenses().slice().sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 5);
  if (!list.length) return '';
  const rows = list.map((d) => `<li class="deprow">
      <span class="deprow__cat">${UI.esc(d.categorie)}</span>
      <span class="deprow__lib">${UI.esc(d.libelle || '—')}</span>
      <span class="deprow__amt">${S.formatF(d.montant)}</span>
      <button class="deprow__del" data-action="del-depense" data-id="${d.id}" title="Supprimer"><span data-icon="close"></span></button>
    </li>`).join('');
  return `<div class="field"><label>Dépenses récentes</label><ul class="deplist">${rows}</ul></div>`;
}
function openDepenseModal() {
  const cats = S.DEPENSE_CATS.map((c, i) => `<button type="button" class="catchip ${i === 0 ? 'is-on' : ''}" data-action="dep-cat" data-cat="${UI.esc(c)}">${UI.esc(c)}</button>`).join('');
  const today = new Date().toISOString().slice(0, 10);
  UI.openModal(UI.modalShell('Ajouter une dépense',
    `<div class="field"><label for="dp-amt">Montant</label>
       <div class="inwrap"><input id="dp-amt" class="input input--lg" type="number" inputmode="numeric" placeholder="0"><span class="inwrap__cur">F</span></div></div>
     <div class="field"><label>Catégorie</label><div class="catchips" id="dp-cats">${cats}</div></div>
     <div class="field"><label for="dp-lib">Libellé (optionnel)</label>
       <input id="dp-lib" class="input" placeholder="Ex. Taxi marché, sacs, facture SBEE"></div>
     <div class="field"><label for="dp-date">Date</label>
       <input id="dp-date" class="input" type="date" value="${today}"></div>
     ${depensesRecentesHTML()}`,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn btn--danger" data-action="save-depense"><span data-icon="minus"></span> Enregistrer la dépense</button>`));
  hydrateIcons($('#modal-root'));
}

// ---------- Solde de caisse (modale) ----------
function openCaisseModal() {
  const cur = S.getSoldeInitial();
  UI.openModal(UI.modalShell('Solde de caisse',
    `<p class="modal__lead">Le <strong>fond de caisse</strong> = l'argent que tu avais avant de commencer à utiliser Boussole.</p>
     <div class="field"><label for="cs-amt">Fond de départ</label>
       <div class="inwrap"><input id="cs-amt" class="input input--lg" type="number" inputmode="numeric" value="${cur || ''}" placeholder="0"><span class="inwrap__cur">F</span></div></div>
     <p class="modal__note">Ensuite chaque vente ajoute à la caisse et chaque dépense la diminue, automatiquement.</p>`,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn" data-action="save-caisse">Enregistrer</button>`));
  hydrateIcons($('#modal-root'));
}

// ---------- Vente détaillée (modale) ----------
function openSellCustom(id) {
  const p = S.getProduit(id); if (!p) return;
  UI.openModal(UI.modalShell('Enregistrer une vente',
    `<p class="modal__lead">${UI.esc(p.nom)}</p>
     <div class="grid2">
       <div class="field"><label for="sv-q">Quantité</label>
         <input id="sv-q" class="input" type="number" inputmode="numeric" value="1" min="1"></div>
       <div class="field"><label for="sv-p">Prix unitaire</label>
         <div class="inwrap"><input id="sv-p" class="input" type="number" inputmode="numeric" value="${p.prix_vente}"><span class="inwrap__cur">F</span></div></div>
     </div>
     <div class="field"><label for="sv-d">Date</label>
       <input id="sv-d" class="input" type="date" value="${new Date().toISOString().slice(0, 10)}"></div>`,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn btn--sell" data-action="save-vente" data-id="${id}">Enregistrer la vente</button>`));
  hydrateIcons($('#modal-root'));
}

// ---------- Auth (modale) ----------
function openAuthModal() {
  const isUp = authMode === 'signup';
  UI.openModal(UI.modalShell(isUp ? 'Créer un compte' : 'Se connecter',
    `<div class="authswitch">
        <button class="authswitch__b ${!isUp ? 'is-on' : ''}" data-action="auth-mode" data-mode="signin">Connexion</button>
        <button class="authswitch__b ${isUp ? 'is-on' : ''}" data-action="auth-mode" data-mode="signup">Créer un compte</button>
     </div>
     <div class="field"><label for="au-mail">E-mail</label>
        <input id="au-mail" class="input" type="email" autocomplete="email" placeholder="toi@exemple.com"></div>
     <div class="field"><label for="au-pass">Mot de passe</label>
        <input id="au-pass" class="input" type="password" autocomplete="${isUp ? 'new-password' : 'current-password'}" placeholder="Au moins 6 caractères"></div>
     <p class="modal__note">La synchronisation garde tes données à jour sur mobile et PC.</p>`,
    `<button class="btn btn--ghost" data-action="close-modal">Fermer</button>
     <button class="btn" data-action="auth-submit">${isUp ? 'Créer' : 'Connexion'}</button>`));
  hydrateIcons($('#modal-root'));
}
async function authSubmit() {
  const email = $('#au-mail').value.trim();
  const pass = $('#au-pass').value;
  if (!email || pass.length < 6) return UI.toast('E-mail + mot de passe (6+ caractères)', 'err');
  const btn = $('#modal-root [data-action="auth-submit"]'); btn.disabled = true; btn.textContent = '…';
  try {
    if (authMode === 'signup') {
      const r = await Cloud.signUp(email, pass);
      if (r.user && !r.session) { UI.closeModal(); UI.toast('Compte créé — vérifie ta boîte e-mail pour confirmer'); }
      else { pendingLogin = true; UI.closeModal(); UI.toast('Compte créé et connecté'); }
    } else {
      await Cloud.signIn(email, pass);
      pendingLogin = true; UI.closeModal(); UI.toast('Connecté — synchronisation activée');
    }
  } catch (e) {
    btn.disabled = false; btn.textContent = authMode === 'signup' ? 'Créer' : 'Connexion';
    UI.toast(traduireErreur(e), 'err');
  }
}
function traduireErreur(e) {
  const m = (e && e.message || '').toLowerCase();
  if (m.includes('invalid login')) return 'E-mail ou mot de passe incorrect';
  if (m.includes('already registered')) return 'Cet e-mail a déjà un compte';
  if (m.includes('email not confirmed')) return 'Confirme ton e-mail avant de te connecter';
  return e.message || 'Une erreur est survenue';
}

// ---------- Bilan : partage / impression ----------
function shareBilan() {
  const t = S.trimestreDe();
  const nom = S.getState().profil.nom_activite || 'Mon activité';
  let txt = `BOUSSOLE — Bilan trimestriel\n${nom}\nT${t.numero} ${t.annee}\n\n`;
  t.mois.forEach((m) => { txt += `${m.label} : bénéfice ${S.formatF(m.benefice)}\n`; });
  txt += `\nRevenu total : ${S.formatF(t.totaux.revenu)}\nBénéfice net total : ${S.formatF(t.totaux.benefice)}\n`;
  txt += t.viable ? `Activité rentable ce trimestre.\n` : `Pas encore rentable ce trimestre.\n`;
  const a = S.analyseBusiness();
  txt += `\nSanté du business : ${a.score}/100`;
  if (a.conseils[0] && a.conseils[0].priorite !== 'info') txt += `\nÀ améliorer : ${a.conseils[0].titre}`;
  window.open('https://wa.me/?text=' + encodeURIComponent(txt), '_blank');
}
function printBilan() {
  const t = S.trimestreDe();
  const a = S.analyseBusiness();
  const nom = S.getState().profil.nom_activite || 'Mon activité';
  const rows = t.mois.map((m) => `<tr><td>${m.label}</td><td>${S.formatF(m.revenu)}</td><td>${S.formatF(m.relance)}</td><td>${S.formatF(m.charges_couvertes)}</td><td>${S.formatF(m.benefice)}</td></tr>`).join('');
  $('#print-area').innerHTML = `
    <h1>Bilan trimestriel — T${t.numero} ${t.annee}</h1>
    <p class="p-sub">${UI.esc(nom)} · généré le ${new Date().toLocaleDateString('fr-FR')}</p>
    <table><thead><tr><th>Mois</th><th>Revenu</th><th>Relance production</th><th>Charges fixes</th><th>Bénéfice net</th></tr></thead>
      <tbody>${rows}</tbody>
      <tfoot><tr><td>Total</td><td>${S.formatF(t.totaux.revenu)}</td><td>${S.formatF(t.totaux.relance)}</td><td>${S.formatF(t.totaux.charges_couvertes)}</td><td>${S.formatF(t.totaux.benefice)}</td></tr></tfoot>
    </table>
    <p class="p-verdict">${t.viable ? 'Activité rentable ce trimestre.' : 'Activité pas encore rentable ce trimestre.'}</p>
    <h2 style="font-size:15px;margin:18px 0 6px">Diagnostic — santé ${a.score}/100</h2>
    <ul>${a.etat.map((e) => `<li>${UI.esc(e)}</li>`).join('')}</ul>
    ${a.conseils.filter((c) => c.priorite !== 'info').length ? `<h2 style="font-size:15px;margin:14px 0 6px">À améliorer</h2><ul>${a.conseils.filter((c) => c.priorite !== 'info').map((c) => `<li><strong>${UI.esc(c.titre)}</strong> — ${UI.esc(c.detail)}</li>`).join('')}</ul>` : ''}
    <p class="p-foot">Boussole — NEBULA Agency</p>`;
  window.print();
}

// ---------- Sauvegarde ----------
function doExport() {
  const blob = new Blob([S.exportData()], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `boussole-sauvegarde-${new Date().toISOString().slice(0, 10)}.json`;
  a.click(); URL.revokeObjectURL(a.href);
  UI.toast('Sauvegarde exportée');
}
function doImport() {
  const inp = document.createElement('input');
  inp.type = 'file'; inp.accept = 'application/json,.json';
  inp.onchange = () => {
    const f = inp.files[0]; if (!f) return;
    const r = new FileReader();
    r.onload = () => { try { S.importData(r.result); UI.toast('Sauvegarde importée'); } catch { UI.toast('Fichier invalide', 'err'); } };
    r.readAsText(f);
  };
  inp.click();
}

// ---------- Wizard ----------
function wizardNext() {
  const view = $('#view');
  if (wizard.step === 1) {
    wizard.nom = ($('#wz-nom')?.value || '').trim();
    if (!wizard.nom) return UI.toast('Donne un nom à ton activité', 'err');
    wizard.step = 2; wizard.produit = wizard.produit || { modele: 'transformation', couts: [] };
    return render();
  }
  if (wizard.step === 2) {
    wizard.produit = readProduct(view);
    if (!wizard.produit.nom) return UI.toast('Nom du produit requis', 'err');
    wizard.step = 3; wizard.charges = wizard.charges || UI.defaultCharges();
    return render();
  }
  // step 3 — terminer
  wizard.charges = readCharges(view);
  S.setProfil({ nom_activite: wizard.nom });
  S.addProduit(wizard.produit);
  wizard.charges.forEach((c) => S.addChargeFixe(c));
  const w = wizard; wizard = null; screen = 'ventes'; render();
  UI.toast(`Bienvenue ${w.nom} — prêt à vendre`);
  maybeShowTuto();
}

// ---------- Didacticiel ----------
function openTutoriel(i) {
  tutoStep = Math.max(0, Math.min(UI.TUTO_STEPS.length - 1, i));
  UI.openModal(UI.tutorielHTML(tutoStep));
  hydrateIcons($('#modal-root'));
}
function tutoSeen() { try { return localStorage.getItem('boussole:tuto-vu') === '1'; } catch { return false; } }
function markTutoSeen() { try { localStorage.setItem('boussole:tuto-vu', '1'); } catch {} }
function maybeShowTuto() { if (!tutoSeen() && isConfigured()) { markTutoSeen(); setTimeout(() => openTutoriel(0), 350); } }

// ---------- Délégation d'événements ----------
document.addEventListener('click', (e) => {
  const el = e.target.closest('[data-action]');
  if (!el) return;
  const a = el.dataset.action;
  const id = el.dataset.id;

  switch (a) {
    case 'go': return setScreen(el.dataset.screen);
    case 'go-config': wizard = { step: 1, charges: UI.defaultCharges() }; return setScreen('config');
    case 'welcome-signup': authMode = 'signup'; return openAuthModal();
    case 'welcome-signin': authMode = 'signin'; return openAuthModal();
    case 'welcome-skip': wizard = { step: 1, charges: UI.defaultCharges() }; return setScreen('config');
    case 'toggle-theme': return toggleTheme();

    // tableau de bord — période & objectif
    case 'set-gran': if (period.gran !== el.dataset.gran) { period.gran = el.dataset.gran; period.offset = 0; savePeriod(); refreshDash(); } return;
    case 'period-prev': period.offset -= 1; return refreshDash();
    case 'period-next': if (period.offset < 0) { period.offset += 1; refreshDash(); } return;
    case 'edit-objectif': return openObjectifModal();
    case 'save-objectif': { const v = Number($('#obj-amt').value) || 0; S.setObjectif(v); UI.closeModal(); UI.toast(v > 0 ? 'Objectif enregistré' : 'Objectif retiré'); return; }

    // dépenses & caisse
    case 'add-depense': return openDepenseModal();
    case 'dep-cat': { const box = $('#dp-cats'); if (box) box.querySelectorAll('.catchip').forEach((c) => c.classList.toggle('is-on', c === el)); return; }
    case 'save-depense': {
      const amt = Number($('#dp-amt').value) || 0;
      if (amt <= 0) return UI.toast('Entre un montant', 'err');
      const on = $('#modal-root .catchip.is-on');
      const cat = on ? on.dataset.cat : 'Divers';
      const lib = ($('#dp-lib').value || '').trim();
      const d = $('#dp-date').value;
      S.addDepense({ libelle: lib, categorie: cat, montant: amt, date: d ? new Date(d).toISOString() : undefined });
      UI.closeModal(); UI.toast('Dépense enregistrée'); return;
    }
    case 'del-depense': { S.deleteDepense(id); const row = el.closest('.deprow'); if (row) row.remove(); UI.toast('Dépense supprimée'); return; }
    case 'edit-caisse': return openCaisseModal();
    case 'save-caisse': { const v = Number($('#cs-amt').value) || 0; S.setSoldeInitial(v); UI.closeModal(); UI.toast('Fond de caisse enregistré'); return; }

    // historique ventes — filtres
    case 'vf-preset': { venteFilter = Object.assign(venteFilter, { preset: el.dataset.preset }, venteRange(el.dataset.preset)); return refreshVentes(); }
    case 'close-modal': return UI.closeModal();
    case 'confirm-ok': { const fn = $('#modal-root')._confirmOk; UI.closeModal(); if (fn) fn(); return; }

    // ventes
    case 'sell': { S.addVente({ produit_id: id, qte: 1 }); UI.toast('Vente enregistrée'); pulseBenef(); return; }
    case 'sell-custom': return openSellCustom(id);
    case 'save-vente': {
      const q = Number($('#sv-q').value) || 1, prix = Number($('#sv-p').value) || 0, d = $('#sv-d').value;
      S.addVente({ produit_id: id, qte: q, prix_unitaire: prix, date: d ? new Date(d).toISOString() : undefined });
      UI.closeModal(); UI.toast('Vente enregistrée'); return;
    }
    case 'del-vente': return S.deleteVente(id);

    // bilan
    case 'share-bilan': return shareBilan();
    case 'print-bilan': return printBilan();

    // produits
    case 'add-produit': return openProductModal(null);
    case 'edit-produit': return openProductModal(id);
    case 'save-produit': return saveProduct(id);
    case 'del-produit': return UI.confirmDialog(
      { title: 'Supprimer le produit', message: 'Le produit et ses ventes seront supprimés. Continuer ?', danger: true, okLabel: 'Supprimer' },
      () => { S.deleteProduit(id); UI.toast('Produit supprimé'); });

    // product form (partagé wizard/modale)
    case 'pf-modele': { const sc = productScope(el); const p = readProduct(sc); p.modele = el.dataset.modele; return reRenderProduct(sc, p); }
    case 'pf-add-cout': { const sc = productScope(el); const p = readProduct(sc); p.couts.push({ libelle: '', montant: '' }); return reRenderProduct(sc, p); }
    case 'pf-del-cout': { const sc = productScope(el); const p = readProduct(sc); p.couts.splice(Number(el.dataset.i), 1); return reRenderProduct(sc, p); }

    // charges
    case 'add-charge': return openChargeModal();
    case 'save-charge': {
      const lib = ($('#cf-lib').value || '').trim(), amt = $('#cf-amt').value;
      if (!lib) return UI.toast('Libellé requis', 'err');
      S.addChargeFixe({ libelle: lib, montant: amt }); UI.closeModal(); UI.toast('Charge ajoutée'); return;
    }
    case 'del-charge': return UI.confirmDialog(
      { title: 'Supprimer la charge', message: 'Supprimer cette charge fixe ?', danger: true, okLabel: 'Supprimer' },
      () => { S.deleteChargeFixe(id); UI.toast('Charge supprimée'); });

    // wizard charges
    case 'wz-add-charge': { const box = $('#wz-charges'); const rows = readCharges($('#view')); rows.push({ libelle: '', montant: '' }); box.innerHTML = UI.chargeRowsHTML(rows); hydrateIcons(box); return; }
    case 'wz-del-charge': { const box = $('#wz-charges'); const rows = readCharges($('#view')); rows.splice(Number(el.dataset.i), 1); box.innerHTML = UI.chargeRowsHTML(rows.length ? rows : []); hydrateIcons(box); return; }
    case 'wz-next': return wizardNext();
    case 'wz-back': if (wizard && wizard.step > 1) { wizard.step--; render(); } return;

    // didacticiel
    case 'open-tuto': return openTutoriel(0);
    case 'tuto-next': { const i = Number(el.dataset.i); if (i >= UI.TUTO_STEPS.length - 1) { markTutoSeen(); UI.closeModal(); } else openTutoriel(i + 1); return; }
    case 'tuto-prev': return openTutoriel(Number(el.dataset.i) - 1);

    // cloud / auth
    case 'open-auth': authMode = 'signin'; return openAuthModal();
    case 'auth-mode': authMode = el.dataset.mode; return openAuthModal();
    case 'auth-submit': return authSubmit();
    case 'logout': return Cloud.signOut().then(() => UI.toast('Déconnecté (données gardées sur cet appareil)'));
    case 'cloud-info': return UI.toast('Mode local : données sur cet appareil. Configure Supabase pour synchroniser.', 'ok');

    // sauvegarde
    case 'export': return doExport();
    case 'import': return doImport();
    case 'wipe': return UI.confirmDialog(
      { title: 'Tout effacer', message: 'Toutes les données locales seront effacées définitivement. Pense à exporter avant.', danger: true, okLabel: 'Effacer' },
      () => { S.resetLocal(); screen = 'ventes'; render(); UI.toast('Données effacées'); });
  }
});

// nom d'activité (réglages) — sur blur
document.addEventListener('change', (e) => {
  const el = e.target;
  if (el.matches('[data-action="save-nom"]')) S.setProfil({ nom_activite: el.value.trim() });
  else if (el.matches('[data-action="vf-from"]')) { venteFilter.from = el.value; venteFilter.preset = 'custom'; refreshVentes(); }
  else if (el.matches('[data-action="vf-to"]')) { venteFilter.to = el.value; venteFilter.preset = 'custom'; refreshVentes(); }
  else if (el.matches('[data-action="vf-produit"]')) { venteFilter.produitId = el.value; refreshVentes(); }
  else if (el.matches('[data-action="vf-search"]')) { venteFilter.q = el.value; refreshVentes(); }
});
// recherche « live » (chaque frappe) sans perdre le focus du champ
document.addEventListener('input', (e) => {
  const el = e.target;
  if (el.matches('[data-action="vf-search"]')) {
    venteFilter.q = el.value;
    clearTimeout(window.__vfSearchT);
    window.__vfSearchT = setTimeout(() => {
      refreshVentes();
      const s = document.querySelector('[data-action="vf-search"]');
      if (s) { s.focus(); const v = s.value; s.setSelectionRange(v.length, v.length); }
    }, 220);
  }
});

function pulseBenef() {
  const el = $('.env--benefice'); if (!el) return;
  el.classList.remove('pulse'); void el.offsetWidth; el.classList.add('pulse');
}

// ---------- Démarrage ----------
async function boot() {
  initTheme();
  S.initStore();
  if (isConfigured()) screen = 'accueil';
  else screen = CLOUD_ENABLED ? 'welcome' : 'config';
  const h = (location.hash || '').replace('#', '');
  if (isConfigured() && ['accueil', 'ventes', 'bilan', 'reglages'].includes(h)) screen = h;
  if (screen === 'config') wizard = { step: 1, charges: UI.defaultCharges() };
  if (screen === 'accueil') animateNext = true;
  render();
  setTimeout(hideSplash, 1300);   // splash signature « boussole » : durée minimale
  maybeShowTuto();
  if (CLOUD_ENABLED) { try { await Cloud.initSupabase(); } catch (e) { console.warn('supabase init', e); } }
  // service worker (offline)
  if ('serviceWorker' in navigator) navigator.serviceWorker.register(`sw.js?v=${APP_VERSION}`).catch(() => {});
}
boot();

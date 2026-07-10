// Boussole — bootstrap, routeur, événements.
import { APP_VERSION, CLOUD_ENABLED, CURRENCIES } from './config.js';
import { hydrateIcons } from './icons.js';
import * as S from './store.js';
import * as Cloud from './supabase.js';
import * as UI from './ui.js';
import * as I18n from './i18n.js';
import * as BT from './btprint.js';
import * as Sec from './security.js';
import { NEBULA_MOMO, NEBULA_WHATSAPP, ADMIN_ROUTE } from './config.js';

let screen = 'ventes';
let wizard = null;
let authMode = 'signin';
let tutoStep = 0;
let period = loadPeriod();
let animateNext = false;   // déclenche cascades + compteurs à l'entrée (pas sur maj live)
let prevUser = null;
let pendingLogin = false;  // vrai après un login volontaire -> 2e splash
let venteFilter = Object.assign({ preset: 'jour', produitId: '', q: '', mode: '', vendeur: '' }, venteRange('jour'));
let depFilter = Object.assign({ preset: 'mois', categorie: '', q: '' }, venteRange('mois'));
let chat = []; // conversation assistant (en mémoire de session)
let rapGran = 'jour'; // période du rapport (écran Bilan)
let stockFilter = { statut: 'tous', q: '' };
let fabOpen = false;         // speed-dial FAB (mobile)
let overlay = null;          // null | 'drawer' | 'notifs'
let sidebarAcc = null;       // groupe accordéon ouvert (sidebar desktop)
let resetScroll = true;      // vrai = remet le scroll en haut (navigation), faux = conserve (maj live)

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

// ---------- Personnalisation (accent, taille du texte, densité, coins) ----------
const PREF_DEFAULTS = { accent: 'ambre', textsize: 'normal', density: 'confort', corners: 'doux' };
function applyPref(k, v) {
  const el = document.documentElement;
  if (v && v !== PREF_DEFAULTS[k]) el.dataset[k] = v; else delete el.dataset[k];
}
function initPrefs() {
  Object.keys(PREF_DEFAULTS).forEach((k) => {
    let v = null; try { v = localStorage.getItem('boussole:' + k); } catch {}
    applyPref(k, v || PREF_DEFAULTS[k]);
  });
}
function setPref(k, v) {
  try { localStorage.setItem('boussole:' + k, v); } catch {}
  applyPref(k, v);
}
function refreshReglages() {
  if (screen !== 'reglages') return;
  const view = $('#view'); const top = view.scrollTop;
  view.innerHTML = UI.viewReglagesHTML(cloudCtx());
  hydrateIcons(view); view.scrollTop = top;
}
const deviseSym = () => (CURRENCIES[S.getDevise()] || { symbol: 'F' }).symbol;

// Insère un texte à l'endroit du curseur d'un champ + sauve le modèle.
function insertAtCursor(ta, text) {
  const s = ta.selectionStart == null ? ta.value.length : ta.selectionStart;
  const e = ta.selectionEnd == null ? ta.value.length : ta.selectionEnd;
  ta.value = ta.value.slice(0, s) + text + ta.value.slice(e);
  const pos = s + text.length; ta.focus(); try { ta.setSelectionRange(pos, pos); } catch {}
  if (ta.dataset.key) S.setWaTemplate(ta.dataset.key, ta.value);
}

// ---------- Impression Bluetooth ----------
function btErr(e) {
  const m = (e && e.message) || '';
  if (/cancel|NotFoundError|chooser|User cancelled/i.test(m + (e && e.name || ''))) return 'Connexion annulée.';
  return 'Impression impossible. Vérifie que l’imprimante est allumée et proche.';
}
function printReceiptBT(d) {
  const p = S.getState().profil;
  BT.printReceipt({
    commerce: p.nom_activite || 'Boussole',
    date: new Date(d.date).toLocaleString('fr-FR'),
    lignes: d.lignes, total: d.total,
    mode: S.PAYMENT_LABELS[d.mode] || d.mode, vendeur: d.vendeur, devise: deviseSym(),
    footer: S.renderTemplate(S.getWaTemplate('recu'), { commerce: p.nom_activite || '', total: S.formatF(d.total) }),
  }).then(() => UI.toast('Reçu envoyé à l’imprimante')).catch((e) => UI.toast(btErr(e), 'err'));
}

// ---------- Langue : ajout / éditeur de langue locale ----------
function openLangAdd() {
  const code = I18n.addCustomLang('locale-' + Date.now().toString(36), 'Ma langue');
  refreshReglages();
  openLangEditor(code);
}
function openLangEditor(code) {
  const lg = I18n.getCustomLangs().find((l) => l.code === code);
  if (!lg) return;
  const rows = I18n.CORE_TERMS.map((fr) => `<div class="lted">
      <span class="lted__fr">${UI.esc(fr)}</span>
      <input class="input lted__in" data-action="lted-term" data-code="${code}" data-fr="${UI.esc(fr)}" value="${UI.esc(lg.terms[fr] || '')}" placeholder="…" autocomplete="off">
    </div>`).join('');
  UI.openModal(UI.modalShell('Traduire l’interface',
    `<div class="field"><label for="lted-name">Nom de la langue</label>
       <input id="lted-name" class="input" data-action="lted-name" data-code="${code}" value="${UI.esc(lg.natif)}" autocomplete="off"></div>
     ${UI.zhelp('Saisis les mots dans ta langue. Ce que tu laisses vide restera en français. Tu peux revenir corriger à tout moment.')}
     <div class="ltedlist">${rows}</div>`,
    `<button class="btn btn--danger-ghost btn--sm" data-action="lang-del" data-code="${code}">Supprimer</button>
     <button class="btn" data-action="close-modal">Terminé</button>`));
  hydrateIcons($('#modal-root'));
}
// ---------- Compte : mot de passe, membres d'équipe ----------
function openChangePwd() {
  UI.openModal(UI.modalShell('Changer le mot de passe',
    `<div class="field"><label for="np">Nouveau mot de passe</label>
       <input id="np" class="input" type="password" autocomplete="new-password" placeholder="Au moins 6 caractères"></div>`,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn" data-action="save-pwd">Enregistrer</button>`));
  hydrateIcons($('#modal-root'));
}
async function savePwd() {
  const v = (($('#np') || {}).value || '').trim();
  if (v.length < 6) return UI.toast('6 caractères minimum', 'err');
  try { await Cloud.updatePassword(v); UI.closeModal(); UI.toast('Mot de passe changé'); }
  catch (e) { UI.toast('Échec : ' + (e.message || ''), 'err'); }
}
function openMembreModal(mid) {
  const m = mid ? S.getMembre(mid) : null;
  const roleOpts = S.ROLES.map((r) => `<option value="${r}" ${m && m.role === r ? 'selected' : ''}>${S.ROLE_LABELS[r]}</option>`).join('');
  UI.openModal(UI.modalShell(m ? 'Modifier le membre' : 'Nouveau membre',
    `<div class="field"><label for="m-nom">Nom</label><input id="m-nom" class="input" value="${m ? UI.esc(m.nom) : ''}" placeholder="Ex. Koffi" autocomplete="off"></div>
     <div class="field"><label for="m-role">Rôle</label>
       <select id="m-role" class="input" data-action="m-role">${roleOpts}</select>
       <p class="fieldhint" id="m-rolehint">${S.ROLE_DESCS[m ? m.role : 'vendeur']}</p></div>
     <div class="field"><label for="m-pin">Code du vendeur (4 chiffres, optionnel)</label>
       <input id="m-pin" class="input" inputmode="numeric" maxlength="4" placeholder="${m && m.pin ? '•••• (déjà défini)' : 'Pour ouvrir sa session'}" autocomplete="off"></div>
     ${m ? `<label class="switchrow"><input type="checkbox" id="m-actif" ${m.actif ? 'checked' : ''}> Membre actif</label>` : ''}`,
    `${m ? `<button class="btn btn--danger-ghost btn--sm" data-action="membre-del" data-id="${m.id}">Supprimer</button>` : ''}
     <button class="btn" data-action="membre-save" data-id="${m ? m.id : ''}">Enregistrer</button>`));
  hydrateIcons($('#modal-root'));
}
async function membreSave(mid) {
  const nom = (($('#m-nom') || {}).value || '').trim();
  const role = ($('#m-role') || {}).value || 'vendeur';
  const pin = (($('#m-pin') || {}).value || '').trim();
  const actif = $('#m-actif') ? $('#m-actif').checked : true;
  if (!nom) return UI.toast('Donne un nom', 'err');
  let pinRec = null;
  if (pin) { if (!/^\d{4}$/.test(pin)) return UI.toast('Le code doit faire 4 chiffres', 'err'); pinRec = await Sec.makePinRecord(pin); }
  if (mid) { const patch = { nom, role, actif }; if (pinRec) patch.pin = pinRec; S.updateMembre(mid, patch); }
  else { S.addMembre(nom, role); const nm = S.getEquipe().find((x) => x.nom.toLowerCase() === nom.toLowerCase()); if (nm && pinRec) S.updateMembre(nm.id, { pin: pinRec }); }
  UI.closeModal(); refreshReglages(); UI.toast('Équipe mise à jour');
}
function openHandOver() {
  const eq = S.getEquipe().filter((m) => m.actif && m.role !== 'patron');
  if (!eq.length) return UI.toast('Ajoute d’abord un vendeur', 'err');
  const rows = eq.map((m) => `<button class="pickrow" data-action="pick-member" data-id="${m.id}">
      <span class="mrow__av">${UI.esc((m.nom || '?').slice(0, 2).toUpperCase())}</span>
      <div class="mrow__b"><strong>${UI.esc(m.nom)}</strong><small>${S.roleLabel(m.role)}</small></div>
      <span data-icon="chevron"></span></button>`).join('');
  UI.openModal(UI.modalShell('Passer la main',
    `${UI.zhelp('Choisis qui prend le téléphone. Il ne verra que ce que son rôle permet. Pour reprendre la main, ton code PIN sera demandé.')}
     <div class="picklist">${rows}</div>`,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>`));
  hydrateIcons($('#modal-root'));
}

// ---------- Abonnement & licences ----------
function contactNebula(extra) {
  const msg = extra || 'Bonjour NEBULA, j’utilise Boussole et j’aimerais des informations sur les licences.';
  window.open('https://wa.me/' + NEBULA_WHATSAPP + '?text=' + encodeURIComponent(msg), '_blank');
}
function openOffresModal() {
  UI.openModal(UI.modalShell('Choisis ton offre',
    `<p class="modal__lead">Débloque tout Boussole. Récupère une seule dette oubliée et l’abonnement est déjà remboursé.</p>
     ${UI.planCardsHTML(S.getLicence().plan)}
     <button class="btn btn--ghost" data-action="have-key"><span data-icon="key"></span> J’ai déjà une clé</button>`,
    `<button class="btn btn--ghost" data-action="close-modal">Fermer</button>`));
  hydrateIcons($('#modal-root'));
}
function openBuyModal(planKey) {
  const p = S.PLANS[planKey] || S.PLANS.essentiel;
  UI.openModal(UI.modalShell(`Souscrire — ${p.nom}`,
    `<p class="buybox__price"><strong>${S.formatNombre(p.prix)} F</strong> / mois</p>
     ${UI.zhelp('Paie par Mobile Money, puis renseigne l’ID de la transaction et ton nom. NEBULA valide et t’envoie ta clé (à usage unique) à activer ici.')}
     <p class="buystep">1. Envoie <strong>${S.formatNombre(p.prix)} F</strong> par Mobile Money au :</p>
     <div class="momo"><div><span class="momo__lbl">Numéro MoMo</span><strong>${NEBULA_MOMO.numero}</strong></div><div><span class="momo__lbl">Nom</span><strong>${UI.esc(NEBULA_MOMO.nom)}</strong></div></div>
     <p class="buystep">2. Renseigne ta transaction :</p>
     <div class="field"><label for="pay-txn">ID de la transaction MoMo</label><input id="pay-txn" class="input" placeholder="Ex. MP230715.1234.A56789" autocomplete="off"></div>
     <div class="field"><label for="pay-nom">Ton nom &amp; prénom</label><input id="pay-nom" class="input" placeholder="Ex. BIAO Mongazi" autocomplete="off"></div>`,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn plan__cta--pro" data-action="pay-submit" data-plan="${planKey}">J’ai payé — envoyer ma demande</button>`));
  hydrateIcons($('#modal-root'));
}
async function submitPayment(el) {
  const planKey = el.dataset.plan; const p = S.PLANS[planKey] || S.PLANS.essentiel;
  const txn = (($('#pay-txn') || {}).value || '').trim();
  const nom = (($('#pay-nom') || {}).value || '').trim();
  if (!txn || !nom) return UI.toast('Renseigne l’ID de transaction et ton nom', 'err');
  try { await Cloud.submitLicenceRequest({ plan: planKey, montant: p.prix, txn, nom, contact: S.getState().profil.tel_pro || '' }); } catch {}
  const msg = `Bonjour NEBULA, je viens de souscrire à Boussole ${p.nom} (${S.formatNombre(p.prix)} F/mois). J'ai payé par Mobile Money.\nID transaction : ${txn}\nNom : ${nom}\nJ'aimerais recevoir ma clé de licence.`;
  window.open('https://wa.me/' + NEBULA_WHATSAPP + '?text=' + encodeURIComponent(msg), '_blank');
  openActivateModal(true);
}
function openActivateModal(after) {
  UI.openModal(UI.modalShell('Activer ma licence',
    `${after ? '<p class="modal__lead">Demande envoyée ! Dès que NEBULA t’envoie ta clé sur WhatsApp, entre-la ici.</p>' : ''}
     ${UI.zhelp('Entre la clé (BSL-XXXX-XXXX) que NEBULA t’a envoyée. Elle ne fonctionne qu’une seule fois. Il faut internet pour l’activer.')}
     <div class="field"><label for="lic-key">Ta clé de licence</label>
       <input id="lic-key" class="input" placeholder="BSL-XXXX-XXXX" autocomplete="off" style="text-transform:uppercase"></div>`,
    `<button class="btn btn--ghost" data-action="close-modal">Fermer</button>
     <button class="btn" data-action="activate-key">Activer</button>`));
  hydrateIcons($('#modal-root'));
}
async function submitActivation() {
  const code = (($('#lic-key') || {}).value || '').trim().toUpperCase();
  if (!code) return UI.toast('Entre ta clé', 'err');
  const btn = $('[data-action="activate-key"]'); if (btn) { btn.disabled = true; btn.textContent = 'Vérification…'; }
  const reset = () => { if (btn) { btn.disabled = false; btn.textContent = 'Activer'; } };
  const res = await Cloud.consumeLicenceKey(code, S.getState().profil.proprietaire || '');
  if (res.offline) { reset(); return UI.toast('Connecte-toi à internet pour activer ta clé.', 'err'); }
  if (!res.ok) { reset(); return UI.toast(res.used ? 'Clé invalide ou déjà utilisée.' : 'Clé refusée.', 'err'); }
  const out = S.activateLicence(code, res.plan);
  if (!out.ok) { reset(); return UI.toast(out.msg, 'err'); }
  UI.closeModal(); render(); UI.toast('Licence activée. Merci !');
}
function openParrainage() {
  const msg = `Salut ! J'utilise Boussole pour gérer mon commerce (ventes, dépenses, dettes, bénéfices). Essaie gratuitement 30 jours. Si tu t'abonnes, on gagne chacun 1 mois offert.`;
  UI.openModal(UI.modalShell('Parrainer un commerçant',
    `${UI.zhelp('Invite un autre commerçant. S’il s’abonne, tu gagnes 1 mois offert (préviens NEBULA).')}
     <div class="momo"><span>${UI.esc(msg)}</span></div>`,
    `<button class="btn btn--ghost" data-action="close-modal">Fermer</button>
     <button class="btn" data-action="share-parrain" data-msg="${encodeURIComponent(msg)}"><span data-icon="whatsapp"></span> Partager</button>`));
  hydrateIcons($('#modal-root'));
}
// ---------- Back-office licences (admin) ----------
async function adminGenKey(plan, reqId) {
  try {
    const cle = await Cloud.adminCreateKey(plan || 'essentiel');
    if (reqId) await Cloud.adminSetRequestStatut(reqId, 'valide');
    await copyText(cle, `Clé ${cle} générée et copiée`);
    renderAdmin();
  } catch (e) { UI.toast('Génération impossible : ' + (e.message || ''), 'err'); }
}
async function adminReject(id) { await Cloud.adminSetRequestStatut(id, 'rejete'); renderAdmin(); UI.toast('Demande rejetée'); }
async function copyText(t, ok) { try { await navigator.clipboard.writeText(t); UI.toast(ok || 'Copié'); } catch { UI.toast(t); } }
async function tgSave() {
  const v = (($('#tg-chat') || {}).value || '').trim();
  try { await Cloud.adminSetConfig('tg_admin_chat', v); UI.toast('Telegram enregistré'); }
  catch (e) { UI.toast('Échec : ' + (e.message || ''), 'err'); }
}
async function tgTest() {
  try { const r = await Cloud.adminTestTelegram(); UI.toast(r === 'envoye' ? 'Test envoyé sur Telegram' : 'Configure d’abord ton chat id', r === 'envoye' ? 'ok' : 'err'); }
  catch (e) { UI.toast('Échec : ' + (e.message || ''), 'err'); }
}

const isConfigured = () => Boolean(S.getState().profil.nom_activite) || S.getProduits({ withArchived: true }).length > 0;

// ---------- Sécurité : session employé + droits ----------
let activeMember = null;   // null = patron ; sinon id du membre (session limitée)
function loadActiveMember() { try { return localStorage.getItem('boussole:active-member') || null; } catch { return null; } }
function setActiveMember(id) {
  activeMember = id || null;
  try { id ? localStorage.setItem('boussole:active-member', id) : localStorage.removeItem('boussole:active-member'); } catch {}
  const m = activeMember ? S.getMembre(activeMember) : null;
  S.setAuditAuthor(m ? m.nom : (S.getState().profil.proprietaire || 'Patron'));   // qui agit -> journal d'audit
}
function currentMembre() { return activeMember ? S.getMembre(activeMember) : null; }
function currentRole() { const m = currentMembre(); return m ? m.role : 'patron'; }
const SCREEN_PERM = { accueil: 'bilan', ventes: 'ventes', depenses: 'depenses', bilan: 'bilan', carnet: 'carnet', stock: 'stock', reglages: 'reglages' };
function can(perm) { return S.rolePerms(currentRole()).includes(perm); }
function screenAllowed(s) { return currentRole() === 'patron' || can(SCREEN_PERM[s] || 'ventes'); }
function allowedScreens() { return ['accueil', 'ventes', 'depenses', 'bilan', 'carnet', 'stock', 'reglages'].filter(screenAllowed); }
function defaultScreen() { const a = allowedScreens(); return a.includes('ventes') ? 'ventes' : (a[0] || 'ventes'); }

// ---------- Écran de verrouillage (clavier PIN) ----------
let pinMode = null, pinBuf = '', pinTmp = '';
function renderLock(mode) {
  pinMode = mode; pinBuf = ''; pinTmp = pinTmp || '';
  const root = $('#lock-root'); root.innerHTML = UI.pinLockHTML(mode); root.classList.add('is-open');
  hydrateIcons(root); updateLockDots();
}
function closeLock() { const r = $('#lock-root'); r.innerHTML = ''; r.classList.remove('is-open'); pinMode = null; pinBuf = ''; pinTmp = ''; }
function updateLockDots() { document.querySelectorAll('#lock-dots span').forEach((d, i) => d.classList.toggle('on', i < pinBuf.length)); }
function lockMsg(t, err) { const m = $('#lock-msg'); if (m) { m.textContent = t || ''; m.classList.toggle('is-err', !!err); } }
function shakeLock() { const d = $('#lock-dots'); if (d) { d.classList.remove('shake'); void d.offsetWidth; d.classList.add('shake'); } }
async function onLockKey(el) {
  const k = el.dataset.lock;
  if (k === 'del') { pinBuf = pinBuf.slice(0, -1); return updateLockDots(); }
  if (k === 'forgot') return openForgotPin();
  if (k === 'ok') return submitPin();
  if (/^\d$/.test(k) && pinBuf.length < 4) { pinBuf += k; lockMsg(''); updateLockDots(); if (pinBuf.length === 4) setTimeout(submitPin, 120); }
}
async function submitPin() {
  if (pinBuf.length < 4) return;
  const code = pinBuf;
  if (pinMode === 'set' || pinMode === 'change') { pinTmp = code; renderLock('confirm'); lockMsg('Retape le même code'); return; }
  if (pinMode === 'confirm') {
    if (code !== pinTmp) { pinBuf = ''; updateLockDots(); shakeLock(); return lockMsg('Les codes ne correspondent pas', true); }
    await Sec.setPin(pinTmp); pinTmp = ''; closeLock(); refreshReglages(); return UI.toast('Code PIN activé');
  }
  if (pinMode === 'owner') {
    if (await Sec.verifyOwner(code)) { setActiveMember(null); closeLock(); render(); return UI.toast('Tu as repris la main'); }
    pinBuf = ''; updateLockDots(); shakeLock(); return lockMsg('Code incorrect', true);
  }
  // mode 'open' : le code identifie le patron OU un vendeur
  const who = await resolveIdentity(code);
  if (!who) { pinBuf = ''; updateLockDots(); shakeLock(); return lockMsg('Code incorrect', true); }
  setActiveMember(who === 'owner' ? null : who);
  closeLock(); render();
}
async function resolveIdentity(code) {
  if (await Sec.verifyOwner(code)) return 'owner';
  for (const m of S.getEquipe()) { if (m.pin && await Sec.matchesRecord(code, m.pin)) return m.id; }
  return null;
}
function openForgotPin() {
  UI.confirmDialog({
    title: 'Code oublié ?', danger: true, okLabel: 'Effacer et repartir',
    message: 'Pour ta sécurité, le code ne peut pas être récupéré. Si tu as un compte cloud, connecte-toi sur un autre appareil pour retrouver tes données. Sinon, tu peux effacer l’appli et repartir à zéro (les données locales seront perdues).',
  }, () => { Sec.clearPin(); S.resetLocal(); setActiveMember(null); closeLock(); location.reload(); });
}

// ---------- Rendu ----------
function render() {
  // Back-office licences (réservé NEBULA — admin connecté uniquement)
  if (screen === 'admin') { if (Cloud.isAdmin()) return renderAdmin(); screen = 'accueil'; }
  // Blocage licence : essai terminé / licence expirée -> paywall plein écran
  const le = S.licenceEtat();
  if (le.bloque && !Cloud.isAdmin()) return renderPaywall(le.mode);
  // Session employé : forcer un écran autorisé par le rôle
  if (activeMember && !screenAllowed(screen)) screen = defaultScreen();
  const tb = $('#topbar');
  tb.style.display = (screen === 'welcome') ? 'none' : '';
  tb.innerHTML = UI.topbarHTML(cloudCtx(), effectiveTheme(), S.notifications().count);
  const view = $('#view');
  const prevScroll = view.scrollTop;
  if (screen === 'config') view.innerHTML = UI.viewConfigHTML(wizard || (wizard = { step: 1, charges: UI.defaultCharges() }));
  else if (screen === 'welcome') view.innerHTML = UI.viewWelcomeHTML();
  else if (screen === 'accueil') view.innerHTML = UI.viewAccueilHTML(period);
  else if (screen === 'depenses') view.innerHTML = UI.viewDepensesHTML(depFilter);
  else if (screen === 'bilan') view.innerHTML = UI.viewBilanHTML(rapGran);
  else if (screen === 'carnet') view.innerHTML = UI.viewCarnetHTML();
  else if (screen === 'stock') view.innerHTML = UI.viewStockHTML(stockFilter);
  else if (screen === 'reglages') view.innerHTML = UI.viewReglagesHTML(cloudCtx());
  else view.innerHTML = UI.viewVentesHTML(venteFilter);
  const chrome = navVisible();
  $('#nav').innerHTML = chrome ? UI.navHTML(screen) : '';
  $('#nav').style.display = chrome ? '' : 'none';
  $('#sidebar').innerHTML = chrome ? UI.sidebarHTML(screen, cloudCtx(), sidebarAcc) : '';
  $('#sidebar').style.display = chrome ? '' : 'none';
  $('#fab').innerHTML = chrome ? UI.fabHTML(fabOpen) : '';
  $('#fab').style.display = chrome ? '' : 'none';
  renderOverlay();
  hydrateIcons(document);
  if (screen === 'accueil' && animateNext) {
    const dash = view.querySelector('.view--dash'); if (dash) dash.classList.add('is-enter');
    animateCounts(view);
  }
  if (screen === 'accueil') wireCarousel();
  // Bandeaux : mode employé + fin d'essai
  const strip = (activeMember ? UI.empBannerHTML(currentMembre()) : UI.trialBannerHTML());
  if (strip && navVisible()) { view.insertAdjacentHTML('afterbegin', strip); hydrateIcons(view.firstElementChild); }
  if (activeMember) pruneChromeForMember();
  animateNext = false;
  view.scrollTop = resetScroll ? 0 : prevScroll;
  resetScroll = false;
}
function renderPaywall(mode) {
  $('#lock-root').innerHTML = ''; $('#lock-root').classList.remove('is-open');
  const tb = $('#topbar'); tb.style.display = 'none';
  const view = $('#view'); view.innerHTML = UI.paywallHTML(mode === 'expire' ? 'expire' : 'essai');
  ['#nav', '#sidebar', '#fab'].forEach((s) => { const el = $(s); el.innerHTML = ''; el.style.display = 'none'; });
  hydrateIcons(view); view.scrollTop = 0;
}
function renderAdmin() {
  const tb = $('#topbar'); tb.style.display = '';
  tb.innerHTML = UI.topbarHTML(cloudCtx(), effectiveTheme(), 0);
  ['#nav', '#sidebar', '#fab'].forEach((s) => { $(s).innerHTML = ''; $(s).style.display = 'none'; });
  const view = $('#view'); view.innerHTML = '<section class="view"><p class="lrow--empty">Chargement…</p></section>';
  Promise.all([Cloud.adminListRequests(), Cloud.adminListKeys(), Cloud.adminGetConfig('tg_admin_chat')]).then(([reqs, keys, tgChat]) => {
    view.innerHTML = UI.adminLicencesHTML(reqs, keys, tgChat); hydrateIcons(view);
  });
}
// Retire de la navigation les écrans interdits au vendeur en session.
function pruneChromeForMember() {
  const allowed = new Set(allowedScreens());
  document.querySelectorAll('#nav [data-screen], #sidebar [data-screen], #overlay-root [data-screen]').forEach((b) => { if (b.dataset.screen && !allowed.has(b.dataset.screen)) b.remove(); });
  if (!can('depenses')) document.querySelectorAll('[data-action="fab-depense"]').forEach((b) => b.remove());
}
function navVisible() { return screen !== 'config' && screen !== 'welcome'; }
// Chrome léger (sans toucher #view -> conserve le scroll)
function renderOverlay() {
  const root = $('#overlay-root');
  if (overlay === 'drawer') root.innerHTML = UI.drawerHTML(cloudCtx(), effectiveTheme());
  else if (overlay === 'notifs') root.innerHTML = UI.notifsHTML();
  else root.innerHTML = '';
  root.classList.toggle('is-open', !!overlay);
  hydrateIcons(root);
}
function renderFab() { $('#fab').innerHTML = navVisible() ? UI.fabHTML(fabOpen) : ''; hydrateIcons($('#fab')); }
function renderSidebar() { $('#sidebar').innerHTML = navVisible() ? UI.sidebarHTML(screen, cloudCtx(), sidebarAcc) : ''; hydrateIcons($('#sidebar')); }
function setOverlay(o) { overlay = o; if (o) { fabOpen = false; renderFab(); } renderOverlay(); }
function refreshStock() { if (screen !== 'stock') return; const v = $('#view'); const t = v.scrollTop; v.innerHTML = UI.viewStockHTML(stockFilter); hydrateIcons(v); v.scrollTop = t; }
function refreshCarnet() { if (screen !== 'carnet') return; const v = $('#view'); const t = v.scrollTop; v.innerHTML = UI.viewCarnetHTML(); hydrateIcons(v); v.scrollTop = t; }

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
function refreshDepenses() {
  if (screen !== 'depenses') return;
  const view = $('#view'); const top = view.scrollTop;
  view.innerHTML = UI.viewDepensesHTML(depFilter);
  hydrateIcons(view); view.scrollTop = top;
}
function refreshBilan() {
  if (screen !== 'bilan') return;
  const view = $('#view'); const top = view.scrollTop;
  view.innerHTML = UI.viewBilanHTML(rapGran);
  hydrateIcons(view); view.scrollTop = top;
}

// ---------- Exports (rapport PDF / Excel / WhatsApp) ----------
function downloadFile(name, text, mime) {
  const blob = new Blob(['﻿' + text], { type: mime + ';charset=utf-8' });
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
}
function rapportCSV(r) {
  const n = (x) => Math.round(Number(x) || 0);
  const L = [`Rapport;${r.label}`, `Généré le;${new Date().toLocaleDateString('fr-FR')}`, '', 'Indicateur;Montant'];
  L.push(`Chiffre d'affaires;${n(r.ca)}`, `Coût des produits vendus;${n(r.cout)}`, `Marge;${n(r.marge)}`,
    `Charges fixes (quote-part);${n(r.charges)}`, `Dépenses;${n(r.depenses)}`, `Bénéfice net;${n(r.benefice)}`,
    `Taux de marge (%);${Math.round((r.tauxMarge || 0) * 100)}`, `Nombre de ventes;${n(r.nbVentes)}`, `Unités vendues;${n(r.unites)}`, `Solde de caisse;${n(r.caisse)}`);
  if (r.depensesCat && r.depensesCat.length) { L.push('', 'Dépenses par catégorie;Montant'); r.depensesCat.forEach((c) => L.push(`${c.categorie};${n(c.total)}`)); }
  if (r.tops && r.tops.length) { L.push('', 'Meilleures ventes;CA;Part (%)'); r.tops.forEach((p) => L.push(`${p.nom};${n(p.revenu)};${Math.round(p.part * 100)}`)); }
  return L.join('\r\n');
}
function printRapport(r) {
  const nom = S.getState().profil.nom_activite || 'Mon activité';
  const line = (k, v, cls) => `<tr><td>${k}</td><td class="num ${cls || ''}">${S.formatF(v)}</td></tr>`;
  const cats = (r.depensesCat || []).map((c) => `<tr><td>${UI.esc(c.categorie)}</td><td class="num">${S.formatF(c.total)}</td></tr>`).join('');
  const tops = (r.tops || []).map((p) => `<tr><td>${UI.esc(p.nom)}</td><td class="num">${S.formatF(p.revenu)}</td><td class="num">${Math.round(p.part * 100)}%</td></tr>`).join('');
  document.getElementById('print-area').innerHTML = `
    <h1>Rapport — ${UI.esc(r.label)}</h1>
    <p class="p-sub">${UI.esc(nom)} · généré le ${new Date().toLocaleDateString('fr-FR')}</p>
    <table><tbody>${line("Chiffre d'affaires", r.ca)}${line('Coût des produits', r.cout)}${line('Marge', r.marge)}${line('Charges fixes', r.charges)}${line('Dépenses', r.depenses)}${line('Bénéfice net', r.benefice, r.benefice >= 0 ? 'pos' : 'neg')}${line('Solde de caisse', r.caisse)}</tbody></table>
    ${cats ? `<h2 style="font-size:15px;margin:18px 0 6px">Dépenses par catégorie</h2><table><tbody>${cats}</tbody></table>` : ''}
    ${tops ? `<h2 style="font-size:15px;margin:18px 0 6px">Meilleures ventes</h2><table><tbody>${tops}</tbody></table>` : ''}
    <p class="p-foot">Boussole — NEBULA Agency</p>`;
  window.print();
}
function shareRapport(r) {
  const nom = S.getState().profil.nom_activite || '';
  const t = `BOUSSOLE — Rapport ${r.label}\n${nom}\n\nVentes : ${S.formatF(r.ca)}\nDépenses : ${S.formatF(r.depenses)}\nBénéfice net : ${S.formatF(r.benefice)}\nCaisse : ${S.formatF(r.caisse)}\nNb ventes : ${r.nbVentes}`;
  window.open('https://wa.me/?text=' + encodeURIComponent(t), '_blank');
}

// ---------- Documents : factures & devis ----------
function frDate(ymd) { const m = String(ymd || '').match(/^(\d{4})-(\d{2})-(\d{2})/); return m ? `${m[3]}/${m[2]}/${m[1]}` : (ymd || ''); }
function docScope(target) {
  const modal = (target && target.closest) ? target.closest('.modal') : null;
  return (modal ? modal.querySelector('.modal__body') : $('#modal-root .modal__body')) || $('#modal-root');
}
function readDoc(scope) {
  const df = scope.querySelector('.docform') || scope;
  const val = (name) => { const el = df.querySelector(`[data-df="${name}"]`); return el ? el.value : ''; };
  const lignes = [...df.querySelectorAll('.dline')].map((r) => ({
    designation: (r.querySelector('[data-dl="designation"]').value || '').trim(),
    qte: r.querySelector('[data-dl="qte"]').value,
    pu: r.querySelector('[data-dl="pu"]').value,
  })).filter((l) => l.designation || Number(l.qte) || Number(l.pu));
  return {
    id: df.dataset.id || '', type: df.dataset.type || 'facture', numero: df.dataset.numero || '',
    date: val('date'), echeance: val('echeance'),
    client: { nom: val('nom'), tel: val('tel'), adresse: val('adresse') },
    lignes, remise: val('remise'), tva_taux: val('tva_taux'), acompte: val('acompte'), notes: val('notes'),
  };
}
function refreshDocTotals(sc) {
  const df = sc.querySelector('.docform') || sc;
  df.querySelectorAll('.dline').forEach((row) => {
    const q = Number(row.querySelector('[data-dl="qte"]').value) || 0;
    const pu = Number(row.querySelector('[data-dl="pu"]').value) || 0;
    const cell = row.querySelector('[data-dl-tot]'); if (cell) cell.textContent = S.formatF(q * pu);
  });
  const tot = df.querySelector('#dc-tot'); if (tot) tot.innerHTML = UI.docTotalsHTML(readDoc(sc));
}
function openDocEditor(id, type) {
  const t = type === 'devis' ? 'devis' : 'facture';
  const doc = id ? S.getDocument(id) : {
    type: t, numero: S.nextDocNumero(t), date: new Date().toISOString().slice(0, 10),
    client: {}, lignes: [], remise: '', tva_taux: '', acompte: '', notes: '',
  };
  if (!doc) return;
  UI.openModal(UI.modalShell(id ? (doc.type === 'devis' ? 'Devis' : 'Facture') : (t === 'devis' ? 'Nouveau devis' : 'Nouvelle facture'),
    UI.docFormFields(doc),
    `<button class="btn btn--ghost" data-action="close-modal">Fermer</button>
     <button class="btn" data-action="doc-save" data-id="${id || ''}">Enregistrer</button>`));
  hydrateIcons($('#modal-root'));
}
function saveDocFromForm(el) {
  const d = readDoc(docScope(el));
  if (!d.lignes.length) { UI.toast('Ajoute au moins un article', 'err'); return null; }
  return d.id ? S.updateDocument(d.id, d) : S.addDocument(d);
}
function printDoc(doc) { if (!doc) return; document.getElementById('print-area').innerHTML = UI.documentPrintHTML(doc); window.print(); }
function shareDocWA(doc) {
  if (!doc) return;
  const p = S.getState().profil, t = S.documentTotals(doc), isFac = doc.type === 'facture';
  const lignes = (doc.lignes || []).filter((l) => l.designation || l.qte || l.pu)
    .map((l) => `• ${l.designation || 'Article'} : ${S.formatNombre(l.qte || 0)} × ${S.formatF(l.pu || 0)} = ${S.formatF((Number(l.qte) || 0) * (Number(l.pu) || 0))}`).join('\n');
  const txt = `*${isFac ? 'FACTURE' : 'DEVIS'} ${doc.numero}*\n${p.nom_activite || ''}\n\n${isFac ? 'Facturé à' : 'Client'} : ${doc.client && doc.client.nom || '—'}\nDate : ${frDate(doc.date)}\n\n${lignes}\n${t.remise ? `\nRemise : − ${S.formatF(t.remise)}` : ''}${t.tva ? `\nTVA (${doc.tva_taux}%) : ${S.formatF(t.tva)}` : ''}\n*${isFac && t.acompte ? 'Net à payer' : 'Total'} : ${S.formatF(isFac ? t.net : t.total)}*${doc.notes ? `\n\n${doc.notes}` : ''}`;
  const tel = (doc.client && doc.client.tel || '').replace(/[^0-9]/g, '');
  window.open('https://wa.me/' + tel + '?text=' + encodeURIComponent(txt), '_blank');
}

// ---------- Chrome : FAB, vente rapide, stock, recherche globale ----------
function closeChrome() { if (fabOpen) { fabOpen = false; renderFab(); } if (overlay) { overlay = null; renderOverlay(); } }
// ---------- Caisse (panier POS) ----------
let cart = [];
let cartMode = 'especes';
let cartVendeur = '';
function openVenteModal() {
  const prods = S.getProduits();
  if (!prods.length) { UI.toast('Ajoute d\'abord un produit', 'err'); return setScreen('reglages'); }
  cart = []; cartMode = 'especes'; cartVendeur = '';
  UI.openModal(UI.modalShell('Caisse', UI.caisseHTML(cart, cartMode, cartVendeur),
    `<button class="btn btn--ghost" data-action="close-modal">Fermer</button>`));
  hydrateIcons($('#modal-root'));
}
function refreshCaisse() {
  const body = $('#modal-root .modal__body'); if (!body) return;
  const y = body.scrollTop;
  body.innerHTML = UI.caisseHTML(cart, cartMode, cartVendeur);
  hydrateIcons(body); body.scrollTop = y;
}
function openReceiptModal(ref) {
  const d = S.receiptByTicket(ref) || S.receiptData(ref); if (!d) return;
  UI.openModal(UI.modalShell('Reçu de caisse',
    `<p class="modal__lead">Encaissé <strong>${S.formatF(d.total)}</strong> · ${UI.esc(S.PAYMENT_LABELS[d.mode] || d.mode)}</p>
     ${UI.zhelp('Donne un reçu à ton client. Le ticket 58 mm est pour une imprimante de caisse ; le reçu A4 pour une imprimante normale ou un PDF ; WhatsApp envoie le détail par message.')}
     <div class="rcpt-actions">
       ${BT.supported() ? `<button class="btn" data-action="rcpt-bt" data-ref="${d.ref}"><span data-icon="bluetooth"></span> Imprimante Bluetooth</button>` : ''}
       <button class="btn ${BT.supported() ? 'btn--ghost' : ''}" data-action="rcpt-print" data-ref="${d.ref}" data-fmt="ticket"><span data-icon="print"></span> Ticket 58 mm</button>
       <button class="btn btn--ghost" data-action="rcpt-print" data-ref="${d.ref}" data-fmt="a4"><span data-icon="doc"></span> Reçu A4</button>
       <button class="btn btn--ghost" data-action="rcpt-wa" data-ref="${d.ref}"><span data-icon="whatsapp"></span> WhatsApp</button>
     </div>`,
    `<button class="btn btn--ghost" data-action="close-modal">Fermer</button>`));
  hydrateIcons($('#modal-root'));
}
function openVenteLibreModal() {
  UI.openModal(UI.modalShell('Montant libre / acompte',
    `${UI.zhelp('Facture un service ou un acompte de projet : entre le montant et une description. Pratique quand ce n’est pas dans ton catalogue.')}
     <div class="field"><label for="vl-amt">Montant</label><div class="inwrap"><input id="vl-amt" class="input input--lg" type="number" inputmode="numeric" placeholder="0"><span class="inwrap__cur">F</span></div></div>
     <div class="field"><label for="vl-desc">Description</label><input id="vl-desc" class="input" placeholder="Ex. Acompte site web, consultation…" autocomplete="off"></div>`,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn" data-action="vl-save"><span data-icon="check"></span> Encaisser</button>`));
  hydrateIcons($('#modal-root'));
}
function printReceipt(d, fmt) { document.getElementById('print-area').innerHTML = UI.receiptHTML(d, fmt); window.print(); }
function shareReceiptWA(d) {
  const nom = S.getState().profil.nom_activite || '';
  const lines = d.lignes.map((l) => `• ${l.nom} ${S.formatNombre(l.qte)}×${S.formatF(l.prix_unitaire)} = ${S.formatF((l.qte || 0) * (l.prix_unitaire || 0))}`).join('\n');
  const footer = S.renderTemplate(S.getWaTemplate('recu'), { commerce: nom, total: S.formatF(d.total), client: '' });
  const txt = `*REÇU — ${nom}*\n${new Date(d.date).toLocaleString('fr-FR')}\n\n${lines}\n\n*TOTAL : ${S.formatF(d.total)}*\nPayé en ${S.PAYMENT_LABELS[d.mode] || d.mode}${d.vendeur ? `\nVendeur : ${d.vendeur}` : ''}\n\n${footer}`;
  window.open('https://wa.me/?text=' + encodeURIComponent(txt), '_blank');
}

// ---------- Achats fournisseurs ----------
function achatScope() { return $('#modal-root .modal__body'); }
function newAchatLine() { return { produit_id: (S.getProduits()[0] || {}).id || '', qte: 1, cout_unitaire: '' }; }
function readAchat(scope) {
  const f = scope.querySelector('.achatform') || scope;
  const lignes = [...f.querySelectorAll('.aline')].map((r) => ({
    produit_id: r.querySelector('[data-al="produit_id"]').value,
    qte: r.querySelector('[data-al="qte"]').value,
    cout_unitaire: r.querySelector('[data-al="cout_unitaire"]').value,
  })).filter((l) => l.produit_id && Number(l.qte) > 0);
  return {
    fournisseur: (f.querySelector('#ac-four') ? f.querySelector('#ac-four').value : '').trim(),
    date: f.querySelector('#ac-date') ? f.querySelector('#ac-date').value : '',
    statut: f.dataset.statut || 'paye',
    note: f.querySelector('#ac-note') ? f.querySelector('#ac-note').value : '',
    lignes,
  };
}
function refreshAchatTotals(sc) {
  const f = sc.querySelector('.achatform') || sc;
  f.querySelectorAll('.aline').forEach((r) => {
    const q = Number(r.querySelector('[data-al="qte"]').value) || 0;
    const c = Number(r.querySelector('[data-al="cout_unitaire"]').value) || 0;
    const cell = r.querySelector('[data-al-tot]'); if (cell) cell.textContent = S.formatF(q * c);
  });
  const tot = f.querySelector('#ac-tot'); if (tot) tot.innerHTML = UI.achatTotalsHTML(readAchat(sc).lignes);
}
function openAchatModal() {
  if (!S.getProduits().length) { UI.toast('Ajoute d\'abord un produit', 'err'); return setScreen('reglages'); }
  const a = { statut: 'paye', date: new Date().toISOString().slice(0, 10), lignes: [] };
  UI.openModal(UI.modalShell('Nouvel achat', UI.achatFormFields(a),
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn" data-action="save-achat">Enregistrer</button>`));
  hydrateIcons($('#modal-root'));
}
function openAchatView(id) {
  const a = S.getAchat(id); if (!a) return;
  const lignes = (a.lignes || []).map((l) => { const p = S.getProduit(l.produit_id); return `<div class="aview__row"><span class="aview__nom">${UI.esc(p ? p.nom : 'Produit')}</span><span class="aview__q">${S.formatNombre(l.qte)} × ${S.formatF(l.cout_unitaire)}</span><span class="aview__m">${S.formatF((Number(l.qte) || 0) * (Number(l.cout_unitaire) || 0))}</span></div>`; }).join('');
  const statutChips = S.ACHAT_STATUTS.map((st) => `<button class="modechip ${a.statut === st ? 'is-on' : ''}" data-action="ac-set-statut" data-id="${id}" data-st="${st}">${st === 'paye' ? 'Payé' : 'À crédit'}</button>`).join('');
  UI.openModal(UI.modalShell(a.fournisseur || 'Achat',
    `<p class="modal__lead">${UI.esc(a.date)} · Total <strong>${S.formatF(S.achatTotal(a))}</strong></p>
     <div class="aview">${lignes}</div>
     <div class="field"><label>Paiement</label><div class="modechips">${statutChips}</div></div>
     ${a.note ? `<p class="modal__note">${UI.esc(a.note)}</p>` : ''}
     <button class="btn btn--danger-ghost btn--sm" data-action="del-achat" data-id="${id}"><span data-icon="trash"></span> Supprimer cet achat</button>`,
    `<button class="btn btn--ghost" data-action="close-modal">Fermer</button>`));
  hydrateIcons($('#modal-root'));
}
function openStockModal(id) {
  const p = S.getProduit(id); if (!p) return;
  const s = S.getStockInfo(p);
  UI.openModal(UI.modalShell('Stock — ' + p.nom,
    `<div class="grid2">
       <div class="field"><label for="st-qte">Quantité en stock</label><input id="st-qte" class="input" type="number" inputmode="numeric" value="${s.suivi ? s.qte : ''}" placeholder="ex. 24"></div>
       <div class="field"><label for="st-seuil">Seuil d'alerte</label><input id="st-seuil" class="input" type="number" inputmode="numeric" value="${s.seuil || ''}" placeholder="ex. 5"></div>
     </div>
     <p class="modal__note">Tu es prévenu quand la quantité passe sous le seuil. Laisse la quantité vide pour ne plus suivre ce produit.</p>`,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn" data-action="save-stock" data-id="${id}">Enregistrer</button>`));
  hydrateIcons($('#modal-root'));
}
function doGlobalSearch(q) {
  const box = $('#gsearch-res'); if (!box) return;
  q = (q || '').trim().toLowerCase();
  if (!q) { box.innerHTML = ''; box.classList.remove('is-open'); return; }
  const res = [];
  S.getProduits().forEach((p) => { if (p.nom.toLowerCase().includes(q)) res.push({ ic: 'box', t: p.nom, s: 'Produit', screen: 'stock' }); });
  S.getClients().forEach((c) => { if (c.nom.toLowerCase().includes(q) || (c.tel || '').includes(q)) res.push({ ic: 'user', t: c.nom, s: c.dette > 0 ? `doit ${S.formatF(c.dette)}` : 'Client', screen: 'carnet' }); });
  S.getDocuments().forEach((d) => { if ((d.numero || '').toLowerCase().includes(q) || (d.client && d.client.nom || '').toLowerCase().includes(q)) res.push({ ic: 'receipt', t: d.numero, s: (d.client && d.client.nom) || d.type, screen: 'bilan' }); });
  const rows = res.slice(0, 8).map((r) => `<button class="gsr" data-action="gsearch-go" data-screen="${r.screen}"><span class="gsr__ic" data-icon="${r.ic}"></span><span class="gsr__t">${UI.esc(r.t)}</span><span class="gsr__s">${UI.esc(r.s)}</span></button>`).join('');
  box.innerHTML = rows || `<div class="gsr gsr--empty">Aucun résultat</div>`;
  box.classList.add('is-open');
  hydrateIcons(box);
}

// ---------- Objectifs multiples ----------
const OBJ_ICONS = [['target', 'Objectif'], ['home', 'Maison'], ['truck', 'Véhicule'], ['box', 'Matériel'], ['book', 'Études'], ['trophy', 'Projet'], ['wallet', 'Épargne'], ['flame', 'Rêve']];
function openGoalModal(id) {
  const o = id ? S.getObjectif2(id) : { icone: 'target', titre: '', montant_cible: '', echeance: '', note: '' };
  if (!o) return;
  const cur = S.getDevise();
  const picker = OBJ_ICONS.map(([ic, lbl]) => `<button type="button" class="objic ${(o.icone || 'target') === ic ? 'is-on' : ''}" data-action="obj-icone" data-ic="${ic}" title="${lbl}" aria-label="${lbl}"><span data-icon="${ic}"></span></button>`).join('');
  const body = `
    <div class="field"><label for="ob-titre">Objectif</label><input id="ob-titre" class="input" value="${UI.esc(o.titre || '')}" placeholder="Ex. Acheter une machine à coudre" autocomplete="off"></div>
    <div class="objics" role="group" aria-label="Icône de l'objectif">${picker}</div>
    <div class="grid2">
      <div class="field"><label for="ob-cible">Montant à atteindre</label><div class="inwrap"><input id="ob-cible" class="input" type="number" inputmode="numeric" value="${o.montant_cible || ''}" placeholder="0"><span class="inwrap__cur">${UI.esc(cur)}</span></div></div>
      <div class="field"><label for="ob-ech">Échéance <span class="opt">(option)</span></label><input id="ob-ech" class="input" type="date" value="${UI.esc(o.echeance || '')}"></div>
    </div>
    ${id ? `<div class="field"><label for="ob-actuel">Déjà mis de côté</label><div class="inwrap"><input id="ob-actuel" class="input" type="number" inputmode="numeric" value="${o.montant_actuel || ''}" placeholder="0"><span class="inwrap__cur">${UI.esc(cur)}</span></div></div>` : ''}
    <div class="field"><label for="ob-note">Note <span class="opt">(option)</span></label><textarea id="ob-note" class="input" rows="2" placeholder="Pourquoi ce projet, comment l'atteindre…">${UI.esc(o.note || '')}</textarea></div>
    ${id ? `<button class="btn btn--danger-ghost btn--sm" data-action="del-objectif" data-id="${id}"><span data-icon="trash"></span> Supprimer cet objectif</button>` : ''}`;
  UI.openModal(UI.modalShell(id ? "Modifier l'objectif" : 'Nouvel objectif', body,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn" data-action="save-objectif" data-id="${id || ''}">Enregistrer</button>`));
  hydrateIcons($('#modal-root'));
}
function openContribModal(id) {
  const o = S.getObjectif2(id); if (!o) return;
  const i = S.objectifInfo(o); const cur = S.getDevise();
  UI.openModal(UI.modalShell('Ajouter à « ' + (o.titre || 'objectif') + ' »',
    `<p class="modal__lead">${S.formatF(i.actuel)} / ${S.formatF(i.cible)} · reste <strong>${S.formatF(i.reste)}</strong></p>
     <div class="field"><label for="ob-add">Montant à ajouter</label><div class="inwrap"><input id="ob-add" class="input input--lg" type="number" inputmode="numeric" placeholder="0"><span class="inwrap__cur">${UI.esc(cur)}</span></div></div>`,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn" data-action="obj-add-montant" data-id="${id}">Ajouter</button>`));
  hydrateIcons($('#modal-root'));
}
// Rafraîchit uniquement le tableau de bord en conservant la position de défilement.
function refreshDash() {
  const view = $('#view');
  const top = view.scrollTop;
  view.innerHTML = UI.viewAccueilHTML(period);
  const dash = view.querySelector('.view--dash'); if (dash) dash.classList.add('is-enter');
  hydrateIcons(view);
  animateCounts(view);
  wireCarousel();
  view.scrollTop = top;
}
// Carrousel KPI : synchronise les points au défilement horizontal.
function wireCarousel() {
  const track = $('#kpicar-track'); if (!track) return;
  const dots = [...document.querySelectorAll('.kpicar__dot')]; if (!dots.length) return;
  let raf = 0;
  const update = () => {
    const first = track.firstElementChild;
    const w = first ? first.getBoundingClientRect().width + 10 : track.clientWidth || 1;
    const i = Math.max(0, Math.min(dots.length - 1, Math.round(track.scrollLeft / w)));
    dots.forEach((d, k) => d.classList.toggle('is-on', k === i));
  };
  track.addEventListener('scroll', () => { if (raf) return; raf = requestAnimationFrame(() => { raf = 0; update(); }); }, { passive: true });
  update();
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
  if (activeMember && !screenAllowed(s)) { UI.toast('Accès réservé au patron', 'err'); return; }
  if (s === 'accueil') animateNext = true;
  screen = s; if (s !== 'config') wizard = null;
  overlay = null; fabOpen = false; sidebarAcc = null; resetScroll = true;
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
    modele: scope.querySelector('.seg__b.is-on[data-modele]')?.dataset.modele || (S.isDigital() ? 'revente' : 'transformation'),
    tarif_type: scope.querySelector('.seg__b.is-on[data-tarif]')?.dataset.tarif || 'fixe',
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
  const cats = S.depenseCats().map((c, i) => `<button type="button" class="catchip ${i === 0 ? 'is-on' : ''}" data-action="dep-cat" data-cat="${UI.esc(c)}">${UI.esc(c)}</button>`).join('');
  const today = new Date().toISOString().slice(0, 10);
  const dig = S.isDigital();
  UI.openModal(UI.modalShell('Ajouter une dépense',
    `<div class="field"><label for="dp-amt">Montant</label>
       <div class="inwrap"><input id="dp-amt" class="input input--lg" type="number" inputmode="numeric" placeholder="0"><span class="inwrap__cur">F</span></div></div>
     <div class="field"><label>Catégorie</label><div class="catchips" id="dp-cats">${cats}</div></div>
     <div class="field"><label for="dp-lib">Libellé (optionnel)</label>
       <input id="dp-lib" class="input" placeholder="${dig ? 'Ex. Abonnement Supabase, GitHub, Canva' : 'Ex. Taxi marché, sacs, facture SBEE'}"></div>
     <label class="switchrow"><input type="checkbox" id="dp-rec" data-action="dep-rec"> Dépense récurrente (abonnement / outil)</label>
     <div class="field" id="dp-freq-wrap" style="display:none"><label for="dp-freq">Fréquence</label>
       <select id="dp-freq" class="input"><option value="mensuel">Chaque mois</option><option value="annuel">Chaque année</option></select>
       <p class="fieldhint">Compté automatiquement dans tes coûts fixes mensuels.</p></div>
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

// ---------- Assistant (chat déterministe local) ----------
function scrollChatBottom() { const b = $('#as-msgs'); if (b) b.scrollTop = b.scrollHeight; }
function openAssistant() {
  if (!chat.length) chat.push({ role: 'bot', text: 'Bonjour ! Pose-moi une question sur ton commerce, ou touche une suggestion ci-dessous.' });
  UI.openModal(UI.assistantHTML(chat));
  hydrateIcons($('#modal-root'));
  scrollChatBottom();
  const inp = $('#as-input'); if (inp) setTimeout(() => inp.focus(), 60);
}
function assistantAsk(question) {
  const qq = (question || '').trim(); if (!qq) return;
  chat.push({ role: 'user', text: qq });
  chat.push({ role: 'bot', text: S.assistantRepondre(qq) });
  const b = $('#as-msgs');
  if (b) { b.innerHTML = UI.assistantMsgsHTML(chat); hydrateIcons(b); scrollChatBottom(); }
  const inp = $('#as-input'); if (inp) { inp.value = ''; inp.focus(); }
}

// ---------- Crédits (clients à crédit) ----------
function creditRow(c) {
  return `<li class="crdrow ${c.paye ? 'is-paid' : ''}">
    <div class="crdrow__id"><strong>${UI.esc(c.client || 'Client')}</strong><small>${S.formatF(c.montant)}${c.echeance ? ` · échéance ${UI.esc(c.echeance)}` : ''}${c.paye ? ' · payé' : ''}</small></div>
    <div class="crdrow__acts">
      ${!c.paye && c.tel ? `<button class="crd-btn crd-btn--wa" data-action="credit-remind" data-id="${c.id}" title="Rappel WhatsApp" aria-label="Rappel WhatsApp"><span data-icon="whatsapp"></span></button>` : ''}
      <button class="crd-btn ${c.paye ? 'is-on' : ''}" data-action="credit-paid" data-id="${c.id}" title="${c.paye ? 'Marquer non payé' : 'Marquer payé'}" aria-label="Marquer payé"><span data-icon="check"></span></button>
      <button class="crd-btn crd-btn--del" data-action="del-credit" data-id="${c.id}" title="Supprimer" aria-label="Supprimer"><span data-icon="trash"></span></button>
    </div></li>`;
}
function openCreditsModal() {
  const cs = S.creditsSummary();
  const list = S.getCredits().slice().sort((a, b) => Number(a.paye) - Number(b.paye) || new Date(b.date) - new Date(a.date));
  const rows = list.length ? list.map(creditRow).join('') : '<li class="crd-empty">Aucun crédit enregistré pour l’instant.</li>';
  UI.openModal(UI.modalShell('Crédits — clients',
    `<p class="modal__lead">On te doit <strong>${S.formatF(cs.total)}</strong>${cs.nb ? ` (${cs.nb} en attente)` : ''}.</p>
     <ul class="crdlist">${rows}</ul>`,
    `<button class="btn btn--ghost" data-action="close-modal">Fermer</button>
     <button class="btn" data-action="add-credit"><span data-icon="plus"></span> Nouveau crédit</button>`));
  hydrateIcons($('#modal-root'));
}
function openAddCreditModal() {
  UI.openModal(UI.modalShell('Nouveau crédit',
    `<div class="field"><label for="cr-client">Client</label><input id="cr-client" class="input" placeholder="Nom du client" autocomplete="off"></div>
     <div class="grid2">
       <div class="field"><label for="cr-montant">Montant dû</label><div class="inwrap"><input id="cr-montant" class="input" type="number" inputmode="numeric" placeholder="0"><span class="inwrap__cur">F</span></div></div>
       <div class="field"><label for="cr-echeance">Échéance</label><input id="cr-echeance" class="input" type="date"></div>
     </div>
     <div class="field"><label for="cr-tel">WhatsApp (pour le rappel)</label><input id="cr-tel" class="input" type="tel" inputmode="tel" placeholder="Ex. 22997000000"></div>`,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn" data-action="save-credit">Enregistrer</button>`));
  hydrateIcons($('#modal-root'));
}
function openVersementModal(id) {
  const c = S.getCredit(id); if (!c) return;
  const reste = S.creditReste(c); const cur = S.getDevise();
  UI.openModal(UI.modalShell('Encaisser un versement',
    `<p class="modal__lead">${UI.esc(c.client || 'Client')} · reste dû <strong>${S.formatF(reste)}</strong></p>
     ${UI.zhelp('Note un paiement partiel reçu du client. Le reste dû se met à jour ; quand il tombe à zéro, la dette est soldée automatiquement.')}
     <div class="field"><label for="vr-montant">Montant reçu</label><div class="inwrap"><input id="vr-montant" class="input input--lg" type="number" inputmode="numeric" placeholder="0"><span class="inwrap__cur">${UI.esc(cur)}</span></div></div>`,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn" data-action="save-versement" data-id="${id}">Encaisser</button>`));
  hydrateIcons($('#modal-root'));
}
function openCreditDetail(id) {
  const c = S.getCredit(id); if (!c) return;
  const reste = S.creditReste(c);
  const pays = (c.paiements || []).slice().reverse().map((p) => `<div class="pay-row"><span>${new Date(p.date).toLocaleDateString('fr-FR')}</span><span class="pay-row__m">+ ${S.formatF(p.montant)}</span></div>`).join('') || '<p class="modal__note">Aucun versement pour l\'instant.</p>';
  UI.openModal(UI.modalShell('Dette — ' + (c.client || 'Client'),
    `<div class="crd-recap"><div><span class="crd-recap__lbl">Montant</span><span>${S.formatF(c.montant)}</span></div><div><span class="crd-recap__lbl">Reste dû</span><span class="${reste > 0 ? 'neg' : 'pos'}">${S.formatF(reste)}</span></div></div>
     ${c.echeance ? `<p class="modal__note">Échéance : ${UI.esc(c.echeance)}</p>` : ''}${c.note ? `<p class="modal__note">${UI.esc(c.note)}</p>` : ''}
     <div class="docform__sec">Historique des paiements</div>
     <div class="pay-list">${pays}</div>
     <div class="crd-detail-acts">
       ${reste > 0 ? `<button class="btn" data-action="credit-versement" data-id="${id}"><span data-icon="coins"></span> Versement</button>
       <button class="btn btn--ghost" data-action="credit-solde" data-id="${id}">Solder (${S.formatF(reste)})</button>` : '<p class="crd-solde-ok"><span data-icon="check"></span> Dette soldée</p>'}
     </div>
     <button class="btn btn--danger-ghost btn--sm" data-action="del-credit" data-id="${id}"><span data-icon="trash"></span> Supprimer</button>`,
    `<button class="btn btn--ghost" data-action="close-modal">Fermer</button>`));
  hydrateIcons($('#modal-root'));
}
function openClientFiche(key) {
  const c = S.clientByKey(key); if (!c) return;
  const creds = S.clientCredits(key), docs = S.clientDocuments(key);
  const tel = (c.tel || '').replace(/[^0-9]/g, '');
  const credRows = creds.map((cr) => { const r = S.creditReste(cr); return `<div class="fiche-row"><span>${cr.date ? new Date(cr.date).toLocaleDateString('fr-FR') : ''} · crédit</span><span class="${r > 0 ? 'neg' : 'pos'}">${r > 0 ? S.formatF(r) + ' dû' : 'soldé'}</span></div>`; }).join('');
  const docRows = docs.map((d) => `<div class="fiche-row"><span>${UI.esc(d.numero)} · ${d.type}</span><span>${S.formatF(d.total)}</span></div>`).join('');
  UI.openModal(UI.modalShell(c.nom || 'Client',
    `${(c.tel || c.adresse) ? `<p class="modal__lead">${[UI.esc(c.tel), UI.esc(c.adresse)].filter(Boolean).join(' · ')}</p>` : ''}
     ${UI.zhelp('La fiche de ce client : ce qu’il te doit, ses crédits, et son historique d’achat (factures/devis). « Modifier » pour ses coordonnées et une note.')}
     <div class="crd-recap"><div><span class="crd-recap__lbl">Reste dû</span><span class="${c.dette > 0 ? 'neg' : 'pos'}">${S.formatF(c.dette)}</span></div><div><span class="crd-recap__lbl">Achats</span><span>${S.formatNombre(docs.length)}</span></div></div>
     ${c.note ? `<p class="modal__note">${UI.esc(c.note)}</p>` : ''}
     ${creds.length ? `<div class="docform__sec">Crédits</div><div class="fiche-list">${credRows}</div>` : ''}
     ${docs.length ? `<div class="docform__sec">Historique d'achat</div><div class="fiche-list">${docRows}</div>` : ''}
     <div class="crd-detail-acts">
       ${tel ? `<a class="btn btn--doc" href="https://wa.me/${tel}?text=${encodeURIComponent(S.renderTemplate(S.getWaTemplate('remerciement'), { client: c.nom || '', commerce: S.getState().profil.nom_activite || '' }))}" target="_blank" rel="noopener"><span data-icon="whatsapp"></span> WhatsApp</a>` : ''}
       <button class="btn btn--ghost" data-action="client-edit" data-key="${UI.esc(key)}" data-id="${c.id || ''}"><span data-icon="edit"></span> Modifier</button>
     </div>`,
    `<button class="btn btn--ghost" data-action="close-modal">Fermer</button>`));
  hydrateIcons($('#modal-root'));
}
function openClientModal(id, prefill) {
  const c = id ? S.getClientEntry(id) : (prefill || { nom: '', tel: '', adresse: '', note: '' });
  if (id && !c) return;
  UI.openModal(UI.modalShell(id ? 'Modifier le client' : 'Nouveau client',
    `<div class="field"><label for="cl-nom">Nom</label><input id="cl-nom" class="input" value="${UI.esc(c.nom || '')}" placeholder="Nom du client" autocomplete="off"></div>
     <div class="grid2">
       <div class="field"><label for="cl-tel">Téléphone / WhatsApp</label><input id="cl-tel" class="input" type="tel" inputmode="tel" value="${UI.esc(c.tel || '')}" placeholder="Ex. 22997000000"></div>
       <div class="field"><label for="cl-adr">Adresse <span class="opt">(option)</span></label><input id="cl-adr" class="input" value="${UI.esc(c.adresse || '')}" placeholder="Ville / quartier"></div>
     </div>
     <div class="field"><label for="cl-note">Note <span class="opt">(option)</span></label><textarea id="cl-note" class="input" rows="2" placeholder="Préférences, remarques…">${UI.esc(c.note || '')}</textarea></div>
     ${id ? `<button class="btn btn--danger-ghost btn--sm" data-action="del-client" data-id="${id}"><span data-icon="trash"></span> Retirer de l'annuaire</button>` : ''}`,
    `<button class="btn btn--ghost" data-action="close-modal">Annuler</button>
     <button class="btn" data-action="save-client" data-id="${id || ''}">Enregistrer</button>`));
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
// Clavier de l'écran de verrouillage (PIN)
document.addEventListener('click', (e) => {
  const k = e.target.closest('[data-lock]');
  if (k) { e.preventDefault(); onLockKey(k); }
});

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

    // Personnalisation (apparence)
    case 'set-accent': setPref('accent', el.dataset.v); return refreshReglages();
    case 'set-textsize': setPref('textsize', el.dataset.v); return refreshReglages();
    case 'set-density': setPref('density', el.dataset.v); return refreshReglages();
    case 'set-corners': setPref('corners', el.dataset.v); return refreshReglages();
    case 'set-theme': { const t = el.dataset.v === 'light' ? 'light' : 'dark'; document.documentElement.dataset.theme = t; try { localStorage.setItem('boussole:theme', t); } catch {} applyThemeMeta(); return refreshReglages(); }

    // Messages WhatsApp configurables
    case 'watpl-reset': S.resetWaTemplate(el.dataset.key); refreshReglages(); return UI.toast('Message réinitialisé');
    case 'watpl-var': { const ta = document.getElementById('watpl-' + el.dataset.key); if (ta) insertAtCursor(ta, '{' + el.dataset.var + '}'); return; }

    // Imprimante Bluetooth
    case 'bt-connect': BT.connect().then((n) => { UI.toast('Imprimante connectée : ' + n); refreshReglages(); }).catch((e) => UI.toast(btErr(e), 'err')); return;
    case 'bt-test': BT.printTest(S.getState().profil.nom_activite, deviseSym()).then(() => UI.toast('Test envoyé à l’imprimante')).catch((e) => UI.toast(btErr(e), 'err')); return;
    case 'bt-forget': BT.forget(); refreshReglages(); return UI.toast('Imprimante oubliée');
    case 'rcpt-bt': { const d = S.receiptByTicket(el.dataset.ref) || S.receiptData(el.dataset.ref); if (d) printReceiptBT(d); return; }

    // Langue
    case 'set-lang': I18n.setLang(el.dataset.code); render(); I18n.applyLang(); return UI.toast('Langue : ' + I18n.langLabel(el.dataset.code));
    case 'lang-add': return openLangAdd();
    case 'lang-edit': return openLangEditor(el.dataset.code);
    case 'lang-del': { const c = el.dataset.code; I18n.removeCustomLang(c); UI.closeModal(); render(); I18n.applyLang(); return UI.toast('Langue supprimée'); }

    // Compte & sécurité
    case 'change-pwd': return openChangePwd();
    case 'pin-set': return renderLock('set');
    case 'pin-change': return renderLock('change');
    case 'pin-off': return UI.confirmDialog({ title: 'Désactiver le code', message: 'L’appli s’ouvrira sans code. Continuer ?', okLabel: 'Désactiver', danger: true }, () => { Sec.clearPin(); refreshReglages(); UI.toast('Code PIN désactivé'); });
    case 'lock-now': return renderLock('open');
    case 'membre-add': return openMembreModal(null);
    case 'membre-edit': return openMembreModal(el.dataset.id);
    case 'hand-over': return openHandOver();
    case 'reprendre': return Sec.hasPin() ? renderLock('owner') : (setActiveMember(null), render(), UI.toast('Tu as repris la main'));

    // Abonnement & licences
    case 'go-offres': return openOffresModal();
    case 'buy-plan': return openBuyModal(el.dataset.plan);
    case 'have-key': return openActivateModal();
    case 'contact-nebula': return contactNebula();
    case 'parrainage': return openParrainage();
    case 'pay-submit': return submitPayment(el);
    case 'activate-key': return submitActivation();

    case 'save-pwd': return savePwd();
    case 'membre-save': return membreSave(el.dataset.id);
    case 'membre-del': return UI.confirmDialog({ title: 'Supprimer le membre', message: 'Retirer ce membre de l’équipe ?', danger: true, okLabel: 'Supprimer' }, () => { S.removeMembre(el.dataset.id); UI.closeModal(); refreshReglages(); UI.toast('Membre retiré'); });
    case 'pick-member': setActiveMember(el.dataset.id); UI.closeModal(); render(); return UI.toast('Mode employé activé');
    case 'share-parrain': return window.open('https://wa.me/?text=' + el.dataset.msg, '_blank');

    // Fonctions Pro : multi-boutiques + relances
    case 'switch-boutique': { S.switchBoutique(el.dataset.id); screen = 'accueil'; resetScroll = true; render(); return UI.toast('Boutique : ' + ((S.getBoutiques().find((b) => b.id === el.dataset.id) || {}).nom || '')); }
    case 'add-boutique': { const v = (($('#rg-bout') || {}).value || '').trim(); if (!v) return UI.toast('Donne un nom', 'err'); S.addBoutique(v); refreshReglages(); return UI.toast('Boutique ajoutée'); }
    case 'del-boutique': return UI.confirmDialog({ title: 'Supprimer la boutique', message: 'Ses données sur cet appareil seront effacées. Continuer ?', danger: true, okLabel: 'Supprimer' }, () => { S.deleteBoutique(el.dataset.id); refreshReglages(); UI.toast('Boutique supprimée'); });
    case 'relance-wa': { const c = S.getCredits().find((x) => x.id === el.dataset.id); if (c && c.tel) window.open('https://wa.me/' + c.tel.replace(/[^0-9]/g, '') + '?text=' + encodeURIComponent(S.messageRelance(c)), '_blank'); return; }

    // Back-office licences (admin)
    case 'admin-genkey': return adminGenKey(el.dataset.plan, el.dataset.id);
    case 'admin-reject': return adminReject(el.dataset.id);
    case 'admin-copykey': return copyText(el.dataset.cle, 'Clé copiée');
    case 'tg-save': return tgSave();
    case 'tg-test': return tgTest();

    // tableau de bord — période & objectif
    case 'set-gran': if (period.gran !== el.dataset.gran) { period.gran = el.dataset.gran; period.offset = 0; savePeriod(); refreshDash(); } return;
    case 'period-prev': period.offset -= 1; return refreshDash();
    case 'period-next': if (period.offset < 0) { period.offset += 1; refreshDash(); } return;
    case 'edit-objectif': return openObjectifModal();
    case 'save-objectif': { const v = Number($('#obj-amt').value) || 0; S.setObjectif(v); UI.closeModal(); UI.toast(v > 0 ? 'Objectif enregistré' : 'Objectif retiré'); return; }

    // dépenses & caisse
    case 'add-depense': return openDepenseModal();
    case 'dep-cat': { const box = $('#dp-cats'); if (box) box.querySelectorAll('.catchip').forEach((c) => c.classList.toggle('is-on', c === el)); return; }
    case 'dep-rec': { const w = $('#dp-freq-wrap'); if (w) w.style.display = el.checked ? '' : 'none'; return; }
    case 'save-depense': {
      const amt = Number($('#dp-amt').value) || 0;
      if (amt <= 0) return UI.toast('Entre un montant', 'err');
      const on = $('#modal-root .catchip.is-on');
      const cat = on ? on.dataset.cat : 'Divers';
      const lib = ($('#dp-lib').value || '').trim();
      const d = $('#dp-date').value;
      const rec = $('#dp-rec') && $('#dp-rec').checked;
      const freq = ($('#dp-freq') || {}).value || 'mensuel';
      S.addDepense({ libelle: lib, categorie: cat, montant: amt, date: d ? new Date(d).toISOString() : undefined, recurrent: rec, frequence: freq });
      UI.closeModal(); UI.toast(rec ? 'Abonnement enregistré' : 'Dépense enregistrée'); return;
    }
    case 'del-depense': { S.deleteDepense(id); const row = el.closest('.deprow'); if (row) row.remove(); UI.toast('Dépense supprimée'); return; }
    case 'edit-caisse': return openCaisseModal();
    case 'save-caisse': { const v = Number($('#cs-amt').value) || 0; S.setSoldeInitial(v); UI.closeModal(); UI.toast('Fond de caisse enregistré'); return; }

    // assistant
    case 'open-assistant': return openAssistant();
    case 'assistant-ask': return assistantAsk(el.dataset.q);
    case 'assistant-send': return assistantAsk($('#as-input') ? $('#as-input').value : '');

    // crédits clients (gérés sur l'écran Carnet — re-rendu réactif via subscribe)
    case 'open-credits': return setScreen('carnet');
    case 'add-credit': return openAddCreditModal();
    case 'save-credit': {
      const client = ($('#cr-client').value || '').trim();
      const montant = Number($('#cr-montant').value) || 0;
      if (montant <= 0) return UI.toast('Entre un montant', 'err');
      S.addCredit({ client, montant, echeance: $('#cr-echeance').value || '', tel: ($('#cr-tel').value || '').trim() });
      UI.closeModal(); UI.toast('Crédit enregistré'); return;
    }
    case 'credit-paid': { S.soldeCredit(id); return; }
    case 'credit-detail': return openCreditDetail(id);
    case 'credit-versement': return openVersementModal(id);
    case 'save-versement': { const v = Number($('#vr-montant').value) || 0; if (v <= 0) return UI.toast('Entre un montant', 'err'); S.addPaiement(id, v); UI.closeModal(); UI.toast('Versement encaissé'); return; }
    case 'credit-solde': { S.soldeCredit(id); UI.closeModal(); UI.toast('Dette soldée'); return; }
    case 'del-credit': return UI.confirmDialog({ title: 'Supprimer le crédit', message: 'Supprimer cette dette client ?', danger: true, okLabel: 'Supprimer' }, () => { S.deleteCredit(id); UI.closeModal(); UI.toast('Crédit supprimé'); });
    case 'credit-remind': {
      const c = S.getCredits().find((x) => x.id === id);
      if (c && c.tel) {
        const nom = S.getState().profil.nom_activite || '';
        const ech = c.echeance ? ` (échéance ${frDate(c.echeance)})` : '';
        const txt = S.renderTemplate(S.getWaTemplate('relance'), { client: c.client || '', commerce: nom, reste: S.formatF(S.creditReste(c)), echeance: ech });
        window.open('https://wa.me/' + c.tel.replace(/[^0-9]/g, '') + '?text=' + encodeURIComponent(txt), '_blank');
      }
      return;
    }
    // annuaire clients
    case 'add-client': return openClientModal(null);
    case 'client-open': return openClientFiche(el.dataset.key);
    case 'client-edit': { if (el.dataset.id) return openClientModal(el.dataset.id); const c = S.clientByKey(el.dataset.key); return openClientModal(null, c ? { nom: c.nom, tel: c.tel, adresse: c.adresse, note: c.note } : null); }
    case 'save-client': {
      const nom = ($('#cl-nom').value || '').trim(), tel = ($('#cl-tel').value || '').trim();
      if (!nom && !tel) return UI.toast('Nom ou téléphone requis', 'err');
      const patch = { nom, tel, adresse: ($('#cl-adr').value || '').trim(), note: ($('#cl-note').value || '').trim() };
      if (id) S.updateClientEntry(id, patch); else S.addClient(patch);
      UI.closeModal(); UI.toast('Client enregistré'); return;
    }
    case 'del-client': return UI.confirmDialog({ title: 'Retirer le client', message: "Retirer ce client de l'annuaire ? (ses ventes et dettes restent enregistrées)", danger: true, okLabel: 'Retirer' }, () => { S.deleteClientEntry(id); UI.closeModal(); UI.toast('Client retiré'); });

    // historique ventes — filtres
    case 'vf-preset': { venteFilter = Object.assign(venteFilter, { preset: el.dataset.preset }, venteRange(el.dataset.preset)); return refreshVentes(); }
    // historique dépenses — filtres
    case 'df-preset': { depFilter = Object.assign(depFilter, { preset: el.dataset.preset }, venteRange(el.dataset.preset)); return refreshDepenses(); }

    // rapports — période + exports
    case 'rap-gran': rapGran = el.dataset.gran; return refreshBilan();
    case 'rap-pdf': return printRapport(S.rapportPeriode(rapGran, 0));
    case 'rap-csv': { downloadFile(`rapport-${rapGran}-${new Date().toISOString().slice(0, 10)}.csv`, rapportCSV(S.rapportPeriode(rapGran, 0)), 'text/csv'); UI.toast('Rapport Excel téléchargé'); return; }
    case 'rap-wa': return shareRapport(S.rapportPeriode(rapGran, 0));

    // factures & devis
    case 'doc-new': return openDocEditor(null, el.dataset.type);
    case 'doc-open': return openDocEditor(id);
    case 'doc-add-ligne': {
      const sc = docScope(el); const d = readDoc(sc); d.lignes.push({ designation: '', qte: '', pu: '' });
      const box = sc.querySelector('#dc-lignes'); box.innerHTML = UI.docLignesHTML(d.lignes); hydrateIcons(box); refreshDocTotals(sc); return;
    }
    case 'doc-del-ligne': {
      const sc = docScope(el); const d = readDoc(sc); d.lignes.splice(Number(el.dataset.i), 1);
      if (!d.lignes.length) d.lignes.push({ designation: '', qte: '', pu: '' });
      const box = sc.querySelector('#dc-lignes'); box.innerHTML = UI.docLignesHTML(d.lignes); hydrateIcons(box); refreshDocTotals(sc); return;
    }
    case 'doc-set-statut': { const sc = docScope(el); const d = readDoc(sc); if (id) { S.updateDocument(id, Object.assign(d, { statut: el.dataset.statut })); openDocEditor(id); } return; }
    case 'doc-save': { const s = saveDocFromForm(el); if (s) { UI.closeModal(); UI.toast(s.type === 'devis' ? 'Devis enregistré' : 'Facture enregistrée'); } return; }
    case 'doc-save-pdf': { const s = saveDocFromForm(el); if (s) { UI.closeModal(); printDoc(s); } return; }
    case 'doc-save-wa': { const s = saveDocFromForm(el); if (s) { UI.closeModal(); shareDocWA(s); } return; }
    case 'doc-pdf': return printDoc(S.getDocument(id));
    case 'doc-wa': return shareDocWA(S.getDocument(id));
    case 'doc-del': return UI.confirmDialog({ title: 'Supprimer le document', message: 'Ce document sera définitivement supprimé. Continuer ?', danger: true, okLabel: 'Supprimer' }, () => { S.deleteDocument(id); UI.closeModal(); UI.toast('Document supprimé'); });

    // navigation / chrome (drawer, cloche, sidebar accordéon, FAB)
    case 'open-drawer': return setOverlay('drawer');
    case 'open-notifs': return setOverlay('notifs');
    case 'close-overlay': return setOverlay(null);
    case 'notif-go': setOverlay(null); return setScreen(el.dataset.screen);
    case 'side-acc': { const g = el.dataset.grp; sidebarAcc = (sidebarAcc === g) ? '__none__' : g; return renderSidebar(); }
    case 'fab-toggle': fabOpen = !fabOpen; return renderFab();
    case 'fab-close': fabOpen = false; return renderFab();
    case 'fab-vente': closeChrome(); return openVenteModal();
    case 'fab-depense': closeChrome(); return openDepenseModal();
    case 'global-search': return; // saisie gérée par le listener input
    case 'gsearch-go': { const b = $('#gsearch-res'); if (b) b.classList.remove('is-open'); return setScreen(el.dataset.screen); }

    // stock
    case 'stock-filter': stockFilter.statut = el.dataset.f; return refreshStock();
    case 'stock-plus': S.ajusterStock(id, 1); return refreshStock();
    case 'stock-minus': S.ajusterStock(id, -1); return refreshStock();
    case 'stock-track': S.setStock(id, 0); UI.toast('Stock suivi'); return refreshStock();
    case 'stock-edit': return openStockModal(id);
    case 'save-stock': {
      const q = $('#st-qte').value;
      S.setStock(id, q === '' ? null : q);
      S.setSeuil(id, $('#st-seuil').value || 0);
      UI.closeModal(); UI.toast('Stock mis à jour'); return refreshStock();
    }

    // objectifs multiples (cagnottes / projets)
    case 'obj-new': return openGoalModal(null);
    case 'obj-open': return openGoalModal(id);
    case 'obj-contrib': return openContribModal(id);
    case 'obj-icone': { const b = el.closest('.modal__body') || document; b.querySelectorAll('[data-action="obj-icone"]').forEach((x) => x.classList.remove('is-on')); el.classList.add('is-on'); return; }
    case 'save-objectif': {
      const titre = ($('#ob-titre').value || '').trim();
      if (!titre) return UI.toast("Donne un nom à l'objectif", 'err');
      const on = $('#modal-root .objic.is-on');
      const icone = (on && on.dataset.ic) || 'target';
      const payload = { titre, icone, montant_cible: $('#ob-cible').value, echeance: $('#ob-ech').value, note: $('#ob-note').value };
      if (id) { if ($('#ob-actuel')) payload.montant_actuel = $('#ob-actuel').value; S.updateObjectif(id, payload); }
      else S.addObjectif(payload);
      UI.closeModal(); UI.toast('Objectif enregistré'); return;
    }
    case 'obj-add-montant': { const v = Number($('#ob-add').value) || 0; if (v <= 0) return UI.toast('Entre un montant', 'err'); S.contribuerObjectif(id, v); UI.closeModal(); UI.toast('Ajouté à ta cagnotte'); return; }
    case 'del-objectif': return UI.confirmDialog({ title: "Supprimer l'objectif", message: 'Supprimer cet objectif et sa cagnotte ?', danger: true, okLabel: 'Supprimer' }, () => { S.deleteObjectif(id); UI.closeModal(); UI.toast('Objectif supprimé'); });

    // caisse (panier POS) + reçu
    case 'cart-add': { const it = cart.find((x) => x.produit_id === id); if (it) it.qte++; else { const p = S.getProduit(id); cart.push({ produit_id: id, qte: 1, prix_unitaire: p ? p.prix_vente : 0 }); } return refreshCaisse(); }
    case 'cart-inc': { const it = cart.find((x) => x.produit_id === id); if (it) it.qte++; return refreshCaisse(); }
    case 'cart-dec': { const it = cart.find((x) => x.produit_id === id); if (it) { it.qte--; if (it.qte <= 0) cart = cart.filter((x) => x.produit_id !== id); } return refreshCaisse(); }
    case 'cart-remove': cart = cart.filter((x) => x.produit_id !== id); return refreshCaisse();
    case 'cart-mode': cartMode = el.dataset.mode; return refreshCaisse();
    case 'cart-encaisser': {
      if (!cart.length) return;
      const ticket = S.encaisserPanier(cart, { mode: cartMode, vendeur: cartVendeur });
      cart = []; UI.closeModal(); UI.toast('Vente encaissée'); pulseBenef();
      if (ticket) openReceiptModal(ticket);
      return;
    }
    case 'rcpt-print': { const d = S.receiptByTicket(el.dataset.ref) || S.receiptData(el.dataset.ref); if (d) printReceipt(d, el.dataset.fmt); return; }
    case 'rcpt-wa': { const d = S.receiptByTicket(el.dataset.ref) || S.receiptData(el.dataset.ref); if (d) shareReceiptWA(d); return; }
    case 'vf-recu': return openReceiptModal(id);

    // vendeurs (liste légère)
    case 'add-vendeur': { const nom = ($('#rg-vend').value || '').trim(); if (!nom) return UI.toast('Entre un nom', 'err'); S.addVendeur(nom); UI.toast('Vendeur ajouté'); return; }
    case 'del-vendeur': { S.removeVendeur(el.dataset.nom); UI.toast('Vendeur retiré'); return; }

    // achats fournisseurs
    case 'ac-new': return openAchatModal();
    case 'ac-open': return openAchatView(id);
    case 'ac-add-ligne': { const sc = achatScope(); const d = readAchat(sc); d.lignes.push(newAchatLine()); const box = sc.querySelector('#ac-lignes'); box.innerHTML = UI.achatLignesHTML(d.lignes); hydrateIcons(box); refreshAchatTotals(sc); return; }
    case 'ac-del-ligne': { const sc = achatScope(); const d = readAchat(sc); d.lignes.splice(Number(el.dataset.i), 1); if (!d.lignes.length) d.lignes.push(newAchatLine()); const box = sc.querySelector('#ac-lignes'); box.innerHTML = UI.achatLignesHTML(d.lignes); hydrateIcons(box); refreshAchatTotals(sc); return; }
    case 'ac-statut': { const f = $('#modal-root .achatform'); if (f) { f.dataset.statut = el.dataset.st; f.querySelectorAll('[data-action="ac-statut"]').forEach((x) => x.classList.remove('is-on')); el.classList.add('is-on'); } return; }
    case 'save-achat': { const d = readAchat(achatScope()); if (!d.lignes.length) return UI.toast('Ajoute au moins un produit', 'err'); S.addAchat(d); UI.closeModal(); UI.toast('Achat enregistré · stock mis à jour'); return; }
    case 'ac-set-statut': S.setAchatStatut(id, el.dataset.st); return openAchatView(id);
    case 'del-achat': return UI.confirmDialog({ title: "Supprimer l'achat", message: "L'achat sera supprimé et le stock ajusté en conséquence. Continuer ?", danger: true, okLabel: 'Supprimer' }, () => { S.deleteAchat(id); UI.closeModal(); UI.toast('Achat supprimé'); });
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
    case 'pf-tarif': { const sc = productScope(el); const p = readProduct(sc); p.tarif_type = el.dataset.tarif; return reRenderProduct(sc, p); }
    case 'wz-biz': S.setBusinessType(el.dataset.v); if (wizard) wizard.produit = null; return render();
    case 'set-biz': S.setBusinessType(el.dataset.v); refreshReglages(); return UI.toast(el.dataset.v === 'digital' ? 'Mode Services & digital' : 'Mode Produits physiques');
    case 'vente-libre': return openVenteLibreModal();
    case 'vl-save': {
      const amt = Number((($('#vl-amt') || {}).value)) || 0;
      if (amt <= 0) return UI.toast('Entre un montant', 'err');
      const v = S.addVenteLibre({ montant: amt, libelle: (($('#vl-desc') || {}).value || '').trim(), mode: cartMode, vendeur: cartVendeur });
      UI.closeModal(); openReceiptModal(v.id); return;
    }
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
  else if (el.matches('[data-action="save-devise"]')) { S.setDevise(el.value); UI.toast('Devise mise à jour'); }
  else if (el.matches('[data-action="vf-from"]')) { venteFilter.from = el.value; venteFilter.preset = 'custom'; refreshVentes(); }
  else if (el.matches('[data-action="vf-to"]')) { venteFilter.to = el.value; venteFilter.preset = 'custom'; refreshVentes(); }
  else if (el.matches('[data-action="vf-produit"]')) { venteFilter.produitId = el.value; refreshVentes(); }
  else if (el.matches('[data-action="vf-search"]')) { venteFilter.q = el.value; refreshVentes(); }
  else if (el.matches('[data-action="df-from"]')) { depFilter.from = el.value; depFilter.preset = 'custom'; refreshDepenses(); }
  else if (el.matches('[data-action="df-to"]')) { depFilter.to = el.value; depFilter.preset = 'custom'; refreshDepenses(); }
  else if (el.matches('[data-action="df-cat"]')) { depFilter.categorie = el.value; refreshDepenses(); }
  else if (el.matches('[data-action="df-search"]')) { depFilter.q = el.value; refreshDepenses(); }
  else if (el.matches('[data-action="save-fisc"]')) { const f = el.dataset.field; if (f) S.setProfil({ [f]: (el.value || '').trim() }); }
  else if (el.matches('[data-action="save-prop"]')) { S.setProfil({ proprietaire: (el.value || '').trim() }); }
  else if (el.matches('[data-action="m-role"]')) { const h = document.getElementById('m-rolehint'); if (h) h.textContent = S.ROLE_DESCS[el.value] || ''; }
  else if (el.matches('[data-action="watpl-save"]')) { S.setWaTemplate(el.dataset.key, el.value); }
  else if (el.matches('[data-action="lted-term"]')) { I18n.setCustomTerm(el.dataset.code, el.dataset.fr, el.value); }
  else if (el.matches('[data-action="lted-name"]')) { I18n.addCustomLang(el.dataset.code, (el.value || '').trim()); refreshReglages(); }
  else if (el.matches('[data-action="cart-vendeur"]')) { cartVendeur = el.value; }
  else if (el.matches('[data-action="vf-mode"]')) { venteFilter.mode = el.value; refreshVentes(); }
  else if (el.matches('[data-action="vf-vendeur"]')) { venteFilter.vendeur = el.value; refreshVentes(); }
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
  } else if (el.matches('[data-action="df-search"]')) {
    depFilter.q = el.value;
    clearTimeout(window.__dfSearchT);
    window.__dfSearchT = setTimeout(() => {
      refreshDepenses();
      const s = document.querySelector('[data-action="df-search"]');
      if (s) { s.focus(); const v = s.value; s.setSelectionRange(v.length, v.length); }
    }, 220);
  } else if (el.matches('[data-action="stock-search"]')) {
    stockFilter.q = el.value;
    clearTimeout(window.__stSearchT);
    window.__stSearchT = setTimeout(() => {
      refreshStock();
      const s = document.querySelector('[data-action="stock-search"]');
      if (s) { s.focus(); const v = s.value; s.setSelectionRange(v.length, v.length); }
    }, 200);
  } else if (el.matches('[data-action="global-search"]')) {
    doGlobalSearch(el.value);
  } else if (el.closest && el.closest('.docform')) {
    // totaux facture/devis recalculés en direct à chaque frappe
    refreshDocTotals(el.closest('.docform'));
  } else if (el.closest && el.closest('.achatform')) {
    refreshAchatTotals(el.closest('.achatform'));
  }
});
// Assistant : Entrée = envoyer
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && e.target && e.target.id === 'as-input') { e.preventDefault(); assistantAsk(e.target.value); }
});
// Sélection auto du contenu au focus des champs chiffrés d'une facture/devis
// (pour que la frappe remplace la valeur par défaut au lieu de s'y ajouter).
document.addEventListener('focusin', (e) => {
  const el = e.target;
  if (el && el.matches && el.matches('.docform input[type="number"], .achatform input[type="number"]')) { try { el.select(); } catch (_) {} }
});

// ---------- Ripple sur TOUS les boutons (onde depuis le point touché) ----------
const RIPPLE_SEL = '.btn, .qsell, .pchip, .vchip, .catchip, .aschip, .chip, .crd-btn, .pnav__btn, .nav__item, .cashtile--caisse, .seg__b, .authswitch__b, .fab__btn, .fab__act, .side__item, .side__sub, .drawer__item, .notif__row, .strow__pm, .objic, .objrow__add, .kpit--tap, .alertrow, .modechip, .cline__pm, .caisse__prod, .modechip, .crdrow__tap, .clirow__main';
document.addEventListener('pointerdown', (e) => {
  const el = e.target.closest ? e.target.closest(RIPPLE_SEL) : null;
  if (!el) return;
  try { if (matchMedia('(prefers-reduced-motion: reduce)').matches) return; } catch {}
  const r = el.getBoundingClientRect();
  const size = Math.max(r.width, r.height);
  const sp = document.createElement('span');
  sp.className = 'ripple';
  sp.style.width = sp.style.height = size + 'px';
  sp.style.left = (e.clientX - r.left - size / 2) + 'px';
  sp.style.top = (e.clientY - r.top - size / 2) + 'px';
  el.appendChild(sp);
  setTimeout(() => sp.remove(), 620);
});

// ---------- Boutons « aimantés » sur PC (suivent légèrement le curseur) ----------
try {
  if (matchMedia('(hover: hover) and (pointer: fine)').matches) {
    let magEl = null;
    document.addEventListener('pointermove', (e) => {
      const el = e.target.closest ? e.target.closest('.btn, .qsell') : null;
      if (magEl && magEl !== el) { magEl.style.translate = ''; magEl = null; }
      if (el) {
        const r = el.getBoundingClientRect();
        const mx = (e.clientX - (r.left + r.width / 2)) * 0.18;
        const my = (e.clientY - (r.top + r.height / 2)) * 0.28;
        el.style.translate = `${mx.toFixed(1)}px ${my.toFixed(1)}px`;
        magEl = el;
      }
    });
  }
} catch {}

function pulseBenef() {
  const el = $('.env--benefice'); if (!el) return;
  el.classList.remove('pulse'); void el.offsetWidth; el.classList.add('pulse');
}

// ---------- Démarrage ----------
async function boot() {
  initTheme();
  initPrefs();
  S.initStore();
  S.ensureTrial();                // démarre l'essai de 30 j à la 1re ouverture
  setActiveMember(loadActiveMember());   // restaure la session + fixe l'auteur du journal d'audit
  if (isConfigured()) screen = 'accueil';
  else screen = CLOUD_ENABLED ? 'welcome' : 'config';
  const h = (location.hash || '').replace('#', '');
  if (h === ADMIN_ROUTE) screen = 'admin';   // back-office (n'affiche que si admin connecté)
  else if (isConfigured() && ['accueil', 'ventes', 'depenses', 'bilan', 'carnet', 'stock', 'reglages'].includes(h)) screen = h;
  if (screen === 'config') wizard = { step: 1, charges: UI.defaultCharges() };
  if (screen === 'accueil') animateNext = true;
  render();
  if (Sec.hasPin() && Sec.lockOnOpen()) renderLock('open');   // verrouillage à l'ouverture
  I18n.startI18n();               // traduit l'interface si une autre langue est choisie
  setTimeout(hideSplash, 1300);   // splash signature « boussole » : durée minimale
  maybeShowTuto();
  if (CLOUD_ENABLED) { try { await Cloud.initSupabase(); } catch (e) { console.warn('supabase init', e); } }
  // service worker (offline)
  if ('serviceWorker' in navigator) navigator.serviceWorker.register(`sw.js?v=${APP_VERSION}`).catch(() => {});
}
boot();

// LA BOBINE · le chef d'orchestre : accueil, éditeur, bibliothèque, réglages, export.

import * as M from './model.js';
import * as S from './stock.js';
import { importer } from './medias.js';
import { Lecteur } from './lecteur.js';
import { Frise } from './frise.js';
import { exporter, dimensionsSortie } from './export.js';
import { OFFRES, estPro } from './offre.js';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const estMobile = () => window.matchMedia('(max-width: 959px)').matches;
const PALETTE = ['#ffffff', '#14110e', '#ffd23f', '#ff5a4e', '#4fc58a', '#5b9dff', '#9a86ff', '#ff9fc6'];

const app = {
  p: null,
  medias: new Map(),
  selection: null,
  historique: new M.Historique(),
  aEffacer: new Set(),
  editionNotee: false,
  enregistreur: null,
  dernierExport: null,
  trouver: (id) => (app.p ? M.trouver(app.p, id) : null),
};
window.__labobine = app;

// ====================================================================== utilitaires
let minuteurToast = 0;
function toast(texte, action, faire, duree = 5000) {
  const t = $('#toast');
  $('#toast-texte').textContent = texte;
  const b = $('#toast-action');
  b.hidden = !action;
  b.textContent = action || '';
  b.onclick = () => { t.hidden = true; if (faire) faire(); };
  t.hidden = false;
  clearTimeout(minuteurToast);
  minuteurToast = setTimeout(() => { t.hidden = true; }, duree);
}

const dateCourte = (ms) => new Date(ms).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
const nombre = (v, n = 1) => Number(v).toFixed(n).replace('.', ',');
function formatValeur(f, v) {
  if (f === 'pct') return `${Math.round(v * 100)} %`;
  if (f === 'x') return `${nombre(v, 2)}×`;
  if (f === 's') return `${nombre(v)} s`;
  if (f === 'deg') return `${Math.round(v)}°`;
  return String(v);
}

async function chargerPolices() {
  try {
    await Promise.all([...M.POLICES.map((f) => document.fonts.load(`${f.poids} 40px "${f.nom}"`)), document.fonts.load('800 40px "Bricolage Grotesque"')]);
  } catch { /* hors ligne : le moteur retombe sur la police système */ }
  if (app.p) app.lecteur.afficher();
}

// ====================================================================== accueil
async function afficherAccueil(remplacer = false) {
  if (app.p) await quitterEditeur();
  $('#editeur').hidden = true;
  $('#accueil').hidden = false;
  document.title = 'LA BOBINE · le montage vidéo dans ton navigateur';
  if (location.hash) history[remplacer ? 'replaceState' : 'pushState'](null, '', location.pathname);
  await rendreProjets();
}

async function rendreProjets() {
  const projets = (await S.lireProjets()).filter((p) => !app.aEffacer.has(p.id));
  const liste = $('#liste-projets');
  if (!projets.length) {
    liste.innerHTML = '<p class="vide">Aucun projet pour l\'instant. Commence par « Nouveau projet ».</p>';
    return;
  }
  liste.innerHTML = projets.map((p) => `
    <article class="carte-projet" data-id="${p.id}">
      <div class="apercu" style="${p.vignette ? `background-image:url('${p.vignette}')` : ''}">${p.vignette ? '' : esc(p.format)}</div>
      <div class="nom">${esc(p.nom)}</div>
      <div class="meta">${esc(p.format)} · ${M.formatTemps(M.dureeProjet(p))} · ${dateCourte(p.modifieLe)}</div>
      <button class="ouvrir" data-action="ouvrir" aria-label="Ouvrir ${esc(p.nom)}"></button>
      <div class="actions"><button data-action="dupliquer">Dupliquer</button><button data-action="supprimer" class="danger">Supprimer</button></div>
    </article>`).join('');
}

function choisirFormat() {
  const dlg = $('#dlg-format');
  $('#choix-formats').innerHTML = Object.entries(M.FORMATS).map(([cle, f]) => {
    const r = 46 / Math.max(f.w, f.h);
    return `<button class="choix-format" value="${cle}"><span class="forme" style="width:${Math.round(f.w * r)}px;height:${Math.round(f.h * r)}px"></span><b>${f.nom} ${cle}</b><small>${f.pour}</small></button>`;
  }).join('');
  dlg.returnValue = '';
  dlg.showModal();
  return new Promise((ok) => dlg.addEventListener('close', () => ok(M.FORMATS[dlg.returnValue] ? dlg.returnValue : null), { once: true }));
}

async function nouveauProjet() {
  const format = await choisirFormat();
  if (!format) return;
  const n = (await S.lireProjets()).length + 1;
  const p = M.nouveauProjet(format, `Projet ${n}`);
  await S.ecrireProjet(p);
  await ouvrir(p.id);
}

async function supprimerProjet(id) {
  app.aEffacer.add(id);
  await rendreProjets();
  const minuteur = setTimeout(async () => {
    if (!app.aEffacer.has(id)) return;
    await S.effacerProjet(id);
    app.aEffacer.delete(id);
    await S.ramasserMedias();
  }, 6500);
  toast('Projet supprimé', 'Annuler', async () => { clearTimeout(minuteur); app.aEffacer.delete(id); await rendreProjets(); }, 6000);
}

async function dupliquerProjet(id) {
  const p = await S.lireProjet(id);
  if (!p) return;
  const copie = JSON.parse(JSON.stringify(p));
  copie.id = M.uid('p');
  copie.nom = `${p.nom} (copie)`;
  copie.creeLe = Date.now();
  copie.modifieLe = Date.now();
  await S.ecrireProjet(copie);
  await rendreProjets();
  toast('Projet dupliqué');
}

// ====================================================================== éditeur
async function ouvrir(id, remplacer = false) {
  const p = await S.lireProjet(id);
  if (!p) { toast("Ce projet n'existe plus."); await afficherAccueil(true); return; }
  p.medias = p.medias || [];
  app.p = p;
  app.medias = new Map();
  for (const mid of p.medias) {
    const m = await S.lireMedia(mid);
    if (m) app.medias.set(mid, m);
  }
  app.historique = new M.Historique();
  app.selection = null;
  $('#accueil').hidden = true;
  $('#editeur').hidden = false;
  if (location.hash !== `#${p.id}`) history[remplacer ? 'replaceState' : 'pushState'](null, '', `#${p.id}`);
  $('#nom-projet').value = p.nom;
  $('#etat-sauve').textContent = '';
  document.title = `${p.nom} · LA BOBINE`;
  app.lecteur.charger(p, app.medias);
  app.lecteur.selection = null;
  app.lecteur.t = 0;
  dimensionnerToile();
  app.frise.ajusterZoom();
  toutRendre();
  await app.lecteur.aller(0);
  app.frise.majTemps(0, true);
  majTemps(0);
}

async function quitterEditeur() {
  if (app.enregistreur) app.enregistreur.stop();
  app.lecteur.detruire();
  await sauver();
  app.p = null;
  fermerFeuilles();
}

function toutRendre() {
  app.frise.rendre();
  rendreInspecteur();
  rendreBiblio();
  majBoutons();
  majDuree();
}

/** Toute modification du montage passe par ici : historique, tassement, rendu, sauvegarde. */
function modifier(fn, { noter = true } = {}) {
  if (!app.p) return;
  if (noter) app.historique.noter(M.etatMontage(app.p));
  app.editionNotee = false;
  fn(app.p);
  M.tasserPrincipale(app.p);
  M.nettoyerPistes(app.p);
  if (app.selection && !M.trouver(app.p, app.selection)) app.selection = null;
  apresModification();
}
app.modifier = modifier;

function apresModification() {
  app.lecteur.charger(app.p, app.medias);
  app.lecteur.selection = app.selection;
  dimensionnerToile();
  app.frise.rendre();
  rendreInspecteur();
  majBoutons();
  majDuree();
  const t = Math.min(app.lecteur.t, M.dureeProjet(app.p));
  app.lecteur.aller(t);
  app.frise.majTemps(t);
  majTemps(t);
  sauverBientot();
}

function annuler() {
  const e = app.historique.annuler(M.etatMontage(app.p));
  if (!e) return;
  Object.assign(app.p, e);
  app.selection = null;
  apresModification();
  toast('Annulé');
}
function retablir() {
  const e = app.historique.retablir(M.etatMontage(app.p));
  if (!e) return;
  Object.assign(app.p, e);
  app.selection = null;
  apresModification();
}

function noterUneFois() {
  if (app.editionNotee || !app.p) return;
  app.historique.noter(M.etatMontage(app.p));
  app.editionNotee = true;
  majBoutons();
}

function selectionner(id, { section } = {}) {
  app.selection = id;
  app.editionNotee = false;
  app.lecteur.selection = id;
  app.frise.marquerSelection(id);
  rendreInspecteur(section);
  majBoutons();
  app.lecteur.afficher();
  if (section && estMobile()) ouvrirFeuille('inspecteur');
}
app.selectionner = selectionner;

function allerA(t) {
  app.lecteur.pause();
  app.lecteur.aller(t);
  app.frise.majTemps(t, true);
  majTemps(t);
}
app.allerA = allerA;

app.surDefilement = (t) => {
  if (app.lecteur.enLecture) app.lecteur.pause();
  app.lecteur.aller(t);
  majTemps(t);
};

function majTemps(t) {
  $('#temps').textContent = M.formatTemps(t, true, app.p ? app.p.fps : 30);
  majBoutons();
}
function majDuree() {
  $('#duree').textContent = M.formatTemps(app.p ? M.dureeProjet(app.p) : 0, true, app.p ? app.p.fps : 30);
}

function clipADiviser() {
  const t = app.lecteur.t;
  const sel = app.selection && M.trouver(app.p, app.selection);
  if (sel && t > sel.clip.debut + M.DUREE_MIN && t < M.finClip(sel.clip) - M.DUREE_MIN) return sel.clip;
  const c = M.clipSous(app.p, t);
  return c && t > c.debut + M.DUREE_MIN && t < M.finClip(c) - M.DUREE_MIN ? c : null;
}

function majBoutons() {
  if (!app.p) return;
  $('#btn-annuler').disabled = !app.historique.peutAnnuler;
  $('#btn-retablir').disabled = !app.historique.peutRetablir;
  $('#btn-supprimer').disabled = !app.selection;
  $('#btn-dupliquer').disabled = !app.selection;
  $('#btn-diviser').disabled = !clipADiviser();
}

function diviserIci() {
  const c = clipADiviser();
  if (!c) return;
  let nouveau = null;
  modifier((p) => { nouveau = M.diviser(p, c.id, app.lecteur.t); });
  if (nouveau) selectionner(nouveau.id);
}
function supprimerSelection() {
  if (!app.selection) return;
  const id = app.selection;
  app.selection = null;
  modifier((p) => M.supprimer(p, id));
  toast('Clip supprimé', 'Annuler', annuler);
}
function dupliquerSelection() {
  if (!app.selection) return;
  let b = null;
  modifier((p) => { b = M.dupliquer(p, app.selection); });
  if (b) selectionner(b.id);
}

// ====================================================================== sauvegarde
let minuteurSauve = 0;
function sauverBientot() {
  $('#etat-sauve').textContent = 'Modifié';
  clearTimeout(minuteurSauve);
  minuteurSauve = setTimeout(sauver, 600);
}
async function sauver() {
  clearTimeout(minuteurSauve);
  const p = app.p;
  if (!p) return;
  p.modifieLe = Date.now();
  const premier = M.principale(p).clips[0];
  const m = premier && app.medias.get(premier.media);
  p.vignette = m ? m.vignette : null;
  try {
    await S.ecrireProjet(p);
    if (app.p === p) $('#etat-sauve').textContent = 'Enregistré';
  } catch {
    $('#etat-sauve').textContent = 'Non enregistré';
    toast("L'enregistrement a échoué : l'espace de ton navigateur est peut-être plein.");
  }
}

// ====================================================================== import
app.ouvrirImport = () => $('#entree-fichiers').click();

async function importerFichiers(fichiers, { versSon = false } = {}) {
  const liste = [...fichiers];
  if (!liste.length || !app.p) return;
  toast(liste.length > 1 ? `Import de ${liste.length} fichiers…` : 'Import en cours…', null, null, 60000);
  const ajoutes = [];
  for (const f of liste) {
    try {
      const m = await importer(f);
      await S.ecrireMedia(m);
      app.medias.set(m.id, m);
      app.p.medias.push(m.id);
      ajoutes.push(m);
    } catch (e) {
      toast(e.message && e.message.includes('«') ? e.message : `« ${f.name} » n'a pas pu être lu : ${e.message || 'format inconnu'}.`);
    }
  }
  if (!ajoutes.length) return;
  $('#toast').hidden = true;
  const visuels = ajoutes.filter((m) => m.type !== 'audio');
  const sons = ajoutes.filter((m) => m.type === 'audio');
  const principaleVide = !M.principale(app.p).clips.length;
  let dernier = null;
  modifier((p) => {
    if (principaleVide) {
      for (const m of visuels) dernier = M.insererPrincipale(p, m, M.dureeProjet({ pistes: [M.principale(p)] }));
    }
    if (versSon) {
      let t = app.lecteur.t;
      for (const m of sons) { const c = M.clipDepuisMedia(m, t); M.poserSurPisteLibre(p, 'audio', c); t = M.finClip(c); dernier = c; }
    }
  });
  if (dernier) selectionner(dernier.id);
  rendreBiblio();
  if (!principaleVide && visuels.length) toast(`${visuels.length} média${visuels.length > 1 ? 's' : ''} dans la bibliothèque : touche « Ajouter » pour le poser.`);
  else if (principaleVide && visuels.length) toast(`${visuels.length} média${visuels.length > 1 ? 's posés' : ' posé'} sur la frise`);
}

function ajouterMedia(id, mode) {
  const m = app.medias.get(id);
  if (!m) return;
  const t = app.lecteur.t;
  let c = null;
  modifier((p) => {
    if (m.type === 'audio') { c = M.clipDepuisMedia(m, t); M.poserSurPisteLibre(p, 'audio', c); }
    else if (mode === 'superposer') { c = M.clipDepuisMedia(m, t); c.echelle = 0.5; M.poserSurPisteLibre(p, 'superposition', c); }
    else c = M.insererPrincipale(p, m, t);
  });
  if (c) selectionner(c.id);
  if (estMobile()) fermerFeuilles();
}

function ajouterTexte(style) {
  const c = M.clipTexte(app.lecteur.t, style);
  modifier((p) => M.poserSurPisteLibre(p, 'texte', c));
  selectionner(c.id);
  if (estMobile()) fermerFeuilles();
}

// ====================================================================== voix off
async function basculerVoix() {
  if (app.enregistreur) { app.enregistreur.stop(); return; }
  if (!navigator.mediaDevices || !window.MediaRecorder) { toast("Ce navigateur ne sait pas enregistrer le micro."); return; }
  let flux;
  try {
    flux = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
  } catch {
    toast('Micro refusé : autorise-le dans les réglages du navigateur.');
    return;
  }
  const type = ['audio/webm;codecs=opus', 'audio/mp4', 'audio/webm'].find((x) => MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(x));
  const rec = new MediaRecorder(flux, type ? { mimeType: type } : undefined);
  const morceaux = [];
  const debut = app.lecteur.t;
  const t0 = Date.now();
  rec.ondataavailable = (e) => { if (e.data.size) morceaux.push(e.data); };
  rec.onstop = async () => {
    flux.getTracks().forEach((x) => x.stop());
    clearInterval(app.minuteurVoix);
    app.enregistreur = null;
    $('#btn-voix').classList.remove('enregistre');
    $('#voix-libelle').textContent = 'Voix off';
    const mime = rec.mimeType || 'audio/webm';
    const blob = new Blob(morceaux, { type: mime });
    const heure = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    const fichier = new File([blob], `Voix off ${heure}.${mime.includes('mp4') ? 'm4a' : 'webm'}`, { type: mime });
    try {
      const m = await importer(fichier);
      await S.ecrireMedia(m);
      app.medias.set(m.id, m);
      app.p.medias.push(m.id);
      const c = M.clipDepuisMedia(m, debut);
      modifier((p) => M.poserSurPisteLibre(p, 'audio', c));
      selectionner(c.id);
      rendreBiblio();
      toast('Voix off ajoutée');
    } catch {
      toast("La voix off n'a pas pu être lue.");
    }
  };
  rec.start(250);
  app.enregistreur = rec;
  $('#btn-voix').classList.add('enregistre');
  app.minuteurVoix = setInterval(() => {
    $('#voix-libelle').textContent = `Arrêter · ${M.formatTemps((Date.now() - t0) / 1000)}`;
  }, 250);
  if (!app.lecteur.enLecture) app.lecteur.jouer();
}

// ====================================================================== bibliothèque
function rendreBiblio() {
  if (!app.p) return;
  const medias = app.p.medias.map((id) => app.medias.get(id)).filter(Boolean);
  const visuels = medias.filter((m) => m.type !== 'audio');
  $('#grille-medias').innerHTML = visuels.length ? visuels.map((m) => `
    <div class="carte-media">
      <div class="vignette" style="background-image:url('${m.vignette}')"></div>
      <span class="duree">${m.type === 'image' ? 'Photo' : M.formatTemps(m.duree)}</span>
      <div class="nom" title="${esc(m.nom)}">${esc(m.nom)}</div>
      <div class="boutons"><button class="ajout" data-ajouter="${m.id}">Ajouter</button><button data-superposer="${m.id}">Superposer</button></div>
    </div>`).join('') : '<p class="aide">Tes vidéos et photos importées apparaîtront ici.</p>';

  const sons = medias.filter((m) => m.type === 'audio');
  $('#liste-sons').innerHTML = sons.length ? sons.map((m) => {
    const n = (m.onde || []).length;
    let d = 'M0 50';
    (m.onde || []).forEach((v, i) => { d += `L${i} ${(50 - Math.max(2, v * 48)).toFixed(1)}`; });
    for (let i = n - 1; i >= 0; i -= 1) d += `L${i} ${(50 + Math.max(2, m.onde[i] * 48)).toFixed(1)}`;
    return `<div class="ligne-son"><span class="nom" title="${esc(m.nom)}">${esc(m.nom)} · ${M.formatTemps(m.duree)}</span>
      <button class="btn petit" data-ajouter="${m.id}">Ajouter</button>
      <svg class="onde" viewBox="0 0 ${Math.max(1, n - 1)} 100" preserveAspectRatio="none" aria-hidden="true"><path d="${d}Z"/></svg></div>`;
  }).join('') : '<p class="aide">Importe une musique, ou enregistre ta voix : elle se pose à la tête de lecture.</p>';
}

function rendreStyles() {
  $('#grille-styles').innerHTML = Object.entries(M.STYLES_TEXTE).map(([cle, s]) => {
    const boite = s.boite === 'pastille' ? `background:${s.couleurBoite};color:${s.couleur};padding:4px 12px;border-radius:999px;`
      : s.boite === 'bande' ? `background:${s.couleurBoite};color:${s.couleur};padding:2px 8px;` : `color:${s.couleur};`;
    const contour = s.contour ? `-webkit-text-stroke:1px ${s.couleurContour};paint-order:stroke fill;` : '';
    return `<button class="style-texte" data-style="${cle}" aria-label="Ajouter un texte ${esc(s.nom)}"><span style="font-family:'${s.police}';font-weight:${s.poids};${boite}${contour}">${esc(s.nom)}</span></button>`;
  }).join('');
}

// ====================================================================== inspecteur
const curseur = (k, label, val, min, max, pas, format) => `<label class="champ"><span>${label}</span><input type="range" data-k="${k}" min="${min}" max="${max}" step="${pas}" value="${val}" data-format="${format}"><output>${formatValeur(format, val)}</output></label>`;
const choix = (k, label, val, options) => `<label class="champ plein"><span>${label}</span><select data-k="${k}">${options.map(([v, t]) => `<option value="${v}"${v === val ? ' selected' : ''}>${t}</option>`).join('')}</select></label>`;
const coche = (k, label, val) => `<label class="interrupteur"><input type="checkbox" data-k="${k}"${val ? ' checked' : ''}><span>${label}</span></label>`;
const couleur = (k, label, val) => `<div class="champ plein"><span>${label}</span><span class="couleurs"><input type="color" data-k="${k}" value="${val}" aria-label="${label}">${PALETTE.map((c) => `<button class="pastille" data-pastille="${c}" data-pour="${k}" style="background:${c}" aria-label="Couleur ${c}"></button>`).join('')}</span></div>`;
const groupe = (titre, html, id = '') => `<section class="groupe-insp"${id ? ` id="insp-${id}"` : ''}><h3>${titre}</h3>${html}</section>`;
const puces = (action, val, options) => `<div class="puces">${options.map(([v, t]) => `<button data-action="${action}" data-v="${v}" aria-pressed="${String(v) === String(val)}">${t}</button>`).join('')}</div>`;

function rendreInspecteur(section) {
  const corps = $('#corps-inspecteur');
  if (!app.p) { corps.innerHTML = ''; return; }
  const f = app.selection && M.trouver(app.p, app.selection);
  if (!f) {
    $('#titre-inspecteur').textContent = 'Projet';
    const p = app.p;
    corps.innerHTML = groupe('Projet', `<label class="champ plein"><span>Nom</span><input type="text" data-k="nom" data-cible="projet" value="${esc(p.nom)}" maxlength="80"></label>`)
      + groupe('Format', `<div class="puces">${Object.entries(M.FORMATS).map(([k, x]) => `<button data-action="format" data-v="${k}" aria-pressed="${k === p.format}">${x.nom} ${k}</button>`).join('')}</div>`)
      + groupe('Fond', choix('fond.type', 'Remplissage', p.fond.type, [['couleur', 'Couleur unie'], ['flou', 'Image floutée']]) + couleur('fond.couleur', 'Couleur', p.fond.couleur))
      + groupe('Montage', `<p class="note">${M.formatTemps(M.dureeProjet(p))} au total, ${p.pistes.reduce((n, t) => n + t.clips.length, 0)} clip(s). Touche un clip de la frise pour le régler.</p>`);
    return;
  }
  const c = f.clip;
  const surPrincipale = f.piste.genre === 'principale';
  let h = '';
  if (c.genre === 'video' || c.genre === 'image') {
    $('#titre-inspecteur').textContent = c.genre === 'video' ? 'Vidéo' : 'Photo';
    h += groupe('Clip', `<div class="actions-insp"><button class="btn petit" data-action="basculer">${surPrincipale ? 'Passer en superposition' : 'Remettre sur la piste principale'}</button></div>`);
    if (c.genre === 'video') {
      h += groupe('Vitesse', curseur('vitesse', 'Vitesse', c.vitesse, M.VITESSE_MIN, M.VITESSE_MAX, 0.05, 'x')
        + puces('vitesse', c.vitesse, [[0.5, '0,5×'], [1, '1×'], [1.5, '1,5×'], [2, '2×'], [3, '3×']]));
      h += groupe('Son', curseur('volume', 'Volume', c.volume, 0, 2, 0.01, 'pct') + coche('muet', 'Couper le son de ce clip', c.muet));
    }
    h += groupe('Image', choix('ajustement', 'Cadrage', c.ajustement, [['adapter', 'Adapter (tout voir)'], ['remplir', "Remplir l'écran"]])
      + curseur('echelle', 'Taille', c.echelle, 0.1, 3, 0.01, 'pct')
      + curseur('cx', 'Position X', c.cx, 0, 1, 0.005, 'pct')
      + curseur('cy', 'Position Y', c.cy, 0, 1, 0.005, 'pct')
      + curseur('rotation', 'Rotation', c.rotation, -180, 180, 1, 'deg')
      + curseur('opacite', 'Opacité', c.opacite, 0, 1, 0.01, 'pct')
      + choix('mouvement', 'Mouvement', c.mouvement, M.MOUVEMENTS)
      + '<p class="note">Sur l\'aperçu : glisse pour déplacer, pince ou molette pour agrandir.</p>');
    h += groupe('Fondus', curseur('fonduEntree', 'Entrée', c.fonduEntree, 0, 3, 0.1, 's') + curseur('fonduSortie', 'Sortie', c.fonduSortie, 0, 3, 0.1, 's'));
    if (surPrincipale && f.index > 0) {
      h += groupe('Transition depuis le clip précédent', choix('transition.type', 'Effet', c.transition.type, M.TRANSITIONS)
        + curseur('transition.duree', 'Durée', c.transition.duree, 0.1, 2, 0.05, 's'), 'transition');
    }
  } else if (c.genre === 'texte') {
    $('#titre-inspecteur').textContent = 'Texte';
    h += groupe('Texte', `<textarea data-k="texte" aria-label="Texte" rows="3">${esc(c.texte)}</textarea>`
      + `<div class="puces">${Object.entries(M.STYLES_TEXTE).map(([k, s]) => `<button data-action="style" data-v="${k}">${esc(s.nom)}</button>`).join('')}</div>`);
    h += groupe('Police', choix('police', 'Police', c.police, M.POLICES.map((x) => [x.nom, x.titre]))
      + curseur('taille', 'Taille', c.taille, 0.02, 0.2, 0.002, 'pct')
      + couleur('couleur', 'Couleur', c.couleur)
      + puces('aligner', c.alignement, [['gauche', 'Gauche'], ['centre', 'Centre'], ['droite', 'Droite']]));
    h += groupe('Habillage', choix('boite', 'Fond', c.boite, [['aucune', 'Aucun'], ['bande', 'Bande sous chaque ligne'], ['pastille', 'Pastille']])
      + couleur('couleurBoite', 'Couleur du fond', c.couleurBoite)
      + coche('contour', 'Contour', c.contour) + couleur('couleurContour', 'Couleur du contour', c.couleurContour));
    h += groupe('Animation', choix('anim', 'Entrée', c.anim, M.ANIMS_TEXTE)
      + `<label class="champ"><span>Durée</span><input type="number" data-k="duree" min="0.1" max="600" step="0.1" value="${c.duree.toFixed(1)}"><output>s</output></label>`);
    h += groupe('Position', curseur('cx', 'Position X', c.cx, 0, 1, 0.005, 'pct') + curseur('cy', 'Position Y', c.cy, 0, 1, 0.005, 'pct')
      + curseur('opacite', 'Opacité', c.opacite, 0, 1, 0.01, 'pct'));
  } else {
    $('#titre-inspecteur').textContent = 'Son';
    h += groupe('Son', curseur('volume', 'Volume', c.volume, 0, 2, 0.01, 'pct') + coche('muet', 'Couper ce son', c.muet)
      + curseur('vitesse', 'Vitesse', c.vitesse, M.VITESSE_MIN, M.VITESSE_MAX, 0.05, 'x'));
    h += groupe('Fondus', curseur('fonduEntree', 'Entrée', c.fonduEntree, 0, 5, 0.1, 's') + curseur('fonduSortie', 'Sortie', c.fonduSortie, 0, 5, 0.1, 's'));
  }
  h += groupe('Actions', `<div class="actions-insp"><button class="btn petit" data-action="diviser">Diviser ici</button><button class="btn petit" data-action="dupliquer">Dupliquer</button><button class="btn petit" data-action="supprimer">Supprimer</button></div>`);
  corps.innerHTML = h;
  if (section) { const s = $(`#insp-${section}`); if (s) s.scrollIntoView({ block: 'start' }); }
}

function surChamp(e) {
  const el = e.target;
  const k = el.dataset.k;
  if (!k || !app.p) return;
  const projet = el.dataset.cible === 'projet' || k.startsWith('fond.');
  const f = app.selection && M.trouver(app.p, app.selection);
  if (!projet && !f) return;
  let v = el.type === 'checkbox' ? el.checked : (el.type === 'range' || el.type === 'number') ? parseFloat(el.value) : el.value;
  if (typeof v === 'number' && !Number.isFinite(v)) return;
  noterUneFois();
  const c = f && f.clip;
  let structurel = false;
  if (k === 'nom') { app.p.nom = String(v).trim() || 'Sans titre'; $('#nom-projet').value = app.p.nom; document.title = `${app.p.nom} · LA BOBINE`; }
  else if (k === 'fond.type') app.p.fond.type = v;
  else if (k === 'fond.couleur') app.p.fond.couleur = v;
  else if (k === 'vitesse') { M.changerVitesse(app.p, c.id, v); structurel = true; }
  else if (k === 'transition.type') { c.transition.type = v; structurel = true; }
  else if (k === 'transition.duree') { c.transition.duree = v; structurel = true; }
  else if (k === 'duree') { c.duree = Math.max(M.DUREE_MIN, v); structurel = true; }
  else c[k] = v;
  const out = el.closest('.champ') && el.closest('.champ').querySelector('output');
  if (out && el.dataset.format) out.textContent = formatValeur(el.dataset.format, v);
  if (structurel || k === 'texte' || k === 'muet' || k === 'volume') {
    M.tasserPrincipale(app.p);
    app.frise.rendre();
    majDuree();
  }
  if (structurel) app.lecteur.aller(app.lecteur.t); else app.lecteur.afficher();
  majBoutons();
  sauverBientot();
}

function surBoutonInspecteur(e) {
  const pastille = e.target.closest('[data-pastille]');
  if (pastille) {
    const entree = $(`input[type="color"][data-k="${pastille.dataset.pour}"]`, $('#corps-inspecteur'));
    if (entree) { app.editionNotee = false; entree.value = pastille.dataset.pastille; entree.dispatchEvent(new Event('input', { bubbles: true })); app.editionNotee = false; }
    return;
  }
  const b = e.target.closest('[data-action]');
  if (!b || !app.p) return;
  const f = app.selection && M.trouver(app.p, app.selection);
  const v = b.dataset.v;
  switch (b.dataset.action) {
    case 'format': modifier((p) => M.changerFormat(p, v)); break;
    case 'basculer': modifier((p) => M.basculerSuperposition(p, app.selection)); selectionner(app.selection); break;
    case 'vitesse': modifier((p) => M.changerVitesse(p, app.selection, parseFloat(v))); break;
    case 'aligner': if (f) modifier(() => { f.clip.alignement = v; }); break;
    case 'style': if (f) modifier(() => {
      const s = M.STYLES_TEXTE[v];
      Object.assign(f.clip, { police: s.police, poids: s.poids, taille: s.taille, couleur: s.couleur, boite: s.boite, couleurBoite: s.couleurBoite || '#000000', contour: s.contour, couleurContour: s.couleurContour || '#000000', anim: s.anim });
    }); break;
    case 'diviser': diviserIci(); break;
    case 'dupliquer': dupliquerSelection(); break;
    case 'supprimer': supprimerSelection(); break;
    default:
  }
}

// ====================================================================== aperçu : déplacer et agrandir au doigt
function ecouterToile() {
  const toile = $('#toile');
  const pointeurs = new Map();
  let geste = null;
  const dansCadre = (r, fx, fy) => {
    const W = app.lecteur.W;
    const H = app.lecteur.H;
    const x = fx * W;
    const y = fy * H;
    return Math.abs(x - r.x) <= r.l / 2 && Math.abs(y - r.y) <= r.h / 2;
  };
  toile.addEventListener('pointerdown', (e) => {
    if (!app.p) return;
    toile.setPointerCapture(e.pointerId);
    pointeurs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    const { fx, fy } = app.lecteur.fraction(e);
    if (pointeurs.size === 1) {
      const ids = Object.keys(app.lecteur.cadres).reverse();
      let id = app.selection && app.lecteur.cadres[app.selection] && dansCadre(app.lecteur.cadres[app.selection], fx, fy) ? app.selection : null;
      if (!id) id = ids.find((k) => dansCadre(app.lecteur.cadres[k], fx, fy)) || null;
      if (id !== app.selection) selectionner(id);
      const f = id && M.trouver(app.p, id);
      geste = f ? { clip: f.clip, fx, fy, cx: f.clip.cx, cy: f.clip.cy, note: false } : null;
    } else if (pointeurs.size === 2 && geste) {
      const [a, b] = [...pointeurs.values()];
      geste.pince = { d: Math.hypot(a.x - b.x, a.y - b.y), echelle: geste.clip.genre === 'texte' ? geste.clip.taille : (geste.clip.echelle ?? 1) };
    }
  });
  toile.addEventListener('pointermove', (e) => {
    if (!pointeurs.has(e.pointerId) || !geste) return;
    pointeurs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (!geste.note) { noterUneFois(); geste.note = true; }
    const c = geste.clip;
    if (geste.pince && pointeurs.size === 2) {
      const [a, b] = [...pointeurs.values()];
      const r = Math.hypot(a.x - b.x, a.y - b.y) / geste.pince.d;
      if (c.genre === 'texte') c.taille = M.clamp(geste.pince.echelle * r, 0.02, 0.3);
      else c.echelle = M.clamp(geste.pince.echelle * r, 0.05, 5);
    } else if (pointeurs.size === 1) {
      const { fx, fy } = app.lecteur.fraction(e);
      c.cx = M.clamp(geste.cx + fx - geste.fx, -0.5, 1.5);
      c.cy = M.clamp(geste.cy + fy - geste.fy, -0.5, 1.5);
    }
    app.lecteur.afficher();
  });
  const fin = (e) => {
    pointeurs.delete(e.pointerId);
    if (pointeurs.size === 0 && geste) {
      if (geste.note) { rendreInspecteur(); sauverBientot(); app.editionNotee = false; majBoutons(); }
      geste = null;
    } else if (geste) geste.pince = null;
  };
  toile.addEventListener('pointerup', fin);
  toile.addEventListener('pointercancel', fin);
  toile.addEventListener('wheel', (e) => {
    const f = app.selection && M.trouver(app.p, app.selection);
    if (!f || f.clip.genre === 'audio') return;
    e.preventDefault();
    noterUneFois();
    const k = e.deltaY < 0 ? 1.05 : 1 / 1.05;
    if (f.clip.genre === 'texte') f.clip.taille = M.clamp(f.clip.taille * k, 0.02, 0.3);
    else f.clip.echelle = M.clamp((f.clip.echelle ?? 1) * k, 0.05, 5);
    app.lecteur.afficher();
    clearTimeout(app.minuteurMolette);
    app.minuteurMolette = setTimeout(() => { rendreInspecteur(); sauverBientot(); app.editionNotee = false; }, 300);
  }, { passive: false });
}

function dimensionnerToile() {
  if (!app.p) return;
  const cadre = $('#cadre-toile');
  const dispoL = cadre.clientWidth - 28;
  const dispoH = cadre.clientHeight - 28;
  if (dispoL <= 0 || dispoH <= 0) return;
  const r = Math.min(dispoL / app.p.w, dispoH / app.p.h);
  const toile = $('#toile');
  toile.style.width = `${Math.floor(app.p.w * r)}px`;
  toile.style.height = `${Math.floor(app.p.h * r)}px`;
}

// ====================================================================== feuilles mobiles
function ouvrirFeuille(nom, onglet) {
  for (const p of $$('.panneau')) p.classList.toggle('ouvert', p.id === nom);
  for (const b of $$('.barre-mobile [data-feuille]')) b.setAttribute('aria-expanded', String(b.dataset.feuille === nom && (!onglet || b.dataset.ongletCible === onglet)));
  if (onglet) choisirOnglet(onglet);
}
function fermerFeuilles() {
  for (const p of $$('.panneau')) p.classList.remove('ouvert');
  for (const b of $$('.barre-mobile [data-feuille]')) b.setAttribute('aria-expanded', 'false');
}
function choisirOnglet(nom) {
  for (const t of $$('#biblio [role="tab"]')) t.setAttribute('aria-selected', String(t.dataset.onglet === nom));
  for (const c of $$('#biblio [data-corps]')) c.hidden = c.dataset.corps !== nom;
}

// ====================================================================== export
function ouvrirExport() {
  if (!app.p || M.dureeProjet(app.p) <= 0) { toast("Ajoute d'abord une vidéo ou une photo."); return; }
  app.lecteur.pause();
  const pro = estPro();
  const qualites = [[720, '720p'], [1080, '1080p'], [2160, '4K']];
  $('#export-qualite').innerHTML = '<legend>Qualité</legend>' + qualites.map(([v, t]) => {
    const permis = (pro ? OFFRES.pro : OFFRES.gratuit).qualites.includes(v);
    return `<label><input type="radio" name="qualite" value="${v}"${v === 1080 ? ' checked' : ''}${permis ? '' : ' disabled'}><span>${t}${permis ? '' : ' <span class="badge-pro">Pro</span>'}</span></label>`;
  }).join('');
  $('#export-cadence').innerHTML = '<legend>Images par seconde</legend>' + [24, 25, 30, 60].map((v) => {
    const permis = (pro ? OFFRES.pro : OFFRES.gratuit).cadences.includes(v);
    return `<label><input type="radio" name="cadence" value="${v}"${v === 30 ? ' checked' : ''}${permis ? '' : ' disabled'}><span>${v}${permis ? '' : ' <span class="badge-pro">Pro</span>'}</span></label>`;
  }).join('');
  const fil = $('#export-filigrane');
  fil.checked = true;
  fil.disabled = !pro;
  $('.offre-pro').hidden = pro;
  majInfosExport();
  $('#export-reglages').hidden = false;
  $('#export-progres').hidden = true;
  $('#export-fini').hidden = true;
  $('#dlg-export').showModal();
}
function majInfosExport() {
  const court = parseInt(($('input[name="qualite"]:checked') || {}).value || '1080', 10);
  const { W, H } = dimensionsSortie(app.p, court);
  $('#export-infos').textContent = `${W} × ${H} pixels · ${M.formatTemps(M.dureeProjet(app.p))} · MP4`;
}

async function lancerExport() {
  const court = parseInt($('input[name="qualite"]:checked').value, 10);
  const fps = parseInt($('input[name="cadence"]:checked').value, 10);
  const filigrane = !estPro() || $('#export-filigrane').checked;
  $('#export-reglages').hidden = true;
  $('#export-progres').hidden = false;
  $('#export-etape').textContent = 'Préparation…';
  $('#export-barre').style.transform = 'scaleX(0)';
  $('#export-pourcent').textContent = '0 %';
  $('#export-reste').textContent = '';
  const ctrl = new AbortController();
  app.exportEnCours = ctrl;
  const t0 = performance.now();
  try {
    await sauver();
    const r = await exporter(app.p, app.medias, {
      court, fps, filigrane, signal: ctrl.signal,
      progres: ({ etape, part }) => {
        $('#export-etape').textContent = etape === 'son' ? 'Mixage du son…' : etape === 'fin' ? 'Finalisation…' : 'Fabrication des images…';
        const total = etape === 'images' ? 0.05 + part * 0.93 : etape === 'son' ? 0.03 : 1;
        $('#export-barre').style.transform = `scaleX(${total})`;
        $('#export-pourcent').textContent = `${Math.round(total * 100)} %`;
        if (etape === 'images' && part > 0.03) {
          const ecoule = (performance.now() - t0) / 1000;
          const reste = Math.max(0, (ecoule / part) * (1 - part));
          $('#export-reste').textContent = `Encore environ ${reste < 60 ? `${Math.ceil(reste)} s` : `${Math.ceil(reste / 60)} min`}`;
        }
      },
    });
    app.dernierExport = r;
    if (app.urlExport) URL.revokeObjectURL(app.urlExport);
    app.urlExport = URL.createObjectURL(r.blob);
    $('#export-video').src = app.urlExport;
    const nom = `${(app.p.nom || 'video').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^\w-]+/g, '-').replace(/^-|-$/g, '') || 'video'}.${r.extension}`;
    const lien = $('#export-telecharger');
    lien.href = app.urlExport;
    lien.download = nom;
    const fichier = new File([r.blob], nom, { type: r.type });
    const partager = $('#export-partager');
    partager.hidden = !(navigator.canShare && navigator.canShare({ files: [fichier] }));
    partager.onclick = () => navigator.share({ files: [fichier], title: app.p.nom }).catch(() => {});
    const mo = r.blob.size / 1048576;
    const sec = ((performance.now() - t0) / 1000).toFixed(0);
    $('#export-resume').textContent = `${r.W} × ${r.H} · ${M.formatTemps(r.duree)} · ${mo < 1 ? `${Math.round(mo * 1024)} Ko` : `${nombre(mo)} Mo`} · fabriquée en ${sec} s${filigrane ? ' · avec filigrane' : ''}`;
    const av = $('#export-avert');
    av.hidden = !r.avertissements.length;
    av.textContent = r.avertissements.join(' ');
    $('#export-progres').hidden = true;
    $('#export-fini').hidden = false;
  } catch (e) {
    $('#export-progres').hidden = true;
    $('#export-reglages').hidden = false;
    if (e && e.name === 'AbortError') toast('Export annulé');
    else { $('#export-infos').textContent = `L'export a échoué : ${e && e.message ? e.message : e}`; console.error(e); }
  } finally {
    app.exportEnCours = null;
  }
}

// ====================================================================== branchements
function brancher() {
  $('#btn-nouveau').addEventListener('click', nouveauProjet);
  $('#liste-projets').addEventListener('click', (e) => {
    const b = e.target.closest('[data-action]');
    const carte = e.target.closest('[data-id]');
    if (!b || !carte) return;
    const id = carte.dataset.id;
    if (b.dataset.action === 'ouvrir') ouvrir(id);
    else if (b.dataset.action === 'supprimer') supprimerProjet(id);
    else if (b.dataset.action === 'dupliquer') dupliquerProjet(id);
  });
  $('#btn-retour').addEventListener('click', () => afficherAccueil());
  window.addEventListener('popstate', () => {
    const id = location.hash.slice(1);
    if (id && (!app.p || app.p.id !== id)) ouvrir(id, true);
    else if (!id && app.p) afficherAccueil(true);
  });
  $('#nom-projet').addEventListener('change', (e) => {
    app.p.nom = e.target.value.trim() || 'Sans titre';
    e.target.value = app.p.nom;
    document.title = `${app.p.nom} · LA BOBINE`;
    if (!app.selection) rendreInspecteur();
    sauverBientot();
  });
  $('#btn-annuler').addEventListener('click', annuler);
  $('#btn-retablir').addEventListener('click', retablir);
  $('#btn-diviser').addEventListener('click', diviserIci);
  $('#btn-supprimer').addEventListener('click', supprimerSelection);
  $('#btn-dupliquer').addEventListener('click', dupliquerSelection);
  $('#btn-zoom').addEventListener('click', () => app.frise.zoomer(app.frise.pps * 1.4));
  $('#btn-dezoom').addEventListener('click', () => app.frise.zoomer(app.frise.pps / 1.4));
  $('#btn-lecture').addEventListener('click', () => app.lecteur.basculer());
  $('#btn-exporter').addEventListener('click', ouvrirExport);

  $('#btn-importer').addEventListener('click', () => $('#entree-fichiers').click());
  $('#btn-importer-son').addEventListener('click', () => $('#entree-sons').click());
  $('#entree-fichiers').addEventListener('change', async (e) => { await importerFichiers(e.target.files); e.target.value = ''; });
  $('#entree-sons').addEventListener('change', async (e) => { await importerFichiers(e.target.files, { versSon: true }); e.target.value = ''; });
  $('#btn-voix').addEventListener('click', basculerVoix);
  $('#biblio').addEventListener('click', (e) => {
    const a = e.target.closest('[data-ajouter]');
    const s = e.target.closest('[data-superposer]');
    const st = e.target.closest('[data-style]');
    const onglet = e.target.closest('[data-onglet]');
    if (a) ajouterMedia(a.dataset.ajouter, 'principale');
    else if (s) ajouterMedia(s.dataset.superposer, 'superposer');
    else if (st) ajouterTexte(st.dataset.style);
    else if (onglet) choisirOnglet(onglet.dataset.onglet);
  });

  const corps = $('#corps-inspecteur');
  corps.addEventListener('pointerdown', (e) => { if (e.target.closest('input, select, textarea')) noterUneFois(); }, true);
  corps.addEventListener('focusin', (e) => { if (e.target.matches('textarea, input[type="text"], input[type="number"]')) noterUneFois(); });
  corps.addEventListener('input', surChamp);
  corps.addEventListener('change', (e) => { surChamp(e); app.editionNotee = false; });
  corps.addEventListener('click', surBoutonInspecteur);

  for (const b of $$('.barre-mobile [data-feuille]')) {
    b.addEventListener('click', () => {
      const ouvert = $(`#${b.dataset.feuille}`).classList.contains('ouvert') && b.getAttribute('aria-expanded') === 'true';
      if (ouvert) fermerFeuilles(); else ouvrirFeuille(b.dataset.feuille, b.dataset.ongletCible);
    });
  }
  for (const b of $$('[data-fermer]')) b.addEventListener('click', fermerFeuilles);
  $('.scene').addEventListener('pointerdown', (e) => { if (estMobile() && !e.target.closest('#toile')) fermerFeuilles(); });

  $('#dlg-export').addEventListener('change', (e) => { if (e.target.name === 'qualite') majInfosExport(); });
  $('#export-lancer').addEventListener('click', lancerExport);
  $('#export-fermer').addEventListener('click', () => $('#dlg-export').close());
  $('#export-retour').addEventListener('click', () => $('#dlg-export').close());
  $('#export-annuler').addEventListener('click', () => { if (app.exportEnCours) app.exportEnCours.abort(); });
  $('#dlg-export').addEventListener('cancel', (e) => { if (app.exportEnCours) e.preventDefault(); });

  document.addEventListener('keydown', (e) => {
    if ($('#editeur').hidden || !app.p) return;
    if (e.target.closest && e.target.closest('input, textarea, select, [contenteditable="true"]')) return;
    if (document.querySelector('dialog[open]')) return;
    const mod = e.ctrlKey || e.metaKey;
    const k = e.key.toLowerCase();
    if (e.code === 'Space') { e.preventDefault(); app.lecteur.basculer(); }
    else if (mod && k === 'z') { e.preventDefault(); if (e.shiftKey) retablir(); else annuler(); }
    else if (mod && k === 'y') { e.preventDefault(); retablir(); }
    else if (mod && k === 'd') { e.preventDefault(); dupliquerSelection(); }
    else if (k === 'delete' || k === 'backspace') { e.preventDefault(); supprimerSelection(); }
    else if (k === 's' && !mod) { e.preventDefault(); diviserIci(); }
    else if (k === 'arrowleft' || k === 'arrowright') {
      e.preventDefault();
      const pas = e.shiftKey ? 1 : 1 / app.p.fps;
      allerA(M.clamp(app.lecteur.t + (k === 'arrowleft' ? -pas : pas), 0, M.dureeProjet(app.p)));
    } else if (k === '+' || k === '=') app.frise.zoomer(app.frise.pps * 1.4);
    else if (k === '-') app.frise.zoomer(app.frise.pps / 1.4);
    else if (k === 'escape') selectionner(null);
  });

  let profondeur = 0;
  const avecFichiers = (e) => e.dataTransfer && [...e.dataTransfer.types].includes('Files');
  window.addEventListener('dragenter', (e) => { if (!app.p || !avecFichiers(e)) return; profondeur += 1; $('#depot-global').hidden = false; });
  window.addEventListener('dragleave', () => { profondeur = Math.max(0, profondeur - 1); if (!profondeur) $('#depot-global').hidden = true; });
  window.addEventListener('dragover', (e) => { if (avecFichiers(e)) e.preventDefault(); });
  window.addEventListener('drop', (e) => {
    if (!avecFichiers(e)) return;
    e.preventDefault();
    profondeur = 0;
    $('#depot-global').hidden = true;
    if (app.p) importerFichiers(e.dataTransfer.files);
  });
  window.addEventListener('beforeunload', () => { if (app.p) sauver(); });
  new ResizeObserver(() => { dimensionnerToile(); if (app.p) app.lecteur.afficher(); }).observe($('#cadre-toile'));
  ecouterToile();
}

// ====================================================================== démarrage
async function demarrer() {
  app.lecteur = new Lecteur($('#toile'), {
    temps: (t) => { app.frise.majTemps(t); majTemps(t); },
    etat: (joue) => $('#editeur').classList.toggle('en-lecture', joue),
  });
  app.frise = new Frise(app);
  rendreStyles();
  brancher();
  chargerPolices();
  S.demanderPersistance();
  const id = location.hash.slice(1);
  if (id) await ouvrir(id, true);
  else await afficherAccueil(true);
}

demarrer().catch((e) => {
  console.error(e);
  document.body.insertAdjacentHTML('afterbegin', `<p style="padding:16px;background:#ff5a4e;color:#fff">LA BOBINE n'a pas pu démarrer : ${esc(e.message)}</p>`);
});

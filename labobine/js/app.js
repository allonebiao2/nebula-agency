// LA BOBINE · le chef d'orchestre : accueil, éditeur, bibliothèque, réglages, export.

import * as M from './model.js';
import * as S from './stock.js';
import { importer, formeOnde } from './medias.js';
import { Lecteur } from './lecteur.js';
import { Frise } from './frise.js';
import { exporter, exporterGif, exporterSon, aDuSon, dimensionsSortie, sonDuClip, TAILLES_GIF, CADENCES_GIF } from './export.js';
import { chargerVision, chercherVisages, clesSuiviVisage, iaPrete } from './ia.js';
import { reduireBruit, versWav, VOLUMES } from './audio.js';
import { chargerTranscription, versMono16k, transcrire, legendes, MODELES } from './soustitres.js';
import { FILTRES, dessinerImage, dessinerSticker } from './rendu.js';
import { STICKERS, AVEC_TEXTE } from './stickers.js';
import { EFFETS, appliquerEffet } from './effets.js';
import { detecterRythme } from './rythme.js';
import { inverserVideo } from './inverser.js';
import { chargerLut } from './lut.js';
import { OFFRES, estPro } from './offre.js';
import * as C from './compte.js';

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
app.ia = { iaPrete };

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
  fabriquerVignettes();
  rendreOutils();
  if (app.p) app.lecteur.afficher();
}

// ====================================================================== vignettes des stickers et des effets
// Elles sont dessinées par le moteur lui-même : ce qu'on voit dans la bibliothèque est ce qui sortira.
const vignettes = { stickers: {}, effets: {} };
app.vignettes = vignettes;
function sceneEssai(o, W, H) {
  o.save();
  o.setTransform(1, 0, 0, 1, 0, 0);
  o.globalAlpha = 1;
  o.globalCompositeOperation = 'source-over';
  const g = o.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#2b4f7a');
  g.addColorStop(0.62, '#e8a05a');
  g.addColorStop(1, '#3a2414');
  o.fillStyle = g;
  o.fillRect(0, 0, W, H);
  o.fillStyle = '#ffd23f';
  o.beginPath(); o.arc(W * 0.66, H * 0.5, W * 0.14, 0, Math.PI * 2); o.fill();
  o.fillStyle = '#1d140c';
  o.beginPath(); o.moveTo(0, H); o.lineTo(0, H * 0.7); o.quadraticCurveTo(W * 0.3, H * 0.56, W * 0.55, H * 0.72); o.quadraticCurveTo(W * 0.8, H * 0.86, W, H * 0.7); o.lineTo(W, H); o.fill();
  o.fillStyle = '#f3ece1';
  o.fillRect(W * 0.22, H * 0.46, W * 0.06, H * 0.26);
  o.beginPath(); o.arc(W * 0.25, H * 0.42, W * 0.05, 0, Math.PI * 2); o.fill();
  o.restore();
}
function fabriquerVignettes() {
  const cv = document.createElement('canvas');
  cv.width = 120;
  cv.height = 120;
  const o = cv.getContext('2d', { willReadFrequently: true });
  for (const [k, st] of Object.entries(STICKERS)) {
    o.setTransform(1, 0, 0, 1, 0, 0);
    o.fillStyle = '#211c17';
    o.fillRect(0, 0, 120, 120);
    const c = M.clipSticker(0, k, { couleur: st.couleur, couleur2: st.couleur2, texte: st.texte || '', echelle: 0.78, animEntree: { type: 'aucune', duree: 0.5 } });
    dessinerSticker(o, c, 0.5, 120, 120);
    vignettes.stickers[k] = cv.toDataURL('image/png');
  }
  for (const k of Object.keys(EFFETS)) {
    sceneEssai(o, 120, 120);
    appliquerEffet(o, { effet: k, debut: 0, duree: 3, intensite: 1 }, 1.03, 120, 120, []);
    vignettes.effets[k] = cv.toDataURL('image/jpeg', 0.82);
  }
}
const tuile = (attr, k, nom, img, presse) => `<button class="vignette-outil" ${attr}="${k}"${presse === undefined ? '' : ` aria-pressed="${presse}"`} type="button"><img src="${img || ''}" alt="">${esc(nom)}</button>`;
function rendreOutils() {
  $('#grille-stickers').innerHTML = Object.entries(STICKERS).map(([k, st]) => tuile('data-sticker', k, st.nom, vignettes.stickers[k])).join('');
  $('#grille-effets').innerHTML = Object.entries(EFFETS).map(([k, e]) => tuile('data-effet', k, e.nom, vignettes.effets[k])).join('');
  if (app.p && app.selection) { const f = M.trouver(app.p, app.selection); if (f && (f.clip.genre === 'sticker' || f.clip.genre === 'effet')) rendreInspecteur(); }
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
  let nuage = [];
  if (C.OUVERT && C.connecte()) {
    try { const locaux = new Set(projets.map((p) => p.id)); nuage = ((await C.nuageLister()) || []).filter((x) => !locaux.has(x.id)); } catch { nuage = []; }
  }
  if (!projets.length && !nuage.length) {
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
    </article>`).join('') + nuage.map((x) => `
    <article class="carte-projet" data-id="${esc(x.id)}">
      <div class="apercu">Dans le nuage</div><span class="badge-nuage">Nuage</span>
      <div class="nom">${esc(x.nom)}</div><div class="meta">${dateCourte(new Date(x.modifie_le).getTime())}</div>
      <button class="ouvrir" data-action="ouvrir-nuage" aria-label="Ouvrir ${esc(x.nom)} depuis le nuage"></button>
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
    if (C.OUVERT && C.connecte()) C.nuageSupprimer(id).catch(() => {});
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
  M.completerProjet(p);
  app.p = p;
  app.medias = new Map();
  for (const mid of p.medias) {
    const m = await S.lireMedia(mid);
    if (m) app.medias.set(mid, m);
  }
  app.manquants = p.medias.filter((id) => !app.medias.has(id));
  app.historique = new M.Historique();
  app.selection = null;
  if (p.pistes.some((t) => t.clips.some((c) => c.detourage))) chargerVision().then(() => app.lecteur.afficher()).catch(() => {});
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
  if (app.manquants.length) toast(`${app.manquants.length} média(s) sont restés sur un autre appareil : importe-les ici, ils se rebrancheront tout seuls par leur nom.`, null, null, 9000);
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
  if (app.p) suivreAnimations();
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
    p.mediasInfo = Object.fromEntries(p.medias.map((id) => app.medias.get(id)).filter(Boolean)
      .map((x) => [x.id, { nom: x.nom, type: x.type, duree: x.duree, l: x.l, h: x.h }]));
    await S.ecrireProjet(p);
    if (app.p === p) $('#etat-sauve').textContent = 'Enregistré';
    if (C.OUVERT && C.connecte()) versNuage(p);
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
      // un média resté sur un autre appareil se rebranche par son nom : les clips le retrouvent
      const info = app.p.mediasInfo || {};
      const absent = Object.keys(info).find((id) => !app.medias.has(id) && info[id].nom === m.nom && info[id].type === m.type);
      if (absent) m.id = absent;
      await S.ecrireMedia(m);
      app.medias.set(m.id, m);
      if (!app.p.medias.includes(m.id)) app.p.medias.push(m.id);
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

function ajouterSticker(forme) {
  const st = STICKERS[forme];
  if (!st || !app.p) return;
  const c = M.clipSticker(app.lecteur.t, forme, { couleur: st.couleur, couleur2: st.couleur2, texte: st.texte || '' });
  modifier((p) => M.poserSurPisteLibre(p, 'sticker', c));
  selectionner(c.id);
  if (estMobile()) fermerFeuilles();
}

function ajouterEffet(effet) {
  if (!EFFETS[effet] || !app.p) return;
  const t = app.lecteur.t;
  const c = M.clipEffet(t, effet);
  // posé sur un clip de la piste principale, l'effet en prend la fin
  const sous = M.principale(app.p).clips.find((x) => t >= x.debut - 1e-6 && t < M.finClip(x) - 1e-6);
  if (sous && M.finClip(sous) - t >= 1) c.duree = M.finClip(sous) - t;
  modifier((p) => M.poserSurPisteLibre(p, 'effet', c));
  selectionner(c.id);
  if (estMobile()) fermerFeuilles();
}

/** Pose un marqueur de rythme à la tête de lecture, ou retire celui qui s'y trouve. */
function marqueurIci() {
  if (!app.p) return;
  let pose = false;
  modifier((p) => { pose = M.basculerMarqueur(p, app.lecteur.t); });
  toast(pose ? 'Marqueur posé : les clips s\'y aimantent' : 'Marqueur retiré', null, null, 2200);
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
  const visuels = medias.filter((m) => m.type === 'video' || m.type === 'image');
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
const FERMES_PAR_DEFAUT = ['Animations', 'Fondus', 'Recadrage', 'Fond vert', 'Masque'];
app.fermes = new Set(FERMES_PAR_DEFAUT);
const ANIMABLE = (c, k) => (c.genre === 'texte' ? M.ANIMABLES_TEXTE : c.genre === 'effet' || c.genre === 'audio' ? [] : M.ANIMABLES_MEDIA).includes(k);
function etatCle(c, k) {
  const lt = app.lecteur.t - c.debut;
  return M.cleIci(c, k, lt) ? 'ici' : M.estAnime(c, k) ? 'anime' : 'libre';
}
const curseur = (k, label, val, min, max, pas, format, c = null) => {
  const cle = c && ANIMABLE(c, k);
  const v = cle ? M.valeur(c, k, app.lecteur.t) : val;
  return `<label class="champ${cle ? ' avec-cle' : ''}"><span>${label}</span><input type="range" data-k="${k}" min="${min}" max="${max}" step="${pas}" value="${v}" data-format="${format}"><output>${formatValeur(format, v)}</output>${cle ? `<button type="button" class="cle ${etatCle(c, k)}" data-cle="${k}" aria-label="Image clé : ${label}" title="Poser ou retirer une image clé ici"></button>` : ''}</label>`;
};
const choix = (k, label, val, options) => `<label class="champ plein"><span>${label}</span><select data-k="${k}">${options.map(([v, t]) => `<option value="${v}"${v === val ? ' selected' : ''}>${t}</option>`).join('')}</select></label>`;
const coche = (k, label, val) => `<label class="interrupteur"><input type="checkbox" data-k="${k}"${val ? ' checked' : ''}><span>${label}</span></label>`;
const couleur = (k, label, val, palette = PALETTE) => `<div class="champ plein"><span>${label}</span><span class="couleurs"><input type="color" data-k="${k}" value="${val}" aria-label="${label}">${palette.map((c) => `<button class="pastille" data-pastille="${c}" data-pour="${k}" style="background:${c}" aria-label="Couleur ${c}"></button>`).join('')}</span></div>`;
const groupe = (titre, html, id = '') => `<details class="groupe-insp"${id ? ` id="insp-${id}"` : ''}${app.fermes.has(titre) ? '' : ' open'}><summary>${titre}</summary><div class="groupe-corps">${html}</div></details>`;
const puces = (action, val, options) => `<div class="puces">${options.map(([v, t]) => `<button data-action="${action}" data-v="${v}" aria-pressed="${String(v) === String(val)}">${t}</button>`).join('')}</div>`;
const bouton = (action, texte) => `<button class="btn petit" data-action="${action}">${texte}</button>`;
const FAMILLES = { texte: 'texte', sticker: 'sticker', effet: 'effet', audio: null };
const famille = (c) => (c.genre in FAMILLES ? FAMILLES[c.genre] : 'media');
const CALER = [[1, 'Chaque temps'], [2, 'Tous les 2 temps'], [4, 'Tous les 4 temps']];

function groupeRythme(p) {
  const pts = M.pointsDeRythme(p);
  return groupe('Rythme', `<p class="note">${pts.length ? `${pts.length} temps sur la frise.` : 'Aucun temps marqué.'} La touche M (ou « Marqueur ») en pose un à la tête de lecture ; sur un son, « Trouver le rythme » les pose tout seul.</p>`
    + (pts.length >= 2 ? `<p class="note">Caler la piste principale : chaque photo dure le nombre de temps choisi, chaque vidéo s'arrête sur un temps.</p>${puces('caler', null, CALER)}` : '')
    + ((p.marqueurs || []).length ? `<div class="actions-insp">${bouton('effacer-marqueurs', 'Effacer les marqueurs')}</div>` : ''));
}

/** La LUT d'un clip : celle qu'il porte, celles déjà importées dans le projet, ou une nouvelle. */
function blocLut(c) {
  const luts = app.p.medias.map((id) => app.medias.get(id)).filter((m) => m && m.type === 'lut');
  const lut = c.lut && c.lut.media && app.medias.get(c.lut.media);
  let h = '<p class="note"><b>LUT 3D</b> · l\'étalonnage d\'un logiciel pro, au format .cube.</p>';
  if (lut) h += `<p class="note">Appliquée : ${esc(lut.nom)}</p>${curseur('lut.intensite', 'Intensité', c.lut.intensite ?? 1, 0, 1, 0.01, 'pct')}`;
  const autres = luts.filter((m) => !lut || m.id !== lut.id);
  if (autres.length) h += `<div class="puces">${autres.map((m) => `<button data-action="lut" data-v="${m.id}">${esc(m.nom.replace(/\.cube$/i, ''))}</button>`).join('')}</div>`;
  h += `<div class="actions-insp">${bouton('importer-lut', 'Importer une LUT (.cube)')}${lut ? bouton('retirer-lut', 'Retirer la LUT') : ''}</div>`;
  return h;
}

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
      + groupe('Montage', `<p class="note">${M.formatTemps(M.dureeProjet(p))} au total, ${p.pistes.reduce((n, t) => n + t.clips.length, 0)} clip(s). Touche un clip de la frise pour le régler.</p>`)
      + groupeRythme(p);
    return;
  }
  const c = f.clip;
  const surPrincipale = f.piste.genre === 'principale';
  const fam = famille(c);
  const collable = app.pressePapier && app.pressePapier.fam === fam;
  const presse = fam ? bouton('copier', 'Copier les réglages') + (collable ? bouton('coller', 'Coller les réglages') : '') : '';
  let h = '';
  if (c.genre === 'video' || c.genre === 'image') {
    $('#titre-inspecteur').textContent = c.genre === 'video' ? 'Vidéo' : 'Photo';
    h += groupe('Clip', `<div class="actions-insp">${bouton('basculer', surPrincipale ? 'Passer en superposition' : 'Remettre sur la piste principale')}`
      + `${c.genre === 'video' && surPrincipale ? bouton('figer', "Figer l'image") : ''}${c.genre === 'video' && !c.muet ? bouton('detacher', 'Détacher le son') : ''}`
      + `${c.genre === 'video' ? bouton('inverser', c.inverse ? "Remettre à l'endroit" : "Lire à l'envers") : ''}`
      + `${bouton('remplacer', 'Remplacer le média')}${presse}</div>`);
    h += groupe("IA sur l'appareil", coche('detourage', 'Détourer la personne (le décor disparaît)', c.detourage)
      + `<div class="actions-insp">${c.genre === 'video' ? bouton('suivre-visages', 'Cadrer sur les visages') : ''}${c.genre === 'video' && !c.muet ? bouton('debruiter', 'Réduire le bruit') + bouton('sous-titres', 'Sous-titres automatiques') : ''}</div>`
      + "<p class=\"note\">Calculé sur ton appareil : rien n'est envoyé. La première fois, le moteur (14 Mo) se télécharge.</p>");
    if (c.genre === 'video') {
      h += groupe('Vitesse', curseur('vitesse', 'Vitesse', c.vitesse, M.VITESSE_MIN, M.VITESSE_MAX, 0.05, 'x')
        + puces('vitesse', c.vitesse, [[0.5, '0,5×'], [1, '1×'], [1.5, '1,5×'], [2, '2×'], [3, '3×']])
        + coche('garderTon', 'Garder le ton de la voix', c.garderTon !== false));
      h += groupe('Son', curseur('volume', 'Volume', c.volume, 0, 2, 0.01, 'pct') + coche('muet', 'Couper le son de ce clip', c.muet));
    }
    h += groupe('Position et taille', choix('ajustement', 'Cadrage', c.ajustement, [['adapter', 'Adapter (tout voir)'], ['remplir', "Remplir l'écran"]])
      + curseur('echelle', 'Taille', c.echelle, 0.1, 3, 0.01, 'pct', c)
      + curseur('cx', 'Position X', c.cx, 0, 1, 0.005, 'pct', c)
      + curseur('cy', 'Position Y', c.cy, 0, 1, 0.005, 'pct', c)
      + curseur('rotation', 'Rotation', c.rotation, -180, 180, 1, 'deg', c)
      + curseur('opacite', 'Opacité', c.opacite, 0, 1, 0.01, 'pct', c)
      + coche('miroirH', 'Miroir horizontal', c.miroirH) + coche('miroirV', 'Miroir vertical', c.miroirV)
      + choix('fusion', 'Fusion', c.fusion, M.FUSIONS)
      + choix('mouvement', 'Zoom lent', c.mouvement, M.MOUVEMENTS)
      + '<p class="note">Le losange pose une image clé à la tête de lecture : le réglage s\'anime d\'une clé à l\'autre. Sur l\'aperçu, glisse pour déplacer, pince ou molette pour agrandir.</p>');
    const vig = (app.medias.get(c.media) || {}).vignette || '';
    h += groupe('Couleur', `<div class="filtres">${Object.entries(FILTRES).map(([k, x]) => `<button class="filtre" data-action="filtre" data-v="${k}" aria-pressed="${k === c.filtre.nom}"><span class="vig" style="background-image:url('${vig}');filter:${x.css ? x.css(1) : 'none'}"></span><span>${x.nom}</span></button>`).join('')}</div>`
      + (c.filtre.nom !== 'aucun' ? curseur('filtre.intensite', 'Intensité', c.filtre.intensite, 0, 1, 0.01, 'pct') : '')
      + curseur('reglages.luminosite', 'Luminosité', c.reglages.luminosite, -1, 1, 0.01, 'pct')
      + curseur('reglages.contraste', 'Contraste', c.reglages.contraste, -1, 1, 0.01, 'pct')
      + curseur('reglages.saturation', 'Saturation', c.reglages.saturation, -1, 1, 0.01, 'pct')
      + curseur('reglages.temperature', 'Température', c.reglages.temperature, -1, 1, 0.01, 'pct')
      + `<div class="actions-insp">${bouton('reinit-couleur', 'Remettre les couleurs d\'origine')}</div>`
      + blocLut(c));
    h += groupe('Animations', choix('animEntree.type', 'Entrée', c.animEntree.type, M.ANIMS_CLIP)
      + curseur('animEntree.duree', "Durée d'entrée", c.animEntree.duree, 0.1, 3, 0.05, 's')
      + choix('animSortie.type', 'Sortie', c.animSortie.type, M.ANIMS_CLIP)
      + curseur('animSortie.duree', 'Durée de sortie', c.animSortie.duree, 0.1, 3, 0.05, 's'));
    h += groupe('Fondus', curseur('fonduEntree', 'Entrée', c.fonduEntree, 0, 3, 0.1, 's') + curseur('fonduSortie', 'Sortie', c.fonduSortie, 0, 3, 0.1, 's'));
    if (surPrincipale && f.index > 0) {
      h += groupe('Transition depuis le clip précédent', choix('transition.type', 'Effet', c.transition.type, M.TRANSITIONS)
        + curseur('transition.duree', 'Durée', c.transition.duree, 0.1, 2, 0.05, 's'), 'transition');
    }
    h += groupe('Recadrage', curseur('recadrage.g', 'Gauche', c.recadrage.g, 0, 0.45, 0.005, 'pct') + curseur('recadrage.d', 'Droite', c.recadrage.d, 0, 0.45, 0.005, 'pct')
      + curseur('recadrage.h', 'Haut', c.recadrage.h, 0, 0.45, 0.005, 'pct') + curseur('recadrage.b', 'Bas', c.recadrage.b, 0, 0.45, 0.005, 'pct'));
    h += groupe('Fond vert', coche('chroma.actif', 'Rendre transparente une couleur', c.chroma.actif)
      + couleur('chroma.couleur', 'Couleur à retirer', c.chroma.couleur, ['#00d000', '#00b140', '#0047bb', '#ffffff', '#000000'])
      + curseur('chroma.seuil', 'Seuil', c.chroma.seuil, 0, 0.6, 0.005, 'pct') + curseur('chroma.douceur', 'Douceur du bord', c.chroma.douceur, 0, 0.4, 0.005, 'pct'));
    h += groupe('Masque', choix('masque.forme', 'Forme', c.masque.forme, M.MASQUES)
      + curseur('masque.taille', 'Taille', c.masque.taille, 0.05, 1.5, 0.01, 'pct') + curseur('masque.adoucir', 'Adoucir', c.masque.adoucir, 0, 1, 0.01, 'pct')
      + coche('masque.inverser', 'Inverser le masque', c.masque.inverser));
  } else if (c.genre === 'sticker') {
    $('#titre-inspecteur').textContent = 'Sticker';
    h += groupe('Sticker', `<div class="grille-vignettes petite">${Object.entries(STICKERS).map(([k, st]) => tuile('data-forme', k, st.nom, vignettes.stickers[k], k === c.forme)).join('')}</div>`
      + (AVEC_TEXTE.has(c.forme) ? `<label class="champ plein"><span>${c.forme === 'emoji' ? 'Émoji' : 'Texte'}</span><input type="text" data-k="texte" value="${esc(c.texte)}" maxlength="40"></label>` : '')
      + couleur('couleur', 'Couleur', c.couleur) + couleur('couleur2', c.forme === 'emoji' ? 'Second ton' : 'Contour et texte', c.couleur2)
      + (presse ? `<div class="actions-insp">${presse}</div>` : ''));
    h += groupe('Mouvement', choix('boucle', 'En boucle', c.boucle, M.BOUCLES)
      + choix('animEntree.type', 'Entrée', c.animEntree.type, M.ANIMS_CLIP) + curseur('animEntree.duree', "Durée d'entrée", c.animEntree.duree, 0.1, 3, 0.05, 's')
      + choix('animSortie.type', 'Sortie', c.animSortie.type, M.ANIMS_CLIP) + curseur('animSortie.duree', 'Durée de sortie', c.animSortie.duree, 0.1, 3, 0.05, 's')
      + `<label class="champ"><span>Durée</span><input type="number" data-k="duree" min="0.1" max="600" step="0.1" value="${c.duree.toFixed(1)}"><output>s</output></label>`);
    h += groupe('Position et taille', curseur('echelle', 'Taille', c.echelle, 0.05, 1.5, 0.01, 'pct', c)
      + curseur('cx', 'Position X', c.cx, 0, 1, 0.005, 'pct', c) + curseur('cy', 'Position Y', c.cy, 0, 1, 0.005, 'pct', c)
      + curseur('rotation', 'Rotation', c.rotation || 0, -180, 180, 1, 'deg', c) + curseur('opacite', 'Opacité', c.opacite, 0, 1, 0.01, 'pct', c)
      + '<p class="note">Sur l\'aperçu : glisse pour déplacer, pince ou molette pour agrandir. Le losange pose une image clé.</p>');
  } else if (c.genre === 'effet') {
    $('#titre-inspecteur').textContent = 'Effet';
    const bat = c.effet === 'battement' || c.effet === 'flash';
    h += groupe('Effet', `<div class="grille-vignettes petite">${Object.entries(EFFETS).map(([k, e]) => tuile('data-change-effet', k, e.nom, vignettes.effets[k], k === c.effet)).join('')}</div>`
      + curseur('intensite', 'Intensité', c.intensite ?? 1, 0, 1.5, 0.01, 'pct')
      + `<label class="champ"><span>Durée</span><input type="number" data-k="duree" min="0.1" max="600" step="0.1" value="${c.duree.toFixed(1)}"><output>s</output></label>`
      + (bat ? `<p class="note">${M.pointsDeRythme(app.p).length ? 'Il bat sur les temps marqués de la frise.' : 'Aucun rythme marqué : il bat à 120 BPM. Marque le rythme d\'une musique pour qu\'il la suive.'}</p>` : '')
      + (presse ? `<div class="actions-insp">${presse}</div>` : ''));
  } else if (c.genre === 'texte') {
    $('#titre-inspecteur').textContent = 'Texte';
    h += groupe('Texte', `<textarea data-k="texte" aria-label="Texte" rows="3">${esc(c.texte)}</textarea>`
      + `<div class="puces">${Object.entries(M.STYLES_TEXTE).map(([k, s]) => `<button data-action="style" data-v="${k}">${esc(s.nom)}</button>`).join('')}</div>`
      + (presse ? `<div class="actions-insp">${presse}</div>` : ''));
    h += groupe('Police', choix('police', 'Police', c.police, M.POLICES.map((x) => [x.nom, x.titre]))
      + curseur('taille', 'Taille', c.taille, 0.02, 0.2, 0.002, 'pct', c)
      + couleur('couleur', 'Couleur', c.couleur)
      + puces('aligner', c.alignement, [['gauche', 'Gauche'], ['centre', 'Centre'], ['droite', 'Droite']]));
    h += groupe('Habillage', choix('boite', 'Fond', c.boite, [['aucune', 'Aucun'], ['bande', 'Bande sous chaque ligne'], ['pastille', 'Pastille']])
      + couleur('couleurBoite', 'Couleur du fond', c.couleurBoite)
      + coche('contour', 'Contour', c.contour) + couleur('couleurContour', 'Couleur du contour', c.couleurContour));
    h += groupe('Animation', choix('anim', 'Entrée', c.anim, M.ANIMS_TEXTE)
      + `<label class="champ"><span>Durée</span><input type="number" data-k="duree" min="0.1" max="600" step="0.1" value="${c.duree.toFixed(1)}"><output>s</output></label>`);
    h += groupe('Position', curseur('cx', 'Position X', c.cx, 0, 1, 0.005, 'pct', c) + curseur('cy', 'Position Y', c.cy, 0, 1, 0.005, 'pct', c)
      + curseur('rotation', 'Rotation', c.rotation || 0, -180, 180, 1, 'deg', c) + curseur('opacite', 'Opacité', c.opacite, 0, 1, 0.01, 'pct', c));
  } else {
    $('#titre-inspecteur').textContent = 'Son';
    h += groupe('Son', curseur('volume', 'Volume', c.volume, 0, 2, 0.01, 'pct') + coche('muet', 'Couper ce son', c.muet)
      + curseur('vitesse', 'Vitesse', c.vitesse, M.VITESSE_MIN, M.VITESSE_MAX, 0.05, 'x') + coche('garderTon', 'Garder le ton de la voix', c.garderTon !== false)
      + `<div class="actions-insp">${bouton('debruiter', 'Réduire le bruit')}${bouton('sous-titres', 'Sous-titres automatiques')}</div>`);
    h += groupe('Fondus', curseur('fonduEntree', 'Entrée', c.fonduEntree, 0, 5, 0.1, 's') + curseur('fonduSortie', 'Sortie', c.fonduSortie, 0, 5, 0.1, 's'));
    h += groupe('Rythme', Array.isArray(c.rythme)
      ? `<p class="note">${c.rythme.length} temps trouvés · ${Math.round(c.bpm || 0)} BPM. Les clips s'y aimantent quand tu les glisses.</p><p class="note">Caler la piste principale sur ce rythme :</p>${puces('caler', null, CALER)}<div class="actions-insp">${bouton('effacer-rythme', 'Effacer le rythme')}</div>`
      : `<div class="actions-insp">${bouton('rythme', 'Trouver le rythme')}</div><p class="note">Les temps de la musique se posent sur la frise, calculés sur ton appareil : les clips s'y aimantent, et chaque photo peut tomber pile sur un temps.</p>`);
  }
  h += groupe('Actions', `<div class="actions-insp">${bouton('diviser', 'Diviser ici')}${bouton('dupliquer', 'Dupliquer')}${bouton('supprimer', 'Supprimer')}</div>`);
  corps.innerHTML = h;
  if (section) { const s = $(`#insp-${section}`); if (s) { s.open = true; s.scrollIntoView({ block: 'start' }); } }
}

/** Pendant la lecture ou quand la tête bouge : les réglages animés suivent l'image. */
let dernierSuivi = 0;
function suivreAnimations(force = false) {
  const f = app.selection && M.trouver(app.p, app.selection);
  if (!f || !Object.keys(f.clip.cles || {}).length) return;
  if (!force && performance.now() - dernierSuivi < 120) return;
  dernierSuivi = performance.now();
  const c = f.clip;
  for (const el of $$('#corps-inspecteur input[type="range"][data-k]')) {
    const k = el.dataset.k;
    if (!ANIMABLE(c, k) || !M.estAnime(c, k) || document.activeElement === el) continue;
    const v = M.valeur(c, k, app.lecteur.t);
    el.value = v;
    const out = el.parentElement.querySelector('output');
    if (out) out.textContent = formatValeur(el.dataset.format, v);
  }
  for (const b of $$('#corps-inspecteur [data-cle]')) b.className = `cle ${etatCle(c, b.dataset.cle)}`;
}

function poserChemin(obj, chemin, v) {
  const parts = chemin.split('.');
  let o = obj;
  for (let i = 0; i < parts.length - 1; i += 1) { o[parts[i]] = o[parts[i]] || {}; o = o[parts[i]]; }
  o[parts[parts.length - 1]] = v;
}

/** Règle une valeur ; si elle est animée, c'est l'image clé sous la tête de lecture qui change. */
function reglerAnimable(c, k, v) {
  if (ANIMABLE(c, k) && M.estAnime(c, k)) M.poserCle(c, k, app.lecteur.t - c.debut, v);
  else c[k] = v;
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
  else if (k.startsWith('fond.')) poserChemin(app.p, k, v);
  else if (k === 'vitesse') { M.changerVitesse(app.p, c.id, v); structurel = true; }
  else if (k === 'transition.type' || k === 'transition.duree') { poserChemin(c, k, v); structurel = true; }
  else if (k === 'duree') { c.duree = Math.max(M.DUREE_MIN, v); structurel = true; }
  else if (k.includes('.')) poserChemin(c, k, v);
  else reglerAnimable(c, k, v);
  if (k === 'detourage' && v) chargerVision().then(() => app.lecteur.afficher()).catch(() => toast("Le moteur d'IA n'a pas pu se charger : vérifie ta connexion."));
  const out = el.closest('.champ') && el.closest('.champ').querySelector('output');
  if (out && el.dataset.format) out.textContent = formatValeur(el.dataset.format, v);
  if (structurel || k === 'texte' || k === 'muet' || k === 'volume' || (c && M.estAnime(c, k))) {
    M.tasserPrincipale(app.p);
    app.frise.rendre();
    majDuree();
  }
  if (structurel) app.lecteur.aller(app.lecteur.t); else app.lecteur.afficher();
  if (c && ANIMABLE(c, k)) suivreAnimations(true);
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
  const cle = e.target.closest('[data-cle]');
  const f = app.selection && M.trouver(app.p, app.selection);
  if (cle && f) {
    e.preventDefault();
    const c = f.clip;
    const k = cle.dataset.cle;
    const lt = app.lecteur.t - c.debut;
    if (lt < -1e-6 || lt > M.dureeClip(c) + 1e-6) { toast('Place la tête de lecture sur ce clip pour poser une image clé.'); return; }
    modifier(() => {
      if (M.cleIci(c, k, lt)) M.retirerCle(c, k, lt);
      else M.poserCle(c, k, lt, M.valeur(c, k, app.lecteur.t));
    });
    return;
  }
  const forme = e.target.closest('[data-forme]');
  if (forme && f && f.clip.genre === 'sticker') {
    const c = f.clip;
    const avant = STICKERS[c.forme];
    const apres = STICKERS[forme.dataset.forme];
    modifier(() => {
      if (!c.texte || (avant && c.texte === avant.texte)) c.texte = apres.texte || '';
      c.forme = forme.dataset.forme;
      c.couleur = apres.couleur;
      c.couleur2 = apres.couleur2;
    });
    return;
  }
  const chEffet = e.target.closest('[data-change-effet]');
  if (chEffet && f && f.clip.genre === 'effet') { modifier(() => { f.clip.effet = chEffet.dataset.changeEffet; }); return; }
  const b = e.target.closest('[data-action]');
  if (!b || !app.p) return;
  const v = b.dataset.v;
  const c = f && f.clip;
  switch (b.dataset.action) {
    case 'format': modifier((p) => M.changerFormat(p, v)); break;
    case 'basculer': modifier((p) => M.basculerSuperposition(p, app.selection)); selectionner(app.selection); break;
    case 'vitesse': modifier((p) => M.changerVitesse(p, app.selection, parseFloat(v))); break;
    case 'aligner': if (c) modifier(() => { c.alignement = v; }); break;
    case 'filtre': if (c) modifier(() => { c.filtre = { nom: v, intensite: c.filtre.intensite || 1 }; }); break;
    case 'reinit-couleur': if (c) modifier(() => { c.filtre = { nom: 'aucun', intensite: 1 }; c.reglages = { luminosite: 0, contraste: 0, saturation: 0, temperature: 0 }; }); break;
    case 'style': if (c) modifier(() => {
      const s = M.STYLES_TEXTE[v];
      Object.assign(c, { police: s.police, poids: s.poids, taille: s.taille, couleur: s.couleur, boite: s.boite, couleurBoite: s.couleurBoite || '#000000', contour: s.contour, couleurContour: s.couleurContour || '#000000', anim: s.anim });
    }); break;
    case 'figer': figerImage(); break;
    case 'inverser': inverser(); break;
    case 'rythme': trouverRythme(); break;
    case 'effacer-rythme': if (c) { modifier(() => { delete c.rythme; delete c.bpm; }); toast('Rythme effacé', 'Annuler', annuler); } break;
    case 'effacer-marqueurs': modifier((p) => { p.marqueurs = []; }); toast('Marqueurs effacés', 'Annuler', annuler); break;
    case 'caler': {
      let n = 0;
      modifier((p) => { n = M.calerSurRythme(p, parseInt(v, 10)); });
      toast(n ? `${n} clip(s) calé(s) sur le rythme` : 'Rien à caler : il faut des photos ou des vidéos sur la piste principale, et des temps marqués.', n ? 'Annuler' : null, annuler);
      break;
    }
    case 'importer-lut': app.aLut = app.selection; $('#entree-lut').click(); break;
    case 'lut': {
      const m = app.medias.get(v);
      if (c && m) chargerLut(m).then(() => modifier(() => { c.lut = { media: m.id, intensite: 1 }; })).catch((err) => toast(err.message));
      break;
    }
    case 'retirer-lut': if (c) modifier(() => { c.lut = { media: null, intensite: 1 }; }); break;
    case 'suivre-visages': suivreVisages(); break;
    case 'debruiter': debruiter(); break;
    case 'sous-titres': sousTitres(); break;
    case 'detacher': {
      let son = null;
      modifier((p) => { son = M.detacherSon(p, app.selection); });
      if (son) { selectionner(son.id); toast('Son détaché sur sa propre piste'); calculerOnde(son.media); }
      break;
    }
    case 'remplacer': app.aRemplacer = app.selection; $('#entree-remplacer').click(); break;
    case 'copier': {
      const fam = famille(c);
      if (!fam) break;
      app.pressePapier = { fam, valeurs: JSON.parse(JSON.stringify(Object.fromEntries(M.COPIABLES[fam].map((k) => [k, c[k]])))) };
      toast('Réglages copiés : sélectionne un autre clip et colle-les');
      rendreInspecteur();
      break;
    }
    case 'coller': if (c && app.pressePapier) { modifier(() => Object.assign(c, JSON.parse(JSON.stringify(app.pressePapier.valeurs)))); toast('Réglages collés'); } break;
    case 'diviser': diviserIci(); break;
    case 'dupliquer': dupliquerSelection(); break;
    case 'supprimer': supprimerSelection(); break;
    default:
  }
}

// ====================================================================== actions sur les clips
async function figerImage() {
  const f = app.selection && M.trouver(app.p, app.selection);
  if (!f || f.clip.genre !== 'video' || f.piste.genre !== 'principale') return;
  const c = f.clip;
  const t = app.lecteur.t;
  if (t < c.debut - 1e-6 || t >= M.finClip(c)) { toast('Place la tête de lecture sur la vidéo à figer.'); return; }
  app.lecteur.pause();
  await app.lecteur.aller(t);
  const el = app.lecteur._el(c);
  if (!el || el.readyState < 2 || !el.videoWidth) { toast("L'image n'est pas encore prête : réessaie dans une seconde."); return; }
  const cv = document.createElement('canvas');
  cv.width = el.videoWidth;
  cv.height = el.videoHeight;
  cv.getContext('2d').drawImage(el, 0, 0);
  const blob = await new Promise((ok) => cv.toBlob(ok, 'image/jpeg', 0.92));
  const m = await importer(new File([blob], `Image figée ${M.formatTemps(t)}.jpg`, { type: 'image/jpeg' }));
  await S.ecrireMedia(m);
  app.medias.set(m.id, m);
  app.p.medias.push(m.id);
  let img = null;
  modifier((p) => {
    const auDebut = t <= c.debut + M.DUREE_MIN;
    if (!auDebut && t < M.finClip(c) - M.DUREE_MIN) M.diviser(p, c.id, t);
    img = M.clipDepuisMedia(m, 0);
    for (const k of ['ajustement', 'echelle', 'cx', 'cy', 'rotation', 'reglages', 'filtre', 'recadrage', 'miroirH', 'miroirV']) img[k] = JSON.parse(JSON.stringify(c[k]));
    const pr = M.principale(p);
    const i = pr.clips.findIndex((x) => x.id === c.id);
    pr.clips.splice(auDebut ? i : i + 1, 0, img);
    let d = 0;
    for (const x of pr.clips) { x.debut = d; d += M.dureeClip(x); }
  });
  if (img) selectionner(img.id);
  rendreBiblio();
  toast('Image figée : 3 secondes ajoutées');
}

/** Trouve les temps d'une musique (calculé sur l'appareil) et les range sur le clip son, en secondes du fichier. */
async function trouverRythme() {
  const f = app.selection && M.trouver(app.p, app.selection);
  if (!f || f.clip.genre !== 'audio') return;
  const c = f.clip;
  const m = app.medias.get(c.media);
  if (!m) return;
  toast('Écoute du rythme…', null, null, 120000);
  await new Promise((ok) => setTimeout(ok, 30));
  try {
    const ext = await sonDuClip(m, { entree: 0, sortie: m.duree });
    const r = ext ? detecterRythme(ext.canaux, ext.sr) : null;
    app.dernierRythme = r || { erreur: 'aucun rythme' };
    if (!r) { toast('Pas de rythme lisible dans ce son : pose des marqueurs à la main (touche M).'); return; }
    modifier(() => { c.rythme = r.temps; c.bpm = r.bpm; });
    toast(`${r.temps.length} temps trouvés · ${Math.round(r.bpm)} BPM`);
  } catch (e) {
    app.dernierRythme = { erreur: e.message };
    toast(`Le rythme n'a pas pu être trouvé : ${e.message}`);
  }
}

/** Lire une vidéo à l'envers : le passage utilisé devient un nouveau média, l'original est gardé pour revenir. */
async function inverser() {
  const f = app.selection && M.trouver(app.p, app.selection);
  if (!f || f.clip.genre !== 'video') return;
  const c = f.clip;
  if (c.inverse) {
    modifier(() => { const inv = c.inverse; c.media = inv.media; c.entree = inv.entree; c.sortie = inv.sortie; delete c.inverse; });
    toast("La vidéo se lit de nouveau à l'endroit");
    return;
  }
  const m = app.medias.get(c.media);
  if (!m) return;
  app.lecteur.pause();
  toast("Préparation de la lecture à l'envers…", null, null, 600000);
  try {
    const fichier = await inverserVideo(m, c.entree, c.sortie, { progres: (k) => toast(`Lecture à l'envers… ${Math.round(k * 100)} %`, null, null, 600000) });
    const nm = await importer(fichier);
    await S.ecrireMedia(nm);
    app.medias.set(nm.id, nm);
    app.p.medias.push(nm.id);
    modifier(() => {
      c.inverse = { media: c.media, entree: c.entree, sortie: c.sortie };
      c.media = nm.id;
      c.entree = 0;
      c.sortie = Math.min(nm.duree, c.inverse.sortie - c.inverse.entree);
    });
    rendreBiblio();
    app.dernierInverse = { ok: true, duree: nm.duree };
    toast("La vidéo se lit à l'envers");
  } catch (e) {
    app.dernierInverse = { erreur: e.message };
    toast(`La lecture à l'envers a échoué : ${e.message}`);
  }
}

async function importerLut(fichier) {
  const id = app.aLut;
  app.aLut = null;
  const f = id && M.trouver(app.p, id);
  if (!f || !fichier) return;
  let m;
  try { m = await importer(fichier); } catch (e) { toast(e.message || 'Ce fichier ne peut pas être lu.'); return; }
  if (m.type !== 'lut') { toast('Choisis un fichier .cube.'); return; }
  await S.ecrireMedia(m);
  app.medias.set(m.id, m);
  if (!app.p.medias.includes(m.id)) app.p.medias.push(m.id);
  try { await chargerLut(m); } catch (e) { toast(e.message); return; }
  modifier(() => { f.clip.lut = { media: m.id, intensite: 1 }; });
  toast(`LUT « ${m.nom} » appliquée`);
}

/** Sous-titres automatiques : le clip sélectionné, sinon toute la piste principale. Tout se passe sur l'appareil. */
async function sousTitres() {
  const f = app.selection && M.trouver(app.p, app.selection);
  const cibles = f && (f.clip.genre === 'video' || f.clip.genre === 'audio')
    ? [f.clip] : M.principale(app.p).clips.filter((c) => c.genre === 'video' && !c.muet);
  if (!cibles.length) { toast('Sélectionne une vidéo ou un son où l\'on parle.'); return; }
  const mode = app.modeSousTitres || 'precis';
  toast(`Préparation du modèle de transcription (${MODELES[mode].poids}, téléchargé une seule fois)…`, null, null, 600000);
  try {
    const asr = await chargerTranscription(mode, (k) => toast(`Téléchargement du modèle… ${Math.round(k * 100)} %`, null, null, 600000));
    const toutes = [];
    for (const [i, c] of cibles.entries()) {
      toast(`Transcription ${i + 1} sur ${cibles.length}…`, null, null, 600000);
      const ext = await sonDuClip(app.medias.get(c.media), c);
      if (!ext) continue;
      const r = await transcrire(asr, await versMono16k(ext.canaux, ext.sr), 'french');
      toutes.push(...legendes(r.chunks, c.debut, c.vitesse || 1, c.sortie - c.entree));
    }
    app.derniersSousTitres = toutes.map((x) => x.texte);
    if (!toutes.length) { toast('Aucune parole reconnue.'); return; }
    let premier = null;
    modifier((p) => {
      const piste = { id: M.uid('t'), genre: 'texte', clips: [] };
      for (const l of toutes) {
        const t = M.clipTexte(l.debut, 'legende', l.texte);
        t.duree = l.duree;
        t.anim = 'aucune';
        piste.clips.push(t);
      }
      piste.clips.sort((a, b) => a.debut - b.debut);
      p.pistes.push(piste);
      premier = piste.clips[0];
    });
    if (premier) selectionner(premier.id);
    toast(`${toutes.length} sous-titres ajoutés : touche-en un pour corriger un mot`);
  } catch (e) {
    app.derniersSousTitres = { erreur: e.message };
    toast(`Les sous-titres ont échoué : ${e.message}`);
  }
}

/** Cherche les visages et pose des images clés sur la position X pour qu'ils restent au centre. */
async function suivreVisages() {
  const f = app.selection && M.trouver(app.p, app.selection);
  if (!f || f.clip.genre !== 'video') return;
  const c = f.clip;
  const m = app.medias.get(c.media);
  toast("Préparation du moteur d'IA…", null, null, 120000);
  try {
    const r = await chercherVisages(m, c, (k) => toast(`Recherche des visages… ${Math.round(k * 100)} %`, null, null, 120000));
    const cles = clesSuiviVisage(c, app.p, m, r.temps, r.centres);
    app.dernierSuivi = { images: r.centres.length, visages: r.centres.filter((x) => x !== null).length, cles: cles.length };
    if (!cles.length) { toast('Aucun visage trouvé : le cadre reste tel quel.'); return; }
    modifier(() => { c.ajustement = 'remplir'; c.cles = c.cles || {}; c.cles.cx = cles; });
    toast(`Cadre calé sur les visages : ${cles.length} images clés`);
  } catch (e) {
    app.dernierSuivi = { erreur: e.message };
    toast(`Le suivi des visages a échoué : ${e.message}`);
  }
}

/** Réduit le bruit de fond d'un clip : le son nettoyé devient un nouveau média, l'original reste intact. */
async function debruiter() {
  const f = app.selection && M.trouver(app.p, app.selection);
  if (!f || (f.clip.genre !== 'video' && f.clip.genre !== 'audio')) return;
  const c = f.clip;
  const m = app.medias.get(c.media);
  toast('Réduction du bruit en cours…', null, null, 120000);
  try {
    const ext = await sonDuClip(m, c);
    if (!ext) { toast("Ce clip n'a pas de son."); return; }
    const propre = reduireBruit(ext.canaux, 0.6);
    const nom = `${m.nom.replace(/\.[^.]+$/, '')} (sans bruit).wav`;
    const nm = await importer(new File([versWav(propre, ext.sr)], nom, { type: 'audio/wav' }));
    await S.ecrireMedia(nm);
    app.medias.set(nm.id, nm);
    app.p.medias.push(nm.id);
    let son = null;
    const video = c.genre === 'video';
    modifier((p) => {
      if (video) {
        son = { id: M.uid(), genre: 'audio', media: nm.id, debut: c.debut, entree: 0, sortie: nm.duree, vitesse: c.vitesse || 1, volume: c.volume ?? 1,
          muet: false, fonduEntree: c.fonduEntree || 0, fonduSortie: c.fonduSortie || 0, garderTon: c.garderTon !== false };
        c.muet = true;
        M.poserSurPisteLibre(p, 'audio', son);
      } else { c.media = nm.id; c.entree = 0; c.sortie = nm.duree; }
    });
    if (son) selectionner(son.id);
    rendreBiblio();
    toast(video ? 'Bruit réduit : le son nettoyé est sur sa propre piste' : 'Bruit réduit');
  } catch (e) {
    toast(`La réduction du bruit a échoué : ${e.message}`);
  }
}

/** Forme d'onde d'une vidéo dont on a détaché le son (calculée une fois, gardée avec le média). */
async function calculerOnde(id) {
  const m = app.medias.get(id);
  if (!m || m.onde || m.taille > 300 * 1048576) return;
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const buf = await ctx.decodeAudioData(await m.fichier.arrayBuffer());
    ctx.close();
    m.onde = formeOnde(buf);
    await S.ecrireMedia(m);
    app.frise.rendre();
  } catch { /* pas de forme d'onde : la piste reste unie */ }
}

async function remplacerMedia(fichier) {
  const id = app.aRemplacer;
  app.aRemplacer = null;
  const f = id && M.trouver(app.p, id);
  if (!f || !fichier) return;
  let m;
  try { m = await importer(fichier); } catch (e) { toast(e.message || 'Ce fichier ne peut pas être lu.'); return; }
  const sonPourSon = (f.clip.genre === 'audio') === (m.type === 'audio');
  if (!sonPourSon) { toast(f.clip.genre === 'audio' ? 'Remplace un son par un autre son.' : 'Remplace une image par une vidéo ou une photo.'); return; }
  await S.ecrireMedia(m);
  app.medias.set(m.id, m);
  app.p.medias.push(m.id);
  modifier(() => {
    const c = f.clip;
    const d = M.dureeClip(c);
    delete c.inverse;
    c.media = m.id;
    if (m.type === 'image') { c.genre = 'image'; c.entree = 0; c.sortie = d; c.vitesse = 1; }
    else { c.genre = m.type === 'audio' ? 'audio' : 'video'; c.entree = 0; c.sortie = Math.min(m.duree, d * (c.vitesse || 1)); }
  });
  rendreBiblio();
  toast('Média remplacé');
}

/** L'image de la tête de lecture, en pleine définition, pour la miniature YouTube ou TikTok. */
async function couverture() {
  if (!app.p) return;
  const { W, H } = dimensionsSortie(app.p, 1080);
  const cv = document.createElement('canvas');
  cv.width = W;
  cv.height = H;
  await app.lecteur.aller(app.lecteur.t);
  dessinerImage(cv.getContext('2d'), app.p, app.lecteur.tVisible(), W, H, app.lecteur._obtenir, app.p.fps);
  const blob = await new Promise((ok) => cv.toBlob(ok, 'image/png'));
  app.derniereCouverture = blob;
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `${(app.p.nom || 'video').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^\w-]+/g, '-')}-couverture.png`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 10000);
  toast('Image de couverture téléchargée');
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
      const t0 = app.lecteur.t;
      geste = f ? { clip: f.clip, fx, fy, cx: M.valeur(f.clip, 'cx', t0), cy: M.valeur(f.clip, 'cy', t0), note: false } : null;
    } else if (pointeurs.size === 2 && geste) {
      const [a, b] = [...pointeurs.values()];
      const kk = geste.clip.genre === 'texte' ? 'taille' : 'echelle';
      geste.pince = { d: Math.hypot(a.x - b.x, a.y - b.y), echelle: M.valeur(geste.clip, kk, app.lecteur.t) ?? 1 };
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
      if (c.genre === 'texte') reglerAnimable(c, 'taille', M.clamp(geste.pince.echelle * r, 0.02, 0.3));
      else reglerAnimable(c, 'echelle', M.clamp(geste.pince.echelle * r, 0.05, 5));
    } else if (pointeurs.size === 1) {
      const { fx, fy } = app.lecteur.fraction(e);
      reglerAnimable(c, 'cx', M.clamp(geste.cx + fx - geste.fx, -0.5, 1.5));
      reglerAnimable(c, 'cy', M.clamp(geste.cy + fy - geste.fy, -0.5, 1.5));
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
    if (!f || f.clip.genre === 'audio' || f.clip.genre === 'effet') return;
    e.preventDefault();
    noterUneFois();
    const k = e.deltaY < 0 ? 1.05 : 1 / 1.05;
    const t0 = app.lecteur.t;
    if (f.clip.genre === 'texte') reglerAnimable(f.clip, 'taille', M.clamp(M.valeur(f.clip, 'taille', t0) * k, 0.02, 0.3));
    else reglerAnimable(f.clip, 'echelle', M.clamp((M.valeur(f.clip, 'echelle', t0) ?? 1) * k, 0.05, 5));
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
  $('#export-taille-gif').innerHTML = '<legend>Taille</legend>' + TAILLES_GIF.map(([v, t]) => `<label><input type="radio" name="taille-gif" value="${v}"${v === 360 ? ' checked' : ''}><span>${t} · ${v} px</span></label>`).join('');
  $('#export-cadence-gif').innerHTML = '<legend>Images par seconde</legend>' + CADENCES_GIF.map((v) => `<label><input type="radio" name="cadence-gif" value="${v}"${v === 15 ? ' checked' : ''}><span>${v}</span></label>`).join('');
  const radioSon = $('input[name="format-export"][value="son"]');
  radioSon.disabled = !aDuSon(app.p);
  if (radioSon.disabled && radioSon.checked) $('input[name="format-export"][value="video"]').checked = true;
  const fil = $('#export-filigrane');
  fil.checked = true;
  fil.disabled = !pro;
  $('#export-volume').innerHTML = VOLUMES.map(([v, t]) => `<option value="${v}"${v === app.p.volumeCible ? ' selected' : ''}>${t}</option>`).join('');
  $('.offre-pro').hidden = pro;
  majFormatExport();
  $('#export-reglages').hidden = false;
  $('#export-progres').hidden = true;
  $('#export-fini').hidden = true;
  $('#dlg-export').showModal();
}
const formatExport = () => ($('input[name="format-export"]:checked') || {}).value || 'video';
function majFormatExport() {
  const f = formatExport();
  $('#export-opt-video').hidden = f !== 'video';
  $('#export-opt-gif').hidden = f !== 'gif';
  $('#export-ligne-filigrane').hidden = f === 'son';
  $('.export-volume').hidden = f === 'gif';
  $('.offre-pro').hidden = estPro() || f === 'son';
  majInfosExport();
}
function majInfosExport() {
  const f = formatExport();
  const duree = M.formatTemps(M.dureeProjet(app.p));
  if (f === 'son') { $('#export-infos').textContent = `${duree} · son seul, M4A (AAC)`; return; }
  if (f === 'gif') {
    const { W, H } = dimensionsSortie(app.p, parseInt(($('input[name="taille-gif"]:checked') || {}).value || '360', 10));
    $('#export-infos').textContent = `${W} × ${H} pixels · ${duree} · GIF animé, sans son${M.dureeProjet(app.p) > 20 ? ' · long pour un GIF : il pèsera lourd' : ''}`;
    return;
  }
  const court = parseInt(($('input[name="qualite"]:checked') || {}).value || '1080', 10);
  const { W, H } = dimensionsSortie(app.p, court);
  $('#export-infos').textContent = `${W} × ${H} pixels · ${duree} · MP4`;
}

async function lancerExport() {
  const format = formatExport();
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
    const progres = ({ etape, part }) => {
      $('#export-etape').textContent = etape === 'son' ? 'Mixage du son…' : etape === 'ia' ? "Chargement du moteur d'IA…" : etape === 'fin' ? 'Finalisation…' : 'Fabrication des images…';
      const total = etape === 'images' ? 0.05 + part * 0.93 : etape === 'son' ? 0.03 : 1;
      $('#export-barre').style.transform = `scaleX(${total})`;
      $('#export-pourcent').textContent = `${Math.round(total * 100)} %`;
      if (etape === 'images' && part > 0.03) {
        const ecoule = (performance.now() - t0) / 1000;
        const reste = Math.max(0, (ecoule / part) * (1 - part));
        $('#export-reste').textContent = `Encore environ ${reste < 60 ? `${Math.ceil(reste)} s` : `${Math.ceil(reste / 60)} min`}`;
      }
    };
    const r = format === 'gif'
      ? await exporterGif(app.p, app.medias, { court: parseInt($('input[name="taille-gif"]:checked').value, 10), fps: parseInt($('input[name="cadence-gif"]:checked').value, 10), filigrane, signal: ctrl.signal, progres })
      : format === 'son'
        ? await exporterSon(app.p, app.medias, { signal: ctrl.signal, progres })
        : await exporter(app.p, app.medias, { court, fps, filigrane, signal: ctrl.signal, progres });
    app.dernierExport = r;
    if (app.urlExport) URL.revokeObjectURL(app.urlExport);
    app.urlExport = URL.createObjectURL(r.blob);
    const video = $('#export-video');
    const gif = $('#export-gif');
    const audio = $('#export-audio');
    video.hidden = format !== 'video';
    gif.hidden = format !== 'gif';
    audio.hidden = format !== 'son';
    for (const el of [video, gif, audio]) if (el.hidden) el.removeAttribute('src');
    (format === 'gif' ? gif : format === 'son' ? audio : video).src = app.urlExport;
    $('#export-titre-fini').textContent = format === 'gif' ? 'Ton GIF est prêt' : format === 'son' ? 'Ton son est prêt' : 'Ta vidéo est prête';
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
    const poids = mo < 1 ? `${Math.round(mo * 1024)} Ko` : `${nombre(mo)} Mo`;
    $('#export-resume').textContent = format === 'son'
      ? `${M.formatTemps(r.duree)} · ${r.extension.toUpperCase()} · ${poids} · fabriqué en ${sec} s`
      : `${r.W} × ${r.H} · ${M.formatTemps(r.duree)} · ${poids} · fabriqué${format === 'gif' ? '' : 'e'} en ${sec} s${filigrane ? ' · avec filigrane' : ''}`;
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
    else if (b.dataset.action === 'ouvrir-nuage') ouvrirNuage(id);
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
  $('#btn-marqueur').addEventListener('click', marqueurIci);
  $('#btn-zoom').addEventListener('click', () => app.frise.zoomer(app.frise.pps * 1.4));
  $('#btn-dezoom').addEventListener('click', () => app.frise.zoomer(app.frise.pps / 1.4));
  $('#btn-lecture').addEventListener('click', () => app.lecteur.basculer());
  $('#btn-exporter').addEventListener('click', ouvrirExport);

  $('#btn-importer').addEventListener('click', () => $('#entree-fichiers').click());
  $('#btn-importer-son').addEventListener('click', () => $('#entree-sons').click());
  $('#entree-fichiers').addEventListener('change', async (e) => { await importerFichiers(e.target.files); e.target.value = ''; });
  $('#entree-sons').addEventListener('change', async (e) => { await importerFichiers(e.target.files, { versSon: true }); e.target.value = ''; });
  $('#btn-voix').addEventListener('click', basculerVoix);
  $('#btn-sous-titres').addEventListener('click', sousTitres);
  $('#entree-remplacer').addEventListener('change', async (e) => { await remplacerMedia(e.target.files[0]); e.target.value = ''; });
  $('#entree-lut').addEventListener('change', async (e) => { await importerLut(e.target.files[0]); e.target.value = ''; });
  $('#export-couverture').addEventListener('click', couverture);
  $('#biblio').addEventListener('click', (e) => {
    const a = e.target.closest('[data-ajouter]');
    const s = e.target.closest('[data-superposer]');
    const st = e.target.closest('[data-style]');
    const sticker = e.target.closest('[data-sticker]');
    const effet = e.target.closest('[data-effet]');
    const onglet = e.target.closest('[data-onglet]');
    if (sticker) ajouterSticker(sticker.dataset.sticker);
    else if (effet) ajouterEffet(effet.dataset.effet);
    else if (a) ajouterMedia(a.dataset.ajouter, 'principale');
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
  corps.addEventListener('toggle', (e) => {
    const d = e.target;
    if (!d.matches || !d.matches('details.groupe-insp')) return;
    const titre = d.querySelector('summary').textContent;
    if (d.open) app.fermes.delete(titre); else app.fermes.add(titre);
  }, true);

  for (const b of $$('.barre-mobile [data-feuille]')) {
    b.addEventListener('click', () => {
      const ouvert = $(`#${b.dataset.feuille}`).classList.contains('ouvert') && b.getAttribute('aria-expanded') === 'true';
      if (ouvert) fermerFeuilles(); else ouvrirFeuille(b.dataset.feuille, b.dataset.ongletCible);
    });
  }
  for (const b of $$('[data-fermer]')) b.addEventListener('click', fermerFeuilles);
  $('.scene').addEventListener('pointerdown', (e) => { if (estMobile() && !e.target.closest('#toile')) fermerFeuilles(); });

  $('#dlg-export').addEventListener('change', (e) => {
    if (e.target.name === 'qualite' || e.target.name === 'taille-gif') majInfosExport();
    if (e.target.name === 'format-export') majFormatExport();
    if (e.target.id === 'export-volume') { app.p.volumeCible = e.target.value; sauverBientot(); }
  });
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
    else if (k === 'm' && !mod) { e.preventDefault(); marqueurIci(); }
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

// ====================================================================== compte, Pro, nuage (vague 4)
let minuteurNuage = 0;
function versNuage(p) {
  clearTimeout(minuteurNuage);
  minuteurNuage = setTimeout(async () => {
    try { await C.nuageEcrire(p); if (app.p === p) $('#etat-sauve').textContent = 'Enregistré · nuage'; } catch { /* hors ligne : le prochain enregistrement réessaiera */ }
  }, 2500);
}

async function ouvrirNuage(id) {
  try {
    const p = await C.nuageLire(id);
    if (!p) { toast("Ce projet n'est plus dans le nuage."); return; }
    await S.ecrireProjet(p);
    await ouvrir(id);
  } catch (e) { toast(`Le nuage ne répond pas : ${e.message}`); }
}

function majCompte() {
  for (const b of $$('[data-ouvrir-compte]')) {
    b.hidden = !C.OUVERT;
    if (b.classList.contains('petit-compte')) b.classList.toggle('pro', estPro());
    else b.textContent = C.connecte() ? (estPro() ? 'Mon compte · Pro' : 'Mon compte') : 'Se connecter';
  }
  $('#export-pro').hidden = !C.OUVERT || estPro();
  $('.pro-bientot').hidden = C.OUVERT;
}

function volet(nom) { for (const v of $$('#dlg-compte [data-volet]')) v.hidden = v.dataset.volet !== nom; }
function messageCompte(id, texte) { const el = $(id); el.hidden = !texte; el.textContent = texte || ''; }

function rendreCompte() {
  const d = C.lesDroits();
  $('#compte-qui').textContent = C.adresse() ? `Connecté avec ${C.adresse()}` : 'Connecté';
  const pro = estPro();
  const jusqua = d && d.pro_jusqua ? new Date(d.pro_jusqua).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }) : '';
  $('#compte-statut').innerHTML = pro
    ? `<b>LA BOBINE Pro</b><span>Actif jusqu'au ${esc(jusqua)} · ${d.credits} crédits IA</span>`
    : `<b>Formule gratuite</b><span>Export avec filigrane, jusqu'en 1080p et 30 images par seconde.${d ? ` ${d.credits} crédits IA.` : ''}</span>`;
  $('#compte-code-parrain').textContent = (d && d.code) || '…';
  $('#compte-zone-parrain').hidden = !!(d && d.parrain);
}

async function ouvrirCompte() {
  messageCompte('#compte-message', '');
  messageCompte('#compte-message-compte', '');
  if (!C.connecte()) volet('connexion');
  else { volet('compte'); rendreCompte(); C.chargerDroits().then(rendreCompte).catch((e) => messageCompte('#compte-message-compte', e.message)); }
  if (!$('#dlg-compte').open) $('#dlg-compte').showModal();
}

/** Au retour de SasPay : on attend la confirmation du serveur, jamais celle du navigateur. */
async function retourPaiement(cas) {
  if (cas === 'paiement-annule') { toast("Paiement annulé : rien n'a été prélevé."); return; }
  toast('Merci ! On attend la confirmation de SasPay…', null, null, 60000);
  for (let i = 0; i < 20 && C.connecte(); i += 1) {
    try { await C.chargerDroits(); } catch { /* on réessaie */ }
    if (estPro()) { majCompte(); toast('LA BOBINE Pro est active. Bon montage !'); return; }
    await new Promise((ok) => setTimeout(ok, 3000));
  }
  toast("Le paiement n'est pas encore confirmé. Pro s'activera tout seul dès qu'il le sera.", null, null, 9000);
}

function brancherCompte() {
  C.lireRetourLien();
  C.surChangement(majCompte);
  majCompte();
  if (C.OUVERT && C.connecte()) C.moi().then(() => C.chargerDroits()).then(majCompte).catch(() => {});
  for (const b of $$('[data-ouvrir-compte]')) b.addEventListener('click', ouvrirCompte);
  for (const b of $$('[data-fermer-compte]')) b.addEventListener('click', () => $('#dlg-compte').close());
  $('#export-pro').addEventListener('click', () => { $('#dlg-export').close(); ouvrirCompte(); });
  $('#compte-envoyer').addEventListener('click', async () => {
    const email = $('#compte-email').value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { messageCompte('#compte-message', "Cette adresse e-mail n'a pas l'air complète."); return; }
    try {
      await C.envoyerLien(email);
      $('#compte-email-envoye').textContent = email;
      volet('code');
    } catch (e) { messageCompte('#compte-message', `L'e-mail n'est pas parti : ${e.message}`); }
  });
  $('#compte-retour').addEventListener('click', () => volet('connexion'));
  $('#compte-verifier').addEventListener('click', async () => {
    try {
      await C.verifierCode($('#compte-email').value, $('#compte-code').value);
      await C.chargerDroits();
      volet('compte');
      rendreCompte();
      if (!app.p) rendreProjets();
    } catch (e) { messageCompte('#compte-message-code', `Code refusé : ${e.message}`); }
  });
  $('#compte-offres').addEventListener('click', async (e) => {
    const b = e.target.closest('[data-offre]');
    if (!b) return;
    try { if (app.p) await sauver(); await C.payer(b.dataset.offre); }
    catch (err) { messageCompte('#compte-message-compte', err.message); }
  });
  $('#compte-copier').addEventListener('click', () => {
    const code = $('#compte-code-parrain').textContent;
    if (navigator.clipboard) navigator.clipboard.writeText(code).then(() => toast('Code copié')).catch(() => {});
  });
  $('#compte-poser-parrain').addEventListener('click', async () => {
    try {
      const r = await C.poserParrain($('#compte-parrain').value);
      messageCompte('#compte-message-compte', r === 'ok' ? 'Code de parrainage enregistré.' : r);
      await C.chargerDroits();
      rendreCompte();
    } catch (e) { messageCompte('#compte-message-compte', e.message); }
  });
  $('#compte-deconnexion').addEventListener('click', async () => {
    await C.deconnecter();
    $('#dlg-compte').close();
    majCompte();
    if (!app.p) rendreProjets();
    toast('Déconnecté');
  });
}

// ====================================================================== démarrage
async function demarrer() {
  app.lecteur = new Lecteur($('#toile'), {
    temps: (t) => { app.frise.majTemps(t); majTemps(t); },
    etat: (joue) => $('#editeur').classList.toggle('en-lecture', joue),
  });
  app.frise = new Frise(app);
  rendreStyles();
  fabriquerVignettes();
  rendreOutils();
  brancher();
  chargerPolices();
  S.demanderPersistance();
  brancherCompte();
  const retour = location.hash.slice(1);
  if (retour === 'merci' || retour === 'paiement-annule') { history.replaceState(null, '', location.pathname); retourPaiement(retour); await afficherAccueil(true); return; }
  const id = location.hash.slice(1);
  if (id) await ouvrir(id, true);
  else await afficherAccueil(true);
}

demarrer().catch((e) => {
  console.error(e);
  document.body.insertAdjacentHTML('afterbegin', `<p style="padding:16px;background:#ff5a4e;color:#fff">LA BOBINE n'a pas pu démarrer : ${esc(e.message)}</p>`);
});

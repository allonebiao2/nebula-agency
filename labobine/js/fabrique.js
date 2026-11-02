// LA BOBINE · la fenêtre « Vidéo depuis mes produits ».
// Deux portes : le catalogue d'une maison, lu à la source et publié avec LA BOBINE (lien #catalogue/<maison>),
// ou les photos que le commerçant ajoute lui-même, avec un nom et un prix.
// Elle fabrique un projet ordinaire (catalogue.js) puis l'ouvre dans l'éditeur.

import * as M from './model.js';
import * as S from './stock.js';
import { importer } from './medias.js';
import { sonDuClip } from './export.js';
import { detecterRythme } from './rythme.js';
import { MODELES, MAX_PRODUITS, dureeEstimee, fabriquerVideo } from './catalogue.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const PAR_DEFAUT = 8;
const FORMATS_VIDEO = [['9:16', 'Vertical 9:16'], ['1:1', 'Carré 1:1'], ['4:5', 'Portrait 4:5']];

export const etat = { source: null, produits: [], categorie: null, modele: 'vitrine', format: '9:16', musique: null };
let outils = null;

const choisis = () => etat.produits.filter((p) => p.choisi);
const message = (t) => { const el = $('#cat-message'); el.hidden = !t; el.textContent = t || ''; };

function rendre() {
  const cats = etat.source ? etat.source.categories : [];
  $('#cat-categories').hidden = cats.length < 2;
  $('#cat-categories').innerHTML = cats.length < 2 ? '' : [['', 'Tout'], ...cats.map((c) => [c, c])]
    .map(([v, t]) => `<button type="button" data-categorie="${esc(v)}" aria-pressed="${(etat.categorie || '') === v}">${esc(t)}</button>`).join('');
  const visibles = etat.produits.map((p, i) => [p, i]).filter(([p]) => !etat.categorie || p.categorie === etat.categorie);
  $('#cat-produits').innerHTML = visibles.length ? visibles.map(([p, i]) => `
    <div class="carte-produit" data-choisi="${p.choisi}">
      <button class="choisir${p.detoure ? ' detoure' : ''}" type="button" data-choisir="${i}" aria-pressed="${p.choisi}" aria-label="${p.choisi ? 'Retirer' : 'Choisir'} ${esc(p.nom)}"${p.photo ? ` style="background-image:url('${esc(p.photo)}')"` : ''}>${p.photo ? '' : `<span>${esc(p.nom)}<br><small>sans photo</small></span>`}</button>
      <input type="text" data-champ="nom" data-i="${i}" value="${esc(p.nom)}" maxlength="50" aria-label="Nom du produit">
      <input type="text" class="prix" data-champ="prix" data-i="${i}" value="${esc(p.prix)}" maxlength="30" placeholder="Prix" aria-label="Prix">
    </div>`).join('') : '<p class="aide">Ajoute les photos de tes produits : chacune devient un plan de la vidéo, avec son nom et son prix.</p>';
  $('#cat-modeles').innerHTML = Object.entries(MODELES).map(([k, m]) => `<button class="carte-modele" type="button" data-modele="${k}" aria-pressed="${k === etat.modele}"><b>${esc(m.nom)}</b><span>${esc(m.note)}</span></button>`).join('');
  $('#cat-formats').innerHTML = FORMATS_VIDEO.map(([k, t]) => `<button type="button" data-format="${k}" aria-pressed="${k === etat.format}">${t}</button>`).join('');
  compter();
}

function compter() {
  const n = choisis().length;
  $('#cat-compte').textContent = n
    ? `${n} produit${n > 1 ? 's' : ''} · environ ${Math.round(dureeEstimee(n, etat.modele))} s${etat.musique && etat.musique.rythme ? ', calée sur la musique' : ''}`
    : 'aucun produit choisi';
}

/** Ouvre la fenêtre : avec le catalogue d'une maison, ou vide pour ses propres photos. */
export async function ouvrirFabrique(slug) {
  Object.assign(etat, { source: null, produits: [], categorie: null, modele: 'vitrine', format: '9:16', musique: null });
  message('');
  $('#cat-musique-nom').textContent = 'Facultatif : les plans se calent sur ses temps.';
  $('#cat-maison').value = '';
  $('#cat-contact').value = '';
  $('#cat-appel').value = 'Commandez sur WhatsApp';
  if (slug) {
    try {
      const rep = await fetch(`catalogues/${encodeURIComponent(slug)}/catalogue.json`, { cache: 'no-cache' });
      if (!rep.ok) throw new Error(String(rep.status));
      const d = await rep.json();
      etat.source = d;
      let pris = 0;
      etat.produits = d.articles.map((a) => {
        const choisi = !!a.photo && pris < PAR_DEFAUT;
        if (choisi) pris += 1;
        return { nom: a.nom, prix: a.prixCourt, categorie: a.categorie, photo: a.photo ? `catalogues/${encodeURIComponent(slug)}/${a.photo}` : null, detoure: !!a.detoure, choisi };
      });
      $('#cat-maison').value = d.maison;
      $('#cat-contact').value = d.contact || '';
      $('#cat-titre').textContent = `La vidéo de ${d.maison}`;
      $('#cat-source').textContent = `${d.articles.length} articles lus sur le site de la maison le ${new Date(d.lu).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long' })}. Les prix sont ceux du site ; tu peux les retoucher ici.`;
      $('#dlg-catalogue').style.setProperty('--fond-maison', d.couleurs.fond);
    } catch {
      outils.toast("Ce catalogue n'est pas disponible : tu peux ajouter tes propres photos.");
      etat.source = null;
    }
  }
  if (!etat.source) {
    $('#cat-titre').textContent = 'Une vidéo depuis tes produits';
    $('#cat-source').textContent = 'Ajoute les photos de tes produits, écris leur nom et leur prix : LA BOBINE monte la vidéo.';
  }
  rendre();
  if (!$('#dlg-catalogue').open) $('#dlg-catalogue').showModal();
}

function ajouterPhotos(fichiers) {
  for (const f of [...fichiers]) {
    if (!(f.type || '').startsWith('image/')) continue;
    etat.produits.push({ nom: f.name.replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' ').slice(0, 50), prix: '', categorie: null, photo: URL.createObjectURL(f), fichier: f, detoure: false, choisi: choisis().length < MAX_PRODUITS });
  }
  etat.categorie = null;
  rendre();
}

async function choisirMusique(f) {
  if (!f) return;
  $('#cat-musique-nom').textContent = 'Écoute du rythme…';
  try {
    const m = await importer(f);
    if (m.type !== 'audio') throw new Error('choisis un fichier son');
    const ext = await sonDuClip(m, { entree: 0, sortie: m.duree });
    const r = ext ? detecterRythme(ext.canaux, ext.sr) : null;
    etat.musique = { media: m, rythme: r ? r.temps : null, bpm: r ? r.bpm : null };
    $('#cat-musique-nom').textContent = r ? `${m.nom} · ${Math.round(r.bpm)} BPM : les plans tomberont sur ses temps` : `${m.nom} · pas de rythme lisible, les plans gardent leur durée`;
  } catch (e) {
    etat.musique = null;
    $('#cat-musique-nom').textContent = `Cette musique n'a pas pu être lue : ${e.message}`;
  }
  compter();
}

/** Le fond des plans d'ouverture et de fin : la couleur de la maison, éclairée par son accent. */
async function fondImage(W, H, couleurs) {
  const cv = document.createElement('canvas');
  cv.width = W;
  cv.height = H;
  const o = cv.getContext('2d');
  o.fillStyle = couleurs.fond;
  o.fillRect(0, 0, W, H);
  for (const [y, r, a] of [[0.16, 0.95, 0.3], [1.05, 0.7, 0.14]]) {
    const g = o.createRadialGradient(W / 2, H * y, 0, W / 2, H * y, Math.max(W, H) * r);
    const hex = couleurs.accent.replace('#', '');
    const rgb = [0, 2, 4].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(',');
    g.addColorStop(0, `rgba(${rgb},${a})`);
    g.addColorStop(1, `rgba(${rgb},0)`);
    o.fillStyle = g;
    o.fillRect(0, 0, W, H);
  }
  return new Promise((ok) => cv.toBlob(ok, 'image/jpeg', 0.9));
}

async function fabriquer() {
  const liste = choisis();
  if (!liste.length) { message('Choisis au moins un produit.'); return; }
  if (liste.length > MAX_PRODUITS) { message(`${MAX_PRODUITS} produits au plus : au-delà, la vidéo devient trop longue pour TikTok.`); return; }
  const maison = $('#cat-maison').value.trim();
  const couleurs = (etat.source && etat.source.couleurs) || { accent: '#ffd23f', fond: '#14110e' };
  $('#dlg-catalogue').close();
  const toast = (t) => outils.toast(t, null, null, 120000);
  try {
    toast('Préparation des photos…');
    const f = M.FORMATS[etat.format];
    const fondBlob = await fondImage(f.w, f.h, couleurs);
    const fond = await importer(new File([fondBlob], `Fond ${maison || 'LA BOBINE'}.jpg`, { type: 'image/jpeg' }));
    await S.ecrireMedia(fond);
    const produits = [];
    for (const [i, p] of liste.entries()) {
      toast(`Préparation des photos… ${i + 1} sur ${liste.length}`);
      let media = null;
      if (p.photo) {
        const blob = p.fichier || (await (await fetch(p.photo)).blob());
        const ext = (blob.type.split('/')[1] || 'jpg').replace('jpeg', 'jpg');
        media = await importer(p.fichier || new File([blob], `${p.nom}.${ext}`, { type: blob.type }));
        await S.ecrireMedia(media);
      }
      produits.push({ nom: p.nom.trim() || `Produit ${i + 1}`, prix: p.prix.trim(), media, detoure: p.detoure });
    }
    if (etat.musique) await S.ecrireMedia(etat.musique.media);
    const projet = fabriquerVideo({
      format: etat.format, maison, produits, modele: etat.modele, fond, couleurs,
      appel: $('#cat-appel').value, contact: $('#cat-contact').value, musique: etat.musique,
    });
    await S.ecrireProjet(projet);
    outils.apres(projet);
    await outils.ouvrir(projet.id);
    outils.toast('Ta vidéo est montée : retouche ce que tu veux, puis exporte.', null, null, 7000);
  } catch (e) {
    outils.toast(`La vidéo n'a pas pu être fabriquée : ${e.message}`, null, null, 9000);
  }
}

export function brancherFabrique(o) {
  outils = o;
  $('#btn-catalogue').addEventListener('click', () => ouvrirFabrique());
  $('#cat-fermer').addEventListener('click', () => $('#dlg-catalogue').close());
  $('#cat-ajouter').addEventListener('click', () => $('#entree-produits').click());
  $('#entree-produits').addEventListener('change', (e) => { ajouterPhotos(e.target.files); e.target.value = ''; });
  $('#cat-musique').addEventListener('click', () => $('#entree-musique').click());
  $('#entree-musique').addEventListener('change', async (e) => { await choisirMusique(e.target.files[0]); e.target.value = ''; });
  $('#cat-fabriquer').addEventListener('click', fabriquer);
  $('#dlg-catalogue').addEventListener('click', (e) => {
    const ch = e.target.closest('[data-choisir]');
    const cat = e.target.closest('[data-categorie]');
    const mo = e.target.closest('[data-modele]');
    const fo = e.target.closest('[data-format]');
    if (ch) {
      const p = etat.produits[Number(ch.dataset.choisir)];
      if (!p.choisi && choisis().length >= MAX_PRODUITS) { message(`${MAX_PRODUITS} produits au plus : retire-en un d'abord.`); return; }
      p.choisi = !p.choisi;
      message('');
      const carte = ch.closest('.carte-produit');
      carte.dataset.choisi = String(p.choisi);
      ch.setAttribute('aria-pressed', String(p.choisi));
      compter();
    } else if (cat) { etat.categorie = cat.dataset.categorie || null; rendre(); }
    else if (mo) { etat.modele = mo.dataset.modele; rendre(); }
    else if (fo) { etat.format = fo.dataset.format; rendre(); }
  });
  $('#cat-produits').addEventListener('input', (e) => {
    const el = e.target.closest('[data-champ]');
    if (!el) return;
    etat.produits[Number(el.dataset.i)][el.dataset.champ] = el.value;
  });
}

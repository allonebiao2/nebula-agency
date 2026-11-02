// LA BOBINE · l'import des fichiers : on lit la durée, les dimensions, on fait une vignette,
// et pour le son une forme d'onde. Le fichier lui-même est gardé tel quel.

import { uid } from './model.js';
import { lireCube } from './lut.js';

const urls = new Map();

export function urlDe(media) {
  if (!media || !media.fichier) return null;
  let u = urls.get(media.id);
  if (!u) { u = URL.createObjectURL(media.fichier); urls.set(media.id, u); }
  return u;
}
export function libererUrl(id) {
  const u = urls.get(id);
  if (u) { URL.revokeObjectURL(u); urls.delete(id); }
}

export function typeDe(fichier) {
  const t = (fichier.type || '').toLowerCase();
  const n = (fichier.name || '').toLowerCase();
  if (/\.cube$/.test(n)) return 'lut';
  if (t.startsWith('video/') || /\.(mp4|mov|m4v|webm|mkv|3gp)$/.test(n)) return 'video';
  if (t.startsWith('image/') || /\.(jpe?g|png|webp|gif|heic|avif)$/.test(n)) return 'image';
  if (t.startsWith('audio/') || /\.(mp3|m4a|aac|wav|ogg|opus|flac)$/.test(n)) return 'audio';
  return null;
}

const attendre = (el, ok, ko, delai = 15000) => new Promise((res, rej) => {
  const fin = setTimeout(() => { nettoyer(); rej(new Error('Lecture trop longue')); }, delai);
  const surOk = () => { nettoyer(); res(); };
  const surKo = () => { nettoyer(); rej(new Error('Format non lu par ce navigateur')); };
  function nettoyer() { clearTimeout(fin); el.removeEventListener(ok, surOk); el.removeEventListener(ko, surKo); }
  el.addEventListener(ok, surOk, { once: true });
  el.addEventListener(ko, surKo, { once: true });
});

function vignette(source, l, h, largeur = 240) {
  const r = largeur / l;
  const c = document.createElement('canvas');
  c.width = Math.round(largeur);
  c.height = Math.max(1, Math.round(h * r));
  c.getContext('2d').drawImage(source, 0, 0, c.width, c.height);
  return c.toDataURL('image/jpeg', 0.72);
}

async function lireVideo(fichier) {
  const url = URL.createObjectURL(fichier);
  const v = document.createElement('video');
  v.muted = true; v.playsInline = true; v.preload = 'auto'; v.src = url;
  try {
    await attendre(v, 'loadedmetadata', 'error');
    let duree = v.duration;
    if (!Number.isFinite(duree)) { // certains WebM n'annoncent pas leur durée
      v.currentTime = 1e7;
      await attendre(v, 'seeked', 'error').catch(() => {});
      duree = v.duration;
    }
    if (!Number.isFinite(duree) || duree <= 0) throw new Error('Durée illisible');
    const l = v.videoWidth;
    const h = v.videoHeight;
    if (!l || !h) throw new Error('Format non lu par ce navigateur');
    v.currentTime = Math.min(duree / 3, 1);
    await attendre(v, 'seeked', 'error');
    return { duree, l, h, vignette: vignette(v, l, h) };
  } finally {
    v.removeAttribute('src'); v.load(); URL.revokeObjectURL(url);
  }
}

async function lireImage(fichier) {
  const bmp = await createImageBitmap(fichier);
  try { return { duree: 0, l: bmp.width, h: bmp.height, vignette: vignette(bmp, bmp.width, bmp.height) }; } finally { bmp.close(); }
}

let ctxAudio = null;
async function lireAudio(fichier) {
  ctxAudio = ctxAudio || new (window.AudioContext || window.webkitAudioContext)();
  const buf = await ctxAudio.decodeAudioData(await fichier.arrayBuffer());
  return { duree: buf.duration, l: 0, h: 0, onde: formeOnde(buf) };
}

/** 400 crêtes entre 0 et 1, assez pour dessiner la forme d'onde d'un clip. */
export function formeOnde(buf, n = 400) {
  const d = buf.getChannelData(0);
  const pas = Math.max(1, Math.floor(d.length / n));
  const res = [];
  for (let i = 0; i < n; i += 1) {
    let m = 0;
    const a = i * pas;
    for (let j = a; j < Math.min(d.length, a + pas); j += 8) m = Math.max(m, Math.abs(d[j]));
    res.push(Math.round(m * 100) / 100);
  }
  return res;
}

/** Une LUT .cube : on la lit une fois pour refuser tout de suite un fichier abîmé. */
async function lireLut(fichier) {
  const lut = lireCube(await fichier.text());
  return { duree: 0, l: 0, h: 0, vignette: null, taille3d: lut.taille };
}

/** Transforme un fichier en média : { id, type, nom, fichier, duree, l, h, vignette, onde }. */
export async function importer(fichier) {
  const type = typeDe(fichier);
  if (!type) throw new Error(`« ${fichier.name} » n'est ni une vidéo, ni une photo, ni un son.`);
  const infos = type === 'video' ? await lireVideo(fichier) : type === 'image' ? await lireImage(fichier) : type === 'lut' ? await lireLut(fichier) : await lireAudio(fichier);
  return {
    id: uid('m'), type, nom: fichier.name || type, fichier, taille: fichier.size,
    mime: fichier.type || '', ...infos, ajouteLe: Date.now(),
  };
}

/** Une image décodée par média photo, gardée pour l'aperçu. */
const bitmaps = new Map();
export async function bitmapDe(media) {
  if (bitmaps.has(media.id)) return bitmaps.get(media.id);
  const p = createImageBitmap(media.fichier).then((b) => { bitmaps.set(media.id, b); return b; });
  bitmaps.set(media.id, p);
  return p;
}
export function bitmapPret(media) {
  const b = bitmaps.get(media.id);
  return b && !(b instanceof Promise) ? b : null;
}

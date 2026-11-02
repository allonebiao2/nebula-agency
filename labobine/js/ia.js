// LA BOBINE · l'IA sur l'appareil : détourage des personnes et suivi des visages, par MediaPipe (Google,
// Apache 2.0). Le moteur (14 Mo) ne se charge qu'au premier usage ; rien ne part vers un serveur.

import { clamp } from './model.js';

const BASE = new URL('../vendor/', import.meta.url).href;
let charge = null;
let segmenteur = null;
let detecteur = null;

export const iaPrete = () => !!segmenteur && !!detecteur;

export function chargerVision() {
  if (charge) return charge;
  charge = (async () => {
    const mp = await import('../vendor/mediapipe-1.2.0/vision_bundle.mjs');
    const fichiers = await mp.FilesetResolver.forVisionTasks(`${BASE}mediapipe-1.2.0/wasm`);
    segmenteur = await mp.ImageSegmenter.createFromOptions(fichiers, {
      baseOptions: { modelAssetPath: `${BASE}modeles/selfie_segmenter.tflite`, delegate: 'CPU' },
      runningMode: 'IMAGE', outputConfidenceMasks: true, outputCategoryMask: false,
    });
    detecteur = await mp.FaceDetector.createFromOptions(fichiers, {
      baseOptions: { modelAssetPath: `${BASE}modeles/blaze_face_short_range.tflite`, delegate: 'CPU' },
      runningMode: 'IMAGE', minDetectionConfidence: 0.5,
    });
  })();
  charge.catch(() => { charge = null; });
  return charge;
}

/** Garde la personne, efface le décor : l'alpha de chaque pixel est multiplié par la confiance du modèle. */
export function detourerDonnees(donnees) {
  if (!segmenteur) return false;
  const res = segmenteur.segment(donnees);
  try {
    const masque = res.confidenceMasks && res.confidenceMasks[0];
    if (!masque) return false;
    const conf = masque.getAsFloat32Array();
    const mw = masque.width;
    const mh = masque.height;
    const { width: l, height: h, data: d } = donnees;
    for (let y = 0; y < h; y += 1) {
      const ligne = Math.min(mh - 1, Math.floor((y * mh) / h)) * mw;
      for (let x = 0; x < l; x += 1) {
        const c = conf[ligne + Math.min(mw - 1, Math.floor((x * mw) / l))];
        const k = clamp((c - 0.3) / 0.4, 0, 1);
        const i = (y * l + x) * 4 + 3;
        d[i] = Math.round(d[i] * k * k * (3 - 2 * k));
      }
    }
    return true;
  } finally {
    if (res.close) res.close();
  }
}

/**
 * Cherche le visage le plus grand, image par image (2,5 images par seconde de montage).
 * Rend { temps: [instants sources], centres: [x du visage en fraction de la largeur, ou null] }.
 */
export async function chercherVisages(media, clip, surProgres = () => {}) {
  await chargerVision();
  const mb = await import('../vendor/mediabunny-1.65.0.min.mjs');
  const entree = new mb.Input({ source: new mb.BlobSource(media.fichier), formats: mb.ALL_FORMATS });
  try {
    const piste = await entree.getPrimaryVideoTrack();
    if (!piste || !(await piste.canDecode())) throw new Error("Cette vidéo ne peut pas être décodée par ce navigateur.");
    const puits = new mb.VideoSampleSink(piste);
    const pas = 0.4 * (clip.vitesse || 1);
    const temps = [];
    for (let t = clip.entree; t < clip.sortie; t += pas) temps.push(t);
    temps.push(Math.max(clip.entree, clip.sortie - 0.05));
    const toile = document.createElement('canvas');
    const ctx = toile.getContext('2d', { willReadFrequently: true });
    const centres = [];
    for await (const s of puits.samplesAtTimestamps(temps)) {
      if (s) {
        if (!toile.width) { toile.width = 480; toile.height = Math.max(1, Math.round((480 * s.displayHeight) / s.displayWidth)); }
        s.draw(ctx, 0, 0, toile.width, toile.height);
        s.close();
        const r = detecteur.detect(toile);
        let mieux = null;
        for (const d of r.detections || []) {
          const b = d.boundingBox;
          if (b && (!mieux || b.width * b.height > mieux.width * mieux.height)) mieux = b;
        }
        centres.push(mieux ? (mieux.originX + mieux.width / 2) / toile.width : null);
      } else centres.push(null);
      surProgres(centres.length / temps.length);
    }
    return { temps, centres };
  } finally {
    entree.dispose();
  }
}

/**
 * Transforme les positions de visages en images clés sur la position X, pour un clip en « remplir l'écran ».
 * Fonction pure (testée dans Node). Rend [] si aucun visage n'a été vu.
 */
export function clesSuiviVisage(c, p, media, temps, centres) {
  if (!centres.some((x) => x !== null)) return [];
  const pleins = centres.slice();
  let dernier = pleins.find((x) => x !== null);
  for (let i = 0; i < pleins.length; i += 1) { if (pleins[i] === null) pleins[i] = dernier; else dernier = pleins[i]; }
  const lisses = pleins.map((_, i) => {
    const fen = pleins.slice(Math.max(0, i - 2), i + 3);
    return fen.reduce((a, b) => a + b, 0) / fen.length;
  });
  const rc = c.recadrage || { g: 0, d: 0, h: 0, b: 0 };
  const sl = media.l * (1 - rc.g - rc.d);
  const sh = media.h * (1 - rc.h - rc.b);
  const s = Math.max(p.w / sl, p.h / sh) * (c.echelle || 1);
  const dl = sl * s;
  const v = c.vitesse || 1;
  const cles = [];
  lisses.forEach((fx, i) => {
    const fc = (fx - rc.g) / (1 - rc.g - rc.d);
    let xc = p.w / 2 - (fc - 0.5) * dl;
    xc = dl >= p.w ? clamp(xc, p.w - dl / 2, dl / 2) : p.w / 2;
    const cx = xc / p.w;
    const t = Math.max(0, (temps[i] - c.entree) / v);
    const prec = cles[cles.length - 1];
    const fin = i === lisses.length - 1;
    if (!prec || fin || Math.abs(cx - prec.v) > 0.012 || t - prec.t > 2.5) cles.push({ t, v: Math.round(cx * 10000) / 10000 });
  });
  return cles;
}

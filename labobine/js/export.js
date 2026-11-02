// LA BOBINE · l'export. Chaque image est décodée exactement (pas « à peu près » comme l'aperçu),
// composée par le même moteur de dessin, puis encodée par le navigateur (WebCodecs, via Mediabunny).
// Le son est mixé d'avance, hors temps réel, puis versé par blocs d'une seconde au rythme des images.

import { dureeProjet, dureeClip, trouver } from './model.js';
import { besoinsA, dessinerImage, nombreImages } from './rendu.js';

let mb = null;
const chargerMediabunny = async () => mb || (mb = await import('../vendor/mediabunny-1.65.0.min.mjs'));

export const QUALITES = [
  { court: 720, nom: '720p', note: 'Léger, idéal pour WhatsApp' },
  { court: 1080, nom: '1080p', note: 'Net, idéal pour TikTok et YouTube' },
];
export const CADENCES = [24, 25, 30, 60];

export function dimensionsSortie(p, court) {
  const r = court / Math.min(p.w, p.h);
  const pair = (v) => Math.max(2, Math.round((v * r) / 2) * 2);
  return { W: pair(p.w), H: pair(p.h) };
}

const SR = 48000;
const aDuSon = (p) => p.pistes.some((t) => t.clips.some((c) => (c.genre === 'video' || c.genre === 'audio') && !c.muet && (c.volume ?? 1) > 0));

function annule(signal) {
  if (signal && signal.aborted) throw new DOMException('Export annulé', 'AbortError');
}

/**
 * Change la durée d'un son sans changer son ton (WSOLA) : on recolle des tranches de 40 ms qui se chevauchent,
 * chacune calée sur l'endroit où elle ressemble le plus à la suite naturelle de la précédente.
 * facteur = durée voulue / durée d'origine (2 = deux fois plus long).
 */
export function etirer(canaux, sr, facteur) {
  if (Math.abs(facteur - 1) < 1e-3) return canaux;
  const N = Math.max(256, Math.round(sr * 0.04));
  const Hs = Math.round(N / 2);
  const Ha = Hs / facteur;
  const tol = Math.round(sr * 0.01);
  const lenIn = canaux[0].length;
  const lenOut = Math.max(1, Math.round(lenIn * facteur));
  const sorties = canaux.map(() => new Float32Array(lenOut + N));
  const poids = new Float32Array(lenOut + N);
  const fen = new Float32Array(N);
  for (let i = 0; i < N; i += 1) fen[i] = 0.5 - 0.5 * Math.cos((2 * Math.PI * i) / (N - 1));
  const ref = canaux[0];
  let precedent = -1;
  for (let posOut = 0, k = 0; posOut < lenOut; posOut += Hs, k += 1) {
    const vise = Math.round(k * Ha);
    let debut = vise;
    if (precedent >= 0 && precedent + Hs + N <= lenIn) {
      const naturel = precedent + Hs;
      let mieux = -Infinity;
      for (let d = -tol; d <= tol; d += 2) {
        const s = vise + d;
        if (s < 0 || s + N > lenIn) continue;
        let c = 0;
        for (let i = 0; i < N; i += 8) c += ref[naturel + i] * ref[s + i];
        if (c > mieux) { mieux = c; debut = s; }
      }
    }
    debut = Math.max(0, Math.min(debut, lenIn - 1));
    const n = Math.min(N, lenIn - debut);
    for (let ch = 0; ch < canaux.length; ch += 1) {
      const src = canaux[ch];
      const dst = sorties[ch];
      for (let i = 0; i < n; i += 1) dst[posOut + i] += src[debut + i] * fen[i];
    }
    for (let i = 0; i < n; i += 1) poids[posOut + i] += fen[i];
    precedent = debut;
  }
  return sorties.map((d) => {
    const r = new Float32Array(lenOut);
    for (let i = 0; i < lenOut; i += 1) r[i] = poids[i] > 1e-3 ? d[i] / poids[i] : 0;
    return r;
  });
}

/** Le son d'un clip, de son entrée à sa sortie, en tableaux continus (un par canal). */
async function extraire(m, c, ctx, decodes, prevenir) {
  if (m.type === 'audio') {
    if (!decodes.has(m.id)) decodes.set(m.id, await ctx.decodeAudioData(await m.fichier.arrayBuffer()));
    const b = decodes.get(m.id);
    const i0 = Math.max(0, Math.round(c.entree * b.sampleRate));
    const i1 = Math.min(b.length, Math.round(c.sortie * b.sampleRate));
    if (i1 <= i0) return null;
    const canaux = [];
    for (let k = 0; k < b.numberOfChannels; k += 1) canaux.push(b.getChannelData(k).slice(i0, i1));
    return { canaux, sr: b.sampleRate };
  }
  const entree = new mb.Input({ source: new mb.BlobSource(m.fichier), formats: mb.ALL_FORMATS });
  try {
    const piste = await entree.getPrimaryAudioTrack();
    if (!piste) return null;
    if (!(await piste.canDecode())) { prevenir(`Le son de « ${m.nom} » n'a pas pu être lu par ce navigateur.`); return null; }
    const morceaux = [];
    let sr = 48000;
    let nc = 1;
    for await (const wb of new mb.AudioBufferSink(piste).buffers(c.entree, c.sortie)) {
      sr = wb.buffer.sampleRate;
      nc = Math.max(nc, wb.buffer.numberOfChannels);
      const d0 = Math.max(0, Math.round((c.entree - wb.timestamp) * sr));
      const d1 = Math.min(wb.buffer.length, Math.round((c.sortie - wb.timestamp) * sr));
      if (d1 > d0) morceaux.push({ buf: wb.buffer, d0, d1 });
    }
    const total = morceaux.reduce((n, x) => n + x.d1 - x.d0, 0);
    if (!total) return null;
    const canaux = [];
    for (let ch = 0; ch < nc; ch += 1) {
      const arr = new Float32Array(total);
      let pos = 0;
      for (const x of morceaux) {
        arr.set(x.buf.getChannelData(Math.min(ch, x.buf.numberOfChannels - 1)).subarray(x.d0, x.d1), pos);
        pos += x.d1 - x.d0;
      }
      canaux.push(arr);
    }
    return { canaux, sr };
  } finally {
    entree.dispose();
  }
}

/** Mixe tout le son du projet dans un AudioBuffer stéréo 48 kHz. */
async function mixerSon(p, medias, duree, signal, prevenir) {
  const ctx = new OfflineAudioContext(2, Math.max(1, Math.ceil(duree * SR)), SR);
  const decodes = new Map();
  for (const piste of p.pistes) {
    for (const c of piste.clips) {
      if ((c.genre !== 'video' && c.genre !== 'audio') || c.muet || (c.volume ?? 1) <= 0) continue;
      annule(signal);
      const m = medias.get(c.media);
      if (!m) continue;
      const v = c.vitesse || 1;
      const gain = ctx.createGain();
      gain.connect(ctx.destination);
      const vol = c.volume ?? 1;
      const a = c.debut;
      const b = a + dureeClip(c);
      gain.gain.setValueAtTime(c.fonduEntree > 0 ? 0 : vol, a);
      if (c.fonduEntree > 0) gain.gain.linearRampToValueAtTime(vol, a + Math.min(c.fonduEntree, b - a));
      if (c.fonduSortie > 0) {
        gain.gain.setValueAtTime(vol, Math.max(a, b - c.fonduSortie));
        gain.gain.linearRampToValueAtTime(0, b);
      }

      if (v !== 1 && c.garderTon !== false) {
        const ext = await extraire(m, c, ctx, decodes, prevenir);
        if (!ext) continue;
        const canaux = etirer(ext.canaux, ext.sr, 1 / v);
        const buf = ctx.createBuffer(canaux.length, canaux[0].length, ext.sr);
        canaux.forEach((d, k) => buf.copyToChannel(d, k));
        const src = ctx.createBufferSource();
        src.buffer = buf;
        src.connect(gain);
        src.start(a);
        continue;
      }

      if (m.type === 'audio') {
        if (!decodes.has(m.id)) decodes.set(m.id, await ctx.decodeAudioData(await m.fichier.arrayBuffer()));
        const src = ctx.createBufferSource();
        src.buffer = decodes.get(m.id);
        src.playbackRate.value = v;
        src.connect(gain);
        src.start(a, c.entree, c.sortie - c.entree);
        continue;
      }

      // vidéo : on ne décode que le passage utilisé, morceau par morceau
      const entree = new mb.Input({ source: new mb.BlobSource(m.fichier), formats: mb.ALL_FORMATS });
      try {
        const pisteSon = await entree.getPrimaryAudioTrack();
        if (!pisteSon) continue;
        if (!(await pisteSon.canDecode())) { prevenir(`Le son de « ${m.nom} » n'a pas pu être lu par ce navigateur.`); continue; }
        const puits = new mb.AudioBufferSink(pisteSon);
        for await (const wb of puits.buffers(c.entree, c.sortie)) {
          const debutSrc = Math.max(wb.timestamp, c.entree);
          const finSrc = Math.min(wb.timestamp + wb.duration, c.sortie);
          if (finSrc <= debutSrc) continue;
          const src = ctx.createBufferSource();
          src.buffer = wb.buffer;
          src.playbackRate.value = v;
          src.connect(gain);
          src.start(a + (debutSrc - c.entree) / v, debutSrc - wb.timestamp, finSrc - debutSrc);
        }
      } finally {
        entree.dispose();
      }
    }
  }
  annule(signal);
  return ctx.startRendering();
}

/**
 * Exporte le projet. Rend { blob, type, extension, W, H, duree, avertissements }.
 * `progres({ etape: 'son' | 'images' | 'fin', part })` est appelé au fil de l'eau.
 */
/** Le filigrane de la version gratuite : la bobine et le nom, en bas à droite, discrets mais lisibles. */
export function dessinerFiligrane(ctx, W, H) {
  const u = Math.min(W, H) * 0.034;
  const marge = u * 0.9;
  ctx.save();
  ctx.font = `800 ${u}px "Bricolage Grotesque", "Arial Black", sans-serif`;
  ctx.textBaseline = 'middle';
  const texte = 'LA BOBINE';
  const lt = ctx.measureText(texte).width;
  const r = u * 0.62;
  const x = W - marge - lt;
  const y = H - marge - r;
  ctx.globalAlpha = 0.82;
  ctx.shadowColor = 'rgba(0,0,0,0.55)';
  ctx.shadowBlur = u * 0.35;
  ctx.fillStyle = '#ffd23f';
  ctx.beginPath();
  ctx.arc(x - r * 1.5, y, r, 0, Math.PI * 2);
  ctx.fill();
  ctx.shadowBlur = 0;
  ctx.fillStyle = '#14110e';
  for (let i = 0; i < 5; i += 1) {
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / 5;
    ctx.beginPath();
    ctx.arc(x - r * 1.5 + Math.cos(a) * r * 0.55, y + Math.sin(a) * r * 0.55, r * 0.22, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.shadowBlur = u * 0.35;
  ctx.fillStyle = '#ffffff';
  ctx.fillText(texte, x, y);
  ctx.restore();
}

export async function exporter(p, medias, { court = 1080, fps = 30, filigrane = true, signal, progres = () => {} } = {}) {
  if (filigrane) await document.fonts.load('800 40px "Bricolage Grotesque"').catch(() => {});
  await chargerMediabunny();
  const avertissements = [];
  const prevenir = (m) => avertissements.push(m);
  const { W, H } = dimensionsSortie(p, court);
  const duree = dureeProjet(p);
  if (duree <= 0) throw new Error('Le projet est vide : ajoute au moins un clip.');
  const N = nombreImages(duree, fps);

  const codecV = await mb.getFirstEncodableVideoCodec(['avc', 'vp9', 'av1', 'vp8'], { width: W, height: H });
  if (!codecV) throw new Error("Ce navigateur ne sait pas fabriquer de vidéo. Ouvre LA BOBINE dans Chrome ou Edge à jour.");
  const enMp4 = codecV === 'avc';
  const codecA = aDuSon(p)
    ? await mb.getFirstEncodableAudioCodec(enMp4 ? ['aac', 'opus'] : ['opus', 'vorbis'], { numberOfChannels: 2, sampleRate: SR })
    : null;
  if (aDuSon(p) && !codecA) prevenir("Ce navigateur ne sait pas encoder le son : la vidéo sortira muette.");

  const cible = new mb.BufferTarget();
  const sortie = new mb.Output({
    format: enMp4 ? new mb.Mp4OutputFormat({ fastStart: 'in-memory' }) : new mb.WebMOutputFormat(),
    target: cible,
  });
  const toile = document.createElement('canvas');
  toile.width = W;
  toile.height = H;
  const ctx = toile.getContext('2d', { alpha: false });
  const srcV = new mb.CanvasSource(toile, { codec: codecV, quality: mb.QUALITY_HIGH, keyFrameInterval: 2 });
  sortie.addVideoTrack(srcV, { frameRate: fps });
  const srcA = codecA ? new mb.AudioBufferSource({ codec: codecA, quality: mb.QUALITY_HIGH }) : null;
  if (srcA) sortie.addAudioTrack(srcA);

  const entrees = [];
  const lecteurs = new Map();
  const images = new Map();
  try {
    await sortie.start();

    let mix = null;
    if (srcA) {
      progres({ etape: 'son', part: 0 });
      mix = await mixerSon(p, medias, duree, signal, prevenir);
    }

    // le plan : pour chaque clip vidéo, la liste des instants sources dans l'ordre où le moteur les demandera
    const plan = new Map();
    for (let i = 0; i < N; i += 1) {
      for (const b of besoinsA(p, i / fps, fps)) {
        if (b.clip.genre === 'video') {
          if (!plan.has(b.clip.id)) plan.set(b.clip.id, []);
          plan.get(b.clip.id).push(b.temps);
        } else if (b.clip.genre === 'image' && !images.has(b.clip.media)) {
          const m = medias.get(b.clip.media);
          if (m) images.set(m.id, await createImageBitmap(m.fichier));
        }
      }
    }
    for (const [id, temps] of plan) {
      const clip = trouver(p, id).clip;
      const m = medias.get(clip.media);
      const entree = new mb.Input({ source: new mb.BlobSource(m.fichier), formats: mb.ALL_FORMATS });
      entrees.push(entree);
      const piste = await entree.getPrimaryVideoTrack();
      if (!piste || !(await piste.canDecode())) throw new Error(`La vidéo « ${m.nom} » ne peut pas être décodée par ce navigateur.`);
      const decalage = typeof piste.getFirstTimestamp === 'function' ? Math.max(0, await piste.getFirstTimestamp()) : 0;
      const puits = new mb.VideoSampleSink(piste);
      lecteurs.set(id, { iter: puits.samplesAtTimestamps(temps.map((x) => x + decalage)), courant: null });
    }

    const obtenir = (clip) => {
      if (clip.genre === 'image') {
        const b = images.get(clip.media);
        return b ? { l: b.width, h: b.height, peindre: (c, sx, sy, sl, sh, x, y, l, h) => c.drawImage(b, sx, sy, sl, sh, x, y, l, h) } : null;
      }
      const s = lecteurs.get(clip.id) && lecteurs.get(clip.id).courant;
      return s ? { l: s.displayWidth, h: s.displayHeight, peindre: (c, sx, sy, sl, sh, x, y, l, h) => s.draw(c, sx, sy, sl, sh, x, y, l, h) } : null;
    };

    let posSon = 0;
    const verserSon = async (jusqua) => {
      if (!mix) return;
      const fin = Math.min(mix.length, Math.ceil(jusqua * SR));
      while (posSon < fin) {
        const n = Math.min(SR, mix.length - posSon);
        const bloc = new AudioBuffer({ length: n, numberOfChannels: 2, sampleRate: SR });
        for (let canal = 0; canal < 2; canal += 1) bloc.copyToChannel(mix.getChannelData(canal).subarray(posSon, posSon + n), canal);
        await srcA.add(bloc);
        posSon += n;
      }
    };

    for (let i = 0; i < N; i += 1) {
      annule(signal);
      const t = i / fps;
      for (const b of besoinsA(p, t, fps)) {
        if (b.clip.genre !== 'video') continue;
        const l = lecteurs.get(b.clip.id);
        const { value, done } = await l.iter.next();
        if (!done && value) {
          if (l.courant && l.courant !== value) l.courant.close();
          l.courant = value;
        }
      }
      dessinerImage(ctx, p, t, W, H, obtenir, fps);
      if (filigrane) dessinerFiligrane(ctx, W, H);
      await srcV.add(t, 1 / fps);
      await verserSon(t + 1 / fps);
      if (i % 3 === 0 || i === N - 1) progres({ etape: 'images', part: (i + 1) / N });
    }
    await verserSon(Infinity);
    srcV.close();
    if (srcA) srcA.close();
    progres({ etape: 'fin', part: 1 });
    await sortie.finalize();
    const type = enMp4 ? 'video/mp4' : 'video/webm';
    return { blob: new Blob([cible.buffer], { type }), type, extension: enMp4 ? 'mp4' : 'webm', W, H, duree, codecV, codecA, avertissements };
  } catch (e) {
    try { await sortie.cancel(); } catch { /* déjà fermée */ }
    throw e;
  } finally {
    for (const l of lecteurs.values()) {
      if (l.courant) { try { l.courant.close(); } catch { /* déjà fermée */ } }
      try { await l.iter.return(); } catch { /* fini */ }
    }
    for (const e of entrees) { try { e.dispose(); } catch { /* déjà libérée */ } }
    for (const b of images.values()) b.close();
  }
}

// LA BOBINE · lire une vidéo à l'envers. Un fichier vidéo ne se décode que vers l'avant (chaque image dépend des
// précédentes) : on le reprend donc par tranches, de la fin vers le début. Chaque tranche est décodée vers l'avant,
// gardée en mémoire, puis réécrite à rebours. Le son est retourné lui aussi. Seul le passage utilisé est traité,
// et le résultat devient un nouveau média : l'original reste intact.

import { sonDuClip } from './export.js';

let mb = null;
const charger = async () => mb || (mb = await import('../vendor/mediabunny-1.65.0.min.mjs'));

/** Rend un File (MP4, ou WebM si le navigateur n'encode pas le H.264) : le passage [entree, sortie] à l'envers. */
export async function inverserVideo(m, entreeS, sortieS, { progres = () => {}, signal } = {}) {
  await charger();
  const entree = new mb.Input({ source: new mb.BlobSource(m.fichier), formats: mb.ALL_FORMATS });
  try {
    const piste = await entree.getPrimaryVideoTrack();
    if (!piste || !(await piste.canDecode())) throw new Error(`La vidéo « ${m.nom} » ne peut pas être décodée par ce navigateur.`);
    const decalage = Math.max(0, await piste.getFirstTimestamp());
    const stats = await piste.computePacketStats(120).catch(() => null);
    const fps = Math.min(60, Math.max(12, Math.round((stats && stats.averagePacketRate) || 30)));
    const r = Math.min(1, 1920 / Math.max(piste.displayWidth, piste.displayHeight));
    const pair = (v) => Math.max(2, Math.round((v * r) / 2) * 2);
    const W = pair(piste.displayWidth);
    const H = pair(piste.displayHeight);
    const d = Math.max(0.05, sortieS - entreeS);
    const N = Math.max(1, Math.round(d * fps));

    const codecV = await mb.getFirstEncodableVideoCodec(['avc', 'vp9', 'vp8'], { width: W, height: H });
    if (!codecV) throw new Error('Ce navigateur ne sait pas fabriquer de vidéo.');
    const enMp4 = codecV === 'avc';
    const son = await sonDuClip(m, { entree: entreeS, sortie: sortieS }).catch(() => null);
    const codecA = son ? await mb.getFirstEncodableAudioCodec(enMp4 ? ['aac', 'opus'] : ['opus', 'vorbis'], { numberOfChannels: Math.min(2, son.canaux.length), sampleRate: son.sr }) : null;

    const cible = new mb.BufferTarget();
    const sortie = new mb.Output({ format: enMp4 ? new mb.Mp4OutputFormat({ fastStart: 'in-memory' }) : new mb.WebMOutputFormat(), target: cible });
    const toile = document.createElement('canvas');
    toile.width = W;
    toile.height = H;
    const ctx = toile.getContext('2d', { alpha: false });
    const srcV = new mb.CanvasSource(toile, { codec: codecV, quality: mb.QUALITY_HIGH, keyFrameInterval: 1 });
    sortie.addVideoTrack(srcV, { frameRate: fps });
    const srcA = codecA ? new mb.AudioBufferSource({ codec: codecA, quality: mb.QUALITY_HIGH }) : null;
    if (srcA) sortie.addAudioTrack(srcA);
    await sortie.start();

    // Le décodeur du navigateur n'a qu'une petite réserve d'images : en garder plusieurs ouvertes le bloque.
    // Chaque image décodée est donc recopiée dans une toile à nous, puis rendue aussitôt au décodeur.
    // Tranches d'environ 160 Mo de toiles au plus.
    const parTranche = Math.max(4, Math.min(60, Math.floor(160e6 / (W * H * 4))));
    const reserve = [];
    const toileN = (i) => {
      if (!reserve[i]) { const t = document.createElement('canvas'); t.width = W; t.height = H; reserve[i] = t; }
      return reserve[i];
    };
    const puits = new mb.VideoSampleSink(piste);
    for (let k0 = 0; k0 < N; k0 += parTranche) {
      if (signal && signal.aborted) throw new DOMException('Annulé', 'AbortError');
      const k1 = Math.min(N, k0 + parTranche);
      // l'image k de la sortie montre l'instant source sortie - (k + 0,5) / fps ; on les demande dans l'ordre croissant
      const temps = [];
      for (let k = k1 - 1; k >= k0; k -= 1) temps.push(Math.max(entreeS, sortieS - (k + 0.5) / fps) + decalage);
      const lot = [];
      let avant = null;
      let idxAvant = -1;
      let n = 0;
      for await (const s of puits.samplesAtTimestamps(temps)) {
        if (s && s === avant) { lot.push(idxAvant); continue; } // la même image pour deux instants voisins
        if (avant) avant.close();
        avant = s;
        if (!s) { lot.push(-1); idxAvant = -1; continue; }
        s.draw(toileN(n).getContext('2d'), 0, 0, W, H);
        lot.push(n);
        idxAvant = n;
        n += 1;
      }
      if (avant) avant.close();
      for (let k = k0; k < k1; k += 1) {
        const j = lot[k1 - 1 - k];
        if (j >= 0) ctx.drawImage(reserve[j], 0, 0);
        await srcV.add(k / fps, 1 / fps);
      }
      progres(k1 / N);
    }
    if (srcA) {
      const nc = Math.min(2, son.canaux.length);
      const canaux = son.canaux.slice(0, nc).map((c) => c.slice().reverse());
      for (let pos = 0; pos < canaux[0].length; pos += son.sr) {
        const n = Math.min(son.sr, canaux[0].length - pos);
        const bloc = new AudioBuffer({ length: n, numberOfChannels: nc, sampleRate: son.sr });
        canaux.forEach((c, i) => bloc.copyToChannel(c.subarray(pos, pos + n), i));
        await srcA.add(bloc);
      }
      srcA.close();
    }
    srcV.close();
    await sortie.finalize();
    const base = m.nom.replace(/\.[^.]+$/, '');
    const type = enMp4 ? 'video/mp4' : 'video/webm';
    return new File([cible.buffer], `${base} (à l'envers).${enMp4 ? 'mp4' : 'webm'}`, { type });
  } finally {
    entree.dispose();
  }
}

// LA BOBINE · les sous-titres automatiques. Le modèle Whisper (OpenAI, licence MIT, version ONNX de
// onnx-community) tourne DANS le navigateur grâce à Transformers.js (Hugging Face, Apache 2.0) : le son ne
// quitte jamais l'appareil. Seul le modèle se télécharge, une fois, puis le navigateur le garde.

const LIB = 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.3.2';
export const MODELES = {
  rapide: { id: 'onnx-community/whisper-tiny', poids: 'environ 40 Mo' },
  precis: { id: 'onnx-community/whisper-base', poids: 'environ 80 Mo' },
};
const transcripteurs = new Map();

export async function chargerTranscription(mode = 'precis', surProgres = () => {}) {
  const m = MODELES[mode] || MODELES.precis;
  if (transcripteurs.has(m.id)) return transcripteurs.get(m.id);
  const promesse = (async () => {
    const t = await import(LIB);
    t.env.allowLocalModels = false;
    const fichiers = new Map();
    const options = {
      dtype: 'q8',
      progress_callback: (e) => {
        if (e && e.status === 'progress' && e.total) {
          fichiers.set(e.file, [e.loaded, e.total]);
          let fait = 0; let total = 0;
          for (const [a, b] of fichiers.values()) { fait += a; total += b; }
          surProgres(total ? fait / total : 0);
        }
      },
    };
    if (typeof navigator !== 'undefined' && navigator.gpu) {
      try { return await t.pipeline('automatic-speech-recognition', m.id, { ...options, device: 'webgpu' }); } catch { /* repli sur WASM */ }
    }
    return t.pipeline('automatic-speech-recognition', m.id, options);
  })();
  transcripteurs.set(m.id, promesse);
  promesse.catch(() => transcripteurs.delete(m.id));
  return promesse;
}

/** Ramène un son en mono 16 kHz, le format qu'attend Whisper. */
export async function versMono16k(canaux, sr) {
  const n = canaux[0].length;
  const mono = new Float32Array(n);
  for (const c of canaux) for (let i = 0; i < n; i += 1) mono[i] += c[i] / canaux.length;
  if (sr === 16000) return mono;
  const ctx = new OfflineAudioContext(1, Math.max(1, Math.ceil((n * 16000) / sr)), 16000);
  const b = ctx.createBuffer(1, n, sr);
  b.copyToChannel(mono, 0);
  const s = ctx.createBufferSource();
  s.buffer = b;
  s.connect(ctx.destination);
  s.start();
  return (await ctx.startRendering()).getChannelData(0);
}

export async function transcrire(transcripteur, audio16k, langue = 'french') {
  const r = await transcripteur(audio16k, {
    language: langue, task: 'transcribe', return_timestamps: true, chunk_length_s: 30, stride_length_s: 5,
  });
  const chunks = (r.chunks && r.chunks.length) ? r.chunks : [{ text: r.text || '', timestamp: [0, audio16k.length / 16000] }];
  return { texte: (r.text || '').trim(), chunks };
}

/**
 * Découpe la transcription en légendes de 7 mots au plus, réparties dans le temps au prorata des lettres.
 * Les instants rendus sont en secondes de montage. Fonction pure (testée dans Node).
 */
export function legendes(chunks, debutClip, vitesse = 1, dureeSon = Infinity, max = 7) {
  const res = [];
  chunks.forEach((ch, i) => {
    const mots = String(ch.text || '').trim().split(/\s+/).filter(Boolean);
    if (!mots.length) return;
    const a = Math.max(0, (ch.timestamp && ch.timestamp[0]) || 0);
    const suivant = chunks[i + 1] && chunks[i + 1].timestamp && chunks[i + 1].timestamp[0];
    let b = ch.timestamp && ch.timestamp[1];
    if (b == null || !(b > a)) b = Math.min(dureeSon, suivant > a ? suivant : a + mots.length * 0.38);
    const n = Math.ceil(mots.length / max);
    const taille = Math.ceil(mots.length / n);
    const groupes = [];
    for (let k = 0; k < mots.length; k += taille) groupes.push(mots.slice(k, k + taille).join(' '));
    const lettres = groupes.reduce((s, g) => s + g.length, 0);
    let t = a;
    for (const g of groupes) {
      const d = ((b - a) * g.length) / lettres;
      res.push({ debut: debutClip + t / vitesse, duree: Math.max(0.4, d / vitesse), texte: g });
      t += d;
    }
  });
  for (let i = 0; i < res.length - 1; i += 1) {
    const fin = res[i + 1].debut;
    if (res[i].debut + res[i].duree > fin) res[i].duree = Math.max(0.2, fin - res[i].debut);
  }
  return res;
}

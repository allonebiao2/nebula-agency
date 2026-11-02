// LA BOBINE · le traitement du son, sans bibliothèque : réduction du bruit, volume perçu (LUFS), fichier WAV.

// ---------- FFT complexe, radix 2, en place ----------
function fft(re, im, inverse) {
  const n = re.length;
  for (let i = 1, j = 0; i < n; i += 1) {
    let bit = n >> 1;
    for (; j & bit; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j) { [re[i], re[j]] = [re[j], re[i]]; [im[i], im[j]] = [im[j], im[i]]; }
  }
  for (let len = 2; len <= n; len <<= 1) {
    const ang = ((inverse ? 2 : -2) * Math.PI) / len;
    const wr = Math.cos(ang);
    const wi = Math.sin(ang);
    for (let i = 0; i < n; i += len) {
      let cr = 1;
      let ci = 0;
      for (let k = 0; k < len / 2; k += 1) {
        const a = i + k;
        const b = a + len / 2;
        const tr = re[b] * cr - im[b] * ci;
        const ti = re[b] * ci + im[b] * cr;
        re[b] = re[a] - tr; im[b] = im[a] - ti;
        re[a] += tr; im[a] += ti;
        const t = cr * wr - ci * wi;
        ci = cr * wi + ci * wr;
        cr = t;
      }
    }
  }
  if (inverse) for (let i = 0; i < n; i += 1) { re[i] /= n; im[i] /= n; }
}

/**
 * Réduction du bruit par porte spectrale. On apprend le bruit de fond (les moments les plus calmes de chaque
 * fréquence), puis on baisse chaque fréquence d'autant qu'elle ressemble à ce bruit. Les gains sont lissés dans
 * le temps et entre fréquences voisines, pour éviter le « gazouillis » des débruiteurs naïfs.
 * force : de 0 (rien) à 1 (fort).
 */
export function reduireBruit(canaux, force = 0.6) {
  const N = 2048;
  const H = 512;
  const len = canaux[0].length;
  const nb = N / 2 + 1;
  const fen = new Float64Array(N);
  for (let i = 0; i < N; i += 1) fen[i] = 0.5 - 0.5 * Math.cos((2 * Math.PI * i) / N);
  const mono = new Float64Array(len);
  for (const c of canaux) for (let i = 0; i < len; i += 1) mono[i] += c[i] / canaux.length;
  const trames = Math.max(1, Math.ceil((len - N) / H) + 1);

  // 1. le bruit de fond : 15e centile de chaque fréquence, sur au plus 1 200 trames
  const pasProfil = Math.max(1, Math.floor(trames / 1200));
  const echantillons = [];
  const re = new Float64Array(N);
  const im = new Float64Array(N);
  for (let f = 0; f < trames; f += pasProfil) {
    const o = f * H;
    for (let i = 0; i < N; i += 1) { re[i] = (mono[o + i] || 0) * fen[i]; im[i] = 0; }
    fft(re, im, false);
    const m = new Float32Array(nb);
    for (let k = 0; k < nb; k += 1) m[k] = re[k] * re[k] + im[k] * im[k];
    echantillons.push(m);
  }
  // l'énergie d'une fréquence de bruit suit une loi exponentielle : son 15e centile vaut -ln(0,85) ≈ 0,16 fois sa
  // moyenne. On prend le centile (la parole ne le touche pas) et on le ramène à la moyenne.
  const bruit = new Float64Array(nb);
  const col = new Float64Array(echantillons.length);
  const rang = Math.floor(echantillons.length * 0.15);
  const versMoyenne = 1 / -Math.log(1 - 0.15);
  for (let k = 0; k < nb; k += 1) {
    for (let f = 0; f < echantillons.length; f += 1) col[f] = echantillons[f][k];
    col.sort();
    bruit[k] = col[rang] * versMoyenne;
  }

  // 2. les gains, trame par trame
  const sur = 1 + 2.5 * force;
  const plancher = Math.max(0.04, 0.35 - 0.3 * force);
  const gains = [];
  let precedent = new Float64Array(nb).fill(1);
  for (let f = 0; f < trames; f += 1) {
    const o = f * H;
    for (let i = 0; i < N; i += 1) { re[i] = (mono[o + i] || 0) * fen[i]; im[i] = 0; }
    fft(re, im, false);
    const g = new Float64Array(nb);
    for (let k = 0; k < nb; k += 1) {
      const p = re[k] * re[k] + im[k] * im[k];
      g[k] = p > 0 ? Math.max(plancher, Math.min(1, (p - sur * bruit[k]) / p)) : plancher;
    }
    const lisse = new Float64Array(nb);
    for (let k = 0; k < nb; k += 1) lisse[k] = (g[Math.max(0, k - 1)] + g[k] + g[Math.min(nb - 1, k + 1)]) / 3;
    for (let k = 0; k < nb; k += 1) lisse[k] = Math.max(lisse[k], precedent[k] * 0.6); // relâchement doux
    gains.push(lisse);
    precedent = lisse;
  }

  // 3. on applique les mêmes gains à chaque canal (l'image stéréo ne bouge pas), puis addition-recouvrement
  return canaux.map((c) => {
    const out = new Float64Array(len + N);
    const norme = new Float64Array(len + N);
    for (let f = 0; f < trames; f += 1) {
      const o = f * H;
      for (let i = 0; i < N; i += 1) { re[i] = (c[o + i] || 0) * fen[i]; im[i] = 0; }
      fft(re, im, false);
      const g = gains[f];
      for (let k = 0; k < nb; k += 1) {
        re[k] *= g[k]; im[k] *= g[k];
        if (k > 0 && k < N / 2) { re[N - k] *= g[k]; im[N - k] *= g[k]; }
      }
      fft(re, im, true);
      for (let i = 0; i < N; i += 1) { out[o + i] += re[i] * fen[i]; norme[o + i] += fen[i] * fen[i]; }
    }
    const r = new Float32Array(len);
    for (let i = 0; i < len; i += 1) r[i] = norme[i] > 1e-6 ? out[i] / norme[i] : 0;
    return r;
  });
}

// ---------- volume perçu, norme UIT BS.1770 (pondération K, portes absolue et relative) ----------
function biquad(x, b0, b1, b2, a1, a2) {
  const y = new Float64Array(x.length);
  let x1 = 0; let x2 = 0; let y1 = 0; let y2 = 0;
  for (let i = 0; i < x.length; i += 1) {
    const v = b0 * x[i] + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2;
    x2 = x1; x1 = x[i]; y2 = y1; y1 = v; y[i] = v;
  }
  return y;
}

/** Coefficients de la pondération K, calculés pour n'importe quelle fréquence d'échantillonnage. */
function coefficientsK(sr) {
  // étage 1 : plateau haut (+4 dB au-dessus de 1,5 kHz environ)
  let f0 = 1681.974450955533; let G = 3.999843853973347; let Q = 0.7071752369554196;
  let K = Math.tan((Math.PI * f0) / sr);
  const Vh = 10 ** (G / 20);
  const Vb = Vh ** 0.4996667741545416;
  let a0 = 1 + K / Q + K * K;
  const s1 = [(Vh + (Vb * K) / Q + K * K) / a0, (2 * (K * K - Vh)) / a0, (Vh - (Vb * K) / Q + K * K) / a0, (2 * (K * K - 1)) / a0, (1 - K / Q + K * K) / a0];
  // étage 2 : passe-haut à 38 Hz
  f0 = 38.13547087602444; Q = 0.5003270373238773;
  K = Math.tan((Math.PI * f0) / sr);
  a0 = 1 + K / Q + K * K;
  const s2 = [1, -2, 1, (2 * (K * K - 1)) / a0, (1 - K / Q + K * K) / a0];
  return [s1, s2];
}

/** Volume perçu intégré, en LUFS. Rend -Infinity pour un silence. */
export function mesurerLUFS(canaux, sr) {
  const [s1, s2] = coefficientsK(sr);
  const filtres = canaux.slice(0, 2).map((c) => {
    const a = biquad(c, s1[0], s1[1], s1[2], s1[3], s1[4]);
    return biquad(a, s2[0], s2[1], s2[2], s2[3], s2[4]);
  });
  const bloc = Math.round(0.4 * sr);
  const pas = Math.round(0.1 * sr);
  const len = filtres[0].length;
  const blocs = [];
  for (let o = 0; o + bloc <= len; o += pas) {
    let z = 0;
    for (const f of filtres) { let s = 0; for (let i = o; i < o + bloc; i += 1) s += f[i] * f[i]; z += s / bloc; }
    blocs.push(z);
  }
  if (!blocs.length) return -Infinity;
  const l = (z) => -0.691 + 10 * Math.log10(z);
  const absolus = blocs.filter((z) => z > 0 && l(z) > -70);
  if (!absolus.length) return -Infinity;
  const moyA = absolus.reduce((a, b) => a + b, 0) / absolus.length;
  const seuil = l(moyA) - 10;
  const relatifs = absolus.filter((z) => l(z) > seuil);
  return l(relatifs.reduce((a, b) => a + b, 0) / relatifs.length);
}

/** Gain qui amène un son au volume visé sans que la crête dépasse -0,5 dBFS. */
export function gainVers(canaux, sr, cible) {
  const l = mesurerLUFS(canaux, sr);
  if (!Number.isFinite(l)) return 1;
  let crete = 0;
  for (const c of canaux) for (let i = 0; i < c.length; i += 1) crete = Math.max(crete, Math.abs(c[i]));
  let g = 10 ** ((cible - l) / 20);
  if (crete * g > 0.944) g = 0.944 / Math.max(crete, 1e-9);
  return g;
}

/** Un fichier WAV 16 bits à partir de canaux en virgule flottante. */
export function versWav(canaux, sr) {
  const nc = canaux.length;
  const n = canaux[0].length;
  const buf = new ArrayBuffer(44 + n * nc * 2);
  const v = new DataView(buf);
  const ecrire = (o, s) => { for (let i = 0; i < s.length; i += 1) v.setUint8(o + i, s.charCodeAt(i)); };
  ecrire(0, 'RIFF'); v.setUint32(4, 36 + n * nc * 2, true); ecrire(8, 'WAVE'); ecrire(12, 'fmt ');
  v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, nc, true); v.setUint32(24, sr, true);
  v.setUint32(28, sr * nc * 2, true); v.setUint16(32, nc * 2, true); v.setUint16(34, 16, true);
  ecrire(36, 'data'); v.setUint32(40, n * nc * 2, true);
  let o = 44;
  for (let i = 0; i < n; i += 1) {
    for (let c = 0; c < nc; c += 1) {
      const s = Math.max(-1, Math.min(1, canaux[c][i]));
      v.setInt16(o, s < 0 ? s * 0x8000 : s * 0x7fff, true);
      o += 2;
    }
  }
  return new Blob([buf], { type: 'audio/wav' });
}

export const VOLUMES = [
  ['tel', 'Tel quel'],
  ['-14', 'Harmonisé pour TikTok et YouTube (-14 LUFS)'],
  ['-16', 'Plus doux (-16 LUFS)'],
  ['-23', 'Télévision (-23 LUFS)'],
];

// LA BOBINE · les temps d'une musique, trouvés sur l'appareil, sans bibliothèque.
// 1. L'enveloppe des attaques : à chaque tranche de 21 ms, de combien le spectre a-t-il grandi (flux spectral) ?
// 2. Le tempo : la période qui revient le plus dans cette enveloppe (autocorrélation), avec une préférence douce
//    pour les tempos qu'on danse (autour de 120 BPM).
// 3. Les temps : le chemin qui passe par les attaques les plus fortes en gardant ce pas (programmation dynamique,
//    à la manière d'Ellis, 2007).

import { fft } from './audio.js';

const N = 1024;
const SAUT = 256;

/** L'enveloppe des attaques, une valeur tous les SAUT échantillons. */
export function enveloppeAttaques(mono, sr) {
  const fen = new Float32Array(N);
  for (let i = 0; i < N; i += 1) fen[i] = 0.5 - 0.5 * Math.cos((2 * Math.PI * i) / N);
  const nb = Math.max(0, Math.floor((mono.length - N) / SAUT) + 1);
  const env = new Float32Array(nb);
  const re = new Float64Array(N);
  const im = new Float64Array(N);
  const bins = Math.min(N / 2, Math.round((11000 / sr) * N));
  let avant = new Float32Array(bins);
  let maintenant = new Float32Array(bins);
  for (let k = 0; k < nb; k += 1) {
    const o = k * SAUT;
    for (let i = 0; i < N; i += 1) { re[i] = mono[o + i] * fen[i]; im[i] = 0; }
    fft(re, im, false);
    let flux = 0;
    for (let b = 1; b < bins; b += 1) {
      const m = Math.log1p(100 * Math.hypot(re[b], im[b]));
      maintenant[b] = m;
      const d = m - avant[b];
      if (d > 0) flux += d;
    }
    env[k] = k ? flux : 0;
    [avant, maintenant] = [maintenant, avant];
  }
  // on retire la moyenne locale (un demi-seconde) : ne restent que les attaques
  const r = Math.max(1, Math.round((0.25 * sr) / SAUT));
  const cumul = new Float64Array(nb + 1);
  for (let k = 0; k < nb; k += 1) cumul[k + 1] = cumul[k] + env[k];
  const sortie = new Float32Array(nb);
  let max = 0;
  for (let k = 0; k < nb; k += 1) {
    const a = Math.max(0, k - r);
    const b = Math.min(nb, k + r + 1);
    const v = Math.max(0, env[k] - (cumul[b] - cumul[a]) / (b - a));
    sortie[k] = v;
    if (v > max) max = v;
  }
  if (max > 0) for (let k = 0; k < nb; k += 1) sortie[k] /= max;
  return sortie;
}

/** La période des temps, en tranches (fractionnaire), et le tempo qui va avec. */
export function estimerTempo(env, sr, { min = 60, max = 200 } = {}) {
  const parSeconde = sr / SAUT;
  const lagMin = Math.max(2, Math.floor((60 / max) * parSeconde));
  const lagMax = Math.min(env.length - 2, Math.ceil((60 / min) * parSeconde));
  if (lagMax <= lagMin) return null;
  const scores = new Float64Array(lagMax + 2);
  for (let L = lagMin; L <= lagMax + 1; L += 1) {
    let s = 0;
    for (let k = L; k < env.length; k += 1) s += env[k] * env[k - L];
    scores[L] = s / (env.length - L);
  }
  let mieux = -1;
  let lag = lagMin;
  for (let L = lagMin; L <= lagMax; L += 1) {
    const bpm = (60 * parSeconde) / L;
    const prefere = Math.exp(-0.5 * (Math.log2(bpm / 120) / 0.9) ** 2);
    // un temps fort revient aussi à deux et quatre périodes : on l'additionne pour stabiliser le choix
    const s = (scores[L] + 0.5 * (2 * L <= lagMax + 1 ? scores[2 * L] : 0)) * prefere;
    if (s > mieux) { mieux = s; lag = L; }
  }
  // raffinement parabolique autour du maximum
  const a = scores[lag - 1] || 0;
  const b = scores[lag];
  const c = scores[lag + 1] || 0;
  const den = a - 2 * b + c;
  const fin = den < 0 ? lag + (0.5 * (a - c)) / den : lag;
  return { periode: fin, bpm: (60 * parSeconde) / fin };
}

/** Les temps, en secondes depuis le début du son. */
export function suivreTemps(env, periode, sr, { serrage = 100 } = {}) {
  const n = env.length;
  const score = new Float64Array(n);
  const precedent = new Int32Array(n).fill(-1);
  const pMin = Math.round(periode / 2);
  const pMax = Math.round(periode * 2);
  for (let k = 0; k < n; k += 1) {
    let mieux = 0;
    let arg = -1;
    for (let m = k - pMax; m <= k - pMin; m += 1) {
      if (m < 0) continue;
      const ecart = Math.log((k - m) / periode);
      const s = score[m] - serrage * ecart * ecart;
      if (arg < 0 || s > mieux) { mieux = s; arg = m; }
    }
    score[k] = env[k] + (arg >= 0 ? Math.max(0, mieux) : 0);
    precedent[k] = arg >= 0 && mieux > 0 ? arg : -1;
  }
  // on part du meilleur score dans la dernière période
  let k = n - 1;
  let mieux = -Infinity;
  for (let i = Math.max(0, n - Math.ceil(periode)); i < n; i += 1) if (score[i] > mieux) { mieux = score[i]; k = i; }
  const tranches = [];
  while (k >= 0) { tranches.push(k); k = precedent[k]; }
  tranches.reverse();
  // le flux d'une tranche répond à une attaque située au milieu de sa fenêtre
  return tranches.filter((x) => env[x] > 0.02).map((x) => (x * SAUT + N / 2) / sr);
}

/** Tout en un : { temps, bpm } d'un son, ou null s'il n'a pas de rythme lisible. */
export function detecterRythme(canaux, sr) {
  const len = canaux[0].length;
  const mono = new Float32Array(len);
  for (const c of canaux) for (let i = 0; i < len; i += 1) mono[i] += c[i] / canaux.length;
  const env = enveloppeAttaques(mono, sr);
  if (env.length < 16) return null;
  const tempo = estimerTempo(env, sr);
  if (!tempo) return null;
  const temps = suivreTemps(env, tempo.periode, sr);
  if (temps.length < 2) return null;
  return { temps: temps.map((t) => Math.round(t * 1000) / 1000), bpm: Math.round(tempo.bpm * 10) / 10 };
}

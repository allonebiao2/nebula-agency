// LA BOBINE · l'encodeur GIF, écrit ici. Chaque image a sa propre palette de 255 couleurs (coupe médiane sur un
// histogramme à 15 bits), un tramage ordonné fixe (il ne scintille pas d'une image à l'autre) et, d'une image à
// la suivante, les pixels qui n'ont pas changé deviennent transparents : un décor immobile ne pèse presque rien.

const TRANSPARENT = 255;
const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map((v) => (v / 16 - 0.5) * 7);

/** Coupe médiane : rend une palette (tableau de [r, g, b]) d'au plus `n` couleurs. */
export function palette(hist, n = 255) {
  const boites = [];
  const pleins = [];
  for (let i = 0; i < hist.length; i += 1) if (hist[i]) pleins.push(i);
  if (!pleins.length) return [[0, 0, 0]];
  const decrire = (ids) => {
    let r0 = 31, r1 = 0, g0 = 31, g1 = 0, b0 = 31, b1 = 0, poids = 0;
    for (const i of ids) {
      const r = i >> 10; const g = (i >> 5) & 31; const b = i & 31;
      if (r < r0) r0 = r; if (r > r1) r1 = r; if (g < g0) g0 = g; if (g > g1) g1 = g; if (b < b0) b0 = b; if (b > b1) b1 = b;
      poids += hist[i];
    }
    return { ids, poids, etendue: Math.max(r1 - r0, g1 - g0, b1 - b0), axe: r1 - r0 >= g1 - g0 && r1 - r0 >= b1 - b0 ? 0 : g1 - g0 >= b1 - b0 ? 1 : 2 };
  };
  boites.push(decrire(pleins));
  while (boites.length < n) {
    // on coupe la boîte qui pèse le plus parmi celles qu'on peut encore couper
    let k = -1;
    let mieux = -1;
    for (let i = 0; i < boites.length; i += 1) {
      const b = boites[i];
      const v = b.poids * (b.etendue + 1);
      if (b.ids.length > 1 && b.etendue > 0 && v > mieux) { mieux = v; k = i; }
    }
    if (k < 0) break;
    const b = boites[k];
    const cle = b.axe === 0 ? (i) => i >> 10 : b.axe === 1 ? (i) => (i >> 5) & 31 : (i) => i & 31;
    b.ids.sort((x, y) => cle(x) - cle(y));
    let cumul = 0;
    let coupe = 1;
    for (let i = 0; i < b.ids.length - 1; i += 1) {
      cumul += hist[b.ids[i]];
      if (cumul >= b.poids / 2) { coupe = i + 1; break; }
      coupe = i + 1;
    }
    boites.splice(k, 1, decrire(b.ids.slice(0, coupe)), decrire(b.ids.slice(coupe)));
  }
  return boites.map((b) => {
    let r = 0, g = 0, bl = 0;
    for (const i of b.ids) { const w = hist[i]; r += (i >> 10) * w; g += ((i >> 5) & 31) * w; bl += (i & 31) * w; }
    const f = 255 / 31 / b.poids;
    return [Math.round(r * f), Math.round(g * f), Math.round(bl * f)];
  });
}

/** Compression LZW du GIF, codes de taille variable, remise à zéro à 4096 codes. */
export function lzw(indices, tailleMin = 8) {
  const clear = 1 << tailleMin;
  const fin = clear + 1;
  const sortie = [];
  let acc = 0;
  let nbits = 0;
  let taille = tailleMin + 1;
  const ecrire = (code) => {
    acc |= code << nbits;
    nbits += taille;
    while (nbits >= 8) { sortie.push(acc & 255); acc >>>= 8; nbits -= 8; }
  };
  let dico = new Map();
  let suivant = fin + 1;
  ecrire(clear);
  let w = indices[0];
  for (let i = 1; i < indices.length; i += 1) {
    const k = indices[i];
    const cle = (w << 8) | k;
    const x = dico.get(cle);
    if (x !== undefined) { w = x; continue; }
    ecrire(w);
    if (suivant < 4096) {
      dico.set(cle, suivant);
      suivant += 1;
      if (suivant > (1 << taille) && taille < 12) taille += 1;
    } else {
      ecrire(clear);
      dico = new Map();
      suivant = fin + 1;
      taille = tailleMin + 1;
    }
    w = k;
  }
  ecrire(w);
  ecrire(fin);
  if (nbits > 0) sortie.push(acc & 255);
  return Uint8Array.from(sortie);
}

export class EncodeurGif {
  constructor(W, H) {
    this.W = W;
    this.H = H;
    this.morceaux = [];
    this.affiche = null; // l'image telle qu'elle est à l'écran après la dernière image écrite
    const ent = [];
    const mot = (v) => ent.push(v & 255, (v >> 8) & 255);
    ent.push(...[...'GIF89a'].map((c) => c.charCodeAt(0)));
    mot(W); mot(H);
    ent.push(0, 0, 0); // pas de palette globale
    ent.push(0x21, 0xff, 11, ...[...'NETSCAPE2.0'].map((c) => c.charCodeAt(0)), 3, 1, 0, 0, 0); // boucle sans fin
    this.morceaux.push(Uint8Array.from(ent));
  }

  /** Ajoute une image RGBA (Uint8ClampedArray de W×H×4), affichée `delai` centièmes de seconde. */
  ajouter(rgba, delai) {
    const { W, H } = this;
    const n = W * H;
    const hist = new Uint32Array(32768);
    const cle = new Uint16Array(n);
    for (let y = 0, p = 0; y < H; y += 1) {
      for (let x = 0; x < W; x += 1, p += 1) {
        const o = p * 4;
        const d = BAYER[((y & 3) << 2) | (x & 3)];
        const r = Math.min(255, Math.max(0, rgba[o] + d)) >> 3;
        const g = Math.min(255, Math.max(0, rgba[o + 1] + d)) >> 3;
        const b = Math.min(255, Math.max(0, rgba[o + 2] + d)) >> 3;
        const k = (r << 10) | (g << 5) | b;
        cle[p] = k;
        hist[k] += 1;
      }
    }
    const pal = palette(hist, 255);
    // la couleur de palette la plus proche, calculée une fois par case de l'histogramme
    const vers = new Int16Array(32768).fill(-1);
    const proche = (k) => {
      const r = ((k >> 10) * 255) / 31; const g = (((k >> 5) & 31) * 255) / 31; const b = ((k & 31) * 255) / 31;
      let mieux = 0;
      let dm = Infinity;
      for (let i = 0; i < pal.length; i += 1) {
        const c = pal[i];
        const dd = (c[0] - r) ** 2 * 2 + (c[1] - g) ** 2 * 4 + (c[2] - b) ** 2 * 3;
        if (dd < dm) { dm = dd; mieux = i; }
      }
      return mieux;
    };
    const idx = new Uint8Array(n);
    const premier = !this.affiche;
    if (premier) this.affiche = new Uint8Array(n * 3);
    const aff = this.affiche;
    let transparents = 0;
    for (let p = 0; p < n; p += 1) {
      let i = vers[cle[p]];
      if (i < 0) { i = proche(cle[p]); vers[cle[p]] = i; }
      const c = pal[i];
      const o = p * 3;
      if (!premier && Math.abs(aff[o] - c[0]) + Math.abs(aff[o + 1] - c[1]) + Math.abs(aff[o + 2] - c[2]) < 18) {
        idx[p] = TRANSPARENT;
        transparents += 1;
      } else {
        idx[p] = i;
        aff[o] = c[0]; aff[o + 1] = c[1]; aff[o + 2] = c[2];
      }
    }
    const tete = [];
    const mot = (v) => tete.push(v & 255, (v >> 8) & 255);
    // extension de contrôle : on garde l'image d'avant sous les pixels transparents
    tete.push(0x21, 0xf9, 4, (1 << 2) | (transparents ? 1 : 0));
    mot(Math.max(2, Math.round(delai)));
    tete.push(TRANSPARENT, 0);
    tete.push(0x2c); mot(0); mot(0); mot(W); mot(H);
    tete.push(0x80 | 7); // palette locale de 256 couleurs
    const table = new Uint8Array(768);
    pal.forEach((c, i) => table.set(c, i * 3));
    const donnees = lzw(idx, 8);
    const blocs = [8];
    for (let i = 0; i < donnees.length; i += 255) {
      const t = Math.min(255, donnees.length - i);
      blocs.push(t);
      for (let j = 0; j < t; j += 1) blocs.push(donnees[i + j]);
    }
    blocs.push(0);
    this.morceaux.push(Uint8Array.from(tete), table, Uint8Array.from(blocs));
  }

  finir() {
    this.morceaux.push(Uint8Array.of(0x3b));
    return new Blob(this.morceaux, { type: 'image/gif' });
  }
}

/** Les délais d'une suite d'images à `fps`, en centièmes, sans dérive : 15 i/s donne 7, 7, 6, 7, 7, 6… */
export function delais(nb, fps) {
  const res = [];
  let avant = 0;
  for (let i = 1; i <= nb; i += 1) {
    const t = Math.round((i * 100) / fps);
    res.push(t - avant);
    avant = t;
  }
  return res;
}

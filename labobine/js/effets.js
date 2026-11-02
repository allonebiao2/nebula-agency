// LA BOBINE · les effets plein écran, dessinés ici. Ils s'appliquent à l'image déjà composée (vidéos et
// superpositions), sous les stickers et les textes, qui restent lisibles.
// Chaque effet ne dépend que de l'instant : le « hasard » est un calcul, l'aperçu et l'export tombent sur la
// même image. Ceux qui battent (Battement, Flash) se calent sur le rythme marqué, sinon sur 120 BPM.

const hasard = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
/** Un bruit doux entre -1 et 1 : deux hasards voisins, raccordés en douceur. */
const bruit = (t) => { const i = Math.floor(t); const f = t - i; const u = f * f * (3 - 2 * f); return (hasard(i) * (1 - u) + hasard(i + 1) * u) * 2 - 1; };
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

/** De 1 (sur le temps) à 0 (loin de lui). Sans rythme marqué : un temps toutes les demi-secondes. */
export function pulsation(temps, t, vitesse = 6) {
  let dernier = Math.floor(t / 0.5) * 0.5;
  if (temps && temps.length) {
    let a = 0;
    let b = temps.length - 1;
    if (t < temps[0]) return 0;
    while (a < b) { const m = (a + b + 1) >> 1; if (temps[m] <= t) a = m; else b = m - 1; }
    dernier = temps[a];
  }
  return Math.exp(-(t - dernier) * vitesse);
}

// ---------- toiles de travail ----------
const toiles = {};
function toile(nom, l, h) {
  let c = toiles[nom];
  if (!c) c = toiles[nom] = typeof OffscreenCanvas !== 'undefined' ? new OffscreenCanvas(l, h) : document.createElement('canvas');
  if (c.width !== l) c.width = l;
  if (c.height !== h) c.height = h;
  return c;
}
function copier(ctx, W, H) {
  const c = toile('copie', W, H);
  const o = c.getContext('2d');
  o.globalCompositeOperation = 'copy';
  o.globalAlpha = 1;
  o.drawImage(ctx.canvas, 0, 0, W, H);
  return c;
}
/** Un flou rapide et identique partout : on réduit l'image en deux fois, puis on l'agrandit. */
function flou(src, W, H, facteur) {
  const l1 = Math.max(2, Math.round(W / Math.sqrt(facteur)));
  const h1 = Math.max(2, Math.round(H / Math.sqrt(facteur)));
  const l2 = Math.max(2, Math.round(W / facteur));
  const h2 = Math.max(2, Math.round(H / facteur));
  const a = toile('flou1', l1, h1);
  const b = toile('flou2', l2, h2);
  const oa = a.getContext('2d');
  const ob = b.getContext('2d');
  oa.imageSmoothingQuality = 'high';
  ob.imageSmoothingQuality = 'high';
  oa.globalCompositeOperation = 'copy';
  ob.globalCompositeOperation = 'copy';
  oa.drawImage(src, 0, 0, l1, h1);
  ob.drawImage(a, 0, 0, l2, h2);
  oa.drawImage(b, 0, 0, l1, h1);
  return a;
}
let tuileGrain = null;
function grain() {
  if (tuileGrain) return tuileGrain;
  const n = 128;
  tuileGrain = toile('grain', n, n);
  const o = tuileGrain.getContext('2d');
  const d = o.createImageData(n, n);
  for (let i = 0; i < n * n; i += 1) {
    const v = Math.round(hasard(i * 0.731 + 3.1) * 255);
    d.data[i * 4] = v; d.data[i * 4 + 1] = v; d.data[i * 4 + 2] = v; d.data[i * 4 + 3] = 255;
  }
  o.putImageData(d, 0, 0);
  return tuileGrain;
}
let tuileLignes = null;
function lignes() {
  if (tuileLignes) return tuileLignes;
  tuileLignes = toile('lignes', 4, 4);
  const o = tuileLignes.getContext('2d');
  o.clearRect(0, 0, 4, 4);
  o.fillStyle = 'rgba(0,0,0,0.55)';
  o.fillRect(0, 2, 4, 2);
  return tuileLignes;
}
function remplirMotif(ctx, tuile, W, H, dx, dy, echelle) {
  const motif = ctx.createPattern(tuile, 'repeat');
  if (!motif) return;
  ctx.save();
  ctx.translate(-dx, -dy);
  ctx.scale(echelle, echelle);
  ctx.fillStyle = motif;
  ctx.fillRect(0, 0, (W + dx) / echelle + tuile.width, (H + dy) / echelle + tuile.height);
  ctx.restore();
}
/** Décalage des couleurs : le rouge part d'un côté, le vert et le bleu de l'autre. */
function decalerRvb(ctx, W, H, s, dy = 0) {
  const src = copier(ctx, W, H);
  const r = toile('rouge', W, H);
  const v = toile('cyan', W, H);
  for (const [c, couleur] of [[r, '#ff0000'], [v, '#00ffff']]) {
    const o = c.getContext('2d');
    o.globalCompositeOperation = 'copy';
    o.drawImage(src, 0, 0);
    o.globalCompositeOperation = 'multiply';
    o.fillStyle = couleur;
    o.fillRect(0, 0, W, H);
  }
  ctx.save();
  ctx.globalCompositeOperation = 'source-over';
  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, W, H);
  ctx.globalCompositeOperation = 'lighter';
  ctx.drawImage(r, -s, -dy);
  ctx.drawImage(v, s, dy);
  ctx.restore();
}
/** Redessine l'image composée, déplacée, tournée et agrandie autour du centre. */
function recadrer(ctx, W, H, { dx = 0, dy = 0, rot = 0, s = 1 }) {
  const src = copier(ctx, W, H);
  ctx.save();
  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, W, H);
  ctx.translate(W / 2 + dx, H / 2 + dy);
  if (rot) ctx.rotate((rot * Math.PI) / 180);
  ctx.scale(s, s);
  ctx.drawImage(src, -W / 2, -H / 2, W, H);
  ctx.restore();
}

// ---------- les effets ----------
// a = { ctx, W, H, lt (temps dans l'effet), d (durée), k (intensité 0 à 1), rythme (temps de montage), t }
export const EFFETS = {
  pellicule: {
    nom: 'Pellicule',
    dessiner({ ctx, W, H, t, k }) {
      const img = Math.floor(t * 24);
      ctx.save();
      ctx.globalCompositeOperation = 'multiply';
      ctx.fillStyle = `rgba(255,226,186,${0.35 * k})`;
      ctx.fillRect(0, 0, W, H);
      ctx.globalCompositeOperation = 'overlay';
      ctx.globalAlpha = 0.45 * k;
      remplirMotif(ctx, grain(), W, H, hasard(img) * 128, hasard(img + 0.37) * 128, Math.max(1, Math.min(W, H) / 540));
      ctx.globalCompositeOperation = 'source-over';
      ctx.globalAlpha = 1;
      ctx.fillStyle = `rgba(0,0,0,${0.09 * k * hasard(img + 0.11)})`;
      ctx.fillRect(0, 0, W, H);
      // rayures et poussières : quelques-unes par image, jamais au même endroit
      ctx.lineCap = 'round';
      for (let i = 0; i < 2; i += 1) {
        if (hasard(img * 3.1 + i) > 0.55) continue;
        ctx.strokeStyle = `rgba(250,240,220,${0.35 * k})`;
        ctx.lineWidth = Math.max(1, W / 700);
        const x = hasard(img * 7.7 + i) * W;
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x + (hasard(img + i) - 0.5) * W * 0.02, H); ctx.stroke();
      }
      ctx.fillStyle = `rgba(20,14,8,${0.6 * k})`;
      for (let i = 0; i < 5; i += 1) {
        if (hasard(img * 1.3 + i * 9.1) > 0.4) continue;
        ctx.beginPath();
        ctx.arc(hasard(img * 2.9 + i) * W, hasard(img * 5.3 + i) * H, Math.max(1, (0.5 + hasard(img + i * 3)) * Math.min(W, H) * 0.003), 0, Math.PI * 2);
        ctx.fill();
      }
      const g = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.35, W / 2, H / 2, Math.hypot(W, H) * 0.6);
      g.addColorStop(0, 'rgba(0,0,0,0)');
      g.addColorStop(1, `rgba(0,0,0,${0.5 * k})`);
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, W, H);
      ctx.restore();
    },
  },
  cassette: {
    nom: 'Cassette',
    dessiner({ ctx, W, H, lt, k }) {
      decalerRvb(ctx, W, H, Math.max(1, W * 0.004 * k));
      const src = copier(ctx, W, H);
      // la bande de réglage qui descend, décalée et bruitée
      const y = (((lt * 0.22) % 1.3) - 0.15) * H;
      const bh = H * 0.07;
      const dx = bruit(lt * 9) * W * 0.03 * k;
      ctx.save();
      ctx.beginPath(); ctx.rect(0, y, W, bh); ctx.clip();
      ctx.drawImage(src, dx, 0);
      ctx.fillStyle = `rgba(255,255,255,${0.12 * k})`;
      ctx.fillRect(0, y, W, bh);
      ctx.restore();
      ctx.save();
      ctx.globalAlpha = 0.5 * k;
      remplirMotif(ctx, lignes(), W, H, 0, 0, Math.max(1, H / 480));
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = 'saturation';
      ctx.fillStyle = `rgba(128,128,128,${0.25 * k})`;
      ctx.fillRect(0, 0, W, H);
      ctx.restore();
    },
  },
  rvb: {
    nom: 'Décalage RVB',
    dessiner({ ctx, W, H, lt, k }) { decalerRvb(ctx, W, H, W * (0.006 + 0.004 * bruit(lt * 3)) * k * 1.6, H * 0.002 * k); },
  },
  lueur: {
    nom: 'Lueur',
    dessiner({ ctx, W, H, k }) {
      const f = flou(copier(ctx, W, H), W, H, 14);
      ctx.save();
      ctx.globalCompositeOperation = 'screen';
      ctx.globalAlpha = 0.6 * k;
      ctx.drawImage(f, 0, 0, W, H);
      ctx.restore();
    },
  },
  vignettage: {
    nom: 'Vignettage',
    dessiner({ ctx, W, H, k }) {
      const g = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.3, W / 2, H / 2, Math.hypot(W, H) * 0.55);
      g.addColorStop(0, 'rgba(0,0,0,0)');
      g.addColorStop(1, `rgba(0,0,0,${0.85 * k})`);
      ctx.save();
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, W, H);
      ctx.restore();
    },
  },
  cinema: {
    nom: 'Bandes cinéma',
    dessiner({ ctx, W, H, lt, d, k }) {
      const e = clamp(Math.min(lt, d - lt) / 0.5, 0, 1);
      const h = H * 0.125 * k * (1 - (1 - e) ** 3);
      ctx.save();
      ctx.fillStyle = '#000';
      ctx.fillRect(0, 0, W, h);
      ctx.fillRect(0, H - h, W, h);
      ctx.restore();
    },
  },
  flou: {
    nom: 'Flou',
    dessiner({ ctx, W, H, k }) {
      if (k <= 0.01) return;
      const f = flou(copier(ctx, W, H), W, H, 2 + 22 * k);
      ctx.save();
      ctx.globalCompositeOperation = 'copy';
      ctx.drawImage(f, 0, 0, W, H);
      ctx.restore();
    },
  },
  secousse: {
    nom: 'Secousse',
    dessiner({ ctx, W, H, lt, k }) {
      recadrer(ctx, W, H, { dx: bruit(lt * 14) * W * 0.025 * k, dy: bruit(lt * 14 + 50) * H * 0.02 * k, rot: bruit(lt * 9 + 100) * 1.5 * k, s: 1 + 0.07 * k });
    },
  },
  battement: {
    nom: 'Battement',
    dessiner({ ctx, W, H, t, k, rythme }) { recadrer(ctx, W, H, { s: 1 + 0.08 * k * pulsation(rythme, t, 7) }); },
  },
  flash: {
    nom: 'Flash',
    dessiner({ ctx, W, H, t, k, rythme }) {
      const a = 0.75 * k * pulsation(rythme, t, 9) ** 2;
      if (a < 0.005) return;
      ctx.save();
      ctx.fillStyle = `rgba(255,255,255,${a})`;
      ctx.fillRect(0, 0, W, H);
      ctx.restore();
    },
  },
  soleil: {
    nom: 'Lumière chaude',
    dessiner({ ctx, W, H, lt, k }) {
      const R = Math.max(W, H) * 0.75;
      ctx.save();
      ctx.globalCompositeOperation = 'screen';
      for (const [x, y, c] of [[0.05 + 0.3 * Math.sin(lt * 0.5), 0.1 + 0.15 * Math.sin(lt * 0.37), '255,138,40'], [0.95 - 0.25 * Math.sin(lt * 0.42 + 1), 0.9 - 0.2 * Math.cos(lt * 0.3), '255,64,96']]) {
        const g = ctx.createRadialGradient(x * W, y * H, 0, x * W, y * H, R);
        g.addColorStop(0, `rgba(${c},${0.65 * k})`);
        g.addColorStop(0.45, `rgba(${c},${0.22 * k})`);
        g.addColorStop(1, `rgba(${c},0)`);
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, W, H);
      }
      ctx.restore();
    },
  },
  paillettes: {
    nom: 'Paillettes',
    dessiner({ ctx, W, H, lt, k }) {
      const u = Math.min(W, H);
      ctx.save();
      ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < 46; i += 1) {
        const x = hasard(i + 0.1) * W + Math.sin(lt * 0.7 + i) * u * 0.01;
        const y = (((hasard(i + 0.3) - lt * 0.035 * (0.5 + hasard(i + 0.7))) % 1) + 1) % 1 * H;
        const a = Math.max(0, Math.sin(lt * 3.2 * (0.6 + hasard(i + 0.9)) + hasard(i) * 6.28)) * k;
        if (a < 0.02) continue;
        const r = (0.008 + 0.014 * hasard(i + 0.2)) * u * (0.6 + 0.4 * a);
        ctx.fillStyle = `rgba(255,214,110,${0.9 * a})`;
        ctx.beginPath();
        ctx.moveTo(x, y - r); ctx.quadraticCurveTo(x, y, x + r, y); ctx.quadraticCurveTo(x, y, x, y + r);
        ctx.quadraticCurveTo(x, y, x - r, y); ctx.quadraticCurveTo(x, y, x, y - r);
        ctx.fill();
        ctx.fillStyle = `rgba(255,250,230,${0.8 * a})`;
        ctx.beginPath(); ctx.arc(x, y, r * 0.16, 0, Math.PI * 2); ctx.fill();
      }
      ctx.restore();
    },
  },
  pluie: {
    nom: 'Pluie',
    dessiner({ ctx, W, H, lt, k }) {
      ctx.save();
      ctx.globalCompositeOperation = 'multiply';
      ctx.fillStyle = `rgba(150,168,200,${0.35 * k})`;
      ctx.fillRect(0, 0, W, H);
      ctx.globalCompositeOperation = 'source-over';
      ctx.strokeStyle = `rgba(214,228,255,${0.45 * k})`;
      ctx.lineWidth = Math.max(1, Math.min(W, H) / 420);
      ctx.lineCap = 'round';
      ctx.beginPath();
      const l = H * 0.05;
      for (let i = 0; i < 140; i += 1) {
        const v = 1.5 + hasard(i + 0.4) * 0.9;
        const y = ((hasard(i + 0.6) + lt * v) % 1.15 - 0.08) * H;
        const x = hasard(i) * W * 1.2 - W * 0.1 + (y / H) * W * 0.06;
        ctx.moveTo(x, y);
        ctx.lineTo(x - l * 0.14, y - l * (0.7 + 0.6 * hasard(i + 0.8)));
      }
      ctx.stroke();
      ctx.restore();
    },
  },
  confettis: {
    nom: 'Confettis',
    dessiner({ ctx, W, H, lt, k }) {
      const u = Math.min(W, H);
      const couleurs = ['#ffd23f', '#ff5a4e', '#4fc58a', '#5b9dff', '#ff9fc6', '#ffffff'];
      ctx.save();
      ctx.globalAlpha = clamp(k, 0, 1);
      for (let i = 0; i < 80; i += 1) {
        const v = 0.22 + 0.28 * hasard(i + 0.4);
        const yy = lt * v - hasard(i + 0.6) * 1.1;
        if (yy < -0.06) continue;
        const y = ((yy % 1.15) - 0.06) * H;
        const x = hasard(i) * W + Math.sin(lt * 2 + i) * u * 0.03;
        const tourne = lt * (2 + 3 * hasard(i + 0.2)) + i;
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(tourne);
        ctx.scale(Math.cos(tourne * 1.7), 1);
        ctx.fillStyle = couleurs[i % couleurs.length];
        ctx.fillRect(-u * 0.011, -u * 0.006, u * 0.022, u * 0.012);
        ctx.restore();
      }
      ctx.restore();
    },
  },
  bokeh: {
    nom: 'Lumières floues',
    dessiner({ ctx, W, H, lt, k }) {
      const u = Math.min(W, H);
      ctx.save();
      ctx.globalCompositeOperation = 'screen';
      for (let i = 0; i < 18; i += 1) {
        const x = ((hasard(i + 0.1) + lt * 0.012 * (hasard(i + 0.5) - 0.5)) % 1) * W;
        const y = ((hasard(i + 0.3) - lt * 0.02 * hasard(i + 0.7) + 1) % 1) * H;
        const r = (0.04 + 0.09 * hasard(i + 0.2)) * u;
        const c = ['255,196,92', '255,140,80', '255,236,180'][i % 3];
        const a = (0.25 + 0.2 * Math.sin(lt * 0.9 + i)) * k;
        const g = ctx.createRadialGradient(x, y, 0, x, y, r);
        g.addColorStop(0, `rgba(${c},${a})`);
        g.addColorStop(0.7, `rgba(${c},${a * 0.6})`);
        g.addColorStop(1, `rgba(${c},0)`);
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
      }
      ctx.restore();
    },
  },
};

/** Applique un clip d'effet à l'image composée jusque-là. */
export function appliquerEffet(ctx, c, t, W, H, rythme) {
  const e = EFFETS[c.effet];
  if (!e) return;
  const lt = t - c.debut;
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  ctx.globalCompositeOperation = 'source-over';
  ctx.filter = 'none';
  e.dessiner({ ctx, W, H, t, lt, d: c.duree, k: clamp(c.intensite ?? 1, 0, 1.5), rythme });
  ctx.restore();
}

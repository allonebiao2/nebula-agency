/* LE MONDE · les matières partagées.
   Les wax ci-dessous sont GÉNÉRÉS (motifs dessinés au canevas) : ils tiennent
   la place des VRAIS tissus d'Hillary jusqu'à ce qu'elle les photographie
   (monde/PROMPTS-NANO-BANANA.md, section A1). Ce sont des tissus de décor :
   aucun n'est présenté comme une pièce à vendre. */
import { THREE, graine } from './moteur.js';

export const PALETTES_WAX = [
  ['#1d3d8f', '#f2b705', '#efe6d2', '#c0392b'],
  ['#5b2a86', '#f4f1ec', '#e6007e', '#2c2c2c'],
  ['#0f6e5b', '#f2c14e', '#1b1b1b', '#f6efe3'],
  ['#c1440e', '#f6d06f', '#1f3b2d', '#faf3e3'],
  ['#7a1f2b', '#f2e9dc', '#d9a441', '#1f1f1f'],
  ['#1b4f72', '#e8d5b5', '#e67e22', '#111111'],
  ['#e6007e', '#ffe9f5', '#0b0a0c', '#f2b705'],
  ['#2f6b3a', '#f4e3b2', '#b5332e', '#20201f'],
];

const cache = new Map();
export function wax(seed = 1, palette = null, taille = 512) {
  const cle = seed + '|' + (palette ? palette.join() : '');
  if (cache.has(cle)) return cache.get(cle);
  const r = graine(seed * 7919 + 13);
  const pal = palette || PALETTES_WAX[Math.floor(r() * PALETTES_WAX.length)];
  const c = document.createElement('canvas'); c.width = c.height = taille;
  const g = c.getContext('2d'); const W = taille;
  g.fillStyle = pal[0]; g.fillRect(0, 0, W, W);
  const type = Math.floor(r() * 6);
  const n = 4 + Math.floor(r() * 3), pas = W / n;
  const dessiner = (fn) => { for (let i = -1; i <= n; i++) for (let j = -1; j <= n; j++) fn(i * pas + (j % 2 ? pas / 2 : 0), j * pas, i, j); };
  g.lineCap = 'round';
  if (type === 0) dessiner((x, y) => {            /* cercles concentriques */
    for (let k = 4; k >= 1; k--) { g.fillStyle = pal[k % pal.length]; g.beginPath(); g.arc(x, y, pas * 0.12 * k, 0, 7); g.fill(); }
  });
  if (type === 1) dessiner((x, y, i, j) => {      /* feuilles */
    g.save(); g.translate(x, y); g.rotate((i + j) * 0.9);
    g.fillStyle = pal[1]; g.beginPath(); g.ellipse(0, 0, pas * 0.42, pas * 0.16, 0, 0, 7); g.fill();
    g.strokeStyle = pal[2]; g.lineWidth = pas * 0.03; g.beginPath(); g.moveTo(-pas * 0.4, 0); g.lineTo(pas * 0.4, 0); g.stroke();
    g.fillStyle = pal[3]; g.beginPath(); g.arc(pas * 0.3, pas * 0.3, pas * 0.07, 0, 7); g.fill(); g.restore();
  });
  if (type === 2) dessiner((x, y) => {            /* losanges et points */
    g.fillStyle = pal[1]; g.beginPath(); g.moveTo(x, y - pas * 0.45); g.lineTo(x + pas * 0.3, y); g.lineTo(x, y + pas * 0.45); g.lineTo(x - pas * 0.3, y); g.fill();
    g.fillStyle = pal[2]; g.beginPath(); g.moveTo(x, y - pas * 0.25); g.lineTo(x + pas * 0.16, y); g.lineTo(x, y + pas * 0.25); g.lineTo(x - pas * 0.16, y); g.fill();
    g.fillStyle = pal[3]; g.beginPath(); g.arc(x + pas / 2, y, pas * 0.06, 0, 7); g.fill();
  });
  if (type === 3) dessiner((x, y) => {            /* éventails */
    for (let k = 5; k >= 1; k--) { g.fillStyle = pal[k % pal.length]; g.beginPath(); g.moveTo(x, y); g.arc(x, y, pas * 0.1 * k, Math.PI, 2 * Math.PI); g.fill(); }
  });
  if (type === 4) dessiner((x, y, i, j) => {      /* bulles */
    /* ⚠️ i et j valent -1 sur les bords : un modulo JavaScript d'un négatif est négatif,
       et un rayon négatif fait planter le canevas (vu au premier essai) */
    const m5 = (((i * 7 + j * 3) % 5) + 5) % 5, m3 = (((i + j) % 3) + 3) % 3, m4 = (((i + j + 1) % 4) + 4) % 4;
    const s = 0.08 + m5 * 0.05;
    g.fillStyle = pal[1 + m3]; g.beginPath(); g.arc(x, y, pas * s, 0, 7); g.fill();
    g.strokeStyle = pal[m4]; g.lineWidth = pas * 0.025; g.beginPath(); g.arc(x, y, pas * (s + 0.06), 0, 7); g.stroke();
  });
  if (type === 5) {                                /* vagues */
    for (let y = 0; y < W + pas; y += pas / 2) {
      g.strokeStyle = pal[1 + Math.floor(y / (pas / 2)) % 3]; g.lineWidth = pas * 0.14;
      g.beginPath(); for (let x = 0; x <= W; x += 4) g.lineTo(x, y + Math.sin(x / W * Math.PI * 2 * 2) * pas * 0.18); g.stroke();
    }
  }
  /* le grain du coton */
  for (let k = 0; k < 2200; k++) { g.fillStyle = `rgba(${r() < 0.5 ? '0,0,0' : '255,255,255'},${0.04 * r()})`; g.fillRect(r() * W, r() * W, 2, 2); }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 4;
  cache.set(cle, t);
  /* le décor (graines ≥ 40) recevra un vrai imprimé ; les vêtements des silhouettes gardent leur dessin */
  if (seed >= 40) waxDecor.push({ g, W, t, seed });
  return t;
}

/* LES WAX PHOTOGRAPHIQUES (vague 3, 2026-11-15) : les rouleaux, les piles et les coupons du décor étaient DESSINÉS par
   le code (cercles, feuilles, losanges) : ça se voyait. Après le premier écran, chaque dessin est remplacé par un vrai
   imprimé (`ressources/wax/wax-N.webp`, huit motifs originaux, 344 Ko en tout). Le motif est dessiné dans le même canevas et la
   texture se répète EN MIROIR : il se raccorde tout seul sur un rouleau, sans couture. Une image qui ne vient pas
   laisse le dessin. ⛔ Matière de décor, jamais le catalogue (`ressources/wax/LICENCE.md`). */
/* ⚠️ Chaque matière porte une COPIE de la texture (pour sa propre répétition). Redessiner le canevas et prévenir l'ORIGINAL
   ne suffit pas : three.js ne renvoie une texture à la carte graphique que si SA version change, et l'original n'est
   porté par aucune matière (vu le 2026-11-15 : les rouleaux gardaient leur dessin). On prévient donc chaque copie. */
const waxDecor = [], copiesWax = new Map();
export const etatWax = { poses: 0, attendus: 0 };   /* pour les contrôles */
export function chargerWaxPhotos(base, n = 8) {
  const images = {};
  etatWax.attendus += waxDecor.length;
  for (const w of waxDecor.splice(0)) {
    const k = 1 + (w.seed % n);
    (images[k] ||= new Promise((ok) => { const i = new Image(); i.onload = () => ok(i); i.onerror = () => ok(null); i.src = `${base}wax-${k}.webp`; }))
      .then((img) => {
        if (!img) return;
        /* l'imprimé en entier dans le canevas (motifs lisibles de loin : en mosaïque 2 × 2 ils devenaient une bouillie
           pastel) ; le raccord se fait par la répétition EN MIROIR de la texture */
        w.g.drawImage(img, 0, 0, w.W, w.W);
        for (const x of [w.t, ...(copiesWax.get(w.t) || [])]) x.wrapS = x.wrapT = THREE.MirroredRepeatWrapping;
        w.t.needsUpdate = true; for (const c of copiesWax.get(w.t) || []) c.needsUpdate = true; etatWax.poses++;
      });
  }
}

export function matWax(seed, palette, repeat = [1, 1], options = {}) {
  const origine = wax(seed, palette), t = origine.clone(); t.needsUpdate = true; t.repeat.set(repeat[0], repeat[1]);
  (copiesWax.get(origine) || copiesWax.set(origine, []).get(origine)).push(t);
  return new THREE.MeshStandardMaterial({ map: t, roughness: 0.82, ...options });
}

/* LES SURFACES VRAIES (vague 3, 2026-11-14) : un bruit doux calculé sur place, partagé (une texture par usage),
   qui sert de relief ou de rugosité. Le réel vient de l'imperfection : aucune grande surface parfaitement unie. */
const surfaces = new Map();
function bruitDoux(nom, { taille = 256, echelles = [32, 12, 4], forces = [0.55, 0.3, 0.15], base = 0.5, contraste = 1, graineN = 3 } = {}) {
  if (surfaces.has(nom)) return surfaces.get(nom);
  const c = document.createElement('canvas'); c.width = c.height = taille; const g = c.getContext('2d');
  const img = g.createImageData(taille, taille), r = graine(graineN);
  /* des couches de bruit de valeur lissé, raccordées (la texture se répète sans couture) */
  const couches = echelles.map((e) => { const n = Math.max(2, Math.round(taille / e)); return { n, v: Array.from({ length: n * n }, () => r()) }; });
  const lisse = (x) => x * x * (3 - 2 * x);
  for (let y = 0; y < taille; y++) for (let x = 0; x < taille; x++) {
    let v = 0;
    couches.forEach(({ n, v: tab }, k) => {
      const fx = x / taille * n, fy = y / taille * n, ix = Math.floor(fx), iy = Math.floor(fy), tx = lisse(fx - ix), ty = lisse(fy - iy);
      const at = (i, j) => tab[((j % n) * n + (i % n))];
      const a = at(ix, iy) + (at(ix + 1, iy) - at(ix, iy)) * tx, b = at(ix, iy + 1) + (at(ix + 1, iy + 1) - at(ix, iy + 1)) * tx;
      v += (a + (b - a) * ty - 0.5) * forces[k];
    });
    const o = Math.max(0, Math.min(255, Math.round((base + v * contraste) * 255))), i = (y * taille + x) * 4;
    img.data[i] = img.data[i + 1] = img.data[i + 2] = o; img.data[i + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  const tx = new THREE.CanvasTexture(c); tx.wrapS = tx.wrapT = THREE.RepeatWrapping; tx.colorSpace = THREE.NoColorSpace;
  surfaces.set(nom, tx); return tx;
}
const repete = (tx, x, y) => { const c = tx.clone(); c.repeat.set(x, y); c.needsUpdate = true; return c; };
/* `?sans-relief` : les matières d'avant la vague 3 (sans reliefs ni rugosités calculés, velours simple), pour MESURER ce
   qu'ils coûtent : un relief sur un grand mur est une lecture de texture et une dérivée par pixel */
const SANS_RELIEF = typeof location !== 'undefined' && new URLSearchParams(location.search).has('sans-relief');
const relief = (f) => SANS_RELIEF ? {} : f();

export const MATIERES = {
  creme: () => new THREE.MeshStandardMaterial({ color: 0xf4efe6, roughness: 0.92, ...relief(() => ({ bumpMap: repete(bruitDoux('enduit'), 3, 3), bumpScale: 0.6 })) }),
  platre: () => new THREE.MeshStandardMaterial({ color: 0xf7f3ec, roughness: 0.96, ...relief(() => ({ bumpMap: repete(bruitDoux('enduit'), 4, 4), bumpScale: 0.7 })) }),
  laque: () => new THREE.MeshStandardMaterial({ color: 0xfbf8f3, roughness: 0.28, metalness: 0 }),
  chene: () => {
    const c = document.createElement('canvas'); c.width = 256; c.height = 512; const g = c.getContext('2d');
    g.fillStyle = '#c9a57b'; g.fillRect(0, 0, 256, 512); const r = graine(5);
    for (let i = 0; i < 90; i++) { g.strokeStyle = `rgba(${120 + r() * 40},${84 + r() * 30},${50 + r() * 20},${0.12 + r() * 0.2})`; g.lineWidth = 1 + r() * 3;
      const x = r() * 256; g.beginPath(); g.moveTo(x, 0); g.bezierCurveTo(x + r() * 20 - 10, 170, x + r() * 20 - 10, 340, x + r() * 16 - 8, 512); g.stroke(); }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping;
    return new THREE.MeshStandardMaterial({ map: t, roughness: 0.55, ...relief(() => ({ bumpMap: t, bumpScale: 0.8 })) });
  },
  /* le laiton patiné : une rugosité qui varie À PEINE (0,22 à 0,38 : traces, poli inégal), jamais un chrome parfait.
     ⚠️ À 0,9 de contraste il paraissait TACHÉ, sali (gros plan du 2026-11-15) */
  laiton: () => new THREE.MeshStandardMaterial({ color: 0xc9a254, roughness: 0.3, metalness: 1, ...relief(() => ({ roughness: 1, roughnessMap: repete(bruitDoux('patine', { base: 0.3, contraste: 0.3, echelles: [48, 16, 6] }), 2, 2) })) }),
  encre: () => new THREE.MeshStandardMaterial({ color: 0x141215, roughness: 0.5 }),
  magenta: () => new THREE.MeshStandardMaterial({ color: 0xe6007e, roughness: 0.6 }),
  /* le velours boit la lumière de face et la renvoie sur ses bords (le « sheen ») : c'est ce qui le fait velours */
  velours: (couleur = 0xb0105f) => SANS_RELIEF ? new THREE.MeshStandardMaterial({ color: couleur, roughness: 0.95 })
    : new THREE.MeshPhysicalMaterial({ color: couleur, roughness: 0.9, sheen: 1, sheenRoughness: 0.42,
      sheenColor: new THREE.Color(couleur).lerp(new THREE.Color(0xffe0ee), 0.45), bumpMap: repete(bruitDoux('enduit'), 6, 6), bumpScale: 0.25 }),
  verre: () => new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.05, metalness: 0, transmission: 0, transparent: true, opacity: 0.12, depthWrite: false }),
  porcelaine: () => new THREE.MeshStandardMaterial({ color: 0xefe8dc, roughness: 0.38 }),
  /* le sol crème poli : sa brillance vient de l'environnement ; au niveau haut, un vrai reflet s'y ajoute */
  sol: () => {
    const c = document.createElement('canvas'); c.width = c.height = 1024; const g = c.getContext('2d');
    g.fillStyle = '#efe5d5'; g.fillRect(0, 0, 1024, 1024); const r = graine(21);
    for (let i = 0; i < 40; i++) { g.strokeStyle = `rgba(190,170,140,${0.05 + r() * 0.08})`; g.lineWidth = 1 + r() * 2.5;
      g.beginPath(); let x = r() * 1024, y = r() * 1024; g.moveTo(x, y); for (let k = 0; k < 8; k++) { x += r() * 120 - 60; y += r() * 120 - 40; g.lineTo(x, y); } g.stroke(); }
    g.strokeStyle = 'rgba(160,140,115,.35)'; g.lineWidth = 2;
    for (let k = 0; k <= 1024; k += 512) { g.beginPath(); g.moveTo(k, 0); g.lineTo(k, 1024); g.stroke(); g.beginPath(); g.moveTo(0, k); g.lineTo(1024, k); g.stroke(); }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(8, 6); t.anisotropy = 8;
    /* la rugosité varie (passage, cire inégale) : le reflet se trouble par endroits, comme un vrai sol poli */
    return new THREE.MeshStandardMaterial({ map: t, roughness: 0.16, metalness: 0, envMapIntensity: 1.3, ...relief(() => ({ roughness: 1, roughnessMap: repete(bruitDoux('cire', { base: 0.17, contraste: 0.32, echelles: [64, 20, 6] }), 3, 2) })) });
  },
};

/* une flaque de lumière douce au sol (le cône d'un spot) : cher en vraie lumière, gratuit en image */
let texFlaque = null;
export function flaqueLumiere(rayon = 1, couleur = 0xffe2b0, intensite = 0.6) {
  if (!texFlaque) {
    const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.55, 'rgba(255,255,255,.35)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 128, 128); texFlaque = new THREE.CanvasTexture(c);
  }
  const m = new THREE.Mesh(new THREE.CircleGeometry(rayon, 32),
    new THREE.MeshBasicMaterial({ map: texFlaque, color: couleur, transparent: true, opacity: intensite, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false }));
  m.rotation.x = -Math.PI / 2; m.position.y = 0.006; m.renderOrder = 1;
  return m;
}

/* l'ombre ronde sous un personnage ou un podium */
let texOmbre = null;
/* L'OMBRE DE CONTACT (REALISME.md R2) : là où un corps touche le sol, une ombre SERRÉE et foncée, au cœur
   d'une ombre LARGE et douce (une seule tache, pâle, ne posait pas les personnages : ils flottaient).
   ⚠️ renderOrder 2 : en qualité haute le sol est translucide (au-dessus de son miroir), et une ombre
   dessinée avant lui disparaissait sous lui selon l'endroit. */
export function ombreContact(rayon = 0.42, force = 0.4) {
  const g = new THREE.Group();
  const large = ombreRonde(rayon, force), serree = ombreRonde(rayon * 0.42, Math.min(0.8, force * 1.7));
  serree.position.y = 0.005;
  for (const m of [large, serree]) m.renderOrder = 2;
  g.add(large, serree); g.userData = { large, serree };
  return g;
}
export function ombreRonde(rayon = 0.4, force = 0.35) {
  if (!texOmbre) {
    const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(0,0,0,1)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 128, 128); texOmbre = new THREE.CanvasTexture(c);
  }
  const m = new THREE.Mesh(new THREE.CircleGeometry(rayon, 24), new THREE.MeshBasicMaterial({ map: texOmbre, transparent: true, opacity: force, depthWrite: false, color: 0x2a1a10 }));
  m.rotation.x = -Math.PI / 2; m.position.y = 0.004;
  return m;
}

// LA BOBINE · le moteur de dessin. Un seul code compose chaque image, pour l'aperçu comme pour l'export :
// ce qu'on voit à l'écran est ce qui sort dans le fichier.
//
// `obtenir(clip, tempsSource, role)` rend une source { l, h, peindre(ctx, sx, sy, sl, sh, dx, dy, dl, dh) } ou null.

import { dureeClip, finClip, tempsSource, principale, clamp, valeur } from './model.js';

export const actif = (c, t) => t >= c.debut - 1e-6 && t < finClip(c) - 1e-6;
const lisse = (k) => k * k * (3 - 2 * k);
const sortieDouce = (k) => 1 - (1 - k) * (1 - k);
const rebond = (k) => { const c1 = 1.70158; const c3 = c1 + 1; return 1 + c3 * (k - 1) ** 3 + c1 * (k - 1) ** 2; };
const tout = (img, ctx, x, y, l, h) => img.peindre(ctx, 0, 0, img.l, img.h, x, y, l, h);

export const FILTRE_OK = typeof CanvasRenderingContext2D !== 'undefined' && 'filter' in CanvasRenderingContext2D.prototype;

/** Les filtres maison. `css` sert à la toile ET aux vignettes du panneau ; `teinte` est un voile de couleur. */
export const FILTRES = {
  aucun: { nom: 'Aucun' },
  cotonou: { nom: 'Cotonou', css: (i) => `saturate(${1 + 0.25 * i}) contrast(${1 + 0.08 * i})`, teinte: ['#ff9a3c', 0.12] },
  harmattan: { nom: 'Harmattan', css: (i) => `sepia(${0.35 * i}) saturate(${1 - 0.3 * i}) brightness(${1 + 0.06 * i}) contrast(${1 - 0.08 * i})`, teinte: ['#e9c48c', 0.1] },
  lagune: { nom: 'Lagune', css: (i) => `saturate(${1 + 0.12 * i}) hue-rotate(${-8 * i}deg)`, teinte: ['#2fb8b0', 0.12] },
  nuit: { nom: 'Nuit', css: (i) => `brightness(${1 - 0.18 * i}) contrast(${1 + 0.15 * i}) saturate(${1 - 0.25 * i})`, teinte: ['#2b4fff', 0.12] },
  nb: { nom: 'Noir et blanc', css: (i) => `grayscale(${i}) contrast(${1 + 0.15 * i})` },
  retro: { nom: 'Rétro', css: (i) => `sepia(${0.55 * i}) contrast(${1 + 0.1 * i}) saturate(${1 - 0.1 * i})`, teinte: ['#ff6b4a', 0.06] },
  eclat: { nom: 'Éclat', css: (i) => `saturate(${1 + 0.55 * i}) contrast(${1 + 0.12 * i})` },
  doux: { nom: 'Doux', css: (i) => `contrast(${1 - 0.15 * i}) brightness(${1 + 0.08 * i}) saturate(${1 - 0.1 * i})`, teinte: ['#ffe2d0', 0.08] },
};

export function cssFiltre(c) {
  const r = c.reglages || {};
  const p = [];
  if (r.luminosite) p.push(`brightness(${(1 + r.luminosite * 0.6).toFixed(3)})`);
  if (r.contraste) p.push(`contrast(${(1 + r.contraste * 0.8).toFixed(3)})`);
  if (r.saturation) p.push(`saturate(${Math.max(0, 1 + r.saturation).toFixed(3)})`);
  const f = c.filtre && FILTRES[c.filtre.nom];
  if (f && f.css) p.push(f.css(c.filtre.intensite ?? 1));
  return p.join(' ');
}

function teintes(c) {
  const res = [];
  const t = (c.reglages && c.reglages.temperature) || 0;
  if (t > 0) res.push(['#ff9a3c', 0.25 * t]);
  if (t < 0) res.push(['#3c8cff', -0.25 * t]);
  const f = c.filtre && FILTRES[c.filtre.nom];
  if (f && f.teinte) res.push([f.teinte[0], f.teinte[1] * (c.filtre.intensite ?? 1)]);
  return res;
}

export function tempsPrecedent(a, fps = 30) {
  return a.genre === 'video' ? Math.max(a.entree, a.sortie - 1 / fps) : 0;
}

export function enTransition(pr, i, t) {
  const c = pr.clips[i];
  const tr = c && c.transition;
  return i > 0 && tr && tr.type !== 'aucune' && t < c.debut + tr.duree;
}

/** Les images sources dont l'instant t a besoin, dans l'ordre où le moteur les demandera. */
export function besoinsA(p, t, fps = 30) {
  const besoins = [];
  const pr = principale(p);
  const i = pr.clips.findIndex((c) => actif(c, t));
  if (i >= 0) {
    const b = pr.clips[i];
    if (enTransition(pr, i, t)) {
      const a = pr.clips[i - 1];
      besoins.push({ clip: a, temps: tempsPrecedent(a, fps), role: 'precedent' });
    }
    besoins.push({ clip: b, temps: tempsSource(b, t), role: 'principal' });
  }
  for (const piste of p.pistes) {
    if (piste.genre !== 'superposition') continue;
    for (const c of piste.clips) if (actif(c, t)) besoins.push({ clip: c, temps: tempsSource(c, t), role: 'superposition' });
  }
  return besoins;
}

export function fondus(c, t) {
  const d = dureeClip(c);
  const lt = t - c.debut;
  let a = 1;
  if (c.fonduEntree > 0) a *= clamp(lt / c.fonduEntree, 0, 1);
  if (c.fonduSortie > 0) a *= clamp((d - lt) / c.fonduSortie, 0, 1);
  return a;
}

function facteurMouvement(c, t) {
  const k = clamp((t - c.debut) / Math.max(0.001, dureeClip(c)), 0, 1);
  if (c.mouvement === 'avant') return 1 + 0.15 * k;
  if (c.mouvement === 'arriere') return 1.15 - 0.15 * k;
  return 1;
}

/** Animation d'entrée et de sortie d'un clip : k va de 0 (caché) à 1 (en place). */
function animClip(c, t, W, H) {
  const r = { alpha: 1, zoom: 1, dx: 0, dy: 0, rot: 0 };
  const d = dureeClip(c);
  const lt = t - c.debut;
  const appliquer = (anim, k) => {
    if (!anim || anim.type === 'aucune' || k >= 1) return;
    const kk = clamp(k, 0, 1);
    const e = sortieDouce(kk);
    switch (anim.type) {
      case 'fondu': r.alpha *= e; break;
      case 'zoom-avant': r.zoom *= 0.5 + 0.5 * e; r.alpha *= e; break;
      case 'zoom-arriere': r.zoom *= 1.5 - 0.5 * e; r.alpha *= e; break;
      case 'glisse-gauche': r.dx -= (1 - e) * W; break;
      case 'glisse-droite': r.dx += (1 - e) * W; break;
      case 'glisse-haut': r.dy -= (1 - e) * H; break;
      case 'glisse-bas': r.dy += (1 - e) * H; break;
      case 'rebond': r.zoom *= Math.max(0.01, rebond(kk)); break;
      case 'tourne': r.rot -= (1 - e) * 120; r.zoom *= 0.6 + 0.4 * e; r.alpha *= e; break;
      default:
    }
  };
  if (c.animEntree) appliquer(c.animEntree, lt / Math.max(0.05, c.animEntree.duree || 0.5));
  if (c.animSortie) appliquer(c.animSortie, (d - lt) / Math.max(0.05, c.animSortie.duree || 0.5));
  return r;
}

// ---------- toiles de travail ----------
let mini = null;
let moyen = null;
let travail = null;
function toile(l, h, ancienne) {
  const c = ancienne || (typeof OffscreenCanvas !== 'undefined' ? new OffscreenCanvas(l, h) : document.createElement('canvas'));
  if (c.width !== l) c.width = l;
  if (c.height !== h) c.height = h;
  return c;
}

/** Fond flouté sans ctx.filter (Safari) : on réduit l'image puis on l'agrandit. */
function fondFlou(ctx, img, W, H, alpha, dx) {
  const pl = Math.max(8, Math.round(W / 24));
  const ph = Math.max(8, Math.round(H / 24));
  mini = toile(pl, ph, mini);
  moyen = toile(pl * 4, ph * 4, moyen);
  const m = mini.getContext('2d');
  const s = Math.max(pl / img.l, ph / img.h);
  m.clearRect(0, 0, pl, ph);
  tout(img, m, (pl - img.l * s) / 2, (ph - img.h * s) / 2, img.l * s, img.h * s);
  const mo = moyen.getContext('2d');
  mo.imageSmoothingEnabled = true;
  mo.drawImage(mini, 0, 0, moyen.width, moyen.height);
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(moyen, dx || 0, 0, W, H);
  ctx.fillStyle = 'rgba(0,0,0,0.22)';
  ctx.fillRect(dx || 0, 0, W, H);
  ctx.restore();
}

function hexRgb(h) {
  const v = parseInt(String(h || '#00d000').slice(1), 16);
  return [(v >> 16) & 255, (v >> 8) & 255, v & 255];
}

/** Fond vert : on éteint les pixels proches de la couleur clé (distance mesurée en chrominance). */
export function appliquerChroma(px, ch) {
  const [kr, kg, kb] = hexRgb(ch.couleur);
  const kcb = -0.168736 * kr - 0.331264 * kg + 0.5 * kb;
  const kcr = 0.5 * kr - 0.418688 * kg - 0.081312 * kb;
  const a0 = ch.seuil ?? 0.25;
  const a1 = a0 + Math.max(0.01, ch.douceur ?? 0.1);
  const vert = kg >= kr && kg >= kb;
  for (let i = 0; i < px.length; i += 4) {
    const r = px[i]; const g = px[i + 1]; const b = px[i + 2];
    const cb = -0.168736 * r - 0.331264 * g + 0.5 * b;
    const cr = 0.5 * r - 0.418688 * g - 0.081312 * b;
    const dist = Math.hypot(cb - kcb, cr - kcr) / 255;
    if (dist >= a1) continue;
    const k = dist <= a0 ? 0 : (dist - a0) / (a1 - a0);
    px[i + 3] = Math.round(px[i + 3] * k);
    if (vert && k > 0) { const m = Math.max(r, b); if (g > m) px[i + 1] = Math.round(m + (g - m) * k); }
  }
}

function dessinerMasque(o, m, l, h) {
  const taille = clamp(m.taille ?? 0.8, 0.05, 1.5);
  const doux = clamp(m.adoucir ?? 0.15, 0, 1);
  o.fillStyle = '#000';
  if (m.forme === 'cercle') {
    const r = Math.max(1, (taille * Math.min(l, h)) / 2);
    const g = o.createRadialGradient(l / 2, h / 2, r * (1 - doux), l / 2, h / 2, r);
    g.addColorStop(0, '#000');
    g.addColorStop(1, 'rgba(0,0,0,0)');
    o.fillStyle = g;
    o.fillRect(0, 0, l, h);
  } else if (m.forme === 'rectangle') {
    const ml = taille * l;
    const mh = taille * h;
    o.beginPath();
    if (o.roundRect) o.roundRect((l - ml) / 2, (h - mh) / 2, ml, mh, (doux * Math.min(ml, mh)) / 2);
    else o.rect((l - ml) / 2, (h - mh) / 2, ml, mh);
    o.fill();
  } else if (m.forme === 'bande') {
    const bh = taille * h;
    const fe = Math.max(1, (doux * bh) / 2);
    const y0 = (h - bh) / 2;
    const g = o.createLinearGradient(0, 0, 0, h);
    const st = (y) => clamp(y / h, 0, 1);
    g.addColorStop(st(y0 - fe), 'rgba(0,0,0,0)');
    g.addColorStop(st(y0), '#000');
    g.addColorStop(st(y0 + bh), '#000');
    g.addColorStop(st(y0 + bh + fe), 'rgba(0,0,0,0)');
    o.fillStyle = g;
    o.fillRect(0, 0, l, h);
  }
}

/** Prépare un clip dans une toile de travail quand il a besoin d'un traitement de pixels (fond vert, masque, teinte). */
function preparer(img, sx, sy, sl, sh, dl, dh, c, voiles) {
  const r = Math.min(1, 1600 / Math.max(dl, dh, 1));
  const ol = Math.max(1, Math.round(dl * r));
  const oh = Math.max(1, Math.round(dh * r));
  travail = toile(ol, oh, travail);
  const o = travail.getContext('2d', { willReadFrequently: true });
  o.save();
  o.globalCompositeOperation = 'source-over';
  o.globalAlpha = 1;
  o.clearRect(0, 0, ol, oh);
  img.peindre(o, sx, sy, sl, sh, 0, 0, ol, oh);
  if (c.chroma && c.chroma.actif) {
    const d = o.getImageData(0, 0, ol, oh);
    appliquerChroma(d.data, c.chroma);
    o.putImageData(d, 0, 0);
  }
  for (const [couleur, a] of voiles) {
    o.globalCompositeOperation = 'source-atop';
    o.globalAlpha = clamp(a, 0, 1);
    o.fillStyle = couleur;
    o.fillRect(0, 0, ol, oh);
  }
  o.globalAlpha = 1;
  const m = c.masque;
  if (m && m.forme && m.forme !== 'aucun') {
    o.globalCompositeOperation = m.inverser ? 'destination-out' : 'destination-in';
    dessinerMasque(o, m, ol, oh);
  }
  o.restore();
  return travail;
}

function peindreMedia(ctx, img, c, W, H, o, t) {
  const rc = c.recadrage || {};
  const sx = (rc.g || 0) * img.l;
  const sy = (rc.h || 0) * img.h;
  const sl = Math.max(1, img.l * (1 - (rc.g || 0) - (rc.d || 0)));
  const sh = Math.max(1, img.h * (1 - (rc.h || 0) - (rc.b || 0)));
  const an = animClip(c, t, W, H);
  const base = (c.ajustement === 'remplir' ? Math.max : Math.min)(W / sl, H / sh);
  const s = base * valeur(c, 'echelle', t) * (o.zoom ?? 1) * an.zoom * facteurMouvement(c, t);
  const dl = sl * s;
  const dh = sh * s;
  const x = W * valeur(c, 'cx', t) + (o.dx || 0) + an.dx;
  const y = H * valeur(c, 'cy', t) + (o.dy || 0) + an.dy;
  const rot = (valeur(c, 'rotation', t) || 0) + (o.rot || 0) + an.rot;
  const alpha = clamp((o.alpha ?? 1) * an.alpha, 0, 1);
  const cadre = { x, y, l: dl, h: dh, rotation: rot };
  if (alpha <= 0) return cadre;
  ctx.save();
  ctx.globalAlpha = alpha;
  if (c.fusion && c.fusion !== 'source-over') ctx.globalCompositeOperation = c.fusion;
  const css = cssFiltre(c);
  if (css && FILTRE_OK) ctx.filter = css;
  ctx.translate(x, y);
  if (rot) ctx.rotate((rot * Math.PI) / 180);
  if (c.miroirH || c.miroirV) ctx.scale(c.miroirH ? -1 : 1, c.miroirV ? -1 : 1);
  const voiles = teintes(c);
  const avance = (c.chroma && c.chroma.actif) || (c.masque && c.masque.forme && c.masque.forme !== 'aucun') || voiles.length;
  if (avance) ctx.drawImage(preparer(img, sx, sy, sl, sh, dl, dh, c, voiles), -dl / 2, -dh / 2, dl, dh);
  else img.peindre(ctx, sx, sy, sl, sh, -dl / 2, -dh / 2, dl, dh);
  ctx.restore();
  return cadre;
}

// ---------- texte ----------
function lignesDe(ctx, texte, max) {
  const res = [];
  for (const para of String(texte ?? '').split('\n')) {
    const mots = para.split(/\s+/).filter(Boolean);
    if (!mots.length) { res.push(''); continue; }
    let l = mots[0];
    for (const m of mots.slice(1)) {
      const essai = `${l} ${m}`;
      if (ctx.measureText(essai).width <= max) l = essai;
      else { res.push(l); l = m; }
    }
    res.push(l);
  }
  return res;
}

function rectArrondi(ctx, x, y, l, h, r) {
  ctx.beginPath();
  if (ctx.roundRect) ctx.roundRect(x, y, l, h, r);
  else ctx.rect(x, y, l, h);
  ctx.fill();
}

export function dessinerTexte(ctx, c, t, W, H) {
  const lt = t - c.debut;
  const d = c.duree;
  const px = Math.max(6, (valeur(c, 'taille', t) || 0.06) * H);
  ctx.save();
  ctx.font = `${c.poids || 700} ${px}px "${c.police}", "Instrument Sans", system-ui, sans-serif`;
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'left';
  const lignes = lignesDe(ctx, c.texte, W * 0.86);
  const largeurs = lignes.map((l) => ctx.measureText(l).width);

  let visibles = lignes;
  if (c.anim === 'machine') {
    let reste = Math.floor(lignes.join('').length * clamp(lt / Math.min(1.4, d * 0.6), 0, 1));
    visibles = lignes.map((l) => { const v = l.slice(0, Math.max(0, reste)); reste -= l.length; return v; });
  }
  const e = clamp(lt / 0.45, 0, 1);
  let alpha = valeur(c, 'opacite', t) ?? 1;
  let dy = 0;
  let s = 1;
  if (c.anim && c.anim !== 'aucune') alpha *= clamp((d - lt) / 0.3, 0, 1);
  if (c.anim === 'fondu') alpha *= e;
  if (c.anim === 'monte') { alpha *= e; dy = (1 - sortieDouce(e)) * H * 0.04; }
  if (c.anim === 'pop') { s = 0.4 + 0.6 * rebond(e); alpha *= clamp(e * 3, 0, 1); }

  const lh = px * 1.2;
  const bl = Math.max(1, ...largeurs);
  const bh = lignes.length * lh;
  const x0 = (valeur(c, 'cx', t) ?? 0.5) * W;
  const y0 = (valeur(c, 'cy', t) ?? 0.5) * H + dy;
  const rot = valeur(c, 'rotation', t) || 0;
  ctx.translate(x0, y0);
  if (rot) ctx.rotate((rot * Math.PI) / 180);
  ctx.scale(s, s);
  ctx.globalAlpha = clamp(alpha, 0, 1);
  const pad = px * 0.3;
  if (c.boite === 'pastille') {
    ctx.fillStyle = c.couleurBoite || '#000';
    rectArrondi(ctx, -bl / 2 - pad * 1.5, -bh / 2 - pad, bl + pad * 3, bh + pad * 2, px * 0.45);
  }
  lignes.forEach((l, j) => {
    const lf = largeurs[j];
    const y = -bh / 2 + lh * (j + 0.5);
    const x = c.alignement === 'gauche' ? -bl / 2 : c.alignement === 'droite' ? bl / 2 - lf : -lf / 2;
    if (c.boite === 'bande' && l) {
      ctx.fillStyle = c.couleurBoite || '#000';
      rectArrondi(ctx, x - pad, y - lh / 2, lf + pad * 2, lh, px * 0.12);
    }
    const v = visibles[j];
    if (!v) return;
    if (c.contour) {
      ctx.lineJoin = 'round';
      ctx.lineWidth = px * 0.14;
      ctx.strokeStyle = c.couleurContour || '#000';
      ctx.strokeText(v, x, y);
    }
    ctx.fillStyle = c.couleur || '#fff';
    ctx.fillText(v, x, y);
  });
  ctx.restore();
  return { x: x0, y: y0, l: (bl + pad * 3) * s, h: (bh + pad * 2) * s, rotation: rot };
}

/**
 * Compose l'image de l'instant t. Rend la position de chaque clip dessiné (pour le cadre de sélection).
 */
export function dessinerImage(ctx, p, t, W, H, obtenir, fps = 30) {
  const cadres = {};
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  ctx.globalCompositeOperation = 'source-over';
  ctx.filter = 'none';
  ctx.fillStyle = (p.fond && p.fond.couleur) || '#000';
  ctx.fillRect(0, 0, W, H);
  const flou = p.fond && p.fond.type === 'flou';

  const couche = (clip, img, alpha, o = {}) => {
    if (!img || alpha <= 0) return;
    const tc = o.tClip ?? t;
    ctx.save();
    if (o.decoupe) o.decoupe(ctx);
    if (flou) fondFlou(ctx, img, W, H, alpha, o.dx);
    cadres[clip.id] = peindreMedia(ctx, img, clip, W, H, { ...o, alpha }, tc);
    ctx.restore();
  };
  const blanc = (a) => {
    if (a <= 0) return;
    ctx.save();
    ctx.globalAlpha = clamp(a, 0, 1);
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, W, H);
    ctx.restore();
  };

  const pr = principale(p);
  const i = pr.clips.findIndex((c) => actif(c, t));
  if (i >= 0) {
    const b = pr.clips[i];
    const alphaB = (valeur(b, 'opacite', t) ?? 1) * fondus(b, t);
    if (enTransition(pr, i, t)) {
      const a = pr.clips[i - 1];
      const imgA = obtenir(a, tempsPrecedent(a, fps), 'precedent');
      const imgB = obtenir(b, tempsSource(b, t), 'principal');
      const k = clamp((t - b.debut) / b.transition.duree, 0, 1);
      const e = lisse(k);
      const finA = finClip(a) - 1e-3;
      const alphaA = valeur(a, 'opacite', finA) ?? 1;
      const A = (alpha, o = {}) => couche(a, imgA, alpha, { ...o, tClip: finA });
      switch (b.transition.type) {
        case 'fondu': A(alphaA); couche(b, imgB, alphaB * e); break;
        case 'noir':
          if (k < 0.5) A(alphaA * (1 - lisse(k * 2)));
          else couche(b, imgB, alphaB * lisse(k * 2 - 1));
          break;
        case 'glisse': A(alphaA, { dx: -e * W }); couche(b, imgB, alphaB, { dx: (1 - e) * W }); break;
        case 'glisse-haut': A(alphaA, { dy: -e * H }); couche(b, imgB, alphaB, { dy: (1 - e) * H }); break;
        case 'zoom': A(alphaA * (1 - e), { zoom: 1 + 0.35 * e }); couche(b, imgB, alphaB * e, { zoom: 1.35 - 0.35 * e }); break;
        case 'balayage':
          A(alphaA);
          couche(b, imgB, alphaB, { decoupe: (c) => { c.beginPath(); c.rect(0, 0, e * W, H); c.clip(); } });
          break;
        case 'rideau':
          A(alphaA);
          couche(b, imgB, alphaB, { decoupe: (c) => { c.beginPath(); c.rect(0, 0, W, e * H); c.clip(); } });
          break;
        case 'iris':
          A(alphaA);
          couche(b, imgB, alphaB, { decoupe: (c) => { c.beginPath(); c.arc(W / 2, H / 2, Math.max(0.5, (e * Math.hypot(W, H)) / 2), 0, Math.PI * 2); c.clip(); } });
          break;
        case 'flash':
          if (k < 0.5) { A(alphaA); blanc(lisse(k * 2)); } else { couche(b, imgB, alphaB); blanc(1 - lisse(k * 2 - 1)); }
          break;
        case 'tourbillon':
          A(alphaA * (1 - e), { zoom: 1 + 0.5 * e, rot: 90 * e });
          couche(b, imgB, alphaB * e, { zoom: 1.5 - 0.5 * e, rot: -90 * (1 - e) });
          break;
        default: couche(b, imgB, alphaB);
      }
    } else {
      couche(b, obtenir(b, tempsSource(b, t), 'principal'), alphaB);
    }
  }

  for (const piste of p.pistes) {
    if (piste.genre !== 'superposition') continue;
    for (const c of piste.clips) {
      if (!actif(c, t)) continue;
      const img = obtenir(c, tempsSource(c, t), 'superposition');
      if (!img) continue;
      cadres[c.id] = peindreMedia(ctx, img, c, W, H, { alpha: (valeur(c, 'opacite', t) ?? 1) * fondus(c, t) }, t);
    }
  }
  for (const piste of p.pistes) {
    if (piste.genre !== 'texte') continue;
    for (const c of piste.clips) if (actif(c, t)) cadres[c.id] = dessinerTexte(ctx, c, t, W, H);
  }
  ctx.restore();
  return cadres;
}

/** Nombre d'images à produire pour un projet. */
export const nombreImages = (duree, fps) => Math.max(1, Math.ceil(duree * fps - 1e-6));

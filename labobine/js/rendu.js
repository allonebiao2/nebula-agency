// LA BOBINE · le moteur de dessin. Un seul code compose chaque image, pour l'aperçu comme pour l'export :
// ce qu'on voit à l'écran est ce qui sort dans le fichier.
//
// `obtenir(clip, tempsSource, role)` rend une source dessinable { l, h, peindre(ctx, x, y, l, h) } ou null.

import { dureeClip, finClip, tempsSource, principale, clamp } from './model.js';

export const actif = (c, t) => t >= c.debut - 1e-6 && t < finClip(c) - 1e-6;
const lisse = (k) => k * k * (3 - 2 * k);
const sortieDouce = (k) => 1 - (1 - k) * (1 - k);
const rebond = (k) => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * (k - 1) ** 3 + c1 * (k - 1) ** 2; };

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

// ---------- fond flouté, sans ctx.filter (Safari ne le connaît pas) ----------
let mini = null;
let moyen = null;
function toile(l, h, ancienne) {
  const c = ancienne || (typeof OffscreenCanvas !== 'undefined' ? new OffscreenCanvas(l, h) : document.createElement('canvas'));
  if (c.width !== l) c.width = l;
  if (c.height !== h) c.height = h;
  return c;
}
function fondFlou(ctx, img, W, H, alpha, dx) {
  const pl = Math.max(8, Math.round(W / 24));
  const ph = Math.max(8, Math.round(H / 24));
  mini = toile(pl, ph, mini);
  moyen = toile(pl * 4, ph * 4, moyen);
  const m = mini.getContext('2d');
  const s = Math.max(pl / img.l, ph / img.h);
  m.clearRect(0, 0, pl, ph);
  img.peindre(m, (pl - img.l * s) / 2, (ph - img.h * s) / 2, img.l * s, img.h * s);
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

function peindreMedia(ctx, img, c, W, H, o = {}) {
  const base = (c.ajustement === 'remplir' ? Math.max : Math.min)(W / img.l, H / img.h);
  const s = base * (c.echelle ?? 1) * (o.zoom ?? 1);
  const dl = img.l * s;
  const dh = img.h * s;
  const x = W * (c.cx ?? 0.5) + (o.dx || 0);
  const y = H * (c.cy ?? 0.5);
  ctx.save();
  ctx.globalAlpha = clamp(o.alpha ?? 1, 0, 1);
  ctx.translate(x, y);
  if (c.rotation) ctx.rotate((c.rotation * Math.PI) / 180);
  img.peindre(ctx, -dl / 2, -dh / 2, dl, dh);
  ctx.restore();
  return { x, y, l: dl, h: dh, rotation: c.rotation || 0 };
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
  const px = Math.max(6, (c.taille || 0.06) * H);
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
  let alpha = c.opacite ?? 1;
  let dy = 0;
  let s = 1;
  if (c.anim && c.anim !== 'aucune') alpha *= clamp((d - lt) / 0.3, 0, 1);
  if (c.anim === 'fondu') alpha *= e;
  if (c.anim === 'monte') { alpha *= e; dy = (1 - sortieDouce(e)) * H * 0.04; }
  if (c.anim === 'pop') { s = 0.4 + 0.6 * rebond(e); alpha *= clamp(e * 3, 0, 1); }

  const lh = px * 1.2;
  const bl = Math.max(1, ...largeurs);
  const bh = lignes.length * lh;
  const x0 = (c.cx ?? 0.5) * W;
  const y0 = (c.cy ?? 0.5) * H + dy;
  ctx.translate(x0, y0);
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
  return { x: x0, y: y0, l: (bl + pad * 3) * s, h: (bh + pad * 2) * s, rotation: 0 };
}

/**
 * Compose l'image de l'instant t. Rend la position de chaque clip dessiné (pour le cadre de sélection).
 */
export function dessinerImage(ctx, p, t, W, H, obtenir, fps = 30) {
  const cadres = {};
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  ctx.fillStyle = (p.fond && p.fond.couleur) || '#000';
  ctx.fillRect(0, 0, W, H);
  const flou = p.fond && p.fond.type === 'flou';

  const couche = (clip, img, alpha, o = {}) => {
    if (!img || alpha <= 0) return;
    if (flou) fondFlou(ctx, img, W, H, alpha, o.dx);
    cadres[clip.id] = peindreMedia(ctx, img, clip, W, H, { ...o, alpha, zoom: (o.zoom || 1) * facteurMouvement(clip, o.tClip ?? t) });
  };

  const pr = principale(p);
  const i = pr.clips.findIndex((c) => actif(c, t));
  if (i >= 0) {
    const b = pr.clips[i];
    const alphaB = (b.opacite ?? 1) * fondus(b, t);
    if (enTransition(pr, i, t)) {
      const a = pr.clips[i - 1];
      const imgA = obtenir(a, tempsPrecedent(a, fps), 'precedent');
      const imgB = obtenir(b, tempsSource(b, t), 'principal');
      const k = clamp((t - b.debut) / b.transition.duree, 0, 1);
      const e = lisse(k);
      const alphaA = a.opacite ?? 1;
      const finA = finClip(a) - 1e-3;
      switch (b.transition.type) {
        case 'fondu':
          couche(a, imgA, alphaA, { tClip: finA });
          couche(b, imgB, alphaB * e);
          break;
        case 'noir':
          if (k < 0.5) couche(a, imgA, alphaA * (1 - lisse(k * 2)), { tClip: finA });
          else couche(b, imgB, alphaB * lisse(k * 2 - 1));
          break;
        case 'glisse':
          couche(a, imgA, alphaA, { dx: -e * W, tClip: finA });
          couche(b, imgB, alphaB, { dx: (1 - e) * W });
          break;
        case 'zoom':
          couche(a, imgA, alphaA * (1 - e), { zoom: 1 + 0.35 * e, tClip: finA });
          couche(b, imgB, alphaB * e, { zoom: 1.35 - 0.35 * e });
          break;
        default:
          couche(b, imgB, alphaB);
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
      cadres[c.id] = peindreMedia(ctx, img, c, W, H, { alpha: (c.opacite ?? 1) * fondus(c, t), zoom: facteurMouvement(c, t) });
    }
  }
  for (const piste of p.pistes) {
    if (piste.genre !== 'texte') continue;
    for (const c of piste.clips) if (actif(c, t)) cadres[c.id] = dessinerTexte(ctx, c, t, W, H);
  }
  ctx.restore();
  return cadres;
}

/** Nombre d'images à produire pour un projet, et l'instant de chacune. */
export const nombreImages = (duree, fps) => Math.max(1, Math.ceil(duree * fps - 1e-6));

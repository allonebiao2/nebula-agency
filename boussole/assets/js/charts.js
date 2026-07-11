// Boussole — graphes SVG maison (légers, offline, responsive) — style « verre lumineux ».
import { formatNombre } from './store.js';

// Palette lue depuis les variables CSS -> les graphes suivent le thème clair/sombre.
function cvar(name, fb) {
  try { const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim(); return v || fb; }
  catch { return fb; }
}
function palette() {
  return {
    pos: cvar('--c-pos', '#0f9d6e'),
    posSoft: cvar('--c-pos-soft', '#d8efe3'),
    neg: cvar('--c-neg', '#d42a50'),
    rev: cvar('--c-rev', '#e08a1e'),
    grid: cvar('--c-grid', '#e7e0d4'),
    text: cvar('--c-text', '#6b6156'),
    trend: cvar('--c-trend', '#0a6a49'),
    glow: cvar('--c-glow', '#f2a93c'),
  };
}

let _uid = 0;
const nextId = () => 'c' + (++_uid);

// Code couleur financier : vert si > 0, rouge si < 0, neutre (gris) si = 0.
const signCol = (v, COL) => (v < 0 ? COL.neg : (v > 0 ? COL.pos : COL.text));
// Dégradés verticaux qui BASCULENT au niveau du zéro (userSpaceOnUse, en coord. viewBox) :
//  sgL = trait plein vert au-dessus de la ligne des 0, rouge en dessous ;
//  sgA = aire qui s'estompe vers 0 pile au zéro (verte au-dessus, rouge en dessous).
// => une courbe de perte plonge visuellement sous le zéro et vire au rouge.
function signDefs(id, COL, zeroY, H) {
  const o = Math.max(0, Math.min(1, zeroY / H)).toFixed(4);
  return `<linearGradient id="sgL${id}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="${H}">
      <stop offset="0" stop-color="${COL.pos}"/><stop offset="${o}" stop-color="${COL.pos}"/>
      <stop offset="${o}" stop-color="${COL.neg}"/><stop offset="1" stop-color="${COL.neg}"/></linearGradient>
    <linearGradient id="sgA${id}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="${H}">
      <stop offset="0" stop-color="${COL.pos}" stop-opacity=".34"/><stop offset="${o}" stop-color="${COL.pos}" stop-opacity="0"/>
      <stop offset="${o}" stop-color="${COL.neg}" stop-opacity="0"/><stop offset="1" stop-color="${COL.neg}" stop-opacity=".30"/></linearGradient>`;
}

function glowDefs(id, COL) {
  return `<defs>
    <filter id="glow${id}" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <linearGradient id="barP${id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="${COL.pos}" stop-opacity="1"/><stop offset="1" stop-color="${COL.pos}" stop-opacity="0.28"/>
    </linearGradient>
    <linearGradient id="barN${id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="${COL.neg}" stop-opacity="0.95"/><stop offset="1" stop-color="${COL.neg}" stop-opacity="0.25"/>
    </linearGradient>
    <linearGradient id="area${id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="${COL.pos}" stop-opacity="0.42"/><stop offset="1" stop-color="${COL.pos}" stop-opacity="0"/>
    </linearGradient>
  </defs>`;
}

// Barres du bénéfice net mensuel — dégradé + sommet lumineux + tendance.
export function chartBeneficeMensuel(serie, opts = {}) {
  const COL = palette(), id = nextId();
  const showValues = opts.showValues !== false && serie.length <= 14;
  const W = 580, H = 260, padL = 16, padR = 16, padT = 26, padB = 34;
  const iw = W - padL - padR, ih = H - padT - padB;
  const n = serie.length || 1;
  const vals = serie.map((s) => s.benefice);
  const max = Math.max(1, ...vals.map((v) => Math.max(v, 0)));
  const min = Math.min(0, ...vals.map((v) => Math.min(v, 0)));
  const span = (max - min) || 1;
  const y = (v) => padT + ih * (1 - (v - min) / span);
  const zeroY = y(0), bw = iw / n, barW = Math.min(44, bw * 0.5);

  let bars = '', caps = '', labels = '', valueLabels = '', points = [];
  serie.forEach((s, i) => {
    const cx = padL + bw * i + bw / 2, v = s.benefice;
    const top = y(Math.max(v, 0)), bot = y(Math.min(v, 0));
    const h = Math.max(2, Math.abs(bot - top));
    const pos = v >= 0, active = s.unites > 0;
    const bx = (cx - barW / 2).toFixed(1), yRect = (pos ? top : zeroY).toFixed(1);
    if (!active) {
      bars += `<rect x="${bx}" y="${yRect}" width="${barW.toFixed(1)}" height="${h.toFixed(1)}" rx="6" fill="${COL.grid}" opacity="0.5"/>`;
    } else {
      bars += `<rect x="${bx}" y="${yRect}" width="${barW.toFixed(1)}" height="${h.toFixed(1)}" rx="6" fill="url(#${pos ? 'barP' : 'barN'}${id})"/>`;
      // sommet lumineux
      const capY = (pos ? top : bot - 3).toFixed(1);
      caps += `<rect x="${bx}" y="${capY}" width="${barW.toFixed(1)}" height="3" rx="1.5" fill="${pos ? COL.pos : COL.neg}" filter="url(#glow${id})"/>`;
      const ly = pos ? top - 8 : bot + 16;
      if (showValues) valueLabels += `<text x="${cx.toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="middle" font-size="11.5" font-family="ui-monospace,monospace" font-weight="700" fill="${pos ? COL.pos : COL.neg}">${formatNombre(v)}</text>`;
    }
    labels += `<text x="${cx.toFixed(1)}" y="${H - 12}" text-anchor="middle" font-size="12" fill="${COL.text}">${s.label}</text>`;
    points.push({ x: cx, y: y(v), active });
  });

  const act = points.filter((p) => p.active);
  let trend = '';
  if (act.length >= 2) {
    const d = act.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');
    trend = `<path d="${d}" fill="none" stroke="${COL.trend}" stroke-width="2" stroke-dasharray="1 6" stroke-linecap="round" opacity="0.5"/>`;
  }
  const zeroLine = `<line x1="${padL}" y1="${zeroY.toFixed(1)}" x2="${W - padR}" y2="${zeroY.toFixed(1)}" stroke="${COL.grid}" stroke-width="1"/>`;

  return `<svg viewBox="0 0 ${W} ${H}" class="chart-svg" role="img" aria-label="Bénéfice net par mois">
    ${glowDefs(id, COL)}${zeroLine}${bars}${trend}${caps}${valueLabels}${labels}
  </svg>`;
}

// Courbe d'évolution : revenu + bénéfice net, lignes lumineuses + aire.
export function chartEvolution(serie) {
  const COL = palette(), id = nextId();
  const W = 580, H = 250, padL = 14, padR = 52, padT = 30, padB = 32;
  const iw = W - padL - padR, ih = H - padT - padB;
  const n = Math.max(1, serie.length);
  const revs = serie.map((s) => s.revenu), bens = serie.map((s) => s.benefice);
  const max = Math.max(1, ...revs, ...bens), min = Math.min(0, ...bens), span = (max - min) || 1;
  const x = (i) => padL + (n === 1 ? iw / 2 : iw * (i / (n - 1)));
  const y = (v) => padT + ih * (1 - (v - min) / span);
  const zeroY = y(0);
  const line = (vals) => vals.map((v, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ');
  const benPath = line(bens);
  const area = `${benPath} L${x(n - 1).toFixed(1)},${zeroY.toFixed(1)} L${x(0).toFixed(1)},${zeroY.toFixed(1)} Z`;
  const dots = (vals, col, signed) => vals.map((v, i) => serie[i].unites > 0
    ? `<circle cx="${x(i).toFixed(1)}" cy="${y(v).toFixed(1)}" r="3.4" fill="${signed ? signCol(v, COL) : col}" filter="url(#glow${id})"/><circle cx="${x(i).toFixed(1)}" cy="${y(v).toFixed(1)}" r="1.6" fill="#fff"/>` : '').join('');
  const labels = serie.map((s, i) => `<text x="${x(i).toFixed(1)}" y="${H - 10}" text-anchor="middle" font-size="12" fill="${COL.text}">${s.label}</text>`).join('');
  const last = n - 1;
  const endLbl = (v, col, dy) => `<text x="${(x(last) + 6).toFixed(1)}" y="${(y(v) + dy).toFixed(1)}" font-size="11" font-family="ui-monospace,monospace" font-weight="700" fill="${col}">${formatNombre(v)}</text>`;
  const legend = `<g font-size="11.5" font-weight="600">
    <circle cx="${padL + 4}" cy="14" r="4" fill="${COL.rev}"/><text x="${padL + 13}" y="17.5" fill="${COL.text}">Revenu</text>
    <circle cx="${padL + 84}" cy="14" r="4" fill="${COL.pos}"/><text x="${padL + 93}" y="17.5" fill="${COL.text}">Bénéfice</text></g>`;

  return `<svg viewBox="0 0 ${W} ${H}" class="chart-svg" role="img" aria-label="Évolution du revenu et du bénéfice">
    ${glowDefs(id, COL)}${signDefs(id, COL, zeroY, H)}
    <line x1="${padL}" y1="${zeroY.toFixed(1)}" x2="${W - padR}" y2="${zeroY.toFixed(1)}" stroke="${COL.grid}" stroke-width="1"/>
    <path d="${area}" fill="url(#sgA${id})"/>
    <path d="${line(revs)}" fill="none" stroke="${COL.rev}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow${id})"/>
    <path d="${benPath}" fill="none" stroke="url(#sgL${id})" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow${id})"/>
    ${dots(revs, COL.rev)}${dots(bens, COL.pos, true)}
    ${endLbl(revs[last], COL.rev, -6)}${endLbl(bens[last], signCol(bens[last], COL), 12)}
    ${labels}${legend}
  </svg>`;
}

// Mini courbe lumineuse (carte héros de l'Accueil).
export function miniSpark(serie, opts = {}) {
  const COL = palette(), id = nextId();
  const W = opts.w || 260, H = opts.h || 70, p = 6;
  const vals = serie.map((s) => s.benefice);
  const max = Math.max(1, ...vals), min = Math.min(0, ...vals), span = (max - min) || 1;
  const x = (i) => p + (W - 2 * p) * (i / Math.max(1, vals.length - 1));
  const y = (v) => p + (H - 2 * p) * (1 - (v - min) / span);
  const d = vals.map((v, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ');
  const area = `${d} L${x(vals.length - 1).toFixed(1)},${H} L${x(0).toFixed(1)},${H} Z`;
  const lastX = x(vals.length - 1).toFixed(1), lastY = y(vals[vals.length - 1]).toFixed(1);
  return `<svg viewBox="0 0 ${W} ${H}" class="chart-svg" preserveAspectRatio="none" aria-hidden="true">
    ${glowDefs(id, COL)}
    <path d="${area}" fill="url(#area${id})"/>
    <path d="${d}" fill="none" stroke="${COL.rev}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow${id})"/>
    <circle cx="${lastX}" cy="${lastY}" r="3.6" fill="${COL.rev}" filter="url(#glow${id})"/><circle cx="${lastX}" cy="${lastY}" r="1.7" fill="#fff"/>
  </svg>`;
}

// Anneau de progression lumineux (donut) — pct 0..100.
export function progressRing(pct, opts = {}) {
  const COL = palette(), id = nextId();
  const size = opts.size || 92, sw = opts.stroke || 9, r = (size - sw) / 2, c = 2 * Math.PI * r;
  const col = opts.color || COL.rev;
  const off = c * (1 - Math.max(0, Math.min(100, pct)) / 100);
  const cx = size / 2;
  return `<svg viewBox="0 0 ${size} ${size}" class="ring" aria-hidden="true">
    <defs><filter id="rg${id}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
    <circle cx="${cx}" cy="${cx}" r="${r}" fill="none" style="stroke:var(--line)" stroke-width="${sw}"/>
    <circle class="ring__fill" cx="${cx}" cy="${cx}" r="${r}" fill="none" stroke-width="${sw}" stroke-linecap="round"
      stroke-dasharray="${c.toFixed(1)}" transform="rotate(-90 ${cx} ${cx})" filter="url(#rg${id})"
      style="stroke:${col}; --c:${c.toFixed(1)}; --o:${off.toFixed(1)}; stroke-dashoffset:var(--o)"/>
  </svg>`;
}

// ===== GRAND GRAPHE HÉROS — Chiffre d'affaires (aire ambre) + Bénéfice (ligne émeraude) =====
export function chartHero(D) {
  const COL = palette(), id = nextId();
  const src0 = D.buckets.filter((b) => !b.future);
  const src = src0.length ? src0 : D.buckets.slice(0, 1);
  const W = 620, H = 236, padL = 12, padR = 56, padT = 30, padB = 30;
  const iw = W - padL - padR, ih = H - padT - padB;
  const n = Math.max(1, src.length);
  const revs = src.map((s) => s.revenu), bens = src.map((s) => s.benefice);
  const max = Math.max(1, ...revs, ...bens), min = Math.min(0, ...bens), span = (max - min) || 1;
  const x = (i) => padL + (n === 1 ? iw / 2 : iw * (i / (n - 1)));
  const y = (v) => padT + ih * (1 - (v - min) / span);
  const zeroY = y(0);
  const path = (vals) => vals.map((v, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ');
  const revPath = path(revs), benPath = path(bens);
  const revArea = `${revPath} L${x(n - 1).toFixed(1)},${zeroY.toFixed(1)} L${x(0).toFixed(1)},${zeroY.toFixed(1)} Z`;
  const grid = [0.5, 1].map((f) => { const yy = padT + ih * (1 - f); return `<line x1="${padL}" y1="${yy.toFixed(1)}" x2="${W - padR}" y2="${yy.toFixed(1)}" stroke="${COL.grid}" stroke-width="1" opacity=".55"/>`; }).join('');
  const labels = src.map((s, i) => s.label ? `<text x="${x(i).toFixed(1)}" y="${H - 9}" text-anchor="middle" font-size="11" fill="${COL.text}">${s.label}</text>` : '').join('');
  const dot = (vals, col) => { const i = n - 1; return `<circle cx="${x(i).toFixed(1)}" cy="${y(vals[i]).toFixed(1)}" r="4" fill="${col}" filter="url(#glow${id})"/><circle cx="${x(i).toFixed(1)}" cy="${y(vals[i]).toFixed(1)}" r="1.8" fill="#fff"/>`; };
  const endLbl = (v, col, dy) => `<text x="${(x(n - 1) + 8).toFixed(1)}" y="${(y(v) + dy).toFixed(1)}" font-size="10.5" font-family="ui-monospace,monospace" font-weight="700" fill="${col}">${formatNombre(v)}</text>`;
  return `<svg viewBox="0 0 ${W} ${H}" class="chart-svg" role="img" aria-label="Évolution du chiffre d'affaires et du bénéfice">
    <defs>
      <filter id="glow${id}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      <linearGradient id="heroA${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${COL.rev}" stop-opacity="0.42"/><stop offset="1" stop-color="${COL.rev}" stop-opacity="0"/></linearGradient>
      ${signDefs(id, COL, zeroY, H)}
    </defs>
    ${grid}
    <line x1="${padL}" y1="${zeroY.toFixed(1)}" x2="${W - padR}" y2="${zeroY.toFixed(1)}" stroke="${COL.grid}" stroke-width="1"/>
    <path d="${revArea}" fill="url(#heroA${id})"/>
    <path d="${revPath}" fill="none" stroke="${COL.rev}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow${id})"/>
    <path d="${benPath}" fill="none" stroke="url(#sgL${id})" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow${id})"/>
    ${dot(revs, COL.rev)}${dot(bens, signCol(bens[n - 1], COL))}
    ${endLbl(revs[n - 1], COL.rev, -6)}${endLbl(bens[n - 1], signCol(bens[n - 1], COL), 12)}
    ${labels}
  </svg>`;
}

// ===== DONUT lumineux multi-segments (répartition). segments = [{value, color}]. Centre géré en HTML. =====
export function chartDonut(segments, opts = {}) {
  const id = nextId();
  const size = opts.size || 168, sw = opts.stroke || 20, r = (size - sw) / 2, c = 2 * Math.PI * r, cx = size / 2;
  const total = segments.reduce((s, x) => s + Math.max(0, x.value), 0);
  let acc = 0, arcs = '';
  if (total <= 0) {
    arcs = `<circle cx="${cx}" cy="${cx}" r="${r}" fill="none" style="stroke:var(--line)" stroke-width="${sw}"/>`;
  } else {
    segments.forEach((seg) => {
      const val = Math.max(0, seg.value); if (val <= 0) return;
      const len = c * (val / total), rot = -90 + (acc / total) * 360;
      arcs += `<circle cx="${cx}" cy="${cx}" r="${r}" fill="none" style="stroke:${seg.color}" stroke-width="${sw}"
        stroke-dasharray="${len.toFixed(2)} ${(c - len).toFixed(2)}" transform="rotate(${rot.toFixed(2)} ${cx} ${cx})" stroke-linecap="butt" filter="url(#dg${id})"/>`;
      acc += val;
    });
  }
  return `<svg viewBox="0 0 ${size} ${size}" class="donut__svg" aria-hidden="true">
    <defs><filter id="dg${id}" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
    <circle cx="${cx}" cy="${cx}" r="${r}" fill="none" style="stroke:var(--line-soft)" stroke-width="${sw}"/>
    ${arcs}
  </svg>`;
}

// ===== Mini-courbe (sparkline) à partir de valeurs brutes. =====
export function sparklineRaw(values, opts = {}) {
  const COL = palette(), id = nextId();
  const W = opts.w || 130, H = opts.h || 34, p = 3, col = opts.color || COL.rev;
  const vals = (values && values.length) ? values : [0, 0];
  const max = Math.max(1, ...vals), min = Math.min(0, ...vals), span = (max - min) || 1;
  const x = (i) => p + (W - 2 * p) * (i / Math.max(1, vals.length - 1));
  const y = (v) => p + (H - 2 * p) * (1 - (v - min) / span);
  const zeroY = y(0);
  const d = vals.map((v, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ');
  const area = `${d} L${x(vals.length - 1).toFixed(1)},${H} L${x(0).toFixed(1)},${H} Z`;
  // sign=true : trait/aire suivent le code couleur financier (vert au-dessus du 0, rouge en dessous).
  const defs = opts.sign
    ? signDefs(id, COL, zeroY, H)
    : `<linearGradient id="sp${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${col}" stop-opacity=".26"/><stop offset="1" stop-color="${col}" stop-opacity="0"/></linearGradient>`;
  const fill = opts.sign ? `url(#sgA${id})` : `url(#sp${id})`;
  const stroke = opts.sign ? `url(#sgL${id})` : col;
  return `<svg viewBox="0 0 ${W} ${H}" class="chart-svg spark" preserveAspectRatio="none" aria-hidden="true">
    <defs>${defs}</defs>
    <path d="${area}" fill="${fill}"/>
    <path d="${d}" fill="none" stroke="${stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
}

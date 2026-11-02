// LA BOBINE · les LUT 3D au format .cube (le format d'échange des étalonneurs : Resolve, Premiere, LUTs achetées).
// Une LUT est un cube de couleurs : on y entre avec (r, g, b), on en sort avec la couleur étalonnée.
// Appliquée par WebGL (une passe, interpolation trilinéaire) ; sans WebGL, le même calcul sur le processeur.

const pretes = new Map();
const enCours = new Map();

/** Lit un fichier .cube. Rend { taille, donnees: Float32Array(taille³ × 3), titre } (r varie le plus vite). */
export function lireCube(texte) {
  let taille = 0;
  let min = [0, 0, 0];
  let max = [1, 1, 1];
  let titre = '';
  const valeurs = [];
  for (const brute of String(texte).split(/\r?\n/)) {
    const l = brute.trim();
    if (!l || l.startsWith('#')) continue;
    const m = l.split(/\s+/);
    const mot = m[0].toUpperCase();
    if (mot === 'TITLE') titre = l.slice(5).trim().replace(/^"|"$/g, '');
    else if (mot === 'LUT_3D_SIZE') taille = parseInt(m[1], 10);
    else if (mot === 'LUT_1D_SIZE') throw new Error('Cette LUT est une LUT 1D : LA BOBINE lit les LUT 3D.');
    else if (mot === 'DOMAIN_MIN') min = m.slice(1, 4).map(Number);
    else if (mot === 'DOMAIN_MAX') max = m.slice(1, 4).map(Number);
    else if (/^[-+.\d]/.test(m[0]) && m.length >= 3) valeurs.push(+m[0], +m[1], +m[2]);
  }
  if (!(taille >= 2 && taille <= 128)) throw new Error('Ce fichier .cube ne dit pas sa taille (LUT_3D_SIZE).');
  if (valeurs.length !== taille ** 3 * 3) throw new Error(`Ce fichier .cube est incomplet : ${valeurs.length / 3} couleurs au lieu de ${taille ** 3}.`);
  const donnees = new Float32Array(valeurs.length);
  for (let i = 0; i < valeurs.length; i += 1) {
    const c = i % 3;
    donnees[i] = Math.min(1, Math.max(0, (valeurs[i] - min[c]) / ((max[c] - min[c]) || 1)));
  }
  return { taille, donnees, titre };
}

export const lutPrete = (id) => (id ? pretes.get(id) || null : null);

/** Prépare la LUT d'un média (une fois). */
export function chargerLut(media) {
  if (!media) return Promise.resolve(null);
  if (pretes.has(media.id)) return Promise.resolve(pretes.get(media.id));
  if (!enCours.has(media.id)) {
    enCours.set(media.id, media.fichier.text().then((t) => { const l = lireCube(t); l.id = media.id; pretes.set(media.id, l); return l; })
      .finally(() => enCours.delete(media.id)));
  }
  return enCours.get(media.id);
}

/** Le même calcul que le nuanceur, sur le processeur. px : RGBA (modifié sur place). */
export function appliquerLutPixels(px, lut, intensite = 1) {
  const n = lut.taille;
  const d = lut.donnees;
  const s = n - 1;
  const k = Math.min(1, Math.max(0, intensite));
  const lire = (r, g, b, c) => d[((b * n + g) * n + r) * 3 + c];
  for (let i = 0; i < px.length; i += 4) {
    const fr = (px[i] / 255) * s; const fg = (px[i + 1] / 255) * s; const fb = (px[i + 2] / 255) * s;
    const r0 = Math.floor(fr); const g0 = Math.floor(fg); const b0 = Math.floor(fb);
    const r1 = Math.min(s, r0 + 1); const g1 = Math.min(s, g0 + 1); const b1 = Math.min(s, b0 + 1);
    const dr = fr - r0; const dg = fg - g0; const db = fb - b0;
    for (let c = 0; c < 3; c += 1) {
      const c00 = lire(r0, g0, b0, c) * (1 - dr) + lire(r1, g0, b0, c) * dr;
      const c10 = lire(r0, g1, b0, c) * (1 - dr) + lire(r1, g1, b0, c) * dr;
      const c01 = lire(r0, g0, b1, c) * (1 - dr) + lire(r1, g0, b1, c) * dr;
      const c11 = lire(r0, g1, b1, c) * (1 - dr) + lire(r1, g1, b1, c) * dr;
      const v = (c00 * (1 - dg) + c10 * dg) * (1 - db) + (c01 * (1 - dg) + c11 * dg) * db;
      px[i + c] = Math.round(px[i + c] * (1 - k) + v * 255 * k);
    }
  }
}

// ---------- WebGL ----------
let gl = null;
let glEchec = false;
let prog = null;
let texImage = null;
let texLut = null;
let lutChargee = null;

const VS = 'attribute vec2 p;varying vec2 uv;void main(){uv=vec2(p.x*.5+.5,.5-p.y*.5);gl_Position=vec4(p,0.,1.);}';
const FS = 'precision highp float;varying vec2 uv;uniform sampler2D img;uniform sampler2D lut;uniform float n;uniform float k;'
  + 'vec3 tranche(float b,vec2 rg){float x=(b*n+rg.x*(n-1.)+.5)/(n*n);float y=(rg.y*(n-1.)+.5)/n;return texture2D(lut,vec2(x,y)).rgb;}'
  + 'void main(){vec4 c=texture2D(img,uv);float b=c.b*(n-1.);float b0=floor(b);float b1=min(b0+1.,n-1.);'
  + 'vec3 v=mix(tranche(b0,c.rg),tranche(b1,c.rg),b-b0);gl_FragColor=vec4(mix(c.rgb,v,k),c.a);}';

function preparerGL() {
  if (gl || glEchec) return gl;
  try {
    const cv = typeof OffscreenCanvas !== 'undefined' ? new OffscreenCanvas(2, 2) : document.createElement('canvas');
    const g = cv.getContext('webgl', { premultipliedAlpha: false, preserveDrawingBuffer: true, antialias: false });
    if (!g) throw new Error('pas de WebGL');
    const sh = (type, src) => {
      const s = g.createShader(type);
      g.shaderSource(s, src);
      g.compileShader(s);
      if (!g.getShaderParameter(s, g.COMPILE_STATUS)) throw new Error(g.getShaderInfoLog(s));
      return s;
    };
    prog = g.createProgram();
    g.attachShader(prog, sh(g.VERTEX_SHADER, VS));
    g.attachShader(prog, sh(g.FRAGMENT_SHADER, FS));
    g.linkProgram(prog);
    if (!g.getProgramParameter(prog, g.LINK_STATUS)) throw new Error(g.getProgramInfoLog(prog));
    g.useProgram(prog);
    const tampon = g.createBuffer();
    g.bindBuffer(g.ARRAY_BUFFER, tampon);
    g.bufferData(g.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), g.STATIC_DRAW);
    const loc = g.getAttribLocation(prog, 'p');
    g.enableVertexAttribArray(loc);
    g.vertexAttribPointer(loc, 2, g.FLOAT, false, 0, 0);
    const tex = (unite) => {
      const t = g.createTexture();
      g.activeTexture(g.TEXTURE0 + unite);
      g.bindTexture(g.TEXTURE_2D, t);
      g.texParameteri(g.TEXTURE_2D, g.TEXTURE_WRAP_S, g.CLAMP_TO_EDGE);
      g.texParameteri(g.TEXTURE_2D, g.TEXTURE_WRAP_T, g.CLAMP_TO_EDGE);
      g.texParameteri(g.TEXTURE_2D, g.TEXTURE_MIN_FILTER, g.LINEAR);
      g.texParameteri(g.TEXTURE_2D, g.TEXTURE_MAG_FILTER, g.LINEAR);
      return t;
    };
    texImage = tex(0);
    texLut = tex(1);
    g.uniform1i(g.getUniformLocation(prog, 'img'), 0);
    g.uniform1i(g.getUniformLocation(prog, 'lut'), 1);
    g.pixelStorei(g.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
    gl = g;
  } catch {
    glEchec = true;
    gl = null;
  }
  return gl;
}

/** Applique la LUT au contenu d'une toile 2D (modifiée sur place). */
export function appliquerLut(toile, lut, intensite = 1) {
  const l = toile.width;
  const h = toile.height;
  let g = preparerGL();
  // une LUT de 65 fait un atlas de 4 225 pixels de large : trop pour certains téléphones
  if (g && lut.taille * lut.taille > g.getParameter(g.MAX_TEXTURE_SIZE)) g = null;
  const o = toile.getContext('2d', { willReadFrequently: true });
  if (!g) {
    const d = o.getImageData(0, 0, l, h);
    appliquerLutPixels(d.data, lut, intensite);
    o.putImageData(d, 0, 0);
    return;
  }
  const cv = g.canvas;
  if (cv.width !== l) cv.width = l;
  if (cv.height !== h) cv.height = h;
  g.viewport(0, 0, l, h);
  if (lutChargee !== lut) {
    const n = lut.taille;
    const octets = new Uint8Array(n * n * n * 4);
    // atlas : les n tranches de bleu côte à côte, r en x, g en y
    for (let b = 0; b < n; b += 1) {
      for (let gg = 0; gg < n; gg += 1) {
        for (let r = 0; r < n; r += 1) {
          const src = ((b * n + gg) * n + r) * 3;
          const dst = (gg * n * n + b * n + r) * 4;
          octets[dst] = Math.round(lut.donnees[src] * 255);
          octets[dst + 1] = Math.round(lut.donnees[src + 1] * 255);
          octets[dst + 2] = Math.round(lut.donnees[src + 2] * 255);
          octets[dst + 3] = 255;
        }
      }
    }
    g.activeTexture(g.TEXTURE1);
    g.bindTexture(g.TEXTURE_2D, texLut);
    g.texImage2D(g.TEXTURE_2D, 0, g.RGBA, n * n, n, 0, g.RGBA, g.UNSIGNED_BYTE, octets);
    lutChargee = lut;
  }
  g.activeTexture(g.TEXTURE0);
  g.bindTexture(g.TEXTURE_2D, texImage);
  g.texImage2D(g.TEXTURE_2D, 0, g.RGBA, g.RGBA, g.UNSIGNED_BYTE, toile);
  g.uniform1f(g.getUniformLocation(prog, 'n'), lut.taille);
  g.uniform1f(g.getUniformLocation(prog, 'k'), Math.min(1, Math.max(0, intensite)));
  g.drawArrays(g.TRIANGLE_STRIP, 0, 4);
  o.save();
  o.globalCompositeOperation = 'copy';
  o.globalAlpha = 1;
  o.drawImage(cv, 0, 0);
  o.restore();
}

export const lutParWebGL = () => !!preparerGL();

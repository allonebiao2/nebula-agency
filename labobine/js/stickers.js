// LA BOBINE · les stickers, dessinés ici en vectoriel (aucune image téléchargée) : ils restent nets en 4K.
// Pensés pour qui vend : montrer un produit (flèche, cercle tracé à la main), annoncer (PROMO, NOUVEAU, le prix),
// situer (l'épingle), réagir (cœur, étoile, feu, émoji).
// Chaque forme se dessine dans une boîte de 100 × 100 centrée sur l'origine.

const P = (d) => (typeof Path2D !== 'undefined' ? new Path2D(d) : null);
const cache = new Map();
const chemin = (d) => { if (!cache.has(d)) cache.set(d, P(d)); return cache.get(d); };

function trait(o, d, couleur, largeur, contour) {
  const p = chemin(d);
  o.lineCap = 'round';
  o.lineJoin = 'round';
  if (contour) { o.strokeStyle = contour; o.lineWidth = largeur + 7; o.stroke(p); }
  o.strokeStyle = couleur;
  o.lineWidth = largeur;
  o.stroke(p);
}
function plein(o, d, couleur, contour, largeur = 5) {
  const p = chemin(d);
  o.lineJoin = 'round';
  if (contour) { o.strokeStyle = contour; o.lineWidth = largeur; o.stroke(p); }
  o.fillStyle = couleur;
  o.fill(p);
}
/** Un texte qui tient dans la largeur donnée, centré en (x, y). */
function texteAjuste(o, texte, x, y, largeur, corps, police, couleur) {
  const t = String(texte || '').trim();
  if (!t) return;
  let c = corps;
  o.font = `${police.poids} ${c}px "${police.nom}", "Arial Black", sans-serif`;
  const l = o.measureText(t).width;
  if (l > largeur) { c = Math.max(6, (c * largeur) / l); o.font = `${police.poids} ${c}px "${police.nom}", "Arial Black", sans-serif`; }
  o.textAlign = 'center';
  o.textBaseline = 'middle';
  o.fillStyle = couleur;
  o.fillText(t, x, y + c * 0.04);
}
const AFFICHE = { nom: 'Anton', poids: 400 };
const GROTESQUE = { nom: 'Bricolage Grotesque', poids: 800 };

function etoile(branches, rExt, rInt, rot = -Math.PI / 2) {
  let d = '';
  for (let i = 0; i < branches * 2; i += 1) {
    const r = i % 2 ? rInt : rExt;
    const a = rot + (i * Math.PI) / branches;
    d += `${i ? 'L' : 'M'}${(Math.cos(a) * r).toFixed(2)} ${(Math.sin(a) * r).toFixed(2)}`;
  }
  return `${d}Z`;
}
function festons(n, r, creux) {
  let d = '';
  for (let i = 0; i <= n * 4; i += 1) {
    const a = (i / (n * 4)) * Math.PI * 2;
    const rr = r - creux * (0.5 - 0.5 * Math.cos(a * n));
    d += `${i ? 'L' : 'M'}${(Math.cos(a) * rr).toFixed(2)} ${(Math.sin(a) * rr).toFixed(2)}`;
  }
  return `${d}Z`;
}
const D_ETOILE = etoile(5, 48, 20);
const D_ECLAT = etoile(14, 50, 39);
const D_FESTONS = festons(18, 48, 4);

export const STICKERS = {
  fleche: {
    nom: 'Flèche', couleur: '#ffd23f', couleur2: '#14110e',
    dessiner(o, c) {
      trait(o, 'M-40 8 C-18 3 8 -1 34 -4', c.couleur, 9, c.couleur2);
      trait(o, 'M17 -21 L36 -4 L19 14', c.couleur, 9, c.couleur2);
      trait(o, 'M-40 8 C-18 3 8 -1 34 -4', c.couleur, 9);
    },
  },
  courbe: {
    nom: 'Flèche courbe', couleur: '#ffffff', couleur2: '#14110e',
    dessiner(o, c) {
      trait(o, 'M-38 30 C-34 -10 2 -30 32 -14', c.couleur, 8, c.couleur2);
      trait(o, 'M15 -27 L33 -13 L20 4', c.couleur, 8, c.couleur2);
      trait(o, 'M-38 30 C-34 -10 2 -30 32 -14', c.couleur, 8);
    },
  },
  cercle: {
    nom: 'Entourer', couleur: '#ff5a4e', couleur2: '#14110e', boite: [100, 76],
    dessiner(o, c) { trait(o, 'M42 -6 C42 -28 12 -38 -12 -34 C-38 -30 -48 -10 -44 8 C-40 28 -12 36 14 32 C36 28 47 12 43 -10 C40 -22 30 -30 16 -34', c.couleur, 6); },
  },
  souligne: {
    nom: 'Souligner', couleur: '#ffd23f', couleur2: '#14110e', boite: [100, 34],
    dessiner(o, c) { trait(o, 'M-46 2 C-20 -6 12 -2 46 -10 M-34 12 C-8 6 16 8 38 4', c.couleur, 7); },
  },
  etoile: { nom: 'Étoile', couleur: '#ffd23f', couleur2: '#14110e', dessiner(o, c) { plein(o, D_ETOILE, c.couleur, c.couleur2, 6); } },
  coeur: {
    nom: 'Cœur', couleur: '#ff5a4e', couleur2: '#ffffff',
    dessiner(o, c) { plein(o, 'M0 36 C-12 26 -48 6 -44 -18 C-40 -40 -10 -42 0 -20 C10 -42 40 -40 44 -18 C48 6 12 26 0 36 Z', c.couleur, c.couleur2, 5); },
  },
  eclair: {
    nom: 'Éclair', couleur: '#ffd23f', couleur2: '#14110e',
    dessiner(o, c) { plein(o, 'M10 -48 L-26 6 L-3 6 L-13 48 L27 -10 L3 -10 L15 -48 Z', c.couleur, c.couleur2, 6); },
  },
  etincelle: {
    nom: 'Étincelle', couleur: '#ffffff', couleur2: '#ffd23f',
    dessiner(o, c) {
      plein(o, 'M-6 -46 C-3 -14 4 -8 34 -4 C4 0 -3 6 -6 38 C-9 6 -16 0 -46 -4 C-16 -8 -9 -14 -6 -46 Z', c.couleur);
      plein(o, 'M30 14 C31 24 34 27 44 28 C34 29 31 32 30 42 C29 32 26 29 16 28 C26 27 29 24 30 14 Z', c.couleur2);
    },
  },
  feu: {
    nom: 'Feu', couleur: '#ff8a1e', couleur2: '#ffd23f',
    dessiner(o, c) {
      plein(o, 'M0 46 C-24 46 -36 30 -34 12 C-32 -6 -18 -14 -16 -32 C-6 -24 -2 -16 0 -8 C4 -24 14 -36 10 -48 C30 -34 38 -12 34 10 C31 32 18 46 0 46 Z', c.couleur);
      plein(o, 'M0 46 C-12 46 -18 36 -16 26 C-14 16 -6 12 -4 2 C2 8 4 14 4 18 C8 12 12 8 12 2 C20 12 20 26 16 34 C12 42 6 46 0 46 Z', c.couleur2);
    },
  },
  coche: {
    nom: 'Validé', couleur: '#4fc58a', couleur2: '#ffffff',
    dessiner(o, c) { plein(o, 'M0 -46 A46 46 0 1 1 0 46 A46 46 0 1 1 0 -46 Z', c.couleur); trait(o, 'M-22 2 L-6 18 L24 -16', c.couleur2, 10); },
  },
  epingle: {
    nom: 'Lieu', couleur: '#ff5a4e', couleur2: '#ffffff',
    dessiner(o, c) {
      plein(o, 'M0 48 C-6 32 -32 10 -32 -14 C-32 -33 -18 -47 0 -47 C18 -47 32 -33 32 -14 C32 10 6 32 0 48 Z', c.couleur);
      plein(o, 'M0 -26 A12 12 0 1 1 0 -2 A12 12 0 1 1 0 -26 Z', c.couleur2);
    },
  },
  bulle: {
    nom: 'Bulle', couleur: '#ffffff', couleur2: '#14110e', texte: 'Waouh !', boite: [100, 84],
    dessiner(o, c) {
      plein(o, 'M-30 -38 L30 -38 Q48 -38 48 -20 L48 4 Q48 22 30 22 L-6 22 L-26 40 L-22 22 L-30 22 Q-48 22 -48 4 L-48 -20 Q-48 -38 -30 -38 Z', c.couleur, c.couleur2, 4);
      texteAjuste(o, c.texte, 0, -8, 84, 26, GROTESQUE, c.couleur2);
    },
  },
  promo: {
    nom: 'Promo', couleur: '#ff5a4e', couleur2: '#ffffff', texte: 'PROMO',
    dessiner(o, c) { plein(o, D_ECLAT, c.couleur); texteAjuste(o, c.texte, 0, 0, 66, 30, AFFICHE, c.couleur2); },
  },
  nouveau: {
    nom: 'Nouveau', couleur: '#ffd23f', couleur2: '#14110e', texte: 'NOUVEAU',
    dessiner(o, c) {
      plein(o, D_FESTONS, c.couleur);
      o.strokeStyle = c.couleur2; o.lineWidth = 2.5; o.beginPath(); o.arc(0, 0, 36, 0, Math.PI * 2); o.stroke();
      texteAjuste(o, c.texte, 0, 0, 62, 22, AFFICHE, c.couleur2);
    },
  },
  prix: {
    nom: 'Prix', couleur: '#ffd23f', couleur2: '#14110e', texte: '5 000 F', boite: [100, 52],
    dessiner(o, c) {
      plein(o, 'M-44 -22 Q-48 -22 -48 -18 L-48 18 Q-48 22 -44 22 L24 22 L46 0 L24 -22 Z', c.couleur, c.couleur2, 4);
      o.save(); o.globalCompositeOperation = 'destination-out'; o.beginPath(); o.arc(29, 0, 4.5, 0, Math.PI * 2); o.fill(); o.restore();
      texteAjuste(o, c.texte, -10, 0, 62, 28, AFFICHE, c.couleur2);
    },
  },
  ruban: {
    nom: 'Bandeau', couleur: '#14110e', couleur2: '#ffd23f', texte: 'LIVRAISON OFFERTE', boite: [100, 34],
    dessiner(o, c) {
      plein(o, 'M-50 -10 L-38 -10 L-38 14 L-50 14 L-44 2 Z M50 -10 L38 -10 L38 14 L50 14 L44 2 Z', c.couleur2);
      plein(o, 'M-42 -15 L42 -15 L42 9 L-42 9 Z', c.couleur);
      texteAjuste(o, c.texte, 0, -3, 78, 16, AFFICHE, c.couleur2);
    },
  },
  emoji: {
    nom: 'Émoji', couleur: '#ffffff', couleur2: '#14110e', texte: '🔥',
    dessiner(o, c) {
      o.font = '78px "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif';
      o.textAlign = 'center';
      o.textBaseline = 'middle';
      o.fillStyle = '#000';
      o.fillText([...String(c.texte || '🔥')].slice(0, 3).join(''), 0, 4);
    },
  },
};

export const AVEC_TEXTE = new Set(Object.entries(STICKERS).filter(([, s]) => s.texte !== undefined).map(([k]) => k));
export const boiteDe = (forme) => (STICKERS[forme] && STICKERS[forme].boite) || [100, 100];

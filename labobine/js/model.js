// LA BOBINE · le modèle d'un projet : pistes, clips, et les opérations de montage.
// Aucune dépendance au DOM : ce fichier se teste tel quel dans Node.

export const FORMATS = {
  '9:16': { w: 1080, h: 1920, nom: 'Vertical', pour: 'TikTok, Reels, Shorts' },
  '16:9': { w: 1920, h: 1080, nom: 'Paysage', pour: 'YouTube, télévision' },
  '1:1': { w: 1080, h: 1080, nom: 'Carré', pour: 'Publication' },
  '4:5': { w: 1080, h: 1350, nom: 'Portrait', pour: 'Fil Instagram, Facebook' },
};

export const POLICES = [
  { nom: 'Bricolage Grotesque', titre: 'Grotesque', poids: 700 },
  { nom: 'Anton', titre: 'Affiche', poids: 400 },
  { nom: 'Playfair Display', titre: 'Élégant', poids: 700 },
  { nom: 'Caveat', titre: 'Manuscrit', poids: 700 },
  { nom: 'Instrument Sans', titre: 'Sobre', poids: 600 },
];

export const TRANSITIONS = [
  ['aucune', 'Aucune'], ['fondu', 'Fondu enchaîné'], ['noir', 'Passage au noir'],
  ['glisse', 'Glissement'], ['glisse-haut', 'Glissement vers le haut'], ['zoom', 'Zoom'], ['balayage', 'Balayage'],
  ['rideau', 'Rideau'], ['iris', 'Iris'], ['flash', 'Flash blanc'], ['tourbillon', 'Tourbillon'],
];
export const ANIMS_TEXTE = [
  ['aucune', 'Aucune'], ['fondu', 'Fondu'], ['monte', 'Montée'], ['pop', 'Rebond'], ['machine', 'Machine à écrire'],
];
export const MOUVEMENTS = [['aucun', 'Aucun'], ['avant', 'Zoom avant lent'], ['arriere', 'Zoom arrière lent']];

export const VITESSE_MIN = 0.25, VITESSE_MAX = 4, DUREE_MIN = 0.1, DUREE_PHOTO = 3, DUREE_TEXTE = 3;

/** Les clips qui ne viennent pas d'un fichier : ils ont une durée propre au lieu d'une entrée et d'une sortie. */
export const SANS_MEDIA = new Set(['texte', 'effet', 'sticker']);
export const aDureePropre = (c) => SANS_MEDIA.has(c.genre);

export const uid = (p = 'c') => p + Math.random().toString(36).slice(2, 9) + Date.now().toString(36).slice(-4);
export const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const copie = (o) => JSON.parse(JSON.stringify(o));

export function nouveauProjet(format = '9:16', nom = 'Sans titre') {
  const f = FORMATS[format] || FORMATS['9:16'];
  const maintenant = Date.now();
  return {
    id: uid('p'), nom, format, w: f.w, h: f.h, fps: 30,
    fond: { type: 'couleur', couleur: '#000000' },
    pistes: [{ id: 'principale', genre: 'principale', clips: [] }],
    medias: [], marqueurs: [], volumeCible: '-14', creeLe: maintenant, modifieLe: maintenant, version: 1,
  };
}

export function changerFormat(p, format) {
  const f = FORMATS[format];
  if (!f) return;
  p.format = format; p.w = f.w; p.h = f.h;
}

// ---------- durées ----------
export const dureeClip = (c) => (SANS_MEDIA.has(c.genre) ? c.duree : (c.sortie - c.entree) / (c.vitesse || 1));
export const finClip = (c) => c.debut + dureeClip(c);
export const tempsSource = (c, t) => c.entree + (t - c.debut) * (c.vitesse || 1);

export function dureeProjet(p) {
  let d = 0;
  for (const piste of p.pistes) for (const c of piste.clips) d = Math.max(d, finClip(c));
  return d;
}

// ---------- pistes ----------
export const principale = (p) => p.pistes.find((t) => t.genre === 'principale');
export const pistesDe = (p, genre) => p.pistes.filter((t) => t.genre === genre);

export function trouver(p, id) {
  for (const piste of p.pistes) {
    const i = piste.clips.findIndex((c) => c.id === id);
    if (i >= 0) return { clip: piste.clips[i], piste, index: i };
  }
  return null;
}

/** La piste principale est aimantée : ses clips se suivent sans trou, dans l'ordre. */
export function tasserPrincipale(p) {
  const pr = principale(p);
  pr.clips.sort((a, b) => a.debut - b.debut);
  let t = 0;
  for (const c of pr.clips) { c.debut = t; t += dureeClip(c); }
  // une transition ne peut pas durer plus que la moitié des clips qu'elle relie
  pr.clips.forEach((c, i) => {
    if (!c.transition) return;
    if (i === 0) { c.transition.type = 'aucune'; return; }
    const max = Math.min(dureeClip(c), dureeClip(pr.clips[i - 1])) / 2;
    c.transition.duree = clamp(c.transition.duree || 0.5, 0.1, Math.max(0.1, max));
  });
}

export function chevauche(piste, debut, fin, saufId) {
  return piste.clips.some((c) => c.id !== saufId && debut < finClip(c) - 1e-6 && fin > c.debut + 1e-6);
}

/** Pose un clip sur la première piste libre du bon genre, ou en crée une. */
export function poserSurPisteLibre(p, genre, clip) {
  const fin = finClip(clip);
  let piste = pistesDe(p, genre).find((t) => !chevauche(t, clip.debut, fin, clip.id));
  if (!piste) {
    piste = { id: uid('t'), genre, clips: [] };
    p.pistes.push(piste);
  }
  piste.clips.push(clip);
  piste.clips.sort((a, b) => a.debut - b.debut);
  return piste;
}

export function nettoyerPistes(p) {
  p.pistes = p.pistes.filter((t) => t.genre === 'principale' || t.clips.length);
}

// ---------- fabrication des clips ----------
const visuelParDefaut = () => ({
  cx: 0.5, cy: 0.5, echelle: 1, rotation: 0, opacite: 1, ajustement: 'adapter',
  fonduEntree: 0, fonduSortie: 0, transition: { type: 'aucune', duree: 0.5 }, mouvement: 'aucun',
  volume: 1, muet: false, garderTon: true,
  reglages: { luminosite: 0, contraste: 0, saturation: 0, temperature: 0 },
  filtre: { nom: 'aucun', intensite: 1 },
  chroma: { actif: false, couleur: '#00d000', seuil: 0.25, douceur: 0.1 },
  masque: { forme: 'aucun', taille: 0.8, adoucir: 0.15, inverser: false },
  recadrage: { g: 0, d: 0, h: 0, b: 0 },
  lut: { media: null, intensite: 1 },
  miroirH: false, miroirV: false, fusion: 'source-over', detourage: false,
  animEntree: { type: 'aucune', duree: 0.5 }, animSortie: { type: 'aucune', duree: 0.5 },
  cles: {},
});

export const ANIMABLES_MEDIA = ['echelle', 'cx', 'cy', 'rotation', 'opacite'];
export const ANIMABLES_TEXTE = ['taille', 'cx', 'cy', 'rotation', 'opacite'];
export const FUSIONS = [['source-over', 'Normal'], ['multiply', 'Produit'], ['screen', 'Écran'], ['overlay', 'Incrustation'],
  ['darken', 'Assombrir'], ['lighten', 'Éclaircir'], ['soft-light', 'Lumière douce'], ['hard-light', 'Lumière crue'], ['difference', 'Différence']];
export const ANIMS_CLIP = [['aucune', 'Aucune'], ['fondu', 'Fondu'], ['zoom-avant', 'Zoom avant'], ['zoom-arriere', 'Zoom arrière'],
  ['glisse-gauche', 'Glissement à gauche'], ['glisse-droite', 'Glissement à droite'], ['glisse-haut', 'Glissement en haut'],
  ['glisse-bas', 'Glissement en bas'], ['rebond', 'Rebond'], ['tourne', 'Tourne']];
export const MASQUES = [['aucun', 'Aucun'], ['cercle', 'Cercle'], ['rectangle', 'Rectangle'], ['bande', 'Bande horizontale']];
export const BOUCLES = [['aucune', 'Aucune'], ['pulse', 'Respire'], ['balance', 'Se balance'], ['flotte', 'Flotte'], ['tourne', 'Tourne'],
  ['clignote', 'Clignote'], ['rythme', 'Bat au rythme']];

const stickerParDefaut = () => ({
  cx: 0.5, cy: 0.5, echelle: 0.34, rotation: 0, opacite: 1, boucle: 'aucune', cles: {},
  animEntree: { type: 'rebond', duree: 0.5 }, animSortie: { type: 'aucune', duree: 0.5 },
});

/** Complète un clip enregistré par une version plus ancienne : rien ne casse à l'ouverture. */
export function completerClip(c) {
  const base = c.genre === 'texte' ? { rotation: 0, cles: {} } : c.genre === 'audio' ? { garderTon: true }
    : c.genre === 'sticker' ? stickerParDefaut() : c.genre === 'effet' ? { intensite: 1 } : visuelParDefaut();
  for (const [k, v] of Object.entries(base)) {
    if (c[k] === undefined) c[k] = JSON.parse(JSON.stringify(v));
    else if (v && typeof v === 'object' && !Array.isArray(v) && k !== 'cles') c[k] = { ...v, ...c[k] };
  }
  return c;
}
export function completerProjet(p) {
  p.medias = p.medias || [];
  p.volumeCible = p.volumeCible || '-14';
  p.fond = p.fond || { type: 'couleur', couleur: '#000000' };
  p.marqueurs = Array.isArray(p.marqueurs) ? p.marqueurs : [];
  for (const t of p.pistes) for (const c of t.clips) completerClip(c);
  return p;
}

// ---------- images clés : temps relatifs au début du clip, en secondes de montage ----------
const lisse = (k) => k * k * (3 - 2 * k);
export const PRES_CLE = 1 / 60;

export function valeur(c, k, t) {
  const cles = c.cles && c.cles[k];
  if (!cles || !cles.length) return c[k];
  const lt = t - c.debut;
  if (lt <= cles[0].t) return cles[0].v;
  const der = cles[cles.length - 1];
  if (lt >= der.t) return der.v;
  for (let i = 1; i < cles.length; i += 1) {
    if (lt <= cles[i].t) {
      const a = cles[i - 1];
      const b = cles[i];
      return a.v + (b.v - a.v) * lisse((lt - a.t) / Math.max(1e-6, b.t - a.t));
    }
  }
  return der.v;
}
export const estAnime = (c, k) => !!(c.cles && c.cles[k] && c.cles[k].length);
export const cleIci = (c, k, lt) => (c.cles && c.cles[k] || []).find((x) => Math.abs(x.t - lt) < PRES_CLE * 1.5) || null;

export function poserCle(c, k, lt, v) {
  c.cles = c.cles || {};
  const liste = c.cles[k] || (c.cles[k] = []);
  const ex = cleIci(c, k, lt);
  if (ex) ex.v = v; else liste.push({ t: Math.max(0, lt), v });
  liste.sort((a, b) => a.t - b.t);
}
export function retirerCle(c, k, lt) {
  if (!c.cles || !c.cles[k]) return;
  c.cles[k] = c.cles[k].filter((x) => Math.abs(x.t - lt) >= PRES_CLE * 1.5);
  if (!c.cles[k].length) delete c.cles[k];
}
export function tempsCles(c) {
  const s = new Set();
  for (const liste of Object.values(c.cles || {})) for (const x of liste) s.add(Math.round(x.t * 1000) / 1000);
  return [...s].sort((a, b) => a - b);
}
/** Décale toutes les clés d'un clip dont le début de contenu a bougé de `d` secondes. */
function decalerCles(c, d) {
  for (const liste of Object.values(c.cles || {})) for (const x of liste) x.t -= d;
}

/** Réglages qu'on copie d'un clip à un autre du même genre. */
export const COPIABLES = {
  media: ['ajustement', 'echelle', 'cx', 'cy', 'rotation', 'opacite', 'mouvement', 'fonduEntree', 'fonduSortie', 'reglages', 'filtre',
    'chroma', 'masque', 'recadrage', 'miroirH', 'miroirV', 'fusion', 'animEntree', 'animSortie', 'volume', 'garderTon', 'cles', 'detourage'],
  texte: ['police', 'poids', 'taille', 'couleur', 'boite', 'couleurBoite', 'contour', 'couleurContour', 'alignement', 'cx', 'cy', 'rotation', 'opacite', 'anim', 'cles'],
  sticker: ['couleur', 'couleur2', 'echelle', 'cx', 'cy', 'rotation', 'opacite', 'boucle', 'animEntree', 'animSortie', 'cles'],
  effet: ['intensite'],
};

export function clipDepuisMedia(media, debut = 0) {
  if (media.type === 'audio') {
    return { id: uid(), genre: 'audio', media: media.id, debut, entree: 0, sortie: media.duree, vitesse: 1,
      volume: 1, muet: false, fonduEntree: 0, fonduSortie: 0 };
  }
  if (media.type === 'image') {
    return { id: uid(), genre: 'image', media: media.id, debut, entree: 0, sortie: DUREE_PHOTO, vitesse: 1, ...visuelParDefaut() };
  }
  return { id: uid(), genre: 'video', media: media.id, debut, entree: 0, sortie: media.duree, vitesse: 1, ...visuelParDefaut() };
}

export const STYLES_TEXTE = {
  titre: { nom: 'Titre', police: 'Bricolage Grotesque', poids: 800, taille: 0.075, couleur: '#ffffff', boite: 'aucune', contour: true, couleurContour: '#000000', anim: 'pop' },
  legende: { nom: 'Légende', police: 'Instrument Sans', poids: 700, taille: 0.042, couleur: '#ffffff', boite: 'bande', couleurBoite: '#000000', contour: false, anim: 'fondu' },
  affiche: { nom: 'Affiche', police: 'Anton', poids: 400, taille: 0.09, couleur: '#ffd23f', boite: 'aucune', contour: true, couleurContour: '#1a1208', anim: 'monte' },
  pastille: { nom: 'Pastille', police: 'Bricolage Grotesque', poids: 700, taille: 0.045, couleur: '#141210', boite: 'pastille', couleurBoite: '#ffd23f', contour: false, anim: 'pop' },
  elegant: { nom: 'Élégant', police: 'Playfair Display', poids: 700, taille: 0.06, couleur: '#fff6e8', boite: 'aucune', contour: false, anim: 'fondu' },
  main: { nom: 'Manuscrit', police: 'Caveat', poids: 700, taille: 0.07, couleur: '#ffffff', boite: 'aucune', contour: false, anim: 'machine' },
};

export function clipTexte(debut = 0, style = 'titre', texte) {
  const s = STYLES_TEXTE[style] || STYLES_TEXTE.titre;
  return {
    id: uid(), genre: 'texte', debut, duree: DUREE_TEXTE,
    texte: texte || (style === 'legende' ? 'Ta légende ici' : style === 'main' ? 'Écrit à la main' : 'Ton titre'),
    police: s.police, poids: s.poids, taille: s.taille, couleur: s.couleur,
    boite: s.boite, couleurBoite: s.couleurBoite || '#000000', contour: s.contour, couleurContour: s.couleurContour || '#000000',
    alignement: 'centre', cx: 0.5, cy: style === 'legende' ? 0.82 : 0.5, opacite: 1, anim: s.anim,
    rotation: 0, cles: {},
  };
}

/** Un sticker : une forme dessinée ici (voir stickers.js), posée comme une superposition. */
export function clipSticker(debut = 0, forme = 'etoile', reglages = {}) {
  return { id: uid(), genre: 'sticker', debut, duree: DUREE_TEXTE, forme, couleur: '#ffd23f', couleur2: '#14110e', texte: '',
    ...stickerParDefaut(), ...reglages };
}

/** Un effet plein écran : il s'applique à toute l'image (vidéos et superpositions) pendant sa durée. */
export function clipEffet(debut = 0, effet = 'vignettage') {
  return { id: uid(), genre: 'effet', debut, duree: DUREE_TEXTE, effet, intensite: 1 };
}

// ---------- rythme ----------
/** Les instants (en secondes de montage) où tombe un temps : marqueurs posés à la main et rythmes des sons. */
export function pointsDeRythme(p) {
  const pts = [...(p.marqueurs || [])];
  for (const piste of p.pistes) {
    if (piste.genre !== 'audio') continue;
    for (const c of piste.clips) {
      if (!Array.isArray(c.rythme)) continue;
      const v = c.vitesse || 1;
      for (const tb of c.rythme) if (tb >= c.entree - 1e-6 && tb < c.sortie - 1e-6) pts.push(c.debut + (tb - c.entree) / v);
    }
  }
  pts.sort((a, b) => a - b);
  return pts.filter((x, i) => i === 0 || x - pts[i - 1] > 0.02);
}

/** Pose ou retire un marqueur à l'instant t (un second appui au même endroit le retire). */
export function basculerMarqueur(p, t) {
  p.marqueurs = p.marqueurs || [];
  const i = p.marqueurs.findIndex((x) => Math.abs(x - t) < 0.05);
  if (i >= 0) { p.marqueurs.splice(i, 1); return false; }
  p.marqueurs.push(Math.max(0, t));
  p.marqueurs.sort((a, b) => a - b);
  return true;
}

/**
 * Cale la piste principale sur le rythme : chaque photo dure `pas` temps, chaque vidéo s'arrête sur le dernier
 * temps qu'elle atteint. Rend le nombre de clips recalés.
 */
export function calerSurRythme(p, pas = 1) {
  const temps = pointsDeRythme(p);
  if (temps.length < 2) return 0;
  const pr = principale(p);
  const MIN = 0.3;
  let t = 0;
  let n = 0;
  for (const c of pr.clips) {
    const v = c.vitesse || 1;
    if (c.genre === 'image') {
      const suivants = temps.filter((x) => x > t + MIN - 1e-6);
      const cible = suivants[Math.min(suivants.length, pas) - 1];
      if (cible !== undefined) { c.sortie = c.entree + (cible - t); n += 1; }
    } else if (c.genre === 'video') {
      const finNaturelle = t + dureeClip(c);
      const avant = temps.filter((x) => x > t + MIN - 1e-6 && x <= finNaturelle + 1e-6);
      if (avant.length) { c.sortie = c.entree + (avant[avant.length - 1] - t) * v; n += 1; }
    }
    t += dureeClip(c);
  }
  tasserPrincipale(p);
  return n;
}

// ---------- opérations de montage ----------
/** Insère un média sur la piste principale, juste après le clip sous la tête de lecture. */
export function insererPrincipale(p, media, t) {
  const pr = principale(p);
  const clip = clipDepuisMedia(media, 0);
  // avant le clip sous la tête si on est sur son tout début, sinon juste après lui
  let i = pr.clips.findIndex((c) => t < finClip(c) - 1e-6);
  if (i < 0) i = pr.clips.length;
  else if (t > pr.clips[i].debut + 1e-6) i += 1;
  pr.clips.splice(i, 0, clip);
  let d = 0;
  for (const c of pr.clips) { c.debut = d; d += dureeClip(c); }
  tasserPrincipale(p);
  return clip;
}

export function diviser(p, id, t) {
  const f = trouver(p, id);
  if (!f) return null;
  const c = f.clip;
  const d = t - c.debut;
  if (d < DUREE_MIN || finClip(c) - t < DUREE_MIN) return null;
  const b = copie(c);
  b.id = uid();
  // les images clés se partagent : chaque moitié garde les siennes, plus la valeur exacte à la coupe
  for (const k of Object.keys(c.cles || {})) {
    const v = valeur(c, k, t);
    c.cles[k] = c.cles[k].filter((x) => x.t <= d - PRES_CLE).concat([{ t: d, v }]);
    b.cles[k] = b.cles[k].filter((x) => x.t >= d + PRES_CLE).map((x) => ({ t: x.t - d, v: x.v }));
    b.cles[k].unshift({ t: 0, v });
  }
  if (aDureePropre(c)) {
    c.duree = d; b.debut = t; b.duree -= d;
  } else {
    const coupe = c.entree + d * (c.vitesse || 1);
    c.sortie = coupe; b.entree = coupe; b.debut = t;
    if (b.transition) b.transition = { type: 'aucune', duree: 0.5 };
    if ('fonduSortie' in c) c.fonduSortie = 0;
    if ('fonduEntree' in b) b.fonduEntree = 0;
  }
  f.piste.clips.splice(f.index + 1, 0, b);
  if (f.piste.genre === 'principale') tasserPrincipale(p);
  return b;
}

export function supprimer(p, id) {
  const f = trouver(p, id);
  if (!f) return false;
  f.piste.clips.splice(f.index, 1);
  if (f.piste.genre === 'principale') tasserPrincipale(p);
  nettoyerPistes(p);
  return true;
}

export function dupliquer(p, id) {
  const f = trouver(p, id);
  if (!f) return null;
  const b = copie(f.clip);
  b.id = uid();
  if (f.piste.genre === 'principale') {
    b.debut = f.clip.debut + 1e-4;
    f.piste.clips.splice(f.index + 1, 0, b);
    let d = 0;
    for (const c of f.piste.clips) { c.debut = d; d += dureeClip(c); }
    tasserPrincipale(p);
  } else {
    b.debut = finClip(f.clip);
    poserSurPisteLibre(p, f.piste.genre, b);
  }
  return b;
}

/** Déplace un clip de la piste principale à l'endroit visé (en secondes) : il change de rang. */
export function deplacerPrincipale(p, id, tVise) {
  const pr = principale(p);
  const i = pr.clips.findIndex((c) => c.id === id);
  if (i < 0) return;
  const [c] = pr.clips.splice(i, 1);
  // le bord gauche du clip glissé doit dépasser le milieu d'un voisin pour passer devant lui
  let k = 0;
  let t = 0;
  for (const o of pr.clips) {
    if (t + dureeClip(o) / 2 < tVise) k += 1;
    t += dureeClip(o);
  }
  pr.clips.splice(k, 0, c);
  let d = 0;
  for (const o of pr.clips) { o.debut = d; d += dureeClip(o); }
  tasserPrincipale(p);
}

/** Déplace un clip d'une piste libre ; s'il heurte un voisin, il passe sur une autre piste du même genre. */
export function deplacerLibre(p, id, nouveauDebut, pisteViseeId) {
  const f = trouver(p, id);
  if (!f || f.piste.genre === 'principale') return;
  const c = f.clip;
  c.debut = Math.max(0, nouveauDebut);
  let cible = p.pistes.find((t) => t.id === pisteViseeId && t.genre === f.piste.genre) || f.piste;
  f.piste.clips.splice(f.index, 1);
  if (chevauche(cible, c.debut, finClip(c), c.id)) {
    poserSurPisteLibre(p, f.piste.genre, c);
  } else {
    cible.clips.push(c);
    cible.clips.sort((a, b) => a.debut - b.debut);
  }
  nettoyerPistes(p);
}

/** Rogne le début (cote 'g') ou la fin (cote 'd') d'un clip de `dt` secondes de montage. */
export function rogner(p, id, cote, dt, dureeMedia) {
  const f = trouver(p, id);
  if (!f) return;
  const c = f.clip;
  const v = c.vitesse || 1;
  if (aDureePropre(c)) {
    if (cote === 'g') {
      const d = clamp(dt, -c.debut, c.duree - DUREE_MIN);
      c.debut += d; c.duree -= d;
      decalerCles(c, d);
    } else {
      c.duree = Math.max(DUREE_MIN, c.duree + dt);
    }
  } else if (c.genre === 'image') {
    if (cote === 'g') {
      const lim = f.piste.genre === 'principale' ? -Infinity : -c.debut;
      const d = clamp(dt, lim, c.sortie - c.entree - DUREE_MIN);
      if (f.piste.genre !== 'principale') c.debut += d;
      c.sortie -= d;
      decalerCles(c, d);
    } else {
      c.sortie = Math.max(c.entree + DUREE_MIN, c.sortie + dt);
    }
  } else {
    const max = Number.isFinite(dureeMedia) ? dureeMedia : c.sortie;
    if (cote === 'g') {
      let nouvelleEntree = clamp(c.entree + dt * v, 0, c.sortie - DUREE_MIN * v);
      if (f.piste.genre !== 'principale') {
        const minEntree = c.entree - c.debut * v; // on ne recule pas avant 0 s de montage
        nouvelleEntree = Math.max(nouvelleEntree, minEntree);
        c.debut += (nouvelleEntree - c.entree) / v;
      }
      decalerCles(c, (nouvelleEntree - c.entree) / v);
      c.entree = nouvelleEntree;
    } else {
      c.sortie = clamp(c.sortie + dt * v, c.entree + DUREE_MIN * v, max);
    }
  }
  if (f.piste.genre === 'principale') tasserPrincipale(p);
}

export function changerVitesse(p, id, vitesse) {
  const f = trouver(p, id);
  if (!f || (f.clip.genre !== 'video' && f.clip.genre !== 'audio')) return;
  f.clip.vitesse = clamp(vitesse, VITESSE_MIN, VITESSE_MAX);
  if (f.piste.genre === 'principale') tasserPrincipale(p);
}

/** Fait passer un clip vidéo ou photo de la piste principale à une superposition, ou l'inverse. */
export function basculerSuperposition(p, id) {
  const f = trouver(p, id);
  if (!f || (f.clip.genre !== 'video' && f.clip.genre !== 'image')) return;
  const c = f.clip;
  f.piste.clips.splice(f.index, 1);
  if (f.piste.genre === 'principale') {
    tasserPrincipale(p);
    c.transition = { type: 'aucune', duree: 0.5 };
    if (c.echelle === 1 && c.cx === 0.5 && c.cy === 0.5) c.echelle = 0.5;
    poserSurPisteLibre(p, 'superposition', c);
  } else {
    const pr = principale(p);
    let i = pr.clips.findIndex((k) => c.debut < finClip(k) - 1e-6);
    if (i < 0) i = pr.clips.length;
    c.cx = 0.5; c.cy = 0.5; c.echelle = 1; c.rotation = 0;
    pr.clips.splice(i, 0, c);
    let d = 0;
    for (const k of pr.clips) { k.debut = d; d += dureeClip(k); }
    tasserPrincipale(p);
  }
  nettoyerPistes(p);
}

/** Sépare le son d'une vidéo : un clip son identique se pose sur une piste son, la vidéo devient muette. */
export function detacherSon(p, id) {
  const f = trouver(p, id);
  if (!f || f.clip.genre !== 'video') return null;
  const c = f.clip;
  const son = { id: uid(), genre: 'audio', media: c.media, debut: c.debut, entree: c.entree, sortie: c.sortie, vitesse: c.vitesse || 1,
    volume: c.volume ?? 1, muet: false, fonduEntree: c.fonduEntree || 0, fonduSortie: c.fonduSortie || 0, garderTon: c.garderTon !== false };
  c.muet = true;
  poserSurPisteLibre(p, 'audio', son);
  return son;
}

/** Le clip à l'instant t sur la piste principale, sinon le premier clip d'une autre piste sous la tête. */
export function clipSous(p, t) {
  for (const piste of [principale(p), ...p.pistes.filter((x) => x.genre !== 'principale')]) {
    const c = piste.clips.find((k) => t >= k.debut - 1e-6 && t < finClip(k) - 1e-6);
    if (c) return c;
  }
  return null;
}

/** Les médias encore utilisés par un projet. */
export const mediasUtilises = (p) => new Set(p.pistes.flatMap((t) => t.clips.flatMap((c) => [c.media, c.lut && c.lut.media, c.inverse && c.inverse.media]).filter(Boolean)));

// ---------- annuler / rétablir ----------
export class Historique {
  constructor(limite = 80) { this.limite = limite; this.avant = []; this.apres = []; }
  noter(etat) {
    this.avant.push(JSON.stringify(etat));
    if (this.avant.length > this.limite) this.avant.shift();
    this.apres.length = 0;
  }
  annuler(courant) {
    if (!this.avant.length) return null;
    this.apres.push(JSON.stringify(courant));
    return JSON.parse(this.avant.pop());
  }
  retablir(courant) {
    if (!this.apres.length) return null;
    this.avant.push(JSON.stringify(courant));
    return JSON.parse(this.apres.pop());
  }
  get peutAnnuler() { return this.avant.length > 0; }
  get peutRetablir() { return this.apres.length > 0; }
}

export const etatMontage = (p) => ({ pistes: p.pistes, fond: p.fond, format: p.format, w: p.w, h: p.h, marqueurs: p.marqueurs || [] });

export function formatTemps(s, avecImages = false, fps = 30) {
  s = Math.max(0, s || 0);
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  const base = `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
  if (!avecImages) return base;
  const img = Math.floor((s - Math.floor(s)) * fps + 1e-6);
  return `${base}.${String(img).padStart(2, '0')}`;
}

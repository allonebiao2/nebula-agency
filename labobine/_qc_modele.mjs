// LA BOBINE · contrôles sans navigateur : le modèle, le rythme, le GIF, les LUT.
//     node labobine/_qc_modele.mjs        (sortie 1 si un contrôle échoue)

import * as M from './js/model.js';
import { detecterRythme } from './js/rythme.js';
import { lzw, EncodeurGif, delais, palette } from './js/gif.js';
import { lireCube, appliquerLutPixels } from './js/lut.js';
import { pulsation, EFFETS } from './js/effets.js';
import { STICKERS, AVEC_TEXTE } from './js/stickers.js';

let verts = 0;
const echecs = [];
const ok = (c, m) => { if (c) { verts += 1; console.log(`  ✔ ${m}`); } else { echecs.push(m); console.log(`  ✘ ${m}`); } };
const proche = (a, b, e = 1e-6) => Math.abs(a - b) <= e;

console.log('Modèle : stickers et effets');
{
  const p = M.nouveauProjet('9:16');
  ok(Array.isArray(p.marqueurs) && p.marqueurs.length === 0, 'un projet neuf a une liste de marqueurs vide');
  const s = M.clipSticker(1, 'prix', { texte: '2 500 F' });
  M.poserSurPisteLibre(p, 'sticker', s);
  ok(M.dureeClip(s) === 3 && M.finClip(s) === 4, 'un sticker dure 3 s par défaut');
  const b = M.diviser(p, s.id, 2.5);
  ok(b && proche(s.duree, 1.5) && proche(b.debut, 2.5) && proche(b.duree, 1.5) && b.texte === '2 500 F', 'diviser un sticker donne deux moitiés qui gardent le texte');
  M.rogner(p, b.id, 'd', 1, Infinity);
  ok(proche(b.duree, 2.5), 'rogner la fin d\'un sticker l\'allonge');
  M.rogner(p, b.id, 'g', 0.5, Infinity);
  ok(proche(b.debut, 3) && proche(b.duree, 2), 'rogner le début d\'un sticker le décale');
  const e = M.clipEffet(0, 'pellicule');
  M.poserSurPisteLibre(p, 'effet', e);
  ok(M.dureeClip(e) === 3 && e.intensite === 1, 'un effet dure 3 s, intensité pleine');
  const vieux = { id: 'x', genre: 'sticker', debut: 0, duree: 2, forme: 'etoile' };
  M.completerClip(vieux);
  ok(vieux.boucle === 'aucune' && vieux.echelle > 0 && vieux.animEntree && vieux.cles, 'un sticker incomplet est complété à l\'ouverture');
  const v = M.completerClip({ id: 'v', genre: 'video', media: 'm', debut: 0, entree: 0, sortie: 2 });
  ok(v.lut && v.lut.media === null && v.lut.intensite === 1, 'une ancienne vidéo reçoit un réglage de LUT vide');
  ok(Object.keys(STICKERS).length >= 15 && AVEC_TEXTE.has('prix') && AVEC_TEXTE.has('emoji') && !AVEC_TEXTE.has('fleche'), `${Object.keys(STICKERS).length} stickers, ceux qui portent un texte sont connus`);
  ok(Object.keys(EFFETS).length >= 15, `${Object.keys(EFFETS).length} effets plein écran`);
  ok(M.COPIABLES.sticker.includes('couleur') && M.COPIABLES.effet.includes('intensite'), 'les réglages de sticker et d\'effet se copient');
}

console.log('Modèle : rythme et marqueurs');
{
  const p = M.nouveauProjet('9:16');
  ok(M.basculerMarqueur(p, 1.2) === true && p.marqueurs.length === 1, 'poser un marqueur');
  ok(M.basculerMarqueur(p, 1.22) === false && p.marqueurs.length === 0, 'un second appui au même endroit le retire');
  const photo = (id) => ({ id, type: 'image', duree: 0 });
  for (const id of ['a', 'b', 'c']) M.insererPrincipale(p, photo(id), M.dureeProjet(p));
  const son = M.clipDepuisMedia({ id: 's', type: 'audio', duree: 30 }, 0);
  son.entree = 2; son.sortie = 30;
  son.rythme = Array.from({ length: 60 }, (_, i) => i * 0.5); // 120 BPM depuis 0 s du fichier
  M.poserSurPisteLibre(p, 'audio', son);
  const pts = M.pointsDeRythme(p);
  ok(proche(pts[0], 0) && proche(pts[1], 0.5) && pts.length === 56, `les temps du son, décalés par son entrée (${pts.length} temps)`);
  const n = M.calerSurRythme(p, 2);
  const pr = M.principale(p).clips;
  ok(n === 3 && pr.every((c) => proche(M.dureeClip(c), 1)), `caler tous les 2 temps : chaque photo dure 1 s (${pr.map((c) => M.dureeClip(c)).join(', ')})`);
  ok(M.calerSurRythme(p, 1) === 3 && M.principale(p).clips.every((c) => proche(M.dureeClip(c), 0.5)), 'caler à chaque temps : 0,5 s');
  const vid = M.clipDepuisMedia({ id: 'v', type: 'video', duree: 10 }, 0);
  vid.sortie = 1.8;
  M.principale(p).clips.push(vid);
  M.tasserPrincipale(p);
  M.calerSurRythme(p, 1);
  const finVideo = M.finClip(M.principale(p).clips[3]);
  ok(proche(finVideo % 0.5, 0, 1e-6) && finVideo <= 1.5 + 1.8 + 1e-6, `une vidéo s'arrête sur le dernier temps qu'elle atteint (fin ${finVideo.toFixed(2)} s)`);
  son.vitesse = 2;
  ok(proche(M.pointsDeRythme(p)[1], 0.25), 'à vitesse 2×, les temps se resserrent');
  const etat = M.etatMontage(p);
  ok(Array.isArray(etat.marqueurs), 'les marqueurs font partie de l\'historique (annuler les rend)');
  const c = M.clipDepuisMedia({ id: 'v2', type: 'video', duree: 4 }, 0);
  c.lut = { media: 'lut1', intensite: 1 };
  c.inverse = { media: 'orig', entree: 0, sortie: 4 };
  M.poserSurPisteLibre(p, 'superposition', c);
  const u = M.mediasUtilises(p);
  ok(u.has('lut1') && u.has('orig'), 'une LUT et l\'original d\'une vidéo inversée restent « utilisés »');
}

console.log('Rythme : détection sur des clics synthétiques');
function piste(bpm, decal, duree, sr = 44100) {
  const x = new Float32Array(Math.round(duree * sr));
  let graine = 7;
  const rnd = () => ((graine = (graine * 16807) % 2147483647) / 2147483647) * 2 - 1;
  for (let i = 0; i < x.length; i += 1) x[i] = 0.05 * Math.sin((2 * Math.PI * 220 * i) / sr) + 0.01 * rnd();
  const vrais = [];
  for (let t = decal; t < duree - 0.05; t += 60 / bpm) {
    vrais.push(t);
    const i0 = Math.round(t * sr);
    for (let k = 0; k < 0.03 * sr && i0 + k < x.length; k += 1) x[i0 + k] += 0.8 * rnd() * Math.exp(-k / (0.006 * sr)) + 0.6 * Math.sin((2 * Math.PI * 60 * k) / sr) * Math.exp(-k / (0.02 * sr));
  }
  return { canaux: [x], sr, vrais };
}
for (const [bpm, decal] of [[120, 0.25], [96, 0.6], [140, 0.1]]) {
  const { canaux, sr, vrais } = piste(bpm, decal, 12);
  const r = detecterRythme(canaux, sr);
  const ecarts = r ? r.temps.map((t) => Math.min(...vrais.map((x) => Math.abs(x - t)))) : [1];
  ok(r && Math.abs(r.bpm - bpm) < 1.5, `${bpm} BPM reconnu (${r && r.bpm})`);
  ok(r && Math.abs(r.temps.length - vrais.length) <= 1 && Math.max(...ecarts) < 0.03, `${r && r.temps.length} temps sur ${vrais.length}, à ${(Math.max(...ecarts) * 1000).toFixed(0)} ms au plus`);
}
{
  const silence = [new Float32Array(44100 * 4)];
  ok(detecterRythme(silence, 44100) === null, 'un silence n\'a pas de rythme');
}
ok(proche(pulsation([1, 2], 1), 1) && pulsation([1, 2], 1.5) < 0.1 && pulsation([1, 2], 0.5) === 0, 'la pulsation vaut 1 sur le temps, s\'éteint ensuite, et rien avant le premier');
ok(proche(pulsation(null, 0.5), 1) && proche(pulsation([], 1.0), 1), 'sans rythme marqué, un temps toutes les demi-secondes');

console.log('GIF');
function delzw(octets, tailleMin, n) {
  const clear = 1 << tailleMin;
  const fin = clear + 1;
  let taille = tailleMin + 1;
  let dico = [];
  const reset = () => { dico = []; for (let i = 0; i < clear; i += 1) dico[i] = [i]; dico[clear] = []; dico[fin] = []; taille = tailleMin + 1; };
  reset();
  const sortie = [];
  let pos = 0;
  let acc = 0;
  let nb = 0;
  let avant = null;
  for (;;) {
    while (nb < taille) { acc |= octets[pos++] << nb; nb += 8; }
    const code = acc & ((1 << taille) - 1);
    acc >>>= taille; nb -= taille;
    if (code === clear) { reset(); avant = null; continue; }
    if (code === fin) break;
    let entree;
    if (code < dico.length) entree = dico[code];
    else entree = avant.concat([avant[0]]);
    sortie.push(...entree);
    if (avant) dico.push(avant.concat([entree[0]]));
    if (dico.length === 1 << taille && taille < 12) taille += 1;
    avant = entree;
    if (sortie.length > n + 10) break;
  }
  return sortie;
}
{
  let g = 3;
  const idx = new Uint8Array(60000);
  for (let i = 0; i < idx.length; i += 1) { g = (g * 1103515245 + 12345) & 0x7fffffff; idx[i] = i < 20000 ? (g >> 16) & 255 : i < 40000 ? (i >> 6) & 7 : 200; }
  const z = lzw(idx, 8);
  const back = delzw(z, 8, idx.length);
  ok(back.length === idx.length && back.every((v, i) => v === idx[i]), `LZW : 60 000 indices compressés puis relus à l'identique (${z.length} octets, remises à zéro comprises)`);
  ok(delais(15, 15).reduce((a, b) => a + b, 0) === 100 && delais(10, 15).join(',') === '7,6,7,7,6,7,7,6,7,7', 'délais sans dérive à 15 images/s');
  const hist = new Uint32Array(32768);
  hist[(31 << 10)] = 50; hist[(31 << 5)] = 50; hist[31] = 50; hist[0] = 50;
  const pal = palette(hist, 255);
  ok(pal.length === 4 && pal.some((c) => c[0] === 255 && c[1] === 0) && pal.some((c) => c[2] === 255 && c[0] === 0), 'la palette retrouve exactement 4 couleurs franches');
  const W = 32; const H = 20;
  const enc = new EncodeurGif(W, H);
  const px = new Uint8ClampedArray(W * H * 4).fill(255);
  enc.ajouter(px, 7);
  enc.ajouter(px, 7);
  const blob = enc.finir();
  const u = new Uint8Array(await blob.arrayBuffer());
  ok(String.fromCharCode(...u.slice(0, 6)) === 'GIF89a' && u[u.length - 1] === 0x3b && blob.type === 'image/gif', `fichier GIF bien formé (${u.length} octets)`);
}

console.log('LUT');
{
  const cube = (n, f) => {
    let t = `TITLE "essai"\nLUT_3D_SIZE ${n}\n`;
    for (let b = 0; b < n; b += 1) for (let g = 0; g < n; g += 1) for (let r = 0; r < n; r += 1) t += `${f(r / (n - 1), g / (n - 1), b / (n - 1)).map((x) => x.toFixed(6)).join(' ')}\n`;
    return t;
  };
  const id = lireCube(cube(17, (r, g, b) => [r, g, b]));
  ok(id.taille === 17 && id.titre === 'essai' && id.donnees.length === 17 ** 3 * 3, 'un .cube de 17 se lit');
  const px = Uint8ClampedArray.from([10, 128, 250, 255, 0, 0, 0, 255, 255, 255, 255, 128]);
  const a = Uint8ClampedArray.from(px);
  appliquerLutPixels(a, id, 1);
  ok(a.every((v, i) => Math.abs(v - px[i]) <= 1), 'la LUT identité ne change rien');
  const inv = lireCube(cube(9, (r, g, b) => [1 - r, 1 - g, 1 - b]));
  const c = Uint8ClampedArray.from(px);
  appliquerLutPixels(c, inv, 1);
  ok(Math.abs(c[0] - 245) <= 1 && Math.abs(c[1] - 127) <= 1 && c[3] === 255 && c[11] === 128, `la LUT inverse inverse et garde l'alpha (${c[0]}, ${c[1]}, ${c[2]})`);
  const d = Uint8ClampedArray.from(px);
  appliquerLutPixels(d, inv, 0.5);
  ok(Math.abs(d[0] - 128) <= 1, 'à 50 %, la moitié du chemin');
  let refus = '';
  try { lireCube('LUT_3D_SIZE 4\n0 0 0\n'); } catch (e) { refus = e.message; }
  ok(refus.includes('incomplet'), 'un .cube incomplet est refusé avec un message clair');
  try { lireCube('LUT_1D_SIZE 4\n'); } catch (e) { refus = e.message; }
  ok(refus.includes('1D'), 'une LUT 1D est refusée');
}

console.log(`\n${verts} verts, ${echecs.length} rouges`);
process.exit(echecs.length ? 1 : 0);

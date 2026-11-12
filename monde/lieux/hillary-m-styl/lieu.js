/* HILLARY M. STYL · le salon, construit à partir de plan.json.
   La phrase du lieu : « une galerie de couture lumineuse, où l'on vient voir
   les pièces de près, toucher les tissus, et finir au comptoir avec Hillary ».

   ⛔ Les pièces exposées sont SES pièces, avec SES photos (lues par le
   constructeur dans la vitrine). Aucune robe générée.
   ⚠️ MAQUETTE : décor modélisé dans le code et personnages de porcelaine, en
   attendant le décor précalculé (vague 2) et les vrais personnages (vague 3). */
import { creerMoteur, THREE, texteCanvas, melanger, borner } from '../../socle/moteur.js';
import { Reflector } from 'three/addons/objects/Reflector.js';
import { creerCiel, COTONOU } from '../../socle/ciel.js';
import { creerGraphe, creerDeplacement } from '../../socle/deplacement.js';
import { creerPersonnage, capVersRotation } from '../../socle/personnages.js';
import { habiller } from '../../socle/habiller.js';
import { creerPnj } from '../../socle/pnj.js';
import { creerDialogue } from '../../socle/dialogue.js';
import { creerBoutique, fcfa, libDelai } from '../../socle/boutique.js';
import { creerSon } from '../../socle/son.js';
import { creerReperes } from '../../socle/reperes.js';
import { creerCarnet } from '../../socle/carnet.js';
import { creerOptions } from '../../socle/options.js';
import { creerRessources } from '../../socle/ressources.js';
import { MATIERES, matWax, flaqueLumiere, ombreRonde, PALETTES_WAX } from '../../socle/matieres.js';
import { DONNEES } from './donnees.js';
import { PERSONNES, faitsMaison, dialoguesHillary, dialoguesVisiteuses, conversations, savoirsMaison } from './textes.js';

const params = new URLSearchParams(location.search);
const D = DONNEES, F = faitsMaison(D);
const plan = await (await fetch('plan.json', { cache: 'no-store' })).json();
/* les polices de la maison doivent être là AVANT de peindre affiches et plaques */
await Promise.all(['500 40px "Bodoni Moda"', '600 20px Archivo', '400 20px Manrope'].map(f => document.fonts.load(f))).catch(() => {});
const pieceDe = (id) => D.pieces.find(p => p.id === id);

/* ---------- l'interface de base ---------- */
const calque = document.getElementById('calque');
const ouverture = document.getElementById('ouverture');
const barre = ouverture.querySelector('.ouv-barre i');
const btEntrer = ouverture.querySelector('.ouv-entrer');

const moteur = creerMoteur(document.getElementById('scene'));
const { scene, camera } = moteur;
const q = moteur.qualite;
scene.background = new THREE.Color(0x0b0a0c);
const M = { sol: MATIERES.sol(), platre: MATIERES.platre(), laque: MATIERES.laque(), chene: MATIERES.chene(), laiton: MATIERES.laiton(),
  encre: MATIERES.encre(), creme: MATIERES.creme(), porcelaine: MATIERES.porcelaine(), velours: MATIERES.velours(0xa0145c), verre: MATIERES.verre() };

let aCharger = 0, charges = 0;
const chargeur = new THREE.TextureLoader();
function photo(nom, ok) {
  aCharger++;
  return chargeur.load('img/' + nom, (t) => { t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; charges++; majBarre(); ok && ok(t); },
    undefined, () => { charges++; majBarre(); });
}
function majBarre() { barre.style.width = (aCharger ? Math.round(charges / aCharger * 100) : 100) + '%'; if (charges >= aCharger) btEntrer.disabled = false; }

const boite = (w, h, p, m) => new THREE.Mesh(new THREE.BoxGeometry(w, h, p), m);
/* ⚠️ la position d'un objet Three.js ne se remplace pas (propriété non modifiable), elle se règle */
const a = (o, x, y, z) => { o.position.set(x, y, z); return o; };
/* chaque objet du décor reçoit un NOM STABLE (l'ordre de construction) : la cuisson de la lumière
   dans Blender rend une carte par objet, retrouvée par ce nom */
let numDecor = 0;
function poser(o, x, y, z, ry = 0) { o.position.set(x, y, z); o.rotation.y = ry; if (!o.name) o.name = 'decor-' + (++numDecor); scene.add(o); return o; }
const H = plan.piece.hauteur, LX = plan.piece.largeur / 2, LZ = plan.piece.profondeur / 2;
const interieurs = [];
const plantesDessinees = [], fauteuilsDessines = [];   /* remplacés ensuite par les objets scannés */   /* ce que la nuit change : lumières, flaques, ligne dorée */

/* ================================================================
   1 · LA PIÈCE
   ================================================================ */
const sol = new THREE.Mesh(new THREE.PlaneGeometry(LX * 2, LZ * 2), M.sol);
sol.rotation.x = -Math.PI / 2; scene.add(sol);
if (q.reflets) {
  const miroir = new Reflector(new THREE.PlaneGeometry(LX * 2, LZ * 2), { textureWidth: 1024, textureHeight: 768, color: 0x9a9088 });
  miroir.rotation.x = -Math.PI / 2; miroir.position.y = -0.002; scene.add(miroir);
  M.sol.transparent = true; M.sol.opacity = 0.84;
}
const murs = [
  { w: LX * 2, x: 0, z: -LZ, ry: 0 },
  { w: LZ * 2, x: -LX, z: 0, ry: Math.PI / 2 },
  { w: LZ * 2, x: LX, z: 0, ry: -Math.PI / 2 },
];
for (const m of murs) {
  poser(new THREE.Mesh(new THREE.PlaneGeometry(m.w, H), M.platre), m.x, H / 2, m.z, m.ry);
  const plinthe = boite(m.w, 0.12, 0.02, M.chene); poser(plinthe, m.x + Math.sin(m.ry) * 0.01, 0.06, m.z + Math.cos(m.ry) * 0.01, m.ry);
  const filet = boite(m.w, 0.018, 0.012, M.laiton); poser(filet, m.x + Math.sin(m.ry) * 0.01, 3.05, m.z + Math.cos(m.ry) * 0.01, m.ry);
}

/* la façade vitrée */
const fz = plan.facade.z;
const fac = plan.facade;
for (const [x1, x2] of [[-LX, fac.porte.x1], [fac.porte.x2, LX]]) {
  poser(boite(x2 - x1, fac.allege, 0.22, M.laque), (x1 + x2) / 2, fac.allege / 2, fz + 0.11);
}
poser(boite(LX * 2, H - fac.linteau, 0.22, M.laque), 0, (H + fac.linteau) / 2, fz + 0.11);
poser(boite(fac.porte.x2 - fac.porte.x1, fac.linteau - fac.porte.haut, 0.22, M.laque), 0, (fac.linteau + fac.porte.haut) / 2, fz + 0.11);
for (const x of [-LX + 0.2, fac.vitrines[0].x2 + 0.2, fac.vitrines[1].x1 - 0.2, LX - 0.2]) poser(boite(0.4, fac.linteau - fac.allege, 0.22, M.laque), x, (fac.linteau + fac.allege) / 2, fz + 0.11);
for (const v of fac.vitrines) {
  poser(new THREE.Mesh(new THREE.PlaneGeometry(v.x2 - v.x1, fac.linteau - fac.allege), M.verre), (v.x1 + v.x2) / 2, (fac.linteau + fac.allege) / 2, fz, Math.PI);
  for (let x = v.x1 + 2; x < v.x2 - 0.5; x += 2) poser(boite(0.04, fac.linteau - fac.allege, 0.06, M.laiton), x, (fac.linteau + fac.allege) / 2, fz);
  poser(boite(v.x2 - v.x1, 0.04, 0.06, M.laiton), (v.x1 + v.x2) / 2, fac.allege + 0.02, fz);
}
for (const s of [-1, 1]) {   /* la porte : deux vantaux, poignées de laiton */
  const w = (fac.porte.x2 - fac.porte.x1) / 2;
  poser(new THREE.Mesh(new THREE.PlaneGeometry(w - 0.04, fac.porte.haut - 0.04), M.verre), s * w / 2, fac.porte.haut / 2, fz + 0.02, Math.PI);
  poser(boite(0.03, 0.9, 0.03, M.laiton), s * 0.12, 1.15, fz - 0.04);
}
poser(boite(fac.porte.x2 - fac.porte.x1, 0.05, 0.08, M.laiton), 0, fac.porte.haut, fz);

/* L'ENSEIGNE D'HILLARY, dehors, au-dessus de la porte (Mongazi, 2026-11-12 : « l'expérience
   commence dehors, avec l'enseigne d'Hillary ») : un caisson lumineux blanc, son VRAI logo au
   centre, comme les enseignes des boutiques de Cotonou. Elle s'allume aussi la nuit. */
{
  const hEns = Math.min(0.56, H - fac.linteau - 0.04), yEns = (H + fac.linteau) / 2, zEns = fz + 0.3;
  const lumiere = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffffff, emissiveIntensity: 0.55, roughness: 0.4 });
  poser(boite(2.9, hEns + 0.06, 0.14, M.laque), 0, yEns, zEns - 0.02);
  poser(new THREE.Mesh(new THREE.PlaneGeometry(2.8, hEns), lumiere), 0, yEns, zEns + 0.055);
  new THREE.TextureLoader().load('img/logo.png', (tex) => {
    tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
    const l = hEns * 0.94, logo = new THREE.MeshStandardMaterial({ map: tex, emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: 0.55, roughness: 0.4 });
    poser(new THREE.Mesh(new THREE.PlaneGeometry(l * (620 / 343), l), logo), 0, yEns, zEns + 0.06);
  });
}

/* le plafond, percé du dôme, et SA ligne dorée */
const forme = new THREE.Shape([new THREE.Vector2(-LX, -LZ), new THREE.Vector2(LX, -LZ), new THREE.Vector2(LX, LZ), new THREE.Vector2(-LX, LZ)]);
const trou = new THREE.Path(); trou.absarc(plan.dome.x, plan.dome.z, plan.dome.rayon, 0, Math.PI * 2, true); forme.holes.push(trou);
/* le plafond a sa propre matière, légèrement lumineuse : sous le seul éclairage d'ambiance, il virait au brun */
const plafond = new THREE.Mesh(new THREE.ShapeGeometry(forme, 64), new THREE.MeshStandardMaterial({ color: 0xfbf8f2, roughness: 0.95, emissive: 0x3a3530 }));
plafond.rotation.x = Math.PI / 2; plafond.position.y = H; scene.add(plafond);
const texLavis = texteCanvas(8, 256, (g) => { const gr = g.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, '#f7efe1'); gr.addColorStop(1, '#ffd79a'); g.fillStyle = gr; g.fillRect(0, 0, 8, 256); });
const matLavis = new THREE.MeshBasicMaterial({ map: texLavis, side: THREE.BackSide });
const paroiDome = new THREE.Mesh(new THREE.CylinderGeometry(plan.dome.rayon, plan.dome.rayon, plan.dome.creux, 96, 1, true), matLavis);
poser(paroiDome, plan.dome.x, H + plan.dome.creux / 2, plan.dome.z);
const fondDome = new THREE.Mesh(new THREE.CircleGeometry(plan.dome.rayon, 96), new THREE.MeshBasicMaterial({ color: 0xf7f1e7 }));
fondDome.rotation.x = Math.PI / 2; poser(fondDome, plan.dome.x, H + plan.dome.creux, plan.dome.z);
const matLigne = new THREE.MeshBasicMaterial({ color: new THREE.Color(2.4, 1.75, 0.9), toneMapped: false });
const ligneDoree = new THREE.Mesh(new THREE.TorusGeometry(plan.dome.rayon - 0.02, 0.022, 8, 160), matLigne);
ligneDoree.rotation.x = Math.PI / 2; poser(ligneDoree, plan.dome.x, H - 0.02, plan.dome.z);
interieurs.push({ maj: (n) => { const k = melanger(1.0, 1.35, n); matLigne.color.setRGB(2.4 * k, 1.75 * k, 0.9 * k); matLavis.color.setScalar(melanger(1, 1.05, n)); } });

/* les spots encastrés, et leurs flaques au sol */
const flaques = [];
function spot(x, z, r = 0.9, force = 0.5) {
  const d = new THREE.Mesh(new THREE.CircleGeometry(0.07, 16), new THREE.MeshBasicMaterial({ color: new THREE.Color(2.2, 1.9, 1.5), toneMapped: false }));
  d.rotation.x = Math.PI / 2; poser(d, x, H - 0.005, z);
  const f = flaqueLumiere(r, 0xffe2b0, force); f.position.x = x; f.position.z = z; scene.add(f); flaques.push({ f, force });
}
interieurs.push({ maj: (n, pluie) => { for (const k of flaques) k.f.material.opacity = k.force * melanger(0.45, 1.0, Math.max(n, pluie * 0.6)); } });

/* les vraies lumières, peu nombreuses (chacune coûte sur un téléphone) */
const lampes = [new THREE.PointLight(0xffd9a8, 0, 11, 2), new THREE.PointLight(0xffd2a0, 0, 9, 2)];
lampes[0].position.set(0, 3.5, 0.4); lampes[1].position.set(0, 3.2, -3.8);
scene.add(lampes[0]); if (q.nom !== 'basse') scene.add(lampes[1]);
interieurs.push({ maj: (n, pluie) => { const k = Math.max(n, pluie * 0.5); lampes[0].intensity = melanger(4, 14, k); lampes[1].intensity = melanger(3, 10, k); } });

/* ================================================================
   2 · LES PIÈCES D'HILLARY : podiums, totems, mur des créations
   ================================================================ */
const totems = {};   /* id de pièce -> objet 3D, pour s'y rendre et la regarder */
function plaque(p, w = 512, h = 110) {
  return texteCanvas(w, h, (g, W, Hh) => {
    g.fillStyle = '#141215'; g.fillRect(0, 0, W, Hh);
    g.fillStyle = '#f4efe6'; g.font = '500 40px "Bodoni Moda", Georgia, serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(p.nom, W / 2, Hh * 0.38, W - 30);
    g.fillStyle = '#e3c27a'; g.font = '600 26px Archivo, Arial, sans-serif';
    g.fillText(p.prix != null ? fcfa(p.prix) : 'Sur devis', W / 2, Hh * 0.76);
  });
}
function totem(p, w = 0.92, h = 1.92) {
  const g = new THREE.Group();
  const cadre = new THREE.Group(); g.add(cadre);
  const e = 0.03;
  cadre.add(a(boite(w, e, 0.05, M.laiton), 0, h, 0));
  cadre.add(a(boite(e, h, 0.05, M.laiton), -w / 2, h / 2, 0));
  cadre.add(a(boite(e, h, 0.05, M.laiton), w / 2, h / 2, 0));
  const fond = new THREE.Mesh(new THREE.PlaneGeometry(w - e, h - e), new THREE.MeshBasicMaterial({ color: 0xfff4e4 }));
  fond.position.set(0, h / 2, -0.005); g.add(fond);
  const dos = new THREE.Mesh(new THREE.PlaneGeometry(w, h), M.laque); dos.position.set(0, h / 2, -0.02); dos.rotation.y = Math.PI; g.add(dos);
  const pl = new THREE.Mesh(new THREE.PlaneGeometry(w - e, 0.2), new THREE.MeshBasicMaterial({ map: plaque(p) })); pl.position.set(0, 0.12, 0.004); g.add(pl);
  if (p.img) {
    const mat = new THREE.MeshBasicMaterial({ transparent: true, alphaTest: 0.03, opacity: 0 });
    const ph = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), mat); ph.position.set(0, 0.24 + (h - 0.3) / 2, 0.006); g.add(ph);
    photo(p.img, (t) => {
      mat.map = t; mat.opacity = 1; mat.needsUpdate = true;
      const r = t.image.width / t.image.height, hh = h - 0.34, ww = w - 0.08;
      if (r > ww / hh) ph.scale.set(ww, ww / r, 1); else ph.scale.set(hh * r, hh, 1);
      ph.position.y = 0.24 + ph.scale.y / 2;
    });
  } else {
    const t = texteCanvas(256, 512, (c, W, Hh) => {
      c.fillStyle = '#fff4e4'; c.fillRect(0, 0, W, Hh); c.strokeStyle = '#e6007e'; c.lineWidth = 3;
      c.setLineDash([10, 8]); c.strokeRect(26, 40, W - 52, Hh - 120); c.setLineDash([]);
      c.fillStyle = '#0b0a0c'; c.font = 'italic 34px "Bodoni Moda", Georgia, serif'; c.textAlign = 'center';
      c.fillText('Votre idée,', W / 2, Hh / 2 - 26); c.fillText('cousue ici', W / 2, Hh / 2 + 18);
      c.fillStyle = '#b8005f'; c.font = '600 18px Archivo, Arial'; c.fillText(p.tag ? p.tag.toUpperCase() : '', W / 2, Hh / 2 + 70);
    });
    const ph = new THREE.Mesh(new THREE.PlaneGeometry(w - 0.1, h - 0.36), new THREE.MeshBasicMaterial({ map: t })); ph.position.set(0, 0.24 + (h - 0.36) / 2, 0.006); g.add(ph);
  }
  return g;
}
for (const pd of plan.podiums) {
  const base = new THREE.Mesh(new THREE.CylinderGeometry(pd.r, pd.r, pd.h, 64), M.laque);
  poser(base, pd.x, pd.h / 2, pd.z);
  const anneau = new THREE.Mesh(new THREE.TorusGeometry(pd.r, 0.012, 6, 96), M.laiton); anneau.rotation.x = Math.PI / 2; poser(anneau, pd.x, pd.h, pd.z);
  const o = ombreRonde(pd.r * 1.15, 0.25); o.position.set(pd.x, 0.003, pd.z); scene.add(o);
  spot(pd.x, pd.z, pd.r + 0.7, 0.55);
  const n = pd.pieces.length;
  pd.pieces.forEach((id, k) => {
    const p = pieceDe(id); if (!p) return;
    const t = totem(p);
    let ang;
    if (n === 1) ang = Math.atan2(-pd.x, 2.4 - pd.z);          /* tourné vers l'allée centrale */
    else ang = (k / n) * Math.PI * 2;                           /* en couronne, la première face à l'entrée */
    const rr = n === 1 ? 0 : pd.r * 0.52;
    t.position.set(pd.x + Math.sin(ang) * rr, pd.h, pd.z + Math.cos(ang) * rr); t.rotation.y = ang;
    scene.add(t); totems[id] = t;
  });
}
/* le mur des créations : toutes les autres pièces, en niches éclairées */
{
  const mc = plan.mur_creations;
  const surPodium = new Set(plan.podiums.flatMap(p => p.pieces));
  const reste = D.pieces.filter(p => !surPodium.has(p.id));
  const pas = (mc.z2 - mc.z1) / mc.colonnes;
  reste.slice(0, mc.colonnes * mc.rangees).forEach((p, i) => {
    const col = i % mc.colonnes, rang = Math.floor(i / mc.colonnes);
    const t = totem(p, 0.9, 1.25);
    const z = mc.z1 + pas * (col + 0.5), y = rang === 0 ? 0.55 : 1.92;
    t.position.set(mc.x - 0.09, y, z); t.rotation.y = -Math.PI / 2; scene.add(t); totems[p.id] = t;
  });
  for (let c = 0; c < mc.colonnes; c++) spot(mc.x - 0.9, mc.z1 + pas * (c + 0.5), 0.6, 0.35);
}

/* ================================================================
   3 · LE COMPTOIR, LE MUR DU FOND, LES TISSUS
   ================================================================ */
const cp = plan.comptoir;
{
  const texCannelure = texteCanvas(512, 128, (g, W, Hh) => { for (let x = 0; x < W; x += 16) { const gr = g.createLinearGradient(x, 0, x + 16, 0); gr.addColorStop(0, '#e9e2d6'); gr.addColorStop(0.5, '#ffffff'); gr.addColorStop(1, '#d9d0c2'); g.fillStyle = gr; g.fillRect(x, 0, 16, Hh); } });
  texCannelure.wrapS = THREE.RepeatWrapping; texCannelure.repeat.set(6, 1);
  const corps = boite(cp.longueur, cp.hauteur - 0.05, cp.profondeur, [M.laque, M.laque, M.laque, M.laque, new THREE.MeshStandardMaterial({ map: texCannelure, roughness: 0.4 }), M.laque]);
  poser(corps, cp.x, (cp.hauteur - 0.05) / 2, cp.z);
  poser(boite(cp.longueur + 0.12, 0.05, cp.profondeur + 0.1, M.chene), cp.x, cp.hauteur - 0.025, cp.z);
  poser(boite(cp.longueur + 0.12, 0.012, 0.012, M.laiton), cp.x, cp.hauteur - 0.05, cp.z + cp.profondeur / 2 + 0.05);
  spot(cp.x - 1.2, cp.z + 1.2, 1.0, 0.45); spot(cp.x + 1.2, cp.z + 1.2, 1.0, 0.45);
  /* sur le comptoir : la machine, le mètre ruban magenta, la tablette, une pile de wax */
  const machine = new THREE.Group();
  machine.add(a(boite(0.4, 0.07, 0.18, M.creme), 0, 0.035, 0));
  machine.add(a(boite(0.08, 0.24, 0.14, M.creme), 0.15, 0.17, 0));
  machine.add(a(boite(0.36, 0.08, 0.13, M.creme), 0.0, 0.28, 0));
  machine.add(a(boite(0.04, 0.1, 0.04, M.laiton), -0.15, 0.2, 0));
  const volant = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.03, 24), M.encre); volant.rotation.z = Math.PI / 2; volant.position.set(0.21, 0.24, 0); machine.add(volant);
  poser(machine, cp.x - 1.5, cp.hauteur, cp.z - 0.05, 0.25);
  const metre = new THREE.Mesh(new THREE.TorusGeometry(0.08, 0.014, 8, 32), MATIERES.magenta()); metre.rotation.x = Math.PI / 2; poser(metre, cp.x + 0.45, cp.hauteur + 0.015, cp.z + 0.1);
  const tablette = boite(0.26, 0.012, 0.18, M.encre); poser(tablette, cp.x + 1.1, cp.hauteur + 0.006, cp.z + 0.05, -0.3);
  for (let i = 0; i < 4; i++) poser(boite(0.34, 0.035, 0.26, matWax(40 + i, PALETTES_WAX[(i + 2) % 8])), cp.x + 1.7, cp.hauteur + 0.02 + i * 0.036, cp.z - 0.05, i * 0.05);
}
/* le mur du fond : lames de chêne et logo rétroéclairé */
{
  const lames = new THREE.InstancedMesh(new THREE.BoxGeometry(0.05, 3.5, 0.04), M.chene, 64);
  const m4 = new THREE.Matrix4();
  for (let i = 0; i < 64; i++) { m4.makeTranslation(-2.6 + i * (5.2 / 63), 1.75, -LZ + 0.03); lames.setMatrixAt(i, m4); }
  scene.add(lames);
  const lg = plan.logo;
  const halo = new THREE.Mesh(new THREE.PlaneGeometry(lg.largeur * 1.5, lg.largeur * 0.95), new THREE.MeshBasicMaterial({
    map: texteCanvas(256, 160, (g, W, Hh) => { const gr = g.createRadialGradient(W / 2, Hh / 2, 0, W / 2, Hh / 2, W / 2); gr.addColorStop(0, 'rgba(255,240,220,.95)'); gr.addColorStop(1, 'rgba(255,240,220,0)'); g.fillStyle = gr; g.fillRect(0, 0, W, Hh); }),
    transparent: true, depthWrite: false, toneMapped: false }));
  poser(halo, 0, lg.y, lg.z + 0.035);
  const logoMat = new THREE.MeshBasicMaterial({ transparent: true, opacity: 0 });
  const logo = new THREE.Mesh(new THREE.PlaneGeometry(lg.largeur, lg.largeur * 343 / 620), logoMat); poser(logo, 0, lg.y, lg.z + 0.05);
  photo('logo.png', (t) => { logoMat.map = t; logoMat.opacity = 1; logoMat.needsUpdate = true; });
}
/* les étagères de wax */
{
  const parMat = new Map();
  for (const et of plan.etageres_tissus) {
    const w = et.x2 - et.x1, cx = (et.x1 + et.x2) / 2;
    for (const y of [0.42, 1.12, 1.82, 2.52]) {
      poser(boite(w, 0.035, 0.46, M.chene), cx, y, -LZ + 0.24);
      const n = Math.floor(w / 0.92);
      for (let i = 0; i < n; i++) for (let k = 0; k < 2; k++) {
        const seed = Math.abs(Math.round(et.x1 * 13 + y * 31 + i * 7 + k * 3));
        const cle = seed % 10;
        if (!parMat.has(cle)) parMat.set(cle, []);
        parMat.get(cle).push(new THREE.Vector3(et.x1 + 0.46 + i * (w / n), y + 0.11 + k * 0.17, -LZ + 0.24 + (k ? -0.02 : 0.08)));
      }
    }
    poser(boite(0.04, 2.7, 0.48, M.chene), et.x1, 1.35, -LZ + 0.24); poser(boite(0.04, 2.7, 0.48, M.chene), et.x2, 1.35, -LZ + 0.24);
  }
  const geo = new THREE.CylinderGeometry(0.085, 0.085, 0.86, 20); geo.rotateZ(Math.PI / 2);
  const m4 = new THREE.Matrix4();
  for (const [cle, pts] of parMat) {
    const im = new THREE.InstancedMesh(geo, matWax(100 + cle, PALETTES_WAX[cle % 8], [3, 1]), pts.length);
    pts.forEach((p, i) => { m4.makeTranslation(p.x, p.y, p.z); im.setMatrixAt(i, m4); });
    scene.add(im);
  }
}

/* ================================================================
   4 · LES MURS QUI PARLENT : événements, TikTok
   ================================================================ */
const JOURS = ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'], MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
const dateLongue = (iso) => { const d = new Date(iso + 'T12:00:00'); return isNaN(d) ? iso : `${JOURS[d.getDay()]} ${d.getDate()} ${MOIS[d.getMonth()]}`; };
function affiche(titre, lignes, sur = '') {
  return texteCanvas(512, 716, (g, W, Hh) => {
    g.fillStyle = '#0b0a0c'; g.fillRect(0, 0, W, Hh);
    g.fillStyle = '#e6007e'; g.fillRect(0, 0, W, 10); g.fillRect(0, Hh - 10, W, 10);
    g.fillStyle = '#e3c27a'; g.font = '600 20px Archivo, Arial'; g.textAlign = 'center'; g.fillText(sur || 'HILLARY M. STYL', W / 2, 70);
    g.fillStyle = '#f4efe6'; g.font = '500 56px "Bodoni Moda", Georgia, serif';
    const mots = titre.split(' '); let l = '', y = 180; const out = [];
    for (const m of mots) { if (g.measureText(l + m).width > W - 70) { out.push(l.trim()); l = ''; } l += m + ' '; } out.push(l.trim());
    for (const o of out) { g.fillText(o, W / 2, y); y += 62; }
    g.fillStyle = '#d8cfc2'; g.font = '400 25px Manrope, Arial';
    y += 30; for (const li of lignes) { g.fillText(li, W / 2, y, W - 60); y += 40; }
  });
}
const panneaux = [];
{
  const me = plan.mur_evenements, evs = F.evenements;
  const contenus = evs.length ? evs.slice(0, me.affiches).map(e => ({ tex: affiche(e.titre, [dateLongue(e.date) + (e.heure ? ' · ' + e.heure : ''), e.lieu || '', e.texte || ''].filter(Boolean), 'RENDEZ-VOUS'), info: { titre: e.titre, lignes: [dateLongue(e.date) + (e.heure ? ', ' + e.heure : ''), e.lieu, e.texte].filter(Boolean) } }))
    : [
      { tex: affiche('Les rendez-vous de la maison', ['s\'afficheront ici.']), info: { titre: 'Les rendez-vous de la maison', lignes: ['Les prochains rendez-vous d\'HILLARY M. STYL s\'afficheront sur ce mur dès qu\'ils seront annoncés.'] } },
      { tex: affiche('Sur-mesure', [`${F.n} créations`, F.normal ? `prêtes en ${F.normal} jours` : '', `express : ${libDelai(F.exMin, F.exMax)}`].filter(Boolean)), info: { titre: 'Sur-mesure', lignes: [`${F.n} créations, toutes cousues à vos mesures.`, F.normal ? `Confection : ${F.normal} jours.` : '', `Express : ${libDelai(F.exMin, F.exMax)}, avec un prix propre à chaque pièce.`].filter(Boolean) } },
      { tex: affiche('Partout', [`${F.nbPays} pays desservis`, 'retrait gratuit', 'sur rendez-vous']), info: { titre: 'Livraison', lignes: [D.atelier.adresse, ...D.pays.filter(p => p.frais != null).map(p => `${p.nom} : ${fcfa(p.frais)}, ${p.achem} jour${p.achem > 1 ? 's' : ''} de route`)] } },
    ];
  const pas = (me.z2 - me.z1) / me.affiches;
  contenus.forEach((c, i) => {
    const g = new THREE.Group();
    g.add(a(boite(1.08, 1.48, 0.04, M.laiton), 0, 0, -0.02));
    const aff = new THREE.Mesh(new THREE.PlaneGeometry(1.0, 1.4), new THREE.MeshBasicMaterial({ map: c.tex })); aff.position.z = 0.002; g.add(aff);
    const lampe = boite(0.5, 0.03, 0.08, M.laiton); lampe.position.set(0, 0.86, 0.06); g.add(lampe);
    poser(g, me.x + 0.05, 1.7, me.z1 + pas * (i + 0.5), Math.PI / 2);
    g.userData.info = c.info;
    deplacementPlus(g, { type: 'affiche', i, info: c.info });
    panneaux.push(g);
  });
  spot(me.x + 1.0, (me.z1 + me.z2) / 2, 1.6, 0.4);
  const banc = new THREE.Group(); banc.add(a(boite(2.4, 0.1, 0.5, M.velours), 0, 0.45, 0));
  for (const s of [-1, 1]) banc.add(a(boite(0.05, 0.4, 0.45, M.laiton), s * 1.1, 0.2, 0));
  poser(banc, me.x + 1.0, 0, (me.z1 + me.z2) / 2, Math.PI / 2);
}
/* le coin TikTok : écran vertical, fauteuils de velours, anneau de lumière */
let ecranTiktok, texEcran, ctxEcran;
{
  const ct = plan.coin_tiktok, e = ct.ecran;
  const cv = document.createElement('canvas'); cv.width = 360; cv.height = 640; ctxEcran = cv.getContext('2d');
  texEcran = new THREE.CanvasTexture(cv); texEcran.colorSpace = THREE.SRGBColorSpace;
  ecranTiktok = new THREE.Mesh(new THREE.PlaneGeometry(e.largeur, e.hauteur), new THREE.MeshBasicMaterial({ map: texEcran, toneMapped: false }));
  poser(ecranTiktok, ct.x + 0.06, e.y, ct.z, Math.PI / 2);
  poser(boite(0.04, e.hauteur + 0.08, e.largeur + 0.08, M.encre), ct.x + 0.03, e.y, ct.z);
  deplacementPlus(ecranTiktok, { type: 'tiktok' });
  for (const f of ct.fauteuils) {
    const g = new THREE.Group();
    g.add(a(boite(0.78, 0.38, 0.72, M.velours), 0, 0.26, 0));
    g.add(a(boite(0.78, 0.5, 0.14, M.velours), 0, 0.62, -0.3));
    for (const s of [-1, 1]) g.add(a(boite(0.12, 0.26, 0.7, M.velours), s * 0.38, 0.52, 0));
    poser(g, f.x - 0.25, 0, f.z, -Math.PI / 2); fauteuilsDessines.push(g);
  }
  const anneau = new THREE.Mesh(new THREE.TorusGeometry(0.22, 0.018, 8, 48), new THREE.MeshBasicMaterial({ color: new THREE.Color(2, 2, 2), toneMapped: false }));
  poser(anneau, ct.x + 1.4, 1.6, ct.z - 1.4, -Math.PI / 3);
  poser(boite(0.02, 1.6, 0.02, M.encre), ct.x + 1.4, 0.8, ct.z - 1.4);
  spot(ct.x + 1.6, ct.z, 1.2, 0.4);
}
let diapo = 0;
const avecPhoto = D.pieces.filter(p => p.img);
const imagesEcran = {};
function dessinerEcran() {
  const g = ctxEcran, W = 360, Hh = 640;
  const gr = g.createLinearGradient(0, 0, 0, Hh); gr.addColorStop(0, '#1a0f17'); gr.addColorStop(1, '#0b0a0c'); g.fillStyle = gr; g.fillRect(0, 0, W, Hh);
  const p = avecPhoto[diapo % avecPhoto.length], im = imagesEcran[p.img];
  if (im) { const r = Math.min((W - 30) / im.width, (Hh - 190) / im.height); g.drawImage(im, (W - im.width * r) / 2, 40, im.width * r, im.height * r); }
  g.fillStyle = '#fff'; g.font = '600 15px Archivo, Arial'; g.textAlign = 'left';
  g.fillText(F.tiktok ? F.tiktok.compte : 'HILLARY M. STYL', 18, Hh - 112);
  g.font = '500 24px "Bodoni Moda", Georgia, serif'; g.fillText(p.nom, 18, Hh - 80, W - 36);
  g.fillStyle = '#e3c27a'; g.font = '600 16px Archivo, Arial'; g.fillText(fcfa(p.prix ?? 0) + (p.tag ? '  ·  ' + p.tag : ''), 18, Hh - 52);
  if (F.tiktok) { g.fillStyle = '#fe2c55'; g.beginPath(); g.roundRect(W - 128, Hh - 70, 110, 38, 19); g.fill(); g.fillStyle = '#fff'; g.font = '700 15px Archivo'; g.textAlign = 'center'; g.fillText('S\'abonner', W - 73, Hh - 46); }
  texEcran.needsUpdate = true;
}
for (const p of avecPhoto) { const im = new Image(); im.onload = () => { imagesEcran[p.img] = im; if (p === avecPhoto[0]) dessinerEcran(); }; im.src = 'img/' + p.img; }
setInterval(() => { diapo++; dessinerEcran(); }, 4200);

/* ================================================================
   5 · LA CABINE, L'ATELIER, LES PLANTES, LES MANNEQUINS
   ================================================================ */
function mannequin(couleur = 0xf2ece2) {
  const g = new THREE.Group(); const m = new THREE.MeshStandardMaterial({ color: couleur, roughness: 0.6 });
  const pts = [[0.001, 0], [0.16, 0.0], [0.19, 0.12], [0.15, 0.32], [0.18, 0.5], [0.2, 0.6], [0.16, 0.7], [0.06, 0.74], [0.05, 0.82], [0.001, 0.84]].map(([r, y]) => new THREE.Vector2(r, y));
  const torse = new THREE.Mesh(new THREE.LatheGeometry(pts, 32), m); torse.scale.z = 0.75; torse.position.y = 0.82; g.add(torse);
  g.add(a(new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.82, 8), M.laiton), 0, 0.41, 0));
  g.add(a(new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.2, 0.03, 24), M.laiton), 0, 0.015, 0));
  return g;
}
{
  const cb = plan.cabine;
  poser(boite(0.06, 2.7, cb.z2 - cb.z1, M.laque), cb.x1, 1.35, (cb.z1 + cb.z2) / 2);
  const geo = new THREE.PlaneGeometry(cb.x2 - cb.x1 - 0.1, 2.5, 48, 1);
  const pos = geo.attributes.position; for (let i = 0; i < pos.count; i++) pos.setZ(i, Math.sin(pos.getX(i) * 14) * 0.05);
  geo.computeVertexNormals();
  const rideau = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: 0xa0145c, roughness: 0.9, side: THREE.DoubleSide }));
  poser(rideau, (cb.x1 + cb.x2) / 2, 1.33, cb.z2);
  poser(boite(cb.x2 - cb.x1, 0.025, 0.025, M.laiton), (cb.x1 + cb.x2) / 2, 2.6, cb.z2);
  const miroir = new THREE.Group();
  miroir.add(boite(0.7, 1.8, 0.03, new THREE.MeshStandardMaterial({ color: 0xc8ccd0, metalness: 1, roughness: 0.04 })));
  miroir.add(a(boite(0.76, 1.86, 0.02, M.laiton), 0, 0, -0.02));
  poser(miroir, cb.x1 - 0.05, 1.05, cb.z2 + 0.5, -Math.PI / 2 + 0.25);
}
{
  const at = plan.atelier;
  const table = new THREE.Group();
  table.add(a(boite(1.4, 0.05, 0.72, M.chene), 0, 0.76, 0));
  for (const [x, z] of [[-0.65, -0.3], [0.65, -0.3], [-0.65, 0.3], [0.65, 0.3]]) table.add(a(boite(0.04, 0.74, 0.04, M.laiton), x, 0.37, z));
  const coupon = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 0.55), matWax(77, PALETTES_WAX[1], [1, 1])); coupon.rotation.x = -Math.PI / 2; coupon.position.set(-0.15, 0.79, 0.02); table.add(coupon);
  for (const s of [-1, 1]) { const lame = boite(0.24, 0.006, 0.02, M.laiton); lame.position.set(0.4, 0.795, 0.1); lame.rotation.y = s * 0.25; table.add(lame); }
  poser(table, at.table.x, 0, at.table.z, 0.2);
  const mq = mannequin(); poser(mq, at.mannequin.x, 0, at.mannequin.z, 0.3);
  const ruban = new THREE.Mesh(new THREE.TorusGeometry(0.075, 0.008, 6, 32), MATIERES.magenta()); ruban.rotation.x = Math.PI / 2 - 0.3; ruban.position.set(at.mannequin.x, 1.6, at.mannequin.z); scene.add(ruban);
  const drape = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.3, 0.55, 24, 1, true, 0, Math.PI * 1.3), matWax(88, PALETTES_WAX[0], [1.5, 1])); drape.position.set(at.mannequin.x, 1.12, at.mannequin.z); drape.rotation.y = 1.2; scene.add(drape);
  spot(at.table.x + 0.4, at.table.z + 0.6, 1.0, 0.35);
  poser(mannequin(), 3.3, 0, -4.9, -0.4);
}
for (const pl of plan.plantes) {
  const g = new THREE.Group(); plantesDessinees.push(g);
  g.add(a(new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.2, 0.5, 24), M.laque), 0, 0.25, 0));
  const texF = texteCanvas(128, 256, (c, W, Hh) => { c.fillStyle = '#2f6b3a'; c.beginPath(); c.ellipse(W / 2, Hh / 2, W * 0.42, Hh * 0.46, 0, 0, 7); c.fill(); c.strokeStyle = '#4c8a55'; c.lineWidth = 3; c.beginPath(); c.moveTo(W / 2, 10); c.lineTo(W / 2, Hh - 10); c.stroke(); c.globalCompositeOperation = 'destination-out'; for (let i = 0; i < 5; i++) { c.beginPath(); c.ellipse(W * 0.15, Hh * (0.2 + i * 0.14), 14, 6, 0.4, 0, 7); c.fill(); c.beginPath(); c.ellipse(W * 0.85, Hh * (0.22 + i * 0.14), 14, 6, -0.4, 0, 7); c.fill(); } });
  const mf = new THREE.MeshStandardMaterial({ map: texF, transparent: true, alphaTest: 0.3, side: THREE.DoubleSide, roughness: 0.7 });
  for (let i = 0; i < 9; i++) { const f = new THREE.Mesh(new THREE.PlaneGeometry(0.42, 0.85), mf); const ang = i / 9 * Math.PI * 2; f.position.set(Math.sin(ang) * 0.18, 0.95 + (i % 3) * 0.18, Math.cos(ang) * 0.18); f.rotation.set(-0.5 + (i % 2) * 0.2, ang, 0); g.add(f); }
  poser(g, pl.x, 0, pl.z);
}

/* ================================================================
   6 · LE CIEL, LE DÉPLACEMENT, LES GENS
   ================================================================ */
const ciel = creerCiel(moteur, { facadeZ: fz, largeur: LX * 2, lieu: COTONOU });
const graphe = creerGraphe(plan);
const deplacement = creerDeplacement(moteur, graphe, { depart: params.has('direct') ? 'entree' : 'dehors', calque });
/* on arrive dehors FACE à la boutique et à son enseigne, pas face à la rue */
if (!params.has('direct')) deplacement.tournerVers(new THREE.Vector3(0, 1.85, plan.facade.z));
function deplacementPlus(objet, cible) { (window.__enAttente = window.__enAttente || []).push([objet, cible]); }
for (const [o, c] of window.__enAttente || []) deplacement.ajouterInteractif(o, c);
for (const id in totems) deplacement.ajouterInteractif(totems[id], { type: 'piece', id });

const son = creerSon();
deplacement.surPas.push(() => son.pas());
ciel.surEclair.push(() => son.tonnerre(0.8 + Math.random() * 2.5));

const personnes = JSON.parse(JSON.stringify(PERSONNES));
const ctx = { ciel: ciel.etat, quete: 0, vuHillary: false, visites: 1 };
try { ctx.visites = (+localStorage.getItem('monde:hms:visites') || 0) + 1; localStorage.setItem('monde:hms:visites', ctx.visites); } catch (e) { /* rien */ }

/* Hillary, derrière son comptoir */
/* ⚠️ LES CARNATIONS (Mongazi, 2026-11-12 : « des Noires, claires de peau ou noires ») : Afi brun
   moyen, Sènami brun clair, Maman Sènami brun très foncé ; Hillary provisoire jusqu'à ses photos.
   ⚠️ LES TAILLES (Mongazi, 2026-11-12) : Hillary mesure 1,68 m, c'est un fait. Les
   visiteuses sont inventées : Afi 1,71 m, Sènami 1,64 m, Maman Sènami 1,62 m. La
   caméra du visiteur est à 1,62 m, hauteur d'yeux d'un adulte de 1,72 m environ.
   ⚠️ LES ÂGES (Mongazi, 2026-11-12 : « on doit appliquer les âges aussi dorénavant… Hillary
   26 ans, donc jeune encore ») : Hillary 26 ans, c'est un fait. Afi 29 (partie de Cotonou il y a
   dix ans), Sènami 21 (une adulte, pas une adolescente), Maman Sènami 47 (pas une grand-mère).
   Chaque image d'un personnage dit son âge : personnages/CONSIGNES.md. */
const hillary = creerPersonnage({ nom: 'Hillary', age: 26, taille: 1.68,peau: 0x6a452f, haut: { couleur: 0xe6007e }, bas: { type: 'jupe', wax: 7, palette: PALETTES_WAX[6], ampleur: 0.3 }, coiffe: 'chignon', boucles: true, manchesLongues: false });
hillary.racine.position.set(plan.hillary.x, 0, plan.hillary.z); hillary.racine.rotation.y = capVersRotation(plan.hillary.cap);
scene.add(hillary.racine); hillary.geste('comptoir');
deplacement.ajouterInteractif(hillary.hitbox, { type: 'hillary' });
personnes.hillary.perso = hillary;

const visiteuses = [
  { id: 'afi', perso: creerPersonnage({ nom: 'Afi', age: 29, peau: 0x7a4e33, haut: { couleur: 0x1a1a1c }, bas: { type: 'manteau', couleur: 0xe6d8bf }, jambes: { couleur: 0x1a1a1c }, coiffe: 'court', boucles: true, sac: 0x6b4a32, manchesLongues: true, taille: 1.71 }),
    gouts: { regarder: 2, photo: 0.6, toucher: 1, telephone: 1.2, assis: 0.5, comptoir: 1.4, fenetre: 1.5 }, goutsPlaces: { voir_heros: 2, mur_1: 1.5, mur_2: 1.5, affiches: 1.2 } },
  { id: 'senami', perso: creerPersonnage({ nom: 'Sènami', age: 21, peau: 0x9a6a48, haut: { wax: 3, palette: PALETTES_WAX[6] }, manches: false, jambes: { couleur: 0x35567f }, chaussures: 0xf2f2f2, coiffe: 'tresses', telephone: 0xe6007e, taille: 1.64 }),
    gouts: { photo: 2.5, telephone: 2, assis: 1.6, regarder: 1, toucher: 0.8, comptoir: 0.6, fenetre: 0.6 }, goutsPlaces: { fauteuil_1: 2, fauteuil_2: 2, voir_d1: 1.5, voir_g1: 1.5 } },
  { id: 'maman', perso: creerPersonnage({ nom: 'Maman Sènami', age: 47, peau: 0x4a2f22, haut: { wax: 11, palette: PALETTES_WAX[2] }, bas: { type: 'boubou', wax: 11, palette: PALETTES_WAX[2] }, amples: true, manchesLongues: true, coiffe: 'gele', boucles: true, sac: 0x7a1f2b, taille: 1.62 }),
    gouts: { toucher: 2.2, regarder: 1.6, assis: 1.2, comptoir: 1, telephone: 0.4, photo: 0.2, fenetre: 0.8 }, goutsPlaces: { tissus_g: 2.5, voir_heros: 1.5, affiches: 1.3 } },
].map(v => ({ ...v, nom: PERSONNES[v.id].nom, couleur: PERSONNES[v.id].couleur, texte: PERSONNES[v.id].texte }));
for (const v of visiteuses) personnes[v.id].perso = v.perso;

const boutique = creerBoutique({ calque, donnees: D, son, cleStockage: 'monde:hms:panier', imgBase: 'img/' });
const dialogue = creerDialogue({ calque, son, deplacement, personnes, ctx });
const options = creerOptions({ moteur, calque, son });
/* le carnet : tout ce qu'on apprend de vrai sur la maison, en explorant les réponses */
const carnet = creerCarnet({ calque, savoirs: savoirsMaison(D, F), cle: 'monde:hms:carnet', son, toast: (h, o) => boutique.toast(h, o) });
ctx.apprendre = (id) => carnet.apprendre(id);

/* ---------- ce que les textes peuvent demander au monde ---------- */
const objectifEl = document.createElement('div'); objectifEl.className = 'objectif'; calque.appendChild(objectifEl);
const monde = {
  objectif(texte, sous = null, fini = false) {
    objectifEl.innerHTML = `<small>${fini ? 'Terminé' : 'En cours'}</small>${texte}${sous ? `<br><span style="opacity:.75">${sous}</span>` : ''}`;
    objectifEl.classList.add('visible'); objectifEl.classList.toggle('fini', fini);
    if (fini) { son.valider(); setTimeout(() => objectifEl.classList.remove('visible'), 7000); }
  },
  montrerPiece(id) { const t = totems[id]; if (t) { const p = new THREE.Vector3(); t.getWorldPosition(p); p.y += 1.1; deplacement.tournerVers(p); } },
  ouvrirTiktok(abonner = false) {
    if (!F.tiktok) return;
    const nom = F.tiktok.compte.replace(/^@/, '');
    const url = !abonner && F.tiktok.derniere_video && F.tiktok.derniere_video.lien ? F.tiktok.derniere_video.lien : `https://www.tiktok.com/@${nom}`;
    window.open(url, '_blank', 'noopener');
  },
  afiAuComptoir() { const n = pnj.parId.afi; n.goutsPlaces = { comptoir_g: 400, comptoir_d: 400 }; n.fin = 0; },
};
Object.assign(dialogue.registre, dialoguesHillary({ D, F, boutique, ctx, monde }), dialoguesVisiteuses({ D, F, ctx, monde }));
const pnj = creerPnj({ moteur, plan, graphe, deplacement, dialogue, calque, visiteuses, conversations: conversations(D, F), ctx, personnes, son });
/* l'oreille suit la caméra ; la porte s'ouvre et se referme quand on la passe */
moteur.chaqueImage(() => son.ecouteur(camera));
deplacement.surDepart.push((id) => { if (id === 'dehors' || deplacement.noeud === 'dehors') setTimeout(() => son.porte(new THREE.Vector3(0, 1.3, fz)), 350); });

/* ---------- les repères au pouce, sur tout ce qui se touche ---------- */
/* trois noms au plus sur un téléphone, quatre sur un écran : au-delà, les étiquettes
   s'empilaient sur les pièces (Mongazi, 2026-11-12 : « c'est tout brouillon ») */
const reperes = creerReperes({ moteur, calque, maxNoms: matchMedia('(pointer: coarse)').matches ? 3 : 4 });
const AUTRE = new THREE.Vector3();
for (const id in totems) {
  const t = totems[id], p = pieceDe(id), haut = t.position.y > 1 ? 0.7 : 1.15;
  /* la plaque d'une pièce porte son nom ET son prix, lus au catalogue (revue Impeccable : « une plaque au-dessus de chaque pièce dit son nom et son prix ») */
  const nomPrix = p.prix == null ? p.nom : `${p.nom} · ${Number(p.prix).toLocaleString('fr-FR').replace(/[  ]/g, ' ')} F`;
  reperes.ajouter({ id: 'piece-' + id, nom: nomPrix, ou: (v) => t.getWorldPosition(v).add(AUTRE.set(0, haut + (t.position.y > 1 ? 0 : 0.05), 0)), faire: () => toucherPiece(id) });
}
for (const n of pnj.pnj) {
  reperes.ajouter({ id: 'pnj-' + n.id, genre: 'personne', nom: () => (n.connue ? n.nom : 'Une visiteuse'),
    ou: (v) => n.perso.positionTete(v).add(AUTRE.set(0, 0.32, 0)), faire: () => toucherPnj(n.id), si: () => n.etat !== 'joueur' });
}
reperes.ajouter({ id: 'hillary', genre: 'personne', nom: 'Hillary', ou: (v) => hillary.positionTete(v).add(AUTRE.set(0, 0.32, 0)), faire: () => toucherHillary() });
reperes.ajouter({ id: 'affiches', nom: 'Les affiches', ou: (v) => panneaux[1].getWorldPosition(v).add(AUTRE.set(0, 0.95, 0)), faire: () => (deplacement.noeud !== 'evenements' ? deplacement.allerA('evenements', { puis: () => lireAffiche(1) }) : lireAffiche(1)) });
reperes.ajouter({ id: 'ecran', nom: F.tiktok ? 'Son TikTok' : 'L\'écran de la maison', ou: (v) => ecranTiktok.getWorldPosition(v).add(AUTRE.set(0.1, 1.1, 0)), faire: () => (deplacement.noeud !== 'tiktok' ? deplacement.allerA('tiktok', { puis: toucherTiktok }) : toucherTiktok()) });
reperes.ajouter({ id: 'porte', genre: 'porte', nom: () => (deplacement.noeud === 'dehors' ? 'Entrer' : 'Sortir'), ou: (v) => v.set(0, 2.25, fz),
  faire: () => deplacement.allerA(deplacement.noeud === 'dehors' ? 'entree' : 'dehors') });

/* ---------- les invites posées sur place (« PAYER » de la référence) ---------- */
const invite = document.createElement('button'); invite.type = 'button'; invite.className = 'invite'; calque.appendChild(invite);
const INVITES = {
  /* ⚠️ ancrée sur le COMPTOIR, pas sur sa tête : sa tête respire, et un bouton qui tremble se vise mal au pouce */
  comptoir: { t: 'Parler à Hillary', ou: () => new THREE.Vector3(plan.comptoir.x, 2.2, plan.comptoir.z - 0.4), faire: () => parlerHillary() },
  tiktok: { t: F.tiktok ? `Voir ${F.tiktok.compte}` : 'Regarder l\'écran', ou: () => ecranTiktok.getWorldPosition(new THREE.Vector3()).add(new THREE.Vector3(0, 1.05, 0)), faire: () => toucherTiktok() },
  evenements: { t: 'Lire les affiches', ou: () => panneaux[1].getWorldPosition(new THREE.Vector3()).add(new THREE.Vector3(0, 0.95, 0)), faire: () => lireAffiche(1) },
};
invite.onclick = () => { const i = INVITES[deplacement.noeud]; if (i) { son.clic(); i.faire(); } };
const projI = new THREE.Vector3();
moteur.chaqueImage(() => {
  const i = INVITES[deplacement.noeud];
  const vis = i && !deplacement.enMarche && !dialogue.actif && !document.body.classList.contains('en-fiche') && !document.body.classList.contains('en-cadran');
  if (vis) {
    projI.copy(i.ou()).project(camera);
    const dans = projI.z < 1 && Math.abs(projI.x) < 0.95 && Math.abs(projI.y) < 0.95;
    invite.innerHTML = `<i aria-hidden="true">◆</i>${i.t}`;
    invite.style.opacity = dans ? '1' : '0'; invite.style.pointerEvents = dans ? 'auto' : 'none';
    if (dans) invite.style.transform = `translate(${Math.round((projI.x * 0.5 + 0.5) * innerWidth)}px, ${Math.round((-projI.y * 0.5 + 0.5) * innerHeight)}px) translate(-50%, -100%)`;
  } else { invite.style.opacity = '0'; invite.style.pointerEvents = 'none'; }
});

/* ---------- ce qu'on touche ---------- */
function parlerHillary(noeud = 'hillary') {
  if (deplacement.noeud === 'comptoir' && !deplacement.enMarche) dialogue.ouvrir(noeud);
  else deplacement.allerA('comptoir', { puis: () => dialogue.ouvrir(noeud) });
}
/* toucher Hillary de loin : on va au comptoir, puis les options */
function toucherHillary() {
  const montrer = () => options.ouvrir({
    titre: 'Hillary', sous: 'HILLARY M. STYL',
    ancre: (v) => v.set(plan.comptoir.x, 2.05, plan.comptoir.z - 0.4),
    choix: [
      { t: 'Parler', icone: '💬', principal: true, faire: () => dialogue.ouvrir('hillary') },
      boutique.panier().length ? { t: 'Valider ma commande', icone: '🛍', faire: () => dialogue.ouvrir('h_cest_tout') } : { t: 'Me conseiller', icone: '✨', faire: () => dialogue.ouvrir('h_conseil') },
      { t: 'Laisser', icone: '↩', faire: () => {} },
    ],
  });
  if (deplacement.noeud === 'comptoir' && !deplacement.enMarche) montrer(); else deplacement.allerA('comptoir', { puis: montrer });
}
function toucherTiktok() {
  if (F.tiktok) { monde.ouvrirTiktok(); return; }
  panneau('L\'écran de la maison', ['Il fait défiler les créations d\'HILLARY M. STYL. Touchez une pièce exposée pour la voir de près.']);
}
function lireAffiche(i) { const c = panneaux[i] && panneaux[i].userData.info; if (c) panneau(c.titre, c.lignes); }
function panneau(titre, lignes) {
  boutique.toast(`<b>${titre}</b>${lignes.length ? '<br>' + lignes.join('<br>') : ''}`, { duree: 7000 });
}
function toucherPiece(id) {
  const t = totems[id], p = new THREE.Vector3(); t.getWorldPosition(p); p.y += t.position.y > 1 ? 0.6 : 1.0;
  const d = Math.hypot(p.x - camera.position.x, p.z - camera.position.z);
  if (d < 3.6) { deplacement.tournerVers(p); boutique.ouvrirFiche(id); }
  else deplacement.allerVoir(p, { puis: () => boutique.ouvrirFiche(id) });
}
/* Mongazi : « on va vers lui avec l'animation, ensuite il y aura des options : parler, etc.,
   et là la discussion commence ». Elle s'arrête et se tourne dès qu'on la choisit. */
const SALUTS = { afi: ['Bonjour !', 'Salut !'], senami: ['Coucou !', 'Salut, toi !'], maman: ['Bonjour, mon enfant.', 'Bonne arrivée !'] };
function toucherPnj(id) {
  const n = pnj.parId[id];
  pnj.retenir(id);
  const p = n.perso.positionTete(new THREE.Vector3());
  /* les options n'apparaissent qu'une fois le regard posé sur elle (au téléphone, le champ est
     étroit en largeur : une personne toute proche sort vite du cadre) */
  deplacement.allerPres(new THREE.Vector3(p.x, p.y - 0.1, p.z), { distance: 1.3, puis: () => setTimeout(() => {
    options.ouvrir({
      titre: n.connue ? n.nom : 'Une visiteuse', sous: n.connue ? '' : 'Vous ne vous connaissez pas encore',
      ancre: (v) => n.perso.positionTete(v).add(new THREE.Vector3(0, -0.55, 0)),
      choix: [
        { t: 'Parler', icone: '💬', principal: true, faire: () => pnj.parler(id, id) },
        { t: 'Saluer', icone: '👋', faire: () => { n.perso.geste('saluer'); setTimeout(() => n.perso.geste('repos'), 1700); dialogue.sousTitre(id, SALUTS[id][Math.floor(Math.random() * 2)]); setTimeout(() => pnj.relacher(id), 2600); } },
        { t: 'Laisser', icone: '↩', faire: () => pnj.relacher(id) },
      ],
      auFermer: () => pnj.relacher(id),
    });
  }, 550) });
}
deplacement.surToucher.push((c) => {
  if (c.type === 'piece') { toucherPiece(c.id); return true; }
  if (c.type === 'hillary') { toucherHillary(); return true; }
  if (c.type === 'pnj') { toucherPnj(c.id); return true; }
  if (c.type === 'tiktok') { if (deplacement.noeud !== 'tiktok') deplacement.allerA('tiktok', { puis: toucherTiktok }); else toucherTiktok(); return true; }
  if (c.type === 'affiche') { const go = () => panneau(c.info.titre, c.info.lignes); if (deplacement.noeud !== 'evenements') deplacement.allerA('evenements', { puis: go }); else go(); return true; }
  return false;
});
boutique.surValider.push(() => parlerHillary('h_cest_tout'));
/* ton sac, posé sur le comptoir : il apparaît avec la première pièce (référence : le sac plein qu'on porte) */
const sacComptoir = new THREE.Group();
{
  const corps = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.4, 0.14), new THREE.MeshStandardMaterial({ color: 0xe6007e, roughness: 0.55 }));
  corps.position.y = 0.2; sacComptoir.add(corps);
  for (const s of [-1, 1]) { const anse = new THREE.Mesh(new THREE.TorusGeometry(0.07, 0.008, 6, 20, Math.PI), M.creme); anse.position.set(s * 0.08, 0.4, 0); sacComptoir.add(anse); }
  const mono = new THREE.Mesh(new THREE.PlaneGeometry(0.18, 0.1), new THREE.MeshBasicMaterial({ map: texteCanvas(256, 140, (g, W, H) => { g.fillStyle = '#f4efe6'; g.font = '600 64px "Bodoni Moda", Georgia, serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('H.M.S', W / 2, H / 2); }), transparent: true }));
  mono.position.set(0, 0.24, 0.072); sacComptoir.add(mono);
  sacComptoir.position.set(plan.comptoir.x - 0.6, plan.comptoir.hauteur, plan.comptoir.z + 0.05); sacComptoir.rotation.y = 0.35;
  sacComptoir.visible = boutique.panier().length > 0; scene.add(sacComptoir);
}
boutique.surChange.push(() => {
  const plein = boutique.panier().length > 0;
  if (plein && !sacComptoir.visible) { sacComptoir.visible = true; sacComptoir.scale.setScalar(0.01); }
  if (!plein) sacComptoir.visible = false;
});
moteur.chaqueImage((dt) => { if (sacComptoir.visible && sacComptoir.scale.x < 1) sacComptoir.scale.setScalar(Math.min(1, sacComptoir.scale.x + dt * 3)); });
boutique.surEnvoi.push(() => {
  setTimeout(() => {
    boutique.fermerCadran();
    dialogue.sousTitre('hillary', 'Merci ! Je te réponds sur WhatsApp.');
    boutique.toast('Commande envoyée sur WhatsApp. Votre sac reste ici tant que vous ne le videz pas.', { annuler: () => boutique.vider(), duree: 9000 });
    const b = document.querySelector('.toast:last-child .toast-annuler'); if (b) b.textContent = 'Vider le sac';
  }, 600);
});

/* ---------- Hillary vit derrière son comptoir ---------- */
let hillaryProchain = 4, hillaryAccueil = false, regardProchain = 0, regardToi = true;
moteur.chaqueImage((dt, t) => {
  const d = camera.position.distanceTo(hillary.racine.position);
  /* ⚠️ elle ne te FIXE pas : elle regarde sa tâche, et lève les yeux vers toi aux temps forts
     (quand elle parle, quand tu arrives) ; la référence alterne ainsi (analyse de la vidéo) */
  if (t > regardProchain) { regardProchain = t + 1.8 + Math.random() * 2.6; regardToi = Math.random() < (d < 4 ? 0.65 : 0.3); }
  if (dialogue.actif) hillary.regarder(camera.position);
  else if (d < 5.5 && regardToi) hillary.regarder(camera.position);
  else hillary.regarder(new THREE.Vector3(plan.comptoir.x + 0.9, 1.08, plan.comptoir.z));
  if (!dialogue.actif && t > hillaryProchain) {
    hillaryProchain = t + 6 + Math.random() * 9;
    /* quand on approche, elle ACCUEILLE (mains sur le comptoir ou bras le long du corps) :
       les bras croisés, c'est le geste de l'impatience (analyse de la référence) */
    hillary.geste(d < 5 ? (Math.random() < 0.6 ? 'comptoir' : 'repos') : ['comptoir', 'toucher', 'regarder', 'telephone', 'croises'][Math.floor(Math.random() * 5)]);
  }
  hillary.maj(dt, t);
});
deplacement.surArrivee.push((id) => {
  if (id === 'comptoir' && !hillaryAccueil && !dialogue.actif) { hillaryAccueil = true; hillary.geste('saluer'); setTimeout(() => hillary.geste('repos'), 1800); }
});

/* ---------- la course d'Afi : elle vient d'elle-même ---------- */
let afiPrete = false;
/* l'accroche : Afi vient dans les premières secondes, dès qu'on est entré (référence : la course
   est confiée avant la 10e seconde) */
deplacement.surArrivee.push((id) => { if (id !== 'dehors') afiPrete = true; son.sortir(id === 'dehors'); });
deplacement.surDepart.push(() => son.sortir(false));
moteur.chaqueImage((dt, t) => {
  /* elle n'aborde pas quelqu'un qui commande au comptoir, ni quelqu'un sur le trottoir */
  if (ctx.quete === 0 && afiPrete && t > 7 && !dialogue.actif && !['comptoir', 'dehors'].includes(deplacement.noeud) && !document.body.classList.contains('en-fiche') && !document.body.classList.contains('en-cadran')) {
    if (pnj.aborder('afi', 'afi_course')) ctx.quete = -1;   /* -1 : en route vers le joueur */
  }
});
dialogue.surFermeture.push(() => {
  if (ctx.quete === -1) ctx.quete = 0;
  if (ctx.quete > 0) pnj.annulerAbordage();   /* la course est acceptée : plus de raison de revenir */
  afiPrete = false; setTimeout(() => { afiPrete = ctx.quete === 0; }, 25000);
});

/* ---------- la nuit, la pluie, à l'intérieur ---------- */
moteur.chaqueImage(() => {
  const e = ciel.etat;
  for (const i of interieurs) i.maj(e.nuit, e.pluie);
  moteur.renderer.toneMappingExposure = melanger(1.05, 0.95, e.nuit) * (1 - e.pluie * 0.08);
  scene.environmentIntensity = melanger(0.6, 0.32, e.nuit);
  moteur.reglerHalo(melanger(0.28, 0.5, e.nuit));
  son.ambiance(e);
});

/* ---------- le haut de l'écran ---------- */
const hud = document.createElement('div'); hud.className = 'hud';
hud.innerHTML = `<div class="hud-marque"><img src="img/logo.webp" alt="HILLARY M. STYL"><span>Le salon</span></div><div class="hud-ciel" aria-live="off"></div>
  <button type="button" class="hud-son" aria-label="Couper le son"><svg viewBox="0 0 24 24"><path d="M4 9h4l5-4v14l-5-4H4z"/><path class="ondes" d="M16 9a4 4 0 0 1 0 6M18.5 6.5a8 8 0 0 1 0 11"/></svg></button>`;
calque.appendChild(hud);
const hudCiel = hud.querySelector('.hud-ciel');
/* au téléphone, la plaque du ciel ne garde que l'heure et la température (revue Impeccable) */
const majCiel = () => {
  const m = ciel.libelle().split(' · ');
  if (m.length < 3) { hudCiel.textContent = m.join(' · '); return; }
  hudCiel.innerHTML = `<span class="ciel-lieu">${m[0]} · </span>${m.slice(1, -1).join(' · ')}<span class="ciel-temps"> · ${m[m.length - 1]}</span>`;
};
majCiel(); setInterval(majCiel, 20000); ciel.pret.then(majCiel);
const btSon = hud.querySelector('.hud-son');
const majSon = () => { btSon.querySelector('.ondes').style.opacity = son.coupe ? '0' : '1'; btSon.setAttribute('aria-label', son.coupe ? 'Remettre le son' : 'Couper le son'); };
btSon.onclick = () => { son.basculer(); majSon(); }; majSon();
const maquette = document.createElement('div'); maquette.className = 'maquette';
maquette.textContent = 'Maquette · personnages et décor provisoires'; calque.appendChild(maquette);

/* ---------- l'ouverture : les portes, puis on entre depuis le trottoir ---------- */
majBarre();
moteur.demarrer();
/* la carte de titre (référence : 6 s, en bas à gauche, le lieu, l'heure, le temps qu'il fait) */
function carteDeTitre() {
  const c = document.createElement('div'); c.className = 'carte-titre';
  const h = ciel.etat.heure, m = ciel.libelle().split(' · ').slice(2).join(' · ');
  c.innerHTML = `<b>HILLARY M. STYL</b><span>Cotonou · ${h.h} h ${String(h.m).padStart(2, '0')}${m ? ' · ' + m : ''}</span>`;
  calque.appendChild(c); requestAnimationFrame(() => c.classList.add('visible'));
  setTimeout(() => { c.classList.remove('visible'); setTimeout(() => c.remove(), 900); }, 6000);
}
function entrer() {
  son.demarrer();
  setTimeout(carteDeTitre, 900);
  setTimeout(() => son.machineACoudre(new THREE.Vector3(plan.atelier.table.x, 0.9, plan.atelier.table.z)), 1500);
  ouverture.classList.add('partie');
  setTimeout(() => ouverture.remove(), 2200);
  if (deplacement.noeud === 'dehors') setTimeout(() => deplacement.allerA('entree'), 700);
  setTimeout(() => dialogue.sousTitre('hillary', ctx.visites > 1 ? 'Re-bonjour ! Entre, entre.' : 'Bienvenue ! Viens, approche-toi.'), 2600);
}
btEntrer.onclick = entrer;
if (params.has('direct')) entrer();

/* ================================================================
   LE SALON S'EMBELLIT APRÈS L'OUVERTURE : lumière photographiée, matières scannées,
   objets scannés (Poly Haven, CC0). En 3G, on entre tout de suite ; le reste arrive.
   ================================================================ */
const R = creerRessources(moteur);
const poserAuSol = (o, x, z, hauteurVisee = null, ry = 0) => {
  const b = new THREE.Box3().setFromObject(o);
  if (hauteurVisee) o.scale.multiplyScalar(hauteurVisee / Math.max(0.01, b.max.y - b.min.y));
  const b2 = new THREE.Box3().setFromObject(o);
  o.position.set(x, -b2.min.y, z); o.rotation.y = ry; scene.add(o); return o;
};
async function embellir() {
  await R.eclairage('photo_studio_loft_hall', 0.6);
  await Promise.all([
    R.matiere(M.sol, 'marble_01', { repeat: [8, 6], relief: 0.5 }),
    R.matiere(M.platre, 'painted_plaster_wall', { repeat: [5, 2], teinte: 0xf4ede3, relief: 0.35 }).then(() => { M.platre.map = null; M.platre.color.set(0xf6f0e6); M.platre.needsUpdate = true; }),   /* le relief du plâtre, pas son gris : sa référence a des murs crème lisses */
    R.matiere(M.chene, 'oak_veneer_01', { repeat: [1, 2] }),
    R.matiere(M.velours, 'velour_velvet', { repeat: [2, 2], teinte: 0xd8307f }),
  ]);
  /* les plantes */
  for (let i = 0; i < plan.plantes.length; i++) {
    const o = await R.objet('potted_plant_04'); if (!o) break;
    const pl = plan.plantes[i];
    poserAuSol(o, pl.x, pl.z, 1.5, i * 1.3); plantesDessinees[i].visible = false;
  }
  /* le coin TikTok : deux vrais fauteuils et une table basse */
  const ct = plan.coin_tiktok;
  for (let i = 0; i < ct.fauteuils.length; i++) {
    const o = await R.objet('modern_arm_chair_01'); if (!o) break;
    const f = ct.fauteuils[i];
    poserAuSol(o, f.x - 0.2, f.z, null, -Math.PI / 2); fauteuilsDessines[i].visible = false;
  }
  const table = await R.objet('coffee_table_round_01');
  if (table) poserAuSol(table, ct.fauteuils[0].x + 0.55, (ct.fauteuils[0].z + ct.fauteuils[1].z) / 2, null);
  /* sur le comptoir et les étagères : céramique et laiton */
  const vase = await R.objet('ceramic_vase_01');
  if (vase) { poserAuSol(vase, plan.comptoir.x + 0.75, plan.comptoir.z - 0.12, 0.32); vase.position.y += plan.comptoir.hauteur; }
  for (const [x, y] of [[-6.2, 2.58], [5.9, 2.58]]) {
    const v = await R.objet('brass_vase_01'); if (!v) break;
    poserAuSol(v, x, -plan.piece.profondeur / 2 + 0.24, 0.3); v.position.y += y;
  }
  /* deux suspensions au-dessus du comptoir */
  for (const x of [-1.1, 1.1]) {
    const l = await R.objet('modern_ceiling_lamp_01'); if (!l) break;
    const b = new THREE.Box3().setFromObject(l);
    l.position.set(plan.comptoir.x + x, H - b.max.y, plan.comptoir.z + 0.1); scene.add(l);
  }
  document.body.classList.add('embelli');
}
setTimeout(() => embellir().catch(e => console.warn('embellissement incomplet', e)), params.has('direct') ? 200 : 2500);

/* AFI, LE PREMIER VRAI PERSONNAGE (TRELLIS.2 puis Mixamo, 2026-11-12) : son corps et ses
   sept animations arrivent après l'ouverture ; d'ici là, et si le chargement échoue, sa
   silhouette tient sa place. Sènami et Maman Sènami suivront le même chemin. */
setTimeout(() => habiller(personnes.afi.perso, { dossier: 'personnages/afi/', prefixe: 'afi', taille: 1.71 })
  .then(() => { const v = visiteuses.find(x => x.id === 'afi'); if (v) v.gouts.assis = 0; })   /* pas encore d'animation assise */
  .catch(e => console.warn('Afi reste en silhouette', e)), params.has('direct') ? 600 : 3200);


/* EXPORTER LE DÉCOR FIXE POUR BLENDER (la cuisson de la lumière, REPRENDRE-ICI.md) : formes, couleurs
   et lampes seulement (⚠️ les textures dessinées par programme font échouer l'exporteur, et la
   cuisson n'en a pas besoin) ;
   sans personnages, sans repères, sans vitres ni miroir ; avec les lumières. Lancé par
   monde/_outils/exporter_decor.py, qui récupère le téléchargement `salon-decor.glb`. */
async function exporterDecor() {
  const { GLTFExporter } = await import('three/addons/exporters/GLTFExporter.js');
  const exclus = new Set([hillary.racine, ...visiteuses.map(v => v.perso.racine)]);
  const dehors = (o) => { for (let q = o; q; q = q.parent) if (exclus.has(q)) return true; return false; };
  const racine = new THREE.Group();
  scene.updateMatrixWorld(true);
  scene.traverse((o) => {
    if (dehors(o) || !o.visible) return;
    if (o.isMesh && o.name && !o.isReflector && !(o.material && o.material.transparent)) {
      const m = o.material || {};
      const c = new THREE.Mesh(o.geometry, new THREE.MeshStandardMaterial({ color: m.color ? m.color.clone() : 0xffffff, roughness: m.roughness ?? 0.8, metalness: m.metalness ?? 0, emissive: m.emissive ? m.emissive.clone() : 0x000000 }));
      c.applyMatrix4(o.matrixWorld); c.name = o.name; racine.add(c);
    } else if (o.isPointLight || o.isSpotLight || o.isDirectionalLight) {
      const l = o.clone(false); l.applyMatrix4(o.parent ? o.parent.matrixWorld : new THREE.Matrix4()); racine.add(l);
    }
  });
  const glb = await new GLTFExporter().parseAsync(racine, { binary: true });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([glb], { type: 'model/gltf-binary' })); a.download = 'salon-decor.glb'; a.click();
  return racine.children.length;
}

/* pour les contrôles automatiques */
window.__monde = { exporterDecor, moteur, deplacement, dialogue, boutique, pnj, ciel, ctx, totems, hillary, plan, F, D, carnet, options, toucherPnj, toucherHillary };

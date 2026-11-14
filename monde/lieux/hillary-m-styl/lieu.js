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
/* LE SALON DE SES IMAGES (Mongazi, 2026-11-13, `ARRIVEES.md` : « parfait, intègre ») : des murs crème, un
   plafond clair, un sol crème qui brille. De jour, la pièce est lumineuse comme sur ses huit images ; le
   soir, elle se TAMISE par la lumière (lampes baissées, gorge dorée qui domine), plus par la peinture.
   ⚠️ Avant (2026-11-12, « tamisé et ultra stylé ») : murs taupe expresso et plafond brun nuit, jour et nuit. */
const MUR = 0xece3d6;
/* la façade : anthracite satiné, comme les boutiques de luxe le soir (audit jeu vidéo, vague 1) */
M.facade = new THREE.MeshStandardMaterial({ color: 0x1d1a19, roughness: 0.38, metalness: 0.15 });
M.platre.color.set(MUR);

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
  poser(boite(x2 - x1, fac.allege, 0.22, M.facade), (x1 + x2) / 2, fac.allege / 2, fz + 0.11);
}
poser(boite(LX * 2, H - fac.linteau, 0.22, M.facade), 0, (H + fac.linteau) / 2, fz + 0.11);
poser(boite(fac.porte.x2 - fac.porte.x1, fac.linteau - fac.porte.haut, 0.22, M.facade), 0, (fac.linteau + fac.porte.haut) / 2, fz + 0.11);
for (const x of [-LX + 0.2, fac.vitrines[0].x2 + 0.2, fac.vitrines[1].x1 - 0.2, LX - 0.2]) poser(boite(0.4, fac.linteau - fac.allege, 0.22, M.facade), x, (fac.linteau + fac.allege) / 2, fz + 0.11);
for (const v of fac.vitrines) {
  poser(new THREE.Mesh(new THREE.PlaneGeometry(v.x2 - v.x1, fac.linteau - fac.allege), M.verre), (v.x1 + v.x2) / 2, (fac.linteau + fac.allege) / 2, fz, Math.PI);
  for (let x = v.x1 + 2; x < v.x2 - 0.5; x += 2) poser(boite(0.04, fac.linteau - fac.allege, 0.06, M.laiton), x, (fac.linteau + fac.allege) / 2, fz);
  poser(boite(v.x2 - v.x1, 0.04, 0.06, M.laiton), (v.x1 + v.x2) / 2, fac.allege + 0.02, fz);
}
const vantaux = [];
for (const s of [-1, 1]) {   /* la porte : deux vantaux coulissants, poignées de laiton */
  const w = (fac.porte.x2 - fac.porte.x1) / 2;
  const verre = poser(new THREE.Mesh(new THREE.PlaneGeometry(w - 0.04, fac.porte.haut - 0.04), M.verre), s * w / 2, fac.porte.haut / 2, fz + 0.02, Math.PI);
  const poignee = poser(boite(0.03, 0.9, 0.03, M.laiton), s * 0.12, 1.15, fz - 0.04);
  vantaux.push({ s, w, verre, poignee, x0: verre.position.x, xp: poignee.position.x });
}
/* les portes vitrées coulissent dans le mur, en 0,9 s, quand on entre */
let portesOuvertes = false;
function ouvrirPortes() {
  if (portesOuvertes) return; portesOuvertes = true;
  let t = 0;
  const fin = moteur.chaqueImage((dt) => {
    t = Math.min(1, t + dt / 0.9); const e = 1 - Math.pow(1 - t, 3);
    for (const v of vantaux) { v.verre.position.x = v.x0 + v.s * v.w * 0.92 * e; v.poignee.position.x = v.xp + v.s * v.w * 0.92 * e; }
    if (t >= 1) fin();
  });
}
poser(boite(fac.porte.x2 - fac.porte.x1, 0.05, 0.08, M.laiton), 0, fac.porte.haut, fz);

/* L'ENSEIGNE D'HILLARY, dehors, au-dessus de la porte (Mongazi, 2026-11-12 : « l'expérience
   commence dehors, avec l'enseigne d'Hillary ») : un caisson lumineux blanc, son VRAI logo au
   centre, comme les enseignes des boutiques de Cotonou. Elle s'allume aussi la nuit. */
{
  /* posée sur le bandeau de l'immeuble, au-dessus du linteau : lisible depuis la rue */
  const hEns = 0.9, yEns = H + 0.75, zEns = fz + 0.3;
  poser(boite(LX * 2 + 0.4, 1.7, 0.3, M.facade), 0, H + 0.85, fz + 0.12);   /* le bandeau */
  poser(new THREE.Mesh(new THREE.BoxGeometry(LX * 2 - 0.6, 0.025, 0.04), new THREE.MeshBasicMaterial({ color: 0xffd2a0, toneMapped: false })), 0, fac.linteau - 0.04, fz + 0.24);   /* le filet de lumière sous le linteau */
  poser(boite(3.4, hEns + 0.08, 0.14, M.facade), 0, yEns, zEns - 0.02);

  const imgLogo = new Image();
  imgLogo.onload = () => {
    /* lettres lumineuses sur bandeau sombre : le fond blanc du logo s'efface, son noir devient crème */
    const c = document.createElement('canvas'); c.width = imgLogo.naturalWidth; c.height = imgLogo.naturalHeight;
    const g = c.getContext('2d'); g.drawImage(imgLogo, 0, 0);
    const d = g.getImageData(0, 0, c.width, c.height), px = d.data;
    for (let i = 0; i < px.length; i += 4) {
      const r = px[i], v = px[i + 1], b = px[i + 2], mx = Math.max(r, v, b), mn = Math.min(r, v, b), sat = mx - mn;
      if (sat < 40 && mn > 200) px[i + 3] = Math.round(255 * Math.max(0, (255 - mn) / 55));          /* le blanc s'efface en douceur */
      else if (sat < 40 && mx < 110) { px[i] = 246; px[i + 1] = 243; px[i + 2] = 238; }                 /* le noir devient crème */
    }
    g.putImageData(d, 0, 0);
    const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
    const l = hEns * 0.94, logo = new THREE.MeshBasicMaterial({ map: tex, transparent: true, toneMapped: false });
    poser(new THREE.Mesh(new THREE.PlaneGeometry(l * (c.width / c.height), l), logo), 0, yEns, zEns + 0.06);
  };
  imgLogo.src = 'img/logo.png';
}

/* L'IMMEUBLE AU-DESSUS DE LA BOUTIQUE (audit jeu vidéo, vague 1) : sans lui, la façade s'arrêtait
   net à 4,20 m, une boîte posée dans le vide. Deux étages d'enduit sombre, des fenêtres dont
   certaines s'allument le soir, une corniche. */
const fenetresImmeuble = [];
/* l'enduit de l'immeuble : de jour il prend le soleil (le tamisage de l'intérieur ne doit pas assombrir la rue) */
const enduitImmeuble = new THREE.MeshStandardMaterial({ color: 0x5a4f49, roughness: 0.92, emissive: 0x000000 });
/* une fenêtre éclairée : lueur chaude plus forte en bas, un rideau tiré d'un côté, des croisillons */
function texFenetre(h) {
  return texteCanvas(128, 192, (g, W, Hh) => {
    const gr = g.createLinearGradient(0, 0, 0, Hh); gr.addColorStop(0, '#5a3a1e'); gr.addColorStop(0.55, '#c98a4a'); gr.addColorStop(1, '#f2c48a');
    g.fillStyle = gr; g.fillRect(0, 0, W, Hh);
    const cote = h < 0.5 ? 0 : W * 0.55; g.fillStyle = 'rgba(40,22,12,.55)'; g.fillRect(cote, 0, W * 0.45, Hh);
    for (let x = cote + 6; x < cote + W * 0.45; x += 9) { g.fillStyle = 'rgba(20,10,6,.25)'; g.fillRect(x, 0, 3, Hh); }
    g.fillStyle = '#1d1a19'; g.fillRect(W / 2 - 3, 0, 6, Hh); g.fillRect(0, Hh * 0.42 - 3, W, 6);
  });
}
{
  const enduit = enduitImmeuble;
  poser(boite(LX * 2 + 0.8, 6.2, 0.4, enduit), 0, H + 1.7 + 3.1, fz + 0.05);
  poser(boite(LX * 2 + 1.0, 0.16, 0.6, M.facade), 0, H + 1.7 + 6.2, fz + 0.1);
  const vitre = new THREE.MeshStandardMaterial({ color: 0x0e1014, roughness: 0.15, metalness: 0.3 });
  let graine = 7;
  const hasard = () => ((graine = (graine * 9301 + 49297) % 233280) / 233280);
  for (const etage of [0, 1]) for (let i = 0; i < 6; i++) {
    const x = -LX + 1.2 + i * ((LX * 2 - 2.4) / 5), y = H + 2.6 + etage * 3.0;
    const allumee = hasard() < 0.45;
    const m = allumee ? new THREE.MeshStandardMaterial({ color: 0x1a120c, emissive: 0xffffff, emissiveMap: texFenetre(hasard()), emissiveIntensity: 0, roughness: 0.3 }) : vitre;
    poser(new THREE.Mesh(new THREE.PlaneGeometry(1.0, 1.5), m), x, y, fz + 0.26);
    poser(boite(1.12, 0.06, 0.12, M.facade), x, y - 0.78, fz + 0.3);
    if (allumee) fenetresImmeuble.push(m);
  }
}
/* le ciel au-dessus de la rue : bleu le jour ; la nuit, bleu profond et lueur chaude de la ville à l'horizon */
const ciel3d = new THREE.ShaderMaterial({
  side: THREE.BackSide, depthWrite: false, toneMapped: false,
  uniforms: { haut: { value: new THREE.Color(0x5d8fc8) }, horizon: { value: new THREE.Color(0xc9dbe8) } },
  vertexShader: 'varying vec3 vP; void main() { vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: 'uniform vec3 haut, horizon; varying vec3 vP; void main() { float h = clamp(vP.y * 1.6, 0.0, 1.0); gl_FragColor = vec4(mix(horizon, haut, pow(h, 0.7)), 1.0); }',
});
const domeCiel = new THREE.Mesh(new THREE.SphereGeometry(70, 32, 16), ciel3d); domeCiel.renderOrder = -1; scene.add(domeCiel);
const CIEL = { jourH: new THREE.Color(0x5d8fc8), jourB: new THREE.Color(0xc9dbe8), nuitH: new THREE.Color(0x060914), nuitB: new THREE.Color(0x3a2418) };

/* LE PLAFOND DE SES IMAGES : clair, percé d'une grande COUPOLE OVALE dont le bord porte une gorge lumineuse
   dorée (`salon-vue-comptoir-arche`, `salon-plan-iso`). La lumière de la gorge monte et lave la paroi de la
   coupole, puis se perd dans son fond crème. (Avant : un rond de 3,4 m, ambré sur fond brun nuit.) */
const coupole = { x: plan.dome.x, z: plan.dome.z, rx: plan.dome.rx ?? plan.dome.rayon, rz: plan.dome.rz ?? plan.dome.rayon, creux: plan.dome.creux };
const dansCoupole = (x, z) => ((x - coupole.x) / coupole.rx) ** 2 + ((z - coupole.z) / coupole.rz) ** 2 < 1;
const forme = new THREE.Shape([new THREE.Vector2(-LX, -LZ), new THREE.Vector2(LX, -LZ), new THREE.Vector2(LX, LZ), new THREE.Vector2(-LX, LZ)]);
const trou = new THREE.Path(); trou.absellipse(coupole.x, coupole.z, coupole.rx, coupole.rz, 0, Math.PI * 2, true); forme.holes.push(trou);
/* légèrement lumineux : sous les seuls spots qui éclairent vers le bas, un plafond clair virait au gris */
const matPlafond = new THREE.MeshStandardMaterial({ color: 0xf2ece3, roughness: 0.92, emissive: 0x1c1813 });
const plafond = new THREE.Mesh(new THREE.ShapeGeometry(forme, 96), matPlafond);
plafond.rotation.x = Math.PI / 2; plafond.position.y = H; scene.add(plafond);
/* la paroi de la coupole : chaude en bas (la gorge), crème en haut */
const texLavis = texteCanvas(8, 256, (g) => { const gr = g.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, '#eadfcf'); gr.addColorStop(0.5, '#f4e3c8'); gr.addColorStop(1, '#ffd79c'); g.fillStyle = gr; g.fillRect(0, 0, 8, 256); });
const matLavis = new THREE.MeshBasicMaterial({ map: texLavis, side: THREE.BackSide });
const paroiDome = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, coupole.creux, 128, 1, true), matLavis);
paroiDome.scale.set(coupole.rx, 1, coupole.rz);
poser(paroiDome, coupole.x, H + coupole.creux / 2, coupole.z);
/* le fond : crème, plus clair au bord où la gorge l'éclaire */
const texFond = texteCanvas(256, 256, (g, W) => { const gr = g.createRadialGradient(W / 2, W / 2, W * 0.1, W / 2, W / 2, W / 2); gr.addColorStop(0, '#e6dccd'); gr.addColorStop(0.75, '#ede2d1'); gr.addColorStop(1, '#f8e7cb'); g.fillStyle = gr; g.fillRect(0, 0, W, W); });
const matFondDome = new THREE.MeshBasicMaterial({ map: texFond });
const fondDome = new THREE.Mesh(new THREE.CircleGeometry(1, 128), matFondDome);
fondDome.rotation.x = Math.PI / 2; fondDome.scale.set(coupole.rx, coupole.rz, 1); poser(fondDome, coupole.x, H + coupole.creux, coupole.z);
/* la gorge dorée : un tube qui suit l'ovale */
const matLigne = new THREE.MeshBasicMaterial({ color: new THREE.Color(2.4, 1.75, 0.9), toneMapped: false });
const ovale = new THREE.CatmullRomCurve3(new THREE.EllipseCurve(0, 0, coupole.rx - 0.03, coupole.rz - 0.03).getPoints(160).slice(0, -1).map(p => new THREE.Vector3(p.x, 0, p.y)), true);
const ligneDoree = new THREE.Mesh(new THREE.TubeGeometry(ovale, 320, 0.024, 8, true), matLigne);
poser(ligneDoree, coupole.x, H - 0.02, coupole.z);
/* le soir, la gorge DOMINE (la pièce baisse, elle non) */
interieurs.push({ maj: (n) => { const k = melanger(1.0, 1.2, n); matLigne.color.setRGB(2.4 * k, 1.75 * k, 0.9 * k); matLavis.color.setScalar(melanger(1, 0.9, n)); matFondDome.color.setScalar(melanger(1, 0.62, n)); matPlafond.emissive.setRGB(0.11, 0.094, 0.074).multiplyScalar(melanger(1, 0.45, n)); } });

/* les spots encastrés, et leurs flaques au sol (dans la coupole, le spot est au fond de la coupole) */
const flaques = [], spotsEncastres = [];
const hauteurPlafond = (x, z) => dansCoupole(x, z) ? H + coupole.creux : H;
function spot(x, z, r = 0.9, force = 0.5) {
  const y = hauteurPlafond(x, z);
  spotsEncastres.push({ x, z, r, force, y });
  const d = new THREE.Mesh(new THREE.CircleGeometry(0.07, 16), new THREE.MeshBasicMaterial({ color: new THREE.Color(2.2, 1.9, 1.5), toneMapped: false }));
  d.rotation.x = Math.PI / 2; poser(d, x, y - 0.005, z);
  const f = flaqueLumiere(r, 0xffe2b0, force); f.position.x = x; f.position.z = z; scene.add(f); flaques.push({ f, force });
}
interieurs.push({ maj: (n, pluie) => { for (const k of flaques) k.f.material.opacity = k.force * melanger(1.0, 0.7, n); } });
/* la couronne de spots autour de la coupole, sur le plafond plat (ses images en montrent partout) */
for (let i = 0; i < 14; i++) {
  const t = (i + 0.5) / 14 * Math.PI * 2, x = coupole.x + Math.cos(t) * (coupole.rx + 0.8), z = coupole.z + Math.sin(t) * (coupole.rz + 0.75);
  if (Math.abs(x) < LX - 0.5 && z > -LZ + 0.5 && z < fz - 0.5) spot(x, z, 0.75, 0.22);
}

/* les vraies lumières, peu nombreuses (chacune coûte sur un téléphone). De jour la boutique est allumée
   en plein ; le soir elle baisse (le tamisé) */
const lampes = [new THREE.PointLight(0xffc98a, 0, 11, 2), new THREE.PointLight(0xffc488, 0, 9, 2)];
lampes[0].position.set(0, 3.5, 0.4); lampes[1].position.set(0, 3.2, -3.8);
scene.add(lampes[0]); if (q.nom !== 'basse') scene.add(lampes[1]);
const TAMISE = 0.45;   /* la force des lampes le soir, rapportée à celle du jour (les projecteurs sur les créations, eux, restent) */
interieurs.push({ maj: (n) => { const k = melanger(1, TAMISE, n); lampes[0].intensity = 9 * k; lampes[1].intensity = 7 * k; } });

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
/* LE BOIS CLAIR CANNELÉ de ses images (comptoir et arche) : des cannelures de 3 cm, une couleur de chêne
   blond et une carte de relief qui creuse vraiment chaque cannelure (la lumière rasante les dessine) */
const CANNELURES = 32;   /* par mètre de texture */
const texCannelure = texteCanvas(512, 256, (g, W, Hh) => {
  g.fillStyle = '#d2ad80'; g.fillRect(0, 0, W, Hh);
  const r = (s => () => (s = (s * 9301 + 49297) % 233280) / 233280)(5);
  for (let i = 0; i < 260; i++) { g.strokeStyle = `rgba(${150 + r() * 40},${105 + r() * 30},${60 + r() * 20},${0.08 + r() * 0.1})`; g.lineWidth = 0.6 + r() * 1.4; const x = r() * W; g.beginPath(); g.moveTo(x, 0); g.bezierCurveTo(x + r() * 6 - 3, Hh * 0.3, x + r() * 6 - 3, Hh * 0.7, x + r() * 4 - 2, Hh); g.stroke(); }   /* le fil du bois */
  const p = W / 16; for (let x = 0; x < W; x += p) { const gr = g.createLinearGradient(x, 0, x + p, 0); gr.addColorStop(0, 'rgba(90,60,30,.28)'); gr.addColorStop(0.18, 'rgba(255,240,215,.10)'); gr.addColorStop(0.55, 'rgba(255,240,215,.16)'); gr.addColorStop(1, 'rgba(90,60,30,.22)'); g.fillStyle = gr; g.fillRect(x, 0, p, Hh); }
});
texCannelure.wrapS = texCannelure.wrapT = THREE.RepeatWrapping; texCannelure.repeat.set(CANNELURES / 16, 1);
const norCannelure = (() => {   /* le relief : un demi-cylindre creux par cannelure, en carte de normales */
  const c = document.createElement('canvas'); c.width = 64; c.height = 4; const g = c.getContext('2d'); const d = g.createImageData(64, 4);
  for (let x = 0; x < 64; x++) { const u = (x + 0.5) / 64 * 2 - 1, nx = -u * 0.85, nz = Math.sqrt(1 - nx * nx); for (let y = 0; y < 4; y++) { const i = (y * 64 + x) * 4; d.data[i] = (nx * 0.5 + 0.5) * 255; d.data[i + 1] = 128; d.data[i + 2] = nz * 255; d.data[i + 3] = 255; } }
  g.putImageData(d, 0, 0); const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(CANNELURES, 1); return t;
})();
M.cannele = new THREE.MeshStandardMaterial({ map: texCannelure, normalMap: norCannelure, normalScale: new THREE.Vector2(0.9, 0.9), roughness: 0.58 });
M.pierre = new THREE.MeshStandardMaterial({ color: 0xf5f1ea, roughness: 0.22 });   /* le plateau : pierre blanche polie */
/* une forme « stade » (rectangle aux bouts ronds), extrudée vers le haut */
function stade(L, P) { const r = P / 2, s = new THREE.Shape(); s.moveTo(-L / 2 + r, -r); s.lineTo(L / 2 - r, -r); s.absarc(L / 2 - r, 0, r, -Math.PI / 2, Math.PI / 2, false); s.lineTo(-L / 2 + r, r); s.absarc(-L / 2 + r, 0, r, Math.PI / 2, Math.PI * 1.5, false); return s; }
function extruder(forme, haut, segments = 24) { const g = new THREE.ExtrudeGeometry(forme, { depth: haut, bevelEnabled: false, curveSegments: segments }); g.rotateX(-Math.PI / 2); return g; }
{
  /* LE COMPTOIR DE SES IMAGES : bois blond cannelé aux bouts arrondis, socle de laiton en retrait, plateau
     de pierre blanche (`salon-vue-comptoir-arche`, `salon-plan-iso`). (Avant : une boîte cannelée expresso.) */
  const socle = 0.08, haut = cp.hauteur - 0.05 - socle;
  poser(new THREE.Mesh(extruder(stade(cp.longueur - 0.08, cp.profondeur - 0.08), socle), M.laiton), cp.x, 0, cp.z);
  poser(new THREE.Mesh(extruder(stade(cp.longueur, cp.profondeur), haut, 32), M.cannele), cp.x, socle, cp.z);
  poser(new THREE.Mesh(extruder(stade(cp.longueur + 0.14, cp.profondeur + 0.12), 0.05, 32), M.pierre), cp.x, cp.hauteur - 0.05, cp.z);
  poser(new THREE.Mesh(extruder(stade(cp.longueur + 0.02, cp.profondeur + 0.02), 0.012, 32), M.laiton), cp.x, cp.hauteur - 0.062, cp.z);
  spot(cp.x - 1.2, cp.z + 1.2, 1.0, 0.45); spot(cp.x + 1.2, cp.z + 1.2, 1.0, 0.45);
  /* sur le comptoir : la machine, la tablette, une pile de wax (le mètre ruban et le reste : « LA VIE DE L'ATELIER ») */
  const machine = new THREE.Group();
  machine.add(a(boite(0.4, 0.07, 0.18, M.creme), 0, 0.035, 0));
  machine.add(a(boite(0.08, 0.24, 0.14, M.creme), 0.15, 0.17, 0));
  machine.add(a(boite(0.36, 0.08, 0.13, M.creme), 0.0, 0.28, 0));
  machine.add(a(boite(0.04, 0.1, 0.04, M.laiton), -0.15, 0.2, 0));
  const volant = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.03, 24), M.encre); volant.rotation.z = Math.PI / 2; volant.position.set(0.21, 0.24, 0); machine.add(volant);
  poser(machine, cp.x - 1.5, cp.hauteur, cp.z - 0.05, 0.25);
  const tablette = boite(0.26, 0.012, 0.18, M.encre); poser(tablette, cp.x + 1.1, cp.hauteur + 0.006, cp.z + 0.05, -0.3);
  for (let i = 0; i < 4; i++) poser(boite(0.34, 0.035, 0.26, matWax(40 + i, PALETTES_WAX[(i + 2) % 8])), cp.x + 1.7, cp.hauteur + 0.02 + i * 0.036, cp.z - 0.05, i * 0.05);
}
/* LE MUR DU FOND : L'ARCHE AU LOGO de ses images (`salon-vue-comptoir-arche`, `salon-vue-allee`) : une arche de
   bois blond cannelé, une niche blanche rétroéclairée dedans, une ligne de lumière qui en suit le bord, et
   son vrai logo au milieu. Elle cadre Hillary derrière son comptoir. (Avant : un pan de lames de chêne.) */
const matArcheLed = new THREE.MeshBasicMaterial({ color: new THREE.Color(2.3, 1.85, 1.25), toneMapped: false });
const matNiche = new THREE.MeshBasicMaterial({ map: texteCanvas(256, 384, (g, W, Hh) => {
  const gr = g.createRadialGradient(W / 2, Hh * 0.62, W * 0.12, W / 2, Hh * 0.62, Hh * 0.75); gr.addColorStop(0, '#fbf6ee'); gr.addColorStop(0.7, '#f3ebdf'); gr.addColorStop(1, '#ffe7c2'); g.fillStyle = gr; g.fillRect(0, 0, W, Hh); }) });
{
  /* une arche = un rectangle surmonté d'un demi-cercle */
  const arche = (w, hDroit) => { const r = w / 2, s = new THREE.Shape(); s.moveTo(-r, 0); s.lineTo(r, 0); s.lineTo(r, hDroit); s.absarc(0, hDroit, r, 0, Math.PI, false); s.lineTo(-r, 0); return s; };
  const zMur = -LZ;
  const ext = new THREE.ExtrudeGeometry(arche(3.5, 2.15), { depth: 0.07, bevelEnabled: false, curveSegments: 48 });
  poser(new THREE.Mesh(ext, M.cannele), 0, 0, zMur + 0.005);
  const wN = 2.7, hN = 1.95;
  const niche = new THREE.Mesh(new THREE.ShapeGeometry(arche(wN, hN), 48), matNiche);
  /* les UV d'une forme sont en mètres : ramenés entre 0 et 1 pour la texture de la niche */
  { const uv = niche.geometry.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, (uv.getX(i) + wN / 2) / wN, uv.getY(i) / (hN + wN / 2)); }
  poser(niche, 0, 0, zMur + 0.078);
  /* la ligne de lumière qui suit le bord de la niche */
  const chemin = new THREE.CurvePath();
  chemin.add(new THREE.LineCurve3(new THREE.Vector3(-wN / 2, 0.05, 0), new THREE.Vector3(-wN / 2, hN, 0)));
  chemin.add(new THREE.CatmullRomCurve3(new THREE.ArcCurve(0, hN, wN / 2, Math.PI, 0, true).getPoints(48).map(p => new THREE.Vector3(p.x, p.y, 0))));
  chemin.add(new THREE.LineCurve3(new THREE.Vector3(wN / 2, hN, 0), new THREE.Vector3(wN / 2, 0.05, 0)));
  poser(new THREE.Mesh(new THREE.TubeGeometry(chemin, 200, 0.016, 6, false), matArcheLed), 0, 0, zMur + 0.09);
  const lg = plan.logo;
  const halo = new THREE.Mesh(new THREE.PlaneGeometry(lg.largeur * 1.2, lg.largeur * 0.8), new THREE.MeshBasicMaterial({
    map: texteCanvas(256, 160, (g, W, Hh) => { const gr = g.createRadialGradient(W / 2, Hh / 2, 0, W / 2, Hh / 2, W / 2); gr.addColorStop(0, 'rgba(255,248,236,.85)'); gr.addColorStop(1, 'rgba(255,248,236,0)'); g.fillStyle = gr; g.fillRect(0, 0, W, Hh); }),
    transparent: true, depthWrite: false }));
  poser(halo, 0, lg.y, zMur + 0.085);
  const logoMat = new THREE.MeshBasicMaterial({ transparent: true, opacity: 0 });
  const logo = new THREE.Mesh(new THREE.PlaneGeometry(lg.largeur, lg.largeur * 343 / 620), logoMat); poser(logo, 0, lg.y, zMur + 0.095);
  photo('logo.png', (t) => { logoMat.map = t; logoMat.opacity = 1; logoMat.needsUpdate = true; });
  interieurs.push({ maj: (n) => { matNiche.color.setScalar(melanger(1, 0.78, n)); } });
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
/* LE PORTANT DORÉ de ses images (`salon-plan-iso`) : contre la vitrine de droite, une barre de laiton sur deux
   montants, et des coupons de wax suspendus sur des cintres de bois. ⛔ Des TISSUS, jamais des vêtements :
   une robe inventée pendue là passerait pour une pièce de son catalogue. */
{
  const x1 = 4.3, x2 = 6.4, z = fz - 0.95, h = 1.72;
  const portant = new THREE.Group();
  const tube = (lg) => new THREE.CylinderGeometry(0.014, 0.014, lg, 12);
  for (const x of [x1, x2]) {
    portant.add(a(new THREE.Mesh(tube(h), M.laiton), x, h / 2, 0));
    const pied = new THREE.Mesh(tube(0.5), M.laiton); pied.rotation.x = Math.PI / 2; portant.add(a(pied, x, 0.015, 0));
  }
  const barre = new THREE.Mesh(tube(x2 - x1 + 0.04), M.laiton); barre.rotation.z = Math.PI / 2; portant.add(a(barre, (x1 + x2) / 2, h, 0));
  const bois = new THREE.MeshStandardMaterial({ color: 0x8a5a34, roughness: 0.5 });
  const n = 7;
  for (let i = 0; i < n; i++) {
    const x = x1 + 0.22 + i * (x2 - x1 - 0.44) / (n - 1), ry = (i % 2 ? 0.08 : -0.06);
    const crochet = new THREE.Mesh(new THREE.TorusGeometry(0.03, 0.004, 6, 16, Math.PI * 1.4), M.laiton); crochet.position.set(x, h + 0.01, 0); crochet.rotation.set(0, Math.PI / 2, -0.4); portant.add(crochet);
    const cintre = boite(0.42, 0.022, 0.03, bois); cintre.position.set(x, h - 0.06, 0); cintre.rotation.y = Math.PI / 2 + ry; portant.add(cintre);
    /* le coupon : un pan de tissu qui tombe en plis souples (ondulé, plus ample en bas) */
    const geo = new THREE.PlaneGeometry(0.4, 1.0, 12, 10), pos = geo.attributes.position;
    for (let k = 0; k < pos.count; k++) { const u = pos.getX(k), v = pos.getY(k), bas = (0.5 - v); pos.setZ(k, Math.sin(u * 22 + i) * 0.018 * (0.4 + bas * 1.4)); pos.setX(k, u * (1 + bas * 0.12)); }
    geo.computeVertexNormals();
    const pan = new THREE.Mesh(geo, matWax(300 + i, PALETTES_WAX[(i * 3) % 8], [1, 2.4])); pan.material.side = THREE.DoubleSide;
    pan.position.set(x, h - 0.58, 0.004); pan.rotation.y = Math.PI / 2 + ry; portant.add(pan);
  }
  poser(portant, 0, 0, z);
}
/* LA VIE DE L'ATELIER (REALISME.md R9, la densité ; Mongazi, 2026-11-13, et la référence Call of Duty : « aucune
   étagère vide, le désordre vrai ») : des TISSUS et des OUTILS, jamais un vêtement inventé. Sur la table de coupe :
   le rouleau entamé d'où sort le coupon, les bobines, une pile de wax pliés, la craie, des chutes tombées au sol.
   Sur le comptoir : une pile, l'échantillonnier en éventail, le mètre ruban sorti de son boîtier, le coussin à
   épingles, le carnet de croquis fermé et son crayon, la tasse d'Hillary. Au pied du comptoir : les sacs de la
   maison à son logo. Contre le mur des rendez-vous : le panier de rouleaux.
   ⚡ LE COÛT : ~70 petits maillages. Matières PARTAGÉES (8 wax, 3 têtes d'épingle…) et maillages opaques marqués
   `fondre` : `fusionnerDecor()` les réunit par matière (un appel de dessin par matière, pas un par objet). */
{
  const at = plan.atelier;
  /* quatre wax pour tous les objets de vie (quatre appels de dessin), aux palettes 0, 2, 5 et 7 : variées entre elles */
  const wx = (() => { const m = [], pal = [0, 2, 5, 7]; return (k) => (m[k % 4] ??= matWax(500 + (k % 4), PALETTES_WAX[pal[k % 4]])); })();
  const fixe = (o) => { o.traverse((x) => { if (x.isMesh && !x.isInstancedMesh && !x.material.transparent) x.userData.fondre = true; }); return o; };
  const pv = (o, x, y, z, ry = 0) => fixe(poser(o, x, y, z, ry));
  /* la table de coupe est tournée de 0,2 rad : on place dans SON repère (x le long, z en profondeur, +z vers la salle) */
  const RT = 0.2, DESSUS = 0.785;
  const surTable = (lx, lz) => [at.table.x + lx * Math.cos(RT) + lz * Math.sin(RT), at.table.z - lx * Math.sin(RT) + lz * Math.cos(RT)];
  const pile = ([x, z], y0, n, graine, ry = 0) => { for (let i = 0; i < n; i++) pv(boite(0.36 - (i % 2) * 0.02, 0.028, 0.27, wx(graine + i * 3)), x + Math.sin(i * 2.1) * 0.012, y0 + 0.014 + i * 0.029, z + Math.cos(i * 1.7) * 0.01, ry + Math.sin(i) * 0.06); };

  /* — LA TABLE DE COUPE — */
  /* le rouleau ENTAMÉ : le coupon posé sur la table sort de lui (même wax) */
  { const r = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.58, 20), matWax(77, PALETTES_WAX[1], [1, 1])); r.rotation.x = Math.PI / 2;
    const g = new THREE.Group(); g.add(r); const [x, z] = surTable(-0.64, 0.02); pv(g, x, DESSUS + 0.055, z, RT); }
  pile(surTable(0.47, -0.19), DESSUS, 6, 1, RT + 0.08);
  /* le présentoir de bobines (40 bobines, une seule forme : un seul appel de dessin) */
  {
    const rack = new THREE.Group();
    rack.add(a(boite(0.5, 0.36, 0.06, M.chene), 0, 0.18, -0.03));
    const bob = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.016, 0.016, 0.045, 10), new THREE.MeshStandardMaterial({ roughness: 0.55 }), 40);
    const m4 = new THREE.Matrix4(), coul = new THREE.Color(), teintes = [0xe6007e, 0xffffff, 0x141215, 0xd4a017, 0x1f4fa8, 0x2e8b57, 0xc0392b, 0xf2c6d6, 0x8e44ad, 0xe67e22];
    for (let i = 0; i < 40; i++) { m4.makeTranslation(-0.21 + (i % 10) * 0.047, 0.05 + Math.floor(i / 10) * 0.085, 0.02); bob.setMatrixAt(i, m4); bob.setColorAt(i, coul.set(teintes[(i * 7) % 10])); }
    rack.add(bob);
    const [x, z] = surTable(-0.1, -0.3); pv(rack, x, DESSUS, z, RT);
  }
  /* la craie de tailleur, au bord du coupon */
  { const [x, z] = surTable(0.12, 0.2); pv(boite(0.05, 0.007, 0.036, new THREE.MeshStandardMaterial({ color: 0x9fc3e6, roughness: 0.9 })), x, 0.794, z, RT + 0.5); }
  /* des chutes tombées sous la table : des BANDES et des POINTES de wax découpées (une coupe n'est jamais carrée),
     à plat, à moitié sous le plateau */
  [[[-0.15, -0.02], [0.14, -0.035], [0.15, 0.008], [-0.13, 0.026]], [[-0.07, -0.05], [0.09, -0.035], [-0.02, 0.065]], [[-0.11, -0.012], [0.12, -0.006], [0.105, 0.018], [-0.1, 0.02]]]
    .forEach((pts, i) => {
      const forme = new THREE.Shape(pts.map(([x, y]) => new THREE.Vector2(x, y)));
      const geo = new THREE.ShapeGeometry(forme).rotateX(-Math.PI / 2);
      const uv = geo.attributes.uv; for (let j = 0; j < uv.count; j++) uv.setXY(j, uv.getX(j) * 2.5, uv.getY(j) * 2.5);   /* les UV d'une forme sont en mètres */
      const [lx, lz, ry] = [[0.28, 0.42, 0.3], [-0.12, 0.38, 1.9], [0.58, 0.24, -0.6]][i], [x, z] = surTable(lx, lz);
      pv(new THREE.Mesh(geo, wx(i * 3 + 1)), x, 0.003 + i * 0.0008, z, ry);
    });

  /* — LE COMPTOIR — */
  pile([cp.x - 0.75, cp.z - 0.12], cp.hauteur - 0.005, 3, 17, 0.08);
  /* l'échantillonnier : six lames de wax en éventail autour d'un rivet de laiton */
  {
    const ev = new THREE.Group();
    for (let i = 0; i < 6; i++) { const l = new THREE.Group(), b = boite(0.075, 0.003, 0.21, wx(i * 3 + 1)); b.position.set(0, i * 0.0032, -0.09); l.add(b); l.rotation.y = -0.55 + i * 0.22; ev.add(l); }
    ev.add(a(new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.024, 12), M.laiton), 0, 0.01, 0));
    pv(ev, cp.x - 1.02, cp.hauteur + 0.002, cp.z + 0.22, 2.6);
  }
  /* le mètre ruban : son boîtier magenta, et le ruban gradué tiré sur le plateau en courbe douce */
  {
    const m = new THREE.Group();
    const boitier = new THREE.Mesh(new THREE.CylinderGeometry(0.034, 0.034, 0.016, 28), MATIERES.magenta()); boitier.position.y = 0.008; m.add(boitier);
    m.add(a(new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.018, 16), M.laiton), 0, 0.009, 0));
    const grad = texteCanvas(512, 16, (g, W, Hh) => { g.fillStyle = '#efcc3e'; g.fillRect(0, 0, W, Hh); g.fillStyle = '#1b1712';   /* jaune de couturière : visible sur la pierre crème */
      for (let i = 0; i <= 60; i++) { const x = i / 60 * W; g.fillRect(x, 0, 1, i % 10 === 0 ? Hh * 0.7 : i % 5 === 0 ? Hh * 0.5 : Hh * 0.3); } });
    const L = 0.42, geo = new THREE.PlaneGeometry(L, 0.016, 24, 1).rotateX(-Math.PI / 2), p = geo.attributes.position;
    for (let j = 0; j < p.count; j++) { const u = (p.getX(j) + L / 2) / L; p.setZ(j, p.getZ(j) + Math.sin(u * Math.PI * 1.3) * 0.05); p.setY(j, 0.0015); }
    geo.computeVertexNormals();
    m.add(a(new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ map: grad, roughness: 0.6 })), L / 2 + 0.03, 0, 0));
    pv(m, cp.x + 0.42, cp.hauteur, cp.z + 0.12, 0.35);
  }
  /* le coussin à épingles (trois matières pour les neuf têtes) */
  {
    const c = new THREE.Group(), tetes = [0xffd23f, 0xffffff, 0x1f4fa8].map(t => new THREE.MeshStandardMaterial({ color: t, roughness: 0.3 })), tete = new THREE.SphereGeometry(0.006, 6, 4);
    c.add(new THREE.Mesh(new THREE.SphereGeometry(0.05, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2), M.velours));
    for (let i = 0; i < 9; i++) { const e = new THREE.Mesh(tete, tetes[i % 3]); const a1 = i * 2.4, b1 = 0.3 + (i % 3) * 0.3; e.position.set(Math.sin(a1) * Math.sin(b1) * 0.06, Math.cos(b1) * 0.06, Math.cos(a1) * Math.sin(b1) * 0.06); c.add(e); }
    pv(c, cp.x + 0.12, cp.hauteur, cp.z - 0.06);
  }
  /* le carnet de croquis FERMÉ (rien d'inventé dedans) et son crayon */
  {
    const k = new THREE.Group();
    k.add(a(boite(0.21, 0.016, 0.148, M.encre), 0, 0.008, 0));
    k.add(a(boite(0.205, 0.013, 0.004, M.creme), 0.002, 0.008, 0.073));   /* la tranche des pages */
    k.add(a(boite(0.008, 0.0175, 0.15, MATIERES.magenta()), 0.07, 0.008, 0));   /* l'élastique */
    const crayon = new THREE.Mesh(new THREE.CylinderGeometry(0.0038, 0.0038, 0.16, 6), new THREE.MeshStandardMaterial({ color: 0x2b2b2b, roughness: 0.5 }));
    crayon.rotation.z = Math.PI / 2; crayon.position.set(0.01, 0.0195, -0.03); crayon.rotation.y = 0.12; k.add(crayon);
    pv(k, cp.x - 0.32, cp.hauteur, cp.z + 0.16, -0.18);
  }
  /* la tasse d'Hillary, côté atelier du comptoir */
  {
    const t = new THREE.Group();
    t.add(new THREE.Mesh(new THREE.CylinderGeometry(0.068, 0.062, 0.008, 28), M.porcelaine));
    t.add(a(new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.032, 0.07, 24, 1, true), M.porcelaine), 0, 0.043, 0));
    t.add(a(new THREE.Mesh(new THREE.CircleGeometry(0.032, 24).rotateX(-Math.PI / 2), M.porcelaine), 0, 0.009, 0));
    t.add(a(new THREE.Mesh(new THREE.CircleGeometry(0.038, 24).rotateX(-Math.PI / 2), new THREE.MeshStandardMaterial({ color: 0x3b2314, roughness: 0.15 })), 0, 0.066, 0));
    const anse = new THREE.Mesh(new THREE.TorusGeometry(0.018, 0.0045, 8, 16, Math.PI * 1.2), M.porcelaine); anse.position.set(0.043, 0.045, 0); anse.rotation.z = -Math.PI * 0.6; t.add(anse);
    pv(t, cp.x + 1.4, cp.hauteur, cp.z - 0.22, 0.5);
  }
  /* les sacs de la maison, au pied du comptoir : papier magenta, anses noires, son logo */
  {
    const papier = new THREE.MeshStandardMaterial({ color: 0xe6007e, roughness: 0.7 }), anse = new THREE.MeshStandardMaterial({ color: 0x141215, roughness: 0.6 });
    const logoSac = new THREE.MeshBasicMaterial({ transparent: true, opacity: 0, color: 0xffffff });
    photo('logo.png', (tx) => { logoSac.map = tx; logoSac.opacity = 1; logoSac.needsUpdate = true; });
    [[0.32, 0.4, 0.12, 0], [0.26, 0.34, 0.1, 0.35], [0.36, 0.3, 0.14, -0.25]].forEach(([w, h, p, ry], i) => {
      const sac = new THREE.Group();
      sac.add(a(boite(w, h, p, papier), 0, h / 2, 0));
      const t = new THREE.Mesh(new THREE.TorusGeometry(w * 0.22, 0.006, 6, 20, Math.PI), anse); t.position.set(0, h, 0); sac.add(t);
      const l = new THREE.Mesh(new THREE.PlaneGeometry(w * 0.7, w * 0.7 * 343 / 620), logoSac); l.position.set(0, h * 0.55, p / 2 + 0.002); sac.add(l);
      pv(sac, cp.x + cp.longueur / 2 + 0.35 + i * 0.3, 0, cp.z + 0.15 - i * 0.12, ry);
    });
  }

  /* — LE PANIER DE ROULEAUX, contre le mur des rendez-vous : osier tressé, un bord roulé — */
  {
    const tresse = texteCanvas(256, 128, (g, W, Hh) => {
      g.fillStyle = '#6e4f2c'; g.fillRect(0, 0, W, Hh);
      const rang = 16, brin = 32;
      for (let y = 0; y < Hh; y += rang) for (let x = 0; x <= W; x += brin) {
        const dec = ((y / rang) % 2) * brin / 2, gr = g.createLinearGradient(0, y, 0, y + rang);
        gr.addColorStop(0, '#8a6538'); gr.addColorStop(0.45, '#b98d57'); gr.addColorStop(1, '#7a5530');
        g.fillStyle = gr; g.beginPath(); g.roundRect(x + dec - brin / 2 + 2, y + 2, brin - 4, rang - 3, 5); g.fill();
      }
    });
    tresse.wrapS = tresse.wrapT = THREE.RepeatWrapping; tresse.repeat.set(5, 3);
    const osier = new THREE.MeshStandardMaterial({ map: tresse, roughness: 0.88, side: THREE.DoubleSide });
    const panier = new THREE.Group();
    panier.add(a(new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.25, 0.5, 28, 1, true), osier), 0, 0.25, 0));
    panier.add(a(new THREE.Mesh(new THREE.CircleGeometry(0.25, 28).rotateX(-Math.PI / 2), osier), 0, 0.01, 0));
    const bord = new THREE.Mesh(new THREE.TorusGeometry(0.3, 0.018, 8, 40), new THREE.MeshStandardMaterial({ color: 0x8a6538, roughness: 0.85 })); bord.rotation.x = Math.PI / 2; bord.position.y = 0.5; panier.add(bord);
    for (let i = 0; i < 7; i++) {
      const r = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 1.15, 14), wx(i * 5));
      const ang = i / 7 * Math.PI * 2; r.position.set(Math.sin(ang) * 0.13, 0.55, Math.cos(ang) * 0.13); r.rotation.set(Math.cos(ang) * 0.18, 0, -Math.sin(ang) * 0.18); panier.add(r);
    }
    pv(panier, -7.45, 0, 0.35);
  }
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
const AVANCE_INTRO = new THREE.Vector3(0, -0.25, 5.4);
const deplacement = creerDeplacement(moteur, graphe, { depart: params.has('direct') ? 'entree' : 'dehors', calque });
/* on arrive dehors FACE à la boutique et à son enseigne, pas face à la rue */
if (!params.has('direct')) deplacement.tournerVers(new THREE.Vector3(0, 2.9, plan.facade.z));   /* l'enseigne dans le tiers haut */
/* L'OUVERTURE CINÉMA (audit jeu vidéo, point 1) : au chargement, la caméra part du milieu de la rue
   et avance lentement jusqu'au trottoir, le regard qui descend de l'enseigne vers la porte ; au
   toucher d'« Entrer », elle accélère, les portes coulissent, on entre. Elle s'efface devant
   « réduire les animations » et devant ?direct. La caméra est reprise APRÈS le déplacement à chaque
   image, puis rendue exactement à la pose qu'il attend : aucun saut. */
const intro = (!params.has('direct') && !matchMedia('(prefers-reduced-motion: reduce)').matches) ? { t: 0, dur: 7.5, vite: false, fini: false, surFin: null } : null;
/* P9 (référence) : les bandes de cinéma, À LA SEULE OUVERTURE, retirées d'un coup quand la main revient au visiteur
   (jamais pendant une conversation : `verre.css` les y cache) */
const bandesIntro = intro ? (() => { const b = document.createElement('div'); b.className = 'bandes-intro'; b.setAttribute('aria-hidden', 'true'); b.innerHTML = '<i></i><i></i>'; calque.appendChild(b); return b; })() : null;
if (intro) {
  const deb = new THREE.Vector3(), fin = new THREE.Vector3(), qDeb = new THREE.Quaternion(), qFin = new THREE.Quaternion();
  const vise = new THREE.Matrix4(), haut = new THREE.Vector3(0, 1, 0), enseigne = new THREE.Vector3(0, 3.6, plan.facade.z);
  const finIntro = moteur.chaqueImage((dt) => {
    if (!btEntrer.disabled || intro.vite) intro.t += dt * (intro.vite ? 4 : 1);   /* il attend que le salon soit chargé */
    const k = Math.min(1, intro.t / intro.dur), e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
    fin.copy(camera.position); qFin.copy(camera.quaternion);
    deb.copy(fin).add(AVANCE_INTRO);
    qDeb.setFromRotationMatrix(vise.lookAt(deb, enseigne, haut));
    camera.position.lerpVectors(deb, fin, e);
    camera.quaternion.slerpQuaternions(qDeb, qFin, e);
    if (k >= 1) { finIntro(); intro.fini = true; if (bandesIntro) bandesIntro.remove(); if (intro.surFin) intro.surFin(); }
  });
}
function deplacementPlus(objet, cible) { (window.__enAttente = window.__enAttente || []).push([objet, cible]); }
for (const [o, c] of window.__enAttente || []) deplacement.ajouterInteractif(o, c);
for (const id in totems) deplacement.ajouterInteractif(totems[id], { type: 'piece', id });

const faisceauxCreations = [];
/* LA CHORÉGRAPHIE DE LUMIÈRE (audit jeu vidéo, point 1) : à l'entrée, les projecteurs s'allument
   un à un sur les créations, en 0,8 s chacun, à 0,35 s d'écart */
let faisceauxAllumes = params.has('direct');   /* en direct, ils sont allumés d'emblée */
function allumerFaisceaux() {
  if (faisceauxAllumes) return; faisceauxAllumes = true;
  let t = 0;
  const fin = moteur.chaqueImage((dt) => {
    t += dt; let tous = true;
    faisceauxCreations.forEach((f, i) => { const k = Math.min(1, Math.max(0, (t - i * 0.35) / 0.8)); f.l.intensity = f.base * k * k * (3 - 2 * k); if (k < 1) tous = false; });
    if (tous) fin();
  });
}
/* LA LUMIÈRE TAMISÉE (Mongazi, 2026-11-12 : « ça doit être tamisé et ultra stylé… les lumières
   exceptionnelles et luxueuses ») : la pièce baisse, et chaque création exposée reçoit SON
   faisceau chaud, comme une maison de couture le soir. Le nombre de faisceaux suit la qualité
   (chacun coûte sur un téléphone). Aucune ombre portée : trop chère, et la flaque peinte au sol
   suffit à poser la lumière. */
{
  const nb = q.nom === 'haute' ? 7 : q.nom === 'moyenne' ? 4 : 2;
  /* sans « direct », ils attendent dans le noir que le visiteur entre (chorégraphie) */
  const exposees = Object.keys(totems).filter(id => totems[id].position.y < 1).slice(0, nb);
  const centre = new THREE.Vector3(0, 0, 0), p = new THREE.Vector3();
  for (const id of exposees) {
    totems[id].getWorldPosition(p);
    const versCentre = centre.clone().sub(p).setY(0).normalize();
    const faisceau = new THREE.SpotLight(0xffcf96, 34, 7.5, 0.36, 0.8, 2);
    faisceau.position.set(p.x + versCentre.x * 1.1, H - 0.25, p.z + versCentre.z * 1.1);
    faisceau.target.position.set(p.x, 1.05, p.z);
    scene.add(faisceau, faisceau.target);
    faisceauxCreations.push({ l: faisceau, base: faisceau.intensity });
    if (!params.has('direct')) faisceau.intensity = 0;
  }
}

const son = creerSon();
deplacement.surPas.push(() => son.pas());
/* P27 : au tonnerre, toutes tournent la tête vers la vitrine, et la plus proche le dit */
const TONNERRE = { maman: 'Eh ! Ça va tomber fort.', afi: 'La pluie de Cotonou… Ça m\'avait manqué.', senami: 'Waouh, tu as entendu ?' };
ciel.surEclair.push(() => { const d = 0.8 + Math.random() * 2.5; son.tonnerre(d); setTimeout(() => pnj.reagir(new THREE.Vector3(0, 1.9, fz + 2.5), { lignes: TONNERRE }), d * 1000 + 350); });

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
    placeDepart: 'voir_g1', gouts: { photo: 2.5, telephone: 2, assis: 1.6, regarder: 1, toucher: 0.8, comptoir: 0.6, fenetre: 0.6 }, goutsPlaces: { fauteuil_1: 2, fauteuil_2: 2, voir_d1: 1.5, voir_g1: 1.5 } },
  { id: 'maman', perso: creerPersonnage({ nom: 'Maman Sènami', age: 47, peau: 0x4a2f22, haut: { wax: 11, palette: PALETTES_WAX[2] }, bas: { type: 'boubou', wax: 11, palette: PALETTES_WAX[2] }, amples: true, manchesLongues: true, coiffe: 'gele', boucles: true, sac: 0x7a1f2b, taille: 1.62 }),
    /* pour l'accroche : à 1,1 m de Sènami, côte à côte VUES DE L'ENTRÉE (l'une derrière l'autre, on ne voyait qu'un dos) */
    placeDepart: { id: 'accroche', x: -1.45, z: 1.75, cap: 140, activite: 'regarder' }, gouts: { toucher: 2.2, regarder: 1.6, assis: 1.2, comptoir: 1, telephone: 0.4, photo: 0.2, fenetre: 0.8 }, goutsPlaces: { tissus_g: 2.5, voir_heros: 1.5, affiches: 1.3 } },
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
objectifEl.addEventListener('click', (e) => { e.stopPropagation(); objectifEl.classList.toggle('replie'); });
const monde = {
  objectif(texte, sous = null, fini = false) {
    /* replié, l'objectif ne garde que son titre court (ce qui précède les deux-points) */
    const [court, ...reste] = String(texte).split(' : ');
    objectifEl.innerHTML = `<small>${fini ? 'Terminé' : 'En cours'}</small><span class="obj-court">${court}</span>${reste.length ? `<span class="obj-suite"> : ${reste.join(' : ')}</span>` : ''}${sous ? `<span class="obj-sous">${sous}</span>` : ''}`;
    objectifEl.classList.add('visible'); objectifEl.classList.toggle('fini', fini); objectifEl.classList.remove('replie');
    /* il se replie en UNE ligne au bout de 6 s, et se rouvre au toucher : rien ne doit occuper
       l'écran (Mongazi, 2026-11-12) */
    clearTimeout(objectifEl._replier); objectifEl._replier = setTimeout(() => objectifEl.classList.add('replie'), 6000);
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
/* au comptoir, personne ne se tient entre le visiteur et Hillary (trois visiteuses alignées devant elle, 2026-11-13) */
pnj.reglages.foyer = () => (Math.hypot(camera.position.x - hillary.racine.position.x, camera.position.z - hillary.racine.position.z) < 3.8 ? hillary.racine.position : null);
/* l'oreille suit la caméra ; la porte s'ouvre et se referme quand on la passe */
moteur.chaqueImage(() => son.ecouteur(camera));
deplacement.surDepart.push((id) => { if (id === 'dehors' || deplacement.noeud === 'dehors') setTimeout(() => son.porte(new THREE.Vector3(0, 1.3, fz)), 350); });

/* ---------- les repères au pouce, sur tout ce qui se touche ---------- */
/* trois noms au plus sur un téléphone, quatre sur un écran : au-delà, les étiquettes
   s'empilaient sur les pièces (Mongazi, 2026-11-12 : « c'est tout brouillon ») */
/* MOINS D'INTERFACE (Mongazi, 2026-11-13, et la référence Call of Duty : « une interface presque absente ») : un seul
   nom à la fois, le plus proche ; les autres repères restent des points ; rien au-delà de 6 m. (Avant : 3 ou 4 noms, 9 m.) */
const reperes = creerReperes({ moteur, calque, maxNoms: 1, distanceMax: 6 });
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
  faire: () => deplacement.allerA(deplacement.noeud === 'dehors' ? 'entree' : 'dehors'),
  /* pas de point « Entrer » ni « Sortir » au-dessus de la tête quand on franchit la porte */
  si: () => Math.hypot(camera.position.x, camera.position.z - fz) > 2.6 });

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
    invite.innerHTML = `<i aria-hidden="true"></i>${i.t}`;
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
      { t: 'Parler', principal: true, faire: () => dialogue.ouvrir('hillary') },
      boutique.panier().length ? { t: 'Valider ma commande', faire: () => dialogue.ouvrir('h_cest_tout') } : { t: 'Me conseiller', faire: () => dialogue.ouvrir('h_conseil') },
      { t: 'Laisser', faire: () => {} },
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
  /* ⚠️ à l'arrivée, on vise sa tête LÀ OÙ ELLE EST (elle a pu bouger pendant le trajet) : viser l'endroit du toucher
     laissait parfois la caméra de dos (QC du 2026-11-14) */
  deplacement.allerPres(new THREE.Vector3(p.x, p.y - 0.1, p.z), { distance: 1.3, puis: () => { deplacement.tournerVers(n.perso.positionTete(new THREE.Vector3()).add(new THREE.Vector3(0, -0.1, 0))); setTimeout(() => {
    options.ouvrir({
      titre: n.connue ? n.nom : 'Une visiteuse', sous: n.connue ? '' : 'Vous ne vous connaissez pas encore',
      ancre: (v) => n.perso.positionTete(v).add(new THREE.Vector3(0, -0.55, 0)),
      choix: [
        { t: 'Parler', principal: true, faire: () => pnj.parler(id, id) },
        { t: 'Saluer', faire: () => { n.perso.geste('saluer'); setTimeout(() => n.perso.geste('repos'), 1700); dialogue.sousTitre(id, SALUTS[id][Math.floor(Math.random() * 2)]); setTimeout(() => pnj.relacher(id), 2600); } },
        { t: 'Laisser', faire: () => pnj.relacher(id) },
      ],
      auFermer: () => pnj.relacher(id),
    });
  }, 550); } });
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
let afiPrete = false, afiPreteA = 0;
/* l'accroche : Afi vient dans les premières secondes, dès qu'on est entré (référence : la course
   est confiée avant la 10e seconde) */
deplacement.surArrivee.push((id) => { if (id !== 'dehors') { if (!afiPrete) afiPreteA = moteur.temps(); afiPrete = true; allumerFaisceaux(); } son.sortir(id === 'dehors'); });
deplacement.surDepart.push(() => son.sortir(false));
/* P47 (référence) : on entre AU MILIEU d'une scène : Sènami filme sa mère, près de l'entrée (Afi vient ensuite, à 9 s) */
let accrocheFaite = false;
/* les conversations n'attendent personne dehors : elles commencent quand on entre, par celle-ci */
if (!params.has('direct')) pnj.reglages.conversations = false;
const accroche = () => {
  pnj.reglages.conversations = true;
  if (accrocheFaite || dialogue.actif) return;
  accrocheFaite = !!pnj.lancer('accroche');
  if (!accrocheFaite) { pnj.liberer('senami'); pnj.liberer('maman'); return; }
  /* pendant la scène, rien d'autre à l'écran (référence) : les noms des lieux se taisent jusqu'à sa fin */
  document.body.classList.add('scene-en-cours');
  const debut = moteur.temps(), fin = setInterval(() => { if (!pnj.conversation || moteur.temps() - debut > 16) { document.body.classList.remove('scene-en-cours'); clearInterval(fin); } }, 500);
  /* P6 (référence : le regard guidé vers ce qui compte) : on entend « Maman, souris ! », on tourne la tête vers elles */
  setTimeout(() => {
    if (dialogue.actif || deplacement.enMarche) return;
    const a = pnj.parId.senami.perso.positionTete(new THREE.Vector3()), b = pnj.parId.maman.perso.positionTete(new THREE.Vector3());
    deplacement.tournerVers(a.add(b).multiplyScalar(0.5).add(new THREE.Vector3(0, -0.25, 0)));
  }, 450);
};
deplacement.surArrivee.push((id) => { if (id !== 'dehors') setTimeout(accroche, 250); });
if (params.has('direct')) setTimeout(accroche, 1500);
/* P27 : une pièce entre dans le sac : celles qui sont près lèvent les yeux, la plus proche approuve (on donne envie) */
const COMPLIMENTS = { afi: 'Bon choix !', senami: 'Oh, elle est belle, celle-là !', maman: 'Ça va bien t\'aller, ça.' };
let tailleSac = boutique.panier().length;

/* P14 (référence : les écrans du lieu vivent) : LA TABLETTE DU COMPTOIR EST ALLUMÉE, sur un pied, tournée vers le
   client, et elle montre TON SAC (nombre de pièces et total tirés du sac, jamais inventés). Dessinée : 0 Ko. */
const peindreTablette = (() => {
  const c = document.createElement('canvas'); c.width = 320; c.height = 220; const g = c.getContext('2d');
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
  const pied = new THREE.Group();
  pied.add(a(boite(0.03, 0.08, 0.03, M.laiton), 0, 0.04, -0.02));
  const ecran = new THREE.Group(); ecran.position.set(0, 0.1, 0); ecran.rotation.x = -0.62;
  ecran.add(boite(0.25, 0.172, 0.009, M.encre));
  ecran.add(a(new THREE.Mesh(new THREE.PlaneGeometry(0.236, 0.158), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false, color: new THREE.Color(0.92, 0.92, 0.92) })), 0, 0, 0.0047));
  pied.add(ecran);
  poser(pied, cp.x + 1.1, cp.hauteur + 0.012, cp.z + 0.05, -0.3);
  const fmt = (n) => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  return () => {
    const T = boutique.totaux();
    g.fillStyle = '#121014'; g.fillRect(0, 0, 320, 220);
    g.fillStyle = '#e6007e'; g.fillRect(0, 214, 320, 6);
    g.textAlign = 'center'; g.fillStyle = '#e6007e'; g.font = '600 15px Archivo, sans-serif'; g.fillText('HILLARY M. STYL', 160, 34);
    g.fillStyle = '#f4efe6'; g.font = '500 34px "Bodoni Moda", Georgia, serif'; g.fillText('Votre sac', 160, 92);
    if (!T.articles) { g.fillStyle = 'rgba(244,239,230,.6)'; g.font = '400 18px Archivo, sans-serif'; g.fillText('vide pour l\'instant', 160, 134); }
    else {
      g.fillStyle = '#f4efe6'; g.font = '500 20px Archivo, sans-serif'; g.fillText(`${T.articles} pièce${T.articles > 1 ? 's' : ''}`, 160, 132);
      g.fillStyle = '#d9b26a'; g.font = '600 28px Archivo, sans-serif'; g.fillText(T.fcfa ? `${fmt(T.fcfa)} F${T.devis ? ' + devis' : ''}` : 'sur devis', 160, 176);
    }
    tex.needsUpdate = true;
  };
})();
peindreTablette(); boutique.surChange.push(peindreTablette);

/* P17 (référence : le désordre vrai ; Cotonou, il fait chaud) : UN VENTILATEUR SUR PIED dans l'atelier, qui tourne et
   balaie lentement de gauche à droite. Il bouge : il n'est ni fondu ni figé avec le décor. */
{
  const v = new THREE.Group(), blanc = new THREE.MeshStandardMaterial({ color: 0xece8e1, roughness: 0.45 });
  v.add(a(new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.22, 0.03, 28), blanc), 0, 0.015, 0));
  v.add(a(new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.014, 1.08, 10), M.laiton), 0, 0.55, 0));
  const tete = new THREE.Group(); tete.position.y = 1.12; v.add(tete);
  tete.add(a(new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.07, 0.14, 18).rotateX(Math.PI / 2), blanc), 0, 0, -0.07));
  const grille = texteCanvas(256, 256, (g2, W) => {
    g2.clearRect(0, 0, W, W); g2.strokeStyle = '#d8d3cb'; g2.lineWidth = 3;
    for (let r = 20; r < 126; r += 21) { g2.beginPath(); g2.arc(W / 2, W / 2, r, 0, 7); g2.stroke(); }
    for (let k = 0; k < 24; k++) { const an = k / 24 * Math.PI * 2; g2.beginPath(); g2.moveTo(W / 2 + Math.cos(an) * 18, W / 2 + Math.sin(an) * 18); g2.lineTo(W / 2 + Math.cos(an) * 125, W / 2 + Math.sin(an) * 125); g2.stroke(); }
    g2.fillStyle = '#d8d3cb'; g2.beginPath(); g2.arc(W / 2, W / 2, 18, 0, 7); g2.fill();
  });
  const matGrille = new THREE.MeshStandardMaterial({ map: grille, transparent: true, alphaTest: 0.4, side: THREE.DoubleSide, roughness: 0.5 });
  for (const z of [0.045, -0.035]) tete.add(a(new THREE.Mesh(new THREE.CircleGeometry(0.24, 40), matGrille), 0, 0, z));
  tete.add(a(new THREE.Mesh(new THREE.TorusGeometry(0.24, 0.008, 6, 48), blanc), 0, 0, 0.005));
  const helice = new THREE.Group(); helice.position.z = 0.005; tete.add(helice);
  const pale = new THREE.MeshStandardMaterial({ color: 0xbfd6e6, roughness: 0.3, transparent: true, opacity: 0.85 });
  for (let k = 0; k < 3; k++) { const p = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 8), pale); p.scale.set(0.055, 0.2, 0.01); p.position.set(Math.sin(k * 2.094) * 0.11, Math.cos(k * 2.094) * 0.11, 0); p.rotation.z = -k * 2.094; helice.add(p); }
  v.position.set(-7.25, 0, -4.85); v.rotation.y = Math.PI / 2 - 0.15; v.name = 'ventilateur'; scene.add(v);
  moteur.chaqueImage((dt, temps) => { helice.rotation.z -= dt * 11; tete.rotation.y = Math.sin(temps * 0.35) * 0.6; });
}

/* P18 (référence : le texte du lieu, partout) : « ESSAYAGE » au-dessus du rideau de la cabine, plaque d'encre filetée de
   laiton comme les affiches. Un mot vrai : la cabine est là. */
{
  const cb = plan.cabine, l = 0.86, h = 0.2;
  const plaque = texteCanvas(512, 120, (g2, W, Hh) => {
    g2.fillStyle = '#141215'; g2.fillRect(0, 0, W, Hh); g2.strokeStyle = '#c9a254'; g2.lineWidth = 4; g2.strokeRect(8, 8, W - 16, Hh - 16);
    g2.fillStyle = '#e6c88a'; g2.textAlign = 'center'; g2.textBaseline = 'middle'; g2.font = '500 54px "Bodoni Moda", Georgia, serif';
    if ('letterSpacing' in g2) g2.letterSpacing = '10px';
    g2.fillText('ESSAYAGE', W / 2 + 5, Hh / 2 + 3);
  });
  poser(new THREE.Mesh(new THREE.PlaneGeometry(l, h), new THREE.MeshStandardMaterial({ map: plaque, roughness: 0.4, emissive: 0x231d12 })), (cb.x1 + cb.x2) / 2, 2.86, cb.z2 + 0.03);
}
boutique.surChange.push(() => { const n = boutique.panier().length; if (n > tailleSac) pnj.reagir(() => camera.position.clone(), { rayon: 6, duree: 1.8, lignes: COMPLIMENTS }); tailleSac = n; });
moteur.chaqueImage((dt, t) => {
  /* elle n'aborde pas quelqu'un qui commande au comptoir, ni quelqu'un sur le trottoir */
  /* elle laisse d'abord la lumière s'allumer : 5 s après l'arrivée dans le salon (l'ouverture cinéma) */
  if (ctx.quete === 0 && afiPrete && t > 7 && t > afiPreteA + 9 && !dialogue.actif && !['comptoir', 'dehors'].includes(deplacement.noeud) && !document.body.classList.contains('en-fiche') && !document.body.classList.contains('en-cadran')) {
    if (pnj.aborder('afi', 'afi_course')) ctx.quete = -1;   /* -1 : en route vers le joueur */
  }
});
dialogue.surFermeture.push(() => {
  if (ctx.quete === -1) ctx.quete = 0;
  if (ctx.quete > 0) pnj.annulerAbordage();   /* la course est acceptée : plus de raison de revenir */
  afiPrete = false; setTimeout(() => { afiPrete = ctx.quete === 0; }, 25000);
});

let cielHemi = null; scene.traverse(o => { if (o.isHemisphereLight) cielHemi = o; });
/* LA LUMIÈRE DE FACE DES CONVERSATIONS (audit jeu vidéo, vague 3) : comme au cinéma, une lumière douce
   portée par la caméra éclaire le visage de celle qui parle, puis s'efface quand la conversation finit */
const lumiereFace = new THREE.SpotLight(0xfff0dd, 0, 6, 0.55, 1, 2);
scene.add(lumiereFace, lumiereFace.target);
const decalFace = new THREE.Vector3();
moteur.chaqueImage((dt) => {
  const orateur = dialogue.actif ? Object.values(personnes).find(p => p.perso && p.perso.st && p.perso.st.parle) : null;
  const vise = orateur ? 2.4 : 0;   /* douce : à 7, le manteau d'Afi brûlait en blanc (capture du 2026-11-13) */
  lumiereFace.intensity += (vise - lumiereFace.intensity) * (1 - Math.exp(-dt * 3));
  if (lumiereFace.intensity < 0.01) return;
  decalFace.set(0.35, 0.25, 0).applyQuaternion(camera.quaternion);
  lumiereFace.position.copy(camera.position).add(decalFace);
  if (orateur) orateur.perso.positionTete(lumiereFace.target.position);
});

/* ---------- la nuit, la pluie, à l'intérieur ---------- */
/* P11 (référence) : L'ŒIL QUI S'HABITUE en passant la porte. Entrer dans plus sombre que d'où l'on vient (le salon
   de jour, la rue la nuit) commence sombre et s'éclaircit ; entrer dans plus clair commence ébloui. 1,5 s environ. */
let oeil = 1, dedansAvant = null;
moteur.chaqueImage((dt) => {
  const e = ciel.etat;
  const dedans = camera.position.z < fz;
  if (dedansAvant !== null && dedans !== dedansAvant) oeil = dedans ? melanger(0.72, 1.22, e.nuit) : melanger(1.3, 0.68, e.nuit);
  dedansAvant = dedans;
  oeil += (1 - oeil) * (1 - Math.exp(-Math.min(dt, 0.1) * 1.5));   /* 90 % du chemin en 1,5 s */
  for (const i of interieurs) i.maj(e.nuit, e.pluie);
  /* LE JOUR DE SES IMAGES, LE SOIR TAMISÉ (2026-11-13) : de jour, la pièce est claire et la lumière du ciel
     entre par la vitrine ; le soir, elle baisse et se réchauffe. (Avant : tamisée jour et nuit.) */
  moteur.renderer.toneMappingExposure = melanger(1.04, 0.84, e.nuit) * (1 - e.pluie * 0.06) * oeil;
  scene.environmentIntensity = melanger(0.5, 0.15, e.nuit);
  if (cielHemi) cielHemi.intensity *= melanger(0.75, 0.42, e.nuit);
  ciel3d.uniforms.haut.value.copy(CIEL.jourH).lerp(CIEL.nuitH, e.nuit); ciel3d.uniforms.horizon.value.copy(CIEL.jourB).lerp(CIEL.nuitB, e.nuit);
  for (const f of fenetresImmeuble) f.emissiveIntensity = 1.4 * e.nuit;
  enduitImmeuble.emissive.setRGB(0.2, 0.17, 0.14).multiplyScalar(Math.max(0, 1 - e.nuit) * (1 - e.pluie * 0.4));
  moteur.reglerHalo(melanger(0.22, 0.42, e.nuit), melanger(1.7, 1.15, e.nuit));   /* seules les lampes, la gorge et les néons rayonnent */
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
  /* le jazz lounge du salon (Pixabay, AtlasAudio, « Lounge ») : il commence dès « Entrer ».
     ⚠️ Appelé DANS le geste (pas dans un délai) : sur iPhone, la lecture n'est permise que là. */
  son.musique('musique/salon-lounge.mp3', 0.3);
  setTimeout(carteDeTitre, 900);
  setTimeout(() => son.machineACoudre(new THREE.Vector3(plan.atelier.table.x, 0.9, plan.atelier.table.z)), 1500);
  ouverture.classList.add('partie');
  setTimeout(() => ouverture.remove(), 2200);
  const avancer = () => { ouvrirPortes(); setTimeout(() => deplacement.allerA('entree'), 450); };
  if (deplacement.noeud === 'dehors') { if (intro && !intro.fini) { intro.vite = true; intro.surFin = avancer; } else setTimeout(avancer, 300); }
  else allumerFaisceaux();
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
  const mapSol = M.sol.map;
  await Promise.all([
    /* LE SOL DE SES IMAGES : crème poli, presque uni, de grandes dalles ; du marbre scanné on garde le relief
       et la rugosité (le poli inégal d'une vraie pierre), pas ses veines beiges (avant : un marbre beige) */
    R.matiere(M.sol, 'marble_01', { repeat: [8, 6], relief: 0.18 }).then(() => { M.sol.map = mapSol; M.sol.color.set(0xffffff); M.sol.roughness = 0.2; M.sol.needsUpdate = true; }),
    R.matiere(M.platre, 'painted_plaster_wall', { repeat: [5, 2], teinte: 0xf4ede3, relief: 0.35 }).then(() => { M.platre.map = null; M.platre.color.set(MUR); M.platre.needsUpdate = true; }),   /* le relief du plâtre, pas son gris : sa référence a des murs crème lisses */
    /* le chêne BLOND de ses étagères : le placage scanné, éclairci (une couleur au-delà de 1 éclaircit) */
    R.matiere(M.chene, 'oak_veneer_01', { repeat: [1, 2] }).then(() => { M.chene.color.setRGB(1.55, 1.38, 1.18); }),
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
  await appliquerCuisson().catch(e => console.warn('lumière cuite non appliquée', e));
  try { poserRefletSol(); } catch (e) { console.warn('reflet du sol non posé', e); }
  await fusionnerDecor().catch(e => console.warn('décor non fusionné', e));
}

/* R14 · MOINS D'APPELS DE DESSIN (Mongazi, 2026-11-13 : « le maximum d'images/s possible ») : le décor fixe CUIT
   était dessiné pièce par pièce (205 maillages sur 232 appels par image, mesuré dans Chrome). Une fois la lumière
   cuite posée, on fond toutes les pièces qui partagent la même matière en UN seul maillage. Les originaux restent,
   CACHÉS : les rayons du toucher les trouvent encore (three.js ne regarde pas `visible` en lançant un rayon), et la
   matière partagée garde le jour et la nuit. Exclus : ce qui bouge (les portes), les personnages, ce qui n'est pas
   cuit. `?sans-fusion` pour comparer. */
const fusionDecor = { avant: 0, apres: 0 };
async function fusionnerDecor() {
  if (params.has('sans-fusion')) return;
  const { mergeGeometries } = await import('three/addons/utils/BufferGeometryUtils.js');
  scene.updateMatrixWorld(true);
  const exclus = PERSONNAGES(), bouge = new Set(vantaux.flatMap(v => [v.verre, v.poignee]));
  const groupes = new Map();
  scene.traverse((o) => {
    if (!o.isMesh || o.isSkinnedMesh || o.isInstancedMesh || o.name === 'fusion' || bouge.has(o) || !vraimentVisible(o) || dansPersonnage(o, exclus)) return;
    const m = o.material;
    if (!m || Array.isArray(m) || !(m.lightMap || o.userData.fondre)) return;   /* le décor fixe à lumière cuite, et les objets de vie (`fondre`) */
    const g = o.geometry, sig = Object.keys(g.attributes).sort().join(',') + (g.index ? '|i' : '');
    const cle = m.uuid + '|' + sig;
    if (!groupes.has(cle)) groupes.set(cle, { m, liste: [] });
    groupes.get(cle).liste.push(o);
  });
  /* LES OBJETS DE VIE UNIS (sans texture) : réunis en UN seul maillage, leur couleur portée par les sommets ; la
     tasse, le crayon, la craie, les épingles… ne coûtent plus un appel de dessin chacun (30 → 1). Le laiton y perd
     son reflet métallique : invisible à cette taille. */
  {
    const unis = [], mUni = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.5 });
    for (const [k, gr] of [...groupes]) if (!gr.m.map && !gr.m.lightMap && gr.liste.every(o => o.userData.fondre)) { unis.push(...gr.liste); groupes.delete(k); }
    const geos = unis.map((o) => {
      const g = (o.geometry.index ? o.geometry.toNonIndexed() : o.geometry.clone()); g.morphAttributes = {};
      for (const n of Object.keys(g.attributes)) if (n !== 'position' && n !== 'normal') g.deleteAttribute(n);
      g.applyMatrix4(o.matrixWorld);
      const c = o.material.color, n = g.attributes.position.count, col = new Float32Array(n * 3);
      for (let i = 0; i < n; i++) { col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b; }
      g.setAttribute('color', new THREE.BufferAttribute(col, 3)); return g;
    });
    const fus = geos.length > 1 ? mergeGeometries(geos, false) : null;
    geos.forEach(g => g.dispose());
    if (fus) {
      const mesh = new THREE.Mesh(fus, mUni); mesh.name = 'fusion'; mesh.matrixAutoUpdate = false; mesh.updateMatrix(); scene.add(mesh);
      for (const o of unis) o.visible = false;
      fusionDecor.avant += unis.length; fusionDecor.apres++; fusionDecor.unis = unis.length;
    }
  }
  for (const { m, liste } of groupes.values()) {
    if (liste.length < 2) continue;
    const geos = liste.map((o) => { const g = o.geometry.clone(); g.morphAttributes = {}; g.applyMatrix4(o.matrixWorld); return g; });
    const fus = mergeGeometries(geos, false);
    geos.forEach(g => g.dispose());
    if (!fus) continue;
    const mesh = new THREE.Mesh(fus, m); mesh.name = 'fusion'; mesh.matrixAutoUpdate = false; mesh.updateMatrix(); scene.add(mesh);
    for (const o of liste) o.visible = false;
    fusionDecor.avant += liste.length; fusionDecor.apres++;
  }
  /* LE DÉCOR FIGÉ : three.js recalcule à CHAQUE image la matrice de chaque objet de la scène (≈ 900 ici), même
     immobile ; le décor posé (`decor-N`) et les objets scannés ne bougent jamais, on les fige une fois pour
     toutes. Restent libres : les portes, les personnages, la caméra du reflet, la lumière de face, la rue. */
  scene.updateMatrixWorld(true);
  for (const o of scene.children) {
    const fixe = (o.name.startsWith('decor-') || (o.userData && o.userData.scan) || o.name === 'fusion') && !bouge.has(o) && !exclus.has(o);
    if (fixe) o.traverse((x) => { if (!bouge.has(x)) { x.matrixAutoUpdate = false; fusionDecor.figes = (fusionDecor.figes || 0) + 1; } });
  }
}
setTimeout(() => embellir().catch(e => console.warn('embellissement incomplet', e)), params.has('direct') ? 200 : 2500);

/* AFI, LE PREMIER VRAI PERSONNAGE (TRELLIS.2 puis Mixamo, 2026-11-12) : son corps et ses
   sept animations arrivent après l'ouverture ; d'ici là, et si le chargement échoue, sa
   silhouette tient sa place. Sènami et Maman Sènami suivront le même chemin. */
/* 2026-11-13 : LA NOUVELLE AFI (29 ans, image de Mongazi, TRELLIS.2, squelette Mixamo `afi29`) et SÈNAMI (21 ans ;
   Mixamo refusait ses tresses, elle a reçu le squelette d'Afi par `_outils/transferer_squelette.py`). Les douze
   gestes viennent des fichiers d'Afi (`gestes`) : un seul fichier par personnage. Repli : l'ancienne Afi. */
const GESTES_AFI = { dossier: 'personnages/afi/', prefixe: 'afi' };
const pasAssise = (id) => () => { const v = visiteuses.find(x => x.id === id); if (v) v.gouts.assis = 0; };   /* pas encore d'animation assise */
setTimeout(() => habiller(personnes.afi.perso, { dossier: 'personnages/afi/', prefixe: 'afi29', taille: 1.71, gestes: GESTES_AFI, texture: 'personnages/afi/afi29-peau.jpg' })
  .catch(() => habiller(personnes.afi.perso, { dossier: 'personnages/afi/', prefixe: 'afi', taille: 1.71 }))
  .then(pasAssise('afi'))
  .catch(e => console.warn('Afi reste en silhouette', e)), params.has('direct') ? 600 : 3200);
setTimeout(() => habiller(personnes.senami.perso, { dossier: 'personnages/senami/', prefixe: 'senami', taille: 1.64, gestes: GESTES_AFI, texture: 'personnages/senami/senami-peau.jpg' })
  .then(pasAssise('senami'))
  .catch(e => console.warn('Sènami reste en silhouette', e)), params.has('direct') ? 900 : 3600);


/* LA CLÉ DE CUISSON : un nom STABLE pour chaque maillage du décor, le même à chaque chargement et à
   chaque qualité. ⚠️ Les numéros « decor-N » dépendent de l'ordre de construction, qui change avec la
   qualité (le nombre de faisceaux, le miroir du sol) ; et le sol, le plafond ou les objets scannés n'en
   avaient même pas : ils manquaient à l'export du 2026-11-12. La clé = la signature de l'objet de premier
   niveau (sa forme, sa position au centimètre, son orientation) + le chemin jusqu'au maillage. */
/* ⚠️ Blender tronque les noms à 63 caractères : la clé voyage sous forme d'empreinte (FNV-1a, 32 bits) */
function empreinte(t) { let h = 0x811c9dc5; for (let i = 0; i < t.length; i++) { h ^= t.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; } return 'c' + h.toString(16).padStart(8, '0'); }
function clesCuisson() {
  const cles = new Map(), vus = new Map();
  for (const T of scene.children) {
    const p = T.position;
    /* ⚠️ la forme est FIGÉE au premier calcul : une fois la géométrie cuite posée, le nombre de sommets
       change, et la clé avec (113 maillages sur 211 seulement, le 2026-11-13) */
    const forme = T.userData.formeCuisson ??= (T.isMesh ? T.geometry.type + ':' + T.geometry.attributes.position.count : (T.userData.scan || 'G') + ':' + T.children.length);
    const sig = forme + '@' + [p.x, p.y, p.z, T.rotation.x, T.rotation.y].map(v => v.toFixed(2)).join(',');
    const n = vus.get(sig) || 0; vus.set(sig, n + 1);
    const parcourir = (o, chemin) => { if (o.isMesh) cles.set(o, empreinte(sig + '#' + n + chemin)); o.children.forEach((c, k) => parcourir(c, chemin + '/' + k)); };
    parcourir(T, '');
  }
  return cles;
}
const PERSONNAGES = () => new Set([hillary.racine, ...visiteuses.map(v => v.perso.racine)]);
const dansPersonnage = (o, exclus) => { for (let q = o; q; q = q.parent) if (exclus.has(q)) return true; return false; };
const vraimentVisible = (o) => { for (let q = o; q; q = q.parent) if (!q.visible) return false; return true; };
/* ce qui reçoit une carte de lumière : le décor opaque éclairé. Les petits objets scannés (plantes, vases,
   suspensions) ne font qu'OCCULTER : ils assombrissent le sol et les murs, sans prendre de place dans la carte */
const OCCULTEURS_SEULS = new Set(['potted_plant_04', 'ceramic_vase_01', 'brass_vase_01', 'modern_ceiling_lamp_01']);

/* EXPORTER LE DÉCOR FIXE POUR BLENDER (la cuisson de la lumière, REALISME.md R1) : formes, couleurs et
   lampes (⚠️ les textures dessinées par programme font échouer l'exporteur, et la cuisson n'en a pas
   besoin) ; sans personnages, sans repères, sans vitres, sans miroir, sans ciel ; avec les lumières.
   Chaque maillage porte sa CLÉ DE CUISSON en nom, et en « extras » : son objet scanné, s'il reçoit une
   carte, et sa zone (dedans ou dehors). Lancé par monde/_outils/exporter_decor.py. */
/* une lampe telle que glTF la comprend : un projecteur pointe selon le −Z de son nœud, sa cible en enfant */
function lampeExportee(projecteur, couleur, intensite, position, cible, angle = 0.5, penombre = 0.5) {
  const l = projecteur ? new THREE.SpotLight(couleur, intensite, 0, angle, penombre, 2) : new THREE.PointLight(couleur, intensite, 0, 2);
  l.position.copy(position);
  if (projecteur) { l.lookAt(cible); l.add(l.target); l.target.position.set(0, 0, -1); }
  return l;
}
/* un groupe de la géométrie = un morceau (même ordre que les groupes) */
function decouperGroupes(geo) {
  const g = geo.index ? geo.toNonIndexed() : geo;
  return geo.groups.map((gr) => {
    const m = new THREE.BufferGeometry();
    for (const [nom, at] of Object.entries(g.attributes)) {
      m.setAttribute(nom, new THREE.BufferAttribute(at.array.slice(gr.start * at.itemSize, (gr.start + gr.count) * at.itemSize), at.itemSize, at.normalized));
    }
    return m;
  });
}
async function exporterDecor() {
  const { GLTFExporter } = await import('three/addons/exporters/GLTFExporter.js');
  const exclus = PERSONNAGES(), cles = clesCuisson();
  const racine = new THREE.Group();
  const dedans = new THREE.Box3(new THREE.Vector3(-LX - 0.3, -0.1, -LZ - 0.3), new THREE.Vector3(LX + 0.3, H + 0.3, fz + 0.3));
  scene.updateMatrixWorld(true);
  const bb = new THREE.Box3(), centre = new THREE.Vector3();
  scene.traverse((o) => {
    if (dansPersonnage(o, exclus) || !vraimentVisible(o)) return;
    if (o.isMesh && cles.has(o) && !o.isReflector && !o.isInstancedMesh && !o.isSkinnedMesh) {
      const m = Array.isArray(o.material) ? o.material[0] : (o.material || {});
      /* ⚠️ en qualité haute le sol est translucide (au-dessus de son miroir) : il cuit quand même */
      if (m.isShaderMaterial || m.isMeshBasicMaterial || (m.transparent && m.opacity < 0.99 && o !== sol) || m.side === THREE.BackSide) return;
      let scan = ''; for (let q = o; q; q = q.parent) if (q.userData && q.userData.scan) { scan = q.userData.scan; break; }
      bb.setFromObject(o).getCenter(centre);
      const extras = { scan, recepteur: !OCCULTEURS_SEULS.has(scan), zone: dedans.containsPoint(centre) ? 'dedans' : 'dehors' };
      const matiere = (mm) => new THREE.MeshStandardMaterial({ color: mm && mm.color ? mm.color.clone() : 0xffffff, roughness: mm?.roughness ?? 0.8, metalness: mm?.metalness ?? 0, emissive: mm && mm.emissive ? mm.emissive.clone() : 0x000000 });
      /* ⚠️ UNE MATIÈRE PAR FACE (les meubles à lattes) : la forme revenue de Blender avait perdu son
         découpage par matière, et three.js ne dessine RIEN d'un maillage à plusieurs matières sans
         groupes (les deux meubles devant les plantes avaient disparu, vu le 2026-11-13). Chaque groupe
         part donc en morceau séparé « clé + g + rang », et la page recolle les morceaux au retour. */
      const morceaux = Array.isArray(o.material) && o.geometry.groups.length ? decouperGroupes(o.geometry) : [o.geometry];
      morceaux.forEach((geo, k) => {
        const mm = Array.isArray(o.material) ? o.material[o.geometry.groups[k].materialIndex] : o.material;
        const c = new THREE.Mesh(geo, matiere(mm));
        c.applyMatrix4(o.matrixWorld); c.name = cles.get(o) + (morceaux.length > 1 || Array.isArray(o.material) ? 'g' + k : '');
        c.userData = extras; racine.add(c);
      });
    } else if ((o.isPointLight || o.isSpotLight) && o.intensity > 0 && o !== lumiereFace) {
      /* ⚠️ un projecteur de three.js VISE SA CIBLE ; l'exporteur glTF ne connaît que l'orientation du nœud :
         sans ce `lookAt`, les 7 projecteurs éclairaient le mur du fond dans Blender (2026-11-13) */
      racine.add(lampeExportee(o.isSpotLight, o.color, o.intensity, o.getWorldPosition(new THREE.Vector3()), o.isSpotLight ? o.target.getWorldPosition(new THREE.Vector3()) : null, o.angle, o.penumbra));
    }
  });
  /* DES LAMPES POUR LA CUISSON SEULEMENT (elles n'existent pas dans la page, elles ne coûtent rien au
     téléphone) : chaque spot encastré du plafond devient un vrai projecteur vers le bas (ses flaques au
     sol étaient peintes), et l'anneau doré de la coupole éclaire vraiment le plafond qui l'entoure */
  for (const k of spotsEncastres) {
    /* ⚠️ un cône large (r × 1,5) fondait les flaques en un éclairage uniforme, sans contraste : on le resserre */
    racine.add(lampeExportee(true, new THREE.Color(0xffe2b0), 70 * k.force, new THREE.Vector3(k.x, k.y - 0.03, k.z), new THREE.Vector3(k.x, 0, k.z), Math.atan(k.r * 1.05 / k.y), 0.55));
  }
  {
    const anneau = new THREE.Mesh(ligneDoree.geometry, new THREE.MeshStandardMaterial({ color: 0x000000, emissive: matLigne.color.clone() }));
    ligneDoree.updateMatrixWorld(true); anneau.applyMatrix4(ligneDoree.matrixWorld);
    anneau.name = 'anneau-dore'; anneau.userData = { recepteur: false, emetteur: true, zone: 'dedans' };
    racine.add(anneau);
  }
  const glb = await new GLTFExporter().parseAsync(racine, { binary: true });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([glb], { type: 'model/gltf-binary' })); a.download = 'salon-decor.glb'; a.click();
  return racine.children.length;
}

/* LA LUMIÈRE CUITE REVIENT (REALISME.md R1) : `cuisson/salon-cuit.glb` porte, pour chaque maillage
   récepteur, sa forme avec une 2e coordonnée de texture (`uv1`, dépliée dans Blender), et
   `cuisson/cuisson.json` nomme la carte d'occlusion. La géométrie cuite REMPLACE l'ancienne (même forme,
   coutures en plus) et chaque matière reçoit la carte en `aoMap` sur le canal 1.
   ⚠️ La bande GAUCHE de la carte est blanche : un maillage qui partage une matière cuite sans avoir
   d'`uv1` lit (0, 0), donc du blanc, donc rien ne change pour lui. `?sans-cuisson` pour comparer. */
const cuisson = { appliquee: 0, total: 0, facteur: 1 };   /* `facteur` : pour régler la lumière cuite à l'œil, en direct */
async function appliquerCuisson() {
  if (params.has('sans-cuisson')) return;
  let info;
  try { const r = await fetch('cuisson/cuisson.json', { cache: 'no-cache' }); if (!r.ok) return; info = await r.json(); } catch { return; }
  const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
  const [g, carte] = await Promise.all([
    new GLTFLoader().loadAsync('cuisson/' + info.geometrie + '?v=' + info.version),
    new THREE.TextureLoader().loadAsync('cuisson/' + info.occlusion + '?v=' + info.version),
  ]);
  carte.flipY = false; carte.channel = 1; carte.colorSpace = THREE.NoColorSpace;
  carte.anisotropy = 4; carte.needsUpdate = true;
  const cuit = new Map(), cuitObj = new Map(), zoneDe = new Map();
  g.scene.traverse((o) => { if (o.isMesh && o.geometry.attributes.uv1) { cuit.set(o.name, o.geometry); cuitObj.set(o.name, o); } });
  cuisson.total = cuit.size;
  const { mergeGeometries } = await import('three/addons/utils/BufferGeometryUtils.js');
  const exclus = PERSONNAGES(), matieres = new Set();
  for (const [o, cle] of clesCuisson()) {
    if (dansPersonnage(o, exclus)) continue;
    let geo = null;
    if (Array.isArray(o.material)) {
      /* les morceaux d'un maillage à plusieurs matières, recollés avec leurs groupes */
      const n = o.geometry.groups.length, morceaux = [];
      for (let k = 0; k < n; k++) morceaux.push(cuit.get(cle + 'g' + k));
      if (!n || morceaux.some(x => !x)) continue;
      geo = mergeGeometries(morceaux, true); if (!geo) continue;
      geo.groups.forEach((gr, k) => { gr.materialIndex = o.geometry.groups[k].materialIndex; });
    } else geo = cuit.get(cle);
    if (!geo) continue;
    o.geometry = geo; cuisson.appliquee++;
    zoneDe.set(o, (cuitObj.get(Array.isArray(o.material) ? cle + 'g0' : cle) || {}).userData?.zone || 'dedans');
    for (const m of [].concat(o.material)) if (m && 'aoMap' in m && !m.isShaderMaterial && !m.isMeshBasicMaterial) matieres.add(m);
  }
  for (const m of matieres) { m.aoMap = carte; m.aoMapIntensity = info.intensite ?? 1; m.needsUpdate = true; }

  /* LA LUMIÈRE DES LAMPES, CUITE : sur les surfaces fixes du DEDANS, elle REMPLACE le calcul en direct des
     plafonniers et des projecteurs (ombres douces, rebonds, l'anneau de la coupole qui éclaire vraiment).
     Le soleil, le ciel et les reflets restent en direct : le jour et la nuit réels continuent de jouer.
     ⚠️ Une matière partagée avec le dehors ou avec un objet non cuit est CLONÉE pour le dedans : sinon le
     dehors perdrait ses lampes, ou un objet sans `uv1` prendrait une lumière plate. */
  if (info.lumiere && !params.has('sans-lumiere-cuite')) {
    const lum = await new THREE.TextureLoader().loadAsync('cuisson/' + info.lumiere + '?v=' + info.version);
    lum.flipY = false; lum.channel = 1; lum.colorSpace = THREE.SRGBColorSpace; lum.anisotropy = 4; lum.needsUpdate = true;
    const autres = new Set();
    scene.traverse((o) => { if (o.isMesh && zoneDe.get(o) !== 'dedans') for (const m of [].concat(o.material)) if (m) autres.add(m); });
    const clones = new Map();
    const convertir = (m) => {
      if (!m || !('lightMap' in m) || m.isShaderMaterial || m.isMeshBasicMaterial) return m;
      if (!autres.has(m)) { eclairerCuit(m, lum, info); return m; }
      if (!clones.has(m)) { const c = m.clone(); eclairerCuit(c, lum, info); clones.set(m, c); }
      return clones.get(m);
    };
    for (const [o, zone] of zoneDe) if (zone === 'dedans') o.material = Array.isArray(o.material) ? o.material.map(convertir) : convertir(o.material);
    cuisson.lumiere = cuitsLumiere.size; cuisson.clones = clones.size;
    /* les flaques peintes au sol faisaient semblant : la vraie lumière cuite les remplace */
    for (const k of flaques) k.f.visible = false;
    /* la force suit les projecteurs (qui s'allument un à un pendant l'ouverture) et la nuit (les
       plafonniers baissent le jour, de 9 à 5 et de 7 à 4) */
    moteur.chaqueImage(() => {
      let p = 1;
      if (faisceauxCreations.length) p = faisceauxCreations.reduce((t, f) => t + (f.base ? f.l.intensity / f.base : 1), 0) / faisceauxCreations.length;
      /* cuite aux forces de JOUR (lampes pleines) ; le soir, elle baisse avec les lampes (le tamisé) */
      const k = (0.3 + 0.7 * p) * melanger(1, TAMISE, nuitCuite) * cuisson.facteur;
      for (const m of cuitsLumiere) m.lightMapIntensity = info.intensite_lumiere * k;
    });
  }
  document.body.classList.add('cuit');
}
let nuitCuite = 1;
interieurs.push({ maj: (n, pluie) => { nuitCuite = Math.max(n, pluie * 0.5); } });
const cuitsLumiere = new Set();
const DEBUT_LAMPES = '#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )', FIN_LAMPES = '#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )';
/* une matière cuite : la carte de lumière, et le shader où les plafonniers et les projecteurs n'apportent plus
   que leurs REFLETS (dans three.js r180 leurs boucles se suivent, juste avant celle du soleil : on encadre de
   l'une à l'autre, et la part diffuse qu'elles ajoutent est retirée) */
function eclairerCuit(m, lum, info) {
  m.lightMap = lum; m.lightMapIntensity = info.intensite_lumiere;
  m.aoMapIntensity = info.ao_sur_lumiere ?? 0.5;   /* la lumière cuite contient déjà ses ombres */
  const avant = m.onBeforeCompile, cle = m.customProgramCacheKey.bind(m);
  m.onBeforeCompile = (sh, r) => {
    if (avant) avant.call(m, sh, r);
    const c = THREE.ShaderChunk.lights_fragment_begin, i = c.indexOf(DEBUT_LAMPES), j = c.indexOf(FIN_LAMPES);
    /* ⚠️ on GARDE les reflets des lampes (le marbre qui brille : un reflet dépend du regard, il ne se cuit
       pas) et on retire seulement leur part diffuse, que la carte de lumière apporte déjà. Couper les
       boucles entières éteignait les reflets du sol (vu au téléphone le 2026-11-13). */
    /* R14 : aux qualités moyenne et basse, les boucles des lampes SAUTENT entièrement sur le décor cuit : leur
       diffus est dans la carte, leur éclat sur le sol vient du reflet à 360° de R6. C'était le gros du coût par
       pixel sur un grand écran (Chrome de Mongazi, 2026-11-13). En haute, on garde leurs reflets. */
    if (i >= 0 && j > i) sh.fragmentShader = sh.fragmentShader.replace('#include <lights_fragment_begin>', q.reflets
      ? c.slice(0, i) + 'vec3 diffusAvantLampes = reflectedLight.directDiffuse;\n' + c.slice(i, j) + 'reflectedLight.directDiffuse = diffusAvantLampes;\n' + c.slice(j)
      : c.slice(0, i) + c.slice(j));
  };
  m.customProgramCacheKey = () => cle() + '|cuit';
  m.needsUpdate = true; cuitsLumiere.add(m);
}

/* R6 · LE SOL QUI REFLÈTE, AU TÉLÉPHONE AUSSI (REALISME.md). En qualité haute, un vrai miroir (`Reflector`,
   qui redessine toute la scène à chaque image). Aux qualités moyenne et basse, LE MIROIR PAR PHOTO À 360° :
   un sol plat reflète exactement ce que voit L'ŒIL DU VISITEUR REFLÉTÉ SOUS LE SOL. On photographie donc la
   pièce depuis ce point (x, −y, z), sans le sol ni les personnages, et chaque point du sol lit la photo dans
   la direction « œil reflété → ce point » : le reflet d'un podium tombe sous le podium, juste et net, tant
   que le visiteur reste là. Il se déplace par points de passage : la photo est REFAITE quand il s'arrête
   ailleurs, et quand la lumière change (jour, soir, projecteurs, pluie). Une face de la photo par image
   (six images), pour ne jamais faire hoqueter le téléphone. Coût ordinaire : une lecture de texture.
   `?sans-reflet` pour comparer.
   ⚠️ 1er essai (même jour) : une photo prise une fois au centre, projetée sur les murs (parallaxe en boîte).
   Aucun reflet visible : un podium AU MILIEU de la pièce n'est pas sur les murs, et le centre tombait même
   dans les panneaux du podium central.
   ⚠️ La matière du sol a déjà sa lumière cuite (`eclairerCuit`) : les deux retouches du shader s'ENCHAÎNENT.
   ⚠️ L'environnement apporte aussi de la lumière DIFFUSE : `irradiance` la règle à part, sans toucher au reflet. */
const refletSol = { prises: 0, actif: false, irradiance: Number(params.get('reflet-irr') || 0.8), force: Number(params.get('reflet-force') || 2.4), signature: '' };   /* réglables à l'essai : ?reflet-force=…&reflet-irr=… */
function poserRefletSol() {
  if (q.reflets || params.has('sans-reflet') || refletSol.actif) return;
  const r = moteur.renderer, mat = sol.material;   /* ⚠️ la matière réellement posée (la cuisson peut l'avoir clonée) */
  const flottant = r.extensions.has('EXT_color_buffer_half_float') || r.extensions.has('EXT_color_buffer_float');
  const cible = new THREE.WebGLCubeRenderTarget(q.nom === 'basse' ? 128 : 256, { type: flottant ? THREE.HalfFloatType : THREE.UnsignedByteType });
  const cam = new THREE.CubeCamera(0.05, 80, cible); scene.add(cam);
  mat.roughness = 0.12;   /* × la rugosité du marbre scanné (0,5) : un poli de 0,06, le sol miroir de ses images */
  const pmrem = new THREE.PMREMGenerator(r);
  const uni = { uOeilReflete: { value: new THREE.Vector3() }, uIrradiance: { value: refletSol.irradiance } };
  let env = null, face = -1;
  const prise = new THREE.Vector3(1e9, 0, 0);   /* où la dernière photo a été prise (l'œil, pas son reflet) */
  function commencer() {
    prise.copy(camera.position);
    cam.position.set(prise.x, -prise.y, prise.z); cam.updateMatrixWorld(true);
    face = 0;
  }
  function uneFace() {
    const caches = [sol, ...PERSONNAGES()].filter(o => o && o.visible);
    caches.forEach(o => { o.visible = false; });
    if (cam.coordinateSystem !== r.coordinateSystem) { cam.coordinateSystem = r.coordinateSystem; cam.updateCoordinateSystem(); }
    const avantCible = r.getRenderTarget(), xr = r.xr.enabled; r.xr.enabled = false;
    r.setRenderTarget(cible, face); r.render(scene, cam.children[face]);
    r.setRenderTarget(avantCible); r.xr.enabled = xr;
    caches.forEach(o => { o.visible = true; });
    if (++face < 6) return;
    face = -1;
    const ancien = env; env = pmrem.fromCubemap(cible.texture);
    uni.uOeilReflete.value.copy(cam.position);
    mat.envMap = env.texture; mat.needsUpdate = !ancien;
    if (ancien) ancien.dispose();
    refletSol.prises++;
  }
  const avant = mat.onBeforeCompile, cle = mat.customProgramCacheKey.bind(mat);
  const ANCRE = 'reflectVec = inverseTransformDirection( reflectVec, viewMatrix );', IRR = 'return PI * envMapColor.rgb * envMapIntensity;';
  mat.onBeforeCompile = (sh, rr) => {
    if (avant) avant.call(mat, sh, rr);
    const chunk = THREE.ShaderChunk.envmap_physical_pars_fragment;
    if (!chunk.includes(ANCRE) || !chunk.includes(IRR)) { console.warn('reflet du sol : le shader de three.js a changé'); return; }
    Object.assign(sh.uniforms, uni);
    sh.vertexShader = 'varying vec3 vPosMonde;\n' + sh.vertexShader.replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\n\tvPosMonde = ( modelMatrix * vec4( transformed, 1.0 ) ).xyz;');
    sh.fragmentShader = 'varying vec3 vPosMonde;\nuniform vec3 uOeilReflete;\nuniform float uIrradiance;\n' +
      sh.fragmentShader.replace('#include <envmap_physical_pars_fragment>', chunk
        .replace(ANCRE, ANCRE + '\n\t\t\treflectVec = normalize( vPosMonde - uOeilReflete );')
        .replace(IRR, 'return PI * envMapColor.rgb * envMapIntensity * uIrradiance;'));
  };
  mat.customProgramCacheKey = () => cle() + '|reflet';
  /* la première photo d'un coup (le sol ne doit pas rester sans reflet), les suivantes face par face */
  commencer(); while (face >= 0) uneFace();
  refletSol.actif = true;
  const signature = () => {
    const e = ciel.etat, p = faisceauxCreations.length ? faisceauxCreations.reduce((t, f) => t + (f.base ? f.l.intensity / f.base : 1), 0) / faisceauxCreations.length : 1;
    return [Math.round(e.nuit * 10), Math.round(e.pluie * 4), Math.round(p * 5), cuisson.appliquee].join(',');
  };
  refletSol.signature = signature();
  let attente = 0, calme = 0;
  const avantPos = camera.position.clone();
  moteur.chaqueImage((dt) => {
    uni.uIrradiance.value = refletSol.irradiance / refletSol.force; mat.envMapIntensity = refletSol.force;
    if (face >= 0) { uneFace(); return; }
    /* le visiteur s'est-il arrêté (moins de 2 mm par image pendant 0,3 s) ? */
    calme = camera.position.distanceTo(avantPos) < 0.002 ? calme + dt : 0; avantPos.copy(camera.position);
    if (calme > 0.3 && camera.position.distanceTo(prise) > 0.25) { commencer(); return; }
    attente += dt; if (attente < 1) return; attente = 0;
    const s = signature();
    if (s !== refletSol.signature) { refletSol.signature = s; commencer(); }
  });
  refletSol.prendre = () => { commencer(); while (face >= 0) uneFace(); };
}

/* pour les contrôles automatiques */
window.__monde = { son, exporterDecor, clesCuisson, cuisson, refletSol, fusionDecor, sol, moteur, deplacement, dialogue, boutique, pnj, ciel, ctx, totems, hillary, plan, F, D, carnet, options, toucherPnj, toucherHillary };

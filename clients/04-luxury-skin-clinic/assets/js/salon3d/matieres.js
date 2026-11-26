// Les matières du salon, toutes dessinées en code (aucune photo de décor, aucun fichier à télécharger).
// Chaque texture garde un grain irrégulier : une surface trop lisse « fait IA » (règle du 19/11).
import { THREE } from "./moteur.js";

// un hasard reproductible : le même terrazzo à chaque visite
export function graine(s) {
  let x = s >>> 0 || 1;
  return () => ((x = (x * 1664525 + 1013904223) >>> 0) / 4294967296);
}

// Sur grand rendu (4K), une toile qui le DEMANDE est en double définition : on dessine dans le même repère, l'échelle
// fait le reste. Seuls les panneaux posés d'un seul tenant le demandent : un sol ou un mur où la matière se répète 6 à
// 14 fois a déjà plus de détail que l'écran, et doubler ses 16 millions de pixels gelait le démarrage (2,5 s mesurées).
function toile(w, h, fin = false) {
  const F = (fin && typeof window !== "undefined" && window.S3D_FINESSE) || 1;
  const c = document.createElement("canvas");
  c.width = w * F; c.height = h * F;
  const g = c.getContext("2d", { willReadFrequently: true });
  if (F !== 1) g.scale(F, F);
  return [c, g];
}

function tex(c, anis, rep = 1) {
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = anis || 1;
  if (rep !== 1) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep, rep); }
  return t;
}

function grain(g, w, h, amp, r) {
  // le grain se pose sur les VRAIS pixels de la toile (getImageData ignore l'échelle)
  const d = g.getImageData(0, 0, g.canvas.width, g.canvas.height), a = d.data;
  for (let i = 0; i < a.length; i += 4) {
    const n = (r() - 0.5) * amp;
    a[i] += n; a[i + 1] += n; a[i + 2] += n;
  }
  g.putImageData(d, 0, 0);
}

// terrazzo clair : fond crème, éclats de toutes tailles, jamais alignés
export function terrazzo(anis, { base = "#ece6da", eclats = ["#c9c2b4", "#a9c7bb", "#d7c08a", "#f7f4ee", "#b7aa98", "#8fb3a4"], n = 2600, taille = 1024, rep = 4 } = {}) {
  const [c, g] = toile(taille, taille), r = graine(229);
  g.fillStyle = base; g.fillRect(0, 0, taille, taille);
  for (let i = 0; i < n; i++) {
    const x = r() * taille, y = r() * taille, s = (r() ** 3) * 22 + 2;
    g.fillStyle = eclats[(r() * eclats.length) | 0];
    g.globalAlpha = 0.55 + r() * 0.45;
    g.beginPath();
    const cotes = 4 + ((r() * 4) | 0);
    for (let j = 0; j < cotes; j++) {
      const a = (j / cotes) * 6.283 + r() * 0.8, d = s * (0.55 + r() * 0.6);
      j ? g.lineTo(x + Math.cos(a) * d, y + Math.sin(a) * d) : g.moveTo(x + Math.cos(a) * d, y + Math.sin(a) * d);
    }
    g.closePath(); g.fill();
  }
  g.globalAlpha = 1;
  grain(g, taille, taille, 10, r);
  return tex(c, anis, rep);
}

// marbre sombre veiné d'or (le cabinet privé, la boutique INA)
export function marbre(anis, { base = "#14110d", veine = "rgba(201,168,76,", rep = 2, taille = 1024, n = 18 } = {}) {
  const [c, g] = toile(taille, taille, rep <= 1), r = graine(1806);
  g.fillStyle = base; g.fillRect(0, 0, taille, taille);
  for (let i = 0; i < n; i++) {
    let x = r() * taille, y = r() * taille, a = r() * 6.283;
    g.strokeStyle = veine + (0.05 + r() * 0.22) + ")";
    g.lineWidth = 0.6 + r() * 2.2;
    g.beginPath(); g.moveTo(x, y);
    for (let j = 0; j < 60; j++) {
      a += (r() - 0.5) * 0.7;
      x += Math.cos(a) * 14; y += Math.sin(a) * 14;
      g.lineTo(x, y);
    }
    g.stroke();
  }
  grain(g, taille, taille, 7, r);
  return tex(c, anis, rep);
}

// chêne clair, veiné dans la longueur (les lattes de l'accueil)
export function chene(anis, { base = "#c9a57b", fonce = "#a88158", w = 256, h = 1024 } = {}) {
  const [c, g] = toile(w, h), r = graine(7);
  g.fillStyle = base; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 70; i++) {
    let x = r() * w;
    g.strokeStyle = fonce; g.globalAlpha = 0.08 + r() * 0.22; g.lineWidth = 0.5 + r() * 2.5;
    g.beginPath(); g.moveTo(x, 0);
    for (let y = 0; y <= h; y += 32) { x += (r() - 0.5) * 3; g.lineTo(x, y); }
    g.stroke();
  }
  g.globalAlpha = 1;
  grain(g, w, h, 14, r);
  return tex(c, anis);
}

// plâtre chaulé : un blanc qui respire
// `taches` règle la force des nuages du plâtre (1 = d'origine ; 0,3 = une chaux lisse, cf. la clinique du 26/11)
export function platre(anis, { base = "#f3efe6", amp = 9, taille = 512, rep = 3, taches = 1 } = {}) {
  const [c, g] = toile(taille, taille), r = graine(31);
  g.fillStyle = base; g.fillRect(0, 0, taille, taille);
  for (let i = 0; i < 260; i++) {
    g.fillStyle = r() > 0.5 ? `rgba(255,255,255,${0.05 * taches})` : `rgba(120,100,70,${0.035 * taches})`;
    g.beginPath(); g.arc(r() * taille, r() * taille, 8 + r() * 40, 0, 6.283); g.fill();
  }
  grain(g, taille, taille, amp, r);
  return tex(c, anis, rep);
}

// une plaque gravée (laiton, papier, verre) : du texte net, dessiné à 2x
export function plaque(anis, { w = 1024, h = 512, fond = "#b8954a", reflet = true, lignes = [], cadre = null } = {}) {
  const [c, g] = toile(w, h);
  if (fond) {
    if (reflet) {
      const d = g.createLinearGradient(0, 0, w, h);
      d.addColorStop(0, shade(fond, 18)); d.addColorStop(0.45, fond); d.addColorStop(1, shade(fond, -22));
      g.fillStyle = d;
    } else g.fillStyle = fond;
    g.fillRect(0, 0, w, h);
    // brossage
    const r = graine(h);
    for (let i = 0; i < h; i += 2) { g.fillStyle = `rgba(255,255,255,${r() * 0.05})`; g.fillRect(0, i, w, 1); }
  }
  if (cadre) { g.strokeStyle = cadre; g.lineWidth = h * 0.012; g.strokeRect(h * 0.05, h * 0.05, w - h * 0.1, h - h * 0.1); }
  g.textAlign = "center"; g.textBaseline = "middle";
  for (const l of lignes) {
    g.font = l.font; g.fillStyle = l.couleur || "#2a1f0e";
    if (l.espace) g.letterSpacing = l.espace;
    if (l.ombre) { g.shadowColor = l.ombre; g.shadowBlur = 0; g.shadowOffsetY = 2; }
    let t = l.t;
    // on raccourcit un nom trop long plutôt que de le laisser déborder
    while (g.measureText(t).width > w * 0.9 && t.length > 4) t = t.slice(0, -2);
    if (t !== l.t) t = t.trim() + "…";
    g.fillText(t, (l.x ?? 0.5) * w, l.y * h);
    g.shadowColor = "transparent"; g.letterSpacing = "0px";
  }
  return tex(c, anis);
}

// LE CAISSON LUMINEUX d'un soin (26/11, « 10 000 $ ») : la direction « LA LUMIÈRE » appliquée au couloir. Un panneau
// rétroéclairé, son croquis d'or (le même que sa carte, dans la page), son nom, son prix, sa durée. Il remplace la
// petite plaque de laiton qu'on ne pouvait pas lire. 768 × 1050 : au plus grand, il occupe 860 px d'un écran 4K.
export function caisson(anis, { w = 768, h = 1050, croquis = null, sur = "", nom = "", prix = "", duree = "" } = {}) {
  const [c, g] = toile(w, h);
  const d = g.createRadialGradient(w * 0.5, h * 0.28, 10, w * 0.5, h * 0.42, h * 0.78);
  d.addColorStop(0, "#fffdf8"); d.addColorStop(0.55, "#f7efdf"); d.addColorStop(1, "#e8d9bb");
  g.fillStyle = d; g.fillRect(0, 0, w, h);
  g.strokeStyle = "rgba(160,122,40,.85)"; g.lineWidth = 3; g.strokeRect(26, 26, w - 52, h - 52);
  g.strokeStyle = "rgba(160,122,40,.38)"; g.lineWidth = 1.5; g.strokeRect(38, 38, w - 76, h - 76);
  g.textAlign = "center"; g.textBaseline = "middle";
  g.font = "500 22px 'DM Mono', monospace"; g.fillStyle = "#7d5f18"; g.letterSpacing = "6px";
  g.fillText(String(sur).toUpperCase(), w / 2, h * 0.085); g.letterSpacing = "0px";
  if (croquis) { const cw = w * 0.8, ch = cw * 100 / 208; g.drawImage(croquis, (w - cw) / 2, h * 0.12, cw, ch); }
  // le nom : la plus grande taille qui tient en deux lignes
  let taille = 86, lignes = [];
  for (; taille >= 56; taille -= 6) {
    g.font = `600 ${taille}px 'Cormorant Garamond', Georgia, serif`;
    lignes = []; let l = "";
    for (const mot of String(nom).split(/\s+/)) {
      const t = l ? l + " " + mot : mot;
      if (g.measureText(t).width > w * 0.82 && l) { lignes.push(l); l = mot; } else l = t;
    }
    if (l) lignes.push(l);
    if (lignes.length <= 2 && lignes.every((x) => g.measureText(x).width <= w * 0.86)) break;
  }
  g.fillStyle = "#2b2112";
  const pas = taille * 1.08;
  let y = h * 0.565 - (lignes.length - 1) * pas / 2;
  for (const l of lignes) { g.fillText(l, w / 2, y); y += pas; }
  g.strokeStyle = "rgba(160,122,40,.9)"; g.lineWidth = 2;
  g.beginPath(); g.moveTo(w / 2 - 56, y - pas * 0.32); g.lineTo(w / 2 + 56, y - pas * 0.32); g.stroke();
  g.font = "500 70px 'Jost', sans-serif"; g.fillStyle = "#7d5f18";
  g.fillText(prix, w / 2, y + 40);
  if (duree) {
    g.font = "500 23px 'DM Mono', monospace"; g.fillStyle = "#5a4718"; g.letterSpacing = "5px";
    g.fillText(String(duree).toUpperCase(), w / 2, y + 104); g.letterSpacing = "0px";
  }
  return tex(c, anis);
}

// un dégradé radial ou vertical (ciel des baies, cônes de lumière, halos)
export function degrade(anis, stops, { w = 64, h = 256, radial = false } = {}) {
  const [c, g] = toile(w, h);
  const d = radial ? g.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, Math.min(w, h) / 2) : g.createLinearGradient(0, 0, 0, h);
  stops.forEach(([o, col]) => d.addColorStop(o, col));
  g.fillStyle = d; g.fillRect(0, 0, w, h);
  return tex(c, anis);
}

// une poussière de lumière (sprite)
export function point(anis, couleur = "255,236,196") {
  const [c, g] = toile(64, 64);
  const d = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  d.addColorStop(0, `rgba(${couleur},1)`); d.addColorStop(0.35, `rgba(${couleur},.35)`); d.addColorStop(1, `rgba(${couleur},0)`);
  g.fillStyle = d; g.fillRect(0, 0, 64, 64);
  return tex(c, anis);
}

// une feuille (olivier, monstera) découpée en alpha
export function feuille(anis, { couleur = "#5f7f52", nervure = "#8fae7a", forme = "olivier" } = {}) {
  const [c, g] = toile(128, 256);
  g.fillStyle = couleur;
  g.beginPath();
  if (forme === "olivier") { g.moveTo(64, 4); g.quadraticCurveTo(108, 128, 64, 252); g.quadraticCurveTo(20, 128, 64, 4); }
  else { g.moveTo(64, 6); g.bezierCurveTo(128, 40, 128, 220, 64, 250); g.bezierCurveTo(0, 220, 0, 40, 64, 6); }
  g.fill();
  g.strokeStyle = nervure; g.lineWidth = 2; g.beginPath(); g.moveTo(64, 10); g.lineTo(64, 246); g.stroke();
  const t = tex(c, anis);
  return t;
}

// L'ÉCLAIRAGE D'AMBIANCE : une petite pièce aux panneaux lumineux, réduite en carte de reflets (PMREM).
// Même principe que RoomEnvironment de three.js, écrit ici pour ne rien télécharger de plus.
export function ambiance(renderer, { mur = 0x8a8478, lumieres = [[0, 9, 0, 14, 0.4, 14, 5], [-9, 4, 0, 0.4, 6, 10, 9], [9, 4, 0, 0.4, 6, 10, 3], [0, 4, -9, 10, 6, 0.4, 3]], chaud = 0xfff2de } = {}) {
  const s = new THREE.Scene();
  const boite = new THREE.Mesh(new THREE.BoxGeometry(20, 12, 20), new THREE.MeshStandardMaterial({ color: mur, side: THREE.BackSide, roughness: 1 }));
  boite.position.y = 5; s.add(boite);
  s.add(new THREE.AmbientLight(0xffffff, 0.6));
  for (const [x, y, z, w, h, d, i] of lumieres) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshBasicMaterial({ color: new THREE.Color(chaud).multiplyScalar(i) }));
    m.position.set(x, y, z); s.add(m);
  }
  const pm = new THREE.PMREMGenerator(renderer);
  const rt = pm.fromScene(s, 0.035);
  pm.dispose();
  return rt.texture;
}

// une boîte aux coins arrondis (comptoir, banquette, table de soin), par extrusion d'un rectangle arrondi
export function boiteArrondie(w, h, d, r = 0.05, seg = 4) {
  const s = new THREE.Shape(), x = -w / 2, y = -h / 2, rr = Math.min(r, w / 2, h / 2);
  s.moveTo(x + rr, y); s.lineTo(x + w - rr, y); s.quadraticCurveTo(x + w, y, x + w, y + rr);
  s.lineTo(x + w, y + h - rr); s.quadraticCurveTo(x + w, y + h, x + w - rr, y + h);
  s.lineTo(x + rr, y + h); s.quadraticCurveTo(x, y + h, x, y + h - rr);
  s.lineTo(x, y + rr); s.quadraticCurveTo(x, y, x + rr, y);
  const b = Math.min(r, d / 2) * 0.9;
  const g = new THREE.ExtrudeGeometry(s, { depth: d - 2 * b, bevelEnabled: true, bevelThickness: b, bevelSize: b * 0.9, bevelSegments: seg, curveSegments: seg * 2 });
  g.translate(0, 0, -(d - 2 * b) / 2);
  g.computeVertexNormals();
  return g;
}

// un comptoir en demi-lune (plan en arc extrudé en hauteur)
export function demiLune(rayon, epaisseur, hauteur, ouverture = Math.PI) {
  const s = new THREE.Shape();
  const a0 = -ouverture / 2 - Math.PI / 2, a1 = ouverture / 2 - Math.PI / 2;
  s.absarc(0, 0, rayon, a0, a1, false);
  s.absarc(0, 0, rayon - epaisseur, a1, a0, true);
  const g = new THREE.ExtrudeGeometry(s, { depth: hauteur, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02, bevelSegments: 3, curveSegments: 48 });
  g.rotateX(-Math.PI / 2);
  return g;
}

function shade(hex, pct) {
  const n = parseInt(hex.slice(1), 16);
  const f = (v) => Math.max(0, Math.min(255, Math.round(v + (pct / 100) * 255)));
  return `rgb(${f(n >> 16)},${f((n >> 8) & 255)},${f(n & 255)})`;
}

// des grains de lumière qui flottent (Points), très peu nombreux, coupés en qualité basse
export function poussiere(anis, { n = 160, boite = [10, 4, 10], centre = [0, 2, 0], couleur = "255,232,190", taille = 0.05, opacite = 0.55 } = {}) {
  const r = graine(n * 13), pos = new Float32Array(n * 3), vit = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    pos[i * 3] = centre[0] + (r() - 0.5) * boite[0];
    pos[i * 3 + 1] = centre[1] + (r() - 0.5) * boite[1];
    pos[i * 3 + 2] = centre[2] + (r() - 0.5) * boite[2];
    vit[i] = 0.02 + r() * 0.06;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  const m = new THREE.PointsMaterial({ map: point(anis, couleur), size: taille, transparent: true, opacity: opacite, depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true });
  const p = new THREE.Points(g, m);
  p.userData.animer = (dt) => {
    const a = g.attributes.position.array;
    for (let i = 0; i < n; i++) {
      a[i * 3 + 1] += vit[i] * dt;
      a[i * 3] += Math.sin((a[i * 3 + 1] + i) * 0.7) * 0.002;
      if (a[i * 3 + 1] > centre[1] + boite[1] / 2) a[i * 3 + 1] = centre[1] - boite[1] / 2;
    }
    g.attributes.position.needsUpdate = true;
  };
  return p;
}

/* LE MONDE · le vrai ciel au-dessus d'un lieu.
   L'heure est CELLE DU LIEU (Cotonou : UTC+1, pas d'heure d'été), quelle que
   soit l'heure du téléphone : un visiteur à Paris voit la nuit de Cotonou.
   La météo vient du relais /api/meteo (MET Norway, gratuit en usage
   commercial, interrogé une fois toutes les 10 minutes pour tout le monde).
   ⚠️ Open-Meteo n'est gratuit qu'en usage NON commercial : pas lui.

   Essais : ?heure=21.5  ?meteo=pluie|orage|clair|brume|nuages

   Position du soleil : formules classiques de l'astronomie (Meeus), les
   mêmes que celles de SunCalc. */
import { THREE, graine, texteCanvas, melanger, borner } from './moteur.js';

export const COTONOU = { lat: 6.3703, lon: 2.3912, decalage: 1, nom: 'Cotonou' };

const RAD = Math.PI / 180, JOUR_MS = 86400000, J1970 = 2440588, J2000 = 2451545, OBLIQ = RAD * 23.4397;

export function positionSoleil(date, lat, lon) {
  const d = date.valueOf() / JOUR_MS - 0.5 + J1970 - J2000;
  const M = RAD * (357.5291 + 0.98560028 * d);
  const C = RAD * (1.9148 * Math.sin(M) + 0.02 * Math.sin(2 * M) + 0.0003 * Math.sin(3 * M));
  const L = M + C + RAD * 102.9372 + Math.PI;
  const dec = Math.asin(Math.sin(OBLIQ) * Math.sin(L));
  const ra = Math.atan2(Math.sin(L) * Math.cos(OBLIQ), Math.cos(L));
  const lw = RAD * -lon, phi = RAD * lat;
  const H = RAD * (280.16 + 360.9856235 * d) - lw - ra;
  const elevation = Math.asin(Math.sin(phi) * Math.sin(dec) + Math.cos(phi) * Math.cos(dec) * Math.cos(H));
  const azimut = Math.atan2(Math.sin(H), Math.cos(H) * Math.sin(phi) - Math.tan(dec) * Math.cos(phi));
  return { elevation: elevation / RAD, azimut: azimut / RAD };   /* azimut : 0 = sud, + vers l'ouest */
}

/* l'heure du lieu, éventuellement forcée par ?heure=  */
export function maintenant(lieu = COTONOU) {
  const p = new URLSearchParams(location.search).get('heure');
  let date = new Date();
  if (p !== null && !isNaN(parseFloat(p))) {
    const h = parseFloat(p);
    const local = new Date(Date.now() + lieu.decalage * 3600000);
    date = new Date(Date.UTC(local.getUTCFullYear(), local.getUTCMonth(), local.getUTCDate(),
      Math.floor(h) - lieu.decalage, Math.round((h % 1) * 60)));
  }
  const l = new Date(date.valueOf() + lieu.decalage * 3600000);
  return { date, h: l.getUTCHours(), m: l.getUTCMinutes(), dec: l.getUTCHours() + l.getUTCMinutes() / 60,
           jourSemaine: l.getUTCDay(), mois: l.getUTCMonth() + 1 };
}

export function interpreterMeteo(m, mois) {
  const forcee = new URLSearchParams(location.search).get('meteo');
  const s = forcee || String(m && m.symbole || 'clearsky').replace(/_(day|night|polartwilight)$/, '');
  let pluie = 0, orage = false, brume = 0;
  let nuages = m && m.nuages != null ? m.nuages / 100 : 0.3;
  if (/heavyrain/.test(s)) pluie = 1;
  else if (/^pluie$/.test(s)) pluie = 0.75;
  else if (/lightrain/.test(s)) pluie = 0.35;
  else if (/rain|showers|sleet/.test(s)) pluie = 0.65;
  if (/thunder|orage/.test(s)) { orage = true; pluie = Math.max(pluie, 0.85); }
  if (/fog|brume/.test(s)) brume = 0.6;
  if (/nuages|cloudy/.test(s)) nuages = Math.max(nuages, 0.85);
  if (/clair|clearsky/.test(s) && forcee) nuages = 0.1;
  if (pluie > 0) nuages = Math.max(nuages, 0.9);
  /* l'harmattan : décembre à février, air sec, la lumière se voile */
  if ([12, 1, 2].includes(mois) && pluie === 0 && (m && m.humidite != null ? m.humidite : 60) < 55) brume = Math.max(brume, 0.45);
  return { symbole: s, pluie, orage, brume, nuages, temp: m && m.temp != null ? m.temp : null };
}

/* ---------- la rue, peinte ---------- */
const ENSEIGNES = ['ALIMENTATION', 'QUINCAILLERIE', 'COIFFURE', 'PHARMACIE', 'MAQUIS', 'TÉLÉPHONES', 'PRESSING', 'BOUTIQUE'];
const MURS = ['#d9a066', '#c9785a', '#e8d9b8', '#9fbfa8', '#7fa7c4', '#e6c27a', '#efe8da', '#b65c4a', '#d7b98e', '#a8c3b0'];

function teinte(hex, f, vers = [0, 0, 0]) {
  const n = parseInt(hex.slice(1), 16);
  const c = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v, i) => Math.round(melanger(v, vers[i], f)));
  return `rgb(${c[0]},${c[1]},${c[2]})`;
}

function plan_de_rue(rnd) {
  const b = []; let x = -20;
  while (x < 2048) {
    const w = 120 + rnd() * 150, h = 330 + rnd() * 330;
    b.push({ x, w, h, mur: MURS[Math.floor(rnd() * MURS.length)], etages: Math.max(2, Math.round(h / 140)),
      citerne: rnd() < 0.55, enseigne: rnd() < 0.6 ? ENSEIGNES[Math.floor(rnd() * ENSEIGNES.length)] : null,
      fen: Array.from({ length: 40 }, () => rnd()) });
    x += w + 6 + rnd() * 30;
  }
  const palmiers = [180, 760, 1290, 1820].map(px => ({ x: px + rnd() * 120, h: 420 + rnd() * 160, s: rnd() }));
  return { b, palmiers };
}

function peindreRue(ctx, W, H, e, plan) {
  const nuit = e.nuit, jour = e.jour, dore = e.dore, gris = borner(e.nuages * 0.7 + e.pluie * 0.5, 0, 1);
  /* le ciel */
  const g = ctx.createLinearGradient(0, 0, 0, H * 0.75);
  const haut = [melanger(142, 11, nuit), melanger(197, 21, nuit), melanger(234, 48, nuit)];
  const bas = [melanger(243, 43, nuit), melanger(230, 35, nuit), melanger(200, 64, nuit)];
  const m = (c, cible, t) => c.map((v, i) => Math.round(melanger(v, cible[i], t)));
  let hC = m(haut, [235, 150, 90], dore * 0.6), bC = m(bas, [255, 196, 120], dore * 0.8);
  hC = m(hC, [melanger(170, 40, nuit), melanger(176, 44, nuit), melanger(182, 54, nuit)], gris);
  bC = m(bC, [melanger(200, 52, nuit), melanger(200, 50, nuit), melanger(198, 62, nuit)], gris);
  g.addColorStop(0, `rgb(${hC})`); g.addColorStop(1, `rgb(${bC})`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const sol = H * 0.93;
  const assombrir = borner(nuit * 0.72 + e.pluie * 0.22, 0, 0.85);
  /* les immeubles */
  for (const b of plan.b) {
    const y = sol - b.h;
    ctx.fillStyle = teinte(b.mur, assombrir, [20, 22, 38]);
    ctx.fillRect(b.x, y, b.w, b.h);
    ctx.fillStyle = teinte(b.mur, Math.min(1, assombrir + 0.25), [10, 10, 20]);
    ctx.fillRect(b.x, y, b.w, 10);                                       /* acrotère */
    if (b.citerne) {                                                     /* la citerne noire sur le toit */
      ctx.fillStyle = teinte('#1d1f22', 0); ctx.fillRect(b.x + b.w * 0.62, y - 46, 34, 46);
      ctx.beginPath(); ctx.ellipse(b.x + b.w * 0.62 + 17, y - 46, 17, 6, 0, 0, Math.PI * 2); ctx.fill();
    }
    const hEt = (b.h - 120) / b.etages; let k = 0;
    for (let et = 0; et < b.etages; et++) {
      const fy = y + 26 + et * hEt;
      for (let fx = b.x + 16; fx < b.x + b.w - 30; fx += 44) {
        const allumee = nuit > 0.3 && b.fen[k++ % 40] < 0.45;
        ctx.fillStyle = allumee ? `rgba(255,${190 + Math.round(40 * b.fen[k % 40])},110,${0.55 + nuit * 0.4})` : teinte('#3a4048', assombrir * 0.5, [8, 8, 14]);
        ctx.fillRect(fx, fy, 22, hEt * 0.5);
        if (allumee) { ctx.fillStyle = 'rgba(255,200,120,.12)'; ctx.fillRect(fx - 8, fy - 8, 38, hEt * 0.5 + 16); }
      }
      ctx.fillStyle = teinte(b.mur, Math.min(1, assombrir + 0.35), [0, 0, 0]);
      ctx.fillRect(b.x, fy + hEt * 0.62, b.w, 4);                          /* balcon */
    }
    /* le rez-de-chaussée : rideau de fer, ou boutique allumée la nuit */
    const ry = sol - 110;
    ctx.fillStyle = nuit > 0.5 && b.fen[3] < 0.5 ? 'rgba(255,205,130,.85)' : teinte('#8c9096', assombrir, [20, 20, 28]);
    ctx.fillRect(b.x + 10, ry, b.w - 20, 100);
    if (!(nuit > 0.5 && b.fen[3] < 0.5)) { ctx.fillStyle = 'rgba(0,0,0,.12)'; for (let s = ry; s < ry + 100; s += 7) ctx.fillRect(b.x + 10, s, b.w - 20, 2); }
    if (b.enseigne) {
      const vert = b.enseigne === 'PHARMACIE';
      ctx.fillStyle = teinte(vert ? '#1f8a4c' : (b.fen[5] < 0.5 ? '#f4efe4' : '#203a6b'), assombrir * 0.6, [0, 0, 0]);
      ctx.fillRect(b.x + 8, ry - 36, b.w - 16, 30);
      ctx.fillStyle = vert || b.fen[5] >= 0.5 ? '#ffffff' : '#7a1f2b';
      ctx.font = 'bold 19px Archivo, Arial, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText(b.enseigne, b.x + b.w / 2, ry - 20, b.w - 26);
      if (nuit > 0.4) { ctx.fillStyle = 'rgba(255,240,200,.18)'; ctx.fillRect(b.x + 4, ry - 40, b.w - 8, 38); }
    }
  }
  /* poteaux et câbles */
  ctx.strokeStyle = `rgba(20,20,24,${0.75 - nuit * 0.3})`; ctx.lineWidth = 3;
  for (let px = 90; px < W; px += 520) {
    ctx.beginPath(); ctx.moveTo(px, sol); ctx.lineTo(px, sol - 600); ctx.stroke();
    ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(px, sol - 580);
    ctx.quadraticCurveTo(px + 260, sol - 520, px + 520, sol - 580); ctx.stroke(); ctx.lineWidth = 3;
  }
  /* palmiers */
  for (const p of plan.palmiers) {
    const c = nuit > 0.6 ? '#0b0d10' : teinte('#2f5a33', assombrir, [5, 8, 6]);
    ctx.strokeStyle = teinte('#6b5640', assombrir, [8, 6, 4]); ctx.lineWidth = 12;
    ctx.beginPath(); ctx.moveTo(p.x, sol); ctx.quadraticCurveTo(p.x + 30 * (p.s - 0.5), sol - p.h / 2, p.x + 18, sol - p.h); ctx.stroke();
    ctx.fillStyle = c;
    for (let i = 0; i < 9; i++) {
      const a = -Math.PI / 2 + (i - 4) * 0.38, L = 110 + 40 * Math.sin(i * 2.1 + p.s * 6);
      ctx.beginPath(); ctx.moveTo(p.x + 18, sol - p.h);
      ctx.quadraticCurveTo(p.x + 18 + Math.cos(a) * L * 0.6, sol - p.h + Math.sin(a) * L * 0.3 - 30,
        p.x + 18 + Math.cos(a) * L, sol - p.h + Math.sin(a) * L * 0.35 + 40);
      ctx.quadraticCurveTo(p.x + 18 + Math.cos(a) * L * 0.5, sol - p.h + 6, p.x + 18, sol - p.h + 8); ctx.fill();
    }
  }
  /* réverbères la nuit */
  if (nuit > 0.25) {
    for (let px = 300; px < W; px += 520) {
      const r = ctx.createRadialGradient(px, sol - 240, 4, px, sol - 240, 140);
      r.addColorStop(0, `rgba(255,190,110,${0.8 * nuit})`); r.addColorStop(1, 'rgba(255,170,90,0)');
      ctx.fillStyle = r; ctx.fillRect(px - 150, sol - 390, 300, 300);
    }
  }
  /* le voile : pluie, brume, harmattan */
  const voile = borner(e.pluie * 0.35 + e.brume * 0.5, 0, 0.7);
  if (voile > 0) { ctx.fillStyle = e.brume > e.pluie ? `rgba(236,222,196,${voile})` : `rgba(150,160,172,${voile * (1 - nuit * 0.6)})`; ctx.fillRect(0, 0, W, H); }
}

function peindreChaussee(ctx, W, H) {
  ctx.fillStyle = '#d8ccb6'; ctx.fillRect(0, 0, W, H * 0.18);                      /* trottoir pavé */
  ctx.strokeStyle = 'rgba(120,100,80,.35)'; ctx.lineWidth = 2;
  for (let x = 0; x < W; x += 32) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H * 0.18); ctx.stroke(); }
  for (let y = 0; y < H * 0.18; y += 22) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  ctx.fillStyle = '#a5522f'; ctx.fillRect(0, H * 0.18, W, H * 0.07);                 /* la latérite */
  ctx.fillStyle = '#4b4d50'; ctx.fillRect(0, H * 0.25, W, H * 0.6);                  /* la chaussée */
  const r = graine(7);
  for (let i = 0; i < 2600; i++) { ctx.fillStyle = `rgba(${r() < 0.5 ? '255,255,255' : '0,0,0'},${0.05 * r()})`; ctx.fillRect(r() * W, H * 0.25 + r() * H * 0.6, 3, 3); }
  ctx.fillStyle = 'rgba(240,235,220,.55)';
  for (let x = 0; x < W; x += 120) ctx.fillRect(x, H * 0.545, 60, 6);                 /* la ligne médiane, usée */
  ctx.fillStyle = '#a5522f'; ctx.fillRect(0, H * 0.85, W, H * 0.05);
  ctx.fillStyle = '#cfc2aa'; ctx.fillRect(0, H * 0.9, W, H * 0.1);
}

function dessinZem(ctx, W, H) {
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = '#1b1c1f';
  ctx.beginPath(); ctx.arc(W * 0.2, H * 0.8, H * 0.15, 0, 7); ctx.arc(W * 0.8, H * 0.8, H * 0.15, 0, 7); ctx.fill();
  ctx.fillStyle = '#2b2e33'; ctx.beginPath();
  ctx.moveTo(W * 0.15, H * 0.68); ctx.lineTo(W * 0.62, H * 0.6); ctx.lineTo(W * 0.86, H * 0.66); ctx.lineTo(W * 0.78, H * 0.78); ctx.lineTo(W * 0.25, H * 0.8); ctx.fill();
  ctx.fillStyle = '#e8c21c'; ctx.beginPath();                                      /* la chemise jaune du zémidjan */
  ctx.moveTo(W * 0.42, H * 0.6); ctx.lineTo(W * 0.46, H * 0.28); ctx.lineTo(W * 0.6, H * 0.28); ctx.lineTo(W * 0.62, H * 0.58); ctx.fill();
  ctx.fillStyle = '#3a2a20'; ctx.fillRect(W * 0.58, H * 0.36, W * 0.2, H * 0.06);   /* le bras vers le guidon */
  ctx.fillStyle = '#1e1e22'; ctx.beginPath(); ctx.arc(W * 0.53, H * 0.2, H * 0.09, 0, 7); ctx.fill();   /* casque */
  ctx.fillStyle = '#2d3a5c'; ctx.fillRect(W * 0.44, H * 0.58, W * 0.18, H * 0.1);   /* jambes */
  ctx.fillStyle = '#7d2c4a'; ctx.beginPath();                                      /* un passager, souvent */
  ctx.moveTo(W * 0.26, H * 0.6); ctx.lineTo(W * 0.3, H * 0.3); ctx.lineTo(W * 0.42, H * 0.3); ctx.lineTo(W * 0.42, H * 0.6); ctx.fill();
  ctx.fillStyle = '#1e1e22'; ctx.beginPath(); ctx.arc(W * 0.36, H * 0.22, H * 0.08, 0, 7); ctx.fill();
}

/* ---------- le ciel complet ---------- */
export function creerCiel(moteur, { facadeZ = 6, largeur = 16, lieu = COTONOU, relais = '/api/meteo' } = {}) {
  const { scene } = moteur;
  const q = moteur.qualite;
  const etat = { heure: maintenant(lieu), soleil: { elevation: 30, azimut: 0 }, jour: 1, nuit: 0, dore: 0,
    pluie: 0, orage: false, brume: 0, nuages: 0.3, temp: null, symbole: 'clearsky', meteoRecue: false, eclair: 0 };

  /* lumières du ciel */
  const hemi = new THREE.HemisphereLight(0xdfeaff, 0xcbb99a, 0.9);
  const soleil = new THREE.DirectionalLight(0xfff1dc, 1.4);
  soleil.target.position.set(0, 0, 0);
  scene.add(hemi, soleil, soleil.target);

  /* la rue : chaussée + façades peintes, au-delà de la vitrine */
  const groupe = new THREE.Group(); scene.add(groupe);
  const texRoute = texteCanvas(1024, 512, peindreChaussee);
  texRoute.wrapS = THREE.RepeatWrapping; texRoute.repeat.set(3, 1);
  const matRoute = new THREE.MeshStandardMaterial({ map: texRoute, roughness: 0.85 });
  const route = new THREE.Mesh(new THREE.PlaneGeometry(80, 14), matRoute);
  route.rotation.x = -Math.PI / 2; route.position.set(0, -0.02, facadeZ + 7); groupe.add(route);

  const toile = document.createElement('canvas'); toile.width = 2048; toile.height = 1024;
  const ctxRue = toile.getContext('2d');
  const texRue = new THREE.CanvasTexture(toile); texRue.colorSpace = THREE.SRGBColorSpace;
  const planRue = plan_de_rue(graine(229));
  const matFond = new THREE.MeshBasicMaterial({ map: texRue, toneMapped: false });
  /* reculée à 13 m (à 8 m, vue du trottoir, la rue paraissait collée au visage) ; la ligne du sol peinte tombe à y = 0 */
  const fond = new THREE.Mesh(new THREE.PlaneGeometry(64, 32), matFond);
  fond.position.set(0, 16 - 0.07 * 32, facadeZ + 13.5); fond.rotation.y = Math.PI; groupe.add(fond);
  let derniereCle = '';
  function repeindre() {
    const cle = [etat.jour, etat.dore, etat.pluie, etat.brume, etat.nuages].map(v => Math.round(v * 12)).join(',');
    if (cle === derniereCle) return;
    derniereCle = cle;
    peindreRue(ctxRue, 2048, 1024, etat, planRue);
    texRue.needsUpdate = true;
  }

  /* les zems qui passent */
  const texZem = texteCanvas(256, 180, dessinZem);
  const zems = [];
  for (let i = 0; i < 3; i++) {
    const t = texZem.clone(); t.needsUpdate = true;
    const mat = new THREE.MeshBasicMaterial({ map: t, transparent: true, alphaTest: 0.05, side: THREE.DoubleSide });
    const m = new THREE.Mesh(new THREE.PlaneGeometry(2.0, 1.4), mat);
    m.visible = false; groupe.add(m);
    zems.push({ m, mat, v: 0, actif: false });
  }
  let prochainZem = 2;

  /* la pluie */
  const N = q.pluie;
  const pos = new Float32Array(N * 6), vit = new Float32Array(N);
  const rndP = graine(11);
  for (let i = 0; i < N; i++) {
    const x = (rndP() - 0.5) * 30, y = rndP() * 8, z = facadeZ + 0.5 + rndP() * 8;
    pos.set([x, y, z, x + 0.05, y + 0.38, z], i * 6); vit[i] = 8 + rndP() * 4;
  }
  const geoPluie = new THREE.BufferGeometry(); geoPluie.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const matPluie = new THREE.LineBasicMaterial({ color: 0xc9d4e0, transparent: true, opacity: 0 });
  const pluie = new THREE.LineSegments(geoPluie, matPluie); pluie.frustumCulled = false; groupe.add(pluie);

  /* les gouttes sur la vitre */
  const texGouttes = texteCanvas(512, 512, (ctx, W, H) => {
    const r = graine(3);
    for (let i = 0; i < 240; i++) {
      const x = r() * W, y = r() * H, s = 1.5 + r() * 4.5;
      ctx.fillStyle = 'rgba(210,225,240,.35)'; ctx.beginPath(); ctx.ellipse(x, y, s * 0.8, s, 0, 0, 7); ctx.fill();
      ctx.fillStyle = 'rgba(255,255,255,.6)'; ctx.beginPath(); ctx.arc(x - s * 0.3, y - s * 0.3, s * 0.3, 0, 7); ctx.fill();
      if (r() < 0.12) { ctx.strokeStyle = 'rgba(210,225,240,.25)'; ctx.lineWidth = s * 0.6; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + (r() - 0.5) * 6, y + 30 + r() * 90); ctx.stroke(); }
    }
  });
  texGouttes.wrapS = texGouttes.wrapT = THREE.RepeatWrapping; texGouttes.repeat.set(5, 1.4);
  const matGouttes = new THREE.MeshBasicMaterial({ map: texGouttes, transparent: true, opacity: 0, depthWrite: false });
  const gouttes = new THREE.Mesh(new THREE.PlaneGeometry(largeur - 0.4, 3.3), matGouttes);
  gouttes.position.set(0, 1.95, facadeZ - 0.06); gouttes.rotation.y = Math.PI; scene.add(gouttes);

  /* ---------- mise à jour ---------- */
  const surEclair = [];
  let prochainEclair = 6, eclairT = -1;
  function calculerHeure() {
    etat.heure = maintenant(lieu);
    etat.soleil = positionSoleil(etat.heure.date, lieu.lat, lieu.lon);
    const el = etat.soleil.elevation;
    etat.jour = borner((el + 6) / 14, 0, 1);
    etat.nuit = 1 - etat.jour;
    etat.dore = el > -4 && el < 16 ? 1 - Math.abs(el - 5) / 11 : 0;
    etat.dore = borner(etat.dore, 0, 1) * (1 - etat.nuages * 0.6);
  }
  async function lireMeteo() {
    let m = null;
    try { const r = await fetch(relais, { cache: 'no-store' }); if (r.ok) m = await r.json(); } catch (e) { /* hors ligne : ciel clair */ }
    Object.assign(etat, interpreterMeteo(m, etat.heure.mois));
    etat.meteoRecue = !!m;
  }
  calculerHeure(); Object.assign(etat, interpreterMeteo(null, etat.heure.mois));
  const pret = lireMeteo();
  setInterval(lireMeteo, 10 * 60 * 1000);
  setInterval(calculerHeure, 30 * 1000);

  function maj(dt, t) {
    const el = etat.soleil.elevation * RAD, az = etat.soleil.azimut * RAD;
    const dir = new THREE.Vector3(-Math.sin(az) * Math.cos(el), Math.max(0.05, Math.sin(el)), Math.cos(az) * Math.cos(el)).normalize();
    soleil.position.copy(dir).multiplyScalar(30);
    const voile = 1 - etat.nuages * 0.55 - etat.pluie * 0.25;
    soleil.intensity = 1.6 * etat.jour * Math.max(0.15, voile);
    soleil.color.setRGB(1, melanger(0.95, 0.78, etat.dore), melanger(0.88, 0.6, etat.dore));
    hemi.intensity = melanger(0.22, 0.95, etat.jour) * (1 - etat.pluie * 0.25);
    hemi.color.setRGB(melanger(0.45, 0.88, etat.jour), melanger(0.5, 0.92, etat.jour), melanger(0.75, 1, etat.jour));
    repeindre();
    /* éclair */
    if (etat.orage) {
      prochainEclair -= dt;
      if (prochainEclair <= 0) { eclairT = 0; prochainEclair = 8 + Math.random() * 18; surEclair.forEach(f => f()); }
    }
    if (eclairT >= 0) {
      eclairT += dt;
      etat.eclair = eclairT < 0.08 || (eclairT > 0.16 && eclairT < 0.22) ? 1 : 0;
      if (eclairT > 0.4) { eclairT = -1; etat.eclair = 0; }
      hemi.intensity += etat.eclair * 3;
      matFond.color.setScalar(1 + etat.eclair * 1.5);
    } else matFond.color.setScalar(1);
    /* pluie */
    matPluie.opacity = etat.pluie * 0.55;
    pluie.visible = etat.pluie > 0.01;
    if (pluie.visible) {
      const n = Math.floor(N * borner(etat.pluie, 0.2, 1));
      for (let i = 0; i < N; i++) {
        const o = i * 6;
        if (i >= n) { pos[o + 1] = pos[o + 4] = -50; continue; }
        if (pos[o + 1] < -1) { pos[o + 1] = 7.5 + Math.random(); pos[o + 4] = pos[o + 1] + 0.38; }
        pos[o + 1] -= vit[i] * dt; pos[o + 4] -= vit[i] * dt;
      }
      geoPluie.attributes.position.needsUpdate = true;
    }
    matGouttes.opacity = etat.pluie * 0.7;
    if (etat.pluie > 0.01) texGouttes.offset.y -= dt * 0.03 * etat.pluie;
    matRoute.roughness = 0.85 - etat.pluie * 0.6;
    /* zems */
    prochainZem -= dt;
    if (prochainZem <= 0) {
      const z = zems.find(k => !k.actif);
      if (z) {
        const sens = Math.random() < 0.5 ? 1 : -1;
        z.actif = true; z.m.visible = true; z.v = sens * (6 + Math.random() * 4);
        z.m.position.set(-sens * 22, 0.72, facadeZ + (sens > 0 ? 3.4 : 5.2));
        /* vu depuis le salon, on regarde le dos du plan : l'image se lit à l'envers,
           donc on ne la retourne que pour les zems qui roulent vers -x */
        z.mat.map.repeat.x = sens > 0 ? 1 : -1; z.mat.map.offset.x = sens > 0 ? 0 : 1;
        z.mat.color.setScalar(melanger(0.3, 1, etat.jour));
      }
      prochainZem = (etat.nuit > 0.5 ? 7 : 2.5) + Math.random() * (etat.pluie > 0.5 ? 14 : 6);
    }
    for (const z of zems) {
      if (!z.actif) continue;
      z.m.position.x += z.v * dt;
      z.m.position.y = 0.72 + Math.sin(t * 9 + z.v) * 0.012;
      if (Math.abs(z.m.position.x) > 24) { z.actif = false; z.m.visible = false; }
    }
  }
  moteur.chaqueImage(maj);

  return { etat, pret, surEclair, hemi, soleil,
    /* « 14 h 32 · 29 °C · pluie » pour l'interface */
    libelle() {
      const h = etat.heure; const t = etat.temp != null ? ` · ${Math.round(etat.temp)} °C` : '';
      const m = etat.orage ? 'orage' : etat.pluie > 0.6 ? 'forte pluie' : etat.pluie > 0 ? 'pluie' :
        etat.brume > 0.4 ? 'brume' : etat.nuages > 0.75 ? 'couvert' : etat.nuit > 0.6 ? 'nuit claire' : 'soleil';
      return `${lieu.nom} · ${h.h} h ${String(h.m).padStart(2, '0')}${t} · ${m}`;
    } };
}

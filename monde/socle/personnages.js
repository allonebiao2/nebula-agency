/* LE MONDE · les personnages de la MAQUETTE.
   Des silhouettes de porcelaine, sans visage, comme les mannequins blancs
   d'Hillary. ⚠️ Elles tiennent la place des vrais personnages 3D (Hillary
   avec son accord écrit, les visiteuses générées) : vague 3. On ne donne pas
   de visage à une personne réelle sans elle, et un visage faux ferait pire
   qu'aucun visage.

   Repère d'un personnage : il regarde vers +z local. Tout est animé à la
   main (aucun squelette importé) : marche, souffle, regard, gestes. */
import { THREE, borner, angleVers, melanger } from './moteur.js';
import { matWax, ombreRonde } from './matieres.js';

export function capVersRotation(cap) { const c = cap * Math.PI / 180; return Math.atan2(Math.sin(c), -Math.cos(c)); }

const capsule = (r, l) => new THREE.CapsuleGeometry(r, l, 4, 10);
const POSES = {
  /* [haut du bras x, écart z, coude x] pour la gauche (G) et la droite (D) */
  repos:     { G: [0.02, 0.07, -0.12], D: [0.02, 0.07, -0.12] },
  telephone: { G: [0.02, 0.07, -0.12], D: [-0.55, 0.32, -2.35] },
  photo:     { G: [-1.2, -0.12, -0.75], D: [-1.2, -0.12, -0.75] },
  toucher:   { G: [0.02, 0.07, -0.12], D: [-0.8, 0.05, -0.35] },
  montrer:   { G: [0.0, 0.07, -0.2], D: [-1.15, 0.45, -0.18] },
  comptoir:  { G: [-0.45, 0.05, -1.25], D: [-0.45, 0.05, -1.25] },
  regarder:  { G: [-0.22, -0.18, -1.0], D: [-0.22, -0.18, -1.0] },
  croises:   { G: [-0.38, -0.25, -1.85], D: [-0.38, -0.25, -1.85] },
  saluer:    { G: [0.02, 0.07, -0.12], D: [-0.25, 2.3, -0.55] },
  assis:     { G: [-0.62, 0.0, -0.62], D: [-0.62, 0.0, -0.62] },
  fenetre:   { G: [-0.25, -0.15, -1.1], D: [-0.25, -0.15, -1.1] },
};

/* Les gestes de la parole, ajoutés à la pose :
   [épaule G avant, épaule G écart, coude G, épaule D avant, épaule D écart, coude D, buste penché, tête inclinée] */
const REPOS_PAROLE = [0, 0, 0, 0, 0, 0, 0, 0];
const GESTES_PAROLE = [
  [-0.35, 0.28, -0.85, -0.35, 0.28, -0.85, 0.05, 0.06],    /* bras ouverts : j'explique */
  [0, 0, 0, -0.6, 0.18, -1.15, 0.06, -0.05],               /* paume tendue vers toi */
  [0, 0, 0, -0.32, -0.38, -1.95, 0.02, 0.08],              /* la main sur le cœur */
  [-0.55, 0.08, -1.5, -0.1, 0, -0.3, 0.04, -0.06],         /* je compte sur mes doigts */
  [-0.28, -0.2, -1.4, -0.28, -0.2, -1.4, 0.03, 0],         /* mains jointes */
  [-0.12, 0.42, -0.55, -0.12, 0.42, -0.55, -0.02, 0.1],    /* haussement d'épaules */
];
/* poser une question : les deux paumes s'ouvrent vers l'autre, la tête s'incline */
const GESTES_QUESTION = [
  [-0.48, 0.22, -1.12, -0.48, 0.22, -1.12, 0.08, 0.14],
  [0, 0, 0, -0.62, 0.22, -1.05, 0.07, 0.12],
];
const PAR_TON = { question: GESTES_QUESTION, exclamation: [GESTES_PAROLE[0], GESTES_PAROLE[5], GESTES_PAROLE[1]], affirmation: GESTES_PAROLE };

export function creerPersonnage(d) {
  const s = (d.taille || 1.68) / 1.68;
  /* une vraie carnation est mate ; la porcelaine (sans d.peau) brille un peu */
  const peau = new THREE.MeshStandardMaterial({ color: d.peau ?? 0xefe8dc, roughness: d.peau ? 0.58 : 0.38 });
  const tissu = (v, rep = [1.4, 1.4]) => !v ? peau : v.wax ? matWax(v.wax, v.palette, rep) : new THREE.MeshStandardMaterial({ color: v.couleur, roughness: v.brillant ? 0.4 : 0.82 });
  const mHaut = tissu(d.haut), mBas = tissu(d.bas, [2, 2]), mJambes = d.jambes ? tissu(d.jambes) : peau;
  const mChaussure = new THREE.MeshStandardMaterial({ color: d.chaussures ?? 0x2a2420, roughness: 0.5 });
  const mCheveux = new THREE.MeshStandardMaterial({ color: 0x1c1512, roughness: 0.75 });

  const racine = new THREE.Group(); racine.name = d.nom;
  const corps = new THREE.Group(); corps.scale.setScalar(s); racine.add(corps);
  const bassin = new THREE.Group(); bassin.position.y = 0.93; corps.add(bassin);
  const maille = (g, m) => { const x = new THREE.Mesh(g, m); x.castShadow = false; return x; };

  function jambe(cote) {
    const hanche = new THREE.Group(); hanche.position.set(cote * 0.085, -0.02, 0); bassin.add(hanche);
    const cuisse = maille(capsule(0.062, 0.32), mJambes); cuisse.position.y = -0.22; hanche.add(cuisse);
    const genou = new THREE.Group(); genou.position.y = -0.45; hanche.add(genou);
    const tibia = maille(capsule(0.05, 0.3), d.jambesBas ? tissu(d.jambesBas) : mJambes); tibia.position.y = -0.2; genou.add(tibia);
    const pied = maille(new THREE.BoxGeometry(0.085, 0.06, 0.21), mChaussure); pied.position.set(0, -0.43, 0.04); genou.add(pied);
    return { hanche, genou };
  }
  const jG = jambe(1), jD = jambe(-1);

  const torse = new THREE.Group(); bassin.add(torse);
  const buste = maille(capsule(0.13, 0.3), mHaut); buste.scale.set(1.12, 1, 0.78); buste.position.y = 0.25; torse.add(buste);
  const cou = maille(new THREE.CylinderGeometry(0.045, 0.05, 0.1, 10), peau); cou.position.y = 0.5; torse.add(cou);
  const tete = new THREE.Group(); tete.position.y = 0.62; torse.add(tete);
  const crane = maille(new THREE.SphereGeometry(0.105, 24, 18), peau); crane.scale.set(0.92, 1.12, 1); tete.add(crane);

  /* coiffures et coiffes */
  if (d.coiffe === 'gele') {
    const m = tissu(d.coiffeTissu || d.haut, [1, 1]);
    const a = maille(new THREE.SphereGeometry(0.15, 20, 14), m); a.scale.set(1.25, 0.72, 1.05); a.position.set(0, 0.1, -0.01); tete.add(a);
    const b = maille(new THREE.SphereGeometry(0.15, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2), m); b.scale.set(1.5, 1.05, 0.55); b.position.set(0, 0.14, -0.06); b.rotation.x = -0.25; tete.add(b);
    const n = maille(new THREE.TorusGeometry(0.11, 0.035, 10, 24), m); n.rotation.x = Math.PI / 2 - 0.2; n.position.y = 0.04; tete.add(n);
  } else if (d.coiffe === 'tresses') {
    const c = maille(new THREE.SphereGeometry(0.112, 20, 14), mCheveux); c.scale.set(0.95, 1.08, 1.05); c.position.set(0, 0.012, -0.006); tete.add(c);
    const q = maille(new THREE.CylinderGeometry(0.035, 0.05, 0.12, 10), mCheveux); q.position.set(0, 0.15, -0.05); q.rotation.x = -0.4; tete.add(q);
    for (let i = 0; i < 9; i++) {
      const t = maille(new THREE.CylinderGeometry(0.009, 0.007, 0.48, 6), mCheveux);
      t.position.set((i - 4) * 0.018, -0.06, -0.12 - Math.abs(i - 4) * 0.004); t.rotation.x = 0.18; tete.add(t);
    }
  } else if (d.coiffe === 'chignon') {
    const c = maille(new THREE.SphereGeometry(0.11, 20, 14), mCheveux); c.scale.set(0.96, 1.05, 1.05); c.position.set(0, 0.015, -0.006); tete.add(c);
    const b = maille(new THREE.SphereGeometry(0.06, 14, 10), mCheveux); b.position.set(0, 0.11, -0.08); tete.add(b);
  } else {
    const c = maille(new THREE.SphereGeometry(0.112, 20, 14), mCheveux); c.scale.set(0.97, 1.06, 1.04); c.position.set(0, 0.02, -0.004); tete.add(c);
  }
  if (d.boucles) for (const c of [1, -1]) { const o = maille(new THREE.TorusGeometry(0.018, 0.004, 6, 16), new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 1, roughness: 0.25 })); o.position.set(c * 0.098, -0.04, 0); o.rotation.y = Math.PI / 2; tete.add(o); }

  function bras(cote) {
    const epaule = new THREE.Group(); epaule.position.set(cote * 0.19, 0.43, 0); torse.add(epaule);
    const mB = d.manches === false ? peau : mHaut;
    const haut = maille(capsule(d.amples ? 0.07 : 0.043, 0.21), mB); haut.position.y = -0.14; epaule.add(haut);
    const coude = new THREE.Group(); coude.position.y = -0.28; epaule.add(coude);
    const avant = maille(capsule(d.amples ? 0.062 : 0.037, 0.19), d.manchesLongues ? mB : peau); avant.position.y = -0.13; coude.add(avant);
    const main = maille(new THREE.SphereGeometry(0.043, 12, 10), peau); main.position.y = -0.27; main.scale.set(0.8, 1.1, 0.6); coude.add(main);
    return { epaule, coude, main };
  }
  const bG = bras(1), bD = bras(-1);

  /* le vêtement du bas */
  const tour = (profil, m, y0, parent) => {
    const pts = profil.map(([r, y]) => new THREE.Vector2(r, y));
    const g = new THREE.LatheGeometry(pts, 36);
    const x = maille(g, m); x.position.y = y0; parent.add(x); return x;
  };
  if (d.bas && d.bas.type === 'jupe') tour([[0.14, 0.06], [0.16, 0], [0.2, -0.25], [0.26, -0.55], [d.bas.ampleur || 0.34, -0.86], [0.001, -0.86]], mBas, 0, bassin);
  if (d.bas && d.bas.type === 'boubou') tour([[0.18, 0.47], [0.24, 0.36], [0.27, 0.0], [0.34, -0.5], [0.42, -0.86], [0.001, -0.86]], mBas, 0, torse);
  if (d.bas && d.bas.type === 'manteau') tour([[0.17, 0.46], [0.2, 0.3], [0.2, 0.0], [0.25, -0.28], [0.29, -0.46], [0.001, -0.46]], mBas, 0, torse);
  const ampleJupe = d.bas && (d.bas.type === 'jupe' || d.bas.type === 'boubou');

  /* accessoires */
  const tel = maille(new THREE.BoxGeometry(0.075, 0.15, 0.012), new THREE.MeshStandardMaterial({ color: d.telephone || 0x111111, roughness: 0.3 }));
  tel.position.set(0, -0.3, 0.03); tel.visible = false; bD.coude.add(tel);
  if (d.sac) {
    const sac = maille(new THREE.BoxGeometry(0.3, 0.26, 0.1), new THREE.MeshStandardMaterial({ color: d.sac, roughness: 0.55 }));
    sac.position.set(0.24, 0.1, 0); torse.add(sac);
  }

  const ombre = ombreRonde(0.38, 0.32); racine.add(ombre);
  const hitbox = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.32, 1.78, 10),
    new THREE.MeshBasicMaterial({ colorWrite: false, depthWrite: false, transparent: true, opacity: 0 }));
  hitbox.position.y = 0.89; racine.add(hitbox);

  /* ---------- l'animation ---------- */
  const st = { vitesse: 0, marcheW: 0, assis: false, assisW: 0, geste: 'repos', poseActuelle: JSON.parse(JSON.stringify(POSES.repos)),
    parle: false, parleW: 0, regard: null, teteLacet: 0, teteTangage: 0, phase: Math.random() * 6, respir: Math.random() * 6,
    rotVisee: null, telephone: false, prochainGeste: 0, gesteParole: 0, offParole: [...REPOS_PAROLE], ecoute: false, hoche: 0 };
  const tmp = new THREE.Vector3(), inv = new THREE.Matrix4();

  function maj(dt, t) {
    const k = (v) => 1 - Math.exp(-dt * v);
    st.marcheW += ((st.vitesse > 0.05 ? 1 : 0) - st.marcheW) * k(7);
    st.assisW += ((st.assis ? 1 : 0) - st.assisW) * k(3.5);
    st.parleW += ((st.parle ? 1 : 0) - st.parleW) * k(6);
    st.phase += dt * Math.max(st.vitesse, 0) / 0.62 * Math.PI;
    if (st.rotVisee != null) racine.rotation.y += angleVers(racine.rotation.y, st.rotVisee) * k(5);

    const w = st.marcheW, sw = Math.sin(st.phase), amp = ampleJupe ? 0.22 : 0.42;
    for (const [j, sgn] of [[jG, 1], [jD, -1]]) {
      j.hanche.rotation.x = melanger(sgn * sw * amp * w, -1.5, st.assisW);
      j.genou.rotation.x = melanger(Math.max(0, -Math.cos(st.phase + (sgn > 0 ? 0 : Math.PI))) * 0.55 * w + 0.03, 1.5, st.assisW);
    }
    bassin.position.y = melanger(0.93 + Math.abs(Math.cos(st.phase)) * 0.022 * w, 0.5, st.assisW);
    bassin.rotation.z = Math.sin(st.phase) * 0.035 * w;
    torse.rotation.y = -Math.sin(st.phase) * 0.06 * w;
    torse.scale.y = 1 + Math.sin(t * 1.7 + st.respir) * 0.007;

    /* la pose des bras : on glisse vers la pose du geste, et la marche balance par-dessus */
    const cible = POSES[st.assisW > 0.5 && st.geste === 'repos' ? 'assis' : st.geste] || POSES.repos;
    for (const c of ['G', 'D']) for (let i = 0; i < 3; i++) st.poseActuelle[c][i] += (cible[c][i] - st.poseActuelle[c][i]) * k(5);
    const balance = (st.geste === 'repos' ? 1 : 0.15) * w;
    const pG = st.poseActuelle.G, pD = st.poseActuelle.D;
    bG.epaule.rotation.set(pG[0] - sw * 0.38 * balance, 0, pG[1]);
    bD.epaule.rotation.set(pD[0] + sw * 0.38 * balance, 0, -pD[1]);
    bG.coude.rotation.x = pG[2] - 0.15 * balance;
    bD.coude.rotation.x = pD[2] - 0.15 * balance;
    if (st.geste === 'saluer') bD.coude.rotation.z = Math.sin(t * 9) * 0.35;
    else bD.coude.rotation.z *= 0.9;
    /* ⚠️ ON PARLE AVEC LE CORPS (Mongazi : « ce sont leurs corps mêmes qui bougent, pas des
       images »). Celle qui parle enchaîne des gestes de parole, se penche, incline la tête ;
       celle qui écoute hoche la tête. Avec les vrais personnages (vague 3), des animations
       capturées et les lèvres synchronisées sur la voix prendront le relais. */
    const jeu = PAR_TON[st.ton] || GESTES_PAROLE;
    if (st.parle && t > st.prochainGeste) {
      st.prochainGeste = t + 1.3 + Math.random() * 1.3;
      let k = Math.floor(Math.random() * jeu.length); if (k === st.gesteParole && jeu.length > 1) k = (k + 1) % jeu.length;
      st.gesteParole = k;
    }
    const cibleP = st.parle && st.geste === 'repos' ? jeu[st.gesteParole % jeu.length] : REPOS_PAROLE;
    for (let i = 0; i < 8; i++) st.offParole[i] += (cibleP[i] - st.offParole[i]) * k(3.8);
    const o = st.offParole, vie = Math.sin(t * 2.3) * 0.08;
    bG.epaule.rotation.x += o[0] + vie * st.parleW; bG.epaule.rotation.z += o[1];
    bG.coude.rotation.x += o[2];
    bD.epaule.rotation.x += o[3] - vie * st.parleW; bD.epaule.rotation.z -= o[4];
    bD.coude.rotation.x += o[5] + Math.sin(t * 3.1) * 0.12 * st.parleW;
    torse.rotation.x = o[6];
    if (st.ecoute && !st.parle) st.hoche = Math.max(0, Math.sin(t * 1.9 + st.respir)) ** 6;
    else st.hoche *= 0.9;
    tel.visible = st.telephone || st.geste === 'telephone' || st.geste === 'photo';

    /* le regard */
    let lacetVise = 0, tangageVise = 0;
    if (st.regard) {
      racine.updateMatrixWorld(); inv.copy(racine.matrixWorld).invert();
      tmp.copy(st.regard).applyMatrix4(inv);
      lacetVise = borner(Math.atan2(tmp.x, tmp.z), -1.05, 1.05);
      tangageVise = borner(-Math.atan2(tmp.y - 1.55, Math.hypot(tmp.x, tmp.z)), -0.35, 0.35);
    } else {
      lacetVise = Math.sin(t * 0.31 + st.respir) * 0.25 * (1 - w);
    }
    st.teteLacet += (lacetVise - st.teteLacet) * k(4);
    st.teteTangage += (tangageVise - st.teteTangage) * k(4);
    tete.rotation.set(st.teteTangage + Math.sin(t * 6.5) * 0.035 * st.parleW + st.hoche * 0.16, st.teteLacet,
      st.offParole[7] + Math.sin(t * 0.9 + st.respir) * 0.05 * st.parleW);
    torse.rotation.y += st.teteLacet * 0.22;
  }

  return {
    nom: d.nom, racine, tete, hitbox, st,
    set vitesse(v) { st.vitesse = v; },
    geste(nom) { st.geste = POSES[nom] ? nom : 'repos'; },
    assis(v) { st.assis = v; },
    /* le ton change le geste : une question ouvre les paumes, une exclamation ouvre les bras */
    parler(v, ton = 'affirmation') { st.parle = v; st.ton = ton; if (v) { st.prochainGeste = 0; st.ecoute = false; } },
    ecouter(v) { st.ecoute = v; },
    telephone(v) { st.telephone = v; },
    regarder(v3) { st.regard = v3 ? v3.clone() : null; },
    tourner(rotY) { st.rotVisee = rotY; },
    tournerVers(p) { const dx = p.x - racine.position.x, dz = p.z - racine.position.z; if (Math.hypot(dx, dz) > 0.01) st.rotVisee = Math.atan2(dx, dz); },
    positionTete(v = new THREE.Vector3()) { tete.getWorldPosition(v); return v; },
    maj,
  };
}

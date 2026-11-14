/* LE MONDE · se déplacer en « point & click », regarder comme dans Street View.
   On ne marche jamais au clavier : on TOUCHE un point lumineux, un objet ou le
   sol, et la caméra y marche seule, le long des passages du plan (jamais à
   travers un podium). On fait glisser le doigt pour regarder partout.

   Convention du plan : le « cap » vaut 0 en regardant le fond (-z), 90 vers
   la droite (+x). La caméra a donc un lacet = -cap. */
import { THREE, doux, borner, angleVers, rad } from './moteur.js';

export function creerGraphe(plan) {
  const noeuds = {};
  for (const p of plan.points) noeuds[p.id] = { ...p, voisins: [] };
  for (const p of plan.passages) noeuds[p.id] = { ...p, voisins: [], passage: true };
  for (const [a, b] of plan.liens) {
    if (!noeuds[a] || !noeuds[b]) throw new Error(`lien vers un point inconnu : ${a} ↔ ${b}`);
    noeuds[a].voisins.push(b); noeuds[b].voisins.push(a);
  }
  const d = (a, b) => Math.hypot(noeuds[a].x - noeuds[b].x, noeuds[a].z - noeuds[b].z);
  function chemin(depart, arrivee) {
    if (depart === arrivee) return [depart];
    const dist = {}, prec = {}, vus = new Set();
    for (const k in noeuds) dist[k] = Infinity;
    dist[depart] = 0;
    while (true) {
      let u = null;
      for (const k in noeuds) if (!vus.has(k) && (u === null || dist[k] < dist[u])) u = k;
      if (u === null || dist[u] === Infinity) return null;
      if (u === arrivee) break;
      vus.add(u);
      for (const v of noeuds[u].voisins) {
        const nd = dist[u] + d(u, v);
        if (nd < dist[v]) { dist[v] = nd; prec[v] = u; }
      }
    }
    const out = [arrivee]; let c = arrivee;
    while (c !== depart) { c = prec[c]; out.unshift(c); }
    return out;
  }
  function plusProche(x, z, filtre = () => true) {
    let best = null, bd = Infinity;
    for (const k in noeuds) {
      if (!filtre(noeuds[k])) continue;
      const dd = Math.hypot(noeuds[k].x - x, noeuds[k].z - z);
      if (dd < bd) { bd = dd; best = k; }
    }
    return best;
  }
  return { noeuds, chemin, plusProche, d };
}

function faisceau() {
  const c = document.createElement('canvas'); c.width = 4; c.height = 128;
  const g = c.getContext('2d'); const gr = g.createLinearGradient(0, 0, 0, 128);
  gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(1, 'rgba(255,255,255,1)');
  g.fillStyle = gr; g.fillRect(0, 0, 4, 128);
  const t = new THREE.CanvasTexture(c); return t;
}

/* P1 (référence) : les yeux à 1,52 m, 15 à 20 cm sous ceux des personnages : on lève à peine les yeux vers Afi
   (1,71 m) et Hillary (1,68 m), on est à hauteur de Maman Sènami (1,62 m), on ne domine personne */
export function creerDeplacement(moteur, graphe, { depart = 'entree', hauteur = 1.52, vitesse = 1.45,
  couleur = 0xe6007e, calque } = {}) {
  const { camera, scene, renderer } = moteur;
  const toile = renderer.domElement;
  const n0 = graphe.noeuds[depart];
  const pos = new THREE.Vector3(n0.x, hauteur, n0.z);
  let lacet = -rad(n0.cap || 0), tangage = -0.04, lacetVise = lacet, tangageVise = tangage;
  let roulis = 0;
  let noeud = depart, marche = null, bloque = false, dernierGlisser = -10, fovBase = null, cinema = 0, cinemaVise = 0, fovCadre = null, suivi = null;
  const surArrivee = [], surPas = [], surToucher = [], surDepart = [];
  let enFondu = false;
  const LONG_TRAJET = 8, reduit = matchMedia('(prefers-reduced-motion: reduce)').matches;
  /* P10 : le voile noir (0,35 s pour descendre, le saut, 0,45 s pour remonter : 0,8 s comme la référence) */
  const voile = calque ? (() => { const v = document.createElement('div'); v.className = 'fondu-noir'; v.setAttribute('aria-hidden', 'true');
    v.style.cssText = 'position:fixed;inset:0;background:#000;opacity:0;pointer-events:none;transition:opacity .35s ease-in;z-index:0';
    calque.prepend(v); return v; })() : null;
  /* le saut n'a lieu qu'une fois l'écran NOIR (fin de la transition), pas au bout d'un temps fixe : sur un téléphone
     occupé, 360 ms pouvaient passer sans qu'une seule image du voile soit peinte, et l'on voyait la caméra sauter
     (vu au QC le 2026-11-14). Filet : 700 ms si la transition ne se termine jamais (onglet caché, image figée). */
  const fondu = voile ? (auMilieu) => {
    voile.style.transition = 'opacity .35s ease-in'; voile.style.opacity = '1'; voile.style.pointerEvents = 'auto';
    let fait = false;
    const sauter = (e) => {
      if (fait || (e && e.propertyName !== 'opacity')) return;
      fait = true; voile.removeEventListener('transitionend', sauter); clearTimeout(filet);
      auMilieu(); requestAnimationFrame(() => { voile.style.transition = 'opacity .45s ease-out'; voile.style.opacity = '0'; voile.style.pointerEvents = 'none'; });
    };
    voile.addEventListener('transitionend', sauter);
    const filet = setTimeout(sauter, 700);
  } : null;
  const interactifs = [];

  /* ---------- les points lumineux ---------- */
  const tex = faisceau();
  const marqueurs = {};
  const geoAnneau = new THREE.RingGeometry(0.24, 0.285, 48);
  const geoDisque = new THREE.CircleGeometry(0.24, 48);
  const geoFaisceau = new THREE.CylinderGeometry(0.24, 0.24, 1.1, 32, 1, true);
  for (const id in graphe.noeuds) {
    const p = graphe.noeuds[id];
    if (p.passage) continue;
    const g = new THREE.Group(); g.position.set(p.x, 0.012, p.z);
    const mA = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.9, depthWrite: false, toneMapped: false });
    const anneau = new THREE.Mesh(geoAnneau, mA); anneau.rotation.x = -Math.PI / 2;
    const mD = new THREE.MeshBasicMaterial({ color: 0xffd9a8, transparent: true, opacity: 0.25, depthWrite: false, toneMapped: false });
    const disque = new THREE.Mesh(geoDisque, mD); disque.rotation.x = -Math.PI / 2; disque.position.y = -0.002;
    const mF = new THREE.MeshBasicMaterial({ color: couleur, map: tex, transparent: true, opacity: 0.22, depthWrite: false,
      side: THREE.DoubleSide, blending: THREE.AdditiveBlending, toneMapped: false });
    const f = new THREE.Mesh(geoFaisceau, mF); f.position.y = 0.55;
    /* ⚠️ plus de colonne lumineuse : c'était un décor d'interface dans la scène (revue Impeccable du 2026-11-12) */
    f.visible = false;
    g.add(anneau, disque, f); scene.add(g);
    const cible = { type: 'point', id };
    for (const m of [anneau, disque, f]) { m.userData.cible = cible; interactifs.push(m); }
    let etiquette = null;
    if (calque) {
      etiquette = document.createElement('button');
      etiquette.className = 'point-etiquette'; etiquette.type = 'button';
      etiquette.innerHTML = `<span>${p.nom}</span>`;
      etiquette.addEventListener('click', (e) => { e.stopPropagation(); allerA(id); });
      calque.appendChild(etiquette);
    }
    marqueurs[id] = { g, mA, mD, mF, etiquette, p };
  }

  /* ---------- marcher ---------- */
  function allerA(id, { regard = null, puis = null, sansChemin = false, fin = null } = {}) {
    if ((bloque && !puis) || enFondu) return false;
    const cibleN = graphe.noeuds[id];
    if (!cibleN) return false;
    let ids = sansChemin ? [id] : graphe.chemin(noeud, id);
    if (!ids) return false;
    const pts = [pos.clone().setY(0)];
    for (const k of ids) {
      const n = graphe.noeuds[k];
      if (Math.hypot(n.x - pos.x, n.z - pos.z) < 0.05) continue;
      pts.push(new THREE.Vector3(n.x, 0, n.z));
    }
    /* un dernier pas hors du graphe : tout près de la personne qu'on va voir */
    if (fin && fin.distanceTo(pts[pts.length - 1]) > 0.15) pts.push(new THREE.Vector3(fin.x, 0, fin.z));
    const capFinal = regard instanceof THREE.Vector3 ? null : (regard != null ? regard : (cibleN.cap != null ? cibleN.cap : null));
    if (pts.length === 1) {   /* déjà sur place : on tourne seulement */
      noeud = id; tournerVers(regard instanceof THREE.Vector3 ? regard : null, capFinal);
      surArrivee.forEach(f => f(id)); if (puis) puis(); return true;
    }
    const courbe = pts.length === 2 ? new THREE.LineCurve3(pts[0], pts[1]) : new THREE.CatmullRomCurve3(pts, false, 'centripetal', 0.5);
    const L = courbe.getLength();
    const prof = profil(L);
    /* P10 (référence) : un LONG trajet se coupe d'un fondu au noir de 0,8 s (une ellipse, comme le film), sauf
       pendant une conversation et pour qui a demandé moins d'animations ; la marche reste pour les pas courts */
    if (L > LONG_TRAJET && fondu && !bloque && !reduit) {
      /* ⚠️ la marche en cours s'arrête net : sinon elle continue sous le voile et ramène la caméra en arrière */
      marche = null; enFondu = true;
      surDepart.forEach(f => f(id));
      fondu(() => {
        enFondu = false;
        const fin = courbe.getPointAt(1), avant = courbe.getPointAt(0.97);
        pos.x = fin.x; pos.z = fin.z; pos.y = hauteur; roulis = 0; noeud = id;
        lacet = lacetVise = Math.atan2(-(fin.x - avant.x), -(fin.z - avant.z));
        tournerVers(regard instanceof THREE.Vector3 ? regard : null, capFinal);
        lacet = lacetVise; tangage = tangageVise;
        surArrivee.forEach(f => f(id)); if (puis) puis();
      });
      return true;
    }
    marche = { courbe, L, t: 0, duree: prof.duree, prof, id, regard, capFinal, puis, pasPrec: 0 };
    surDepart.forEach(f => f(id));
    return true;
  }
  /* P4 (référence) : une vitesse de CROISIÈRE constante, un départ en 0,3 s et un arrêt en 0,4 s (avant : un
     cosinus sur tout le trajet, la vitesse variait sans cesse jusqu'à 2,3 m/s, et la cadence des pas avec elle).
     Un trajet trop court pour atteindre la croisière fait un triangle à la même accélération. */
  const T_DEPART = 0.3, T_ARRET = 0.4;
  function profil(L) {
    const v = Math.min(vitesse, 2 * L / (T_DEPART + T_ARRET));
    const croisiere = Math.max(0, (L - v * (T_DEPART + T_ARRET) / 2) / v);
    const duree = T_DEPART + croisiere + T_ARRET;
    return { L, v, croisiere, duree,
      parcouru(t) {
        if (t <= 0) return 0;
        if (t < T_DEPART) return 0.5 * v / T_DEPART * t * t;
        if (t < T_DEPART + croisiere) return v * T_DEPART / 2 + v * (t - T_DEPART);
        const reste = Math.max(0, duree - t); return L - 0.5 * v / T_ARRET * reste * reste;
      } };
  }
  function tournerVers(point, cap) {
    if (point) { lacetVise = Math.atan2(-(point.x - pos.x), -(point.z - pos.z)); tangageVise = Math.atan2(point.y - hauteur, Math.hypot(point.x - pos.x, point.z - pos.z)) * 0.8; }
    else if (cap != null) { lacetVise = -rad(cap); tangageVise = -0.04; }
    lacetVise = lacet + angleVers(lacet, lacetVise);
  }

  /* ---------- regarder : glisser comme dans Street View ---------- */
  let appui = null, elan = { x: 0, y: 0 };
  toile.addEventListener('pointerdown', (e) => {
    appui = { x: e.clientX, y: e.clientY, t: performance.now(), glisse: false, id: e.pointerId };
    elan = { x: 0, y: 0 };
  });
  addEventListener('pointermove', (e) => {
    if (!appui || e.pointerId !== appui.id) { survol(e); return; }
    const dx = e.clientX - appui.x, dy = e.clientY - appui.y;
    if (!appui.glisse && Math.hypot(dx, dy) > 7) { appui.glisse = true; try { toile.setPointerCapture(e.pointerId); } catch (_) {} }
    if (appui.glisse) {
      /* ⚠️ movementX vaut 0 au doigt sur plusieurs navigateurs : on calcule l'écart nous-mêmes */
      const mx = e.clientX - (appui.lx ?? appui.x), my = e.clientY - (appui.ly ?? appui.y);
      appui.lx = e.clientX; appui.ly = e.clientY;
      const k = rad(camera.fov) * camera.aspect / toile.clientWidth * 0.95;
      lacet += mx * k; tangage += my * k;
      elan = { x: mx * k, y: my * k };
      tangage = borner(tangage, -0.62, 0.5); lacetVise = lacet; tangageVise = tangage;
      dernierGlisser = moteur.temps();
    }
  });
  addEventListener('pointerup', (e) => {
    if (!appui || e.pointerId !== appui.id) return;
    const a = appui; appui = null;
    if (!a.glisse && performance.now() - a.t < 600) toucher(e.clientX, e.clientY);
  });
  addEventListener('keydown', (e) => {
    if (e.target && /INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return;
    if (e.key === 'ArrowLeft') { lacetVise += 0.35; }
    if (e.key === 'ArrowRight') { lacetVise -= 0.35; }
    if (e.key === 'ArrowUp') { tangageVise = borner(tangageVise + 0.15, -0.62, 0.5); }
    if (e.key === 'ArrowDown') { tangageVise = borner(tangageVise - 0.15, -0.62, 0.5); }
  });

  const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
  function viser(x, y) {
    const r = toile.getBoundingClientRect();
    ndc.set(((x - r.left) / r.width) * 2 - 1, -((y - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(ndc, camera);
    const hits = ray.intersectObjects(interactifs.filter(o => o.visible !== false && visibleDansArbre(o)), false);
    return hits.length ? hits[0] : null;
  }
  function visibleDansArbre(o) { for (let x = o; x; x = x.parent) if (x.visible === false) return false; return true; }
  let survolActuel = null;
  function survol(e) {
    if (e.pointerType !== 'mouse') return;
    const h = viser(e.clientX, e.clientY);
    const c = h ? h.object.userData.cible : null;
    toile.style.cursor = c ? 'pointer' : 'grab';
    if (c !== survolActuel) { survolActuel = c; deplacement.surSurvol.forEach(f => f(c)); }
  }
  function toucher(x, y) {
    const h = viser(x, y);
    if (h) {
      const c = h.object.userData.cible;
      if (c.type === 'point') { if (!bloque) allerA(c.id); return; }
      for (const f of surToucher) if (f(c, h) === true) return;
      return;
    }
    if (bloque) return;
    /* le sol : on va au point de passage le plus proche, et on regarde là où l'on a touché */
    const sol = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0), p = new THREE.Vector3();
    if (ray.ray.intersectPlane(sol, p) && p.distanceTo(pos) < 18) {
      const k = graphe.plusProche(p.x, p.z);
      if (k && k !== noeud) allerA(k, { regard: new THREE.Vector3(p.x, 1.2, p.z) });
      else tournerVers(new THREE.Vector3(p.x, 1.2, p.z));
    }
  }

  /* ---------- chaque image ---------- */
  const proj = new THREE.Vector3();
  const tailleToile = { w: toile.clientWidth, h: toile.clientHeight };
  addEventListener('resize', () => { tailleToile.w = toile.clientWidth; tailleToile.h = toile.clientHeight; });
  moteur.chaqueImage((dt, t) => {
    if (fovBase === null) fovBase = camera.fov;
    if (marche) {
      marche.t += dt;
      const u = marche.L > 0 ? Math.min(1, marche.prof.parcouru(marche.t) / marche.L) : 1;
      const p = marche.courbe.getPointAt(Math.min(u, 1));
      pos.x = p.x; pos.z = p.z;
      const dist = u * marche.L;
      /* ⚠️ un pas tous les 0,68 m (≈ 2,1 pas/s à 1,45 m/s) : la tête descend À CHAQUE PAS et
         le son tombe au même instant ; l'ancien réglage (0,39 m) faisait 3,7 pas/s, désaccordés */
      const enveloppe = Math.sin(Math.PI * Math.min(u, 1));
      pos.y = hauteur - Math.abs(Math.sin(dist * Math.PI / 0.68)) * 0.022 * enveloppe;
      roulis = Math.sin(dist * Math.PI / 0.68) * 0.006 * enveloppe;
      const pas = Math.floor(dist / 0.68);
      if (pas !== marche.pasPrec) { marche.pasPrec = pas; surPas.forEach(f => f()); }
      if (t - dernierGlisser > 1.2) {
        const devant = marche.courbe.getPointAt(Math.min(1, u + 0.08));
        if (u < 0.82 && devant.distanceTo(p) > 0.02) {
          const vise = Math.atan2(-(devant.x - p.x), -(devant.z - p.z));
          lacetVise = lacet + angleVers(lacet, vise); tangageVise = -0.05;
        } else if (marche.capFinal != null || marche.regard instanceof THREE.Vector3) {
          tournerVers(marche.regard instanceof THREE.Vector3 ? marche.regard : null, marche.capFinal);
        }
      }
      if (marche.t >= marche.duree) {
        const m = marche; marche = null; noeud = m.id; pos.y = hauteur; roulis = 0;
        tournerVers(m.regard instanceof THREE.Vector3 ? m.regard : null, m.capFinal);
        surArrivee.forEach(f => f(m.id));
        if (m.puis) m.puis();
      }
    }
    /* en conversation, la caméra SUIT celle qui parle à chaque image. ⚠️ La viser une seule fois ne
       suffisait pas : selon le trajet, une orientation arrivée après coup la laissait cadrée sur les
       hanches d'Afi, la tête coupée (capture du 2026-11-13, tangage −0,47 au lieu de −0,20) */
    if (suivi && !marche && !appui) { const cible = suivi(); if (cible) tournerVers(cible); }
    if (!appui) {
      lacet += elan.x; tangage = borner(tangage + elan.y, -0.62, 0.5);
      if (Math.abs(elan.x) + Math.abs(elan.y) > 1e-5) { lacetVise = lacet; tangageVise = tangage; }
      elan.x *= 0.88; elan.y *= 0.88;
      const k = 1 - Math.exp(-dt * 5.5);
      lacet += (lacetVise - lacet) * k; tangage += (tangageVise - tangage) * k;
    }
    camera.position.copy(pos);
    /* un souffle de caméra à l'épaule, mesuré sur la référence (0,1 à 0,3 px au repos) : la vue vit */
    const souffle = marche ? 0 : 1;
    camera.rotation.set(tangage + souffle * 0.0016 * Math.sin(t * 0.83), lacet + souffle * 0.0013 * Math.sin(t * 0.61 + 1.7), roulis + souffle * 0.0008 * Math.sin(t * 0.47));
    cinema += (cinemaVise - cinema) * (1 - Math.exp(-dt * 3));
    /* en conversation, le cadre se resserre jusqu'à « fovCadre » (cadrage de celle qui parle), sinon de 8° */
    const baseFov = camera.userData.fovBase || fovBase || camera.fov;
    camera.fov = baseFov - cinema * (fovCadre != null ? Math.max(4, baseFov - fovCadre) : 8); camera.updateProjectionMatrix();
    /* les points : ils respirent, et celui où l'on se tient s'efface.
       ⚠️ Seuls les DEUX plus proches portent leur nom : nommer tous les points visibles
       empilait six ou sept étiquettes, dont une sur la robe exposée (vu le 2026-11-12). */
    const proches = Object.keys(marqueurs).filter(id => marqueurs[id].etiquette && !(id === noeud && !marche))
      .map(id => [id, Math.hypot(marqueurs[id].p.x - pos.x, marqueurs[id].p.z - pos.z)])
      .sort((x, y) => x[1] - y[1]).slice(0, 1).map(x => x[0]);   /* un seul nom de lieu à la fois (moins d'interface, 2026-11-13) */
    for (const id in marqueurs) {
      const m = marqueurs[id];
      const ici = id === noeud && !marche;
      const d = Math.hypot(m.p.x - pos.x, m.p.z - pos.z);
      const a = ici || bloque ? 0 : borner((d - 0.6) / 1.5, 0, 1);
      const pulse = 0.75 + 0.25 * Math.sin(t * 2.6 + m.p.x);
      m.mA.opacity = 0.34 * a; m.mD.opacity = 0.1 * a; m.mF.opacity = 0;   /* fixe : plus de pulsation décorative (DESIGN.md) */
      m.g.visible = a > 0.01;
      if (m.etiquette) {
        proj.set(m.p.x, 0.55, m.p.z).project(camera);
        const vis = proches.includes(id) && a > 0.3 && proj.z < 1 && Math.abs(proj.x) < 1.05 && Math.abs(proj.y) < 1.05 && d < 13;
        /* ⚠️ R14 : n'écrire que ce qui change, et mesurer la largeur UNE fois (son texte ne change pas) ; la taille de
           la toile est lue une fois par image, pas une fois par étiquette (lectures forcées de mise en page) */
        const op = vis ? String(Math.round(Math.min(1, a) * 50) / 50) : '0';
        if (m.op !== op) { m.etiquette.style.opacity = op; m.op = op; }
        if (m.pe !== vis) { m.etiquette.style.pointerEvents = vis ? 'auto' : 'none'; m.pe = vis; }
        /* l'étiquette reste DANS l'écran : bornée à 8 px des bords (revue Impeccable du 2026-11-12) */
        if (vis) {
          if (!m.demi) m.demi = (m.etiquette.offsetWidth || 0) / 2;
          const demi = m.demi || 60, W = tailleToile.w;
          const x = Math.min(W - demi - 8, Math.max(demi + 8, (proj.x * 0.5 + 0.5) * W));
          const tr = `translate(${Math.round(x)}px, ${Math.round((-proj.y * 0.5 + 0.5) * tailleToile.h)}px) translate(-50%, -100%)`;
          if (m.tr !== tr) { m.etiquette.style.transform = tr; m.tr = tr; }
        }
      }
    }
  });

  const deplacement = {
    allerA, tournerVers, graphe, interactifs, surArrivee, surPas, surToucher, surDepart, surSurvol: [],
    get position() { return pos; }, get noeud() { return noeud; }, get enMarche() { return !!marche || enFondu; },
    get camera() { return camera; },
    get lacet() { return lacet; },
    ajouterInteractif(objet, cible) { objet.traverse(o => { if (o.isMesh) { o.userData.cible = cible; interactifs.push(o); } }); },
    bloquer(v) { bloque = v; },
    cinema(v) { cinemaVise = v ? 1 : 0; if (!v) { fovCadre = null; suivi = null; moteur.flou && moteur.flou(false); } },
    /* suivre un point qui bouge (la tête de celle qui parle) : une fonction qui rend un Vector3, ou null */
    suivre(f) { suivi = f || null; },
    /* cadrer celle qui parle : le champ vertical voulu, et la mise au point à sa distance */
    cadrer(fov, distance) { fovCadre = fov; moteur.flou && moteur.flou(fov != null, distance); },
    /* aller TOUT PRÈS de quelqu'un : le point de passage le plus proche, puis les derniers pas
       jusqu'à ~1,3 m d'elle (Mongazi : « il faut être un peu plus proche ») */
    allerPres(point, { distance = 1.3, puis } = {}) {
      const k = graphe.plusProche(point.x, point.z), n = graphe.noeuds[k];
      const v = new THREE.Vector3(n.x - point.x, 0, n.z - point.z);
      let fin = null;
      if (v.length() > distance + 0.25) { v.setLength(distance); fin = new THREE.Vector3(point.x + v.x, 0, point.z + v.z); }
      else if (Math.hypot(pos.x - point.x, pos.z - point.z) < distance + 0.4) { tournerVers(point.clone()); if (puis) puis(); return true; }
      return allerA(k, { regard: point.clone(), puis, fin });
    },
    /* aller se placer devant quelque chose (un PNJ, une pièce) : le point le plus proche, puis on le regarde */
    allerVoir(point, { puis } = {}) {
      const k = graphe.plusProche(point.x, point.z, n => !n.passage || true);
      return allerA(k, { regard: point.clone(), puis });
    },
  };
  return deplacement;
}

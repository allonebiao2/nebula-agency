// LE SALON 3D · moteur commun aux trois univers de Luxury Club 229 (clinique, INA Luxury, harmonisation faciale).
//
// Une scène three.js collée à l'écran pendant qu'on défile. La caméra va d'une STATION à l'autre en suivant une
// courbe ; chaque station a son calque de texte, ses points posés dans le décor, et des objets qu'on touche.
// Le MONDE (décor, lumière, matières, stations) vient d'un module par univers. Ce fichier ne sait rien d'un métier.
//
// Références : FIRST PAGE 3D (le parcours en étapes, les points posés dans la scène, les pastilles sur le bord) et
// Vibrant Wellness (toucher une zone, la caméra s'approche). Voir REFONTE-26-11.md.
//
// Règles de la maison tenues ici :
//  · netteté NATIVE de l'écran (jusqu'à 3x), plancher à 2x jamais franchi ; si l'appareil peine, on coupe d'abord
//    les ombres et la poussière, puis on descend vers le plancher, jamais en dessous ;
//  · on ne rend rien quand la scène est hors de l'écran ; on ne rend pas quand rien ne bouge ;
//  · `prefers-reduced-motion` : la caméra saute d'une station à l'autre, aucun effet continu ;
//  · sans WebGL : la section se retire et la page d'origine reste entière.
import * as THREE from "./vendor/three.module.min.js";
export { THREE };

const lisse = (t) => t * t * (3 - 2 * t);
const borne = (x, a, b) => Math.max(a, Math.min(b, x));

export async function lancer({ racine, monde, surStation = null, surMouvement = null, surSurvol = null }) {
  const mobile = matchMedia("(max-width: 760px)").matches;
  const calme = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const scene3 = racine.querySelector(".s3d-scene");
  const canvas = racine.querySelector("canvas");

  // ---------- le rendu ----------
  let renderer;
  try {
    const natifTest = Math.min(devicePixelRatio || 1, 3);
    renderer = new THREE.WebGLRenderer({ canvas, antialias: natifTest < 2, powerPreference: "high-performance", alpha: false });
  } catch (e) {
    racine.classList.add("s3d-sans");
    return null;
  }
  const natif = Math.min(devicePixelRatio || 1, 3);
  const plancher = Math.min(natif, 2);
  let dpr = natif;
  renderer.setPixelRatio(dpr);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.NeutralToneMapping;
  renderer.toneMappingExposure = 1;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(mobile ? 62 : 48, 1, 0.05, 220);
  const anis = renderer.capabilities.getMaxAnisotropy();
  const outils = { anis, natif, plancher, charger: chargeur(anis) };

  const M = await monde({ THREE, scene, renderer, camera, mobile, calme, outils });
  const stations = M.stations;
  const N = stations.length;

  // ---------- la section : une hauteur d'écran par station ----------
  const H = mobile ? 96 : 100;
  racine.style.setProperty("--s3d-n", N);
  racine.style.height = `calc(${N} * ${H}svh)`;

  // ---------- les calques de texte ----------
  const calques = racine.querySelector(".s3d-calques");
  calques.innerHTML = stations.map((st, k) =>
    `<div class="s3d-calque ${st.cote || "a-gauche"}" data-k="${k}" aria-hidden="${k ? "true" : "false"}">${st.calque || ""}</div>`).join("");
  const blocs = [...calques.children];

  // ---------- les pastilles du bord (FIRST PAGE) ----------
  const nav = racine.querySelector(".s3d-pastilles");
  if (nav) {
    nav.innerHTML = stations.map((st, k) =>
      `<button type="button" data-k="${k}" aria-label="${(st.nom || "Étape " + (k + 1)).replace(/"/g, "&quot;")}"><i></i><span>${st.nom || ""}</span></button>`).join("");
    nav.addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) aller(+b.dataset.k); });
  }
  const pastilles = nav ? [...nav.children] : [];
  const jauge = racine.querySelector(".s3d-jauge i");

  // ---------- les points posés dans la scène ----------
  const couche = racine.querySelector(".s3d-points");
  const points = [];
  stations.forEach((st, k) => (st.points || []).forEach((pt) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "s3d-pt";
    if (pt.id) b.dataset.id = pt.id;
    b.innerHTML = `<i aria-hidden="true"></i><span>${pt.label}</span>`;
    b.addEventListener("click", (e) => { e.stopPropagation(); pt.act && pt.act(); });
    couche.appendChild(b);
    points.push({ k, el: b, v: new THREE.Vector3(...pt.p), toujours: !!pt.toujours });
  }));

  // ---------- la courbe de la caméra : stations + points de passage ----------
  const cle = (s) => (mobile && s.camM ? s.camM : s.cam);
  const posPts = [], cibPts = [], idxStation = [];
  stations.forEach((st, k) => {
    const c = cle(st);
    (c.via || []).forEach((v, j, arr) => {
      const prev = cle(stations[Math.max(0, k - 1)]);
      const f = (j + 1) / (arr.length + 1);
      posPts.push(new THREE.Vector3(...v.p));
      cibPts.push(v.c ? new THREE.Vector3(...v.c) : new THREE.Vector3(...prev.c).lerp(new THREE.Vector3(...c.c), f));
    });
    idxStation.push(posPts.length);
    posPts.push(new THREE.Vector3(...c.p));
    cibPts.push(new THREE.Vector3(...c.c));
  });
  const courbeP = new THREE.CatmullRomCurve3(posPts, false, "centripetal");
  const courbeC = new THREE.CatmullRomCurve3(cibPts, false, "centripetal");
  const nPts = posPts.length - 1 || 1;

  const camPos = courbeP.getPoint(0), camCib = courbeC.getPoint(0);
  const visePos = camPos.clone(), viseCib = camCib.clone();
  // un décalage ajouté par le monde (s'approcher d'une zone touchée, Vibrant)
  const decal = { p: new THREE.Vector3(), c: new THREE.Vector3(), pV: new THREE.Vector3(), cV: new THREE.Vector3() };
  camera.position.copy(camPos);
  camera.lookAt(camCib);

  // ---------- défilement -> progression ----------
  let f = 0, kActif = -1, haut = 0;
  const mesurer = () => { haut = racine.getBoundingClientRect().top + scrollY; };
  const progression = () => {
    const total = racine.offsetHeight - innerHeight;
    return borne((scrollY - haut) / Math.max(1, total), 0, 1) * (N - 1);
  };
  // la caméra se pose sur chaque station : la moitié du trajet se fait au milieu du défilement entre deux stations
  const posee = (x) => {
    const i = Math.min(Math.floor(x), N - 2), t = x - i;
    const tt = lisse(borne((t - 0.18) / 0.64, 0, 1));
    return { i: Math.max(0, i), t: N < 2 ? 0 : tt };
  };
  function viser() {
    const { i, t } = posee(f);
    const a = idxStation[i] / nPts, b = idxStation[Math.min(i + 1, N - 1)] / nPts;
    const u = a + (b - a) * t;
    courbeP.getPoint(u, visePos);
    courbeC.getPoint(u, viseCib);
    visePos.add(decal.p);
    viseCib.add(decal.c);
  }

  function aller(k) {
    mesurer();
    const total = racine.offsetHeight - innerHeight;
    scrollTo({ top: haut + (k / Math.max(1, N - 1)) * total + 2, behavior: calme ? "auto" : "smooth" });
  }

  // ---------- toucher les objets de la scène ----------
  const ray = new THREE.Raycaster(), souris = new THREE.Vector2();
  const cliquables = M.cliquables || [];
  let appui = null;
  const viser3D = (e) => {
    const r = canvas.getBoundingClientRect();
    souris.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(souris, camera);
    const h = ray.intersectObjects(cliquables, true)[0];
    if (!h) return null;
    let o = h.object;
    while (o && !o.userData.act) o = o.parent;
    return o && (o.userData.k == null || o.userData.k === kActif) ? o : null;
  };
  scene3.addEventListener("pointerdown", (e) => { appui = { x: e.clientX, y: e.clientY }; });
  scene3.addEventListener("pointerup", (e) => {
    if (!appui || Math.hypot(e.clientX - appui.x, e.clientY - appui.y) > 8) return;
    const o = viser3D(e);
    if (o) o.userData.act();
  });
  let survolDernier = null;
  if (!mobile) {
    let att = 0;
    scene3.addEventListener("pointermove", (e) => {
      const t = performance.now();
      if (t - att < 90) return;
      att = t;
      const o = viser3D(e);
      scene3.style.cursor = o ? "pointer" : "";
      if (o && o !== survolDernier && surSurvol) surSurvol(o);
      survolDernier = o;
      if (M.survol) M.survol(o);
    });
  }

  // ---------- taille ----------
  function taille() {
    const w = scene3.clientWidth, h = scene3.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    if (M.taille) M.taille(w, h);
    mesurer();
    sale = true;
  }
  let sale = true;
  new ResizeObserver(taille).observe(scene3);
  addEventListener("scroll", () => { sale = true; }, { passive: true });

  // ---------- la boucle ----------
  let visible = true, horloge = performance.now(), t0 = horloge;
  new IntersectionObserver((es) => {
    visible = es[0].isIntersecting;
    if (visible) { horloge = performance.now(); requestAnimationFrame(boucle); }
  }, { rootMargin: "120px" }).observe(racine);

  const tampon = new THREE.Vector3();
  let vitesseDite = 0;
  const lent = { n: 0, s: 0, palier: 0 };
  function ajuster(dt) {
    // on mesure 50 images d'affilée ; sous 45 i/s, on allège d'un cran
    lent.n++; lent.s += dt;
    if (lent.n < 50) return;
    const moy = lent.s / lent.n;
    lent.n = 0; lent.s = 0;
    if (moy > 0.022) {
      if (lent.palier === 0 && M.qualite) { M.qualite("basse"); lent.palier = 1; return; }
      if (dpr > plancher) { dpr = Math.max(plancher, +(dpr - 0.25).toFixed(2)); renderer.setPixelRatio(dpr); taille(); }
    } else if (moy < 0.0135 && dpr < natif) {
      dpr = Math.min(natif, +(dpr + 0.25).toFixed(2)); renderer.setPixelRatio(dpr); taille();
    }
  }

  function boucle(maintenant) {
    if (!visible) return;
    requestAnimationFrame(boucle);
    // le menu recouvre la page : on ne dessine rien (menu.js pose la classe)
    if (document.documentElement.classList.contains("lm-ouvert")) { horloge = maintenant; sale = true; return; }
    const dt = Math.min(0.05, (maintenant - horloge) / 1000);
    horloge = maintenant;
    const fAvant = f;
    f = progression();
    if (jauge && f !== fAvant) jauge.style.transform = `scaleX(${N > 1 ? f / (N - 1) : 1})`;

    // la station active
    const k = Math.round(f);
    if (k !== kActif) {
      kActif = k;
      blocs.forEach((b, j) => { b.classList.toggle("on", j === k); b.setAttribute("aria-hidden", j === k ? "false" : "true"); });
      pastilles.forEach((b, j) => b.classList.toggle("on", j === k));
      racine.dataset.station = stations[k].id || k;
      if (M.surStation) M.surStation(k);
      if (surStation) surStation(k, stations[k]);
    }

    // la caméra suit sa cible, lissée (amortissement critique)
    viser();
    decal.p.lerp(decal.pV, calme ? 1 : 1 - Math.exp(-dt * 3.2));
    decal.c.lerp(decal.cV, calme ? 1 : 1 - Math.exp(-dt * 3.2));
    const a = calme ? 1 : 1 - Math.exp(-dt * 5.5);
    camPos.lerp(visePos, a);
    camCib.lerp(viseCib, a);
    const bouge = camPos.distanceToSquared(visePos) > 1e-7 || camCib.distanceToSquared(viseCib) > 1e-7;
    // la vitesse de la caméra (m/s, ramenée à 0-1) : le souffle du mouvement la suit
    if (surMouvement) {
      const v = dt > 0 ? Math.min(1, camera.position.distanceTo(camPos) / dt / 7) : 0;
      if (Math.abs(v - vitesseDite) > 0.03 || (v === 0 && vitesseDite !== 0)) { vitesseDite = v; surMouvement(v); }
    }
    camera.position.copy(camPos);
    camera.lookAt(camCib);

    const vivant = M.anime ? M.anime((maintenant - t0) / 1000, dt, { k: kActif, f, camera }) : false;
    if (!(bouge || vivant || sale)) return;
    sale = false;
    renderer.render(scene, camera);
    ajuster(dt);

    // les points de la station, projetés sur l'écran
    const w = scene3.clientWidth, h = scene3.clientHeight;
    for (const p of points) {
      const on = p.k === kActif;
      if (!on) { if (p.el.classList.contains("on")) p.el.classList.remove("on"); continue; }
      tampon.copy(p.v).project(camera);
      const dedans = tampon.z < 1 && Math.abs(tampon.x) < 0.96 && Math.abs(tampon.y) < 0.92;
      p.el.classList.toggle("on", dedans);
      if (dedans) p.el.style.transform = `translate3d(${((tampon.x + 1) / 2) * w}px, ${((1 - tampon.y) / 2) * h}px, 0)`;
    }
  }

  taille();
  requestAnimationFrame(boucle);
  racine.classList.add("s3d-pret");

  return {
    aller,
    station: () => kActif,
    // s'approcher d'un point (la zone touchée) : décalage de la caméra et de sa cible, remis à zéro par approcher(null)
    approcher(dp, dc) {
      if (!dp) { decal.pV.set(0, 0, 0); decal.cV.set(0, 0, 0); }
      else { decal.pV.set(...dp); decal.cV.set(...(dc || dp)); }
      sale = true;
    },
    rafraichir() { sale = true; },
    renderer, scene, camera,
  };
}

// Un chargeur d'images en textures : la variante du srcset juste assez grande pour l'écran, jamais 4K entière.
function chargeur(anis) {
  const charge = new THREE.TextureLoader();
  return (src) => new Promise((ok) => charge.load(src, (t) => {
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = anis;
    ok(t);
  }, undefined, () => ok(null)));
}

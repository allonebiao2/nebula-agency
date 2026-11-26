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
//  · 4K (Mongazi, 26/11) : jamais sous 2x, même sur un écran de PC ordinaire (1x) : un écran 1920 est rendu en
//    3840 px de large. Le plafond est le natif de l'écran (jusqu'à 3x) ET un budget de 3840 × 2160 pixels : un grand
//    écran atteint la 4K sans la dépasser. Sur grand rendu, les matières sont dessinées en double définition et les
//    produits détourés viennent en 2x ;
//  · LA FLUIDITÉ D'ABORD (Mongazi, 26/11 : « le plus fluide possible ») : 60 images/s visées, aucun plafond (un
//    écran 120 Hz en reçoit 120). Sous 55, on coupe la poussière et les rais (jamais les ombres : les couper
//    recompile toutes les matières et gèle la 3D), puis on descend vers la 4K plancher
//    (2x), puis jusqu'à la netteté NATIVE de l'écran, jamais en dessous. Une définition baissée ne remonte pas sur un
//    écran 60 Hz (pas d'aller-retour, chacun est un à-coup) ;
//  · les ombres ne bougent pas (aucun objet qui en porte ne se déplace) : calculées au départ et à chaque étape,
//    jamais à chaque image ;
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
  // ---------- la définition : 4K ----------
  const natif = Math.min(devicePixelRatio || 1, 3);
  const BUDGET = 3840 * 2160;
  const plafondEcran = () => {
    const w = scene3.clientWidth || innerWidth, h = scene3.clientHeight || innerHeight;
    return +Math.min(Math.max(natif, 2), Math.max(1, Math.sqrt(BUDGET / (w * h)))).toFixed(2);
  };
  let plafond = plafondEcran();
  let plancher = Math.min(2, plafond);
  // le dernier recours de la fluidité : la netteté native de l'écran (un PC 1x : 1x ; un iPhone 3x : 2x)
  let plancherFluide = Math.min(plancher, Math.max(1, natif));
  // un grand rendu (un PC, un écran 4K) : matières en double définition, produits en 2x
  let grand = (scene3.clientWidth || innerWidth) * plafond >= 2600;
  // UNE CARTE GRAPHIQUE FAIBLE (Intel HD/UHD intégrée, Mali, PowerVR, Adreno d'entrée de gamme : la plupart des
  // portables et des téléphones de Cotonou) ne tient pas 60 images/s en 4K quand la caméra bouge (Intel HD 5500
  // mesurée à 40 i/s en 2x, 26/11). Elle démarre à la netteté native de l'écran, sans double définition, avec
  // l'anticrénelage (qui se décide à la création du contexte : d'où la toile d'essai, lue puis rendue) ; une carte
  // forte (iPhone, Mac, PC de jeu) démarre en 4K. L'adaptation corrige ensuite dans les deux sens.
  let gpu = "";
  try {
    const essai = document.createElement("canvas").getContext("webgl2") || document.createElement("canvas").getContext("webgl");
    const dbg = essai && essai.getExtension("WEBGL_debug_renderer_info");
    gpu = String((essai && ((dbg && essai.getParameter(dbg.UNMASKED_RENDERER_WEBGL)) || essai.getParameter(essai.RENDERER))) || "");
    const perte = essai && essai.getExtension("WEBGL_lose_context");
    if (perte) perte.loseContext();
  } catch (e) {}
  const faible = /Intel.*(HD|UHD) Graphics|Mali|PowerVR|Adreno \(TM\) [1-6]\d\d|SwiftShader|llvmpipe|Basic Render/i.test(gpu);
  if (faible) { grand = false; plancherFluide = Math.min(plancherFluide, Math.max(1, Math.min(natif, 1.5))); }
  window.S3D_FINESSE = grand ? 2 : 1;
  let dpr = faible ? Math.min(plafond, Math.max(plancherFluide, Math.min(natif, 2))) : plafond;
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: dpr < 2, powerPreference: "high-performance", alpha: false });
  } catch (e) {
    racine.classList.add("s3d-sans");
    return null;
  }
  renderer.setPixelRatio(dpr);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.NeutralToneMapping;
  renderer.toneMappingExposure = 1;
  renderer.shadowMap.enabled = true;
  // au téléphone, l'ombre douce coûte trop de lectures par pixel : la même ombre, filtrée plus simplement
  renderer.shadowMap.type = mobile || faible ? THREE.PCFShadowMap : THREE.PCFSoftShadowMap;
  // les ombres sont figées : on les recalcule seulement quand on le demande (voir « ombres » dans la boucle)
  renderer.shadowMap.autoUpdate = false;
  let ombres = 90;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(mobile ? 62 : 48, 1, 0.05, 220);
  const anis = renderer.capabilities.getMaxAnisotropy();
  const outils = { anis, natif, plancher, faible, finesse: window.S3D_FINESSE, charger: chargeur(anis, grand, renderer) };

  const tMonde = performance.now();
  const M = await monde({ THREE, scene, renderer, camera, mobile, calme, outils });
  const tempsMonde = Math.round(performance.now() - tMonde);
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
    // l'écran a changé de taille (rotation, fenêtre) : le budget 4K se recalcule
    const p = plafondEcran();
    if (p !== plafond) {
      plafond = p; plancher = Math.min(2, plafond); plancherFluide = Math.min(plancher, Math.max(1, natif));
      plancherFluide = faible ? Math.min(plancherFluide, Math.max(1, Math.min(natif, 1.5))) : plancherFluide;
      dpr = borne(dpr, plancherFluide, plafond); renderer.setPixelRatio(dpr);
    }
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

  // LA COMPILATION SANS GEL : la carte graphique compile les matières en parallèle (KHR_parallel_shader_compile) ;
  // pendant ce temps on ne dessine pas (l'image précédente reste), mais la page continue de défiler. Sans cela, la
  // première image et le passage en qualité basse gelaient tout (2 s mesurées sur une Intel HD 5500, 26/11).
  let compilation = null;
  function recompiler() {
    if (!renderer.compileAsync) return Promise.resolve();
    const t = performance.now();
    const p = renderer.compileAsync(scene, camera).catch(() => {}).then(() => {
      if (compilation === p) compilation = null;   // l'envoi des textures du démarrage peut être encore en cours
      sale = true;
      if (window.S3D) (S3D.temps = S3D.temps || {}).compilation_ms = Math.round(performance.now() - t);
    });
    compilation = p;
    return p;
  }
  const tampon = new THREE.Vector3();
  let vitesseDite = 0;
  // ce que le moteur rend vraiment, lisible dans la console (et par le QC) : window.S3D
  const S3D = window.S3D = { dpr, plafond, rendu: [canvas.width, canvas.height], ips: null, finesse: window.S3D_FINESSE, gpu, faible,
    temps: { monde_ms: tempsMonde } };
  const lent = { n: 0, s: 0, palier: 0, chauffe: 45, baisse: 0, debut: 0 };
  function ajuster(dt, maintenant) {
    // les premières secondes montent les textures et les photos : elles ne disent rien de l'appareil
    if (!lent.debut) lent.debut = maintenant;
    if (lent.chauffe > 0 || maintenant - lent.debut < 2500) { if (lent.chauffe > 0) lent.chauffe--; return; }
    // on mesure 40 images RENDUES d'affilée ; sous 55 i/s, on allège d'un cran
    lent.n++; lent.s += dt;
    if (lent.n < 40) return;
    const moy = lent.s / lent.n;
    lent.n = 0; lent.s = 0;
    S3D.ips = Math.round(1 / moy);
    if (moy > 1 / 55) {
      lent.baisse = maintenant;
      if (lent.palier === 0 && M.qualite) { M.qualite("basse"); lent.palier = 1; lent.chauffe = 20; }
      else if (dpr > plancherFluide) {
        // l'appareil peine vraiment (sous 45 i/s) : un grand pas ; sinon un petit. D'abord vers la 4K plancher, puis
        // jusqu'à la netteté native
        const pas = moy > 1 / 45 ? 0.5 : 0.25, bas = dpr > plancher ? plancher : plancherFluide;
        dpr = Math.max(bas, +(dpr - pas).toFixed(2)); renderer.setPixelRatio(dpr); taille(); lent.chauffe = 10;
      }
    } else if (moy < 1 / 80 && dpr < plafond && maintenant - lent.baisse > 10000) {
      // un écran 120 Hz qui a de la marge remonte vers la 4K, pas plus d'un cran toutes les 10 s après une baisse
      dpr = Math.min(plafond, +(dpr + 0.25).toFixed(2)); renderer.setPixelRatio(dpr); taille(); lent.chauffe = 10;
    }
    S3D.dpr = dpr; S3D.rendu = [renderer.domElement.width, renderer.domElement.height]; S3D.qualite = lent.palier ? "basse" : "pleine";
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
      ombres = Math.max(ombres, 2);   // une étape neuve : les ombres se refont une fois (un décor chargé entre-temps)
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
    if (compilation) return;
    sale = false;
    if (ombres > 0) { renderer.shadowMap.needsUpdate = true; ombres--; }
    renderer.render(scene, camera);
    ajuster(dt, maintenant);

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
  recompiler();
  // les textures du décor partent vers la carte graphique UNE PAR IMAGE, pendant que les matières se compilent :
  // la première image n'a plus rien à envoyer (tout d'un coup, c'était le gel du démarrage)
  const aEnvoyer = new Set();
  scene.traverse((o) => {
    const ms = o.material ? (Array.isArray(o.material) ? o.material : [o.material]) : [];
    for (const m of ms) for (const k of ["map", "normalMap", "roughnessMap", "alphaMap", "emissiveMap", "bumpMap"]) if (m[k] && m[k].isTexture) aEnvoyer.add(m[k]);
  });
  const avantPremiere = compilation;
  compilation = (async () => {
    for (const t of aEnvoyer) {
      try { renderer.initTexture(t); } catch (e) {}
      await new Promise((r) => requestAnimationFrame(r));
    }
    if (avantPremiere) await avantPremiere;
    compilation = null; sale = true;
  })();
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
    rafraichir() { sale = true; ombres = Math.max(ombres, 2); },
    renderer, scene, camera,
  };
}

// Un chargeur d'images en textures. Sur grand rendu, un produit détouré vient en 2x (`_detoures/2x/`, agrandi par
// `_outils/_agrandir_detoures.py`) ; s'il manque, l'original prend sa place sans un mot.
// Chaque photo est DÉCODÉE hors du fil principal (decode()) puis envoyée à la carte graphique dès son arrivée
// (initTexture) : sans cela, le décodage et l'envoi tombaient sur l'image où la caméra arrive devant le produit.
// Hors Safari, createImageBitmap décode ET retourne l'image hors du fil principal, et l'envoi d'un ImageBitmap est
// direct. Safari (iPhone) garde l'image classique : ses options de createImageBitmap ne sont pas fiables partout.
function chargeur(anis, grand, renderer) {
  const safari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
  const bitmap = !safari && typeof createImageBitmap === "function" && THREE.ImageBitmapLoader;
  const charge = bitmap ? new THREE.ImageBitmapLoader() : new THREE.TextureLoader();
  if (bitmap) charge.setOptions({ imageOrientation: "flipY", premultiplyAlpha: "none" });
  const pret = (t) => {
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = anis;
    try { if (renderer) renderer.initTexture(t); } catch (e) {}
    return t;
  };
  const une = (src) => new Promise((ok) => charge.load(src, async (x) => {
    if (bitmap) { const t = new THREE.Texture(x); t.flipY = false; t.needsUpdate = true; return ok(pret(t)); }
    try { if (x.image && x.image.decode) await x.image.decode(); } catch (e) {}
    ok(pret(x));
  }, undefined, () => ok(null)));
  // la liste des produits déjà agrandis (`2x/liste.json`, écrite par l'agrandisseur) : on ne demande jamais un
  // fichier absent
  let liste = null;
  const lire = (dossier) => liste || (liste = fetch(dossier + "2x/liste.json").then((r) => (r.ok ? r.json() : []))
    .catch(() => []).then((a) => new Set(a)));
  return async (src) => {
    if (grand && src && src.includes("/_detoures/") && !src.includes("/2x/")) {
      const i = src.indexOf("/_detoures/") + 11, nom = src.slice(i).split("?")[0];
      if ((await lire(src.slice(0, i))).has(nom)) {
        const t = await une(src.slice(0, i) + "2x/" + src.slice(i));
        if (t) return t;
      }
    }
    return une(src);
  };
}

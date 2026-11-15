/* LE MONDE · le personnage-vidéo : en conversation, on voit la VIDÉO de la personne, plus son modèle 3D.

   Mongazi (2026-11-14) : « comment faire pour que ce soit ultra réaliste ? », « pour les visages, comment se
   rapprocher le maximum possible ? ». Ses vidéos (image → vidéo) sont photoréalistes ; le passage en 3D les
   détruisait (TRELLIS ne donne qu'une centaine de pixels de texture au visage, Mixamo un mouvement générique).
   Donc, quand une visiteuse parle AU visiteur (elle lui fait face, la caméra est cadrée sur elle, le fond est
   flou), le salon montre la vidéo détourée, posée à sa place ; le modèle 3D reste là, invisible, et continue de
   donner la position de la tête (cadrage, étiquette) et les ombres des pieds. Hors conversation (elle marche, de
   loin), c'est la 3D. Hillary, qui ne quitte pas son comptoir, est en vidéo en permanence (`actif: () => true`).

   Les vidéos sont préparées par `monde/_outils/perso_video.py` : couleur à GAUCHE, opacité à DROITE dans une
   seule vidéo H.264 (le seul format à transparence que lisent aussi les iPhone) + un `.json` (où sont la tête et
   les pieds dans l'image). `sources` : { parler: 'personnages/afi/video-parler', ecouter: '…' } (sans extension).
   Une vidéo absente ou illisible : la 3D reste, sans erreur. `?sans-video` : la 3D partout (pour comparer).

   ⚠️ ON N'ATTEND JAMAIS QU'UNE VIDÉO « SE CHARGE TOUTE SEULE » (2026-11-15). La première version attendait
   l'événement `loadeddata` avant de déclarer la vidéo prête : un iPhone ne précharge RIEN sans lecture (Hillary n'y
   serait jamais apparue), et même Chrome laissait parfois la vidéo en plan (deux captures sur trois montraient
   encore le mannequin). Ici : la vidéo est dans la page (cachée), on la LANCE (muette, « playsinline » : permis
   partout sans geste), on la met en pause dès qu'elle a une image, et on ne la MONTRE que lorsqu'elle en a une
   (`readyState ≥ 2`). Tant qu'aucune n'est prête, la 3D reste. Une vidéo qui ne vient pas est relancée. */
import { THREE } from './moteur.js';

const VS = 'varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }';
/* la vidéo est en sRVB : décodée ici à la main (la texture est déclarée sans espace de couleur, sinon un
   navigateur la décode et l'autre non) ; ni lumière ni tonalité du salon : la lumière est DANS la vidéo, on
   la teinte seulement (le soir tamisé) */
const FS = `uniform sampler2D carte; uniform vec3 teinte; uniform float opacite, chute, fonduBas; varying vec2 vUv;
void main() {
  vec3 c = sRGBTransferEOTF(vec4(texture2D(carte, vec2(vUv.x * 0.5, vUv.y)).rgb, 1.0)).rgb;
  float a = texture2D(carte, vec2(0.5 + vUv.x * 0.5, vUv.y)).r;
  a = smoothstep(0.03, 0.97, a) * opacite;
  /* un buste coupé par le cadre : son bord bas se fond (il est derrière le comptoir) */
  if (fonduBas > 0.0) a *= smoothstep(0.0, fonduBas, vUv.y);
  if (a < 0.01) discard;
  /* le soir, la lumière tombe des spots : la tête et les épaules plus éclairées que les jambes (vUv.y = 1 en haut) */
  c *= mix(1.0 - chute, 1.0, smoothstep(0.05, 0.85, vUv.y));
  gl_FragColor = vec4(c * teinte, a);
  #include <colorspace_fragment>
}`;

/* les vidéos vivent dans la page, dans une boîte d'un pixel (jamais `display:none` : certains navigateurs cessent
   alors de les décoder) */
function boiteVideos() {
  let b = document.getElementById('videos-personnages');
  if (!b) {
    b = document.createElement('div'); b.id = 'videos-personnages'; b.setAttribute('aria-hidden', 'true');
    b.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:1px;overflow:hidden;opacity:0;pointer-events:none;z-index:-1';
    document.body.appendChild(b);
  }
  return b;
}

/* `teinte()` : un nombre (gris) ou { r, g, b, chute } donné par le lieu (le soir : plus bas, plus chaud, la lumière
   qui tombe d'en haut) */
export function creerPersoVideo({ moteur, perso, sources, taille, actif = () => false, teinte = () => 1 }) {
  if (new URLSearchParams(location.search).has('sans-video')) return null;
  const { scene, camera } = moteur;
  const clips = {};
  const groupe = new THREE.Group(); groupe.visible = false; groupe.userData.garder = true; scene.add(groupe);
  let courant = null, montre = 0, vise = 0, temps = 0;
  const etat = { pret: false, clip: null, montre: 0, erreur: '', charge: 0 };
  const aUneImage = (c) => !!c && c.video.readyState >= 2 && !c.video.error;

  /* lancer une vidéo pour qu'elle se charge (et la relancer si elle ne vient pas) */
  function amorcer(c) {
    if (aUneImage(c) || (c.amorce != null && temps - c.amorce < 4)) return;
    if (c.amorce != null && c.video.readyState < 1 && c.essais < 3) { c.essais++; try { c.video.load(); } catch (e) { /* rien */ } }
    c.amorce = temps;
    const p = c.video.play(); if (p && p.catch) p.catch(() => {});
  }

  async function preparer(nom, base) {
    const meta = await fetch(base + '.json').then(r => { if (!r.ok) throw new Error(base + '.json : ' + r.status); return r.json(); });
    const video = Object.assign(document.createElement('video'), { muted: true, loop: !meta.une_fois, playsInline: true, preload: 'auto', crossOrigin: 'anonymous', disableRemotePlayback: true });
    video.setAttribute('playsinline', ''); video.setAttribute('webkit-playsinline', ''); video.setAttribute('muted', '');
    video.defaultPlaybackRate = meta.vitesse || 1; video.playbackRate = meta.vitesse || 1;
    video.addEventListener('error', () => { etat.erreur = 'vidéo illisible : ' + base; });
    boiteVideos().appendChild(video);
    video.src = base + '.mp4';
    const tex = new THREE.VideoTexture(video); tex.colorSpace = THREE.NoColorSpace; tex.minFilter = THREE.LinearFilter; tex.generateMipmaps = false;
    const mat = new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: FS, transparent: true, depthWrite: false, toneMapped: false,
      uniforms: { carte: { value: tex }, teinte: { value: new THREE.Color(1, 1, 1) }, opacite: { value: 0 }, chute: { value: 0 }, fonduBas: { value: meta.fondu_bas || 0 } } });
    /* la taille : de la tête aux pieds, la personne mesure `taille` ; l'image entière est donc plus haute…
       ou, pour un BUSTE (le bas du corps hors cadre), la hauteur réelle du cadre donnée par la préparation */
    const hauteur = meta.hauteur_m || taille / Math.max(0.2, meta.pieds - meta.tete), largeur = hauteur * meta.largeur / meta.hauteur;
    const plan = new THREE.Mesh(new THREE.PlaneGeometry(largeur, hauteur), mat);
    /* centrée sur ses pieds ; les pieds (fraction `pieds` depuis le haut) posés au sol : le bas de l'image est à
       −(1 − pieds)·hauteur ; un buste est posé à la hauteur de son bord bas */
    plan.position.set((0.5 - meta.centre) * largeur, meta.hauteur_m ? meta.bas_m + hauteur / 2 : hauteur / 2 - (1 - meta.pieds) * hauteur, 0);
    plan.renderOrder = 3; plan.frustumCulled = false; plan.visible = false;
    groupe.add(plan);
    const c = clips[nom] = { video, mat, plan, meta, poids: 0, amorce: null, essais: 0 };
    amorcer(c);
  }

  const pret = Promise.allSettled(Object.entries(sources).map(([nom, base]) => preparer(nom, base)))
    .then((r) => {
      etat.pret = Object.keys(clips).length > 0;
      const rates = r.filter(x => x.status === 'rejected'); if (rates.length && !etat.erreur) etat.erreur = String(rates[0].reason);
      return etat.pret;
    });

  /* « saluer » se joue UNE fois, en entier, quand le personnage salue (Hillary, à l'arrivée du visiteur au comptoir),
     sauf si elle se met à parler ; puis on revient à « écouter » */
  let salut = false, gestePrec = null;
  function voulue() {
    const st = perso.st || {}, s = clips.saluer;
    if (s) {
      if (st.geste === 'saluer' && gestePrec !== 'saluer' && !st.parle) { salut = true; try { s.video.currentTime = 0; } catch (e) { /* rien */ } }
      gestePrec = st.geste;
      if (salut && (st.parle || s.video.ended || (courant === 'saluer' && s.video.currentTime >= s.video.duration - 0.12))) salut = false;
      if (salut) return 'saluer';
    }
    if (!st.parle && clips.ecouter) return 'ecouter';
    return clips.parler ? 'parler' : Object.keys(clips)[0];
  }
  /* celle qu'on veut si elle a une image ; sinon on la demande, et on prend en attendant une autre qui en a une */
  function choisir() {
    const v = voulue();
    if (aUneImage(clips[v])) return v;
    if (clips[v]) amorcer(clips[v]);
    return ['ecouter', 'parler', ...Object.keys(clips)].find(k => k !== 'saluer' && aUneImage(clips[k])) || null;
  }
  /* LE FONDU ENTRE DEUX VIDÉOS (« écouter » ↔ « parler ») : la nouvelle repart de sa première image et monte en
     0,25 s PAR-DESSUS l'ancienne, qui reste pleine (sinon le décor transparaît à mi-fondu), puis l'ancienne s'efface. */
  function jouer(nom) {
    if (nom === courant) return;
    const c = clips[nom];
    try { c.video.currentTime = 0; } catch (e) { /* rien */ }
    c.video.playbackRate = c.meta.vitesse || 1;
    const p = c.video.play(); if (p && p.catch) p.catch(() => {});
    c.plan.visible = true; c.plan.renderOrder = 4;
    if (courant && clips[courant]) clips[courant].plan.renderOrder = 3;
    if (!courant) c.poids = 1;   /* la première : pas de fondu entre vidéos (c'est le fondu avec la 3D qui joue) */
    courant = nom; etat.clip = nom;
  }
  function fondre(dt) {
    const c = clips[courant]; if (!c) return;
    c.poids = Math.min(1, c.poids + dt / 0.25);
    for (const [k, o] of Object.entries(clips)) {
      if (k === courant) continue;
      if (c.poids >= 1 && o.poids > 0) o.poids = Math.max(0, o.poids - dt / 0.12);
      if (o.poids <= 0 && o.plan.visible) { o.plan.visible = false; o.video.pause(); }
    }
  }

  const coul = new THREE.Color();
  moteur.chaqueImage((dt) => {
    temps += dt;
    if (!etat.pret) return;
    /* les vidéos lancées pour se charger s'arrêtent dès qu'elles ont une image ; celles qui ne viennent pas sont relancées */
    let charge = 0;
    for (const c of Object.values(clips)) {
      if (aUneImage(c)) { charge++; if (!c.plan.visible && !c.video.paused) c.video.pause(); }
      else amorcer(c);
    }
    etat.charge = charge;
    const nom = actif() ? choisir() : null;
    vise = nom ? 1 : 0;
    /* une bascule courte (≈ 0,3 s) : elle se fait pendant que la caméra se cadre sur la conversation */
    montre += (vise - montre) * Math.min(1, dt * 10);
    if (Math.abs(montre - vise) < 0.004) montre = vise;
    etat.montre = montre;
    groupe.visible = montre > 0.002;
    /* la 3D s'efface dès que la vidéo couvre (plus de double image), et revient avant qu'elle parte */
    const corps3d = perso.modele3d || perso.corps; if (corps3d) corps3d.visible = montre < 0.6;
    if (!groupe.visible) { if (courant) { for (const o of Object.values(clips)) { o.video.pause(); o.plan.visible = false; o.poids = 0; } courant = null; etat.clip = null; } return; }
    if (nom) jouer(nom);
    fondre(dt);
    const r = perso.racine.position;
    groupe.position.set(r.x, r.y, r.z);
    groupe.rotation.y = Math.atan2(camera.position.x - r.x, camera.position.z - r.z);
    const k = teinte(), tr = typeof k === 'number' ? { r: k, g: k * 0.97, b: k * 0.92, chute: 0 } : k;
    etat.teinte = [tr.r, tr.g, tr.b, tr.chute || 0].map(x => Math.round(x * 1000) / 1000); coul.setRGB(tr.r, tr.g, tr.b);
    for (const o of Object.values(clips)) { if (!o.plan.visible) continue; o.mat.uniforms.opacite.value = montre * o.poids; o.mat.uniforms.teinte.value.copy(coul); o.mat.uniforms.chute.value = tr.chute || 0; }
  });

  return { etat, pret, clips, get montre() { return montre; } };
}

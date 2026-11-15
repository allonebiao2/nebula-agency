/* LE MONDE · le moteur commun à tous les lieux.
   Rendu, niveaux de qualité, boucle. Aucun lieu n'est décrit ici.

   ⚠️ Trois niveaux, choisis TOUT SEULS selon l'appareil, puis corrigés en
   marchant : si les images tombent sous ~35 par seconde, on descend d'un
   cran (résolution, puis halo, puis reflets). Le visiteur d'Hillary a un
   Tecno ou un Infinix, pas une console.
   Forcer pour un essai : ?qualite=basse|moyenne|haute */
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';

export { THREE };

/* L'ÉTALONNAGE DE FILM, DANS LE TONE MAPPING (vague 2, 2026-11-14). Avant : seule la qualité « haute » avait un
   étalonnage (une passe d'image en plus) ; le PC de Mongazi et tous les téléphones (« moyenne », « basse ») n'en
   avaient AUCUN. Ici : l'AgX de three.js (r180) recopié, avec un « look » posé là où Blender pose les siens, dans le
   domaine encodé d'AgX, après la courbe de contraste (ASC CDL : pente, puissance, saturation). Le « Punchy » de
   Blender (1,35 et 1,4) brûle le crème et sature le wax ; dosage plus doux, réglé sur les captures. Coût : quelques
   opérations par pixel dans chaque matière, aucune passe d'image. La passe de sortie de la haute l'utilise aussi. */
/* réglé sur les captures du 2026-11-15 : à [1,03 ; 1 ; 0,955] les murs crème viraient au pêche, et à 1,16 de puissance les
   personnages du soir devenaient noirs */
export const LOOK = { pente: [1.018, 1.0, 0.975], puissance: 1.11, saturation: 1.12 };
{
  const v = (a) => `vec3(${a.map(x => x.toFixed(4)).join(', ')})`;
  const C = THREE.ShaderChunk, vide = 'vec3 CustomToneMapping( vec3 color ) { return color; }';
  if (C.tonemapping_pars_fragment.includes(vide)) C.tonemapping_pars_fragment = C.tonemapping_pars_fragment.replace(vide, `
vec3 nebulaLook( vec3 val ) {
  float luma = dot( val, vec3( 0.2126, 0.7152, 0.0722 ) );
  val = pow( max( val * ${v(LOOK.pente)}, 0.0 ), vec3( ${LOOK.puissance.toFixed(4)} ) );
  return luma + ${LOOK.saturation.toFixed(4)} * ( val - luma );
}
vec3 CustomToneMapping( vec3 color ) {
  const mat3 AgXInsetMatrix = mat3(
    vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ),
    vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ),
    vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 ) );
  const mat3 AgXOutsetMatrix = mat3(
    vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ),
    vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ),
    vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 ) );
  const float AgxMinEv = - 12.47393; const float AgxMaxEv = 4.026069;
  color *= toneMappingExposure;
  color = LINEAR_SRGB_TO_LINEAR_REC2020 * color;
  color = AgXInsetMatrix * color;
  color = max( color, 1e-10 ); color = log2( color );
  color = ( color - AgxMinEv ) / ( AgxMaxEv - AgxMinEv );
  color = clamp( color, 0.0, 1.0 );
  color = agxDefaultContrastApprox( color );
  color = nebulaLook( color );
  color = AgXOutsetMatrix * color;
  color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) );
  color = LINEAR_REC2020_TO_LINEAR_SRGB * color;
  return clamp( color, 0.0, 1.0 );
}`);
}

const PRESETS = {
  basse:   { nom: 'basse',   dpr: 0.8,  halo: false, reflets: false, pluie: 350,  ombres: false },
  moyenne: { nom: 'moyenne', dpr: 1.0,  halo: false, reflets: false, pluie: 800,  ombres: false },
  haute:   { nom: 'haute',   dpr: 1.6,  halo: true,  reflets: true,  pluie: 1500, ombres: false, cinema: true },
};

function detecterQualite(renderer) {
  const p = new URLSearchParams(location.search).get('qualite');
  if (p && PRESETS[p]) return { ...PRESETS[p], force: true, gpu: '' };
  let gpu = '';
  try {
    const gl = renderer.getContext();
    const ext = gl.getExtension('WEBGL_debug_renderer_info');
    gpu = ext ? String(gl.getParameter(ext.UNMASKED_RENDERER_WEBGL)) : '';
  } catch (e) { /* rien */ }
  const mem = navigator.deviceMemory || 4;
  const tactile = matchMedia('(pointer: coarse)').matches;
  let n = 'haute';
  if (/SwiftShader|llvmpipe|Software|Microsoft Basic/i.test(gpu)) n = 'basse';
  else if (tactile && (mem <= 3 || /Mali-4|Mali-T|PowerVR|Adreno \(TM\) [3-5]\d\d/i.test(gpu))) n = 'basse';
  else if (tactile || /Intel|HD Graphics|UHD/i.test(gpu) || mem <= 4) n = 'moyenne';
  return { ...PRESETS[n], force: false, gpu };
}

export function creerMoteur(conteneur) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance', preserveDrawingBuffer: false });
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  /* AgX : les hautes lumières se désaturent comme sur une vraie caméra (ACES « brûle » les blancs crème) */
  /* `?sans-look` : l'AgX nu d'avant (pour comparer) */
  renderer.toneMapping = new URLSearchParams(location.search).has('sans-look') ? THREE.AgXToneMapping : THREE.CustomToneMapping;
  renderer.toneMappingExposure = 1.0;
  conteneur.appendChild(renderer.domElement);
  renderer.domElement.setAttribute('aria-label', 'Le salon en 3D');

  const qualite = detecterQualite(renderer);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(68, 1, 0.05, 90);
  camera.rotation.order = 'YXZ';

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.55;

  let composer = null, halo = null, etalonnage = null, flouPasse = null;
  /* LE RENDU CINÉMA (qualité « haute » seulement : ordinateurs et appareils capables).
     Mongazi (2026-11-12) : « ressembler à GTA 6 et Call of Duty ». Trois briques de three.js (MIT) :
     - GTAO : les ombres de contact, là où un objet touche le sol ou le mur (ce qui « pose » un décor) ;
     - un étalonnage de film : contraste et chaleur légers, vignettage, grain fin ;
     - SMAA : un anticrénelage propre (le composeur contourne l'anticrénelage du moteur). */
  const ETALONNAGE = {
    uniforms: { tDiffuse: { value: null }, temps: { value: 0 }, grain: { value: 0.022 }, vignette: { value: 0.34 } },
    vertexShader: 'varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
    fragmentShader: `uniform sampler2D tDiffuse; uniform float temps, grain, vignette; varying vec2 vUv;
      float bruit(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233)) + temps) * 43758.5453); }
      void main() {
        vec4 c = texture2D(tDiffuse, vUv); vec3 col = c.rgb;
        /* le contraste, la saturation et la chaleur sont DANS le tone mapping (LOOK) : ici, vignettage et grain */
        vec2 d = vUv - 0.5; col *= 1.0 - vignette * dot(d, d) * 1.6;
        col += (bruit(vUv * 997.0) - 0.5) * grain;
        gl_FragColor = vec4(clamp(col, 0.0, 1.0), c.a);
      }`,
  };
  function monterHalo() {
    composer = new EffectComposer(renderer);
    composer.addPass(new RenderPass(scene, camera));
    if (qualite.cinema) {
      const ao = new GTAOPass(scene, camera, innerWidth, innerHeight);
      ao.output = GTAOPass.OUTPUT.Default; ao.blendIntensity = 0.9;
      ao.updateGtaoMaterial({ radius: 0.32, distanceExponent: 1.4, thickness: 1.0, scale: 1.0, samples: 12 });
      ao.updatePdMaterial({ lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 6, rings: 2, samples: 12 });
      composer.addPass(ao);
      /* la profondeur de champ des conversations (audit jeu vidéo, vague 3) : éteinte hors dialogue.
         ⚠️ le flou de three.js ne gère pas l'occlusion : un fond très clair (le disque d'un podium) « bave »
         sur la personne nette. À 0,009 il voilait les jambes d'Afi : flou plafonné à 0,0055. */
      flouPasse = new BokehPass(scene, camera, { focus: 2, aperture: 0.0018, maxblur: 0.0055 });
      flouPasse.enabled = false; composer.addPass(flouPasse);
    }
    /* ⚠️ en rendu cinéma, un halo plus fort voilait les robes de blanc laiteux (capture du 2026-11-12) */
    halo = new UnrealBloomPass(new THREE.Vector2(256, 256), qualite.cinema ? 0.16 : 0.32, 0.5, qualite.cinema ? 0.95 : 0.86);
    composer.addPass(halo);
    composer.addPass(new OutputPass());
    if (qualite.cinema) {
      etalonnage = new ShaderPass(ETALONNAGE); composer.addPass(etalonnage);
      composer.addPass(new SMAAPass());
    }
  }
  if (qualite.halo) monterHalo();
  if (!qualite.cinema) {
    const vignette = document.createElement('div'); vignette.className = 'vignette-film'; vignette.setAttribute('aria-hidden', 'true');
    vignette.style.cssText = 'position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse 75% 70% at 50% 46%, rgba(0,0,0,0) 58%, rgba(10,6,3,.28) 100%)';
    conteneur.appendChild(vignette);
  }

  let dpr = Math.min(window.devicePixelRatio || 1, qualite.dpr);
  function redimensionner() {
    const w = conteneur.clientWidth || innerWidth, h = conteneur.clientHeight || innerHeight;
    renderer.setPixelRatio(dpr);
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    /* ⚠️ 75° en HORIZONTAL, mesuré sur la scène de référence (ANALYSE-VIDEO-REFERENCE.md) :
       66° en vertical donnait ~98° en horizontal sur un écran large, un effet « fish-eye ».
       En portrait on plafonne le vertical à 80°, sinon le haut et le bas se déforment. */
    const vf = 2 * Math.atan(Math.tan((75 * Math.PI / 180) / 2) / camera.aspect) * 180 / Math.PI;
    camera.fov = Math.max(42, Math.min(80, vf));
    camera.userData.fovBase = camera.fov;
    camera.updateProjectionMatrix();
    if (composer) { composer.setPixelRatio(dpr); composer.setSize(w, h); }
  }
  addEventListener('resize', redimensionner);
  redimensionner();

  const abonnes = [];
  /* ?profil : le temps moyen de chaque tâche par image (R14, « le maximum d'images/s »), lu par moteur.profil() */
  const profil = new URLSearchParams(location.search).has('profil');
  const horloge = new THREE.Clock();
  let tempsTotal = 0, enMarche = false, sansComposition = false;
  /* mesure des images, pour descendre d'un cran si l'appareil peine */
  let fenetre = [], dernierAjustement = 0;
  function surveiller(dt) {
    if (qualite.force) return;
    fenetre.push(dt);
    if (fenetre.length < 90) return;
    const moy = fenetre.reduce((a, b) => a + b, 0) / fenetre.length;
    fenetre = [];
    if (tempsTotal - dernierAjustement < 3) return;
    /* … et REMONTER quand il y a de la marge (Mongazi, 2026-11-13 : « le maximum d'images/s ») : une baisse de
       finesse décidée pendant le chargement (pic de calcul) ne doit pas durer toute la visite */
    const plafond = Math.min(window.devicePixelRatio || 1, qualite.dpr);
    if (moy < 1 / 55 && dpr < plafond - 0.05 && tempsTotal - dernierAjustement > 6) {
      dernierAjustement = tempsTotal; dpr = Math.min(plafond, dpr + 0.1); redimensionner(); return;
    }
    if (moy > 1 / 33) {
      dernierAjustement = tempsTotal;
      if (dpr > 0.7) { dpr = Math.max(0.6, dpr - 0.2); redimensionner(); }
      else if (composer) { composer = null; halo = null; etalonnage = null; flouPasse = null; qualite.halo = false; qualite.cinema = false; }
      moteur.surDescente.forEach(f => f(qualite));
    }
  }

  function boucle() {
    if (!enMarche) return;
    requestAnimationFrame(boucle);
    const dt = Math.min(horloge.getDelta(), 0.05);
    tempsTotal += dt;
    if (profil) for (const f of abonnes) { const t0 = performance.now(); f(dt, tempsTotal); f.__ms = (f.__ms || 0) * 0.97 + (performance.now() - t0) * 0.03; }
    else for (const f of abonnes) f(dt, tempsTotal);
    if (etalonnage) etalonnage.uniforms.temps.value = tempsTotal % 100;
    if (composer && !sansComposition) composer.render(); else renderer.render(scene, camera);
    surveiller(dt);
  }

  const moteur = {
    THREE, renderer, scene, camera, qualite,
    /* flou de profondeur de champ : net à `distance` mètres, le reste se floute (qualité haute seulement) */
    flou(actif, distance = 2) { if (!flouPasse) return; flouPasse.enabled = !!actif; flouPasse.uniforms.focus.value = distance; },
    surDescente: [],
    chaqueImage(f) { abonnes.push(f); return () => abonnes.splice(abonnes.indexOf(f), 1); },
    demarrer() { if (!enMarche) { enMarche = true; horloge.getDelta(); boucle(); } },
    temps: () => tempsTotal,
    redimensionner,
    /* la force du halo selon l'heure (la ligne dorée brille plus la nuit) */
    /* `seuil` (facultatif) : au-dessus de quelle luminance un pixel rayonne. Une pièce claire dépasse 0,95
       partout et tout l'écran devenait laiteux (salon crème, 2026-11-13) : seules les lampes doivent rayonner */
    profil: () => abonnes.filter(f => f.__ms).sort((a, b) => b.__ms - a.__ms).slice(0, 12).map(f => [Math.round(f.__ms * 100) / 100, f.toString().replace(/\s+/g, ' ').slice(0, 90)]),
    /* le monde photographique (socle/monde-photo.js) porte déjà sa lumière et ses couleurs : ni ombres de
       contact, ni halo, ni étalonnage par-dessus (ils délavaient la photo et ne coûtaient que des images/s) */
    composition(oui) { sansComposition = !oui; },
    reglerHalo(force, seuil) { if (halo) { halo.strength = force; if (seuil != null) halo.threshold = seuil; } },
  };
  return moteur;
}

/* ---------- petits outils partagés ---------- */
export const lisser = (t) => t * t * (3 - 2 * t);
export const doux = (t) => 0.5 - 0.5 * Math.cos(Math.PI * Math.min(1, Math.max(0, t)));
export const borner = (v, a, b) => Math.max(a, Math.min(b, v));
export const melanger = (a, b, t) => a + (b - a) * t;
export function angleVers(a, b) { let d = b - a; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return d; }
export const rad = (deg) => deg * Math.PI / 180;

/* hasard reproductible : les mêmes façades à chaque visite */
export function graine(s) { let x = s >>> 0 || 1; return () => ((x = (x * 1664525 + 1013904223) >>> 0) / 4294967296); }

export function texteCanvas(w, h, dessiner) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  dessiner(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}

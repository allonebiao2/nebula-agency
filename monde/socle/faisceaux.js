/* LE MONDE · les faisceaux qu'on VOIT : le cône de lumière d'un projecteur, et la poussière qui danse dedans.

   Mongazi (2026-11-14) : « le soir, des spots qui découpent les robes dans la pénombre, la poussière qui danse dans
   les faisceaux ». Un SpotLight de three.js éclaire, mais l'air reste invisible : une maison de couture le soir,
   c'est d'abord le faisceau qu'on voit tomber sur la robe. Ici, ce que font les jeux sur téléphone :
   - un cône additif (aucune ombre, aucun calcul de volume) : clair à la source, qui s'efface vers le sol et sur ses
     bords (on regarde l'épaisseur traversée : un bord de cône vu de biais est presque vide) ;
   - une brume qui bouge à peine dedans (un bruit lent), pour que l'air ait de la matière ;
   - des grains de poussière (des points) qui dérivent lentement et scintillent quand ils passent dans la lumière.
   Coût : un maillage et un nuage de points par projecteur, aucune passe d'image ; la poussière dépend de la
   qualité (aucune en « basse »). La force suit l'allumage du projecteur et l'heure (presque rien en plein jour). */
import { THREE } from './moteur.js';

const VS_CONE = `varying vec3 vN, vV; varying float vH; varying vec3 vP;
void main() {
  vec4 mp = modelMatrix * vec4(position, 1.0); vP = mp.xyz;
  vN = normalize(mat3(modelMatrix) * normal); vV = normalize(cameraPosition - mp.xyz);
  vH = uv.y;   /* 1 à la source, 0 au sol */
  gl_Position = projectionMatrix * viewMatrix * mp;
}`;
const FS_CONE = `uniform vec3 couleur; uniform float force, temps; varying vec3 vN, vV, vP; varying float vH;
float h(vec3 p) { return fract(sin(dot(p, vec3(12.9898, 78.233, 37.719))) * 43758.5453); }
float bruit(vec3 p) { vec3 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(mix(h(i), h(i + vec3(1,0,0)), f.x), mix(h(i + vec3(0,1,0)), h(i + vec3(1,1,0)), f.x), f.y),
             mix(mix(h(i + vec3(0,0,1)), h(i + vec3(1,0,1)), f.x), mix(h(i + vec3(0,1,1)), h(i + vec3(1,1,1)), f.x), f.y), f.z); }
void main() {
  /* l'épaisseur traversée : de face au centre du cône, presque rien sur le bord vu de biais */
  float epais = pow(abs(dot(normalize(vN), normalize(vV))), 1.6);
  /* plus dense à la source, qui s'efface en arrivant au sol (sans ligne dure) */
  /* dense à la source, DISSOUS avant la pièce éclairée (elle est dans le tiers bas du cône) : le faisceau se voit
     tomber du plafond, il ne voile pas la robe. ⚠️ « long » est un mot réservé de GLSL */
  float duHaut = smoothstep(0.12, 0.78, vH);
  float brume = 0.75 + 0.25 * bruit(vP * 2.3 + vec3(0.0, -temps * 0.06, temps * 0.03));
  float a = epais * duHaut * brume * force;
  gl_FragColor = vec4(couleur * a, 1.0);
}`;
const VS_GRAINS = `attribute float graine; uniform float temps, taille; varying float vScint;
void main() {
  vScint = 0.35 + 0.65 * pow(0.5 + 0.5 * sin(temps * (0.6 + graine * 1.7) + graine * 40.0), 3.0);
  vec4 mv = modelViewMatrix * vec4(position, 1.0);
  gl_PointSize = taille * (0.6 + graine * 0.8) / max(0.3, -mv.z);
  gl_Position = projectionMatrix * mv;
}`;
const FS_GRAINS = `uniform vec3 couleur; uniform float force; varying float vScint;
void main() { vec2 d = gl_PointCoord - 0.5; float r = dot(d, d); if (r > 0.25) discard;
  float a = (1.0 - r * 4.0); gl_FragColor = vec4(couleur * a * a * vScint * force, 1.0); }`;

/* `projecteurs` : [{ lumiere (SpotLight), base (sa pleine intensité, avant l'allumage), sol (hauteur du sol, 0) }] ; `nuit()` : 0 le jour → 1 le soir ;
   `densite` : grains par projecteur (0 = aucune poussière) */
export function creerFaisceaux({ moteur, projecteurs, nuit = () => 1, densite = 60, forceMax = 0.22 }) {
  const { scene, camera } = moteur;
  const groupe = new THREE.Group(); groupe.userData.garder = true; scene.add(groupe);
  const liste = [];
  const haut = new THREE.Vector3(0, 1, 0), dir = new THREE.Vector3(), q = new THREE.Quaternion();
  for (const p of projecteurs) {
    const l = p.lumiere, src = l.position.clone(), cible = l.target.position.clone();
    dir.copy(cible).sub(src).normalize();
    /* le cône va jusqu'au sol, le long de l'axe du projecteur */
    const t = dir.y < -1e-3 ? (src.y - (p.sol || 0)) / -dir.y : 4;
    const L = Math.min(t, l.distance || 8), R = Math.tan(l.angle) * L * 0.92;
    const geo = new THREE.ConeGeometry(R, L, 40, 1, true);
    geo.translate(0, -L / 2, 0);   /* la pointe à l'origine, le cône qui descend le long de −y */
    /* uv.y : 1 en haut (la source), 0 en bas : celui de ConeGeometry convient */
    const mat = new THREE.ShaderMaterial({ vertexShader: VS_CONE, fragmentShader: FS_CONE, transparent: true, depthWrite: false,
      blending: THREE.AdditiveBlending, side: THREE.DoubleSide, toneMapped: false,
      uniforms: { couleur: { value: new THREE.Color(l.color).multiplyScalar(1.0) }, force: { value: 0 }, temps: { value: 0 } } });
    const cone = new THREE.Mesh(geo, mat); cone.renderOrder = 4; cone.frustumCulled = false;
    cone.position.copy(src);
    q.setFromUnitVectors(new THREE.Vector3(0, -1, 0), dir); cone.quaternion.copy(q);
    groupe.add(cone);
    let grains = null;
    if (densite > 0) {
      const pos = new Float32Array(densite * 3), graine = new Float32Array(densite), base = [];
      for (let i = 0; i < densite; i++) {
        /* un point au hasard DANS le cône (plus dense vers le haut, où l'on regarde) */
        const y = -L * Math.pow(Math.random(), 0.8) * 0.95, rr = R * (-y / L) * Math.sqrt(Math.random()) * 0.85, a = Math.random() * Math.PI * 2;
        base.push(new THREE.Vector3(Math.cos(a) * rr, y, Math.sin(a) * rr));
        graine[i] = Math.random();
      }
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('graine', new THREE.BufferAttribute(graine, 1));
      const m = new THREE.ShaderMaterial({ vertexShader: VS_GRAINS, fragmentShader: FS_GRAINS, transparent: true, depthWrite: false,
        blending: THREE.AdditiveBlending, toneMapped: false,
        uniforms: { couleur: { value: new THREE.Color(l.color) }, force: { value: 0 }, temps: { value: 0 }, taille: { value: 18 * Math.min(2, devicePixelRatio || 1) } } });
      grains = new THREE.Points(g, m); grains.frustumCulled = false; grains.renderOrder = 5;
      grains.position.copy(src); grains.quaternion.copy(q);
      groupe.add(grains);
      grains.userData = { base, graine, L, R };
    }
    liste.push({ l, base: p.base || l.intensity || 1, cone, mat, grains, src: src.clone(), axe: dir.clone(), L });
  }

  let temps = 0; const vCam = new THREE.Vector3();
  moteur.chaqueImage((dt) => {
    temps += dt;
    const n = THREE.MathUtils.clamp(nuit(), 0, 1), k = 0.18 + 0.82 * n;   /* de jour, un souffle ; le soir, pleinement */
    for (const f of liste) {
      const allume = THREE.MathUtils.clamp(f.l.intensity / Math.max(1e-6, f.base), 0, 1);
      /* DE PRÈS, un faisceau ne se voit pas (on est dedans) et il voilerait ce qu'on regarde : il s'efface à moins de
         1,2 m de son axe et n'est plein qu'au-delà de 4,5 m (vu à l'ordinateur le 2026-11-15 : un voile blanc sur la
         robe du premier plan) */
      vCam.copy(camera.position).sub(f.src); const le = THREE.MathUtils.clamp(vCam.dot(f.axe), 0, f.L);
      const dAxe = vCam.addScaledVector(f.axe, -le).length();
      const pres = THREE.MathUtils.smoothstep(dAxe, 1.2, 4.5);
      const force = forceMax * k * allume * pres;
      f.mat.uniforms.force.value = force; f.mat.uniforms.temps.value = temps;
      f.cone.visible = force > 0.002;
      if (f.grains) {
        const { base, graine, L } = f.grains.userData, pos = f.grains.geometry.attributes.position;
        /* la dérive : lente, en spirale, qui retombe doucement et remonte (l'air chaud du spot) */
        for (let i = 0; i < base.length; i++) {
          const b = base[i], s = graine[i] * 6.28, v = 0.05 + graine[i] * 0.05;
          pos.setXYZ(i, b.x + Math.sin(temps * v * 2 + s) * 0.06, b.y + Math.sin(temps * v + s * 1.3) * 0.08 - ((temps * 0.012 * (0.5 + graine[i])) % 0.15),
            b.z + Math.cos(temps * v * 1.7 + s) * 0.06);
        }
        pos.needsUpdate = true;
        f.grains.material.uniforms.force.value = force * 2.2; f.grains.material.uniforms.temps.value = temps;
        f.grains.visible = force > 0.002;
      }
    }
  });
  return { liste, groupe };
}

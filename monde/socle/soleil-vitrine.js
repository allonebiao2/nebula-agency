/* LE MONDE · le soleil qui entre par la vitrine : des flaques de lumière chaude sur le sol poli.

   Mongazi (2026-11-14) : « le jour qui entre par la vitrine et se pose en flaques chaudes sur un sol poli qui
   reflète tout ». Le salon suit le vrai soleil de Cotonou (`ciel.js`), mais sans ombres portées (trop chères au
   téléphone) le soleil n'« entrait » nulle part. Ici, la géométrie fait le travail d'une ombre : chaque ouverture
   de la façade (vitrines, porte) est PROJETÉE sur le sol le long de la direction du soleil. Le résultat est exact
   (la flaque est là où le soleil tombe vraiment, elle s'allonge quand il descend, elle glisse avec l'heure) et ne
   coûte que trois quadrilatères additifs. Les montants de laiton de la vitrine y laissent leur ombre ; les bords
   s'adoucissent en s'éloignant du vitrage (la pénombre du soleil) ; la flaque est coupée aux murs de la pièce.

   `ouvertures` : [{ x1, x2, bas, haut, montants }] sur le plan de la façade (z = facadeZ, la pièce est du côté −z).
   ⚠️ Il faut que la façade REGARDE le soleil : voir `capFacade` dans `ciel.js` (à Cotonou le soleil est au sud dix
   mois sur douze ; une vitrine plein nord ne reçoit jamais rien). */
import { THREE } from './moteur.js';

const VS = `varying vec2 vUv; varying vec3 vW;
void main() { vUv = uv; vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`;
const FS = `uniform vec3 couleur; uniform float force, montants; uniform vec4 piece; varying vec2 vUv; varying vec3 vW;
void main() {
  if (vW.x < piece.x || vW.x > piece.y || vW.z < piece.z || vW.z > piece.w) discard;
  /* vUv.y : 0 au pied du vitrage → 1 au bout de la flaque ; la pénombre s'élargit avec la distance */
  float pen = mix(0.012, 0.10, vUv.y);
  float a = smoothstep(0.0, pen, vUv.x) * smoothstep(0.0, pen, 1.0 - vUv.x)
          * smoothstep(0.0, 0.02 + pen, vUv.y) * smoothstep(0.0, 0.03 + pen * 1.4, 1.0 - vUv.y);
  if (montants > 0.5) {
    float f = fract(vUv.x * (montants + 1.0)); float d = min(f, 1.0 - f) / (montants + 1.0);
    /* l'ombre d'un montant de 4 cm se dissout avec la distance (le soleil n'est pas un point : sa pénombre grandit de
       9 mm par mètre) : nette au pied du vitrage, presque effacée au bout de la flaque */
    a *= mix(mix(0.55, 0.94, vUv.y), 1.0, smoothstep(0.002, 0.005 + 0.022 * vUv.y, d));
  }
  gl_FragColor = vec4(couleur * (a * force), 1.0);
}`;

export function creerSoleilVitrine({ moteur, ciel, facadeZ, ouvertures, piece, forceMax = 0.4, ySol = 0.008 }) {
  const { scene } = moteur;
  const groupe = new THREE.Group(); groupe.userData.garder = true; scene.add(groupe);
  const flaques = ouvertures.map((o) => {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(12), 3));
    geo.setAttribute('uv', new THREE.BufferAttribute(new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]), 2));
    geo.setIndex([0, 2, 1, 0, 3, 2]);
    const mat = new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: FS, transparent: true, depthWrite: false, side: THREE.DoubleSide,
      /* le soleil ÉCLAIRCIT le sol, il ne le recouvre pas : sol × (1 + soleil). En additif simple, la flaque était un
         aplat blanc sans matière (vu le 2026-11-15) ; ainsi le grain du sol, ses joints et les ombres de contact restent */
      blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.DstColorFactor, blendDst: THREE.OneFactor, toneMapped: false,
      uniforms: { couleur: { value: new THREE.Color(1, 0.9, 0.75) }, force: { value: 0 }, montants: { value: o.montants || 0 },
        piece: { value: new THREE.Vector4(piece.x1, piece.x2, piece.z1, piece.z2) } } });
    const m = new THREE.Mesh(geo, mat); m.frustumCulled = false; m.renderOrder = 2; m.visible = false;
    groupe.add(m);
    return { o, m, geo, mat };
  });
  const dir = new THREE.Vector3(), chaud = new THREE.Color(1, 0.965, 0.89);
  const etat = { force: 0, profondeur: 0, part: 0 };

  moteur.chaqueImage(() => {
    const e = ciel.etat;
    dir.copy(ciel.soleil.position).normalize();   /* vers le soleil */
    /* le soleil est-il DEVANT la façade (côté +z), assez haut, et le ciel assez dégagé ? */
    const devant = THREE.MathUtils.smoothstep(dir.z, 0.03, 0.25), haut = THREE.MathUtils.smoothstep(dir.y, 0.06, 0.22);
    const voile = Math.max(0, 1 - (e.nuages || 0) * 0.65 - (e.pluie || 0) * 0.9 - (e.brume || 0) * 0.5);
    const force = forceMax * (e.jour || 0) * devant * haut * voile;
    etat.force = Math.round(force * 1000) / 1000; etat.part = forceMax > 0 ? force / forceMax : 0;   /* 0 → 1 : pour l'exposition du lieu */
    for (const f of flaques) {
      f.m.visible = force > 0.004;
      if (!f.m.visible) continue;
      const p = f.geo.attributes.position, k = Math.min(1 / dir.y, 26);   /* jamais plus de 26 m par mètre de hauteur */
      const proj = (i, x, y) => p.setXYZ(i, x - dir.x * y * k, ySol, facadeZ - dir.z * y * k);
      proj(0, f.o.x1, f.o.bas); proj(1, f.o.x2, f.o.bas); proj(2, f.o.x2, f.o.haut); proj(3, f.o.x1, f.o.haut);
      p.needsUpdate = true;
      f.mat.uniforms.force.value = force;
      /* un peu plus chaud que le soleil lui-même : la lumière qui a traversé le vitrage et rebondi sur un sol crème */
      f.mat.uniforms.couleur.value.copy(ciel.soleil.color).multiply(chaud);
    }
    etat.profondeur = Math.round(dir.z * (ouvertures[0] ? ouvertures[0].haut : 3) * Math.min(1 / dir.y, 26) * 100) / 100;
  });
  return { etat, flaques, groupe };
}

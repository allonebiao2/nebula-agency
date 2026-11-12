/* LE MONDE · habiller une silhouette d'un VRAI personnage 3D (squelette et animations Mixamo, FBX).
   Mongazi (2026-11-12) : « je ne veux pas de Lego, je veux de vrais personnages 3D ».

   La silhouette de maquette reste le repli : tant que le modèle n'est pas arrivé (ou s'il
   échoue), c'est elle qu'on voit, et elle continue de calculer l'état du personnage
   (vitesse, parole, écoute, geste, regard). Le modèle lit cet état et choisit son
   animation : rien d'autre dans le salon ne change.

   Fichiers attendus dans `dossier` : <prefixe>-attendre.fbx (AVEC le corps), puis, sans le
   corps : -marcher (sur place), -parler, -saluer, -hocher, -reflechir, -regarder. */
import { THREE } from './moteur.js';
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';
import { mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';

const ANIMATIONS = ['marcher', 'parler', 'saluer', 'hocher', 'reflechir', 'regarder'];

/* l'état de la silhouette → l'animation du corps */
function animationVoulue(st) {
  if (st.vitesse > 0.05) return 'marcher';
  if (st.geste === 'saluer') return 'saluer';
  if (st.parle) return 'parler';
  if (st.ecoute) return 'hocher';
  if (st.geste === 'regarder' || st.geste === 'toucher') return 'reflechir';
  if (st.geste === 'fenetre' || st.geste === 'photo') return 'regarder';
  return 'attendre';
}

export async function habiller(perso, { dossier, prefixe, taille, vitesseMarche = 1.2, fondu = 0.35 }) {
  const chargeur = new FBXLoader();
  const charger = (nom) => new Promise((ok, ko) => chargeur.load(`${dossier}${prefixe}-${nom}.fbx`, ok, undefined, ko));

  const modele = await charger('attendre');

  /* des matières qui répondent à la lumière du salon comme le décor (l'export Mixamo est en Phong) */
  modele.traverse((o) => {
    if (!o.isMesh) return;
    o.castShadow = false; o.receiveShadow = false;
    /* ⚠️ L'EXPORT MIXAMO D'UN OBJ ARRIVE SANS NORMALES, et « éclaté » (343 854 sommets pour
       115 000 triangles, aucun partagé) : sans normales la lumière ne s'y pose pas, le corps
       est NOIR (vu le 2026-11-12). On soude les sommets identiques, puis on recalcule des
       normales lisses : le corps s'éclaire, et la carte graphique a trois fois moins à animer. */
    if (!o.geometry.attributes.normal) {
      const g = mergeVertices(o.geometry, 1e-5);
      g.computeVertexNormals();
      o.geometry.dispose(); o.geometry = g;
    }
    o.frustumCulled = false;   /* la boîte d'un corps animé suit mal le squelette : pas de disparition */
    const convertir = (m) => {
      const n = new THREE.MeshStandardMaterial({ map: m.map || null, color: m.map ? 0xffffff : m.color, roughness: 0.82, metalness: 0 });
      if (n.map) n.map.colorSpace = THREE.SRGBColorSpace;
      return n;
    };
    o.material = Array.isArray(o.material) ? o.material.map(convertir) : convertir(o.material);
  });

  const melangeur = new THREE.AnimationMixer(modele);
  const actions = {};
  const ajouter = (nom, clip) => { if (clip) { clip.name = nom; actions[nom] = melangeur.clipAction(clip); } };
  ajouter('attendre', modele.animations[0]);
  if (!actions.attendre) throw new Error(`${prefixe} : aucune animation dans ${prefixe}-attendre.fbx`);
  let courante = 'attendre';
  actions.attendre.play();

  /* à sa vraie taille, les pieds au sol. ⚠️ On mesure sur les OS (sommet de la tête, bout
     des orteils) ET APRÈS la première image de l'animation : la boîte d'un maillage skinné se
     calcule sur la géométrie brute, et le squelette au repos est centré, alors que
     l'animation remet les pieds au sol. Mesuré avant, Afi flottait à un mètre (2026-11-12). */
  melangeur.update(0);
  modele.updateMatrixWorld(true);
  let haut = -Infinity, bas = Infinity;
  const w = new THREE.Vector3();
  modele.traverse((o) => {
    if (!o.isBone) return;
    o.getWorldPosition(w);
    if (/HeadTop_End$/.test(o.name)) haut = Math.max(haut, w.y);
    if (/(Toe_End|ToeBase)$/.test(o.name)) bas = Math.min(bas, w.y);
  });
  if (!isFinite(haut) || !isFinite(bas)) { const b = new THREE.Box3().setFromObject(modele, true); haut = b.max.y; bas = b.min.y; }
  const s = taille / Math.max(1e-6, haut - bas);
  modele.scale.multiplyScalar(s);
  modele.position.y = -bas * s;

  /* la tête suit encore le regard que la silhouette calcule (vers le joueur, vers une autre) */
  let tete = null;
  modele.traverse((o) => { if (!tete && o.isBone && /Head$/.test(o.name)) tete = o; });
  const e = new THREE.Euler(0, 0, 0, 'YXZ'), q = new THREE.Quaternion();

  /* le corps remplace la silhouette */
  perso.racine.add(modele);
  perso.corps.visible = false;
  if (tete) perso.positionTete = (v = new THREE.Vector3()) => tete.getWorldPosition(v);

  const majSilhouette = perso.maj;
  perso.maj = (dt, t) => {
    majSilhouette(dt, t);
    const st = perso.st;
    let voulue = animationVoulue(st);
    if (!actions[voulue]) voulue = 'attendre';
    if (voulue !== courante) {
      const de = actions[courante], vers = actions[voulue];
      vers.reset(); vers.setEffectiveTimeScale(1); vers.setEffectiveWeight(1); vers.play();
      vers.crossFadeFrom(de, fondu, true);
      courante = voulue;
    }
    if (courante === 'marcher') actions.marcher.setEffectiveTimeScale(THREE.MathUtils.clamp(st.vitesse / vitesseMarche, 0.6, 1.6));
    melangeur.update(dt);
    if (tete) { e.set(st.teteTangage * 0.8, st.teteLacet * 0.8, 0); tete.quaternion.multiply(q.setFromEuler(e)); }
  };

  /* les autres animations arrivent ensuite, sans retenir l'apparition du corps */
  Promise.allSettled(ANIMATIONS.map(n => charger(n).then(o => ajouter(n, o.animations[0]))))
    .then(r => { const rates = r.filter(x => x.status === 'rejected').length; if (rates) console.warn(`${prefixe} : ${rates} animation(s) manquante(s)`); });

  return { modele, actions };
}

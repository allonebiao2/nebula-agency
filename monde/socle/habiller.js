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
import { ombreContact } from './matieres.js';

const ANIMATIONS = ['marcher', 'parler', 'saluer', 'hocher', 'reflechir', 'regarder', 'parler-2', 'attendre-2', 'demarrer', 'arreter'];
/* plusieurs gestes par situation, tirés au hasard (audit jeu vidéo, vague 2) : jamais le même en boucle */
const VARIANTES = { parler: ['parler', 'parler-2'], attendre: ['attendre', 'attendre-2'] };
/* jouées une fois, autour de la marche ; leur déplacement propre est retiré (c'est le code qui fait avancer) */
const UNE_FOIS = new Set(['demarrer', 'arreter']);

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

/* `gestes` (facultatif) : { dossier, prefixe } d'un AUTRE personnage dont on rejoue les animations. Tous les
   squelettes Mixamo portent les mêmes noms d'os : un seul téléchargement par personnage (son corps, avec
   `attendre`), les douze autres gestes viennent d'Afi. Seules les ROTATIONS passent d'un corps à l'autre ;
   la position du bassin est remise à l'échelle du nouveau corps (sinon il flotte ou s'enfonce), et les
   positions des autres os sont jetées (elles imposeraient les longueurs d'os de l'autre). */
/* `texture` (facultatif) : une texture qui REMPLACE celle du fichier (même dépliage) : le visage reprojeté depuis
   l'image d'origine par `_outils/projeter_visage.py` (Mongazi, 2026-11-13 : « les visages sont catastrophiques »). */
export async function habiller(perso, { dossier, prefixe, taille, vitesseMarche = 1.2, fondu = 0.35, gestes = null, texture = null }) {
  const chargeur = new FBXLoader();
  const charger = (nom) => new Promise((ok, ko) => chargeur.load(`${dossier}${prefixe}-${nom}.fbx`, ok, undefined, ko));
  const chargerGeste = gestes ? (nom) => new Promise((ok, ko) => chargeur.load(`${gestes.dossier}${gestes.prefixe}-${nom}.fbx`, ok, undefined, ko)) : charger;
  /* la hauteur du bassin DEBOUT, lue sur la PREMIÈRE IMAGE d'une animation debout. ⚠️ Pas sur la pose de repos
     du fichier : celle de la nouvelle Afi (Mixamo) met le bassin à −0,06 contre +0,03 chez l'ancienne, le
     rapport devenait NÉGATIF et le corps passait 1,76 m sous le sol, invisible (2026-11-13). */
  const bassinDebout = (clip) => { const p = clip && clip.tracks.find(x => /Hips\.position$/.test(x.name)); return p ? p.values[1] : null; };

  const modele = await charger('attendre');
  const bassinCible = bassinDebout(modele.animations[0]);   /* son « attendre », debout */

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
    if (texture) new THREE.TextureLoader().load(texture, (tx) => {
      tx.colorSpace = THREE.SRGBColorSpace; tx.anisotropy = 4;
      for (const m of [].concat(o.material)) if (m.map) { tx.flipY = m.map.flipY; tx.wrapS = m.map.wrapS; tx.wrapT = m.map.wrapT; m.map = tx; m.needsUpdate = true; }
    });
  });

  const melangeur = new THREE.AnimationMixer(modele);
  const actions = {};
  const ajouter = (nom, clip) => {
    if (!clip) return;
    clip.name = nom;
    if (UNE_FOIS.has(nom)) for (const piste of clip.tracks) if (/Hips\.position$/.test(piste.name)) {
      const v = piste.values, x0 = v[0], z0 = v[2];
      for (let i = 0; i < v.length; i += 3) { v[i] = x0; v[i + 2] = z0; }
    }
    actions[nom] = melangeur.clipAction(clip);
    if (UNE_FOIS.has(nom)) { actions[nom].setLoop(THREE.LoopOnce, 1); actions[nom].clampWhenFinished = true; }
  };
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
  let tete = null, cou = null;
  modele.traverse((o) => { if (!tete && o.isBone && /Head$/.test(o.name)) tete = o; if (!cou && o.isBone && /Neck$/.test(o.name)) cou = o; });
  const e = new THREE.Euler(0, 0, 0, 'YXZ'), q = new THREE.Quaternion();

  /* LES OMBRES DES PIEDS (REALISME.md R2) : une petite ombre allongée sous chaque pied, qui le suit et pâlit
     quand il se lève ; l'ombre large suit le bassin (un geste le déplace). Les os sont lus après l'animation. */
  const os = {};
  modele.traverse((o) => { if (o.isBone) for (const k of ['Hips', 'LeftFoot', 'RightFoot']) if (!os[k] && new RegExp(k + '$').test(o.name)) os[k] = o; });
  const piedsOmbre = [];
  if (os.LeftFoot && os.RightFoot && perso.ombre) {
    for (let i = 0; i < 2; i++) {
      const p = ombreContact(0.11, 0.55); p.scale.set(0.75, 1, 1.5); p.position.y = 0.002;
      perso.racine.add(p); piedsOmbre.push(p);
    }
  }
  const vPied = new THREE.Vector3();

  /* le corps remplace la silhouette */
  perso.racine.add(modele);
  perso.corps.visible = false;
  if (tete) perso.positionTete = (v = new THREE.Vector3()) => tete.getWorldPosition(v);

  const majSilhouette = perso.maj;
  /* l'état « de base » (marcher, parler, attendre…) et le clip qui le joue (une variante) */
  let base = 'attendre', transitoire = null, prochainChangement = 0, rotPrec = perso.racine.rotation.y;
  const dernier = {};
  function choisir(b) {
    const liste = (VARIANTES[b] || [b]).filter(n => actions[n]);
    if (!liste.length) return actions[b] ? b : 'attendre';
    let n = liste[Math.floor(Math.random() * liste.length)];
    if (liste.length > 1 && n === dernier[b]) n = liste[(liste.indexOf(n) + 1) % liste.length];
    return (dernier[b] = n);
  }
  function jouer(nom, duree = fondu) {
    const vers = actions[nom]; if (!vers || nom === courante) return;
    const de = actions[courante];
    vers.reset(); vers.setEffectiveTimeScale(1); vers.setEffectiveWeight(1); vers.play();
    if (de) vers.crossFadeFrom(de, duree, true);
    courante = nom;
  }
  melangeur.addEventListener('finished', (ev) => { if (transitoire && ev.action === actions[transitoire]) transitoire = null; });

  perso.maj = (dt, t) => {
    majSilhouette(dt, t);
    const st = perso.st;
    let voulue = animationVoulue(st);
    if (!actions[voulue] && !VARIANTES[voulue]) voulue = 'attendre';
    /* une animation jouée une fois se laisse finir, sauf si l'on se met à parler ou à saluer */
    if (transitoire && (voulue === 'parler' || voulue === 'saluer')) transitoire = null;
    if (!transitoire) {
      if (voulue !== base) {
        if (voulue === 'marcher' && actions.demarrer) { jouer('demarrer', 0.2); transitoire = 'demarrer'; }
        else if (base === 'marcher' && voulue !== 'parler' && voulue !== 'saluer' && actions.arreter) { jouer('arreter', 0.25); transitoire = 'arreter'; }
        else jouer(choisir(voulue));
        base = voulue; prochainChangement = t + 6 + Math.random() * 4;
      } else if (UNE_FOIS.has(courante)) {
        jouer(choisir(base), 0.3);   /* le départ ou l'arrêt fini, on enchaîne sur la marche ou l'attente */
      } else if ((base === 'parler' || base === 'attendre') && t > prochainChangement) {
        jouer(choisir(base), 0.6);   /* une longue réplique, une longue attente : le geste change */
        prochainChangement = t + (base === 'parler' ? 5 + Math.random() * 3 : 9 + Math.random() * 5);
      }
    }
    /* la marche suit la vitesse réelle ; à l'arrêt, si elle pivote, ses pieds piétinent au lieu de glisser */
    const vitesseRot = Math.abs(Math.atan2(Math.sin(perso.racine.rotation.y - rotPrec), Math.cos(perso.racine.rotation.y - rotPrec))) / Math.max(dt, 1e-3);
    rotPrec = perso.racine.rotation.y;
    if (courante === 'marcher') actions.marcher.setEffectiveTimeScale(THREE.MathUtils.clamp(st.vitesse / vitesseMarche, 0.6, 1.6));
    if (!transitoire && base === 'attendre' && vitesseRot > 1.2 && actions.marcher && courante !== 'marcher') { jouer('marcher', 0.15); actions.marcher.setEffectiveTimeScale(0.55); }
    else if (base === 'attendre' && courante === 'marcher' && vitesseRot < 0.3) jouer(choisir('attendre'), 0.3);
    melangeur.update(dt);
    if (piedsOmbre.length) {
      perso.racine.updateMatrixWorld(true);
      [os.LeftFoot, os.RightFoot].forEach((b, i) => {
        b.getWorldPosition(vPied); const haut = vPied.y;
        perso.racine.worldToLocal(vPied); piedsOmbre[i].position.x = vPied.x; piedsOmbre[i].position.z = vPied.z + 0.04;
        const k = THREE.MathUtils.clamp(1 - (haut - 0.09) / 0.14, 0, 1);   /* le pied se lève : son ombre pâlit */
        piedsOmbre[i].userData.large.material.opacity = 0.55 * k; piedsOmbre[i].userData.serree.material.opacity = 0.8 * k;
      });
      if (os.Hips) { os.Hips.getWorldPosition(vPied); perso.racine.worldToLocal(vPied); perso.ombre.position.x = vPied.x; perso.ombre.position.z = vPied.z; }
    }
    /* le regard : le cou en prend 40 %, la tête 60 % (une tête seule qui tourne fait poupée) */
    if (tete) {
      if (cou) { e.set(st.teteTangage * 0.3, st.teteLacet * 0.35, 0); cou.quaternion.multiply(q.setFromEuler(e)); }
      e.set(st.teteTangage * (cou ? 0.5 : 0.8), st.teteLacet * (cou ? 0.5 : 0.8), 0); tete.quaternion.multiply(q.setFromEuler(e));
    }
  };

  /* les autres animations arrivent ensuite, sans retenir l'apparition du corps */
  /* la référence de l'autre personnage : SON attente debout (« attendre-2 »), chargée d'abord */
  const bassinSource = gestes ? await chargerGeste('attendre-2').then(o => bassinDebout(o.animations[0])).catch(() => null) : null;
  const k = bassinSource && bassinCible && bassinSource > 0 && bassinCible > 0 ? bassinCible / bassinSource : 1;
  const adapter = (o) => {
    const clip = o.animations[0];
    if (!gestes || !clip) return clip;
    clip.tracks = clip.tracks.filter(p => !/\.position$/.test(p.name) || /Hips\.position$/.test(p.name));
    for (const p of clip.tracks) if (/Hips\.position$/.test(p.name)) for (let i = 0; i < p.values.length; i++) p.values[i] *= k;
    return clip;
  };
  Promise.allSettled(ANIMATIONS.map(n => chargerGeste(n).then(o => ajouter(n, adapter(o)))))
    .then(r => { const rates = r.filter(x => x.status === 'rejected').length; if (rates) console.warn(`${prefixe} : ${rates} animation(s) manquante(s)`); });

  /* pour les contrôles : le geste joué en ce moment */
  perso.animation = () => courante;
  return { modele, actions };
}

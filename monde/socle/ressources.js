/* LE MONDE · les ressources RÉELLES : éclairage photographié, matières scannées, objets scannés.
   Poly Haven, CC0 (monde/socle/ressources/polyhaven/LICENCE.md).

   ⚠️ CHARGÉES APRÈS L'OUVERTURE : on entre tout de suite dans le salon (matières simples),
   puis il s'embellit pendant qu'on regarde. En 3G, attendre 6 Mo avant d'entrer, c'est
   perdre le visiteur. Si un fichier manque, la version simple reste : rien ne casse.

   Mongazi (2026-11-12) : « le graphisme et la qualité doivent ressembler à Call of Duty
   Korea, GTA 6 ». Ce qui sépare une maquette d'un décor qui a l'air réel : la lumière
   photographiée (HDR), les matières photographiées, les objets scannés. */
import { THREE } from './moteur.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { HDRLoader } from 'three/addons/loaders/HDRLoader.js';

export function creerRessources(moteur, base = '../../socle/ressources/polyhaven/') {
  const { renderer, scene } = moteur;
  const tex = new THREE.TextureLoader();
  const gltf = new GLTFLoader();
  const pmrem = new THREE.PMREMGenerator(renderer);
  const cacheObjets = new Map();

  function texture(chemin, couleur = false, repeat = [1, 1]) {
    return new Promise((ok) => tex.load(base + chemin, (t) => {
      if (couleur) t.colorSpace = THREE.SRGBColorSpace;
      t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]);
      t.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
      ok(t);
    }, undefined, () => ok(null)));
  }

  return {
    /* la lumière photographiée d'un vrai studio : elle donne aux matières leurs reflets */
    async eclairage(nom = 'photo_studio_loft_hall', intensite = 0.7) {
      return new Promise((ok) => new HDRLoader().load(base + nom + '/eclairage_1k.hdr', (hdr) => {
        const env = pmrem.fromEquirectangular(hdr).texture; hdr.dispose();
        scene.environment = env; scene.environmentIntensity = intensite;
        ok(true);
      }, undefined, () => ok(false)));
    },
    /* une matière scannée posée SUR un matériau existant : tout ce qui l'utilise change d'un coup */
    async matiere(materiau, nom, { repeat = [1, 1], teinte = null, rugosite = null, relief = 1 } = {}) {
      const [d, n, r] = await Promise.all([
        texture(`${nom}/diffuse.webp`, true, repeat), texture(`${nom}/nor_gl.webp`, false, repeat), texture(`${nom}/rough.webp`, false, repeat)]);
      if (!d) return false;
      materiau.map = d;
      if (n) { materiau.normalMap = n; materiau.normalScale = new THREE.Vector2(relief, relief); }
      if (r) materiau.roughnessMap = r;
      materiau.color = new THREE.Color(teinte ?? 0xffffff);
      if (rugosite != null) materiau.roughness = rugosite;
      materiau.needsUpdate = true;
      return true;
    },
    /* un objet scanné (glTF), à sa taille réelle ; le même objet chargé une fois, cloné ensuite */
    async objet(nom) {
      if (!cacheObjets.has(nom)) {
        cacheObjets.set(nom, new Promise((ok) => gltf.load(`${base}${nom}/${nom}.gltf`, (g) => ok(g.scene), undefined, () => ok(null))));
      }
      const modele = await cacheObjets.get(nom);
      return modele ? modele.clone(true) : null;
    },
  };
}

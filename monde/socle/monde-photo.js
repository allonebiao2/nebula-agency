/* LE MONDE · le monde photographique (Gaussian splat).

   Mongazi (2026-11-14) : « c'est limite comme un GTA de 2001 ». Voie choisie : un MONDE 3D GÉNÉRÉ PAR IA
   (World Labs Marble, ou tout fichier .spz / .ply / .sog / .splat), qui REMPLACE le décor modélisé. Les
   personnages, les pièces d'Hillary (ses vraies photos), le sac et la commande restent des objets three.js
   posés PAR-DESSUS : ils se mêlent au monde (profondeur commune, mesuré le 2026-11-14).

   Mesuré sur le PC de Mongazi (Intel HD 5500, vraie carte, pas SwiftShader), monde Marble d'exemple :
   - 500 000 points, 7,8 Mo : 26 images/s en 1280×720, 31 en format téléphone ;
   - 2 000 000 points, 30,7 Mo : 12,8 images/s. Trop lourd : on livre la version 500 000 ;
   - le niveau de détail calculé dans le navigateur (`lod`) est PIRE ici (7 à 20 images/s) : éteint.

   La règle 3G : rien de tout ça n'est dans le premier écran. Spark (980 Ko compressé) n'est importé que si un
   monde est déclaré, et le monde arrive APRÈS le salon modélisé, en fondu, quand il est complet.

   Calage (le monde généré a sa propre origine : la place de l'appareil photo de l'image d'origine) :
   `?calage` ouvre le pupitre : flèches = avancer/décaler, PgPréc/PgSuiv = monter/descendre, A/E = tourner,
   R/F et T/G = pencher, +/- = taille, Maj = ×5, C = copier le réglage pour plan.json, M = comparer avec
   le salon modélisé (aussi sans `?calage`). */
import * as THREE from 'three';

const DEG = Math.PI / 180;
/* LE REMPLISSAGE est le vrai coût d'un monde en splats sur un petit processeur graphique : près de l'œil, un
   point couvre l'écran, et des centaines se superposent. Par qualité : jusqu'où on dessine chaque point (en
   écarts types), la taille maximale d'un point à l'écran, et l'opacité sous laquelle on ne le dessine pas. */
const REMPLISSAGE = {
  basse:   { maxStdDev: Math.sqrt(5), maxPixelRadius: 96,  minAlpha: 4 / 255 },
  moyenne: { maxStdDev: Math.sqrt(6), maxPixelRadius: 160, minAlpha: 2 / 255 },
  haute:   {},
};

export function creerMondePhoto({ moteur, decor, surEtat = () => {} }) {
  const { scene, renderer } = moteur;
  let spark = null, maillage = null, cache = [], photo = false, fondu = 0, opaciteCible = 1;
  const reglage = { position: [0, 0, 0], rotation: [0, 0, 0], echelle: 1 };
  const etat = { charge: 0, pret: false, points: 0, erreur: '' };

  function appliquer() {
    if (!maillage) return;
    const [x, y, z] = reglage.position, [rx, ry, rz] = reglage.rotation;
    maillage.position.set(x, y, z);
    /* les mondes Marble sont « y vers le bas » (convention OpenCV) : le demi-tour sur X les remet debout,
       puis le calage tourne autour du vertical du salon */
    maillage.quaternion.setFromEuler(new THREE.Euler(rx * DEG, ry * DEG, rz * DEG, 'YXZ')).multiply(new THREE.Quaternion(1, 0, 0, 0));
    maillage.scale.setScalar(reglage.echelle);
  }

  /* le décor modélisé du dedans sort de la scène (et ses miroirs avec : de la puissance rendue au téléphone) */
  function montrerPhoto(oui) {
    if (!maillage || photo === oui) return;
    photo = oui;
    if (oui) { cache = decor().filter(o => o !== spark && o !== maillage); cache.forEach(o => scene.remove(o)); maillage.visible = true; }
    else { cache.forEach(o => scene.add(o)); cache = []; maillage.visible = false; }
    moteur.composition(!oui);
    surEtat({ ...etat, photo });
  }

  async function charger(url, calage = {}) {
    Object.assign(reglage, JSON.parse(JSON.stringify(calage)));
    const { SparkRenderer, SplatMesh } = await import('@sparkjsdev/spark');
    /* `garder` : le salon retire son décor du dedans, jamais le monde lui-même ni son moteur */
    if (!spark) { spark = new SparkRenderer({ renderer, ...(REMPLISSAGE[moteur.qualite.nom] || {}) }); spark.userData.garder = true; scene.add(spark); }
    return new Promise((ok) => {
      maillage = new SplatMesh({
        url,
        onProgress: (e) => { if (e.lengthComputable) { etat.charge = e.loaded / e.total; surEtat({ ...etat, photo }); } },
        onLoad: (m) => {
          etat.pret = true; etat.charge = 1; etat.points = m.numSplats;
          /* le fondu : le monde se lève par-dessus le salon modélisé, puis le salon s'en va */
          m.opacity = 0; m.visible = true; fondu = 0.001;
          ok(m);
        },
      });
      maillage.visible = false; maillage.userData.garder = true;
      appliquer();
      scene.add(maillage);
    }).catch((e) => { etat.erreur = String(e); surEtat({ ...etat, photo }); });
  }

  moteur.chaqueImage((dt) => {
    if (!maillage || !fondu) return;
    fondu = Math.min(1, fondu + dt / 1.4);
    maillage.opacity = fondu * fondu * (3 - 2 * fondu) * opaciteCible;
    if (fondu >= 1) { fondu = 0; montrerPhoto(true); }
  });

  /* le pupitre de calage : au clavier, pour l'œil de celui qui aligne le monde sur le salon */
  function pupitre(afficher) {
    const ecran = document.createElement('pre');
    ecran.className = 'calage-pupitre';
    ecran.style.cssText = 'position:fixed;left:10px;bottom:10px;z-index:50;margin:0;padding:8px 10px;border-radius:8px;background:rgba(0,0,0,.7);color:#f6f3ee;font:12px/1.4 ui-monospace,monospace;pointer-events:none;white-space:pre';
    if (afficher) document.body.appendChild(ecran);
    const ecrire = () => { ecran.textContent = 'CALAGE (C = copier, M = comparer)\n' + JSON.stringify(reglage); };
    ecrire();
    addEventListener('keydown', (e) => {
      if (e.target && /INPUT|TEXTAREA/.test(e.target.tagName)) return;
      const k = e.key.toLowerCase(), f = e.shiftKey ? 5 : 1, p = reglage.position, r = reglage.rotation;
      if (k === 'm') { montrerPhoto(!photo); if (maillage) maillage.opacity = opaciteCible; return; }
      if (!afficher) return;
      const cam = moteur.camera, av = new THREE.Vector3(); cam.getWorldDirection(av); av.y = 0; av.normalize();
      const cote = new THREE.Vector3(-av.z, 0, av.x), pas = 0.05 * f;
      const bouger = (v, s) => { p[0] += v.x * s; p[2] += v.z * s; };
      const actions = {
        arrowup: () => bouger(av, pas), arrowdown: () => bouger(av, -pas), arrowright: () => bouger(cote, pas), arrowleft: () => bouger(cote, -pas),
        pageup: () => { p[1] += pas; }, pagedown: () => { p[1] -= pas; },
        a: () => { r[1] += f; }, e: () => { r[1] -= f; }, r: () => { r[0] += 0.5 * f; }, f: () => { r[0] -= 0.5 * f; },
        t: () => { r[2] += 0.5 * f; }, g: () => { r[2] -= 0.5 * f; },
        '+': () => { reglage.echelle *= 1 + 0.01 * f; }, '=': () => { reglage.echelle *= 1 + 0.01 * f; }, '-': () => { reglage.echelle /= 1 + 0.01 * f; },
        c: () => navigator.clipboard && navigator.clipboard.writeText(JSON.stringify(reglage)).catch(() => {}),
      };
      if (!actions[k]) return;
      e.preventDefault(); actions[k]();
      for (let i = 0; i < 3; i++) { p[i] = Math.round(p[i] * 1000) / 1000; r[i] = Math.round(r[i] * 10) / 10; }
      reglage.echelle = Math.round(reglage.echelle * 1000) / 1000;
      appliquer(); ecrire();
    });
  }

  return {
    charger, pupitre, montrerPhoto, reglage, etat,
    caler(r) { Object.assign(reglage, JSON.parse(JSON.stringify(r))); appliquer(); },
    get photo() { return photo; },
    get maillage() { return maillage; },
    /* la nuit et le tamisé : le monde est une photo de jour, on le baisse (couleur multipliée) */
    /* ⚠️ seulement quand la teinte CHANGE : toucher `recolor` fait recalculer les 500 000 points par Spark (mesuré :
       6 images/s au lieu de 26 quand on la reposait à chaque image) */
    teinter(couleur) { if (maillage && !maillage.recolor.equals(couleur) && Math.abs(maillage.recolor.r - couleur.r) > 0.004) maillage.recolor.copy(couleur); },
  };
}

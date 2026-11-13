/* LE MONDE · les repères sur les éléments, pensés pour le POUCE.
   Mongazi (2026-11-12) : « la majorité des gens utilise des mobiles… avec un
   pouce ils pourront toucher et voir tout autour : quand dans le champ il y a
   une zone touchable (habits, affiche, clients inconnus, comptoir, sortir,
   entrée), ils peuvent cliquer sur le point lumineux avec le nom ».

   Chaque élément touchable VISIBLE porte un point lumineux. Les plus proches
   affichent leur nom (sinon un petit écran devient illisible), les autres un
   point seul, qu'on peut toucher quand même. Cible de 44 px au doigt. */
import { THREE } from './moteur.js';

export function creerReperes({ moteur, calque, maxNoms = null, distanceMax = 9 }) {
  const { camera } = moteur;
  const liste = [];
  const tactile = matchMedia('(pointer: coarse)').matches;
  const nbNoms = maxNoms || (tactile ? 4 : 7);
  const v = new THREE.Vector3();

  function ajouter({ id, nom, ou, faire, si = null, genre = '' }) {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'repere ' + genre;
    b.innerHTML = '<i aria-hidden="true"></i><span></span>';
    b.addEventListener('click', (e) => { e.stopPropagation(); faire(); });
    calque.appendChild(b);
    const r = { id, nom, ou, faire, si, b, txt: '' };
    liste.push(r);
    return r;
  }

  moteur.chaqueImage(() => {
    const cache = document.body.classList.contains('en-dialogue') || document.body.classList.contains('en-fiche') || document.body.classList.contains('en-cadran');
    const vus = [];
    for (const r of liste) {
      if (cache || (r.si && !r.si())) { if (r.vu !== false) { r.b.classList.remove('vu'); r.vu = false; } continue; }
      r.ou(v);
      const d = v.distanceTo(camera.position);
      v.project(camera);
      const dans = v.z < 1 && Math.abs(v.x) < 0.9 && v.y > -0.82 && v.y < 0.86 && d < distanceMax;
      if (!dans) { if (r.vu !== false) { r.b.classList.remove('vu'); r.vu = false; } continue; }
      vus.push({ r, d, x: Math.round((v.x * 0.5 + 0.5) * innerWidth), y: Math.round((-v.y * 0.5 + 0.5) * innerHeight) });
    }
    vus.sort((a, b) => a.d - b.d);
    const places = [];
    vus.forEach((o, i) => {
      /* deux noms ne se chevauchent pas : le plus loin se contente du point */
      const chevauche = places.some(p => o.x + 200 > p.g && o.x - 30 < p.d && Math.abs(p.y - o.y) < 38);
      const avecNom = i < nbNoms && !chevauche;
      /* un point seul ne se pose jamais SUR l'étiquette d'un autre (vu le 2026-11-12 :
         « ROBE DE C●RÉMONIE ») : il attend qu'on se rapproche */
      if (!avecNom && places.some(p => o.x > p.g - 16 && o.x < p.d + 16 && Math.abs(o.y - p.y) < 26)) { if (o.r.vu !== false) { o.r.b.classList.remove('vu'); o.r.vu = false; } return; }
      const nom = typeof o.r.nom === 'function' ? o.r.nom() : o.r.nom;
      if (nom !== o.r.txt) { o.r.txt = nom; o.r.b.querySelector('span').textContent = nom; o.r.b.setAttribute('aria-label', nom); }
      /* ⚠️ R14 : n'écrire dans le DOM que ce qui CHANGE, et ne mesurer une largeur qu'une fois par texte. Lire
         `offsetWidth` juste après avoir changé une classe ou un `transform` force le navigateur à recalculer TOUTE la
         mise en page, étiquette par étiquette, à chaque image : la cadence tombait de moitié en marchant. */
      if (!o.r.vu) { o.r.b.classList.add('vu'); o.r.vu = true; }
      if (o.r.nomme !== avecNom) { o.r.b.classList.toggle('nomme', avecNom); o.r.nomme = avecNom; }
      /* une étiquette ne sort jamais de l'écran : elle passe à gauche de son point SEULEMENT si
         elle déborderait vraiment à droite (un seuil fixe retournait l'étiquette centrale au téléphone) */
      let gauche = false, w = 44;
      if (avecNom) {
        if (o.r.wPour !== o.r.txt || !o.r.w) { o.r.w = o.r.b.offsetWidth; o.r.wPour = o.r.txt; }
        w = o.r.w; gauche = o.x - 22 + w > innerWidth - 8 && o.x + 22 - w >= 8;
      }
      if (o.r.gauche !== gauche) { o.r.b.classList.toggle('gauche', gauche); o.r.gauche = gauche; }
      const tx = gauche ? o.x - w + 44 : o.x;
      if (avecNom) places.push({ g: tx - 22, d: tx - 22 + w, y: o.y });
      const tr = `translate(${tx}px, ${o.y}px)`;
      if (o.r.tr !== tr) { o.r.b.style.transform = tr; o.r.tr = tr; }
    });
  });

  return { ajouter, liste };
}

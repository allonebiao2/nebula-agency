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
      if (cache || (r.si && !r.si())) { r.b.classList.remove('vu'); continue; }
      r.ou(v);
      const d = v.distanceTo(camera.position);
      v.project(camera);
      const dans = v.z < 1 && Math.abs(v.x) < 0.9 && v.y > -0.82 && v.y < 0.86 && d < distanceMax;
      if (!dans) { r.b.classList.remove('vu'); continue; }
      vus.push({ r, d, x: Math.round((v.x * 0.5 + 0.5) * innerWidth), y: Math.round((-v.y * 0.5 + 0.5) * innerHeight) });
    }
    vus.sort((a, b) => a.d - b.d);
    const places = [];
    vus.forEach((o, i) => {
      /* deux noms ne se chevauchent pas : le plus loin se contente du point */
      const chevauche = places.some(p => Math.abs(p.x - o.x) < 210 && Math.abs(p.y - o.y) < 38);
      const avecNom = i < nbNoms && !chevauche;
      if (avecNom) places.push(o);
      /* un point seul ne se pose jamais SUR l'étiquette d'un autre (vu le 2026-11-12 :
         « ROBE DE C●RÉMONIE ») : il attend qu'on se rapproche */
      else if (places.some(p => o.x > p.x - 16 && o.x < p.x + 260 && Math.abs(o.y - p.y) < 26)) { o.r.b.classList.remove('vu'); return; }
      const nom = typeof o.r.nom === 'function' ? o.r.nom() : o.r.nom;
      if (nom !== o.r.txt) { o.r.txt = nom; o.r.b.querySelector('span').textContent = nom; o.r.b.setAttribute('aria-label', nom); }
      o.r.b.classList.add('vu');
      o.r.b.classList.toggle('nomme', avecNom);
      /* une étiquette ne sort jamais de l'écran : près du bord droit, elle passe à gauche de son point */
      const aGauche = avecNom && o.x > innerWidth - 240;
      o.r.b.classList.toggle('gauche', aGauche);
      o.r.b.style.transform = aGauche ? `translate(${o.x - o.r.b.offsetWidth + 44}px, ${o.y}px)` : `translate(${o.x}px, ${o.y}px)`;
    });
  });

  return { ajouter, liste };
}

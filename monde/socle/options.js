/* LE MONDE · les options près d'une personne ou d'une chose.
   Mongazi (2026-11-12) : « quand on voit quelqu'un au loin et que le point
   s'affiche, on va vers lui avec l'animation, ensuite il y aura des options :
   parler, etc., et là la discussion commence ».

   Une petite carte s'accroche près de la personne (son nom, puis « Parler »,
   « Saluer », « Laisser »…). Elle se ferme si l'on choisit, si l'on touche
   ailleurs, ou si l'on s'éloigne. Boutons de 48 px, pour le pouce. */
import { THREE } from './moteur.js';

export function creerOptions({ moteur, calque, son }) {
  const { camera } = moteur;
  const carte = document.createElement('div');
  carte.className = 'options'; carte.setAttribute('role', 'menu');
  calque.appendChild(carte);
  let courant = null;
  const v = new THREE.Vector3();
  const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  function ouvrir({ titre, sous = '', ancre, choix, auFermer = null }) {
    fermer(false);
    courant = { ancre, auFermer, depart: camera.position.clone() };
    carte.innerHTML = `<div class="opt-titre">${esc(titre)}${sous ? `<small>${esc(sous)}</small>` : ''}</div>` +
      choix.map((c, i) => `<button type="button" role="menuitem" class="opt ${c.principal ? 'opt-principal' : ''}" data-i="${i}">${c.icone ? `<i aria-hidden="true">${c.icone}</i>` : ''}${esc(c.t)}</button>`).join('');
    carte.querySelectorAll('[data-i]').forEach(b => b.addEventListener('click', (e) => {
      e.stopPropagation(); son && son.choix();
      const c = choix[+b.dataset.i]; fermer(c.garder ? false : true); c.faire && c.faire();
    }));
    carte.classList.add('ouverte'); son && son.ouvrir();
    setTimeout(() => { const b = carte.querySelector('.opt'); b && b.focus({ preventScroll: true }); }, 60);
  }
  function fermer(appelerFermeture = true) {
    if (!courant) return;
    const f = courant.auFermer; courant = null;
    carte.classList.remove('ouverte');
    if (appelerFermeture && f) f();
  }
  /* toucher ailleurs ferme la carte */
  addEventListener('pointerdown', (e) => { if (courant && !carte.contains(e.target)) fermer(); }, true);
  addEventListener('keydown', (e) => { if (courant && e.key === 'Escape') fermer(); });

  moteur.chaqueImage(() => {
    if (!courant) return;
    if (camera.position.distanceTo(courant.depart) > 1.5) { fermer(); return; }   /* on s'est éloigné */
    courant.ancre(v); v.project(camera);
    const x = Math.round((v.x * 0.5 + 0.5) * innerWidth), y = Math.round((-v.y * 0.5 + 0.5) * innerHeight);
    /* on garde la carte dans l'écran */
    const w = carte.offsetWidth || 200, h = carte.offsetHeight || 160;
    const cx = Math.min(innerWidth - w / 2 - 12, Math.max(w / 2 + 12, x));
    const cy = Math.min(innerHeight - h - 12, Math.max(80, y));
    carte.style.transform = `translate(${cx}px, ${cy}px) translate(-50%, 0)`;
  });

  return { ouvrir, fermer, get ouvert() { return !!courant; } };
}

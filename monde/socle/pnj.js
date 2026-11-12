/* LE MONDE · la vie des personnages non joueurs.
   Pas de boucle : un AGENDA. Chaque visiteuse choisit sa prochaine activité
   selon ses goûts, ce qu'elle a déjà fait, et ce qui est libre ; elle y
   marche, s'y occupe un temps variable, puis repart. De temps en temps, deux
   d'entre elles se rejoignent et se parlent : on lit ce qu'elles se disent
   quand on est assez près. Aucune visite ne ressemble à la précédente.

   ⛔ Les répliques vivent dans le lieu (textes.js), jamais ici. */
import { THREE, angleVers } from './moteur.js';
import { capVersRotation } from './personnages.js';

const DUREES = { regarder: [9, 20], photo: [5, 9], toucher: [6, 12], telephone: [10, 24], assis: [18, 40], comptoir: [12, 26], fenetre: [9, 18] };
const GESTES = { regarder: 'regarder', photo: 'photo', toucher: 'toucher', telephone: 'telephone', assis: 'repos', comptoir: 'comptoir', fenetre: 'fenetre' };
const hasard = (a, b) => a + Math.random() * (b - a);

export function creerPnj({ moteur, plan, graphe, deplacement, dialogue, calque, visiteuses, conversations, ctx, personnes, son = null }) {
  const { scene, camera } = moteur;
  const places = plan.places_pnj;
  const occupees = new Map();
  let prochaineConv = hasard(8, 14), convEnCours = null;
  const dejaDites = new Set();

  const pnj = visiteuses.map((v, i) => {
    const p = places[(i * 5 + 2) % places.length];
    v.perso.racine.position.set(p.x, 0, p.z);
    v.perso.racine.rotation.y = capVersRotation(p.cap);
    scene.add(v.perso.racine);
    deplacement.ajouterInteractif(v.perso.hitbox, { type: 'pnj', id: v.id });
    const etiquette = document.createElement('div'); etiquette.className = 'pnj-nom'; etiquette.textContent = v.nom;
    etiquette.style.setProperty('--c', v.couleur); calque.appendChild(etiquette);
    occupees.set(p.id, v.id);
    return { ...v, etat: 'activite', place: p, fin: moteur.temps() + hasard(3, 10), chemin: null, histo: [p.id], etiquette, survol: false };
  });
  const parId = Object.fromEntries(pnj.map(n => [n.id, n]));

  function cheminVers(n, cible) {
    const r = n.perso.racine.position;
    const depart = graphe.plusProche(r.x, r.z);
    const arrivee = cible.pres || graphe.plusProche(cible.x, cible.z);
    const ids = graphe.chemin(depart, arrivee) || [];
    const pts = [];
    for (const k of ids) { const g = graphe.noeuds[k]; pts.push(new THREE.Vector3(g.x, 0, g.z)); }
    pts.push(new THREE.Vector3(cible.x, 0, cible.z));
    /* ⚠️ jamais par l'endroit où se tient le joueur : son point de passage est souvent le plus
       proche, et le réflexe qui l'évite la repoussait à chaque image (Afi restait plantée à 55 cm) */
    const joueur = new THREE.Vector3(camera.position.x, 0, camera.position.z);
    for (let i = pts.length - 2; i >= 0; i--) if (pts[i].distanceTo(joueur) < 0.9) pts.splice(i, 1);
    /* on saute le premier point s'il nous fait revenir en arrière */
    if (pts.length > 1 && pts[0].distanceTo(r) < 1.2) pts.shift();
    return pts;
  }
  function partir(n, cible, ensuite) {
    if (n.place) occupees.delete(n.place.id);
    n.perso.assis(false); n.perso.geste('repos'); n.perso.telephone(false); n.perso.regarder(null);
    n.chemin = cheminVers(n, cible); n.etat = 'marche'; n.ensuite = ensuite;
  }
  function choisirPlace(n) {
    const libres = places.filter(p => !occupees.has(p.id) && !n.histo.slice(-3).includes(p.id));
    if (!libres.length) return null;
    const poids = libres.map(p => (n.gouts[p.activite] ?? 1) * (n.goutsPlaces && n.goutsPlaces[p.id] ? n.goutsPlaces[p.id] : 1));
    let r = Math.random() * poids.reduce((a, b) => a + b, 0);
    for (let i = 0; i < libres.length; i++) { r -= poids[i]; if (r <= 0) return libres[i]; }
    return libres[libres.length - 1];
  }
  function suivante(n) {
    const p = choisirPlace(n); if (!p) { n.fin = moteur.temps() + 4; return; }
    occupees.set(p.id, n.id); n.histo.push(p.id); n.place = p;
    partir(n, p, () => commencer(n, p));
  }
  function commencer(n, p) {
    n.etat = 'activite'; n.place = p;
    n.perso.tourner(capVersRotation(p.cap));
    n.perso.assis(p.activite === 'assis');
    n.perso.geste(GESTES[p.activite] || 'repos');
    const d = DUREES[p.activite] || [8, 16]; n.fin = moteur.temps() + hasard(d[0], d[1]);
    const a = capVersRotation(p.cap);
    n.perso.regarder(new THREE.Vector3(p.x + Math.sin(a) * 1.4, p.activite === 'assis' ? 1.6 : 1.25, p.z + Math.cos(a) * 1.4));
    /* toucher un tissu, ça s'entend, de là où elle est */
    if (son && p.activite === 'toucher') setTimeout(() => son.tissu(new THREE.Vector3(p.x, 1.1, p.z)), 600);
  }

  /* ---------- conversations entre elles ---------- */
  function lancerConversation() {
    if (dialogue.actif) return false;
    const libres = pnj.filter(n => n.etat === 'activite');
    const toutes = conversations(ctx).filter(c => !dejaDites.has(c.id) && c.qui.every(q => libres.some(n => n.id === q)) && (!c.si || c.si(ctx)));
    if (!toutes.length) return false;
    const c = toutes[Math.floor(Math.random() * toutes.length)];
    dejaDites.add(c.id);
    const [a, b] = c.qui.map(q => parId[q]);
    const pb = b.perso.racine.position, pa = a.perso.racine.position;
    const vers = new THREE.Vector3().subVectors(pa, pb); vers.y = 0;
    const loin = vers.length();
    convEnCours = { c, a, b, i: -1, finLigne: 0 };
    if (loin < 2.6) { demarrerLignes(); return true; }
    vers.normalize().multiplyScalar(0.95);
    const rdv = { x: pb.x + vers.x, z: pb.z + vers.z, pres: graphe.plusProche(pb.x, pb.z) };
    b.etat = 'attend'; b.perso.regarder(a.perso.positionTete());
    partir(a, rdv, () => { a.etat = 'conversation'; demarrerLignes(); });
    a.etat = 'marche-conv';
    return true;
  }
  function demarrerLignes() {
    const { a, b } = convEnCours;
    a.etat = b.etat = 'conversation';
    a.perso.assis(false); b.perso.assis(false); a.perso.geste('repos'); b.perso.geste('repos'); a.perso.telephone(false); b.perso.telephone(false);
    a.perso.tournerVers(b.perso.racine.position); b.perso.tournerVers(a.perso.racine.position);
    a.perso.regarder(b.perso.positionTete()); b.perso.regarder(a.perso.positionTete());
    convEnCours.i = -1; convEnCours.finLigne = 0;
  }
  function avancerConversation(t) {
    const cv = convEnCours; if (!cv || cv.i === undefined) return;
    if (cv.a.etat !== 'conversation') return;
    if (t < cv.finLigne) return;
    cv.i++;
    if (cv.i > 0) { const prec = cv.c.lignes[cv.i - 1]; parId[prec.qui] && parId[prec.qui].perso.parler(false); }
    if (cv.i >= cv.c.lignes.length) {
      /* une conversation entendue de près apprend quelque chose : au carnet */
      if (cv.entendu && cv.c.savoir && ctx && ctx.apprendre) ctx.apprendre(cv.c.savoir);
      for (const n of [cv.a, cv.b]) { n.etat = 'activite'; n.fin = t + hasard(1, 4); n.perso.regarder(null); n.perso.ecouter(false); }
      convEnCours = null; prochaineConv = t + hasard(14, 30); return;
    }
    const l = cv.c.lignes[cv.i];
    const qui = parId[l.qui];
    const ton = /\?\s*$/.test(l.t) ? 'question' : /!\s*$/.test(l.t) ? 'exclamation' : 'affirmation';
    if (qui) qui.perso.parler(true, ton);
    /* l'autre écoute, et le montre */
    for (const m of [cv.a, cv.b]) if (m !== qui) { m.perso.parler(false); m.perso.ecouter(true); }
    const milieu = new THREE.Vector3().addVectors(cv.a.perso.racine.position, cv.b.perso.racine.position).multiplyScalar(0.5);
    const pres = milieu.distanceTo(new THREE.Vector3(camera.position.x, 0, camera.position.z)) < 9.5;
    if (pres) { dialogue.sousTitre(l.qui, l.t); cv.entendu = true; }
    cv.finLigne = t + 1.6 + l.t.length * 0.055;
  }

  /* ---------- venir parler au joueur ---------- */
  let abordage = null;
  function aborder(id, noeud) {
    const n = parId[id]; if (!n || abordage) return false;
    if (n.etat === 'joueur') return false;   /* elle nous parle déjà : on ne la rappelle pas par-dessus */
    /* elle a quelque chose à demander : elle s'excuse auprès de l'autre et vient */
    if (convEnCours && (convEnCours.a === n || convEnCours.b === n)) {
      for (const m of [convEnCours.a, convEnCours.b]) { m.perso.parler(false); m.perso.ecouter(false); m.etat = 'activite'; m.fin = moteur.temps() + 4; m.perso.regarder(null); }
      convEnCours = null; prochaineConv = moteur.temps() + 12;
    }
    abordage = { n, noeud, relance: 0 };
    n.etat = 'aborde';
    return true;
  }
  function annulerAbordage() {
    if (!abordage) return;
    const n = abordage.n; abordage = null;
    n.chemin = null; n.etat = 'activite'; n.fin = moteur.temps() + 2;
  }
  let derniereFermeture = -10;
  function majAbordage(t) {
    const ab = abordage; if (!ab) return;
    const n = ab.n, r = n.perso.racine.position;
    /* ⚠️ on ne coupe JAMAIS la parole : ni pendant un dialogue, ni dans les 3 s qui suivent
       (entre la dernière réplique d'Hillary et le cadran, Afi s'était glissée), ni devant
       une fiche ou un cadran ouverts */
    if (dialogue.actif || deplacement.enMarche || t - derniereFermeture < 3) return;
    if (document.body.classList.contains('en-fiche') || document.body.classList.contains('en-cadran')) return;
    const avant = new THREE.Vector3(-Math.sin(deplacement.lacet), 0, -Math.cos(deplacement.lacet));
    const ici = new THREE.Vector3(camera.position.x, 0, camera.position.z);
    const rdv = ici.clone().addScaledVector(avant, 1.25);
    /* arrivée : à son rendez-vous, ou déjà tout près du joueur */
    if (r.distanceTo(rdv) > 0.35 && r.distanceTo(ici) > 1.5) {
      /* ⚠️ on ne recalcule le chemin que si le joueur a VRAIMENT bougé : recalculer toutes
         les 2 s la renvoyait au point de passage le plus proche, et elle n'arrivait jamais */
      const bouge = !ab.cible || ab.cible.distanceTo(rdv) > 1;
      if (bouge && t > ab.relance) {
        ab.relance = t + 1.5; ab.cible = rdv.clone();
        if (r.distanceTo(rdv) < 6) { n.chemin = [rdv.clone()]; n.etat = 'aborde'; }
        else { partir(n, { x: rdv.x, z: rdv.z, pres: graphe.plusProche(rdv.x, rdv.z) }, null); n.etat = 'aborde'; }
      } else if (!n.chemin) n.chemin = [ab.cible.clone()];
      return;
    }
    n.chemin = null; n.perso.vitesse = 0; n.perso.tournerVers(ici); n.perso.regarder(camera.position);
    abordage = null;
    parler(n.id, ab.noeud);
  }
  /* on vient vers elle : elle s'arrête, se tourne, attend (ou repart si on la laisse) */
  function retenir(id) {
    const n = parId[id]; if (!n) return;
    if (convEnCours && (convEnCours.a === n || convEnCours.b === n)) {
      for (const m of [convEnCours.a, convEnCours.b]) { m.perso.parler(false); m.perso.ecouter(false); m.etat = 'activite'; m.fin = moteur.temps() + 3; }
      convEnCours = null;
    }
    if (abordage && abordage.n === n) abordage = null;
    n.etat = 'retenue'; n.chemin = null; n.perso.vitesse = 0; n.perso.assis(false); n.perso.geste('repos'); n.perso.telephone(false);
    n.perso.tournerVers(camera.position); n.perso.regarder(camera.position);
  }
  function relacher(id) {
    const n = parId[id]; if (!n || n.etat !== 'retenue') return;
    n.etat = 'activite'; n.fin = moteur.temps() + hasard(1, 3); n.perso.regarder(null);
  }
  /* le joueur parle à une visiteuse (il l'a touchée, ou elle est venue) */
  function parler(id, noeud) {
    const n = parId[id]; if (!n) return;
    if (convEnCours && (convEnCours.a === n || convEnCours.b === n)) {
      for (const m of [convEnCours.a, convEnCours.b]) { m.perso.parler(false); m.etat = 'activite'; m.fin = moteur.temps() + 3; }
      convEnCours = null;
    }
    if (n.place) occupees.delete(n.place.id);
    n.connue = true;   /* son repère passe de « Une visiteuse » à son prénom */
    n.etat = 'joueur'; n.chemin = null; n.perso.vitesse = 0; n.perso.assis(false); n.perso.geste('repos'); n.perso.telephone(false);
    n.perso.tournerVers(camera.position); n.perso.regarder(camera.position);
    if (!dialogue.ouvrir(noeud)) { n.etat = 'activite'; n.fin = moteur.temps() + 2; }
  }
  dialogue.surFermeture.push(() => {
    derniereFermeture = moteur.temps();
    for (const n of pnj) if (n.etat === 'joueur') { n.etat = 'activite'; n.fin = moteur.temps() + hasard(1.5, 4); n.perso.regarder(null); }
  });
  deplacement.surSurvol.push((c) => { for (const n of pnj) n.survol = !!(c && c.type === 'pnj' && c.id === n.id); });

  /* ---------- chaque image ---------- */
  const proj = new THREE.Vector3(), cam2 = new THREE.Vector3();
  moteur.chaqueImage((dt, t) => {
    if (t > prochaineConv && !convEnCours && !abordage) { if (!lancerConversation()) prochaineConv = t + hasard(6, 12); }
    if (convEnCours) avancerConversation(t);
    majAbordage(t);
    cam2.set(camera.position.x, 0, camera.position.z);
    for (const n of pnj) {
      const r = n.perso.racine.position;
      if (n.chemin && n.chemin.length) {
        const cible = n.chemin[0];
        const d = cible.clone().sub(r); d.y = 0; const L = d.length();
        const v = n.vitesse || 1.0;
        if (L < 0.08) { n.chemin.shift(); if (!n.chemin.length) { n.chemin = null; n.perso.vitesse = 0; const e = n.ensuite; n.ensuite = null; if (e) e(); } }
        else {
          const pasL = Math.min(L, v * dt); r.addScaledVector(d.normalize(), pasL);
          /* ses pas viennent de là où elle marche */
          n.distPas = (n.distPas || 0) + pasL;
          if (son && n.distPas > 0.62) { n.distPas = 0; son.pasDe(new THREE.Vector3(r.x, 0.05, r.z)); }
          n.perso.vitesse = v; n.perso.tourner(Math.atan2(d.x, d.z));
          /* on contourne le joueur au lieu de lui passer à travers */
          const dj = r.distanceTo(cam2); if (dj < 0.55) r.addScaledVector(r.clone().sub(cam2).setY(0).normalize(), (0.55 - dj));
        }
      } else n.perso.vitesse = 0;
      if (n.etat === 'activite' && t > n.fin) suivante(n);
      /* on lève les yeux vers le joueur qui passe tout près */
      if (n.etat === 'activite' && r.distanceTo(cam2) < 2.2 && Math.random() < 0.01) n.perso.regarder(camera.position);
      if (n.etat === 'retenue') { n.perso.tournerVers(cam2); n.perso.regarder(camera.position); }
      n.perso.maj(dt, t);
      /* le nom au-dessus de celle qui parle, ou qu'on survole */
      const montrer = (n.perso.st.parle || n.survol) && !document.body.classList.contains('en-fiche');
      if (montrer) {
        n.perso.positionTete(proj); proj.y += 0.34; proj.project(camera);
        const vis = proj.z < 1 && Math.abs(proj.x) < 1 && Math.abs(proj.y) < 1;
        n.etiquette.style.opacity = vis ? '1' : '0';
        if (vis) n.etiquette.style.transform = `translate(${(proj.x * 0.5 + 0.5) * innerWidth}px, ${(-proj.y * 0.5 + 0.5) * innerHeight}px) translate(-50%, -100%)`;
      } else n.etiquette.style.opacity = '0';
    }
  });

  return { pnj, parId, aborder, annulerAbordage, parler, retenir, relacher, get conversation() { return convEnCours; }, get abordage() { return abordage; } };
}

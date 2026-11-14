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

/* la hauteur de voix de chacune, pour son murmure (Maman la plus grave, Sènami la plus haute) */
const HAUTEURS_VOIX = { afi: 212, senami: 238, maman: 188 };
export function creerPnj({ moteur, plan, graphe, deplacement, dialogue, calque, visiteuses, conversations, ctx, personnes, son = null }) {
  /* `reglages.foyer()` : une position (ou null) que personne ne doit cacher au visiteur, posée par le lieu */
  /* `conversations` : le lieu peut retenir les conversations tant que le visiteur n'est pas entré (l'accroche les ouvre) */
  const reglages = { foyer: null, conversations: true };
  const { scene, camera } = moteur;
  const places = plan.places_pnj;
  const occupees = new Map();
  let prochaineConv = hasard(8, 14), convEnCours = null;
  const dejaDites = new Set();

  const pnj = visiteuses.map((v, i) => {
    /* `placeDepart` : le lieu peut poser une visiteuse quelque part au chargement (l'accroche de l'entrée) */
    const p = (v.placeDepart && (typeof v.placeDepart === 'object' ? v.placeDepart : places.find(x => x.id === v.placeDepart))) || places[(i * 5 + 2) % places.length];
    v.perso.racine.position.set(p.x, 0, p.z);
    v.perso.racine.rotation.y = capVersRotation(p.cap);
    scene.add(v.perso.racine);
    deplacement.ajouterInteractif(v.perso.hitbox, { type: 'pnj', id: v.id });
    const etiquette = document.createElement('div'); etiquette.className = 'pnj-nom'; etiquette.textContent = v.nom;
    etiquette.style.setProperty('--c', v.couleur); etiquette.style.setProperty('--c-texte', v.texte || '#15110f'); calque.appendChild(etiquette);
    occupees.set(p.id, v.id);
    /* posée pour l'accroche, elle attend là jusqu'à ce que le lieu la libère (ou que l'accroche finisse) */
    return { ...v, etat: 'activite', place: p, fin: v.placeDepart ? Infinity : moteur.temps() + hasard(3, 10), chemin: null, histo: [p.id], etiquette, survol: false };
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
  /* `voulu` : lancer UNE conversation précise (l'accroche) ; elle ignore sa condition `si` (qui la tient hors du tirage) */
  function lancerConversation(voulu = null) {
    if (dialogue.actif) return false;
    const libres = pnj.filter(n => n.etat === 'activite');
    const toutes = conversations(ctx).filter(c => !dejaDites.has(c.id) && c.qui.every(q => libres.some(n => n.id === q)) && (voulu ? c.id === voulu : (!c.si || c.si(ctx))));
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
    /* ⚠️ la conversation a pu être annulée pendant la marche (le visiteur lui a parlé) : on ne
       relance que CELLE-CI, jamais une conversation disparue (erreur vue au QC du 2026-11-12) */
    const cetteConv = convEnCours;
    partir(a, rdv, () => { if (convEnCours !== cetteConv) return; a.etat = 'conversation'; demarrerLignes(); });
    a.etat = 'marche-conv';
    return true;
  }
  function demarrerLignes() {
    if (!convEnCours) return;
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
      for (const n of [cv.a, cv.b]) { n.etat = 'activite'; n.fin = t + hasard(1, 4); n.perso.regarder(null); n.perso.ecouter(false); n.perso.telephone(false); }
      convEnCours = null; prochaineConv = t + hasard(14, 30); return;
    }
    const l = cv.c.lignes[cv.i];
    const qui = parId[l.qui];
    const ton = /\?\s*$/.test(l.t) ? 'question' : /!\s*$/.test(l.t) ? 'exclamation' : 'affirmation';
    if (qui) qui.perso.parler(true, ton);
    /* l'autre écoute, et le montre */
    for (const m of [cv.a, cv.b]) if (m !== qui) { m.perso.parler(false); m.perso.ecouter(true); }
    /* une réplique peut porter un geste : sortir ou ranger le téléphone, regarder le visiteur ensemble */
    if (qui && l.telephone !== undefined) qui.perso.telephone(!!l.telephone);
    if (l.regardeJoueur) for (const m of [cv.a, cv.b]) m.perso.regarder(camera.position.clone());
    const milieu = new THREE.Vector3().addVectors(cv.a.perso.racine.position, cv.b.perso.racine.position).multiplyScalar(0.5);
    const pres = milieu.distanceTo(new THREE.Vector3(camera.position.x, 0, camera.position.z)) < 9.5;
    if (pres) { dialogue.sousTitre(l.qui, l.t); cv.entendu = true; }
    /* P43 (référence) : trop loin pour lire, on les ENTEND quand même, un murmure sans mots là où elles parlent */
    else if (son && son.murmure) son.murmure(new THREE.Vector3(milieu.x, 1.5, milieu.z), 1.1 + l.t.length * 0.05, HAUTEURS_VOIX[l.qui] || 215);
    cv.finLigne = t + 1.6 + l.t.length * 0.055;
  }

  /* P27 (référence : tous les soldats lèvent la tête vers la télé) : UNE RÉACTION COLLECTIVE. Celles qui ne parlent pas
     au visiteur tournent la tête vers la même chose, presque ensemble (décalées de quelques dixièmes), puis reprennent ;
     la plus proche peut lâcher une phrase (`lignes` : une par personne), sous-titrée si on est assez près. */
  function reagir(point, { duree = 2.4, rayon = Infinity, lignes = null } = {}) {
    const c = new THREE.Vector3(camera.position.x, 0, camera.position.z);
    const ok = pnj.filter(n => !['joueur', 'retenue'].includes(n.etat) && n.perso.racine.position.distanceTo(c) < rayon);
    ok.forEach((n, i) => setTimeout(() => { n.perso.regarder(typeof point === 'function' ? point() : point.clone()); n.reagitJusqua = moteur.temps() + duree * (0.85 + Math.random() * 0.3); }, i * 170 + Math.random() * 120));
    if (lignes && !dialogue.actif) {
      const parle = ok.filter(n => lignes[n.id]).sort((a, b) => a.perso.racine.position.distanceTo(c) - b.perso.racine.position.distanceTo(c))[0];
      if (parle && parle.perso.racine.position.distanceTo(c) < 9.5) setTimeout(() => dialogue.sousTitre(parle.id, lignes[parle.id]), 650);
    }
    return ok.length;
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
    /* ⚠️ 1,60 m : au téléphone, en portrait, le champ vertical est très ouvert, et à 1,25 m son visage
       remplissait l'écran (capture du 2026-11-13) ; à 1,60 m on cadre la tête et le buste */
    const rdv = ici.clone().addScaledVector(avant, 1.6);
    /* arrivée : à son rendez-vous, ou déjà assez près du joueur */
    if (r.distanceTo(rdv) > 0.35 && r.distanceTo(ici) > 1.8) {
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
    if (reglages.conversations && t > prochaineConv && !convEnCours && !abordage) { if (!lancerConversation()) prochaineConv = t + hasard(6, 12); }
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
      /* L'ESPACE DE CHACUNE (Mongazi, 2026-11-12 : « ils se rentrent dedans ») : deux
         visiteuses ne s'approchent pas à moins de 0,65 m, et aucune ne reste à moins de
         0,85 m du visiteur (sauf pendant qu'elle lui parle). On écarte doucement, jamais d'un saut. */
      /* ⚠️ seule celle qui MARCHE s'écarte : écarter deux visiteuses immobiles qui conversent
         les faisait glisser, et celle qu'on allait voir sortait du cadre (QC du 2026-11-12) */
      if (n.chemin) for (const m of pnj) {
        if (m === n) continue;
        const o = m.perso.racine.position, dx = r.x - o.x, dz = r.z - o.z, dd = Math.hypot(dx, dz);
        if (dd > 1e-4 && dd < 0.65) { const k = Math.min(0.65 - dd, dt * 0.9) / dd; r.x += dx * k; r.z += dz * k; }
      }
      {
        /* 0,85 m au moins ; et celle qui PARLE au visiteur se tient à 1,30 m, sinon son visage remplit
           l'écran du téléphone (capture du 2026-11-13) */
        const mini = n.etat === 'joueur' ? 1.3 : n.etat === 'retenue' ? 0 : 0.85;
        const dx = r.x - cam2.x, dz = r.z - cam2.z, dd = Math.hypot(dx, dz);
        if (mini && dd > 1e-4 && dd < mini) { const k = Math.min(mini - dd, dt * 0.8) / dd; r.x += dx * k; r.z += dz * k; }
      }
      /* personne ne s'interpose entre le visiteur et celle qui lui parle : une visiteuse sur la ligne de
         regard s'écarte doucement de côté (capture du 2026-11-13 : Maman Sènami cachait Afi) */
      /* … ni entre lui et le FOYER que le lieu désigne (au comptoir : Hillary ; capture du 2026-11-13, trois
         visiteuses alignées entre le visiteur et elle) */
      const foyer = pnj.find(m => m.etat === 'joueur');
      const fPos = foyer ? (foyer !== n ? foyer.perso.racine.position : null) : (reglages.foyer ? reglages.foyer() : null);
      if (fPos) {
        const f = fPos, ax = f.x - cam2.x, az = f.z - cam2.z, L2 = ax * ax + az * az;
        if (L2 > 0.01) {
          const k = Math.max(0, Math.min(1, ((r.x - cam2.x) * ax + (r.z - cam2.z) * az) / L2));
          const px = cam2.x + ax * k, pz = cam2.z + az * k, dx = r.x - px, dz = r.z - pz, dd = Math.hypot(dx, dz);
          if (k > 0 && k < 0.98 && dd < 0.9) {
            const L = Math.sqrt(L2), nx = dd > 1e-3 ? dx / dd : -az / L, nz = dd > 1e-3 ? dz / dd : ax / L;
            const pas = Math.min(0.9 - dd, dt * 0.9); r.x += nx * pas; r.z += nz * pas;
          }
        }
      }
      if (n.reagitJusqua && t > n.reagitJusqua) {
        n.reagitJusqua = 0; const cv = convEnCours;
        if (cv && (cv.a === n || cv.b === n)) n.perso.regarder((cv.a === n ? cv.b : cv.a).perso.positionTete()); else if (n.etat !== 'joueur' && n.etat !== 'retenue') n.perso.regarder(null);
      }
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

  return { pnj, parId, reglages, aborder, annulerAbordage, parler, retenir, relacher, reagir, lancer: (id) => !convEnCours && lancerConversation(id),
    liberer(id) { const n = parId[id]; if (n && n.fin === Infinity) n.fin = moteur.temps() + hasard(1, 4); }, get conversation() { return convEnCours; }, get abordage() { return abordage; } };
}

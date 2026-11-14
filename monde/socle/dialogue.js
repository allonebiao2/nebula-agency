/* LE MONDE · parler.
   Deux voix :
   - les SOUS-TITRES : ce que les personnages se disent entre eux, nommés et
     colorés, en bas à gauche (on lit ce qu'ils se disent, comme dans la
     scène de référence) ;
   - le DIALOGUE : quand on parle à quelqu'un. Bandes de cinéma, la caméra se
     resserre, le texte s'écrit, on touche pour continuer, puis les réponses
     s'offrent EN CROIX (haut, gauche, droite, bas), au doigt ou aux flèches.

   Un nœud de dialogue est une fonction (ctx) => { qui, dit: [...], choix: [...], alors, suite }.
   ⛔ Les textes ne vivent PAS ici : ils sont dans le lieu (textes.js), et
   tout chiffre y est tiré des données de la maison. */
import { THREE } from './moteur.js';

const DIRS = ['haut', 'gauche', 'droite', 'bas'];
/* P34 (référence : ≈ 5 s ; au téléphone on lit plus lentement) : le temps laissé pour une réplique LÉGÈRE */
const DUREE_LEGER = 7000;
const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

const cibleRegard = new THREE.Vector3(), BAISSE_REGARD = new THREE.Vector3(0, -0.2, 0), ecran = new THREE.Vector3();
export function creerDialogue({ calque, son, deplacement, personnes, registre = {}, ctx = {} }) {
  const el = (tag, cls, html = '') => { const e = document.createElement(tag); if (cls) e.className = cls; e.innerHTML = html; return e; };
  const st = el('div', 'soustitres'); st.setAttribute('aria-live', 'polite'); calque.appendChild(st);
  const bandes = el('div', 'bandes', '<i></i><i></i>'); calque.appendChild(bandes);
  const boite = el('section', 'dialogue');
  boite.setAttribute('role', 'dialog'); boite.setAttribute('aria-label', 'Conversation');
  /* ⚠️ pas de portrait-image : c'est le CORPS 3D qui parle (Mongazi, 2026-11-12) */
  boite.innerHTML = `<div class="dlg-corps"><div class="dlg-nom"></div><p class="dlg-texte" aria-live="polite"></p><span class="dlg-suite" aria-hidden="true">▸</span></div>
    <button type="button" class="dlg-partir" aria-label="Partir">Partir</button>
    <div class="dlg-croix" role="group" aria-label="Vos réponses"></div>`;
  calque.appendChild(boite);
  const $ = (s) => boite.querySelector(s);
  let actif = false, attente = null, tapeur = null, choixCourants = [], selection = 0, cadree = null;
  /* les réponses déjà explorées : cochées ; les autres : une étoile. On a envie de tout essayer. */
  let vus = new Set();
  try { vus = new Set(JSON.parse(localStorage.getItem('monde:vus')) || []); } catch (e) { /* rien */ }
  const cleChoix = (n, c) => `${n.qui || ''}|${c.t}`;
  boite.querySelector('.dlg-partir').addEventListener('click', (e) => { e.stopPropagation(); son && son.clic(); fermer(); });

  /* ---------- sous-titres ---------- */
  function sousTitre(qui, texte, duree) {
    if (actif) return;
    const p = personnes[qui] || { nom: qui, couleur: '#fff' };
    const l = el('p', 'st-ligne', `<b style="--c:${p.couleur};--c-texte:${p.texte || '#15110f'}">${esc(p.nom)}</b><span>${esc(texte)}</span>`);
    st.appendChild(l);
    while (st.children.length > 3) st.firstChild.remove();
    const d = duree || (1.6 + texte.length * 0.055) * 1000;
    setTimeout(() => { l.classList.add('part'); setTimeout(() => l.remove(), 600); }, d);
  }

  /* ---------- le dialogue ---------- */
  const tonDe = (t) => (/\?\s*$/.test(t) ? 'question' : /!\s*$/.test(t) ? 'exclamation' : 'affirmation');
  function montrer(qui, texte = '') {
    const p = personnes[qui] || { nom: qui, couleur: '#e6007e' };
    $('.dlg-nom').textContent = p.nom; $('.dlg-nom').style.color = p.texte || p.couleur;
    boite.style.setProperty('--c', p.couleur);
    for (const k in personnes) if (personnes[k].perso) personnes[k].perso.parler(k === qui, tonDe(texte));
    if (p.perso && deplacement) {
      /* LA MISE EN SCÈNE (audit jeu vidéo, vague 3) : celle qui parle est cadrée de la taille à la tête,
         quelle que soit sa distance, le regard au tiers haut ; le fond se floute sur les appareils capables */
      const tete = p.perso.positionTete(new THREE.Vector3()), camera = deplacement.camera;
      /* P7 (référence) : à plusieurs, la caméra NE SAUTE PAS d'une oratrice à l'autre ; elle ne se tourne vers la
         nouvelle que si celle-ci sort du centre de l'image (sinon : un coup de caméra à chaque réplique) */
      if (cadree && cadree !== qui) {
        ecran.copy(tete).project(camera);
        if (ecran.z < 1 && Math.abs(ecran.x) < 0.55 && ecran.y > -0.45 && ecran.y < 0.8) return;
      }
      cadree = qui;
      const d = Math.max(0.8, tete.distanceTo(camera.position));
      const base = camera.userData.fovBase || camera.fov;
      /* deux exigences : de la taille à la tête en hauteur (1,2 m), et 1,10 m de large autour d'elle :
         en portrait, l'écran est étroit, et un cadre calculé sur la seule hauteur coupait tout (capture du 2026-11-13) */
      const enHauteur = 2 * Math.atan(0.6 / d);
      const enLargeur = 2 * Math.atan(Math.tan(Math.atan(0.55 / d)) / Math.max(0.3, camera.aspect));
      const fov = Math.min(base - 4, Math.max(base * 0.55, Math.max(enHauteur, enLargeur) * 180 / Math.PI));
      /* le regard visé : 20 cm sous l'os de la tête (le menton), suivi à chaque image */
      const vise = () => p.perso.positionTete(cibleRegard).add(BAISSE_REGARD);
      if (deplacement.suivre) deplacement.suivre(vise); else deplacement.tournerVers(vise());
      deplacement.cadrer && deplacement.cadrer(fov, d);
    }
  }
  function ecrire(texte) {
    const t = $('.dlg-texte'); t.textContent = ''; boite.classList.remove('peut-suivre');
    clearInterval(tapeur);
    let i = 0; const lent = matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (lent) { t.textContent = texte; boite.classList.add('peut-suivre'); return; }
    tapeur = setInterval(() => {
      i += 2; t.textContent = texte.slice(0, i);
      if (i >= texte.length) { clearInterval(tapeur); tapeur = null; boite.classList.add('peut-suivre'); }
    }, 18);
    return () => { if (tapeur) { clearInterval(tapeur); tapeur = null; t.textContent = texte; boite.classList.add('peut-suivre'); return true; } return false; };
  }
  /* ⚠️ comme dans la scène de référence, une réplique AVANCE SEULE une fois lue (le temps de
     la lire) ; toucher la fait aller plus vite. Seul le choix d'une réponse attend le joueur. */
  let minuteur = null;
  function attendreSuite(texte) {
    return new Promise((ok) => {
      const finirFrappe = ecrire(texte);
      const duree = (1.5 + texte.length * 0.045) * 1000 + texte.length * 9;
      const suivre = () => { clearTimeout(minuteur); minuteur = null; attente = null; ok(); };
      minuteur = setTimeout(suivre, duree);
      attente = () => { if (finirFrappe && finirFrappe()) { clearTimeout(minuteur); minuteur = setTimeout(suivre, 900 + texte.length * 25); return; } suivre(); };
    });
  }
  boite.addEventListener('pointerup', (e) => { if (e.target.closest('.dlg-croix')) return; if (attente) { son && son.clic(); attente(); } });
  addEventListener('keydown', (e) => {
    if (!actif) return;
    if (attente && (e.key === ' ' || e.key === 'Enter')) { e.preventDefault(); attente(); return; }
    if (choixCourants.length) {
      const idx = { ArrowUp: 'haut', ArrowLeft: 'gauche', ArrowRight: 'droite', ArrowDown: 'bas' }[e.key];
      if (idx) { e.preventDefault(); const b = $(`.dlg-croix [data-dir="${idx}"]`); if (b) b.click(); }
      if (/^[1-4]$/.test(e.key)) { const b = $$('.dlg-croix button')[+e.key - 1]; if (b) b.click(); }
    }
  });
  const $$ = (s) => [...boite.querySelectorAll(s)];

  /* P33 et P34 (référence) : sur une conversation LÉGÈRE (`leger: true`, jamais une commande ni une course), la croix
     offre « Pas de réponse » en haut, et un minuteur doux se vide par les deux bouts ; à zéro, on se tait, et
     l'autre réagit (`silence`, sa phrase à elle). Toucher n'importe quelle réponse arrête le minuteur. */
  let compteChoix = null;
  function proposer(choix, n) {
    const leger = !!(n && n.leger) && choix.length < 4 && !choix.some(c => c.dir === 'haut');
    if (leger) choix = [{ t: 'Pas de réponse', dir: 'haut', muet: true, silence: true, va: n.silence ? () => ({ qui: n.qui, dit: [n.silence] }) : null }, ...choix];
    return new Promise((ok) => {
      const croix = $('.dlg-croix'); croix.innerHTML = '<i class="losange" aria-hidden="true"></i>';
      const libres = DIRS.filter(d => !choix.some(c => c.dir === d));
      choixCourants = choix.map(c => ({ ...c, dir: c.dir || libres.shift() }));
      choixCourants.forEach((c, i) => {
        const k = cleChoix(n || {}, c), deja = vus.has(k);
        const b = el('button', `ch ch-${c.dir} ${c.silence ? 'ch-silence' : deja ? 'deja' : 'neuf'}`, `<kbd>${i + 1}</kbd>${esc(c.t)}`);
        b.type = 'button'; b.dataset.dir = c.dir;
        b.addEventListener('click', (e) => {
          e.stopPropagation(); clearTimeout(compteChoix); compteChoix = null;
          son && son.choix(); choixCourants = []; croix.innerHTML = ''; boite.classList.remove('en-choix');
          vus.add(k); try { localStorage.setItem('monde:vus', JSON.stringify([...vus])); } catch (_) { /* rien */ }
          ok(c);
        });
        croix.appendChild(b);
      });
      if (leger) {
        const m = el('div', 'dlg-minuteur', '<i></i>'); m.setAttribute('aria-hidden', 'true'); m.style.setProperty('--duree', DUREE_LEGER + 'ms');
        croix.appendChild(m);
        compteChoix = setTimeout(() => { const s = croix.querySelector('.ch-silence'); if (s) s.click(); }, DUREE_LEGER);
      }
      boite.classList.add('en-choix');
      /* le focus va à la première VRAIE réponse (pas au silence) */
      setTimeout(() => { const b = croix.querySelector('button:not(.ch-silence)') || croix.querySelector('button'); if (b) b.focus({ preventScroll: true }); }, 50);
    });
  }

  function direToi(texte) {
    return new Promise((ok) => {
      $('.dlg-nom').textContent = 'Toi'; $('.dlg-nom').style.color = '#15110f';
      boite.style.setProperty('--c', '#ffffff');
      for (const k in personnes) if (personnes[k].perso) personnes[k].perso.parler(false);
      $('.dlg-texte').textContent = texte; boite.classList.add('peut-suivre');
      const fin = () => { clearTimeout(minuteur); attente = null; ok(); };
      minuteur = setTimeout(fin, 700 + texte.length * 22);
      attente = fin;
    });
  }
  async function jouer(id) {
    let n = typeof id === 'function' ? id(ctx) : (registre[id] ? registre[id](ctx) : null);
    while (n) {
      if (!actif) return;
      for (const ligne of (n.dit || [])) {
        if (!actif) return;
        const l = typeof ligne === 'string' ? { qui: n.qui, t: ligne } : ligne;
        if (!l.t) continue;
        montrer(l.qui || n.qui, l.t);
        await attendreSuite(l.t);
      }
      if (n.savoir && ctx.apprendre) [].concat(n.savoir).forEach(s => ctx.apprendre(s));
      let suite = n.suite || null;
      /* « alors » peut ouvrir une fiche et décider de la suite selon ce que le joueur y a fait */
      if (n.alors) { const r = await n.alors(ctx); if (r !== undefined) suite = r; }
      const choix = (n.choix || []).filter(c => !c.si || c.si(ctx)).slice(0, 4);
      if (choix.length) {
        $('.dlg-texte').parentElement.classList.add('fige');
        /* pendant qu'on choisit sa réponse, elle se tait et ÉCOUTE (elle hoche la tête) */
        const ecoutant = personnes[n.qui] && personnes[n.qui].perso;
        if (ecoutant) { ecoutant.parler(false); ecoutant.ecouter(true); }
        const c = await proposer(choix, n);
        if (ecoutant) ecoutant.ecouter(false);
        $('.dlg-texte').parentElement.classList.remove('fige');
        /* ta réponse, dite : elle reste un instant sous « Toi » avant que l'autre réponde */
        if (!c.muet) await direToi(c.t);
        if (c.action) { const r = await c.action(ctx); if (r !== undefined) suite = r; }
        if (c.va !== undefined) suite = c.va;
      }
      if (!suite) break;
      n = typeof suite === 'function' ? suite(ctx) : (registre[suite] ? registre[suite](ctx) : null);
    }
    fermer();
  }

  function ouvrir(id) {
    if (actif) return false;
    actif = true; st.innerHTML = ''; cadree = null;
    document.body.classList.add('en-dialogue');
    boite.classList.add('ouverte'); bandes.classList.add('ouvertes');
    if (deplacement) { deplacement.bloquer(true); deplacement.cinema(true); }
    son && son.ouvrir();
    jouer(id);
    return true;
  }
  function fermer() {
    if (!actif) return;
    actif = false; attente = null; choixCourants = []; clearTimeout(minuteur); clearTimeout(compteChoix); compteChoix = null;
    for (const k in personnes) if (personnes[k].perso) personnes[k].perso.parler(false);
    document.body.classList.remove('en-dialogue');
    boite.classList.remove('ouverte', 'en-choix'); bandes.classList.remove('ouvertes');
    if (deplacement) { deplacement.bloquer(false); deplacement.cinema(false); }
    dialogue.surFermeture.forEach(f => f());
  }

  const dialogue = { ouvrir, fermer, sousTitre, registre, ctx, surFermeture: [], get actif() { return actif; } };
  return dialogue;
}

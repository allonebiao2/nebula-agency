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
const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

export function creerDialogue({ calque, son, deplacement, personnes, registre = {}, ctx = {} }) {
  const el = (tag, cls, html = '') => { const e = document.createElement(tag); if (cls) e.className = cls; e.innerHTML = html; return e; };
  const st = el('div', 'soustitres'); st.setAttribute('aria-live', 'polite'); calque.appendChild(st);
  const bandes = el('div', 'bandes', '<i></i><i></i>'); calque.appendChild(bandes);
  const boite = el('section', 'dialogue');
  boite.setAttribute('role', 'dialog'); boite.setAttribute('aria-label', 'Conversation');
  /* ⚠️ pas de portrait-image : c'est le CORPS 3D qui parle (Mongazi, 2026-11-12) */
  boite.innerHTML = `<div class="dlg-corps"><div class="dlg-nom"></div><p class="dlg-texte" aria-live="polite"></p><span class="dlg-suite" aria-hidden="true">▸</span></div>
    <button type="button" class="dlg-partir" aria-label="Partir">Partir ✕</button>
    <div class="dlg-croix" role="group" aria-label="Vos réponses"></div>`;
  calque.appendChild(boite);
  const $ = (s) => boite.querySelector(s);
  let actif = false, attente = null, tapeur = null, choixCourants = [], selection = 0;
  /* les réponses déjà explorées : cochées ; les autres : une étoile. On a envie de tout essayer. */
  let vus = new Set();
  try { vus = new Set(JSON.parse(localStorage.getItem('monde:vus')) || []); } catch (e) { /* rien */ }
  const cleChoix = (n, c) => `${n.qui || ''}|${c.t}`;
  boite.querySelector('.dlg-partir').addEventListener('click', (e) => { e.stopPropagation(); son && son.clic(); fermer(); });

  /* ---------- sous-titres ---------- */
  function sousTitre(qui, texte, duree) {
    if (actif) return;
    const p = personnes[qui] || { nom: qui, couleur: '#fff' };
    const l = el('p', 'st-ligne', `<b style="color:${p.couleur}">${esc(p.nom)}</b> ${esc(texte)}`);
    st.appendChild(l);
    while (st.children.length > 3) st.firstChild.remove();
    const d = duree || (1.6 + texte.length * 0.055) * 1000;
    setTimeout(() => { l.classList.add('part'); setTimeout(() => l.remove(), 600); }, d);
  }

  /* ---------- le dialogue ---------- */
  const tonDe = (t) => (/\?\s*$/.test(t) ? 'question' : /!\s*$/.test(t) ? 'exclamation' : 'affirmation');
  function montrer(qui, texte = '') {
    const p = personnes[qui] || { nom: qui, couleur: '#e6007e' };
    $('.dlg-nom').textContent = p.nom; $('.dlg-nom').style.color = p.couleur;
    boite.style.setProperty('--c', p.couleur);
    for (const k in personnes) if (personnes[k].perso) personnes[k].perso.parler(k === qui, tonDe(texte));
    if (p.perso && deplacement) {
      const tete = p.perso.positionTete(new THREE.Vector3());
      deplacement.tournerVers(tete.add(new THREE.Vector3(0, -0.08, 0)));
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

  function proposer(choix, n) {
    return new Promise((ok) => {
      const croix = $('.dlg-croix'); croix.innerHTML = '<i class="losange" aria-hidden="true"></i>';
      const libres = DIRS.filter(d => !choix.some(c => c.dir === d));
      choixCourants = choix.map(c => ({ ...c, dir: c.dir || libres.shift() }));
      choixCourants.forEach((c, i) => {
        const k = cleChoix(n || {}, c), deja = vus.has(k);
        const b = el('button', `ch ch-${c.dir} ${deja ? 'deja' : 'neuf'}`, `<kbd>${i + 1}</kbd>${esc(c.t)}`);
        b.type = 'button'; b.dataset.dir = c.dir;
        b.addEventListener('click', (e) => {
          e.stopPropagation(); son && son.choix(); choixCourants = []; croix.innerHTML = ''; boite.classList.remove('en-choix');
          vus.add(k); try { localStorage.setItem('monde:vus', JSON.stringify([...vus])); } catch (_) { /* rien */ }
          ok(c);
        });
        croix.appendChild(b);
      });
      boite.classList.add('en-choix');
      setTimeout(() => { const b = croix.querySelector('button'); if (b) b.focus({ preventScroll: true }); }, 50);
    });
  }

  function direToi(texte) {
    return new Promise((ok) => {
      $('.dlg-nom').textContent = 'Toi'; $('.dlg-nom').style.color = '#ffffff';
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
    actif = true; st.innerHTML = '';
    document.body.classList.add('en-dialogue');
    boite.classList.add('ouverte'); bandes.classList.add('ouvertes');
    if (deplacement) { deplacement.bloquer(true); deplacement.cinema(true); }
    son && son.ouvrir();
    jouer(id);
    return true;
  }
  function fermer() {
    if (!actif) return;
    actif = false; attente = null; choixCourants = []; clearTimeout(minuteur);
    for (const k in personnes) if (personnes[k].perso) personnes[k].perso.parler(false);
    document.body.classList.remove('en-dialogue');
    boite.classList.remove('ouverte', 'en-choix'); bandes.classList.remove('ouvertes');
    if (deplacement) { deplacement.bloquer(false); deplacement.cinema(false); }
    dialogue.surFermeture.forEach(f => f());
  }

  const dialogue = { ouvrir, fermer, sousTitre, registre, ctx, surFermeture: [], get actif() { return actif; } };
  return dialogue;
}

// LA BOBINE · la frise de montage. La tête de lecture reste au centre ; c'est la bande qui défile,
// au doigt comme à la molette. Toucher un clip le sélectionne ; un clip sélectionné se déplace et se rogne.

import { dureeClip, finClip, dureeProjet, principale, clamp, formatTemps, deplacerPrincipale, deplacerLibre, rogner } from './model.js';

const PPS_MIN = 6;
const PPS_MAX = 400;
const ORDRE = { texte: 0, superposition: 1, principale: 2, audio: 3 };
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const ICONE_JONCTION = '<svg viewBox="0 0 24 24"><path d="M4 12h6M14 12h6M10 7l4 5-4 5"/></svg>';
const ICONE_PLUS = '<svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>';

function ondeSvg(onde, a, b) {
  if (!onde || !onde.length) return '';
  const i0 = clamp(Math.floor(a * onde.length), 0, onde.length - 1);
  const i1 = clamp(Math.ceil(b * onde.length), i0 + 2, onde.length);
  const pts = onde.slice(i0, i1);
  const n = pts.length;
  let d = 'M0 50';
  pts.forEach((v, i) => { d += `L${i} ${(50 - Math.max(2, v * 48)).toFixed(1)}`; });
  for (let i = n - 1; i >= 0; i -= 1) d += `L${i} ${(50 + Math.max(2, pts[i] * 48)).toFixed(1)}`;
  return `<svg class="onde" viewBox="0 0 ${Math.max(1, n - 1)} 100" preserveAspectRatio="none" aria-hidden="true"><path d="${d}Z"/></svg>`;
}

export class Frise {
  constructor(app) {
    this.app = app;
    this.zone = document.getElementById('frise-zone');
    this.defile = document.getElementById('frise-defile');
    this.contenu = document.getElementById('frise-contenu');
    this.regle = document.getElementById('regle');
    this.pistes = document.getElementById('pistes');
    this.pps = 60;
    this.scrollProgramme = -1;
    this.geste = null;
    this.pince = null;
    this._ecouter();
  }

  get demi() { return Math.round(this.zone.clientWidth / 2); }

  ajusterZoom() {
    const d = Math.max(dureeProjet(this.app.p), 6);
    this.pps = clamp((this.zone.clientWidth * 0.82) / d, 8, 140);
  }

  zoomer(pps) {
    const t = this.app.lecteur.t;
    this.pps = clamp(pps, PPS_MIN, PPS_MAX);
    this.rendre();
    this.majTemps(t, true);
  }

  rendre() {
    const app = this.app;
    const p = app.p;
    if (!p) return;
    const pps = this.pps;
    const d = dureeProjet(p);
    const demi = this.demi;
    this.contenu.style.setProperty('--demi', `${demi}px`);
    this.contenu.style.width = `${demi * 2 + Math.max(d, 1) * pps + 90}px`;

    const pas = [0.5, 1, 2, 5, 10, 15, 30, 60, 120, 300, 600].find((s) => s * pps >= 70) || 1200;
    let r = '';
    for (let s = 0; s <= Math.max(d, 1) + pas; s += pas) {
      // les demi-secondes ont un trait, seules les secondes entières ont un chiffre
      const chiffre = Math.abs(s - Math.round(s)) < 1e-6 ? `<span style="left:${s * pps}px">${formatTemps(s)}</span>` : '';
      r += `<i style="left:${s * pps}px"></i>${chiffre}`;
    }
    this.regle.innerHTML = r;

    const pistes = [...p.pistes].sort((a, b) => ORDRE[a.genre] - ORDRE[b.genre]);
    this.pistes.innerHTML = pistes.map((piste) => {
      let h = '';
      for (const c of piste.clips) h += this._clip(c, piste);
      if (piste.genre === 'principale') {
        piste.clips.forEach((c, i) => {
          if (i === 0) return;
          const actif = c.transition && c.transition.type !== 'aucune';
          h += `<button class="jonction${actif ? ' active' : ''}" data-jonction="${c.id}" style="left:${c.debut * pps}px" aria-label="Transition entre deux clips" title="Transition">${ICONE_JONCTION}</button>`;
        });
        const fin = piste.clips.length ? finClip(piste.clips[piste.clips.length - 1]) : 0;
        h += `<button class="ajout-fin" data-ajout style="left:${fin * pps}px" aria-label="Ajouter des vidéos ou des photos" title="Ajouter">${ICONE_PLUS}</button>`;
      }
      return `<div class="piste g-${piste.genre}" data-piste="${piste.id}" data-genre="${piste.genre}">${h}</div>`;
    }).join('');
  }

  _clip(c, piste) {
    const app = this.app;
    const pps = this.pps;
    const dur = dureeClip(c);
    const sel = c.id === app.selection ? ' sel' : '';
    let corps = '';
    const m = c.media ? app.medias.get(c.media) : null;
    if (c.genre === 'video' || c.genre === 'image') {
      const v = c.vitesse && c.vitesse !== 1 ? ` · ${String(c.vitesse).replace('.', ',')}×` : '';
      const muet = c.genre === 'video' && (c.muet || c.volume === 0) ? ' · muet' : '';
      corps = `<div class="film" style="background-image:url('${m ? m.vignette : ''}')"></div>`
        + `<span class="etiquette">${c.genre === 'image' ? 'Photo · ' : ''}${formatTemps(dur)}${v}${muet}</span>`;
    } else if (c.genre === 'texte') {
      corps = `<span class="etiquette">${esc(c.texte.replace(/\n/g, ' '))}</span>`;
    } else if (c.genre === 'audio') {
      const total = m && m.duree ? m.duree : c.sortie;
      corps = ondeSvg(m && m.onde, c.entree / total, c.sortie / total)
        + `<span class="etiquette">${esc(m ? m.nom : 'Son')}</span>`;
    }
    corps += '<span class="poignee g" data-poignee="g"></span><span class="poignee d" data-poignee="d"></span>';
    return `<div class="clip g-${c.genre}${sel}" data-clip="${c.id}" style="left:${c.debut * pps}px;width:${Math.max(4, dur * pps)}px" role="button" tabindex="-1" aria-label="${c.genre === 'texte' ? 'Texte' : c.genre === 'audio' ? 'Son' : c.genre === 'image' ? 'Photo' : 'Vidéo'}, ${formatTemps(dur)}">${corps}</div>`;
  }

  marquerSelection(id) {
    for (const el of this.pistes.querySelectorAll('.clip.sel')) el.classList.remove('sel');
    if (id) { const el = this.pistes.querySelector(`[data-clip="${id}"]`); if (el) el.classList.add('sel'); }
  }

  /** Fait défiler la bande pour que l'instant t soit sous la tête de lecture. */
  majTemps(t, force = false) {
    const x = Math.round(t * this.pps);
    if (!force && Math.abs(this.defile.scrollLeft - x) < 1) return;
    this.scrollProgramme = x;
    this.defile.scrollLeft = x;
  }

  _aimanter(clip, debut) {
    const seuil = 9 / this.pps;
    const d = dureeClip(clip);
    const cibles = [0, this.app.lecteur.t];
    for (const piste of this.app.p.pistes) for (const c of piste.clips) if (c.id !== clip.id) cibles.push(c.debut, finClip(c));
    let mieux = debut;
    let ecart = seuil;
    for (const x of cibles) {
      if (Math.abs(x - debut) < ecart) { ecart = Math.abs(x - debut); mieux = x; }
      if (Math.abs(x - (debut + d)) < ecart) { ecart = Math.abs(x - debut - d); mieux = x - d; }
    }
    return Math.max(0, mieux);
  }

  _ecouter() {
    const app = this.app;
    this.defile.addEventListener('scroll', () => {
      if (Math.abs(this.defile.scrollLeft - this.scrollProgramme) < 1.5) return;
      this.scrollProgramme = -1;
      app.surDefilement(this.defile.scrollLeft / this.pps);
    }, { passive: true });

    this.regle.addEventListener('click', (e) => {
      const r = this.regle.getBoundingClientRect();
      const t = clamp((e.clientX - r.left) / this.pps, 0, dureeProjet(app.p));
      app.allerA(t);
    });

    this.pistes.addEventListener('click', (e) => {
      const j = e.target.closest('[data-jonction]');
      if (j) { app.selectionner(j.dataset.jonction, { section: 'transition' }); return; }
      if (e.target.closest('[data-ajout]')) { app.ouvrirImport(); return; }
      if (!e.target.closest('.clip') && !this.geste) app.selectionner(null);
    });

    this.pistes.addEventListener('pointerdown', (e) => this._debutGeste(e));
    this.defile.addEventListener('wheel', (e) => {
      if (!e.ctrlKey && !e.metaKey) return;
      e.preventDefault();
      this.zoomer(this.pps * (e.deltaY < 0 ? 1.15 : 1 / 1.15));
    }, { passive: false });

    const dist = (t) => Math.hypot(t[0].clientX - t[1].clientX, t[0].clientY - t[1].clientY);
    this.defile.addEventListener('touchstart', (e) => { if (e.touches.length === 2) this.pince = { d: dist(e.touches), pps: this.pps }; }, { passive: true });
    this.defile.addEventListener('touchmove', (e) => {
      if (!this.pince || e.touches.length !== 2) return;
      const pps = this.pince.pps * (dist(e.touches) / this.pince.d);
      if (!this.rafPince) this.rafPince = requestAnimationFrame(() => { this.rafPince = 0; this.zoomer(pps); });
    }, { passive: true });
    this.defile.addEventListener('touchend', (e) => { if (e.touches.length < 2) this.pince = null; }, { passive: true });

    new ResizeObserver(() => { if (app.p) { this.rendre(); this.majTemps(app.lecteur.t, true); } }).observe(this.zone);
  }

  _debutGeste(e) {
    const el = e.target.closest('.clip');
    if (!el || e.button > 0) return;
    const app = this.app;
    const id = el.dataset.clip;
    const poignee = e.target.closest('[data-poignee]');
    const dejaSel = app.selection === id;
    if (!dejaSel) {
      app.selectionner(id);
      if (e.pointerType !== 'mouse') return; // au doigt : un premier toucher sélectionne, le suivant déplace
    }
    const f = app.trouver(id);
    if (!f) return;
    this.geste = {
      el, id, mode: poignee ? `rogner-${poignee.dataset.poignee}` : 'deplacer',
      x0: e.clientX, y0: e.clientY, left0: parseFloat(el.style.left), w0: parseFloat(el.style.width),
      genre: f.piste.genre, demarre: false, pointeur: e.pointerId,
    };
    el.setPointerCapture(e.pointerId);
    const bouger = (ev) => this._bouger(ev);
    const fin = (ev) => {
      el.removeEventListener('pointermove', bouger);
      el.removeEventListener('pointerup', fin);
      el.removeEventListener('pointercancel', fin);
      this._finGeste(ev, ev.type === 'pointercancel');
    };
    el.addEventListener('pointermove', bouger);
    el.addEventListener('pointerup', fin);
    el.addEventListener('pointercancel', fin);
  }

  _bouger(e) {
    const g = this.geste;
    if (!g || e.pointerId !== g.pointeur) return;
    const dx = e.clientX - g.x0;
    const dy = e.clientY - g.y0;
    if (!g.demarre) {
      if (Math.abs(dx) < 4 && Math.abs(dy) < 4) return;
      g.demarre = true;
      g.el.classList.add('glisse');
      this.app.lecteur.pause();
    }
    if (g.mode === 'deplacer') {
      g.el.style.transform = `translate(${dx}px, ${g.genre === 'principale' ? 0 : dy}px)`;
    } else if (g.mode === 'rogner-g') {
      const d = Math.min(dx, g.w0 - 6);
      g.el.style.left = `${g.left0 + d}px`;
      g.el.style.width = `${g.w0 - d}px`;
    } else {
      g.el.style.width = `${Math.max(6, g.w0 + dx)}px`;
    }
  }

  _finGeste(e, annule) {
    const g = this.geste;
    setTimeout(() => { this.geste = null; }, 0);
    if (!g || !g.demarre) return;
    g.el.classList.remove('glisse');
    if (annule) { this.rendre(); return; }
    const app = this.app;
    const dt = (e.clientX - g.x0) / this.pps;
    const f = app.trouver(g.id);
    if (!f) { this.rendre(); return; }
    const c = f.clip;
    if (g.mode === 'deplacer') {
      if (g.genre === 'principale') {
        app.modifier((p) => deplacerPrincipale(p, g.id, c.debut + dt));
      } else {
        g.el.style.visibility = 'hidden';
        const sous = document.elementFromPoint(e.clientX, e.clientY);
        g.el.style.visibility = '';
        const ligne = sous && sous.closest('.piste');
        const cible = ligne && ligne.dataset.genre === g.genre ? ligne.dataset.piste : f.piste.id;
        const debut = this._aimanter(c, c.debut + dt);
        app.modifier((p) => deplacerLibre(p, g.id, debut, cible));
      }
    } else {
      const m = c.media ? app.medias.get(c.media) : null;
      app.modifier((p) => rogner(p, g.id, g.mode === 'rogner-g' ? 'g' : 'd', dt, m ? m.duree : Infinity));
    }
  }
}

// LA BOBINE · l'aperçu en direct. Chaque clip vidéo ou son a son propre élément <video>/<audio> détaché
// du document ; le moteur de dessin compose leurs images sur la toile, image après image.

import { dureeProjet, tempsSource, clamp, finClip } from './model.js';
import { besoinsA, dessinerImage, actif, fondus } from './rendu.js';
import { urlDe, bitmapDe, bitmapPret } from './medias.js';

const PORTEE_POOL = 20; // secondes : au-delà, un élément est libéré

export class Lecteur {
  constructor(toile, rappels = {}) {
    this.toile = toile;
    this.ctx = toile.getContext('2d');
    this.rappels = rappels;
    this.pool = new Map();
    this.instantanes = new Map();
    this.t = 0;
    this.enLecture = false;
    this.jeton = 0;
    this.selection = null;
    this.cadres = {};
    this.dernierMenage = 0;
    this._tick = this._tick.bind(this);
    this._obtenir = this._obtenir.bind(this);
  }

  charger(projet, medias) {
    this.p = projet;
    this.medias = medias;
    this.dimensionner();
    for (const piste of projet.pistes) {
      for (const c of piste.clips) {
        if (c.genre === 'image') { const m = medias.get(c.media); if (m) bitmapDe(m).then(() => this.afficher()); }
      }
    }
  }

  get duree() { return this.p ? dureeProjet(this.p) : 0; }
  get fps() { return (this.p && this.p.fps) || 30; }

  dimensionner() {
    if (!this.p) return;
    const long = Math.max(this.p.w, this.p.h);
    const petitEcran = Math.min(window.innerWidth, window.innerHeight) < 600;
    const max = petitEcran ? 960 : 1280;
    const r = Math.min(1, max / long);
    const W = Math.round(this.p.w * r);
    const H = Math.round(this.p.h * r);
    if (this.toile.width !== W) this.toile.width = W;
    if (this.toile.height !== H) this.toile.height = H;
    this.W = W;
    this.H = H;
  }

  /** À la toute fin du projet, on montre la dernière image plutôt qu'un écran noir. */
  tVisible(t = this.t) {
    const d = this.duree;
    return d > 0 && t >= d ? Math.max(0, d - 1 / this.fps) : t;
  }

  _el(c) {
    const x = this.pool.get(c.id);
    if (x && x.media === c.media) return x.el;
    const m = this.medias.get(c.media);
    const el = document.createElement(c.genre === 'audio' ? 'audio' : 'video');
    el.preload = 'auto';
    el.muted = true;
    el.playsInline = true;
    el.setAttribute('playsinline', '');
    el.src = urlDe(m) || '';
    el.addEventListener('loadeddata', () => { if (!this.enLecture) this.afficher(); });
    this.pool.set(c.id, { el, media: c.media });
    return el;
  }

  _liberer(id) {
    const x = this.pool.get(id);
    if (!x) return;
    x.el.pause();
    x.el.removeAttribute('src');
    x.el.load();
    this.pool.delete(id);
  }

  /** Libère les éléments des clips loin de la tête de lecture, et ceux des clips disparus. */
  menage(t) {
    const vivants = new Map();
    for (const piste of this.p.pistes) for (const c of piste.clips) vivants.set(c.id, c);
    for (const id of [...this.pool.keys()]) {
      const c = vivants.get(id);
      if (!c || c.debut > t + PORTEE_POOL || finClip(c) < t - PORTEE_POOL) this._liberer(id);
    }
    for (const id of [...this.instantanes.keys()]) if (!vivants.has(id)) this.instantanes.delete(id);
  }

  _instantane(clip, el) {
    if (!el || el.readyState < 2 || !el.videoWidth) return;
    const r = Math.min(1, 480 / Math.max(el.videoWidth, el.videoHeight));
    let c = this.instantanes.get(clip.id);
    if (!c) { c = document.createElement('canvas'); this.instantanes.set(clip.id, c); }
    c.width = Math.round(el.videoWidth * r);
    c.height = Math.round(el.videoHeight * r);
    c.getContext('2d').drawImage(el, 0, 0, c.width, c.height);
    c._l = el.videoWidth;
    c._h = el.videoHeight;
  }

  _obtenir(clip, temps, role) {
    const m = this.medias.get(clip.media);
    if (!m) return null;
    if (clip.genre === 'image') {
      const b = bitmapPret(m);
      if (!b) { bitmapDe(m).then(() => this.afficher()); return null; }
      return { l: b.width, h: b.height, peindre: (c, sx, sy, sl, sh, x, y, l, h) => c.drawImage(b, sx, sy, sl, sh, x, y, l, h) };
    }
    if (clip.genre !== 'video') return null;
    const el = this._el(clip);
    const pret = el.readyState >= 2 && el.videoWidth > 0;
    if (role === 'precedent') {
      if (pret && Math.abs(el.currentTime - temps) < 0.15) return sourceVideo(el);
      const s = this.instantanes.get(clip.id);
      if (!s) return null;
      const k = s.width / s._l;
      return { l: s._l, h: s._h, peindre: (c, sx, sy, sl, sh, x, y, l, h) => c.drawImage(s, sx * k, sy * k, sl * k, sh * k, x, y, l, h) };
    }
    if (!pret) return null;
    if (temps > clip.sortie - 0.25 * (clip.vitesse || 1)) this._instantane(clip, el);
    return sourceVideo(el);
  }

  afficher() {
    if (!this.p) return;
    const t = this.tVisible();
    this.cadres = dessinerImage(this.ctx, this.p, t, this.W, this.H, this._obtenir, this.fps);
    this._dessinerSelection();
    if (this.rappels.apresImage) this.rappels.apresImage(t);
  }

  _dessinerSelection() {
    const r = this.selection && this.cadres[this.selection];
    if (!r || this.enLecture) return;
    const ctx = this.ctx;
    ctx.save();
    ctx.translate(r.x, r.y);
    if (r.rotation) ctx.rotate((r.rotation * Math.PI) / 180);
    ctx.strokeStyle = '#ffd23f';
    ctx.lineWidth = Math.max(2, this.W / 360);
    ctx.setLineDash([this.W / 60, this.W / 90]);
    ctx.strokeRect(-r.l / 2, -r.h / 2, r.l, r.h);
    ctx.restore();
  }

  _synchroniser(t, lecture) {
    for (const piste of this.p.pistes) {
      for (const c of piste.clips) {
        if (c.genre !== 'video' && c.genre !== 'audio') continue;
        const x = this.pool.get(c.id);
        if (!actif(c, t)) {
          if (x && !x.el.paused) x.el.pause();
          continue;
        }
        const el = this._el(c);
        const voulu = tempsSource(c, t);
        const vitesse = clamp(c.vitesse || 1, 0.25, 4);
        if (el.playbackRate !== vitesse) el.playbackRate = vitesse;
        const ton = c.garderTon !== false;
        if (el.preservesPitch !== ton) { el.preservesPitch = ton; el.webkitPreservesPitch = ton; }
        const vol = c.muet ? 0 : clamp((c.volume ?? 1) * fondus(c, t), 0, 1);
        el.volume = vol;
        el.muted = !lecture || vol === 0;
        if (!lecture) continue;
        if (el.paused) {
          if (Math.abs(el.currentTime - voulu) > 0.05) el.currentTime = voulu;
          el.play().catch(() => { el.muted = true; el.play().catch(() => {}); });
        } else if (Math.abs(el.currentTime - voulu) > 0.3) {
          el.currentTime = voulu;
        }
      }
    }
  }

  jouer() {
    if (!this.p || this.enLecture) return;
    if (this.t >= this.duree - 1e-3) this.t = 0;
    this.enLecture = true;
    this.base = this.t;
    this.t0 = performance.now();
    this._synchroniser(this.t, true); // dans le geste de l'utilisateur : iOS autorise alors le son
    this.raf = requestAnimationFrame(this._tick);
    if (this.rappels.etat) this.rappels.etat(true);
  }

  pause() {
    if (!this.enLecture) return;
    this.enLecture = false;
    cancelAnimationFrame(this.raf);
    for (const { el } of this.pool.values()) el.pause();
    if (this.rappels.etat) this.rappels.etat(false);
    this.aller(this.t);
  }

  basculer() { if (this.enLecture) this.pause(); else this.jouer(); }

  _tick() {
    if (!this.enLecture) return;
    const t = this.base + (performance.now() - this.t0) / 1000;
    if (t >= this.duree) {
      this.t = this.duree;
      this.pause();
      if (this.rappels.temps) this.rappels.temps(this.t);
      return;
    }
    this.t = t;
    this._synchroniser(t, true);
    this.afficher();
    if (this.rappels.temps) this.rappels.temps(t);
    if (performance.now() - this.dernierMenage > 2000) { this.dernierMenage = performance.now(); this.menage(t); }
    this.raf = requestAnimationFrame(this._tick);
  }

  /** Va à l'instant t. À l'arrêt, attend que chaque vidéo soit calée sur la bonne image avant de dessiner. */
  async aller(t) {
    if (!this.p) return;
    this.t = clamp(t, 0, this.duree);
    if (this.enLecture) {
      this.base = this.t;
      this.t0 = performance.now();
      this._synchroniser(this.t, true);
      return;
    }
    const jeton = ++this.jeton;
    this._synchroniser(this.t, false);
    this.afficher();
    const tv = this.tVisible();
    const besoins = besoinsA(this.p, tv, this.fps).filter((b) => b.clip.genre === 'video');
    await Promise.all(besoins.map((b) => caler(this._el(b.clip), b.temps)));
    if (jeton !== this.jeton) return;
    for (const b of besoins) if (b.role === 'precedent') this._instantane(b.clip, this._el(b.clip));
    this.afficher();
    this.menage(this.t);
  }

  /** Coordonnées d'un pointeur sur la toile, en fractions de l'image (0 à 1). */
  fraction(ev) {
    const r = this.toile.getBoundingClientRect();
    return { fx: (ev.clientX - r.left) / r.width, fy: (ev.clientY - r.top) / r.height };
  }

  detruire() {
    this.pause();
    for (const id of [...this.pool.keys()]) this._liberer(id);
    this.instantanes.clear();
  }
}

function sourceVideo(el) {
  return { l: el.videoWidth, h: el.videoHeight, peindre: (c, sx, sy, sl, sh, x, y, l, h) => c.drawImage(el, sx, sy, sl, sh, x, y, l, h) };
}

function caler(el, temps) {
  return new Promise((ok) => {
    let fini = false;
    const fin = () => { if (fini) return; fini = true; clearTimeout(minuteur); el.removeEventListener('seeked', fin); ok(); };
    const minuteur = setTimeout(fin, 2000);
    const go = () => {
      if (el.readyState >= 2 && Math.abs(el.currentTime - temps) < 0.001) { fin(); return; }
      el.addEventListener('seeked', fin);
      el.currentTime = temps;
    };
    if (el.readyState >= 1) go();
    else el.addEventListener('loadedmetadata', go, { once: true });
  });
}

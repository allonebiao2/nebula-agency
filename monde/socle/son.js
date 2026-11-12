/* LE MONDE · le son, entièrement SYNTHÉTISÉ (Web Audio, aucun fichier).
   ⚠️ iOS ne joue rien avant un geste : tout démarre au premier toucher, avec
   un tampon muet pour déverrouiller (leçon de MA LETTRE À…). Coupure
   mémorisée dans le navigateur du visiteur. */
/* Les bruitages ENREGISTRÉS (Kenney, CC0 : usage commercial permis, licences dans
   socle/sons/). Chaque nom peut avoir des variantes (pas-1 … pas-5) : on en tire une au
   hasard, avec une vitesse légèrement différente, pour qu'aucun pas ne sonne deux fois
   pareil. Ce qui n'est pas encore là reste synthétisé. */
const BANQUE = { pas: 5, tissu: 4, sac: 2, choix: 2, clic: 1, ouvrir: 1, valider: 1, fermer: 1, cintre: 1, 'porte-ouvre': 0, 'porte-ferme': 0 };

export function creerSon({ base = '../../socle/sons/' } = {}) {
  let ctx = null, maitre = null, bruitBuf = null, rue = null, pluie = null, clim = null, coupe = false, dirEcoute = null, dehors = false;
  let machine = null;
  let musiqueEl = null, musiqueFiltre = null, musiqueGain = null, musiqueVolume = 0.3;
  function reglerMusique(fondu = 0.8) {
    if (!musiqueGain) return;
    const t = ctx.currentTime;
    musiqueGain.gain.setTargetAtTime(dehors ? musiqueVolume * 0.35 : musiqueVolume, t, fondu / 3);
    musiqueFiltre.frequency.setTargetAtTime(dehors ? 650 : 18000, t, 0.25);
  }
  const bruts = {}, tampons = {};
  /* on télécharge tout de suite (116 Ko), on décode au premier geste */
  for (const [nom, n] of Object.entries(BANQUE)) {
    const fichiers = n ? Array.from({ length: n }, (_, i) => nom + '-' + (i + 1)) : [nom];
    bruts[nom] = fichiers.map(f => fetch(base + f + '.mp3').then(r => (r.ok ? r.arrayBuffer() : null)).catch(() => null));
  }
  async function decoder() {
    for (const nom in bruts) {
      const liste = await Promise.all(bruts[nom]);
      tampons[nom] = (await Promise.all(liste.map(b => (b ? ctx.decodeAudioData(b.slice(0)).catch(() => null) : null)))).filter(Boolean);
    }
  }
  /* jouer un bruitage ; avec une position, il est PLACÉ dans l'espace (HRTF) */
  function jouer(nom, { pos = null, vol = 1, vitesse = null } = {}) {
    if (!ctx || coupe) return false;
    const t = tampons[nom]; if (!t || !t.length) return false;
    const src = ctx.createBufferSource(); src.buffer = t[Math.floor(Math.random() * t.length)];
    src.playbackRate.value = vitesse || (0.93 + Math.random() * 0.14);
    const g = ctx.createGain(); g.gain.value = vol;
    if (pos) {
      const p = ctx.createPanner(); p.panningModel = 'HRTF'; p.distanceModel = 'inverse'; p.refDistance = 1.4; p.rolloffFactor = 1.3;
      if (p.positionX) { p.positionX.value = pos.x; p.positionY.value = pos.y; p.positionZ.value = pos.z; } else p.setPosition(pos.x, pos.y, pos.z);
      src.connect(g).connect(p).connect(maitre);
    } else src.connect(g).connect(maitre);
    src.start();
    return true;
  }
  try { coupe = localStorage.getItem('monde:son') === 'coupe'; } catch (e) { /* rien */ }

  function bruit() {
    if (bruitBuf) return bruitBuf;
    bruitBuf = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate);
    const d = bruitBuf.getChannelData(0); let b = 0;
    for (let i = 0; i < d.length; i++) { const w = Math.random() * 2 - 1; b = (b + 0.02 * w) / 1.02; d[i] = w * 0.6 + b * 3.5; }
    return bruitBuf;
  }
  function source(filtre, freq, q, gain) {
    const s = ctx.createBufferSource(); s.buffer = bruit(); s.loop = true;
    const f = ctx.createBiquadFilter(); f.type = filtre; f.frequency.value = freq; f.Q.value = q;
    const g = ctx.createGain(); g.gain.value = gain;
    s.connect(f).connect(g).connect(maitre); s.start();
    return { s, f, g };
  }
  function demarrer() {
    if (ctx) { if (ctx.state === 'suspended') ctx.resume(); return; }
    const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
    ctx = new AC();
    const muet = ctx.createBuffer(1, 1, 22050), m = ctx.createBufferSource(); m.buffer = muet; m.connect(ctx.destination); m.start(0);
    const comp = ctx.createDynamicsCompressor(); comp.connect(ctx.destination);
    maitre = ctx.createGain(); maitre.gain.value = coupe ? 0 : 0.8; maitre.connect(comp);
    rue = source('lowpass', 420, 0.4, 0.035);          /* la rumeur de la rue, derrière la vitre */
    clim = source('lowpass', 180, 0.7, 0.018);         /* le souffle du climatiseur : la pièce existe */
    pluie = source('bandpass', 2400, 0.6, 0);          /* la pluie sur la tôle */
    decoder();
  }
  ['pointerdown', 'keydown', 'touchstart'].forEach(ev => addEventListener(ev, demarrer, { once: false, passive: true }));

  function bip(freq, duree = 0.12, type = 'sine', vol = 0.12, glisse = 0) {
    if (!ctx || coupe) return;
    const t = ctx.currentTime, o = ctx.createOscillator(), g = ctx.createGain();
    o.type = type; o.frequency.setValueAtTime(freq, t); if (glisse) o.frequency.exponentialRampToValueAtTime(freq * glisse, t + duree);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + 0.008); g.gain.exponentialRampToValueAtTime(0.0001, t + duree);
    o.connect(g).connect(maitre); o.start(t); o.stop(t + duree + 0.02);
  }
  function souffle(freq, duree, vol, type = 'bandpass', q = 1) {
    if (!ctx || coupe) return;
    const t = ctx.currentTime, s = ctx.createBufferSource(); s.buffer = bruit();
    const f = ctx.createBiquadFilter(); f.type = type; f.frequency.value = freq; f.Q.value = q;
    const g = ctx.createGain(); g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + 0.01); g.gain.exponentialRampToValueAtTime(0.0001, t + duree);
    s.connect(f).connect(g).connect(maitre); s.start(t, Math.random()); s.stop(t + duree + 0.05);
  }

  return {
    demarrer,
    get coupe() { return coupe; },
    basculer() {
      coupe = !coupe; try { localStorage.setItem('monde:son', coupe ? 'coupe' : 'ouvert'); } catch (e) { /* rien */ }
      if (maitre) maitre.gain.setTargetAtTime(coupe ? 0 : 0.8, ctx.currentTime, 0.1);
      return coupe;
    },
    jouer,
    pas() { if (!jouer('pas', { vol: 0.32 })) souffle(900 + Math.random() * 300, 0.07, 0.05, 'bandpass', 2.5); },
    clic() { if (!jouer('clic', { vol: 0.5 })) { bip(1850, 0.09, 'sine', 0.07); bip(2780, 0.07, 'sine', 0.03); } },
    choix() { if (!jouer('choix', { vol: 0.45 })) bip(1320, 0.1, 'triangle', 0.06); },
    ouvrir() { if (!jouer('ouvrir', { vol: 0.3 })) bip(660, 0.18, 'sine', 0.06, 1.5); },
    sac() { if (jouer('sac', { vol: 0.8 })) { setTimeout(() => jouer('tissu', { vol: 0.5 }), 140); return; } souffle(3200, 0.25, 0.09, 'highpass', 0.7); bip(880, 0.25, 'sine', 0.05, 1.25); },
    valider() { if (!jouer('valider', { vol: 0.55 })) { bip(784, 0.16, 'sine', 0.07); setTimeout(() => bip(1175, 0.28, 'sine', 0.07), 130); } },
    /* placés dans l'espace */
    porte(pos) { jouer('porte-ouvre', { pos, vol: 0.9, vitesse: 1 }); setTimeout(() => jouer('porte-ferme', { pos, vol: 0.8, vitesse: 1 }), 1700); },
    pasDe(pos) { jouer('pas', { pos, vol: 0.22 }); },
    tissu(pos) { jouer('tissu', { pos, vol: 0.55 }); },
    cintre(pos) { jouer('cintre', { pos, vol: 0.35 }); },
    sortir(v) { dehors = v; reglerMusique(); },
    /* LA MUSIQUE DU LIEU (Mongazi, 2026-11-12 : « une musique libre de droit… jouée à l'intérieur
       du salon, qui sera tamisé ») : en boucle, douce, lue en flux (rien n'est décodé en mémoire),
       ÉTOUFFÉE derrière la vitre quand on est dehors, coupée avec les autres sons. Elle ne se
       charge qu'au premier geste (aucune donnée dépensée avant d'entrer). */
    musique(url, volume = 0.3) {
      if (!ctx || musiqueEl) return;
      musiqueEl = new Audio(); musiqueEl.src = url; musiqueEl.loop = true; musiqueEl.preload = 'auto';
      const src = ctx.createMediaElementSource(musiqueEl);
      musiqueFiltre = ctx.createBiquadFilter(); musiqueFiltre.type = 'lowpass';
      musiqueGain = ctx.createGain(); musiqueGain.gain.value = 0; musiqueVolume = volume;
      src.connect(musiqueFiltre); musiqueFiltre.connect(musiqueGain); musiqueGain.connect(maitre);
      musiqueEl.play().catch(() => { /* réessayé au prochain geste */ addEventListener('pointerdown', () => musiqueEl.play().catch(() => {}), { once: true }); });
      reglerMusique(2.5);
    },
    /* la machine à coudre de l'atelier, placée dans l'espace : on l'entend en s'approchant */
    machineACoudre(pos) {
      if (!ctx || machine) return;
      const sr = ctx.sampleRate, buf = ctx.createBuffer(1, sr * 3, sr), d = buf.getChannelData(0);
      for (let i = 0; i < d.length; i++) {
        const t = i / sr, cycle = (t * 13) % 1;                       /* 13 points par seconde */
        const choc = Math.exp(-cycle * 38) * (Math.random() * 2 - 1);
        const moteur = Math.sin(2 * Math.PI * 92 * t) * 0.12 + Math.sin(2 * Math.PI * 184 * t) * 0.05;
        const rafale = (t % 3) < 2.2 ? 1 : 0;                         /* elle s'arrête, elle reprend */
        d[i] = (choc * 0.6 + moteur) * rafale * 0.5;
      }
      const src = ctx.createBufferSource(); src.buffer = buf; src.loop = true;
      const p = ctx.createPanner(); p.panningModel = 'HRTF'; p.distanceModel = 'inverse'; p.refDistance = 1.2; p.rolloffFactor = 1.6;
      if (p.positionX) { p.positionX.value = pos.x; p.positionY.value = pos.y; p.positionZ.value = pos.z; } else p.setPosition(pos.x, pos.y, pos.z);
      const g = ctx.createGain(); g.gain.value = 0.18;
      src.connect(g).connect(p).connect(maitre); src.start();
      machine = { src, g };
    },
    /* l'oreille suit la caméra */
    ecouteur(camera) {
      if (!ctx) return;
      if (!dirEcoute) dirEcoute = camera.position.clone();
      const L = ctx.listener, p = camera.position, d = camera.getWorldDirection(dirEcoute);
      if (L.positionX) { L.positionX.value = p.x; L.positionY.value = p.y; L.positionZ.value = p.z; L.forwardX.value = d.x; L.forwardY.value = d.y; L.forwardZ.value = d.z; L.upX.value = 0; L.upY.value = 1; L.upZ.value = 0; }
      else { L.setPosition(p.x, p.y, p.z); L.setOrientation(d.x, d.y, d.z, 0, 1, 0); }
    },
    tonnerre(delai = 1.5) {
      if (!ctx || coupe) return;
      setTimeout(() => { souffle(90, 3.2, 0.5, 'lowpass', 0.7); souffle(160, 1.6, 0.25, 'lowpass', 0.9); }, delai * 1000);
    },
    /* l'ambiance suit le ciel : pluie forte = la tôle chante, nuit = la rue se calme */
    ambiance(etat) {
      if (!ctx) return;
      const t = ctx.currentTime;
      /* dehors, la rue monte de ~10 dB et le filtre s'ouvre (la vitre ne la retient plus) */
      rue.g.gain.setTargetAtTime(coupe ? 0 : 0.035 * (dehors ? 3.2 : 1) * (1 - etat.nuit * 0.55) * (1 - etat.pluie * 0.5), t, 0.6);
      rue.f.frequency.setTargetAtTime(dehors ? 1600 : 420, t, 0.5);
      if (clim) clim.g.gain.setTargetAtTime(coupe ? 0 : (dehors ? 0.004 : 0.018), t, 0.8);
      pluie.g.gain.setTargetAtTime(coupe ? 0 : 0.11 * etat.pluie, t, 1.5);
      pluie.f.frequency.setTargetAtTime(1800 + etat.pluie * 1400, t, 2);
    },
  };
}

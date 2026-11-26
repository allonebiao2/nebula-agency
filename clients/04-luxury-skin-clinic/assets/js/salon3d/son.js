// Le son du salon (commun aux trois univers).
// La musique : une <audio> nue dans la page, chargée sans jouer, lancée au PREMIER CONTACT (règle de la maison,
// comme Angy Art et NEBULA Agency), fondu à l'entrée, -12 LUFS dans le fichier, joué à 0,66 au téléphone / 0,57 au PC.
// Les bruitages : synthétisés en Web Audio (aucun fichier), discrets, coupés avec la musique.
// Le choix « son : non » est gardé pour les trois pages (sessionStorage `lcSon`).
const mobile = matchMedia("(max-width: 760px)").matches;
const VOLUME = mobile ? 0.66 : 0.57;
let ctx = null, coupe = false, musique = null, demarre = false;
// la clinique, INA et le hub ont déjà leur ambiance (Web Audio) et son bouton dans la barre du bas (#lcMute) :
// là, on ne joue aucune musique de plus, et les bruitages se taisent quand la maison est coupée
const muetMaison = () => { const m = document.getElementById("lcMute"); return m ? !m.classList.contains("playing") : false; };

try { coupe = sessionStorage.getItem("lcSon") === "non"; } catch (e) { /* navigation privée : son actif par défaut */ }

function audio() {
  if (!ctx) {
    const C = window.AudioContext || window.webkitAudioContext;
    if (!C) return null;
    ctx = new C();
  }
  if (ctx.state === "suspended") ctx.resume();
  return ctx;
}

function fondu(el, vers, ms) {
  const de = el.volume, t0 = performance.now();
  const pas = (t) => {
    const k = Math.min(1, (t - t0) / ms);
    el.volume = de + (vers - de) * k;
    if (k < 1) requestAnimationFrame(pas);
    else if (vers === 0) el.pause();
  };
  requestAnimationFrame(pas);
}

function jouer() {
  if (!musique || coupe) return;
  musique.volume = 0;
  const p = musique.play();
  if (p && p.then) p.then(() => fondu(musique, VOLUME, 1800)).catch(() => {});
}

export function installerSon({ bouton = null } = {}) {
  musique = document.getElementById("s3dMusique");
  const majBouton = () => {
    if (!bouton) return;
    bouton.textContent = coupe ? "Son : non" : "Son : oui";
    bouton.setAttribute("aria-pressed", coupe ? "false" : "true");
  };
  majBouton();
  // on télécharge la musique une fois la page chargée, sans la jouer
  const precharger = () => { if (musique && musique.preload === "none") { musique.preload = "auto"; musique.load(); } };
  if (document.readyState === "complete") setTimeout(precharger, 1200);
  else addEventListener("load", () => setTimeout(precharger, 1200), { once: true });

  const premier = () => {
    if (demarre) return;
    demarre = true;
    audio();
    precharger();
    jouer();
    ["pointerdown", "touchstart", "keydown", "wheel", "scroll"].forEach((t) => removeEventListener(t, premier, true));
  };
  ["pointerdown", "touchstart", "keydown", "wheel", "scroll"].forEach((t) => addEventListener(t, premier, { capture: true, passive: true }));

  if (bouton) bouton.addEventListener("click", (e) => {
    e.stopPropagation();
    coupe = !coupe;
    try { sessionStorage.setItem("lcSon", coupe ? "non" : "oui"); } catch (er) { /* rien */ }
    if (coupe && musique) fondu(musique, 0, 500);
    else { demarre = true; jouer(); }
    majBouton();
  });

  // la page passe en arrière-plan : on se tait
  document.addEventListener("visibilitychange", () => {
    if (!musique || coupe) return;
    if (document.hidden) musique.pause();
    else if (demarre) jouer();
  });
}

// ---------- les bruitages ----------
function note(f, { type = "sine", duree = 0.6, vol = 0.12, attaque = 0.005, retard = 0, glisse = 0 } = {}) {
  const c = audio();
  if (!c || coupe || muetMaison()) return;
  const t = c.currentTime + retard;
  const o = c.createOscillator(), g = c.createGain();
  o.type = type;
  o.frequency.setValueAtTime(f, t);
  if (glisse) o.frequency.exponentialRampToValueAtTime(f * glisse, t + duree);
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(vol, t + attaque);
  g.gain.exponentialRampToValueAtTime(0.0001, t + duree);
  o.connect(g).connect(c.destination);
  o.start(t);
  o.stop(t + duree + 0.05);
}

function souffle({ duree = 1.1, vol = 0.05, de = 900, vers = 3200, retard = 0 } = {}) {
  const c = audio();
  if (!c || coupe || muetMaison()) return;
  const t = c.currentTime + retard, n = Math.floor(c.sampleRate * duree);
  const b = c.createBuffer(1, n, c.sampleRate), d = b.getChannelData(0);
  for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / n);
  const s = c.createBufferSource(), f = c.createBiquadFilter(), g = c.createGain();
  s.buffer = b; f.type = "bandpass"; f.Q.value = 0.8;
  f.frequency.setValueAtTime(de, t); f.frequency.exponentialRampToValueAtTime(vers, t + duree);
  g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + 0.15); g.gain.exponentialRampToValueAtTime(0.0001, t + duree);
  s.connect(f).connect(g).connect(c.destination);
  s.start(t);
}

export const bruit = {
  // la porte de verre qui coulisse
  porte() { souffle({ duree: 1.3, vol: 0.06, de: 500, vers: 2400 }); note(1568, { type: "sine", duree: 1.4, vol: 0.035, retard: 0.9 }); },
  // le carillon de l'accueil (trois notes cristallines)
  carillon() { [1318.5, 1760, 2093].forEach((f, i) => note(f, { duree: 1.6, vol: 0.05, retard: i * 0.11 })); },
  // un clic de laiton (plaque, bouton)
  laiton() { note(2400, { type: "triangle", duree: 0.09, vol: 0.06 }); note(3600, { type: "sine", duree: 0.18, vol: 0.025, retard: 0.012 }); },
  // une note d'or (zone qui s'allume)
  or() { note(880, { duree: 0.9, vol: 0.06 }); note(1320, { duree: 1.1, vol: 0.035, retard: 0.04 }); },
  // la vapeur (cabine)
  vapeur() { souffle({ duree: 1.8, vol: 0.035, de: 1800, vers: 700 }); },
  // une page qu'on tourne (le carnet de rendez-vous)
  page() { souffle({ duree: 0.35, vol: 0.05, de: 2200, vers: 5200 }); },
  // --- l'immersion (Mongazi, 26/11 : « des bruitages au toucher, au mouvement, tout ») ---
  // une goutte d'eau (le toucher) : une sinusoïde qui tombe vite, puis son écho plus doux
  goutte() {
    const h = 900 + Math.random() * 500;
    note(h, { duree: 0.16, vol: 0.07, glisse: 0.32 });
    note(h * 1.6, { duree: 0.12, vol: 0.025, glisse: 0.4, retard: 0.07 });
  },
  // un bol chantant (l'arrivée sur une étape) : des partiels non harmoniques, longs, qui battent un peu
  bol() {
    const f = [196, 207.7, 220][(Math.random() * 3) | 0];
    [[1, 0.045, 4.2], [2.76, 0.022, 3.2], [5.4, 0.011, 2.2], [1.004, 0.03, 4.0]].forEach(([m, v, d]) => note(f * m, { duree: d, vol: v, attaque: 0.02 }));
  },
  // une note de verre (survoler un objet qu'on peut toucher)
  tinte() { note(2637, { duree: 0.25, vol: 0.022 }); note(3951, { duree: 0.18, vol: 0.01, retard: 0.01 }); },
  // le menu qui s'ouvre ou se ferme : un souffle bref
  menu() { souffle({ duree: 0.45, vol: 0.04, de: 700, vers: 2600 }); },
};

// LE SOUFFLE DU MOUVEMENT : un bruit d'air filtré, en boucle, dont le volume et la couleur suivent la vitesse de la
// caméra (v de 0 à 1). Silencieux à l'arrêt ; coupé avec le son.
let souffleG = null, souffleF = null;
export function mouvement(v) {
  const c = audio();
  if (!c) return;
  if (!souffleG) {
    const n = c.sampleRate * 2, b = c.createBuffer(1, n, c.sampleRate), d = b.getChannelData(0);
    let dernier = 0;
    for (let i = 0; i < n; i++) { dernier = (dernier + 0.02 * (Math.random() * 2 - 1)) / 1.02; d[i] = dernier * 3.5; }  // bruit brun : un souffle, pas un grésillement
    const s = c.createBufferSource(); s.buffer = b; s.loop = true;
    souffleF = c.createBiquadFilter(); souffleF.type = "lowpass"; souffleF.frequency.value = 500; souffleF.Q.value = 0.6;
    souffleG = c.createGain(); souffleG.gain.value = 0;
    s.connect(souffleF).connect(souffleG).connect(c.destination);
    s.start();
  }
  const muet = coupe || muetMaison();
  const k = muet ? 0 : Math.min(1, Math.max(0, v));
  souffleG.gain.setTargetAtTime(k * 0.11, c.currentTime, 0.18);
  souffleF.frequency.setTargetAtTime(380 + k * 1400, c.currentTime, 0.25);
}
// pour les scripts classiques de la page (le menu) : les mêmes bruitages
window.LCBruit = (nom) => { if (bruit[nom]) bruit[nom](); };

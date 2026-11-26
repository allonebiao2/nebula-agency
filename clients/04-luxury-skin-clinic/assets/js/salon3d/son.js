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
};

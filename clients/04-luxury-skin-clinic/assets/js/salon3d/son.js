// Le son du salon (commun aux trois univers).
// La musique : une <audio> nue dans la page, chargée sans jouer, lancée au PREMIER CONTACT (règle de la maison,
// comme Angy Art et NEBULA Agency), fondu à l'entrée, -12 LUFS dans le fichier, joué à 0,66 au téléphone / 0,57 au PC.
// Les bruitages : de VRAIS enregistrements depuis le 27/11 (assets/js/sons.js, `LCSons`), coupés avec la musique.
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
    // l'horodatage de la première image peut PRÉCÉDER t0 : k négatif donnait un volume négatif, et une exception (27/11)
    const k = Math.min(1, Math.max(0, (t - t0) / ms));
    el.volume = Math.min(1, Math.max(0, de + (vers - de) * k));
    if (k < 1) requestAnimationFrame(pas);
    else if (vers === 0) el.pause();
  };
  requestAnimationFrame(pas);
}

// COMME LA VITRINE NEBULA (27/11) : on réessaie à chaque geste tant que la musique ne joue pas (un iPhone refuse un
// premier toucher ou un défilement : l'ancien code s'arrêtait après cet essai raté, et la musique ne venait jamais)
const GESTES = ["pointerdown", "touchend", "click", "touchstart", "keydown", "wheel", "scroll"];
function retirerGestes() { GESTES.forEach((t) => removeEventListener(t, premier, true)); }
function jouer() {
  if (!musique || coupe) return;
  if (!musique.paused) { retirerGestes(); return; }
  musique.volume = 0;
  const p = musique.play();
  if (p && p.then) p.then(() => { retirerGestes(); fondu(musique, VOLUME, 1800); }).catch(() => {});
}
let premier = () => {};

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

  premier = () => {
    demarre = true;
    audio();
    precharger();
    jouer();      // les gestes ne sont retirés qu'une fois la musique PARTIE
  };
  GESTES.forEach((t) => addEventListener(t, premier, { capture: true, passive: true }));

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
// 27/11 (Mongazi : « enlève ce bruitage générique bizarre ») : les sons synthétisés (sinusoïdes, souffles de bruit
// filtré) sont remplacés par de vrais enregistrements, joués par le lecteur commun de la page (`window.LCSons`,
// assets/js/sons.js). Le « vent » qui suivait la vitesse de la caméra est RETIRÉ : aucun vrai son n'y correspondait.
const S = (nom, vol) => { if (!coupe && window.LCSons) window.LCSons.jouer(nom, { vol }); };
let dernierBol = 0, dernierTinte = 0;
export const bruit = {
  porte() { S("porte"); },                 // l'entrée : une harpe en glissando
  carillon() { S("carillon"); },           // le carillon de l'accueil
  laiton() { S("verre"); },                // un bouton, une plaque : une note de kalimba
  or() { S("cloche"); },                   // une zone qui s'allume : une cloche de méditation
  vapeur() { S("vapeur"); },               // la cabine : de l'eau qu'on verse
  page() { S("page"); },                   // le carnet de rendez-vous
  goutte() { S("goutte"); },               // le toucher dans la scène
  // l'arrivée sur une étape : un bol tibétain, pas plus d'un toutes les 1,5 s (en défilant vite, ils s'empilaient)
  bol() { const t = performance.now(); if (t - dernierBol < 1500) return; dernierBol = t; S("bol"); },
  // le survol d'un objet qu'on peut toucher
  tinte() { const t = performance.now(); if (t - dernierTinte < 180) return; dernierTinte = t; S("tinte"); },
  menu() { S("tissu"); },                  // le menu qui s'ouvre ou se ferme
};

// le mouvement de la caméra ne fait plus de bruit (le vent synthétisé est retiré) : la fonction reste pour les appels
export function mouvement() {}
// pour les scripts classiques de la page (le menu) : les mêmes bruitages
window.LCBruit = (nom) => { if (bruit[nom]) bruit[nom](); };

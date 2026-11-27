/* LES BRUITAGES RÉELS de Luxury Club 229 (27/11, Mongazi : « enlève ce bruitage générique bizarre, remplace par des
   bruitages réels, adaptés à la vitrine »).
   Puis (même jour) : « trouve des sons ULTRA RELAXANTS ». Avant : des bips et des glissandos synthétisés (la sirène
   du menu, le bip carré des filtres, le « vent » qui suivait le défilement). Maintenant : de vrais enregistrements de
   spa (Pixabay, licence Pixabay Content License, usage commercial permis sans attribution), choisis à la MESURE (graves,
   sans aigus durs, bruit de fond bas), coupés, fondus, mis au même volume (`assets/audio/sfx/`, 240 Ko en tout) :
     bol      un bol tibétain frappé (l'arrivée sur une étape de la visite)
     goutte   une goutte d'eau (le toucher dans la scène)
     carillon un carillon à vent (l'accueil)      porte   une harpe en glissando (l'entrée)
     verre    une note de kalimba (un bouton, un produit, le panier)
     tinte    une note douce, sans aigu (le survol)   cloche  une cloche de méditation profonde (une confirmation)
     page     une note douce (le carnet de rendez-vous)   vapeur  de l'eau qu'on verse (la cabine)
     tissu    la harpe, plus courte (le menu qui s'ouvre)
   Un seul lecteur pour les quatre pages : `LCSons.jouer(nom, { vol })`. Les sons se téléchargent au premier geste,
   pas avant. Ils se taisent avec le bouton son de la maison (#lcMute) ou celui de la visite (« Son : non »).
   Une variation de hauteur de ±3 % évite qu'un son répété sonne mécanique. */
(function () {
  if (window.LCSons) return;
  var NOMS = ["bol", "goutte", "carillon", "porte", "verre", "tinte", "cloche", "page", "vapeur", "tissu"];
  var VOL = { bol: 0.5, goutte: 0.45, carillon: 0.42, porte: 0.45, verre: 0.42, tinte: 0.2, cloche: 0.4, page: 0.4, vapeur: 0.32, tissu: 0.38 };
  var BASE = (document.currentScript && document.currentScript.src.replace(/js\/sons\.js.*$/, "")) || "assets/";
  var V = "20261127b";
  var ctx = null, maitre = null, tampons = {}, demandes = {}, pret = false;

  function muet() {
    var m = document.getElementById("lcMute");
    if (m) return !m.classList.contains("playing");
    try { return sessionStorage.getItem("lcSon") === "non"; } catch (e) { return false; }
  }
  function contexte() {
    if (!ctx) {
      var C = window.AudioContext || window.webkitAudioContext;
      if (!C) return null;
      ctx = new C();
      maitre = ctx.createGain(); maitre.gain.value = 0.9; maitre.connect(ctx.destination);
    }
    if (ctx.state === "suspended") { try { ctx.resume(); } catch (e) {} }
    return ctx;
  }
  function charger(nom) {
    if (tampons[nom] || demandes[nom] || !contexte()) return demandes[nom];
    demandes[nom] = fetch(BASE + "audio/sfx/" + nom + ".mp3?v=" + V)
      .then(function (r) { return r.arrayBuffer(); })
      .then(function (b) { return new Promise(function (ok, ko) { ctx.decodeAudioData(b, ok, ko); }); })
      .then(function (t) { tampons[nom] = t; return t; })
      .catch(function () { demandes[nom] = null; });
    return demandes[nom];
  }
  // au premier geste : on ouvre le son et on télécharge les dix fichiers (une fois)
  function premier() {
    if (pret) return;
    pret = true;
    contexte();
    NOMS.forEach(charger);
    ["pointerdown", "touchstart", "keydown"].forEach(function (t) { removeEventListener(t, premier, true); });
  }
  ["pointerdown", "touchstart", "keydown"].forEach(function (t) { addEventListener(t, premier, { capture: true, passive: true }); });

  function jouer(nom, o) {
    o = o || {};
    if (muet() || !contexte()) return;
    var t = tampons[nom];
    if (!t) { var p = charger(nom); if (p && o.attendre !== false) p.then(function () { jouer(nom, { vol: o.vol, attendre: false }); }); return; }
    var s = ctx.createBufferSource(), g = ctx.createGain();
    s.buffer = t;
    s.playbackRate.value = o.hauteur || (1 + (Math.random() - 0.5) * 0.06);
    g.gain.value = (VOL[nom] || 0.4) * (o.vol == null ? 1 : o.vol);
    s.connect(g); g.connect(maitre);
    s.start();
  }
  window.LCSons = { jouer: jouer };
})();

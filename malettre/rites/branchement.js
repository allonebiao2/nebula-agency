/* ═══════════════════════════════════════════════════════════════════════════
   MA LETTRE À… · LE BRANCHEMENT : poser le théâtre dans le seuil de la lettre.
   Lit ce que la lettre a déjà (`D`, `HAB`, `EN`, `doux`, `$`), glisse un canvas
   sous les mots du seuil, cadre l'enveloppe 3D EXACTEMENT où était celle en CSS
   (qui reste là, invisible, pour la mise en page et pour le doigt), et rend la
   main à l'ouverture d'avant au moindre souci : pas de WebGL, aperçu du
   constructeur, erreur. Une lettre s'ouvre TOUJOURS.
   Après l'ouverture, en 3D ou non, la lettre s'écrit (`ecriture.js`).
   Mouvement réduit : rien de tout cela, la lettre de toujours.
   ═══════════════════════════════════════════════════════════════════════════ */
function Branchement(rite) {
  "use strict";
  if (doux || D.apercu) return null;
  var seuil = $("#seuil"), env = $("#env");
  if (!seuil || !env) return null;
  /* la suite de la lettre, puis l'écriture */
  function puis(s) { return function () { s(); try { Ecriture.commencer({ rite: rite }); } catch (e) {} }; }
  /* sans 3D (pas de WebGL, contexte refusé, théâtre tombé avant le geste) : l'ouverture d'avant, puis l'écriture */
  var simple = { rite: null, ouvrir: function (s) {
    env.classList.add("brise"); sonOuverture(); setTimeout(puis(s), 1150); return true;
  } };
  if (!window.WebGLRenderingContext) return simple;
  var style = document.createElement("style");
  /* ⚠️ Le bouton du son est en position absolue : lui ne passe pas en relative (il quitterait son coin). */
  style.textContent = ".theatre{position:absolute;inset:0;width:100%;height:100%;z-index:0;pointer-events:none;display:block}" +
    ".avec-rite #seuil>:not(.theatre):not(.son){position:relative;z-index:1}.avec-rite #seuil>.son{z-index:2}" +
    ".avec-rite #env{opacity:0}.avec-rite #seuil{background:#141019}" +
    /* l'ouverture jouée : les mots s'effacent, la scène garde tout l'écran */
    ".rite-joue #seuil>:not(.theatre):not(.son){opacity:0;transition:opacity .35s;pointer-events:none}";
  document.head.appendChild(style);
  var cv = document.createElement("canvas");
  cv.className = "theatre"; cv.setAttribute("aria-hidden", "true");
  seuil.insertBefore(cv, seuil.firstChild);
  document.documentElement.classList.add("avec-rite");
  var bouton = $("#btn-ouvrir"), motAvant = bouton && bouton.textContent;
  /* le bouton dit le geste de ce rite (« Souffler la bougie ») ; sinon, celui de toujours */
  if (rite.bouton && bouton) bouton.textContent = rite.bouton[EN ? "en" : "fr"] || motAvant;
  var suite = null, perdu = false;
  function cadre() {
    var r = env.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2, l: r.width };
  }
  var donnees = {
    pour: D.pour || L.toi, de: D.de || "", EN: EN, HAB: HAB, cadre: cadre(),
    /* avant l'heure, la cire dort (éteinte, sans souffle) ; à l'heure, elle s'allume et appelle le doigt */
    verrou: function () { return document.documentElement.classList.contains("verrouille"); }
  };
  addEventListener("resize", function () { donnees.cadre = cadre(); });
  function rendre() {
    perdu = true;
    document.documentElement.classList.remove("avec-rite");
    if (bouton && motAvant) bouton.textContent = motAvant;
    if (cv.parentNode) cv.parentNode.removeChild(cv);
  }
  var jeu = Theatre.jouer(cv, rite, donnees, {
    fin: function () { if (suite) { var s = suite; suite = null; s(); } },
    abandon: function (e) {
      /* le théâtre a cédé : si le geste a déjà eu lieu, la lettre s'ouvre quand même, tout de suite. On dit pourquoi
         (une console, rien d'autre) : un abandon silencieux passerait des semaines inaperçu */
      if (e && window.console) console.warn("malettre · théâtre abandonné :", e && e.message || e);
      rendre();
      if (suite) { var s = suite; suite = null; s(); }
    }
  });
  if (!jeu) { rendre(); return simple; }
  return {
    rite: rite,
    /* ouvrir(suite) → vrai : le théâtre (ou l'ouverture d'avant) joue, et appellera suite au bon moment */
    ouvrir: function (s) {
      if (perdu) return simple.ouvrir(s);
      suite = puis(s); jeu.ouvrir();
      document.documentElement.classList.add("rite-joue");
      /* le seuil parti, on libère la carte graphique */
      setTimeout(function () { jeu.arreter(); if (cv.parentNode) cv.parentNode.removeChild(cv); }, (rite.duree + 1.6) * 1000);
      return true;
    }
  };
}

/* ═══════════════════════════════════════════════════════════════════════════
   MA LETTRE À… · LE BRANCHEMENT : poser le théâtre dans le seuil de la lettre.
   Lit ce que la lettre a déjà (`D`, `HAB`, `EN`, `doux`, `$`), glisse un canvas
   sous les mots du seuil, cadre l'enveloppe 3D EXACTEMENT où était celle en CSS
   (qui reste là, invisible, pour la mise en page et pour le doigt), et rend la
   main à l'ouverture d'avant au moindre souci : pas de WebGL, aperçu du
   constructeur, erreur. Une lettre s'ouvre TOUJOURS.
   Un rite `plein` (les portes) prend tout l'écran : le doigt et l'inclinaison
   du téléphone lui sont passés, toucher la scène presse le bouton (le code
   secret reste respecté), et au moment où la lettre se montre, la scène passe
   DEVANT la page : les portes s'ouvrent sur la vraie lettre.
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
  var plein = !!rite.plein, racine = document.documentElement;
  var style = document.createElement("style");
  /* ⚠️ Le bouton du son est en position absolue : lui ne passe pas en relative (il quitterait son coin). */
  style.textContent = ".theatre{position:absolute;inset:0;width:100%;height:100%;z-index:0;pointer-events:none;display:block}" +
    ".avec-rite #seuil>:not(.theatre):not(.son){position:relative;z-index:1}.avec-rite #seuil>.son{z-index:2}" +
    ".avec-rite #env{opacity:0}.avec-rite #seuil{background:#141019}" +
    /* l'ouverture jouée : les mots s'effacent, la scène garde tout l'écran */
    ".rite-joue #seuil>:not(.theatre):not(.son){opacity:0;transition:opacity .35s;pointer-events:none}" +
    (plein ?
      /* plein écran : les mots du seuil sont gravés sur les portes (lus par le lecteur d'écran, cachés à l'œil) ;
         toute la scène est sensible au doigt ; le compte à rebours garde un fond qui se lit sur n'importe quel motif */
      ".rite-plein #seuil .pour,.rite-plein #s-touche{position:absolute!important;width:1px;height:1px;margin:0;overflow:hidden;" +
      "clip:rect(0 0 0 0);white-space:nowrap}.rite-plein .theatre{pointer-events:auto;touch-action:none;cursor:pointer}" +
      ".rite-plein #env{pointer-events:none}.rite-plein #attente{background:rgba(16,12,20,.84);border-radius:18px;padding:14px 20px}" +
      ".theatre.devant{position:fixed;z-index:101;pointer-events:none}" +
      ".rite-indice{position:fixed;left:50%;bottom:max(28px,env(safe-area-inset-bottom));transform:translate(-50%,10px);z-index:102;" +
      "font:500 14px/1.3 -apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,sans-serif;color:#f4ede0;background:rgba(20,16,25,.84);" +
      "padding:11px 18px;border-radius:999px;white-space:nowrap;opacity:0;pointer-events:none;" +
      "transition:opacity .5s,transform .7s cubic-bezier(.2,1,.3,1)}.rite-indice.vu{opacity:1;transform:translate(-50%,0)}" : "");
  document.head.appendChild(style);
  var cv = document.createElement("canvas");
  cv.className = "theatre"; cv.setAttribute("aria-hidden", "true");
  seuil.insertBefore(cv, seuil.firstChild);
  racine.classList.add("avec-rite");
  if (plein) racine.classList.add("rite-plein");
  var bouton = $("#btn-ouvrir"), motAvant = bouton && bouton.textContent;
  /* le bouton dit le geste de ce rite (« Souffler la bougie ») ; sinon, celui de toujours */
  if (rite.bouton && bouton) bouton.textContent = rite.bouton[EN ? "en" : "fr"] || motAvant;
  var suite = null, perdu = false, lance = false, revele = false, jeu = null, indice = null;
  function cadre() {
    var r = env.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2, l: r.width };
  }
  var donnees = {
    pour: D.pour || L.toi, de: D.de || "", EN: EN, HAB: HAB, cadre: cadre(),
    /* avant l'heure, la cire dort (éteinte, sans souffle) ; à l'heure, elle s'allume et appelle le doigt */
    verrou: function () { return racine.classList.contains("verrouille"); },
    /* pour les contrôles seulement : repousser l'ouverture automatique des portes (jamais posé dans une vraie lettre) */
    auto: window.__malettreAuto
  };
  addEventListener("resize", function () { donnees.cadre = cadre(); });
  function liberer() {
    if (jeu) jeu.arreter();
    [cv, indice].forEach(function (e) { if (e && e.parentNode) e.parentNode.removeChild(e); });
  }
  function rendre() {
    perdu = true;
    racine.classList.remove("avec-rite"); racine.classList.remove("rite-plein");
    if (bouton && motAvant) bouton.textContent = motAvant;
    liberer();
  }
  jeu = Theatre.jouer(cv, rite, donnees, {
    fin: function () {
      revele = true;
      if (indice) indice.classList.remove("vu");
      /* les portes passent DEVANT la page : la lettre apparaît derrière elles pendant qu'elles s'ouvrent */
      if (plein) { cv.classList.add("devant"); document.body.appendChild(cv); }
      if (suite) { var s = suite; suite = null; s(); }
    },
    fini: liberer,
    abandon: function (e) {
      /* le théâtre a cédé : si le geste a déjà eu lieu, la lettre s'ouvre quand même, tout de suite. On dit pourquoi
         (une console, rien d'autre) : un abandon silencieux passerait des semaines inaperçu */
      if (e && window.console) console.warn("malettre · théâtre abandonné :", e && e.message || e);
      rendre();
      if (suite) { var s = suite; suite = null; s(); }
    }
  });
  if (!jeu) { rendre(); return simple; }
  if (plein) {
    if (rite.indice) {
      indice = document.createElement("div");
      indice.className = "rite-indice"; indice.setAttribute("aria-hidden", "true");
      indice.textContent = rite.indice[EN ? "en" : "fr"];
      document.body.appendChild(indice);
      /* le rite peut changer sa phrase en route (« Encore un ») ou la faire taire */
      rite.dire = function (m) { if (revele) return; indice.textContent = m[EN ? "en" : "fr"]; indice.classList.add("vu"); };
      rite.taire = function () { indice.classList.remove("vu"); };
    }
    var envoi = function (type) {
      return function (ev) {
        var t = type === "bouge" ? (ev.buttons || ev.pointerType === "touch" ? "glisse" : "survol") : type;
        /* la phrase s'efface au doigt AVANT que le rite le reçoive : il peut en dire une autre (« Encore un ») */
        if (t === "bas" && lance && indice) indice.classList.remove("vu");
        jeu.toucher({ type: t, x: ev.clientX, y: ev.clientY, id: ev.pointerId });
      };
    };
    var x0 = null;
    cv.addEventListener("pointerdown", function (ev) { x0 = ev.clientX; try { cv.setPointerCapture(ev.pointerId); } catch (x) {} envoi("bas")(ev); });
    cv.addEventListener("pointermove", function (ev) {
      envoi("bouge")(ev);
      /* on a voulu écarter les portes avant de toucher le cachet : c'est le même geste, on presse le bouton pour lui */
      if (!lance && x0 != null && (ev.buttons || ev.pointerType === "touch") && Math.abs(ev.clientX - x0) > 24 && bouton) { x0 = null; bouton.click(); }
    });
    cv.addEventListener("pointerup", function (ev) { x0 = null; envoi("haut")(ev); });
    cv.addEventListener("pointercancel", envoi("haut"));
    /* avant le geste, toucher la scène, c'est presser le bouton : le code secret, s'il y en a un, est demandé */
    cv.addEventListener("click", function () { if (!lance && bouton) bouton.click(); });
    /* l'inclinaison d'un téléphone Android promène la lumière (iOS demande une permission : on s'en passe) */
    var zero = null;
    addEventListener("deviceorientation", function (ev) {
      if (ev.gamma == null || revele) return;
      if (!zero) zero = [ev.gamma, ev.beta];
      jeu.toucher({ type: "incline", x: (ev.gamma - zero[0]) / 25, y: (ev.beta - zero[1]) / 25 });
    });
  }
  return {
    rite: rite,
    /* ouvrir(suite) → vrai : le théâtre (ou l'ouverture d'avant) joue, et appellera suite au bon moment */
    ouvrir: function (s) {
      if (perdu) return simple.ouvrir(s);
      lance = true;
      suite = puis(s); jeu.ouvrir();
      racine.classList.add("rite-joue");
      if (indice) setTimeout(function () { if (!revele) indice.classList.add("vu"); }, 1100);
      /* garde-fou : le théâtre se libère de lui-même (`fini`) ; s'il ne le faisait pas, au plus tard ici */
      setTimeout(liberer, (plein ? 90 : (rite.duree || 4) + 2.5) * 1000);
      return true;
    }
  };
}

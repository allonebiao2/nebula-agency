/* ═══════════════════════════════════════════════════════════════════════════
   MA LETTRE À… · LA LETTRE QUI S'ÉCRIT (2026-10-22)
   Mongazi : « le texte aussi doit être animé et venir s'écrire lentement […] faire durer : c'est l'expérience qui
   est mise en avant pour impressionner la personne qui reçoit ». Après l'ouverture, la lettre ne s'affiche pas,
   elle S'ÉCRIT, dans l'ordre de la page : l'occasion, le titre lettre à lettre (l'encre arrive couleur de cire et
   sèche couleur d'encre), le texte au rythme d'une main (une pause à chaque mot, plus longue aux virgules, aux
   points, au bout d'un paragraphe), une plume d'or qui suit et gratte ; puis la phrase à gratter, les photos une à
   une, les jours qui roulent, la formule, le nom, le trait de la signature, et la pluie de l'habillage en dernier.
   ─ Un toucher : la main accélère ; un second (ou Échap) : tout est écrit. Relue sur le même appareil, plus vite.
   ─ Une longue lettre s'écrit plus vite (40 s de texte au plus, 70 s pour une lettre fleuve), jamais en 3 minutes.
   ─ Le texte de l'acheteur n'est jamais interprété : chaque caractère est posé par `textContent`. Une copie entière
     reste lisible par un lecteur d'écran (`.sr`), les caractères lui sont cachés ; à la fin, le texte redevient
     du texte (sélection, traduction, recherche).
   ─ Les caractères pas encore écrits sont en `visibility:hidden` (aucun filtre sur 3 000 éléments) ; seuls ceux
     qui arrivent s'animent.
   ═══════════════════════════════════════════════════════════════════════════ */
var Ecriture = (function () {
  "use strict";
  /* ⚠️ La règle générale `.vu:not(.c)` vient AVANT les cas particuliers (même poids : la dernière gagne) */
  var CSS = ".ecrit-lent .lettre p{animation:none!important;opacity:1!important;filter:none!important;transform:none!important}" +
    ".ecrit-lent .vu:not(.c){opacity:1;filter:none;transform:none}" +
    /* le titre reçoit le focus pour le lecteur d'écran ; ce n'est pas un bouton, il ne porte pas d'anneau */
    ".ecrit-lent #l-titre:focus{outline:none}.ecrit-lent .c{visibility:hidden}.ecrit-lent .mot{white-space:nowrap}.ecrit-lent .c.b{display:inline-block}" +
    ".ecrit-lent .c.vu{visibility:visible;animation:ec-a .5s ease-out both,ec-c 1.8s ease-out both}" +
    ".ecrit-lent .titre .c.vu{animation:ec-a .6s ease-out both,ec-c 2.4s ease-out both,ec-t .9s cubic-bezier(.2,1,.3,1) both}" +
    "@keyframes ec-a{from{opacity:0;filter:blur(3px)}}@keyframes ec-c{from{color:var(--cire-texte)}}" +
    "@keyframes ec-t{from{transform:translateY(.14em) scale(.6)}}" +
    ".ecrit-lent .occasion{opacity:0;filter:blur(4px);transform:translateY(6px);transition:opacity 1s,filter 1s,transform 1.2s cubic-bezier(.2,1,.3,1)}" +
    ".ecrit-lent .filet{transform:scaleX(0);transition:transform 1.2s cubic-bezier(.2,1,.3,1)}" +
    ".ecrit-lent .polaroid{opacity:0;transform:translateY(46px) rotate(calc(var(--r,-2deg) * -2.5)) scale(.92);" +
    "transition:opacity .9s,transform 1.4s cubic-bezier(.2,1,.3,1)}.ecrit-lent .polaroid.vu{transform:rotate(var(--r,-2deg))}" +
    ".ecrit-lent .polaroid .cadre::after{animation:none!important}" +
    ".ecrit-lent .polaroid.vu .cadre::after{animation:developpe 2.4s .35s var(--t) forwards!important}" +
    ".ecrit-lent .gratter,.ecrit-lent .compte,.ecrit-lent .repondre,.ecrit-lent .pied,.ecrit-lent .retrait{opacity:0;" +
    "transform:translateY(14px);transition:opacity 1s,transform 1.2s cubic-bezier(.2,1,.3,1)}" +
    ".ecrit-lent .signe .nom path{animation:none!important}.ecrit-lent .signe .nom.trace path{animation:trace 1.6s var(--t) forwards!important}" +
    ".plume{position:absolute;left:0;top:0;width:30px;height:30px;pointer-events:none;z-index:2;opacity:0;" +
    "transition:opacity .4s,transform .12s linear;will-change:transform}.plume.vu{opacity:1}" +
    ".plume i{position:absolute;left:3px;bottom:3px;width:7px;height:7px;border-radius:50%;" +
    "background:radial-gradient(circle,rgba(255,236,170,.95),rgba(224,194,102,0) 70%);box-shadow:0 0 12px 4px rgba(224,194,102,.45)}" +
    ".ecrit-astuce{position:fixed;left:50%;bottom:max(18px,env(safe-area-inset-bottom));transform:translateX(-50%);z-index:120;" +
    "font:500 13px/1.3 -apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,sans-serif;color:#f4ede0;background:rgba(20,16,25,.8);" +
    "padding:9px 16px;border-radius:999px;white-space:nowrap;opacity:0;transition:opacity .6s;pointer-events:none}.ecrit-astuce.vu{opacity:1}";
  var PLUME = '<svg viewBox="0 0 30 30" width="30" height="30" aria-hidden="true"><path d="M6 24 C9 15 16 7 27 3 C24 13 17 20 8 25 Z" ' +
    'fill="#e0c266" stroke="#7a5a14" stroke-width=".8"/><path d="M6 24 L15 14" stroke="#7a5a14" stroke-width=".8"/></svg><i></i>';
  /* un caractère, c'est ce que l'œil voit : un emoji composé ou une lettre accentuée restent entiers */
  var SEG = typeof Intl !== "undefined" && Intl.Segmenter ? new Intl.Segmenter("fr", { granularity: "grapheme" }) : null;
  function graphemes(s) {
    if (SEG) return Array.from(SEG.segment(s), function (x) { return x.segment; });
    var out = [];
    Array.from(s).forEach(function (ch) {
      var n = out.length;
      if (n && (/[̀-ͯ‍️]|[\u{1f3fb}-\u{1f3ff}]/u.test(ch) || out[n - 1].slice(-1) === "‍")) out[n - 1] += ch;
      else out.push(ch);
    });
    return out;
  }

  /* Poser chaque caractère dans son span. Les espaces restent du texte (la ligne se coupe exactement comme avant) ;
     au titre, les caractères d'un mot court sont des blocs (pour grandir), tenus ensemble dans un mot insécable. */
  function decouper(el, titre) {
    var texte = el.textContent, spans = [];
    var lu = document.createElement("span"), vu = document.createElement("span");
    lu.className = "sr"; lu.textContent = texte; vu.setAttribute("aria-hidden", "true");
    texte.split(/(\s+)/).forEach(function (bout) {
      if (!bout) return;
      if (/^\s+$/.test(bout)) { vu.appendChild(document.createTextNode(bout)); if (spans.length) spans[spans.length - 1].fm = 1; return; }
      var g = graphemes(bout), bloc = titre && g.length <= 12, mot = vu;
      if (bloc) { mot = document.createElement("span"); mot.className = "mot"; vu.appendChild(mot); }
      g.forEach(function (ch) {
        var c = document.createElement("span");
        c.className = bloc ? "c b" : "c"; c.textContent = ch; mot.appendChild(c); spans.push(c);
      });
    });
    el.textContent = "";
    el.appendChild(lu); el.appendChild(vu);
    return { spans: spans, rendre: function () { el.textContent = texte; } };
  }

  function commencer(o) {
    o = o || {};
    var lettre = $("#lettre"), feuille = lettre && lettre.querySelector(".feuille");
    if (doux || !feuille) return false;
    var anglais = typeof EN !== "undefined" && EN;
    var cle = "malettre:lue:" + location.pathname, deja = false;
    try { deja = localStorage.getItem(cle) === "1"; } catch (e) {}
    var style = document.createElement("style");
    style.textContent = CSS; document.head.appendChild(style);
    document.documentElement.classList.add("ecrit-lent");
    var vitesse = deja ? 4 : 1, fini = false, enCours = true, touches = 0;
    var plume = document.createElement("div");
    plume.className = "plume"; plume.innerHTML = PLUME; feuille.appendChild(plume);
    var astuce = document.createElement("div");
    astuce.className = "ecrit-astuce"; astuce.setAttribute("aria-hidden", "true"); document.body.appendChild(astuce);
    /* la pluie de l'habillage attend la signature : son premier appel (à l'ouverture) est avalé, une fois */
    if (typeof pleuvoir === "function") { var vraie = pleuvoir; pleuvoir = function () { pleuvoir = vraie; }; }

    /* ce qui s'écrit, et ce qui apparaît */
    var visible = function (s) { var e = $(s); return e && !e.hidden ? e : null; };
    var occ = $("#l-occasion"), filet = feuille.querySelector(".filet"), nomP = $("#l-de");
    var cT = decouper($("#l-titre"), true);
    var cP = Array.prototype.map.call(feuille.querySelectorAll("#l-corps p"), function (p) { return decouper(p, false); });
    var cF = decouper($("#l-formule"), false), cN = decouper($("#l-de-nom"), false);
    var photos = Array.prototype.slice.call(feuille.querySelectorAll(".polaroid"));
    var morceaux = cP.concat([cF, cN]);
    /* une longue lettre s'écrit plus vite : 40 s de texte au plus, 70 s pour une lettre fleuve */
    var n = 0;
    cP.forEach(function (p) { n += p.spans.length; });
    var nominal = n * 42.5, cible = nominal <= 40000 ? nominal : Math.min(70000, 40000 + (nominal - 40000) * 0.2);
    var bCorps = 34 * (nominal ? cible / nominal : 1), bTitre = Math.min(95, 3500 / Math.max(1, cT.spans.length * 1.15));

    /* la plume suit le dernier caractère ; la page défile seule, sauf quand on la tient */
    var tenu = 0, defile = 0;
    ["wheel", "touchmove"].forEach(function (ev) { addEventListener(ev, function () { tenu = Date.now(); }, { passive: true }); });
    function suivre(c) {
      var r = c.getBoundingClientRect(), f = feuille.getBoundingClientRect(), now = Date.now();
      plume.style.transform = "translate(" + Math.round(r.right - f.left - 5) + "px," + Math.round(r.top + r.height * 0.76 - f.top - 24) +
        "px) rotate(" + ((Math.random() - 0.5) * 7).toFixed(1) + "deg)";
      if (now - tenu > 2500 && now - defile > 650 && (r.bottom > innerHeight * 0.72 || r.top < innerHeight * 0.1)) {
        defile = now;
        scrollTo({ top: scrollY + r.top - innerHeight * 0.42, behavior: "smooth" });
      }
    }
    var dernierSon = 0;
    function gratte() {
      var now = Date.now();
      if (now - dernierSon > 85) { dernierSon = now; Atelier.Son.plume(); }
    }
    /* le rythme d'une main : le caractère, puis la pause que demandent le mot qui finit et la ponctuation */
    function attente(c, base) {
      var ch = c.textContent, k = /[.!?…]/.test(ch) ? 9 : /[,;:]/.test(ch) ? 4.5 : c.fm ? 1.6 : 1;
      return base * k * (0.75 + Math.random() * 0.5) / vitesse;
    }
    /* écrire une suite de caractères ; quand la main va vite, plusieurs par battement (une minuterie ne descend pas
       sous 4 ms) */
    function ecrire(spans, base, apres) {
      var i = 0;
      (function un() {
        if (fini) { for (; i < spans.length; i++) spans[i].classList.add("vu"); apres(); return; }
        var d = 0, c = null;
        while (i < spans.length && d < 16) { c = spans[i++]; c.classList.add("vu"); d += attente(c, base); }
        if (c) { suivre(c); gratte(); }
        setTimeout(i < spans.length ? un : apres, d);
      })();
    }
    function attendre(ms, k) { setTimeout(k, fini ? 0 : ms / vitesse); }
    /* ce qui apparaît vient se montrer : une photo qui se développe sous le pli de l'écran, personne ne la voit */
    function montrer(el, ms, k) {
      if (el) {
        el.classList.add("vu");
        var r = el.getBoundingClientRect(), now = Date.now();
        if (!fini && now - tenu > 2500 && (r.bottom > innerHeight * 0.88 || r.top < 0)) {
          defile = now;
          scrollTo({ top: scrollY + r.top - Math.max(innerHeight * 0.18, (innerHeight - r.height) / 2), behavior: "smooth" });
        }
      }
      attendre(ms, k);
    }
    function voir(sur) { plume.classList.toggle("vu", sur); }

    var etapes = [], gratter = visible("#l-gratter"), compte = visible("#l-compte");
    etapes.push(function (k) { montrer(occ, 650, k); });
    etapes.push(function (k) { voir(true); ecrire(cT.spans, bTitre, k); });
    etapes.push(function (k) { voir(false); montrer(filet, 600, k); });
    cP.forEach(function (p, j) {
      etapes.push(function (k) { voir(true); ecrire(p.spans, bCorps, function () { attendre(j < cP.length - 1 ? 560 : 320, k); }); });
    });
    if (gratter) etapes.push(function (k) { voir(false); montrer(gratter, 1000, k); });
    photos.forEach(function (ph) { etapes.push(function (k) { voir(false); montrer(ph, 1100, k); }); });
    if (compte) etapes.push(function (k) {
      voir(false); montrer(compte, 0, function () { if (typeof rouler === "function") rouler(); attendre(1400, k); });
    });
    etapes.push(function (k) { voir(true); ecrire(cF.spans, 45, function () { attendre(300, k); }); });
    etapes.push(function (k) { ecrire(cN.spans, 80, k); });
    etapes.push(function (k) { voir(false); if (nomP) nomP.classList.add("trace"); attendre(1300, k); });
    [visible("#l-repondre"), visible("#l-pied"), visible("#l-retrait")].forEach(function (el) {
      if (el) etapes.push(function (k) { montrer(el, 450, k); });
    });

    var etape = 0;
    function prochaine() {
      if (etape >= etapes.length) { terminer(); return; }
      try { etapes[etape++](prochaine); } catch (e) { secours(); }
    }
    /* au moindre souci, tout est écrit d'un coup : une lettre se lit TOUJOURS */
    function secours() {
      fini = true;
      document.querySelectorAll(".ecrit-lent .c,#l-occasion,.filet,.polaroid,#l-gratter,#l-compte,#l-repondre,#l-pied,#l-retrait")
        .forEach(function (e) { e.classList.add("vu"); });
      if (nomP) nomP.classList.add("trace");
      terminer();
    }
    function terminer() {
      if (!enCours) return;
      enCours = false; fini = true;
      voir(false); astuce.classList.remove("vu");
      try { localStorage.setItem(cle, "1"); } catch (e) {}
      if (typeof pleuvoir === "function" && typeof HAB !== "undefined") pleuvoir(HAB.pluie);
      setTimeout(function () {
        morceaux.forEach(function (m) { m.rendre(); });
        [plume, astuce].forEach(function (e) { if (e.parentNode) e.parentNode.removeChild(e); });
      }, 2400);
      if (o.fin) o.fin();
    }
    function dire(mot, ms) {
      astuce.textContent = mot; astuce.classList.add("vu");
      clearTimeout(dire.t); dire.t = setTimeout(function () { astuce.classList.remove("vu"); }, ms);
    }
    /* un toucher : plus vite ; un second : tout de suite */
    function presser(tout) {
      if (!enCours) return;
      touches++;
      if (touches === 1 && !tout) {
        vitesse = Math.max(vitesse * 3.5, 3.5);
        dire(anglais ? "Tap again to see it all" : "Encore une fois pour tout voir", 2600);
      } else { fini = true; astuce.classList.remove("vu"); }
    }
    lettre.addEventListener("click", function (e) {
      if (!e.target.closest || !e.target.closest("a,button,input,canvas,.g-zone")) presser(false);
    });
    addEventListener("keydown", function (e) {
      if (e.key === "Escape") presser(true);
      else if (e.key === "Enter" && e.target === document.body) presser(false);
    });
    setTimeout(function () {
      if (enCours && !touches) dire(anglais ? "Tap to write faster" : "Touche pour écrire plus vite", 5200);
    }, deja ? 300 : 3600);
    /* un filet de sûreté, bien au-delà de la durée prévue */
    setTimeout(function () { if (enCours) secours(); }, (cible + photos.length * 1100 + 20000) * 2 / vitesse);
    setTimeout(prochaine, o.delai == null ? 1100 : o.delai);
    return true;
  }
  return { commencer: commencer };
})();

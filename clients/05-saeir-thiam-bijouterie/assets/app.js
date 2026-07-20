/* ============================================================
   DJAMBAR TEAM — Comportements partagés
   Nav · reveal · galerie filtrable + lightbox · ambiance audio
   Progressive enhancement : si JS off, le contenu reste lisible.
   ============================================================ */
(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isMobile = window.matchMedia("(max-width: 760px)").matches;
  var saveData = !!(navigator.connection && navigator.connection.saveData);

  /* ---------- Préchargeur « écrin » : chargement + ouverture animée ----------
     Couverture posée AVANT peinture par html.preloading (CSS). Ici on enrichit
     d'un monogramme tracé + éclat + barre, puis on OUVRE l'écrin (2 panneaux qui
     s'écartent) sur le hero. Tout est piloté par minuteries (robuste onglet caché /
     rendu headless) ; un filet inline (5 s) retire la couverture même si ce JS tombe.
     1re visite de session = intro complète ; navigation interne = ouverture rapide. */
  (function () {
    var root = document.documentElement;
    if (!root.classList.contains("preloading")) return;
    var firstVisit = true;
    try { firstVisit = !sessionStorage.getItem("djbIntro"); sessionStorage.setItem("djbIntro", "1"); } catch (e) {}

    var pl = document.createElement("div");
    pl.className = "preloader";
    pl.setAttribute("aria-hidden", "true");
    pl.innerHTML =
      '<div class="pl-panel pl-top"></div>' +
      '<div class="pl-panel pl-bot"></div>' +
      '<i class="pl-seam"></i>' +
      '<div class="pl-brand">' +
        '<svg class="pl-mark" viewBox="0 0 64 66" fill="none" aria-hidden="true">' +
          '<path pathLength="1" d="M16 22 L24 8 H40 L48 22 L32 58 Z M16 22 H48 M24 8 L32 22 L40 8"/>' +
        '</svg>' +
        '<div class="pl-word">DJAMBAR TEAM</div>' +
        '<div class="pl-sub">Saeir Thiam · Cotonou</div>' +
        '<div class="pl-bar"><i class="pl-fill"></i></div>' +
      '</div>';
    document.body.appendChild(pl);
    root.style.overflow = "hidden";

    var fill = pl.querySelector(".pl-fill");
    var done = false;
    function setFill(v) { if (fill) fill.style.clipPath = "inset(0 " + v + " 0 0)"; }
    function remove() { if (pl.parentNode) pl.parentNode.removeChild(pl); root.style.overflow = ""; }
    function openCase() {
      root.classList.remove("preloading");        // retire la couverture ::before
      pl.classList.add("pl-reveal");               // l'écrin s'ouvre
      setTimeout(remove, reduce ? 340 : (firstVisit ? 1080 : 720));
    }
    function reveal() {
      if (done) return; done = true;
      setFill("0%");                               // la barre se complète
      setTimeout(openCase, reduce ? 60 : (firstVisit ? 360 : 90));
    }

    if (reduce) { pl.classList.add("pl-reduced"); setTimeout(reveal, 220); return; }
    if (!firstVisit) { pl.classList.add("pl-quick"); setTimeout(reveal, 280); return; }

    /* intro complète */
    pl.classList.add("pl-in");
    setTimeout(function () { if (!done) setFill("12%"); }, 90);   // 0 -> ~88 % pendant le chargement
    var MIN = 1200, CAP = 2500, t0 = Date.now(), fired = false;
    function go() { if (fired) return; fired = true; setTimeout(reveal, Math.max(0, MIN - (Date.now() - t0))); }
    if (document.readyState === "complete") { go(); }
    else {
      window.addEventListener("load", go, { once: true });
      setTimeout(go, CAP);                         // filet : on révèle même si « load » tarde
    }
  })();

  /* ---------- Année ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* ---------- Halo lumineux qui suit la navigation (desktop) ---------- */
  if (!reduce && window.matchMedia("(hover:hover) and (pointer:fine)").matches) {
    var halo = document.createElement("div");
    halo.className = "halo";
    halo.setAttribute("aria-hidden", "true");
    document.body.appendChild(halo);
    var tx = window.innerWidth / 2, ty = window.innerHeight * 0.3, cx = tx, cy = ty, raf = null, shown = false;
    function tick() {
      cx += (tx - cx) * 0.14; cy += (ty - cy) * 0.14;
      halo.style.left = cx.toFixed(1) + "px";
      halo.style.top = cy.toFixed(1) + "px";
      if (Math.abs(tx - cx) > 0.5 || Math.abs(ty - cy) > 0.5) { raf = requestAnimationFrame(tick); }
      else { raf = null; }
    }
    window.addEventListener("pointermove", function (e) {
      tx = e.clientX; ty = e.clientY;
      if (!shown) { shown = true; halo.classList.add("on"); }
      if (!raf) raf = requestAnimationFrame(tick);
    }, { passive: true });
    document.addEventListener("mouseleave", function () { halo.classList.remove("on"); });
    document.addEventListener("mouseenter", function () { if (shown) halo.classList.add("on"); });
  }

  /* ---------- Hero : faisceaux de lumière animés (canvas, couleurs marque) ----------
     Adaptation vanilla de l'effet "beams" : faisceaux bleu nuit + or, en
     mix-blend multiply -> teintent le hero clair comme une lumière de vitrail.
     Perf : DPR plafonné, ne tourne que si le hero est visible, pause onglet caché.
     reduced-motion : une seule frame statique (aurore figée), aucune boucle.
  ------------------------------------------------------------------------------- */
  // Beams = canvas avec blur(34px) par frame (coûteux). Réservé au desktop : sur mobile
  // (et en data-saver), le hero garde sa vidéo/photo + sparkles + grille → fluidité préservée.
  var beamCanvas = document.querySelector(".hero-beams");
  if (beamCanvas && !isMobile && !saveData) {
    var heroEl = beamCanvas.closest(".hero") || beamCanvas.parentElement;
    var bctx = beamCanvas.getContext("2d");
    var beams = [];
    var braf = null;
    var DPRb = 0.5; // faisceaux très flous (flou GPU en CSS) -> rendu 0.5x puis étiré : 4x moins de pixels à dessiner ET à flouter, invisible à l'œil
    // Hero NUIT (page Bijouterie) : faisceaux plus nombreux & lumineux (blend screen).
    var night = heroEl.classList.contains("hero-night");

    function mkBeam(w, h) {
      var gold = Math.random() < (night ? 0.5 : 0.42);
      return {
        x: Math.random() * w,
        y: Math.random() * h * 1.3,
        w: (night ? 50 : 40) + Math.random() * (night ? 80 : 70),
        len: h * 1.6,
        angle: -32 + Math.random() * 8,
        speed: (night ? 0.4 : 0.25) + Math.random() * (night ? 0.6 : 0.5),
        op: (night ? 0.14 : 0.08) + Math.random() * (night ? 0.16 : 0.13),
        hue: gold ? 40 + Math.random() * 8 : 212 + Math.random() * 14,
        sat: gold ? 72 : 66,
        light: gold ? (night ? 62 : 56) : (night ? 64 : 58),
        pulse: Math.random() * Math.PI * 2,
        pulseSpeed: 0.012 + Math.random() * 0.02
      };
    }
    function sizeBeams() {
      var r = heroEl.getBoundingClientRect();
      var w = Math.max(1, r.width), h = Math.max(1, r.height);
      beamCanvas.width = Math.round(w * DPRb);
      beamCanvas.height = Math.round(h * DPRb);
      beamCanvas.style.width = w + "px";
      beamCanvas.style.height = h + "px";
      bctx.setTransform(DPRb, 0, 0, DPRb, 0, 0);
      var n = window.innerWidth < 760 ? (night ? 12 : 9) : (night ? 20 : 15);
      beams = [];
      for (var i = 0; i < n; i++) beams.push(mkBeam(w, h));
    }
    function drawBeam(b) {
      bctx.save();
      bctx.translate(b.x, b.y);
      bctx.rotate(b.angle * Math.PI / 180);
      var op = b.op * (0.7 + Math.sin(b.pulse) * 0.3);
      var c = "hsla(" + b.hue + "," + b.sat + "%," + b.light + "%,";
      var g = bctx.createLinearGradient(0, 0, 0, b.len);
      g.addColorStop(0, c + "0)");
      g.addColorStop(0.15, c + (op * 0.5) + ")");
      g.addColorStop(0.5, c + op + ")");
      g.addColorStop(0.85, c + (op * 0.5) + ")");
      g.addColorStop(1, c + "0)");
      bctx.fillStyle = g;
      bctx.fillRect(-b.w / 2, 0, b.w, b.len);
      bctx.restore();
    }
    function renderBeams() {
      var w = beamCanvas.width / DPRb, h = beamCanvas.height / DPRb;
      bctx.clearRect(0, 0, w, h);
      // Flou déplacé en CSS (filter:blur sur le canvas) = GPU, 1x par composite,
      // au lieu de bctx.filter=blur par frame (CPU, ruinait le FPS sur PC : ~9fps).
      for (var i = 0; i < beams.length; i++) {
        var b = beams[i];
        b.y -= b.speed; b.pulse += b.pulseSpeed;
        if (b.y + b.len < -80) { beams[i] = mkBeam(w, h); beams[i].y = h + 80; }
        drawBeam(beams[i]);
      }
    }
    sizeBeams();
    if (reduce) {
      renderBeams(); // aurore figée, pas de boucle
    } else {
      var bRunning = false, bInView = true, bHidden = false;
      function bLoop() { renderBeams(); braf = requestAnimationFrame(bLoop); }
      function bSync() {
        if (bInView && !bHidden) { if (!bRunning) { bRunning = true; bLoop(); } }
        else { bRunning = false; if (braf) cancelAnimationFrame(braf); braf = null; }
      }
      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (es) {
          es.forEach(function (e) { bInView = e.isIntersecting; });
          bSync();
        }, { threshold: 0 }).observe(heroEl);
      }
      document.addEventListener("visibilitychange", function () { bHidden = document.hidden; bSync(); });
      var bRz;
      window.addEventListener("resize", function () { clearTimeout(bRz); bRz = setTimeout(sizeBeams, 200); }, { passive: true });
      bSync();
    }
  }

  /* ---------- Nav : état scrollé + burger ---------- */
  var nav = document.querySelector(".nav");
  var links = document.querySelector(".nav-links");
  var burger = document.querySelector(".burger");

  function onScroll() {
    if (!nav) return;
    nav.classList.toggle("scrolled", window.scrollY > 24);
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  if (burger && links) {
    burger.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
    links.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        links.classList.remove("open");
        burger.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---------- Reveal on scroll ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if (reduce || !("IntersectionObserver" in window)) {
    reveals.forEach(function (el) { el.classList.add("in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
    reveals.forEach(function (el) { io.observe(el); });
    // Filet de sécurité : si l'IO ne se déclenche pas (rendu headless, onglet caché,
    // crawler), révéler au load ce qui est déjà au-dessus/dans le viewport → jamais de
    // section blanche. Le scroll-reveal des sections plus bas reste géré par l'IO.
    window.addEventListener("load", function () {
      setTimeout(function () {
        document.querySelectorAll(".reveal:not(.in)").forEach(function (el) {
          if (el.getBoundingClientRect().top < window.innerHeight * 1.15) el.classList.add("in");
        });
      }, 500);
    });
  }

  /* ---------- Horaires : surligner le jour courant ---------- */
  var hours = document.querySelector("[data-hours]");
  if (hours) {
    var today = new Date().getDay(); // 0=dim … 6=sam
    hours.querySelectorAll(".h").forEach(function (row) {
      var days = (row.getAttribute("data-day") || "").split(/\s+/);
      if (days.indexOf(String(today)) !== -1) row.classList.add("today");
    });
  }

  /* ---------- Galerie : masonry + filtre + collections + reveal ---------- */
  var gfilter = document.querySelector(".gfilter");
  var gallery = document.querySelector(".gallery");
  var tiles = Array.prototype.slice.call(document.querySelectorAll(".gitem"));
  var ROW = 8, GAP = 16; // doivent matcher grid-auto-rows / gap du CSS
  var mosaic = !!(gallery && gallery.classList.contains("mosaic")); // mosaïque éditoriale = tailles via CSS (pas de masonry JS)

  function spanTile(t) {
    if (mosaic) return; // les spans sont gérés par le CSS bento
    if (t.classList.contains("hide")) return;
    var img = t.querySelector("img");
    if (!img) return;
    var h = img.getBoundingClientRect().height;
    if (!h) return;
    var rows = Math.ceil((h + GAP) / (ROW + GAP));
    t.style.gridRowEnd = "span " + rows;
  }
  function layout() { tiles.forEach(spanTile); }

  if (gallery) {
    // légende au survol (générée depuis data-cap)
    tiles.forEach(function (t) {
      var cap = t.getAttribute("data-cap");
      if (cap && !t.querySelector(".cap")) {
        var el = document.createElement("span");
        el.className = "cap";
        el.innerHTML = "<b></b>";
        el.firstChild.textContent = cap;
        t.appendChild(el);
      }
    });
    // (re)calcul des hauteurs masonry
    tiles.forEach(function (t) {
      var img = t.querySelector("img");
      if (img) {
        if (img.complete) spanTile(t);
        img.addEventListener("load", function () { spanTile(t); });
      }
    });
    window.addEventListener("load", layout);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(layout);
    var rT;
    window.addEventListener("resize", function () { clearTimeout(rT); rT = setTimeout(layout, 150); }, { passive: true });

    // apparition échelonnée (quand la galerie entre dans le viewport)
    function revealVisible() {
      var i = 0;
      tiles.forEach(function (t) {
        if (t.classList.contains("hide") || t.classList.contains("in")) return;
        t.style.transitionDelay = Math.min(i * 45, 480) + "ms";
        t.classList.add("in");
        i++;
      });
      setTimeout(function () { tiles.forEach(function (t) { t.style.transitionDelay = ""; }); }, 900);
    }
    if (reduce || !("IntersectionObserver" in window)) {
      tiles.forEach(function (t) { t.classList.add("in"); });
    } else {
      var gio = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { revealVisible(); gio.disconnect(); } });
      }, { threshold: 0.06 });
      gio.observe(gallery);
    }

    // filtre commun (pills + collections)
    window.applyGalleryFilter = function (cat, doScroll) {
      if (gfilter) gfilter.querySelectorAll("button").forEach(function (x) {
        x.classList.toggle("active", x.getAttribute("data-cat") === cat);
      });
      tiles.forEach(function (t) {
        t.classList.toggle("hide", cat !== "all" && t.getAttribute("data-cat") !== cat);
      });
      layout();
      tiles.forEach(function (t) { if (!t.classList.contains("hide")) t.classList.add("in"); });
      if (doScroll && gallery) {
        var y = gallery.getBoundingClientRect().top + window.scrollY - 90;
        window.scrollTo({ top: y, behavior: reduce ? "auto" : "smooth" });
      }
    };

    if (gfilter) gfilter.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (b) window.applyGalleryFilter(b.getAttribute("data-cat"), false);
    });

    // cartes Collections -> filtre + scroll vers la galerie
    document.querySelectorAll("[data-coll]").forEach(function (c) {
      c.addEventListener("click", function (e) {
        e.preventDefault();
        window.applyGalleryFilter(c.getAttribute("data-coll"), true);
      });
    });
  }

  /* ---------- Galerie : lightbox (navigue dans les visibles) ---------- */
  var lb = document.querySelector(".lb");
  if (lb && tiles.length) {
    var stage = lb.querySelector(".stage");
    var cap = lb.querySelector(".lb-cap") || lb.querySelector("figcaption");
    var order = lb.querySelector(".lb-order");
    var current = 0;

    function visible() {
      return tiles.filter(function (t) { return !t.classList.contains("hide"); });
    }
    function render(i) {
      var vis = visible();
      if (!vis.length) return;
      current = (i + vis.length) % vis.length;
      var src = vis[current];
      var img = src.querySelector("img");
      stage.innerHTML = "";
      if (img) {
        var big = new Image();
        big.src = img.currentSrc || img.src;
        big.alt = img.alt || "";
        stage.appendChild(big);
      } else if (src.querySelector(".ph")) {
        stage.innerHTML = src.querySelector(".ph").outerHTML;
      }
      var capText = src.getAttribute("data-cap") || "";
      cap.textContent = capText;
      if (order) {
        var msg = "Bonjour Saeir Thiam Bijouterie, je suis intéressé(e) par ce modèle";
        if (capText) msg += " : " + capText;
        msg += ". Pouvez-vous me renseigner ?";
        order.href = "https://wa.me/2290197967671?text=" + encodeURIComponent(msg);
      }
    }
    function openTile(tile) {
      var vis = visible();
      var i = vis.indexOf(tile);
      render(i < 0 ? 0 : i);
      lb.classList.add("open");
      lb.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
      lb.querySelector(".lb-close").focus();
    }
    function close() {
      lb.classList.remove("open");
      lb.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
    }
    tiles.forEach(function (it) {
      it.setAttribute("tabindex", "0");
      it.setAttribute("role", "button");
      it.addEventListener("click", function () { openTile(it); });
      it.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openTile(it); }
      });
    });
    lb.querySelector(".lb-close").addEventListener("click", close);
    lb.querySelector(".lb-prev").addEventListener("click", function () { render(current - 1); });
    lb.querySelector(".lb-next").addEventListener("click", function () { render(current + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    document.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") render(current - 1);
      if (e.key === "ArrowRight") render(current + 1);
    });
  }

  /* ---------- Ambiance audio : boucle jazz (mp3). Preload en sourdine + activation du son au 1er contact ---------- */
  var audioBtn = document.querySelector(".fab-audio");
  if (audioBtn) {
    var jazz = new Audio("assets/audio/jazz-loop.mp3?v=20260720b");
    jazz.loop = true; jazz.preload = "auto"; jazz.setAttribute("playsinline", "");
    var AUD_TGT = isMobile ? 0.34 : 0.26, audUnlocked = false, audMuted = false, audRaf = 0;
    try { audMuted = localStorage.getItem("djt:audio") === "muted"; } catch (e) {}

    function audFade(v, ms) {
      cancelAnimationFrame(audRaf);
      var s = jazz.volume || 0, t0 = performance.now();
      (function st(t) {
        var p = Math.min((t - t0) / ms, 1), e = 1 - Math.pow(1 - p, 3);
        try { jazz.volume = s + (v - s) * e; } catch (x) {}
        if (p < 1) audRaf = requestAnimationFrame(st);
      })(t0);
    }
    function paintOn() { audioBtn.classList.add("playing"); audioBtn.setAttribute("aria-pressed", "true"); }
    function paintOff() { audioBtn.classList.remove("playing"); audioBtn.setAttribute("aria-pressed", "false"); }

    // 1) demarre TOUT DE SUITE en sourdine (autorise partout) => la piste tourne, bufferisee, prete a etre revelee sans delai
    jazz.muted = true; jazz.volume = 0;
    jazz.play().catch(function () {});

    // 2) au 1er contact reel (tap / clic / touche / scroll tactile), on ACTIVE le son instantanement
    var EVTS = ["pointerdown", "touchstart", "keydown", "click"];
    function removeUnlock() { EVTS.forEach(function (ev) { window.removeEventListener(ev, unlock, true); }); }
    function unlock() {
      if (audUnlocked || audMuted) return;
      jazz.muted = false;
      var p = jazz.play();
      if (p && p.then) {
        p.then(function () { audUnlocked = true; paintOn(); audFade(AUD_TGT, 800); removeUnlock(); })
         .catch(function () { jazz.muted = true; jazz.play().catch(function () {}); });
      } else { audUnlocked = true; paintOn(); audFade(AUD_TGT, 800); removeUnlock(); }
    }
    EVTS.forEach(function (ev) { window.addEventListener(ev, unlock, { passive: true, capture: true }); });

    // 3) bouton : couper / remettre
    audioBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      if (jazz.muted || jazz.paused || jazz.volume < 0.01) {
        audMuted = false; audUnlocked = true;
        try { localStorage.setItem("djt:audio", "playing"); } catch (x) {}
        jazz.muted = false; jazz.play().catch(function () {}); paintOn(); audFade(AUD_TGT, 700);
      } else {
        audMuted = true;
        try { localStorage.setItem("djt:audio", "muted"); } catch (x) {}
        audFade(0, 500); paintOff();
        setTimeout(function () { if (audMuted) jazz.muted = true; }, 520);
      }
    });
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) { if (!jazz.paused) jazz.pause(); }
      else if (audUnlocked && !audMuted) jazz.play().catch(function () {});
    });
  }


  /* ---------- Barre de progression de lecture ----------
     Animée par CSS scroll-driven (animation-timeline). Si non supporté,
     repli léger : on pilote --p en JS (rAF passif). Aucun effet sans scroll. */
  (function () {
    var bar = document.createElement("div");
    bar.className = "scroll-progress";
    bar.setAttribute("aria-hidden", "true");
    document.body.appendChild(bar);
    var supportsSDA = CSS && CSS.supports && CSS.supports("animation-timeline: scroll()");
    if (supportsSDA || reduce) return; // CSS s'en occupe (ou rien si reduced-motion)
    var ticking = false;
    function upd() {
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      bar.style.transform = "scaleX(" + (max > 0 ? (h.scrollTop / max) : 0).toFixed(4) + ")";
      ticking = false;
    }
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; requestAnimationFrame(upd); }
    }, { passive: true });
    upd();
  })();

  /* ---------- Vidéos de fond (volet « commander » + hero « Bientôt ») ----------
     Autoplay fiable : muted/playsinline forcés EN JS (l'attribut seul ne suffit pas sur
     certains navigateurs) + play() relancé (au load, à la visibilité, au 1er tap).
     Pause hors-écran (économie) ; reduced-motion = figé sur le poster. */
  var bgVids = document.querySelectorAll("video.cta-media, video.soon-media, video.hero-media");
  bgVids.forEach(function (vid) {
    vid.muted = true; vid.defaultMuted = true; vid.playsInline = true;
    vid.setAttribute("muted", ""); vid.setAttribute("playsinline", "");
    if (reduce) { vid.removeAttribute("autoplay"); try { vid.pause(); } catch (e) {} return; }

    var wantPlay = true;
    function tryPlay() {
      if (!wantPlay) return;
      var p = vid.play();
      if (p && p.catch) p.catch(function () {
        // autoplay refusé : réessaie au 1er geste utilisateur
        var once = function () { vid.play().catch(function () {}); document.removeEventListener("pointerdown", once); document.removeEventListener("touchstart", once); };
        document.addEventListener("pointerdown", once, { once: true, passive: true });
        document.addEventListener("touchstart", once, { once: true, passive: true });
      });
    }
    // lance dès que des données sont prêtes
    if (vid.readyState >= 2) tryPlay();
    vid.addEventListener("loadeddata", tryPlay);
    vid.addEventListener("canplay", tryPlay);
    try { vid.load(); } catch (e) {}

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          wantPlay = e.isIntersecting;
          if (e.isIntersecting) tryPlay(); else { try { vid.pause(); } catch (x) {} }
        });
      }, { threshold: 0.01 }).observe(vid);
    } else { tryPlay(); }
  });

  /* ---------- Formulaire de devis -> message WhatsApp pré-rempli ---------- */
  var devisForm = document.querySelector("#devis-form");
  if (devisForm) {
    var WA = "2290197967671";
    function fieldOf(name) { var el = devisForm.querySelector('[name="' + name + '"]'); return el ? el.closest(".field") : null; }
    function val(name) {
      var els = devisForm.querySelectorAll('[name="' + name + '"]');
      if (!els.length) return "";
      if (els[0].type === "radio") { var c = devisForm.querySelector('[name="' + name + '"]:checked'); return c ? c.value : ""; }
      return (els[0].value || "").trim();
    }
    // Taille de bague : visible seulement pour Bague / Alliance.
    var ringField = devisForm.querySelector(".field-ring");
    function syncRing() { var b = val("bijou"); if (ringField) ringField.hidden = !(b === "Bague" || b === "Alliance"); }
    devisForm.querySelectorAll('[name="bijou"]').forEach(function (r) { r.addEventListener("change", syncRing); });
    syncRing();

    var errBox = devisForm.querySelector(".form-error");
    devisForm.addEventListener("submit", function (e) {
      e.preventDefault();
      devisForm.querySelectorAll(".field.invalid").forEach(function (f) { f.classList.remove("invalid"); });
      var req = ["prenom", "nom", "tel", "service", "bijou"], bad = null;
      req.forEach(function (n) {
        if (!val(n)) { var f = fieldOf(n); if (f) { f.classList.add("invalid"); if (!bad) bad = f; } }
      });
      if (bad) {
        if (errBox) errBox.hidden = false;
        bad.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
        var fo = bad.querySelector("input.inp, textarea.inp, input[type=radio]");
        if (fo && fo.focus) { try { fo.focus({ preventScroll: true }); } catch (_) { fo.focus(); } }
        return;
      }
      if (errBox) errBox.hidden = true;

      var L = [];
      L.push("Bonjour Saeir Thiam Bijouterie, voici ma demande de devis :");
      L.push("");
      L.push("Client : " + val("prenom") + " " + val("nom"));
      L.push("Numéro : " + val("tel"));
      if (val("indication")) L.push("Quartier : " + val("indication"));
      if (val("premiere")) L.push("Première visite en bijouterie : " + val("premiere"));
      L.push("");
      L.push("Service : " + val("service"));
      L.push("Bijou : " + val("bijou"));
      if (val("matiere")) L.push("Matière : " + val("matiere"));
      if (val("modele")) L.push("Modèle de référence : " + val("modele"));
      if (ringField && !ringField.hidden && val("taille")) L.push("Taille (bague) : " + val("taille"));
      if (val("motif")) L.push("Motif / idée : " + val("motif"));
      if (val("gravure")) L.push("Gravure : " + val("gravure"));
      if (val("occasion")) L.push("Occasion / échéance : " + val("occasion"));
      L.push("");
      L.push("(Envoyé depuis le site Djambar Team)");

      var url = "https://wa.me/" + WA + "?text=" + encodeURIComponent(L.join("\n"));
      var w = window.open(url, "_blank", "noopener");
      if (!w) window.location.href = url;
    });
  }

  /* ---------- Boutons aimantés + tilt des cartes (desktop fin uniquement) ---------- */
  var fine = window.matchMedia("(hover:hover) and (pointer:fine)").matches;
  if (fine && !reduce) {
    // CTA aimantés : le bouton suit légèrement le curseur
    document.querySelectorAll(".btn-lg.btn-gold, .btn-lg.btn-wa").forEach(function (b) {
      var r = null;
      b.addEventListener("pointerenter", function () { r = b.getBoundingClientRect(); });
      b.addEventListener("pointermove", function (e) {
        if (!r) r = b.getBoundingClientRect();
        var mx = e.clientX - (r.left + r.width / 2), my = e.clientY - (r.top + r.height / 2);
        b.style.transform = "translate(" + (mx * 0.18).toFixed(1) + "px," + (my * 0.3 - 2).toFixed(1) + "px)";
      });
      b.addEventListener("pointerleave", function () { r = null; b.style.transform = ""; });
    });
    // Tilt 3D subtil sur les cartes pôles + collections
    document.querySelectorAll(".pole, .coll").forEach(function (c) {
      var r = null;
      c.addEventListener("pointerenter", function () {
        r = c.getBoundingClientRect();
        c.style.transition = "transform .14s var(--ease-quart)";
      });
      c.addEventListener("pointermove", function (e) {
        if (!r) r = c.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5, py = (e.clientY - r.top) / r.height - 0.5;
        c.style.transform = "perspective(900px) rotateX(" + (-py * 4).toFixed(2) + "deg) rotateY(" + (px * 5).toFixed(2) + "deg) translateY(-6px)";
      });
      c.addEventListener("pointerleave", function () { r = null; c.style.transition = ""; c.style.transform = ""; });
    });
  }

  /* ---------- V18 · AVIS : étoiles d'or qui se remplissent en séquence ----------
     PE : sans anim les étoiles sont pleines. On pose .stars-anim (état creux)
     puis on allume .lit une à une à l'entrée. */
  (function () {
    var quotes = Array.prototype.slice.call(document.querySelectorAll(".sec-voices .quote"));
    if (!quotes.length) return;
    function fill(q) {
      var stars = q.querySelector(".stars");
      if (!stars || stars.dataset.done) return;
      stars.dataset.done = "1";
      var svgs = stars.querySelectorAll("svg");
      if (reduce) { svgs.forEach(function (s) { s.classList.add("lit"); }); return; }
      stars.classList.add("stars-anim");
      svgs.forEach(function (s, i) { setTimeout(function () { s.classList.add("lit"); }, 140 + i * 110); });
    }
    if (reduce || !("IntersectionObserver" in window)) { quotes.forEach(fill); return; }
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { fill(e.target); io.unobserve(e.target); } });
    }, { threshold: 0.4 });
    quotes.forEach(function (q) { io.observe(q); });
  })();

  /* ---------- V18 · CTA : poussière d'or à l'entrée (bornée, GPU) ---------- */
  (function () {
    var cta = document.querySelector(".sec-celebrate");
    if (!cta || reduce) return;
    var box = cta.querySelector(".goldfall");
    if (!box) return;
    function burst() {
      if (cta.dataset.done) return;
      cta.dataset.done = "1";
      var n = window.innerWidth < 760 ? 14 : 22;
      for (var i = 0; i < n; i++) {
        var d = document.createElement("i");
        d.className = "gd";
        d.style.left = (Math.random() * 100) + "%";
        var sz = (4 + Math.random() * 5).toFixed(1);
        d.style.width = d.style.height = sz + "px";
        d.style.setProperty("--d", (2.4 + Math.random() * 1.8).toFixed(2) + "s");
        d.style.setProperty("--delay", (Math.random() * 0.7).toFixed(2) + "s");
        box.appendChild(d);
      }
      cta.classList.add("go");
      setTimeout(function () { box.innerHTML = ""; cta.classList.remove("go"); cta.dataset.done = ""; }, 5200);
    }
    if (!("IntersectionObserver" in window)) return;
    var cio = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { burst(); } });
    }, { threshold: 0.5 });
    cio.observe(cta);
  })();

  /* ---------- V18 · PÔLE COMMUNICATION : barres d'égaliseur (studio) ---------- */
  (function () {
    if (!document.body.classList.contains("pole-comm")) return;
    var wave = document.querySelector(".eqwave");
    if (!wave) return;
    var n = window.innerWidth < 760 ? 22 : 40;
    for (var i = 0; i < n; i++) {
      var b = document.createElement("i");
      b.style.setProperty("--h", (35 + Math.random() * 60).toFixed(0) + "%");
      b.style.animationDelay = (Math.random() * 1.8).toFixed(2) + "s";
      b.style.animationDuration = (1.3 + Math.random() * 1.1).toFixed(2) + "s";
      wave.appendChild(b);
    }
  })();

  /* ---------- V18 · PÔLE ÉVÉNEMENTIEL : guirlande d'ampoules (showbiz) ---------- */
  (function () {
    if (!document.body.classList.contains("pole-event")) return;
    var bulbs = document.querySelector(".bulbs");
    if (!bulbs) return;
    var n = window.innerWidth < 760 ? 12 : 22;
    for (var i = 0; i < n; i++) {
      var b = document.createElement("i");
      b.style.animationDelay = (i * 0.12).toFixed(2) + "s";
      bulbs.appendChild(b);
    }
  })();

  /* ---------- V19 · Barre CTA collante (mobile) : Devis WhatsApp + Appeler ---------- */
  (function () {
    if (document.querySelector(".mcta")) return;
    var WA = "https://wa.me/2290197967671?text=" + encodeURIComponent("Bonjour Djambar Team, je souhaite un devis pour un bijou.");
    var bar = document.createElement("div");
    bar.className = "mcta";
    bar.setAttribute("aria-label", "Actions rapides");
    bar.innerHTML =
      '<a class="m-wa" href="' + WA + '" target="_blank" rel="noopener">' +
        '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15l-1.3 4.8 4.9-1.3A10 10 0 1 0 12 2zm0 18a8 8 0 0 1-4.1-1.1l-.3-.2-2.9.8.8-2.8-.2-.3A8 8 0 1 1 12 20zm4.4-6c-.2-.1-1.4-.7-1.6-.8s-.4-.1-.5.1-.6.8-.8 1-.3.2-.5.1a6.5 6.5 0 0 1-3.2-2.8c-.2-.4.2-.4.6-1.2v-.4l-.7-1.7c-.2-.5-.4-.4-.5-.4h-.5a.9.9 0 0 0-.7.3 2.8 2.8 0 0 0-.9 2.1 4.9 4.9 0 0 0 1 2.6 11 11 0 0 0 4.3 3.8c1.6.6 1.9.5 2.6.5a2.4 2.4 0 0 0 1.6-1.1 2 2 0 0 0 .1-1.1c-.1-.1-.3-.2-.5-.3z"/></svg>' +
        'Devis WhatsApp</a>' +
      '<a class="m-call" href="tel:+2290197967671">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3.1-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.7a2 2 0 0 1-.5 2.1L8 9.6a16 16 0 0 0 6 6l1.1-1.1a2 2 0 0 1 2.1-.5c.9.3 1.8.5 2.7.6a2 2 0 0 1 1.7 2z"/></svg>' +
        'Appeler</a>';
    document.body.appendChild(bar);
    document.body.classList.add("has-mcta");
  })();
})();

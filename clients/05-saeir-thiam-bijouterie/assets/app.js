/* ============================================================
   DJAMBAR TEAM — Comportements partagés
   Nav · reveal · galerie filtrable + lightbox · ambiance audio
   Progressive enhancement : si JS off, le contenu reste lisible.
   ============================================================ */
(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isMobile = window.matchMedia("(max-width: 760px)").matches;

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
  var beamCanvas = document.querySelector(".hero-beams");
  if (beamCanvas) {
    var heroEl = beamCanvas.closest(".hero") || beamCanvas.parentElement;
    var bctx = beamCanvas.getContext("2d");
    var beams = [];
    var braf = null;
    var DPRb = Math.min(window.devicePixelRatio || 1, 2);
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
      var n = window.innerWidth < 760 ? (night ? 16 : 12) : (night ? 30 : 22);
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
      bctx.filter = "blur(" + (night ? 34 : 30) + "px)";
      for (var i = 0; i < beams.length; i++) {
        var b = beams[i];
        b.y -= b.speed; b.pulse += b.pulseSpeed;
        if (b.y + b.len < -80) { beams[i] = mkBeam(w, h); beams[i].y = h + 80; }
        drawBeam(beams[i]);
      }
      bctx.filter = "none";
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

  function spanTile(t) {
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
    var cap = lb.querySelector("figcaption");
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
      cap.textContent = src.getAttribute("data-cap") || "";
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

  /* ---------- Ambiance audio (placeholder procédural) ----------
     Baseline mobile NEBULA : déblocage iOS (silent buffer) +
     DynamicsCompressor + gain modéré boosté mobile, fondu sans clic.
     -> Remplaçable par la piste libre de droits du client :
        poser <audio data-ambiance src="..."> et ce bloc l'utilisera.
  ------------------------------------------------------------------ */
  var audioBtn = document.querySelector(".fab-audio");
  if (audioBtn) {
    var ctx = null, master = null, nodes = [], playing = false;
    var fileEl = document.querySelector("[data-ambiance]");
    var TARGET = isMobile ? 0.17 : 0.13;

    function unlock() {
      var b = ctx.createBuffer(1, 1, 22050);
      var s = ctx.createBufferSource(); s.buffer = b;
      s.connect(ctx.destination); s.start(0);
    }
    function buildPad() {
      var comp = ctx.createDynamicsCompressor();
      comp.threshold.value = -24; comp.knee.value = 28; comp.ratio.value = 12;
      comp.attack.value = 0.01; comp.release.value = 0.28;
      var lp = ctx.createBiquadFilter(); lp.type = "lowpass";
      lp.frequency.value = 1350; lp.Q.value = 0.6;
      lp.connect(comp); comp.connect(master);
      var freqs = [146.83, 220.0, 277.18, 329.63, 415.30];
      freqs.forEach(function (f, i) {
        var o = ctx.createOscillator();
        o.type = i % 2 ? "sine" : "triangle";
        o.frequency.value = f; o.detune.value = (i - 2) * 4;
        var g = ctx.createGain(); g.gain.value = i === 0 ? 0.5 : 0.26;
        var lfo = ctx.createOscillator(); lfo.frequency.value = 0.05 + i * 0.013;
        var lfoG = ctx.createGain(); lfoG.gain.value = 0.10;
        lfo.connect(lfoG); lfoG.connect(g.gain);
        o.connect(g); g.connect(lp);
        o.start(); lfo.start();
        nodes.push(o, lfo);
      });
    }
    function fade(to, t) {
      if (!master) return;
      var now = ctx.currentTime;
      master.gain.cancelScheduledValues(now);
      master.gain.setValueAtTime(master.gain.value, now);
      master.gain.linearRampToValueAtTime(to, now + t);
    }
    function start() {
      if (!ctx) {
        ctx = new (window.AudioContext || window.webkitAudioContext)();
        unlock();
        master = ctx.createGain(); master.gain.value = 0.0001;
        master.connect(ctx.destination);
        if (fileEl) {
          fileEl.loop = true;
          var src = ctx.createMediaElementSource(fileEl);
          var comp = ctx.createDynamicsCompressor();
          src.connect(comp); comp.connect(master);
          fileEl.play().catch(function () {});
        } else { buildPad(); }
      }
      if (ctx.state === "suspended") ctx.resume();
      fade(TARGET, 1.2);
      playing = true;
      audioBtn.classList.add("playing");
      audioBtn.setAttribute("aria-pressed", "true");
    }
    function stop() {
      fade(0.0001, 0.6);
      playing = false;
      audioBtn.classList.remove("playing");
      audioBtn.setAttribute("aria-pressed", "false");
      setTimeout(function () { if (!playing && ctx && ctx.state === "running") ctx.suspend(); }, 700);
    }
    audioBtn.addEventListener("click", function () { playing ? stop() : start(); });
    document.addEventListener("visibilitychange", function () {
      if (document.hidden && playing) stop();
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

  /* ---------- Vidéo de fond du volet « commander » : pause hors-écran + reduced-motion ---------- */
  var ctaVid = document.querySelector("video.cta-media");
  if (ctaVid) {
    if (reduce) {
      ctaVid.removeAttribute("autoplay");
      ctaVid.pause();
    } else if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting) { var p = ctaVid.play(); if (p && p.catch) p.catch(function () {}); }
          else ctaVid.pause();
        });
      }, { threshold: 0.12 }).observe(ctaVid);
    }
  }

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
})();

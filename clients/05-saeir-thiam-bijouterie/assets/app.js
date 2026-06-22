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

  /* ---------- Galerie : filtre par catégorie ---------- */
  var gfilter = document.querySelector(".gfilter");
  var tiles = Array.prototype.slice.call(document.querySelectorAll(".gitem"));
  if (gfilter) {
    gfilter.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b) return;
      gfilter.querySelectorAll("button").forEach(function (x) { x.classList.remove("active"); });
      b.classList.add("active");
      var cat = b.getAttribute("data-cat");
      tiles.forEach(function (t) {
        t.classList.toggle("hide", cat !== "all" && t.getAttribute("data-cat") !== cat);
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
})();

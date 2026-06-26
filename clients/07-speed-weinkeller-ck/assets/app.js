/* ==========================================================================
   SPEED SHOPPING × WEINKELLER BY CK — comportements partagés (client #07)
   Nav · reveal · vol France→Bénin · filtre+lightbox bouteilles · audio · barre CTA mobile
   Progressive enhancement : sans JS le contenu reste lisible.
   ========================================================================== */
document.documentElement.classList.add("js");
(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isMobile = window.matchMedia("(max-width: 760px)").matches;
  var fine = window.matchMedia("(hover:hover) and (pointer:fine)").matches;
  var saveData = !!(navigator.connection && navigator.connection.saveData);

  /* ---------- Année ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* ---------- Halo curseur (desktop) ---------- */
  if (!reduce && fine && !document.body.classList.contains("splash")) {
    var halo = document.createElement("div");
    halo.className = "halo"; halo.setAttribute("aria-hidden", "true");
    document.body.appendChild(halo);
    var tx = innerWidth / 2, ty = innerHeight * .3, cx = tx, cy = ty, raf = null, shown = false;
    function tick() {
      cx += (tx - cx) * .14; cy += (ty - cy) * .14;
      halo.style.left = cx.toFixed(1) + "px"; halo.style.top = cy.toFixed(1) + "px";
      if (Math.abs(tx - cx) > .5 || Math.abs(ty - cy) > .5) raf = requestAnimationFrame(tick); else raf = null;
    }
    addEventListener("pointermove", function (e) {
      tx = e.clientX; ty = e.clientY;
      if (!shown) { shown = true; halo.classList.add("on"); }
      if (!raf) raf = requestAnimationFrame(tick);
    }, { passive: true });
    document.addEventListener("mouseleave", function () { halo.classList.remove("on"); });
  }

  /* ---------- Nav : scrolled + burger ---------- */
  var nav = document.querySelector(".nav");
  var links = document.querySelector(".nav-links");
  var burger = document.querySelector(".burger");
  function onScroll() { if (nav) nav.classList.toggle("scrolled", scrollY > 24); }
  onScroll(); addEventListener("scroll", onScroll, { passive: true });
  if (burger && links) {
    burger.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
    links.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { links.classList.remove("open"); burger.setAttribute("aria-expanded", "false"); });
    });
  }

  /* ---------- Reveal on scroll ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if (reduce || !("IntersectionObserver" in window)) {
    reveals.forEach(function (el) { el.classList.add("in"); });
  } else {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { threshold: .12, rootMargin: "0px 0px -7% 0px" });
    reveals.forEach(function (el) { io.observe(el); });
    addEventListener("load", function () {
      setTimeout(function () {
        document.querySelectorAll(".reveal:not(.in)").forEach(function (el) {
          if (el.getBoundingClientRect().top < innerHeight * 1.15) el.classList.add("in");
        });
      }, 500);
    });
  }

  /* ---------- Vol France→Bénin (Speed) : déclenche l'animation quand visible ---------- */
  var flight = document.querySelector(".flight");
  if (flight) {
    if (reduce || !("IntersectionObserver" in window)) { flight.classList.add("in"); }
    else {
      new IntersectionObserver(function (es, o) {
        es.forEach(function (e) { if (e.isIntersecting) { flight.classList.add("in"); o.disconnect(); } });
      }, { threshold: .4 }).observe(flight);
    }
  }

  /* ---------- Sélection Weinkeller : filtre + lightbox ---------- */
  var wfilter = document.querySelector(".wein-filter");
  var bottles = Array.prototype.slice.call(document.querySelectorAll(".bottle"));
  if (wfilter && bottles.length) {
    wfilter.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      var cat = b.getAttribute("data-cat");
      wfilter.querySelectorAll("button").forEach(function (x) { x.classList.toggle("active", x === b); });
      bottles.forEach(function (t) {
        var show = cat === "all" || t.getAttribute("data-cat") === cat;
        t.style.display = show ? "" : "none";
      });
    });
  }
  // lightbox (agrandit la silhouette + fiche)
  var lb = document.querySelector(".lb");
  if (lb && bottles.length) {
    var stage = lb.querySelector(".stage"), capEl = lb.querySelector(".lb-cap"), cur = 0;
    function vis() { return bottles.filter(function (t) { return t.style.display !== "none"; }); }
    function render(i) {
      var v = vis(); if (!v.length) return;
      cur = (i + v.length) % v.length;
      var src = v[cur], svg = src.querySelector(".visual svg"), name = src.querySelector("h3");
      stage.innerHTML = svg ? svg.outerHTML : "";
      capEl.textContent = name ? name.textContent : "";
    }
    function open(t) { var v = vis(); render(Math.max(0, v.indexOf(t))); lb.classList.add("open"); lb.setAttribute("aria-hidden", "false"); document.body.style.overflow = "hidden"; lb.querySelector(".lb-close").focus(); }
    function close() { lb.classList.remove("open"); lb.setAttribute("aria-hidden", "true"); document.body.style.overflow = ""; }
    bottles.forEach(function (t) {
      var v = t.querySelector(".visual");
      if (v) { v.style.cursor = "zoom-in"; v.addEventListener("click", function () { open(t); }); }
    });
    lb.querySelector(".lb-close").addEventListener("click", close);
    lb.querySelector(".lb-prev").addEventListener("click", function () { render(cur - 1); });
    lb.querySelector(".lb-next").addEventListener("click", function () { render(cur + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    document.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("open")) return;
      if (e.key === "Escape") close(); if (e.key === "ArrowLeft") render(cur - 1); if (e.key === "ArrowRight") render(cur + 1);
    });
  }

  /* ---------- Barre CTA mobile (injectée) ---------- */
  var waUrl = document.body.getAttribute("data-wa");
  var telNum = document.body.getAttribute("data-tel");
  if (waUrl && !document.body.classList.contains("splash")) {
    var bar = document.createElement("div");
    bar.className = "mcta";
    var label = document.body.getAttribute("data-wa-label") || "Commander";
    var html = '<a class="btn btn-wa" href="' + waUrl + '" target="_blank" rel="noopener">' +
      '<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.2-.7-2.7-1.1-4.4-3.9-4.5-4.1-.1-.2-1-1.4-1-2.6s.6-1.8.9-2.1c.2-.2.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.4.6c-.2.2-.3.4-.1.7.2.3.8 1.3 1.7 2.1 1.2 1 2 1.3 2.3 1.5.2.1.4.1.6-.1l.7-.8c.2-.2.4-.2.6-.1l1.9.9c.3.2.5.3.6.4.1.2.1.6-.1 1.1Z"/></svg>' +
      label + '</a>';
    if (telNum) html += '<a class="btn btn-ghost" href="tel:' + telNum + '">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/></svg>Appeler</a>';
    bar.innerHTML = html;
    document.body.appendChild(bar);
    document.body.classList.add("has-mcta");
  }

  /* ---------- Ambiance audio (procédurale, baseline mobile, OFF par défaut) ---------- */
  var audioBtn = document.querySelector(".fab-audio");
  if (audioBtn) {
    var ctx = null, master = null, nodes = [], playing = false;
    var TARGET = isMobile ? 0.16 : 0.12;
    var dark = document.body.classList.contains("w-wein");
    function unlock() { var b = ctx.createBuffer(1, 1, 22050); var s = ctx.createBufferSource(); s.buffer = b; s.connect(ctx.destination); s.start(0); }
    function buildPad() {
      var comp = ctx.createDynamicsCompressor();
      comp.threshold.value = -24; comp.knee.value = 28; comp.ratio.value = 12; comp.attack.value = .01; comp.release.value = .28;
      var lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = dark ? 1050 : 1500; lp.Q.value = .6;
      lp.connect(comp); comp.connect(master);
      // accords distincts par monde : Weinkeller plus grave/feutré, Speed plus clair
      var freqs = dark ? [110, 164.81, 220, 246.94, 329.63] : [196, 261.63, 329.63, 392, 523.25];
      freqs.forEach(function (f, i) {
        var o = ctx.createOscillator(); o.type = i % 2 ? "sine" : "triangle"; o.frequency.value = f; o.detune.value = (i - 2) * 4;
        var g = ctx.createGain(); g.gain.value = i === 0 ? .5 : .24;
        var lfo = ctx.createOscillator(); lfo.frequency.value = .05 + i * .013;
        var lfoG = ctx.createGain(); lfoG.gain.value = .1; lfo.connect(lfoG); lfoG.connect(g.gain);
        o.connect(g); g.connect(lp); o.start(); lfo.start(); nodes.push(o, lfo);
      });
    }
    function fade(to, t) { if (!master) return; var n = ctx.currentTime; master.gain.cancelScheduledValues(n); master.gain.setValueAtTime(master.gain.value, n); master.gain.linearRampToValueAtTime(to, n + t); }
    function start() {
      if (!ctx) { ctx = new (window.AudioContext || window.webkitAudioContext)(); unlock(); master = ctx.createGain(); master.gain.value = .0001; master.connect(ctx.destination); buildPad(); }
      if (ctx.state === "suspended") ctx.resume();
      fade(TARGET, 1.2); playing = true; audioBtn.classList.add("playing"); audioBtn.setAttribute("aria-pressed", "true");
    }
    function stop() { fade(.0001, .6); playing = false; audioBtn.classList.remove("playing"); audioBtn.setAttribute("aria-pressed", "false"); setTimeout(function () { if (!playing && ctx && ctx.state === "running") ctx.suspend(); }, 700); }
    audioBtn.addEventListener("click", function () { playing ? stop() : start(); });
    document.addEventListener("visibilitychange", function () { if (document.hidden && playing) stop(); });
  }

  /* ---------- Vidéos de fond (si présentes) ---------- */
  document.querySelectorAll("video.hero-media,video.cta-media").forEach(function (vid) {
    vid.muted = true; vid.defaultMuted = true; vid.playsInline = true;
    vid.setAttribute("muted", ""); vid.setAttribute("playsinline", "");
    if (reduce) { vid.removeAttribute("autoplay"); try { vid.pause(); } catch (e) {} return; }
    function tryPlay() { var p = vid.play(); if (p && p.catch) p.catch(function () {
      var once = function () { vid.play().catch(function () {}); document.removeEventListener("pointerdown", once); };
      document.addEventListener("pointerdown", once, { once: true, passive: true });
    }); }
    if (vid.readyState >= 2) tryPlay();
    vid.addEventListener("loadeddata", tryPlay); vid.addEventListener("canplay", tryPlay);
  });

  /* ---------- Boutons aimantés + tilt cartes (desktop fin) ---------- */
  if (fine && !reduce) {
    document.querySelectorAll(".btn-lg").forEach(function (b) {
      var r = null;
      b.addEventListener("pointerenter", function () { r = b.getBoundingClientRect(); });
      b.addEventListener("pointermove", function (e) {
        if (!r) r = b.getBoundingClientRect();
        var mx = e.clientX - (r.left + r.width / 2), my = e.clientY - (r.top + r.height / 2);
        b.style.transform = "translate(" + (mx * .16).toFixed(1) + "px," + (my * .28 - 2).toFixed(1) + "px)";
      });
      b.addEventListener("pointerleave", function () { r = null; b.style.transform = ""; });
    });
    document.querySelectorAll(".cat,.cellar,.bottle").forEach(function (c) {
      var r = null;
      c.addEventListener("pointerenter", function () { r = c.getBoundingClientRect(); c.style.transition = "transform .14s var(--ease)"; });
      c.addEventListener("pointermove", function (e) {
        if (!r) r = c.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - .5, py = (e.clientY - r.top) / r.height - .5;
        c.style.transform = "perspective(900px) rotateX(" + (-py * 3).toFixed(2) + "deg) rotateY(" + (px * 4).toFixed(2) + "deg) translateY(-6px)";
      });
      c.addEventListener("pointerleave", function () { r = null; c.style.transition = ""; c.style.transform = ""; });
    });
  }
})();

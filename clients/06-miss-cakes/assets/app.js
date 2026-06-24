/* ============================================================
   MISS CAKES — Comportements partagés · Pâtisserie artisanale (Cotonou)
   Nav · reveal · galerie filtrable + lightbox · ambiance audio
   · commande WhatsApp pré-remplie · motion fluide (mobile-first)
   Progressive enhancement : sans JS, le contenu reste lisible.
   Socle nebula-site (gold standard Djambar). Bumper ?v= à chaque modif.
   ============================================================ */
(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isMobile = window.matchMedia("(max-width: 760px)").matches;

  /* ---------- WhatsApp (numéro migré 10 chiffres — à CONFIRMER) ---------- */
  var WA = "2290167748955";

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

  /* ---------- Lien de nav actif selon la section visible ---------- */
  var navAnchors = links ? Array.prototype.slice.call(links.querySelectorAll('a[href^="#"]')) : [];
  var sections = navAnchors.map(function (a) {
    var id = a.getAttribute("href").slice(1);
    return id ? document.getElementById(id) : null;
  });
  if (navAnchors.length && "IntersectionObserver" in window) {
    var navIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var i = sections.indexOf(e.target);
        if (i < 0) return;
        navAnchors.forEach(function (a) { a.classList.remove("active"); });
        navAnchors[i].classList.add("active");
      });
    }, { rootMargin: "-45% 0px -50% 0px", threshold: 0 });
    sections.forEach(function (s) { if (s) navIo.observe(s); });
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
    // Filet de sécurité : si l'IO ne se déclenche pas (rendu headless, onglet
    // caché, crawler), révéler au load ce qui est déjà dans le viewport.
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

  /* ---------- Galerie : masonry + filtre + reveal ---------- */
  var gfilter = document.querySelector(".gfilter");
  var gallery = document.querySelector(".gallery");
  var tiles = Array.prototype.slice.call(document.querySelectorAll(".gitem"));
  var ROW = 8, GAP = 16; // doivent matcher grid-auto-rows / gap du CSS

  function spanTile(t) {
    if (t.classList.contains("hide")) return;
    var img = t.querySelector("img");
    if (!img) return; // placeholders .ph -> span par défaut (CSS)
    var h = img.getBoundingClientRect().height;
    if (!h) return;
    var rows = Math.ceil((h + GAP) / (ROW + GAP));
    t.style.gridRowEnd = "span " + rows;
  }
  function layout() { tiles.forEach(spanTile); }

  if (gallery) {
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
        var msg = "Bonjour Miss cakes, ce modèle me plaît";
        if (capText) msg += " : " + capText;
        msg += ". Est-il réalisable sur commande ?";
        order.href = "https://wa.me/" + WA + "?text=" + encodeURIComponent(msg);
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

  /* ---------- Ambiance audio (pad procédural doux, OFF par défaut) ----------
     Baseline mobile NEBULA : déblocage iOS (silent buffer) +
     DynamicsCompressor + gain modéré boosté mobile, fondu sans clic.
     -> Remplaçable par une piste libre de droits du client :
        poser <audio data-ambiance src="..."> et ce bloc l'utilisera.
  ------------------------------------------------------------------ */
  var audioBtn = document.querySelector(".fab-audio");
  if (audioBtn) {
    var ctx = null, master = null, nodes = [], playing = false;
    var fileEl = document.querySelector("[data-ambiance]");
    var TARGET = isMobile ? 0.16 : 0.12;

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
      lp.frequency.value = 1300; lp.Q.value = 0.6;
      lp.connect(comp); comp.connect(master);
      // accord doux et chaleureux (Ré majeur 9)
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
     repli léger : on pilote scaleX en JS (rAF passif). */
  (function () {
    var bar = document.createElement("div");
    bar.className = "scroll-progress";
    bar.setAttribute("aria-hidden", "true");
    document.body.appendChild(bar);
    var supportsSDA = CSS && CSS.supports && CSS.supports("animation-timeline: scroll()");
    if (supportsSDA || reduce) return;
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

  /* ---------- Vidéos de fond éventuelles (autoplay fiable) ---------- */
  var bgVids = document.querySelectorAll("video.cta-media, video.hero-media");
  bgVids.forEach(function (vid) {
    vid.muted = true; vid.defaultMuted = true; vid.playsInline = true;
    vid.setAttribute("muted", ""); vid.setAttribute("playsinline", "");
    if (reduce) { vid.removeAttribute("autoplay"); try { vid.pause(); } catch (e) {} return; }
    var wantPlay = true;
    function tryPlay() {
      if (!wantPlay) return;
      var p = vid.play();
      if (p && p.catch) p.catch(function () {
        var once = function () { vid.play().catch(function () {}); document.removeEventListener("pointerdown", once); document.removeEventListener("touchstart", once); };
        document.addEventListener("pointerdown", once, { once: true, passive: true });
        document.addEventListener("touchstart", once, { once: true, passive: true });
      });
    }
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

  /* ---------- Formulaire de commande -> message WhatsApp pré-rempli ---------- */
  var devisForm = document.querySelector("#devis-form");
  if (devisForm) {
    function fieldOf(name) { var el = devisForm.querySelector('[name="' + name + '"]'); return el ? el.closest(".field") : null; }
    function val(name) {
      var els = devisForm.querySelectorAll('[name="' + name + '"]');
      if (!els.length) return "";
      if (els[0].type === "radio") { var c = devisForm.querySelector('[name="' + name + '"]:checked'); return c ? c.value : ""; }
      return (els[0].value || "").trim();
    }

    var errBox = devisForm.querySelector(".form-error");
    devisForm.addEventListener("submit", function (e) {
      e.preventDefault();
      devisForm.querySelectorAll(".field.invalid").forEach(function (f) { f.classList.remove("invalid"); });
      var req = ["prenom", "tel", "occasion", "type"], bad = null;
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
      L.push("Bonjour Miss cakes, voici ma demande de commande :");
      L.push("");
      L.push("Nom : " + val("prenom") + (val("nom") ? " " + val("nom") : ""));
      L.push("Numéro : " + val("tel"));
      if (val("quartier")) L.push("Quartier (livraison) : " + val("quartier"));
      L.push("");
      L.push("Occasion : " + val("occasion"));
      L.push("Création : " + val("type"));
      if (val("parts")) L.push("Nombre de parts : " + val("parts"));
      if (val("parfum")) L.push("Parfums : " + val("parfum"));
      if (val("date")) L.push("Date souhaitée : " + val("date"));
      if (val("message")) L.push("Message sur le gâteau : " + val("message"));
      if (val("details")) L.push("Mon idée : " + val("details"));
      L.push("");
      L.push("(Envoyé depuis le site Miss cakes)");

      var url = "https://wa.me/" + WA + "?text=" + encodeURIComponent(L.join("\n"));
      var w = window.open(url, "_blank", "noopener");
      if (!w) window.location.href = url;
    });
  }

  /* ---------- Sucre / confettis qui flottent dans le hero (desktop, !reduce) ---------- */
  (function () {
    var field = document.querySelector(".sprinkle-field");
    if (!field || reduce || isMobile) return;
    var cols = ["#E59CA9", "#C76B7C", "#C9925B", "#F6D9DE", "#9C6B33", "#E7C9A3"];
    for (var i = 0; i < 12; i++) {
      var s = document.createElement("i");
      s.className = "spr";
      s.style.left = (6 + Math.random() * 88) + "%";
      s.style.bottom = (-6 + Math.random() * 28) + "%";
      s.style.background = cols[i % cols.length];
      s.style.setProperty("--r", (Math.random() * 180 - 90).toFixed(0) + "deg");
      s.style.setProperty("--d", (7 + Math.random() * 7).toFixed(1) + "s");
      s.style.setProperty("--delay", (Math.random() * 8).toFixed(1) + "s");
      if (Math.random() < 0.4) { s.style.width = "6px"; s.style.height = "6px"; s.style.borderRadius = "50%"; }
      field.appendChild(s);
    }
  })();

  /* ---------- Ripple au clic (boutons & actions) ---------- */
  if (!reduce) {
    document.querySelectorAll(".btn, .order, .lb-order, .form-foot button, .gfilter button").forEach(function (el) {
      el.classList.add("rippleable");
      el.addEventListener("pointerdown", function (e) {
        var r = el.getBoundingClientRect();
        var rip = document.createElement("span");
        rip.className = "ripple";
        var d = Math.max(r.width, r.height) * 1.15;
        rip.style.width = rip.style.height = d + "px";
        rip.style.left = (e.clientX - r.left) + "px";
        rip.style.top = (e.clientY - r.top) + "px";
        el.appendChild(rip);
        setTimeout(function () { rip.remove(); }, 650);
      }, { passive: true });
    });
  }

  /* ---------- Tilt des cartes + CTA aimantés (desktop fin uniquement) ---------- */
  var fine = window.matchMedia("(hover:hover) and (pointer:fine)").matches;
  if (fine && !reduce) {
    document.querySelectorAll(".creation, .coll").forEach(function (c) {
      var r = null;
      c.addEventListener("pointerenter", function () {
        r = c.getBoundingClientRect();
        c.style.transition = "transform .14s var(--ease-quart)";
      });
      c.addEventListener("pointermove", function (e) {
        if (!r) r = c.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5, py = (e.clientY - r.top) / r.height - 0.5;
        c.style.transform = "perspective(900px) rotateX(" + (-py * 3.5).toFixed(2) + "deg) rotateY(" + (px * 4.5).toFixed(2) + "deg) translateY(-6px)";
      });
      c.addEventListener("pointerleave", function () { r = null; c.style.transition = ""; c.style.transform = ""; });
    });
    document.querySelectorAll(".btn-lg.btn-rose, .btn-lg.btn-wa, .btn-lg.btn-gold").forEach(function (b) {
      var r = null;
      b.addEventListener("pointerenter", function () { r = b.getBoundingClientRect(); });
      b.addEventListener("pointermove", function (e) {
        if (!r) r = b.getBoundingClientRect();
        var mx = e.clientX - (r.left + r.width / 2), my = e.clientY - (r.top + r.height / 2);
        b.style.transform = "translate(" + (mx * 0.16).toFixed(1) + "px," + (my * 0.28 - 2).toFixed(1) + "px)";
      });
      b.addEventListener("pointerleave", function () { r = null; b.style.transform = ""; });
    });
  }
})();

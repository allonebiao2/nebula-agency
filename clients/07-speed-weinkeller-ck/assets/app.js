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

  /* ---------- Écran de chargement signature (effacement) ----------
     Le loader s'auto-efface en CSS (sécurité sans JS). Ici on l'efface plus vite
     dès que la page est prête, après un temps mini pour apprécier l'animation. */
  (function () {
    var loader = document.querySelector(".world-loader");
    if (!loader) return;
    var docEl = document.documentElement;
    docEl.style.overflow = "hidden"; // verrou de défilement (JS-only : jamais piégé sans JS)
    var done = false;
    var MIN = reduce ? 0 : 1900;
    var t0 = (window.performance && performance.now) ? performance.now() : Date.now();
    function dismiss() {
      if (done) return; done = true;
      docEl.classList.add("loaded");
      docEl.style.overflow = "";
      setTimeout(function () { if (loader && loader.parentNode) loader.parentNode.removeChild(loader); }, 700);
    }
    function whenReady() {
      var now = (window.performance && performance.now) ? performance.now() : Date.now();
      setTimeout(dismiss, Math.max(0, MIN - (now - t0)));
    }
    if (document.readyState === "complete") whenReady();
    else window.addEventListener("load", whenReady);
    setTimeout(dismiss, 4200); // garde-fou absolu
  })();

  /* ---------- Fiches services Speed (lecture obligatoire avant action) ---------- */
  (function () {
    var sheets = document.querySelectorAll(".svc-sheet");
    if (!sheets.length) return;
    var openSheet = null, lastFocus = null;
    function lockBody(on) { document.documentElement.style.overflow = on ? "hidden" : ""; }
    function progress(sheet) {
      var body = sheet.querySelector(".svc-body"), bar = sheet.querySelector(".svc-progress i");
      var max = body.scrollHeight - body.clientHeight;
      var pct = max <= 4 ? 1 : Math.min(1, body.scrollTop / max);
      if (bar) bar.style.width = (pct * 100).toFixed(1) + "%";
      if (pct >= 0.985 || max <= 4) sheet.classList.add("read"); // déverrouille le CTA
    }
    function open(id) {
      var sheet = document.getElementById("svc-" + id); if (!sheet) return;
      lastFocus = document.activeElement;
      sheet.hidden = false; void sheet.offsetWidth;
      sheet.classList.add("open"); sheet.classList.remove("read");
      openSheet = sheet; lockBody(true);
      var body = sheet.querySelector(".svc-body"), bar = sheet.querySelector(".svc-progress i");
      body.scrollTop = 0; if (bar) bar.style.width = "0%";
      if (!body._svcBound) { body.addEventListener("scroll", function () { progress(sheet); }, { passive: true }); body._svcBound = true; }
      requestAnimationFrame(function () { progress(sheet); try { body.focus({ preventScroll: true }); } catch (e) {} });
    }
    function close() {
      if (!openSheet) return;
      var s = openSheet; openSheet = null;
      s.classList.remove("open"); lockBody(false);
      setTimeout(function () { if (!s.classList.contains("open")) s.hidden = true; }, 420);
      if (lastFocus && lastFocus.focus) try { lastFocus.focus(); } catch (e) {}
    }
    document.querySelectorAll("[data-svc]").forEach(function (btn) {
      btn.addEventListener("click", function (e) { e.preventDefault(); open(btn.getAttribute("data-svc")); });
    });
    sheets.forEach(function (sheet) {
      sheet.querySelectorAll("[data-close]").forEach(function (el) { el.addEventListener("click", close); });
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && openSheet) close(); });
    window.addEventListener("resize", function () { if (openSheet) progress(openSheet); }, { passive: true });
  })();

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
    // Filet de sécurité anti-section-vide : révèle tout ce qui entre dans le viewport
    // (l'IO peut « sauter » un élément lors d'un défilement rapide ou en rendu headless)
    var rvTick = false;
    function revealSafety() {
      rvTick = false;
      var vh = innerHeight;
      document.querySelectorAll(".reveal:not(.in)").forEach(function (el) {
        if (el.getBoundingClientRect().top < vh * 0.92) el.classList.add("in");
      });
    }
    addEventListener("scroll", function () { if (!rvTick) { rvTick = true; requestAnimationFrame(revealSafety); } }, { passive: true });
    addEventListener("load", function () { setTimeout(revealSafety, 400); });
    revealSafety();
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

  /* ---------- Sélection Weinkeller : navigation par catégorie (panneau + accordéon) ---------- */
  var caveNav = document.querySelector("#caveNav");
  var bottles = Array.prototype.slice.call(document.querySelectorAll(".bottle"));
  if (caveNav && bottles.length) {
    var caveHead = document.querySelector("#caveHead");
    var caveScrim = document.querySelector("#caveScrim");
    var caveOpenBtn = document.querySelector("#caveOpen");
    var TAX = [
      { cat: "champagne", short: "Champagnes", label: "Champagnes & Effervescents", subs: [["prestige", "Prestige & Millésimés"], ["blancdeblancs", "Blanc de Blancs"], ["brut", "Bruts"], ["rose", "Rosés"]] },
      { cat: "tequila", short: "Tequila", label: "Tequila", subs: [["cristalino", "Cristalino"], ["blanco", "Blanco / Silver"], ["reposado", "Reposado"], ["anejo", "Añejo"]] }
    ];
    var CHEV = '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>';
    function cnt(c, s) { return bottles.filter(function (b) { return b.getAttribute("data-cat") === c && (!s || b.getAttribute("data-sub") === s); }).length; }
    function isReal(c) { return bottles.some(function (b) { return b.getAttribute("data-cat") === c && !b.classList.contains("is-ph"); }); }
    var labelOf = {}; TAX.forEach(function (f) { labelOf[f.cat] = { label: f.label, subs: f.subs }; });

    // construit l'accordéon
    var html = '<div class="cave-nh">La cave</div>' +
      '<button class="cave-row cave-all active" data-cat="all"><span class="lbl">Toute la cave</span><span class="cave-count">' + bottles.length + '</span></button>';
    TAX.forEach(function (f) {
      html += '<div class="acc-fam' + (isReal(f.cat) ? '' : ' soon') + '" data-cat="' + f.cat + '">' +
        '<button class="cave-row fam" data-cat="' + f.cat + '"><span class="lbl">' + f.short + '</span><span class="cave-count">' + cnt(f.cat) + '</span>' + (f.subs.length ? CHEV : '') + '</button>';
      if (f.subs.length) {
        html += '<div class="acc-sub"><div class="acc-sub-inner">';
        f.subs.forEach(function (s) { html += '<button class="sub-row" data-cat="' + f.cat + '" data-sub="' + s[0] + '"><span class="lbl">' + s[1] + '</span><span class="cave-count">' + cnt(f.cat, s[0]) + '</span></button>'; });
        html += '</div></div>';
      }
      html += '</div>';
    });
    caveNav.innerHTML = html;

    function setHead(cat, sub) {
      if (!caveHead) return;
      if (cat === "all") { caveHead.innerHTML = 'Toute la cave <span class="ch-n">' + bottles.length + ' références</span>'; return; }
      var meta = labelOf[cat] || { label: "", subs: [] }, lbl = meta.label;
      if (sub) { var sm = meta.subs.filter(function (s) { return s[0] === sub; })[0]; if (sm) lbl += ' · ' + sm[1]; }
      var n = cnt(cat, sub);
      caveHead.innerHTML = lbl + ' <span class="ch-n">' + n + (n > 1 ? ' bouteilles' : ' bouteille') + '</span>' + (isReal(cat) ? '' : ' <span class="ch-soon">à venir</span>');
    }
    function filterCave(cat, sub) {
      var vi = 0;
      bottles.forEach(function (t) {
        var show = cat === "all" || (t.getAttribute("data-cat") === cat && (!sub || t.getAttribute("data-sub") === sub));
        if (show) {
          t.style.display = "";
          if (reduce) { t.classList.remove("b-out", "b-in"); }
          else { t.classList.remove("b-out"); t.style.animationDelay = (Math.min(vi, 10) * 0.035) + "s"; t.classList.remove("b-in"); void t.offsetWidth; t.classList.add("b-in"); }
          vi++;
        } else if (reduce) { t.style.display = "none"; t.classList.remove("b-in"); }
        else { t.classList.remove("b-in"); t.classList.add("b-out"); setTimeout(function () { if (t.classList.contains("b-out")) t.style.display = "none"; }, 300); }
      });
      caveNav.querySelectorAll(".cave-row,.sub-row").forEach(function (r) {
        var rc = r.getAttribute("data-cat"), on;
        if (r.classList.contains("cave-all")) on = (cat === "all");
        else if (r.classList.contains("fam")) on = (rc === cat);
        else on = (rc === cat && r.getAttribute("data-sub") === sub);
        r.classList.toggle("active", on);
      });
      setHead(cat, sub);
    }

    function openDrawer() { caveNav.classList.add("open"); if (caveScrim) { caveScrim.hidden = false; requestAnimationFrame(function () { caveScrim.classList.add("show"); }); } if (caveOpenBtn) caveOpenBtn.setAttribute("aria-expanded", "true"); }
    function closeDrawer() { if (!caveNav.classList.contains("open")) return; caveNav.classList.remove("open"); if (caveScrim) { caveScrim.classList.remove("show"); setTimeout(function () { caveScrim.hidden = true; }, 350); } if (caveOpenBtn) caveOpenBtn.setAttribute("aria-expanded", "false"); }

    caveNav.addEventListener("click", function (e) {
      var sub = e.target.closest(".sub-row");
      if (sub) { filterCave(sub.getAttribute("data-cat"), sub.getAttribute("data-sub")); closeDrawer(); return; }
      if (e.target.closest(".cave-all")) { caveNav.querySelectorAll(".acc-fam.open").forEach(function (f) { f.classList.remove("open"); }); filterCave("all", null); closeDrawer(); return; }
      var fam = e.target.closest(".cave-row.fam");
      if (fam) {
        var wrap = fam.parentNode, hasSub = !!wrap.querySelector(".acc-sub"), wasOpen = wrap.classList.contains("open");
        caveNav.querySelectorAll(".acc-fam.open").forEach(function (f) { if (f !== wrap) f.classList.remove("open"); });
        if (hasSub) wrap.classList.toggle("open", !wasOpen);
        filterCave(fam.getAttribute("data-cat"), null);
        if (!hasSub) closeDrawer();
      }
    });
    if (caveOpenBtn) caveOpenBtn.addEventListener("click", function () { caveNav.classList.contains("open") ? closeDrawer() : openDrawer(); });
    if (caveScrim) caveScrim.addEventListener("click", closeDrawer);
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeDrawer(); });

    // Cartes « univers » -> scroll fluide + ouvre la catégorie
    document.querySelectorAll("[data-jump]").forEach(function (el) {
      el.addEventListener("click", function (ev) {
        var cat = el.getAttribute("data-jump"), sel = document.querySelector("#selection");
        if (sel) { ev.preventDefault(); sel.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" }); }
        setTimeout(function () {
          var fam = caveNav.querySelector('.acc-fam[data-cat="' + cat + '"]');
          if (fam && fam.querySelector(".acc-sub")) { caveNav.querySelectorAll(".acc-fam.open").forEach(function (f) { f.classList.remove("open"); }); fam.classList.add("open"); }
          filterCave(cat, null);
        }, reduce ? 0 : 380);
      });
    });

    setHead("all", null);
  }
  // lightbox (agrandit la silhouette + fiche)
  var lb = document.querySelector(".lb");
  if (lb && bottles.length) {
    var stage = lb.querySelector(".stage"), capEl = lb.querySelector(".lb-cap"), cur = 0;
    function vis() { return bottles.filter(function (t) { return t.style.display !== "none"; }); }
    function render(i) {
      var v = vis(); if (!v.length) return;
      cur = (i + v.length) % v.length;
      var src = v[cur], vis2 = src.querySelector(".visual img, .visual svg"), name = src.querySelector("h3");
      stage.innerHTML = vis2 ? vis2.outerHTML : "";
      capEl.textContent = name ? (name.textContent || "").replace(/\s+à valider\s*$/i, "") : "";
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

  /* ---------- Coverflow 3D champagnes (Weinkeller) ---------- */
  var cf = document.querySelector(".cf");
  if (cf) {
    var cfItems = Array.prototype.slice.call(cf.querySelectorAll(".cf-item"));
    var cfMeta = document.querySelector(".cf-meta");
    var cfDots = document.querySelector(".cf-dots");
    var cave = document.querySelector(".cave-3d");
    var act = Math.min(2, cfItems.length - 1), paused = false, sx = null;

    if (cfDots) cfItems.forEach(function (it, i) {
      var b = document.createElement("button");
      b.setAttribute("aria-label", "Voir la bouteille " + (i + 1));
      b.addEventListener("click", function () { go(i); });
      cfDots.appendChild(b);
    });
    var dots = cfDots ? Array.prototype.slice.call(cfDots.children) : [];
    // Lazy-load des visuels du coverflow (la centrale garde son src pour le LCP) : à la demande
    var cfLazy = cfItems.map(function (it) { return it.querySelector("img[data-lazy]"); });
    function cfLoad(i) { var im = cfLazy[i]; if (im && im.getAttribute("data-lazy")) { im.src = im.getAttribute("data-lazy"); im.removeAttribute("data-lazy"); } }

    function place() {
      cfItems.forEach(function (it, i) {
        var o = i - act, ao = Math.abs(o), tx, tz, ry, sc, op, br, zi;
        if (ao === 0) { tx = 0; tz = 170; ry = 0; sc = 1.1; op = 1; br = 1; zi = 50; }
        else if (ao === 1) { tx = o * 74; tz = 10; ry = -o * 40; sc = .9; op = .92; br = .66; zi = 40; }
        else if (ao === 2) { tx = o * 64 + (o > 0 ? 60 : -60); tz = -130; ry = -o * 46; sc = .78; op = .5; br = .46; zi = 30; }
        else { tx = o * 50; tz = -340; ry = -o * 48; sc = .66; op = 0; br = .4; zi = 5; }
        it.style.transform = "translateX(" + tx + "%) translateZ(" + tz + "px) rotateY(" + ry + "deg) scale(" + sc + ")";
        it.style.opacity = op; it.style.filter = "brightness(" + br + ")"; it.style.zIndex = zi;
        it.setAttribute("aria-hidden", ao === 0 ? "false" : "true");
        it.tabIndex = ao === 0 ? 0 : -1;
      });
      dots.forEach(function (d, i) { d.classList.toggle("on", i === act); });
      var a = cfItems[act];
      if (cfMeta) {
        var set = function (sel, at) { var el = cfMeta.querySelector(sel); if (el) el.textContent = a.getAttribute(at) || ""; };
        set(".b", "data-brand"); set("h3", "data-name"); set(".d", "data-detail"); set(".p", "data-price");
      }
      var ord = document.querySelector(".cf-order a");
      if (ord && a.getAttribute("data-wa")) ord.href = a.getAttribute("data-wa");
      cfLoad(act); cfLoad((act + 1) % cfItems.length); cfLoad((act - 1 + cfItems.length) % cfItems.length);
    }
    function go(i) { act = Math.max(0, Math.min(cfItems.length - 1, i)); place(); }
    cfItems.forEach(function (it, i) {
      it.addEventListener("click", function () {
        if (i !== act) { go(i); }
        else { var w = it.getAttribute("data-wa"); if (w) window.open(w, "_blank", "noopener"); }
      });
    });
    var pv = document.querySelector(".cf-prev"), nx = document.querySelector(".cf-next");
    if (pv) pv.addEventListener("click", function () { go(act - 1); });
    if (nx) nx.addEventListener("click", function () { go(act + 1); });
    cf.addEventListener("pointerdown", function (e) { sx = e.clientX; paused = true; });
    window.addEventListener("pointerup", function (e) {
      if (sx !== null) { var dx = e.clientX - sx; if (Math.abs(dx) > 42) go(act + (dx < 0 ? 1 : -1)); sx = null; }
      setTimeout(function () { paused = false; }, 900);
    });
    if (cave) {
      cave.addEventListener("keydown", function (e) {
        if (e.key === "ArrowLeft") { e.preventDefault(); go(act - 1); }
        if (e.key === "ArrowRight") { e.preventDefault(); go(act + 1); }
      });
      cave.addEventListener("pointerenter", function () { paused = true; });
      cave.addEventListener("pointerleave", function () { paused = false; });
      cave.classList.add("ready");
    }
    place();
    if (!reduce) {
      var cfTimer = null, cfInView = true;
      function cfTick() { if (!paused && cfInView && !document.hidden) { act = (act + 1) % cfItems.length; place(); } }
      function cfStart() { if (!cfTimer) cfTimer = setInterval(cfTick, 4800); }
      function cfStop() { if (cfTimer) { clearInterval(cfTimer); cfTimer = null; } }
      // Pause quand le hero est hors-écran (économise repeints) ; ne démarre qu'après
      // stabilisation du LCP (sinon l'auto-rotation repeint de grandes images et gonfle le LCP)
      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (es) { cfInView = es[0].isIntersecting; cfInView ? cfStart() : cfStop(); }, { threshold: .25 }).observe(cave || cf);
      }
      var cfBoot = function () { setTimeout(cfStart, 2600); };
      if (document.readyState === "complete") cfBoot(); else addEventListener("load", cfBoot);
    }
    // Diffère le chargement des autres visuels du coverflow au-delà du 1er rendu (ne starve pas le CSS/LCP)
    var cfStream = function () {
      var ord = cfItems.map(function (_, i) { return i; }).sort(function (x, y) { return Math.abs(x - act) - Math.abs(y - act); });
      (function nxt(k) { if (k < ord.length) { cfLoad(ord[k]); requestAnimationFrame(function () { nxt(k + 1); }); } })(0);
    };
    if (document.readyState === "complete") setTimeout(cfStream, 300); else addEventListener("load", function () { setTimeout(cfStream, 300); });
  }

  /* ---------- Poussière d'or (canvas, hero Weinkeller) ---------- */
  var gd = document.querySelector("canvas.golddust");
  if (gd && !reduce && !isMobile && !saveData) {
    var gx = gd.getContext("2d"), host = gd.closest(".hero") || gd.parentElement, motes = [], graf = null, DPR = Math.min(devicePixelRatio || 1, 2);
    function gsize() {
      var r = host.getBoundingClientRect();
      gd.width = Math.round(r.width * DPR); gd.height = Math.round(r.height * DPR);
      gx.setTransform(DPR, 0, 0, DPR, 0, 0);
      motes = [];
      var n = Math.min(46, Math.round(r.width / 26));
      for (var i = 0; i < n; i++) motes.push(mk(r.width, r.height, true));
    }
    function mk(w, h, anywhere) {
      return { x: Math.random() * w, y: anywhere ? Math.random() * h : h + 8, r: .6 + Math.random() * 1.8,
        s: .15 + Math.random() * .5, d: (Math.random() - .5) * .25, o: .15 + Math.random() * .5, ph: Math.random() * 6.28 };
    }
    function gframe() {
      var w = gd.width / DPR, h = gd.height / DPR;
      gx.clearRect(0, 0, w, h);
      for (var i = 0; i < motes.length; i++) {
        var m = motes[i]; m.y -= m.s; m.x += m.d + Math.sin((m.y + m.ph) * .02) * .25; m.ph += .01;
        if (m.y < -8) motes[i] = mk(w, h, false);
        gx.beginPath(); gx.arc(m.x, m.y, m.r, 0, 6.2832);
        gx.fillStyle = "rgba(206,168,92," + (m.o * (.6 + Math.sin(m.ph) * .4)) + ")"; gx.fill();
      }
      graf = requestAnimationFrame(gframe);
    }
    var grun = false, gin = true;
    function gsync() { if (gin && !document.hidden) { if (!grun) { grun = true; gframe(); } } else { grun = false; if (graf) cancelAnimationFrame(graf); graf = null; } }
    function gstart() {
      gsize();
      if ("IntersectionObserver" in window) new IntersectionObserver(function (es) { es.forEach(function (e) { gin = e.isIntersecting; }); gsync(); }, { threshold: 0 }).observe(host);
      document.addEventListener("visibilitychange", gsync);
      var grz; addEventListener("resize", function () { clearTimeout(grz); grz = setTimeout(gsize, 200); }, { passive: true });
      gsync();
    }
    // init différée hors du chemin critique de chargement (réduit la tâche longue au démarrage)
    if ("requestIdleCallback" in window) requestIdleCallback(gstart, { timeout: 1400 }); else setTimeout(gstart, 700);
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

  /* ---------- Bulle coffrets cadeaux (Weinkeller) : après 10 s, fermable, 1x/session ---------- */
  (function () {
    var gb = document.getElementById("giftBubble");
    if (!gb) return;
    try { if (sessionStorage.getItem("gb-dismissed") === "1") return; } catch (e) {}
    var closed = false;
    function show() { if (closed || gb.hidden === false) return; gb.hidden = false; requestAnimationFrame(function () { gb.classList.add("open"); }); }
    var timer = setTimeout(show, 10000);
    function dismiss() { try { sessionStorage.setItem("gb-dismissed", "1"); } catch (e) {} }
    function close() { closed = true; clearTimeout(timer); gb.classList.remove("open"); dismiss(); setTimeout(function () { gb.hidden = true; }, 550); }
    var cb = document.getElementById("gbClose"); if (cb) cb.addEventListener("click", close);
    var cta = gb.querySelector(".gb-cta"); if (cta) cta.addEventListener("click", dismiss);
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && gb.classList.contains("open")) close(); });
  })();
})();

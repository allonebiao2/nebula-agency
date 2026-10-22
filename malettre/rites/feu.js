/* ── LE FEU D'ARTIFICE · « le ciel s'allume pour toi » ── Une nuit étoilée au-dessus de l'eau, les lumières d'une rive
   au loin ; tout ce qui brille dans le ciel tremble dans l'eau. On touche le ciel : une fusée monte VERS LE DOIGT (son
   sifflement), éclate (le choc, puis le crépitement), en pivoine, en anneau, en saule d'or ; trois fois (sinon les
   fusées partent seules). Au troisième, le bouquet final : une dernière fusée monte au milieu et ÉCRIT LE PRÉNOM en
   étincelles (dans un cœur, pour l'amour) ; le nom reste suspendu, scintille, puis retombe en pluie d'or sur la lettre
   qui apparaît derrière (`plein` : la nuit s'efface, la page est derrière). Tout est calculé à partir du temps (traînée
   de l'air résolue exactement) : le même instant se rejoue à l'identique, pour les planches et pour le film.
   Thèmes (`THEME.motif`) : fete (toutes les couleurs), or (or et champagne), amour (rose, rouge et or, le cœur). */
(function () {
  var M = Theatre.M, C = Theatre.C;
  var MOTIFS = {
    fete: { couleurs: ["#ffd36b", "#ff5d7a", "#6be0ff", "#a6ff8a", "#c99bff", "#fff4dc"], forme: "nom", ciel: ["#1d1745", "#0a0818", "#2c2457"] },
    or: { couleurs: ["#ffd36b", "#fff1c4", "#ffb347", "#fff4dc"], forme: "nom", ciel: ["#151b36", "#070810", "#26304f"] },
    amour: { couleurs: ["#ff5d7a", "#ff9db0", "#ffd36b", "#fff4dc"], forme: "coeur", ciel: ["#2b1030", "#0d0611", "#46203f"] }
  };
  var EAU = -0.56, GR = 0.55, K = 2.1, BAS = -0.62, SORTES = ["pivoine", "anneau", "saule", "pivoine", "anneau"];
  /* ses sons à lui (seule une lettre qui porte ce rite les emporte) : le contexte et les sons partagés viennent de
     l'atelier, `bruit` et `SON` de la lettre */
  var SONS = {
    /* une fusée qui monte : un sifflement qui grimpe, et le souffle de sa traînée */
    fusee: function (quand, duree) {
      var ctx = Atelier.Son.ctx(); if (!ctx || typeof bruit !== "function") return;
      var t = ctx.currentTime + (quand || 0), d = duree || 1, o = ctx.createOscillator(), g = ctx.createGain();
      o.type = "sine"; o.frequency.setValueAtTime(700 + Math.random() * 200, t); o.frequency.exponentialRampToValueAtTime(1900 + Math.random() * 500, t + d);
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.022, t + 0.08); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
      o.connect(g); g.connect(SON.sortie); o.start(t); o.stop(t + d + 0.05);
      Atelier.Son.souffle(quand || 0, d * 0.9, 2400, 5200, 0.05);
    },
    /* l'éclatement : un choc grave qui roule, puis le crépitement des étoiles qui s'allument */
    boum: function (quand, force) {
      var ctx = Atelier.Son.ctx(); if (!ctx || typeof bruit !== "function") return;
      var t = ctx.currentTime + (quand || 0), k = force || 1, b = bruit(ctx, 1.4), f = ctx.createBiquadFilter(), g = ctx.createGain();
      f.type = "lowpass"; f.frequency.setValueAtTime(900, t); f.frequency.exponentialRampToValueAtTime(120, t + 1.2);
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.55 * k, t + 0.012); g.gain.exponentialRampToValueAtTime(0.0001, t + 1.3);
      b.connect(f); f.connect(g); g.connect(SON.sortie); b.start(t);
      var o = ctx.createOscillator(), g2 = ctx.createGain();
      o.type = "sine"; o.frequency.setValueAtTime(64, t); o.frequency.exponentialRampToValueAtTime(34, t + 0.5);
      g2.gain.setValueAtTime(0.0001, t); g2.gain.exponentialRampToValueAtTime(0.4 * k, t + 0.01); g2.gain.exponentialRampToValueAtTime(0.0001, t + 0.6);
      o.connect(g2); g2.connect(SON.sortie); o.start(t); o.stop(t + 0.65);
      SONS.crepite((quand || 0) + 0.35, 1.3 * k, 0.05 * k);
    },
    /* le crépitement : des centaines de petits claquements aigus, de plus en plus rares */
    crepite: function (quand, duree, force) {
      var ctx = Atelier.Son.ctx(); if (!ctx || typeof bruit !== "function") return;
      var t0 = ctx.currentTime + (quand || 0), d = duree || 1, n = Math.round(d * 90), buf = bruit(ctx, 0.012).buffer;
      for (var i = 0; i < n; i++) {
        var k = i / n, t = t0 + Math.pow(k, 1.6) * d, s = ctx.createBufferSource(), f = ctx.createBiquadFilter(), g = ctx.createGain();
        s.buffer = buf; f.type = "highpass"; f.frequency.value = 2500 + Math.random() * 4000;
        g.gain.setValueAtTime((force || 0.05) * (1 - k) * (0.3 + Math.random() * 0.7), t); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.012);
        s.connect(f); f.connect(g); g.connect(SON.sortie); s.start(t); s.stop(t + 0.02);
      }
    }
  };

  /* la position et la vitesse d'une étincelle lancée à v, freinée par l'air (K) et tirée par la pesanteur : exact */
  function vol(v, tau, g) {
    var e = Math.exp(-K * tau), a = (1 - e) / K;
    return [v[0] * a, v[1] * a - (g / K) * (tau - a), v[2] * a, v[0] * e, v[1] * e - (g / K) * (1 - e)];
  }
  /* les points d'un prénom (et d'un cœur) : on l'écrit sur une toile, on garde ce qui est encré, une maille sur trois */
  function points(D, forme, largeur) {
    var cv = document.createElement("canvas"), w = 720, h = 220, g = cv.getContext("2d"), nom = String(D.pour || (D.EN ? "you" : "toi")).slice(0, 14);
    cv.width = w; cv.height = h;
    var taille = 170; g.font = "italic 700 " + taille + "px " + Atelier.SERIF;
    while (g.measureText(nom).width > w * 0.92 && taille > 30) { taille -= 6; g.font = "italic 700 " + taille + "px " + Atelier.SERIF; }
    g.fillStyle = "#fff"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(nom, w / 2, h / 2);
    var d = g.getImageData(0, 0, w, h).data, P = [], pas = 4, x0 = w, x1 = 0, y0 = h, y1 = 0;
    for (var y = 0; y < h; y += pas) for (var x = 0; x < w; x += pas) if (d[(y * w + x) * 4 + 3] > 140) {
      P.push([x, y]); x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y);
    }
    var cible = largeur * (forme === "coeur" ? 0.58 : 1), ech = Math.min(cible / Math.max(1, x1 - x0), cible * 0.42 / Math.max(1, y1 - y0));
    var max = 460, k = Math.max(1, Math.ceil(P.length / max)), sortie = [], mx = (x0 + x1) / 2, my = (y0 + y1) / 2;
    for (var i = 0; i < P.length; i += k) sortie.push([(P[i][0] - mx) * ech, -(P[i][1] - my) * ech]);
    if (forme === "coeur") {
      /* le cœur autour du nom : la courbe classique, 120 étincelles */
      for (var q = 0; q < 120; q++) {
        var t = q / 120 * Math.PI * 2, s = largeur / 34;
        sortie.push([16 * Math.pow(Math.sin(t), 3) * s, (13 * Math.cos(t) - 5 * Math.cos(2 * t) - 2 * Math.cos(3 * t) - Math.cos(4 * t)) * s + largeur * 0.06]);
      }
    }
    return sortie;
  }

  return {
    id: "feu",
    plein: true,
    duree: 30,
    bouton: { fr: "Allumer le ciel", en: "Light up the sky" },
    indice: { fr: "Touche le ciel", en: "Touch the sky" },
    monter: function (S, D) {
      var A = Atelier, th = typeof THEME !== "undefined" && THEME ? THEME : {}, T = {}, k;
      var base = MOTIFS[th.motif] || MOTIFS.fete;
      for (k in base) T[k] = base[k];
      for (k in th) T[k] = th[k];
      A.matieres(S, MATIERES);
      this.T = T; this.D = D; this.fusees = []; this.finale = null; this.lancees = 0;
      this.cols = T.couleurs.map(function (c) { return A.rvb(c); });
      var asp = S.W / S.H; this.asp = asp;
      /* la nuit : le ciel en dégradé, les étoiles, la rive au loin et ses lumières, l'eau et ses rides */
      var Hc = 1024, Wc = 512, Wv = Hc * asp; while (Wc < Wv * 0.85 && Wc < 2048) Wc *= 2;
      var hor = (1 - EAU) / 2 * Hc;
      this.ciel = S.toile(Wc, Hc, function (g) {
        var d = g.createLinearGradient(0, 0, 0, hor);
        d.addColorStop(0, T.ciel[1]); d.addColorStop(0.65, T.ciel[0]); d.addColorStop(1, T.ciel[2]);
        g.fillStyle = d; g.fillRect(0, 0, Wc, hor);
        var e = g.createLinearGradient(0, hor, 0, Hc); e.addColorStop(0, T.ciel[0]); e.addColorStop(1, "#030308");
        g.fillStyle = e; g.fillRect(0, hor, Wc, Hc - hor);
        g.setTransform(Wc / Wv, 0, 0, 1, 0, 0);
        var h = C.hasard(61), i;
        for (i = 0; i < 420; i++) {
          var y = Math.pow(h(), 1.4) * hor * 0.95, r = 0.4 + h() * h() * 1.6;
          g.fillStyle = "rgba(255,250,235," + (0.25 + h() * 0.7).toFixed(2) + ")"; g.beginPath(); g.arc(h() * Wv, y, r, 0, Math.PI * 2); g.fill();
        }
        /* la rive : une bande sombre, quelques lumières chaudes, leurs reflets en traits dans l'eau */
        g.fillStyle = "#05040a"; g.fillRect(0, hor - 9, Wv, 12);
        for (i = 0; i < 46; i++) {
          var x = h() * Wv, c = h() < 0.7 ? "255,196,120" : "255,236,200";
          g.fillStyle = "rgba(" + c + "," + (0.5 + h() * 0.5).toFixed(2) + ")"; g.fillRect(x, hor - 7 + h() * 4, 1.6, 1.6);
          g.fillStyle = "rgba(" + c + ",0.18)"; g.fillRect(x - 0.4, hor + 4, 2.4, 10 + h() * 26);
        }
        for (i = 0; i < 160; i++) { g.fillStyle = "rgba(160,170,230," + (0.03 + h() * 0.06).toFixed(3) + ")"; g.fillRect(h() * Wv, hor + 6 + h() * (Hc - hor), 8 + h() * 40, 1); }
      }, false);
      this.ciel.toile = null;
      this.quad = S.maillage({ p: [-1, -1, 0, 1, -1, 0, -1, 1, 0, 1, 1, 0], n: [0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1], uv: [0, 1, 1, 1, 0, 0, 1, 0], i: [0, 1, 2, 1, 3, 2] });
      this.nom = points(D, T.forme, Math.min(2 * asp * 0.86, 1.5));
      var hs = C.hasard(9), et = [];
      for (var q = 0; q < 34; q++) et.push({ x: (hs() * 2 - 1) * asp, y: EAU + 0.1 + Math.pow(hs(), 1.3) * (1 - EAU - 0.1), ph: hs() * 6.3, s: 0.006 + hs() * 0.01 });
      this.etoiles = et;
    },
    /* une fusée : du bas de l'eau vers (x, y), elle monte en ralentissant, puis éclate ; le son est réglé d'avance */
    lancer: function (t, x, y, finale) {
      var n = this.fusees.length, d = finale ? 1.25 : 0.95 + (y - EAU) * 0.18;
      var f = { t0: t, x0: x * 0.6 + (n % 2 ? 0.05 : -0.05), x1: x, y1: y, d: d, n: n, finale: !!finale,
        sorte: finale ? "nom" : SORTES[n % SORTES.length], c: this.cols[n % this.cols.length] };
      this.fusees.push(f);
      SONS.fusee(0, d); SONS.boum(d, finale ? 1.4 : 0.8 + (n % 3) * 0.1);
      if (!finale) this.lancees++;
      if (!finale && this.lancees === 3) {
        if (this.taire) this.taire();
        this.finale = t + 1.7;
      }
      return f;
    },
    geste: function () { this.lancer(0, 0.38 * this.asp, 0.42); this.auto = this.D.auto != null ? this.D.auto : 1.6; },
    toucher: function (S, e) {
      if (e.type !== "bas" || e.t < 0) return;
      var last = this.fusees.length ? this.fusees[this.fusees.length - 1].t0 : -1;
      if (e.t - last < 0.22 || (this.finale != null && e.t > this.finale + 2.5)) return;
      var x = (e.x / S.W * 2 - 1) * this.asp, y = Math.max(EAU + 0.42, Math.min(0.82, 1 - e.y / S.H * 2));
      this.lancer(e.t, x, y);
    },
    sommet: function () { var f = this.fusees.filter(function (q) { return q.finale; })[0]; return f ? f.t0 + f.d : null; },
    revele: function (t) { var s = this.sommet(); return s != null && t > s + 2.7; },
    fini: function (t) { var s = this.sommet(); return s != null && t > s + 5.2; },
    rendre: function (S, t, ti) {
      var T = this.T, D = this.D, dort = D.verrou && D.verrou(), asp = S.W / S.H, self = this;
      /* les fusées qui manquent partent seules ; le bouquet final part à son heure */
      if (t >= 0 && this.lancees < 3 && t > this.fusees[this.fusees.length - 1].t0 + this.auto) {
        var h = C.hasard(this.fusees.length * 7 + 3);
        this.lancer(t, (h() * 1.6 - 0.8) * asp, 0.2 + h() * 0.55);
      }
      if (this.finale != null && t >= this.finale && !this.sommet()) this.lancer(this.finale, 0, 0.3, true);
      var som = this.sommet(), rev = som != null ? som + 2.7 : null;
      var ciel = rev == null ? 1 : 1 - C.p(t, rev, rev + 0.9);
      var champ = 30, d = 1 / Math.tan(champ * Math.PI / 360), choc = som != null && t > som ? Math.exp(-(t - som) * 6) * 0.01 : 0;
      S.camera([Math.sin(ti * 53) * choc, Math.cos(ti * 61) * choc, d], [0, 0, 0], champ);
      S.lumiere({ lum: [0, 0, 1], lumc: [0, 0, 0], amb: [1, 1, 1], lp: [0, 0, 1], lpc: [0, 0, 0], brume: 0, rim: [0, 0, 0] });
      S.post.dof = 0; S.post.bloom = 0.95; S.post.seuil = 0.55; S.post.vign = 0.38; S.post.grain = 0.022;
      S.effacer();
      /* la nuit (elle s'efface quand la lettre apparaît) */
      if (ciel > 0) S.dessiner(this.quad, { mode: "plat", tex: this.ciel, teinte: [1, 1, 1, ciel] }, M.echelle(asp, 1, 1));
      var L = [], lumiere = 0;
      /* les étoiles qui scintillent */
      if (ciel > 0) this.etoiles.forEach(function (e) {
        L.push({ p: [e.x, e.y, 0.01], s: e.s * (1 + 0.5 * Math.sin(ti * 2.3 + e.ph)), c: [1, 0.96, 0.88, ciel * (0.35 + 0.35 * Math.sin(ti * 1.7 + e.ph * 3)) * (dort ? 0.6 : 1)] });
      });
      this.fusees.forEach(function (f) {
        var tau = t - f.t0; if (tau < 0) return;
        if (tau < f.d) {
          /* la montée : une tête brillante, une traînée d'étincelles qui retombent */
          var u = tau / f.d, k = 1 - Math.pow(1 - u, 2.2), x = C.mix(f.x0, f.x1, k), y = C.mix(BAS, f.y1, k);
          L.push({ p: [x, y, 0.02], s: 0.045, c: [1, 0.92, 0.7, 1] }); L.push({ p: [x, y, 0.02], s: 0.16, c: [1, 0.7, 0.4, 0.25] });
          for (var q = 1; q <= 9; q++) {
            var u2 = Math.max(0, (tau - q * 0.035) / f.d), k2 = 1 - Math.pow(1 - u2, 2.2);
            L.push({ p: [C.mix(f.x0, f.x1, k2) + Math.sin(q * 7.1 + f.n) * 0.004 * q, C.mix(BAS, f.y1, k2) - q * q * 0.0006, 0.02], s: 0.03 * (1 - q / 11), c: [1, 0.75, 0.4, 0.75 * (1 - q / 10)] });
          }
          return;
        }
        /* l'éclatement */
        var b = tau - f.d, cx = f.x1, cy = f.y1, h = C.hasard(f.n * 131 + 7), c = f.c;
        lumiere += Math.exp(-b * 2.5) * (f.finale ? 1.4 : 0.8);
        if (b < 0.25) L.push({ p: [cx, cy, 0.03], s: 0.35 + b * 1.2, c: [1, 0.95, 0.85, (1 - b / 0.25) * 0.45] });
        if (f.sorte === "nom") {
          /* le bouquet final : chaque étincelle file à sa place dans le prénom, s'y tient, scintille, puis tombe en pluie */
          self.nom.forEach(function (p, i) {
            var r = h(), ar = Math.min(1, b / 0.95), e = C.sort(ar), tx = cx + p[0], ty = cy + p[1];
            var x = C.mix(cx, tx, e) + Math.sin(b * 3 + i) * 0.002, y = C.mix(cy, ty, e), chute = Math.max(0, b - 2.6), a = 1;
            if (chute > 0) { y -= 0.42 * chute * chute + 0.05 * chute; x += Math.sin(i + chute * 2) * 0.01 * chute; a = Math.max(0, 1 - chute / 1.9); }
            var sc = b > 1 && b < 2.6 ? 0.55 + 0.45 * Math.sin(ti * 9 + i * 1.7) : 1, col = r < 0.75 ? [1, 0.82, 0.42] : [1, 0.96, 0.86];
            L.push({ p: [x, y, 0.04], s: 0.024 + 0.01 * r, c: [col[0], col[1], col[2], a * sc] });
            if (chute > 0) L.push({ p: [x, y + 0.02, 0.04], s: 0.03, ax: [0, 1, 0], ay: [1, 0, 0], h: 0.25, c: [1, 0.7, 0.3, a * 0.4] });
          });
          return;
        }
        var nb = f.sorte === "saule" ? 170 : f.sorte === "anneau" ? 130 : 230, vie = f.sorte === "saule" ? 3.1 : 2.3;
        var g = f.sorte === "saule" ? GR * 1.5 : GR;
        var axe = [h() - 0.5, h() - 0.5, h() - 0.5];
        for (var i = 0; i < nb; i++) {
          var v, vi = vie * (0.75 + h() * 0.25);
          if (f.sorte === "anneau") {
            var a = i / nb * Math.PI * 2, R = 0.95;
            v = [Math.cos(a) * R, Math.sin(a) * R * 0.55 + axe[1] * 0.3, Math.sin(a) * R * 0.6];
          } else {
            var th = h() * Math.PI * 2, ph = Math.acos(2 * h() - 1), R2 = (f.sorte === "saule" ? 0.62 : 1.0) * (0.9 + h() * 0.12);
            v = [Math.sin(ph) * Math.cos(th) * R2, Math.cos(ph) * R2, Math.sin(ph) * Math.sin(th) * R2];
          }
          var blanc = h() < 0.16;
          if (b > vi) continue;
          var r2 = vol(v, b, g), al = Math.pow(1 - b / vi, 0.9);
          /* les paillettes crépitent en mourant (selon le temps : un tirage conditionnel décalerait toutes les suivantes) */
          if (blanc && b > vi * 0.55) al *= Math.sin(ti * 41 + i * 13.7) > 0 ? 1 : 0.15;
          var col2 = blanc ? [1, 0.97, 0.9] : f.sorte === "saule" ? [1, 0.78, 0.38] : [c[0], c[1], c[2]];
          var vit = Math.hypot(r2[3], r2[4]) || 0.001, px = cx + r2[0], py = cy + r2[1];
          /* une traînée dans le sens de la course (plus elle va vite, plus elle est longue) */
          L.push({ p: [px, py, 0.03 + r2[2] * 0.3], s: 0.03 + vit * 0.09, ax: [r2[3] / vit, r2[4] / vit, 0], ay: [-r2[4] / vit, r2[3] / vit, 0], h: 0.3, c: [col2[0], col2[1], col2[2], al] });
          if (i % 3 === 0) L.push({ p: [px, py, 0.03 + r2[2] * 0.3], s: 0.1, c: [col2[0], col2[1], col2[2], al * 0.12] });
        }
      });
      /* la lueur d'un éclatement éclaire le ciel et l'eau */
      if (lumiere > 0) L.push({ p: [0, 0.2, -0.01], s: 3.2, c: [0.6, 0.5, 0.7, Math.min(0.22, lumiere * 0.12) * ciel] });
      /* l'eau : la lumière de chaque bouquet y tombe en colonnes de rides sous lui, qui tremblent et s'éteignent avec lui */
      var R = [];
      if (ciel > 0) this.fusees.forEach(function (f) {
        var b = t - f.t0 - f.d; if (b < 0) return;
        var force = Math.exp(-b * (f.finale ? 0.6 : 1.4)) * ciel, c = f.finale ? [1, 0.8, 0.45] : f.c;
        if (force < 0.02) return;
        for (var q = 0; q < 14; q++) {
          var y = EAU - 0.025 - q * 0.032, ride = Math.sin(q * 2.3 + ti * 5 + f.n) * 0.5 + 0.5;
          R.push({ p: [f.x1 + Math.sin(q * 1.7 + ti * 3.1 + f.n) * 0.03, y, 0.01], s: 0.07 + 0.1 * ride * (f.finale ? 2 : 1), h: 0.18,
            ax: [1, 0, 0], ay: [0, 1, 0], c: [c[0], c[1], c[2], force * (0.35 - q * 0.02) * (0.4 + 0.6 * ride)] });
        }
      });
      S.lutins(R.concat(L), S.rond, true);
    }
  };
})()

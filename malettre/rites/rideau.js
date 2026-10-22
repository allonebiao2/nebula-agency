/* ── LE RIDEAU · « les trois coups » ── L'écran est une scène : deux pans de velours lourds tombent jusqu'aux feux de
   la rampe, un lambrequin festonné en haut porte « Ma lettre à <prénom> » brodé d'or, des franges d'or bordent tout.
   Au théâtre, on frappe trois coups avant que le rideau se lève : le premier toucher est le premier coup (un choc sourd
   sur le plancher, la scène tremble, la poussière tombe du lambrequin) ; on frappe les deux autres du doigt (sinon ils
   viennent seuls) ; au troisième, un silence, puis le rideau s'ouvre « à l'italienne » (chaque pan relevé vers son coin,
   les plis se serrent), un projecteur cherche la lettre, et pour une fête, la salle applaudit. Derrière, la vraie
   lettre (`plein` : fenêtre transparente) ; puis le rideau et le lambrequin s'envolent hors de la scène.
   Thèmes (`THEME.motif`) : rouge (le velours de théâtre), ivoire (une soie de mariage), nuit (un velours de minuit). */
(function () {
  var M = Theatre.M, C = Theatre.C;
  var MOTIFS = {
    rouge: { a: "#8a1424", b: "#4a0812", or: "#d8b25a", rim: [0.42, 0.08, 0.1], lum: [0.95, 0.86, 0.8], amb: [0.16, 0.08, 0.09], bravo: true },
    ivoire: { a: "#f2ead9", b: "#d8c8ae", or: "#c9a35a", rim: [0.3, 0.26, 0.2], lum: [0.82, 0.8, 0.76], amb: [0.3, 0.28, 0.28], bravo: false },
    nuit: { a: "#22305e", b: "#0e142e", or: "#d8bf78", rim: [0.16, 0.2, 0.42], lum: [0.86, 0.86, 0.95], amb: [0.1, 0.11, 0.17], bravo: true }
  };
  var NX = 64, NY = 38, PLIS = 6, BAS = 0.6;   /* le bas du lambrequin (en y : 1 en haut de l'écran, -1 en bas) */

  /* le velours : un dégradé, des côtes verticales à peine marquées, la frange d'or en bas (feuille d'or dans la hauteur) */
  function velours(S, T, haut, frange) {
    return S.toile(512, 1024, function (g) {
      var h = C.hasard(haut ? 3 : 4);
      if (haut) { g.fillStyle = "rgb(90,0,0)"; g.fillRect(0, 0, 512, 1024); }
      else { var d = g.createLinearGradient(0, 0, 0, 1024); d.addColorStop(0, T.b); d.addColorStop(0.18, T.a); d.addColorStop(1, T.a); g.fillStyle = d; g.fillRect(0, 0, 512, 1024); }
      if (!haut) for (var i = 0; i < 60; i++) {
        g.fillStyle = "rgba(" + (h() < 0.5 ? "255,255,255," : "0,0,0,") + (0.008 + h() * 0.018).toFixed(3) + ")";
        g.fillRect(h() * 512, 0, 6 + h() * 30, 1024);
      }
      if (!haut) for (var i2 = 0; i2 < 14000; i2++) { g.fillStyle = "rgba(255,255,255," + (h() * 0.03).toFixed(3) + ")"; g.fillRect(h() * 512, h() * 1024, 1, 1); }
      if (!frange) return;
      /* la frange : un galon tressé, puis des brins d'or qui pendent */
      var y0 = 1024 - 70;
      g.fillStyle = haut ? "rgb(200,255,0)" : T.or; g.fillRect(0, y0, 512, 14);
      for (var x2 = 0; x2 < 512; x2 += 6) {
        g.fillStyle = haut ? "rgb(" + (150 + (x2 % 12 ? 50 : 0)) + ",255,0)" : T.or;
        g.fillRect(x2, y0 + 16, 3, 50 + (x2 % 18 === 0 ? 6 : 0));
      }
      if (haut) for (var x3 = 0; x3 < 512; x3 += 8) { g.fillStyle = "rgb(255,255,0)"; g.beginPath(); g.arc(x3, y0 + 7, 3, 0, Math.PI * 2); g.fill(); }
    }, true);
  }
  /* le lambrequin : le même velours, le galon d'or, et le nom brodé au milieu */
  function lambrequin(S, T, D, haut, rapport) {
    /* la toile fait 1024 × 512 ; on y dessine dans les proportions du lambrequin à l'écran (largeur / hauteur = rapport) */
    var Hv = 512, Wv = Hv * rapport;
    return S.toile(1024, 512, function (g) {
      if (haut) { g.fillStyle = "rgb(90,0,0)"; g.fillRect(0, 0, 1024, 512); }
      else { var d = g.createLinearGradient(0, 0, 0, 512); d.addColorStop(0, T.b); d.addColorStop(1, T.a); g.fillStyle = d; g.fillRect(0, 0, 1024, 512); }
      g.setTransform(1024 / Wv, 0, 0, 1, 0, 0);
      var or = haut ? "rgb(220,255,0)" : T.or;
      g.fillStyle = or; g.fillRect(0, 400, Wv, 16); g.fillRect(0, 428, Wv, 6);
      for (var x = 0; x < Wv; x += 8) g.fillRect(x, 440, 3.5, 60);
      g.textAlign = "center"; g.fillStyle = or;
      var t1 = D.EN ? "MY LETTER TO" : "MA LETTRE À", petit = Math.round(Hv * 0.085), esp = petit * 0.4, larg = 0, i;
      g.font = "600 " + petit + "px " + Atelier.SERIF;
      for (i = 0; i < t1.length; i++) larg += g.measureText(t1[i]).width + esp;
      var x0 = Wv / 2 - (larg - esp) / 2; g.textAlign = "left";
      for (i = 0; i < t1.length; i++) { g.fillText(t1[i], x0, Hv * 0.32); x0 += g.measureText(t1[i]).width + esp; }
      var n = String(D.pour || (D.EN ? "you" : "toi")).slice(0, 18), taille = Math.round(Hv * 0.34);
      g.font = "italic 500 " + taille + "px " + Atelier.SERIF;
      while (g.measureText(n).width > Wv * 0.72 && taille > 20) { taille -= 4; g.font = "italic 500 " + taille + "px " + Atelier.SERIF; }
      g.textAlign = "center"; g.fillText(n, Wv / 2, Hv * 0.68);
    }, false);
  }
  /* un pan de rideau : une grille dont les sommets bougent à chaque image (`S.maj`) */
  function pan(S, sens) {
    var n = (NX + 1) * (NY + 1), uv = [], idx = [], i, j;
    for (j = 0; j <= NY; j++) for (i = 0; i <= NX; i++) uv.push(i / NX * 3, j / NY);
    for (j = 0; j < NY; j++) for (i = 0; i < NX; i++) {
      var a = j * (NX + 1) + i, b = a + 1, c = a + NX + 1, d = c + 1;
      if (sens > 0) idx.push(a, b, c, b, d, c); else idx.push(a, c, b, b, c, d);
    }
    var p = new Float32Array(n * 3), nn = new Float32Array(n * 3);
    return { m: S.maillage({ p: p, n: nn, uv: uv, i: idx }), p: p, n: nn, sens: sens };
  }
  /* la normale de chaque sommet, par différences sur la grille, tournée vers la salle */
  function normales(P, N, nx, ny) {
    for (var j = 0; j <= ny; j++) for (var i = 0; i <= nx; i++) {
      var k = (j * (nx + 1) + i) * 3, kl = (j * (nx + 1) + Math.max(0, i - 1)) * 3, kr = (j * (nx + 1) + Math.min(nx, i + 1)) * 3;
      var ku = (Math.max(0, j - 1) * (nx + 1) + i) * 3, kd = (Math.min(ny, j + 1) * (nx + 1) + i) * 3;
      var ax = P[kr] - P[kl], ay = P[kr + 1] - P[kl + 1], az = P[kr + 2] - P[kl + 2];
      var bx = P[kd] - P[ku], by = P[kd + 1] - P[ku + 1], bz = P[kd + 2] - P[ku + 2];
      var x = ay * bz - az * by, y = az * bx - ax * bz, z = ax * by - ay * bx, l = Math.hypot(x, y, z) || 1;
      if (z < 0) l = -l;
      N[k] = x / l; N[k + 1] = y / l; N[k + 2] = z / l;
    }
  }

  return {
    id: "rideau",
    plein: true,
    duree: 30,
    bouton: { fr: "Frapper les trois coups", en: "Knock three times" },
    indice: { fr: "Frappe encore deux coups", en: "Two more knocks" },
    monter: function (S, D) {
      var A = Atelier, th = typeof THEME !== "undefined" && THEME ? THEME : {}, T = {}, k;
      var base = MOTIFS[th.motif] || MOTIFS.rouge;
      for (k in base) T[k] = base[k];
      for (k in th) T[k] = th[k];
      A.matieres(S, MATIERES);
      this.T = T; this.D = D; this.coups = []; this.tOuvre = null;
      this.tex = velours(S, T, false, true); this.haut = velours(S, T, true, true);
      var rapport = (2 * S.W / S.H) / (1.02 - BAS + 0.04);
      this.texL = lambrequin(S, T, D, false, rapport); this.hautL = lambrequin(S, T, D, true, rapport);
      this.G = pan(S, -1); this.Dr = pan(S, 1);
      /* le lambrequin : une bande festonnée (des drapés qui pendent entre leurs points d'attache) */
      var LX = 90, LY = 8, p = [], n = [], uv = [], idx = [], i, j;
      for (j = 0; j <= LY; j++) for (i = 0; i <= LX; i++) { p.push(0, 0, 0); n.push(0, 0, 1); uv.push(i / LX, j / LY); }
      for (j = 0; j < LY; j++) for (i = 0; i < LX; i++) { var a = j * (LX + 1) + i, b = a + 1, c = a + LX + 1, d = c + 1; idx.push(a, c, b, b, c, d); }
      this.L = { m: S.maillage({ p: p, n: n, uv: uv, i: idx }), p: new Float32Array(p), n: new Float32Array(n), nx: LX, ny: LY };
      var h = C.hasard(53), pou = [];
      for (var q = 0; q < 70; q++) pou.push({ x: (h() - 0.5) * 2.2, v: 0.3 + h() * 0.5, s: 0.006 + h() * 0.012, ph: h() * 6.3, k: q % 3 });
      this.poussiere = pou;
    },
    /* un coup : le premier est le toucher qui ouvre ; chaque toucher suivant en frappe un autre */
    frapper: function (t) {
      if (this.coups.length >= 3 || (this.coups.length && t - this.coups[this.coups.length - 1] < 0.32)) return;
      this.coups.push(t);
      Atelier.Son.coup(0);
      if (this.coups.length === 2 && this.dire) this.dire({ fr: "Encore un", en: "One more" });
      if (this.coups.length === 3) {
        if (this.taire) this.taire();
        this.tOuvre = t + 0.75;
        var S = Atelier.Son;
        S.souffle(0.75, 2.4, 180, 700, 0.22); S.accord(0.9, [130.81, 196, 261.63, 392], 3.6, 0.04);
        if (this.T.bravo) S.applaudir(1.6, 3.4, 0.11);
      }
    },
    geste: function () { this.frapper(0); this.auto = this.D.auto != null ? this.D.auto : 3.4; },
    toucher: function (S, e) {
      if (e.type === "bas" && e.t >= 0) this.frapper(e.t);
    },
    revele: function (t) { return this.tOuvre != null && t > this.tOuvre + 0.55; },
    fini: function (t) { return this.tOuvre != null && t > this.tOuvre + 4.2; },
    rendre: function (S, t, ti) {
      var T = this.T, D = this.D, dort = D.verrou && D.verrou(), asp = S.W / S.H;
      /* les coups qui manquent viennent seuls (on ne bloque personne devant un rideau fermé) */
      if (t >= 0 && this.coups.length < 3 && t > this.coups[this.coups.length - 1] + (this.coups.length === 1 ? this.auto : 1.6)) this.frapper(t);
      var o = this.tOuvre == null ? 0 : C.doux(C.p(t, this.tOuvre, this.tOuvre + 2.3));
      var envol = this.tOuvre == null ? 0 : C.entre(C.p(t, this.tOuvre + 2.6, this.tOuvre + 4));
      /* le tremblement de la scène à chaque coup, la poussière qui tombe du lambrequin */
      var choc = 0, self = this;
      this.coups.forEach(function (c) { if (t >= c) choc += Math.exp(-(t - c) * 14) * Math.sin((t - c) * 70); });
      var feux = dort ? 0.25 : 0.7 + 0.04 * Math.sin(ti * 5.1) + 0.03 * Math.sin(ti * 13.7);
      if (this.coups.length) this.coups.forEach(function (c) { if (t >= c) feux += 0.5 * Math.exp(-(t - c) * 5); });
      var proj = this.tOuvre == null ? 0 : Math.sin(Math.PI * C.p(t, this.tOuvre + 0.4, this.tOuvre + 3.6));
      /* la lumière : une face douce d'en haut, les feux de la rampe d'en bas (chauds), le lustre du velours sur les plis */
      S.lumiere({ lum: [-0.75, 0.55, 0.55], lumc: T.lum, amb: T.amb, lp: [0, -1.35, 0.9], lpc: [feux * 0.95, feux * 0.62, feux * 0.32],
        brume: 0, rim: T.rim });
      var champ = 30, d = 1 / Math.tan(champ * Math.PI / 360);
      S.camera([choc * 0.004, choc * 0.006, d], [0, 0, 0], champ);
      S.post.dof = 0; S.post.bloom = 0.5 + proj * 0.3; S.post.seuil = 0.82; S.post.vign = 0.42; S.post.grain = 0.02;
      S.effacer();

      /* les deux pans : ils se serrent vers leur bord, leur coin bas intérieur remonte (« à l'italienne »), puis s'envolent */
      var f = 1 - 0.8 * o, A = 0.04 + 0.06 * o;
      [this.G, this.Dr].forEach(function (R) {
        var P = R.p, s = R.sens;
        for (var j = 0; j <= NY; j++) for (var i = 0; i <= NX; i++) {
          var u = i / NX, v = j / NY, k = (j * (NX + 1) + i) * 3;
          var leve = o * Math.pow(u, 1.5) * v * v;
          var x = asp - u * asp * f + leve * asp * 0.32 + envol * asp * 1.1;
          var y = BAS + 0.02 - v * (BAS + 1.04) + leve * 1.1 + choc * 0.004 * (1 - v);
          var z = A * Math.sin(2 * Math.PI * u * PLIS + s) * (1 - 0.25 * v) + 0.006 * Math.sin(ti * 0.9 + v * 3 + u * 4) * (1 - o) + 0.04 * o * Math.sin(Math.PI * u);
          P[k] = s * x; P[k + 1] = y; P[k + 2] = z;
        }
        normales(P, R.n, NX, NY);
        S.maj(R.m, P, R.n);
        S.dessiner(R.m, { mode: "papier", tex: self.tex, haut: self.haut, bump: 0.6, metal: 1, spec: [0.06, 10] }, M.id());
      });
      /* le lambrequin : il reste en place jusqu'à l'envol, puis remonte hors de la scène */
      var L = this.L, LP = L.p;
      for (var j2 = 0; j2 <= L.ny; j2++) for (var i2 = 0; i2 <= L.nx; i2++) {
        var u2 = i2 / L.nx, v2 = j2 / L.ny, k2 = (j2 * (L.nx + 1) + i2) * 3, x2 = (u2 * 2 - 1) * asp;
        var bas = BAS - 0.07 * Math.sin(Math.PI * ((u2 * 5) % 1));
        LP[k2] = x2; LP[k2 + 1] = 1.02 - v2 * (1.02 - bas) + envol * 0.75 + choc * 0.003;
        LP[k2 + 2] = 0.06 + 0.025 * Math.sin(Math.PI * ((u2 * 5) % 1)) * v2;
      }
      normales(LP, L.n, L.nx, L.ny);
      S.maj(L.m, LP, L.n);
      S.dessiner(L.m, { mode: "papier", tex: this.texL, haut: this.hautL, bump: 0.5, metal: 1, spec: [0.06, 10] }, M.id());
      /* les feux de la rampe, la poussière des coups, le projecteur qui cherche la lettre */
      var Lt = [];
      for (var q = 0; q < 9; q++) {
        var fx = ((q + 0.5) / 9 * 2 - 1) * asp * 0.92;
        Lt.push({ p: [fx, -0.99, 0.3], s: 0.07, c: [1, 0.82, 0.5, Math.min(1, feux) * (1 - envol)] });
        Lt.push({ p: [fx, -0.97, 0.28], s: 0.34, c: [1, 0.66, 0.3, Math.min(1, feux) * 0.22 * (1 - envol)] });
      }
      this.coups.forEach(function (c) {
        var tt = t - c; if (tt < 0 || tt > 2.2) return;
        self.poussiere.forEach(function (q2, n2) {
          if (n2 % 3 !== self.coups.indexOf(c)) return;
          var y = BAS - 0.02 - tt * q2.v - tt * tt * 0.25;
          Lt.push({ p: [q2.x * asp + Math.sin(tt * 2 + q2.ph) * 0.03, y, 0.12], s: q2.s, c: [1, 0.9, 0.75, 0.6 * (1 - tt / 2.2)] });
        });
      });
      if (proj > 0) Lt.push({ p: [Math.sin((1 - C.p(t, this.tOuvre + 0.4, this.tOuvre + 1.8)) * 1.4) * 0.5, 0.05, -0.2], s: 1.7, c: [1, 0.94, 0.82, proj * 0.3] });
      S.lutins(Lt, S.rond, true);
    }
  };
})()

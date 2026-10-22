/* ── LES LANTERNES · « garde le doigt sur la lanterne » ── À la tombée de la nuit, une lanterne de papier flotte sur l'eau.
   On la touche : une petite flamme prend. On garde le doigt dessus : la flamme grandit, le papier s'allume de l'intérieur,
   se gonfle, tremble, se soulève à peine (si on lâche trop tôt, elle retombe doucement ; si on ne fait rien, elle finit
   par s'allumer seule). Pleine de chaleur, elle s'envole : le regard la suit vers le ciel, et des dizaines d'autres
   lanternes montent de la rive, tout le ciel s'allume et tremble dans l'eau ; la lettre apparaît dans leur lumière
   (`plein` : la nuit s'efface, la page est derrière). Douce, sans éclat : elle convient à l'espoir (courage, guérison),
   au pardon, à ce qu'on laisse partir (rupture, brouille), au merci ; avec le croissant de lune, à la Tabaski et à l'Aïd.
   Thèmes (`THEME.motif`) : papier (le papier orangé, un crépuscule mauve), croissant (le papier d'or, la lune, la nuit bleue). */
(function () {
  var M = Theatre.M, C = Theatre.C, G = Theatre.G;
  var MOTIFS = {
    papier: { ciel: ["#0b0a1f", "#2b2050", "#9b5a6a", "#f0a868"], papier: "#f6c98a", lueur: [1.12, 0.7, 0.34], lune: false },
    croissant: { ciel: ["#050b1c", "#13254a", "#3d4a7a", "#c99a5a"], papier: "#f3d58a", lueur: [1.1, 0.8, 0.38], lune: true }
  };
  var EAU = -1.05, HOR = 0.9;   /* le niveau de l'eau ; la part du décor au-dessus de l'horizon */

  return {
    id: "lanterne",
    plein: true,
    duree: 30,
    bouton: { fr: "Allumer la lanterne", en: "Light the lantern" },
    indice: { fr: "Garde le doigt sur la lanterne", en: "Keep your finger on the lantern" },
    monter: function (S, D) {
      var A = Atelier, th = typeof THEME !== "undefined" && THEME ? THEME : {}, T = {}, k;
      var base = MOTIFS[th.motif] || MOTIFS.papier;
      for (k in base) T[k] = base[k];
      for (k in th) T[k] = th[k];
      A.matieres(S, MATIERES);
      this.T = T; this.D = D; this.tient = false; this.envol = null; this.touche = false; this.c0 = 0; this.c1 = 0; this.tB = 0; this.tH = 0;
      /* le ciel du crépuscule, la rive lointaine, la lune (pour le croissant) : un grand décor au fond */
      this.ciel = S.toile(512, 1024, function (g) {
        var hor = 1024 * HOR, d = g.createLinearGradient(0, 0, 0, hor);
        d.addColorStop(0, T.ciel[0]); d.addColorStop(0.55, T.ciel[1]); d.addColorStop(0.86, T.ciel[2]); d.addColorStop(1, T.ciel[3]);
        g.fillStyle = d; g.fillRect(0, 0, 512, hor);
        var h = C.hasard(71), i;
        for (i = 0; i < 260; i++) { g.fillStyle = "rgba(255,248,230," + (0.15 + h() * 0.6).toFixed(2) + ")"; g.fillRect(h() * 512, Math.pow(h(), 1.6) * hor * 0.8, 1.2, 1.2); }
        if (T.lune) {
          /* dans le cadre d'un téléphone : un peu à droite, haut dans le ciel du départ */
          g.fillStyle = "rgba(255,240,200,.95)"; g.beginPath(); g.arc(285, 600, 14, 0, Math.PI * 2); g.fill();
          g.globalCompositeOperation = "destination-out"; g.beginPath(); g.arc(291, 596, 12.5, 0, Math.PI * 2); g.fill();
          g.globalCompositeOperation = "source-over";
        }
        /* la rive : des collines sombres, quelques fenêtres */
        g.fillStyle = "#08060f"; g.beginPath(); g.moveTo(0, hor);
        for (var x = 0; x <= 512; x += 16) g.lineTo(x, hor - 10 - Math.sin(x * 0.013) * 14 - Math.sin(x * 0.041) * 6);
        g.lineTo(512, 1024); g.lineTo(0, 1024); g.closePath(); g.fill();
        for (i = 0; i < 30; i++) { g.fillStyle = "rgba(255,190,110," + (0.4 + h() * 0.5).toFixed(2) + ")"; g.fillRect(h() * 512, hor - 6 - h() * 10, 1.5, 1.5); }
      }, false);
      this.ciel.toile = null;
      /* l'eau : sombre, des rides plus claires près de la rive */
      this.eau = S.toile(256, 512, function (g) {
        var d = g.createLinearGradient(0, 0, 0, 512); d.addColorStop(0, T.ciel[2]); d.addColorStop(0.12, T.ciel[1]); d.addColorStop(0.45, "#0e0b1b"); d.addColorStop(1, "#050409");
        g.fillStyle = d; g.fillRect(0, 0, 256, 512);
        var h = C.hasard(5);
        for (var i = 0; i < 300; i++) { var y = Math.pow(h(), 2) * 512; g.fillStyle = "rgba(180,170,230," + (0.03 + (1 - y / 512) * 0.08).toFixed(3) + ")"; g.fillRect(h() * 256, y, 6 + h() * 30, 1); }
      }, true);
      this.eau.toile = null;
      this.fond = S.maillage(G.plan(2, 2, 1, 1));
      /* la lanterne : un ballon de papier tendu sur des baguettes, ouvert en bas, plus large en haut */
      this.corps = S.maillage(G.tour([[0.13, 0], [0.16, 0.08], [0.19, 0.22], [0.205, 0.36], [0.19, 0.47], [0.15, 0.535], [0.08, 0.575], [0.001, 0.59]], 40));
      this.papier = S.toile(256, 256, function (g) {
        var d = g.createLinearGradient(0, 0, 0, 256); d.addColorStop(0, "#ffffff"); d.addColorStop(0.55, T.papier); d.addColorStop(1, "#ffe9c4");
        g.fillStyle = d; g.fillRect(0, 0, 256, 256);
        g.fillStyle = "rgba(120,60,20,.35)";
        for (var x = 0; x < 256; x += 32) g.fillRect(x, 0, 2, 256);                       /* les baguettes */
        g.fillRect(0, 236, 256, 3); g.fillRect(0, 40, 256, 2);                              /* les cercles */
        var h = C.hasard(3);
        for (var i = 0; i < 900; i++) { g.fillStyle = "rgba(255,255,255," + (h() * 0.08).toFixed(3) + ")"; g.fillRect(h() * 256, h() * 256, 2, 2); }
        if (T.lune) { g.fillStyle = "rgba(150,90,20,.35)"; g.beginPath(); g.arc(128, 120, 22, 0, Math.PI * 2); g.fill(); g.globalCompositeOperation = "destination-out";
          g.beginPath(); g.arc(137, 114, 19, 0, Math.PI * 2); g.fill(); g.globalCompositeOperation = "source-over"; }
      }, true);
      /* les lanternes lointaines : une lueur en forme de lanterne (plus claire en bas, où brûle la flamme) */
      this.texL = S.toile(64, 96, function (g) {
        var r = g.createRadialGradient(32, 64, 2, 32, 52, 46);
        r.addColorStop(0, "rgba(255,255,230,1)"); r.addColorStop(0.35, "rgba(255,200,120,.9)"); r.addColorStop(1, "rgba(255,140,60,0)");
        g.fillStyle = r; g.beginPath(); g.moveTo(14, 20); g.lineTo(50, 20); g.quadraticCurveTo(58, 52, 46, 82); g.lineTo(18, 82); g.quadraticCurveTo(6, 52, 14, 20); g.fill();
      });
      var h = C.hasard(91), L = [];
      for (var i = 0; i < 150; i++) {
        L.push({ x: (h() * 2 - 1) * (1.5 + h() * 8), z: -1.5 - h() * 11, d: h() < 0.12 ? -6 : h() * 2.6, v: 0.32 + h() * 0.36, s: 0.1 + h() * 0.12, ph: h() * 6.3 });
      }
      this.loin = L;
    },
    geste: function () {
      this.allume = 0; this.auto = this.D.auto != null ? this.D.auto : 5;
      Atelier.Son.souffle(0, 0.5, 900, 300, 0.12); Atelier.Son.tinte(1320, 0.05, 0.025);
    },
    /* la chaleur à l'instant t, d'après le doigt : elle monte quand il est posé (0,62 par seconde), redescend doucement
       quand il est levé ; sans doigt, la lanterne finit par s'allumer seule. Calculée sur le temps, jamais par image : une
       image lente (un téléphone faible) ne ralentit pas la flamme. */
    chaleurA: function (t) {
      if (this.envol != null) return 1;
      var c = this.tient ? Math.min(1, this.c0 + 0.62 * (t - this.tB)) : Math.max(0, this.c1 - 0.2 * (t - this.tH));
      if (!this.touche && this.auto != null && t > this.auto) c = Math.max(c, C.p(t, this.auto, this.auto + 1.8));
      return c;
    },
    toucher: function (S, e) {
      if (e.t < 0 || this.envol != null) return;
      if (e.type === "bas" && !this.tient) { this.c0 = this.chaleurA(e.t); this.tB = e.t; this.tient = true; this.touche = true; }
      else if (e.type === "haut" && this.tient) { this.c1 = this.chaleurA(e.t); this.tH = e.t; this.tient = false; }
    },
    revele: function (t) { return this.envol != null && t > this.envol + 3; },
    fini: function (t) { return this.envol != null && t > this.envol + 5.6; },
    rendre: function (S, t, ti) {
      var T = this.T, D = this.D, dort = D.verrou && D.verrou(), dt = this.avant == null ? 0 : Math.max(0, Math.min(0.05, ti - this.avant));
      this.avant = ti;
      /* la chaleur : le doigt la fait monter ; sans doigt, la lanterne finit par s'allumer seule (jamais bloqué devant elle) */
      if (t >= 0 && this.envol == null) {
        this.chaleur = this.chaleurA(t);
        if (this.chaleur >= 1) {
          /* l'instant exact où elle a été pleine (pas l'image qui le constate) */
          this.envol = this.tient ? this.tB + (1 - this.c0) / 0.62 : Math.min(t, this.auto + 1.8);
          if (this.taire) this.taire();
          Atelier.Son.accord(0.05, [174.61, 261.63, 349.23, 523.25], 4.5, 0.05); Atelier.Son.souffle(0.1, 2.5, 200, 520, 0.12);
        } else if (this.tient && this.chaleur > 0.35 && this.dire && !this.encore) { this.encore = 1; this.dire({ fr: "Encore un peu…", en: "A little longer…" }); }
      }
      var ch = this.envol != null ? 1 : t < 0 ? 0 : this.chaleur, u = this.envol == null ? 0 : t - this.envol;
      var monte = this.envol == null ? ch * 0.04 : 0.04 + 0.18 * u + 0.11 * u * u;
      var rev = this.envol == null ? null : this.envol + 3, nuit = rev == null ? 1 : 1 - C.p(t, rev, rev + 1);
      /* la caméra : face à la lanterne sur l'eau ; quand elle s'envole, le regard monte avec elle */
      var leve = this.envol == null ? 0 : C.doux(C.p(u, 0, 4.5)) * Math.min(monte, 2.4);
      S.camera([Math.sin(ti * 0.2) * 0.04, -0.6 + leve * 0.5, 3.9], [0, -0.5 + leve, 0], 34);
      S.lumiere({ lum: [0, 0.5, 1], lumc: [0.2, 0.18, 0.25], amb: [0.3, 0.27, 0.35], lp: [0, -0.6 + monte, 0.5], lpc: [ch * 1.2, ch * 0.8, ch * 0.4], brume: 0, rim: [0, 0, 0] });
      S.post.dof = 0; S.post.bloom = 0.75 + ch * 0.25; S.post.seuil = 0.62; S.post.vign = 0.45; S.post.grain = 0.022;
      S.effacer();
      if (nuit > 0) {
        /* le ciel (un grand décor, loin derrière) et l'eau (un plan à plat qui le rejoint) */
        var yh = -0.85, haut = yh + HOR * 18;
        S.dessiner(this.fond, { mode: "plat", tex: this.ciel, teinte: [1, 1, 1, nuit] }, M.chaine(M.trans(0, haut - 9, -14), M.rx(Math.PI / 2), M.echelle(16, 1, 9)));
        S.dessiner(this.fond, { mode: "plat", tex: this.eau, teinte: [1, 1, 1, nuit], rep: [3, 1] }, M.chaine(M.trans(0, EAU, -5), M.echelle(16, 1, 9.5)));
      }
      /* la lanterne : éteinte, un papier dans la nuit ; chaude, elle brille de l'intérieur et tremble */
      var vib = this.envol == null ? ch * ch * 0.012 * Math.sin(ti * 31) : 0, gonfle = 1 + ch * 0.06;
      var x = Math.sin(u * 0.9) * 0.08 * Math.min(1, u), y = EAU + 0.06 + monte, sway = Math.sin(ti * 1.3) * 0.04 + vib;
      var teinte = [C.mix(0.3, T.lueur[0], ch), C.mix(0.26, T.lueur[1], ch), C.mix(0.3, T.lueur[2], ch), nuit > 0 || this.envol != null ? 1 : 1];
      var m = M.chaine(M.trans(x, y, 0.4), M.rz(sway), M.ry(ti * 0.15), M.echelle(0.5 * gonfle, 0.5 * gonfle * (1 + vib), 0.5 * gonfle));
      if (y < 4.5) S.dessiner(this.corps, { mode: "plat", tex: this.papier, teinte: teinte }, m);
      var Ls = [], Rf = [], Fl = [], flamme = t < 0 ? 0 : 0.25 + ch * 0.75;
      if (flamme > 0 && y < 4.5) {
        Fl.push({ p: [x, y + 0.012, 0.4], s: 0.035 + ch * 0.03, c: [1, 0.85, 0.5, flamme] });
        Fl.push({ p: [x, y + 0.15, 0.38], s: 0.45 + ch * 0.35, c: [1, 0.6, 0.25, ch * 0.2] });
      }
      /* les autres lanternes : quelques-unes déjà loin dans le ciel, puis des dizaines qui montent de la rive */
      var self = this;
      this.loin.forEach(function (l, i) {
        var dep = l.d < 0 ? -99 : (self.envol == null ? 1e9 : self.envol + 0.4 + l.d);
        var tt = t - dep; if (tt < 0) return;
        var yy = l.d < 0 ? 0.6 + (i % 5) * 0.5 + Math.sin(ti * 0.1 + l.ph) * 0.05 : EAU + 0.15 + tt * l.v + tt * tt * 0.01;
        var a = Math.min(1, tt * 0.8) * (l.d < 0 ? 0.6 : 0.95);
        var p = [l.x + Math.sin(ti * 0.4 + l.ph) * 0.12, yy, l.z];
        Ls.push({ p: p, s: l.s, h: 1.35, c: [1, 0.9, 0.75, a] });
        if (nuit > 0 && yy > EAU) Rf.push({ p: [p[0], 2 * EAU - yy, p[2]], s: l.s * 1.2, h: 0.5, ax: [1, 0, 0], ay: [0, 1, 0], c: [1, 0.7, 0.4, a * 0.3 * nuit] });
      });
      /* le reflet de la lanterne dans l'eau, tant qu'elle est près */
      if (ch > 0 && nuit > 0) for (var q = 0; q < 10; q++) {
        var ry = EAU - 0.03 - q * 0.04 - monte * 0.6; if (ry < EAU - 1.2) break;
        Rf.push({ p: [x + Math.sin(q * 2.1 + ti * 3) * 0.03, ry, 0.42], s: 0.18 + Math.sin(q + ti * 4) * 0.05, h: 0.2, ax: [1, 0, 0], ay: [0, 1, 0], c: [1, 0.65, 0.3, ch * 0.4 * (1 - q / 10) * nuit] });
      }
      var gl = S.gl;
      gl.disable(gl.DEPTH_TEST); S.lutins(Rf, S.rond, true); gl.enable(gl.DEPTH_TEST);
      S.lutins(Fl, S.rond, true);
      S.lutins(Ls, this.texL, true);
    }
  };
})()

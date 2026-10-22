/* ── LES PORTES BRODÉES · la Saint-Valentin (d'après la vidéo 3964bcf0 de Mongazi) ──
   Deux battants brodés de fleurs, aux bords festonnés, tenus fermés par un cœur de cire. On touche : le cœur bat
   deux fois, se fend, chaque moitié part avec sa porte, les portes pivotent sur leurs gonds, une lumière rose monte
   de l'intérieur, des pétales s'envolent, et la carte se lève. */
({
  id: "portes",
  nom: { fr: "Les portes brodées", en: "The embroidered doors" },
  duree: 3.0,
  revele: 2.6,
  monter: function (S, D) {
    var A = Atelier, G = Theatre.G, C = Theatre.C;
    A.matieres(S, MATIERES);
    this.D = D;
    var hab = D.HAB || {}, pap = hab.papier || "creme", P = A.PAPIERS[pap] || A.PAPIERS.creme;
    this.table = A.Table(S, "#26161f");
    this.bokeh = A.Bokeh(S, 10, 61, [[1, 0.6, 0.7], [1, 0.8, 0.85], [1, 0.72, 0.5]]);
    this.texC = A.carte(S, D, pap, hab.cire || "rose");
    this.texInt = A.papier(S, pap, 21);
    var W = 1.9, H = 1.25;
    this.W = W; this.H = H;
    this.fond = S.maillage(G.plan(W, H, 1, 1));
    this.carte = S.maillage(G.plan(1.42, 0.92, 1, 1));
    /* un battant : un plan dont l'arête x = 0 est la charnière ; la broderie court le long du bord libre */
    var plan = G.plan(W / 2, H, 1, 1);
    for (var k = 0; k < plan.p.length; k += 3) plan.p[k] += W / 4;  /* x de 0 (gond) à W/2 (bord libre) */
    this.battant = S.maillage(plan);
    function broderie(g, w, h, relief) {
      var hs = C.hasard(7);
      if (!relief) {
        var d = g.createLinearGradient(0, 0, w, 0); d.addColorStop(0, P.b); d.addColorStop(1, P.a);
        g.fillStyle = d; g.fillRect(0, 0, w, h);
      } else { g.fillStyle = "#000"; g.fillRect(0, 0, w, h); }
      /* deux tiges qui ondulent le long du bord libre (à droite de la texture), la seconde plus fine */
      g.lineCap = "round";
      [[0.7, 2.2, 0.06], [0.5, 1.3, 0.05]].forEach(function (tg) {
        g.strokeStyle = relief ? "#fff" : "#8fb39a"; g.lineWidth = relief ? tg[1] + 2 : tg[1];
        g.beginPath();
        for (var y = -10; y <= h + 10; y += 6) { var x = w * tg[0] + Math.sin(y * 0.045 + tg[0] * 5) * w * tg[2]; if (y < 0) g.moveTo(x, y); else g.lineTo(x, y); }
        g.stroke();
      });
      for (var i = 0; i < 9; i++) {
        var yy = (i + 0.5) * h / 9, xx = w * 0.7 + Math.sin(yy * 0.045 + 3.5) * w * 0.06, s = i % 2 ? 1 : -1;
        /* deux feuilles */
        g.fillStyle = relief ? "#ddd" : "#9cc0a6";
        for (var f = 0; f < 2; f++) {
          g.save(); g.translate(xx, yy + (f ? 14 : -10)); g.rotate((f ? 0.9 : -0.6) * s);
          g.beginPath(); g.ellipse(s * 14, 0, 13, 5.5, 0, 0, Math.PI * 2); g.fill(); g.restore();
        }
        /* une rose : des pétales en spirale */
        var rx = xx - s * 24, rose = i % 3 === 0 ? "#c4566a" : "#e39bb0";
        for (var pet = 0; pet < 6; pet++) {
          g.fillStyle = relief ? "#fff" : (pet % 2 ? rose : "#f6d3db");
          g.beginPath(); g.arc(rx + Math.cos(pet * 1.1) * (8 - pet), yy + Math.sin(pet * 1.1) * (8 - pet), 9 - pet, 0, Math.PI * 2); g.fill();
        }
        /* des points de fil d'or */
        g.fillStyle = relief ? "#bbb" : "#c9a227";
        for (var pt = 0; pt < 5; pt++) { g.beginPath(); g.arc(xx + (hs() - 0.5) * 50, yy + (hs() - 0.5) * 40, 1.8, 0, Math.PI * 2); g.fill(); }
      }
      /* le bord libre festonné : des morsures rondes (transparentes, la découpe les enlève) */
      g.globalCompositeOperation = "destination-out";
      for (var b = 0; b < h; b += 36) { g.beginPath(); g.arc(w + 4, b + 18, 15, 0, Math.PI * 2); g.fill(); }
      g.globalCompositeOperation = "source-over";
    }
    this.texB = S.toile(256, 512, function (g, w, h) { broderie(g, w, h, false); });
    this.hautB = S.toile(256, 512, function (g, w, h) { broderie(g, w, h, true); });
    this.texDedans = S.toile(64, 64, function (g) { var d = g.createLinearGradient(0, 0, 64, 64); d.addColorStop(0, "#f3c9d2"); d.addColorStop(1, "#e3a4b4"); g.fillStyle = d; g.fillRect(0, 0, 64, 64); });
    /* le cœur de cire : deux moitiés le long d'une fêlure en zigzag */
    var coeur = [];
    for (var i2 = 0; i2 <= 48; i2++) {
      var tt = Math.PI * i2 / 48;  /* de la pointe du bas (0) au creux du haut (π), côté droit */
      coeur.push([16 * Math.pow(Math.sin(tt), 3) / 17, (13 * Math.cos(tt) - 5 * Math.cos(2 * tt) - 2 * Math.cos(3 * tt) - Math.cos(4 * tt)) / 17]);
    }
    var fel = [[0, coeur[48][1]], [0.05, 0.22], [-0.04, 0.02], [0.05, -0.2], [-0.03, -0.45], [0, coeur[0][1]]];
    function moitie(s) {
      var c = coeur.map(function (q) { return [q[0] * s, -q[1]]; });
      var f = fel.slice().reverse().map(function (q) { return [q[0], -q[1]]; });
      return G.extrusion(c.concat(f.slice(1, -1)), 0.16, 0.03, 2);
    }
    this.mCoeurD = S.maillage(moitie(1)); this.mCoeurG = S.maillage(moitie(-1));
    var ini = (D.de || "M").trim().charAt(0).toUpperCase() || "M";
    this.hautCoeur = S.toile(256, 256, function (g) {
      g.fillStyle = "#000"; g.fillRect(0, 0, 256, 256); g.fillStyle = "#fff";
      g.font = "120px " + A.SERIF; g.textAlign = "center"; g.textBaseline = "middle";
      for (var k2 = 0; k2 < 7; k2++) { g.globalAlpha = 0.2; g.fillText(ini, 128 + Math.cos(k2) * 2, 128 + Math.sin(k2) * 2); }
      g.globalAlpha = 0.5; g.fillText(ini, 128, 128);
    });
    var h = C.hasard(53), pet = [];
    for (var j = 0; j < 46; j++) pet.push({ a: h() * 6.283, v: 0.2 + h() * 0.7, up: 1.6 + h() * 1.6, s: 0.07 + h() * 0.06, ph: h() * 6.3, sp: (h() - 0.5) * 6, d: h() * 0.5,
      c: [[0.70, 0.26, 0.31], [0.85, 0.54, 0.63], [0.94, 0.78, 0.81], [0.55, 0.18, 0.22]][j % 4] });
    this.petales = pet;
    this.texPetale = S.toile(64, 64, function (g) {
      var r = g.createRadialGradient(26, 30, 2, 32, 32, 30); r.addColorStop(0, "rgba(255,255,255,1)"); r.addColorStop(1, "rgba(255,255,255,.75)");
      g.fillStyle = r; g.beginPath(); g.ellipse(32, 32, 30, 17, 0, 0, Math.PI * 2); g.fill();
    });
  },
  rendre: function (S, t, ti) {
    var M = Theatre.M, C = Theatre.C, self = this;
    var cad = this.D.cadre || { x: S.W / 2, y: S.H * 0.47, l: Math.min(S.W * 0.78, 340) };
    var dort = this.D.verrou && this.D.verrou();
    var o = Math.max(0, t);
    /* le cœur bat deux fois avant de céder */
    var bat = t < 0 ? (dort ? 0 : 0.012 * Math.max(0, Math.sin(ti * 2.4)) ) : 0.07 * Math.exp(-Math.pow((o - 0.04) / 0.05, 2)) + 0.09 * Math.exp(-Math.pow((o - 0.22) / 0.05, 2));
    var lueur = t < 0 ? (dort ? 0 : 0.08) : Math.min(1, o / 0.2) * (1 - C.p(o, 0.4, 0.8));
    var thG = C.sort(C.p(o, 0.34, 1.4)) * 2.9, thD = C.sort(C.p(o, 0.4, 1.46)) * 2.9;
    var rose = t < 0 ? 0 : C.p(o, 0.45, 1.2);
    var leve = C.doux(C.p(o, 1.45, 2.45)), plonge = C.doux(C.p(o, 1.55, 2.85));

    /* la caméra : le cœur bat, elle s'approche ; les portes s'ouvrent, elle plonge ENTRE elles vers la lumière */
    var champ = 30, d0 = S.distance(2.12, cad.l, champ), d1 = S.distance(1.5, S.W * 0.98, champ);
    var approche = t < 0 ? 0 : C.sort(C.p(o, 0, 0.3)) * 0.12 * (1 - C.p(o, 0.4, 0.9));
    var entre = t < 0 ? 0 : C.doux(C.p(o, 0.45, 1.6));
    var el = C.mix(55 + Math.sin(ti * 0.4) * 1.4 - approche * 12 + entre * 14, 89, plonge) * Math.PI / 180, az = Math.sin(ti * 0.3) * 0.05 * (1 - plonge);
    var cible = [0, C.mix(0, 0.3, leve), 0.02], d = C.mix(d0 * (1 - approche - entre * 0.22), d1, plonge);
    S.camera([Math.sin(az) * d * Math.cos(el), cible[1] + d * Math.sin(el), cible[2] + Math.cos(az) * d * Math.cos(el)], cible, champ,
      C.mix(cad.x, S.W / 2, plonge), C.mix(cad.y, S.H / 2, plonge));
    S.post.dof = C.mix(0.85, 0.3, plonge); S.post.bloom = 0.6 + rose * 0.15 * (1 - leve);
    var fl = 1 + 0.05 * Math.sin(ti * 7.7);
    S.lumiere({ lum: [-0.4, 0.86, 0.45], lumc: [0.86, 0.78, 0.76], amb: [0.13, 0.1, 0.13],
      lp: [0, 0.5, 0], lpc: [0.6 * fl + rose * 0.7, 0.45 * fl + rose * 0.3, 0.45 * fl + rose * 0.38], brume: 0.6 });

    S.effacer();
    this.table.dessiner();
    S.ombre(0, 0, 0.02, 1.22, 0.86, 0.55);
    /* l'intérieur : le fond, la carte qui se lève */
    S.dessiner(this.fond, { mode: "papier", tex: this.texInt, rep: [1.2, 0.8], teinte: [0.98, 0.9, 0.9, 1] }, M.trans(0, 0.001, 0));
    S.dessiner(this.carte, { mode: "papier", tex: this.texC }, M.chaine(M.trans(0, 0.004 + leve * 0.3, 0), M.rx(-leve * 0.1)));
    /* les deux portes, chacune avec sa moitié de cœur ; la gauche tourne autour de son gond, la droite en miroir */
    var mc = S.matcaps["cire-" + ((this.D.HAB || {}).cire || "rose")] || S.matcaps["cire-rose"] || S.matcaps["cire-bordeaux"];
    var ecart = t < 0 ? 0 : C.p(o, 0.28, 0.36) * 0.012;
    [[-1, thG, this.mCoeurG], [1, thD, this.mCoeurD]].forEach(function (b) {
      var s = b[0], th = b[1];
      var m = s < 0 ? M.chaine(M.trans(-self.W / 2, 0.006, 0), M.rz(th)) : M.chaine(M.trans(self.W / 2, 0.006, 0), M.ry(Math.PI), M.rz(th));
      S.dessiner(self.battant, { mode: "papier", tex: self.texB, coupe: 0.5, emis: [0.06, 0.05, 0.05] }, M.mul(m, M.trans(0, 0.004, 0)));
      S.dessiner(self.battant, { mode: "papier", tex: self.texDedans, coupe: 0, teinte: [1, 0.95, 0.96, 1] }, m);
      /* la moitié du cœur, posée sur le bord libre du battant (en miroir pour la porte droite) */
      var e = M.echelle(0.3 * (1 + bat));
      var mh = s < 0 ? M.chaine(m, M.trans(self.W / 2 - ecart, 0.005, 0), e) : M.chaine(m, M.trans(self.W / 2 - ecart, 0.005, 0), M.ry(Math.PI), e);
      S.dessiner(b[2], { mode: "matcap", tex: mc, haut: self.hautCoeur, bump: 2.2, teinte: [1.15, 1.12, 1.12, 1], emis: [lueur * 0.5, lueur * 0.2, lueur * 0.25] }, mh);
    });
    /* la lueur rose de l'intérieur, l'éclair de la fêlure, puis les pétales qui s'envolent et retombent */
    var L = [];
    /* la lueur rose de l'intérieur : elle doit laisser lire la carte (à 0,45, elle brûlait le prénom) */
    if (rose > 0) L.push({ p: [0, 0.32, -0.15], s: 2.2 * rose, c: [1, 0.5, 0.62, 0.2 * rose * (1 - leve * 0.8)] });
    var flash = t < 0 ? 0 : Math.max(0, 1 - Math.abs(o - 0.3) / 0.16);
    if (flash > 0) L.push({ p: [0, 0.12, 0], s: 0.9 + flash * 1.2, c: [1, 0.8, 0.85, flash * 0.8] });
    S.lutins(L, S.rond, true);
    if (t >= 0) {
      var Q = [];
      this.petales.forEach(function (q) {
        var u = o - 0.5 - q.d; if (u <= 0 || u > 2.6) return;
        var y = 0.05 + q.up * u - 1.5 * u * u; if (y < 0.012) y = 0.012;
        var r = q.ph + u * q.sp, x = Math.cos(q.a) * q.v * u * 1.2, z = Math.sin(q.a) * q.v * u * 0.8;
        Q.push({ p: [x, y, z], s: q.s, h: 0.6, c: [q.c[0], q.c[1], q.c[2], 1 - C.p(u, 2.1, 2.6)],
          ax: [Math.cos(r), Math.sin(r * 0.8) * 0.35, Math.sin(r)], ay: [-Math.sin(r) * 0.9, Math.cos(r * 0.6) * 0.45, Math.cos(r) * 0.9] });
      });
      S.lutins(Q, this.texPetale, false);
    }
    this.bokeh.dessiner(ti, 1 - plonge * 0.7);
  },
  geste: function () {
    var Son = Atelier.Son;
    Son.toc(0, 70, 0.4); Son.toc(0.18, 66, 0.45);       /* le cœur : deux battements sourds */
    setTimeout(function () { Son.craque(); }, 280);       /* la cire se fend, le papier glisse */
    Son.souffle(0.36, 0.9, 400, 1600, 0.14);              /* l'air des portes */
    Son.tinte(1568, 0.62, 0.05); Son.tinte(2093, 0.74, 0.04);
  }
})

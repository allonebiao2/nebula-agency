/* ── LE COLLIER DE PERLES · le mariage (d'après la vidéo 971ee54d de Mongazi) ──
   Une pochette à quatre rabats, ceinte d'un double rang de perles et de grains d'or, tenue par un cachet. On
   touche : le cachet casse, le collier se dénoue, les perles roulent sur la table (les plus proches d'abord), les
   quatre rabats doublés de damas s'ouvrent l'un après l'autre, et la carte se lève vers celle qui lit. */
({
  id: "perles",
  nom: { fr: "Le collier de perles", en: "The pearl necklace" },
  duree: 3.3,
  revele: 2.85,
  monter: function (S, D) {
    var A = Atelier, G = Theatre.G, C = Theatre.C;
    A.matieres(S, MATIERES);
    this.D = D;
    var hab = D.HAB || {}, pap = hab.papier || "creme", P = A.PAPIERS[pap] || A.PAPIERS.creme;
    this.table = A.Table(S, "#1b1620");
    this.texP = A.papier(S, pap, 13); this.texD = A.doublure(S, hab.cire || "bordeaux"); this.texC = A.carte(S, D, pap, hab.cire || "bordeaux");
    this.teinteP = A.rvb(P.a); this.teinteDos = A.rvb(P.dos);
    var W = 1.9, H = 1.25, k = 0.06;
    this.W = W; this.H = H;
    this.dos = S.maillage(G.plan(W, H, 1, 1));
    this.carte = S.maillage(G.plan(1.5, 0.98, 1, 1));
    /* les quatre rabats, chacun dessiné depuis sa charnière (axe X local), pointe vers le centre */
    var long = S.maillage(G.extrusion([[-W / 2, 0], [W / 2, 0], [0, H / 2 + k]], 0.003, 0));
    var court = S.maillage(G.extrusion([[-H / 2, 0], [H / 2, 0], [0, W / 2 + k]], 0.003, 0));
    var M = Theatre.M;
    /* l'ordre de fermeture : bas, haut, gauche, droite (la droite dessus) ; on ouvre à l'envers */
    this.rabats = [
      { m: court, base: M.chaine(M.trans(W / 2, 0.013, 0), M.ry(-Math.PI / 2)), de: 0.72, a: 1.32 },
      { m: court, base: M.chaine(M.trans(-W / 2, 0.010, 0), M.ry(Math.PI / 2)), de: 0.92, a: 1.52 },
      { m: long, base: M.trans(0, 0.007, -H / 2), de: 1.12, a: 1.72 },
      { m: long, base: M.chaine(M.trans(0, 0.004, H / 2), M.ry(Math.PI)), de: 1.32, a: 1.92 }
    ];
    this.cachet = A.Cachet(S, D);
    /* le collier : deux rangs, perles et grains d'or alternés, qui débordent sur la table */
    this.perleG = S.maillage(G.sphere(0.05, 14)); this.perleP = S.maillage(G.sphere(0.032, 12)); this.grain = S.maillage(G.sphere(0.018, 8));
    var h = C.hasard(29), perles = [];
    [[0, 0.05, 0.14], [0.085, 0.032, 0.095]].forEach(function (rang, ri) {
      for (var x = -1.04; x <= 1.04; x += rang[2]) {
        if (Math.abs(x) < 0.17) continue;
        [[x, rang[1], ri === 0 ? "G" : "P"], [x + rang[2] / 2, 0.018, "o"]].forEach(function (q) {
          if (Math.abs(q[0]) < 0.17 || Math.abs(q[0]) > 1.06) return;
          var b2 = Math.max(0, Math.abs(q[0]) - W / 2);
          perles.push({ x: q[0], z: rang[0] + (h() - 0.5) * 0.006, r: q[1], type: q[2],
            y: Math.max(q[1], 0.017 + q[1] - b2 * 0.9),
            tr: 0.36 + (Math.abs(q[0]) - 0.17) * 0.32 + h() * 0.08,
            loin: 0.35 + h() * 1.05, dz: (h() - 0.5) * 0.9, saut: 0.02 + h() * 0.05, ph: h() * 6.3 });
        });
      }
    });
    this.perles = perles;
    var et = [];
    for (var i = 0; i < 40; i++) et.push({ a: h() * 6.283, v: 0.8 + h() * 1.6, y: 0.5 + h() * 1.4, s: 0.025 + h() * 0.045, d: h() * 0.1 });
    this.etincelles = et;
  },
  rendre: function (S, t, ti) {
    var M = Theatre.M, C = Theatre.C, self = this;
    var cad = this.D.cadre || { x: S.W / 2, y: S.H * 0.47, l: Math.min(S.W * 0.78, 340) };
    var dort = this.D.verrou && this.D.verrou();
    var o = Math.max(0, t);
    var eclat = t < 0 ? 0 : C.p(o, 0.28, 1.1);
    var lueur = t < 0 ? (dort ? 0 : 0.1 + 0.06 * Math.sin(ti * 2.2)) : C.p(o, 0, 0.18) * (1 - C.p(o, 0.3, 0.65));
    var leve = C.doux(C.p(o, 1.9, 2.8)), plonge = C.doux(C.p(o, 1.95, 3.05));

    var champ = 30, d0 = S.distance(2.15, cad.l, champ), d1 = S.distance(1.6, S.W * 0.98, champ);
    var el = C.mix(54 + Math.sin(ti * 0.4) * 1.5, 89, plonge) * Math.PI / 180, az = Math.sin(ti * 0.3) * 0.06 * (1 - plonge);
    var cible = [0, C.mix(0, 0.34, leve), C.mix(0.02, 0, plonge)], d = C.mix(d0, d1, plonge);
    S.camera([cible[0] + Math.sin(az) * d * Math.cos(el), cible[1] + d * Math.sin(el), cible[2] + Math.cos(az) * d * Math.cos(el)], cible, champ,
      C.mix(cad.x, S.W / 2, plonge), C.mix(cad.y, S.H / 2, plonge));
    var fl = 1 + 0.06 * Math.sin(ti * 8.3) + 0.03 * Math.sin(ti * 21.1);
    S.lumiere({ lum: [-0.4, 0.86, 0.45], lumc: [0.86, 0.8, 0.74], amb: [0.13, 0.11, 0.15],
      lp: [-1.5, 1.2, 1.1], lpc: [0.8 * fl + lueur * 0.4, 0.68 * fl + lueur * 0.2, 0.52 * fl + lueur * 0.15], brume: 0.6 });

    S.effacer();
    this.table.dessiner();
    S.ombre(0, 0, 0.03, 1.22, 0.86, 0.55);
    S.dessiner(this.dos, { mode: "papier", tex: this.texP, teinte: this.teinteDos, rep: [1.3, 0.9] }, M.trans(0, 0.001, 0));
    /* la carte au fond de la pochette, qui se lève et se tourne vers la caméra */
    S.dessiner(this.carte, { mode: "papier", tex: this.texC }, M.chaine(M.trans(0, 0.003 + leve * 0.34, 0), M.rx(-leve * 0.12)));
    this.rabats.forEach(function (r) {
      var th = C.doux(C.p(o, r.de, r.a)) * Math.PI * 0.985;
      var dessous = th > Math.PI / 2;
      S.dessiner(r.m, dessous ? { mode: "papier", tex: self.texD, rep: [3, 3] } : { mode: "papier", tex: self.texP, teinte: self.teinteP, rep: [1.3, 0.9] },
        M.chaine(r.base, M.rx(-th)));
    });
    /* le collier : chaque perle part à son heure, roule hors de la pochette, saute, s'arrête sur la table */
    var mP = S.matcaps.perle, mO = S.matcaps.or;
    this.perles.forEach(function (q) {
      var u = t < 0 ? -1 : o - q.tr, x = q.x, y = q.y, z = q.z;
      if (u > 0) {
        var k = 1 - Math.exp(-u / 0.42), s = Math.sign(q.x);
        x = q.x + s * q.loin * k; z = q.z + q.dz * k;
        var horsBord = Math.abs(x) > self.W / 2 + 0.02;
        y = horsBord ? q.r + q.saut * Math.abs(Math.sin(u * 9 + q.ph)) * Math.exp(-u * 3.2) : 0.017 + q.r;
      } else if (t < 0) {
        y += 0.002 * Math.sin(ti * 1.3 + q.x * 3);
      }
      var mesh = q.type === "G" ? self.perleG : q.type === "P" ? self.perleP : self.grain;
      S.dessiner(mesh, { mode: "matcap", tex: q.type === "o" ? mO : mP, teinte: q.type === "o" ? [1.1, 1.05, 1, 1] : [1.06, 1.04, 1.02, 1] }, M.trans(x, y, z));
    });
    if (eclat < 1) this.cachet.dessiner(M.chaine(M.trans(0, 0.02, 0), M.echelle(0.235 * (t < 0 ? 1 + 0.015 * Math.sin(ti * 1.7) : 1))), lueur, eclat, [0, 2.0, 2.4]);
    /* les lumières : le reflet qui court sur le rang au repos, l'éclair et les étincelles au toucher */
    var L = [];
    if (t < 0 && !dort) {
      var ph = (ti * 0.55) % 3, xs = -1.1 + ph * 1.2;
      if (Math.abs(xs) < 1.05 && Math.abs(xs) > 0.17) L.push({ p: [xs, 0.07, 0], s: 0.16, c: [1, 0.95, 0.85, 0.55 * Math.sin(Math.PI * Math.min(1, ph / 1.8))] });
    }
    var flash = t < 0 ? 0 : Math.max(0, 1 - Math.abs(o - 0.3) / 0.22);
    if (flash > 0) L.push({ p: [0, 0.1, 0], s: 1.0 + flash * 1.5, c: [1, 0.86, 0.72, flash * 0.85] });
    if (t >= 0) this.etincelles.forEach(function (e) {
      var tt = o - 0.28 - e.d; if (tt <= 0 || tt > 1) return;
      L.push({ p: [Math.cos(e.a) * e.v * tt, 0.06 + e.y * tt - 1.3 * tt * tt, Math.sin(e.a) * e.v * tt * 0.8], s: e.s * (2 - tt), c: [1, 0.9, 0.7, 1 - tt] });
    });
    S.lutins(L, S.rond, true);
  },
  geste: function () {
    var Son = Atelier.Son, p = this.perles || [];
    Son.craque();
    /* les perles qui tombent : quelques-unes seulement font du bruit (on n'entend pas soixante billes) */
    for (var i = 0; i < p.length; i += 4) Son.toc(p[i].tr + 0.22 + (i % 3) * 0.03, 2600 + (i * 37) % 1400, 0.035);
    [0.72, 0.92, 1.12, 1.32].forEach(function (q) { Son.souffle(q, 0.45, 600, 2200, 0.12); });
  }
})

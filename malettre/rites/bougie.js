/* ── LA BOUGIE · l'anniversaire ──
   Une bougie torsadée brûle sur le cachet ; c'est elle qui éclaire la lettre (sa flamme est une vraie lumière, elle
   vacille sur le papier). Avant l'heure, elle est éteinte ; à l'heure, elle s'allume. On souffle (on touche) : la
   flamme se couche et meurt, un ruban de fumée monte, un temps de noir, puis la lumière revient d'un coup avec une
   gerbe de confettis, la bougie bascule, le cachet cède, la lettre sort. */
({
  id: "bougie",
  nom: { fr: "La bougie", en: "The candle" },
  bouton: { fr: "Souffler la bougie", en: "Blow out the candle" },
  duree: 3.0,
  revele: 2.55,
  monter: function (S, D) {
    var A = Atelier, G = Theatre.G, C = Theatre.C;
    A.matieres(S, MATIERES);
    this.D = D;
    var hab = D.HAB || {}, cire = A.CIRES[hab.cire] || A.CIRES.bordeaux;
    this.table = A.Table(S);
    this.bokeh = A.Bokeh(S, 10, 77);
    this.env = A.Enveloppe(S, D);
    this.cachet = A.Cachet(S, D);
    /* la bougie : un fût torsadé (crème et couleur de la cire), une mèche */
    this.fut = S.maillage(G.tour([[0.046, 0], [0.046, 0.6], [0.042, 0.618], [0.016, 0.625]], 22));
    this.meche = S.maillage(G.tour([[0.006, 0.61], [0.006, 0.68], [0.004, 0.69]], 6));
    this.texFut = S.toile(64, 256, function (g) {
      g.fillStyle = "#f6efe2"; g.fillRect(0, 0, 64, 256);
      g.fillStyle = cire.cire;
      for (var y = -64; y < 320; y += 40) { g.beginPath(); g.moveTo(0, y); g.lineTo(64, y + 32); g.lineTo(64, y + 46); g.lineTo(0, y + 14); g.closePath(); g.fill(); }
    }, true);
    /* la flamme : une goutte de lumière (cœur blanc, jaune, bord orangé) */
    this.texFlamme = S.toile(64, 128, function (g) {
      var r = g.createRadialGradient(32, 92, 2, 32, 80, 52);
      r.addColorStop(0, "rgba(255,255,245,1)"); r.addColorStop(0.25, "rgba(255,226,140,.95)"); r.addColorStop(0.6, "rgba(255,140,40,.55)"); r.addColorStop(1, "rgba(255,90,20,0)");
      g.fillStyle = r; g.beginPath(); g.moveTo(32, 4); g.bezierCurveTo(52, 50, 60, 84, 32, 124); g.bezierCurveTo(4, 84, 12, 50, 32, 4); g.fill();
    });
    var h = C.hasard(41), fumee = [], conf = [], cols = ["#c9a227", "#b2434e", "#4f8a6f", "#e0c266", "#f4ede0", "#d88aa0"];
    for (var i = 0; i < 26; i++) fumee.push({ d: i * 0.055, ph: h() * 6.3, w: 0.6 + h() * 0.8 });
    for (var j = 0; j < 90; j++) conf.push({ a: h() * 6.283, v: 0.5 + h() * 1.5, up: 2.0 + h() * 2.2, s: 0.05 + h() * 0.05, c: A.rvb(cols[j % cols.length]), sp: (h() - 0.5) * 14, ph: h() * 6.3 });
    this.fumee = fumee; this.conf = conf;
  },
  rendre: function (S, t, ti) {
    var M = Theatre.M, C = Theatre.C, env = this.env;
    var cad = this.D.cadre || { x: S.W / 2, y: S.H * 0.47, l: Math.min(S.W * 0.78, 340) };
    var dort = this.D.verrou && this.D.verrou();
    var o = Math.max(0, t);
    /* la flamme : éteinte avant l'heure, vive au repos, couchée puis morte au souffle */
    var vie = dort ? 0 : t < 0 ? 1 : 1 - C.p(o, 0.08, 0.36);
    var couche = t < 0 ? 0 : C.sort(C.p(o, 0, 0.22));
    var fl = 1 + 0.09 * Math.sin(ti * 11.3) + 0.05 * Math.sin(ti * 27.1) + 0.03 * Math.sin(ti * 47.9);
    var lumiere = t < 0 ? 0.35 : C.p(o, 0.62, 0.9); /* la pièce : sombre (la bougie seule), puis la lumière revient */
    var eclat = t < 0 ? 0 : C.p(o, 0.66, 1.45);
    var ouvre = C.doux(C.p(o, 0.8, 1.55)), sort = C.p(o, 1.35, 2.5), plonge = C.doux(C.p(o, 1.5, 2.85));

    /* la caméra : elle s'approche de la flamme pour souffler, reste dans le noir, puis recule d'un coup dans la fête */
    var champ = 30, d0 = S.distance(2.12, cad.l, champ), d1 = S.distance(1.72, S.W * 0.98, champ);
    var souffle = t < 0 ? 0 : C.sort(C.p(o, 0, 0.3)) * (1 - C.sort(C.p(o, 0.6, 1.2)));
    var fete = t < 0 ? 0 : Math.sin(Math.PI * C.p(o, 0.62, 1.9)) * (1 - plonge);
    var el = C.mix(50 + Math.sin(ti * 0.42) * 1.4 - souffle * 14, 89, plonge) * Math.PI / 180, az = Math.sin(ti * 0.31) * 0.05 * (1 - plonge) + fete * 0.18;
    var cz = C.mix(0.02, -env.H * 0.86, C.sort(sort));
    var cible = [0, C.mix(0.05, 0.16, sort) + souffle * 0.35, C.mix(C.mix(0.04, env.zr - 0.06, souffle), cz, plonge)];
    var d = C.mix(d0 * (1 - souffle * 0.42 + fete * 0.1), d1, plonge);
    S.camera([cible[0] + Math.sin(az) * d * Math.cos(el), cible[1] + d * Math.sin(el), cible[2] + Math.cos(az) * d * Math.cos(el)], cible, champ,
      C.mix(cad.x, S.W / 2, plonge), C.mix(cad.y, S.H / 2, plonge));
    S.post.dof = C.mix(0.9, 0.35, plonge); S.post.bloom = 0.75;

    /* la mèche, au-dessus du cachet posé sur la pointe du rabat */
    var sz = env.zr - 0.06, base = [0, 0.016 + 0.235 * 0.27, sz], mech = [base[0], base[1] + 0.67, base[2]];
    var puissance = vie * fl;
    S.lumiere({ lum: [-0.45, 0.85, 0.5], lumc: [0.82 * lumiere, 0.76 * lumiere, 0.68 * lumiere], amb: [0.07 + 0.06 * lumiere, 0.06 + 0.05 * lumiere, 0.09 + 0.05 * lumiere],
      lp: [mech[0] - couche * 0.05, mech[1] + 0.05, mech[2] - couche * 0.12], lpc: [1.7 * puissance, 1.05 * puissance, 0.45 * puissance], brume: 0.55 });

    S.effacer();
    this.table.dessiner();
    S.ombre(0, 0, 0.04, 1.32, 0.9, 0.5);
    env.dessiner(M.id(), ouvre, sort);
    if (eclat < 1) this.cachet.dessiner(M.chaine(M.trans(0, 0.016, sz), M.echelle(0.27)), 0, eclat, [0, 2.0, 2.4]);
    /* la bougie : droite, puis elle bascule et tombe sur la table quand la cire cède */
    var tombe = t < 0 ? 0 : C.p(o, 0.66, 1.25), bascule = C.entre(tombe) * 1.45;
    var mb = M.chaine(M.trans(base[0] + tombe * 0.55, base[1] - C.entre(tombe) * (base[1] - 0.034), base[2] + tombe * 0.22), M.rz(-bascule), M.rx(tombe * 0.3));
    /* la cire de la bougie luit près de sa flamme (sa lumière vient d'en haut : sans cela, le fût paraissait noir) */
    S.dessiner(this.fut, { mode: "papier", tex: this.texFut, rep: [1, 1], emis: [0.3 * puissance + 0.12, 0.22 * puissance + 0.1, 0.12 * puissance + 0.09] }, mb);
    S.dessiner(this.meche, { mode: "papier", tex: S.blanc, teinte: [0.12, 0.1, 0.1, 1] }, mb);
    /* la flamme et son halo (lumière additive) */
    var L = [];
    if (vie > 0.01 && tombe === 0) {
      var hautF = 0.22 * (0.5 + 0.5 * vie) * (1 + 0.07 * Math.sin(ti * 13.7));
      L.push({ p: [mech[0] - couche * 0.04, mech[1] + hautF * 0.42, mech[2] - couche * 0.1], s: hautF * 0.55, h: 1.9 * (1 - couche * 0.35), r: couche * 0.9,
        c: [1, 1, 1, Math.min(1, vie * 1.1)] });
    }
    S.lutins(L, this.texFlamme, true);
    var G2 = [];
    if (vie > 0.01) G2.push({ p: [mech[0], mech[1] + 0.06, mech[2]], s: 1.3 * vie * fl, c: [1, 0.62, 0.28, 0.3 * vie] });
    /* l'éclair de la lumière qui revient, sur le cachet */
    var flash = t < 0 ? 0 : Math.max(0, 1 - Math.abs(o - 0.68) / 0.2);
    if (flash > 0) G2.push({ p: [0, 0.12, sz], s: 1.2 + flash * 1.4, c: [1, 0.86, 0.7, flash * 0.75] });
    S.lutins(G2, S.rond, true);
    /* la fumée : un ruban gris qui monte de la mèche et s'enroule */
    if (t >= 0) {
      var F = [];
      this.fumee.forEach(function (q) {
        var u = o - 0.18 - q.d; if (u <= 0 || u > 1.3) return;
        var a = Math.sin(Math.PI * Math.min(1, u / 1.3)) * 0.2;
        F.push({ p: [mech[0] + Math.sin(u * 2.6 + q.ph) * 0.07 * u * q.w, mech[1] + u * 0.7, mech[2] + Math.cos(u * 2.1 + q.ph) * 0.04 * u], s: 0.035 + u * 0.1, c: [0.82, 0.8, 0.84, a] });
      });
      S.lutins(F, S.rond, false);
    }
    /* la gerbe de confettis : lancée du cachet, elle retombe en tournoyant sur la table */
    if (t >= 0) {
      var Q = [], u0 = o - 0.66;
      if (u0 > 0 && u0 < 2.6) this.conf.forEach(function (q) {
        var u = u0, y = 0.1 + q.up * u - 2.6 * u * u;
        if (y < 0.015) y = 0.015;
        var x = Math.cos(q.a) * q.v * u, z = sz + Math.sin(q.a) * q.v * u * 0.7, r = q.ph + u * q.sp;
        Q.push({ p: [x, y, z], s: q.s, h: 0.55, c: [q.c[0], q.c[1], q.c[2], 1 - C.p(u, 2.0, 2.6)],
          ax: [Math.cos(r), Math.sin(r) * 0.4, Math.sin(r)], ay: [-Math.sin(r) * 0.9, Math.cos(r * 0.7) * 0.45, Math.cos(r) * 0.9] });
      });
      S.lutins(Q, S.blanc, false);
    }
    this.bokeh.dessiner(ti, (t < 0 ? 0.7 : 0.4 + 0.6 * C.p(o, 0.62, 1)) * (1 - plonge * 0.7));
  },
  geste: function () {
    var Son = Atelier.Son;
    Son.souffle(0, 0.5, 900, 300, 0.32);                 /* le souffle */
    setTimeout(function () { Son.craque(); }, 650);       /* la lumière revient, la cire cède */
    for (var i = 0; i < 6; i++) Son.toc(0.7 + i * 0.05, 2200 + i * 330, 0.03); /* les confettis */
  }
})

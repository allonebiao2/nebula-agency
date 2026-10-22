/* ── LE CACHET · l'ouverture de toujours, en vraie 3D (toute occasion qui n'a pas encore la sienne) ──
   On touche : la cire s'allume, cède en trois éclats pleins, le rabat doublé de damas se lève, la carte sort,
   et la caméra plonge sur elle jusqu'à ce qu'elle devienne la lettre. */
({
  id: "cachet",
  nom: { fr: "Le cachet", en: "The seal" },
  duree: 2.6,
  revele: 2.15,
  monter: function (S, D) {
    var A = Atelier, C = Theatre.C;
    A.matieres(S, MATIERES);
    this.D = D;
    this.table = A.Table(S, "#191420");
    this.env = A.Enveloppe(S, D);
    this.cachet = A.Cachet(S, D);
    var h = C.hasard(17), et = [], po = [];
    for (var i = 0; i < 46; i++) et.push({ a: h() * 6.283, v: 0.9 + h() * 1.8, y: 0.6 + h() * 1.6, s: 0.03 + h() * 0.05, d: h() * 0.12 });
    for (var j = 0; j < 26; j++) po.push({ x: (h() - 0.5) * 3.4, y: 0.2 + h() * 1.4, z: (h() - 0.5) * 2.4, s: 0.012 + h() * 0.02, ph: h() * 6.3 });
    this.etincelles = et; this.poussiere = po;
  },
  rendre: function (S, t, ti) {
    var M = Theatre.M, C = Theatre.C, env = this.env;
    var cad = this.D.cadre || { x: S.W / 2, y: S.H * 0.47, l: Math.min(S.W * 0.78, 340) };
    var o = Math.max(0, t);
    /* la cire s'allume au toucher, puis s'éteint en cassant (les éclats gardent leur couleur) */
    var dort = this.D.verrou && this.D.verrou();
    /* avant l'heure, la cire dort ; à l'heure, elle s'allume et appelle le doigt */
    var lueur = t < 0 ? (dort ? 0 : 0.2 + 0.12 * Math.sin(ti * 2.6)) : C.p(o, 0, 0.2) * (1 - C.p(o, 0.34, 0.7));
    var eclat = t < 0 ? 0 : C.p(o, 0.3, 1.15);
    var ouvre = C.doux(C.p(o, 0.42, 1.2));
    var sort = C.p(o, 1.0, 2.15);
    var plonge = C.doux(C.p(o, 1.1, 2.45));

    /* la caméra : de trois quarts au repos (elle respire), puis à la verticale de la carte qui monte */
    var champ = 30, d0 = S.distance(2.12, cad.l, champ), el = C.mix(53 + Math.sin(ti * 0.45) * 1.4, 89, plonge) * Math.PI / 180;
    var cz = C.mix(0.02, -env.H * 0.86, C.sort(sort));
    var cible = [0, C.mix(0, 0.05, sort), C.mix(0.04, cz, plonge)];
    /* à la fin, la carte (1,72 de large) remplit la largeur de l'écran : elle devient la lettre */
    var d1 = S.distance(1.72, S.W * 0.98, champ), d = C.mix(d0, d1, plonge), az = Math.sin(ti * 0.32) * 0.05 * (1 - plonge);
    S.camera([cible[0] + Math.sin(az) * d * Math.cos(el), cible[1] + d * Math.sin(el), cible[2] + Math.cos(az) * d * Math.cos(el)], cible, champ,
      C.mix(cad.x, S.W / 2, plonge), C.mix(cad.y, S.H / 2, plonge));

    /* la lumière : une clé chaude, une bougie qui vacille à gauche, une ambiance prune */
    var fl = 1 + 0.07 * Math.sin(ti * 9.1) + 0.04 * Math.sin(ti * 23.7);
    S.lumiere({ lum: [-0.45, 0.85, 0.5], lumc: [0.86, 0.8, 0.72], amb: [0.13, 0.11, 0.14],
      lp: [-1.4, 1.3, 1.0], lpc: [0.85 * fl + lueur * 0.5, 0.66 * fl + lueur * 0.25, 0.44 * fl + lueur * 0.18], brume: 0.6 });

    S.effacer();
    this.table.dessiner();
    S.ombre(0, 0, 0.04, 1.32, 0.9, 0.55);
    var base = M.id();
    env.dessiner(base, ouvre, sort);
    /* le cachet est posé sur la pointe du rabat ; il respire au repos, s'enfonce d'un rien au toucher */
    var press = t < 0 ? 1 + (dort ? 0 : 0.02 * Math.sin(ti * 1.8)) : 1 - 0.06 * Math.sin(C.p(o, 0, 0.3) * Math.PI);
    var mc = M.chaine(M.trans(0, 0.016, env.zr - 0.06), M.echelle(0.27 * press));
    if (eclat < 1) {
      if (!eclat) S.ombre(0, 0.014, env.zr - 0.03, 0.34, 0.34, 0.4);
      this.cachet.dessiner(mc, lueur, eclat, [0, 2.2, 2.6]);
    }
    /* l'éclair de la cire qui cède, puis la gerbe d'étincelles */
    var L = [], sx = 0, sy = 0.1, sz = env.zr - 0.06;
    var flash = t < 0 ? 0 : Math.max(0, 1 - Math.abs(o - 0.32) / 0.22);
    if (flash > 0) L.push({ p: [sx, sy + 0.05, sz], s: 1.1 + flash * 1.6, c: [1, 0.78, 0.6, flash * 0.9] });
    if (t >= 0) this.etincelles.forEach(function (e) {
      var tt = o - 0.3 - e.d; if (tt <= 0 || tt > 1.1) return;
      var a = 1 - tt / 1.1;
      L.push({ p: [sx + Math.cos(e.a) * e.v * tt, sy + e.y * tt - 1.4 * tt * tt, sz + Math.sin(e.a) * e.v * tt * 0.8], s: e.s * (1 + a), c: [1, 0.82, 0.55, a] });
    });
    /* la poussière dans la lumière de la bougie */
    this.poussiere.forEach(function (q) {
      L.push({ p: [q.x + Math.sin(ti * 0.2 + q.ph) * 0.2, q.y + Math.sin(ti * 0.15 + q.ph * 2) * 0.12, q.z], s: q.s, c: [1, 0.86, 0.66, 0.22 + 0.18 * Math.sin(ti + q.ph)] });
    });
    S.lutins(L, S.rond, true);
  },
  /* le geste : la cire qui craque, puis le papier qui glisse */
  geste: function () { Atelier.Son.craque(); }
})

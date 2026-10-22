/* ── LE CACHET · l'ouverture de toujours, en vraie 3D (toute occasion qui n'a pas encore la sienne) ──
   Au repos, la caméra tourne doucement autour de l'enveloppe posée sur le noyer, la bougie (hors champ) vacille.
   On touche : la caméra s'approche du cachet, la cire s'allume, cède en trois éclats (la caméra tressaille), une gerbe
   d'étincelles et des braises qui montent ; elle recule en tournant pendant que le rabat s'enroule et se couche ;
   puis elle s'élève avec la carte jusqu'à la regarder d'en haut, et la carte devient la lettre. */
({
  id: "cachet",
  nom: { fr: "Le cachet", en: "The seal" },
  duree: 3.0,
  revele: 2.55,
  monter: function (S, D) {
    var A = Atelier, C = Theatre.C;
    A.matieres(S, MATIERES);
    this.D = D;
    this.table = A.Table(S);
    this.env = A.Enveloppe(S, D);
    this.cachet = A.Cachet(S, D);
    this.bokeh = A.Bokeh(S, 10, 31);
    var h = C.hasard(17), et = [], po = [], br = [];
    for (var i = 0; i < 84; i++) et.push({ a: h() * 6.283, v: 0.7 + h() * 2.2, y: 0.5 + h() * 2.0, s: 0.022 + h() * 0.05, d: h() * 0.14 });
    for (var j = 0; j < 30; j++) po.push({ x: (h() - 0.5) * 3.6, y: 0.2 + h() * 1.6, z: (h() - 0.5) * 2.6, s: 0.012 + h() * 0.022, ph: h() * 6.3 });
    for (var k = 0; k < 26; k++) br.push({ x: (h() - 0.5) * 0.5, z: (h() - 0.5) * 0.4, v: 0.25 + h() * 0.5, s: 0.02 + h() * 0.03, ph: h() * 6.3, d: h() * 0.5 });
    this.etincelles = et; this.poussiere = po; this.braises = br;
  },
  rendre: function (S, t, ti) {
    var M = Theatre.M, C = Theatre.C, env = this.env;
    var cad = this.D.cadre || { x: S.W / 2, y: S.H * 0.47, l: Math.min(S.W * 0.78, 340) };
    var dort = this.D.verrou && this.D.verrou();
    var o = Math.max(0, t);
    var lueur = t < 0 ? (dort ? 0 : 0.2 + 0.12 * Math.sin(ti * 2.6)) : C.p(o, 0, 0.2) * (1 - C.p(o, 0.36, 0.7));
    var eclat = t < 0 ? 0 : C.p(o, 0.34, 1.2);
    var ouvre = C.doux(C.p(o, 0.48, 1.3));
    var sort = C.p(o, 1.12, 2.3);
    var plonge = C.doux(C.p(o, 1.2, 2.75));

    /* la caméra : approche au toucher, tressaillement à la fêlure, recul en tournant, puis l'élévation avec la carte */
    var champ = 30, d0 = S.distance(2.12, cad.l, champ), d1 = S.distance(1.72, S.W * 0.98, champ);
    var approche = t < 0 ? 0 : Math.sin(Math.PI * C.p(o, 0, 0.62)) * 0.16;
    var choc = t < 0 ? 0 : (o > 0.34 ? Math.exp(-(o - 0.34) * 9) : 0);
    var tour = t < 0 ? Math.sin(ti * 0.32) * 0.07 : Math.sin(ti * 0.32) * 0.07 * (1 - plonge) + C.doux(C.p(o, 0.45, 1.4)) * 0.22 * (1 - plonge);
    var el = C.mix(52 + Math.sin(ti * 0.45) * 1.5 - approche * 18, 89, plonge) * Math.PI / 180;
    var cz = C.mix(0.02, -env.H * 0.86, C.sort(sort));
    var cible = [Math.sin(ti * 47) * 0.004 * choc, C.mix(0, 0.16, sort) + Math.cos(ti * 53) * 0.004 * choc, C.mix(C.mix(0.04, env.zr - 0.06, approche * 4), cz, plonge)];
    var d = C.mix(d0 * (1 - approche), d1, plonge);
    S.camera([cible[0] + Math.sin(tour) * d * Math.cos(el), cible[1] + d * Math.sin(el), cible[2] + Math.cos(tour) * d * Math.cos(el)], cible, champ,
      C.mix(cad.x, S.W / 2, plonge), C.mix(cad.y, S.H / 2, plonge));
    S.post.dof = C.mix(0.85, 0.35, plonge); S.post.bloom = 0.6 + choc * 0.5;

    /* la lumière : une clé tiède, une bougie hors champ qui vacille à gauche, une ambiance prune, un liseré froid */
    var fl = 1 + 0.07 * Math.sin(ti * 9.1) + 0.04 * Math.sin(ti * 23.7);
    S.lumiere({ lum: [-0.45, 0.85, 0.5], lumc: [0.84, 0.78, 0.7], amb: [0.11, 0.09, 0.12],
      lp: [-1.5, 1.3, 1.0], lpc: [0.95 * fl + lueur * 0.5, 0.72 * fl + lueur * 0.25, 0.46 * fl + lueur * 0.18], brume: 0.55, rim: [0.1, 0.12, 0.18] });

    S.effacer();
    this.table.dessiner();
    S.ombre(0, 0, 0.04, 1.34, 0.92, 0.6);
    S.ombre(0, 0, 0.04, 1.12, 0.74, 0.4);
    env.dessiner(M.id(), ouvre, sort);
    var press = t < 0 ? 1 + (dort ? 0 : 0.02 * Math.sin(ti * 1.8)) : 1 - 0.07 * Math.sin(C.p(o, 0, 0.34) * Math.PI);
    var mc = M.chaine(M.trans(0, 0.016, env.zr - 0.06), M.echelle(0.27 * press));
    if (eclat < 1) {
      if (!eclat) S.ombre(0, 0.014, env.zr - 0.03, 0.34, 0.34, 0.45);
      this.cachet.dessiner(mc, lueur, eclat, [0, 2.3, 2.7]);
    }
    /* l'éclair de la cire qui cède, la gerbe d'étincelles, les braises qui montent, la poussière dans la lumière */
    var L = [], sx = 0, sy = 0.1, sz = env.zr - 0.06;
    var flash = t < 0 ? 0 : Math.max(0, 1 - Math.abs(o - 0.36) / 0.24);
    if (flash > 0) { L.push({ p: [sx, sy + 0.05, sz], s: 1.0 + flash * 1.3, c: [1, 0.78, 0.6, flash * 0.65] }); L.push({ p: [sx, sy + 0.05, sz], s: 0.3, c: [1, 1, 0.95, flash * 0.9] }); }
    if (t >= 0) {
      this.etincelles.forEach(function (e) {
        var tt = o - 0.34 - e.d; if (tt <= 0 || tt > 1.2) return;
        var a = 1 - tt / 1.2;
        L.push({ p: [sx + Math.cos(e.a) * e.v * tt, sy + e.y * tt - 1.6 * tt * tt, sz + Math.sin(e.a) * e.v * tt * 0.8], s: e.s * (1 + a), c: [1, 0.8 + 0.15 * a, 0.5 + 0.3 * a, a] });
      });
      this.braises.forEach(function (b) {
        var tt = o - 0.4 - b.d; if (tt <= 0 || tt > 1.5) return;
        var a = Math.sin(Math.PI * Math.min(1, tt / 1.5)) * 0.8;
        L.push({ p: [sx + b.x + Math.sin(tt * 2 + b.ph) * 0.12, sy + tt * b.v, sz + b.z + Math.cos(tt * 1.7 + b.ph) * 0.08], s: b.s, c: [1, 0.55, 0.25, a] });
      });
    }
    this.poussiere.forEach(function (q) {
      L.push({ p: [q.x + Math.sin(ti * 0.2 + q.ph) * 0.2, q.y + Math.sin(ti * 0.15 + q.ph * 2) * 0.12, q.z], s: q.s, c: [1, 0.86, 0.66, 0.22 + 0.18 * Math.sin(ti + q.ph)] });
    });
    S.lutins(L, S.rond, true);
    this.bokeh.dessiner(ti, 1 - plonge * 0.7);
  },
  geste: function () { Atelier.Son.craque(); }
})

/* ── LE PLI · « déplier la lettre » ── Avant les enveloppes, une lettre se fermait en se pliant sur elle-même. Sur la
   table, une feuille pliée en carré, ses quatre rabats réunis au centre sous un petit cachet. On touche : le cachet se
   décolle (il glisse et s'en va, sans éclat) et le premier rabat se déplie ; chaque toucher en déplie un autre (sinon
   ils se déplient seuls), chacun se soulève et s'enroule comme du vrai papier, avec son froissement. La feuille à plat,
   le regard plonge dedans : le papier devient la lettre (une feuille crème se fond dans la page crème). Sobre, intime :
   il convient au pardon, aux ruptures, à l'encouragement, à la guérison, au merci, à l'amitié.
   Thèmes (`THEME.motif`) : lin (une nappe de lin, la lumière d'une fenêtre), noyer (la table de bois, plus chaude). */
(function () {
  var M = Theatre.M, C = Theatre.C, G = Theatre.G;
  var MOTIFS = { lin: { table: "#8a8276", lum: [0.7, 0.68, 0.64], amb: [0.27, 0.27, 0.29] }, noyer: { table: null, lum: [0.78, 0.7, 0.6], amb: [0.2, 0.17, 0.2] } };
  var A_ = 1.3, ORDRE = ["haut", "bas", "droite", "gauche"], COUCHE = { gauche: 0.004, droite: 0.008, bas: 0.012, haut: 0.016 };
  var POSE = { bas: [0, A_ / 2, 0], haut: [0, -A_ / 2, Math.PI], droite: [A_ / 2, 0, Math.PI / 2], gauche: [-A_ / 2, 0, -Math.PI / 2] };

  return {
    id: "pli",
    plein: true,
    duree: 30,
    bouton: { fr: "Déplier la lettre", en: "Unfold the letter" },
    indice: { fr: "Touche pour déplier", en: "Tap to unfold" },
    monter: function (S, D) {
      var A = Atelier, th = typeof THEME !== "undefined" && THEME ? THEME : {}, T = {}, k;
      var base = MOTIFS[th.motif] || MOTIFS.lin;
      for (k in base) T[k] = base[k];
      for (k in th) T[k] = th[k];
      A.matieres(S, MATIERES);
      this.T = T; this.D = D; this.ouv = []; this.tGeste = null;
      /* le papier de l'habillage, nuit comprise : la feuille 3D se fond dans la page de la MÊME couleur */
      var hab = D.HAB || {}, pap = hab.papier || "creme", P = A.PAPIERS[pap] || A.PAPIERS.creme;
      this.table = A.Table(S, T.table);
      this.dehors = A.papier(S, pap, 21);
      /* le dedans : la même feuille, réglée de lignes très pâles ; au centre, « Ma lettre à » et le prénom, à l'encre */
      var dedans = function (centre) {
        return S.toile(1024, 1024, function (g) {
          var d = g.createLinearGradient(0, 0, 1024, 1024); d.addColorStop(0, P.a); d.addColorStop(1, P.b);
          g.fillStyle = d; g.fillRect(0, 0, 1024, 1024);
          var h = C.hasard(centre ? 4 : 6);
          for (var i = 0; i < 2500; i++) { g.fillStyle = "rgba(" + P.fibre + "," + (h() * 0.04).toFixed(3) + ")"; g.fillRect(h() * 1024, h() * 1024, 1 + h() * 6, 1); }
          g.fillStyle = "rgba(60,70,110,.12)";
          for (var y = 90; y < 1024; y += 64) g.fillRect(70, y, 884, 2);
          if (!centre) return;
          g.textAlign = "center"; g.fillStyle = P.encre;
          g.font = "64px " + A.SERIF; g.fillText(D.EN ? "My letter to" : "Ma lettre à", 512, 440);
          var n = String(D.pour || (D.EN ? "you" : "toi")).slice(0, 18), taille = 150;
          g.font = "italic " + taille + "px " + A.SERIF;
          while (g.measureText(n).width > 820 && taille > 40) { taille -= 6; g.font = "italic " + taille + "px " + A.SERIF; }
          g.fillStyle = (A.CIRES[hab.cire] || A.CIRES.bordeaux).cire; g.fillText(n, 512, 610);
        }, false);
      };
      this.dedansRabat = dedans(false); this.dedansCentre = dedans(true);
      this.centre = S.maillage(G.plan(A_, A_, 1, 1));
      /* un rabat : un triangle de papier, deux faces décalées d'un rien (le dedans en haut quand il est ouvert,
         le dehors en haut quand il est replié sur le centre) ; le nuanceur le soulève et l'enroule */
      this.rabatDedans = S.maillage(G.feuille(A_, A_ / 2, 16, null, 0.0012));
      this.rabatDehors = S.maillage(G.feuille(A_, A_ / 2, 16, null, -0.0012));
      this.cachet = A.Cachet(S, D);
    },
    /* déplier le rabat suivant (pas avant que le précédent ait fait le plus gros de son geste) */
    deplier: function (t) {
      if (this.ouv.length >= 4 || (this.ouv.length && t - this.ouv[this.ouv.length - 1] < 0.45)) return;
      this.ouv.push(t);
      var S = Atelier.Son;
      S.souffle(0, 0.38, 2400, 5200, 0.09); S.souffle(0.12, 0.3, 1400, 3200, 0.05);
      if (this.ouv.length === 4 && this.taire) this.taire();
    },
    geste: function () {
      this.tGeste = 0; this.auto = this.D.auto != null ? this.D.auto : 2.4;
      Atelier.Son.toc(0, 900, 0.05);
      this.ouv.push(0.55);
      Atelier.Son.souffle(0.55, 0.38, 2400, 5200, 0.09);
    },
    toucher: function (S, e) { if (e.type === "bas" && e.t >= 0.6) this.deplier(e.t); },
    revele: function (t) { return this.ouv.length === 4 && t > this.ouv[3] + 2.1; },
    fini: function (t) { return this.ouv.length === 4 && t > this.ouv[3] + 2.9; },
    rendre: function (S, t, ti) {
      var T = this.T, D = this.D, dort = D.verrou && D.verrou(), asp = S.W / S.H, self = this;
      /* les rabats qui manquent se déplient seuls */
      if (t >= 0 && this.ouv.length < 4 && t > this.ouv[this.ouv.length - 1] + this.auto) this.deplier(t);
      var fin = this.ouv.length === 4 ? this.ouv[3] : null;
      var plonge = fin == null ? 0 : C.doux(C.p(t, fin + 0.9, fin + 2.2)), fondu = fin == null ? 1 : 1 - C.p(t, fin + 2.1, fin + 2.8);
      /* la caméra : au-dessus de la table, presque à plomb ; à la fin elle descend dans la feuille */
      var champ = 30, tn = Math.tan(champ * Math.PI / 360), d0 = Math.max(A_ * 1.25 / (0.78 * 2 * tn * asp), A_ * 1.25 / (0.62 * 2 * tn));
      var d = C.mix(d0, 0.9, plonge), el = (80 + Math.sin(ti * 0.3) * 1.2) * Math.PI / 180, az = Math.sin(ti * 0.21) * 0.05 * (1 - plonge);
      S.camera([Math.sin(az) * d * Math.cos(el), d * Math.sin(el), Math.cos(az) * d * Math.cos(el)], [0, 0, 0], champ);
      S.lumiere({ lum: [-0.55, 0.8, 0.25], lumc: T.lum, amb: T.amb, lp: [-2, 2.2, 1], lpc: [0.2, 0.19, 0.17], brume: 0, rim: [0, 0, 0] });
      S.post.dof = 0.25 * (1 - plonge); S.post.bloom = 0.35; S.post.seuil = 0.92; S.post.vign = 0.38 * fondu; S.post.grain = 0.02;
      S.effacer();
      var a = fondu, tr = function (x) { return [x[0], x[1], x[2], a]; };
      if (plonge < 0.7) { this.table.dessiner(); S.ombre(0, 0, 0, A_ * 0.95, A_ * 0.95, 0.35); }
      S.dessiner(this.centre, { mode: "papier", tex: this.dedansCentre, teinte: tr([1, 1, 1]), spec: [0.05, 16] }, M.trans(0, 0.001, 0));
      /* les rabats : repliés sur le centre (le dehors en haut), ils se déplient un à un, en se soulevant et en s'enroulant */
      ORDRE.forEach(function (nom, k) {
        var u = self.ouv[k] == null ? 0 : C.p(t, self.ouv[k], self.ouv[k] + 0.95), e = u < 1 ? 1 - Math.pow(1 - u, 3) : 1;
        var pose = POSE[nom], m = M.chaine(M.trans(pose[0], COUCHE[nom], pose[1]), M.ry(pose[2]));
        /* replié, un rabat n'est jamais tout à fait à plat : sa pointe se soulève d'un rien, la lumière le sépare des autres */
        var pli = [Math.PI * (1 - e) - 0.07 * (1 - e), Math.sin(Math.PI * e) * 1.5 + 0.3 * (1 - e)];
        S.dessiner(self.rabatDedans, { mode: "papier", tex: self.dedansRabat, teinte: tr([1, 1, 1]), pli: pli, spec: [0.05, 16] }, m);
        S.dessiner(self.rabatDehors, { mode: "papier", tex: self.dehors, teinte: tr([1, 1, 1]), pli: pli, spec: [0.06, 18] }, m);
      });
      /* le petit cachet au centre : il se décolle et glisse hors de la feuille */
      var g = this.tGeste == null ? 0 : C.sort(C.p(t, 0, 0.7));
      if (g < 1) {
        var lueur = t < 0 ? (dort ? 0 : 0.12 + 0.08 * Math.sin(ti * 2.2)) : 0.2 * (1 - g);
        this.cachet.dessiner(M.chaine(M.trans(g * 1.9, 0.02 + Math.sin(Math.PI * g) * 0.25, -g * 1.4), M.ry(g * 1.6), M.echelle(0.13)), lueur, 0);
      }
    }
  };
})()

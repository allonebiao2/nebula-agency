/* ═══════════════════════════════════════════════════════════════════════════
   MA LETTRE À… · L'ATELIER : les objets que partagent les ouvertures.
   La table, l'enveloppe (dos, carte, poche, rabat doublé), le cachet de cire
   (le sceau en relief, ses éclats PLEINS), les pluies en 3D. Chaque rite y
   puise, puis joue sa propre scène. Unités : l'enveloppe fait 2 de large,
   couchée sur la table (plan XZ, y vers le haut, z vers celui qui regarde).
   ═══════════════════════════════════════════════════════════════════════════ */
var Atelier = (function () {
  "use strict";
  var M = Theatre.M, C = Theatre.C, G = Theatre.G;

  function rvb(h, a) {
    h = h.replace("#", "");
    return [parseInt(h.slice(0, 2), 16) / 255, parseInt(h.slice(2, 4), 16) / 255, parseInt(h.slice(4, 6), 16) / 255, a == null ? 1 : a];
  }
  /* Les habits du produit (`lettre.html` : .cire-*, .papier-*) : la même lettre en CSS et en 3D. */
  var CIRES = {
    bordeaux: { cire: "#8c2f39", clair: "#b2434e", fonce: "#6d1f27", lumiere: "#e08a93" },
    or: { cire: "#b8892b", clair: "#e0b85a", fonce: "#7a5a14", lumiere: "#e0c266" },
    nuit: { cire: "#2b2433", clair: "#4a3f56", fonce: "#141019", lumiere: "#c4b9d4" },
    sapin: { cire: "#2f5d4a", clair: "#4f8a6f", fonce: "#1b3a2d", lumiere: "#8cc9ab" },
    rose: { cire: "#b25a72", clair: "#d88aa0", fonce: "#7e3a4e", lumiere: "#eaa9bb" }
  };
  var PAPIERS = {
    creme: { a: "#f4ede0", b: "#e7dcc6", dos: "#e3d4ba", encre: "#241d2b", fibre: "60,40,30" },
    coton: { a: "#f7f3ea", b: "#ece5d6", dos: "#e6dccb", encre: "#241d2b", fibre: "80,70,60" },
    kraft: { a: "#e6d3b3", b: "#d6bf98", dos: "#cdb38b", encre: "#2e2318", fibre: "70,45,20" },
    nuit: { a: "#2f2839", b: "#231d2c", dos: "#1f1a27", encre: "#f4ede0", fibre: "255,255,255" }
  };
  /* Les sceaux du produit, en 24 × 24 (les mêmes tracés que la lettre). */
  var SCEAUX = {
    coeur: ["M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"],
    colombe: ["M3.5 13.5c2.2.4 4.3-.2 6-1.8 1.6-1.6 2.3-3.9 4.4-4.8 1.6-.7 3.4-.4 4.6.6l-2.1.8c.5 1.9 0 3.9-1.5 5.4-1.9 1.9-4.7 2.7-7.3 2.4-1.5-.2-2.9-.8-4.1-1.7z",
      "M9.8 11.5C8.3 9.4 8 6.9 9.1 4.6c1.6 1.6 2.4 3.7 2.4 5.8", "M3.5 13.5 2 16.5l3-1.2"],
    couronne: ["M4 17 3 8l5 4 4-6 4 6 5-4-1 9z", "M5 20h14"]
  };
  var SERIF = '"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif';

  /* ── Les textures dessinées ── */
  function papier(S, p, graine) {
    var P = PAPIERS[p] || PAPIERS.creme, h = C.hasard(graine || 7);
    /* 1024 px : de près (la caméra plonge sur la carte), une texture de 512 se voyait en escaliers */
    return S.toile(1024, 1024, function (g) {
      var d = g.createLinearGradient(0, 0, 1024, 1024); d.addColorStop(0, P.a); d.addColorStop(1, P.b);
      g.fillStyle = d; g.fillRect(0, 0, 1024, 1024);
      for (var i = 0; i < 7000; i++) {
        g.strokeStyle = "rgba(" + P.fibre + "," + (0.015 + h() * 0.045).toFixed(3) + ")";
        g.lineWidth = 0.4 + h() * 0.9; var x = h() * 1024, y = h() * 1024, l = 3 + h() * 16, a = h() * Math.PI;
        g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a + 0.4) * l * 0.5, y + Math.sin(a + 0.4) * l * 0.5, x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke();
      }
    }, true);
  }
  /* La doublure : un damas d'or sur la cire (les invitations des vidéos de Mongazi). */
  function doublure(S, cire) {
    var c = CIRES[cire] || CIRES.bordeaux;
    return S.toile(256, 256, function (g) {
      g.fillStyle = c.fonce; g.fillRect(0, 0, 256, 256);
      g.strokeStyle = "rgba(224,194,102,.6)"; g.lineWidth = 1.6;
      for (var y = -1; y < 5; y++) for (var x = -1; x < 5; x++) {
        var cx = x * 64 + (y % 2 ? 32 : 0), cy = y * 64;
        g.beginPath(); g.ellipse(cx, cy, 12, 19, 0, 0, Math.PI * 2);
        g.moveTo(cx - 20, cy); g.quadraticCurveTo(cx, cy - 27, cx + 20, cy); g.quadraticCurveTo(cx, cy + 27, cx - 20, cy);
        g.stroke();
      }
    }, true);
  }
  /* La carte dans l'enveloppe : « Ma lettre à » et le prénom, à l'encre de la cire. */
  function carte(S, D, p, cire) {
    var P = PAPIERS[p] || PAPIERS.creme, c = CIRES[cire] || CIRES.bordeaux;
    /* 1024 px : la carte finit plein écran, ses mots doivent rester nets */
    return S.toile(1024, 1024, function (g) {
      var d = g.createLinearGradient(0, 0, 0, 1024); d.addColorStop(0, p === "nuit" ? "#3a3146" : "#fbf7ef"); d.addColorStop(1, P.a);
      g.fillStyle = d; g.fillRect(0, 0, 1024, 1024);
      g.textAlign = "center"; g.fillStyle = P.encre;
      g.font = "68px " + SERIF; g.fillText(D.EN ? "My letter to" : "Ma lettre à", 512, 300);
      g.fillStyle = p === "nuit" ? c.lumiere : c.cire;
      var taille = 128, nom = String(D.pour || (D.EN ? "you" : "toi")).slice(0, 18);
      g.font = "italic " + taille + "px " + SERIF;
      while (g.measureText(nom).width > 880 && taille > 40) { taille -= 6; g.font = "italic " + taille + "px " + SERIF; }
      g.fillText(nom, 512, 464);
      /* un filet d'or sous le prénom */
      g.strokeStyle = "rgba(201,162,39,.7)"; g.lineWidth = 3; g.beginPath(); g.moveTo(452, 520); g.lineTo(572, 520); g.stroke();
    });
  }
  /* Le sceau en hauteur (blanc = relief) : l'anneau, le pointillé, puis le dessin ou l'initiale. */
  function hauteurSceau(S, sceau, initiale, dessins) {
    return S.toile(256, 256, function (g) {
      g.fillStyle = "#000"; g.fillRect(0, 0, 256, 256);
      var trait = function (passe) {
        g.save(); g.translate(128, 128);
        g.strokeStyle = g.fillStyle = "#fff"; g.globalAlpha = passe;
        g.lineWidth = 9; g.beginPath(); g.arc(0, 0, 76, 0, Math.PI * 2); g.stroke();
        g.lineWidth = 2.5; g.setLineDash([7, 6]); g.beginPath(); g.arc(0, 0, 64, 0, Math.PI * 2); g.stroke(); g.setLineDash([]);
        var traces = dessins || SCEAUX[sceau];
        if (traces) {
          g.scale(4.1, 4.1); g.translate(-12, -12.4); g.lineWidth = 1.9; g.lineJoin = g.lineCap = "round";
          traces.forEach(function (d) { g.stroke(new Path2D(d)); });
        } else {
          g.font = "112px " + SERIF; g.textAlign = "center"; g.textBaseline = "middle";
          g.fillText(String(initiale || "M").charAt(0).toUpperCase(), 0, 6);
        }
        g.restore();
      };
      /* un flou fait main (Safari n'a pas `filter` sur un canvas) : le tracé posé plusieurs fois, décalé */
      for (var k = 0; k < 7; k++) {
        g.save(); g.translate(Math.cos(k * 0.9) * 2.2, Math.sin(k * 0.9) * 2.2); trait(0.2); g.restore();
      }
      trait(0.45);
    });
  }

  /* ── La table : un grand drap sombre, et une flaque de lumière chaude sur l'enveloppe. ── */
  function Table(S, teinte) {
    var tex = S.toile(256, 256, function (g) {
      g.fillStyle = teinte || "#1d1826"; g.fillRect(0, 0, 256, 256);
      var h = C.hasard(3);
      for (var i = 0; i < 900; i++) { g.fillStyle = "rgba(255,255,255," + (h() * 0.035).toFixed(3) + ")"; g.fillRect(h() * 256, h() * 256, 1, 2 + h() * 3); }
      for (var j = 0; j < 256; j += 3) { g.fillStyle = "rgba(0,0,0,.07)"; g.fillRect(0, j, 256, 1); }
    }, true);
    var mesh = S.maillage(G.plan(30, 30, 1, 1));
    return {
      dessiner: function () {
        S.dessiner(mesh, { mode: "papier", tex: tex, rep: [9, 9] }, M.trans(0, -0.002, 0));
      }
    };
  }

  /* ── L'enveloppe ── l : largeur, h : hauteur ; pointe : où descend le V du rabat (part de la hauteur). */
  function Enveloppe(S, D, o) {
    o = o || {};
    var hab = D.HAB || {}, pap = o.papier || hab.papier || "creme", cire = o.cire || hab.cire || "bordeaux";
    var L = o.l || 2, H = o.h || 1.3, pointe = o.pointe || 0.56, P = PAPIERS[pap] || PAPIERS.creme;
    var texP = papier(S, pap, 11), texD = doublure(S, cire), texC = carte(S, D, pap, cire);
    var z0 = -H / 2, zv = z0 + H * 0.54, zr = z0 + H * pointe;
    var dos = S.maillage(G.plan(L, H, 1, 1));
    var carteM = S.maillage(G.plan(L * 0.86, H * 0.84, 1, 1));
    /* la poche : tout le rectangle sauf l'échancrure en V du haut, en deux moitiés convexes (un polygone creux
       triangulé depuis son centre recouvrait l'échancrure) */
    var pocheG = S.maillage(G.extrusion([[-L / 2, z0], [0, zv], [0, -z0], [-L / 2, -z0]], 0.004, 0));
    var pocheD = S.maillage(G.extrusion([[0, zv], [L / 2, z0], [L / 2, -z0], [0, -z0]], 0.004, 0));
    /* le rabat : une FEUILLE pendue à l'arête du haut, en bandes, que le nuanceur plie et enroule ; deux faces
       décalées d'un rien (le papier dehors, la doublure dedans) : la face tournée vers la caméra gagne */
    var rabatDehors = S.maillage(G.feuille(L, zr - z0, 16, null, 0.0012)), rabatDedans = S.maillage(G.feuille(L, zr - z0, 16, null, -0.0012));
    var teinteP = rvb(P.a), teinteDos = rvb(P.dos);
    return {
      L: L, H: H, z0: z0, zr: zr, cire: cire, papier: pap,
      /* base : la matrice qui pose l'enveloppe ; ouvre 0 → 1 : le rabat se lève ; sort 0 → 1 : la carte sort */
      dessiner: function (base, ouvre, sort) {
        ouvre = ouvre || 0; sort = sort || 0;
        S.dessiner(dos, { mode: "papier", tex: texP, teinte: teinteDos, rep: [1.4, 0.9] }, M.mul(base, M.trans(0, 0.001, 0)));
        /* la carte glisse vers le haut et se soulève (elle passe DEVANT le rabat ouvert) */
        var cz = C.mix(0.02, -H * 0.86, C.sort(sort)), cy = 0.004 + C.sort(sort) * 0.16;
        S.dessiner(carteM, { mode: "papier", tex: texC, teinte: [1, 1, 1, 1] }, M.chaine(base, M.trans(0, cy, cz)));
        S.dessiner(pocheG, { mode: "papier", tex: texP, teinte: teinteP, rep: [1.4, 0.9] }, M.mul(base, M.trans(0, 0.006, 0)));
        S.dessiner(pocheD, { mode: "papier", tex: texP, teinte: teinteP, rep: [1.4, 0.9] }, M.mul(base, M.trans(0, 0.006, 0)));
        /* le rabat tourne autour de son arête ; passé la verticale, on voit sa doublure */
        /* le rabat se soulève en s'enroulant (la courbure culmine à mi-course), puis se couche à plat derrière
           l'enveloppe, sous la carte qui sort */
        var pli = [ouvre * Math.PI, Math.sin(Math.PI * ouvre) * 1.6];
        var m = M.chaine(base, M.trans(0, 0.012, z0));
        S.dessiner(rabatDehors, { mode: "papier", tex: texP, teinte: teinteP, rep: [1.4, 0.9], pli: pli, spec: [0.1, 22] }, m);
        S.dessiner(rabatDedans, { mode: "papier", tex: texD, rep: [3, 3], pli: pli, spec: [0.18, 30] }, m);
      }
    };
  }

  /* ── Le cachet : un corps de cire coulée (bord bombé, irrégulier), un plateau qui porte le sceau en relief. ── */
  function corpsCachet() {
    var prof = [[0, 0.17], [0.62, 0.17], [0.7, 0.2], [0.78, 0.235]];
    for (var i = 0; i <= 10; i++) { var a = (i / 10) * Math.PI / 2; prof.push([0.78 + 0.22 * Math.sin(a), 0.235 * Math.cos(a)]); }
    var g = G.tour(prof.reverse(), 72);
    for (var k = 0; k < g.p.length; k += 3) {
      var x = g.p[k], z = g.p[k + 2], r = Math.hypot(x, z);
      if (r < 0.6) continue;
      var an = Math.atan2(z, x), b = 1 + 0.045 * Math.sin(an * 5 + 0.7) + 0.03 * Math.sin(an * 11 + 2.1) + 0.02 * Math.sin(an * 17), q = (r - 0.6) / 0.4;
      g.p[k] = x * (1 + (b - 1) * q); g.p[k + 2] = z * (1 + (b - 1) * q);
    }
    return g.normales();
  }
  function rayonBord(a) { return 1 + 0.045 * Math.sin(a * 5 + 0.7) + 0.03 * Math.sin(a * 11 + 2.1) + 0.02 * Math.sin(a * 17); }
  /* Les trois éclats PLEINS : des secteurs extrudés, aux lignes de fracture partagées et ondulées. */
  function eclats() {
    var plans = [[90, 210], [210, 330], [330, 450]], jonction = [0.05, -0.04];
    function fracture(d) {
      var pts = [];
      for (var i = 0; i <= 8; i++) {
        var f = i / 8, ang = d + 9 * Math.sin(f * 11 + d) + 5 * Math.sin(f * 23 + d * 2) + (i > 0 && i < 8 ? (i % 2 ? 3 : -3) : 0);
        var a = ang * Math.PI / 180, rb = rayonBord(a) - 0.04;
        pts.push(i === 0 ? jonction : [Math.cos(a) * rb * f, Math.sin(a) * rb * f]);
      }
      return pts;
    }
    return plans.map(function (pl) {
      var aller = fracture(pl[0]), retour = fracture(pl[1]).reverse();
      var a0 = Math.atan2(aller[8][1], aller[8][0]), a1 = Math.atan2(retour[0][1], retour[0][0]);
      while (a1 <= a0) a1 += Math.PI * 2;
      var contour = aller.slice(), pas = Math.max(8, Math.round((a1 - a0) / 0.06));
      for (var i = 1; i < pas; i++) { var a = a0 + (a1 - a0) * i / pas, rb = rayonBord(a) - 0.04; contour.push([Math.cos(a) * rb, Math.sin(a) * rb]); }
      contour = contour.concat(retour);
      return { g: G.extrusion(contour, 0.15, 0.035, 2), milieu: ((pl[0] + pl[1]) / 2) * Math.PI / 180 };
    });
  }
  function Cachet(S, D, o) {
    o = o || {};
    var hab = D.HAB || {}, cire = o.cire || hab.cire || "bordeaux";
    var sceau = o.sceau || hab.sceau || "initiale";
    var haut = hauteurSceau(S, sceau, (D.de || "M").trim().charAt(0) || "M", o.dessins);
    var mc = o.matcap || S.matcaps["cire-" + cire] || S.matcaps["cire-bordeaux"];
    var corps = S.maillage(corpsCachet());
    /* le plateau : un disque qui porte le relief (bosselage), un peu au-dessus du corps ; ses coordonnées de
       texture sont celles du cachet entier (rayon 1), comme la face des éclats : le sceau ne bouge pas en cassant */
    var rond = []; for (var i = 0; i < 64; i++) rond.push([Math.cos(i / 64 * Math.PI * 2) * 0.62, Math.sin(i / 64 * Math.PI * 2) * 0.62]);
    var plateau = S.maillage(G.extrusion(rond, 0.002, 0));
    var morceaux = eclats().map(function (e) { return { m: S.maillage(e.g), milieu: e.milieu }; });
    var lumiere = rvb((CIRES[cire] || CIRES.bordeaux).lumiere);
    /* la matcap a la lumière d'une chambre le soir : un cachet de 2 cm la veut un peu plus vive */
    var ECLAT = [1.22, 1.18, 1.15, 1];
    return {
      cire: cire,
      /* base : matrice du cachet (rayon 1) ; lueur 0 → 1 ; eclat 0 → 1 : brisé, morceaux projetés */
      dessiner: function (base, lueur, eclat, envol) {
        lueur = lueur || 0;
        var em = [lumiere[0] * lueur * 0.5, lumiere[1] * lueur * 0.5, lumiere[2] * lueur * 0.5];
        if (!eclat) {
          S.dessiner(corps, { mode: "matcap", tex: mc, emis: em, teinte: ECLAT }, base);
          S.dessiner(plateau, { mode: "matcap", tex: mc, haut: haut, bump: 2.6, emis: em, teinte: ECLAT }, M.mul(base, M.trans(0, 0.17, 0)));
          return;
        }
        var e = eclat, v = envol || [0, 1.6, 2.2];
        morceaux.forEach(function (mo, k) {
          var dx = Math.cos(mo.milieu) * e * 2.6, dz = Math.sin(mo.milieu) * e * 2.6;
          var m = M.chaine(base, M.trans(dx, e * v[1] + e * e * v[2], dz), M.rx(e * (k - 1) * 2.4), M.ry(e * 3 * (k + 1)), M.rz(e * (1 - k) * 1.8));
          S.dessiner(mo.m, { mode: "matcap", tex: mc, haut: haut, bump: 2.2, emis: em, teinte: ECLAT }, m);
        });
      }
    };
  }

  /* ── Les pluies, en vraie 3D : pétales qui tournoient, confettis, étoiles qui scintillent. ── */
  var COULEURS = {
    petales: ["#b2434e", "#d88aa0", "#f0c6cf", "#8c2f39"],
    confettis: ["#c9a227", "#b2434e", "#4f8a6f", "#e0c266", "#f4ede0"],
    etoiles: ["#e0c266", "#c9a227", "#f7e7b0"]
  };
  function Pluie(S, type, n, graine) {
    var h = C.hasard(graine || 5), P = [], cols = COULEURS[type] || COULEURS.etoiles;
    var tex = type === "petales" ? S.toile(64, 64, function (g) {
      var r = g.createRadialGradient(26, 30, 2, 32, 32, 30); r.addColorStop(0, "rgba(255,255,255,1)"); r.addColorStop(1, "rgba(255,255,255,.75)");
      g.fillStyle = r; g.beginPath(); g.ellipse(32, 32, 30, 17, 0, 0, Math.PI * 2); g.fill();
    }) : type === "confettis" ? S.blanc : S.toile(64, 64, function (g) {
      g.translate(32, 32); g.fillStyle = "#fff"; g.beginPath();
      for (var i = 0; i < 8; i++) { var a = i * Math.PI / 4, rr = i % 2 ? 9 : 30; g.lineTo(Math.cos(a) * rr, Math.sin(a) * rr); }
      g.closePath(); g.fill();
    });
    for (var i = 0; i < (n || 60); i++) {
      P.push({ x: (h() - 0.5) * 5, z: (h() - 0.5) * 3.5, y0: 2.6 + h() * 2.4, v: 0.55 + h() * 0.7, s: 0.07 + h() * 0.09,
        ph: h() * 6.28, w: 1 + h() * 2.5, c: rvb(cols[i % cols.length]), d: h() * 0.6 });
    }
    return {
      /* t : secondes depuis le début de la pluie ; elle tombe deux secondes et demie, puis s'efface */
      dessiner: function (t) {
        if (t <= 0 || t > 4) return;
        var a = t > 2.6 ? Math.max(0, 1 - (t - 2.6) / 1.2) : 1, L = [];
        P.forEach(function (q) {
          var tt = t - q.d; if (tt < 0) return;
          var y = q.y0 - q.v * tt * 1.4, x = q.x + Math.sin(q.ph + tt * 1.3) * 0.35, z = q.z + Math.cos(q.ph + tt) * 0.2;
          if (y < 0.02) y = 0.02;
          /* couchés plus que debout : vus d'en haut, des quads dressés ressemblaient à des aiguilles */
          var r = q.ph + tt * q.w, ax = [Math.cos(r), Math.sin(r * 0.7) * 0.4, Math.sin(r)], ay = [-Math.sin(r) * 0.9, Math.cos(r * 0.7) * 0.45, Math.cos(r) * 0.9];
          L.push({ p: [x, y, z], s: q.s * (type === "etoiles" ? 1.4 : 1), c: [q.c[0], q.c[1], q.c[2], a], ax: type === "etoiles" ? null : ax, ay: type === "etoiles" ? null : ay, h: type === "confettis" ? 0.5 : 1, r: type === "etoiles" ? r * 0.3 : 0 });
        });
        S.lutins(L, tex, type === "etoiles");
      }
    };
  }

  /* ── Le son : les outils de la lettre (`audio`, `bruit`, `SON`), s'ils existent (pas dans le studio). ── */
  var Son = {
    ctx: function () { return typeof audio === "function" ? audio() : null; },
    craque: function () { if (typeof sonOuverture === "function") sonOuverture(); },
    /* une note brève et claire (verre, perle, cloche) */
    tinte: function (f, quand, force) {
      var ctx = Son.ctx(); if (!ctx) return;
      var t = ctx.currentTime + (quand || 0), o = ctx.createOscillator(), g = ctx.createGain();
      o.type = "sine"; o.frequency.setValueAtTime(f, t);
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(force || 0.12, t + 0.004); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.35);
      o.connect(g); g.connect(SON.sortie); o.start(t); o.stop(t + 0.4);
    },
    /* un petit claquement sourd (une perle sur le bois, un bouchon) */
    toc: function (quand, f, force) {
      var ctx = Son.ctx(); if (!ctx) return;
      var t = ctx.currentTime + (quand || 0), o = ctx.createOscillator(), g = ctx.createGain();
      o.type = "triangle"; o.frequency.setValueAtTime(f || 1800, t); o.frequency.exponentialRampToValueAtTime((f || 1800) * 0.6, t + 0.05);
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(force || 0.08, t + 0.002); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.07);
      o.connect(g); g.connect(SON.sortie); o.start(t); o.stop(t + 0.08);
    },
    /* un souffle filtré (le papier qui glisse, l'air d'une porte, la flamme qu'on souffle) */
    souffle: function (quand, duree, de, a, force) {
      var ctx = Son.ctx(); if (!ctx || typeof bruit !== "function") return;
      var t = ctx.currentTime + (quand || 0), b = bruit(ctx, duree), f = ctx.createBiquadFilter(), g = ctx.createGain();
      f.type = "bandpass"; f.Q.value = 1.2; f.frequency.setValueAtTime(de, t); f.frequency.exponentialRampToValueAtTime(a, t + duree);
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(force || 0.2, t + duree * 0.25); g.gain.exponentialRampToValueAtTime(0.0001, t + duree);
      b.connect(f); f.connect(g); g.connect(SON.sortie); b.start(t);
    }
  };

  /* Les matières de Blender, posées en data: par la construction (`MATIERES`), décodées avant la première image. */
  function matieres(S, liste) {
    S.matcaps = {};
    for (var k in liste) S.matcaps[k] = S.image(liste[k]);
    return S.matcaps;
  }

  return { matieres: matieres, doublure: doublure, carte: carte, rvb: rvb, CIRES: CIRES, PAPIERS: PAPIERS, SCEAUX: SCEAUX, SERIF: SERIF, Table: Table, Enveloppe: Enveloppe,
    Cachet: Cachet, Pluie: Pluie, Son: Son, hauteurSceau: hauteurSceau, papier: papier };
})();

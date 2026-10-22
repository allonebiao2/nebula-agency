/* ── LES PORTES · plein écran ── Mongazi (2026-10-22) : « comme dans une ou deux vidéos, l'écran entier du téléphone
   doit s'ouvrir comme une porte en 3D, de façon immersive ».
   Deux battants couvrent TOUT l'écran, gaufrés : leur relief prend une lumière qui glisse seule et suit le doigt (et
   l'inclinaison d'un téléphone Android). Un cachet les tient, à cheval sur la fente. On touche : le cachet casse, les
   battants se déverrouillent (un trait de lumière dans la fente). On les écarte du bout des doigts : ils suivent le
   doigt, reviennent s'ils ne sont pas assez ouverts, partent seuls passé 55° ; un simple toucher les ouvre aussi, et
   au bout de six secondes ils s'ouvrent d'eux-mêmes. Ils s'ouvrent VERS SOI, la lumière entre, et derrière eux il
   y a la vraie lettre (`plein` : la scène est une fenêtre transparente).
   Le motif vient de l'ouverture choisie (`THEME.motif`) : la dentelle (mariage, demande, anniversaire de couple,
   fête des mères), le velours capitonné aux cœurs d'or (Saint-Valentin, demande de couple, mois de rencontre), le
   moucharabieh qu'une lanterne éclaire par derrière (Tabaski, fin du Ramadan), l'Art déco noir et or (Nouvel an,
   soirée, réussite, invitation). Tout est DESSINÉ ici (aucune image à télécharger). */
(function () {
  var M = Theatre.M, C = Theatre.C;
  /* fond : le dégradé ; ton : le relief sans or ; or : couleur de la feuille d'or ; tout-or : tout le relief est d'or ;
     creux : les gorges ; dos : la doublure ; tranche : l'épaisseur ; lum, amb : la lumière ; halo : celle qui entre ;
     sceau : « or » (métal) ou « cire » (la cire de l'habillage) ; ajoure : des jours dans les battants */
  var MOTIFS = {
    dentelle: { fond: ["#f7e7dd", "#ebd1c3"], ton: "#fff6ef", or: "#cfa95e", toutOr: false, creux: "rgba(110,64,50,.30)",
      dos: "#efdccf", tranche: [0.84, 0.72, 0.66], lum: [0.8, 0.78, 0.76], amb: [0.37, 0.35, 0.36], halo: [1, 0.86, 0.7],
      sceau: "or", ep: 0.012, bump: 1.8, spec: [0.08, 24], seuil: 0.97, pl: 0.16 },
    coeurs: { fond: ["#7c2232", "#4b1120"], ton: "#b0465a", or: "#dcb862", toutOr: false, creux: "rgba(28,4,10,.55)",
      dos: "#5c1828", tranche: [0.28, 0.07, 0.11], lum: [1, 0.86, 0.8], amb: [0.3, 0.2, 0.22], halo: [1, 0.74, 0.7],
      sceau: "cire", ep: 0.016, bump: 1.0, spec: [0.16, 14], seuil: 0.86, pl: 0.3 },
    moucharabieh: { fond: ["#22304a", "#121a2a"], ton: "#2f4366", or: "#d0aa52", toutOr: true, creux: "rgba(0,0,0,.55)",
      dos: "#16202f", tranche: [0.09, 0.12, 0.17], lum: [1, 0.88, 0.7], amb: [0.24, 0.22, 0.26], halo: [1, 0.78, 0.45],
      sceau: "or", ep: 0.022, bump: 1.6, spec: [0.12, 30], ajoure: true, seuil: 0.86, pl: 0.3 },
    deco: { fond: ["#17141a", "#0a090c"], ton: "#2a262d", or: "#dcbc6a", toutOr: true, creux: "rgba(0,0,0,.6)",
      dos: "#120f14", tranche: [0.05, 0.045, 0.055], lum: [1, 0.92, 0.8], amb: [0.22, 0.21, 0.23], halo: [1, 0.86, 0.62],
      sceau: "or", ep: 0.016, bump: 1.4, spec: [0.2, 40], seuil: 0.86, pl: 0.3 }
  };
  var OUVERT = 1.95, ELAN = 0.95, SEUIL = 0.42, REPOS = 0.1;   // radians : grand ouvert, partent seuls, lâchés, déverrouillés

  function pot(x) { var p = 512; while (p < x * 0.85 && p < 4096) p *= 2; return p; }
  function bez(q, t) {
    var u = 1 - t;
    return [u * u * u * q[0][0] + 3 * u * u * t * q[1][0] + 3 * u * t * t * q[2][0] + t * t * t * q[3][0],
      u * u * u * q[0][1] + 3 * u * u * t * q[1][1] + 3 * u * t * t * q[2][1] + t * t * t * q[3][1]];
  }
  /* un ressort amorti (0 → 1, un léger rebond) : le poids d'un battant */
  function ressort(u) {
    if (u >= 1) return 1;
    var z = 0.5, w = 9, wd = w * Math.sqrt(1 - z * z), x = u * 1.6;
    return 1 - Math.exp(-z * w * x) * (Math.cos(wd * x) + z * w / wd * Math.sin(wd * x));
  }

  /* ── Les pinceaux : la même gravure est peinte deux fois, en couleur (`c`) et en hauteur (`h` : rouge = relief,
     vert = feuille d'or). ── */
  function pinceaux(T, haut) {
    var orC = T.or, tonC = T.ton;
    return haut ? {
      r: function (n) { return "rgb(" + n + "," + (T.toutOr ? 255 : 0) + ",0)"; },
      o: function (n) { return "rgb(" + n + ",255,0)"; },
      m: function (n) { return "rgb(" + n + ",0,0)"; },
      c: function (a) { return "rgba(0,0,0," + (a == null ? 0.9 : a) + ")"; },
      haut: true
    } : {
      r: function (n) { return T.toutOr ? orC : rvba(tonC, 0.18 + n / 255 * 0.55); },
      o: function () { return orC; },
      m: function (n) { return rvba(tonC, 0.18 + n / 255 * 0.55); },
      c: function () { return T.creux; },
      haut: false
    };
  }
  function rvba(h, a) {
    h = h.replace("#", "");
    return "rgba(" + parseInt(h.slice(0, 2), 16) + "," + parseInt(h.slice(2, 4), 16) + "," + parseInt(h.slice(4, 6), 16) + "," + a.toFixed(3) + ")";
  }

  /* ── Les gestes du graveur ── */
  function arche(g, w, Hv, m) {
    var r = (w - 2 * m) / 2;
    g.beginPath(); g.moveTo(m, Hv - m); g.lineTo(m, m + r); g.arc(w / 2, m + r, r, Math.PI, 0); g.lineTo(w - m, Hv - m); g.closePath();
  }
  function petale(g, r) {
    g.beginPath(); g.moveTo(0, 0);
    g.quadraticCurveTo(r * 0.2, -r * 0.5, r * 0.62, -r * 0.42); g.quadraticCurveTo(r * 1.06, -r * 0.3, r, 0);
    g.quadraticCurveTo(r * 1.06, r * 0.3, r * 0.62, r * 0.42); g.quadraticCurveTo(r * 0.2, r * 0.5, 0, 0);
  }
  /* une rose vue d'en haut : trois couronnes de pétales qui montent vers le cœur, un cœur en spirale */
  function rose(g, x, y, r, P, rot) {
    [[5, 1, 120], [5, 0.74, 170], [4, 0.5, 225]].forEach(function (c, k) {
      for (var i = 0; i < c[0]; i++) {
        g.save(); g.translate(x, y); g.rotate(rot + (i + k * 0.5) * 2 * Math.PI / c[0]);
        petale(g, r * c[1]); g.fillStyle = P.r(c[2]); g.fill();
        g.lineWidth = Math.max(1, r * 0.045); g.strokeStyle = P.c(0.8); g.stroke();
        g.restore();
      }
    });
    g.beginPath();
    for (var s = 0; s < 36; s++) { var a = rot + s * 0.42, rr = r * 0.24 * (1 - s / 36); g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); }
    g.lineWidth = Math.max(1, r * 0.05); g.strokeStyle = P.c(0.8); g.stroke();
  }
  function feuille(g, x, y, l, a, P, n) {
    g.save(); g.translate(x, y); g.rotate(a);
    g.beginPath(); g.moveTo(0, 0); g.quadraticCurveTo(l * 0.5, -l * 0.34, l, 0); g.quadraticCurveTo(l * 0.5, l * 0.34, 0, 0);
    g.fillStyle = P.r(n); g.fill();
    g.beginPath(); g.moveTo(l * 0.1, 0); g.lineTo(l * 0.84, 0); g.lineWidth = Math.max(1, l * 0.04); g.strokeStyle = P.c(0.7); g.stroke();
    g.restore();
  }
  /* une tige en courbe de Bézier, des feuilles de part et d'autre, une fleurette au bout */
  function liane(g, q, P, ep, nf, l) {
    g.beginPath(); g.moveTo(q[0][0], q[0][1]); g.bezierCurveTo(q[1][0], q[1][1], q[2][0], q[2][1], q[3][0], q[3][1]);
    g.lineWidth = ep; g.lineCap = "round"; g.strokeStyle = P.r(140); g.stroke();
    for (var i = 1; i <= nf; i++) {
      var t = i / (nf + 1), p = bez(q, t), p2 = bez(q, Math.min(1, t + 0.01)), a = Math.atan2(p2[1] - p[1], p2[0] - p[0]);
      feuille(g, p[0], p[1], l * (1 - t * 0.35), a + (i % 2 ? 0.95 : -0.95), P, 160);
    }
    fleurette(g, q[3][0], q[3][1], l * 0.42, P);
  }
  function fleurette(g, x, y, r, P) {
    for (var i = 0; i < 5; i++) {
      var a = i * 2 * Math.PI / 5;
      g.beginPath(); g.arc(x + Math.cos(a) * r * 0.55, y + Math.sin(a) * r * 0.55, r * 0.42, 0, Math.PI * 2);
      g.fillStyle = P.r(175); g.fill();
    }
    g.beginPath(); g.arc(x, y, r * 0.24, 0, Math.PI * 2); g.fillStyle = P.r(230); g.fill();
  }
  function perles(g, pts, r, P, n) {
    pts.forEach(function (p) { g.beginPath(); g.arc(p[0], p[1], r, 0, Math.PI * 2); g.fillStyle = P.r(n); g.fill(); });
  }
  /* des points posés le long d'une arche, à pas régulier */
  function surArche(w, Hv, m, pas) {
    var r = (w - 2 * m) / 2, cy = m + r, pts = [], y;
    for (y = Hv - m; y > cy; y -= pas) pts.push([m, y]);
    var n = Math.round(Math.PI * r / pas);
    for (var i = 0; i <= n; i++) { var a = Math.PI + Math.PI * i / n; pts.push([w / 2 + Math.cos(a) * r, cy + Math.sin(a) * r]); }
    for (y = cy + pas; y < Hv - m; y += pas) pts.push([w - m, y]);
    return pts;
  }
  function coeur(g, x, y, s) {
    g.beginPath(); g.moveTo(x, y + s * 0.35);
    g.bezierCurveTo(x - s * 0.1, y + s * 0.22, x - s * 0.5, y + s * 0.02, x - s * 0.5, y - s * 0.2);
    g.bezierCurveTo(x - s * 0.5, y - s * 0.48, x - s * 0.08, y - s * 0.5, x, y - s * 0.22);
    g.bezierCurveTo(x + s * 0.08, y - s * 0.5, x + s * 0.5, y - s * 0.48, x + s * 0.5, y - s * 0.2);
    g.bezierCurveTo(x + s * 0.5, y + s * 0.02, x + s * 0.1, y + s * 0.22, x, y + s * 0.35);
  }
  function etoile8(g, x, y, r, k) {
    g.beginPath();
    for (var i = 0; i < 16; i++) { var a = i * Math.PI / 8 + Math.PI / 16, rr = i % 2 ? r * k : r; g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); }
    g.closePath();
  }

  /* ── Les quatre motifs (le battant de GAUCHE, de 0 à w ; le droit en est le miroir) ── */
  var PEINTRES = {
    dentelle: function (g, w, Hv, P, h) {
      var u = Hv / 100, m = w * 0.075, r = (w - 2 * m) / 2, cy = m + r;
      arche(g, w, Hv, m); g.lineWidth = u * 0.55; g.strokeStyle = P.r(150); g.stroke();
      arche(g, w, Hv, m + u * 1.5); g.lineWidth = u * 0.22; g.strokeStyle = P.r(110); g.stroke();
      perles(g, surArche(w, Hv, m + u * 2.5, u * 1.25), u * 0.3, P, 170);
      /* le bouquet du haut, sous l'arche */
      var bx = w / 2, by = cy - r * 0.08;
      liane(g, [[bx, by], [bx - r * 0.5, by + r * 0.1], [m + u * 4, by + r * 0.5], [m + u * 4.2, by + r * 1.5]], P, u * 0.32, 5, u * 2.6);
      liane(g, [[bx, by], [bx + r * 0.5, by + r * 0.1], [w - m - u * 4, by + r * 0.5], [w - m - u * 4.2, by + r * 1.5]], P, u * 0.32, 5, u * 2.6);
      rose(g, bx - r * 0.42, by + r * 0.16, u * 2.1, P, 1.2);
      rose(g, bx + r * 0.42, by + r * 0.16, u * 2.1, P, 2.3);
      rose(g, bx, by - r * 0.06, u * 3.2, P, 0.4);
      /* le bouquet du bas, du côté de la charnière, qui remonte */
      var y0 = Hv - m - u * 6;
      liane(g, [[m + u * 5, y0], [m + u * 3, y0 - u * 12], [m + u * 9, y0 - u * 18], [m + u * 5.5, y0 - u * 27]], P, u * 0.3, 6, u * 2.4);
      liane(g, [[m + u * 5, y0], [w * 0.55, y0 + u * 1.5], [w * 0.7, y0 - u * 4], [w - m - u * 5, y0 - u * 2]], P, u * 0.3, 4, u * 2.2);
      rose(g, m + u * 5.5, y0 - u * 1, u * 3, P, 0.9);
      rose(g, m + u * 11, y0 + u * 0.5, u * 1.8, P, 2.6);
      /* la bande de dentelle le long du bord intérieur : des œillets dans des festons */
      for (var y = cy + r * 0.6; y < Hv - m - u * 10; y += u * 2.4) {
        g.beginPath(); g.arc(w - m * 0.62, y, u * 0.5, 0, Math.PI * 2); g.lineWidth = u * 0.22; g.strokeStyle = P.r(160); g.stroke();
        g.beginPath(); g.arc(w - m * 0.62, y, u * 0.2, 0, Math.PI * 2); g.fillStyle = P.c(0.6); g.fill();
      }
      /* des fleurettes semées sur une trame en quinconce (un rien décalées), loin du nom, du cachet et des bouquets */
      for (var j = 0; j < 9; j++) for (var i = 0; i < 3; i++) {
        var px = m + u * 5 + (i + (j % 2) * 0.5) * (w - 2 * m - u * 10) / 2.5 + (h() - 0.5) * u, py = cy + r * 1.5 + j * u * 7.2 + (h() - 0.5) * u;
        if (px > w - m - u * 4 || py > Hv - m - u * 30 || Math.abs(py - Hv * 0.37) < u * 9 || Math.abs(py - Hv * 0.5) < u * 8) continue;
        fleurette(g, px, py, u * 0.9, P);
        feuille(g, px, py + u * 0.9, u * 1.4, Math.PI / 2 + (h() - 0.5) * 0.8, P, 130);
      }
    },
    coeurs: function (g, w, Hv, P, h) {
      var u = Hv / 100, s = u * 6.4, i, j;
      /* le capitonné : des losanges bombés (le relief monte vers leur cœur), cousus aux pointes */
      for (j = -1; j * s * 0.5 < Hv + s; j++) for (i = -1; i * s < w + s; i++) {
        var x = i * s + (j % 2 ? s / 2 : 0), y = j * s * 0.5;
        if (P.haut) {
          var gr = g.createRadialGradient(x, y, 0, x, y, s * 0.55);
          gr.addColorStop(0, "rgb(210,0,0)"); gr.addColorStop(0.7, "rgb(120,0,0)"); gr.addColorStop(1, "rgb(40,0,0)");
          g.fillStyle = gr;
        } else {
          var gc = g.createRadialGradient(x - s * 0.1, y - s * 0.12, 0, x, y, s * 0.6);
          gc.addColorStop(0, rvba("#ffffff", 0.07)); gc.addColorStop(1, rvba("#000000", 0.12)); g.fillStyle = gc;
        }
        g.beginPath(); g.moveTo(x, y - s * 0.5); g.lineTo(x + s * 0.5, y); g.lineTo(x, y + s * 0.5); g.lineTo(x - s * 0.5, y); g.closePath(); g.fill();
      }
      /* les coutures, et un bouton d'or à chaque pointe ; un petit cœur d'or une pointe sur trois */
      for (j = -1; j * s * 0.5 < Hv + s; j++) for (i = -1; i * s < w + s; i++) {
        var px = i * s + (j % 2 ? s / 2 : 0) + s / 2, py = j * s * 0.5;
        if (Math.abs(py - Hv * 0.37) < u * 8 || Math.abs(py - Hv * 0.5) < u * 6) continue;
        if ((i + j * 2) % 3 === 0) { coeur(g, px, py, u * 1.6); g.fillStyle = P.o(230); g.fill(); }
        else { g.beginPath(); g.arc(px, py, u * 0.42, 0, Math.PI * 2); g.fillStyle = P.o(200); g.fill(); }
      }
      /* le cadre d'or, en arche, double */
      var m = w * 0.08;
      arche(g, w, Hv, m); g.lineWidth = u * 0.6; g.strokeStyle = P.o(190); g.stroke();
      arche(g, w, Hv, m + u * 1.3); g.lineWidth = u * 0.22; g.strokeStyle = P.o(150); g.stroke();
      perles(g, surArche(w, Hv, m + u * 2.3, u * 1.5), u * 0.28, { r: P.o }, 180);
      /* un grand cœur d'or au trait sous l'arche */
      coeur(g, w / 2, m + (w - 2 * m) / 2 + u * 2, u * 9); g.lineWidth = u * 0.5; g.strokeStyle = P.o(210); g.stroke();
    },
    moucharabieh: function (g, w, Hv, P, h) {
      var u = Hv / 100, m = w * 0.07, i, j, g0 = m + u * 2.6, s = (w - 2 * g0) / 4;
      /* le panneau, puis le treillis d'étoiles à huit branches : chaque étoile est un JOUR (la lanterne passe) */
      var jour = function (trace) {
        trace();
        if (P.haut) { g.fillStyle = "rgb(0,0,0)"; g.fill(); } else { g.save(); g.globalCompositeOperation = "destination-out"; g.fillStyle = "#000"; g.fill(); g.restore(); }
        trace(); g.lineWidth = u * 0.32; g.strokeStyle = P.o(205); g.stroke();
      };
      var dedans = function (x, y, y0, y1) { return x > g0 - 1 && x < w - g0 + 1 && y > y0 && y < y1; };
      var ajoure = function (y0, y1, arc) {
        for (j = -1; y0 + j * s < y1 + s; j++) for (i = -1; i * s < w + s; i++) {
          var x = g0 + s / 2 + i * s, y = y0 + j * s, x2 = x + s / 2, y2 = y + s / 2;
          var ok = function (px, py, rr) { return dedans(px - rr, py - rr, y0, y1) && dedans(px + rr, py + rr, y0, y1) && (!arc || arc(px, py, rr)); };
          if (ok(x, y, s * 0.42)) jour(function () { etoile8(g, x, y, s * 0.4, 0.66); });
          if (ok(x2, y2, s * 0.18)) jour(function () { g.beginPath(); g.moveTo(x2, y2 - s * 0.17); g.lineTo(x2 + s * 0.17, y2); g.lineTo(x2, y2 + s * 0.17); g.lineTo(x2 - s * 0.17, y2); g.closePath(); });
        }
      };
      var r = (w - 2 * m) / 2, cy = m + r * 1.15, a0 = Math.PI * 0.92, xs = w / 2 + Math.cos(a0) * r, ys = cy + Math.sin(a0) * r;
      ajoure(m, Hv * 0.235, function (px, py, rr) { var dx = px - w / 2, dy = py - cy; return py > cy || Math.sqrt(dx * dx + dy * dy) < r - u * 2.4 - rr; });
      ajoure(Hv * 0.6, Hv - m - u * 2);
      /* l'arc outrepassé (plus qu'un demi-cercle, comme une porte de Fès) et le cadre */
      g.beginPath(); g.moveTo(xs, Hv - m); g.lineTo(xs, ys); g.arc(w / 2, cy, r, a0, Math.PI * 2.08, false);
      g.lineTo(w - xs, Hv - m); g.closePath(); g.lineWidth = u * 0.7; g.strokeStyle = P.o(200); g.stroke();
      g.beginPath(); g.moveTo(m + u * 1.4, Hv * 0.585); g.lineTo(w - m - u * 1.4, Hv * 0.585); g.lineWidth = u * 0.4; g.stroke();
      g.beginPath(); g.moveTo(m + u * 1.4, Hv * 0.245); g.lineTo(w - m - u * 1.4, Hv * 0.245); g.stroke();
    },
    deco: function (g, w, Hv, P, h) {
      var u = Hv / 100, m = w * 0.08, i;
      /* le cadre à redans, trois fois */
      [0, 1.6, 3].forEach(function (d, k) {
        var a = m + u * d, c = u * (3 - k * 0.6);
        g.beginPath(); g.moveTo(a + c, a); g.lineTo(w - a - c, a); g.lineTo(w - a - c, a + c); g.lineTo(w - a, a + c);
        g.lineTo(w - a, Hv - a - c); g.lineTo(w - a - c, Hv - a - c); g.lineTo(w - a - c, Hv - a); g.lineTo(a + c, Hv - a);
        g.lineTo(a + c, Hv - a - c); g.lineTo(a, Hv - a - c); g.lineTo(a, a + c); g.lineTo(a + c, a + c); g.closePath();
        g.lineWidth = u * (k ? 0.22 : 0.5); g.strokeStyle = P.o(200 - k * 30); g.stroke();
      });
      /* le soleil levant : un éventail de rayons sous une arche, en haut */
      var cx = w / 2, cy = m + u * 22, R = (w - 2 * m) * 0.42;
      for (i = 0; i <= 18; i++) {
        var a = Math.PI + Math.PI * i / 18;
        g.beginPath(); g.moveTo(cx + Math.cos(a) * R * 0.18, cy + Math.sin(a) * R * 0.18); g.lineTo(cx + Math.cos(a) * R, cy + Math.sin(a) * R);
        g.lineWidth = u * (i % 2 ? 0.16 : 0.3); g.strokeStyle = P.o(i % 2 ? 160 : 210); g.stroke();
      }
      [1, 1.08, 0.18].forEach(function (k) { g.beginPath(); g.arc(cx, cy, R * k, Math.PI, 0); g.lineWidth = u * 0.3; g.strokeStyle = P.o(200); g.stroke(); });
      g.beginPath(); g.moveTo(cx - R * 1.08, cy); g.lineTo(cx + R * 1.08, cy); g.lineWidth = u * 0.3; g.stroke();
      /* des filets verticaux du côté de la charnière, des chevrons en bas */
      for (i = 0; i < 3; i++) { g.beginPath(); g.moveTo(m + u * (5 + i * 1.2), cy + u * 4); g.lineTo(m + u * (5 + i * 1.2), Hv * 0.82); g.lineWidth = u * 0.14; g.strokeStyle = P.o(150); g.stroke(); }
      for (i = 0; i < 5; i++) {
        var y = Hv * 0.84 + i * u * 1.6;
        g.beginPath(); g.moveTo(m + u * 6, y); g.lineTo(w / 2, y - u * 2.2); g.lineTo(w - m - u * 6, y);
        g.lineWidth = u * 0.22; g.strokeStyle = P.o(190 - i * 18); g.stroke();
      }
      /* le long de la fente, une colonne de petits losanges d'or */
      for (var y2 = m + u * 6; y2 < Hv - m - u * 6; y2 += u * 3) {
        if (Math.abs(y2 - Hv * 0.37) < u * 8 || Math.abs(y2 - Hv * 0.5) < u * 7) continue;
        g.beginPath(); g.moveTo(w - m * 0.55, y2 - u * 0.8); g.lineTo(w - m * 0.55 + u * 0.5, y2); g.lineTo(w - m * 0.55, y2 + u * 0.8); g.lineTo(w - m * 0.55 - u * 0.5, y2);
        g.closePath(); g.fillStyle = P.o(220); g.fill();
      }
    }
  };

  /* « Ma lettre à » et le prénom, en feuille d'or, à cheval sur les deux battants (ils se séparent en s'ouvrant) */
  function nom(g, Wv, Hv, P, D) {
    var u = Hv / 100, cx = Wv / 2, t1 = D.EN ? "MY LETTER TO" : "MA LETTRE À";
    g.textAlign = "center"; g.textBaseline = "alphabetic";
    var petit = Math.round(u * 1.9);
    g.font = "600 " + petit + "px " + Atelier.SERIF;
    var esp = petit * 0.34, larg = 0, i;
    for (i = 0; i < t1.length; i++) larg += g.measureText(t1[i]).width + esp;
    var x = cx - (larg - esp) / 2;
    g.fillStyle = P.o(230); g.textAlign = "left";
    for (i = 0; i < t1.length; i++) { g.fillText(t1[i], x, Hv * 0.315); x += g.measureText(t1[i]).width + esp; }
    var taille = Math.round(u * 7.4), n = String(D.pour || (D.EN ? "you" : "toi")).slice(0, 18);
    g.font = "italic 500 " + taille + "px " + Atelier.SERIF;
    while (g.measureText(n).width > Wv * 0.8 && taille > 12) { taille -= 2; g.font = "italic 500 " + taille + "px " + Atelier.SERIF; }
    g.textAlign = "center"; g.fillText(n, cx, Hv * 0.395);
    g.beginPath(); g.moveTo(cx - u * 4, Hv * 0.418); g.lineTo(cx + u * 4, Hv * 0.418); g.lineWidth = u * 0.22; g.strokeStyle = P.o(200); g.stroke();
  }

  /* un flou sur le relief seul (le rouge), en JavaScript : Safari n'a pas `filter` sur un canvas */
  function adoucir(cv, r) {
    var g = cv.getContext("2d"), w = cv.width, h = cv.height, im = g.getImageData(0, 0, w, h), d = im.data, t = new Uint8ClampedArray(w * h), x, y, s, k;
    for (k = 0; k < 2; k++) {
      for (y = 0; y < h; y++) { s = 0; var o = y * w; for (x = -r; x <= r; x++) s += d[(o + Math.min(w - 1, Math.max(0, x))) * 4];
        for (x = 0; x < w; x++) { t[o + x] = s / (2 * r + 1); s += d[(o + Math.min(w - 1, x + r + 1)) * 4] - d[(o + Math.max(0, x - r)) * 4]; } }
      for (x = 0; x < w; x++) { s = 0; for (y = -r; y <= r; y++) s += t[Math.min(h - 1, Math.max(0, y)) * w + x];
        for (y = 0; y < h; y++) { d[(y * w + x) * 4] = s / (2 * r + 1); s += t[Math.min(h - 1, y + r + 1) * w + x] - t[Math.max(0, y - r) * w + x]; } }
    }
    g.putImageData(im, 0, 0);
  }

  /* ── Un battant : sa face (le motif), son dos (la doublure), sa tranche ; le bord intérieur festonné ── */
  function battant(S, sens, ep, profil) {
    var N = 140, face = { p: [], n: [], uv: [], i: [] }, dos = { p: [], n: [], uv: [], i: [] }, bord = { p: [], n: [], uv: [], i: [] };
    var U = function (x) { return sens > 0 ? x / 2 : 1 - x / 2; }, j, k;
    for (j = 0; j <= N; j++) {
      var y = 1 - 2 * j / N, xe = profil(y), v = (1 - y) / 2;
      face.p.push(0, y, 0, sens * xe, y, 0); face.n.push(0, 0, 1, 0, 0, 1); face.uv.push(U(0), v, U(xe), v);
      dos.p.push(0, y, -ep, sens * xe, y, -ep); dos.n.push(0, 0, -1, 0, 0, -1); dos.uv.push(U(0), v, U(xe), v);
      bord.p.push(sens * xe, y, 0, sens * xe, y, -ep); bord.n.push(sens, 0, 0, sens, 0, 0); bord.uv.push(0, v, 1, v);
    }
    for (j = 0; j < N; j++) {
      k = j * 2;
      /* le sens des triangles : la face regarde la caméra, le dos la fuit (le nuanceur retourne les normales du revers) */
      if (sens > 0) { face.i.push(k, k + 2, k + 1, k + 1, k + 2, k + 3); dos.i.push(k, k + 1, k + 2, k + 1, k + 3, k + 2); bord.i.push(k, k + 1, k + 2, k + 1, k + 3, k + 2); }
      else { face.i.push(k, k + 1, k + 2, k + 1, k + 3, k + 2); dos.i.push(k, k + 2, k + 1, k + 1, k + 2, k + 3); bord.i.push(k, k + 2, k + 1, k + 1, k + 2, k + 3); }
    }
    /* le haut et le bas (on les voit quand le battant tourne) */
    var b0 = bord.p.length / 3;
    [[1, 1], [-1, -1]].forEach(function (yy, q) {
      var xe = profil(yy[0]), o = b0 + q * 4;
      bord.p.push(0, yy[0], 0, sens * xe, yy[0], 0, 0, yy[0], -ep, sens * xe, yy[0], -ep);
      for (var z = 0; z < 4; z++) { bord.n.push(0, yy[1], 0); bord.uv.push(0, 0); }
      bord.i.push(o, o + 1, o + 2, o + 1, o + 3, o + 2);
    });
    return { face: S.maillage(face), dos: S.maillage(dos), bord: S.maillage(bord) };
  }

  return {
    id: "battants",
    plein: true,
    duree: 30,
    bouton: { fr: "Ouvrir les portes", en: "Open the doors" },
    indice: { fr: "Écarte les portes du bout des doigts", en: "Part the doors with your fingertips" },
    monter: function (S, D) {
      var A = Atelier, self = this, th = typeof THEME !== "undefined" && THEME ? THEME : {}, T = {}, k;
      var base = MOTIFS[th.motif] || MOTIFS.dentelle;
      for (k in base) T[k] = base[k];
      for (k in th) T[k] = th[k];
      A.matieres(S, MATIERES);
      this.T = T; this.D = D; this.etat = "ferme"; this.ang = 0; this.lx = -0.35; this.ly = 0.5; this.fx = 0; this.fy = 0; this.lumT = -99;
      this.doigts = {};
      var h = C.hasard(29), asp = S.W / S.H;
      /* la gravure : un canvas aux dimensions de puissance de deux (mipmaps, filtrage anisotrope), dessiné dans les
         proportions de l'écran (un cercle reste un cercle) */
      var Hc = asp < 1 ? 2048 : 1024, Wc = pot(Hc * asp), Hv = Hc, Wv = Hc * asp, peintre = PEINTRES[T.motif] || PEINTRES.dentelle;
      function graver(g, haut) {
        var cv = g.canvas, P = pinceaux(T, haut);
        if (haut) { g.fillStyle = T.ajoure ? "rgb(120,0,0)" : "rgb(70,0,0)"; g.fillRect(0, 0, Wc, Hc); }
        else {
          var d = g.createLinearGradient(0, 0, 0, Hc); d.addColorStop(0, T.fond[0]); d.addColorStop(1, T.fond[1]);
          g.fillStyle = d; g.fillRect(0, 0, Wc, Hc);
          /* le grain du papier ou du velours */
          var hg = C.hasard(5);
          for (var i = 0; i < 9000; i++) { g.fillStyle = "rgba(255,255,255," + (hg() * 0.035).toFixed(3) + ")"; g.fillRect(hg() * Wc, hg() * Hc, 1.4, 1.4); }
        }
        g.setTransform(Wc / Wv, 0, 0, 1, 0, 0);
        peintre(g, Wv / 2, Hv, P, C.hasard(41));
        /* le battant de droite est le miroir du gauche (sa moitié d'abord effacée : les jours du moucharabieh passent) */
        g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(Wc / 2, 0, Wc / 2, Hc);
        g.setTransform(-1, 0, 0, 1, Wc, 0);
        g.drawImage(cv, 0, 0, Wc / 2, Hc, 0, 0, Wc / 2, Hc);
        g.setTransform(Wc / Wv, 0, 0, 1, 0, 0);
        nom(g, Wv, Hv, P, D);
        /* l'ombre portée le long de la fente : les battants ne sont pas collés */
        if (!haut) {
          g.setTransform(1, 0, 0, 1, 0, 0);
          var f = g.createLinearGradient(Wc / 2 - Wc * 0.02, 0, Wc / 2 + Wc * 0.02, 0);
          f.addColorStop(0, "rgba(0,0,0,0)"); f.addColorStop(0.5, "rgba(0,0,0,.18)"); f.addColorStop(1, "rgba(0,0,0,0)");
          g.fillStyle = f; g.fillRect(Wc / 2 - Wc * 0.02, 0, Wc * 0.04, Hc);
        }
        if (haut) adoucir(cv, Hc > 1500 ? 2 : 1);
      }
      this.tex = S.toile(Wc, Hc, function (g) { graver(g, false); });
      this.haut = S.toile(Wc, Hc, function (g) { graver(g, true); });
      /* envoyées à la carte graphique, les toiles (8 Mo chacune) n'ont plus rien à faire en mémoire */
      this.tex.toile = this.haut.toile = null;
      this.texDos = S.toile(512, 1024, function (g) {
        g.fillStyle = T.dos; g.fillRect(0, 0, 512, 1024);
        var hg = C.hasard(8);
        for (var i = 0; i < 3000; i++) { g.fillStyle = "rgba(255,255,255," + (hg() * 0.04).toFixed(3) + ")"; g.fillRect(hg() * 512, hg() * 1024, 1.2, 1.2); }
        g.strokeStyle = T.or; g.lineWidth = 3; g.strokeRect(28, 28, 456, 968); g.lineWidth = 1.2; g.strokeRect(40, 40, 432, 944);
      });
      /* le bord intérieur, festonné, sauf là où passent le nom et le cachet */
      var amp = 0.006 / asp, festons = 15;
      var profil = function (y) {
        var fen = C.doux(C.borne((Math.abs(y) - 0.2) / 0.08)) * C.doux(C.borne((Math.abs(y - 0.27) - 0.14) / 0.06)) * C.doux(C.borne((0.97 - Math.abs(y)) / 0.04));
        return 1 - amp * Math.pow(Math.abs(Math.sin(Math.PI * festons * (y + 1) / 2)), 0.7) * fen;
      };
      this.G = battant(S, 1, T.ep, profil); this.Dr = battant(S, -1, T.ep, profil);
      var mc = T.sceau === "or" ? S.matcaps.or : null;
      /* le sceau : celui que l'acheteur a choisi (cœur, colombe, couronne) ; sinon l'emblème de l'occasion ; sinon l'initiale */
      var sc = (D.HAB || {}).sceau, dessins = (!sc || sc === "initiale") && T.embleme ? [T.embleme] : null;
      this.cachet = A.Cachet(S, D, { matcap: mc, dessins: dessins });
      var hh = C.hasard(17), et = [], po = [];
      for (var i = 0; i < 70; i++) et.push({ a: hh() * 6.283, v: 0.5 + hh() * 1.6, s: 0.012 + hh() * 0.03, d: hh() * 0.12 });
      for (var j = 0; j < 46; j++) po.push({ x: (hh() - 0.5) * 2.4, y: (hh() - 0.5) * 2, z: -0.6 + hh() * 1.6, s: 0.006 + hh() * 0.014, ph: hh() * 6.3, v: 0.03 + hh() * 0.06 });
      this.etincelles = et; this.poussiere = po;
    },
    /* le doigt : avant tout, il promène la lumière ; après le cachet, il écarte les battants */
    toucher: function (S, e) {
      var fx = (e.x / S.W) * 2 - 1, fy = 1 - (e.y / S.H) * 2;
      if (e.type === "incline") { this.fx = Math.max(-1, Math.min(1, e.x)); this.fy = 0.4 + Math.max(-1, Math.min(1, -e.y)) * 0.6; this.lumT = e.ti; return; }
      var dd = this.doigts, ids, ecart, prendre = (this.etat === "libre" || this.etat === "retour") && e.t > 0.45;
      if (e.type === "survol" || e.type === "bas" || (e.type === "glisse" && this.etat !== "tire")) { this.fx = fx; this.fy = fy; this.lumT = e.ti; }
      if (e.type === "survol") return;
      if (e.type === "bas") {
        dd[e.id] = { x: e.x, y: e.y, x0: e.x, y0: e.y };
        if (prendre) { this.etat = "tire"; this.a0 = this.ang; this.cible = this.ang; this.bouge = 0; }
        return;
      }
      if (!dd[e.id]) return;
      dd[e.id].x = e.x; dd[e.id].y = e.y;
      /* un doigt posé AVANT que le cachet cède (on a voulu écarter tout de suite) prend les battants dès qu'ils sont libres */
      if (e.type === "glisse" && prendre) {
        this.etat = "tire"; this.a0 = this.ang; this.cible = this.ang; this.bouge = 0;
        for (var id in dd) { dd[id].x0 = dd[id].x; dd[id].y0 = dd[id].y; }
      }
      ids = Object.keys(dd);
      /* un doigt : sa course horizontale ; deux doigts : l'écart qui grandit entre eux */
      if (ids.length >= 2) {
        var p = dd[ids[0]], q = dd[ids[1]], e1 = Math.abs(p.x - q.x), e0 = Math.abs(p.x0 - q.x0);
        ecart = Math.max(0, e1 - e0);
      } else ecart = Math.abs(dd[e.id].x - dd[e.id].x0);
      if (e.type === "glisse" && this.etat === "tire") {
        this.bouge = Math.max(this.bouge, ecart);
        this.cible = Math.min(1.5, this.a0 + ecart / (S.W * 0.5) * 1.8);
        if (this.cible > ELAN) this.partir(e.t);
      } else if (e.type === "haut") {
        delete dd[e.id];
        if (e.t < 0) return;
        if (this.etat === "tire" && !Object.keys(dd).length) {
          if (this.ang > SEUIL || this.bouge < 12) this.partir(e.t);
          else { this.etat = "retour"; this.t0 = e.t; this.a0 = this.ang; Atelier.Son.toc(0.05, 160, 0.06); }
        }
      }
    },
    partir: function (t) {
      if (this.etat === "ouvre") return;
      this.etat = "ouvre"; this.t0 = t; this.a0 = this.ang;
      var S = Atelier.Son;
      S.souffle(0, 1.4, 260, 1100, 0.2);
      S.accord(0.15, [196, 293.66, 392, 587.33], 3.4, 0.045);
      S.tinte(1568, 0.35, 0.025); S.tinte(2093, 0.6, 0.02);
    },
    geste: function () {
      this.etat = "libre"; this.auto = this.D.auto != null ? this.D.auto : 6.5;
      var S = Atelier.Son;
      S.craque(); S.toc(0.42, 150, 0.16); S.souffle(0.45, 0.8, 500, 1800, 0.07);
    },
    revele: function () { return this.etat === "ouvre" && this.ang > 0.55; },
    fini: function (t) { return this.etat === "ouvre" && t - this.t0 > 2.1; },
    rendre: function (S, t, ti) {
      var T = this.T, D = this.D, dt = this.avant == null ? 0.016 : Math.max(0, Math.min(0.05, ti - this.avant));
      this.avant = ti;
      var asp = S.W / S.H, dort = D.verrou && D.verrou();
      /* ── l'angle des battants ── */
      if (t >= 0) {
        if (this.etat === "libre") {
          this.ang = REPOS * Math.max(0, ressort(C.p(t, 0.42, 1.0)));
          if (this.auto != null && t > this.auto) this.partir(t);
        } else if (this.etat === "tire") {
          this.ang += (this.cible - this.ang) * (1 - Math.exp(-dt * 16));
        } else if (this.etat === "retour") {
          var u = C.p(t, this.t0, this.t0 + 0.7);
          this.ang = Math.max(0.01, C.mix(this.a0, REPOS, ressort(u)));
          if (u >= 1) { this.etat = "libre"; this.auto = t + 6; }
        } else if (this.etat === "ouvre") {
          var u2 = C.p(t, this.t0, this.t0 + 1.6), k2 = this.a0 < 0.2 ? C.doux(u2) : C.sort(u2);
          this.ang = C.mix(this.a0, OUVERT, k2);
        }
      }
      var a = this.ang, o = Math.max(0, t);
      /* la lumière : la clé rase les battants (le relief se lit), elle dérive seule et suit le doigt deux secondes */
      var age = ti - this.lumT, w = age < 2.5 ? 1 : Math.exp(-(age - 2.5) * 0.7);
      var tx = C.mix(-0.3 + Math.sin(ti * 0.23) * 0.55, this.fx, w), ty = C.mix(0.55 + Math.cos(ti * 0.17) * 0.25, this.fy, w);
      var kl = 1 - Math.exp(-dt * 4.5);
      this.lx += (tx - this.lx) * (dt ? kl : 1); this.ly += (ty - this.ly) * (dt ? kl : 1);
      var flot = t < 0 ? 0 : (this.etat === "ouvre" ? Math.sin(Math.PI * C.p(a, 0.05, 1.5)) : Math.min(1, a / 0.9) * 0.6);
      var fuite = t < 0 ? (dort ? 0 : 0.12 + 0.05 * Math.sin(ti * 1.7)) : Math.max(C.p(t, 0.35, 0.6) * 0.75, flot);
      S.lumiere({ lum: [this.lx * 0.85, this.ly * 0.85, 0.36], lumc: T.lum, amb: T.amb, lp: [this.lx * 1.1, this.ly * 1.1, 1.3],
        lpc: [T.pl + flot * 0.3, T.pl * 0.82 + flot * 0.22, T.pl * 0.64 + flot * 0.15], brume: 0, rim: [0, 0, 0] });
      /* la caméra : face aux battants, qui remplissent l'écran ; un rien d'élan vers l'avant quand ils s'ouvrent */
      var champ = 30, d = 1 / Math.tan(champ * Math.PI / 360), avance = this.etat === "ouvre" ? C.doux(C.p(t, this.t0, this.t0 + 2)) * 0.35 : 0;
      var choc = t < 0 ? 0 : (t > 0.42 ? Math.exp(-(t - 0.42) * 10) : 0) * 0.006;
      S.camera([Math.sin(ti * 61) * choc, Math.cos(ti * 47) * choc, d - avance], [0, 0, 0], champ);
      S.post.dof = 0; S.post.bloom = 0.45 + flot * 0.4; S.post.seuil = T.seuil; S.post.vign = 0.34; S.post.grain = 0.018;

      S.effacer();
      /* derrière les battants : la lanterne (moucharabieh) et la lumière qui attend dans la fente */
      var L = [];
      if (T.ajoure) {
        /* la flamme d'une lanterne : elle respire et vacille ; avant l'heure, elle veille plus bas */
        var lant = ((t < 0 && dort) ? 0.3 : 0.75) * (t < 0 ? 1 : 1 - C.p(a, 0.25, 1.1)) * (1 + 0.08 * Math.sin(ti * 7.3) + 0.05 * Math.sin(ti * 13.1));
        L.push({ p: [0, 0.12, -0.55], s: 3.4, c: [T.halo[0], T.halo[1] * 0.92, T.halo[2] * 0.8, lant * 0.8] });
        L.push({ p: [0, 0.05, -0.5], s: 1.5, c: [1, 0.86, 0.6, lant * 0.6] });
      }
      for (var g2 = -1; g2 <= 1.001; g2 += 0.1) L.push({ p: [0, g2, -0.08], s: 0.16 + fuite * 0.3, c: [T.halo[0], T.halo[1], T.halo[2], fuite * 0.45] });
      if (flot > 0) {
        L.push({ p: [0, 0.1, -0.6], s: 1.2 + 2.2 * flot, c: [T.halo[0], T.halo[1], T.halo[2], flot * 0.42] });
        L.push({ p: [0, 0.1, -0.5], s: 0.5 + 0.8 * flot, c: [1, 0.96, 0.9, flot * 0.3] });
      }
      S.lutins(L, S.rond, true);
      /* les battants */
      var mg = M.chaine(M.trans(-asp, 0, 0), M.ry(-a), M.echelle(asp, 1, 1)), md = M.chaine(M.trans(asp, 0, 0), M.ry(a), M.echelle(asp, 1, 1));
      var face = { mode: "papier", tex: this.tex, haut: this.haut, bump: T.bump, metal: 1, spec: T.spec, coupe: T.ajoure ? 0.5 : 0 };
      var dos = T.ajoure ? { mode: "papier", tex: this.tex, teinte: [0.55, 0.55, 0.6, 1], spec: [0.08, 18], coupe: 0.5 } : { mode: "papier", tex: this.texDos, spec: [0.08, 18] };
      var bord = { mode: "papier", tex: S.blanc, teinte: [T.tranche[0], T.tranche[1], T.tranche[2], 1] };
      [[this.G, mg], [this.Dr, md]].forEach(function (b) {
        S.dessiner(b[0].face, face, b[1]); S.dessiner(b[0].dos, dos, b[1]); S.dessiner(b[0].bord, bord, b[1]);
      });
      /* le cachet, à cheval sur la fente ; au toucher il s'allume, casse, et ses éclats tombent */
      var lueur = (t < 0 ? (dort ? 0 : 0.12 + 0.08 * Math.sin(ti * 2.4)) : C.p(o, 0, 0.16) * (1 - C.p(o, 0.3, 0.6)) * 0.6) * (T.sceau === "or" ? 0.5 : 1);
      var eclat = t < 0 ? 0 : C.p(o, 0.18, 1.4), R = 0.15, zc = 0.004;
      if (eclat < 1) {
        if (!eclat) S.lutins([{ p: [0.012, -0.02, 0.002], s: R * 2.9, ax: [1, 0, 0], ay: [0, 1, 0], c: [0.02, 0.01, 0.03, 0.4] }], S.rond, false);
        var base = M.chaine(M.trans(0, -2.6 * eclat * eclat, zc + eclat * 0.3), M.rx(Math.PI / 2), M.echelle(R));
        this.cachet.dessiner(base, lueur, eclat, [0, 0.9, 0.6]);
      }
      /* les étincelles du cachet, et la poussière d'or dans la lumière qui entre */
      var L2 = [], flash = t < 0 ? 0 : Math.max(0, 1 - Math.abs(o - 0.2) / 0.2);
      if (flash > 0) L2.push({ p: [0, 0, 0.12], s: 0.35 + flash * 0.5, c: [1, 0.85, 0.6, flash * 0.35] });
      if (t >= 0) this.etincelles.forEach(function (e) {
        var tt = o - 0.18 - e.d; if (tt <= 0 || tt > 1) return;
        var al = 1 - tt;
        L2.push({ p: [Math.cos(e.a) * e.v * tt * 0.6, Math.sin(e.a) * e.v * tt * 0.6 - 0.9 * tt * tt, 0.1 + tt * 0.4], s: e.s * (1 + al), c: [1, 0.82, 0.55, al] });
      });
      if (flot > 0.02) this.poussiere.forEach(function (q) {
        L2.push({ p: [q.x * 0.6 + Math.sin(ti * 0.3 + q.ph) * 0.1, q.y + ((ti * q.v + q.ph) % 2) - 1, q.z], s: q.s, c: [1, 0.9, 0.7, flot * (0.35 + 0.25 * Math.sin(ti * 2 + q.ph))] });
      });
      S.lutins(L2, S.rond, true);
    }
  };
})()

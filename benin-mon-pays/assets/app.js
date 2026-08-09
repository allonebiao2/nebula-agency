/* ═══════════════════════════════════════════════════════════════
   BÉNIN MON PAYS · moteur
   Zéro bibliothèque. Tout est écrit ici.
   Grammaires reprises des trois références :
     · le rideau et l'anneau gradué          (vidéo 1)
     · le cartel qui balaye, titre fantôme   (vidéo 2)
     · la parallaxe par mot, fond qui morphe (vidéo 3)
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var D = document, W = window;
  var doux = W.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fin  = W.matchMedia('(hover: hover) and (pointer: fine)').matches;

  function $(s, p) { return (p || D).querySelector(s); }
  function $$(s, p) { return Array.prototype.slice.call((p || D).querySelectorAll(s)); }
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }

  /* graine déterministe : le dessin est le même à chaque visite */
  function alea(g) {
    var s = g;
    return function () {
      s = (s * 1103515245 + 12345) % 2147483648;
      return s / 2147483648;
    };
  }

  var stations = $$('.st');
  var barreH = 60;

  /* ═══ 1 · LES MOTIFS ════════════════════════════════════════
     Des relevés géométriques, dessinés. Aucun ne prétend être une
     photographie d'un lieu : c'est la règle du projet. */

  var MOTIFS = {

    porte: function (r) {
      var p = '', i;
      /* l'arche */
      p += '<path class="tr" d="M240 620 L240 300 A160 160 0 0 1 560 300 L560 620"/>';
      p += '<path class="tr" d="M300 620 L300 320 A100 100 0 0 1 500 320 L500 620"/>';
      /* l'horizon et la mer */
      for (i = 0; i < 9; i++) {
        var y = 640 + i * 22;
        var d1 = 60 + r() * 120, d2 = 740 - r() * 120;
        p += '<path class="tr" d="M' + d1.toFixed(0) + ' ' + y + ' L' + d2.toFixed(0) + ' ' + y + '"/>';
      }
      p += '<path class="tr" d="M40 630 L760 630"/>';
      return '<svg viewBox="0 0 800 860" aria-hidden="true">' + p + '</svg>';
    },

    route: function (r) {
      var p = '', i;
      /* la route qui remonte, sinueuse */
      var d = 'M400 820';
      for (i = 1; i <= 8; i++) {
        var y = 820 - i * 96;
        var x = 400 + Math.sin(i * 1.15) * (150 - i * 8);
        d += ' Q' + (x + 60).toFixed(0) + ' ' + (y + 48) + ' ' + x.toFixed(0) + ' ' + y.toFixed(0);
      }
      p += '<path class="tr" d="' + d + '"/>';
      /* les bornes */
      for (i = 1; i <= 7; i++) {
        var yy = 820 - i * 96, xx = 400 + Math.sin(i * 1.15) * (150 - i * 8);
        p += '<path class="tr" d="M' + (xx - 16).toFixed(0) + ' ' + yy + ' L' + (xx + 16).toFixed(0) + ' ' + yy + '"/>';
      }
      /* la forêt sacrée */
      for (i = 0; i < 14; i++) {
        var cx = 70 + r() * 660, cy = 120 + r() * 640, ra = 9 + r() * 17;
        p += '<circle class="tr" cx="' + cx.toFixed(0) + '" cy="' + cy.toFixed(0) + '" r="' + ra.toFixed(0) + '"/>';
      }
      return '<svg viewBox="0 0 800 860" aria-hidden="true">' + p + '</svg>';
    },

    marche: function (r) {
      var p = '', i;
      for (i = 0; i < 74; i++) {
        var w = 26 + r() * 74, h = 20 + r() * 46;
        var x = 20 + r() * (760 - w), y = 40 + r() * (780 - h);
        p += '<rect class="tr" x="' + x.toFixed(0) + '" y="' + y.toFixed(0) +
             '" width="' + w.toFixed(0) + '" height="' + h.toFixed(0) + '"/>';
      }
      return '<svg viewBox="0 0 800 860" aria-hidden="true">' + p + '</svg>';
    },

    pilotis: function (r) {
      var p = '', i;
      /* l'eau */
      for (i = 0; i < 12; i++) {
        var y = 470 + i * 30;
        p += '<path class="tr" d="M' + (30 + r() * 90).toFixed(0) + ' ' + y +
             ' L' + (770 - r() * 90).toFixed(0) + ' ' + y + '"/>';
      }
      /* les pilotis et les toits */
      for (i = 0; i < 17; i++) {
        var x = 50 + i * 42 + r() * 12;
        var h = 150 + r() * 190;
        p += '<path class="tr" d="M' + x.toFixed(0) + ' ' + (470 - h).toFixed(0) + ' L' + x.toFixed(0) + ' 560"/>';
        if (i % 2 === 0) {
          var t = (470 - h).toFixed(0);
          p += '<path class="tr" d="M' + (x - 34).toFixed(0) + ' ' + t + ' L' + x.toFixed(0) + ' ' +
               (parseFloat(t) - 40).toFixed(0) + ' L' + (x + 34).toFixed(0) + ' ' + t + '"/>';
        }
      }
      /* la pirogue */
      p += '<path class="tr" d="M300 690 Q400 736 500 690 L470 706 Q400 748 330 706 Z"/>';
      p += '<path class="tr" d="M396 690 L396 606"/>';
      return '<svg viewBox="0 0 800 860" aria-hidden="true">' + p + '</svg>';
    },

    relief: function (r) {
      var p = '', c, l;
      for (l = 0; l < 4; l++) {
        for (c = 0; c < 4; c++) {
          var x = 60 + c * 175, y = 70 + l * 185;
          p += '<rect class="tr" x="' + x + '" y="' + y + '" width="150" height="160"/>';
          var k = Math.floor(r() * 4), mx = x + 75, my = y + 80;
          if (k === 0) {
            p += '<circle class="tr" cx="' + mx + '" cy="' + my + '" r="34"/>' +
                 '<path class="tr" d="M' + (mx - 34) + ' ' + my + ' L' + (mx + 34) + ' ' + my + '"/>';
          } else if (k === 1) {
            p += '<path class="tr" d="M' + (mx - 36) + ' ' + (my + 32) + ' L' + mx + ' ' + (my - 36) +
                 ' L' + (mx + 36) + ' ' + (my + 32) + ' Z"/>';
          } else if (k === 2) {
            p += '<path class="tr" d="M' + (mx - 38) + ' ' + (my - 26) + ' Q' + mx + ' ' + (my + 46) + ' ' +
                 (mx + 38) + ' ' + (my - 26) + '"/>' +
                 '<path class="tr" d="M' + (mx - 20) + ' ' + (my - 4) + ' L' + (mx + 20) + ' ' + (my - 4) + '"/>';
          } else {
            p += '<rect class="tr" x="' + (mx - 30) + '" y="' + (my - 30) + '" width="60" height="60"/>' +
                 '<path class="tr" d="M' + (mx - 30) + ' ' + (my - 30) + ' L' + (mx + 30) + ' ' + (my + 30) + '"/>';
          }
        }
      }
      return '<svg viewBox="0 0 800 860" aria-hidden="true">' + p + '</svg>';
    },

    tata: function () {
      var p = '';
      /* coupe d'une maison-forteresse : les étages se lisent de bas en haut */
      p += '<path class="tr" d="M230 760 L230 380 Q230 300 320 300 L480 300 Q570 300 570 380 L570 760 Z"/>';
      p += '<path class="tr" d="M230 620 L570 620"/>';
      p += '<path class="tr" d="M230 500 L570 500"/>';
      p += '<path class="tr" d="M230 396 L570 396"/>';
      /* les greniers */
      p += '<path class="tr" d="M285 500 L285 430 Q285 400 320 400 Q355 400 355 430 L355 500"/>';
      p += '<path class="tr" d="M445 500 L445 430 Q445 400 480 400 Q515 400 515 430 L515 500"/>';
      /* la terrasse et l'échelle */
      p += '<path class="tr" d="M300 300 L300 250 M500 300 L500 250"/>';
      p += '<path class="tr" d="M610 760 L640 300"/>';
      p += '<path class="tr" d="M596 690 L634 686 M600 620 L638 616 M604 550 L642 546 M608 480 L646 476 M612 410 L650 406"/>';
      /* le sol et la cour */
      p += '<path class="tr" d="M90 760 L710 760"/>';
      p += '<circle class="tr" cx="150" cy="700" r="22"/>';
      return '<svg viewBox="0 0 800 860" aria-hidden="true">' + p + '</svg>';
    },

    courbes: function (r) {
      var p = '', i, j;
      for (i = 0; i < 11; i++) {
        var d = 'M-20 ' + (120 + i * 66);
        for (j = 1; j <= 6; j++) {
          var x = j * 140;
          var y = 120 + i * 66 + Math.sin(j * 1.4 + i * .8) * (26 + r() * 22);
          d += ' Q' + (x - 70) + ' ' + (y + 34).toFixed(0) + ' ' + x + ' ' + y.toFixed(0);
        }
        p += '<path class="tr" d="' + d + '"/>';
      }
      return '<svg viewBox="0 0 800 860" aria-hidden="true">' + p + '</svg>';
    },

    fleuve: function (r) {
      var p = '', i;
      for (i = 0; i < 16; i++) {
        var y = 200 + i * 32;
        var a = 14 + r() * 26;
        p += '<path class="tr" d="M-20 ' + y + ' Q200 ' + (y - a).toFixed(0) + ' 400 ' + y +
             ' T820 ' + y + '"/>';
      }
      p += '<path class="tr" d="M60 160 L740 160"/>';
      p += '<path class="tr" d="M60 730 L740 730"/>';
      return '<svg viewBox="0 0 800 860" aria-hidden="true">' + p + '</svg>';
    }
  };

  function poserMotifs() {
    stations.forEach(function (st, i) {
      var nom = st.getAttribute('data-motif');
      var f = MOTIFS[nom];
      if (!f) return;
      var boite = $('.st-motif', st);
      if (!boite) return;
      boite.innerHTML = f(alea(7919 + i * 131));
      /* la longueur réelle de chaque trait : le dessin se trace */
      if (!doux) {
        $$('.tr', boite).forEach(function (t) {
          var L = 900;
          try { L = t.getTotalLength ? Math.ceil(t.getTotalLength()) : 900; } catch (e) {}
          if (!L || !isFinite(L)) L = 900;
          t.style.setProperty('--L', L);
          t.style.transitionDelay = (Math.random() * .5).toFixed(2) + 's';
        });
      }
    });
  }

  /* ═══ 2 · LE RIDEAU ═════════════════════════════════════════
     Le compte tourne au MINUTEUR, jamais sur rAF : leçon Angy Art. */

  function rideau(apres) {
    var r = $('#rideau'), n = $('#rideauN');
    if (!r || doux) {
      if (r && r.parentNode) r.parentNode.removeChild(r);
      D.body.classList.remove('rideau-la');
      apres();
      return;
    }
    D.body.classList.add('rideau-la');
    requestAnimationFrame(function () { r.classList.add('tire'); });

    var PAS = 40, TOTAL = 25, i = 0;
    var tic = setInterval(function () {
      i += 1;
      var v = Math.min(700, Math.round(i * 700 / TOTAL));
      if (n) n.textContent = v;
      if (i < TOTAL) return;
      clearInterval(tic);
      r.classList.add('parti');
      D.body.classList.remove('rideau-la');
      apres();
      setTimeout(function () { if (r.parentNode) r.parentNode.removeChild(r); }, 1250);
    }, PAS);
  }

  /* ═══ 3 · LE SON, synthétisé (aucun fichier) ════════════════
     Rien ne sonne avant un geste : c'est la règle des navigateurs
     et c'est aussi la politesse. */

  var Son = (function () {
    var ctx = null, gain = null, actif = false, sources = [];

    function bruit(dur) {
      var n = Math.floor(ctx.sampleRate * dur);
      var b = ctx.createBuffer(1, n, ctx.sampleRate);
      var d = b.getChannelData(0);
      for (var i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
      return b;
    }

    function demarrer() {
      if (ctx) return;
      var AC = W.AudioContext || W.webkitAudioContext;
      if (!AC) return;
      ctx = new AC();

      /* silence d'amorçage : iOS n'ouvre la sortie qu'après un vrai son */
      var s0 = ctx.createBufferSource();
      s0.buffer = ctx.createBuffer(1, 1, 22050);
      s0.connect(ctx.destination); s0.start(0);

      gain = ctx.createGain();
      gain.gain.value = 0;
      var comp = ctx.createDynamicsCompressor();
      gain.connect(comp); comp.connect(ctx.destination);

      /* la nappe : un bruit filtré, dont la couleur suit la latitude */
      var src = ctx.createBufferSource();
      src.buffer = bruit(4); src.loop = true;
      var f = ctx.createBiquadFilter();
      f.type = 'lowpass'; f.frequency.value = 420; f.Q.value = 1.2;
      src.connect(f); f.connect(gain); src.start(0);
      sources.push({ src: src, filtre: f });

      /* une respiration lente */
      var lfo = ctx.createOscillator(), lg = ctx.createGain();
      lfo.frequency.value = 0.07; lg.gain.value = 190;
      lfo.connect(lg); lg.connect(f.frequency); lfo.start(0);

      actif = true;
      monter();
    }

    function monter() {
      if (!ctx || !gain) return;
      gain.gain.cancelScheduledValues(ctx.currentTime);
      gain.gain.setTargetAtTime(0.16, ctx.currentTime, 1.4);
    }
    function couper() {
      if (!ctx || !gain) return;
      gain.gain.cancelScheduledValues(ctx.currentTime);
      gain.gain.setTargetAtTime(0, ctx.currentTime, 0.4);
    }

    return {
      demarrer: demarrer,
      dispo: function () { return !!ctx; },
      basculer: function (muet) { if (muet) couper(); else monter(); },
      /* p va de 0 (l'océan) à 1 (le fleuve) : l'eau devient du vent */
      latitude: function (p) {
        if (!ctx || !sources.length) return;
        var f = sources[0].filtre;
        f.frequency.setTargetAtTime(360 + p * 1500, ctx.currentTime, 1.2);
        f.Q.setTargetAtTime(1.2 + p * 2.4, ctx.currentTime, 1.2);
      },
      actif: function () { return actif; }
    };
  })();

  /* ═══ 4 · LE DÉFILEMENT LISSÉ ═══════════════════════════════
     À la molette seulement. Au doigt, on laisse le navigateur :
     lui reprendre l'inertie tactile, c'est casser le site. */

  var lisse = { cible: 0, cour: 0, anim: false, actif: false };

  function hauteurMax() {
    return Math.max(0, D.documentElement.scrollHeight - W.innerHeight);
  }

  function boucleLisse() {
    lisse.cour += (lisse.cible - lisse.cour) * 0.115;
    if (Math.abs(lisse.cible - lisse.cour) < 0.4) {
      lisse.cour = lisse.cible;
      lisse.anim = false;
    }
    W.scrollTo(0, lisse.cour);
    if (lisse.anim) requestAnimationFrame(boucleLisse);
  }

  function surMolette(e) {
    if (e.ctrlKey) return;                  /* on ne vole pas le zoom */
    e.preventDefault();
    lisse.cible = clamp(lisse.cible + e.deltaY, 0, hauteurMax());
    if (!lisse.anim) { lisse.anim = true; requestAnimationFrame(boucleLisse); }
  }

  function activerLisse() {
    if (doux || !fin) return;
    lisse.cible = lisse.cour = W.scrollY;
    lisse.actif = true;
    W.addEventListener('wheel', surMolette, { passive: false });
  }

  function allerA(el) {
    if (!el) return;
    var y = el.getBoundingClientRect().top + W.scrollY - barreH;
    y = clamp(y, 0, hauteurMax());
    if (lisse.actif) {
      lisse.cible = y;
      if (!lisse.anim) { lisse.anim = true; requestAnimationFrame(boucleLisse); }
    } else {
      W.scrollTo({ top: y, behavior: doux ? 'auto' : 'smooth' });
    }
  }

  /* ═══ 5 · LES RÉVÉLATIONS ═══════════════════════════════════
     Balayage à chaque défilement, jamais un IntersectionObserver
     seul : un clic de menu saute des sections, et l'observer les
     laisserait invisibles pour toujours. */

  var revelables = [];

  function balayer() {
    var h = W.innerHeight, seuil = h * 0.86;
    for (var i = 0; i < revelables.length; i++) {
      var el = revelables[i];
      if (el.__vu) continue;
      var t = el.getBoundingClientRect().top;
      if (t < seuil) { el.classList.add('vue'); el.__vu = true; }
    }
  }

  /* ═══ 6 · LA JAUGE ══════════════════════════════════════════ */

  var jauge = $('#jauge'), jaugeN = $('#jaugeN'), jaugeA = $('#jaugeA');
  var KM_MAX = 700, R = 78, CIRC = 2 * Math.PI * R;
  var stationCour = -1;

  function construireJauge() {
    if (!jaugeA) return;
    var p = '', i;
    for (i = 0; i < 40; i++) {
      var a = (i / 40) * Math.PI * 2 - Math.PI / 2;
      var l = (i % 5 === 0) ? 9 : 5;
      var x1 = 100 + Math.cos(a) * (R + 7), y1 = 100 + Math.sin(a) * (R + 7);
      var x2 = 100 + Math.cos(a) * (R + 7 + l), y2 = 100 + Math.sin(a) * (R + 7 + l);
      p += '<line class="' + (i % 5 === 0 ? 'grad5' : 'grad') + '" x1="' + x1.toFixed(1) +
           '" y1="' + y1.toFixed(1) + '" x2="' + x2.toFixed(1) + '" y2="' + y2.toFixed(1) + '"/>';
    }
    p += '<circle class="anneau" cx="100" cy="100" r="' + R + '"/>';
    p += '<circle class="arc" id="jaugeArc" cx="100" cy="100" r="' + R +
         '" transform="rotate(-90 100 100)" stroke-dasharray="' + CIRC.toFixed(2) +
         '" stroke-dashoffset="' + CIRC.toFixed(2) + '"/>';
    jaugeA.innerHTML = p;
  }

  function majJauge() {
    if (!stations.length) return;
    var mil = W.innerHeight * 0.5, i, idx = 0, dedans = false;

    for (i = 0; i < stations.length; i++) {
      var b0 = stations[i].getBoundingClientRect();
      if (b0.top <= mil) idx = i;
      if (b0.top <= mil && b0.bottom > mil) { idx = i; dedans = true; break; }
    }

    var a = stations[idx];
    var kmA = parseFloat(a.getAttribute('data-km')) || 0;
    var km = kmA;

    /* Quand une station occupe le milieu de l'écran, la jauge affiche SON
       kilomètre exact : sinon elle contredit l'étiquette que le visiteur a
       sous les yeux. On n'interpole que dans les intervalles (halte, saut). */
    if (!dedans) {
      var b1 = stations[idx + 1];
      if (b1) {
        var ra = a.getBoundingClientRect(), rb = b1.getBoundingClientRect();
        var d = (rb.top - ra.bottom) || 1;
        var frac = clamp((mil - ra.bottom) / d, 0, 1);
        var kmB = parseFloat(b1.getAttribute('data-km')) || kmA;
        km = Math.round(kmA + (kmB - kmA) * frac);
      }
    }

    if (jaugeN) jaugeN.textContent = km;
    if (jauge) jauge.style.setProperty('--p', (km / KM_MAX).toFixed(4));
    var arc = $('#jaugeArc');
    if (arc) arc.setAttribute('stroke-dashoffset', (CIRC * (1 - km / KM_MAX)).toFixed(2));

    /* la couleur de la terre ne change QU'AU changement de station :
       réécrire une variable de :root à chaque image recalcule tout
       le document (leçon Hillary). */
    if (idx !== stationCour) {
      stationCour = idx;
      var terre = a.getAttribute('data-terre');
      if (terre) D.documentElement.style.setProperty('--terre', terre);
      Son.latitude(clamp(km / KM_MAX, 0, 1));
      rangerJauge(a);
    }
  }

  /* L'anneau se range du côté opposé au cartel. Sans ça il se pose sur
     l'avertissement de la Pendjari, dont le cartel est à gauche. */
  function rangerJauge(st) {
    if (!jauge) return;
    var large = D.documentElement.clientWidth;
    if (large <= 900) { jauge.style.setProperty('--jx', '0px'); return; }
    var cartelGauche = !!$('.st-in--g', st);
    var l = parseFloat(getComputedStyle(jauge).left) || 0;
    var w = jauge.offsetWidth || 108;
    var dec = cartelGauche ? Math.max(0, large - w - l * 2) : 0;
    jauge.style.setProperty('--jx', dec.toFixed(0) + 'px');
  }

  /* le fond clair ou sombre sous le curseur */
  function majFond() {
    var clairs = $$('.ha, .ca');
    var mil = W.innerHeight * 0.5, sur = false;
    for (var i = 0; i < clairs.length; i++) {
      var r = clairs[i].getBoundingClientRect();
      if (r.top < mil && r.bottom > mil) { sur = true; break; }
    }
    D.body.classList.toggle('sur-clair', sur);
  }

  /* ═══ 7 · LA CARTE DES HUIT LIEUX ═══════════════════════════ */

  function construireCarte() {
    var ul = $('#carteL'), bt = $('#ouvrirCarte'), pan = $('#carte');
    if (!ul || !bt || !pan) return;

    var h = '';
    stations.forEach(function (st) {
      var t = $('.st-t', st);
      var nom = t ? t.textContent.trim().replace(/\s+/g, ' ') : '';
      h += '<li><a class="carte-a" href="#' + st.id + '">' +
           '<span class="km">km ' + (st.getAttribute('data-km') || '0') + '</span>' +
           '<span class="nm">' + nom + '</span>' +
           '<span class="vb">' + (st.getAttribute('data-verbe') || '') + '</span></a></li>';
    });
    ul.innerHTML = h;

    function ouvrir(o) {
      bt.setAttribute('aria-expanded', o ? 'true' : 'false');
      if (o) {
        pan.hidden = false;
        requestAnimationFrame(function () { pan.classList.add('la'); });
      } else {
        pan.classList.remove('la');
        setTimeout(function () { if (bt.getAttribute('aria-expanded') === 'false') pan.hidden = true; }, 800);
      }
    }

    bt.addEventListener('click', function () {
      ouvrir(bt.getAttribute('aria-expanded') !== 'true');
    });

    ul.addEventListener('click', function (e) {
      var a = e.target.closest ? e.target.closest('a') : null;
      if (!a) return;
      e.preventDefault();
      ouvrir(false);
      var cible = D.getElementById(a.getAttribute('href').slice(1));
      setTimeout(function () { allerA(cible); balayer(); }, 220);
    });

    D.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && bt.getAttribute('aria-expanded') === 'true') ouvrir(false);
    });
  }

  /* ═══ 8 · LES VERBES ════════════════════════════════════════ */

  var sejours = {};   /* pour le carnet : le temps passé par lieu */

  /* ─ TENIR · la Porte ─────────────────────────────────────── */
  function verbeTenir() {
    var b = $('#tenirB'), j = $('#tenirJ'), l = $('#tenirL'), z = $('#tenir');
    if (!b || !j) return;
    var LONG = 289.03, DUREE = 3000;
    var t0 = 0, raf = 0, fini = false;

    function pose() {
      j.style.strokeDashoffset = LONG;
      if (l) l.textContent = 'Appuyer et tenir';
    }

    function boucle(t) {
      if (!t0) t0 = t;
      var p = clamp((t - t0) / DUREE, 0, 1);
      j.style.strokeDashoffset = (LONG * (1 - p)).toFixed(2);
      if (p >= 1) { termine(); return; }
      raf = requestAnimationFrame(boucle);
    }

    function termine() {
      fini = true;
      cancelAnimationFrame(raf);
      if (l) l.textContent = 'Vous pouvez remonter';
      z.classList.add('fini');
      setTimeout(function () {
        var s = D.getElementById('station-1');
        if (s) allerA(s);
      }, 900);
    }

    function debut(e) {
      if (fini) return;
      e.preventDefault();
      t0 = 0;
      raf = requestAnimationFrame(boucle);
    }
    function arret() {
      if (fini) return;
      cancelAnimationFrame(raf);
      t0 = 0;
      pose();
    }

    pose();
    b.addEventListener('pointerdown', debut);
    b.addEventListener('pointerup', arret);
    b.addEventListener('pointercancel', arret);
    b.addEventListener('pointerleave', arret);
    /* au clavier : espace ou entrée maintenus */
    b.addEventListener('keydown', function (e) {
      if ((e.key === ' ' || e.key === 'Enter') && !e.repeat) { e.preventDefault(); debut(e); }
    });
    b.addEventListener('keyup', arret);
    b.addEventListener('blur', arret);
  }

  /* ─ CHOISIR · Dantokpa ───────────────────────────────────── */
  function verbeChoisir() {
    var z = $('#choisir');
    if (!z || doux) return;
    var r = alea(4271), h = '', i;
    for (i = 0; i < 26; i++) {
      var w = 5 + r() * 13, ht = 4 + r() * 10;
      var x = r() * (100 - w), y = r() * (100 - ht);
      var d = (r() * 9).toFixed(1), du = (16 + r() * 20).toFixed(1);
      h += '<b style="left:' + x.toFixed(1) + '%;top:' + y.toFixed(1) + '%;width:' + w.toFixed(1) +
           '%;height:' + ht.toFixed(1) + '%;animation:flotte ' + du + 's ease-in-out ' + d + 's infinite alternate"></b>';
    }
    z.innerHTML = h;
    if (!$('#kfFlotte')) {
      var s = D.createElement('style');
      s.id = 'kfFlotte';
      s.textContent = '@keyframes flotte{from{transform:translate3d(0,0,0)}to{transform:translate3d(2.5%,-3%,0)}}';
      D.head.appendChild(s);
    }
  }

  /* ─ PAGAYER · Ganvié ─────────────────────────────────────── */
  function verbePagayer() {
    var p = $('#pagaieP');
    if (!p) return;
    var x = 0, v = 0, tire = false, xd = 0, x0 = 0, raf = 0, LIM = 0;

    function limite() { LIM = Math.max(60, p.clientWidth - 34); }

    function pose() {
      x = clamp(x, 0, LIM);
      p.style.setProperty('--x', x.toFixed(1) + 'px');
      p.setAttribute('aria-valuenow', Math.round((x / (LIM || 1)) * 100));
    }

    function inertie() {
      if (tire) { raf = 0; return; }
      v *= 0.93;
      x += v;
      if (x < 0) { x = 0; v = 0; }
      if (x > LIM) { x = LIM; v = 0; }
      pose();
      raf = Math.abs(v) > 0.15 ? requestAnimationFrame(inertie) : 0;
    }

    p.addEventListener('pointerdown', function (e) {
      limite(); tire = true; xd = e.clientX; x0 = x; v = 0;
      p.setPointerCapture && p.setPointerCapture(e.pointerId);
    });
    p.addEventListener('pointermove', function (e) {
      if (!tire) return;
      var nx = clamp(x0 + (e.clientX - xd), 0, LIM);
      v = nx - x; x = nx; pose();
    });
    function fin_(e) {
      if (!tire) return;
      tire = false;
      if (!raf && !doux) raf = requestAnimationFrame(inertie);
    }
    p.addEventListener('pointerup', fin_);
    p.addEventListener('pointercancel', fin_);

    p.addEventListener('keydown', function (e) {
      limite();
      if (e.key === 'ArrowRight') { x = clamp(x + 26, 0, LIM); pose(); e.preventDefault(); }
      if (e.key === 'ArrowLeft')  { x = clamp(x - 26, 0, LIM); pose(); e.preventDefault(); }
    });

    W.addEventListener('resize', function () { limite(); pose(); });
    limite(); pose();
  }

  /* ─ FROTTER · Abomey ─────────────────────────────────────── */
  function verbeFrotter() {
    var m = $('#frotterM');
    if (!m) return;

    var r = alea(9137), p = '', i;
    for (i = 0; i < 8; i++) {
      p += '<line class="mur" x1="0" y1="' + (i * 14) + '" x2="320" y2="' + (i * 14) + '" stroke-width="1"/>';
    }
    for (i = 0; i < 10; i++) {
      var cx = 22 + r() * 276, cy = 18 + r() * 92;
      var k = Math.floor(r() * 3);
      if (k === 0) p += '<circle class="grave" cx="' + cx.toFixed(0) + '" cy="' + cy.toFixed(0) + '" r="11" fill="none"/>';
      else if (k === 1) p += '<path class="grave" fill="none" d="M' + (cx - 13) + ' ' + (cy + 10) + ' L' + cx + ' ' + (cy - 12) + ' L' + (cx + 13) + ' ' + (cy + 10) + ' Z"/>';
      else p += '<path class="grave" fill="none" d="M' + (cx - 14) + ' ' + cy + ' Q' + cx + ' ' + (cy + 18) + ' ' + (cx + 14) + ' ' + cy + '"/>';
    }
    m.innerHTML = '<svg viewBox="0 0 320 130" preserveAspectRatio="none" aria-hidden="true">' + p + '</svg>' +
                  '<div class="voile"></div>';

    var v = $('.voile', m), R0 = 0, cible = 0, raf = 0;

    function anim() {
      R0 += (cible - R0) * 0.16;
      v.style.setProperty('--r', R0.toFixed(1) + 'px');
      raf = Math.abs(cible - R0) > 0.5 ? requestAnimationFrame(anim) : 0;
    }
    function pousse() { if (!raf) raf = requestAnimationFrame(anim); }

    m.addEventListener('pointermove', function (e) {
      var b = m.getBoundingClientRect();
      v.style.setProperty('--mx', (((e.clientX - b.left) / b.width) * 100).toFixed(1) + '%');
      v.style.setProperty('--my', (((e.clientY - b.top) / b.height) * 100).toFixed(1) + '%');
      cible = Math.max(b.width, b.height) * 0.42;
      pousse();
    });
    m.addEventListener('pointerleave', function () { cible = 0; pousse(); });
    m.addEventListener('pointerdown', function (e) { e.preventDefault(); });
  }

  /* ─ DESCENDRE · les Tata Somba ───────────────────────────── */
  function verbeDescendre() {
    var c = $('#tataC');
    if (!c) return;
    var n = $$('.tata-n', c);
    n.forEach(function (el) {
      el.addEventListener('click', function () { el.classList.toggle('ouvert'); });
    });
    /* la descente se fait aussi au défilement : on ouvre les niveaux
       l'un après l'autre à mesure que la section traverse l'écran */
    return function () {
      var b = c.getBoundingClientRect();
      var p = clamp((W.innerHeight * 0.82 - b.top) / (b.height || 1), 0, 1);
      var k = Math.floor(p * (n.length + 0.4));
      n.forEach(function (el, i) { el.classList.toggle('ouvert', i < k); });
    };
  }

  /* ─ ATTENDRE · la Pendjari ───────────────────────────────── */
  function verbeAttendre() {
    var sec = $('#station-6'), n = $('#attenteN');
    if (!sec || !n) return null;
    var s = 0, tic = null;
    return function () {
      var b = sec.getBoundingClientRect();
      var dedans = b.top < W.innerHeight * 0.5 && b.bottom > W.innerHeight * 0.5;
      if (dedans && !tic) {
        tic = setInterval(function () { s += 1; n.textContent = s; }, 1000);
      } else if (!dedans && tic) {
        clearInterval(tic); tic = null;
      }
    };
  }

  /* ═══ 9 · LA PARALLAXE PAR MOT ══════════════════════════════ */

  function couperEnMots() {
    $$('[data-mots]').forEach(function (el) {
      var mots = el.textContent.trim().split(/\s+/);
      el.innerHTML = mots.map(function (m, i) {
        var dx = (i % 3 === 0) ? '-2.2em' : (i % 3 === 1 ? '1.6em' : '-.8em');
        var d = (i * 0.045).toFixed(3);
        return '<span class="m" style="--dx:' + dx + ';transition-delay:' + d + 's,' + d + 's">' +
               m + '</span>';
      }).join(' ');
    });
  }

  /* ═══ 9 bis · LES TITRES QUI NE DÉBORDENT JAMAIS ════════════
     « Koutammakou » est plus long que son cartel : on rétrécit le
     titre jusqu'à ce qu'il tienne, plutôt que de couper un nom de
     lieu ou de choisir une taille au jugé. */

  function ajusterTitres() {
    $$('.st-t, .ha-t, .ca-t').forEach(function (t) {
      t.style.fontSize = '';
      var garde = 0;
      var f = parseFloat(getComputedStyle(t).fontSize) || 40;
      while (t.scrollWidth > t.clientWidth + 1 && f > 24 && garde < 60) {
        f -= 2;
        t.style.fontSize = f + 'px';
        garde += 1;
      }
    });
  }

  /* ═══ 10 · LE CARNET ════════════════════════════════════════ */

  function carnet() {
    var g = $('#caG'), t0 = Date.now();
    if (!g) return null;

    function rendre() {
      var sec = Math.round((Date.now() - t0) / 1000);
      var mn = Math.floor(sec / 60), ss = sec % 60;
      var vus = stations.filter(function (s) { return s.__vu; }).length;

      var plus = '', max = 0, k;
      for (k in sejours) if (sejours[k] > max) { max = sejours[k]; plus = k; }

      g.innerHTML =
        '<div class="ca-i"><b>' + vus + ' / ' + stations.length + '</b><span>lieux traversés</span></div>' +
        '<div class="ca-i"><b>' + (vus ? stations[Math.min(vus, stations.length) - 1].getAttribute('data-km') : 0) +
        '</b><span>kilomètres remontés</span></div>' +
        '<div class="ca-i"><b>' + mn + ' min ' + (ss < 10 ? '0' : '') + ss + '</b><span>passées ici</span></div>' +
        '<div class="ca-i"><b>' + (plus || '—') + '</b><span>là où vous êtes resté le plus</span></div>';

      var w = $('#partager');
      if (w) {
        var txt = 'J’ai remonté le Bénin, de la Porte du Non-Retour au fleuve. ' +
                  vus + ' lieux, ' + (vus ? stations[Math.min(vus, stations.length) - 1].getAttribute('data-km') : 0) +
                  ' km. Regarde : ' + W.location.href.split('#')[0];
        w.setAttribute('href', 'https://wa.me/?text=' + encodeURIComponent(txt));
      }
    }

    var r = $('#refaire');
    if (r) r.addEventListener('click', function () {
      var s = D.getElementById('station-0');
      if (s) allerA(s);
    });

    return rendre;
  }

  /* ═══ 11 · LE CURSEUR ═══════════════════════════════════════ */

  function curseur() {
    var c = $('#curseur');
    if (!c || !fin || doux) return;
    var x = -100, y = -100, cx = -100, cy = -100, raf = 0;

    function boucle() {
      cx += (x - cx) * 0.19;
      cy += (y - cy) * 0.19;
      c.style.setProperty('--cx', cx.toFixed(1) + 'px');
      c.style.setProperty('--cy', cy.toFixed(1) + 'px');
      raf = requestAnimationFrame(boucle);
    }

    W.addEventListener('pointermove', function (e) {
      x = e.clientX; y = e.clientY;
      if (!c.classList.contains('la')) c.classList.add('la');
      if (!raf) raf = requestAnimationFrame(boucle);
      var t = e.target;
      var gros = !!(t && t.closest && t.closest('a, button, .pagaie-p, .frotter-m, .tata-n'));
      c.classList.toggle('gros', gros);
    }, { passive: true });

    W.addEventListener('pointerleave', function () { c.classList.remove('la'); });
  }

  /* ═══ 12 · LE SEUIL D'ENTRÉE ════════════════════════════════ */

  function seuil(apres) {
    var z = $('#seuil'), b = $('#entrer');
    if (!z) { apres(false); return; }
    z.hidden = false;
    var passe = false;

    function entrer(avecSon) {
      if (passe) return;
      passe = true;
      if (avecSon) Son.demarrer();
      z.classList.add('parti');
      setTimeout(function () { z.hidden = true; }, 700);
      apres(avecSon);
    }

    if (b) b.addEventListener('click', function () { entrer(true); });
    /* on n'emprisonne personne : défiler entre aussi, sans le son */
    W.addEventListener('wheel', function () { entrer(false); }, { once: true, passive: true });
    W.addEventListener('touchmove', function () { entrer(false); }, { once: true, passive: true });
    W.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'PageDown' || e.key === ' ') entrer(false);
    }, { once: true });
  }

  /* ═══ 13 · LE SUIVI DU SÉJOUR ═══════════════════════════════ */

  function suivreSejour() {
    var dernier = null, t = Date.now();
    return function () {
      var mil = W.innerHeight * 0.5, cour = null;
      for (var i = 0; i < stations.length; i++) {
        var b = stations[i].getBoundingClientRect();
        if (b.top < mil && b.bottom > mil) {
          var tt = $('.st-t', stations[i]);
          cour = tt ? tt.textContent.trim().replace(/\s+/g, ' ') : null;
          break;
        }
      }
      var now = Date.now();
      if (dernier) sejours[dernier] = (sejours[dernier] || 0) + (now - t);
      t = now;
      dernier = cour;
    };
  }

  /* ═══ MISE EN MARCHE ════════════════════════════════════════ */

  function demarrer() {
    var an = $('#an');
    if (an) an.textContent = new Date().getFullYear();

    barreH = parseInt(getComputedStyle(D.documentElement)
             .getPropertyValue('--barre-h'), 10) || 60;

    /* le cartel alterne les côtés, comme le panneau de la vidéo 2 */
    stations.forEach(function (st, i) {
      var box = $('.st-in', st);
      if (box) box.classList.add(i % 2 ? 'st-in--d' : 'st-in--g');
    });

    poserMotifs();
    couperEnMots();
    ajusterTitres();
    if (D.fonts && D.fonts.ready) D.fonts.ready.then(ajusterTitres);
    construireJauge();
    construireCarte();
    verbeTenir();
    verbeChoisir();
    verbePagayer();
    verbeFrotter();
    curseur();

    var tacheTata = verbeDescendre();
    var tacheAttente = verbeAttendre();
    var tacheCarnet = carnet();
    var tacheSejour = suivreSejour();

    revelables = $$('.st, .ha, .saut, .ca');

    var enCours = false;
    function surDefilement() {
      if (enCours) return;
      enCours = true;
      requestAnimationFrame(function () {
        balayer();
        majJauge();
        majFond();
        if (tacheTata) tacheTata();
        if (tacheAttente) tacheAttente();
        if (tacheSejour) tacheSejour();
        if (!lisse.anim && lisse.actif) lisse.cible = lisse.cour = W.scrollY;
        enCours = false;
      });
    }

    W.addEventListener('scroll', surDefilement, { passive: true });
    W.addEventListener('resize', function () {
      barreH = parseInt(getComputedStyle(D.documentElement)
               .getPropertyValue('--barre-h'), 10) || 60;
      ajusterTitres();
      if (stationCour >= 0 && stations[stationCour]) rangerJauge(stations[stationCour]);
      surDefilement();
    }, { passive: true });

    rideau(function () {
      seuil(function () {
        $('#barre').classList.add('la');
        if (jauge) jauge.classList.add('la');
        activerLisse();
        balayer();
        majJauge();
        surDefilement();
      });
    });

    /* le bouton de son */
    var sb = $('#sonBtn');
    if (sb) sb.addEventListener('click', function () {
      if (!Son.dispo()) { Son.demarrer(); sb.setAttribute('aria-pressed', 'false'); return; }
      var muet = sb.getAttribute('aria-pressed') === 'true';
      sb.setAttribute('aria-pressed', muet ? 'false' : 'true');
      Son.basculer(!muet);
    });

    /* le carnet se recalcule quand on l'atteint */
    var ca = $('#carnet');
    if (ca && tacheCarnet) {
      W.addEventListener('scroll', function () {
        var b = ca.getBoundingClientRect();
        if (b.top < W.innerHeight && b.bottom > 0) tacheCarnet();
      }, { passive: true });
      tacheCarnet();
    }

    /* les ancres internes passent par notre défilement */
    D.addEventListener('click', function (e) {
      var a = e.target.closest ? e.target.closest('a[href^="#"]') : null;
      if (!a || a.closest('#carte')) return;
      var id = a.getAttribute('href').slice(1);
      if (!id) return;
      var el = D.getElementById(id);
      if (!el) return;
      e.preventDefault();
      allerA(el);
      balayer();
    });

    balayer();
  }

  if (D.readyState === 'loading') {
    D.addEventListener('DOMContentLoaded', demarrer);
  } else {
    demarrer();
  }
})();

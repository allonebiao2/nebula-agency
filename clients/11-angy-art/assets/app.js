/* ==================================================================
   ANGY ART — le comportement, écrit à la main.
   Défilement lissé, curseur suiveur, révélations au scroll, carrousel
   en coverflow, modale de demande : aucune bibliothèque, zéro Ko de
   dépendance. Tout ce qui suit ENRICHIT une page déjà lisible sans JS.
   ================================================================== */
(function () {
  'use strict';

  /* ================================================================
     ZONE À COMPLÉTER — c'est ici, et nulle part ailleurs.
     ================================================================ */

  /* LES MISES EN SITUATION.
     Ce sont ses VRAIS masques, photographiés dans des intérieurs de
     présentation montés. Preuve qu'ils sont d'elle : le terracotta à
     spirale de situ-1 est celui qu'elle peint dans « Le trait », et le
     jaune/orange de situ-2 est celui de la section « La démarche ».

     ⛔ JAMAIS un prix, JAMAIS une dimension, JAMAIS le mot « disponible ».
        Une mise en situation n'est pas un catalogue, et le cartel le dit.
     ⛔ JAMAIS un titre d'œuvre inventé : `t` décrit ce qu'on voit, rien de
        plus. Seule Angélique peut nommer une pièce.

     Le jour où ses photos d'œuvres arrivent (fond neutre, une pièce par
     image), elles vont dans un tableau ŒUVRES séparé, avec leur vrai titre,
     leur technique et leurs dimensions. Les deux ne se mélangent pas. */
  /* ⚠️ LA MARQUE DE VERSION DES IMAGES. À bumper en même temps que le `?v=`
     de index.html dès qu'une image change de contenu SANS changer de nom.
     Nos images portent `Cache-Control: immutable` pour un an : le 2026-08-08,
     Mongazi voyait encore l'ancienne image générée alors que le serveur
     envoyait déjà la vraie photo (MD5 identique au fichier du disque). Ce
     n'était ni le déploiement ni Cloudflare : c'était son propre navigateur. */
  var VER = '?v=20260822a';

  var SITUATIONS = [
    { f: "situ-1.webp", ar: "798/1004", t: "Deux visages, terre et blanc",
      s: "Socles dorés, tablette de marbre, mur de noyer." },
    { f: "situ-2.webp", ar: "4/5", t: "Le collier de perles",
      s: "Jaune et terre, tige serpentine, socle noir." },
    { f: "situ-3.webp", ar: "4/5", t: "Le bleu outremer",
      s: "Boucles vertes, tige en spirale, niche de pierre claire." },
    { f: "situ-4.webp", ar: "4/5", t: "Jaune et terre",
      s: "Socle clair, épis secs, lumière rasante de niche." },
    { f: "situ-5.webp", ar: "4/5", t: "Le visage terracotta",
      s: "Boucles jaunes, socle blanc, étagère de noyer." },
    { f: "situ-6.webp", ar: "4/5", t: "Le même, sur socle noir",
      s: "Travertin, vase d'épis, lumière chaude." }
  ];

  /* Les messages WhatsApp, un par porte d'entrée. Le numéro vit dans
     index.html : les liens fonctionnent même si ce fichier ne charge pas. */
  var MSG = {
    portfolio: "Bonjour Angélique, j'ai vu votre site. Pouvez-vous m'envoyer le portfolio complet des pièces disponibles ?",
    direct:    "Bonjour Angélique, j'ai vu votre site et je voudrais échanger avec vous."
  };

  /* ================================================================ */

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var doux = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fin = matchMedia('(hover:hover) and (pointer:fine)').matches;
  var petit = matchMedia('(max-width: 880px)').matches;

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c];
    });
  }

  /* ---------- 1. Les portes WhatsApp -------------------------------- */
  var NUM = '';
  $$('[data-wa]').forEach(function (a) {
    var base = (a.getAttribute('href') || '').split('?')[0];
    if (base.indexOf('wa.me') === -1) return;
    NUM = base;
    var m = MSG[a.getAttribute('data-wa')] || MSG.direct;
    a.setAttribute('href', base + '?text=' + encodeURIComponent(m));
    a.setAttribute('rel', 'noopener');
    a.setAttribute('target', '_blank');
  });

  /* ---------- 2. Longueur des tracés normalisée à 1 ------------------ */
  $$('.entailles path, .scene-tr path').forEach(function (p) {
    p.setAttribute('pathLength', '1');
  });

  /* ---------- 3. Le découpage en mots -------------------------------- */
  function decouper(el) {
    Array.prototype.slice.call(el.childNodes).forEach(function (nd) {
      if (nd.nodeType === 3) {
        if (!nd.textContent.trim()) return;
        var frag = document.createDocumentFragment();
        nd.textContent.split(/(\s+)/).forEach(function (t) {
          if (!t) return;
          if (!t.trim()) { frag.appendChild(document.createTextNode(t)); return; }
          var m = document.createElement('span'); m.className = 'mot';
          var i = document.createElement('span'); i.textContent = t;
          m.appendChild(i); frag.appendChild(m);
        });
        nd.parentNode.replaceChild(frag, nd);
      } else if (nd.nodeType === 1 && nd.tagName !== 'BR') {
        decouper(nd);
      }
    });
  }
  if (!doux) {
    $$('[data-mots]').forEach(function (el) {
      decouper(el);
      $$('.mot', el).forEach(function (m, i) { m.style.setProperty('--d', (i * 42) + 'ms'); });
    });
  }

  /* ---------- 4. Les révélations -------------------------------------
     Un balayage au défilement plutôt qu'un IntersectionObserver.
     Pourquoi : avec un observateur seul, un visiteur qui clique « L'ATELIER »
     saute par-dessus la démarche, l'observateur ne se déclenche jamais pour
     elle, et ses textes restent invisibles POUR TOUJOURS. Ici, tout ce qui
     est passé au-dessus de la ligne de flottaison est révélé, sauté ou non.
     Chaque élément n'est traité qu'une fois, et jamais rejoué en remontant. */
  (function revelations() {
    var restants = $$('[data-mots], .lab, .rv, .plein, .split-i, .split-t, .split-lg,'
      + ' .cit-i, .cit-a, .cars-b, .folio-d, .tags, .plein-d, .plein .pill,'
      + ' .temps-d, .tp,'
      /* ajoutés le 2026-08-21 : la signature « l'entaille » et les blocs de
         la section des créations personnalisées */
      + ' .ent, .perso-t, .deux li, .perso-go,'
      /* la section des œuvres : chaque cartel s'écrit quand sa pièce entre */
      + ' .oeu, .oeu-intro');
    if (doux) { restants.forEach(function (el) { el.classList.add('vu'); }); return; }

    var attente = false;
    function balayer() {
      attente = false;
      var seuil = innerHeight * 0.92;
      restants = restants.filter(function (el) {
        if (el.getBoundingClientRect().top >= seuil) return true;
        el.classList.add('vu');
        return false;
      });
      if (!restants.length) {
        removeEventListener('scroll', pousser);
        removeEventListener('resize', pousser);
      }
    }
    function pousser() {
      if (attente) return;
      attente = true;
      requestAnimationFrame(balayer);
    }
    addEventListener('scroll', pousser, { passive: true });
    addEventListener('resize', pousser, { passive: true });
    balayer();
  })();

  /* ---------- 4 bis. Le passage d'une section à l'autre ---------------
     Un volet de la couleur opposée couvre chaque section, puis se retire
     vers le haut quand elle entre : la section suivante a l'air de glisser
     par-dessus la précédente. Même balayage que les révélations, donc une
     section sautée par un clic de menu lève quand même son volet. */
  (function volets() {
    var restants = $$('.sec, .cit');
    if (doux) { restants.forEach(function (s) { s.classList.add('leve'); }); return; }

    var attente = false;
    function balayer() {
      attente = false;
      var seuil = innerHeight * 0.86;
      restants = restants.filter(function (s) {
        if (s.getBoundingClientRect().top >= seuil) return true;
        s.classList.add('leve');
        return false;
      });
      if (!restants.length) {
        removeEventListener('scroll', pousser);
        removeEventListener('resize', pousser);
      }
    }
    function pousser() {
      if (attente) return;
      attente = true;
      requestAnimationFrame(balayer);
    }
    addEventListener('scroll', pousser, { passive: true });
    addEventListener('resize', pousser, { passive: true });
    balayer();
  })();

  /* ---------- 5. Le rideau, puis le héros s'ouvre ---------------------
     Le rideau porte le nom, tire son filet, compte, puis se retire vers le
     haut. Le héros n'ouvre qu'APRÈS : ses lettres montent pendant que le
     panneau s'en va, c'est ce qui donne l'enchaînement. */
  (function ouverture() {
    var h = $('.hero');
    var r = $('#rideau'), n = $('#rideauN');

    function ouvrirHeros() { if (h) h.classList.add('ouvert'); }

    if (doux || !r) {
      if (r) r.remove();
      document.body.classList.remove('rideau-la');
      ouvrirHeros();
      return;
    }

    document.body.classList.add('rideau-la');
    requestAnimationFrame(function () { r.classList.add('tire'); });

    /* ⚠️ Le compte tourne au MINUTEUR, pas sur `requestAnimationFrame`.
       Mesuré le 2026-08-08 : avec rAF, le compteur atteignait 100 et le
       rideau partait en moins de 200 ms au lieu de 1 000. Un minuteur est
       plus grossier mais il tient la durée qu'on lui donne, et pour un
       compteur qui affiche des entiers la finesse de rAF n'apporte rien. */
    var PAS = 40, TOTAL = 25;             /* 25 x 40 ms = 1 s d'ouverture */
    var i = 0;
    var tic = setInterval(function () {
      i += 1;
      var v = Math.min(100, Math.round(i * 100 / TOTAL));
      if (n) n.textContent = (v < 10 ? '0' : '') + v;
      if (i < TOTAL) return;
      clearInterval(tic);
      r.classList.add('parti');
      document.body.classList.remove('rideau-la');
      ouvrirHeros();
      /* on le retire du document : un panneau plein écran, même parti,
         reste un calque que le navigateur compose à chaque image */
      setTimeout(function () { if (r.parentNode) r.parentNode.removeChild(r); }, 1300);
    }, PAS);
  })();

  /* ---------- 6. Le défilement lissé --------------------------------
     L'équivalent maison de Lenis : on interpole scrollTop, on ne
     transforme rien. Les éléments en position:fixed restent intacts. */
  var majCible = function () {};
  if (fin && !doux) {
    (function lisse() {
      var cible = window.scrollY, courant = window.scrollY, anime = false;
      document.documentElement.style.scrollBehavior = 'auto';

      function borne(v) {
        return Math.max(0, Math.min(document.documentElement.scrollHeight - innerHeight, v));
      }
      /* ⚠️ L'INTERPOLATION SE FAIT AU TEMPS, PAS À L'IMAGE. En avançant d'un
         cran fixe par image, le glissement dure deux fois plus longtemps sur
         une machine qui tourne à 30 images/s que sur une qui en fait 60 : le
         même clic « accueil » ramenait en haut ici, et s'arrêtait encore à
         284 px là-bas (mesuré le 2026-08-22, page d'accueil de 10 318 px).
         C'est le téléphone bas de gamme de Cotonou qui payait la différence.
         `k` est le même 0,095 rapporté à une image de 60 Hz. */
      var dernier = 0;
      function boucle(ts) {
        var dt = dernier ? Math.min(64, ts - dernier) : 16.7;
        dernier = ts;
        var k = 1 - Math.pow(1 - 0.095, dt / 16.7);
        courant += (cible - courant) * k;
        if (Math.abs(cible - courant) < 0.5) { courant = cible; anime = false; }
        window.scrollTo(0, courant);
        if (anime) requestAnimationFrame(boucle);
      }
      function lancer() {
        if (!anime) { anime = true; dernier = 0; requestAnimationFrame(boucle); }
      }

      majCible = function (v) { cible = borne(v); lancer(); };

      window.addEventListener('wheel', function (e) {
        if (e.ctrlKey) return;                                  /* le zoom reste le zoom */
        if (document.querySelector('dialog[open]')) return;     /* pas dans une modale */
        if (e.target.closest && e.target.closest('select')) return;
        e.preventDefault();
        cible = borne(cible + e.deltaY * (e.deltaMode === 1 ? 18 : 1));
        lancer();
      }, { passive: false });

      /* ⚠️ UNE FORCE EXTÉRIEURE PEUT DÉPLACER LA PAGE PENDANT QUE LE MOTEUR
         GLISSE : la recherche du navigateur, un lecteur d'écran, la touche Fin,
         le passage au clavier sur un bouton hors écran. Tant que `cible` n'était
         relue QUE `if (!anime)`, la boucle en cours ramenait la page à SON idée
         du bon endroit et le saut était annulé sans un mot. C'est le piège
         déjà documenté sur Au Braisé d'Or (Lenis interrompait tout
         `scrollIntoView`), retrouvé ici le 2026-08-21.
         On ne peut pas simplement adopter tout écart : une image perdue laisse
         la page sur le CHEMIN du moteur, et l'adopter arrêterait le glissement
         net au milieu. Alors on regarde OÙ : ce qui est entre `courant` et
         `cible` vient de nous, ce qui est ailleurs vient de quelqu'un d'autre,
         et c'est lui qui a raison. */
      window.addEventListener('scroll', function () {
        var y = window.scrollY;
        if (!anime) { cible = y; courant = y; return; }
        var bas = Math.min(courant, cible) - 12, haut = Math.max(courant, cible) + 12;
        if (y < bas || y > haut) { cible = borne(y); courant = y; }
      }, { passive: true });
      window.addEventListener('resize', function () { cible = borne(cible); }, { passive: true });
    })();
  }

  /* les ancres passent par le même moteur */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute('href').slice(1);
    if (!id) return;
    var c = document.getElementById(id);
    if (!c) return;
    e.preventDefault();
    /* ⚠️ On défile à la main, donc `scroll-margin-top` n'est PAS appliqué tout
       seul : il faut le lire et le retrancher. Sans ça, sur téléphone, cliquer
       une entrée du menu posait l'étiquette de section à 6 px sous la barre
       fixe (mesuré) : elle la touchait presque. Sur grand écran le défaut se
       cachait derrière le grand rembourrage des sections. */
    var marge = parseFloat(getComputedStyle(c).scrollMarginTop) || 0;
    var y = c.getBoundingClientRect().top + window.scrollY - marge;
    if (fin && !doux) majCible(y);
    else window.scrollTo({ top: y, behavior: doux ? 'auto' : 'smooth' });
    history.replaceState(null, '', '#' + id);
  });

  /* ---------- 7. Le curseur ------------------------------------------ */
  if (fin && !doux) {
    (function curseur() {
      var c = $('#cur'), t = $('#curT');
      if (!c) return;
      document.body.classList.add('cur-ok');
      var x = innerWidth / 2, y = innerHeight / 2, cx = x, cy = y, anime = false, ne = false;

      window.addEventListener('pointermove', function (e) {
        x = e.clientX; y = e.clientY;
        if (!ne) { ne = true; cx = x; cy = y; }      /* il naît sous la souris */
        c.classList.add('on');
        if (!anime) { anime = true; requestAnimationFrame(suivre); }
      }, { passive: true });

      function suivre() {
        cx += (x - cx) * 0.15;                    /* le lerp demandé */
        cy += (y - cy) * 0.15;
        c.style.transform = 'translate3d(' + cx.toFixed(2) + 'px,' + cy.toFixed(2) + 'px,0)';
        if (Math.abs(x - cx) > 0.3 || Math.abs(y - cy) > 0.3) requestAnimationFrame(suivre);
        else anime = false;                       /* la boucle s'arrête d'elle-même */
      }

      document.addEventListener('pointerover', function (e) {
        var z = e.target.closest && e.target.closest('[data-cur]');
        var lien = e.target.closest && e.target.closest('a,button,select');
        c.classList.toggle('gros', !!(z || lien));
        t.textContent = z ? z.getAttribute('data-cur') : '';
      });
      document.addEventListener('pointerleave', function () { c.classList.remove('on'); });
    })();
  }

  /* ---------- 8. Le parallaxe de l'image d'atelier -------------------- */
  if (!doux) {
    (function parallaxe() {
      var els = $$('[data-para] .scene');
      if (!els.length) return;
      var attente = false;
      function poser() {
        attente = false;
        els.forEach(function (el) {
          var r = el.parentNode.getBoundingClientRect();
          if (r.bottom < -200 || r.top > innerHeight + 200) return;
          var k = (r.top + r.height / 2 - innerHeight / 2) / innerHeight;
          el.style.transform = 'translate3d(0,' + (k * -34).toFixed(1) + 'px,0) scale(1.06)';
        });
      }
      addEventListener('scroll', function () {
        if (attente) return;
        attente = true; requestAnimationFrame(poser);
      }, { passive: true });
      poser();
    })();
  }

  /* ---------- 9. La barre de navigation ------------------------------ */
  (function navigation() {
    var nav = $('#nav'), b = $('#burger'), l = $('#navC');
    addEventListener('scroll', function () {
      if (nav) nav.classList.toggle('pose', scrollY > 40);
    }, { passive: true });
    if (!b || !l) return;
    function basculer(o) {
      b.setAttribute('aria-expanded', o ? 'true' : 'false');
      b.setAttribute('aria-label', o ? 'Fermer le menu' : 'Ouvrir le menu');
      l.classList.toggle('ouvert', o);
      document.body.classList.toggle('fige', o);
    }
    b.addEventListener('click', function () { basculer(b.getAttribute('aria-expanded') !== 'true'); });
    l.addEventListener('click', function (e) { if (e.target.closest('a')) basculer(false); });
    addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && b.getAttribute('aria-expanded') === 'true') { basculer(false); b.focus(); }
    });
  })();

  /* ---------- 10. LE CARROUSEL --------------------------------------- */
  (function carrousel() {
    var zone = $('#cars'), piste = $('#carsP');
    if (!zone || !piste) return;

    var data = SITUATIONS.filter(function (o) { return o && o.f; });
    if (!data.length) { zone.remove(); return; }

    /* le bloc de texte, à gauche du centre */
    var txt = document.createElement('div');
    txt.className = 'cars-t';
    zone.appendChild(txt);

    /* Le texte alternatif dit ce que c'est, et ce que ce n'est pas.
       Un lecteur d'écran ne doit pas croire à une fiche produit. */
    function legende(o) {
      return o.t + ", pièce d'Angélique Avocevou, en mise en situation. " + o.s;
    }

    piste.innerHTML = data.map(function (o, i) {
      return '<figure class="car car--photo" data-i="' + i + '">' +
        '<div class="car-c" style="--ar:' + esc(o.ar || '4/5') + '">' +
        '<img src="assets/images/situations/' + esc(o.f) + VER + '" alt="' + esc(legende(o)) +
        '" loading="lazy" decoding="async">' +
        '</div></figure>';
    }).join('');

    var cartes = $$('.car', piste);
    var actif = 0, n = cartes.length;
    var cpt = $('#carsC');

    function deux(v) { return (v < 10 ? '0' : '') + v; }

    function ecrire() {
      var o = data[actif];
      txt.classList.add('chg');
      setTimeout(function () {
        txt.innerHTML =
          '<p class="l">MISE EN SITUATION</p>' +
          '<p class="t">' + esc(o.t) + '</p>' +
          '<p class="s">' + esc(o.s) + '</p>';
        txt.classList.remove('chg');
      }, 230);
      if (cpt) cpt.innerHTML = deux(actif + 1) + ' <i>—</i> ' + deux(n);
    }

    function placer() {
      var pas = cartes[0].offsetWidth * 1.02;
      cartes.forEach(function (c, i) {
        var o = i - actif;
        if (o > n / 2) o -= n;
        if (o < -n / 2) o += n;
        var a = Math.abs(o);
        var sc = a === 0 ? 1 : (a === 1 ? 0.6 : 0.45);
        var op = a === 0 ? 1 : (a === 1 ? 0.55 : 0.22);
        var bl = a === 0 ? 0 : (a === 1 ? 3 : 5);
        var gs = a === 0 ? 0 : (a === 1 ? 0.15 : 0.35);
        c.style.setProperty('--tx', (o * pas).toFixed(1) + 'px');
        c.style.setProperty('--sc', sc);
        c.style.setProperty('--op', op);
        c.style.setProperty('--bl', bl + 'px');
        c.style.setProperty('--gs', gs);
        c.classList.toggle('car--act', a === 0);
        c.setAttribute('aria-hidden', a === 0 ? 'false' : 'true');
      });
    }

    function aller(i) { actif = (i + n) % n; placer(); ecrire(); }

    $('#carPrev').addEventListener('click', function () { aller(actif - 1); });
    $('#carNext').addEventListener('click', function () { aller(actif + 1); });
    addEventListener('resize', placer, { passive: true });

    /* le glissement du doigt */
    var dx = 0, dep = false;
    zone.addEventListener('pointerdown', function (e) { dep = true; dx = e.clientX; });
    zone.addEventListener('pointerup', function (e) {
      if (!dep) return;
      dep = false;
      var d = e.clientX - dx;
      if (Math.abs(d) > 42) aller(actif + (d < 0 ? 1 : -1));
      else ouvrirLoupe(actif);
    });
    zone.addEventListener('pointercancel', function () { dep = false; });

    aller(0);

    /* la vue en grand */
    var d = $('#loupe'), f = $('#loupeF'), cap = $('#loupeCap');
    var img = null;
    function ouvrirLoupe(i) {
      if (!d || !d.showModal) return;
      if (!img) { img = document.createElement('img'); f.insertBefore(img, cap); }
      var o = data[i];
      img.src = 'assets/images/situations/' + o.f + VER;
      img.alt = legende(o);
      /* même en grand, le cartel rappelle ce que l'image est */
      cap.textContent = 'MISE EN SITUATION · ' + o.t.toUpperCase();
      d.showModal();
      document.body.classList.add('fige');
    }
    if (d) {
      $('#loupeX').addEventListener('click', function () { d.close(); });
      d.addEventListener('click', function (e) { if (e.target === d) d.close(); });
      d.addEventListener('close', function () { document.body.classList.remove('fige'); });
    }
  })();

  /* ---------- 11. LA MODALE : la demande de visite -------------------- */
  (function modale() {
    var d = $('#mod');
    if (!d || !d.showModal) return;
    var f = $('#modF'), err = $('#modE'), ok = $('#modOk');
    var champs = { cherche: $('#chCherche'), format: $('#chFormat'), quand: $('#chQuand') };
    var dernier = null;

    $$('[data-modale]').forEach(function (b) {
      b.addEventListener('click', function () {
        dernier = b;
        ok.hidden = true; err.hidden = true;
        champs.cherche.parentNode.classList.remove('mal');
        d.showModal();
        document.body.classList.add('fige');
      });
    });

    function fermer() { d.close(); }
    $('#modX').addEventListener('click', fermer);
    d.addEventListener('click', function (e) { if (e.target === d) fermer(); });
    d.addEventListener('close', function () {
      document.body.classList.remove('fige');
      if (dernier) dernier.focus();
    });

    champs.cherche.addEventListener('change', function () {
      if (champs.cherche.value) { err.hidden = true; champs.cherche.parentNode.classList.remove('mal'); }
    });

    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!champs.cherche.value) {
        err.hidden = false;
        champs.cherche.parentNode.classList.add('mal');
        champs.cherche.focus();
        return;
      }
      var l = ["Bonjour Angélique, j'ai vu votre site."];
      l.push('Ce que je cherche : ' + champs.cherche.value + '.');
      if (champs.format.value) l.push('Format ou espace : ' + champs.format.value + '.');
      if (champs.quand.value) l.push('Quand : ' + champs.quand.value + '.');
      l.push('Pouvez-vous me dire comment on avance ?');
      var url = (NUM || 'https://wa.me/2290152006490') + '?text=' + encodeURIComponent(l.join('\n'));
      ok.hidden = false;
      window.open(url, '_blank', 'noopener');
    });
  })();

  /* ---------- 11bis. LE PROJET DE CRÉATION PERSONNALISÉE --------------
     Les 15 questions du brief d'Angélique, en trois temps.

     ⚠️ CE FORMULAIRE NE « SOUMET » RIEN, et c'est volontaire. Le site est
     statique : pas de serveur, pas de base, pas de boîte mail. Il RÉDIGE le
     brief et ouvre la conversation WhatsApp d'Angélique avec le texte déjà
     écrit. Un bouton « Envoyer » qui ferait semblant d'envoyer serait le
     pire des défauts : le client croirait sa demande partie.

     ⚠️ LA QUESTION 11 (téléversement) DEVIENT UNE PHRASE. On ne peut pas
     recevoir un fichier sans serveur. Plutôt qu'un bouton « Parcourir » qui
     n'enverrait rien, on dit au client de joindre ses photos dans la
     conversation — au Bénin c'est de toute façon le geste naturel — et le
     message le rappelle à Angélique pour qu'elle les attende.

     ⚠️ LE NOM ET LA DATE SONT DANS LE MESSAGE. Le brief demande de pouvoir
     identifier une demande par le nom du client et sa date : sans base de
     données, c'est le message lui-même qui les porte. */
  (function personnalise() {
    var d = $('#per');
    if (!d) return;
    var f = $('#perF'), err = $('#perE'), ok = $('#perOk');
    var prec = $('#perPrec'), suiv = $('#perSuiv'), go = $('#perGo');
    var etapes = $$('.etp', f), pastilles = $$('#perPas li');
    var pas = 1, dernier = null;
    var v = function (id) { var e = $(id); return e ? String(e.value || '').trim() : ''; };

    function montrer() {
      etapes.forEach(function (e) { e.hidden = (+e.dataset.etp !== pas); });
      pastilles.forEach(function (li, i) { li.classList.toggle('pas--on', i <= pas - 1); });
      prec.hidden = pas === 1;
      suiv.hidden = pas === 3;
      go.hidden = pas !== 3;
      err.hidden = true;
      /* on remonte en haut de la modale : au troisième temps, rester en bas
         donnait l'impression que rien ne s'était passé */
      d.scrollTop = 0;
    }
    function refus(msg, id) {
      err.textContent = msg; err.hidden = false;
      var e = $(id); if (e) { e.parentNode.classList.add('mal'); e.focus(); }
    }
    /* on nettoie le liseré rouge dès que le visiteur corrige */
    f.addEventListener('input', function (e) {
      if (e.target && e.target.parentNode) e.target.parentNode.classList.remove('mal');
      err.hidden = true;
    });

    /* les deux champs qui n'apparaissent que si on en a besoin */
    var t = $('#pType'), tw = $('#pTypeAW');
    if (t && tw) t.addEventListener('change', function () { tw.hidden = t.value !== 'Autre'; });
    var dm = $('#pDim'), dw = $('#pDimW');
    if (dm && dw) dm.addEventListener('change', function () {
      dw.hidden = dm.value.indexOf('idée') === -1;
    });

    $$('[data-perso]').forEach(function (b) {
      b.addEventListener('click', function () {
        dernier = b; pas = 1; ok.hidden = true; montrer();
        d.showModal(); document.body.classList.add('fige');
      });
    });
    $('#perX').addEventListener('click', function () { d.close(); });
    d.addEventListener('click', function (e) { if (e.target === d) d.close(); });
    d.addEventListener('close', function () {
      document.body.classList.remove('fige');
      if (dernier) dernier.focus();
    });

    prec.addEventListener('click', function () { if (pas > 1) { pas--; montrer(); } });
    suiv.addEventListener('click', function () {
      if (pas === 1 && !v('#pHist')) {
        return refus("Racontez-moi votre histoire, même en deux lignes : c'est d'elle que naît l'œuvre.", '#pHist');
      }
      if (pas < 3) { pas++; montrer(); }
    });

    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!v('#pNom')) return refus('Il me faut votre nom pour vous répondre.', '#pNom');
      if (!v('#pTel') && !v('#pMail')) {
        return refus('Un numéro WhatsApp ou une adresse e-mail, au choix : sans ça je ne peux pas revenir vers vous.', '#pTel');
      }
      var l = ['Bonjour Angélique, je viens de votre site.',
               'Je souhaite une CRÉATION PERSONNALISÉE.', ''];
      function ligne(t, x) { if (x) l.push(t + ' : ' + x); }

      l.push('— MON HISTOIRE —');
      var ty = v('#pType');
      if (ty === 'Autre' && v('#pTypeA')) ty = v('#pTypeA');
      ligne("Type d'œuvre", ty);
      ligne('Destinée', v('#pPour'));
      ligne("L'histoire", v('#pHist'));
      ligne('À représenter', v('#pQui'));
      ligne('Éléments à faire apparaître', v('#pElem'));
      ligne('Ce que je veux transmettre', v('#pSens'));

      l.push('', '— MA VISION —');
      ligne('Couleurs', v('#pCoul'));
      ligne('À éviter', v('#pEvit'));
      ligne('Liberté artistique', v('#pLib'));
      ligne("Une œuvre qui m'inspire", v('#pInsp'));
      var dims = v('#pDim');
      if (v('#pDimL') && v('#pDimH')) dims = v('#pDimL') + ' x ' + v('#pDimH') + ' cm';
      ligne('Dimensions', dims);
      ligne('Où elle sera exposée', v('#pLieu'));

      l.push('', '— MON PROJET —');
      ligne('Budget', v('#pBud'));
      var q = v('#pDate');
      if (q) {
        var p2 = q.split('-');
        q = p2.length === 3 ? p2[2] + '/' + p2[1] + '/' + p2[0] : q;
      }
      if (v('#pOcc')) q = (q ? q + ' ' : '') + '(' + v('#pOcc') + ')';
      ligne('Date souhaitée', q);

      l.push('', '— MOI —');
      ligne('Nom', v('#pNom'));
      ligne('WhatsApp ou téléphone', v('#pTel'));
      ligne('E-mail', v('#pMail'));
      ligne('Ville et pays', v('#pVille'));
      ligne('Me répondre par', v('#pPref'));

      var n = new Date();
      var d2 = function (x) { return (x < 10 ? '0' : '') + x; };
      l.push('', 'Demande envoyée le ' + d2(n.getDate()) + '/' + d2(n.getMonth() + 1)
             + '/' + n.getFullYear() + '.');
      if ($('#pPh') && $('#pPh').checked) {
        l.push('Je vous envoie mes photographies et mes références juste après ce message.');
      }

      var url = (NUM || 'https://wa.me/2290152006490') + '?text=' + encodeURIComponent(l.join('\n'));
      ok.hidden = false;
      window.open(url, '_blank', 'noopener');
    });

    montrer();
  })();

  /* ---------- 12. L'ambiance de l'atelier -----------------------------
     Synthétisée : aucun fichier, aucun droit à payer, 0 Ko de réseau.
     Éteinte par défaut. Jamais un son sans un geste de l'utilisateur. */
  (function ambiance() {
    var b = $('#fabSon');
    if (!b) return;
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) { b.hidden = true; return; }

    var ctx = null, maitre = null, minuteur = null, allume = false;
    var VOL = petit ? 0.15 : 0.10;
    var NOTES = [110, 146.83, 164.81, 220, 246.94, 293.66];

    function batir() {
      ctx = new AC();
      var bf = ctx.createBuffer(1, 1, 22050), s = ctx.createBufferSource();
      s.buffer = bf; s.connect(ctx.destination); s.start(0);   /* déblocage iOS */

      var comp = ctx.createDynamicsCompressor();
      comp.threshold.value = -26; comp.knee.value = 22; comp.ratio.value = 8;
      comp.attack.value = 0.006; comp.release.value = 0.3;
      maitre = ctx.createGain(); maitre.gain.value = 0;
      maitre.connect(comp); comp.connect(ctx.destination);

      var filtre = ctx.createBiquadFilter();
      filtre.type = 'lowpass'; filtre.frequency.value = 420; filtre.Q.value = 0.6;
      filtre.connect(maitre);

      [55, 82.41, 110].forEach(function (fr, i) {
        var o = ctx.createOscillator(), g = ctx.createGain();
        o.type = i === 2 ? 'triangle' : 'sine';
        o.frequency.value = fr * (1 + (i - 1) * 0.0016);
        g.gain.value = [0.5, 0.3, 0.14][i];
        o.connect(g); g.connect(filtre); o.start();
      });

      var nb = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate), dd = nb.getChannelData(0);
      for (var i = 0; i < dd.length; i++) dd[i] = (Math.random() * 2 - 1) * 0.5;
      var src = ctx.createBufferSource(); src.buffer = nb; src.loop = true;
      var bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 620; bp.Q.value = 0.5;
      var ng = ctx.createGain(); ng.gain.value = 0.02;
      src.connect(bp); bp.connect(ng); ng.connect(maitre); src.start();

      var lfo = ctx.createOscillator(), lg = ctx.createGain();
      lfo.frequency.value = 0.035; lg.gain.value = 170;
      lfo.connect(lg); lg.connect(filtre.frequency); lfo.start();
    }

    function goutte() {
      if (!allume || !ctx) return;
      var fr = NOTES[(Math.random() * NOTES.length) | 0];
      var o = ctx.createOscillator(), g = ctx.createGain(), t = ctx.currentTime;
      o.type = 'sine'; o.frequency.value = fr;
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(0.07, t + 0.05);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 3.4);
      o.connect(g); g.connect(maitre); o.start(t); o.stop(t + 3.6);
      minuteur = setTimeout(goutte, 7000 + Math.random() * 11000);
    }

    b.addEventListener('click', function () {
      if (allume) {
        allume = false; clearTimeout(minuteur);
        maitre.gain.cancelScheduledValues(ctx.currentTime);
        maitre.gain.setValueAtTime(maitre.gain.value, ctx.currentTime);
        maitre.gain.linearRampToValueAtTime(0.0001, ctx.currentTime + 0.7);
        b.setAttribute('aria-pressed', 'false');
        b.setAttribute('aria-label', "Activer l'ambiance sonore de l'atelier");
      } else {
        if (!ctx) batir();
        if (ctx.state === 'suspended') ctx.resume();
        allume = true;
        maitre.gain.cancelScheduledValues(ctx.currentTime);
        maitre.gain.setValueAtTime(maitre.gain.value, ctx.currentTime);
        maitre.gain.linearRampToValueAtTime(VOL, ctx.currentTime + 1.6);
        minuteur = setTimeout(goutte, 3200);
        b.setAttribute('aria-pressed', 'true');
        b.setAttribute('aria-label', "Couper l'ambiance sonore de l'atelier");
      }
    });

    document.addEventListener('visibilitychange', function () {
      if (!ctx || !allume) return;
      document.hidden ? ctx.suspend() : ctx.resume();
    });
  })();

})();

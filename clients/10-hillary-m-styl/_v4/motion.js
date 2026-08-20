/* ==================================================================
   HILLARY M. STYL — V4 « LA COUPE » · le mouvement
   Lenis, GSAP, ScrollTrigger, SplitText et Swiper réécrits à la main.
   Aucune bibliothèque : règle NEBULA + 4G et Android d'entrée de gamme.
   ================================================================== */
(function () {
  'use strict';

  /* ================================================================
     LES IMAGES — c'est ici, et nulle part ailleurs.

     Chaque entrée a un champ `f`. Tant qu'il est vide, l'emplacement
     montre un dessin au trait. Dès qu'on met un nom de fichier, la
     photo prend sa place : rien d'autre à toucher.

     Les fichiers vont dans  assets/images/  et sont injectés en base64
     par _build.py (marqueurs), ou référencés en relatif si le site
     passe en multi-fichiers.

     ⛔ Aucune photo générée par IA présentée comme une pièce vendable.
     ================================================================ */

  /* --- 1 · LE HÉROS : 4 mannequins, fond blanc uni impératif --- */
  var HERO = [
    { f:'hero-1.webp', c:'#0b2d92', col:'Robe de cérémonie', mat:'Sur-mesure · 2 semaines',
      t:'Robe de cérémonie',  d:"Bustier structuré, jupe à volants de satin, gele assorti." },
    { f:'hero-2.webp', c:'#ae6e0d', col:"L'ensemble Mira",   mat:'Sur-mesure · 2 semaines',
      t:"L'ensemble Mira",    d:"Haut à manches ballon et jupe à volants étagés. Cérémonie, cocktail, dîner." },
    { f:'hero-3.webp', c:'#275eb7', col:'Ensemble JOSY',     mat:'Fait main · 2 semaines',
      t:'Ensemble JOSY',      d:"Pantalon large, empiècements peints, ceinture corset lacée. Fait main." },
    { f:'hero-4.webp', c:'#0e85b7', col:'Robe de ville',     mat:'Sur-mesure · 2 semaines',
      t:'Robe de ville',      d:"Dos nu, wax à feuillages et panneaux de satin qui s'ouvrent à la marche." },
    /* ── Ajoutées le 2026-08-17. Le héros ne montrait que 4 pièces sur les 8
       du catalogue : les quatre reçues le 2026-08-10 n'y étaient jamais
       passées. On prend les trois plus fortes, et on garde la quatrième
       (la robe à tulle) au seul carrousel : son violet doublait celui de la
       robe de cérémonie violette, et deux nappes identiques qui se suivent
       ne se voient pas.
       ⚠️ Elles pointent sur `piece-*.webp` et non sur un `hero-*.webp` : c'est
       la MÊME photo détourée, en 950 px de haut. La redécouper en WebP une
       seconde fois ne ferait que la dégrader. */
    { f:'piece-violette.webp', c:'#6b3065', col:'Cérémonie',      mat:'Sur-mesure · 2 semaines',
      t:'Robe de cérémonie violette', d:"Buste ajusté, manches ballon, jupe longue à volants dans un wax à fougères. Le dos se lace en corset." },
    { f:'piece-orange.webp',   c:'#925437', col:'Sur-mesure',     mat:'Sur-mesure · 2 semaines',
      t:'Robe Naja',           d:"Bustier à découpe sous la poitrine, manches détachées des épaules, jupe courte très ample." },
    { f:'piece-verte.webp',    c:'#7e6730', col:'Sur-mesure',     mat:'Sur-mesure · 2 semaines',
      t:'Robe de ville verte', d:"Une seule épaule, nouée sur le côté. La taille descend bas, la jupe est froncée et très ample." },

    { f:'piece-coeurs.webp', c:'#952838', col:'Fait main', mat:'Fait main · 2 semaines',
      t:"Tailleur Cœurs", d:"Veste cintrée à revers et épaules structurées, pantalon large assorti, wax bordeaux à cœurs." },
    { f:'piece-emeraude.webp', c:'#136b16', col:'Sur-mesure', mat:'Sur-mesure · 2 semaines',
      t:"Robe Émeraude", d:"Coupe courte ajustée, manches longues, grands motifs verts et jaunes cernés de noir." },
    { f:'piece-jean.webp', c:'#971f25', col:'Sur-mesure', mat:'Sur-mesure · 2 semaines',
      t:"Ensemble Jean", d:"Haut court épaules dénudées à manches ballon, jupe longue à volants montée sur un empiècement en jean." },
    { f:'piece-lacee.webp', c:'#35196b', col:'Sur-mesure', mat:'Sur-mesure · 2 semaines',
      t:"Robe Lacée", d:"Épaules dénudées à fines bretelles, manches ballon, basque à la taille, dos lacé au ruban." },
    { f:'piece-noeud.webp', c:'#ad1a24', col:'Sur-mesure', mat:'Sur-mesure · 2 semaines',
      t:"Ensemble Nœud", d:"Haut dos nu à col, noué dans le dos, et pantalon large avec un pan de wax rouge et blanc." },
    { f:'piece-orange-uni.webp', c:'#ad4c1e', col:'Sur-mesure', mat:'Sur-mesure · 2 semaines',
      t:"Ensemble Orange", d:"Bustier froncé à lien au cou, découpes sur les côtés, bas long et très ample en tissu uni." },
    { f:'piece-organza.webp', c:'#ad1e1a', col:'Cérémonie', mat:'Sur-mesure · 2 semaines',
      t:"Robe de ville organza", d:"Manches ballon détachées des épaules, col en organza froncé, découpe à la taille, dos lacé au ruban et jupon d'organza sous un wax rouge." },
    { f:'piece-sirene.webp', c:'#31166b', col:'Cérémonie', mat:'Sur-mesure · 2 semaines',
      t:"Robe Sirène", d:"Fourreau en wax violet, volants bleu roi en bordure et le long de la fente, traîne et foulard assorti." },
    { f:'piece-soleil.webp', c:'#ad1a21', col:'Cérémonie', mat:'Sur-mesure · 2 semaines',
      t:"Robe Soleil", d:"Épaules drapées à cordons et pompons, ceinture drapée, jupe très ample en bazin teint rouge et or." }
  ];
  /* --- 3 · LES COLLECTIONS : 6 à 8 pièces phares --- */
  /* ⛔ LE CARROUSEL NE PORTE QUE SES VRAIES PIÈCES. Les vêtements générés en
     ont été retirés le 2026-08-06 : un vêtement sans prix dans un carrousel
     qui mène au catalogue reste une promesse. Ici, tout est réel. */
  var COLLECTIONS = [
    { f:'piece-ceremonie.webp', l:'Cérémonie',    t:'Robe de cérémonie', s:'Bustier structuré, jupe à volants de satin' },
    { f:'piece-mira.webp', l:'Sur-mesure',   t:"L'ensemble Mira",   s:'Haut à manches ballon, jupe à volants étagés' },
    { f:'piece-josy.webp', l:'Fait main',    t:'Ensemble JOSY',     s:'Pantalon large, empiècements peints, corset lacé' },
    { f:'piece-ville.webp', l:'Sur-mesure',   t:'Robe de ville',     s:'Dos nu, wax à feuillages et panneaux de satin' },
    { f:'piece-violette.webp', f2:'piece-violette-dos.webp', l:'Cérémonie',  t:'Robe de cérémonie violette', s:'Manches ballon, jupe à volants, dos lacé en corset' },
    { f:'piece-orange.webp', f2:'piece-orange-dos.webp', l:'Sur-mesure',   t:'Robe Naja',         s:'Bustier découpé, manches détachées, jupe très ample' },
    { f:'piece-verte.webp', f2:'piece-verte-dos.webp', l:'Sur-mesure',    t:'Robe de ville verte', s:'Une épaule nouée, taille basse, jupe froncée' },
    { f:'piece-tulle.webp', f2:'piece-tulle-dos.webp', l:'Sur-mesure',    t:'Robe de ville à tulle', s:'Col montant noué, dos dégagé, volant de tulle violet' },
    { f:'piece-organza.webp', f2:'piece-organza-dos.webp', l:'Cérémonie', t:"Robe de ville organza", s:'Manches ballon détachées des épaules, col en organza' },
    { f:'piece-noeud.webp', f2:'piece-noeud-dos.webp', l:'Sur-mesure', t:"Ensemble Nœud", s:'Haut dos nu à col, noué dans le dos, et pantalon large' },
    { f:'piece-lacee.webp', f2:'piece-lacee-dos.webp', l:'Sur-mesure', t:"Robe Lacée", s:'Épaules dénudées à fines bretelles, manches ballon' },
    { f:'piece-coeurs.webp', l:'Fait main', t:"Tailleur Cœurs", s:'Veste cintrée à revers et épaules structurées, pantalon' },
    { f:'piece-jean.webp', f2:'piece-jean-dos.webp', l:'Sur-mesure', t:"Ensemble Jean", s:'Haut court épaules dénudées à manches ballon, jupe' },
    { f:'piece-sirene.webp', l:'Cérémonie', t:"Robe Sirène", s:'Fourreau en wax violet, volants bleu roi en bordure et' },
    { f:'piece-emeraude.webp', l:'Sur-mesure', t:"Robe Émeraude", s:'Coupe courte ajustée, manches longues, grands motifs' },
    { f:'piece-orange-uni.webp', l:'Sur-mesure', t:"Ensemble Orange", s:'Bustier froncé à lien au cou, découpes sur les côtés' },
    { f:'piece-soleil.webp', l:'Cérémonie', t:"Robe Soleil", s:'Épaules drapées à cordons et pompons, ceinture drapée' }
  ];
  /* ================================================================ */

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var doux = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fin = matchMedia('(hover:hover) and (pointer:fine)').matches;

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c];
    });
  }
  function d2(n) { return (n < 10 ? '0' : '') + n; }

  /* la robe au trait, quand il n'y a pas encore de photo */
  var SIL = '<div class="sil"><svg viewBox="0 0 120 170" fill="none" aria-hidden="true">'
    + '<path d="M46 26c0-8 6-14 14-14s14 6 14 14"/>'
    + '<path d="M46 26 24 44l10 13 12-10"/><path d="M74 26l22 18-10 13-12-10"/>'
    + '<path d="M46 33v34l-8 91h44l-8-91V33"/>'
    + '<path d="M40 78h40"/><path d="M44 112h32"/>'
    + '</svg></div>';

  /* ---------- 1 · LE LOADER — la coupe qui s'ouvre ---------------- */
  (function loader() {
    var l = $('#load'), h = $('#hero');
    if (!l) { if (h) h.classList.add('ouvert'); return; }
    if (doux) { l.classList.add('fini'); if (h) h.classList.add('ouvert'); return; }
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { l.classList.add('vue'); });
    });
    setTimeout(function () {
      l.classList.add('parti');
      if (h) h.classList.add('ouvert');
    }, 1750);
    setTimeout(function () { l.classList.add('fini'); }, 2900);
    /* filet de sécurité : jamais de rideau bloqué à l'écran */
    setTimeout(function () {
      l.classList.add('fini');
      if (h) h.classList.add('ouvert');
    }, 4800);
  })();

  /* ---------- 2 · LE DÉCOUPAGE EN MOTS (SplitText réécrit) -------- */
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
      $$('.mot', el).forEach(function (m, i) { m.style.setProperty('--d', (i * 40) + 'ms'); });
    });
  }

  /* ---------- 3 · LES RÉVÉLATIONS — un balayage, pas un observateur
     Un IntersectionObserver laisse invisibles POUR TOUJOURS les
     sections qu'un clic de menu a sautées. Leçon du 2026-08-05. ---- */
  (function revelations() {
    var restants = $$('[data-mots], .lab, .rv, .deck, .piliers, .plans, .cars-b,'
      + ' .coll-d, .look-hd, .look-bas, .pills, .coords, .socs, .lk, .et,'
      /* ajoutés le 2026-08-17 : la grille du catalogue et la liste des
         questions ont leur propre signature, il leur faut la classe */
      + ' #grille, .faq-l');
    if (doux) { restants.forEach(function (el) { el.classList.add('vu'); }); return; }
    var attente = false;
    function balayer() {
      attente = false;
      var seuil = innerHeight * 0.9;
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
      attente = true; requestAnimationFrame(balayer);
    }
    addEventListener('scroll', pousser, { passive: true });
    addEventListener('resize', pousser, { passive: true });
    balayer();
  })();

  /* ---------- 4 · LE DÉFILEMENT LISSÉ (Lenis réécrit) -------------
     On interpole scrollTop. On ne transforme rien : les éléments en
     position:fixed et la modale restent intacts. ------------------- */
  var majCible = function () {};
  if (fin && !doux) {
    (function lisse() {
      var cible = scrollY, courant = scrollY, anime = false;
      document.documentElement.style.scrollBehavior = 'auto';
      function borne(v) {
        return Math.max(0, Math.min(document.documentElement.scrollHeight - innerHeight, v));
      }
      function boucle() {
        courant += (cible - courant) * 0.1;
        if (Math.abs(cible - courant) < 0.5) { courant = cible; anime = false; }
        scrollTo(0, courant);
        if (anime) requestAnimationFrame(boucle);
      }
      function lancer() { if (!anime) { anime = true; requestAnimationFrame(boucle); } }
      majCible = function (v) { cible = borne(v); lancer(); };
      addEventListener('wheel', function (e) {
        if (e.ctrlKey) return;                                /* le zoom reste le zoom */
        if (document.body.classList.contains('lock')) return; /* pas dans la modale */
        if (e.target.closest && e.target.closest('.ov,select,textarea')) return;
        e.preventDefault();
        cible = borne(cible + e.deltaY * (e.deltaMode === 1 ? 18 : 1));
        lancer();
      }, { passive: false });
      addEventListener('scroll', function () {
        if (!anime) { cible = scrollY; courant = scrollY; }
      }, { passive: true });
      addEventListener('resize', function () { cible = borne(cible); }, { passive: true });
    })();
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute('href').slice(1);
    if (!id) return;
    var c = document.getElementById(id);
    if (!c) return;
    e.preventDefault();
    var y = c.getBoundingClientRect().top + scrollY;
    if (fin && !doux) majCible(y);
    else scrollTo({ top: y, behavior: doux ? 'auto' : 'smooth' });
    history.replaceState(null, '', '#' + id);
  });

  /* ---------- 5 · LE CURSEUR — la lame ---------------------------- */
  if (fin && !doux) {
    (function curseur() {
      var c = $('#cur'), t = $('#curT');
      if (!c) return;
      document.body.classList.add('cur-ok');
      var x = innerWidth / 2, y = innerHeight / 2, cx = x, cy = y, anime = false, ne = false;
      addEventListener('pointermove', function (e) {
        x = e.clientX; y = e.clientY;
        if (!ne) { ne = true; cx = x; cy = y; }   /* il naît sous la souris */
        c.classList.add('on');
        if (!anime) { anime = true; requestAnimationFrame(suivre); }
      }, { passive: true });
      function suivre() {
        cx += (x - cx) * 0.15;
        cy += (y - cy) * 0.15;
        c.style.transform = 'translate3d(' + cx.toFixed(2) + 'px,' + cy.toFixed(2) + 'px,0)';
        if (Math.abs(x - cx) > 0.3 || Math.abs(y - cy) > 0.3) requestAnimationFrame(suivre);
        else anime = false;                        /* la boucle s'arrête d'elle-même */
      }
      document.addEventListener('pointerover', function (e) {
        var z = e.target.closest && e.target.closest('[data-cur]');
        var lien = e.target.closest && e.target.closest('a,button,.piece');
        c.classList.toggle('gros', !!(z || lien));
        t.textContent = z ? z.getAttribute('data-cur') : (lien ? 'OUVRIR' : '');
      });
      document.addEventListener('pointerleave', function () { c.classList.remove('on'); });
    })();
  }

  /* ---------- 6 · LA NAVIGATION ----------------------------------- */
  (function navigation() {
    var nav = $('#nav'), b = $('#burger'), l = $('#navC');
    var sombres = $$('.sec--encre');
    var attente = false;
    function poser() {
      attente = false;
      if (!nav) return;
      nav.classList.toggle('pose', scrollY > 30);
      /* la barre s'inverse quand elle passe sur une section encre */
      var h = nav.getBoundingClientRect().height || 64;
      var dessus = sombres.some(function (s) {
        var r = s.getBoundingClientRect();
        return r.top <= h * 0.6 && r.bottom >= h * 0.6;
      });
      nav.classList.toggle('sombre', dessus);
    }
    addEventListener('scroll', function () {
      if (attente) return;
      attente = true; requestAnimationFrame(poser);
    }, { passive: true });
    poser();
    if (!b || !l) return;
    function basculer(o) {
      b.setAttribute('aria-expanded', o ? 'true' : 'false');
      b.setAttribute('aria-label', o ? 'Fermer le menu' : 'Ouvrir le menu');
      l.classList.toggle('ouvert', o);
      document.body.classList.toggle('lock', o);
    }
    b.addEventListener('click', function () { basculer(b.getAttribute('aria-expanded') !== 'true'); });
    l.addEventListener('click', function (e) { if (e.target.closest('a')) basculer(false); });
    addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && b.getAttribute('aria-expanded') === 'true') { basculer(false); b.focus(); }
    });
  })();

  /* ---------- 7 · LE RUBAN, sans couture -------------------------- */
  (function ruban() {
    var r = $('#ruban');
    if (r) r.innerHTML += r.innerHTML;
  })();

  /* ---------- 8 · LE HÉROS — le slider éditorial ------------------
     Glissement latéral avec skew, numéro géant synchronisé au DÉBUT
     de la transition (pas après), autoplay 5 s en pause au survol. -- */
  (function heros() {
    var sc = $('#hsc'), num = $('#hnum'), col = $('#hcol'), des = $('#hdes'), cpt = $('#hcpt');
    if (!sc) return;

    /* ⚠️ LA PREMIÈRE PIÈCE D'ABORD, LES TROIS AUTRES ENSUITE.
       `loading="lazy"` faisait attendre le téléchargement au moment du clic,
       et la pièce restait immobile. Les charger toutes les quatre d'un coup
       est pire : elles se partagent la bande passante, et sur une 4G à
       1,6 Mb/s la PREMIÈRE n'arrivait qu'à la neuvième seconde, sur une page
       déjà affichée et vide de vêtement. C'est ça, « la page ne marche pas ».
       Alors : la première part seule (et le `<link rel=preload>` du `<head>`
       la demande avant même ce script), les trois autres suivent une fois
       qu'elle est peinte. Un clic anticipé les réclame à la demande. */
    /* ⚠️ LA PREMIÈRE DIAPOSITIVE EST DÉJÀ DANS LE HTML et on n'y touche pas :
       c'est elle que voit un visiteur dont le navigateur limite le
       JavaScript, et c'est elle que le navigateur télécharge sans attendre
       que ce script tourne. On ajoute les trois autres à la suite. */
    var premiere = sc.querySelector('.hsl');
    sc.insertAdjacentHTML('beforeend', HERO.map(function (o, i) {
      if (premiere && i === 0) return '';
      var img = o.f
        ? '<img ' + (i ? 'data-src' : 'src') + '="assets/images/' + esc(o.f) + '"'
          + ' alt="' + esc(o.t) + ', création Hillary M. Styl"'
          + (i ? '' : ' fetchpriority="high"') + ' decoding="async">'
        : SIL;
      return '<figure class="hsl' + (i === 0 ? ' act' : '') + '" data-i="' + i + '">'
        + '<div class="hsl-c">' + img + '</div></figure>';
    }).join(''));

    var sl = $$('.hsl', sc), n = sl.length, actif = 0, occupe = false;

    /* réclamer une pièce : au clic si elle n'est pas encore là, ou en fond
       une fois la première peinte. `decode()` évite le à-coup du premier
       affichage et ne bloque pas le fil principal. */
    function charger(i) {
      var im = sl[i] && sl[i].querySelector('img[data-src]');
      if (!im) return;
      im.src = im.getAttribute('data-src');
      im.removeAttribute('data-src');
      if (im.decode) im.decode().catch(function () {});
    }
    (function suite() {
      var prem = sl[0] && sl[0].querySelector('img');
      function lancer() {
        /* une par une, jamais en rafale : trois téléchargements simultanés
           sur une 4G, c'est trois pièces lentes au lieu d'une rapide. */
        var i = 1;
        (function suivante() {
          if (i >= sl.length) return;
          var k = i++;
          charger(k);
          var im = sl[k] && sl[k].querySelector('img');
          if (!im || im.complete) return setTimeout(suivante, 60);
          im.addEventListener('load', function () { setTimeout(suivante, 60); }, { once: true });
          im.addEventListener('error', function () { setTimeout(suivante, 60); }, { once: true });
        })();
      }
      if (!prem || prem.complete) return setTimeout(lancer, 400);
      prem.addEventListener('load', function () { setTimeout(lancer, 400); }, { once: true });
      prem.addEventListener('error', function () { setTimeout(lancer, 400); }, { once: true });
    })();

    /* Le chiffre géant roule DANS LE SENS du glissement et sur la MÊME durée.
       Deux chiffres coexistent le temps du croisement : l'ancien sort par le
       haut, le nouveau entre par le bas (et l'inverse en marche arrière).

       ⚠️ En DEUX temps, et c'est tout l'intérêt : `preparerNum` fabrique le
       chiffre et le pose à son point de départ, `aller()` récupère la fonction
       de départ et la déclenche DANS LA MÊME IMAGE que le glissement. Les deux
       transitions partent donc sur la même horloge, à la milliseconde.
       Avant, tout ce travail se faisait AVANT le mouvement : fabriquer un
       glyphe de 30rem coûte un calcul de mise en page, et la pièce restait
       immobile un demi-tour d'horloge après le clic. */
    function preparerNum(i, sens) {
      if (!num) return function () {};
      /* ⚠️ un chiffre déjà en train de sortir n'a plus rien à faire là. Sans
         ça, cliquer vite empilait « 0302 » : le verrou de `aller()` et le
         retrait de l'ancien chiffre tombent tous deux à 1050 ms, et selon
         lequel gagne la course, un chiffre restait sur le carreau. */
      $$('span.hn-s', num).forEach(function (s) { num.removeChild(s); });
      var vieux = num.querySelector('span');
      var neuf = document.createElement('span');
      neuf.textContent = d2(i + 1);
      neuf.className = 'hn-e';
      neuf.style.setProperty('--s', sens > 0 ? '1' : '-1');
      num.appendChild(neuf);
      if (vieux) vieux.style.setProperty('--s', sens > 0 ? '1' : '-1');
      /* on force le calcul MAINTENANT : au moment du départ, il ne reste
         plus qu'à changer une classe. */
      void neuf.offsetWidth;
      return function () {
        neuf.classList.remove('hn-e');
        if (vieux) vieux.classList.add('hn-s');
        setTimeout(function () {
          /* seule la transition LA PLUS RÉCENTE fait le ménage, et elle ne
             laisse qu'un chiffre. Une transition dépassée ne touche à rien :
             elle effacerait le chiffre de celle qui l'a doublée. */
          if (num.lastElementChild !== neuf) return;
          $$('span', num).forEach(function (s) { if (s !== neuf) num.removeChild(s); });
        }, 1050);
      };
    }

    /* la couleur et les deux textes : ils ne portent pas le mouvement, ils
       le suivent. On les traite APRÈS le départ pour ne pas le retarder. */
    function ecrire(i) {
      var o = HERO[i];
      /* LA COULEUR SUIT LE VÊTEMENT. La teinte dominante de chaque pièce est
         relevée sur la photo (`_v4/_couleurs.json`) et pilote le héros :
         la nappe de fond, le trait sous le titre et le badge de tête.
         Le magenta de la maison reste ailleurs — ici c'est le tissu qui parle. */
      if (o.c) document.documentElement.style.setProperty('--piece', o.c);
      [col, des].forEach(function (e) { if (e) e.classList.add('chg'); });
      /* les deux textes se relèvent au tiers du glissement : assez tard pour
         faire partie du même mouvement, assez tôt pour être lisibles à
         l'arrivée de la pièce. */
      setTimeout(function () {
        if (col) col.innerHTML = '<b>' + esc(o.col) + '</b><span class="m">' + esc(o.mat) + '</span>';
        if (des) des.innerHTML = '<b>' + esc(o.t) + '</b><p>' + esc(o.d) + '</p>';
        [col, des].forEach(function (e) { if (e) e.classList.remove('chg'); });
      }, 340);
      if (cpt) cpt.textContent = d2(i + 1) + ' — ' + d2(n);
    }

    function aller(i, sens) {
      if (occupe || n < 2) return;
      i = (i + n) % n;
      if (i === actif) return;
      occupe = true;
      charger(i);                  /* si le visiteur va plus vite que le réseau */
      var sort = sl[actif], entre = sl[i];
      entre.classList.remove('act', 'sort', 'entre');
      entre.classList.add(sens > 0 ? 'entre' : 'sort');
      var partirNum = preparerNum(i, sens);
      sc.classList.add('bouge');   /* ombres coupées : voir style-page.css */
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          /* LA MÊME IMAGE pour les trois : la pièce sort, la pièce entre,
             le chiffre roule. Rien d'autre ne se glisse entre eux. */
          sort.classList.remove('act');
          sort.classList.add(sens > 0 ? 'sort' : 'entre');
          entre.classList.remove('sort', 'entre');
          entre.classList.add('act');
          partirNum();
          /* la couleur et les textes à l'image suivante : leur recalcul ne
             doit pas s'intercaler dans le départ du mouvement. */
          requestAnimationFrame(function () { ecrire(i); });
        });
      });
      setTimeout(function () {
        sl.forEach(function (s) { if (s !== entre) s.classList.remove('act', 'sort', 'entre'); });
        sc.classList.remove('bouge');
        actif = i; occupe = false;
      }, 1050);   /* doit couvrir la transition CSS (1 s) */
    }

    var prev = $('#hPrev'), next = $('#hNext');
    if (prev) prev.addEventListener('click', function () { aller(actif - 1, -1); relancer(); });
    if (next) next.addEventListener('click', function () { aller(actif + 1, 1); relancer(); });

    /* le glissement du doigt */
    var dx = 0, dep = false;
    sc.addEventListener('pointerdown', function (e) { dep = true; dx = e.clientX; });
    sc.addEventListener('pointerup', function (e) {
      if (!dep) return; dep = false;
      var d = e.clientX - dx;
      if (Math.abs(d) > 42) { aller(actif + (d < 0 ? 1 : -1), d < 0 ? 1 : -1); relancer(); }
    });
    sc.addEventListener('pointercancel', function () { dep = false; });

    /* autoplay, en pause au survol et onglet caché */
    var minuteur = null;
    function relancer() {
      clearInterval(minuteur);
      if (doux || n < 2) return;
      minuteur = setInterval(function () {
        if (document.hidden) return;
        aller(actif + 1, 1);
      }, 5000);
    }
    sc.addEventListener('pointerenter', function () { clearInterval(minuteur); });
    sc.addEventListener('pointerleave', relancer);
    /* au premier rendu il n'y a rien à croiser : le chiffre du balisage est
       déjà le bon, on pose seulement la couleur, les textes et le compteur. */
    ecrire(0);
    relancer();
  })();

  /* ---------- 9 · LES COLLECTIONS — coverflow (Swiper réécrit) ---- */
  (function collections() {
    var zone = $('#cars'), piste = $('#carsP');
    if (!zone || !piste) return;
    var data = COLLECTIONS;
    if (!data.length) { zone.remove(); return; }

    var txt = document.createElement('div');
    txt.className = 'cars-t';
    zone.appendChild(txt);

    piste.innerHTML = data.map(function (o, i) {
      /* `f2` = la même pièce vue de dos. Un seul `alt` : les deux images
         montrent une seule création, pas deux. */
      var img = o.f
        ? '<img class="v1" src="assets/images/' + esc(o.f) + '" alt="' + esc(o.t)
          + ', création Hillary M. Styl' + (o.f2 ? ', vue de face et de dos' : '') + '" '
          + 'loading="lazy" decoding="async">'
          + (o.f2 ? '<img class="v2" src="assets/images/' + esc(o.f2) + '" alt="" '
                  + 'loading="lazy" decoding="async">' : '')
        : SIL;
      return '<figure class="car" data-i="' + i + '"><div class="car-c'
        + (o.f2 ? ' duo' : '') + '">' + img + '</div></figure>';
    }).join('');

    var cartes = $$('.car', piste), n = cartes.length, actif = 0;
    var cpt = $('#cCpt');

    function ecrire() {
      var o = data[actif];
      txt.classList.add('chg');
      setTimeout(function () {
        txt.innerHTML = '<p class="l">' + esc(o.l) + '</p>'
          + '<p class="t">' + esc(o.t) + '</p>'
          + '<p class="s">' + esc(o.s) + '</p>';
        txt.classList.remove('chg');
      }, 230);
      if (cpt) cpt.textContent = d2(actif + 1) + ' — ' + d2(n);
    }
    function placer() {
      var pas = cartes[0].offsetWidth * 1.04;
      cartes.forEach(function (c, i) {
        var o = i - actif;
        if (o > n / 2) o -= n;
        if (o < -n / 2) o += n;
        var a = Math.abs(o);
        c.style.setProperty('--tx', (o * pas).toFixed(1) + 'px');
        c.style.setProperty('--sc', a === 0 ? 1 : (a === 1 ? 0.75 : 0.58));
        c.style.setProperty('--op', a === 0 ? 1 : (a === 1 ? 0.4 : 0.16));
        c.style.setProperty('--bl', (a === 0 ? 0 : (a === 1 ? 2 : 4)) + 'px');
        c.classList.toggle('car--act', a === 0);
        c.setAttribute('aria-hidden', a === 0 ? 'false' : 'true');
      });
    }
    /* La carte active respire de la face au dos, quand la pièce a deux
       vues. Le minuteur REPART à chaque changement de carte : une pièce
       qui arrive se montre toujours de face d'abord. Les cartes de côté
       sont floutées et à 16 % : y faire passer un fondu ne se verrait pas
       et coûterait pour rien. */
    var batC = null;
    function respirer() {
      if (batC) { clearInterval(batC); batC = null; }
      $$('.car-c.dos', piste).forEach(function (c) { c.classList.remove('dos'); });
      if (doux) return;
      var c = $('.car-c.duo', cartes[actif]);
      if (!c) return;
      batC = setInterval(function () {
        if (document.hidden || document.body.classList.contains('ecran-on')) return;
        /* même règle qu'au catalogue : on ne montre pas une image absente */
        var v2 = c.querySelector('.v2');
        if (!c.classList.contains('dos') && v2 && !v2.complete) return;
        c.classList.toggle('dos');
      }, 3600);
    }
    function aller(i) { actif = (i + n) % n; placer(); ecrire(); respirer(); }

    var p = $('#cPrev'), s = $('#cNext');
    if (p) p.addEventListener('click', function () { aller(actif - 1); });
    if (s) s.addEventListener('click', function () { aller(actif + 1); });
    addEventListener('resize', placer, { passive: true });

    var dx = 0, dep = false;
    zone.addEventListener('pointerdown', function (e) { dep = true; dx = e.clientX; });
    zone.addEventListener('pointerup', function (e) {
      if (!dep) return; dep = false;
      var d = e.clientX - dx;
      if (Math.abs(d) > 42) aller(actif + (d < 0 ? 1 : -1));
      else {
        /* un clic sur la carte active mène au catalogue commandable */
        var c = document.getElementById('catalogue');
        if (c) {
          var y = c.getBoundingClientRect().top + scrollY;
          if (fin && !doux) majCible(y); else scrollTo({ top: y, behavior: 'smooth' });
        }
      }
    });
    zone.addEventListener('pointercancel', function () { dep = false; });
    aller(0);
  })();

  /* ---------- 10 · LE LOOKBOOK — compteur fixe et parallaxe -------
     ScrollTrigger + scrub réécrits : une boucle rAF, scrollY lu une
     seule fois, et le compteur qui « clique » sur chaque vue. ------ */
  (function lookbook() {
    var sc = $('#lookSc'), gr = $('#lookGr'), nEl = $('#lkN'), tEl = $('#lkT'), pg = $('#lkPage');
    if (!sc || !gr) return;
    var vues = $$('.lk', gr), n = vues.length;
    if (tEl) tEl.textContent = d2(n);
    var cour = -1, attente = false;

    function poser() {
      attente = false;
      var r = sc.getBoundingClientRect();
      var h = sc.offsetHeight - innerHeight;
      if (h <= 0) return;
      var k = Math.min(1, Math.max(0, -r.top / h));
      var i = Math.min(n - 1, Math.floor(k * n));
      if (i !== cour) {
        cour = i;
        if (nEl) {
          nEl.classList.add('chg');
          setTimeout(function () {
            nEl.innerHTML = '<span>' + d2(i + 1) + '</span>';
            nEl.classList.remove('chg');
          }, 220);
        }
        if (pg) pg.textContent = d2(i + 1) + ' / ' + d2(n);
      }
      /* la parallaxe : chaque vue à sa propre vitesse */
      if (!doux) {
        vues.forEach(function (v) {
          var vr = v.getBoundingClientRect();
          if (vr.bottom < -200 || vr.top > innerHeight + 200) return;
          var vit = parseFloat(v.getAttribute('data-vit') || '1');
          var c = (vr.top + vr.height / 2 - innerHeight / 2) / innerHeight;
          v.style.setProperty('--py', (c * (1 - vit) * 150).toFixed(1) + 'px');
          v.style.translate = '0 ' + (c * (1 - vit) * 150).toFixed(1) + 'px';
        });
      }
    }
    function pousser() {
      if (attente) return;
      attente = true; requestAnimationFrame(poser);
    }
    addEventListener('scroll', pousser, { passive: true });
    addEventListener('resize', pousser, { passive: true });
    poser();
  })();

  /* ---------- 11 · LE PROCESSUS — l'étape centrée se remplit ------ */
  (function processus() {
    var ets = $$('.et');
    if (!ets.length) return;
    if (doux) { return; }
    var attente = false;
    function poser() {
      attente = false;
      var mi = innerHeight / 2, best = null, dist = 1e9;
      ets.forEach(function (e) {
        var r = e.getBoundingClientRect();
        if (r.bottom < 0 || r.top > innerHeight) { e.classList.remove('act'); return; }
        var d = Math.abs(r.top + r.height / 2 - mi);
        if (d < dist) { dist = d; best = e; }
      });
      ets.forEach(function (e) { e.classList.toggle('act', e === best && dist < innerHeight * 0.34); });
    }
    function pousser() {
      if (attente) return;
      attente = true; requestAnimationFrame(poser);
    }
    addEventListener('scroll', pousser, { passive: true });
    addEventListener('resize', pousser, { passive: true });
    poser();
  })();

  /* ---------- 12 · LE LIEN WHATSAPP DES RÉSEAUX ------------------- */
  (function reseaux() {
    var bas = $('#waBas');
    var soc = $('[data-wa-soc]');
    if (bas && soc) {
      /* le moteur pose déjà l'href de #waBas : on le recopie */
      setTimeout(function () { soc.setAttribute('href', bas.getAttribute('href') || '#'); }, 0);
    }
  })();

  /* ==================================================================
     REPRIS DE LA V3 — le toucher, les cartes du catalogue, le tunnel.
     Le CSS gardé (`garde-css-toucher.css`) en dépend : sans ce bloc,
     l'onde ne naît jamais, les cartes n'ont plus d'inclinaison et les
     étapes du tunnel perdent leur animation. Trois régressions
     trouvées par le contrôle, pas à l'œil.
     ================================================================== */


  /* ================================================================
     LE TOUCHER — l'onde, l'enfoncement, la vibration
     Une seule écoute déléguée : les cartes et les options sont
     recréées à chaque rendu, un écouteur par élément fuirait.
     ================================================================ */
  var SEL_TAP = "[data-tap],.piece,.bt,.opt,.taille,.tab,.porte,.x,.wa,.cta,.alt";
  var ROT = [-1.6, 1.2, -0.9, 1.7, -1.3, 0.8];

  function vibre(ms){
    /* Android uniquement : iOS ne l'expose pas dans Safari.
       On ne vibre que sur un CHOIX, jamais au simple défilement. */
    if(doux) return;
    try{ if(navigator.vibrate) navigator.vibrate(ms); }catch(e){}
  }

  function onde(el, x, y){
    if(doux || !el) return;
    var r = el.getBoundingClientRect();
    var d = Math.max(r.width, r.height) * 2.1;
    var o = document.createElement("span");
    o.className = "onde" + (el.matches(".bt.p,.bt.w,.porte.a,.wa,.cta,.taille.sel") ? " clair" : "");
    o.style.width = o.style.height = d + "px";
    o.style.left = (x - r.left) + "px";
    o.style.top  = (y - r.top) + "px";
    el.appendChild(o);
    setTimeout(function(){ if(o.parentNode) o.parentNode.removeChild(o); }, 700);
  }

  document.addEventListener("pointerdown", function(e){
    var el = e.target.closest && e.target.closest(SEL_TAP);
    if(!el || el.disabled) return;
    var st = getComputedStyle(el);
    if(st.position === "static") el.style.position = "relative";
    if(st.overflow === "visible") el.style.overflow = "hidden";
    onde(el, e.clientX, e.clientY);
    /* la carte du catalogue : le tissu brille, la craie se retrace */
    if(el.classList.contains("piece")){
      el.classList.remove("brille");
      void el.offsetWidth;
      el.classList.add("brille");
    }
    if(el.matches(".opt,.taille,.bt.p,.bt.w,.piece,.porte,.tab")) vibre(9);
  }, {passive:true});

  /* ---- 02 · le catalogue : des échantillons qu'on pose ---- */
  function poserCartes(){
    Array.prototype.forEach.call(document.querySelectorAll("#grille .piece"), function(el,i){
      el.style.setProperty("--rot", ROT[i % ROT.length] + "deg");
      el.setAttribute("data-tap","");
    });
  }
  /* la table se vide avant qu'on repose : sans ça, changer d'onglet est
     un remplacement brutal — c'est ce qui faisait « sage » */
  if(typeof onglet === "function"){
    var _on = onglet;
    onglet = function(cat){
      var g = document.getElementById("grille");
      if(!g || doux){ _on(cat); poserCartes(); return; }
      g.classList.add("sort");
      setTimeout(function(){
        _on(cat); poserCartes(); g.classList.remove("sort");
      }, 175);
    };
  }
  poserCartes();

  /* ---- le tunnel : l'étape en cours pilote son animation ---- */
  if(typeof dessiner === "function"){
    var _de2 = dessiner;
    dessiner = function(){
      _de2();
      var bd = document.getElementById("shBd");
      if(!bd) return;
      /* ⚠️ Depuis le panier (2026-08-16) il y a DEUX parcours : la fiche
         d'une pièce (mesures, délai) et la commande (livraison, coordonnées,
         envoi). Les animations sont écrites par étape dans la feuille de
         style ; on garde leur sens d'origine :
           1 mesures · 2 livraison · 3 délai · 4 coordonnées · 5 envoi     */
      var _e = (typeof cmd !== "undefined" && cmd.actif)
        ? (cmd.etape === 1 ? 2 : (cmd.etape === 2 ? 4 : 5))
        : (etat ? (etat.etape === 1 ? 1 : 3) : 0);
      if(!_e) return;
      bd.setAttribute("data-e", String(_e));
      Array.prototype.forEach.call(bd.querySelectorAll(".taille"), function(t,i){
        t.style.setProperty("--t", i);
      });
    };
  }

  /* ---- la modale : le carnet qui s'ouvre, les champs qui se posent ---- */
  if(typeof dessiner === "function"){
    var _de = dessiner;
    dessiner = function(){
      _de();
      var bd = document.getElementById("shBd");
      if(!bd) return;
      Array.prototype.forEach.call(bd.querySelectorAll(".fd"), function(el,i){
        el.style.setProperty("--d", Math.min(i, 14));
      });
    };
  }

  /* ---------- 13 · LA MODALE : verrouiller le fond ----------------
     Le moteur expose ouvrir()/fermer() ; on les enveloppe pour
     bloquer le défilement de la page derrière la modale. ---------- */
  if (typeof window.ouvrir === 'function') {
    var _ou = window.ouvrir;
    window.ouvrir = function (id) { document.body.classList.add('lock'); _ou(id); };
  }
  if (typeof window.fermer === 'function') {
    var _fe = window.fermer;
    window.fermer = function () { document.body.classList.remove('lock'); _fe(); };
  }

})();

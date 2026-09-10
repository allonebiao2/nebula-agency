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
  var VER = '?v=20260826a';

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
      /* ⚠️ ON LIT TOUT, PUIS ON ÉCRIT TOUT. Avant, `classList.add('vu')`
         tombait au MILIEU de la boucle de lecture : chaque classe posée
         invalide la mise en page, et le `getBoundingClientRect()` suivant
         oblige le navigateur à la recalculer AVANT de répondre. Au premier
         écran il reste une centaine d'éléments à balayer : cela faisait
         jusqu'à cent recalculs complets dans une seule image, exactement au
         moment où le visiteur commence à défiler. Séparer les deux passes ne
         change rien à ce qui est révélé, seulement au nombre de recalculs :
         un seul. */
      var aVoir = [];
      restants = restants.filter(function (el) {
        if (el.getBoundingClientRect().top >= seuil) return true;
        aVoir.push(el);
        return false;
      });
      for (var i = 0; i < aVoir.length; i++) aVoir[i].classList.add('vu');
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
      /* même règle qu'au-dessus : on lit tout, puis on écrit tout */
      var aLever = [];
      restants = restants.filter(function (s) {
        if (s.getBoundingClientRect().top >= seuil) return true;
        aLever.push(s);
        return false;
      });
      for (var i = 0; i < aLever.length; i++) aLever[i].classList.add('leve');
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

  /* ---------- 9. La barre, le tiroir et le bouton flottant ----------- */
  (function navigation() {
    var nav = $('#nav'), voile = $('#voile');
    addEventListener('scroll', function () {
      if (nav) nav.classList.toggle('pose', scrollY > 40);
    }, { passive: true });

    /* DEUX PORTES, UN SEUL MÉCANISME.
       - le hamburger ouvre le tiroir de la barre, sur téléphone ;
       - le bouton flottant ouvre SON panneau, à toutes les largeurs.
       Elles s'excluent : ouvrir l'une referme l'autre. Chacune gèle ce qui
       n'est pas elle, sinon une tabulation sort du panneau vers des liens
       qu'on ne voit pas et un lecteur d'écran lit la page cachée derrière
       (leçon Hillary, 2026-08-25). */
    var portes = [];

    function porte(bouton, panneau, geler) {
      if (!bouton || !panneau) return null;
      var p = {
        b: bouton, p: panneau,
        ouvert: function () { return panneau.classList.contains('ouvert'); },
        poser: function (o) {
          if (o) portes.forEach(function (a) { if (a !== p && a.ouvert()) a.poser(false); });
          bouton.setAttribute('aria-expanded', o ? 'true' : 'false');
          panneau.classList.toggle('ouvert', o);
          if (voile) {
            voile.classList.toggle('on', portes.some(function (a) { return a.ouvert(); }));
            /* le voile passe devant la barre pour le panneau flottant, jamais
               pour le tiroir : celui-ci vit DANS la barre. */
            voile.classList.toggle('haut', panneau.id === 'plan' && o);
          }
          document.body.classList.toggle('plan-ouvert', panneau.id === 'plan' && o);
          document.body.classList.toggle('fige', portes.some(function (a) { return a.ouvert(); }));
          geler.forEach(function (s) {
            var el = $(s);
            if (el) el.inert = o;
          });
          if (o) panneau.focus({ preventScroll: true });
          else bouton.focus({ preventScroll: true });
        }
      };
      bouton.addEventListener('click', function () { p.poser(!p.ouvert()); });
      panneau.addEventListener('click', function (e) {
        if (e.target.closest('a') || e.target.closest('[data-modale]')) p.poser(false);
      });
      portes.push(p);
      return p;
    }

    porte($('#burger'), $('#navC'), ['#haut', '.pied', '#fabSon', '.fab-z']);
    porte($('#fab'), $('#plan'), ['#haut', '.pied', '#fabSon', '#nav']);

    if (voile) voile.addEventListener('click', function () {
      portes.forEach(function (p) { if (p.ouvert()) p.poser(false); });
    });
    addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      portes.forEach(function (p) { if (p.ouvert()) p.poser(false); });
    });
    /* ⚠️ Le tiroir de la barre n'existe que sous 880 px. S'il reste ouvert
       pendant qu'on élargit la fenêtre, ses liens repassent en ligne dans la
       barre et le voile reste posé sur une page qu'on ne peut plus toucher. */
    addEventListener('resize', function () {
      var t = portes[0];
      if (t && t.ouvert() && innerWidth > 880) t.poser(false);
    }, { passive: true });
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

  /* ---------- 12. LA MUSIQUE DE LA MAISON ------------------------------
     Mongazi, 2026-09-10 : « quand on rentre sur la vitrine le son doit se
     déclencher, ou limite dès qu'il y a contact, et que ce soit tamisé et
     immersif ». Le morceau est de lui (jazz lofi, Tama's Little Music Shop).

     ⚠️ CE BLOC REMPLACE L'AMBIANCE SYNTHÉTISÉE (trois oscillateurs graves, un
        bruit filtré, des gouttes). Elle ne coûtait aucun octet, mais deux
        nappes superposées font de la bouillie : le lofi porte déjà sa propre
        basse. Le code retiré reste dans git si on veut le reprendre.

     ⚠️ LE MÊME MOTEUR QUE nebula-agency.online, à la demande de Mongazi : une
        balise `<audio>` NUE avec `loop`, le premier geste qui lance, un fondu,
        un bouton qui coupe. Rien de Web Audio.
        ⚠️ UNE SEULE DIFFÉRENCE, mesurée : là où l'agence TENTE une lecture au
        chargement (refusée par le navigateur, donc sans effet), on TÉLÉCHARGE
        sans jouer. C'est ce qui fait sortir le son 33 ms après le contact au
        lieu d'attendre 677 Ko. Voir `precharger()` plus bas.
     ⚠️ ET C'EST VOULU : un `<audio>` non routé dans Web Audio joue sur iPhone
        MÊME EN MODE SILENCIEUX (il passe par le canal média), là où Web Audio
        reste muet. Beaucoup de téléphones ici vivent en silencieux.

     ⚠️ LE TAMISÉ SE FAIT ICI, AU VOLUME. `_son.py` livre un fichier franc
        (-11 LUFS, comme la source) et c'est `VOL` ci-dessous qui le pose au
        bon niveau : une seule ligne, qui s'entend tout de suite. Un fichier
        encodé trop bas, lui, ne se rattrape pas.

     ⚠️ LA BOUCLE AUSSI EST DANS LE FICHIER : le morceau reçu portait un fondu
        de sortie de quatre secondes, donc en `loop` le site se serait éteint
        puis rallumé d'un coup toutes les deux minutes. `_son.py` rogne ce
        fondu et referme le morceau sur lui-même par un fondu croisé (raccord
        mesuré à 14 % d'écart, la maison tolère 35 %). D'où `loop` tout simple. */
  (function musique() {
    var b = $('#fabSon');
    if (!b) return;

    var CLE = 'angy:son';
    /* ⚠️ La détection mobile de la page (`petit`) ne regarde que la largeur et
       rate une tablette. Pour le son on prend aussi le pointeur grossier : un
       haut-parleur de téléphone rend moins fort qu'un ordinateur. */
    var tactile = petit || matchMedia('(pointer: coarse)').matches;
    /* ⚠️ CE COUPLE A DÉJÀ ÉTÉ RÉGLÉ TROP BAS UNE FOIS. Le fichier était
       normalisé à -17 LUFS ET joué à 0,34 : deux atténuations l'une sur
       l'autre, soit -26,8 LUFS entendus, quand le site de l'agence sort à
       -18,0. Mongazi : « j'entends un bruit tout bas ». Le fichier est
       maintenant à -11 LUFS et c'est CE volume qui tamise, lui seul. */
    var VOL = tactile ? 0.66 : 0.57;      /* ≈ -14,6 / -15,9 LUFS entendus */
    var FONDU = 1200;                    /* ms — l'arrivée ne doit pas se remarquer */
    /* ⚠️ LA MUSIQUE A SA PROPRE MARQUE DE VERSION, séparée de celle des
       images, parce que les deux ne changent jamais en même temps : bumper
       `VER` pour une photo ferait retélécharger 677 Ko de son à tout le monde,
       et changer le morceau sans toucher aux images l'aurait laissé figé un an
       dans les caches (`/assets/*` porte `immutable`). */
    var VER_SON = '?v=20260910b';
    var SRC = 'assets/sons/ambiance.mp3' + VER_SON;

    var refuse = false;
    try { refuse = localStorage.getItem(CLE) === 'coupe'; } catch (e) {}

    var el = null, joue = false, raf = 0;

    /* ⛔ CE GARDE-FOU NE DOIT JAMAIS EMPÊCHER DE JOUER, SEULEMENT DE
       PRÉCHARGER. Il barrait les deux portes, et `navigator.connection`
       n'existe QUE sur Android : sur PC il rend `4g` et la musique partait,
       sur un téléphone de Cotonou il rend très souvent `2g` (c'est une
       estimation de latence, pas la vraie radio) et le site refusait alors de
       jouer QUEL QUE SOIT le geste, pour toujours. Mongazi, 2026-09-10 :
       « le son marche sur PC, sur mobile c'est comme au tout départ ».
       ⚠️ Économiser les données de la visiteuse, c'est ne pas télécharger
       677 Ko qu'elle n'a pas demandés. Ce n'est pas lui refuser le son
       qu'elle vient de demander en touchant l'écran. */
    function economie() {
      var c = navigator.connection || navigator.webkitConnection;
      return !!(c && (c.saveData === true ||
                      /(^|-)2g$/.test(c.effectiveType || '')));
    }

    function batir() {
      if (el) return;
      el = new Audio();
      el.loop = true;
      el.preload = 'none';
      el.setAttribute('playsinline', '');   /* iOS : ne prend pas l'écran */
      el.volume = 0;
      el.src = SRC;
      /* ⚠️ IL ENTRE DANS LA PAGE, et ce n'est pas décoratif : un `new Audio()`
         gardé dans une variable est INVISIBLE pour tout contrôle — on ne peut
         vérifier ni qu'il boucle, ni que son volume monte, ni qu'il se tait
         quand on le coupe. `hidden` ne l'empêche pas de jouer. Même choix
         qu'Au Braisé d'Or. */
      el.hidden = true;
      /* ⛔ CE QUI REND LA MUSIQUE AUDIBLE NE DOIT PAS ÊTRE UNE PROMESSE.
         L'élément naît à `volume = 0` et seul `reussi()` le remonte. Tant que
         `reussi()` ne tenait qu'au `.then()` de `play()`, une promesse qui
         tardait, se perdait ou courait contre la mise en pause d'un onglet
         caché laissait la piste tourner à volume ZÉRO pour toujours :
         `paused` faux, le bouton affichant encore « Écouter la musique », et
         la visiteuse n'entendant rien. Mesuré le 2026-09-10.
         `playing` est l'événement qui signifie littéralement « du son sort
         maintenant » — c'est lui qui doit commander le fondu. La promesse
         reste, en second chemin ; `reussi()` ne s'exécute qu'une fois. */
      el.addEventListener('playing', reussi);
      document.body.appendChild(el);
    }

    /* Fondu en ease-out cubique, comme partout ailleurs sur ce site.
       ⛔ `requestAnimationFrame` NE TOURNE PAS dans un onglet caché. Mesuré le
          2026-09-10 : un fondu lancé là ne progresse jamais, et le volume reste
          à 0 — la piste avance, l'horloge défile, et on n'entend rien au retour.
          Personne ne regarde un onglet caché : on y pose la valeur d'un coup. */
    function fondre(vers, ms, fini) {
      cancelAnimationFrame(raf);
      if (document.hidden) {
        try { el.volume = vers; } catch (x) {}
        if (fini) fini();
        return;
      }
      var de = el ? el.volume : 0, t0 = performance.now();
      (function pas(t) {
        var p = Math.min((t - t0) / ms, 1);
        try { el.volume = de + (vers - de) * (1 - Math.pow(1 - p, 3)); } catch (x) {}
        if (p < 1) raf = requestAnimationFrame(pas);
        else if (fini) fini();
      })(t0);
    }

    function marquer(on) {
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.setAttribute('aria-label', on ? 'Couper la musique' : 'Écouter la musique');
    }

    /* ⚠️ CE PRÉCHARGEMENT N'EST PAS UN CONFORT, IL EST LE PRODUIT.
       Mesuré ici : sans lui, `play()` est refusé tant qu'il n'y a pas eu de
       geste, et rien n'est téléchargé — le premier contact déclenche alors les
       677 Ko AVANT le premier son. Sur la 3G de Cotonou, la visiteuse touche
       l'écran et n'entend rien pendant plusieurs secondes.

       ⛔ ET L'ASTUCE DE LA MAISON NE MARCHE PAS. Djambar et Au Braisé d'Or
          lancent une lecture EN SOURDINE au chargement en la croyant toujours
          autorisée (« la piste tourne, bufferisée, prête à être révélée sans
          délai »). Mesuré ici, Chromium la refuse aussi :
              NotAllowedError: play() failed because the user didn't interact
          Ces deux sites croient donc bufferiser et ne bufferisent rien.
          ⚠️ À vérifier chez eux un jour — ce n'est pas le chantier d'Angélique.

       Ce qui marche, et qui ne dépend d'AUCUNE politique de lecture
       automatique, c'est de télécharger sans jouer : `preload` puis `load()`.
       Le fichier arrive pendant qu'on lit le héros, et le contact ne fait plus
       que le dévoiler.
       ⛔ Aucun navigateur ne laisse sortir du son sans geste : « dès qu'il y a
          contact » est le mieux qui existe, et c'est bien ce qu'on livre. */
    function precharger() {
      if (joue || refuse || economie()) return;
      batir();
      el.preload = 'auto';
      try { el.load(); } catch (x) {}
    }

    function demarrer() {
      /* ⚠️ PAS de `economie()` ici : voir plus haut. Le geste fait foi. */
      if (joue || refuse) return;
      batir();
      el.muted = false;
      var p = el.play();
      if (p && p.then) {
        p.then(reussi).catch(function () {
          /* le navigateur veut un vrai geste : le fichier est déjà là, le
             prochain contact partira tout de suite. */
        });
      } else { reussi(); }
    }

    function reussi() {
      if (joue) return;                  /* deux chemins y mènent : un seul agit */
      joue = true;
      el.muted = false;
      marquer(true);
      fondre(VOL, FONDU);
      desarmer();
    }

    function couper() {
      if (!el) return;
      fondre(0, 420, function () { try { el.pause(); } catch (x) {} });
      joue = false;
      marquer(false);
    }

    b.addEventListener('click', function (e) {
      e.stopPropagation();
      if (joue) {
        refuse = true;
        try { localStorage.setItem(CLE, 'coupe'); } catch (x) {}
        couper();
      } else {
        refuse = false;
        try { localStorage.setItem(CLE, 'joue'); } catch (x) {}
        batir();
        el.muted = false;
        var p = el.play();
        if (p && p.then) p.then(reussi).catch(function () {}); else reussi();
      }
    });

    /* ⚠️ LE PREMIER CONTACT, QUEL QU'IL SOIT. `scroll` est dans la liste parce
       que c'est le premier geste réel d'une visiteuse sur téléphone — mais sur
       Chrome de bureau une molette N'EST PAS un geste au sens de la lecture
       automatique : `play()` y sera refusé jusqu'au premier clic ou à la
       première touche. C'est le navigateur qui décide, pas nous. */
    var GESTES = ['pointerdown', 'touchstart', 'keydown', 'click', 'scroll'];
    function auContact(e) {
      if (e && e.target && b.contains(e.target)) return;   /* le bouton a sa logique */
      demarrer();
    }
    function desarmer() {
      GESTES.forEach(function (g) { window.removeEventListener(g, auContact, true); });
    }
    GESTES.forEach(function (g) {
      window.addEventListener(g, auContact, { passive: true, capture: true });
    });

    /* La tentative d'entrée : elle réussit là où le navigateur l'autorise, et
       elle échoue en silence ailleurs — les gestes ci-dessus prennent le relais.
       Après `load` : le premier écran du site pèse 244 Ko mesurés, la musique
       ne passe jamais devant. */
    if (document.readyState === 'complete') precharger();
    else window.addEventListener('load', precharger, { once: true });

    marquer(false);

    document.addEventListener('visibilitychange', function () {
      if (!el || !joue) return;
      if (document.hidden) { try { el.pause(); } catch (x) {} }
      else { var p = el.play(); if (p && p.catch) p.catch(function () {}); }
    });
  })();

  /* ---------- 13. LA SÉLECTION ----------------------------------------
     Le « panier » d'une artiste qui n'affiche plus ses prix : il n'y a pas
     de total, il y a une LISTE. On retient plusieurs œuvres, et Angélique
     reçoit un seul message au lieu d'un par pièce.

     ⚠️ LES ŒUVRES NE SONT PAS RECOPIÉES ICI. Titre, dimensions et image sont
     LUS dans la fiche. Le jour où elle change un texte, la sélection suit.

     ⚠️ LA HAUTEUR DE LA BANDE EST MESURÉE, pas écrite à la main. Une valeur
     en dur laisse toujours quelques pixels de recouvrement quand la bande
     passe sur deux lignes (leçon Hillary du 2026-08-16).
     ------------------------------------------------------------------- */
  (function selection() {
    var bande = $('#selb'), modale = $('#selM');
    if (!bande || !modale || !modale.showModal) return;

    var CLE = 'angy_selection';
    var liste = $('#selL'), vide = $('#selVide'), nb = $('#selbN'), mot = $('#selbM');
    var choisies = [];

    function lire() {
      try {
        var v = JSON.parse(localStorage.getItem(CLE));
        return Array.isArray(v) ? v : [];
      } catch (e) { return []; }
    }
    function ecrire() {
      try { localStorage.setItem(CLE, JSON.stringify(choisies)); } catch (e) {}
    }

    /* la fiche est la source : on n'en garde que l'identifiant */
    function oeuvre(id) {
      var a = document.getElementById(id);
      if (!a) return null;
      var t = a.querySelector('.oeu-t'), img = a.querySelector('.oeu-p img'), dim = '';
      a.querySelectorAll('.oeu-c div').forEach(function (d) {
        var dt = d.querySelector('dt');
        if (dt && dt.textContent.trim().indexOf('DIMENSIONS') === 0) {
          var dd = d.querySelector('dd');
          if (dd) dim = dd.textContent.trim();
        }
      });
      return {
        id: id,
        titre: t ? t.textContent.trim() : id,
        dim: dim,
        img: img ? img.getAttribute('src') : '',
        alt: img ? (img.getAttribute('alt') || '') : ''
      };
    }

    function mesurer() {
      var h = Math.round(bande.getBoundingClientRect().height);
      if (h > 0) document.documentElement.style.setProperty('--selb-h', h + 'px');
    }

    function poser() {
      /* on écarte ce qui n'existe plus : une œuvre retirée de la page ne doit
         pas rester dans une sélection oubliée dans le navigateur */
      choisies = choisies.filter(function (id) { return !!document.getElementById(id); });

      var n = choisies.length;
      bande.hidden = (n === 0);
      document.body.classList.toggle('a-selection', n > 0);
      if (nb) nb.textContent = n;
      if (mot) mot.textContent = (n > 1 ? 'œuvres sélectionnées' : 'œuvre sélectionnée');

      $$('[data-add]').forEach(function (b) {
        var a = b.closest('.oeu');
        var dedans = a && choisies.indexOf(a.id) >= 0;
        b.setAttribute('aria-pressed', dedans ? 'true' : 'false');
        var t = b.querySelector('.oeu-add-t');
        if (t) t.textContent = dedans ? 'DANS MA SÉLECTION' : 'AJOUTER À MA SÉLECTION';
      });

      if (liste) {
        liste.innerHTML = '';
        choisies.forEach(function (id) {
          var o = oeuvre(id);
          if (!o) return;
          var li = document.createElement('li');
          li.className = 'sel-i';
          li.innerHTML =
            '<img src="' + o.img + '" alt="" width="56" height="56" loading="lazy" decoding="async">' +
            '<div class="sel-i-c"><p class="sel-i-t"></p><p class="sel-i-d"></p></div>' +
            '<button class="sel-i-x" type="button" aria-label="Retirer cette œuvre de ma sélection">' +
            '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>';
          li.querySelector('.sel-i-t').textContent = o.titre;
          li.querySelector('.sel-i-d').textContent = o.dim;
          li.querySelector('.sel-i-x').addEventListener('click', function () {
            choisies = choisies.filter(function (x) { return x !== id; });
            ecrire(); poser();
          });
          liste.appendChild(li);
        });
      }
      if (vide) vide.hidden = (n > 0);
      var envoi = $('#selEnvoi'), vider = $('#selVider');
      if (envoi) envoi.disabled = (n === 0);
      if (vider) vider.hidden = (n === 0);
      requestAnimationFrame(mesurer);
    }

    /* --- le geste : ajouter, retirer --- */
    $$('[data-add]').forEach(function (b) {
      b.addEventListener('click', function () {
        var a = b.closest('.oeu');
        if (!a || !a.id) return;
        var i = choisies.indexOf(a.id);
        if (i >= 0) choisies.splice(i, 1); else choisies.push(a.id);
        ecrire(); poser();
      });
    });

    /* --- la modale : `showModal` donne le piège au clavier, Échap et
           l'inertie de la page derrière, sans une ligne de plus --- */
    var dernier = null;
    function ouvrir(depuis) {
      dernier = depuis || null;
      poser();
      modale.showModal();
      document.body.classList.add('fige');
    }
    $('#selbOpen').addEventListener('click', function () { ouvrir(this); });
    $('#selX').addEventListener('click', function () { modale.close(); });
    modale.addEventListener('click', function (e) { if (e.target === modale) modale.close(); });
    modale.addEventListener('close', function () {
      document.body.classList.remove('fige');
      if (dernier && document.contains(dernier)) dernier.focus({ preventScroll: true });
    });

    $('#selVider').addEventListener('click', function () {
      choisies = []; ecrire(); poser();
      modale.close();
    });

    /* --- le message : un seul, pour toutes les œuvres --- */
    $('#selEnvoi').addEventListener('click', function () {
      if (!choisies.length) return;
      var pieces = choisies.map(oeuvre).filter(Boolean);
      var l = [pieces.length > 1
        ? "Bonjour Angélique, j'ai vu ces œuvres sur votre site :"
        : "Bonjour Angélique, j'ai vu cette œuvre sur votre site :"];
      l.push('');
      pieces.forEach(function (o) {
        l.push('• ' + o.titre + (o.dim ? ' (' + o.dim + ')' : ''));
      });
      l.push('');
      l.push(pieces.length > 1
        ? 'Pouvez-vous me dire comment les acquérir ?'
        : "Pouvez-vous me dire comment l'acquérir ?");
      var url = (NUM || 'https://wa.me/2290152006490') + '?text=' + encodeURIComponent(l.join('\n'));
      window.open(url, '_blank', 'noopener');
    });

    choisies = lire();
    poser();
    addEventListener('resize', mesurer, { passive: true });
  })();


})();

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
    { f:'', col:'Sur-mesure',     mat:'Vos mesures, votre coupe',
      t:'La pièce ajustée',  d:"Tracée sur vos mesures exactes, pas sur une taille standard." },
    { f:'', col:'Pagne & wax',    mat:'Tissus d’ici, coupe d’aujourd’hui',
      t:'Le pagne',          d:"Le tissu qu’on connaît depuis toujours, dans une coupe qui tombe." },
    { f:'', col:'Prêt-à-porter',  mat:'Par tailles, prêt à partir',
      t:'Les tailles',       d:"Pour ce qui n’a pas besoin d’attendre l’atelier." },
    { f:'', col:'Cérémonie',      mat:'Mariages et grandes occasions',
      t:'La tenue de fête',  d:"Ce qu’on porte le jour dont on se souvient." }
  ];

  /* --- 3 · LES COLLECTIONS : 6 à 8 pièces phares --- */
  var COLLECTIONS = [
    { f:'', l:'Sur-mesure',    t:'Robe coupée à la taille', s:'9 mesures · toutes matières' },
    { f:'', l:'Sur-mesure',    t:'Robe droite',             s:'15 mesures · tombé net' },
    { f:'', l:'Pagne',         t:'Ensemble pagne',          s:'Haut et bas assortis' },
    { f:'', l:'Prêt-à-porter', t:'Chemise',                 s:'8 mesures ou par tailles' },
    { f:'', l:'Sur-mesure',    t:'Pantalon',                s:'6 mesures · ourlet posé à l’essayage' },
    { f:'', l:'Cérémonie',     t:'Tenue de cérémonie',      s:'Sur rendez-vous · délai à convenir' }
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
      + ' .coll-d, .look-hd, .look-bas, .pills, .coords, .socs, .lk, .et');
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

    sc.innerHTML = HERO.map(function (o, i) {
      var img = o.f
        ? '<img src="assets/images/' + esc(o.f) + '" alt="' + esc(o.t) + ', création Hillary M. Styl"'
          + (i ? ' loading="lazy"' : ' fetchpriority="high"') + ' decoding="async">'
        : SIL;
      return '<figure class="hsl' + (i === 0 ? ' act' : '') + '" data-i="' + i + '">'
        + '<div class="hsl-c">' + img + '</div></figure>';
    }).join('');

    var sl = $$('.hsl', sc), n = sl.length, actif = 0, occupe = false;

    function ecrire(i) {
      var o = HERO[i];
      if (num) {
        num.classList.add('chg');
        setTimeout(function () {
          num.innerHTML = '<span>' + d2(i + 1) + '</span>';
          num.classList.remove('chg');
        }, 240);
      }
      [col, des].forEach(function (e) { if (e) e.classList.add('chg'); });
      setTimeout(function () {
        if (col) col.innerHTML = '<b>' + esc(o.col) + '</b><span class="m">' + esc(o.mat) + '</span>';
        if (des) des.innerHTML = '<b>' + esc(o.t) + '</b><p>' + esc(o.d) + '</p>';
        [col, des].forEach(function (e) { if (e) e.classList.remove('chg'); });
      }, 260);
      if (cpt) cpt.textContent = d2(i + 1) + ' — ' + d2(n);
    }

    function aller(i, sens) {
      if (occupe || n < 2) return;
      i = (i + n) % n;
      if (i === actif) return;
      occupe = true;
      var sort = sl[actif], entre = sl[i];
      entre.classList.remove('act', 'sort', 'entre');
      entre.classList.add(sens > 0 ? 'entre' : 'sort');
      /* le numéro change AU DÉBUT du mouvement */
      ecrire(i);
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          sort.classList.remove('act');
          sort.classList.add(sens > 0 ? 'sort' : 'entre');
          entre.classList.remove('sort', 'entre');
          entre.classList.add('act');
        });
      });
      setTimeout(function () {
        sl.forEach(function (s) { if (s !== entre) s.classList.remove('act', 'sort', 'entre'); });
        actif = i; occupe = false;
      }, 950);
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
    ecrire(0); relancer();
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
      var img = o.f
        ? '<img src="assets/images/' + esc(o.f) + '" alt="' + esc(o.t)
          + ', création Hillary M. Styl" loading="lazy" decoding="async">'
        : SIL;
      return '<figure class="car" data-i="' + i + '"><div class="car-c">' + img + '</div></figure>';
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
    function aller(i) { actif = (i + n) % n; placer(); ecrire(); }

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
      if(!bd || !etat) return;
      bd.setAttribute("data-e", String(etat.etape));
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

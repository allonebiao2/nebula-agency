/* LE MENU · commun aux quatre pages de Luxury Club 229 (demande de la cliente, 26/11).
 *
 * Ses mots : « quand les gens entrent dans un truc, ils ont déjà la notion de regarder en haut […] à côté de
 * l'accueil, tu mets le truc avec l'icône de menu, tu mets Menu » ; « catalogue, les gens ne comprennent pas » ;
 * « si quelqu'un se perd, il n'arrive pas à swiper, il clique sur Menu » ; « une petite notification en haut :
 * Retrouvez ici notre menu ».
 *
 * Ce que fait ce fichier :
 *  1. un bouton « ☰ Menu » en haut, à côté d'« Accueil » (dans le même bloc : la mise en page de l'en-tête ne bouge pas) ;
 *  2. il ouvre LE tiroir du site (celui de la barre du bas, renommé « Menu ») ou en crée un identique là où il manque ;
 *  3. en tête du tiroir, « Sur cette page » : les étapes de la visite 3D (on y va en un toucher, sans défiler) et les
 *     raccourcis de la page ; puis « Nos univers » ;
 *  4. la bulle « Retrouvez ici notre menu », une fois par page et par visite, qui disparaît seule.
 * Chaque page déclare ses raccourcis dans window.LC_MENU (posé par _outils/_menu_poser.py).
 */
(function () {
  var CFG = window.LC_MENU || {};
  var doc = document;
  var calme = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var ICONE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>';
  var FLECHE = '<svg viewBox="0 0 24 12"><path d="M1 6h21M17 1l5 5-5 5"/></svg>';
  var UNIVERS = [
    { t: 'Accueil · Luxury Club 229', h: 'index.html' },
    { t: 'Luxury Skin Clinic', h: 'luxury-skin-clinic.html' },
    { t: 'INA Luxury', h: 'ina-luxury.html' },
    { t: 'Harmonisation faciale', h: 'harmonisation-faciale.html' }
  ];
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };

  /* ---------- le style (le tiroir reprend celui de la barre du bas, à l'identique) ---------- */
  var css = doc.createElement('style');
  css.id = 'lm-css';
  css.textContent = [
    '.lm-gauche{display:flex;align-items:center;gap:6px;}',
    /* les destinations du menu s'arrêtent SOUS les barres collantes (INA : 143 px ; clinique : 79 ; harmonisation : 64) */
    '.layout{scroll-margin-top:150px;}#soins,#rdv-booking,#questions,#techniques,.tech{scroll-margin-top:86px;}',
    /* « Accueil » perd son mot au téléphone : la flèche garde une cible de 44 px */
    '.lm-gauche .back-hub,.lm-gauche .retour{display:inline-flex;align-items:center;justify-content:center;min-width:44px;min-height:44px;}',
    '.lm-btn{display:inline-flex;align-items:center;gap:8px;min-height:44px;min-width:44px;padding:0 14px;border-radius:999px;cursor:pointer;',
    '  font:600 12.5px/1 "Jost",system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;',
    '  background:#1c1812;color:#f3e3b5;border:1px solid rgba(201,168,76,.65);transition:background .25s,color .25s,border-color .25s;}',
    '.lm-btn:hover,.lm-btn:focus-visible{background:#c9a84c;color:#16120a;border-color:#c9a84c;}',
    '.lm-btn:focus-visible{outline:2px solid #c9a84c;outline-offset:3px;}',
    '.lm-btn svg{width:17px;height:17px;stroke:currentColor;fill:none;stroke-width:2;flex:none;}',
    '.lm-hub{position:absolute;top:14px;left:14px;z-index:60;}',
    /* la bulle : passe-partout (pointer-events:none), elle ne gêne jamais ce qu'elle survole et part seule */
    '.lm-bulle{position:fixed;z-index:9000;pointer-events:none;max-width:240px;padding:10px 14px;border-radius:12px;',
    '  background:#c9a84c;color:#16120a;font:600 13.5px/1.35 "Jost",system-ui,sans-serif;box-shadow:0 12px 30px rgba(0,0,0,.28);',
    '  opacity:0;transform:translateY(-6px);transition:opacity .35s ease,transform .35s ease;}',
    '.lm-bulle.on{opacity:1;transform:none;}',
    '.lm-bulle::before{content:"";position:absolute;top:-7px;left:var(--lm-fleche,24px);border:7px solid transparent;border-top:0;border-bottom-color:#c9a84c;}',
    /* « Sur cette page » : des boutons qui ont l'allure des liens du tiroir */
    '.lm-sec{padding:4px 0 6px;border-bottom:1px solid rgba(201,168,76,.16);margin-bottom:4px;}',
    '.lm-sec .lc-cat-cat{padding-top:12px;}',
    'button.lc-cat-sub.lm-tete{padding-left:22px;margin-top:8px;color:#ead9a6;font-family:"Cormorant Garamond",serif;font-size:15px;font-weight:600;}',
    'button.lc-cat-sub.lm-tete::before{content:none;}',
    'button.lc-cat-sub{background:none;border:0;width:100%;text-align:left;cursor:pointer;font:inherit;font-size:13px;min-height:40px;}',
    'a.lc-cat-sub.lm-l,button.lc-cat-sub{font-size:13px;color:#cfc2a3;}',
    'a.lc-cat-sub.lm-l:hover,button.lc-cat-sub:hover{color:#fff3cf;}',
    /* le tiroir, pour les pages qui n'en ont pas (copie du tiroir de la barre du bas) */
    '.lc-cat-scrim{position:fixed;inset:0;z-index:8690;background:rgba(6,6,6,.74);opacity:0;visibility:hidden;transition:opacity .35s,visibility .35s;}',
    '.lc-cat-scrim.open{opacity:1;visibility:visible;}',
    '.lc-cat-panel{position:fixed;top:0;left:0;bottom:0;width:322px;max-width:88vw;z-index:8700;',
    '  background:linear-gradient(168deg,#1c1812,#0b0a08);border-right:1px solid rgba(201,168,76,.3);box-shadow:10px 0 50px rgba(0,0,0,.7);',
    '  transform:translateX(-105%);transition:transform .42s cubic-bezier(.22,1,.36,1);overflow-y:auto;-webkit-overflow-scrolling:touch;padding:20px 0 34px;}',
    '.lc-cat-panel.open{transform:none;}',
    '.lc-cat-top{display:flex;align-items:center;justify-content:space-between;padding:0 18px 14px;border-bottom:1px solid rgba(201,168,76,.16);margin-bottom:6px;}',
    '.lc-cat-top h3{font-family:"Cormorant Garamond",serif;font-size:1.25rem;color:#ead9a6;font-weight:600;margin:0;}',
    '.lc-cat-close{width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:none;border:1px solid rgba(201,168,76,.3);color:#ead9a6;cursor:pointer;flex-shrink:0;}',
    '.lc-cat-close svg{width:14px;height:14px;stroke:currentColor;fill:none;stroke-width:2;}',
    '.lc-cat-brand{display:flex;align-items:center;justify-content:space-between;margin:12px 12px 3px;padding:12px 13px;border-radius:9px;text-decoration:none;',
    '  font:600 11px/1.2 "Jost",system-ui,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:#e3cd86;background:rgba(201,168,76,.09);min-height:44px;}',
    '.lc-cat-brand:hover{background:rgba(201,168,76,.17);}',
    '.lc-cat-brand svg{width:16px;height:9px;stroke:currentColor;fill:none;stroke-width:1.8;flex-shrink:0;}',
    '.lc-cat-cat{padding:10px 22px 3px;font-size:13.5px;letter-spacing:.03em;color:#d8c8a4;font-family:"Cormorant Garamond",serif;font-weight:600;}',
    '.lc-cat-sub{display:flex;align-items:center;padding:5px 22px 5px 38px;font-size:12px;color:#a99f88;text-decoration:none;position:relative;min-height:40px;}',
    '.lc-cat-sub::before{content:"·";position:absolute;left:27px;color:#c9a84c;}',
    '@media(max-width:760px){.lm-gauche .back-hub .lm-mot,.lm-gauche .retour span{display:none;}.lm-btn{padding:0 12px;letter-spacing:.1em;}}',
    '@media(prefers-reduced-motion:reduce){.lc-cat-panel,.lm-bulle{transition:none;}}'
  ].join('\n');
  doc.head.appendChild(css);

  /* ---------- le tiroir : celui du site, ou le même créé ici ---------- */
  var panel = doc.getElementById('lcCatPanel'), scrim = doc.getElementById('lcCatScrim'), body = doc.getElementById('lcCatBody');
  var existait = !!panel;
  if (!panel) {
    scrim = doc.createElement('div'); scrim.className = 'lc-cat-scrim'; scrim.id = 'lcCatScrim';
    panel = doc.createElement('aside'); panel.className = 'lc-cat-panel'; panel.id = 'lcCatPanel';
    panel.innerHTML = '<div class="lc-cat-top"><h3>Menu</h3><button class="lc-cat-close" type="button" aria-label="Fermer le menu">' +
      '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div><div id="lcCatBody"></div>';
    doc.body.appendChild(scrim); doc.body.appendChild(panel);
    body = doc.getElementById('lcCatBody');
    body.innerHTML = '<div class="lc-cat-cat">Nos univers</div>' + UNIVERS.map(function (u) {
      return '<a class="lc-cat-brand" href="' + u.h + '">' + esc(u.t) + FLECHE + '</a>';
    }).join('') + '<a class="lc-cat-brand" href="https://wa.me/2290167975626" target="_blank" rel="noopener">Nous écrire sur WhatsApp' + FLECHE + '</a>';
  } else {
    var h3 = panel.querySelector('.lc-cat-top h3');
    if (h3) h3.textContent = 'Menu';
    panel.setAttribute('aria-label', 'Menu Luxury Club 229');
  }
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-label', 'Menu Luxury Club 229');

  /* « Sur cette page » : construit à l'ouverture (la visite 3D se charge après la page) */
  var sec = doc.createElement('div');
  sec.className = 'lm-sec';
  body.insertBefore(sec, body.firstChild);
  /* La cliente, 26/11 : « la nouvelle interface, c'est une sorte d'accueil pour chaque espace ; quand ils ne se
     retrouvent pas, ils cliquent sur Menu et ça les amène dans un espace normal, comme un site internet normal ».
     Le menu ne mène donc JAMAIS dans la visite 3D : il mène aux listes de la page (catalogue, soins, techniques). */
  var GROUPES = { visage: 'Soins du visage', corps: 'Soins du corps', capillaires: 'Soins capillaires', complet: 'Expérience VIP' };
  function remplir() {
    var h = '';
    if (CFG.familles && window.LC_INA) {
      var I = window.LC_INA;
      I.familles.filter(function (f) { return I.produits.some(function (p) { return p.f === f.key; }); }).forEach(function (f) {
        h += '<button type="button" class="lc-cat-sub lm-tete" data-lm-famille="' + esc(f.key) + '">' + esc(f.label) + '</button>';
        (I.sous[f.key] || []).filter(function (s) { return I.produits.some(function (p) { return p.f === f.key && p.s === s.key; }); })
          .forEach(function (s) { h += '<button type="button" class="lc-cat-sub" data-lm-famille="' + esc(f.key) + '" data-lm-sous="' + esc(s.key) + '">' + esc(s.label) + '</button>'; });
      });
    }
    if (CFG.soins && window.LC_CLINIC) {
      var S = window.LC_CLINIC.services, vus = {};
      S.forEach(function (s) { vus[s.g] = 1; });
      Object.keys(vus).forEach(function (g) {
        h += '<div class="lc-cat-cat">' + esc(GROUPES[g] || g) + '</div>';
        S.forEach(function (s, i) { if (s.g === g) h += '<button type="button" class="lc-cat-sub" data-lm-soin="' + i + '">' + esc(s.n) + '</button>'; });
      });
    }
    if (CFG.techniques && window.LC_HARMO) {
      h += '<div class="lc-cat-cat">Les techniques</div>';
      h += window.LC_HARMO.donnees.map(function (t) { return '<button type="button" class="lc-cat-sub" data-lm-ancre="#' + esc(t.id) + '">' + esc(t.nom) + '</button>'; }).join('');
    }
    if (CFG.raccourcis && CFG.raccourcis.length) {
      h += '<div class="lc-cat-cat">Raccourcis</div>';
      h += CFG.raccourcis.map(function (r, i) {
        return r.h && r.h.charAt(0) !== '#' && r.h.charAt(0) !== '.'
          ? '<a class="lc-cat-sub lm-l" href="' + esc(r.h) + '">' + esc(r.t) + '</a>'
          : '<button type="button" class="lc-cat-sub" data-lm-r="' + i + '">' + esc(r.t) + '</button>';
      }).join('');
    }
    sec.innerHTML = h ? '<div class="lc-cat-cat" style="font-size:11px;letter-spacing:.22em;text-transform:uppercase;font-family:Jost,sans-serif;color:#c9a84c">Sur cette page</div>' + h : '';
  }

  function ouvrir() {
    remplir();
    panel.classList.add('open'); scrim.classList.add('open');
    if (window.LCAudio) window.LCAudio.play('menuOpen'); else if (window.LCBruit) window.LCBruit('menu');
    var c = panel.querySelector('.lc-cat-close'); if (c) c.focus();
    cacherBulle();
  }
  function fermer() {
    panel.classList.remove('open'); scrim.classList.remove('open');
    if (window.LCAudio) window.LCAudio.play('menuClose'); else if (window.LCBruit) window.LCBruit('menu');
  }
  window.LCMenu = { ouvrir: ouvrir, fermer: fermer };
  // tant que le menu recouvre la page, la visite 3D se met en pause (quel que soit le bouton qui l'a ouvert) :
  // le tiroir glisse sans à-coup et le téléphone ne dessine pas une scène cachée (26/11)
  new MutationObserver(function () { doc.documentElement.classList.toggle('lm-ouvert', panel.classList.contains('open')); })
    .observe(panel, { attributes: true, attributeFilter: ['class'] });
  if (!existait) {
    panel.querySelector('.lc-cat-close').addEventListener('click', fermer);
    scrim.addEventListener('click', fermer);
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape' && panel.classList.contains('open')) fermer(); });
  }
  // Celui qui ouvre le menu s'est perdu : il ARRIVE. Au-delà de deux écrans et demi (toute la visite 3D à traverser),
  // on saute ; en dessous, on glisse (26/11).
  function glisser(el, bloc) {
    var loin = Math.abs(el.getBoundingClientRect().top) > innerHeight * 2.5;
    el.scrollIntoView({ behavior: calme || loin ? 'auto' : 'smooth', block: bloc || 'start' });
  }
  window.LCGlisser = glisser;
  var aller = function (sel) {
    var el = doc.querySelector(sel);
    if (el) glisser(el, 'start');
  };
  sec.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    fermer();
    if (b.dataset.lmFamille && window.LC_INA) {
      window.LC_INA.ouvrir(b.dataset.lmFamille, b.dataset.lmSous || null);
    } else if (b.dataset.lmSoin != null) {
      // le soin, dans la liste des soins (le site « comme avant »), mis en lumière un instant
      var bk = doc.querySelector('#svcSections [data-book="' + b.dataset.lmSoin + '"]');
      var carte = bk && (bk.closest('.svc') || bk.parentElement);
      if (carte) {
        glisser(carte, 'center');
        carte.style.transition = 'box-shadow .4s ease'; carte.style.boxShadow = '0 0 0 3px #c9a84c';
        setTimeout(function () { carte.style.boxShadow = ''; }, 2200);
      } else aller('#soins');
    } else if (b.dataset.lmAncre) {
      aller(b.dataset.lmAncre);
    } else if (b.dataset.lmR != null) {
      var r = CFG.raccourcis[+b.dataset.lmR];
      if (r.clic) { var c = doc.querySelector(r.clic); if (c) setTimeout(function () { c.click(); }, 60); }
      else if (r.h) aller(r.h);
    }
  });

  /* ---------- le bouton « Menu » en haut, à côté d'« Accueil » ---------- */
  function bouton() {
    var b = doc.createElement('button');
    b.type = 'button'; b.className = 'lm-btn'; b.setAttribute('aria-label', 'Ouvrir le menu');
    b.setAttribute('aria-haspopup', 'dialog');
    b.innerHTML = ICONE + '<span>Menu</span>';
    b.addEventListener('click', function (e) { e.stopPropagation(); ouvrir(); });
    return b;
  }
  var accueil = doc.querySelector('.head-in .back-hub, header.tete .retour');
  var haut;
  if (accueil) {
    var g = doc.createElement('div'); g.className = 'lm-gauche';
    accueil.parentNode.insertBefore(g, accueil);
    g.appendChild(accueil);
    // le mot « Accueil » se cache au téléphone (la flèche reste) : il faut la place pour « Menu »
    [].slice.call(accueil.childNodes).forEach(function (n) {
      if (n.nodeType === 3 && n.textContent.trim()) { var s = doc.createElement('span'); s.className = 'lm-mot'; s.textContent = n.textContent.trim(); accueil.replaceChild(s, n); }
    });
    if (!accueil.getAttribute('aria-label')) accueil.setAttribute('aria-label', 'Accueil');
    haut = bouton(); g.appendChild(haut);
  } else if (CFG.hub) {
    var w = doc.createElement('div'); w.className = 'lm-hub';
    haut = bouton(); w.appendChild(haut);
    doc.body.appendChild(w);
  }

  /* les autres portes vers le menu : le bouton de la barre du bas, « Catalogue » d'INA, « Tout le catalogue » */
  var dock = doc.getElementById('lcCatBtn');
  if (dock) {
    var s = dock.querySelector('span'); if (s) s.textContent = 'Menu';
    dock.setAttribute('aria-label', 'Ouvrir le menu');
  }
  var rayon = doc.getElementById('menuToggle');
  if (rayon) {
    rayon.lastChild.textContent = ' Menu';
    rayon.addEventListener('click', function (e) { e.stopImmediatePropagation(); e.preventDefault(); ouvrir(); }, true);
  }
  doc.addEventListener('click', function (e) {
    if (e.target.closest('[data-lm-ouvrir]')) { e.preventDefault(); ouvrir(); }
  });

  /* ---------- la bulle « Retrouvez ici notre menu » ---------- */
  var bulle = null, cle = 'lmBulle:' + location.pathname;
  function cacherBulle() {
    if (!bulle) return;
    bulle.classList.remove('on');
    var b = bulle; bulle = null;
    setTimeout(function () { if (b.parentNode) b.parentNode.removeChild(b); }, 400);
  }
  function montrerBulle() {
    try { if (sessionStorage.getItem(cle)) return; sessionStorage.setItem(cle, '1'); } catch (e) { /* navigation privée : on montre quand même */ }
    if (!haut) return;
    var r = haut.getBoundingClientRect();
    if (r.bottom < 0 || r.top > innerHeight || r.width === 0) return;
    bulle = doc.createElement('div');
    bulle.className = 'lm-bulle'; bulle.setAttribute('role', 'status');
    bulle.textContent = 'Retrouvez ici notre menu';
    doc.body.appendChild(bulle);
    var x = Math.max(10, Math.min(innerWidth - 250, r.left));
    bulle.style.left = x + 'px';
    bulle.style.top = (r.bottom + 12) + 'px';
    bulle.style.setProperty('--lm-fleche', Math.max(12, r.left + r.width / 2 - x - 7) + 'px');
    requestAnimationFrame(function () { if (bulle) bulle.classList.add('on'); });
    setTimeout(cacherBulle, 6500);
    addEventListener('scroll', function f() { if (scrollY > 400) { cacherBulle(); removeEventListener('scroll', f); } }, { passive: true });
  }
  // la bulle vient après l'écran d'accueil de la page (on attend le premier geste du visiteur)
  var vu = false;
  function premier() {
    if (vu) return; vu = true;
    setTimeout(montrerBulle, 900);
  }
  ['pointerdown', 'keydown', 'touchstart'].forEach(function (t) { addEventListener(t, premier, { passive: true, once: true }); });
  setTimeout(function () { if (!vu && !doc.getElementById('welcome-gate')) premier(); }, 3500);
})();

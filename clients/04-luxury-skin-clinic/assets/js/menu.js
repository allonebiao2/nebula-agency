/* LE MENU · commun aux quatre pages de Luxury Club 229.
 *
 * La cliente (26/11) : « à côté de l'accueil, tu mets le truc avec l'icône de menu, tu mets Menu » ; « catalogue,
 * les gens ne comprennent pas » ; « si quelqu'un se perd, il clique sur Menu et ça l'amène dans un espace normal » ;
 * « une petite notification en haut : Retrouvez ici notre menu ».
 * Mongazi (27/11) : « le menu moins généré par IA, beaucoup plus profond, ajoute de la profondeur et de la beauté ».
 *
 * Avant : un tiroir de 322 px, une liste de texte et des puces « · » (un gabarit). Maintenant : LA CARTE, plein écran.
 *  · un grand titre éditorial propre à chaque univers (« La boutique », « La carte des soins », « Les techniques ») ;
 *  · INA : chaque famille est une carte, avec SES vrais produits détourés en éventail, posés sur leur ombre, qui
 *    débordent de la carte (la profondeur) ; ses sous-catégories en pastilles ;
 *  · la clinique : une carte de spa imprimée, le croquis de chaque soin, son nom, sa durée, des points de conduite et
 *    son prix ;
 *  · le cabinet : les techniques avec les visuels de SES flyers, inclinés, qui se redressent au survol ;
 *  · en bas, les quatre univers et WhatsApp.
 * ⛔ Aucune image générée par IA : des produits photographiés, les flyers de la cliente, nos croquis dessinés.
 * Le menu ne mène JAMAIS dans la visite 3D : il mène aux listes de la page (le site « comme avant »).
 * Chaque page déclare ses raccourcis dans window.LC_MENU (posé par _outils/_menu_poser.py).
 */
(function () {
  var CFG = window.LC_MENU || {};
  var doc = document;
  var calme = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var ICONE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>';
  var FLECHE = '<svg viewBox="0 0 24 12" aria-hidden="true"><path d="M1 6h21M17 1l5 5-5 5"/></svg>';
  var DETOURES = 'assets/images/ina-luxury/_detoures/detoures.json?v=20261126y';
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  // un prix ne se coupe jamais en deux lignes (« dès 7 / 500 F » au téléphone, 27/11) : espaces insécables
  var fcfa = function (n) { return Number(n || 0).toLocaleString('fr-FR').replace(/ | | /g, ' ') + ' F'; };
  var deux = function (n) { return (n < 9 ? '0' : '') + (n + 1); };
  var ICI = (location.pathname.split('/').pop() || 'index.html').replace(/\.html$/, '') || 'index';

  /* ---------- le style ---------- */
  var css = doc.createElement('style');
  css.id = 'lm-css';
  css.textContent = [
    /* le bouton « Menu » de l'en-tête et la bulle */
    '.lm-gauche{display:flex;align-items:center;gap:6px;}',
    '.layout{scroll-margin-top:150px;}#soins,#rdv-booking,#questions,#techniques,.tech{scroll-margin-top:86px;}',
    '.lm-gauche .back-hub,.lm-gauche .retour{display:inline-flex;align-items:center;justify-content:center;min-width:44px;min-height:44px;}',
    '.lm-btn{display:inline-flex;align-items:center;gap:8px;min-height:44px;min-width:44px;padding:0 14px;border-radius:999px;cursor:pointer;',
    '  font:600 12.5px/1 "Jost",system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;',
    '  background:#1c1812;color:#f3e3b5;border:1px solid rgba(201,168,76,.65);transition:background .25s,color .25s,border-color .25s;}',
    '.lm-btn:hover,.lm-btn:focus-visible{background:#c9a84c;color:#16120a;border-color:#c9a84c;}',
    '.lm-btn:focus-visible{outline:2px solid #c9a84c;outline-offset:3px;}',
    '.lm-btn svg{width:17px;height:17px;stroke:currentColor;fill:none;stroke-width:2;flex:none;}',
    '.lm-hub{position:absolute;top:14px;left:14px;z-index:60;}',
    '.lm-bulle{position:fixed;z-index:9000;pointer-events:none;max-width:240px;padding:10px 14px;border-radius:12px;',
    '  background:#c9a84c;color:#16120a;font:600 13.5px/1.35 "Jost",system-ui,sans-serif;box-shadow:0 12px 30px rgba(0,0,0,.28);',
    '  opacity:0;transform:translateY(-6px);transition:opacity .35s ease,transform .35s ease;}',
    '.lm-bulle.on{opacity:1;transform:none;}',
    '.lm-bulle::before{content:"";position:absolute;top:-7px;left:var(--lm-fleche,24px);border:7px solid transparent;border-top:0;border-bottom-color:#c9a84c;}',
    '@media(max-width:760px){.lm-gauche .back-hub .lm-mot,.lm-gauche .retour span{display:none;}.lm-btn{padding:0 12px;letter-spacing:.1em;}}',

    /* LA CARTE */
    '.lm-carte{position:fixed;inset:0;z-index:9500;visibility:hidden;opacity:0;transition:opacity .45s ease,visibility 0s linear .45s;color:#f1e6cf;}',
    '.lm-carte.open{visibility:visible;opacity:1;transition-delay:0s;}',
    '.lm-fond{position:absolute;inset:0;overflow:hidden;background:',
    '  radial-gradient(110% 70% at 88% -8%,rgba(201,168,76,.24),rgba(201,168,76,0) 58%),',
    '  radial-gradient(80% 60% at -5% 105%,rgba(122,74,34,.38),rgba(122,74,34,0) 62%),',
    '  linear-gradient(172deg,#19130c 0%,#0c0a07 58%,#070605 100%);}',
    '.lm-fili{position:absolute;right:-5vw;top:6vh;font:500 min(64vw,760px)/.78 "Cormorant Garamond",Georgia,serif;letter-spacing:-.05em;',
    '  color:rgba(201,168,76,.055);pointer-events:none;user-select:none;will-change:transform;}',
    '.lm-defile{position:absolute;inset:0;overflow-y:auto;overscroll-behavior:contain;-webkit-overflow-scrolling:touch;}',
    '.lm-in{position:relative;max-width:1140px;margin:0 auto;padding:0 clamp(16px,4vw,52px) calc(40px + env(safe-area-inset-bottom));}',
    '.lm-tete{position:sticky;top:0;z-index:3;display:flex;align-items:center;justify-content:space-between;gap:12px;',
    '  padding:calc(14px + env(safe-area-inset-top)) 0 14px;background:linear-gradient(#120e09 62%,rgba(18,14,9,0));}',
    '.lm-marque{display:flex;align-items:center;gap:12px;font:600 11px/1.2 "Jost",system-ui,sans-serif;letter-spacing:.3em;text-transform:uppercase;color:#c9a84c;}',
    '.lm-mono{width:38px;height:38px;border-radius:50%;display:grid;place-items:center;border:1px solid rgba(201,168,76,.55);',
    '  font:600 15px/1 "Cormorant Garamond",serif;letter-spacing:0;color:#e9d394;box-shadow:inset 0 0 0 3px rgba(201,168,76,.08);}',
    '.lm-x{width:50px;height:50px;border-radius:50%;display:grid;place-items:center;cursor:pointer;flex:none;color:#f1e6cf;',
    '  background:rgba(255,240,210,.04);border:1px solid rgba(201,168,76,.45);transition:transform .45s cubic-bezier(.2,.8,.2,1),background .3s;}',
    '.lm-x:hover{transform:rotate(90deg);background:rgba(201,168,76,.16);}',
    '.lm-x svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.7;}',
    '.lm-x:focus-visible,.lm-carte button:focus-visible,.lm-carte a:focus-visible{outline:2px solid #c9a84c;outline-offset:3px;}',
    '.lm-titre{padding:clamp(14px,5vh,52px) 0 clamp(22px,4.5vh,44px);}',
    '.lm-sur{display:flex;align-items:center;gap:12px;font:500 11.5px/1 "Jost",sans-serif;letter-spacing:.32em;text-transform:uppercase;color:#c9a84c;}',
    '.lm-sur::before{content:"";width:34px;height:1px;background:linear-gradient(90deg,#c9a84c,rgba(201,168,76,0));}',
    '.lm-titre h2{margin:16px 0 0;font:500 clamp(46px,9.5vw,96px)/.95 "Cormorant Garamond",Georgia,serif;letter-spacing:-.01em;color:#f6ecd8;',
    '  text-shadow:0 18px 40px rgba(0,0,0,.55);}',
    '.lm-titre h2 em{font-style:italic;color:#e2c47a;}',
    '.lm-titre p{margin:14px 0 0;max-width:560px;font:400 15.5px/1.6 "Jost",sans-serif;color:#bfb196;}',
    /* une carte, en relief : liseré d'or, lumière par le haut, ombre longue */
    '.lm-bloc{position:relative;border-radius:24px;border:1px solid rgba(201,168,76,.22);',
    '  background:linear-gradient(152deg,rgba(255,236,200,.075),rgba(255,236,200,.012) 46%),#130f0a;',
    '  box-shadow:inset 0 1px 0 rgba(255,236,200,.09),0 34px 64px -30px rgba(0,0,0,.95),0 14px 26px -14px rgba(0,0,0,.7);',
    '  transition:transform .5s cubic-bezier(.2,.8,.2,1),border-color .4s,box-shadow .5s;}',
    '@media(hover:hover){.lm-bloc:hover{transform:translateY(-5px);border-color:rgba(201,168,76,.5);',
    '  box-shadow:inset 0 1px 0 rgba(255,236,200,.12),0 44px 80px -30px rgba(0,0,0,1),0 18px 30px -14px rgba(0,0,0,.75);}}',
    '.lm-num{font:500 13px/1 "DM Mono","Jost",monospace;letter-spacing:.1em;color:#c9a84c;}',
    '.lm-nom{display:block;font:500 clamp(30px,5vw,40px)/1 "Cormorant Garamond",Georgia,serif;color:#f6ecd8;}',
    '.lm-meta{display:block;margin-top:9px;font:500 11.5px/1.35 "Jost",sans-serif;letter-spacing:.15em;text-transform:uppercase;color:#bda772;}',
    /* l'entrée : chaque bloc monte en perspective, l'un après l'autre */
    '.lm-anim{opacity:0;transform:perspective(1100px) translate3d(0,38px,-70px) rotateX(10deg);transform-origin:50% 100%;',
    '  transition:opacity .65s ease,transform .95s cubic-bezier(.16,.84,.24,1);transition-delay:calc(var(--i,0) * 65ms + 90ms);}',
    '.lm-carte.open .lm-anim{opacity:1;transform:none;}',
    /* INA : les familles */
    '.lm-familles{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,470px),1fr));gap:30px 22px;padding-top:30px;}',
    '.lm-fam{padding-bottom:16px;}',
    '.lm-fam-lien{all:unset;box-sizing:border-box;display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:end;gap:10px;width:100%;',
    '  padding:22px 18px 14px 24px;cursor:pointer;min-height:156px;}',
    '.lm-fam-lien .lm-num{display:block;margin-bottom:14px;}',
    '.lm-pile{position:relative;width:min(160px,40vw);height:150px;margin:-62px 0 0;}',
    '.lm-pile::after{content:"";position:absolute;left:6%;right:6%;bottom:-8px;height:18px;z-index:0;',
    '  background:radial-gradient(closest-side,rgba(0,0,0,.75),rgba(0,0,0,0));}',
    '.lm-pile img{position:absolute;bottom:0;left:50%;width:auto;height:auto;max-width:44%;max-height:140px;object-fit:contain;transform-origin:50% 100%;',
    '  filter:drop-shadow(0 18px 18px rgba(0,0,0,.62)) drop-shadow(0 2px 3px rgba(0,0,0,.5));transition:transform .6s cubic-bezier(.2,.8,.2,1);}',
    '.lm-pile img:nth-child(1){transform:translateX(-100%) rotate(-9deg) scale(.84);z-index:1;}',
    '.lm-pile img:nth-child(2){transform:translateX(-50%);z-index:3;}',
    '.lm-pile img:nth-child(3){transform:translateX(0) rotate(9deg) scale(.84);z-index:2;}',
    '.lm-pile img:only-child{transform:translateX(-50%);}',
    '@media(hover:hover){.lm-fam:hover .lm-pile img:nth-child(1){transform:translateX(-118%) rotate(-15deg) scale(.86);}',
    '  .lm-fam:hover .lm-pile img:nth-child(2){transform:translateX(-50%) translateY(-8px) scale(1.04);}',
    '  .lm-fam:hover .lm-pile img:nth-child(3){transform:translateX(18%) rotate(15deg) scale(.86);}}',
    '.lm-pills{display:flex;flex-wrap:wrap;gap:8px;padding:0 24px;}',
    '.lm-pill,.lm-chip{all:unset;box-sizing:border-box;cursor:pointer;min-height:44px;display:inline-flex;align-items:center;padding:0 16px;border-radius:999px;',
    '  font:500 13.5px/1 "Jost",sans-serif;color:#eadfc4;border:1px solid rgba(201,168,76,.3);background:rgba(255,240,210,.03);',
    '  transition:background .3s,color .3s,border-color .3s;}',
    '.lm-pill:hover,.lm-chip:hover{background:#c9a84c;border-color:#c9a84c;color:#16120a;}',
    /* la clinique : la carte des soins */
    '.lm-soins{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,500px),1fr));gap:24px;align-items:start;}',
    '.lm-groupe{padding:24px clamp(16px,3vw,28px) 12px;}',
    '.lm-g-tete{display:flex;align-items:flex-end;gap:14px;padding-bottom:16px;border-bottom:1px solid rgba(201,168,76,.22);}',
    '.lm-g-tete .lm-nom{font-size:clamp(28px,4.4vw,36px);}',
    '.lm-g-tete .lm-meta{margin:0 0 4px auto;white-space:nowrap;}',
    '.lm-soin{all:unset;box-sizing:border-box;cursor:pointer;display:grid;grid-template-columns:54px minmax(0,max-content) minmax(14px,1fr) auto;align-items:end;',
    '  gap:12px;width:100%;padding:13px 6px;min-height:62px;border-bottom:1px solid rgba(201,168,76,.08);border-radius:10px;transition:background .3s,transform .35s;}',
    '.lm-soin:last-child{border-bottom:0;}',
    '@media(hover:hover){.lm-soin:hover{background:rgba(201,168,76,.07);transform:translateX(5px);}}',
    '.lm-croq{align-self:center;}.lm-croq svg{display:block;width:54px;height:26px;}',
    '.lm-sn{font:500 20px/1.15 "Cormorant Garamond",Georgia,serif;color:#f3e8d1;}',
    '.lm-sn small{display:block;margin-top:5px;font:500 10.5px/1.3 "Jost",sans-serif;letter-spacing:.13em;text-transform:uppercase;color:#a89770;}',
    '.lm-filet{border-bottom:1.5px dotted rgba(201,168,76,.42);margin-bottom:7px;}',
    '.lm-px{font:500 16.5px/1 "Jost",sans-serif;color:#e2c47a;white-space:nowrap;padding-bottom:3px;}',
    '@media(max-width:520px){.lm-soin{grid-template-columns:44px minmax(0,1fr) auto;}.lm-croq svg{width:44px;height:21px;}.lm-filet{display:none;}}',
    /* le cabinet : les techniques et leurs flyers */
    '.lm-techs{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,250px),1fr));gap:24px 20px;}',
    '.lm-tech{all:unset;box-sizing:border-box;cursor:pointer;display:block;padding:18px 18px 20px;perspective:900px;}',
    '.lm-tech img{display:block;width:100%;aspect-ratio:4/5;object-fit:cover;object-position:50% 20%;border-radius:12px;',
    '  box-shadow:0 30px 44px -20px rgba(0,0,0,.95),0 0 0 1px rgba(201,168,76,.25);transform:rotateY(-10deg) rotateX(5deg) translateZ(0);',
    '  transition:transform .7s cubic-bezier(.2,.8,.2,1);margin-bottom:18px;}',
    '@media(hover:hover){.lm-tech:hover img{transform:rotateY(0) rotateX(0) translateZ(30px);}}',
    '.lm-tech .lm-num{display:block;margin-bottom:8px;}',
    '.lm-tech .lm-nom{font-size:clamp(26px,3.6vw,30px);}',
    /* les raccourcis, les univers, WhatsApp */
    '.lm-chips{display:flex;flex-wrap:wrap;gap:10px;margin-top:30px;}',
    '.lm-sep{display:flex;align-items:center;gap:14px;margin:clamp(36px,7vh,64px) 0 18px;font:500 11.5px/1 "Jost",sans-serif;letter-spacing:.3em;text-transform:uppercase;color:#c9a84c;}',
    '.lm-sep::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,rgba(201,168,76,.4),rgba(201,168,76,0));}',
    '.lm-univers{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;}',
    '.lm-u{position:relative;display:flex;flex-direction:column;justify-content:flex-end;min-height:156px;padding:16px 16px 15px;text-decoration:none;overflow:hidden;}',
    '.lm-u img{position:absolute;right:10px;top:12px;width:auto;max-width:46%;height:86px;object-fit:contain;',
    '  filter:drop-shadow(0 12px 14px rgba(0,0,0,.6));transition:transform .6s cubic-bezier(.2,.8,.2,1);}',
    '.lm-u img.lm-u-flyer{right:0;top:0;height:100%;max-width:52%;width:52%;object-fit:cover;filter:none;opacity:.5;',
    '  -webkit-mask-image:linear-gradient(90deg,transparent,#000 60%);mask-image:linear-gradient(90deg,transparent,#000 60%);}',
    '@media(hover:hover){.lm-u:hover img{transform:translateY(-5px) scale(1.05);}}',
    /* une balise <i> : la règle des sous-titres des tuiles (.lm-u span) ne doit pas l'atteindre */
    '.lm-u-mono{font-style:normal;position:absolute;right:14px;top:14px;width:70px;height:70px;border-radius:50%;display:grid;place-items:center;',
    '  font:500 28px/1 "Cormorant Garamond",Georgia,serif;color:#ecd79c;border:1px solid rgba(201,168,76,.6);',
    '  background:radial-gradient(circle at 35% 30%,rgba(255,236,200,.12),rgba(0,0,0,0) 70%);box-shadow:inset 0 0 0 5px rgba(201,168,76,.07),0 14px 28px -12px rgba(0,0,0,.9);}',
    '.lm-u b{position:relative;font:500 23px/1.05 "Cormorant Garamond",Georgia,serif;color:#f6ecd8;}',
    '.lm-u span{position:relative;display:block;margin-top:7px;font:500 10.5px/1.3 "Jost",sans-serif;letter-spacing:.15em;text-transform:uppercase;color:#bda772;}',
    '.lm-u[aria-current="page"]{border-color:rgba(201,168,76,.62);}',
    '.lm-u[aria-current="page"] span{color:#e2c47a;}',
    '.lm-wa{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-top:14px;padding:18px 22px;text-decoration:none;',
    '  font:500 15px/1.3 "Jost",sans-serif;color:#f1e6cf;}',
    '.lm-wa svg{width:26px;height:13px;stroke:#c9a84c;fill:none;stroke-width:1.6;flex:none;}',
    '@media(max-width:760px){.lm-univers{grid-auto-flow:column;grid-template-columns:none;grid-auto-columns:72%;overflow-x:auto;scroll-snap-type:x mandatory;',
    '  padding:6px 2px 10px;margin:0 -2px;scrollbar-width:none;}.lm-univers::-webkit-scrollbar{display:none;}.lm-u{scroll-snap-align:start;}',
    '  .lm-fam-lien{padding:20px 14px 12px 20px;}.lm-pills{padding:0 20px;}.lm-pile{height:132px;margin-top:-54px;}.lm-pile img{max-height:122px;}}',
    '@media(prefers-reduced-motion:reduce){.lm-carte,.lm-anim,.lm-bloc,.lm-pile img,.lm-tech img,.lm-bulle{transition:none;}.lm-anim{opacity:1;transform:none;}}'
  ].join('\n');
  doc.head.appendChild(css);

  /* ---------- la carte ---------- */
  var carte = doc.createElement('div');
  carte.className = 'lm-carte'; carte.id = 'lmCarte';
  carte.setAttribute('role', 'dialog'); carte.setAttribute('aria-modal', 'true'); carte.setAttribute('aria-label', 'Menu Luxury Club 229');
  carte.innerHTML = '<div class="lm-fond" aria-hidden="true"><span class="lm-fili">LC</span></div>' +
    '<div class="lm-defile"><div class="lm-in">' +
    '<div class="lm-tete"><div class="lm-marque"><span class="lm-mono" aria-hidden="true">LC</span>Luxury Club 229</div>' +
    '<button class="lm-x" type="button" aria-label="Fermer le menu"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>' +
    '<div class="lm-corps"></div></div></div>';
  doc.body.appendChild(carte);
  var corps = carte.querySelector('.lm-corps'), defile = carte.querySelector('.lm-defile'), fili = carte.querySelector('.lm-fili');

  // les produits détourés d'INA (les vraies photos, sans leur fond), lus une fois
  var detoures = null;
  function chargerDetoures() {
    if (detoures) return detoures;
    detoures = fetch(DETOURES).then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; });
    return detoures;
  }

  var GROUPES = { visage: 'Soins du visage', corps: 'Soins du corps', capillaires: 'Soins capillaires', complet: 'Expérience VIP' };
  var duree = function (s) { var m = (s.meta || []).filter(function (x) { return /h|min|séance|semaine/i.test(x[0]); })[0]; return m ? m[0] : ''; };

  function titre(sur, h2, p) {
    return '<div class="lm-titre lm-anim" style="--i:0"><div class="lm-sur">' + esc(sur) + '</div><h2>' + h2 + '</h2>' + (p ? '<p>' + esc(p) + '</p>' : '') + '</div>';
  }

  function boutique(det) {
    var I = window.LC_INA, k = 0;
    var fams = I.familles.filter(function (f) { return I.produits.some(function (p) { return p.f === f.key; }); });
    var h = titre('INA Luxury', 'La <em>boutique</em>', I.produits.length + ' produits, en ' + fams.length + ' familles. Touchez une famille pour voir ses produits.');
    h += '<div class="lm-familles">';
    fams.forEach(function (f, i) {
      var ps = I.produits.filter(function (p) { return p.f === f.key; });
      var prix = ps.map(function (p) { return p.p; }).filter(function (x) { return x > 0; });
      var vis = ps.filter(function (p) { return det && det[p.n]; });
      vis = vis.filter(function (p) { return p.best; }).concat(vis.filter(function (p) { return !p.best; })).slice(0, 3);
      // la plus haute au milieu
      if (vis.length === 3) vis = [vis[1], vis[0], vis[2]];
      var sous = (I.sous[f.key] || []).filter(function (s) { return ps.some(function (p) { return p.s === s.key; }); });
      h += '<article class="lm-bloc lm-fam lm-anim" style="--i:' + (++k) + '">' +
        '<button type="button" class="lm-fam-lien" data-lm-famille="' + esc(f.key) + '" aria-label="' + esc(f.label + ', ' + ps.length + ' produits') + '">' +
        '<span><span class="lm-num">' + deux(i) + '</span><span class="lm-nom">' + esc(f.label) + '</span>' +
        '<span class="lm-meta">' + ps.length + ' produit' + (ps.length > 1 ? 's' : '') + (prix.length ? ' · <span style="white-space:nowrap">dès ' + fcfa(Math.min.apply(null, prix)) + '</span>' : '') + '</span></span>' +
        '<span class="lm-pile" aria-hidden="true">' + vis.map(function (p) {
          return '<img src="' + esc(det[p.n]) + '" alt="" loading="lazy" decoding="async">';
        }).join('') + '</span></button>' +
        (sous.length ? '<div class="lm-pills">' + sous.map(function (s) {
          return '<button type="button" class="lm-pill" data-lm-famille="' + esc(f.key) + '" data-lm-sous="' + esc(s.key) + '">' + esc(s.label) + '</button>';
        }).join('') + '</div>' : '') + '</article>';
    });
    return h + '</div>';
  }

  function soins() {
    var C = window.LC_CLINIC, S = C.services, art = C.art || {}, artF = C.artFamille || {}, k = 0, vus = [];
    S.forEach(function (s) { if (vus.indexOf(s.g) < 0) vus.push(s.g); });
    var h = titre('Luxury Skin Clinic', 'La carte <em>des soins</em>', S.length + ' soins, réalisés par Mme Sabrina, esthéticienne diplômée. Du lundi au samedi, sur rendez-vous.');
    h += '<div class="lm-soins">';
    vus.forEach(function (g) {
      var liste = S.map(function (s, i) { return { s: s, i: i }; }).filter(function (x) { return x.s.g === g; });
      h += '<section class="lm-bloc lm-groupe lm-anim" style="--i:' + (++k) + '"><div class="lm-g-tete"><span class="lm-nom">' + esc(GROUPES[g] || g) + '</span>' +
        '<span class="lm-meta">' + liste.length + ' soin' + (liste.length > 1 ? 's' : '') + '</span></div>' +
        liste.map(function (x) {
          var d = duree(x.s);
          return '<button type="button" class="lm-soin" data-lm-soin="' + x.i + '"><span class="lm-croq" aria-hidden="true">' + (art[x.s.a] || artF[x.s.g] || '') + '</span>' +
            '<span class="lm-sn">' + esc(x.s.n) + (d ? '<small>' + esc(d) + '</small>' : '') + '</span><span class="lm-filet" aria-hidden="true"></span>' +
            '<span class="lm-px">' + (x.s.p ? fcfa(x.s.p) : 'Sur devis') + '</span></button>';
        }).join('') + '</section>';
    });
    return h + '</div>';
  }

  function techniques() {
    var H = window.LC_HARMO, T = H.donnees, k = 0;
    var h = titre('Cabinet privé', 'Les <em>techniques</em>', T.length + ' techniques d’harmonisation faciale. Une lecture, zone par zone, et le tarif de chacune.');
    h += '<div class="lm-techs">';
    T.forEach(function (t, i) {
      var p = (t.zones || []).map(function (z) { return z.pMin || z.p || 0; }).filter(function (x) { return x > 0; });
      h += '<button type="button" class="lm-bloc lm-tech lm-anim" style="--i:' + (++k) + '" data-lm-ancre="#' + esc(t.id) + '">' +
        (t.flyer ? '<img src="' + esc(t.flyer) + '" alt="" loading="lazy" decoding="async">' : '') +
        '<span class="lm-num">' + deux(i) + '</span><span class="lm-nom">' + esc(t.nom) + '</span>' +
        '<span class="lm-meta">' + (t.zones || []).length + ' zones' + (p.length ? ' · <span style="white-space:nowrap">dès ' + fcfa(Math.min.apply(null, p)) + '</span>' : '') + '</span></button>';
    });
    return h + '</div>';
  }

  function univers(det, k) {
    var produit = det && (det['Savon Noir Papaya'] || det[Object.keys(det)[0]]);
    var U = [
      // les logos en PNG ont un fond noir carré : un monogramme dessiné à la place (27/11)
      { id: 'index', t: 'Luxury Club 229', s: 'L’accueil', h: 'index.html', mono: 'LC' },
      { id: 'luxury-skin-clinic', t: 'Luxury Skin Clinic', s: 'Les soins', h: 'luxury-skin-clinic.html', mono: 'LS' },
      { id: 'ina-luxury', t: 'INA Luxury', s: 'La boutique', h: 'ina-luxury.html', img: produit || '' },
      { id: 'harmonisation-faciale', t: 'Harmonisation faciale', s: 'Le cabinet', h: 'harmonisation-faciale.html', img: 'assets/harmonisation/flyer-facial-balancing.jpg', flyer: true }
    ];
    return '<div class="lm-sep lm-anim" style="--i:' + k + '">Nos univers</div><nav class="lm-univers lm-anim" style="--i:' + (k + 1) + '" aria-label="Nos univers">' +
      U.map(function (u) {
        var la = u.id === ICI;
        return '<a class="lm-bloc lm-u" href="' + u.h + '"' + (la ? ' aria-current="page"' : '') + '>' +
          (u.mono ? '<i class="lm-u-mono" aria-hidden="true">' + u.mono + '</i>' : '') +
          (u.img ? '<img src="' + esc(u.img) + '" alt="" loading="lazy" decoding="async"' + (u.flyer ? ' class="lm-u-flyer"' : '') + '>' : '') +
          '<b>' + esc(u.t) + '</b><span>' + (la ? 'Vous êtes ici' : esc(u.s)) + '</span></a>';
      }).join('') + '</nav>' +
      '<a class="lm-bloc lm-wa lm-anim" style="--i:' + (k + 2) + '" href="https://wa.me/2290167975626" target="_blank" rel="noopener">' +
      'Une question ? Écrivez à la maison sur WhatsApp' + FLECHE + '</a>';
  }

  function remplir(det) {
    var h = '';
    if (CFG.familles && window.LC_INA) h += boutique(det);
    else if (CFG.soins && window.LC_CLINIC) h += soins();
    else if (CFG.techniques && window.LC_HARMO) h += techniques();
    else h += titre('Luxury Club 229', 'Nos <em>univers</em>', 'Les soins de Mme Sabrina, la boutique INA Luxury, le cabinet d’harmonisation faciale.');
    var n = (h.match(/lm-anim/g) || []).length;
    if (CFG.raccourcis && CFG.raccourcis.length) {
      h += '<div class="lm-chips lm-anim" style="--i:' + (n + 1) + '">' + CFG.raccourcis.map(function (r, i) {
        return r.h && r.h.charAt(0) !== '#' && r.h.charAt(0) !== '.'
          ? '<a class="lm-chip" href="' + esc(r.h) + '">' + esc(r.t) + '</a>'
          : '<button type="button" class="lm-chip" data-lm-r="' + i + '">' + esc(r.t) + '</button>';
      }).join('') + '</div>';
    }
    corps.innerHTML = h + univers(det, n + 2);
  }

  /* ---------- ouvrir, fermer ---------- */
  var avant = null, ouvert = false;
  function ouvrir() {
    if (ouvert) return;
    ouvert = true; avant = doc.activeElement;
    remplir(null);
    chargerDetoures().then(function (det) { if (ouvert && det && Object.keys(det).length) { remplir(det); } });
    defile.scrollTop = 0; fili.style.transform = '';
    // deux images : la carte se pose, PUIS ses blocs entrent (sinon le navigateur saute l'animation)
    requestAnimationFrame(function () { requestAnimationFrame(function () { carte.classList.add('open'); }); });
    doc.documentElement.classList.add('lm-ouvert');
    doc.documentElement.style.overflow = 'hidden';
    if (window.LCAudio) window.LCAudio.play('menuOpen'); else if (window.LCBruit) window.LCBruit('menu');
    setTimeout(function () { var x = carte.querySelector('.lm-x'); if (x) x.focus({ preventScroll: true }); }, 60);
    cacherBulle();
  }
  function fermer() {
    if (!ouvert) return;
    ouvert = false;
    carte.classList.remove('open');
    doc.documentElement.classList.remove('lm-ouvert');
    doc.documentElement.style.overflow = '';
    if (window.LCAudio) window.LCAudio.play('menuClose'); else if (window.LCBruit) window.LCBruit('menu');
    if (avant && avant.focus) try { avant.focus({ preventScroll: true }); } catch (e) {}
  }
  window.LCMenu = { ouvrir: ouvrir, fermer: fermer };
  carte.querySelector('.lm-x').addEventListener('click', fermer);
  doc.addEventListener('keydown', function (e) { if (e.key === 'Escape' && ouvert) fermer(); });
  // le grand monogramme, en filigrane, remonte plus lentement que la carte (la profondeur)
  var rafF = 0;
  defile.addEventListener('scroll', function () {
    if (calme || rafF) return;
    rafF = requestAnimationFrame(function () { rafF = 0; fili.style.transform = 'translate3d(0,' + (-defile.scrollTop * 0.22) + 'px,0)'; });
  }, { passive: true });

  // Celui qui ouvre le menu s'est perdu : il ARRIVE. Au-delà de deux écrans et demi (toute la visite 3D à traverser),
  // on saute ; en dessous, on glisse (26/11).
  function glisser(el, bloc) {
    var loin = Math.abs(el.getBoundingClientRect().top) > innerHeight * 2.5;
    el.scrollIntoView({ behavior: calme || loin ? 'auto' : 'smooth', block: bloc || 'start' });
  }
  window.LCGlisser = glisser;
  var aller = function (sel) { var el = doc.querySelector(sel); if (el) glisser(el, 'start'); };
  corps.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    fermer();
    if (b.dataset.lmFamille && window.LC_INA) {
      window.LC_INA.ouvrir(b.dataset.lmFamille, b.dataset.lmSous || null);
    } else if (b.dataset.lmSoin != null) {
      // le soin, dans la liste des soins (le site « comme avant »), mis en lumière un instant
      var bk = doc.querySelector('#svcSections [data-book="' + b.dataset.lmSoin + '"]');
      var c = bk && (bk.closest('.svc') || bk.parentElement);
      if (c) {
        glisser(c, 'center');
        c.style.transition = 'box-shadow .4s ease'; c.style.boxShadow = '0 0 0 3px #c9a84c';
        setTimeout(function () { c.style.boxShadow = ''; }, 2200);
      } else aller('#soins');
    } else if (b.dataset.lmAncre) {
      aller(b.dataset.lmAncre);
    } else if (b.dataset.lmR != null) {
      var r = CFG.raccourcis[+b.dataset.lmR];
      if (r.clic) { var q = doc.querySelector(r.clic); if (q) setTimeout(function () { q.click(); }, 60); }
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

  /* les autres portes vers le menu : le bouton de la barre du bas, « Catalogue » d'INA, « Tout le catalogue » ; l'ancien
     tiroir de la barre du bas n'est plus ouvert : c'est la carte qui s'ouvre */
  var dock = doc.getElementById('lcCatBtn');
  if (dock) {
    var sp = dock.querySelector('span'); if (sp) sp.textContent = 'Menu';
    dock.setAttribute('aria-label', 'Ouvrir le menu');
    dock.addEventListener('click', function (e) { e.stopImmediatePropagation(); e.preventDefault(); ouvrir(); }, true);
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
  var vu = false;
  function premier() {
    if (vu) return; vu = true;
    setTimeout(montrerBulle, 900);
  }
  ['pointerdown', 'keydown', 'touchstart'].forEach(function (t) { addEventListener(t, premier, { passive: true, once: true }); });
  setTimeout(function () { if (!vu && !doc.getElementById('welcome-gate')) premier(); }, 3500);
})();

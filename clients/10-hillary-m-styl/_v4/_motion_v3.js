   LE MOUVEMENT — « le fil »
   Une signature par section, toutes tirées du métier de couturier.
   Aucune bibliothèque : un IntersectionObserver, une boucle rAF.
   ================================================================== */
(function(){
  var doux = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fin  = window.matchMedia && window.matchMedia("(hover:hover) and (pointer:fine)").matches;

  /* ---- le rideau d'ouverture ---- */
  document.documentElement.classList.add("go");
  setTimeout(function(){
    var r = document.getElementById("rideau");
    if(r && r.parentNode) r.parentNode.removeChild(r);
  }, doux ? 60 : 2300);

  /* ---- le ruban défilant (dupliqué pour boucler sans couture) ---- */
  var mots = ["Sur-mesure","Prêt-à-porter","Cotonou","Fait à l'atelier","Vos mesures, votre coupe"];
  var piste = document.getElementById("piste");
  if(piste){
    var h = mots.map(function(m){return "<span>"+m+"</span>";}).join("");
    piste.innerHTML = h + h;
  }

  /* ---- révélations ---- */
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(!e.isIntersecting) return;
      e.target.classList.add("vu");
      io.unobserve(e.target);
    });
  }, {threshold:.14, rootMargin:"0px 0px -8% 0px"});

  function observe(sel){ Array.prototype.forEach.call(document.querySelectorAll(sel), function(el){ io.observe(el); }); }
  observe("[data-rv]"); observe("[data-drape]"); observe("[data-coupe]"); observe("[data-pil]"); observe("[data-et]");

  /* ---- 01 · le point de couture : la piqûre se fait à mesure ---- */
  /* ---- 03 · le fil qui relie les quatre étapes ------------------ */
  var piqure = document.getElementById("piqure");
  var trace  = document.getElementById("trace");
  var couture= document.getElementById("couture");
  var parcours=document.getElementById("parcours");
  var fil    = document.getElementById("fil");
  var nav    = document.getElementById("nav");
  var hero   = document.getElementById("top");
  var chemin = piqure ? piqure.querySelector("path") : null;
  var LONG   = 1000;
  if(chemin){ chemin.style.strokeDasharray = "9 7"; }

  function progSection(el){
    if(!el) return 0;
    var r = el.getBoundingClientRect();
    var vh = window.innerHeight;
    var p = (vh*0.86 - r.top) / Math.max(1, r.height*0.72);
    return Math.max(0, Math.min(1, p));
  }

  var tick = false;
  function boucle(){
    tick = false;
    var y = window.pageYOffset || document.documentElement.scrollTop;

    /* le fil de progression en haut */
    var max = document.documentElement.scrollHeight - window.innerHeight;
    if(fil) fil.style.transform = "scaleX(" + (max>0 ? y/max : 0) + ")";

    /* la barre : claire sur le héros, posée ensuite */
    if(nav && hero){
      var seuil = hero.offsetHeight - 90;
      nav.classList.toggle("pose", y > seuil);
      nav.classList.toggle("clair", y <= seuil);
    }

    /* la piqûre */
    if(chemin && couture){
      var p1 = progSection(couture);
      chemin.style.strokeDashoffset = (LONG * (1 - p1)).toFixed(1);
      piqure.style.setProperty("--p", p1.toFixed(3));
    }
    /* le fil des étapes */
    if(trace && parcours){
      trace.style.setProperty("--p", progSection(parcours).toFixed(3));
    }
  }
  function onScroll(){ if(!tick){ tick = true; requestAnimationFrame(boucle); } }
  window.addEventListener("scroll", onScroll, {passive:true});
  window.addEventListener("resize", onScroll);
  boucle();

  /* ---- 04 · les chiffres qui se comptent ---- */
  var ioC = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(!e.isIntersecting) return;
      var el = e.target, but = parseInt(el.dataset.chiffre,10) || 0;
      var pre = el.dataset.prefix||"", suf = el.dataset.suffix||"";
      if(doux){ el.textContent = pre+but+suf; ioC.unobserve(el); return; }
      var t0 = null, dur = 1100;
      function pas(t){
        if(t0===null) t0 = t;
        var k = Math.min(1, (t-t0)/dur);
        var v = Math.round(but * (1 - Math.pow(1-k, 3)));
        el.textContent = pre + v + suf;
        if(k < 1) requestAnimationFrame(pas);
      }
      requestAnimationFrame(pas);
      ioC.unobserve(el);
    });
  }, {threshold:.5});
  Array.prototype.forEach.call(document.querySelectorAll("[data-chiffre]"), function(el){ ioC.observe(el); });

  /* ---- l'aiguille (curseur) et l'aimant ---- */
  if(fin && !doux){
    var a = document.getElementById("aig"), ar = document.getElementById("aigR");
    var cx=0, cy=0, rx=0, ry=0, actif=false;
    document.addEventListener("mousemove", function(e){
      cx = e.clientX; cy = e.clientY;
      if(a && !a.classList.contains("on")){ a.classList.add("on"); if(ar) ar.classList.add("on"); }
      if(a) a.style.transform = "translate3d("+cx+"px,"+cy+"px,0)";
      if(!actif){ actif = true; suit(); }
    }, {passive:true});
    function suit(){
      rx += (cx-rx)*.16; ry += (cy-ry)*.16;
      if(ar) ar.style.transform = "translate3d("+rx.toFixed(2)+"px,"+ry.toFixed(2)+"px,0)";
      requestAnimationFrame(suit);
    }
    document.addEventListener("mouseover", function(e){
      var c = e.target.closest && e.target.closest("[data-mag],button,a,.piece");
      if(ar) ar.classList.toggle("mag", !!c);
    });
  }

  /* ---- 02 · le patron à la craie sur chaque pièce ---- */
  var ioP = new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add("vu"); ioP.unobserve(e.target); } });
  }, {threshold:.12});

  function habilleCartes(){
    Array.prototype.forEach.call(document.querySelectorAll("#grille .piece"), function(el, i){
      el.style.setProperty("--d", i % 4);
      if(!el.querySelector(".patron")){
        var ph = el.querySelector(".ph");
        if(ph){
          var svg = document.createElementNS("http://www.w3.org/2000/svg","svg");
          svg.setAttribute("class","patron");
          svg.setAttribute("viewBox","0 0 100 133");
          svg.setAttribute("preserveAspectRatio","none");
          svg.setAttribute("aria-hidden","true");
          var r = document.createElementNS("http://www.w3.org/2000/svg","rect");
          r.setAttribute("x","1"); r.setAttribute("y","1");
          r.setAttribute("width","98"); r.setAttribute("height","131");
          svg.appendChild(r); ph.appendChild(svg);
        }
      }
      ioP.observe(el);
    });
  }
  if(typeof rendreGrille === "function"){
    var _rg = rendreGrille;
    rendreGrille = function(cat){ _rg(cat); habilleCartes(); };
  }
  habilleCartes();


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
  if(typeof ouvrir === "function"){
    var _ou = ouvrir;
    ouvrir = function(id){ document.body.classList.add("lock"); _ou(id); };
  }
  if(typeof fermer === "function"){
    var _fe = fermer;
    fermer = function(){ document.body.classList.remove("lock"); _fe(); };
  }
})();
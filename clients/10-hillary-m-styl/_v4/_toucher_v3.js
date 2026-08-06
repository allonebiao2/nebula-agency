

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
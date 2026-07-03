/* Digital HSE — script partagé (maquette) : rail commun, toasts, interactions */
(function(){
  var RM = matchMedia('(prefers-reduced-motion:reduce)').matches;

  function ic(p){return '<svg viewBox="0 0 24 24">'+p+'</svg>';}
  var ICON={
    cockpit:'<path d="M3 13h4l3 7 4-16 3 9h4"/>',
    evo:'<path d="M4 16l5-6 4 3 7-9"/><path d="M17 4h4v4"/>',
    ind:'<path d="M4 19V9m5 10V5m5 14v-7m5 7V8"/>',
    rep:'<path d="M4 4h16v13H4z"/><path d="M4 21h16"/>',
    sec:'<path d="M12 3 4 6v6c0 5 3.5 8 8 10 4.5-2 8-5 8-10V6Z"/><path d="m9 12 2 2 4-4"/>',
    soc:'<circle cx="9" cy="8" r="3"/><path d="M4 20c0-3 2-5 5-5s5 2 5 5"/><circle cx="17" cy="9" r="2.4"/>',
    env:'<path d="M12 21c5-3 7-7 7-11a7 7 0 0 0-14 0c0 4 2 8 7 11Z"/><path d="M12 12c2-1 3-3 3-5"/>',
    imp:'<path d="M4 7V5h16v2M4 7l1 12h14l1-12M9 11v4m6-4v4"/>',
    site:'<path d="M4 6h16M4 12h16M4 18h10"/>'
  };

  function railHTML(active){
    function n(key,label,href,extra){
      var on = active===key ? ' on' : '';
      var tag = href ? 'a href="'+href+'"' : 'button type="button" onclick="VIGIE.toast(\'Écran à venir dans la maquette\')"';
      return '<'+ (href?'a':'button') + (href?' href="'+href+'"':' type="button"') +
             ' class="nav'+on+'"'+(href?'':' onclick="VIGIE.toast(\'Écran à venir\')')+(href?'':'"')+'>'+
             ic(ICON[key==='sec'||key==='soc'||key==='env'?key:key])+label+(extra||'')+'</'+(href?'a':'button')+'>';
    }
    // build simply and explicitly to avoid escaping issues
    function link(key,label,href,dot){
      var on=active===key?' on':'';
      var d=dot?'<span class="dot" style="'+dot+'"></span>':'';
      return '<a class="nav'+on+'" href="'+href+'">'+ic(ICON[key])+label+d+'</a>';
    }
    function stub(key,label,dot){
      var d=dot?'<span class="dot" style="'+dot+'"></span>':'';
      return '<button type="button" class="nav" onclick="VIGIE.toast(\'Écran à venir dans la maquette\')">'+ic(ICON[key])+label+d+'</button>';
    }
    return ''+
    '<div class="brand"><svg class="logo" viewBox="0 0 40 40" fill="none" aria-hidden="true">'+
      '<rect width="40" height="40" rx="10" fill="#0C6D7D"/>'+
      '<path d="M20 9c-6 3-9 5-9 5s0 8 4 12 5 4 5 4 1 0 5-4 4-12 4-12-3-2-9-5Z" stroke="#EAF3F1" stroke-width="2" fill="none"/>'+
      '<circle cx="20" cy="19.5" r="3.4" fill="#EAF3F1"/></svg>'+
      '<div><b>Digital HSE</b><small>Reporting automatisé</small></div></div>'+
    '<div class="navgroup"><span class="lbl">Pilotage</span>'+
      link('cockpit','Cockpit','index.html')+
      link('evo','Évolution','evolution.html')+
      link('ind','Indicateurs','indicateurs.html')+
      link('rep','Rapports','rapports.html')+'</div>'+
    '<div class="navgroup"><span class="lbl">Les 3 mondes · socle unifié</span>'+
      stub('sec','Sécurité','background:var(--safe);box-shadow:0 0 0 3px var(--safe-t)')+
      stub('soc','Social','background:var(--line2)')+
      stub('env','Environnement','background:var(--line2)')+'</div>'+
    '<div class="navgroup"><span class="lbl">Données</span>'+
      link('imp','Import Excel/CSV','saisie.html')+
      stub('site','Sites &amp; effectifs')+'</div>'+
    '<div class="rail-foot">Usine de Cotonou · 312 agents<br>Maquette de direction — données fictives</div>';
  }

  var tEl,tTo;
  function toast(m){
    if(!tEl){tEl=document.getElementById('toast');}
    if(!tEl)return;
    tEl.textContent=m;tEl.classList.add('show');clearTimeout(tTo);
    tTo=setTimeout(function(){tEl.classList.remove('show');},2600);
  }
  function pick(b){
    var sibs=b.parentNode.children;
    for(var i=0;i<sibs.length;i++)sibs[i].classList.remove('on');
    b.classList.add('on');toast('Filtre appliqué : '+b.textContent.trim()+' (démo)');
  }
  function tab(btn,pane){
    var bar=btn.parentNode.children;for(var i=0;i<bar.length;i++)bar[i].classList.remove('on');btn.classList.add('on');
    var panes=document.querySelectorAll('.tabpane');for(var j=0;j<panes.length;j++)panes[j].classList.remove('on');
    document.getElementById(pane).classList.add('on');
  }

  function reveal(){
    var rvs=[].slice.call(document.querySelectorAll('.rv'));
    if(RM){rvs.forEach(function(e){e.classList.add('in');});return;}
    rvs.forEach(function(e,i){setTimeout(function(){e.classList.add('in');},70+i*65);});
  }
  function counter(){
    var flaps=[].slice.call(document.querySelectorAll('#flaps .flap span'));
    if(!flaps.length||RM)return;
    flaps.forEach(function(s,i){
      var f=s.textContent;s.textContent='0';s.style.opacity='0';
      setTimeout(function(){s.style.transition='opacity .4s';s.style.opacity='1';
        var seq=[3,7,f],k=0,iv=setInterval(function(){s.textContent=seq[k++];if(k>=seq.length)clearInterval(iv);},110);},400+i*140);
    });
  }
  function dropzones(){
    [].forEach.call(document.querySelectorAll('.dropzone'),function(dz){
      dz.addEventListener('click',function(){toast('Sélecteur de fichier (démo) — glisse ton Excel/CSV ici');});
      dz.addEventListener('dragover',function(e){e.preventDefault();dz.classList.add('drag');});
      dz.addEventListener('dragleave',function(){dz.classList.remove('drag');});
      dz.addEventListener('drop',function(e){e.preventDefault();dz.classList.remove('drag');toast('Fichier reçu (démo) — analyse & mapping…');});
    });
  }

  window.VIGIE={
    rail:function(active){var el=document.getElementById('rail');if(el)el.innerHTML=railHTML(active);},
    init:function(){reveal();counter();dropzones();},
    toast:toast, pick:pick, tab:tab
  };
})();

# -*- coding: utf-8 -*-
"""_nos_resultats.py · sur l'accueil, la zone des avis devient « Nos résultats » (demande de la cliente, 26/11).

Ses mots : « est-ce que c'est possible de mettre des photos au lieu de mettre avis client […] on met un témoignage
de nos patientes, mais tu mets Nos résultats ou Nos patientes, et je t'envoie tous les avant/après que j'avais mis
sur mon Instagram ».

  · la galerie photo (#temoignages) devient « Nos résultats », surtitre « Nos patientes » ;
  · la zone des avis écrits (#avis) est retirée de la page (elle ne portait aucun avis : REVIEWS était vide) ;
  · le bouton flottant « Avis clients » devient « Nos résultats » ;
  · un témoignage peut être une PAIRE avant / après (deux photos) : la carte montre les deux moitiés, la visionneuse
    un comparateur à faire glisser. Une photo seule (déjà assemblée par elle sur Instagram) reste possible (src) ;
  · tant qu'aucune photo n'est posée, la section renvoie vers SON Instagram (jamais un « bientôt »).
Idempotent. Les photos s'ajoutent dans TESTIMONIALS (index.html), fichiers dans assets/images/temoignages/.
"""
import io
import sys
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "index.html"
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

CSS = """<style id="nos-resultats-css">
/* « Nos résultats » : le comparateur avant / après (26/11) */
.ba-carte{position:relative;display:grid;grid-template-columns:1fr 1fr;width:100%;aspect-ratio:4/5;overflow:hidden;background:#111;}
.ba-carte img{width:100%;height:100%;object-fit:cover;display:block;}
.ba-carte i{position:absolute;top:10px;font:600 10.5px/1 'Jost',sans-serif;letter-spacing:.16em;text-transform:uppercase;font-style:normal;
  background:rgba(13,11,8,.82);color:#f3e3b5;padding:6px 8px;border-radius:999px;}
.ba-carte i:first-of-type{left:10px;} .ba-carte i:last-of-type{right:10px;}
.ba-carte::after{content:"";position:absolute;top:0;bottom:0;left:50%;width:2px;background:#c9a84c;}
.ba{position:relative;width:min(88vw,620px);aspect-ratio:4/5;max-height:76vh;overflow:hidden;border-radius:12px;background:#111;--x:50%;touch-action:pan-y;}
.ba img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;}
.ba .ba-avant{clip-path:inset(0 calc(100% - var(--x)) 0 0);}
.ba .ba-trait{position:absolute;top:0;bottom:0;left:var(--x);width:2px;margin-left:-1px;background:#c9a84c;pointer-events:none;}
.ba .ba-trait::after{content:"⟷";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:44px;height:44px;border-radius:50%;
  display:grid;place-items:center;background:#c9a84c;color:#16120a;font:600 18px/1 sans-serif;}
.ba input{position:absolute;inset:0;width:100%;height:100%;opacity:0;cursor:ew-resize;margin:0;}
.ba .ba-l{position:absolute;bottom:12px;font:600 11px/1 'Jost',sans-serif;letter-spacing:.16em;text-transform:uppercase;
  background:rgba(13,11,8,.85);color:#f3e3b5;padding:7px 10px;border-radius:999px;pointer-events:none;}
.ba .ba-l1{left:12px;} .ba .ba-l2{right:12px;}
.testi-insta{display:inline-flex;align-items:center;gap:10px;margin-top:14px;min-height:46px;padding:0 20px;border-radius:999px;
  background:#c9a84c;color:#16120a;text-decoration:none;font:600 14px/1 'Jost',sans-serif;}
.testi-insta:hover{background:#e3cd86;}
</style>"""

INSTA = "https://www.instagram.com/luxuryclub229/"

REMPLACEMENTS = [
    ('<section class="hub-testi" id="temoignages" aria-label="Témoignages clients en photos">',
     '<section class="hub-testi" id="temoignages" aria-label="Nos résultats, en photos">'),
    ('<div class="testi-eyebrow">Résultats vérifiés</div>', '<div class="testi-eyebrow">Nos patientes</div>'),
    ('<h2 class="testi-title">Témoignages clients</h2>', '<h2 class="testi-title">Nos résultats</h2>'),
    ("""<p class="testi-intro">Photos de résultats, captures de discussions, retours visuels —
        partagés par nos clientes avec leur accord. Cliquez sur une image pour l'agrandir.</p>""",
     """<p class="testi-intro">Avant / après et photos de résultats, partagés par nos patientes avec leur accord.
        Touchez une image pour l'agrandir, puis faites glisser pour comparer.</p>"""),
    # la zone des avis écrits quitte la page (elle était vide) ; son code reste, inerte
    ('<section class="hub-reviews" id="avis" aria-label="Avis clients">',
     '<section class="hub-reviews" id="avis" aria-label="Avis clients" style="display:none" aria-hidden="true">'),
    ('<a href="#avis" id="fabAvis" class="fab-avis" aria-label="Laisser un avis ou lire les avis clients">',
     '<a href="#temoignages" id="fabAvis" class="fab-avis" aria-label="Voir nos résultats">'),
    ('<span class="fab-avis-label">Avis clients</span>', '<span class="fab-avis-label">Nos résultats</span>'),
    ("""  var fab=document.getElementById('fabAvis');
  var sec=document.getElementById('avis');""",
     """  var fab=document.getElementById('fabAvis');
  var sec=document.getElementById('temoignages');"""),
    # sans photo : son Instagram, pas un « bientôt »
    ("""    grid.innerHTML='<div class="testi-empty">Les premières photos de témoignages seront publiées très prochainement.<br>'+
      'Envoyez les vôtres à Mme Sabrina via WhatsApp pour les ajouter à cette galerie.</div>';""",
     """    grid.innerHTML='<div class="testi-empty">Les avant / après de nos patientes sont sur notre Instagram.<br>'+
      '<a class="testi-insta" href="%s" target="_blank" rel="noopener">Voir nos résultats sur Instagram</a></div>';""" % INSTA),
    # une paire avant / après : la carte montre les deux moitiés
    ("""      '<img src="'+escapeHTML(t.src)+'" alt="'+escapeHTML(t.caption||badge)+'" loading="lazy">'+""",
     """      (t.avant&&t.apres
        ?'<span class="ba-carte"><img src="'+escapeHTML(t.avant)+'" alt="Avant" loading="lazy"><img src="'+escapeHTML(t.apres)+'" alt="Après" loading="lazy"><i>Avant</i><i>Après</i></span>'
        :'<img src="'+escapeHTML(t.src)+'" alt="'+escapeHTML(t.caption||badge)+'" loading="lazy">')+"""),
    # la visionneuse : un comparateur à faire glisser pour une paire
    ("""  var t=list[testiState.current];
  $('testiLbImg').src=t.src;
  $('testiLbImg').alt=t.caption||'';""",
     """  var t=list[testiState.current];
  var img=$('testiLbImg'),ba=document.getElementById('testiBa');
  if(t.avant&&t.apres){
    if(!ba){
      ba=document.createElement('div');ba.className='ba';ba.id='testiBa';
      ba.innerHTML='<img class="ba-apres" alt="Après"><img class="ba-avant" alt="Avant"><span class="ba-trait"></span>'+
        '<span class="ba-l ba-l1">Avant</span><span class="ba-l ba-l2">Après</span>'+
        '<input type="range" min="0" max="100" value="50" aria-label="Faire glisser pour comparer avant et après">';
      img.parentNode.insertBefore(ba,img);
      ba.querySelector('input').addEventListener('input',function(e){ba.style.setProperty('--x',e.target.value+'%');});
    }
    ba.querySelector('.ba-avant').src=t.avant;ba.querySelector('.ba-apres').src=t.apres;
    ba.querySelector('input').value=50;ba.style.setProperty('--x','50%');
    ba.style.display='';img.style.display='none';
  }else{
    if(ba)ba.style.display='none';
    img.style.display='';
    img.src=t.src;
    img.alt=t.caption||'';
  }"""),
]


def main():
    s = P.read_text(encoding="utf-8")
    faits = 0
    for a, b in REMPLACEMENTS:
        if a in s:
            s = s.replace(a, b, 1)
            faits += 1
        elif b not in s:
            raise SystemExit("introuvable ni déjà fait : " + a[:80])
    if 'id="nos-resultats-css"' not in s:
        s = s.replace("</head>", CSS + "\n</head>", 1)
        faits += 1
    P.write_text(s, encoding="utf-8")
    print(f"index.html : {faits} changement(s) · « Nos résultats » en place")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""_musique_poser.py · l'ambiance sonore des quatre pages : UNE par niveau (27/11).

Mongazi, 27/11 : « enlève cette musique générique IA pour un son relaxant, le son artificiel basique est toujours
présent », puis « 4 sons ultra relaxants, un pour chaque niveau, qui se déclenchent comme sur la vitrine de NEBULA ».
La piste « Spa » du 26/11 (une nappe de synthèse) est retirée. Chaque niveau a désormais son ENREGISTREMENT réel
(Pixabay, licence Pixabay Content License), mis en boucle sans couture (la fin se fond dans le début) et à -15 LUFS :
  · l'accueil          ambiance-accueil.mp3    un ruisseau de forêt et ses oiseaux (la bienvenue)
  · la clinique        ambiance-clinique.mp3   des bols de cristal, une fontaine zen en dessous (la lumière)
  · la boutique INA    ambiance-boutique.mp3   une fontaine en bois, des bols himalayens (la chaleur)
  · le cabinet         ambiance-cabinet.mp3    des bols de méditation frappés (la profondeur)
Le déclenchement est celui de la vitrine NEBULA : au PREMIER GESTE, quel qu'il soit (toucher, clic, touche,
défilement), en fondu, et on RÉESSAIE à chaque geste tant que le son ne joue pas (un iPhone refuse un premier toucher
ou un défilement : l'ancien code abandonnait après cet essai raté, et la musique ne venait jamais). Jamais si le
visiteur l'a coupée.
  · l'accueil, la clinique et INA : musicStart / musicStop de la maison jouent la piste (bouton #lcMute) ;
  · le cabinet : `assets/js/salon3d/son.js` lit sa piste (bouton « Son » de la visite).
Idempotent (marqueurs <!--MUS--> … <!--/MUS-->).
"""
import re
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
PISTES = {
    "index.html": "assets/audio/ambiance-accueil.mp3",
    "luxury-skin-clinic.html": "assets/audio/ambiance-clinique.mp3",
    "ina-luxury.html": "assets/audio/ambiance-boutique.mp3",
    "harmonisation-faciale.html": "assets/audio/ambiance-cabinet.mp3",
}

LECTEUR = """<!--MUS-->
<audio id="lcMusiqueFichier" src="%s" preload="none" loop></audio>
<script>
/* L'AMBIANCE DE CE NIVEAU (27/11) : un vrai enregistrement, en boucle ; musicStart / musicStop de la maison l'appellent.
   Elle part au premier geste comme sur la vitrine NEBULA, et on réessaie à chaque geste tant qu'elle ne joue pas. */
window.LCMusique=(function(){
  var a=document.getElementById('lcMusiqueFichier');if(!a)return null;
  var V=matchMedia('(max-width:760px)').matches?.7:.6,f=0,voulu=false,coupee=false;
  var EV=['pointerdown','touchend','click','keydown','scroll','touchstart','wheel'];
  function fondu(vers,ms,fin){cancelAnimationFrame(f);var de=a.volume,t0=performance.now();
    (function pas(t){var k=Math.min(1,Math.max(0,(t-t0)/ms));a.volume=Math.min(1,Math.max(0,de+(vers-de)*k));if(k<1)f=requestAnimationFrame(pas);else if(fin)fin();})(t0);}
  function retirer(){EV.forEach(function(e){removeEventListener(e,essai,true);});}
  function jouer(){voulu=true;coupee=false;if(a.preload==='none')a.preload='auto';if(!a.paused){retirer();return;}
    a.volume=0;var p=a.play();
    if(p&&p.then)p.then(function(){retirer();fondu(V,1800);}).catch(function(){});else{retirer();fondu(V,1800);}}
  function couper(){voulu=false;coupee=true;fondu(0,600,function(){a.pause();});}
  function essai(){if(coupee)return;jouer();}
  EV.forEach(function(e){addEventListener(e,essai,{capture:true,passive:true});});
  document.addEventListener('visibilitychange',function(){if(document.hidden)a.pause();else if(voulu){var p=a.play();if(p&&p.catch)p.catch(function(){});}});
  return{jouer:jouer,couper:couper};
})();
</script>
<!--/MUS-->
"""


def main():
    for nom in ("index.html", "luxury-skin-clinic.html", "ina-luxury.html"):
        p = ICI / nom
        s = p.read_text(encoding="utf-8")
        a = "  if(musicOn)return;musicOn=true;\n"
        b = a + "  if(window.LCMusique){window.LCMusique.jouer();return;}   /* la piste de spa (26/11) */\n"
        if b not in s:
            if a not in s:
                raise SystemExit(nom + " : musicStart introuvable")
            s = s.replace(a, b, 1)
        a = "  musicOn=false;clearTimeout(musicTimer);\n"
        b = a + "  if(window.LCMusique){window.LCMusique.couper();return;}\n"
        if b not in s:
            if a not in s:
                raise SystemExit(nom + " : musicStop introuvable")
            s = s.replace(a, b, 1)
        lecteur = LECTEUR % PISTES[nom]
        if "<!--MUS-->" in s:
            s = re.sub(r"<!--MUS-->.*?<!--/MUS-->\n?", lambda m: lecteur, s, count=1, flags=re.S)
        else:
            i = s.rindex("</body>")
            s = s[:i] + lecteur + s[i:]
        p.write_text(s, encoding="utf-8")
        print(f"{nom} : {PISTES[nom]}")
    p = ICI / "harmonisation-faciale.html"
    s = p.read_text(encoding="utf-8")
    s2 = re.sub(r'(<audio id="s3dMusique" src=")[^"]+(")', r"\g<1>" + PISTES[p.name] + r"\g<2>", s)
    if PISTES[p.name] not in s2:
        raise SystemExit("harmonisation : lecteur introuvable")
    p.write_text(s2, encoding="utf-8")
    print(f"{p.name} : {PISTES[p.name]}")
    for vieux in ("luxury-spa.mp3", "luxury-ambiance.mp3"):
        f = ICI / "assets" / "audio" / vieux
        if f.exists():
            f.unlink()
            print(f"assets/audio/{vieux} : retiré (plus aucune page ne le lit)")


if __name__ == "__main__":
    main()

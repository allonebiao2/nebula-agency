# -*- coding: utf-8 -*-
"""_musique_poser.py · la musique de spa sur les quatre pages (Mongazi, 26/11 : « un son apaisant, relaxant, qui donne
l'impression d'être dans un spa », choisie sur Pixabay).

La piste : « Spa » de leberch (Pixabay, licence Pixabay Content License, piste « Content ID Registered » : sans effet
sur un site web, mais une vidéo du site publiée sur YouTube ou Facebook pourrait être réclamée).
Fichier : assets/audio/luxury-spa.mp3 (4:56, -12,3 LUFS, 96 kb/s, fondus d'entrée et de sortie pour la boucle).

  · l'accueil, la clinique et INA avaient une ambiance SYNTHÉTISÉE (LCAudio, bouton #lcMute de la barre du bas) :
    ses fonctions musicStart / musicStop jouent désormais la piste, en fondu, au volume de la maison (0,66 au
    téléphone, 0,57 au PC). Le même bouton la commande ; jamais deux musiques à la fois ;
  · l'harmonisation jouait déjà un fichier (son.js) : la piste remplace l'ancienne.
Idempotent (marqueurs <!--MUS--> … <!--/MUS-->).
"""
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
PISTE = "assets/audio/luxury-spa.mp3"

LECTEUR = """<!--MUS-->
<audio id="lcMusiqueFichier" src="%s" preload="none" loop></audio>
<script>
/* LA MUSIQUE DE SPA (26/11) : la piste remplace l'ambiance synthétisée ; musicStart / musicStop de la maison l'appellent */
window.LCMusique=(function(){
  var a=document.getElementById('lcMusiqueFichier');if(!a)return null;
  var V=matchMedia('(max-width:760px)').matches?.66:.57,f=0,voulu=false;
  function fondu(vers,ms,fin){cancelAnimationFrame(f);var de=a.volume,t0=performance.now();
    (function pas(t){var k=Math.min(1,Math.max(0,(t-t0)/ms));a.volume=de+(vers-de)*k;if(k<1)f=requestAnimationFrame(pas);else if(fin)fin();})(t0);}
  document.addEventListener('visibilitychange',function(){if(document.hidden)a.pause();else if(voulu){var p=a.play();if(p&&p.catch)p.catch(function(){});}});
  return{jouer:function(){voulu=true;if(a.preload==='none')a.preload='auto';a.volume=0;var p=a.play();
           if(p&&p.then)p.then(function(){fondu(V,1800);}).catch(function(){});},
         couper:function(){voulu=false;fondu(0,600,function(){a.pause();});}};
})();
</script>
<!--/MUS-->
""" % PISTE


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
        if "<!--MUS-->" in s:
            s = re.sub(r"<!--MUS-->.*?<!--/MUS-->\n?", lambda m: LECTEUR, s, count=1, flags=re.S)
        else:
            i = s.rindex("</body>")
            s = s[:i] + LECTEUR + s[i:]
        p.write_text(s, encoding="utf-8")
        print(f"{nom} : la piste de spa remplace l'ambiance synthétisée")
    p = ICI / "harmonisation-faciale.html"
    s = p.read_text(encoding="utf-8")
    s = s.replace('src="assets/audio/luxury-ambiance.mp3"', 'src="%s"' % PISTE)
    if PISTE not in s:
        raise SystemExit("harmonisation : lecteur introuvable")
    p.write_text(s, encoding="utf-8")
    print("harmonisation-faciale.html : la piste de spa remplace l'ancienne")
    ancien = ICI / "assets" / "audio" / "luxury-ambiance.mp3"
    if ancien.exists():
        ancien.unlink()
        print("assets/audio/luxury-ambiance.mp3 : retiré (plus aucune page ne le lit)")


if __name__ == "__main__":
    main()

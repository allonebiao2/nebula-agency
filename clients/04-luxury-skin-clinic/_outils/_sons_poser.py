# -*- coding: utf-8 -*-
"""_sons_poser.py · les bruitages RÉELS sur les quatre pages (27/11, Mongazi : « enlève ce bruitage générique bizarre,
remplace par des bruitages réels sur Pixabay, adaptés à la vitrine »).

  · pose `assets/js/sons.js` (le lecteur commun, `LCSons.jouer`) dans les quatre pages ;
  · remplace les bips synthétisés de la maison (`var SFX={...}` de l'accueil, de la clinique et d'INA : la sirène du
    menu, le bip carré des filtres, l'accord électronique du panier) par les vrais sons ;
  · les sons de la visite 3D passent par le même lecteur (`assets/js/salon3d/son.js`, édité à la main).
Les fichiers : `assets/audio/sfx/*.mp3`, tirés de Pixabay, coupés, fondus et mis au même volume (voir sons.js).
Idempotent : marqueurs <!--SONS--> et /*SONS-REELS*/.
    python _outils/_sons_poser.py [--version 20261127a]
"""
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
V = sys.argv[sys.argv.index("--version") + 1] if "--version" in sys.argv else "20261127b"
PAGES = ["index.html", "luxury-skin-clinic.html", "ina-luxury.html", "harmonisation-faciale.html"]
BALISE = f'<!--SONS--><script src="assets/js/sons.js?v={V}" defer></script><!--/SONS-->'
SFX = """var SFX={ /*SONS-REELS*/ /* 27/11 : de vrais enregistrements (assets/js/sons.js), plus des bips synthétisés */
  brandClick:function(){S('cloche');},
  hover:function(){S('tinte',.8);},
  addCart:function(){S('verre');setTimeout(function(){S('cloche',.6);},140);},
  menuOpen:function(){S('tissu');},
  menuClose:function(){S('tissu',.7);},
  filter:function(){S('verre',.6);},
  whatsapp:function(){S('verre');},
  chordOk:function(){S('cloche');},
  tap:function(){S('goutte',.7);}
};
function S(n,v){if(window.LCSons)window.LCSons.jouer(n,{vol:v});}
"""


def main():
    for nom in PAGES:
        p = ICI / nom
        s = p.read_text(encoding="utf-8")
        s = re.sub(r"<!--SONS-->.*?<!--/SONS-->", "", s, flags=re.S)
        s = s.replace("</head>", BALISE + "\n</head>", 1)
        if "var SFX={" in s:
            i = s.index("var SFX={")
            j = s.index("function play(n)", i)
            s = s[:i] + SFX + s[j:]
        p.write_text(s, encoding="utf-8")
        print(f"  {nom:28} lecteur posé{', bips remplacés' if '/*SONS-REELS*/' in s else ''}")


if __name__ == "__main__":
    main()

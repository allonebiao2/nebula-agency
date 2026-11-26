# -*- coding: utf-8 -*-
"""_salon3d_poser.py · pose la visite 3D dans la clinique et dans INA Luxury (26/11).

Idempotent : chaque morceau est entre des marqueurs <!--S3D-…--> et se REMPLACE au lieu de s'ajouter.
Ce qu'il pose, par page :
  · la feuille de style du salon et la police DM Mono (les petites étiquettes) ;
  · la section 3D (la porte en HTML pour la clinique ; INA a déjà son écran d'accueil) ;
  · la musique (<audio> nue, chargée sans jouer) et la PASSERELLE vers les moteurs de la page
    (startBooking chez la clinique, select chez INA) : la scène appelle ce qui existe, elle ne le refait pas ;
  · le module de démarrage.
Usage : python _outils/_salon3d_poser.py [--version 20261126b]
"""
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
V = "20261126a"
if "--version" in sys.argv:
    V = sys.argv[sys.argv.index("--version") + 1]

POLICE_DM = "&family=DM+Mono:wght@400;500"

SCENE = """    <div class="s3d-scene">
      <canvas aria-hidden="true"></canvas>
      <div class="s3d-points"></div>
      <div class="s3d-calques"></div>
      <nav class="s3d-pastilles" aria-label="{nav}"></nav>
      <button class="s3d-son" type="button">Son : oui</button>
      <div class="s3d-jauge" aria-hidden="true"><i></i></div>
      <div class="s3d-indice" aria-hidden="true">Faites défiler</div>{porte}
    </div>"""

PAGES = {
    "luxury-skin-clinic.html": {
        "ancre": "<main>\n", "apres": True,
        "section": '<section class="s3d sc" id="visite" aria-label="La visite de la clinique, en 3D">\n' + SCENE.format(
            nav="Les étapes de la visite",
            porte="""
      <div class="s3d-porte" role="button" tabindex="0" aria-label="Entrer dans la clinique">
        <div class="battant g"><span class="poignee"></span></div>
        <div class="battant d"><span class="poignee"></span></div>
        <div class="enseigne">
          <div class="ls" aria-hidden="true">LS</div>
          <div class="titre">L'institut où la peau <em>retrouve sa lumière</em></div>
          <p>Luxury Skin Clinic · Cotonou · Sur rendez-vous</p>
          <span class="pousser">Poussez la porte</span>
        </div>
      </div>""") + "\n</section>\n",
        "pont": """<script>
/* LA PASSERELLE de la visite 3D : la scène appelle les moteurs de cette page, elle ne les refait pas. */
window.LC_CLINIC={services:SERVICES,book:function(i){startBooking(SERVICES[i]);}};
</script>""",
        "boot": "boot-clinique.js",
    },
    "ina-luxury.html": {
        "ancre": '<div class="layout">', "apres": False,
        "section": '<section class="s3d ina" id="boutique" aria-label="La boutique INA Luxury, en 3D">\n' + SCENE.format(
            nav="Les vitrines de la boutique", porte="") + "\n</section>\n",
        "pont": """<script>
/* LA PASSERELLE de la vitrine 3D : les produits, les photos et les familles sont LUS ici, jamais recopiés. */
window.LC_INA={produits:PRODUCTS,img:IMG,familles:FAMILIES,sous:SUBCATS,
  ouvrir:function(f,s){select(f,s||null,null);var m=document.querySelector('.layout');if(m){if(window.LCGlisser)window.LCGlisser(m,'start');else m.scrollIntoView();}}};
/* une famille ouverte par l'adresse (ina-luxury.html#intime-bien-etre : les anciens liens de Cozy y arrivent) */
(function(){var k=decodeURIComponent((location.hash||'').slice(1));if(k&&FAMILIES.some(function(f){return f.key===k;})){select(k,null,null);setTimeout(function(){var m=document.querySelector('.layout');if(m)m.scrollIntoView();},400);}})();
</script>""",
        "boot": "boot-ina.js",
    },
}


def remplacer(s, nom, bloc, ancre, apres):
    deb, fin = f"<!--S3D-{nom}-->", f"<!--/S3D-{nom}-->"
    morceau = f"{deb}\n{bloc}\n{fin}\n"
    if deb in s:
        return re.sub(re.escape(deb) + r".*?" + re.escape(fin) + r"\n?", lambda m: morceau, s, count=1, flags=re.S)
    if ancre not in s:
        raise SystemExit(f"ancre introuvable pour {nom} : {ancre!r}")
    i = s.index(ancre)
    return s[:i + len(ancre)] + morceau + s[i + len(ancre):] if apres else s[:i] + morceau + s[i:]


def main():
    for page, cfg in PAGES.items():
        p = ICI / page
        s = p.read_text(encoding="utf-8")
        # la police des étiquettes
        s = re.sub(r'(<link href="https://fonts\.googleapis\.com/css2\?[^"]*?)(&display=swap")',
                   lambda m: m.group(1) + ("" if "DM+Mono" in m.group(1) else POLICE_DM) + m.group(2), s, count=1)
        s = remplacer(s, "CSS", f'<link rel="stylesheet" href="assets/js/salon3d/salon3d.css?v={V}">', "</head>", False)
        s = remplacer(s, "SECTION", cfg["section"].rstrip("\n"), cfg["ancre"], cfg["apres"])
        # pas de <audio> ici : la page a déjà son ambiance musicale (Web Audio, bouton #lcMute dans la barre du bas)
        fin = f'{cfg["pont"]}\n<script type="module" src="assets/js/salon3d/{cfg["boot"]}?v={V}"></script>'
        s = remplacer(s, "FIN", fin, "</body>", False)
        p.write_text(s, encoding="utf-8")
        print(f"{page} : visite posée (v={V})")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""_invite_poser.py · pose l'hôtesse qui vient saluer (assets/js/invite.js) sur les trois univers (26/11).
Le portrait est DESSINÉ (_outils/avatar.mjs, le dessinateur commun des aperçus), rendu ici en SVG par Node.
Idempotent (marqueurs <!--IV--> … <!--/IV-->). Bumper --version à chaque modification d'invite.js.
    python _outils/_invite_poser.py [--version 20261126q]
"""
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ICI = Path(__file__).resolve().parent.parent
V = sys.argv[sys.argv.index("--version") + 1] if "--version" in sys.argv else "20261126q"
WA = "https://wa.me/2290167975626?text="

# l'hôtesse de la maison : une seule pour les trois univers (peau ouest-africaine, tunique menthe, foulard d'or)
HOTESSE = {"peau": "#7a4b2e", "ombre": "#5e3720", "tenue": "#7fae9d", "col": "#f6f2e8", "fond": ["#f6eddc", "#d8b878"],
           "coiffe": "foulard", "tissu": "#c9a84c", "nom": "L'hôtesse de Luxury Club 229"}

PAGES = {
    "luxury-skin-clinic.html": {
        "nom": "Votre hôtesse", "theme": "clair", "bas": 68,
        "texte": "Bonjour 👋 Bienvenue chez Luxury Skin Clinic. Un soin du visage, du corps ou des cheveux ? Je vous mets en relation avec Mme Sabrina pour choisir le bon.",
        "oui": "Oui, conseillez-moi", "non": "Je regarde d'abord",
        "action": {"type": "lien", "url": WA + quote("Bonjour, je visite le site de Luxury Skin Clinic et j'aimerais un conseil pour choisir mon soin.")},
    },
    "ina-luxury.html": {
        "nom": "Votre hôtesse", "theme": "sombre", "bas": 68,
        "texte": "Bonjour 👋 Vous hésitez entre plusieurs produits ? Mme Sabrina peut vous orienter vers la routine qui convient à votre peau.",
        "oui": "Faire ma consultation", "non": "Je regarde d'abord",
        "action": {"type": "clic", "sel": "#consultBtn"},
    },
    "harmonisation-faciale.html": {
        "nom": "Votre hôtesse", "theme": "sombre", "bas": 0,
        "texte": "Bonjour 👋 Une zone du visage vous intéresse ? Je prépare votre demande de consultation, Mme Sabrina vous répond sur WhatsApp.",
        "oui": "Demander ma consultation", "non": "Je regarde d'abord",
        "action": {"type": "harmo"},
    },
}


def portrait():
    code = ("import {avatar} from './avatar.mjs';process.stdout.write(avatar(%s));" % json.dumps(HOTESSE, ensure_ascii=False))
    r = subprocess.run(["node", "--input-type=module", "-e", code], cwd=str(Path(__file__).resolve().parent),
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise SystemExit("node : " + r.stderr[:300])
    # l'identifiant du dégradé est tiré au hasard : on le fige, pour un fichier qui ne change pas à chaque passage
    svg = re.sub(r"\bav[a-z0-9]{5}f\b", "avlcf", r.stdout)
    return re.sub(r"\s*\n\s*", " ", svg)


def main():
    svg = portrait()
    for page, cfg in PAGES.items():
        p = ICI / page
        s = p.read_text(encoding="utf-8")
        c = dict(cfg, avatar=svg)
        js = json.dumps(c, ensure_ascii=False).replace("</", "<\\/")
        bloc = (f'<!--IV-->\n<script type="application/json" id="invite-cfg">{js}</script>\n'
                f'<script src="assets/js/invite.js?v={V}" defer></script>\n<!--/IV-->\n')
        if "<!--IV-->" in s:
            s = re.sub(r"<!--IV-->.*?<!--/IV-->\n?", lambda m: bloc, s, count=1, flags=re.S)
        else:
            i = s.rindex("</body>")
            s = s[:i] + bloc + s[i:]
        p.write_text(s, encoding="utf-8")
        print(f"{page} : hôtesse posée (v={V})")


if __name__ == "__main__":
    main()

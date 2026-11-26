# -*- coding: utf-8 -*-
"""_menu_poser.py · pose le Menu (assets/js/menu.js) sur les quatre pages, avec les raccourcis de chacune (26/11).
Idempotent (marqueurs <!--LM--> … <!--/LM-->). Bumper --version à chaque modification de menu.js.
    python _outils/_menu_poser.py [--version 20261126m]
"""
import json
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
V = sys.argv[sys.argv.index("--version") + 1] if "--version" in sys.argv else "20261126m"

PAGES = {
    "index.html": {"hub": True, "raccourcis": [
        {"t": "Nos univers", "h": "#brands"}, {"t": "Mme Sabrina", "h": "#bio"}, {"t": "Nos résultats", "h": "#temoignages"}]},
    "luxury-skin-clinic.html": {"soins": True, "raccourcis": [
        {"t": "Tous les soins et leurs tarifs", "h": "#soins"}, {"t": "Réserver un rendez-vous", "h": "#rdv-booking"},
        {"t": "Questions fréquentes", "h": "#questions"}]},
    "ina-luxury.html": {"familles": True, "raccourcis": [
        {"t": "Tous les produits", "h": ".layout"}, {"t": "Mon panier", "clic": "#cartBtn"},
        {"t": "Faire ma consultation", "clic": "#consultBtn"}]},
    "harmonisation-faciale.html": {"techniques": True, "raccourcis": [
        {"t": "Toutes les techniques et leurs tarifs", "h": "#techniques"},
        {"t": "Demander ma consultation", "clic": ".consult [data-consult]"}]},
}


def main():
    for page, cfg in PAGES.items():
        p = ICI / page
        s = p.read_text(encoding="utf-8")
        bloc = ("<!--LM-->\n<script>window.LC_MENU=%s;</script>\n<script src=\"assets/js/menu.js?v=%s\"></script>\n<!--/LM-->\n"
                % (json.dumps(cfg, ensure_ascii=False), V))
        if "<!--LM-->" in s:
            s = re.sub(r"<!--LM-->.*?<!--/LM-->\n?", lambda m: bloc, s, count=1, flags=re.S)
        else:
            i = s.rindex("</body>")
            s = s[:i] + bloc + s[i:]
        p.write_text(s, encoding="utf-8")
        print(f"{page} : menu posé (v={V})")


if __name__ == "__main__":
    main()

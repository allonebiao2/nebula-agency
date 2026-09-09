# -*- coding: utf-8 -*-
"""Photographie la lettre, fermee puis ouverte, en 390 et en 1440.

Le standard maison dit qu'une vitrine n'est pas finie quand elle marche, mais
quand elle impressionne, et qu'on REGARDE les captures avant de dire fini.
Ce script ne juge rien : il fabrique ce qu'il faut regarder.
"""
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from playwright.sync_api import sync_playwright

ICI = pathlib.Path(__file__).resolve().parent
OUT = ICI / "_vues"
LETTRE = ICI / "lettre.html"

# Un exemple qui ressemble a une vraie commande, code compris.
EXEMPLE = {
    "occasion": "Anniversaire",
    "pour": "Zara",
    "de": "Robert",
    "titre": "Joyeux anniversaire",
    "code": "",
    "lettre": [
        "Je ne sais pas ecrire les belles phrases, alors je vais ecrire les vraies.",
        "Depuis que tu es la, les journees ordinaires ont cesse d'etre ordinaires.",
        "Bon anniversaire. Je nous souhaite encore beaucoup de jours comme ceux-la.",
    ],
    "photos": [],
    "depuis": "2024-03-14",
    "pied": True,
    "lien": "https://lepli.nebula-agency.online",
}


# On passe par _injecter : ecrire des donnees dans le gabarit se fait a UN
# seul endroit, sinon la protection contre « </script> » se perd en chemin.
from _injecter import poser


def main():
    OUT.mkdir(exist_ok=True)
    essai = OUT / "_essai.html"
    essai.write_text(poser(EXEMPLE), encoding="utf-8")

    # La meme lettre, mais programmee : le verrou d'heure est ce que voit
    # d'abord celle qui la recoit avant l'heure.
    import datetime
    quand = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=12)
    verrou = OUT / "_essai_verrou.html"
    verrou.write_text(poser(dict(EXEMPLE, ouvre=quand.strftime("%Y-%m-%dT%H:%M"))),
                      encoding="utf-8")

    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        for nom, larg, haut in (("390", 390, 844), ("1440", 1440, 900)):
            pg = nav.new_page(viewport={"width": larg, "height": haut},
                              device_scale_factor=2)
            pg.goto(essai.as_uri())
            pg.wait_for_timeout(900)
            pg.screenshot(path=str(OUT / ("seuil-%s.png" % nom)))

            # Le seuil VERROUILLE : c'est le premier ecran d'une lettre
            # programmee, donc le plus vu du produit. Il se regarde.
            pg.goto(verrou.as_uri())
            pg.wait_for_timeout(900)
            pg.screenshot(path=str(OUT / ("verrou-%s.png" % nom)))
            pg.goto(essai.as_uri())
            pg.wait_for_timeout(700)

            pg.click("#btn-ouvrir")
            # L'ouverture dure ~620 ms, puis les lignes s'ecrivent une a une.
            pg.wait_for_timeout(3800)
            pg.screenshot(path=str(OUT / ("lettre-%s.png" % nom)),
                          full_page=True)
            pg.close()
        nav.close()

    for f in sorted(OUT.glob("*.png")):
        print("  %-18s %6d Ko" % (f.name, f.stat().st_size // 1024))
    print("\n  a REGARDER :", OUT)


if __name__ == "__main__":
    sys.exit(main())

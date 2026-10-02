"""Les vraies réalisations NEBULA, photographiées en ligne pour la vidéo de marque.

Trois images par site, dans public/nebula30/sites/ :

    <site>-tel.jpg        le premier écran sur téléphone (390 x 844, x3)
    <site>-tel-long.jpg   la page sur téléphone, assez haute pour défiler dans l'écran
    <site>-pc.jpg         le premier écran sur ordinateur (1440 x 900)

⚠️ Deux pièges déjà connus du dépôt :
- un navigateur sans interface se présente « HeadlessChrome » et Cloudflare répond
  403 sur *.pages.dev : on se présente comme un Chrome ordinaire ;
- les sections se révèlent au défilement : on demande « mouvement réduit », que ces
  sites respectent, et on fait défiler la page une fois avant de photographier.

    python _outils/nebula30_captures.py            tous les sites
    python _outils/nebula30_captures.py angy-art   un seul
"""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ICI = Path(__file__).resolve().parent.parent
DOSSIER = ICI / "public/nebula30/sites"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
UA_TEL = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36")

# Dans l'ordre demandé par Mongazi : ces quatre-là d'abord.
SITES = [
    ("angy-art", "https://angyart.online/"),
    ("braise-dor", "https://au-braise-dor.pages.dev/"),
    ("hillary", "https://hillary-m-styl.pages.dev/"),
    ("weinkeller", "https://speed-weinkeller.pages.dev/weinkeller"),
    ("djambar", "https://djambarteam.com/"),
    ("luxury-club", "https://luxuryclub229.com/"),
    ("grain", "https://graindesthetique.com/"),
    ("miss-cakes", "https://miss-cakes.pages.dev/"),
    ("hh-design", "https://hh-design.pages.dev/"),
]
HAUTEUR_LONGUE = 2600  # en pixels CSS : trois écrans de téléphone, de quoi défiler

# Ce qui se pose PAR-DESSUS l'accueil à chaque visite, et qu'une photo de vitrine
# ne doit pas montrer. Weinkeller ouvre sa fenêtre « Offrir un cadeau » et une
# bulle « Cliquez ici pour voir toutes nos boissons ».
A_MASQUER = {
    "weinkeller": "#giftBubble, .cl-hint { display: none !important; }",
}


def ranger(page, nom):
    if nom in A_MASQUER:
        page.add_style_tag(content=A_MASQUER[nom])
        time.sleep(0.3)


def parcourir(page):
    """Fait défiler toute la page (révélations, images paresseuses), puis remonte."""
    hauteur = page.evaluate("document.documentElement.scrollHeight")
    for y in range(0, min(hauteur, 9000), 500):
        page.evaluate(f"window.scrollTo(0, {y})")
        time.sleep(0.12)
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(1.2)


def photographier(navigateur, nom, url):
    tel = navigateur.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3,
                                 is_mobile=True, has_touch=True, user_agent=UA_TEL,
                                 reduced_motion="reduce", locale="fr-FR")
    page = tel.new_page()
    reponse = page.goto(url, wait_until="load", timeout=60000)
    print(f"  {nom} : HTTP {reponse.status if reponse else '?'}")
    time.sleep(2.5)
    parcourir(page)
    ranger(page, nom)
    page.screenshot(path=str(DOSSIER / f"{nom}-tel.jpg"), type="jpeg", quality=88)
    page.screenshot(path=str(DOSSIER / f"{nom}-tel-long.jpg"), type="jpeg", quality=82,
                    full_page=True, clip={"x": 0, "y": 0, "width": 390, "height": HAUTEUR_LONGUE})
    tel.close()

    pc = navigateur.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1,
                                user_agent=UA, reduced_motion="reduce", locale="fr-FR")
    page = pc.new_page()
    page.goto(url, wait_until="load", timeout=60000)
    time.sleep(2.5)
    parcourir(page)
    ranger(page, nom)
    page.screenshot(path=str(DOSSIER / f"{nom}-pc.jpg"), type="jpeg", quality=86)
    pc.close()


def main():
    DOSSIER.mkdir(parents=True, exist_ok=True)
    voulus = sys.argv[1:]
    with sync_playwright() as p:
        navigateur = p.chromium.launch()
        for nom, url in SITES:
            if voulus and nom not in voulus:
                continue
            try:
                photographier(navigateur, nom, url)
            except Exception as e:  # un site en panne ne bloque pas les autres
                print(f"  ⛔ {nom} : {e}")
        navigateur.close()
    print("→", DOSSIER)


if __name__ == "__main__":
    main()

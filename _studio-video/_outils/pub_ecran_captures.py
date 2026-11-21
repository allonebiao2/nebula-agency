# -*- coding: utf-8 -*-
"""La preuve de la pub écran NEBULA : le VRAI catalogue d'un client livré, photographié en ligne au téléphone.

    python _outils/pub_ecran_captures.py

Écrit `public/pub-ecran-nebula/braise-tel-long.jpg` : https://aubraisedor.com/ à 390 px de large (x2), assez haut
pour défiler dans le téléphone de la ligne 8 (« ta boutique dans son téléphone »).

⛔ Seulement un client LIVRÉ et payé (Au Braisé d'Or) : jamais l'aperçu non payé d'un prospect.
⚠️ Travail lourd (un Chromium) : à lancer seul, aucun rendu en même temps (8 Go sur ce PC).
⚠️ Un navigateur sans interface se présente « HeadlessChrome » et Cloudflare peut répondre 403 : on se présente
comme un Chrome de téléphone ordinaire. Les sections se révèlent au défilement : on fait défiler toute la page
avant de photographier (même recette que `nebula30_captures.py`).
"""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ICI = Path(__file__).resolve().parent.parent
SORTIE = ICI / "public/pub-ecran-nebula/braise-tel-long.jpg"
URL = "https://aubraisedor.com/"
UA_TEL = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36")
HAUTEUR = 3400          # en pixels CSS : quatre écrans de téléphone


def main():
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        navigateur = p.chromium.launch()
        tel = navigateur.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True,
                                     has_touch=True, user_agent=UA_TEL, locale="fr-FR")
        page = tel.new_page()
        reponse = page.goto(URL, wait_until="load", timeout=90000)
        print(f"{URL} : HTTP {reponse.status if reponse else '?'}")
        time.sleep(3.0)
        hauteur = page.evaluate("document.documentElement.scrollHeight")
        for y in range(0, min(hauteur, HAUTEUR + 1600), 300):
            page.mouse.wheel(0, 300)
            time.sleep(0.18)
        time.sleep(1.0)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2.0)
        page.screenshot(path=str(SORTIE), type="jpeg", quality=86, full_page=True,
                        clip={"x": 0, "y": 0, "width": 390, "height": min(HAUTEUR, hauteur)})
        print(f"page de {hauteur} px CSS → {SORTIE.relative_to(ICI)}")
        tel.close()
        navigateur.close()


if __name__ == "__main__":
    main()

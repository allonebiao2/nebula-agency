"""La vitrine de Grain d'Esthétique, photographiée en ligne pour la pub de 35 s.

Sur téléphone (390 x 844, x3), dans public/grain35/vitrine/ :

    accueil.jpg     le premier écran (le bouton « Prendre rendez-vous »)
    <section>.jpg   chaque section entière : visage, corps, ongles, avances, hommes
                    (le bandeau) et hommessoins (la liste des soins hommes)
                    (les vraies cartes, les vrais prix, les vrais boutons « Réserver »)

Mêmes précautions que _outils/nebula30_captures.py : un Chrome ordinaire (Cloudflare
répond 403 à « HeadlessChrome »), « mouvement réduit » pour que les sections soient
déjà révélées, et un défilement complet avant de photographier.

    python _outils/grain35_captures.py
"""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ICI = Path(__file__).resolve().parent.parent
DOSSIER = ICI / "public/grain35/vitrine"
URL = "https://graindesthetique.com/"
UA_TEL = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36")
SECTIONS = ["visage", "corps", "ongles", "avances", "hommes", "hommessoins"]


def main():
    DOSSIER.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        nav = p.chromium.launch()
        ctx = nav.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3,
                              is_mobile=True, has_touch=True, user_agent=UA_TEL,
                              reduced_motion="reduce", locale="fr-FR")
        page = ctx.new_page()
        rep = page.goto(URL, wait_until="load", timeout=60000)
        print("HTTP", rep.status if rep else "?")
        time.sleep(2.5)
        hauteur = page.evaluate("document.documentElement.scrollHeight")
        for y in range(0, hauteur, 500):
            page.evaluate(f"window.scrollTo(0, {y})")
            time.sleep(0.1)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1.2)
        page.screenshot(path=str(DOSSIER / "accueil.jpg"), type="jpeg", quality=90)
        # Le bouton WhatsApp flottant (.wa-fab) et le bouton musique se posent sur tout :
        # masqués pour les sections (au 1er essai le sélecteur visait « .wa-float », qui
        # n'existe pas, et le bouton s'est imprimé sur la fiche Hyaluropen).
        page.add_style_tag(content="#music-btn, .wa-fab { display: none !important; }")
        for s in SECTIONS:
            el = page.locator(f"#{s}")
            if el.count() == 0:
                print("  ⛔ section absente :", s)
                continue
            el.first.scroll_into_view_if_needed()
            time.sleep(0.6)
            el.first.screenshot(path=str(DOSSIER / f"{s}.jpg"), type="jpeg", quality=88)
            b = el.first.bounding_box()
            print(f"  {s} : {b['width']:.0f} x {b['height']:.0f} px CSS")
        ctx.close()
        nav.close()
    print("→", DOSSIER)


if __name__ == "__main__":
    main()

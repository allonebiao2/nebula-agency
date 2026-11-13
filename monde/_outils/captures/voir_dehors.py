"""Capture l'arrivée DEHORS (avant « Entrer ») au téléphone, puis le rendu cinéma à l'ordinateur."""
import sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

VUES = Path(r"C:\Users\USER\nebula-agency\monde\_vues")
BASE = "http://localhost:8765/lieux/hillary-m-styl/"
erreurs = []
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--enable-unsafe-swiftshader"])
    for nom, vp, url, tactile in [("tel-00-arrivee", {"width": 390, "height": 844}, BASE, True),
                                  ("tel-00-interieur", {"width": 390, "height": 844}, BASE + "?direct=1", True),
                                  ("ordi-00-cinema", {"width": 1440, "height": 900}, BASE + "?direct=1&qualite=haute", False)]:
        ctx = b.new_context(viewport=vp, is_mobile=tactile, has_touch=tactile)
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: erreurs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and erreurs.append(m.text))
        pg.goto(url)
        t0 = time.time()
        while time.time() - t0 < 60:
            if nom == "tel-00-arrivee" and pg.evaluate("!document.querySelector('.ouv-entrer').disabled"): break
            if (nom.startswith("ordi") or nom.endswith("interieur")) and pg.evaluate("document.body.classList.contains('embelli')"): break
            time.sleep(1)
        time.sleep(4)
        pg.screenshot(path=str(VUES / f"{nom}.png"))
        print(nom, "capturé en", round(time.time() - t0), "s")
        ctx.close()
    b.close()
print("erreurs :", erreurs[:6] if erreurs else "aucune")

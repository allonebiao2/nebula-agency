"""Compare le salon avec et sans lumière cuite, au même endroit, ordinateur (haute) et téléphone."""
import os, sys, time
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
V = "C:/Users/USER/nebula-agency/monde/_vues/"
vues = sys.argv[1:] or ["entree"]
heure = os.environ.get("HEURE", "21")   # HEURE=14 pour le jour
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=angle", "--enable-unsafe-swiftshader"])
    for nom, vp, tactile, q in [("ordi", {"width": 1440, "height": 900}, False, "&qualite=haute"), ("tel", {"width": 390, "height": 844}, True, "")]:
        for mode in ["", "&sans-cuisson"]:
            ctx = b.new_context(viewport=vp, is_mobile=tactile, has_touch=tactile); pg = ctx.new_page()
            err = []; pg.on("pageerror", lambda e: err.append(str(e))); pg.on("console", lambda m: m.type == "warning" and "cuite" in m.text and err.append(m.text))
            pg.goto(f"http://localhost:8765/lieux/hillary-m-styl/?direct=1&heure={heure}" + q + mode)
            t0 = time.time()
            while time.time() - t0 < 150:
                try:
                    if pg.evaluate("document.body.classList.contains('embelli')"): break
                except Exception: pass
                time.sleep(1)
            time.sleep(6)
            etat = pg.evaluate("__monde.cuisson")
            for v in vues:
                if v != "entree":
                    pg.evaluate(f"__monde.deplacement.allerA('{v}')"); time.sleep(5)
                suffixe = "avec" if not mode else "sans"
                pg.screenshot(path=V + f"{nom}-cuisson-{v}-{heure}h-{suffixe}.png")
            etat = pg.evaluate("__monde.cuisson"); print(nom, suffixe, "cuisson :", etat, "erreurs :", err or "aucune")
            ctx.close()
    b.close()

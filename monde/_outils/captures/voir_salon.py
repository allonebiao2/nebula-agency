"""Le salon tel qu'un visiteur le voit, de jour ET de nuit, à l'ordinateur (qualité haute) et au téléphone.

Usage : python monde/_outils/captures/voir_salon.py [suffixe] [point ...]
  suffixe : ajouté au nom des captures (ex. « avant », « apres ») ; défaut « vue »
  point   : points de passage (`__monde.plan.points`) où se rendre en plus de l'entrée
→ monde/_vues/{ordi,tel}-salon-<point>-<heure>h-<suffixe>.png
Un seul navigateur, une page à la fois (ce PC a 8 Go). Variables : HEURES="14 21", APPAREILS="ordi tel".
"""
import os, sys, time
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

V = os.path.join(os.path.dirname(__file__), "..", "..", "_vues") + os.sep
suffixe = sys.argv[1] if len(sys.argv) > 1 else "vue"
points = ["entree"] + sys.argv[2:]
heures = os.environ.get("HEURES", "14 21").split()
appareils = os.environ.get("APPAREILS", "ordi tel").split()
CONF = {"ordi": ({"width": 1440, "height": 900}, False, "&qualite=haute"), "tel": ({"width": 390, "height": 844}, True, "")}

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=angle", "--enable-unsafe-swiftshader"])
    for nom in appareils:
        vp, tactile, q = CONF[nom]
        for h in heures:
            ctx = b.new_context(viewport=vp, is_mobile=tactile, has_touch=tactile); pg = ctx.new_page()
            err = []
            pg.on("pageerror", lambda e: err.append(str(e)))
            pg.on("console", lambda m: m.type in ("error", "warning") and err.append(m.text[:160]))
            pg.goto(f"http://localhost:8765/lieux/hillary-m-styl/?direct=1&meteo=clair&heure={h}{q}")
            t0 = time.time()
            while time.time() - t0 < 150:
                try:
                    if pg.evaluate("document.body.classList.contains('cuit') || (document.body.classList.contains('embelli') && performance.now() > 25000)"): break
                except Exception: pass
                time.sleep(1)
            time.sleep(6)
            for p in points:
                if p != "entree":
                    pg.evaluate(f"__monde.deplacement.allerA('{p}')"); time.sleep(5)
                f = V + f"{nom}-salon-{p}-{h}h-{suffixe}.png"
                pg.screenshot(path=f); print("→", os.path.basename(f))
            print(nom, h + "h", "qualité", pg.evaluate("__monde.moteur.qualite.nom"), "· erreurs :", err or "aucune")
            ctx.close()
    b.close()

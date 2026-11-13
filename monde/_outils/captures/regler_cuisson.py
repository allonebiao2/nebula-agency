"""Une seule page (ordinateur, qualité haute, 21 h) : photographie le salon pour plusieurs facteurs de la lumière cuite, et la référence sans cuisson."""
import sys, time
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
import numpy as np
from PIL import Image
V = "C:/Users/USER/nebula-agency/monde/_vues/"
facteurs = [float(x) for x in (sys.argv[1:] or ["0.15", "0.2", "0.3"])]
heure = "21"
def lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def Y(path, z):
    a = np.array(Image.open(path).convert("RGB")).astype(float) / 255
    x1, y1, x2, y2 = z; return float((lin(a[y1:y2, x1:x2]) @ [0.2126, 0.7152, 0.0722]).mean())
zones = {'sol gauche': (100, 780, 400, 880), 'mur gauche haut': (80, 200, 300, 260), 'mur centre-droit': (950, 240, 1010, 280), 'podium flanc': (500, 790, 560, 830)}
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=angle", "--enable-unsafe-swiftshader"])
    ctx = b.new_context(viewport={"width": 1440, "height": 900}); pg = ctx.new_page()
    pg.goto(f"http://localhost:8765/lieux/hillary-m-styl/?direct=1&qualite=haute&heure={heure}")
    t0 = time.time()
    while time.time() - t0 < 150 and not pg.evaluate("document.body.classList.contains('cuit')"): time.sleep(1)
    time.sleep(4)
    pg.evaluate("for (const v of __monde.pnj.liste || []) {}")
    for f in facteurs:
        pg.evaluate(f"__monde.cuisson.facteur = {f}"); time.sleep(1.5)
        chemin = V + f"ordi-regle-{f}.png"; pg.screenshot(path=chemin)
        print(f, {n: round(Y(chemin, z) / max(Y(V + 'ordi-cuisson-entree-sans.png', z), 1e-4), 2) for n, z in zones.items()})
    b.close()

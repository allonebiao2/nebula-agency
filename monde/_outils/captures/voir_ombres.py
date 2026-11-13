"""Les ombres de contact des personnages (REALISME.md R2) : Afi abordée (pieds, de près), puis un plan large.
Ordinateur en qualité haute (le sol y est translucide, au-dessus de son miroir) et téléphone."""
import sys, time
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
V = "C:/Users/USER/nebula-agency/monde/_vues/"
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=angle", "--enable-unsafe-swiftshader"])
    for nom, vp, tactile, q in [("ordi", {"width": 1440, "height": 900}, False, "&qualite=haute"), ("tel", {"width": 390, "height": 844}, True, "")]:
        ctx = b.new_context(viewport=vp, is_mobile=tactile, has_touch=tactile); pg = ctx.new_page()
        err = []; pg.on("pageerror", lambda e: err.append(str(e)))
        pg.goto("http://localhost:8765/lieux/hillary-m-styl/?direct=1&heure=21" + q)
        t0 = time.time()
        while time.time() - t0 < 150:
            try:
                if pg.evaluate("document.body.classList.contains('cuit')"): break
            except Exception: pass
            time.sleep(1)
        time.sleep(3)
        pg.screenshot(path=V + f"{nom}-ombres-large.png")
        pg.evaluate("__monde.toucherPnj('afi')"); time.sleep(7)
        pg.evaluate("__monde.deplacement.tournerVers((() => { const p = __monde.pnj.parId.afi.perso.racine.position; return new (__monde.moteur.THREE.Vector3)(p.x, 0.3, p.z); })())"); time.sleep(2.5)
        pg.screenshot(path=V + f"{nom}-ombres-pieds.png")
        print(nom, "erreurs :", err or "aucune")
        ctx.close()
    b.close()

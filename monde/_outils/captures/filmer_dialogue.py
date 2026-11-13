import sys, time
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
V = "C:/Users/USER/nebula-agency/monde/_vues/"
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=angle", "--enable-unsafe-swiftshader"])
    for nom, vp, tactile, q in [("ordi", {"width": 1440, "height": 900}, False, "&qualite=haute"), ("tel", {"width": 390, "height": 844}, True, "")]:
        ctx = b.new_context(viewport=vp, is_mobile=tactile, has_touch=tactile); pg = ctx.new_page()
        err = []; pg.on("pageerror", lambda e: err.append(str(e)))
        pg.goto("http://localhost:8765/lieux/hillary-m-styl/?direct=1" + q); t0 = time.time()
        while time.time() - t0 < 120:
            try:
                if pg.evaluate("document.body.classList.contains('embelli')"): break
            except Exception: pass
            time.sleep(1)
        time.sleep(2)
        pg.evaluate("__monde.toucherHillary()")
        t1 = time.time()
        while time.time() - t1 < 40 and not pg.evaluate("document.querySelector('.options').classList.contains('ouverte')"): time.sleep(0.5)
        pg.click(".opt-principal"); time.sleep(3.5)
        pg.screenshot(path=V + f"{nom}-scene-hillary.png")
        pg.evaluate("__monde.dialogue.fermer && __monde.dialogue.fermer()"); time.sleep(1)
        # le vrai parcours : toucher Afi (on s'approche à 1,30 m), puis « Parler »
        pg.evaluate("__monde.toucherPnj('afi')")
        t2 = time.time()
        while time.time() - t2 < 40 and not pg.evaluate("(() => { const o = document.querySelector('.options'); return o.classList.contains('ouverte') && /visiteuse|Afi/.test(o.textContent); })()"): time.sleep(0.5)
        print(nom, "options :", pg.evaluate("document.querySelector('.options').textContent.slice(0,80)"))
        pg.evaluate("document.querySelector('.options .opt-principal').click()"); time.sleep(4)
        pg.screenshot(path=V + f"{nom}-scene-afi.png")
        print(nom, "erreurs :", err or "aucune")
        ctx.close()
    b.close()

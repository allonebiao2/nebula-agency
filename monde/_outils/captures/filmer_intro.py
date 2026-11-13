import sys, time
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
V = "C:/Users/USER/nebula-agency/monde/_vues/"
heure = sys.argv[1] if len(sys.argv) > 1 else ""
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=angle", "--enable-unsafe-swiftshader"])
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); pg = ctx.new_page()
    err = []; pg.on("pageerror", lambda e: err.append(str(e)))
    pg.goto("http://localhost:8765/lieux/hillary-m-styl/" + (f"?heure={heure}" if heure else ""))
    t0 = time.time()
    while time.time() - t0 < 90:
        try:
            if pg.evaluate("!!document.querySelector('.ouv-entrer') && !document.querySelector('.ouv-entrer').disabled"): break
        except Exception: pass
        time.sleep(0.3)
    suffixe = f"-{heure}h" if heure else ""
    time.sleep(0.4); pg.screenshot(path=V + f"tel-intro-1{suffixe}.png")
    time.sleep(3.6); pg.screenshot(path=V + f"tel-intro-2{suffixe}.png")
    time.sleep(5.0); pg.screenshot(path=V + f"tel-intro-3{suffixe}.png")
    pg.click(".ouv-entrer"); time.sleep(8); pg.screenshot(path=V + f"tel-intro-4{suffixe}.png")
    print("erreurs :", err or "aucune")
    b.close()

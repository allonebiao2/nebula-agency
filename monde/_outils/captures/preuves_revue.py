"""Preuves pour la revue Impeccable : intérieur, réplique d'ambiance, étiquette près du bord droit."""
import sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")
REV = Path(r"C:\Users\USER\nebula-agency\monde\.impeccable\review")
URL = "http://localhost:8765/lieux/hillary-m-styl/?direct=1"
TOURNER = """(deg) => { const M = __monde, T = M.moteur.THREE, cam = M.moteur.camera.position;
  const k = Object.keys(M.totems)[0], p = new T.Vector3(); M.totems[k].getWorldPosition(p);
  const d = p.clone().sub(cam); d.y = 0; const a = deg * Math.PI / 180;
  const r = new T.Vector3(d.x * Math.cos(a) - d.z * Math.sin(a), 0, d.x * Math.sin(a) + d.z * Math.cos(a));
  M.deplacement.tournerVers(cam.clone().add(r).setY(1.5)); }"""
erreurs = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=angle", "--enable-unsafe-swiftshader"])
    for pref, vp, tactile in [("mobile", {"width": 390, "height": 844}, True), ("desktop", {"width": 1440, "height": 900}, False)]:
        ctx = b.new_context(viewport=vp, is_mobile=tactile, has_touch=tactile); pg = ctx.new_page()
        pg.on("pageerror", lambda e: erreurs.append(str(e)))
        pg.goto(URL); t0 = time.time()
        while time.time() - t0 < 90 and not pg.evaluate("document.body.classList.contains('embelli')"): time.sleep(1)
        time.sleep(3)
        pg.screenshot(path=str(REV / f"{pref}-interieur.png"))
        pg.evaluate("__monde.dialogue.sousTitre('maman', \"Regarde ce wax sur l'étagère. Ta tante avait le même en 1998.\")")
        time.sleep(1.2); pg.screenshot(path=str(REV / f"{pref}-09-ambiance.png"))
        for deg in (-14, -20, -26, -32):
            pg.evaluate(TOURNER, deg); time.sleep(1.6)
            hors = pg.evaluate("[...document.querySelectorAll('.repere.vu.nomme')].filter(e => { const r = e.getBoundingClientRect(); return r.right > innerWidth || r.left < 0; }).length")
            gauche = pg.evaluate("document.querySelectorAll('.repere.vu.nomme.gauche').length")
            print(pref, deg, "degrés : étiquettes hors écran =", hors, "· retournées =", gauche)
            if gauche: break
        pg.screenshot(path=str(REV / f"{pref}-10-bord.png"))
        ctx.close()
    b.close()
print("erreurs :", erreurs[:5] or "aucune")

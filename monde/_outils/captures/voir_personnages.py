"""Les vrais personnages dans le salon, de près : la caméra va se placer à 2,4 m de chacun et le regarde.

    python monde/_outils/captures/voir_personnages.py [suffixe]   → monde/_vues/{ordi,tel}-perso-<id>-<suffixe>.png
Dit aussi quel geste chacun joue, et s'il est habillé (vrai modèle) ou encore en silhouette.
"""
import os, sys, time
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
V = os.path.join(os.path.dirname(__file__), "..", "..", "_vues") + os.sep
suffixe = sys.argv[1] if len(sys.argv) > 1 else "vue"
QUI = ["afi", "senami", "maman"]
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=angle", "--enable-unsafe-swiftshader"])
    for nom, vp, tactile, q in [("ordi", {"width": 1440, "height": 900}, False, ""), ("tel", {"width": 390, "height": 844}, True, "")]:
        ctx = b.new_context(viewport=vp, is_mobile=tactile, has_touch=tactile); pg = ctx.new_page()
        err = []; pg.on("console", lambda m: m.type in ("error", "warning") and "Audio" not in m.text and err.append(m.text[:160]))
        pg.on("pageerror", lambda e: err.append(str(e)[:160]))
        pg.goto("http://localhost:8765/lieux/hillary-m-styl/?direct=1&meteo=clair&heure=14" + q)
        t0 = time.time()
        while time.time() - t0 < 150:
            try:
                if pg.evaluate("document.body.classList.contains('cuit')"): break
            except Exception: pass
            time.sleep(1)
        time.sleep(10)
        for qui in QUI:
            etat = pg.evaluate("""(qui) => { const n = __monde.pnj.parId[qui]; if (!n) return null; const p = n.perso;
              let habille = false; p.racine.traverse(o => { if (o.isSkinnedMesh) habille = true; });
              return { habille, geste: p.animation ? p.animation() : null, x: p.racine.position.x, z: p.racine.position.z }; }""", qui)
            if not etat: continue
            pg.evaluate("""(qui) => { const n = __monde.pnj.parId[qui], c = __monde.moteur.camera;
              /* on la RETIENT au milieu de l'allée (elle s'arrête et regarde le visiteur), et on la filme de face */
              __monde.pnj.retenir(qui); n.perso.racine.position.set(0, 0, 3.3);
              window.__suivi && window.__suivi(); let actif = true; window.__suivi = () => { actif = false; };
              __monde.moteur.chaqueImage(() => { if (!actif) return; c.position.set(0.25, 1.5, 5.5); c.lookAt(0, 1.05, 3.3); }); }""", qui)
            time.sleep(4)
            pg.evaluate("(qui) => __monde.pnj.relacher(qui)", qui)
            f = V + f"{nom}-perso-{qui}-{suffixe}.png"; pg.screenshot(path=f)
            print(nom, qui, etat)
        print(nom, "erreurs :", err or "aucune")
        ctx.close()
    b.close()

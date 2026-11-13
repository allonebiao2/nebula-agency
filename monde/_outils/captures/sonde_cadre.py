import sys, time
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=angle", "--enable-unsafe-swiftshader"])
    ctx = b.new_context(viewport={"width": 1440, "height": 900}); pg = ctx.new_page()
    pg.goto("http://localhost:8765/lieux/hillary-m-styl/?direct=1&qualite=haute"); t0 = time.time()
    while time.time() - t0 < 120:
        try:
            if pg.evaluate("document.body.classList.contains('embelli')"): break
        except Exception: pass
        time.sleep(1)
    time.sleep(2)
    pg.evaluate("""(() => { const D = __monde.deplacement; window.__journal = [];
      const o1 = D.tournerVers; D.tournerVers = (p, c) => { __journal.push(['tournerVers', p && +p.y.toFixed(2), +__monde.moteur.camera.rotation.x.toFixed(2)]); return o1(p, c); };
      const o2 = D.cadrer; D.cadrer = (f, d) => { __journal.push(['cadrer', f && +f.toFixed(1), d && +d.toFixed(2)]); return o2(f, d); }; })()""")
    pg.evaluate("__monde.toucherPnj('afi')")
    t2 = time.time()
    while time.time() - t2 < 40 and not pg.evaluate("(() => { const o = document.querySelector('.options'); return o.classList.contains('ouverte') && /visiteuse|Afi/.test(o.textContent); })()"): time.sleep(0.5)
    pg.evaluate("document.querySelector('.options .opt-principal').click()")
    for i in range(6):
        time.sleep(1)
        print(pg.evaluate("""(() => { const M = __monde, c = M.moteur.camera, n = M.pnj.parId.afi, h = n.perso.positionTete(new M.moteur.THREE.Vector3());
          const r = n.perso.racine.position; return {cam: [c.position.x, c.position.y, c.position.z].map(v => +v.toFixed(2)), pitch: +c.rotation.x.toFixed(3), fov: +c.fov.toFixed(1),
          tete: [h.x, h.y, h.z].map(v => +v.toFixed(2)), pieds: +r.y.toFixed(2), d: +h.distanceTo(c.position).toFixed(2), anim: n.perso.animation && n.perso.animation() }; })()"""))
    print(pg.evaluate("""(() => { const M = __monde, T = M.moteur.THREE, c = M.moteur.camera, n = M.pnj.parId.afi; const out = {};
      n.perso.racine.traverse(o => { if (o.isBone && /(HeadTop_End|Head|Neck|LeftEye|Hips)$/.test(o.name)) { const v = o.getWorldPosition(new T.Vector3()); const y = v.y; v.project(c); out[o.name.replace(/^mixamorig:?/, '')] = [+y.toFixed(2), Math.round((1 - v.y) / 2 * innerHeight)]; } });
      return out; })()"""))
    for l in pg.evaluate("__journal"): print(l)
    pg.screenshot(path="C:/Users/USER/nebula-agency/monde/_vues/sonde-cadre.png")
    ctx.close(); b.close()

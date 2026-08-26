# -*- coding: utf-8 -*-
"""
MESURE LA FLUIDITÉ D'ANGY ART — le site se chronomètre lui-même.

    python _fluidite.py            # le dossier du disque
    python _fluidite.py --live     # le site en ligne

⚠️ POURQUOI LA PAGE MESURE ET PAS LE SCRIPT. Une capture d'écran coûte des
centaines de millisecondes : un instrument qui photographie pour mesurer
ajoute le retard qu'il prétend mesurer (leçon payée deux fois, Angy Art puis
Mon Bénin). Ici on installe un compteur d'images DANS la page, on la fait
défiler, et on relit ses chiffres à la fin.

⚠️ ET ON RALENTIT LE PROCESSEUR. Sur cette machine tout est fluide. Le site
est fait pour des téléphones d'entrée de gamme à Cotonou : c'est là que se
voit la différence entre « ça marche » et « ça glisse ». `--lent` fixe le
facteur (4 = un bon téléphone, 6 = un téléphone d'entrée de gamme).

Ce qui est mesuré, et pourquoi :
  · l'écart entre deux images pendant un défilement continu — c'est ça, la
    fluidité ressentie ; la moyenne ment, on regarde le 95e centile ;
  · les images « perdues » (> 32 ms, soit deux images ratées à 60 Hz) ;
  · les tâches longues (> 50 ms), pendant lesquelles la page ne répond plus ;
  · le temps que prend UNE transition du carrousel, la plus chère de la page.
"""
import argparse
import functools
import http.server
import json
import os
import socketserver
import statistics
import sys
import threading

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
LIVE = "https://angy-art.pages.dev/"

# Le compteur, posé dans la page avant tout le reste.
SONDE = """
window.__f = { t: [], long: [], t0: 0 };
(function () {
  let p = 0;
  function tic(ts) {
    if (p) window.__f.t.push(ts - p);
    p = ts;
    requestAnimationFrame(tic);
  }
  requestAnimationFrame(tic);
  try {
    new PerformanceObserver(function (l) {
      for (const e of l.getEntries()) window.__f.long.push(Math.round(e.duration));
    }).observe({ entryTypes: ['longtask'] });
  } catch (e) {}
})();
"""


class Serveur(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def centile(v, p):
    if not v:
        return 0
    v = sorted(v)
    return v[min(len(v) - 1, int(len(v) * p))]


def mesurer(pg, nom, ralenti):
    """Fait défiler la page de bout en bout, puis relit ses chiffres."""
    pg.evaluate("window.__f.t = []; window.__f.long = [];")
    haut = pg.evaluate("document.documentElement.scrollHeight")
    vue = pg.evaluate("innerHeight")

    # ⚠️ On défile comme un humain : par crans, pas d'un bond. Un `scrollTo`
    #    unique ne réveille ni les révélations, ni le parallaxe, ni le volet.
    pas = max(1, int((haut - vue) / 60))
    for i in range(60):
        pg.mouse.wheel(0, pas)
        pg.wait_for_timeout(60)
    pg.wait_for_timeout(400)

    d = pg.evaluate("window.__f")
    t = [x for x in d["t"] if x < 500]          # on jette les pauses de l'outil
    if not t:
        return None
    perdues = [x for x in t if x > 32]
    return {
        "vue": nom,
        "lent": ralenti,
        "images": len(t),
        "median": round(statistics.median(t), 1),
        "p95": round(centile(t, 0.95), 1),
        "pire": round(max(t), 1),
        "perdues": len(perdues),
        "pc_perdues": round(100.0 * len(perdues) / len(t), 1),
        "taches_longues": len(d["long"]),
        "pire_tache": max(d["long"]) if d["long"] else 0,
    }


def carrousel(pg):
    """Le coût d'UNE transition du carrousel, la plus chère de la page."""
    ok = pg.evaluate("!!document.querySelector('.cars-p')")
    if not ok:
        return None
    pg.evaluate("""() => { const e = document.querySelector('.cars');
        e.scrollIntoView({ block: 'center' }); }""")
    pg.wait_for_timeout(1200)
    pg.evaluate("window.__f.t = []; window.__f.long = [];")
    suiv = pg.query_selector('[data-cars="1"], .cars-s, .cars-n, .cars-b')
    if suiv:
        suiv.click()
    else:
        pg.keyboard.press("ArrowRight")
    pg.wait_for_timeout(1100)
    t = [x for x in pg.evaluate("window.__f.t") if x < 500]
    if not t:
        return None
    return {"images": len(t), "median": round(statistics.median(t), 1),
            "p95": round(centile(t, 0.95), 1), "pire": round(max(t), 1),
            "perdues": len([x for x in t if x > 32])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--lent", type=int, default=6, help="facteur de ralentissement du processeur")
    args = ap.parse_args()

    srv = None
    if args.live:
        url = LIVE
    else:
        h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ICI)
        srv = Serveur(("127.0.0.1", 0), h)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        url = "http://127.0.0.1:%d/" % srv.server_address[1]

    print("  source : %s   processeur ralenti x%d\n" % (url, args.lent))
    lignes = []
    with sync_playwright() as p:
        nav = p.chromium.launch()
        for nom, l, ht in (("bureau 1440", 1440, 900), ("telephone 390", 390, 844)):
            pg = nav.new_page(viewport={"width": l, "height": ht})
            cdp = pg.context.new_cdp_session(pg)
            cdp.send("Emulation.setCPUThrottlingRate", {"rate": args.lent})
            pg.add_init_script(SONDE)
            pg.goto(url, wait_until="networkidle", timeout=120000)
            pg.wait_for_timeout(3600)          # le rideau d'ouverture
            r = mesurer(pg, nom, args.lent)
            if r:
                lignes.append(r)
                print("  [%s] %d images · median %.1f ms · p95 %.1f ms · pire %.1f ms"
                      % (r["vue"], r["images"], r["median"], r["p95"], r["pire"]))
                print("      %d image(s) perdue(s) (>32 ms) = %.1f %% · "
                      "%d tache(s) longue(s), la pire a %d ms"
                      % (r["perdues"], r["pc_perdues"], r["taches_longues"], r["pire_tache"]))
            c = carrousel(pg)
            if c:
                print("      carrousel, une transition : median %.1f ms · p95 %.1f ms · "
                      "pire %.1f ms · %d image(s) perdue(s)"
                      % (c["median"], c["p95"], c["pire"], c["perdues"]))
            print()
            pg.close()
        nav.close()
    if srv:
        srv.shutdown()

    print(json.dumps(lignes, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Photographie la carte de l'attiéké et sa fiche, en 390 et 1440.

    python _outils/_vues_attieke.py

⚠️ UN QC VERT NE DIT PAS QUE C'EST BEAU. Il dit que rien n'est cassé. Les
   six défauts d'Hillary et les quatre du héros de cette maison ont tous été
   trouvés SUR LES CAPTURES, pas dans les chiffres.
"""
import functools, http.server, io, os, socketserver, sys, threading

for _f in (sys.stdout, sys.stderr):
    try: _f.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

from playwright.sync_api import sync_playwright

RACINE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "..", "experience", "out"))
VUES = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_vues"))


def sert():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=RACINE)
    # ⚠️ MULTI-TÂCHE. Un TCPServer simple fait échouer un chargement sur deux
    #    en « Page.goto: Timeout » : ce n'est pas le site, c'est le serveur.
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), h)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def main():
    os.makedirs(VUES, exist_ok=True)
    srv, port = sert()
    with sync_playwright() as p:
        nav = p.chromium.launch()
        for nom, w, h in (("390", 390, 844), ("1440", 1440, 900)):
            pg = nav.new_page(viewport={"width": w, "height": h},
                              device_scale_factor=2, reduced_motion="reduce")
            pg.goto("http://127.0.0.1:%d/" % port, wait_until="networkidle", timeout=60000)
            pg.wait_for_selector("#cat-grillades", state="attached", timeout=60000)
            pg.wait_for_timeout(1500)
            pg.evaluate("""() => { const e = document.getElementById('cat-grillades');
                window.__lenis ? window.__lenis.scrollTo(e, { immediate: true }) : e.scrollIntoView(); }""")
            pg.wait_for_timeout(1800)
            pg.screenshot(path=os.path.join(VUES, "attieke-%s-carte.png" % nom))

            pg.evaluate("""() => document.querySelector('.ct-item[data-plat="Attiéké"]').click()""")
            pg.wait_for_timeout(900)
            pg.screenshot(path=os.path.join(VUES, "attieke-%s-fiche.png" % nom))

            pg.evaluate("""() => document.querySelector('[data-choix] button').click()""")
            pg.wait_for_timeout(500)
            pg.screenshot(path=os.path.join(VUES, "attieke-%s-fiche-choisi.png" % nom))
            print("  %s : 3 vues" % nom)
            pg.close()
        nav.close()
    srv.shutdown()


if __name__ == "__main__":
    main()

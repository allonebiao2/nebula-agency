# -*- coding: utf-8 -*-
"""
PHOTOGRAPHIE LE HÉROS, SAUCE PAR SAUCE — Au Braisé d'Or.

    cd experience && npm run build
    python ../_outils/_vues_heros.py

⚠️ POURQUOI UN SCRIPT ALORS QUE LE QC EST VERT. Un QC vert dit que rien n'est
cassé, il ne dit pas que c'est beau. Depuis que le héros porte quatorze sauces
dont plusieurs en ardoise, la seule façon de savoir ce que voit un client est
de REGARDER les quatorze, en 390 et en 1440.

Les planches sortent dans `_vues/heros/`.
"""
import functools
import http.server
import os
import socketserver
import sys
import threading

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.normpath(os.path.join(ICI, "..", "experience", "out"))
VUES = os.path.normpath(os.path.join(ICI, "..", "_vues", "heros"))


class Serveur(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    if not os.path.isdir(RACINE):
        sys.exit("⛔ %s est absent : `npm run build` dans experience/ d'abord." % RACINE)
    os.makedirs(VUES, exist_ok=True)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=RACINE)
    srv = Serveur(("127.0.0.1", 0), handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    with sync_playwright() as p:
        nav = p.chromium.launch()
        for nom, l, h in [("390", 390, 844), ("1440", 1440, 900)]:
            # ⚠️ `reduced_motion` : sinon la scène avance entre le clic et la
            #    photo, et on prend en photo une autre sauce que celle visée.
            pg = nav.new_page(viewport={"width": l, "height": h},
                              device_scale_factor=2, reduced_motion="reduce")
            pg.goto("http://127.0.0.1:%d/" % port, wait_until="networkidle", timeout=60000)
            pg.wait_for_selector("[data-sauce]", timeout=60000)
            n = pg.evaluate(
                "document.querySelectorAll('.swiper-slide button[aria-label]').length")
            for k in range(n):
                pg.evaluate("""(k) => document
                    .querySelectorAll('.swiper-slide button[aria-label]')[k].click()""", k)
                # laisser les tweens d'entrée du titre et de la carte finir
                pg.wait_for_timeout(1200)
                titre = pg.evaluate(
                    """() => document.querySelector('.dt-l2').textContent""")
                f = os.path.join(VUES, "%s-%02d.png" % (nom, k))
                pg.screenshot(path=f)
                print("  %s  %2d  %s" % (nom, k, titre))
            pg.close()
        nav.close()
    srv.shutdown()
    print("\n→ %s" % VUES)


if __name__ == "__main__":
    main()

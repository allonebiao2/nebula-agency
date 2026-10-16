# -*- coding: utf-8 -*-
"""Photographie la page d'accueil : chaque section, et la scène 3D à plusieurs
moments du défilement, en 390 (téléphone émulé) et en 1440.

    python malettre/_voir_accueil.py            # tout
    python malettre/_voir_accueil.py scene      # la scène seule

Ce script ne juge rien : il fabrique ce qu'il faut REGARDER (standard maison
§5). ⚠️ Émulation `is_mobile` en 390, sinon le viewport est ignoré.
"""
import functools
import pathlib
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from playwright.sync_api import sync_playwright

ICI = pathlib.Path(__file__).resolve().parent
OUT = ICI / "_vues" / "accueil"
OUT.mkdir(parents=True, exist_ok=True)
SEULE = sys.argv[1] if len(sys.argv) > 1 else ""

SECTIONS = ["haut", "exemples", "plume", "occasions", "seuil", "prix", "promesses", "fin"]
MOMENTS = [0.06, 0.2, 0.36, 0.5, 0.6, 0.72, 0.84, 0.97]


class Muet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Muet, directory=str(ICI)))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d/index.html" % srv.server_address[1]
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        for larg, haut, mob in ((390, 844, True), (1440, 900, False)):
            ctx = nav.new_context(viewport={"width": larg, "height": haut}, is_mobile=mob,
                                  has_touch=mob, device_scale_factor=1)
            pg = ctx.new_page()
            pg.goto(base)
            # ⚠️ Le chargement (la lettre nouée) couvre la page ~3 s : sans
            # cette attente, la première capture le photographie par-dessus.
            pg.wait_for_function("document.getElementById('chargement').hidden", timeout=8000)
            pg.wait_for_timeout(300)
            if SEULE in ("", "scene"):
                for m in MOMENTS:
                    pg.evaluate("""m => { const s = document.querySelector('#comment');
                        const top = s.getBoundingClientRect().top + scrollY;
                        scrollTo(0, top + m * (s.offsetHeight - (innerHeight - 62))); }""", m)
                    pg.wait_for_timeout(700)
                    pg.screenshot(path=str(OUT / ("%d-scene-%02d.png" % (larg, int(m * 100)))))
            if SEULE in ("", "sections"):
                for sid in SECTIONS:
                    pg.evaluate("id => { const s = document.getElementById(id); scrollTo(0, s.getBoundingClientRect().top + scrollY - 62); }", sid)
                    pg.wait_for_timeout(1300)
                    pg.screenshot(path=str(OUT / ("%d-%s.png" % (larg, sid))))
                    # une deuxième vue plus bas dans les sections longues
                    pg.evaluate("() => scrollBy(0, innerHeight * .8)")
                    pg.wait_for_timeout(900)
                    pg.screenshot(path=str(OUT / ("%d-%s-b.png" % (larg, sid))))
            ctx.close()
        nav.close()
    srv.shutdown()
    print("captures dans", OUT)


if __name__ == "__main__":
    main()

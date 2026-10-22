# -*- coding: utf-8 -*-
"""Photographie la page d'accueil : chaque section, et la scène 3D à plusieurs
moments du défilement, en 390 (téléphone émulé) et en 1440.

    python malettre/_voir_accueil.py            # tout
    python malettre/_voir_accueil.py scene      # la scène seule
    python malettre/_voir_accueil.py en         # la page anglaise (_vues/accueil-en)

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
ARGS = sys.argv[1:]
LANGUE = "en" if "en" in ARGS else "fr"
OUT = ICI / "_vues" / ("accueil-en" if LANGUE == "en" else "accueil")
OUT.mkdir(parents=True, exist_ok=True)
SEULE = next((a for a in ARGS if a != "en"), "")

SECTIONS = ["haut", "exemples", "plume", "nuit-lettres", "occasions", "faire-part", "seuil", "prix", "promesses", "questions", "fin"]
MOMENTS = [0.06, 0.2, 0.36, 0.5, 0.6, 0.72, 0.84, 0.97]


class Muet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Muet, directory=str(ICI)))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d/%sindex.html" % (srv.server_address[1], "en/" if LANGUE == "en" else "")
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        for larg, haut, mob in ((390, 844, True), (1440, 900, False)):
            ctx = nav.new_context(viewport={"width": larg, "height": haut}, is_mobile=mob,
                                  has_touch=mob, device_scale_factor=1)
            pg = ctx.new_page()
            pg.goto(base)
            # ⚠️ Le chargement (la lettre nouée) couvre la page ~3 s : sans
            # cette attente, la première capture le photographie par-dessus.
            pg.locator("#chargement").click()   # la lettre attend le premier contact (2026-10-22)
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
                # « Ouvre-la toi-même » : rhabillée (cire or, papier coton, étoiles), puis ouverte.
                pg.evaluate("() => { const s = document.getElementById('seuil'); scrollTo(0, s.querySelector('.essai').getBoundingClientRect().top + scrollY - 80); }")
                pg.wait_for_timeout(600)
                for nom, val in (("cire", "or"), ("papier", "coton"), ("pluie", "etoiles")):
                    pg.click('input[name="hb-%s"][value="%s"]' % (nom, val))
                    pg.wait_for_timeout(500)
                pg.wait_for_timeout(1500)
                pg.screenshot(path=str(OUT / ("%d-seuil-habillee.png" % larg)))
                fr = pg.query_selector("#seuil-cadre").content_frame()
                fr.evaluate("document.getElementById('btn-ouvrir').click()")
                pg.wait_for_timeout(2600)
                pg.screenshot(path=str(OUT / ("%d-seuil-ouverte.png" % larg)))
                fr.evaluate("document.getElementById('l-gratter').scrollIntoView({block: 'center'})")
                pg.wait_for_timeout(500)
                pg.screenshot(path=str(OUT / ("%d-seuil-gratter.png" % larg)))
                # Les questions, deux réponses ouvertes.
                pg.evaluate("() => { const q = [...document.querySelectorAll('.faq details.q')]; q[0].open = q[3].open = true;"
                            " scrollTo(0, document.getElementById('questions').getBoundingClientRect().top + scrollY - 62); }")
                pg.wait_for_timeout(1200)
                pg.screenshot(path=str(OUT / ("%d-questions-ouvertes.png" % larg)))
            ctx.close()
        nav.close()
    srv.shutdown()
    print("captures dans", OUT)


if __name__ == "__main__":
    main()

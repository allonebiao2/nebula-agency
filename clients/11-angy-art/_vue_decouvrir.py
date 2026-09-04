# -*- coding: utf-8 -*-
"""ANGY ART — photographier le bouton « DÉCOUVRIR » et ce qu'il ouvre.

    python _vue_decouvrir.py

Six images dans `_vues/` : le héros (bouton fermé), le panneau ouvert, et la
même page en bas d'écran où seul le bouton de la barre reste, en 390 et en 1440.

⚠️ CES IMAGES SE REGARDENT. Un QC vert dit que rien n'est cassé, pas que c'est
lisible : les quatre défauts du 2026-08-26 chez Au Braisé d'Or et les trois du
2026-08-21 ici ont tous été trouvés sur des captures, jamais dans le code.
"""
import functools, http.server, os, socketserver, threading

ICI = os.path.dirname(os.path.abspath(__file__))
PORT = 8623
BASE = f"http://127.0.0.1:{PORT}/"
SORTIE = os.path.join(ICI, "_vues")


class Muet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


def servir():
    class Serveur(socketserver.ThreadingTCPServer):
        daemon_threads = True
        allow_reuse_address = True
    srv = Serveur(("127.0.0.1", PORT), functools.partial(Muet, directory=ICI))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    from playwright.sync_api import sync_playwright
    os.makedirs(SORTIE, exist_ok=True)
    srv = servir()
    with sync_playwright() as p:
        nav = p.chromium.launch(args=["--force-color-profile=srgb"])
        for larg, haut, mob in [(390, 844, True), (1440, 900, False)]:
            ctx = nav.new_context(viewport={"width": larg, "height": haut},
                                  is_mobile=mob, has_touch=mob,
                                  device_scale_factor=2 if mob else 1)
            page = ctx.new_page()
            page.goto(BASE, wait_until="networkidle")
            page.wait_for_timeout(3400)          # le rideau d'ouverture

            page.screenshot(path=os.path.join(SORTIE, f"dec-{larg}-1-heros.png"))

            page.evaluate("() => document.querySelector('#heroDec').click()")
            page.wait_for_timeout(900)
            page.screenshot(path=os.path.join(SORTIE, f"dec-{larg}-2-panneau.png"))

            page.keyboard.press("Escape")
            page.wait_for_timeout(700)
            page.evaluate("() => window.scrollTo(0, document.body.scrollHeight * 0.55)")
            page.wait_for_timeout(1400)
            page.screenshot(path=os.path.join(SORTIE, f"dec-{larg}-3-barre.png"))
            ctx.close()
        nav.close()
    srv.shutdown()
    print(f"six images -> _vues/dec-*.png")


if __name__ == "__main__":
    main()

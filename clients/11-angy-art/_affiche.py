# -*- coding: utf-8 -*-
"""
ANGY ART — imprime `affiche.html` en PDF A4.

    python _affiche.py   ->  assets/docs/Affiche_Angy_Art_A4.pdf

⚠️ À RELANCER dès que `assets/images/scenes/hero.webp` change : l'affiche
   porte cette photo en pleine hauteur. Le 2026-08-08, le PDF traînait encore
   l'ancienne image générée alors que le site était déjà passé aux vraies
   photos : une affiche périmée est la seule pièce du livrable qui part chez
   l'imprimeur, donc celle qu'on ne peut plus corriger après coup.

Le rendu passe par Chromium (Playwright), qui sait imprimer les fonds. Un
navigateur est nécessaire ici : l'affiche est une mise en page HTML, pas un
SVG composé à la main.
"""
import functools
import http.server
import os
import socketserver
import threading

from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "assets", "docs", "Affiche_Angy_Art_A4.pdf")


class Muet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Muet, directory=ICI))
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            nav = p.chromium.launch()
            page = nav.new_page(viewport={"width": 1240, "height": 1754})
            page.goto(f"http://127.0.0.1:{port}/affiche.html", wait_until="networkidle")
            page.wait_for_timeout(1500)
            page.pdf(path=SORTIE, format="A4", print_background=True,
                     margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
            nav.close()
    finally:
        srv.shutdown()
    print(f"  {os.path.relpath(SORTIE, ICI)}  {os.path.getsize(SORTIE) // 1024} Ko")


if __name__ == "__main__":
    main()

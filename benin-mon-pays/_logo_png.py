# -*- coding: utf-8 -*-
"""Les PNG du logo, rendus par le navigateur.

Pourquoi pas cairosvg : `libcairo-2.dll` n'est pas installable proprement sur
ce poste Windows. Playwright est déjà là pour le contrôle qualité, il rend le
même SVG avec le moteur qui servira le site. Le fond reste **transparent**
quand le SVG n'a pas de rectangle de fond.
"""
import io
import os
import re

from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ICI, "assets", "images", "logo")

# (fichier source, largeur du PNG)
SORTIES = [("logo.svg", 1200), ("logo-clair.svg", 1200),
           ("logo-marque.svg", 512), ("logo-marque-clair.svg", 512),
           ("favicon.svg", 180)]


def rendre():
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        for nom, larg in SORTIES:
            src = os.path.join(OUT, nom)
            svg = io.open(src, encoding="utf-8").read()
            m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
            vw, vh = float(m.group(1)), float(m.group(2))
            haut = int(round(larg * vh / vw))
            page = nav.new_page(viewport={"width": larg, "height": haut},
                                device_scale_factor=1)
            page.set_content(
                '<html><body style="margin:0;background:transparent">'
                + re.sub(r'width="[\d.]+" height="[\d.]+"',
                         'width="%d" height="%d"' % (larg, haut), svg, count=1)
                + "</body></html>")
            dst = os.path.join(OUT, nom.replace(".svg", ".png"))
            page.screenshot(path=dst, omit_background=True)
            page.close()
            print("  %-24s %6d o  %dx%d" % (os.path.basename(dst),
                                            os.path.getsize(dst), larg, haut))
        nav.close()


if __name__ == "__main__":
    print("PNG :")
    rendre()

# -*- coding: utf-8 -*-
"""_vues_3d.py · photographier les visites 3D, station par station, pour les REGARDER (26/11).

Un QC vert ne dit pas qu'une scène est belle : il faut la voir. Ce script sert le site en HTTP (les modules ne
marchent pas en file://), ouvre chaque visite, va aux stations choisies et assemble une planche.
    python _outils/_vues_3d.py                 (téléphone, 390 × 844)
    python _outils/_vues_3d.py --largeur 1440  (ordinateur)
La planche est écrite dans _vues/ (exclu du déploiement).
"""
import argparse
import functools
import http.server
import io
import os
import socketserver
import sys
import threading
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ICI = Path(__file__).resolve().parent.parent
VISITES = [
    ("luxury-skin-clinic.html", "visite", [1, 2, 3, 9, 10, 13, 15]),
    ("ina-luxury.html", "boutique", [0, 1, 2, 7]),
    ("harmonisation-faciale.html", "cabinet", [1]),
]


def servir():
    class Muet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    class S(socketserver.ThreadingMixIn, http.server.HTTPServer):
        daemon_threads = True

    s = S(("127.0.0.1", 0), functools.partial(Muet, directory=str(ICI)))
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--largeur", type=int, default=390)
    a = ap.parse_args()
    w = a.largeur
    h = 844 if w < 700 else 900
    srv = servir()
    port = srv.server_address[1]
    sortie = ICI / "_vues"
    sortie.mkdir(exist_ok=True)
    vignettes = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=["--use-angle=d3d11", "--ignore-gpu-blocklist", "--renderer-process-limit=1"])
        for page_html, ident, stations in VISITES:
            ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=w < 700, has_touch=w < 700, device_scale_factor=1)
            p = ctx.new_page()
            p.goto(f"http://127.0.0.1:{port}/{page_html}", wait_until="domcontentloaded", timeout=90000)
            p.wait_for_timeout(2500)
            for sel in ("#welcome-gate", f"#{ident} .s3d-porte"):
                try:
                    p.click(sel, timeout=1500)
                    p.wait_for_timeout(600)
                except Exception:
                    pass
            p.wait_for_selector(f"#{ident}.s3d-pret", timeout=60000)
            for k in stations:
                p.evaluate("([i, k]) => document.getElementById(i).s3d.moteur.aller(k)", [ident, k])
                p.wait_for_timeout(3200)
                f = sortie / f"{ident}-{w}-{k:02d}.png"
                p.screenshot(path=str(f))
                vignettes.append((f, f"{page_html.split('.')[0]} · station {k}"))
            ctx.close()
        b.close()
    srv.shutdown()
    # la planche
    tw = 300 if w < 700 else 480
    th = int(tw * h / w)
    cols = 6
    rangs = (len(vignettes) + cols - 1) // cols
    pl = Image.new("RGB", (cols * (tw + 8), rangs * (th + 26)), "white")
    d = ImageDraw.Draw(pl)
    for i, (f, nom) in enumerate(vignettes):
        im = Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = (i % cols) * (tw + 8), (i // cols) * (th + 26)
        pl.paste(im, (x, y))
        d.text((x + 4, y + th + 6), nom, fill=(0, 0, 0))
    out = sortie / f"planche-3d-{w}.jpg"
    pl.save(out, quality=78)
    print(out)


if __name__ == "__main__":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except Exception:
        pass
    main()

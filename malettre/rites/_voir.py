"""MA LETTRE À… · photographier une ouverture à plusieurs instants, pour la REGARDER avant de la livrer.

    python malettre/rites/_voir.py cachet                 # 390 × 844 (téléphone)
    python malettre/rites/_voir.py cachet --large         # 1440 × 900
    python malettre/rites/_voir.py mariage -t -1 0.2 0.5 1 1.6 2.2 --cire or --papier coton

Sert `malettre/rites/` en local, ouvre `essai.html` dans Chromium, peint chaque instant par `figer(t)` (le temps est
une donnée : aucune attente, aucune image ratée) et assemble une planche dans `rites/_planches/<rite>.png`.
"""
import argparse
import functools
import http.server
import io
import socketserver
import sys
import threading
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
ICI = Path(__file__).resolve().parent
SORTIE = ICI / "_planches"


def servir():
    gestion = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ICI))
    gestion.log_message = lambda *a: None
    srv = socketserver.TCPServer(("127.0.0.1", 0), gestion)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rite")
    ap.add_argument("-t", nargs="*", type=float, default=[-1, 0.15, 0.35, 0.6, 0.9, 1.3, 1.8, 2.3])
    ap.add_argument("--large", action="store_true")
    ap.add_argument("--cire", default="bordeaux")
    ap.add_argument("--papier", default="creme")
    ap.add_argument("--sceau", default="initiale")
    a = ap.parse_args()
    w, h = (1440, 900) if a.large else (390, 844)
    srv, port = servir()
    SORTIE.mkdir(exist_ok=True)
    images = []
    with sync_playwright() as pw:
        nav = pw.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = nav.new_page(viewport={"width": w, "height": h})
        erreurs = []
        pg.on("pageerror", lambda e: erreurs.append(str(e)))
        pg.on("console", lambda m: erreurs.append(m.text) if m.type == "error" else None)
        pg.goto(f"http://127.0.0.1:{port}/essai.html?rite={a.rite}&cire={a.cire}&papier={a.papier}&sceau={a.sceau}")
        pg.wait_for_function("window.__pret === true || window.__erreur", timeout=30000)
        if pg.evaluate("window.__erreur"):
            sys.exit("⛔ " + pg.evaluate("window.__erreur"))
        for t in a.t:
            pg.evaluate(f"figer({t}, 3)")
            # la page, pas le canvas seul : une ouverture plein écran est une fenêtre, on la juge sur ce qu'elle découvre
            images.append((t, Image.open(io.BytesIO(pg.screenshot())).convert("RGB")))
        nav.close()
    srv.shutdown()
    if erreurs:
        print("⚠️ erreurs de la page :", *erreurs[:6], sep="\n   ")
    k = 0.5 if not a.large else 0.33
    tw, th = int(w * k), int(h * k)
    col = 4
    pl = Image.new("RGB", (tw * col, th * ((len(images) + col - 1) // col)), (10, 8, 14))
    for i, (t, im) in enumerate(images):
        im = im.resize((tw, th))
        ImageDraw.Draw(im).text((6, 4), "t = %.2f s" % t, fill=(255, 220, 120))
        pl.paste(im, ((i % col) * tw, (i // col) * th))
    nom = SORTIE / (a.rite + ("-large" if a.large else "") + ".png")
    pl.save(nom)
    print("planche :", nom)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Sert le site et capture chaque section, en 390 et en 1440."""
import functools
import http.server
import math
import os
import socketserver
import threading

from PIL import Image
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = r"C:/Users/USER/.claude/jobs/bc7778e0/tmp/benin"
os.makedirs(SORTIE, exist_ok=True)
PORT = 8731


def servir():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ICI)
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


SECTIONS = ["station-0", "station-1", "station-2", "station-3", "halte-1",
            "station-4", "saut", "station-5", "station-6", "station-7", "carnet"]


def planche(fichiers, cols, larg, nom):
    ims = [Image.open(f).convert("RGB") for f in fichiers]
    w0, h0 = ims[0].size
    h = int(larg * h0 / w0)
    lig = math.ceil(len(ims) / cols)
    s = Image.new("RGB", (cols * larg, lig * h), (18, 18, 18))
    for i, im in enumerate(ims):
        s.paste(im.resize((larg, h), Image.LANCZOS), ((i % cols) * larg, (i // cols) * h))
    p = os.path.join(SORTIE, nom)
    s.save(p)
    print(p, s.size)
    return p


def passe(pw, larg, haut, mobile, etiq):
    nav = pw.chromium.launch()
    ctx = nav.new_context(viewport={"width": larg, "height": haut},
                          device_scale_factor=1, is_mobile=mobile,
                          has_touch=mobile)
    pg = ctx.new_page()
    erreurs = []
    pg.on("pageerror", lambda e: erreurs.append(str(e)))
    pg.on("console", lambda m: erreurs.append(m.text) if m.type == "error" else None)
    manquants = []
    pg.on("response", lambda r: manquants.append("%d %s" % (r.status, r.url))
          if r.status >= 400 else None)

    pg.goto("http://127.0.0.1:%d/index.html" % PORT, wait_until="load")
    pg.wait_for_timeout(1800)                       # le rideau
    pg.click("#entrer")
    pg.wait_for_timeout(900)

    fichiers = []
    for s in SECTIONS:
        pg.evaluate("""(id)=>{
          document.documentElement.style.scrollBehavior='auto';
          const e=document.getElementById(id);
          if(e) window.scrollTo(0, e.getBoundingClientRect().top + window.scrollY - 54);
        }""", s)
        pg.wait_for_timeout(1500)                   # le trait se dessine
        f = os.path.join(SORTIE, "%s_%s.png" % (etiq, s))
        pg.screenshot(path=f)
        fichiers.append(f)

    ctx.close()
    nav.close()
    return fichiers, erreurs, manquants


if __name__ == "__main__":
    srv = servir()
    try:
        with sync_playwright() as pw:
            f14, e14, m14 = passe(pw, 1440, 900, False, "pc")
            f39, e39, m39 = passe(pw, 390, 844, True, "tel")
        planche(f14, 3, 620, "planche_pc.png")
        planche(f39, 6, 300, "planche_tel.png")
        print("\nerreurs JS  PC :", e14 or "aucune")
        print("erreurs JS  TEL:", e39 or "aucune")
        print("reponses>=400  :", (m14 + m39) or "aucune")
    finally:
        srv.shutdown()

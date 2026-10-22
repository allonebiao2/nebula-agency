"""MA LETTRE À… · la démonstration des ouvertures : une vraie lettre par rite, contrôlée, puis servie en local.

    python malettre/rites/_demo.py            # contrôle les lettres, puis les sert sur http://localhost:8765/
    python malettre/rites/_demo.py --seul     # contrôle seulement

Chaque lettre est bâtie comme le serveur la bâtit (gabarit, données, `poserRite`). Le contrôle : le théâtre est posé,
aucune erreur, et le toucher ouvre la lettre. ⚠️ `python malettre/_rites.py` avant, après toute retouche d'un rite.
"""
import argparse
import functools
import http.server
import json
import socketserver
import sys
import threading
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
from _lettre_essai import lettre  # noqa: E402

DEMO = ICI / "_planches" / "demo"
EXEMPLES = {
    "bougie": ("Anniversaire", "Joyeux anniversaire", "bordeaux", "initiale", "creme", "confettis"),
    "portes": ("Saint-Valentin", "Joyeuse Saint-Valentin", "rose", "coeur", "coton", "petales"),
    "perles": ("Mariage", "Tous mes vœux de bonheur", "or", "couronne", "creme", "etoiles"),
    "cachet": ("Une lettre pour toi", "Une lettre pour toi", "bordeaux", "initiale", "kraft", "etoiles"),
}


def batir():
    DEMO.mkdir(parents=True, exist_ok=True)
    carte = json.loads((ICI / "carte.json").read_text(encoding="utf-8"))
    liens = []
    for rite, (occ, titre, cire, sceau, papier, pluie) in EXEMPLES.items():
        html = lettre(rite, cire, papier, sceau, pluie, False, occasion=occ, titre=titre)
        (DEMO / ("lettre-" + rite + ".html")).write_text(html, encoding="utf-8")
        liens.append('<a href="lettre-%s.html"><b>%s</b><i>%s</i></a>' % (rite, carte[rite]["nom"]["fr"], occ))
    (DEMO / "index.html").write_text("""<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Les ouvertures</title><style>
body{margin:0;min-height:100vh;background:#141019;color:#f4ede0;font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px;padding:32px 16px;box-sizing:border-box}
h1{font-weight:400;font-size:clamp(28px,7vw,44px);margin:0;text-align:center}
p{margin:0;color:#b3a9c2;font-family:system-ui,sans-serif;font-size:15px;text-align:center;max-width:34ch}
nav{display:grid;gap:14px;width:min(100%,420px)}
a{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:18px 22px;border-radius:14px;text-decoration:none;
color:#f4ede0;background:#1d1826;box-shadow:inset 0 0 0 1px rgba(244,237,224,.12)}
a b{font-weight:400;font-size:22px}a i{font-style:normal;font-family:system-ui,sans-serif;font-size:13px;color:#e0c266}
a:hover{background:#262033}</style></head><body>
<h1>Les ouvertures</h1><p>Une vraie lettre par ouverture. Touche le cachet (ou le bouton). Pour rejouer, recharge la page.</p>
<nav>""" + "".join(liens) + "</nav></body></html>", encoding="utf-8")


def servir(port):
    gestion = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DEMO))
    gestion.log_message = lambda *x: None
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.ThreadingTCPServer(("0.0.0.0", port), gestion)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def controler(port):
    from playwright.sync_api import sync_playwright
    ok = True
    with sync_playwright() as pw:
        nav = pw.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        for rite in EXEMPLES:
            pg = nav.new_page(viewport={"width": 390, "height": 844})
            erreurs = []
            pg.on("pageerror", lambda e: erreurs.append(str(e)))
            pg.goto("http://127.0.0.1:%d/lettre-%s.html" % (port, rite))
            pg.wait_for_timeout(1500)
            pose = pg.evaluate("document.documentElement.classList.contains('avec-rite')")
            bouton = pg.evaluate("document.querySelector('#btn-ouvrir').textContent")
            pg.click("#env")
            t0 = time.time()
            ouverte = False
            while time.time() - t0 < 12:
                if pg.evaluate("document.querySelector('#lettre').classList.contains('ouverte')"):
                    ouverte = True
                    break
                pg.wait_for_timeout(200)
            bon = pose and ouverte and not erreurs
            ok = ok and bon
            print("%s %-7s théâtre %s · bouton « %s » · ouverte en %.1f s%s" % ("✓" if bon else "✗", rite, "posé" if pose else "ABSENT",
                  bouton, time.time() - t0, (" · " + "; ".join(erreurs[:2])) if erreurs else ""))
            pg.close()
        nav.close()
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seul", action="store_true")
    a = ap.parse_args()
    batir()
    srv = servir(8765)
    ok = controler(8765)
    if a.seul:
        srv.shutdown()
        sys.exit(0 if ok else 1)
    print("\nLa démonstration : http://localhost:8765/   (Ctrl+C pour arrêter)")
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()

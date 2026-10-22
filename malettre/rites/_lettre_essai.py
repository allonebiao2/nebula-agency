"""MA LETTRE À… · essayer une ouverture DANS une vraie lettre (le seuil, ses mots, le toucher, l'ouverture).

    python malettre/rites/_lettre_essai.py cachet                    # photographie le seuil puis l'ouverture
    python malettre/rites/_lettre_essai.py cachet --cire or --pluie confettis --verrou
    python malettre/rites/_lettre_essai.py cachet --servir           # la laisse ouverte sur http://localhost:8765/

Bâtit la lettre comme le serveur : le gabarit, les données (`_injecter.py`), puis l'ouverture (`poserRite` de
`rites.js`, la même fonction que le serveur). ⚠️ Lancer `python malettre/_rites.py` avant, après toute retouche d'un rite.
"""
import argparse
import functools
import http.server
import json
import socketserver
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ICI = Path(__file__).resolve().parent
RACINE = ICI.parent
sys.path.insert(0, str(RACINE))
from _injecter import poser  # noqa: E402

SORTIE = ICI / "_planches"


def lettre(rite, cire, papier, sceau, pluie, verrou, occasion="Anniversaire", titre="Joyeux anniversaire", plus=None):
    d = {
        "occasion": occasion, "pour": "Afi", "de": "Koffi", "titre": titre, "code": "",
        "lettre": ["Je ne sais pas écrire les belles phrases, alors je vais écrire les vraies.",
                   "Depuis que tu es là, les journées ordinaires ont cessé d'être ordinaires.",
                   "Bon anniversaire. Je nous souhaite encore beaucoup de jours comme ceux-là."],
        "photos": [], "depuis": "", "formule": "Avec tout mon cœur,", "pied": True,
        "ouvre": (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M") if verrou else "",
        "lien": "https://malettre.nebula-agency.online", "langue": "fr",
        "habillage": {"cire": cire, "sceau": sceau, "papier": papier, "pluie": pluie},
        "gratter": "", "repondre": "", "rite": rite,
    }
    d.update(plus or {})
    html = poser(d)
    # ⚠️ Par un fichier : `node -e` avec les 50 Ko de rites.js dépasse la longueur d'une commande sous Windows.
    SORTIE.mkdir(exist_ok=True)
    poseur = SORTIE / "_poser.js"
    poseur.write_text("const fs=require('fs');eval(fs.readFileSync(process.argv[2],'utf8'));let s='';"
                      "process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>process.stdout.write(poserRite(s,process.argv[3],process.argv[4])));",
                      encoding="utf-8")
    r = subprocess.run(["node", str(poseur), str(ICI.parent / "rites.js"), rite, cire], input=html.encode("utf-8"),
                       capture_output=True, check=True)
    return r.stdout.decode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rite")
    ap.add_argument("--cire", default="bordeaux")
    ap.add_argument("--papier", default="creme")
    ap.add_argument("--sceau", default="initiale")
    ap.add_argument("--pluie", default="etoiles")
    ap.add_argument("--verrou", action="store_true")
    ap.add_argument("--servir", action="store_true")
    a = ap.parse_args()
    SORTIE.mkdir(exist_ok=True)
    (SORTIE / "lettre.html").write_text(lettre(a.rite, a.cire, a.papier, a.sceau, a.pluie, a.verrou), encoding="utf-8")
    gestion = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SORTIE))
    gestion.log_message = lambda *x: None
    srv = socketserver.TCPServer(("127.0.0.1", 8765 if a.servir else 0), gestion)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = "http://127.0.0.1:%d/lettre.html" % srv.server_address[1]
    if a.servir:
        print("la lettre :", url, "(Ctrl+C pour arrêter)")
        while True:
            time.sleep(3600)
    from playwright.sync_api import sync_playwright
    from PIL import Image, ImageDraw
    import io
    vues = []
    with sync_playwright() as pw:
        nav = pw.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        erreurs = []
        pg.on("pageerror", lambda e: erreurs.append(str(e)))
        pg.on("console", lambda m: erreurs.append(m.text) if m.type in ("error", "warning") else None)
        pg.goto(url)
        pg.wait_for_timeout(1800)
        avec = pg.evaluate("document.documentElement.classList.contains('avec-rite')")
        vues.append(("seuil", Image.open(io.BytesIO(pg.screenshot())).convert("RGB")))
        if not a.verrou:
            pg.click("#env")
            t0 = time.time()
            for k in (0.3, 0.7, 1.1, 1.6, 2.1, 2.6, 3.4):
                pg.wait_for_timeout(max(0, int((k - (time.time() - t0)) * 1000)))
                vues.append(("%.1f s" % (time.time() - t0), Image.open(io.BytesIO(pg.screenshot())).convert("RGB")))
        etat = pg.evaluate("({ouverte: document.querySelector('#lettre').classList.contains('ouverte'), parti: document.querySelector('#seuil').classList.contains('parti')})")
        nav.close()
    srv.shutdown()
    print("théâtre posé :", avec, "· après :", etat)
    if erreurs:
        print("⚠️", *erreurs[:8], sep="\n   ")
    tw, th = 195, 422
    pl = Image.new("RGB", (tw * 4, th * ((len(vues) + 3) // 4)), (10, 8, 14))
    for i, (lib, im) in enumerate(vues):
        im = im.resize((tw, th))
        ImageDraw.Draw(im).text((6, 4), lib, fill=(255, 220, 120))
        pl.paste(im, ((i % 4) * tw, (i // 4) * th))
    nom = SORTIE / ("lettre-" + a.rite + ("-verrou" if a.verrou else "") + ".png")
    pl.save(nom)
    print("planche :", nom)


if __name__ == "__main__":
    main()

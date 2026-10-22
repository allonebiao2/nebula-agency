"""MA LETTRE À… · le GESTE des portes, vérifié (pas seulement « la lettre finit par s'ouvrir »).

    python malettre/rites/_geste_essai.py                  # portes-dentelle
    python malettre/rites/_geste_essai.py moucharabieh

Pourquoi ce banc : le 2026-10-22, le contrôle de la démonstration disait « ouverte, portes devant la lettre » alors
que les portes s'étaient ouvertes TOUTES SEULES (l'ouverture automatique de 6,5 s) : le rendu logiciel du navigateur
de contrôle (SwiftShader) met une demi-seconde par image, le geste arrivait trop tard. Ici l'ouverture automatique
est repoussée (`auto=99`) : si les portes s'ouvrent, c'est le doigt qui les a ouvertes.

Sur le banc (`essai.html?jouer=1`) :
  · un simple toucher, une fois le cachet cassé → elles s'ouvrent ;
  · un petit glissé (20 px), lâché → elles reviennent ;
  · un grand glissé (120 px) → elles partent seules ;
Dans une vraie lettre (`_planches/demo/`, bâtie par `_demo.py`) :
  · glisser AVANT d'avoir touché le cachet → le cachet casse, et le même doigt ouvre les portes.
"""
import functools
import http.server
import socketserver
import sys
import threading
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ICI = Path(__file__).resolve().parent


def servir(dossier):
    g = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(dossier))
    g.log_message = lambda *a: None
    srv = socketserver.TCPServer(("127.0.0.1", 0), g)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    rite = sys.argv[1] if len(sys.argv) > 1 else "portes-dentelle"
    banc, demo = servir(ICI), servir(ICI / "_planches" / "demo")
    from playwright.sync_api import sync_playwright
    bons, erreurs = [], []
    with sync_playwright() as pw:
        nav = pw.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])

        def page(url):
            pg = nav.new_page(viewport={"width": 390, "height": 844})
            pg.on("pageerror", lambda e: erreurs.append(str(e)))
            pg.goto(url)
            pg.wait_for_function("window.__pret === true || window.__erreur || window.RITE !== undefined", timeout=40000)
            return pg

        def etat(pg, objet="window.__rite"):
            return pg.evaluate("(() => { const r = %s; return { etat: r.etat, ang: +(r.ang || 0).toFixed(2), t0: r.t0 }; })()" % objet)

        def libre(pg):
            pg.evaluate("__ouvrir()")
            pg.wait_for_function("window.__rite.etat === 'libre'", timeout=20000)
            pg.wait_for_timeout(900)          # le cachet est tombé, les battants sont déverrouillés (0,45 s)

        url = "http://127.0.0.1:%d/essai.html?rite=%s&jouer=1&auto=99" % (banc.server_address[1], rite)
        # 1 · un simple toucher
        pg = page(url); libre(pg)
        pg.mouse.click(195, 520)
        pg.wait_for_timeout(400)
        e = etat(pg); bons.append(("un toucher les ouvre", e["etat"] == "ouvre", e)); pg.close()
        # 2 · un petit glissé lâché : elles reviennent
        pg = page(url); libre(pg)
        pg.mouse.move(195, 520); pg.mouse.down(); pg.mouse.move(215, 520, steps=3); pg.wait_for_timeout(300); pg.mouse.up()
        pg.wait_for_timeout(300)
        e = etat(pg); bons.append(("un petit glissé (20 px) : elles reviennent", e["etat"] in ("retour", "libre"), e)); pg.close()
        # 3 · un grand glissé : elles partent seules
        pg = page(url); libre(pg)
        pg.mouse.move(195, 520); pg.mouse.down(); pg.mouse.move(315, 520, steps=6)
        e = etat(pg); pg.mouse.up()
        bons.append(("un grand glissé (120 px) : elles partent pendant le geste", e["etat"] == "ouvre", e)); pg.close()
        # 4 · dans une vraie lettre : glisser AVANT d'avoir touché le cachet
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: erreurs.append(str(e)))
        # l'ouverture automatique repoussée (le crochet des contrôles) : SwiftShader livre le geste en plusieurs secondes
        pg.add_init_script("window.__malettreAuto = 99")
        pg.goto("http://127.0.0.1:%d/lettre-%s.html" % (demo.server_address[1], rite))
        pg.wait_for_timeout(2500)
        t = time.time()
        # ⚠️ sur les portes, pas sur le bouton « Ouvrir les portes » (vers y = 530), qui est au-dessus d'elles
        pg.mouse.move(195, 300); pg.mouse.down(); pg.mouse.move(235, 300, steps=3)     # 40 px : c'est le geste, le cachet casse
        pg.wait_for_timeout(700)
        pg.mouse.move(345, 300, steps=6); pg.mouse.up()                              # le même doigt écarte les portes
        e = etat(pg, "RITE.rite")
        par_le_doigt = e["etat"] == "ouvre" and e["t0"] is not None and e["t0"] < 90
        bons.append(("vraie lettre : un glissé avant le cachet casse le cachet, puis ouvre les portes (pas l'automatique)", par_le_doigt, e))
        nav.close()
    banc.shutdown(); demo.shutdown()
    for lib, ok, e in bons:
        print(("✓ " if ok else "✗ ") + lib + ("" if ok else "   " + str(e)))
    if erreurs:
        print("⚠️", *erreurs[:5], sep="\n   ")
    sys.exit(0 if all(ok for _, ok, _ in bons) and not erreurs else 1)


if __name__ == "__main__":
    main()

"""MA LETTRE À… · le GESTE des ouvertures plein écran, vérifié (pas seulement « la lettre finit par s'ouvrir »).

    python malettre/rites/_geste_essai.py                  # portes-dentelle
    python malettre/rites/_geste_essai.py moucharabieh
    python malettre/rites/_geste_essai.py rideau-theatre

Pourquoi ce banc : le 2026-10-22, le contrôle de la démonstration disait « ouverte, portes devant la lettre » alors
que les portes s'étaient ouvertes TOUTES SEULES (l'ouverture automatique de 6,5 s) : le rendu logiciel du navigateur
de contrôle (SwiftShader) met une demi-seconde par image, le geste arrivait trop tard. Ici l'automatique est repoussé
(`auto=99` sur le banc, `window.__malettreAuto` dans une vraie lettre) : si ça s'ouvre, c'est le doigt.

LES PORTES, sur le banc (`essai.html?jouer=1`) : un simple toucher les ouvre ; un petit glissé (20 px) lâché, elles
reviennent ; un grand glissé (120 px), elles partent pendant le geste. Dans une vraie lettre (`_planches/demo/`, bâtie
par `_demo.py`) : glisser AVANT d'avoir touché le cachet le casse, et le même doigt ouvre les portes.
LE RIDEAU : le 2e toucher frappe le 2e coup, le 3e lève le rideau ; deux touchers collés ne font qu'un coup ; dans une
vraie lettre, le bouton puis deux touchers sur la scène.
"""
import functools
import http.server
import socketserver
import sys
import threading
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ICI = Path(__file__).resolve().parent
VUE = {"width": 390, "height": 844}


def servir(dossier):
    g = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(dossier))
    g.log_message = lambda *a: None
    srv = socketserver.TCPServer(("127.0.0.1", 0), g)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


class Banc:
    def __init__(self, nav, banc, demo, rite):
        self.nav, self.rite, self.bons, self.erreurs = nav, rite, [], []
        self.url = "http://127.0.0.1:%d/essai.html?rite=%s&jouer=1&auto=99" % (banc.server_address[1], rite)
        self.lettre = "http://127.0.0.1:%d/lettre-%s.html" % (demo.server_address[1], rite)

    def page(self, url=None, crochet=False):
        pg = self.nav.new_page(viewport=VUE)
        pg.on("pageerror", lambda e: self.erreurs.append(str(e)))
        if crochet:
            # l'ouverture automatique repoussée (le crochet des contrôles) : SwiftShader livre le geste en plusieurs secondes
            pg.add_init_script("window.__malettreAuto = 99")
        pg.goto(url or self.url)
        if url:
            pg.wait_for_timeout(2500)
        else:
            pg.wait_for_function("window.__pret === true || window.__erreur", timeout=40000)
        return pg

    def note(self, lib, ok, e):
        self.bons.append((lib, ok, e))

    # ── les portes ──
    def portes(self):
        etat = lambda pg, o="window.__rite": pg.evaluate("(() => { const r = %s; return { etat: r.etat, ang: +(r.ang || 0).toFixed(2), t0: r.t0 }; })()" % o)

        def libre(pg):
            pg.evaluate("__ouvrir()")
            pg.wait_for_function("window.__rite.etat === 'libre'", timeout=20000)
            pg.wait_for_timeout(900)          # le cachet est tombé, les battants sont déverrouillés (0,45 s)
        pg = self.page(); libre(pg)
        pg.mouse.click(195, 520); pg.wait_for_timeout(400)
        e = etat(pg); self.note("un toucher les ouvre", e["etat"] == "ouvre", e); pg.close()
        pg = self.page(); libre(pg)
        pg.mouse.move(195, 520); pg.mouse.down(); pg.mouse.move(215, 520, steps=3); pg.wait_for_timeout(300); pg.mouse.up()
        pg.wait_for_timeout(300)
        e = etat(pg); self.note("un petit glissé (20 px) : elles reviennent", e["etat"] in ("retour", "libre"), e); pg.close()
        pg = self.page(); libre(pg)
        pg.mouse.move(195, 520); pg.mouse.down(); pg.mouse.move(315, 520, steps=6)
        e = etat(pg); pg.mouse.up()
        self.note("un grand glissé (120 px) : elles partent pendant le geste", e["etat"] == "ouvre", e); pg.close()
        pg = self.page(self.lettre, crochet=True)
        # ⚠️ sur les portes, pas sur le bouton « Ouvrir les portes » (vers y = 530), qui est au-dessus d'elles
        pg.mouse.move(195, 300); pg.mouse.down(); pg.mouse.move(235, 300, steps=3)     # 40 px : c'est le geste, le cachet casse
        pg.wait_for_timeout(700)
        pg.mouse.move(345, 300, steps=6); pg.mouse.up()                              # le même doigt écarte les portes
        e = etat(pg, "RITE.rite"); pg.close()
        self.note("vraie lettre : un glissé avant le cachet casse le cachet, puis ouvre les portes (pas l'automatique)",
                  e["etat"] == "ouvre" and e["t0"] is not None and e["t0"] < 90, e)

    # ── le rideau : les trois coups ──
    def rideau(self):
        lire = "(() => { const r = window.__rite || (window.RITE && RITE.rite); return { coups: r.coups.length, ouvre: r.tOuvre != null }; })()"
        pg = self.page()
        pg.evaluate("__ouvrir()"); pg.wait_for_timeout(500)
        pg.mouse.click(195, 420); pg.wait_for_timeout(500)
        e2 = pg.evaluate(lire)
        pg.mouse.click(195, 420); pg.wait_for_timeout(300)
        e3 = pg.evaluate(lire); pg.close()
        self.note("le 2e toucher frappe le 2e coup", e2["coups"] == 2 and not e2["ouvre"], e2)
        self.note("le 3e toucher frappe le 3e coup et le rideau se lève", e3["coups"] == 3 and e3["ouvre"], e3)
        pg = self.page()
        pg.evaluate("__ouvrir()"); pg.wait_for_timeout(500)
        pg.evaluate("""(() => { const c = document.getElementById('scene'), o = { clientX: 195, clientY: 420, pointerId: 1, bubbles: true };
          c.dispatchEvent(new PointerEvent('pointerdown', o)); c.dispatchEvent(new PointerEvent('pointerup', o));
          c.dispatchEvent(new PointerEvent('pointerdown', o)); c.dispatchEvent(new PointerEvent('pointerup', o)); })()""")
        e = pg.evaluate(lire); pg.close()
        self.note("deux touchers collés ne comptent qu'un coup", e["coups"] == 2, e)
        pg = self.page(self.lettre, crochet=True)
        pg.click("#btn-ouvrir"); pg.wait_for_timeout(600)
        pg.mouse.click(195, 300); pg.wait_for_timeout(600); pg.mouse.click(195, 300)
        e = pg.evaluate(lire); pg.close()
        self.note("vraie lettre : le bouton puis deux touchers lèvent le rideau", e["coups"] == 3 and e["ouvre"], e)


def main():
    rite = sys.argv[1] if len(sys.argv) > 1 else "portes-dentelle"
    banc, demo = servir(ICI), servir(ICI / "_planches" / "demo")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        nav = pw.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        b = Banc(nav, banc, demo, rite)
        pg = b.page(); meca = pg.evaluate("window.__rite.id"); pg.close()
        if meca == "rideau":
            b.rideau()
        elif meca == "battants":
            b.portes()
        else:
            sys.exit("⛔ « %s » n'est pas une ouverture à geste (mécanique %s)" % (rite, meca))
        nav.close()
    banc.shutdown(); demo.shutdown()
    for lib, ok, e in b.bons:
        print(("✓ " if ok else "✗ ") + lib + ("" if ok else "   " + str(e)))
    if b.erreurs:
        print("⚠️", *b.erreurs[:5], sep="\n   ")
    sys.exit(0 if all(ok for _, ok, _ in b.bons) and not b.erreurs else 1)


if __name__ == "__main__":
    main()

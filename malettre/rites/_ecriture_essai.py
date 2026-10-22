"""MA LETTRE À… · regarder la lettre S'ÉCRIRE (`rites/ecriture.js`) dans une vraie lettre complète.

    python malettre/rites/_ecriture_essai.py                      # planche : l'ouverture, puis l'écriture seconde après seconde
    python malettre/rites/_ecriture_essai.py --rite bougie --papier nuit
    python malettre/rites/_ecriture_essai.py --presser            # deux touchers : tout doit être écrit tout de suite
    python malettre/rites/_ecriture_essai.py --sans-3d            # sans WebGL : l'ouverture d'avant, puis l'écriture

La lettre porte tout : quatre paragraphes, deux photos, la phrase à gratter, les jours ensemble, « Répondre », le pied.
Contrôle : aucune erreur ; l'écriture AVANCE (des caractères visibles, pas tous) et la page la suit ; à la fin, tout
est écrit, le texte est redevenu du texte, la plume est partie, la pluie est tombée.
⚠️ `python malettre/_rites.py` avant, après toute retouche.
"""
import argparse
import base64
import functools
import http.server
import io
import socketserver
import sys
import threading
import time
from pathlib import Path

from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8")
ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
from _lettre_essai import lettre  # noqa: E402

SORTIE = ICI / "_planches"
TEXTE = [
    "Afi, je ne sais pas écrire les belles phrases, alors je vais écrire les vraies, une par une, sans me presser.",
    "Depuis que tu es là, les journées ordinaires ont cessé d'être ordinaires : le marché du samedi, le thé trop sucré, "
    "tes rires dans la cour quand la pluie arrive d'un coup.",
    "Je garde tout. Les petits mots sur le frigo, la photo floue de Ouidah, et cette chanson que tu fredonnes faux "
    "(oui, faux) en cuisinant.",
    "Bon anniversaire, mon cœur. Je nous souhaite encore beaucoup de jours comme ceux-là, et quelques-uns meilleurs.",
]


def photo(teinte):
    im = Image.new("RGB", (480, 480), teinte)
    g = ImageDraw.Draw(im)
    for i in range(14):
        g.ellipse((40 + i * 22, 60 + (i % 5) * 50, 160 + i * 22, 180 + (i % 5) * 50),
                  fill=tuple(min(255, c + 18 * (i % 4)) for c in teinte))
    b = io.BytesIO()
    im.save(b, "JPEG", quality=70)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode("ascii")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rite", default="cachet")
    ap.add_argument("--cire", default="bordeaux")
    ap.add_argument("--papier", default="creme")
    ap.add_argument("--pluie", default="confettis")
    ap.add_argument("--presser", action="store_true")
    ap.add_argument("--sans-3d", action="store_true")
    a = ap.parse_args()
    plus = {"lettre": TEXTE, "gratter": "Je t'emmène à Grand-Popo en décembre.", "repondre": "22997000000",
            "depuis": "2019-03-14",
            "photos": [{"src": photo((168, 96, 74)), "legende": "Ouidah, 2023"}, {"src": photo((70, 104, 128)), "legende": "La cour"}]}
    html = lettre(a.rite, a.cire, a.papier, "initiale", a.pluie, False, plus=plus)
    SORTIE.mkdir(exist_ok=True)
    (SORTIE / "ecriture.html").write_text(html, encoding="utf-8")
    gestion = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SORTIE))
    gestion.log_message = lambda *x: None
    srv = socketserver.TCPServer(("127.0.0.1", 0), gestion)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = "http://127.0.0.1:%d/ecriture.html" % srv.server_address[1]

    from playwright.sync_api import sync_playwright
    vues, journal, erreurs = [], [], []
    ETAT = """() => { const c = document.querySelectorAll('.c'); let v = 0; c.forEach(e => { if (e.classList.contains('vu')) v++; });
      return { vu: v, tout: c.length, y: Math.round(scrollY), plume: !!document.querySelector('.plume.vu'),
        pluie: !!document.querySelector('canvas.pluie'), ecrit: document.documentElement.classList.contains('ecrit-lent') }; }"""
    with sync_playwright() as pw:
        args = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] + (["--disable-webgl", "--disable-3d-apis"] if a.sans_3d else [])
        nav = pw.chromium.launch(args=args)
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: erreurs.append(str(e)))
        pg.on("console", lambda m: erreurs.append(m.text) if m.type in ("error", "warning") else None)
        pg.goto(url)
        pg.wait_for_timeout(1500)
        vues.append(("seuil", Image.open(io.BytesIO(pg.screenshot())).convert("RGB")))
        pg.click("#env")
        t0 = time.time()
        pluie_vue = False
        if a.presser:
            # attendre que la main écrive, toucher deux fois la feuille, mesurer le temps qu'il faut pour que TOUT soit écrit
            pg.wait_for_function("document.querySelectorAll('.c.vu').length >= 20", timeout=60000)
            journal.append((round(time.time() - t0, 1), pg.evaluate(ETAT)))
            pg.mouse.click(195, 420); pg.wait_for_timeout(250); pg.mouse.click(195, 420)
            t1 = time.time()
            pg.wait_for_function("(() => { const c = document.querySelectorAll('.c'); return c.length && Array.from(c).every(e => e.classList.contains('vu')); })()", timeout=15000)
            main.tout_en = time.time() - t1
            journal.append((round(time.time() - t0, 1), pg.evaluate(ETAT)))
            vues.append(("2 touchers + %.1f s" % main.tout_en, Image.open(io.BytesIO(pg.screenshot())).convert("RGB")))
        instants = () if a.presser else (1.5, 3.5, 5.5, 7.5, 10, 13, 17, 21, 26, 31, 36, 42, 48)
        for k in instants:
            while time.time() - t0 < k:
                pg.wait_for_timeout(100)
                pluie_vue = pluie_vue or pg.evaluate("!!document.querySelector('canvas.pluie')")
            e = pg.evaluate(ETAT)
            journal.append((round(time.time() - t0, 1), e))
            vues.append(("%.0f s · %d/%d" % (time.time() - t0, e["vu"], e["tout"]), Image.open(io.BytesIO(pg.screenshot())).convert("RGB")))
            if e["tout"] and e["vu"] == e["tout"] and not e["plume"] and k > 8:
                break
        # la fin : la pluie tombe, puis le texte redevient du texte
        for _ in range(40):
            pluie_vue = pluie_vue or pg.evaluate("!!document.querySelector('canvas.pluie')")
            if pg.evaluate("!document.querySelector('.plume')"):
                break
            pg.wait_for_timeout(250)
        fin = pg.evaluate("""() => ({ restes: document.querySelectorAll('#l-corps .c').length,
          texte: Array.from(document.querySelectorAll('#l-corps p')).map(p => p.textContent),
          titre: document.querySelector('#l-titre .sr') && document.querySelector('#l-titre .sr').textContent,
          plume: !!document.querySelector('.plume'), ouvert: document.querySelector('#lettre').classList.contains('ouverte'),
          photos: Array.from(document.querySelectorAll('.polaroid')).map(p => getComputedStyle(p).opacity),
          pied: getComputedStyle(document.querySelector('#l-pied')).opacity,
          lu: localStorage.getItem('malettre:lue:' + location.pathname) })""")
        vues.append(("fin", Image.open(io.BytesIO(pg.screenshot(full_page=True))).convert("RGB")))
        nav.close()
    srv.shutdown()

    for t, e in journal:
        print("%5.1f s  %4d/%-4d  défilement %5d  plume %s  pluie %s" % (t, e["vu"], e["tout"], e["y"], "oui" if e["plume"] else "non", "oui" if e["pluie"] else "non"))
    bons = []
    bons.append(("aucune erreur", not erreurs))
    avance = [e["vu"] for _, e in journal if 0 < e["vu"] < e["tout"]]
    if not a.presser:
        bons.append(("l'écriture avance (au moins 4 états intermédiaires croissants)", len(avance) >= 4 and avance == sorted(avance)))
        ys = [e["y"] for _, e in journal]
        bons.append(("la page suit l'écriture (le défilement descend)", max(ys) > 600))
    else:
        # ⚠️ SwiftShader (le rendu logiciel du navigateur de contrôle) rend la page lente : 3 s ici, c'est l'instant ailleurs
        bons.append(("deux touchers : tout est écrit d'un coup (%.1f s)" % main.tout_en, main.tout_en < 3))
    bons.append(("le texte est redevenu du texte", fin["restes"] == 0 and fin["texte"] == TEXTE))
    bons.append(("le titre reste lisible (copie pour lecteur d'écran)", bool(fin["titre"])))
    bons.append(("la plume est partie", not fin["plume"]))
    bons.append(("les photos et le pied sont visibles", all(float(o) > 0.99 for o in fin["photos"]) and float(fin["pied"]) > 0.99))
    bons.append(("la pluie est tombée à la fin", pluie_vue or any(e["pluie"] for _, e in journal)))
    bons.append(("la lettre est notée lue sur cet appareil", fin["lu"] == "1"))
    for lib, ok in bons:
        print(("✓ " if ok else "✗ ") + lib)
    if erreurs:
        print("⚠️", *erreurs[:6], sep="\n   ")

    tw, th = 195, 422
    cadres = [(l, im) for l, im in vues if l != "fin"]
    pl = Image.new("RGB", (tw * 5, th * ((len(cadres) + 4) // 5)), (10, 8, 14))
    for i, (lib, im) in enumerate(cadres):
        im = im.resize((tw, th))
        ImageDraw.Draw(im).text((6, 4), lib, fill=(255, 220, 120))
        pl.paste(im, ((i % 5) * tw, (i // 5) * th))
    nom = SORTIE / ("ecriture-" + a.rite + ("-presser" if a.presser else "") + ("-sans3d" if a.sans_3d else "") + ".png")
    pl.save(nom)
    fin_im = vues[-1][1]
    fin_im.resize((390, int(fin_im.height * 390 / fin_im.width))).save(SORTIE / "ecriture-fin.png")
    print("planche :", nom, "· page entière :", SORTIE / "ecriture-fin.png")
    sys.exit(0 if all(ok for _, ok in bons) else 1)


if __name__ == "__main__":
    main()

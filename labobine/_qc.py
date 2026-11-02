"""QC de LA BOBINE : le parcours complet dans un vrai Chrome, puis l'examen du MP4 exporté.

    python labobine/_qc.py            (sortie 1 si un contrôle échoue)

Fabrique ses propres médias d'essai avec FFmpeg, sert le dossier en local, joue le rôle de l'utilisateur
(créer, importer, écrire, diviser, annuler, transition, exporter, recharger, téléphone) et range les captures
dans %TEMP%/labobine-qc pour qu'on les REGARDE.
"""
import base64
import json
import os
import shutil
import socket
import subprocess
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
ICI = Path(__file__).resolve().parent
TMP = Path(os.environ.get("TEMP", "/tmp")) / "labobine-qc"
LIENS = Path.home() / "AppData/Local/Microsoft/WinGet/Links"
FFMPEG = shutil.which("ffmpeg") or str(LIENS / "ffmpeg.exe")
FFPROBE = shutil.which("ffprobe") or str(LIENS / "ffprobe.exe")
verts, rouges = 0, []


def ok(cond, msg):
    global verts
    if cond:
        verts += 1
        print(f"  ✔ {msg}")
    else:
        rouges.append(msg)
        print(f"  ✘ {msg}")


def ff(*args):
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", *args], check=True)


def medias_essai():
    TMP.mkdir(parents=True, exist_ok=True)
    a, b, photo, son = TMP / "a.mp4", TMP / "b.mp4", TMP / "photo.png", TMP / "son.m4a"
    if not a.exists():
        ff("-f", "lavfi", "-i", "testsrc2=size=640x360:rate=30:duration=3", "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(a))
        ff("-f", "lavfi", "-i", "smptebars=size=480x270:rate=30:duration=2", "-f", "lavfi", "-i", "sine=frequency=880:duration=2",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(b))
        ff("-f", "lavfi", "-i", "color=c=0x3b7ddd:size=800x600:d=1", "-frames:v", "1", str(photo))
        ff("-f", "lavfi", "-i", "sine=frequency=330:duration=4", "-c:a", "aac", str(son))
    return a, b, photo, son


class Service(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".js": "text/javascript", ".mjs": "text/javascript",
                      ".webmanifest": "application/manifest+json", ".svg": "image/svg+xml"}

    def log_message(self, *a):
        pass


def servir():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    srv = ThreadingHTTPServer(("127.0.0.1", port), partial(Service, directory=str(ICI)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{port}/"


ETAT = """() => { const a = window.__labobine, p = a.p; if (!p) return null;
  const fin = c => c.debut + (c.genre === 'texte' ? c.duree : (c.sortie - c.entree) / (c.vitesse || 1));
  return { pistes: p.pistes.map(t => ({ genre: t.genre, n: t.clips.length })), principale: p.pistes[0].clips.map(c => c.id),
    duree: Math.max(0, ...p.pistes.flatMap(t => t.clips.map(fin))), sel: a.selection,
    textes: p.pistes.filter(t => t.genre === 'texte').flatMap(t => t.clips.map(c => c.texte)) }; }"""

LIRE_BLOB = """async () => { const b = window.__labobine.dernierExport.blob; const u = new Uint8Array(await b.arrayBuffer());
  let s = ''; for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); return btoa(s); }"""


def nb(etat, genre):
    return sum(t["n"] for t in etat["pistes"] if t["genre"] == genre)


def main():
    a, b, photo, son = medias_essai()
    srv, url = servir()
    erreurs = []
    with sync_playwright() as pw:
        nav = pw.chromium.launch(channel="chrome", headless=True, args=["--autoplay-policy=no-user-gesture-required"])
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.on("console", lambda m: erreurs.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: erreurs.append(str(e)))
        etat = lambda: page.evaluate(ETAT)

        print("Accueil")
        page.goto(url)
        page.wait_for_selector("#liste-projets .vide")
        ok(page.is_visible("#accueil"), "l'accueil s'affiche, sans projet")

        print("Nouveau projet et import")
        page.click("#btn-nouveau")
        page.click('.choix-format[value="9:16"]')
        page.wait_for_selector("#editeur:not([hidden])")
        ok(page.evaluate("() => window.__labobine.p.format") == "9:16", "projet vertical 9:16 créé")
        page.set_input_files("#entree-fichiers", [str(a), str(b), str(photo)])
        page.wait_for_function("() => window.__labobine.p && window.__labobine.p.pistes[0].clips.length === 3", timeout=30000)
        e = etat()
        ok(abs(e["duree"] - 8) < 0.15, f"3 médias posés bout à bout : {e['duree']:.2f} s (attendu 8)")
        ok(page.locator("#pistes .clip").count() == 3, "3 clips dessinés sur la frise")
        ok(page.locator("#grille-medias .carte-media").count() == 3, "3 médias dans la bibliothèque")

        page.click('[data-onglet="son"]')
        page.set_input_files("#entree-sons", [str(son)])
        page.wait_for_function("() => window.__labobine.p.pistes.some(t => t.genre === 'audio')", timeout=20000)
        ok(page.locator("#pistes .clip.g-audio svg.onde").count() == 1, "le son importé a sa forme d'onde sur la frise")

        print("Texte")
        page.evaluate("() => window.__labobine.allerA(0)")
        page.click('[data-onglet="texte"]')
        page.click('[data-style="titre"]')
        page.wait_for_selector('#corps-inspecteur textarea[data-k="texte"]')
        page.fill('#corps-inspecteur textarea[data-k="texte"]', "Bonjour Cotonou")
        ok("Bonjour Cotonou" in etat()["textes"], "le texte se modifie depuis les réglages")

        print("Diviser, annuler, rétablir")
        page.evaluate("() => { const a = window.__labobine; a.selectionner(a.p.pistes[0].clips[0].id); a.allerA(1); }")
        page.click("#btn-diviser")
        ok(len(etat()["principale"]) == 4, "diviser à 1 s donne 4 clips")
        ok(abs(etat()["duree"] - 8) < 0.15, "diviser ne change pas la durée")
        page.click("#btn-annuler")
        ok(len(etat()["principale"]) == 3, "annuler revient à 3 clips")
        page.click("#btn-retablir")
        ok(len(etat()["principale"]) == 4, "rétablir redonne 4 clips")

        print("Transition et aperçu")
        page.evaluate("() => { const a = window.__labobine; a.selectionner(a.p.pistes[0].clips[2].id, {}); }")
        page.select_option('[data-k="transition.type"]', "fondu")
        ok(page.evaluate("() => window.__labobine.p.pistes[0].clips[2].transition.type") == "fondu", "transition « fondu » posée")
        ok(page.locator(".jonction.active").count() == 1, "la jonction s'allume sur la frise")
        page.evaluate("() => { const a = window.__labobine; a.selectionner(null); a.allerA(0.5); }")
        page.wait_for_timeout(900)
        lum = page.evaluate("""() => { const c = document.getElementById('toile'); const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
          let s = 0, n = 0; for (let i = 0; i < d.length; i += 4 * 97) { s += d[i] + d[i + 1] + d[i + 2]; n += 3; } return s / n; }""")
        ok(lum > 25, f"l'aperçu montre l'image (luminosité moyenne {lum:.0f})")
        page.screenshot(path=str(TMP / "bureau-1440.png"))

        print("Export")
        page.click("#btn-exporter")
        page.wait_for_selector("#dlg-export[open]")
        ok(page.is_disabled('input[name="qualite"][value="2160"]'), "la 4K est réservée à Pro")
        ok(page.is_disabled('input[name="cadence"][value="60"]'), "60 images/s réservé à Pro")
        ok(page.is_checked("#export-filigrane") and page.is_disabled("#export-filigrane"), "le filigrane est imposé en gratuit")
        page.click('#export-qualite label:has(input[value="720"])')
        page.screenshot(path=str(TMP / "export-reglages.png"))
        page.click("#export-lancer")
        page.wait_for_function("() => !document.getElementById('export-fini').hidden || !document.getElementById('export-reglages').hidden", timeout=240000)
        fini = page.is_visible("#export-fini")
        ok(fini, "l'export se termine" + ("" if fini else f" ; message : {page.inner_text('#export-infos')}"))
        if fini:
            page.screenshot(path=str(TMP / "export-fini.png"))
            sortie = TMP / "export.mp4"
            sortie.write_bytes(base64.b64decode(page.evaluate(LIRE_BLOB)))
            info = json.loads(subprocess.run([FFPROBE, "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height:format=duration",
                                              "-of", "json", str(sortie)], capture_output=True, text=True, check=True).stdout)
            v = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
            s = next((s for s in info["streams"] if s["codec_type"] == "audio"), {})
            d = float(info["format"]["duration"])
            ok(v.get("codec_name") == "h264" and v.get("width") == 720 and v.get("height") == 1280, f"vidéo H.264 720×1280 ({v.get('codec_name')} {v.get('width')}×{v.get('height')})")
            ok(s.get("codec_name") in ("aac", "opus"), f"piste son présente ({s.get('codec_name')})")
            ok(abs(d - 8) < 0.3, f"durée du fichier {d:.2f} s (attendu 8)")
            vol = subprocess.run([FFMPEG, "-ss", "0.5", "-t", "1", "-i", str(sortie), "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
            maxv = next((float(l.split(":")[1].split()[0]) for l in vol.splitlines() if "max_volume" in l), -99)
            ok(maxv > -30, f"le son est audible ({maxv:.1f} dB au plus fort)")
            from PIL import Image
            img = TMP / "image-0_5.png"
            ff("-ss", "0.5", "-i", str(sortie), "-frames:v", "1", str(img))
            im = Image.open(img).convert("RGB")
            octets = im.resize((36, 64)).tobytes()
            moy = sum(octets) / len(octets)
            ok(moy > 25, f"l'image exportée n'est pas noire ({moy:.0f})")
            l, h = im.size
            coin = im.crop((int(l * 0.6), int(h * 0.92), l, h)).tobytes()
            jaunes = sum(1 for i in range(0, len(coin), 3) if coin[i] > 200 and coin[i + 1] > 160 and coin[i + 2] < 120)
            ok(jaunes > 20, f"le filigrane LA BOBINE est en bas à droite ({jaunes} pixels jaunes)")
        page.click("#export-retour" if fini else "#export-fermer")

        print("Sauvegarde")
        page.wait_for_timeout(900)
        page.reload()
        page.wait_for_selector("#editeur:not([hidden])")
        page.wait_for_function("() => window.__labobine.p && window.__labobine.p.pistes[0].clips.length === 4", timeout=15000)
        ok(True, "après rechargement, le projet rouvre avec ses 4 clips")
        ok("Bonjour Cotonou" in etat()["textes"], "et son texte")
        page.click("#btn-retour")
        page.wait_for_selector(".carte-projet")
        ok(page.locator(".carte-projet").count() == 1, "le projet apparaît à l'accueil")
        page.click('.carte-projet [data-action="supprimer"]')
        page.wait_for_function("() => !document.querySelector('.carte-projet')", timeout=5000)
        ok(page.locator(".carte-projet").count() == 0, "supprimer retire le projet")
        page.click("#toast-action")
        page.wait_for_selector(".carte-projet")
        ok(page.locator(".carte-projet").count() == 1, "« Annuler » le fait revenir")

        print("Téléphone (390 px)")
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path=str(TMP / "accueil-390.png"), full_page=True)
        page.click('.carte-projet [data-action="ouvrir"]')
        page.wait_for_selector("#editeur:not([hidden])")
        page.wait_for_timeout(700)
        deborde = page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth + 1")
        ok(not deborde, "pas de défilement horizontal de la page sur téléphone")
        ok(page.is_visible(".barre-mobile"), "la barre d'outils du bas s'affiche")
        page.screenshot(path=str(TMP / "editeur-390.png"))
        page.click('.barre-mobile [data-onglet-cible="texte"]')
        page.wait_for_timeout(400)
        ok(page.evaluate("() => document.getElementById('biblio').classList.contains('ouvert')"), "la feuille Texte s'ouvre")
        page.screenshot(path=str(TMP / "editeur-390-texte.png"))

        nav.close()
    srv.shutdown()
    utiles = [x for x in erreurs if "favicon" not in x]
    ok(not utiles, "aucune erreur dans la console" + ("" if not utiles else " : " + " | ".join(utiles[:5])))
    print(f"\n{verts} verts, {len(rouges)} rouges · captures dans {TMP}")
    sys.exit(1 if rouges else 0)


if __name__ == "__main__":
    main()

"""QC de LA BOBINE : le parcours complet dans un vrai Chrome, puis l'examen du MP4 exporté.

    python labobine/_qc.py            (sortie 1 si un contrôle échoue)
    python labobine/_qc.py --sans-ia  (saute Whisper et MediaPipe : PC à court de mémoire)

Commence par les contrôles sans navigateur (_qc_modele.mjs : modèle, rythme, GIF, LUT).

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

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
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
    a, b, photo, son, vert = TMP / "a.mp4", TMP / "b.mp4", TMP / "photo.png", TMP / "son.m4a", TMP / "vert.mp4"
    bruit = TMP / "bruit.wav"
    parole = TMP / "parole.wav"
    if not parole.exists():
        script = ("Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                  "$s.SelectVoice('Microsoft Hortense Desktop'); $s.Rate = -1; "
                  f"$s.SetOutputToWaveFile('{parole}'); $s.Speak('Bonjour Cotonou. Bienvenue dans la bobine, le montage vidéo pour tout le monde.'); $s.Dispose()")
        subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True)
    if not bruit.exists():
        ff("-f", "lavfi", "-i", "sine=frequency=500:duration=3", "-f", "lavfi", "-i", "anoisesrc=color=white:amplitude=0.08:duration=3",
           "-filter_complex", "amix=inputs=2:normalize=0", str(bruit))
    if not vert.exists():
        ff("-f", "lavfi", "-i", "color=c=0x00d000:size=640x360:rate=30:duration=2", "-vf", "drawbox=x=220:y=110:w=200:h=140:color=red@1:t=fill",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", str(vert))
    if not a.exists():
        ff("-f", "lavfi", "-i", "testsrc2=size=640x360:rate=30:duration=3", "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(a))
        ff("-f", "lavfi", "-i", "smptebars=size=480x270:rate=30:duration=2", "-f", "lavfi", "-i", "sine=frequency=880:duration=2",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(b))
        ff("-f", "lavfi", "-i", "color=c=0x3b7ddd:size=800x600:d=1", "-frames:v", "1", str(photo))
        ff("-f", "lavfi", "-i", "sine=frequency=330:duration=4", "-c:a", "aac", str(son))
    return a, b, photo, son, vert, bruit, parole


def medias_vague2bis():
    """Une piste de clics à 120 BPM (8 s) et une LUT .cube qui inverse les couleurs."""
    import math
    import struct
    import wave
    clics, lut, fondu = TMP / "clics.wav", TMP / "inverse.cube", TMP / "fondu.mp4"
    if not fondu.exists():
        ff("-f", "lavfi", "-i", "color=c=white:size=320x180:rate=30:duration=2", "-vf", "fade=t=in:st=0:d=2",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", str(fondu))
    if not clics.exists():
        sr = 44100
        x = [0.03 * math.sin(2 * math.pi * 220 * i / sr) for i in range(8 * sr)]
        t = 0.25
        while t < 7.9:
            i0 = int(t * sr)
            for k in range(int(0.03 * sr)):
                x[i0 + k] += 0.7 * math.sin(2 * math.pi * 1200 * k / sr) * math.exp(-k / (0.004 * sr)) + 0.5 * math.sin(2 * math.pi * 60 * k / sr) * math.exp(-k / (0.02 * sr))
            t += 0.5
        with wave.open(str(clics), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 32000)) for v in x))
    if not lut.exists():
        n = 17
        lignes = ['TITLE "Inverse"', f"LUT_3D_SIZE {n}"]
        for bl in range(n):
            for g in range(n):
                for r in range(n):
                    lignes.append(f"{1 - r / (n - 1):.6f} {1 - g / (n - 1):.6f} {1 - bl / (n - 1):.6f}")
        lut.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return clics, lut, fondu


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
  const fin = c => c.debut + (['texte', 'sticker', 'effet'].includes(c.genre) ? c.duree : (c.sortie - c.entree) / (c.vitesse || 1));
  return { pistes: p.pistes.map(t => ({ genre: t.genre, n: t.clips.length })), principale: p.pistes[0].clips.map(c => c.id),
    duree: Math.max(0, ...p.pistes.flatMap(t => t.clips.map(fin))), sel: a.selection,
    textes: p.pistes.filter(t => t.genre === 'texte').flatMap(t => t.clips.map(c => c.texte)) }; }"""

LIRE_BLOB = """async () => { const b = window.__labobine.dernierExport.blob; const u = new Uint8Array(await b.arrayBuffer());
  let s = ''; for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); return btoa(s); }"""


def nb(etat, genre):
    return sum(t["n"] for t in etat["pistes"] if t["genre"] == genre)


def main():
    print("Contrôles sans navigateur (modèle, rythme, GIF, LUT)")
    r = subprocess.run(["node", str(ICI / "_qc_modele.mjs")], capture_output=True, text=True, encoding="utf-8")
    fin = [l for l in r.stdout.strip().splitlines() if "verts" in l]
    ok(r.returncode == 0, f"_qc_modele.mjs : {fin[-1] if fin else r.stderr.strip()[:200]}")
    a, b, photo, son, vert, bruit, parole = medias_essai()
    clics, lut, fondu = medias_vague2bis()
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

        print("Vague 2 : images clés, couleur, fond vert, figer, détacher, vitesse")
        page.evaluate("() => { const a = window.__labobine; a.selectionner(a.p.pistes[0].clips[0].id); a.allerA(0.1); }")
        page.wait_for_timeout(400)
        page.click('#corps-inspecteur [data-cle="cx"]')
        page.evaluate("() => window.__labobine.allerA(0.9)")
        page.wait_for_timeout(400)
        page.evaluate("""() => { const el = document.querySelector('#corps-inspecteur input[data-k="cx"]'); el.value = 0.85;
          el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); }""")
        n_cles = page.evaluate("() => (window.__labobine.p.pistes[0].clips[0].cles.cx || []).length")
        ok(n_cles == 2, f"deux images clés sur la position X ({n_cles})")
        ok(page.locator("#pistes .losange").count() >= 2, "les losanges des images clés apparaissent sur la frise")
        pos = lambda t: page.evaluate(f"""async () => {{ const a = window.__labobine; a.allerA({t}); await new Promise(r => setTimeout(r, 500));
          return a.lecteur.cadres[a.p.pistes[0].clips[0].id].x / a.lecteur.W; }}""")
        x1, x2 = pos(0.1), pos(0.9)
        ok(abs(x1 - 0.5) < 0.02 and abs(x2 - 0.85) < 0.02, f"le clip glisse d'une clé à l'autre (X {x1:.2f} puis {x2:.2f})")

        page.click('#corps-inspecteur [data-action="filtre"][data-v="nb"]')
        page.evaluate("() => window.__labobine.allerA(0.5)")
        page.wait_for_timeout(700)
        sat = page.evaluate("""() => { const c = document.getElementById('toile'), x = c.getContext('2d');
          const d = x.getImageData(Math.round(c.width / 2) - 40, Math.round(c.height / 2) - 40, 80, 80).data; let s = 0, n = 0;
          for (let i = 0; i < d.length; i += 4) { s += Math.abs(d[i] - d[i + 1]) + Math.abs(d[i + 1] - d[i + 2]); n++; } return s / n; }""")
        ok(page.evaluate("() => window.__labobine.p.pistes[0].clips[0].filtre.nom") == "nb" and sat < 12, f"filtre « Noir et blanc » appliqué (écart de couleur {sat:.1f})")

        page.click('[data-onglet="medias"]')
        page.evaluate("() => window.__labobine.allerA(0.5)")
        page.set_input_files("#entree-fichiers", [str(vert)])
        page.wait_for_function("() => window.__labobine.p.medias.length === 5", timeout=20000)
        page.locator("#grille-medias [data-superposer]").last.click()
        page.wait_for_timeout(700)
        verts_px = lambda: page.evaluate("""() => { const c = document.getElementById('toile'); const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
          let v = 0, r = 0; for (let i = 0; i < d.length; i += 16) { if (d[i + 1] > 150 && d[i] < 90 && d[i + 2] < 90) v++; if (d[i] > 200 && d[i + 1] < 70 && d[i + 2] < 70) r++; } return [v, r]; }""")
        avant, _ = verts_px()
        page.click('#corps-inspecteur summary:text-is("Fond vert")')
        page.check('#corps-inspecteur [data-k="chroma.actif"]')
        page.wait_for_timeout(500)
        apres, px_rouges = verts_px()
        ok(avant > 500 and apres < avant * 0.05 and px_rouges > 50, f"fond vert retiré (pixels verts {avant} puis {apres}, le carré rouge reste : {px_rouges})")

        page.evaluate("() => { const a = window.__labobine; a.selectionner(a.p.pistes[0].clips[1].id); a.allerA(2); }")
        page.wait_for_timeout(500)
        d0 = etat()["duree"]
        page.click('#corps-inspecteur [data-action="figer"]')
        page.wait_for_function("() => window.__labobine.p.pistes[0].clips.some(c => c.genre === 'image' && c.media && window.__labobine.medias.get(c.media).nom.startsWith('Image figée'))", timeout=15000)
        ok(abs(etat()["duree"] - d0 - 3) < 0.05, f"figer l'image ajoute 3 s ({d0:.2f} puis {etat()['duree']:.2f})")

        page.evaluate("() => { const a = window.__labobine; a.selectionner(a.p.pistes[0].clips[0].id); a.allerA(0.5); }")
        page.wait_for_timeout(300)
        n_sons = nb(etat(), "audio")
        page.click('#corps-inspecteur [data-action="detacher"]')
        ok(nb(etat(), "audio") == n_sons + 1 and page.evaluate("() => window.__labobine.p.pistes[0].clips[0].muet"), "détacher le son : nouveau clip son, vidéo muette")

        page.evaluate("() => { const a = window.__labobine; const c = a.p.pistes[0].clips.find(x => x.genre === 'video' && !x.muet); a.selectionner(c.id); }")
        page.wait_for_timeout(300)
        d1 = etat()["duree"]
        page.click('#corps-inspecteur [data-action="vitesse"][data-v="2"]')
        ok(etat()["duree"] < d1 - 0.2, f"vitesse 2× raccourcit le montage ({d1:.2f} puis {etat()['duree']:.2f})")
        page.evaluate("() => { const a = window.__labobine; a.selectionner(null); a.allerA(0.5); }")
        page.wait_for_timeout(500)
        page.screenshot(path=str(TMP / "vague2-1440.png"))

        if "--sans-ia" in sys.argv:
            print("Vague 3 : sautée (--sans-ia, pour un PC à court de mémoire)")
        else:
            print("Vague 3 : IA sur l'appareil")
            lumi = """() => { const c = document.getElementById('toile'); const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
              let s = 0, n = 0; for (let i = 0; i < d.length; i += 4 * 13) { s += d[i] + d[i + 1] + d[i + 2]; n += 3; } return s / n; }"""
            page.evaluate("() => { const a = window.__labobine; const c = a.p.pistes[0].clips[0]; a.selectionner(c.id); a.allerA(0.3); }")
            page.wait_for_timeout(700)
            avant = page.evaluate(lumi)
            page.check('#corps-inspecteur [data-k="detourage"]')
            page.wait_for_function("() => window.__labobine.ia.iaPrete()", timeout=180000)
            page.evaluate("() => window.__labobine.allerA(0.3)")
            page.wait_for_timeout(1200)
            apres = page.evaluate(lumi)
            ok(apres < avant * 0.7, f"détourage : le décor sans personne disparaît (luminosité {avant:.0f} puis {apres:.0f})")

            page.evaluate("() => { const a = window.__labobine; const c = a.p.pistes[0].clips.find(x => x.genre === 'video' && !x.muet) || a.p.pistes[0].clips.find(x => x.genre === 'video'); a.selectionner(c.id); }")
            page.wait_for_timeout(300)
            page.click('#corps-inspecteur [data-action="suivre-visages"]')
            page.wait_for_function("() => window.__labobine.dernierSuivi", timeout=180000)
            suivi = page.evaluate("() => window.__labobine.dernierSuivi")
            ok("erreur" not in suivi and suivi.get("images", 0) >= 2, f"détecteur de visages : {suivi.get('images')} images analysées, {suivi.get('visages')} visage(s) (la mire n'en a pas)")

            page.click('[data-onglet="son"]')
            page.evaluate("() => window.__labobine.allerA(0)")
            page.set_input_files("#entree-sons", [str(bruit)])
            page.wait_for_function("() => [...window.__labobine.medias.values()].some(m => m.nom === 'bruit.wav')", timeout=20000)
            page.evaluate("() => { const a = window.__labobine; const id = [...a.medias.values()].find(m => m.nom === 'bruit.wav').id; const c = a.p.pistes.flatMap(t => t.clips).find(x => x.media === id); a.selectionner(c.id); }")
            page.wait_for_timeout(300)
            page.click('#corps-inspecteur [data-action="debruiter"]')
            page.wait_for_function("() => [...window.__labobine.medias.values()].some(m => m.nom.includes('(sans bruit)'))", timeout=120000)
            branche = page.evaluate("() => { const a = window.__labobine; const m = [...a.medias.values()].find(x => x.nom.includes('(sans bruit)')); return a.p.pistes.flatMap(t => t.clips).some(c => c.media === m.id); }")
            ok(branche, "réduction du bruit : le son nettoyé remplace l'original sur la frise")

            print("Sous-titres automatiques (Whisper dans le navigateur)")
            page.click('[data-onglet="son"]')
            page.evaluate("() => window.__labobine.allerA(0)")
            page.set_input_files("#entree-sons", [str(parole)])
            page.wait_for_function("() => [...window.__labobine.medias.values()].some(m => m.nom === 'parole.wav')", timeout=20000)
            page.evaluate("""() => { const a = window.__labobine; a.modeSousTitres = 'rapide';
              const id = [...a.medias.values()].find(m => m.nom === 'parole.wav').id;
              a.selectionner(a.p.pistes.flatMap(t => t.clips).find(x => x.media === id).id); }""")
            page.wait_for_timeout(300)
            page.click('#corps-inspecteur [data-action="sous-titres"]')
            page.wait_for_function("() => window.__labobine.derniersSousTitres", timeout=600000)
            st = page.evaluate("() => window.__labobine.derniersSousTitres")
            texte = " ".join(st).lower() if isinstance(st, list) else str(st)
            ok(isinstance(st, list) and ("bonjour" in texte or "cotonou" in texte), f"sous-titres reconnus : « {texte[:80]} »")
            n_legendes = page.evaluate("() => window.__labobine.p.pistes.filter(t => t.genre === 'texte').flatMap(t => t.clips).length")
            ok(isinstance(st, list) and n_legendes >= len(st) + 1, f"{len(st) if isinstance(st, list) else 0} légendes posées sur la frise")
        print("Vague 2 bis : LUT, lecture à l'envers, rythme, stickers, effets")
        page.click('[data-onglet="medias"]')
        pixel = lambda fx, fy: page.evaluate(f"""() => {{ const c = document.getElementById('toile'); const x = Math.round(c.width * {fx}), y = Math.round(c.height * {fy});
          const d = c.getContext('2d').getImageData(x - 3, y - 3, 7, 7).data; const m = [0, 0, 0]; for (let i = 0; i < d.length; i += 4) for (let k = 0; k < 3; k++) m[k] += d[i + k] / 49; return m.map(Math.round); }}""")
        t_photo = page.evaluate("""() => { const a = window.__labobine; const c = a.p.pistes[0].clips.find(x => x.media && a.medias.get(x.media).nom === 'photo.png');
          a.selectionner(c.id); a.allerA(c.debut + 0.5); return c.debut + 0.5; }""")
        page.wait_for_timeout(600)
        avant_lut = pixel(0.3, 0.3)
        with page.expect_file_chooser() as choix:
            page.click('#corps-inspecteur [data-action="importer-lut"]')
        choix.value.set_files(str(lut))
        page.wait_for_function("() => { const a = window.__labobine; return a.p.pistes[0].clips.some(c => c.lut && c.lut.media); }", timeout=15000)
        page.evaluate(f"() => window.__labobine.allerA({t_photo})")
        page.wait_for_timeout(600)
        apres_lut = pixel(0.3, 0.3)
        attendu_lut = [255 - v for v in avant_lut]
        ecart = max(abs(x - y) for x, y in zip(apres_lut, attendu_lut))
        ok(ecart <= 12, f"LUT .cube appliquée par le moteur : {avant_lut} devient {apres_lut} (attendu {attendu_lut})")
        ok(page.evaluate("() => document.querySelectorAll('#grille-medias .carte-media').length") == page.evaluate("() => [...window.__labobine.medias.values()].filter(m => m.type === 'video' || m.type === 'image').length"),
           "la LUT ne se mélange pas aux vidéos et photos de la bibliothèque")

        # une vidéo qui va du noir au blanc : à l'envers, elle doit commencer blanche
        page.set_input_files("#entree-fichiers", [str(fondu)])
        page.wait_for_function("() => [...window.__labobine.medias.values()].some(m => m.nom === 'fondu.mp4')", timeout=20000)
        page.evaluate("() => window.__labobine.allerA(0)")
        page.locator("#grille-medias [data-ajouter]").last.click()
        page.wait_for_timeout(400)
        info = page.evaluate("""() => { const a = window.__labobine; const c = a.trouver(a.selection).clip;
          return { id: c.id, debut: c.debut, fin: c.debut + (c.sortie - c.entree) / (c.vitesse || 1), media: c.media, nom: a.medias.get(c.media).nom }; }""")
        centre = lambda: page.evaluate("""() => { const c = document.getElementById('toile'); const d = c.getContext('2d').getImageData(Math.round(c.width / 2) - 10, Math.round(c.height / 2) - 10, 20, 20).data;
          let s = 0; for (let i = 0; i < d.length; i += 4) s += d[i] + d[i + 1] + d[i + 2]; return s / 400 / 3; }""")
        aller = lambda t: (page.evaluate(f"() => window.__labobine.allerA({t})"), page.wait_for_timeout(700))
        aller(info["debut"] + 0.1)
        debut_avant = centre()
        page.click('#corps-inspecteur [data-action="inverser"]')
        page.wait_for_function("() => window.__labobine.dernierInverse", timeout=180000)
        inv = page.evaluate("() => window.__labobine.dernierInverse")
        ok("erreur" not in inv and info["nom"] == "fondu.mp4", "lire à l'envers : la vidéo est refaite" + (f" ({inv})" if "erreur" in inv else f" ({inv['duree']:.2f} s)"))
        aller(info["debut"] + 0.1)
        debut_apres = centre()
        ok(debut_avant < 40 and debut_apres > 200, f"à l'envers, le fondu au blanc commence blanc (début {debut_avant:.0f} puis {debut_apres:.0f})")
        page.click('#corps-inspecteur [data-action="inverser"]')
        ok(page.evaluate(f"() => {{ const c = window.__labobine.trouver('{info['id']}').clip; return !c.inverse && c.media === '{info['media']}'; }}"), "« Remettre à l'endroit » rend le média d'origine")
        page.keyboard.press("Control+z")
        ok(page.evaluate(f"() => !!window.__labobine.trouver('{info['id']}').clip.inverse"), "et « Annuler » remet la lecture à l'envers")

        page.click('[data-onglet="son"]')
        page.evaluate("() => window.__labobine.allerA(0)")
        page.set_input_files("#entree-sons", [str(clics)])
        page.wait_for_function("() => [...window.__labobine.medias.values()].some(m => m.nom === 'clics.wav')", timeout=20000)
        page.evaluate("""() => { const a = window.__labobine; const id = [...a.medias.values()].find(m => m.nom === 'clics.wav').id;
          a.selectionner(a.p.pistes.flatMap(t => t.clips).find(x => x.media === id).id); }""")
        page.wait_for_timeout(300)
        page.click('#corps-inspecteur [data-action="rythme"]')
        page.wait_for_function("() => window.__labobine.dernierRythme", timeout=60000)
        ry = page.evaluate("() => window.__labobine.dernierRythme")
        ok("erreur" not in ry and abs(ry.get("bpm", 0) - 120) < 2 and 14 <= len(ry.get("temps", [])) <= 17, f"rythme trouvé : {ry.get('bpm')} BPM, {len(ry.get('temps', []))} temps (attendu 120 et 16)")
        ok(page.locator("#pistes .temps-rythme").count() >= 14 and page.locator("#regle .temps").count() >= 14, "les temps s'affichent sur le son et sur la règle")
        page.click('#corps-inspecteur [data-action="caler"][data-v="2"]')
        cale = page.evaluate("""() => { const a = window.__labobine; const p = a.p; const fin = c => c.debut + (c.sortie - c.entree) / (c.vitesse || 1);
          const pts = []; for (const t of p.pistes) for (const c of t.clips) if (c.rythme) for (const x of c.rythme) if (x >= c.entree && x < c.sortie) pts.push(c.debut + (x - c.entree) / (c.vitesse || 1));
          const photos = p.pistes[0].clips.filter(c => c.genre === 'image'); return { n: photos.length, sur: photos.filter(c => pts.some(x => Math.abs(x - fin(c)) < 1e-3)).length }; }""")
        ok(cale["n"] >= 1 and cale["sur"] == cale["n"], f"« Caler tous les 2 temps » : {cale['sur']} photo(s) sur {cale['n']} finissent pile sur un temps")
        page.evaluate("() => { const a = window.__labobine; a.selectionner(null); a.allerA(1.3); }")
        page.keyboard.press("m")
        ok(page.evaluate("() => window.__labobine.p.marqueurs.length") == 1 and page.locator("#regle .marqueur").count() == 1, "la touche M pose un marqueur sur la règle")
        page.keyboard.press("m")
        ok(page.evaluate("() => window.__labobine.p.marqueurs.length") == 0, "un second M le retire")

        t_deco = page.evaluate("() => { const a = window.__labobine; const c = a.p.pistes[0].clips[0]; a.allerA(c.debut + 0.05); return c.debut + 0.05; }")
        page.click('[data-onglet="stickers"]')
        ok(page.locator("#grille-stickers .vignette-outil img[src^='data:image']").count() >= 15, "les vignettes des stickers sont dessinées par le moteur")
        page.click('#grille-stickers [data-sticker="etoile"]')
        page.wait_for_selector('#corps-inspecteur [data-forme="etoile"][aria-pressed="true"]')
        page.evaluate(f"() => window.__labobine.allerA({t_deco + 0.8})")
        page.wait_for_timeout(600)
        jaunes_etoile = page.evaluate("""() => { const c = document.getElementById('toile'); const d = c.getContext('2d').getImageData(Math.round(c.width / 2) - 30, Math.round(c.height / 2) - 30, 60, 60).data;
          let n = 0; for (let i = 0; i < d.length; i += 4) if (d[i] > 200 && d[i + 1] > 170 && d[i + 2] < 120) n++; return n; }""")
        ok(jaunes_etoile > 1500, f"le sticker étoile est dessiné au centre de l'aperçu ({jaunes_etoile} pixels jaunes)")
        ok(page.locator("#pistes .clip.g-sticker").count() == 1, "il a sa piste sur la frise")
        page.click('#corps-inspecteur [data-forme="prix"]')
        page.fill('#corps-inspecteur input[data-k="texte"]', "2 000 F")
        ok(page.evaluate("() => { const a = window.__labobine; const c = a.trouver(a.selection).clip; return c.forme === 'prix' && c.texte === '2 000 F'; }"), "le sticker devient une étiquette de prix, au texte modifiable")
        ok(bool(page.evaluate("() => { const a = window.__labobine; return a.lecteur.cadres[a.selection]; }")), "il a un cadre sur l'aperçu : on peut le glisser et le pincer")
        page.screenshot(path=str(TMP / "sticker-1440.png"))

        page.evaluate(f"() => window.__labobine.allerA({t_deco + 0.8})")
        page.wait_for_timeout(500)
        haut = lambda: page.evaluate("""() => { const c = document.getElementById('toile'); const d = c.getContext('2d').getImageData(0, 0, c.width, Math.max(2, Math.round(c.height * 0.04))).data;
          let s = 0; for (let i = 0; i < d.length; i += 4) s += d[i] + d[i + 1] + d[i + 2]; return s / (d.length / 4) / 3; }""")
        coin = lambda: page.evaluate("""() => { const c = document.getElementById('toile'); const d = c.getContext('2d').getImageData(2, Math.round(c.height * 0.2), 20, 20).data;
          let s = 0; for (let i = 0; i < d.length; i += 4) s += d[i] + d[i + 1] + d[i + 2]; return s / 400 / 3; }""")
        # un projet vertical garde des bandes noires au-dessus d'une vidéo paysage : un fond gris rend l'effet mesurable
        page.evaluate(f"() => {{ const a = window.__labobine; a.modifier(p => {{ p.fond.couleur = '#808080'; }}); a.allerA({t_deco + 1.5}); }}")
        page.wait_for_timeout(600)
        haut_avant, coin_avant = haut(), coin()
        # l'effet se pose à 0,85 s ; les bandes cinéma entrent en 0,5 s : on mesure 0,65 s plus loin
        page.evaluate(f"() => window.__labobine.allerA({t_deco + 0.8})")
        page.wait_for_timeout(300)
        page.click('[data-onglet="effets"]')
        ok(page.locator("#grille-effets .vignette-outil img[src^='data:image']").count() >= 15, "les vignettes des effets sont dessinées par le moteur")
        page.click('#grille-effets [data-effet="cinema"]')
        page.evaluate(f"() => window.__labobine.allerA({t_deco + 1.5})")
        page.wait_for_timeout(600)
        haut_apres = haut()
        ok(haut_apres < 2 and haut_avant > 8, f"effet « Bandes cinéma » : le haut de l'image devient noir ({haut_avant:.0f} puis {haut_apres:.0f})")
        page.click('#corps-inspecteur [data-change-effet="vignettage"]')
        page.evaluate(f"() => window.__labobine.allerA({t_deco + 1.5})")
        page.wait_for_timeout(600)
        coin_apres = coin()
        ok(coin_apres < coin_avant * 0.75, f"effet « Vignettage » : le bord s'assombrit ({coin_avant:.0f} puis {coin_apres:.0f})")
        ok(page.evaluate("() => { const a = window.__labobine; const c = a.trouver(a.selection).clip; return c.genre === 'effet' && c.effet === 'vignettage'; }"), "l'effet change sans changer de clip")
        page.evaluate(f"() => {{ const a = window.__labobine; a.selectionner(null); a.allerA({t_deco + 1.5}); }}")
        page.wait_for_timeout(500)
        page.screenshot(path=str(TMP / "vague2bis-1440.png"))
        page.evaluate("() => window.__labobine.modifier(p => { p.fond.couleur = '#000000'; })")
        attendu = etat()["duree"]
        t_image = page.evaluate("() => window.__labobine.p.pistes[0].clips[1].debut + 0.2")
        n_principale = len(etat()["principale"])

        print("Export")
        page.click("#btn-exporter")
        page.wait_for_selector("#dlg-export[open]")
        ok(page.is_disabled('input[name="qualite"][value="2160"]'), "la 4K est réservée à Pro")
        ok(page.is_disabled('input[name="cadence"][value="60"]'), "60 images/s réservé à Pro")
        ok(page.is_checked("#export-filigrane") and page.is_disabled("#export-filigrane"), "le filigrane est imposé en gratuit")
        page.click("#export-couverture")
        page.wait_for_function("() => window.__labobine.derniereCouverture", timeout=15000)
        ok(page.evaluate("() => window.__labobine.derniereCouverture.size") > 20000, "image de couverture PNG fabriquée")
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
            ok(abs(d - attendu) < 0.3, f"durée du fichier {d:.2f} s (attendu {attendu:.2f})")
            vol = subprocess.run([FFMPEG, "-ss", "0.5", "-t", "1", "-i", str(sortie), "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
            maxv = next((float(l.split(":")[1].split()[0]) for l in vol.splitlines() if "max_volume" in l), -99)
            ok(maxv > -30, f"le son est audible ({maxv:.1f} dB au plus fort)")
            import re
            eb = subprocess.run([FFMPEG, "-nostats", "-i", str(sortie), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
            mesures = re.findall(r"I:\s+(-?[0-9.]+) LUFS", eb)
            lufs = float(mesures[-1]) if mesures else -99
            tout = subprocess.run([FFMPEG, "-i", str(sortie), "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
            crete = next((float(l.split(":")[1].split()[0]) for l in tout.splitlines() if "max_volume" in l), -99)
            # le moteur vise -14 LUFS mais ne pousse jamais la crête au-delà de -0,5 dBFS : un son très « piqué »
            # (des clics) s'arrête donc plus bas, et c'est voulu
            ok(abs(lufs + 14) < 1.0 or (lufs < -14 and crete > -1.5), f"volume harmonisé, mesuré par FFmpeg : {lufs} LUFS, crête {crete} dBFS (visé -14, ou crête au plafond de -0,5)")
            from PIL import Image
            img = TMP / "image-0_5.png"
            ff("-ss", f"{t_image:.2f}", "-i", str(sortie), "-frames:v", "1", str(img))
            im = Image.open(img).convert("RGB")
            octets = im.resize((36, 64)).tobytes()
            moy = sum(octets) / len(octets)
            ok(moy > 25, f"l'image exportée n'est pas noire ({moy:.0f})")
            l, h = im.size
            coin = im.crop((int(l * 0.6), int(h * 0.92), l, h)).tobytes()
            jaunes = sum(1 for i in range(0, len(coin), 3) if coin[i] > 200 and coin[i + 1] > 160 and coin[i + 2] < 120)
            ok(jaunes > 20, f"le filigrane LA BOBINE est en bas à droite ({jaunes} pixels jaunes)")
        page.click("#export-retour" if fini else "#export-fermer")

        print("Export en GIF et en son seul")
        page.click("#btn-exporter")
        page.wait_for_selector("#dlg-export[open]")
        page.click('#export-format label:has(input[value="gif"])')
        ok(page.is_visible("#export-opt-gif") and page.is_hidden("#export-opt-video"), "choisir « GIF animé » montre ses propres réglages")
        page.click('#export-taille-gif label:has(input[value="240"])')
        page.click('#export-cadence-gif label:has(input[value="10"])')
        page.click("#export-lancer")
        page.wait_for_function("() => !document.getElementById('export-fini').hidden || !document.getElementById('export-reglages').hidden", timeout=240000)
        fini_gif = page.is_visible("#export-fini")
        ok(fini_gif and page.is_visible("#export-gif"), "le GIF se termine et s'affiche" + ("" if fini_gif else f" ; message : {page.inner_text('#export-infos')}"))
        if fini_gif:
            from PIL import Image, ImageSequence
            g = TMP / "export.gif"
            g.write_bytes(base64.b64decode(page.evaluate(LIRE_BLOB)))
            im = Image.open(g)
            n_img = im.n_frames
            total = sum(f.info.get("duration", 0) for f in ImageSequence.Iterator(im))
            ok(im.size == (240, 426), f"GIF de 240 × 426 ({im.size[0]} × {im.size[1]})")
            ok(abs(n_img - attendu * 10) <= 2 and abs(total / 1000 - attendu) < 0.15, f"{n_img} images, {total / 1000:.2f} s (attendu {attendu:.2f} s à 10 i/s)")
            im.seek(0)
            premiere = im.convert("RGB")
            l, h = premiere.size
            coin_gif = premiere.crop((int(l * 0.55), int(h * 0.9), l, h)).tobytes()
            jaunes = sum(1 for i in range(0, len(coin_gif), 3) if coin_gif[i] > 190 and coin_gif[i + 1] > 150 and coin_gif[i + 2] < 130)
            ok(jaunes > 5, f"le filigrane est aussi sur le GIF gratuit ({jaunes} pixels jaunes)")
            ok(g.stat().st_size < 4 * 1048576, f"le GIF pèse {g.stat().st_size // 1024} Ko")
        page.click("#export-retour" if fini_gif else "#export-fermer")
        page.click("#btn-exporter")
        page.wait_for_selector("#dlg-export[open]")
        page.click('#export-format label:has(input[value="son"])')
        ok(page.is_hidden("#export-ligne-filigrane"), "« Son seul » : pas de filigrane à régler")
        page.click("#export-lancer")
        page.wait_for_function("() => !document.getElementById('export-fini').hidden || !document.getElementById('export-reglages').hidden", timeout=120000)
        fini_son = page.is_visible("#export-fini")
        ok(fini_son and page.is_visible("#export-audio"), "le son seul se termine" + ("" if fini_son else f" ; message : {page.inner_text('#export-infos')}"))
        if fini_son:
            a_son = TMP / "export-son.m4a"
            a_son.write_bytes(base64.b64decode(page.evaluate(LIRE_BLOB)))
            info_son = json.loads(subprocess.run([FFPROBE, "-v", "error", "-show_entries", "stream=codec_type,codec_name:format=duration", "-of", "json", str(a_son)],
                                                 capture_output=True, text=True, check=True).stdout)
            types = [x["codec_type"] for x in info_son["streams"]]
            ok(types == ["audio"] and info_son["streams"][0]["codec_name"] == "aac", f"fichier M4A, une seule piste son ({types}, {info_son['streams'][0].get('codec_name')})")
            ok(abs(float(info_son["format"]["duration"]) - attendu) < 0.3, f"durée du son {float(info_son['format']['duration']):.2f} s (attendu {attendu:.2f})")
        page.click("#export-retour" if fini_son else "#export-fermer")

        print("Sauvegarde")
        page.wait_for_timeout(900)
        page.reload()
        page.wait_for_selector("#editeur:not([hidden])")
        page.wait_for_function(f"() => window.__labobine.p && window.__labobine.p.pistes[0].clips.length === {n_principale}", timeout=15000)
        ok(page.evaluate("() => window.__labobine.p.pistes[0].clips.some(c => ((c.cles || {}).cx || []).length === 2)"), f"après rechargement, le projet rouvre avec ses {n_principale} clips et ses images clés")
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


        print("Vague 4 : le compte (sans serveur, sans e-mail envoyé)")
        if "export const OUVERT = true" in (ICI / "js" / "compte.js").read_text(encoding="utf-8"):
            print("  (interrupteur OUVERT dans le code : les comptes sont visibles pour tout le monde)")
        else:
            ok(page.locator("[data-ouvrir-compte]:visible").count() == 0, "interrupteur fermé : aucun bouton de compte n'apparaît")
        comptes = ctx.new_page()
        comptes.add_init_script("window.__labobineComptes = true")
        comptes.on("pageerror", lambda e: erreurs.append(str(e)))
        comptes.goto(url)
        comptes.wait_for_selector("#accueil:not([hidden])")
        ok(comptes.is_visible("[data-ouvrir-compte]") and comptes.inner_text("[data-ouvrir-compte]:visible") == "Se connecter", "interrupteur ouvert : « Se connecter » apparaît à l'accueil")
        comptes.click("[data-ouvrir-compte]:visible")
        comptes.wait_for_selector("#dlg-compte[open]")
        ok(comptes.is_visible("#compte-email") and comptes.is_hidden('[data-volet="compte"]'), "la fenêtre de connexion demande un e-mail")
        comptes.fill("#compte-email", "pas-une-adresse")
        comptes.click("#compte-envoyer")
        ok("pas l'air complète" in comptes.inner_text("#compte-message"), "une adresse incomplète est refusée avant tout envoi")
        comptes.set_viewport_size({"width": 390, "height": 844})
        comptes.screenshot(path=str(TMP / "compte-390.png"))
        comptes.close()
        print("Vidéo depuis un catalogue, lu à la source")
        r_cat = subprocess.run([sys.executable, str(ICI / "_catalogues.py")], capture_output=True, text=True, encoding="utf-8")
        ok(r_cat.returncode == 0, "les catalogues se relisent dans les sources des maisons" + ("" if r_cat.returncode == 0 else f" : {r_cat.stderr[-300:]}"))
        lire_cat = lambda slug: json.loads((ICI / "catalogues" / slug / "catalogue.json").read_text(encoding="utf-8"))
        cat_h, cat_b = lire_cat("hillary-m-styl"), lire_cat("au-braise-dor")
        vp = ctx.new_page()
        vp.on("console", lambda m: erreurs.append(m.text) if m.type == "error" else None)
        vp.on("pageerror", lambda e: erreurs.append(str(e)))
        vp.goto(url + "#catalogue/hillary-m-styl")
        vp.wait_for_selector("#dlg-catalogue[open] #cat-produits .carte-produit")
        n_cartes = vp.locator("#cat-produits .carte-produit").count()
        ok(n_cartes == len(cat_h["articles"]), f"le lien d'Hillary ouvre ses {n_cartes} articles ({len(cat_h['articles'])} dans le catalogue)")
        ok(cat_h["contact"] and vp.input_value("#cat-contact") == cat_h["contact"] and vp.input_value("#cat-maison") == cat_h["maison"], f"sa maison et son numéro viennent de sa fiche ({cat_h['contact']})")
        while vp.locator('#cat-produits .carte-produit[data-choisi="true"]').count() > 3:
            vp.locator('#cat-produits .carte-produit[data-choisi="true"] .choisir').last.click()
        attendus = [a_["prixCourt"] for a_ in cat_h["articles"] if a_["photo"]][:3]
        vp.screenshot(path=str(TMP / "catalogue-1440.png"))
        vp.click("#cat-fabriquer")
        vp.wait_for_function("() => window.__labobine.dernierCatalogue && window.__labobine.p && window.__labobine.p.id === window.__labobine.dernierCatalogue.id", timeout=60000)
        st = vp.evaluate("""() => { const p = window.__labobine.p; const tous = g => p.pistes.filter(t => t.genre === g).flatMap(t => t.clips);
          return { principale: p.pistes[0].clips.length, prix: tous('sticker').filter(c => c.forme === 'prix').sort((a, b) => a.debut - b.debut).map(c => c.texte),
            textes: tous('texte').map(c => c.texte), medias: p.medias.length, debut: p.pistes[0].clips[1].debut }; }""")
        ok(st["principale"] == 5, f"la vidéo est montée : ouverture, 3 pièces, fin ({st['principale']} plans)")
        ok(st["prix"] == attendus, f"les étiquettes portent les prix du site, tels quels ({' · '.join(st['prix'])})")
        ok(cat_h["contact"] in st["textes"] and cat_h["maison"] in st["textes"], "la vidéo s'ouvre sur la maison et finit sur son numéro")
        vp.evaluate(f"() => window.__labobine.allerA({st['debut'] + 1.0})")
        vp.wait_for_timeout(900)
        jaunes_prix = vp.evaluate("""() => { const c = document.getElementById('toile'); const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
          let n = 0; for (let i = 0; i < d.length; i += 16) if (d[i] > 200 && d[i + 1] > 170 && d[i + 2] < 120) n++; return n; }""")
        ok(jaunes_prix > 400, f"l'étiquette de prix est dessinée sur la pièce ({jaunes_prix} pixels jaunes)")
        vp.screenshot(path=str(TMP / "catalogue-video-1440.png"))
        vp.click("#btn-exporter")
        vp.click('#export-format label:has(input[value="gif"])')
        vp.click('#export-taille-gif label:has(input[value="240"])')
        vp.click('#export-cadence-gif label:has(input[value="10"])')
        vp.click("#export-lancer")
        vp.wait_for_function("() => !document.getElementById('export-fini').hidden || !document.getElementById('export-reglages').hidden", timeout=180000)
        ok(vp.is_visible("#export-fini"), "la vidéo d'Hillary s'exporte avec les vraies photos du catalogue" + ("" if vp.is_visible("#export-fini") else f" : {vp.inner_text('#export-infos')}"))
        vp.click("#export-retour" if vp.is_visible("#export-fini") else "#export-fermer")

        vp.evaluate("() => { location.hash = 'catalogue/au-braise-dor'; }")
        vp.wait_for_function(f"() => document.querySelectorAll('#cat-produits .carte-produit').length === {len(cat_b['articles'])}", timeout=15000)
        ok(vp.input_value("#cat-contact") == "" and cat_b["contact"] == "", "Au Braisé d'Or : sa fiche n'a pas de numéro, le champ reste vide (rien n'est deviné)")
        ok(vp.locator("#cat-categories button").count() == len(cat_b["categories"]) + 1, f"ses {len(cat_b['categories'])} rubriques se filtrent")
        ok(vp.locator("#cat-produits .choisir small").count() == sum(1 for a_ in cat_b["articles"] if not a_["photo"]), "un plat sans photo est annoncé « sans photo », jamais illustré par une image d'emprunt")
        vp.click("#cat-fermer")

        vp.click("#btn-retour")
        vp.wait_for_selector("#accueil:not([hidden])")
        produit2 = TMP / "produit2.png"
        if not produit2.exists():
            ff("-f", "lavfi", "-i", "color=c=0xd2452f:size=900x900:d=1", "-frames:v", "1", str(produit2))
        vp.click("#btn-catalogue")
        vp.wait_for_selector("#dlg-catalogue[open]")
        vp.set_input_files("#entree-produits", [str(photo), str(produit2)])
        vp.wait_for_function("() => document.querySelectorAll('#cat-produits .carte-produit').length === 2")
        vp.fill('#cat-produits [data-champ="nom"][data-i="0"]', "Pagne wax")
        vp.fill('#cat-produits [data-champ="prix"][data-i="0"]', "7 500 F")
        vp.fill('#cat-produits [data-champ="prix"][data-i="1"]', "12 000 F")
        vp.fill("#cat-maison", "Chez Afi")
        vp.click('#cat-modeles [data-modele="promo"]')
        vp.set_input_files("#entree-musique", [str(clics)])
        vp.wait_for_function("() => /BPM/.test(document.getElementById('cat-musique-nom').textContent)", timeout=60000)
        vp.click("#cat-fabriquer")
        vp.wait_for_function("() => window.__labobine.dernierCatalogue && window.__labobine.dernierCatalogue.maison === 'Chez Afi' && window.__labobine.p && window.__labobine.p.id === window.__labobine.dernierCatalogue.id", timeout=60000)
        mp = vp.evaluate("""() => { const a = window.__labobine; const p = a.p; const tous = g => p.pistes.filter(t => t.genre === g).flatMap(t => t.clips);
          const fin = c => c.debut + (c.sortie - c.entree) / (c.vitesse || 1); const son = tous('audio')[0];
          const pts = son.rythme.filter(x => x >= son.entree && x <= son.sortie + 1e-6).map(x => son.debut + (x - son.entree) / (son.vitesse || 1));
          return { n: p.pistes[0].clips.length, surTemps: p.pistes[0].clips.filter(c => pts.some(x => Math.abs(x - fin(c)) < 1e-3)).length,
            effets: tous('effet').map(c => c.effet).sort(), textes: tous('texte').map(c => c.texte) }; }""")
        ok(mp["n"] == 4 and mp["surTemps"] == 4, f"tes propres photos + une musique : {mp['n']} plans, {mp['surTemps']} finissent sur un temps")
        ok(mp["effets"] == ["battement", "flash"] and "7 500 F" in mp["textes"] and "Pagne wax" in mp["textes"], "le style Promo pose le prix en grand et bat sur la musique")
        vp.set_viewport_size({"width": 390, "height": 844})
        vp.click("#btn-retour")
        vp.wait_for_selector("#accueil:not([hidden])")
        vp.screenshot(path=str(TMP / "accueil-catalogue-390.png"), full_page=True)
        vp.evaluate("() => { location.hash = 'catalogue/hillary-m-styl'; }")
        vp.wait_for_selector("#dlg-catalogue[open] #cat-produits .carte-produit")
        vp.wait_for_timeout(500)
        deborde_dlg = vp.evaluate("() => { const d = document.getElementById('dlg-catalogue'); return d.scrollWidth > d.clientWidth + 1 || document.documentElement.scrollWidth > innerWidth + 1; }")
        ok(not deborde_dlg, "la fenêtre du catalogue tient sur 390 px")
        vp.screenshot(path=str(TMP / "catalogue-390.png"))
        vp.close()

        print("Téléphone (390 px)")
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path=str(TMP / "accueil-390.png"), full_page=True)
        page.click('.carte-projet [data-action="ouvrir"]')
        page.wait_for_selector("#editeur:not([hidden])")
        page.wait_for_timeout(700)
        deborde = page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth + 1")
        ok(not deborde, "pas de défilement horizontal de la page sur téléphone")
        ok(page.is_visible(".barre-mobile"), "la barre d'outils du bas s'affiche")
        coupes = page.evaluate("() => [...document.querySelectorAll('.barre-mobile button span')].filter(s => s.scrollWidth > s.parentElement.clientWidth + 1).map(s => s.textContent)")
        ok(page.locator(".barre-mobile button").count() == 6 and not coupes, "les 6 boutons du bas tiennent sur 390 px" + (f" (coupés : {coupes})" if coupes else ""))
        page.screenshot(path=str(TMP / "editeur-390.png"))
        page.click('.barre-mobile [data-onglet-cible="texte"]')
        page.wait_for_timeout(400)
        ok(page.evaluate("() => document.getElementById('biblio').classList.contains('ouvert')"), "la feuille Texte s'ouvre")
        page.screenshot(path=str(TMP / "editeur-390-texte.png"))
        page.click('.barre-mobile [data-onglet-cible="stickers"]')
        page.wait_for_timeout(400)
        page.screenshot(path=str(TMP / "editeur-390-stickers.png"))

        nav.close()
    srv.shutdown()
    # MediaPipe écrit ses informations de démarrage sur le canal des erreurs : on les écarte nommément
    utiles = [x for x in erreurs if "favicon" not in x and not x.startswith("INFO: Created TensorFlow Lite")]
    ok(not utiles, "aucune erreur dans la console" + ("" if not utiles else " : " + " | ".join(utiles[:5])))
    print(f"\n{verts} verts, {len(rouges)} rouges · captures dans {TMP}")
    sys.exit(1 if rouges else 0)


if __name__ == "__main__":
    main()

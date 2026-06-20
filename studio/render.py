# -*- coding: utf-8 -*-
"""
NEBULA Studio Quotidien — MOTEUR VIDÉO (gratuit, illimité).

Transforme un concept (storyboard) en vidéo verticale 1080x1920 de marque :
  - charge le gabarit kinetic.html avec window.CONCEPT
  - Playwright (Chromium) ENREGISTRE l'animation → .webm
  - si ffmpeg est présent → transcode en .mp4 (H.264, compatible partout)
  - capture aussi une affiche (poster.png)

Aucune dépendance payante. ffmpeg est optionnel en local ; en CI il est installé.
"""
import os, json, shutil, subprocess, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = (HERE / "templates" / "kinetic.html").resolve()

def _find_ffmpeg():
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    try:                                   # binaire ffmpeg embarqué (pip)
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None

def _to_mp4(webm, mp4):
    ff = _find_ffmpeg()
    if not ff:
        return False
    cmd = [ff, "-y", "-i", str(webm), "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30",
           "-movflags", "+faststart", "-an", str(mp4)]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return mp4.exists()
    except Exception as e:
        print("ffmpeg KO:", e)
        return False

def render(concept, out_dir):
    from playwright.sync_api import sync_playwright
    out_dir = pathlib.Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    viddir = out_dir / "_vid"; viddir.mkdir(exist_ok=True)
    poster = out_dir / "poster.png"
    webm = out_dir / "video.webm"
    mp4 = out_dir / "video.mp4"

    cjson = json.dumps(concept, ensure_ascii=False)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
        ctx = browser.new_context(
            viewport={"width": 1080, "height": 1920},
            device_scale_factor=1,
            record_video_dir=str(viddir),
            record_video_size={"width": 1080, "height": 1920},
        )
        page = ctx.new_page()
        page.add_init_script("window.CONCEPT = " + cjson + ";")
        page.goto(TEMPLATE.as_uri())
        # attendre que le gabarit annonce la durée totale, puis filmer jusqu'à la fin
        page.wait_for_function("window.__NEBULA_TOTAL > 0", timeout=20000)
        total = page.evaluate("window.__NEBULA_TOTAL")
        # affiche = la scène la plus percutante, pleinement révélée (signalée par le gabarit)
        try:
            page.wait_for_function("window.__POSTER_OK === true", timeout=15000)
            page.wait_for_timeout(120)
        except Exception:
            page.wait_for_timeout(int(total * 0.3))
        page.screenshot(path=str(poster))
        page.wait_for_function("window.__NEBULA_DONE === true", timeout=int(total) + 12000)
        page.wait_for_timeout(250)
        ctx.close()            # <- déclenche l'écriture du .webm
        browser.close()

    # récupérer le webm produit par Playwright (nom aléatoire) → video.webm
    vids = sorted(viddir.glob("*.webm"), key=lambda f: f.stat().st_mtime)
    if vids:
        if webm.exists():
            webm.unlink()
        shutil.move(str(vids[-1]), str(webm))
    shutil.rmtree(viddir, ignore_errors=True)

    result = {"poster": str(poster) if poster.exists() else None,
              "webm": str(webm) if webm.exists() else None, "mp4": None}
    if webm.exists() and _to_mp4(webm, mp4):
        result["mp4"] = str(mp4)
    result["video"] = result["mp4"] or result["webm"]
    return result

if __name__ == "__main__":
    import sys
    c = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else {}
    print(render(c, HERE / "out" / "_manual"))

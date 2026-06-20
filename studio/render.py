# -*- coding: utf-8 -*-
"""
NEBULA Studio Quotidien — MOTEUR VIDÉO (gratuit, illimité, FLUIDE).

Rendu DÉTERMINISTE image par image (≠ enregistrement temps réel) :
  - le gabarit expose __DURATION et __seek(t) ; aucune animation CSS.
  - on calcule chaque frame à un temps EXACT (t = i/fps) et on la capture en
    pleine résolution → vitesse parfaite, zéro ralenti, zéro frame perdue.
  - ffmpeg assemble la séquence PNG en MP4 1080×1920 (9:16), 30 i/s, H.264 net.

Le navigateur sans écran peut être lent : peu importe, on l'ATTEND frame par frame.
"""
import os, json, shutil, subprocess, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = (HERE / "templates" / "kinetic.html").resolve()
FPS = 30
W, H = 1080, 1920

def _find_ffmpeg():
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None

def render(concept, out_dir, fps=FPS):
    from playwright.sync_api import sync_playwright
    out_dir = pathlib.Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    frames = out_dir / "_frames"
    if frames.exists():
        shutil.rmtree(frames, ignore_errors=True)
    frames.mkdir(parents=True, exist_ok=True)
    poster = out_dir / "poster.png"
    mp4 = out_dir / "video.mp4"

    cjson = json.dumps(concept, ensure_ascii=False)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--force-color-profile=srgb", "--hide-scrollbars", "--disable-gpu"])
        ctx = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=1)
        page = ctx.new_page()
        page.add_init_script("window.CONCEPT = " + cjson + ";")
        # domcontentloaded : ne PAS bloquer sur le réseau (polices Google) → évite les timeouts
        page.goto(TEMPLATE.as_uri(), wait_until="domcontentloaded", timeout=45000)
        page.wait_for_function("window.__DURATION > 0", timeout=20000)
        try:
            page.wait_for_function("window.__FONTS_READY === true", timeout=9000)
        except Exception:
            pass
        total = page.evaluate("window.__DURATION")
        poster_t = page.evaluate("window.__POSTER_T")

        # affiche (scène la plus percutante, pleinement révélée)
        page.evaluate("window.__seek(%f)" % poster_t)
        page.screenshot(path=str(poster))

        # toutes les frames, à des temps exacts
        nframes = int(round(total / 1000.0 * fps))
        for f in range(nframes + 1):
            page.evaluate("window.__seek(%f)" % (f / fps * 1000.0))
            page.screenshot(path=str(frames / ("%05d.png" % f)))
        ctx.close(); browser.close()

    result = {"poster": str(poster) if poster.exists() else None,
              "mp4": None, "webm": None, "video": None}
    ff = _find_ffmpeg()
    if ff:
        cmd = [ff, "-y", "-framerate", str(fps), "-i", str(frames / "%05d.png"),
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17",
               "-preset", "medium", "-movflags", "+faststart", "-an", str(mp4)]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            if mp4.exists():
                result["mp4"] = result["video"] = str(mp4)
        except Exception as e:
            print("ffmpeg KO:", getattr(e, "stderr", b"")[-500:] if hasattr(e, "stderr") else e)
    shutil.rmtree(frames, ignore_errors=True)
    return result

if __name__ == "__main__":
    import sys
    c = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else {}
    print(render(c, HERE / "out" / "_manual"))

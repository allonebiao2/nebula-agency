# -*- coding: utf-8 -*-
"""
NEBULA Studio Quotidien — MOTEUR VIDÉO (gratuit, illimité, 4K @ 60 i/s, FLUIDE).

Rendu DÉTERMINISTE image par image (≠ enregistrement temps réel) :
  - le gabarit expose __DURATION et __seek(t) ; aucune animation CSS.
  - mise en page logique en 1080×1920, capturée en ×2 → 2160×3840 (4K) ;
  - chaque frame est calculée à un temps EXACT (t = i/60s) puis capturée
    (JPEG, rapide) → vitesse parfaite, zéro ralenti, zéro frame perdue ;
  - ffmpeg assemble en MP4 4K vertical (9:16), 60 i/s, H.264 net.

Le vrai logo NEBULA Agency (studio/assets) est injecté (fond noir effacé via
mix-blend screen côté gabarit). Le navigateur sans écran peut être lent : on
l'ATTEND frame par frame, donc la qualité reste parfaite.
"""
import os, json, base64, shutil, subprocess, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = (HERE / "templates" / "kinetic.html").resolve()
LOGO_FILE = HERE / "assets" / "nebula-logo.png"
FPS = 60
SCALE = 2          # 1080×1920 logique → 2160×3840 (4K)
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

def _logo_uri():
    try:
        return "data:image/png;base64," + base64.b64encode(LOGO_FILE.read_bytes()).decode()
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
    logo = _logo_uri()

    def _capture():                                  # une tentative complète
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=[
                "--force-color-profile=srgb", "--hide-scrollbars", "--disable-gpu"])
            ctx = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
            page = ctx.new_page()
            page.add_init_script("window.CONCEPT = " + cjson + ";")
            if logo:
                page.add_init_script("window.__LOGO = " + json.dumps(logo) + ";")
            page.goto(TEMPLATE.as_uri(), wait_until="commit", timeout=60000)
            page.wait_for_function("window.__DURATION > 0", timeout=30000)
            try:
                page.wait_for_function("window.__FONTS_READY === true", timeout=9000)
            except Exception:
                pass
            total = page.evaluate("window.__DURATION")
            poster_t = page.evaluate("window.__POSTER_T")
            page.evaluate("window.__seek(%f)" % poster_t)
            page.screenshot(path=str(poster))                          # affiche PNG nette
            nframes = int(round(total / 1000.0 * fps))
            for f in range(nframes + 1):
                page.evaluate("window.__seek(%f)" % (f / fps * 1000.0))
                page.screenshot(path=str(frames / ("%05d.jpg" % f)), type="jpeg", quality=92)
            ctx.close(); browser.close()

    last = None
    for attempt in range(2):                          # 1 reprise auto si timeout/contention
        try:
            _capture(); last = None; break
        except Exception as e:
            last = e; print(f"  rendu: tentative {attempt + 1} échouée ({e}); reprise…")
    if last:
        raise last

    result = {"poster": str(poster) if poster.exists() else None, "mp4": None, "webm": None, "video": None}
    ff = _find_ffmpeg()
    if ff:
        cmd = [ff, "-y", "-framerate", str(fps), "-i", str(frames / "%05d.jpg"),
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
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

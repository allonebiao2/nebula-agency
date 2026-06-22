#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEBULA Agency — Rendu vidéo recrutement partenaires
Produit un MP4 vertical 4K (2160×3840) @ 60 i/s, format 9:16.

Usage :
  python render-video.py

Sortie : _marketing/recrutement-partenaires/output/video.mp4
         _marketing/recrutement-partenaires/output/poster.png

Prérequis :
  pip install playwright
  playwright install chromium
  ffmpeg (installé dans PATH ou via imageio-ffmpeg)
"""
import os, base64, shutil, subprocess, pathlib, json

HERE        = pathlib.Path(__file__).resolve().parent
REPO_ROOT   = HERE.parent.parent
TEMPLATE    = (HERE / "video.html").resolve()
LOGO_FILE   = HERE / "logo.png"                     # logo fourni par Mongazi
OUT_DIR     = HERE / "output"
FRAMES_DIR  = OUT_DIR / "_frames"
FPS         = 60
SCALE       = 2   # 1080×1920 → 2160×3840 (4K)
W, H        = 1080, 1920

# Essaie aussi le logo du studio si pas de logo local
if not LOGO_FILE.exists():
    fallback = REPO_ROOT / "studio" / "assets" / "nebula-logo.png"
    if fallback.exists():
        LOGO_FILE = fallback


def find_ffmpeg():
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def logo_uri():
    if not LOGO_FILE.exists():
        print(f"⚠️  Logo introuvable : {LOGO_FILE}")
        return None
    ext = LOGO_FILE.suffix.lower().lstrip('.')
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "svg": "image/svg+xml", "webp": "image/webp"}.get(ext, "image/png")
    data = base64.b64encode(LOGO_FILE.read_bytes()).decode()
    return f"data:{mime};base64,{data}"


CHROME_PATH = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def render():
    from playwright.sync_api import sync_playwright

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if FRAMES_DIR.exists():
        shutil.rmtree(FRAMES_DIR, ignore_errors=True)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    poster_path = OUT_DIR / "poster.png"
    mp4_path    = OUT_DIR / "video.mp4"
    logo        = logo_uri()

    print("🎬 NEBULA Agency — Recrutement Partenaires")
    print(f"   Template : {TEMPLATE}")
    print(f"   Logo     : {LOGO_FILE} ({'OK' if logo else 'ABSENT'})")
    print(f"   Sortie   : {OUT_DIR}")
    print(f"   Format   : 4K {W*SCALE}×{H*SCALE} @ {FPS} fps")

    def _capture():
        with sync_playwright() as p:
            chrome = CHROME_PATH if os.path.exists(CHROME_PATH) else None
            browser = p.chromium.launch(
                headless=True,
                executable_path=chrome,
                args=["--no-sandbox", "--disable-dev-shm-usage",
                      "--force-color-profile=srgb", "--hide-scrollbars", "--disable-gpu"]
            )
            ctx = browser.new_context(
                viewport={"width": W, "height": H},
                device_scale_factor=SCALE
            )
            page = ctx.new_page()

            if logo:
                page.add_init_script(f"window.__LOGO = {json.dumps(logo)};")

            page.goto(TEMPLATE.as_uri(), wait_until="commit", timeout=90000)
            page.wait_for_function("window.__DURATION > 0", timeout=30000)

            # Attendre les polices Google (9 s max, non bloquant si KO)
            try:
                page.wait_for_function("window.__FONTS_READY === true", timeout=9000)
                print("   Polices : chargées ✓")
            except Exception:
                print("   Polices : timeout (rendu avec fallback système)")

            total    = page.evaluate("window.__DURATION")
            poster_t = page.evaluate("window.__POSTER_T")
            nframes  = int(round(total / 1000.0 * FPS))
            duration_s = total / 1000.0

            print(f"   Durée   : {duration_s:.1f} s — {nframes} frames")

            # Poster
            page.evaluate(f"window.__seek({poster_t})")
            page.screenshot(path=str(poster_path))
            print(f"   Poster  : {poster_path}")

            # Frames
            print(f"   Capture : 0/{nframes}", end="", flush=True)
            for f in range(nframes + 1):
                page.evaluate(f"window.__seek({f / FPS * 1000.0})")
                page.screenshot(
                    path=str(FRAMES_DIR / f"{f:05d}.jpg"),
                    type="jpeg", quality=92
                )
                if f % 60 == 0:
                    print(f"\r   Capture : {f}/{nframes}", end="", flush=True)
            print(f"\r   Capture : {nframes}/{nframes} ✓            ")

            ctx.close()
            browser.close()

    # 2 tentatives (réseau/timeout occasionnel)
    last_err = None
    for attempt in range(2):
        try:
            _capture()
            last_err = None
            break
        except Exception as e:
            last_err = e
            print(f"   Tentative {attempt + 1} échouée ({e}); reprise…")
    if last_err:
        raise last_err

    # Encodage ffmpeg
    ff = find_ffmpeg()
    if not ff:
        print("⚠️  ffmpeg introuvable — frames conservées dans _frames/")
        print(f"   Assembler manuellement :\n   ffmpeg -framerate {FPS} -i {FRAMES_DIR}/%05d.jpg "
              f"-c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium {mp4_path}")
        return

    print("   Encodage ffmpeg…")
    cmd = [
        ff, "-y",
        "-framerate", str(FPS),
        "-i", str(FRAMES_DIR / "%05d.jpg"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-preset", "medium",
        "-movflags", "+faststart",
        "-an",
        str(mp4_path)
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode == 0 and mp4_path.exists():
        size_mb = mp4_path.stat().st_size / 1024 / 1024
        print(f"   MP4     : {mp4_path} ({size_mb:.1f} Mo) ✓")
    else:
        print("❌ ffmpeg KO :", result.stderr[-500:] if result.stderr else "(pas de stderr)")

    # Nettoyage frames
    shutil.rmtree(FRAMES_DIR, ignore_errors=True)
    print("✅ Terminé !")
    print(f"   → {mp4_path}")
    print(f"   → {poster_path}")


if __name__ == "__main__":
    render()

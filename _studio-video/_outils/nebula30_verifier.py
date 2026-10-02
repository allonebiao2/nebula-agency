"""Vérifie la vidéo livrée (out/NEBULA-Agency-30s.mp4), sans la croire sur parole.

    · les flux : une image H.264 1080x1920 à 30 i/s, un son AAC, 30,00 s ;
    · le son : sonie intégrée (cible −14 LUFS) et crête vraie (≤ −1 dBTP) ;
    · la SYNCHRO : la voix du MP4 est comparée, par corrélation, à la voix placée
      (`public/nebula30/voix.wav`) ; le décalage doit être nul, à une image près ;
    · une planche de 15 images tirées DU MP4 lui-même (pas de la composition).

    python _outils/nebula30_verifier.py
"""
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import signal
from scipy.io import wavfile

from nebula30_master import crete_vraie, lufs

ICI = Path(__file__).resolve().parent.parent
OUTILS = ICI / "node_modules/@remotion/compositor-win32-x64-msvc"
FINAL = ICI / "out/NEBULA-Agency-30s.mp4"
VOIX = ICI / "public/nebula30/voix.wav"
TMP = ICI / "out/_verif"
INSTANTS = [0.6, 1.9, 3.0, 4.9, 6.9, 8.4, 10.6, 12.0, 14.9, 16.6, 18.0, 19.3, 21.6, 24.6, 28.5]


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    sonde = json.loads(subprocess.run([str(OUTILS / "ffprobe.exe"), "-v", "error", "-show_streams", "-show_format", "-of", "json", str(FINAL)],
                                      capture_output=True, text=True, check=True).stdout)
    for s in sonde["streams"]:
        if s["codec_type"] == "video":
            print(f"image : {s['codec_name']} {s['width']}x{s['height']} · {s['r_frame_rate']} i/s · {s.get('nb_frames', '?')} images")
        else:
            print(f"son   : {s['codec_name']} · {s['sample_rate']} Hz · {s['channels']} canaux")
    print(f"durée : {float(sonde['format']['duration']):.2f} s · {int(sonde['format']['size']) / 1e6:.1f} Mo")

    son = TMP / "son.wav"
    subprocess.run([str(OUTILS / "ffmpeg.exe"), "-v", "error", "-y", "-i", str(FINAL), "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(son)], check=True)
    sr, x = wavfile.read(son)
    x = x.astype(np.float64) / 32768
    print(f"sonie : {lufs(x, sr):.1f} LUFS · crête vraie {crete_vraie(x):.1f} dBTP")

    # la synchro : corrélation de l'enveloppe de la voix seule avec celle du mélange
    srv, v = wavfile.read(VOIX)
    v = v.astype(np.float64).mean(1) / 32768
    v = signal.resample_poly(v, sr, srv)[: len(x)]
    def enveloppe(a):
        a = signal.sosfilt(signal.butter(4, [300, 3400], btype="band", fs=sr, output="sos"), a)
        return np.sqrt(np.convolve(a ** 2, np.ones(480) / 480, mode="same"))[::48]  # 1 ms
    ev, em = enveloppe(v), enveloppe(x.mean(1))
    n = min(len(ev), len(em))
    c = signal.correlate(em[:n] - em[:n].mean(), ev[:n] - ev[:n].mean(), mode="full")
    retard = np.argmax(c) - (n - 1)
    print(f"synchro de la voix : décalage {retard:+d} ms ({'OK' if abs(retard) <= 34 else 'À REVOIR'} : une image = 33 ms)")

    # la planche, tirée du MP4
    police = ImageFont.truetype("arial.ttf", 24)
    L, H = 270, 480
    planche = Image.new("RGB", (5 * (L + 6), 3 * (H + 6)), (25, 25, 25))
    for k, s in enumerate(INSTANTS):
        f = TMP / f"{s:05.2f}.jpg"
        subprocess.run([str(OUTILS / "ffmpeg.exe"), "-v", "error", "-y", "-ss", f"{s}", "-i", str(FINAL), "-frames:v", "1", "-q:v", "3", str(f)], check=True)
        im = Image.open(f).resize((L, H), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 84, 30], fill=(0, 0, 0))
        d.text((5, 2), f"{s:.1f}s", fill=(255, 220, 0), font=police)
        planche.paste(im, ((k % 5) * (L + 6), (k // 5) * (H + 6)))
    sortie = ICI / "out/NEBULA-Agency-30s_planche.jpg"
    planche.save(sortie, quality=86)
    print("planche →", sortie)


if __name__ == "__main__":
    main()

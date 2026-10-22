"""MA LETTRE À… · « Minuit pile, pour maman » : assemble la vidéo livrée, puis la VÉRIFIE sans la croire sur parole.

    python _outils/malettre_minuit_verifier.py

1. L'assemblage : l'image rendue par morceaux (`out/malettre-minuit.mp4`, recopiée sans réencodage) et LE master du
   script du son (`public/malettre-minuit/mix.wav`), encodé en AAC 320 kb/s. Sortie : `out/MaLettreA-Minuit-pile-YouTube.mp4`.
   ⚠️ Un nom vraiment différent : sous Windows les noms ignorent la casse (piège du 2026-10-02, le fichier lu écrasé).
2. Les flux : H.264 1920×1080 à 60 i/s, AAC 48 kHz, la durée du minutage, et TOUTES les images de la composition
   (comptées une à une : `-shortest` en avait coupé quatre, le 2026-10-22, avec une durée affichée juste).
3. Le son, MESURÉ DANS LE MP4 (après l'AAC, qui peut ajouter de la crête) : −14 LUFS, crête vraie ≤ −1 dBTP. Si
   l'AAC a dépassé, on baisse le gain et on réencode.
4. La synchro : le son du MP4 contre le master, par corrélation ; le décalage doit être nul, à une image près.
5. Une planche de 16 images tirées DU MP4 (pas de la composition).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import signal
from scipy.io import wavfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from malettre_minuit_son import crete_vraie, lufs  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ICI = Path(__file__).resolve().parent.parent
OUTILS = ICI / "node_modules/@remotion/compositor-win32-x64-msvc"
IMAGE = ICI / "out/malettre-minuit.mp4"
MASTER = ICI / "public/malettre-minuit/mix.wav"
FINAL = ICI / "out/MaLettreA-Minuit-pile-YouTube.mp4"
TMP = ICI / "out/_verif-minuit"
MINUTAGE = json.loads((ICI / "src/malettre-minuit/minutage.json").read_text(encoding="utf-8"))


def assembler(gain_db=0.0):
    af = ["-af", "volume=%.2fdB" % gain_db] if gain_db else []
    subprocess.run([str(OUTILS / "ffmpeg.exe"), "-v", "error", "-y", "-i", str(IMAGE), "-i", str(MASTER), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", *af, "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(FINAL)], check=True)


def son_du_mp4():
    TMP.mkdir(parents=True, exist_ok=True)
    w = TMP / "son.wav"
    subprocess.run([str(OUTILS / "ffmpeg.exe"), "-v", "error", "-y", "-i", str(FINAL), "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(w)], check=True)
    sr, d = wavfile.read(w)
    return sr, d.astype(np.float64) / 32768


def main():
    if not IMAGE.exists():
        sys.exit("⛔ l'image n'est pas rendue : node _outils/rendu_morceaux.mjs malettre-minuit 300 1")
    gain = 0.0
    for essai in range(3):
        assembler(gain)
        sr, y = son_du_mp4()
        l, tp = lufs(y), crete_vraie(y)
        print("assemblage %d : %.1f LUFS · crête vraie %.2f dBTP" % (essai + 1, l, tp))
        if tp <= -1.0:
            break
        gain -= (tp + 1.0) + 0.15
    sonde = json.loads(subprocess.run([str(OUTILS / "ffprobe.exe"), "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json",
                                       str(FINAL)], capture_output=True, text=True, check=True).stdout)
    attendues = round(MINUTAGE["duree"] * 60)
    images = 0
    for s in sonde["streams"]:
        if s["codec_type"] == "video":
            images = int(s.get("nb_read_frames", 0))
            print("image : %s %sx%s · %s i/s · %d images lues (composition : %d)" % (s["codec_name"], s["width"], s["height"],
                                                                                   s["r_frame_rate"], images, attendues))
        else:
            print("son   : %s · %s Hz · %s canaux" % (s["codec_name"], s["sample_rate"], s["channels"]))
    duree = float(sonde["format"]["duration"])
    print("durée : %.2f s (minutage : %.2f s) · %.1f Mo" % (duree, MINUTAGE["duree"], int(sonde["format"]["size"]) / 1e6))

    # la synchro : le son du MP4 contre le master, sur 20 s autour de minuit
    srm, m = wavfile.read(MASTER)
    m = m.astype(np.float64) / 32768
    a, b = int((MINUTAGE["minuit"] - 4) * sr), int((MINUTAGE["minuit"] + 16) * sr)
    x, r = y[a:b].mean(1), m[a:b].mean(1)
    c = signal.correlate(x, r, mode="full", method="fft")
    decal = (np.argmax(c) - (len(r) - 1)) / sr
    print("synchro : décalage %.1f ms (une image = 16,7 ms)" % (decal * 1000))

    # la planche : 16 images tirées du MP4
    import cv2
    cap = cv2.VideoCapture(str(FINAL))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    instants = [0.5, 2.4, 4.6, 8.4, 10.6, 11.5, 13.3, 14.35, 15.5, 19.8, 22.5, 25.5, 33.0, 38.3, 45.9, DUREE_FIN(duree)]
    W, H = 480, 270
    planche = Image.new("RGB", (W * 4, H * 4), (0, 0, 0))
    for i, s in enumerate(instants):
        cap.set(cv2.CAP_PROP_POS_FRAMES, min(n - 1, int(s * fps)))
        ok, fr = cap.read()
        if not ok:
            continue
        im = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).resize((W, H))
        ImageDraw.Draw(im).text((8, 6), "%.2f s" % s, fill=(255, 220, 120))
        planche.paste(im, ((i % 4) * W, (i // 4) * H))
    cap.release()
    planche.save(TMP / "planche.jpg", quality=88)
    ok = images == attendues and abs(duree - MINUTAGE["duree"]) < 0.1 and -14.6 < l < -13.4 and tp <= -1.0 and abs(decal) < 0.017
    print(("✓ " if ok else "✗ ") + "livrable : %s · planche : %s" % (FINAL, TMP / "planche.jpg"))
    return 0 if ok else 1


def DUREE_FIN(d):
    return max(0, d - 0.6)


if __name__ == "__main__":
    sys.exit(main())

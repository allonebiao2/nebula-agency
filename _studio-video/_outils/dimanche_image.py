"""Prépare l'image de la vidéo « le plan du dimanche » pour Remotion.

La source est une copie retéléchargée de TikTok : 576x1024, très compressée, et
ses sous-titres (CapCut, blanc) sont INCRUSTÉS dans l'image, sur la poitrine.
Ce script, image par image :
  1. efface ces sous-titres (masque du blanc pur dans la bande mesurée, puis
     remplissage Telea) ; les nouveaux sous-titres se posent au même endroit ;
  2. étalonne légèrement (contraste doux, un peu de chaleur et de saturation) ;
  3. agrandit en 1080x1920 (Lanczos) et redonne un peu de piqué.

Le son n'est pas touché ici : voir dimanche_son.py.

    python _outils/dimanche_image.py            # tout
    python _outils/dimanche_image.py --essai 56 # une image, pour regarder
"""
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ICI = Path(__file__).resolve().parent.parent
SOURCE = ICI / "public/dimanche/source.mp4"
SORTIE = ICI / "public/dimanche/image.mp4"
FFMPEG = ICI / "node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe"
L, H = 1080, 1920

# La bande des anciens sous-titres, mesurée sur toute la vidéo (texte blanc
# intermittent) : lignes 240-329, colonnes 107-368 à 576x1024. On prend une marge.
Y0, Y1, X0, X1 = 205, 372, 80, 400


def masque_texte(bande):
    """Le texte incrusté est d'un blanc PUR ; les poignets de chemise sont d'un
    blanc cassé et forment de gros blocs. On garde le blanc pur, en traits fins."""
    hsv = cv2.cvtColor(bande, cv2.COLOR_BGR2HSV)
    m = ((hsv[..., 2] > 222) & (hsv[..., 1] < 40)).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    garde = np.zeros(n, bool)
    for i in range(1, n):
        x, y, w, h, aire = stats[i]
        # une lettre ou un mot : moins de 34 px de haut. Un « i » ou un « l » est
        # un petit bâton PLEIN : le critère d'aplat ne vaut que pour un gros bloc.
        plein = aire / max(w * h, 1) >= 0.75
        garde[i] = h <= 34 and aire <= 1800 and (aire < 220 or not plein)
    m = garde[lab].astype(np.uint8) * 255
    # le liseré sombre du texte part avec lui
    return cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))


def lut_etalonnage():
    x = np.arange(256) / 255.0
    y = x ** 0.94                                        # la source est sombre (moyenne 92/255)
    courbe = np.clip(y - 0.30 * np.sin(2 * np.pi * y) / (2 * np.pi), 0, 1)  # S doux
    b = np.clip(courbe * 0.985, 0, 1)                    # un rien plus chaud
    r = np.clip(courbe * 1.02, 0, 1)
    return [np.round(c * 255).astype(np.uint8) for c in (b, courbe, r)]


LUT = lut_etalonnage()


def traiter(f):
    bande = f[Y0:Y1, X0:X1]
    m = masque_texte(bande)
    if m.any():
        f[Y0:Y1, X0:X1] = cv2.inpaint(bande, m, 5, cv2.INPAINT_TELEA)
    f = cv2.merge([cv2.LUT(c, lut) for c, lut in zip(cv2.split(f), LUT)])
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.08, 0, 255)
    f = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    g = cv2.resize(f, (L, H), interpolation=cv2.INTER_LANCZOS4)
    flou = cv2.GaussianBlur(g, (0, 0), 1.4)
    return cv2.addWeighted(g, 1.45, flou, -0.45, 0)


def essai(t):
    cap = cv2.VideoCapture(str(SOURCE))
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, f = cap.read()
    avant = cv2.resize(f, (L, H), interpolation=cv2.INTER_LINEAR)
    apres = traiter(f.copy())
    sortie = ICI / f"out/essai_image_{t}.jpg"
    sortie.parent.mkdir(exist_ok=True)
    cv2.imwrite(str(sortie), np.hstack([avant, apres]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(sortie)


def tout():
    cap = cv2.VideoCapture(str(SOURCE))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    enc = subprocess.Popen(
        # le ffmpeg de Remotion n'a pas le démultiplexeur « rawvideo » : on lui
        # envoie des JPEG à 97, le format qu'il reçoit lui-même au rendu
        [str(FFMPEG), "-v", "error", "-y", "-f", "image2pipe", "-c:v", "mjpeg",
         "-framerate", "30", "-i", "-", "-c:v", "libx264", "-preset", "medium",
         "-crf", "16", "-g", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         str(SORTIE)],
        stdin=subprocess.PIPE)
    i = 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        enc.stdin.write(cv2.imencode(".jpg", traiter(f), [cv2.IMWRITE_JPEG_QUALITY, 97])[1].tobytes())
        i += 1
        if i % 300 == 0:
            print(f"{i}/{n}", flush=True)
    enc.stdin.close()
    enc.wait()
    print("image prête :", SORTIE, i, "images")


if __name__ == "__main__":
    if "--essai" in sys.argv:
        essai(float(sys.argv[sys.argv.index("--essai") + 1]))
    else:
        tout()

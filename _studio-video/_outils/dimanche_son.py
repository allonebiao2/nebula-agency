"""Nettoie et remonte la voix de la vidéo « le plan du dimanche ».

Mesuré sur la source : voix à −29 dBFS en moyenne (TikTok tourne vers −14 LUFS),
bruit de fond à −41 dB, soit à peine 10 dB sous la voix, et ce bruit est grave
(85 % de son énergie sous 500 Hz : clim, résonance de la pièce).

Chaîne : passe-haut 85 Hz · réduction de bruit spectrale douce (profil pris dans
les silences, plancher à −10 dB pour ne pas « gargouiller ») · un peu de présence
vers 3 kHz · compression 3:1 · loudness intégrée −14 LUFS (BS.1770) · limiteur
à −1,5 dBFS. Chaque étape est mesurée avant/après, on ne l'écoute pas de confiance.

    python _outils/dimanche_son.py
"""
import subprocess
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

ICI = Path(__file__).resolve().parent.parent
SOURCE = ICI / "public/dimanche/source.mp4"
SORTIE = ICI / "public/dimanche/voix.wav"
FFMPEG = ICI / "node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe"
SR = 44100


def lire():
    # le ffmpeg de Remotion n'a pas le format brut « s16le » : on passe par un WAV
    tmp = ICI / "out/_voix_source.wav"
    tmp.parent.mkdir(exist_ok=True)
    subprocess.run([str(FFMPEG), "-v", "error", "-y", "-i", str(SOURCE), "-vn", "-ac", "1",
                    "-ar", str(SR), "-c:a", "pcm_s16le", str(tmp)], check=True)
    _, brut = wavfile.read(tmp)
    return brut.astype(np.float64) / 32768


def biquad(kind, fc, q, gain_db=0.0):
    """Coefficients RBJ (Audio EQ Cookbook)."""
    a = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * fc / SR
    al = np.sin(w0) / (2 * q)
    c = np.cos(w0)
    if kind == "hp":
        b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]
        d = [1 + al, -2 * c, 1 - al]
    elif kind == "peak":
        b = [1 + al * a, -2 * c, 1 - al * a]
        d = [1 + al / a, -2 * c, 1 - al / a]
    elif kind == "shelf_haut":
        s = 2 * np.sqrt(a) * al
        b = [a * ((a + 1) + (a - 1) * c + s), -2 * a * ((a - 1) + (a + 1) * c), a * ((a + 1) + (a - 1) * c - s)]
        d = [(a + 1) - (a - 1) * c + s, 2 * ((a - 1) - (a + 1) * c), (a + 1) - (a - 1) * c - s]
    b, d = np.array(b), np.array(d)
    return b / d[0], d / d[0]


def lufs(x):
    """Loudness intégrée BS.1770-4 (pondération K, blocs de 400 ms, double porte)."""
    y = signal.lfilter(*biquad("shelf_haut", 1681.97, 0.7072, 4.0), x)
    y = signal.lfilter(*biquad("hp", 38.13, 0.5003), y)
    blk, pas = int(0.4 * SR), int(0.1 * SR)
    z = np.array([np.mean(y[i:i + blk] ** 2) for i in range(0, len(y) - blk, pas)])
    l = -0.691 + 10 * np.log10(z + 1e-12)
    z = z[l > -70]
    rel = -0.691 + 10 * np.log10(z.mean()) - 10
    z = z[-0.691 + 10 * np.log10(z) > rel]
    return -0.691 + 10 * np.log10(z.mean())


def plancher(x):
    fr = x[: len(x) // 2205 * 2205].reshape(-1, 2205)
    return np.percentile(20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9), [5, 50])


def debruiter(x):
    f, t, X = signal.stft(x, SR, nperseg=2048, noverlap=1536)
    mag = np.abs(X)
    e = mag.sum(0)
    silence = e <= np.percentile(e, 8)            # les trames les plus calmes = le bruit seul
    bruit = np.median(mag[:, silence], axis=1, keepdims=True)
    gain = np.clip(1 - 1.6 * bruit / (mag + 1e-12), 0.316, 1)   # plancher −10 dB
    gain = signal.convolve2d(gain, np.ones((3, 5)) / 15, mode="same", boundary="symm")
    _, y = signal.istft(X * gain, SR, nperseg=2048, noverlap=1536)
    return y[: len(x)]


def compresser(x, seuil_db=-24, ratio=3.0):
    env = np.sqrt(signal.lfilter([1 - np.exp(-1 / (0.012 * SR))], [1, -np.exp(-1 / (0.012 * SR))], x ** 2))
    db = 20 * np.log10(env + 1e-9)
    exces = np.maximum(db - seuil_db, 0)
    red = -exces * (1 - 1 / ratio)
    red = signal.lfilter([1 - np.exp(-1 / (0.15 * SR))], [1, -np.exp(-1 / (0.15 * SR))], red)
    return x * 10 ** (red / 20)


def limiter(x, plafond_db=-1.5):
    plafond = 10 ** (plafond_db / 20)
    fen = int(0.005 * SR)
    pic = np.abs(x)
    pic = np.lib.stride_tricks.sliding_window_view(np.pad(pic, (fen, 0)), fen + 1).max(1)[: len(x)]
    g = np.minimum(1, plafond / (pic + 1e-12))
    g = signal.lfilter([1 - np.exp(-1 / (0.05 * SR))], [1, -np.exp(-1 / (0.05 * SR))], g)
    g = np.minimum(g, plafond / (np.abs(x) + 1e-12))  # garantie dure
    return x * g


def main():
    x = lire()
    print(f"source      : {lufs(x):6.1f} LUFS · plancher/médiane {plancher(x).round(1)} dB")
    x = signal.lfilter(*biquad("hp", 85, 0.707), x)
    x = signal.lfilter(*biquad("hp", 85, 0.707), x)   # 24 dB/octave
    x = debruiter(x)
    print(f"débruité    : {lufs(x):6.1f} LUFS · plancher/médiane {plancher(x).round(1)} dB")
    x = signal.lfilter(*biquad("peak", 3200, 1.0, 2.5), x)
    x = compresser(x)
    x = x * 10 ** ((-14 - lufs(x)) / 20)
    x = limiter(x)
    print(f"final       : {lufs(x):6.1f} LUFS · plancher/médiane {plancher(x).round(1)} dB · crête {20*np.log10(np.abs(x).max()):.1f} dBFS")
    s = np.round(np.clip(x, -1, 1) * 32767).astype(np.int16)
    wavfile.write(SORTIE, SR, np.stack([s, s], 1))
    print("voix prête :", SORTIE, f"{len(x)/SR:.2f} s")


if __name__ == "__main__":
    main()

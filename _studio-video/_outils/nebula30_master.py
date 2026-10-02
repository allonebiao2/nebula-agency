"""Le MASTERING de la vidéo de marque NEBULA, après le rendu.

Remotion additionne la voix, la musique et les bruitages SANS limiteur : on lui a
laissé 2,5 dB de marge (MIX = 0,75 dans `donnees.ts`). Ici on reprend le son
rendu (`out/morceaux/nebula-30s/son.wav`) et on pose le niveau de diffusion :

    · −14 LUFS intégrés (BS.1770, ce que visent TikTok, Instagram et YouTube) ;
    · limiteur stéréo lié, crêtes vraies ≤ −1 dBTP (contrôle suréchantillonné x4) ;
    · contrôle : la voix doit PASSER DEVANT. Sur chaque réplique, la sonie du
      mélange ne doit dépasser celle de la voix seule que de peu (sinon c'est que
      la musique ou les bruitages lui marchent dessus).

Puis on recolle les morceaux d'image, sans les réencoder, sous ce son :
out/NEBULA-Agency-30s.mp4.

⚠️ PIÈGE WINDOWS, rencontré le 2026-10-02 : les noms de fichiers ignorent la casse.
La première version écrivait `NEBULA-30s.mp4` en lisant `nebula-30s.mp4` : C'EST
LE MÊME FICHIER, ffmpeg l'a écrasé pendant qu'il le lisait (il restait 4 images).
On repart donc des morceaux eux-mêmes, et la sortie porte un nom vraiment différent.

    python _outils/nebula30_master.py
"""
import re
import subprocess
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

ICI = Path(__file__).resolve().parent.parent
FFMPEG = ICI / "node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe"
SON = ICI / "out/morceaux/nebula-30s/son.wav"
MORCEAUX = ICI / "out/morceaux/nebula-30s/liste.txt"
MASTER = ICI / "out/morceaux/nebula-30s/son-master.wav"
FINAL = ICI / "out/NEBULA-Agency-30s.mp4"
VOIX = ICI / "public/nebula30/voix.wav"
CIBLE = -14.0
PLAFOND_DBTP = -1.0
MIX = 0.75


def biquad(kind, fc, q, gain_db, sr):
    a = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * fc / sr
    al = np.sin(w0) / (2 * q)
    c = np.cos(w0)
    if kind == "hp":
        b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]
        d = [1 + al, -2 * c, 1 - al]
    else:  # plateau haut
        s = 2 * np.sqrt(a) * al
        b = [a * ((a + 1) + (a - 1) * c + s), -2 * a * ((a - 1) + (a + 1) * c), a * ((a + 1) + (a - 1) * c - s)]
        d = [(a + 1) - (a - 1) * c + s, 2 * ((a - 1) - (a + 1) * c), (a + 1) - (a - 1) * c - s]
    b, d = np.array(b), np.array(d)
    return b / d[0], d / d[0]


def pondere(x, sr):
    """Pondération K de BS.1770, canal par canal."""
    y = signal.lfilter(*biquad("plateau", 1681.97, 0.7072, 4.0, sr), x, axis=0)
    return signal.lfilter(*biquad("hp", 38.13, 0.5003, 0.0, sr), y, axis=0)


def lufs(x, sr):
    """Sonie intégrée BS.1770-4 (stéréo : somme des puissances des canaux, double porte)."""
    y = pondere(x if x.ndim == 2 else x[:, None], sr)
    blk, pas = int(0.4 * sr), int(0.1 * sr)
    z = np.array([np.mean(y[i:i + blk] ** 2, axis=0).sum() for i in range(0, len(y) - blk, pas)])
    l = -0.691 + 10 * np.log10(z + 1e-12)
    z = z[l > -70]
    rel = -0.691 + 10 * np.log10(z.mean()) - 10
    z = z[-0.691 + 10 * np.log10(z) > rel]
    return -0.691 + 10 * np.log10(z.mean())


def crete_vraie(x):
    """Crête estimée après suréchantillonnage x4 (dBTP)."""
    sur = signal.resample_poly(x, 4, 1, axis=0)
    return 20 * np.log10(np.abs(sur).max() + 1e-12)


def limiter(x, sr, plafond_db, anticipation=0.005, relache=0.08):
    """Limiteur stéréo lié à anticipation : un seul gain pour les deux canaux."""
    plafond = 10 ** (plafond_db / 20)
    n = int(anticipation * sr)
    pic = np.abs(x).max(axis=1)
    pic = np.lib.stride_tricks.sliding_window_view(np.pad(pic, (0, n)), n + 1).max(1)[: len(x)]
    voulu = np.minimum(1, plafond / (pic + 1e-12))
    r = np.exp(-1 / (relache * sr))
    g = np.empty_like(voulu)
    v = 1.0
    for i, cible in enumerate(voulu):
        v = cible if cible < v else cible + r * (v - cible)
        g[i] = v
    y = x * g[:, None]
    return np.clip(y, -plafond, plafond)


def repliques():
    ts = (ICI / "src/nebula30/minutage.ts").read_text(encoding="utf-8")
    bloc = re.search(r"export const REPLIQUES = (\{.*?\}) as const;", ts).group(1)
    return {k: (float(a), float(b)) for k, a, b in re.findall(r'"(\w+)": \[([\d.]+), ([\d.]+)\]', bloc)}


def main():
    sr, brut = wavfile.read(SON)
    x = brut.astype(np.float64) / (32768 if brut.dtype == np.int16 else 1)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    sature = int((np.abs(brut) >= 32767).sum()) if brut.dtype == np.int16 else 0
    print(f"rendu      : {len(x)/sr:6.2f} s · {sr} Hz · {lufs(x, sr):6.1f} LUFS · crête {20*np.log10(np.abs(x).max()):5.1f} dBFS · échantillons saturés : {sature}")
    y = x * 10 ** ((CIBLE - lufs(x, sr)) / 20)
    for _ in range(3):  # le limiteur mange un peu de sonie : on recale, puis on relimite
        y = limiter(y, sr, PLAFOND_DBTP - 0.6)
        y = y * 10 ** ((CIBLE - lufs(y, sr)) / 20)
    y = limiter(y, sr, PLAFOND_DBTP - 0.6)
    print(f"master     : {lufs(y, sr):6.1f} LUFS · crête vraie {crete_vraie(y):5.1f} dBTP")

    # la voix passe-t-elle devant ? (voix seule, au même gain que dans le mélange)
    srv, v = wavfile.read(VOIX)
    v = v.astype(np.float64) / 32768 * MIX
    if srv != sr:
        v = signal.resample_poly(v, sr, srv, axis=0)
    v = v[: len(x)]
    gain_master = 10 ** ((lufs(y, sr) - lufs(x, sr)) / 20)
    print("réplique        mélange   voix seule   écart")
    ecarts = []
    for nom, (a, b) in repliques().items():
        i0, i1 = int(a * sr), int(b * sr)
        lm = lufs(y[i0:i1], sr) if i1 - i0 > sr * 0.45 else float("nan")
        lv = lufs(v[i0:i1] * gain_master, sr) if i1 - i0 > sr * 0.45 else float("nan")
        if not np.isnan(lm):
            ecarts.append(lm - lv)
        print(f"  {nom:13s} {lm:7.1f}   {lv:9.1f}   {lm - lv:+5.1f} LU")
    print(f"écart médian : {np.median(ecarts):+.1f} LU (près de 0 = la voix domine ; au-delà de +3 = elle est couverte)")

    wavfile.write(MASTER, sr, np.round(y * 32767).astype(np.int16))
    subprocess.run([str(FFMPEG), "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(MORCEAUX), "-i", str(MASTER),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", str(FINAL)], check=True)
    print("→", FINAL, f"({FINAL.stat().st_size / 1e6:.1f} Mo)")


if __name__ == "__main__":
    main()

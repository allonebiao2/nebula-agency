"""Les bruitages de « le plan du dimanche », SYNTHÉTISÉS (aucun fichier tiers,
aucun droit à gérer) : un son par geste de la feuille.

    pop     une étiquette qui se pose         whoosh  une feuille qui glisse
    tampon  le coup sourd d'un tampon         coche   la coche d'une case
    stylo   un trait de feutre                clic    le clic de souris
    tic     l'aiguille d'une horloge          montee  la bascule budget → marché
    ding    une clochette claire (gratuite, live)

Chaque son est normalisé à −3 dBFS de crête ; le volume se règle au montage.

    python _outils/dimanche_bruitages.py
"""
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

ICI = Path(__file__).resolve().parent.parent
DOSSIER = ICI / "public/dimanche/sfx"
SR = 44100
rng = np.random.default_rng(7)


def t(duree):
    return np.arange(int(SR * duree)) / SR


def env(duree, attaque, chute):
    x = t(duree)
    return np.minimum(1, x / max(attaque, 1e-4)) * np.exp(-x / chute)


def passe_bande(x, bas, haut, ordre=2):
    sos = signal.butter(ordre, [bas, haut], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def ecrire(nom, x):
    x = x / (np.abs(x).max() + 1e-9) * 10 ** (-3 / 20)
    fondu = int(0.004 * SR)
    x[-fondu:] *= np.linspace(1, 0, fondu)
    wavfile.write(DOSSIER / f"{nom}.wav", SR, np.round(x * 32767).astype(np.int16))


def pop():
    x = t(0.12)
    f = 950 * np.exp(-x * 14) + 420
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.12, 0.002, 0.035)
    return s + 0.15 * passe_bande(rng.standard_normal(len(x)), 2000, 6000) * env(0.12, 0.001, 0.006)


def whoosh():
    n = int(SR * 0.42)
    bruit = rng.standard_normal(n)
    # un filtre qui balaie 350 → 2600 Hz, par blocs
    sortie = np.zeros(n)
    blocs = 24
    for k in range(blocs):
        a, b = k * n // blocs, (k + 1) * n // blocs
        fc = 350 + (2600 - 350) * (k / blocs) ** 1.5
        sortie[a:b] = passe_bande(bruit[max(0, a - 2000):b], fc * 0.6, fc * 1.4)[-(b - a):]
    x = t(0.42)
    forme = np.sin(np.pi * np.clip(x / 0.42, 0, 1)) ** 2
    return sortie * forme


def tampon():
    x = t(0.3)
    coup = np.sin(2 * np.pi * (70 + 60 * np.exp(-x * 30)) * x) * env(0.3, 0.001, 0.09)
    papier = passe_bande(rng.standard_normal(len(x)), 300, 3000) * env(0.3, 0.001, 0.02)
    return coup + 0.6 * papier


def coche():
    x = t(0.09)
    return np.sin(2 * np.pi * 2300 * x) * env(0.09, 0.001, 0.018) + 0.5 * passe_bande(rng.standard_normal(len(x)), 3000, 9000) * env(0.09, 0.0005, 0.004)


def stylo():
    x = t(0.5)
    grain = passe_bande(rng.standard_normal(len(x)), 1800, 6000)
    mod = 0.55 + 0.45 * np.sin(2 * np.pi * 13 * x + 2 * np.sin(2 * np.pi * 3 * x))
    forme = np.minimum(1, x / 0.03) * np.minimum(1, (0.5 - x) / 0.08)
    return grain * mod * forme


def clic():
    x = t(0.06)
    un = passe_bande(rng.standard_normal(len(x)), 2500, 8000) * env(0.06, 0.0003, 0.003)
    deux = np.roll(un, int(0.018 * SR)) * 0.6
    return un + deux


def tic():
    x = t(0.04)
    return np.sin(2 * np.pi * 3200 * x) * env(0.04, 0.0005, 0.006)


def montee():
    x = t(0.9)
    f = 180 * (1 + 5 * (x / 0.9) ** 2)
    ton = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5
    souffle = passe_bande(rng.standard_normal(len(x)), 800, 5000)
    forme = (x / 0.9) ** 2 * np.minimum(1, (0.9 - x) / 0.05)
    return (ton + 0.5 * souffle) * forme


def ding():
    x = t(0.9)
    return (np.sin(2 * np.pi * 1320 * x) + 0.5 * np.sin(2 * np.pi * 1980 * x) + 0.25 * np.sin(2 * np.pi * 2640 * x)) * env(0.9, 0.002, 0.22)


if __name__ == "__main__":
    DOSSIER.mkdir(parents=True, exist_ok=True)
    for f in (pop, whoosh, tampon, coche, stylo, clic, tic, montee, ding):
        ecrire(f.__name__, f())
        print("·", f.__name__)
    print("→", DOSSIER)

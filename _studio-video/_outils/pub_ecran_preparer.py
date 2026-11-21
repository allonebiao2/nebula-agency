# -*- coding: utf-8 -*-
"""Prépare ce que la pub écran NEBULA pose à l'écran et à l'oreille (tout va dans `public/pub-ecran-nebula/`, hors dépôt).

    python _outils/pub_ecran_preparer.py            tout
    python _outils/pub_ecran_preparer.py neon       l'enseigne
    python _outils/pub_ecran_preparer.py sons       les bruitages
    python _outils/pub_ecran_preparer.py musique    la musique
    python _outils/pub_ecran_preparer.py grain      le grain de l'image filmée

1. L'ENSEIGNE NÉON, dessinée comme dans `avatar_studio.py` (Mongazi, 20/11) : NEBULA en violet (172, 82, 255),
   AGENCY en cyan (40, 222, 255), en Arial Black, des TUBES (le contour de chaque lettre) au cœur presque blanc, et
   des halos de plus en plus larges. Trois couches par enseigne, que la vidéo allume l'une après l'autre :
   `neon-eteint.png` (le verre éteint), `neon-tube-<mot>.png` (le tube allumé) et `neon-halo-<mot>.png` (la lueur,
   4 fois plus petite : elle est floue, la vidéo l'agrandit). Le tube et le halo sont des lumières rendues
   transparentes (alpha = intensité) : posées sur la nuit, elles s'y ajoutent comme un vrai néon.
2. LES BRUITAGES, tous synthétisés ici (aucun fichier tiers) : pop (la bulle), clic (le doigt), carillon doux (la
   commande), souffle (le grand texte), néon (l'allumage et le bourdonnement), glisse, tic, éclat.
3. LA MUSIQUE : « Piano Jazz Rainy Night » d'Alex Morgan (Pixabay n° 564276, licence Pixabay Content License, usage
   commercial permis), déjà dans `_partage/`, coupée et ramenée à -28 LUFS. ⛔ Rien de la musique des références.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage, signal

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ICI = Path(__file__).resolve().parent.parent
RACINE = ICI.parent
DOSSIER = ICI / "public/pub-ecran-nebula"
SR = 48000
POLICE = os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", "ariblk.ttf")   # Arial Black
MUSIQUE = RACINE / "_partage/alex-morgan-piano-jazz-rainy-night-music-564276.mp3"
GRAINE = np.random.default_rng(20261121)


# ─────────────────────────────── 1. l'enseigne ───────────────────────────────
# Les proportions sont celles d'`avatar_studio.py`, ramenées à la hauteur H de NEBULA (112 px là-bas) :
# AGENCY fait 78/112 de NEBULA, son centre est 128/112 H plus bas ; le tube a une demi-épaisseur de 3,4/112 H.
H = 220                       # hauteur de NEBULA dans les PNG (px)
LARGEUR, HAUTEUR = 2600, 1500  # la toile : assez de marge pour la lueur
CENTRE_N = (LARGEUR / 2, HAUTEUR / 2 - 64 / 112 * H)
CENTRE_A = (LARGEUR / 2, HAUTEUR / 2 + 64 / 112 * H)


def tubes_texte(texte, hauteur, centre):
    """Les lettres en TUBES (une bande sur le contour, pas la lettre pleine), rendues à 4x puis réduites."""
    s = 4
    f = ImageFont.truetype(POLICE, round(hauteur * s * 1.32))
    l, t, r, b = f.getbbox(texte)
    m = Image.new("L", (r - l + 40 * s, b - t + 40 * s), 0)
    ImageDraw.Draw(m).text((20 * s - l, 20 * s - t), texte, font=f, fill=255)
    ep = max(3, round(3.4 / 112 * H * s))                   # demi-épaisseur du tube
    dedans = m.filter(ImageFilter.MinFilter(2 * ep + 1))
    tube = np.clip(np.asarray(m).astype(np.float32) - np.asarray(dedans).astype(np.float32), 0, 255)
    tube = Image.fromarray(tube.astype(np.uint8)).filter(ImageFilter.GaussianBlur(s * 0.9))
    w_, h_ = m.width // s, m.height // s
    tube = np.asarray(tube.resize((w_, h_), Image.LANCZOS)).astype(np.float32) / 255
    plein = np.asarray(m.resize((w_, h_), Image.LANCZOS)).astype(np.float32) / 255
    T = np.zeros((HAUTEUR, LARGEUR), np.float32)
    P = np.zeros_like(T)
    x, y = round(centre[0] - w_ / 2), round(centre[1] - h_ / 2)
    T[y:y + h_, x:x + w_] = tube
    P[y:y + h_, x:x + w_] = plein
    return T, P


def flou(x, r):
    """Flou gaussien en flottants (aucune marche d'escalier dans les lueurs faibles), canal par canal."""
    return np.stack([ndimage.gaussian_filter(x[..., c], r, mode="constant") for c in range(x.shape[2])], axis=-1)


def reduire(x, q):
    """Moyenne par blocs de q x q : la lueur se calcule au quart, elle est floue de toute façon."""
    h, w = x.shape[0] // q * q, x.shape[1] // q * q
    return x[:h, :w].reshape(h // q, q, w // q, q, -1).mean(axis=(1, 3))


def lumiere_rgba(x):
    """Une lumière sur du noir devient une image TRANSPARENTE (alpha = la plus forte composante, couleur ramenée à
    pleine intensité) : posée normalement sur un fond sombre, elle s'ajoute comme une lumière, sans mode de fusion
    (un mode « screen » ne traverse pas un groupe isolé par une opacité ou un flou, et le noir de l'image s'y voyait)."""
    x = np.clip(x, 0, 255)
    a = x.max(axis=-1, keepdims=True) / 255
    rgb = np.where(a > 1e-4, x / np.maximum(a, 1e-4), 0)
    return Image.fromarray(np.concatenate([np.clip(rgb, 0, 255), a * 255], axis=-1).astype(np.uint8), "RGBA")


def enseigne():
    DOSSIER.mkdir(parents=True, exist_ok=True)
    k = H / 112                                              # l'échelle d'avatar_studio
    eteint = np.zeros((HAUTEUR, LARGEUR, 4), np.float32)
    boites = {}
    for mot, hauteur, centre, coeur, gaz in (("nebula", H, CENTRE_N, (244, 228, 255), (172, 82, 255)),
                                             ("agency", 78 / 112 * H, CENTRE_A, (228, 255, 255), (40, 222, 255))):
        T, P = tubes_texte(mot.upper(), hauteur, centre)
        gaz = np.array(gaz, np.float32)
        lum = T[..., None] * gaz
        # le tube allumé : le cœur presque blanc, le bord coloré, et la lueur serrée
        tube = flou(lum, 2 * k) * 1.1 + flou(lum, 6 * k) * 0.95
        t = T[..., None]
        tube = tube * (1 - t) + np.maximum(tube, np.array(coeur, np.float32) * t + gaz * (1 - t) * 0.6) * t
        # la lueur : l'intérieur des lettres teinté, puis des halos de plus en plus larges
        q = 4
        petit_lum = reduire(lum, q)
        halo = reduire(P[..., None] * gaz * 0.16, q)
        for r, poids in ((15 * k, 0.75), (38 * k, 0.5), (95 * k, 0.28), (200 * k, 0.14)):
            halo += flou(petit_lum, r / q) * poids
        halo *= 2.2                                           # sur du noir pur, la lueur d'avatar_studio paraît trop faible
        lumiere_rgba(tube).save(DOSSIER / f"neon-tube-{mot}.png", optimize=True)
        lumiere_rgba(halo).save(DOSSIER / f"neon-halo-{mot}.png", optimize=True)
        # le verre éteint : un tube gris-violet sombre, à peine visible dans la nuit
        verre = np.array((74, 66, 92), np.float32)
        eteint[..., :3] = np.where(T[..., None] > eteint[..., 3:4] / 255, verre, eteint[..., :3])
        eteint[..., 3] = np.maximum(eteint[..., 3], T * 230)
        ys, xs = np.nonzero(T > 0.2)
        boites[mot] = {"x": int(xs.min()), "y": int(ys.min()), "w": int(xs.max() - xs.min()),
                       "h": int(ys.max() - ys.min())}
    Image.fromarray(np.clip(eteint, 0, 255).astype(np.uint8), "RGBA").save(DOSSIER / "neon-eteint.png", optimize=True)
    infos = {"largeur": LARGEUR, "hauteur": HAUTEUR, "halo_reduit": 4, **boites}
    (DOSSIER / "neon.json").write_text(json.dumps(infos, indent=1), encoding="utf-8")
    print("enseigne :", infos)


# ─────────────────────────────── 2. les bruitages ───────────────────────────────

def t_(d):
    return np.arange(int(d * SR)) / SR


def env(n, att=0.002, rel=0.01):
    e = np.ones(n)
    a = max(1, int(att * SR))
    r = max(1, int(rel * SR))
    e[:a] = np.linspace(0, 1, a)
    e[-r:] *= np.linspace(1, 0, r)
    return e


def passe_bande(x, bas, haut, ordre=2):
    sos = signal.butter(ordre, [bas, haut], "bandpass", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def passe_bas(x, fc, ordre=2):
    return signal.sosfilt(signal.butter(ordre, fc, "lowpass", fs=SR, output="sos"), x)


def passe_haut(x, fc, ordre=2):
    return signal.sosfilt(signal.butter(ordre, fc, "highpass", fs=SR, output="sos"), x)


def ecrire(nom, x, crete_db=-3.0):
    x = np.asarray(x, np.float64)
    x = x / (np.abs(x).max() + 1e-12) * 10 ** (crete_db / 20)
    sf.write(DOSSIER / "sfx" / nom, x.astype(np.float32), SR, subtype="PCM_16")
    print(f"  {nom:22} {len(x) / SR:5.2f} s")


def pop():
    """La bulle qui arrive : une goutte, la hauteur qui tombe vite, et un rien de clic au début."""
    t = t_(0.16)
    f = 380 + 820 * np.exp(-t / 0.018)
    phase = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(phase) * np.exp(-t / 0.045) + 0.18 * np.sin(2 * phase) * np.exp(-t / 0.02)
    clic = passe_bande(GRAINE.standard_normal(len(t)), 2500, 7000) * np.exp(-t / 0.0015) * 0.35
    ecrire("pop.wav", (x + clic) * env(len(t), 0.0015, 0.03), -3)


def clic():
    """Le doigt sur « Commander » : le petit choc du verre, un mode aigu qui meurt vite, et le sourd du doigt."""
    t = t_(0.09)
    choc = passe_bande(GRAINE.standard_normal(len(t)), 1800, 6500) * np.exp(-t / 0.0025)
    mode = np.sin(2 * np.pi * 2300 * t) * np.exp(-t / 0.009) * 0.5
    sourd = np.sin(2 * np.pi * 170 * t) * np.exp(-t / 0.018) * 0.7
    ecrire("clic.wav", (choc + mode + sourd) * env(len(t), 0.0005, 0.02), -4)


def cloche(f, d, partiels=((1, 1.0, 1.3), (2.0, 0.18, 0.5), (2.76, 0.32, 0.55), (5.4, 0.12, 0.22))):
    t = t_(d)
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / tau) for r, a, tau in partiels)
    return x * env(len(t), 0.004, 0.2)


def carillon():
    """La commande qui arrive : deux notes de cloche douce (sol, puis ré), rien qui rappelle une application."""
    d = 1.9
    x = np.zeros(int(d * SR))
    for debut, f, g in ((0.0, 784.0, 1.0), (0.14, 1174.7, 0.8)):
        c = cloche(f, d - debut) * g
        i = int(debut * SR)
        x[i:i + len(c)] += c[: len(x) - i]
    ecrire("carillon.wav", passe_bas(x, 7000), -5)


def souffle():
    """Le grand texte : un souffle d'air qui monte puis retombe, la bande qui s'ouvre vers l'aigu."""
    d = 1.3
    t = t_(d)
    bruit = GRAINE.standard_normal(len(t))
    bas = passe_bande(bruit, 250, 1400)
    haut = passe_bande(bruit, 1400, 6000)
    ouverture = np.clip(t / 0.45, 0, 1)
    forme = np.where(t < 0.42, (t / 0.42) ** 1.6, np.exp(-(t - 0.42) / 0.32))
    x = (bas * (1 - 0.6 * ouverture) + haut * ouverture * 0.55) * forme
    ecrire("souffle.wav", x * env(len(t), 0.01, 0.15), -4)


def glisse():
    """Ce qui s'en va (la bulle qui part ailleurs) : un souffle court qui descend."""
    d = 0.55
    t = t_(d)
    bruit = GRAINE.standard_normal(len(t))
    x = np.zeros_like(t)
    for k, (a, b) in enumerate(((3500, 6500), (1800, 3500), (800, 1800))):
        poids = np.exp(-((t - 0.08 - k * 0.12) / 0.09) ** 2)
        x += passe_bande(bruit, a, b) * poids
    ecrire("glisse.wav", x * env(len(t), 0.005, 0.1), -6)


def tic():
    """Le compteur de vues, les lettres tapées : un tic de verre, très court."""
    t = t_(0.04)
    x = passe_bande(GRAINE.standard_normal(len(t)), 2500, 8000) * np.exp(-t / 0.0012)
    x += np.sin(2 * np.pi * 3100 * t) * np.exp(-t / 0.005) * 0.4
    ecrire("tic.wav", x * env(len(t), 0.0003, 0.01), -6)


def eclat():
    """La lumière qui brille (le lien, les étincelles de Noël) : quelques tintements aigus, de plus en plus rares."""
    d = 1.4
    x = np.zeros(int(d * SR))
    instants = [0.0, 0.07, 0.16, 0.3, 0.5, 0.78]
    for k, debut in enumerate(instants):
        f = GRAINE.uniform(2600, 5200)
        c = cloche(f, d - debut, partiels=((1, 1.0, 0.35), (2.76, 0.25, 0.12))) * (0.9 ** k)
        i = int(debut * SR)
        x[i:i + len(c)] += c[: len(x) - i]
    ecrire("eclat.wav", x, -9)


def neon():
    """L'enseigne : le claquement d'allumage (un déclic et un grésillement), puis le bourdonnement du gaz, 100 Hz
    (le secteur à 50 Hz) et ses harmoniques, qui boucle sans couture sur 3 s (300 périodes, modulations entières)."""
    t = t_(0.16)
    declic = passe_bande(GRAINE.standard_normal(len(t)), 1500, 9000) * np.exp(-t / 0.003)
    gresil = sum(np.sin(2 * np.pi * 100 * h * t) / h ** 0.7 for h in range(1, 14)) * np.exp(-t / 0.05) * 0.25
    crepite = passe_haut(GRAINE.standard_normal(len(t)), 3000) * (GRAINE.random(len(t)) > 0.985) * np.exp(-t / 0.06)
    ecrire("neon-allume.wav", (declic + gresil + crepite * 0.8) * env(len(t), 0.0003, 0.03), -4)

    d = 3.0
    t = t_(d)
    x = sum((1 / h ** 1.1) * np.sin(2 * np.pi * 100 * h * t + GRAINE.uniform(0, 6.28)) for h in range(1, 24))
    x *= 1 + 0.08 * np.sin(2 * np.pi * 1.0 * t)                      # la respiration du gaz (1 cycle par seconde)
    fizz = passe_bande(GRAINE.standard_normal(len(t)), 4000, 9000) * 0.05
    fizz = np.concatenate([fizz[len(fizz) // 2:], fizz[: len(fizz) // 2]])  # sans couture : on raccorde au milieu
    fondu = np.minimum(1, np.minimum(t, d - t) / 0.4)
    fizz = fizz * fondu + np.roll(fizz, len(fizz) // 2) * (1 - fondu)
    ecrire("neon-bourdon.wav", passe_bas(x, 3000) * 0.9 + fizz, -6)


def sons():
    (DOSSIER / "sfx").mkdir(parents=True, exist_ok=True)
    print("bruitages :")
    for f in (pop, clic, carillon, souffle, glisse, tic, eclat, neon):
        f()


# ─────────────────────────────── 3. la musique ───────────────────────────────

def musique(debut=0.0, duree=52.0, lufs=-28.0):
    """Coupée (50 s suffisent pour 42 s de pub), ramenée à -28 LUFS en deux passes. Les fondus se font dans la vidéo,
    qui connaît sa durée par `minutage.json`."""
    if not MUSIQUE.exists():
        raise SystemExit(f"musique introuvable : {MUSIQUE}")
    coupe = f"atrim=start={debut}:duration={duree},asetpts=PTS-STARTPTS"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(MUSIQUE), "-af",
                        f"{coupe},loudnorm=I={lufs}:TP=-6:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    j = r.stderr
    m = json.loads(j[j.rindex("{"): j.rindex("}") + 1])
    chaine = (f"{coupe},loudnorm=I={lufs}:TP=-6:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
              f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}"
              ":linear=true")
    sortie = DOSSIER / "musique.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-i", str(MUSIQUE), "-af", chaine, "-ar", str(SR),
                    "-ac", "2", "-c:a", "pcm_s16le", str(sortie)], check=True, capture_output=True)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(sortie), "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    print(f"musique : {MUSIQUE.name} → {sortie.relative_to(ICI)} ({duree:.0f} s, {i[-1] if i else '?'} LUFS)")


def grain():
    """Le grain de l'image filmée : des points clairs et sombres presque transparents, en tuile de 384 px. Il casse
    aussi les marches d'escalier des dégradés sombres, que la compression de TikTok creuse."""
    n = 384
    g = np.random.default_rng(7)
    clair = g.random((n, n)) > 0.5
    rgb = np.where(clair[..., None], 255, 0).astype(np.uint8).repeat(3, axis=2)
    alpha = (g.random((n, n)) ** 2 * 34).astype(np.uint8)
    Image.fromarray(np.concatenate([rgb, alpha[..., None]], axis=2), "RGBA").save(DOSSIER / "grain.png", optimize=True)
    print("grain : grain.png")


if __name__ == "__main__":
    voulu = sys.argv[1:] or ["neon", "sons", "musique", "grain"]
    if "grain" in voulu:
        grain()
    if "neon" in voulu:
        enseigne()
    if "sons" in voulu:
        sons()
    if "musique" in voulu:
        musique()

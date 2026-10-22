"""MA LETTRE À… · « Minuit pile, pour maman » : prépare la matière du film dans `public/malettre-minuit/`.

    python _outils/malettre_minuit_preparer.py

`public/` est ignoré par git (dépôt public) : rien de ce qui suit n'y part, tout se refait ici.

    · les FONDS d'ambiance de la vitrine, en JPEG, depuis leurs originaux (`_partage/ma lettre/fonds/
      <zone>-paysage.png`, les images de Mongazi, plus fines que les WebP du site) ;
    · la MARQUE : le cachet aux trois points du site (`malettre/logo/cachet.svg`), tel quel ;
    · un GRAIN de pellicule (une tuile de bruit qu'on décale à chaque image) ;
    · les BRUITAGES, tous synthétisés ici : aucun fichier venu d'ailleurs, aucune licence.

Les musiques (Pixabay) ne passent pas par ici : `malettre_minuit_son.py` les lit dans `_partage/`.
⛔ Ce sont des AMBIANCES : jamais présentées comme une vraie lettre, un vrai client, ni le produit lui-même.

⚠️ Un son de synthèse se MESURE, il ne s'écoute pas de confiance (leçon du 2026-10-22, le clic de
verre coupé à −35 dB) : chaque bruitage est imprimé avec sa durée, son pic et le niveau de sa fin.
"""
import shutil
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.signal import lfilter

sys.stdout.reconfigure(encoding="utf-8")
ICI = Path(__file__).resolve().parent.parent
RACINE = ICI.parent
SORTIE = ICI / "public" / "malettre-minuit"
SR = 48000
ALEA = np.random.default_rng(20261022)

# Les zones de la vitrine que le film montre (la chambre, Paris, la plume, le cachet, la nuit).
FONDS = ["seuil", "heros", "plume", "promesses", "nuit"]


def fonds():
    for zone in FONDS:
        src = RACINE / "_partage" / "ma lettre" / "fonds" / (zone + "-paysage.png")
        if not src.exists():
            sys.exit("⛔ fond introuvable : %s" % src)
        im = Image.open(src).convert("RGB")
        im.save(SORTIE / (zone + ".jpg"), quality=93)  # le réglage du rendu du 2026-10-22 : refait à l'octet près
        print("fond    %-13s %dx%d  ← %s" % (zone + ".jpg", im.width, im.height, src.name))


def marque():
    src = RACINE / "malettre" / "logo" / "cachet.svg"
    shutil.copyfile(src, SORTIE / "logo-cachet.svg")
    print("marque  logo-cachet.svg  ← malettre/logo/cachet.svg")


def grain():
    g = ALEA.normal(128, 38, (512, 512)).clip(0, 255).astype(np.uint8)
    Image.fromarray(g, "L").save(SORTIE / "grain.png")
    print("grain   grain.png 512x512")


# ── les outils du son ─────────────────────────────────────────────────────────
def t_(duree):
    return np.arange(int(SR * duree)) / SR


def env(n, att=0.002, fin=0.01):
    e = np.ones(n)
    a, f = max(1, int(SR * att)), max(1, int(SR * fin))
    e[:a] = np.linspace(0, 1, a)
    e[-f:] *= np.linspace(1, 0, f)
    return e


def passe_bas(x, fc):
    """Un pôle : y[n] = (1 − a)·x[n] + a·y[n − 1]."""
    a = np.exp(-2 * np.pi * fc / SR)
    return lfilter([1 - a], [1, -a], x)


def passe_haut(x, fc):
    return x - passe_bas(x, fc)


def resonateur(n, f, tau, a=1.0):
    """a·rⁿ·sin(ωn) : un mode qui sonne et meurt (le même calcul que le clic du site)."""
    i = np.arange(n)
    return a * np.exp(-i / (tau * SR)) * np.sin(2 * np.pi * f * i / SR)


def verre(survol=False, cristal=False, graine=0):
    """Le clic de verre du site (verre fin), ou le cristal (la coupe effleurée)."""
    r = np.random.default_rng(graine)
    if cristal:
        f0, rr, tau, a, duree = 2350, [1, 2.28, 3.93, 5.84], [.26, .12, .06, .03], [1, .45, .25, .12], 1.35
    else:
        f0, rr, tau, a, duree = 3150, [1, 1.47, 2.09, 2.83, 3.71], [.06, .038, .024, .016, .01], [1, .6, .42, .25, .15], .32
    court = .45 if survol else 1
    n = int(SR * duree * (.5 if survol else 1))
    k = (1 + r.uniform(-.025, .025)) * (1.12 if survol else 1)
    d = np.zeros(n)
    for j in range(len(rr)):
        f = f0 * rr[j] * k * (1 + r.uniform(-.006, .006))
        d += resonateur(n, f, tau[j] * court, a[j])
        if j < 2:
            d += resonateur(n, f * (1 + .004 * (j + 1)), tau[j] * .9 * court, a[j] * .45)
    tb = SR * .00045
    m = min(n, int(tb * 7))
    bruit = r.uniform(-1, 1, m + 1)
    d[:m] += (.54 if survol else .9) * np.diff(bruit) * np.exp(-np.arange(m) / tb)
    return d * env(n, .0003, .008)


def normaliser(x, pic_db=-3.0):
    return x / (np.abs(x).max() + 1e-12) * 10 ** (pic_db / 20)


def ecrire(nom, x, pic_db=-3.0, stereo=None):
    x = normaliser(x, pic_db)
    if stereo is None:
        st = np.stack([x, x], 1)
    else:
        st = stereo / (np.abs(stereo).max() + 1e-12) * 10 ** (pic_db / 20)
    data = (st * 32767).astype(np.int16)
    with wave.open(str(SORTIE / nom), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    mono = st.mean(1)
    pic = np.abs(mono).max()
    queue = np.sqrt(np.mean(mono[-int(SR * .02):] ** 2)) + 1e-12
    print("son     %-13s %5.2f s · pic %5.1f dBFS · fin %6.1f dB sous le pic"
          % (nom, len(mono) / SR, 20 * np.log10(pic + 1e-12), 20 * np.log10(queue / pic)))


# ── les bruitages ─────────────────────────────────────────────────────────────
def pluie():
    """La pluie sur la vitre de Paris : un souffle large, et des gouttes qui tombent, chacune à sa place."""
    n = int(SR * 9.0)
    voies = []
    for v in range(2):
        b = ALEA.normal(0, 1, n)
        nappe = passe_bas(passe_haut(b, 700), 5200) * .35
        gouttes = np.zeros(n)
        for _ in range(520):
            i = ALEA.integers(0, n - 2400)
            f = ALEA.uniform(1800, 5200)
            gouttes[i:i + 2400] += resonateur(2400, f, ALEA.uniform(.003, .012), ALEA.uniform(.1, .5))
        voies.append(nappe + gouttes * .5)
    st = np.stack(voies, 1) * env(n, .8, 1.5)[:, None]
    ecrire("pluie.wav", st.mean(1), -9, st)


def tictac():
    """Le tic de la pendule : un bloc de bois, deux hauteurs (tic, tac)."""
    for nom, f in (("tic.wav", 2600), ("tac.wav", 2100)):
        n = int(SR * .12)
        x = resonateur(n, f, .012) + resonateur(n, f * 2.7, .006, .5) + resonateur(n, 900, .02, .4)
        b = ALEA.normal(0, 1, n) * np.exp(-np.arange(n) / (SR * .0015)) * .6
        ecrire(nom, (x + b) * env(n, .0005, .01), -6)


def coeur():
    """Un battement : deux coups sourds (lub-dub), sous la musique qui se tait."""
    n = int(SR * .7)
    x = np.zeros(n)
    for debut, f, a in ((0, 52, 1.0), (int(SR * .19), 46, .7)):
        m = n - debut
        tt = np.arange(m) / SR
        glisse = f * (1 + .6 * np.exp(-tt / .02))
        phase = 2 * np.pi * np.cumsum(glisse) / SR
        x[debut:] += a * np.sin(phase) * np.exp(-tt / .09)
    ecrire("coeur.wav", passe_bas(x, 180) * env(n, .003, .05), -4)


def notif():
    """La notification : deux clics de verre du site, à 0,13 s."""
    a, b = verre(graine=1), verre(graine=2) * .8
    n = len(a) + int(SR * .13)
    x = np.zeros(n)
    x[:len(a)] += a
    x[int(SR * .13):int(SR * .13) + len(b)] += b
    ecrire("notif.wav", x, -6)
    ecrire("clic.wav", verre(graine=3), -6)


def embrase():
    """Minuit : la cire s'embrase. Un grondement grave, et un scintillement qui monte."""
    n = int(SR * 2.2)
    tt = t_(2.2)
    grave = np.sin(2 * np.pi * (38 + 14 * np.exp(-tt / .3)) * tt) * np.exp(-tt / .9)
    b = ALEA.normal(0, 1, n)
    montee = passe_haut(b, 3000) * np.clip(tt / 1.2, 0, 1) ** 2 * np.exp(-np.clip(tt - 1.2, 0, None) / .35) * .25
    eclats = np.zeros(n)
    for _ in range(40):
        i = int(ALEA.uniform(.2, 1.6) * SR)
        m = min(n - i, int(SR * .25))
        eclats[i:i + m] += resonateur(m, ALEA.uniform(3200, 7600), ALEA.uniform(.03, .09), ALEA.uniform(.05, .18))
    ecrire("embrase.wav", (grave * .9 + montee + eclats) * env(n, .01, .3), -3)


def eclat():
    """Le cachet se brise : un claquement net, les éclats de cire, un souffle, et le grave qui porte."""
    n = int(SR * 1.8)
    tt = t_(1.8)
    b = ALEA.normal(0, 1, n)
    claque = passe_haut(b, 1500) * np.exp(-tt / .012) * 1.2
    sous = np.sin(2 * np.pi * (60 * np.exp(-tt / .15) + 34) * tt) * np.exp(-tt / .35) * .9
    eclats = np.zeros(n)
    for _ in range(14):
        i = int(ALEA.uniform(.01, .5) * SR)
        m = min(n - i, int(SR * .08))
        eclats[i:i + m] += resonateur(m, ALEA.uniform(1400, 4200), ALEA.uniform(.008, .02), ALEA.uniform(.15, .4))
    souffle = passe_bas(passe_haut(b, 400), 4000) * np.sin(np.pi * np.clip(tt / 1.1, 0, 1)) * .35
    ecrire("eclat.wav", (claque + sous + eclats + souffle) * env(n, .0005, .3), -2)


def etoiles():
    """La pluie d'étoiles : des tintements d'or, de plus en plus rares, éparpillés à gauche et à droite."""
    n = int(SR * 3.0)
    g, d = np.zeros(n), np.zeros(n)
    for k in range(46):
        moment = 2.6 * (k / 46) ** 1.6 + ALEA.uniform(0, .08)
        i = int(moment * SR)
        m = min(n - i, int(SR * .5))
        s = resonateur(m, ALEA.uniform(3400, 7800), ALEA.uniform(.05, .16), ALEA.uniform(.15, .45) * (1 - k / 60))
        pan = ALEA.uniform(0, 1)
        g[i:i + m] += s * np.sqrt(1 - pan)
        d[i:i + m] += s * np.sqrt(pan)
    st = np.stack([g, d], 1) * env(n, .002, .3)[:, None]
    ecrire("etoiles.wav", st.mean(1), -6, st)


def papier():
    """La feuille qui se déplie : un froissement doux, deux temps (deux plis)."""
    n = int(SR * 1.1)
    tt = t_(1.1)
    b = ALEA.normal(0, 1, n)
    grain_ = passe_bas(passe_haut(b, 1200), 7000)
    mod = np.abs(passe_bas(ALEA.normal(0, 1, n), 40)) * 6
    forme = np.exp(-((tt - .25) / .12) ** 2) + .8 * np.exp(-((tt - .62) / .14) ** 2)
    ecrire("papier.wav", grain_ * mod * forme * env(n, .01, .1), -8)


def souffle():
    """Le recul vers le ciel : un souffle qui passe."""
    n = int(SR * 1.6)
    tt = t_(1.6)
    b = ALEA.normal(0, 1, n)
    x = passe_bas(passe_haut(b, 250), 2600) * np.sin(np.pi * np.clip(tt / 1.6, 0, 1)) ** 2
    ecrire("souffle.wav", x * env(n, .05, .2), -6)


def tin():
    ecrire("tin.wav", verre(cristal=True, graine=7), -6)


def tampon():
    """Le cachet qu'on presse : un coup sourd, la cire qui s'écrase un peu."""
    n = int(SR * .6)
    tt = t_(.6)
    coup = np.sin(2 * np.pi * (85 * np.exp(-tt / .05) + 42) * tt) * np.exp(-tt / .12)
    b = ALEA.normal(0, 1, n)
    ecrase = passe_bas(b, 900) * np.exp(-tt / .05) * .5
    ecrire("tampon.wav", (coup + ecrase) * env(n, .001, .05), -3)


def insiste():
    """Insister pour ouvrir : trois tapotements d'ongle sur la cire, puis le verrou qui dit non."""
    n = int(SR * 1.2)
    x = np.zeros(n)
    for k, moment in enumerate((0.0, .17, .34)):
        i = int(moment * SR)
        m = int(SR * .09)
        x[i:i + m] += (resonateur(m, 1900 + 120 * k, .01) + resonateur(m, 720, .018, .6)) * (.8 + .1 * k)
    i = int(.62 * SR)
    m = n - i
    tt = np.arange(m) / SR
    x[i:] += np.sin(2 * np.pi * (140 * np.exp(-tt / .04) + 60) * tt) * np.exp(-tt / .09) * 1.1
    x[i:i + int(SR * .05)] += resonateur(int(SR * .05), 2600, .006, .5)
    ecrire("insiste.wav", x * env(n, .001, .05), -4)


def plume():
    """La plume qui écrit : le bec qui gratte le papier, par traits."""
    n = int(SR * 2.4)
    tt = t_(2.4)
    b = ALEA.normal(0, 1, n)
    gratte = passe_bas(passe_haut(b, 2500), 9000)
    traits = np.zeros(n)
    t0 = 0.0
    while t0 < 2.3:
        d = ALEA.uniform(.12, .32)
        i0, i1 = int(t0 * SR), int(min(2.4, t0 + d) * SR)
        traits[i0:i1] = np.sin(np.linspace(0, np.pi, i1 - i0)) * ALEA.uniform(.5, 1)
        t0 += d + ALEA.uniform(.03, .12)
    ecrire("plume.wav", gratte * traits * env(n, .01, .1), -10)


def occupe():
    """« Raccroché au nez » : le petit déclic, puis la tonalité occupée (deux bips)."""
    n = int(SR * 1.15)
    x = np.zeros(n)
    x[:int(SR * .03)] += resonateur(int(SR * .03), 1800, .004, .8)
    for debut in (.18, .63):
        i = int(debut * SR)
        m = int(SR * .3)
        tt = np.arange(m) / SR
        x[i:i + m] += (np.sin(2 * np.pi * 425 * tt) * .6 + np.sin(2 * np.pi * 850 * tt) * .15) * env(m, .005, .02)
    ecrire("occupe.wav", x, -8)


def emballe():
    """La demande : un cœur qui s'emballe, quatre battements de plus en plus serrés."""
    n = int(SR * 1.6)
    x = np.zeros(n)
    t0 = 0.0
    for k in range(4):
        for decale, f, a in ((0, 56, 1.0), (.15, 48, .65)):
            i = int((t0 + decale) * SR)
            m = min(n - i, int(SR * .35))
            if m <= 0:
                continue
            tt = np.arange(m) / SR
            x[i:i + m] += a * np.sin(2 * np.pi * f * (1 + .5 * np.exp(-tt / .02)) * tt) * np.exp(-tt / .08)
        t0 += .42 - k * .05
    ecrire("emballe.wav", passe_bas(x, 200) * env(n, .002, .05), -4)


def pop():
    """La soirée entre potes : un bouchon qui saute, une pluie de confettis."""
    n = int(SR * 1.6)
    tt = t_(1.6)
    x = np.zeros(n)
    m = int(SR * .06)
    x[:m] += resonateur(m, 520, .012, 1.0) + ALEA.normal(0, 1, m) * np.exp(-np.arange(m) / (SR * .004)) * .8
    for _ in range(60):
        i = int(ALEA.uniform(.08, 1.3) * SR)
        mm = min(n - i, int(SR * .03))
        x[i:i + mm] += passe_haut(ALEA.normal(0, 1, mm), 3000) * np.exp(-np.arange(mm) / (SR * .006)) * ALEA.uniform(.05, .2)
    ecrire("pop.wav", x * env(n, .001, .2), -4)


def frappe():
    """Le prénom qu'on tape : cinq touches douces."""
    n = int(SR * 1.0)
    x = np.zeros(n)
    for k in range(5):
        i = int((k * .16 + ALEA.uniform(0, .02)) * SR)
        m = int(SR * .05)
        x[i:i + m] += resonateur(m, ALEA.uniform(2400, 3100), .006, .7) + resonateur(m, 380, .01, .3)
    ecrire("frappe.wav", x * env(n, .001, .05), -8)


def swish():
    """Un passage court, pour les changements de plan sur le temps."""
    n = int(SR * .45)
    tt = t_(.45)
    b = ALEA.normal(0, 1, n)
    x = passe_bas(passe_haut(b, 600), 6000) * np.sin(np.pi * np.clip(tt / .45, 0, 1)) ** 3
    ecrire("swish.wav", x, -10)


if __name__ == "__main__":
    SORTIE.mkdir(parents=True, exist_ok=True)
    fonds()
    marque()
    grain()
    for f in (pluie, tictac, coeur, notif, embrase, eclat, etoiles, papier, souffle, tin,
              tampon, insiste, plume, occupe, emballe, pop, frappe, swish):
        f()
    print("✓ public/malettre-minuit prêt")

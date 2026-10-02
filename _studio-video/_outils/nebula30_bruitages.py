"""Les bruitages de la vidéo de marque NEBULA (30 s), SYNTHÉTISÉS : aucun fichier
tiers, aucun droit à gérer. Un son par geste du film, en stéréo.

    battement   le cœur de l'étoile, avant tout          aspiration  l'air aspiré avant l'explosion
    impact      l'explosion de la nébuleuse               scintille   la poussière d'étoiles
    whoosh      un passage rapide                         souffle     un mouvement de caméra, grave
    trace       le plan d'architecte qui se dessine       pose        un élément qui se pose
    carte       une fiche produit qui passe               commande    une commande qui arrive
    module      un module qui s'emboîte                   donnee      un chiffre qui s'affiche
    montee      la tension avant que tout se fige         arret       tout s'arrête net
    rembobine   la tête de lecture qui recule             declic      le déclic du logiciel de montage
    etincelle   l'éclat d'une étoile                      touche1..4  une touche de clavier
    envoi       un message qui part                       implosion   tout revient au centre
    final       l'étoile du logo s'allume                 nappe       le fond de l'espace (boucle)

⚠️ Le son de notification n'imite PAS celui de WhatsApp : c'est la marque d'un
autre. Deux notes à nous, une quinte au-dessus d'un petit pop.

Chaque son est normalisé à −3 dBFS de crête ; le volume se règle au montage.

    python _outils/nebula30_bruitages.py
"""
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

ICI = Path(__file__).resolve().parent.parent
DOSSIER = ICI / "public/nebula30/sfx"
SR = 44100
rng = np.random.default_rng(30)


def t(duree):
    return np.arange(int(SR * duree)) / SR


def env(duree, attaque, chute):
    x = t(duree)
    return np.minimum(1, x / max(attaque, 1e-4)) * np.exp(-x / chute)


def filtre(x, bas=None, haut=None, ordre=2):
    if bas and haut:
        sos = signal.butter(ordre, [bas, haut], btype="band", fs=SR, output="sos")
    elif bas:
        sos = signal.butter(ordre, bas, btype="high", fs=SR, output="sos")
    else:
        sos = signal.butter(ordre, haut, btype="low", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def bruit(duree):
    return rng.standard_normal(int(SR * duree))


def balayage(x, f_debut, f_fin, largeur=0.5, blocs=40, courbe=1.0):
    """Un filtre passe-bande dont la fréquence glisse de f_debut à f_fin, par blocs."""
    n = len(x)
    sortie = np.zeros(n)
    for k in range(blocs):
        a, b = k * n // blocs, (k + 1) * n // blocs
        fc = f_debut * (f_fin / f_debut) ** ((k / blocs) ** courbe)
        sortie[a:b] = filtre(x[max(0, a - 3000):b], fc * (1 - largeur), min(fc * (1 + largeur), SR / 2 - 100))[-(b - a):]
    return sortie


def ton(frequences, duree):
    """Une sinusoïde dont la fréquence suit un tableau (glissando sans clic)."""
    f = np.broadcast_to(frequences, (int(SR * duree),))
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def stereo(gauche, droite=None):
    return np.stack([gauche, gauche if droite is None else droite], axis=1)


def panoramique(x, depart, arrivee):
    """Fait voyager un son mono de gauche (−1) à droite (+1)."""
    p = np.linspace(depart, arrivee, len(x))
    angle = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(angle), x * np.sin(angle)], axis=1)


def reverb(x, duree=2.2, melange=0.35, clair=6000):
    """Réverbération par convolution : deux queues de bruit décorrélées (gauche, droite)."""
    if x.ndim == 1:
        x = stereo(x)
    n = int(SR * duree)
    queue = np.exp(-np.arange(n) / SR / (duree / 6.9))
    sortie = np.zeros((len(x) + n - 1, 2))
    for c in range(2):
        ir = filtre(rng.standard_normal(n), haut=clair) * queue
        ir /= np.sqrt((ir ** 2).sum())
        sortie[:, c] = signal.fftconvolve(x[:, c], ir)
    sec = np.zeros_like(sortie)
    sec[: len(x)] = x
    return sec * (1 - melange) + sortie * melange * 3


def ecrire(nom, x):
    if x.ndim == 1:
        x = stereo(x)
    x = x / (np.abs(x).max() + 1e-9) * 10 ** (-3 / 20)
    fondu = int(0.006 * SR)
    x[-fondu:] *= np.linspace(1, 0, fondu)[:, None]
    wavfile.write(DOSSIER / f"{nom}.wav", SR, np.round(x * 32767).astype(np.int16))


# ---------------------------------------------------------------- les sons

def battement():
    sortie = np.zeros(int(SR * 0.9))
    for debut, force in ((0.0, 1.0), (0.27, 0.7)):
        x = t(0.35)
        coup = ton(72 * np.exp(-x * 9) + 40, 0.35) * env(0.35, 0.003, 0.11)
        peau = filtre(bruit(0.35), 150, 700) * env(0.35, 0.001, 0.02) * 0.4
        a = int(SR * debut)
        sortie[a:a + len(x)] += (coup + peau) * force
    return reverb(sortie, 1.2, 0.18, 1500)


def aspiration():
    d = 1.4
    x = t(d)
    souffle = balayage(bruit(d), 250, 7000, 0.35, courbe=1.6)
    monte = ton(90 * (1 + 7 * (x / d) ** 2.2), d) * 0.35
    forme = (x / d) ** 3.2
    g = (souffle + monte) * forme
    dr = (balayage(bruit(d), 260, 7200, 0.35, courbe=1.6) + monte) * forme
    return stereo(g, dr)


def impact():
    d = 3.6
    x = t(d)
    sub = ton(56 * np.exp(-x * 1.4) + 24, d) * env(d, 0.002, 1.1)
    corps = filtre(bruit(d), 60, 520, 3) * env(d, 0.001, 0.28) * 1.6
    craque = filtre(bruit(d), 2200, 12000) * env(d, 0.0005, 0.045) * 1.2
    eclat = filtre(bruit(d), 4500, 14000) * env(d, 0.02, 0.9) * 0.12
    return reverb(sub * 1.5 + corps + craque + eclat, 2.8, 0.3, 4000)


def scintille():
    d = 1.8
    sortie = np.zeros((int(SR * d), 2))
    for _ in range(140):
        debut = rng.random() ** 0.7 * (d - 0.25)
        f = rng.uniform(3200, 10500)
        x = t(0.22)
        grain = np.sin(2 * np.pi * f * x) * env(0.22, 0.001, rng.uniform(0.02, 0.07)) * rng.uniform(0.2, 1)
        p = rng.uniform(-1, 1)
        a = int(SR * debut)
        sortie[a:a + len(x)] += panoramique(grain, p, p)
    return reverb(sortie, 1.8, 0.45, 9000)


def whoosh():
    d = 0.75
    x = t(d)
    corps = balayage(bruit(d), 300, 3200, 0.45, courbe=1.2)
    forme = np.sin(np.pi * np.clip(x / d, 0, 1)) ** 2.2
    return reverb(panoramique(corps * forme, -0.8, 0.8), 0.8, 0.15)


def souffle():
    d = 1.1
    x = t(d)
    corps = balayage(bruit(d), 70, 700, 0.5, courbe=1.3)
    forme = np.sin(np.pi * np.clip(x / d, 0, 1)) ** 1.6
    return reverb(panoramique(corps * forme, 0.6, -0.6), 1.2, 0.2, 2000)


def trace():
    d = 1.1
    sortie = np.zeros(int(SR * d))
    instants = np.cumsum(rng.uniform(0.012, 0.045, 60))
    for k, debut in enumerate(instants[instants < d - 0.02]):
        x = t(0.012)
        clic = filtre(bruit(0.012), 2500, 9000) * env(0.012, 0.0002, 0.0018) * rng.uniform(0.4, 1)
        a = int(SR * debut)
        sortie[a:a + len(x)] += clic
    grattage = filtre(bruit(d), 3000, 7000) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t(d))) * 0.06
    forme = np.minimum(1, t(d) / 0.05) * np.minimum(1, (d - t(d)) / 0.1)
    return reverb((sortie + grattage) * forme, 0.5, 0.12)


def pose():
    d = 0.22
    x = t(d)
    thump = ton(160 * np.exp(-x * 25) + 90, d) * env(d, 0.001, 0.05)
    clic = filtre(bruit(d), 2000, 8000) * env(d, 0.0003, 0.004) * 0.6
    return reverb(thump + clic, 0.4, 0.12)


def carte():
    d = 0.16
    x = t(d)
    froisse = filtre(bruit(d), 1200, 6000) * env(d, 0.002, 0.03)
    return panoramique(froisse + ton(1800 - 4000 * x, d) * env(d, 0.001, 0.02) * 0.2, -0.3, 0.3)


def commande():
    d = 0.75
    x = t(d)
    pop = ton(520 + 520 * np.minimum(1, x / 0.05), d) * env(d, 0.001, 0.035)
    note1 = (np.sin(2 * np.pi * 1046.5 * x) + 0.3 * np.sin(2 * np.pi * 2093 * x)) * env(d, 0.002, 0.12)
    retard = int(0.085 * SR)
    note2 = np.zeros_like(x)
    note2[retard:] = ((np.sin(2 * np.pi * 1568 * x) + 0.25 * np.sin(2 * np.pi * 3136 * x)) * env(d, 0.002, 0.2))[: len(x) - retard]
    return reverb(pop * 0.7 + note1 * 0.6 + note2, 0.9, 0.22, 8000)


def module():
    d = 0.14
    x = t(d)
    clic = filtre(bruit(d), 3000, 9000) * env(d, 0.0002, 0.003)
    thock = ton(210 * np.exp(-x * 30) + 120, d) * env(d, 0.001, 0.025)
    return clic * 0.8 + thock


def donnee():
    d = 0.07
    x = t(d)
    chirp = np.sign(np.sin(2 * np.pi * np.cumsum(2100 + 1500 * x / d) / SR))
    return filtre(chirp, haut=6000) * env(d, 0.001, 0.02)


def montee():
    d = 1.7
    x = t(d)
    sirene = ton(160 * (1 + 9 * (x / d) ** 2), d)
    tremolo = 0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(4 + 26 * (x / d) ** 2) / SR)
    vent = balayage(bruit(d), 400, 6000, 0.4, courbe=1.5)
    forme = (x / d) ** 2.4
    return reverb(stereo((sirene * 0.5 + vent * 0.6) * tremolo * forme), 1.0, 0.18)


def arret():
    d = 0.75
    x = t(d)
    chute = np.maximum(0, 1 - x / 0.62) ** 1.8
    accord = sum(signal.sawtooth(2 * np.pi * np.cumsum(f * chute) / SR) for f in (110, 138.6, 164.8, 220))
    grave = filtre(accord, haut=2500) * np.maximum(0, 1 - x / 0.65) ** 0.8
    return stereo(grave * 0.6)


def rembobine():
    d = 1.0
    x = t(d)
    jacasse = balayage(bruit(d), 900, 5500, 0.35, courbe=0.8)
    hachure = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * np.cumsum(18 + 30 * x) / SR))
    sifflet = ton(600 + 2600 * (x / d) ** 1.4, d) * 0.18
    forme = np.minimum(1, x / 0.08) * np.minimum(1, (d - x) / 0.12)
    return reverb(panoramique((jacasse * hachure + sifflet) * forme, 0.7, -0.7), 0.6, 0.15)


def declic():
    d = 0.12
    un = filtre(bruit(d), 1800, 9000) * env(d, 0.0002, 0.0025)
    deux = np.roll(un, int(0.024 * SR)) * 0.7
    return reverb(un + deux, 0.3, 0.1)


def etincelle():
    d = 1.6
    x = t(d)
    cloche = sum(a * np.sin(2 * np.pi * f * x) * env(d, 0.001, c)
                 for f, a, c in ((2637, 1, 0.42), (3951, 0.55, 0.3), (5274.5, 0.35, 0.22), (7040, 0.18, 0.14)))
    return reverb(cloche, 2.0, 0.4, 11000)


def touche(graine):
    r = np.random.default_rng(graine)
    d = 0.06
    x = t(d)
    clic = filtre(r.standard_normal(len(x)), 1800 + 400 * r.random(), 7000) * env(d, 0.0002, 0.004)
    corps = ton(380 + 120 * r.random(), d) * env(d, 0.001, 0.012) * 0.5
    return clic + corps


def envoi():
    d = 0.4
    x = t(d)
    monte = balayage(bruit(d), 700, 4200, 0.4, courbe=0.9) * np.sin(np.pi * np.clip(x / 0.3, 0, 1)) ** 2
    pop = ton(700 + 500 * np.minimum(1, np.maximum(0, x - 0.28) / 0.04), d) * env(d, 0.001, 0.04) * (x > 0.28)
    return reverb(panoramique(monte * 0.7 + pop, -0.4, 0.5), 0.6, 0.15)


def implosion():
    d = 1.25
    x = t(d)
    boum = ton(48 * np.exp(-x * 2) + 28, d) * env(d, 0.002, 0.5)
    vent = filtre(bruit(d), 300, 9000) * env(d, 0.001, 0.35)
    scint = sum(np.sin(2 * np.pi * f * x) * env(d, 0.001, 0.25) for f in (3100, 4700, 6300)) * 0.15
    a_l_envers = reverb((boum + vent * 0.6 + scint)[::-1], 0.6, 0.15)
    return a_l_envers[: int(SR * d)]


def final():
    d = 5.0
    x = t(d)
    sub = ton(52 * np.exp(-x * 1.1) + 26, d) * env(d, 0.002, 1.4)
    corps = filtre(bruit(d), 50, 450, 3) * env(d, 0.001, 0.32) * 1.4
    craque = filtre(bruit(d), 2500, 13000) * env(d, 0.0005, 0.05)
    # un accord clair (do majeur ouvert) qui s'allume avec l'étoile
    accord = sum(a * np.sin(2 * np.pi * f * x) for f, a in ((523.25, 1), (659.25, 0.7), (783.99, 0.75), (1046.5, 0.5), (1567.98, 0.25)))
    halo = accord * np.minimum(1, x / 0.08) * np.exp(-x / 1.8) * 0.35
    eclat = sum(np.sin(2 * np.pi * f * x) * env(d, 0.001, 0.6) for f in (2637, 3951, 5274.5)) * 0.12
    return reverb(sub * 1.6 + corps + craque * 0.8 + halo + eclat, 3.6, 0.38, 5000)


def nappe():
    d = 10.0
    x = t(d)
    drone = (np.sin(2 * np.pi * 55 * x) + np.sin(2 * np.pi * 55.35 * x) + 0.5 * np.sin(2 * np.pi * 82.4 * x)) * 0.3
    vent = filtre(bruit(d), 180, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * x / d * 2)) * 0.25
    vent2 = filtre(bruit(d), 190, 950) * (0.6 + 0.4 * np.cos(2 * np.pi * x / d * 2)) * 0.25
    # la boucle se referme sans couture : fondu croisé sur la dernière seconde
    g, dr = drone + vent, drone + vent2
    raccord = int(SR * 1.0)
    rampe = np.linspace(0, 1, raccord)
    for canal in (g, dr):
        canal[:raccord] = canal[:raccord] * rampe + canal[-raccord:] * (1 - rampe)
    return stereo(g[:-raccord], dr[:-raccord])


if __name__ == "__main__":
    DOSSIER.mkdir(parents=True, exist_ok=True)
    sons = [battement, aspiration, impact, scintille, whoosh, souffle, trace, pose, carte,
            commande, module, donnee, montee, arret, rembobine, declic, etincelle, envoi,
            implosion, final, nappe]
    for f in sons:
        ecrire(f.__name__, f())
        print("·", f.__name__)
    for k in range(1, 5):
        ecrire(f"touche{k}", touche(100 + k))
        print("·", f"touche{k}")
    print("→", DOSSIER)

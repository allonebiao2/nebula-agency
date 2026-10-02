"""Le son de la vidéo de marque NEBULA : la voix off placée, la musique montée.

ENTRÉES (public/nebula30/, hors dépôt) :
    voix-vous-brute.mp3   la prise ElevenLabs (Alimata, Eleven v4)
    musique-brute.mp3     « afro house » d'artissizm, Pixabay (licence Pixabay)
    transcription-vous.json   Whisper large-v3-turbo, au mot

SORTIES :
    public/nebula30/voix.wav      la voix nettoyée, découpée en répliques et posée
                                  sur la grille du film (30 s)
    public/nebula30/musique.wav   la musique montée et BAISSÉE SOUS LA VOIX
    src/nebula30/minutage.ts      les répliques et les mots en temps du film, et
                                  les instants musicaux : les animations s'y calent

LA VOIX. Mesurée sur la prise : 22,2 s, −26,6 LUFS (bien trop bas), crête
−6,6 dBFS, plancher −79 dB (une voix de synthèse : rien à débruiter).
Chaîne : passe-haut 70 Hz · présence +2,5 dB vers 3,2 kHz · compression 3:1 ·
−16 LUFS · limiteur −1,5 dBFS. On la découpe dans ses SILENCES (mesurés, jamais
dans un mot) et chaque réplique est posée à son instant du film.

LA MUSIQUE. Mesurée : 120 BPM pile (un temps = 0,5 s), mesures à 1,25 + 2k s,
montée de 15,25 à 31,25 s, CHUTE à 31,25 s, fin naturelle de 125 à 129 s.
    · l'explosion du film tombe sur un premier temps de la montée (piste 17,25 s) ;
    · l'image se FIGE pile là où la chute devait tomber (piste 31,25 s) :
      la musique s'arrête comme une bande qu'on freine ;
    · la chute éclate APRÈS « La vôtre est la prochaine » ;
    · le logo s'allume deux mesures plus tard, sur un premier temps ;
    · les dernières secondes reprennent la VRAIE fin du morceau.
Sous chaque phrase, la musique est baissée automatiquement (≈ −29 LUFS
momentanés au plus) : la voix passe toujours 12 à 14 LU au-dessus.

    python _outils/nebula30_son.py
"""
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

from dimanche_son import biquad, compresser, limiter, lufs

ICI = Path(__file__).resolve().parent.parent
PUB = ICI / "public/nebula30"
FFMPEG = ICI / "node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe"
SR = 44100
DUREE = 30.0

# ------------------------------------------------------------- le plan du film
# Les répliques, dans l'ordre de la prise, et l'instant du film où chacune COMMENCE
# à parler. La prise en compte 14 : ses 13 phrases mesurées, plus « Et même » et
# « cette vidéo » séparés dans leur silence (−60 dB entre 14,64 et 14,76 s).
REPLIQUES = [
    ("regardez", 0.45),
    ("toutCe", 2.25),
    ("nebulaCree", 3.75),
    ("vitrine", 6.20),
    ("marque", 7.55),
    ("catalogue", 9.30),
    ("commandes", 10.70),
    ("outil", 12.65),
    ("etMeme", 16.35),
    ("cetteVideo", 17.35),
    ("votre", 18.55),
    ("ecrivez", 20.45),
    ("nebulaAgency", 24.00),
    ("etoiles", 25.65),
]
COUPES_EN_PLUS = [14.70]  # le silence entre « même » et « cette »

# Les instants musicaux du film (secondes), tous sur la grille à 120 BPM.
BANG = 1.95                 # piste 17,25 s : premier temps d'une mesure de la montée
FIGE = BANG + 14.0          # piste 31,25 s : là où la chute devait tomber
CHUTE = 19.75               # la chute (piste 31,25 s), après « …la prochaine. »
HIT = CHUTE + 4.0           # deux mesures plus tard (piste 35,25 s) : le logo
RACCORD = CHUTE + 6.0       # on saute à la vraie fin du morceau (piste 123,25 s)
PISTE = {"montee": 17.25, "chute": 31.25, "fin": 123.25}


def lire(nom, canaux):
    tmp = ICI / f"out/_{nom}.wav"
    tmp.parent.mkdir(exist_ok=True)
    subprocess.run([str(FFMPEG), "-v", "error", "-y", "-i", str(PUB / nom), "-ac", str(canaux),
                    "-ar", str(SR), "-c:a", "pcm_s16le", str(tmp)], check=True)
    _, x = wavfile.read(tmp)
    return x.astype(np.float64) / 32768


def energie_db(x, fen_s=0.01):
    fen = int(fen_s * SR)
    return 20 * np.log10(np.sqrt(np.convolve(x ** 2, np.ones(fen) / fen, mode="same")) + 1e-9)


def phrases(x, seuil=-45, trou_min=0.18):
    """Les plages où la voix parle, séparées par des silences d'au moins trou_min."""
    parle = energie_db(x) > seuil
    bords = np.flatnonzero(np.diff(parle.astype(int)))
    segs, debut = [], None
    for b in bords:
        if parle[b + 1] and debut is None:
            debut = b
        elif not parle[b + 1] and debut is not None:
            segs.append([debut / SR, b / SR])
            debut = None
    fus = []
    for a, b in segs:
        if fus and a - fus[-1][1] < trou_min:
            fus[-1][1] = b
        else:
            fus.append([a, b])
    return fus


def traiter_voix(x):
    x = signal.lfilter(*biquad("hp", 70, 0.707), x)
    x = signal.lfilter(*biquad("hp", 70, 0.707), x)
    x = signal.lfilter(*biquad("peak", 3200, 1.0, 2.5), x)
    x = x * 10 ** ((-20 - lufs(x)) / 20)       # au même niveau avant le compresseur
    x = compresser(x, seuil_db=-26, ratio=3.0)
    x = x * 10 ** ((-16 - lufs(x)) / 20)
    return limiter(x, -1.5)


def fondu(n, debut=True):
    r = np.linspace(0, 1, n) ** 2
    return r if debut else r[::-1]


def momentane(x):
    """Loudness momentanée (pondération K, fenêtre 400 ms), échantillon par échantillon."""
    y = signal.lfilter(*biquad("shelf_haut", 1681.97, 0.7072, 4.0), x)
    y = signal.lfilter(*biquad("hp", 38.13, 0.5003), y)
    fen = int(0.4 * SR)
    m = np.convolve(y ** 2, np.ones(fen) / fen, mode="same")
    return -0.691 + 10 * np.log10(m + 1e-12)


def lisser_gain(g, attaque=0.06, relache=0.4):
    """Un gain qui descend vite (attaque) et remonte lentement (relâche)."""
    a = np.exp(-1 / (attaque * SR))
    r = np.exp(-1 / (relache * SR))
    sortie = np.empty_like(g)
    v = 1.0
    for i, cible in enumerate(g):
        coef = a if cible < v else r
        v = cible + coef * (v - cible)
        sortie[i] = v
    return sortie


def bande_freinee(piste, depart, duree=0.6):
    """La bande qu'on freine : la lecture ralentit de 1 à 0 en `duree` secondes."""
    n = int(duree * SR)
    vitesse = np.linspace(1, 0, n) ** 1.3
    pos = depart * SR + np.cumsum(vitesse)
    i = np.clip(pos.astype(int), 0, len(piste) - 2)
    f = (pos - i)[:, None]
    son = piste[i] * (1 - f) + piste[i + 1] * f
    return son * np.linspace(1, 0, n)[:, None] ** 0.5


def main():
    # ---------------------------------------------------------------- la voix
    brute = lire("voix-vous-brute.mp3", 1)
    print(f"voix brute  : {len(brute)/SR:5.2f} s · {lufs(brute):6.1f} LUFS")
    segs = phrases(brute)
    for c in COUPES_EN_PLUS:
        for s in segs:
            if s[0] < c < s[1]:
                segs.append([c + 0.06, s[1]])
                s[1] = c - 0.06
        segs.sort()
    assert len(segs) == len(REPLIQUES), f"la prise a {len(segs)} phrases, le plan en attend {len(REPLIQUES)} : nouvelle prise ?"
    voix = traiter_voix(brute)
    placee = np.zeros(int(DUREE * SR))
    repliques, decalages = {}, []
    for k, ((nom, film), (a, b)) in enumerate(zip(REPLIQUES, segs)):
        # une marge dans le silence de chaque côté, sans mordre sur la voisine
        avant = segs[k - 1][1] if k else 0.0
        apres = segs[k + 1][0] if k + 1 < len(segs) else len(brute) / SR
        ma, mb = max(avant + 0.02, a - 0.07), min(apres - 0.02, b + 0.16)
        bout = voix[int(ma * SR):int(mb * SR)].copy()
        bout[: int(0.008 * SR)] *= fondu(int(0.008 * SR))
        bout[-int(0.03 * SR):] *= fondu(int(0.03 * SR), debut=False)
        i0 = int((film - (a - ma)) * SR)
        placee[i0:i0 + len(bout)] += bout
        repliques[nom] = [round(film, 3), round(film + (b - a), 3)]
        decalages.append((a, b, film))
        print(f"  {nom:13s} prise {a:5.2f}-{b:5.2f} s → film {film:5.2f}-{film + b - a:5.2f} s")
    stereo = np.stack([placee, placee], 1)
    wavfile.write(PUB / "voix.wav", SR, np.round(np.clip(stereo, -1, 1) * 32767).astype(np.int16))

    # Les mots : Whisper se trompe de ±0,2 s ; on recale les mots de chaque phrase
    # sur ses bords MESURÉS, puis on les passe en temps du film.
    bruts = json.loads((PUB / "transcription-vous.json").read_text(encoding="utf-8"))
    mots = []
    for (a, b, film), (nom, _) in zip(decalages, REPLIQUES):
        dedans = [m for m in bruts if a - 0.3 <= (m["debut"] + m["fin"]) / 2 + 0.1 <= b + 0.1 and m not in mots_pris(mots)]
        if not dedans:
            continue
        w0, w1 = dedans[0]["debut"], dedans[-1]["fin"]
        echelle = (b - a) / max(1e-3, w1 - w0)
        for m in dedans:
            d = film + (m["debut"] - w0) * echelle
            f = film + (m["fin"] - w0) * echelle
            mots.append({"mot": m["mot"], "debut": round(d, 3), "fin": round(f, 3), "replique": nom, "_src": m})
    # ------------------------------------------------------------- la musique
    piste = lire("musique-brute.mp3", 2)
    lit = lambda a, n: piste[int(a * SR):int(a * SR) + n].copy()  # noqa: E731
    musique = np.zeros((int(DUREE * SR), 2))
    n_a = int((FIGE - 0.05 - BANG) * SR)
    a_part = lit(PISTE["montee"], n_a)
    a_part[: int(0.005 * SR)] *= fondu(int(0.005 * SR))[:, None]
    musique[int(BANG * SR):int(BANG * SR) + n_a] = a_part
    frein = bande_freinee(piste, PISTE["chute"] - 0.05)
    i = int((FIGE - 0.05) * SR)
    musique[i:i + len(frein)] += frein
    n_b = int((RACCORD - CHUTE) * SR)
    croise = int(0.03 * SR)
    b_part = lit(PISTE["chute"], n_b + croise)
    b_part[-croise:] *= fondu(croise, debut=False)[:, None]
    musique[int(CHUTE * SR):int(CHUTE * SR) + n_b + croise] += b_part
    n_c = int((DUREE - RACCORD) * SR)
    c_part = lit(PISTE["fin"], n_c)
    c_part[:croise] *= fondu(croise)[:, None]
    c_part[-int(0.8 * SR):] *= fondu(int(0.8 * SR), debut=False)[:, None]
    musique[int(RACCORD * SR):int(RACCORD * SR) + n_c] += c_part
    # le niveau : la chute à environ −17 LUFS quand personne ne parle
    groove = musique[int(CHUTE * SR):int(RACCORD * SR)].mean(1)
    musique *= 10 ** ((-17 - lufs(groove)) / 20)
    # SOUS LA VOIX : la musique ne dépasse jamais −29 LUFS momentanés
    parle = (np.abs(placee) > 10 ** (-40 / 20)).astype(float)
    parle = np.convolve(parle, np.ones(int(0.25 * SR)), mode="same") > 0
    mm = momentane(musique.mean(1))
    plafond = np.where(parle, np.minimum(1, 10 ** ((-29 - mm) / 20)), 1.0)
    gain = lisser_gain(plafond)
    musique *= gain[:, None]
    musique = np.stack([limiter(musique[:, 0], -1.5), limiter(musique[:, 1], -1.5)], 1)
    wavfile.write(PUB / "musique.wav", SR, np.round(np.clip(musique, -1, 1) * 32767).astype(np.int16))

    # ------------------------------------------------------------- le contrôle
    vm = momentane(placee)
    mm2 = momentane(musique.mean(1))
    sous = parle & (vm > -40)
    print(f"voix placée : {lufs(placee):6.1f} LUFS (sur ses phrases)")
    print(f"musique     : {lufs(musique.mean(1)):6.1f} LUFS intégrés · sous la voix, momentané médian {np.median(mm2[sous]):6.1f} · max {mm2[sous].max():6.1f}")
    print(f"écart voix/musique sous les phrases : {np.median(vm[sous] - mm2[sous]):4.1f} LU (médiane)")

    # ------------------------------------------------------------- le minutage
    module = ICI / "src/nebula30/minutage.ts"
    lignes = [
        "/**",
        " * Écrit par `_outils/nebula30_son.py` : NE PAS ÉDITER À LA MAIN.",
        " * Les répliques et les mots de la voix off EN TEMPS DU FILM (secondes), et les",
        " * instants musicaux (120 BPM). Toutes les animations s'y calent.",
        " */",
        f"export const REPLIQUES = {json.dumps(repliques, ensure_ascii=False)} as const;",
        "export const MOTS: {mot: string; debut: number; fin: number; replique: string}[] = "
        + json.dumps([{k: v for k, v in m.items() if k != "_src"} for m in mots], ensure_ascii=False) + ";",
        f"export const MUSIQUE = {json.dumps({'bang': BANG, 'fige': FIGE, 'chute': CHUTE, 'hit': HIT, 'raccord': RACCORD})} as const;",
        "/** L'enveloppe de la voix et de la musique, un point par dixième de seconde (0..1) :",
        " *  la timeline du logiciel de montage montre les VRAIES ondes. */",
        f"export const ONDE_VOIX = {json.dumps(enveloppe(placee))};",
        f"export const ONDE_MUSIQUE = {json.dumps(enveloppe(musique.mean(1)))};",
    ]
    module.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"{len(mots)} mots → {module}")


def enveloppe(x, pas=0.1):
    n = int(pas * SR)
    blocs = x[: len(x) // n * n].reshape(-1, n)
    v = np.sqrt((blocs ** 2).mean(1))
    return [round(float(a), 3) for a in v / (v.max() + 1e-9)]


def mots_pris(mots):
    return [m["_src"] for m in mots]


if __name__ == "__main__":
    main()

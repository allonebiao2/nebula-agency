"""Le son de la pub Grain d'Esthétique (35 s) : la voix placée, la musique montée.

ENTRÉES (public/grain35/sources/, hors dépôt) :
    voix-brute.mp3              la prise ElevenLabs (Alimata, Eleven v4, vitesse 1,08,
                                stabilité 50, avec balises d'émotion), 23,95 s
    transcription-voix.json     Whisper large-v3-turbo, au mot, SANS indice
    musique-djoldcatz.mp3       « Soulfire, the midnight ritual » (djoldcatz, Pixabay 460495)
    musique-jacquesflix.mp3     « Afrobeat ethnic beat electro chill » (jacquesflix, Pixabay 293723)

SORTIES :
    public/grain35/voix.wav      la voix nettoyée, coupée en 13 répliques et posée
    public/grain35/musique.wav   la musique choisie, montée et BAISSÉE SOUS LA VOIX
    src/grain35/minutage.ts      les répliques, les mots et les instants musicaux en
                                 temps du film : toutes les animations s'y calent

LA VOIX. Coupée dans ses SILENCES MESURÉS (le point le plus bas de l'énergie dans
une petite fenêtre autour de chaque frontière), jamais dans un mot. Whisper la lit
sans indice : « Sotis Paris » (juste) et « écrivez rendez-vous » : ElevenLabs a
développé « RDV », l'écran dit donc « rendez-vous » aussi. Le chuchotement
(« sans une seule piqûre ») est remonté à 2,5 LU sous les autres répliques : il
reste un secret sans se noyer dans la relance de la musique.

LA MUSIQUE, deux au choix (Mongazi : « tu choisiras ou tu pourras switcher ») :
    soulfire    (par défaut) 90 BPM pile, premier temps à 0,023 s, mesure 2,667 s.
                Une seule fenêtre, SANS RACCORD : piste 211,36 → 246,36 s. Elle part
                sans basse (l'œil se dessine), la basse entre à 2,0 s du film sur
                « Mais qui s'occupe de vous ? », un arrêt d'un temps puis la relance
                à 12,67 s (les avis), un deuxième arrêt à 22,66 s après « Et des
                lèvres repulpées… » et LA RELANCE à 23,33 s sur « sans une seule
                piqûre », un premier temps à 28,66 s, le grain du logo tombe sur le
                suivant (31,33 s) et LA VRAIE FIN DU MORCEAU s'éteint sous le logo.
    afro-chill  113 BPM, mais 22,8 s de musique seulement (le fichier en fait 27) et
                aucune montée : on rejoue ses mesures 2 à 9 pour tenir 35 s. Moins
                bon, gardé en réserve.

    python _outils/grain35_son.py              (soulfire)
    python _outils/grain35_son.py afro-chill
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

from dimanche_son import biquad, compresser, limiter, lufs

ICI = Path(__file__).resolve().parent.parent
SRC = ICI / "public/grain35/sources"
PUB = ICI / "public/grain35"
FFMPEG = ICI / "node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe"
SR = 44100
DUREE = 35.0
DUREE_PRISE = 23.95  # la prise attendue : une autre prise = un autre plan

# ------------------------------------------------------------- le plan de la voix
# Les répliques dans l'ordre de la prise, la frontière APPROCHÉE qui les sépare de
# la suivante (secondes de la prise, affinée sur le silence mesuré), et l'instant
# du FILM où chacune commence à parler.
REPLIQUES = [
    ("occupe", 2.15, 0.45),
    ("quiVous", 3.85, 2.65),
    ("chez", 5.22, 5.25),
    ("premier", 7.22, 6.45),
    ("maisons", 10.28, 8.70),
    ("visage", 12.20, 16.40),
    ("corps", 14.25, 18.60),     # commence par le souffle de [exhales softly]
    ("levres", 16.08, 21.00),
    ("piqure", 17.50, 23.55),    # le chuchotement, juste après la relance (23,33)
    ("tour", 18.73, 25.30),
    ("ecrivez", 20.65, 26.30),
    ("nom", 21.90, 29.25),
    ("devise", None, 31.75),     # après le grain (31,33), sur la fin du morceau
]
SONIE = {"piqure": -18.5}  # LUFS par réplique ; les autres à -16

# ------------------------------------------------------------- les musiques
MUSIQUES = {
    "soulfire": {
        "fichier": "musique-djoldcatz.mp3", "bpm": 90.0, "premier_temps": 0.023,
        "morceaux": [(211.36, 246.36)],
        # les instants du film, relevés sur la piste (piste − 211,36)
        "instants": {"basse": 2.0, "relanceAvis": 12.67, "arret": 22.66, "relance": 23.33,
                     "logo": 28.55, "grain": 31.33, "fin": 34.6},
    },
    "afro-chill": {
        "fichier": "musique-jacquesflix.mp3", "bpm": 113.02, "premier_temps": 0.937,
        # mesures 0 à 7 (0 → 15,80 s), puis on rejoue depuis la mesure 2 (5,18 s) jusqu'à la fin
        "morceaux": [(0.0, 15.80), (5.18, 24.5)],
        "instants": None,  # calés sur la grille de ce morceau, voir instants_cales()
    },
}


def lire(chemin, canaux):
    tmp = ICI / f"out/_{chemin.stem}-{canaux}.wav"
    tmp.parent.mkdir(exist_ok=True)
    subprocess.run([str(FFMPEG), "-v", "error", "-y", "-i", str(chemin), "-ac", str(canaux),
                    "-ar", str(SR), "-c:a", "pcm_s16le", str(tmp)], check=True)
    _, x = wavfile.read(tmp)
    return x.astype(np.float64) / 32768


def moyenne_glissante(x, fen):
    """Moyenne sur `fen` échantillons, centrée, par somme cumulée : O(n). ⚠️ Pas de
    np.convolve ici : sur 35 s et une fenêtre de 400 ms, c'est 2,7·10¹⁰ opérations
    (l'outil ne finissait pas en 5 minutes)."""
    c = np.concatenate([[0.0], np.cumsum(x)])
    i = np.arange(len(x))
    a = np.clip(i - fen // 2, 0, len(x))
    b = np.clip(i + fen - fen // 2, 0, len(x))
    return (c[b] - c[a]) / fen


def energie_db(x, fen_s=0.01):
    return 20 * np.log10(np.sqrt(np.maximum(moyenne_glissante(x ** 2, int(fen_s * SR)), 0)) + 1e-9)


def silence_le_plus_bas(e, t, demi=0.15):
    a, b = int((t - demi) * SR), int((t + demi) * SR)
    return (a + int(np.argmin(e[a:b]))) / SR


def bords_parole(e, a, b, seuil=-50):
    """Le premier et le dernier instant où la voix dépasse le seuil dans [a, b]."""
    i = np.flatnonzero(e[int(a * SR):int(b * SR)] > seuil)
    return a + i[0] / SR, a + i[-1] / SR


def traiter_voix(x):
    x = signal.lfilter(*biquad("hp", 70, 0.707), x)
    x = signal.lfilter(*biquad("hp", 70, 0.707), x)
    x = signal.lfilter(*biquad("peak", 3200, 1.0, 2.0), x)
    x = x * 10 ** ((-20 - lufs(x)) / 20)
    x = compresser(x, seuil_db=-26, ratio=2.5)
    return x * 10 ** ((-16 - lufs(x)) / 20)


def fondu(n, debut=True):
    r = np.linspace(0, 1, n) ** 2
    return r if debut else r[::-1]


def momentane(x):
    """Loudness momentanée (pondération K, fenêtre 400 ms), échantillon par échantillon."""
    y = signal.lfilter(*biquad("shelf_haut", 1681.97, 0.7072, 4.0), x)
    y = signal.lfilter(*biquad("hp", 38.13, 0.5003), y)
    m = np.maximum(moyenne_glissante(y ** 2, int(0.4 * SR)), 0)
    return -0.691 + 10 * np.log10(m + 1e-12)


def lisser_gain(g, attaque=0.06, relache=0.45):
    a = np.exp(-1 / (attaque * SR))
    r = np.exp(-1 / (relache * SR))
    sortie = np.empty_like(g)
    v = 1.0
    for i, cible in enumerate(g):
        v = cible + (a if cible < v else r) * (v - cible)
        sortie[i] = v
    return sortie


def monter_musique(choix):
    m = MUSIQUES[choix]
    piste = lire(SRC / m["fichier"], 2)
    sortie = np.zeros((int(DUREE * SR), 2))
    pos, croise = 0, int(0.025 * SR)
    for k, (a, b) in enumerate(m["morceaux"]):
        bout = piste[int(a * SR):int(b * SR)].copy()
        bout = bout[: max(0, len(sortie) - pos + croise)]
        if k:  # raccord sur un premier temps, fondu croisé de 25 ms
            bout[:croise] *= fondu(croise)[:, None]
            pos -= croise
        fin = min(len(sortie), pos + len(bout))
        sortie[pos:fin] += bout[: fin - pos]
        pos = fin
    entree = int(0.12 * SR)
    sortie[:entree] *= fondu(entree)[:, None]
    sortie[-int(0.6 * SR):] *= fondu(int(0.6 * SR), debut=False)[:, None]
    return sortie, m


def instants_cales(m):
    """Pour une musique sans instants relevés : les instants du plan, recalés sur
    le premier temps le plus proche de SA grille (en temps du film)."""
    plan = MUSIQUES["soulfire"]["instants"]
    mesure = 4 * 60 / m["bpm"]
    temps_film, debut_film = [], 0.0
    for a, b in m["morceaux"]:
        k0 = int(np.ceil((a - m["premier_temps"]) / mesure))
        t = m["premier_temps"] + k0 * mesure
        while t < b:
            temps_film.append(debut_film + t - a)
            t += mesure
        debut_film += b - a
    temps_film = np.array(temps_film)
    cale = lambda v: float(round(temps_film[np.argmin(np.abs(temps_film - v))], 3))  # noqa: E731
    out = {k: cale(v) for k, v in plan.items() if k not in ("logo", "fin", "arret")}
    out["logo"] = round(out["grain"] - 2.78, 3)
    out["arret"] = round(out["relance"] - 60 / m["bpm"], 3)
    out["fin"] = 34.6
    return out


def main():
    choix = sys.argv[1] if len(sys.argv) > 1 else "soulfire"
    assert choix in MUSIQUES, f"musique inconnue : {choix} ({', '.join(MUSIQUES)})"

    # ---------------------------------------------------------------- la voix
    brute = lire(SRC / "voix-brute.mp3", 1)
    duree = len(brute) / SR
    assert abs(duree - DUREE_PRISE) < 0.3, f"la prise fait {duree:.2f} s, le plan en attend {DUREE_PRISE} : nouvelle prise ?"
    print(f"voix brute : {duree:5.2f} s · {lufs(brute):6.1f} LUFS")
    e = energie_db(brute)
    coupes = [0.0] + [silence_le_plus_bas(e, c) for _, c, _ in REPLIQUES[:-1]] + [duree]
    voix = traiter_voix(brute)
    placee = np.zeros(int(DUREE * SR))
    repliques, plages = {}, []
    for k, (nom, _, film) in enumerate(REPLIQUES):
        a, b = bords_parole(e, coupes[k], coupes[k + 1])
        ma, mb = max(coupes[k], a - 0.06), min(coupes[k + 1], b + 0.15)
        bout = voix[int(ma * SR):int(mb * SR)].copy()
        cible = SONIE.get(nom, -16.0)
        if len(bout) > 0.45 * SR:
            bout *= 10 ** (np.clip(cible - lufs(bout), -6, 9) / 20)
        bout[: int(0.008 * SR)] *= fondu(int(0.008 * SR))
        bout[-int(0.04 * SR):] *= fondu(int(0.04 * SR), debut=False)
        i0 = int((film - (a - ma)) * SR)
        placee[i0:i0 + len(bout)] += bout
        repliques[nom] = [round(film, 3), round(film + (b - a), 3)]
        plages.append((nom, a, b, film))
        print(f"  {nom:9s} prise {a:5.2f}-{b:5.2f} s → film {film:5.2f}-{film + b - a:5.2f} s")
    noms = [n for n, _, _ in REPLIQUES]
    for x, y in zip(noms, noms[1:]):
        assert repliques[x][1] < repliques[y][0], f"{x} déborde sur {y}"
    assert repliques["devise"][1] < DUREE - 0.8, "la devise finit trop tard"
    placee = limiter(placee, -1.5)
    stereo = np.stack([placee, placee], 1)
    wavfile.write(PUB / "voix.wav", SR, np.round(np.clip(stereo, -1, 1) * 32767).astype(np.int16))

    # les mots, en temps du film (Whisper se trompe de ±0,2 s : pour l'écran ça suffit)
    trans = json.loads((SRC / "transcription-voix.json").read_text(encoding="utf-8"))
    corrige = {"Sotis": "Sothys", "Sultan": "Sultane", "Sabah.": "Saba."}
    mots = []
    for seg in trans["segments"]:
        for w in seg["mots"]:
            milieu = (w["d"] + w["f"]) / 2
            for nom, a, b, film in plages:
                if a - 0.25 <= milieu <= b + 0.25:
                    txt = w["m"].strip()
                    mots.append({"mot": corrige.get(txt, txt), "debut": round(film + w["d"] - a, 3),
                                 "fin": round(film + w["f"] - a, 3), "replique": nom})
                    break

    # ------------------------------------------------------------- la musique
    musique, m = monter_musique(choix)
    instants = m["instants"] or instants_cales(m)
    calme = (np.abs(placee) < 10 ** (-45 / 20))
    musique *= 10 ** ((-17 - lufs(musique.mean(1))) / 20)
    # sous la voix : la musique ne dépasse pas -28 LUFS momentanés. Le masque de
    # parole s'ouvre 0,12 s avant chaque mot et se referme 0,3 s après, pour que
    # le coup de la relance (23,33) passe AVANT le chuchotement (23,55).
    parle = (np.abs(placee) > 10 ** (-40 / 20)).astype(float)
    av, ap = int(0.12 * SR), int(0.3 * SR)
    c = np.concatenate([[0.0], np.cumsum(parle)])
    i = np.arange(len(parle))
    parle = (c[np.clip(i + av + 1, 0, len(parle))] - c[np.clip(i - ap, 0, len(parle))]) > 0
    mm = momentane(musique.mean(1))
    plafond = np.where(parle, np.minimum(1, 10 ** ((-28 - mm) / 20)), 1.0)
    musique *= lisser_gain(plafond)[:, None]
    musique = np.stack([limiter(musique[:, 0], -1.5), limiter(musique[:, 1], -1.5)], 1)
    wavfile.write(PUB / "musique.wav", SR, np.round(np.clip(musique, -1, 1) * 32767).astype(np.int16))

    # ------------------------------------------------------------- le contrôle
    vm, mm2 = momentane(placee), momentane(musique.mean(1))
    sous = parle & (vm > -40)
    print(f"musique « {choix} » : {lufs(musique.mean(1)):6.1f} LUFS intégrés · sans voix {lufs(musique.mean(1)[calme]):6.1f}")
    print(f"écart voix/musique sous les phrases : {np.median(vm[sous] - mm2[sous]):4.1f} LU (médiane), "
          f"{np.percentile(vm[sous] - mm2[sous], 5):4.1f} LU (5 % les plus serrés)")
    for nom, (a, b) in repliques.items():
        z = slice(int(a * SR), int(b * SR))
        print(f"  {nom:9s} voix {np.median(vm[z]):6.1f} · musique {np.median(mm2[z]):6.1f} · écart {np.median(vm[z] - mm2[z]):4.1f} LU")

    # ------------------------------------------------------------- le minutage
    module = ICI / "src/grain35/minutage.ts"
    lignes = [
        "/**",
        " * Écrit par `_outils/grain35_son.py` : NE PAS ÉDITER À LA MAIN.",
        " * Les répliques et les mots de la voix EN TEMPS DU FILM (secondes), et les",
        f" * instants musicaux de « {choix} ». Toutes les animations s'y calent.",
        " */",
        "import type {Replique} from './donnees';",
        "",
        "export const PROVISOIRE = false;",
        f"export const MUSIQUE_CHOISIE = {json.dumps(choix)};",
        f"export const REPLIQUES: Record<Replique, readonly [number, number]> = {json.dumps(repliques, ensure_ascii=False)};",
        "export const MOTS: {mot: string; debut: number; fin: number; replique: Replique}[] = "
        + json.dumps(mots, ensure_ascii=False) + ";",
        f"export const MUSIQUE = {json.dumps(instants)} as const;",
        "export const SON = {voix: true, musique: true} as const;",
    ]
    module.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"{len(mots)} mots → {module}")


if __name__ == "__main__":
    main()

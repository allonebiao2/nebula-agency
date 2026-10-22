"""MA LETTRE À… · « Minuit pile, pour maman » : LE SON, et le minutage qui en découle.

    python _outils/malettre_minuit_son.py

Une seule vérité pour l'image et le son. Ce script :
    · découpe les deux voix de Mongazi (Koffi, Alimata) en phrases, et pose chaque phrase à sa place ;
    · pose les deux musiques Pixabay choisies par Mongazi (le piano pour l'histoire, l'afrobeat pour la suite),
      la seconde calée pour que son premier temps fort tombe sur « Ça, c'est Ma lettre à… » ;
    · pose les bruitages (tous synthétisés par `malettre_minuit_preparer.py`) ;
    · traite les voix (coupe-bas, présence, compression, atténuation des sifflantes), fait baisser la musique
      sous chaque phrase, mixe, et masterise pour YouTube : −14 LUFS intégrés, crête vraie ≤ −1 dBTP ;
    · VÉRIFIE que la voix passe devant, phrase par phrase (le mélange contre la voix seule) ;
    · écrit `public/malettre-minuit/mix.wav` (hors git) et `src/malettre-minuit/minutage.json` (lu par Remotion).

Mongazi (2026-10-22) : « le volume des voix doit être fort pour qu'on les entende bien, et égalise bien le son,
les bruitages ». ⚠️ Rien n'est accéléré chez Koffi (l'intime) ; Alimata est poussée de 5 % (imperceptible,
plus vif), parce que les voix seules font déjà 41 s pour un film voulu court.
⚠️ Chaque phrase est NIVELÉE (±6 dB) : les phrases murmurées de Koffi passaient sous la musique.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

sys.stdout.reconfigure(encoding="utf-8")
ICI = Path(__file__).resolve().parent.parent
RACINE = ICI.parent
PUB = ICI / "public" / "malettre-minuit"
FFMPEG = ICI / "node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe"
SR = 48000
CIBLE_LUFS = -14.0
PLAFOND_DBTP = -1.0

SOURCES = {
    "koffi": RACINE / "_partage" / "voix de koffi tony.mp3",
    "alimata": RACINE / "_partage" / "voix de alimata.mp3",
    "piano": RACINE / "_partage" / "nastelbom-emotional-piano-598096.mp3",
    "afro": RACINE / "_partage" / "sonican-afrobeat-music-loop-positive-vibes-481253.mp3",
}
ACCELERE = {"alimata": 1.07}

# Ce que chaque morceau de voix DIT : le script de `src/malettre-minuit/VOIX.md`, découpé à ses pauses.
KOFFI = ["Dans trois secondes…", "ma mère va pleurer.", "Elle a soixante ans ce soir.", "Moi…",
         "je suis à Paris.", "Alors je lui ai écrit une lettre…", "qui ne s'ouvre qu'à minuit pile.",
         "Maman…", "tu me réveillais à cinq heures… pour réviser le bac…"]
ALIMATA = ["Ça, c'est Ma lettre à…", "Une lettre scellée…", "qui s'ouvre à l'heure que tu choisis.",
           "Et avant l'heure ?", "Impossible de l'ouvrir. Même en insistant.", "Tu l'écris…",
           "ou la plume l'écrit avec toi, à partir de tes souvenirs.", "La cire, le sceau, le papier, ta photo…",
           "et une pluie d'étoiles à l'ouverture.", "Pour la Saint-Valentin…", "à minuit pile,", "avant tout le monde.",
           "Pour t'excuser…", "sans qu'on te raccroche au nez.", "Pour une demande…", "quand la voix tremble.",
           "Ou la soirée entre potes : l'heure, le lieu…", "et qui ramène les boissons.", "Ma lettre à…",
           "Dès mille francs.", "Tape un prénom :", "ta lettre commence."]
# Les morceaux d'une même ligne du script se suivent de près ; une nouvelle ligne respire un peu plus.
LIGNES_ALIMATA = [[0], [1, 2], [3, 4], [5, 6], [7, 8], [9, 10, 11], [12, 13], [14, 15], [16, 17], [18, 19], [20, 21]]

# L'afrobeat (mesuré le 2026-10-22) : 96,1 BPM, premier temps à 0,353 s, la grosse caisse sur le 3e temps.
AFRO_TEMPS, AFRO_PERIODE, AFRO_MESURE0 = 0.353, 60 / 96.1, 1.601


# ── lire, découper ────────────────────────────────────────────────────────────
def decoder(src, canaux, tempo=None):
    """Décode en WAV 16 bits (le ffmpeg allégé de Remotion n'écrit pas de flux brut sur la sortie standard)."""
    af = ["-af", "atempo=%.3f" % tempo] if tempo else []
    tmp = PUB / "_decode.wav"
    subprocess.run([str(FFMPEG), "-v", "error", "-y", "-i", str(src), *af, "-ac", str(canaux), "-ar", str(SR),
                    "-c:a", "pcm_s16le", str(tmp)], check=True)
    sr, d = wavfile.read(tmp)
    tmp.unlink()
    return d.astype(np.float64) / 32768


def segments(x, attendu, nom):
    """Les phrases : de la parole séparée par au moins 0,26 s de silence (seuil : 32 dB sous la crête)."""
    pas = int(SR * .02)
    e = np.array([np.sqrt(np.mean(x[i:i + pas] ** 2)) for i in range(0, len(x) - pas, pas)])
    db = 20 * np.log10(e + 1e-9)
    parle = db > db.max() - 32
    seg, i = [], 0
    while i < len(parle):
        if parle[i]:
            j = i
            while j < len(parle) and (parle[j] or (j + 13 < len(parle) and np.any(parle[j:j + 13]))):
                j += 1
            seg.append([max(0.0, i * .02 - .04), min(len(x) / SR, j * .02 + .08)])
            i = j
        else:
            i += 1
    if len(seg) != attendu:
        sys.exit("⛔ %s : %d phrases trouvées, %d attendues (le script a changé ?)" % (nom, len(seg), attendu))
    return seg


# ── filtres ───────────────────────────────────────────────────────────────────
def biquad(kind, fc, q, gain_db=0.0):
    a = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * fc / SR
    al = np.sin(w0) / (2 * q)
    c = np.cos(w0)
    if kind == "hp":
        b, d = [(1 + c) / 2, -(1 + c), (1 + c) / 2], [1 + al, -2 * c, 1 - al]
    elif kind == "lp":
        b, d = [(1 - c) / 2, 1 - c, (1 - c) / 2], [1 + al, -2 * c, 1 - al]
    elif kind == "pic":
        b, d = [1 + al * a, -2 * c, 1 - al * a], [1 + al / a, -2 * c, 1 - al / a]
    else:  # plateau haut
        s = 2 * np.sqrt(a) * al
        b = [a * ((a + 1) + (a - 1) * c + s), -2 * a * ((a - 1) + (a + 1) * c), a * ((a + 1) + (a - 1) * c - s)]
        d = [(a + 1) - (a - 1) * c + s, 2 * ((a - 1) - (a + 1) * c), (a + 1) - (a - 1) * c - s]
    b, d = np.array(b), np.array(d)
    return b / d[0], d / d[0]


def filtre(x, *spec):
    return signal.lfilter(*biquad(*spec), x, axis=0)


def enveloppe(x, attaque, relache, fenetre=.01):
    """Enveloppe RMS lissée, attaque et relâche distinctes (en secondes)."""
    m = x if x.ndim == 1 else x.mean(1)
    n = max(1, int(fenetre * SR))
    rms = np.sqrt(np.convolve(m ** 2, np.ones(n) / n, mode="same"))
    ra, rr = np.exp(-1 / (attaque * SR)), np.exp(-1 / (relache * SR))
    out = np.empty_like(rms)
    v = 0.0
    for i, s in enumerate(rms):
        r = ra if s > v else rr
        v = s + r * (v - s)
        out[i] = v
    return out


def voix_traitee(x):
    """La chaîne de la voix : coupe-bas, moins de boue, plus de présence, un peu d'air, compression, sifflantes."""
    y = filtre(x, "hp", 85, .707)
    y = filtre(y, "pic", 230, .9, -2.5)
    y = filtre(y, "pic", 3200, .8, 3.5)
    y = filtre(y, "plateau", 9000, .7, 1.5)
    # compression douce : seuil −24 dBFS, rapport 3:1
    env = enveloppe(y, .006, .12)
    db = 20 * np.log10(env + 1e-9)
    gain_db = np.where(db > -24, -(db + 24) * (1 - 1 / 3), 0.0)
    y = y * 10 ** (gain_db / 20)
    # sifflantes : on n'atténue la bande 5,5-9 kHz que quand elle dépasse
    s = filtre(filtre(y, "hp", 5500, .707), "lp", 9000, .707)
    es = enveloppe(s, .002, .05, .004)
    exces = np.clip(20 * np.log10(es + 1e-9) + 30, 0, 9)
    y = y - s * (1 - 10 ** (-exces / 20))
    return y


# ── sonie (BS.1770-4) et limiteur, repris du mastering de la vidéo NEBULA ─────
def pondere(x):
    y = signal.lfilter(*biquad("plateau", 1681.97, 0.7072, 4.0), x, axis=0)
    return signal.lfilter(*biquad("hp", 38.13, 0.5003), y, axis=0)


def lufs(x):
    y = pondere(x if x.ndim == 2 else x[:, None])
    blk, pas = int(0.4 * SR), int(0.1 * SR)
    if len(y) < blk:
        return float("nan")
    z = np.array([np.mean(y[i:i + blk] ** 2, axis=0).sum() for i in range(0, len(y) - blk + 1, pas)])
    l = -0.691 + 10 * np.log10(z + 1e-12)
    z = z[l > -70]
    if not len(z):
        return float("nan")
    rel = -0.691 + 10 * np.log10(z.mean()) - 10
    z = z[-0.691 + 10 * np.log10(z) > rel]
    return -0.691 + 10 * np.log10(z.mean())


def crete_vraie(x):
    return 20 * np.log10(np.abs(signal.resample_poly(x, 4, 1, axis=0)).max() + 1e-12)


def limiter(x, plafond_db, anticipation=0.005, relache=0.08):
    plafond = 10 ** (plafond_db / 20)
    n = int(anticipation * SR)
    pic = np.abs(x).max(axis=1)
    pic = np.lib.stride_tricks.sliding_window_view(np.pad(pic, (0, n)), n + 1).max(1)[: len(x)]
    voulu = np.minimum(1, plafond / (pic + 1e-12))
    r = np.exp(-1 / (relache * SR))
    g = np.empty_like(voulu)
    v = 1.0
    for i, cible in enumerate(voulu):
        v = cible if cible < v else cible + r * (v - cible)
        g[i] = v
    return np.clip(x * g[:, None], -plafond, plafond)


def courbe(points, n):
    """Une automation de gain (dB) : des points (t, dB), interpolés, rendue en facteur linéaire."""
    t = np.arange(n) / SR
    ts, vs = zip(*points)
    db = np.interp(t, ts, vs)
    return 10 ** (db / 20)


def poser(piste, son, t, gain_db=0.0, pan=0.0):
    i = int(round(t * SR))
    if son.ndim == 1:
        son = np.stack([son * np.sqrt((1 - pan) / 2), son * np.sqrt((1 + pan) / 2)], 1) * np.sqrt(2)
    j = min(len(piste), i + len(son))
    if j > i >= 0:
        piste[i:j] += son[: j - i] * 10 ** (gain_db / 20)


def sfx(nom):
    sr, d = wavfile.read(PUB / (nom + ".wav"))
    x = d.astype(np.float64) / 32768
    return x if sr == SR else signal.resample_poly(x, SR, sr, axis=0)


# ── le film ───────────────────────────────────────────────────────────────────
def main():
    voix = {n: decoder(SOURCES[n], 1, ACCELERE.get(n)) for n in ("koffi", "alimata")}
    # ⚠️ On découpe l'enregistrement D'ORIGINE, puis on convertit les temps : accélérée, la pause de 0,26 s
    # entre « Ma lettre à… » et « Dès mille francs » passait sous le seuil, et les deux phrases se collaient.
    seg = {}
    for nom, textes, titre in (("koffi", KOFFI, "Koffi"), ("alimata", ALIMATA, "Alimata")):
        k = ACCELERE.get(nom, 1.0)
        seg[nom] = [[a / k, b / k] for a, b in segments(decoder(SOURCES[nom], 1), len(textes), titre)]
    lignes = []

    def placer(nom, k, t, texte, lid):
        a, b = seg[nom][k]
        lignes.append({"id": lid, "voix": nom, "texte": texte, "debut": round(t, 3), "fin": round(t + (b - a), 3),
                       "src": [a, b]})
        return t + (b - a)

    # Koffi : l'accroche, Paris, la lettre.
    t = 0.45
    ecarts = [None, .38, .55, .22, .1, .38, .26]
    for k in range(7):
        if k:
            t += ecarts[k]
        t = placer("koffi", k, t, KOFFI[k], "k%d" % (k + 1))
    MINUIT = t + 3.05                      # l'envol, la chambre, 58, 59… minuit
    t = placer("koffi", 7, MINUIT + 3.15, KOFFI[7], "k8")
    t = placer("koffi", 8, t + .28, KOFFI[8], "k9")
    debut_a = t + .55
    t = debut_a
    for n, ligne in enumerate(LIGNES_ALIMATA):
        for m, k in enumerate(ligne):
            if n or m:
                t += .08 if m else (.4 if k == 18 else .2)
            t = placer("alimata", k, t, ALIMATA[k], "a%d" % (k + 1))
    FIN = t + 1.5
    n = int(FIN * SR)
    L = {l["id"]: l for l in lignes}

    # L'afrobeat : son premier temps fort tombe sur « Ça, c'est Ma lettre à… ».
    S_AFRO = debut_a - AFRO_MESURE0
    temps_afro = [round(S_AFRO + AFRO_TEMPS + k * AFRO_PERIODE, 3) for k in range(200)
                  if debut_a - 2 <= S_AFRO + AFRO_TEMPS + k * AFRO_PERIODE <= FIN]
    mesures_afro = [round(S_AFRO + AFRO_MESURE0 + m * 4 * AFRO_PERIODE, 3) for m in range(60)
                    if debut_a - .01 <= S_AFRO + AFRO_MESURE0 + m * 4 * AFRO_PERIODE <= FIN]

    # ── les voix, traitées, posées ──
    piste_voix = np.zeros((n, 2))
    for nom in ("koffi", "alimata"):
        v = voix_traitee(voix[nom])
        # chaque voix à la même sonie de parole (−18 LUFS avant le master), Koffi un rien plus bas (l'intime)
        v = v * 10 ** (((-18.5 if nom == "koffi" else -18.0) - lufs(v)) / 20)
        for l in lignes:
            if l["voix"] != nom:
                continue
            a, b = l["src"]
            morceau = v[int(a * SR):int(b * SR)].copy()
            # le niveleur : chaque phrase vers la sonie voulue, sans dépasser ±6 dB (un murmure reste un murmure)
            lm = lufs(morceau)
            if not np.isnan(lm):
                cible = -18.5 if nom == "koffi" else -18.0
                morceau *= 10 ** (np.clip(cible - lm, -6, 6) / 20)
            fond = min(len(morceau), int(.012 * SR))
            morceau[:fond] *= np.linspace(0, 1, fond)
            morceau[-fond:] *= np.linspace(1, 0, fond)
            poser(piste_voix, morceau, l["debut"])
    presence = enveloppe(piste_voix, .06, .35, .03)
    presence = np.clip(presence / (np.percentile(presence[presence > 1e-4], 70) + 1e-9), 0, 1)

    # ── les musiques ──
    piano = decoder(SOURCES["piano"], 2)
    afro = decoder(SOURCES["afro"], 2)
    piste_piano = np.zeros((n, 2))
    fin_piano = debut_a + .6
    poser(piste_piano, piano[: int(fin_piano * SR)], 0.0)
    # l'attente étouffe le piano (passe-bas), minuit le rouvre d'un coup : le « wow » s'entend
    etouffe = filtre(piste_piano, "lp", 700, .707)
    ouvert = courbe([(0, 1), (MINUIT - 3.6, 1), (MINUIT - 3.0, 0), (MINUIT, 0), (MINUIT + .25, 1), (FIN, 1)], n)
    piste_piano = piste_piano * ouvert[:, None] + etouffe * (1 - ouvert[:, None])
    piste_piano *= courbe([(0, -60), (1.3, -2), (MINUIT - 3.5, -2), (MINUIT - 2.9, -6), (MINUIT - .05, -6),
                           (MINUIT + .15, 1.5), (MINUIT + 1.4, 1.5), (MINUIT + 2.6, -1), (debut_a - .5, -1),
                           (fin_piano, -60), (FIN, -60)], n)[:, None]
    piste_afro = np.zeros((n, 2))
    poser(piste_afro, afro[int(max(0, (debut_a - .7) - S_AFRO) * SR):], debut_a - .7)
    piste_afro *= courbe([(0, -60), (debut_a - .7, -60), (debut_a - .05, 0), (FIN - 1.5, 0), (FIN, -60)], n)[:, None]
    musique = piste_piano + piste_afro
    # une place pour la présence de la voix, puis la musique se baisse sous chaque phrase (jusqu'à −10 dB)
    musique = filtre(musique, "pic", 3000, .9, -4.0)
    musique = filtre(musique, "pic", 1300, 1.0, -2.0)
    musique *= 10 ** ((-24 - lufs(musique)) / 20)
    # sous chaque phrase, la musique se retire de 12 dB (l'afrobeat est dense : les phrases douces d'Alimata passaient dessous)
    musique *= (10 ** (-12 * presence / 20))[:, None]

    # ── les bruitages ──
    piste_sfx = np.zeros((n, 2))
    pose = []

    def b(nom, t, g=0.0, pan=0.0):
        poser(piste_sfx, sfx(nom), t, g, pan)
        pose.append({"son": nom, "t": round(t, 3)})

    b("notif", .22, -8)
    b("tic", .2, -12)
    b("pluie", L["k3"]["debut"] - .5, -16)
    b("plume", L["k6"]["debut"] - .1, -16)
    b("tampon", L["k7"]["debut"] + .15, -6)
    b("souffle", L["k7"]["fin"] - .2, -9)
    for k, dt in enumerate((-3.0, -2.0, -1.0)):
        b("tic" if k % 2 == 0 else "tac", MINUIT + dt, -10)
        b("coeur", MINUIT + dt + .12, -6)
    b("embrase", MINUIT, -3)
    b("souffle", MINUIT + .45, -8)
    b("clic", MINUIT + .9, -6)
    b("eclat", MINUIT + 1.0, -1)
    b("etoiles", MINUIT + 1.05, -7)
    b("papier", MINUIT + 2.2, -9)
    b("papier", MINUIT + 3.15, -11)
    b("tin", L["a1"]["debut"] + .05, -7)
    b("swish", L["a2"]["debut"] - .2, -10)
    b("insiste", L["a5"]["debut"] + 1.2, -6)
    b("plume", L["a7"]["debut"], -14)
    for k, dt in enumerate((0.0, .55, 1.15, 1.85)):
        b("clic", L["a8"]["debut"] + dt, -12, (-.4, .4, -.2, .2)[k])
    b("etoiles", L["a9"]["debut"] + .5, -10)
    b("swish", L["a10"]["debut"] - .15, -10)
    b("occupe", L["a14"]["fin"] - .65, -12)
    b("emballe", L["a16"]["debut"] - .1, -8)
    b("pop", L["a18"]["debut"] + .1, -8)
    b("tin", L["a19"]["debut"] + .02, -8)
    b("frappe", L["a21"]["fin"] - .1, -10)
    piste_sfx *= 10 ** ((-26 - lufs(piste_sfx)) / 20) if np.abs(piste_sfx).max() > 0 else 1
    # les bruitages se baissent sous la voix (−7 dB), sauf les coups voulus de minuit, laissés libres
    tt = np.arange(n) / SR
    libre = np.interp(tt, [0, MINUIT - .1, MINUIT, MINUIT + 2.4, MINUIT + 2.9, FIN], [0, 0, 1, 1, 0, 0])
    piste_sfx *= (10 ** (-7 * presence * (1 - libre) / 20))[:, None]

    # ── le mélange, puis le master ──
    melange = piste_voix + musique + piste_sfx
    y = melange * 10 ** ((CIBLE_LUFS - lufs(melange)) / 20)
    for _ in range(3):
        y = limiter(y, PLAFOND_DBTP - 1.1)
        y = y * 10 ** ((CIBLE_LUFS - lufs(y)) / 20)
    y = limiter(y, PLAFOND_DBTP - 1.1)
    gain = (np.abs(y).max() / (np.abs(melange).max() + 1e-12))
    print("durée        %.2f s · minuit à %.2f s · « Ça, c'est Ma lettre à… » à %.2f s" % (FIN, MINUIT, debut_a))
    print("master       %.1f LUFS · crête vraie %.1f dBTP" % (lufs(y), crete_vraie(y)))
    print("musique seule %.1f LUFS · bruitages seuls %.1f LUFS (avant master)" % (lufs(musique), lufs(piste_sfx)))

    # la voix passe-t-elle devant ? le mélange contre la voix seule, au même gain
    g_master = 10 ** ((lufs(y) - lufs(melange)) / 20)
    ec = []
    for l in lignes:
        i0, i1 = int(l["debut"] * SR), int(l["fin"] * SR)
        if i1 - i0 < SR * .45:
            continue
        lm, lv = lufs(y[i0:i1]), lufs(piste_voix[i0:i1] * g_master)
        ec.append(lm - lv)
    print("la voix devant : écart médian %+.1f LU, pire %+.1f LU (0 = la voix domine ; au-delà de +2, elle est couverte)"
          % (np.median(ec), max(ec)))
    for l, e in zip([l for l in lignes if (l["fin"] - l["debut"]) * SR >= SR * .45], ec):
        if e > 1.5:
            print("   ⚠️ %s (%.2f s) +%.1f LU : %s" % (l["id"], l["debut"], e, l["texte"]))
    del gain

    wavfile.write(PUB / "mix.wav", SR, np.round(np.clip(y, -1, 1) * 32767).astype(np.int16))
    sortie = {"duree": round(FIN, 3), "minuit": round(MINUIT, 3), "debutNarratrice": round(debut_a, 3),
              "lignes": [{k: v for k, v in l.items() if k != "src"} for l in lignes],
              "tempsAfro": temps_afro, "mesuresAfro": mesures_afro, "bruitages": pose}
    (ICI / "src" / "malettre-minuit" / "minutage.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=1),
                                                                    encoding="utf-8")
    print("✓ public/malettre-minuit/mix.wav · src/malettre-minuit/minutage.json (%d phrases)" % len(lignes))


if __name__ == "__main__":
    main()

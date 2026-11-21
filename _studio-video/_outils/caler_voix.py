# -*- coding: utf-8 -*-
"""Cale une pub sur la voix de Mongazi : la voix nettoyée, chaque mot et son temps, ligne par ligne.

    python _outils/caler_voix.py <fichier-voix>        (m4a, ogg, opus, mp3, wav)
    python _outils/caler_voix.py --provisoire          (minutage estimé, en attendant la voix)

    options : --projet pub-ecran-nebula   le dossier de la pub (src/<projet>/ et public/<projet>/)
              --avance 0.35               le premier mot tombe à 0,35 s (la voix est décalée pour ça)
              --sans-cache                retranscrire même si <voix>.deepgram.json existe
              --sortie <fichier.json>     écrire le minutage ailleurs (pour un essai, sans toucher à celui de la pub)
              --forcer                    laisser --provisoire remplacer un minutage calé sur la vraie voix

Ce qu'il fait, dans l'ordre :
1. convertit la voix en WAV 48 kHz mono ;
2. la nettoie : passe-haut 80 Hz, débruitage léger (afftdn), puis -16 LUFS (loudnorm en deux passes, crête -1,5 dBTP) ;
3. la transcrit avec Deepgram nova-3 en français, mot à mot (clé `DEEPGRAM_API_KEY` dans `secrets/deepgram.env`),
   ou relit `<voix>.deepgram.json` posé à côté de la voix : la réponse est gardée là, on ne paie qu'une fois ;
4. aligne chaque mot du TEXTE DIT (`src/<projet>/script.json`) sur les mots entendus, en souplesse : un mot changé,
   ajouté, oublié, deux mots collés (« écris-moi » / « écris moi ») ou un nombre écrit en chiffres ;
5. écrit `src/<projet>/minutage.json` (une entrée par ligne : début, fin, mots et leurs temps) et
   `public/<projet>/voix.wav`.

⚠️ Le texte affiché reste celui du script : il fait foi (Deepgram entend « Nebulla », « prêt », « il l'appuie »). Les
écarts sont listés à l'écran pour qu'un humain les relise. Si Mongazi change ses mots, on corrige `script.json` et on
relance.
⚠️ La voix d'un client ne passe jamais par ici : c'est la voix de Mongazi, pour ses propres pubs.
"""
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ICI = Path(__file__).resolve().parent.parent          # _studio-video/
RACINE = ICI.parent                                    # nebula-agency/

CIBLE_LUFS = -16.0
CRETE = -1.5


def option(nom, defaut):
    if nom in sys.argv:
        i = sys.argv.index(nom)
        return sys.argv[i + 1]
    return defaut


PROJET = option("--projet", "pub-ecran-nebula")
AVANCE = float(option("--avance", "0.35"))
SCRIPT = ICI / "src" / PROJET / "script.json"
MINUTAGE = Path(option("--sortie", str(ICI / "src" / PROJET / "minutage.json"))).resolve()
VOIX_SORTIE = ICI / "public" / PROJET / "voix.wav"


def outil_ffmpeg():
    trouve = shutil.which("ffmpeg")
    if trouve:
        return trouve
    local = ICI / "node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe"
    if local.exists():
        return str(local)
    raise SystemExit("ffmpeg introuvable")


FFMPEG = outil_ffmpeg()


def ffmpeg(*args):
    r = subprocess.run([FFMPEG, "-hide_banner", "-nostdin", "-y", *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit("ffmpeg a échoué :\n" + r.stderr[-2000:])
    return r.stderr


# ─────────────────────────────── le texte ───────────────────────────────

UNITES = ["zero", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze",
          "treize", "quatorze", "quinze", "seize"]
DIZAINES = {2: "vingt", 3: "trente", 4: "quarante", 5: "cinquante", 6: "soixante"}


def nombre_fr(n):
    """Le nombre en lettres, collé (« quarantehuit ») : Deepgram écrit tantôt 48, tantôt quarante-huit."""
    if n < 17:
        return UNITES[n]
    if n < 20:
        return "dix" + UNITES[n - 10]
    if n < 70:
        d, u = divmod(n, 10)
        return DIZAINES[d] + ("" if u == 0 else ("etun" if u == 1 else UNITES[u]))
    if n < 80:
        return "soixante" + ("etonze" if n == 71 else nombre_fr(n - 60))
    if n < 100:
        return "quatrevingt" + ("s" if n == 80 else nombre_fr(n - 80))
    if n < 1000:
        c, r = divmod(n, 100)
        return ("" if c == 1 else UNITES[c]) + "cent" + ("" if r == 0 else nombre_fr(r))
    return str(n)


def normal(s):
    """Ce qu'on compare : minuscules, sans accents, sans ponctuation, les nombres en lettres."""
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"\d+", lambda m: nombre_fr(int(m.group())), s)
    return re.sub(r"[^a-z]", "", s)


OUVRANTS = "«(“"


def mots_du_script(ligne):
    """Les mots affichés d'une ligne. La ponctuation isolée (« : », « ? », « » ») se colle à son mot par une espace
    insécable, comme le veut la typographie française, pour ne jamais tomber seule en début de sous-titre."""
    bruts = [m for m in ligne.split(" ") if m]
    mots = []
    attente = ""
    for m in bruts:
        if normal(m) == "":
            if m[0] in OUVRANTS:
                attente += m + "\u00a0"
            elif mots:
                mots[-1] += "\u00a0" + m
            else:
                attente += m + "\u00a0"
            continue
        mots.append(attente + m)
        attente = ""
    if attente and mots:
        mots[-1] += "\u00a0" + attente.strip()
    return mots


# ─────────────────────────────── l'alignement ───────────────────────────────

ECART = -0.55          # un mot du script que la voix ne dit pas, ou un mot entendu que le script n'a pas
COLLE = 0.15           # deux mots pour un (« écris-moi » / « écris » « moi ») : un peu moins sûr qu'un mot pour un


def ressemblance(a, b):
    if not a or not b:
        return -1.0
    if a == b:
        return 1.0
    return 2 * SequenceMatcher(None, a, b, autojunk=False).ratio() - 1


def aligner(script, entendus):
    """Programmation dynamique (Needleman-Wunsch) entre les mots du script et les mots entendus.
    Rend, pour chaque mot du script, la liste des mots entendus qui lui correspondent, et la part qu'il en prend."""
    S = [normal(m) for m in script]
    T = [normal(w["word"]) for w in entendus]
    n, m = len(S), len(T)
    neg = -1e9
    score = np.full((n + 1, m + 1), neg)
    retour = {}
    score[0, 0] = 0
    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0:
                continue
            best, choix = neg, None
            if i and j:
                v = score[i - 1, j - 1] + ressemblance(S[i - 1], T[j - 1])
                if v > best:
                    best, choix = v, (1, 1)
            if i:
                v = score[i - 1, j] + ECART
                if v > best:
                    best, choix = v, (1, 0)
            if j:
                v = score[i, j - 1] + ECART
                if v > best:
                    best, choix = v, (0, 1)
            if i >= 2 and j:
                v = score[i - 2, j - 1] + ressemblance(S[i - 2] + S[i - 1], T[j - 1]) - COLLE
                if v > best:
                    best, choix = v, (2, 1)
            if i and j >= 2:
                v = score[i - 1, j - 2] + ressemblance(S[i - 1], T[j - 2] + T[j - 1]) - COLLE
                if v > best:
                    best, choix = v, (1, 2)
            score[i, j] = best
            retour[(i, j)] = choix
    paires = []
    i, j = n, m
    while i or j:
        di, dj = retour[(i, j)]
        paires.append((list(range(i - di, i)), list(range(j - dj, j))))
        i, j = i - di, j - dj
    paires.reverse()
    return paires


def temps_des_mots(script, entendus, paires):
    """Le début et la fin de chaque mot du script ; un mot que la voix n'a pas dit prend sa place entre ses voisins."""
    temps = [None] * len(script)
    ecarts = []
    for si, tj in paires:
        if si and tj:
            a = min(entendus[j]["start"] for j in tj)
            b = max(entendus[j]["end"] for j in tj)
            if len(si) == 1:
                temps[si[0]] = [a, b]
            else:                                          # deux mots du script pour un mot entendu
                l = [max(1, len(normal(script[k]))) for k in si]
                c = a
                for k, lk in zip(si, l):
                    d = (b - a) * lk / sum(l)
                    temps[k] = [c, c + d]
                    c += d
            entendu = " ".join(entendus[j].get("punctuated_word", entendus[j]["word"]) for j in tj)
            dit = " ".join(script[k] for k in si)
            if ressemblance(normal(dit), normal(entendu)) < 0.6:
                ecarts.append((si[0], dit, entendu))
        elif si:
            for k in si:
                ecarts.append((k, script[k], "(pas entendu)"))
        elif tj:
            for j in tj:
                ecarts.append((None, "(rien dans le script)", entendus[j].get("punctuated_word", entendus[j]["word"])))
    # les trous : entre le voisin d'avant et celui d'après, à proportion de la longueur des mots
    k = 0
    while k < len(temps):
        if temps[k] is not None:
            k += 1
            continue
        fin_trou = k
        while fin_trou < len(temps) and temps[fin_trou] is None:
            fin_trou += 1
        avant = temps[k - 1][1] if k > 0 else (temps[fin_trou][0] - 0.3 * (fin_trou - k) if fin_trou < len(temps) else 0)
        apres = temps[fin_trou][0] if fin_trou < len(temps) else avant + 0.3 * (fin_trou - k)
        apres = max(apres, avant + 0.12 * (fin_trou - k))
        l = [max(1, len(normal(script[q]))) for q in range(k, fin_trou)]
        c = avant
        for q, lq in zip(range(k, fin_trou), l):
            d = (apres - avant) * lq / sum(l)
            temps[q] = [c, c + d]
            c += d
        k = fin_trou
    return temps, ecarts


# ─────────────────────────────── la voix ───────────────────────────────

def lire_cle():
    for l in io.open(RACINE / "secrets" / "deepgram.env", encoding="utf-8"):
        if "=" in l and not l.strip().startswith("#"):
            nom, val = l.split("=", 1)
            if "DEEPGRAM" in nom.upper() or "KEY" in nom.upper():
                return val.strip().strip('"').strip("'")
    raise SystemExit("clé DEEPGRAM_API_KEY introuvable dans secrets/deepgram.env")


def deepgram(wav):
    url = ("https://api.deepgram.com/v1/listen?model=nova-3&language=fr&punctuate=true&smart_format=true")
    req = urllib.request.Request(url, data=Path(wav).read_bytes(), method="POST",
                                 headers={"Authorization": "Token " + lire_cle(), "Content-Type": "audio/wav"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Deepgram a répondu HTTP {e.code} : {e.read()[:300]!r}")


def debut_du_son(wav):
    """Le premier instant où la voix sort du silence (fenêtres de 10 ms, au-dessus de -45 dBFS et de 40 dB sous la
    crête) : Deepgram arrondit ses débuts, et un « Chaque » annoncé à 0,00 s peut commencer à 0,08 s."""
    x, sr = sf.read(wav, dtype="float32", always_2d=True)
    x = x.mean(axis=1)
    sos = signal.butter(4, 80, "highpass", fs=sr, output="sos")
    x = signal.sosfilt(sos, x)
    pas = int(0.01 * sr)
    n = len(x) // pas
    rms = np.sqrt(np.mean(x[: n * pas].reshape(n, pas) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    seuil = max(-45.0, db.max() - 40.0)
    au_dessus = np.nonzero(db > seuil)[0]
    return (au_dessus[0] * pas / sr) if len(au_dessus) else 0.0, len(x) / sr


def nettoyer(brut, sortie, decalage):
    """Décalage, passe-haut, débruitage léger, puis -16 LUFS en deux passes (la première mesure, la seconde applique)."""
    if decalage >= 0:
        cale = f"adelay=delays={round(decalage * 1000)}:all=1"
    else:
        cale = f"atrim=start={-decalage:.4f},asetpts=PTS-STARTPTS"
    chaine = f"{cale},highpass=f=80,afftdn=nr=10:nf=-50:tn=1"
    journal = ffmpeg("-i", str(brut), "-af", f"{chaine},loudnorm=I={CIBLE_LUFS}:TP={CRETE}:LRA=11:print_format=json",
                     "-f", "null", "-")
    mesure = json.loads(journal[journal.rindex("{"): journal.rindex("}") + 1])
    seconde = (f"{chaine},loudnorm=I={CIBLE_LUFS}:TP={CRETE}:LRA=11:measured_I={mesure['input_i']}"
               f":measured_TP={mesure['input_tp']}:measured_LRA={mesure['input_lra']}"
               f":measured_thresh={mesure['input_thresh']}:offset={mesure['target_offset']}:linear=true"
               f":print_format=json")
    journal = ffmpeg("-i", str(brut), "-af", seconde, "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(sortie))
    final = json.loads(journal[journal.rindex("{"): journal.rindex("}") + 1])
    return mesure, final


def verifier(wav):
    journal = ffmpeg("-i", str(wav), "-af", "ebur128=peak=true", "-f", "null", "-")
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", journal)
    p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", journal)
    return (float(i[-1]) if i else float("nan")), (float(p[-1]) if p else float("nan"))


# ─────────────────────────────── le minutage ───────────────────────────────

def lire_script():
    d = json.loads(SCRIPT.read_text(encoding="utf-8"))
    return [mots_du_script(l) for l in d["lignes"]], d["lignes"]


def ecrire_minutage(lignes_mots, textes, temps_par_ligne, source, voix, decalage, duree_voix, entendu_par_ligne=None):
    lignes = []
    for n, (mots, texte, temps) in enumerate(zip(lignes_mots, textes, temps_par_ligne), start=1):
        entree = {
            "n": n,
            "texte": texte,
            "debut": round(temps[0][0], 3),
            "fin": round(temps[-1][1], 3),
            "mots": [{"m": m, "a": round(a, 3), "b": round(b, 3)} for m, (a, b) in zip(mots, temps)],
        }
        if entendu_par_ligne:
            entree["entendu"] = entendu_par_ligne[n - 1]
        lignes.append(entree)
    doc = {
        "note": "Écrit par _outils/caler_voix.py : ne pas éditer à la main, relancer l'outil.",
        "source": source,
        "voix": voix,
        "decalage": round(decalage, 3),
        "duree_voix": round(duree_voix, 3),
        "fin_voix": lignes[-1]["fin"],
        "lignes": lignes,
    }
    MINUTAGE.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return doc


def provisoire():
    """En attendant la voix : 2,6 mots par seconde, 0,6 s entre deux lignes, 1 s après les lignes 2 et 7, 1,2 s avant
    la ligne 16 ; dans une ligne, chaque mot dure à proportion de sa longueur."""
    # ⚠️ jamais par-dessus un minutage calé sur la vraie voix (arrivé le 21/11 : un essai a écrasé le vrai minutage)
    if MINUTAGE.exists() and "--forcer" not in sys.argv:
        if json.loads(MINUTAGE.read_text(encoding="utf-8")).get("source") == "voix":
            raise SystemExit(f"{MINUTAGE} est calé sur la vraie voix : un minutage provisoire ne le remplace pas. "
                             "Utiliser --sortie <fichier> pour un essai, ou --forcer.")
    lignes_mots, textes = lire_script()
    t = 0.7
    temps_par_ligne = []
    for n, mots in enumerate(lignes_mots, start=1):
        if n > 1:
            t += 1.0 if n - 1 in (2, 7) else 0.6
            if n == 16:
                t += 0.6                                   # 0,6 + 0,6 = 1,2 s avant la signature
        duree = len(mots) / 2.6
        poids = [len(normal(m)) + 2 for m in mots]
        temps, c = [], t
        for p in poids:
            d = duree * p / sum(poids)
            temps.append([c, c + d])
            c += d
        temps_par_ligne.append(temps)
        t = c
    doc = ecrire_minutage(lignes_mots, textes, temps_par_ligne, "provisoire", None, 0.0, t)
    print(f"minutage PROVISOIRE écrit : {MINUTAGE} (voix estimée de {doc['lignes'][0]['debut']:.2f} à {doc['fin_voix']:.2f} s)")
    for l in doc["lignes"]:
        print(f"{l['n']:>3}  {l['debut']:6.2f} {l['fin']:6.2f}  {l['texte']}")


def caler(chemin):
    chemin = Path(chemin).resolve()
    if not chemin.exists():
        raise SystemExit(f"voix introuvable : {chemin}")
    lignes_mots, textes = lire_script()
    script = [m for mots in lignes_mots for m in mots]
    ligne_du_mot = [n for n, mots in enumerate(lignes_mots) for _ in mots]

    with tempfile.TemporaryDirectory() as tmp:
        brut = Path(tmp) / "brut.wav"
        ffmpeg("-i", str(chemin), "-vn", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", str(brut))
        onset, duree = debut_du_son(brut)

        cache = chemin.with_suffix(".deepgram.json")
        if cache.exists() and "--sans-cache" not in sys.argv:
            reponse = json.loads(cache.read_text(encoding="utf-8"))
            print(f"transcription relue : {cache.name}")
        else:
            print("transcription Deepgram nova-3…")
            reponse = deepgram(brut)
            cache.write_text(json.dumps(reponse, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"transcription gardée : {cache.name}")
        entendus = reponse["results"]["channels"][0]["alternatives"][0]["words"]
        if not entendus:
            raise SystemExit("Deepgram n'a entendu aucun mot.")
        if entendus[-1]["end"] < duree - 6:
            print(f"⚠️ Deepgram s'arrête à {entendus[-1]['end']:.1f} s sur {duree:.1f} s : la fin n'est peut-être pas "
                  "transcrite. Relancer avec --sans-cache, ou vérifier la voix.")

        premier = min(onset, entendus[0]["start"])
        decalage = AVANCE - premier
        mesure, final = nettoyer(brut, Path(tmp) / "voix.wav", decalage)
        VOIX_SORTIE.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Path(tmp) / "voix.wav", VOIX_SORTIE)

    paires = aligner(script, entendus)
    temps, ecarts = temps_des_mots(script, entendus, paires)
    temps = [[a + decalage, b + decalage] for a, b in temps]

    # ce que Deepgram a entendu, rangé par ligne (pour relire les écarts)
    entendu_par_ligne = [[] for _ in lignes_mots]
    derniere = 0
    for si, tj in paires:
        if si:
            derniere = ligne_du_mot[si[0]]
        for j in tj:
            entendu_par_ligne[derniere].append(entendus[j].get("punctuated_word", entendus[j]["word"]))
    entendu_par_ligne = [" ".join(e) for e in entendu_par_ligne]

    temps_par_ligne, k = [], 0
    for mots in lignes_mots:
        temps_par_ligne.append(temps[k: k + len(mots)])
        k += len(mots)
    duree_voix = duree + decalage
    doc = ecrire_minutage(lignes_mots, textes, temps_par_ligne, "voix", f"{PROJET}/voix.wav", decalage, duree_voix,
                          entendu_par_ligne)

    lufs, crete = verifier(VOIX_SORTIE)
    print(f"\nvoix : {chemin.name} → {VOIX_SORTIE.relative_to(ICI)}")
    print(f"  début du son {premier:.2f} s → décalée de {decalage:+.2f} s (premier mot à {AVANCE:.2f} s)")
    print(f"  avant : {float(mesure['input_i']):.1f} LUFS, crête {float(mesure['input_tp']):.1f} dBTP"
          f" · après : {lufs:.1f} LUFS, crête {crete:.1f} dBFS (cible {CIBLE_LUFS:.0f} LUFS, {CRETE} dBTP)")
    print(f"\n{'n':>2}  {'début':>6} {'fin':>6}  texte dit / entendu")
    for l in doc["lignes"]:
        print(f"{l['n']:>2}  {l['debut']:6.2f} {l['fin']:6.2f}  {l['texte']}")
        if normal(l["texte"]) != normal(l["entendu"]):
            print(f"{'':17}entendu : {l['entendu']}")
    if ecarts:
        print("\nÉcarts entre le texte dit et ce que Deepgram a entendu (le texte dit est gardé à l'écran) :")
        for k, dit, entendu in ecarts:
            ou = f"ligne {ligne_du_mot[k] + 1}" if k is not None else "entre deux lignes"
            print(f"  · {ou} : « {dit} » / entendu « {entendu} »")
    print(f"\nminutage écrit : {MINUTAGE} · voix de {doc['lignes'][0]['debut']:.2f} à "
          f"{doc['fin_voix']:.2f} s, fichier de {duree_voix:.2f} s")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for nom in ("--projet", "--avance", "--sortie"):
        if nom in sys.argv:
            args.remove(sys.argv[sys.argv.index(nom) + 1])
    if "--provisoire" in sys.argv:
        provisoire()
    elif args:
        caler(args[0])
    else:
        raise SystemExit(__doc__)

"""MA LETTRE À… · « Minuit pile, pour maman » : chaque phrase dit-elle ce qu'on croit, et s'entend-elle dans le film ?

    python _outils/malettre_minuit_ecouter.py

Le script du son découpe les deux voix à leurs silences et attribue le n-ième morceau à la n-ième phrase du
texte. Si une prise a une pause de plus (ou de moins), tout glisse d'un cran et le film fait dire à Alimata la
phrase d'à côté, sous le mauvais plan. Le nombre de morceaux ne le prouve pas : on ÉCOUTE, par Whisper, sans
lui souffler le texte (aucun `initial_prompt`), et on compare.

Deux écoutes, sur les mêmes 31 phrases :
    1. la prise seule : chaque morceau découpé est-il la bonne phrase ?
    2. le film (`public/malettre-minuit/mix.wav`, aux instants du minutage) : la phrase s'entend-elle encore
       par-dessus la musique et les bruitages ? Une phrase que Whisper ne reconnaît plus dans le mélange est
       une phrase couverte.
⚠️ TROIS passages de Whisper (les deux prises, le film), au mot, puis on range les mots par phrase. Une première
version écoutait les 62 morceaux un par un : Whisper traite toujours 30 s d'audio, même pour une seconde, et
l'écoute durait plus de 25 minutes sur ce PC.
⚠️ Une phrase que l'écoute du film entier ne trouve pas est réécoutée DE PRÈS (sa fenêtre seule) : sur un long
enregistrement, Whisper saute volontiers un mot isolé qui suit une plage de musique (« Maman… », juste après minuit,
le 2026-10-22, alors que la mesure de niveau donnait la voix devant).
Sortie 1 si une phrase ne ressemble pas assez au texte (seuil : 0,6 de mots en commun, après normalisation).
⚠️ Lourd (Whisper large-v3-turbo sur le processeur, environ 1 Go) : jamais pendant un rendu.
"""
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from malettre_minuit_son import ALIMATA, KOFFI, SOURCES, SR, decoder, segments  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ICI = Path(__file__).resolve().parent.parent
MIX = ICI / "public/malettre-minuit/mix.wav"
MINUTAGE = json.loads((ICI / "src/malettre-minuit/minutage.json").read_text(encoding="utf-8"))
SEUIL = 0.6

# Whisper écrit les nombres en chiffres : on les remet en lettres, comme le texte.
NOMBRES = {"3": "trois", "5": "cinq", "60": "soixante", "1000": "mille", "1": "un"}


def mots(s):
    s = unicodedata.normalize("NFD", s.lower().replace("’", "'"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"(\d)[\s  ](\d{3})", r"\1\2", s)  # « 1 000 » → « 1000 »
    s = re.sub(r"[^a-z0-9]+", " ", s.replace("'", " "))
    return [NOMBRES.get(w, w) for w in s.split()]


def ressemblance(attendu, entendu):
    return difflib.SequenceMatcher(a=mots(attendu), b=mots(entendu), autojunk=False).ratio()


def main():
    from faster_whisper import WhisperModel

    modele = WhisperModel("mobiuslabsgmbh/faster-whisper-large-v3-turbo", device="cpu", compute_type="int8")

    def ecouter(x48, nom):
        """Un enregistrement entier (48 kHz, mono) → ses mots, avec leur instant (secondes), sans indice."""
        print("… Whisper écoute %s (%.0f s)" % (nom, len(x48) / SR), flush=True)
        x16 = signal.resample_poly(x48, 1, 3).astype(np.float32)
        segs, _ = modele.transcribe(x16, language="fr", beam_size=5, vad_filter=False, word_timestamps=True,
                                    condition_on_previous_text=False)
        return [(w.word, (w.start + w.end) / 2) for s in segs for w in s.words]

    def de_pres(x48, a, b):
        """Une fenêtre seule, avec un souffle de chaque côté : ce que Whisper y entend."""
        i0, i1 = int(max(0, a - 0.4) * SR), int(min(len(x48) / SR, b + 0.4) * SR)
        segs, _ = modele.transcribe(signal.resample_poly(x48[i0:i1], 1, 3).astype(np.float32), language="fr", beam_size=5,
                                    vad_filter=False, condition_on_previous_text=False, without_timestamps=True)
        return " ".join(s.text.strip() for s in segs).strip()

    def dans(entendus, a, b):
        """Les mots dont le milieu tombe dans [a, b] : ce que Whisper a entendu là."""
        return "".join(w for w, m in entendus if a <= m <= b).strip()

    lignes = {l["id"]: l for l in MINUTAGE["lignes"]}
    sr, mix = wavfile.read(MIX)
    assert sr == SR
    mono = mix.astype(np.float64).mean(1) / 32768
    film = ecouter(mono, "le film")
    mauvais = []
    for nom, textes, prefixe in (("koffi", KOFFI, "k"), ("alimata", ALIMATA, "a")):
        x = decoder(SOURCES[nom], 1)
        coupes = segments(x, len(textes), nom)
        prise = ecouter(x, "la prise de " + nom)
        print("── %s : %d phrases" % (nom, len(coupes)))
        for k, ((a, b), texte) in enumerate(zip(coupes, textes)):
            lid = "%s%d" % (prefixe, k + 1)
            l = lignes[lid]
            p_txt = dans(prise, a, b)
            f_txt = dans(film, l["debut"] - 0.05, l["fin"] + 0.05)
            rp, rf = ressemblance(texte, p_txt), ressemblance(texte, f_txt)
            if rf < SEUIL:
                proche = de_pres(mono, l["debut"], l["fin"])
                if ressemblance(texte, proche) > rf:
                    f_txt, rf = proche + "  (de près)", ressemblance(texte, proche)
            drapeau = "✓" if min(rp, rf) >= SEUIL else "✗"
            print("%s %-3s %5.2f s  « %s »" % (drapeau, lid, l["debut"], texte))
            print("        prise %.2f  « %s »" % (rp, p_txt))
            print("        film  %.2f  « %s »" % (rf, f_txt))
            if drapeau == "✗":
                mauvais.append(lid)
    if mauvais:
        print("✗ %d phrase(s) à écouter : %s" % (len(mauvais), ", ".join(mauvais)))
        return 1
    print("✓ les %d phrases sont les bonnes, et elles s'entendent dans le film" % len(lignes))
    return 0


if __name__ == "__main__":
    sys.exit(main())

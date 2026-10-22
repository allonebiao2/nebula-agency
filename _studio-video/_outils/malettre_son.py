"""MA LETTRE À… : la voix de Mongazi posée, et l'image calée sur elle (pas l'inverse).

ENTRÉES (hors dépôt) :
    _partage/ma lettre/voix/<version>.mp3   les six prises ElevenLabs de VOIX.md
                                            (fr-30, en-30, fr-15-lettre, fr-15-plume,
                                            en-15-letter, en-15-quill)

SORTIES :
    public/malettre/voix-<version>.wav              la voix nettoyée (−16 LUFS, limiteur)
    public/malettre/transcription-<version>.json    Whisper large-v3-turbo, au mot, SANS indice
    src/malettre/minutage.ts                        réécrit : chaque plan commence sur SA
                                                    phrase, ses instants tombent sur leur mot

LE CALAGE. Les phrases sont celles des blocs « Texte à coller » de VOIX.md, lues dans
le fichier (jamais recopiées ici). Chaque mot du texte est rapproché du mot que Whisper
a entendu (alignement de séquences, sans accents ni ponctuation) : un mot mal entendu
ne décale pas la suite. Chaque phrase ouvre un plan, 0,2 s avant elle ; ses `temps`
sont le début des mots-clés (un prénom, une occasion, « plume », « cire »…).
Si la voix va plus vite que l'image (une lettre qui s'ouvre se LIT : `MINIMUM`), la prise
est coupée dans le souffle qui précède la phrase suivante, et cette phrase attend.
⚠️ Une version sans MP3 garde son minutage provisoire : on peut caler au fur et à mesure.
⚠️ Une coupe de 15 s dont la voix déborde est REFUSÉE (un statut WhatsApp coupe à 15 s) :
il faut une prise plus rapide (vitesse 1,08 → 1,15), pas une image plus courte.

    python _outils/malettre_son.py              (toutes les versions dont le MP3 est là)
    python _outils/malettre_son.py --essai      (sans audio : une fausse transcription,
                                                 pour vérifier le calage et l'écriture)
"""
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
VOIX_MD = ICI / "src/malettre/VOIX.md"
SOURCES = ICI.parent / "_partage/ma lettre/voix"
PUB = ICI / "public/malettre"
MINUTAGE = ICI / "src/malettre/minutage.ts"
DEPART = 0.3  # la voix part à 0,3 s : le premier mot n'est pas coupé par l'ouverture d'un lecteur

# L'ordre des blocs « Texte à coller » dans VOIX.md, et ce que chaque version en fait.
# plan : (id, numéro de la phrase qui l'ouvre, mots-clés dont le début devient un `temps`)
VERSIONS = {
    "fr-30": {"bloc": 0, "langue": "fr", "duree": 30, "fin": "prix", "plans": [
        ("accroche", 0, ["papa", "afi", "maman"]), ("scellee", 1, []), ("plume", 2, ["plume"]),
        ("attente", 3, ["cachet"]), ("ouverture", 4, ["cire", "brise"]),
        ("occasions", 5, ["anniversaire", "demande", "pardon", "fete"]), ("marque", 6, [])]},
    "en-30": {"bloc": 1, "langue": "en", "duree": 30, "fin": "prix", "plans": [
        ("accroche", 0, ["dad", "afi", "mum"]), ("scellee", 1, []), ("plume", 2, ["quill"]),
        ("attente", 3, ["seal"]), ("ouverture", 4, ["wax", "break"]),
        ("occasions", 5, ["birthday", "proposal", "apology", "celebration"]), ("marque", 6, [])]},
    "fr-15-lettre": {"bloc": 2, "langue": "fr", "duree": 15, "fin": "prix", "plans": [
        ("accroche", 0, ["papa", "afi", "maman"]), ("scellee", 1, []), ("ouverture", 2, ["cire", "lit"]),
        ("marque", 3, [])]},
    "fr-15-plume": {"bloc": 3, "langue": "fr", "duree": 15, "fin": "plume", "plans": [
        ("pageBlanche", 0, []), ("plume", 1, []), ("scellee", 2, []), ("marque", 3, [])]},
    "en-15-letter": {"bloc": 4, "langue": "en", "duree": 15, "fin": "prix", "plans": [
        ("accroche", 0, ["dad", "afi", "mum"]), ("scellee", 1, []), ("ouverture", 2, ["wax", "read"]),
        ("marque", 3, [])]},
    "en-15-quill": {"bloc": 5, "langue": "en", "duree": 15, "fin": "plume", "plans": [
        ("pageBlanche", 0, []), ("plume", 1, []), ("scellee", 2, []), ("marque", 3, [])]},
}


def norme(m):
    m = unicodedata.normalize("NFD", m.lower())
    m = "".join(c for c in m if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", m)


def mots(texte):
    """Les mots d'une phrase, coupés comme Whisper les coupe à peu près (l'apostrophe sépare)."""
    return [w for w in (norme(x) for x in re.split(r"[\s'’]+", texte)) if w]


def blocs_voix():
    """Les blocs de code de VOIX.md, dans l'ordre : une liste de phrases par bloc."""
    s = VOIX_MD.read_text(encoding="utf-8")
    return [[l.strip() for l in b.strip().splitlines() if l.strip()] for b in re.findall(r"```\n(.*?)```", s, re.S)]


def transcrire(mp3, langue, cache):
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    from faster_whisper import WhisperModel

    modele = WhisperModel("mobiuslabsgmbh/faster-whisper-large-v3-turbo", device="cpu", compute_type="int8")
    segs, _ = modele.transcribe(str(mp3), language=langue, word_timestamps=True, vad_filter=False)
    sortie = [{"mot": w.word.strip(), "debut": round(w.start, 3), "fin": round(w.end, 3)} for s in segs for w in s.words]
    cache.write_text(json.dumps(sortie, ensure_ascii=False, indent=0), encoding="utf-8")
    return sortie


def caler(phrases, entendus):
    """Pour chaque mot du texte : (phrase, mot normé, début entendu ou None)."""
    texte = [(i, w) for i, ph in enumerate(phrases) for w in mots(ph)]
    oreille = []  # Whisper colle parfois « l'écris » : on le recoupe comme le texte
    for e in entendus:
        for w in mots(e["mot"]):
            oreille.append((w, e["debut"], e["fin"]))
    sm = difflib.SequenceMatcher(a=[w for _, w in texte], b=[w for w, _, _ in oreille], autojunk=False)
    debut = [None] * len(texte)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            debut[a + k] = oreille[b + k][1]
    fin_voix = max((f for _, _, f in oreille), default=0.0)
    return [(i, w, d) for (i, w), d in zip(texte, debut)], fin_voix, sm.ratio()


# Le temps qu'il faut à chaque plan pour que son geste se lise (secondes). Une voix
# rapide ne raccourcit pas une lettre qui s'ouvre : on attend avant la phrase suivante.
MINIMUM = {"accroche": 2.8, "scellee": 3.0, "pageBlanche": 1.8, "plume": 4.2, "attente": 4.2,
           "ouverture": 4.4, "occasions": 3.2, "marque": 2.6}


def plan_de(version, phrases, entendus):
    """Le plan de la version, et les morceaux de voix : (début, fin) dans la prise, instant du film."""
    v = VERSIONS[version]
    cale, fin_voix, ratio = caler(phrases, entendus)
    if [n for _, n, _ in v["plans"]] != list(range(len(phrases))):
        raise SystemExit(f"⛔ {version} : chaque phrase de VOIX.md doit ouvrir un plan, dans l'ordre")

    def bornes(n):
        ds = [d for i, _, d in cale if i == n and d is not None]
        if not ds:
            raise SystemExit(f"⛔ {version} : la phrase {n + 1} (« {phrases[n]} ») n'a pas été entendue")
        return min(ds)

    def debut_mot(n, cle):
        for i, w, d in cale:
            if i == n and w.startswith(cle) and d is not None:
                return d
        raise SystemExit(f"⛔ {version} : le mot « {cle} » n'a pas été entendu dans « {phrases[n]} »")

    debuts = [bornes(n) for n in range(len(phrases))]
    # Les coupes de la prise : 0,12 s avant chaque phrase (dans le souffle), jamais dans un mot.
    coupes = [0.0] + [d - 0.12 for d in debuts[1:]] + [fin_voix + 0.25]
    decalage, plans, morceaux = DEPART, [], []
    for k, (pid, n, cles) in enumerate(v["plans"]):
        debut = 0.0 if k == 0 else round(debuts[n] + decalage - 0.2, 2)
        if plans:
            court = MINIMUM[plans[-1]["id"]] - (debut - plans[-1]["debut"])
            if court > 0:
                decalage += court
                debut = round(debut + court, 2)
        morceaux.append((coupes[n], coupes[n + 1], coupes[n] + decalage))
        plans.append({"id": pid, "debut": debut, "temps": [round(debut_mot(n, c) + decalage, 2) for c in cles]})

    duree = float(v["duree"])
    fin_film = fin_voix + decalage + 0.6
    if fin_film > duree:
        if duree <= 15:
            raise SystemExit(f"⛔ {version} : la voix finit à {fin_film:.2f} s pour une coupe de {duree:.0f} s. "
                             "Une prise plus rapide (vitesse 1,15), pas une image plus courte.")
        print(f"  ⚠️ {version} : la voix finit à {fin_film:.2f} s, la vidéo passe à {fin_film:.1f} s")
        duree = round(fin_film + 0.05, 1)
    for k, pl in enumerate(plans):
        pl["fin"] = plans[k + 1]["debut"] if k + 1 < len(plans) else duree
    if plans[-1]["fin"] - plans[-1]["debut"] < MINIMUM["marque"]:
        raise SystemExit(f"⛔ {version} : la marque n'a que {plans[-1]['fin'] - plans[-1]['debut']:.2f} s")
    return {"langue": v["langue"], "duree": duree, "fin": v["fin"], "plans": plans}, morceaux, ratio


def ecrire_minutage(cales):
    """Réécrit les versions calées dans minutage.ts ; les autres gardent leur ligne provisoire."""
    s = MINUTAGE.read_text(encoding="utf-8")
    debut = s.index("export const VERSIONS")
    corps = s[debut:]
    for vid, (v, voix) in cales.items():
        plans = ", ".join(
            "{" + f"id: '{p['id']}', debut: {p['debut']}, fin: {p['fin']}" + (f", temps: {p['temps']}" if p["temps"] else "") + "}"
            for p in v["plans"])
        ligne = (f"\t'{vid}': {{langue: '{v['langue']}', duree: {v['duree']}, voix: '{voix}', fin: '{v['fin']}', "
                 f"plans: [{plans}]}},")
        corps = re.sub(rf"\t'{re.escape(vid)}': .*,\n", lambda _: ligne + "\n", corps, count=1)
    MINUTAGE.write_text(s[:debut] + corps, encoding="utf-8")


def voix_wav(mp3, morceaux, duree, sortie):
    """La prise nettoyée, coupée entre ses phrases et chaque phrase posée à son instant."""
    import numpy as np
    from scipy.io import wavfile

    from dimanche_son import limiter
    from grain35_son import SR, lire, traiter_voix

    prise = traiter_voix(lire(mp3, 1))
    x = np.zeros(int(duree * SR))
    for a, b, t in morceaux:
        m = prise[int(a * SR):int(b * SR)].copy()
        n = min(len(m), int(0.008 * SR))  # 8 ms de fondu aux coupes : pas de clic
        if n:
            m[:n] *= np.linspace(0, 1, n)
            m[-n:] *= np.linspace(1, 0, n)
        i = int(t * SR)
        x[i:i + len(m)] += m[:max(0, len(x) - i)]
    x = limiter(x, plafond_db=-1.5)
    wavfile.write(sortie, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))


def main():
    essai = "--essai" in sys.argv
    blocs = blocs_voix()
    if len(blocs) != 6:
        raise SystemExit(f"⛔ VOIX.md porte {len(blocs)} blocs « Texte à coller », il en faut 6")
    PUB.mkdir(parents=True, exist_ok=True)
    cales = {}
    for vid, v in VERSIONS.items():
        phrases = blocs[v["bloc"]]
        if essai:
            # Une fausse oreille : 0,32 s par mot, 0,45 s de souffle entre deux phrases.
            entendus, t = [], 0.1
            for ph in phrases:
                for w in re.split(r"\s+", ph):
                    entendus.append({"mot": w, "debut": round(t, 3), "fin": round(t + 0.28, 3)})
                    t += 0.32 if v["duree"] == 30 else 0.26
                t += 0.45 if v["duree"] == 30 else 0.25
            m, morceaux, ratio = plan_de(vid, phrases, entendus)
            print(f"  {vid} : {len(m['plans'])} plans, durée {m['duree']} s, accord {ratio:.2f}, "
                  f"attente ajoutée {morceaux[-1][2] - morceaux[-1][0] - DEPART:.2f} s")
            for p in m["plans"]:
                print(f"     {p['id']:<12} {p['debut']:>5.2f} → {p['fin']:>5.2f}  {p['temps'] or ''}")
            continue
        mp3 = SOURCES / f"{vid}.mp3"
        if not mp3.exists():
            print(f"  · {vid} : pas de MP3 ({mp3.name}), minutage provisoire gardé")
            continue
        entendus = transcrire(mp3, v["langue"], PUB / f"transcription-{vid}.json")
        m, morceaux, ratio = plan_de(vid, phrases, entendus)
        print(f"  {vid} : accord texte / voix {ratio:.0%}, durée {m['duree']} s")
        if ratio < 0.85:
            print(f"  ⚠️ {vid} : la prise ne dit pas tout à fait le texte de VOIX.md : l'écouter")
        voix_wav(mp3, morceaux, m["duree"], PUB / f"voix-{vid}.wav")
        cales[vid] = (m, f"malettre/voix-{vid}.wav")
    if cales:
        ecrire_minutage(cales)
        print("écrit :", MINUTAGE.relative_to(ICI), "·", ", ".join(cales))


if __name__ == "__main__":
    main()

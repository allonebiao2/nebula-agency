# -*- coding: utf-8 -*-
"""Génère les sons d'atelier d'Hillary M. Styl, avec WaveSpeed.

DIRECTION : **atelier réel**, choisie par Mongazi le 2026-08-11. On entend
l'acier, le tissu, la machine. Hillary vend du fait-main : un son trop poli
dirait le contraire.

⚠️ Ce ne sont pas des ambiances mais des sons PONCTUELS : `ambience: false`,
on a besoin d'une attaque nette, pas d'un raccord invisible.

⚠️ Six sons seulement, ceux qui portent le sens. Un site où chaque geste
sonne devient fatigant en deux minutes, et on peut toujours en ajouter,
jamais retirer une habitude.

Modèle : mirelo-ai/sfx-1.6/text-to-audio · 0,01 $ la seconde.

    python _sons.py           génère ce qui manque
    python _sons.py --refaire tout regénérer
"""
import io
import json
import os
import sys
import time
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
SONS = os.path.join(ICI, "assets", "sons")
BRUT = os.path.join(ICI, "_sources", "sons_bruts")
ENV = r"C:/Users/USER/nebula-agency/secrets/wavespeed.env"
MODELE = "mirelo-ai/sfx-1.6/text-to-audio"

# nom · durée · description. En anglais : le modèle est entraîné dessus.
# On EXCLUT explicitement ce qu'on ne veut pas, sinon il ajoute des voix
# ou une nappe musicale.
SONS_A_FAIRE = [
    ("ouvrir", 1.0,
     "A pair of heavy steel tailor scissors opening once, single crisp "
     "metallic scrape of two blades separating. Dry, close, no reverb. "
     "No music, no voices, no room tone."),

    ("fiche", 0.8,
     "A single piece of heavy cotton fabric lifted and unfolded once, one "
     "short crisp cloth rustle. Dry, close-miked. "
     "No music, no voices, no footsteps."),

    # ⚠️ REECRIT : la premiere version donnait une NAPPE continue (facteur
    # de crete 3,6, enveloppe pleine) au lieu d'un tic. Il faut insister
    # sur l'unicite et sur le silence qui suit.
    ("mesure", 0.35,
     "One single sharp fingernail tap on a hard metal surface, one isolated "
     "transient click, immediately followed by complete silence. Extremely "
     "short and dry, close-miked, no reverb, no tail, no repetition. "
     "No music, no voices, no background noise."),

    ("etape", 1.0,
     "An old mechanical sewing machine stitching three or four stitches "
     "then stopping, mechanical needle punching through fabric. Dry, close. "
     "No music, no voices, no motor hum after."),

    ("couper", 0.8,
     "One decisive cut of tailor scissors slicing through fabric, single "
     "clean shear stroke, blades closing. Dry, close-miked, no reverb. "
     "No music, no voices."),

    ("envoyer", 1.1,
     "A sewing thread being pulled tight and knotted once, soft fibrous "
     "friction ending in a small snap. Very close, intimate, quiet. "
     "No music, no voices."),
]


def cle():
    for l in io.open(ENV, encoding="utf-8"):
        if l.startswith("WAVESPEED_API_KEY="):
            return l.split("=", 1)[1].strip().strip('"')
    raise SystemExit("cle WaveSpeed introuvable")


K = cle()
TETE = {"Authorization": "Bearer " + K, "Content-Type": "application/json"}


def solde():
    r = urllib.request.Request("https://api.wavespeed.ai/api/v3/balance",
                               headers={"Authorization": "Bearer " + K})
    return json.loads(urllib.request.urlopen(r, timeout=60).read())["data"]["balance"]


def generer(texte, duree):
    corps = json.dumps({"text_prompt": texte, "duration": duree,
                        "ambience": False, "num_samples": 1}).encode("utf-8")
    req = urllib.request.Request("https://api.wavespeed.ai/api/v3/" + MODELE,
                                 data=corps, headers=TETE)
    ident = json.loads(urllib.request.urlopen(req, timeout=180).read())["data"]["id"]
    print("   %s ..." % ident[:10], end="", flush=True)
    for _ in range(90):
        time.sleep(3)
        r = urllib.request.Request(
            "https://api.wavespeed.ai/api/v3/predictions/%s/result" % ident,
            headers={"Authorization": "Bearer " + K})
        s = json.loads(urllib.request.urlopen(r, timeout=60).read())["data"]
        if s.get("status") == "completed":
            print(" ok")
            return s["outputs"][0]
        if s.get("status") == "failed":
            print(" ECHEC :", s.get("error"))
            return None
        print(".", end="", flush=True)
    print(" delai depasse")
    return None


if __name__ == "__main__":
    os.makedirs(SONS, exist_ok=True)
    os.makedirs(BRUT, exist_ok=True)
    refaire = "--refaire" in sys.argv

    av = solde()
    print("solde avant : %.3f $\n" % av)

    faits = 0
    for nom, duree, texte in SONS_A_FAIRE:
        dest = os.path.join(BRUT, nom + ".mp3")
        if os.path.exists(dest) and not refaire:
            print("%-10s deja la" % nom)
            continue
        print("%-10s" % nom, end=" ", flush=True)
        url = generer(texte, duree)
        if not url:
            continue
        b = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}),
            timeout=180).read()
        io.open(dest, "wb").write(b)
        print("   %-10s %d o" % ("", len(b)))
        faits += 1

    ap = solde()
    print("\nsolde apres : %.3f $   (depense %.3f $ pour %d son%s)"
          % (ap, av - ap, faits, "s" if faits > 1 else ""))
    print("\nEtape suivante : python _sons_finir.py")

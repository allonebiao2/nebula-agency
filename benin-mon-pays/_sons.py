# -*- coding: utf-8 -*-
"""Génère une ambiance sonore par lieu, avec WaveSpeed (Mirelo SFX 1.6).

⚠️ RÈGLE DE PROBITÉ, à ne jamais contourner
Un son généré est une MATIÈRE, pas un document. Aucune de ces ambiances ne
prétend être « l'enregistrement de Ganvié » : ce sont des textures, écrites
comme telles dans les crédits du site, et destinées à être remplacées par de
vrais enregistrements. C'est la même règle que pour les images.

Le modèle : mirelo-ai/sfx-1.6/text-to-audio, le seul qui boucle SANS COUTURE
(`ambience: true`). Une ambiance qui claque toutes les dix secondes est pire
que pas d'ambiance du tout.

Coût : 0,01 $ la seconde. Huit lieux × 8 s = 0,64 $.

    python _sons.py --essai      un seul lieu, pour juger
    python _sons.py              tous les lieux qui manquent
    python _sons.py --refaire X  refait le lieu X
"""
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
SONS = os.path.join(ICI, "assets", "sons")
ENV = r"C:/Users/USER/nebula-agency/secrets/wavespeed.env"
MODELE = "mirelo-ai/sfx-1.6/text-to-audio"
DUREE = 8
PRIX_SEC = 0.01

# Chaque texte décrit une MATIÈRE, jamais « le son du lieu ».
# Les mots sont en anglais : le modèle est entraîné dessus.
LIEUX = [
    ("porte", "Ocean waves breaking steadily on an empty sand beach, deep and "
              "slow, distant surf, faint wind. No voices, no music, no birds."),
    ("ouidah", "Quiet dirt road at dusk in a small West African town, soft warm "
               "wind through palm leaves, very distant faint activity. "
               "No voices, no music."),
    ("cotonou", "Dense open-air market ambience, many footsteps on packed earth, "
                "distant indistinct crowd murmur, occasional motorbike passing "
                "far away. No clear voices, no music."),
    ("ganvie", "Calm shallow lake water lapping against wooden stilts, a single "
               "wooden paddle dipping slowly, faint creaking wood. "
               "No voices, no music."),
    ("abomey", "Very quiet interior courtyard of an old earthen palace, warm "
               "still air, faint dry wind over clay walls, distant weaver bird. "
               "No voices, no music."),
    ("koutammakou", "Dry savanna wind moving over mud walls and thatch, subtle "
                    "grain rustling, wide open silence, very sparse. "
                    "No voices, no music."),
    ("pendjari", "Wide dry bush at midday, hot still air, distant cicadas, "
                 "occasional far bird call, deep spacious silence. "
                 "No voices, no music, no engines."),
    ("fleuve", "Wide slow river flowing, gentle deep water movement, light wind "
               "across open water, very distant shore. No voices, no music."),
]


def cle():
    for l in io.open(ENV, encoding="utf-8"):
        if l.startswith("WAVESPEED_API_KEY="):
            return l.split("=", 1)[1].strip().strip('"')
    raise SystemExit("clé WaveSpeed introuvable")


K = cle()
TETE = {"Authorization": "Bearer " + K, "Content-Type": "application/json"}


def solde():
    r = urllib.request.Request("https://api.wavespeed.ai/api/v3/balance",
                               headers={"Authorization": "Bearer " + K})
    d = json.loads(urllib.request.urlopen(r, timeout=60).read().decode("utf-8"))
    return d["data"]["balance"]


def generer(nom, texte):
    corps = json.dumps({
        "text_prompt": texte,
        "duration": DUREE,
        "ambience": True,          # la boucle sans couture : indispensable
        "num_samples": 1,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.wavespeed.ai/api/v3/" + MODELE, data=corps, headers=TETE)
    d = json.loads(urllib.request.urlopen(req, timeout=180).read().decode("utf-8"))
    ident = d["data"]["id"]
    print("   tâche %s ..." % ident[:12], end="", flush=True)

    for _ in range(90):
        time.sleep(3)
        r = urllib.request.Request(
            "https://api.wavespeed.ai/api/v3/predictions/%s/result" % ident,
            headers={"Authorization": "Bearer " + K})
        s = json.loads(urllib.request.urlopen(r, timeout=60).read().decode("utf-8"))["data"]
        etat = s.get("status")
        if etat == "completed":
            url = s["outputs"][0]
            print(" ok")
            return url
        if etat == "failed":
            print(" ÉCHEC :", s.get("error"))
            return None
        print(".", end="", flush=True)
    print(" délai dépassé")
    return None


def telecharger(url, chemin):
    r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    b = urllib.request.urlopen(r, timeout=180).read()
    io.open(chemin, "wb").write(b)
    return len(b)


if __name__ == "__main__":
    os.makedirs(SONS, exist_ok=True)
    essai = "--essai" in sys.argv
    refaire = None
    if "--refaire" in sys.argv:
        refaire = sys.argv[sys.argv.index("--refaire") + 1]

    av = solde()
    print("solde avant : %.3f $" % av)

    a_faire = LIEUX[:1] if essai else LIEUX
    if refaire:
        a_faire = [x for x in LIEUX if x[0] == refaire]

    faits = []
    for nom, texte in a_faire:
        dest = os.path.join(SONS, nom + ".aac")
        if os.path.exists(dest) and not refaire and not essai:
            print("%-14s déjà là (%d o)" % (nom, os.path.getsize(dest)))
            continue
        print("%-14s" % nom, end=" ", flush=True)
        url = generer(nom, texte)
        if not url:
            continue
        ext = url.split("?")[0].rsplit(".", 1)[-1].lower()
        if ext not in ("mp3", "aac", "wav", "m4a", "flac", "ogg"):
            ext = "mp3"
        dest = os.path.join(SONS, nom + "." + ext)
        t = telecharger(url, dest)
        print("   %-14s %s  %d o" % ("", os.path.basename(dest), t))
        faits.append(nom)

    ap = solde()
    print("\nsolde après : %.3f $   (dépensé %.3f $ pour %d son%s)"
          % (ap, av - ap, len(faits), "s" if len(faits) > 1 else ""))

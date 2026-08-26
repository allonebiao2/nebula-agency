# -*- coding: utf-8 -*-
"""
GENERE LES PHOTOS QUI MANQUENT ENCORE A LA CARTE (petit-dej + desserts).

    python _outils/_gen_plats.py            # ne genere que ce qui manque
    python _outils/_gen_plats.py --force    # regenere tout

⚠️ CE QUE CE SCRIPT N'EST PAS. Le cerveau NEBULA interdit qu'une image generee
   serve de catalogue a un client. Les 48 photos de plats d'Au Braise d'Or sont
   un heritage assume (tranche par Mongazi le 2026-08-20), et il a demande le
   2026-08-26 que les 6 dernieres lignes sans image soient completees dans le
   MEME style. Ce sont des produits de commodite (un cafe serre, un the au
   citron, une boule de glace), pas des creations de la maison : rien ici ne
   pretend montrer une piece unique. Les VRAIES photos, quand elles arrivent,
   remplacent ces fichiers sans toucher au code.

⚠️ LE STYLE EST UN SOCLE, PAS SIX PROMPTS. C'est ce qui fait une serie au lieu
   d'une collection : meme lumiere, meme table, meme optique, une seule phrase
   qui change. Releve sur les images deja en ligne (pd-cappuccino, pd-cafe-lait,
   pd-omelette-nature) : carre 900x900, fond sombre flou, lumiere chaude
   rasante, faible profondeur de champ, sujet seul et centre.
"""
import argparse
import io
import os
import re
import sys
import time
import urllib.request
import json

from PIL import Image

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.join(RACINE, "assets", "images")
PUBLIC = os.path.join(RACINE, "experience", "public", "carte")
SECRET = os.path.join(RACINE, "..", "..", "secrets", "wavespeed.env")

MODELE = "google/nano-banana-pro/text-to-image"
COTE = 900          # les 48 photos existantes font 900x900
QUALITE = 82        # donne ~60-90 Ko, la fourchette des fichiers voisins

# --- le socle, commun aux six -------------------------------------------------
BOIS = ("on a dark aged wooden table with visible grain")
ARDOISE = ("on a dark grey slate serving board")

SOCLE = (
    "Professional food photography for a West African restaurant menu. {sujet}, {support}, "
    "single subject centred in frame, warm low-key side light raking from the left with a soft "
    "falloff into a deep dark blurred background, shallow depth of field, shot on a 100mm macro "
    "lens at f/4, appetising, natural colours, clean and simple composition. "
    "No people, no hands, no text, no lettering, no signature, no watermark, no logo, no branding."
)

# --- une phrase par plat ------------------------------------------------------
PLATS = [
    dict(
        cle="pd-oeuf-plat",
        nom="Œuf sur plat",
        sujet=("Two sunny-side-up fried eggs on a small plain white plate, glossy bright orange "
               "runny yolks, thin lightly crisped golden edges, a few grains of black pepper"),
        support=BOIS,
    ),
    dict(
        cle="pd-cafe-serre",
        nom="Café chaud serré",
        sujet=("A small white porcelain espresso cup filled with short strong black coffee under a "
               "thick hazelnut crema, on a white saucer with a small steel spoon, a wisp of steam"),
        support=BOIS,
    ),
    dict(
        cle="pd-cafe-lait-ecreme",
        nom="Café au lait écrémé",
        sujet=("A clear glass tumbler of milky coffee made with skimmed milk, pale caramel colour, "
               "a thin layer of light foam on top, a small plain steel milk jug standing beside it"),
        support=BOIS,
    ),
    dict(
        cle="pd-lipton-citron",
        nom="Lipton citron",
        sujet=("A clear glass cup of hot lemon tea, translucent amber liquid, a fresh lemon slice "
               "resting on the rim, a plain unmarked paper tea tag hanging over the side, "
               "on a white saucer, a wisp of steam"),
        support=BOIS,
    ),
    dict(
        cle="d-yaourt",
        nom="Yaourt",
        sujet=("A clear glass cup of thick plain white yogurt, smooth glossy surface with a spoon "
               "resting in it, one gentle swirl on top"),
        support=BOIS,
    ),
    dict(
        # ⚠️ TROIS boules : la maison vend 1, 2 ou 3 boules et la carte annonce
        #    la fourchette. Une seule boule sur la photo ferait croire que le
        #    prix haut achete la meme chose que le prix bas.
        cle="d-glace",
        nom="Glace",
        sujet=("Three round scoops of ice cream, vanilla, chocolate and strawberry, in a footed "
               "clear glass coupe, a long spoon resting against the rim, tiny beads of condensation "
               "on the glass"),
        support=BOIS,
    ),
]


def cle_api():
    chemin = os.path.normpath(SECRET)
    with open(chemin, "r", encoding="utf-8", errors="replace") as f:
        m = re.search(r"^WAVESPEED_API_KEY=(.+)$", f.read(), re.M)
    if not m:
        sys.exit("clé WaveSpeed introuvable dans " + chemin)
    return m.group(1).strip()


def poste(cle, prompt):
    """Lance un rendu, renvoie l'identifiant de la tâche."""
    req = urllib.request.Request(
        "https://api.wavespeed.ai/api/v3/" + MODELE,
        data=json.dumps({"prompt": prompt, "aspect_ratio": "1:1", "resolution": "2k"}).encode(),
        headers={"Authorization": "Bearer " + cle, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["data"]["id"]


def attends(cle, ident, patience=180):
    """Relit la tâche jusqu'à ce qu'elle aboutisse. Renvoie l'URL de l'image."""
    t0 = time.time()
    while time.time() - t0 < patience:
        req = urllib.request.Request(
            "https://api.wavespeed.ai/api/v3/predictions/%s/result" % ident,
            headers={"Authorization": "Bearer " + cle},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)["data"]
        if d["status"] == "completed":
            return d["outputs"][0]
        if d["status"] == "failed":
            raise RuntimeError(d.get("error") or "rendu échoué")
        time.sleep(3)
    raise TimeoutError("rendu trop long : " + ident)


def pose(url, cle_fichier):
    """Télécharge, recadre en carré 900, écrit le webp aux DEUX endroits.

    ⚠️ Les images vivent en double : `assets/images/` (le site historique) et
    `experience/public/carte/` (l'application servie). Écrire une seule des
    deux laisse une carte à moitié illustrée sans que rien ne le signale.
    """
    with urllib.request.urlopen(url, timeout=120) as r:
        im = Image.open(io.BytesIO(r.read())).convert("RGB")
    c = min(im.size)
    g = (im.width - c) // 2
    h = (im.height - c) // 2
    im = im.crop((g, h, g + c, h + c)).resize((COTE, COTE), Image.LANCZOS)
    ecrits = []
    for dossier in (IMAGES, PUBLIC):
        os.makedirs(dossier, exist_ok=True)
        chemin = os.path.join(dossier, cle_fichier + ".webp")
        im.save(chemin, "WEBP", quality=QUALITE, method=6)
        ecrits.append(chemin)
    return ecrits, os.path.getsize(ecrits[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="regénère même ce qui existe")
    ap.add_argument("--seul", help="ne traite qu'une clé")
    args = ap.parse_args()

    cle = cle_api()
    faits, sautes = [], []
    for p in PLATS:
        if args.seul and p["cle"] != args.seul:
            continue
        dst = os.path.join(PUBLIC, p["cle"] + ".webp")
        if os.path.exists(dst) and not args.force:
            sautes.append(p["cle"])
            continue
        prompt = SOCLE.format(sujet=p["sujet"], support=p["support"])
        print("  … %-22s %s" % (p["cle"], p["nom"]))
        url = attends(cle, poste(cle, prompt))
        _, poids = pose(url, p["cle"])
        print("     %s.webp  %d x %d  %d Ko" % (p["cle"], COTE, COTE, poids // 1024))
        faits.append(p["cle"])

    if sautes:
        print("  déjà là (--force pour refaire) : " + ", ".join(sautes))
    print("  %d image(s) posée(s)" % len(faits))


if __name__ == "__main__":
    main()

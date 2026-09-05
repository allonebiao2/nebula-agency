# -*- coding: utf-8 -*-
"""
LES IMAGES D'AMBIANCE DE LA CLINIQUE — 7 bandes de matière et de lumière.

    python _outils/_gen_ambiances.py            # ne genere que ce qui manque
    python _outils/_gen_ambiances.py --force    # tout regenerer
    python _outils/_gen_ambiances.py --seul heros

⛔ CE QUE CE SCRIPT N'EST PAS, ET NE SERA JAMAIS.
   Le cerveau NEBULA interdit qu'une image generee serve de catalogue a un
   client. Ici, AUCUNE image ne montre :
     . un visage, une peau, un cheveu, une main  -> ce serait un faux resultat
     . un interieur d'institut, une cabine, un lit de soin  -> ce serait faire
       passer un decor invente pour la clinique de Gloria
     . un produit, un flacon de marque, une etiquette
   Ce sont des MATIERES et de la LUMIERE : eau, huile, cristaux, soie, marbre,
   brume. C'est ce que le standard du 2026-08-01 autorise explicitement
   (« ambiance, matiere, texture, arriere-plan, editorial »).

LA PHRASE DONT TOUT SORT :
   « Une clinique esthetique, c'est LA LUMIERE QU'ON APPROCHE D'UNE PEAU :
     d'abord pour la lire, ensuite pour la reveler. »
   D'ou le socle commun : une lumiere rasante, douce, qui vient de la gauche,
   et une matiere qui la retient.

LE SOCLE EST UN SOCLE, PAS SEPT PROMPTS : meme lumiere, meme optique, meme
palette (creme nacre, or #C9A84C, menthe pale, encre). Une seule phrase change.
C'est ce qui fait une serie au lieu d'une collection.
"""
import argparse, io, json, os, re, sys, time, urllib.request
from PIL import Image

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(RACINE, "assets", "images", "clinic")
SECRET = os.path.join(RACINE, "..", "..", "secrets", "wavespeed.env")

MODELE = "google/nano-banana-pro/text-to-image"

SOCLE = (
    "Luxury beauty editorial still life, abstract material study. {sujet}. "
    "Soft directional light raking from the upper left at a low angle, luminous and clean, "
    "warm highlights with pale mint-green cool shadows, palette of pearl cream, ivory, "
    "antique gold and deep ink brown. Shot on a 100mm macro lens at f/4, shallow depth of "
    "field, generous negative space, calm and expensive, no clutter. "
    "No people, no face, no skin, no hair, no hands, no body part, no product, no bottle, "
    "no jar, no packaging, no room, no furniture, no text, no lettering, no signature, "
    "no watermark, no logo, no branding."
)

IMAGES = [
    dict(cle="heros", ratio="16:9", largeur=1800, q=74,
         nom="Heros — la lumiere qu'on approche",
         sujet=("A single wide beam of golden light crossing a fine luminous mist above a polished "
                "cream marble surface, tiny suspended water droplets catching the light, faint "
                "gold veining in the stone, everything very pale and airy")),
    dict(cle="visage", ratio="16:9", largeur=1600, q=76,
         nom="Visage — la goutte de serum",
         sujet=("Extreme macro of large translucent serum droplets resting on a satin cream surface, "
                "each drop acting as a tiny lens with a golden highlight inside, a slow viscous "
                "trail of clear oil running between them")),
    dict(cle="corps", ratio="16:9", largeur=1600, q=76,
         nom="Corps — le gommage",
         sujet=("Extreme macro of fine sugar and mineral salt crystals scattered on pale cream stone, "
                "a thread of warm golden oil pouring across them and pooling, crystals sparkling "
                "where the light grazes")),
    dict(cle="capillaires", ratio="16:9", largeur=1600, q=76,
         nom="Capillaires — la fibre",
         sujet=("Extreme macro of long glossy silk fibres flowing in parallel waves across the frame, "
                "deep espresso brown and black silk with golden rim light along each strand, "
                "soft focus at both ends")),
    dict(cle="vip", ratio="16:9", largeur=1600, q=76,
         nom="VIP — la soie",
         sujet=("Folds of heavy champagne-gold silk draped in soft diagonal waves, deep velvety "
                "shadows in the folds, a warm glow sliding along one crest, very rich and quiet")),
    dict(cle="rdv", ratio="16:9", largeur=1600, q=72,
         nom="Rendez-vous — le marbre",
         sujet=("A very pale cream marble slab seen flat from above, delicate gold and pale mint "
                "veining, almost abstract, softly lit, minimal and serene, wide empty areas")),
    dict(cle="final", ratio="16:9", largeur=1600, q=76,
         nom="Final — le halo",
         sujet=("A warm golden halo of light blooming inside deep dark ink-brown haze, gentle "
                "concentric glow fading into darkness, a few floating dust motes catching the light, "
                "very dark image overall")),
]


def cle_api():
    with io.open(SECRET, encoding="utf-8") as f:
        m = re.search(r"^WAVESPEED_API_KEY=(.+)$", f.read(), re.M)
    if not m:
        sys.exit("cle WaveSpeed introuvable dans " + SECRET)
    return m.group(1).strip()


def poste(cle, prompt, ratio):
    req = urllib.request.Request(
        "https://api.wavespeed.ai/api/v3/" + MODELE,
        data=json.dumps({"prompt": prompt, "aspect_ratio": ratio, "resolution": "2k"}).encode(),
        headers={"Authorization": "Bearer " + cle, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["data"]["id"]


def attends(cle, ident, patience=240):
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
            raise RuntimeError(d.get("error") or "rendu echoue")
        time.sleep(3)
    raise TimeoutError("rendu trop long : " + ident)


def pose(url, spec):
    with urllib.request.urlopen(url, timeout=180) as r:
        im = Image.open(io.BytesIO(r.read())).convert("RGB")
    L = spec["largeur"]
    H = int(round(im.height * L / im.width))
    im = im.resize((L, H), Image.LANCZOS)
    os.makedirs(DEST, exist_ok=True)
    p = os.path.join(DEST, spec["cle"] + ".webp")
    im.save(p, "WEBP", quality=spec["q"], method=6)
    return p, im.size, os.path.getsize(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--seul")
    a = ap.parse_args()
    cle = cle_api()
    faits = 0
    for spec in IMAGES:
        if a.seul and spec["cle"] != a.seul:
            continue
        p = os.path.join(DEST, spec["cle"] + ".webp")
        if os.path.exists(p) and not a.force:
            print("  deja la : %s" % spec["cle"])
            continue
        print("  ... %-12s %s" % (spec["cle"], spec["nom"]))
        sys.stdout.flush()
        url = attends(cle, poste(cle, SOCLE.format(sujet=spec["sujet"]), spec["ratio"]))
        _, taille, poids = pose(url, spec)
        print("      %s.webp  %dx%d  %d Ko" % (spec["cle"], taille[0], taille[1], poids // 1024))
        sys.stdout.flush()
        faits += 1
    print("  %d image(s) posee(s)  (~%.2f $)" % (faits, faits * 0.14))


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
LES AMBIANCES DES TROIS UNIVERS — hub, INA Luxury, Cozy.

    python _outils/_gen_univers.py            # ne genere que ce qui manque
    python _outils/_gen_univers.py --force
    python _outils/_gen_univers.py --seul hub-heros

⛔ MEME REGLE QUE POUR LA CLINIQUE : aucune de ces images ne montre un visage,
   une peau, un cheveu, une main, un produit, un flacon ni un interieur. Ce
   sont des MATIERES et de la LUMIERE. Les vraies photos des produits de
   Gloria sont deja dans `assets/images/ina-luxury/` et `assets/images/cozy/` :
   ces ambiances les entourent, elles ne les remplacent jamais.

TROIS PALETTES, TROIS MONDES — c'est la demande de Mongazi (2026-09-05) :
   . hub LUXURY CLUB 229  : noir profond + or, la maison
   . INA Luxury           : noir + or, le laboratoire
   . Cozy                 : rose poudre + creme + or, l'intime
Le socle (lumiere rasante, optique, cadrage) reste celui de la clinique :
c'est ce qui fait que les quatre pages ont l'air photographiees le meme jour.
"""
import argparse, io, json, os, re, sys, time, urllib.request
from PIL import Image

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(RACINE, "assets", "images", "ambiances")
SECRET = os.path.join(RACINE, "..", "..", "secrets", "wavespeed.env")
MODELE = "google/nano-banana-pro/text-to-image"

SOCLE = (
    "Luxury beauty editorial still life, abstract material study. {sujet}. "
    "Soft directional light raking from the upper left at a low angle, "
    "{palette}. Shot on a 100mm macro lens at f/4, shallow depth of field, "
    "generous negative space, calm and expensive, no clutter. "
    "No people, no face, no skin, no hair, no hands, no body part, no product, no bottle, "
    "no jar, no packaging, no room, no furniture, no text, no lettering, no signature, "
    "no watermark, no logo, no branding."
)

NUIT = ("deep black and espresso background with antique gold highlights, very dark and rich, "
        "light falling on a small part of the frame only")
ROSE = ("powder rose, blush pink, warm cream and soft gold palette, luminous and airy, "
        "very soft shadows")

IMAGES = [
    # --- le hub : la maison ------------------------------------------------
    dict(cle="hub-heros", palette=NUIT, largeur=1800, q=74,
         nom="Hub — la maison",
         sujet=("A wide shaft of warm golden light crossing deep black space, fine gold dust "
                "suspended in it, a polished black stone surface catching a thin gold reflection")),
    dict(cle="hub-ina", palette=NUIT, largeur=1200, q=76,
         nom="Hub — INA Luxury",
         sujet=("Extreme macro of a thick golden serum drop suspended on black glass, "
                "one bright specular highlight inside the drop, everything else in darkness")),
    dict(cle="hub-clinic", palette=("pearl cream, ivory and antique gold palette, luminous, "
                                    "clinical yet warm, pale mint-green cool shadows"),
         largeur=1200, q=76,
         nom="Hub — Luxury Skin Clinic",
         sujet=("A beam of clean light crossing a fine mist above pale cream marble, "
                "tiny water droplets sparkling in the beam")),
    dict(cle="hub-cozy", palette=ROSE, largeur=1200, q=76,
         nom="Hub — Cozy",
         sujet=("Folds of powder-rose silk with a single small pearl resting in a fold, "
                "very soft light, blush and cream tones")),

    # --- INA Luxury : le laboratoire ---------------------------------------
    dict(cle="ina-heros", palette=NUIT, largeur=1800, q=74,
         nom="INA Luxury — le heros",
         sujet=("A slow thread of golden oil pouring through darkness and coiling on black glass, "
                "gold rim light along the stream, deep black background")),
    dict(cle="ina-visage", palette=NUIT, largeur=1400, q=76,
         nom="INA Luxury — visage",
         sujet=("Extreme macro of clear serum droplets on a black satin surface, "
                "each drop lit from behind with a warm gold edge")),
    dict(cle="ina-corps", palette=NUIT, largeur=1400, q=76,
         nom="INA Luxury — corps",
         sujet=("Coarse mineral salt and raw shea butter shavings on black slate, "
                "a ribbon of golden oil running between them")),
    dict(cle="ina-capillaires", palette=NUIT, largeur=1400, q=76,
         nom="INA Luxury — capillaires",
         sujet=("Long glossy black silk fibres flowing in parallel waves through darkness, "
                "thin gold rim light along a few strands")),
    dict(cle="ina-enfant", palette=("warm cream, soft honey and pale gold palette, gentle and "
                                    "luminous, very soft shadows"),
         largeur=1400, q=76,
         nom="INA Luxury — enfant",
         sujet=("A soft swirl of pale milky cream with a single gentle bubble, warm honey tones, "
                "extremely soft and calm")),

    dict(cle="ina-levres", palette=NUIT, largeur=1400, q=76,
         nom="INA Luxury — soin levres",
         sujet=("Extreme macro of a glossy amber balm swirl on black glass, a thick clear "
                "gloss ribbon catching one bright golden highlight")),

    # --- Cozy : l'intime ---------------------------------------------------
    dict(cle="cozy-heros", palette=ROSE, largeur=1800, q=74,
         nom="Cozy — le heros",
         sujet=("Folds of powder-rose silk lit softly from the left, gentle diagonal waves, "
                "a faint golden glow sliding along one crest")),
    dict(cle="cozy-intime", palette=ROSE, largeur=1400, q=76,
         nom="Cozy — hygiene intime",
         sujet=("Clear water drops on a blush satin surface, a few tiny rose petals out of focus "
                "in the background, extremely soft and clean")),
    dict(cle="cozy-selfcare", palette=ROSE, largeur=1400, q=76,
         nom="Cozy — selfcare",
         sujet=("A soft swirl of pale rose cream with a delicate golden shimmer running through it, "
                "creamy texture, very soft light")),
    dict(cle="cozy-fermete", palette=ROSE, largeur=1400, q=76,
         nom="Cozy — fermete",
         sujet=("Smooth blush stone spheres resting on rose silk, warm gold reflections on their "
                "curves, quiet and sculptural")),
]


def cle_api():
    with io.open(SECRET, encoding="utf-8") as f:
        m = re.search(r"^WAVESPEED_API_KEY=(.+)$", f.read(), re.M)
    if not m:
        sys.exit("cle WaveSpeed introuvable dans " + SECRET)
    return m.group(1).strip()


def poste(cle, prompt):
    req = urllib.request.Request(
        "https://api.wavespeed.ai/api/v3/" + MODELE,
        data=json.dumps({"prompt": prompt, "aspect_ratio": "16:9", "resolution": "2k"}).encode(),
        headers={"Authorization": "Bearer " + cle, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["data"]["id"]


def attends(cle, ident, patience=240):
    t0 = time.time()
    while time.time() - t0 < patience:
        req = urllib.request.Request(
            "https://api.wavespeed.ai/api/v3/predictions/%s/result" % ident,
            headers={"Authorization": "Bearer " + cle})
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
    im = im.resize((L, int(round(im.height * L / im.width))), Image.LANCZOS)
    os.makedirs(DEST, exist_ok=True)
    p = os.path.join(DEST, spec["cle"] + ".webp")
    im.save(p, "WEBP", quality=spec["q"], method=6)
    return im.size, os.path.getsize(p)


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
        print("  ... %-16s %s" % (spec["cle"], spec["nom"]))
        sys.stdout.flush()
        url = attends(cle, poste(cle, SOCLE.format(sujet=spec["sujet"], palette=spec["palette"])))
        taille, poids = pose(url, spec)
        print("      %s.webp  %dx%d  %d Ko" % (spec["cle"], taille[0], taille[1], poids // 1024))
        sys.stdout.flush()
        faits += 1
    print("  %d image(s) posee(s)  (~%.2f $)" % (faits, faits * 0.14))


if __name__ == "__main__":
    main()

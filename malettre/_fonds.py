# -*- coding: utf-8 -*-
"""MA LETTRE À… · les fonds d'ambiance : des images de Mongazi aux WebP du site.

    python malettre/_fonds.py
    python malettre/_build_accueil.py      # la page ne nomme que les images présentes

Lit `_partage/ma lettre/fonds/<zone>-paysage.*` et `<zone>-portrait.*` (jpg, png
ou webp) et écrit `malettre/fonds/<zone>-l.webp` (ordinateur, 1920 px de large au
plus) et `<zone>-p.webp` (téléphone, 1080 × 1920 au plus), en VISANT UN POIDS et
non une qualité : la 3G de Cotonou paie chaque octet. Le héros, au premier
écran, a le plafond le plus bas.

S'il manque une des deux formes, elle est découpée au centre de l'autre (et on le
dit) : mieux vaut un cadrage moins juste qu'une zone sans fond au téléphone.

⛔ Ce sont des AMBIANCES (règle NEBULA) : jamais présentées comme une vraie
lettre, un vrai client, ni le produit lui-même. Aucun visage.
"""
import pathlib
import sys
from io import BytesIO

from PIL import Image, ImageOps

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ICI = pathlib.Path(__file__).resolve().parent
SOURCE = ICI.parent / "_partage" / "ma lettre" / "fonds"
SORTIE = ICI / "fonds"
# ⚠️ La même liste que FONDS dans `_build_accueil.py` : une zone ici et pas là
# ne serait jamais affichée.
ZONES = ["heros", "plume", "nuit", "faire-part", "seuil", "promesses", "fin"]
FORMES = {"l": ("paysage", (1920, 1200), 16 / 9), "p": ("portrait", (1080, 1920), 9 / 16)}
PLAFOND = {"l": 190_000, "p": 140_000}
PLAFOND_HEROS = {"l": 120_000, "p": 85_000}
# Où découper quand une forme manque (0 = bord gauche, 1 = bord droit) : la plume
# a sa main et son bec à droite, une découpe au centre les coupait.
ANCRE = {"plume": .8}
# Retourné gauche-droite : le faire-part pose ses alliances CÔTÉ CARTON, et la
# nuit du bloc garde le côté du texte (image sans aucune écriture : rien ne se lit à l'envers).
MIROIR = {"faire-part"}


def trouver(zone, nom):
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        for p in (SOURCE / ("%s-%s%s" % (zone, nom, ext)), SOURCE / ("%s-%s%s" % (zone, nom, ext.upper()))):
            if p.exists():
                return p
    return None


def recadrer(im, ratio, ancre=.5):
    """Le plus grand rectangle du ratio voulu, centré sur l'ancre horizontale."""
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio)
        x = min(max(int(w * ancre - nw / 2), 0), w - nw)
        return im.crop((x, 0, x + nw, h))
    nh = int(w / ratio)
    return im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))


def viser(im, plafond):
    """La meilleure qualité WebP qui tient sous le plafond (recherche par moitiés)."""
    bas, haut, mieux = 25, 90, None
    while bas <= haut:
        q = (bas + haut) // 2
        tampon = BytesIO()
        im.save(tampon, "WEBP", quality=q, method=6)
        if tampon.tell() <= plafond:
            mieux, bas = (q, tampon.getvalue()), q + 1
        else:
            haut = q - 1
    if mieux is None:
        tampon = BytesIO()
        im.save(tampon, "WEBP", quality=25, method=6)
        mieux = (25, tampon.getvalue())
    return mieux


def main():
    if not SOURCE.is_dir():
        sys.exit("⛔ dossier absent : %s" % SOURCE)
    SORTIE.mkdir(exist_ok=True)
    faits = 0
    for zone in ZONES:
        sources = {f: trouver(zone, FORMES[f][0]) for f in FORMES}
        if not any(sources.values()):
            continue
        for f, (nom, boite, ratio) in FORMES.items():
            src = sources[f] or sources["p" if f == "l" else "l"]
            im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
            if not sources[f]:
                print("  ⚠️ %s : pas de « %s », découpé dans « %s » (à %d %% de la largeur)"
                      % (zone, nom, src.stem, round(ANCRE.get(zone, .5) * 100)))
            im = recadrer(im, ratio, ANCRE.get(zone, .5) if not sources[f] else .5)
            if zone in MIROIR:
                im = ImageOps.mirror(im)
            im.thumbnail(boite, Image.LANCZOS)
            plafond = (PLAFOND_HEROS if zone == "heros" else PLAFOND)[f]
            q, octets = viser(im, plafond)
            sortie = SORTIE / ("%s-%s.webp" % (zone, f))
            sortie.write_bytes(octets)
            faits += 1
            print("  %-26s %4d × %-4d  qualité %2d  %5.0f Ko" % (sortie.relative_to(ICI), im.width, im.height, q, len(octets) / 1024))
    print("%d image(s) écrite(s). Ensuite : python malettre/_build_accueil.py" % faits)


if __name__ == "__main__":
    main()

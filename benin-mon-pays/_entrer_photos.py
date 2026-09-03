# -*- coding: utf-8 -*-
"""L'entrée des photos envoyées par Mongazi.

Ce que ce script fait, et pourquoi chaque contrôle existe :

  · **Il dit si la photo est en portrait.** Le site est un plein écran
    vertical. 90 % des photos de tourisme sont en paysage et se recadrent mal.
  · **Il dit si le fichier est passé par WhatsApp.** WhatsApp divise le poids
    par dix et ça se voit en grand. Une photo de 1 600 px et 90 Ko est une
    copie compressée, pas l'originale : il faut redemander le fichier.
  · **Il lit les coordonnées GPS quand elles sont là.** Le site place tout à
    sa latitude réelle : une photo géolocalisée se pose toute seule sur la
    route, et le kilomètre se calcule au lieu de se deviner.
  · **Il ne convertit rien tant qu'on ne le lui demande pas.** On regarde
    d'abord, on garde ensuite.

    python _entrer_photos.py                     # regarde _partage/
    python _entrer_photos.py <dossier>           # regarde ailleurs
    python _entrer_photos.py <dossier> --garder  # convertit les retenues

⚠️ Ce script ne juge PAS le contenu. Une personne reconnaissable sans accord
écrit, et un enfant dans tous les cas, se refusent à l'œil, pas au calcul.
"""
import io
import os
import sys

from PIL import Image, ImageOps

ICI = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.abspath(os.path.join(ICI, ".."))
PARTAGE = os.path.join(DEPOT, "_partage")
RECUES = os.path.join(ICI, "_sources", "recues")

EXT = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif")

# L'échelle du voyage, la même que le site : la latitude convertie en km
# depuis la côte. 700 km du sud au nord, 6,21 °N à la Porte.
LAT0, LAT1, KM1 = 6.354, 12.384, 700.0


def km_depuis_lat(lat):
    return max(0, round((lat - LAT0) / (LAT1 - LAT0) * KM1))


def gps(im):
    """Renvoie (lat, lon) si la photo les porte, sinon None."""
    try:
        ex = im.getexif()
        ifd = ex.get_ifd(0x8825)  # GPSInfo
        if not ifd:
            return None

        def deg(v, ref):
            d = float(v[0]) + float(v[1]) / 60 + float(v[2]) / 3600
            return -d if ref in ("S", "W") else d

        return (deg(ifd[2], ifd[1]), deg(ifd[4], ifd[3]))
    except Exception:
        return None


def regarder(chemin):
    im = Image.open(chemin)
    im = ImageOps.exif_transpose(im)
    l, h = im.size
    poids = os.path.getsize(chemin)
    portrait = h > l
    # densité : une photo d'origine tient autour de 1 octet par pixel en JPEG
    # de qualité. Sous 0,20, elle a été recompressée par une messagerie.
    dens = poids / float(l * h)
    pos = gps(Image.open(chemin))

    verdict, pourquoi = "GARDER", []
    if not portrait:
        verdict = "A RECADRER"
        pourquoi.append("en paysage (le site est vertical)")
    if max(l, h) < 2000:
        verdict = "REDEMANDER"
        pourquoi.append("%d px sur le grand côté, il en faut 2000" % max(l, h))
    if dens < 0.20:
        verdict = "REDEMANDER"
        pourquoi.append("%.2f octet/pixel : passée par une messagerie" % dens)
    return {
        "nom": os.path.basename(chemin), "chemin": chemin,
        "l": l, "h": h, "poids": poids, "portrait": portrait,
        "dens": dens, "gps": pos, "verdict": verdict,
        "pourquoi": " · ".join(pourquoi),
    }


def garder(f, dossier=RECUES):
    """Range la photo au format du site : une grande WebP + sa miniature."""
    os.makedirs(dossier, exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(f["chemin"])).convert("RGB")
    base = os.path.splitext(f["nom"])[0].lower().replace(" ", "-")
    g = im.copy()
    g.thumbnail((1400, 2200), Image.LANCZOS)
    pg = os.path.join(dossier, base + ".webp")
    g.save(pg, "WEBP", quality=82, method=6)
    p = im.copy()
    p.thumbnail((24, 38), Image.LANCZOS)
    pp = os.path.join(dossier, base + "-min.webp")
    p.save(pp, "WEBP", quality=45, method=6)
    return pg, os.path.getsize(pg), os.path.getsize(pp)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dossier = args[0] if args else PARTAGE
    on_garde = "--garder" in sys.argv

    if not os.path.isdir(dossier):
        print("Dossier introuvable :", dossier)
        return 1
    fichiers = sorted(os.path.join(dossier, n) for n in os.listdir(dossier)
                      if n.lower().endswith(EXT))
    if not fichiers:
        print("Aucune image dans", dossier)
        return 0

    print("%d image(s) dans %s\n" % (len(fichiers), dossier))
    print("  %-34s %-11s %-8s %-9s %s"
          % ("FICHIER", "TAILLE", "POIDS", "VERDICT", "POURQUOI / GPS"))
    print("  " + "-" * 96)
    gardees = []
    for c in fichiers:
        try:
            f = regarder(c)
        except Exception as e:
            print("  %-34s  illisible (%s)" % (os.path.basename(c),
                                               type(e).__name__))
            continue
        note = f["pourquoi"]
        if f["gps"]:
            lat, lon = f["gps"]
            note = (note + " · " if note else "") + \
                "GPS %.4f, %.4f → km %d" % (lat, lon, km_depuis_lat(lat))
        print("  %-34s %-11s %-8s %-9s %s"
              % (f["nom"][:34], "%dx%d" % (f["l"], f["h"]),
                 "%.1f Mo" % (f["poids"] / 1e6), f["verdict"], note))
        if f["verdict"] != "REDEMANDER":
            gardees.append(f)

    if on_garde:
        print("\nRangées dans _sources/recues/ :")
        for f in gardees:
            p, pg, pp = garder(f)
            print("  %-34s %6.0f Ko + %3.0f Ko (miniature)"
                  % (os.path.basename(p), pg / 1024.0, pp / 1024.0))
    else:
        print("\n%d retenue(s). Ajouter --garder pour les convertir."
              % len(gardees))
    return 0


if __name__ == "__main__":
    sys.exit(main())

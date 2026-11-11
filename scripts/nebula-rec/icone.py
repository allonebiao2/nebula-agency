# -*- coding: utf-8 -*-
"""L'icône de NEBULA REC, dessinée en Python pur (aucun fichier image dans le dépôt, aucune bibliothèque).

Un carré d'encre aux coins arrondis, un point rouge d'enregistrement cerclé d'un anneau clair.
"""

import math
import struct

ENCRE = (0x14, 0x14, 0x18)
ROUGE = (0xFF, 0x3B, 0x3B)
ANNEAU = (0xF2, 0xEF, 0xE8)


def _couvert(d, bord):
    """Couverture anticrénelée d'un pixel à la distance signée d (négative = dedans)."""
    return max(0.0, min(1.0, 0.5 - d / bord))


def _pixel(x, y, n):
    c = (n - 1) / 2.0
    bord = max(1.0, n / 64.0)
    # Carré arrondi (rayon 22 %)
    r = 0.22 * n
    qx, qy = max(abs(x - c) - (c - r), 0.0), max(abs(y - c) - (c - r), 0.0)
    fond = _couvert(math.hypot(qx, qy) - r, bord)
    dist = math.hypot(x - c, y - c)
    anneau = _couvert(abs(dist - 0.33 * n) - 0.035 * n, bord)
    point = _couvert(dist - 0.22 * n, bord)
    rgb = list(ENCRE)
    for couleur, a in ((ANNEAU, anneau), (ROUGE, point)):
        rgb = [round(rgb[k] * (1 - a) + couleur[k] * a) for k in range(3)]
    return rgb[0], rgb[1], rgb[2], round(255 * fond)


def _image(n):
    """Une image d'icône (BITMAPINFOHEADER + pixels BGRA de bas en haut + masque ET)."""
    lignes = []
    for y in range(n - 1, -1, -1):
        ligne = bytearray()
        for x in range(n):
            r, g, b, a = _pixel(x, y, n)
            ligne += bytes((b, g, r, a))
        lignes.append(bytes(ligne))
    masque_ligne = ((n + 31) // 32) * 4
    entete = struct.pack("<IiiHHIIiiII", 40, n, n * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    return entete + b"".join(lignes) + b"\x00" * (masque_ligne * n)


def fabriquer_icone(chemin, tailles=(16, 24, 32, 48, 64, 256)):
    images = [_image(n) for n in tailles]
    tete = struct.pack("<HHH", 0, 1, len(images))
    decalage = 6 + 16 * len(images)
    entrees = b""
    for n, img in zip(tailles, images):
        entrees += struct.pack("<BBBBHHII", n % 256, n % 256, 0, 0, 1, 32, len(img), decalage)
        decalage += len(img)
    with open(chemin, "wb") as f:
        f.write(tete + entrees + b"".join(images))
    return chemin


if __name__ == "__main__":
    import sys
    print(fabriquer_icone(sys.argv[1] if len(sys.argv) > 1 else "nebula-rec.ico"))

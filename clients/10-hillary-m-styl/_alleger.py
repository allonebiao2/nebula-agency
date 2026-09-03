#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HILLARY M. STYL — allège les images sans toucher au détourage.

    python _alleger.py            regarde et propose
    python _alleger.py --ecrire   applique

POURQUOI CE SCRIPT EXISTE
Mesuré le 2026-08-06 sur une 4G d'Afrique de l'Ouest (1,6 Mb/s, processeur
quatre fois plus lent) : **la première pièce du héros n'apparaissait qu'à
9,3 secondes**. Entre la disparition du rideau d'ouverture (2,9 s) et cette
neuvième seconde, le visiteur voyait une page avec un chiffre géant, des
textes, et AUCUN vêtement. Ça ne ressemble pas à un site qui charge : ça
ressemble à un site cassé. C'est ce que Mongazi a vu sur son téléphone.

CE QUI EST FAIT ICI
Le canal alpha reste **sans perte** (`alpha_quality=100`, `exact=True`) : c'est
lui qui porte le détourage, et une seule dent dedans fait un halo blanc autour
de la silhouette. Seul le RVB est compressé davantage.

Mesuré sur les huit découpes : à **qualité 84**, l'écart alpha est de **0**
(bit pour bit) et l'écart RVB moyen de 3 sur 255, invisible sur une photo,
pour **moitié moins d'octets**.

⛔ Ne PAS baisser `alpha_quality`. ⛔ Ne pas relancer `_pose_images.py` après
   coup sur les découpes : il ne les connaît pas, mais il régénère l'atelier
   et le lookbook, eux, à sa propre qualité.
"""
import io, os, sys, glob, pathlib

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from PIL import Image
import numpy as np

ICI = pathlib.Path(__file__).resolve().parent
IMG = ICI / "assets" / "images"
ECRIRE = "--ecrire" in sys.argv

# (motif, qualité, largeur maximale)
LOTS = [
    # les découpes : alpha sans perte, RVB à 84
    ("hero-*.webp", 84, None),
    ("piece-*.webp", 84, None),
    # l'ambiance : personne ne la regarde à la loupe
    ("atelier-*.webp", 74, 800),
    ("look-*.webp", 74, 900),
    # le logo part en base64 DANS le HTML : chaque octet y compte 1,33 fois
    ("logo.webp", 84, 400),
]


def traiter(f, q, larg):
    im = Image.open(f)
    rgba = im.mode == "RGBA" or "transparency" in im.info
    im = im.convert("RGBA" if rgba else "RGB")
    a0 = np.asarray(im.getchannel("A"), dtype=np.int16) if rgba else None
    if larg and im.width > larg:
        im = im.resize((larg, round(im.height * larg / im.width)), Image.LANCZOS)
        a0 = None                      # redimensionné : la comparaison n'a plus de sens
    b = io.BytesIO()
    opts = dict(quality=q, method=6)
    if rgba:
        opts.update(alpha_quality=100, exact=True)
    im.save(b, "WEBP", **opts)
    ecart = None
    if a0 is not None:
        a1 = np.asarray(Image.open(io.BytesIO(b.getvalue())).convert("RGBA")
                        .getchannel("A"), dtype=np.int16)
        ecart = int(np.abs(a0 - a1).max())
    return b.getvalue(), ecart


def main():
    if not IMG.exists():
        print("aucun dossier d'images"); return 1
    print("HILLARY M. STYL — allègement des images"
          + ("" if ECRIRE else "   (essai — ajouter --ecrire pour appliquer)") + "\n")
    av = ap = 0
    for motif, q, larg in LOTS:
        for f in sorted(IMG.glob(motif)):
            k0 = f.stat().st_size
            data, ecart = traiter(f, q, larg)
            k1 = len(data)
            av += k0; ap += k1
            if ecart is not None and ecart > 0:
                print(f"  [KO] {f.name} : l'alpha bougerait de {ecart} — on ne touche pas")
                ap += k0 - k1
                continue
            gain = 100 * (k0 - k1) / k0 if k0 else 0
            marque = "alpha intact" if ecart == 0 else ""
            print(f"  {f.name:<22} {k0//1024:>4} -> {k1//1024:>4} Ko  ({gain:+5.1f} %)  {marque}")
            if ECRIRE and k1 < k0:
                f.write_bytes(data)
            elif ECRIRE:
                ap += k0 - k1          # on garde l'original s'il est déjà plus léger
    print(f"\n  {av//1024} Ko  ->  {ap//1024} Ko   ({100*(av-ap)/av:.0f} % de moins)")
    if not ECRIRE:
        print("\n  rien n'a été écrit. Relancer avec --ecrire.")
    else:
        print("\n  écrit. Enchaîner : python _build.py && python _qc.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())

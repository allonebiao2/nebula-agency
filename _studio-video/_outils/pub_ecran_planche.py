# -*- coding: utf-8 -*-
"""La planche de la pub écran NEBULA : une image fixe par plan, dans les deux formats, aux instants lus dans
`src/pub-ecran-nebula/minutage.json` (jamais une seconde écrite à la main). À REGARDER avant tout rendu.

    python _outils/pub_ecran_planche.py            les deux formats
    python _outils/pub_ecran_planche.py 169        le 16:9 seulement
    python _outils/pub_ecran_planche.py tiktok     le 9:16 seulement

Écrit `out/planches/pub-ecran-nebula-169.jpg` et `out/planches/pub-ecran-nebula-tiktok.jpg`.
⚠️ Travail lourd (un navigateur) : un format après l'autre, jamais pendant un rendu.
"""
import json
import subprocess
import sys
import unicodedata
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ICI = Path(__file__).resolve().parent.parent
M = json.loads((ICI / "src/pub-ecran-nebula/minutage.json").read_text(encoding="utf-8"))


def normal(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def ligne(n):
    return M["lignes"][n - 1]


def quand(n, cle, occ=1):
    k = 0
    for w in ligne(n)["mots"]:
        if normal(w["m"]).startswith(normal(cle)):
            k += 1
            if k == occ:
                return w["a"]
    return ligne(n)["debut"]


INSTANTS = [
    ("début", 0.0),
    ("1 · la nuit", ligne(1)["fin"] - 0.05),
    ("2 · « clients » s'efface", ligne(2)["fin"] - 0.2),
    ("3 · le statut, 1 vue", quand(3, "voit") + 0.5),
    ("4 · « C'est combien ? »", quand(4, "combien") + 0.35),
    ("5 · ailleurs", ligne(5)["fin"] + 0.12),
    ("6 · Retiens bien ça", ligne(6)["fin"]),
    ("7 · la phrase-clé", quand(7, "tout", 1) + 0.35),
    ("7 · TOUT DE SUITE", ligne(7)["fin"]),
    ("8 · le vrai catalogue", ligne(8)["debut"] + 0.9),
    ("8 · on entre dans l'écran", ligne(8)["fin"] - 0.05),
    ("9 · les produits, les prix", quand(9, "prix") + 0.7),
    ("9 · un seul lien", ligne(9)["fin"] - 0.05),
    ("10 · il appuie", quand(10, "appuie") + 0.12),
    ("11 · la commande, déjà écrite", quand(11, "deja") + 0.1),
    ("12 · même à minuit", ligne(12)["fin"] - 0.15),
    ("13 · J-34", ligne(13)["fin"] - 0.15),
    ("14 · 48 h", quand(14, "heures")),
    ("15 · CATALOGUE", quand(15, "whatsapp") + 0.15),
    ("16 · le néon s'allume", quand(16, "nebula") + 0.05),
    ("16 · l'enseigne posée", ligne(16)["fin"] + 0.5),
]


def rendre(id_):
    secondes = [f"{s:.3f}" for _, s in INSTANTS]
    subprocess.run(["node", "_outils/planches.mjs", id_, *secondes], cwd=ICI, check=True)
    return [ICI / "out/planches" / id_ / f"{s.zfill(6)}.jpg" for s in secondes]


def assembler(id_, fichiers, colonnes, l, h, nom):
    police = ImageFont.truetype("arialbd.ttf", 22)
    lignes = (len(fichiers) + colonnes - 1) // colonnes
    marge = 6
    planche = Image.new("RGB", (colonnes * (l + marge) + marge, lignes * (h + marge + 34) + marge), (24, 24, 28))
    d = ImageDraw.Draw(planche)
    for k, (f, (titre, s)) in enumerate(zip(fichiers, INSTANTS)):
        im = Image.open(f).convert("RGB").resize((l, h), Image.LANCZOS)
        x = marge + (k % colonnes) * (l + marge)
        y = marge + (k // colonnes) * (h + marge + 34)
        d.text((x + 2, y + 4), f"{s:5.2f} s  {titre}", fill=(255, 214, 90), font=police)
        planche.paste(im, (x, y + 32))
    sortie = ICI / "out/planches" / nom
    planche.save(sortie, quality=88)
    print("planche :", sortie)
    return sortie


if __name__ == "__main__":
    voulu = sys.argv[1:] or ["169", "tiktok"]
    if "169" in voulu:
        assembler("PubEcranNebula169", rendre("PubEcranNebula169"), 4, 480, 270, "pub-ecran-nebula-169.jpg")
    if "tiktok" in voulu:
        assembler("PubEcranNebulaTikTok", rendre("PubEcranNebulaTikTok"), 5, 288, 512, "pub-ecran-nebula-tiktok.jpg")

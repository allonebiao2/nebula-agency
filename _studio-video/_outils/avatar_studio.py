# -*- coding: utf-8 -*-
"""Le plan studio de l'avatar de Mongazi (TikTok NEBULA) : l'image Flow recadrée au BORD DE LA TABLE (rien en dessous),
le logo de l'ordinateur effacé, et le VRAI logo NEBULA AGENCY posé sur le mur comme une enseigne lumineuse.

    python _studio-video/_outils/avatar_studio.py [source.jpg] [sortie.jpg]

Pourquoi le logo n'est pas généré par l'IA : elle déforme les lettres et invente des marques. On pose les vraies pièces
(`public/nebula30/logo/` : marque.png, nebula.png, agency.png, fonds transparents).
Mongazi, 20/11 : « on ne voit pas en dessous de la table, la limite doit être la table, et il est marqué Nebula agency
avec le logo ». Les images de l'avatar vivent dans `_partage/avatar/` (exclu de GitHub)."""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageFilter

ICI = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(ICI, "..", "public", "nebula30", "logo")
AV = os.path.join(ICI, "..", "..", "_partage", "avatar")
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AV, "S3-cadre-table-2k.jpg")
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(AV, "STUDIO-NEBULA.jpg")

im = Image.open(src).convert("RGB")
W, H = im.size                                       # 1536 x 2752 (Flow, « 2K »)

# 1. effacer la pomme du capot de l'ordinateur (mesurée sur l'image 2K)
a = np.asarray(im).copy()
masque = np.zeros(a.shape[:2], np.uint8)
cv2.ellipse(masque, (785, 2236), (42, 14), 0, 0, 360, 255, -1)
a = cv2.inpaint(a, masque, 9, cv2.INPAINT_TELEA)
im = Image.fromarray(a)

# 2. recadrer : le bas de l'image = le bord avant de la table (y 2415 mesuré), en 9:16
bas = 2415
larg = round(bas * 9 / 16)
x0 = (W - larg) // 2
im = im.crop((x0, 0, x0 + larg, bas))
k = im.width / 1080

# 3. l'enseigne : le logo ENTIER recomposé à ses positions d'origine (couches.json). ⚠️ Le « A » d'AGENCY est rangé
#    dans trait-g.png (agency.png seul donne « GENCY ») : on pose toutes les couches, jamais une seule.
import json
C = json.load(open(os.path.join(LOGO, "couches.json"), encoding="utf-8"))
boite = C["logo"]
largeur = round(520 * k)                              # 520 px sur 1080 ; sous les onglets de TikTok (haut ~100 px)
echelle = largeur / boite["w"]
pos = ((im.width - largeur) // 2, round(84 * k))


def couche(noms):
    """Les pièces demandées, à leur place d'origine, mises à l'échelle et posées dans l'image (fond transparent)."""
    L = Image.new("RGBA", (boite["w"], boite["h"]), (0, 0, 0, 0))
    for nom in noms:
        c = C[nom]
        L.alpha_composite(Image.open(os.path.join(LOGO, c["fichier"])).convert("RGBA"), (c["x"] - boite["x"], c["y"] - boite["y"]))
    L = L.resize((largeur, round(boite["h"] * echelle)), Image.LANCZOS)
    out_ = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out_.alpha_composite(L, pos)
    return np.asarray(out_).astype(np.float32)


def flou(x, r):
    return np.asarray(Image.fromarray(np.clip(x, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32)


# 4. LES NÉONS (Mongazi, 20/11 : « Nebula doit être incrusté comme si c'était des lumières néon ») : le tube (un cœur
#    éclairci), puis des halos de plus en plus larges dans la couleur du logo, saturée, AJOUTÉS à la lumière du mur (un
#    néon éclaire, il ne recouvre pas), jusqu'à une lueur très large qui teinte le panneau.
#    Les lettres sont des tubes presque blancs ; la planète garde ses couleurs (blanchie, elle devenait pastel).
def neon(base, E, blanc, force):
    a = E[..., 3:4] / 255
    rgb = E[..., :3]
    gris = rgb.mean(-1, keepdims=True)
    lumiere = np.clip(gris + (rgb - gris) * 1.8, 0, 255) * a  # la couleur du gaz, plus franche que le logo imprimé
    for r, poids in ((3 * k, 0.9), (10 * k, 0.85), (26 * k, 0.7), (70 * k, 0.45), (160 * k, 0.25)):
        base += flou(lumiere, r) * poids * force
    coeur = np.clip(rgb * (1 - blanc) * 1.15 + 255 * blanc, 0, 255)
    return base * (1 - a) + np.maximum(base, coeur) * a


base = np.asarray(im).astype(np.float32)
base = neon(base, couche(["marque"]), blanc=0.18, force=0.65)
base = neon(base, couche(["nebula", "trait-g", "agency", "trait-d"]), blanc=0.62, force=1.0)
im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")

im = im.convert("RGB").resize((1080, 1920), Image.LANCZOS)
im.save(out, quality=94)
print("écrit :", out, im.size, f"(recadré {larg}x{bas} depuis {W}x{H})")

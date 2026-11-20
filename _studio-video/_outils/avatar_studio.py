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
logo = Image.new("RGBA", (boite["w"], boite["h"]), (0, 0, 0, 0))
for nom in ("marque", "nebula", "trait-g", "agency", "trait-d"):
    c = C[nom]
    logo.alpha_composite(Image.open(os.path.join(LOGO, c["fichier"])).convert("RGBA"), (c["x"] - boite["x"], c["y"] - boite["y"]))
largeur = round(520 * k)                              # 520 px sur 1080 ; sous les onglets de TikTok (haut ~100 px)
logo = logo.resize((largeur, round(logo.height * largeur / logo.width)), Image.LANCZOS)
enseigne = Image.new("RGBA", im.size, (0, 0, 0, 0))
enseigne.alpha_composite(logo, ((im.width - logo.width) // 2, round(84 * k)))

# halo : l'enseigne éclaire un peu le mur autour d'elle (lumière additive, douce)
halo = enseigne.filter(ImageFilter.GaussianBlur(28 * k))
base = np.asarray(im).astype(np.float32)
h = np.asarray(halo).astype(np.float32)
base += h[..., :3] * (h[..., 3:4] / 255) * 0.55
im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
ens = np.asarray(enseigne).astype(np.float32)
ens[..., 3] *= 0.92                                   # une enseigne au mur, pas un autocollant collé sur l'écran
im.alpha_composite(Image.fromarray(ens.astype(np.uint8)))

im = im.convert("RGB").resize((1080, 1920), Image.LANCZOS)
im.save(out, quality=94)
print("écrit :", out, im.size, f"(recadré {larg}x{bas} depuis {W}x{H})")

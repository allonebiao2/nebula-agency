#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANGY ART — pose les images choisies dans le site.

    python _pose_images.py

Prend les images retenues dans `_sources/ia/`, les met au format et au poids
du web, et les écrit dans `assets/images/`. Ré-exécutable.

Deux traitements :
  · les SCÈNES sont seulement redimensionnées (la lumière du site passera dessus)
  · les ŒUVRES reçoivent un fond unifié : Nano Banana rend des gris de fond qui
    vont du clair au foncé d'une image à l'autre, ce qui ferait un carrousel
    bariolé. Un assombrissement radial ramène tous les bords au même noir, sans
    toucher à l'œuvre au centre.

⚠️ Ces visuels sont une PRÉFIGURATION. Ils partent le jour où Angélique envoie
   les photos de ses vraies pièces. Aucun prix, aucune dimension, aucune mention
   « disponible » ne doit leur être associée.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RACINE = os.path.dirname(os.path.abspath(__file__))
IA = os.path.join(RACINE, "_sources", "ia")
IMG = os.path.join(RACINE, "assets", "images")

# ---- ce qui a été retenu, après les avoir regardées ---------------------
SCENES = [
    ("hero-2",       "scenes/hero.webp",       1100, 84),
    ("demarche-1",   "scenes/demarche.webp",   1400, 82),
    ("atelier-1",    "scenes/atelier.webp",    2000, 80),
    ("vernissage-1", "scenes/vernissage.webp", 1300, 82),
    ("soir-1",       "scenes/soir.webp",       2000, 80),
]
OEUVRES = [f"oeuvre-{i}" for i in range(1, 9)]
LARG_OEUVRE, Q_OEUVRE = 900, 82


def poids(p):
    return os.path.getsize(p) // 1024


def redim(im, larg):
    if im.width <= larg:
        return im
    return im.resize((larg, round(im.height * larg / im.width)), Image.LANCZOS)


def unifier_fond(im):
    """Ramène tous les bords au même noir, sans toucher au centre.
    Un masque radial flou multiplié sur l'image : au centre il vaut 1
    (rien ne change), aux coins il vaut ~0,14 (le fond devient l'encre)."""
    L, H = im.size
    m = Image.new("L", (L, H), 0)
    d = ImageDraw.Draw(m)
    # l'ellipse lumineuse couvre l'œuvre, pas les marges
    d.ellipse([-L * 0.10, -H * 0.10, L * 1.10, H * 1.10], fill=255)
    d.ellipse([L * 0.02, H * 0.02, L * 0.98, H * 0.98], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(min(L, H) * 0.16))
    # on remonte le plancher : les coins gardent 14 % de leur clarté
    m = m.point(lambda v: 36 + v * 219 // 255)
    noir = Image.new("RGB", (L, H), (10, 10, 10))
    return Image.composite(im, noir, m)


def ecrire(im, rel, q):
    p = os.path.join(IMG, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    im.convert("RGB").save(p, "WEBP", quality=q, method=6)
    return p


if __name__ == "__main__":
    print("ANGY ART — pose des images")
    total = 0

    print("\n  scènes")
    for src, rel, larg, q in SCENES:
        s = os.path.join(IA, src + ".png")
        if not os.path.exists(s):
            print(f"    [KO] {src}.png introuvable")
            continue
        p = ecrire(redim(Image.open(s), larg), rel, q)
        k = poids(p)
        total += k
        print(f"    {rel:<26} {larg:>5}px  {k:>4} Ko" + ("   ⚠️ lourd" if k > 400 else ""))

    print("\n  œuvres (fond unifié)")
    for n in OEUVRES:
        s = os.path.join(IA, n + ".png")
        if not os.path.exists(s):
            print(f"    [KO] {n}.png introuvable")
            continue
        im = unifier_fond(redim(Image.open(s).convert("RGB"), LARG_OEUVRE))
        p = ecrire(im, f"gallery/{n}.webp", Q_OEUVRE)
        k = poids(p)
        total += k
        print(f"    gallery/{n}.webp        {k:>4} Ko" + ("   ⚠️ lourd" if k > 300 else ""))

    print(f"\n  total images : {total} Ko")

"""Le logo NEBULA en couches, pour l'animer sans le redessiner.

Le logo n'existe qu'en JPEG lumineux sur fond noir (galaxie + NEBULA + AGENCY).
Un logo qui brille sur du noir se détoure par sa LUMIÈRE, pas par rembg :
l'alpha est la luminance, la couleur est « dé-prémultipliée ». Le halo est gardé.

Ce qui sort, dans public/nebula30/logo/ (agrandi x2, Lanczos) :

    marque.png        la galaxie seule
    nebula.png        le mot NEBULA entier
    lettres/0..5.png  ses six lettres, découpées dans les VRAIES lettres
    agency.png        le mot AGENCY
    trait-g.png       le trait à gauche d'AGENCY
    trait-d.png       le trait à droite
    couches.json      position et taille de chaque couche, en pixels du logo x2,
                      et le centre de l'étoile de la galaxie
    points-*.json     des points tirés dans chaque forme, pour les particules

Et src/nebula30/couches.ts, le même contenu en module : le montage le lit sans
attendre de chargement (comme `mots.ts` pour le plan du dimanche).

    python _outils/nebula30_logo.py
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

ICI = Path(__file__).resolve().parent.parent
SOURCE = ICI.parent / "00-nebula-agency/logo-nebula-agency.jpg"
DOSSIER = ICI / "public/nebula30/logo"
ECHELLE = 2
rng = np.random.default_rng(29)

# Les trois bandes lues sur le fichier (y en pixels du JPEG, 1536 x 1024).
BANDE_MARQUE = (240, 552)
BANDE_NEBULA = (556, 642)
BANDE_AGENCY = (652, 688)


def detourer(rgb):
    """Alpha = luminance (le noir disparaît, le halo reste), couleur dé-prémultipliée."""
    lum = rgb.max(axis=2)
    alpha = np.clip((lum - 6) / (255 - 6), 0, 1) ** 0.85
    couleur = np.clip(rgb / np.maximum(alpha[..., None], 1e-3), 0, 255)
    couleur[alpha < 0.004] = 0
    return np.dstack([couleur, alpha * 255]).astype(np.uint8)


def boite(alpha, seuil=10):
    ys, xs = np.where(alpha > seuil)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def segments(profil, seuil, ecart_min):
    """Les plages de colonnes allumées, séparées par au moins `ecart_min` colonnes éteintes."""
    allume = profil > seuil
    plages, debut, trou = [], None, 0
    for x, v in enumerate(allume):
        if v:
            if debut is None:
                debut = x
            trou = 0
            fin = x + 1
        elif debut is not None:
            trou += 1
            if trou >= ecart_min:
                plages.append((debut, fin))
                debut, trou = None, 0
    if debut is not None:
        plages.append((debut, fin))
    return plages


def tirer_points(rgba, n):
    """n points tirés dans la forme, plus souvent là où elle brille. Coordonnées 0..1."""
    a = rgba[..., 3].astype(np.float64) / 255
    poids = (a ** 1.6).ravel()
    poids /= poids.sum()
    idx = rng.choice(len(poids), size=n, p=poids)
    h, w = a.shape
    ys, xs = np.divmod(idx, w)
    xs = (xs + rng.random(n)) / w
    ys = (ys + rng.random(n)) / h
    couleurs = rgba[..., :3].reshape(-1, 3)[idx]
    return [[round(float(x), 4), round(float(y), 4), "#%02x%02x%02x" % tuple(c)] for x, y, c in zip(xs, ys, couleurs)]


def sauver(rgba, nom):
    img = Image.fromarray(rgba, "RGBA")
    img = img.resize((img.width * ECHELLE, img.height * ECHELLE), Image.LANCZOS)
    img.save(DOSSIER / nom, optimize=True)
    return img


def main():
    (DOSSIER / "lettres").mkdir(parents=True, exist_ok=True)
    rgb = np.asarray(Image.open(SOURCE).convert("RGB")).astype(np.float32)
    logo = detourer(rgb)
    couches = {}

    def poser(nom, x0, y0, x1, y1, fichier):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        part = logo[y0:y1, x0:x1].copy()
        sauver(part, fichier)
        couches[nom] = {"x": x0 * ECHELLE, "y": y0 * ECHELLE, "w": (x1 - x0) * ECHELLE, "h": (y1 - y0) * ECHELLE, "fichier": fichier}
        return part

    # La galaxie : bande du haut, cadrée sur ce qui brille.
    y0, y1 = BANDE_MARQUE
    x0, by0, x1, by1 = boite(logo[y0:y1, :, 3])
    marque = poser("marque", x0, y0 + by0, x1, y0 + by1, "marque.png")
    # Le centre de l'étoile = le point le plus blanc du CŒUR de la galaxie. Sur toute
    # la galaxie, c'est un reflet du bord droit qui gagne.
    gy0, gx0 = y0 + by0, x0
    h, w = by1 - by0, x1 - x0
    coeur = rgb[gy0 + h // 4:gy0 + 3 * h // 4, gx0 + w // 4:gx0 + 3 * w // 4].min(axis=2)
    cy, cx = np.unravel_index(np.argmax(coeur), coeur.shape)
    couches["etoile"] = {"x": (gx0 + w // 4 + int(cx)) * ECHELLE, "y": (gy0 + h // 4 + int(cy)) * ECHELLE}

    # NEBULA, puis ses six lettres.
    y0, y1 = BANDE_NEBULA
    x0, by0, x1, by1 = boite(logo[y0:y1, :, 3], seuil=40)
    poser("nebula", x0, y0 + by0, x1, y0 + by1, "nebula.png")
    bande = logo[y0 + by0:y0 + by1, x0:x1, 3].astype(np.float64)
    plages = segments(bande.max(axis=0), 45, 3)
    print("NEBULA :", len(plages), "lettres", plages)
    couches["lettres"] = []
    for i, (a, b) in enumerate(plages):
        a, b = max(0, a - 2), min(bande.shape[1], b + 2)
        poser(f"lettre{i}", x0 + a, y0 + by0, x0 + b, y0 + by1, f"lettres/{i}.png")
        couches["lettres"].append(couches.pop(f"lettre{i}"))

    # AGENCY et ses deux traits.
    y0, y1 = BANDE_AGENCY
    x0, by0, x1, by1 = boite(logo[y0:y1, :, 3], seuil=25)
    bande = logo[y0 + by0:y0 + by1, x0:x1, 3].astype(np.float64)
    plages = segments(bande.max(axis=0), 25, 12)
    print("AGENCY :", plages)
    gauche, *milieu, droite = plages
    poser("trait-g", x0 + gauche[0], y0 + by0, x0 + gauche[1], y0 + by1, "trait-g.png")
    poser("agency", x0 + milieu[0][0], y0 + by0, x0 + milieu[-1][1], y0 + by1, "agency.png")
    poser("trait-d", x0 + droite[0], y0 + by0, x0 + droite[1], y0 + by1, "trait-d.png")

    # Le cadre du logo entier (pour poser les couches les unes par rapport aux autres).
    x0, ya, x1, yb = boite(logo[..., 3], seuil=10)
    couches["logo"] = {"x": x0 * ECHELLE, "y": ya * ECHELLE, "w": (x1 - x0) * ECHELLE, "h": (yb - ya) * ECHELLE}

    (DOSSIER / "couches.json").write_text(json.dumps(couches, indent=1), encoding="utf-8")
    points_marque = tirer_points(marque, 2600)
    nebula = np.asarray(Image.open(DOSSIER / "nebula.png"))
    points_nebula = tirer_points(nebula, 1400)
    (DOSSIER / "points-marque.json").write_text(json.dumps(points_marque), encoding="utf-8")
    (DOSSIER / "points-nebula.json").write_text(json.dumps(points_nebula), encoding="utf-8")
    module = ICI / "src/nebula30/couches.ts"
    module.parent.mkdir(parents=True, exist_ok=True)
    entete = [
        "/**",
        " * Écrit par `_outils/nebula30_logo.py` : NE PAS ÉDITER À LA MAIN.",
        " * Les couches du logo NEBULA (en pixels du logo agrandi x2) et des points tirés",
        " * dans la galaxie et dans le mot NEBULA, pour que les particules les dessinent.",
        " */",
        "type Couche = {x: number; y: number; w: number; h: number; fichier: string};",
        "export const COUCHES: {marque: Couche; nebula: Couche; agency: Couche; 'trait-g': Couche; 'trait-d': Couche;",
        "\tlettres: Couche[]; etoile: {x: number; y: number}; logo: {x: number; y: number; w: number; h: number}} =",
        f"\t{json.dumps(couches, ensure_ascii=False)};",
        f"export const POINTS_MARQUE: [number, number, string][] = {json.dumps(points_marque)};",
        f"export const POINTS_NEBULA: [number, number, string][] = {json.dumps(points_nebula)};",
    ]
    module.write_text("\n".join(entete) + "\n", encoding="utf-8")
    for nom, c in couches.items():
        print(" ·", nom, c if not isinstance(c, list) else f"{len(c)} lettres")
    print("→", DOSSIER)


if __name__ == "__main__":
    main()

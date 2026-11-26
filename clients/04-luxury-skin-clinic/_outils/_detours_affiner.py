# -*- coding: utf-8 -*-
"""_detours_affiner.py · des détourages INA au niveau d'une vitrine de luxe (26/11, Mongazi : « y a de mauvais
détourages, c'est très mauvais, relève le niveau et corrige tout au maximum »).

Ce que le détourage brut (rembg / isnet, `_detourer_ina.py`) laissait passer, vu sur les photos de Mongazi :
  · des TROUS dans le produit : la boîte du Lip Kit est imprimée de lèvres blanches et roses, que le modèle a prises
    pour du fond ; dans la 3D, on voyait le noir à travers (« un rectangle de bruit ») ;
  · des débris détachés du produit ;
  · un liseré clair au bord, la couleur du fond blanc de la photo, qui ressort sur le noir.

Ce qu'il fait, pour chaque produit du manifeste, à partir de la PHOTO D'ORIGINE (jamais retouchée) :
  1. le masque du modèle, seuillé ; on garde le produit (les morceaux de plus de 3 % du plus gros), pas les débris ;
  2. on BOUCHE les trous : un flacon ou un pot est plein, tout trou à l'intérieur du contour est une erreur, et il se
     remplit avec les vraies couleurs de la photo ;
  3. l'intérieur devient opaque, le bord garde sa douceur, rogné d'un pixel ;
  4. le bord est recoloré avec la couleur du produit juste à côté (au lieu du blanc du fond).
Il écrit le même fichier (le manifeste ne change pas), avec les couleurs gardées sous la transparence (`exact`), et
une planche de CONTRÔLE sur magenta à regarder.
    python _outils/_detours_affiner.py              tout le manifeste
    python _outils/_detours_affiner.py "Lip Kit"    un seul produit
"""
import io
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ICI = Path(__file__).resolve().parent.parent
DOSSIER = ICI / "assets/images/ina-luxury/_detoures"
MANIFESTE = DOSSIER / "detoures.json"
# UNE BOÎTE EST CONVEXE : là où son imprimé clair touche le fond blanc de la photo (les lèvres blanches du Lip Kit, sur
# le bord haut), aucun modèle ne peut séparer les deux par la couleur. Sa silhouette est donc complétée par son enveloppe
# convexe, limitée à la part haute de l'image (la boîte) : le ruban qui pend dessous n'est pas touché.
CONVEXE = {"Lip Kit": 0.63}


def flou(x, s):
    return ndi.gaussian_filter(x, s, mode="nearest")


def affiner(photo, alpha_brut, convexe=None):
    rgb = np.asarray(photo, np.float32)
    a = np.asarray(alpha_brut, np.float32)
    m = a > 127
    lab, n = ndi.label(m)
    if n == 0:
        return None, {}
    tailles = ndi.sum(m, lab, range(1, n + 1))
    garder = [i + 1 for i, t in enumerate(tailles) if t >= tailles.max() * 0.03]
    corps = np.isin(lab, garder)
    plein = ndi.binary_fill_holes(corps)
    if convexe:
        from scipy.spatial import ConvexHull
        from PIL import ImageDraw as _D
        ys, xs = np.nonzero(plein)
        haut = ys.min() + (ys.max() - ys.min()) * convexe
        sel = ys <= haut
        pts = np.column_stack([xs[sel], ys[sel]])[:: max(1, int(sel.sum() // 20000))]
        h = ConvexHull(pts)
        poly = Image.new("L", (plein.shape[1], plein.shape[0]), 0)
        _D.Draw(poly).polygon([tuple(map(float, pts[i])) for i in h.vertices], fill=255)
        plein = plein | (np.asarray(poly) > 0)
    trous = plein & ~corps
    # le bord doux du modèle, mais seulement autour du produit gardé (pas autour des débris)
    zone = ndi.binary_dilation(plein, iterations=3)
    alpha = np.where(zone, a, 0.0)
    interieur = ndi.binary_erosion(plein, iterations=2)
    alpha[interieur] = 255.0
    alpha[trous] = 255.0
    # on rogne le bord d'un pixel (le liseré du fond blanc), puis on l'adoucit d'un demi-pixel
    alpha = ndi.minimum_filter(alpha, size=3)
    alpha = flou(alpha, 0.55)
    alpha[alpha < 10] = 0
    # le bord prend la couleur du produit juste à côté (moyenne normalisée de l'intérieur)
    coeur = ndi.binary_erosion(plein, iterations=3).astype(np.float32)
    poids = flou(coeur, 3.0) + 1e-4
    voisin = np.stack([flou(rgb[..., c] * coeur, 3.0) / poids for c in range(3)], -1)
    bord = (plein & ~ndi.binary_erosion(plein, iterations=3)) | (~plein & (alpha > 0))
    t = np.clip((255.0 - alpha) / 255.0, 0, 1)[..., None] * 0.85 + 0.15
    rgb2 = np.where(bord[..., None], rgb * (1 - t) + voisin * t, rgb)
    out = np.dstack([np.clip(rgb2, 0, 255), np.clip(alpha, 0, 255)]).astype(np.uint8)
    stats = {"trous": float(trous.sum()) / max(1.0, float(plein.sum())) * 100,
             "debris": float((m & ~corps).sum()) / max(1.0, float(m.sum())) * 100}
    return Image.fromarray(out, "RGBA"), stats


def main():
    s = (ICI / "ina-luxury.html").read_text(encoding="utf-8")
    img = json.loads(re.search(r"const IMG=(\{[\s\S]*?\n\});", s).group(1))
    man = json.loads(MANIFESTE.read_text(encoding="utf-8"))
    choix = [a for a in sys.argv[1:] if not a.startswith("--")] or list(man)
    from rembg import new_session, remove
    session = new_session("isnet-general-use")
    faits = []
    for nom in choix:
        if nom not in man or nom not in img:
            print("  inconnu :", nom)
            continue
        src = ICI / img[nom].split("?")[0]
        photo = Image.open(src).convert("RGB")
        photo.thumbnail((900, 900), Image.LANCZOS)
        brut = remove(photo, session=session, post_process_mask=True, only_mask=True)
        out, st = affiner(photo, brut.convert("L"), CONVEXE.get(nom))
        if out is None:
            print("  rien trouvé :", nom)
            continue
        box = out.getchannel("A").getbbox()
        mg = 8
        out = out.crop((max(0, box[0] - mg), max(0, box[1] - mg), min(out.width, box[2] + mg), min(out.height, box[3] + mg)))
        dst = ICI / man[nom].split("?")[0]
        tmp = dst.with_suffix(".tmp")
        out.save(tmp, "WEBP", quality=92, method=6, exact=True)
        tmp.replace(dst)
        faits.append((nom, dst))
        print(f"  {nom:36} trous bouchés {st['trous']:5.2f} %  débris retirés {st['debris']:5.2f} %  {out.size}")
    # la planche de contrôle, sur magenta : un trou, un débris, un liseré s'y voient tout de suite
    t, cols = 200, 9
    pl = Image.new("RGB", (cols * (t + 6), ((len(faits) + cols - 1) // cols) * (t + 24)), (40, 40, 40))
    d = ImageDraw.Draw(pl)
    for i, (nom, f) in enumerate(faits):
        p = Image.open(f).convert("RGBA"); p.thumbnail((t - 10, t - 10), Image.LANCZOS)
        c = Image.new("RGBA", (t, t), (255, 0, 255, 255)); c.alpha_composite(p, ((t - p.width) // 2, (t - p.height) // 2))
        x, y = (i % cols) * (t + 6), (i // cols) * (t + 24)
        pl.paste(c.convert("RGB"), (x, y)); d.text((x + 2, y + t + 6), nom[:30], fill=(255, 255, 255))
    (ICI / "_vues").mkdir(exist_ok=True)
    out = ICI / "_vues/detoures-affines-magenta.jpg"
    pl.save(out, quality=86)
    print(len(faits), "affiné(s) ;", out)


if __name__ == "__main__":
    main()

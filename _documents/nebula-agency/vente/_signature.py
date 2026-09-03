#!/usr/bin/env python3
"""
Détoure la signature manuscrite de Mongazi, depuis une photo, vers un PNG à fond
transparent utilisable par _build_pdf.py.

    python3 _documents/nebula-agency/vente/_signature.py <photo>
    python3 _documents/nebula-agency/vente/_signature.py <photo> --voir

Entrée  : une photo de la signature à l'encre bleue sur papier blanc.
Sortie  : secrets/signature-mongazi.png  (ignoré par git, le dépôt est PUBLIC)
`--voir` écrit en plus une planche sur damier, à REGARDER avant de conclure.

⛔ Pas de rembg ici. rembg détoure un SUJET posé sur un fond ; un trait d'encre
sur du papier n'a pas de silhouette. Ce qui le sépare du papier est une COULEUR.
Un seuil sur la dominante bleue donne un alpha continu, donc des traits qui
gardent leur délié : une binarisation les hacherait.

⚠️ On ne cherche jamais la FEUILLE : sur la photo d'origine le carrelage était
presque aussi clair qu'elle. Chercher l'encre directement évite le problème.

⛔ Aucun redressement. L'axe principal d'une signature n'est pas sa ligne de
base : il est dominé par la longue envolée finale. Se caler dessus pencherait
l'écriture vers le bas.
"""
import os, sys
import numpy as np
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(ROOT, "..", "..", ".."))
SORTIE = os.path.join(REPO, "secrets", "signature-mongazi.png")

# Repérage de l'encre : une dominante bleue franche ET un pixel sombre.
# La teinte décide, la luminance sert de garde-fou — un reflet bleuté mais
# CLAIR n'est pas de l'encre.
SEUIL_BLEU = 30      # B - R, en niveaux 0-255
SEUIL_LUM  = 180     # au-dessus, c'est du papier ou un reflet

# ⛔ La rotation N'A PAS DE VALEUR PAR DÉFAUT, et c'est délibéré.
# La 1re photo arrivait couchée et demandait un quart de tour horaire. La 2e,
# prise au même endroit sur le même carrelage, sortait DÉJÀ DROITE d'
# `exif_transpose` : le même quart de tour la remettait sur le flanc. Un défaut
# se trompe donc une fois sur deux. On regarde la planche, on décide, on passe
# `--rot`. Le script prévient quand la boîte est plus haute que large : une
# signature couchée, c'est presque toujours ça.
ROTATIONS = {
    "aucune":  None,
    "horaire": Image.Transpose.ROTATE_270,
    "anti":    Image.Transpose.ROTATE_90,
    "demi":    Image.Transpose.ROTATE_180,
}

MARGE = 24           # px de papier gardés autour du tracé


def _charger(chemin):
    """Ouvre la photo, en redressant l'orientation EXIF de l'appareil."""
    try:
        import pillow_heif                      # noqa: F401
        pillow_heif.register_heif_opener()
    except ImportError:
        if chemin.lower().endswith((".heic", ".heif")):
            raise SystemExit(
                "Photo HEIC (iPhone) et pillow_heif absent : pip install pillow-heif"
            )
    im = Image.open(chemin)
    im = ImageOps.exif_transpose(im)             # sinon la photo arrive couchée
    return im.convert("RGB")


def detourer(chemin, marge=MARGE, rotation=None):
    im = _charger(chemin)
    a = np.asarray(im).astype(np.int16)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]

    teinte = B - R                                # dominante bleue de l'encre
    lum = (0.299 * R + 0.587 * G + 0.114 * B)

    encre = (teinte > SEUIL_BLEU) & (lum < SEUIL_LUM)
    if not encre.any():
        raise SystemExit("Aucune encre bleue trouvée : mauvaise photo, ou seuils à revoir.")

    # Le masque attrape aussi les reflets bleutés du carrelage. Une signature est
    # d'un seul tenant : on ne garde que la plus grosse tache, et ce qui la
    # frôle (un point détaché, une barre). Sans ça, un reflet à l'autre bout de
    # la photo étirait la boîte de 1241 px à 1911.
    from scipy import ndimage
    etiq, n = ndimage.label(ndimage.binary_dilation(encre, iterations=6))
    if n > 1:
        tailles = ndimage.sum(encre, etiq, range(1, n + 1))
        encre = encre & (etiq == (int(np.argmax(tailles)) + 1))

    ys, xs = np.nonzero(encre)
    y0, y1 = int(ys.min()), int(ys.max())
    x0, x1 = int(xs.min()), int(xs.max())
    h, l = im.size[1], im.size[0]

    # Le seuil a-t-il vraiment trouvé l'encre, ou toute l'image ?
    part = encre.mean()
    if part > 0.25:
        raise SystemExit(
            "Le masque couvre %.0f %% de la photo : ce n'est pas une signature. "
            "Fond bleuté ou lumière colorée." % (part * 100)
        )

    y0, y1 = max(0, y0 - marge), min(h - 1, y1 + marge)
    x0, x1 = max(0, x0 - marge), min(l - 1, x1 + marge)

    # Alpha CONTINU : la teinte décide, la noirceur module. Les déliés survivent.
    #
    # ⚠️ La rampe était FIXE (60 niveaux au-dessus du seuil), calibrée sur une
    # photo dont l'encre montait à B-R = 90. La 2e photo, prise dans une pièce
    # plus sombre, plafonne à 42 : la même formule sortait 0,20 d'opacité, une
    # signature fantôme, et le masque était pourtant PARFAIT. La rampe se cale
    # donc sur CETTE photo-ci, au 85e centile de la teinte de l'encre trouvée :
    # le plein du trait devient opaque, les bords restent progressifs, et une
    # photo vive comme une photo terne sortent pareil.
    plein = float(np.percentile(teinte[encre], 85))
    plein = max(plein, SEUIL_BLEU + 12)          # garde-fou si l'encre est très pâle
    t = np.clip((teinte - SEUIL_BLEU) / (plein - SEUIL_BLEU), 0, 1)
    noirceur = np.clip((SEUIL_LUM - lum) / SEUIL_LUM, 0, 1)
    alpha = np.clip(t * (0.55 + 0.45 * noirceur), 0, 1)

    alpha = alpha[y0:y1 + 1, x0:x1 + 1]
    encre_c = a[y0:y1 + 1, x0:x1 + 1]

    # L'encre est peinte en bleu nuit franc plutôt qu'en ses pixels d'origine :
    # une photo porte la couleur de l'ampoule de la pièce.
    rgba = np.zeros(alpha.shape + (4,), dtype=np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = 22, 30, 74
    rgba[..., 3] = (alpha * 255).astype(np.uint8)

    out = Image.fromarray(rgba, "RGBA")
    if rotation is not None:
        out = out.transpose(rotation)

    infos = {
        "photo": im.size,
        "boite": (x1 - x0 + 1, y1 - y0 + 1),
        "sortie": out.size,
        "part": part,
        "opaque": float((alpha > 0.5).mean()),
    }
    return out, infos, encre_c


def planche(img, dest, carreau=16):
    """Pose l'image sur un damier : sans lui, un alpha raté ne se voit pas."""
    l, h = img.size
    fond = Image.new("RGB", (l, h), "#ffffff")
    px = fond.load()
    for y in range(h):
        for x in range(l):
            if ((x // carreau) + (y // carreau)) % 2:
                px[x, y] = (214, 214, 214)
    fond.paste(img, (0, 0), img)
    fond.save(dest)
    return dest


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    voir = "--voir" in sys.argv
    if not args:
        raise SystemExit(__doc__.strip().splitlines()[2].strip())

    nom_rot = "aucune"
    for a in sys.argv:
        if a.startswith("--rot="):
            nom_rot = a.split("=", 1)[1]
    if nom_rot not in ROTATIONS:
        raise SystemExit("--rot doit valoir : " + " | ".join(ROTATIONS))

    img, infos, _ = detourer(args[0], rotation=ROTATIONS[nom_rot])
    print("  photo   %d x %d" % infos["photo"])
    print("  boîte   %d x %d  (%.2f %% de la photo est de l'encre)"
          % (infos["boite"][0], infos["boite"][1], infos["part"] * 100))
    print("  sortie  %d x %d  (rotation : %s)" % (infos["sortie"] + (nom_rot,)))
    if infos["sortie"][1] > infos["sortie"][0]:
        print("  ⚠️  plus HAUTE que large : une signature est presque toujours\n"
              "      couchée dans ce cas. Regarder la planche avant de conclure.")
    print("  opaque  %.1f %% des pixels au-dessus de 50 %% d'alpha"
          % (infos["opaque"] * 100))

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    img.save(SORTIE)
    print("\n  ->  %s  (%d Ko, hors git)" % (SORTIE, os.path.getsize(SORTIE) // 1024))

    if voir:
        # ⚠️ La planche PORTE la signature. Elle sort donc dans pdf/signe/, déjà
        # ignoré par git, jamais à la racine du dépôt : le point d'entrée d'un
        # fichier sensible n'est pas là où on le range, c'est là où on le dépose.
        dossier = os.path.join(ROOT, "pdf", "signe")
        os.makedirs(dossier, exist_ok=True)
        dest = os.path.join(dossier, "_planche-signature.png")
        planche(img, dest)
        print("  ->  %s\n      À REGARDER avant de conclure (hors git)." % dest)

# -*- coding: utf-8 -*-
"""_detourer_ina.py · les produits INA détourés, pour les poser sur fond noir dans la 3D (demande de la cliente, 26/11 :
« j'aime l'idée mais c'est pas possible de les mettre en fond noir, les produits ? Pour que ce soit plus esthétique »).

  · LIT les photos dans la table IMG d'ina-luxury.html (jamais une liste recopiée) ;
  · détoure avec rembg / isnet (un seul modèle chargé, une photo après l'autre : le PC a 8 Go) ;
  · nettoie le bord (l'alpha très faible est coupé, il laisserait un halo gris sur le noir) et recadre au produit ;
  · écrit assets/images/ina-luxury/_detoures/<nom>.webp et un manifeste detoures.json (nom du produit -> fichier) ;
  · fait une planche de CONTRÔLE sur fond magenta (_vues/detoures-magenta.jpg) : à REGARDER avant de publier
    (règle de la maison) ; un produit raté se retire du manifeste par --ecarter "Nom du produit".
Les originaux ne sont jamais touchés.
    python _outils/_detourer_ina.py            (ne refait que ce qui manque)
    python _outils/_detourer_ina.py --tout     (refait tout)
    python _outils/_detourer_ina.py --ecarter "Nom exact"
"""
import io
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ICI = Path(__file__).resolve().parent.parent
SORTIE = ICI / "assets" / "images" / "ina-luxury" / "_detoures"
MANIFESTE = SORTIE / "detoures.json"
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass


def slug(nom):
    t = nom.lower()
    for a, b in (("éèêë", "e"), ("àâä", "a"), ("îï", "i"), ("ôö", "o"), ("ûüù", "u"), ("ç", "c")):
        for c in a:
            t = t.replace(c, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def nettoyer(rgba):
    r, g, b, a = rgba.split()
    # l'alpha faible (ombre portée, halo du fond blanc) laisserait un voile gris sur le noir : on le coupe,
    # puis on adoucit d'un demi-pixel pour garder un bord propre
    a = a.point(lambda v: 0 if v < 28 else (255 if v > 235 else v))
    a = a.filter(ImageFilter.GaussianBlur(0.5))
    out = Image.merge("RGBA", (r, g, b, a))
    box = a.getbbox()
    if box:
        m = 8
        box = (max(0, box[0] - m), max(0, box[1] - m), min(out.width, box[2] + m), min(out.height, box[3] + m))
        out = out.crop(box)
    return out


def main():
    s = (ICI / "ina-luxury.html").read_text(encoding="utf-8")
    img = json.loads(re.search(r"const IMG=(\{[\s\S]*?\n\});", s).group(1))
    SORTIE.mkdir(parents=True, exist_ok=True)
    man = json.loads(MANIFESTE.read_text(encoding="utf-8")) if MANIFESTE.exists() else {}
    if "--ecarter" in sys.argv:
        nom = sys.argv[sys.argv.index("--ecarter") + 1]
        man.pop(nom, None)
        MANIFESTE.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
        print("écarté :", nom)
        return
    tout = "--tout" in sys.argv
    from rembg import new_session, remove
    session = new_session("isnet-general-use")
    faits = 0
    for nom, chemin in img.items():
        src = ICI / chemin.split("?")[0]
        dst = SORTIE / (slug(nom) + ".webp")
        if not src.exists():
            print("  photo absente :", chemin)
            continue
        if dst.exists() and not tout and nom in man:
            continue
        im = Image.open(src).convert("RGB")
        im.thumbnail((900, 900), Image.LANCZOS)
        out = nettoyer(remove(im, session=session, post_process_mask=True))
        out.save(dst, "WEBP", quality=90, method=6)
        man[nom] = "assets/images/ina-luxury/_detoures/" + dst.name
        faits += 1
        print(f"  {nom:42} {out.width}x{out.height}")
    MANIFESTE.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{faits} détouré(s), {len(man)} au manifeste")
    # la planche de contrôle, sur magenta : un halo, un trou, un débris s'y voient tout de suite
    vues = ICI / "_vues"
    vues.mkdir(exist_ok=True)
    t, cols = 150, 10
    noms = list(man)
    pl = Image.new("RGB", (cols * (t + 6), ((len(noms) + cols - 1) // cols) * (t + 22)), (255, 0, 255))
    d = ImageDraw.Draw(pl)
    for i, n in enumerate(noms):
        p = Image.open(ICI / man[n]).convert("RGBA")
        p.thumbnail((t, t))
        x, y = (i % cols) * (t + 6), (i // cols) * (t + 22)
        pl.paste(p, (x + (t - p.width) // 2, y + (t - p.height) // 2), p)
        d.text((x + 2, y + t + 4), n[:24], fill=(0, 0, 0))
    pl.save(vues / "detoures-magenta.jpg", quality=85)
    print("planche :", vues / "detoures-magenta.jpg")


if __name__ == "__main__":
    main()

"""Agrandir les produits détourés d'INA pour les grands écrans (26/11, Mongazi : « la vitrine en 4K »).

Le détourage part de photos en 900 px, et un produit n'en occupe qu'une partie : 118 à 528 px. Rendu en 4K, c'est
flou. Real-ESRGAN x4plus (ONNX, processeur, carrés de 128 px) AFFINE la vraie photo, il n'invente pas de produit :
c'est la même règle que pour Quesiah. La transparence n'est pas « agrandie par IA » : elle suit en Lanczos.

Sortie : `assets/images/ina-luxury/_detoures/2x/<nom>.webp`, au double de l'original (x4 puis réduit de moitié :
plus net qu'un x2 direct). Le moteur ne les demande que sur grand écran ; le téléphone garde les originaux.

    python _outils/_agrandir_detoures.py            # tous ceux qui manquent
    python _outils/_agrandir_detoures.py --essai    # chronomètre un carré et s'arrête
    python _outils/_agrandir_detoures.py --planche  # planche avant / après sur magenta, à REGARDER
"""
import json, sys, time

# la console de Windows (cp1252) ne sait pas écrire « → » : sans cela, le premier produit fini arrêtait tout (26/11)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
import numpy as np
from PIL import Image

ICI = Path(__file__).resolve().parent.parent
DOSSIER = ICI / "assets/images/ina-luxury/_detoures"
SORTIE = DOSSIER / "2x"
MODELE = Path.home() / ".modeles-ia/realesrgan/real_esrgan_x4plus-onnx-float/real_esrgan_x4plus_onnx/real_esrgan_x4plus.onnx"
T, BORD = 128, 12          # un carré de 128 px, dont 12 px de recouvrement de chaque côté (pas de couture)


def session():
    import onnxruntime as ort
    o = ort.SessionOptions()
    o.intra_op_num_threads = 3      # le PC a peu de mémoire et d autres travaux : on reste discret
    o.enable_mem_pattern = False
    return ort.InferenceSession(str(MODELE), o, providers=["CPUExecutionProvider"])


def x4(s, rgb):
    """rgb : tableau float32 HxWx3 dans [0,1] → 4H x 4W x 3."""
    h, w, _ = rgb.shape
    pas = T - 2 * BORD
    H = max(T, ((h - 2 * BORD + pas - 1) // pas) * pas + 2 * BORD)
    W = max(T, ((w - 2 * BORD + pas - 1) // pas) * pas + 2 * BORD)
    src = np.pad(rgb, ((0, H - h), (0, W - w), (0, 0)), mode="edge")
    out = np.zeros((H * 4, W * 4, 3), np.float32)
    for y in range(0, H - 2 * BORD, pas):
        for x in range(0, W - 2 * BORD, pas):
            y0, x0 = min(y, H - T), min(x, W - T)
            bloc = src[y0:y0 + T, x0:x0 + T].transpose(2, 0, 1)[None]
            r = s.run(None, {"image": np.ascontiguousarray(bloc)})[0][0].transpose(1, 2, 0)
            # on ne garde que le cœur du carré (le bord a vu trop peu de voisins)
            gy0 = 0 if y0 == 0 else BORD; gx0 = 0 if x0 == 0 else BORD
            gy1 = T if y0 + T >= H else T - BORD; gx1 = T if x0 + T >= W else T - BORD
            out[(y0 + gy0) * 4:(y0 + gy1) * 4, (x0 + gx0) * 4:(x0 + gx1) * 4] = r[gy0 * 4:gy1 * 4, gx0 * 4:gx1 * 4]
    return np.clip(out[:h * 4, :w * 4], 0, 1)


def agrandir(s, f):
    im = Image.open(f).convert("RGBA")
    w, h = im.size
    a = im.getchannel("A")
    # sous la transparence, la couleur est souvent du bruit : on la remplit par la couleur voisine avant l'IA
    rgb = Image.new("RGB", im.size, (0, 0, 0)); rgb.paste(im.convert("RGB"), mask=a)
    fond = im.convert("RGB").resize((max(1, w // 8), max(1, h // 8)), Image.BOX).resize((w, h), Image.BILINEAR)
    plein = Image.composite(im.convert("RGB"), fond, a.point(lambda v: 255 if v > 8 else 0))
    gros = x4(s, np.asarray(plein, np.float32) / 255.0)
    gros = Image.fromarray((gros * 255 + 0.5).astype(np.uint8)).resize((w * 2, h * 2), Image.LANCZOS)
    gros.putalpha(a.resize((w * 2, h * 2), Image.LANCZOS))
    return gros


def ecrire_liste():
    """Le moteur ne demande en 2x que les produits de cette liste : jamais un fichier absent."""
    # un fichier vide (le PC a tué l'agrandisseur en pleine écriture, 26/11) n'est pas un produit agrandi
    noms = sorted(f.name for f in SORTIE.glob("*.webp") if f.stat().st_size > 0)
    (SORTIE / "liste.json").write_text(json.dumps(noms, ensure_ascii=False), encoding="utf-8")


def main():
    man = json.loads((DOSSIER / "detoures.json").read_text(encoding="utf-8"))
    fichiers = sorted({ICI / p.split("?")[0] for p in man.values()})
    if "--planche" in sys.argv:
        return planche(fichiers)
    s = session()
    if "--essai" in sys.argv:
        t = time.time(); s.run(None, {"image": np.zeros((1, 3, T, T), np.float32)})
        print(f"un carré de {T} px : {time.time() - t:.2f} s")
        return
    SORTIE.mkdir(exist_ok=True)
    ecrire_liste()
    for i, f in enumerate(fichiers, 1):
        dest = SORTIE / (f.stem + ".webp")
        if dest.exists() and dest.stat().st_size > 0 and dest.stat().st_mtime > f.stat().st_mtime:
            continue
        t = time.time()
        g = agrandir(s, f)
        # écrit à côté puis renommé : un arrêt brutal ne laisse jamais un fichier à moitié écrit sous le vrai nom
        tmp = dest.with_suffix(".tmp")
        g.save(tmp, "WEBP", quality=88, method=6, exact=True)
        tmp.replace(dest)
        ecrire_liste()
        print(f"{i}/{len(fichiers)} {f.name} {Image.open(f).size} → {g.size} {dest.stat().st_size // 1024} Ko ({time.time() - t:.0f} s)", flush=True)
    print("fini.")


def planche(fichiers):
    """Avant (agrandi bêtement) / après (IA), sur magenta : on voit le détourage ET la netteté."""
    cases = []
    for f in fichiers:
        d = SORTIE / (f.stem + ".webp")
        if not d.exists():
            continue
        a = Image.open(f).convert("RGBA"); b = Image.open(d).convert("RGBA")
        a = a.resize(b.size, Image.BICUBIC)
        for im in (a, b):
            c = Image.new("RGBA", (380, 380), (255, 0, 255, 255)); im2 = im.copy(); im2.thumbnail((370, 370), Image.LANCZOS)
            c.alpha_composite(im2, ((380 - im2.width) // 2, (380 - im2.height) // 2)); cases.append(c)
    if not cases:
        print("rien à montrer"); return
    col = 6; lignes = (len(cases) + col - 1) // col
    p = Image.new("RGB", (col * 380, lignes * 380), (40, 40, 40))
    for i, c in enumerate(cases):
        p.paste(c.convert("RGB"), ((i % col) * 380, (i // col) * 380))
    out = ICI / "_outils/_planche_2x.jpg"
    p.save(out, quality=86); print(out)


if __name__ == "__main__":
    main()

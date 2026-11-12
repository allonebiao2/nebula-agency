"""LE MONDE · un personnage .glb vers l'archive .zip (OBJ + MTL + texture) qu'accepte Mixamo.

    python monde/_outils/glb_vers_obj.py personnage.glb            # écrit personnage-mixamo.zip à côté

Mixamo (squelette et animations, gratuit avec un compte Adobe) n'accepte pas le glTF :
seulement FBX, OBJ, ou une archive .zip qui contient l'OBJ, son MTL et ses textures.
Écrit sans bibliothèque (le 2026-11-12, PyPI ne répondait pas depuis Cotonou) : on lit le
glTF binaire à la main (en-tête, bloc JSON, bloc binaire), on applique les transformations
des nœuds, et on écrit l'OBJ.
"""
from __future__ import annotations

import io
import json
import math
import struct
import sys
import zipfile
from pathlib import Path

TYPES = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I", 5126: "f"}
TAILLES = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def lire_glb(chemin: Path):
    d = chemin.read_bytes()
    magic, version, longueur = struct.unpack_from("<4sII", d, 0)
    if magic != b"glTF":
        raise SystemExit("⛔ ce n'est pas un .glb")
    pos, js, binaire = 12, None, b""
    while pos < longueur:
        taille, genre = struct.unpack_from("<I4s", d, pos); pos += 8
        bloc = d[pos:pos + taille]; pos += taille
        if genre == b"JSON":
            js = json.loads(bloc.decode("utf-8"))
        elif genre.startswith(b"BIN"):
            binaire = bloc
    return js, binaire


def accesseur(js, binaire, i):
    a = js["accessors"][i]; vue = js["bufferViews"][a["bufferView"]]
    n, comp = a["count"], TAILLES[a["type"]]
    fmt = TYPES[a["componentType"]]; pas = vue.get("byteStride") or struct.calcsize(fmt) * comp
    debut = vue.get("byteOffset", 0) + a.get("byteOffset", 0)
    out = []
    for k in range(n):
        v = struct.unpack_from("<" + fmt * comp, binaire, debut + k * pas)
        out.append(v if comp > 1 else v[0])
    if a.get("normalized") and fmt in "BbHh":
        m = {"B": 255, "b": 127, "H": 65535, "h": 32767}[fmt]
        out = [tuple(x / m for x in v) if comp > 1 else v / m for v in out]
    return out


def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def mat_noeud(n):
    if "matrix" in n:
        m = n["matrix"]; return [[m[c * 4 + r] for c in range(4)] for r in range(4)]
    t = n.get("translation", [0, 0, 0]); s = n.get("scale", [1, 1, 1]); x, y, z, w = n.get("rotation", [0, 0, 0, 1])
    R = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
         [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
         [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    return [[R[r][0] * s[0], R[r][1] * s[1], R[r][2] * s[2], t[r]] for r in range(3)] + [[0, 0, 0, 1]]


def appliquer(m, p, w=1.0):
    return tuple(m[r][0] * p[0] + m[r][1] * p[1] + m[r][2] * p[2] + m[r][3] * w for r in range(3))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    src = Path(sys.argv[1]); nom = src.stem
    js, binaire = lire_glb(src)
    I = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    obj, vt_total, v_total, image = [f"mtllib {nom}.mtl", f"usemtl {nom}"], 0, 0, None

    def visiter(i, parent):
        nonlocal vt_total, v_total, image
        n = js["nodes"][i]; m = mat_mul(parent, mat_noeud(n))
        if "mesh" in n:
            for prim in js["meshes"][n["mesh"]]["primitives"]:
                P = accesseur(js, binaire, prim["attributes"]["POSITION"])
                T = accesseur(js, binaire, prim["attributes"]["TEXCOORD_0"]) if "TEXCOORD_0" in prim["attributes"] else None
                ids = accesseur(js, binaire, prim["indices"]) if "indices" in prim else list(range(len(P)))
                for p in P:
                    q = appliquer(m, p); obj.append(f"v {q[0]:.5f} {q[1]:.5f} {q[2]:.5f}")
                if T:
                    for t in T: obj.append(f"vt {t[0]:.5f} {1 - t[1]:.5f}")
                for k in range(0, len(ids), 3):
                    a, b, c = (ids[k] + 1 + v_total, ids[k + 1] + 1 + v_total, ids[k + 2] + 1 + v_total)
                    if T:
                        ta, tb, tc = (ids[k] + 1 + vt_total, ids[k + 1] + 1 + vt_total, ids[k + 2] + 1 + vt_total)
                        obj.append(f"f {a}/{ta} {b}/{tb} {c}/{tc}")
                    else:
                        obj.append(f"f {a} {b} {c}")
                v_total += len(P); vt_total += len(T) if T else 0
                mat = js.get("materials", [{}])[prim.get("material", 0)] if js.get("materials") else {}
                tex = mat.get("pbrMetallicRoughness", {}).get("baseColorTexture")
                if tex and image is None:
                    t = js["textures"][tex["index"]]
                    source = t.get("source")
                    if source is None:   # texture rangée dans une extension (EXT_texture_webp, KHR_texture_basisu…)
                        source = next(v["source"] for v in t.get("extensions", {}).values() if "source" in v)
                    img = js["images"][source]
                    vue = js["bufferViews"][img["bufferView"]]
                    image = (binaire[vue.get("byteOffset", 0): vue.get("byteOffset", 0) + vue["byteLength"]], img.get("mimeType", "image/png"))
        for e in n.get("children", []):
            visiter(e, m)

    for racine in js["scenes"][js.get("scene", 0)]["nodes"]:
        visiter(racine, I)
    if image and "webp" in image[1]:   # Mixamo ne lit pas le WebP : on passe en PNG
        from PIL import Image
        tampon = io.BytesIO(); Image.open(io.BytesIO(image[0])).convert("RGB").save(tampon, "PNG"); image = (tampon.getvalue(), "image/png")
    ext = ".jpg" if image and "jpeg" in image[1] else ".png"
    mtl = f"newmtl {nom}\nKa 1 1 1\nKd 1 1 1\nKs 0 0 0\nd 1\n" + (f"map_Kd {nom}{ext}\n" if image else "")
    cible = src.with_name(f"{nom}-mixamo.zip")
    with zipfile.ZipFile(cible, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{nom}.obj", "\n".join(obj) + "\n")
        z.writestr(f"{nom}.mtl", mtl)
        if image:
            z.writestr(f"{nom}{ext}", image[0])
    print(f"✅ {cible.name} · {v_total} sommets · texture {'oui' if image else 'non'} · {cible.stat().st_size / 1e6:.1f} Mo")


if __name__ == "__main__":
    main()

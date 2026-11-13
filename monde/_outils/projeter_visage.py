"""LE MONDE · reprojeter le VISAGE NET de l'image d'origine sur la tête 3D (Mongazi, 2026-11-13 : « les visages
sont catastrophiques »).

    "D:/Blender/blender.exe" -b --factory-startup -P monde/_outils/projeter_visage.py -- modele.glb image.jpg correspondance.npz [--hauteur-tete 0.16] [--seuil 0.2]

Pourquoi : TRELLIS.2 refait une forme 3D à partir d'UNE image ; sa texture du visage sort floue et pâteuse, alors que
l'image d'origine (1536 × 2752) a un visage net. Le modèle sort de TRELLIS ALIGNÉ sur cette image (vue de face,
pose A) : on peut donc reprojeter la photo, de face, sur la tête.

Ce qu'il fait, sans fenêtre :
  1. lit le modèle (.glb, celui qui a servi à Mixamo : mêmes UV que le FBX animé) et sa texture ;
  2. trouve la silhouette dans l'image (fond gris uni) et met la hauteur du modèle sur celle de la silhouette ;
  3. pour chaque triangle de la TÊTE tourné vers l'avant, parcourt ses texels dans la texture, retrouve leur point 3D,
     le projette de face sur l'image, et y prend la couleur ; mélange progressif sur les côtés et au cou ;
  4. écrit la CORRESPONDANCE (`correspondance.npz`) ; `appliquer_visage.py modele.glb image.jpg correspondance.npz
     texture.jpg` fait le mélange sur la texture d'origine, à poser par `habiller({ texture })`.
⚠️ Regarder le résultat de face ET de trois quarts : une image décalée met les yeux à côté des yeux.
"""
import sys

import bpy
import numpy as np

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(args) < 3:
    print("usage : … -- modele.glb image.jpg texture-sortie.jpg")
    sys.exit(1)
MODELE, IMAGE, SORTIE = args[:3]
def option(nom, defaut):
    return type(defaut)(args[args.index(nom) + 1]) if nom in args else defaut
HT = option("--hauteur-tete", 0.16)      # part de la hauteur totale comptée comme « tête » (cou compris)
SEUIL = option("--seuil", 0.2)           # orientation minimale vers l'avant (0 = de profil, 1 = pile de face)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=MODELE)
obj = next(o for o in bpy.context.scene.objects if o.type == "MESH")
me = obj.data
mw = obj.matrix_world
tex = None
for m in me.materials:
    if m and m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type == "TEX_IMAGE" and n.image:
                tex = n.image
if tex is None:
    print("[visage] aucune texture dans le modèle"); sys.exit(1)
TW, TH = tex.size
T = np.array(tex.pixels[:], dtype=np.float32).reshape(TH, TW, 4)        # lignes de BAS en HAUT (Blender)

src = bpy.data.images.load(IMAGE)
SW, SH = src.size
S = np.array(src.pixels[:], dtype=np.float32).reshape(SH, SW, 4)[::-1]  # lignes de HAUT en BAS
# la silhouette : tout ce qui s'écarte du fond (pris aux coins)
fond = np.median(np.concatenate([S[:20, :20, :3].reshape(-1, 3), S[:20, -20:, :3].reshape(-1, 3)]), axis=0)
masque = np.abs(S[:, :, :3] - fond).sum(axis=2) > 0.12
lignes, colonnes = np.where(masque)
iy0, iy1 = np.percentile(lignes, 0.2), np.percentile(lignes, 99.8)
ix0, ix1 = np.percentile(colonnes, 0.2), np.percentile(colonnes, 99.8)

V = np.array([mw @ v.co for v in me.vertices], dtype=np.float64)
zmin, zmax = V[:, 2].min(), V[:, 2].max()
xmin, xmax = V[:, 0].min(), V[:, 0].max()
s = (iy1 - iy0) / (zmax - zmin)                       # pixels par unité, réglé sur la HAUTEUR
# ⚠️ centrer sur la TÊTE, pas sur toute la silhouette : les bras d'un modèle refait n'ont pas exactement l'envergure
# de la photo, et le visage de Sènami sortait décalé (une tresse sur la joue, 2026-11-13)
bande = 0.12
haut_img = masque[int(iy0):int(iy0 + bande * (iy1 - iy0))]
cols = np.where(haut_img.any(axis=0))[0]
cxi = (cols.min() + cols.max()) / 2
tete = V[V[:, 2] > zmax - bande * (zmax - zmin)]
cxm = (tete[:, 0].min() + tete[:, 0].max()) / 2
print(f"[visage] image {SW}×{SH}, silhouette x {ix0:.0f}-{ix1:.0f}, y {iy0:.0f}-{iy1:.0f} ; modèle h {zmax - zmin:.3f} ; texture {TW}×{TH}")
def vers_image(p):
    return (p[..., 0] - cxm) * s + cxi, (zmax - p[..., 2]) * s + iy0

zcou = zmax - HT * (zmax - zmin)
uv = me.uv_layers.active.data
me.calc_loop_triangles()
ecrits = 0
acc_ligne, acc_col, acc_u, acc_v, acc_w = [], [], [], [], []
for tri in me.loop_triangles:
    pts = V[list(tri.vertices)]
    if pts[:, 2].max() < zcou:
        continue
    n = np.cross(pts[1] - pts[0], pts[2] - pts[0]); L = np.linalg.norm(n)
    if L < 1e-12:
        continue
    face = -n[1] / L                                   # vers −Y = vers l'avant (glTF +Z)
    if face < SEUIL:
        continue
    t = np.array([uv[i].uv[:] for i in tri.loops]) * [TW, TH]   # texels (origine en BAS à gauche)
    x0, y0 = np.floor(t.min(axis=0)).astype(int); x1, y1 = np.ceil(t.max(axis=0)).astype(int)
    if x1 - x0 > 600 or y1 - y0 > 600:
        continue
    gx, gy = np.meshgrid(np.arange(max(0, x0), min(TW, x1 + 1)) + 0.5, np.arange(max(0, y0), min(TH, y1 + 1)) + 0.5)
    a, b, c = t
    d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
    if abs(d) < 1e-9:
        continue
    l1 = ((b[1] - c[1]) * (gx - c[0]) + (c[0] - b[0]) * (gy - c[1])) / d
    l2 = ((c[1] - a[1]) * (gx - c[0]) + (a[0] - c[0]) * (gy - c[1])) / d
    l3 = 1 - l1 - l2
    dedans = (l1 >= -0.03) & (l2 >= -0.03) & (l3 >= -0.03)
    if not dedans.any():
        continue
    P = l1[..., None] * pts[0] + l2[..., None] * pts[1] + l3[..., None] * pts[2]
    u, v = vers_image(P)
    ui = np.clip(u.astype(int), 0, SW - 1); vi = np.clip(v.astype(int), 0, SH - 1)
    col = S[vi, ui, :3]
    # mélange : plein de face, nul de profil ; plein sur la tête, nul en bas du cou
    w = np.clip((face - SEUIL) / 0.25, 0, 1) * np.clip((P[..., 2] - zcou) / (0.03 * (zmax - zmin)), 0, 1)
    w = np.where(dedans, w, 0) * masque[vi, ui]
    yy, xx = gy.astype(int), gx.astype(int)
    garde = w > 0.001
    acc_ligne.append((TH - 1 - yy[garde]).astype(np.int32)); acc_col.append(xx[garde].astype(np.int32))
    acc_u.append(ui[garde].astype(np.int32)); acc_v.append(vi[garde].astype(np.int32)); acc_w.append(w[garde].astype(np.float32))
    ecrits += int((w > 0.5).sum())

# ⚠️ ON N'ÉCRIT PAS L'IMAGE DANS BLENDER : `tex.save()` après `pixels.foreach_set` rendait TOUTE la texture verte et
# cyan (2026-11-13). Blender écrit seulement la correspondance « texel ← pixel de la photo, poids » ; le mélange se
# fait sur la texture d'origine, extraite du .glb telle quelle, par `appliquer_visage.py` (Python pur).
np.savez_compressed(SORTIE, ligne=np.concatenate(acc_ligne), col=np.concatenate(acc_col), u=np.concatenate(acc_u),
                    v=np.concatenate(acc_v), w=np.concatenate(acc_w), taille=np.array([TW, TH]))
print(f"[visage] {ecrits} texels du visage → correspondance écrite : {SORTIE}")

"""LE MONDE · alléger un personnage 3D (sortie TRELLIS.2, ≥ 100 000 faces) avant son squelette Mixamo.

    "D:/Blender/blender.exe" -b --factory-startup -P monde/_outils/alleger_perso.py -- entree.glb sortie.glb [--triangles 40000] [--texture 2048]

Pourquoi : la démo TRELLIS.2 refuse depuis le 2026-11-13 de rendre moins de 100 000 faces, et un téléphone
anime mal 100 000 triangles par personnage (Afi en faisait 88 000 sommets, AUDIT-JEU-VIDEO.md vague 4).
On allège AVANT Mixamo : le squelette et les poids se posent sur le maillage léger, rien n'est à refaire.

Ce qu'il fait, sans fenêtre : importe le .glb, réunit les maillages, « Decimate » (réduction des arêtes,
qui garde la silhouette et les UV) jusqu'au nombre de triangles visé, réduit la texture si elle dépasse
`--texture` px, puis réexporte un .glb (texture embarquée). Il imprime le compte avant/après.
⚠️ Regarder le résultat (visage, mains) : une réduction trop forte efface les doigts.
"""
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(args) < 2:
    print("usage : … -- entree.glb sortie.glb [--triangles 40000] [--texture 2048]")
    sys.exit(1)
ENTREE, SORTIE = args[0], args[1]
def option(nom, defaut):
    return type(defaut)(args[args.index(nom) + 1]) if nom in args else defaut
TRIANGLES = option("--triangles", 40000)
TEXTURE = option("--texture", 2048)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ENTREE)
maillages = [o for o in bpy.context.scene.objects if o.type == "MESH"]
for o in bpy.context.scene.objects:
    o.select_set(o in maillages)
bpy.context.view_layer.objects.active = maillages[0]
if len(maillages) > 1:
    bpy.ops.object.join()
obj = bpy.context.view_layer.objects.active

def triangles(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)

avant = triangles(obj)
if avant > TRIANGLES:
    mod = obj.modifiers.new("alleger", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = TRIANGLES / avant
    mod.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=mod.name)
apres = triangles(obj)
# ⚠️ LISSER APRÈS la réduction : les normales importées restent celles des faces d'avant, et le visage d'Afi
# sortait à facettes (2026-11-13). On efface les normales personnalisées et on lisse.
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
try:
    bpy.ops.mesh.customdata_custom_splitnormals_clear()
except Exception:
    pass
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.shade_smooth()

for img in bpy.data.images:
    if img.size[0] > TEXTURE or img.size[1] > TEXTURE:
        k = TEXTURE / max(img.size[0], img.size[1])
        img.scale(max(1, int(img.size[0] * k)), max(1, int(img.size[1] * k)))
        img.pack()

bpy.ops.export_scene.gltf(filepath=SORTIE, export_format="GLB", use_selection=False, export_image_format="JPEG", export_jpeg_quality=90)
print(f"[alléger] {avant} → {apres} triangles · textures ≤ {TEXTURE} px · {SORTIE}")

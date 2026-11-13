"""LE MONDE · donner à un personnage le squelette Mixamo d'un AUTRE (quand Mixamo refuse de le calculer).

    "D:/Blender/blender.exe" -b --factory-startup -P monde/_outils/transferer_squelette.py -- donneur.fbx cible.glb sortie.fbx

Né le 2026-11-13 : Mixamo échouait sans un mot sur Sènami (« Unknown error while generating motion », cinq
essais, modèle allégé ou d'origine, squelette complet ou sans doigts ; ses longues tresses en sont la cause
probable). Afi, elle, venait d'être calculée. Les deux sont en POSE A, aux proportions voisines.

Ce qu'il fait, sans fenêtre :
  1. importe le DONNEUR (FBX Mixamo AVEC le corps : squelette + maillage pondéré + son animation) ;
  2. importe la CIBLE (.glb), la met à la même taille et à la même place que le corps du donneur (pieds au
     sol, centrée), sans la tourner ;
  3. recopie les POIDS os par os, du corps du donneur vers la cible, au point de surface le plus proche
     (interpolé) ; c'est ce qui dit « ce sommet suit l'avant-bras » ;
  4. attache la cible au squelette du donneur, efface le corps du donneur, et exporte un FBX
     « squelette + nouveau corps + l'animation du donneur », avec les mêmes axes d'os que Mixamo
     (primaire Y, secondaire X, sans os de bout) : les animations des autres fichiers Mixamo s'y rejouent.
⚠️ Regarder le résultat qui marche (bras, jambes, tête) : le transfert suppose deux corps qui se superposent.
"""
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(args) < 3:
    print("usage : … -- donneur.fbx cible.glb sortie.fbx")
    sys.exit(1)
DONNEUR, CIBLE, SORTIE = args[:3]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=DONNEUR, automatic_bone_orientation=False, ignore_leaf_bones=False)
armature = next(o for o in bpy.context.scene.objects if o.type == "ARMATURE")
corps_donneur = [o for o in bpy.context.scene.objects if o.type == "MESH"]
armature.data.pose_position = "REST"
bpy.context.view_layer.update()

def boite(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx

dmn, dmx = boite(corps_donneur)
print(f"[squelette] donneur : {len(corps_donneur)} maillage(s), hauteur {dmx.z - dmn.z:.3f}")

avant = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=CIBLE)
nouveaux = [o for o in bpy.context.scene.objects if o not in avant]
maillages = [o for o in nouveaux if o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in maillages:
    o.select_set(True)
bpy.context.view_layer.objects.active = maillages[0]
if len(maillages) > 1:
    bpy.ops.object.join()
cible = bpy.context.view_layer.objects.active
# détacher de tout parent glTF et figer les transformations
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in nouveaux:
    if o != cible and o.name in bpy.data.objects:
        bpy.data.objects.remove(o, do_unlink=True)

cmn, cmx = boite([cible])
k = (dmx.z - dmn.z) / max(1e-6, cmx.z - cmn.z)
cible.scale = (k, k, k)
bpy.context.view_layer.update()
cmn, cmx = boite([cible])
centre_d = (dmn + dmx) / 2
centre_c = (cmn + cmx) / 2
cible.location += Vector((centre_d.x - centre_c.x, centre_d.y - centre_c.y, dmn.z - cmn.z))
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
cmn, cmx = boite([cible])
print(f"[squelette] cible alignée : hauteur {cmx.z - cmn.z:.3f}, largeur {cmx.x - cmn.x:.3f} (donneur {dmx.x - dmn.x:.3f})")

# le corps du donneur en UN maillage (la source du transfert)
bpy.ops.object.select_all(action="DESELECT")
for o in corps_donneur:
    o.select_set(True)
bpy.context.view_layer.objects.active = corps_donneur[0]
if len(corps_donneur) > 1:
    bpy.ops.object.join()
source = bpy.context.view_layer.objects.active
for m in list(source.modifiers):
    if m.type == "ARMATURE":
        source.modifiers.remove(m)

# les mêmes groupes de sommets (un par os), puis les poids au plus proche
for g in source.vertex_groups:
    if g.name not in cible.vertex_groups:
        cible.vertex_groups.new(name=g.name)
dt = cible.modifiers.new("poids", "DATA_TRANSFER")
dt.object = source
dt.use_vert_data = True
dt.data_types_verts = {"VGROUP_WEIGHTS"}
dt.vert_mapping = "POLYINTERP_NEAREST"
dt.layers_vgroup_select_src = "ALL"
dt.layers_vgroup_select_dst = "NAME"
bpy.ops.object.select_all(action="DESELECT")
cible.select_set(True)
bpy.context.view_layer.objects.active = cible
bpy.ops.object.modifier_apply(modifier=dt.name)
ponderes = sum(1 for v in cible.data.vertices if any(g.weight > 0.01 for g in v.groups))
print(f"[squelette] poids recopiés : {ponderes} / {len(cible.data.vertices)} sommets pondérés")

# attacher au squelette, effacer le corps du donneur
cible.parent = armature
cible.matrix_parent_inverse = armature.matrix_world.inverted()
mod = cible.modifiers.new("Armature", "ARMATURE")
mod.object = armature
bpy.data.objects.remove(source, do_unlink=True)
armature.data.pose_position = "POSE"

# ⚠️ UNE IMAGE SANS NOM DE FICHIER part dans le FBX sous « fbm\image_0 », sans extension : le chargeur de
# three.js la refuse et le corps arrive SANS texture (Sènami, 2026-11-13). On lui donne un nom en .jpg.
import os
base = os.path.splitext(os.path.basename(SORTIE))[0]
for i, img in enumerate(bpy.data.images):
    if img.type == "IMAGE" and not os.path.splitext(img.filepath or "")[1]:
        img.name = f"{base}-{i}.jpg"
        img.filepath_raw = f"//{base}-{i}.jpg"
        img.file_format = "JPEG"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.fbx(filepath=SORTIE, use_selection=False, object_types={"ARMATURE", "MESH"},
                         add_leaf_bones=False, primary_bone_axis="Y", secondary_bone_axis="X",
                         bake_anim=True, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                         path_mode="COPY", embed_textures=True, axis_forward="-Z", axis_up="Y")
print(f"[squelette] écrit : {SORTIE}")

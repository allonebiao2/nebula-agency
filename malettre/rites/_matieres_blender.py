"""MA LETTRE À… · les matières des ouvertures, rendues dans Blender (Cycles) : des « matcaps ».

    "D:/outils/blender-4.5.15-windows-x64/blender.exe" --background --factory-startup --python malettre/rites/_matieres_blender.py

Une matcap est une sphère photographiée sous une lumière : la lettre la lit selon l'orientation de chaque point de
l'objet, et la cire, l'or ou la perle ont alors la lumière d'un vrai rendu, pour le prix d'une texture de 128 px.
C'est ce qui rend la 3D belle sur un téléphone modeste : tout le calcul de la lumière est fait ici, une fois.

Lumière : « interior » (une chambre d'hôtel le soir, Poly Haven, CC0, fournie avec Blender), un peu tournée pour
que le reflet principal tombe en haut à gauche, comme la bougie des fonds.
Écrit `malettre/rites/matieres/<nom>.png` (256 px) ; `_rites.py` les réduit en WebP 128 px pour la lettre.
⚠️ Cycles sur le PROCESSEUR : EEVEE plante sur la carte de ce PC (Intel HD 5500).
"""
import math
import os
import sys

import bpy

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "matieres")
os.makedirs(SORTIE, exist_ok=True)
HDRI = os.path.join(os.path.dirname(bpy.app.binary_path), "4.5", "datafiles", "studiolights", "world", "interior.exr")


def srgb(h):
    """#rrggbb (sRGB) → linéaire, comme Blender l'attend."""
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (1.0,)


# Les cires du produit (`lettre.html`, `.cire-*`) : la même couleur que le cachet en CSS.
CIRES = {"bordeaux": "#8c2f39", "or": "#b8892b", "nuit": "#2b2433", "sapin": "#2f5d4a", "rose": "#b25a72"}


def matiere(nom):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    if nom.startswith("cire-"):
        b.inputs["Base Color"].default_value = srgb(CIRES[nom[5:]])
        b.inputs["Roughness"].default_value = 0.36
        b.inputs["Subsurface Weight"].default_value = 0.12
        b.inputs["Subsurface Radius"].default_value = (0.6, 0.25, 0.2)
        b.inputs["Coat Weight"].default_value = 0.35
        b.inputs["Coat Roughness"].default_value = 0.18
    elif nom == "or":
        b.inputs["Base Color"].default_value = (1.0, 0.71, 0.29, 1)
        b.inputs["Metallic"].default_value = 1.0
        b.inputs["Roughness"].default_value = 0.2
    elif nom == "or-brosse":
        b.inputs["Base Color"].default_value = (0.95, 0.66, 0.27, 1)
        b.inputs["Metallic"].default_value = 1.0
        b.inputs["Roughness"].default_value = 0.42
    elif nom == "argent":
        b.inputs["Base Color"].default_value = (0.93, 0.93, 0.95, 1)
        b.inputs["Metallic"].default_value = 1.0
        b.inputs["Roughness"].default_value = 0.16
    elif nom == "perle":
        b.inputs["Base Color"].default_value = (0.92, 0.89, 0.84, 1)
        b.inputs["Roughness"].default_value = 0.22
        b.inputs["Coat Weight"].default_value = 1.0
        b.inputs["Coat Roughness"].default_value = 0.08
        b.inputs["Thin Film Thickness"].default_value = 420.0  # l'irisation de la nacre
        b.inputs["Thin Film IOR"].default_value = 1.45
    elif nom.startswith("velours-"):
        b.inputs["Base Color"].default_value = srgb({"velours-bordeaux": "#5c1620", "velours-nuit": "#1d1826"}[nom])
        b.inputs["Roughness"].default_value = 0.9
        b.inputs["Sheen Weight"].default_value = 1.0
        b.inputs["Sheen Roughness"].default_value = 0.45
        b.inputs["Sheen Tint"].default_value = (1.0, 0.86, 0.86, 1)
    elif nom == "papier":
        b.inputs["Base Color"].default_value = srgb("#f4ede0")
        b.inputs["Roughness"].default_value = 0.92
        b.inputs["Sheen Weight"].default_value = 0.2
    return m


NOMS = ["cire-" + c for c in CIRES] + ["or", "or-brosse", "argent", "perle", "velours-bordeaux", "velours-nuit", "papier"]
seuls = [a for a in sys.argv[sys.argv.index("--") + 1:]] if "--" in sys.argv else []

# La scène : une sphère, une caméra orthographique en face, la lumière de la chambre.
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 96
sc.cycles.use_denoising = True
sc.render.resolution_x = sc.render.resolution_y = 256
sc.render.film_transparent = True
sc.view_settings.view_transform = "Standard"  # une matcap porte des couleurs d'écran, pas un rendu « Filmic »
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGBA"

monde = bpy.data.worlds.new("chambre")
sc.world = monde
monde.use_nodes = True
nt = monde.node_tree
env = nt.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(HDRI)
coord = nt.nodes.new("ShaderNodeTexCoord")
tourne = nt.nodes.new("ShaderNodeMapping")
tourne.inputs["Rotation"].default_value = (0, 0, math.radians(200))
nt.links.new(coord.outputs["Generated"], tourne.inputs["Vector"])
nt.links.new(tourne.outputs["Vector"], env.inputs["Vector"])
nt.links.new(env.outputs["Color"], nt.nodes["Background"].inputs["Color"])
nt.nodes["Background"].inputs["Strength"].default_value = 1.15

bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=1.0, location=(0, 0, 0))
boule = bpy.context.active_object
bpy.ops.object.shade_smooth()
bpy.ops.object.camera_add(location=(0, -6, 0), rotation=(math.radians(90), 0, 0))
cam = bpy.context.active_object
cam.data.type = "ORTHO"
cam.data.ortho_scale = 2.0
sc.camera = cam

for nom in NOMS:
    if seuls and nom not in seuls:
        continue
    boule.data.materials.clear()
    boule.data.materials.append(matiere(nom))
    sc.render.filepath = os.path.join(SORTIE, nom + ".png")
    bpy.ops.render.render(write_still=True)
    print("matière", nom)

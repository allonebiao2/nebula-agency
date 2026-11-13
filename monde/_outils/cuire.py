"""LE MONDE · cuire la lumière du salon dans Blender (REALISME.md, R1).

    python monde/_servir.py --sans-construire          (dans un autre terminal)
    python monde/_outils/exporter_decor.py             → monde/_cuisson/salon-decor.glb
    "D:/Blender/blender.exe" -b --factory-startup -P monde/_outils/cuire.py -- [--taille 2048] [--echantillons 128]
        [--echantillons-lumiere 256] [--quoi ao,lumiere] [--emission 1] [--calibrage 1] [--lissage 2]

Ce qu'il fait, sans fenêtre :
  1. importe le décor exporté par la page (chaque maillage porte sa CLÉ DE CUISSON en nom, et en
     « extras » : `recepteur` (reçoit une carte) et `zone` (dedans ou dehors)) ;
  2. déplie une 2e coordonnée de texture « cuisson » sur TOUS les récepteurs ensemble, dans une seule
     carte (Smart UV Project, puis rangement des îlots) ; le dehors y prend moins de place que le dedans ;
  3. réserve une BANDE BLANCHE à gauche de la carte : un maillage sans `uv1` lit (0, 0), donc du blanc ;
  4. cuit l'OCCLUSION avec Cycles (les ombres douces des coins et sous les objets ; les petits objets
     scannés occultent sans recevoir), puis la LUMIÈRE DES LAMPES du salon, à leur force de nuit
     (directe + rebonds ; le soleil et le ciel restent calculés en direct dans la page) ;
  5. lisse le bruit sans déborder d'un îlot à l'autre, et écrit dans `monde/lieux/hillary-m-styl/cuisson/` :
     `occlusion.png`, `lumiere.png` (8 bits sRGB, avec son échelle dans le JSON), `salon-cuit.glb`
     (les récepteurs avec leurs deux coordonnées de texture, sans matière) et `cuisson.json`.
⚠️ Ce PC : processeur seul (Intel HD 5500 inutilisable par Cycles). Compter quelques minutes à 128
   échantillons en 2048.
"""
import json
import math
import os
import struct
import sys
import time

import bpy
import bmesh  # noqa: F401  (gardé pour les retouches d'UV)

ICI = os.path.dirname(os.path.abspath(__file__))
MONDE = os.path.dirname(ICI)
ENTREE = os.path.join(MONDE, "_cuisson", "salon-decor.glb")
SORTIE = os.path.join(MONDE, "lieux", "hillary-m-styl", "cuisson")

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def option(nom, defaut):
    return type(defaut)(args[args.index(nom) + 1]) if nom in args else defaut
TAILLE = option("--taille", 2048)
ECHANTILLONS = option("--echantillons", 128)
DISTANCE_AO = option("--distance", 1.2)       # en mètres : jusqu'où un objet assombrit son voisin
POIDS_DEHORS = option("--poids-dehors", 0.3)  # le dehors prend 0,3 fois la densité du dedans
BANDE = 0.012                                 # la bande blanche réservée, à gauche
ECHANTILLONS_LUMIERE = option("--echantillons-lumiere", 256)
EMISSION = option("--emission", 1.0)          # l'anneau doré éclaire : facteur sur son émission physique (÷ 683)
CALIBRAGE = option("--calibrage", 1.0)        # correction finale de la lumière cuite, réglée à l'œil
LISSAGE = option("--lissage", 2)              # rayon du lissage anti-bruit, en pixels
QUOI = option("--quoi", "ao,lumiere").split(",")
PLAFOND_REBONDS = option("--clamp", 0.02)     # plafonne un rebond isolé trop fort (les « lucioles » de Cycles)

t0 = time.time()
def dire(m):
    print(f"[cuisson {time.time() - t0:6.1f} s] {m}", flush=True)

# 1 · la scène vide, puis le décor
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ENTREE)
maillages = [o for o in bpy.context.scene.objects if o.type == "MESH"]
recepteurs = [o for o in maillages if bool(o.get("recepteur", True))]
dire(f"{len(maillages)} maillages importés, {len(recepteurs)} récepteurs, "
     f"{sum(1 for o in bpy.context.scene.objects if o.type == 'LIGHT')} lampes")

# chaque objet garde SA géométrie (l'exporteur partage les formes identiques : sans ça, deux
# objets identiques se déplieraient au même endroit de la carte et se voleraient leurs ombres)
bpy.ops.object.select_all(action="DESELECT")
for o in recepteurs:
    o.select_set(True)
bpy.context.view_layer.objects.active = recepteurs[0]
bpy.ops.object.make_single_user(type="SELECTED_OBJECTS", object=True, obdata=True)

# 2 · la 2e coordonnée de texture ; ⚠️ un maillage sans 1re coordonnée en reçoit une vide, sinon
#     « cuisson » deviendrait la 1re à l'export et la page ne la trouverait pas en `uv1`
for o in recepteurs:
    me = o.data
    if len(me.uv_layers) == 0:
        me.uv_layers.new(name="UVMap")
    while len(me.uv_layers) > 1:
        me.uv_layers.remove(me.uv_layers[-1])
    uv = me.uv_layers.new(name="cuisson")
    me.uv_layers.active = uv

bpy.context.scene.tool_settings.use_uv_select_sync = True
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.0, area_weight=0.0,
                         correct_aspect=True, scale_to_bounds=False)
bpy.ops.object.mode_set(mode="OBJECT")
dire("dépliage fait")

# le dehors moins dense que le dedans (on le voit surtout de loin, pendant l'ouverture)
for o in recepteurs:
    if o.get("zone", "dedans") == "dehors":
        donnees = o.data.uv_layers["cuisson"].data
        for d in donnees:
            d.uv = (d.uv[0] * POIDS_DEHORS, d.uv[1] * POIDS_DEHORS)

bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.select_all(action="SELECT")
bpy.ops.uv.pack_islands(rotate=True, margin=0.003)
bpy.ops.object.mode_set(mode="OBJECT")
dire("îlots rangés")

# 3 · la bande blanche à gauche : tout se décale vers la droite
for o in recepteurs:
    for d in o.data.uv_layers["cuisson"].data:
        d.uv = (BANDE + (1 - BANDE) * d.uv[0], d.uv[1])

# 4 · la cuisson : l'occlusion, puis la lumière des lampes, sur une COPIE FUSIONNÉE
import numpy as np  # noqa: E402  (numpy est livré avec Blender)

sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
if sc.world is None:
    sc.world = bpy.data.worlds.new("monde")
sc.world.light_settings.distance = DISTANCE_AO
sc.render.bake.margin = 16
sc.render.bake.use_clear = True
sc.cycles.sample_clamp_indirect = PLAFOND_REBONDS
os.makedirs(SORTIE, exist_ok=True)

# le ciel : NOIR pour la cuisson. Le ciel et le soleil restent calculés en direct dans la page.
# ⚠️ un ciel « presque noir » (0,004) pesait autant que toutes les lampes réunies, car leurs candelas
#    sont divisées par 683 à l'import : il entrait par la vitrine et la coupole et teintait tout de lavande
#    (2026-11-13)
sc.world.use_nodes = True
fond = sc.world.node_tree.nodes.get("Background")
if fond:
    fond.inputs["Color"].default_value = (0, 0, 0, 1)
    fond.inputs["Strength"].default_value = 0.0

# les lampes : le soleil part (il reste en direct) ; les lampes du salon restent, à leur force de nuit
for l in [o for o in sc.objects if o.type == "LIGHT"]:
    if l.data.type == "SUN" or l.data.energy <= 0:
        bpy.data.objects.remove(l, do_unlink=True)
lampes = [o for o in sc.objects if o.type == "LIGHT"]
dire(f"{len(lampes)} lampes gardées pour la cuisson : " + ", ".join(f"{l.data.type.lower()} {l.data.energy:.2f} W" for l in lampes))

# CE QUI ÉMET : seuls les objets marqués « emetteur » (l'anneau doré) éclairent, à l'échelle PHYSIQUE.
# ⚠️ three.js et Blender ne comptent pas la même unité : l'import glTF divise les candelas des lampes
#    par 683, pas l'émission des matières. Le plafond porte une lueur de 0,047 dans la page (pour ne pas
#    virer au brun) : non corrigée, elle valait 683 fois plus dans Blender, et tout le plafond devenait
#    une lampe géante qui aplatissait la pièce (2026-11-13). Les autres lueurs sont donc éteintes ici.
for o in [o for o in sc.objects if o.type == "MESH"]:
    for m in o.data.materials:
        if m is None or not m.use_nodes:
            continue
        for n in m.node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED" and "Emission Strength" in n.inputs:
                n.inputs["Emission Strength"].default_value *= (EMISSION / 683) if o.get("emetteur") else 0.0

images = {}
def image(nom, flottant):
    im = bpy.data.images.new(nom, TAILLE, TAILLE, alpha=True, float_buffer=flottant)
    im.generated_color = (1, 0, 1, 0)      # magenta transparent = « pas un îlot » (pour le lissage)
    images[nom] = im
    return im

for o in recepteurs:
    if not o.data.materials:
        o.data.materials.append(bpy.data.materials.new("cuisson-" + o.name))
    for m in o.data.materials:
        if m is None:
            continue
        m.use_nodes = True
        n = m.node_tree.nodes.new("ShaderNodeTexImage")
        n.name = "cible-cuisson"
        m.node_tree.nodes.active = n

# ⚠️ cuire 206 objets un par un relance le moteur 206 fois (7 min 30 pour un simple essai, mesuré le
#    2026-11-13) : on cuit une COPIE FUSIONNÉE, en une seule passe ; les originaux sont masqués au rendu
#    pour ne pas assombrir deux fois (deux surfaces confondues se font de l'ombre)
bpy.ops.object.select_all(action="DESELECT")
for o in recepteurs:
    o.select_set(True)
bpy.context.view_layer.objects.active = recepteurs[0]
bpy.ops.object.duplicate()
bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
bpy.ops.object.join()
fusion = bpy.context.view_layer.objects.active
fusion.data.uv_layers.active = fusion.data.uv_layers["cuisson"]
for o in recepteurs:
    o.hide_render = True
bpy.ops.object.select_all(action="DESELECT")
fusion.select_set(True)
bpy.context.view_layer.objects.active = fusion

def cuire(im, type_, echantillons, **kw):
    for m in bpy.data.materials:
        if m.use_nodes and "cible-cuisson" in m.node_tree.nodes:
            m.node_tree.nodes["cible-cuisson"].image = im
            m.node_tree.nodes.active = m.node_tree.nodes["cible-cuisson"]
    sc.cycles.samples = echantillons
    bpy.ops.object.bake(type=type_, margin=16, use_clear=True, **kw)

def lire(im):
    px = np.empty(TAILLE * TAILLE * 4, dtype=np.float32)
    im.pixels.foreach_get(px)
    return px.reshape(TAILLE, TAILLE, 4)

def lisser(rgb, masque, rayon):
    """Lissage qui ne déborde pas d'un îlot à l'autre : moyenne pondérée par le masque (convolution
    normalisée, deux boîtes successives ≈ une gaussienne). Le bruit de Cycles part, les arêtes restent."""
    if rayon <= 0:
        return rgb
    def boite(a, r, axe):
        c = np.cumsum(np.pad(a, [(r + 1, r) if k == axe else (0, 0) for k in range(a.ndim)], mode="edge"), axis=axe)
        haut = np.take(c, range(2 * r + 1, c.shape[axe]), axis=axe)
        bas = np.take(c, range(0, c.shape[axe] - 2 * r - 1), axis=axe)
        return (haut - bas) / (2 * r + 1)
    w = masque.astype(np.float32)[..., None]
    num, den = rgb * w, w
    for _ in range(2):
        for axe in (0, 1):
            num, den = boite(num, rayon, axe), boite(den, rayon, axe)
    return np.where(den > 1e-4, num / np.maximum(den, 1e-4), rgb)

def ilots(px):
    """les pixels cuits (îlots et leur marge) : opaques, et pas du magenta témoin"""
    temoin = (np.abs(px[..., 0] - 1) < 0.01) & (px[..., 1] < 0.01) & (np.abs(px[..., 2] - 1) < 0.01)
    m = (px[..., 3] > 0.5) & ~temoin
    dire(f"îlots : {m.mean() * 100:.1f} % de la carte")
    return m

def bande(px, valeur):
    px[:, : int(BANDE * TAILLE) - 2, :3] = valeur
    px[:, :, 3] = 1.0

def ecrire(im, px, nom):
    # ⚠️ ne JAMAIS changer l'espace colorimétrique d'une image après y avoir écrit : Blender la régénère
    #    et efface les pixels (la 1re carte de lumière était toute noire, 2026-11-13). Une image 8 bits
    #    est en sRGB par défaut : les valeurs écrites sont déjà encodées.
    im.pixels.foreach_set(px.ravel())
    chemin = os.path.join(SORTIE, nom)
    im.filepath_raw = chemin
    im.file_format = "PNG"
    im.save()
    dire(f"carte écrite : {chemin}")

resultat = {"geometrie": "salon-cuit.glb", "version": int(time.time()), "taille": TAILLE}

if "ao" in QUOI:
    im = image("occlusion", False)
    dire(f"cuisson de l'occlusion : {TAILLE} px, {ECHANTILLONS} échantillons, portée {DISTANCE_AO} m…")
    cuire(im, "AO", ECHANTILLONS)
    px = lire(im)
    masque = ilots(px)
    px[..., :3] = np.where(masque[..., None], lisser(px[..., :3], masque, LISSAGE), 1.0)
    bande(px, 1.0)
    ecrire(im, px, "occlusion.png")
    resultat.update({"occlusion": "occlusion.png", "intensite": 1.0, "distance": DISTANCE_AO, "echantillons": ECHANTILLONS})

if "lumiere" in QUOI:
    im = image("lumiere", True)
    dire(f"cuisson de la lumière des lampes : {TAILLE} px, {ECHANTILLONS_LUMIERE} échantillons, "
         f"{sc.cycles.max_bounces} rebonds au plus…")
    cuire(im, "DIFFUSE", ECHANTILLONS_LUMIERE, pass_filter={"DIRECT", "INDIRECT"})
    px = lire(im)
    masque = ilots(px)
    rgb = lisser(px[..., :3], masque, LISSAGE)
    # l'échelle : la carte est enregistrée en 8 bits sRGB (les ombres gardent leur finesse) entre 0 et
    # « haut » ; la page multiplie par « intensité »
    lum = rgb[masque].max(axis=-1) if masque.any() else np.array([1.0])
    haut = float(np.percentile(lum, 99.7)) or 1.0
    mediane = float(np.median(lum)) / haut
    rgb = np.clip(rgb / haut, 0, 1)
    rgb = np.where(rgb <= 0.0031308, rgb * 12.92, 1.055 * np.power(rgb, 1 / 2.4) - 0.055)   # linéaire → sRGB
    px[..., :3] = np.where(masque[..., None], rgb, 0.0)
    # la bande : la lumière MÉDIANE du salon, pour un maillage qui partage une matière cuite sans uv1
    med = 1.055 * mediane ** (1 / 2.4) - 0.055 if mediane > 0.0031308 else mediane * 12.92
    bande(px, med)
    im8 = bpy.data.images.new("lumiere8", TAILLE, TAILLE, alpha=False)
    ecrire(im8, px, "lumiere.png")
    # Blender : « diffuse sans couleur » = E / π, avec E en W/m² ; la page (three.js) attend E en
    # candelas/m², et l'import glTF a converti les candelas en watts par 4π/683 : facteur π × 683
    resultat.update({"lumiere": "lumiere.png", "intensite_lumiere": round(haut * math.pi * 683 * CALIBRAGE, 4),
                     "echantillons_lumiere": ECHANTILLONS_LUMIERE, "emission": EMISSION})

bpy.data.objects.remove(fusion, do_unlink=True)
for o in recepteurs:
    o.hide_render = False

# 5 · les récepteurs, avec leurs deux coordonnées de texture, sans matière
bpy.ops.object.select_all(action="DESELECT")
for o in recepteurs:
    o.select_set(True)
chemin_glb = os.path.join(SORTIE, "salon-cuit.glb")
bpy.ops.export_scene.gltf(filepath=chemin_glb, export_format="GLB", use_selection=True,
                          export_materials="NONE", export_texcoords=True, export_normals=True,
                          export_extras=True, export_yup=True)

# vérification : chaque maillage exporté doit porter TEXCOORD_1
with open(chemin_glb, "rb") as f:
    f.read(12)
    longueur, _ = struct.unpack("<II", f.read(8))
    doc = json.loads(f.read(longueur))
sans = [m.get("name", "?") for m in doc.get("meshes", []) for p in m["primitives"] if "TEXCOORD_1" not in p["attributes"]]
dire(f"{len(doc.get('meshes', []))} maillages exportés, {len(sans)} sans 2e coordonnée de texture")
if sans:
    print("⚠️ sans TEXCOORD_1 :", sans[:10], flush=True)

# on garde ce qui n'a pas été recuit cette fois (cuire la lumière seule ne doit pas effacer l'occlusion)
chemin_json = os.path.join(SORTIE, "cuisson.json")
ancien = {}
if os.path.exists(chemin_json):
    with open(chemin_json, encoding="utf-8") as f:
        ancien = json.load(f)
ancien.update(resultat)
with open(chemin_json, "w", encoding="utf-8") as f:
    json.dump(ancien, f, ensure_ascii=False, indent=2)
dire("fini")

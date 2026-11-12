"""LE MONDE · construire un lieu DANS UNREAL ENGINE, à partir du même plan que le navigateur.

Mongazi, 2026-11-12 : « il faut que tu utilises Unreal Engine pour la construction
aussi », « la construction, niveau fluidité, tu dois normalement la faire aussi avec
Unreal Engine ».

À quoi sert Unreal dans LE MONDE (et à quoi il ne sert pas) :
  ✅ CONSTRUIRE et ÉCLAIRER le salon en qualité cinéma (Lumen, lumière précalculée),
     à partir du MÊME plan.json que le navigateur : une seule disposition, deux moteurs ;
  ✅ tourner la BANDE-ANNONCE du salon pour TikTok (Movie Render Queue), avec les
     caméras posées ici sur chaque point du plan ;
  ✅ EXPORTER des éléments (glTF) et des textures de lumière vers le navigateur ;
  ⛔ PAS faire tourner le salon dans le téléphone de la cliente : Unreal ne sort plus
     pour le navigateur, sauf « Pixel Streaming » (un serveur à carte graphique par
     visiteur, payé à l'heure).

⚠️ ÉCRIT LE 2026-11-12 SANS POUVOIR LE LANCER : le moteur n'était pas encore installé
sur ce PC. À éprouver au premier lancement ; le carnet DEROULEMENT.md dira ce qui a marché.

Lancer, dans l'éditeur Unreal (5.4 et plus), avec les extensions « Python Editor Script
Plugin » et « Editor Scripting Utilities » activées :
    Outils > Exécuter un script Python… > monde/unreal/construire_lieu.py
ou dans la console Python de l'éditeur :
    exec(open(r"C:/Users/USER/nebula-agency/monde/unreal/construire_lieu.py", encoding="utf-8").read())

Repères : le plan est en MÈTRES (x à droite, y en haut, z vers l'entrée). Unreal est en
CENTIMÈTRES (X devant, Y à droite, Z en haut). On pose : X = -z, Y = x, Z = y.
"""
import json
import math
import os

import unreal

LIEU = os.environ.get("MONDE_LIEU", "hillary-m-styl")
ICI = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else r"C:/Users/USER/nebula-agency/monde/unreal"
PLAN = os.path.join(ICI, "..", "lieux", LIEU, "plan.json")
DOSSIER = "LE_MONDE/" + LIEU            # le dossier des acteurs dans l'Outliner

with open(PLAN, encoding="utf-8") as f:
    plan = json.load(f)

acteurs = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
CUBE = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube")
CYLINDRE = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cylinder.Cylinder")
PLAN_MESH = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane.Plane")


def ue(x, y, z):
    """mètres du plan → centimètres Unreal"""
    return unreal.Vector(-z * 100.0, x * 100.0, y * 100.0)


def poser(maillage, nom, x, y, z, largeur, hauteur, profondeur, cap_deg=0.0, sous_dossier=""):
    """une forme de base, centrée en (x, y, z), aux dimensions données en mètres"""
    a = acteurs.spawn_actor_from_object(maillage, ue(x, y, z), unreal.Rotator(0.0, 0.0, -cap_deg))
    a.set_actor_label(nom)
    # les formes de base font 100 cm : l'échelle vaut la dimension en mètres
    a.set_actor_scale3d(unreal.Vector(profondeur, largeur, hauteur))
    a.set_folder_path(DOSSIER + ("/" + sous_dossier if sous_dossier else ""))
    return a


def lumiere(classe, nom, x, y, z, intensite, couleur=(255, 226, 176), rayon=900.0):
    a = acteurs.spawn_actor_from_class(classe, ue(x, y, z))
    a.set_actor_label(nom)
    a.set_folder_path(DOSSIER + "/Lumières")
    comp = a.get_component_by_class(unreal.LightComponent)
    if comp:
        comp.set_editor_property("intensity", intensite)
        comp.set_editor_property("light_color", unreal.Color(couleur[2], couleur[1], couleur[0], 255))
        if hasattr(comp, "set_attenuation_radius"):
            comp.set_attenuation_radius(rayon)
    return a


def construire():
    P = plan["piece"]
    L, Pr, H = P["largeur"], P["profondeur"], P["hauteur"]
    # la pièce
    poser(CUBE, "Sol", 0, -0.05, 0, L, 0.1, Pr, sous_dossier="Pièce")
    poser(CUBE, "Plafond", 0, H + 0.05, 0, L, 0.1, Pr, sous_dossier="Pièce")
    poser(CUBE, "Mur du fond", 0, H / 2, -Pr / 2 - 0.05, L, H, 0.1, sous_dossier="Pièce")
    poser(CUBE, "Mur gauche", -L / 2 - 0.05, H / 2, 0, 0.1, H, Pr, sous_dossier="Pièce")
    poser(CUBE, "Mur droit", L / 2 + 0.05, H / 2, 0, 0.1, H, Pr, sous_dossier="Pièce")
    fac = plan["facade"]
    poser(CUBE, "Façade · linteau", 0, (H + fac["linteau"]) / 2, fac["z"] + 0.1, L, H - fac["linteau"], 0.2, sous_dossier="Façade")
    for i, v in enumerate(fac["vitrines"]):
        poser(CUBE, f"Façade · allège {i + 1}", (v["x1"] + v["x2"]) / 2, fac["allege"] / 2, fac["z"] + 0.1, v["x2"] - v["x1"], fac["allege"], 0.2, sous_dossier="Façade")
    # le dôme et sa ligne dorée
    d = plan["dome"]
    poser(CYLINDRE, "Dôme", d["x"], H + d["creux"] / 2, d["z"], d["rayon"] * 2, d["creux"], d["rayon"] * 2, sous_dossier="Dôme")
    # les podiums et leurs pièces
    for pd in plan["podiums"]:
        poser(CYLINDRE, f"Podium {pd['id']}", pd["x"], pd["h"] / 2, pd["z"], pd["r"] * 2, pd["h"], pd["r"] * 2, sous_dossier="Expositions")
        for k, piece in enumerate(pd["pieces"]):
            poser(CUBE, f"Totem {piece}", pd["x"], pd["h"] + 0.96, pd["z"], 0.92, 1.92, 0.05, sous_dossier="Expositions")
    # le comptoir
    c = plan["comptoir"]
    poser(CUBE, "Comptoir", c["x"], c["hauteur"] / 2, c["z"], c["longueur"], c["hauteur"], c["profondeur"], sous_dossier="Comptoir")
    # les étagères de tissus
    for i, e in enumerate(plan["etageres_tissus"]):
        for y in (0.42, 1.12, 1.82, 2.52):
            poser(CUBE, f"Étagère {i + 1} · {y}", (e["x1"] + e["x2"]) / 2, y, -Pr / 2 + 0.24, e["x2"] - e["x1"], 0.035, 0.46, sous_dossier="Tissus")
    # les lumières : le soleil, le ciel, les lampes du dôme et du comptoir
    soleil = acteurs.spawn_actor_from_class(unreal.DirectionalLight, ue(0, 30, 10), unreal.Rotator(0.0, -50.0, 180.0))
    soleil.set_actor_label("Soleil de Cotonou"); soleil.set_folder_path(DOSSIER + "/Lumières")
    ciel = acteurs.spawn_actor_from_class(unreal.SkyLight, ue(0, H, 0)); ciel.set_actor_label("Ciel"); ciel.set_folder_path(DOSSIER + "/Lumières")
    lumiere(unreal.PointLight, "Lampe du dôme", d["x"], H - 0.6, d["z"], 8000.0)
    lumiere(unreal.PointLight, "Lampe du comptoir", c["x"], H - 1.0, c["z"] + 0.6, 6000.0)
    # une caméra de cinéma sur chaque point du plan : pour la bande-annonce TikTok
    for p in plan["points"]:
        cam = acteurs.spawn_actor_from_class(unreal.CineCameraActor, ue(p["x"], 1.55, p["z"]), unreal.Rotator(0.0, 0.0, -float(p.get("cap", 0)) + 180.0))
        cam.set_actor_label(f"Caméra · {p['nom']}")
        cam.set_folder_path(DOSSIER + "/Caméras")
    unreal.log(f"LE MONDE : {LIEU} construit depuis {PLAN}")


construire()

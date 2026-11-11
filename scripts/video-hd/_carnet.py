#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fabrique Video_HD.ipynb (le carnet Google Colab) à partir de video_hd.py.

Le moteur est recopié tel quel dans le carnet : il n'y a qu'une seule vérité, video_hd.py.
On ne modifie jamais Video_HD.ipynb à la main, on relance :

    python scripts/video-hd/_carnet.py
"""

import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
MOTEUR = open(os.path.join(ICI, "video_hd.py"), encoding="utf-8").read()

# Le moteur voyage dans une chaîne r'''…''' : elle ne doit pas pouvoir se refermer en route.
if "'''" in MOTEUR or MOTEUR.rstrip().endswith("\\"):
    sys.exit("video_hd.py contient ''' ou finit par une barre oblique inverse : le carnet serait cassé.")


def lignes(texte):
    morceaux = texte.strip("\n").split("\n")
    return [m + "\n" for m in morceaux[:-1]] + [morceaux[-1]]


def texte(md):
    return {"cell_type": "markdown", "metadata": {}, "source": lignes(md)}


def code(src):
    return {"cell_type": "code", "metadata": {"cellView": "form"}, "execution_count": None,
            "outputs": [], "source": lignes(src)}


INTRO = """
# 🎬 VIDÉO HD
### Monter une vidéo en **4K** et en **60 images par seconde**, avec l'IA, gratuitement

**Mode d'emploi, téléphone ou ordinateur (par Google Drive, le plus sûr)**
1. Dans **Google Drive**, mets ta vidéo dans un dossier nommé **Video-HD**
   (sur le téléphone : appli Drive → **+** → **Importer** → choisis la vidéo).
   S'il n'existe pas encore, le carnet le crée au premier lancement.
2. Ici, menu **Exécution → Tout exécuter** (sur téléphone, le menu est sous **⋮**).
   Accepte l'avertissement de Google, puis **autorise l'accès à ton Drive**.
3. À la fin, la vidéo améliorée est dans **Drive → Video-HD → resultats**.

Le carnet prend **la vidéo la plus récente** du dossier Video-HD.

**Sur un ordinateur**, tu peux aussi envoyer la vidéo directement : dans la case
**1 · Réglages**, choisis « Je l'envoie depuis cet appareil », puis le bouton **Parcourir**
apparaît dans la case **3** et le résultat se télécharge à la fin.

**Conseil** : coche d'abord **ESSAI_10_SECONDES**. En une ou deux minutes tu vois la qualité,
et le carnet t'annonce le temps qu'il faudra pour la vidéo entière.

⚠️ **Garde cet onglet ouvert et l'écran allumé** pendant le travail : si la page reste trop
longtemps sans activité, Google coupe la session et le travail est perdu.

La carte graphique est prêtée gratuitement par Google. S'il n'y en a pas :
**Exécution → Modifier le type d'exécution → T4 GPU**, puis recommence.

<sub>IA libres utilisées : Real-ESRGAN (BSD-3-Clause) pour agrandir, RIFE 4.25 (MIT) pour
fluidifier. Ta vidéo reste dans ta session Colab et disparaît quand elle se ferme.</sub>
"""

REGLAGES = """
#@title 1 · Réglages
#@markdown **Taille du résultat** (une vidéo verticale de téléphone devient 2160 x 3840 en 4K)
TAILLE = "4K" #@param ["4K", "1440p", "1080p", "Garder la taille d'origine"]
#@markdown **Images par seconde** (60 = mouvement très fluide)
IMAGES_PAR_SECONDE = "60" #@param ["60", "30", "50", "25", "Garder"]
#@markdown **Genre de vidéo**
STYLE = "Vidéo filmée (rapide)" #@param ["Vidéo filmée (rapide)", "Dessin animé", "Vidéo filmée, finesse maximale (beaucoup plus lent)"]
#@markdown **Essai** : ne traiter que les 10 premières secondes, pour voir la qualité et le temps
ESSAI_10_SECONDES = False #@param {type:"boolean"}
#@markdown **Où est ta vidéo ?** (Google Drive marche partout, téléphone compris)
OU_EST_LA_VIDEO = "Dans mon Google Drive, dossier Video-HD" #@param ["Dans mon Google Drive, dossier Video-HD", "Je l'envoie depuis cet appareil (ordinateur)"]
#@markdown **Lissage** (vidéo filmée) : 0 = garde le grain et les textures fines, 100 = lisse tout
LISSAGE = 50 #@param {type:"slider", min:0, max:100, step:10}
#@markdown **Qualité du fichier** : 18 = plus beau mais plus lourd, 24 = plus léger
QUALITE = 20 #@param {type:"slider", min:16, max:26, step:1}
print("✅ Réglages pris en compte.")
"""

PREPARER = """
#@title 2 · Préparer la carte graphique et le moteur
import importlib, os, sys, torch

if not torch.cuda.is_available():
    raise SystemExit("❌ Pas de carte graphique. Menu Exécution → Modifier le type d'exécution → "
                     "choisis « T4 GPU », enregistre, puis relance tout (Ctrl + F9).")
carte = torch.cuda.get_device_properties(0)
print(f"✅ Carte graphique : {carte.name}, {carte.total_memory / 1e9:.0f} Go")

MOTEUR = r'''__MOTEUR__'''
with open("/content/video_hd.py", "w", encoding="utf-8") as f:
    f.write(MOTEUR)
if "/content" not in sys.path:
    sys.path.insert(0, "/content")
import video_hd
importlib.reload(video_hd)
print("✅ Moteur prêt (Real-ESRGAN + RIFE 4.25).")
"""

CHOISIR = """
#@title 3 · Choisir la vidéo
import glob, os

EXTENSIONS = (".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".3gp", ".mts", ".m2ts", ".wmv", ".flv")
DRIVE = OU_EST_LA_VIDEO.startswith("Dans mon Google Drive")

if DRIVE:
    from google.colab import drive
    drive.mount("/content/drive")
    DOSSIER_DRIVE = "/content/drive/MyDrive/Video-HD"
    os.makedirs(DOSSIER_DRIVE, exist_ok=True)
    videos = [f for f in glob.glob(DOSSIER_DRIVE + "/*") if f.lower().endswith(EXTENSIONS)]
    if not videos:
        raise SystemExit("Le dossier « Video-HD » de ton Google Drive est vide (je viens de le créer s'il "
                         "n'existait pas). Mets ta vidéo dedans (sur le téléphone : appli Drive → + → "
                         "Importer), attends la fin de l'envoi, puis relance : Exécution → Tout exécuter.")
    ENTREE = max(videos, key=os.path.getmtime)
    print("✅ Vidéo choisie (la plus récente du dossier Video-HD) :", os.path.basename(ENTREE))
else:
    from google.colab import files
    os.makedirs("/content/videos", exist_ok=True)
    os.chdir("/content")
    print("Choisis ta vidéo. Pour un gros fichier, l'envoi peut prendre plusieurs minutes.")
    recu = files.upload()
    if not recu:
        raise SystemExit("Aucune vidéo reçue.")
    nom = next(iter(recu))
    del recu
    ENTREE = os.path.join("/content/videos", nom)
    os.replace(os.path.join("/content", nom), ENTREE)
    print("✅ Vidéo reçue :", nom)
"""

LANCER = """
#@title 4 · Lancer le travail
import os, shutil

taille = {"4K": "4k", "1440p": "1440p", "1080p": "1080p"}.get(TAILLE, "garder")
ips = "garder" if IMAGES_PAR_SECONDE == "Garder" else IMAGES_PAR_SECONDE
style = "anime" if STYLE.startswith("Dessin") else ("max" if "finesse" in STYLE else "reel")
args = [ENTREE, "--taille", taille, "--ips", ips, "--style", style,
        "--qualite", str(QUALITE), "--debruitage", str(LISSAGE / 100), "--dossier", "/content/resultats", "--modeles", "/content/modeles"]
if ESSAI_10_SECONDES:
    args += ["--essai", "10"]

RESULTAT = video_hd.principal(args)

if DRIVE:
    os.makedirs(DOSSIER_DRIVE + "/resultats", exist_ok=True)
    copie = shutil.copy(RESULTAT, DOSSIER_DRIVE + "/resultats/")
    print("✅ Rangé dans ton Google Drive :", copie.replace("/content/drive/MyDrive/", ""))
else:
    from google.colab import files
    print("Téléchargement du résultat vers ton appareil…")
    try:
        files.download(RESULTAT)
    except Exception:  # noqa: BLE001 (le téléchargement direct échoue souvent sur téléphone)
        print("⚠️ Le téléchargement n'a pas démarré. Le fichier est ici, dans le panneau Fichiers à "
              "gauche :", RESULTAT, "\\nSur téléphone, choisis plutôt Google Drive dans la case 1.")
"""

carnet = {
    "nbformat": 4,
    "nbformat_minor": 0,
    "metadata": {
        "colab": {"name": "Video_HD.ipynb", "provenance": [], "gpuType": "T4"},
        "accelerator": "GPU",
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
    },
    "cells": [
        texte(INTRO),
        code(REGLAGES),
        code(PREPARER.replace("__MOTEUR__", MOTEUR)),
        code(CHOISIR),
        code(LANCER),
    ],
}

sortie = os.path.join(ICI, "Video_HD.ipynb")
with open(sortie, "w", encoding="utf-8", newline="\n") as f:
    json.dump(carnet, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("carnet écrit :", sortie, f"({os.path.getsize(sortie) // 1024} Ko)")

# -*- coding: utf-8 -*-
"""Prépare les huit photos du voyage, à partir des candidats moissonnés.

⚠️ CE SONT DE VRAIES PHOTOS DE VRAIS LIEUX, sous licence libre vérifiée sur
Wikimedia Commons. Elles remplacent l'atlas dessiné, qui n'était qu'une
attente. Aucune image générée n'entre ici, jamais.

⛔ DEUX CANDIDATS ONT ÉTÉ ÉCARTÉS D'OFFICE : une photo d'enfants à la Porte
   et un portrait rapproché d'un guide à Ouidah. Personne identifiable sans
   accord, et jamais un enfant. La règle passe avant la qualité de l'image.

⚠️ ATTRIBUTION OBLIGATOIRE. Les licences CC BY et CC BY-SA EXIGENT de citer
   l'auteur et la licence. Ce n'est pas une politesse, c'est la condition
   d'usage. Le pied de page les porte, et un contrôle le vérifie.
"""
import io
import json
import os
import re

from PIL import Image, ImageOps

ICI = os.path.dirname(os.path.abspath(__file__))
CAND = os.path.join(ICI, "_sources", "candidats")
IMG = os.path.join(ICI, "assets", "images", "lieux")

# station -> (dossier, fichier retenu, ce que la photo montre)
CHOIX = [
    ("porte", "porte", "08.jpg",
     "La Porte du Non-Retour, au bout de l'allée de sable, sur la plage d'Ouidah."),
    ("ouidah", "ouidah", "04.jpg",
     "Une case au toit de tuiles coniques, dans l'enceinte du temple des Pythons, à Ouidah."),
    ("cotonou", "cotonou", "02.jpg",
     "Le marché Dantokpa vu d'en haut : les parasols, les étals, la foule."),
    ("ganvie", "ganvie", "05.jpg",
     "Ganvié : les maisons sur pilotis alignées le long d'un chenal du lac Nokoué."),
    ("abomey", "abomey", "00.jpg",
     "Un bas-relief en terre du quartier de Gbécon-Hounli, à Abomey."),
    ("koutammakou", "koutammakou", "01.jpg",
     "Une Tata Somba : la maison-forteresse en terre des Batammariba, avec ses tourelles de chaume."),
    ("pendjari", "pendjari", "00.jpg",
     "Un baobab au bord d'un point d'eau, dans la savane sèche de la Pendjari."),
    ("fleuve", "fleuve", "02.jpg",
     "Les pirogues alignées sur la berge du fleuve Niger, à Malanville."),
]

LARGE = 1400          # le fond d'une station, en paysage large
# ⚠️ Une photo de FOND, posée sous un voile sombre et un grain, n'a pas
# besoin de qualité studio : à 78 la Pendjari faisait 405 Ko à elle seule,
# sur une page qui en pèse 189 en tout. À 66 la différence ne se voit pas.
QUAL = 66


def nettoyer(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


# certaines sources demandent un resserrement : le bas-relief d'Abomey est
# un tirage sur plaque, et son CADRE apparaissait dans l'image.
ZOOM = {"abomey": 1.30, "pendjari": 1.18}


def cadrer(im, larg, rapport=0.62, zoom=1.0):
    """Recadre au centre haut : sur une photo de lieu, le sujet est
    rarement en bas, et le bas reçoit le texte."""
    if zoom > 1.0:
        w, h = int(im.width / zoom), int(im.height / zoom)
        x, y = (im.width - w) // 2, (im.height - h) // 2
        im = im.crop((x, y, x + w, y + h))
    cible = larg, int(round(larg * rapport))
    r = max(cible[0] / im.width, cible[1] / im.height)
    im = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))),
                   Image.LANCZOS)
    x = (im.width - cible[0]) // 2
    y = int((im.height - cible[1]) * 0.34)
    return im.crop((x, y, x + cible[0], y + cible[1]))


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    fiche = json.loads(io.open(os.path.join(CAND, "fiche.json"),
                               encoding="utf-8").read())

    credits, total = [], 0
    for station, dossier, fichier, legende in CHOIX:
        src = os.path.join(CAND, dossier, fichier)
        if not os.path.exists(src):
            print("%-13s MANQUE %s" % (station, src))
            continue

        meta = next((x for x in fiche.get(dossier, [])
                     if x["fichier"] == fichier), None)
        if not meta:
            print("%-13s pas de fiche pour %s" % (station, fichier))
            continue

        # ⚠️ EXIF : sans `exif_transpose`, les photos prises au téléphone
        # arrivent COUCHÉES. Cinq candidats de Ganvié l'étaient.
        im = Image.open(src)
        im = ImageOps.exif_transpose(im).convert("RGB")
        im = cadrer(im, LARGE, zoom=ZOOM.get(station, 1.0))

        dst = os.path.join(IMG, station + ".webp")
        im.save(dst, "WEBP", quality=QUAL, method=6)
        t = os.path.getsize(dst)
        total += t

        # la version minuscule et floue, qui s'affiche pendant le
        # chargement ET sert de fondu : l'effet et la performance sont
        # la même chose (grammaire de la vidéo 3)
        pt = im.resize((28, int(28 * im.height / im.width)), Image.LANCZOS)
        dpt = os.path.join(IMG, station + "-min.webp")
        pt.save(dpt, "WEBP", quality=58, method=6)
        total += os.path.getsize(dpt)

        credits.append({
            "station": station,
            "legende": legende,
            "titre": nettoyer(meta["titre"].replace("File:", "")),
            "auteur": nettoyer(meta["auteur"]) or "auteur non précisé",
            "licence": meta["licence"],
            "page": meta["page"],
        })
        print("%-13s %-10s %4dx%-4d %6d o  %s"
              % (station, fichier, im.width, im.height, t, meta["licence"]))

    io.open(os.path.join(IMG, "credits.json"), "w", encoding="utf-8").write(
        json.dumps(credits, ensure_ascii=False, indent=1))
    print("\n%d photos, %.0f Ko au total (vignettes comprises)"
          % (len(credits), total / 1024.0))
    print("credits.json ecrit : l'attribution est OBLIGATOIRE en CC BY et CC BY-SA.")

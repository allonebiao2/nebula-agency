#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HILLARY M. STYL — les ONZE modèles reçus les 2026-08-16 et 17, prêts à entrer.

    python _nouveaux_modeles.py           dit ce qui manque, ne touche à rien
    python _nouveaux_modeles.py --poser   détoure, pose les images, injecte

POURQUOI CE FICHIER EXISTE
Hillary a envoyé onze modèles avec leurs prix, leurs délais et leur type de
mesures. **Tout est ici, sauf les photos** : elles ont été montrées dans une
conversation, elles ne sont jamais devenues des fichiers sur le disque. Ce
script garde les données au chaud pour que leur arrivée ne coûte qu'une
commande, et il REFUSE de travailler tant qu'une photo manque.

⛔ IL N'INVENTE RIEN. Pas de photo générée, pas de prix déduit, pas de nom
   fabriqué autrement que le descriptif provisoire validé par Mongazi.

COMMENT ON S'EN SERT
1. Les photos arrivent dans `_partage/`.
2. On les range, une par dossier : `_sources/modele-<clé>/photo.jpg`
   (deux photos si on a le dos : la principale d'abord dans l'ordre du nom).
3. `python _nouveaux_modeles.py --poser`
4. `python _v4/_assembler.py && python _build.py && python _qc.py`
"""
import io, json, os, re, sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ICI, "_sources")
IMG = os.path.join(ICI, "assets", "images")
MOTEUR = os.path.join(ICI, "_v4", "garde-moteur.js")
MOTION = os.path.join(ICI, "_v4", "motion.js")
COULEURS = os.path.join(ICI, "_v4", "_couleurs.json")

# ⚠️ LES DONNÉES SONT CELLES QU'ELLE A DONNÉES, MOT POUR MOT.
#    Prix normal, prix express TOTAL, délais, type de mesures. Les euros et
#    les dollars sont les siens : on ne les recalcule jamais.
#    Les noms sont provisoires : Mongazi a tranché le 2026-08-16, « on garde,
#    elle corrigera ce qui ne lui va pas ».
#    `indice` sert à reconnaître la photo au moment de la ranger.
MODELES = [
    dict(cle="organza", id="h10", nom="Robe Organza",
         prix=40000, expPrix=55000, eur=60, usd=72, eurExp=82, usdExp=100,
         type="robe_ovale", tag="Cérémonie",
         indice="robe rouge à motifs blancs, col en organza blanc froncé, jupon d'organza — fond JAUNE, deux vues : face et dos (la face est arrivée le 17/08)",
         ds="Manches ballon détachées des épaules, col en organza froncé, découpe à la taille, dos lacé au ruban et jupon d'organza sous un wax rouge."),
    dict(cle="noeud", id="h11", nom="Ensemble Nœud",
         prix=25000, expPrix=35000, eur=37, usd=45, eurExp=52, usdExp=63,
         type="haut_pantalon", tag="",
         indice="haut dos nu à col, noué dans le dos, et pantalon large rouge — face et dos",
         ds="Haut dos nu à col, noué dans le dos, et pantalon large avec un pan de wax rouge et blanc."),
    dict(cle="lacee", id="h12", nom="Robe Lacée",
         prix=35000, expPrix=45000, eur=52, usd=63, eurExp=67, usdExp=81,
         type="robe_ovale", tag="",
         indice="robe wax violet à éventails bleu et blanc, sur mannequin, dos lacé — face et dos",
         ds="Épaules dénudées à fines bretelles, manches ballon, basque à la taille, dos lacé au ruban."),
    dict(cle="coeurs", id="h13", nom="Tailleur Cœurs",
         prix=50000, expPrix=65000, eur=75, usd=90, eurExp=99, usdExp=115,
         type="haut_pantalon", tag="Fait main",
         indice="tailleur bordeaux à cœurs blancs, veste cintrée et pantalon large, sur mannequin",
         ds="Veste cintrée à revers et épaules structurées, pantalon large assorti, wax bordeaux à cœurs."),
    dict(cle="jean", id="h14", nom="Ensemble Jean",
         prix=35000, expPrix=45000, eur=52, usd=63, eurExp=67, usdExp=81,
         type="haut_jupe", tag="",
         indice="haut court et jupe à volants montée sur un empiècement en JEAN — deux mannequins",
         ds="Haut court épaules dénudées à manches ballon, jupe longue à volants montée sur un empiècement en jean."),
    dict(cle="sirene", id="h15", nom="Robe Sirène",
         prix=40000, expPrix=55000, eur=60, usd=72, eurExp=82, usdExp=100,
         type="robe_droite", tag="Cérémonie",
         indice="fourreau violet à volants bleu roi, traîne, foulard assorti — ⛔ prendre la vue de PROFIL, celle de face porte un cœur collé",
         ds="Fourreau en wax violet, volants bleu roi en bordure et le long de la fente, traîne et foulard assorti."),
    dict(cle="emeraude", id="h16", nom="Robe Émeraude",
         prix=25000, expPrix=35000, eur=37, usd=45, eurExp=52, usdExp=63,
         type="haut_jupe", tag="",
         indice="robe courte verte et jaune à manches longues, fond blanc",
         ds="Coupe courte ajustée, manches longues, grands motifs verts et jaunes cernés de noir."),
    dict(cle="orange-uni", id="h17", nom="Ensemble Orange",
         prix=35000, expPrix=45000, eur=52, usd=63, eurExp=67, usdExp=81,
         type="haut_pantalon", tag="",
         indice="tissu UNI orange, bustier froncé à lien au cou, découpes à la taille (⚠️ le sac beige n'est pas la pièce)",
         ds="Bustier froncé à lien au cou, découpes sur les côtés, bas long et très ample en tissu uni."),
    dict(cle="soleil", id="h18", nom="Robe Soleil",
         prix=25000, expPrix=35000, eur=37, usd=45, eurExp=52, usdExp=63,
         type="robe_ovale", tag="Cérémonie",
         indice="robe longue bazin tie-dye ROUGE ET OR, épaules drapées à pompons, sur mannequin",
         ds="Épaules drapées à cordons et pompons, ceinture drapée, jupe très ample en bazin teint rouge et or."),
    dict(cle="ete", id="h19", nom="Robe d'été",
         prix=35000, expPrix=45000, eur=52, usd=63, eurExp=67, usdExp=81,
         type="robe_ovale", tag="Plage",
         indice="DEUX mannequins, haut court noué au cou + jupe longue : bazin tie-dye brun et jaune à médaillons roses, et tie-dye orange et bleu — capture d'écran, bandes noires à couper",
         ds="Haut court noué au cou et jupe longue très ample, en bazin teint. La pièce d'été, qui va de la plage au déjeuner."),
    dict(cle="volants", id="h20", nom="Ensemble Volants",
         prix=40000, expPrix=55000, eur=60, usd=72, eurExp=82, usdExp=100,
         type="haut_pantalon", tag="",
         indice="haut court noué devant à MANCHES A TROIS VOLANTS, bazin tie-dye rouge et blanc, + pantalon tres evase en JEAN a empiecements rouges — face et dos, un seul mannequin",
         ds="Haut court noué devant, manches à trois volants étagés, et pantalon très évasé en jean à empiècements de bazin teint."),
]

# Les trois qui iront au héros quand elles seront là : les plus fortes, et
# trois couleurs qui ne se doublent pas.
HEROS = ["lacee", "coeurs", "soleil"]

JMIN = JMAX = 14          # deux semaines fermes, pour les dix
EXPMIN, EXPMAX = 2, 4     # « 2 à 4 jours », pour les dix


def dossier(m):
    return os.path.join(SRC, "modele-" + m["cle"])


def photos(m):
    d = dossier(m)
    if not os.path.isdir(d):
        return []
    return sorted(f for f in os.listdir(d)
                  if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))


def etat():
    prets, manquants = [], []
    for m in MODELES:
        (prets if photos(m) else manquants).append(m)
    return prets, manquants


def dire():
    prets, manquants = etat()
    print(f"\n  {len(prets)} modèle(s) prêt(s), {len(manquants)} en attente de photo.\n")
    for m in manquants:
        os.makedirs(dossier(m), exist_ok=True)   # pour qu'il se voie dans l'explorateur
        print(f"  ⛔ {m['nom']:<18} {m['prix']:>6} F   {dossier(m)[len(ICI)+1:]}/")
        print(f"     à reconnaître : {m['indice']}")
    for m in prets:
        print(f"  ✅ {m['nom']:<18} {m['prix']:>6} F   {len(photos(m))} photo(s)")
    if manquants:
        print("\n  Rien n'a été modifié. Déposez les photos dans les dossiers"
              "\n  ci-dessus, puis relancez avec --poser.\n")
    return prets, manquants


def teinte(chemin):
    """La teinte dominante du tissu, comme pour les pièces déjà en ligne.
    ⚠️ Seuil de saturation à 0,22 : à 0,35 les tissus sourds (le sauge de la
    robe verte) étaient écartés et deux pièces tombaient sur la même nappe."""
    import colorsys
    from collections import defaultdict
    from PIL import Image
    im = Image.open(chemin).convert("RGBA")
    im = im.resize((max(1, im.width // 3), max(1, im.height // 3)), Image.LANCZOS)
    px = im.load()
    seaux = defaultdict(list)
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a < 220:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if s < 0.22 or v < 0.18 or v > 0.92:
                continue
            seaux[int(h * 360) // 12].append((r, g, b))
    if not seaux:
        return "#6b3065"
    p = seaux[max(seaux, key=lambda k: len(seaux[k]))]
    r = sum(x[0] for x in p) / len(p)
    g = sum(x[1] for x in p) / len(p)
    b = sum(x[2] for x in p) / len(p)
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    v = min(0.68, max(0.42, v))
    s = min(0.85, max(0.42, s))
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def poser_images(prets):
    """Détoure et pose, exactement comme `_detourer.py` : même hauteur, même
    encodage. On ne réencode jamais une image déjà posée."""
    from rembg import new_session, remove
    from PIL import Image
    session = new_session("isnet-general-use")
    faits = []
    for m in prets:
        for rang, f in enumerate(photos(m)[:2]):
            suffixe = "" if rang == 0 else "-dos"
            dest = os.path.join(IMG, f"piece-{m['cle']}{suffixe}.webp")
            if os.path.exists(dest):
                print(f"     {os.path.basename(dest)} déjà posée")
                continue
            with open(os.path.join(dossier(m), f), "rb") as fh:
                im = Image.open(io.BytesIO(remove(fh.read(), session=session))).convert("RGBA")
            bb = im.getbbox()
            if bb:
                im = im.crop(bb)
            haut = min(950 if rang == 0 else 760, im.height)
            r = haut / float(im.height)
            im = im.resize((max(1, int(round(im.width * r))), haut), Image.LANCZOS)
            im.save(dest, "WEBP", quality=94, alpha_quality=100, method=6, exact=True)
            print(f"     {os.path.basename(dest)} — {os.path.getsize(dest)//1024} Ko")
        faits.append(m)
    return faits


def injecter(faits):
    """Ajoute les pièces au catalogue, au carrousel et, pour les meilleures,
    au héros. Idempotent : une pièce déjà présente n'est pas doublée."""
    mot = io.open(MOTEUR, encoding="utf-8").read()
    mtn = io.open(MOTION, encoding="utf-8").read()
    coul = json.load(io.open(COULEURS, encoding="utf-8"))
    ajouts = 0

    for m in faits:
        if f'id:"{m["id"]}"' in mot:
            print(f"     {m['nom']} déjà au catalogue")
            continue
        img = f"piece-{m['cle']}.webp"
        img2 = f"piece-{m['cle']}-dos.webp"
        a_dos = os.path.exists(os.path.join(IMG, img2))
        fiche = (
            f'\n  {{id:"{m["id"]}", cat:"sm", nom:"{m["nom"]}", type:"{m["type"]}", tag:"{m["tag"]}",\n'
            f'   img:"{img}"' + (f', img2:"{img2}"' if a_dos else "") + ",\n"
            f'   prix:{m["prix"]}, jmin:{JMIN}, jmax:{JMAX}, expPrix:{m["expPrix"]}, '
            f'expMin:{EXPMIN}, expMax:{EXPMAX},\n'
            f'   eur:{m["eur"]}, usd:{m["usd"]}, eurExp:{m["eurExp"]}, usdExp:{m["usdExp"]},\n'
            f'   ds:"{m["ds"]}"}},'
        )
        # on insère juste avant la « Création libre », qui doit rester la dernière
        ancre = '  /* Une CRÉATION LIBRE'
        if ancre not in mot:
            sys.exit("⛔ ancre du catalogue introuvable : injection annulée")
        mot = mot.replace(ancre, fiche.lstrip("\n") + "\n\n" + ancre, 1)

        coul["piece-" + m["cle"]] = teinte(os.path.join(IMG, img))
        ajouts += 1

    # le carrousel prend TOUTES les pièces, le héros seulement les meilleures
    for m in faits:
        img = f"piece-{m['cle']}.webp"
        if img in mtn:
            continue
        fin_coll = mtn.index("  ];", mtn.index("var COLLECTIONS = ["))
        ligne = ("    { f:'%s', l:'%s', t:\"%s\", s:'%s' }"
                 % (img, m["tag"] or "Sur-mesure", m["nom"], m["ds"][:56]))
        mtn = (mtn[:fin_coll].rstrip().rstrip(",") + ",\n" + ligne + "\n"
               + mtn[fin_coll:])
        if m["cle"] in HEROS:
            fin_hero = mtn.index("  ];", mtn.index("var HERO = ["))
            h = ("    { f:'%s', c:'%s', col:'%s', mat:'Sur-mesure · 2 semaines',\n"
                 "      t:\"%s\", d:\"%s\" }"
                 % (img, coul["piece-" + m["cle"]], m["tag"] or "Sur-mesure",
                    m["nom"], m["ds"]))
            mtn = (mtn[:fin_hero].rstrip().rstrip(",") + ",\n" + h + "\n"
                   + mtn[fin_hero:])

    io.open(MOTEUR, "w", encoding="utf-8", newline="\n").write(mot)
    io.open(COULEURS, "w", encoding="utf-8", newline="\n").write(
        json.dumps(coul, ensure_ascii=False, indent=1) + "\n")
    print(f"\n  {ajouts} pièce(s) ajoutée(s) au catalogue.")
    print("  Carrousel : toutes. Héros : " + ", ".join(HEROS) + ".")
    print("  ⚠️ Regarder le résultat AVANT de déployer : une photo mal détourée")
    print("     se voit au héros, jamais dans un contrôle.")
    print("  Ensuite : python _v4/_assembler.py && python _build.py && python _qc.py")


def main():
    prets, manquants = dire()
    if "--poser" not in sys.argv:
        return 0
    if manquants:
        print("  ⛔ On ne pose rien tant qu'il manque une photo : un catalogue")
        print("     à moitié rempli est pire qu'un catalogue qui attend.\n")
        return 1
    print("\n  Détourage et pose…")
    injecter(poser_images(prets))
    return 0


if __name__ == "__main__":
    sys.exit(main())

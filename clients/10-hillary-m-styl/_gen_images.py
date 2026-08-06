#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HILLARY M. STYL — génération des visuels via WaveSpeed (Nano Banana Pro).

    python _gen_images.py hero        4 mannequins, FOND BLANC UNI impératif
    python _gen_images.py atelier     3 plans : tissu, patron, finition
    python _gen_images.py lookbook    6 vues éditoriales
    python _gen_images.py collections 6 pièces sur fond neutre clair
    python _gen_images.py tout        les 19

Les images tombent dans `_sources/ia/`. Elles n'entrent dans le site qu'après
avoir été REGARDÉES et choisies, puis mises au web par `_pose_images.py`.

⚠️ 0,14 $ l'image. Le script affiche le coût et refuse si le solde ne suffit pas.

⛔ CE QUI NE SERA JAMAIS GÉNÉRÉ : les photos du CATALOGUE COMMANDABLE (`PIECES`
   du moteur). Elles portent un prix, un délai et un bouton de commande. Une
   cliente qui verse un acompte sur une robe qui n'existe pas, c'est la maison
   qui répond. Le carrousel des collections, lui, n'a ni prix ni bouton : une
   image de préfiguration y est tenable, et elle est marquée comme telle.
"""
import os, sys, io, json, time, urllib.request, urllib.error

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(RACINE, "_sources", "ia")
MODELE = "google/nano-banana-pro/text-to-image"
PRIX = 0.14


def cle():
    p = os.path.abspath(os.path.join(RACINE, "..", "..", "secrets", "wavespeed.env"))
    for l in io.open(p, encoding="utf-8"):
        if l.startswith("WAVESPEED_API_KEY="):
            return l.split("=", 1)[1].strip()
    raise SystemExit("clé WaveSpeed introuvable dans secrets/wavespeed.env")


# --- ce qui rend la série cohérente -------------------------------------
# ⚠️ « West African », « Beninese » écrits EXPLICITEMENT : le modèle
#    occidentalise par défaut (leçon Angy Art, 2026-08-05).
QUI = ("a Beninese West African woman with dark brown skin, natural hair or a "
       "wax-print headwrap, calm confident posture, ")
TISSU = ("authentic West African wax print / pagne fabric with bold geometric "
         "and organic motifs in indigo, terracotta, ochre and deep green, ")
NEG = ("No text, no lettering, no signature, no watermark, no logo, no brand mark, "
       "no border, no frame. ")

# --- 1 · LE HÉROS : le fond blanc uni décide de tout --------------------
# Sans lui, le numéro géant ne peut pas passer derrière le mannequin et le nom
# de la maison ne peut pas la chevaucher. C'est la contrainte n° 1 du brief.
FOND_BLANC = ("Full-length studio fashion photograph, the model standing centred "
              "against a completely plain seamless pure white studio background, "
              "no props, no furniture, no visible floor line, soft even diffused "
              "studio lighting with a gentle shadow at the feet only. Shot on an "
              "85mm lens, f/5.6, sharp, high-end lookbook quality. Vertical 4:5. ")

HERO = [
  ("hero-1", "4:5", QUI + "wearing a made-to-measure fitted dress in deep indigo "
   "fabric with clean tailored seams, hem at mid-calf. " + FOND_BLANC + NEG),
  ("hero-2", "4:5", QUI + "wearing a flowing boubou in " + TISSU
   + "cut wide with a fitted shoulder. " + FOND_BLANC + NEG),
  ("hero-3", "4:5", QUI + "wearing a simple ready-to-wear two-piece: a plain "
   "cream shirt and wide dark trousers, understated. " + FOND_BLANC + NEG),
  ("hero-4", "4:5", QUI + "wearing an elaborate ceremony gown in " + TISSU
   + "with a structured bodice and a long full skirt. " + FOND_BLANC + NEG),
]

# --- 2 · L'ATELIER : trois plans rapprochés, fond sombre ---------------
ATELIER = [
  ("atelier-1", "3:4",
   "Close-up photograph of rolls of " + TISSU + "stacked and standing upright in "
   "a tailor's workshop, folded edges and selvedges visible, the patterns crisp. "
   "Warm low side light raking across the folds, deep shadow behind. Shot on an "
   "85mm lens, f/4, shallow depth of field, tactile, editorial. " + NEG),
  ("atelier-2", "3:4",
   "Close-up photograph of a tailor's cutting table: a paper dress pattern pinned "
   "to dark fabric, tailor's chalk, a measuring tape, fabric shears and pins. "
   "A dark-skinned hand resting at the edge of the frame, face out of frame. "
   "Warm low side light, deep shadow. Shot on a 50mm lens, f/2.8. " + NEG),
  ("atelier-3", "3:4",
   "Extreme close-up photograph of a finished seam and hand embroidery on "
   + TISSU + "the stitches crisp and regular, a needle still in the cloth. "
   "Warm raking light, deep shadow, every thread visible. Shot on a 100mm macro "
   "lens, f/5.6, extremely detailed. " + NEG),
]

# --- 4 · LE LOOKBOOK : éditorial, formats variés ----------------------
#     Elles s'affichent en noir et blanc et reprennent leurs couleurs au survol,
#     donc on génère EN COULEUR.
LOOK = [
  ("look-1", "4:5", QUI + "photographed full length walking, wearing a long dress in "
   + TISSU + "the fabric caught mid-movement. Editorial fashion photograph in a "
   "bright plain room, warm daylight from a tall window on the left, plain pale "
   "wall behind. Shot on a 50mm lens, f/2, natural light. " + NEG),
  ("look-2", "1:1",
   "Extreme close-up detail of " + TISSU + "draped and folded, the weave and the "
   "printed motif filling the frame. Warm raking light from the left, every fibre "
   "visible. Shot on a 100mm macro lens, f/8. " + NEG),
  ("look-3", "3:4", QUI + "photographed from behind, from the shoulders down, wearing "
   "a dress in " + TISSU + "the back seam and the tie at the waist visible. Plain "
   "pale wall, warm side light. Shot on an 85mm lens, f/2.8. " + NEG + "Face not visible."),
  ("look-4", "4:5", QUI + "seated on a plain wooden stool, wearing a tailored jacket "
   "and skirt in deep indigo, hands resting in her lap. Bright plain room, warm "
   "daylight from the side. Shot on a 50mm lens, f/2. " + NEG),
  ("look-5", "5:4",
   "Wide photograph of a tailor's workshop in Cotonou, empty of people: a sewing "
   "machine on a wooden table, folds of " + TISSU + "a dress form, spools of thread, "
   "shears. Warm afternoon light entering hard from a window on the left, dust in "
   "the beam, deep shadow on the right. Shot on a 35mm lens, f/5.6. " + NEG),
  ("look-6", "3:4",
   "Extreme close-up of a hand-finished detail on a garment: a covered button, a "
   "rolled hem and a line of hand stitching on " + TISSU + "A dark-skinned "
   "fingertip at the edge of the frame. Warm raking light, deep shadow. Shot on a "
   "100mm macro lens, f/5.6. " + NEG + "Face not visible."),
]

# --- 3 · LES COLLECTIONS : socle identique, une ligne qui change -------
#     ⚠️ Ces images vont dans le CARROUSEL (sans prix, sans bouton de commande),
#        jamais dans le catalogue commandable.
SOCLE_COLL = (
  "Studio product photograph of a single finished garment presented on a plain "
  "dress form, centred, shot square-on against a seamless very light warm grey "
  "background. Soft large key light from the upper left at a low angle to reveal "
  "the fabric texture and the fall of the cloth, subtle fill from the right, no "
  "hotspots. Identical lighting, distance and framing across the whole series. "
  "Shot on an 85mm lens, f/8, colour-accurate, high-end catalogue quality. "
  "Vertical 4:5. ")
COLL = [
  ("coll-1", "PIÈCE: a fitted dress cut at the waist, deep indigo fabric, clean seams"),
  ("coll-2", "PIÈCE: a straight column dress in plain black fabric, long sleeves"),
  ("coll-3", "PIÈCE: a two-piece set, top and wrap skirt, in " + TISSU.rstrip(', ')),
  ("coll-4", "PIÈCE: a simple cream shirt with a sharp collar and covered buttons"),
  ("coll-5", "PIÈCE: wide high-waisted trousers in dark fabric, sharp crease"),
  ("coll-6", "PIÈCE: a ceremony gown with a structured bodice and a long full skirt in "
   + TISSU.rstrip(', ')),
]

LOTS = {
  "hero": HERO,
  "atelier": ATELIER,
  "lookbook": LOOK,
  "collections": [(n, "4:5", SOCLE_COLL + v + ". " + NEG + "No human figure, no face, no hands.")
                  for n, v in COLL],
}


def poste(url, corps, k):
    r = urllib.request.Request(url, data=json.dumps(corps).encode(),
        headers={"Authorization": "Bearer " + k, "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=120) as h:
        return json.loads(h.read())


def lit(url, k):
    r = urllib.request.Request(url, headers={"Authorization": "Bearer " + k})
    with urllib.request.urlopen(r, timeout=60) as h:
        return json.loads(h.read())


def solde(k):
    return lit("https://api.wavespeed.ai/api/v3/balance", k)["data"]["balance"]


def generer(k, nom, ratio, prompt):
    try:
        r = poste(f"https://api.wavespeed.ai/api/v3/{MODELE}",
                  {"prompt": prompt, "aspect_ratio": ratio, "resolution": "2k"}, k)
    except urllib.error.HTTPError as e:
        print(f"  [KO] {nom} : {e.code} {e.read()[:180].decode(errors='replace')}")
        return None
    ident = r["data"]["id"]
    for _ in range(100):
        time.sleep(3)
        d = lit(f"https://api.wavespeed.ai/api/v3/predictions/{ident}/result", k)["data"]
        if d["status"] == "completed":
            os.makedirs(SORTIE, exist_ok=True)
            p = os.path.join(SORTIE, nom + ".png")
            urllib.request.urlretrieve(d["outputs"][0], p)
            print(f"  [ok] {nom:<14} {ratio:<5} {os.path.getsize(p)//1024:>5} Ko")
            return p
        if d["status"] == "failed":
            print(f"  [KO] {nom} : {str(d.get('error'))[:180]}")
            return None
    print(f"  [KO] {nom} : délai dépassé")
    return None


def lot(k, travaux):
    cout = len(travaux) * PRIX
    s = solde(k)
    print(f"{len(travaux)} images × {PRIX} $ = {cout:.2f} $   (solde {s:.2f} $)\n")
    if s < cout:
        raise SystemExit("solde insuffisant")
    faits = [generer(k, n, r, p) for n, r, p in travaux]
    print(f"\n{len([f for f in faits if f])}/{len(travaux)} produites → _sources/ia/")
    print(f"solde restant : {solde(k):.2f} $")


if __name__ == "__main__":
    k = cle()
    quoi = sys.argv[1] if len(sys.argv) > 1 else ""
    if quoi == "tout":
        lot(k, LOTS["hero"] + LOTS["atelier"] + LOTS["lookbook"] + LOTS["collections"])
    elif quoi in LOTS:
        lot(k, LOTS[quoi])
    else:
        print(__doc__)
        print("lots :", ", ".join(LOTS), "· tout")

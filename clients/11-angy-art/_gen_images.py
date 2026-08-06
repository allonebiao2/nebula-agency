#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANGY ART — génération des visuels via WaveSpeed (Nano Banana Pro).

    python _gen_images.py scenes      les 5 scènes d'ambiance, 2 variantes chacune
    python _gen_images.py oeuvres     les 8 pièces du carrousel
    python _gen_images.py <clé>       une seule, par son nom

Les images tombent dans `_sources/ia/`. Elles n'entrent dans le site qu'après
avoir été REGARDÉES et choisies, puis converties en WebP par `_pose_images.py`.

⚠️ Chaque appel coûte 0,14 $. Le script affiche le coût avant de lancer et
   refuse de tourner si le solde ne suffit pas.
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

# --- la clé vit dans secrets/, jamais ici ---------------------------------
def cle():
    p = os.path.join(RACINE, "..", "..", "secrets", "wavespeed.env")
    for l in io.open(os.path.abspath(p), encoding="utf-8"):
        if l.startswith("WAVESPEED_API_KEY="):
            return l.split("=", 1)[1].strip()
    raise SystemExit("clé WaveSpeed introuvable dans secrets/wavespeed.env")


# --- le socle commun : c'est lui qui rend la série cohérente --------------
LUMIERE = (
    "Hard raking light coming from the far left at a very low angle, grazing every "
    "surface so relief and texture read as sculpture, long shadows, deep falloff into "
    "near-black on the right. Palette: deep charcoal black, bone cream, burnt ochre, "
    "raw umber and warm brushed gold. Natural colour grade, no artificial saturation. "
)
NEG = ("No text, no lettering, no signature, no watermark, no logo, no border, no frame. ")

SCENES = {
  "hero": ("4:5",
    "Extreme macro photograph of a hand-made contemporary African abstract relief "
    "painting surface. Thick impasto ridges and deep hand-carved incisions forming "
    "concentric arcs and chevron marks inspired by traditional West African "
    "scarification. Raw linen canvas weave visible where the paint thins out. "
    "Fragments of coarse textile embedded in the paint. "
    + LUMIERE +
    "Shot on a 100mm macro lens, f/5.6, tack sharp on the relief, fine art photography, "
    "museum quality. Vertical composition. " + NEG + "No human figure."),

  "demarche": ("4:5",
    "Documentary fine art photograph of a Black West African woman artist's hands at "
    "work in her studio. Hands and forearms only, face and body out of frame. Fingers "
    "pressing thick ochre pigment into the raised surface of a textured painting, a worn "
    "palette knife beside them, dried pigment under the fingernails. Old brushes in a "
    "clay jar, a folded piece of indigo cloth and raw pigment powder softly out of focus "
    "behind. Raw linen canvas. "
    + LUMIERE +
    "Soft warm window light, dust floating in the beam. Shot on a 50mm lens, f/2.8, "
    "shallow depth of field. Vertical composition. " + NEG + "No visible face."),

  "atelier": ("16:9",
    "Wide architectural photograph of a contemporary artist's studio-gallery in West "
    "Africa, empty of people. Textured off-white plaster walls, polished concrete floor. "
    "Three large abstract relief paintings in ochre, charcoal and indigo hanging spaced "
    "apart on the main wall. One tall wooden easel on the left. A low table with jars of "
    "raw pigment, folded cloth and brushes. "
    + LUMIERE +
    "Late afternoon sun entering hard from a tall window on the far left, a long bright "
    "beam on the floor, dust suspended in the light. Shot on a 24mm lens, f/8, "
    "architectural photography, no lens distortion. " + NEG + "No people, no signage."),

  "vernissage": ("4:5",
    "Intimate photograph of two West African visitors seen from behind, a woman in an "
    "elegant dark wax-print dress with a headwrap and a man in a simple dark shirt, "
    "standing close together in front of a large dark abstract relief painting in a "
    "gallery in Cotonou. Dark brown skin, understated elegance, the woman holding a "
    "glass. They are silhouetted, faces not visible, slightly out of focus. The painting "
    "is sharp, its carved surface catching a single warm "
    "picture light from above-left in ridges of ochre and copper against near-black. "
    "The rest of the room falls into deep shadow. Warm tungsten glow, hushed evening "
    "atmosphere, no crowd. Shot on a 35mm lens, f/2, shallow depth of field, cinematic, "
    "natural available-light look. Vertical composition. "
    + NEG + "No visible faces, no branding."),

  "soir": ("16:9",
    "Wide photograph of a West African artist's studio-gallery at night, empty of people. "
    "Warm tungsten picture lights glowing low over two large relief paintings on a "
    "textured plaster wall, pools of amber light falling off fast into near-total "
    "darkness. A single work light on a stand casting a hard raking beam across the wall "
    "texture. Canvases stacked leaning against the wall in the shadows. Polished concrete "
    "floor reflecting the warm pools of light. Deep amber and near-black, almost no "
    "mid-tones. Intimate, quiet, after-hours atmosphere. Shot on a 35mm lens, f/2, "
    "long-exposure feel, cinematic colour grade. " + NEG + "No people, no signage."),
}

# --- le carrousel : socle identique, seule la VARIANTE change -------------
SOCLE_OEUVRE = (
    "Frontal catalogue photograph of a contemporary African abstract relief artwork, "
    "centred, shot perfectly square-on, floating against a seamless neutral dark grey "
    "background. Mixed media on raw linen: thick impasto, carved grooves, embedded "
    "textile fragments and applied materials. Soft large key light from the upper left "
    "at a low 20 degree angle to reveal the surface relief, plus a very subtle fill from "
    "the right, no hotspots, no reflections. Identical studio lighting, identical camera "
    "distance and framing across the whole series. Shot on an 85mm lens, f/11, "
    "edge-to-edge sharp, colour-accurate art documentation. "
)
OEUVRES = [
  ("oeuvre-1", "4:5", "concentric arcs carved into a burnt ochre ground, brushed gold catching the ridges"),
  ("oeuvre-2", "1:1", "dense vertical chevron incisions, deep indigo and charcoal, thin white kaolin lines"),
  ("oeuvre-3", "3:4", "a raised oval mask-like form emerging from the surface, raw umber and bone white"),
  ("oeuvre-4", "5:4", "strips of woven indigo textile embedded in cracked terracotta impasto"),
  ("oeuvre-5", "4:5", "radiating scarification marks around a dark centre, black on black with gold glints"),
  ("oeuvre-6", "1:1", "horizontal strata of pigment like eroded earth, ochre, rust and ash grey"),
  ("oeuvre-7", "3:4", "a grid of small carved squares, some filled with gold, on a deep crimson ground"),
  ("oeuvre-8", "4:5", "interlacing raised lines like a woven pattern, kaolin white on charcoal"),
]


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
    """Lance un rendu, attend, télécharge. Rend le chemin ou None."""
    try:
        r = poste(f"https://api.wavespeed.ai/api/v3/{MODELE}",
                  {"prompt": prompt, "aspect_ratio": ratio, "resolution": "2k"}, k)
    except urllib.error.HTTPError as e:
        print(f"  [KO] {nom} : {e.code} {e.read()[:180].decode(errors='replace')}")
        return None
    ident = r["data"]["id"]
    for _ in range(90):
        time.sleep(3)
        d = lit(f"https://api.wavespeed.ai/api/v3/predictions/{ident}/result", k)["data"]
        if d["status"] == "completed":
            u = d["outputs"][0]
            os.makedirs(SORTIE, exist_ok=True)
            p = os.path.join(SORTIE, nom + ".png")
            urllib.request.urlretrieve(u, p)
            ko = os.path.getsize(p) // 1024
            print(f"  [ok] {nom:<16} {ratio:<5} {ko:>5} Ko")
            return p
        if d["status"] == "failed":
            print(f"  [KO] {nom} : {str(d.get('error'))[:180]}")
            return None
    print(f"  [KO] {nom} : délai dépassé")
    return None


def lot(k, travaux):
    cout = len(travaux) * PRIX
    s = solde(k)
    print(f"{len(travaux)} images × {PRIX} $ = {cout:.2f} $   (solde {s:.2f} $)")
    if s < cout:
        raise SystemExit("solde insuffisant")
    print()
    faits = [generer(k, n, r, p) for n, r, p in travaux]
    reussis = [f for f in faits if f]
    print(f"\n{len(reussis)}/{len(travaux)} images produites → _sources/ia/")
    print(f"solde restant : {solde(k):.2f} $")


if __name__ == "__main__":
    k = cle()
    quoi = sys.argv[1] if len(sys.argv) > 1 else ""
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 2

    if quoi == "scenes":
        t = []
        for nom, (r, p) in SCENES.items():
            for i in range(1, n + 1):
                t.append((f"{nom}-{i}", r, p))
        lot(k, t)
    elif quoi == "oeuvres":
        lot(k, [(nom, r, SOCLE_OEUVRE + "VARIATION: " + v + ". " + NEG
                 + "No human figure, no wall, no frame.") for nom, r, v in OEUVRES])
    elif quoi in SCENES:
        r, p = SCENES[quoi]
        lot(k, [(f"{quoi}-{i}", r, p) for i in range(1, n + 1)])
    else:
        print(__doc__)
        print("scènes :", ", ".join(SCENES))

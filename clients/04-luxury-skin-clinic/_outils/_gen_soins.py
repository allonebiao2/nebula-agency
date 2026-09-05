# -*- coding: utf-8 -*-
"""
LES IMAGES DE SOINS — le geste, pas la matiere.

    python _outils/_gen_soins.py             # genere ce qui manque
    python _outils/_gen_soins.py --poser     # remplace les bandes actuelles

⛔ CE SCRIPT NE PEUT PAS TOURNER AUJOURD'HUI : le solde WaveSpeed est tombe a
   0,03 $ le 2026-09-05 (19 images produites dans la journee, ~2,66 $), et le
   compte Higgsfield est a 0 credit. Rechargez WaveSpeed, relancez la commande
   ci-dessus : rien d'autre n'est a faire.

POURQUOI CE SCRIPT EXISTE
   Les bandes en place montrent des MATIERES (goutte de serum, cristaux de
   gommage, soie, marbre, halo). Mongazi a demande le 2026-09-05 que les
   images « mettent en avant les soins, les massages, l'esthetique ». Ce sont
   donc des GESTES DE SOIN, en photo d'ambiance editoriale.

⛔ LA LIGNE QUI N'EST PAS FRANCHIE, ET POURQUOI
   . aucun AVANT / APRES, jamais : ce serait un resultat fabrique, et une
     cliente qui reserve sur un resultat invente, c'est la maison qui paie.
   . aucun VISAGE en gros plan presente comme le resultat d'un soin, pour la
     meme raison. Un visage peut etre partiellement dans le cadre pendant le
     geste, jamais en portrait « apres soin ».
   . aucune vue large d'une cabine presentee comme l'institut de Gloria :
     on cadre le geste, la matiere, le linge — pas un lieu qui pretendrait
     etre le sien.
   . la vraie photo de son institut et de ses soins reste le dernier palier,
     celui qu'on ne peut pas franchir a sa place. Ces images l'attendent.

⚠️ LA PEAU EST OUEST-AFRICAINE, ET C'EST ECRIT. Le modele occidentalise par
   defaut (leçon Angy Art du 2026-08-05) : sans la phrase, il rend des mains
   claires a une clientele qui ne l'est pas.
"""
import argparse, io, json, os, re, shutil, sys, time, urllib.request
from PIL import Image

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(RACINE, "assets", "images", "clinic", "soins")
FINAL = os.path.join(RACINE, "assets", "images", "clinic")
SECRET = os.path.join(RACINE, "..", "..", "secrets", "wavespeed.env")
MODELE = "google/nano-banana-pro/text-to-image"

SOCLE = (
    "Editorial photograph inside a high-end aesthetic clinic. {sujet}. "
    "All people are West African with deep brown skin. "
    "Soft directional light raking from the upper left, warm and clean, palette of pearl "
    "cream, ivory, antique gold and pale mint green. Shot on a 85mm lens at f/2.8, shallow "
    "depth of field, calm and expensive, uncluttered. "
    "No before-and-after, no split image, no close-up portrait, no eye contact, "
    "no text, no lettering, no signature, no watermark, no logo, no branding."
)

IMAGES = [
    dict(cle="heros", ratio="16:9", largeur=1800, q=74,
         nom="Heros — le geste du soin",
         sujet=("A West African aesthetician's hands, seen from above, holding a small ceramic bowl "
                "of pale cream and a flat brush over a folded white towel, faint steam rising, "
                "the client out of frame")),
    dict(cle="visage", ratio="16:9", largeur=1600, q=76,
         nom="Visage — le masque qu'on pose",
         sujet=("Gloved hands of a West African aesthetician applying a smooth cream mask with a "
                "flat brush along a client's cheek and jaw, the client's face mostly out of frame, "
                "only the jawline and shoulder visible, deep brown skin, white headband")),
    dict(cle="corps", ratio="16:9", largeur=1600, q=76,
         nom="Corps — le modelage",
         sujet=("Hands of a West African masseuse gliding warm oil along a client's shoulder and "
                "upper back, deep brown skin, white towel folded across the back, no face in frame")),
    dict(cle="capillaires", ratio="16:9", largeur=1600, q=76,
         nom="Capillaires — le cuir chevelu",
         sujet=("Hands of a West African hair therapist massaging a client's scalp, seen from "
                "directly above, dense natural coily hair parted in sections, no face in frame")),
    dict(cle="vip", ratio="16:9", largeur=1600, q=76,
         nom="VIP — le rituel",
         sujet=("A close editorial still of a treatment table corner: crisp white linen, three "
                "rolled towels, a small brass bowl, a lit candle and one white orchid, warm light, "
                "no people")),
]


def cle_api():
    with io.open(SECRET, encoding="utf-8") as f:
        m = re.search(r"^WAVESPEED_API_KEY=(.+)$", f.read(), re.M)
    if not m:
        sys.exit("cle WaveSpeed introuvable dans " + SECRET)
    return m.group(1).strip()


def solde(cle):
    req = urllib.request.Request("https://api.wavespeed.ai/api/v3/balance",
                                 headers={"Authorization": "Bearer " + cle})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]["balance"]


def poste(cle, prompt, ratio):
    req = urllib.request.Request(
        "https://api.wavespeed.ai/api/v3/" + MODELE,
        data=json.dumps({"prompt": prompt, "aspect_ratio": ratio, "resolution": "2k"}).encode(),
        headers={"Authorization": "Bearer " + cle, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["data"]["id"]


def attends(cle, ident, patience=240):
    t0 = time.time()
    while time.time() - t0 < patience:
        req = urllib.request.Request(
            "https://api.wavespeed.ai/api/v3/predictions/%s/result" % ident,
            headers={"Authorization": "Bearer " + cle})
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)["data"]
        if d["status"] == "completed":
            return d["outputs"][0]
        if d["status"] == "failed":
            raise RuntimeError(d.get("error") or "rendu echoue")
        time.sleep(3)
    raise TimeoutError("rendu trop long : " + ident)


def pose(url, spec):
    with urllib.request.urlopen(url, timeout=180) as r:
        im = Image.open(io.BytesIO(r.read())).convert("RGB")
    L = spec["largeur"]
    im = im.resize((L, int(round(im.height * L / im.width))), Image.LANCZOS)
    os.makedirs(DEST, exist_ok=True)
    p = os.path.join(DEST, spec["cle"] + ".webp")
    im.save(p, "WEBP", quality=spec["q"], method=6)
    return im.size, os.path.getsize(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--seul")
    ap.add_argument("--poser", action="store_true",
                    help="remplace les bandes de matiere par les images de soins")
    a = ap.parse_args()

    if a.poser:
        n = 0
        for spec in IMAGES:
            src = os.path.join(DEST, spec["cle"] + ".webp")
            if not os.path.exists(src):
                print("  manquante, rien pose : " + spec["cle"])
                continue
            shutil.copyfile(src, os.path.join(FINAL, spec["cle"] + ".webp"))
            print("  posee : %s.webp" % spec["cle"])
            n += 1
        print("  %d image(s) posee(s). Relancer `python _outils/_qc.py`." % n)
        return

    cle = cle_api()
    s = solde(cle)
    print("  solde WaveSpeed : %.2f $" % s)
    if s < 0.20:
        sys.exit("  ⛔ solde insuffisant : rechargez, puis relancez cette commande.")

    faits = 0
    for spec in IMAGES:
        if a.seul and spec["cle"] != a.seul:
            continue
        p = os.path.join(DEST, spec["cle"] + ".webp")
        if os.path.exists(p) and not a.force:
            print("  deja la : " + spec["cle"])
            continue
        print("  ... %-12s %s" % (spec["cle"], spec["nom"]))
        sys.stdout.flush()
        url = attends(cle, poste(cle, SOCLE.format(sujet=spec["sujet"]), spec["ratio"]))
        taille, poids = pose(url, spec)
        print("      %s.webp  %dx%d  %d Ko" % (spec["cle"], taille[0], taille[1], poids // 1024))
        faits += 1
    print("  %d image(s) produite(s) dans %s" % (faits, os.path.relpath(DEST, RACINE)))
    print("  ⚠️ LES REGARDER une par une avant `--poser` : ce script ne sait pas")
    print("     voir si un visage a pris toute la place ni si la peau est juste.")


if __name__ == "__main__":
    main()

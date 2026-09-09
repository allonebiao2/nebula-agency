# -*- coding: utf-8 -*-
"""
ANGY ART — bascule le site de `angy-art.pages.dev` vers son nom de domaine.

    python _domaine.py --verifier    ce qui changerait, sans rien écrire
    python _domaine.py               bascule, puis refait le QR, l'affiche et la carte

L'adresse d'un site vit à sept endroits, et six d'entre eux ne se voient pas
depuis la page :

    index.html      canonical, og:url, og:image, et les @id du JSON-LD
    sitemap.xml     le <loc>
    robots.txt      la ligne Sitemap:
    llms.txt        les deux liens de fin
    affiche.html    le pied de page, IMPRIMÉ
    qr-site.png     le QR de l'affiche, qui encode l'ancienne adresse
    les outils      _outils_llms.py, _audit.py, _fluidite.py, _build_assets.py

Oublier le JSON-LD casse l'identité de l'artiste aux yeux des moteurs : le
`@id` d'une Person est une clé, pas une décoration, et six VisualArtwork
pointent dessus. Oublier le QR de l'affiche laisse partir chez l'imprimeur un
carré qui mène à une adresse qu'on vient d'abandonner.

--------------------------------------------------------------------------
⛔ IL REFUSE D'ÉCRIRE TANT QUE LE DOMAINE NE RÉPOND PAS
--------------------------------------------------------------------------
Déclarer une adresse canonique qui ne résout pas est pire que de garder
l'ancienne : les moteurs suivent le canonical, le trouvent mort, et cessent
d'indexer la page qui marchait. `--force` existe pour préparer, jamais pour
publier.
"""
import argparse
import io
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ICI = os.path.dirname(os.path.abspath(__file__))
ANCIEN = "angy-art.pages.dev"
NOUVEAU = "angyart.online"

# Le fichier, et ce qu'on y remplace. `None` = l'hôte partout où il paraît.
FICHIERS = [
    ("index.html", None),
    ("sitemap.xml", None),
    ("robots.txt", None),
    ("llms.txt", None),
    ("_outils_llms.py", None),
    ("_audit.py", None),
    ("_fluidite.py", None),
    ("_build_assets.py", None),
]


def repondre(url):
    r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (NEBULA)"})
    try:
        with urllib.request.urlopen(r, timeout=25) as rep:
            return rep.status, rep.read(6000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return None, type(e).__name__


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verifier", action="store_true", help="ne rien écrire")
    ap.add_argument("--force", action="store_true",
                    help="écrire même si le domaine ne répond pas (préparer, pas publier)")
    a = ap.parse_args()

    print(f"\n  ANGY ART · {ANCIEN}  →  {NOUVEAU}\n")

    # ------------------------------------------------------ le domaine répond ?
    code, corps = repondre(f"https://{NOUVEAU}/")
    if code == 200 and ("Angy" in corps or "Angélique" in corps):
        print(f"   ✅ https://{NOUVEAU}/ répond 200 et sert bien son site")
    else:
        quoi = f"répond {code}" if code else f"injoignable ({corps})"
        if not (a.verifier or a.force):
            raise SystemExit(
                f"⛔ ARRÊT — https://{NOUVEAU}/ {quoi}.\n"
                "   Le domaine n'est pas branché sur le projet Cloudflare Pages.\n"
                "   Rien n'est écrit : un canonical mort déréférence la page qui marche.\n"
                "   Pour préparer sans publier : --force")
        print(f"   ⚠️  https://{NOUVEAU}/ {quoi} — "
              + ("simulation" if a.verifier else "on écrit quand même (--force)"))

    # ------------------------------------------------------------- les fichiers
    total = 0
    for nom, _ in FICHIERS:
        p = os.path.join(ICI, nom)
        if not os.path.exists(p):
            print(f"   ⚠️  {nom} absent")
            continue
        s = io.open(p, encoding="utf-8").read()
        n = s.count(ANCIEN)
        if n:
            total += n
            if not a.verifier:
                io.open(p, "w", encoding="utf-8", newline="\n").write(s.replace(ANCIEN, NOUVEAU))
        print(f"   . {nom:<22} {n:>3} occurrence(s)")

    # --------------------------------------------- l'affiche, qui part imprimée
    p = os.path.join(ICI, "affiche.html")
    s = io.open(p, encoding="utf-8").read()
    n = len(re.findall(ANCIEN, s, re.I))
    if n and not a.verifier:
        s = re.sub(re.escape(ANCIEN), lambda m: NOUVEAU.upper() if m.group(0).isupper()
                   else NOUVEAU, s, flags=re.I)
        io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(f"   . {'affiche.html':<22} {n:>3} occurrence(s)  (pied de page IMPRIMÉ)")
    total += n

    print(f"\n   {total} occurrence(s) au total.")
    if a.verifier:
        print("   Simulation : rien n'a été écrit.\n")
        return

    # ------------------------------- le QR de l'affiche encode l'ancienne adresse
    refaire_qr_site()

    # -------------------------------------- et on réimprime ce qui portait l'URL
    for outil, quoi in (("_carte.py", "la carte de visite"), ("_affiche.py", "l'affiche A4")):
        arg = ["--sans-reseau"] if (outil == "_carte.py" and code != 200) else []
        print(f"\n  → {quoi}")
        r = subprocess.run([sys.executable, os.path.join(ICI, outil)] + arg,
                           cwd=ICI, capture_output=True, text=True, encoding="utf-8")
        print("\n".join("     " + l for l in (r.stdout or r.stderr).strip().splitlines()[-8:]))
        if r.returncode:
            raise SystemExit(f"⛔ {outil} a échoué.")

    print("\n  Reste à faire à la main :")
    print("   . python _outils_llms.py     (llms.txt se régénère depuis la page)")
    print("   . python _qc.py              (les contrôles)")
    print("   . python _dist.py            (le livrable)")
    print("   . wrangler pages deploy _dist --project-name=angy-art --branch=main\n")


def refaire_qr_site():
    """Le QR « LE SITE » de l'affiche, décodé après écriture."""
    import segno
    import cv2
    import numpy as np

    dest = os.path.join(ICI, "assets", "images", "qr", "qr-site.png")
    url = f"https://{NOUVEAU}/"
    segno.make(url, error="m", mode="byte", boost_error=False).save(
        dest, scale=40, border=4, dark="#0a0a0a", light="#ffffff")
    lu, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread(dest))
    if lu != url:
        raise SystemExit(f"⛔ ARRÊT — qr-site.png décodé {lu!r}, attendu {url!r}.")
    print(f"\n   . qr-site.png refait et décodé → {lu}")


if __name__ == "__main__":
    main()

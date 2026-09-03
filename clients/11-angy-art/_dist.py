# -*- coding: utf-8 -*-
"""
ANGY ART — compose `_dist/`, ce qui part sur Cloudflare Pages.

⚠️ Un déploiement Cloudflare est un INSTANTANÉ COMPLET : ce qui manque ici
   disparaît du site en ligne. Ce script repart donc d'un dossier vide, et la
   liste ci-dessous est la seule source de vérité de ce qui est publié.

Ce qui NE part PAS : les sources (`_sources/`), les scripts (`_*.py`), les
captures de contrôle (`_qc_captures/`), et `affiche.html` (c'est un gabarit
d'impression, le PDF suffit).

    python _dist.py
    npx wrangler pages deploy clients/11-angy-art/_dist --project-name=angy-art --branch=main
"""
import os
import shutil

ICI = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ICI, "_dist")

FICHIERS = ["index.html", "404.html", "robots.txt", "sitemap.xml", "_headers"]
DOSSIERS = ["assets"]
# rien de tout ça ne doit se retrouver en ligne
EXCLUS = shutil.ignore_patterns("_*", ".*")


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)

    for f in FICHIERS:
        src = os.path.join(ICI, f)
        if not os.path.exists(src):
            raise SystemExit(f"  manquant : {f}")
        shutil.copy2(src, os.path.join(DIST, f))

    for d in DOSSIERS:
        shutil.copytree(os.path.join(ICI, d), os.path.join(DIST, d), ignore=EXCLUS)

    n = poids = 0
    for racine, _, fs in os.walk(DIST):
        for f in fs:
            n += 1
            poids += os.path.getsize(os.path.join(racine, f))
    print(f"_dist : {n} fichiers, {poids / 1024 / 1024:.2f} Mo")

    # garde-fou : plus aucune image générée ne doit traîner
    for racine, _, fs in os.walk(DIST):
        for f in fs:
            if "gallery" in racine.replace("\\", "/"):
                raise SystemExit("  ⛔ assets/images/gallery est de retour (images IA)")
    print("aucune trace des anciennes images générées.")


if __name__ == "__main__":
    main()

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
import io
import os
import re
import shutil

ICI = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ICI, "_dist")

# ⚠️ `llms.txt` est une LISTE EXPLICITE : un fichier absent d'ici ne part pas
#    en ligne, et rien ne le signale (ajoute le 2026-09-09).
FICHIERS = ["index.html", "404.html", "robots.txt", "sitemap.xml", "_headers", "llms.txt"]
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

    # ⚠️ GARDE-FOU DES SONS. `copytree` copie tout ce qui existe, mais RIEN ne
    #    vérifiait que ce que la page RÉCLAME est bien parti : un fichier
    #    renommé ou oublié aurait donné un 404 et un site muet, sans un mot.
    #    Chez Hillary, ce défaut exact a livré un site muet une fois.
    #    ⚠️ On lit le nom dans les DEUX fichiers qui peuvent le porter : la page
    #    et le script (le chemin y est concaténé avec la marque de version).
    reclames = set()
    for f in ("index.html", os.path.join("assets", "app.js")):
        chemin = os.path.join(ICI, f)
        if os.path.exists(chemin):
            with io.open(chemin, encoding="utf-8") as fh:
                reclames |= set(re.findall(r"assets/sons/([A-Za-z0-9_.-]+\.mp3)", fh.read()))
    manquants = [n for n in sorted(reclames)
                 if not os.path.exists(os.path.join(DIST, "assets", "sons", n))]
    if manquants:
        raise SystemExit("  ⛔ des sons réclamés par la page ne sont pas dans _dist : "
                         + ", ".join(manquants)
                         + "\n     Relance `python _son.py`, puis ce script.")
    if reclames:
        poids_son = sum(os.path.getsize(os.path.join(DIST, "assets", "sons", n))
                        for n in reclames)
        print("%d son(s) publié(s), %d Ko." % (len(reclames), poids_son // 1024))


if __name__ == "__main__":
    main()

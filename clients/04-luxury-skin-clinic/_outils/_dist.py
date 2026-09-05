# -*- coding: utf-8 -*-
"""
_dist.py — prepare le dossier a publier.

    python _outils/_dist.py
    wrangler pages deploy _dist --project-name luxury-club-229

⚠️ POURQUOI CE SCRIPT EXISTE (2026-09-05). Le site se deployait avec `.`,
   c'est-a-dire TOUT le dossier client. Mesure faite ce jour-la sur le site en
   ligne :
     . https://luxuryclub229.com/CONTEXT.md          -> 200
     . https://luxuryclub229.com/assets/_inbox/...   -> 200
   Les notes internes du client (prix, decisions, « a valider ») et 7,2 Mo de
   photos sources brutes de Gloria etaient publiquement telechargeables, sans
   qu'aucune page ne les reference. Ce script ne publie que ce qui doit l'etre.

⚠️ UN DEPLOIEMENT PAGES EST UN INSTANTANE COMPLET : ce qui manque ici disparait
   du site. Les exclusions ci-dessous ont donc ete verifiees une par une —
   aucune page ni aucun script ne les reference (`grep` a 0).
"""
import io, os, shutil, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(RACINE, "_dist")

# ce qui ne doit jamais partir en ligne
EXCLUS_RACINE = {"_dist", "_outils", "_vues", ".wrangler", ".git", ".impeccable",
                 ".gitignore", "CONTEXT.md"}
EXCLUS_ASSETS = {"_inbox", "og-source"}


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)

    poids, fichiers = 0, 0
    for nom in sorted(os.listdir(RACINE)):
        if nom in EXCLUS_RACINE:
            continue
        src = os.path.join(RACINE, nom)
        dst = os.path.join(DIST, nom)
        if os.path.isdir(src):
            def ignore(dossier, noms):
                if os.path.abspath(dossier) == os.path.abspath(os.path.join(RACINE, "assets")):
                    return [n for n in noms if n in EXCLUS_ASSETS]
                return []
            shutil.copytree(src, dst, ignore=ignore)
        else:
            shutil.copyfile(src, dst)

    for base, _, noms in os.walk(DIST):
        for n in noms:
            fichiers += 1
            poids += os.path.getsize(os.path.join(base, n))

    # verification : rien d'exclu ne doit avoir suivi
    fuites = []
    for base, dossiers, noms in os.walk(DIST):
        rel = os.path.relpath(base, DIST)
        for d in list(dossiers):
            if d in EXCLUS_RACINE or (rel == "assets" and d in EXCLUS_ASSETS):
                fuites.append(os.path.join(rel, d))
        for n in noms:
            if n in EXCLUS_RACINE:
                fuites.append(os.path.join(rel, n))
    if fuites:
        sys.exit("⛔ des fichiers exclus ont suivi : " + ", ".join(fuites))

    print("  _dist pret : %d fichiers, %.1f Mo" % (fichiers, poids / 1048576.0))
    print("  exclus : " + ", ".join(sorted(EXCLUS_RACINE | {"assets/" + e for e in EXCLUS_ASSETS})))
    print("  wrangler pages deploy _dist --project-name luxury-club-229")


if __name__ == "__main__":
    main()

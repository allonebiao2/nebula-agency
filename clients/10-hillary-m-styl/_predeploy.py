#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HILLARY M. STYL — le garde-fou avant mise en ligne.

    cd clients/10-hillary-m-styl
    python3 _predeploy.py

Il enchaîne, et il S'ARRÊTE au premier problème :

  1. la V4 est-elle bien là ?      (sinon on déploierait l'ancienne version)
  2. `_build.py`                    source -> vitrine.html
  3. `_qc.py`                       71 contrôles, tous verts obligatoires
  4. aucun reliquat public          numéro de test, « à confirmer », placeholders
  5. `_dist/index.html` préparé     et la commande de déploiement affichée

Pourquoi ce fichier existe : le site est DÉJÀ EN LIGNE avec la V2.
Un déploiement rate ne casse pas un brouillon — il casse un site que des
clientes utilisent. On ne déploie pas « pour voir ».
"""

import pathlib
import re
import shutil
import subprocess
import sys

# la console Windows est en cp1252 : un seul caractere de trace fait tomber
# tout le script au premier affichage. Lecon du 2026-08-05, revue le 08-06.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ICI = pathlib.Path(__file__).resolve().parent
SRC = ICI / "_vitrine_src.html"
OUT = ICI / "vitrine.html"
DIST = ICI / "_dist"
PROJET = "hillary-m-styl"

# Les seuls « à confirmer » légitimes, tous les trois pour le MÊME cas :
# le pays « Autre », dont les frais d'expédition sont réellement à confirmer
# au cas par cas. Ce n'est pas un placeholder oublié, c'est une réponse honnête.
#   1. dans la liste déroulante des pays
#   2. dans le message WhatsApp envoyé à l'atelier
#   3. dans le récapitulatif chiffré (avec une capitale)
TOLERES = [
    '(frais à confirmer)',
    '"à confirmer" : fcfa(f)',
    '"À confirmer" : fcfa(f)',
]


def echec(msg, aide=""):
    print("\n  ❌", msg)
    if aide:
        print("     " + aide)
    sys.exit(1)


def etape(n, titre):
    print(f"\n  [{n}/5] {titre}")


def main():
    print("\n  HILLARY M. STYL — vérification avant mise en ligne")
    print("  " + "─" * 52)

    # ---------- 1. est-ce bien la V4 « LA COUPE » ? ----------
    etape(1, "la bonne version est-elle là ?")
    if not SRC.exists():
        echec("`_vitrine_src.html` est absent.",
              "Vous êtes sur une branche qui n'a pas la V3. Faites :\n"
              "     git fetch origin && git checkout claude/github-repo-context-nisd2r")
    s = SRC.read_text(encoding="utf-8")
    for marqueur, quoi in [("Bodoni Moda", "la typographie de la maison"),
                           ("LA COUPE", "la direction V4"),
                           ("hsl-c", "le slider éditorial du héros"),
                           ("look-cpt", "le compteur fixe du lookbook"),
                           ("class=\"bdg", "les badges flottants"),
                           ("data-tap", "les réactions au toucher"),
                           ("var MESURES", "le moteur de mesures")]:
        if marqueur not in s:
            echec(f"la source ne contient pas {quoi} (`{marqueur}`).",
                  "Ce n'est pas la V4 « LA COUPE ». Ne déployez pas.")
    print("       ✅ source V4 « LA COUPE » confirmée, moteur inclus")

    # ---------- 2. construire ----------
    etape(2, "construction du livrable")
    r = subprocess.run([sys.executable, "_build.py"], cwd=ICI,
                       capture_output=True, text=True)
    if r.returncode != 0:
        echec("`_build.py` a échoué.", r.stdout + r.stderr)
    print("       ✅ " + OUT.name + f" — {OUT.stat().st_size // 1024} Ko")

    # ---------- 3. contrôle qualité ----------
    etape(3, "contrôle qualité (71 contrôles)")
    r = subprocess.run([sys.executable, "_qc.py"], cwd=ICI,
                       capture_output=True, text=True)
    sortie = r.stdout + r.stderr
    if r.returncode != 0 or "TOUT EST VERT" not in sortie:
        for l in sortie.splitlines():
            if l.startswith("FAIL") or "INTERROMPU" in l:
                print("       " + l)
        echec("le QC n'est pas vert.", "On ne déploie pas par-dessus un site vivant "
              "avec un contrôle rouge.")
    print("       ✅ " + [l for l in sortie.splitlines() if "TOUT EST VERT" in l][0].strip())

    # ---------- 4. aucun reliquat visible par une cliente ----------
    etape(4, "aucun placeholder sur la page publique")
    h = OUT.read_text(encoding="utf-8")
    if "22900000000" in h:
        echec("le numéro WhatsApp de test est encore là.",
              "Aucune commande n'arriverait.")
    reste = h
    for t in TOLERES:
        reste = reste.replace(t, "")
    for motif, quoi in [(r"à confirmer", "« à confirmer »"),
                        (r"À COMPLÉTER", "« À COMPLÉTER »"),
                        (r"lorem", "du faux texte")]:
        trouve = re.findall(motif, reste, re.I)
        if trouve:
            echec(f"il reste {len(trouve)} fois {quoi} dans la page.",
                  "Ces mots seront lus par une cliente. Corrigez la source.")
    wa = re.search(r'var WHATSAPP\s*=\s*"(\d+)"', h)
    print(f"       ✅ aucun placeholder · WhatsApp = {wa.group(1) if wa else '?'}")

    # ---------- 5. le dossier à publier ----------
    etape(5, "préparation du dossier à publier")
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copy(OUT, DIST / "index.html")

    # ⚠️ Depuis la V4, le site n'est PLUS un fichier unique : 19 photos vivent
    #    dans assets/images/. En base64 elles feraient un HTML de plus de 6 Mo,
    #    illisible, non cachable et impossible à charger en 4G. Un déploiement
    #    Cloudflare est un instantané complet : ce qui manque ici disparaît du site.
    src_img = ICI / "assets" / "images"
    n_img = poids_img = 0
    if src_img.exists():
        dst_img = DIST / "assets" / "images"
        dst_img.mkdir(parents=True, exist_ok=True)
        for f in sorted(src_img.glob("*.webp")):
            shutil.copy(f, dst_img / f.name)
            n_img += 1
            poids_img += f.stat().st_size
    # toute image référencée par le HTML doit être dans _dist
    import re as _re
    manquantes = [r for r in set(_re.findall(r'assets/images/([A-Za-z0-9_.-]+)', OUT.read_text(encoding="utf-8")))
                  if not (DIST / "assets" / "images" / r).exists()]
    if manquantes:
        stop("des images référencées par la page ne sont pas dans _dist : "
             + ", ".join(sorted(manquantes)[:6]),
             "Relancez `python _pose_images.py`, puis ce script.")

    poids = (DIST / "index.html").stat().st_size
    print(f"       ✅ _dist/index.html — {poids // 1024} Ko")
    print(f"       ✅ {n_img} images copiées — {poids_img // 1024} Ko")
    print(f"          total à publier : {(poids + poids_img) // 1024} Ko")
    print("")

    print("\n  " + "─" * 52)
    print("  TOUT EST PRÊT. La commande à lancer :\n")
    print(f"    npx -y wrangler@3 pages deploy _dist --project-name {PROJET} --branch main\n")
    print("  Identifiants : secrets/cloudflare.env")
    print("  Après coup, ouvrez https://hillary-m-styl.pages.dev et vérifiez")
    print("  que le loader se fend en deux, que le numéro géant passe derrière la")
    print("  silhouette, et que le compteur du lookbook avance au défilement.")
    print("  ✅ Le catalogue porte les VRAIES pieces d'Hillary (recues le 2026-08-06).")
    print("  ⚠️ Reste a confirmer : les 11 mesures de la robe ovale, la matiere de")
    print("     chaque piece, et le libelle « Robe de ville » (voir _sources/hillary/).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

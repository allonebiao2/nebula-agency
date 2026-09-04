#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HILLARY M. STYL — le garde-fou avant mise en ligne.

    cd clients/10-hillary-m-styl
    python3 _predeploy.py

Il enchaîne, et il S'ARRÊTE au premier problème :

  1. la V4 est-elle bien là ?      (sinon on déploierait l'ancienne version)
  2. `_v4/_assembler.py`            morceaux de _v4/ -> _vitrine_src.html
     puis `_build.py`               source -> vitrine.html
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
    # ⛔ L'ASSEMBLEUR D'ABORD. Le site se monte en deux temps : `_assembler.py`
    #    recompose `_vitrine_src.html` depuis les morceaux de `_v4/`, puis
    #    `_build.py` en tire `vitrine.html`. Cette étape ne faisait que le
    #    second : qui modifiait un morceau de `_v4/` puis lançait ce script
    #    déployait un livrable bâti sur une source PÉRIMÉE — tout vert, tout
    #    en ligne, et le changement absent, sans un mot.
    #    ⚠️ L'assembleur refuse d'écrire si l'un des 18 identifiants du moteur
    #       manque : ce garde-fou entre donc aussi dans le chemin de déploiement.
    etape(2, "assemblage de la source, puis construction du livrable")
    r = subprocess.run([sys.executable, str(ICI / "_v4" / "_assembler.py")],
                       cwd=ICI, capture_output=True, text=True)
    if r.returncode != 0:
        echec("`_v4/_assembler.py` a échoué : la source n'est pas à jour.",
              r.stdout + r.stderr)
    print("       ✅ _vitrine_src.html réassemblé depuis _v4/")
    r = subprocess.run([sys.executable, "_build.py"], cwd=ICI,
                       capture_output=True, text=True)
    if r.returncode != 0:
        echec("`_build.py` a échoué.", r.stdout + r.stderr)
    print("       ✅ " + OUT.name + f" — {OUT.stat().st_size // 1024} Ko")

    # ---------- 3. contrôle qualité ----------
    # ⚠️ jamais de nombre recopié ici : la suite en gagne à chaque défaut
    #    corrigé, et un chiffre figé finit toujours par mentir.
    etape(3, "contrôle qualité (suite complète)")
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
    # ⚠️ LES SONS AUSSI. Ils n'étaient pas copiés : la page les demandait,
    #    Cloudflare répondait 404, et le site partait muet sans que rien
    #    ne le signale. Un déploiement est un instantané complet.
    src_son = ICI / "assets" / "sons"
    n_son = poids_son = 0
    if src_son.exists():
        dst_son = DIST / "assets" / "sons"
        dst_son.mkdir(parents=True, exist_ok=True)
        for f in sorted(src_son.glob("*.mp3")):
            shutil.copy(f, dst_son / f.name)
            n_son += 1
            poids_son += f.stat().st_size

    # toute image ET tout son référencés par le HTML doivent être dans _dist
    import re as _re
    _html = OUT.read_text(encoding="utf-8")
    # ⚠️ La boucle ci-dessus ne copie que les .webp. L'image de partage est un
    #    JPEG (l'aperçu WhatsApp ne lit pas toujours le WebP) : sans cette
    #    reprise, `og.jpg` restait sur le disque et le lien partagé n'avait
    #    aucune image. On copie donc tout ce que la page réclame vraiment.
    for r in sorted(set(_re.findall(r'assets/images/([A-Za-z0-9_.-]+)', _html))):
        src_f = src_img / r
        if src_f.exists() and not (DIST / "assets" / "images" / r).exists():
            shutil.copy(src_f, DIST / "assets" / "images" / r)
            n_img += 1
            poids_img += src_f.stat().st_size
    manquantes = [r for r in set(_re.findall(r'assets/images/([A-Za-z0-9_.-]+)', _html))
                  if not (DIST / "assets" / "images" / r).exists()]
    if manquantes:
        stop("des images référencées par la page ne sont pas dans _dist : "
             + ", ".join(sorted(manquantes)[:6]),
             "Relancez `python _pose_images.py`, puis ce script.")

    sons_manquants = [r for r in set(_re.findall(r'assets/sons/([A-Za-z0-9_.-]+)', _html))
                      if not (DIST / "assets" / "sons" / r).exists()]
    # les six sons sont nommés dans un tableau JS, pas dans un chemin complet
    for n in _re.findall(r'var SONS = \[([^\]]+)\]', _html):
        for nom in _re.findall(r'"([a-z]+)"', n):
            if not (DIST / "assets" / "sons" / (nom + ".mp3")).exists():
                sons_manquants.append(nom + ".mp3")
    if sons_manquants:
        stop("des sons référencés par la page ne sont pas dans _dist : "
             + ", ".join(sorted(set(sons_manquants))[:6]),
             "Relancez `python _sons_finir.py`, puis ce script.")

    # UNE PAGE 404, TOUJOURS. Sans elle, Cloudflare Pages répond 200 avec le
    # HTML d'accueil pour un fichier absent — et ce 200 hérite du cache
    # `immutable` d'un an. Une erreur reste alors servie pendant un an à la
    # place du fichier. C'est la panne qui a cassé PISTE (2026-08-04).
    (DIST / "404.html").write_text(
        '<!doctype html><html lang="fr"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Page introuvable — HILLARY M. STYL</title>'
        '<style>html{background:#0B0A0C;color:#F4F1EC;font:16px/1.6 system-ui,sans-serif}'
        'body{margin:0;min-height:100vh;display:grid;place-items:center;text-align:center;padding:24px}'
        'h1{font-size:clamp(1.6rem,6vw,2.6rem);margin:0 0 12px;font-weight:700}'
        'p{margin:0 0 26px;color:rgba(244,241,236,.68)}'
        'a{display:inline-block;padding:15px 26px;border-radius:50px;background:#E6007E;'
        'color:#fff;text-decoration:none;font-weight:600;letter-spacing:.06em}</style>'
        '<div><h1>Cette page n\'existe pas.</h1>'
        '<p>Le fil s\'est arrêté ici. Reprenons depuis le début.</p>'
        '<a href="/">Retour à l\'accueil</a></div></html>', encoding="utf-8")

    # ROBOTS ET SITEMAP. Sans eux, un moteur découvre la page au hasard des
    # liens ; avec eux, il sait qu'elle existe et quand elle a changé.
    import datetime as _dt
    (DIST / "robots.txt").write_text("\n".join([
        "User-agent: *",
        "Allow: /",
        "",
        "Sitemap: https://hillary-m-styl.pages.dev/sitemap.xml",
        "",
    ]), encoding="utf-8")
    (DIST / "sitemap.xml").write_text("\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url><loc>https://hillary-m-styl.pages.dev/</loc>'
        f'<lastmod>{_dt.date.today().isoformat()}</lastmod>'
        '<changefreq>weekly</changefreq><priority>1.0</priority></url>',
        '</urlset>',
        "",
    ]), encoding="utf-8")

    poids = (DIST / "index.html").stat().st_size
    print(f"       ✅ _dist/index.html — {poids // 1024} Ko")
    print("       ✅ 404.html — un fichier absent ne sera jamais mis en cache un an")
    print(f"       ✅ {n_img} images copiées — {poids_img // 1024} Ko")
    if n_son:
        print(f"       ✅ {n_son} sons d'atelier copiés — {poids_son // 1024} Ko")
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

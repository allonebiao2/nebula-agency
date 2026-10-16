# -*- coding: utf-8 -*-
"""MA LETTRE À… · prépare `_dist/` : uniquement ce qui doit être en ligne.

    python malettre/_build_accueil.py && python malettre/_qc_accueil.py
    python malettre/_dist.py

⛔ On ne déploie JAMAIS le dossier `malettre/` lui-même : il porte les scripts,
les contrôles, la caisse (`supabase/`), les notes (`*.md`) et `exemples.json`.
Un déploiement Cloudflare Pages est un instantané complet : ce qui est dans le
dossier est en ligne (leçon Luxury Club : notes internes et photos sources
téléchargeables pendant des mois).

Écrit aussi `404.html` (sans lui, Pages sert l'accueil en 200 pour toute
adresse inconnue), `robots.txt` et `_headers`.

⚠️ La route `/l/<jeton>` (les lettres payées, servies par la fonction
`malettre-lettre`) arrive avec le branchement de la caisse : ce jour-là,
`_dist` devra la porter (`_redirects` ou fonction Pages). Voir PAIEMENT.md.
"""
import pathlib
import shutil
import sys

ICI = pathlib.Path(__file__).resolve().parent
DIST = ICI / "_dist"

PAGES = ["index.html", "creer.html", "lettre.html", "paiement.html", "merci.html", "favicon.svg", "og.jpg",
         # l'anglais (2026-10-16) : fabriqué par _build_accueil.py, qui lance _traduire.py
         "og-en.jpg", "en/index.html", "en/creer.html", "en/paiement.html", "en/merci.html",
         # ce qu'un agent lit sans rendre la page (vague 3) : fabriqué par _build_accueil.py
         "llms.txt"]
SOURCES_ACCUEIL = ["_accueil_src.html", "exemples.json", "exemples.en.json", "creer.html", "lettre.html",
                   "_build_accueil.py", "i18n/en.txt", "faire-part/offre.json"]

ERREUR = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>Lettre introuvable · Letter not found · Ma lettre à…</title>
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
html,body{margin:0;min-height:100%;background:#141019;color:#f4ede0}
body{display:grid;place-items:center;min-height:100vh;padding:24px;box-sizing:border-box;text-align:center;
 font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.cachet{width:64px;height:64px;margin:0 auto 26px;border-radius:50%;
 background:radial-gradient(circle at 34% 30%,#b2434e,#8c2f39 62%,#6d1f27);box-shadow:0 8px 18px rgba(0,0,0,.4)}
h1{font-family:"Iowan Old Style","Palatino Linotype",Georgia,serif;font-weight:400;font-size:clamp(32px,7vw,56px);margin:0 0 14px;line-height:1.05}
p{color:#a39bb3;margin:0 auto 28px;max-width:32em;line-height:1.6}
.en{margin-top:-8px;font-size:14px}
.liens{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
a{display:inline-flex;align-items:center;min-height:52px;padding:0 28px;border-radius:999px;background:#f4ede0;
 color:#241d2b;text-decoration:none;font-weight:700}
</style></head><body><main>
<div class="cachet" aria-hidden="true"></div>
<h1>Cette lettre n'est pas ici</h1>
<p>L'adresse est peut-être incomplète, ou la lettre a expiré, ou elle a été retirée.
Vérifie le lien qu'on t'a envoyé, en entier.</p>
<!-- On ne sait pas d'où vient le visiteur : la page parle les deux langues. -->
<p class="en" lang="en">This letter is not here. The link may be incomplete, or the letter has
expired or been removed. Check the whole link you were sent.</p>
<div class="liens"><a href="/">Écrire ma lettre</a><a href="/en/" lang="en">Write my letter</a></div>
</main></body></html>
"""

# Tout autorisé, robots d'IA compris : l'accueil doit pouvoir être cité.
# Les lettres, elles, portent `noindex` (balise ET en-tête) : ne pas les
# interdire ici, sinon le robot ne lit jamais ce `noindex`.
ROBOTS = """User-agent: *
Allow: /
"""

# ⚠️ Jamais `immutable` : aucun fichier n'est versionné par `?v=` ici, une
# image changée resterait périmée un an. Une heure suffit.
ENTETES = """/*
  X-Frame-Options: SAMEORIGIN
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains

/l/*
  X-Robots-Tag: noindex, nofollow, noarchive
  Referrer-Policy: no-referrer

/exemples/*
  X-Robots-Tag: noindex, nofollow

/en/exemples/*
  X-Robots-Tag: noindex, nofollow

/en/paiement.html
  X-Robots-Tag: noindex, nofollow

/en/merci.html
  X-Robots-Tag: noindex, nofollow

/lettre.html
  X-Robots-Tag: noindex, nofollow

/paiement.html
  X-Robots-Tag: noindex, nofollow

/merci.html
  X-Robots-Tag: noindex, nofollow

/og.jpg
  Cache-Control: public, max-age=3600

/og-en.jpg
  Cache-Control: public, max-age=3600

/favicon.svg
  Cache-Control: public, max-age=3600
"""


def main():
    index = min((ICI / "index.html").stat().st_mtime, (ICI / "en" / "index.html").stat().st_mtime)
    vieux = [n for n in SOURCES_ACCUEIL if (ICI / n).stat().st_mtime > index + 1]
    if vieux:
        sys.exit("⛔ index.html est plus ancien que %s : python malettre/_build_accueil.py" % ", ".join(vieux))
    exemples = sorted((ICI / "exemples").glob("*.html")) + sorted((ICI / "en" / "exemples").glob("*.html"))
    if len(exemples) < 12:
        sys.exit("⛔ il manque des exemples (%d sur 12) : python malettre/_build_accueil.py" % len(exemples))

    if DIST.is_dir():
        shutil.rmtree(DIST)
    DIST.mkdir()
    total = 0
    for rel in PAGES + [p.relative_to(ICI).as_posix() for p in exemples]:
        src = ICI / rel
        if not src.exists():
            sys.exit("⛔ MANQUE : " + rel)
        dst = DIST / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        total += dst.stat().st_size
        print("  %-26s %7.1f Ko" % (rel, dst.stat().st_size / 1024))
    for nom, contenu in (("404.html", ERREUR), ("robots.txt", ROBOTS), ("_headers", ENTETES)):
        (DIST / nom).write_text(contenu, encoding="utf-8", newline="\n")
        total += (DIST / nom).stat().st_size
        print("  %-26s %7.1f Ko" % (nom, (DIST / nom).stat().st_size / 1024))

    # La garde : rien de privé n'a glissé dans le livrable.
    fuites = [str(p.relative_to(DIST)) for p in DIST.rglob("*")
              if p.is_file() and (p.name.startswith(("_", ".")) and p.name != "_headers"
                                  or p.suffix in (".md", ".py", ".mjs", ".ts", ".sql", ".json"))]
    if fuites:
        sys.exit("⛔ fichiers privés dans _dist : %s" % fuites)
    print("_dist : %d fichiers, %.0f Ko · rien de privé" % (sum(1 for p in DIST.rglob("*") if p.is_file()), total / 1024))
    print("Publier (avec le feu vert de Mongazi seulement) :")
    print("  wrangler pages deploy malettre/_dist --project-name malettre --branch main")


if __name__ == "__main__":
    main()

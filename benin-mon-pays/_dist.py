# -*- coding: utf-8 -*-
"""Prepare _dist/ : uniquement ce qui doit etre en ligne.

Les scripts, le QC et le CONTEXT restent au chaud. Ecrit aussi un 404.html :
sans lui, un fichier absent repond 200 sur Cloudflare Pages, et ce 200 est
mis en cache un an (panne vecue sur PISTE).
"""
import io
import os
import shutil

ICI = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ICI, "_dist")

GARDE = [
    "index.html",
    "assets/app.css",
    "assets/app.js",
    "assets/fonts/bodoni-normal.woff2",
    "assets/fonts/bodoni-italic.woff2",
    "assets/images/favicon.svg",
    "assets/images/og.png",
]

if os.path.isdir(DIST):
    shutil.rmtree(DIST)
os.makedirs(DIST)

total = 0
for rel in GARDE:
    src = os.path.join(ICI, rel)
    if not os.path.exists(src):
        raise SystemExit("MANQUE : " + rel)
    dst = os.path.join(DIST, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    t = os.path.getsize(dst)
    total += t
    print("  %-42s %7.1f Ko" % (rel, t / 1024.0))

# la page d'erreur, sobre et autonome
err = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Page introuvable · Mon Bénin</title>
<style>
html,body{margin:0;height:100%;background:#0b0a09;color:#f2ede5;
 font-family:ui-sans-serif,system-ui,'Segoe UI',Roboto,Arial,sans-serif;
 display:grid;place-items:center;text-align:center;padding:24px}
h1{font-family:Georgia,'Noto Serif',serif;font-weight:300;
 font-size:clamp(32px,7vw,64px);margin:0 0 14px;letter-spacing:-.01em}
p{color:#cdc4b6;margin:0 0 26px;max-width:34em}
a{display:inline-flex;align-items:center;min-height:52px;padding:0 28px;
 border:1px solid rgba(242,237,229,.34);border-radius:999px;color:inherit;
 text-decoration:none;font-size:12px;letter-spacing:.24em;text-transform:uppercase}
a:hover{background:rgba(242,237,229,.07)}
</style></head><body><main>
<h1>Cette route n'existe pas</h1>
<p>La page demandée est introuvable. Le voyage, lui, commence toujours au même
endroit : sur le sable, au kilomètre zéro.</p>
<a href="/">Revenir au départ</a>
</main></body></html>
"""
p404 = os.path.join(DIST, "404.html")
io.open(p404, "w", encoding="utf-8", newline="\n").write(err)
total += os.path.getsize(p404)
print("  %-42s %7.1f Ko" % ("404.html", os.path.getsize(p404) / 1024.0))

# en-tetes : les ressources versionnees peuvent etre gardees longtemps,
# mais JAMAIS index.html ni la page d'erreur.
head = """/assets/fonts/*
  Cache-Control: public, max-age=31536000, immutable

/assets/images/*
  Cache-Control: public, max-age=31536000, immutable

/assets/app.*
  Cache-Control: public, max-age=31536000, immutable

/index.html
  Cache-Control: public, max-age=0, must-revalidate

/404.html
  Cache-Control: public, max-age=0, must-revalidate

/
  Cache-Control: public, max-age=0, must-revalidate
"""
ph = os.path.join(DIST, "_headers")
io.open(ph, "w", encoding="utf-8", newline="\n").write(head)
print("  %-42s %7.1f Ko" % ("_headers", os.path.getsize(ph) / 1024.0))

n = sum(len(f) for _, _, f in os.walk(DIST))
print("\n_dist : %d fichiers, %.2f Mo" % (n, total / 1048576.0))

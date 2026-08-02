# -*- coding: utf-8 -*-
"""
Fabrique le dossier à publier pour Boussole.

Ce que sert la production : le proto **aplaté à la racine**. `connexion.html`
devient `index.html`, `app.html` devient `app.html`, et les chemins `../assets/`
deviennent `/assets/`.

    python boussole/_outils/_build_dist.py
    npx -y wrangler@3 pages deploy boussole/_dist --project-name boussole --branch main

⚠️ `sw.js` et `_headers` vivent dans `boussole/_deploy/`. Ils n'étaient nulle part
dans le dépôt jusqu'au 2026-08-02 : ils n'existaient que dans le déploiement, et
un redéploiement les aurait effacés. `sw.js` est un **kill-switch** : il désinstalle
l'ancien service worker et vide ses caches. Le retirer laisserait des visiteurs
coincés sur une version périmée.
"""
import io, re, shutil, sys
from pathlib import Path

RACINE = Path(r"C:/Users/USER/nebula-agency/boussole")
DIST = RACINE / "_dist"


def aplatir(html: str) -> str:
    """Le proto vit dans _proto/ ; publié, il est à la racine."""
    html = html.replace("../assets/", "/assets/")
    html = html.replace('href="app.html"', 'href="/app"')
    html = html.replace("'app.html'", "'/app'").replace('"app.html"', '"/app"')
    html = html.replace('href="connexion.html"', 'href="/"')
    return html


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # les deux pages, aplaties
    for source, cible in (("connexion.html", "index.html"), ("app.html", "app.html")):
        h = io.open(RACINE / "_proto" / source, encoding="utf-8").read()
        io.open(DIST / cible, "w", encoding="utf-8", newline="").write(aplatir(h))
    print("  ✓ index.html (connexion) + app.html, chemins aplatis")

    # les assets
    shutil.copytree(RACINE / "assets", DIST / "assets")
    print(f"  ✓ assets ({sum(1 for _ in (DIST / 'assets').rglob('*') if _.is_file())} fichiers)")

    # le kill-switch et les en-têtes
    for f in ("sw.js", "_headers"):
        shutil.copy2(RACINE / "_deploy" / f, DIST / f)
    print("  ✓ sw.js (kill-switch) + _headers")

    # garde-fous : ce qui doit être vrai avant de publier
    app = io.open(DIST / "app.html", encoding="utf-8").read()
    controles = [
        ('src="/assets/js/proto-app.js"', "le module externalisé"),
        ("perf-lite", "le mode performance adaptatif"),
        ("--acc: #ff8a1e", "la palette Orange & Nuit"),
        ('data-theme="light"', "le thème clair"),
    ]
    for motif, quoi in controles:
        if motif not in app:
            print(f"  ⛔ MANQUE : {quoi} ({motif})"); sys.exit(1)
        print(f"  ✓ {quoi}")
    if "../assets/" in app:
        print("  ⛔ des chemins ../assets/ subsistent"); sys.exit(1)

    poids = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
    print(f"\n  Prêt : {poids // 1024} Ko. Publier avec :")
    print("    npx -y wrangler@3 pages deploy boussole/_dist --project-name boussole --branch main")
    return 0


if __name__ == "__main__":
    sys.exit(main())

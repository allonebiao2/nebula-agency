"""Prépare labobine/_dist : uniquement ce qui doit être en ligne. On ne publie jamais le dossier entier."""
import shutil
import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
DIST = ICI / "_dist"
A_PUBLIER = ["index.html", "404.html", "app.css", "manifest.webmanifest", "_headers", "js", "vendor", "icons", "catalogues"]

# les catalogues des maisons se relisent à la source à chaque publication : un prix changé sur un site suit
subprocess.run([sys.executable, str(ICI / "_catalogues.py")], check=True)

if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir()
for nom in A_PUBLIER:
    src = ICI / nom
    if src.is_dir():
        shutil.copytree(src, DIST / nom)
    else:
        shutil.copy2(src, DIST / nom)
taille = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
print(f"_dist prêt : {sum(1 for f in DIST.rglob('*') if f.is_file())} fichiers, {taille / 1024:.0f} Ko")

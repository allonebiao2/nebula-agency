# -*- coding: utf-8 -*-
"""_syntaxe.py · chaque script de chaque page passe `node --check` (26/11).

Né d'une apostrophe : un remplacement de texte a écrit « (chargement d'INA…) » dans une chaîne JavaScript entre
apostrophes, et TOUT le script de la clinique est tombé (les soins, la réservation, la visite 3D). Une erreur de
syntaxe ne se voit pas en lisant la page : elle se voit en compilant. Sortie 1 si une page casse.
    python _outils/_syntaxe.py
"""
import io
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "luxury-skin-clinic.html", "ina-luxury.html", "harmonisation-faciale.html", "cozy.html", "admin.html"]
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass


def main():
    mauvais = 0
    for nom in PAGES:
        p = ICI / nom
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8")
        blocs = re.findall(r"<script(?![^>]*\bsrc=)([^>]*)>(.*?)</script>", s, re.S)
        n = 0
        for attrs, code in blocs:
            if "application/json" in attrs or "ld+json" in attrs or not code.strip():
                continue
            ext = ".mjs" if "module" in attrs else ".js"
            with tempfile.NamedTemporaryFile("w", suffix=ext, delete=False, encoding="utf-8") as f:
                f.write(code)
            r = subprocess.run(["node", "--check", f.name], capture_output=True, text=True, encoding="utf-8")
            os.unlink(f.name)
            n += 1
            if r.returncode:
                mauvais += 1
                ligne = next((l for l in r.stderr.splitlines() if "Error" in l), r.stderr.strip()[:200])
                print(f"  ✗ {nom}, script n°{n} : {ligne}")
        print(f"{nom} : {n} script(s) vérifié(s)")
    print("tout compile." if not mauvais else f"{mauvais} script(s) cassé(s).")
    sys.exit(1 if mauvais else 0)


if __name__ == "__main__":
    main()

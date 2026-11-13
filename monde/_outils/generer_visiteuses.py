import re, subprocess, sys
from pathlib import Path
txt = Path("monde/lieux/hillary-m-styl/personnages/CONSIGNES.md").read_text(encoding="utf-8")
blocs = re.findall(r"```\n(.+?)\n```", txt, re.S)
sortie = Path(sys.argv[1])
for nom, p in zip(["senami", "maman"], blocs):
    for essai in (1, 2):
        f = sortie / f"{nom}-{essai}.jpg"
        r = subprocess.run([sys.executable, "scripts/image_cf.py", p, "--modele", "flux-2-dev", "--largeur", "1024", "--hauteur", "1024", "--sortie", str(f)], capture_output=True, text=True, encoding="utf-8")
        print(nom, essai, r.returncode, (r.stdout + r.stderr).strip()[-200:])

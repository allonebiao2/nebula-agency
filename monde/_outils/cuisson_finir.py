"""LE MONDE · finir une cuisson : convertir les cartes en WebP (4 Mo → ~0,4 Mo) et les nommer dans cuisson.json.

    python monde/_outils/cuisson_finir.py

À lancer après `cuire.py`. Les PNG bruts restent sur le disque (ignorés par git), la page lit les WebP.
"""
import json
import sys
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
DOSSIER = Path(__file__).resolve().parents[1] / "lieux" / "hillary-m-styl" / "cuisson"
info = json.loads((DOSSIER / "cuisson.json").read_text(encoding="utf-8"))
for cle, qualite in (("occlusion", 90), ("lumiere", 92)):
    png = DOSSIER / f"{cle}.png"
    if not png.exists():
        continue
    webp = DOSSIER / f"{cle}.webp"
    Image.open(png).convert("RGB").save(webp, "WEBP", quality=qualite, method=6)
    info[cle] = webp.name
    print(f"{cle} : {png.stat().st_size // 1024} Ko → {webp.stat().st_size // 1024} Ko")
(DOSSIER / "cuisson.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
print("cuisson.json :", info)

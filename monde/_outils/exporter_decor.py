"""LE MONDE · exporter le décor fixe du salon en .glb, pour la cuisson de la lumière dans Blender.

    python monde/_servir.py                     (dans un autre terminal)
    python monde/_outils/exporter_decor.py      → monde/_cuisson/salon-decor.glb

Le salon est construit dans le navigateur à partir de plan.json : on l'ouvre (sans écran
d'ouverture), on attend que les matières Poly Haven soient posées (« embelli »), puis la page
exporte elle-même son décor (`__monde.exporterDecor()`) : sans personnages, sans repères, sans
vitres ni miroir, avec les lumières. Chaque objet garde un NOM STABLE (decor-1, decor-2…) pour
retrouver sa carte de lumière au retour.
⚠️ Un seul navigateur à la fois sur ce PC.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ICI = Path(__file__).resolve().parent.parent
SORTIE = ICI / "_cuisson"
# ⚠️ `sans-cuisson` : exporter une page qui a déjà posé la lumière cuite exporterait ses formes recousues
# qualité HAUTE (les 7 projecteurs, le 2e plafonnier) et 21 h (les lampes à leur force de nuit)
URL = "http://localhost:8765/lieux/hillary-m-styl/?direct=1&qualite=haute&heure=21&sans-cuisson"


def main() -> int:
    SORTIE.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=angle", "--enable-unsafe-swiftshader"])
        pg = b.new_page(viewport={"width": 1280, "height": 720}, accept_downloads=True)
        erreurs: list[str] = []
        pg.on("pageerror", lambda e: erreurs.append(str(e)))
        pg.goto(URL)
        t0 = time.time()
        while time.time() - t0 < 90 and not pg.evaluate("document.body.classList.contains('embelli')"):
            time.sleep(1)
        time.sleep(3)
        with pg.expect_download(timeout=120_000) as dl:
            n = pg.evaluate("__monde.exporterDecor()")
        cible = SORTIE / "salon-decor.glb"
        dl.value.save_as(str(cible))
        b.close()
    print(f"{n} objets et lumières exportés → {cible} ({cible.stat().st_size // 1024} Ko)")
    if erreurs:
        print("erreurs de la page :", erreurs[:5])
    return 0


if __name__ == "__main__":
    sys.exit(main())

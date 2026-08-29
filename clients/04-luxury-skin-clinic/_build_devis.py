#!/usr/bin/env python3
"""Rend le devis HTML en PDF, à la charte LUXURY CLUB 229.

Même chaîne que le reste de la maison : HTML stylé → Chrome headless → PDF
(`_documents/nebula-agency/vente/_build_pdf.py`, les affiches, la carte de visite).
Aucune bibliothèque de mise en page : ce qu'on voit dans le navigateur est ce
qui sort à l'impression.

⚠️ On attend que les polices Google soient chargées avant d'imprimer. Sans
`--virtual-time-budget`, Chrome imprime parfois avant l'arrivée de Cormorant
Garamond et le devis sort en police système — le même défaut a déjà trompé un
contrôle chez Angy Art le 2026-08-26.

    python clients/04-luxury-skin-clinic/_build_devis.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
SOURCE = ICI / "devis-vitrine-tablette.html"
SORTIE = ICI / "assets" / "docs" / "Devis_Vitrine_Tablette_LUXURY_CLUB_229.pdf"


def trouver_chrome() -> str:
    pistes = [
        "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
        r"C:/Program Files/Google/Chrome/Application/chrome.exe",
        r"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    ]
    for p in pistes:
        if Path(p).exists():
            return p
    for nom in ("google-chrome", "chromium", "chromium-browser", "msedge", "chrome"):
        trouve = shutil.which(nom)
        if trouve:
            return trouve
    raise SystemExit("⛔ Aucun navigateur trouvé pour fabriquer le PDF.")


def main() -> int:
    if not SOURCE.exists():
        raise SystemExit(f"⛔ Source introuvable : {SOURCE}")
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    chrome = trouver_chrome()
    resultat = subprocess.run([
        chrome, "--headless", "--disable-gpu", "--no-sandbox",
        "--no-pdf-header-footer",
        "--virtual-time-budget=12000",   # laisse arriver les polices
        f"--print-to-pdf={SORTIE}",
        SOURCE.as_uri(),
    ], capture_output=True, text=True, timeout=180)
    if not SORTIE.exists() or SORTIE.stat().st_size < 5000:
        print(resultat.stderr[-800:])
        raise SystemExit("⛔ Le PDF n'a pas été produit, ou il est vide.")
    print(f"✓ {SORTIE.relative_to(ICI.parent.parent)} · "
          f"{SORTIE.stat().st_size / 1024:.0f} Ko")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

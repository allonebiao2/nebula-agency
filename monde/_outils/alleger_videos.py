"""LE MONDE · une version LÉGÈRE de chaque vidéo de personnage, pour le téléphone (règle 3G).

    python monde/_outils/alleger_videos.py [lieu]            (défaut : hillary-m-styl)

Pour chaque `personnages/<prénom>/video-<nom>.mp4`, écrit à côté `video-<nom>-tel.mp4` : trois quarts de la hauteur
(960 → 720 en pied, 832 → 624 en buste) et une compression plus forte (CRF 28 au lieu de 24). Au téléphone la personne
occupe 400 à 600 px de haut : la différence ne se voit pas, le poids est divisé par deux à trois. Le `.json` est
commun aux deux (il ne porte que des fractions). Le salon prend la version légère hors qualité « haute »
(`socle/perso-video.js`, `leger`). Les fichiers restent hors dépôt (`.gitignore`).
⚠️ La largeur doit rester PAIRE et la moitié gauche (couleur) rester la moitié exacte de l'image : on impose une
largeur multiple de 4.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    lieu = next((a for a in sys.argv[1:] if not a.startswith("--")), "hillary-m-styl")
    dossier = RACINE / "lieux" / lieu / "personnages"
    avant = apres = 0
    for src in sorted(dossier.glob("*/video-*.mp4")):
        if src.stem.endswith("-tel"): continue
        meta = json.loads(src.with_suffix(".json").read_text(encoding="utf-8"))
        h = int(round(meta["hauteur"] * 0.75 / 2) * 2)
        l = int(round(meta["largeur"] * 2 * 0.75 / 4) * 4)   # les deux moitiés côte à côte
        dst = src.with_name(src.stem + "-tel.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", f"scale={l}:{h}:flags=lanczos",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "28", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.0",
                        "-movflags", "+faststart", "-an", str(dst)], check=True)
        a, b = src.stat().st_size, dst.stat().st_size; avant += a; apres += b
        print(f"{src.parent.name}/{src.name:22} {a / 1024:6.0f} Ko → {b / 1024:6.0f} Ko  ({l}×{h})")
    print(f"total : {avant / 1e6:.1f} Mo → {apres / 1e6:.1f} Mo")


if __name__ == "__main__":
    main()

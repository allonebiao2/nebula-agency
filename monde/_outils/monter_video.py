"""LE MONDE · monter une vidéo de personnage à partir de morceaux DÉJÀ préparés par `perso_video.py --garder`.

    python monde/_outils/monter_video.py <sortie sans extension> --modele <un .json de perso_video.py> \
           "<dossier de travail>:0-80" "<dossier>:0-80" "<autre dossier>:0-64" "<autre dossier>:63-1" …

Chaque morceau : le dossier de travail (ses images finies sont dans `fini/`), puis `début-fin` (dans l'ordre donné :
`63-1` rejoue à l'envers). Sert à faire UNE longue boucle vivante avec des morceaux qui commencent et finissent tous
dans la même pose (Hillary : le calme, le calme, un hochement de tête et un sourire, puis le calme), sans détourer
deux fois la même image. Le `.json` de sortie reprend celui du modèle (cadre, hauteur réelle), boucle « directe ».
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("sortie"); ap.add_argument("morceaux", nargs="+")
    ap.add_argument("--modele", required=True); ap.add_argument("--qualite", type=int, default=24)
    ap.add_argument("--une-fois", action="store_true", help="la vidéo se joue une fois (un salut), elle ne boucle pas")
    a = ap.parse_args()
    meta = json.loads(Path(a.modele).read_text(encoding="utf-8"))
    tmp = Path(tempfile.mkdtemp(prefix="monter_video_")); n = 0
    try:
        for m in a.morceaux:
            dossier, plage = m.rsplit(":", 1); d, f = (int(x) for x in plage.split("-"))
            for k in (range(d, f + 1) if f >= d else range(d, f - 1, -1)):
                src = Path(dossier) / "fini" / f"f_{k:04d}.png"
                if not src.exists(): sys.exit(f"⛔ image absente : {src}")
                shutil.copy(src, tmp / f"f_{n:04d}.png"); n += 1
        sortie = Path(a.sortie); sortie.parent.mkdir(parents=True, exist_ok=True)
        mp4 = sortie.with_suffix(".mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", f"{meta['ips']:g}", "-i", str(tmp / "f_%04d.png"),
                        "-c:v", "libx264", "-preset", "slow", "-crf", str(a.qualite), "-pix_fmt", "yuv420p",
                        "-profile:v", "high", "-level", "4.0", "-movflags", "+faststart", "-an", str(mp4)], check=True)
        meta.update({"boucle": "une fois" if a.une_fois else "directe", "images": n, "montage": a.morceaux, "poids_ko": round(mp4.stat().st_size / 1024)})
        if a.une_fois: meta["une_fois"] = True
        meta.pop("calme", None); meta.pop("vitesse", None)
        sortie.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps({k: meta[k] for k in ("images", "ips", "boucle", "poids_ko")}, ensure_ascii=False))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()

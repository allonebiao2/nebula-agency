# -*- coding: utf-8 -*-
"""MA LETTRE À… · la musique de la vitrine : du MP3 choisi par Mongazi à `son/musique.mp3`.

    python malettre/_son.py "_partage/<morceau>.mp3" "Alex Morgan"
    python malettre/_build_accueil.py      # le bouton son paraît, le crédit va au pied

Ce qu'il fait au morceau (ffmpeg de `imageio-ffmpeg`, installé par pip) :
  - le VOLUME égalisé (EBU R128, -16 LUFS, crête vraie -1,5 dB) : les morceaux de
    Pixabay arrivent mixés fort (-10 LUFS mesuré), et la page le joue déjà à 30 % ;
  - un fondu d'entrée (2 s) et de sortie (4 s) : la boucle RESPIRE au lieu de couper
    (un MP3 bouclé par le navigateur laisse un petit trou au raccord) ;
  - 96 kb/s stéréo, 44,1 kHz : environ 2 Mo pour 3 minutes, chargé seulement au
    premier geste du visiteur, jamais avant.
Puis il RE-MESURE ce qu'il a écrit (on ne fait pas confiance à un son à l'oreille).

⚠️ Pixabay : usage commercial permis, crédit non obligatoire mais donné (au pied).
⛔ Avant de choisir un morceau, vérifier qu'il n'est pas « Content ID » si la pub
doit le réutiliser (TikTok ou YouTube signaleraient la vidéo).
"""
import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ICI = pathlib.Path(__file__).resolve().parent
SORTIE = ICI / "son" / "musique.mp3"
CREDIT = ICI / "son" / "credit.txt"


def ffmpeg():
    try:
        import imageio_ffmpeg
    except ImportError:
        sys.exit("⛔ ffmpeg absent : python -m pip install imageio-ffmpeg")
    return imageio_ffmpeg.get_ffmpeg_exe()


def mesurer(ff, chemin):
    r = subprocess.run([ff, "-hide_banner", "-i", str(chemin), "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    duree = int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3)) if d else 0
    return (float(i[-1]) if i else None), duree


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, auteur = pathlib.Path(sys.argv[1]), sys.argv[2].strip()
    if not src.exists():
        sys.exit("⛔ introuvable : %s" % src)
    ff = ffmpeg()
    lufs, duree = mesurer(ff, src)
    print("source : %.1f s, %.1f LUFS" % (duree, lufs))
    SORTIE.parent.mkdir(exist_ok=True)
    fin = max(duree - 4, 1)
    filtre = "afade=t=in:st=0:d=2,afade=t=out:st=%.2f:d=4,loudnorm=I=-16:TP=-1.5:LRA=11" % fin
    subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-af", filtre,
                    "-ar", "44100", "-ac", "2", "-b:a", "96k", "-map_metadata", "-1", str(SORTIE)], check=True)
    lufs2, duree2 = mesurer(ff, SORTIE)
    CREDIT.write_text(auteur + "\n", encoding="utf-8")
    print("son/musique.mp3 : %.1f s, %.1f LUFS, %.0f Ko · crédit : %s"
          % (duree2, lufs2, SORTIE.stat().st_size / 1024, auteur))
    if lufs2 is None or abs(lufs2 + 16) > 1.5:
        sys.exit("⛔ le volume n'est pas celui visé (-16 LUFS) : réécouter, re-mesurer")


if __name__ == "__main__":
    main()

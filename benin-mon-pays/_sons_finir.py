# -*- coding: utf-8 -*-
"""Met les huit ambiances au même niveau et les allège.

Brut de génération, l'écart de niveau entre le Koutammakou (vent sec et
clairsemé) et la Pendjari (cicadas) est d'un facteur 15 : le voyage passerait
du quasi-silence au fort. On aligne tout sur la même sonie perçue (EBU R128),
puis on descend le débit, parce que ces fichiers ne se téléchargent que sur
un réseau béninois.
"""
import io
import os
import subprocess

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ICI, "assets", "sons")
BRUT = os.path.join(ICI, "_sources_sons")

os.makedirs(BRUT, exist_ok=True)

# on garde les originaux : une régénération coûte de l'argent
for f in sorted(os.listdir(SRC)):
    if not f.endswith(".mp3"):
        continue
    o = os.path.join(BRUT, f)
    if not os.path.exists(o):
        io.open(o, "wb").write(io.open(os.path.join(SRC, f), "rb").read())

total = 0
for f in sorted(os.listdir(BRUT)):
    if not f.endswith(".mp3"):
        continue
    src = os.path.join(BRUT, f)
    dst = os.path.join(SRC, f)
    # -20 LUFS : une ambiance de fond, pas une bande-son ; mono ; 48 kb/s
    subprocess.run([
        FF, "-y", "-hide_banner", "-loglevel", "error", "-i", src,
        "-af", "loudnorm=I=-20:TP=-2:LRA=11",
        "-ac", "1", "-ar", "32000", "-b:a", "48k",
        dst], check=True)
    t = os.path.getsize(dst)
    total += t
    print("  %-18s %6d o" % (f, t))

print("\n%d sons, %.0f Ko au total" % (
    len([f for f in os.listdir(SRC) if f.endswith('.mp3')]), total / 1024.0))
print("Ils ne sont JAMAIS charges d'avance : seul le lieu ou l'on se trouve")
print("telecharge son ambiance, et seulement si le son est allume.")

"""Assemble les images de out/planches/<id>/ en planches de 5 colonnes, pour les regarder."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

dossier = Path(__file__).resolve().parent.parent / "out/planches" / sys.argv[1]
choix = sys.argv[2:]
imgs = [dossier / f"{s.zfill(6)}.jpg" for s in choix] if choix else sorted(dossier.glob("*.jpg"))
L, H, COL = 432, 768, 5
police = ImageFont.truetype("arial.ttf", 26)
lignes = (len(imgs) + COL - 1) // COL
planche = Image.new("RGB", (COL * (L + 6), lignes * (H + 6)), (25, 25, 25))
for n, f in enumerate(imgs):
    im = Image.open(f).resize((L, H), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 110, 34], fill=(0, 0, 0))
    d.text((6, 3), f"{float(f.stem):.1f}s", fill=(255, 220, 0), font=police)
    planche.paste(im, ((n % COL) * (L + 6), (n // COL) * (H + 6)))
sortie = dossier.parent / f"{sys.argv[1]}_{choix[0] if choix else 'tout'}.jpg"
planche.save(sortie, quality=86)
print(sortie)

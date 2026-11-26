# -*- coding: utf-8 -*-
"""_images_harmo.py · les images de l'harmonisation faciale (26/11), faites avec SES flyers (aucune image générée).

  assets/images/ambiances/hub-harmonisation.webp  (1200 × 670, la carte du hub, sous son voile)
  assets/images/og-harmonisation.jpg              (1200 × 630, le partage)
Un triptyque : ses trois flyers, côte à côte, sur un fond encre et or. À relancer si un flyer change.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ICI = Path(__file__).resolve().parent.parent
FLYERS = ["flyer-facial-balancing.jpg", "flyer-genesis-hollywood.jpg", "flyer-genesis-soft.jpg"]


def fond(w, h):
    im = Image.new("RGB", (w, h), (14, 12, 9))
    d = ImageDraw.Draw(im)
    # un halo d'or doux au centre, et des filets verticaux (le mur du cabinet)
    halo = Image.new("L", (w, h), 0)
    ImageDraw.Draw(halo).ellipse([w * 0.2, -h * 0.2, w * 0.8, h * 1.1], fill=110)
    halo = halo.filter(ImageFilter.GaussianBlur(h * 0.25))
    im = Image.composite(Image.new("RGB", (w, h), (92, 70, 32)), im, halo)
    d = ImageDraw.Draw(im)
    for x in range(0, w, 46):
        d.line([(x, 0), (x, h)], fill=(40, 32, 20), width=1)
    return im


def triptyque(w, h, haut):
    im = fond(w, h)
    fl = [Image.open(ICI / "assets" / "harmonisation" / f).convert("RGB") for f in FLYERS]
    hh = int(h * haut)
    ww = int(hh * fl[0].width / fl[0].height)
    ecart = int(w * 0.035)
    x0 = (w - (3 * ww + 2 * ecart)) // 2
    y0 = (h - hh) // 2
    for i, f in enumerate(fl):
        f = f.resize((ww, hh), Image.LANCZOS)
        x = x0 + i * (ww + ecart)
        ombre = Image.new("L", (ww + 60, hh + 60), 0)
        ImageDraw.Draw(ombre).rectangle([30, 36, ww + 30, hh + 36], fill=160)
        ombre = ombre.filter(ImageFilter.GaussianBlur(16))
        im.paste((0, 0, 0), (x - 30, y0 - 30), ombre)
        ImageDraw.Draw(im).rectangle([x - 5, y0 - 5, x + ww + 4, y0 + hh + 4], fill=(180, 140, 62))
        im.paste(f, (x, y0))
    return im


def main():
    hub = ICI / "assets" / "images" / "ambiances" / "hub-harmonisation.webp"
    triptyque(1200, 670, 0.9).save(hub, "WEBP", quality=86, method=6)
    og = ICI / "assets" / "images" / "og-harmonisation.jpg"
    triptyque(1200, 630, 0.9).save(og, "JPEG", quality=86, optimize=True, progressive=True)
    for p in (hub, og):
        print(p.name, round(p.stat().st_size / 1024), "Ko")


if __name__ == "__main__":
    main()

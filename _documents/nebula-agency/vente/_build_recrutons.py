#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Affiche « NOUS RECRUTONS » — source -> PNG 1080 x 1350 (format réseaux sociaux).

    cd _documents/nebula-agency/vente && python3 _build_recrutons.py

On édite `_affiche_recrutons_src.html`. Ce script y injecte les polices, le
logo et l'objet héros (dessiné en SVG, pas une photo), puis rend :

    assets/Affiche-NOUS-RECRUTONS.png    (1080 x 1350, x2 = 2160 x 2700)

Pourquoi le téléphone est dessiné et non photographié : le style du panneau
est plat et vectoriel. Une photo détourée y ferait tache, et surtout un
dessin se corrige au pixel là où une photo générée se rejoue au hasard.
"""

import base64, glob, pathlib, subprocess, sys

ICI = pathlib.Path(__file__).resolve().parent
import sys as _s
V916 = "--916" in _s.argv
SRC = ICI / ("_affiche_recrutons_916_src.html" if V916 else "_affiche_recrutons_src.html")
OUT = ICI / ("_affiche_recrutons_916.html" if V916 else "_affiche_recrutons.html")
ASSETS = ICI / "assets"
LOGO = ICI / "assets/nebula-logo-transparent.png"   # detoure, fond noir retire

_C = [g for g in glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome") if "headless" not in g]
CHROME = _C[0] if _C else "chromium"

NAVY, GOLD, BLANC = "#0B1020", "#E8C88A", "#FFFFFF"


def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode("ascii")


def hero():
    """Le téléphone : coque bleu nuit, écran clair, vraie grille de catalogue.
    C'est le produit qu'on vend ; le montrer vaut mieux que toute promesse."""
    W, H = 430, 700
    cw, ch = 300, 620                      # coque
    cx = (W - cw) / 2
    sw, sh = cw - 26, ch - 30              # écran
    sx, sy = cx + 13, 15

    # la grille du catalogue : 2 colonnes x 3 rangées
    cards = []
    gx, gy = sx + 16, sy + 74
    cwid, chei, gap = (sw - 32 - 12) / 2, 128, 12
    produits = [(0.62, 0.30), (0.48, 0.44), (0.70, 0.24),
                (0.40, 0.52), (0.58, 0.34), (0.52, 0.40)]
    for i, (lp, hp) in enumerate(produits):
        col, row = i % 2, i // 2
        x = gx + col * (cwid + gap)
        y = gy + row * (chei + gap)
        cards.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cwid:.1f}" height="{chei}" rx="8" fill="#F6F1E6"/>')
        # la photo du produit, une forme sombre simple
        pw_, ph_ = cwid * lp, chei * 0.52
        px, py = x + (cwid - pw_) / 2, y + 12
        cards.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{pw_:.1f}" height="{ph_:.1f}" rx="5" fill="{NAVY}" opacity=".82"/>')
        # le libellé de prix
        cards.append(f'<rect x="{x+11:.1f}" y="{y+chei-34}" width="{cwid*0.66:.1f}" height="9" rx="4.5" fill="{NAVY}" opacity=".30"/>')
        cards.append(f'<rect x="{x+11:.1f}" y="{y+chei-19}" width="{cwid*hp:.1f}" height="11" rx="5.5" fill="{GOLD}"/>')

    return f'''<div class="hero"><svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
  <rect x="{cx}" y="0" width="{cw}" height="{ch}" rx="42" fill="{NAVY}"/>
  <rect x="{cx+3}" y="3" width="{cw-6}" height="{ch-6}" rx="39" fill="none" stroke="{GOLD}" stroke-width="1.4" opacity=".55"/>
  <rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="30" fill="#FBF7EF"/>
  <rect x="{sx}" y="{sy}" width="{sw}" height="58" rx="30" fill="{NAVY}"/>
  <rect x="{sx}" y="{sy+30}" width="{sw}" height="28" fill="{NAVY}"/>
  <rect x="{sx+18}" y="{sy+24}" width="96" height="11" rx="5.5" fill="{GOLD}"/>
  <circle cx="{sx+sw-30}" cy="{sy+30}" r="8" fill="{GOLD}" opacity=".65"/>
  {''.join(cards)}
  <rect x="{cx+cw/2-34}" y="{ch-22}" width="68" height="5" rx="2.5" fill="{GOLD}" opacity=".5"/>
</svg></div>'''


def main():
    ASSETS.mkdir(exist_ok=True)
    html = SRC.read_text(encoding="utf-8")
    for k, v in {"__ARCHIVO__": b64(ASSETS / "fonts/archivo.woff2"),
                 "__MANROPE__": b64(ASSETS / "fonts/manrope.woff2"),
                 "__LOGO__": b64(LOGO),
                 "__HERO__": hero()}.items():
        if k not in html:
            print("marqueur absent :", k); return 1
        html = html.replace(k, v)
    OUT.write_text(html, encoding="utf-8")
    print("  source assemblée :", OUT.name, OUT.stat().st_size, "octets")

    png = ASSETS / ("Affiche-NOUS-RECRUTONS-9x16.png" if V916 else "Affiche-NOUS-RECRUTONS.png")
    import asyncio
    from playwright.async_api import async_playwright

    async def shot():
        async with async_playwright() as pw:
            br = await pw.chromium.launch(executable_path=CHROME)
            ctx = await br.new_context(viewport={"width": 1080, "height": 1920 if V916 else 1350},
                                       device_scale_factor=2)
            pg = await ctx.new_page()
            await pg.goto(OUT.as_uri(), wait_until="networkidle")
            await pg.wait_for_timeout(500)
            # rien ne doit deborder du cadre
            deb = await pg.evaluate("""()=>{
              const b=document.body, r=[], R=e=>document.querySelector(e).getBoundingClientRect();
              // .t2 est en inline-block : sa boite epouse le mot, et
              // getBoundingClientRect tient deja compte du scaleX
              const bx=R('.t2');
              if(bx.right > 1080-40) r.push('titre deborde du cadre ('+Math.round(bx.right)+' px)');
              if(R('.pills').bottom > R('.gain').top+1) r.push('pastilles et chiffre se chevauchent');
              if(R('.gain').bottom > R('.annos').top+1) r.push('chiffre et reperes se chevauchent');
              if(R('.annos').bottom > R('.filtre').top+1) r.push('reperes et ligne du bas se chevauchent');
              if(R('.filtre').bottom > R('.urgence').top+1) r.push('ligne du bas et barre doree se chevauchent');
              if(R('.hero').bottom > R('.urgence').top+1) r.push('le telephone descend sous la barre doree');
              return {w:b.scrollWidth, h:b.scrollHeight, err:r};}""")
            await pg.screenshot(path=str(png))
            await br.close()
            return deb

    d = asyncio.run(shot())
    H = 1920 if V916 else 1350
    if d["w"] > 1080 or d["h"] > H:
        print("  ❌ DEBORDEMENT : %d x %d au lieu de 1080 x %d" % (d["w"], d["h"], H))
        return 1
    if d["err"]:
        for e in d["err"]:
            print("  ❌", e)
        return 1
    print("  mise en page : %d x %d, ca tient" % (d["w"], d["h"]))
    print("  PNG   :", png.name, png.stat().st_size, "octets")
    return 0


if __name__ == "__main__":
    sys.exit(main())

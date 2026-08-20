# -*- coding: utf-8 -*-
"""
L'IMAGE DE PARTAGE — Au Braisé d'Or.

    python _outils/_og.py

Au Bénin tout circule par WhatsApp. Sans `og:image`, un lien partagé n'est
qu'une **ligne de texte grise** à côté de liens qui montrent une photo : c'est
le défaut le plus coûteux qu'une vitrine puisse avoir, et il est **invisible
quand on regarde le site**.

⚠️ EN JPEG, PAS EN WEBP : l'aperçu WhatsApp ne lit pas toujours le WebP.
⚠️ La photo posée dessus est une VRAIE photo de la maison (une sauce envoyée
   par la propriétaire, détourée). Jamais une image générée.
⚠️ Aucun texte inventé : ni note, ni chef, ni « meilleur restaurant de ».
"""
import io, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

for _f in (sys.stdout, sys.stderr):
    try: _f.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

ICI = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.normpath(os.path.join(ICI, "..", "experience", "public"))
SORTIE = os.path.join(PUB, "og.jpg")

# La palette du site, relue dans globals.css : on ne réinvente pas des couleurs.
ENCRE = (29, 26, 23)
PAPIER = (246, 239, 230)
TERRE = (168, 84, 47)
BRAISE = (214, 106, 42)

LOURDE = [r"C:\Windows\Fonts\seguibl.ttf", r"C:\Windows\Fonts\ariblk.ttf",
          r"C:\Windows\Fonts\impact.ttf"]
COURANTE = [r"C:\Windows\Fonts\framd.ttf", r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arial.ttf"]


def police(liste, taille):
    for p in liste:
        if os.path.exists(p):
            return ImageFont.truetype(p, taille)
    return ImageFont.load_default()


def espace(d, xy, texte, font, fill, ecart):
    """Une graisse lourde a besoin d'air entre les lettres pour rester noble."""
    x, y = xy
    for c in texte:
        d.text((x, y), c, font=font, fill=fill)
        x += d.textlength(c, font=font) + ecart
    return x


def main():
    L, H = 1200, 630
    im = Image.new("RGB", (L, H), ENCRE)
    d = ImageDraw.Draw(im)

    # La braise : une lueur chaude qui monte du bas droit, pas un dégradé plat.
    lueur = Image.new("L", (L, H), 0)
    dl = ImageDraw.Draw(lueur)
    dl.ellipse([620, 210, 1420, 1010], fill=190)
    lueur = lueur.filter(ImageFilter.GaussianBlur(150))
    im = Image.composite(Image.new("RGB", (L, H), BRAISE), im, lueur)
    d = ImageDraw.Draw(im)

    # Un grain de fumée, très léger : sans lui l'aplat fait « gabarit ».
    grain = Image.effect_noise((L, H), 14).filter(ImageFilter.GaussianBlur(0.6))
    im = Image.blend(im, Image.merge("RGB", (grain, grain, grain)), 0.045)
    d = ImageDraw.Draw(im)

    # LA VRAIE PHOTO : une sauce de la maison, détourée, avec son ombre au sol.
    src = os.path.join(PUB, "plats", "sc-gombo.webp")
    plat = Image.open(src).convert("RGBA")
    cible = 470
    r = cible / max(plat.size)
    plat = plat.resize((int(plat.width * r), int(plat.height * r)), Image.LANCZOS)
    px, py = 700, (H - plat.height) // 2 + 10

    ombre = Image.new("RGBA", (L, H), (0, 0, 0, 0))
    do = ImageDraw.Draw(ombre)
    do.ellipse([px + 60, py + plat.height - 46, px + plat.width - 60,
                py + plat.height + 22], fill=(0, 0, 0, 120))
    ombre = ombre.filter(ImageFilter.GaussianBlur(26))
    im = Image.alpha_composite(im.convert("RGBA"), ombre)
    im.alpha_composite(plat, (px, py))
    im = im.convert("RGB")
    d = ImageDraw.Draw(im)

    # ⚠️ On relève le fond AVANT d'écrire dessus. Mesuré après, le « pixel le
    #    plus clair de la zone » est une lettre du titre : l'instrument annonce
    #    alors 1,1:1 sur un titre parfaitement lisible. Même famille de piège
    #    que le décile clair du QC.
    fond_titre = im.crop((104, 120, 700, 300)).copy()

    # LE TEXTE — rien qui ne soit vrai.
    f_nom = police(LOURDE, 74)
    f_sur = police(COURANTE, 25)
    f_pied = police(COURANTE, 24)

    d.rectangle([70, 118, 76, 178], fill=BRAISE)          # le filet de braise
    espace(d, (104, 120), "AU BRAISÉ", f_nom, PAPIER, 2.5)
    espace(d, (104, 206), "D'OR", f_nom, BRAISE, 2.5)

    espace(d, (106, 322), "GRILLADES AU FEU DE BOIS", f_sur, (232, 205, 186), 3.2)
    espace(d, (106, 360), "COTONOU · DE PARIS À COTONOU", f_sur, (196, 168, 150), 3.2)

    d.line([106, 424, 300, 424], fill=(120, 92, 74), width=2)
    d.text((106, 452), "La carte entière, et la commande", font=f_pied, fill=(226, 214, 203))
    d.text((106, 486), "part sur WhatsApp en un geste.", font=f_pied, fill=(226, 214, 203))

    im.save(SORTIE, "JPEG", quality=88, optimize=True, progressive=True)
    ko = os.path.getsize(SORTIE) / 1024

    # ⚠️ On MESURE la lisibilité sur les pixels rendus, on ne la suppose pas :
    #    le fond est une photo et un dégradé, pas une couleur déclarée.
    def lum(c):
        v = [x / 255 for x in c]
        v = [(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in v]
        return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]

    fond = fond_titre.resize((60, 18))
    pires = sorted(list(fond.getdata()), key=lum)[-6:]     # le fond le plus clair
    contraste = min((lum(PAPIER) + 0.05) / (lum(p) + 0.05) for p in pires)
    contraste = max(contraste, 1 / contraste)

    print("og.jpg  %d x %d  %.0f Ko  JPEG" % (im.width, im.height, ko))
    print("titre sur son fond réel : %.1f:1 (mesuré, seuil 4,5)" % contraste)
    if contraste < 4.5:
        print("ROUGE : le nom n'est pas assez lisible sur la braise")
        return 1
    if ko > 300:
        print("ROUGE : trop lourd pour un aperçu")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEBULA · les cartes de question TikTok, fond noir, 1080x1920.

    python _cartes.py                 les 26 cartes des 3 scripts
    python _cartes.py --script 1      un seul script
    python _cartes.py --fond f.png    sur une texture generee

POURQUOI CE SCRIPT PLUTOT QU'UN MODELE D'IMAGE
Ces cartes sont du texte blanc sur du noir. Un modele d'image REDESSINE les
lettres au lieu de les ecrire : en francais il rate les accents (« deja » pour
« déjà »), il coupe les mots au mauvais endroit, et il ne se corrige pas. Ici le
texte est exact au caractere, la correction coute deux secondes, et les 26
cartes coutent zero franc.

Le modele d'image reste utile pour UNE chose : la texture de fond, generee une
fois et passee en --fond. Voir TIKTOK-PROMPTS-CARTES.md.
"""
import os, sys, argparse

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "tiktok")

L, H = 1080, 1920
MARGE = 118                 # le vide sur les cotes : c'est lui qui fait lire
NOIR = (7, 7, 8)
BLANC = (255, 255, 255)

# La police : une grasse large, lisible a bout de bras sur un telephone.
POLICES = [
    r"C:\Windows\Fonts\seguibl.ttf",     # Segoe UI Black
    r"C:\Windows\Fonts\ariblk.ttf",      # Arial Black
    r"C:\Windows\Fonts\arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

SCRIPTS = {
    1: ("prix", [
        "Il faut 500 000 F pour avoir un site ?",
        "Il faut attendre trois mois ?",
        "Il faut savoir se servir d'un ordinateur ?",
        "Donc n'importe qui peut en avoir un ?",
        "Il faut payer quelque chose tous les mois ?",
        "Vous avez déjà livré en retard ?",
        "Vous l'avez dit au client avant ?",
        "Vos clients sont de vrais commerçants d'ici ?",
        "Je peux vous écrire maintenant ?",
    ]),
    2: ("besoin", [
        "J'ai déjà WhatsApp. J'ai besoin d'un site ?",
        "J'ai déjà une page Facebook. J'ai besoin d'un site ?",
        "Donc un site ne sert à rien ?",
        "Vous répétez vingt fois par jour les mêmes prix ?",
        "Vous renvoyez la même photo dix fois par jour ?",
        "Ça, un lien peut le faire à votre place ?",
        "Et ça coûte moins qu'un carton de marchandise ?",
        "Vous voulez le lien ?",
    ]),
    3: ("logiciel", [
        "Vous faites des sites web ?",
        "C'est votre métier principal ?",
        "Vous faites des logiciels ?",
        "Pour les grandes entreprises ?",
        "Pour une vendeuse de tissu au marché ?",
        "Elle a besoin d'un ordinateur ?",
        "Le logiciel lui dit ce qu'elle gagne vraiment ?",
        "Elle le savait avant ?",
    ]),
}

FIN = ("NEBULA Agency · Cotonou", "Le lien est dans la bio")


def police(taille):
    for p in POLICES:
        if os.path.exists(p):
            return ImageFont.truetype(p, taille)
    raise SystemExit("aucune police grasse trouvee")


import re

INSEC = " "     # colle deux mots ensemble pour la coupe, s'affiche en espace


def mots(txt):
    """Decoupe en mots, mais UN PRIX NE SE COUPE JAMAIS.

    « Il faut 500 000 F » se retrouvait a cheval sur deux lignes : « Il faut
    500 » / « 000 F pour ». Sur une carte dont tout l'effet tient au chiffre,
    c'est le chiffre qu'on casse. Meme lecon que sur la vitrine d'Hillary.
    """
    txt = re.sub(r"(\d)\s+(?=\d)", r"\1" + INSEC, txt)          # 500 000
    txt = re.sub(r"(\d)\s+(F|FCFA|€|\$)\b", r"\1" + INSEC + r"\2", txt)  # 000 F
    # ⚠️ en francais la ponctuation double porte une espace AVANT, et cette
    #    espace ne doit jamais casser : le « ? » se retrouvait seul sur la
    #    derniere ligne, et une carte de question qui perd son point
    #    d'interrogation a l'air ratee.
    txt = re.sub(r"\s+([?!:;»])", INSEC + r"\1", txt)
    txt = re.sub(r"([«])\s+", r"\1" + INSEC, txt)
    return txt.split(" ")


def rendu(s):
    return s.replace(INSEC, " ")


def largeur(d, txt, f):
    b = d.textbbox((0, 0), rendu(txt), font=f)
    return b[2] - b[0]


def _greedy(d, mots, f, maxi):
    lignes, courante = [], ""
    for mot in mots:
        essai = (courante + " " + mot).strip()
        if largeur(d, essai, f) <= maxi or not courante:
            courante = essai
        else:
            lignes.append(courante); courante = mot
    if courante:
        lignes.append(courante)
    return lignes


def couper(d, txt, f, maxi):
    """Coupe en lignes SANS jamais couper un mot, et EQUILIBRE les lignes.

    Une coupe gloutonne laisse « site ? » tout seul en bas : le bloc a l'air
    de tomber. On cherche donc la plus PETITE largeur qui tienne encore dans
    le meme nombre de lignes, ce qui repartit les mots au lieu de bourrer les
    premieres. C'est ce que fait `text-wrap: balance` en CSS.
    """
    ms = mots(txt)
    lignes = _greedy(d, ms, f, maxi)
    n = len(lignes)
    if n < 2:
        return lignes
    bas, haut = max(largeur(d, m, f) for m in ms), maxi
    while bas < haut:
        mi = (bas + haut) // 2
        if len(_greedy(d, ms, f, mi)) <= n:
            haut = mi
        else:
            bas = mi + 1
    return _greedy(d, ms, f, haut)


def grain(im, force=7):
    """Un grain fin : le noir plat d'un ecran fait carton, pas cinema.

    ⚠️ TRES leger. Un premier reglage melangeait 14 % de bruit gris et le fond
    remontait a #1a1a1a : sur un telephone ca ne se lit plus comme du noir, ca
    se lit comme du gris sale. Mongazi a demande du NOIR.
    """
    import random
    b = Image.new("L", (im.width // 3, im.height // 3))
    b.putdata([random.randint(0, 255) for _ in range(b.width * b.height)])
    b = b.resize(im.size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(0.5))
    n = Image.merge("RGB", (b, b, b)).point(lambda v: int((v - 128) * force / 255 + 128))
    return Image.blend(im, Image.blend(im, n, 0.5), 0.10)


def carte(texte, chemin, fond=None, sous=None):
    im = Image.new("RGB", (L, H), NOIR)
    if fond and os.path.exists(fond):
        f = Image.open(fond).convert("RGB")
        r = max(L / f.width, H / f.height)
        f = f.resize((round(f.width * r), round(f.height * r)), Image.LANCZOS)
        im.paste(f, ((L - f.width) // 2, (H - f.height) // 2))
    d = ImageDraw.Draw(im)

    # la taille descend jusqu'a ce que le texte tienne en 4 lignes maximum :
    # au-dela, on ne lit plus une question, on lit un paragraphe.
    maxi = L - 2 * MARGE
    for t in range(104, 43, -3):
        f = police(t)
        lignes = couper(d, texte, f, maxi)
        if len(lignes) <= 4:
            break
    inter = int(t * 1.22)
    total = len(lignes) * inter
    y = (H - total) // 2 - (34 if sous else 0)
    for ln in lignes:
        d.text(((L - largeur(d, ln, f)) // 2, y), rendu(ln), font=f, fill=BLANC)
        y += inter

    if sous:
        fp = police(int(t * 0.44))
        d.text(((L - largeur(d, sous, fp)) // 2, y + 26), sous, font=fp,
               fill=(168, 164, 158))

    im = grain(im)
    im.save(chemin, "PNG")
    return len(lignes), t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", type=int, choices=[1, 2, 3])
    ap.add_argument("--fond", default=None)
    a = ap.parse_args()

    os.makedirs(SORTIE, exist_ok=True)
    quels = [a.script] if a.script else [1, 2, 3]
    n = 0
    print("NEBULA · cartes TikTok 1080x1920\n")
    for s in quels:
        nom, qs = SCRIPTS[s]
        for i, q in enumerate(qs, 1):
            p = os.path.join(SORTIE, f"s{s}-{nom}-{i:02d}.png")
            nl, t = carte(q, p, a.fond)
            n += 1
            print(f"  s{s}-{i:02d}  {nl} ligne(s) a {t}px   {q[:52]}")
    p = os.path.join(SORTIE, "z-fin.png")
    carte(FIN[0], p, a.fond, sous=FIN[1])
    n += 1
    print(f"\n  {n} cartes ecrites dans {os.path.relpath(SORTIE, ICI)}/")
    print("  Aucun caractere n'a ete redessine : le texte est exact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

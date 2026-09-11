#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REND L'AFFICHE CARRÉE, ET REFUSE D'ÉCRIRE SI ELLE EST FAUSSE.

⚠️ C'est le point du fichier. Une affiche part chez l'imprimeur : le défaut se
découvre une fois les exemplaires payés. Sur le prospectus Igname, le premier
jet avait le bas coupé de 44 mm. Donc on ne regarde pas « si ça a l'air bien »,
on mesure, et au moindre rouge **rien n'est écrit**.

Les contrôles :
  1. les FONTES ont réellement chargé (sinon Cormorant retombe en serif
     générique, et ça ne se voit pas sur une petite capture) ;
  2. rien ne DÉBORDE du carré, et rien ne sort du cadre doré ;
  3. le QR relu **dans l'image finale rendue** pointe bien sur le domaine
     — pas le QR d'origine, celui qui sera imprimé, oeil de la marque compris ;
  4. les textes obligatoires sont présents (numéro, horaires, domaine) ;
  5. aucune apostrophe droite (') : une affiche se compose en typographie ;
  6. le contraste des textes clés, mesuré sur les PIXELS RENDUS et non sur le
     CSS déclaré (le fond est un dégradé : lire `background-color` ne dit rien).

Sorties : PNG 4320x4320 (36 cm a 300 dpi), PDF carré, JPG léger pour WhatsApp.
"""
import glob, os, sys
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
CLIENT = os.path.dirname(ICI)
os.chdir(CLIENT)

COTE = 1080
ECHELLE = 4                      # 4320 px : 36 cm a 300 dpi, 30 cm a 360 dpi
DOCS = os.path.join("assets", "docs")
PNG = os.path.join(DOCS, "Affiche_Grain_Institut.png")
PDF = os.path.join(DOCS, "Affiche_Grain_Institut.pdf")
JPG = os.path.join(DOCS, "Affiche_Grain_Institut.jpg")
URL = "https://graindesthetique.com"

OBLIGATOIRES = ["01 97 08 55 76", "graindesthetique.com", "Mardi à samedi",
                "09h – 19h", "SOTHYS PARIS", "SULTANE DE SABA", "Sur rendez-vous",
                "Visage", "Corps", "Épilation", "Mains & Pieds", "Soins Avancés",
                "Espace Hommes", "COTONOU · HAIE-VIVE"]

rouges, verts = [], []
def ok(m):  verts.append(m)
def ko(m):  rouges.append(m)


def luminance(rgb):
    c = [v / 255 for v in rgb]
    c = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def contraste(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def main():
    from playwright.sync_api import sync_playwright
    from PIL import Image

    src = os.path.abspath("affiche_institut.html")
    if not os.path.exists(src):
        sys.exit("⛔ affiche_institut.html absent : lance d'abord _build_affiche_institut.py")
    os.makedirs(DOCS, exist_ok=True)

    c = glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome")
    exe = c[0] if c else None

    tmp_png = os.path.join(DOCS, "_tmp_affiche.png")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=exe)
        pg = b.new_page(viewport={"width": COTE, "height": COTE},
                        device_scale_factor=ECHELLE)
        pg.goto("file://" + src, wait_until="networkidle")
        pg.wait_for_timeout(900)

        # 1 · les fontes
        f = pg.evaluate("""() => ({
            cormorant: document.fonts.check("400 33px 'Cormorant Garamond'"),
            cormorant_it: document.fonts.check("italic 400 33px 'Cormorant Garamond'"),
            jost: document.fonts.check("400 17px 'Jost'"),
            chargees: document.fonts.size })""")
        if f["cormorant"] and f["cormorant_it"] and f["jost"]:
            ok(f"fontes chargées (Cormorant droit + italique, Jost) — {f['chargees']} faces")
        else:
            ko(f"FONTES MANQUANTES {f} : l'affiche partirait en serif générique")

        # 2 · débordements
        deb = pg.evaluate("""(cote) => {
            const a = document.getElementById('aff');
            const cadre = a.getBoundingClientRect();
            const out = {taille: [a.scrollWidth, a.scrollHeight], hors: []};
            const marge = 34 + 9;   // le double filet doré
            for (const el of a.querySelectorAll('.z, .z *')) {
              const r = el.getBoundingClientRect();
              if (r.width === 0 || r.height === 0) continue;
              if (r.left < cadre.left + marge - 1 || r.right > cadre.right - marge + 1 ||
                  r.top < cadre.top + marge - 1 || r.bottom > cadre.bottom - marge + 1) {
                out.hors.push({
                  t: (el.textContent || el.className || el.tagName).toString().trim().slice(0, 34),
                  x: Math.round(r.left), y: Math.round(r.top),
                  w: Math.round(r.width), h: Math.round(r.height)});
              }
            }
            return out; }""", COTE)
        if deb["taille"] == [COTE, COTE]:
            ok(f"le carré fait bien {COTE}x{COTE}, rien ne le fait grandir")
        else:
            ko(f"LE CARRÉ DÉBORDE : {deb['taille']} au lieu de [{COTE}, {COTE}]")
        if not deb["hors"]:
            ok("aucun élément ne sort du cadre doré")
        else:
            for e in deb["hors"][:6]:
                ko(f"HORS CADRE : « {e['t']} » a ({e['x']},{e['y']}) {e['w']}x{e['h']}")

        # 4 · les textes obligatoires
        txt = pg.inner_text("#aff")
        manque = [t for t in OBLIGATOIRES if t not in txt]
        ok(f"{len(OBLIGATOIRES)} textes obligatoires présents") if not manque \
            else ko(f"TEXTES MANQUANTS : {manque}")

        # 5 · typographie
        ko("APOSTROPHE DROITE dans l'affiche") if "'" in txt else ok("apostrophes typographiques")

        # 6 · contraste sur les pixels rendus
        mesures = []
        for sel, nom, mini in [(".fam-t", "nom de famille de soins", 4.5),
                               (".cta", "l'appel a l'action", 4.5),
                               (".web", "l'adresse du site", 4.5),
                               (".infos .it", "le téléphone", 4.5),
                               (".lieu", "la ville", 4.5)]:
            m = pg.evaluate("""(sel) => {
                const el = document.querySelector(sel); if (!el) return null;
                const st = getComputedStyle(el); const r = el.getBoundingClientRect();
                return {couleur: st.color, x: r.left, y: r.top, w: r.width, h: r.height}; }""", sel)
            if m: mesures.append((sel, nom, mini, m))
        pg.screenshot(path=tmp_png, clip={"x": 0, "y": 0, "width": COTE, "height": COTE})

        # on masque le texte pour photographier le FOND sous lui
        pg.evaluate("""() => { for (const s of ['.fam-t','.cta','.web','.infos','.lieu'])
            document.querySelectorAll(s).forEach(e => e.style.visibility='hidden'); }""")
        fond_png = os.path.join(DOCS, "_tmp_fond.png")
        pg.screenshot(path=fond_png, clip={"x": 0, "y": 0, "width": COTE, "height": COTE})
        b.close()

    im = Image.open(tmp_png).convert("RGB")
    fond = Image.open(fond_png).convert("RGB")
    for sel, nom, mini, m in mesures:
        # ⚠️ on reléve le FOND, jamais le texte : le décile le plus clair d'une
        #    zone de texte, ce sont les lettres elles-mémes ou leur anticrénelage.
        z = fond.crop((int(m["x"] * ECHELLE), int(m["y"] * ECHELLE),
                       int((m["x"] + m["w"]) * ECHELLE), int((m["y"] + m["h"]) * ECHELLE)))
        px = np.asarray(z).reshape(-1, 3)
        f_moy = tuple(int(v) for v in np.median(px, axis=0))
        col = m["couleur"]
        rgb = tuple(int(v) for v in col[col.find("(") + 1:col.find(")")].split(",")[:3])
        r = contraste(rgb, f_moy)
        (ok if r >= mini else ko)(f"contraste {nom} : {r:.1f}:1 (minimum {mini})")

    # 3 · le QR, relu dans l'image finale
    import cv2
    arr = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
    lu, _, _ = cv2.QRCodeDetector().detectAndDecode(arr)
    if lu == URL:
        ok(f"QR relu dans l'image RENDUE : « {lu} »")
    else:
        ko(f"QR ILLISIBLE OU FAUX dans l'image rendue : « {lu }» (attendu {URL})")

    print("\n".join("  ✅ " + v for v in verts))
    if rouges:
        print("\n".join("  ⛔ " + r for r in rouges))
        for f in (tmp_png, fond_png):
            os.path.exists(f) and os.remove(f)
        sys.exit(f"\n⛔ {len(rouges)} contrôle(s) rouge(s) : RIEN N'A ÉTÉ ÉCRIT.")

    os.replace(tmp_png, PNG)
    os.path.exists(fond_png) and os.remove(fond_png)
    # ⚠️ Le JPG n'est PAS l'image d'impression : c'est celle qu'on envoie sur
    #    WhatsApp. Envoyer 4320 px, c'est laisser WhatsApp recompresser sauvagement
    #    une image qu'il va de toute façon réduire. On réduit proprement avant.
    im.resize((1600, 1600), Image.LANCZOS).save(JPG, quality=90, subsampling=0, optimize=True)

    # le PDF, a la même géométrie carrée
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=exe)
        pg = b.new_page(viewport={"width": COTE, "height": COTE})
        pg.goto("file://" + src, wait_until="networkidle"); pg.wait_for_timeout(700)
        pg.pdf(path=PDF, width=f"{COTE}px", height=f"{COTE}px", print_background=True,
               margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        b.close()

    print(f"\n  {len(verts)} contrôles verts, 0 rouge.")
    print(f"  PNG  {PNG}  {im.size[0]}x{im.size[1]}  {os.path.getsize(PNG)//1024} Ko")
    print(f"  PDF  {PDF}  {os.path.getsize(PDF)//1024} Ko")
    print(f"  JPG  {JPG}  {os.path.getsize(JPG)//1024} Ko  1600px (pour WhatsApp)")
    print(f"  → impression nette jusqu'a 36 x 36 cm a 300 dpi.")


if __name__ == "__main__":
    main()

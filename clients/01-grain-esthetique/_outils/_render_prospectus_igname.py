#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rend le prospectus A5 recto-verso en PNG (impression) + PDF 2 pages.

Contrôle AVANT d'écrire quoi que ce soit : si une page déborde de l'A5 ou si un
texte obligatoire manque, on n'écrit rien. Un prospectus dont le bas est coupé
part chez l'imprimeur et se voit une fois les 500 exemplaires payés.
"""
import glob
import os
import sys

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "assets", "docs")
SRC = os.path.join(ROOT, "_outils", "prospectus_igname.html")
SITE = "https://graindesthetique.com"
PDF = os.path.join(DOCS, "Prospectus_Igname_A5.pdf")
PNG_R = os.path.join(DOCS, "Prospectus_Igname_A5_recto.png")
PNG_V = os.path.join(DOCS, "Prospectus_Igname_A5_verso.png")

# A5 = 148 x 210 mm. À 96 dpi : 559 x 794 px. Facteur 4 → ~384 dpi à l'impression.
VIEWPORT = {"width": 560, "height": 794}
ECHELLE = 4
PX_PAR_MM = 96 / 25.4

# Textes qui doivent figurer, sinon le prospectus ne sert à rien
OBLIGATOIRES = [
    "Fête de l’Igname", "La fête se prépare", "01 97 08 55 76",
    "graindesthetique.com", "Haie-Vive", "sur rendez-vous",
]


def chromium_du_systeme():
    """Le Chromium préinstallé (PLAYWRIGHT_BROWSERS_PATH) ne porte pas forcément le
    numéro de build attendu par la version de playwright installée. On le pointe
    directement plutôt que de retélécharger."""
    for motif in ("/opt/pw-browsers/chromium-*/chrome-linux/chrome",
                  "/opt/pw-browsers/chromium/chrome-linux/chrome"):
        trouve = sorted(glob.glob(motif))
        if trouve:
            return trouve[-1]
    return None


def qr_lisible(png):
    """Relit le QR DANS l'image finale. Un QR juste au moment où on le fabrique et
    illisible une fois rendu, ça ne se voit qu'imprimé."""
    try:
        import cv2
        import numpy as np
        from PIL import Image
    except ImportError:
        print("  (QR non relu : opencv absent)")
        return None
    arr = np.array(Image.open(png).convert("RGB"))[:, :, ::-1]
    ok, infos, _, _ = cv2.QRCodeDetector().detectAndDecodeMulti(arr)
    if not ok or not infos:
        return "aucun QR détectable dans le rendu"
    if infos[0] != SITE:
        return f"le QR pointe sur « {infos[0] } » au lieu de « {SITE} »"
    print(f"  QR relu dans le rendu → {infos[0]}")
    return None


MESURE = """() => [...document.querySelectorAll('.page')].map(pg => {
  const inner = pg.querySelector('.inner');
  const cs = getComputedStyle(inner);
  let h = parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom);
  let large = 0;
  for (const el of inner.children) {
    if (el.classList.contains('spacer')) continue;
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    h += r.height + parseFloat(s.marginTop) + parseFloat(s.marginBottom);
    large = Math.max(large, el.scrollWidth);
  }
  return {
    dispo: pg.getBoundingClientRect().height,
    contenu: h,
    largeurDispo: inner.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight),
    largeurContenu: large,
  };
})"""


def main() -> int:
    exe = chromium_du_systeme()
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        pg = b.new_page(viewport=VIEWPORT, device_scale_factor=ECHELLE)
        pg.goto("file://" + SRC, wait_until="networkidle")
        pg.wait_for_timeout(900)

        pages = pg.locator(".page")
        mesures = pg.evaluate(MESURE)
        texte = pg.inner_text("body")
        ennuis = []

        if pages.count() != 2:
            ennuis.append(f"{pages.count()} page(s) au lieu de 2")

        for i, m in enumerate(mesures):
            nom = "recto" if i == 0 else "verso"
            debord = (m["contenu"] - m["dispo"]) / PX_PAR_MM
            reste = -debord
            print(f"  {nom} : contenu {m['contenu']/PX_PAR_MM:6.1f} mm "
                  f"sur {m['dispo']/PX_PAR_MM:.0f} mm · marge restante {reste:+5.1f} mm")
            if debord > 0:
                ennuis.append(f"{nom} déborde de {debord:.1f} mm")
            elif reste < 3:
                ennuis.append(f"{nom} n'a que {reste:.1f} mm de marge, trop juste")
            if m["largeurContenu"] > m["largeurDispo"] + 1:
                ennuis.append(f"{nom} déborde en largeur "
                              f"({(m['largeurContenu']-m['largeurDispo'])/PX_PAR_MM:.1f} mm)")

        for attendu in OBLIGATOIRES:
            if attendu not in texte:
                ennuis.append(f"texte manquant : « {attendu} »")

        if "'" in texte.replace("l'oeil", ""):
            ennuis.append("apostrophe droite ' trouvée dans le texte, utiliser ’")

        if ennuis:
            print("\n⛔ RIEN N'A ÉTÉ ÉCRIT :")
            for e in ennuis:
                print("   ·", e)
            b.close()
            return 1

        os.makedirs(DOCS, exist_ok=True)
        pages.nth(0).screenshot(path=PNG_R)
        pages.nth(1).screenshot(path=PNG_V)
        souci = qr_lisible(PNG_V)
        if souci:
            print("\n⛔ QR :", souci)
            b.close()
            return 1
        pg.pdf(path=PDF, width="148mm", height="210mm", print_background=True,
               margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        b.close()

    print("\n✓ contrôles passés")
    for f in (PNG_R, PNG_V, PDF):
        print(f"  {os.path.basename(f):38s} {os.path.getsize(f)//1024:5d} Ko")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""
ANGY ART — la carte de visite d'Angélique, et son QR.

    python _carte.py                 -> les quatre fichiers
    python _carte.py --url https://…  -> pour essayer une autre adresse

Produit dans `assets/docs/` :

  Carte_Angy_Art_recto-verso.pdf   91 x 61 mm, 2 pages, FOND PERDU 3 mm.
                                   C'est le fichier d'imprimeur. Coupe 85 x 55.
  Carte_Angy_Art_planche_A4.pdf    8 cartes par page, bord à bord, 2 pages
                                   (rectos puis versos). Pour le petit atelier
                                   de Cotonou qui imprime un A4 et massicote.
  Carte_Angy_Art_apercu.png        recto et verso côte à côte, pour WhatsApp.
  assets/images/qr/qr-carte.png    le QR seul, réutilisable.

--------------------------------------------------------------------------
CE QUE CE SCRIPT REFUSE DE FAIRE
--------------------------------------------------------------------------
Une carte de visite est la seule pièce du livrable qu'on ne peut plus
corriger : elle part chez l'imprimeur, elle revient en cinq cents
exemplaires. Donc rien n'est écrit sur la foi de ce que le code voulait
faire, tout est mesuré sur ce que le rendu donne.

⛔ Il refuse si le QR ne se décode pas **depuis l'image rendue à 600 ppp**,
   et pas seulement depuis le PNG qu'il vient de fabriquer. Un QR peut être
   parfait dans son fichier et se retrouver écrasé, flouté ou rogné par la
   mise en page. C'est le pixel imprimé qui compte.

⛔ Il refuse si un module du QR mesure moins d'un demi-millimètre sur le
   papier. En dessous, un téléphone décroche sur une impression ordinaire.

⛔ Il refuse si Playfair Display ou Public Sans n'a pas chargé. Elles
   viennent du réseau : sans connexion, Chromium retombe silencieusement sur
   Georgia et Helvetica, le PDF a l'air correct, et la carte n'est plus la
   sienne. C'est le genre de panne qu'on découvre sur le papier.

⛔ Il refuse si l'adresse du QR ne répond pas — sauf avec --sans-reseau.
   Un QR qui mène à une page de parking est pire qu'une carte sans QR.
"""
import argparse
import functools
import http.server
import io
import os
import socketserver
import sys
import threading
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ICI = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ICI, "assets", "docs")
QR = os.path.join(ICI, "assets", "images", "qr", "qr-carte.png")

URL = "https://angyart.online"

# La carte, en millimètres.
COUPE_L, COUPE_H = 85.0, 55.0     # le format fini
PERDU = 3.0                       # le fond perdu, de chaque côté
PAGE_L, PAGE_H = COUPE_L + 2 * PERDU, COUPE_H + 2 * PERDU
QR_MM = 20.0                      # le côté du QR sur le papier
PPP = 600                         # la définition des rendus

MM = 96 / 25.4                    # un millimètre, en pixels CSS


class Muet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


# ---------------------------------------------------------------- le QR
def fabriquer_qr(url):
    """Écrit le QR et rend son nombre de modules, zone de silence comprise."""
    import segno

    os.makedirs(os.path.dirname(QR), exist_ok=True)
    # Correction M (15 %) et non Q : sur une carte, ce qui fait décrocher un
    # téléphone n'est pas la rayure, c'est la finesse des modules. M tient
    # l'adresse en version 2 (25 modules) là où Q imposerait la version 3
    # (29) — soit des modules 16 % plus gros pour la même surface de papier.
    code = segno.make(url, error="m", mode="byte", boost_error=False)
    bord = 4                       # la zone de silence exigée par la norme
    cotes = code.symbol_size(scale=1, border=bord)[0]
    code.save(QR, scale=40, border=bord, dark="#0a0a0a", light="#f3efe6")
    return cotes


def decoder(png_bytes, quoi):
    """Décode un QR dans une image, par deux lecteurs indépendants."""
    import numpy as np
    import cv2
    from PIL import Image

    im = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    arr = np.array(im)[:, :, ::-1].copy()

    lus = set()
    t, _, _ = cv2.QRCodeDetector().detectAndDecode(arr)
    if t:
        lus.add(("opencv", t))
    try:
        from pyzbar.pyzbar import decode as zb
        for r in zb(im):
            lus.add(("zbar", r.data.decode("utf-8")))
    except Exception as e:
        print(f"   . zbar indisponible ({type(e).__name__})")

    if not lus:
        raise SystemExit(f"⛔ ARRÊT — aucun lecteur n'a décodé le QR sur {quoi}.")
    textes = {t for _, t in lus}
    if len(textes) > 1:
        raise SystemExit(f"⛔ ARRÊT — deux lectures différentes sur {quoi} : {textes}")
    for lecteur, t in sorted(lus):
        print(f"   . {quoi} · {lecteur} → {t}")
    return textes.pop()


# ------------------------------------------------------------- le rendu
def rendre(url_attendue, sans_reseau):
    from playwright.sync_api import sync_playwright

    os.makedirs(DOCS, exist_ok=True)
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Muet, directory=ICI))
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    faces = {}
    try:
        with sync_playwright() as p:
            nav = p.chromium.launch()

            # --- 1. le PDF d'imprimeur, en vectoriel
            page = nav.new_page(viewport={"width": round(PAGE_L * MM),
                                          "height": round(PAGE_H * MM)})
            page.goto(f"http://127.0.0.1:{port}/carte.html", wait_until="networkidle")
            page.wait_for_timeout(1200)
            verifier_polices(page)
            pdf = os.path.join(DOCS, "Carte_Angy_Art_recto-verso.pdf")
            page.pdf(path=pdf, width=f"{PAGE_L}mm", height=f"{PAGE_H}mm",
                     print_background=True,
                     margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
            page.close()

            # --- 2. les deux faces à 600 ppp, pour la planche et l'aperçu
            page = nav.new_page(viewport={"width": round(PAGE_L * MM),
                                          "height": round(PAGE_H * MM)},
                                device_scale_factor=PPP / 96)
            page.goto(f"http://127.0.0.1:{port}/carte.html", wait_until="networkidle")
            page.wait_for_timeout(1200)
            verifier_polices(page)
            for nom, sel in (("recto", ".recto"), ("verso", ".verso")):
                faces[nom] = page.locator(sel).screenshot()
            page.close()
            nav.close()
    finally:
        srv.shutdown()

    # --- 3. le contrôle qui compte : décoder le QR sur le PIXEL RENDU
    lu = decoder(faces["verso"], "le verso rendu à 600 ppp")
    if lu != url_attendue:
        raise SystemExit(f"⛔ ARRÊT — le QR rendu dit {lu!r}, on attendait {url_attendue!r}.")

    return faces


def verifier_polices(page):
    """Chromium retombe en silence sur Georgia si le réseau manque."""
    page.evaluate("() => document.fonts.ready")
    manquantes = page.evaluate("""() => {
      const veut = [["Playfair Display","italic 400 16px"],["Public Sans","300 16px"]];
      return veut.filter(([f,d]) => !document.fonts.check(`${d} "${f}"`)).map(x => x[0]);
    }""")
    if manquantes:
        raise SystemExit("⛔ ARRÊT — police absente : " + ", ".join(manquantes) +
                         ".\n   Google Fonts n'a pas répondu. La carte serait imprimée"
                         " dans une autre typographie que la sienne.")


# ----------------------------------------------------------- la planche
def planche(faces):
    """8 cartes par page, bord à bord : un coup de massicot sépare deux voisines."""
    from PIL import Image

    px = lambda mm: round(mm / 25.4 * PPP)
    A4 = (px(210), px(297))
    cols, lignes = 2, 4
    cl, ch = px(COUPE_L), px(COUPE_H)
    ox, oy = (A4[0] - cols * cl) // 2, (A4[1] - lignes * ch) // 2

    pages = []
    for nom in ("recto", "verso"):
        # on retire le fond perdu : la planche est au format fini
        f = Image.open(io.BytesIO(faces[nom])).convert("RGB")
        b = round(PERDU / 25.4 * PPP)
        f = f.crop((b, b, f.width - b, f.height - b)).resize((cl, ch), Image.LANCZOS)

        feuille = Image.new("RGB", A4, "#ffffff")
        for r in range(lignes):
            for c in range(cols):
                feuille.paste(f, (ox + c * cl, oy + r * ch))
        marques(feuille, ox, oy, cl, ch, cols, lignes)
        # ⚠️ Les huit cartes sont identiques, donc aucun miroir de colonnes n'est
        #    utile — un premier jet en posait un, ce qui donnait l'illusion que le
        #    recto-verso était géré. La seule règle qui compte est ailleurs, et
        #    elle est invisible dans le fichier : RETOURNEMENT SUR LE BORD LONG.
        #    Sur le bord court, la feuille tourne de 180° et tous les versos
        #    sortent à l'envers. On l'écrit donc dans la marge, là où l'atelier
        #    d'impression regarde.
        legende(feuille, nom, oy)
        pages.append(feuille)

    sortie = os.path.join(DOCS, "Carte_Angy_Art_planche_A4.pdf")
    pages[0].save(sortie, "PDF", resolution=PPP, save_all=True, append_images=pages[1:])
    return sortie


def legende(im, nom, oy):
    """La consigne d'impression, dans la marge : jamais sur une carte."""
    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(im)
    txt = ("RECTOS — imprimer en recto-verso, RETOURNEMENT SUR LE BORD LONG"
           if nom == "recto" else
           "VERSOS — si les dos sortent à l'envers, le retournement était sur le bord court")
    try:
        f = ImageFont.truetype("arial.ttf", round(3.1 / 25.4 * PPP))
    except Exception:
        f = ImageFont.load_default()
    d.text((round(14 / 25.4 * PPP), oy - round(11 / 25.4 * PPP)), txt, fill="#9a9a9a", font=f)


def marques(im, ox, oy, cl, ch, cols, lignes):
    """Traits de coupe, dans la marge seulement : jamais sur une carte."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    long_ = round(4 / 25.4 * PPP)
    ep = max(1, round(.12 / 25.4 * PPP))
    for c in range(cols + 1):
        x = ox + c * cl
        d.line([(x, oy - long_), (x, oy - ep * 2)], fill="#909090", width=ep)
        d.line([(x, oy + lignes * ch + ep * 2), (x, oy + lignes * ch + long_)],
               fill="#909090", width=ep)
    for r in range(lignes + 1):
        y = oy + r * ch
        d.line([(ox - long_, y), (ox - ep * 2, y)], fill="#909090", width=ep)
        d.line([(ox + cols * cl + ep * 2, y), (ox + cols * cl + long_, y)],
               fill="#909090", width=ep)


def apercu(faces):
    """Recto et verso côte à côte, à l'échelle : ce qu'on envoie sur WhatsApp."""
    from PIL import Image
    ims = [Image.open(io.BytesIO(faces[n])).convert("RGB") for n in ("recto", "verso")]
    ech = 1400 / ims[0].width
    ims = [i.resize((round(i.width * ech), round(i.height * ech)), Image.LANCZOS) for i in ims]
    marge, entre = 60, 44
    L = marge * 2 + ims[0].width + entre + ims[1].width
    H = marge * 2 + ims[0].height
    p = Image.new("RGB", (L, H), "#8a8a8a")
    p.paste(ims[0], (marge, marge))
    p.paste(ims[1], (marge + ims[0].width + entre, marge))
    sortie = os.path.join(DOCS, "Carte_Angy_Art_apercu.png")
    p.save(sortie, optimize=True)
    return sortie


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=URL)
    ap.add_argument("--sans-reseau", action="store_true",
                    help="ne pas exiger que l'adresse réponde (le domaine n'est pas encore branché)")
    a = ap.parse_args()

    print(f"\n  ANGY ART · carte de visite — {COUPE_L:.0f} x {COUPE_H:.0f} mm\n")

    # --- l'adresse répond-elle ?
    if a.sans_reseau:
        print(f"   ⚠️  {a.url} n'est PAS vérifiée (--sans-reseau).")
        print("      NE PAS IMPRIMER tant que le domaine ne répond pas.")
    else:
        verifier_adresse(a.url)

    # --- le QR
    cotes = fabriquer_qr(a.url)
    module = QR_MM / cotes
    print(f"   . QR : {cotes} modules sur {QR_MM:.0f} mm → {module:.3f} mm le module")
    if module < 0.5:
        raise SystemExit(f"⛔ ARRÊT — module de {module:.3f} mm, en dessous du demi-millimètre.")
    decoder(open(QR, "rb").read(), "le fichier QR")

    # --- le rendu, et le contrôle sur le pixel
    faces = rendre(a.url, a.sans_reseau)
    pl = planche(faces)
    ap_ = apercu(faces)

    print("\n  Écrit :")
    for f in (os.path.join(DOCS, "Carte_Angy_Art_recto-verso.pdf"), pl, ap_, QR):
        print(f"   . {os.path.relpath(f, ICI):<48} {os.path.getsize(f) // 1024} Ko")
    print(f"\n  Coupe {COUPE_L:.0f} x {COUPE_H:.0f} mm · fond perdu {PERDU:.0f} mm"
          f" · page {PAGE_L:.0f} x {PAGE_H:.0f} mm\n")


def verifier_adresse(url):
    r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (NEBULA carte)"})
    try:
        with urllib.request.urlopen(r, timeout=20) as rep:
            corps = rep.read(4000).decode("utf-8", "replace")
            code = rep.status
    except urllib.error.HTTPError as e:
        code, corps = e.code, ""
    except Exception as e:
        raise SystemExit(f"⛔ ARRÊT — {url} ne répond pas ({type(e).__name__}).\n"
                         "   Le domaine n'est pas encore branché. Relancer avec"
                         " --sans-reseau pour préparer sans imprimer.")
    if code != 200:
        raise SystemExit(f"⛔ ARRÊT — {url} répond {code}.")
    if "Angy" not in corps and "Angélique" not in corps:
        raise SystemExit(f"⛔ ARRÊT — {url} répond 200 mais ce n'est pas son site"
                         " (page de parking ?).")
    print(f"   . {url} répond 200 et c'est bien son site")


if __name__ == "__main__":
    main()

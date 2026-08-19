# -*- coding: utf-8 -*-
"""
QC DU CATALOGUE — Au Braisé d'Or.

    cd clients/09-au-braise-dor/experience && npm run build
    python ../_outils/_qc.py

Il sert le dossier `experience/out` et regarde la carte comme un client la
regarde : en 390 et en 1440.

⚠️ TROIS PIÈGES D'INSTRUMENT, tous payés ici le 2026-08-19. Un contrôle faux
coûte plus cher qu'un contrôle absent, parce qu'on le croit.

1. SERVEUR MULTI-TÂCHES. Avec un `TCPServer` mono-tâche, le QC d'Hillary
   échouait une fois sur deux sur « Page.goto: Timeout ». Ce n'était pas le
   site, c'était le serveur de test.

2. DEUX DIALOGUES DANS CETTE PAGE. Le tiroir des univers est monté en
   permanence et vient en premier dans le DOM : `querySelector('[role=dialog]')`
   mesure le tiroir, pas la fiche de commande. On vise par l'étiquette.

3. ON NE MESURE PAS UN CONTRASTE AU « DÉCILE LE PLUS CLAIR » QUAND LE TEXTE
   COUVRE UN DIXIÈME DE LA BOÎTE. Le décile tombe alors dans l'anticrénelage
   et annonce 2,15:1 sur une pastille parfaitement nette, vérifiée à l'œil.
   Ici la couleur du texte est DÉCLARÉE (donc solide et connue) et seul le
   fond dépend de la photo posée dessous : on déclare l'une, on mesure l'autre.
   ⚠️ Et on neutralise l'animation d'apparition avant de photographier, sinon
   on mesure le contraste d'un fondu.
"""
import functools, http.server, io, os, socketserver, sys, threading
from playwright.sync_api import sync_playwright
from PIL import Image

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experience", "out")
RACINE = os.path.normpath(RACINE)
VUES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_vues")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# Les 13 plats que la propriétaire a fait retirer le 2026-08-19 (note
# manuscrite « Correction pour Au Braisé d'Or »). Ils ne doivent réapparaître
# ni par une régénération, ni par un retour en arrière mal ciblé.
RETIRES = [
    "Napolitaine", "Oriental", "Margherita", "Pili chaud", "À la crème", "Pêcheur",
    # ⚠️ « Lapin » seul, pas toute la ligne : Mongazi a confirmé le 19/08 au
    # soir que LE MOUTON FRIT RESTE, au même prix. La note manuscrite disait
    # « Lapin », on avait d'abord retiré la ligne entière « lapin ou mouton
    # frit » et donc supprimé un plat que la maison vend toujours.
    "Lapin", "Viande de caille",
    "Crispy poulet", "Nugget pomme au four",
    "JOQ Viagra", "Mojito", "Piña Colada",
]

# la carte est la vérité : le QC compte les plats dans les données, il n'en
# recopie jamais le nombre. Une carte qui grandit ne doit pas rendre le QC faux.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def plats_attendus():
    """Compte les plats dans `experience/data/carte.ts`, sans les retaper."""
    src = os.path.join(RACINE, "..", "data", "carte.ts")
    txt = io.open(os.path.normpath(src), encoding="utf-8").read()
    return txt.count("      { n: ")


def lum(c):
    def f(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def contraste(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


class Serveur(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    if not os.path.isdir(RACINE):
        sys.exit("⛔ %s est absent : lancer `npm run build` dans experience/ d'abord." % RACINE)
    os.makedirs(VUES, exist_ok=True)
    attendu = plats_attendus()

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=RACINE)
    srv = Serveur(("127.0.0.1", 0), handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    ok, ko = [], []

    def dire(bon, txt):
        (ok if bon else ko).append(txt)
        print(("  vert  " if bon else "  ROUGE ") + txt)

    with sync_playwright() as p:
        nav = p.chromium.launch(executable_path=CHROME)

        for nom, largeur, hauteur in [("mobile", 390, 844), ("bureau", 1440, 900)]:
            pg = nav.new_page(viewport={"width": largeur, "height": hauteur},
                              device_scale_factor=2)
            erreurs, mauvais = [], []
            pg.on("console", lambda m: erreurs.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: erreurs.append(str(e)))
            pg.on("response",
                  lambda r: mauvais.append("%d %s" % (r.status, r.url)) if r.status >= 400 else None)

            pg.goto("http://127.0.0.1:%d/" % port, wait_until="networkidle", timeout=60000)
            pg.wait_for_timeout(1500)
            pg.evaluate("""() => { const e = document.getElementById('cat-petitdej');
                window.__lenis ? window.__lenis.scrollTo(e, { immediate: true }) : e.scrollIntoView(); }""")
            pg.wait_for_timeout(1800)
            pg.screenshot(path=os.path.join(VUES, "%s-petitdej.png" % nom))

            n = pg.evaluate("document.querySelectorAll('.ct-item').length")
            dire(n == attendu, "[%s] %d plats affichés (la carte en compte %d)" % (nom, n, attendu))

            sans = pg.evaluate("""() => [...document.querySelectorAll('.ct-item')]
                .filter(a => !a.querySelector('img'))
                .map(a => { const t = a.querySelector('.police-titre');
                            const r = t.getBoundingClientRect();
                            return { nom: t.textContent, w: r.width, h: r.height }; })""")
            for s in sans:
                dire(s["w"] > 20 and s["h"] > 8,
                     "[%s] ardoise « %s » lisible : %dx%d px" % (nom, s["nom"], s["w"], s["h"]))

            casse = pg.evaluate("""() => [...document.querySelectorAll('img')]
                .filter(i => i.complete && i.naturalWidth === 0).map(i => i.currentSrc || i.src)""")
            dire(not casse, "[%s] 0 image cassée%s" % (nom, "" if not casse else " → %s" % casse[:3]))
            dire(not any("undefined" in (m or "") for m in mauvais),
                 "[%s] aucun /carte/undefined.webp demandé" % nom)

            deb = pg.evaluate(
                "document.documentElement.scrollWidth - document.documentElement.clientWidth")
            dire(deb <= 0, "[%s] débordement horizontal : %d px" % (nom, deb))

            # ⚠️ la fiche, visée par son étiquette (voir piège 2)
            pg.evaluate("""() => [...document.querySelectorAll('.ct-item')]
                .find(x => !x.querySelector('img')).click()""")
            pg.wait_for_timeout(900)
            fiche = pg.evaluate("""() => {
                const d = document.querySelector('[role=dialog][aria-label^="Commander"]');
                if (!d) return null;
                const b = [...d.querySelectorAll('button')].find(x => /Ajouter/.test(x.textContent || ''));
                return { titre: d.querySelector('h3')?.textContent,
                         bouton: b ? b.textContent.trim() : null,
                         img: !!d.querySelector('img') }; }""")
            dire(fiche is not None, "[%s] la fiche s'ouvre sur un plat sans photo" % nom)
            if fiche:
                dire(not fiche["img"],
                     "[%s] la fiche n'appelle aucune image : ardoise « %s »" % (nom, fiche["titre"]))
                dire(bool(fiche["bouton"]), "[%s] le bouton de commande est là : %s" % (nom, fiche["bouton"]))

            # ── ce que la propriétaire a fait retirer le 2026-08-19 ──────
            # ⚠️ un plat retiré de la carte mais laissé sur la page se
            # commande quand même : le client paie pour un plat qui n'existe
            # plus, et c'est le restaurant qui gère la déception.
            page = pg.evaluate("document.getElementById('carte').innerText")
            for parti in RETIRES:
                dire(parti not in page, "[%s] « %s » n'est plus sur la carte" % (nom, parti))

            # ⚠️ AUCUN « 0 F » NULLE PART. Un plat dont la maison n'a pas
            # encore donné le prix porte « Prix sur demande », jamais zéro.
            dire("0 F" not in page.replace("00 F", "").replace("0 F\n", "0 F "),
                 "[%s] aucun prix affiché à 0 F" % nom)

            dire(not erreurs, "[%s] 0 erreur console%s" % (nom, "" if not erreurs else " → %s" % erreurs[:2]))
            dire(not mauvais, "[%s] 0 réponse ≥ 400%s" % (nom, "" if not mauvais else " → %s" % mauvais[:3]))
            pg.close()

        # ── LE PRIX SE LIT-IL ? (voir piège 3) ────────────────────────────
        pg = nav.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=3,
                          reduced_motion="reduce")
        pg.goto("http://127.0.0.1:%d/" % port, wait_until="networkidle", timeout=60000)
        pg.wait_for_timeout(1200)
        pg.add_style_tag(content=".ct-item{opacity:1!important;visibility:visible!important;transform:none!important}")
        for cat in ["grillades", "pizza", "petitdej", "cocktails"]:
            pg.evaluate("""(c) => { const e = document.getElementById('cat-' + c);
                window.__lenis ? window.__lenis.scrollTo(e, { immediate: true }) : e.scrollIntoView(); }""", cat)
            pg.wait_for_timeout(2000)
            cartes = pg.locator("#cat-%s .ct-item" % cat)
            pire, pire_nom = 99.0, ""
            for i in range(cartes.count()):
                carte = cartes.nth(i)
                past = carte.locator("span.absolute.bottom-2").first
                if not past.is_visible():
                    continue
                coul = past.evaluate("e => getComputedStyle(e).color")
                texte = tuple(int(v) for v in coul[coul.index("(") + 1:coul.index(")")].split(",")[:3])
                im = Image.open(io.BytesIO(past.screenshot())).convert("RGB")
                px = sorted(im.getdata(), key=lum)
                fond = px[len(px) // 4]
                r = contraste(texte, fond)
                if r < pire:
                    pire, pire_nom = r, carte.locator("p.police-titre").last.inner_text()
            dire(pire >= 4.5, "[prix] %s : la pastille la moins lisible est « %s » à %.1f:1"
                 % (cat, pire_nom, pire))
        pg.close()
        nav.close()

    srv.shutdown()
    print("\n%d verts, %d rouges" % (len(ok), len(ko)))
    if ko:
        print("ROUGE :")
        for k in ko:
            print("  - " + k)
    return 1 if ko else 0


if __name__ == "__main__":
    sys.exit(main())

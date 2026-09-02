"""QC du back-office de création · MINUIT

    cd vitrina/lettre && python3 _qc_creer.py

Il remplit VRAIMENT les onze étapes dans un navigateur, monte la lettre, et
vérifie que la lettre produite fonctionne. Aucun envoi réel : la route
/api/order est interceptée.

Les contrôles qui comptent :
  · la sauvegarde survit à une fermeture d'onglet (le défaut le plus cher)
  · la lettre montée est une VRAIE lettre qui s'ouvre avec le bon code
  · le contenu tapé se retrouve dedans, et rien d'autre
  · aucune photo inventée quand le client n'en met pas
  · on ne peut pas envoyer sans référence de transaction
"""
import glob
import http.server
import json
import os
import re
import socketserver
import sys
import threading

from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
PORT = 8731

ok = 0
rouges = []


def t(nom, cond, info=""):
    global ok
    if cond:
        ok += 1
        print(f"  OK   {nom}")
    else:
        rouges.append(nom)
        print(f"  ROUGE {nom}   {info}")


class Serveur(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ICI, **k)

    def log_message(self, *a):
        pass

    def do_GET(self):
        # Le formulaire lit le compte Mobile Money sur le serveur.
        if self.path.startswith("/api/config"):
            corps = json.dumps({
                "momo_name": "NEBULA Agency",
                "momo_number": "0197085576",
                "momo_network": "MTN MoMo",
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(corps)))
            self.end_headers()
            self.wfile.write(corps)
            return
        super().do_GET()


# ⚠️ Un serveur mono-tâche fait échouer le QC une fois sur deux (leçon Hillary
# et Angy Art : « Page.goto: Timeout » qui n'est pas un défaut du site).
class Fil(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def attendre_iframe(pg, sel, vise, plafond_ms=8000):
    """Attend que le script de l'apercu ait ecrit sa valeur. Rend ce qu'il lit."""
    lu = None
    for _ in range(plafond_ms // 50):
        lu = pg.evaluate("""(s) => { try {
              const d = document.querySelector('#cadre').contentDocument;
              const e = d && d.querySelector(s);
              return e ? e.textContent.trim() : null;
            } catch (x) { return null; } }""", sel)
        if lu == vise:
            return lu
        pg.wait_for_timeout(50)
    return lu


def main():
    src = open(os.path.join(ICI, "creer.html"), encoding="utf-8").read()

    print("\n=== 1. Le fichier se tient ===")
    # ⚠️ Chercher "const LETTRE" ici donnait un FAUX ROUGE : creer.html
    # ECRIT cette ligne pour la lettre montee, c'est normal. Ce qui prouverait
    # une recopie, c'est la presence du CONTENU d'exemple du gabarit.
    t("il va chercher le gabarit au lieu de le recopier",
      'fetch("gabarit.html"' in src
      and ".enveloppe{" not in src and "#seuil{" not in src,
      "le contenu du gabarit est recopie dans creer.html : deux verites")
    t("il sauvegarde a chaque frappe", "localStorage.setItem" in src)
    t("il n'oublie le brouillon QU'APRES l'envoi",
      src.index("function fini") < src.index("oublier();", src.index("function fini")))
    t("les photos sont reduites avant d'entrer", "toDataURL" in src and "MAX_COTE" in src)
    t("aucune bibliotheque", not re.search(r'<script[^>]+src=', src))

    exe = glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome")
    if not exe:
        print("\n(pas de navigateur : le reste est saute)")
        return 1 if rouges else 0

    srv = Fil(("127.0.0.1", PORT), Serveur)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{PORT}"

    try:
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=exe[0])
            ctx = b.new_context(viewport={"width": 390, "height": 844})
            pg = ctx.new_page()
            errs = []
            alertes = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            # Filet : une alerte qu'on n'attendait pas bloquerait tout le QC
            # pendant 30 s et ferait accuser le produit a tort.
            ctx.on("dialog", lambda d: (alertes.append(d.message), d.accept()))

            # On intercepte la commande : rien ne part pour de vrai.
            envoye = {}

            def prendre(route):
                d = json.loads(route.request.post_data or "{}")
                envoye.update(d)
                route.fulfill(status=200, content_type="application/json",
                              body=json.dumps({"ok": True, "id": 1, "slug": "lettre-ama-7f3a"}))

            pg.route("**/api/order", prendre)

            pg.goto(base + "/creer.html")
            pg.wait_for_timeout(900)

            print("\n=== 2. Étape 1 : l'occasion ===")
            # ⚠️ text-transform:uppercase rend "ÉTAPE 1 SUR 11". On lit ce qui
            # est RENDU, jamais la casse ecrite dans la source.
            t("onze etapes annoncees", "sur 11" in pg.inner_text("#compte").lower(),
              pg.inner_text("#compte"))
            pg.click('button[data-occ="anniv"]')
            pg.wait_for_timeout(400)
            t("l'occasion choisie est marquee",
              pg.get_attribute('button[data-occ="anniv"]', "aria-pressed") == "true")
            pg.click("#bSuite")
            pg.wait_for_timeout(400)

            print("\n=== 3. On ne passe pas sans l'essentiel ===")
            pg.click("#bSuite")
            pg.wait_for_timeout(400)
            t("sans prenom, on reste bloque", "Pour qui" in pg.inner_text("h1"))

            print("\n=== 4. On remplit ===")
            pg.fill("#fPour", "Ama")
            pg.fill("#fDe", "Koffi")
            pg.click("#bSuite"); pg.wait_for_timeout(400)
            t("l'accueil est pre-rempli selon l'occasion",
              "anniversaire" in (pg.input_value("#fAccueil") or "").lower(),
              pg.input_value("#fAccueil"))
            pg.fill("#fCorps", "Premier paragraphe pour Ama.\n\nDeuxieme paragraphe.")
            pg.click("#bSuite"); pg.wait_for_timeout(400)
            pg.fill("#fSign", "Pour toujours, Koffi")
            pg.click("#bSuite"); pg.wait_for_timeout(400)
            t("etape des petits mots", "phrases" in pg.inner_text("h1").lower() or
                                        "petites" in pg.inner_text("h1").lower())
            pg.fill('#rangsMots input[data-k="0"]', "Mange a l'heure.")
            pg.click("#plusMot"); pg.wait_for_timeout(250)
            pg.fill('#rangsMots input[data-k="1"]', "Ecris-moi en arrivant.")
            pg.click("#bSuite"); pg.wait_for_timeout(400)

            print("\n=== 5. Photos : aucune inventee ===")
            t("il le dit clairement", "Ta photo ici" in pg.inner_text(".note"))
            t("aucune photo par defaut",
              pg.evaluate("document.querySelectorAll('#grillePhotos .vig').length") == 0)
            pg.click("#bSuite"); pg.wait_for_timeout(400)

            print("\n=== 6. Musique, question, code ===")
            pg.fill('#rangsMus input[data-k="0"][data-f="titre"]', "Notre morceau")
            pg.fill('#rangsMus input[data-k="0"][data-f="artiste"]', "L'artiste")
            pg.click("#bSuite"); pg.wait_for_timeout(400)
            t("la question est pre-remplie selon l'occasion",
              (pg.input_value("#fQ") or "").strip() != "")
            pg.click("#bSuite"); pg.wait_for_timeout(400)
            pg.fill("#fCode", "abc1234")
            t("le code ne garde que 4 chiffres", pg.input_value("#fCode") == "1234",
              pg.input_value("#fCode"))
            pg.fill("#fInd", "Notre date.")

            print("\n=== 7. LA SAUVEGARDE SURVIT A LA FERMETURE ===")
            brouillon = pg.evaluate("localStorage.getItem('minuit:brouillon:v1')")
            t("un brouillon est en memoire", bool(brouillon) and "Ama" in brouillon)
            pg2 = ctx.new_page()          # même contexte = même localStorage
            pg2.route("**/api/order", prendre)
            pg2.goto(base + "/creer.html")
            pg2.wait_for_timeout(900)
            t("on repart la ou on s'etait arrete",
              "code" in pg2.inner_text("h1").lower(), pg2.inner_text("h1"))
            t("  -> et le code tape est toujours la", pg2.input_value("#fCode") == "1234")
            t("  -> on le DIT au client", "retrouv" in pg2.inner_text("main").lower())
            pg.close()
            pg = pg2

            print("\n=== 8. L'apercu monte une VRAIE lettre ===")
            pg.click("#bSuite"); pg.wait_for_timeout(1600)
            t("le recapitulatif est juste",
              "Ama" in pg.inner_text("#recap") and "1234" in pg.inner_text("#recap"),
              pg.inner_text("#recap"))
            cadre = pg.frame_locator("#cadre")
            t("l'enveloppe est la", cadre.locator("#enveloppe").is_visible())
            # ⚠️ « toi » et « M » sont ECRITS EN DUR dans le gabarit et
            # remplaces par le script au chargement. Lire l'iframe trop tot
            # renvoie donc les valeurs d'exemple, et faisait accuser le
            # produit a tort. On ATTEND le signal, on ne devine pas un delai.
            nom = attendre_iframe(pg, "#destinataire", "Ama")
            t("le prenom est sur l'enveloppe", nom == "Ama", repr(nom))
            ini = attendre_iframe(pg, "#initiale", "K")
            t("l'initiale du cachet est le K de Koffi", ini == "K", repr(ini))
            # on ouvre la lettre DANS l'apercu
            cadre.locator("#enveloppe").click()
            pg.wait_for_timeout(2000)
            t("le code garde la porte dans l'apercu", cadre.locator("#code").is_visible())
            for c in "1234":
                cadre.locator(f"#clavier button:text-is('{c}')").click()
            pg.wait_for_timeout(1600)
            t("LE BON CODE OUVRE LA LETTRE", cadre.locator("#lettre").is_visible())
            corps = cadre.locator("#corps").inner_text()
            t("les deux paragraphes tapes sont dedans",
              "Premier paragraphe pour Ama." in corps and "Deuxieme paragraphe." in corps)
            t("rien du gabarit d'exemple n'a survecu",
              "je les écris comme elles viennent" not in corps, corps[:80])
            t("les petits mots sont dedans",
              "Mange a l'heure." in cadre.locator("#listeMots").inner_text())
            t("le morceau est dedans",
              "Notre morceau" in cadre.locator("#listeMusiques").inner_text())
            t("AUCUNE PHOTO INVENTEE",
              cadre.locator("#listePhotos img").count() == 0)
            t("  -> la section photos est meme masquee",
              cadre.locator("#s-photos").is_hidden())

            print("\n=== 8 bis. LA LETTRE N'ATTEND PAS LE CDN DE POLICES ===")
            # ⛔ Defaut trouve ici : le <link> vers Google Fonts BLOQUAIT le
            # script. CDN injoignable = la lettre affichait « toi » et « M »
            # au lieu du prenom pendant 12 640 ms mesurees. A Cotonou, sur une
            # mauvaise connexion, c'est le produit qui rate son seul moment.
            t("le lien de police ne bloque pas",
              'media="print"' in src and "this.media='all'" in src,
              "la feuille externe bloque encore l'execution du script")
            ctx2 = b.new_context(viewport={"width": 390, "height": 844})
            ctx2.route("**fonts.googleapis.com**", lambda r: r.abort())
            ctx2.route("**fonts.gstatic.com**", lambda r: r.abort())
            p2 = ctx2.new_page()
            p2.on("dialog", lambda d: d.accept())
            p2.goto(base + "/creer.html")
            p2.wait_for_timeout(600)
            p2.evaluate("""() => { E.pour='Zola'; E.de='Ben'; E.corps='Un para.';
              garder(); i = ETAPES.indexOf('apercu'); rendre(); }""")
            import time as _t
            _d = _t.time()
            vu = attendre_iframe(p2, "#destinataire", "Zola", 6000)
            ms = round((_t.time() - _d) * 1000)
            t(f"CDN de polices coupe : le prenom s'affiche en {ms} ms",
              vu == "Zola" and ms < 2500, f"{vu!r} en {ms} ms")
            ctx2.close()

            print("\n=== 9. Le paiement exige la reference ===")
            pg.click("#bSuite"); pg.wait_for_timeout(700)
            t("le compte Mobile Money est lu sur le serveur",
              "0197085576" in pg.inner_text("#numero"), pg.inner_text("#numero"))
            t("le montant est affiche", "5 000" in pg.inner_text("#montant"))
            pg.fill("#fNom", "Koffi")
            pg.click("#bSuite"); pg.wait_for_timeout(500)
            t("sans WhatsApp, refus explicite", "WhatsApp" in pg.inner_text("#errPaie"),
              pg.inner_text("#errPaie"))
            pg.fill("#fWa", "22990112233")
            pg.click("#bSuite"); pg.wait_for_timeout(500)
            t("SANS REFERENCE, REFUS EXPLICITE",
              "référence" in pg.inner_text("#errPaie").lower(), pg.inner_text("#errPaie"))
            t("  -> et rien n'a ete envoye", not envoye)

            print("\n=== 10. L'envoi ===")
            pg.fill("#fRef", "MP260828.1102.B44219")
            pg.click("#bSuite"); pg.wait_for_timeout(1800)
            t("la commande est partie", bool(envoye))
            t("  -> avec la reference", envoye.get("ref") == "MP260828.1102.B44219")
            t("  -> avec le WhatsApp du client", envoye.get("whatsapp") == "22990112233")
            t("  -> avec le reseau", envoye.get("network") == "MTN")
            html = envoye.get("html", "")
            t("  -> avec une lettre ENTIERE", html.startswith("<!DOCTYPE html>") and len(html) > 40000,
              f"{len(html)} octets")
            t("  -> qui contient le contenu du client", "Premier paragraphe pour Ama." in html)
            t("  -> et le code du client", '"code": "1234"' in html)
            t("  -> avec la police embarquee", "data:font/woff2;base64," in html)
            t("l'ecran de fin donne le lien", "lettre-ama-7f3a" in pg.inner_text("main"))
            t("LE BROUILLON EST OUBLIE APRES L'ENVOI",
              pg.evaluate("localStorage.getItem('minuit:brouillon:v1')") is None)

            print("\n=== 11. Propreté ===")
            t("aucune erreur JS sur tout le parcours", not errs, str(errs[:2]))
            ov = pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
            t("aucun debordement horizontal a 390px", ov <= 1, f"{ov}px")
            petits = pg.evaluate("""(()=>{const o=[];
              document.querySelectorAll('button,input,select,textarea').forEach(e=>{
                const r=e.getBoundingClientRect();
                if(r.width>0&&r.height>0&&r.height<40) o.push((e.textContent||e.id||e.tagName).trim().slice(0,16)+' h='+Math.round(r.height));
              });return o.slice(0,5)})()""")
            t("cibles tactiles >= 40px", not petits, str(petits))

            ctx.close()
            b.close()
    finally:
        srv.shutdown()

    print(f"\n===== {ok} verts / {len(rouges)} rouges =====")
    for r in rouges:
        print("  ROUGE :", r)
    return 1 if rouges else 0


if __name__ == "__main__":
    sys.exit(main())

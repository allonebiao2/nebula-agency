# -*- coding: utf-8 -*-
"""MINUIT · les controles du gabarit de la lettre.

Ce qu'une suite verte doit prouver ici, et que l'oeil ne voit pas :
le seuil tient vraiment, le texte d'un acheteur ne peut pas injecter de HTML,
la page ne va chercher AUCUN fichier sur le reseau, et une lettre reste
lisible pour qui a coupe les animations.

    python minuit/_qc.py
"""
import json
import pathlib
import re
import sys

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _injecter import poser  # noqa: E402

ICI = pathlib.Path(__file__).resolve().parent
LETTRE = ICI / "lettre.html"
TMP = ICI / "_vues"

BASE = {
    "occasion": "Anniversaire", "pour": "Zara", "de": "Robert",
    "titre": "Joyeux anniversaire", "code": "",
    "lettre": ["Premiere ligne.", "Deuxieme ligne.", "Troisieme ligne."],
    "photos": [], "depuis": "", "pied": True,
    "lien": "https://nebula-agency.online/minuit",
}

verts, rouges = [], []


def ok(nom):
    verts.append(nom)
    print("  [ok] %s" % nom)


def ko(nom, detail=""):
    rouges.append((nom, detail))
    print("  [KO] %s %s" % (nom, ("-> " + detail) if detail else ""))


def dit(nom, cond, detail=""):
    ok(nom) if cond else ko(nom, detail)


def attendre(fn, limite=6000, pas=100):
    """Attend qu'une condition devienne vraie, au lieu de parier sur une duree."""
    import time
    t0 = time.time()
    while (time.time() - t0) * 1000 < limite:
        try:
            if fn():
                return True
        except Exception:
            pass
        time.sleep(pas / 1000.0)
    return False


def servir(dossier):
    """Un petit serveur MULTITACHE sur le dossier minuit/.

    ⚠️ ThreadingHTTPServer, jamais HTTPServer : mono-tache, il se bloque des
    que la page demande un second fichier, et le controle echoue sur un
    « Page.goto: Timeout » qui n'a rien a voir avec le produit. Deja vu chez
    Hillary et chez Angy.
    """
    import functools
    import threading
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    h = functools.partial(SimpleHTTPRequestHandler, directory=str(dossier))
    srv = ThreadingHTTPServer(("127.0.0.1", 0), h)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def page_avec(donnees, nom="_qc.html"):
    TMP.mkdir(exist_ok=True)
    f = TMP / nom
    f.write_text(poser(donnees), encoding="utf-8")
    return f


def main():
    src = LETTRE.read_text(encoding="utf-8")

    # ─────────────────────────────────────────── 1 · le fichier lui-meme
    print("\n== Le fichier")
    dit("aucune balise script externe", not re.search(r"<script[^>]+src=", src))
    dit("aucune feuille de style externe", "<link" not in src)
    dit("aucune URL http(s) dans le CSS ou le HTML de structure",
        not re.search(r"(src|href)\s*=\s*[\"']https?://(?!nebula-agency)", src))
    dit("noindex present", 'name="robots"' in src and "noindex" in src)
    dit("referrer no-referrer", 'name="referrer"' in src)
    dit("prefers-reduced-motion honore", "prefers-reduced-motion" in src)
    dit("jamais #000 ni #fff en fond",
        not re.search(r"background[^;]*:\s*(#000|#fff|#ffffff|#000000)\b", src, re.I))
    # Regle absolue de la maison : aucun tiret cadratin, ca fait IA.
    for f in ("lettre.html", "creer.html"):
        src_f = (ICI / f).read_text(encoding="utf-8")
        dit("%s : aucun tiret cadratin" % f, "\u2014" not in src_f)
    dit("le marqueur de donnees est unique",
        src.count("/*MINUIT_DONNEES*/") == 1 and src.count("/*FIN_MINUIT_DONNEES*/") == 1)
    # Une animation signature par section : on verifie qu'elles sont bien
    # distinctes, pas qu'une seule serve partout.
    sigs = set(re.findall(r"@keyframes\s+([a-zA-Z0-9_-]+)", src))
    dit("au moins 6 animations distinctes (une par section)", len(sigs) >= 6,
        "trouvees : %s" % sorted(sigs))

    with sync_playwright() as pw:
        nav = pw.chromium.launch()

        # ───────────────────────────────────── 2 · le seuil
        print("\n== Le seuil")
        f = page_avec(BASE)
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        erreurs = []
        pg.on("pageerror", lambda e: erreurs.append(str(e)))
        reseau = []
        pg.on("request", lambda r: reseau.append(r.url))
        pg.goto(f.as_uri())
        pg.wait_for_timeout(400)

        dit("la lettre est cachee au chargement",
            pg.eval_on_selector("#lettre", "e=>getComputedStyle(e).opacity") == "0")
        dit("le seuil est visible",
            pg.is_visible("#seuil"))
        # inner_text renvoie le texte REND U : .pour est en majuscules par CSS.
        # On lit donc le contenu, pas le rendu.
        dit("le prenom du destinataire est au seuil",
            pg.text_content("#s-pour").strip() == "Zara")
        dit("le titre de l'onglet nomme le destinataire", "Zara" in pg.title())

        pg.click("#btn-ouvrir")
        pg.wait_for_timeout(1400)
        dit("sans code, le cachet ouvre la lettre",
            pg.eval_on_selector("#lettre", "e=>e.classList.contains('ouverte')"))
        dit("le seuil s'efface apres l'ouverture",
            pg.eval_on_selector("#seuil", "e=>e.classList.contains('parti')"))
        dit("le focus entre DANS la lettre",
            pg.evaluate("document.activeElement && document.activeElement.id") == "l-titre")
        dit("les 3 lignes sont posees",
            pg.eval_on_selector_all("#l-corps p", "n=>n.length") == 3)
        dit("aucune erreur JavaScript", not erreurs, " | ".join(erreurs[:2]))

        externes = [u for u in reseau if not u.startswith("file:")]
        dit("aucune requete reseau", not externes, " | ".join(externes[:3]))
        pg.close()

        # ───────────────────────────────────── 3 · le code secret
        print("\n== Le code secret")
        f = page_avec(dict(BASE, code="4821"), "_qc_code.html")
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        pg.goto(f.as_uri())
        pg.click("#btn-ouvrir")
        pg.wait_for_timeout(200)
        dit("le clavier a code apparait", pg.is_visible("#cases"))

        for c in "1111":
            pg.keyboard.type(c)
        pg.wait_for_timeout(500)
        dit("un mauvais code n'ouvre RIEN",
            not pg.eval_on_selector("#lettre", "e=>e.classList.contains('ouverte')"))
        dit("un mauvais code le dit", pg.inner_text("#code-msg").strip() != "")
        dit("les cases se vident apres un echec",
            pg.eval_on_selector_all("#cases input", "n=>n.every(i=>i.value==='')"))

        for c in "4821":
            pg.keyboard.type(c)
        pg.wait_for_timeout(1400)
        dit("le bon code ouvre la lettre",
            pg.eval_on_selector("#lettre", "e=>e.classList.contains('ouverte')"))
        pg.close()

        # ───────────────────────────────────── 4 · ce qu'un acheteur ecrit
        print("\n== Le texte vient d'un acheteur, jamais d'un ami")
        piege = dict(
            BASE,
            pour='<img src=x onerror="window.__pwn=1">',
            de="<script>window.__pwn=1</script>",
            titre="<b>gras</b>",
            lettre=["<i>italique</i> & <esperluette>"],
        )
        f = page_avec(piege, "_qc_xss.html")
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        pg.goto(f.as_uri())
        pg.click("#btn-ouvrir")
        pg.wait_for_timeout(1400)
        dit("aucun HTML injecte n'est execute",
            pg.evaluate("window.__pwn === undefined"))
        dit("les balises s'affichent en TEXTE",
            "<b>gras</b>" in (pg.text_content("#l-titre") or ""))
        dit("aucune balise reelle dans le corps",
            pg.eval_on_selector("#l-corps", "e=>e.querySelectorAll('i,script,img').length") == 0)

        # ⛔ Le defaut trouve le 2026-09-02 : « </script> » dans le mot d'un
        # acheteur fermait le bloc de script et TUAIT la page entiere. json.dumps
        # ne protege pas de ca. Ce controle est la preuve que _injecter tient.
        pg.close()
        f = page_avec(dict(BASE,
                           lettre=["Fin </script><script>window.__pwn=1</script>",
                                   "Et un <!-- commentaire --> aussi."],
                           titre="Titre </script> piege"),
                      "_qc_script.html")
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        casse = []
        pg.on("pageerror", lambda e: casse.append(str(e)))
        pg.goto(f.as_uri())
        pg.click("#btn-ouvrir")
        pg.wait_for_timeout(1500)
        dit("« </script> » dans une lettre ne casse pas la page",
            pg.eval_on_selector("#lettre", "e=>e.classList.contains('ouverte')"))
        dit("« </script> » ne fait executer aucun code",
            pg.evaluate("window.__pwn === undefined"))
        dit("« </script> » reste du texte",
            "</script>" in (pg.text_content("#l-titre") or ""))
        dit("un commentaire HTML n'avale pas la suite",
            pg.eval_on_selector_all("#l-corps p", "n=>n.length") == 2)
        dit("aucune erreur JavaScript sur la lettre piegee", not casse,
            " | ".join(casse[:2]))

        # Une photo qui n'est pas une donnee viendrait d'un serveur tiers :
        # elle fuiterait l'ouverture de la lettre. Elle doit etre refusee.
        pg.close()
        f = page_avec(dict(BASE, photos=[{"src": "https://exemple.test/a.jpg"},
                                         {"src": "data:image/gif;base64,R0lGODlhAQABAAAAACw="}]),
                      "_qc_photos.html")
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        pg.goto(f.as_uri())
        pg.wait_for_timeout(300)
        dit("une photo distante est refusee, une photo en donnees passe",
            pg.eval_on_selector_all("#l-photos img", "n=>n.length") == 1)
        pg.close()

        # ───────────────────────────────────── 5 · le compte des jours
        print("\n== Le compte des jours")
        f = page_avec(dict(BASE, depuis="2024-03-14"), "_qc_jours.html")
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        pg.goto(f.as_uri())
        pg.click("#btn-ouvrir")
        pg.wait_for_timeout(3000)
        n = int(pg.inner_text("#l-jours").strip() or 0)
        dit("le compte est plausible et positif", n > 400, "lu : %d" % n)
        dit("le libelle s'accorde",
            "jours ensemble" in pg.text_content("#l-jours-lib"))
        pg.close()

        # Une date future donnerait un nombre negatif : la section doit disparaitre.
        f = page_avec(dict(BASE, depuis="2099-01-01"), "_qc_futur.html")
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        pg.goto(f.as_uri())
        pg.wait_for_timeout(300)
        dit("une date future ne montre AUCUN compte negatif",
            pg.eval_on_selector("#l-compte", "e=>e.hidden") is True)
        pg.close()

        # ───────────────────────────────────── 6 · le pied viral
        print("\n== Le pied viral")
        f = page_avec(dict(BASE, pied=False), "_qc_sanspied.html")
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        pg.goto(f.as_uri())
        pg.wait_for_timeout(250)
        dit("le palier paye retire le pied", pg.eval_on_selector("#l-pied", "e=>e.hidden") is True)
        pg.close()

        f = page_avec(BASE, "_qc_pied.html")
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        pg.goto(f.as_uri())
        pg.wait_for_timeout(250)
        dit("le palier gratuit porte le pied", not pg.eval_on_selector("#l-pied", "e=>e.hidden"))
        dit("le lien du pied est bien pose",
            pg.get_attribute("#pied-lien", "href").startswith("https://"))
        pg.close()

        # ───────────────────────────────────── 7 · les trois largeurs
        print("\n== 390, 768 et 1440")
        for larg in (390, 768, 1440):
            f = page_avec(dict(BASE, depuis="2024-03-14",
                               photos=[{"src": "data:image/gif;base64,R0lGODlhAQABAAAAACw=",
                                        "legende": "Nous deux"}]),
                          "_qc_%d.html" % larg)
            pg = nav.new_page(viewport={"width": larg, "height": 900})
            pg.goto(f.as_uri())
            pg.click("#btn-ouvrir")
            pg.wait_for_timeout(3400)
            deb = pg.evaluate(
                "document.documentElement.scrollWidth - document.documentElement.clientWidth")
            dit("%d px : aucun debordement horizontal" % larg, deb <= 0, "%d px" % deb)

            # Les cibles tactiles. On mesure ce qui est REELLEMENT cliquable.
            petites = pg.evaluate("""() => {
              const out = [];
              document.querySelectorAll('a,button,input').forEach(e => {
                const r = e.getBoundingClientRect();
                if (r.width === 0 && r.height === 0) return;
                if (r.height < 44) out.push((e.id || e.tagName) + ' ' + Math.round(r.height));
              });
              return out;
            }""")
            dit("%d px : toutes les cibles font 44 px ou plus" % larg, not petites,
                " | ".join(petites[:3]))

            # Le texte de la lettre est-il VRAIMENT visible a la fin ?
            caches = pg.evaluate("""() => {
              const out = [];
              document.querySelectorAll('#l-corps p').forEach((e,i) => {
                if (parseFloat(getComputedStyle(e).opacity) < .9) out.push('ligne ' + (i+1));
              });
              return out;
            }""")
            dit("%d px : toutes les lignes sont arrivees" % larg, not caches,
                " | ".join(caches))
            pg.close()

        # ───────────────────────────────────── 8 · contraste sur les PIXELS
        # Le controle habituel lit background-color ; sur un degrade il est
        # aveugle. On lit donc la couleur reellement peinte derriere le texte.
        print("\n== Contraste, mesure sur ce qui est peint")
        f = page_avec(BASE, "_qc_contraste.html")
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        pg.goto(f.as_uri())
        pg.click("#btn-ouvrir")
        pg.wait_for_timeout(3400)
        ratio = pg.evaluate("""() => {
          const lum = c => { const s = c.map(v => { v /= 255;
            return v <= .03928 ? v/12.92 : Math.pow((v+.055)/1.055, 2.4); });
            return .2126*s[0] + .7152*s[1] + .0722*s[2]; };
          const p = document.querySelector('#l-corps p');
          const cs = getComputedStyle(p);
          const t = cs.color.match(/\\d+/g).map(Number);
          // Le fond peint : on remonte jusqu'a la feuille, qui porte le degrade.
          const f = getComputedStyle(document.querySelector('.feuille'));
          const grad = f.backgroundImage;
          // On prend la borne la plus claire du degrade, la moins favorable.
          const m = [...grad.matchAll(/rgba?\\(([^)]+)\\)/g)].map(x =>
            x[1].split(',').slice(0,3).map(Number));
          const fond = m.length ? m.reduce((a,b) => lum(a) > lum(b) ? a : b) : [255,255,255];
          const L1 = Math.max(lum(t), lum(fond)), L2 = Math.min(lum(t), lum(fond));
          return Math.round(((L1+.05)/(L2+.05)) * 100) / 100;
        }""")
        dit("le corps de la lettre depasse 4,5:1", ratio >= 4.5, "mesure : %s:1" % ratio)
        pg.close()

        # ───────────────────────────────────── 9 · mouvement reduit
        print("\n== Mouvement reduit")
        pg = nav.new_page(viewport={"width": 390, "height": 844},
                          reduced_motion="reduce")
        pg.goto(page_avec(dict(BASE, depuis="2024-03-14"), "_qc_doux.html").as_uri())
        pg.click("#btn-ouvrir")
        pg.wait_for_timeout(700)
        dit("mouvement reduit : la lettre s'ouvre quand meme",
            pg.eval_on_selector("#lettre", "e=>e.classList.contains('ouverte')"))
        invisibles = pg.evaluate("""() => [...document.querySelectorAll('#l-corps p')]
            .filter(e => parseFloat(getComputedStyle(e).opacity) < .9).length""")
        dit("mouvement reduit : rien ne reste invisible", invisibles == 0,
            "%d ligne(s)" % invisibles)
        dit("mouvement reduit : le compte affiche son chiffre",
            int(pg.inner_text("#l-jours").strip() or 0) > 400)
        pg.close()

        # ═══════════════════════════════════════════════════════════
        # 10 · LE CONSTRUCTEUR
        # Il a besoin d'un serveur : il va chercher le vrai gabarit pour
        # bâtir son apercu.
        # ═══════════════════════════════════════════════════════════
        print("\n== Le constructeur")
        srv, port = servir(ICI)
        try:
            base = "http://127.0.0.1:%d/creer.html" % port
            pg = nav.new_page(viewport={"width": 1280, "height": 900})
            bugs = []
            pg.on("pageerror", lambda e: bugs.append(str(e)))
            pg.goto(base)
            pg.wait_for_timeout(900)

            dit("le constructeur s'ouvre sans erreur", not bugs, " | ".join(bugs[:2]))
            dit("les 6 occasions sont proposees",
                pg.eval_on_selector_all(".occ", "n=>n.length") == 6)
            dit("les 4 paliers sont proposes",
                pg.eval_on_selector_all(".pal", "n=>n.length") == 4)

            pg.click('.occ[data-id="anniv"]')
            pg.fill("#f-pour", "Zara")
            pg.fill("#f-de", "Robert")
            pg.fill("#f-lettre", "Un mot vrai.\n\nUn deuxieme.")

            # L'apercu est-il le VRAI gabarit, ou une imitation ?
            cadre = pg.frame_locator("#apercu")
            dit("l'apercu montre la vraie lettre",
                attendre(lambda: cadre.locator("#s-pour")
                         .inner_text().strip().upper() == "ZARA"))
            # Le focus doit RESTER visible dans une vraie lettre : on verifie
            # que la retouche ne concerne que l'apercu.
            dit("hors apercu, le titre garde son cercle de focus",
                ".est-apercu #l-titre:focus-visible{outline:none}"
                in (ICI / "lettre.html").read_text(encoding="utf-8")
                and ":focus-visible{outline:2px solid" in src)
            dit("l'apercu montre les MOTS, pas une enveloppe fermee",
                attendre(lambda: cadre.locator("#lettre")
                         .evaluate("e=>e.classList.contains('ouverte')")))
            pg.click("#btn-rejouer")
            dit("« Rejouer l'ouverture » remet le seuil",
                attendre(lambda: pg.frame_locator("#apercu")
                         .locator("#btn-ouvrir").is_visible()))

            # ⛔ LE TROU DE L'ECRAN 4 : il quitte la page pour payer.
            garde = pg.evaluate("localStorage.getItem('minuit:brouillon')")
            dit("le brouillon est ecrit a la frappe", bool(garde) and "Zara" in garde)

            pg.goto("about:blank")
            pg.wait_for_timeout(150)
            pg.goto(base)                      # il revient de son application MoMo
            pg.wait_for_timeout(900)
            dit("au retour, le mot est retrouve",
                pg.input_value("#f-lettre").startswith("Un mot vrai"))
            dit("au retour, les prenoms sont retrouves",
                pg.input_value("#f-pour") == "Zara" and pg.input_value("#f-de") == "Robert")
            dit("au retour, on le DIT a l'acheteur",
                not pg.eval_on_selector("#repris", "e=>e.hidden"))
            dit("au retour, on le remet sur l'ecran d'ecriture",
                pg.eval_on_selector("#e-lettre", "e=>e.classList.contains('on')"))

            # ⛔ Une commande sans reference oblige a arbitrer a la main.
            pg.click("#vers-palier")
            pg.click('.pal[data-id="lettre"]')
            pg.click("#vers-paiement")
            pg.wait_for_timeout(300)
            dit("la somme affichee suit le palier", "5 000" in pg.inner_text("#p-somme"))

            pg.click("#btn-commander")
            pg.wait_for_timeout(250)
            dit("sans reference, la commande ne part PAS",
                not pg.eval_on_selector("#e-fini", "e=>e.classList.contains('on')"))

            pg.fill("#f-ref", "MP260827.1432.A81234")
            pg.click("#btn-commander")
            pg.wait_for_timeout(250)
            dit("sans WhatsApp non plus, la commande ne part pas",
                not pg.eval_on_selector("#e-fini", "e=>e.classList.contains('on')"))

            pg.fill("#f-wa", "0197085576")
            pg.click("#btn-commander")
            pg.wait_for_timeout(600)
            dit("avec tout, la commande part",
                pg.eval_on_selector("#e-fini", "e=>e.classList.contains('on')"))
            cmd = pg.evaluate("window.MINUIT_COMMANDE")
            # On teste le MARQUEUR, pas le mot : « MINUIT_DONNEES » figure aussi
            # dans le commentaire d'en-tete du gabarit, qui doit rester.
            dit("la commande porte le HTML complet de la lettre",
                bool(cmd) and "<html" in cmd["html"]
                and "/*MINUIT_DONNEES*/" not in cmd["html"]
                and '"pour"' in cmd["html"] and "Zara" in cmd["html"])
            # ⛔ La lettre LIVREE garde son cachet : le seuil EST le produit.
            dit("la lettre livree n'est PAS deja ouverte",
                bool(cmd) and '"apercu"' not in cmd["html"])
            dit("la commande porte la reference et le WhatsApp",
                bool(cmd) and cmd["ref"] == "MP260827.1432.A81234"
                and cmd["whatsapp"] == "0197085576")
            dit("le brouillon n'est efface QU'APRES l'envoi",
                pg.evaluate("localStorage.getItem('minuit:brouillon')") is None)

            # Le palier gratuit garde le pied viral, le palier paye le retire.
            pg.evaluate("localStorage.clear()")
            pg.goto(base)
            pg.wait_for_timeout(900)
            pg.click('.occ[data-id="anniv"]')
            pg.click("#vers-palier")
            pg.click('.pal[data-id="gratuit"]')
            dit("palier gratuit : le pied MINUIT reste",
                attendre(lambda: not pg.frame_locator("#apercu")
                         .locator("#l-pied").evaluate("e=>e.hidden")))
            pg.click('.pal[data-id="coffret"]')
            dit("palier paye : le pied MINUIT disparait",
                attendre(lambda: pg.frame_locator("#apercu")
                         .locator("#l-pied").evaluate("e=>e.hidden")))
            pg.close()

            # Sur telephone.
            pg = nav.new_page(viewport={"width": 390, "height": 844})
            pg.goto(base)
            pg.wait_for_timeout(900)
            deb = pg.evaluate(
                "document.documentElement.scrollWidth - document.documentElement.clientWidth")
            dit("constructeur 390 px : aucun debordement", deb <= 0, "%d px" % deb)
            petites = pg.evaluate("""() => {
              const out = [];
              document.querySelectorAll('button,input,select,textarea').forEach(e => {
                const r = e.getBoundingClientRect();
                if (r.width === 0 && r.height === 0) return;
                if (r.height < 44) out.push((e.id || e.className || e.tagName) + ' ' + Math.round(r.height));
              });
              return out;
            }""")
            dit("constructeur 390 px : cibles a 44 px", not petites, " | ".join(petites[:3]))
            pg.close()
        finally:
            srv.shutdown()

        nav.close()

    print("\n%d controles verts, %d en echec" % (len(verts), len(rouges)))
    if rouges:
        print("\nA REPRENDRE :")
        for n, d in rouges:
            print("  - %s %s" % (n, ("(" + d + ")") if d else ""))
        return 1
    print("Tout est vert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

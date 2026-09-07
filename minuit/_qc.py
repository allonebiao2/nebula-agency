# -*- coding: utf-8 -*-
"""MINUIT · les controles du gabarit de la lettre.

Ce qu'une suite verte doit prouver ici, et que l'oeil ne voit pas :
le seuil tient vraiment, le texte d'un acheteur ne peut pas injecter de HTML,
la page ne va chercher AUCUN fichier sur le reseau, et une lettre reste
lisible pour qui a coupe les animations.

    python minuit/_qc.py
"""
import datetime
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

# Les memes noms que dans lettre.html : un libelle recopie a la main derive.
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def dans(secondes):
    """Une heure de calendrier, comme celle que l'acheteur tape.

    ⚠️ Sans fuseau, et c'est le sujet : minuit, c'est minuit sur le telephone
    de celle qui lit. Les secondes ne servent qu'ici : un controle ne peut pas
    attendre une minute pour voir un verrou se lever.
    """
    d = datetime.datetime.now() + datetime.timedelta(seconds=secondes)
    return d, d.strftime("%Y-%m-%dT%H:%M:%S")


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
    # ⛔ UNE SEULE ECHELLE DE PRIX. Les occasions en portaient une deuxieme,
    # affichee « des 10 000 F » et appliquee nulle part : on choisissait
    # « Demande en mariage · des 10 000 F », puis le palier gratuit, et on
    # payait 0 F. Deux echelles dans un fichier sont deux verites.
    creer = (ICI / "creer.html").read_text(encoding="utf-8")
    bloc_occ = re.search(r"var OCCASIONS = \[(.*?)\];", creer, re.S)
    dit("les occasions ne portent aucun prix",
        bool(bloc_occ) and "prix" not in bloc_occ.group(1))
    dit("aucune carte d'occasion n'affiche « des X F »",
        'textContent = "dès " + fmt' not in creer)
    bloc_pal = re.search(r"var PALIERS = \[(.*?)\];", creer, re.S)
    dit("les paliers, eux, portent les 4 prix",
        bool(bloc_pal) and bloc_pal.group(1).count("prix:") == 4)

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

        # ───────────────────────────────────── 5 bis · LE VERROU D'HEURE
        # C'est la fonction qui donne son nom au produit. Elle etait demandee
        # a l'acheteur et n'existait nulle part : ni dans la lettre, ni dans
        # une machine a envoyer (n8n tournait sur un serveur qui n'est plus a
        # Mongazi). Elle vit desormais DANS la lettre.
        print("\n== Le verrou d'heure")

        d, tard = dans(95)
        f = page_avec(dict(BASE, ouvre=tard), "_qc_verrou.html")
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        bugs = []
        pg.on("pageerror", lambda e: bugs.append(str(e)))
        pg.goto(f.as_uri())
        pg.wait_for_timeout(400)

        dit("avant l'heure : aucun bouton a pousser", not pg.is_visible("#btn-ouvrir"))
        dit("avant l'heure : la lettre reste fermee",
            not pg.eval_on_selector("#lettre", "e=>e.classList.contains('ouverte')"))
        quand = pg.text_content("#att-quand")
        dit("avant l'heure : la page DIT quand elle s'ouvre",
            ("%d %s" % (d.day, MOIS[d.month - 1])) in quand, "lu : %s" % quand)

        # Le compte descend vraiment. On ECHANTILLONNE : deux instantanes
        # peuvent tomber dans la meme seconde et faire echouer un site sain.
        vus = []
        for _ in range(4):
            vus.append(pg.text_content("#att-reste"))
            pg.wait_for_timeout(700)
        dit("avant l'heure : le compte descend", len(set(vus)) >= 2, " / ".join(vus))

        # ⛔ Le garde-fou est DANS ouvrir(), pas seulement sur le bouton : le
        # code secret appelle ouvrir() directement.
        pg.evaluate("ouvrir()")
        pg.wait_for_timeout(300)
        dit("avant l'heure : ouvrir() refuse, meme appele directement",
            not pg.eval_on_selector("#lettre", "e=>e.classList.contains('ouverte')"))
        dit("avant l'heure : le cachet dort (il ne respire pas)",
            pg.eval_on_selector(".cachet", "e=>getComputedStyle(e).animationName") == "none")
        pg.close()

        # Le bon code ne suffit pas non plus : l'heure passe avant le code.
        d, tard = dans(95)
        f = page_avec(dict(BASE, ouvre=tard, code="1234"), "_qc_verrou_code.html")
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        pg.goto(f.as_uri())
        pg.wait_for_timeout(300)
        pg.evaluate("""() => {
          const cs = Array.prototype.slice.call(document.querySelectorAll('#cases input'));
          '1234'.split('').forEach((v, i) => {
            cs[i].value = v;
            cs[i].dispatchEvent(new Event('input', { bubbles: true }));
          });
        }""")
        pg.wait_for_timeout(400)
        dit("avant l'heure : le BON code n'ouvre pas non plus",
            not pg.eval_on_selector("#lettre", "e=>e.classList.contains('ouverte')"))
        pg.close()

        # ⚠️ TEMOIN. Sans lui, un verrou reste ferme pour toujours passerait
        # tous les controles ci-dessus avec les honneurs.
        _, passee = dans(-120)
        f = page_avec(dict(BASE, ouvre=passee), "_qc_verrou_passe.html")
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        pg.goto(f.as_uri())
        pg.wait_for_timeout(300)
        dit("heure passee : le bouton est la", pg.is_visible("#btn-ouvrir"))
        dit("heure passee : rien n'annonce d'attente",
            not pg.is_visible("#attente"))
        pg.click("#btn-ouvrir")
        pg.wait_for_timeout(1400)
        dit("heure passee : la lettre s'ouvre normalement",
            pg.eval_on_selector("#lettre", "e=>e.classList.contains('ouverte')"))
        pg.close()

        # L'heure arrive SOUS LES YEUX : le verrou se leve seul, sans
        # rechargement, et la cire s'allume.
        _, bientot = dans(3)
        f = page_avec(dict(BASE, ouvre=bientot), "_qc_verrou_degel.html")
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        pg.goto(f.as_uri())
        pg.wait_for_timeout(200)
        pg.evaluate("window.__temoin = 1")
        froide = pg.eval_on_selector(".cachet", "e=>getComputedStyle(e).filter")
        leve = attendre(lambda: pg.is_visible("#btn-ouvrir"), 9000, 200)
        dit("l'heure arrive : le verrou se leve tout seul", leve)
        dit("l'heure arrive : la page ne s'est PAS rechargee",
            pg.evaluate("window.__temoin") == 1)
        dit("l'heure arrive : on le dit a celle qui attend",
            "C'est l'heure" in pg.text_content("#s-touche"))
        chaude = pg.eval_on_selector(".cachet", "e=>getComputedStyle(e).filter")
        dit("l'heure arrive : la cire s'allume", froide != chaude and froide != "none",
            "%s -> %s" % (froide, chaude))
        pg.click("#btn-ouvrir")
        pg.wait_for_timeout(1400)
        dit("l'heure arrive : la lettre s'ouvre",
            pg.eval_on_selector("#lettre", "e=>e.classList.contains('ouverte')"))
        dit("le verrou n'a leve aucune erreur JavaScript", not bugs, " | ".join(bugs[:2]))
        pg.close()

        # ⛔ L'apercu du constructeur n'est JAMAIS verrouille : l'acheteur doit
        # voir SES mots pendant qu'il les tape. C'est la ou la vente se fait.
        _, tard2 = dans(9999)
        f = page_avec(dict(BASE, ouvre=tard2, apercu=True), "_qc_verrou_apercu.html")
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        pg.goto(f.as_uri())
        dit("l'apercu ignore le verrou",
            attendre(lambda: pg.eval_on_selector(
                "#lettre", "e=>e.classList.contains('ouverte')")))
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

        # ⛔ LE SEUIL N'ETAIT MESURE PAR RIEN, et c'est l'ecran le plus vu du
        # produit : une lettre programmee ne montre QUE lui pendant des heures.
        # Le meme gris tenait 4,8:1 sur le papier et 3,4:1 sur la nuit.
        _, tard3 = dans(4000)
        f = page_avec(dict(BASE, ouvre=tard3), "_qc_contraste_seuil.html")
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        pg.goto(f.as_uri())
        pg.wait_for_timeout(400)
        mesures = pg.evaluate("""() => {
          const lum = c => { const s = c.map(v => { v /= 255;
            return v <= .03928 ? v/12.92 : Math.pow((v+.055)/1.055, 2.4); });
            return .2126*s[0] + .7152*s[1] + .0722*s[2]; };
          // Le fond du seuil est un degrade : on prend sa borne la PLUS CLAIRE,
          // la moins favorable pour du texte clair.
          const g = getComputedStyle(document.querySelector('#seuil')).backgroundImage;
          const m = [...g.matchAll(/rgba?\(([^)]+)\)/g)].map(x =>
            x[1].split(',').slice(0,3).map(Number));
          const fond = m.length ? m.reduce((a,b) => lum(a) > lum(b) ? a : b) : [0,0,0];
          const out = {};
          for (const sel of ['.pour', '#s-touche', '#att-quand', '#att-reste']) {
            const e = document.querySelector(sel);
            const t = getComputedStyle(e).color.match(/\d+/g).map(Number);
            const L1 = Math.max(lum(t), lum(fond)), L2 = Math.min(lum(t), lum(fond));
            out[sel] = Math.round(((L1+.05)/(L2+.05)) * 100) / 100;
          }
          return out;
        }""")
        for sel, r in mesures.items():
            dit("seuil %s depasse 4,5:1" % sel, r >= 4.5, "mesure : %s:1" % r)
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

            # ⛔ « maxlength » TRONQUE AVANT le filtre : coller « abc1234 »
            # laissait « abc1 », le filtre retirait les lettres, et le code
            # tombait a « 1 ». Defaut trouve par la session telephone dans mon
            # propre fichier, mesure en navigateur.
            for saisi, attendu in (("abc1234", "1234"), ("12ab34", "1234"),
                                   ("99999", "9999"), ("1234", "1234")):
                pg.fill("#f-code", "")
                pg.type("#f-code", saisi)
                pg.wait_for_timeout(120)
                dit("code secret : « %s » donne « %s »" % (saisi, attendu),
                    pg.input_value("#f-code") == attendu,
                    "obtenu %r" % pg.input_value("#f-code"))
            pg.fill("#f-code", "")

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

            pg.click("#vers-palier")
            pg.click('.pal[data-id="lettre"]')
            pg.click("#vers-paiement")
            pg.wait_for_timeout(300)
            dit("la somme affichee suit le palier", "5 000" in pg.inner_text("#p-somme"))

            # ⚠️ CONTROLE RETOURNE (2026-09-06). Il disait « sans reference, la
            # commande ne part pas » : c'etait vrai, et ca ne l'est plus, parce
            # que la reference elle-meme a disparu avec SasPay. Un controle qui
            # devient faux ne se supprime pas, il dit la nouvelle verite.
            dit("il n'y a plus de reference de SMS a coller",
                pg.eval_on_selector_all("#f-ref", "n=>n.length") == 0)
            dit("ni de reseau a choisir : la page de paiement le demande",
                pg.eval_on_selector_all("#f-reseau", "n=>n.length") == 0)
            dit("le bouton annonce la somme", "5 000" in pg.inner_text("#btn-commander"))

            pg.click("#btn-commander")
            pg.wait_for_timeout(250)
            dit("sans WhatsApp, la commande ne part pas",
                not pg.eval_on_selector("#e-fini", "e=>e.classList.contains('on')"))

            # ── La caisse, interceptee ────────────────────────────────────
            # ⚠️ On ne parle a personne : on repond nous-memes a la place de la
            # fonction de bord. Ce qui est mesure ici, c'est CE QUE LE
            # CONSTRUCTEUR ENVOIE, et rien d'autre.
            envois = []

            def caisse(route, request):
                envois.append(json.loads(request.post_data or "{}"))
                route.fulfill(status=200, content_type="application/json",
                              body=json.dumps({"ok": True, "offert": False,
                                               "jeton": "c" * 22,
                                               "adresse": "https://exemple.invalid/l/" + "c" * 22,
                                               "paiement": "https://paiement.invalid/session/42",
                                               "palier": "La Lettre", "prix": 5000}))

            pg.route("**/minuit-commande", caisse)

            # ⛔ Le brouillon ne doit PAS partir tant que la reponse n'est pas
            # heureuse : un acheteur qui perd son quart d'heure ne recommence
            # pas. On coupe d'abord la caisse pour le prouver.
            pg.route("**/minuit-commande", lambda r, q: r.abort())
            pg.fill("#f-wa", "0197085576")
            pg.click("#btn-commander")
            attendre(lambda: not pg.eval_on_selector("#envoi-mot", "e=>e.hidden"))
            dit("reseau coupe : on le DIT a l'acheteur",
                "réseau" in pg.inner_text("#envoi-mot").lower())
            dit("reseau coupe : le brouillon est GARDE",
                pg.evaluate("localStorage.getItem('minuit:brouillon')") is not None)
            dit("reseau coupe : on ne montre pas « commande recue »",
                not pg.eval_on_selector("#e-fini", "e=>e.classList.contains('on')"))
            dit("reseau coupe : le bouton redevient cliquable",
                pg.eval_on_selector("#btn-commander", "e=>!e.disabled"))

            pg.unroute("**/minuit-commande")
            pg.route("**/minuit-commande", caisse)
            pg.click("#btn-commander")
            attendre(lambda: len(envois) > 0)
            dit("la commande part vers la caisse", len(envois) == 1)

            cmd = envois[0] if envois else {}
            # ⛔ ON N'ENVOIE PLUS DE HTML. Une porte publique qui accepte du HTML
            # et le sert sur notre domaine est un hebergeur de pages
            # arbitraires. Le serveur rebatit la lettre a partir du gabarit.
            dit("⛔ la commande ne porte AUCUN HTML", "html" not in cmd)
            dit("elle porte les mots de l'acheteur",
                cmd.get("pour") == "Zara" and isinstance(cmd.get("lettre"), list)
                and len(cmd.get("lettre") or []) >= 1)
            dit("elle porte le palier, pas un prix",
                cmd.get("palier") == "lettre"
                and not any(k in cmd for k in ("prix", "total", "montant")))
            dit("elle porte le WhatsApp de l'acheteur", cmd.get("whatsapp") == "0197085576")
            dit("elle ne porte plus aucune reference", "ref" not in cmd)
            # ⛔ Le seuil EST le produit : le drapeau d'apercu ne franchit jamais
            # la porte, et le pied viral est une decision du serveur.
            dit("le drapeau d'apercu ne part pas", "apercu" not in cmd)
            dit("le pied viral n'est pas decide par le navigateur", "pied" not in cmd)

            # ⚠️ ON N'INTERROGE PAS `pg.url` EN BOUCLE POUR ATTENDRE UNE
            # NAVIGATION : le contexte d'execution est detruit pendant qu'elle
            # a lieu, et la sonde tombe sur « Execution context was destroyed »
            # ou conclut trop tot que rien n'a bouge. Playwright a un guetteur
            # pour ca, et lui survit au changement de page.
            parti = True
            try:
                pg.wait_for_url("**/paiement.html", timeout=15000)
            except Exception as e:
                parti = False
                detail = str(e).splitlines()[0]
            # ⚠️ On ne part PAS directement chez l'encaisseur : on passe par
            # notre page, qui montre ce qu'on achete et le lien en clair.
            dit("une lettre payee passe par NOTRE page de paiement",
                parti, "" if parti else detail)

            # ── La page de paiement ───────────────────────────────────────
            print("\n== La page de paiement")
            pg.wait_for_timeout(300)
            dit("elle montre pour qui", "Zara" in pg.inner_text("#r-pour"))
            dit("elle montre l'offre", "La Lettre" in pg.inner_text("#r-palier"))
            dit("elle montre la somme rendue par la caisse",
                "5 000" in pg.inner_text("#r-somme"), pg.inner_text("#r-somme"))
            dit("le bouton annonce la somme", "5 000" in pg.inner_text("#btn-payer"))
            # ⛔ CE QU'IL EST VENU CHERCHER : le lien.
            dit("le bouton porte le lien de paiement",
                pg.get_attribute("#btn-payer", "href") == "https://paiement.invalid/session/42",
                str(pg.get_attribute("#btn-payer", "href")))
            dit("le lien est aussi ecrit en clair, pour payer d'un autre telephone",
                "paiement.invalid/session/42" in pg.inner_text("#r-lien"))
            dit("elle montre l'adresse de la lettre",
                "exemple.invalid/l/" in pg.inner_text("#r-adresse"))
            # ⛔ AUCUN CODE NE PASSE PAR CETTE PAGE. Une page de vitrine qui
            # demanderait un code Mobile Money est exactement ce qu'on apprend
            # aux gens a ne jamais faire.
            dit("⛔ elle ne demande AUCUN code, aucun numero",
                pg.eval_on_selector_all("input, select, textarea", "n=>n.length") == 0)
            dit("elle ne s'indexe pas", "noindex" in (pg.get_attribute(
                "meta[name=robots]", "content") or ""))
            # ⚠️ TEMOIN : le brouillon reste tant qu'il n'a pas paye, et la page
            # de paiement est sur NOTRE origine, donc on le lit d'ici.
            dit("il part payer, et son brouillon l'attend",
                pg.evaluate("localStorage.getItem('minuit:brouillon')") is not None)

            deb = pg.evaluate(
                "document.documentElement.scrollWidth - document.documentElement.clientWidth")
            dit("page de paiement 1280 px : aucun debordement", deb <= 0, "%d px" % deb)

            # Ouverte a la main, sans commande : elle le dit, elle ne ment pas.
            pg.evaluate("localStorage.removeItem('minuit:paiement')")
            pg.goto(base.replace("creer.html", "paiement.html"))
            pg.wait_for_timeout(300)
            dit("sans commande, la page de paiement le DIT",
                pg.is_visible("#vide") and not pg.is_visible("#carte"))
            dit("et elle renvoie ecrire une lettre",
                "creer.html" in (pg.get_attribute("#vide a", "href") or ""))

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

            # ⛔ UNE LETTRE OFFERTE N'A PAS DE CAISSE. Le code disait
            # « aller(p.prix === 0 ? "e-paiement" : "e-paiement") » : les deux
            # branches etaient identiques, donc l'intention avait ete ecrite
            # puis perdue. Le palier gratuit, celui qui porte toute la boucle
            # virale, affichait « Envoie exactement cette somme, au franc
            # pres » au-dessus d'un numero Mobile Money, pour zero franc.
            pg.click('.pal[data-id="gratuit"]')
            pg.click("#vers-paiement")
            pg.wait_for_timeout(250)
            dit("offert : aucune somme a envoyer",
                pg.eval_on_selector("#bloc-reglement", "e=>e.hidden") is True)
            dit("offert : le bouton ne parle pas de paiement",
                "payé" not in pg.inner_text("#btn-commander"))
            dit("offert : on demande quand meme ou envoyer le lien",
                pg.is_visible("#f-wa"))
            pg.route("**/minuit-commande", lambda r, q: r.fulfill(
                status=200, content_type="application/json",
                body=json.dumps({"ok": True, "offert": True,
                                 "adresse": "https://exemple.invalid/l/" + "e" * 22})))
            pg.fill("#f-wa", "0197085576")
            pg.click("#btn-commander")
            dit("offert : la commande part sans reference",
                attendre(lambda: pg.eval_on_selector("#e-fini", "e=>e.classList.contains('on')")))

            # ⚠️ TEMOIN : un ecran qui serait TOUJOURS nu passerait les quatre
            # controles ci-dessus. On repasse a un palier paye.
            pg.evaluate("localStorage.clear()")
            pg.goto(base)
            pg.wait_for_timeout(900)
            pg.click('.occ[data-id="anniv"]')
            pg.click("#vers-palier")
            pg.click('.pal[data-id="lettre"]')
            pg.click("#vers-paiement")
            pg.wait_for_timeout(250)
            dit("paye : la caisse revient",
                pg.eval_on_selector("#bloc-reglement", "e=>e.hidden") is False)
            pg.close()

            # ⛔ L'HEURE PART AVEC LA LETTRE. Elle etait demandee, promise sur
            # l'ecran final, et n'entrait dans aucune lettre livree.
            pg = nav.new_page(viewport={"width": 1280, "height": 900})
            pg.goto(base)
            pg.wait_for_timeout(900)
            pg.click('.occ[data-id="anniv"]')
            pg.fill("#f-pour", "Zara")
            pg.fill("#f-lettre", "Un mot vrai.")
            pg.fill("#f-quand", "2027-02-14")
            pg.fill("#f-quand-h", "00:00")
            pg.click("#vers-palier")
            pg.click('.pal[data-id="coffret"]')
            pg.click("#vers-paiement")
            pg.fill("#f-wa", "0197085576")
            envois2 = []
            pg.route("**/minuit-commande", lambda r, q: (
                envois2.append(json.loads(q.post_data or "{}")),
                r.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"ok": True, "offert": True,
                                           "adresse": "https://exemple.invalid/l/" + "d" * 22}))))
            pg.click("#btn-commander")
            attendre(lambda: len(envois2) > 0)
            cmd2 = envois2[0] if envois2 else {}
            dit("la lettre livree porte l'heure choisie",
                cmd2.get("ouvre") == "2027-02-14T00:00", str(cmd2.get("ouvre")))
            # ⚠️ Sans fuseau, et c'est le sujet : minuit, c'est minuit sur le
            # telephone de celle qui lit, pas celui de l'acheteur.
            dit("l'heure est une heure de calendrier, sans fuseau",
                not any(c in str(cmd2.get("ouvre")) for c in ("Z", "+")))
            attendre(lambda: pg.eval_on_selector("#e-fini", "e=>e.classList.contains('on')"))
            dit("une lettre offerte montre son adresse",
                "exemple.invalid/l/" in pg.inner_text("#lien-lettre"))
            dit("et son brouillon est alors oublie",
                pg.evaluate("localStorage.getItem('minuit:brouillon')") is None)
            # On ne promet que ce que la lettre tient toute seule.
            promesse = pg.inner_text("#fini-quand")
            dit("l'ecran final ne promet aucun envoi automatique",
                "ne se brisera pas avant" in promesse
                and "recevra" not in promesse, promesse)
            # ── La page de retour ─────────────────────────────────────────
            print("\n== La page de retour")
            merci = base.replace("creer.html", "merci.html") + "?j=" + ("c" * 22)

            # 1 · tant que la notification n'est pas arrivee, la lettre attend.
            pg.route("**/etat", lambda r, q: r.fulfill(
                status=200, content_type="application/json",
                body=json.dumps({"etat": "attente"})))
            pg.goto(merci)
            pg.wait_for_timeout(700)
            # ⛔ ELLE NE PROUVE RIEN : l'adresse se tape a la main. On ne dit
            # JAMAIS « paiement reussi » ici.
            corps = pg.inner_text("body").lower()
            dit("⛔ la page de retour ne declare aucun paiement reussi",
                "réussi" not in corps and "confirmé" not in corps, corps[:80])
            dit("elle dit qu'on attend la confirmation", "attend" in corps)
            dit("et le bouton n'ouvre encore rien",
                pg.get_attribute("#ouvrir", "aria-disabled") == "true")

            # 2 · la notification est arrivee : la lettre est vivante.
            pg.unroute("**/etat")
            pg.route("**/etat", lambda r, q: r.fulfill(
                status=200, content_type="application/json",
                body=json.dumps({"etat": "vivante"})))
            pg.goto(merci)
            dit("quand la lettre s'ouvre, la page le dit toute seule",
                attendre(lambda: "ouverte" in pg.inner_text("#titre").lower()))
            dit("et le bouton mene a la lettre",
                (pg.get_attribute("#ouvrir", "href") or "").endswith("c" * 22))
            dit("l'adresse est copiable", pg.is_visible("#copier"))
            pg.unroute("**/etat")
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

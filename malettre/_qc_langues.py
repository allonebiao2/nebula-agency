# -*- coding: utf-8 -*-
"""MA LETTRE À… · les contrôles de l'anglais (2026-10-16).

    python malettre/_traduire.py && python malettre/_qc_langues.py

Ce qu'une suite verte doit prouver :
- les pages anglaises sont EXACTEMENT celles que fabrique le dictionnaire
  (personne ne les a retouchées à la main, et aucune n'est en retard) ;
- il n'y reste aucun mot français : ni dans le texte, ni dans un attribut
  (placeholder, aria-label…), ni dans une chaîne du script qui s'affichera
  plus tard (un message d'erreur, un bouton qui change de nom) ;
- un parcours anglais part en anglais : la plume, la commande et l'aperçu
  portent `langue: "en"`, et la lettre reçue parle anglais (seuil, compte à
  rebours, jours ensemble, pied) ;
- les deux sélecteurs de langue mènent quelque part.
"""
import functools
import html.parser
import json
import pathlib
import re
import sys
import threading
from datetime import datetime, timedelta
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from playwright.sync_api import sync_playwright

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import _traduire  # noqa: E402
from _injecter import poser  # noqa: E402

verts, rouges = [], []


def dit(nom, cond, detail=""):
    (verts if cond else rouges).append((nom, detail))
    print("  [%s] %s %s" % ("ok" if cond else "KO", nom, ("-> " + str(detail)) if (detail and not cond) else ""))
    return cond


# ── 1 · Les restes de français ───────────────────────────────────────────
ACCENTS = re.compile(r"[éèêëàâîïôûùçœÉÈÊËÀÂÎÏÔÛÙÇŒ]")
MOTS_FR = re.compile(r"\b(le|la|les|des|une|est|pour|avec|tu|ta|ton|tes|ses|sa|vous|nous|qui|que|pas|dans|"
                     r"sur|mais|elle|aux|du|au|cette|mon|mes|et|ou|ne|ici|lettre|cachet|offre|"
                     # les mots d'interface sans accent, que la liste ci-dessus laisserait passer
                     r"copier|payer|retour|continuer|choisir|merci|ouvrir|envoyer|recevoir|commencer|gratuit|"
                     r"offert|commande|mois|jours|heure|minuit|toi|moi|ensemble|avant|chaque|rien|jamais|toujours)\b", re.I)
# Ce qui a le droit de rester : la marque, des noms propres, deux mots que
# l'anglais a pris au français, et une clé interne du script.
PERMIS = ["« Ma lettre à… »", "Ma lettre à…", "Ma lettre à", "Ma lettre", "MA LETTRE", "malettre", "fiancée", "fiancé", "Lomé",
          # les personnes et les lieux des exemples (inventés, mais avec leurs accents)
          "Côte d'Ivoire", "Grâce", "Sèna", "Ismaël", "Fidjrossè", "attiéké", "Adjamé"]
# Des clés internes : « prénom » (une clé de MOTS), « pour » (un champ de l'état).
CLES = {"prénom", "pour",
        # les identifiants des offres (posés par le build dans les données de la page)
        "carte", "mot", "lettre", "coffret",
        # le mode « qui écrit » (« moi » ou « plume ») est un identifiant, comme une offre (2026-10-22)
        "moi",
        # l'ouverture de repli du constructeur : un identifiant du catalogue `ouvertures.js` (2026-10-22), jamais affiché
        "cachet"}


def francais(t):
    # L'accueil a l'apostrophe typographique depuis le 2026-10-21 (« Côte d’Ivoire ») :
    # la liste des mots permis s'écrit avec l'apostrophe droite, on compare les deux pareil.
    t = t.replace("’", "'")
    for p in PERMIS:
        t = t.replace(p, " ")
    return bool(ACCENTS.search(t) or MOTS_FR.search(t))


class Textes(html.parser.HTMLParser):
    ATTRS = {"placeholder", "title", "aria-label", "alt"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.textes, self.scripts, self.dans = [], [], None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.dans = tag
        a = dict(attrs)
        if a.get("lang") == "fr":
            return   # le lien vers la page française parle français, exprès
        for k, v in attrs:
            if not v:
                continue
            if k in self.ATTRS:
                self.textes.append(("@" + k, v))
            elif tag == "meta" and k == "content" and (a.get("name") == "description"
                                                        or a.get("property") in ("og:title", "og:description")):
                self.textes.append(("@content", v))

    def handle_endtag(self, tag):
        if tag == self.dans:
            self.dans = None

    def handle_data(self, d):
        if self.dans == "script":
            self.scripts.append(d)
        elif self.dans is None and d.strip():
            self.textes.append(("texte", d.strip()))


def chaines_js(code):
    code = re.sub(r"/\*.*?\*/", " ", code, flags=re.S)
    return re.findall(r'"((?:[^"\\\n]|\\.)*)"', code)


def restes(nom, html_txt):
    t = Textes()
    t.feed(html_txt)
    trouves = [(o, v) for o, v in t.textes if francais(v)]
    # Les identifiants ne sont pas du texte : occasions, questions, sélecteurs
    # (« #r-pour »), écrans (« e-paiement »). ⚠️ Un mot seul SANS tiret reste
    # suspect (« elle », défaut de « Pour » dans le paiement), sauf s'il est un
    # identifiant d'occasion ou de question, lus dans la page elle-même.
    ids = set(re.findall(r'\bid:"([a-z]+)"', html_txt)) | set(re.findall(r'^\s*"([a-z-]+)":\s*\{q:', html_txt, re.M))
    for s in chaines_js("\n".join(t.scripts)):
        if s in CLES or s in ids or not re.search(r"[A-Za-zÀ-ÿ]", s):
            continue
        if re.fullmatch(r"[#.]?[a-z0-9]+(?:[-:_][a-z0-9]+)+|[#.][\w\s#.\[\]=\"'():,>-]+", s):   # identifiant, sélecteur
            continue
        if re.fullmatch(r"[\w./-]+\.html(\?.*)?", s) or re.match(r"https?://\S+$", s):   # un chemin, une adresse
            continue
        if francais(s):
            trouves.append(("js", s))
    dit("%s : aucun mot français restant (texte, attributs, script)" % nom, not trouves,
        "; ".join("%s « %s »" % (o, v[:50]) for o, v in trouves[:8]))


def statiques():
    print("\n· les pages anglaises")
    # LE TÉMOIN : un détecteur qui ne voit rien ne prouve rien.
    fr = ["Copier", "elle", "Retour", "Ta lettre est prête.", "Payer 500 F", "Bientôt", "Vérification…"]
    en = ["Copy", "Back", "Your letter is ready.", "Pay 500 F", "Ma lettre à… is a service", "My fiancée",
          "Their new home in Lomé"]
    dit("témoin : le détecteur voit le français", all(francais(x) for x in fr), [x for x in fr if not francais(x)])
    dit("témoin : et laisse passer l'anglais", not any(francais(x) for x in en), [x for x in en if francais(x)])
    dico = _traduire.lire_dico()
    for nom in _traduire.PAGES:
        attendu = _traduire.traduire((ICI / nom).read_text(encoding="utf-8"), dico[nom], nom)
        reel = (ICI / "en" / nom).read_text(encoding="utf-8") if (ICI / "en" / nom).exists() else ""
        dit("en/%s est exactement ce que fabrique le dictionnaire (python malettre/_traduire.py)" % nom, reel == attendu)
        restes("en/" + nom, reel)
    restes("en/index.html", (ICI / "en" / "index.html").read_text(encoding="utf-8"))
    fr = (ICI / "creer.html").read_text(encoding="utf-8")
    en = (ICI / "en" / "creer.html").read_text(encoding="utf-8")
    dit("le constructeur anglais écrit des lettres anglaises", 'var LANGUE = "en";' in en and 'var LANGUE = "fr";' in fr)
    dit("un brouillon par langue", 'var CLE = "malettre:brouillon:en";' in en and 'var CLE = "malettre:brouillon";' in fr)
    dit("la page anglaise va chercher le gabarit à la racine", 'fetch("../lettre.html")' in en)
    ids = lambda s: re.findall(r'\{id:"([a-z]+)"', s)
    dit("mêmes identifiants (occasions, familles, offres) dans les deux langues", ids(fr) == ids(en), len(ids(fr)))
    prix = lambda s: re.findall(r"prix:(\d+)", s)
    dit("mêmes prix dans les deux langues", prix(fr) == prix(en) and bool(prix(fr)), prix(en))


# ── 2 · Dans le navigateur ───────────────────────────────────────────────
class Muet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def lettre_en(dossier, nom, d):
    (dossier / nom).write_text(poser(d), encoding="utf-8")
    return nom


def navigateur(base):
    tmp = ICI / "_vues"
    tmp.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        nav = pw.chromium.launch()

        print("\n· le constructeur anglais")
        ctx = nav.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        pg = ctx.new_page()
        erreurs, envois = [], {}
        pg.on("pageerror", lambda e: erreurs.append(str(e)))

        def capter(route, nom, reponse):
            try:
                envois[nom] = json.loads(route.request.post_data or "{}")
            except Exception:
                envois[nom] = {}
            route.fulfill(status=200, content_type="application/json", body=json.dumps(reponse))

        pg.route("**/functions/v1/malettre-plume", lambda r: capter(r, "plume", {
            "ok": True, "titre": "Merry Christmas, Ama", "lettre": ["One.", "Two."], "formule": "With love,", "restantes": 2}))
        pg.route("**/functions/v1/malettre-commande", lambda r: capter(r, "commande", {
            "ok": True, "offert": True, "adresse": "https://malettre.nebula-agency.online/l/abc"}))
        pg.goto(base + "en/creer.html")
        pg.wait_for_function("document.getElementById('apercu').srcdoc.length > 3000", timeout=8000)
        dit("en : la page est en anglais (lang, titre)", pg.evaluate("document.documentElement.lang") == "en"
            and pg.title().endswith("write it"))
        dit("en : les familles d'occasions sont en anglais", pg.inner_text("#liste-occasions .fam >> nth=0").strip().lower() == "love")
        pg.click('.occ[data-id="noel"]')
        dit("en : Noël pose « Merry Christmas » et sa formule", pg.input_value("#f-titre") == "Merry Christmas"
            and pg.input_value("#f-formule") == "Merry Christmas,")
        dit("en : Noël propose le 25 décembre à minuit", pg.input_value("#f-quand").endswith("-12-25")
            and pg.input_value("#f-quand-h") == "00:00")
        pg.fill("#f-pour", "Ama")
        pg.fill("#f-de", "Kojo")
        pg.click("#questions .puce >> nth=0")
        dit("en : les questions de la plume sont en anglais", "Who are they to you?" in pg.inner_text("#questions"))
        pg.click("#btn-plume")
        pg.wait_for_function("document.getElementById('f-lettre').value.length > 0", timeout=6000)
        f = envois.get("plume", {})
        dit("en : la fiche part à la plume avec langue « en »", f.get("langue") == "en", f.get("langue"))
        dit("en : et ses questions en anglais", any(r.get("q") == "Who are they to you?" for r in f.get("reponses", [])))
        pg.wait_for_timeout(600)
        apercu = pg.eval_on_selector("#apercu", "e => e.srcdoc")
        dit("en : l'aperçu porte la langue de la lettre", '"langue":"en"' in apercu and '"occasion":"Christmas"' in apercu)
        pg.click("#vers-palier")
        pg.click('.pal[data-id="carte"]')
        dit("en : La Carte s'appelle « The Card » et coûte 1 500 F avec la plume",
            "The Card" in pg.inner_text('.pal[data-id="carte"]') and "1 500 F" in pg.inner_text('.pal[data-id="carte"] .px').replace("\u00a0", " "))
        pg.click("#vers-paiement")
        dit("en : le bouton dit « Pay 1 500 F »", pg.inner_text("#btn-commander").strip().replace("\u00a0", " ") == "Pay 1 500 F",
            pg.inner_text("#btn-commander"))
        pg.fill("#f-wa", "0197085576")
        pg.click("#btn-commander")
        pg.wait_for_timeout(800)
        c = envois.get("commande", {})
        dit("en : la commande part avec langue « en »", c.get("langue") == "en", c.get("langue"))
        dit("en : et l'occasion en anglais", c.get("occasion") == "Christmas", c.get("occasion"))
        dit("en : « Order received. » à la fin", "Order received." in pg.inner_text("#e-fini"))
        dit("en : aucune erreur JavaScript", not erreurs, erreurs[:2])
        ctx.close()

        print("\n· la lettre reçue, en anglais")
        dossier = ICI / "_vues"
        demain = datetime.now() + timedelta(days=2)
        base_d = {"occasion": "Birthday", "pour": "Ama", "de": "Kojo", "titre": "Happy birthday", "code": "",
                  "lettre": ["Tell me about your day."], "photos": [], "formule": "", "pied": True,
                  "lien": "https://malettre.nebula-agency.online/en/", "langue": "en"}
        ctx = nav.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        pg = ctx.new_page()
        erreurs = []
        pg.on("pageerror", lambda e: erreurs.append(str(e)))
        n = lettre_en(dossier, "_qc_en_futur.html", dict(base_d, ouvre=demain.strftime("%Y-%m-%dT00:00"), depuis=""))
        pg.goto(base + "_vues/" + n)
        pg.wait_for_timeout(300)
        jour = demain.strftime("%A")
        dit("lettre en : la page est en anglais", pg.evaluate("document.documentElement.lang") == "en")
        dit("lettre en : « My letter to Ama »", pg.inner_text(".pour").strip().lower() == "my letter to ama"
            and pg.title() == "My letter to Ama", (pg.inner_text(".pour"), pg.title()))
        dit("lettre en : « A letter is waiting for you. »", pg.inner_text("#s-touche").strip() == "A letter is waiting for you.")
        q = pg.inner_text("#att-quand")
        dit("lettre en : elle dit quand elle s'ouvre, en anglais", q.startswith("It opens " + jour) and q.rstrip(".").endswith("at midnight"), q)
        dit("lettre en : le compte à rebours dit « in … »", pg.inner_text("#att-reste").startswith("in "), pg.inner_text("#att-reste"))
        ctx.close()

        ctx = nav.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: erreurs.append(str(e)))
        cent = (datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")
        n = lettre_en(dossier, "_qc_en_ouverte.html", dict(base_d, ouvre="", depuis=cent, code="2468"))
        pg.goto(base + "_vues/" + n)
        dit("lettre en : le bouton dit « Break the seal »", pg.inner_text("#btn-ouvrir").strip() == "Break the seal")
        pg.click("#btn-ouvrir")
        dit("lettre en : le code se demande en anglais", pg.inner_text("#s-touche").strip() == "Enter the code you were given."
            and "locked with a code" in pg.inner_text("#code"))
        dit("lettre en : les cases du code ont des noms anglais",
            pg.get_attribute("#cases input >> nth=0", "aria-label") == "Digit 1")
        for i, ch in enumerate("1111"):
            pg.fill("#cases input >> nth=%d" % i, ch)
        dit("lettre en : un mauvais code se dit en anglais", "not the right code" in pg.inner_text("#code-msg"))
        for i, ch in enumerate("2468"):
            pg.fill("#cases input >> nth=%d" % i, ch)
        pg.wait_for_timeout(1800)
        # ⚠️ text_content, pas inner_text : innerText applique le text-transform
        # (« DAYS TOGETHER »), et la sonde accusait une page juste.
        dit("lettre en : « days together »", pg.text_content("#l-jours-lib").strip() == "days together",
            pg.text_content("#l-jours-lib"))
        dit("lettre en : la formule par défaut est anglaise", pg.inner_text("#l-formule").strip() == "With all my heart,")
        pied = pg.inner_text("#pied-lien").strip()
        dit("lettre en : le pied dit « Write yours » et mène à la page anglaise",
            pied == "Write yours: Ma lettre à…" and pg.get_attribute("#pied-lien", "href").endswith("/en/"), pied)
        dit("lettre en : la note du pied est anglaise", "In five minutes." in pg.inner_text("#l-pied .note"))
        dit("lettre en : le texte de l'acheteur n'est jamais traduit", "Tell me about your day." in pg.inner_text("#l-corps"))
        dit("lettre en : aucune erreur JavaScript", not erreurs, erreurs[:2])
        ctx.close()

        print("\n· les lettres d'exemple anglaises, rendues")
        ctx = nav.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        pg = ctx.new_page()
        # ⚠️ « papa » est lu AVANT puis APRÈS l'ouverture : lu seulement après,
        # le seuil (déjà effacé) cachait « Une lettre t'attend. » resté en français.
        for ex, ouvrir in (("afi", False), ("papa", False), ("papa", True)):
            pg.goto(base + "en/exemples/%s.html" % ex)
            if ouvrir:
                pg.click("#btn-ouvrir")
                pg.wait_for_timeout(1500)
            # Le corps est écrit par la plume (relu par son propre garde-fou) :
            # ici, seuls les mots du GABARIT comptent.
            txt = pg.evaluate("() => { const c = document.getElementById('l-corps'); if (c) c.remove(); return document.body.innerText; }")
            dit("exemple %s : le gabarit parle anglais (%s)" % (ex, "ouverte" if ouvrir else "scellée"),
                not francais(txt) and "Example ·" in pg.text_content("#l-occasion"), txt[:120])
        ctx.close()

        print("\n· le paiement et le merci, en anglais")
        ctx = nav.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        pg = ctx.new_page()
        pg.goto(base + "en/paiement.html")
        pg.evaluate("""() => localStorage.setItem('malettre:paiement', JSON.stringify({paiement: 'https://pay.example/x',
            pour: 'Ama', palier: 'The Letter', somme: '5 000 F', adresse: 'https://malettre.nebula-agency.online/l/abc',
            ouvre: '2026-12-25T00:00', jeton: 'abc'}))""")
        pg.reload()
        dit("paiement en : la date se dit en anglais", pg.inner_text("#r-heure").strip() == "25 December at midnight",
            pg.inner_text("#r-heure"))
        dit("paiement en : « Pay 5 000 F »", pg.inner_text("#btn-mot").strip() == "Pay 5 000 F")
        dit("paiement en : « Back to my letter » mène au constructeur anglais",
            pg.eval_on_selector("a.retour", "a => a.href").endswith("/en/creer.html"))
        pg.goto(base + "en/merci.html?j=abc")
        wa = pg.get_attribute("#wa", "href")
        dit("merci en : « Thank you. » et un message WhatsApp anglais", pg.inner_text("#titre").strip() == "Thank you."
            and "Hello%2C%20I've%20just%20paid" in wa, wa[:80])
        ctx.close()

        print("\n· les sélecteurs de langue")
        ctx = nav.new_context()
        pg = ctx.new_page()
        for de, vers, attendu in (("creer.html", "a.langue", "/en/creer.html"), ("en/creer.html", "a.langue", "/creer.html")):
            pg.goto(base + de)
            href = pg.eval_on_selector(vers, "a => a.href")
            r = pg.request.get(href)
            dit("%s mène à %s (%d)" % (de, attendu, r.status), href.endswith(attendu) and r.status == 200, href)
        ctx.close()
        nav.close()
    for f in ("_qc_en_futur.html", "_qc_en_ouverte.html"):
        try:
            (ICI / "_vues" / f).unlink()
        except OSError:
            pass


def main():
    statiques()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Muet, directory=str(ICI)))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        navigateur("http://127.0.0.1:%d/" % srv.server_address[1])
    finally:
        srv.shutdown()
    print("\n%d contrôles verts, %d en échec" % (len(verts), len(rouges)))
    for n, d in rouges:
        print("  ✗ %s %s" % (n, d))
    return 1 if rouges else 0


if __name__ == "__main__":
    sys.exit(main())

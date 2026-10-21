# -*- coding: utf-8 -*-
"""MA LETTRE À… · les contrôles de la page d'accueil (`index.html`).

    python malettre/_build_accueil.py && python malettre/_qc_accueil.py

Ce qu'une suite verte doit prouver ici, et que l'œil ne voit pas :
- le livrable est à jour de sa source, et il ne dit aucun prix à la main
  (les timbres sont comparés aux catalogues LUS dans `creer.html` par le
  navigateur, pas par la regex du build : sinon le contrôle vérifierait le
  build par lui-même) ;
- le prénom tapé arrive vraiment dans le constructeur ;
- chaque exemple ouvre une VRAIE lettre, qui dit qu'elle est un exemple, et
  rien ne ressemble à un avis client (faux témoignage) ;
- le chargement se retire seul, et n'existe pas sans JavaScript ;
- rien ne déborde, rien ne saute (CLS), aucune cible sous 44 px, et le
  contraste est mesuré sur les PIXELS rendus (le texte d'abord lu, PUIS
  rendu transparent : l'inverse mesurait du vide, leçon Luxury Club) ;
- qui a coupé les animations voit toute la page.

⚠️ Les images par seconde au défilement (processeur ralenti ×4) sont une
MESURE, imprimée : Chromium sans écran rend sans carte graphique, le chiffre
ne vaut que comparé à lui-même d'une version à l'autre.
"""
import datetime
import functools
import html
import json
import pathlib
import re
import sys
import threading
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from playwright.sync_api import sync_playwright

ICI = pathlib.Path(__file__).resolve().parent
SOURCE = ICI / "_accueil_src.html"
NEBULA_WA = "22996740732"  # le numéro de NEBULA, le même que `merci.html`

# Les deux langues (2026-10-16) : les MÊMES contrôles, sur l'accueil français
# puis sur l'accueil anglais. Ce qui change, c'est ce qu'on s'attend à lire.
OFFRE_FP = ICI / "faire-part" / "offre.json"
LLMS = ICI / "llms.txt"
SOURCES = [SOURCE, ICI / "creer.html", ICI / "lettre.html", ICI / "_build_accueil.py", OFFRE_FP]
LANGS = {
    "fr": {"tag": "fr", "index": ICI / "index.html", "prefixe": "", "exemples": ICI / "exemples.json",
           "dossier": "exemples", "inventes": "personnes inventées", "marque": '"occasion":"Exemple · ',
           "og": "og.jpg", "offert": "Offert", "plume": "La plume", "des": "la plume dès ",
           "seuil": '"titre":"C\'est l\'heure"', "occ": "Exemple", "fp_mot": "faire-part", "sep": " : ",
           "sources": SOURCES + [ICI / "exemples.json"]},
    "en": {"tag": "en", "index": ICI / "en" / "index.html", "prefixe": "en/", "exemples": ICI / "exemples.en.json",
           "dossier": "en/exemples", "inventes": "invented people", "marque": '"occasion":"Example · ',
           "og": "og-en.jpg", "offert": "Free", "plume": "The Quill", "des": "the Quill from ",
           "seuil": '"titre":"It\'s time"', "occ": "Example", "fp_mot": "wedding", "sep": ": ",
           "sources": SOURCES + [ICI / "exemples.en.json", ICI / "i18n" / "en.txt", ICI / "en" / "creer.html"]},
}
L = LANGS["fr"]   # la langue en cours, posée par main()
NB = " "

verts, rouges = [], []


def ok(nom):
    nom = "%s · %s" % (L["tag"], nom)
    verts.append(nom)
    print("  [ok] %s" % nom)


def ko(nom, detail=""):
    nom = "%s · %s" % (L["tag"], nom)
    rouges.append((nom, detail))
    print("  [KO] %s %s" % (nom, ("-> " + str(detail)) if detail else ""))


def dit(nom, cond, detail=""):
    (ok(nom) if cond else ko(nom, detail))
    return cond


class Muet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def fmt(n):
    if n == 0:
        return L["offert"]
    return re.sub(r"\B(?=(\d{3})+(?!\d))", " ", str(n)) + " F"


def plat(t):
    return re.sub(r"\s+", " ", (t or "").replace(NB, " ")).strip()


# ── 1 · Le fichier lui-même ──────────────────────────────────────────────
def statiques():
    print("\n· le livrable")
    INDEX = L["index"]
    s = INDEX.read_text(encoding="utf-8")
    vieux = [p.name for p in L["sources"] if p.stat().st_mtime > INDEX.stat().st_mtime + 1]
    dit("index.html est à jour de ses sources (sinon : python malettre/_build_accueil.py)", not vieux, vieux)
    dit("aucun marqueur du build oublié", "<!--__" not in s and "/*__DONNEES__*/" not in s)
    dit("aucun tiret cadratin dans la page", "—" not in s, s.count("—"))
    dit("aucune trace de l'ancien nom (LE PLI, lepli)", not re.search(r"LE PLI|Le Pli|lepli", s))
    dit("aucun script chargé d'ailleurs", not re.search(r"<script[^>]+src=", s, re.I))
    avis = re.findall(r"AggregateRating|\"Review\"|ratingValue|reviewRating", s)
    dit("aucun balisage d'avis (des personnes inventées ne notent rien)", not avis, avis)
    dit("la page dit que les exemples sont inventés", L["inventes"] in s)
    dit("le chargement porte « by NEBULA Agency »", "by NEBULA Agency" in s)
    dit("le retrait se demande au WhatsApp de NEBULA",
        bool(re.search(r'id="retrait" href="https://wa\.me/%s\?text=' % NEBULA_WA, s)))
    og = re.search(r'property="og:image" content="([^"]+)"', s)
    dit("l'image de partage existe sur le disque (%s)" % L["og"],
        bool(og) and og.group(1).endswith("/" + L["og"]) and (ICI / L["og"]).exists())
    canon = re.search(r'rel="canonical" href="([^"]+)"', s)
    # L'image vit à la racine du site (/og-en.jpg), la page anglaise sous /en/ :
    # on exige le même DOMAINE, et un og:url égal à l'adresse canonique.
    site = re.match(r"https://[^/]+/", canon.group(1)).group(0) if canon else "?"
    dit("canonical, og:url et og:image sur le même site",
        bool(canon and og) and og.group(1).startswith(site) and ('og:url" content="%s"' % canon.group(1)) in s)

    doc = json.loads(L["exemples"].read_text(encoding="utf-8"))
    ids = [x["id"] for x in doc["exemples"]]
    for x in doc["exemples"]:
        f = ICI / L["dossier"] / ("%s.html" % x["id"])
        t = f.read_text(encoding="utf-8") if f.exists() else ""
        dit("exemple %s : une vraie lettre, marquée « %s · »" % (x["id"], L["occ"]),
            L["marque"] in t and "noindex" in t)
        dit("exemple %s : aucun tiret cadratin" % x["id"],
            "—" not in json.dumps(x, ensure_ascii=False))
    dit("une carte par exemple, ni plus ni moins",
        sorted(re.findall(r'class="carte" type="button" data-id="([a-z]+)"', s)) == sorted(ids))

    # Vague 3 : les exemples sont HABILLÉS, chacun autrement, et leur lettre le porte.
    mal = []
    for x in doc["exemples"]:
        t = (ICI / L["dossier"] / ("%s.html" % x["id"])).read_text(encoding="utf-8")
        h = x.get("habillage") or {}
        if not h or any('"%s":"%s"' % (k, v) not in t for k, v in h.items()):
            mal.append(x["id"])
        if x.get("gratter") and json.dumps(x["gratter"], ensure_ascii=False) not in t:
            mal.append(x["id"] + " (phrase à gratter)")
    dit("chaque exemple porte son habillage dans sa lettre", not mal, mal)
    combis = {json.dumps(x.get("habillage"), sort_keys=True) for x in doc["exemples"]}
    dit("six exemples, six habillages différents", len(combis) == len(ids), len(combis))
    dit("deux exemples au moins cachent une phrase à gratter", sum(1 for x in doc["exemples"] if x.get("gratter")) >= 2)

    # llms.txt : à jour, sans tiret cadratin, et il porte chaque question de la page.
    llms = LLMS.read_text(encoding="utf-8") if LLMS.exists() else ""
    dit("llms.txt existe et est à jour de la page", bool(llms) and LLMS.stat().st_mtime + 1 >= INDEX.stat().st_mtime)
    qs = [plat(html.unescape(re.sub(r"<[^>]+>", "", q))) for q in re.findall(r"<summary>(.*?)</summary>", s)]
    dit("llms.txt porte les %d questions de la page" % len(qs), qs and all(q in plat(llms) for q in qs),
        [q for q in qs if q not in plat(llms)][:2])
    dit("llms.txt : aucun tiret cadratin", "—" not in llms)
    return s


# ── 2 · Dans le navigateur ───────────────────────────────────────────────
PROBE = ".sur, .h2, .chapo, .petit, .champ span, .qui label, .etape h3, .etape p, .carte .occ, .carte .a1, .carte .de, " \
        ".carte .verrou, .mention, .fiche-d .t, .fiche-d .q, .fiche-d .libre, .puce, .lettre-d .o, .lettre-d h3, " \
        ".lettre-d p, .pl-prix span, .fam-t, .case .ev b, .case .ev span, .case .bord, .timbre .nm, .timbre .vl, " \
        ".timbre .ds, .payer, .billet b, .billet p, .aveu, .pied p, .marque, .barre nav a, .pri, .sec-btn, " \
        ".bientot, .fp-o, .fp-noms, .fp-dit, .fp-date, .fp-lieu, .fp-rep span, .fp-h, .fp-p, .fp-prix span, " \
        ".hb-t, .hb-l, .faq summary, .faq .r p, .ecris, .timbre .hb"



def lum(c):
    v = [x / 255 for x in c]
    v = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in v]
    return .2126 * v[0] + .7152 * v[1] + .0722 * v[2]


def rgb(css):
    return tuple(int(float(x)) for x in re.findall(r"[\d.]+", css)[:3])


def mesurer(pg, sel):
    """Un texte : sa couleur LUE, puis le fond PHOTOGRAPHIÉ sous lui, texte effacé.

    ⚠️ Ni `clip` (coordonnées du document, la découpe tombait hors de l'image)
    ni capture d'élément : en émulation téléphone, celle-ci refait défiler la
    page, et le fond était mesuré une section à côté (le titre des exemples,
    sur papier, mesuré sur la nuit). On photographie l'ÉCRAN, et on découpe le
    rectangle relu au même instant ; si la page a bougé entre-temps, on jette.
    """
    from io import BytesIO
    from PIL import Image
    # ⚠️ GSAP (2026-10-21) : un mouvement lié au défilement a de l'INERTIE (scrub).
    # Après le saut de scrollIntoView, la feuille est encore en train de se
    # redresser : on la laisse arriver (la pose qu'un visiteur lit), sinon on
    # photographie le fond d'à côté. Et l'opacité est celle qu'on VOIT : le
    # produit des parents, et rien si un parent est caché (le bouton de la fin
    # de la nuit des lettres, invisible tant qu'on n'y est pas, mesurait 1,07:1).
    info = pg.evaluate("""(s) => { const e = document.querySelector(s); e.scrollIntoView({block: 'center'});
        if (window.ScrollTrigger) { ScrollTrigger.update();
            ScrollTrigger.getAll().forEach(t => { const tw = t.getTween && t.getTween(); if (tw) tw.progress(1); }); }
        const cs = getComputedStyle(e);
        let o = 1, x = e;
        while (x && x.nodeType === 1) { const c = getComputedStyle(x); o *= parseFloat(c.opacity); x = x.parentElement; }
        if (cs.visibility === 'hidden') o = 0;
        return {c: cs.color, o: o, t: parseFloat(cs.fontSize), g: parseInt(cs.fontWeight),
                nom: (e.className || e.id || e.tagName) + ' « ' + e.innerText.trim().slice(0, 30) + ' »'}; }""", sel)
    r = pg.evaluate("""(s) => { const e = document.querySelector(s); e.classList.add('sonde-x');
        const r = e.getBoundingClientRect();
        return {x: r.left, y: r.top, w: r.width, h: r.height, vw: innerWidth, vh: innerHeight, sy: scrollY}; }""", sel)
    png = pg.screenshot()
    bouge = pg.evaluate("(s) => { document.querySelector(s).classList.remove('sonde-x'); return scrollY; }", sel)
    x0, y0 = max(0, r["x"]), max(0, r["y"])
    x1, y1 = min(r["x"] + r["w"], r["vw"]), min(r["y"] + r["h"], r["vh"])
    # hors de l'écran, transparent, ou page qui a bougé : rien de fiable à photographier
    if info["o"] < .99 or r["y"] < 0 or r["y"] + r["h"] > r["vh"] or x1 - x0 < 3 or y1 - y0 < 3 or bouge != r["sy"]:
        return None
    im = Image.open(BytesIO(png)).convert("RGB")
    k = im.width / r["vw"]
    px = sorted(im.crop((int(x0 * k), int(y0 * k), int(x1 * k), int(y1 * k))).getdata(), key=lum)
    fond = px[len(px) // 2]
    lt, lf = lum(rgb(info["c"])), lum(fond)
    grand = info["t"] >= 24 or (info["t"] >= 18.66 and info["g"] >= 700)
    return {"ratio": (max(lt, lf) + .05) / (min(lt, lf) + .05), "seuil": 3.0 if grand else 4.5,
            "fond": fond, "nom": info["nom"]}


def contraste(pg, larg):
    """Tous les textes de la page, puis le TÉMOIN : une sonde qui ne voit pas
    un gris sur gris, ou qui ne lit pas le papier sous un bouton papier, ment."""
    pg.add_style_tag(content=".sonde-x,.sonde-x *{color:transparent!important;text-shadow:none!important;"
                             "-webkit-text-fill-color:transparent!important}")
    n = pg.evaluate("(s) => { let i = 0; document.querySelectorAll(s).forEach(e => { "
                    "const r = e.getBoundingClientRect(); if (r.width > 4 && r.height > 4 && e.offsetParent !== null"
                    " && getComputedStyle(e).visibility !== 'hidden' && (e.innerText || '').trim()) e.dataset.sonde = i++; });"
                    " return i; }", PROBE)
    pires, mesures = [], 0
    for i in range(n):
        m = mesurer(pg, '[data-sonde="%d"]' % i)
        if not m:
            continue
        mesures += 1
        if m["ratio"] < m["seuil"]:
            pires.append("%s %.2f:1 (seuil %.1f)" % (m["nom"], m["ratio"], m["seuil"]))
    dit("%d : contraste mesuré sur les pixels, %d textes, tous au seuil" % (larg, mesures), mesures > 40 and not pires,
        "; ".join(pires[:6]) or ("seulement %d mesures" % mesures))

    papier = mesurer(pg, ".barre .pri")
    dit("%d : témoin, la sonde lit le papier sous le bouton de la barre" % larg,
        bool(papier) and max(abs(a - b) for a, b in zip(papier["fond"], (244, 237, 224))) <= 6,
        papier and papier["fond"])
    pg.evaluate("""() => { const t = document.createElement('p'); t.id = 'temoin-sonde'; t.textContent = 'Témoin gris sur gris';
        t.style.cssText = 'background:#8a8a8a;color:#9a9a9a;font-size:16px;padding:10px;margin:0';
        document.querySelector('#exemples .etroit').appendChild(t); }""")
    gris = mesurer(pg, "#temoin-sonde")
    pg.evaluate("() => document.getElementById('temoin-sonde').remove()")
    dit("%d : témoin, la sonde attrape un gris sur gris" % larg, bool(gris) and gris["ratio"] < 1.5,
        gris and round(gris["ratio"], 2))


def defiler_tout(pg, larg):
    """Descend toute la page par pas d'un demi-écran, en relevant les débordements.

    ⚠️ On compare à la largeur DEMANDÉE, jamais à `innerWidth` : au téléphone,
    un élément trop large ÉLARGIT la fenêtre de mise en page (le navigateur
    dézoome), et `scrollWidth <= innerWidth` reste vrai. Le champ du prénom
    poussait la page à 597 px, et ce contrôle-là passait au vert.
    """
    return pg.evaluate("""async (L) => {
        const pause = ms => new Promise(r => setTimeout(r, ms));
        let deborde = 0, pire = 0;
        for (let y = 0; y < document.documentElement.scrollHeight; y += 422) {
            scrollTo(0, y); await pause(45);
            const sw = Math.max(document.documentElement.scrollWidth, innerWidth);
            if (sw > L + 1) { deborde++; pire = Math.max(pire, sw - L); }
        }
        scrollTo(0, document.documentElement.scrollHeight); await pause(1800);
        return {deborde, pire};
    }""", larg)


def vague3(pg, larg, cat, offre):
    """La vitrine de la vague 3 : ce qu'elle promet, prouvé dans le navigateur."""
    norm = lambda t: re.sub(r"\s+", " ", (t or "").replace(NB, " ")).strip()

    # La FAQ visible et son FAQPage : la même chose, mot pour mot.
    r = pg.evaluate("""() => {
        const ld = [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => JSON.parse(s.textContent))
            .find(x => x['@type'] === 'FAQPage');
        return {ld: ld ? ld.mainEntity.map(q => [q.name, q.acceptedAnswer.text]) : null, lang: ld && ld.inLanguage,
                vis: [...document.querySelectorAll('.faq details.q')].map(d => [d.querySelector('summary').textContent,
                      d.querySelector('.r').textContent])}; }""")
    vis = [[norm(a), norm(b)] for a, b in r["vis"]]
    ld = [[norm(a), norm(b)] for a, b in (r["ld"] or [])]
    dit("%d : la FAQ visible et son FAQPage disent la même chose (%d questions)" % (larg, len(vis)),
        len(vis) >= 6 and vis == ld and r["lang"] == L["tag"], (len(vis), len(ld), r["lang"]))
    mots = [len(b.split()) for a, b in vis]
    dit("%d : chaque réponse tient debout seule (30 à 75 mots)" % larg, all(30 <= m <= 75 for m in mots), mots)
    pg.click(".faq details.q summary")
    pg.wait_for_timeout(700)
    dit("%d : une question s'ouvre au toucher, sa réponse se lit" % larg,
        pg.evaluate("() => { const d = document.querySelector('.faq details.q'); return d.open"
                    " && d.querySelector('.r').getBoundingClientRect().height > 20; }"))
    pg.click(".faq details.q summary")

    # Le faire-part : SON prix, celui de offre.json, partout où il est écrit.
    prix = fmt(offre["prix"])
    dit("%d : le faire-part dit le prix de offre.json (%s), au bloc et dans la FAQ" % (larg, prix),
        plat(pg.inner_text(".fp-prix .px")) == prix and prix in vis[-1][1], plat(pg.inner_text(".fp-prix .px")))
    href = pg.get_attribute("#fp-demander", "href") or ""
    m = re.match(r"https://wa\.me/(\d+)\?text=(.+)$", href)
    dit("%d : « Demander notre faire-part » écrit au WhatsApp de NEBULA, message prêt" % larg,
        bool(m) and m.group(1) == offre["whatsapp"] and L["fp_mot"] in urllib.parse.unquote(m.group(2)).lower(), href[:90])
    dit("%d : la barre mène au faire-part" % larg,
        pg.evaluate("() => !!document.querySelector('.barre nav a[href=\"#faire-part\"]') && !!document.getElementById('faire-part')"))
    # « Ouvrir l'exemple » : le VRAI faire-part (vague 4), dans la fenêtre téléphone.
    pg.click("#fp-voir")
    try:
        fr = pg.frame_locator("#modale-cadre")
        qui = fr.locator("#s-pour").text_content(timeout=4000) or ""
    except Exception:
        qui = ""
    src = pg.get_attribute("#modale-cadre", "src") or ""
    dit("%d : « Ouvrir l'exemple » montre le vrai faire-part de Kossi et Afiwa" % larg,
        re.search(r"faire-part/exemple(-en)?\.html$", src) is not None and "Kossi" in qui and "Afiwa" in qui, (src, qui))
    pg.click("#modale-fermer")
    q = pg.get_attribute("#question", "href") or ""
    dit("%d : « Une autre question ? » écrit au WhatsApp de NEBULA" % larg, q.startswith("https://wa.me/%s?text=" % NEBULA_WA), q[:60])

    # Les timbres disent ce que chaque offre débloque : l'habillage, là où il est.
    hb = pg.evaluate("() => [...document.querySelectorAll('.timbre:not(.plume-t)')].map(t => !!t.querySelector('.hb'))")
    dit("%d : « + l'habillage » sur chaque offre qui le porte, et seulement elles" % larg,
        hb == [p["habillage"] for p in cat["paliers"]], hb)

    # La prochaine grande date : recalculée ici, à part, sur les dates du constructeur.
    auj = datetime.date.today()

    def prochaine(j):
        x = datetime.date(auj.year, int(j[:2]), int(j[3:5]))
        return x if x >= auj else datetime.date(auj.year + 1, int(j[:2]), int(j[3:5]))
    o = min(cat["dates"], key=lambda d: prochaine(d["jour"]))
    n = (prochaine(o["jour"]) - auj).days
    t = plat(pg.inner_text("#bientot"))
    lien = pg.get_attribute("#bientot a", "href") or ""
    dit("%d : la prochaine grande date est juste (%s, %d jours)" % (larg, o["nom"], n),
        o["nom"] in t and (n < 2 or str(n) in t) and lien.endswith("creer.html?occasion=" + o["id"]), (t, lien))

    # « Ouvre-la toi-même » : la lettre nue attend 10 s, la pastille la rhabille.
    groupes = pg.evaluate("""() => ['cire', 'papier', 'pluie'].map(k => [...document.querySelectorAll('input[name="hb-' + k + '"]')]
        .map(i => [i.value, i.checked]))""")
    dit("%d : une pastille par cire, papier et pluie du constructeur, la première cochée" % larg,
        [[v for v, c in g] for g in groupes] == [cat["hab"][k] for k in ("cire", "papier", "pluie")]
        and all(g[0][1] and not any(c for v, c in g[1:]) for g in groupes), groupes)
    doc0 = pg.get_attribute("#seuil-cadre", "srcdoc") or ""
    ouvre = re.search(r'"ouvre":"([^"]+)"', doc0)
    reste = pg.evaluate("(s) => (new Date(s) - Date.now()) / 1000", ouvre.group(1)) if ouvre else 99
    dit("%d : témoin, la lettre de départ est nue et s'ouvre dans 10 s au plus" % larg,
        '"habillage"' not in doc0 and reste <= 10.5, round(reste, 1))
    pg.click('input[name="hb-cire"][value="or"]')
    try:
        pg.wait_for_function("""() => (document.getElementById('seuil-cadre').srcdoc || '').includes('"cire":"or"')""", timeout=3000)
        fr = pg.query_selector("#seuil-cadre").content_frame()
        fr.wait_for_function("document.documentElement.classList.contains('cire-or')", timeout=4000)
        pg.click('input[name="hb-papier"][value="nuit"]')
        pg.wait_for_function("""() => (document.getElementById('seuil-cadre').srcdoc || '').includes('"papier":"nuit"')""", timeout=3000)
        fr = pg.query_selector("#seuil-cadre").content_frame()
        fr.wait_for_function("document.documentElement.classList.contains('papier-nuit')"
                             " && document.documentElement.classList.contains('cire-or')", timeout=4000)
        doc1 = pg.get_attribute("#seuil-cadre", "srcdoc")
        ok("%d : une pastille rhabille la vraie lettre (cire or, puis papier nuit)" % larg)
        dit("%d : rhabillée, elle s'ouvre tout de suite et cache une phrase à gratter" % larg,
            '"ouvre":""' in doc1 and '"gratter":"' in doc1)
        fr.wait_for_selector("#btn-ouvrir", state="visible", timeout=4000)
        fr.evaluate("document.getElementById('btn-ouvrir').click()")
        fr.wait_for_selector("#l-gratter", state="visible", timeout=5000)
        ok("%d : on brise le cachet, la phrase à gratter paraît" % larg)
    except Exception as x:
        ko("%d : une pastille rhabille la vraie lettre, qui s'ouvre" % larg, str(x)[:120])
    pg.click("#seuil-refaire")
    pg.wait_for_timeout(300)
    doc2 = pg.get_attribute("#seuil-cadre", "srcdoc") or ""
    dit("%d : « recommencer » la referme avec son habillage, l'heure à attendre" % larg,
        '"papier":"nuit"' in doc2 and re.search(r'"ouvre":"\d{4}-', doc2) is not None)


POSER = """() => { if (window.ScrollTrigger) { ScrollTrigger.update();
    ScrollTrigger.getAll().forEach(t => { const tw = t.getTween && t.getTween(); if (tw) tw.progress(1); }); } }"""


def profondeur(pg, larg, cat, base):
    """La profondeur (2026-10-21) : GSAP servi d'ici, la nuit des lettres, les
    volets du faire-part, la barre d'achat. On laisse chaque mouvement arriver
    (`POSER`) avant de lire : c'est la pose qu'un visiteur voit."""
    pg.evaluate("() => scrollTo(0, 60)")
    try:
        pg.wait_for_function("document.documentElement.classList.contains('gsap')", timeout=8000)
        ok("%d : GSAP est arrivé après un geste" % larg)
    except Exception:
        ko("%d : GSAP est arrivé après un geste" % larg)
    scripts = pg.evaluate("() => performance.getEntriesByType('resource').filter(r => r.initiatorType === 'script').map(r => r.name)")
    dit("%d : aucun script d'une autre origine, GSAP servi d'ici et versionné" % larg,
        all(x.startswith(base) for x in scripts) and any("vendor/gsap.min.js?v=3.13.0" in x for x in scripts)
        and any("vendor/ScrollTrigger.min.js?v=3.13.0" in x for x in scripts), scripts)

    # Les fonds : exactement les zones dont l'image est sur le disque ; celui du
    # héros s'est allumé quand le rideau s'est levé (et pas dans le premier écran).
    zones = sorted({p.name[:-len("-l.webp")] for p in (ICI / "fonds").glob("*-l.webp")})
    poses = pg.evaluate("() => [...document.querySelectorAll('.fond')].map(f => f.dataset.fond).sort()")
    heros = pg.evaluate("""() => { const f = document.querySelector('.fond[data-fond="heros"] i b');
        return f ? getComputedStyle(f).backgroundImage : ''; }""")
    dit("%d : un fond par image présente sur le disque (%d), celui du héros allumé après le rideau" % (larg, len(zones)),
        poses == zones and ("heros" not in zones or "heros-" in heros), (poses, zones, heros[:70]))

    # La musique : le bouton n'existe que si le morceau est sur le disque, et son crédit va au pied.
    if (ICI / "son" / "musique.mp3").exists():
        b = pg.evaluate("""() => { const b = document.getElementById('son'); if (!b) return null; const r = b.getBoundingClientRect();
            return [Math.round(r.width), Math.round(r.height), b.getAttribute('aria-label'), b.dataset.src]; }""")
        cre = pg.evaluate("() => (document.querySelector('.credit-son') || {}).textContent || ''")
        dit("%d : le bouton son (44 px, nommé, le morceau d'ici) et le crédit de la musique au pied" % larg,
            bool(b) and b[0] >= 44 and b[1] >= 44 and bool(b[2]) and b[3].endswith("son/musique.mp3") and "Pixabay" in cre, (b, cre))

    # La nuit des lettres : une enveloppe par occasion RÉELLE, puis la caméra.
    noms = pg.evaluate("() => [...document.querySelectorAll('.nl-ev b')].map(b => b.textContent)")
    dit("%d : la nuit des lettres porte une enveloppe par occasion du constructeur (%d)" % (larg, len(noms)),
        [plat(n) for n in noms] == [plat(n) for n in cat["noms"]], (len(noms), len(cat["noms"])))

    def nuit(p):
        pg.evaluate("""p => { const s = document.getElementById('nuit-lettres'); const top = s.getBoundingClientRect().top + scrollY;
            scrollTo(0, top - 62 + p * (s.offsetHeight - innerHeight)); }""", p)
        # On ATTEND que la caméra arrive (inertie 1,1 s), comme un visiteur qui
        # s'arrête : pousser l'inertie à sa fin ne suffisait pas sur un PC chargé.
        pg.wait_for_timeout(150)
        pg.evaluate(POSER)
        pg.wait_for_timeout(1500)
        return pg.evaluate("""() => ({texte: parseFloat(getComputedStyle(document.getElementById('nl-texte')).opacity),
            fin: document.getElementById('nl-fin').classList.contains('on'),
            achat: document.getElementById('achat-bas').classList.contains('on'),
            vues: [...document.querySelectorAll('.nl-ev')].filter(e => getComputedStyle(e).visibility === 'visible'
                  && parseFloat(e.style.opacity) > .05).length,
            tienne: (() => { const t = document.querySelector('.nl-vol .nl-tienne'); return t ? [t.classList.contains('allume'),
                  t.querySelector('.nl-nom').textContent, getComputedStyle(t).visibility] : null; })()})""")
    a, m, z = nuit(0.0), nuit(.5), nuit(1.0)
    dit("%d : nuit, au début : le titre se lit, le bouton n'est pas encore là" % larg, a["texte"] > .95 and not a["fin"], a)
    dit("%d : nuit, au milieu : des enveloppes traversent le ciel, le titre s'est effacé" % larg,
        m["vues"] >= 3 and m["texte"] < .05, m)
    dit("%d : nuit, à la fin : la tienne arrive au prénom tapé, cachet allumé, et le bouton paraît" % larg,
        z["fin"] and z["tienne"] and z["tienne"][0] and z["tienne"][1] == "Sèna" and z["tienne"][2] == "visible", z)
    # ⚠️ Vu sur capture : la barre d'achat recouvrait « Écrire la mienne » (deux boutons empilés).
    # Au téléphone seulement (sur ordinateur, la barre n'existe pas) ; relu après quelques images,
    # le temps que la boucle tourne (le PC chargé retardait sa lecture).
    if larg < 761:
        pg.wait_for_timeout(300)
        achat = pg.evaluate("() => document.getElementById('achat-bas').classList.contains('on')")
        dit("%d : nuit, à la fin : la barre d'achat s'efface devant « Écrire la mienne »" % larg, not achat, z)

    # Le faire-part : les volets s'ouvrent sur le carton.
    pg.evaluate("() => document.querySelector('.fp-carton').scrollIntoView({block: 'center'})")
    pg.wait_for_timeout(150)
    pg.evaluate(POSER)
    pg.wait_for_timeout(1000)
    ang = pg.evaluate("""() => [...document.querySelectorAll('.fp-volet')].map(v => {
        const m = new DOMMatrix(getComputedStyle(v).transform); return Math.round(Math.atan2(-m.m13, m.m11) * 180 / Math.PI); })""")
    dit("%d : le faire-part ouvre ses deux volets quand on le regarde" % larg,
        len(ang) == 2 and ang[0] <= -90 and ang[1] >= 90, ang)

    # La barre d'achat : au téléphone seulement, après le héros, jamais devant la fin.
    if larg < 761:
        def etat(js):
            pg.evaluate(js)
            pg.wait_for_timeout(300)
            return pg.evaluate("() => document.getElementById('achat-bas').classList.contains('on')")
        haut = etat("() => scrollTo(0, 0)")
        milieu = etat("() => document.getElementById('prix').scrollIntoView()")
        fin = etat("() => document.querySelector('#fin .qui').scrollIntoView({block: 'center'})")
        fond = pg.evaluate("() => getComputedStyle(document.getElementById('achat-bas')).backgroundColor")
        lien = pg.get_attribute("#achat-bas a", "href")
        dit("%d : la barre d'achat paraît après le héros, s'efface devant le formulaire de la fin, opaque" % larg,
            not haut and milieu and not fin and fond.startswith("rgb(") and lien == "creer.html", (haut, milieu, fin, fond, lien))
    else:
        dit("%d : pas de barre d'achat sur ordinateur" % larg,
            pg.evaluate("() => getComputedStyle(document.getElementById('achat-bas')).display") == "none")


def navigateur(base, s):
    with sync_playwright() as pw:
        nav = pw.chromium.launch()

        # Le catalogue tel que le NAVIGATEUR le lit dans creer.html.
        ctx = nav.new_context()
        pg = ctx.new_page()
        page = base + L["prefixe"]
        pg.goto(page + "creer.html")
        cat = pg.evaluate("() => ({paliers: PALIERS.map(p => ({nom: p.nom, prix: p.prix, habillage: !!p.habillage})),"
                          " plume: PLUME.prix, occasions: OCCASIONS.map(o => o.id), noms: OCCASIONS.map(o => o.nom),"
                          " dates: OCCASIONS.filter(o => o.jour).map(o => ({id: o.id, nom: o.nom, jour: o.jour})),"
                          " hab: {cire: HABILLAGE.cire.map(o => o.id), papier: HABILLAGE.papier.map(o => o.id),"
                          " pluie: HABILLAGE.pluie.map(o => o.id)}})")
        ctx.close()
        offre = json.loads(OFFRE_FP.read_text(encoding="utf-8"))

        # llms.txt dit les prix du constructeur, lus par le navigateur.
        llms = plat(LLMS.read_text(encoding="utf-8"))
        manque = [p["nom"] for p in cat["paliers"]
                  if plat("%s%s%s" % (p["nom"], L["sep"], fmt(p["prix"]) if p["prix"] else "0 F")) not in llms]
        dit("llms.txt dit le nom et le prix de chaque offre du constructeur", not manque, manque)
        dit("llms.txt dit le prix de la plume et du faire-part",
            ("+" + fmt(cat["plume"])) in llms and fmt(offre["prix"]) in llms)

        for larg, haut, mob in ((390, 844, True), (1440, 900, False)):
            print("\n· en %d" % larg)
            ctx = nav.new_context(viewport={"width": larg, "height": haut}, is_mobile=mob, has_touch=mob)
            pg = ctx.new_page()
            erreurs = []
            pg.on("pageerror", lambda e: erreurs.append(str(e)))
            pg.add_init_script("""window.__cls = 0; new PerformanceObserver(l => { for (const e of l.getEntries())
                if (!e.hadRecentInput) window.__cls += e.value; }).observe({type: 'layout-shift', buffered: true});""")
            poids = []
            pg.on("response", lambda r: poids.append(r))
            pg.goto(page, wait_until="domcontentloaded")
            # ⚠️ Lu TOUT DE SUITE : le chargement vit 3 s, et attendre « load »
            # puis peser les réponses (polices comprises) en prenait parfois plus.
            # La sonde lisait alors « none » sur une page juste.
            vu = pg.evaluate("() => getComputedStyle(document.getElementById('chargement')).display")
            pg.wait_for_load_state("load")
            pg.wait_for_timeout(1200)
            octets = 0
            for r in poids:
                try:
                    octets += len(r.body())
                except Exception:
                    pass
            dit("%d : premier écran sous 320 Ko (fichiers bruts, polices comprises)" % larg, octets < 320 * 1024,
                "%d Ko" % (octets // 1024))
            # GSAP (2026-10-21) arrive APRÈS le premier écran, jamais dedans.
            dit("%d : GSAP n'est pas dans le premier écran" % larg, not any("/vendor/" in r.url for r in poids),
                [r.url for r in poids if "/vendor/" in r.url][:2])
            iw = pg.evaluate("() => Math.max(innerWidth, document.documentElement.scrollWidth)")
            dit("%d : la page tient dans l'écran dès l'ouverture (aucun dézoom)" % larg, iw <= larg, iw)
            dit("%d : le chargement couvre la page à l'ouverture" % larg, vu != "none", vu)
            try:
                pg.wait_for_function("document.getElementById('chargement').hidden", timeout=4800)
                ok("%d : le chargement se retire seul (filet à 4,5 s)" % larg)
            except Exception:
                ko("%d : le chargement se retire seul (filet à 4,5 s)" % larg)

            # Le prénom tapé : le héros le montre, puis le constructeur le reçoit.
            pg.fill("#q-pour", "Sèna")
            dit("%d : le prénom tapé s'écrit dans le titre" % larg, pg.inner_text("#nom-heros").strip() == "Sèna")

            # La scène avance : trois moments, trois poses.
            poses = []
            for p in (0.0, 0.5, 1.0):
                pg.evaluate("""p => { const s = document.getElementById('comment');
                    const top = s.getBoundingClientRect().top + scrollY;
                    scrollTo(0, top + p * (s.offsetHeight - (innerHeight - 62))); }""", p)
                pg.wait_for_timeout(250)
                poses.append(pg.evaluate("() => [document.getElementById('objet').style.transform,"
                                         " document.getElementById('feuille').style.transform,"
                                         " [...document.querySelectorAll('.etape')].findIndex(e => e.classList.contains('on'))]"))
            dit("%d : la scène avance au défilement (3 poses différentes)" % larg,
                len({p[0] + p[1] for p in poses}) == 3, poses)
            dit("%d : la légende suit (1re étape au début, 7e à la fin)" % larg, poses[0][2] == 0 and poses[2][2] == 6,
                [p[2] for p in poses])
            dit("%d : la feuille de la scène porte le prénom tapé" % larg,
                pg.evaluate("() => document.querySelector('#feuille .texte .a b').textContent") == "Sèna")

            pg.evaluate("() => scrollTo(0, 0)")
            d = defiler_tout(pg, larg)
            dit("%d : rien ne déborde à droite, de haut en bas" % larg, d["deborde"] == 0, d)
            restes = pg.evaluate("() => [...document.querySelectorAll('[data-rv]')].filter(e =>"
                                 " !e.classList.contains('vu') || parseFloat(getComputedStyle(e).opacity) < .99).length")
            dit("%d : toutes les révélations ont eu lieu" % larg, restes == 0, restes)
            cls = pg.evaluate("() => window.__cls")
            dit("%d : rien ne saute (CLS < 0,05)" % larg, cls < 0.05, round(cls, 4))

            # Les cibles : 44 px. Les liens DANS une phrase en sont dispensés (WCAG 2.5.8).
            petites = pg.evaluate("""() => [...document.querySelectorAll('a, button, input, .carte, .case')]
                .filter(e => e.offsetParent !== null && !e.closest('p') && !e.closest('[hidden]'))
                .map(e => { const r = e.getBoundingClientRect(); return [e.className || e.id || e.tagName, Math.round(r.width), Math.round(r.height)]; })
                .filter(x => x[2] < 44 || x[1] < 44)""")
            dit("%d : aucune cible tactile sous 44 px" % larg, not petites, petites[:5])
            # ⚠️ « Write my letter » passait sur deux lignes au téléphone quand le
            # sélecteur de langue est arrivé dans la barre (vu sur capture).
            hb = pg.evaluate("() => document.querySelector('.barre .pri').getBoundingClientRect().height")
            dit("%d : le bouton de la barre tient sur une ligne" % larg, hb <= 48, round(hb))

            # Les éléments fixes ne sont sous aucun parent transformé.
            tr = pg.evaluate("""() => ['chargement', 'modale', 'plume-s', 'achat-bas'].map(id => { let e = document.getElementById(id).parentElement, n = 0;
                while (e) { if (getComputedStyle(e).transform !== 'none') n++; e = e.parentElement; } return n; })""")
            dit("%d : chargement, modale, curseur et barre d'achat sous aucun parent transformé" % larg, tr == [0, 0, 0, 0], tr)

            # Le prix : chaque timbre contre le catalogue du constructeur.
            timbres = pg.evaluate("() => [...document.querySelectorAll('.timbre')].map(t => [t.querySelector('.nm').textContent, t.querySelector('.vl').textContent])")
            attendu = [[p["nom"], fmt(p["prix"])] for p in cat["paliers"]] + [[L["plume"], "+" + fmt(cat["plume"])]]
            dit("%d : les timbres disent les prix du constructeur" % larg,
                [[plat(a), plat(b)] for a, b in timbres] == attendu, (timbres, attendu))
            dit("%d : le prix de la plume, partout le même" % larg,
                plat(pg.inner_text(".pl-prix .px")) == fmt(cat["plume"]) and (L["des"] + fmt(cat["plume"])) in plat(pg.inner_text(".petit")))
            occ = pg.evaluate("() => [...document.querySelectorAll('.case')].map(a => new URL(a.href).searchParams.get('occasion'))")
            dit("%d : chaque case du casier mène à une occasion qui existe (%d)" % (larg, len(occ)),
                len(occ) == len(cat["occasions"]) and set(occ) == set(cat["occasions"]))

            # Les exemples : la modale montre la vraie lettre.
            ids = pg.evaluate("() => [...document.querySelectorAll('.carte')].map(c => c.dataset.id)")
            mauvais = []
            for cid in ids:
                pg.click('.carte[data-id="%s"]' % cid)
                pg.wait_for_timeout(150)
                src = pg.get_attribute("#modale-cadre", "src") or ""
                fr = pg.frame_locator("#modale-cadre")
                try:
                    occ_t = fr.locator("#l-occasion").text_content(timeout=4000) or ""
                except Exception:
                    occ_t = ""
                if src != "exemples/%s.html" % cid or not occ_t.startswith(L["occ"]):
                    mauvais.append((cid, src, occ_t))
                pg.click("#modale-fermer")
                if not pg.evaluate("() => document.getElementById('modale').hidden"):
                    mauvais.append((cid, "ne se ferme pas"))
            dit("%d : chaque exemple ouvre sa vraie lettre, marquée « %s »" % (larg, L["occ"]), ids and not mauvais, mauvais)
            pg.click('.carte[data-id="%s"]' % ids[0])
            pg.keyboard.press("Escape")
            dit("%d : Échap ferme la modale et rend le focus à la carte" % larg,
                pg.evaluate("() => document.getElementById('modale').hidden && document.activeElement.dataset.id") == ids[0])

            # Le seuil : une vraie lettre, rebâtie depuis le gabarit.
            pg.evaluate("() => document.getElementById('seuil').scrollIntoView()")
            try:
                pg.wait_for_function("(document.getElementById('seuil-cadre').srcdoc || '').length > 5000", timeout=6000)
                doc = pg.get_attribute("#seuil-cadre", "srcdoc")
                dit("%d : le seuil joue une vraie lettre (gabarit rempli)" % larg,
                    "/*MALETTRE_DONNEES*/" not in doc and L["seuil"] in doc)
            except Exception:
                ko("%d : le seuil joue une vraie lettre (gabarit rempli)" % larg, "srcdoc jamais posé")

            vague3(pg, larg, cat, offre)
            profondeur(pg, larg, cat, base)

            # Les réponses ouvertes, le temps que le pli finisse : leur contraste se mesure aussi.
            pg.evaluate("() => document.querySelectorAll('.faq details.q').forEach(d => d.open = true)")
            pg.wait_for_timeout(900)
            contraste(pg, larg)

            # Enfin : le prénom part au constructeur.
            pg.evaluate("() => scrollTo(0, 0)")
            pg.fill("#q-pour", "Sèna")
            pg.click(".heros .qui button[type=submit]")
            pg.wait_for_url(re.compile(r"creer\.html\?pour="), timeout=6000)
            pg.wait_for_timeout(400)
            dit("%d : le prénom tapé arrive dans le constructeur" % larg, pg.input_value("#f-pour") == "Sèna",
                pg.input_value("#f-pour"))
            dit("%d : aucune erreur JavaScript" % larg, not erreurs, erreurs[:3])
            ctx.close()

        # Mouvement réduit : tout est là, sans défiler.
        print("\n· mouvement réduit, sans JavaScript")
        ctx = nav.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, reduced_motion="reduce")
        pg = ctx.new_page()
        pg.goto(page, wait_until="load")
        try:
            pg.wait_for_function("document.getElementById('chargement').hidden", timeout=1500)
            ok("mouvement réduit : le chargement part en moins d'1,5 s")
        except Exception:
            ko("mouvement réduit : le chargement part en moins d'1,5 s")
        caches = pg.evaluate("() => [...document.querySelectorAll('[data-rv], .etape')].filter(e => parseFloat(getComputedStyle(e).opacity) < .99).length")
        dit("mouvement réduit : tout est visible sans défiler (révélations, 7 étapes)", caches == 0, caches)
        dit("mouvement réduit : la scène n'est plus épinglée",
            pg.evaluate("() => getComputedStyle(document.querySelector('.scene-cadre')).position") == "relative")
        pg.evaluate("() => scrollTo(0, document.documentElement.scrollHeight / 2)")
        pg.wait_for_timeout(400)
        dit("mouvement réduit : la nuit des lettres à plat (titre, la tienne, le bouton), et GSAP jamais chargé",
            pg.evaluate("""() => getComputedStyle(document.querySelector('.nl-cadre')).position === 'relative'
                && parseFloat(getComputedStyle(document.getElementById('nl-fin')).opacity) > .99
                && getComputedStyle(document.querySelector('.nl-fin .nl-tienne')).display !== 'none'
                && !document.querySelector('script[src*="vendor/"]')"""))
        ctx.close()

        ctx = nav.new_context(viewport={"width": 390, "height": 844}, java_script_enabled=False)
        pg = ctx.new_page()
        pg.goto(page, wait_until="load")
        dit("sans JavaScript : pas de chargement qui couvrirait tout", pg.locator("#chargement").is_hidden())
        dit("sans JavaScript : les sections sont lisibles",
            pg.locator("#prix .h2").is_visible() and pg.locator(".timbre").first.is_visible())
        dit("sans JavaScript : la nuit des lettres se lit (titre, la tienne, le bouton)",
            pg.locator("#nl-titre").is_visible() and pg.locator(".nl-fin .pri").is_visible()
            and pg.locator(".nl-fin .nl-tienne").is_visible())
        ctx.close()

        # La mesure : images par seconde dans la scène, processeur ralenti ×4.
        # Une seule fois : la scène est la même dans les deux langues.
        if L["tag"] != "fr":
            nav.close()
            return
        ctx = nav.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        pg = ctx.new_page()
        pg.goto(page, wait_until="load")
        pg.wait_for_function("document.getElementById('chargement').hidden", timeout=6000)
        cdp = ctx.new_cdp_session(pg)
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
        ips = pg.evaluate("""() => new Promise(fin => {
            const s = document.getElementById('comment'), top = s.getBoundingClientRect().top + scrollY;
            const long = s.offsetHeight - innerHeight, t = [];
            let y = 0, d = performance.now();
            function pas(now) { t.push(now - d); d = now; y += long / 180; scrollTo(0, top + y);
              if (y < long) requestAnimationFrame(pas); else { t.sort((a, b) => a - b);
                fin({med: 1000 / t[t.length >> 1], p95: 1000 / t[Math.floor(t.length * .95)]}); } }
            requestAnimationFrame(pas); })""")
        print("  [mesure] scène, processeur ×4 : %.0f images/s en médiane, %.0f au 95e centile"
              % (ips["med"], ips["p95"]))
        dit("la scène ne s'effondre pas sous un processeur ×4 (médiane ≥ 15 images/s)", ips["med"] >= 15,
            "%.1f" % ips["med"])
        ctx.close()
        nav.close()


def main():
    global L
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Muet, directory=str(ICI)))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        for langue in ("fr", "en"):
            L = LANGS[langue]
            print("\n════════ %s ════════" % langue)
            s = statiques()
            navigateur("http://127.0.0.1:%d/" % srv.server_address[1], s)
    finally:
        srv.shutdown()
    print("\n%d contrôles verts, %d en échec" % (len(verts), len(rouges)))
    for n, d in rouges:
        print("  ✗ %s %s" % (n, d))
    return 1 if rouges else 0


if __name__ == "__main__":
    sys.exit(main())

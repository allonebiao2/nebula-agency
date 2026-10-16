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
import functools
import json
import pathlib
import re
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from playwright.sync_api import sync_playwright

ICI = pathlib.Path(__file__).resolve().parent
INDEX = ICI / "index.html"
SOURCE = ICI / "_accueil_src.html"
EXEMPLES = ICI / "exemples.json"
NEBULA_WA = "22996740732"  # le numéro de NEBULA, le même que `merci.html`
NB = " "

verts, rouges = [], []


def ok(nom):
    verts.append(nom)
    print("  [ok] %s" % nom)


def ko(nom, detail=""):
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
        return "Offert"
    return re.sub(r"\B(?=(\d{3})+(?!\d))", " ", str(n)) + " F"


def plat(t):
    return re.sub(r"\s+", " ", (t or "").replace(NB, " ")).strip()


# ── 1 · Le fichier lui-même ──────────────────────────────────────────────
def statiques():
    print("\n· le livrable")
    s = INDEX.read_text(encoding="utf-8")
    sources = [SOURCE, EXEMPLES, ICI / "creer.html", ICI / "lettre.html", ICI / "_build_accueil.py"]
    vieux = [p.name for p in sources if p.stat().st_mtime > INDEX.stat().st_mtime + 1]
    dit("index.html est à jour de ses sources (sinon : python malettre/_build_accueil.py)", not vieux, vieux)
    dit("aucun marqueur du build oublié", "<!--__" not in s and "/*__DONNEES__*/" not in s)
    dit("aucun tiret cadratin dans la page", "—" not in s, s.count("—"))
    dit("aucune trace de l'ancien nom (LE PLI, lepli)", not re.search(r"LE PLI|Le Pli|lepli", s))
    dit("aucun script chargé d'ailleurs", not re.search(r"<script[^>]+src=", s, re.I))
    avis = re.findall(r"AggregateRating|\"Review\"|ratingValue|reviewRating", s)
    dit("aucun balisage d'avis (des personnes inventées ne notent rien)", not avis, avis)
    dit("la page dit que les exemples sont inventés", "personnes inventées" in s)
    dit("le chargement porte « by NEBULA Agency »", "by NEBULA Agency" in s)
    dit("le retrait se demande au WhatsApp de NEBULA",
        bool(re.search(r'id="retrait" href="https://wa\.me/%s\?text=' % NEBULA_WA, s)))
    og = re.search(r'property="og:image" content="([^"]+)"', s)
    dit("l'image de partage existe sur le disque (og.jpg)",
        bool(og) and og.group(1).endswith("/og.jpg") and (ICI / "og.jpg").exists())
    canon = re.search(r'rel="canonical" href="([^"]+)"', s)
    dit("canonical, og:url et og:image sur la même adresse",
        bool(canon and og) and og.group(1).startswith(canon.group(1)) and ('og:url" content="%s"' % canon.group(1)) in s)

    doc = json.loads(EXEMPLES.read_text(encoding="utf-8"))
    ids = [x["id"] for x in doc["exemples"]]
    for x in doc["exemples"]:
        f = ICI / "exemples" / ("%s.html" % x["id"])
        t = f.read_text(encoding="utf-8") if f.exists() else ""
        dit("exemple %s : une vraie lettre, marquée « Exemple · »" % x["id"],
            '"occasion":"Exemple · ' in t and "noindex" in t)
        dit("exemple %s : aucun tiret cadratin" % x["id"],
            "—" not in json.dumps(x, ensure_ascii=False))
    dit("une carte par exemple, ni plus ni moins",
        sorted(re.findall(r'class="carte" type="button" data-id="([a-z]+)"', s)) == sorted(ids))
    return s


# ── 2 · Dans le navigateur ───────────────────────────────────────────────
PROBE = ".sur, .h2, .chapo, .petit, .champ span, .qui label, .etape h3, .etape p, .carte .occ, .carte .a1, .carte .de, " \
        ".carte .verrou, .mention, .fiche-d .t, .fiche-d .q, .fiche-d .libre, .puce, .lettre-d .o, .lettre-d h3, " \
        ".lettre-d p, .pl-prix span, .fam-t, .case .ev b, .case .ev span, .case .bord, .timbre .nm, .timbre .vl, " \
        ".timbre .ds, .payer, .billet b, .billet p, .aveu, .pied p, .marque, .barre nav a, .pri, .sec-btn"



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
    info = pg.evaluate("""(s) => { const e = document.querySelector(s); e.scrollIntoView({block: 'center'});
        const cs = getComputedStyle(e);
        return {c: cs.color, o: parseFloat(cs.opacity), t: parseFloat(cs.fontSize), g: parseInt(cs.fontWeight),
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


def navigateur(base, s):
    with sync_playwright() as pw:
        nav = pw.chromium.launch()

        # Le catalogue tel que le NAVIGATEUR le lit dans creer.html.
        ctx = nav.new_context()
        pg = ctx.new_page()
        pg.goto(base + "creer.html")
        cat = pg.evaluate("() => ({paliers: PALIERS.map(p => ({nom: p.nom, prix: p.prix})), plume: PLUME.prix,"
                          " occasions: OCCASIONS.map(o => o.id)})")
        ctx.close()

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
            pg.goto(base, wait_until="load")
            pg.wait_for_timeout(1200)
            octets = 0
            for r in poids:
                try:
                    octets += len(r.body())
                except Exception:
                    pass
            dit("%d : premier écran sous 320 Ko (fichiers bruts, polices comprises)" % larg, octets < 320 * 1024,
                "%d Ko" % (octets // 1024))
            iw = pg.evaluate("() => Math.max(innerWidth, document.documentElement.scrollWidth)")
            dit("%d : la page tient dans l'écran dès l'ouverture (aucun dézoom)" % larg, iw <= larg, iw)
            vu = pg.evaluate("() => getComputedStyle(document.getElementById('chargement')).display")
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

            # Les éléments fixes ne sont sous aucun parent transformé.
            tr = pg.evaluate("""() => ['chargement', 'modale', 'plume-s'].map(id => { let e = document.getElementById(id).parentElement, n = 0;
                while (e) { if (getComputedStyle(e).transform !== 'none') n++; e = e.parentElement; } return n; })""")
            dit("%d : chargement, modale et curseur sous aucun parent transformé" % larg, tr == [0, 0, 0], tr)

            # Le prix : chaque timbre contre le catalogue du constructeur.
            timbres = pg.evaluate("() => [...document.querySelectorAll('.timbre')].map(t => [t.querySelector('.nm').textContent, t.querySelector('.vl').textContent])")
            attendu = [[p["nom"], fmt(p["prix"])] for p in cat["paliers"]] + [["La plume", "+" + fmt(cat["plume"])]]
            dit("%d : les timbres disent les prix du constructeur" % larg,
                [[plat(a), plat(b)] for a, b in timbres] == attendu, (timbres, attendu))
            dit("%d : le prix de la plume, partout le même" % larg,
                plat(pg.inner_text(".pl-prix .px")) == fmt(cat["plume"]) and ("la plume dès " + fmt(cat["plume"])) in plat(pg.inner_text(".petit")))
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
                if src != "exemples/%s.html" % cid or not occ_t.startswith("Exemple"):
                    mauvais.append((cid, src, occ_t))
                pg.click("#modale-fermer")
                if not pg.evaluate("() => document.getElementById('modale').hidden"):
                    mauvais.append((cid, "ne se ferme pas"))
            dit("%d : chaque exemple ouvre sa vraie lettre, marquée « Exemple »" % larg, ids and not mauvais, mauvais)
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
                    "/*MALETTRE_DONNEES*/" not in doc and '"titre":"C\'est l\'heure"' in doc)
            except Exception:
                ko("%d : le seuil joue une vraie lettre (gabarit rempli)" % larg, "srcdoc jamais posé")

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
        pg.goto(base, wait_until="load")
        try:
            pg.wait_for_function("document.getElementById('chargement').hidden", timeout=1500)
            ok("mouvement réduit : le chargement part en moins d'1,5 s")
        except Exception:
            ko("mouvement réduit : le chargement part en moins d'1,5 s")
        caches = pg.evaluate("() => [...document.querySelectorAll('[data-rv], .etape')].filter(e => parseFloat(getComputedStyle(e).opacity) < .99).length")
        dit("mouvement réduit : tout est visible sans défiler (révélations, 7 étapes)", caches == 0, caches)
        dit("mouvement réduit : la scène n'est plus épinglée",
            pg.evaluate("() => getComputedStyle(document.querySelector('.scene-cadre')).position") == "relative")
        ctx.close()

        ctx = nav.new_context(viewport={"width": 390, "height": 844}, java_script_enabled=False)
        pg = ctx.new_page()
        pg.goto(base, wait_until="load")
        dit("sans JavaScript : pas de chargement qui couvrirait tout", pg.locator("#chargement").is_hidden())
        dit("sans JavaScript : les sections sont lisibles",
            pg.locator("#prix .h2").is_visible() and pg.locator(".timbre").first.is_visible())
        ctx.close()

        # La mesure : images par seconde dans la scène, processeur ralenti ×4.
        ctx = nav.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        pg = ctx.new_page()
        pg.goto(base, wait_until="load")
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
    s = statiques()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Muet, directory=str(ICI)))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        navigateur("http://127.0.0.1:%d/" % srv.server_address[1], s)
    finally:
        srv.shutdown()
    print("\n%d contrôles verts, %d en échec" % (len(verts), len(rouges)))
    for n, d in rouges:
        print("  ✗ %s %s" % (n, d))
    return 1 if rouges else 0


if __name__ == "__main__":
    sys.exit(main())

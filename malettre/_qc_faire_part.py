# -*- coding: utf-8 -*-
"""MA LETTRE À… · les contrôles du FAIRE-PART DE MARIAGE (vague 4).

    python malettre/_faire_part.py && python malettre/_qc_faire_part.py

Ce qu'une suite verte doit prouver :
- le générateur REFUSE une fiche fausse (numéro, date passée, lien de carte
  qui n'est pas Google Maps), et accepte `</script>` et U+2028 dans un mot
  sans casser la page (le témoin s'affiche tel quel) ;
- un vrai couple reçoit un jeton de 16 caractères, GARDÉ d'une fabrication à
  l'autre, et `publies.txt` porte son EMPREINTE, jamais le jeton (le dépôt
  est public, le jeton est l'adresse) ;
- une photo devient une donnée, réduite à 1 200 px ;
- dans le navigateur : aucune requête réseau, le cachet aux initiales se
  brise, le compte vise le jour J À L'HEURE DU LIEU, chaque moment a sa carte,
  les deux réponses partent vers le WhatsApp DES MARIÉS avec le prénom, le
  nombre et la date, l'exemple n'envoie rien ; le jour passé, plus de réponse ;
- rien ne déborde au téléphone, aucune cible sous 44 px, contraste mesuré sur
  les PIXELS (avec témoin), mouvement réduit respecté.
"""
import datetime
import hashlib
import json
import pathlib
import re
import shutil
import sys
import tempfile
import urllib.parse

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import _faire_part as FP  # noqa: E402

from playwright.sync_api import sync_playwright  # noqa: E402

verts, rouges = [], []
NB = " "


def dit(nom, cond, detail=""):
    if cond:
        verts.append(nom)
        print("  [ok] %s" % nom)
    else:
        rouges.append((nom, detail))
        print("  [KO] %s %s" % (nom, ("-> " + str(detail)) if detail else ""))
    return cond


def refuse(fiche, dossier, nom):
    """La fiche doit être REFUSÉE, et rien ne doit être écrit."""
    p = dossier / (nom + ".json")
    p.write_text(json.dumps(fiche, ensure_ascii=False), encoding="utf-8")
    sortie = dossier / (nom + ".html")
    try:
        FP.fabriquer(p, sortie)
        return False
    except SystemExit:
        return not sortie.exists()


def donnees(page):
    a, b = page.index(FP.DEBUT) + len(FP.DEBUT), page.index(FP.FIN)
    return json.loads(page[a:b].replace("<\\/", "</").replace("<\\!--", "<!--"))


def instant(d):
    signe = 1 if d["fuseau"][0] == "+" else -1
    hh, mm = int(d["fuseau"][1:3]), int(d["fuseau"][4:6])
    loc = datetime.datetime.fromisoformat("%sT%s:00" % (d["date"], d["heure"]))
    return (loc - signe * datetime.timedelta(hours=hh, minutes=mm)).replace(tzinfo=datetime.timezone.utc)


# ── 1 · Le générateur ────────────────────────────────────────────────────
def generateur(tmp):
    print("\n· le générateur")
    base = json.loads((FP.DOSSIER / "exemple.json").read_text(encoding="utf-8"))
    vrai = dict(base, exemple=False, whatsapp="2290197000000")
    vrai.pop("_lire", None)

    for (src, page) in FP.EXEMPLES:
        sources = [src, FP.GABARIT, ICI / "_faire_part.py"]
        vieux = [s.name for s in sources if s.stat().st_mtime > page.stat().st_mtime + 1]
        dit("%s est à jour (sinon : python malettre/_faire_part.py)" % page.name, not vieux, vieux)
        t = page.read_text(encoding="utf-8")
        d = donnees(t)
        dit("%s : noindex, aucun tiret cadratin, moins de 60 Ko" % page.name,
            "noindex" in t and "—" not in t and len(t.encode("utf-8")) < 60 * 1024)
        dit("%s : marqué exemple, sans numéro (ses réponses ne partent nulle part)" % page.name,
            d["exemple"] is True and d["whatsapp"] == "")
        urls = set(re.findall(r'https?://[^\s"\'<>)]+', t))
        etrangers = [u for u in urls if not re.match(r"https://(wa\.me/|www\.google\.com/maps|malettre\.nebula-agency\.online)", u)
                     and not FP.CARTE.match(u)]
        dit("%s : aucune adresse hors WhatsApp, Google Maps et le site" % page.name, not etrangers, etrangers[:3])

    # Les refus
    dit("témoin : un numéro sans indicatif est refusé", refuse(dict(vrai, whatsapp="0197000000x"), tmp, "r1"))
    dit("témoin : un mariage déjà passé est refusé", refuse(dict(vrai, date="2020-05-02"), tmp, "r2"))
    prog = [dict(vrai["programme"][0], carte="https://exemple.invalid/maps?q=x")]
    dit("témoin : un lien de carte qui n'est pas Google Maps est refusé", refuse(dict(vrai, programme=prog), tmp, "r3"))
    dit("témoin : un exemple avec un numéro est refusé", refuse(dict(base, whatsapp="2290197000000"), tmp, "r4"))
    dit("témoin : une photo introuvable est refusée", refuse(dict(vrai, photos=["absente.jpg"]), tmp, "r5"))

    # Le jeton, l'empreinte, l'adresse stable — dans un dossier à part, jamais dans _couples/.
    vieux = (FP.SORTIE, FP.PUBLIES)
    FP.SORTIE, FP.PUBLIES = tmp / "sortie", tmp / "publies.txt"
    try:
        fiche = tmp / "couple.json"
        fiche.write_text(json.dumps(vrai, ensure_ascii=False), encoding="utf-8")
        FP.fabriquer(fiche)
        j1 = json.loads(fiche.read_text(encoding="utf-8")).get("jeton", "")
        FP.fabriquer(fiche)
        j2 = json.loads(fiche.read_text(encoding="utf-8")).get("jeton", "")
        pub = FP.PUBLIES.read_text(encoding="utf-8")
        dit("un vrai couple reçoit un jeton de 16 caractères, gardé d'une version à l'autre",
            re.fullmatch(r"[%s]{16}" % FP.ALPHABET, j1) is not None and j1 == j2, (j1, j2))
        dit("sa page s'appelle par son jeton", (FP.SORTIE / ("%s.html" % j1)).exists())
        dit("publies.txt porte l'EMPREINTE du jeton, jamais le jeton",
            hashlib.sha256(j1.encode()).hexdigest() in pub and j1 not in pub)
    finally:
        FP.SORTIE, FP.PUBLIES = vieux
    lignes = [l for l in FP.PUBLIES.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    dit("publies.txt (le vrai) : seulement des empreintes", all(re.fullmatch(r"[0-9a-f]{64}", l) for l in lignes), lignes[:2])

    # Témoin de la garde de _dist.py : une page publiée absente de ce disque fait
    # REFUSER le livrable (sinon un déploiement d'ailleurs l'effacerait du site).
    import subprocess
    avant = FP.PUBLIES.read_bytes()
    try:
        FP.PUBLIES.write_bytes(avant + (hashlib.sha256(b"temoin-absent-du-disque").hexdigest() + "\n").encode("ascii"))
        r = subprocess.run([sys.executable, str(ICI / "_dist.py")], capture_output=True, text=True, encoding="utf-8",
                           env=dict(__import__("os").environ, PYTHONIOENCODING="utf-8"))
        dit("témoin : _dist.py refuse si un faire-part publié manque sur ce disque",
            r.returncode != 0 and "absent(s) de ce disque" in (r.stdout + r.stderr), (r.returncode, (r.stdout + r.stderr)[-120:]))
    finally:
        FP.PUBLIES.write_bytes(avant)

    # Une photo devient une donnée, réduite
    from PIL import Image
    Image.new("RGB", (2400, 1800), (120, 90, 60)).save(tmp / "grande.png")
    p = FP.fabriquer(_fiche(tmp, "photo", dict(vrai, photos=["grande.png"])), tmp / "photo.html")
    d = donnees(p.read_text(encoding="utf-8"))
    import base64
    import io
    ok_photo = False
    if d["photos"] and d["photos"][0].startswith("data:image/jpeg;base64,"):
        im = Image.open(io.BytesIO(base64.b64decode(d["photos"][0].split(",", 1)[1])))
        ok_photo = max(im.size) <= 1200
    dit("une photo devient une donnée JPEG d'au plus 1 200 px", ok_photo)

    # Les pièges d'écriture : </script>, commentaire, U+2028
    piege = "Nous vous attendons </script><script>window.__pirate=1</script> <!-- " + chr(0x2028) + " fin"
    pp = FP.fabriquer(_fiche(tmp, "piege", dict(vrai, mot=piege)), tmp / "piege.html")
    t = pp.read_text(encoding="utf-8")
    bloc = t[t.index(FP.DEBUT):t.index(FP.FIN)]
    dit("témoin : </script>, <!-- et U+2028 sont neutralisés dans les données",
        "</script>" not in bloc and "<!--" not in bloc and chr(0x2028) not in bloc)
    vrai_page = FP.fabriquer(_fiche(tmp, "vrai", vrai), tmp / "vrai.html")
    return {"vrai": vrai_page, "piege": pp, "piege_texte": piege, "photo": p}


def _fiche(tmp, nom, f):
    p = tmp / (nom + ".json")
    p.write_text(json.dumps(f, ensure_ascii=False), encoding="utf-8")
    return p


# ── 2 · Dans le navigateur ───────────────────────────────────────────────
SONDE = (".exemple, .familles, .annonce, .noms, .oui, .date, .heure-l, .ville, .compte .sous, .chiffres b, .chiffres i, "
         ".mot p, .sec h2, .prog .h, .prog b, .prog .lieu, .prog a, .tenue p, .avant, .reponse label, .nombre > span, "
         ".choix a, .pied a")


def ouvrir_page(nav, chemin, larg=390, haut=844, mob=True, doux=False):
    ctx = nav.new_context(viewport={"width": larg, "height": haut}, is_mobile=mob, has_touch=mob,
                          reduced_motion="reduce" if doux else "no-preference")
    pg = ctx.new_page()
    erreurs, reseau = [], []
    pg.on("pageerror", lambda e: erreurs.append(str(e)))
    pg.on("request", lambda r: reseau.append(r.url) if not r.url.startswith(("file:", "data:")) else None)
    pg.goto(pathlib.Path(chemin).as_uri())
    pg.wait_for_timeout(300)
    return ctx, pg, erreurs, reseau


def contraste(pg, nom):
    from _qc_accueil import mesurer
    pg.add_style_tag(content=".sonde-x,.sonde-x *{color:transparent!important;text-shadow:none!important;"
                             "-webkit-text-fill-color:transparent!important}")
    n = pg.evaluate("(s) => { let i = 0; document.querySelectorAll(s).forEach(e => { const r = e.getBoundingClientRect();"
                    " if (r.width > 4 && r.height > 4 && e.offsetParent !== null && (e.innerText || '').trim()) e.dataset.sonde = i++; });"
                    " return i; }", SONDE)
    pires, mesures = [], 0
    for i in range(n):
        m = mesurer(pg, '[data-sonde="%d"]' % i)
        if not m:
            continue
        mesures += 1
        if m["ratio"] < m["seuil"]:
            pires.append("%s %.2f:1" % (m["nom"], m["ratio"]))
    dit("%s : contraste mesuré sur les pixels, %d textes au seuil" % (nom, mesures), mesures >= 20 and not pires,
        "; ".join(pires[:5]) or mesures)
    pg.evaluate("""() => { const t = document.createElement('p'); t.id = 'temoin'; t.textContent = 'Témoin gris sur gris';
        t.style.cssText = 'background:#8a8a8a;color:#9a9a9a;padding:10px;font-size:16px';
        document.getElementById('f-programme').appendChild(t); }""")
    g = mesurer(pg, "#temoin")
    dit("%s : témoin, la sonde attrape un gris sur gris" % nom, bool(g) and g["ratio"] < 1.5, g and round(g["ratio"], 2))


def navigateur(pages):
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        exemples = [(FP.EXEMPLES[0][1], "fr"), (FP.EXEMPLES[1][1], "en")]
        for chemin, langue in exemples:
            d = donnees(chemin.read_text(encoding="utf-8"))
            for larg, haut, mob in ((390, 844, True), (1440, 900, False)):
                nom = "%s · %d" % (langue, larg)
                print("\n· l'exemple %s" % nom)
                ctx, pg, erreurs, reseau = ouvrir_page(nav, chemin, larg, haut, mob)
                # ⚠️ textContent, pas innerText : le seuil est en capitales (text-transform),
                # et innerText rend « KOSSI » (la sonde mentait, leçon du 2026-10-16).
                pour = pg.evaluate("() => document.getElementById('s-pour').textContent")
                dit("%s : le seuil nomme le couple, le cachet porte ses initiales" % nom,
                    d["noms"][0] in pour and d["noms"][1] in pour
                    and pg.evaluate("() => document.getElementById('s-i1').textContent + document.getElementById('s-i2').textContent")
                    == d["noms"][0][0] + d["noms"][1][0])
                dit("%s : avant l'ouverture, le faire-part est caché" % nom,
                    pg.evaluate("() => getComputedStyle(document.getElementById('fp')).visibility") == "hidden")
                pg.click("#btn-ouvrir")
                pg.wait_for_timeout(1400)
                dit("%s : on brise le cachet, le carton sort, le focus suit" % nom,
                    pg.evaluate("() => document.getElementById('seuil').classList.contains('parti')"
                                " && document.getElementById('fp').classList.contains('ouvert')"
                                " && document.activeElement.id === 'f-noms'"))
                attendu = (instant(d) - datetime.datetime.now(datetime.timezone.utc)).total_seconds() // 86400
                jours = int(pg.inner_text("#c-j"))
                dit("%s : le compte vise le jour J à l'heure du lieu (%d jours)" % (nom, jours), abs(jours - attendu) <= 0, (jours, attendu))
                cartes = pg.evaluate("() => [...document.querySelectorAll('#f-prog li')].map(li => [li.querySelector('.lieu').textContent,"
                                     " (li.querySelector('a') || {}).href || ''])")
                dit("%s : chaque moment du programme a sa carte (%d)" % (nom, len(cartes)),
                    len(cartes) == len(d["programme"]) and all(FP.CARTE.match(h) and urllib.parse.quote(l.split(",")[0]) in h
                                                               for l, h in cartes), cartes[:1])
                # La langue : aucun mot de l'autre langue dans ce qui se LIT à l'écran.
                autre = (["Touchez", "Une invitation de", "Serez-vous", "Voir sur la carte", "La journée", "Je serai là",
                          "jours", "Votre prénom", "Comment s'habiller", "Le grand jour"] if langue == "en" else
                         ["Touch the seal", "An invitation from", "Will you be there", "See on the map", "The day",
                          "I'll be there", "days", "Your name", "What to wear", "The big day"])
                vu = pg.evaluate("() => document.body.innerText")
                dit("%s : rien de l'autre langue à l'écran" % nom, not [m for m in autre if m in vu], [m for m in autre if m in vu])
                pg.click("#r-oui")
                dit("%s : l'exemple n'envoie rien, il explique" % nom,
                    pg.get_attribute("#r-oui", "href") == "#" and len(pg.inner_text("#r-note")) > 20)
                iw = pg.evaluate("() => Math.max(innerWidth, document.documentElement.scrollWidth)")
                dit("%s : rien ne déborde (aucun dézoom)" % nom, iw <= larg, iw)
                petites = pg.evaluate("""() => [...document.querySelectorAll('a, button, input')]
                    .filter(e => e.offsetParent !== null && !e.closest('p') && !e.closest('[hidden]'))
                    .map(e => { const r = e.getBoundingClientRect(); return [e.id || e.className, Math.round(r.width), Math.round(r.height)]; })
                    .filter(x => x[2] < 44 || x[1] < 44)""")
                dit("%s : aucune cible sous 44 px" % nom, not petites, petites[:4])
                pg.evaluate("() => scrollTo(0, document.documentElement.scrollHeight)")
                pg.wait_for_timeout(1900)
                pg.wait_for_timeout(1200)   # la pluie (2,6 s) est partie
                caches = pg.evaluate("() => [...document.querySelectorAll('.rv:not([hidden]), .prog li')].filter(e =>"
                                     " parseFloat(getComputedStyle(e).opacity) < .99).length")
                dit("%s : toutes les sections se sont révélées" % nom, caches == 0, caches)
                contraste(pg, nom)
                dit("%s : aucune requête réseau" % nom, not reseau, reseau[:3])
                dit("%s : aucune erreur JavaScript" % nom, not erreurs, erreurs[:2])
                ctx.close()

        # Un vrai couple : les deux réponses vers SON WhatsApp, prénom, nombre, date.
        print("\n· un vrai couple")
        vrai = pages["vrai"]
        d = donnees(vrai.read_text(encoding="utf-8"))
        ctx, pg, erreurs, reseau = ouvrir_page(nav, vrai)
        pg.click("#btn-ouvrir")
        pg.wait_for_timeout(1400)
        pg.fill("#r-nom", "Sèna")
        pg.click("#r-plus")
        pg.click("#r-plus")
        oui = urllib.parse.unquote(pg.get_attribute("#r-oui", "href") or "")
        non = urllib.parse.unquote(pg.get_attribute("#r-non", "href") or "")
        dit("« Je serai là » écrit aux mariés : prénom, nombre et date",
            oui.startswith("https://wa.me/%s?text=" % d["whatsapp"]) and "Sèna" in oui and " 3 " in oui
            and "12 décembre 2026" in oui and "Kossi et Afiwa" in oui, oui[:140])
        dit("« Je ne pourrai pas venir » aussi, et dit qu'on ne vient pas",
            non.startswith("https://wa.me/%s?text=" % d["whatsapp"]) and "Sèna" in non and "pas venir" in non, non[:120])
        dit("vrai couple : aucune requête réseau, aucune erreur", not reseau and not erreurs, (reseau[:2], erreurs[:2]))
        ctx.close()

        # Le piège : le mot qui contient </script> s'affiche tel quel, rien ne s'exécute.
        ctx, pg, erreurs, reseau = ouvrir_page(nav, pages["piege"])
        pg.click("#btn-ouvrir")
        pg.wait_for_timeout(1300)
        mot = pg.evaluate("() => document.getElementById('f-mot-t').textContent")
        dit("témoin : le mot piégé s'affiche tel quel, aucun script ne s'exécute",
            "</script><script>window.__pirate=1</script>" in mot and not pg.evaluate("() => window.__pirate") and not erreurs,
            (mot[:60], erreurs[:1]))
        ctx.close()

        # Le jour J, puis le lendemain : on rebâtit la page avec d'autres dates.
        for cas, date, heure, attendu in (("le jour même", datetime.date.today().isoformat(), "00:00", "#f-jourj"),
                                          ("après le mariage", "2020-01-04", "10:00", "#f-merci")):
            t = vrai.read_text(encoding="utf-8")
            t = t.replace('"date":"%s"' % d["date"], '"date":"%s"' % date, 1).replace('"heure":"%s"' % d["heure"], '"heure":"%s"' % heure, 1)
            p = vrai.parent / ("cas-%s.html" % ("j" if "jour" in cas else "apres"))
            p.write_text(t, encoding="utf-8")
            ctx, pg, erreurs, reseau = ouvrir_page(nav, p)
            pg.click("#btn-ouvrir")
            pg.wait_for_timeout(1300)
            dit("%s : %s paraît, plus de réponse à donner" % (cas, attendu),
                pg.is_visible(attendu) and not pg.is_visible("#f-reponse"))
            ctx.close()

        # Mouvement réduit : tout est là tout de suite.
        ctx, pg, erreurs, reseau = ouvrir_page(nav, FP.EXEMPLES[0][1], doux=True)
        pg.click("#btn-ouvrir")
        pg.wait_for_timeout(300)
        caches = pg.evaluate("() => [...document.querySelectorAll('.rv:not([hidden]), .prog li, .ecrit')].filter(e =>"
                             " parseFloat(getComputedStyle(e).opacity) < .99 || getComputedStyle(e).clipPath.startsWith('inset(0px 100%')).length")
        dit("mouvement réduit : tout est visible dès l'ouverture", caches == 0, caches)
        ctx.close()
        nav.close()


def main():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="fp-qc-"))
    try:
        pages = generateur(tmp)
        navigateur(pages)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d contrôles verts, %d en échec" % (len(verts), len(rouges)))
    for n, d in rouges:
        print("  x %s %s" % (n, d))
    return 1 if rouges else 0


if __name__ == "__main__":
    sys.exit(main())

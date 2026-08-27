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

# ⚠️ La console de Windows écrit en cp1252 : un simple « ≥ » dans un libellé
#    faisait planter le contrôle APRÈS l'avoir réussi. On écrit en UTF-8.
for _f in (sys.stdout, sys.stderr):
    try: _f.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
from playwright.sync_api import sync_playwright
from PIL import Image

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experience", "out")
RACINE = os.path.normpath(RACINE)
VUES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_vues")
# ⚠️ Ce chemin n'existe QUE sur la machine du nuage. Sur un poste Windows,
#    Playwright trouve son navigateur tout seul : on ne lui impose rien.
import os as _os
_C = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
CHROME = _C if _os.path.exists(_C) else None

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


def _carte_src():
    src = os.path.join(RACINE, "..", "data", "carte.ts")
    return io.open(os.path.normpath(src), encoding="utf-8").read()


def plats_attendus():
    """Compte les plats dans `experience/data/carte.ts`, sans les retaper."""
    return _carte_src().count("      { n: ")


def sauces_attendues():
    """Compte les sauces, qui sont TOUTES au héros depuis le 2026-08-26.

    ⚠️ Lu dans les données, jamais recopié : le jour où la maison ajoute une
    sauce, ce contrôle doit la réclamer au héros tout seul.
    """
    txt = _carte_src()
    i = txt.index('id: "sauces"')
    j = txt.index('id: "petitdej"')
    return txt.count("      { n: ", i, j)


def rgb(txt):
    """« rgb(29, 26, 23) » ou « rgba(…) » → (29, 26, 23). None si transparent."""
    n = [float(v) for v in txt[txt.index("(") + 1:txt.index(")")].split(",")]
    if len(n) > 3 and n[3] < 0.99:
        return None
    return tuple(int(v) for v in n[:3])


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
        nav = p.chromium.launch(**({'executable_path': CHROME} if CHROME else {}))

        for nom, largeur, hauteur in [("mobile", 390, 844), ("bureau", 1440, 900)]:
            pg = nav.new_page(viewport={"width": largeur, "height": hauteur},
                              device_scale_factor=2)
            erreurs, mauvais = [], []
            pg.on("console", lambda m: erreurs.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: erreurs.append(str(e)))
            pg.on("response",
                  lambda r: mauvais.append("%d %s" % (r.status, r.url)) if r.status >= 400 else None)

            pg.goto("http://127.0.0.1:%d/" % port, wait_until="networkidle", timeout=60000)
            # ⚠️ « networkidle » ne dit pas que la carte est montée : le 19/08 le
            #    contrôle a planté sur un `getElementById` qui renvoyait null,
            #    alors que la rubrique était bien dans la page. On ATTEND l'élément
            #    au lieu de parier sur un délai fixe (un poste lent perd le pari).
            pg.wait_for_selector("#cat-petitdej", state="attached", timeout=60000)
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

            # ⚠️ CE CONTROLE PLANTAIT SUR UN `null.click()` LE 2026-08-26, le jour
            #    ou le dernier plat a recu sa photo. Il cherchait « un plat sans
            #    image » pour ouvrir sa fiche, et il n'y en a plus AUCUN sur les 52.
            #    Un controle qui plante ne protege plus rien : il doit dire qu'il
            #    n'a plus de sujet, pas s'arreter au milieu de la suite.
            # ⚠️ ET SURTOUT : DEUX CHOSES SANS RAPPORT etaient accrochees au meme
            #    clic. L'ardoise est un cas particulier qui peut disparaitre ;
            #    l'ACCOMPAGNEMENT OBLIGATOIRE est une regle metier valable pour
            #    tout plat, et une commande qui part sans lui arrive incomplete en
            #    cuisine. En laissant les deux ensemble, la seconde serait morte
            #    avec la premiere, sans un mot. On les separe : a defaut d'ardoise,
            #    on ouvre une SAUCE, categorie qui exige toujours un accompagnement.
            vise = pg.evaluate("""() => {
                const tous = [...document.querySelectorAll(".ct-item")];
                const sans = tous.find(x => !x.querySelector("img"));
                if (sans) { sans.click(); return "ardoise"; }
                const sauce = document.querySelector("#cat-sauces .ct-item");
                if (sauce) { sauce.click(); return "sauce"; }
                if (tous[0]) { tous[0].click(); return "premier plat"; }
                return null; }""")
            pg.wait_for_timeout(900)
            fiche = pg.evaluate("""() => {
                const d = document.querySelector('[role=dialog][aria-label^="Commander"]');
                if (!d) return null;
                const b = d.querySelector('button.flex-1');
                const acc = [...d.querySelectorAll('p')]
                    .some(p => /Accompagnement/.test(p.textContent || ''));
                return { titre: d.querySelector('h3')?.textContent,
                         bouton: b ? b.textContent.trim() : null,
                         bloque: b ? b.disabled : null,
                         demandeAcc: acc,
                         img: !!d.querySelector('img') }; }""")
            dire(fiche is not None,
                 "[%s] la fiche s'ouvre (%s)" % (nom, vise or "aucun plat a ouvrir"))
            if fiche:
                if vise == "ardoise":
                    dire(not fiche["img"],
                         "[%s] la fiche n'appelle aucune image : ardoise « %s »"
                         % (nom, fiche["titre"]))
                else:
                    dire(True, "[%s] plus aucune ardoise au menu : les 52 plats ont leur photo,\n       le controle de la fiche sans image n'a plus de sujet" % nom)
                # ⚠️ L'ACCOMPAGNEMENT EST OBLIGATOIRE quand la catégorie en propose.
                # Une commande sans accompagnement arrive incomplète en cuisine.
                if fiche["demandeAcc"]:
                    dire(fiche["bloque"] is True,
                         "[%s] sans accompagnement, la commande est bloquée : « %s »"
                         % (nom, fiche["bouton"]))
                    pg.evaluate("""() => {
                        const d = document.querySelector('[role=dialog][aria-label^="Commander"]');
                        const t = [...d.querySelectorAll('p')]
                            .find(p => /Accompagnement/.test(p.textContent || ''));
                        t.parentElement.querySelector('button').click(); }""")
                    pg.wait_for_timeout(300)
                    fiche = pg.evaluate("""() => {
                        const d = document.querySelector('[role=dialog][aria-label^="Commander"]');
                        const b = d.querySelector('button.flex-1');
                        return { bouton: b.textContent.trim(), bloque: b.disabled }; }""")
                dire(bool(fiche["bouton"]) and not fiche["bloque"],
                     "[%s] le bouton de commande est là : %s" % (nom, fiche["bouton"]))

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

        # ══ LE HÉROS (refonte du 2026-08-26) ═══════════════════════════════
        # Trois demandes de Mongazi, trois familles de contrôles : TOUTES les
        # sauces, ça avance TOUT SEUL et vite, on COMMANDE depuis là.
        attendues = sauces_attendues()
        for nom, largeur, hauteur in [("mobile", 390, 844), ("bureau", 1440, 900)]:
            pg = nav.new_page(viewport={"width": largeur, "height": hauteur},
                              device_scale_factor=2)
            bugs = []
            pg.on("pageerror", lambda e: bugs.append(str(e)))
            pg.goto("http://127.0.0.1:%d/" % port, wait_until="networkidle", timeout=60000)
            pg.wait_for_selector("[data-sauce]", timeout=60000)

            # ── 1. toutes les sauces sont là ──────────────────────────────
            n = pg.evaluate(
                "document.querySelectorAll('.swiper-slide button[aria-label]').length")
            dire(n == attendues,
                 "[héros %s] %d sauces au carrousel (la carte en compte %d)"
                 % (nom, n, attendues))

            # ── 2. elles ne sont pas TOUTES chargées d'un coup ────────────
            # ⚠️ Les quatorze découpes pèsent plus de 2 Mo. C'est le premier
            #    écran : on n'en monte qu'une poignée.
            img = pg.evaluate("document.querySelectorAll('.scene-plat img').length")
            dire(img <= 5, "[héros %s] %d assiettes chargées au départ, pas %d"
                 % (nom, img, attendues))

            # ── 3. ÇA AVANCE TOUT SEUL, et vite ───────────────────────────
            # ⚠️ LE TÉMOIN D'ABORD. Un contrôle de pause qui n'a pas prouvé
            #    que le mécanisme tourne passe aussi quand le mécanisme est
            #    MORT. On prouve donc le mouvement avant de prouver l'arrêt.
            a = pg.get_attribute("[data-sauce]", "data-sauce")
            pg.wait_for_timeout(4200)      # une sauce toutes les 2,8 s
            b = pg.get_attribute("[data-sauce]", "data-sauce")
            dire(a != b, "[héros %s] la scène avance seule : sauce %s → %s en 4,2 s"
                 % (nom, a, b))

            # ── 3 bis. LE BOUTON QUI PREND LA COMMANDE EST-IL VISIBLE ? ───
            # ⛔ TROUVÉ SUR UNE CAPTURE, PAS PAR UN CONTRÔLE, et c'est la
            #    leçon : `clearProps: "all"` ne retire pas « ce que GSAP a
            #    posé », il VIDE l'attribut `style`. Le bouton, dont la
            #    couleur était en style en ligne, finissait en texte crème sur
            #    fond transparent, au-dessus d'une carte de verre claire :
            #    **1,1:1**, invisible. ⚠️ Le défaut est ANTÉRIEUR à la refonte
            #    du héros — l'ancien bouton vert « Commander sur WhatsApp »
            #    avait exactement le même sort, sur le site en ligne.
            b = pg.evaluate("""() => {
                const e = [...document.querySelectorAll('button')]
                    .find(x => /Ajouter au panier/.test(x.textContent || ''));
                if (!e) return null;
                const s = getComputedStyle(e);
                return { fond: s.backgroundColor, texte: s.color,
                         opacite: parseFloat(s.opacity) }; }""")
            dire(b is not None, "[héros %s] le bouton « Ajouter au panier » existe" % nom)
            if b:
                fond, texte = rgb(b["fond"]), rgb(b["texte"])
                dire(fond is not None,
                     "[héros %s] son fond est opaque : %s" % (nom, b["fond"]))
                if fond and texte:
                    r = contraste(texte, fond)
                    dire(r >= 4.5, "[héros %s] on lit « Ajouter au panier » : %.1f:1"
                         % (nom, r))
                # ⚠️ ON ÉCHANTILLONNE, ON NE PHOTOGRAPHIE PAS. Le héros change
                #    de sauce en permanence et le bouton traverse un fondu de
                #    ~750 ms à chaque passage : un relevé unique tombait dedans
                #    environ une fois sur quatre et déclarait le bouton
                #    invisible. Mesuré le 2026-08-26, 63 relevés en 16 s :
                #    min 0,00, MAX 1,00, médiane 1,00, pleine opacité 71 % du
                #    temps. Le site allait bien, le contrôle mentait — et il
                #    mentait déjà sur `main`, les deux rouges y étaient.
                #    Ce qu'on veut savoir tient en une phrase : le bouton
                #    DEVIENT-IL pleinement visible ? On regarde donc le maximum
                #    sur un cycle complet. Le défaut d'origine
                #    (`clearProps:"all"` qui vidait le style et laissait le
                #    bouton transparent POUR TOUJOURS) reste attrapé : dans ce
                #    cas-là le maximum ne monte jamais.
                ops = []
                for _ in range(28):
                    o = pg.evaluate("""() => {
                        const e = [...document.querySelectorAll("button")]
                            .find(x => /Ajouter au panier/.test(x.textContent || ""));
                        return e ? parseFloat(getComputedStyle(e).opacity) : null; }""")
                    if o is not None:
                        ops.append(o)
                    pg.wait_for_timeout(250)
                haut = max(ops) if ops else 0
                dire(haut >= 0.99,
                     "[héros %s] il atteint la pleine opacité : %.2f (max sur %d relevés)"
                     % (nom, haut, len(ops)))

            # ── 3 ter. LA DEUXIÈME LIGNE DU TITRE EST LA PLUS GROSSE ──────
            # ⚠️ C'est LA signature du héros : une ligne fine et espacée, puis
            #    la même police en très gras juste dessous. Le corps de la 2e
            #    ligne est calculé par sauce (donc en style en ligne) : le même
            #    `clearProps: "all"` l'effaçait et la ligne qu'on doit lire
            #    ressortait plus PETITE que l'autre.
            t = pg.evaluate("""() => {
                const a = document.querySelector('.dt-l1');
                const b = document.querySelector('.dt-l2');
                if (!a || !b) return null;
                return { l1: parseFloat(getComputedStyle(a).fontSize),
                         l2: parseFloat(getComputedStyle(b).fontSize) }; }""")
            dire(t is not None and t["l2"] > t["l1"],
                 "[héros %s] la 2e ligne du titre est la plus grosse : %s"
                 % (nom, "" if not t else "%.0f px contre %.0f" % (t["l2"], t["l1"])))

            # ── 3 ter bis. L'ASSIETTE NE SORT PAS DE SA BOÎTE ─────────────
            # ⛔ Vu sur capture : l'ardoise ronde débordait de 100 px sous sa
            #    boîte en 390 px et se posait sur l'accroche et sur le titre.
            #    `absolute inset-0` fixe DÉJÀ les deux dimensions, donc
            #    `aspect-ratio` est ignoré — et la boîte de l'assiette n'est
            #    carrée que sur grand écran.
            # ⚠️ ET ON VA LA CHERCHER. Mesurer « l'ardoise » sur la sauce
            #    courante, c'est ne rien mesurer huit fois sur quatorze : il
            #    n'y en a pas là. On saute donc sur la première sauce qui n'a
            #    pas de photo. Le jour où la maison les aura toutes envoyées,
            #    il n'y en aura plus, et le contrôle le DIT au lieu de passer
            #    en silence.
            k = pg.evaluate("""() => [...document.querySelectorAll(
                '.swiper-slide button[aria-label]')].findIndex(b => !b.querySelector('img'))""")
            if k < 0:
                dire(True, "[héros %s] plus aucune ardoise : toutes les sauces ont leur photo" % nom)
            else:
                pg.evaluate("""(k) => document
                    .querySelectorAll('.swiper-slide button[aria-label]')[k].click()""", k)
                pg.wait_for_timeout(900)
                # ⚠️ ON MESURE L'ENFANT CONTRE SON PROPRE CONTENEUR, PAS
                #    CONTRE `.scene-plat`. Les quatorze assiettes sont
                #    DÉPLACÉES par GSAP (74 % de large, 66 % de haut) : les
                #    comparer à la boîte commune, c'est mesurer un
                #    déplacement, pas un débordement. Le premier jet annonçait
                #    « 170 px » sur une ardoise qui tient parfaitement — il
                #    avait attrapé la voisine, garée hors champ.
                #    Enfant et conteneur subissent la MÊME transformation :
                #    leur différence est du pur débordement de mise en page.
                # ⚠️ ET ON LES MESURE TOUTES. Chercher « celle qui est à
                #    l'écran » demandait de deviner laquelle : la scène avance
                #    toute seule, et entre le clic et la mesure elle avait
                #    parfois changé de sauce — le contrôle renvoyait `None`
                #    sur un site sain. Puisque la comparaison enfant/parent est
                #    insensible aux transformations, les huit ardoises se
                #    mesurent aussi bien garées qu'à l'écran.
                debord = pg.evaluate("""() => {
                    const l = [...document.querySelectorAll('.ardoise-plat')];
                    if (!l.length) return null;
                    return Math.round(Math.max(...l.map(e => {
                        const q = e.getBoundingClientRect();
                        const r = e.parentElement.getBoundingClientRect();
                        return Math.max(q.bottom - r.bottom, r.top - q.top,
                                        q.right - r.right, r.left - q.left);
                    }))); }""")
                dire(debord is not None and debord <= 1,
                     "[héros %s] l'ardoise tient dans sa boîte : %s px de débordement"
                     % (nom, debord))

            # ── 3 quater. LES POINTS NE SE POSENT PAS SUR LE TEXTE ────────
            # ⚠️ Sur téléphone la scène est une colonne pleine largeur : la
            #    pile de points tombait sur l'accroche et sur le titre. Un
            #    instrument flottant ne recouvre jamais du texte.
            pts = pg.evaluate("""() => {
                const d = [...document.querySelectorAll('[aria-label^="Aller à la sauce"]')];
                if (!d.length) return { cache: true, cognes: [] };
                const b = d[0].parentElement.getBoundingClientRect();
                // ⚠️ `display: none` laisse les boutons dans le DOM. Sans ce
                //    test, le contrôle passait en annonçant une pile visible.
                if (!b.width || !b.height) return { cache: true, cognes: [] };
                const cognes = [];
                for (const s of ['.scene-txt', '.scene-carte']) {
                    const e = document.querySelector(s);
                    if (!e) continue;
                    const r = e.getBoundingClientRect();
                    const h = Math.min(b.bottom, r.bottom) - Math.max(b.top, r.top);
                    const w = Math.min(b.right, r.right) - Math.max(b.left, r.left);
                    if (h > 1 && w > 1) cognes.push(s + ' sur ' + Math.round(w) + ' px');
                }
                return { cache: false, cognes }; }""")
            dire(pts["cache"] or not pts["cognes"],
                 "[héros %s] les points ne recouvrent aucun texte%s"
                 % (nom, " (masqués sur téléphone)" if pts["cache"]
                    else ("" if not pts["cognes"] else " → %s" % pts["cognes"])))

            # ── 4. on commande DEPUIS le héros ────────────────────────────
            pg.evaluate("""() => [...document.querySelectorAll('button')]
                .find(b => /Ajouter au panier/.test(b.textContent || '')).click()""")
            pg.wait_for_timeout(700)
            ouverte = pg.evaluate(
                """() => !!document.querySelector('[role=dialog][aria-label^="Commander"]')""")
            dire(ouverte, "[héros %s] « Ajouter au panier » ouvre la fiche de commande" % nom)

            # ── 5. …et la scène s'arrête DERRIÈRE la fiche ────────────────
            # ⚠️ Sans ça, la sauce change pendant qu'on choisit son
            #    accompagnement, et on ajoute au panier autre chose que ce
            #    qu'on regardait.
            c = pg.get_attribute("[data-sauce]", "data-sauce")
            pg.wait_for_timeout(4200)
            d = pg.get_attribute("[data-sauce]", "data-sauce")
            dire(c == d, "[héros %s] la scène ne tourne plus derrière la fiche (sauce %s)"
                 % (nom, c))

            # ── 6. la sauce tombe bien dans LE panier ─────────────────────
            titre = pg.evaluate(
                """() => document.querySelector('[role=dialog][aria-label^="Commander"] h3').textContent""")
            pg.evaluate("""() => {
                const d = document.querySelector('[role=dialog][aria-label^="Commander"]');
                const t = [...d.querySelectorAll('p')]
                    .find(p => /Accompagnement/.test(p.textContent || ''));
                if (t) t.parentElement.querySelector('button').click(); }""")
            pg.wait_for_timeout(250)
            pg.evaluate("""() => document
                .querySelector('[role=dialog][aria-label^="Commander"] button.flex-1').click()""")
            pg.wait_for_timeout(600)
            barre = pg.evaluate("""() => {
                const a = [...document.querySelectorAll('a')]
                    .find(x => /Envoyer la commande/.test(x.textContent || ''));
                if (!a) return null;
                const r = a.getBoundingClientRect();
                return { visible: r.width > 0 && r.bottom <= innerHeight + 1,
                         texte: a.parentElement.innerText }; }""")
            dire(barre is not None and barre["visible"],
                 "[héros %s] « %s » ajoutée depuis le héros : la barre du panier s'affiche"
                 % (nom, titre))
            if barre:
                dire("1 article" in barre["texte"],
                     "[héros %s] le panier compte bien un article" % nom)

            # ── 6 bis. LA BARRE DU PANIER NE RECOUVRE RIEN ────────────────
            # ⚠️ Elle est FIXE et elle apparaît maintenant pendant qu'on est
            #    encore sur la scène : elle se posait par-dessus la barre du
            #    bas et par-dessus le carrousel des sauces. Un instrument
            #    flottant ne recouvre jamais un autre instrument.
            chevauche = pg.evaluate("""() => {
                const bar = [...document.querySelectorAll('a')]
                    .find(x => /Envoyer la commande/.test(x.textContent || ''));
                if (!bar) return null;
                const b = bar.closest('div.fixed').getBoundingClientRect();
                const cognes = [];
                for (const s of ['.nav-bas', '.rail-bas']) {
                    const e = document.querySelector(s);
                    if (!e) continue;
                    const r = e.getBoundingClientRect();
                    const h = Math.min(b.bottom, r.bottom) - Math.max(b.top, r.top);
                    const w = Math.min(b.right, r.right) - Math.max(b.left, r.left);
                    if (h > 1 && w > 1) cognes.push(s + ' sur ' + Math.round(h) + ' px');
                }
                return cognes; }""")
            dire(chevauche is not None and not chevauche,
                 "[héros %s] la barre du panier ne recouvre ni la nav ni le carrousel%s"
                 % (nom, "" if not chevauche else " → %s" % chevauche))

            deb = pg.evaluate(
                "document.documentElement.scrollWidth - document.documentElement.clientWidth")
            dire(deb <= 0, "[héros %s] débordement horizontal, panier plein : %d px" % (nom, deb))
            dire(not bugs, "[héros %s] 0 erreur JS%s"
                 % (nom, "" if not bugs else " → %s" % bugs[:2]))
            pg.close()

            # ── 7. aucun titre de sauce ne déborde de sa colonne ──────────
            # ⚠️ « SAUCE TÊTE DE MOUTON » en très gras traverse la colonne du
            #    titre, qui ne fait que 366 px sur un écran de 1440.
            # ⚠️ ET ON MESURE SOUS `prefers-reduced-motion`. Sans ça, la scène
            #    avance toute seule entre le clic et la mesure : on croit
            #    mesurer la 7e sauce et on mesure la 8e. Un contrôle qui vise à
            #    côté une fois sur cinq est pire qu'un contrôle absent.
            pg = nav.new_page(viewport={"width": largeur, "height": hauteur},
                              reduced_motion="reduce")
            pg.goto("http://127.0.0.1:%d/" % port, wait_until="networkidle", timeout=60000)
            pg.wait_for_selector("[data-sauce]", timeout=60000)
            pire, pire_nom = -99.0, ""
            for k in range(attendues):
                pg.evaluate("""(k) => document
                    .querySelectorAll('.swiper-slide button[aria-label]')[k].click()""", k)
                # ⚠️ ON NE MESURE PAS UNE BOÎTE QUI EST EN TRAIN DE GLISSER.
                #    Premier jet : `getBoundingClientRect().right` comparé au
                #    parent, 260 ms après le clic. Le titre entre en scène par
                #    un `fromTo({x: 50})` de 0,7 s (GSAP ignore
                #    `prefers-reduced-motion`, seul notre code le lit) : on
                #    mesurait le X de l'animation et le contrôle annonçait
                #    « KRINKRIN dépasse de 36 px » sur un titre parfaitement
                #    posé. `scrollWidth - clientWidth` ne connaît pas les
                #    transformations, et il voit aussi le mot qui ne peut pas
                #    aller à la ligne — c'est exactement le défaut cherché.
                pg.wait_for_timeout(1150)
                m = pg.evaluate("""() => {
                    const e = document.querySelector('.dt-l2');
                    if (!e) return null;
                    return { d: e.scrollWidth - e.clientWidth, t: e.textContent }; }""")
                if m and m["d"] > pire:
                    pire, pire_nom = m["d"], m["t"]
            dire(pire <= 1.0,
                 "[héros %s] le titre le plus large est « %s », il dépasse de %.0f px"
                 % (nom, pire_nom, pire))
            pg.close()

        # ══ LA GLACE SE VEND À LA BOULE ════════════════════════════════════
        # ⚠️ Trois prix, pas deux. Le modèle ne connaissait que « Normal /
        #    Grand » : un troisième palier oublié, c'est la maison qui encaisse
        #    2 500 F de moins sans que personne le voie.
        pg = nav.new_page(viewport={"width": 1440, "height": 900})
        pg.goto("http://127.0.0.1:%d/" % port, wait_until="networkidle", timeout=60000)
        pg.wait_for_selector("#cat-dessert", state="attached", timeout=60000)
        pg.evaluate("""() => { const e = document.getElementById('cat-dessert');
            window.__lenis ? window.__lenis.scrollTo(e, { immediate: true }) : e.scrollIntoView(); }""")
        pg.wait_for_timeout(1500)
        pg.evaluate("""() => [...document.querySelectorAll('#cat-dessert .ct-item')]
            .find(a => /Glace/.test(a.innerText)).click()""")
        pg.wait_for_timeout(800)
        crans = pg.evaluate("""() => {
            const d = document.querySelector('[role=dialog][aria-label^="Commander"]');
            const t = [...d.querySelectorAll('p')].find(p => /^Taille$/.test(p.textContent.trim()));
            return t ? [...t.parentElement.querySelectorAll('button')].map(b => b.textContent.trim()) : []; }""")
        dire(len(crans) == 3, "[glace] %d paliers dans la fiche : %s" % (len(crans), crans))
        # ⚠️ Les prix sont écrits avec des espaces INSÉCABLES (un prix ne se
        #    coupe pas en fin de ligne) : on compare sans aucune espace, sinon
        #    le contrôle échoue sur un site parfaitement juste.
        def serrer(s):
            return "".join(c for c in s if not c.isspace() and c not in "\u00a0\u202f")
        for cran in ["1 boule · 1 000 F", "2 boules · 1 500 F", "3 boules · 2 500 F"]:
            dire(any(serrer(c) == serrer(cran) for c in crans),
                 "[glace] le palier « %s » est là" % cran)
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

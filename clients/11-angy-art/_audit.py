# -*- coding: utf-8 -*-
"""
AUDIT D'ANGY ART — ce que les 150 contrôles ne regardent pas.

    python _audit.py            # le dossier du disque
    python _audit.py --live     # le site en ligne

⚠️ CE N'EST PAS UN DEUXIÈME QC. `_qc.py` vérifie que le site est juste ; il
était vert à 150 pendant que la page tournait à quinze images par seconde et
que sa vignette de partage pesait un demi-méga en PNG. Ce fichier regarde
ailleurs : le poids du premier écran, la vignette de partage, la modale au
clavier, les cibles au doigt, les ancres mortes, les identifiants en double,
et le décalage de mise en page.
"""
import argparse
import functools
import http.server
import io
import json
import os
import re
import socketserver
import sys
import threading

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
LIVE = "https://angy-art.pages.dev/"

ok, ko = [], []


def dire(bon, txt):
    (ok if bon else ko).append(txt)
    print(("  vert  " if bon else "  ROUGE ") + txt)


class Serveur(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def sans_navigateur():
    """Ce qui se lit dans les fichiers, sans rien lancer."""
    html = io.open(os.path.join(ICI, "index.html"), encoding="utf-8").read()

    # ── la vignette de partage ───────────────────────────────────────
    m = re.search(r'property="og:image"\s+content="([^"]+)"', html)
    dire(bool(m), "og:image declaree")
    if m:
        rel = m.group(1).split("?")[0].split("angy-art.pages.dev/")[-1]
        f = os.path.join(ICI, rel.replace("/", os.sep))
        existe = os.path.exists(f)
        dire(existe, "og:image presente sur le disque : %s" % rel)
        if existe:
            tete = io.open(f, "rb").read(3)
            # ⚠️ LA RÈGLE DE LA MAISON EST « EN JPEG ». Un PNG d'aperçu part
            #    lourd et certains lecteurs de lien l'abandonnent : la vignette
            #    WhatsApp est la première impression au Bénin, et c'est le
            #    défaut le plus cher parce qu'il est INVISIBLE depuis le site.
            dire(tete == b"\xff\xd8\xff",
                 "og:image est un JPEG (elle est en %s)"
                 % ("JPEG" if tete == b"\xff\xd8\xff" else "PNG/autre"))
            ko_poids = os.path.getsize(f)
            dire(ko_poids < 300 * 1024,
                 "og:image pese %.0f Ko (viser moins de 300)" % (ko_poids / 1024))

    # ── les identifiants en double ───────────────────────────────────
    ids = re.findall(r'\sid="([^"]+)"', html)
    doubles = sorted({i for i in ids if ids.count(i) > 1})
    dire(not doubles, "aucun identifiant en double%s"
         % ("" if not doubles else " -> %s" % doubles[:5]))

    # ── les ancres mortes ────────────────────────────────────────────
    cibles = set(ids)
    morts = sorted({a for a in re.findall(r'href="#([^"]+)"', html)
                    if a and a not in cibles})
    dire(not morts, "aucune ancre morte%s" % ("" if not morts else " -> %s" % morts))

    # ── les images sans dimensions (donc a decalage) ─────────────────
    sans_dim = [t[:70] for t in re.findall(r"<img [^>]*>", html)
                if "width=" not in t or "height=" not in t]
    dire(not sans_dim, "toutes les images portent width et height%s"
         % ("" if not sans_dim else " -> %d sans" % len(sans_dim)))

    # ── ce qui ne doit jamais apparaitre sur un site publie ──────────
    for mot in ("à valider", "à confirmer", "lorem", "TODO", "photo à venir"):
        dire(mot.lower() not in html.lower(),
             "le mot « %s » n'est pas dans la page" % mot)


def avec_navigateur(url):
    with sync_playwright() as p:
        nav = p.chromium.launch()

        # ══ 1. LE PREMIER ÉCRAN : ce qu'on télécharge avant de voir ═══
        pg = nav.new_page(viewport={"width": 390, "height": 844})
        poids = {"total": 0, "images": 0}
        erreurs, mauvais = [], []
        pg.on("pageerror", lambda e: erreurs.append(str(e)))
        pg.on("console", lambda m: erreurs.append(m.text) if m.type == "error" else None)
        pg.on("response", lambda r: mauvais.append("%d %s" % (r.status, r.url))
              if r.status >= 400 else None)

        def compter(r):
            try:
                n = int(r.headers.get("content-length") or 0)
            except Exception:
                n = 0
            poids["total"] += n
            if (r.headers.get("content-type") or "").startswith("image"):
                poids["images"] += n

        # ⚠️⚠️ ON MESURE SUR UNE 3G, PAS SUR LOCALHOST, ET C'EST TOUT LE
        #    CONTRÔLE. En local la bande passante est infinie, et le seuil de
        #    `loading="lazy"` de Chrome grandit avec la vitesse de la
        #    connexion : la page semblait télécharger **1 920 Ko** avant le
        #    moindre défilement, dont les six photos du carrousel situées à
        #    3 500 px du haut. Sur une vraie 3G, les mêmes 3,8 secondes ne
        #    téléchargent que **794 Ko** et le carrousel ne bouge pas : le
        #    différé fonctionne. Le premier jet de ce contrôle a failli faire
        #    réécrire le carrousel pour un défaut qui n'existait pas.
        # ⚠️ ET ON COMPTE LE CHEMIN CRITIQUE, PAS « TOUT CE QUI EST ARRIVÉ
        #    EN NEUF SECONDES ». Le premier jet faisait la seconde chose : le
        #    même site donnait 210, 242 puis 753 Ko d'une mesure à l'autre,
        #    selon que le différé avait eu le temps de démarrer ou non. Un
        #    contrôle qui change d'avis à chaque exécution finit par ne plus
        #    être lu. Ce qui compte est ce que le visiteur DOIT attendre pour
        #    voir le premier écran : on arrête le compteur quand l'image du
        #    héros est décodée, et on somme ce qui a précédé.
        cdp = pg.context.new_cdp_session(pg)
        cdp.send("Network.enable")
        cdp.send("Network.emulateNetworkConditions", {
            "offline": False, "downloadThroughput": 1.6 * 1024 * 1024 / 8,
            "uploadThroughput": 400 * 1024 / 8, "latency": 300})
        pg.on("response", compter)
        pg.goto(url, wait_until="commit", timeout=180000)
        pg.wait_for_function(
            """() => { const i = document.querySelector('.hero img, .scene img');
                       return i && i.complete && i.naturalWidth > 0; }""",
            timeout=120000)
        critique = poids["total"]
        pg.wait_for_timeout(6000)
        dire(critique < 420 * 1024,
             "chemin critique sur 3G : %.0f Ko avant que le heros soit la "
             "(puis %.0f Ko de plus, differes)"
             % (critique / 1024, (poids["total"] - critique) / 1024))
        dire(not erreurs, "0 erreur JS%s" % ("" if not erreurs else " -> %s" % erreurs[:2]))
        dire(not mauvais, "0 reponse >= 400%s" % ("" if not mauvais else " -> %s" % mauvais[:3]))

        # ══ 2. LE DÉCALAGE DE MISE EN PAGE (CLS) ═════════════════════
        cls = pg.evaluate("""() => new Promise(res => {
            let s = 0;
            try {
              new PerformanceObserver(l => {
                for (const e of l.getEntries()) if (!e.hadRecentInput) s += e.value;
              }).observe({ type: 'layout-shift', buffered: true });
            } catch (e) {}
            setTimeout(() => res(Math.round(s * 1000) / 1000), 900); })""")
        dire(cls <= 0.1, "decalage de mise en page (CLS) : %.3f (seuil 0,1)" % cls)

        # ══ 3. LES CIBLES AU DOIGT ═══════════════════════════════════
        # ⚠️ On ne mesure QUE ce qui est visible : un bouton de menu replié a
        #    une boîte de zéro, ce n'est pas une cible trop petite.
        # ⚠️ « UNE BOÎTE DE ZÉRO » NE SUFFISAIT PAS. Un panneau fermé par
        #    `visibility:hidden` garde une boîte, et s'il se ferme en
        #    `scale(.96)` ses liens se mesurent 4 % plus petits : le contrôle a
        #    accusé « ÉCRIRE SUR WHATSAPP » de faire 42 px alors qu'il en fait
        #    44 une fois ouvert (2026-09-04). L'instrument mesurait sa propre
        #    animation, pas le site — même famille que le débordement mesuré
        #    sur un `transform` chez Au Braisé d'Or. `visibility` s'hérite,
        #    donc lire celle de l'élément suffit à écarter tout un panneau.
        # ⚠️ ET ON EXCLUT LES LIENS DANS UNE PHRASE. « Site conçu par NEBULA
        #    Agency, Cotonou » porte un lien de 89 × 15 px : c'est du texte
        #    courant, et la règle des 44 px l'exempte explicitement. Sans cette
        #    exception, le contrôle criait au loup sur un pied de page normal,
        #    et un contrôle qui crie au loup finit par ne plus être lu.
        petites = pg.evaluate("""() => {
            const dansUnePhrase = (e) => {
                const p = e.closest('p,li,blockquote,figcaption');
                if (!p) return false;
                // du texte autour du lien, donc une phrase et non une barre
                return (p.textContent || '').trim().length >
                       (e.textContent || '').trim().length + 12;
            };
            return [...document.querySelectorAll(
                'a[href],button,[role=button],input,select,summary')]
              .filter(e => getComputedStyle(e).visibility !== 'hidden')
              .filter(e => !dansUnePhrase(e))
              .map(e => { const r = e.getBoundingClientRect();
                          return { t: (e.getAttribute('aria-label') || e.textContent || '')
                                       .trim().slice(0, 34),
                                   w: Math.round(r.width), h: Math.round(r.height) }; })
              .filter(x => x.w > 0 && x.h > 0 && (x.w < 44 || x.h < 44)); }""")
        dire(len(petites) == 0, "toutes les cibles font 44 px ou plus%s"
             % ("" if not petites else " -> %s"
                % [("%s %dx%d" % (x["t"], x["w"], x["h"])) for x in petites[:5]]))
        # ══ 3 bis. LA BARRE DU HAUT EST-ELLE VRAIMENT OPAQUE ? ═══════
        # ⚠️ ON PHOTOGRAPHIE, ON NE LIT PAS LE CSS. Une bande de bord a le
        #    droit de recouvrir du texte — c'est la seule chose qui l'ait —
        #    mais seulement si l'on ne voit RIEN au travers. Elle était à 92 % :
        #    la phrase qui passait dessous restait lisible en filigrane.
        #    Le test : la même bande, à deux hauteurs de défilement où le
        #    contenu du dessous diffère. Opaque, les deux images sont
        #    identiques ; translucide, elles ne le sont pas.
        # ⚠️ SUR UNE PAGE NEUVE, SANS BRIDAGE, ET APRÈS LES POLICES. Le premier
        #    jet réutilisait la page bridée en 3G : entre les deux photos, la
        #    police du menu finissait de charger et le texte de la barre se
        #    redessinait. Le contrôle annonçait **233/255** sur une barre
        #    parfaitement opaque. Ce n'est pas le fond qu'il mesurait, c'est un
        #    changement de police.
        from PIL import Image, ImageChops, ImageStat
        import io as _io
        pg.close()
        pg = nav.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        pg.goto(url, wait_until="networkidle", timeout=90000)
        pg.evaluate("() => document.fonts.ready")
        pg.wait_for_timeout(3800)
        pg.evaluate("() => window.scrollTo(0, 900)")
        pg.wait_for_timeout(1500)
        barre = pg.query_selector(".nav")
        a = Image.open(_io.BytesIO(barre.screenshot())).convert("RGB")
        pg.evaluate("() => window.scrollTo(0, 2100)")
        pg.wait_for_timeout(1500)
        b = Image.open(_io.BytesIO(pg.query_selector(".nav").screenshot())).convert("RGB")
        if a.size == b.size:
            ecart = max(ImageStat.Stat(ImageChops.difference(a, b)).extrema[0])
            dire(ecart <= 4,
                 "la barre du haut est vraiment opaque : %d/255 d'ecart entre "
                 "deux fonds differents" % ecart)
        else:
            dire(False, "la barre change de taille entre deux hauteurs")
        pg.close()

        # ══ 4. LA MODALE DE DEMANDE, AU CLAVIER ══════════════════════
        # ⚠️ Cette modale EST le bon de commande. Si on ne peut pas la remplir
        #    au clavier, quelqu'un au lecteur d'ecran ne peut pas commander.
        pg = nav.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(url, wait_until="load", timeout=90000)
        pg.wait_for_timeout(3800)
        # ⚠️ ON VISE LE BOUTON QUI OUVRE VRAIMENT LA MODALE. Le premier jet
        #    prenait « le premier bouton dont le texte parle de demande » : il
        #    tombait sur un bouton qui fait DÉFILER vers une section, aucune
        #    modale ne s'ouvrait, et les deux contrôles suivants passaient dans
        #    le vide — « Échap referme la modale » était vrai parce qu'il n'y
        #    avait pas de modale. Un contrôle qui n'a rien testé doit le dire.
        ouvre = pg.evaluate("""() => {
            const b = document.querySelector('[data-modale]');
            if (!b) return null; b.click(); return true; }""")
        pg.wait_for_timeout(900)
        d = pg.evaluate("""() => {
            const m = document.querySelector('dialog[open]');
            if (!m) return null;
            const f = document.activeElement;
            return { vrai_dialog: true,
                     focus_dedans: m.contains(f),
                     focus_sur: (f.tagName || '') + '.' + (f.className || '').split(' ')[0],
                     fond_inert: !!document.querySelector('[inert]') ||
                                 document.body.classList.contains('fige') }; }""")
        dire(ouvre is not None, "un bouton ouvre la demande sur mesure")
        dire(d is not None, "c'est un vrai <dialog> ouvert")
        if d:
            dire(d["focus_dedans"],
                 "le focus entre dans la modale (il est sur %s)" % d["focus_sur"])
        # ⚠️ On ne teste la fermeture QUE si quelque chose s'était ouvert :
        #    sinon le contrôle se félicite de refermer le vide.
        if d:
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(400)
            dire(pg.evaluate("() => !document.querySelector('dialog[open]')"),
                 "Echap referme la modale")
        pg.close()
        nav.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()

    srv = None
    if args.live:
        url = LIVE
    else:
        h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ICI)
        srv = Serveur(("127.0.0.1", 0), h)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        url = "http://127.0.0.1:%d/" % srv.server_address[1]

    print("  source : %s\n" % url)
    sans_navigateur()
    print()
    avec_navigateur(url)
    if srv:
        srv.shutdown()

    print("\n  %d vert(s), %d rouge(s)" % (len(ok), len(ko)))
    if ko:
        print("  ROUGE :")
        for k in ko:
            print("    - " + k)
    return 1 if ko else 0


if __name__ == "__main__":
    sys.exit(main())

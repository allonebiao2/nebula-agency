# -*- coding: utf-8 -*-
"""Contrôle qualité de « Bénin mon pays ».

Ce que cette suite regarde et que l'oeil oublie :
  · le compteur de la jauge doit dire LE MÊME kilomètre que l'étiquette
  · aucun élément fixe ne doit se poser sur du texte
  · le contraste se mesure sur les PIXELS RENDUS, pas sur background-color
    (transparent au-dessus d'un motif, donc aveugle)
  · une section sautée par le menu doit quand même se révéler
  · zéro requête vers un tiers : la page doit s'ouvrir sans le monde
"""
import functools
import http.server
import io
import os
import socketserver
import sys
import threading

from PIL import Image
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
PORT = 8733
BASE = "http://127.0.0.1:%d/index.html" % PORT

STATIONS = ["station-0", "station-1", "station-2", "station-3",
            "station-4", "station-5", "station-6", "station-7"]
KM = [0, 6, 7, 18, 98, 430, 538, 617]

ok, ko = [], []


def v(cond, titre, detail=""):
    (ok if cond else ko).append(titre + ((" — " + str(detail)) if detail and not cond else ""))


def servir():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ICI)
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def entrer(pg):
    pg.goto(BASE, wait_until="load")
    pg.wait_for_timeout(1800)
    pg.click("#entrer")
    pg.wait_for_timeout(900)


def aller(pg, ident):
    pg.evaluate("""(id)=>{
      document.documentElement.style.scrollBehavior='auto';
      const e=document.getElementById(id);
      if(e) window.scrollTo(0, e.getBoundingClientRect().top + window.scrollY - 54);
    }""", ident)
    pg.wait_for_timeout(700)


# ─── contraste mesuré sur les pixels rendus ────────────────────────
def lum(c):
    def f(u):
        u /= 255.0
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def contraste(a, b):
    la, lb = lum(a), lum(b)
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


def fond_reel(pg, sel):
    """Photographie la zone du texte SANS le texte, et prend le décile le
    plus clair : c'est le pire cas pour du texte clair."""
    b = pg.evaluate("""(s)=>{const e=document.querySelector(s);
        if(!e) return null; const r=e.getBoundingClientRect();
        if(r.width<2||r.height<2) return null;
        return {x:r.x,y:r.y,w:r.width,h:r.height};}""", sel)
    if not b:
        return None
    pg.evaluate("""(s)=>{const e=document.querySelector(s); if(e) e.style.visibility='hidden';}""", sel)
    png = pg.screenshot(clip={"x": max(0, b["x"]), "y": max(0, b["y"]),
                              "width": max(2, min(b["w"], 1400)),
                              "height": max(2, min(b["h"], 400))})
    pg.evaluate("""(s)=>{const e=document.querySelector(s); if(e) e.style.visibility='';}""", sel)
    im = Image.open(io.BytesIO(png)).convert("RGB")
    px = list(im.getdata())
    px.sort(key=lum)
    return px[int(len(px) * 0.9)]


def couleur_texte(pg, sel):
    c = pg.evaluate("""(s)=>{const e=document.querySelector(s);
        return e? getComputedStyle(e).color : null;}""", sel)
    if not c:
        return None
    n = [int(x) for x in c.replace("rgba(", "").replace("rgb(", "").replace(")", "").split(",")[:3]]
    return tuple(n)


# ═══════════════════════════════════════════════════════════════════
def controler():
    with sync_playwright() as pw:
        nav = pw.chromium.launch()

        # ── PASSE 1 · PC 1440 ──────────────────────────────────────
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        erreurs, mauvaises, externes = [], [], []
        pg.on("pageerror", lambda e: erreurs.append(str(e)))
        pg.on("console", lambda m: erreurs.append(m.text) if m.type == "error" else None)
        pg.on("response", lambda r: mauvaises.append("%d %s" % (r.status, r.url)) if r.status >= 400 else None)
        pg.on("request", lambda r: externes.append(r.url)
              if not r.url.startswith("http://127.0.0.1") and not r.url.startswith("data:") else None)

        entrer(pg)

        v(not erreurs, "aucune erreur JavaScript", erreurs[:3])
        v(not mauvaises, "aucune réponse >= 400", mauvaises[:3])
        v(not externes, "aucune requête vers un tiers (page autonome)", externes[:3])

        # 1 · les huit stations existent et sont dans l'ordre
        n = pg.eval_on_selector_all(".st", "e=>e.length")
        v(n == 8, "huit stations", n)
        kms = pg.eval_on_selector_all(".st", "e=>e.map(x=>+x.dataset.km)")
        v(kms == KM, "kilomètres dans l'ordre réel du sud au nord", kms)
        verbes = pg.eval_on_selector_all(".st", "e=>e.map(x=>x.dataset.verbe)")
        v(len(set(verbes)) == 8, "un verbe DIFFÉRENT par lieu", verbes)
        motifs = pg.eval_on_selector_all(".st", "e=>e.map(x=>x.dataset.motif)")
        v(len(set(motifs)) == 8, "un motif dessiné différent par lieu", motifs)

        # 2 · chaque station se révèle, et la jauge dit son kilomètre
        for i, s in enumerate(STATIONS):
            aller(pg, s)
            vue = pg.eval_on_selector("#" + s, "e=>e.classList.contains('vue')")
            v(vue, "la station %s se révèle" % s)
            # on place le MILIEU de l'écran dans la station
            pg.evaluate("""(id)=>{const e=document.getElementById(id);
                const r=e.getBoundingClientRect();
                window.scrollTo(0, r.top + window.scrollY + r.height/2 - window.innerHeight/2);}""", s)
            pg.wait_for_timeout(450)
            lu = pg.eval_on_selector("#jaugeN", "e=>+e.textContent")
            v(lu == KM[i], "la jauge affiche km %d sur %s" % (KM[i], s), "elle affiche %s" % lu)

        # 3 · le titre ne déborde jamais de son cartel
        for s in STATIONS:
            aller(pg, s)
            deb = pg.eval_on_selector("#" + s + " .st-t",
                                      "e=>e.scrollWidth - e.clientWidth")
            v(deb <= 1, "le titre de %s tient dans son cartel" % s, "déborde de %spx" % deb)

        # 4 · L'ANNEAU est un instrument FLOTTANT, transparent : il ne doit
        #     jamais se poser sur du texte, sinon les deux deviennent
        #     illisibles. (Les bandes de bord, elles, ont le droit : voir 4bis.)
        for s in STATIONS + ["halte-1", "saut", "carnet"]:
            aller(pg, s)
            chev = pg.evaluate("""()=>{
              const f=document.getElementById('jauge');
              if(!f||getComputedStyle(f).visibility==='hidden') return [];
              const a=f.getBoundingClientRect();
              if(a.width<2) return [];
              const sel='.st-tx p, .st-av, .ha-tx p, .ca-p, .tata-n, .pagaie-l,'
                       +' .frotter-l, .ca-b a, .ca-b button, .st-jauge, .attente,'
                       +' .st-t, .ha-t, .ca-t, .ha-c, .ca-i';
              const bad=[];
              for(const t of document.querySelectorAll(sel)){
                const b=t.getBoundingClientRect();
                if(b.width<2||b.bottom<0||b.top>innerHeight) continue;
                const ox=Math.min(a.right,b.right)-Math.max(a.left,b.left);
                const oy=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);
                if(ox>4&&oy>4) bad.push('anneau sur '+(t.className||t.tagName));
              }
              return bad;
            }""")
            v(not chev, "l'anneau ne se pose sur aucun texte sur %s" % s, chev[:2])

        # 4bis · une bande de bord a le droit de passer devant du contenu,
        #        mais alors elle doit être VRAIMENT opaque.
        # On ne lit pas une chaîne CSS, on PHOTOGRAPHIE la barre pendant
        # qu'un motif clair défile dessous, et on regarde si ça transparaît.
        aller(pg, "station-2")
        pg.evaluate("()=>window.scrollBy(0, 220)")
        pg.wait_for_timeout(400)
        bande = pg.screenshot(clip={"x": 400, "y": 0, "width": 600, "height": 10})
        im = Image.open(io.BytesIO(bande)).convert("RGB")
        px = list(im.getdata())
        pire = max(lum(p) for p in px)
        v(pire < 0.02,
          "le voile du haut de barre est vraiment opaque (rien ne transparaît)",
          "luminance la plus claire mesurée : %.4f" % pire)

        # 5 · le contraste, mesuré sur les pixels réellement rendus
        aller(pg, "station-3")
        for sel, nom in [(".st-tx p", "le texte d'une station"),
                         ("#station-3 .st-r", "le sous-titre italique"),
                         ("#station-3 .st-k", "l'étiquette de kilomètre")]:
            f = fond_reel(pg, sel)
            c = couleur_texte(pg, sel)
            if f and c:
                r = contraste(c, f)
                v(r >= 4.5, "contraste de %s : %.2f:1" % (nom, r), "%.2f:1" % r)

        aller(pg, "halte-1")
        for sel, nom in [(".ha-tx p", "le texte de la halte"),
                         (".ha-ch", "le chapeau italique de la halte")]:
            f = fond_reel(pg, sel)
            c = couleur_texte(pg, sel)
            if f and c:
                r = contraste(c, f)
                v(r >= 4.5, "contraste de %s : %.2f:1" % (nom, r), "%.2f:1" % r)

        # 6 · le verbe TENIR remplit vraiment, et seulement si on tient
        aller(pg, "station-0")
        b = pg.query_selector("#tenirB")
        box = b.bounding_box()
        pg.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        pg.mouse.down()
        pg.wait_for_timeout(1500)
        moitie = pg.eval_on_selector("#tenirJ", "e=>+e.style.strokeDashoffset||289.03")
        pg.mouse.up()
        pg.wait_for_timeout(200)
        relache = pg.eval_on_selector("#tenirJ", "e=>+e.style.strokeDashoffset||289.03")
        v(moitie < 220, "tenir remplit l'anneau", "reste %.1f" % moitie)
        v(relache > 280, "relâcher remet l'anneau à zéro", "reste %.1f" % relache)

        # 7 · le verbe PAGAYER répond au glissement
        aller(pg, "station-3")
        p = pg.query_selector("#pagaieP")
        bb = p.bounding_box()
        pg.mouse.move(bb["x"] + 30, bb["y"] + bb["height"] / 2)
        pg.mouse.down()
        pg.mouse.move(bb["x"] + 230, bb["y"] + bb["height"] / 2, steps=8)
        pg.mouse.up()
        pg.wait_for_timeout(500)
        av = pg.eval_on_selector("#pagaieP", "e=>+e.getAttribute('aria-valuenow')")
        v(av > 5, "pagayer fait avancer la pirogue", "valeur %s" % av)

        # 8 · le verbe FROTTER découvre le mur
        aller(pg, "station-4")
        m = pg.query_selector("#frotterM")
        mb = m.bounding_box()
        pg.mouse.move(mb["x"] + mb["width"] / 2, mb["y"] + mb["height"] / 2)
        pg.wait_for_timeout(700)
        r_ = pg.eval_on_selector("#frotterM .voile",
                                 "e=>parseFloat(getComputedStyle(e).getPropertyValue('--r'))||0")
        v(r_ > 20, "frotter découvre le bas-relief", "rayon %.1f" % r_)

        # 9 · arriver par le MENU révèle quand même (piège de l'observer)
        pg2 = ctx.new_page()
        pg2.goto(BASE, wait_until="load")
        pg2.wait_for_timeout(1800)
        pg2.click("#entrer")
        pg2.wait_for_timeout(600)
        pg2.click("#ouvrirCarte")
        pg2.wait_for_timeout(900)
        pg2.click('#carteL a[href="#station-6"]')
        pg2.wait_for_timeout(1600)
        v(pg2.eval_on_selector("#station-6", "e=>e.classList.contains('vue')"),
          "une station atteinte par le menu se révèle")
        # Ce qui compte n'est pas la position de la section mais que sa
        # PREMIÈRE LIGNE soit visible sous la barre : c'est exactement le
        # défaut qui était passé chez Angy Art (étiquette à 6 px sous la barre).
        etiq = pg2.evaluate("""()=>{
          const k=document.querySelector('#station-6 .st-k');
          const b=document.getElementById('barre');
          if(!k||!b) return null;
          return {haut: Math.round(k.getBoundingClientRect().top),
                  barre: Math.round(b.getBoundingClientRect().bottom)};
        }""")
        v(etiq and etiq["haut"] >= etiq["barre"],
          "le menu laisse l'étiquette du lieu SOUS la barre, jamais dessous elle", etiq)
        pg2.close()

        # 10 · pas de débordement horizontal
        for larg in (390, 768, 1440):
            pg.set_viewport_size({"width": larg, "height": 860})
            pg.wait_for_timeout(500)
            d = pg.evaluate("()=>document.documentElement.scrollWidth - document.documentElement.clientWidth")
            v(d <= 1, "aucun débordement horizontal en %d" % larg, "%spx" % d)
        pg.set_viewport_size({"width": 1440, "height": 900})

        ctx.close()

        # ── PASSE 2 · téléphone 390, tactile ───────────────────────
        ctx2 = nav.new_context(viewport={"width": 390, "height": 844},
                               is_mobile=True, has_touch=True)
        m2 = ctx2.new_page()
        err2 = []
        m2.on("pageerror", lambda e: err2.append(str(e)))
        entrer(m2)
        v(not err2, "aucune erreur JavaScript au téléphone", err2[:2])

        petites = m2.evaluate("""()=>{
          const bad=[];
          for(const e of document.querySelectorAll('a[href], button')){
            const r=e.getBoundingClientRect();
            if(r.width<2||r.height<2) continue;
            if(getComputedStyle(e).visibility==='hidden') continue;
            if(r.height<44 || r.width<44) bad.push((e.id||e.className||e.tagName)+' '+Math.round(r.width)+'x'+Math.round(r.height));
          }
          return bad;
        }""")
        v(not petites, "toute cible tactile fait au moins 44 px", petites[:3])

        # Au téléphone l'anneau devient une réglette de bord. Elle a le droit
        # de passer devant du contenu, à deux conditions : être opaque, et
        # laisser tout le contenu ATTEIGNABLE (le dernier écran doit pouvoir
        # défiler au-dessus d'elle).
        aller(m2, "station-5")
        fond = m2.eval_on_selector("#jauge", "e=>getComputedStyle(e).backgroundColor")
        v("rgb(" in fond and "rgba" not in fond,
          "la réglette du téléphone est vraiment opaque", fond)

        m2.evaluate("()=>window.scrollTo(0, document.body.scrollHeight)")
        m2.wait_for_timeout(700)
        reste = m2.evaluate("""()=>{
          const j=document.getElementById('jauge').getBoundingClientRect();
          const bad=[];
          for(const t of document.querySelectorAll('.pied-c, .ca-b a, .ca-b button')){
            const b=t.getBoundingClientRect();
            if(b.width<2) continue;
            const ox=Math.min(j.right,b.right)-Math.max(j.left,b.left);
            const oy=Math.min(j.bottom,b.bottom)-Math.max(j.top,b.top);
            if(ox>4&&oy>4) bad.push(t.className);
          }
          return bad;
        }""")
        v(not reste, "en bas de page, la réglette ne bloque plus rien", reste[:2])
        ctx2.close()

        # ── PASSE 3 · mouvement réduit : tout doit être VISIBLE ────
        ctx3 = nav.new_context(viewport={"width": 1200, "height": 860},
                               reduced_motion="reduce")
        m3 = ctx3.new_page()
        m3.goto(BASE, wait_until="load")
        m3.wait_for_timeout(900)
        v(m3.eval_on_selector_all("#rideau", "e=>e.length===0 || getComputedStyle(e[0]).display==='none'"),
          "sans animation, aucun rideau ne bloque")
        m3.evaluate("()=>{const s=document.getElementById('seuil'); if(s&&!s.hidden) document.getElementById('entrer').click();}")
        m3.wait_for_timeout(400)
        aller(m3, "station-4")
        op = m3.eval_on_selector("#station-4 .st-tx p", "e=>+getComputedStyle(e).opacity")
        v(op > .9, "sans animation, le texte est visible d'emblée", op)
        ctx3.close()

        nav.close()


if __name__ == "__main__":
    srv = servir()
    try:
        controler()
    finally:
        srv.shutdown()

    print("\n" + "=" * 62)
    for t in ok:
        print("  OK   " + t)
    for t in ko:
        print("  ECHEC " + t)
    print("=" * 62)
    print("%d controles verts, %d echecs" % (len(ok), len(ko)))
    sys.exit(1 if ko else 0)

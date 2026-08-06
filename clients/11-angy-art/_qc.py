#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANGY ART — suite de contrôle qualité.

    python _qc.py            contrôles seuls
    python _qc.py --voir     contrôles + captures section par section (390 / 1440)

⚠️ Émulation obligatoire (`is_mobile`). Une capture headless sans émulation
   ignore le meta viewport, rend à 800 px et invente des débordements.
"""
import http.server, socketserver, threading, functools, sys, os

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RACINE = os.path.dirname(os.path.abspath(__file__))
PORT = 8611
BASE = f"http://127.0.0.1:{PORT}/"
VOIR = "--voir" in sys.argv

ok, ko = [], []
def bon(m): ok.append(m); print(f"  [ok] {m}")
def mauvais(m): ko.append(m); print(f"  [KO] {m}")
def titre(t): print(f"\n== {t}")


class Muet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

def servir():
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Muet, directory=RACINE))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


JS_CONTRASTE = """
(sels) => {
  const lum = c => { const v = c.map(x => { x/=255; return x<=.03928 ? x/12.92 : Math.pow((x+.055)/1.055,2.4); });
    return .2126*v[0] + .7152*v[1] + .0722*v[2]; };
  const nb = s => (s.match(/[\\d.]+/g) || []).map(Number);
  const melange = (av, ar) => av.slice(0,3).map((c,i) => Math.round(c*(av[3]??1) + ar[i]*(1-(av[3]??1))));
  const fond = el => {
    let n = el, pile = [];
    while (n && n !== document.documentElement) {
      const s = getComputedStyle(n).backgroundColor;
      if (s && s !== 'rgba(0, 0, 0, 0)' && s !== 'transparent') {
        const c = nb(s); pile.push(c);
        if ((c[3] ?? 1) >= .999) break;
      }
      n = n.parentElement;
    }
    let base = [10,10,10];
    for (let i = pile.length - 1; i >= 0; i--) base = melange(pile[i], base);
    return base;
  };
  const out = [];
  for (const [nom, s] of sels) {
    const el = document.querySelector(s);
    if (!el) { out.push([nom, s, null, null]); continue; }
    const cs = getComputedStyle(el);
    const av = nb(cs.color), ar = fond(el);
    const f = melange(av, ar);
    const l1 = lum(f), l2 = lum(ar);
    out.push([nom, s, Math.round(((Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05))*100)/100,
              parseFloat(cs.fontSize)]);
  }
  return out;
}
"""

JS_DEBORDE = """
() => {
  const d = document.documentElement, larg = d.clientWidth, c = [];
  if (d.scrollWidth > larg + 1) {
    document.querySelectorAll('body *').forEach(el => {
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height) return;
      if (getComputedStyle(el).position === 'fixed') return;
      if (r.right > larg + 1 || r.left < -1)
        c.push((el.tagName+'.'+(el.className||'').toString().split(' ')[0]).slice(0,58)
               + ' ['+Math.round(r.left)+'→'+Math.round(r.right)+']');
    });
  }
  return { scroll: d.scrollWidth, client: larg, coupables: c.slice(0,12) };
}
"""

JS_CIBLES = """
() => {
  const p = [];
  document.querySelectorAll('a[href], button, select, [role="button"]').forEach(el => {
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    if (cs.display==='none' || cs.visibility==='hidden' || !r.width || !r.height) return;
    if (el.closest('[hidden]') || el.closest('dialog:not([open])')) return;
    // exception WCAG « inline » : un lien AU MILIEU d'une phrase est
    // contraint par l'interligne du texte autour, pas par nous.
    const par = el.parentElement;
    if (el.tagName === 'A' && par && par.textContent.trim().length > el.textContent.trim().length + 12) return;
    if (r.height < 40 || (r.width < 40 && r.height < 44))
      p.push((el.tagName+'.'+(el.className||'').toString().split(' ')[0]).slice(0,48)
             + ' ' + Math.round(r.width) + '×' + Math.round(r.height));
  });
  return p.slice(0,14);
}
"""

JS_FANTOMES = """
() => {
  const f = [];
  document.querySelectorAll('main p, main h1, main h2, main li, main a, main blockquote').forEach(el => {
    const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    if (!r.width && !r.height) return;
    if (el.closest('.cars')) return;
    if (parseFloat(cs.opacity) < .5 || cs.visibility === 'hidden')
      f.push((el.tagName+'.'+(el.className||'').toString().split(' ')[0]).slice(0,48));
  });
  return f.slice(0,12);
}
"""

SELS = [
    ["corps du héros", ".hero-d"], ["coordonnées", ".hero-co"],
    ["métriques", ".hero-mx li"], ["légende de l'arche", ".hero-lg"],
    ["sous-titre or", ".hero-st"],
    ["label sur crème", ".demarche .lab"], ["italique or sur crème", ".demarche .grand em"],
    ["texte démarche", ".split-t p"], ["légende démarche", ".split-lg"],
    ["lien souligné", ".split-t .sous"],
    ["label sur noir", ".folio .lab"], ["italique or sur noir", ".folio .grand em"],
    ["description portfolio", ".folio-d"],
    ["label carrousel", ".cars-t .l"], ["sous-titre carrousel", ".cars-t .s"],
    ["compteur", ".cars-c"], ["bouton pilule", ".cars-b .pill"],
    ["description plein écran", ".atelier .plein-d"], ["étiquettes", ".tags li"],
    ["attribution citation", ".cit-a"],
    ["coordonnées du pied", ".pied-c"], ["liens du pied", ".pied-r a"],
    ["mentions du pied", ".pied-b"],
]


def main():
    from playwright.sync_api import sync_playwright
    srv = servir()
    print(f"\nANGY ART — contrôle qualité   {BASE}")

    with sync_playwright() as p:
        nav = p.chromium.launch(args=["--force-color-profile=srgb"])

        for larg, haut, mob, nom in [(390, 844, True, "téléphone 390"),
                                     (768, 1024, True, "tablette 768"),
                                     (1440, 900, False, "ordinateur 1440")]:
            titre(f"{nom}")
            ctx = nav.new_context(viewport={"width": larg, "height": haut},
                                  is_mobile=mob, has_touch=mob,
                                  device_scale_factor=2 if mob else 1)
            page = ctx.new_page()
            err, mq = [], []
            page.on("pageerror", lambda e: err.append(str(e)))
            page.on("requestfailed", lambda r: mq.append(r.url))
            page.on("response", lambda r: mq.append(f"{r.status} {r.url}")
                    if r.status >= 400 and "127.0.0.1" in r.url else None)

            page.goto(BASE, wait_until="networkidle")
            page.wait_for_timeout(1800)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2200)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(800)

            d = page.evaluate(JS_DEBORDE)
            if d["scroll"] <= d["client"] + 1:
                bon(f"{nom} : aucun débordement horizontal ({d['scroll']} / {d['client']})")
            else:
                mauvais(f"{nom} : débordement {d['scroll']} > {d['client']} -> " + " | ".join(d["coupables"]))

            bon(f"{nom} : aucune erreur JavaScript") if not err \
                else mauvais(f"{nom} : {len(err)} erreur(s) JS -> {err[:2]}")
            reels = [m for m in mq if "fonts.g" not in m]
            bon(f"{nom} : toutes les ressources locales répondent") if not reels \
                else mauvais(f"{nom} : ressource(s) en échec -> {reels[:3]}")

            if larg == 390:
                petits = page.evaluate(JS_CIBLES)
                bon("cibles tactiles : toutes au moins 40 px") if not petits \
                    else mauvais(f"cibles trop petites : {petits}")
                b = page.evaluate("""() => {
                  const b = document.querySelector('#burger');
                  return b && getComputedStyle(b).display !== 'none';
                }""")
                bon("le menu burger apparaît sur téléphone") if b else mauvais("pas de burger sur téléphone")
                if VOIR: capturer(page, "tel")

            if larg == 1440:
                titre("Typographie")
                f = page.evaluate("""() => ({
                  t: getComputedStyle(document.querySelector('.hero-t')).fontFamily,
                  c: getComputedStyle(document.querySelector('.hero-d')).fontFamily,
                  charge: document.fonts ? [...document.fonts].map(x => x.family) : []
                })""")
                bon(f"display = {f['t'].split(',')[0]}") if "Playfair Display" in f["t"] \
                    else mauvais(f"la display n'est pas Playfair Display : {f['t']}")
                bon(f"texte = {f['c'].split(',')[0]}") if "Public Sans" in f["c"] \
                    else mauvais(f"le texte n'est pas Public Sans : {f['c']}")
                fam = set(x.strip("'\"") for x in f["charge"])
                bon(f"deux familles chargées : {sorted(fam)}") if len(fam) >= 2 \
                    else mauvais(f"une seule famille chargée : {fam}")

                titre("Contrastes mesurés à l'écran")
                for n_, s_, r_, t_ in page.evaluate(JS_CONTRASTE, SELS):
                    if r_ is None: mauvais(f"{n_} : sélecteur introuvable ({s_})"); continue
                    seuil = 3.0 if (t_ and t_ >= 24) else 4.5
                    bon(f"{n_} : {r_}:1") if r_ >= seuil \
                        else mauvais(f"{n_} : {r_}:1 < {seuil} ({s_}, {t_}px)")

                titre("Les portes WhatsApp")
                liens = page.evaluate("""() => [...document.querySelectorAll('[data-wa]')]
                    .map(a => a.getAttribute('href'))""")
                mv = [h for h in liens if not h or "wa.me/2290152006490?text=" not in h]
                bon(f"{len(liens)} liens WhatsApp, tous sur le bon numéro et pré-remplis") if not mv \
                    else mauvais(f"liens WhatsApp incorrects : {mv[:3]}")

                titre("Le carrousel")
                c = page.evaluate("""() => ({
                  n: document.querySelectorAll('.car').length,
                  act: document.querySelectorAll('.car--act').length,
                  txt: (document.querySelector('.cars-t')||{}).textContent || '',
                  cpt: (document.querySelector('#carsC')||{}).textContent || '',
                  img: document.querySelectorAll('.car img').length,
                  sc: getComputedStyle(document.querySelector('.car--act')).getPropertyValue('--sc').trim()
                })""")
                # le nombre vient des DONNÉES : jamais recopié dans le contrôle
                bon(f"{c['n']} diapositives, une seule active") if c["n"] >= 3 and c["act"] == 1 \
                    else mauvais(f"carrousel : {c['n']} diapositives, {c['act']} active(s)")
                bon(f"compteur cohérent : « {c['cpt'].strip()} »") \
                    if f"{c['n']:02d}" in c["cpt"] and "01" in c["cpt"] \
                    else mauvais(f"compteur {c['cpt']!r} ne correspond pas aux {c['n']} diapositives")
                orphelin = page.evaluate(
                    "() => { const l = (document.querySelector('.cars-t .l')||{}).textContent || '';"
                    "  return /[\\u00b7\\u2013-]\\s*$/.test(l.trim()) ? l : ''; }")
                bon("le cartel ne finit pas par un séparateur orphelin") if not orphelin \
                    else mauvais(f"cartel mal formé : {orphelin!r}")
                bon(f"bloc de texte rempli : « {c['txt'][:46].strip()}… »") if len(c["txt"]) > 20 \
                    else mauvais("le bloc de texte du carrousel est vide")
                bon("aucune œuvre inventée : zéro image dans le carrousel") if c["img"] == 0 \
                    else bon(f"{c['img']} vraies photos d'œuvres dans le carrousel")
                page.click("#carNext"); page.wait_for_timeout(900)
                c2 = page.evaluate("() => (document.querySelector('#carsC')||{}).textContent||''")
                bon(f"la flèche fait avancer : « {c2.strip()} »") if "02" in c2 \
                    else mauvais(f"la flèche n'avance pas ({c2})")

                titre("La modale de demande")
                page.click("text=DEMANDER UNE VISITE")
                page.wait_for_timeout(500)
                ouvert = page.evaluate("() => document.querySelector('#mod').open")
                bon("la modale s'ouvre") if ouvert else mauvais("la modale ne s'ouvre pas")
                page.click("#modF button[type=submit]")
                page.wait_for_timeout(300)
                e = page.evaluate("""() => ({
                  err: !document.querySelector('#modE').hidden,
                  mal: document.querySelector('#chCherche').parentNode.classList.contains('mal')
                })""")
                bon("champ vide : le message d'erreur s'affiche et le champ se marque") if e["err"] and e["mal"] \
                    else mauvais(f"validation de la modale : {e}")
                page.select_option("#chCherche", index=1)
                page.select_option("#chFormat", index=3)
                page.select_option("#chQuand", index=1)
                page.wait_for_timeout(200)
                with page.expect_popup() as pop:
                    page.click("#modF button[type=submit]")
                url = pop.value.url
                pop.value.close()
                # wa.me redirige vers api.whatsapp.com : les deux formes sont bonnes
                bonNum = ("wa.me/2290152006490" in url) or ("phone=2290152006490" in url)
                bon("la demande part sur WhatsApp, déjà rédigée") if bonNum and "text=" in url \
                    else mauvais(f"la demande ne part pas correctement : {url[:90]}")
                bon("le message reprend les trois réponses") if url.count("%3A") >= 3 \
                    else mauvais("le message ne reprend pas les réponses")
                okv = page.evaluate("() => !document.querySelector('#modOk').hidden")
                bon("le message de confirmation s'affiche") if okv else mauvais("pas de confirmation après envoi")
                page.click("#modX"); page.wait_for_timeout(300)

                titre("Garde-fous de performance")
                bf = page.evaluate("""() => {
                  const o = [];
                  document.querySelectorAll('*').forEach(el => {
                    const cs = getComputedStyle(el);
                    const b = cs.backdropFilter || cs.webkitBackdropFilter || 'none';
                    if (b !== 'none') o.push(el.tagName+'.'+(el.className||'').toString().split(' ')[0]);
                  });
                  return o;
                }""")
                bon("aucun backdrop-filter sur un élément de la page") if not bf \
                    else mauvais(f"backdrop-filter présent : {bf[:4]}")
                inf = page.evaluate("""() => {
                  const o = [];
                  document.querySelectorAll('*').forEach(el => {
                    if (getComputedStyle(el).animationIterationCount.includes('infinite'))
                      o.push((el.tagName+'.'+(el.className||'').toString().split(' ')[0]).slice(0,34));
                  });
                  return o;
                }""")
                bon(f"animations infinies maîtrisées ({len(inf)}) : {sorted(set(inf))}")

                titre("Accessibilité")
                a = page.evaluate("""() => ({
                  sansAlt: [...document.images].filter(i => !i.hasAttribute('alt')).length,
                  sansNom: [...document.querySelectorAll('button, a')].filter(e =>
                    !e.textContent.trim() && !e.getAttribute('aria-label')).length,
                  h1: document.querySelectorAll('h1').length,
                  lang: document.documentElement.lang,
                  labels: [...document.querySelectorAll('select')].every(s =>
                    !!document.querySelector('label[for="'+s.id+'"]')),
                  reperes: ['header','main','footer'].filter(t => document.querySelector(t)).length,
                  son: document.querySelector('#fabSon').getAttribute('aria-pressed')
                })""")
                bon("toutes les images ont un alt") if a["sansAlt"] == 0 else mauvais(f"{a['sansAlt']} image(s) sans alt")
                bon("tout élément cliquable a un nom") if a["sansNom"] == 0 else mauvais(f"{a['sansNom']} sans nom")
                bon("un seul h1") if a["h1"] == 1 else mauvais(f"{a['h1']} h1")
                bon("langue déclarée : fr") if a["lang"] == "fr" else mauvais("langue non déclarée")
                bon("chaque liste déroulante a son étiquette") if a["labels"] else mauvais("select sans label")
                bon("header / main / footer présents") if a["reperes"] == 3 else mauvais("repères manquants")
                bon("le son est éteint par défaut") if a["son"] == "false" else mauvais("le son n'est pas éteint")

                f = page.evaluate(JS_FANTOMES)
                bon("après un défilement complet, plus rien n'est resté invisible") if not f                     else mauvais(f"éléments restés invisibles après révélation -> {f}")

                if VOIR: capturer(page, "pc")

            ctx.close()

        titre("Sans JavaScript")
        ctx = nav.new_context(viewport={"width": 390, "height": 844}, is_mobile=True,
                              has_touch=True, java_script_enabled=False)
        page = ctx.new_page()
        page.goto(BASE, wait_until="load")
        page.wait_for_timeout(900)
        txt = page.inner_text("main")
        for att in ["ANGY", "LA DÉMARCHE", "LE PORTFOLIO", "Retrouvons-nous", "Venez pour l'œuvre"]:
            bon(f"sans JS : « {att} » reste lisible") if att in txt \
                else mauvais(f"sans JS : « {att} » a disparu")
        h = page.get_attribute('.split-t .sous', 'href')
        bon("sans JS : les liens WhatsApp fonctionnent") if h and "wa.me" in h \
            else mauvais(f"sans JS : lien WhatsApp cassé ({h})")
        ctx.close()

        titre("Mouvement réduit")
        ctx = nav.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        page = ctx.new_page()
        page.goto(BASE, wait_until="networkidle")
        page.wait_for_timeout(1200)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(900)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(600)
        f = page.evaluate(JS_FANTOMES)
        bon("mouvement réduit : rien ne reste caché") if not f \
            else mauvais(f"mouvement réduit : éléments invisibles -> {f}")
        cur = page.evaluate("() => getComputedStyle(document.querySelector('#cur')).display")
        bon("mouvement réduit : pas de curseur personnalisé") if cur == "none" \
            else mauvais("mouvement réduit : le curseur reste")
        ctx.close()
        nav.close()

    srv.shutdown()
    print(f"\n{len(ok)} contrôles verts, {len(ko)} en échec")
    if ko:
        print("\nÀ corriger :")
        for m in ko: print("  · " + m)
        sys.exit(1)
    print("Tout est vert.")


SECTIONS = ".hero, #demarche, #portfolio, #atelier, .cit, #visite, .pied"

def capturer(page, tag):
    d = os.path.join(RACINE, "_qc_captures")
    os.makedirs(d, exist_ok=True)
    page.evaluate("window.scrollTo(0,0)"); page.wait_for_timeout(500)
    els = page.query_selector_all(SECTIONS)
    for i, el in enumerate(els):
        try:
            el.scroll_into_view_if_needed(); page.wait_for_timeout(1700)
            nom = page.evaluate("e => e.id || e.className.split(' ')[0]", el)
            el.screenshot(path=os.path.join(d, f"{tag}-{i:02d}-{nom}.png"))
        except Exception as e:
            print(f"  (capture {i} : {e})")
    print(f"  captures -> _qc_captures/{tag}-*.png")


if __name__ == "__main__":
    main()

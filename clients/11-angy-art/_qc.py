#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANGY ART — suite de contrôle qualité.

    python _qc.py            contrôles seuls
    python _qc.py --voir     contrôles + captures section par section (390 / 1440)

⚠️ Émulation obligatoire (`is_mobile`). Une capture headless sans émulation
   ignore le meta viewport, rend à 800 px et invente des débordements.
"""
import http.server, socketserver, threading, functools, sys, os, glob

# ⚠️ ON DIT À PLAYWRIGHT OÙ EST LE NAVIGATEUR. Dans l'environnement distant,
#    Chromium est déjà là (`/opt/pw-browsers`) mais Playwright cherche le
#    numéro de version qu'il attend, ne le trouve pas, et réclame
#    « playwright install » — un téléchargement inutile de 150 Mo qui ne
#    marche pas non plus derrière le filtre. On lui donne le chemin.
#    Sur le PC de Cotonou le motif ne correspond à rien et rien ne change.
_CH = [g for g in glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")
       if "headless" not in g]
NAVIG = {"executable_path": _CH[0]} if _CH else {}

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


# ── contraste mesuré SUR LA PHOTO, pas sur la couleur calculée ─────────────
# Le contrôle de contraste classique lit `background-color`. Au-dessus d'une
# photo cette couleur est transparente : il ne voit donc RIEN, et laisse
# passer un texte blanc posé sur un masque orange vif. Ici on masque le
# texte, on photographie la zone, et on mesure les pixels qui restent.

def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(r, g, b):
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contraste(l1, l2):
    a, b = max(l1, l2), min(l1, l2)
    return round((a + 0.05) / (b + 0.05), 2)


def placer(page, sel, essais=6):
    """Amène `sel` au centre de l'écran et VÉRIFIE qu'il y est arrivé.

    ⚠️ LE SITE A SON PROPRE MOTEUR DE DÉFILEMENT. Tant qu'il glisse, il écrit
    lui aussi dans `scrollY` : un `scrollIntoView` venu du contrôle est effacé
    à l'image suivante. Attendre 500 ms ne prouve donc rien — il faut REGARDER
    où on a atterri, et recommencer.

    Le 2026-08-21 ce contrôle passait seul et échouait juste après les
    captures, qui laissent le moteur en pleine course : ce n'était pas le
    site, c'était la mesure. Même famille que la leçon d'Au Braisé d'Or.
    Rend la boîte finale (ou None), au contrôle de dire ce qu'il en pense.
    """
    etat = None
    for _ in range(essais):
        page.evaluate("""(s) => {
          document.documentElement.style.scrollBehavior = 'auto';
          const e = document.querySelector(s); if (!e) return;
          const r = e.getBoundingClientRect();
          window.scrollTo(0, r.top + window.scrollY - (innerHeight - r.height) / 2);
        }""", sel)
        page.wait_for_timeout(420)
        etat = page.evaluate("""(s) => {
          const e = document.querySelector(s); if (!e) return null;
          const r = e.getBoundingClientRect();
          return { haut: Math.round(r.top), bas: Math.round(r.bottom),
                   h: Math.round(r.height), ecran: innerHeight };
        }""", sel)
        if etat is None:
            return None
        # une boîte plus haute que l'écran ne rentrera jamais : on demande
        # seulement qu'elle occupe l'écran.
        vu = min(etat["bas"], etat["ecran"]) - max(etat["haut"], 0)
        if vu >= 0.9 * min(etat["h"], etat["ecran"]):
            return etat
    return etat


def fond_derriere(page, sel, alpha=0.72):
    """Rend (contraste, description) pour un texte clair posé sur une photo.

    On retient le DÉCILE LE PLUS CLAIR du fond : c'est là que le texte se perd,
    et une moyenne le noierait. Le texte est du blanc à `alpha` composité sur
    ce fond, exactement comme le navigateur le peint.
    """
    from PIL import Image
    el = page.query_selector(sel)
    if el is None:
        return None, f"{sel} introuvable"
    page.evaluate("s => document.querySelector(s).style.visibility='hidden'", sel)
    # ⚠️ La boîte se lit APRÈS que tout se soit posé. Lue avant, pendant que le
    # défilement doux finissait sa course, elle était périmée de quelques
    # centaines de pixels : on mesurait la photo au lieu du fond du texte.
    page.wait_for_timeout(450)
    boite = el.bounding_box()
    if not boite or boite["width"] < 8 or boite["height"] < 8:
        page.evaluate("s => document.querySelector(s).style.visibility=''", sel)
        return None, f"{sel} sans surface"
    brut = page.screenshot()          # le viewport, rien d'autre
    page.evaluate("s => document.querySelector(s).style.visibility=''", sel)
    import io
    plein = Image.open(io.BytesIO(brut)).convert("RGB")
    # ⚠️ `bounding_box()` parle en pixels CSS relatifs au VIEWPORT, alors que
    # `screenshot(clip=…)` parle en pixels de la PAGE : les mélanger fait
    # mesurer une zone qui n'a rien à voir. On découpe donc nous-mêmes, en
    # remettant l'échelle de l'écran (device_scale_factor).
    ech = plein.width / page.viewport_size["width"]
    g = max(0, int(boite["x"] * ech))
    h = max(0, int(boite["y"] * ech))
    d = min(plein.width, int((boite["x"] + boite["width"]) * ech))
    b = min(plein.height, int((boite["y"] + boite["height"]) * ech))
    if d - g < 2 or b - h < 2:
        return None, f"{sel} hors du viewport"
    im = plein.crop((g, h, d, b))
    px = list(im.getdata())
    lums = sorted(luminance(*p) for p in px)
    pire = lums[int(len(lums) * 0.9)]          # le fond le plus clair
    i = min(range(len(px)), key=lambda k: abs(luminance(*px[k]) - pire))
    fr, fg, fb = px[i]
    tr = alpha * 255 + (1 - alpha) * fr        # blanc à `alpha` sur ce fond
    tg = alpha * 255 + (1 - alpha) * fg
    tb = alpha * 255 + (1 - alpha) * fb
    return contraste(luminance(tr, tg, tb), pire), f"fond le plus clair rgb({fr},{fg},{fb})"

def servir():
    # ⚠️ SERVEUR MULTI-TÂCHES, PAS `TCPServer`. Le navigateur garde ses
    #    connexions ouvertes : avec un serveur mono-tâche, l'une bloque les
    #    autres et la page ne se charge plus dans les temps. Le symptôme est
    #    « Page.goto: Timeout » et il fait accuser le site, qui n'y est pour
    #    rien. Même panne réparée chez Hillary le 2026-08-17.
    class Serveur(socketserver.ThreadingTCPServer):
        daemon_threads = True
        allow_reuse_address = True

    srv = Serveur(("127.0.0.1", PORT), functools.partial(Muet, directory=RACINE))
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

# ── LE BOUTON UNIQUE, ET CE QU'IL OUVRE ───────────────────────────────────
# « Visible » ne veut pas dire « présent dans le document » : un bouton peut
# avoir une boîte, un texte, et être effacé (opacité), masqué (`visibility`) ou
# simplement hors de l'écran. Les trois cas se produisent ici, et c'est le
# troisième qui compte le plus : celui du héros existe encore quand on est en
# bas de page, il n'est juste plus là où on regarde.
JS_DEC = """
() => {
  const vu = el => {
    const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    return cs.display !== 'none' && cs.visibility !== 'hidden'
      && parseFloat(cs.opacity) > .5 && r.width > 0 && r.height > 0
      && r.bottom > 0 && r.top < innerHeight;
  };
  const b = [...document.querySelectorAll('[data-dec]')];
  return { total: b.length, vus: b.filter(vu).map(e => e.id) };
}
"""

JS_PANNEAU = """
() => {
  const l = document.querySelector('#navC');
  if (!l) return { ouvert: false, total: 0, dedans: 0, dehors: ['pas de panneau'],
                   coupe: true, deborde: 0, inerte: false };
  const as = [...l.querySelectorAll('a')], dehors = [];
  for (const a of as) {
    const r = a.getBoundingClientRect();
    const dedans = r.width > 0 && r.height > 0 && r.top > -1 && r.bottom < innerHeight + 1
      && r.left > -1 && r.right < innerWidth + 1;
    if (!dedans) dehors.push(a.textContent.trim() + ' [' + Math.round(r.top) + '→'
      + Math.round(r.bottom) + ']');
  }
  return {
    ouvert: l.classList.contains('ouvert'),
    total: as.length, dedans: as.length - dehors.length, dehors: dehors.slice(0, 4),
    coupe: l.scrollHeight > l.clientHeight + 1,
    deborde: Math.max(0, l.scrollHeight - l.clientHeight),
    inerte: !!document.querySelector('#haut').inert
  };
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
    ["label des quatre temps", ".temps .lab"], ["italique or sur papier", ".temps .grand em"],
    ["description des quatre temps", ".temps-d"],
    ["numéro d'étape", ".tp-n"], ["titre d'étape", ".tp-t"], ["texte d'étape", ".tp-s"],
    ["label sur noir", ".folio .lab"], ["italique or sur noir", ".folio .grand em"],
    ["description portfolio", ".folio-d"],
    ["label carrousel", ".cars-t .l"], ["sous-titre carrousel", ".cars-t .s"],
    ["compteur", ".cars-c"], ["bouton pilule", ".cars-b .pill"],
    ["description plein écran", ".lieux .plein-d"], ["étiquettes", ".tags li"],
    ["attribution citation", ".cit-a"],
    ["coordonnées du pied", ".pied-c"], ["liens du pied", ".pied-r a"],
    ["mentions du pied", ".pied-b"],
]


def main():
    from playwright.sync_api import sync_playwright
    srv = servir()
    print(f"\nANGY ART — contrôle qualité   {BASE}")

    with sync_playwright() as p:
        nav = p.chromium.launch(args=["--force-color-profile=srgb"], **NAVIG)

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
            # ⚠️ le rideau d'ouverture dure ~2,3 s (compte puis retrait) :
            # mesurer avant, c'est mesurer le rideau et non la page.
            page.wait_for_timeout(3400)
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
                if VOIR: capturer(page, "tel")

            # ══ LE BOUTON UNIQUE « DÉCOUVRIR » ═══════════════════════════════
            # Mongazi, 2026-09-04 : « je veux que tous ces points se voient
            # quand on clique sur un seul bouton, découvrir, et qui reste
            # visible partout sur la page, surtout sur mobile ».
            # ⚠️ TROIS CHOSES À PROUVER, ET AUCUNE NE DÉCOULE DES AUTRES :
            #    il y en a TOUJOURS un de visible (sinon la page n'a plus de
            #    navigation), il n'y en a JAMAIS deux (sinon « un seul bouton »
            #    est faux), et ce qu'il ouvre porte VRAIMENT toutes les entrées.
            #    Le premier contrôle seul laisserait passer un site où les deux
            #    boutons s'affichent ensemble ; le deuxième seul laisserait
            #    passer un site où aucun ne s'affiche.
            titre(f"{nom} : le bouton « DÉCOUVRIR »")
            noms_ = page.evaluate("""() => [...document.querySelectorAll('[data-dec]')]
                .map(e => e.textContent.trim().split(/[^A-Za-zÀ-ÿ]+/).join(' ').trim())""")
            bon(f"{nom} : les {len(noms_)} boutons portent le même nom") \
                if noms_ and all("DÉCOUVRIR" in n.upper() for n in noms_) \
                else mauvais(f"{nom} : un bouton ne s'appelle pas « DÉCOUVRIR » -> {noms_}")

            for etage_, js_ in [("en haut", "0"),
                                ("au milieu", "document.body.scrollHeight / 2"),
                                ("en bas", "document.body.scrollHeight")]:
                page.evaluate(f"() => window.scrollTo(0, {js_})")
                page.wait_for_timeout(900)
                v_ = page.evaluate(JS_DEC)
                if len(v_["vus"]) == 1:
                    bon(f"{nom}, {etage_} : un seul bouton « DÉCOUVRIR » visible "
                        f"(#{v_['vus'][0]})")
                else:
                    mauvais(f"{nom}, {etage_} : {len(v_['vus'])} bouton(s) visible(s) "
                            f"sur {v_['total']} -> {v_['vus']}")

            # On ouvre depuis le BAS de la page : c'est là que le sommaire
            # d'avant n'existait plus, et c'est tout l'objet de la demande.
            page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(900)
            ouvreur_ = page.evaluate("""() => {
              const b = [...document.querySelectorAll('[data-dec]')].find(e => {
                const cs = getComputedStyle(e);
                return cs.display !== 'none' && cs.visibility !== 'hidden';
              });
              if (!b) return null;
              b.click();
              return b.id;
            }""")
            page.wait_for_timeout(900)
            if not ouvreur_:
                mauvais(f"{nom} : aucun bouton « DÉCOUVRIR » à cliquer en bas de page")
            else:
                pan_ = page.evaluate(JS_PANNEAU)
                bon(f"{nom} : le panneau s'ouvre depuis le bas de la page") if pan_["ouvert"] \
                    else mauvais(f"{nom} : le bouton n'ouvre rien en bas de page")
                # ⚠️ « SE VOIT » SE MESURE : une entrée peut exister, avoir une
                #    boîte, et être repoussée hors de l'écran par les autres. On
                #    compte celles qui tiennent VRAIMENT dans la fenêtre, et on
                #    refuse un panneau qu'il faudrait faire défiler pour lire.
                if pan_["dedans"] == pan_["total"]:
                    bon(f"{nom} : les {pan_['total']} points du sommaire se voient tous")
                else:
                    mauvais(f"{nom} : {pan_['dedans']} points visibles sur {pan_['total']} "
                            f"-> {pan_['dehors']}")
                bon(f"{nom} : le panneau ne cache rien derrière un défilement") \
                    if not pan_["coupe"] \
                    else mauvais(f"{nom} : le panneau déborde de {pan_['deborde']} px, "
                                 "les dernières entrées se cherchent")
                # Le reste de la page devient inerte : sinon la tabulation sort
                # du panneau vers des liens qu'on ne voit pas (leçon Hillary).
                bon(f"{nom} : la page derrière le panneau est inerte") if pan_["inerte"] \
                    else mauvais(f"{nom} : la page reste au clavier derrière le panneau")

                page.keyboard.press("Escape")
                page.wait_for_timeout(900)
                fin_ = page.evaluate("""() => ({
                  ouvert: document.querySelector('#navC').classList.contains('ouvert'),
                  focus: document.activeElement ? document.activeElement.id : '',
                  inerte: !!document.querySelector('#haut').inert
                })""")
                bon(f"{nom} : Échap referme le panneau") if not fin_["ouvert"] \
                    else mauvais(f"{nom} : Échap ne referme pas le panneau")
                bon(f"{nom} : le focus revient sur le bouton (#{fin_['focus']})") \
                    if fin_["focus"] == ouvreur_ \
                    else mauvais(f"{nom} : le focus part ailleurs après la fermeture "
                                 f"(#{fin_['focus']} au lieu de #{ouvreur_})")
                bon(f"{nom} : la page redevient atteignable au clavier") if not fin_["inerte"] \
                    else mauvais(f"{nom} : la page reste inerte après la fermeture")
            page.evaluate("() => window.scrollTo(0, 0)")
            page.wait_for_timeout(700)

            # Le défilement est écrit à la main, donc `scroll-margin-top` doit
            # être retranché explicitement. Quand on l'oublie, l'étiquette de
            # la section arrive collée sous la barre fixe : invisible sur les
            # captures d'ensemble, très visible pour qui clique le menu.
            # Deux boîtes qui se croisent : invisible dans un contrôle de
            # débordement, très visible à l'œil. Vu à 768 px, où la pilule
            # centrée en absolu s'asseyait sur la ligne des métriques.
            titre("Rien ne se chevauche")
            page.evaluate("() => window.scrollTo(0, 0)")
            page.wait_for_timeout(400)
            # ⚠️ On compare aux boîtes qui portent VRAIMENT du texte. Comparer à
            # `.hero-mx` (un <ul> large de toute la page même quand ses trois
            # libellés sont courts) déclarait un chevauchement inexistant.
            # ⚠️ `.hero-pill` retiré le 2026-08-27 à la demande d'Angélique : les
            #    deux paires qui le nommaient sont parties avec lui. Elles ne
            #    plantaient pas — le contrôle rend `None` et annonce « absent à
            #    cette taille » — mais un contrôle qui décrit un élément
            #    disparu ne protège plus rien et fait croire qu'il veille.
            # ⚠️ `.son` CONTRE LE BOUTON DU HÉROS : le bouton du son est en
            #    `position:fixed` en bas à droite, et il s'était posé sur
            #    « DÉCOUVRIR LES ŒUVRES » — 11 × 34 px, à 390 px seulement,
            #    c'est-à-dire pile la pastille qu'Angélique a nommée et pile
            #    la largeur où elle regarde. Un instrument flottant ne
            #    recouvre jamais du texte (règle née sur Mon Bénin).
            for a_, b_ in [(".hero-lg", ".cadre"), (".hero-mx li", ".cadre"),
                           (".son", ".hero-dec")]:
                croise = page.evaluate("""([sa, sb]) => {
                  const A = document.querySelector(sa);
                  const Bs = [...document.querySelectorAll(sb)];
                  if (!A || !Bs.length) return null;
                  const a = A.getBoundingClientRect();
                  let pire = 0;
                  for (const B of Bs) {
                    const b = B.getBoundingClientRect();
                    const x = Math.min(a.right, b.right) - Math.max(a.left, b.left);
                    const y = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
                    if (x > 2 && y > 2) pire = Math.max(pire, Math.round(Math.min(x, y)));
                  }
                  return pire;
                }""", [a_, b_])
                if croise is None:
                    bon(f"{a_} / {b_} : absent à cette taille")
                elif croise:
                    mauvais(f"{a_} chevauche {b_} sur {croise} px")
                else:
                    bon(f"{a_} et {b_} ne se touchent pas")

            # ⚠️ Nos images portent `Cache-Control: immutable` pour UN AN. Une
            # image qui change de contenu sans changer d'URL reste servie par
            # le navigateur du visiteur pendant tout ce temps. Le 2026-08-08,
            # Mongazi voyait encore l'ancienne image générée alors que le
            # serveur envoyait déjà la vraie (MD5 identique au fichier).
            titre("Toute image porte sa marque de version")
            sans = page.evaluate("""() => [...document.querySelectorAll('img')]
                .map(i => i.getAttribute('src') || '')
                .filter(s => s.indexOf('assets/images/') === 0 && s.indexOf('?v=') === -1)""")
            n_img = page.evaluate("() => document.querySelectorAll('img').length")
            bon(f"{n_img} images, toutes versionnées") if not sans \
                else mauvais(f"{len(sans)} image(s) sans ?v= : {sans[:3]}")

            # Le seul contrôle qui regarde vraiment ce qu'il y a SOUS le texte.
            titre("Texte posé sur une photo")
            for nom_, sel_, seuil_ in [("description « pour un lieu »", ".lieux .plein-d", 4.5),
                                       ("titre « pour un lieu »", ".lieux .plein-t", 3.0),
                                       ("description « la visite »", "#visite .plein-d", 4.5),
                                       # le second appel est POSÉ SUR LA PHOTO lui aussi :
                                       # il se mesure comme le reste, pas « à l'œil ».
                                       ("relance « sur mesure »", ".visite-sm", 4.5),
                                       ("bouton « sur mesure »", ".visite-b", 3.0),
                                       ("légende du héros", ".hero-lg", 4.5)]:
                # ⚠️ ON SE PLACE, PUIS ON VÉRIFIE QU'ON Y EST. Le moteur de
                # défilement du site écrit lui aussi dans `scrollY` : couper le
                # lissage et attendre 500 ms ne suffisait pas, la page revenait.
                # Voir `placer()`. Et si on n'y arrive pas, on le DIT avec le
                # chiffre, au lieu de laisser croire à un défaut de contraste.
                ou_ = placer(page, sel_)
                if ou_ is None:
                    mauvais(f"{nom_} : {sel_} introuvable")
                    continue
                vu_ = min(ou_["bas"], ou_["ecran"]) - max(ou_["haut"], 0)
                if vu_ < 0.9 * min(ou_["h"], ou_["ecran"]):
                    mauvais(f"{nom_} : impossible d'amener {sel_} à l'écran "
                            f"(haut {ou_['haut']} px, écran {ou_['ecran']} px) "
                            f"-> le moteur de défilement reprend la main")
                    continue
                r_, quoi_ = fond_derriere(page, sel_)
                if r_ is None:
                    mauvais(f"{nom_} : {quoi_}")
                elif r_ >= seuil_:
                    bon(f"{nom_} : {r_}:1 sur la photo ({quoi_})")
                else:
                    mauvais(f"{nom_} : {r_}:1 < {seuil_} SUR LA PHOTO ({quoi_})")

            titre("Arrivée par le menu")
            # ⚠️ CE CONTRÔLE LIT LE MENU, IL NE RECOPIE PLUS D'ANCRES.
            # Il en portait trois, écrites à la main, dont `#portfolio` : le
            # jour où le menu a changé (2026-08-21, sur le récapitulatif
            # d'Angélique), le contrôle a planté sur un `null.click()` au lieu
            # de tester quoi que ce soit. Une liste recopiée finit toujours par
            # mentir sur ce qu'elle décrit — et un contrôle qui plante ne
            # protège plus rien.
            ancres = page.evaluate("""() => [...document.querySelectorAll('.nav-c a[href^="#"]')]
                .map(a => a.getAttribute('href'))""")
            bon(f"le menu porte {len(ancres)} entrées de page") if len(ancres) >= 4 \
                else mauvais(f"menu trop court : {ancres}")
            for ancre in ancres:
                # ⚠️ UNE ENTRÉE « ACCUEIL » NE SE TESTE PAS DEPUIS LE HAUT.
                # Partir de 0 pour vérifier qu'on arrive à 0 ne prouve rien : le
                # contrôle passerait même si le lien était mort. On part donc du
                # BAS de la page pour celle-là, et du haut pour les autres.
                haut_ = page.evaluate(f"() => document.querySelector('{ancre}') === "
                                      "document.querySelector('main')")
                if haut_:
                    page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                else:
                    page.evaluate("() => window.scrollTo(0, 0)")
                page.wait_for_timeout(600)
                depart_ = page.evaluate("() => Math.round(scrollY)")
                page.evaluate(f"document.querySelector('a[href=\"{ancre}\"]').click()")
                # ⚠️ ON ATTEND QUE LA PAGE SE POSE, ON NE PARIE PAS SUR UN DÉLAI.
                #    Le défilement maison glisse : 1 700 ms suffisaient sur deux
                #    formats et pas sur le troisième, et le contrôle accusait le
                #    site d'un défaut qui n'était qu'une seconde manquante.
                pose, immobile = None, 0
                for _ in range(40):
                    page.wait_for_timeout(150)
                    y_c = page.evaluate("() => Math.round(scrollY)")
                    immobile = immobile + 1 if y_c == pose else 0
                    pose = y_c
                    if immobile >= 3:
                        break

                if haut_:
                    y_ = page.evaluate("() => Math.round(scrollY)")
                    if depart_ < 400:
                        mauvais(f"{ancre} : la page ne descend pas ({depart_} px), "
                                "le retour en haut ne prouve rien")
                    else:
                        bon(f"« accueil » ramène en haut ({depart_} -> {y_} px)") if y_ <= 20 \
                            else mauvais(f"« accueil » laisse la page à {y_} px "
                                         f"(partie de {depart_} px)")
                    continue

                # la première ligne de la section : son étiquette, sinon son titre
                jeu = page.evaluate("""(a) => {
                  const s = document.querySelector(a);
                  if (!s) return null;
                  const l = s.querySelector('.lab') || s.querySelector('h2');
                  if (!l) return null;
                  const n = document.querySelector('.nav').getBoundingClientRect();
                  return Math.round(l.getBoundingClientRect().top - n.bottom);
                }""", ancre)
                if jeu is None:
                    mauvais(f"{ancre} : section ou titre introuvable")
                else:
                    bon(f"{ancre} : le titre respire sous la barre ({jeu} px)") if jeu >= 16 \
                        else mauvais(f"{ancre} : le titre arrive à {jeu} px de la barre fixe")
            page.evaluate("() => window.scrollTo(0, 0)")
            page.wait_for_timeout(400)

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
                # ⚠️ CE CONTRÔLE A BESOIN DU RÉSEAU, et il doit le dire.
                # Les deux familles viennent de Google Fonts. Hors ligne, ou
                # derrière un filtre, AUCUNE ne se charge : le contrôle
                # passait au rouge alors que le site est parfait, et un
                # rapport rouge à tort finit par ne plus être lu.
                # Les DEUX contrôles au-dessus, eux, restent stricts : ils
                # lisent la police DEMANDÉE, qui ne dépend d'aucun réseau.
                if not fam:
                    print("  [~~] polices Google injoignables ici : contrôle du chargement sauté")
                else:
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
                # ⚠️ ON INTERCEPTE `window.open`, ON NE NAVIGUE PAS.
                # Ce contrôle dit « la demande part sur WhatsApp, déjà
                # rédigée » : il doit lire le MESSAGE. En ouvrant vraiment
                # wa.me il testait surtout la connexion — et rendait rouge un
                # site parfait dès qu'on est hors ligne ou derrière un filtre
                # (`chrome-error://chromewebdata/`). Corrigé le 2026-08-21.
                page.evaluate("() => { window.__url = ''; window.open = function (u) { window.__url = u; return null; }; }")
                page.click("#modF button[type=submit]")
                page.wait_for_timeout(200)
                url = page.evaluate("() => window.__url || ''")
                # wa.me redirige vers api.whatsapp.com : les deux formes sont bonnes
                bonNum = ("wa.me/2290152006490" in url) or ("phone=2290152006490" in url)
                bon("la demande part sur WhatsApp, déjà rédigée") if bonNum and "text=" in url \
                    else mauvais(f"la demande ne part pas correctement : {url[:90]}")
                bon("le message reprend les trois réponses") if url.count("%3A") >= 3 \
                    else mauvais("le message ne reprend pas les réponses")
                okv = page.evaluate("() => !document.querySelector('#modOk').hidden")
                bon("le message de confirmation s'affiche") if okv else mauvais("pas de confirmation après envoi")
                page.click("#modX"); page.wait_for_timeout(300)

                titre("Les œuvres")
                # LES SIX PIÈCES, AVEC LEUR CARTEL.
                # ⚠️ Elles sont écrites EN DUR dans la page, pas dans le
                # JavaScript : ce qui fait la valeur de ce site — les textes
                # d'Angélique, les dimensions, les prix — doit rester lisible
                # sans JS et visible pour les moteurs de recherche.
                o = page.evaluate("""() => {
                  const a = [...document.querySelectorAll('.oeu')];
                  return a.map(e => ({
                    t: (e.querySelector('.oeu-t') || {}).textContent || '',
                    dt: [...e.querySelectorAll('.oeu-c dt')].map(x => x.textContent.trim()),
                    dd: [...e.querySelectorAll('.oeu-c dd')].map(x => x.textContent.trim()),
                    situ: !!e.querySelector('.oeu-situ'),
                    texte: [...e.querySelectorAll('.oeu-d p')].length,
                    wa: (e.querySelector('a[href*="wa.me"]') || {}).href || '',
                    alt: (e.querySelector('img') || {}).alt || ''
                  }));
                }""")
                bon(f"{len(o)} œuvres au catalogue") if len(o) == 6 \
                    else mauvais(f"{len(o)} œuvres, six attendues")
                if o:
                    sansCartel = [x["t"] for x in o if len(x["dd"]) < 4]
                    bon("chaque œuvre porte son cartel complet") if not sansCartel \
                        else mauvais(f"cartel incomplet : {sansCartel}")
                    sansPrix = [x["t"] for x in o
                                if not any(("FCFA" in d) or ("demande" in d) for d in x["dd"])]
                    bon("chaque œuvre annonce son prix, ou qu'il est sur demande") if not sansPrix \
                        else mauvais(f"sans prix ni mention : {sansPrix}")
                    sansDim = [x["t"] for x in o if not any("cm" in d for d in x["dd"])]
                    bon("chaque œuvre annonce ses dimensions") if not sansDim \
                        else mauvais(f"sans dimensions : {sansDim}")
                    court = [x["t"] for x in o if x["texte"] < 4]
                    bon("le texte d'Angélique est dans la PAGE, pas dans le script") if not court \
                        else mauvais(f"texte trop court ou absent : {court}")
                    sansWa = [x["t"] for x in o if "wa.me" not in x["wa"] or "text=" not in x["wa"]]
                    bon("chaque œuvre a son lien d'acquisition, déjà rédigé") if not sansWa \
                        else mauvais(f"lien d'acquisition manquant : {sansWa}")
                    sansAlt = [x["t"] for x in o if len(x["alt"]) < 20]
                    bon("chaque œuvre décrit sa photo aux lecteurs d'écran") if not sansAlt \
                        else mauvais(f"texte alternatif trop court : {sansAlt}")
                    # ⚠️ LE CARTEL DE L'HONNÊTETÉ. Les masques sont d'Angélique,
                    #    les niches de marbre sont des rendus. Trois des six
                    #    photos sont des mises en situation, et le disent.
                    nSitu = sum(1 for x in o if x["situ"])
                    bon(f"{nSitu} photos annoncent « mise en situation »") if nSitu >= 3 \
                        else mauvais(f"seulement {nSitu} mise(s) en situation annoncée(s)")

                titre("Les créations personnalisées")
                # LA SECTION EXISTE, ET ELLE DIT LA DISTINCTION.
                # Le brief d'Angélique l'exige en toutes lettres : une
                # collection existe déjà, une création personnalisée naît de
                # l'histoire du client. Le contrôle lit les DEUX blocs.
                sec = page.evaluate("""() => {
                  const s = document.getElementById('personnalise');
                  if (!s) return null;
                  const d = [...s.querySelectorAll('.deux li b')].map(e => e.textContent.trim());
                  return {titre: (s.querySelector('h2') || {}).textContent || '',
                          deux: d, ent: !!s.querySelector('.ent path'),
                          cta: !!s.querySelector('[data-perso]'),
                          wa: !!s.querySelector('a[href*="wa.me"]')};
                }""")
                if not sec:
                    mauvais("la section des créations personnalisées est absente")
                else:
                    bon("la section « créations personnalisées » est là") if "histoire" in sec["titre"].lower() \
                        else mauvais(f"titre inattendu : {sec['titre'][:50]}")
                    bon(f"la distinction avec les collections est écrite ({len(sec['deux'])} blocs)") \
                        if len(sec["deux"]) == 2 else mauvais(f"distinction incomplète : {sec['deux']}")
                    bon("la signature « l'entaille » est présente") if sec["ent"] \
                        else mauvais("pas de signature dans cette section")
                    bon("sans JavaScript, un vrai lien WhatsApp reste") if sec["wa"] \
                        else mauvais("aucun lien WhatsApp écrit en dur dans la section")

                # LE FORMULAIRE EN TROIS TEMPS, PARCOURU COMME UNE VISITEUSE
                page.click("[data-perso]"); page.wait_for_timeout(400)
                e = page.evaluate("""() => ({
                  vis: [...document.querySelectorAll('#perF .etp')].filter(x => !x.hidden).length,
                  precise: !document.getElementById('pTypeAW').hidden,
                  dims: !document.getElementById('pDimW').hidden
                })""")
                bon("une seule étape à la fois") if e["vis"] == 1 else mauvais(f"{e['vis']} étapes visibles d'un coup")
                # ⚠️ `hidden` ne cache rien quand un `display` est déclaré :
                #    ces deux champs conditionnels l'avaient appris à leurs
                #    dépens (capture du 2026-08-21).
                bon("les champs conditionnels restent cachés tant qu'on n'en a pas besoin") \
                    if not e["precise"] and not e["dims"] else mauvais(f"champ conditionnel visible à tort : {e}")

                page.click("#perSuiv"); page.wait_for_timeout(250)
                bloque = page.evaluate("() => !document.getElementById('perE').hidden")
                bon("sans histoire, on ne passe pas à la suite") if bloque \
                    else mauvais("le premier temps se franchit sans avoir rien raconté")

                page.fill("#pHist", "Le pagne indigo de ma grand-mère, et la maison de Ouidah.")
                page.select_option("#pType", label="Autre"); page.wait_for_timeout(150)
                pre = page.evaluate("() => !document.getElementById('pTypeAW').hidden")
                bon("« Autre » fait apparaître le champ à préciser") if pre \
                    else mauvais("le champ à préciser ne s'ouvre pas")
                page.click("#perSuiv"); page.wait_for_timeout(300)
                # ⚠️ on remplit CE QUI EST À L'ÉCRAN : `#pCoul` vit au deuxième
                #    temps, et un champ caché ne se remplit pas.
                page.fill("#pCoul", "indigo et terre")
                page.click("#perSuiv"); page.wait_for_timeout(300)
                t3 = page.evaluate("""() => ({
                  etp: (document.querySelector('#perF .etp:not([hidden])') || {}).dataset,
                  go: !document.getElementById('perGo').hidden
                })""")
                bon("le troisième temps porte le bouton d'envoi") if t3["go"] \
                    else mauvais("pas de bouton d'envoi au troisième temps")

                page.click("#perGo"); page.wait_for_timeout(200)
                sansNom = page.evaluate("() => !document.getElementById('perE').hidden")
                bon("sans nom, la demande ne part pas") if sansNom \
                    else mauvais("la demande part sans nom")

                page.fill("#pNom", "Awa Kponou")
                page.fill("#pTel", "+229 97 00 00 00")
                page.evaluate("() => { window.__u2 = ''; window.open = function (u) { window.__u2 = u; return null; }; }")
                page.click("#perGo"); page.wait_for_timeout(250)
                u2 = page.evaluate("() => window.__u2 || ''")
                from urllib.parse import unquote
                msg = unquote(u2.split("text=", 1)[1]) if "text=" in u2 else ""
                bon("le projet part sur WhatsApp, déjà rédigé") \
                    if ("wa.me/2290152006490" in u2 or "phone=2290152006490" in u2) and msg \
                    else mauvais(f"le projet ne part pas correctement : {u2[:80]}")
                # ⚠️ LE MESSAGE DOIT PORTER LES RÉPONSES, PAS UN GABARIT VIDE.
                #    Sans base de données derrière, ce message EST la demande :
                #    le nom et la date y sont, comme le brief le demande.
                manquants = [x for x in ("pagne indigo", "Awa Kponou", "indigo et terre",
                                         "MON HISTOIRE", "MA VISION", "MON PROJET",
                                         "Demande envoyée le") if x not in msg]
                bon(f"le message porte l'histoire, le nom et la date ({len(msg)} caractères)") \
                    if not manquants else mauvais(f"le message oublie : {manquants}")
                okv = page.evaluate("() => !document.getElementById('perOk').hidden")
                bon("la confirmation « votre projet a bien été transmis » s'affiche") if okv \
                    else mauvais("pas de confirmation après envoi du projet")
                page.click("#perX"); page.wait_for_timeout(300)

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

                # ⚠️ CE CONTRÔLE A BESOIN D'UN TÉMOIN. Sans lui, il passerait
                # aussi le jour où le moteur de défilement serait mort : une
                # page qui ne glisse pas ne ramène évidemment rien. On prouve
                # donc d'abord QUE ÇA GLISSE, puis on saute par-dessus.
                # (Le moteur n'existe que sur pointeur fin : c'est ici, en
                # contexte PC, et nulle part ailleurs.)
                titre("Le défilement lissé laisse passer les autres")
                page.evaluate("() => window.scrollTo(0, 3000)")
                page.wait_for_timeout(700)
                depart = page.evaluate("() => Math.round(scrollY)")
                page.mouse.move(700, 400)
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(120)
                pendant = page.evaluate("() => Math.round(scrollY)")
                if pendant - depart > 60:
                    bon(f"témoin : la page glisse bien ({depart} -> {pendant} px)")
                    # on saute AILLEURS que sur son chemin : il doit céder
                    page.evaluate("() => window.scrollTo(0, 200)")
                    page.wait_for_timeout(900)
                    apres = page.evaluate("() => Math.round(scrollY)")
                    bon(f"un saut extérieur pendant le glissement tient ({apres} px)") \
                        if apres < 500 else \
                        mauvais(f"le moteur a ramené la page à {apres} px : un scrollIntoView "
                                "venu de la recherche du navigateur ou d'un lecteur d'écran "
                                "est annulé")
                else:
                    mauvais(f"témoin muet : la page n'a pas glissé ({depart} -> {pendant} px), "
                            "le contrôle ne prouve rien")
                page.evaluate("() => window.scrollTo(0, 0)")
                page.wait_for_timeout(600)

                if VOIR: capturer(page, "pc")

            ctx.close()

        titre("Sans JavaScript")
        ctx = nav.new_context(viewport={"width": 390, "height": 844}, is_mobile=True,
                              has_touch=True, java_script_enabled=False)
        page = ctx.new_page()
        page.goto(BASE, wait_until="load")
        page.wait_for_timeout(900)
        txt = page.inner_text("main")
        # ⚠️ LES ÉTIQUETTES SE LISENT DANS LA PAGE, ELLES NE SE RECOPIENT PAS.
        # La liste portait « LA DÉMARCHE », « L'ATELIER », « DANS UN LIEU » en
        # dur : le jour où Angélique a donné SON vocabulaire (2026-08-21), le
        # contrôle a accusé le site d'avoir perdu des textes qu'il n'avait
        # jamais perdus — il avait seulement changé de mots. Même famille que
        # le contrôle du menu qui plantait sur une ancre recopiée.
        # Ce qui reste écrit ici, ce sont les PHRASES d'Angélique : celles-là
        # ne doivent jamais disparaître, quel que soit le vocabulaire du menu.
        etiquettes = page.evaluate(
            "() => [...document.querySelectorAll('main .lab')].map(e => e.textContent.trim())")
        bon(f"sans JS : les {len(etiquettes)} étiquettes de section sont là") \
            if len(etiquettes) >= 4 and all(len(e) > 4 for e in etiquettes) \
            else mauvais(f"sans JS : étiquettes manquantes ou vides : {etiquettes}")
        for att in ["ANGY", "par sa main", "La forme", "Le trait", "Retrouvons-nous",
                    "ÉNERGIES", "Votre histoire"]:
            bon(f"sans JS : « {att} » reste lisible") if att in txt \
                else mauvais(f"sans JS : « {att} » a disparu")
        # ⚠️ SANS SCRIPT, LE PANNEAU NE S'OUVRE PAS : le bouton « DÉCOUVRIR »
        #    se retire, et le sommaire redevient une rangée de liens dans une
        #    barre qui ne flotte plus. Ce qui se contrôle ici, c'est qu'il
        #    reste une navigation, pas qu'elle soit belle.
        sansjs_ = page.evaluate("""() => {
          const as = [...document.querySelectorAll('.nav-c a')].filter(a => {
            const r = a.getBoundingClientRect();
            return r.width > 0 && r.height > 0 && r.right <= innerWidth + 1 && r.left > -1;
          });
          const b = document.querySelector('#dec');
          return { liens: as.length,
                   bouton: b ? getComputedStyle(b).display : 'absent',
                   flotte: getComputedStyle(document.querySelector('#nav')).position };
        }""")
        bon(f"sans JS : les {sansjs_['liens']} entrées du sommaire restent atteignables") \
            if sansjs_["liens"] >= 7 \
            else mauvais(f"sans JS : plus que {sansjs_['liens']} entrées atteignables")
        bon("sans JS : le bouton « DÉCOUVRIR » se retire au lieu de ne rien faire") \
            if sansjs_["bouton"] == "none" \
            else mauvais(f"sans JS : le bouton reste ({sansjs_['bouton']}) et n'ouvre rien")
        bon("sans JS : la barre ne flotte pas au-dessus du texte") \
            if sansjs_["flotte"] == "static" \
            else mauvais(f"sans JS : la barre est en {sansjs_['flotte']} sans fond posé")

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


# ⚠️ ON NE RECOPIE PAS LA LISTE DES SECTIONS. Elle en portait huit, écrites à
# la main : les deux sections ajoutées pour Angélique (les œuvres, le
# sur-mesure) n'ont JAMAIS été photographiées, et personne ne l'a vu — les
# captures ne se plaignent pas de ce qu'elles ne montrent pas. Troisième fois
# que la même famille de défaut sort ici le 2026-08-21.
SECTIONS = "section, .pied"

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

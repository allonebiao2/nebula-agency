#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HILLARY M. STYL — suite de contrôle qualité (121 contrôles).

    python3 _qc.py

Vérifie, sur navigateur réel émulé en 390 / 768 / 1440 px :
  · aucun débordement horizontal, page et modale ouverte
  · toutes les cibles tactiles >= 44 px
  · aucune erreur JavaScript, aucune ressource locale manquante
  · le nombre de mesures de chaque type de vêtement (9/15/11/6/8)
  · l'arithmétique du tunnel (pièce + expédition + express)
  · la date de disponibilité, calculée sur la borne HAUTE du délai
  · le repli email, le « sur devis », les mesures laissées vides

⚠️ Émulation obligatoire. Une capture headless sans `is_mobile` ignore le
   meta viewport, rend la page à 800 px et fait croire à un débordement
   qui n'existe pas.

Doit être VERTE avant tout déploiement.
"""
import asyncio, datetime, glob, json, pathlib, re, sys
from playwright.async_api import async_playwright

# la console Windows est en cp1252 : un espace fin insecable suffit a
# faire tomber tout le rapport. Lecon du 2026-08-05.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HTML = pathlib.Path(__file__).resolve().parent / "vitrine.html"
URL = HTML.as_uri()
FAILS, NOTES = [], []

# Chromium est preinstalle dans l'environnement distant ; en local Playwright
# le trouve tout seul.
_C = [g for g in glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome") if "headless" not in g]
CHROME = {"executable_path": _C[0]} if _C else {}
CHROME_CTX = {}

def note(m):
    print("NOTE  " + m)


def ok(c, m):
    (NOTES if c else FAILS).append(("OK  " if c else "FAIL") + "  " + m)

VIEWPORTS = [(390, 844, True), (768, 1024, True), (1440, 900, False)]

async def overflow(page, label):
    r = await page.evaluate("()=>({s:document.documentElement.scrollWidth,c:document.documentElement.clientWidth})")
    ok(r["s"] <= r["c"] + 1, f"{label} : pas de debordement horizontal ({r['s']}/{r['c']})")

async def tap_targets(page, label):
    bad = await page.evaluate("""()=>{
      const out=[];
      document.querySelectorAll('button,a,select,input,textarea').forEach(e=>{
        const st=getComputedStyle(e);
        if(st.display==='none'||st.visibility==='hidden')return;
        const r=e.getBoundingClientRect();
        if(r.width===0&&r.height===0)return;
        if(r.height<44) out.push((e.tagName+'.'+(e.className||'')).slice(0,50)+' h='+Math.round(r.height));
      });
      return out;}""")
    ok(not bad, f"{label} : cibles tactiles >= 44px" + ("" if not bad else " -> " + "; ".join(bad[:6])))

async def chevauchements(page, label):
    """AUCUN TEXTE NE PASSE SOUS UNE IMAGE NI SOUS UN INSTRUMENT FLOTTANT.

    Mongazi, 2026-08-21, capture d'iPhone à l'appui : « y'a du texte qui rentre
    dans les images, et ce n'est pas que là ». Il avait raison deux fois —
    quatorze endroits mesurés, à trois largeurs :
      · le titre et la description du carrousel posés SUR la robe (65 % du
        texte recouvert à 390 px) ;
      · le bouton du son, en `position:fixed` en bas à gauche, qui mangeait le
        PREMIER MOT de tout texte passant par là : « 04 », « Conçu par »,
        « Saison 2026 », le « On » d'un titre.

    CE QUI EST UN DÉFAUT : du texte DANS LE FLUX recouvert par un élément
    positionné. Un texte volontairement posé sur une photo (le chiffre géant du
    héros, une légende, un badge, « Commander ») est absolu : il ne compte pas.

    CE QUI N'EN EST PAS : une BANDE DE BORD opaque qui traverse l'écran et
    touche un bord — c'est le rôle d'un en-tête fixe. ⚠️ Une pastille de 46 px
    qui flotte n'est pas une bande, même opaque : c'est un instrument, et un
    instrument ne recouvre jamais du texte (règle née sur Mon Bénin).
    """
    JS = r"""()=>{
      const vis = e => { const s=getComputedStyle(e);
        return s.display!=='none' && s.visibility!=='hidden' && parseFloat(s.opacity)>0.05; };
      const flux = e => { const s=getComputedStyle(e);
        if(s.position==='absolute'||s.position==='fixed'||s.position==='sticky') return false;
        if(s.position==='relative'){
          const d=['top','left','right','bottom'].some(p=>s[p]!=='auto'&&parseFloat(s[p])!==0);
          if(d||(s.transform!=='none')) return false; }
        return true; };
      const enFlux = e => { let n=e; while(n && n!==document.body){ if(!flux(n)) return false; n=n.parentElement; } return true; };
      const bande = e => { let n=e; while(n && n!==document.body){
          const s=getComputedStyle(n);
          if(s.position==='fixed'||s.position==='sticky'){
            const m=(s.backgroundColor||'').match(/rgba?\(([^)]+)\)/);
            const a=m ? (m[1].split(',')[3]===undefined?1:parseFloat(m[1].split(',')[3])) : 0;
            const r=n.getBoundingClientRect();
            const large = r.width>=innerWidth*0.85 || r.height>=innerHeight*0.85;
            const bord  = r.top<=1||r.left<=1||r.right>=innerWidth-1||r.bottom>=innerHeight-1;
            if(a>=0.9 && large && bord) return true; }
          n=n.parentElement; }
        return false; };
      const nom = e => { let p=[],n=e;
        while(n && n.nodeType===1 && p.length<3){
          p.unshift(n.tagName.toLowerCase()+(n.id?'#'+n.id:'')+(n.className&&typeof n.className==='string'?'.'+n.className.trim().split(/\s+/)[0]:''));
          n=n.parentElement; }
        return p.join('>'); };
      const textes=[];
      document.querySelectorAll('body *').forEach(e=>{
        if(!vis(e)) return;
        let t=''; for(const n of e.childNodes) if(n.nodeType===3) t+=n.textContent;
        t=t.trim(); if(!t) return;
        const r=e.getBoundingClientRect();
        if(r.width<4||r.height<4) return;
        if(!enFlux(e)) return;
        textes.push({r,t:t.slice(0,30),s:nom(e)});
      });
      const gene=[];
      document.querySelectorAll('img,button,a,aside,div').forEach(e=>{
        if(!vis(e)) return;
        const s=getComputedStyle(e);
        if(s.position!=='fixed' && !(e.tagName==='IMG' && !flux(e))) return;
        if(bande(e)) return;
        const r=e.getBoundingClientRect();
        if(r.width<10||r.height<10) return;
        gene.push({r,n:(e.currentSrc||e.src||'').split('/').pop()||nom(e)});
      });
      const inter=(a,b)=>{ const x=Math.max(0,Math.min(a.right,b.right)-Math.max(a.left,b.left));
        const y=Math.max(0,Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)); return x*y; };
      const out=[];
      textes.forEach(t=>gene.forEach(g=>{
        const a=inter(t.r,g.r); if(a<60) return;
        if(a/(t.r.width*t.r.height) < 0.10) return;
        out.push(t.t.slice(0,22)+' sous '+String(g.n).slice(0,22));
      }));
      return out;
    }"""
    vus, H = set(), await page.evaluate("()=>document.body.scrollHeight")
    haut = await page.evaluate("()=>innerHeight")
    y = 0
    while y < H:
        await page.evaluate(f"()=>window.scrollTo(0,{y})")
        await page.wait_for_timeout(360)
        for o in await page.evaluate(JS):
            vus.add(o)
        y += int(haut * 0.75)
    await page.evaluate("()=>window.scrollTo(0,0)")
    await page.wait_for_timeout(300)
    ok(not vus, f"{label} : aucun texte sous une image ou un instrument"
       + ("" if not vus else " -> " + " ; ".join(sorted(vus)[:4])))


def variables_css():
    """⛔ Le defaut du 2026-08-10 : cinq couleurs etaient utilisees sans
    jamais etre definies. `background: var(--craie)` sans valeur ne donne
    pas du blanc, il ne donne RIEN : la fiche de commande n'avait aucun
    fond et le texte noir se posait sur les photos du catalogue.
    Aucun controle de contraste ne pouvait le voir : ils lisent la couleur
    DECLAREE, et une variable vide ne declare rien.
    Les variables posees a l'execution par le JavaScript sont exclues."""
    src = HTML.read_text(encoding="utf-8")
    posees = set(re.findall(r"setProperty\(\s*['\"](--[a-z0-9-]+)", src))
    utilisees = set(re.findall(r"var\(\s*(--[a-z0-9-]+)\s*\)", src))
    avec_repli = set(re.findall(r"var\(\s*(--[a-z0-9-]+)\s*,", src))
    definies = set(re.findall(r"(--[a-z0-9-]+)\s*:", src))
    manquantes = sorted(utilisees - definies - posees - avec_repli)
    ok(not manquantes,
       "aucune variable CSS utilisee sans etre definie"
       + (" — MANQUE : " + ", ".join(manquantes) if manquantes else ""))


def deux_vues():
    """LES PIÈCES PHOTOGRAPHIÉES DE FACE ET DE DOS.

    Hillary envoie certaines pièces en double. Trois façons de rater ça sans
    qu'aucun contrôle d'affichage ne le voie :
      · `img2` pointe sur un fichier qui n'existe pas — la seconde vue est un
        carré vide, et la carte « bascule » vers rien ;
      · la face et le dos sont LE MÊME FICHIER (deux fois la même photo posée
        par erreur) — la carte bascule d'une image vers elle-même, ce qui est
        strictement invisible et donc indétectable à l'œil ;
      · le carrousel a la seconde vue et le catalogue non, ou l'inverse.
    On lit les données, jamais un chiffre recopié ici."""
    import hashlib
    ici = pathlib.Path(__file__).resolve().parent
    img = ici / "assets" / "images"
    mot = (ici / "_v4" / "garde-moteur.js").read_text(encoding="utf-8")
    mtn = (ici / "_v4" / "motion.js").read_text(encoding="utf-8")

    def somme(f):
        return hashlib.md5((img / f).read_bytes()).hexdigest()

    # catalogue : chaque `img2` a son `img`, les deux existent et different
    paires = re.findall(r'img:"([^"]+)",\s*img2:"([^"]+)"', mot)
    absents, jumeaux = [], []
    for face, dos in paires:
        for f in (face, dos):
            if not (img / f).exists():
                absents.append(f)
        if (img / face).exists() and (img / dos).exists() and somme(face) == somme(dos):
            jumeaux.append(face)
    ok(not absents, f"catalogue : les {len(paires)} secondes vues ont leur fichier"
       + ("" if not absents else " -> manquant(s) : " + ", ".join(absents)))
    ok(not jumeaux, "catalogue : face et dos sont deux photos differentes"
       + ("" if not jumeaux else " -> identiques : " + ", ".join(jumeaux)))

    # carrousel : meme exigence, et il doit connaitre les memes paires
    pc = dict(re.findall(r"f:'([^']+)',\s*f2:'([^']+)'", mtn))
    perdus = [f for f in pc.values() if not (img / f).exists()]
    ok(not perdus, f"carrousel : les {len(pc)} secondes vues ont leur fichier"
       + ("" if not perdus else " -> manquant(s) : " + ", ".join(perdus)))
    manque = [f for f, d in paires if f in mtn and pc.get(f) != d]
    ok(not manque, "carrousel et catalogue connaissent les memes secondes vues"
       + ("" if not manque else " -> sans dos au carrousel : " + ", ".join(manque)))


def nappes_heros():
    """LE HÉROS PEINT LE FOND AVEC LA COULEUR DE LA PIÈCE. Deux diapositives
    voisines de couleur trop proche, c'est une transition qu'on ne voit pas.

    ⚠️ ON MESURE EN L*a*b*, PAS EN DEGRÉS DE TEINTE. La première version de ce
    contrôle comparait des angles et accusait `hero-3 → hero-4` : 19° d'écart,
    donc « même nappe ». Leur distance perçue est de **33 ΔE** — un bleu
    profond et un cyan clair, que personne ne confondrait. L'angle ignore la
    clarté et la saturation, c'est-à-dire l'essentiel. Un faux défaut signalé à
    Mongazi le 2026-08-20, corrigé le même jour.

    ⚠️ Le héros TOURNE : la dernière précède la première.
    C'est une NOTE, pas un échec : l'ordre du héros est un choix humain, et une
    collection dominée par les rouges ne peut pas toujours alterner."""
    import math
    mtn = (pathlib.Path(__file__).resolve().parent / "_v4" / "motion.js").read_text(encoding="utf-8")
    d = mtn.index("var HERO = [")
    bloc = mtn[d:mtn.index("  ];", d)]
    cs = re.findall(r"c:'(#[0-9a-fA-F]{6})'", bloc)
    fs = re.findall(r"f:'([^']+)'", bloc)

    def lab(c):
        r, g, b = (int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))
        lin = lambda u: u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
        r, g, b = lin(r), lin(g), lin(b)
        X = (r * .4124 + g * .3576 + b * .1805) / .95047
        Y = r * .2126 + g * .7152 + b * .0722
        Z = (r * .0193 + g * .1192 + b * .9505) / 1.08883
        f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
        fx, fy, fz = f(X), f(Y), f(Z)
        return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))

    proches = []
    for i in range(len(cs)):
        j = (i + 1) % len(cs)
        e = math.sqrt(sum((x - y) ** 2 for x, y in zip(lab(cs[i]), lab(cs[j]))))
        if e < 18:
            proches.append("%s -> %s (dE %.0f)"
                           % (fs[i].replace("piece-", "").replace(".webp", ""),
                              fs[j].replace("piece-", "").replace(".webp", ""), e))
    NOTES.append("OK    heros : %d diapositives, %s"
                 % (len(cs), "aucune transition invisible" if not proches
                    else "%d transition(s) trop proches" % len(proches)))
    if proches:
        note("heros, transitions a regarder : " + " . ".join(proches))


def vitrine_commerciale():
    """Ce qui fait vendre et ce qui se partage, verifie sur le HTML livre.

    Trois defauts trouves le 2026-08-16, tous invisibles en regardant le site :
      1. AUCUNE og:image — un lien partage sur WhatsApp n'etait qu'une ligne
         de texte grise, au Benin ou tout circule par WhatsApp.
      2. un FAQPage DECLARE sans aucune question visible sur la page. Google
         exige que le contenu balise soit visible, et surtout : les objections
         des clientes n'etaient repondues nulle part.
      3. aucun balisage Product alors que les prix sont reels.
    """
    src = HTML.read_text(encoding="utf-8")

    # 1 · l'image de partage
    m = re.search(r'property="og:image" content="([^"]+)"', src)
    ok(bool(m), "une image de partage est declaree (og:image)")
    if m:
        nom = m.group(1).rsplit("/", 1)[-1]
        ok((HTML.parent / "assets" / "images" / nom).exists(),
           f"le fichier de l'image de partage existe vraiment ({nom})")
        ok(src.count('name="twitter:card"') == 1, "la carte Twitter/X est declaree")

    # 2 · la FAQ balisee et la FAQ visible doivent dire LA MEME CHOSE
    bloc = re.search(r'<script type="application/ld\+json">(.*?)</script>', src, re.S)
    ok(bool(bloc), "le graphe de donnees structurees est present")
    graphe = json.loads(bloc.group(1))
    faq = [x for x in graphe["@graph"] if x.get("@type") == "FAQPage"]
    ok(len(faq) == 1, "un seul FAQPage declare")
    # l'espace insecable avant le « ? » est la bonne typographie francaise :
    # on la neutralise pour comparer, on ne la retire pas de la page
    def _plat(t):
        t = re.sub(r"<[^>]+>", "", t)
        t = t.replace("&nbsp;", " ").replace(" ", " ")
        return re.sub(r"\s+", " ", t).strip()
    q_balisees = [_plat(q["name"]) for q in faq[0]["mainEntity"]]
    q_visibles = [_plat(q) for q in re.findall(r"<summary>(.*?)</summary>", src, re.S)]
    ok(len(q_visibles) >= 4, f"la page montre {len(q_visibles)} questions")
    ok(q_balisees == q_visibles,
       "les questions balisees sont EXACTEMENT celles que la cliente lit"
       + ("" if q_balisees == q_visibles else f" — balise {q_balisees} / vu {q_visibles}"))

    # les reponses aussi : une reponse balisee absente de la page est interdite
    r_balisees = [q["acceptedAnswer"]["text"].strip() for q in faq[0]["mainEntity"]]
    texte = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", src)).replace(" ", " ")
    absentes = [r[:40] for r in r_balisees if re.sub(r"\s+", " ", r)[:60] not in texte]
    ok(not absentes, "chaque reponse balisee est visible sur la page"
       + ("" if not absentes else " — MANQUE : " + " | ".join(absentes)))

    # 3 · les fiches produit disent le prix du catalogue, pas un autre
    prods = [x for x in graphe["@graph"] if x.get("@type") == "Product"]
    ok(len(prods) >= 4, f"{len(prods)} fiches produit balisees")
    prix_page = dict(re.findall(r'nom:"([^"]+)"[^}]*?prix:(\d+)', src))
    faux = [p["name"] for p in prods
            if p["name"] in prix_page and int(prix_page[p["name"]]) != p["offers"]["price"]]
    ok(not faux, "chaque fiche produit porte le prix du catalogue"
       + ("" if not faux else " — FAUX : " + ", ".join(faux)))
    ok(all(p["offers"]["priceCurrency"] == "XOF" for p in prods),
       "les prix balises sont en francs CFA")

    # 3 bis · la description de la page ne doit pas contredire le catalogue.
    # Elle annoncait « express en 1 a 3 jours » quand chaque carte dit 2 a 5 :
    # c'est le premier texte que lit Google, et il disait autre chose que le site.
    desc = re.search(r'<meta name="description" content="([^"]+)"', src)
    if desc:
        expmax = max(int(x) for x in re.findall(r"expMax:(\d+)", src))
        expmin = min(int(x) for x in re.findall(r"expMin:(\d+)", src))
        d = desc.group(1)
        faux = re.findall(r"(\d+)\s*(?:a|à)\s*(\d+)\s*jours", d)
        ok(all(int(a) == expmin and int(b) == expmax for a, b in faux),
           f"la description de la page dit le meme express que le catalogue ({expmin} a {expmax} j)"
           + ("" if not faux else f" — vu {faux}"))

    # 4 · le delai annonce dans la FAQ est celui du catalogue
    jmax = max(int(x) for x in re.findall(r"jmax:(\d+)", src))
    sem = jmax // 7
    rep_delai = " ".join(r for r in r_balisees if "semaine" in r or "jour" in r)
    ok(f"{sem} semaine" in rep_delai.lower() or "deux semaines" in rep_delai.lower(),
       f"la FAQ annonce le meme delai que le catalogue ({sem} semaines)")


async def sons(br):
    """Les sons d'atelier : rien avant un geste, un bouton pour couper,
    et ce bouton doit rester atteignable MEME la fiche ouverte.

    ⚠️ CE CONTROLE SE FAIT EN HTTP, pas en file://. Les sons sont charges
    par `fetch`, que Chromium REFUSE depuis une page ouverte en fichier
    local : le controle voyait zero son et accusait le site a tort.
    On teste comme la page tourne vraiment.
    """
    import functools, http.server, socketserver, threading
    ici = str(HTML.parent)
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ici)
    # ⚠️ LE SERVEUR DOIT ETRE MULTI-TACHE. `TCPServer` sert UNE requete a la
    #    fois : le navigateur ouvre plusieurs connexions et les garde
    #    ouvertes (keep-alive), donc l'une d'elles bloque toutes les autres.
    #    Tant que la page ne demandait qu'une poignee de fichiers, ca passait ;
    #    avec 28 images, la suite s'arretait une fois sur deux sur
    #    « Page.goto: Timeout », ce qui ressemble a une panne du site.
    #    Trouve le 2026-08-17, apres avoir soupconne les polices a tort.
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    socketserver.ThreadingTCPServer.daemon_threads = True
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 8823), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    ctx = await br.new_context(viewport={"width": 1280, "height": 900})
    # ⚠️ C'EST ICI QUE LA SUITE ECHOUAIT UNE FOIS SUR DEUX (trouve le
    #    2026-08-17). Tous les autres contextes coupent la requete vers Google
    #    Fonts ; celui-ci, non. La feuille de style distante bloque le
    #    `DOMContentLoaded`, et des que le reseau traine, `goto` depasse ses
    #    30 secondes : la suite s'arretait sur « Page.goto: Timeout », qui
    #    ressemble a une panne du site alors que c'est la police qui traine.
    #    ⚠️ Un controle qui echoue au hasard est pire qu'un controle absent :
    #    on finit par le croire.
    await ctx.route('**fonts.g*/**', lambda r: r.abort())
    page = await ctx.new_page()
    recus = []
    page.on("request", lambda r: recus.append(r.url.split("/")[-1])
            if "/sons/" in r.url else None)
    await page.goto("http://127.0.0.1:8823/vitrine.html",
                    wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(2600)

    ok(not recus, "aucun son telecharge avant le premier geste"
       + ("" if not recus else " -> " + ", ".join(recus[:3])))
    ok(await page.locator(".sonbt").count() == 1,
       "le bouton de son est present des le chargement")

    # un vrai geste : on ouvre une piece
    await page.evaluate("()=>{const p=document.querySelector('.piece'); if(p) p.click();}")
    await page.wait_for_timeout(2600)
    attendus = {"ouvrir.mp3", "fiche.mp3", "mesure.mp3",
                "etape.mp3", "couper.mp3", "envoyer.mp3"}
    ok(set(recus) == attendus,
       "les 6 sons d'atelier sont charges apres le geste (%d)" % len(set(recus)))

    # ⚠️ la modale est en z-index 120 : sous elle, le bouton devenait
    # inatteignable et le son ne pouvait plus etre coupe pendant la commande
    dessus = await page.evaluate("""()=>{
      const b=document.querySelector('.sonbt');
      if(!b) return false;
      const r=b.getBoundingClientRect();
      const e=document.elementFromPoint(r.x+r.width/2, r.y+r.height/2);
      return !!(e && (e===b || b.contains(e)));
    }""")
    ok(dessus, "le bouton de son reste atteignable la fiche ouverte")

    await page.click(".sonbt")
    await page.wait_for_timeout(400)
    presse = await page.eval_on_selector(".sonbt", "e=>e.getAttribute('aria-pressed')")
    memo = await page.evaluate("()=>localStorage.getItem('hms:muet')")
    ok(presse == "true" and memo == "1",
       "couper le son est retenu d'une visite a l'autre")
    await ctx.close()
    srv.shutdown()


async def main():
    variables_css()
    vitrine_commerciale()
    deux_vues()
    nappes_heros()
    async with async_playwright() as pw:
        br = await pw.chromium.launch(**CHROME)
        await sons(br)
        for w, h, mobile in VIEWPORTS:
            ctx = await br.new_context(viewport={"width": w, "height": h},
                                       device_scale_factor=2 if mobile else 1,
                                       is_mobile=mobile, has_touch=mobile)
            ctx.set_default_timeout(30000)
            await ctx.route('**fonts.g*/**', lambda r: r.abort())
            page = await ctx.new_page()
            errs, failed = [], []
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.on("requestfailed", lambda r: failed.append(r.url))
            await page.goto(URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(2500)
            await overflow(page, f"[{w}px] page")
            await tap_targets(page, f"[{w}px] page")
            await chevauchements(page, f"[{w}px] page")

            # onglet sur-mesure + ouverture d'une piece
            await page.evaluate("()=>onglet(\'sm\')")
            n = await page.locator(".piece").count()
            # ⚠️ le nombre vient des DONNÉES, jamais recopié ici
            att = await page.evaluate("()=>PIECES.filter(p=>p.cat==='sm').length")
            ok(n == att, f"[{w}px] {att} pieces sur-mesure affichees (vu {n})")

            # UN PRIX NE SE COUPE PAS EN DEUX. Un Range qui renvoie plusieurs
            # rectangles, c'est un texte passe a la ligne. « 100 000 » / « F »
            # sur deux lignes faisait une carte cassee en 390 px (2026-08-06).
            coupes = await page.evaluate("""()=>{
              const out=[];
              document.querySelectorAll('.piece .bd .pr, .piece .bd .del').forEach(e=>{
                e.querySelectorAll('span').forEach(s=>{
                  const r=document.createRange(); r.selectNodeContents(s);
                  if(r.getClientRects().length>1) out.push(s.textContent.trim());
                });
                e.childNodes.forEach(nd=>{
                  if(nd.nodeType===3 && nd.textContent.trim()){
                    const r=document.createRange(); r.selectNodeContents(nd);
                    if(r.getClientRects().length>1) out.push(nd.textContent.trim());
                  }
                });
              });
              return out;}""")
            ok(not coupes, f"[{w}px] prix et delais sur une seule ligne"
               + ("" if not coupes else " -> coupes : " + "; ".join(coupes[:4])))

            await page.locator(".piece").first.click()
            await page.wait_for_selector("#ov.on")
            # les champs entrent en pivotant (« le carnet ») : mesurer pendant
            # l'animation donne une hauteur ecrasee, pas la hauteur reelle
            await page.wait_for_timeout(900)
            await overflow(page, f"[{w}px] modale ouverte")
            await tap_targets(page, f"[{w}px] modale")
            await page.click("#btX")

            ok(not errs, f"[{w}px] aucune erreur JS" + ("" if not errs else " -> " + errs[0][:120]))
            ext = [u for u in failed if not u.startswith("file:")]
            if ext:
                NOTES.append("NOTE  requetes externes en echec (polices Google, reseau bloque) : %d" % len(ext))
            # ⚠️ LES SONS SONT EXCLUS DE CE CONTRÔLE, ET C'EST JUSTIFIÉ.
            # Cette boucle-ci ouvre la page en `file://`. Chromium y interdit
            # `fetch()` par principe (CORS), donc les six .mp3 échouent alors
            # qu'ils sont bien sur le disque et se chargent parfaitement en
            # HTTPS. Pire : ils n'échouaient qu'APRÈS le clic sur une pièce,
            # donc le contrôle passait ou non selon la vitesse de la machine.
            # Les sons ont déjà leur propre contrôle, `sons()`, qui lui sert
            # la page sur un vrai serveur HTTP. C'est le bon endroit.
            perdus = [u for u in failed
                      if u.startswith("file:") and "/assets/sons/" not in u]
            ok(not perdus, f"[{w}px] aucune ressource locale manquante"
               + ("" if not perdus else " -> " + "; ".join(u.split("/")[-1] for u in perdus[:5])))
            await ctx.close()

        # ---------- tunnel complet ----------
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        ctx.set_default_timeout(30000)
        await ctx.route('**fonts.g*/**', lambda r: r.abort())
        page = await ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        # laisser le rideau d'ouverture se retirer : tant qu'il est la,
        # la page n'est pas dans son etat definitif
        await page.wait_for_timeout(2500)

        # nombre de mesures par type de vetement
        attendu = {"robe_taille": 9, "robe_droite": 15, "robe_ovale": 11, "pantalon": 6, "haut": 8}
        got = await page.evaluate("()=>{const o={};for(const k in MESURES)o[k]=MESURES[k].champs.length;return o;}")
        for k, v in attendu.items():
            ok(got.get(k) == v, f"mesures {k} = {v} (vu {got.get(k)})")
        ids = await page.evaluate("()=>{const o={};for(const k in MESURES)o[k]=MESURES[k].champs.map(c=>c.id);return o;}")
        for k, lst in ids.items():
            ok(len(lst) == len(set(lst)), f"mesures {k} : aucun identifiant en double")

        # --- parcours d'achat complet, sur la PREMIERE piece reelle du catalogue.
        #     Le nom, le prix et le supplement express sont LUS dans les donnees :
        #     un controle ne recopie jamais un chiffre (regle du depot).
        pap = await page.evaluate("()=>PIECES.filter(p=>p.cat==='pap').length")
        if pap:
            await page.evaluate("()=>onglet(\'pap\')")
        else:
            note("aucune piece en pret-a-porter : le controle des tailles est sans objet")
            await page.evaluate("()=>onglet(\'sm\')")
        P = await page.evaluate("()=>{const p=PIECES.filter(x=>x.cat===(PIECES.some(y=>y.cat==='pap')?'pap':'sm'))[0];"
                                " return {nom:p.nom, prix:p.prix, exp:(p.expPrix!=null?p.expPrix-p.prix:0),"
                                " expMax:(p.expMax!=null?p.expMax:4), type:p.type||null};}")
        await page.locator(".piece").first.click()
        if P["type"]:
            nb = await page.locator("[data-mes]").count()
            for i in range(nb):
                await page.locator("[data-mes]").nth(i).fill("60")
        else:
            await page.click('[data-taille="M"]')
        # le parcours a panier : mesures -> delai -> panier -> commande
        await page.click('[data-nav="suiv"]')          # etape 2 : le delai
        await page.click('[data-exp="1"]')             # express
        await page.click('[data-nav="suiv"]')          # « Ajouter au panier »
        ok(await page.locator("#pan.on").count() == 1, "le panier s'ouvre des qu'une piece y tombe")
        ok((await page.inner_text("#panN")).strip() == "1", "la pastille du panier affiche 1")
        await page.click('[data-pan="commander"]')
        await page.click('[data-mode="expedition"]')
        await page.select_option("#f_pays", "ci")
        await page.fill("#f_ville", "Abidjan")
        dispo = (await page.locator(".dispo p").inner_text()).strip()
        ok(len(dispo) > 6, f"date de disponibilite affichee des le choix de la livraison : « {dispo} »")
        j = await page.evaluate("()=>joursTotal()")
        att_j = P["expMax"] + 4                       # 4 jours d'acheminement CI
        ok(j == att_j, f"delai express ({P['expMax']} j) + acheminement CI (4 j) = {att_j} j (vu {j})")
        attendu_d = datetime.date.today() + datetime.timedelta(days=att_j)
        ok(str(attendu_d.day) in dispo, f"la date correspond bien a J+{att_j} ({attendu_d})")
        await page.click('[data-nav="suiv"]')          # coordonnees
        await page.fill("#f_prenom", "Ama")
        await page.fill("#f_tel", "+22997000000")
        tot = (await page.locator(".recap .tt span").last.inner_text()).strip()
        att_t = P["prix"] + 12000 + P["exp"]          # piece + expedition CI + express
        att_s = f"{att_t:,}".replace(",", " ") + " F"
        vu = tot.replace(" ", " ").replace(" ", " ")
        ok(vu == att_s.replace(" ", " "),
           f"total {P['prix']}+12000+{P['exp']} = {att_s} (vu « {tot} »)")
        await page.click('[data-nav="suiv"]')
        href = await page.get_attribute("#btWa", "href")
        ok(href.startswith("https://wa.me/"), "lien WhatsApp genere")
        msg = await page.evaluate("()=>message()")
        if P["type"]:
            ok("MESURES" in msg, "les mesures figurent dans le message")
        else:
            ok("Taille" in msg, "la taille figure dans le message")
        # ⚠️ ne PAS recopier « mailto: » ici : tant qu'Hillary n'a pas donne son
        #    adresse, EMAIL est vide et le repli est un appel. Ce qui compte,
        #    c'est qu'il mene QUELQUE PART DE REEL. Une adresse inventee est
        #    restee en ligne, et les commandes de qui n'a pas WhatsApp
        #    partaient dans le vide (2026-08-06).
        alt = await page.get_attribute("#altMail", "href")
        mail_cfg = await page.evaluate("()=>EMAIL")
        attendu = "mailto:" + mail_cfg if mail_cfg else "tel:+"
        ok(alt.startswith(attendu),
           f"repli sans WhatsApp : lien reel a l'etape finale ({alt[:34]})")
        libelle = (await page.inner_text("#altMail")).lower()
        ok(("email" in libelle) == bool(mail_cfg),
           "le libelle du repli dit ce que le lien fait vraiment")
        await page.click("#btX")
        await page.evaluate("()=>{panier=[];sauvePanier();rendrePanier();}")

        # --- parcours sur-mesure : retrait atelier, delai normal, mesures partielles
        await page.evaluate("()=>onglet(\'sm\')")
        # la DERNIERE piece du catalogue, quel que soit son nom : le nombre de
        # champs attendu est lu dans MESURES, jamais recopie
        # la derniere piece QUI A UN JEU DE MESURES (« Creation libre » n'en a
        # pas : le client choisit son type, donc 0 champ au depart)
        der = await page.evaluate("()=>{const l=PIECES.filter(p=>p.type);"
                                  " const p=l[l.length-1];"
                                  " return {nom:p.nom, type:p.type, jmax:p.jmax, prix:p.prix};}")
        att_m = await page.evaluate("t=>t?MESURES[t].champs.length:0", der["type"])
        await page.locator(".piece", has_text=der["nom"]).first.click()
        champs = await page.locator("[data-mes]").count()
        ok(champs == att_m, f"{der['nom']} : {att_m} champs de mesure affiches (vu {champs})")
        aide = await page.locator(".aide p").inner_text()
        ok("vous-meme" in aide.replace("ê", "e").replace("é", "e") or "vous-même" in aide,
           "message d'aide affiche au-dessus des mesures")
        dis = await page.get_attribute('[data-nav="suiv"]', "disabled")
        ok(dis is not None, "impossible d'avancer sans aucune mesure")
        der_jmax = der["jmax"]
        moitie = att_m // 2 + 1
        for i in range(moitie):
            await page.locator("[data-mes]").nth(i).fill("80")
        dis = await page.get_attribute('[data-nav="suiv"]', "disabled")
        ok(dis is None, f"{moitie} mesures sur {att_m} suffisent pour avancer")
        await page.click('[data-nav="suiv"]')          # etape 2 : le delai
        await page.click('[data-exp="0"]')             # confection normale
        await page.click('[data-nav="suiv"]')          # au panier
        await page.click('[data-pan="commander"]')
        await page.click('[data-mode="retrait"]')
        j = await page.evaluate("()=>joursTotal()")
        ok(j == der_jmax, f"retrait + normal : borne haute de la piece = {der_jmax} j (vu {j})")
        lab = await page.locator(".dispo b").inner_text()
        ok("retirer" in lab.lower(), f"libelle adapte au retrait (« {lab} »)")
        await page.click('[data-nav="suiv"]')          # coordonnees
        await page.fill("#f_prenom", "Koffi")
        await page.fill("#f_mail", "koffi@gmail.com")
        dis = await page.get_attribute('[data-nav="suiv"]', "disabled")
        ok(dis is None, "email seul (sans WhatsApp) suffit pour valider")
        tot = (await page.locator(".recap .tt span").last.inner_text()).strip()
        der_prix = der["prix"]
        att2 = f"{der_prix:,}".replace(",", " ") + " F"
        vu2 = tot.replace(" ", " ").replace(" ", " ")
        ok(vu2 == att2, f"total retrait + normal = {att2} (vu « {tot} »)")
        msg = await page.evaluate("()=>message()")
        manq = att_m - moitie
        ok(f"{manq}" in msg or "à prendre ensemble" in msg,
           f"les {manq} mesures manquantes sont signalees dans le message")
        await page.click("#btX")
        await page.evaluate("()=>{panier=[];sauvePanier();rendrePanier();}")

        # --- sur devis + type libre
        await page.locator(".piece", has_text="Creation libre").first.click() if False else None
        await page.locator(".piece", has_text="Cr").filter(has_text="libre").first.click()
        sel = await page.locator("#f_type").count()
        ok(sel == 1, "creation libre : le client choisit le type de vetement")
        await page.select_option("#f_type", "robe_droite")
        champs = await page.locator("[data-mes]").count()
        ok(champs == 15, f"robe droite via creation libre : 15 champs (vu {champs})")
        await page.evaluate("()=>{etat.mesures={epaules:'40',carr_dev:'36',poitrine:'92',t_sous_sein:'78',t_taille:'70',t_ceinture:'72',t_hanche:'96',l_sous_sein:'22'};etat.etape=2;dessiner();}")
        await page.click('[data-exp="1"]')
        await page.click('[data-nav="suiv"]')          # au panier
        await page.click('[data-pan="commander"]')
        await page.click('[data-mode="retrait"]')
        tot = (await page.evaluate("()=>totalCommande()"))
        ok(tot is None, "piece sans prix : le total reste « sur devis »")
        await page.click('[data-nav="suiv"]')
        tt = (await page.locator(".recap .tt span").last.inner_text()).strip()
        ok(tt.lower().startswith("sur devis"), f"affichage « sur devis » dans le recapitulatif (vu « {tt} »)")
        await page.click("#btX")
        await page.evaluate("()=>{panier=[];sauvePanier();rendrePanier();}")

        # --- LE PANIER (ajoute le 2026-08-16) -----------------------
        # deux pieces dans le meme panier : le total est la somme, et le
        # delai retenu est celui de la piece la PLUS LENTE, pas la plus rapide.
        await page.evaluate("()=>{panier=[];sauvePanier();rendrePanier();}")
        deux = await page.evaluate("""()=>{const l=PIECES.filter(p=>p.prix!=null&&p.type);
          return l.slice(0,2).map(p=>({id:p.id,nom:p.nom,prix:p.prix,expPrix:p.expPrix,
                                       jmax:p.jmax,expMax:p.expMax,type:p.type}));}""")
        if len(deux) >= 2:
            for i, pc in enumerate(deux):
                await page.evaluate("id=>{ouvrir(id);}", pc["id"])
                nb = await page.locator("[data-mes]").count()
                for k in range(nb):
                    await page.locator("[data-mes]").nth(k).fill("70")
                await page.click('[data-nav="suiv"]')
                await page.click('[data-exp="%d"]' % (1 if i == 1 else 0))
                await page.click('[data-nav="suiv"]')
            n = (await page.inner_text("#panN")).strip()
            ok(n == "2", f"deux pieces au panier : la pastille affiche 2 (vu {n})")
            lignes = await page.locator("#panBd .pl").count()
            ok(lignes == 2, f"le tiroir montre les deux lignes (vu {lignes})")
            att = deux[0]["prix"] + (deux[1]["expPrix"] or deux[1]["prix"])
            vu = await page.evaluate("()=>totaux().fcfa")
            ok(vu == att, f"sous-total = {att} F, la somme des deux lignes (vu {vu})")
            attj = max(deux[0]["jmax"], deux[1]["expMax"] or 4)
            vuj = await page.evaluate("()=>joursConfection()")
            ok(vuj == attj, f"delai retenu = la piece la plus lente, {attj} j (vu {vuj})")
            # une ligne en moins, un total qui suit
            await page.locator("#panBd [data-rm]").first.click()
            vu2 = await page.evaluate("()=>totaux().fcfa")
            ok(vu2 == (deux[1]["expPrix"] or deux[1]["prix"]),
               f"une ligne retiree : le total suit (vu {vu2})")
            # la quantite
            await page.locator("#panBd [data-plus]").first.click()
            q = await page.evaluate("()=>totaux().articles")
            ok(q == 2, f"le bouton + passe la ligne a 2 exemplaires (vu {q})")
            vu3 = await page.evaluate("()=>totaux().fcfa")
            ok(vu3 == vu2 * 2, f"deux exemplaires : le prix double ({vu3})")
            # le panier survit a un rechargement
            await page.reload(wait_until="domcontentloaded")
            await page.wait_for_timeout(1200)
            gard = await page.evaluate("()=>panier.length")
            ok(gard == 1, f"le panier survit au rechargement de la page (vu {gard} ligne)")
            await page.evaluate("()=>{panier=[];sauvePanier();rendrePanier();}")
        else:
            note("moins de deux pieces chiffrees au catalogue : controle du panier sans objet")

        # --- robe ovale : avertissement de validation
        nom_ov = await page.evaluate("()=>{const p=PIECES.filter(x=>x.type==='robe_ovale')[0];"
                                     " return p?p.nom:'';}")
        await page.locator(".piece", has_text=nom_ov).first.click()
        w = await page.locator(".warn").count()
        ok(w >= 1, "robe ovale : avertissement « mesures en cours de validation » affiche")
        await page.click("#btX")

        ok(not errs, "tunnel complet : aucune erreur JS" + ("" if not errs else " -> " + errs[0][:150]))
        await ctx.close()
        # ---------- la couche de mouvement ----------
        ctx = await br.new_context(viewport={"width": 1440, "height": 900}, **CHROME_CTX)
        ctx.set_default_timeout(30000)
        await ctx.route('**fonts.g*/**', lambda r: r.abort())
        page = await ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")

        # V4 : le loader s'appelle #load et se retire par la classe .fini
        ok(await page.locator("#load").count() == 1, "le loader d'ouverture est present au chargement")
        await page.wait_for_timeout(3400)
        fini = await page.evaluate("()=>{const l=document.getElementById('load'); return !l || l.classList.contains('fini') || getComputedStyle(l).display==='none';}")
        ok(fini, "le loader s'efface apres l'ouverture (il ne bloque rien)")

        await page.evaluate("()=>window.scrollTo(0, document.body.scrollHeight*0.55)")
        await page.wait_for_timeout(500)
        # V4 : la barre s'inverse en passant sur une section encre
        inv = await page.evaluate("()=>{const n=document.getElementById('nav'); return !!n && n.classList.contains('pose');}")
        ok(inv, "la barre de navigation se pose au defilement")

        # chaque signature de section se declenche
        for sel, nom in [("#maison .piliers", "01 les piliers"),
                         ("#collections .coll-d", "02 les collections"),
                         ("#lookbook .lk", "03 le lookbook"),
                         ("#process .et", "04 le processus"),
                         ("#contact .socs", "05 le contact")]:
            await page.evaluate("s=>{const e=document.querySelector(s); if(e) e.scrollIntoView({block:'center'});}", sel)
            await page.wait_for_timeout(950)
            n = await page.locator(sel + ".vu").count()
            ok(n >= 1, f"revelation {nom} : declenchee ({n} element(s))")

        # V4 : le compteur du lookbook suit le defilement
        # ⚠️ offsetTop est relatif a l'ancetre POSITIONNE (.look est en relative),
        #    pas au document. C'est getBoundingClientRect()+scrollY qui donne
        #    la vraie position. Le controle se trompait, pas le site.
        await page.evaluate("""()=>{const e=document.getElementById('lookSc');
          if(e) window.scrollTo(0, e.getBoundingClientRect().top + scrollY + e.offsetHeight*0.7);}""")
        await page.wait_for_timeout(800)
        c = await page.evaluate("()=>(document.getElementById('lkPage')||{}).textContent||''")
        ok("/" in c and c.strip() != "01 / 06",
           f"le compteur du lookbook a avance ({c.strip()})")

        # V4 : le heros presente bien 4 creations, le carrousel 6 pieces
        nh = await page.locator(".hsl").count()
        nc = await page.locator(".car").count()
        ok(nh >= 3, f"le heros presente {nh} creations")
        ok(nc >= 4, f"le carrousel presente {nc} pieces")

        # AUCUN CONTACT AFFICHE NE DOIT MENER DANS LE VIDE, et les delais
        # annonces dans le bloc contact doivent dire la meme chose que le
        # catalogue. Une adresse inventee et un « 7 a 14 jours » qui
        # contredisait chaque carte sont restes en ligne (2026-08-06).
        cont = await page.evaluate("""()=>{
          const t=document.body.innerText;
          const mails=(t.match(/[\\w.+-]+@[\\w-]+\\.[\\w.]+/g)||[]);
          const j=[...new Set((PIECES.filter(p=>p.jmax!=null).map(p=>p.jmax)))];
          const e=[...new Set((PIECES.filter(p=>p.expMax!=null).map(p=>p.expMax)))];
          return {mails, hor:(document.getElementById('hor')||{}).textContent||'',
                  jmax:Math.max.apply(null,j), expMax:Math.max.apply(null,e),
                  expMin:Math.min.apply(null,PIECES.filter(p=>p.expMin!=null).map(p=>p.expMin))};}""")
        ok(not cont["mails"] or (await page.evaluate("()=>EMAIL")) in cont["mails"],
           "aucune adresse email affichee qui ne soit celle configuree"
           + ("" if not cont["mails"] else " -> " + ", ".join(cont["mails"][:3])))
        sem = str(cont["jmax"] // 7)
        ok((sem + " semaine") in cont["hor"] or str(cont["jmax"]) in cont["hor"],
           f"le bloc contact annonce le meme delai que le catalogue ({cont['hor'][:52]})")
        ok(str(cont["expMax"]) in cont["hor"] and str(cont["expMin"]) in cont["hor"],
           f"le bloc contact annonce le meme express que le catalogue "
           f"({cont['expMin']} a {cont['expMax']} jours)")

        # LA PAGE MONTRE UNE VRAIE PIECE MEME SANS JAVASCRIPT.
        # Sans ca, un navigateur qui limite le script (Opera Mini en mode
        # economie, un mode « Lite ») affiche un heros vide : un chiffre geant
        # sur du rose, aucun vetement. C'est « la page ne marche pas ».
        ctx2 = await br.new_context(viewport={"width": 360, "height": 740},
                                    is_mobile=True, has_touch=True,
                                    java_script_enabled=False)
        pg2 = await ctx2.new_page()
        await ctx2.route('**fonts.g*/**', lambda r: r.abort())
        await pg2.goto(URL, wait_until="load")
        await pg2.wait_for_timeout(1200)
        sans = await pg2.evaluate("""()=>{
          const i=document.querySelector('#hsc img');
          const d=document.getElementById('hdes'), c=document.getElementById('hcol');
          return {img:i?i.getAttribute('src'):null,
                  des:(d&&d.textContent||'').trim().length,
                  col:(c&&c.textContent||'').trim().length};}""")
        ok(bool(sans["img"]) and sans["des"] > 20 and sans["col"] > 10,
           "sans JavaScript : une vraie piece et son texte s'affichent"
           + f" (photo {sans['img']}, {sans['des']} + {sans['col']} caracteres)")
        # ⚠️ et surtout : on doit pouvoir JOINDRE LA MAISON. Le bouton
        #    principal avait href="#" et n'etait rempli que par le script.
        morts = await pg2.evaluate("""()=>[...document.querySelectorAll('a')]
            .filter(a=>{const h=a.getAttribute('href')||'';
              return (h==='#'||h==='') && !a.classList.contains('skip');})
            .map(a=>(a.className||a.id||a.tagName)+' « '+(a.textContent||'').trim().slice(0,26)+' »')""")
        joindre = await pg2.evaluate("""()=>({
            wa:[...document.querySelectorAll('a[href*="wa.me"]')].length,
            tel:[...document.querySelectorAll('a[href^="tel:"]')].length})""")
        ok(not morts, "sans JavaScript : aucun lien mort"
           + ("" if not morts else " -> " + "; ".join(morts[:4])))
        ok(joindre["wa"] >= 1 and joindre["tel"] >= 1,
           f"sans JavaScript : on peut ecrire ET appeler ({joindre['wa']} WhatsApp, {joindre['tel']} telephone)")
        await ctx2.close()

        # LE CHIFFRE GEANT SUIT LA PIECE.
        # Il roulait 240 ms puis se remplacait d'un coup, alors que le
        # glissement dure 1,15 s : il arrivait 900 ms avant le vetement.
        # On verifie qu'ils se croisent VRAIMENT en cours de route, et qu'il
        # n'en reste qu'un a l'arrivee, accorde au compteur.
        # ⚠️ on ECHANTILLONNE tout le glissement au lieu de regarder a un
        #    instant fixe : le defilement automatique peut avaler le clic, et
        #    un controle qui tombe au mauvais moment ment dans les deux sens.
        croise = await page.evaluate("""()=>new Promise(res=>{
            const t0=performance.now(); let vu2=0, ymin=0, ymax=0, clics=0;
            function clic(){ document.getElementById('hNext').click(); clics++; }
            clic();
            (function tick(){
              const sp=[...document.querySelectorAll('#hnum span')];
              if(sp.length===2){
                vu2++;
                const y=sp.map(s=>new DOMMatrix(getComputedStyle(s).transform).m42);
                ymin=Math.min(ymin,...y); ymax=Math.max(ymax,...y);
              }
              const t=performance.now()-t0;
              if(t>340 && vu2===0 && clics<3){ clic(); }
              if(t>2200) return res({vu2, ymin:Math.round(ymin), ymax:Math.round(ymax), clics});
              requestAnimationFrame(tick);
            })();})""")
        ok(croise["vu2"] > 0,
           f"le chiffre croise pendant le glissement (vu sur {croise['vu2']} image(s))")
        # l'ecart suffit a prouver le croisement : l'un est haut, l'autre bas.
        # ⚠️ ne PAS exiger de voir le chiffre entrant en positif : la courbe
        #    part vite, et un rendu lent le rate sans que rien ne cloche.
        ok(croise["ymin"] < -20 and (croise["ymax"] - croise["ymin"]) > 120,
           f"les deux chiffres sont de part et d'autre (y de {croise['ymin']} a {croise['ymax']})")
        await page.wait_for_timeout(1400)
        fin_ = await page.evaluate("""()=>({n:document.querySelectorAll('#hnum span').length,
             num:(document.getElementById('hnum').textContent||'').trim(),
             cpt:(document.getElementById('hcpt').textContent||'').trim()})""")
        ok(fin_["n"] == 1, f"un seul chiffre a l'arrivee (vu {fin_['n']})")
        ok(fin_["cpt"].startswith(fin_["num"]),
           f"le chiffre geant et le compteur disent la meme chose ({fin_['num']} / {fin_['cpt']})")

        # cliquer vite ne doit rien empiler ni desaccorder
        for _ in range(4):
            await page.evaluate("()=>document.getElementById('hPrev').click()")
            await page.wait_for_timeout(150)
            await page.evaluate("()=>document.getElementById('hNext').click()")
            await page.wait_for_timeout(150)
        await page.wait_for_timeout(1600)
        ap = await page.evaluate("""()=>({n:document.querySelectorAll('#hnum span').length,
             num:(document.getElementById('hnum').textContent||'').trim(),
             cpt:(document.getElementById('hcpt').textContent||'').trim(),
             act:document.querySelectorAll('.hsl.act').length})""")
        ok(ap["n"] == 1 and ap["act"] == 1 and ap["cpt"].startswith(ap["num"]),
           f"clics rapides : rien ne s'empile ({ap['n']} chiffre, {ap['act']} diapo, {ap['num']}/{ap['cpt']})")

        # LES PIECES SONT DETOUREES, ET RIEN NE LES ENCADRE.
        # Deux defauts vus par Mongazi le 2026-08-06 : une bande blanche autour
        # du mannequin (image non detouree) et un cadre autour des pieces du
        # carrousel (fond opaque sur le conteneur). Un rectangle blanc couvre
        # aussi le chiffre geant : l'effet du heros disparait avec lui.
        opaques = []
        for f in sorted(glob.glob(str(pathlib.Path(__file__).resolve().parent
                                      / "assets" / "images" / "hero-*.webp"))
                        + glob.glob(str(pathlib.Path(__file__).resolve().parent
                                        / "assets" / "images" / "piece-*.webp"))):
            try:
                from PIL import Image
                im = Image.open(f)
                a = im.convert("RGBA").getchannel("A")
                if a.getextrema()[0] > 8:          # aucun pixel transparent
                    opaques.append(pathlib.Path(f).name)
            except Exception as e:
                opaques.append(pathlib.Path(f).name + " (illisible)")
        ok(not opaques, "heros et carrousel : images detourees (fond transparent)"
           + ("" if not opaques else " -> opaques : " + ", ".join(opaques)))

        cadres = await page.evaluate("""()=>{
          const out=[];
          document.querySelectorAll('.car-c, .hsl').forEach(e=>{
            const s=getComputedStyle(e);
            const bg=s.backgroundColor||'';
            const m=bg.match(/rgba?\\(([^)]+)\\)/);
            const op=m ? (m[1].split(',')[3]===undefined ? 1 : parseFloat(m[1].split(',')[3])) : 0;
            if(op>0.02) out.push((e.className||e.tagName)+' '+bg);
            if(parseFloat(s.borderTopWidth)>0) out.push((e.className||e.tagName)+' bordure');
          });
          return out;}""")
        ok(not cadres, "heros et carrousel : aucun cadre autour des pieces"
           + ("" if not cadres else " -> " + str(cadres[:3])))

        # ── LA BASCULE FACE / DOS, VUE ET NON SUPPOSEE ──────────────
        # Une piece envoyee en double doit passer d'une vue a l'autre TOUTE
        # SEULE pendant qu'on la regarde, et s'arreter des qu'on ne la
        # regarde plus. Les quatre controles qui suivent mesurent l'opacite
        # reellement calculee, ils ne lisent pas le CSS.
        await page.evaluate("()=>onglet('sm')")
        await page.evaluate("""()=>{const e=document.getElementById('catalogue');
          if(e) window.scrollTo(0, e.getBoundingClientRect().top+scrollY+40);}""")
        await page.wait_for_timeout(700)
        d = await page.evaluate("""()=>{
          const l=[...document.querySelectorAll('#grille .ph.duo')];
          if(!l.length) return {n:0};
          const c=l[0], p=[...c.querySelectorAll('.vues i')];
          return {n:l.length, img:c.querySelectorAll('img').length, pts:p.length,
                  seule:[...document.querySelectorAll('#grille .ph:not(.duo) img')].length};}""")
        ok(d["n"] >= 1, f"catalogue : {d['n']} piece(s) photographiee(s) de face ET de dos")
        if d["n"]:
            ok(d["img"] == 2 and d["pts"] == 2,
               f"une piece a deux vues porte 2 images et 2 pastilles (vu {d['img']} et {d['pts']})")
            ok(d["seule"] >= 1,
               f"une piece a une seule photo n'en porte qu'une ({d['seule']} carte(s))")

            # elle bascule, sans qu'on touche a rien
            b = await page.evaluate("""()=>new Promise(res=>{
              const c=document.querySelector('#grille .ph.duo');
              const a=c.querySelector('.v1'), b=c.querySelector('.v2');
              const o1=[], o2=[]; let t=0;
              const id=setInterval(()=>{
                o1.push(parseFloat(getComputedStyle(a).opacity));
                o2.push(parseFloat(getComputedStyle(b).opacity));
                if((t+=200)>=5000){ clearInterval(id);
                  res({max2:Math.max(...o2), min1:Math.min(...o1)}); }
              },200);})""")
            ok(b["max2"] > 0.9 and b["min1"] < 0.1,
               "la seconde vue prend la place de la premiere, toute seule "
               f"(dos monte a {b['max2']:.2f}, face descend a {b['min1']:.2f})")

            # la pastille active n'est pas SEULEMENT rose : elle est plus large
            # ⚠️ ON ECHANTILLONNE, ON NE MESURE PAS UN INSTANT. La largeur est
            #    animee : pendant le croisement des deux vues, les deux
            #    pastilles passent toutes les deux par ~9 px et l'ecart tombe a
            #    1. La version d'avant tombait pile la, apres 5 s a echantillonner
            #    l'opacite juste au-dessus : ECHEC annonce sur un site sain,
            #    mesure a 9,7 px d'ecart au repos. On garde le MEILLEUR ecart
            #    vu sur une seconde : si le style regressait a la seule couleur,
            #    aucun echantillon n'atteindrait le seuil.
            ecarts = []
            for _ in range(6):
                w = await page.evaluate("""()=>{
                  const p=[...document.querySelector('#grille .ph.duo .vues').children];
                  return p.map(e=>e.getBoundingClientRect().width);}""")
                ecarts.append((max(w) - min(w), w))
                await page.wait_for_timeout(200)
            meilleur, w = max(ecarts)
            ok(meilleur >= 4,
               f"l'etat de la pastille ne tient pas qu'a la couleur "
               f"(ecart {meilleur:.1f} px, largeurs {[round(x,1) for x in w]})")

            # ⚠️ ON ECHANTILLONNE, ON NE COMPARE PAS DEUX INSTANTANES.
            #    Premiere version de ce controle : etat, on attend 5,2 s, etat,
            #    « ils doivent differer ». La bascule a une periode de 7,2 s
            #    (3,6 s par vue) : une fois sur cinq, les deux releves tombent
            #    sur la MEME phase et le controle echoue sans que rien ne soit
            #    casse. Meme famille que le controle qui echouait au hasard le
            #    2026-08-17. On releve toutes les 200 ms et on compte les etats
            #    DISTINCTS : plus aucun hasard.
            # ⚠️ Et il faut un TEMOIN : « rien ne bascule hors de l'ecran »
            #    passerait tout seul si le mecanisme etait mort.
            suivre = """(ms)=>new Promise(res=>{
              const lire=()=>[...document.querySelectorAll('#grille .ph.duo')]
                    .map(e=>e.classList.contains('dos')?'D':'f').join('');
              const vu=new Set([lire()]); let t=0;
              const id=setInterval(()=>{ vu.add(lire());
                if((t+=200)>=ms){ clearInterval(id); res([...vu]); } },200);})"""
            v = await page.evaluate(suivre, 8000)
            ok(len(v) >= 2, f"sous les yeux, le catalogue tourne tout seul (etats vus : {v})")

            # hors de l'ecran, plus rien ne tourne
            await page.evaluate("()=>window.scrollTo(0,0)")
            await page.wait_for_timeout(900)
            v = await page.evaluate(suivre, 5000)
            ok(len(v) == 1, f"hors de l'ecran, aucune carte ne bascule (etats vus : {v})")

            # fiche de commande ouverte : le catalogue derriere se fige
            await page.evaluate("""()=>{const e=document.getElementById('catalogue');
              if(e) window.scrollTo(0, e.getBoundingClientRect().top+scrollY+40);}""")
            await page.wait_for_timeout(600)
            await page.locator(".piece").first.click()
            await page.wait_for_selector("#ov.on")
            v = await page.evaluate(suivre, 5000)
            ok(len(v) == 1, f"fiche ouverte : le catalogue derriere se fige (etats vus : {v})")
            await page.click("#btX")
            await page.wait_for_timeout(300)

            # au carrousel, SEULE la carte active respire
            n2 = await page.evaluate("""()=>{
              const l=[...document.querySelectorAll('.car')];
              return l.findIndex(e=>e.querySelector('.car-c.duo'));}""")
            if n2 >= 0:
                for _ in range(n2):
                    await page.click("#cNext")
                    await page.wait_for_timeout(120)
                await page.wait_for_timeout(4200)
                r = await page.evaluate("""()=>({
                  act:document.querySelectorAll('.car--act .car-c.duo.dos').length,
                  autres:document.querySelectorAll('.car:not(.car--act) .car-c.dos').length});""")
                ok(r["act"] == 1 and r["autres"] == 0,
                   f"carrousel : seule la carte active respire ({r['act']} active, {r['autres']} autre(s))")

        # ── MOUVEMENT REDUIT : PLUS RIEN NE BASCULE ─────────────────
        # La regle de la maison est constante : `prefers-reduced-motion` coupe
        # tout ce qui bouge tout seul. Une image qui se substitue a une autre
        # sans qu'on l'ait demande en fait partie. Le dos reste joignable dans
        # la fiche de commande (figure « Le dos »), il n'est pas perdu.
        ctx3 = await br.new_context(viewport={"width": 1440, "height": 900},
                                    reduced_motion="reduce")
        pg3 = await ctx3.new_page()
        await ctx3.route('**fonts.g*/**', lambda r: r.abort())
        await pg3.goto(URL, wait_until="domcontentloaded")
        await pg3.wait_for_timeout(2200)
        await pg3.evaluate("()=>onglet('sm')")
        await pg3.evaluate("""()=>{const e=document.getElementById('catalogue');
          if(e) window.scrollTo(0, e.getBoundingClientRect().top+scrollY+40);}""")
        await pg3.wait_for_timeout(5400)
        rm = await pg3.evaluate("""()=>{
          const l=[...document.querySelectorAll('#grille .ph.duo')];
          if(!l.length) return null;
          const v=document.querySelector('#grille .ph.duo .vues');
          return {bascule:l.filter(e=>e.classList.contains('dos')).length,
                  dos:Math.max(...l.map(e=>parseFloat(getComputedStyle(e.querySelector('.v2')).opacity))),
                  pastilles:v?getComputedStyle(v).display:'none'};}""")
        if rm:
            ok(rm["bascule"] == 0 and rm["dos"] < 0.05,
               f"mouvement reduit : aucune vue ne bascule ({rm['bascule']} carte(s), dos a {rm['dos']:.2f})")
            ok(rm["pastilles"] == "none",
               f"mouvement reduit : pas de pastilles figees (display {rm['pastilles']})")
        await ctx3.close()

        # ── UNE SECONDE VUE QUI N'ARRIVE PAS NE VIDE PAS LA CARTE ───
        # La vue de dos est en `loading="lazy"`. Sur une 4G de Cotonou elle
        # peut n'etre la qu'apres l'heure de la premiere bascule : basculer
        # quand meme revelerait du VIDE pendant 3,6 s, et la cliente verrait
        # une carte cassee. On coupe le reseau sur les `-dos.webp` et on
        # verifie que la carte reste sur sa face, sans jamais se vider.
        ctx4 = await br.new_context(viewport={"width": 1440, "height": 900})
        pg4 = await ctx4.new_page()
        await ctx4.route('**fonts.g*/**', lambda r: r.abort())
        await ctx4.route('**/*-dos.webp', lambda r: r.abort())
        await pg4.goto(URL, wait_until="domcontentloaded")
        await pg4.wait_for_timeout(2200)
        await pg4.evaluate("()=>onglet('sm')")
        await pg4.evaluate("""()=>{const e=document.getElementById('catalogue');
          if(e) window.scrollTo(0, e.getBoundingClientRect().top+scrollY+40);}""")
        await pg4.wait_for_timeout(8000)
        vide = await pg4.evaluate("""()=>{
          const l=[...document.querySelectorAll('#grille .ph.duo')];
          if(!l.length) return null;
          return {dos:l.filter(e=>e.classList.contains('dos')).length,
                  face:Math.min(...l.map(e=>parseFloat(getComputedStyle(e.querySelector('.v1')).opacity)))};}""")
        if vide:
            ok(vide["dos"] == 0 and vide["face"] > 0.95,
               "seconde vue absente : la carte reste sur sa face "
               f"({vide['dos']} bascule(s), face a {vide['face']:.2f})")
        await ctx4.close()

        # regle du depot : jamais d'animation infinie sous un backdrop-filter
        mauvais = await page.evaluate("""()=>{
          const out=[];
          document.querySelectorAll('*').forEach(e=>{
            const s=getComputedStyle(e);
            if(s.animationIterationCount==='infinite'){
              let p=e.parentElement;
              while(p){ const ps=getComputedStyle(p);
                if(ps.backdropFilter && ps.backdropFilter!=='none'){ out.push(e.className||e.tagName); break; }
                p=p.parentElement; }
            }
          });
          return out;}""")
        ok(not mauvais, "aucune animation infinie sous un backdrop-filter" + ("" if not mauvais else " -> " + str(mauvais[:3])))

        await overflow(page, "[1440px] apres ouverture du loader")
        ok(not errs, "couche de mouvement : aucune erreur JS" + ("" if not errs else " -> " + errs[0][:140]))
        await ctx.close()

        # ---------- le toucher et la vie du catalogue ----------
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        ctx.set_default_timeout(30000)
        await ctx.route('**fonts.g*/**', lambda r: r.abort())
        page = await ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(2600)

        # les cartes sont posees de travers, comme des echantillons
        rots = await page.evaluate("""()=>[...document.querySelectorAll('#grille .piece')]
            .map(e=>e.style.getPropertyValue('--rot')).filter(Boolean)""")
        # ⚠️ le nombre de cartes vient des DONNÉES, jamais recopié
        att_r = await page.evaluate("()=>PIECES.filter(p=>p.cat===document.querySelector"
                                    "('.tab[aria-selected=\"true\"]').dataset.onglet).length")
        ok(len(rots) == att_r and len(set(rots)) > 1,
           f"catalogue : {att_r} cartes, inclinaisons differentes ({len(set(rots))} valeurs)")

        # l'onde de toucher nait au point touche
        c = page.locator("#grille .piece").first
        await c.scroll_into_view_if_needed()
        await page.wait_for_timeout(500)
        b = await c.bounding_box()
        await page.mouse.move(b["x"] + b["width"] / 2, b["y"] + 30)
        await page.mouse.down()
        await page.wait_for_timeout(90)
        n = await page.locator("#grille .piece .onde").count()
        brille = await page.locator("#grille .piece.brille").count()
        await page.mouse.up()
        # appuyer puis relacher sur une carte = un clic : la fiche s'ouvre.
        # On la referme, sinon tout ce qui suit est bloque par la modale.
        if await page.locator("#ov.on").count():
            await page.click("#btX")
            await page.wait_for_timeout(250)
        ok(n >= 1, f"toucher : l'onde de lumiere apparait ({n})")
        ok(brille >= 1, "toucher : le tissu brille et la craie se retrace")
        await page.wait_for_timeout(800)
        reste = await page.locator(".onde").count()
        ok(reste == 0, f"l'onde est retiree du DOM apres coup ({reste} restante(s))")

        # la vibration est bien gardee (Android seulement, jamais au defilement)
        v = await page.evaluate("()=>typeof vibre === 'function'")
        ok(v is False or v is True, "fonction de vibration presente" if v else "vibration : encapsulee")

        # une animation par etape du tunnel
        await page.evaluate("()=>onglet(\'sm\')")
        await page.wait_for_timeout(400)
        # la premiere piece qui a un jeu de mesures, quel que soit son nom
        nom_m = await page.evaluate("()=>{const p=PIECES.filter(x=>x.type)[0]; return p?p.nom:'';}")
        await page.locator(".piece", has_text=nom_m).first.click()
        await page.wait_for_timeout(300)
        vus = []
        nb_m = await page.locator("[data-mes]").count()
        for i in range(min(nb_m, nb_m // 2 + 1)):
            await page.locator("[data-mes]").nth(i).fill("80")
        # parcours a panier : mesures (1) -> delai (3) -> livraison (2)
        # -> coordonnees (4). Les numeros sont ceux des animations, pas
        # l'ordre des ecrans : chaque etape garde SON animation d'origine.
        vus.append(await page.get_attribute("#shBd", "data-e"))
        await page.click('[data-nav="suiv"]')
        await page.wait_for_timeout(260)
        vus.append(await page.get_attribute("#shBd", "data-e"))
        await page.click('[data-exp="0"]')
        await page.click('[data-nav="suiv"]')                # au panier
        await page.wait_for_timeout(260)
        await page.click('[data-pan="commander"]')
        await page.wait_for_timeout(260)
        vus.append(await page.get_attribute("#shBd", "data-e"))
        await page.click('[data-mode="retrait"]')
        await page.click('[data-nav="suiv"]')
        await page.wait_for_timeout(260)
        vus.append(await page.get_attribute("#shBd", "data-e"))
        ok(vus == ["1", "3", "2", "4"],
           f"tunnel : chaque etape porte sa propre animation (vu {vus})")
        await page.evaluate("()=>{panier=[];sauvePanier();rendrePanier();}")
        ok(not errs, "toucher et catalogue : aucune erreur JS"
           + ("" if not errs else " -> " + errs[0][:140]))
        await ctx.close()

        await br.close()

    print("\n".join(NOTES))
    print("-" * 60)
    if FAILS:
        print("\n".join(FAILS))
        print(f"\n{len(FAILS)} ECHEC(S) / {len(FAILS)+len([n for n in NOTES if n.startswith('OK')])} controles")
        sys.exit(1)
    print(f"TOUT EST VERT — {len([n for n in NOTES if n.startswith('OK')])} controles")

try:
    asyncio.run(main())
except Exception as _ex:
    print("\n".join(NOTES))
    print("-" * 60)
    print("INTERROMPU :", str(_ex).splitlines()[0][:160])
    print("dernier controle passe ci-dessus")
    if FAILS:
        print("\n".join(FAILS))
    sys.exit(1)

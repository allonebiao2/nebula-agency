#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L'AFFICHE DE GRAIN D'ESTHÉTIQUE EN **VRAI SVG**.

⛔ Ce n'est PAS un PNG emballé dans une balise `<image>`. Tout est vectoriel :
le logo, les six icônes, le cadre, les filets, **les textes convertis en tracés**
et **le QR redessiné module par module** en rectangles. Le fichier ne référence
rien : ni fonte, ni image, ni réseau. Il s'ouvre dans un navigateur, dans
Illustrator, dans Inkscape, et part tel quel chez l'imprimeur.

⚠️ LA MISE EN PAGE N'EST PAS RECOPIÉE. Elle est **relevée dans le navigateur**
sur `affiche_institut.html`, qui est la version déja contrôlée. Retaper les
coordonnées a la main aurait créé une deuxiéme mise en page qui dérive de la
premiére des la premiére retouche : le PNG et le SVG ne seraient plus la même
affiche.

⚠️ ON PLACE LES TEXTES SUR LE BORD GAUCHE MESURÉ, pas sur un centrage recalculé.
CSS compte l'interlettrage du DERNIER caractére dans la largeur, donc un texte
centré trés espacé est en réalité décalé d'un demi-espacement vers la gauche
(2,8 px sur « COTONOU · HAIE-VIVE »). Le recentrer « correctement » ici ferait
un SVG qui ne se superpose plus au PNG. **Trois fichiers, une seule affiche.**

Sortie : `assets/docs/Affiche_Grain_Institut.svg`
Contrôle : re-rendu du SVG, QR relu dedans, et **comparaison pixel a pixel avec
le PNG de référence**. Au-dela de l'écart toléré, rien n'est écrit.
"""
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import _polices_svg as PO

ICI = os.path.dirname(os.path.abspath(__file__))
CLIENT = os.path.dirname(ICI)
os.chdir(CLIENT)

COTE = 1080
SRC = os.path.abspath("affiche_institut.html")
SVG_OUT = os.path.join("assets", "docs", "Affiche_Grain_Institut.svg")
PNG_REF = os.path.join("assets", "docs", "Affiche_Grain_Institut.png")
URL = "https://graindesthetique.com"
ROSE, ROSE_F, OR, OR_F = "#C4648A", "#A94A70", "#D4AF72", "#B08B4F"
# ⚠️ Le plancher mesuré est d'environ 1,0 : le QR a ~600 arêtes de modules et
#    le logo 55 contours, et deux documents ne rasterisent jamais une arête a
#    l'identique. On tolére 1,5 : au-dessus, c'est qu'un élément a réellement
#    bougé, changé de taille ou de couleur.
ECART_TOLERE = 1.5      # écart moyen par canal (sur 255), grain éteint, après flou

rouges, verts = [], []
ok = lambda m: verts.append(m)
ko = lambda m: rouges.append(m)

# ── ce qu'on va relever dans la page ────────────────────────────────────────
JS = r"""() => {
  const R = el => { const r = el.getBoundingClientRect();
    return {x:r.left, y:r.top, w:r.width, h:r.height}; };
  const cv = document.createElement('canvas').getContext('2d');

  // Chaque noeud de texte, avec sa boîte, son style et sa ligne de base.
  // ⚠️ On demande l'ascendante a Chrome lui-même (measureText) : recalculer
  //    depuis les métriques du fichier de fonte donne un décalage vertical,
  //    parce que Chrome ne prend pas toujours la même table.
  const textes = [];
  const marcher = (el) => {
    for (const n of el.childNodes) {
      if (n.nodeType === 3) {
        const t = n.textContent;
        if (!t.trim()) continue;
        const rg = document.createRange(); rg.selectNodeContents(n);
        const rects = [...rg.getClientRects()].filter(r => r.width > 0);
        const st = getComputedStyle(el);
        cv.font = `${st.fontStyle} ${st.fontWeight} ${st.fontSize} ${st.fontFamily}`;
        const m = cv.measureText(t);
        textes.push({
          texte: t, lignes: rects.length,
          x: rects[0].left, y: rects[0].top, w: rects[0].width, h: rects[0].height,
          asc: m.fontBoundingBoxAscent, desc: m.fontBoundingBoxDescent,
          famille: st.fontFamily.split(',')[0].replace(/["']/g, '').trim(),
          style: st.fontStyle, poids: parseInt(st.fontWeight),
          taille: parseFloat(st.fontSize),
          tracking: st.letterSpacing === 'normal' ? 0 : parseFloat(st.letterSpacing),
          couleur: st.color,
        });
      } else if (n.nodeType === 1 && n.tagName.toLowerCase() !== 'svg') {
        marcher(n);
      }
    }
  };
  marcher(document.getElementById('aff'));

  // Les SVG déja vectoriels : on les transplante tels quels.
  const svgs = [...document.querySelectorAll('#aff svg')]
    .filter(s => !s.classList.contains('grain'))
    .map(s => ({...R(s), vb: s.getAttribute('viewBox'),
                dedans: s.innerHTML,
                classe: (s.classList.contains('qrsvg') ? 'qr'
                        : s.closest('.ico') ? 'ico' : s.closest('.oeil') ? 'oeil'
                        : s.closest('.it') ? 'it' : 'logo'),
                trait: getComputedStyle(s).stroke,
                epaisseur: parseFloat(getComputedStyle(s).strokeWidth) || 0,
                remplissage: getComputedStyle(s).fill}));

  const boite = s => { const e = document.querySelector(s); return e ? R(e) : null; };
  const boites = s => [...document.querySelectorAll(s)].map(R);
  return {textes, svgs, formes: {
    cadre: boite('.cadre'), eq: boites('.eq'),
    fl: boite('.fl'), fr: boite('.fr'), gem: boite('.gem'),
    surfilets: boites('.sur i'),
    points: boites('.maisons i').concat(boites('.sep')),
    carte: boite('.carte'), oeil: boite('.oeil'),
    barre: boite('.barre'),
  }};
}"""


def relever():
    from playwright.sync_api import sync_playwright
    c = glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=c[0] if c else None)
        pg = b.new_page(viewport={"width": COTE, "height": COTE})
        pg.goto("file://" + SRC, wait_until="networkidle"); pg.wait_for_timeout(900)
        if not pg.evaluate("() => document.fonts.check(\"400 30px 'Cormorant Garamond'\")"):
            sys.exit("⛔ les fontes ne sont pas chargées dans la page de référence")
        g = pg.evaluate(JS)
        b.close()
    return g


def rgb(css, defaut="#000000"):
    """Une couleur calculée par le navigateur en couple (hex, alpha).

    ⚠️ `fill` vaut « none » sur les icônes au trait, et `stroke` vaut « none »
    sur le logo. Ce n'est pas une erreur, c'est le CSS : il faut le rendre tel
    quel, pas essayer de le convertir.
    """
    css = (css or "").strip()
    if not css.startswith(("rgb(", "rgba(")):
        return (css if css in ("none", "transparent") or css.startswith("#") else defaut), 1.0
    v = [float(x) for x in css[css.find("(") + 1:css.find(")")].split(",")]
    return "#%02x%02x%02x" % (int(v[0]), int(v[1]), int(v[2])), (v[3] if len(v) > 3 else 1.0)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    from PIL import Image, ImageFilter
    if not os.path.exists(SRC):
        sys.exit("⛔ affiche_institut.html absent : lance _build_affiche_institut.py")
    polices = PO.charger()
    g = relever()
    out = []

    # ── le fond, les seuls éléments réécrits a la main (un dégradé ne se reléve pas)
    out.append(f"""<defs>
<radialGradient id="h" gradientUnits="userSpaceOnUse" cx="540.0" cy="-86.4" r="1134.0" gradientTransform="translate(540.0,-86.4) scale(1,0.64762) translate(-540.0,--86.4)"><stop offset="0" stop-color="#FCEAF1"/><stop offset=".58" stop-color="#FCEAF1" stop-opacity="0"/></radialGradient><radialGradient id="o" gradientUnits="userSpaceOnUse" cx="1166.4" cy="1144.8" r="842.4" gradientTransform="translate(1166.4,1144.8) scale(1,0.74359) translate(-1166.4,-1144.8)"><stop offset="0" stop-color="#D4AF72" stop-opacity=".30"/><stop offset=".62" stop-color="#D4AF72" stop-opacity="0"/></radialGradient><radialGradient id="r" gradientUnits="userSpaceOnUse" cx="-108.0" cy="1080.0" r="756.0" gradientTransform="translate(-108.0,1080.0) scale(1,0.74286) translate(--108.0,-1080.0)"><stop offset="0" stop-color="#C4648A" stop-opacity=".16"/><stop offset=".60" stop-color="#C4648A" stop-opacity="0"/></radialGradient>
<linearGradient id="gl"><stop offset="0" stop-color="{OR}" stop-opacity="0"/><stop offset="1" stop-color="{OR}"/></linearGradient>
<linearGradient id="gr"><stop offset="0" stop-color="{OR}"/><stop offset="1" stop-color="{OR}" stop-opacity="0"/></linearGradient>
<linearGradient id="gb"><stop offset="0" stop-color="{ROSE}" stop-opacity="0"/><stop offset=".28" stop-color="{ROSE}"/><stop offset=".5" stop-color="{OR}"/><stop offset=".72" stop-color="{ROSE}"/><stop offset="1" stop-color="{ROSE}" stop-opacity="0"/></linearGradient>
<radialGradient id="mg" gradientUnits="userSpaceOnUse" cx="540.0" cy="496.8" r="712.8" gradientTransform="translate(540.0,496.8) scale(1,0.90909) translate(-540.0,-496.8)"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></radialGradient>
<!-- ⚠️ Un masque SVG pése la LUMINANCE fois l'alpha, un masque CSS ne pése
     que l'alpha. Avec un dégradé noir-transparent vers blanc-opaque, la
     courbe devenait t^2 au lieu de t, et le grain ressortait plus faible au
     milieu que dans le HTML. Blanc partout, seul l'alpha varie. -->
<mask id="mgrain"><rect width="{COTE}" height="{COTE}" fill="url(#mg)"/></mask>
<filter id="grain" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency="0.86" numOctaves="3" stitchTiles="stitch"/>
<feColorMatrix type="saturate" values="0"/>
<feComponentTransfer><feFuncA type="linear" slope="0.13"/></feComponentTransfer></filter>
<filter id="ombreQR" x="-30%" y="-30%" width="160%" height="180%">
<feDropShadow dx="0" dy="22" stdDeviation="15" flood-color="{ROSE_F}" flood-opacity=".42"/></filter>
<filter id="ombreOeil" x="-40%" y="-40%" width="180%" height="180%">
<feDropShadow dx="0" dy="3" stdDeviation="5.5" flood-color="#1A0E14" flood-opacity=".13"/></filter>
</defs>""")
    out.append(f'<rect width="{COTE}" height="{COTE}" fill="#FDF7F4"/>')
    for i in ("r", "o", "h"):
        out.append(f'<rect width="{COTE}" height="{COTE}" fill="url(#{i})"/>')
    out.append(f'<g id="couche-grain" mask="url(#mgrain)" opacity=".5"><rect width="{COTE}" height="{COTE}" filter="url(#grain)"/></g>')

    # ── le cadre et les équerres
    f = g["formes"]
    c = f["cadre"]
    out.append(f'<rect x="{c["x"]+.5:.1f}" y="{c["y"]+.5:.1f}" width="{c["w"]-1:.1f}" height="{c["h"]-1:.1f}" fill="none" stroke="{OR}" stroke-opacity=".42"/>')
    out.append(f'<rect x="{c["x"]+9.5:.1f}" y="{c["y"]+9.5:.1f}" width="{c["w"]-19:.1f}" height="{c["h"]-19:.1f}" fill="none" stroke="{OR}" stroke-opacity=".20"/>')
    for i, e in enumerate(f["eq"]):
        haut, gauche = e["y"] < COTE / 2, e["x"] < COTE / 2
        x0, y0, x1, y1 = e["x"], e["y"], e["x"] + e["w"], e["y"] + e["h"]
        cx, cy = (x0 if gauche else x1), (y0 if haut else y1)
        d = (f'M{(x1 if gauche else x0):.1f},{cy+ (1 if haut else -1):.1f} L{cx+(1 if gauche else -1):.1f},{cy+(1 if haut else -1):.1f} '
             f'L{cx+(1 if gauche else -1):.1f},{(y1 if haut else y0):.1f}')
        out.append(f'<path d="{d}" fill="none" stroke="{OR}" stroke-opacity=".85" stroke-width="2"/>')

    # ── filets, gemme, points
    out.append(f'<rect x="{f["fl"]["x"]:.1f}" y="{f["fl"]["y"]:.1f}" width="{f["fl"]["w"]:.1f}" height="1" fill="url(#gl)"/>')
    out.append(f'<rect x="{f["fr"]["x"]:.1f}" y="{f["fr"]["y"]:.1f}" width="{f["fr"]["w"]:.1f}" height="1" fill="url(#gr)"/>')
    gm = f["gem"]
    out.append(f'<rect x="{gm["x"]:.1f}" y="{gm["y"]:.1f}" width="{gm["w"]:.1f}" height="{gm["h"]:.1f}" fill="{ROSE}" transform="rotate(45 {gm["x"]+gm["w"]/2:.1f} {gm["y"]+gm["h"]/2:.1f})"/>')
    for s in f["surfilets"]:
        out.append(f'<rect x="{s["x"]:.1f}" y="{s["y"]:.1f}" width="{s["w"]:.1f}" height="1" fill="{OR}" fill-opacity=".55"/>')
    for p in f["points"]:
        out.append(f'<circle cx="{p["x"]+p["w"]/2:.2f}" cy="{p["y"]+p["h"]/2:.2f}" r="{p["w"]/2:.2f}" fill="{OR}"/>')
    b = f["barre"]
    out.append(f'<rect x="{b["x"]:.1f}" y="{b["y"]:.1f}" width="{b["w"]:.1f}" height="{b["h"]:.1f}" fill="url(#gb)"/>')

    # ── la carte du QR : les anneaux du box-shadow, redessinés en rectangles
    ca = f["carte"]; R0 = 20
    for pousse, couleur, opac in ((8, OR, .28), (7, "#FFFFFF", 1), (1, OR, .55), (0, "#FFFFFF", 1)):
        filtre = ' filter="url(#ombreQR)"' if pousse == 8 else ""
        out.append(f'<rect x="{ca["x"]-pousse:.1f}" y="{ca["y"]-pousse:.1f}" '
                   f'width="{ca["w"]+2*pousse:.1f}" height="{ca["h"]+2*pousse:.1f}" '
                   f'rx="{R0+pousse}" fill="{couleur}" fill-opacity="{opac}"{filtre}/>')

    # ⚡ Le QR n'est plus refait ici : il est vectoriel DANS le HTML et se
    #    transplante comme le logo. Un seul QR pour le PNG, le PDF et le SVG.

    # ── les SVG déja vectoriels : transplantés a leur place mesurée
    # ⛔ L'ORDRE COMPTE, et il coûtait cher : le fond blanc de l'oeil était
    #    dessiné AVANT le QR, donc le QR le recouvrait entiérement et la marque
    #    se posait sur les modules noirs. Le QR restait lisible, mais le centre
    #    n'était plus le même dessin que dans le PNG. Trouvé sur la carte
    #    d'écart, pas par un contrôle : le seul point encore lumineux.
    ordre = {"logo": 0, "ico": 1, "it": 2, "qr": 3, "oeil": 4}
    for s in sorted(g["svgs"], key=lambda s: ordre.get(s["classe"], 9)):
        if s["classe"] == "oeil":
            oe = f["oeil"]
            out.append(f'<rect x="{oe["x"]:.1f}" y="{oe["y"]:.1f}" width="{oe["w"]:.1f}" '
                       f'height="{oe["h"]:.1f}" rx="11" fill="#FFFFFF" filter="url(#ombreOeil)"/>')
        vb = [float(v) for v in re.split(r"[ ,]+", s["vb"].strip())]
        k = s["w"] / vb[2]
        dedans = s["dedans"].replace("currentColor", rgb(s["remplissage"], "#1A0E14")[0])
        style = f'fill="{rgb(s["remplissage"], "#1A0E14")[0]}"' if s["classe"] in ("logo", "oeil", "qr") else (
            f'fill="none" stroke="{rgb(s["trait"])[0]}" stroke-width="{s["epaisseur"]/k:.2f}" '
            f'stroke-linecap="round" stroke-linejoin="round"')
        out.append(f'<g transform="translate({s["x"]:.2f},{s["y"]:.2f}) scale({k:.5f}) '
                   f'translate({-vb[0]:.2f},{-vb[1]:.2f})" {style}>{dedans}</g>')

    # ── LES TEXTES, CONVERTIS EN TRACÉS
    manques, n_glyphes = [], 0
    for t in g["textes"]:
        if t["lignes"] != 1:
            ko(f"« {t['texte'][:28]} » tient sur {t['lignes']} lignes : "
               f"le relevé ne sait placer qu'une ligne par noeud de texte")
            continue
        pol = PO.choisir(polices, t["famille"], t["style"], t["poids"])
        absents = pol.couvre(t["texte"])
        if absents:
            manques.append((t["texte"][:24], absents))
            continue
        morceaux, largeur, notdef, largeur_css = pol.composer(t["texte"], t["taille"], t["tracking"])
        if notdef:
            ko(f"{notdef} glyphe(s) NON TROUVÉ(S) dans « {t['texte'][:26]} » "
               f"({t['famille']} {t['style']} {t['poids']}) : ça imprimerait des cases")
            continue
        # ⚡ La largeur composée doit retomber sur celle mesurée par le
        #    navigateur. Si elle s'en écarte, c'est que la fonte utilisée ici
        #    n'est pas celle que Chrome a rendue (mauvaise graisse, mauvaise
        #    instance variable) : le texte dériverait le long de la ligne.
        if abs(largeur_css - t["w"]) > max(1.2, t["w"] * 0.010):
            ko(f"largeur composée {largeur_css:.1f} px contre {t['w']:.1f} mesurée "
               f"dans « {t['texte'][:26]} » : ce n'est pas la même fonte")
        base = t["y"] + t["asc"] * (t["h"] / max(t["asc"] + t["desc"], 1e-6))
        couleur, alpha = rgb(t["couleur"])
        op = f' fill-opacity="{alpha:.3f}"' if alpha < .999 else ""
        d = []
        for chemin, dx, dy, k in morceaux:
            d.append(f'<path transform="translate({t["x"]+dx:.2f},{base+dy:.2f}) '
                     f'scale({k:.5f},{-k:.5f})" d="{chemin}"/>')
            n_glyphes += 1
        out.append(f'<g fill="{couleur}"{op}>{"".join(d)}</g>')

    if manques:
        for txt, cs in manques:
            ko(f"GLYPHES ABSENTS dans « {txt} » : {cs}")

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {COTE} {COTE}" '
           f'width="{COTE}" height="{COTE}">'
           f'<title>Grain d\'Esthétique, institut de beauté à Cotonou Haie-Vive</title>'
           f'<desc>Affiche carrée. Tous les textes sont vectorisés, aucune fonte requise. '
           f'QR vers {URL}.</desc>'
           + "".join(out) + "</svg>")

    # ── LES CONTRÔLES ───────────────────────────────────────────────────────
    ok(f"{len(g['textes'])} blocs de texte convertis, {n_glyphes} glyphes en tracés")
    if "<text" in svg:
        ko("il reste un <text> : le fichier dépendrait d'une fonte chez l'imprimeur")
    else:
        ok("aucun <text> : rien ne dépend d'une fonte installée")
    dehors = re.sub(r'<(title|desc)>.*?</\1>', '', svg, flags=re.S)
    dehors = re.sub(r'xmlns(:\w+)?="[^"]*"', '', dehors)
    if re.search(r'(https?:)?//|xlink:href|<image|@font-face|src=', dehors):
        trouve = re.findall(r'.{0,40}(?:(?:https?:)?//|xlink:href|<image|@font-face|src=).{0,25}', dehors)[:3]
        ko(f"le SVG référence quelque chose d'extérieur : {trouve}")
    else:
        ok("autonome : aucune référence externe, aucune image")

    tmp = os.path.join("assets", "docs", "_tmp.svg")
    open(tmp, "w", encoding="utf-8").write(svg)
    from playwright.sync_api import sync_playwright
    c = glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome")
    rendu = os.path.join("assets", "docs", "_tmp_svg.png")
    nu_svg = os.path.join("assets", "docs", "_tmp_svg_nu.png")
    nu_html = os.path.join("assets", "docs", "_tmp_html_nu.png")
    ETEINDRE = ("() => { const g = document.getElementById('couche-grain') "
                "|| document.querySelector('.grain'); if (g) g.style.display = 'none'; "
                "return !!g; }")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=c[0] if c else None)
        pg = b.new_page(viewport={"width": COTE, "height": COTE}, device_scale_factor=4)
        pg.goto("file://" + os.path.abspath(tmp)); pg.wait_for_timeout(700)
        pg.screenshot(path=rendu, clip={"x": 0, "y": 0, "width": COTE, "height": COTE})
        # ⚠️ Le grain est une texture PROCÉDURALE a 13 % d'alpha. Deux documents
        #    différents ne la rasterisent jamais pareil, et ce n'est pas un
        #    défaut : le comparer revient a comparer du bruit. On l'éteint des
        #    DEUX côtés, et ce qui reste est du contenu — un décalage, une
        #    taille, une couleur. On vérifie quand même qu'il EXISTE.
        if not pg.evaluate(ETEINDRE):
            ko("le calque de grain est introuvable dans le SVG")
        pg.wait_for_timeout(250)
        pg.screenshot(path=nu_svg, clip={"x": 0, "y": 0, "width": COTE, "height": COTE})
        pg2 = b.new_page(viewport={"width": COTE, "height": COTE}, device_scale_factor=4)
        pg2.goto("file://" + SRC, wait_until="networkidle"); pg2.wait_for_timeout(900)
        pg2.evaluate(ETEINDRE); pg2.wait_for_timeout(250)
        pg2.screenshot(path=nu_html, clip={"x": 0, "y": 0, "width": COTE, "height": COTE})
        b.close()

    import cv2
    im = Image.open(rendu).convert("RGB")
    lu, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR))
    ok(f"QR relu dans le SVG rendu : « {lu} »") if lu == URL else \
        ko(f"QR ILLISIBLE dans le SVG : « {lu} »")

    # ⚡ le contrôle qui compte : le SVG et le PNG doivent être la MÊME affiche
    if os.path.exists(nu_svg) and os.path.exists(nu_html):
        im = Image.open(nu_svg).convert("RGB")
        ref = Image.open(nu_html).convert("RGB")
        brut = np.abs(np.asarray(im, float) - np.asarray(ref, float)).mean()
        # ⚠️ On ne juge PAS sur l'écart brut. Un glyphe dessiné en tracé n'est
        #    pas anticrénelé comme le même glyphe rendu par le moteur de texte,
        #    et le grain est un bruit procédural : les deux font du bruit sans
        #    qu'aucun élément n'ait bougé. Un léger flou les efface et ne laisse
        #    que ce qui compte — un décalage, une taille, une couleur fausse.
        fl = ImageFilter.GaussianBlur(2)
        net = np.abs(np.asarray(im.filter(fl), float)
                     - np.asarray(ref.filter(fl), float)).mean()
        (ok if net <= ECART_TOLERE else ko)(
            f"superposition au PNG : écart {net:.2f}/255 hors anticrénelage "
            f"(toléré {ECART_TOLERE}) — brut {brut:.2f}")
    else:
        ko("rendus de comparaison absents : superposition invérifiable")

    print("\n".join("  ✅ " + v for v in verts))
    if rouges and "--diagnostic" in sys.argv:
        print("\n".join("  ⛔ " + r for r in rouges))
        print("  ⚠️ MODE DIAGNOSTIC : on écrit quand même pour pouvoir regarder.")
        rouges.clear()
    if rouges:
        print("\n".join("  ⛔ " + r for r in rouges))
        for x in (tmp, rendu, nu_svg, nu_html):
            os.path.exists(x) and os.remove(x)
        sys.exit(f"\n⛔ {len(rouges)} rouge(s) : RIEN N'A ÉTÉ ÉCRIT.")

    os.replace(tmp, SVG_OUT)
    [os.path.exists(x) and os.remove(x) for x in (rendu, nu_svg, nu_html)]
    print(f"\n  {len(verts)} contrôles verts, 0 rouge.")
    print(f"  SVG  {SVG_OUT}  {os.path.getsize(SVG_OUT)//1024} Ko  (vectoriel, autonome)")


if __name__ == "__main__":
    main()

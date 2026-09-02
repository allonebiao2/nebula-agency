#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L'AFFICHE CARRÉE 1:1 DE GRAIN D'ESTHÉTIQUE, a coller dans l'institut.

Ce script écrit `affiche_institut.html`. `_render_affiche_institut.py` le
photographie ensuite en PNG et en PDF, et REFUSE d'écrire si quelque chose
cloche.

────────────────────────────────────────────────────────────────────────────
LA PHRASE, AVANT LE DESSIN (régle maison : sans phrase, on décore)
  Un institut de beauté comme celui-ci, c'est **un grain de peau qu'on révéle**.
  Le nom le dit déja. L'objet concret est donc **le grain** : une poussiére
  trés fine, plus dense sur les bords, qui s'efface au centre la ou le regard
  se pose. C'est le fond de l'affiche, et ce n'est pas un ornement pris au
  hasard : c'est le métier.
  Et **sa marque est un oeil** : c'est lui qui tient le haut de l'affiche, et
  c'est lui qu'on retrouve au centre du QR.

CE QUE L'ANCIENNE AFFICHE N'AVAIT PAS, et qui manquait vraiment
  - **son logo** (elle n'y était pas, le nom était simplement retapé) ;
  - **ce que la maison fait** : les 6 familles de soins ;
  - **les maisons partenaires** (Sothys Paris, Sultane de Saba) : c'est ce qui
    dit « haut de gamme » sans avoir a l'écrire ;
  - **les horaires** : une affiche murale sans horaires oblige a demander ;
  - un QR qui mangeait un tiers de l'affiche : ici il est plus petit ET plus
    lisible, parce qu'il est posé sur du blanc franc et entouré de vide.

⛔ RIEN N'EST INVENTÉ ICI
  Le numéro, l'adresse, les horaires et les six familles sont **lus dans le
  site** (`grain-esthetique-LIVE.html`, bloc JSON-LD compris). L'accroche
  « La beauté est un art de vivre » est **sa phrase**, publiée sur sa page
  A Propos. Aucun prix, aucune note, aucun avis, aucun slogan fabriqué.
  ⚠️ `Lot N 18` figure dans notre CONTEXT.md mais **PAS sur le site** : on ne
  le met pas, sinon l'affiche et le site donnent deux adresses différentes.

⚠️ LES FONTES SONT EMBARQUÉES EN BASE64. Une affiche qui va chez l'imprimeur ne
  peut pas dépendre du réseau : sans ça, le jour ou Google Fonts ne répond pas,
  Cormorant retombe sur un serif générique et **personne ne le voit avant que
  les exemplaires soient payés**. Le rendu vérifie que les fontes ont chargé.
"""
import base64, io, os, re, sys, urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
CLIENT = os.path.dirname(ICI)
os.chdir(CLIENT)

# ── LES DONNÉES, TOUTES LUES DANS LE SITE ───────────────────────────────────
SITE_HTML = "grain-esthetique-LIVE.html"
URL = "https://graindesthetique.com"

ROSE, ROSE_F, OR, OR_F = "#C4648A", "#A94A70", "#D4AF72", "#B08B4F"
ENCRE, ENCRE_2 = "#1A0E14", "#4A3540"
PAPIER = "#FDF7F4"

FAMILLES = [
    ("Visage",        "eclat"),
    ("Corps",         "feuille"),
    ("Épilation",     "goutte"),
    ("Mains & Pieds", "vernis"),
    ("Soins Avancés", "gemme"),
    ("Espace Hommes", "noeud"),
]

# ⚠️ Les icônes reprennent le VOCABULAIRE DU SITE, section par section :
#    Visage = Radiance (l'éclat) · Corps = Respiration (la feuille) ·
#    Épilation = Glisse (la goutte) · Mains & Pieds = Vernis ·
#    Soins Avancés = la gemme · Espace Hommes = le noeud papillon doré.
#    Une affiche qui parle une autre langue que le site n'est pas la même maison.
ICONES = {
 "eclat":  '<path d="M12 3.2c.7 4.3 1.8 5.4 6.1 6.1-4.3.7-5.4 1.8-6.1 6.1-.7-4.3-1.8-5.4-6.1-6.1 4.3-.7 5.4-1.8 6.1-6.1Z"/><path d="M18.4 15.1c.3 1.9.8 2.4 2.7 2.7-1.9.3-2.4.8-2.7 2.7-.3-1.9-.8-2.4-2.7-2.7 1.9-.3 2.4-.8 2.7-2.7Z"/>',
 "feuille":'<path d="M20 4.5c0 8.2-4.3 12.4-10.4 12.4-2.2 0-4-.6-5.1-1.6C3.4 8.5 8.6 4.5 20 4.5Z"/><path d="M4.2 20.2C6.5 14.4 10.3 10.6 15.6 8"/>',
 "goutte": '<path d="M12 3.4c3.4 4 5.4 6.8 5.4 9.4a5.4 5.4 0 0 1-10.8 0c0-2.6 2-5.4 5.4-9.4Z"/><path d="M9.4 13.6a2.7 2.7 0 0 0 2.2 3.6"/>',
 "vernis": '<path d="M9.6 9.1h4.8c.7 0 1.2.5 1.3 1.2l.6 8.6c0 .8-.5 1.4-1.3 1.4H9c-.8 0-1.4-.6-1.3-1.4l.6-8.6c.1-.7.6-1.2 1.3-1.2Z"/><path d="M10.4 9.1V6.4h3.2v2.7"/><path d="M11 3.5h2v2.9h-2z"/><path d="M8.1 13.4h7.8"/>',
 "gemme":  '<path d="M8.1 4h7.8l3.6 5-7.5 10.9L4.5 9Z"/><path d="M4.5 9h15"/><path d="M8.1 4 12 19.9 15.9 4"/>',
 "noeud":  '<path d="M10.5 10.1 4.9 6.9c-.9-.5-1.7.1-1.7 1v8.2c0 .9.8 1.5 1.7 1l5.6-3.2Z"/><path d="m13.5 10.1 5.6-3.2c.9-.5 1.7.1 1.7 1v8.2c0 .9-.8 1.5-1.7 1l-5.6-3.2Z"/><rect x="10.2" y="9.1" width="3.6" height="5.8" rx="1.1"/>',
}


def lire_le_site():
    """Numéro, ville, quartier et horaires : lus, jamais recopiés a la main.

    ⚠️ Recopier, c'est fabriquer une deuxiéme vérité. Le jour ou le site change
    d'horaires, l'affiche continue d'annoncer les anciens et c'est la cliente
    qui trouve porte close.
    """
    h = open(SITE_HTML, encoding="utf-8").read()
    m = re.search(r'application/ld\+json[^>]*>(.*?)</script>', h, re.S)
    if not m:
        sys.exit("⛔ pas de JSON-LD dans le site : les données ne sont pas vérifiables")
    import json
    d = json.loads(m.group(1))
    tel = d["telephone"].replace("+229", "")
    tel = " ".join([tel[i:i+2] for i in range(0, len(tel), 2)])
    ho = d["openingHoursSpecification"][0]
    jours = {"Tuesday": "mardi", "Saturday": "samedi"}
    lib = f'{jours[ho["dayOfWeek"][0]]} à {jours[ho["dayOfWeek"][-1]]}'
    heures = f'{ho["opens"].replace(":00","h").replace(":","h")} – {ho["closes"].replace(":00","h").replace(":","h")}'
    a = d["address"]
    return {
        "tel": tel, "jours": lib.capitalize(), "heures": heures,
        "lieu": f'{a["addressLocality"]} · {a["streetAddress"]}'.upper(),
        "url_site": d["url"].rstrip("/"),
    }


def fontes():
    """Télécharge les woff2 Google et les inline. Refuse de continuer sans."""
    css_url = ("https://fonts.googleapis.com/css2"
               "?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400;1,600"
               "&family=Jost:wght@300;400;500;600&display=swap")
    req = urllib.request.Request(css_url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"})
    css = urllib.request.urlopen(req, timeout=40).read().decode()
    urls = sorted(set(re.findall(r"url\((https://[^)]+\.woff2)\)", css)))
    if not urls:
        sys.exit("⛔ aucune fonte récupérée : l'affiche partirait avec un serif générique")
    cache = {}
    for u in urls:
        cache[u] = urllib.request.urlopen(u, timeout=40).read()
    for u, data in cache.items():
        css = css.replace(u, "data:font/woff2;base64," + base64.b64encode(data).decode())
    print(f"fontes embarquées : {len(urls)} fichiers, "
          f"{sum(len(v) for v in cache.values())//1024} Ko")
    return css


def le_qr():
    """QR vers le domaine, correction H, avec l'oeil de la marque au centre.

    ⚠️ La correction H tolére ~30 % de perte : un centre couvert a ~16 % passe
    largement. Mais on ne le croit pas sur parole, **le rendu relit le QR dans
    l'image finale** — c'est la seule preuve qui compte.
    """
    import qrcode
    from qrcode.constants import ERROR_CORRECT_H
    q = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_H, box_size=22, border=1)
    q.add_data(URL); q.make(fit=True)
    img = q.make_image(fill_color=ENCRE, back_color="#FFFFFF").convert("RGB")
    buf = io.BytesIO(); img.save(buf, format="PNG")
    print(f"QR : {img.size[0]}px, version {q.version}, correction H")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def svg_inline(chemin, hauteur_css):
    svg = open(chemin, encoding="utf-8").read()
    svg = re.sub(r'\swidth="[^"]*"', "", svg, count=1)
    svg = re.sub(r'\sheight="[^"]*"', "", svg, count=1)
    return svg.replace("<svg ", f'<svg style="height:{hauteur_css};width:auto;display:block" ', 1)


D = lire_le_site()
CSS_FONTES = fontes()
QR64 = le_qr()
LOGO = svg_inline("assets/images/logo-grain-esthetique.svg", "170px")
MARQUE = svg_inline("assets/images/logo-grain-marque.svg", "33px")

cases = "".join(
    f'<div class="fam"><span class="ico"><svg viewBox="0 0 24 24">{ICONES[k]}</svg></span>'
    f'<span class="fam-t">{nom}</span></div>'
    for nom, k in FAMILLES
)

HTML = f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<title>Affiche Grain d'Esthétique</title>
<style>
{CSS_FONTES}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{background:#888}}
.aff{{
  width:1080px;height:1080px;position:relative;overflow:hidden;
  background:
    radial-gradient(105% 68% at 50% -8%, #FCEAF1 0%, rgba(252,234,241,0) 58%),
    radial-gradient(78% 58% at 108% 106%, rgba(212,175,114,.30) 0%, rgba(212,175,114,0) 62%),
    radial-gradient(70% 52% at -10% 100%, rgba(196,100,138,.16) 0%, rgba(196,100,138,0) 60%),
    {PAPIER};
  font-family:'Jost',sans-serif;color:{ENCRE};
  display:flex;flex-direction:column;align-items:center;text-align:center;
  padding:58px 80px 44px;
}}
/* ── LE GRAIN : la matiére du métier, pas une texture décorative.
      Dense sur les bords, effacé au centre — le regard se pose la ou c'est net. */
.grain{{position:absolute;inset:0;pointer-events:none;opacity:.5;
  -webkit-mask-image:radial-gradient(66% 60% at 50% 46%,transparent 0%,#000 100%);
          mask-image:radial-gradient(66% 60% at 50% 46%,transparent 0%,#000 100%)}}
/* le cadre : double filet or, respirant, jamais coupé par le bord */
.cadre{{position:absolute;inset:34px;border:1px solid rgba(212,175,114,.42);pointer-events:none}}
.cadre::after{{content:"";position:absolute;inset:9px;border:1px solid rgba(212,175,114,.20)}}
.eq{{position:absolute;width:56px;height:56px;border:2px solid rgba(212,175,114,.85);pointer-events:none}}
.eq1{{top:34px;left:34px;border-right:0;border-bottom:0}}
.eq2{{top:34px;right:34px;border-left:0;border-bottom:0}}
.eq3{{bottom:34px;left:34px;border-right:0;border-top:0}}
.eq4{{bottom:34px;right:34px;border-left:0;border-top:0}}

.z{{position:relative;z-index:2;width:100%}}
.logo{{display:flex;justify-content:center;color:{ENCRE}}}

.filet{{display:flex;align-items:center;justify-content:center;gap:15px;margin:15px 0 11px}}
.fl,.fr{{width:104px;height:1px}}
.fl{{background:linear-gradient(90deg,transparent,{OR})}}
.fr{{background:linear-gradient(90deg,{OR},transparent)}}
.gem{{width:8px;height:8px;background:{ROSE};transform:rotate(45deg)}}
.lieu{{font-size:15.5px;letter-spacing:.36em;color:#6F5462;font-weight:400}}

.accroche{{font-family:'Cormorant Garamond',serif;font-style:italic;font-weight:400;
  font-size:30px;color:{ROSE_F};margin-top:10px;letter-spacing:.005em}}

.soins{{margin-top:17px}}
.sur{{font-size:12.5px;letter-spacing:.40em;color:{OR_F};font-weight:500;margin-bottom:16px;display:flex;align-items:center;justify-content:center;gap:16px}}
.sur i{{width:62px;height:1px;background:rgba(212,175,114,.55);display:block;flex:none}}
.grille{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px 4px;max-width:600px;margin:0 auto}}
.fam{{display:flex;flex-direction:column;align-items:center;gap:9px}}
.ico svg{{width:32px;height:32px;fill:none;stroke:{ROSE};stroke-width:1.45;
  stroke-linecap:round;stroke-linejoin:round}}
.fam-t{{font-size:17px;font-weight:400;color:{ENCRE_2};letter-spacing:.015em;white-space:nowrap}}

.maisons{{margin-top:17px;display:flex;align-items:center;justify-content:center;gap:15px;
  font-size:13px;letter-spacing:.26em;color:{OR_F};font-weight:500}}
.maisons i{{width:4px;height:4px;background:{OR};border-radius:50%;display:block}}

.bloc-qr{{margin-top:17px;display:flex;flex-direction:column;align-items:center}}
.carte{{position:relative;background:#fff;padding:17px;border-radius:20px;
  box-shadow:0 22px 46px -20px rgba(169,74,112,.42),
             0 0 0 1px rgba(212,175,114,.55),
             0 0 0 7px #fff,
             0 0 0 8px rgba(212,175,114,.28)}}
.carte img{{width:194px;height:194px;display:block;image-rendering:pixelated}}
.oeil{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:52px;height:52px;background:#fff;border-radius:11px;
  display:flex;align-items:center;justify-content:center;color:{ENCRE};
  box-shadow:0 3px 11px rgba(26,14,20,.13)}}
.cta{{font-family:'Cormorant Garamond',serif;font-size:27px;line-height:1.32;
  color:#2A1B24;margin-top:13px;max-width:660px}}
.cta b{{color:{ROSE_F};font-weight:600;font-style:italic}}
.web{{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:25px;
  color:{ROSE_F};margin-top:6px;letter-spacing:.01em}}

.pied{{margin-top:auto;width:100%}}
.infos{{display:flex;align-items:center;justify-content:center;gap:17px;flex-wrap:wrap;
  font-size:17px;color:{ENCRE};font-weight:400}}
.it{{display:inline-flex;align-items:center;gap:8px;white-space:nowrap}}
.it svg{{width:19px;height:19px;fill:none;stroke:{ROSE};stroke-width:1.6;
  stroke-linecap:round;stroke-linejoin:round;flex:none}}
.sep{{width:4px;height:4px;background:{OR};border-radius:50%;display:block}}
.barre{{margin-top:16px;height:2.5px;width:100%;
  background:linear-gradient(90deg,transparent,{ROSE} 28%,{OR} 50%,{ROSE} 72%,transparent)}}
.credit{{margin-top:10px;font-size:10.5px;letter-spacing:.30em;color:rgba(138,80,100,.52);
  font-weight:400}}
</style></head><body><div class="aff" id="aff">

<svg class="grain" xmlns="http://www.w3.org/2000/svg"><filter id="g">
<feTurbulence type="fractalNoise" baseFrequency="0.86" numOctaves="3" stitchTiles="stitch"/>
<feColorMatrix type="saturate" values="0"/>
<feComponentTransfer><feFuncA type="linear" slope="0.13"/></feComponentTransfer>
</filter><rect width="100%" height="100%" filter="url(#g)"/></svg>

<div class="cadre"></div>
<i class="eq eq1"></i><i class="eq eq2"></i><i class="eq eq3"></i><i class="eq eq4"></i>

<div class="z logo">{LOGO}</div>

<div class="z filet"><span class="fl"></span><span class="gem"></span><span class="fr"></span></div>
<div class="z lieu">{D['lieu']}</div>

<div class="z accroche">« La beauté est un art de vivre. »</div>

<div class="z soins">
  <div class="sur"><i></i><span>LES SOINS DE LA MAISON</span><i></i></div>
  <div class="grille">{cases}</div>
</div>

<div class="z maisons"><span>SOTHYS PARIS</span><i></i><span>SULTANE DE SABA</span></div>

<div class="z bloc-qr">
  <div class="carte"><img src="{QR64}" alt="QR vers graindesthetique.com"><span class="oeil">{MARQUE}</span></div>
  <div class="cta">Toute la carte des soins,<br>et votre <b>rendez-vous</b>, en un scan.</div>
  <div class="web">graindesthetique.com</div>
</div>

<div class="z pied">
  <div class="infos">
    <span class="it"><svg viewBox="0 0 24 24"><path d="M21 16.4v2.9a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 1.1 3.6 2 2 0 0 1 3.1 1.4h2.9a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L7 9.2a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>{D['tel']}</span>
    <i class="sep"></i>
    <span class="it"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9.2"/><path d="M12 6.6V12l3.4 2.1"/></svg>{D['jours']} · {D['heures']}</span>
    <i class="sep"></i>
    <span class="it"><svg viewBox="0 0 24 24"><path d="M12 21.4s7.2-5.6 7.2-11a7.2 7.2 0 0 0-14.4 0c0 5.4 7.2 11 7.2 11Z"/><circle cx="12" cy="10.2" r="2.7"/></svg>Sur rendez-vous</span>
  </div>
  <div class="barre"></div>
  <div class="credit">VITRINE SIGNÉE NEBULA AGENCY</div>
</div>

</div></body></html>"""

open("affiche_institut.html", "w", encoding="utf-8").write(HTML)
print(f"affiche_institut.html écrit : {len(HTML)//1024} Ko (autonome, aucun réseau)")
print(f"  téléphone {D['tel']} · {D['jours']} {D['heures']} · {D['lieu']}")

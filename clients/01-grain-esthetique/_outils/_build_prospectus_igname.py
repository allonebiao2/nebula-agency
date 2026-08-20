#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prospectus A5 recto-verso « Fête de l'Igname » pour Grain d'Esthétique.

Tout est embarqué dans le HTML (fontes, logo, QR) : le fichier ne dépend d'aucun
réseau au moment de l'impression. Rendu par `_render_prospectus_igname.py`.

⚠️ Les montants viennent de la promo Fête des Pères validée par Jocelyne
   (CONTEXT.md). À reconfirmer avant impression pour cette occasion.
⚠️ Les dates sont une proposition. Bloc ZONE À CONFIRMER ci-dessous.
"""
import base64, io, os, re, sys

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ══════════════════════════════════════════════════════════════════════
# ZONE À CONFIRMER PAR JOCELYNE AVANT IMPRESSION
# ══════════════════════════════════════════════════════════════════════
PERIODE = "Du 15 au 31 août 2026"          # dates de l'offre
OFFRES = [                                  # (intitulé, précision, prix barré, prix fête)
    ("Le rituel de fête", "Soin du visage + Pédicure & Manucure", "45 000", "40 000"),
    ("Soin du visage",    "Éclat et fraîcheur avant le grand jour", "30 000", "25 000"),
    ("Hydrafacial",       "Notre soin le plus demandé",             "60 000", "45 000"),
    ("Massage relaxant",  "Une heure pour souffler",                "15 000", "12 000"),
]
# ══════════════════════════════════════════════════════════════════════

SITE = "https://graindesthetique.com"
WA_NUM = "2290197085576"                    # ⚠️ NE JAMAIS CHANGER (CLAUDE.md)
WA_TEXTE = "Bonjour ✨ Je souhaite réserver pour la Fête de l’Igname. Quelles sont vos disponibilités ?"
TEL_LISIBLE = "01 97 08 55 76"

ROSE, ROSE_SOMBRE = "#C4648A", "#8E3F5F"
OR, OR_SOMBRE = "#D4AF72", "#A97C2E"
ENCRE = "#1A0E14"


def b64(data: bytes, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(data).decode()


# ── 1. Les fontes, embarquées ────────────────────────────────────────
def fontes() -> str:
    """Récupère les woff2 Google et les inline. Sans réseau, on retombe sur les
    fontes système : la mise en page tient, le caractère change."""
    import requests
    ua = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
    url = ("https://fonts.googleapis.com/css2"
           "?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400;1,600"
           "&family=Jost:wght@300;400;500;600&display=swap")
    try:
        css = requests.get(url, headers=ua, timeout=30).text
    except Exception as e:                                    # pragma: no cover
        print("  ⚠️  fontes injoignables (%s) : repli système" % type(e).__name__)
        return ""

    # On ne garde que les blocs latin, sinon le fichier explose
    blocs, garde = [], []
    for bloc in css.split("@font-face"):
        if "src:" not in bloc:
            continue
        if "unicode-range" in bloc and "U+0000-00FF" not in bloc:
            continue
        garde.append("@font-face" + bloc)

    cache = {}
    for bloc in garde:
        m = re.search(r"url\((https://[^)]+\.woff2)\)", bloc)
        if not m:
            continue
        u = m.group(1)
        if u not in cache:
            cache[u] = requests.get(u, headers=ua, timeout=30).content
        blocs.append(bloc.replace(u, b64(cache[u], "font/woff2")))
    print(f"  fontes embarquées : {len(blocs)} coupes, "
          f"{sum(len(v) for v in cache.values())//1024} Ko")
    return "\n".join(blocs)


# ── 2. Le logo, agrandi proprement pour l'impression ─────────────────
def logo() -> str:
    """Le logo n'existe qu'en 224x162. Agrandissement x4 au Lanczos puis
    raidissement du canal alpha : sur du trait noir, ça retrouve un bord net."""
    src = os.path.join("assets", "images", "logo-grain-esthetique-detoure.png")
    im = Image.open(src).convert("RGBA")
    grand = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)
    r, g, b, a = grand.split()
    a = a.point(lambda v: 0 if v < 40 else (255 if v > 190 else int((v - 40) * 255 / 150)))
    grand = Image.merge("RGBA", (r, g, b, a))
    buf = io.BytesIO()
    grand.save(buf, format="PNG", optimize=True)
    print(f"  logo {im.size} → {grand.size}, {len(buf.getvalue())//1024} Ko")
    return b64(buf.getvalue(), "image/png")


# ── 3. Les QR ────────────────────────────────────────────────────────
def qr(donnee: str, sombre: str = "#231018") -> str:
    q = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=16, border=2)
    q.add_data(donnee)
    q.make(fit=True)
    img = q.make_image(fill_color=sombre, back_color="#ffffff").convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return b64(buf.getvalue(), "image/png")


# ── 4. L'ornement : une feuille d'igname, au trait ───────────────────
FEUILLE = """<svg class="lf" viewBox="0 0 64 46" aria-hidden="true">
  <path d="M32 43 C 12 34 5 20 12 10 C 17 3 27 4 32 12 C 37 4 47 3 52 10 C 59 20 52 34 32 43 Z"/>
  <path d="M32 43 L32 13"/>
  <path d="M32 20 C 26 18 21 15 18 11"/><path d="M32 20 C 38 18 43 15 46 11"/>
  <path d="M32 29 C 25 27 20 23 17 18"/><path d="M32 29 C 39 27 44 23 47 18"/>
</svg>"""


def construire() -> str:
    lg, css_fontes = logo(), fontes()
    qr_site = qr(SITE)
    lignes = "\n".join(
        f"""<div class="offre">
              <div class="o-txt"><div class="o-nom">{nom}</div><div class="o-det">{det}</div></div>
              <div class="o-prix"><span class="o-old">{old} F</span><span class="o-new">{new} F</span></div>
            </div>""" for nom, det, old, new in OFFRES)

    soins = [
        ("Visage", "Nettoyage, éclat, anti-âge"),
        ("Corps", "Gommage, enveloppement, massage"),
        ("Épilation", "Cire tiède, visage et corps"),
        ("Mains &amp; Pieds", "Manucure, pédicure, pose de vernis"),
        ("Soins avancés", "Hydrafacial et protocoles ciblés"),
        ("Espace Hommes", "Un espace dédié, sur rendez-vous"),
    ]
    grille = "\n".join(
        f'<div class="soin"><div class="s-nom">{n}</div><div class="s-det">{d}</div></div>'
        for n, d in soins)

    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<title>Grain d'Esthétique · Prospectus Fête de l'Igname</title>
<style>
{css_fontes}
@page {{ size: 148mm 210mm; margin: 0; }}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{background:#fff}}
.page{{width:148mm;height:210mm;position:relative;overflow:hidden;
  font-family:'Jost',-apple-system,'Segoe UI',sans-serif;color:{ENCRE};
  background:radial-gradient(120% 78% at 50% -8%,#FBE9F1 0%,#FFFFFF 44%,#FDF5F8 100%);
  display:flex;flex-direction:column;align-items:center;text-align:center}}
.page + .page{{page-break-before:always}}
.page::before,.page::after{{content:"";position:absolute;width:62mm;height:62mm;border-radius:50%;pointer-events:none}}
.page::before{{top:-24mm;left:-24mm;background:radial-gradient(circle,rgba(212,175,114,.20),transparent 68%)}}
.page::after{{bottom:-26mm;right:-26mm;background:radial-gradient(circle,rgba(196,100,138,.16),transparent 68%)}}
.corner{{position:absolute;width:13mm;height:13mm;border:.35mm solid rgba(212,175,114,.6)}}
.c1{{top:7mm;left:7mm;border-right:0;border-bottom:0}}
.c2{{top:7mm;right:7mm;border-left:0;border-bottom:0}}
.c3{{bottom:7mm;left:7mm;border-right:0;border-top:0}}
.c4{{bottom:7mm;right:7mm;border-left:0;border-top:0}}
.inner{{position:relative;z-index:2;width:100%;height:100%;padding:10mm 12mm 8mm;
  display:flex;flex-direction:column;align-items:center}}

.logo{{width:28mm;display:block;margin:0 auto}}
.rule{{display:flex;align-items:center;justify-content:center;gap:3mm;margin:3mm 0 2.5mm;width:100%}}
.rl{{width:22mm;height:.3mm;background:linear-gradient(90deg,transparent,{OR})}}
.rr{{width:22mm;height:.3mm;background:linear-gradient(90deg,{OR},transparent)}}
.gem{{width:2mm;height:2mm;background:{ROSE};transform:rotate(45deg)}}

.eyebrow{{font-size:2.7mm;letter-spacing:.42em;text-transform:uppercase;color:#A8788C;font-weight:500}}
.occasion{{display:flex;align-items:center;justify-content:center;gap:4mm;margin-top:1.5mm}}
.lf{{width:9.5mm;height:7mm;fill:none;stroke:{OR_SOMBRE};stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;opacity:.85;flex:none}}
.lf.r{{transform:scaleX(-1)}}
.fete{{font-family:'Cormorant Garamond',Georgia,serif;font-weight:600;font-size:10.5mm;line-height:1.05;
  background:linear-gradient(92deg,{OR_SOMBRE},{OR} 46%,{OR_SOMBRE});-webkit-background-clip:text;
  background-clip:text;color:transparent;white-space:nowrap}}

.phrase{{font-family:'Cormorant Garamond',Georgia,serif;font-style:italic;font-weight:400;
  font-size:7.4mm;line-height:1.16;color:{ROSE_SOMBRE};margin-top:4.5mm;max-width:112mm}}
.sub{{font-size:3mm;line-height:1.5;color:#5C4450;margin-top:3mm;max-width:100mm;font-weight:300}}

.offres{{width:100%;margin-top:4mm;display:flex;flex-direction:column;gap:0}}
.offre{{display:flex;align-items:center;justify-content:space-between;gap:4mm;
  padding:2.4mm 1mm;border-bottom:.25mm solid rgba(212,175,114,.42);text-align:left}}
.offre:first-child{{border-top:.25mm solid rgba(212,175,114,.42)}}
.o-nom{{font-family:'Cormorant Garamond',Georgia,serif;font-size:4.6mm;font-weight:600;line-height:1.1;color:{ENCRE}}}
.o-det{{font-size:2.5mm;line-height:1.25;color:#7A6270;margin-top:.5mm;font-weight:300;letter-spacing:.01em}}
.o-prix{{display:flex;align-items:baseline;gap:2.5mm;white-space:nowrap}}
.o-old{{font-size:3mm;color:#A8949E;text-decoration:line-through}}
.o-new{{font-family:'Cormorant Garamond',Georgia,serif;font-size:5.8mm;font-weight:600;color:{ROSE}}}

.periode{{margin-top:4mm;display:inline-block;padding:2mm 6mm;border-radius:99mm;
  background:linear-gradient(92deg,rgba(212,175,114,.16),rgba(196,100,138,.14));
  border:.25mm solid rgba(212,175,114,.55);
  font-size:2.9mm;letter-spacing:.2em;text-transform:uppercase;font-weight:500;color:{ROSE_SOMBRE}}}

.spacer{{flex:1}}
.cta{{font-family:'Cormorant Garamond',Georgia,serif;font-size:4.8mm;color:#2D1E27;line-height:1.35}}
.cta b{{color:{ROSE};font-weight:600;font-style:italic}}
.tel{{display:inline-flex;align-items:center;gap:2mm;margin-top:2mm;font-size:5mm;font-weight:500;letter-spacing:.02em}}
.tel svg{{width:5mm;height:5mm;fill:none;stroke:{ROSE};stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}}
.footbar{{margin-top:3.5mm;height:.7mm;width:100%;
  background:linear-gradient(90deg,transparent,{ROSE} 30%,{OR} 50%,{ROSE} 70%,transparent)}}
.web{{font-family:'Cormorant Garamond',Georgia,serif;font-style:italic;font-size:4mm;color:{ROSE};margin-top:2.5mm}}
.credit{{margin-top:1.5mm;font-size:2.1mm;letter-spacing:.28em;text-transform:uppercase;color:rgba(138,80,100,.45)}}

/* ── verso ── */
.v-titre{{font-family:'Cormorant Garamond',Georgia,serif;font-size:10.5mm;font-weight:300;line-height:1;color:{ENCRE}}}
.v-titre em{{font-style:italic;color:{ROSE}}}
.grille{{width:100%;margin-top:4mm;display:grid;grid-template-columns:1fr 1fr;gap:3mm}}
.soin{{border:.25mm solid rgba(212,175,114,.5);border-radius:2.4mm;padding:3.2mm 3.4mm;
  background:rgba(255,255,255,.62);text-align:left}}
.s-nom{{font-family:'Cormorant Garamond',Georgia,serif;font-size:4.2mm;font-weight:600;color:{ENCRE};line-height:1.1}}
.s-det{{font-size:2.5mm;color:#7A6270;margin-top:.9mm;font-weight:300;line-height:1.3}}
.maisons{{margin-top:5mm;font-size:2.6mm;letter-spacing:.22em;text-transform:uppercase;color:#9A7A88;font-weight:400}}
.infos{{margin-top:5mm;display:flex;flex-direction:column;gap:1.8mm;font-size:3.1mm;color:#3C2A34;font-weight:300}}
.infos b{{font-weight:500}}
.qrwrap{{margin-top:5mm;display:flex;flex-direction:column;align-items:center}}
.scan{{font-size:2.6mm;letter-spacing:.42em;text-transform:uppercase;color:{ROSE};font-weight:600;margin-bottom:2.5mm}}
.qrcard{{background:#fff;border-radius:4mm;padding:2.6mm;
  box-shadow:0 4mm 9mm -4mm rgba(196,100,138,.42),0 0 0 .25mm rgba(212,175,114,.55)}}
.qrcard img{{width:34mm;height:34mm;display:block;image-rendering:pixelated}}
.qrleg{{font-family:'Cormorant Garamond',Georgia,serif;font-size:4.2mm;color:#2D1E27;margin-top:4mm;
  line-height:1.35;max-width:96mm}}
.qrleg b{{color:{ROSE};font-weight:600;font-style:italic}}
</style></head><body>

<!-- ══════════════ RECTO ══════════════ -->
<div class="page">
  <div class="corner c1"></div><div class="corner c2"></div>
  <div class="corner c3"></div><div class="corner c4"></div>
  <div class="inner">
    <img class="logo" src="{lg}" alt="Grain d’Esthétique, institut de beauté">
    <div class="rule"><div class="rl"></div><div class="gem"></div><div class="rr"></div></div>

    <div class="eyebrow">À l’occasion de la</div>
    <div class="occasion">{FEUILLE}<div class="fete">Fête de l’Igname</div>{FEUILLE.replace('class="lf"', 'class="lf r"')}</div>

    <div class="phrase">La fête se prépare<br>la veille.</div>
    <div class="sub">On se retrouve, on s’habille, on se photographie. Nos rituels pour arriver
      au jour de la fête à votre avantage.</div>

    <div class="offres">{lignes}</div>
    <div class="periode">{PERIODE} · sur rendez-vous</div>

    <div class="spacer"></div>
    <div class="cta">Réservez sur <b>WhatsApp</b></div>
    <div class="tel">
      <svg viewBox="0 0 24 24"><path d="M21 16.9v2.5a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 1.1 3.7 2 2 0 0 1 3.1 1.5h2.5a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L6.7 9.3a16 16 0 0 0 6 6l1.2-1.1a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/></svg>
      {TEL_LISIBLE}
    </div>
    <div class="footbar"></div>
    <div class="web">graindesthetique.com</div>
    <div class="credit">Cotonou · Haie-Vive</div>
  </div>
</div>

<!-- ══════════════ VERSO ══════════════ -->
<div class="page">
  <div class="corner c1"></div><div class="corner c2"></div>
  <div class="corner c3"></div><div class="corner c4"></div>
  <div class="inner">
    <div class="v-titre">Nos <em>soins</em></div>
    <div class="rule"><div class="rl"></div><div class="gem"></div><div class="rr"></div></div>

    <div class="grille">{grille}</div>
    <div class="maisons">Sothys Paris · Sultane de Saba</div>

    <div class="infos">
      <div><b>Haie-Vive, Lot N 18</b> · Cotonou</div>
      <div>Mardi à samedi, 9 h à 19 h · lundi et dimanche fermé</div>
      <div>Sur rendez-vous · {TEL_LISIBLE}</div>
    </div>

    <div class="qrwrap">
      <div class="scan">Scannez-moi</div>
      <div class="qrcard"><img src="{qr_site}" alt="QR vers graindesthetique.com"></div>
      <div class="qrleg">Tous nos soins et la prise de rendez-vous,<br><b>en un scan.</b></div>
    </div>

    <div class="spacer"></div>
    <div class="footbar"></div>
    <div class="web">graindesthetique.com</div>
    <div class="credit">Vitrine signée NEBULA Agency</div>
  </div>
</div>

</body></html>"""


if __name__ == "__main__":
    print("Prospectus Fête de l'Igname · Grain d'Esthétique")
    html = construire()
    dest = os.path.join("_outils", "prospectus_igname.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  HTML : {dest} ({os.path.getsize(dest)//1024} Ko)")

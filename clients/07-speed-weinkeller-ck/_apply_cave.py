#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ajoute les 28 nouvelles bouteilles au catalogue Weinkeller + reclasse les cognacs.
Remplace UNIQUEMENT le contenu de <div class="bottles"> (préserve le drawer #caveNav & la
section). Cartes existantes gardées VERBATIM (champagne/tequila conservent leur data-sub) ;
les 6 cognacs (whisky/cognac) -> data-cat="cognac" ; les single malts (whisky/scotch) -> whisky à plat.
Idempotent (clé = slug). Nécessite _apply_tax pour aligner la TAX de app.js. UTF-8 garanti."""
import re, io
from urllib.parse import quote

F = "weinkeller.html"
WA = "https://wa.me/2290197158484?text="
def wa(m): return WA + quote(m)
WAICON = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Z"/></svg>'
BADGE = {"champagne":"Champagne","whisky":"Whisky","cognac":"Cognac","tequila":"Tequila",
         "rhum":"Rhum","gin":"Gin","vodka":"Vodka","aperitif":"Apéritif"}
CAT_ORDER = ["champagne","whisky","cognac","tequila","rhum","gin","vodka","aperitif"]

NEW = [
 ("gin","Dry Gin · XII","Gin de Provence · 70 cl","25 000","gin-dry"),
 ("gin","Hendrick's","Gin · Écosse","35 000","hendricks"),
 ("gin","June · by G'Vine","Gin floral","30 000","june-gvine"),
 ("gin","Whitley Neill · Blood Orange","Handcrafted gin",None,"whitley-neill"),
 ("vodka","Cîroc","Vodka · France","50 000","ciroc"),
 ("rhum","Bologne · Réserve Spéciale","Rhum agricole · Guadeloupe","60 000","bologne-reserve"),
 ("rhum","Ti' Ced · Ananas Victoria","Rhum arrangé","35 000","ti-ced"),
 ("rhum","Kraken · Black Spiced","Rhum épicé · 70 cl","40 000","kraken"),
 ("rhum","Hédone","Rhum vieux · France",None,"hedone"),
 ("rhum","Rivière du Mât · Black Spiced","Rhum épicé · La Réunion",None,"riviere-du-mat"),
 ("aperitif","Baileys · The Original","Crème irlandaise","20 000","baileys-original"),
 ("aperitif","Baileys · Salted Caramel","Crème · caramel salé","22 000","baileys-salted"),
 ("aperitif","Ricard","Pastis de Marseille","20 000","ricard"),
 ("aperitif","Martini · Rosso","Vermouth rouge","15 000","martini-rosso"),
 ("aperitif","Jägermeister · 1 L","Liqueur","30 000","jagermeister-1l"),
 ("aperitif","Jägermeister · 70 cl","Liqueur","25 000","jagermeister-70"),
 ("aperitif","Jägermeister · 35 cl","Liqueur","15 000","jagermeister-35"),
 ("whisky","Chivas Regal · 18 ans","Blended · Écosse","65 000","chivas-18"),
 ("whisky","Glenfiddich · VAT 01","Single malt · Speyside","80 000","glenfiddich-vat01"),
 ("whisky","The San-In","Blended japonais","50 000","the-san-in"),
 ("whisky","Akashi · Sherry Cask","Blended japonais · sherry","40 000","akashi-sherry"),
 ("whisky","Haig Club","Single grain · Clubman","30 000","haig-club"),
 ("whisky","Jack Daniel's","Tennessee whiskey · 70 cl","26 000","jack-daniels"),
 ("whisky","Aberlour · Distillery 10 ans","Single malt · Speyside","25 000","aberlour-10"),
 ("whisky","The Deveron · 10 ans","Single malt · Highlands","20 000","the-deveron-10"),
 ("whisky","Glen Turner · 12 ans","Single malt · Réserve",None,"glen-turner-12"),
 ("whisky","Knockando · 18 ans","Single malt · Speyside",None,"knockando-18"),
 ("whisky","Hwayo","Whisky de riz · Corée",None,"hwayo"),
]

s = io.open(F, encoding="utf-8").read()

def pnum(p):
    if "demande" in p.lower(): return -1
    m = re.search(r"(\d[\d  ]*\d|\d)", p)
    return int(re.sub(r"\D", "", m.group(1))) if m else 0

# --- cartes existantes (verbatim, avec fixes cat pour whisky/cognac) ---
existing = []  # (cat, price_num, html)
for m in re.finditer(r'<article class="bottle real"[^>]*data-cat="([^"]+)"(?:[^>]*data-sub="([^"]*)")?[^>]*>.*?</article>', s, re.S):
    cat, sub = m.group(1), m.group(2) or ""
    html = m.group(0)
    price = re.search(r'class="price">(.*?)</div>', html, re.S).group(1)
    if cat == "whisky":
        newcat = "cognac" if sub == "cognac" else "whisky"
        html = re.sub(r'<article class="bottle real"[^>]*>', f'<article class="bottle real" data-cat="{newcat}">', html, count=1)
        html = re.sub(r'<span class="badge-cat">[^<]*</span>', f'<span class="badge-cat">{BADGE[newcat]}</span>', html, count=1)
        cat = newcat
    existing.append((cat, pnum(price), html))

# --- nouvelles cartes ---
def newcard(cat, h3, detail, price, slug):
    txt = h3.replace(" · ", " ")
    pr = f"{price} FCFA" if price else "Prix sur demande"
    mp = f"({pr})" if price else "(prix à confirmer)"
    alt = f"{BADGE[cat]} {txt}"
    msg = f"Bonjour Weinkeller by CK, je souhaite commander : {txt} {mp}. Est-elle disponible ?"
    return (f'        <article class="bottle real" data-cat="{cat}">\n'
            f'          <div class="visual"><span class="badge-cat">{BADGE[cat]}</span>'
            f'<img decoding="async" src="assets/images/cave/{slug}.webp" alt="{alt}" loading="lazy"></div>\n'
            f'          <h3>{h3}</h3><div class="vintage">{detail}</div><div class="price">{pr}</div>\n'
            f'          <a class="order" href="{wa(msg)}" target="_blank" rel="noopener">{WAICON}Commander</a>\n'
            f'        </article>')

new_items = [(cat, pnum(price or ""), newcard(cat, h3, detail, price, slug)) for cat, h3, detail, price, slug in NEW]

allc = existing + new_items
allc.sort(key=lambda t: (CAT_ORDER.index(t[0]) if t[0] in CAT_ORDER else 99, -t[1]))
cards = "\n".join(h for _, _, h in allc)

# --- remplace UNIQUEMENT le contenu de <div class="bottles"> (profondeur des div) ---
key = '<div class="bottles">'
j = s.index(key) + len(key)
depth, k, nc = 1, j, -1
while depth > 0:
    nd = s.find("<div", k); nc = s.find("</div>", k)
    if nc == -1: break
    if nd != -1 and nd < nc: depth += 1; k = nd + 4
    else: depth -= 1; k = nc + 6
indent = s[:nc][s[:nc].rfind("\n") + 1:]
s = s[:j] + "\n" + cards + "\n" + indent + s[nc:]

s = s.replace("?v=20260702b", "?v=20260713a")
io.open(F, "w", encoding="utf-8").write(s)

by = {}
for cat, _, _ in allc: by[cat] = by.get(cat, 0) + 1
print("bottles régénéré :", len(allc), "cartes —", ", ".join(f"{c}:{by.get(c,0)}" for c in CAT_ORDER))

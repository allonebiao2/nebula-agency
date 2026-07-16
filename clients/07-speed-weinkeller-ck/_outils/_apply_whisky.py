#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Injecte les cartes Whiskys/Cognacs (catégorie whisky) + Rhum (Eminente) dans la
sélection de weinkeller.html, sans toucher au reste. Idempotent (marqueurs).
UTF-8 garanti — ne jamais éditer via PowerShell Get-Content/WriteAllText."""
import io, os
from urllib.parse import quote

os.chdir(os.path.dirname(os.path.abspath(__file__)))
F = "weinkeller.html"
WA = "https://wa.me/2290197158484?text="
WAICON = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Z"/></svg>'

def wa(name, price_txt):
    return WA + quote(f"Bonjour Weinkeller by CK, je souhaite commander : {name} ({price_txt}). Est-elle disponible ?")

# cat, sub, badge, slug, titre, détail, prix affiché, nom WA, prix WA, alt
CARDS = [
    # --- Whiskys · Single Malt ---
    ("whisky","scotch","Whisky","lagavulin-distillers","Lagavulin · Distillers Edition","Single Malt · Islay","90 000 FCFA","Lagavulin Distillers Edition","90 000 FCFA","Whisky Lagavulin Distillers Edition, single malt d'Islay"),
    ("whisky","scotch","Whisky","lagavulin-16","Lagavulin · 16 ans","Single Malt · Islay","71 000 FCFA","Lagavulin 16 ans","71 000 FCFA","Whisky Lagavulin 16 ans, single malt d'Islay"),
    ("whisky","scotch","Whisky","aberlour-14","Aberlour · 14 ans","Single Malt · Speyside","60 000 FCFA","Aberlour 14 ans","60 000 FCFA","Whisky Aberlour 14 ans, single malt du Speyside"),
    ("whisky","scotch","Whisky","benriach-10","BenRiach · 10 ans","Single Malt · Speyside","53 000 FCFA","BenRiach 10 ans","53 000 FCFA","Whisky BenRiach 10 ans, single malt du Speyside"),
    # --- Cognacs (dans la catégorie whisky, badge Cognac) ---
    ("whisky","cognac","Cognac","hennessy-vsop","Hennessy · V.S.O.P Privilège","Cognac · 70 CL / 1 L","90 000 – 120 000 FCFA","Hennessy V.S.O.P Privilège","70 CL — 90 000 F / 1 L — 120 000 F","Cognac Hennessy V.S.O.P Privilège"),
    ("whisky","cognac","Cognac","martell-vs","Martell · V.S","Cognac · 1 L","65 000 FCFA","Martell V.S 1 L","65 000 FCFA","Cognac Martell V.S 1 litre"),
    ("whisky","cognac","Cognac","hennessy-vs","Hennessy · Very Special","Cognac · 70 CL / 1 L","50 000 – 60 000 FCFA","Hennessy Very Special","70 CL — 50 000 F / 1 L — 60 000 F","Cognac Hennessy Very Special"),
    ("whisky","cognac","Cognac","martell-vsop","Martell · V.S.O.P","Cognac · 1 L","60 000 FCFA","Martell V.S.O.P 1 L","60 000 FCFA","Cognac Martell V.S.O.P 1 litre"),
    ("whisky","cognac","Cognac","remy-martin-vsop","Rémy Martin · V.S.O.P","Cognac · Fine Champagne","60 000 FCFA","Rémy Martin V.S.O.P","60 000 FCFA","Cognac Rémy Martin V.S.O.P Fine Champagne"),
    ("whisky","cognac","Cognac","camus-vs","Camus · Very Special","Cognac · 1 L","60 000 FCFA","Camus Very Special 1 L","60 000 FCFA","Cognac Camus Very Special 1 litre"),
    # --- Rhum (catégorie rhum, activée par cette bouteille) ---
    ("rhum",None,"Rhum","eminente-reserva","Eminente · Reserva","Rhum ambré · Cuba · 70 CL","65 000 FCFA","Eminente Reserva 70 CL","65 000 FCFA","Rhum ambré Eminente Reserva, Cuba, 70 CL"),
]

def card(cat, sub, badge, slug, title, detail, price, waname, waprice, alt):
    subattr = f' data-sub="{sub}"' if sub else ''
    return (
        f'        <article class="bottle real" data-cat="{cat}"{subattr}>\n'
        f'          <div class="visual"><span class="badge-cat">{badge}</span>'
        f'<img decoding="async" src="assets/images/cave/{slug}.webp" alt="{alt}" loading="lazy"></div>\n'
        f'          <h3>{title}</h3><div class="vintage">{detail}</div><div class="price">{price}</div>\n'
        f'          <a class="order" href="{wa(waname, waprice)}" target="_blank" rel="noopener">{WAICON}Commander</a>\n'
        f'        </article>'
    )

BLOCK = ("        <!-- WHISKY+RHUM START -->\n"
         + "\n".join(card(*c) for c in CARDS)
         + "\n        <!-- WHISKY+RHUM END -->")

src = io.open(F, encoding="utf-8").read()

# 1) cartes — idempotent via marqueurs
S, E = "        <!-- WHISKY+RHUM START -->", "        <!-- WHISKY+RHUM END -->"
if S in src and E in src:
    pre, rest = src.split(S, 1)
    _, post = rest.split(E, 1)
    src = pre + BLOCK + post
    where = "remplacées"
else:
    anchor = '\n          </div>\n          <div class="cave-empty" id="caveEmpty" hidden>'
    assert anchor in src, "ancre .bottles introuvable"
    src = src.replace(anchor, "\n" + BLOCK + anchor, 1)
    where = "insérées"

# 2) notice — Whiskys/Cognacs/Rhum désormais en stock
old_notice = ("<b>Champagnes &amp; Tequilas</b> sont en stock, avec leurs prix et la commande directe sur WhatsApp. "
              "<b>Vins, Whiskys, Rhum, Gin, Pastis, Vodka</b> arrivent bientôt")
new_notice = ("<b>Champagnes, Whiskys, Cognacs, Tequilas &amp; Rhum</b> sont en stock, avec leurs prix et la commande directe sur WhatsApp. "
              "<b>Vins, Gin, Pastis &amp; Vodka</b> arrivent bientôt")
if old_notice in src:
    src = src.replace(old_notice, new_notice)
    notice = "maj"
else:
    notice = "déjà à jour / introuvable"

# 3) cache-bust site-relatif à cette page
src = src.replace("?v=20260701m", "?v=20260701n")

io.open(F, "w", encoding="utf-8").write(src)
print(f"weinkeller.html : {len(CARDS)} cartes {where} (10 whisky/cognac + 1 rhum) · notice {notice} · ?v=20260701n")

# 4) cache-bust des pages sœurs (app.js/app.css partagés) — reste sur une version unique
for sib in ("index.html", "speed.html"):
    try:
        s = io.open(sib, encoding="utf-8").read()
        n = s.count("?v=20260701m")
        if n:
            io.open(sib, "w", encoding="utf-8").write(s.replace("?v=20260701m", "?v=20260701n"))
        print(f"{sib} : {n} version(s) bumpée(s) -> ?v=20260701n")
    except FileNotFoundError:
        print(f"{sib} : absent")


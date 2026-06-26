#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Réécrit le HERO (coverflow 3D champagnes) + la SÉLECTION (8 champagnes réels + placeholders)
de weinkeller.html. Idempotent via marqueurs de commentaires. UTF-8 garanti."""
import io
from urllib.parse import quote

F = "weinkeller.html"
WA = "https://wa.me/2290197158484?text="
def wa(msg): return WA + quote(msg)

# marque, cuvée, détail, prix, slug
CAT = [
 ("Ruinart","Blanc de Blancs","75 CL · étui","80 000","ruinart-blanc-de-blancs"),
 ("Ruinart","Brut Rosé","75 CL","80 000","ruinart-brut-rose"),
 ("Ruinart","R de Ruinart","75 CL · étui","60 000","ruinart-r"),
 ("Veuve Clicquot","Brut","75 CL","60 000","veuve-clicquot"),
 ("Moët & Chandon","Ice Impérial","75 CL","55 000","moet-ice"),
 ("Nicolas Feuillatte","Cuvée Spéciale","Blanc de Blancs","50 000","nicolas-feuillatte"),
 ("Lanson","Black Label","75 CL · étui","45 000","lanson-black-label"),
 ("Moët & Chandon","Brut Impérial","75 CL","45 000","moet-brut-imperial"),
]
WAICON = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Z"/></svg>'

def cf_items():
    out = []
    for b,n,d,p,s in CAT:
        u = wa(f"Bonjour Weinkeller by CK, je souhaite commander : {b} {n} ({p} FCFA). Est-elle disponible ?")
        out.append(f'        <div class="cf-item" data-brand="{b}" data-name="{n}" data-detail="{d}" data-price="{p} FCFA" data-wa="{u}"><img src="assets/images/cave/{s}.webp" alt="Champagne {b} {n}" loading="lazy" width="200" height="700"></div>')
    return "\n".join(out)

def champ_cards():
    out = []
    for b,n,d,p,s in CAT:
        u = wa(f"Bonjour Weinkeller by CK, je souhaite commander : {b} {n} ({p} FCFA). Est-elle disponible ?")
        out.append(f'''        <article class="bottle real" data-cat="champagne">
          <div class="visual"><span class="badge-cat">Champagne</span><img src="assets/images/cave/{s}.webp" alt="Champagne {b} {n}" loading="lazy"></div>
          <h3>{b} · {n}</h3><div class="vintage">{d}</div><div class="price">{p} FCFA</div>
          <a class="order" href="{u}" target="_blank" rel="noopener">{WAICON}Commander</a>
        </article>''')
    return "\n".join(out)

# placeholders (autres caves, en attente liste/prix client)
def ph(cat, badge, title, vintage, glass, msg):
    u = wa(msg)
    svgs = {
      "wine": '<path class="glass" fill="url(#%s)" d="M26 6h8v8c0 3 1 4 1 7v15c7 4 11 11 11 22v122a6 6 0 0 1-6 6H20a6 6 0 0 1-6-6V58c0-11 4-18 11-22V21c0-3 1-4 1-7V6Z"/><rect class="label" x="15" y="120" width="30" height="44" rx="2"/><rect class="shine" x="20" y="46" width="3.5" height="150" rx="2"/>',
      "whisky": '<path class="glass" fill="url(#%s)" d="M24 8h12v18c8 3 12 8 12 16v138a6 6 0 0 1-6 6H18a6 6 0 0 1-6-6V42c0-8 4-13 12-16V8Z"/><rect class="label" x="15" y="118" width="30" height="46" rx="2"/><rect class="shine" x="20" y="52" width="3.5" height="140" rx="2"/>',
      "slim": '<path class="glass" fill="url(#%s)" d="M27 6h6v16c5 2 8 6 8 13v144a6 6 0 0 1-6 6H21a6 6 0 0 1-6-6V35c0-7 3-11 8-13V6Z"/><rect class="label" x="17" y="120" width="26" height="44" rx="2"/><rect class="shine" x="21" y="44" width="3" height="146" rx="2"/>',
    }
    shape, grad = glass
    body = svgs[shape] % grad
    return f'''        <article class="bottle is-ph" data-cat="{cat}">
          <div class="visual"><span class="badge-cat">{badge}</span>
            <svg class="bottle-svg" viewBox="0 0 60 210">{body}</svg>
          </div>
          <h3>{title} <span class="tovalid">à valider</span></h3>
          <div class="vintage">{vintage}</div>
          <div class="price">Prix sur demande</div>
          <a class="order" href="{u}" target="_blank" rel="noopener">{WAICON}Commander</a>
        </article>'''

PLACEHOLDERS = "\n".join([
 ph("rouge","Vin rouge","Grand rouge de garde","Millésime à préciser",("wine","bottleGlass"),"Bonjour Weinkeller by CK, je suis intéressé(e) par un grand rouge de garde. Quelles références avez-vous ?"),
 ph("rouge","Vin rouge","Rouge de plaisir","Pour la table, au quotidien",("wine","bottleGlass"),"Bonjour Weinkeller by CK, je cherche un bon rouge pour la table."),
 ph("blanc","Vin blanc","Blanc ciselé","Frais & élégant",("wine","gClear"),"Bonjour Weinkeller by CK, je suis intéressé(e) par un vin blanc."),
 ph("blanc","Rosé","Rosé de soleil","L'apéritif, en terrasse",("wine","gClear"),"Bonjour Weinkeller by CK, je cherche un bon rosé."),
 ph("spiritueux","Whisky","Whisky de caractère","Single malt / blend",("whisky","gAmber"),"Bonjour Weinkeller by CK, je suis intéressé(e) par un whisky."),
 ph("spiritueux","Spiritueux","Cognac / rhum rare","Pour les amateurs avertis",("whisky","gAmber"),"Bonjour Weinkeller by CK, je cherche un cognac ou un rhum rare."),
 ph("liqueur","Liqueur","Liqueur fine","Apéritif & digestif",("slim","gAmber"),"Bonjour Weinkeller by CK, je suis intéressé(e) par vos liqueurs et apéritifs."),
 ph("biere","Bière premium","Bière premium","L'instant convivial",("slim","gAmber"),"Bonjour Weinkeller by CK, quelles bières premium avez-vous ?"),
])

ARR = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
HERO = '''  <!-- HERO -->
  <header class="hero" style="display:flex;flex-direction:column;justify-content:center;gap:0">
    <canvas class="golddust" aria-hidden="true"></canvas>
    <div class="wrap" style="text-align:center;position:relative;z-index:2;max-width:900px">
      <span class="kicker">La cave de Porto-Novo</span>
      <h1 style="margin-top:14px">Weinkeller <span class="gold">by CK</span></h1>
      <div class="wein-rule" style="margin-inline:auto"></div>
      <p class="wein-hero-sub" style="margin-inline:auto">Une cave d'exception à Porto-Novo. Notre sélection de <span class="gold">champagnes de prestige</span> — Ruinart, Moët &amp; Chandon, Veuve Clicquot, Lanson — prête à célébrer vos plus beaux moments.</p>
      <div class="btn-row" style="justify-content:center;margin-top:26px">
        <a class="btn btn-lg btn-gold" href="#selection">Voir toute la sélection</a>
        <a class="btn btn-lg btn-ghost" href="''' + wa("Bonjour Weinkeller by CK, je souhaite commander une bouteille.") + '''" target="_blank" rel="noopener">Commander sur WhatsApp</a>
      </div>
    </div>

    <div class="cave-3d" aria-roledescription="carrousel" aria-label="Nos champagnes en vedette">
      <div class="cf-glow" aria-hidden="true"></div>
      <div class="cf">
''' + cf_items() + '''
      </div>
    </div>
    <div class="wrap" style="position:relative;z-index:6">
      <div class="cf-meta" aria-live="polite"><span class="b"></span><h3></h3><span class="d"></span><div class="p"></div></div>
      <div class="cf-order"><a class="btn btn-gold" href="#" target="_blank" rel="noopener">Commander cette bouteille</a></div>
      <div class="cf-controls">
        <button class="cf-arrow cf-prev" aria-label="Champagne précédent"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M15 6l-6 6 6 6"/></svg></button>
        <div class="cf-dots" role="tablist" aria-label="Choisir un champagne"></div>
        <button class="cf-arrow cf-next" aria-label="Champagne suivant"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M9 6l6 6-6 6"/></svg></button>
      </div>
    </div>
  </header>

'''

SELECTION = '''  <!-- SELECTION -->
  <section class="sec" id="selection">
    <div class="wrap">
      <div class="sec-head center reveal">
        <span class="kicker" style="justify-content:center">La sélection</span>
        <h2 class="h-lg">Notre cave, bouteille par bouteille.</h2>
      </div>

      <div class="notice reveal" style="margin:30px auto 36px;max-width:860px">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 8h.01M11 12h1v4h1"/></svg>
        <p><b>Champagnes disponibles ci-dessous</b>, avec leurs prix — commande directe sur WhatsApp. Le reste de la cave (vins rouges, blancs, whiskies &amp; spiritueux…) s'enrichit&nbsp;: dites-nous ce que vous cherchez, on vous répond tout de suite.</p>
      </div>

      <div class="wein-filter reveal" role="tablist" aria-label="Filtrer la sélection">
        <button class="active" data-cat="all">Tout</button>
        <button data-cat="champagne">Champagnes</button>
        <button data-cat="rouge">Vins rouges</button>
        <button data-cat="blanc">Blancs &amp; rosés</button>
        <button data-cat="spiritueux">Whiskies &amp; spiritueux</button>
        <button data-cat="liqueur">Liqueurs</button>
        <button data-cat="biere">Bières</button>
      </div>

      <div class="bottles reveal">
''' + champ_cards() + "\n" + PLACEHOLDERS + '''
      </div>
    </div>
  </section>

'''

src = io.open(F, encoding="utf-8").read()

# remplace HERO
pre, rest = src.split("  <!-- HERO -->", 1)
_, post = rest.split("  <!-- LA MAISON -->", 1)
src = pre + HERO + "  <!-- LA MAISON -->" + post
# remplace SELECTION
pre, rest = src.split("  <!-- SELECTION -->", 1)
_, post = rest.split("  <!-- COMMANDER", 1)
src = pre + SELECTION + "  <!-- COMMANDER" + post
# n° Weinkeller confirmé (même que la maison) -> retire le caveat
src = src.replace("Commandes &amp; conseils · ligne à confirmer", "Commandes &amp; conseils · Cotonou &amp; Porto-Novo")
# cache-bust
src = src.replace("?v=20260626b", "?v=20260626c")

io.open(F, "w", encoding="utf-8").write(src)
print("weinkeller.html mis à jour :", len(CAT), "champagnes réels + coverflow 3D + placeholders")

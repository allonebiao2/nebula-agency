#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remplace la grille de catégories Speed par un coverflow 3D (cartes). UTF-8, idempotent par anciens."""
import io
from urllib.parse import quote

F = "speed.html"
WA = "https://wa.me/2290197158484?text="
def wa(msg): return WA + quote(msg)

# nom, description, [chips], icone_svg_inner
CATS = [
 ("Vêtements &amp; chaussures", "Mode homme, femme et enfants : les meilleures marques.", ["Zara","Nike","Zalando"],
  '<path d="M12 4a2 2 0 0 0-2 2c0 1 1 1.5 1 1.5L3 12v3h18v-3l-8-4.5S14 7 14 6a2 2 0 0 0-2-2Z"/>'),
 ("Cosmétiques &amp; parfums", "Parfums, soins, maquillage à prix avantageux.", ["Sephora","Parfums"],
  '<circle cx="12" cy="8" r="4"/><path d="M5 21a7 7 0 0 1 14 0"/>'),
 ("Téléphones &amp; électronique", "Smartphones, accessoires, ordinateurs et plus.", ["Amazon","Cdiscount"],
  '<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M11 18h2"/>'),
 ("Articles pour enfants", "Tout pour le confort et le bonheur des enfants.", ["Jouets","Puériculture"],
  '<path d="M12 4c-2 3-5 4-5 8a5 5 0 0 0 10 0c0-4-3-5-5-8Z"/>'),
 ("Articles de maison", "Ustensiles, décoration, électroménager.", ["Déco","Maison"],
  '<path d="M3 11 12 3l9 8"/><path d="M5 10v10h14V10"/>'),
 ("Produits alimentaires", "Produits secs, gourmandises et spécialités.", ["Épicerie","Spécialités"],
  '<path d="M5 7h14l-1.5 12.5a2 2 0 0 1-2 1.5H8.5a2 2 0 0 1-2-1.5L5 7Z"/><path d="M9 7a3 3 0 0 1 6 0"/>'),
]

def items():
    out = []
    for name, desc, chips, ico in CATS:
        clean = name.replace("&amp;", "&")
        u = wa(f"Bonjour Speed Shopping, je souhaite commander dans la catégorie « {clean} ». Voici ce que je cherche : ")
        ch = "".join(f"<span>{c}</span>" for c in chips)
        out.append(f'''          <div class="cf-item" data-wa="{u}">
            <div class="cf-card">
              <span class="cf-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ico}</svg></span>
              <h3>{name}</h3><p>{desc}</p><div class="cf-chips">{ch}</div>
            </div>
          </div>''')
    return "\n".join(out)

L = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M15 6l-6 6 6 6"/></svg>'
R = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M9 6l6 6-6 6"/></svg>'
BLOCK = '''      <div class="cave-3d" aria-roledescription="carrousel" aria-label="Ce que l'on peut vous rapporter">
        <div class="cf-glow" aria-hidden="true"></div>
        <div class="cf">
''' + items() + '''
        </div>
      </div>
      <div class="wrap" style="position:relative;z-index:6;padding:0">
        <div class="cf-order" style="margin-top:18px"><a class="btn btn-lg btn-wa" href="''' + wa("Bonjour Speed Shopping, je souhaite passer une commande.") + '''" target="_blank" rel="noopener">Commander cette catégorie</a></div>
        <div class="cf-controls">
          <button class="cf-arrow cf-prev" aria-label="Catégorie précédente">''' + L + '''</button>
          <div class="cf-dots" role="tablist" aria-label="Choisir une catégorie"></div>
          <button class="cf-arrow cf-next" aria-label="Catégorie suivante">''' + R + '''</button>
        </div>
      </div>

'''

src = io.open(F, encoding="utf-8").read()
A = '      <div class="cats" style="margin-top:40px">'
B = '      <div class="reveal" style="margin-top:42px">'
pre, rest = src.split(A, 1)
_, post = rest.split(B, 1)
src = pre + BLOCK + B + post
src = src.replace("?v=20260626c", "?v=20260626d")
io.open(F, "w", encoding="utf-8").write(src)
print("speed.html : grille catégories -> coverflow 3D (6 cartes)")

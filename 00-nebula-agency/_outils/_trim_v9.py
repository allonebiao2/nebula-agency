#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retire : forfait Fiche Google Maps + section Avatar IA (Essentiel/Pro) + options formulaire,
l'onglet nav Tarifs, et les aperçus flottants du hero. UTF-8."""
import io, os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
F = "nebula_agency_v9.html"
s = io.open(F, encoding="utf-8").read()
n0 = len(s)

# 1) carte service "Fiche Google Maps"
s2 = re.sub(r'\n      <div class="card svc rv-scale rv-d3">.*?Fiche Google Maps.*?\n      </div>', '', s, count=1, flags=re.S)
assert s2 != s, "carte Google Maps introuvable"; s = s2

# 2) section Avatar IA entière (Essentiel + Pro)
s2 = re.sub(r'\n\n<!-- AVATAR IA -->\n<section id="avatar-ia">.*?\n</section>', '', s, count=1, flags=re.S)
assert s2 != s, "section Avatar IA introuvable"; s = s2

# 3) services : grille 4 -> 3 colonnes (+ CSS grid-3 & responsive)
assert '<div class="grid grid-4">' in s
s = s.replace('<div class="grid grid-4">', '<div class="grid grid-3">', 1)
s = s.replace('.grid-4{grid-template-columns:repeat(4,1fr)}',
              '.grid-4{grid-template-columns:repeat(4,1fr)}\n.grid-3{grid-template-columns:repeat(3,1fr)}', 1)
s = s.replace('.grid-4{grid-template-columns:1fr 1fr}', '.grid-4,.grid-3{grid-template-columns:1fr 1fr}', 1)
s = s.replace('.grid-4,.grid-2,.port-grid,.ct-grid{grid-template-columns:1fr}',
              '.grid-4,.grid-3,.grid-2,.port-grid,.ct-grid{grid-template-columns:1fr}', 1)

# 4) onglet nav "Tarifs" (desktop + overlay mobile)
s2 = s.replace('\n      <a href="#order">Tarifs</a>', '', 1); assert s2 != s, "nav Tarifs desktop introuvable"; s = s2
s2 = s.replace('\n  <a href="#order">Tarifs & Commander</a>', '', 1); assert s2 != s, "nav Tarifs mobile introuvable"; s = s2

# 5) options du formulaire (services supprimés)
for opt in ['\n          <option>Création Fiche Google Maps — 20 000 F</option>',
            '\n          <option>Forfait Avatar IA ESSENTIEL — 30 000 F/mois</option>',
            '\n          <option>Forfait Avatar IA PRO — 100 000 F/mois</option>']:
    s2 = s.replace(opt, '', 1); assert s2 != s, f"option formulaire introuvable: {opt[:40]}"; s = s2

# 6) aperçus flottants du hero (hero-visual entier) + hero passe en 1 colonne
s2 = re.sub(r'    <div class="hero-visual rv-scale rv-d2">.*?    </div>\n  </div>\n</header>',
            '  </div>\n</header>', s, count=1, flags=re.S)
assert s2 != s, "hero-visual (aperçus) introuvable"; s = s2
s = s.replace('.hero-grid{display:grid;grid-template-columns:1.08fr .92fr;gap:52px;align-items:center;width:100%}',
              '.hero-grid{display:grid;grid-template-columns:1fr;gap:52px;align-items:center;width:100%;max-width:880px}', 1)

# garde-fous
assert 'id="avatar-ia"' not in s and 'Forfait ESSENTIEL' not in s and 'Forfait PRO' not in s, "reste Avatar IA"
assert 'Fiche Google Maps' not in s, "reste Fiche Google Maps"
assert 'class="peek' not in s and 'class="hero-visual' not in s, "reste aperçus hero"
assert '>Tarifs<' not in s, "reste onglet Tarifs"
assert s.count('wa.me/22996740732') >= 5 and 'function soumettreCommande' in s, "formulaire/WhatsApp impacté"
assert s.count('<div class="card svc') == 3, f"cartes services restantes = {s.count(chr(60)+'div class=\"card svc')} (attendu 3 : Vitrine+Catalogue+QR)"
io.open(F, "w", encoding="utf-8").write(s)
print(f"trim OK · -{n0-len(s)} caractères · services restants: Vitrine + Catalogue + QR Review · hero sans aperçus · nav sans Tarifs")

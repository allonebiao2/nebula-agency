#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Injecte les screenshots réels du portfolio + upgrade la typo display (Space Grotesk -> Syne). UTF-8."""
import io, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
PORT = r"C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-nebula-agency\79468563-0b06-48bc-bdf7-2e27043a505c\scratchpad\port"
F = "nebula_agency_v9.html"
s = io.open(F, encoding="utf-8").read()

# 1) Typo : Space Grotesk -> Syne (display distinctif, non-générique)
s = s.replace("family=Space+Grotesk:wght@400;500;600;700", "family=Syne:wght@600;700;800")
n_font = s.count("'Space Grotesk',sans-serif")
s = s.replace("'Space Grotesk',sans-serif", "'Syne',sans-serif")

# 2) Injection des vrais screenshots
slugs = ["djambar","speedwein","misscakes","hhdesign","grain","luxury"]
inj = {}
for sl in slugs:
    uri = io.open(os.path.join(PORT, sl+".b64"), encoding="utf-8").read().strip()
    ph = "PLACEHOLDER_"+sl
    c = s.count(ph)
    s = s.replace(ph, uri)
    inj[sl] = c

# garde-fous
assert "PLACEHOLDER_" not in s, "placeholder résiduel !"
assert "wa.me/22996740732" in s and s.count("wa.me/22996740732") >= 5, "WhatsApp manquant"
assert "soumettreCommande" in s and "site-lead" in s, "logique formulaire perdue"
assert "'Space Grotesk'" not in s, "Space Grotesk résiduel"
io.open(F, "w", encoding="utf-8").write(s)
print(f"typo -> Syne ({n_font} règles) · images injectées:", inj, "· taille {0:.0f} KB".format(os.path.getsize(F)/1024))

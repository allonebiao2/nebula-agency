#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retire proprement la promo « Fête des Pères » expirée (pastille + modal + CSS + JS),
en conservant le moteur reveal/parallax et TOUS les liens WhatsApp « Réserver ». UTF-8."""
import io, os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
F = "grain-esthetique-LIVE.html"
s = io.open(F, encoding="utf-8").read()
n0 = len(s)

# 1) pastille promo dans le hero
s2 = re.sub(r'\s*<button class="promo-pill".*?</button>', '', s, count=1, flags=re.S)
assert s2 != s, "pastille introuvable"; s = s2

# 2) bloc CSS promo + modal (jusqu'au <script> IIFE reveal/parallax) — enlève aussi le flyer base64
s2 = re.sub(r'<style>\s*/\* ===== Promo Fete des Peres.*?(?=<script>\s*\(function\(\)\{)', '', s, count=1, flags=re.S)
assert s2 != s, "bloc CSS+modal promo introuvable"; s = s2

# 3) fonctions JS promo (waPromo/bookPromo/openPromo/closePromo + keydown + auto-popup) — garde </script>
s2 = re.sub(r'function waPromo\(svc\)\{.*?(?=</script>\s*</body>)', '', s, count=1, flags=re.S)
assert s2 != s, "JS promo introuvable"; s = s2

# 4) selecteurs promo morts dans le garde-fou mobile (tidy)
s = s.replace('  .promo-pill{max-width:calc(100vw - 26px)}\n', '')
s = s.replace('  .promo-pill .pp-txt{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}\n', '')
s = s.replace('  .promo-card{max-width:none;width:100%}\n', '')

# garde-fous : le numéro WhatsApp et les boutons Réserver restent intacts
assert s.count('wa.me/2290197085576') >= 40, "⚠ liens WhatsApp Réserver impactés !"
assert 'openPromo' not in s and 'promo-modal' not in s and 'promo-pill' not in s, "reste de promo"
assert '(function(){' in s and "classList.add('rv')" in s, "moteur reveal/parallax perdu"

io.open(F, "w", encoding="utf-8").write(s)
print(f"promo retirée · {n0-len(s)} caractères supprimés (flyer base64 inclus) · WA Réserver: {s.count('wa.me/2290197085576')} liens intacts")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Raffinements premium additifs : CTA rendez-vous dans le hero, badges maisons
partenaires, bouton WhatsApp flottant, rel=noopener. MÊME numéro WhatsApp. UTF-8."""
import io, os, re
from urllib.parse import quote
os.chdir(os.path.dirname(os.path.abspath(__file__)))
F = "grain-esthetique-LIVE.html"
s = io.open(F, encoding="utf-8").read()
WA = "https://wa.me/2290197085576"
wa0 = s.count('wa.me/2290197085576')

rdv = WA + "?text=" + quote("Bonjour ✨ Je souhaite prendre rendez-vous à Grain d'Esthétique. Quelles sont vos disponibilités ?")
WAGLYPH = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.2-.7-2.7-1.1-4.4-3.9-4.5-4.1-.1-.2-1-1.4-1-2.6s.6-1.8.9-2.1c.2-.2.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.4.6c-.2.2-.3.4-.1.7.2.3.8 1.3 1.7 2.1 1.2 1 2 1.3 2.3 1.5.2.1.4.1.6-.1l.7-.8c.2-.2.4-.2.6-.1l1.9.9c.3.2.5.3.6.4.1.2.1.6-.1 1.1Z"/></svg>'
CALICON = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="5" width="17" height="15.5" rx="2.2"/><path d="M3.5 9.5h17M8 3.2v3.6M16 3.2v3.6M9 14l2 2 4-4"/></svg>'

# 1) CTA rendez-vous dans le hero (avant le bouton Découvrir)
hero_cta = f'<a class="hero-cta" href="{rdv}" target="_blank" rel="noopener">{CALICON}Prendre rendez-vous</a>\n    '
s2 = s.replace('    <a class="scroll-btn" href="#apropos">', '    ' + hero_cta + '<a class="scroll-btn" href="#apropos">', 1)
assert s2 != s, "hero scroll-btn introuvable"; s = s2

# 2) Badges maisons partenaires (avant la grille de stats)
maisons = ('  <div class="maisons">\n'
           '    <span class="maisons-label">Nos maisons partenaires</span>\n'
           '    <span class="maison-badge">Sothys Paris</span>\n'
           '    <span class="maison-badge">Sultane de Saba</span>\n'
           '  </div>\n  ')
s2 = s.replace('  <div class="stats-row">', maisons + '<div class="stats-row">', 1)
assert s2 != s, "stats-row introuvable"; s = s2

# 3) Bouton WhatsApp flottant (au-dessus du bouton musique)
wafab = (f'<a class="wa-fab" href="{rdv}" target="_blank" rel="noopener" aria-label="Prendre rendez-vous sur WhatsApp">{WAGLYPH}</a>\n\n'
         '<!-- Ambient Music Player -->')
s2 = s.replace('<!-- Ambient Music Player -->', wafab, 1)
assert s2 != s, "ancre music player introuvable"; s = s2

# 4) rel=noopener sur tous les liens target=_blank qui en manquent (perf + sécurité)
before = s.count('target="_blank">')
s = s.replace('target="_blank">', 'target="_blank" rel="noopener">')
print("rel=noopener ajouté sur", before, "liens")

# 5) CSS des raffinements (avant </head>)
CSS = """<style>
/* ===== Raffinements premium (additif) ===== */
.hero-cta{display:inline-flex;align-items:center;gap:9px;margin-bottom:20px;padding:13px 26px;border-radius:999px;
  background:linear-gradient(135deg,#C4648A,#D98AAC 50%,#C4648A);color:#FFF!important;font-family:'Jost',sans-serif;
  font-size:12px;font-weight:600;letter-spacing:2px;text-transform:uppercase;text-decoration:none;
  box-shadow:0 10px 30px rgba(196,100,138,.42);transition:transform .25s cubic-bezier(.22,1,.36,1),box-shadow .25s ease;
  animation:fadeUp 1s ease .3s both}
.hero-cta svg{width:17px;height:17px}
.hero-cta:hover{transform:translateY(-2px);box-shadow:0 16px 40px rgba(196,100,138,.55)}
.hero-content{display:flex;flex-direction:column;align-items:center}
.maisons{display:flex;align-items:center;justify-content:center;gap:14px;flex-wrap:wrap;margin:30px 0 6px}
.maisons-label{font-size:9px;letter-spacing:4px;color:#B09AA8;text-transform:uppercase;width:100%;text-align:center;margin-bottom:4px}
.maison-badge{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:16px;letter-spacing:1px;color:#8A5A70;
  border:1px solid rgba(196,100,138,.28);border-radius:999px;padding:8px 20px;background:#FDF5F8;transition:all .3s cubic-bezier(.22,1,.36,1)}
.maison-badge:hover{border-color:#C4648A;color:#C4648A;transform:translateY(-2px);box-shadow:0 8px 20px rgba(196,100,138,.14)}
.wa-fab{position:fixed;right:22px;bottom:84px;z-index:999;width:52px;height:52px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;text-decoration:none;color:#fff;
  background:linear-gradient(135deg,#C4648A,#D4AF72);box-shadow:0 8px 26px rgba(196,100,138,.45);
  transition:transform .28s cubic-bezier(.22,1,.36,1),box-shadow .28s ease;animation:waPulse 2.6s ease-in-out infinite}
.wa-fab svg{width:27px;height:27px;fill:currentColor}
.wa-fab:hover{transform:scale(1.09);box-shadow:0 12px 32px rgba(196,100,138,.6)}
@keyframes waPulse{0%,100%{box-shadow:0 8px 26px rgba(196,100,138,.45)}50%{box-shadow:0 8px 30px rgba(196,100,138,.7)}}
@media (prefers-reduced-motion:reduce){.wa-fab,.hero-cta{animation:none;transition:none}}
</style>
</head>"""
assert s.count("</head>") == 1
s = s.replace("</head>", CSS)

# garde-fous
assert s.count('wa.me/2290197085576') == wa0 + 2, "compte de liens WhatsApp inattendu"
assert '01 97 08 55 76' in s, "numéro affiché perdu"
io.open(F, "w", encoding="utf-8").write(s)
print("raffinements OK : hero CTA + maisons partenaires + WA FAB + rel=noopener")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remplace tous les emojis par des icônes SVG line-art élégantes (palette rose/or).
Ajoute le CSS d'icônes, remplace section/horaires/contact/footer/musique. UTF-8."""
import io, os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
F = "grain-esthetique-LIVE.html"
s = io.open(F, encoding="utf-8").read()

def svg(path, extra=""):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true"{extra}>{path}</svg>'

# --- icônes de section (24x24, trait) ---
FLOWER = svg('<circle cx="12" cy="12" r="2.4"/><path d="M12 9.6a2.6 2.6 0 1 1 0-5.2 2.6 2.6 0 0 1 0 5.2M12 14.4a2.6 2.6 0 1 1 0 5.2 2.6 2.6 0 0 1 0-5.2M9.6 12a2.6 2.6 0 1 1-5.2 0 2.6 2.6 0 0 1 5.2 0M14.4 12a2.6 2.6 0 1 1 5.2 0 2.6 2.6 0 0 1-5.2 0"/>')
SPARKLE = svg('<path d="M12 3c.6 4 2.8 6.2 6.8 6.8C14.8 10.4 12.6 12.6 12 16.6 11.4 12.6 9.2 10.4 5.2 9.8 9.2 9.2 11.4 7 12 3Z"/><path d="M18.5 15.5c.2 1.4 1 2.2 2.4 2.4-1.4.2-2.2 1-2.4 2.4-.2-1.4-1-2.2-2.4-2.4 1.4-.2 2.2-1 2.4-2.4Z"/>')
LEAF = svg('<path d="M4 20c0-8 5-13 16-13 0 11-5 16-13 15.5"/><path d="M4 20C8 14 12 11 17 10"/>')
DROP = svg('<path d="M12 3.5s6 6.3 6 10.5a6 6 0 0 1-12 0c0-4.2 6-10.5 6-10.5Z"/><path d="M9 14.5a3 3 0 0 0 3 3"/>')
POLISH = svg('<rect x="9" y="8" width="6" height="13" rx="2"/><path d="M10 8V5.5h4V8"/><path d="M10.5 3h3"/><path d="M9 12h6"/>')
GEM = svg('<path d="M6 3.5h12l3 5.5-9 11.5L3 9z"/><path d="M3 9h18M9 3.5 6.5 9l5.5 8 5.5-8L15 3.5M12 3.5v16.5"/>')
CLOCK = svg('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.2V12l3.2 1.9"/>')
PIN = svg('<path d="M12 21s-6.5-5.2-6.5-10.5a6.5 6.5 0 0 1 13 0C18.5 15.8 12 21 12 21Z"/><circle cx="12" cy="10.3" r="2.4"/>')
PHONE = svg('<path d="M15.6 21A15.6 15.6 0 0 1 3 8.4 2.9 2.9 0 0 1 5.9 5.4h1.9a1 1 0 0 1 1 .8l.7 2.9a1 1 0 0 1-.3 1L7.7 11.4a12.5 12.5 0 0 0 4.9 4.9l1.3-1.5a1 1 0 0 1 1-.3l2.9.7a1 1 0 0 1 .8 1v1.9A2.9 2.9 0 0 1 15.6 21Z"/>')
CAL = svg('<rect x="3.5" y="5" width="17" height="15.5" rx="2.2"/><path d="M3.5 9.5h17M8 3.2v3.6M16 3.2v3.6"/>')
NOTE = svg('<path d="M9 17.5V5.2l10-2v12.1"/><circle cx="6.4" cy="17.6" r="2.6"/><circle cx="16.4" cy="15.3" r="2.6"/>', ' fill="none"')

secmap = {"🌸": FLOWER, "✨": SPARKLE, "🌿": LEAF, "🕯️": DROP, "💅": POLISH, "⭐": GEM}
for emo, ic in secmap.items():
    old = f'<span class="sec-icon">{emo}</span>'
    assert old in s, f"section emoji introuvable: {emo}"
    s = s.replace(old, f'<span class="sec-icon">{ic}</span>')

# horaires (titre carte sombre)
s = s.replace('<div class="horaires-title">🕐 Horaires', f'<div class="horaires-title">{CLOCK} Horaires')

# contact (cercles)
s = s.replace('<div class="contact-icon">📍</div>', f'<div class="contact-icon">{PIN}</div>')
s = s.replace('<div class="contact-icon">📞</div>', f'<div class="contact-icon">{PHONE}</div>')
s = s.replace('<div class="contact-icon">🗓️</div>', f'<div class="contact-icon">{CAL}</div>')

# footer
s = s.replace('<div class="fc-icon">📍</div>', f'<div class="fc-icon">{PIN}</div>')
s = s.replace('<div class="fc-icon">📞</div>', f'<div class="fc-icon">{PHONE}</div>')
s = s.replace('<div class="fc-icon">🕐</div>', f'<div class="fc-icon">{CLOCK}</div>')

# bouton musique : SVG note + a11y ; on stoppe le textContent qui écraserait le SVG
s = s.replace('<span id="music-icon">♪</span>', f'<span id="music-icon">{NOTE}</span>')
s = s.replace("document.getElementById('music-icon').textContent = '♫';", "")
s = s.replace("document.getElementById('music-icon').textContent = '♪';", "")

# CSS des icônes (inséré avant </head>)
ICON_CSS = """<style>
/* ===== Icônes SVG (remplacent les emojis — même palette rose/or) ===== */
.sec-icon{display:inline-flex;align-items:center;justify-content:center;color:#C4648A;margin-bottom:14px}
.sec-icon svg{width:30px;height:30px;fill:none;stroke:currentColor;stroke-width:1.4;stroke-linecap:round;stroke-linejoin:round}
.hommes-body .sec-icon,.hommes-banner .sec-icon{color:#D4AF72}
.horaires-title svg{width:20px;height:20px;fill:none;stroke:#E8A0C0;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;flex:none}
.contact-icon svg{width:18px;height:18px;fill:none;stroke:#C4648A;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.fc-icon{display:inline-flex;align-items:center;justify-content:center}
.fc-icon svg{width:17px;height:17px;fill:none;stroke:#C4648A;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
#music-icon{display:flex;align-items:center;justify-content:center}
#music-icon svg{width:19px;height:19px;fill:none;stroke:#fff;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
</style>
</head>"""
assert s.count("</head>") == 1
s = s.replace("</head>", ICON_CSS)

# garde-fous : plus aucun emoji résiduel dans l'UI (on ignore le texte des liens WhatsApp : ✨ y est volontaire)
ui = re.sub(r'wa\.me/[^"]+', '', s)
for emo in list(secmap) + ["🕐","📍","📞","🗓️","♪","♫"]:
    assert emo not in ui, f"emoji résiduel dans l'UI: {emo}"
assert s.count('wa.me/2290197085576') >= 40, "liens WhatsApp impactés"

io.open(F, "w", encoding="utf-8").write(s)
print("emojis → SVG : sections(6) + horaires + contact(3) + footer(3) + musique · CSS injecté · 0 emoji résiduel")

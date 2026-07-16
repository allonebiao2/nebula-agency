#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Accessibilité : nav clavier (div→button), bouton musique (div→button + aria),
alt manquant, CSS reset boutons. UTF-8. Ne touche à aucun lien WhatsApp."""
import io, os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
F = "grain-esthetique-LIVE.html"
s = io.open(F, encoding="utf-8").read()
wa0 = s.count('wa.me/2290197085576')

# 1) nav-item : div -> button (clavier natif), dans le bloc nav-inner uniquement
m = re.search(r'<div class="nav-inner">(.*?)</div>\s*</nav>', s, re.S)
assert m, "nav-inner introuvable"
inner = m.group(1)
inner2, n = re.subn(r'<div (class="nav-item[^"]*" onclick="[^"]*")>([^<]*)</div>',
                    r'<button type="button" \1>\2</button>', inner)
assert n == 7, f"nav-items convertis: {n} (attendu 7)"
s = s[:m.start(1)] + inner2 + s[m.end(1):]

# 2) bouton musique : div -> button + aria (bloc entier en un seul regex)
s, nm = re.subn(
  r'<div id="music-btn"[^>]*>(\s*<span id="music-icon">.*?</span>\s*)</div>',
  r'<button id="music-btn" type="button" onclick="toggleMusic()" aria-label="Activer la musique d\'ambiance" aria-pressed="false" title="Musique d\'ambiance">\1</button>',
  s, count=1, flags=re.S)
assert nm == 1, "bouton musique introuvable"

# 3) aria-pressed synchronisé dans toggleMusic
s = s.replace("btn.classList.add('playing');\n    btn.classList.remove('muted');",
              "btn.classList.add('playing');\n    btn.classList.remove('muted');\n    btn.setAttribute('aria-pressed','true');")
s = s.replace("btn.classList.remove('playing');\n    btn.classList.add('muted');",
              "btn.classList.remove('playing');\n    btn.classList.add('muted');\n    btn.setAttribute('aria-pressed','false');")

# 4) alt manquant (logo NEBULA en pied)
s = s.replace('filter:invert(1) brightness(1.1);mix-blend-mode:screen;">',
              'filter:invert(1) brightness(1.1);mix-blend-mode:screen;" alt="NEBULA Agency">')

# 5) CSS reset boutons (identique visuellement)
A11Y_CSS = """<style>
/* ===== Accessibilité : boutons natifs au rendu identique ===== */
button.nav-item{background:transparent;border:0;font-family:'Jost',sans-serif;cursor:pointer}
button#music-btn{border:1px solid rgba(255,255,255,0.2);padding:0;-webkit-appearance:none;appearance:none}
</style>
</head>"""
assert s.count("</head>") == 1
s = s.replace("</head>", A11Y_CSS)

# garde-fous
assert s.count('wa.me/2290197085576') == wa0, "liens WhatsApp impactés !"
assert 'class="nav-item' in s and '<div class="nav-item' not in s, "nav non converti"
assert '<button id="music-btn"' in s, "bouton musique non converti"
assert s.count('</button>') >= 8, "boutons mal fermés"

io.open(F, "w", encoding="utf-8").write(s)
print("a11y OK : nav 7 boutons + musique button + aria-pressed + alt + reset CSS")

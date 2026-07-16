#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Une animation SIGNATURE différente par section (adaptée à chacune) + micro-anim d'icône.
Corrige aussi l'emoji 🎩 résiduel (→ nœud papillon SVG) et branche la révélation de l'Espace Hommes.
Additif, UTF-8, respecte prefers-reduced-motion. Ne touche à aucun lien WhatsApp."""
import io, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
F = "grain-esthetique-LIVE.html"
s = io.open(F, encoding="utf-8").read()
wa0 = s.count('wa.me/2290197085576')

# 1) emoji 🎩 -> emblème nœud papillon doré (cohérent avec les icônes SVG)
BOW = ('<div class="hommes-emblem"><svg viewBox="0 0 24 24" aria-hidden="true">'
       '<path d="M11 12 4 8.4v7.2L11 12Z"/><path d="M13 12l7-3.6v7.2L13 12Z"/>'
       '<rect x="10.6" y="9.7" width="2.8" height="4.6" rx="0.7"/></svg></div>')
old_hat = '<div style="font-size:32px;margin-bottom:10px">🎩</div>'
assert old_hat in s, "emoji 🎩 introuvable"
s = s.replace(old_hat, BOW)

# 2) id sur la liste des soins Hommes (sibling du bandeau) + branchement révélation
assert '<div class="hommes-body">' in s
s = s.replace('<div class="hommes-body">', '<div class="hommes-body" id="hommessoins">', 1)
old_ids = "var ids=['apropos','visage','corps','epilation','ongles','avances','hommes'];"
assert old_ids in s, "tableau ids (IIFE révélation) introuvable"
s = s.replace(old_ids, "var ids=['apropos','visage','corps','epilation','ongles','avances','hommes','hommessoins'];")

# 3) CSS des animations signatures (par section) + icônes + garde-fou mouvement réduit
ANIM = """<style>
/* ===== Animations SIGNATURE par section (adaptées à chacune) ===== */

/* — À PROPOS : Éclosion (bloom doux, fondu + flou) — */
@keyframes gBloom{from{opacity:0;transform:scale(.94);filter:blur(7px)}to{opacity:1;transform:none;filter:blur(0)}}
#apropos.rv .apropos-img-wrap,#apropos.rv .apropos-block,#apropos.rv .stat-card,#apropos.rv .horaires-card,#apropos.rv .contact-row{
  animation-name:gBloom;animation-duration:.9s;animation-timing-function:cubic-bezier(.22,1,.36,1);animation-fill-mode:backwards}
#apropos.rv .maisons{animation:gBloom .9s cubic-bezier(.22,1,.36,1) .14s backwards}
@keyframes gFlower{0%{opacity:0;transform:scale(.35) rotate(-45deg)}60%{opacity:1}100%{opacity:1;transform:none}}
#apropos.rv .sec-icon svg{animation:gFlower 1.05s cubic-bezier(.22,1,.36,1) both;transform-origin:center}

/* — VISAGE : Radiance (les soins s'allument) — */
@keyframes gRadiate{0%{opacity:0;transform:translateY(12px);filter:brightness(1.9) saturate(1.15)}100%{opacity:1;transform:none;filter:none}}
#visage.rv .soin{animation-name:gRadiate;animation-duration:.6s;animation-timing-function:ease-out;animation-fill-mode:backwards}
@keyframes gTwinkle{0%{opacity:0;transform:scale(.4) rotate(-30deg)}55%{opacity:1;transform:scale(1.18) rotate(60deg)}100%{opacity:1;transform:scale(1) rotate(0)}}
#visage.rv .sec-icon svg{animation:gTwinkle 1.15s ease both}

/* — CORPS : Respiration (montée lente et calme) — */
@keyframes gBreathe{0%{opacity:0;transform:translateY(28px) scale(.99)}60%{opacity:1}100%{opacity:1;transform:none}}
#corps.rv .soin{animation-name:gBreathe;animation-duration:.85s;animation-timing-function:cubic-bezier(.4,0,.2,1);animation-fill-mode:backwards}
@keyframes gLeaf{0%{opacity:0;transform:rotate(-20deg) translateY(6px)}60%{opacity:1;transform:rotate(7deg)}100%{opacity:1;transform:rotate(0)}}
#corps.rv .sec-icon svg{animation:gLeaf 1.2s ease both;transform-origin:bottom center}

/* — ÉPILATION : Glisse (mouvement latéral net, façon passage de cire) — */
@keyframes gGlide{0%{opacity:0;transform:translateX(-32px)}100%{opacity:1;transform:none}}
#epilation.rv .soin{animation-name:gGlide;animation-duration:.5s;animation-timing-function:cubic-bezier(.22,1,.36,1);animation-fill-mode:backwards}
@keyframes gDrip{0%{opacity:0;transform:translateY(-11px) scale(.7)}60%{opacity:1;transform:translateY(3px) scale(1.06)}100%{opacity:1;transform:none}}
#epilation.rv .sec-icon svg{animation:gDrip 1s cubic-bezier(.5,0,.3,1.4) both}

/* — MAINS & PIEDS : Vernis (révélation gauche→droite, comme une pose de vernis) — */
@keyframes gPolish{0%{opacity:0;clip-path:inset(0 100% 0 0)}100%{opacity:1;clip-path:inset(0 0 0 0)}}
#ongles.rv .soin{animation-name:gPolish;animation-duration:.62s;animation-timing-function:cubic-bezier(.7,0,.3,1);animation-fill-mode:backwards}
@keyframes gShimmer{0%{opacity:0;transform:translateY(8px)}50%{opacity:1;filter:drop-shadow(0 0 7px rgba(212,175,114,.75))}100%{opacity:1;filter:none;transform:none}}
#ongles.rv .sec-icon svg{animation:gShimmer 1.05s ease both}

/* — SOINS AVANCÉS : Élévation premium (cartes qui montent + gemme qui brille) — */
@keyframes gLift{0%{opacity:0;transform:translateY(32px) scale(.96)}100%{opacity:1;transform:none}}
#avances.rv .avance-card{animation-name:gLift;animation-duration:.75s;animation-timing-function:cubic-bezier(.22,1,.36,1);animation-fill-mode:backwards}
#avances.rv .avance-card:nth-child(2){animation-delay:.06s}
#avances.rv .avance-card:nth-child(3){animation-delay:.2s}
@keyframes gGem{0%{opacity:0;transform:scale(.55) rotate(-16deg)}55%{opacity:1;filter:drop-shadow(0 0 9px rgba(212,175,114,.85))}100%{opacity:1;transform:none;filter:none}}
#avances.rv .sec-icon svg{animation:gGem 1.15s ease both}

/* — ESPACE HOMMES : Assurance (montée nette + nœud papillon qui se noue) — */
@keyframes gFirm{0%{opacity:0;transform:translateY(22px)}100%{opacity:1;transform:none}}
#hommes.rv .hommes-num,#hommes.rv .hommes-title,#hommes.rv .hm-rule{animation:gFirm .7s cubic-bezier(.22,1,.36,1) both}
#hommes.rv .hommes-title{animation-delay:.08s}
#hommes.rv .hm-rule{animation-delay:.16s}
#hommessoins.rv .soin{animation-name:gFirm;animation-duration:.55s;animation-timing-function:cubic-bezier(.22,1,.36,1);animation-fill-mode:backwards}
@keyframes gBow{0%{opacity:0;transform:scale(.3)}55%{opacity:1;transform:scale(1.14)}100%{opacity:1;transform:scale(1)}}
.hommes-emblem{display:flex;justify-content:center;margin-bottom:10px}
.hommes-emblem svg{width:36px;height:36px;fill:none;stroke:#D4AF72;stroke-width:1.4;stroke-linejoin:round;stroke-linecap:round}
#hommes.rv .hommes-emblem{animation:gBow .95s cubic-bezier(.5,0,.3,1.5) both}

/* Mouvement réduit : tout apparaît sans animation */
@media (prefers-reduced-motion:reduce){
  #apropos.rv .apropos-img-wrap,#apropos.rv .apropos-block,#apropos.rv .stat-card,#apropos.rv .horaires-card,#apropos.rv .contact-row,#apropos.rv .maisons,
  #visage.rv .soin,#corps.rv .soin,#epilation.rv .soin,#ongles.rv .soin,#avances.rv .avance-card,#hommessoins.rv .soin,
  #hommes.rv .hommes-num,#hommes.rv .hommes-title,#hommes.rv .hm-rule,
  .sec-icon svg,.hommes-emblem{animation:none!important;opacity:1!important;transform:none!important;filter:none!important;clip-path:none!important}
}
</style>
</head>"""
assert s.count("</head>") == 1
s = s.replace("</head>", ANIM)

# garde-fous
assert s.count('wa.me/2290197085576') == wa0, "liens WhatsApp impactés !"
assert '🎩' not in s, "emoji 🎩 résiduel"
assert 'id="hommessoins"' in s and "'hommessoins'" in s, "révélation Hommes non branchée"
io.open(F, "w", encoding="utf-8").write(s)
print("animations signatures OK : 7 sections + icônes animées + nœud papillon + révélation Hommes")

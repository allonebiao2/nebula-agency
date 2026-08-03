# -*- coding: utf-8 -*-
"""
Refonte, vague 1 : la coquille. Ce qui profite aux 22 écrans d'un coup.

Trois changements, tous tirés de PRODUCT.md et DESIGN.md :

1. **NAVIGATION ÉCRITE.** Les libellés existaient déjà dans le code (`NAV`), ils
   n'étaient jamais affichés : on ne voyait que des icônes. Une coupe, un sablier,
   un mégaphone ne se devinent pas. Sur PC, colonne de 216 px avec les mots. Sur
   téléphone, 5 entrées avec leur mot sous l'icône, le reste sous « Plus ».

2. **DEUX THÈMES.** Sombre par défaut, clair d'un clic, mémorisé. Le clair existe
   pour le téléphone en plein soleil à Cotonou, pas pour la mode. Les couleurs de
   statut changent de VALEUR entre les thèmes : un vert clair sur blanc est
   illisible.

3. **LES MOTS DU LECTEUR.** « Affiliés », « Recrues », « Publication »,
   « Questions prospects » sont des mots d'initiés. Ils deviennent ce qu'un
   débutant comprend sans explication.

Idempotent, UTF-8 strict.
    python nebula-affilies/_outils/_refonte_coquille.py
"""
import io, re, sys
from pathlib import Path

RACINE = Path(r"C:/Users/USER/nebula-agency/nebula-affilies")

# --- 1. les mots ------------------------------------------------------------
MOTS_NAV = {
    "'Affiliés'": "'Mes partenaires'",
    "'Réseau'": "'Qui a recruté qui'",
    "'Clients'": "'Les clients'",
    "'Paiements'": "'À payer'",
    "'Recrues'": "'Candidatures'",
    "'Classement'": "'Classement'",
    "'Rangs'": "'Les rangs'",
    "'Documentation'": "'Documents'",
    "'Publication'": "'À partager'",
    "'Questions prospects'": "'Questions reçues'",
}
MOTS_TITRES = {
    "aff: 'Réseau d\\'affiliés'": "aff: 'Mes partenaires'",
    "reseau: 'Arborescence du réseau'": "reseau: 'Qui a recruté qui'",
    "leads: 'Clients du réseau'": "leads: 'Les clients'",
    "paiements: 'Commissions à verser'": "paiements: 'Ce que je dois payer'",
    "recrues: 'Candidatures & recrues'": "recrues: 'Candidatures reçues'",
    "classement: 'Classement du réseau'": "classement: 'Classement'",
    "rangs: 'L\\'échelle des rangs'": "rangs: 'Les rangs'",
    "docs: 'Documentation partenaires'": "docs: 'Documents des partenaires'",
    "publi: 'Contenus à publier'": "publi: 'Contenus à partager'",
    "questions: 'Questions des prospects'": "questions: 'Questions reçues'",
}

# --- 2. la coquille : CSS ---------------------------------------------------
CSS = """

/* ══════════ REFONTE, VAGUE 1 : LA COQUILLE (2026-08-03) ══════════
   Voir PRODUCT.md et DESIGN.md. Trois idées : la navigation porte des MOTS,
   deux thèmes au choix, et le décor cesse de concurrencer l'information. */

/* ---- Thème clair. Les statuts changent de VALEUR, pas juste d'opacité :
        un vert clair sur blanc ne se lit pas. ---- */
html[data-theme="clair"] {
  --bg:#f7f7fa; --bg-2:#eeeef4;
  --ink:#16161f; --muted:#55536b; --faint:#6c6a82;
  --glass:rgba(0,0,0,.025); --glass-2:rgba(0,0,0,.045);
  --hair:rgba(0,0,0,.10); --hair-2:rgba(0,0,0,.16);
  --accent:#6a45f5; --accent-tx:#5a35e0; --accent-2:#0e7490;
  --ok:#0a8f57; --warn:#a86a00; --bad:#c8253f; --gold:#8a6a00;
  --sh-soft:0 18px 44px -22px rgba(20,16,60,.28);
  color-scheme: light;
}
html[data-theme="clair"] body { color: var(--ink); }
/* Le décor nocturne n'a aucun sens sur fond clair. */
html[data-theme="clair"] .bg-orbs { opacity:.28; filter:saturate(.7); }
html[data-theme="clair"] .bg-grain { display:none; }
html[data-theme="clair"] .dock { background:#ffffff; }
html[data-theme="clair"] .card > .in {
  background: linear-gradient(180deg, rgba(0,0,0,.012), rgba(0,0,0,.004));
}

/* ---- La navigation porte des mots ---- */
.app { grid-template-columns: 216px 1fr; }
.dock { background: var(--surface-2, rgba(255,255,255,.03)); }
.nav-i {
  display: flex; align-items: center; gap: 11px;
  width: 100%; height: auto; min-height: 44px;
  padding: 9px 12px; border-radius: 12px;
  justify-content: flex-start; text-align: left;
  font-size: .875rem; font-weight: 500; line-height: 1.25;
  color: var(--muted);
}
.nav-i .nav-tx { display: block; }
.nav-i svg { flex: 0 0 19px; }
.nav-i.on { color: var(--ink); background: color-mix(in srgb, var(--accent) 16%, transparent); }
.nav-i:hover { color: var(--ink); }

/* ---- Téléphone : 5 entrées avec leur mot, le reste sous « Plus » ---- */
@media (max-width: 640px) {
  .app { grid-template-columns: 1fr; }
  .dock { display: grid; grid-template-columns: repeat(6, 1fr); gap: 2px;
          padding: 6px 4px calc(6px + env(safe-area-inset-bottom, 0px));
          overflow: visible; }
  .nav-i {
    flex-direction: column; gap: 3px; padding: 6px 2px;
    min-height: 50px; font-size: .62rem; font-weight: 600;
    letter-spacing: .01em; text-align: center; justify-content: center;
  }
  .nav-i .nav-tx {
    max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  .nav-i svg { flex: none; width: 20px; height: 20px; }
  /* au-delà de la 5e entrée, on passe par « Plus » */
  .dock .nav-i[data-rang="reste"] { display: none; }
  .dock.deplie .nav-i[data-rang="reste"] { display: flex; }
  .dock.deplie { grid-template-columns: repeat(4, 1fr); max-height: 62vh; overflow-y: auto; }
}
@media (min-width: 641px) {
  .nav-i[data-plus] { display: none; }   /* « Plus » n'existe que sur téléphone */
}
"""

# --- 3. le rendu de la navigation + le bouton de thème ----------------------
JS_NAV = """function buildDock() {
  const nav = document.getElementById('nav');
  const dock = nav.closest('.dock') || nav;
  const PRINCIPALES = 5;                      // ce qu'on voit sans déplier, sur téléphone
  NAV.forEach((n, i) => {
    const b = el(`<button class="nav-i" id="navi-${n.id}" data-v="${n.id}" data-rang="${i < PRINCIPALES ? 'tete' : 'reste'}" title="${n.label}">${icon(n.icon)}<span class="nav-tx">${n.label}</span></button>`);
    b.onclick = () => { switchView(n.id); dock.classList.remove('deplie'); };
    nav.appendChild(b);
  });
  // « Plus » : sur téléphone, une navigation de 12 icônes muettes qui défile
  // n'est pas une navigation, c'est une devinette.
  const plus = el(`<button class="nav-i" data-plus="1" title="Voir tout le menu">${icon('menu') || icon('spark')}<span class="nav-tx">Plus</span></button>`);
  plus.onclick = () => { dock.classList.toggle('deplie'); sound.sfx.tab(); };
  nav.appendChild(plus);
  document.getElementById('logout').innerHTML = icon('logout');
  document.getElementById('logout').onclick = async () => { await api('/api/logout', { body: {} }); location.href = '{{ADMIN_PATH}}'; };
}"""

JS_THEME = """

/* ===== Thème clair / sombre =================================================
   Le clair n'est pas décoratif : il existe pour le téléphone en plein soleil.
   Le choix est mémorisé, et suit le réglage du système à la première visite. */
(function themeInit() {
  const CLE = 'naff_theme';
  const de = document.documentElement;
  const sysClair = () => { try { return matchMedia('(prefers-color-scheme: light)').matches; } catch (e) { return false; } };
  const lu = (() => { try { return localStorage.getItem(CLE); } catch (e) { return null; } })();
  const poser = (t) => {
    de.setAttribute('data-theme', t);
    try { localStorage.setItem(CLE, t); } catch (e) {}
    const b = document.getElementById('theme-b');
    if (b) {
      b.innerHTML = (typeof icon === 'function') ? icon(t === 'clair' ? 'moon' : 'sun') || (t === 'clair' ? '🌙' : '☀️') : (t === 'clair' ? '🌙' : '☀️');
      b.title = t === 'clair' ? 'Passer en sombre' : 'Passer en clair';
      b.setAttribute('aria-label', b.title);
    }
  };
  poser(lu || (sysClair() ? 'clair' : 'sombre'));
  window.NAFF_TOGGLE_THEME = () => poser(de.getAttribute('data-theme') === 'clair' ? 'sombre' : 'clair');
})();
"""


def main():
    faits = []

    # ---- CSS ----
    p = RACINE / "static/app.css"
    css = io.open(p, encoding="utf-8").read()
    if "REFONTE, VAGUE 1 : LA COQUILLE" not in css:
        io.open(p, "w", encoding="utf-8", newline="").write(css.rstrip() + CSS)
        faits.append("coquille : navigation écrite + thème clair (CSS)")

    # ---- app.js : le thème ----
    p = RACINE / "static/app.js"
    js = io.open(p, encoding="utf-8").read()
    if "NAFF_TOGGLE_THEME" not in js:
        io.open(p, "w", encoding="utf-8", newline="").write(js.rstrip() + JS_THEME)
        faits.append("bascule de thème, mémorisée")

    # ---- les pages ----
    for f in ("admin.html", "partenaire.html"):
        pf = RACINE / f
        if not pf.exists():
            continue
        h = io.open(pf, encoding="utf-8").read()
        avant = h

        # navigation écrite
        m = re.search(r"function buildDock\(\) \{.*?\n\}", h, re.S)
        if m and "nav-tx" not in m.group(0):
            corps = JS_NAV
            if f == "partenaire.html":
                corps = corps.replace("location.href = '{{ADMIN_PATH}}'", "location.href = '/'")
            h = h[:m.start()] + corps + h[m.end():]

        # les mots du lecteur
        for vieux, neuf in MOTS_NAV.items():
            h = h.replace("label: " + vieux, "label: " + neuf)
        for vieux, neuf in MOTS_TITRES.items():
            h = h.replace(vieux, neuf)

        # le bouton de thème, à côté des autres boutons ronds
        if 'id="theme-b"' not in h and 'id="snd"' in h:
            h = h.replace('<button class="icon-btn" id="snd"',
                          '<button class="icon-btn" id="theme-b" onclick="NAFF_TOGGLE_THEME()" title="Changer de thème"></button>'
                          '<button class="icon-btn" id="snd"', 1)

        if h != avant:
            io.open(pf, "w", encoding="utf-8", newline="").write(h)
            faits.append(f"{f} : navigation écrite, mots simples, bouton de thème")

    if not faits:
        print("  Tout était déjà en place.")
        return 0
    for x in faits:
        print("  ✓", x)
    return 0


if __name__ == "__main__":
    sys.exit(main())

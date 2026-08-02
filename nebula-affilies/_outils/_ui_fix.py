# -*- coding: utf-8 -*-
"""
Corrige ce que l'audit a réellement mesuré dans les deux back-offices.

Rien n'est corrigé « au cas où » : chaque changement répond à un défaut relevé
par `_audit_ui.py`, avec son chiffre.

  1. `--faint` : contraste 3,69 sur les libellés de statistiques, là où il en
     faut 4,5. Passe à #8a8aa6 → 5,68. Reste nettement plus discret que
     `--muted` (7,19), donc la hiérarchie visuelle est préservée.
  2. Cibles tactiles sous 44 px : les boutons ronds (42, puis 40 en mobile), la
     croix des notifications (34) et les boutons de pagination (38 de haut).
     44 px est le minimum pour un doigt ; en dessous, on rate sa cible.
  3. Le confort de frappe sur mobile : un champ sous 16 px fait zoomer Safari
     tout seul, et la page part de travers.

Idempotent, UTF-8 strict.
    python nebula-affilies/_outils/_ui_fix.py
"""
import io, sys
from pathlib import Path

RACINE = Path(r"C:/Users/USER/nebula-agency/nebula-affilies")

CSS = [
    # (ce qu'on cherche, ce qu'on pose, pourquoi)
    ("--faint:#6b6b86;", "--faint:#8a8aa6;",
     "contraste des libellés : 3,69 → 5,68 (minimum 4,5)"),
    (".icon-btn{width:42px;height:42px;", ".icon-btn{width:44px;height:44px;",
     "bouton rond : 42 → 44 px, la taille d'un doigt"),
    ("  .icon-btn{width:40px;height:40px}", "  .icon-btn{width:44px;height:44px}",
     "idem en mobile, où c'était encore plus petit"),
    (".btn.sm{padding:9px 12px 9px 16px;font-size:.85rem}",
     ".btn.sm{padding:9px 14px 9px 18px;font-size:.85rem;min-height:44px}",
     "petits boutons : hauteur minimale de 44 px"),
]

HTML = [
    ('id="notif-close" style="width:34px;height:34px"',
     'id="notif-close" style="width:44px;height:44px"',
     "croix des notifications : 34 → 44 px"),
]

# Ajouté en fin de feuille : ce qui n'a pas de règle existante à modifier.
APPOINT = """

/* ============ CONFORT ET LISIBILITÉ (audit du 2026-08-02) ============
   Chaque règle répond à une mesure, pas à une impression. */

/* Un champ sous 16 px déclenche le zoom automatique de Safari iOS : la page
   saute et se retrouve de travers. 16 px est le seuil, pas une préférence. */
@media (max-width: 640px) {
  input, select, textarea { font-size: 16px; }
}

/* Les liens de bas de formulaire faisaient 16 à 18 px de haut : impossibles à
   viser au pouce. On leur donne de la hauteur sans changer leur apparence. */
.link-sm, a.small, .foot-link {
  display: inline-flex; align-items: center;
  min-height: 44px; padding: 0 2px;
}

/* Le focus au clavier était invisible sur fond sombre : on ne savait plus où
   l'on était en naviguant à la tabulation. */
:where(a, button, input, select, textarea, summary, [tabindex]):focus-visible {
  outline: 2px solid var(--accent-2);
  outline-offset: 2px;
  border-radius: 8px;
}

/* Respecter le réglage système « réduire les animations ». Sans cela, une
   interface qui bouge en permanence est pénible, voire douloureuse, pour
   certaines personnes. */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
    scroll-behavior: auto !important;
  }
}
"""


def main():
    faits = []

    css_p = RACINE / "static/app.css"
    css = io.open(css_p, encoding="utf-8").read()
    for vieux, neuf, pourquoi in CSS:
        if neuf in css:
            continue
        if vieux not in css:
            print(f"  ⚠️  motif introuvable : {vieux[:44]}")
            continue
        css = css.replace(vieux, neuf, 1)
        faits.append(pourquoi)

    if "CONFORT ET LISIBILITÉ (audit du 2026-08-02)" not in css:
        css = css.rstrip() + APPOINT
        faits.append("zoom iOS, cibles des liens, focus clavier visible, animations réduites")

    io.open(css_p, "w", encoding="utf-8", newline="").write(css)

    for f in ("admin.html", "partenaire.html"):
        p = RACINE / f
        if not p.exists():
            continue
        h = io.open(p, encoding="utf-8").read()
        avant = h
        for vieux, neuf, pourquoi in HTML:
            if vieux in h:
                h = h.replace(vieux, neuf)
                faits.append(f"{f} : {pourquoi}")
        if h != avant:
            io.open(p, "w", encoding="utf-8", newline="").write(h)

    if not faits:
        print("  Tout était déjà corrigé.")
        return 0
    for f in faits:
        print("  ✓", f)

    # garde-fous
    css = io.open(css_p, encoding="utf-8").read()
    assert "--faint:#8a8aa6" in css, "le jeton de contraste n'est pas posé"
    assert "width:44px;height:44px" in css, "les boutons ronds ne sont pas à 44 px"
    print("  ✓ contrôles passés")
    return 0


if __name__ == "__main__":
    sys.exit(main())

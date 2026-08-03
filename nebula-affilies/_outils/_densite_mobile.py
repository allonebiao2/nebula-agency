# -*- coding: utf-8 -*-
"""
Rend les back-offices lisibles sur un téléphone, sans rien casser sur PC.

Mesuré sur un écran de 390 px avant correction :
  · chaque carte de chiffre faisait **108 px de haut** pour afficher UN nombre ;
  · les 4 compteurs prenaient **tout l'écran**, une carte par ligne ;
  · il fallait faire défiler **1 811 px** pour voir le tableau de bord ;
  · en-tête 62 px + barre du bas 63 px = 125 px de décor avant le contenu.

Cause : en mobile, TOUTES les cartes passent en pleine largeur
(`.col-3 … .col-8 { grid-column: span 12 }`). Une carte qui contient un seul
chiffre n'a aucune raison de prendre toute la largeur d'un téléphone.

Ce qu'on change, et rien d'autre :
  1. les petites cartes de chiffres vont **par deux** sur mobile ;
  2. les marges intérieures et les écarts se resserrent ;
  3. les chiffres restent gros, mais moins démesurés, et les libellés
     redeviennent lisibles au lieu d'être étirés par l'interlettrage ;
  4. rien ne descend sous 44 px de cible tactile, ni sous les contrastes
     déjà corrigés.

Idempotent, UTF-8 strict.
    python nebula-affilies/_outils/_densite_mobile.py
"""
import io, sys
from pathlib import Path

RACINE = Path(r"C:/Users/USER/nebula-agency/nebula-affilies")

CSS = """

/* ============ DENSITÉ SUR TÉLÉPHONE (mesuré le 2026-08-03) ============
   Avant : 4 compteurs occupaient tout l'écran, 108 px chacun, et il fallait
   faire défiler 1 811 px pour lire le tableau de bord. Une carte qui porte un
   seul chiffre n'a pas besoin de toute la largeur d'un téléphone. */

@media (max-width: 640px) {

  /* Les petites cartes de chiffres vont PAR DEUX. C'est le changement qui
     divise par deux la hauteur du tableau de bord. */
  .col-3 { grid-column: span 6; }
  .bento { gap: 10px; }

  /* On resserre l'intérieur des cartes : 16 px de marge sur un écran de 390 px,
     c'est 8 % de la largeur perdue de chaque côté. */
  .card > .in { padding: 13px 14px; }
  .work { padding: 14px 12px 104px; }

  /* Le chiffre reste le héros, mais 2,4 rem sur un téléphone poussait la carte
     à 108 px de haut pour rien. */
  .stat .num { font-size: 1.85rem; }
  .stat .lbl {
    font-size: .7rem;
    letter-spacing: .06em;      /* .14em étirait les libellés sur 2 lignes */
    margin-bottom: 5px;
    line-height: 1.25;
  }
  .stat .sub { font-size: .76rem; margin-top: 4px; }

  /* L'en-tête prenait 62 px avant même le premier chiffre. */
  .topbar { margin-bottom: 14px; }
  .topbar h2 { font-size: 1.28rem !important; }

  /* Les titres de section : lisibles sans manger un tiers de l'écran. */
  .h-section { font-size: 1.3rem; }

  /* Les lignes de liste : de l'air, mais pas du vide. */
  .rl-row { padding: 9px 11px; gap: 10px; }
  .lb-row { padding: 10px 12px; gap: 10px; grid-template-columns: 30px 40px 1fr auto; }

  /* Les pastilles d'information ne doivent pas faire une ligne chacune. */
  .chip { font-size: .74rem; padding: 5px 9px; }
}

/* Très petits téléphones : on garde deux colonnes, on ne rétrécit que le texte.
   Repasser à une colonne annulerait tout le gain. */
@media (max-width: 360px) {
  .stat .num { font-size: 1.6rem; }
  .stat .lbl { font-size: .66rem; }
  .card > .in { padding: 11px 12px; }
}
"""


def main():
    p = RACINE / "static/app.css"
    css = io.open(p, encoding="utf-8").read()
    if "DENSITÉ SUR TÉLÉPHONE (mesuré le 2026-08-03)" in css:
        print("  Déjà appliqué.")
        return 0
    io.open(p, "w", encoding="utf-8", newline="").write(css.rstrip() + CSS)
    print("  ✓ densité mobile posée")

    # garde-fous : on n'a pas dégradé ce qui avait été corrigé hier
    css = io.open(p, encoding="utf-8").read()
    for motif, quoi in (("--faint:#8a8aa6", "le contraste corrigé"),
                        ("width:44px;height:44px", "les cibles tactiles de 44 px"),
                        ("perf-lite", "le mode performance")):
        print(("  ✓ " if motif in css else "  ⛔ ") + quoi + " intact")
    return 0


if __name__ == "__main__":
    sys.exit(main())

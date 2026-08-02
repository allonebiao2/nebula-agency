# -*- coding: utf-8 -*-
"""
Mode performance adaptatif pour les deux back-offices.

Mesuré avant d'agir, sur un écran de téléphone, en défilant :

    tel quel ................................ 35 images/s
    sans les flous d'arrière-plan ........... 53
    sans les animations infinies ............ 56
    sans les ombres ......................... 35   (aucun effet)
    sans flous NI animations ................ 60   (le plafond)

Les flous et les deux animations d'ambiance coûtent donc **25 images sur 60**.
Les ombres, rien : on n'y touche pas.

Le remède est celui qui a fait ses preuves sur Boussole : on ne dégrade personne
d'office. Sur un appareil confortable, tout reste. Sur un appareil modeste, ou
si la fluidité mesurée s'effondre, la classe `perf-lite` calme les effets
d'ambiance — jamais les interactions, jamais les transitions au toucher.

Idempotent, UTF-8 strict.
    python nebula-affilies/_outils/_perf_mode.py
"""
import io, sys
from pathlib import Path

RACINE = Path(r"C:/Users/USER/nebula-agency/nebula-affilies")

CSS = """

/* ============ MODE PERFORMANCE ADAPTATIF (mesuré le 2026-08-02) ============
   Sur appareil modeste, ou si la fluidité mesurée tombe, on calme les effets
   d'AMBIANCE : les flous d'arrière-plan et les deux animations en boucle.
   On ne touche NI aux interactions, NI aux transitions au toucher : c'est ce
   qui donne la sensation de réactivité, et ça ne coûte rien.
   Piloté par initPerfMode() dans app.js, via .perf-lite sur <html>.
   .perf-pause = onglet en arrière-plan : inutile d'animer ce que personne
   ne regarde. */

/* Le flou d'arrière-plan est l'opération la plus chère de toute l'interface :
   53 images/s contre 35 une fois retiré. Les fonds sont déjà presque opaques,
   la lisibilité ne bouge pas. */
html.perf-lite .drawer,
html.perf-lite .sheet,
html.perf-lite .scrim,
html.perf-lite .chat-search,
html.perf-lite .seg {
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

/* Les deux animations d'ambiance : la dérive du fond et l'anneau du bouton
   NOVA. Décoratives toutes les deux. */
html.perf-lite .bg-orbs,
html.perf-lite .nova-fab .pulse {
  animation: none !important;
}
html.perf-lite .nova-fab .pulse { opacity: .35; }

/* Onglet en arrière-plan : on suspend tout ce qui tourne en boucle. */
html.perf-pause *,
html.perf-pause *::before,
html.perf-pause *::after {
  animation-play-state: paused !important;
}
"""

JS = """

/* ===== Mode performance adaptatif =========================================
   Mesuré le 2026-08-02 : les flous d'arrière-plan et les deux animations
   d'ambiance coûtent 25 images par seconde sur 60. On ne dégrade personne
   d'office : on regarde l'appareil, puis on mesure la fluidité réelle.
   ======================================================================== */
NA.initPerfMode = function () {
  var de = document.documentElement;
  if (de.dataset.perfInit) return;      // une seule fois
  de.dataset.perfInit = '1';

  var calme = function (raison) {
    if (de.classList.contains('perf-lite')) return;
    de.classList.add('perf-lite');
    try { console.info('[NEBULA] mode calme :', raison); } catch (e) {}
  };

  // 1. l'appareil se déclare-t-il modeste ?
  var coeurs = navigator.hardwareConcurrency || 8;
  var memoire = navigator.deviceMemory || 8;
  if (coeurs <= 4 || memoire <= 4) calme('appareil modeste (' + coeurs + ' cœurs, ' + memoire + ' Go)');

  // 2. la personne a-t-elle demandé moins d'animations ?
  try {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) calme('réglage système');
  } catch (e) {}

  // 3. sinon, on mesure vraiment, une seule fois, sans bloquer le démarrage
  if (!de.classList.contains('perf-lite')) {
    setTimeout(function () {
      var n = 0, t0 = performance.now();
      (function tic() {
        n++;
        var dt = performance.now() - t0;
        if (dt < 1000) { requestAnimationFrame(tic); return; }
        var fps = n / (dt / 1000);
        if (fps < 45) calme('fluidité mesurée à ' + Math.round(fps) + ' images/s');
      })();
    }, 2500);
  }

  // 4. onglet en arrière-plan : rien à animer pour personne
  document.addEventListener('visibilitychange', function () {
    de.classList.toggle('perf-pause', document.hidden);
  });
};
try { NA.initPerfMode(); } catch (e) {}
"""


def main():
    faits = []

    css_p = RACINE / "static/app.css"
    css = io.open(css_p, encoding="utf-8").read()
    if "MODE PERFORMANCE ADAPTATIF (mesuré le 2026-08-02)" not in css:
        io.open(css_p, "w", encoding="utf-8", newline="").write(css.rstrip() + CSS)
        faits.append("règles .perf-lite ajoutées au CSS")

    js_p = RACINE / "static/app.js"
    js = io.open(js_p, encoding="utf-8").read()
    if "NA.initPerfMode" not in js:
        io.open(js_p, "w", encoding="utf-8", newline="").write(js.rstrip() + JS)
        faits.append("initPerfMode() ajouté à app.js")

    if not faits:
        print("  Tout était déjà en place.")
        return 0
    for x in faits:
        print("  ✓", x)
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""
À QUI EST LE COÛT ? — Angy Art, attribution mécanisme par mécanisme.

    python _attribuer.py [--lent 6] [--vue 1440]

`_fluidite.py` dit QUE ça rame (médiane 66,7 ms sur ordinateur, 85 % des
images perdues). Il ne dit pas POURQUOI. Ici on éteint un mécanisme à la fois
et on remesure : la différence est le coût de ce mécanisme, et rien d'autre.

⚠️ ON N'ÉTEINT RIEN DÉFINITIVEMENT. Ce script ne modifie aucun fichier du
site : il injecte des neutralisants au chargement, dans un navigateur jetable.
"""
import argparse
import functools
import http.server
import os
import socketserver
import statistics
import sys
import threading

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))

SONDE = """
window.__f = { t: [], long: [] };
(function () {
  let p = 0;
  function tic(ts) { if (p) window.__f.t.push(ts - p); p = ts; requestAnimationFrame(tic); }
  requestAnimationFrame(tic);
  try { new PerformanceObserver(l => { for (const e of l.getEntries())
    window.__f.long.push(Math.round(e.duration)); }).observe({ entryTypes: ['longtask'] });
  } catch (e) {}
})();
"""

# ── les neutralisants, posés AVANT que le site ne s'exécute ────────────────
SANS_POINTEUR_FIN = """
/* `fin` commande le défilement lissé maison ET le curseur suiveur. */
(function () {
  const vrai = window.matchMedia.bind(window);
  window.matchMedia = function (q) {
    if (/hover\\s*:\\s*hover/.test(q) && /pointer\\s*:\\s*fine/.test(q))
      return { matches: false, media: q, addListener() {}, removeListener() {},
               addEventListener() {}, removeEventListener() {}, onchange: null };
    return vrai(q);
  };
})();
"""

SANS_GRAIN = """
document.addEventListener('DOMContentLoaded', function () {
  const s = document.createElement('style');
  s.textContent = 'body::after{display:none!important}';
  document.head.appendChild(s);
});
"""

SANS_PARALLAXE = """
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[data-para]').forEach(e => e.removeAttribute('data-para'));
}, true);
"""

SANS_FLOU_CARROUSEL = """
document.addEventListener('DOMContentLoaded', function () {
  const s = document.createElement('style');
  s.textContent = '.car{filter:none!important;transition:transform .8s cubic-bezier(.4,0,.2,1),opacity .8s ease!important}';
  document.head.appendChild(s);
});
"""

SANS_MELANGE = """
document.addEventListener('DOMContentLoaded', function () {
  const s = document.createElement('style');
  s.textContent = '*{mix-blend-mode:normal!important}';
  document.head.appendChild(s);
});
"""

def style(css):
    """Pose une règle après le chargement, sans toucher au site."""
    return ("document.addEventListener('DOMContentLoaded', function () {"
            "  const s = document.createElement('style');"
            "  s.textContent = " + repr(css).replace("'", '"', 2) + ";"
            "  document.head.appendChild(s); });")


def _st(css):
    return ("document.addEventListener('DOMContentLoaded', function(){"
            "var s=document.createElement('style');s.textContent=%s;"
            "document.head.appendChild(s);});" % ("`" + css + "`"))


# ⚠️ `*` NE SÉLECTIONNE PAS LES PSEUDO-ÉLÉMENTS. Le premier jet neutralisait
#    `mix-blend-mode` avec `*{...}` et concluait « le mélange ne coûte rien » :
#    il n'avait jamais touché `body::after`, qui est justement le coupable.
#    Cette série vise le grain par ses vraies propriétés, une par une.
SERIE_GRAIN = [
    ("tel quel", []),
    ("body::after sans mix-blend-mode", [_st("body::after{mix-blend-mode:normal!important}")]),
    ("body::after en inset:0 (au lieu de -30%)", [_st("body::after{inset:0!important}")]),
    ("body::after sans son image de bruit", [_st("body::after{background-image:none!important}")]),
    ("body::after en absolute (au lieu de fixed)", [_st("body::after{position:absolute!important}")]),
    ("body::after supprime", [_st("body::after{display:none!important}")]),
]

SANS_LIN = _st(".scene--lin::before,.scene--lin2::before,.scene--lin3::before,"
               ".scene--lin4::before{mix-blend-mode:normal!important}")
SANS_OMBRES = _st(".car-c,.car--photo .car-c{box-shadow:none!important}")

# ⚠️ L'ORDRE COMPTE PEU, MAIS LE MOMENT OUI. Cette série a d'abord été passée
#    alors que le grain plein écran écrasait tout : elle concluait « rien
#    d'autre ne coûte », ce qui était vrai *sous* le grain et faux une fois
#    celui-ci retiré. Une attribution se refait après chaque correction.
PASSES = [
    ("tel quel", []),
    ("sans le pointeur fin (moteur + curseur)", [SANS_POINTEUR_FIN]),
    ("sans le parallaxe", [SANS_PARALLAXE]),
    ("sans le flou du carrousel", [SANS_FLOU_CARROUSEL]),
    ("sans le melange des textures de scene", [SANS_LIN]),
    ("sans les grandes ombres portees", [SANS_OMBRES]),
]


class Serveur(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def centile(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(len(v) * p))] if v else 0


def une_passe(nav, url, largeur, hauteur, lent, scripts):
    pg = nav.new_page(viewport={"width": largeur, "height": hauteur})
    cdp = pg.context.new_cdp_session(pg)
    cdp.send("Emulation.setCPUThrottlingRate", {"rate": lent})
    for s in scripts:
        pg.add_init_script(s)
    pg.add_init_script(SONDE)
    pg.goto(url, wait_until="networkidle", timeout=120000)
    pg.wait_for_timeout(3600)
    pg.evaluate("window.__f.t = []; window.__f.long = [];")

    haut = pg.evaluate("document.documentElement.scrollHeight")
    pas = max(1, int((haut - hauteur) / 60))
    for _ in range(60):
        pg.mouse.wheel(0, pas)
        pg.wait_for_timeout(60)
    pg.wait_for_timeout(400)

    d = pg.evaluate("window.__f")
    t = [x for x in d["t"] if x < 500]
    pg.close()
    if not t:
        return None
    return {
        "median": statistics.median(t),
        "p95": centile(t, 0.95),
        "perdues": 100.0 * len([x for x in t if x > 32]) / len(t),
        "longues": len(d["long"]),
        "pire_tache": max(d["long"]) if d["long"] else 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lent", type=int, default=6)
    ap.add_argument("--vue", type=int, default=1440)
    ap.add_argument("--serie", choices=("mecanismes", "grain"), default="mecanismes")
    args = ap.parse_args()
    passes = SERIE_GRAIN if args.serie == "grain" else PASSES

    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ICI)
    srv = Serveur(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = "http://127.0.0.1:%d/" % srv.server_address[1]
    hauteur = 900 if args.vue >= 1000 else 844

    print("  %d px, processeur ralenti x%d\n" % (args.vue, args.lent))
    print("  %-42s %8s %8s %9s %8s %10s" %
          ("passe", "median", "p95", "perdues", "longues", "pire tache"))
    base = None
    for nom, scripts in passes:
        with sync_playwright() as p:
            nav = p.chromium.launch()
            r = une_passe(nav, url, args.vue, hauteur, args.lent, scripts)
            nav.close()
        if not r:
            print("  %-42s  (rien mesure)" % nom)
            continue
        if base is None:
            base = r["median"]
            gain = ""
        else:
            gain = "  (%+.0f %%)" % (100.0 * (r["median"] - base) / base)
        print("  %-42s %7.1fms %7.1fms %8.1f%% %8d %9dms%s" %
              (nom, r["median"], r["p95"], r["perdues"], r["longues"],
               r["pire_tache"], gain))
    srv.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())

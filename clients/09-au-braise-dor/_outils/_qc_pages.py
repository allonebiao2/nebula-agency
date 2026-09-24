# -*- coding: utf-8 -*-
"""
Les pages de contenu (carte, rubriques, traiteur, commande, contact), MESURÉES dans un navigateur.

    python _outils/_qc_pages.py          (sert `experience/out` lui-même sur un port libre)

Né le 2026-09-18 : sur la page des grillades, à 390 px, « Normal 3 000 F, Grand 6 000 F » débordait
de sa carte et se faisait couper ; sur `/carte/`, les prix longs des sauces poussaient la page de
43 px vers la droite. `_qc_seo.py` lit le HTML, il ne peut pas voir ça. Ici, pour chaque page, en
390 et 1440 px : aucun débordement horizontal, aucun élément qui sort de l'écran, 0 erreur JS, et
le H1 est dans le premier écran.
⚠️ Le serveur est lancé avec `--directory` depuis un autre dossier : servi DEPUIS `out/`, il le
verrouille sous Windows et la construction suivante échoue (EBUSY), vu le même jour.
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time

ICI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(ICI, "..", "experience", "out"))
PAGES = ["/", "/carte/", "/traiteur-et-place-des-fetes/", "/commander/", "/contact/", "/404/"]
ok, ko = [], []

MESURE = """() => { const W = document.documentElement.clientWidth; const fautes = [];
  for (const el of document.querySelectorAll('main *, footer *')) {
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
    if (getComputedStyle(el).position === 'fixed') continue;
    let p = el.parentElement, clip = false;
    while (p) { const o = getComputedStyle(p).overflowX;
      if (o === 'hidden' || o === 'auto' || o === 'scroll' || o === 'clip') { clip = true; break; } p = p.parentElement; }
    if (!clip && r.right > W + 1) fautes.push(el.tagName + ' « ' + (el.textContent || '').trim().slice(0, 30) + ' » +' + Math.round(r.right - W) + ' px');
  }
  const h1 = document.querySelector('h1'); const b = h1 ? h1.getBoundingClientRect() : null;
  return { debord: document.documentElement.scrollWidth - W, fautes: fautes.slice(0, 3),
           h1_visible: !!b && b.top < innerHeight + (location.pathname === '/' ? 99999 : 0) }; }"""


def dire(bon, txt):
    (ok if bon else ko).append(txt)
    print(("  vert  " if bon else "  ROUGE ") + txt)


def port_libre() -> int:
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from playwright.sync_api import sync_playwright
    rubriques = sorted(d for d in os.listdir(os.path.join(OUT, "carte"))
                       if os.path.isdir(os.path.join(OUT, "carte", d)))
    pages = PAGES + [f"/carte/{r}/" for r in rubriques]
    port = port_libre()
    serveur = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--directory", OUT],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=ICI)
    try:
        time.sleep(1.2)
        with sync_playwright() as p:
            nav = p.chromium.launch()
            for largeur in (390, 1440):
                pg = nav.new_page(viewport={"width": largeur, "height": 844})
                pg.emulate_media(reduced_motion="reduce")
                erreurs: list[str] = []
                pg.on("pageerror", lambda e: erreurs.append(str(e)))
                for u in pages:
                    erreurs.clear()
                    pg.goto(f"http://127.0.0.1:{port}{u}", wait_until="networkidle")
                    time.sleep(0.3)
                    r = pg.evaluate(MESURE)
                    dire(r["debord"] <= 0 and not r["fautes"],
                         f"{largeur:>4} {u:<30} débordement {r['debord']} px {r['fautes'] or ''}")
                    if u != "/":
                        dire(r["h1_visible"], f"{largeur:>4} {u:<30} le H1 est dans le premier écran")
                    dire(not erreurs, f"{largeur:>4} {u:<30} 0 erreur JS {erreurs[:1] or ''}")
                pg.close()
            nav.close()
    finally:
        serveur.terminate()
    print(f"\n{len(ok)} verts, {len(ko)} rouges")
    return 1 if ko else 0


if __name__ == "__main__":
    sys.exit(main())

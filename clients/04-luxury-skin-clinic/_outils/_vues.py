# -*- coding: utf-8 -*-
"""
_vues.py — photographie la vitrine Luxury Skin Clinic, zone par zone,
en 390 px (telephone emule) et en 1440 px (ordinateur).

    python _outils/_vues.py
    python _outils/_vues.py --seul heros
    python _outils/_vues.py --large 390

⚠️ On photographie la FENETRE, pas l'element : une barre `sticky` ou `fixed` se
   repeint au bord de la fenetre et se retrouve en plein milieu d'une capture
   d'element (lecon Hillary du 2026-09-04). La fenetre montre la page telle que
   la cliente la voit — les instruments flottants compris, qui sont justement
   ce qu'il faut surveiller.

Les images atterrissent dans _vues/. On les REGARDE : le QC protege la
logique, il ne protege pas le gout (standard NEBULA du 2026-08-01).
"""
import argparse, os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_vues")

# nom          selecteur a amener a l'ecran        cadrage
ZONES = [
    ("heros",       ".hero",                        "haut"),
    ("bandeau",     ".rdv-banner",                  "centre"),
    ("manifeste",   "#manifeste",                   "haut"),
    ("ruban",       ".ruban",                       "centre"),
    ("bande-visage", "#svcSections .sec-band",      "haut"),
    ("cartes",      "#svcSections .svc-grid",       "haut"),
    ("rdv",         "#rdv-booking",                 "haut"),
    ("rdv-bas",     "#rdvAck",                      "haut"),
    ("final",       ".final",                       "centre"),
]


def run(pagefile, only=None, widths=(390, 1440)):
    url = "file:///" + os.path.join(ROOT, pagefile).replace("\\", "/")
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for w in widths:
            mobile = w < 700
            ctx = b.new_context(
                viewport={"width": w, "height": 844 if mobile else 900},
                device_scale_factor=2, is_mobile=mobile, has_touch=mobile,
                user_agent=("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
                            "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1") if mobile else None,
            )
            page = ctx.new_page()
            page.goto(url)
            page.wait_for_timeout(2800)
            try:
                page.click("#welcome-gate", timeout=1500)
            except Exception:
                pass
            page.wait_for_timeout(1000)
            print("-- %d px" % w)
            for nom, sel, cadrage in ZONES:
                if only and only != nom:
                    continue
                el = page.query_selector(sel)
                if not el:
                    print("   ! %-13s selecteur absent (%s)" % (nom, sel))
                    continue
                page.evaluate(
                    """([s, mode]) => {
                        const e = document.querySelector(s);
                        const r = e.getBoundingClientRect();
                        const y = r.top + scrollY - (mode === 'haut' ? 0 : (innerHeight - r.height) / 2);
                        scrollTo({top: Math.max(0, y), behavior: 'instant'});
                    }""", [sel, cadrage])
                page.wait_for_timeout(1700)   # les revelations ont le temps de jouer
                p = os.path.join(OUT, "%s-%d.png" % (nom, w))
                page.screenshot(path=p)
                print("   . %s" % os.path.relpath(p, ROOT))
            ctx.close()
        b.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", default="luxury-skin-clinic.html")
    ap.add_argument("--seul")
    ap.add_argument("--large", type=int)
    a = ap.parse_args()
    run(a.page, a.seul, (a.large,) if a.large else (390, 1440))

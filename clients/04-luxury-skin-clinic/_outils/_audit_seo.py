# -*- coding: utf-8 -*-
"""
_audit_seo.py — releve SEO du site EN LIGNE, page par page.

    python _outils/_audit_seo.py
    python _outils/_audit_seo.py --local     # sur les fichiers du disque

⚠️ ON RELEVE DANS UN NAVIGATEUR, PAS AVEC curl. Un `curl` ne voit pas le
   balisage injecte par JavaScript, et il ne mesure ni le poids reel ni le
   decalage de mise en page. Ici tout est statique, mais l'outil doit rester
   juste le jour ou ca ne le sera plus.
"""
import argparse, json, os, sys
from playwright.sync_api import sync_playwright

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAINE = "https://luxuryclub229.com"

PAGES = [
    ("accueil",  "/",                    "index.html"),
    ("clinique", "/luxury-skin-clinic",  "luxury-skin-clinic.html"),
    ("ina",      "/ina-luxury",          "ina-luxury.html"),
    ("cozy",     "/cozy",                "cozy.html"),
]
# les pages internes : elles ne doivent PAS etre indexables
INTERNES = ["admin.html", "dossier.html", "facture.html", "carnet.html",
            "affiche-luxury-skin-clinic.html", "affiche-luxury-skin-clinic-carre.html",
            "carte-visite-luxury-skin-clinic.html", "404.html"]

RELEVE = """() => {
  const q = s => document.querySelector(s);
  const t = e => e ? (e.getAttribute('content') || e.textContent || '').trim() : null;
  const imgs = [...document.querySelectorAll('img')];
  const liens = [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'));
  return {
    titre: (document.title || '').trim(),
    desc: t(q('meta[name="description"]')),
    canonical: q('link[rel=canonical]') ? q('link[rel=canonical]').href : null,
    robots: t(q('meta[name="robots"]')),
    ogTitre: t(q('meta[property="og:title"]')),
    ogDesc: t(q('meta[property="og:description"]')),
    ogUrl: t(q('meta[property="og:url"]')),
    ogImage: t(q('meta[property="og:image"]')),
    lang: document.documentElement.getAttribute('lang'),
    h1: [...document.querySelectorAll('h1')].map(h => h.textContent.trim().slice(0, 70)),
    h2: document.querySelectorAll('h2').length,
    ordre: (() => {
      const n = [...document.querySelectorAll('h1,h2,h3,h4')].map(h => +h.tagName[1]);
      const sauts = [];
      for (let i = 1; i < n.length; i++) if (n[i] - n[i-1] > 1) sauts.push(n[i-1] + '->' + n[i]);
      return sauts;
    })(),
    jsonld: [...document.querySelectorAll('script[type="application/ld+json"]')]
              .map(s => { try { return JSON.parse(s.textContent); } catch(e) { return {erreur: true}; } }),
    images: imgs.length,
    imagesSansAlt: imgs.filter(i => i.getAttribute('alt') === null).length,
    imagesAltVide: imgs.filter(i => i.getAttribute('alt') === '').length,
    imagesLazy: imgs.filter(i => i.getAttribute('loading') === 'lazy').length,
    liensInternes: liens.filter(h => h && !/^(https?:|#|mailto:|tel:)/.test(h)).length,
    liensSortants: [...new Set(liens.filter(h => h && /^https?:/.test(h) && !h.includes('luxuryclub229')))].length,
    motsVisibles: (document.body.innerText || '').split(/\\s+/).filter(Boolean).length,
  };
}"""


def mesure(page):
    """Poids reel + decalage de mise en page + plus grande peinture."""
    return page.evaluate("""() => new Promise(res => {
        let cls = 0;
        try {
            new PerformanceObserver(l => { for (const e of l.getEntries())
                if (!e.hadRecentInput) cls += e.value; }).observe({type:'layout-shift', buffered:true});
        } catch(e) {}
        setTimeout(() => {
            const r = performance.getEntriesByType('resource');
            const nav = performance.getEntriesByType('navigation')[0] || {};
            const lcp = performance.getEntriesByType('largest-contentful-paint').pop();
            res({
                poids: Math.round(r.reduce((s,x) => s + (x.transferSize||0), 0) / 1024),
                requetes: r.length,
                images: Math.round(r.filter(x => x.initiatorType === 'img')
                                    .reduce((s,x) => s + (x.transferSize||0), 0) / 1024),
                ttfb: Math.round(nav.responseStart || 0),
                dcl: Math.round(nav.domContentLoadedEventEnd || 0),
                lcp: lcp ? Math.round(lcp.startTime) : null,
                cls: Math.round(cls * 1000) / 1000,
            });
        }, 3200);
    })""")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", action="store_true")
    a = ap.parse_args()
    base = ("file:///" + RACINE.replace("\\", "/") + "/") if a.local else DOMAINE + "/"
    rapport = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={"width": 1440, "height": 900},
                            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"))
        for nom, chemin, fichier in PAGES:
            page = ctx.new_page()
            url = base + (fichier if a.local else chemin.lstrip("/"))
            page.goto(url, wait_until="load")
            page.wait_for_timeout(2600)
            try:
                page.click("#welcome-gate", timeout=1200)
            except Exception:
                pass
            page.wait_for_timeout(600)
            d = page.evaluate(RELEVE)
            d["perf"] = mesure(page)
            rapport[nom] = d
            page.close()

        # les pages internes : indexables ou pas ?
        rapport["_internes"] = {}
        for f in INTERNES:
            page = ctx.new_page()
            try:
                page.goto(base + f, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(500)
                rapport["_internes"][f] = page.evaluate(
                    """() => {const m=document.querySelector('meta[name="robots"]');
                        return {robots: m ? m.content : null, titre: (document.title||'').trim().slice(0,60)};}""")
            except Exception as e:
                rapport["_internes"][f] = {"erreur": str(e)[:60]}
            page.close()
        b.close()

    p = os.path.join(RACINE, "_vues", "audit-seo.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(rapport, f, ensure_ascii=False, indent=1)
    print(json.dumps(rapport, ensure_ascii=False, indent=1)[:200])
    print("... releve complet dans _vues/audit-seo.json")


if __name__ == "__main__":
    main()

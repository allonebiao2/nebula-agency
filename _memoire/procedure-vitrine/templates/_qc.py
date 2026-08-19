#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GABARIT NEBULA — suite de contrôle qualité d'une vitrine.

    cp _memoire/procedure-vitrine/templates/_qc.py clients/NN-slug/
    cd clients/NN-slug && python3 _qc.py

Contrôles de base, valables sur TOUTE vitrine :
  · aucun débordement horizontal en 390 / 768 / 1440
  · toutes les cibles tactiles >= 44 px (y compris les liens de texte)
  · aucune erreur JavaScript, aucune ressource locale manquante
  · aucune animation infinie sous un `backdrop-filter` (leçon Boussole)
  · le rideau d'ouverture, s'il existe, se retire bien du DOM
  · les signatures de section se déclenchent au défilement

Ajouter ensuite les contrôles PROPRES AU CLIENT (arithmétique d'un tunnel,
nombre de champs d'un formulaire, liens WhatsApp…) dans `metier()`.

⚠️ Émulation obligatoire. Une capture headless sans `is_mobile` ignore le
   meta viewport, rend la page à 800 px et fait croire à un débordement qui
   n'existe pas.

⚠️ Le QC vert prouve que rien n'est cassé. Il ne prouve pas que c'est beau.
   Voir DIRECTION-ARTISTIQUE.md §5 : capturer chaque section en 390 et 1440,
   et LES REGARDER, une par une.

Doit être VERTE avant tout déploiement.
"""

import asyncio, glob, pathlib, sys
from playwright.async_api import async_playwright

# ⚠️ La console de Windows écrit en cp1252 : un « ≥ » ou un « → » dans un
#    libellé fait planter la suite APRÈS qu'elle a réussi ses contrôles.
for _f in (sys.stdout, sys.stderr):
    try: _f.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

URL = (pathlib.Path(__file__).resolve().parent / "vitrine.html").as_uri()
FAILS, NOTES = [], []

# Chromium préinstallé en session distante ; en local Playwright le trouve seul.
_C = [g for g in glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome") if "headless" not in g]
CHROME = {"executable_path": _C[0]} if _C else {}

VIEWPORTS = [(390, 844, True), (768, 1024, True), (1440, 900, False)]

# Signatures de section à vérifier : (sélecteur, nom lisible). À adapter par client.
SIGNATURES = []          # ex. [("#catalogue .piece", "02 le patron a la craie")]


def ok(c, m):
    (NOTES if c else FAILS).append(("OK  " if c else "FAIL") + "  " + m)


async def overflow(page, label):
    r = await page.evaluate("()=>({s:document.documentElement.scrollWidth,c:document.documentElement.clientWidth})")
    ok(r["s"] <= r["c"] + 1, f"{label} : pas de debordement horizontal ({r['s']}/{r['c']})")


async def tap_targets(page, label):
    bad = await page.evaluate("""()=>{
      const out=[];
      document.querySelectorAll('button,a,select,input,textarea').forEach(e=>{
        const st=getComputedStyle(e);
        if(st.display==='none'||st.visibility==='hidden')return;
        const r=e.getBoundingClientRect();
        if(r.width===0&&r.height===0)return;
        if(r.height<44) out.push((e.tagName+'.'+(e.className||'')).slice(0,50)+' h='+Math.round(r.height));
      });
      return out;}""")
    ok(not bad, f"{label} : cibles tactiles >= 44px" + ("" if not bad else " -> " + "; ".join(bad[:6])))


async def perf_rules(page):
    mauvais = await page.evaluate("""()=>{
      const out=[];
      document.querySelectorAll('*').forEach(e=>{
        const s=getComputedStyle(e);
        if(s.animationIterationCount==='infinite'){
          let p=e.parentElement;
          while(p){ const ps=getComputedStyle(p);
            if(ps.backdropFilter && ps.backdropFilter!=='none'){ out.push(e.className||e.tagName); break; }
            p=p.parentElement; }
        }
      });
      return out;}""")
    ok(not mauvais, "aucune animation infinie sous un backdrop-filter"
       + ("" if not mauvais else " -> " + str(mauvais[:3])))


async def metier(page):
    """Contrôles propres au client. À écrire pour chaque vitrine."""
    return


async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(**CHROME)

        for w, h, mobile in VIEWPORTS:
            ctx = await br.new_context(viewport={"width": w, "height": h},
                                       device_scale_factor=2 if mobile else 1,
                                       is_mobile=mobile, has_touch=mobile)
            page = await ctx.new_page()
            errs, failed = [], []
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.on("requestfailed", lambda r: failed.append(r.url))
            await page.goto(URL, wait_until="networkidle")
            await overflow(page, f"[{w}px] page")
            await tap_targets(page, f"[{w}px] page")
            ok(not errs, f"[{w}px] aucune erreur JS" + ("" if not errs else " -> " + errs[0][:120]))
            ok(not [u for u in failed if u.startswith("file:")],
               f"[{w}px] aucune ressource locale manquante")
            await ctx.close()

        ctx = await br.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")

        if await page.locator("#rideau").count():
            await page.wait_for_timeout(3000)
            ok(await page.locator("#rideau").count() == 0,
               "le rideau se retire du DOM apres l'ouverture (il ne bloque rien)")

        for sel, nom in SIGNATURES:
            await page.evaluate("s=>{const e=document.querySelector(s); if(e) e.scrollIntoView({block:'center'});}", sel)
            await page.wait_for_timeout(700)
            n = await page.locator(sel + ".vu").count()
            ok(n >= 1, f"signature {nom} : declenchee ({n} element(s))")

        await perf_rules(page)
        await metier(page)
        await overflow(page, "[1440px] apres ouverture")
        ok(not errs, "aucune erreur JS au parcours complet"
           + ("" if not errs else " -> " + errs[0][:140]))
        await ctx.close()
        await br.close()

    print("\n".join(NOTES))
    print("-" * 60)
    if FAILS:
        print("\n".join(FAILS))
        print(f"\n{len(FAILS)} ECHEC(S)")
        sys.exit(1)
    print(f"TOUT EST VERT — {len([n for n in NOTES if n.startswith('OK')])} controles")


asyncio.run(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HILLARY M. STYL — suite de contrôle qualité (53 contrôles).

    python3 _qc.py

Vérifie, sur navigateur réel émulé en 390 / 768 / 1440 px :
  · aucun débordement horizontal, page et modale ouverte
  · toutes les cibles tactiles >= 44 px
  · aucune erreur JavaScript, aucune ressource locale manquante
  · le nombre de mesures de chaque type de vêtement (9/15/11/6/8)
  · l'arithmétique du tunnel (pièce + expédition + express)
  · la date de disponibilité, calculée sur la borne HAUTE du délai
  · le repli email, le « sur devis », les mesures laissées vides

⚠️ Émulation obligatoire. Une capture headless sans `is_mobile` ignore le
   meta viewport, rend la page à 800 px et fait croire à un débordement
   qui n'existe pas.

Doit être VERTE avant tout déploiement.
"""
import asyncio, datetime, glob, pathlib, sys
from playwright.async_api import async_playwright

URL = (pathlib.Path(__file__).resolve().parent / "vitrine.html").as_uri()
FAILS, NOTES = [], []

# Chromium est preinstalle dans l'environnement distant ; en local Playwright
# le trouve tout seul.
_C = [g for g in glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome") if "headless" not in g]
CHROME = {"executable_path": _C[0]} if _C else {}
CHROME_CTX = {}

def ok(c, m):
    (NOTES if c else FAILS).append(("OK  " if c else "FAIL") + "  " + m)

VIEWPORTS = [(390, 844, True), (768, 1024, True), (1440, 900, False)]

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

            # onglet sur-mesure + ouverture d'une piece
            await page.click("#tab-sm")
            n = await page.locator(".piece").count()
            ok(n == 6, f"[{w}px] 6 pieces sur-mesure affichees (vu {n})")
            await page.locator(".piece", has_text="Robe droite").first.click()
            await page.wait_for_selector("#ov.on")
            await overflow(page, f"[{w}px] modale ouverte")
            await tap_targets(page, f"[{w}px] modale")
            await page.click("#btX")

            ok(not errs, f"[{w}px] aucune erreur JS" + ("" if not errs else " -> " + errs[0][:120]))
            ext = [u for u in failed if not u.startswith("file:")]
            if ext:
                NOTES.append("NOTE  requetes externes en echec (polices Google, reseau bloque) : %d" % len(ext))
            ok(not [u for u in failed if u.startswith("file:")], f"[{w}px] aucune ressource locale manquante")
            await ctx.close()

        # ---------- tunnel complet ----------
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        page = await ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")

        # nombre de mesures par type de vetement
        attendu = {"robe_taille": 9, "robe_droite": 15, "robe_ovale": 11, "pantalon": 6, "haut": 8}
        got = await page.evaluate("()=>{const o={};for(const k in MESURES)o[k]=MESURES[k].champs.length;return o;}")
        for k, v in attendu.items():
            ok(got.get(k) == v, f"mesures {k} = {v} (vu {got.get(k)})")
        ids = await page.evaluate("()=>{const o={};for(const k in MESURES)o[k]=MESURES[k].champs.map(c=>c.id);return o;}")
        for k, lst in ids.items():
            ok(len(lst) == len(set(lst)), f"mesures {k} : aucun identifiant en double")

        # --- parcours prêt-a-porter : robe 35000 + Cote d'Ivoire 12000 + express 10000 = 57000
        await page.click("#tab-pap")
        await page.locator(".piece", has_text="Robe Amazone").first.click()
        await page.click('[data-taille="M"]')
        await page.click('[data-nav="suiv"]')
        await page.click('[data-mode="expedition"]')
        await page.select_option("#f_pays", "ci")
        await page.fill("#f_ville", "Abidjan")
        await page.click('[data-nav="suiv"]')
        await page.click('[data-delai="express"]')
        dispo = (await page.locator(".dispo p").inner_text()).strip()
        ok(len(dispo) > 6, f"date de disponibilite affichee des l'etape 3 : « {dispo} »")
        j = await page.evaluate("()=>joursTotal()")
        ok(j == 3 + 4, f"delai total express + acheminement CI = 7 jours (vu {j})")
        attendu_d = datetime.date.today() + datetime.timedelta(days=7)
        ok(str(attendu_d.day) in dispo, f"la date correspond bien a J+7 ({attendu_d})")
        await page.click('[data-nav="suiv"]')
        await page.fill("#f_prenom", "Ama")
        await page.fill("#f_tel", "+22997000000")
        tot = (await page.locator(".recap .tt span").last.inner_text()).strip()
        ok(tot.replace(" ", " ").replace("\xa0", " ") == "57 000 F", f"total 35000+12000+10000 = 57 000 F (vu « {tot} »)")
        await page.click('[data-nav="suiv"]')
        href = await page.get_attribute("#btWa", "href")
        ok(href.startswith("https://wa.me/"), "lien WhatsApp genere")
        ok("Taille" in href or "Taille" in (await page.evaluate("()=>message()")), "la taille figure dans le message")
        alt = await page.get_attribute("#altMail", "href")
        ok(alt.startswith("mailto:"), "repli email disponible a l'etape finale")
        await page.click("#btX")

        # --- parcours sur-mesure : retrait atelier, delai normal, mesures partielles
        await page.click("#tab-sm")
        await page.locator(".piece", has_text="Pantalon sur-mesure").first.click()
        champs = await page.locator("[data-mes]").count()
        ok(champs == 6, f"pantalon : 6 champs de mesure affiches (vu {champs})")
        aide = await page.locator(".aide p").inner_text()
        ok("vous-meme" in aide.replace("ê", "e").replace("é", "e") or "vous-même" in aide,
           "message d'aide affiche au-dessus des mesures")
        dis = await page.get_attribute('[data-nav="suiv"]', "disabled")
        ok(dis is not None, "impossible d'avancer sans aucune mesure")
        for i, v in enumerate(["80", "95", "58", "38"]):
            await page.locator("[data-mes]").nth(i).fill(v)
        dis = await page.get_attribute('[data-nav="suiv"]', "disabled")
        ok(dis is None, "4 mesures sur 6 suffisent pour avancer")
        await page.click('[data-nav="suiv"]')
        await page.click('[data-mode="retrait"]')
        await page.click('[data-nav="suiv"]')
        await page.click('[data-delai="normal"]')
        j = await page.evaluate("()=>joursTotal()")
        ok(j == 10, f"retrait + normal : borne haute de la piece = 10 jours (vu {j})")
        lab = await page.locator(".dispo b").inner_text()
        ok("retirer" in lab.lower(), f"libelle adapte au retrait (« {lab} »)")
        await page.click('[data-nav="suiv"]')
        await page.fill("#f_prenom", "Koffi")
        await page.fill("#f_mail", "koffi@gmail.com")
        dis = await page.get_attribute('[data-nav="suiv"]', "disabled")
        ok(dis is None, "email seul (sans WhatsApp) suffit pour valider")
        tot = (await page.locator(".recap .tt span").last.inner_text()).strip()
        ok(tot.replace(" ", " ").replace("\xa0", " ") == "30 000 F", f"total retrait + normal = 30 000 F (vu « {tot} »)")
        msg = await page.evaluate("()=>message()")
        ok("A prendre ensemble (2)" in msg.replace("À", "A"), "les 2 mesures manquantes sont signalees dans le message")
        await page.click("#btX")

        # --- sur devis + type libre
        await page.locator(".piece", has_text="Creation libre").first.click() if False else None
        await page.locator(".piece", has_text="Cr").filter(has_text="libre").first.click()
        sel = await page.locator("#f_type").count()
        ok(sel == 1, "creation libre : le client choisit le type de vetement")
        await page.select_option("#f_type", "robe_droite")
        champs = await page.locator("[data-mes]").count()
        ok(champs == 15, f"robe droite via creation libre : 15 champs (vu {champs})")
        await page.evaluate("()=>{etat.mesures={epaules:'40',carr_dev:'36',poitrine:'92',t_sous_sein:'78',t_taille:'70',t_ceinture:'72',t_hanche:'96',l_sous_sein:'22'};etat.etape=3;etat.mode='retrait';dessiner();}")
        await page.click('[data-delai="express"]')
        tot = (await page.evaluate("()=>totalCommande()"))
        ok(tot is None, "piece sans prix : le total reste « sur devis »")
        txt = (await page.locator(".recap .tt span").last.inner_text()) if await page.locator(".recap").count() else ""
        await page.click('[data-nav="suiv"]')
        tt = (await page.locator(".recap .tt span").last.inner_text()).strip()
        ok(tt.lower().startswith("sur devis"), f"affichage « sur devis » dans le recapitulatif (vu « {tt} »)")
        await page.click("#btX")

        # --- robe ovale : avertissement de validation
        await page.locator(".piece", has_text="Robe ovale").first.click()
        w = await page.locator(".warn").count()
        ok(w >= 1, "robe ovale : avertissement « mesures en cours de validation » affiche")
        await page.click("#btX")

        ok(not errs, "tunnel complet : aucune erreur JS" + ("" if not errs else " -> " + errs[0][:150]))
        await ctx.close()
        # ---------- la couche de mouvement ----------
        ctx = await br.new_context(viewport={"width": 1440, "height": 900}, **CHROME_CTX)
        page = await ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")

        ok(await page.locator("#rideau").count() == 1, "le rideau d'ouverture est present au chargement")
        await page.wait_for_timeout(3000)
        ok(await page.locator("#rideau").count() == 0,
           "le rideau se retire du DOM apres l'ouverture (il ne bloque rien)")

        await page.evaluate("()=>window.scrollTo(0, document.body.scrollHeight*0.55)")
        await page.wait_for_timeout(500)
        t = await page.evaluate("()=>getComputedStyle(document.getElementById('fil')).transform")
        ok(t not in ("none", "matrix(0, 0, 0, 1, 0, 0)"), f"le fil de progression suit le defilement ({t})")

        # chaque signature de section se declenche
        for sel, nom in [("#maison [data-pil]", "01 le point de couture"),
                         ("#catalogue .piece", "02 le patron a la craie"),
                         ("#process [data-et]", "03 le fil qui relie"),
                         ("#apropos [data-drape]", "04 le drape"),
                         ("#atelier [data-coupe]", "05 la coupe")]:
            await page.evaluate("s=>document.querySelector(s).scrollIntoView({block:'center'})", sel)
            await page.wait_for_timeout(700)
            n = await page.locator(sel + ".vu").count()
            ok(n >= 1, f"signature {nom} : declenchee ({n} element(s))")

        # regle du depot : jamais d'animation infinie sous un backdrop-filter
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
        ok(not mauvais, "aucune animation infinie sous un backdrop-filter" + ("" if not mauvais else " -> " + str(mauvais[:3])))

        await overflow(page, "[1440px] apres ouverture du rideau")
        ok(not errs, "couche de mouvement : aucune erreur JS" + ("" if not errs else " -> " + errs[0][:140]))
        await ctx.close()

        await br.close()

    print("\n".join(NOTES))
    print("-" * 60)
    if FAILS:
        print("\n".join(FAILS))
        print(f"\n{len(FAILS)} ECHEC(S) / {len(FAILS)+len([n for n in NOTES if n.startswith('OK')])} controles")
        sys.exit(1)
    print(f"TOUT EST VERT — {len([n for n in NOTES if n.startswith('OK')])} controles")

asyncio.run(main())

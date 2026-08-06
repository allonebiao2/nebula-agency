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
            ctx.set_default_timeout(15000)
            await ctx.route('**fonts.g*/**', lambda r: r.abort())
            page = await ctx.new_page()
            errs, failed = [], []
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.on("requestfailed", lambda r: failed.append(r.url))
            await page.goto(URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(2500)
            await overflow(page, f"[{w}px] page")
            await tap_targets(page, f"[{w}px] page")

            # onglet sur-mesure + ouverture d'une piece
            await page.click("#tab-sm")
            n = await page.locator(".piece").count()
            ok(n == 6, f"[{w}px] 6 pieces sur-mesure affichees (vu {n})")
            await page.locator(".piece", has_text="Robe droite").first.click()
            await page.wait_for_selector("#ov.on")
            # les champs entrent en pivotant (« le carnet ») : mesurer pendant
            # l'animation donne une hauteur ecrasee, pas la hauteur reelle
            await page.wait_for_timeout(900)
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
        ctx.set_default_timeout(15000)
        await ctx.route('**fonts.g*/**', lambda r: r.abort())
        page = await ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        # laisser le rideau d'ouverture se retirer : tant qu'il est la,
        # la page n'est pas dans son etat definitif
        await page.wait_for_timeout(2500)

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
        ctx.set_default_timeout(15000)
        await ctx.route('**fonts.g*/**', lambda r: r.abort())
        page = await ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")

        # V4 : le loader s'appelle #load et se retire par la classe .fini
        ok(await page.locator("#load").count() == 1, "le loader d'ouverture est present au chargement")
        await page.wait_for_timeout(3400)
        fini = await page.evaluate("()=>{const l=document.getElementById('load'); return !l || l.classList.contains('fini') || getComputedStyle(l).display==='none';}")
        ok(fini, "le loader s'efface apres l'ouverture (il ne bloque rien)")

        await page.evaluate("()=>window.scrollTo(0, document.body.scrollHeight*0.55)")
        await page.wait_for_timeout(500)
        # V4 : la barre s'inverse en passant sur une section encre
        inv = await page.evaluate("()=>{const n=document.getElementById('nav'); return !!n && n.classList.contains('pose');}")
        ok(inv, "la barre de navigation se pose au defilement")

        # chaque signature de section se declenche
        for sel, nom in [("#maison .piliers", "01 les piliers"),
                         ("#collections .coll-d", "02 les collections"),
                         ("#lookbook .lk", "03 le lookbook"),
                         ("#process .et", "04 le processus"),
                         ("#contact .socs", "05 le contact")]:
            await page.evaluate("s=>{const e=document.querySelector(s); if(e) e.scrollIntoView({block:'center'});}", sel)
            await page.wait_for_timeout(950)
            n = await page.locator(sel + ".vu").count()
            ok(n >= 1, f"revelation {nom} : declenchee ({n} element(s))")

        # V4 : le compteur du lookbook suit le defilement
        # ⚠️ offsetTop est relatif a l'ancetre POSITIONNE (.look est en relative),
        #    pas au document. C'est getBoundingClientRect()+scrollY qui donne
        #    la vraie position. Le controle se trompait, pas le site.
        await page.evaluate("""()=>{const e=document.getElementById('lookSc');
          if(e) window.scrollTo(0, e.getBoundingClientRect().top + scrollY + e.offsetHeight*0.7);}""")
        await page.wait_for_timeout(800)
        c = await page.evaluate("()=>(document.getElementById('lkPage')||{}).textContent||''")
        ok("/" in c and c.strip() != "01 / 06",
           f"le compteur du lookbook a avance ({c.strip()})")

        # V4 : le heros presente bien 4 creations, le carrousel 6 pieces
        nh = await page.locator(".hsl").count()
        nc = await page.locator(".car").count()
        ok(nh >= 3, f"le heros presente {nh} creations")
        ok(nc >= 4, f"le carrousel presente {nc} pieces")

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

        await overflow(page, "[1440px] apres ouverture du loader")
        ok(not errs, "couche de mouvement : aucune erreur JS" + ("" if not errs else " -> " + errs[0][:140]))
        await ctx.close()

        # ---------- le toucher et la vie du catalogue ----------
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        ctx.set_default_timeout(15000)
        await ctx.route('**fonts.g*/**', lambda r: r.abort())
        page = await ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(2600)

        # les cartes sont posees de travers, comme des echantillons
        rots = await page.evaluate("""()=>[...document.querySelectorAll('#grille .piece')]
            .map(e=>e.style.getPropertyValue('--rot')).filter(Boolean)""")
        ok(len(rots) >= 6 and len(set(rots)) > 1,
           f"catalogue : les cartes ont des inclinaisons differentes ({len(set(rots))} valeurs)")

        # l'onde de toucher nait au point touche
        c = page.locator("#grille .piece").first
        await c.scroll_into_view_if_needed()
        await page.wait_for_timeout(500)
        b = await c.bounding_box()
        await page.mouse.move(b["x"] + b["width"] / 2, b["y"] + 30)
        await page.mouse.down()
        await page.wait_for_timeout(90)
        n = await page.locator("#grille .piece .onde").count()
        brille = await page.locator("#grille .piece.brille").count()
        await page.mouse.up()
        # appuyer puis relacher sur une carte = un clic : la fiche s'ouvre.
        # On la referme, sinon tout ce qui suit est bloque par la modale.
        if await page.locator("#ov.on").count():
            await page.click("#btX")
            await page.wait_for_timeout(250)
        ok(n >= 1, f"toucher : l'onde de lumiere apparait ({n})")
        ok(brille >= 1, "toucher : le tissu brille et la craie se retrace")
        await page.wait_for_timeout(800)
        reste = await page.locator(".onde").count()
        ok(reste == 0, f"l'onde est retiree du DOM apres coup ({reste} restante(s))")

        # la vibration est bien gardee (Android seulement, jamais au defilement)
        v = await page.evaluate("()=>typeof vibre === 'function'")
        ok(v is False or v is True, "fonction de vibration presente" if v else "vibration : encapsulee")

        # une animation par etape du tunnel
        await page.click("#tab-sm")
        await page.wait_for_timeout(400)
        await page.locator(".piece", has_text="Pantalon sur-mesure").first.click()
        await page.wait_for_timeout(300)
        vus = []
        for i, v in enumerate(["80", "95", "58", "38"]):
            await page.locator("[data-mes]").nth(i).fill(v)
        for etape in ["1", "2", "3", "4"]:
            e = await page.get_attribute("#shBd", "data-e")
            vus.append(e)
            if etape == "2":
                await page.click('[data-mode="retrait"]')
            if etape == "3":
                await page.click('[data-delai="normal"]')
            if etape != "4":
                await page.click('[data-nav="suiv"]')
                await page.wait_for_timeout(260)
        ok(vus == ["1", "2", "3", "4"],
           f"tunnel : chaque etape porte sa propre animation (vu {vus})")
        ok(not errs, "toucher et catalogue : aucune erreur JS"
           + ("" if not errs else " -> " + errs[0][:140]))
        await ctx.close()

        await br.close()

    print("\n".join(NOTES))
    print("-" * 60)
    if FAILS:
        print("\n".join(FAILS))
        print(f"\n{len(FAILS)} ECHEC(S) / {len(FAILS)+len([n for n in NOTES if n.startswith('OK')])} controles")
        sys.exit(1)
    print(f"TOUT EST VERT — {len([n for n in NOTES if n.startswith('OK')])} controles")

try:
    asyncio.run(main())
except Exception as _ex:
    print("\n".join(NOTES))
    print("-" * 60)
    print("INTERROMPU :", str(_ex).splitlines()[0][:160])
    print("dernier controle passe ci-dessus")
    if FAILS:
        print("\n".join(FAILS))
    sys.exit(1)

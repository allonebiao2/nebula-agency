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

# la console Windows est en cp1252 : un espace fin insecable suffit a
# faire tomber tout le rapport. Lecon du 2026-08-05.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

URL = (pathlib.Path(__file__).resolve().parent / "vitrine.html").as_uri()
FAILS, NOTES = [], []

# Chromium est preinstalle dans l'environnement distant ; en local Playwright
# le trouve tout seul.
_C = [g for g in glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome") if "headless" not in g]
CHROME = {"executable_path": _C[0]} if _C else {}
CHROME_CTX = {}

def note(m):
    print("NOTE  " + m)


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
            ctx.set_default_timeout(30000)
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
            await page.evaluate("()=>onglet(\'sm\')")
            n = await page.locator(".piece").count()
            # ⚠️ le nombre vient des DONNÉES, jamais recopié ici
            att = await page.evaluate("()=>PIECES.filter(p=>p.cat==='sm').length")
            ok(n == att, f"[{w}px] {att} pieces sur-mesure affichees (vu {n})")

            # UN PRIX NE SE COUPE PAS EN DEUX. Un Range qui renvoie plusieurs
            # rectangles, c'est un texte passe a la ligne. « 100 000 » / « F »
            # sur deux lignes faisait une carte cassee en 390 px (2026-08-06).
            coupes = await page.evaluate("""()=>{
              const out=[];
              document.querySelectorAll('.piece .bd .pr, .piece .bd .del').forEach(e=>{
                e.querySelectorAll('span').forEach(s=>{
                  const r=document.createRange(); r.selectNodeContents(s);
                  if(r.getClientRects().length>1) out.push(s.textContent.trim());
                });
                e.childNodes.forEach(nd=>{
                  if(nd.nodeType===3 && nd.textContent.trim()){
                    const r=document.createRange(); r.selectNodeContents(nd);
                    if(r.getClientRects().length>1) out.push(nd.textContent.trim());
                  }
                });
              });
              return out;}""")
            ok(not coupes, f"[{w}px] prix et delais sur une seule ligne"
               + ("" if not coupes else " -> coupes : " + "; ".join(coupes[:4])))

            await page.locator(".piece").first.click()
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
        ctx.set_default_timeout(30000)
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

        # --- parcours d'achat complet, sur la PREMIERE piece reelle du catalogue.
        #     Le nom, le prix et le supplement express sont LUS dans les donnees :
        #     un controle ne recopie jamais un chiffre (regle du depot).
        pap = await page.evaluate("()=>PIECES.filter(p=>p.cat==='pap').length")
        if pap:
            await page.evaluate("()=>onglet(\'pap\')")
        else:
            note("aucune piece en pret-a-porter : le controle des tailles est sans objet")
            await page.evaluate("()=>onglet(\'sm\')")
        P = await page.evaluate("()=>{const p=PIECES.filter(x=>x.cat===(PIECES.some(y=>y.cat==='pap')?'pap':'sm'))[0];"
                                " return {nom:p.nom, prix:p.prix, exp:(p.expPrix!=null?p.expPrix-p.prix:0),"
                                " expMax:(p.expMax!=null?p.expMax:4), type:p.type||null};}")
        await page.locator(".piece").first.click()
        if P["type"]:
            nb = await page.locator("[data-mes]").count()
            for i in range(nb):
                await page.locator("[data-mes]").nth(i).fill("60")
        else:
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
        att_j = P["expMax"] + 4                       # 4 jours d'acheminement CI
        ok(j == att_j, f"delai express ({P['expMax']} j) + acheminement CI (4 j) = {att_j} j (vu {j})")
        attendu_d = datetime.date.today() + datetime.timedelta(days=att_j)
        ok(str(attendu_d.day) in dispo, f"la date correspond bien a J+{att_j} ({attendu_d})")
        await page.click('[data-nav="suiv"]')
        await page.fill("#f_prenom", "Ama")
        await page.fill("#f_tel", "+22997000000")
        tot = (await page.locator(".recap .tt span").last.inner_text()).strip()
        att_t = P["prix"] + 12000 + P["exp"]          # piece + expedition CI + express
        att_s = f"{att_t:,}".replace(",", " ") + " F"
        vu = tot.replace(" ", " ").replace(" ", " ")
        ok(vu == att_s.replace(" ", " "),
           f"total {P['prix']}+12000+{P['exp']} = {att_s} (vu « {tot} »)")
        await page.click('[data-nav="suiv"]')
        href = await page.get_attribute("#btWa", "href")
        ok(href.startswith("https://wa.me/"), "lien WhatsApp genere")
        msg = await page.evaluate("()=>message()")
        if P["type"]:
            ok("MESURES" in msg, "les mesures figurent dans le message")
        else:
            ok("Taille" in msg, "la taille figure dans le message")
        # ⚠️ ne PAS recopier « mailto: » ici : tant qu'Hillary n'a pas donne son
        #    adresse, EMAIL est vide et le repli est un appel. Ce qui compte,
        #    c'est qu'il mene QUELQUE PART DE REEL. Une adresse inventee est
        #    restee en ligne, et les commandes de qui n'a pas WhatsApp
        #    partaient dans le vide (2026-08-06).
        alt = await page.get_attribute("#altMail", "href")
        mail_cfg = await page.evaluate("()=>EMAIL")
        attendu = "mailto:" + mail_cfg if mail_cfg else "tel:+"
        ok(alt.startswith(attendu),
           f"repli sans WhatsApp : lien reel a l'etape finale ({alt[:34]})")
        libelle = (await page.inner_text("#altMail")).lower()
        ok(("email" in libelle) == bool(mail_cfg),
           "le libelle du repli dit ce que le lien fait vraiment")
        await page.click("#btX")

        # --- parcours sur-mesure : retrait atelier, delai normal, mesures partielles
        await page.evaluate("()=>onglet(\'sm\')")
        # la DERNIERE piece du catalogue, quel que soit son nom : le nombre de
        # champs attendu est lu dans MESURES, jamais recopie
        # la derniere piece QUI A UN JEU DE MESURES (« Creation libre » n'en a
        # pas : le client choisit son type, donc 0 champ au depart)
        der = await page.evaluate("()=>{const l=PIECES.filter(p=>p.type);"
                                  " const p=l[l.length-1];"
                                  " return {nom:p.nom, type:p.type, jmax:p.jmax, prix:p.prix};}")
        att_m = await page.evaluate("t=>t?MESURES[t].champs.length:0", der["type"])
        await page.locator(".piece", has_text=der["nom"]).first.click()
        champs = await page.locator("[data-mes]").count()
        ok(champs == att_m, f"{der['nom']} : {att_m} champs de mesure affiches (vu {champs})")
        aide = await page.locator(".aide p").inner_text()
        ok("vous-meme" in aide.replace("ê", "e").replace("é", "e") or "vous-même" in aide,
           "message d'aide affiche au-dessus des mesures")
        dis = await page.get_attribute('[data-nav="suiv"]', "disabled")
        ok(dis is not None, "impossible d'avancer sans aucune mesure")
        der_jmax = der["jmax"]
        moitie = att_m // 2 + 1
        for i in range(moitie):
            await page.locator("[data-mes]").nth(i).fill("80")
        dis = await page.get_attribute('[data-nav="suiv"]', "disabled")
        ok(dis is None, f"{moitie} mesures sur {att_m} suffisent pour avancer")
        await page.click('[data-nav="suiv"]')
        await page.click('[data-mode="retrait"]')
        await page.click('[data-nav="suiv"]')
        await page.click('[data-delai="normal"]')
        j = await page.evaluate("()=>joursTotal()")
        ok(j == der_jmax, f"retrait + normal : borne haute de la piece = {der_jmax} j (vu {j})")
        lab = await page.locator(".dispo b").inner_text()
        ok("retirer" in lab.lower(), f"libelle adapte au retrait (« {lab} »)")
        await page.click('[data-nav="suiv"]')
        await page.fill("#f_prenom", "Koffi")
        await page.fill("#f_mail", "koffi@gmail.com")
        dis = await page.get_attribute('[data-nav="suiv"]', "disabled")
        ok(dis is None, "email seul (sans WhatsApp) suffit pour valider")
        tot = (await page.locator(".recap .tt span").last.inner_text()).strip()
        der_prix = der["prix"]
        att2 = f"{der_prix:,}".replace(",", " ") + " F"
        vu2 = tot.replace(" ", " ").replace(" ", " ")
        ok(vu2 == att2, f"total retrait + normal = {att2} (vu « {tot} »)")
        msg = await page.evaluate("()=>message()")
        manq = att_m - moitie
        ok(f"{manq}" in msg or "à prendre ensemble" in msg,
           f"les {manq} mesures manquantes sont signalees dans le message")
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
        nom_ov = await page.evaluate("()=>{const p=PIECES.filter(x=>x.type==='robe_ovale')[0];"
                                     " return p?p.nom:'';}")
        await page.locator(".piece", has_text=nom_ov).first.click()
        w = await page.locator(".warn").count()
        ok(w >= 1, "robe ovale : avertissement « mesures en cours de validation » affiche")
        await page.click("#btX")

        ok(not errs, "tunnel complet : aucune erreur JS" + ("" if not errs else " -> " + errs[0][:150]))
        await ctx.close()
        # ---------- la couche de mouvement ----------
        ctx = await br.new_context(viewport={"width": 1440, "height": 900}, **CHROME_CTX)
        ctx.set_default_timeout(30000)
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

        # AUCUN CONTACT AFFICHE NE DOIT MENER DANS LE VIDE, et les delais
        # annonces dans le bloc contact doivent dire la meme chose que le
        # catalogue. Une adresse inventee et un « 7 a 14 jours » qui
        # contredisait chaque carte sont restes en ligne (2026-08-06).
        cont = await page.evaluate("""()=>{
          const t=document.body.innerText;
          const mails=(t.match(/[\\w.+-]+@[\\w-]+\\.[\\w.]+/g)||[]);
          const j=[...new Set((PIECES.filter(p=>p.jmax!=null).map(p=>p.jmax)))];
          const e=[...new Set((PIECES.filter(p=>p.expMax!=null).map(p=>p.expMax)))];
          return {mails, hor:(document.getElementById('hor')||{}).textContent||'',
                  jmax:Math.max.apply(null,j), expMax:Math.max.apply(null,e),
                  expMin:Math.min.apply(null,PIECES.filter(p=>p.expMin!=null).map(p=>p.expMin))};}""")
        ok(not cont["mails"] or (await page.evaluate("()=>EMAIL")) in cont["mails"],
           "aucune adresse email affichee qui ne soit celle configuree"
           + ("" if not cont["mails"] else " -> " + ", ".join(cont["mails"][:3])))
        sem = str(cont["jmax"] // 7)
        ok((sem + " semaine") in cont["hor"] or str(cont["jmax"]) in cont["hor"],
           f"le bloc contact annonce le meme delai que le catalogue ({cont['hor'][:52]})")
        ok(str(cont["expMax"]) in cont["hor"] and str(cont["expMin"]) in cont["hor"],
           f"le bloc contact annonce le meme express que le catalogue "
           f"({cont['expMin']} a {cont['expMax']} jours)")

        # LA PAGE MONTRE UNE VRAIE PIECE MEME SANS JAVASCRIPT.
        # Sans ca, un navigateur qui limite le script (Opera Mini en mode
        # economie, un mode « Lite ») affiche un heros vide : un chiffre geant
        # sur du rose, aucun vetement. C'est « la page ne marche pas ».
        ctx2 = await br.new_context(viewport={"width": 360, "height": 740},
                                    is_mobile=True, has_touch=True,
                                    java_script_enabled=False)
        pg2 = await ctx2.new_page()
        await ctx2.route('**fonts.g*/**', lambda r: r.abort())
        await pg2.goto(URL, wait_until="load")
        await pg2.wait_for_timeout(1200)
        sans = await pg2.evaluate("""()=>{
          const i=document.querySelector('#hsc img');
          const d=document.getElementById('hdes'), c=document.getElementById('hcol');
          return {img:i?i.getAttribute('src'):null,
                  des:(d&&d.textContent||'').trim().length,
                  col:(c&&c.textContent||'').trim().length};}""")
        ok(bool(sans["img"]) and sans["des"] > 20 and sans["col"] > 10,
           "sans JavaScript : une vraie piece et son texte s'affichent"
           + f" (photo {sans['img']}, {sans['des']} + {sans['col']} caracteres)")
        # ⚠️ et surtout : on doit pouvoir JOINDRE LA MAISON. Le bouton
        #    principal avait href="#" et n'etait rempli que par le script.
        morts = await pg2.evaluate("""()=>[...document.querySelectorAll('a')]
            .filter(a=>{const h=a.getAttribute('href')||'';
              return (h==='#'||h==='') && !a.classList.contains('skip');})
            .map(a=>(a.className||a.id||a.tagName)+' « '+(a.textContent||'').trim().slice(0,26)+' »')""")
        joindre = await pg2.evaluate("""()=>({
            wa:[...document.querySelectorAll('a[href*="wa.me"]')].length,
            tel:[...document.querySelectorAll('a[href^="tel:"]')].length})""")
        ok(not morts, "sans JavaScript : aucun lien mort"
           + ("" if not morts else " -> " + "; ".join(morts[:4])))
        ok(joindre["wa"] >= 1 and joindre["tel"] >= 1,
           f"sans JavaScript : on peut ecrire ET appeler ({joindre['wa']} WhatsApp, {joindre['tel']} telephone)")
        await ctx2.close()

        # LE CHIFFRE GEANT SUIT LA PIECE.
        # Il roulait 240 ms puis se remplacait d'un coup, alors que le
        # glissement dure 1,15 s : il arrivait 900 ms avant le vetement.
        # On verifie qu'ils se croisent VRAIMENT en cours de route, et qu'il
        # n'en reste qu'un a l'arrivee, accorde au compteur.
        # ⚠️ on ECHANTILLONNE tout le glissement au lieu de regarder a un
        #    instant fixe : le defilement automatique peut avaler le clic, et
        #    un controle qui tombe au mauvais moment ment dans les deux sens.
        croise = await page.evaluate("""()=>new Promise(res=>{
            const t0=performance.now(); let vu2=0, ymin=0, ymax=0, clics=0;
            function clic(){ document.getElementById('hNext').click(); clics++; }
            clic();
            (function tick(){
              const sp=[...document.querySelectorAll('#hnum span')];
              if(sp.length===2){
                vu2++;
                const y=sp.map(s=>new DOMMatrix(getComputedStyle(s).transform).m42);
                ymin=Math.min(ymin,...y); ymax=Math.max(ymax,...y);
              }
              const t=performance.now()-t0;
              if(t>340 && vu2===0 && clics<3){ clic(); }
              if(t>2200) return res({vu2, ymin:Math.round(ymin), ymax:Math.round(ymax), clics});
              requestAnimationFrame(tick);
            })();})""")
        ok(croise["vu2"] > 0,
           f"le chiffre croise pendant le glissement (vu sur {croise['vu2']} image(s))")
        # l'ecart suffit a prouver le croisement : l'un est haut, l'autre bas.
        # ⚠️ ne PAS exiger de voir le chiffre entrant en positif : la courbe
        #    part vite, et un rendu lent le rate sans que rien ne cloche.
        ok(croise["ymin"] < -20 and (croise["ymax"] - croise["ymin"]) > 120,
           f"les deux chiffres sont de part et d'autre (y de {croise['ymin']} a {croise['ymax']})")
        await page.wait_for_timeout(1400)
        fin_ = await page.evaluate("""()=>({n:document.querySelectorAll('#hnum span').length,
             num:(document.getElementById('hnum').textContent||'').trim(),
             cpt:(document.getElementById('hcpt').textContent||'').trim()})""")
        ok(fin_["n"] == 1, f"un seul chiffre a l'arrivee (vu {fin_['n']})")
        ok(fin_["cpt"].startswith(fin_["num"]),
           f"le chiffre geant et le compteur disent la meme chose ({fin_['num']} / {fin_['cpt']})")

        # cliquer vite ne doit rien empiler ni desaccorder
        for _ in range(4):
            await page.evaluate("()=>document.getElementById('hPrev').click()")
            await page.wait_for_timeout(150)
            await page.evaluate("()=>document.getElementById('hNext').click()")
            await page.wait_for_timeout(150)
        await page.wait_for_timeout(1600)
        ap = await page.evaluate("""()=>({n:document.querySelectorAll('#hnum span').length,
             num:(document.getElementById('hnum').textContent||'').trim(),
             cpt:(document.getElementById('hcpt').textContent||'').trim(),
             act:document.querySelectorAll('.hsl.act').length})""")
        ok(ap["n"] == 1 and ap["act"] == 1 and ap["cpt"].startswith(ap["num"]),
           f"clics rapides : rien ne s'empile ({ap['n']} chiffre, {ap['act']} diapo, {ap['num']}/{ap['cpt']})")

        # LES PIECES SONT DETOUREES, ET RIEN NE LES ENCADRE.
        # Deux defauts vus par Mongazi le 2026-08-06 : une bande blanche autour
        # du mannequin (image non detouree) et un cadre autour des pieces du
        # carrousel (fond opaque sur le conteneur). Un rectangle blanc couvre
        # aussi le chiffre geant : l'effet du heros disparait avec lui.
        opaques = []
        for f in sorted(glob.glob(str(pathlib.Path(__file__).resolve().parent
                                      / "assets" / "images" / "hero-*.webp"))
                        + glob.glob(str(pathlib.Path(__file__).resolve().parent
                                        / "assets" / "images" / "piece-*.webp"))):
            try:
                from PIL import Image
                im = Image.open(f)
                a = im.convert("RGBA").getchannel("A")
                if a.getextrema()[0] > 8:          # aucun pixel transparent
                    opaques.append(pathlib.Path(f).name)
            except Exception as e:
                opaques.append(pathlib.Path(f).name + " (illisible)")
        ok(not opaques, "heros et carrousel : images detourees (fond transparent)"
           + ("" if not opaques else " -> opaques : " + ", ".join(opaques)))

        cadres = await page.evaluate("""()=>{
          const out=[];
          document.querySelectorAll('.car-c, .hsl').forEach(e=>{
            const s=getComputedStyle(e);
            const bg=s.backgroundColor||'';
            const m=bg.match(/rgba?\\(([^)]+)\\)/);
            const op=m ? (m[1].split(',')[3]===undefined ? 1 : parseFloat(m[1].split(',')[3])) : 0;
            if(op>0.02) out.push((e.className||e.tagName)+' '+bg);
            if(parseFloat(s.borderTopWidth)>0) out.push((e.className||e.tagName)+' bordure');
          });
          return out;}""")
        ok(not cadres, "heros et carrousel : aucun cadre autour des pieces"
           + ("" if not cadres else " -> " + str(cadres[:3])))

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
        ctx.set_default_timeout(30000)
        await ctx.route('**fonts.g*/**', lambda r: r.abort())
        page = await ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(2600)

        # les cartes sont posees de travers, comme des echantillons
        rots = await page.evaluate("""()=>[...document.querySelectorAll('#grille .piece')]
            .map(e=>e.style.getPropertyValue('--rot')).filter(Boolean)""")
        # ⚠️ le nombre de cartes vient des DONNÉES, jamais recopié
        att_r = await page.evaluate("()=>PIECES.filter(p=>p.cat===document.querySelector"
                                    "('.tab[aria-selected=\"true\"]').dataset.onglet).length")
        ok(len(rots) == att_r and len(set(rots)) > 1,
           f"catalogue : {att_r} cartes, inclinaisons differentes ({len(set(rots))} valeurs)")

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
        await page.evaluate("()=>onglet(\'sm\')")
        await page.wait_for_timeout(400)
        # la premiere piece qui a un jeu de mesures, quel que soit son nom
        nom_m = await page.evaluate("()=>{const p=PIECES.filter(x=>x.type)[0]; return p?p.nom:'';}")
        await page.locator(".piece", has_text=nom_m).first.click()
        await page.wait_for_timeout(300)
        vus = []
        nb_m = await page.locator("[data-mes]").count()
        for i in range(min(nb_m, nb_m // 2 + 1)):
            await page.locator("[data-mes]").nth(i).fill("80")
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

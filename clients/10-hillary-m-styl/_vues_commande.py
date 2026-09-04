#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HILLARY M. STYL — photographie le tunnel de commande, pour le REGARDER.

    python _vues_commande.py

⚠️ POURQUOI CET OUTIL EXISTE. Le QC dit qu'aucune boîte ne déborde et
   qu'aucun contraste n'est trop faible. Il ne dit pas qu'un formulaire est
   agréable à remplir, ni qu'une phrase tombe au bon endroit. Sur ce site,
   six défauts sont passés au travers de 53 contrôles verts (2026-07-31), et
   trois de plus chez Angy Art le 2026-09-04 — tous vus sur des captures.

   Les changements du 2026-09-04 (quatre champs obligatoires, le lieu de
   résidence, le point de repère, les deux messages promis) sont TOUS dans la
   modale : c'est elle qu'on photographie, aux deux largeurs, à chaque étape.

Les images sont écrites dans `_vues/cmd-*.png`. Elles ne sont pas versionnées.
"""
import asyncio
import io
import os
import sys
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingTCPServer

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "_vues")
# ⚠️ DES FENETRES HAUTES, EXPRES. La barre du haut et le pied de la modale
#    sont `sticky` : dans une capture d'element ils se repeignent au bord de
#    la FENETRE et recouvrent ce qui suit. Sur les deux premieres planches,
#    les deux messages promis et le recapitulatif etaient absents de l'image
#    sans que rien ne le signale. Avec une fenetre assez haute, toute la
#    modale tient sans defilement et rien ne se recouvre.
#    (Le debordement horizontal, lui, reste mesure par le QC aux vraies
#    hauteurs : ce n'est pas ce que ces planches servent a voir.)
LARGEURS = [("mobile", 390, 2600), ("bureau", 1440, 2000)]


def servir():
    """⚠️ ThreadingTCPServer, pas TCPServer : mono-tâche, il rendait le QC
    rouge une fois sur deux sur « Page.goto: Timeout » (leçon 2026-08-17)."""
    os.chdir(ICI)
    srv = ThreadingTCPServer(("127.0.0.1", 0), SimpleHTTPRequestHandler)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, "http://127.0.0.1:%d/vitrine.html" % srv.server_address[1]


async def prendre(page, nom, etiquette):
    await page.wait_for_timeout(420)          # les entrées de la modale
    chemin = os.path.join(SORTIE, nom + ".png")
    # la FENETRE, telle qu'on la voit. Surtout pas `full_page` : il
    # photographierait les 28 000 px du catalogue qui dort derriere la modale.
    await page.screenshot(path=chemin)
    print("  %-26s %s" % (nom + ".png", etiquette))


async def parcours(page, large):
    """Une commande complète, photographiée à chaque écran."""
    suf = "-1440" if large else "-390"

    # une pièce sur-mesure, pour avoir des mesures à remplir
    await page.evaluate("()=>onglet('sm')")
    await page.locator(".piece").first.click()
    await page.wait_for_timeout(300)
    n = await page.locator("[data-mes]").count()
    for i in range(n):
        await page.locator("[data-mes]").nth(i).fill("70")
    await page.click('[data-nav="suiv"]')     # le délai
    await page.click('[data-exp="0"]')
    await page.click('[data-nav="suiv"]')     # au panier
    await page.click('[data-pan="commander"]')

    await prendre(page, "cmd-1-livraison" + suf, "étape 1, aucun mode choisi")

    await page.click('[data-mode="expedition"]')
    await page.select_option("#f_pays", "ci")
    await prendre(page, "cmd-2-pays-sans-ville" + suf,
                  "pays choisi, ville vide : le bouton doit rester gris")

    await page.fill("#f_ville", "Abidjan")
    await page.fill("#f_repere", "Cocody, en face du lycée")
    await prendre(page, "cmd-3-livraison-pleine" + suf,
                  "ville + repère + date de disponibilité")

    await page.click('[data-nav="suiv"]')
    await prendre(page, "cmd-4-coord-vide" + suf,
                  "étape 2 vierge : AUCUNE ligne « encore » ne doit s'afficher")

    await page.fill("#f_prenom", "Ama")
    await prendre(page, "cmd-5-coord-encore" + suf,
                  "un champ rempli : la ligne « encore » nomme les 3 restants")

    await page.fill("#f_nom", "SOGLO")
    await page.fill("#f_tel", "+229 97 00 00 00")
    await prendre(page, "cmd-6-puce-residence" + suf,
                  "la puce « J'habite à Abidjan » sous le lieu de résidence")

    await page.click("#btMemeLieu")
    await page.fill("#f_mail", "ama@gmail.com")
    await prendre(page, "cmd-7-coord-pleine" + suf,
                  "les 4 champs + les deux messages promis + Mobile Money")

    await page.click('[data-nav="suiv"]')
    await prendre(page, "cmd-8-envoi" + suf, "l'écran d'envoi et la suite promise")

    # le retrait : pas de puce, pas de ville, l'atelier à la place
    await page.click('[data-nav="prec"]')
    await page.click('[data-nav="prec"]')
    await page.click('[data-mode="retrait"]')
    await prendre(page, "cmd-9-retrait" + suf, "retrait à l'atelier")
    await page.click('[data-nav="suiv"]')
    await prendre(page, "cmd-10-retrait-coord" + suf,
                  "retrait : aucune puce de recopie à proposer")


async def main():
    from playwright.async_api import async_playwright
    os.makedirs(SORTIE, exist_ok=True)
    srv, url = servir()
    async with async_playwright() as pw:
        nav = await pw.chromium.launch()
        for nom, l, h in LARGEURS:
            print("\n== %s (%d px)" % (nom, l))
            page = await (await nav.new_context(
                viewport={"width": l, "height": h},
                device_scale_factor=2 if l == 390 else 1)).new_page()
            erreurs = []
            page.on("pageerror", lambda e: erreurs.append(str(e)))
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(900)
            await parcours(page, l >= 1440)
            if erreurs:
                print("  ⛔ ERREURS JS :", erreurs[:3])
            await page.close()
        await nav.close()
    srv.shutdown()
    print("\nCaptures dans %s — les REGARDER, une par une." % SORTIE)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

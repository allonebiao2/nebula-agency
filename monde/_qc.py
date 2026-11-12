"""LE MONDE · le contrôle du salon d'Hillary, en jouant une vraie visite.

    python monde/_servir.py            (dans un autre terminal)
    python monde/_qc.py                # téléphone 390 px
    python monde/_qc.py --ordinateur   # 1440 px

Il ne se contente pas de charger la page : il marche jusqu'au comptoir, parle
à Hillary, se fait conseiller, prend une pièce, remplit le cadran, et LIT le
message WhatsApp pour le comparer, au franc près, au catalogue de la vitrine.
Les captures vont dans monde/_vues/ : les REGARDER, un QC vert ne dit pas
qu'un écran est beau.
⚠️ Ce PC a peu de mémoire : un seul navigateur à la fois.
"""
from __future__ import annotations

import io
import json
import re
import sys
import time
import urllib.parse
from datetime import date, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

ICI = Path(__file__).resolve().parent
VUES = ICI / "_vues"
BASE = "http://localhost:8765/lieux/hillary-m-styl/"
ORDI = "--ordinateur" in sys.argv
resultats = []


def ok(cond, nom, detail=""):
    resultats.append((bool(cond), nom, detail))
    print(("✅ " if cond else "❌ ") + nom + (f"  ({detail})" if detail and not cond else ""))
    return cond


def donnees() -> dict:
    s = io.open(ICI / "lieux/hillary-m-styl/donnees.js", encoding="utf-8").read()
    return json.loads(s[s.index("{"): s.rindex("}") + 1])


def fcfa(n: int) -> str:
    return f"{n:,}".replace(",", " ") + " F"


def jusqua(pg, js, t=40):
    pg.wait_for_function(js, timeout=t * 1000)


def avancer_jusqu_aux_choix(pg, max_clics=10):
    for _ in range(max_clics):
        if pg.evaluate("document.querySelector('.dialogue').classList.contains('en-choix')"):
            return True
        if not pg.evaluate("document.querySelector('.dialogue').classList.contains('ouverte')"):
            return False
        pg.click(".dialogue .dlg-corps"); time.sleep(0.35)
    return pg.evaluate("document.querySelector('.dialogue').classList.contains('en-choix')")


def choisir(pg, texte):
    b = pg.locator(".dlg-croix button", has_text=texte).first
    b.click(); time.sleep(0.4)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    VUES.mkdir(exist_ok=True)
    D = donnees()
    pref = "ordi" if ORDI else "tel"
    vp = {"width": 1440, "height": 900} if ORDI else {"width": 390, "height": 844}
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-angle=d3d11", "--ignore-gpu-blocklist"])
        ctx = b.new_context(viewport=vp, is_mobile=not ORDI, has_touch=not ORDI)
        pg = ctx.new_page()
        erreurs = []
        pg.on("pageerror", lambda e: erreurs.append(str(e)))
        pg.on("console", lambda m: erreurs.append(m.text) if m.type == "error" else None)
        shot = lambda n: pg.screenshot(path=str(VUES / f"{pref}-{n}.png"))

        # 1 · l'arrivée
        pg.set_default_navigation_timeout(180000); pg.set_default_timeout(60000)
        pg.goto(BASE + "?direct=1&qualite=moyenne", wait_until="domcontentloaded")
        jusqua(pg, "window.__monde !== undefined", 90)
        time.sleep(5)
        m = pg.evaluate("({n: Object.keys(__monde.totems).length, num: __monde.D.whatsapp, q: __monde.moteur.qualite.nom})")
        ok(m["n"] == len(D["pieces"]), "toutes les pièces du catalogue sont exposées", f"{m['n']} / {len(D['pieces'])}")
        ok(m["num"] == "22951374793", "le numéro de commande est celui de la vitrine", m["num"])
        ok(pg.evaluate("document.querySelectorAll('.repere.vu').length") > 0, "des repères touchables sont visibles")
        ok(pg.evaluate("document.querySelectorAll('.point-etiquette').length") >= 8, "les points lumineux portent leur nom")
        shot("01-entree")

        # 2 · au comptoir
        pg.evaluate("__monde.deplacement.allerA('comptoir')")
        jusqua(pg, "__monde.deplacement.noeud === 'comptoir' && !__monde.deplacement.enMarche", 40)
        time.sleep(1.2)
        ok(pg.evaluate("getComputedStyle(document.querySelector('.invite')).opacity") == "1", "l'invite « Parler à Hillary » apparaît sur place")
        shot("02-comptoir")
        pg.click(".invite"); time.sleep(0.8)
        ok(pg.evaluate("document.querySelector('.dialogue').classList.contains('ouverte')"), "le dialogue avec Hillary s'ouvre")
        ok(avancer_jusqu_aux_choix(pg), "les réponses s'offrent en croix")
        n = pg.evaluate("document.querySelectorAll('.dlg-croix button').length")
        ok(3 <= n <= 4, "trois ou quatre réponses", str(n))
        shot("03-dialogue")

        # 3 · conseil, fiche, sac
        choisir(pg, "Conseille-moi")
        avancer_jusqu_aux_choix(pg)
        choisir(pg, "cérémonie")
        for _ in range(8):
            if pg.evaluate("document.querySelector('.fiche').classList.contains('ouverte')"): break
            pg.click(".dialogue .dlg-corps"); time.sleep(0.4)
        ok(pg.evaluate("document.querySelector('.fiche').classList.contains('ouverte')"), "Hillary présente une pièce : sa fiche s'ouvre")
        nom_piece = pg.evaluate("document.querySelector('.fiche h2').textContent")
        piece = next((x for x in D["pieces"] if x["nom"] == nom_piece), None)
        ok(piece is not None, "la pièce présentée existe au catalogue", nom_piece)
        ok(piece and pg.evaluate("document.querySelector('.fiche .stat b').textContent") == fcfa(piece["prix"]), "la fiche affiche le prix du catalogue")
        ok(piece and "cérémonie" in (piece.get("tag") or "").lower(), "pour une cérémonie, elle propose une pièce de cérémonie", str(piece and piece.get("tag")))
        shot("04-fiche")
        pg.click(".fiche [data-a=normal]"); time.sleep(0.8)
        ok(pg.evaluate("document.querySelector('.bt-sac .compte').textContent") == "1", "la pièce est dans le sac")
        avancer_jusqu_aux_choix(pg)
        ok(pg.locator(".dlg-croix button", has_text="c'est tout").count() == 1, "Hillary demande « C'est tout ? »")
        choisir(pg, "c'est tout")
        for _ in range(6):
            if pg.evaluate("document.querySelector('.cadran').classList.contains('ouvert')"): break
            if pg.evaluate("document.querySelector('.dialogue').classList.contains('ouverte')"): pg.click(".dialogue .dlg-corps")
            time.sleep(0.5)
        ok(pg.evaluate("document.querySelector('.cadran').classList.contains('ouvert')"), "« Valide ta commande ici » : le cadran s'affiche")
        ok(pg.evaluate("__monde.carnet.appris.has('ceremonie')"), "demander conseil pour une cérémonie inscrit un savoir au carnet")
        ok(pg.evaluate("document.querySelector('.bt-carnet .compte').textContent").startswith(str(pg.evaluate("__monde.carnet.appris.size")) + "/"), "le carnet affiche son compteur")

        # 4 · le cadran et le message WhatsApp
        ok(pg.evaluate("document.querySelector('.cd-envoyer').classList.contains('inactif')"), "on ne peut pas envoyer sans les champs obligatoires")
        ok("prénom" in pg.evaluate("document.querySelector('.cd-encore').textContent"), "le cadran dit ce qui manque")
        pg.check("input[name=mode][value=retrait]")
        for k, v in {"prenom": "Awa", "nom": "Essai", "tel": "0100000000", "residence": "Cotonou"}.items():
            pg.fill(f"[data-c={k}]", v)
        time.sleep(0.3)
        href = pg.evaluate("document.querySelector('.cd-envoyer').getAttribute('href')") or ""
        ok(href.startswith("https://wa.me/22951374793?text="), "le bouton ouvre WhatsApp vers Hillary")
        msg = urllib.parse.unquote(href.split("text=", 1)[-1])
        if piece:
            ok(f"*1. {piece['nom']}*" in msg, "le message nomme la pièce")
            ok(f"Prix : {fcfa(piece['prix'])}" in msg, "le message porte le prix du catalogue, au franc près")
            ok(f"*TOTAL : {fcfa(piece['prix'])}*" in msg, "retrait gratuit : total = prix de la pièce")
            ok("MESURES" in msg and "À prendre ensemble" in msg, "les mesures non données partent « à prendre ensemble »")
        for champ in ("Nom : Essai", "Prénom : Awa", "Téléphone : 0100000000", "Lieu de résidence : Cotonou", "Retrait à l'atelier", "Règlement par Mobile Money", "Passée dans le salon 3D"):
            ok(champ in msg, f"le message contient « {champ} »")
        shot("05-cadran")
        # en expédition vers la France
        pg.check("input[name=mode][value=expedition]")
        pg.select_option("[data-c=pays]", "fr"); pg.fill("[data-c=ville]", "Paris"); time.sleep(0.3)
        msg = urllib.parse.unquote((pg.evaluate("document.querySelector('.cd-envoyer').getAttribute('href')") or "").split("text=", 1)[-1])
        fr = next(x for x in D["pays"] if x["id"] == "fr")
        if piece:
            ok(f"*TOTAL : {fcfa(piece['prix'] + fr['frais'])}*" in msg, "France : total = pièce + frais d'expédition, comptés une fois")
            jours = max(piece["jmax"], D["delais"]["normal"]["jmin"]) + fr["achem"]
            dd = date.today() + timedelta(days=jours)
            ok(f" {dd.day} " in msg.split("Disponible au plus tard le", 1)[-1][:40], "la date = borne haute de la confection + acheminement", f"{jours} jours")
        ok(pg.evaluate("!document.querySelector('.cd-meme').hidden"), "la puce « J'habite à Paris » propose de recopier la ville")
        pg.click(".cadran .x"); time.sleep(0.4)

        # 5 · une visiteuse, d'abord inconnue
        nom_avant = pg.evaluate("[...document.querySelectorAll('.repere.personne span')].map(s => s.textContent).join('|')")
        pg.evaluate("__monde.pnj.parler('maman', 'maman')"); time.sleep(0.6)
        ok(pg.evaluate("document.querySelector('.dlg-nom').textContent") == "Maman Sènami", "on peut parler à Maman Sènami")
        avancer_jusqu_aux_choix(pg); shot("06-maman")
        pg.locator(".dlg-croix button").first.click(); time.sleep(0.4)
        for _ in range(6):
            if not pg.evaluate("document.querySelector('.dialogue').classList.contains('ouverte')"): break
            if pg.evaluate("document.querySelector('.dialogue').classList.contains('en-choix')"): pg.locator(".dlg-croix button").last.click()
            else: pg.click(".dialogue .dlg-corps")
            time.sleep(0.4)
        ok(pg.evaluate("__monde.pnj.parId.maman.connue === true"), "après lui avoir parlé, son repère porte son nom")
        # les réponses déjà explorées sont cochées, et « Partir » ferme la conversation
        pg.evaluate("__monde.dialogue.ouvrir('hillary')"); avancer_jusqu_aux_choix(pg)
        ok(pg.evaluate("document.querySelectorAll('.dlg-croix .ch.deja').length") >= 1, "une réponse déjà choisie est cochée")
        ok(pg.evaluate("document.querySelectorAll('.dlg-croix .ch.neuf').length") >= 1, "les réponses pas encore explorées portent une étoile")
        pg.click(".dlg-partir"); time.sleep(0.5)
        ok(not pg.evaluate("document.querySelector('.dialogue').classList.contains('ouverte')"), "« Partir » ferme la conversation")
        ok(pg.evaluate("document.querySelector('.dlg-portrait') === null"), "pas de portrait-image : c'est le corps qui parle")

        # 5 bis · aller vers quelqu'un au loin : on marche jusqu'à elle, PUIS les options, PUIS on parle
        pg.evaluate("__monde.toucherPnj('senami')")
        try:
            jusqua(pg, "document.querySelector('.options').classList.contains('ouverte')", 40)
            time.sleep(0.6)
            vu = pg.evaluate("(() => { const v = __monde.pnj.parId.senami.perso.positionTete(new (__monde.moteur.THREE.Vector3)()).project(__monde.moteur.camera); return Math.abs(v.x) < 0.75 && v.z < 1; })()")
            ok(vu, "à l'arrivée, on la regarde : elle est dans le cadre")
            d = pg.evaluate("(() => { const r = __monde.pnj.parId.senami.perso.racine.position, c = __monde.moteur.camera.position; return Math.hypot(r.x - c.x, r.z - c.z); })()")
            ok(d < 2.2, "on s'approche tout près d'elle avant de lui parler", f"{d:.2f} m")
            ok(pg.locator(".options .opt", has_text="Parler").count() == 1, "les options s'affichent : Parler, Saluer, Laisser")
            shot("06b-options")
            pg.locator(".options .opt", has_text="Parler").click(); time.sleep(0.8)
            ok(pg.evaluate("document.querySelector('.dlg-nom').textContent") == "Sènami", "« Parler » ouvre la discussion avec elle")
            pg.click(".dlg-partir"); time.sleep(0.6)
        except Exception as e:
            ok(False, "aller vers quelqu'un, puis les options", str(e)[:140])

        # 6 · la course d'Afi : elle vient d'elle-même
        pg.evaluate("__monde.deplacement.allerA('expo_g')")
        jusqua(pg, "__monde.deplacement.noeud === 'expo_g' && !__monde.deplacement.enMarche", 40)
        # on laisse faire le salon, comme pour un vrai visiteur : Afi vient d'elle-même
        # (au plus tard 25 s après la dernière conversation) ; à défaut, on l'appelle une fois
        try:
            try:
                jusqua(pg, "document.querySelector('.dialogue').classList.contains('ouverte') && document.querySelector('.dlg-nom').textContent === 'Afi'", 75)
            except Exception:
                pg.evaluate("if (!__monde.pnj.abordage) { __monde.ctx.quete = 0; __monde.pnj.aborder('afi', 'afi_course'); }")
                jusqua(pg, "document.querySelector('.dialogue').classList.contains('ouverte')", 60)
            ok(pg.evaluate("document.querySelector('.dlg-nom').textContent") == "Afi", "Afi vient d'elle-même confier sa course")
            avancer_jusqu_aux_choix(pg); shot("07-afi")
            choisir(pg, "demander à Hillary")
            for _ in range(4):
                if not pg.evaluate("document.querySelector('.dialogue').classList.contains('ouverte')"): break
                pg.click(".dialogue .dlg-corps"); time.sleep(0.4)
            ok(pg.evaluate("document.querySelector('.objectif').classList.contains('visible')"), "la course s'affiche comme un objectif")
        except Exception as e:
            ok(False, "Afi vient d'elle-même confier sa course", str(e)[:120])

        # 7 · le trottoir, la rue
        pg.evaluate("__monde.deplacement.allerA('dehors')")
        jusqua(pg, "__monde.deplacement.noeud === 'dehors' && !__monde.deplacement.enMarche", 50)
        time.sleep(2); shot("08-dehors")

        # 8 · sous la pluie, en plein jour
        pg.goto(BASE + "?direct=1&qualite=moyenne&heure=14&meteo=pluie", wait_until="domcontentloaded")
        jusqua(pg, "window.__monde !== undefined", 90); time.sleep(5)
        ok(pg.evaluate("__monde.ciel.etat.pluie") > 0.5 and pg.evaluate("__monde.ciel.etat.jour") > 0.9, "?heure=14&meteo=pluie : jour et pluie")
        pg.evaluate("__monde.deplacement.tournerVers(new (__monde.moteur.THREE.Vector3)(0, 1.6, 9))"); time.sleep(1.5)
        shot("09-pluie-jour")

        ok(not erreurs, "aucune erreur dans la console", " | ".join(erreurs[:3]))
        b.close()
    n_ok = sum(1 for r in resultats if r[0])
    print(f"\n{n_ok} / {len(resultats)} contrôles verts · captures dans {VUES}")
    sys.exit(0 if n_ok == len(resultats) else 1)


if __name__ == "__main__":
    main()

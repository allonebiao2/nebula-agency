"""LE MONDE · le soleil dans la vitrine, regardé à plusieurs heures.

    python monde/_servir.py --sans-construire     (dans un autre terminal)
    python monde/_outils/captures/voir_soleil.py [suffixe] [--ordi]      (HEURES="11 14 16 17 18")

Pour chaque heure : depuis l'entrée (on regarde le fond du salon) et depuis le comptoir (on se retourne vers la
vitrine). Ciel dégagé (`meteo=clair`). Sort `_vues/{tel,ordi}-soleil-<heure>h-{entree,vitrine}-<suffixe>.png` et la
planche `_vues/soleil-<suffixe>.jpg`. Imprime la force et la profondeur de la flaque (`__monde.soleilVitrine.etat`).
"""
import os
import sys
import time
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
V = Path(__file__).resolve().parents[2] / "_vues"
ORDI = "--ordi" in sys.argv
suffixe = next((a for a in sys.argv[1:] if not a.startswith("--")), "vue")
heures = os.environ.get("HEURES", "11 14 16 17 18").split()
nom, vp, tactile, q = ("ordi", {"width": 1440, "height": 900}, False, "&qualite=haute") if ORDI else ("tel", {"width": 390, "height": 844}, True, "")

sorties = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-angle=d3d11", "--ignore-gpu-blocklist"])
    for h in heures:
        ctx = b.new_context(viewport=vp, is_mobile=tactile, has_touch=tactile); pg = ctx.new_page()
        err = []; pg.on("pageerror", lambda e: err.append(str(e)[:160]))
        pg.goto(f"http://localhost:8765/lieux/hillary-m-styl/?direct=1&meteo=clair&heure={h}{q}")
        pg.wait_for_function("document.body.classList.contains('embelli')", timeout=150000)
        try: pg.wait_for_function("document.body.classList.contains('cuit')", timeout=60000)
        except Exception: pass
        pg.evaluate("__monde.pnj.reglages.conversations = false; __monde.pnj.annulerAbordage && __monde.pnj.annulerAbordage()")
        time.sleep(3)
        f = V / f"{nom}-soleil-{h}h-entree-{suffixe}.png"; pg.screenshot(path=str(f), timeout=120000); sorties.append(f)
        pg.evaluate("__monde.deplacement.allerA('comptoir')")
        pg.wait_for_function("__monde.deplacement.noeud === 'comptoir' && !__monde.deplacement.enMarche", timeout=60000)
        pg.evaluate("__monde.deplacement.tournerVers(new (__monde.moteur.THREE.Vector3)(1.5, 0.6, 6))"); time.sleep(2.5)
        f = V / f"{nom}-soleil-{h}h-vitrine-{suffixe}.png"; pg.screenshot(path=str(f), timeout=120000); sorties.append(f)
        print(f"{h} h :", pg.evaluate("JSON.stringify(__monde.soleilVitrine.etat) + ' · soleil ' + JSON.stringify(__monde.ciel.etat.soleil) + ' · doré ' + __monde.ciel.etat.dore.toFixed(2)"), "· erreurs :", err or "aucune", flush=True)
        ctx.close()
    b.close()

H = 620 if not ORDI else 330
ims = [Image.open(f) for f in sorties]; ims = [i.resize((int(i.width * H / i.height), H)) for i in ims]
pl = Image.new("RGB", (sum(i.width for i in ims) + 6 * (len(ims) - 1), H), (20, 20, 20)); x = 0
for i in ims: pl.paste(i, (x, 0)); x += i.width + 6
pl.save(V / f"soleil-{suffixe}.jpg", quality=86); print("planche :", V / f"soleil-{suffixe}.jpg", pl.size)

"""LE MONDE · mesurer le salon (REALISME.md R14, AUDIT-JEU-VIDEO.md vague 4) : poids, temps, dessin, cadence.

    python monde/_outils/mesurer.py [suffixe]          (le serveur doit tourner : python monde/_servir.py --sans-construire)
    → monde/_vues/mesure-<suffixe>.json + un tableau imprimé

Pour chaque qualité (basse, moyenne, haute) au format téléphone (390 × 844), et en haute à l'ordinateur :
  · le poids de chaque fichier chargé, et le total ;
  · le temps jusqu'au bouton « Entrer » actif, jusqu'à « embelli », jusqu'à « cuit » ;
  · par image : appels de dessin, triangles ; en mémoire graphique : textures et géométries ;
  · la cadence (images par seconde) sur 10 s, immobile à l'entrée, puis pendant un déplacement.
⚠️ Ce PC (Intel HD 5500, 8 Go) n'est PAS un téléphone : la cadence mesurée ici est un ORDRE DE GRANDEUR, la vraie
preuve est un Android d'entrée de gamme et l'iPhone de Mongazi. Les poids et les appels de dessin, eux, sont
justes partout. Un seul navigateur à la fois.
"""
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
VUES = os.path.join(ICI, "..", "_vues")
suffixe = sys.argv[1] if len(sys.argv) > 1 else "mesure"
URL = "http://localhost:8765/lieux/hillary-m-styl/?direct=1&meteo=clair&heure=14"
CAS = [("tel", "basse"), ("tel", "moyenne"), ("tel", "haute"), ("ordi", "haute")]
VP = {"tel": ({"width": 390, "height": 844}, True), "ordi": ({"width": 1440, "height": 900}, False)}

CADENCE = """async (duree) => {
  let n = 0; const t0 = performance.now();
  await new Promise(ok => { const f = () => { n++; if (performance.now() - t0 < duree) requestAnimationFrame(f); else ok(); }; requestAnimationFrame(f); });
  return Math.round(n / ((performance.now() - t0) / 1000) * 10) / 10;
}"""
INFO = """() => { const r = __monde.moteur.renderer, i = r.info;
  return { appels: i.render.calls, triangles: i.render.triangles, textures: i.memory.textures, geometries: i.memory.geometries,
           qualite: __monde.moteur.qualite.nom, programmes: (i.programs || []).length }; }"""

resultats = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=angle", "--enable-unsafe-swiftshader"])
    for appareil, qualite in CAS:
        vp, tactile = VP[appareil]
        ctx = b.new_context(viewport=vp, is_mobile=tactile, has_touch=tactile)
        pg = ctx.new_page()
        poids = {}
        def reponse(r):
            try:
                if r.request.resource_type in ("document", "script", "stylesheet", "image", "media", "font", "fetch", "xhr", "other"):
                    corps = r.body()
                    poids[r.url.split("?")[0].replace("http://localhost:8765/", "")] = len(corps)
            except Exception:
                pass
        pg.on("response", reponse)
        t0 = time.time()
        pg.goto(URL + f"&qualite={qualite}")
        temps = {}
        while time.time() - t0 < 180:
            try:
                etat = pg.evaluate("({ entrer: !!document.querySelector('.ouv-entrer') && !document.querySelector('.ouv-entrer').disabled, embelli: document.body.classList.contains('embelli'), cuit: document.body.classList.contains('cuit') })")
            except Exception:
                etat = {}
            for k, v in etat.items():
                if v and k not in temps:
                    temps[k] = round(time.time() - t0, 1)
            if "cuit" in temps:
                break
            time.sleep(0.5)
        time.sleep(4)
        info = pg.evaluate(INFO)
        fps_immobile = pg.evaluate(CADENCE, 10000)
        pg.evaluate("__monde.deplacement.allerA('comptoir')")
        fps_marche = pg.evaluate(CADENCE, 4000)
        info2 = pg.evaluate(INFO)
        total = sum(poids.values())
        lourds = sorted(poids.items(), key=lambda kv: -kv[1])[:8]
        r = {"appareil": appareil, "qualite_demandee": qualite, **info, "appels_comptoir": info2["appels"], "triangles_comptoir": info2["triangles"],
             "fps_immobile": fps_immobile, "fps_marche": fps_marche, "temps_s": temps, "poids_total_ko": round(total / 1024), "fichiers": len(poids),
             "plus_lourds_ko": [(u, round(n / 1024)) for u, n in lourds]}
        resultats.append(r)
        print(f"{appareil:4} {qualite:7} → {info['qualite']:7} · {r['poids_total_ko']:6} Ko ({len(poids)} fichiers) · entrer {temps.get('entrer', '?')} s, cuit {temps.get('cuit', '?')} s · "
              f"{info['appels']} appels, {info['triangles']} triangles · {info['textures']} textures · {fps_immobile} i/s immobile, {fps_marche} en marchant")
        ctx.close()
    b.close()

with open(os.path.join(VUES, f"mesure-{suffixe}.json"), "w", encoding="utf-8") as f:
    json.dump(resultats, f, ensure_ascii=False, indent=1)
print("\nles plus lourds (téléphone, moyenne) :")
for u, n in next((r for r in resultats if r["qualite_demandee"] == "moyenne"), resultats[0])["plus_lourds_ko"]:
    print(f"  {n:6} Ko  {u}")

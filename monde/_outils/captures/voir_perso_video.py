"""LE MONDE · les personnages-vidéo, regardés : la même conversation en 3D puis en vidéo, côte à côte.

    python monde/_servir.py --sans-construire     (dans un autre terminal)
    python monde/_outils/captures/voir_perso_video.py [hillary afi senami maman] [--nuit] [--tel | --ordi]

Par le VRAI parcours : aller au comptoir et parler à Hillary ; toucher une visiteuse, s'approcher, « Parler ».
Au téléphone (390) et à l'ordinateur (1440, qualité haute). Sort, par personnage, les captures
`_vues/{tel,ordi}-{video,3d}-<qui>[-nuit].png` et la planche `_vues/video-contre-3d-<qui>[-nuit].jpg`
(téléphone 3D | téléphone vidéo | ordinateur 3D | ordinateur vidéo). Hillary a en plus `…-hillary-attend…`
(au comptoir, avant de lui parler). À REGARDER : un contrôle vert ne dit pas qu'un visage est beau.
Une page par (appareil, mode), tous les personnages à la suite : ce PC a 8 Go, un seul navigateur.
"""
import sys
import time
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
V = Path(__file__).resolve().parents[2] / "_vues"
NUIT = "--nuit" in sys.argv
QUI = [a for a in sys.argv[1:] if not a.startswith("--")] or ["hillary", "afi", "senami", "maman"]
HEURE = "&heure=21" if NUIT else "&heure=14"
SUF = "-nuit" if NUIT else ""
APPAREILS = [("tel", {"width": 390, "height": 844}, True, ""), ("ordi", {"width": 1440, "height": 900}, False, "&qualite=haute")]
if "--tel" in sys.argv: APPAREILS = APPAREILS[:1]
if "--ordi" in sys.argv: APPAREILS = APPAREILS[1:]


def attendre_options(pg, motif):
    t = time.time()
    while time.time() - t < 45:
        if pg.evaluate("(m) => { const o = document.querySelector('.options'); return o.classList.contains('ouverte') && new RegExp(m).test(o.textContent); }", motif):
            return True
        time.sleep(0.5)
    return False


def fermer(pg):
    pg.evaluate("__monde.dialogue.fermer && __monde.dialogue.fermer()"); time.sleep(0.8)
    pg.evaluate("(() => { const o = document.querySelector('.options'); if (o && o.classList.contains('ouverte')) { const b = o.querySelector('[data-a=fermer], .opt-fermer'); if (b) b.click(); } })()")
    time.sleep(0.4)


with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-angle=d3d11", "--ignore-gpu-blocklist", "--autoplay-policy=no-user-gesture-required"])
    for nom, vp, tactile, q in APPAREILS:
        for mode in ("video", "3d"):
            ctx = b.new_context(viewport=vp, is_mobile=tactile, has_touch=tactile); pg = ctx.new_page()
            err = []; pg.on("pageerror", lambda e: err.append(str(e)[:200]))
            pg.goto("http://localhost:8765/lieux/hillary-m-styl/?direct=1" + q + HEURE + ("&sans-video" if mode == "3d" else ""))
            pg.wait_for_function("document.body.classList.contains('embelli')", timeout=150000)
            pg.wait_for_function("(() => { const n = __monde.pnj.parId.afi; return n && n.perso.modele3d; })()", timeout=120000)
            if mode == "video":
                for qui in QUI:
                    try:
                        pg.wait_for_function(f"__monde.persoVideos['{qui}'] && __monde.persoVideos['{qui}'].etat.pret", timeout=90000)
                    except Exception:
                        print(nom, qui, "vidéo PAS prête :", pg.evaluate(f"__monde.persoVideos['{qui}'] ? JSON.stringify(__monde.persoVideos['{qui}'].etat) : 'absente'"),
                              pg.evaluate("JSON.stringify(performance.getEntriesByType('resource').filter(e => /video-/.test(e.name)).map(e => [e.name.slice(-34), Math.round(e.startTime), Math.round(e.responseEnd), e.transferSize]))"),
                              pg.evaluate("location.href"))
            pg.evaluate("__monde.pnj.reglages.conversations = false; __monde.pnj.annulerAbordage && __monde.pnj.annulerAbordage()")
            time.sleep(1.5)
            for qui in QUI:
                try:
                    if qui == "hillary":
                        pg.evaluate("__monde.deplacement.allerA('comptoir')")
                        pg.wait_for_function("__monde.deplacement.noeud === 'comptoir' && !__monde.deplacement.enMarche", timeout=60000)
                        time.sleep(2.5)
                        pg.screenshot(path=str(V / f"{nom}-{mode}-hillary-attend{SUF}.png"))
                        pg.evaluate("__monde.toucherHillary()")
                        attendre_options(pg, ".")
                        pg.evaluate("document.querySelector('.options .opt-principal').click()"); time.sleep(3.2)
                    else:
                        pg.evaluate("(q) => __monde.toucherPnj(q)", qui)
                        attendre_options(pg, "visiteuse|Afi|Sènami|Maman")
                        pg.evaluate("document.querySelector('.options .opt-principal').click()")
                        if mode == "video":
                            try: pg.wait_for_function(f"__monde.persoVideos['{qui}'].montre === 1", timeout=30000)
                            except Exception: pass
                        time.sleep(3.2)
                    pg.screenshot(path=str(V / f"{nom}-{mode}-{qui}{SUF}.png"))
                    etat = pg.evaluate(f"__monde.persoVideos['{qui}'] ? JSON.stringify(__monde.persoVideos['{qui}'].etat) : 'sans vidéo'")
                    print(nom, mode, qui, etat)
                except Exception as e:
                    print(nom, mode, qui, "ÉCHEC :", str(e)[:200])
                fermer(pg)
            print(nom, mode, "erreurs :", err or "aucune", flush=True)
            ctx.close()
    b.close()

# les planches : téléphone 3D | téléphone vidéo | ordinateur 3D | ordinateur vidéo, à la même hauteur
H = 700
for qui in QUI + (["hillary-attend"] if "hillary" in QUI else []):
    noms = [f"{a}-{m}-{qui}{SUF}.png" for a, *_ in APPAREILS for m in ("3d", "video")]
    ims = [Image.open(V / n) for n in noms if (V / n).exists()]
    if not ims: continue
    ims = [im.resize((int(im.width * H / im.height), H)) for im in ims]
    pl = Image.new("RGB", (sum(i.width for i in ims) + 10 * (len(ims) - 1), H), (20, 20, 20))
    x = 0
    for i in ims: pl.paste(i, (x, 0)); x += i.width + 10
    f = V / f"video-contre-3d-{qui}{SUF}.jpg"; pl.save(f, quality=85); print("planche :", f)

# -*- coding: utf-8 -*-
"""MA LETTRE À… · l'image de partage (`og.jpg`, 1200 × 630).

    python malettre/_og.py            # og.jpg (français) et og-en.jpg (anglais)

Sans `og:image` en JPEG, un lien collé dans WhatsApp s'affiche en carte grise
(leçon du parc). Rendue par Playwright, comme les logos de Mon Bénin : les
polices de la page arrivent de Google Fonts, donc il faut le réseau.
⛔ Aucune personne, aucun visage : la lettre, le prénom, le cachet.
"""
import pathlib

from playwright.sync_api import sync_playwright

ICI = pathlib.Path(__file__).resolve().parent
TEXTES = {
    "og.jpg": {"lang": "fr", "sur": "Lettres digitales scellées", "ma": "Ma lettre à",
               "chapo": "Une lettre scellée qui s'ouvre à l'heure que tu choisis."},
    "og-en.jpg": {"lang": "en", "sur": "Sealed digital letters", "ma": "My letter to",
                  "chapo": "A sealed letter that opens at the time you choose."},
}

PAGE = """<!DOCTYPE html><html lang="__LANG__"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Display&family=Pinyon+Script&family=Schibsted+Grotesk:wght@500;700&display=block">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1200px;height:630px;overflow:hidden;font-family:"Schibsted Grotesk",sans-serif;color:#f4ede0;
  background:radial-gradient(90% 120% at 72% 40%,#2a2234 0%,#1d1826 38%,#141019 75%)}
.g{position:absolute;left:84px;top:96px;width:620px}
.sur{font-size:19px;letter-spacing:.26em;text-transform:uppercase;font-weight:700;color:#c9a227}
h1{font-family:"Libre Caslon Display",Georgia,serif;font-weight:400;font-size:118px;line-height:.95;margin-top:26px;letter-spacing:-.015em}
.nom{display:block;font-family:"Pinyon Script",cursive;color:#c9a227;font-size:150px;line-height:1.05;margin-top:-4px}
.chapo{font-size:27px;color:#a39bb3;margin-top:22px;max-width:30ch;line-height:1.35}
.by{position:absolute;left:84px;bottom:48px;font-size:15px;letter-spacing:.3em;text-transform:uppercase;font-weight:700;color:#a39bb3}
.scene{position:absolute;right:70px;top:120px;width:400px;height:400px;perspective:1100px}
.env{position:absolute;left:0;top:70px;width:400px;height:250px;transform:rotateX(12deg) rotateY(-20deg) rotateZ(-5deg);
  transform-style:preserve-3d}
.face{position:absolute;inset:0;border-radius:7px;background:linear-gradient(160deg,#f7f1e6,#ebe0cd);
  box-shadow:0 44px 80px rgba(0,0,0,.6);overflow:hidden}
.rabat{position:absolute;left:0;right:0;top:0;height:62%;background:linear-gradient(180deg,#efe4d1,#e2d4bc);
  clip-path:polygon(0 0,100% 0,50% 100%);filter:drop-shadow(0 2px 0 rgba(36,29,43,.1))}
.cire{position:absolute;left:50%;top:62%;width:92px;height:92px;margin:-46px 0 0 -46px;border-radius:50%;
  background:radial-gradient(circle at 34% 30%,#b2434e,#8c2f39 60%,#6d1f27);display:grid;place-items:center;
  font-family:"Libre Caslon Display",serif;font-size:46px;color:#f0d6cf;
  box-shadow:0 8px 18px rgba(0,0,0,.4),inset 0 -4px 8px rgba(0,0,0,.25),inset 0 4px 6px rgba(255,255,255,.18)}
.ombre{position:absolute;left:40px;right:40px;top:340px;height:40px;border-radius:50%;
  background:radial-gradient(closest-side,rgba(0,0,0,.55),transparent)}
</style></head><body>
<div class="g">
  <p class="sur">__SUR__</p>
  <h1>__MA__<span class="nom">Afi</span></h1>
  <p class="chapo">__CHAPO__</p>
</div>
<div class="scene"><div class="ombre"></div><div class="env"><div class="face"><div class="rabat"></div><div class="cire">K</div></div></div></div>
<p class="by">by NEBULA Agency</p>
</body></html>"""


def main():
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        pg = nav.new_page(viewport={"width": 1200, "height": 630})
        for nom, t in TEXTES.items():
            page = (PAGE.replace("__LANG__", t["lang"]).replace("__SUR__", t["sur"])
                    .replace("__MA__", t["ma"]).replace("__CHAPO__", t["chapo"]))
            pg.set_content(page, wait_until="networkidle")
            # ⚠️ `document.fonts.ready` répondait AVANT que les polices soient
            # demandées : la première image (og.jpg) est sortie SANS UN MOT,
            # la seconde était juste (polices en cache). On charge chaque
            # police par son nom, et on refuse d'écrire si l'une manque.
            ok = pg.evaluate("""async () => {
                const f = ['118px "Libre Caslon Display"', '150px "Pinyon Script"',
                           '700 19px "Schibsted Grotesk"', '500 27px "Schibsted Grotesk"'];
                await Promise.all(f.map(x => document.fonts.load(x)));
                await document.fonts.ready;
                return f.every(x => document.fonts.check(x)); }""")
            if not ok:
                raise SystemExit("⛔ %s : une police n'est pas arrivée (réseau ?), rien n'est écrit" % nom)
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(ICI / nom), type="jpeg", quality=88)
            print("%s : %d Ko" % (nom, (ICI / nom).stat().st_size // 1024))
        nav.close()


if __name__ == "__main__":
    main()

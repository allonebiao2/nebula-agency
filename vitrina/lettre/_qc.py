"""QC du gabarit de lettre · MINUIT

    cd vitrina/lettre && python3 _qc.py

Ce que ça vérifie, et pourquoi ces contrôles-là :
  · le seuil s'ouvre et le code garde vraiment la porte
  · la lettre est LISIBLE (contraste mesuré, pas supposé)
  · le « Non » s'enfuit SANS SORTIR de sa zone (sur un téléphone, un bouton
    qui part hors de l'écran n'est pas drôle, il casse la page)
  · aucune image inventée quand il n'y a pas de photo
  · aucune ressource externe bloquante pour la police manuscrite
  · rien ne déborde à 390, 768 et 1440
"""
import glob
import json
import os
import re
import sys
import unicodedata

from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ICI, "gabarit.html")
URL = "file://" + FICHIER

ok = 0
rouges = []


def t(nom, cond, info=""):
    global ok
    if cond:
        ok += 1
        print(f"  OK   {nom}")
    else:
        rouges.append(nom)
        print(f"  ROUGE {nom}   {info}")


def contraste(c1, c2):
    def lin(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    def lum(r, g, b):
        return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    a, b = lum(*c1), lum(*c2)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def rgb(txt):
    n = [int(x) for x in re.findall(r"\d+", txt)[:3]]
    return tuple(n) if len(n) == 3 else (0, 0, 0)


def entrer(pg, code="0410"):
    """Franchit le seuil : ouvre l'enveloppe puis compose le code."""
    pg.click("#enveloppe")
    pg.wait_for_timeout(1800)
    if code:
        for c in code:
            pg.click(f"#clavier button:text-is('{c}')")
        pg.wait_for_timeout(1400)


def main():
    src = open(FICHIER, encoding="utf-8").read()

    print("\n=== 1. Le fichier est autonome ===")
    externes = re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)', src)
    non_polices = [u for u in externes if "fonts.googleapis" not in u and "fonts.gstatic" not in u]
    t("aucune ressource externe hors polices", not non_polices, str(non_polices))
    t("la police manuscrite est EMBARQUEE", "data:font/woff2;base64," in src)
    t("aucune balise img en dur (pas de photo inventee)",
      not re.search(r"<img\s", src), "une <img> ecrite en dur dans le gabarit")
    t("aucune bibliotheque", not re.search(r'<script[^>]+src=', src))
    t("non indexable", 'content="noindex,nofollow,noarchive"' in src)

    # ⚠️ LE DÉFAUT LE PLUS CHER DE CE FICHIER, et il tenait en UNE frappe :
    # « --or-clair:#d3ae६8 » portait un CHIFFRE DEVANAGARI au lieu d'un 6.
    # La couleur devenait invalide, donc le radial-gradient entier était
    # invalide : le cachet de cire ne s'affichait PAS et le prénom de la
    # destinataire était illisible. Les deux éléments les plus importants du
    # premier écran, tués par un caractère sosie que rien ne signalait.
    sosies = []
    for i, ch in enumerate(src):
        if ord(ch) < 128:
            continue
        try:
            n = unicodedata.name(ch)
        except ValueError:
            continue
        if any(a in n for a in ("CYRILLIC", "GREEK", "DEVANAGARI", "FULLWIDTH",
                                "ARABIC", "MATHEMATICAL", "CHEROKEE")):
            sosies.append(f"ligne {src[:i].count(chr(10))+1} : {ch!r} ({n})")
    t("aucun caractere SOSIE d'un autre alphabet", not sosies, " · ".join(sosies[:3]))

    exe = glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome")
    if not exe:
        print("\n(pas de navigateur : contrôles visuels sautés)")
        return
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=exe[0])

        # ---------- le seuil et le code ----------
        print("\n=== 2. Le seuil ===")
        pg = b.new_page(viewport={"width": 390, "height": 844})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(URL)
        pg.wait_for_timeout(2200)
        t("la lettre est CACHEE avant l'ouverture", pg.locator("#lettre").is_hidden())
        t("le prenom est en manuscrite",
          pg.evaluate("""(()=>{const t=document.createElement('span');t.textContent='Ama';
            t.style.cssText='position:absolute;font-size:60px;visibility:hidden';
            t.style.fontFamily='"Petit Formal Script",monospace';document.body.appendChild(t);
            const a=t.getBoundingClientRect().width;t.style.fontFamily='monospace';
            const c=t.getBoundingClientRect().width;t.remove();return a!==c;})()"""),
          "la police embarquee ne s'applique pas")
        pg.click("#enveloppe")
        pg.wait_for_timeout(900)
        t("le cachet se fend a l'ouverture",
          pg.evaluate("document.querySelector('.enveloppe').classList.contains('ouvert')"))
        pg.wait_for_timeout(1100)
        t("le code apparait", pg.locator("#code").is_visible())
        t("  -> la lettre n'est TOUJOURS pas accessible", pg.locator("#lettre").is_hidden())

        print("\n=== 3. Le code garde la porte ===")
        for c in "1111":
            pg.click(f"#clavier button:text-is('{c}')")
        pg.wait_for_timeout(300)
        t("un mauvais code fait trembler la carte",
          pg.evaluate("document.querySelector('#carteCode').classList.contains('faux')"))
        pg.wait_for_timeout(700)
        t("  -> et remet les points a zero",
          pg.evaluate("document.querySelectorAll('#points i.plein').length") == 0)
        t("  -> la lettre reste fermee", pg.locator("#lettre").is_hidden())
        for c in "0410":
            pg.click(f"#clavier button:text-is('{c}')")
        pg.wait_for_timeout(1500)
        t("le BON code ouvre la lettre", pg.locator("#lettre").is_visible())
        t("aucune erreur JS", not errs, str(errs[:2]))

        # ---------- la lettre ----------
        print("\n=== 4. La lettre se lit ===")
        pg.wait_for_timeout(1200)
        t("le texte de la lettre est affiche",
          "je les écris comme elles viennent" in pg.inner_text("#corps"))
        vis = pg.evaluate("""(()=>{const s=document.querySelector('#s-lettre .ligne span');
          return getComputedStyle(s).transform;})()""")
        t("les lignes sont montees (encre ecrite, pas restee cachee)",
          vis in ("none", "matrix(1, 0, 0, 1, 0, 0)"), vis)
        fond = rgb(pg.evaluate("getComputedStyle(document.querySelector('main')).backgroundColor"))
        enc = rgb(pg.evaluate("getComputedStyle(document.querySelector('#corps p')).color"))
        r = contraste(fond, enc)
        t(f"contraste du texte de la lettre ({r:.1f}:1)", r >= 7)
        acc = rgb(pg.evaluate("getComputedStyle(document.querySelector('#accueil')).color"))
        ra = contraste(fond, acc)
        t(f"contraste de l'accueil ({ra:.1f}:1)", ra >= 4.5)

        print("\n=== 5. Aucune photo inventee ===")
        # ⚠️ text-transform:uppercase rend « TA PHOTO ICI » : on lit ce qui
        # est RENDU, pas ce qui est écrit dans la source.
        t("un cadre sans photo le DIT",
          "ta photo ici" in pg.inner_text("#listePhotos").lower())
        t("  -> et n'affiche aucune image",
          pg.evaluate("document.querySelectorAll('#listePhotos img').length") == 0)
        # ⚠️ Trouvé sur une capture, pas dans le code : les légendes étaient
        # coupées en plein mot (« Notre premi… »). Sur un cadeau, c'est pire
        # que pas de légende. On mesure le débordement réel du texte.
        coupees = pg.evaluate("""(()=>{const o=[];
          document.querySelectorAll('#listePhotos figcaption').forEach(c=>{
            if(c.scrollWidth > c.clientWidth + 1) o.push(c.textContent.slice(0,20));
          });return o})()""")
        t("aucune legende de photo coupee", not coupees, str(coupees))

        print("\n=== 6. Le Non s'enfuit, mais reste dans sa zone ===")
        pg.locator("#s-question").scroll_into_view_if_needed()
        pg.wait_for_timeout(600)
        av = pg.evaluate("JSON.stringify(document.querySelector('#bNon').getBoundingClientRect())")
        for _ in range(6):
            pg.evaluate("document.querySelector('#bNon').dispatchEvent(new MouseEvent('mouseenter'))")
            pg.wait_for_timeout(120)
        ap = pg.evaluate("JSON.stringify(document.querySelector('#bNon').getBoundingClientRect())")
        t("il bouge", av != ap)
        dedans = pg.evaluate("""(()=>{const n=document.querySelector('#bNon').getBoundingClientRect();
          const z=document.querySelector('#duo').getBoundingClientRect();
          return n.left>=z.left-1 && n.right<=z.right+1 && n.top>=z.top-1 && n.bottom<=z.bottom+1;})()""")
        t("IL NE SORT PAS de sa zone", dedans,
          "un bouton hors de l'ecran sur telephone casse la page")
        t("il se moque en fuyant", pg.inner_text("#raillerie").strip() != "")
        # Le contrôle qui compte : après beaucoup de fuites, le Oui doit
        # rester cliquable. C'est ici qu'on a trouvé que le Non se posait
        # dessus et rendait la réponse impossible.
        for _ in range(15):
            pg.evaluate("document.querySelector('#bNon').dispatchEvent(new MouseEvent('mouseenter'))")
            pg.wait_for_timeout(40)
        couvert = pg.evaluate("""(()=>{const o=document.querySelector('#bOui').getBoundingClientRect();
          const el=document.elementFromPoint(o.left+o.width/2,o.top+o.height/2);
          return el && el.id!=='bOui';})()""")
        t("LE OUI RESTE CLIQUABLE apres 15 fuites", not couvert,
          "le Non s'est pose sur le Oui : on ne peut plus repondre")
        pg.click("#bOui", timeout=5000)
        pg.wait_for_timeout(600)
        t("le Oui repond", pg.inner_text("#reponse").strip() != "")

        print("\n=== 7. Rien ne deborde ===")
        for w, h in ((390, 844), (768, 1024), (1440, 900)):
            pv = b.new_page(viewport={"width": w, "height": h})
            pv.goto(URL)
            pv.wait_for_timeout(1500)
            entrer(pv)
            pv.wait_for_timeout(800)
            ov = pv.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
            t(f"aucun debordement horizontal a {w}px", ov <= 1, f"{ov}px")
            petits = pv.evaluate("""(()=>{const o=[];
              document.querySelectorAll('button,a[href]').forEach(e=>{
                const r=e.getBoundingClientRect();
                if(r.width>0 && (r.height<40||r.width<40)) o.push(e.textContent.trim().slice(0,18)+' '+Math.round(r.width)+'x'+Math.round(r.height));
              });return o.slice(0,5)})()""")
            if w == 390:
                t("cibles tactiles >= 40px a 390px", not petits, str(petits))
            pv.close()
        pg.close()

        print("\n=== 8. Mouvement reduit : tout reste lisible ===")
        pr = b.new_page(viewport={"width": 390, "height": 844})
        pr.emulate_media(reduced_motion="reduce")
        pr.goto(URL)
        pr.wait_for_timeout(1200)
        entrer(pr)
        pr.wait_for_timeout(900)
        t("la lettre s'ouvre quand meme", pr.locator("#lettre").is_visible())
        op = pr.evaluate("""(()=>{const s=document.querySelector('#s-lettre .ligne span');
          return getComputedStyle(s).opacity;})()""")
        t("le texte est visible sans animation", float(op) > 0.9, op)
        pr.close()

        print("\n=== 9. Sans code, on entre directement ===")
        sc = src.replace('code: "0410"', 'code: ""')
        tmp = os.path.join(ICI, "_tmp_sans_code.html")
        open(tmp, "w", encoding="utf-8").write(sc)
        pn = b.new_page(viewport={"width": 390, "height": 844})
        pn.goto("file://" + tmp)
        pn.wait_for_timeout(1200)
        pn.click("#enveloppe")
        pn.wait_for_timeout(2200)
        t("pas de clavier quand il n'y a pas de code", pn.locator("#code").is_hidden())
        t("  -> la lettre s'ouvre directement", pn.locator("#lettre").is_visible())
        pn.close()
        os.remove(tmp)

        b.close()

    print(f"\n===== {ok} verts / {len(rouges)} rouges =====")
    if rouges:
        for r in rouges:
            print("  ROUGE :", r)
    return 1 if rouges else 0


if __name__ == "__main__":
    sys.exit(main())

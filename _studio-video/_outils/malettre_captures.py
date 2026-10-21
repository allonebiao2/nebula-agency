"""Le vrai constructeur de MA LETTRE À…, photographié pour la pub (plan « la plume »).

Sur téléphone (390 x 844, x3), dans public/malettre/<langue>/ :

    entete.jpg      l'en-tête du constructeur (« Ma lettre à… », la jauge)
    moi.jpg         l'écran « Écris-la », le mode « Je l'écris moi-même » choisi
    fiche-<k>.jpg   la fiche de la plume, ENTIÈRE, après k puces cochées (k = 0..n)
    lettre.jpg      le titre et le mot, remplis de la lettre que la plume a écrite

et src/malettre/captures.ts : la taille de la fiche et le centre de chaque puce
(px CSS, dans la fiche), pour que le doigt tombe juste et que la fiche défile
jusqu'à la puce qu'on coche.

⚠️ Rien n'est inventé : les puces cochées et le souvenir sont ceux de la FICHE de
la lettre d'exemple d'Afi (`malettre/exemples.json`), et la lettre est celle que
la vraie plume a écrite à partir de cette fiche le 2026-10-16. Le constructeur
est le fichier du dépôt, ouvert tel quel : la plume n'est pas appelée.

    python _outils/malettre_captures.py
"""
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ICI = Path(__file__).resolve().parent.parent
MALETTRE = ICI.parent / "malettre"
PUBLIC = ICI / "public/malettre"
SORTIE_TS = ICI / "src/malettre/captures.ts"

LANGUES = {
    "fr": {"page": MALETTRE / "creer.html", "exemples": MALETTRE / "exemples.json"},
    "en": {"page": MALETTRE / "en/creer.html", "exemples": MALETTRE / "exemples.en.json"},
}


def exemple(fichier):
    return next(e for e in json.loads(fichier.read_text(encoding="utf-8"))["exemples"] if e["id"] == "afi")


def boite(page, el, ref):
    """Le centre d'un élément, en px CSS, relatif au coin de `ref`."""
    b, r = el.bounding_box(), ref.bounding_box()
    return {"x": round(b["x"] + b["width"] / 2 - r["x"], 1), "y": round(b["y"] + b["height"] / 2 - r["y"], 1)}


def photographier(p, langue, conf):
    dossier = PUBLIC / langue
    dossier.mkdir(parents=True, exist_ok=True)
    ex = exemple(conf["exemples"])
    nav = p.chromium.launch()
    ctx = nav.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True,
                          has_touch=True, reduced_motion="reduce", locale="fr-FR" if langue == "fr" else "en-GB")
    page = ctx.new_page()
    page.goto(conf["page"].as_uri(), wait_until="load")
    time.sleep(0.8)
    page.locator("header").first.screenshot(path=str(dossier / "entete.jpg"), type="jpeg", quality=90)
    entete_h = page.locator("header").first.bounding_box()["height"]

    # L'occasion de la lettre d'Afi, par son nom exact dans le constructeur.
    page.locator(".occ", has=page.locator("b", has_text=ex["occasionNom"])).first.click()
    time.sleep(0.5)
    page.fill("#f-pour", ex["pour"])
    page.fill("#f-de", ex["de"])

    # « Je l'écris moi-même » : le mot vide, prêt à recevoir.
    moi = page.locator('.m[data-mode="moi"]')
    moi.click()
    time.sleep(0.3)
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(0.3)
    page.screenshot(path=str(dossier / "moi.jpg"), type="jpeg", quality=88)
    vue = page.locator("body")
    doigt_moi = boite(page, moi, vue)

    # La plume : la fiche, puis chaque puce de la fiche d'Afi, une à une.
    plume = page.locator('.m[data-mode="plume"]')
    doigt_plume = boite(page, plume, vue)
    plume.click()
    time.sleep(0.4)
    # L'en-tête collant se poserait sur la fiche photographiée : il est photographié à part.
    page.add_style_tag(content="header{position:static!important}")
    fiche = page.locator("#fiche")
    puces = []
    for rep in ex["fiche"]["reponses"]:
        for r in rep["r"]:
            q = page.locator("#questions .q").filter(has=page.locator(".q-t", has_text=rep["q"]))
            el = q.get_by_role("button", name=r, exact=True).first
            if el.count() == 0:
                print("  ⛔ puce absente :", rep["q"], "→", r)
                continue
            # ⚠️ Certaines questions ont un choix d'office (la longueur, le français) :
            # cliquer une puce déjà cochée la DÉCOCHERAIT.
            if el.get_attribute("aria-pressed") == "true":
                continue
            puces.append((el, r))
    fiche.screenshot(path=str(dossier / "fiche-0.jpg"), type="jpeg", quality=86)
    taille = fiche.bounding_box()
    centres = []
    for k, (el, r) in enumerate(puces, start=1):
        centres.append({**boite(page, el, fiche), "texte": r})
        el.click()
        time.sleep(0.15)
        if k == len(puces):
            page.fill("#f-souvenir", ex["fiche"]["souvenir"])
        fiche.screenshot(path=str(dossier / f"fiche-{k}.jpg"), type="jpeg", quality=86)
    souvenir = boite(page, page.locator("#f-souvenir"), fiche)

    # La lettre écrite par la plume, dans le titre et le mot.
    page.fill("#f-titre", ex["titre"])
    page.fill("#f-lettre", "\n\n".join(ex["lettre"]))
    page.fill("#f-formule", ex["formule"])
    page.evaluate("document.querySelector('#f-lettre').style.height = document.querySelector('#f-lettre').scrollHeight + 'px'")
    titre = page.locator("#f-titre")
    titre.scroll_into_view_if_needed()
    page.evaluate(f"window.scrollBy(0, document.querySelector('#f-titre').closest('.groupe').getBoundingClientRect().top - 24)")
    time.sleep(0.4)
    page.screenshot(path=str(dossier / "lettre.jpg"), type="jpeg", quality=88)
    nav.close()
    print(f"  {langue} : fiche {taille['width']:.0f} x {taille['height']:.0f} px, {len(centres)} puces")
    return {
        "entete": round(entete_h, 1),
        "fiche": {"l": round(taille["width"], 1), "h": round(taille["height"], 1)},
        "puces": centres,
        "souvenir": souvenir,
        "doigt": {"moi": doigt_moi, "plume": doigt_plume},
    }


def main():
    sortie = {}
    with sync_playwright() as p:
        for langue, conf in LANGUES.items():
            sortie[langue] = photographier(p, langue, conf)
    SORTIE_TS.write_text(
        "/**\n * Écrit par `_outils/malettre_captures.py` : NE PAS ÉDITER À LA MAIN.\n"
        " * Les mesures du vrai constructeur (px CSS, téléphone de 390 px) : la hauteur de\n"
        " * l'en-tête, la taille de la fiche de la plume, le centre de chaque puce cochée.\n */\n"
        f"export const CAPTURES = {json.dumps(sortie, ensure_ascii=False)} as const;\n",
        encoding="utf-8")
    print("écrit :", SORTIE_TS.relative_to(ICI))


if __name__ == "__main__":
    main()

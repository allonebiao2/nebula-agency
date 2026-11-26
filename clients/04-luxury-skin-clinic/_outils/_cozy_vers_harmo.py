# -*- coding: utf-8 -*-
"""_cozy_vers_harmo.py · l'univers Cozy devient l'Harmonisation faciale, partout dans le site (26/11).

Demande de la cliente : les produits de Cozy rejoignent INA Luxury (fait par _cozy_vers_ina.py), et la place de
Cozy dans le club revient à son nouveau domaine, l'harmonisation faciale. Ce script change, mot pour mot :
  · le hub : la troisième carte, sa description, ses balises de partage, son balisage, les filtres d'avis ;
  · le menu « Catalogue » de la barre du bas (hub, clinique, INA) ;
  · la recherche commune : Cozy n'est plus une page à charger (ses produits sont dans INA) ;
  · cozy.html : une page de redirection vers la famille Intime & bien-être d'INA ;
  · le sitemap et la redirection Cloudflare (_redirects).
Idempotent : une phrase déjà remplacée n'est pas retouchée. Il dit ce qu'il a changé, fichier par fichier.
"""
import io
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

HARMO_MENU_HUB = """  {b:'Harmonisation faciale',href:'harmonisation-faciale.html',cats:[
    {n:'Facial Balancing',subs:['Zone supérieure','Milieu du visage','Zone inférieure','Genesis Face']},
    {n:'Genesis Hollywood',subs:['Frontalis + zone glabellaire','Rhinoplastie','Affiner le bas du visage','Visage complet']},
    {n:'Genesis Soft',subs:['Creux infraorbitaire','Sillon nasogénien','Restructuration labiale','Mâchoire et joues']}
  ]}"""
COZY_MENU_HUB = """  {b:'Cozy',href:'cozy.html',cats:[
    {n:'Hygiène intime',subs:['Gel Nettoyant Intime']},
    {n:'SELFCARE',subs:['Huile Intime','Body Butter Baiser Nocturne','Crème Mains','Baume Pailleté']},
    {n:'Produits raffermissants',subs:['Maca Cream','Le Boost Fermeté']}
  ]}"""

CHANGEMENTS = {
    "index.html": [
        ("soins visage et corps, cosmétiques INA Luxury et hygiène intime Cozy",
         "soins visage et corps, harmonisation faciale, cosmétiques INA Luxury et hygiène intime"),
        ("Trois univers : INA Luxury, Luxury Skin Clinic et Cozy", "Trois univers : INA Luxury, Luxury Skin Clinic et l'harmonisation faciale"),
        ('<article class="brand b3" data-href="cozy.html" tabindex="0" role="link" aria-label="Découvrir Cozy">',
         '<article class="brand b3" data-href="harmonisation-faciale.html" tabindex="0" role="link" aria-label="Découvrir l\'harmonisation faciale">'),
        ('assets/images/ambiances/hub-cozy.webp', 'assets/images/ambiances/hub-harmonisation.webp'),
        ('<div class="brand-emblem em-cozy"><img class="emblem-logo" src="assets/images/logos/logo-cozy.png" alt="Cozy"></div>',
         '<div class="brand-emblem em-cozy"><span>LS</span></div>'),
        ('<div class="brand-kicker">Hygiène Intime & Bien-être</div>', '<div class="brand-kicker">Cabinet de soins privés</div>'),
        ('<h2>Cozy</h2>', '<h2>Harmonisation faciale</h2>'),
        ('<p class="brand-desc">Des soins intimes pensés pour votre féminité, votre confort et votre bien-être.</p>',
         '<p class="brand-desc">Facial Balancing, Genesis Hollywood, Genesis Soft : chaque zone du visage, et son tarif.</p>'),
        ('>Produits Cozy</button>', '>Intime & bien-être</button>'),
        ('>Un produit Cozy</option>', '>Un produit intime & bien-être</option>'),
        ("cozy:'Un produit Cozy',", "cozy:'Un produit intime & bien-être',"),
        (COZY_MENU_HUB, HARMO_MENU_HUB),
    ],
    "luxury-skin-clinic.html": [
        (COZY_MENU_HUB, HARMO_MENU_HUB),
        ("(chargement INA &amp; Cozy…)", "(chargement INA Luxury…)"),
        ("Chargement des catalogues INA Luxury et Cozy…", "Chargement du catalogue INA Luxury…"),
    ],
    "ina-luxury.html": [
        ("""  {label:'COZY',href:'cozy.html',groups:[
    {label:'Hygiène intime',items:['Gel Nettoyant Intime']},
    {label:'SELFCARE',items:['Huile Intime','Crème Mains','Baume Pailleté']},
    {label:'Produits raffermissants',items:['Maca Cream','Le Boost Fermeté']},
  ]},""",
         """  {label:'HARMONISATION FACIALE',href:'harmonisation-faciale.html',groups:[
    {label:'Facial Balancing',items:['Zone supérieure','Milieu du visage','Zone inférieure','Genesis Face']},
    {label:'Genesis Hollywood',items:['Frontalis + zone glabellaire','Rhinoplastie','Affiner le bas du visage','Visage complet']},
    {label:'Genesis Soft',items:['Creux infraorbitaire','Sillon nasogénien','Restructuration labiale','Mâchoire et joues']},
  ]},"""),
        ("(chargement Cozy &amp; Clinic…)", "(chargement de la clinique…)"),
        ("Chargement des catalogues Cozy et Skin Clinic…", "Chargement du catalogue Skin Clinic…"),
    ],
    "assets/js/global-catalog.js": [
        ("   Recherche cross-marque (INA Luxury + Cozy + Luxury Skin Clinic).",
         "   Recherche cross-marque (INA Luxury + Luxury Skin Clinic). Cozy a rejoint INA le 26/11 : ses produits y sont."),
        ("    cozy:   {label:'Cozy',           short:'COZY',   url:'cozy.html',               color:'#d99aa9', kind:'produit'},\n", ""),
    ],
    "sitemap.xml": [
        ("https://luxuryclub229.com/cozy</loc>", "https://luxuryclub229.com/harmonisation-faciale</loc>"),
    ],
}

REDIRECTION = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cozy a rejoint INA Luxury | Luxury Club 229</title>
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="https://luxuryclub229.com/ina-luxury">
<meta http-equiv="refresh" content="0; url=ina-luxury.html#intime-bien-etre">
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#0b0a08;color:#f3eadb;font:16px/1.6 system-ui,sans-serif;text-align:center;padding:24px}
a{color:#e2c47a}</style>
</head>
<body>
<p>Les produits Cozy (hygiène intime, selfcare, produits raffermissants) sont désormais chez <a href="ina-luxury.html#intime-bien-etre">INA Luxury</a>.<br>
L'harmonisation faciale a son <a href="harmonisation-faciale.html">cabinet privé</a>.</p>
<script>location.replace('ina-luxury.html#intime-bien-etre');</script>
</body>
</html>
"""


def main():
    for f, reps in CHANGEMENTS.items():
        p = ICI / f
        s = p.read_text(encoding="utf-8")
        faits = 0
        for a, b in reps:
            if a in s:
                s = s.replace(a, b)
                faits += 1
            elif b and b in s:
                pass
            else:
                print(f"  ⚠ {f} : introuvable ni déjà fait : {a[:70]!r}")
        p.write_text(s, encoding="utf-8")
        print(f"{f} : {faits} changement(s)")
    (ICI / "cozy.html").write_text(REDIRECTION, encoding="utf-8")
    print("cozy.html : page de redirection vers INA (famille Intime & bien-être)")
    r = ICI / "_redirects"
    lignes = r.read_text(encoding="utf-8").splitlines() if r.exists() else []
    for l in ["/cozy /ina-luxury#intime-bien-etre 301", "/cozy.html /ina-luxury#intime-bien-etre 301"]:
        if l not in lignes:
            lignes.append(l)
    r.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("_redirects :", len(lignes), "règle(s)")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""_harmo_meso_2611.py · la Mésothérapie amincissante entre au cabinet d'harmonisation (Mme Sabrina, 26/11 :
« j'ai oublié ceci pour la grille tarifaire de l'espace harmonisation faciale »).

Son flyer donne, pour chaque zone, un prix à la SÉANCE et un FORFAIT de 4 séances (ancien prix barré). Le forfait est
une notion neuve : il a sa propre case (`forfait: {seances, p, avant}`), jamais confondue avec le prix d'une séance
(leçon : « une notion neuve = une case neuve »). Textes et prix de son flyer, mot pour mot.
Ce script pose les données et met d'accord les textes qui comptaient « trois » techniques. Idempotent.
"""
import io
import json
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

MESO = {
    "id": "mesotherapie-amincissante", "nom": "Mésothérapie amincissante",
    "famille": "Visage et ligne de mâchoire, double menton et joues",
    "flyer": "assets/harmonisation/flyer-mesotherapie-amincissante.jpg",
    "texte": ("Une technique qui élimine de façon saine les excès de gras au niveau des joues, du double menton et de la "
              "ligne de mâchoire, afin de réduire jusqu'à 80 % la masse graisseuse et d'affiner le visage, sans régime ni "
              "perte de poids."),
    "zones": [
        {"nom": "Double menton", "pin": [0.145, 0.355], "p": 160000, "forfait": {"seances": 4, "p": 544000, "avant": 640000},
         "r": [[0.02, 0.29, 0.98, 0.42]]},
        {"nom": "Joues", "pin": [0.145, 0.496], "p": 160000, "forfait": {"seances": 4, "p": 544000, "avant": 640000},
         "r": [[0.02, 0.43, 0.98, 0.56]]},
        {"nom": "Combo joues et menton", "pin": [0.145, 0.639], "p": 300000, "forfait": {"seances": 4, "p": 1020000, "avant": 1200000},
         "r": [[0.02, 0.57, 0.98, 0.71]]},
    ],
}
MENU_HUB = "    {n:'Mésothérapie amincissante',subs:['Double menton','Joues','Combo joues et menton']}"
MENU_INA = "    {label:'Mésothérapie amincissante',items:['Double menton','Joues','Combo joues et menton']},"


def remplace(s, a, b, nom):
    if a in s:
        return s.replace(a, b, 1)
    if b in s:
        return s
    raise SystemExit(f"{nom} : introuvable : {a[:80]}")


def main():
    # 1. la page : les données
    p = ICI / "harmonisation-faciale.html"
    s = p.read_text(encoding="utf-8")
    m = re.search(r'(<script id="harmo-donnees" type="application/json">)(.*?)(</script>)', s, re.S)
    d = json.loads(m.group(2))
    if not any(t["id"] == MESO["id"] for t in d):
        d.append(MESO)
        corps = "\n[\n" + ",\n".join(" " + json.dumps(t, ensure_ascii=False) for t in d) + "\n]\n"
        s = s[:m.start(2)] + corps + s[m.end(2):]
        print("données : Mésothérapie amincissante ajoutée (%d techniques)" % len(d))
    # 2. la page : les textes qui comptaient trois techniques, et le prix d'une séance / d'un forfait
    for a, b in [
        ("<title>Harmonisation faciale · Facial Balancing, Genesis Hollywood, Genesis Soft | Luxury Skin Clinic, Cotonou</title>",
         "<title>Harmonisation faciale · Facial Balancing, Genesis, Mésothérapie amincissante | Luxury Skin Clinic, Cotonou</title>"),
        ("Facial Balancing, Genesis Hollywood et Genesis Soft. Chaque zone du visage et son tarif, sur rendez-vous.",
         "Facial Balancing, Genesis Hollywood, Genesis Soft et Mésothérapie amincissante. Chaque zone du visage et son tarif, sur rendez-vous."),
        ("<p>Trois techniques, présentées avec les visuels du cabinet : on voit exactement de quelle zone on parle.</p>",
         "<p>Quatre techniques, présentées avec les visuels du cabinet : on voit exactement de quelle zone on parle.</p>"),
        ("  var prix=function(z){return z.pMin?(fcfa(z.pMin).replace(' FCFA','')+' à '+fcfa(z.pMax)):fcfa(z.p);};\n"
         "  window.LC_HARMO={donnees:HARMO,prix:prix,choix:{t:0,z:0}};",
         "  var prix=function(z){return z.pMin?(fcfa(z.pMin).replace(' FCFA','')+' à '+fcfa(z.pMax)):fcfa(z.p)+(z.forfait?' la séance':'');};\n"
         "  /* le forfait (Mésothérapie amincissante, 26/11) : sa propre case, jamais confondue avec le prix d'une séance */\n"
         "  var forfait=function(z){return z.forfait?fcfa(z.forfait.p)+' les '+z.forfait.seances+' séances':'';};\n"
         "  window.LC_HARMO={donnees:HARMO,prix:prix,forfait:forfait,choix:{t:0,z:0}};"),
        ("(z.detail?' ('+z.detail+')':'')+', '+prix(z)+'. Merci de me proposer un rendez-vous.';",
         "(z.detail?' ('+z.detail+')':'')+', '+prix(z)+(z.forfait?' ou '+forfait(z):'')+'. Merci de me proposer un rendez-vous.';"),
        ("recap.innerHTML='<b>'+t.nom+' · '+z.nom+'</b><span>'+(z.detail?z.detail+' · ':'')+prix(z)+'</span>';",
         "recap.innerHTML='<b>'+t.nom+' · '+z.nom+'</b><span>'+(z.detail?z.detail+' · ':'')+prix(z)+(z.forfait?' · forfait : '+forfait(z):'')+'</span>';"),
    ]:
        s = remplace(s, a, b, "harmonisation-faciale.html")
    p.write_text(s, encoding="utf-8")
    # 3. le hub et les menus des trois autres pages
    q = ICI / "index.html"
    t = q.read_text(encoding="utf-8")
    t = remplace(t, "Facial Balancing, Genesis Hollywood, Genesis Soft : chaque zone du visage, et son tarif.",
                 "Facial Balancing, Genesis, Mésothérapie amincissante : chaque zone du visage, et son tarif.", "index.html")
    q.write_text(t, encoding="utf-8")
    for nom in ("index.html", "luxury-skin-clinic.html"):
        q = ICI / nom
        t = q.read_text(encoding="utf-8")
        a = "    {n:'Genesis Soft',subs:['Creux infraorbitaire','Sillon nasogénien','Restructuration labiale','Mâchoire et joues']}\n  ]}"
        if MENU_HUB not in t:
            t = remplace(t, a, a.replace("\n  ]}", ",\n" + MENU_HUB + "\n  ]}"), nom)
        q.write_text(t, encoding="utf-8")
    q = ICI / "ina-luxury.html"
    t = q.read_text(encoding="utf-8")
    a = "    {label:'Genesis Soft',items:['Creux infraorbitaire','Sillon nasogénien','Restructuration labiale','Mâchoire et joues']},\n"
    if MENU_INA not in t:
        t = remplace(t, a, a + MENU_INA + "\n", "ina-luxury.html")
    q.write_text(t, encoding="utf-8")
    print("textes, hub et menus : à jour")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""_soins_2611.py · les changements de soins demandés par la cliente le 26/11 (Luxury Skin Clinic).

Ses mots, recopiés tels quels dans les fiches :
  · Soins visage : AJOUTER Cosmelan Peel 950 000 F, Melan 2 Peel 999 000 F, Perfect Derma Peel 200 000 F ;
  · Soins du corps : RETIRER le Luxury Massage ;
  · Soins capillaires : « Soin Activateur de Pousse » devient « Mésothérapie ANAGEN » ;
  · RETIRER le Soin Complet VIP du menu.
Partout où ces soins sont nommés : SERVICES (la seule source des prix), la FAQ des tarifs, les menus des trois pages.
Le JSON-LD, llms.txt et tarifs.md se refont ensuite en LISANT la page (_jsonld.py, _llms.py).
Idempotent : un changement déjà fait n'est pas refait. Refuse d'écrire si un repère manque.
"""
import io
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

TEXTE_DEPIG = ("Un traitement dépigmentant professionnel de référence, conçu pour corriger les hyperpigmentations persistantes "
               "et réguler la production excessive de mélanine.")
TEXTE_CIBLE = ("Il cible notamment le mélasma, les taches brunes, les marques post-acnéiques et les irrégularités pigmentaires. "
               "Il contribue à retrouver un teint plus uniforme, lumineux et harmonieux grâce à une action correctrice et "
               "régulatrice prolongée, associée à un protocole de soins à domicile.")

PEELS = """  {g:'visage',n:'Cosmelan Peel',a:'cosmelan',tier:'Avancé',tierCls:'vip',p:950000,kind:'book',
   d:"Correction intensive des hyperpigmentations — Peeling + routine complète maison.",
   c:['taches','irregulier','acne'],
   meta:[['Peeling + routine complète maison','grid']],
   det:`<div class="det-h">🌿 Correction intensive des hyperpigmentations</div><p class="det-p">%(dep)s</p><p class="det-p">%(cib)s</p>`,
   protocol:{type:'list',h:'Le traitement inclut',items:["Le peeling en institut","La routine complète à suivre à la maison"]}},
  {g:'visage',n:'Melan 2 Peel',a:'melan2',tier:'Avancé',tierCls:'vip',p:999000,kind:'book',
   d:"Traitement dépigmentant professionnel — Peeling + routine complète maison.",
   c:['taches','irregulier','acne'],
   meta:[['Peeling + routine complète maison','grid']],
   det:`<div class="det-h">🌿 Le traitement</div><p class="det-p">%(dep)s</p><p class="det-p">%(cib)s</p>`,
   protocol:{type:'list',h:'Le traitement inclut',items:["Le peeling en institut","La routine complète à suivre à la maison"]}},
  {g:'visage',n:'Perfect Derma Peel',a:'perfectderma',tier:'Avancé',tierCls:'vip',p:200000,kind:'book',
   d:"Peeling rénovateur et éclaircissant — Hyperpigmentations • Texture • Éclat.",
   c:['taches','irregulier','acne','texture','age'],
   meta:[['Profondeur moyenne','grid']],
   det:`<div class="det-h">🌿 Peeling rénovateur et éclaircissant</div><p class="det-p">Un peeling professionnel de profondeur moyenne associant plusieurs actifs exfoliants et antioxydants, notamment le glutathion.</p><p class="det-p">Il aide à atténuer les hyperpigmentations, le mélasma, les cicatrices pigmentaires d’acné et les irrégularités du teint. Il améliore également la texture cutanée, affine le grain de peau et atténue l’apparence des ridules pour une peau visiblement plus lisse et lumineuse.</p>`},
""" % {"dep": TEXTE_DEPIG, "cib": TEXTE_CIBLE}

VISAGE_ANCIEN = "'Soin Glass Skin','Luxury Peel']"
VISAGE_NOUVEAU = "'Soin Glass Skin','Luxury Peel','Cosmelan Peel','Melan 2 Peel','Perfect Derma Peel']"
MENUS = [
    (VISAGE_ANCIEN, VISAGE_NOUVEAU),
    ("['Gommage Luxury','Luxury Massage']", "['Gommage Luxury']"),
    ("'Le Hair Spa','Activateur de Pousse']", "'Le Hair Spa','Mésothérapie ANAGEN']"),
    (",\n    {n:'Expérience VIP',subs:['Le Soin Complet VIP']}", ""),
    ("    {label:'VIP',items:['Le Soin Complet VIP']},\n", ""),
]


def bloc(s, debut, fin_motif):
    """Retire l'objet qui commence par `debut` et finit au premier `fin_motif` qui suit."""
    i = s.find(debut)
    if i < 0:
        return s, False
    j = s.index(fin_motif, i) + len(fin_motif)
    if s[j:j + 1] == "\n":
        j += 1
    return s[:i] + s[j:], True


def main():
    p = ICI / "luxury-skin-clinic.html"
    s = p.read_text(encoding="utf-8")
    faits = []
    if "n:'Cosmelan Peel'" not in s:
        ancre = '"Kit pré-peeling et kit post-peeling disponibles"]}},\n'
        if ancre not in s:
            raise SystemExit("fin du Luxury Peel introuvable")
        s = s.replace(ancre, ancre + PEELS, 1)
        faits.append("3 peelings ajoutés")
    s, ok = bloc(s, "  {g:'corps',n:'Luxury Massage'", '"Cuir chevelu","Nuque","Dos","Bras","Jambes","Pieds"]}},')
    if ok:
        faits.append("Luxury Massage retiré")
    s, ok = bloc(s, "  {g:'complet',n:'Le Soin Complet VIP'", '"Espace VIP privatisé exclusif"]}},')
    if ok:
        faits.append("Soin Complet VIP retiré")
    if "n:'Soin Activateur de Pousse'" in s:
        s = s.replace("n:'Soin Activateur de Pousse'", "n:'Mésothérapie ANAGEN'", 1)
        faits.append("Activateur de Pousse → Mésothérapie ANAGEN")
    faq_a = "à 150 000 FCFA\n             pour Le Soin Complet VIP."
    if faq_a in s:
        s = s.replace(faq_a, "à 999 000 FCFA\n             pour le Melan 2 Peel.", 1)
        faits.append("FAQ des tarifs")
    for a, b in MENUS:
        if a in s:
            s = s.replace(a, b)
    p.write_text(s, encoding="utf-8")
    print("luxury-skin-clinic.html :", " · ".join(faits) or "déjà à jour")
    for nom in ("index.html", "ina-luxury.html"):
        q = ICI / nom
        t = q.read_text(encoding="utf-8")
        n = 0
        for a, b in MENUS:
            if a in t:
                t = t.replace(a, b); n += 1
        q.write_text(t, encoding="utf-8")
        print(f"{nom} : {n} changement(s) de menu")
    # contrôle : les prix de SERVICES, tels qu'ils sont maintenant
    m = re.search(r"const SERVICES=\[(.*?)\n\];", s, re.S)
    for x in re.finditer(r"\{g:'([a-z]+)',n:'([^']+)'.*?p:(\d+)", m.group(1)):
        print(f"  {x.group(1):12} {x.group(2):36} {int(x.group(3)):>9,} F".replace(",", " "))


if __name__ == "__main__":
    main()
